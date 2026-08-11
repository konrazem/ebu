"""Official durable single-attempt runner for V3.0 Gate 1D-C.

Import is side-effect free and standard-library-only.  Complete operational
preflight runs before the result directory exists.  The immutable execution
receipt and execution-start control are durably published, and the start file
is exclusively locked, before scientific modules are imported or a scientific
call becomes reachable.  The runner owns the registered stdout artifact and
publishes receipt, start, trace, closed stdout, and summary in that order.
``MANIFEST.md`` is produced only by the separate frozen mechanical finalizer.
"""
from __future__ import annotations

import ast
import ctypes
import fcntl
import gzip
import hashlib
import importlib
import io
import json
import math
import os
import platform
import re
import signal
import stat
import subprocess
import sys
import zlib


BRANCH = "v3.0-local-ebu-foundation"
REMOTE = "origin"
REMOTE_REF = "refs/heads/v3.0-local-ebu-foundation"
REPOSITORY_ROOT = "/Users/konrad.grzyb/code/ebu"
PLAN_CANONICAL = "f9dd4b804a83744268bffe48d2d3861825cbc96d90aa871f348251e4108ef287"
PLAN_RAW = "91a2c42558c09051988bfebe6f0d11c0fab440340d161171afc4442c86fa30fe"
PROTOCOL_SHA256 = "3122aa673f47290bbee866feb56d16afc4540f552ed7c7b458f097ef4e44d04f"
ADDENDUM_SHA256 = "28d47aa314e74206b4cc3da9ceccfbf0a08bd2196930490636c1d3c991039fa1"
CONTRACT_RAW = "81d96d3f377a2d1d2471b38328af8968b9c728db590023d0d921e4312cd23155"
CONTRACT_CANONICAL = "ed90eaf901b506cc91e0a7ba3c4a6329ad6f8730278716383c07f525b748e208"
COMPATIBILITY_ADDENDUM_SHA256 = (
    "2e439afad6ba7532aae83631ef4fb7ea6648980be035674f8e2d13faeecd9b51")
COMPATIBILITY_CONTRACT_RAW = (
    "628ee126011b3bdb6587af53c64f69db2fbd86d92deaef27ff60366b4d80ef8b")
COMPATIBILITY_CONTRACT_CANONICAL = (
    "0fbdaf54734d10a88172ed79451dc2e7a31e4021b66c765d5df164a1d93f3077")
PLAN = "v30_gate1dc_outcome_discrimination_plan.json"
PROTOCOL = "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md"
ADDENDUM = "V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md"
CONTRACT = "v30_gate1dc_execution_finalization_contract.json"
COMPATIBILITY_ADDENDUM = (
    "V3.0_GATE1D_C_MACOS_ENVIRONMENT_COMPATIBILITY_ADDENDUM.md")
COMPATIBILITY_CONTRACT = (
    "v30_gate1dc_macos_environment_compatibility_contract.json")

OUTDIR = "results/v3.0/gate1dc"
RECEIPT = f"{OUTDIR}/v30_gate1dc_execution_receipt.json"
EXECUTION_STARTED = f"{OUTDIR}/v30_gate1dc_execution_started.json"
MANIFEST = f"{OUTDIR}/MANIFEST.md"
SUMMARY = f"{OUTDIR}/v30_gate1dc_summary.json"
TRACE = f"{OUTDIR}/v30_gate1dc_trace.jsonl.gz"
STDOUT = f"{OUTDIR}/v30_gate1dc_stdout.txt"

TEMPORARY_PATHS = {
    RECEIPT: f"{OUTDIR}/.v30_gate1dc_execution_receipt.json.tmp",
    EXECUTION_STARTED: f"{OUTDIR}/.v30_gate1dc_execution_started.json.tmp",
    TRACE: f"{OUTDIR}/.v30_gate1dc_trace.jsonl.gz.tmp",
    STDOUT: f"{OUTDIR}/.v30_gate1dc_stdout.txt.tmp",
    SUMMARY: f"{OUTDIR}/.v30_gate1dc_summary.json.tmp",
    MANIFEST: f"{OUTDIR}/.MANIFEST.md.tmp",
}
REGISTERED_ARTIFACTS = (
    RECEIPT, EXECUTION_STARTED, TRACE, STDOUT, SUMMARY, MANIFEST,
)
ORIGINAL_SOURCE_HASH_ORDER = (
    "AGENTS.md", PROTOCOL, PLAN, ADDENDUM, CONTRACT,
    "gate1dc_v30.py", "test_v30_gate1dc.py", "exp_v30_gate1dc.py",
    "finalize_v30_gate1dc.py", "d0_v29.py", "p1c_v29.py",
    "ebu_quote_v30.py", "service_v30.py",
)
SOURCE_HASH_ORDER = (
    "AGENTS.md", PROTOCOL, PLAN, ADDENDUM, CONTRACT,
    COMPATIBILITY_ADDENDUM, COMPATIBILITY_CONTRACT,
    "gate1dc_v30.py", "test_v30_gate1dc.py", "exp_v30_gate1dc.py",
    "finalize_v30_gate1dc.py", "d0_v29.py", "p1c_v29.py",
    "ebu_quote_v30.py", "service_v30.py",
)
FROZEN_SOURCE_HASHES = {
    "AGENTS.md": "92e934b78017962191dd5fcb021bac079d598e4cf80d4722c33b839fabc1d9cf",
    PROTOCOL: PROTOCOL_SHA256,
    PLAN: PLAN_RAW,
    ADDENDUM: ADDENDUM_SHA256,
    CONTRACT: CONTRACT_RAW,
    COMPATIBILITY_ADDENDUM: COMPATIBILITY_ADDENDUM_SHA256,
    COMPATIBILITY_CONTRACT: COMPATIBILITY_CONTRACT_RAW,
    "d0_v29.py": "f7fdce8d946b44b4e0bfab9338fcd5c378796f9d14cd80323c53732e08a3bfe9",
    "p1c_v29.py": "a30c869000080b4b0235a9ba1daa517a5b0fe734ba55ac423ae3042da5940729",
    "ebu_quote_v30.py": "44a2ea282837f7613198a06a7037fb89f2f9fd99f05cedde65e0b1ba726e1b79",
    "service_v30.py": "a83bcd5e449b8804f44607e56326ec392324cdfed71260e28fdc4c48899d44e0",
}
EXPECTED_ENVIRONMENT = {
    "PATH": "/opt/homebrew/bin:/usr/bin:/bin",
    "LC_ALL": "C",
    "LANG": "C",
    "TZ": "UTC",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
}
COMPATIBILITY_VARIABLE = "__CF_USER_TEXT_ENCODING"
COMPATIBILITY_VALUE = "0x1F5:0x0:0x0"
ENTRY_ENVIRONMENT_KEYS = (
    "PATH", "LC_ALL", "LANG", "TZ", "PYTHONHASHSEED",
    "PYTHONNOUSERSITE", COMPATIBILITY_VARIABLE,
    "EBU_GATE1DC_EXECUTION_SHA",
)
NORMALIZED_ENVIRONMENT_KEYS = (
    "PATH", "LC_ALL", "LANG", "TZ", "PYTHONHASHSEED",
    "PYTHONNOUSERSITE", "EBU_GATE1DC_EXECUTION_SHA",
)
PYTHON_INVOKED_AS = "/opt/homebrew/bin/python3"
PYTHON_REALPATH = ("/opt/homebrew/Cellar/python@3.14/3.14.2/Frameworks/"
                   "Python.framework/Versions/3.14/bin/python3.14")
PYTHON_VERSION = "3.14.2"
ZLIB_VERSION = "1.2.12"
ATTEMPT_ID = "gate1dc-single-authorized-attempt"
OUTCOME_CLASS_ORDER = (
    "numerical_or_domain_failure", "systemic_collapse",
    "destructive_service", "physical_impossibility",
    "distributive_or_policy_under_service",
    "safe_rationing_physical_scarcity", "preserve_but_under_serve",
    "preserve_and_serve", "unclassified",
)

EXEC_ARMS = (
    "A_full_multi_edge_p1c", "B_restricted_matched_non_ebu",
    "C_restricted_observational_quote",
    "D_restricted_exact_total_quote_greedy",
    "S_restricted_local_service_priority",
)
WORLD_NAMES = ("DC1_flux_lock", "DC2_capacity_split", "DC3_demand_pulse")
DT_LABELS = ("conservative", "near_certificate")
ARM_A, ARM_B, ARM_C, ARM_D, ARM_S = EXEC_ARMS
PRIMARY_BASELINE_ARM = ARM_B
REQUIRED_TICK_FIELDS_EXTRA = (
        "x_before", "x_after", "menus", "candidate_exact_quotes",
        "request_shaping_identity", "rested", "pulse_tick",
        "transport_loss", "negative_corrections", "domain_failure",
        "reserve_crossings", "allee_crossings", "dead_sources",
        "physical_overuse", "p1c_rejections", "quote_sign_counts",
        "group_diagnostic", "ebu_pos", "ebu_neg", "quoted",
)

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
_SCIENTIFIC_MODULES = ("d0_v29", "p1c_v29", "ebu_quote_v30",
                       "service_v30", "gate1dc_v30")
_AUTHORIZED_SHA_RE = r"^[0-9a-f]{40}$"
_SHA256_RE = r"^[0-9a-f]{64}$"

# Bound only after the durable start control is published and locked.
dc = eq = sv = None
REQUIRED_TICK_FIELDS = REQUIRED_TICK_FIELDS_EXTRA


def _fatal(message: str):
    raise SystemExit(f"FATAL: {message}")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: str) -> str:
    try:
        with open(path, "rb") as handle:
            return _sha256_bytes(handle.read())
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


def _reject_nonfinite(value):
    raise ValueError(f"non-finite JSON constant {value!r} rejected")


def _reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r} rejected")
        result[key] = value
    return result


def strict_loads(payload):
    if isinstance(payload, bytes):
        if payload.startswith(b"\xef\xbb\xbf"):
            raise ValueError("JSON UTF-8 BOM rejected")
        payload = payload.decode("utf-8", errors="strict")
    if not isinstance(payload, str):
        raise TypeError("strict JSON input must be str or bytes")
    return json.loads(payload, object_pairs_hook=_reject_duplicate_pairs,
                      parse_constant=_reject_nonfinite)


def canonical_bytes(value) -> bytes:
    return strict_dumps(value, separators=(",", ":")).encode("utf-8")


def ordered_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=False, ensure_ascii=True,
                       allow_nan=False, separators=(",", ":")) + "\n").encode(
                           "utf-8")


def _raw_environment_entries() -> list[tuple[str, str]]:
    """Read the process-entry vector without collapsing duplicate names."""
    try:
        process = ctypes.CDLL(None)
        if sys.platform == "darwin":
            get_environ = process._NSGetEnviron
            get_environ.restype = ctypes.POINTER(
                ctypes.POINTER(ctypes.c_char_p))
            environ = get_environ()[0]
        else:
            environ = ctypes.POINTER(ctypes.c_char_p).in_dll(
                process, "environ")
        entries = []
        index = 0
        while environ[index] is not None:
            text = os.fsdecode(environ[index])
            key, separator, value = text.partition("=")
            if separator != "=" or not key:
                _fatal("malformed process-entry environment declaration")
            entries.append((key, value))
            index += 1
        return entries
    except (AttributeError, OSError, TypeError, ValueError) as error:
        _fatal(f"cannot inspect raw process-entry environment: {error}")


def _normalize_entry_environment(environment=None, raw_entries=None) -> str:
    """Validate exact eight-key entry, delete only the compatibility key."""
    actual_environment = os.environ if environment is None else environment
    if raw_entries is None:
        raw_entries = (_raw_environment_entries() if environment is None
                       else list(actual_environment.items()))
    raw_entries = list(raw_entries)
    raw_keys = [key for key, _value in raw_entries]
    if len(raw_entries) != len(ENTRY_ENVIRONMENT_KEYS) \
            or len(set(raw_keys)) != len(raw_keys) \
            or set(raw_keys) != set(ENTRY_ENVIRONMENT_KEYS):
        _fatal("process entry does not contain exactly eight unique frozen keys")
    raw_environment = dict(raw_entries)
    snapshot = dict(actual_environment)
    if raw_environment != snapshot:
        _fatal("raw and Python process-entry environments differ")
    authorized_sha = snapshot.get("EBU_GATE1DC_EXECUTION_SHA")
    expected_entry = {
        **EXPECTED_ENVIRONMENT,
        COMPATIBILITY_VARIABLE: COMPATIBILITY_VALUE,
        "EBU_GATE1DC_EXECUTION_SHA": authorized_sha,
    }
    if set(snapshot) != set(expected_entry) or any(
            snapshot.get(key) != value for key, value in expected_entry.items()):
        _fatal("environment does not equal the frozen eight-key entry allowlist")
    if snapshot.get(COMPATIBILITY_VARIABLE) != COMPATIBILITY_VALUE:
        _fatal("macOS compatibility value is not the exact frozen value")
    if authorized_sha is None or re.fullmatch(
            _AUTHORIZED_SHA_RE, authorized_sha) is None:
        _fatal("EBU_GATE1DC_EXECUTION_SHA must be one lowercase 40-hex SHA")
    try:
        del actual_environment[COMPATIBILITY_VARIABLE]
    except BaseException as error:
        _fatal(f"failed to delete only the macOS compatibility key: {error}")
    expected_normalized = {
        **EXPECTED_ENVIRONMENT, "EBU_GATE1DC_EXECUTION_SHA": authorized_sha,
    }
    if dict(actual_environment) != expected_normalized \
            or set(actual_environment) != set(NORMALIZED_ENVIRONMENT_KEYS):
        _fatal("post-normalization environment differs from exact seven-key allowlist")
    return authorized_sha


def _validate_compatibility_contract() -> dict:
    """Strictly validate the compatibility contract before any Git action."""
    try:
        raw = open(COMPATIBILITY_CONTRACT, "rb").read()
    except OSError as error:
        _fatal(f"cannot read macOS compatibility contract: {error}")
    if _sha256_bytes(raw) != COMPATIBILITY_CONTRACT_RAW:
        _fatal("raw macOS compatibility-contract SHA-256 mismatch")
    try:
        compatibility = strict_loads(raw)
    except (TypeError, UnicodeError, ValueError) as error:
        _fatal(f"strict macOS compatibility-contract parse failed: {error}")
    if _sha256_bytes(canonical_bytes(compatibility)) != \
            COMPATIBILITY_CONTRACT_CANONICAL:
        _fatal("canonical macOS compatibility-contract SHA-256 mismatch")
    entry = compatibility.get("entry_environment", {})
    normalized = compatibility.get("normalization", {}).get(
        "normalized_environment", {})
    expected_entry_values = {
        **EXPECTED_ENVIRONMENT,
        COMPATIBILITY_VARIABLE: COMPATIBILITY_VALUE,
        "EBU_GATE1DC_EXECUTION_SHA": "<authorized_execution_sha>",
    }
    expected_normalized_values = {
        **EXPECTED_ENVIRONMENT,
        "EBU_GATE1DC_EXECUTION_SHA": "<authorized_execution_sha>",
    }
    runner_line = (
        "env -i PATH=/opt/homebrew/bin:/usr/bin:/bin LC_ALL=C LANG=C "
        "TZ=UTC PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 "
        "__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0 "
        "EBU_GATE1DC_EXECUTION_SHA=\"${AUTHORIZED_EXECUTION_SHA}\" "
        "/opt/homebrew/bin/python3 -B -s -X utf8 exp_v30_gate1dc.py")
    invocations = compatibility.get("official_invocations", {})
    if (compatibility.get("compatibility_sources") != {
            "markdown": COMPATIBILITY_ADDENDUM,
            "json": COMPATIBILITY_CONTRACT,
            "markdown_role": "normative human rendering",
            "json_role": "mechanical schema and ordering source",
            "agreement_rule": (
                "Any disagreement between the compatibility Markdown and JSON "
                "is an integrity failure and causes fail-closed refusal; "
                "neither may be applied selectively."),
            }
            or entry.get("key_count") != 8
            or tuple(entry.get("key_order", ())) != ENTRY_ENVIRONMENT_KEYS
            or entry.get("exact_values") != expected_entry_values
            or entry.get("additional_or_missing_keys_permitted") is not False
            or compatibility.get("normalization", {}).get("delete_only")
            != COMPATIBILITY_VARIABLE
            or normalized.get("key_count") != 7
            or tuple(normalized.get("key_order", ()))
            != NORMALIZED_ENVIRONMENT_KEYS
            or normalized.get("exact_values") != expected_normalized_values
            or compatibility.get("normalization", {}).get(
                "other_normalization_permitted") is not False
            or invocations.get("runner_shell_lines") != [
                "AUTHORIZED_EXECUTION_SHA='<AUDITED_40_LOWERCASE_HEX_EXECUTION_SHA>'",
                runner_line]
            or tuple(compatibility.get("receipt_integration", {}).get(
                "source_sha256_order", ())) != SOURCE_HASH_ORDER
            or compatibility.get("receipt_integration", {}).get(
                "top_level_field_count") != 16
            or compatibility.get("receipt_integration", {}).get(
                "contract_raw_sha256_meaning") != (
                    "Unchanged: SHA-256 of the exact committed "
                    "v30_gate1dc_execution_finalization_contract.json bytes "
                    "at the authorized execution SHA.")
            or compatibility.get("manifest_integration", {}).get(
                "provenance_row_count") != 15):
        _fatal("macOS compatibility contract schema or ordering mismatch")
    return compatibility


def _git_bytes(*arguments: str) -> bytes:
    try:
        completed = subprocess.run(
            ("git",) + arguments, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        _fatal(f"Git check failed for {' '.join(arguments)}: "
               f"{(detail or str(error)).strip()}")
    return completed.stdout


def _git(*arguments: str) -> str:
    return _git_bytes(*arguments).decode("utf-8", errors="strict").strip()


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
    expected = [
        "screen_budget", "candidate_menu", "quote_schedule_for",
        "select_arm_B", "select_arm_D", "select_arm_S",
    ]
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


def _validate_runtime(authorized_sha: str) -> None:
    if len(sys.argv) != 1 or sys.argv[0] != "exp_v30_gate1dc.py":
        _fatal("this runner takes no arguments and must use its exact filename")
    expected_environment = {
        **EXPECTED_ENVIRONMENT, "EBU_GATE1DC_EXECUTION_SHA": authorized_sha,
    }
    if set(os.environ) != set(expected_environment) or any(
            os.environ.get(key) != value
            for key, value in expected_environment.items()):
        _fatal("environment does not equal the frozen env -i allowlist")
    if re.fullmatch(_AUTHORIZED_SHA_RE, authorized_sha) is None:
        _fatal("normalized execution SHA is not lowercase 40-hex")
    original = tuple(getattr(sys, "orig_argv", ()))
    expected_argv = (PYTHON_INVOKED_AS, "-B", "-s", "-X", "utf8",
                     "exp_v30_gate1dc.py")
    if original != expected_argv:
        _fatal("Python argv is not the exact frozen invocation")
    if os.path.realpath(PYTHON_INVOKED_AS) != PYTHON_REALPATH \
            or os.path.realpath(sys.executable) != PYTHON_REALPATH:
        _fatal("Python executable realpath mismatch")
    if platform.python_version() != PYTHON_VERSION:
        _fatal("Python version mismatch")
    if zlib.ZLIB_VERSION != ZLIB_VERSION or zlib.ZLIB_RUNTIME_VERSION != ZLIB_VERSION:
        _fatal("zlib compile/runtime version mismatch")
    if not (sys.flags.dont_write_bytecode and sys.flags.no_user_site
            and sys.flags.utf8_mode == 1):
        _fatal("Python flags must be exactly compatible with -B -s -X utf8")
    if any(name in sys.modules for name in _SCIENTIFIC_MODULES):
        _fatal("scientific module became reachable before receipt durability")


def _validate_repository(authorized_sha: str) -> dict:
    root = os.path.realpath(REPOSITORY_ROOT)
    if os.path.realpath(os.path.dirname(__file__)) != root \
            or os.path.realpath(os.getcwd()) != root:
        _fatal(f"runner must execute from exact repository root {root}")
    if _git("rev-parse", "--show-toplevel") != root:
        _fatal("Git top-level does not equal the frozen repository root")
    branch = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != BRANCH:
        _fatal(f"branch {branch!r} != registered {BRANCH!r}")
    head = _git("rev-parse", "HEAD")
    remote = _git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    live_lines = _git("ls-remote", "--heads", REMOTE, REMOTE_REF).splitlines()
    if len(live_lines) != 1 or live_lines[0].split() != [authorized_sha, REMOTE_REF]:
        _fatal("live remote ref does not equal authorized execution SHA")
    if head != authorized_sha or remote != authorized_sha:
        _fatal("local HEAD or tracking ref does not equal authorized SHA")
    status = _git_bytes("status", "--porcelain=v2", "--untracked-files=all")
    if status:
        _fatal("index/worktree is not exactly clean before result-directory creation")
    if os.path.lexists(OUTDIR):
        _fatal("registered result directory already exists; retry forbidden")
    parent = os.path.dirname(OUTDIR)
    try:
        parent_stat = os.lstat(parent)
    except OSError as error:
        _fatal(f"cannot inspect registered result parent: {error}")
    if not stat.S_ISDIR(parent_stat.st_mode) or stat.S_ISLNK(parent_stat.st_mode):
        _fatal("results/v3.0 must be an existing non-symlink directory")

    source_hashes = {}
    for path in SOURCE_HASH_ORDER:
        try:
            path_stat = os.lstat(path)
        except OSError as error:
            _fatal(f"cannot inspect source {path}: {error}")
        if not stat.S_ISREG(path_stat.st_mode) or stat.S_ISLNK(path_stat.st_mode):
            _fatal(f"source is not a regular non-symlink file: {path}")
        tree_line = _git("ls-tree", authorized_sha, "--", path)
        fields = tree_line.split(None, 3)
        if len(fields) != 4 or fields[0] != "100644" or fields[1] != "blob" \
                or fields[3] != path:
            _fatal(f"source is not an exact tracked regular blob: {path}")
        worktree = open(path, "rb").read()
        committed = _git_bytes("show", f"{authorized_sha}:{path}")
        if worktree != committed:
            _fatal(f"worktree/Git blob byte mismatch for {path}")
        digest = _sha256_bytes(worktree)
        if path in FROZEN_SOURCE_HASHES and digest != FROZEN_SOURCE_HASHES[path]:
            _fatal(f"frozen source SHA-256 mismatch for {path}: {digest}")
        source_hashes[path] = digest
    return {
        "branch": branch, "execution_sha": head, "remote_tracking_sha": remote,
        "source_sha256": source_hashes,
        "required_source_sha256": source_hashes,
        "runner_sha256": source_hashes["exp_v30_gate1dc.py"],
        "python": {
            "invoked_as": PYTHON_INVOKED_AS,
            "executable_realpath": PYTHON_REALPATH,
            "version": PYTHON_VERSION,
            "zlib_version": ZLIB_VERSION,
            "zlib_runtime_version": ZLIB_VERSION,
            "flags": ["-B", "-s", "-X", "utf8"],
        },
        "platform": platform.platform(),
    }


def _validate_contract_and_plan(
        compatibility: dict) -> tuple[dict, dict, list]:
    plan_raw = open(PLAN, "rb").read()
    contract_raw = open(CONTRACT, "rb").read()
    if _sha256_bytes(plan_raw) != PLAN_RAW or _sha256_bytes(contract_raw) != CONTRACT_RAW:
        _fatal("raw plan or execution-contract SHA-256 mismatch")
    plan = strict_loads(plan_raw)
    contract = strict_loads(contract_raw)
    if _sha256_bytes(canonical_bytes(plan)) != PLAN_CANONICAL \
            or _sha256_bytes(canonical_bytes(contract)) != CONTRACT_CANONICAL:
        _fatal("canonical plan or execution-contract SHA-256 mismatch")
    if (_sha256(PROTOCOL) != PROTOCOL_SHA256
            or _sha256(ADDENDUM) != ADDENDUM_SHA256
            or _sha256(COMPATIBILITY_ADDENDUM)
            != COMPATIBILITY_ADDENDUM_SHA256):
        _fatal("protocol or operational-addendum SHA-256 mismatch")
    legal = contract.get("legal_and_scientific_status", {})
    if legal.get("scientific_precedence") != [PROTOCOL, PLAN] \
            or legal.get("scientific_preregistration_unchanged") is not True \
            or legal.get("f4_exact_expression") != (
                "certified_lower_bound - 1e-9 * (1 + abs(certified_lower_bound))"):
        _fatal("scientific precedence or F4 contract mismatch")
    paths = contract.get("paths", {})
    expected_paths = {
        "repository_root": REPOSITORY_ROOT, "branch": BRANCH,
        "remote": REMOTE, "remote_ref": REMOTE_REF,
        "result_directory": OUTDIR, "execution_receipt": RECEIPT,
        "execution_started": EXECUTION_STARTED, "stdout": STDOUT,
        "trace": TRACE, "summary": SUMMARY, "manifest": MANIFEST,
        "runner": "exp_v30_gate1dc.py", "finalizer": "finalize_v30_gate1dc.py",
    }
    if any(paths.get(key) != value for key, value in expected_paths.items()):
        _fatal("contract path inventory mismatch")
    receipt_contract = contract.get("execution_receipt", {})
    if tuple(receipt_contract.get("source_hash_order", ())) != \
            ORIGINAL_SOURCE_HASH_ORDER:
        _fatal("original receipt source-hash order mismatch")
    if tuple(compatibility.get("receipt_integration", {}).get(
            "top_level_field_order", ())) != tuple(
                receipt_contract.get("field_order", ())) \
            or tuple(compatibility.get("receipt_integration", {}).get(
                "source_sha256_order", ())) != SOURCE_HASH_ORDER:
        _fatal("amended receipt source-hash order mismatch")
    expected_temporary_names = {
        "receipt": os.path.basename(TEMPORARY_PATHS[RECEIPT]),
        "execution_started": os.path.basename(TEMPORARY_PATHS[EXECUTION_STARTED]),
        "trace": os.path.basename(TEMPORARY_PATHS[TRACE]),
        "stdout": os.path.basename(TEMPORARY_PATHS[STDOUT]),
        "summary": os.path.basename(TEMPORARY_PATHS[SUMMARY]),
        "manifest": os.path.basename(TEMPORARY_PATHS[MANIFEST]),
    }
    if contract.get("temporary_files", {}).get("names") != expected_temporary_names \
            or [item.get("path_key") for item in contract.get(
                "artifact_inventory", [])] != [
                    "execution_receipt", "execution_started", "trace", "stdout",
                    "summary", "manifest"] \
            or contract.get("runner_summary_completion_contract", {}).get(
                "required_top_level_fields") != [
                    "gate", "plan_id", "plan_version", "plan_canonical_hash",
                    "plan_raw_sha256", "equation_version",
                    "implementation_sha256", "execution_sha", "branch",
                    "python", "platform", "registered", "n_runs", "runs",
                    "comparisons", "discriminator_v2", "positive_controls",
                    "hypotheses", "falsifiers", "o3_aggregate_diagnostic",
                    "outcome_class_counts", "registered_artifacts",
                    "completion", "non_claims"]:
        _fatal("artifact, temporary, or summary contract schema mismatch")
    inventory = contract.get("registered_execution_inventory", {})
    run_ids = inventory.get("run_ids")
    expected_run_ids = [
        f"{world}|{arm}|{label}" for world in WORLD_NAMES
        for label in DT_LABELS for arm in EXEC_ARMS
    ]
    if (inventory.get("world_order") != list(WORLD_NAMES)
            or inventory.get("timestep_order") != list(DT_LABELS)
            or inventory.get("arm_order") != list(EXEC_ARMS)
            or inventory.get("run_length_ticks") != 200
            or inventory.get("total_runs") != 30
            or inventory.get("trace_rows") != 6000
            or run_ids != expected_run_ids):
        _fatal("registered execution inventory mismatch")
    if (plan.get("experiment_size", {}).get("total_runs") != 30
            or plan.get("experiment_size", {}).get("run_length_ticks") != 200
            or list(plan.get("worlds", {})) != list(WORLD_NAMES)
            or list(plan.get("hypotheses", {})) != [f"H{i}" for i in range(1, 11)]
            or list(plan.get("falsifiers", {})) != [f"F{i}" for i in range(1, 17)]
            or len(plan.get("non_claims", [])) != 8):
        _fatal("scientific plan schema/inventory mismatch")
    if len(contract.get("failure_retry_matrix", [])) != 17:
        _fatal("failure/retry matrix must contain exactly 17 frozen cases")
    if tuple(contract.get("state_machine", {}).get("classification_order", ())) != (
            "FINALIZED", "RUNNER_COMPLETE", "EXECUTING", "ATTEMPT_COMMITTED",
            "PREFLIGHT", "UNSTARTED", "FAILED_OR_INTERRUPTED"):
        _fatal("seven-state classification order mismatch")
    specs = []
    for run_identifier in run_ids:
        world, arm, label = run_identifier.split("|")
        specs.append({"world": world, "arm": arm, "dt_label": label,
                      "run_id": run_identifier})
    return plan, contract, specs


def preflight() -> tuple[list, dict, dict, dict]:
    """Finish every check before creating the result directory or receipt."""
    authorized_sha = _normalize_entry_environment()
    compatibility = _validate_compatibility_contract()
    _validate_runtime(authorized_sha)
    plan, contract, specs = _validate_contract_and_plan(compatibility)
    for source in _RANDOMNESS_GUARDED_SOURCES:
        hits = _randomness_imports(source)
        if hits:
            _fatal(f"{source} imports randomness: {sorted(hits)}")
    _validate_information_boundary()
    repository = _validate_repository(authorized_sha)
    return specs, repository, plan, contract


def _load_scientific_modules(plan: dict) -> None:
    """Make scientific code reachable only after receipt/start durability."""
    global dc, eq, sv, REQUIRED_TICK_FIELDS
    dc = importlib.import_module("gate1dc_v30")
    eq = importlib.import_module("ebu_quote_v30")
    sv = importlib.import_module("service_v30")
    if (dc.PLAN_RAW != PLAN_RAW or dc.PLAN_CANONICAL != PLAN_CANONICAL
            or dc.COMPATIBILITY_CONTRACT_RAW != COMPATIBILITY_CONTRACT_RAW
            or dc.COMPATIBILITY_CONTRACT_CANONICAL
            != COMPATIBILITY_CONTRACT_CANONICAL
            or tuple(dc.SOURCE_HASH_ORDER) != SOURCE_HASH_ORDER
            or tuple(dc.EXEC_ARMS) != EXEC_ARMS
            or tuple(dc.WORLD_NAMES) != WORLD_NAMES
            or tuple(dc.DT_LABELS) != DT_LABELS):
        _fatal("scientific implementation locks disagree with frozen contract")
    dc.validate_plan(plan)
    dc.validate_output_contract()
    if (dc.RUN_TICKS, dc.BURN_IN_TICKS, dc.MEASUREMENT_TICKS,
            dc.PERSISTENCE_WINDOW) != (200, 50, 150, 20):
        _fatal("scientific horizon/window locks disagree")
    for world in WORLD_NAMES:
        certificate = dc.world_certificates(world)
        dts = dc.world_dts(world)
        for label, expected_r in (("conservative", 0.5),
                                  ("near_certificate", 0.9)):
            r_dt = dts[label] / certificate["binding_certificate"]
            if abs(r_dt - expected_r) > 1e-12 or r_dt > 1.0:
                _fatal(f"{world}/{label}: registered r_dt mismatch")
    REQUIRED_TICK_FIELDS = tuple(dict.fromkeys(
        tuple(dc.TICK_RECORD_FIELDS) + REQUIRED_TICK_FIELDS_EXTRA))


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
        "implementation_sha256": dict(repository["source_sha256"]),
        "execution_sha": repository["execution_sha"],
        "branch": repository["branch"], "python": dict(repository["python"]),
        "platform": repository["platform"],
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
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0,
                       compresslevel=9) as gz:
        for row in rows:
            gz.write((strict_dumps(row, separators=(",", ":")) + "\n").encode())
    return buffer.getvalue()


def render_summary(summary: dict) -> bytes:
    return (strict_dumps(summary, indent=2) + "\n").encode()


def _json_number(value) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value):
        _fatal(f"stdout numeric value is not a finite JSON number: {value!r}")
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def render_stdout(summary: dict) -> bytes:
    lines = [
        "EBP V3.0 Gate 1D-C - outcome-discrimination study",
        f"execution SHA: {summary['execution_sha']}",
        f"plan canonical hash: {PLAN_CANONICAL}",
        "registered: 3 worlds x 2 timesteps x 5 arms = 30 runs; 200 ticks "
        "each; burn-in 50; measurement 150; no seed",
    ]
    frozen_order = summary["registered"]["frozen_order"]
    for index, run_identifier in enumerate(frozen_order, 1):
        record = summary["runs"][run_identifier]
        lines.append(
            f"run {index:02d}/30 | {run_identifier} | "
            f"service={_json_number(record['total_service'])} | "
            f"unmet={_json_number(record['total_unmet'])} | "
            f"ebu={_json_number(record['ebu_total'])} | "
            f"r_dt={_json_number(record['r_dt'])}")
    for outcome in OUTCOME_CLASS_ORDER:
        if outcome in summary["outcome_class_counts"]:
            count = summary["outcome_class_counts"][outcome]
            if isinstance(count, bool) or not isinstance(count, int):
                _fatal("outcome-class count is not an integer")
            lines.append(f"outcome | {outcome} | {count}")
    fired = [f"F{index}" for index in range(1, 17)
             if summary["falsifiers"][f"F{index}"]["fired"]]
    lines.extend([
        "falsifiers fired: " + (", ".join(fired) if fired else "none"),
        "runner outputs validated in memory",
        "trace published durably",
        "stdout complete; summary publication follows",
    ])
    log = io.StringIO(newline="\n")
    for line in lines:
        log.write(line)
        log.write("\n")
    payload = log.getvalue().encode("utf-8")
    log.close()
    _validate_text_bytes(payload, "stdout")
    return payload


def _validate_text_bytes(payload: bytes, label: str) -> None:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload \
            or b"\r" in payload or not payload.endswith(b"\n") \
            or payload.endswith(b"\n\n"):
        _fatal(f"{label} violates UTF-8/LF/exact-final-LF contract")
    try:
        payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        _fatal(f"{label} is invalid UTF-8: {error}")


def validate_complete_outputs_in_memory(runs: list, summary: dict,
                                        rows: list, trace_bytes: bytes,
                                        stdout_bytes: bytes,
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
            if missing or set(row) != set(dc.TRACE_PROVENANCE_FIELDS):
                _fatal(f"trace row {position} missing provenance {missing}")
            position += 1
    if list(summary["runs"]) != expected_ids or summary["n_runs"] != 30:
        _fatal("summary run inventory/order mismatch")
    if set(summary) != set(dc.SUMMARY_REQUIRED_BLOCKS):
        _fatal("summary top-level fields differ from exact contract")
    if list(summary["hypotheses"]) != [f"H{i}" for i in range(1, 11)]:
        _fatal("summary H1-H10 ordering mismatch")
    if list(summary["falsifiers"]) != [f"F{i}" for i in range(1, 17)]:
        _fatal("summary F1-F16 ordering mismatch")
    if list(summary["positive_controls"]) != list(dc._PC_BOUNDS):
        _fatal("summary PC1-PC4 ordering mismatch")
    expected_artifact_fields = {
        "execution_receipt": {"path", "bytes", "sha256"},
        "execution_started": {"path", "bytes", "sha256"},
        "trace": {"path", "bytes", "sha256"},
        "stdout": {"path", "bytes", "sha256"},
        "summary": {"path", "runner_completion_sentinel",
                    "self_hash_deferred_to_manifest"},
        "manifest": {"path", "written_by_runner",
                     "full_study_completion_sentinel"},
    }
    if set(summary["registered_artifacts"]) != set(expected_artifact_fields) \
            or any(set(summary["registered_artifacts"][key]) != fields
                   for key, fields in expected_artifact_fields.items()):
        _fatal("summary registered-artifact schema mismatch")
    expected_completion = {
        "runner_complete": True, "runner_completion_sentinel": SUMMARY,
        "study_finalized": False, "full_study_completion_sentinel": MANIFEST,
        "scientific_attempts_committed": 1,
        "scientific_retry_permitted": False,
    }
    if summary["completion"] != expected_completion:
        _fatal("summary completion contract mismatch")
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
    parsed_summary = strict_loads(summary_bytes)
    if render_summary(parsed_summary) != summary_bytes:
        _fatal("summary bytes are not deterministic strict summary JSON")
    try:
        decompressed = gzip.decompress(trace_bytes)
    except (OSError, EOFError) as error:
        _fatal(f"trace gzip cannot be decompressed: {error}")
    lines = decompressed.splitlines(keepends=True)
    if len(lines) != 6000 or any(not line.endswith(b"\n") for line in lines):
        _fatal("trace does not contain exactly 6000 LF-terminated JSON lines")
    reparsed = []
    for index, line in enumerate(lines):
        value = strict_loads(line[:-1])
        if canonical_bytes(value) + b"\n" != line:
            _fatal(f"trace row {index} is not canonical strict JSON")
        reparsed.append(value)
    if render_trace(reparsed) != trace_bytes:
        _fatal("trace gzip bytes are not deterministic")
    if render_stdout(summary) != stdout_bytes:
        _fatal("stdout bytes differ from the frozen grammar")


def _fsync_directory(path: str) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("short artifact write")
        view = view[written:]


def _publish_new(path: str, payload: bytes) -> None:
    """Publish via the sole fixed-name, same-filesystem, no-overwrite primitive."""
    if path not in REGISTERED_ARTIFACTS[:-1] or path not in TEMPORARY_PATHS:
        raise ValueError(f"unregistered publication path {path!r}")
    temporary = TEMPORARY_PATHS[path]
    directory = os.path.dirname(path)
    allowed_entries = {os.path.basename(item) for item in REGISTERED_ARTIFACTS}
    allowed_entries |= {os.path.basename(item)
                        for item in TEMPORARY_PATHS.values()}
    unexpected = set(os.listdir(directory)) - allowed_entries
    if unexpected:
        raise ValueError(f"unexpected result-directory entries: {sorted(unexpected)}")
    if os.path.lexists(temporary) or os.path.lexists(path):
        raise FileExistsError(f"publication path or fixed temporary exists: {path}")
    position = REGISTERED_ARTIFACTS.index(path)
    expected_prefix = {os.path.basename(item)
                       for item in REGISTERED_ARTIFACTS[:position]}
    if set(os.listdir(directory)) != expected_prefix:
        raise ValueError("registered publication prefix is not exact")
    directory_stat = os.stat(directory, follow_symlinks=False)
    if not stat.S_ISDIR(directory_stat.st_mode) \
            or stat.S_ISLNK(directory_stat.st_mode):
        raise OSError("publication destination is not a regular directory")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600)
    closed = False
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_dev != directory_stat.st_dev:
            raise OSError("temporary file is not regular or is on another filesystem")
        os.fchmod(descriptor, 0o600)
        if stat.S_IMODE(os.fstat(descriptor).st_mode) != 0o600:
            raise OSError("temporary file mode is not 0600")
        _write_all(descriptor, payload)
        os.fsync(descriptor)
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        os.close(descriptor)
        closed = True
        if os.path.lexists(path):
            raise FileExistsError(path)
        os.link(temporary, path, follow_symlinks=False)
        _fsync_directory(directory)
        os.unlink(temporary)
        _fsync_directory(directory)
    finally:
        if not closed:
            os.close(descriptor)


def _verify_published(path: str, expected: bytes) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        chunks = []
        remaining = len(expected) + 1
        while remaining:
            chunk = os.read(descriptor, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
    finally:
        os.close(descriptor)
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o444
            or info.st_nlink != 1 or payload != expected):
        _fatal(f"published artifact failed immutable byte check: {path}")
    return payload


def _create_result_directory() -> None:
    if os.path.lexists(OUTDIR):
        _fatal("result directory exists; scientific retry is forbidden")
    parent = os.path.dirname(OUTDIR)
    os.mkdir(OUTDIR, 0o700)
    info = os.lstat(OUTDIR)
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) \
            or stat.S_IMODE(info.st_mode) != 0o700:
        _fatal("result directory was not created as exact mode-0700 directory")
    _fsync_directory(parent)


def _pre_receipt_cleanup() -> None:
    """The only cleanup path; valid solely before any receipt final exists."""
    finals = (RECEIPT, EXECUTION_STARTED, TRACE, STDOUT, SUMMARY, MANIFEST)
    if any(os.path.lexists(path) for path in finals):
        raise RuntimeError("pre-receipt cleanup forbidden after any final artifact")
    if not os.path.lexists(OUTDIR):
        return
    info = os.lstat(OUTDIR)
    if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
        raise RuntimeError("pre-receipt residue is not a directory")
    receipt_temporary = TEMPORARY_PATHS[RECEIPT]
    entries = os.listdir(OUTDIR)
    allowed = {os.path.basename(receipt_temporary)}
    if not set(entries) <= allowed:
        raise RuntimeError("pre-receipt residue contains an unexpected entry")
    if os.path.lexists(receipt_temporary):
        temporary_info = os.lstat(receipt_temporary)
        if not stat.S_ISREG(temporary_info.st_mode) \
                or stat.S_ISLNK(temporary_info.st_mode):
            raise RuntimeError("receipt temporary residue is not regular")
        os.unlink(receipt_temporary)
        _fsync_directory(OUTDIR)
    if os.listdir(OUTDIR):
        raise RuntimeError("pre-receipt result directory is not empty")
    os.rmdir(OUTDIR)
    _fsync_directory(os.path.dirname(OUTDIR))


def _official_invocation(authorized_sha: str) -> str:
    del authorized_sha
    return ("env -i PATH=/opt/homebrew/bin:/usr/bin:/bin LC_ALL=C LANG=C "
            "TZ=UTC PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 "
            "__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0 "
            "EBU_GATE1DC_EXECUTION_SHA=<authorized_execution_sha> "
            "/opt/homebrew/bin/python3 -B -s -X utf8 exp_v30_gate1dc.py")


def _build_receipt(repository: dict) -> dict:
    source_hashes = {path: repository["source_sha256"][path]
                     for path in SOURCE_HASH_ORDER}
    return {
        "schema_version": "1.0.0",
        "artifact_type": "gate1dc_execution_receipt",
        "gate": "V3.0 Gate 1D-C",
        "attempt_id": ATTEMPT_ID,
        "branch": BRANCH,
        "remote_ref": REMOTE_REF,
        "authorized_execution_sha": repository["execution_sha"],
        "authorized_execution_sha_source": "EBU_GATE1DC_EXECUTION_SHA",
        "plan_raw_sha256": PLAN_RAW,
        "plan_canonical_sha256": PLAN_CANONICAL,
        "contract_raw_sha256": CONTRACT_RAW,
        "contract_canonical_sha256": CONTRACT_CANONICAL,
        "source_sha256": source_hashes,
        "python": dict(repository["python"]),
        "official_invocation": _official_invocation(repository["execution_sha"]),
        "authorization_consumed_when": (
            "the execution_receipt final path exists and the result-directory "
            "fsync after its exclusive atomic link has returned success"),
    }


def _validate_receipt_bytes(receipt: dict, payload: bytes, contract: dict) -> None:
    expected_order = contract["execution_receipt"]["field_order"]
    if list(receipt) != expected_order or list(receipt["source_sha256"]) != list(
            SOURCE_HASH_ORDER):
        _fatal("receipt or source hashes have wrong field order")
    if ordered_bytes(receipt) != payload or strict_loads(payload) != receipt:
        _fatal("receipt bytes are not exact ordered strict JSON")
    expected_python = {
        "invoked_as": PYTHON_INVOKED_AS,
        "executable_realpath": PYTHON_REALPATH,
        "version": PYTHON_VERSION,
        "zlib_version": ZLIB_VERSION,
        "zlib_runtime_version": ZLIB_VERSION,
        "flags": ["-B", "-s", "-X", "utf8"],
    }
    if (receipt["schema_version"] != "1.0.0"
            or receipt["artifact_type"] != "gate1dc_execution_receipt"
            or receipt["gate"] != "V3.0 Gate 1D-C"
            or receipt["attempt_id"] != ATTEMPT_ID
            or receipt["branch"] != BRANCH
            or receipt["remote_ref"] != REMOTE_REF
            or receipt["authorized_execution_sha_source"]
            != "EBU_GATE1DC_EXECUTION_SHA"
            or re.fullmatch(_AUTHORIZED_SHA_RE,
                            receipt["authorized_execution_sha"]) is None
            or receipt["plan_raw_sha256"] != PLAN_RAW
            or receipt["plan_canonical_sha256"] != PLAN_CANONICAL
            or receipt["contract_raw_sha256"] != CONTRACT_RAW
            or receipt["contract_canonical_sha256"] != CONTRACT_CANONICAL
            or any(re.fullmatch(_SHA256_RE, value) is None
                   for value in receipt["source_sha256"].values())
            or list(receipt["python"]) != list(expected_python)
            or receipt["python"] != expected_python
            or receipt["official_invocation"] != _official_invocation(
                receipt["authorized_execution_sha"])
            or receipt["authorization_consumed_when"] != (
                "the execution_receipt final path exists and the result-directory "
                "fsync after its exclusive atomic link has returned success")):
        _fatal("receipt fixed schema mismatch")


def _build_execution_start(receipt: dict, receipt_bytes: bytes) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "gate1dc_execution_started",
        "gate": "V3.0 Gate 1D-C",
        "attempt_id": ATTEMPT_ID,
        "authorized_execution_sha": receipt["authorized_execution_sha"],
        "execution_receipt_sha256": _sha256_bytes(receipt_bytes),
        "phase": "scientific_execution_reachable",
    }


def _lock_execution_start() -> int:
    descriptor = os.open(EXECUTION_STARTED,
                         os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _complete_summary(summary: dict, receipt_bytes: bytes, start_bytes: bytes,
                      trace_bytes: bytes, stdout_bytes: bytes) -> None:
    summary["registered_artifacts"] = {
        "execution_receipt": {
            "path": RECEIPT, "bytes": len(receipt_bytes),
            "sha256": _sha256_bytes(receipt_bytes)},
        "execution_started": {
            "path": EXECUTION_STARTED, "bytes": len(start_bytes),
            "sha256": _sha256_bytes(start_bytes)},
        "trace": {"path": TRACE, "bytes": len(trace_bytes),
                  "sha256": _sha256_bytes(trace_bytes)},
        "stdout": {"path": STDOUT, "bytes": len(stdout_bytes),
                   "sha256": _sha256_bytes(stdout_bytes)},
        "summary": {"path": SUMMARY, "runner_completion_sentinel": True,
                    "self_hash_deferred_to_manifest": True},
        "manifest": {"path": MANIFEST, "written_by_runner": False,
                     "full_study_completion_sentinel": True},
    }
    summary["completion"] = {
        "runner_complete": True,
        "runner_completion_sentinel": SUMMARY,
        "study_finalized": False,
        "full_study_completion_sentinel": MANIFEST,
        "scientific_attempts_committed": 1,
        "scientific_retry_permitted": False,
    }


def write_outputs(runs: list, summary: dict, rows: list,
                  receipt_bytes: bytes, start_bytes: bytes) -> dict:
    """Validate all bytes, then publish trace, closed stdout, and summary."""
    trace_bytes = render_trace(rows)
    stdout_bytes = render_stdout(summary)
    _complete_summary(summary, receipt_bytes, start_bytes, trace_bytes,
                      stdout_bytes)
    summary_bytes = render_summary(summary)
    validate_complete_outputs_in_memory(
        runs, summary, rows, trace_bytes, stdout_bytes, summary_bytes)
    for path in (TRACE, STDOUT, SUMMARY, MANIFEST):
        if os.path.lexists(path):
            _fatal(f"refusing to overwrite registered artifact {path}")
    _publish_new(TRACE, trace_bytes)
    _verify_published(TRACE, trace_bytes)
    _publish_new(STDOUT, stdout_bytes)
    _verify_published(STDOUT, stdout_bytes)
    _publish_new(SUMMARY, summary_bytes)
    _verify_published(SUMMARY, summary_bytes)
    return {
        TRACE: {"sha256": _sha256_bytes(trace_bytes),
                "bytes": len(trace_bytes)},
        STDOUT: {"sha256": _sha256_bytes(stdout_bytes),
                 "bytes": len(stdout_bytes)},
        SUMMARY: {"sha256": _sha256_bytes(summary_bytes),
                  "bytes": len(summary_bytes)},
    }


def _signal_abort(signum, _frame):
    raise SystemExit(f"FATAL: interrupted by signal {signum}; residues preserved")


def main() -> int:
    specs, repository, plan, contract = preflight()
    start_descriptor = None
    prior_handlers = {}
    for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        prior_handlers[signum] = signal.signal(signum, _signal_abort)
    try:
        _create_result_directory()
        receipt = _build_receipt(repository)
        receipt_bytes = ordered_bytes(receipt)
        _validate_receipt_bytes(receipt, receipt_bytes, contract)
        _publish_new(RECEIPT, receipt_bytes)
        _verify_published(RECEIPT, receipt_bytes)

        execution_start = _build_execution_start(receipt, receipt_bytes)
        if list(execution_start) != contract["execution_started_control"]["field_order"]:
            _fatal("execution-start field order mismatch")
        start_bytes = ordered_bytes(execution_start)
        if strict_loads(start_bytes) != execution_start:
            _fatal("execution-start bytes are not strict ordered JSON")
        _publish_new(EXECUTION_STARTED, start_bytes)
        _verify_published(EXECUTION_STARTED, start_bytes)
        start_descriptor = _lock_execution_start()

        # The first project/scientific import and every scientific call are
        # dynamically and lexically after durable receipt/start plus the lock.
        _load_scientific_modules(plan)
        runs = execute_registered_study(specs)
        summary = build_summary(runs, repository)
        rows = list(trace_rows(runs, repository))
        write_outputs(runs, summary, rows, receipt_bytes, start_bytes)

        fcntl.flock(start_descriptor, fcntl.LOCK_UN)
        os.close(start_descriptor)
        start_descriptor = None
        return 0
    except BaseException:
        if start_descriptor is not None:
            try:
                fcntl.flock(start_descriptor, fcntl.LOCK_UN)
            finally:
                os.close(start_descriptor)
                start_descriptor = None
        if not os.path.lexists(RECEIPT):
            _pre_receipt_cleanup()
        raise
    finally:
        for signum, handler in prior_handlers.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(main())
