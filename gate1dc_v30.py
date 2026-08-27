"""V3.0 Gate 1D-C frozen outcome-discrimination study implementation.

Importing this library performs strict, read-only validation of the locked
plan.  It does not advance a model, execute a run, write an artifact, or
inspect an outcome.  ``gate1dc_tick`` and ``run_arm`` are execution primitives
for the separately authorized future runner; the pre-execution suite is
statically prohibited from calling them.

The decision-path split is load-bearing.  ``DECISION_PATH_FUNCS`` may read
only source-local state/configuration, adjacent LocalViews, edge constants,
the authoritative P1C budget, candidate quantities, exact committed quote
schedules, deterministic identifiers, and (for arm S only) the current-tick
demand-rate vector.  Demand-schedule construction, bounded service, global
diagnostics, predicates, classifications, and records live outside that path.

Released modules are reused without modification: d0_v29, p1c_v29,
ebu_quote_v30, and service_v30.  Numerical validation is not proof.  O3
remains open; arm A settles and allocates no EBU.  Gate 1E and Gate 2 remain
untouched.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Mapping, Optional, Sequence

import d0_v29 as d0
import ebu_quote_v30 as eq
import p1c_v29 as p1c
import service_v30 as sv


PLAN_PATH = "v30_gate1dc_outcome_discrimination_plan.json"
PLAN_RAW = "91a2c42558c09051988bfebe6f0d11c0fab440340d161171afc4442c86fa30fe"
PLAN_CANONICAL = "f9dd4b804a83744268bffe48d2d3861825cbc96d90aa871f348251e4108ef287"
CONTRACT_PATH = "v30_gate1dc_execution_finalization_contract.json"
CONTRACT_RAW = "81d96d3f377a2d1d2471b38328af8968b9c728db590023d0d921e4312cd23155"
CONTRACT_CANONICAL = "ed90eaf901b506cc91e0a7ba3c4a6329ad6f8730278716383c07f525b748e208"
ADDENDUM_PATH = "V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md"
ADDENDUM_SHA256 = "28d47aa314e74206b4cc3da9ceccfbf0a08bd2196930490636c1d3c991039fa1"
COMPATIBILITY_ADDENDUM_PATH = (
    "V3.0_GATE1D_C_MACOS_ENVIRONMENT_COMPATIBILITY_ADDENDUM.md")
COMPATIBILITY_ADDENDUM_SHA256 = (
    "2e439afad6ba7532aae83631ef4fb7ea6648980be035674f8e2d13faeecd9b51")
COMPATIBILITY_CONTRACT_PATH = (
    "v30_gate1dc_macos_environment_compatibility_contract.json")
COMPATIBILITY_CONTRACT_RAW = (
    "628ee126011b3bdb6587af53c64f69db2fbd86d92deaef27ff60366b4d80ef8b")
COMPATIBILITY_CONTRACT_CANONICAL = (
    "0fbdaf54734d10a88172ed79451dc2e7a31e4021b66c765d5df164a1d93f3077")
LAUNCHER_COMPATIBILITY_ADDENDUM_PATH = (
    "V3.0_GATE1D_C_MACOS_PYTHON_LAUNCHER_COMPATIBILITY_ADDENDUM.md")
LAUNCHER_COMPATIBILITY_ADDENDUM_SHA256 = (
    "d81afc5d77e1d2c7ccd9ceaae44d96ce33ddbb85ddc35fe0a0a0e1141394e8c3")
LAUNCHER_COMPATIBILITY_CONTRACT_PATH = (
    "v30_gate1dc_macos_python_launcher_compatibility_contract.json")
LAUNCHER_COMPATIBILITY_CONTRACT_RAW = (
    "b937e0ed047799fbcce9d6390ca2836b0db6ca18c0a2b8ab854f89395bd79c82")
LAUNCHER_COMPATIBILITY_CONTRACT_CANONICAL = (
    "b937e0ed047799fbcce9d6390ca2836b0db6ca18c0a2b8ab854f89395bd79c82")

EXEC_ARMS = (
    "A_full_multi_edge_p1c",
    "B_restricted_matched_non_ebu",
    "C_restricted_observational_quote",
    "D_restricted_exact_total_quote_greedy",
    "S_restricted_local_service_priority",
)
DT_LABELS = ("conservative", "near_certificate")
WORLD_NAMES = ("DC1_flux_lock", "DC2_capacity_split", "DC3_demand_pulse")
FRACTIONS = (0.25, 0.5, 0.75, 1.0)
RUN_TICKS = 200
BURN_IN_TICKS = 50
MEASUREMENT_TICKS = 150
PERSISTENCE_WINDOW = 20
LAM_L = 0.1
C0 = 0.0
EPS_X = EPS_U = 0.0
NUM_TOL_REL = 1e-9
SERVICE_REL = UNMET_REL = 0.05
SERVICE_ABS = UNMET_ABS = 1.0
EBU_THRESHOLD = 1.0
DELTA_R = 0.5

FUTURE_ARTIFACTS = (
    "exp_v30_gate1dc.py",
    "results/v3.0/gate1dc/MANIFEST.md",
    "results/v3.0/gate1dc/v30_gate1dc_summary.json",
    "results/v3.0/gate1dc/v30_gate1dc_trace.jsonl.gz",
    "results/v3.0/gate1dc/v30_gate1dc_stdout.txt",
)
SUMMARY_PATH = FUTURE_ARTIFACTS[2]
TRACE_PATH = FUTURE_ARTIFACTS[3]
MANIFEST_PATH = FUTURE_ARTIFACTS[1]
STDOUT_PATH = FUTURE_ARTIFACTS[4]
RESULT_DIRECTORY = "results/v3.0/gate1dc"
RECEIPT_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_execution_receipt.json"
EXECUTION_STARTED_PATH = f"{RESULT_DIRECTORY}/v30_gate1dc_execution_started.json"
FINALIZER_PATH = "finalize_v30_gate1dc.py"
REGISTERED_ARTIFACTS = (
    RECEIPT_PATH,
    EXECUTION_STARTED_PATH,
    TRACE_PATH,
    STDOUT_PATH,
    SUMMARY_PATH,
    MANIFEST_PATH,
)
TEMPORARY_BASENAMES = (
    ".v30_gate1dc_execution_receipt.json.tmp",
    ".v30_gate1dc_execution_started.json.tmp",
    ".v30_gate1dc_trace.jsonl.gz.tmp",
    ".v30_gate1dc_stdout.txt.tmp",
    ".v30_gate1dc_summary.json.tmp",
    ".MANIFEST.md.tmp",
)
ORIGINAL_SOURCE_HASH_ORDER = (
    "AGENTS.md",
    "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md",
    PLAN_PATH,
    ADDENDUM_PATH,
    CONTRACT_PATH,
    "gate1dc_v30.py",
    "test_v30_gate1dc.py",
    "exp_v30_gate1dc.py",
    FINALIZER_PATH,
    "d0_v29.py",
    "p1c_v29.py",
    "ebu_quote_v30.py",
    "service_v30.py",
)
ENVIRONMENT_SOURCE_HASH_ORDER = (
    "AGENTS.md",
    "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md",
    PLAN_PATH,
    ADDENDUM_PATH,
    CONTRACT_PATH,
    COMPATIBILITY_ADDENDUM_PATH,
    COMPATIBILITY_CONTRACT_PATH,
    "gate1dc_v30.py",
    "test_v30_gate1dc.py",
    "exp_v30_gate1dc.py",
    FINALIZER_PATH,
    "d0_v29.py",
    "p1c_v29.py",
    "ebu_quote_v30.py",
    "service_v30.py",
)
SOURCE_HASH_ORDER = (
    "AGENTS.md",
    "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md",
    PLAN_PATH,
    ADDENDUM_PATH,
    CONTRACT_PATH,
    COMPATIBILITY_ADDENDUM_PATH,
    COMPATIBILITY_CONTRACT_PATH,
    LAUNCHER_COMPATIBILITY_ADDENDUM_PATH,
    LAUNCHER_COMPATIBILITY_CONTRACT_PATH,
    "gate1dc_v30.py",
    "test_v30_gate1dc.py",
    "exp_v30_gate1dc.py",
    FINALIZER_PATH,
    "d0_v29.py",
    "p1c_v29.py",
    "ebu_quote_v30.py",
    "service_v30.py",
)
STATE_CLASSIFICATION_ORDER = (
    "FINALIZED", "RUNNER_COMPLETE", "EXECUTING", "ATTEMPT_COMMITTED",
    "PREFLIGHT", "UNSTARTED", "FAILED_OR_INTERRUPTED",
)
OUTCOME_CLASS_ORDER = (
    "numerical_or_domain_failure", "systemic_collapse",
    "destructive_service", "physical_impossibility",
    "distributive_or_policy_under_service",
    "safe_rationing_physical_scarcity", "preserve_but_under_serve",
    "preserve_and_serve", "unclassified",
)

TRACE_PROVENANCE_FIELDS = (
    "plan_canonical_hash", "plan_raw_sha256", "equation_version",
    "implementation_sha256", "execution_sha",
    "run_id", "world", "arm", "dt_label", "dt", "dt_certificate",
    "certificate_kind", "r_dt", "tick", "record",
)
SUMMARY_REQUIRED_BLOCKS = (
    "gate", "plan_id", "plan_version", "plan_canonical_hash",
    "plan_raw_sha256", "equation_version", "implementation_sha256",
    "execution_sha", "branch", "python", "platform", "registered",
    "n_runs", "runs", "comparisons", "discriminator_v2",
    "positive_controls", "hypotheses", "falsifiers",
    "o3_aggregate_diagnostic", "outcome_class_counts",
    "registered_artifacts", "completion", "non_claims",
)
MANIFEST_REQUIRED_SECTIONS = (
    "provenance and execution SHA", "artifact SHA-256 and byte counts",
    "30-run frozen inventory and ordering", "6000 ordered trace rows",
    "plan and implementation hashes", "pre-execution validation",
    "PC1-PC4 and F1-F16", "single-execution and no-rerun record",
    "limitations and non-claims", "next stage not begun",
)

_TIMESTEP_LOCKS = {
    "DC1_flux_lock": (5.0, 0.7892659826361483, 0.5083884087442806,
                      0.5083884087442806, "gershgorin",
                      0.2541942043721403, 0.45754956786985257),
    "DC2_capacity_split": (5.0, 0.8293593199253576, 0.3837666698647222,
                           0.3837666698647222, "gershgorin",
                           0.1918833349323611, 0.34539000287825),
    "DC3_demand_pulse": (5.0, 0.7892659826361483, 0.5083884087442806,
                         0.5083884087442806, "gershgorin",
                         0.2541942043721403, 0.45754956786985257),
}
_WORLD_LOCKS = {
    "DC1_flux_lock": {
        "cells": [
            {"alpha": 1.0, "beta": 0.5, "chi": 1.0, "L": 5.0,
             "U": 25.0, "R": 8.0, "K": 20.0, "source": "logistic",
             "rho": 0.6},
            {"alpha": 1.0, "beta": 0.5, "chi": 0.0, "L": 5.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
            {"alpha": 2.5, "beta": 0.5, "chi": 0.0, "L": 5.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
        ],
        "edges": [
            {"i": 0, "j": 1, "M": 0.28, "theta": 0.05, "eta": 0.9},
            {"i": 0, "j": 2, "M": 0.08, "theta": 0.05, "eta": 0.9},
        ],
        "x0": [12.0, 0.0, 3.5], "demand": [0.0, 3.0, 0.5],
        "demand_schedule": {"type": "constant"},
        "types": {"0": "regenerative"}, "feasible": False,
    },
    "DC2_capacity_split": {
        "cells": [
            {"alpha": 1.0, "beta": 0.5, "chi": 1.0, "L": 5.0,
             "U": 25.0, "R": 8.0, "K": 20.0, "source": "logistic",
             "rho": 0.6},
            {"alpha": 2.5, "beta": 0.5, "chi": 0.0, "L": 4.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
            {"alpha": 0.55, "beta": 0.5, "chi": 0.0, "L": 5.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
            {"alpha": 1.2, "beta": 0.5, "chi": 0.0, "L": 6.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
        ],
        "edges": [
            {"i": 0, "j": 1, "M": 0.06, "theta": 0.05, "eta": 0.95},
            {"i": 0, "j": 2, "M": 0.28, "theta": 0.05, "eta": 0.85},
            {"i": 0, "j": 3, "M": 0.13, "theta": 0.05, "eta": 0.75},
        ],
        "x0": [12.0, 2.0, 0.5, 1.8], "demand": [0.0, 0.4, 0.9, 0.6],
        "demand_schedule": {"type": "constant"},
        "types": {"0": "regenerative"}, "feasible": True,
    },
    "DC3_demand_pulse": {
        "cells": [
            {"alpha": 1.0, "beta": 0.5, "chi": 1.0, "L": 5.0,
             "U": 25.0, "R": 8.0, "K": 20.0, "source": "logistic",
             "rho": 0.6},
            {"alpha": 1.0, "beta": 0.5, "chi": 0.0, "L": 5.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
            {"alpha": 2.5, "beta": 0.5, "chi": 0.0, "L": 5.0,
             "U": 15.0, "R": 0.0, "K": 20.0},
        ],
        "edges": [
            {"i": 0, "j": 1, "M": 0.28, "theta": 0.05, "eta": 0.9},
            {"i": 0, "j": 2, "M": 0.08, "theta": 0.05, "eta": 0.9},
        ],
        "x0": [12.0, 0.0, 0.5], "demand": [0.0, 3.0, 0.0],
        "demand_schedule": {
            "type": "pulse_amount", "pulse_destination": 2,
            "pulse_amount_P": 1.0,
            "pulse_ticks": [10, 35, 60, 85, 110, 135, 160, 185],
            "window_pulses": 6,
        },
        "types": {"0": "regenerative"}, "feasible": False,
    },
}
_PC_BOUNDS = {
    "PC1_DC1_S_starves_dst2": {
        "conservative": 15.564565327910522,
        "near_certificate": 30.816217590238942,
    },
    "PC2_DC3_S_misses_pulses": {
        "conservative": 5.5, "near_certificate": 5.5,
    },
    "PC3_DC1_A_vs_B_capability_cost": {
        "conservative": 18.427051868293074,
        "near_certificate": 28.012116339140597,
    },
    "PC4_DC2_A_vs_B_capacity_gap": {
        "conservative": 7.476597260519597,
        "near_certificate": 25.384451045418373,
    },
}


def _reject_nonfinite(name):
    raise ValueError(f"non-finite JSON constant {name!r} rejected")


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


def plan_canonical_hash(plan: dict) -> str:
    encoded = json.dumps(plan, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_plan(path: str = PLAN_PATH,
              expected_canonical: str = PLAN_CANONICAL,
              expected_raw: Optional[str] = PLAN_RAW) -> dict:
    with open(path, "rb") as handle:
        raw = handle.read()
    raw_hash = hashlib.sha256(raw).hexdigest()
    if expected_raw is not None and raw_hash != expected_raw:
        raise SystemExit(f"FATAL: raw Gate 1D-C plan SHA-256 mismatch: {raw_hash}")
    plan = strict_json_loads(raw)
    canonical = plan_canonical_hash(plan)
    if canonical != expected_canonical:
        raise SystemExit(
            f"FATAL: canonical Gate 1D-C plan SHA-256 mismatch: {canonical}")
    return plan


def _need(container, key, kind=None, context=""):
    if key not in container:
        raise ValueError(f"plan schema: missing {context}{key!r}")
    value = container[key]
    if kind is not None and not isinstance(value, kind):
        raise ValueError(
            f"plan schema: {context}{key!r} is {type(value).__name__}, "
            f"expected {kind}")
    return value


def _finite_tree(value, path="plan"):
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        if not math.isfinite(value):
            raise ValueError(f"plan schema: non-finite numeric value at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _finite_tree(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _finite_tree(item, f"{path}.{key}")
        return
    raise ValueError(f"plan schema: unsupported value at {path}")


def validate_plan(plan: dict) -> None:
    """Fail closed on every execution-relevant frozen plan contract."""
    _finite_tree(plan)
    if _need(plan, "plan_id", str) != "v30_gate1dc_outcome_discrimination":
        raise ValueError("plan schema: wrong plan_id")
    if _need(plan, "plan_version", str) != "1.0.0":
        raise ValueError("plan schema: wrong plan_version")
    if _need(plan, "equation_version_expected", str) != eq.EQUATION_VERSION:
        raise ValueError("plan schema: equation version mismatch")

    size = _need(plan, "experiment_size", dict)
    locked_size = {
        "worlds": 3, "arms": 5, "timesteps": 2, "total_runs": 30,
        "run_length_ticks": RUN_TICKS, "burn_in_ticks": BURN_IN_TICKS,
        "persistence_window_ticks": PERSISTENCE_WINDOW,
        "stochastic_study": False,
        "frozen_order": ("sorted world names x dt labels (conservative, "
                         "near_certificate) x executable arms (A, B, C, D, S)"),
    }
    for key, expected in locked_size.items():
        if _need(size, key, type(expected), "experiment_size.") != expected:
            raise ValueError(f"plan schema: experiment_size.{key} mismatch")
    if size["total_runs"] != size["worlds"] * size["arms"] * size["timesteps"]:
        raise ValueError("plan schema: inconsistent run count")

    menu = _need(plan, "quantity_menu", dict)
    if menu.get("fractions") != list(FRACTIONS):
        raise ValueError("plan schema: quantity-menu fractions mismatch")
    if menu.get("identical_for_arms") != ["B", "C", "D", "S"]:
        raise ValueError("plan schema: common-menu arm set/order mismatch")

    arms = _need(plan, "arms", dict)
    if tuple(k[0] for k in arms if k[:1] in {"A", "B", "C", "D", "S"}) != \
            ("A", "B", "C", "D", "S"):
        raise ValueError("plan schema: arm order mismatch")
    for long_name in EXEC_ARMS:
        _need(arms, long_name, str, "arms.")
    if "NOT REGISTERED FOR EXECUTION" not in _need(
            arms, "E_aggregate_source_group_quote", str, "arms."):
        raise ValueError("plan schema: arm E became executable")
    if arms.get("primary_comparison") != "D versus B":
        raise ValueError("plan schema: primary comparison mismatch")
    if arms.get("primary_baseline") != "B_restricted_matched_non_ebu":
        raise ValueError("plan schema: primary baseline mismatch")
    if arms.get("forbidden_baseline") != "A_full_multi_edge_p1c":
        raise ValueError("plan schema: forbidden baseline mismatch")

    worlds = _need(plan, "worlds", dict)
    if tuple(worlds) != WORLD_NAMES:
        raise ValueError("plan schema: world names/order mismatch")
    for name, expected in _WORLD_LOCKS.items():
        actual = worlds[name]
        for key, value in expected.items():
            if key == "demand_schedule" and name == "DC3_demand_pulse":
                for subkey, subvalue in value.items():
                    if actual[key].get(subkey) != subvalue:
                        raise ValueError(
                            f"plan schema: {name}.{key}.{subkey} mismatch")
            elif actual.get(key) != value:
                raise ValueError(f"plan schema: {name}.{key} mismatch")

    timestep = _need(_need(plan, "timestep", dict), "per_world", dict,
                     "timestep.")
    if tuple(timestep) != WORLD_NAMES:
        raise ValueError("plan schema: timestep world order mismatch")
    fields = ("lv_exact", "one_edge_certificate", "gershgorin_certificate",
              "binding_certificate", "binding_kind",
              "registered_conservative_dt", "registered_near_certificate_dt")
    for name, expected in _TIMESTEP_LOCKS.items():
        if tuple(timestep[name][key] for key in fields) != expected:
            raise ValueError(f"plan schema: {name} timestep certificate mismatch")
        if timestep[name].get("r_dt_conservative") != 0.5 \
                or timestep[name].get("r_dt_near") != 0.9:
            raise ValueError(f"plan schema: {name} r_dt mismatch")

    if list(_need(plan, "hypotheses", dict)) != [f"H{i}" for i in range(1, 11)]:
        raise ValueError("plan schema: H1-H10 mismatch")
    if list(_need(plan, "falsifiers", dict)) != [f"F{i}" for i in range(1, 17)]:
        raise ValueError("plan schema: F1-F16 mismatch")
    controls = _need(plan, "positive_control", dict)
    if list(controls)[:4] != list(_PC_BOUNDS) or list(controls)[4:] != ["rule"]:
        raise ValueError("plan schema: PC1-PC4 mismatch")
    for key, bounds in _PC_BOUNDS.items():
        if controls[key].get("certified_lower_bound") != bounds:
            raise ValueError(f"plan schema: {key} certified bound mismatch")
        _need(controls[key], "measured_as", str, f"positive_control.{key}.")
    f4_rule = controls["rule"]
    if "1e-9*(1+|bound|)" not in f4_rule or "no separate slack floor" not in f4_rule:
        raise ValueError("plan schema: F4 threshold rule mismatch")

    predicate = _need(plan, "service_alignment_predicate", dict)
    required_predicate_tokens = ("VERBATIM", "5%", "1.0", "20 ticks",
                                 "delta_R = 0.5", "1e-9*(1+|value|)")
    if not all(token in predicate.get("reuse", "")
               for token in required_predicate_tokens):
        raise ValueError("plan schema: Gate 1D predicate constants mismatch")
    if "per destination" not in predicate.get("per_destination_channel", ""):
        raise ValueError("plan schema: per-destination channel missing")
    if "VERBATIM" not in _need(plan, "outcome_classes", dict).get("reuse", ""):
        raise ValueError("plan schema: outcome precedence is not verbatim")
    if _need(plan, "discriminator_v2", dict).get("tolerance") != \
            "1e-9 * (1 + |value|)":
        raise ValueError("plan schema: discriminator tolerance mismatch")

    planned = _need(plan, "planned_future_files_not_created", list)
    expected_prefixes = ("gate1dc_v30.py", "test_v30_gate1dc.py") + FUTURE_ARTIFACTS
    if tuple(item.split(" ", 1)[0] for item in planned) != expected_prefixes:
        raise ValueError("plan schema: future artifact filenames mismatch")
    requirements = _need(plan, "harness_requirements", list)
    for token in ("canonical plan hash", "every certificate", "no command-line",
                  "strict JSON", "per-tick capability-identity",
                  "per-tick demand_rate vector", "every registered metric"):
        if not any(token in item for item in requirements):
            raise ValueError(f"plan schema: harness requirement {token!r} missing")


PLAN = load_plan()
validate_plan(PLAN)

_DT_FIELD = {
    "conservative": "registered_conservative_dt",
    "near_certificate": "registered_near_certificate_dt",
}
MENU_CONTRACT_HASH = hashlib.sha256(json.dumps(
    {"fractions": FRACTIONS, "arms": EXEC_ARMS[1:],
     "cap": "authoritative-p1c-before-ranking", "unsafe": "removed"},
    sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_world(name: str):
    """Reconstruct one locked static world; no state is advanced."""
    if name not in WORLD_NAMES:
        raise ValueError(f"unregistered world {name!r}")
    spec = PLAN["worlds"][name]
    cells = tuple(
        d0.Cell(**{key: float(value) for key, value in cell.items()
                   if key not in ("source", "rho")},
                **({"source": cell["source"], "rho": float(cell["rho"])}
                   if "source" in cell else {}))
        for cell in spec["cells"])
    edges = tuple(d0.Edge(i=int(edge["i"]), j=int(edge["j"]),
                          M=float(edge["M"]), theta=float(edge["theta"]),
                          eta=float(edge["eta"]))
                  for edge in spec["edges"])
    world = d0.World(cells=cells, edges=edges)
    configs = {
        int(cell_id): p1c.SourceConfig(
            source_id=int(cell_id), source_type=source_type,
            R_eff=world.cells[int(cell_id)].R, eps_x=EPS_X, eps_u=EPS_U)
        for cell_id, source_type in spec["types"].items()
    }
    meta = {"feasible": spec["feasible"], "family": spec["family"],
            "note": spec["note"]}
    return (world, tuple(float(v) for v in spec["x0"]), configs,
            tuple(float(v) for v in spec["demand"]), meta)


def world_certificates(name: str) -> dict:
    world, *_ = build_world(name)
    locked = PLAN["timestep"]["per_world"][name]
    lv = d0.lv_exact(world)
    one_edge = min(d0.one_edge_dt_certificate(edge, lv)
                   for edge in world.edges)
    gershgorin = d0.gershgorin_dt_certificate(world, lv)
    binding = min(one_edge, gershgorin)
    kind = "gershgorin" if gershgorin <= one_edge else "one_edge"
    got = {
        "lv_exact": lv, "one_edge_certificate": one_edge,
        "gershgorin_certificate": gershgorin,
        "binding_certificate": binding, "binding_kind": kind,
        "registered_conservative_dt": 0.5 * binding,
        "registered_near_certificate_dt": 0.9 * binding,
    }
    for key, value in got.items():
        if locked.get(key) != value:
            raise SystemExit(
                f"FATAL: {name} certificate {key}: {value!r} != {locked.get(key)!r}")
    return got


def world_dts(name: str) -> dict:
    certificate = world_certificates(name)
    result = {}
    for label in DT_LABELS:
        dt = certificate[_DT_FIELD[label]]
        r_dt = dt / certificate["binding_certificate"]
        if r_dt > 1.0:
            raise SystemExit(f"FATAL: {name}/{label} has r_dt > 1")
        result[label] = dt
    return result


def demand_rate_for_tick(world_name: str, dt_label: str, tick: int) -> tuple:
    """Construct only the current tick's demand input from the frozen plan."""
    if not isinstance(tick, int) or isinstance(tick, bool) \
            or not 1 <= tick <= RUN_TICKS:
        raise ValueError(f"tick must be an integer in [1, {RUN_TICKS}]")
    dt = world_dts(world_name)[dt_label]
    spec = PLAN["worlds"][world_name]
    demand = [float(value) for value in spec["demand"]]
    schedule = spec["demand_schedule"]
    if schedule["type"] == "constant":
        return tuple(demand)
    if schedule["type"] != "pulse_amount":
        raise ValueError("unregistered demand schedule type")
    destination = int(schedule["pulse_destination"])
    demand[destination] = (float(schedule["pulse_amount_P"]) / dt
                           if tick in schedule["pulse_ticks"] else 0.0)
    return tuple(demand)


# ---------------------------------------------------------------------------
# Decision path: filtering/menu construction precedes every selector.
# ---------------------------------------------------------------------------
def screen_budget(cfg: p1c.SourceConfig, x: float, u: float, dt: float):
    state = p1c.classify_state(cfg, x, u, dt)
    if state == "P" and cfg.source_type == "regenerative":
        return state, p1c.robust_budget(cfg, x, u, dt)
    return state, 0.0


def candidate_menu(world: d0.World, x, u, sid: int,
                   cfg: p1c.SourceConfig, dt: float):
    """One budget-capped physically feasible menu shared by B/C/D/S."""
    state, budget = screen_budget(cfg, x[sid], u[sid], dt)
    candidates = []
    if budget <= 0.0:
        return state, budget, candidates
    source_view = d0.local_view(world.cells[sid], x[sid])
    for edge_index, edge in enumerate(world.edges):
        if edge.i != sid:
            continue
        destination_view = d0.local_view(world.cells[edge.j], x[edge.j])
        force, raw_flux = d0.edge_flux(source_view, destination_view, edge)
        if raw_flux <= 0.0:
            continue
        edge_max = min(raw_flux, budget)
        for quant_index, fraction in enumerate(FRACTIONS):
            scaled = d0.Edge(i=edge.i, j=edge.j, M=fraction * edge.M,
                             theta=edge.theta, eta=edge.eta)
            force_scaled, requested = d0.edge_flux(
                source_view, destination_view, scaled)
            if force_scaled != force:
                raise AssertionError("mobility scaling changed force")
            accepted = min(requested, budget)
            if accepted <= 0.0:
                continue
            candidates.append({
                "edge": edge_index, "quant_index": quant_index,
                "frac": fraction, "f": force, "J": raw_flux,
                "q_req": requested, "q_e_max": edge_max,
                "q_acc": accepted,
            })
    return state, budget, candidates


def quote_schedule_for(world: d0.World, x, u, dt: float, candidate: dict,
                       tick: int):
    if candidate["q_acc"] < 0.0 or candidate["q_acc"] > candidate["q_e_max"]:
        raise ValueError("candidate quote quantity outside [0, q_e_max]")
    edge = world.edges[candidate["edge"]]
    quote_input = eq.LocalQuoteInput(
        src=d0.local_view(world.cells[edge.i], x[edge.i]),
        dst=d0.local_view(world.cells[edge.j], x[edge.j]),
        u_src=u[edge.i], u_dst=u[edge.j], dt=dt, eta=edge.eta,
        q_req=candidate["q_req"], q_acc=candidate["q_acc"],
        source_id=edge.i, dest_id=edge.j,
        config_id=f"cfg:{edge.i}:R{world.cells[edge.i].R}")
    cost = eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, c0=C0,
                          c1=LAM_L * dt * (1.0 - edge.eta))
    return eq.build_quote(quote_input, cost, f"pass-{tick}", tick, 0)


def continuous_vertex_diagnostic(world: d0.World, x, u, dt: float,
                                 candidate: dict) -> Optional[float]:
    edge = world.edges[candidate["edge"]]
    source, destination = world.cells[edge.i], world.cells[edge.j]
    z_source = x[edge.i] + dt * u[edge.i]
    z_destination = x[edge.j] + dt * u[edge.j]
    destination_deficit = max(0.0, destination.L - z_destination)
    source_deficit = max(0.0, source.L - z_source)
    active_source_alpha = source.alpha if z_source < source.L else 0.0
    denominator = 2.0 * dt * (
        destination.alpha * edge.eta * edge.eta + active_source_alpha)
    if denominator <= 0.0:
        return None
    numerator = (2.0 * destination.alpha * edge.eta * destination_deficit
                 - 2.0 * active_source_alpha * source_deficit
                 - LAM_L * (1.0 - edge.eta))
    return numerator / denominator if numerator > 0.0 else 0.0


def select_arm_B(candidates: Sequence[dict]) -> Optional[dict]:
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: (
        candidate["f"], candidate["q_acc"], -candidate["edge"],
        -candidate["quant_index"]))


def select_arm_D(candidates: Sequence[dict],
                 exact_total_quotes: Sequence[float]) -> Optional[int]:
    """Rank by exact total local EBU only; per-unit values never enter."""
    if len(candidates) != len(exact_total_quotes):
        raise ValueError("candidates/quotes length mismatch")
    best = None
    for index, (candidate, quote) in enumerate(zip(candidates,
                                                   exact_total_quotes)):
        key = (quote, -candidate["edge"], -candidate["quant_index"])
        if best is None or key > best[0]:
            best = (key, index, quote)
    return None if best is None or best[2] <= 0.0 else best[1]


def select_arm_S(candidates: Sequence[dict], current_demand_rate,
                 world: d0.World) -> Optional[dict]:
    """Use only adjacent destinations' declared current-tick demand."""
    if not candidates:
        return None

    def score(candidate):
        edge = world.edges[candidate["edge"]]
        indicator = 1.0 if current_demand_rate[edge.j] > 0.0 else 0.0
        return edge.eta * candidate["q_acc"] * indicator

    best = max(candidates, key=lambda candidate: (
        score(candidate), -candidate["edge"], -candidate["quant_index"]))
    return best if score(best) > 0.0 else None


DECISION_PATH_FUNCS = (
    screen_budget, candidate_menu, quote_schedule_for,
    select_arm_B, select_arm_D, select_arm_S,
)


def shaped_active_world(world: d0.World,
                        candidate: Optional[dict]) -> d0.World:
    if candidate is None:
        return d0.World(cells=world.cells, edges=())
    edge = world.edges[candidate["edge"]]
    shaped = d0.Edge(i=edge.i, j=edge.j,
                     M=candidate["frac"] * edge.M,
                     theta=edge.theta, eta=edge.eta)
    return d0.World(cells=world.cells, edges=(shaped,))


def group_quote_diagnostic(world: d0.World, x, u, dt: float,
                           edge_q_acc: Sequence[float], tick: int) -> dict:
    """Settlement-free arm-A group quote; nothing is issued or allocated."""
    active = [(index, edge, quantity)
              for index, (edge, quantity) in enumerate(zip(world.edges,
                                                             edge_q_acc))
              if quantity > 0.0]
    if not active:
        return {"group_quote": 0.0, "naive_independent_sum": 0.0,
                "double_count": 0.0, "n_actions": 0}
    involved = sorted({edge.i for _, edge, _ in active}
                      | {edge.j for _, edge, _ in active})
    z = {cell: x[cell] + dt * u[cell] for cell in involved}

    def penalty(cell, value):
        spec = world.cells[cell]
        return d0.penalty(spec.alpha, spec.beta, spec.chi, spec.L, spec.U,
                          spec.R, value)

    before = math.fsum(penalty(cell, z[cell]) for cell in involved)
    successor = dict(z)
    process_cost = 0.0
    for _, edge, quantity in active:
        successor[edge.i] -= dt * quantity
        successor[edge.j] += dt * edge.eta * quantity
        process_cost += (LAM_L * dt * (1.0 - edge.eta)) * quantity
    after = math.fsum(penalty(cell, successor[cell]) for cell in involved)
    group = before - after - process_cost
    independent = 0.0
    for edge_index, _edge, quantity in active:
        candidate = {"edge": edge_index, "quant_index": 0, "frac": 1.0,
                     "f": 0.0, "J": quantity, "q_req": quantity,
                     "q_e_max": quantity, "q_acc": quantity}
        independent += quote_schedule_for(
            world, x, u, dt, candidate, tick).exact(quantity)
    return {"group_quote": group, "naive_independent_sum": independent,
            "double_count": independent - group, "n_actions": len(active)}


def threshold_diagnostics(world: d0.World, x, dt: float) -> Optional[dict]:
    """Frozen DC1/DC3 threshold-region diagnostic; never used to select."""
    if len(world.cells) != 3 or len(world.edges) != 2 \
            or world.edges[0].M != 0.28 or world.edges[1].M != 0.08:
        return None
    label = ("conservative"
             if dt == _TIMESTEP_LOCKS["DC1_flux_lock"][5]
             else "near_certificate")
    thresholds = PLAN["instrument_sensitivity_certificate"] \
        ["DC1_flux_lock"]["registered_thresholds"]
    xbar_b = thresholds["xbar_B"]
    xbar_d = thresholds[f"xbar_D_{label}"]
    stock = x[2]
    return {
        "destination": 2, "stock": stock, "xbar_B": xbar_b,
        "xbar_D": xbar_d, "below_B": stock < xbar_b,
        "below_D": stock < xbar_d,
        "registered_divergence_region": xbar_d < stock < xbar_b,
    }


def f4_threshold(certified_lower_bound: float) -> float:
    """The sole registered F4 threshold; there is no other slack floor."""
    certified_lower_bound = float(certified_lower_bound)
    if not math.isfinite(certified_lower_bound):
        raise ValueError("certified lower bound must be finite")
    return certified_lower_bound - 1e-9 * (1 + abs(certified_lower_bound))


def positive_control_thresholds() -> dict:
    return {
        control: {label: f4_threshold(bound)
                  for label, bound in bounds.items()}
        for control, bounds in _PC_BOUNDS.items()
    }


def positive_control_result(control: str, dt_label: str,
                            executed_value: float) -> dict:
    """Apply PC1-PC4's frozen one-sided F4 rule to a future result value."""
    if control not in _PC_BOUNDS or dt_label not in DT_LABELS:
        raise ValueError("unregistered positive-control key")
    executed_value = float(executed_value)
    if not math.isfinite(executed_value):
        raise ValueError("positive-control value must be finite")
    bound = _PC_BOUNDS[control][dt_label]
    threshold = f4_threshold(bound)
    return {
        "control": control, "dt_label": dt_label,
        "measured_as": PLAN["positive_control"][control]["measured_as"],
        "certified_lower_bound": bound, "f4_threshold": threshold,
        "executed_value": executed_value,
        "f4_fired": executed_value < threshold,
    }


def per_destination_alignment_predicate(run_d: sv.RunResult,
                                        run_b: sv.RunResult) -> dict:
    """Registered channel iii using Gate 1D magnitudes and persistence."""
    if len(run_d.series["unmet_by_dest"]) != len(run_b.series["unmet_by_dest"]):
        raise ValueError("paired runs have different horizons")
    n = len(run_b.series["unmet_by_dest"][0])
    reserve = sv.service_alignment_predicate(run_d, run_b)
    destinations = []
    for destination in range(n):
        b_series = [row[destination] for row in run_b.series["unmet_by_dest"]]
        d_series = [row[destination] for row in run_d.series["unmet_by_dest"]]
        baseline = math.fsum(b_series[BURN_IN_TICKS:])
        actor = math.fsum(d_series[BURN_IN_TICKS:])
        excess = actor - baseline
        relative = (excess / baseline if baseline > 0.0
                    else (1.0 if excess > 0.0 else 0.0))
        persistent = all(
            d_value > b_value + sv.tol(b_value)
            for b_value, d_value in zip(b_series[-PERSISTENCE_WINDOW:],
                                        d_series[-PERSISTENCE_WINDOW:]))
        condition = (excess >= UNMET_ABS and relative >= UNMET_REL
                     and persistent)
        fired = bool(reserve["ebu_threshold_met"] and condition
                     and not reserve["preservation_justified"])
        destinations.append({
            "destination": destination, "pbi_unmet_baseline": baseline,
            "pbi_unmet_actor": actor, "unmet_excess_absolute": excess,
            "unmet_excess_relative": relative,
            "unmet_persistent": bool(persistent),
            "unmet_condition": bool(condition),
            "is_service_alignment_failure": fired,
        })
    return {"destinations": destinations,
            "any_destination_failure": any(
                row["is_service_alignment_failure"] for row in destinations)}


def discriminator_v2_channels(run_a: sv.RunResult, run_b: sv.RunResult,
                              run_d: sv.RunResult) -> dict:
    service_a = math.fsum(run_a.series["service"][BURN_IN_TICKS:])
    service_b = math.fsum(run_b.series["service"][BURN_IN_TICKS:])
    service_d = math.fsum(run_d.series["service"][BURN_IN_TICKS:])
    capability = abs(service_a - service_b)
    ratio_delta = abs(service_d / service_b - 1.0) if service_b > 0.0 else 0.0
    n = len(run_b.series["unmet_by_dest"][0])
    destination_deltas = []
    for destination in range(n):
        unmet_b = math.fsum(row[destination]
                            for row in run_b.series["unmet_by_dest"][BURN_IN_TICKS:])
        unmet_d = math.fsum(row[destination]
                            for row in run_d.series["unmet_by_dest"][BURN_IN_TICKS:])
        destination_deltas.append(abs(unmet_d - unmet_b))
    per_destination = max(destination_deltas, default=0.0)
    channels = (capability, ratio_delta, per_destination)
    return {
        "i_capability_cost_absolute": capability,
        "ii_service_ratio_delta": ratio_delta,
        "iii_max_destination_unmet_delta": per_destination,
        "world_discriminating": any(
            value > NUM_TOL_REL * (1.0 + abs(value)) for value in channels),
    }


# ---------------------------------------------------------------------------
# Future execution layer.  The authorized pre-execution suite never calls it.
# ---------------------------------------------------------------------------
def gate1dc_tick(world: d0.World, x, dt: float,
                 configs: Mapping[int, p1c.SourceConfig],
                 current_demand_rate: Sequence[float], arm: str,
                 tick: int) -> dict:
    if arm not in EXEC_ARMS:
        raise ValueError(f"arm {arm!r} is not executable")
    u = sv.drive_no_demand(world, x)
    menus = {}
    candidate_quotes = {}
    selected = None
    rested = False
    if arm == EXEC_ARMS[0]:
        active_world = world
    else:
        chosen = []
        for source_id in sorted(configs):
            state, budget, candidates = candidate_menu(
                world, x, u, source_id, configs[source_id], dt)
            menus[source_id] = {
                "state": state, "budget": budget,
                "menu_contract_hash": MENU_CONTRACT_HASH,
                "candidates": candidates,
            }
            if not candidates:
                rested = True
                continue
            if arm in (EXEC_ARMS[1], EXEC_ARMS[2]):
                pick = select_arm_B(candidates)
                exact = [quote_schedule_for(world, x, u, dt, candidate,
                                             tick).exact(candidate["q_acc"])
                         for candidate in candidates]
            elif arm == EXEC_ARMS[3]:
                exact = [quote_schedule_for(world, x, u, dt, candidate,
                                             tick).exact(candidate["q_acc"])
                         for candidate in candidates]
                selected_index = select_arm_D(candidates, exact)
                pick = (candidates[selected_index]
                        if selected_index is not None else None)
            else:
                pick = select_arm_S(candidates, current_demand_rate, world)
                exact = [quote_schedule_for(world, x, u, dt, candidate,
                                             tick).exact(candidate["q_acc"])
                         for candidate in candidates]
            candidate_quotes[source_id] = exact
            if pick is None:
                rested = True
            else:
                chosen.append(pick)
        selected = chosen[0] if chosen else None
        active_world = shaped_active_world(world, selected)

    outcome = sv.bounded_step(world, x, dt, configs, current_demand_rate,
                              active_world=active_world)
    if arm != EXEC_ARMS[0] and selected is not None:
        if len(outcome.q_acc) != 1 or outcome.q_acc[0] != selected["q_acc"]:
            raise AssertionError("request-shaping identity violated")

    ebu = ebu_positive = ebu_negative = 0.0
    quoted = 0
    if arm in (EXEC_ARMS[2], EXEC_ARMS[3]) and selected is not None \
            and outcome.q_acc[0] > 0.0:
        registry = eq.EpochRegistry()
        schedule = quote_schedule_for(world, x, u, dt, selected, tick)
        registry.register(schedule)
        settlement = registry.settle(schedule, outcome.q_acc[0], tick, 0)
        if settlement.status == "settled":
            ebu = settlement.issued
            ebu_positive = max(0.0, ebu)
            ebu_negative = max(0.0, -ebu)
            quoted = 1

    if arm == EXEC_ARMS[0]:
        executed_by_edge = list(outcome.q_acc)
    else:
        executed_by_edge = [0.0] * len(world.edges)
        if selected is not None:
            executed_by_edge[selected["edge"]] = outcome.q_acc[0]
    delivered_by_edge = [edge.eta * quantity
                         for edge, quantity in zip(world.edges,
                                                   executed_by_edge)]
    source_results = {result.source_id: result for result in outcome.source_results}
    sigma = {source: result.sigma for source, result in source_results.items()}
    utilization = {
        source: (result.Q_acc / result.Q_max if result.Q_max > 0.0 else 0.0)
        for source, result in source_results.items()
    }
    reserve_crossings = sum(
        sv.reserve_crossing(outcome.x_before[source], outcome.x_after[source],
                            config.R_eff)
        for source, config in configs.items() if config.R_eff is not None)
    overuse = math.fsum(max(0.0, result.Q_acc - result.Q_max)
                        for result in outcome.source_results)
    source_ids = [source for source, config in configs.items()
                  if config.R_eff is not None]
    if menus:
        active_out_edges = sorted({candidate["edge"]
                                   for menu in menus.values()
                                   for candidate in menu["candidates"]})
    else:
        active_out_edges = [index for index, quantity in enumerate(outcome.q_req)
                            if quantity > 0.0]
    all_quotes = [quote for values in candidate_quotes.values()
                  for quote in values]
    quote_sign_counts = {
        "positive": sum(quote > 0.0 for quote in all_quotes),
        "zero": sum(quote == 0.0 for quote in all_quotes),
        "negative": sum(quote < 0.0 for quote in all_quotes),
    }
    p1c_rejections = sum(requested > 0.0 and accepted <= 0.0
                         for requested, accepted in zip(outcome.q_req,
                                                        outcome.q_acc))
    recomputation_residuals = {
        "max_service_above_available": max(
            (service - available for service, available
             in zip(outcome.service, outcome.available)), default=0.0),
        "max_service_above_demand": max(
            (service - demand for service, demand
             in zip(outcome.service, outcome.demand_amount)), default=0.0),
        "max_unmet_identity": max(
            (abs(unmet - (demand - service))
             for unmet, demand, service in zip(
                 outcome.unmet, outcome.demand_amount, outcome.service)),
            default=0.0),
        "max_delivery_identity": max(
            (abs(delivery - world.edges[index].eta * executed_by_edge[index])
             for index, delivery in enumerate(delivered_by_edge)), default=0.0),
    }
    return {
        "tick": tick, "arm": arm, "dt": dt,
        "x_before": list(outcome.x_before), "x_after": list(outcome.x_after),
        "u": list(u), "available": list(outcome.available),
        "active_out_edges": active_out_edges,
        "menus": {source: {**menu, "candidates": [dict(candidate)
                                                   for candidate in menu["candidates"]]}
                  for source, menu in menus.items()},
        "candidate_exact_quotes": {source: list(values)
                                   for source, values in candidate_quotes.items()},
        "candidate_per_unit_quotes": {
            source: [quote / candidate["q_acc"]
                     for quote, candidate in zip(
                         candidate_quotes[source], menu["candidates"])]
            for source, menu in menus.items()},
        "candidate_continuous_vertices": {
            source: [continuous_vertex_diagnostic(world, x, u, dt, candidate)
                     for candidate in menu["candidates"]]
            for source, menu in menus.items()},
        "selected": dict(selected) if selected is not None else None,
        "threshold_diagnostics": threshold_diagnostics(world, x, dt),
        "rested": bool(rested and selected is None),
        "request_shaping_identity": bool(
            arm == EXEC_ARMS[0] or selected is None
            or executed_by_edge[selected["edge"]] == selected["q_acc"]),
        "executed_q_acc": executed_by_edge,
        "delivered": delivered_by_edge,
        "sigma": sigma, "budget_utilization": utilization,
        "service": list(outcome.service), "unmet": list(outcome.unmet),
        "demand_amount": list(outcome.demand_amount),
        "pulse_tick": bool(len(world.cells) == 3
                           and current_demand_rate[2] > 1.0),
        "transport_loss": outcome.transport_loss,
        "negative_corrections": list(outcome.negative_corrections),
        "ledger_residual": outcome.ledger_residual,
        "domain_failure": bool(outcome.domain_failure),
        "reserve_crossings": reserve_crossings,
        "allee_crossings": 0, "dead_sources": 0,
        "physical_overuse": overuse, "p1c_rejections": p1c_rejections,
        "min_source": min(outcome.x_after[source] for source in source_ids),
        "burden": d0.V_total(world, outcome.x_after),
        "viability": 100.0 * sum(
            outcome.x_after[index] >= world.cells[index].L
            for index in range(world.n)) / world.n,
        "ebu": ebu, "ebu_pos": ebu_positive, "ebu_neg": ebu_negative,
        "quoted": quoted, "quote_sign_counts": quote_sign_counts,
        "recomputation_residuals": recomputation_residuals,
        "group_diagnostic": (group_quote_diagnostic(
            world, x, u, dt, outcome.q_acc, tick)
            if arm == EXEC_ARMS[0] else None),
    }


def run_arm(world_name: str, arm: str, dt_label: str,
            ticks: Optional[int] = None) -> sv.RunResult:
    """Future runner primitive.  Never called by pre-execution validation."""
    world, x0, configs, _demand, meta = build_world(world_name)
    dt = world_dts(world_name)[dt_label]
    horizon = RUN_TICKS if ticks is None else int(ticks)
    if not 1 <= horizon <= RUN_TICKS:
        raise ValueError("horizon outside registered range")
    state = tuple(x0)
    series = {
        "service": [], "unmet": [], "demand": [], "burden": [],
        "viability": [], "ebu": [], "actions": [], "q_acc": [],
        "loss": [], "min_source": [], "opportunities": [], "proposed": [],
        "rests": [], "p1c_rejected": [], "quoted": [], "corrections": [],
        "ledger": [], "selected_edge": [], "service_by_dest": [],
        "unmet_by_dest": [], "demand_by_dest": [], "pulse_tick": [],
        "tick_records": [],
    }
    totals = {
        "service": 0.0, "unmet": 0.0, "demand": 0.0, "ebu": 0.0,
        "ebu_pos": 0.0, "ebu_neg": 0.0, "actions": 0,
        "opportunities": 0, "proposed": 0, "accepted": 0, "quoted": 0,
        "rests": 0, "p1c_rejected": 0, "loss": 0.0, "overuse": 0.0,
        "reserve_crossings": 0, "allee_crossings": 0, "corrections": 0.0,
        "max_ledger_residual": 0.0, "quote_pos": 0, "quote_zero": 0,
        "quote_neg": 0,
    }
    domain_failure_tick = None
    for tick in range(1, horizon + 1):
        current_demand = demand_rate_for_tick(world_name, dt_label, tick)
        record = gate1dc_tick(world, state, dt, configs, current_demand,
                             arm, tick)
        action_count = sum(quantity > 0.0
                           for quantity in record["executed_q_acc"])
        opportunities = (sum(len(menu["candidates"])
                             for menu in record["menus"].values())
                         if record["menus"] else len(world.edges))
        proposed = int(record["selected"] is not None)
        rejected = record["p1c_rejections"]
        for values in record["candidate_exact_quotes"].values():
            for quote in values:
                totals["quote_pos" if quote > 0.0 else
                       "quote_neg" if quote < 0.0 else "quote_zero"] += 1
        service = math.fsum(record["service"])
        unmet = math.fsum(record["unmet"])
        demand = math.fsum(record["demand_amount"])
        values = {
            "service": service, "unmet": unmet, "demand": demand,
            "burden": record["burden"], "viability": record["viability"],
            "ebu": record["ebu"], "actions": action_count,
            "q_acc": math.fsum(record["executed_q_acc"]),
            "loss": record["transport_loss"],
            "min_source": record["min_source"],
            "opportunities": opportunities, "proposed": proposed,
            "rests": int(record["rested"]), "p1c_rejected": rejected,
            "quoted": record["quoted"],
            "corrections": math.fsum(record["negative_corrections"]),
            "ledger": record["ledger_residual"],
        }
        for key, value in values.items():
            series[key].append(value)
        series["selected_edge"].append(
            record["selected"]["edge"] if record["selected"] else None)
        series["service_by_dest"].append(list(record["service"]))
        series["unmet_by_dest"].append(list(record["unmet"]))
        series["demand_by_dest"].append(list(record["demand_amount"]))
        series["pulse_tick"].append(record["pulse_tick"])
        series["tick_records"].append(record)
        for key in ("service", "unmet", "demand", "ebu", "actions",
                    "opportunities", "proposed", "quoted", "rests",
                    "p1c_rejected", "loss", "corrections"):
            totals[key] += values[key]
        totals["accepted"] += action_count
        totals["ebu_pos"] += record["ebu_pos"]
        totals["ebu_neg"] += record["ebu_neg"]
        totals["overuse"] += record["physical_overuse"] * dt
        totals["reserve_crossings"] += record["reserve_crossings"]
        totals["allee_crossings"] += record["allee_crossings"]
        totals["max_ledger_residual"] = max(
            totals["max_ledger_residual"], abs(record["ledger_residual"]))
        if record["domain_failure"] and domain_failure_tick is None:
            domain_failure_tick = tick
        state = tuple(record["x_after"])
    source_ids = sorted(configs)
    final = {
        "x": list(state), "burden": series["burden"][-1],
        "viability": series["viability"][-1],
        "min_source": series["min_source"][-1], "dead_sources": 0,
        "domain_failure_tick": domain_failure_tick,
        "negative_state": any(value < -sv.DOMAIN_TOL for value in state),
        "source_stock": math.fsum(state[index] for index in source_ids),
        "destination_stock": math.fsum(
            state[index] for index in range(world.n) if index not in source_ids),
        "feasible_world": meta["feasible"], "note": meta["note"],
    }
    certificate = world_certificates(world_name)
    return sv.RunResult(
        run_id=run_id(world_name, arm, dt_label), world=world_name, arm=arm,
        dt_label=dt_label, dt=dt,
        dt_certificate=certificate["binding_certificate"],
        certificate_kind=certificate["binding_kind"],
        r_dt=dt / certificate["binding_certificate"], series=series,
        totals=totals, final=final, x_trajectory_tail=state)


def run_id(world: str, arm: str, dt_label: str) -> str:
    return f"{world}|{arm}|{dt_label}"


def build_run_specs() -> list:
    specs = [
        {"world": world, "dt_label": dt_label, "arm": arm,
         "run_id": run_id(world, arm, dt_label)}
        for world in WORLD_NAMES for dt_label in DT_LABELS for arm in EXEC_ARMS
    ]
    if len(specs) != 30 or len({spec["run_id"] for spec in specs}) != 30:
        raise SystemExit("FATAL: frozen 30-run inventory mismatch")
    return specs


METRIC_FIELDS = {
    PLAN["metrics_per_run"][0]: ("x_before", "x_after"),
    PLAN["metrics_per_run"][1]: ("active_out_edges",),
    PLAN["metrics_per_run"][2]: ("menus",),
    PLAN["metrics_per_run"][3]: ("candidate_exact_quotes",),
    PLAN["metrics_per_run"][4]: ("candidate_per_unit_quotes",),
    PLAN["metrics_per_run"][5]: ("candidate_continuous_vertices",),
    PLAN["metrics_per_run"][6]: ("selected", "executed_q_acc",
                                 "request_shaping_identity"),
    PLAN["metrics_per_run"][7]: ("executed_q_acc", "delivered"),
    PLAN["metrics_per_run"][8]: ("budget_utilization", "sigma"),
    PLAN["metrics_per_run"][9]: ("service", "unmet"),
    PLAN["metrics_per_run"][10]: ("demand_amount",),
    PLAN["metrics_per_run"][11]: ("pulse_tick", "service", "unmet"),
    PLAN["metrics_per_run"][12]: ("selected", "threshold_diagnostics"),
    PLAN["metrics_per_run"][13]: ("service", "unmet"),
    PLAN["metrics_per_run"][14]: ("burden", "viability"),
    PLAN["metrics_per_run"][15]: ("reserve_crossings", "allee_crossings"),
    PLAN["metrics_per_run"][16]: ("dead_sources", "physical_overuse",
                                  "transport_loss"),
    PLAN["metrics_per_run"][17]: ("executed_q_acc", "rested",
                                  "p1c_rejections"),
    PLAN["metrics_per_run"][18]: ("candidate_exact_quotes",
                                  "quote_sign_counts", "quoted"),
    PLAN["metrics_per_run"][19]: ("group_diagnostic",),
    PLAN["metrics_per_run"][20]: ("domain_failure", "negative_corrections"),
    PLAN["metrics_per_run"][21]: ("dt",),
    PLAN["metrics_per_run"][22]: ("ledger_residual",
                                  "recomputation_residuals"),
    PLAN["metrics_per_run"][23]: ("ebu", "ebu_pos", "ebu_neg"),
}
TICK_RECORD_FIELDS = tuple(dict.fromkeys(
    ("tick", "arm", "dt", "u", "available", "min_source")
    + tuple(field for fields in METRIC_FIELDS.values() for field in fields)))


def validate_output_contract() -> None:
    if list(METRIC_FIELDS) != PLAN["metrics_per_run"]:
        raise ValueError("output schema does not cover metrics in frozen order")
    if len(METRIC_FIELDS) != 24 or any(not fields for fields in METRIC_FIELDS.values()):
        raise ValueError("output schema metric mapping incomplete")
    if len(build_run_specs()) * RUN_TICKS != 6000:
        raise ValueError("output schema trace row count mismatch")
    if FUTURE_ARTIFACTS[1:] != (
            MANIFEST_PATH, SUMMARY_PATH, TRACE_PATH, STDOUT_PATH):
        raise ValueError("output filenames mismatch")
    if REGISTERED_ARTIFACTS != (
            RECEIPT_PATH, EXECUTION_STARTED_PATH, TRACE_PATH, STDOUT_PATH,
            SUMMARY_PATH, MANIFEST_PATH):
        raise ValueError("registered artifact publication order mismatch")
    if len(TEMPORARY_BASENAMES) != 6 or len(set(TEMPORARY_BASENAMES)) != 6:
        raise ValueError("temporary artifact names mismatch")
    if len(ORIGINAL_SOURCE_HASH_ORDER) != 13 \
            or len(set(ORIGINAL_SOURCE_HASH_ORDER)) != 13:
        raise ValueError("original execution source hash inventory mismatch")
    if len(ENVIRONMENT_SOURCE_HASH_ORDER) != 15 \
            or len(set(ENVIRONMENT_SOURCE_HASH_ORDER)) != 15:
        raise ValueError("environment-amended source hash inventory mismatch")
    if len(SOURCE_HASH_ORDER) != 17 or len(set(SOURCE_HASH_ORDER)) != 17:
        raise ValueError("launcher-amended source hash inventory mismatch")
    if len(SUMMARY_REQUIRED_BLOCKS) != 24:
        raise ValueError("runner summary top-level schema mismatch")


def strict_json_dumps(obj, **kwargs) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, **kwargs)


validate_output_contract()


if __name__ == "__main__":
    raise SystemExit(
        "gate1dc_v30 is a library. Run test_v30_gate1dc.py for static "
        "pre-execution validation. The Gate 1D-C study is not authorized here.")
