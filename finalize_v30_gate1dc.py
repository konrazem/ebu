"""Mechanical finalizer for already completed V3.0 Gate 1D-C outputs.

Importing this module has zero side effects.  It imports only the standard
library and performs no Git call, filesystem inspection, open, parse, print,
lock, write, or scientific action until ``main`` is called explicitly.
"""
from __future__ import annotations

import errno
import ctypes
import fcntl
import gzip
import hashlib
import io
import json
import math
import os
import platform
import re
import stat
import subprocess
import sys
import zlib


REPOSITORY_ROOT = "/Users/konrad.grzyb/code/ebu"
BRANCH = "v3.0-local-ebu-foundation"
REMOTE = "origin"
REMOTE_REF = "refs/heads/v3.0-local-ebu-foundation"
PLAN_PATH = "v30_gate1dc_outcome_discrimination_plan.json"
PROTOCOL_PATH = "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md"
ADDENDUM_PATH = "V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md"
CONTRACT_PATH = "v30_gate1dc_execution_finalization_contract.json"
PLAN_RAW = "91a2c42558c09051988bfebe6f0d11c0fab440340d161171afc4442c86fa30fe"
PLAN_CANONICAL = "f9dd4b804a83744268bffe48d2d3861825cbc96d90aa871f348251e4108ef287"
PROTOCOL_SHA256 = "3122aa673f47290bbee866feb56d16afc4540f552ed7c7b458f097ef4e44d04f"
ADDENDUM_SHA256 = "28d47aa314e74206b4cc3da9ceccfbf0a08bd2196930490636c1d3c991039fa1"
CONTRACT_RAW = "81d96d3f377a2d1d2471b38328af8968b9c728db590023d0d921e4312cd23155"
CONTRACT_CANONICAL = "ed90eaf901b506cc91e0a7ba3c4a6329ad6f8730278716383c07f525b748e208"
COMPATIBILITY_ADDENDUM_PATH = (
    "V3.0_GATE1D_C_MACOS_ENVIRONMENT_COMPATIBILITY_ADDENDUM.md")
COMPATIBILITY_CONTRACT_PATH = (
    "v30_gate1dc_macos_environment_compatibility_contract.json")
COMPATIBILITY_ADDENDUM_SHA256 = (
    "2e439afad6ba7532aae83631ef4fb7ea6648980be035674f8e2d13faeecd9b51")
COMPATIBILITY_CONTRACT_RAW = (
    "628ee126011b3bdb6587af53c64f69db2fbd86d92deaef27ff60366b4d80ef8b")
COMPATIBILITY_CONTRACT_CANONICAL = (
    "0fbdaf54734d10a88172ed79451dc2e7a31e4021b66c765d5df164a1d93f3077")

RESULT_DIRECTORY = "results/v3.0/gate1dc"
RECEIPT_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_execution_receipt.json"
START_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_execution_started.json"
TRACE_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_trace.jsonl.gz"
STDOUT_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_stdout.txt"
SUMMARY_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_summary.json"
MANIFEST_PATH = f"{RESULT_DIRECTORY}/MANIFEST.md"
FINAL_PATHS = (
    RECEIPT_PATH, START_PATH, TRACE_PATH, STDOUT_PATH, SUMMARY_PATH,
    MANIFEST_PATH,
)
TEMPORARY_PATHS = {
    RECEIPT_PATH: f"{RESULT_DIRECTORY}/.v30_gate1dc_execution_receipt.json.tmp",
    START_PATH: f"{RESULT_DIRECTORY}/.v30_gate1dc_execution_started.json.tmp",
    TRACE_PATH: f"{RESULT_DIRECTORY}/.v30_gate1dc_trace.jsonl.gz.tmp",
    STDOUT_PATH: f"{RESULT_DIRECTORY}/.v30_gate1dc_stdout.txt.tmp",
    SUMMARY_PATH: f"{RESULT_DIRECTORY}/.v30_gate1dc_summary.json.tmp",
    MANIFEST_PATH: f"{RESULT_DIRECTORY}/.MANIFEST.md.tmp",
}
ORIGINAL_SOURCE_HASH_ORDER = (
    "AGENTS.md", PROTOCOL_PATH, PLAN_PATH, ADDENDUM_PATH, CONTRACT_PATH,
    "gate1dc_v30.py", "test_v30_gate1dc.py", "exp_v30_gate1dc.py",
    "finalize_v30_gate1dc.py", "d0_v29.py", "p1c_v29.py",
    "ebu_quote_v30.py", "service_v30.py",
)
SOURCE_HASH_ORDER = (
    "AGENTS.md", PROTOCOL_PATH, PLAN_PATH, ADDENDUM_PATH, CONTRACT_PATH,
    COMPATIBILITY_ADDENDUM_PATH, COMPATIBILITY_CONTRACT_PATH,
    "gate1dc_v30.py", "test_v30_gate1dc.py", "exp_v30_gate1dc.py",
    "finalize_v30_gate1dc.py", "d0_v29.py", "p1c_v29.py",
    "ebu_quote_v30.py", "service_v30.py",
)
FROZEN_SOURCE_HASHES = {
    "AGENTS.md": "92e934b78017962191dd5fcb021bac079d598e4cf80d4722c33b839fabc1d9cf",
    PROTOCOL_PATH: PROTOCOL_SHA256,
    PLAN_PATH: PLAN_RAW,
    ADDENDUM_PATH: ADDENDUM_SHA256,
    CONTRACT_PATH: CONTRACT_RAW,
    COMPATIBILITY_ADDENDUM_PATH: COMPATIBILITY_ADDENDUM_SHA256,
    COMPATIBILITY_CONTRACT_PATH: COMPATIBILITY_CONTRACT_RAW,
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
STATE_ORDER = (
    "FINALIZED", "RUNNER_COMPLETE", "EXECUTING", "ATTEMPT_COMMITTED",
    "PREFLIGHT", "UNSTARTED", "FAILED_OR_INTERRUPTED",
)
WORLD_ORDER = ("DC1_flux_lock", "DC2_capacity_split", "DC3_demand_pulse")
DT_ORDER = ("conservative", "near_certificate")
ARM_ORDER = (
    "A_full_multi_edge_p1c", "B_restricted_matched_non_ebu",
    "C_restricted_observational_quote",
    "D_restricted_exact_total_quote_greedy",
    "S_restricted_local_service_priority",
)
CONTROL_ORDER = (
    "PC1_DC1_S_starves_dst2", "PC2_DC3_S_misses_pulses",
    "PC3_DC1_A_vs_B_capability_cost", "PC4_DC2_A_vs_B_capacity_gap",
)
OUTCOME_ORDER = (
    "numerical_or_domain_failure", "systemic_collapse",
    "destructive_service", "physical_impossibility",
    "distributive_or_policy_under_service",
    "safe_rationing_physical_scarcity", "preserve_but_under_serve",
    "preserve_and_serve", "unclassified",
)
SUMMARY_FIELDS = (
    "gate", "plan_id", "plan_version", "plan_canonical_hash",
    "plan_raw_sha256", "equation_version", "implementation_sha256",
    "execution_sha", "branch", "python", "platform", "registered",
    "n_runs", "runs", "comparisons", "discriminator_v2",
    "positive_controls", "hypotheses", "falsifiers",
    "o3_aggregate_diagnostic", "outcome_class_counts",
    "registered_artifacts", "completion", "non_claims",
)
RUN_RECORD_FIELDS = (
    "run_id", "world", "arm", "dt_label", "dt", "dt_certificate",
    "certificate_kind", "r_dt", "total_service", "total_unmet",
    "total_demand", "ebu_total", "ebu_positive", "ebu_negative",
    "pbi_service", "pbi_unmet", "pbi_service_by_destination",
    "pbi_unmet_by_destination", "service_by_destination",
    "unmet_by_destination", "accepted_actions", "voluntary_rests",
    "p1c_rejections", "reserve_crossings", "allee_crossings",
    "physical_overuse", "negative_corrections", "max_ledger_residual",
    "selected_edge_switches", "max_simultaneous_actions", "min_sigma",
    "final_state", "final_burden", "final_viability",
    "domain_failure_tick", "negative_state", "feasible_world",
    "service_alignment_predicate", "per_destination_alignment",
    "outcome_class",
)
TICK_RECORD_FIELDS = (
    "tick", "arm", "dt", "x_before", "x_after", "u", "available",
    "active_out_edges", "menus", "candidate_exact_quotes",
    "candidate_per_unit_quotes", "candidate_continuous_vertices",
    "selected", "threshold_diagnostics", "rested",
    "request_shaping_identity", "executed_q_acc", "delivered", "sigma",
    "budget_utilization", "service", "unmet", "demand_amount",
    "pulse_tick", "transport_loss", "negative_corrections",
    "ledger_residual", "domain_failure", "reserve_crossings",
    "allee_crossings", "dead_sources", "physical_overuse",
    "p1c_rejections", "min_source", "burden", "viability", "ebu",
    "ebu_pos", "ebu_neg", "quoted", "quote_sign_counts",
    "recomputation_residuals", "group_diagnostic",
)
COMPARISON_FIELDS = (
    "A_vs_B_capability_cost", "B_vs_C_observational_identity",
    "B_vs_D_primary_alignment", "S_vs_B_and_D_secondary",
    "timestep_sensitivity", "primary_baseline_arm", "forbidden_baseline_arm",
)
TOTAL_ALIGNMENT_FIELDS = (
    "ebu_total", "ebu_threshold_met", "pbi_service_baseline",
    "pbi_service_actor", "service_deficit_absolute",
    "service_deficit_relative", "service_persistent", "service_condition",
    "pbi_unmet_baseline", "pbi_unmet_actor", "unmet_excess_absolute",
    "unmet_excess_relative", "unmet_persistent", "unmet_condition",
    "service_deficit_per_tick_magnitude_variant",
    "baseline_crossed_reserve", "actor_crossed_reserve",
    "min_source_baseline", "min_source_actor", "preservation_justified",
    "is_service_alignment_failure",
)
DESTINATION_ALIGNMENT_FIELDS = (
    "destination", "pbi_unmet_baseline", "pbi_unmet_actor",
    "unmet_excess_absolute", "unmet_excess_relative", "unmet_persistent",
    "unmet_condition", "is_service_alignment_failure",
)
_SHA40 = r"^[0-9a-f]{40}$"
_SHA64 = r"^[0-9a-f]{64}$"
_TRANSIENT_ERRNOS = {
    errno.EINTR, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
    errno.EHOSTUNREACH, errno.ENETUNREACH,
}
_NETWORK_TRANSIENT_MARKERS = (
    "could not resolve host", "name or service not known",
    "temporary failure in name resolution", "nodename nor servname provided",
    "connection timed out", "connection reset", "connection refused",
    "failed to connect", "couldn't connect", "no route to host",
    "network is unreachable",
)


class TransientFinalizationError(RuntimeError):
    """A frozen transient that permits restarting unchanged validation."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _reject_nonfinite(value):
    raise ValueError(f"non-finite JSON constant {value!r} rejected")


def _reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r} rejected")
        result[key] = value
    return result


def strict_json_loads(payload):
    if isinstance(payload, bytes):
        if payload.startswith(b"\xef\xbb\xbf"):
            raise ValueError("JSON UTF-8 BOM rejected")
        payload = payload.decode("utf-8", errors="strict")
    if not isinstance(payload, str):
        raise TypeError("strict JSON input must be str or bytes")
    return json.loads(payload, object_pairs_hook=_reject_duplicate_pairs,
                      parse_constant=_reject_nonfinite)


def canonical_json_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def ordered_json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=False, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def summary_json_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       allow_nan=False, indent=2) + "\n").encode("utf-8")


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
                raise ValueError("malformed process-entry environment declaration")
            entries.append((key, value))
            index += 1
        return entries
    except (AttributeError, OSError, TypeError, ValueError) as error:
        raise RuntimeError(
            f"cannot inspect raw process-entry environment: {error}") from error


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
        raise ValueError(
            "process entry does not contain exactly eight unique frozen keys")
    raw_environment = dict(raw_entries)
    snapshot = dict(actual_environment)
    if raw_environment != snapshot:
        raise ValueError("raw and Python process-entry environments differ")
    authorized_sha = snapshot.get("EBU_GATE1DC_EXECUTION_SHA")
    expected_entry = {
        **EXPECTED_ENVIRONMENT,
        COMPATIBILITY_VARIABLE: COMPATIBILITY_VALUE,
        "EBU_GATE1DC_EXECUTION_SHA": authorized_sha,
    }
    if set(snapshot) != set(expected_entry) or any(
            snapshot.get(key) != value for key, value in expected_entry.items()):
        raise ValueError(
            "environment does not equal the frozen eight-key entry allowlist")
    if snapshot.get(COMPATIBILITY_VARIABLE) != COMPATIBILITY_VALUE:
        raise ValueError("macOS compatibility value is not the exact frozen value")
    if authorized_sha is None or re.fullmatch(_SHA40, authorized_sha) is None:
        raise ValueError("execution SHA must be one lowercase 40-hex value")
    try:
        del actual_environment[COMPATIBILITY_VARIABLE]
    except BaseException as error:
        raise RuntimeError(
            f"failed to delete only the macOS compatibility key: {error}") from error
    expected_normalized = {
        **EXPECTED_ENVIRONMENT, "EBU_GATE1DC_EXECUTION_SHA": authorized_sha,
    }
    if dict(actual_environment) != expected_normalized \
            or set(actual_environment) != set(NORMALIZED_ENVIRONMENT_KEYS):
        raise ValueError(
            "post-normalization environment differs from exact seven-key allowlist")
    return authorized_sha


def _validate_compatibility_contract() -> dict:
    """Strictly validate the compatibility contract before any Git action."""
    raw = open(COMPATIBILITY_CONTRACT_PATH, "rb").read()
    if sha256_bytes(raw) != COMPATIBILITY_CONTRACT_RAW:
        raise ValueError("raw macOS compatibility-contract SHA-256 mismatch")
    compatibility = strict_json_loads(raw)
    if sha256_bytes(canonical_json_bytes(compatibility)) != \
            COMPATIBILITY_CONTRACT_CANONICAL:
        raise ValueError(
            "canonical macOS compatibility-contract SHA-256 mismatch")
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
    finalizer_line = (
        "env -i PATH=/opt/homebrew/bin:/usr/bin:/bin LC_ALL=C LANG=C "
        "TZ=UTC PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 "
        "__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0 "
        "EBU_GATE1DC_EXECUTION_SHA=\"${AUTHORIZED_EXECUTION_SHA}\" "
        "/opt/homebrew/bin/python3 -B -s -X utf8 finalize_v30_gate1dc.py")
    invocations = compatibility.get("official_invocations", {})
    manifest = compatibility.get("manifest_integration", {})
    if (compatibility.get("compatibility_sources", {}).get("markdown")
            != COMPATIBILITY_ADDENDUM_PATH
            or compatibility.get("compatibility_sources", {}).get("json")
            != COMPATIBILITY_CONTRACT_PATH
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
            or invocations.get("finalizer_shell_lines") != [
                "AUTHORIZED_EXECUTION_SHA='<THE_SAME_AUDITED_40_LOWERCASE_HEX_EXECUTION_SHA>'",
                finalizer_line]
            or tuple(compatibility.get("receipt_integration", {}).get(
                "source_sha256_order", ())) != SOURCE_HASH_ORDER
            or compatibility.get("receipt_integration", {}).get(
                "top_level_field_count") != 16
            or manifest.get("provenance_row_count") != 15
            or manifest.get("compatibility_rows") != [
                {"order": 6, "source": COMPATIBILITY_ADDENDUM_PATH},
                {"order": 7, "source": COMPATIBILITY_CONTRACT_PATH}]):
        raise ValueError(
            "macOS compatibility contract schema or ordering mismatch")
    return compatibility


def deterministic_gzip(rows: list[dict]) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0,
                       compresslevel=9) as handle:
        for row in rows:
            handle.write(canonical_json_bytes(row) + b"\n")
    return buffer.getvalue()


def validate_text_bytes(payload: bytes, label: str) -> str:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload \
            or b"\r" in payload or not payload.endswith(b"\n") \
            or payload.endswith(b"\n\n"):
        raise ValueError(f"{label} violates UTF-8/LF/exact-final-LF rules")
    return payload.decode("utf-8", errors="strict")


def validate_finite_tree(value, path="value") -> None:
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_finite_tree(item, f"{path}/{index}")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_finite_tree(item, f"{path}/{key}")
        return
    raise TypeError(f"unsupported JSON value at {path}")


def _require_number(value, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value):
        raise ValueError(f"finite JSON number required at {path}")


def _require_number_list(value, path: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"JSON number array required at {path}")
    for index, item in enumerate(value):
        _require_number(item, f"{path}/{index}")


def classify_state(snapshot: dict) -> str:
    """Classify a validated synthetic/filesystem snapshot in frozen order."""
    if snapshot.get("recoverable_runner_complete") \
            and snapshot.get("manifest_valid") \
            and snapshot.get("manifest_exists") \
            and snapshot.get("no_unexpected_entries") \
            and not snapshot.get("lock_held"):
        return "FINALIZED"
    if snapshot.get("recoverable_runner_complete") \
            and not snapshot.get("manifest_exists"):
        return "RUNNER_COMPLETE"
    if (snapshot.get("receipt_valid") and snapshot.get("start_valid")
            and snapshot.get("lock_held") and snapshot.get("prefix_valid")
            and snapshot.get("no_unexpected_entries")
            and not snapshot.get("manifest_exists")):
        return "EXECUTING"
    if (snapshot.get("receipt_valid") and not snapshot.get("start_exists")
            and not snapshot.get("runner_outputs_exist")
            and not snapshot.get("manifest_exists")
            and not snapshot.get("lock_held")
            and snapshot.get("no_unexpected_entries")):
        return "ATTEMPT_COMMITTED"
    if (snapshot.get("result_directory_exists")
            and snapshot.get("preflight_entries_valid")
            and not snapshot.get("any_final_exists")):
        return "PREFLIGHT"
    if not snapshot.get("result_directory_exists"):
        return "UNSTARTED"
    return "FAILED_OR_INTERRUPTED"


def failure_disposition(contract: dict, failure_point: str) -> dict:
    rows = contract.get("failure_retry_matrix")
    if not isinstance(rows, list) or len(rows) != 17:
        raise ValueError("failure/retry matrix is not the exact 17-row contract")
    matches = [row for row in rows if row.get("failure_point") == failure_point]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate failure point {failure_point!r}")
    return dict(matches[0])


def render_cell(value) -> str:
    if value is None:
        rendered = "null"
    elif isinstance(value, bool):
        rendered = "true" if value else "false"
    elif isinstance(value, int):
        rendered = str(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite manifest cell")
        rendered = json.dumps(value, allow_nan=False, ensure_ascii=True)
    elif isinstance(value, str):
        rendered = value
    elif isinstance(value, (list, dict)):
        rendered = canonical_json_bytes(value).decode("ascii")
    else:
        raise TypeError(f"unsupported manifest cell {type(value).__name__}")
    return (rendered.replace("\\", "\\\\").replace("|", "\\|")
            .replace("\r\n", "<br>").replace("\r", "<br>")
            .replace("\n", "<br>"))


def _table(columns, rows) -> str:
    output = ["| " + " | ".join(render_cell(value) for value in columns) + " |",
              "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        if len(row) != len(columns):
            raise ValueError("manifest table row width mismatch")
        output.append("| " + " | ".join(render_cell(value) for value in row) + " |")
    return "\n".join(output)


def _bullets(values) -> str:
    return "\n".join("- " + render_cell(value) for value in values)


def render_manifest(receipt: dict, start: dict, summary: dict, plan: dict,
                    contract: dict, artifact_info: dict) -> bytes:
    """Pure deterministic render from five validated inputs and the contract."""
    del start
    schema = contract["manifest_rendering"]
    sections = schema["sections"]
    if [section["heading"] for section in sections] != schema["section_order"]:
        raise ValueError("manifest section order mismatch")
    blocks = [schema["title"]]

    section = sections[0]
    rows = [
        ["Study state", "FINALIZED", "contract state machine"],
        ["Attempt ID", receipt["attempt_id"], "execution receipt"],
        ["Execution SHA", receipt["authorized_execution_sha"],
         "execution receipt; must equal summary:/execution_sha"],
        ["Runner completion sentinel", SUMMARY_PATH, "contract artifact inventory"],
        ["Full-study completion sentinel", MANIFEST_PATH,
         "contract artifact inventory"],
        ["Registered runs", summary["n_runs"], "summary:/n_runs; exact 30"],
        ["Trace rows", 6000, "validated trace count"],
        ["Single scientific attempt", True, "receipt exists; no retry path"],
    ]
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[1]
    rows = [[index, path, receipt["source_sha256"][path]]
            for index, path in enumerate(SOURCE_HASH_ORDER, 1)]
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[2]
    roles = ("control", "control", "runner-output", "runner-output",
             "runner-output completion sentinel")
    rows = [[index, role, path, artifact_info[path]["bytes"],
             artifact_info[path]["sha256"]]
            for index, (role, path) in enumerate(zip(roles, FINAL_PATHS[:5]), 1)]
    rows.append([6, "full-study completion sentinel", MANIFEST_PATH,
                 "verified by deterministic render and Git blob", "not self-hashed"])
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[3]
    run_ids = contract["registered_execution_inventory"]["run_ids"]
    rows = [[index, run_identifier, "present", 200, "1–200"]
            for index, run_identifier in enumerate(run_ids, 1)]
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[4]
    rows = []
    for control in CONTROL_ORDER:
        for label in DT_ORDER:
            value = summary["positive_controls"][control][label]
            rows.append([control, label, value["measured_as"],
                         value["certified_lower_bound"], value["f4_threshold"],
                         value["executed_value"], value["f4_fired"]])
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[5]
    rows = [[key, plan["hypotheses"][key],
             summary["hypotheses"][key]["status"],
             summary["hypotheses"][key]["evidence"]]
            for key in (f"H{index}" for index in range(1, 11))]
    blocks.append("\n\n".join([section["heading"],
                                _table(section["table"]["columns"], rows)]))

    section = sections[6]
    rows = [[key, plan["falsifiers"][key],
             summary["falsifiers"][key]["fired"],
             summary["falsifiers"][key]["evidence"]]
            for key in (f"F{index}" for index in range(1, 17))]
    blocks.append("\n\n".join([section["heading"],
                                _table(section["table"]["columns"], rows)]))

    section = sections[7]
    rows = []
    for world in WORLD_ORDER:
        for label in DT_ORDER:
            key = f"{world}|{label}"
            value = summary["discriminator_v2"][key]
            rows.append([key, value["i_capability_cost_absolute"],
                         value["ii_service_ratio_delta"],
                         value["iii_max_destination_unmet_delta"],
                         value["world_discriminating"]])
    blocks.append("\n\n".join([section["heading"],
                                _table(section["table"]["columns"], rows)]))

    section = sections[8]
    o3 = summary["o3_aggregate_diagnostic"]
    rows = [["Arm-A ticks", o3["arm_A_ticks"]],
            ["Multi-action ticks", o3["multi_action_ticks"]],
            ["Total group quote", o3["total_group_quote"]],
            ["Total naive independent sum", o3["total_naive_independent_sum"]],
            ["Total double count", o3["total_double_count"]],
            ["Nothing settled or allocated", o3["nothing_settled_or_allocated"]],
            ["Frozen note", o3["note"]]]
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]
                                + [_table(section["table"]["columns"], rows)]))

    section = sections[9]
    rows = [[index, outcome, summary["outcome_class_counts"].get(outcome, 0)]
            for index, outcome in enumerate(OUTCOME_ORDER, 1)]
    blocks.append("\n\n".join([section["heading"],
                                _table(section["table"]["columns"], rows)]))

    section = sections[10]
    blocks.append("\n\n".join([
        section["heading"], section["fixed_subheading"],
        _bullets(section["fixed_limitations"]), section["nonclaim_subheading"],
        _bullets(summary["non_claims"]),
    ]))

    section = sections[11]
    blocks.append("\n\n".join([section["heading"]]
                                + section["fixed_paragraphs"]))
    payload = ("\n\n".join(blocks) + "\n").encode("utf-8")
    validate_text_bytes(payload, "manifest")
    if any(line.endswith((b" ", b"\t")) for line in payload.splitlines()):
        raise ValueError("manifest contains trailing whitespace")
    return payload


def validate_receipt(receipt_bytes: bytes, contract: dict,
                     authorized_sha: str, source_hashes: dict) -> dict:
    receipt = strict_json_loads(receipt_bytes)
    if list(receipt) != contract["execution_receipt"]["field_order"] \
            or ordered_json_bytes(receipt) != receipt_bytes:
        raise ValueError("receipt field order or exact bytes mismatch")
    fixed = {
        "schema_version": "1.0.0", "artifact_type": "gate1dc_execution_receipt",
        "gate": "V3.0 Gate 1D-C", "attempt_id": ATTEMPT_ID,
        "branch": BRANCH, "remote_ref": REMOTE_REF,
        "authorized_execution_sha": authorized_sha,
        "authorized_execution_sha_source": "EBU_GATE1DC_EXECUTION_SHA",
        "plan_raw_sha256": PLAN_RAW, "plan_canonical_sha256": PLAN_CANONICAL,
        "contract_raw_sha256": CONTRACT_RAW,
        "contract_canonical_sha256": CONTRACT_CANONICAL,
        "official_invocation": (
            "env -i PATH=/opt/homebrew/bin:/usr/bin:/bin LC_ALL=C LANG=C "
            "TZ=UTC PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 "
            "__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0 "
            "EBU_GATE1DC_EXECUTION_SHA=<authorized_execution_sha> "
            "/opt/homebrew/bin/python3 -B -s -X utf8 exp_v30_gate1dc.py"),
        "authorization_consumed_when": (
            "the execution_receipt final path exists and the result-directory "
            "fsync after its exclusive atomic link has returned success"),
    }
    if any(receipt.get(key) != value for key, value in fixed.items()):
        raise ValueError("receipt fixed field mismatch")
    if list(receipt.get("source_sha256", {})) != list(SOURCE_HASH_ORDER) \
            or receipt["source_sha256"] != source_hashes:
        raise ValueError("receipt source hashes mismatch")
    expected_python = {
        "invoked_as": PYTHON_INVOKED_AS,
        "executable_realpath": PYTHON_REALPATH,
        "version": PYTHON_VERSION,
        "zlib_version": ZLIB_VERSION,
        "zlib_runtime_version": ZLIB_VERSION,
        "flags": ["-B", "-s", "-X", "utf8"],
    }
    if list(receipt.get("python", {})) != list(expected_python) \
            or receipt.get("python") != expected_python:
        raise ValueError("receipt Python identity mismatch")
    return receipt


def validate_start(start_bytes: bytes, contract: dict, receipt: dict,
                   receipt_bytes: bytes) -> dict:
    started = strict_json_loads(start_bytes)
    if list(started) != contract["execution_started_control"]["field_order"] \
            or ordered_json_bytes(started) != start_bytes:
        raise ValueError("execution-start field order or exact bytes mismatch")
    expected = {
        "schema_version": "1.0.0",
        "artifact_type": "gate1dc_execution_started",
        "gate": "V3.0 Gate 1D-C", "attempt_id": ATTEMPT_ID,
        "authorized_execution_sha": receipt["authorized_execution_sha"],
        "execution_receipt_sha256": sha256_bytes(receipt_bytes),
        "phase": "scientific_execution_reachable",
    }
    if started != expected:
        raise ValueError("execution-start schema or receipt link mismatch")
    return started


def validate_summary(summary_bytes: bytes, contract: dict, plan: dict,
                     receipt: dict, artifact_info: dict) -> dict:
    summary = strict_json_loads(summary_bytes)
    if summary_json_bytes(summary) != summary_bytes or set(summary) != set(SUMMARY_FIELDS):
        raise ValueError("summary serialization or top-level schema mismatch")
    validate_finite_tree(summary, "summary")
    if (summary["gate"] != "V3.0 Gate 1D-C outcome-discrimination study"
            or summary["plan_id"] != plan["plan_id"]
            or summary["plan_version"] != plan["plan_version"]
            or summary["plan_canonical_hash"] != PLAN_CANONICAL
            or summary["plan_raw_sha256"] != PLAN_RAW
            or summary["execution_sha"] != receipt["authorized_execution_sha"]
            or summary["branch"] != BRANCH
            or summary["python"] != receipt["python"]
            or summary["implementation_sha256"] != receipt["source_sha256"]):
        raise ValueError("summary provenance mismatch")
    if summary["equation_version"] != plan["equation_version_expected"] \
            or not isinstance(summary["platform"], str) \
            or not summary["platform"]:
        raise ValueError("summary equation/platform provenance mismatch")
    inventory = contract["registered_execution_inventory"]
    registered = summary["registered"]
    expected_registered = {
        "worlds": list(WORLD_ORDER), "arms": list(ARM_ORDER),
        "dt_labels": list(DT_ORDER), "total_runs": 30,
        "run_length_ticks": 200, "trace_rows": 6000,
        "burn_in_ticks": 50, "measurement_ticks": 150,
        "persistence_window_ticks": 20, "deterministic": True,
        "seed": None, "frozen_order": inventory["run_ids"],
    }
    if registered != expected_registered or summary["n_runs"] != 30:
        raise ValueError("summary registered inventory mismatch")
    run_ids = inventory["run_ids"]
    if set(summary["runs"]) != set(run_ids):
        raise ValueError("summary run records differ from frozen inventory")
    for run_identifier in run_ids:
        record = summary["runs"][run_identifier]
        world, arm, label = run_identifier.split("|")
        if set(record) != set(RUN_RECORD_FIELDS) \
                or record.get("run_id") != run_identifier \
                or record.get("world") != world or record.get("arm") != arm \
                or record.get("dt_label") != label \
                or record.get("outcome_class") not in OUTCOME_ORDER:
            raise ValueError(f"summary run identity mismatch: {run_identifier}")
        for field in ("dt", "dt_certificate", "r_dt", "total_service",
                      "total_unmet", "total_demand", "ebu_total",
                      "ebu_positive", "ebu_negative", "pbi_service",
                      "pbi_unmet", "accepted_actions", "voluntary_rests",
                      "p1c_rejections", "reserve_crossings", "allee_crossings",
                      "physical_overuse", "negative_corrections",
                      "max_ledger_residual", "selected_edge_switches",
                      "max_simultaneous_actions", "final_burden",
                      "final_viability"):
            _require_number(record[field], f"summary/runs/{run_identifier}/{field}")
        if record["min_sigma"] is not None:
            _require_number(record["min_sigma"],
                            f"summary/runs/{run_identifier}/min_sigma")
        for field in ("pbi_service_by_destination",
                      "pbi_unmet_by_destination", "service_by_destination",
                      "unmet_by_destination", "final_state"):
            _require_number_list(record[field],
                                 f"summary/runs/{run_identifier}/{field}")
        if not isinstance(record["negative_state"], bool) \
                or not isinstance(record["feasible_world"], bool) \
                or not (record["domain_failure_tick"] is None or (
                    isinstance(record["domain_failure_tick"], int)
                    and not isinstance(record["domain_failure_tick"], bool))):
            raise ValueError(f"summary run status schema mismatch: {run_identifier}")
        total_alignment = record["service_alignment_predicate"]
        destination_alignment = record["per_destination_alignment"]
        if arm != ARM_ORDER[3]:
            if total_alignment is not None or destination_alignment is not None:
                raise ValueError(f"non-D run has alignment result: {run_identifier}")
        else:
            if not isinstance(total_alignment, dict) \
                    or set(total_alignment) != set(TOTAL_ALIGNMENT_FIELDS) \
                    or not isinstance(destination_alignment, dict) \
                    or set(destination_alignment) != {
                        "destinations", "any_destination_failure"} \
                    or not isinstance(
                        destination_alignment["any_destination_failure"], bool) \
                    or not isinstance(destination_alignment["destinations"], list):
                raise ValueError(f"D-run alignment schema mismatch: {run_identifier}")
            for destination, value in enumerate(
                    destination_alignment["destinations"]):
                if not isinstance(value, dict) \
                        or set(value) != set(DESTINATION_ALIGNMENT_FIELDS) \
                        or value["destination"] != destination:
                    raise ValueError(
                        f"destination alignment schema mismatch: {run_identifier}")
    pair_keys = {f"{world}|{label}" for world in WORLD_ORDER for label in DT_ORDER}
    comparisons = summary["comparisons"]
    if set(comparisons) != set(COMPARISON_FIELDS) \
            or comparisons["primary_baseline_arm"] != ARM_ORDER[1] \
            or comparisons["forbidden_baseline_arm"] != ARM_ORDER[0] \
            or any(set(comparisons[key]) != pair_keys for key in (
                "A_vs_B_capability_cost", "B_vs_C_observational_identity",
                "B_vs_D_primary_alignment", "S_vs_B_and_D_secondary")) \
            or set(comparisons["timestep_sensitivity"]) != set(WORLD_ORDER):
        raise ValueError("summary comparison schema/inventory mismatch")
    comparison_shapes = {
        "A_vs_B_capability_cost": {
            "pbi_service_A", "pbi_service_B", "capability_cost_absolute",
            "capability_cost_relative", "max_simultaneous_actions_A"},
        "B_vs_C_observational_identity": {
            "identical", "first_difference", "max_state_difference"},
        "B_vs_D_primary_alignment": {
            "pbi_service_B", "pbi_service_D", "service_ratio_D_over_B",
            "pbi_unmet_B_by_destination", "pbi_unmet_D_by_destination",
            "total_predicate", "per_destination_predicate"},
        "S_vs_B_and_D_secondary": {
            "pbi_service_S", "pbi_service_B", "pbi_service_D",
            "pbi_unmet_S_by_destination", "pbi_unmet_B_by_destination",
            "pbi_unmet_D_by_destination"},
    }
    for comparison, fields in comparison_shapes.items():
        if any(set(value) != fields for value in comparisons[comparison].values()):
            raise ValueError(f"summary comparison field mismatch: {comparison}")
    timestep_fields = {"total_alignment_failure_conservative",
                       "total_alignment_failure_near_certificate", "consistent"}
    if any(set(value) != timestep_fields
           for value in comparisons["timestep_sensitivity"].values()):
        raise ValueError("summary timestep-sensitivity field mismatch")
    if set(summary["hypotheses"]) != {f"H{i}" for i in range(1, 11)} \
            or set(summary["falsifiers"]) != {f"F{i}" for i in range(1, 17)}:
        raise ValueError("summary H/F inventory mismatch")
    for index in range(1, 11):
        value = summary["hypotheses"][f"H{index}"]
        if set(value) != {"status", "evidence"} or not isinstance(value["status"], str):
            raise ValueError("hypothesis summary schema mismatch")
    for index in range(1, 17):
        value = summary["falsifiers"][f"F{index}"]
        if set(value) != {"fired", "evidence"} or not isinstance(value["fired"], bool):
            raise ValueError("falsifier summary schema mismatch")
    if set(summary["positive_controls"]) != set(CONTROL_ORDER):
        raise ValueError("positive-control inventory mismatch")
    for control in CONTROL_ORDER:
        if set(summary["positive_controls"][control]) != set(DT_ORDER):
            raise ValueError("positive-control timestep inventory mismatch")
        for label in DT_ORDER:
            value = summary["positive_controls"][control][label]
            required = {"control", "dt_label", "measured_as",
                        "certified_lower_bound", "f4_threshold",
                        "executed_value", "f4_fired"}
            if set(value) != required or value["control"] != control \
                    or value["dt_label"] != label \
                    or not isinstance(value["f4_fired"], bool) \
                    or value["measured_as"] != plan["positive_control"][
                        control]["measured_as"] \
                    or value["certified_lower_bound"] != plan[
                        "positive_control"][control]["certified_lower_bound"][label]:
                raise ValueError("positive-control result schema mismatch")
            bound = value["certified_lower_bound"]
            _require_number(bound, f"summary/positive_controls/{control}/{label}/bound")
            _require_number(value["executed_value"],
                            f"summary/positive_controls/{control}/{label}/executed")
            exact = bound - 1e-9 * (1 + abs(bound))
            if value["f4_threshold"] != exact \
                    or value["f4_fired"] is not (value["executed_value"] < exact):
                raise ValueError("F4 exact threshold mismatch")
    discriminator_keys = {f"{world}|{label}" for world in WORLD_ORDER
                          for label in DT_ORDER}
    if set(summary["discriminator_v2"]) != discriminator_keys:
        raise ValueError("discriminator-v2 key inventory mismatch")
    discriminator_fields = {
        "i_capability_cost_absolute", "ii_service_ratio_delta",
        "iii_max_destination_unmet_delta", "world_discriminating",
    }
    for value in summary["discriminator_v2"].values():
        if set(value) != discriminator_fields \
                or not isinstance(value["world_discriminating"], bool):
            raise ValueError("discriminator-v2 field schema mismatch")
        for field in discriminator_fields - {"world_discriminating"}:
            _require_number(value[field], f"summary/discriminator_v2/{field}")
    o3_fields = {"arm_A_ticks", "multi_action_ticks", "total_group_quote",
                 "total_naive_independent_sum", "total_double_count",
                 "nothing_settled_or_allocated", "note"}
    if set(summary["o3_aggregate_diagnostic"]) != o3_fields:
        raise ValueError("O3 diagnostic field schema mismatch")
    o3 = summary["o3_aggregate_diagnostic"]
    for field in ("arm_A_ticks", "multi_action_ticks", "total_group_quote",
                  "total_naive_independent_sum", "total_double_count"):
        _require_number(o3[field], f"summary/o3_aggregate_diagnostic/{field}")
    if not isinstance(o3["nothing_settled_or_allocated"], bool) \
            or o3["note"] != "settlement-free diagnostic only; O3 remains open":
        raise ValueError("O3 diagnostic value mismatch")
    counts = summary["outcome_class_counts"]
    if not set(counts) <= set(OUTCOME_ORDER) or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in counts.values()) or sum(counts.values()) != 30:
        raise ValueError("outcome-class counts mismatch")
    reconstructed_counts = {}
    for record in summary["runs"].values():
        outcome = record["outcome_class"]
        reconstructed_counts[outcome] = reconstructed_counts.get(outcome, 0) + 1
    if counts != reconstructed_counts:
        raise ValueError("outcome-class counts do not match run records")
    expected_artifacts = {
        "execution_receipt": {"path": RECEIPT_PATH,
                              "bytes": artifact_info[RECEIPT_PATH]["bytes"],
                              "sha256": artifact_info[RECEIPT_PATH]["sha256"]},
        "execution_started": {"path": START_PATH,
                              "bytes": artifact_info[START_PATH]["bytes"],
                              "sha256": artifact_info[START_PATH]["sha256"]},
        "trace": {"path": TRACE_PATH,
                  "bytes": artifact_info[TRACE_PATH]["bytes"],
                  "sha256": artifact_info[TRACE_PATH]["sha256"]},
        "stdout": {"path": STDOUT_PATH,
                   "bytes": artifact_info[STDOUT_PATH]["bytes"],
                   "sha256": artifact_info[STDOUT_PATH]["sha256"]},
        "summary": {"path": SUMMARY_PATH, "runner_completion_sentinel": True,
                    "self_hash_deferred_to_manifest": True},
        "manifest": {"path": MANIFEST_PATH, "written_by_runner": False,
                     "full_study_completion_sentinel": True},
    }
    if summary["registered_artifacts"] != expected_artifacts:
        raise ValueError("summary registered-artifact descriptors mismatch")
    if summary["completion"] != contract[
            "runner_summary_completion_contract"]["completion_exact_values"]:
        raise ValueError("summary completion sentinel contract mismatch")
    if summary["non_claims"] != plan["non_claims"] or len(summary["non_claims"]) != 8:
        raise ValueError("summary frozen nonclaims mismatch")
    return summary


def validate_trace(trace_bytes: bytes, contract: dict, summary: dict,
                   receipt: dict) -> list[dict]:
    try:
        decompressed = gzip.decompress(trace_bytes)
    except (OSError, EOFError) as error:
        raise ValueError(f"trace gzip failure: {error}") from error
    lines = decompressed.splitlines(keepends=True)
    if len(lines) != 6000 or any(not line.endswith(b"\n") for line in lines):
        raise ValueError("trace must contain exactly 6000 LF-terminated rows")
    rows = []
    required_fields = {
        "plan_canonical_hash", "plan_raw_sha256", "equation_version",
        "implementation_sha256", "execution_sha", "run_id", "world", "arm",
        "dt_label", "dt", "dt_certificate", "certificate_kind", "r_dt",
        "tick", "record",
    }
    run_ids = contract["registered_execution_inventory"]["run_ids"]
    for position, line in enumerate(lines):
        row = strict_json_loads(line[:-1])
        if canonical_json_bytes(row) + b"\n" != line or set(row) != required_fields:
            raise ValueError(f"trace row {position} schema/canonical mismatch")
        run_index, tick_offset = divmod(position, 200)
        run_identifier = run_ids[run_index]
        world, arm, label = run_identifier.split("|")
        summary_record = summary["runs"][run_identifier]
        if (row["run_id"] != run_identifier or row["world"] != world
                or row["arm"] != arm or row["dt_label"] != label
                or row["tick"] != tick_offset + 1
                or row["plan_canonical_hash"] != PLAN_CANONICAL
                or row["plan_raw_sha256"] != PLAN_RAW
                or row["equation_version"] != summary["equation_version"]
                or row["execution_sha"] != receipt["authorized_execution_sha"]
                or row["implementation_sha256"] != receipt["source_sha256"][
                    "exp_v30_gate1dc.py"]
                or row["dt"] != summary_record["dt"]
                or row["dt_certificate"] != summary_record["dt_certificate"]
                or row["certificate_kind"] != summary_record["certificate_kind"]
                or row["r_dt"] != summary_record["r_dt"]):
            raise ValueError(f"trace row {position} provenance/order mismatch")
        if (not isinstance(row["record"], dict)
                or set(row["record"]) != set(TICK_RECORD_FIELDS)
                or row["record"].get("tick") != row["tick"]
                or row["record"].get("arm") != arm
                or row["record"].get("dt") != row["dt"]):
            raise ValueError(f"trace row {position} record mismatch")
        validate_finite_tree(row, f"trace/{position}")
        rows.append(row)
    if deterministic_gzip(rows) != trace_bytes:
        raise ValueError("trace is not deterministic single-member gzip")
    for run_index, run_identifier in enumerate(run_ids):
        segment = rows[run_index * 200:(run_index + 1) * 200]
        service = math.fsum(math.fsum(row["record"]["service"]) for row in segment)
        unmet = math.fsum(math.fsum(row["record"]["unmet"]) for row in segment)
        demand = math.fsum(math.fsum(row["record"]["demand_amount"])
                           for row in segment)
        ebu = math.fsum(row["record"]["ebu"] for row in segment)
        ebu_positive = math.fsum(row["record"]["ebu_pos"] for row in segment)
        ebu_negative = math.fsum(row["record"]["ebu_neg"] for row in segment)
        record = summary["runs"][run_identifier]
        for actual, expected, label in (
                (service, record["total_service"], "service"),
                (unmet, record["total_unmet"], "unmet"),
                (demand, record["total_demand"], "demand"),
                (ebu, record["ebu_total"], "ebu"),
                (ebu_positive, record["ebu_positive"], "ebu-positive"),
                (ebu_negative, record["ebu_negative"], "ebu-negative")):
            tolerance = 1e-9 * (1 + abs(expected))
            if abs(actual - expected) > tolerance:
                raise ValueError(f"trace/summary {label} mismatch for {run_identifier}")
    return rows


def _json_number(value) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value):
        raise ValueError("stdout value is not a finite JSON number")
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def expected_stdout_bytes(summary: dict) -> bytes:
    lines = [
        "EBP V3.0 Gate 1D-C - outcome-discrimination study",
        f"execution SHA: {summary['execution_sha']}",
        f"plan canonical hash: {PLAN_CANONICAL}",
        "registered: 3 worlds x 2 timesteps x 5 arms = 30 runs; 200 ticks "
        "each; burn-in 50; measurement 150; no seed",
    ]
    for index, run_identifier in enumerate(summary["registered"]["frozen_order"], 1):
        record = summary["runs"][run_identifier]
        lines.append(
            f"run {index:02d}/30 | {run_identifier} | "
            f"service={_json_number(record['total_service'])} | "
            f"unmet={_json_number(record['total_unmet'])} | "
            f"ebu={_json_number(record['ebu_total'])} | "
            f"r_dt={_json_number(record['r_dt'])}")
    for outcome in OUTCOME_ORDER:
        if outcome in summary["outcome_class_counts"]:
            lines.append(f"outcome | {outcome} | {summary['outcome_class_counts'][outcome]}")
    fired = [f"F{index}" for index in range(1, 17)
             if summary["falsifiers"][f"F{index}"]["fired"]]
    lines.extend([
        "falsifiers fired: " + (", ".join(fired) if fired else "none"),
        "runner outputs validated in memory",
        "trace published durably",
        "stdout complete; summary publication follows",
    ])
    return ("\n".join(lines) + "\n").encode("utf-8")


def validate_stdout(stdout_bytes: bytes, summary: dict) -> None:
    validate_text_bytes(stdout_bytes, "stdout")
    if stdout_bytes != expected_stdout_bytes(summary):
        raise ValueError("stdout grammar/content mismatch or post-summary content")


def _git_bytes(*arguments: str, network: bool = False) -> bytes:
    try:
        completed = subprocess.run(("git",) + arguments, check=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except OSError as error:
        if error.errno in _TRANSIENT_ERRNOS:
            raise TransientFinalizationError(
                f"transient Git errno {error.errno} for {' '.join(arguments)}"
            ) from error
        raise RuntimeError(
            f"Git check failed for {' '.join(arguments)}: {error}") from error
    except subprocess.CalledProcessError as error:
        detail = getattr(error, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        lowered = detail.lower()
        if network and any(
                marker in lowered for marker in _NETWORK_TRANSIENT_MARKERS):
            raise TransientFinalizationError(
                f"transient DNS failure for {' '.join(arguments)}: "
                f"{detail.strip()}") from error
        raise RuntimeError(f"Git check failed for {' '.join(arguments)}: "
                           f"{(detail or str(error)).strip()}") from error
    return completed.stdout


def _git(*arguments: str) -> str:
    return _git_bytes(*arguments).decode("utf-8", errors="strict").strip()


def _validate_runtime(authorized_sha: str) -> None:
    if len(sys.argv) != 1 or sys.argv[0] != "finalize_v30_gate1dc.py":
        raise ValueError("finalizer takes no arguments and requires its exact filename")
    expected = {**EXPECTED_ENVIRONMENT, "EBU_GATE1DC_EXECUTION_SHA": authorized_sha}
    if set(os.environ) != set(expected) or any(
            os.environ.get(key) != value for key, value in expected.items()):
        raise ValueError("environment differs from exact env -i allowlist")
    if re.fullmatch(_SHA40, authorized_sha) is None:
        raise ValueError("normalized execution SHA is not lowercase 40-hex")
    original = tuple(getattr(sys, "orig_argv", ()))
    expected_argv = (PYTHON_INVOKED_AS, "-B", "-s", "-X", "utf8",
                     "finalize_v30_gate1dc.py")
    if original != expected_argv:
        raise ValueError("finalizer Python argv is not the exact frozen invocation")
    if os.path.realpath(PYTHON_INVOKED_AS) != PYTHON_REALPATH \
            or os.path.realpath(sys.executable) != PYTHON_REALPATH \
            or platform.python_version() != PYTHON_VERSION \
            or zlib.ZLIB_VERSION != ZLIB_VERSION \
            or zlib.ZLIB_RUNTIME_VERSION != ZLIB_VERSION:
        raise ValueError("Python or zlib identity mismatch")
    if not (sys.flags.dont_write_bytecode and sys.flags.no_user_site
            and sys.flags.utf8_mode == 1):
        raise ValueError("Python flags mismatch")
    if os.path.realpath(os.getcwd()) != REPOSITORY_ROOT \
            or os.path.realpath(os.path.dirname(__file__)) != REPOSITORY_ROOT:
        raise ValueError("repository root/current directory mismatch")


def _validate_git_state(authorized_sha: str) -> None:
    if _git("rev-parse", "--show-toplevel") != REPOSITORY_ROOT \
            or _git("symbolic-ref", "--quiet", "--short", "HEAD") != BRANCH \
            or _git("rev-parse", "HEAD") != authorized_sha \
            or _git("rev-parse", f"refs/remotes/origin/{BRANCH}") != authorized_sha:
        raise ValueError("branch/local/tracking Git identity mismatch")
    live = _git_bytes("ls-remote", "--heads", REMOTE, REMOTE_REF,
                      network=True).decode("utf-8", errors="strict").strip().splitlines()
    if len(live) != 1 or live[0].split() != [authorized_sha, REMOTE_REF]:
        raise ValueError("live remote ref differs from authorized execution SHA")
    status_lines = _git("status", "--porcelain=v2", "--untracked-files=all").splitlines()
    allowed = {f"? {path}" for path in FINAL_PATHS[:5]}
    allowed |= {f"? {path}" for path in TEMPORARY_PATHS.values()}
    allowed |= {f"? {MANIFEST_PATH}"}
    if any(line not in allowed for line in status_lines):
        raise ValueError(f"tracked or unexpected worktree status: {status_lines}")
    required_finals = {f"? {path}" for path in FINAL_PATHS[:5]}
    if not required_finals <= set(status_lines):
        raise ValueError("worktree does not contain all five runner-complete inputs")


def _validate_sources(authorized_sha: str) -> dict:
    source_hashes = {}
    for path in SOURCE_HASH_ORDER:
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise ValueError(f"source is not regular/non-symlink: {path}")
        tree_line = _git("ls-tree", authorized_sha, "--", path).split(None, 3)
        if len(tree_line) != 4 or tree_line[0:2] != ["100644", "blob"] \
                or tree_line[3] != path:
            raise ValueError(f"source is not exact tracked blob: {path}")
        worktree = open(path, "rb").read()
        committed = _git_bytes("show", f"{authorized_sha}:{path}")
        if worktree != committed:
            raise ValueError(f"source worktree/Git bytes differ: {path}")
        digest = sha256_bytes(worktree)
        if path in FROZEN_SOURCE_HASHES and digest != FROZEN_SOURCE_HASHES[path]:
            raise ValueError(f"frozen source hash mismatch: {path}")
        source_hashes[path] = digest
    return source_hashes


def _load_contract_and_plan(
        receipt_preview: dict, compatibility: dict) -> tuple[dict, dict]:
    contract_raw = open(CONTRACT_PATH, "rb").read()
    plan_raw = open(PLAN_PATH, "rb").read()
    contract = strict_json_loads(contract_raw)
    plan = strict_json_loads(plan_raw)
    if sha256_bytes(contract_raw) != CONTRACT_RAW \
            or sha256_bytes(canonical_json_bytes(contract)) != CONTRACT_CANONICAL \
            or sha256_bytes(plan_raw) != PLAN_RAW \
            or sha256_bytes(canonical_json_bytes(plan)) != PLAN_CANONICAL:
        raise ValueError("contract or plan raw/canonical hash mismatch")
    if sha256_bytes(open(ADDENDUM_PATH, "rb").read()) != ADDENDUM_SHA256 \
            or sha256_bytes(open(
                COMPATIBILITY_ADDENDUM_PATH, "rb").read()) \
            != COMPATIBILITY_ADDENDUM_SHA256 \
            or sha256_bytes(open(PROTOCOL_PATH, "rb").read()) != PROTOCOL_SHA256:
        raise ValueError("operational addendum or protocol hash mismatch")
    legal = contract["legal_and_scientific_status"]
    if (legal["scientific_precedence"] != [PROTOCOL_PATH, PLAN_PATH]
            or legal["scientific_preregistration_unchanged"] is not True
            or receipt_preview.get("source_sha256", {}).get(ADDENDUM_PATH)
            != ADDENDUM_SHA256
            or receipt_preview.get("source_sha256", {}).get(
                COMPATIBILITY_ADDENDUM_PATH) != COMPATIBILITY_ADDENDUM_SHA256
            or receipt_preview.get("source_sha256", {}).get(
                COMPATIBILITY_CONTRACT_PATH) != COMPATIBILITY_CONTRACT_RAW):
        raise ValueError("scientific precedence/addendum receipt lock mismatch")
    if len(contract.get("failure_retry_matrix", [])) != 17 \
            or tuple(contract["state_machine"]["classification_order"]) != STATE_ORDER:
        raise ValueError("failure matrix or seven-state order mismatch")
    expected_paths = {
        "repository_root": REPOSITORY_ROOT, "branch": BRANCH,
        "remote": REMOTE, "remote_ref": REMOTE_REF,
        "result_directory": RESULT_DIRECTORY,
        "execution_receipt": RECEIPT_PATH, "execution_started": START_PATH,
        "stdout": STDOUT_PATH, "trace": TRACE_PATH, "summary": SUMMARY_PATH,
        "manifest": MANIFEST_PATH, "runner": "exp_v30_gate1dc.py",
        "finalizer": "finalize_v30_gate1dc.py",
    }
    inventory = contract["registered_execution_inventory"]
    expected_run_ids = [f"{world}|{arm}|{label}" for world in WORLD_ORDER
                        for label in DT_ORDER for arm in ARM_ORDER]
    expected_temporary_names = {
        "receipt": os.path.basename(TEMPORARY_PATHS[RECEIPT_PATH]),
        "execution_started": os.path.basename(TEMPORARY_PATHS[START_PATH]),
        "trace": os.path.basename(TEMPORARY_PATHS[TRACE_PATH]),
        "stdout": os.path.basename(TEMPORARY_PATHS[STDOUT_PATH]),
        "summary": os.path.basename(TEMPORARY_PATHS[SUMMARY_PATH]),
        "manifest": os.path.basename(TEMPORARY_PATHS[MANIFEST_PATH]),
    }
    if (contract["paths"] != expected_paths
            or tuple(contract["execution_receipt"]["source_hash_order"])
            != ORIGINAL_SOURCE_HASH_ORDER
            or tuple(compatibility["receipt_integration"][
                "top_level_field_order"]) != tuple(
                    contract["execution_receipt"]["field_order"])
            or tuple(compatibility["receipt_integration"][
                "source_sha256_order"]) != SOURCE_HASH_ORDER
            or inventory != {
                "world_order": list(WORLD_ORDER), "timestep_order": list(DT_ORDER),
                "arm_order": list(ARM_ORDER), "run_length_ticks": 200,
                "total_runs": 30, "trace_rows": 6000,
                "run_ids": expected_run_ids}
            or contract["temporary_files"]["names"] != expected_temporary_names
            or contract["runner_summary_completion_contract"][
                "required_top_level_fields"] != list(SUMMARY_FIELDS)
            or [row["path_key"] for row in contract["artifact_inventory"]] != [
                "execution_receipt", "execution_started", "trace", "stdout",
                "summary", "manifest"]):
        raise ValueError("operational contract inventory/schema mismatch")
    return contract, plan


def _read_no_follow(path: str) -> tuple[bytes, os.stat_result]:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    return b"".join(chunks), info


def _read_immutable(path: str) -> bytes:
    payload, info = _read_no_follow(path)
    if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o444:
        raise ValueError(f"artifact is not immutable mode-0444 regular file: {path}")
    matching_aliases = 0
    temporary = TEMPORARY_PATHS[path]
    if os.path.lexists(temporary):
        alias = os.lstat(temporary)
        if (alias.st_dev, alias.st_ino) != (info.st_dev, info.st_ino):
            raise ValueError(f"temporary is not same-inode alias: {temporary}")
        matching_aliases = 1
    if info.st_nlink != 1 + matching_aliases:
        raise ValueError(f"artifact has unenumerated hard link: {path}")
    return payload


def _validate_entries_and_inputs() -> dict:
    directory_info = os.lstat(RESULT_DIRECTORY)
    if (not stat.S_ISDIR(directory_info.st_mode)
            or stat.S_ISLNK(directory_info.st_mode)
            or stat.S_IMODE(directory_info.st_mode) != 0o700):
        raise ValueError("result directory is not regular non-symlink directory")
    allowed = {os.path.basename(path) for path in FINAL_PATHS}
    allowed |= {os.path.basename(path) for path in TEMPORARY_PATHS.values()}
    entries = set(os.listdir(RESULT_DIRECTORY))
    if not entries <= allowed:
        raise ValueError(f"unexpected result-directory entries: {sorted(entries - allowed)}")
    for path in FINAL_PATHS[:5]:
        if not os.path.lexists(path):
            raise ValueError(f"missing runner-complete artifact: {path}")
    payloads = {path: _read_immutable(path) for path in FINAL_PATHS[:5]}
    return payloads


def _require_start_lock_released() -> None:
    descriptor = os.open(START_PATH, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise TransientFinalizationError("original runner lock is still held") from error
        finally:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            except OSError:
                pass
    finally:
        os.close(descriptor)


def _artifact_info(payloads: dict) -> dict:
    return {path: {"bytes": len(payload), "sha256": sha256_bytes(payload)}
            for path, payload in payloads.items()}


def _fsync_directory(path: str) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _unlink_verified_aliases() -> None:
    for path in FINAL_PATHS[:5]:
        temporary = TEMPORARY_PATHS[path]
        if not os.path.lexists(temporary):
            continue
        final_info = os.lstat(path)
        temporary_info = os.lstat(temporary)
        if (final_info.st_dev, final_info.st_ino) != (
                temporary_info.st_dev, temporary_info.st_ino):
            raise ValueError(f"refusing unique temporary residue: {temporary}")
        os.unlink(temporary)
        _fsync_directory(RESULT_DIRECTORY)


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        count = os.write(descriptor, view)
        if count <= 0:
            raise OSError("short manifest write")
        view = view[count:]


def _validate_manifest_resume_state(payload: bytes) -> None:
    """Validate any manifest publication residue without mutating it."""
    temporary = TEMPORARY_PATHS[MANIFEST_PATH]
    final_exists = os.path.lexists(MANIFEST_PATH)
    temporary_exists = os.path.lexists(temporary)
    directory_info = os.stat(RESULT_DIRECTORY, follow_symlinks=False)
    if final_exists:
        if _read_immutable(MANIFEST_PATH) != payload:
            raise ValueError("existing manifest differs from deterministic render")
        return
    if not temporary_exists:
        return
    existing, info = _read_no_follow(temporary)
    if (not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o444
            or info.st_dev != directory_info.st_dev or info.st_nlink != 1
            or existing != payload):
        raise ValueError("preserved manifest temporary cannot be resumed")


def _publish_manifest(payload: bytes) -> None:
    temporary = TEMPORARY_PATHS[MANIFEST_PATH]
    directory_info = os.stat(RESULT_DIRECTORY, follow_symlinks=False)
    if os.path.lexists(MANIFEST_PATH):
        existing = _read_immutable(MANIFEST_PATH)
        if existing != payload:
            raise FileExistsError("existing manifest differs from deterministic render")
        _fsync_directory(RESULT_DIRECTORY)
        if os.path.lexists(temporary):
            final_info = os.lstat(MANIFEST_PATH)
            temporary_info = os.lstat(temporary)
            if (final_info.st_dev, final_info.st_ino) != (
                    temporary_info.st_dev, temporary_info.st_ino):
                raise ValueError("manifest temporary is not final's same-inode alias")
            os.unlink(temporary)
            _fsync_directory(RESULT_DIRECTORY)
        return
    if os.path.lexists(temporary):
        existing, info = _read_no_follow(temporary)
        if (not stat.S_ISREG(info.st_mode)
                or stat.S_IMODE(info.st_mode) != 0o444
                or info.st_dev != directory_info.st_dev or info.st_nlink != 1
                or existing != payload):
            raise ValueError("preserved manifest temporary cannot be resumed")
        os.link(temporary, MANIFEST_PATH, follow_symlinks=False)
        _fsync_directory(RESULT_DIRECTORY)
        os.unlink(temporary)
        _fsync_directory(RESULT_DIRECTORY)
        return
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(temporary, flags, 0o600)
    closed = False
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_dev != directory_info.st_dev:
            raise OSError("manifest temporary is not same-filesystem regular file")
        os.fchmod(descriptor, 0o600)
        if stat.S_IMODE(os.fstat(descriptor).st_mode) != 0o600:
            raise OSError("manifest temporary mode is not 0600")
        _write_all(descriptor, payload)
        os.fsync(descriptor)
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        os.close(descriptor)
        closed = True
        if os.path.lexists(MANIFEST_PATH):
            raise FileExistsError(MANIFEST_PATH)
        os.link(temporary, MANIFEST_PATH, follow_symlinks=False)
        _fsync_directory(RESULT_DIRECTORY)
        os.unlink(temporary)
        _fsync_directory(RESULT_DIRECTORY)
    finally:
        if not closed:
            os.close(descriptor)


def _validate_finalized_filesystem(expected_manifest: bytes,
                                   input_payloads: dict) -> dict:
    expected_entries = {os.path.basename(path) for path in FINAL_PATHS}
    if set(os.listdir(RESULT_DIRECTORY)) != expected_entries:
        raise ValueError("FINALIZED state has missing, temporary, or unexpected entry")
    for path in FINAL_PATHS[:5]:
        if _read_immutable(path) != input_payloads[path]:
            raise ValueError(f"input artifact changed during finalization: {path}")
    if _read_immutable(MANIFEST_PATH) != expected_manifest:
        raise ValueError("manifest changed during final-state classification")
    _require_start_lock_released()
    return {
        "recoverable_runner_complete": True,
        "manifest_valid": True,
        "manifest_exists": True,
        "no_unexpected_entries": True,
        "lock_held": False,
    }


def finalize() -> bytes:
    """Execute the contract's exact 15-step mechanical validation sequence."""
    # Compatibility supersession: normalize and validate its contract before
    # any original finalizer action, source check, or Git subprocess.
    authorized_sha = _normalize_entry_environment()
    compatibility = _validate_compatibility_contract()

    # 1. Exact arguments, normalized environment, runtime, root, and cwd.
    _validate_runtime(authorized_sha)

    # 2. Branch/local/tracking/live refs, index, and exact untracked set.
    _validate_git_state(authorized_sha)

    # 3. Strict contract/plan hashes, addendum hash, scientific precedence.
    receipt_preview_bytes, _receipt_preview_info = _read_no_follow(RECEIPT_PATH)
    receipt_preview = strict_json_loads(receipt_preview_bytes)
    contract, plan = _load_contract_and_plan(receipt_preview, compatibility)

    # 4. Receipt bytes/order/schema/source Git/worktree hashes/immutability.
    receipt_bytes = _read_immutable(RECEIPT_PATH)
    if receipt_bytes != receipt_preview_bytes:
        raise ValueError("receipt changed between contract and receipt validation")
    source_hashes = _validate_sources(authorized_sha)
    receipt = validate_receipt(receipt_bytes, contract, authorized_sha,
                               source_hashes)

    # 5. Execution-start exact bytes, receipt link, SHA, and released lock.
    start_bytes = _read_immutable(START_PATH)
    started = validate_start(start_bytes, contract, receipt,
                             receipt_bytes)
    _require_start_lock_released()

    # 6. Recoverable runner completion, exact entries/modes/aliases/no overwrite.
    payloads = _validate_entries_and_inputs()
    if payloads[RECEIPT_PATH] != receipt_preview_bytes \
            or payloads[START_PATH] != start_bytes:
        raise ValueError("control artifact changed during validation")
    info = _artifact_info(payloads)

    # 7. Strict complete summary and runner-completion declaration.
    summary = validate_summary(payloads[SUMMARY_PATH], contract, plan, receipt,
                               info)

    # 8. Deterministic 6000-row trace and frozen summary cross-checks.
    rows = validate_trace(payloads[TRACE_PATH], contract, summary, receipt)
    if len(rows) != 6000:
        raise ValueError("trace row count mismatch")

    # 9. Exact stdout grammar and no content after its frozen final line.
    validate_stdout(payloads[STDOUT_PATH], summary)

    # 10. SHA-256/byte counts and summary descriptors.
    info = _artifact_info(payloads)
    for key, path in (("execution_receipt", RECEIPT_PATH),
                      ("execution_started", START_PATH),
                      ("trace", TRACE_PATH), ("stdout", STDOUT_PATH)):
        descriptor = summary["registered_artifacts"][key]
        if descriptor["bytes"] != info[path]["bytes"] \
                or descriptor["sha256"] != info[path]["sha256"]:
            raise ValueError(f"summary descriptor mismatch for {path}")

    # 11. Manifest pointers/types/finiteness/cross-file identities.
    if summary["execution_sha"] != receipt["authorized_execution_sha"] \
            or summary["registered"]["frozen_order"] != contract[
                "registered_execution_inventory"]["run_ids"]:
        raise ValueError("manifest source pointer identity mismatch")
    validate_finite_tree(summary, "manifest-source-summary")

    # 12. Complete render and independent rerender, without scientific code.
    first_render = render_manifest(receipt, started, summary, plan, contract, info)
    second_render = render_manifest(
        strict_json_loads(receipt_bytes), strict_json_loads(start_bytes),
        strict_json_loads(payloads[SUMMARY_PATH]),
        strict_json_loads(canonical_json_bytes(plan)),
        strict_json_loads(canonical_json_bytes(contract)),
        strict_json_loads(canonical_json_bytes(info)),
    )
    if first_render != second_render:
        raise ValueError("independent manifest rerenders differ")
    _validate_manifest_resume_state(first_render)

    # 13. Only now complete verified same-inode aliases and fsync the directory.
    _unlink_verified_aliases()
    _fsync_directory(RESULT_DIRECTORY)

    # 14. Exclusive manifest publication or exact frozen resume path.
    _publish_manifest(first_render)

    # 15. Reopen/compare, fsync, classify FINALIZED, fixed stderr success line.
    final_bytes = _read_immutable(MANIFEST_PATH)
    if final_bytes != first_render:
        raise ValueError("published manifest byte mismatch")
    _fsync_directory(RESULT_DIRECTORY)
    state = classify_state(_validate_finalized_filesystem(first_render, payloads))
    if state != "FINALIZED":
        raise ValueError("final state classification mismatch")
    _write_all(2, (f"FINALIZED V3.0 Gate 1D-C at {authorized_sha}: "
                   f"{MANIFEST_PATH}\n").encode("utf-8"))
    return first_render


def main() -> int:
    finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
