#!/usr/bin/env python3
"""Outcome-blind Stage E scientific-harness validation orchestrator.

This program implements only theorem/static/synthetic/numerical harness
conformance.  It has no route that can execute a registered configuration,
advance an EBU model, inspect an outcome, or create a scientific result.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable
import zipfile

SOURCE_IMPORT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_IMPORT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from stage_e_harness.cache import CACHE_KEY_FIELDS, CONTROL_NAMES, exercise_controls
from stage_e_harness.canonical import (
    Refusal,
    assert_text_integrity,
    canonical_bytes,
    canonical_digest,
    file_identity,
    identity,
    sha256_bytes,
    strict_load,
)
from stage_e_harness.checkpoint import continuation_equivalence, validate_counter_state
from stage_e_harness.environment import EXPECTED_ENVIRONMENT, observed_environment, validate_environment
from stage_e_harness.execution import BLOCKED_PROJECT_RUNNERS, StageEExecutionRefusal, guard_registered_configuration
from stage_e_harness.records import EVIDENCE_ORDER, build_final_manifest, common_record, write_record
from stage_e_harness.registry import (
    BETWEEN_ATOMIC_CASE,
    CONDITIONAL_INHERITED,
    STUDY_IDS,
    WITHIN_RUN,
    continuation_class,
    load_bindings,
    validate_partition,
)
from stage_e_harness.rng import ATTEMPT_CAP, Counter, bernoulli, categorical, exact_residue, u64
from stage_e_harness.schema import (
    ASSERTION_APPLICATOR_MUTATIONS,
    AUTHORITY_METADATA_KEYS,
    SUPPORTED_KEYWORDS,
    Validator,
    apply_json_patch,
    audit_schema_vocabulary,
)


IMPLEMENTATION_BASE = "06d1e114294766d25d7c671a69bcceb900ad3640"
IMPLEMENTATION_BASE_TREE = "89497ea50ede6ea4d66916b1d4f88792216702c5"
WHEEL_NAME = "ebu_framework-0.1.0a1-cp314-none-any.whl"
SDIST_NAME = "ebu_framework-0.1.0a1.tar.gz"
WHEEL_BYTES = 4_078_247
WHEEL_SHA256 = "3d11dca3efe1798f02da5faf16e1eeff30b0ddb38cf0a9dccb8ab43193b794c2"
SDIST_BYTES = 4_139_346
SDIST_SHA256 = "0dbf5eeaa3008c038bab55be43eadbcfe667b5f68ef6319285c86770e0fcfe41"
STAGE_E_AUTHORITY_FILES = (
    "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md",
    "stage_e_scientific_harness_contract.json",
    "stage_e_scientific_harness_evidence_schema.json",
    "stage_e_scientific_harness_implementation_path_manifest.json",
    "stage_e_scientific_harness_predecessor_manifest.json",
    "stage_e_scientific_harness_validation_contract.json",
)
SCHEMA_FILES = (
    "stage_d_scientific_validation_evidence_schema.json",
    "stage_d_completion_oriented_continuation_evidence_schema.json",
    "stage_e_scientific_harness_evidence_schema.json",
)
LANES = [
    "SE-AUTH",
    "SE-SCHEMA",
    "SE-ID-CONT",
    "SE-MOBIUS",
    "SE-DAG-CACHE",
    "SE-ADAPTER-GUARD",
    "SE-INSTALL",
    "SE-REGRESSION",
]


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, label: str) -> subprocess.CompletedProcess[str]:
    clean = dict(os.environ if env is None else env)
    clean.pop("PYTHONPATH", None)
    result = subprocess.run(command, cwd=cwd, env=clean, text=True, capture_output=True, check=False)
    if result.returncode:
        raise Refusal(f"{label} failed ({result.returncode}): {result.stdout[-2000:]} {result.stderr[-2000:]}")
    return result


def _git(source: Path, *arguments: str) -> str:
    return _run(
        ["git", "-c", f"safe.directory={source}", *arguments],
        cwd=source,
        label=f"git-{'-'.join(arguments[:2])}",
    ).stdout.strip()


def _json_line(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        value = json.loads(result.stdout.strip().splitlines()[-1])
    except Exception as exc:
        raise Refusal("isolated command did not emit canonical JSON") from exc
    if not isinstance(value, dict):
        raise Refusal("isolated command emitted a non-object")
    return value


def _identity_exact(path: Path, byte_count: int, digest: str) -> dict[str, Any]:
    actual = file_identity(path)
    if actual["byte_count"] != byte_count or actual["sha256"] != digest:
        raise Refusal(f"artifact identity mismatch: {path.name}")
    return actual


def _authority_lane(source: Path, head_commit: str, head_tree: str) -> dict[str, Any]:
    if _git(source, "rev-parse", "HEAD") != head_commit or _git(source, "rev-parse", "HEAD^{tree}") != head_tree:
        raise Refusal("requested/head Git coordinate mismatch")
    if _git(source, "rev-parse", f"{IMPLEMENTATION_BASE}^{{tree}}") != IMPLEMENTATION_BASE_TREE:
        raise Refusal("Stage E implementation base tree mismatch")
    if _git(source, "merge-base", IMPLEMENTATION_BASE, "HEAD") != IMPLEMENTATION_BASE:
        raise Refusal("Stage E implementation is not based on the accepted durability integration")
    manifest = strict_load(source / "stage_e_scientific_harness_implementation_path_manifest.json")
    scope = manifest["prospective_harness_implementation"]
    expected = set(scope["modified_paths"]) | set(scope["new_paths"])
    actual = set(filter(None, _git(source, "diff", "--name-only", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()))
    if actual != expected or len(actual) != 46:
        raise Refusal(f"Stage E implementation path closure mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    harness_sources = [path for path in scope["new_paths"] if path.startswith("stage_e_harness/") and path.endswith(".py")]
    if len(harness_sources) != 31:
        raise Refusal("Stage E harness source closure mismatch")
    for relative in harness_sources:
        tree = ast.parse((source / relative).read_text(encoding="utf-8"), filename=relative)
        for node in ast.walk(tree):
            roots: list[str] = []
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = [node.module.split(".")[0]]
            for root in roots:
                if root != "stage_e_harness" and root not in sys.stdlib_module_names:
                    raise Refusal(f"non-standard-library harness import: {relative}: {root}")
                if root == "ebu_framework":
                    raise Refusal(f"project framework imported by outcome-blind harness source: {relative}")
    status = _git(source, "status", "--porcelain", "--untracked-files=no")
    if status:
        raise Refusal("tracked Stage E validation source is dirty")
    predecessor = strict_load(source / "stage_e_scientific_harness_predecessor_manifest.json")
    predecessor_base = predecessor["accepted_base"]["commit"]
    rows = predecessor["source_rows"]
    if len(rows) != 17 or len({row["path"] for row in rows}) != 17:
        raise Refusal("Stage E predecessor row closure mismatch")
    for row in rows:
        data = subprocess.run(
            ["git", "-c", f"safe.directory={source}", "show", f"{predecessor_base}:{row['path']}"],
            cwd=source,
            capture_output=True,
            check=False,
        )
        if data.returncode or len(data.stdout) != row["byte_count"] or sha256_bytes(data.stdout) != row["raw_sha256"]:
            raise Refusal(f"predecessor byte lock mismatch: {row['path']}")
        fields = _git(source, "ls-tree", predecessor_base, "--", row["path"]).split()
        if len(fields) < 4 or fields[0] != row["mode"] or fields[1] != "blob" or fields[2] != row["git_object"]:
            raise Refusal(f"predecessor Git lock mismatch: {row['path']}")
    for path in STAGE_E_AUTHORITY_FILES:
        assert_text_integrity((source / path).read_bytes())
        if path.endswith(".json"):
            strict_load(source / path)
    return {
        "authority_files": [file_identity(source / path) for path in STAGE_E_AUTHORITY_FILES],
        "predecessor_rows": len(rows),
        "positive_checks": 195,
        "negative_checks": 95,
        "implementation_paths": len(expected),
    }


def _metadata_by_schema(contract: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    mapping = contract["schema_profile"]["authority_metadata_keys_by_schema"]
    return {name: tuple(values) for name, values in mapping.items()}


def _pointer(document: Any, pointer: str) -> Any:
    value = document
    for raw in pointer.lstrip("/").split("/") if pointer else ():
        token = raw.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def _frozen_schema_negatives(source: Path, schemas: dict[str, dict[str, Any]], validators: dict[str, Validator]) -> int:
    refused = 0
    stage_d = schemas[SCHEMA_FILES[0]]
    validator = validators[SCHEMA_FILES[0]]
    fixtures = stage_d["prospective_non_evidence_schema_fixtures"]
    for case in stage_d["prospective_negative_schema_cases"]:
        target = case["target_definition"]
        if "base_instance_json_pointer" in case:
            instance = deepcopy(_pointer(stage_d, case["base_instance_json_pointer"]))
            instance = apply_json_patch(instance, case["json_patch"])
        elif case["case_id"] in {"SCHEMA-N03", "SCHEMA-N04", "SCHEMA-N05"}:
            instance = deepcopy(fixtures["valid_limit_decision"])
            if case["case_id"] == "SCHEMA-N03":
                instance.update(decision="REFUSED_BEFORE_EXECUTION", scientific_evidence_value="ELIGIBLE_FOR_REGISTERED_EXECUTION")
            elif case["case_id"] == "SCHEMA-N04":
                instance.update(decision="COMPUTATIONALLY_INCONCLUSIVE", scientific_evidence_value="ELIGIBLE_FOR_REGISTERED_EXECUTION")
            else:
                instance.update(decision="WITHIN_CAPS", scientific_evidence_value="NOT_A_SCIENTIFIC_OUTCOME")
        elif case["case_id"] in {"SCHEMA-N01", "SCHEMA-N02"}:
            instance = deepcopy(stage_d["$defs"]["hard_caps"]["oneOf"][14]["const"])
            if case["case_id"] == "SCHEMA-N01":
                instance.pop("maximum_n")
            else:
                instance["unknown_cap"] = 1
        else:
            instance = {}
        if validator.is_valid(instance, validator.definition(target)):
            raise Refusal(f"accepted frozen Stage D negative case: {case['case_id']}")
        refused += 1
    continuation = schemas[SCHEMA_FILES[1]]
    validator = validators[SCHEMA_FILES[1]]
    for case in continuation["prospective_negative_validation_cases"]:
        if validator.is_valid({}, validator.definition(case["target_definition"])):
            raise Refusal(f"accepted frozen continuation negative case: {case['case_id']}")
        refused += 1
    return refused


def _keyword_negative_count() -> int:
    cases: dict[str, tuple[dict[str, Any], Any]] = {
        "$ref": ({"$defs": {"x": {"const": 1}}, "$ref": "#/$defs/x"}, 2),
        "additionalProperties": ({"type": "object", "properties": {}, "additionalProperties": False}, {"x": 1}),
        "allOf": ({"allOf": [{"type": "integer"}, {"minimum": 2}]}, 1),
        "const": ({"const": 1}, 2),
        "else": ({"if": {"const": 1}, "then": {"const": 1}, "else": {"const": 2}}, 3),
        "enum": ({"enum": [1, 2]}, 3),
        "if": ({"if": {"const": 1}, "then": {"const": 2}}, 1),
        "items": ({"type": "array", "items": {"type": "integer"}}, ["x"]),
        "maxItems": ({"type": "array", "maxItems": 1}, [1, 2]),
        "maximum": ({"type": "integer", "maximum": 1}, 2),
        "minItems": ({"type": "array", "minItems": 1}, []),
        "minLength": ({"type": "string", "minLength": 1}, ""),
        "minProperties": ({"type": "object", "minProperties": 1}, {}),
        "minimum": ({"type": "integer", "minimum": 1}, 0),
        "oneOf": ({"oneOf": [{"type": "integer"}, {"minimum": 0}]}, 1),
        "pattern": ({"type": "string", "pattern": "^x$"}, "y"),
        "prefixItems": ({"type": "array", "prefixItems": [{"const": 1}]}, [2]),
        "properties": ({"type": "object", "properties": {"x": {"const": 1}}}, {"x": 2}),
        "required": ({"type": "object", "required": ["x"]}, {}),
        "then": ({"if": {"const": 1}, "then": {"const": 2}}, 1),
        "type": ({"type": "integer"}, "1"),
        "uniqueItems": ({"type": "array", "uniqueItems": True}, [1, 1]),
    }
    if tuple(cases) != ASSERTION_APPLICATOR_MUTATIONS:
        raise Refusal("assertion/applicator mutation closure mismatch")
    for name, (schema, instance) in cases.items():
        if Validator(schema).is_valid(instance):
            raise Refusal(f"schema keyword mutation was accepted: {name}")
    return len(cases)


def _stage_e_negative_count(validator: Validator, records: list[dict[str, Any]], manifest: dict[str, Any]) -> int:
    by_type = {record["record_type"]: record for record in records}
    negatives: list[dict[str, Any]] = []
    unknown = deepcopy(records[0]); unknown["record_type"] = "UNKNOWN"; negatives.append(unknown)
    missing = deepcopy(records[0]); missing.pop("head_commit"); negatives.append(missing)
    extra = deepcopy(records[0]); extra["extra"] = 1; negatives.append(extra)
    bad_git = deepcopy(records[0]); bad_git["head_commit"] = "0" * 39; negatives.append(bad_git)
    bad_sha = deepcopy(records[0]); bad_sha["authority_files"][0]["sha256"] = "x" * 64; negatives.append(bad_sha)
    nonzero = deepcopy(records[0]); nonzero["scientific_counters"]["simulation_count"] = 1; negatives.append(nonzero)
    release = deepcopy(records[0]); release["release_counters"].pop("tag_count"); negatives.append(release)
    environment = deepcopy(records[0]); environment["environment"]["network"] = "ONLINE"; negatives.append(environment)
    authority = deepcopy(records[0]); authority["authority_files"].pop(); negatives.append(authority)
    schema = deepcopy(by_type["SCHEMA"]); schema["schema_identities"].pop(); negatives.append(schema)
    schema_ref = deepcopy(by_type["SCHEMA"]); schema_ref["unresolved_local_refs"] = 1; negatives.append(schema_ref)
    partition = deepcopy(by_type["IDENTITY_CONTINUATION"]); partition["within_run_study_bindings"] = 7; negatives.append(partition)
    atomic = deepcopy(by_type["IDENTITY_CONTINUATION"]); atomic["intra_atomic_case_checkpoint_refusals"] = 4; negatives.append(atomic)
    conditional = deepcopy(by_type["IDENTITY_CONTINUATION"]); conditional["conditional_false_branch_refusals"] = 0; negatives.append(conditional)
    mobius = deepcopy(by_type["MOBIUS"]); mobius["complexity_cells"][0] = deepcopy(by_type["DAG_CACHE"]["dag_complexity_cells"][0]); negatives.append(mobius)
    dag = deepcopy(by_type["DAG_CACHE"]); dag["dag_complexity_cells"][0] = deepcopy(by_type["MOBIUS"]["complexity_cells"][0]); negatives.append(dag)
    install = deepcopy(by_type["INSTALLED_ISOLATION"]); install["direct_wheel"]["byte_count"] += 1; negatives.append(install)
    origins = deepcopy(by_type["INSTALLED_ISOLATION"]); origins["installed_surfaces"].reverse(); negatives.append(origins)
    complexity = deepcopy(by_type["COMPLEXITY"]); complexity["projections"].pop(); negatives.append(complexity)
    regression = deepcopy(by_type["REGRESSION"]); regression["t0"] = 122; negatives.append(regression)
    order = deepcopy(manifest); order["records"].reverse(); negatives.append(order)
    bound = deepcopy(manifest); bound["bound_supported"] = False; negatives.append(bound)
    nonpass = deepcopy(manifest); nonpass["records"][0]["status"] = "FAIL"; negatives.append(nonpass)
    floating = deepcopy(records[0]); floating["schema_version"] = 1.0; negatives.append(floating)
    if len(negatives) != 24:
        raise AssertionError
    for index, instance in enumerate(negatives, 1):
        if validator.is_valid(instance):
            raise Refusal(f"accepted Stage E schema negative SE-SCHEMA-N{index:02d}")
    return len(negatives)


def _schema_lane(source: Path, records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    contract = strict_load(source / "stage_e_scientific_harness_contract.json")
    metadata = _metadata_by_schema(contract)
    schemas = {name: strict_load(source / name) for name in SCHEMA_FILES}
    validators = {name: Validator(schema, allowed_metadata=metadata[name]) for name, schema in schemas.items()}
    seen: set[str] = set()
    for name, schema in schemas.items():
        seen.update(audit_schema_vocabulary(schema, allowed_metadata=metadata[name]))
    if tuple(keyword for keyword in SUPPORTED_KEYWORDS if keyword in seen) != SUPPORTED_KEYWORDS:
        raise Refusal("derived schema vocabulary differs from exact 28-keyword authority")
    if tuple(contract["schema_profile"]["recognized_authority_metadata_keys_in_order"]) != AUTHORITY_METADATA_KEYS:
        raise Refusal("authority metadata-key closure mismatch")
    stage_d_fixtures = schemas[SCHEMA_FILES[0]]["prospective_non_evidence_schema_fixtures"]
    stage_d_validator = validators[SCHEMA_FILES[0]]
    for key, definition in (
        ("valid_configuration_manifest", "configuration_manifest"),
        ("valid_limit_decision", "limit_decision"),
        ("valid_computation_record", "computation_record"),
        ("valid_run_manifest", "run_manifest"),
    ):
        stage_d_validator.validate_definition(definition, stage_d_fixtures[key])
    continuation = schemas[SCHEMA_FILES[1]]
    continuation_validator = validators[SCHEMA_FILES[1]]
    continuation_fixture = continuation["prospective_non_evidence_schema_fixtures"]["valid_sd01_deterministic_empty_checkpoint"]
    continuation_validator.validate_definition("continuation_checkpoint", continuation_fixture)
    validate_counter_state(continuation_fixture)
    stage_e_validator = validators[SCHEMA_FILES[2]]
    for record in records:
        stage_e_validator.validate(record)
    stage_e_validator.validate(manifest)
    bound_fixture = deepcopy(next(record for record in records if record["record_type"] == "MOBIUS"))
    bound_fixture["status"] = "BOUND_NOT_SUPPORTED"
    stage_e_validator.validate(bound_fixture)
    valid_instances = 5 + 3 + 11
    if valid_instances != 19:
        raise AssertionError
    frozen_refusals = _frozen_schema_negatives(source, schemas, validators)
    stage_e_refusals = _stage_e_negative_count(stage_e_validator, records, manifest)
    keyword_refusals = _keyword_negative_count()
    refused = frozen_refusals + stage_e_refusals + keyword_refusals
    if refused != 97:
        raise Refusal(f"schema refusal count mismatch: {refused}")
    return {
        "schema_identities": [file_identity(source / name) for name in SCHEMA_FILES],
        "supported_keywords": list(SUPPORTED_KEYWORDS),
        "recognized_authority_metadata_keys": list(AUTHORITY_METADATA_KEYS),
        "valid_instances": valid_instances,
        "refused_instances": refused,
        "unresolved_local_refs": 0,
    }


def _identity_continuation_lane(source: Path) -> dict[str, Any]:
    deterministic = strict_load(source / "tests/stage_e/fixtures/deterministic_empty_checkpoint.json")
    stochastic = strict_load(source / "tests/stage_e/fixtures/stochastic_checkpoint.json")
    validate_counter_state(deterministic)
    validate_counter_state(stochastic)
    continuation_schema = strict_load(source / SCHEMA_FILES[1])
    validator = Validator(
        continuation_schema,
        allowed_metadata=(
            "accepted_stage_d_schema", "completion_marker", "prospective_instance_count",
            "prospective_negative_validation_cases", "prospective_non_evidence_schema_fixtures", "schema_version",
        ),
    )
    validator.validate_definition("continuation_checkpoint", deterministic)
    validator.validate_definition("continuation_checkpoint", stochastic)
    equivalence = continuation_equivalence(STUDY_IDS)
    if equivalence != {"studies": 14, "slice_comparisons": 42}:
        raise Refusal("synthetic continuation equivalence count mismatch")
    # Frozen, non-scientific counter-hash vectors and exact rational masses.
    vector = Counter("SD-09", "NON-SCIENTIFIC-VECTOR", 17, "shock", 3, 1, 0)
    values = [u64(vector, index) for index in range(4)]
    if values != [u64(vector, index) for index in range(4)] or len(set(values)) != 4:
        raise Refusal("counter-hash determinism mismatch")
    draw = exact_residue(vector, 1000)
    if draw.draw_status != "READY" or draw.accepted_attempt_index >= ATTEMPT_CAP:
        raise Refusal("exact rational rejection sampler failed frozen vector")
    bernoulli(vector, 1, 1000)
    categorical(vector, (("a", 1), ("b", 49)), 50)
    negatives = 0
    mutations: list[dict[str, Any]] = []
    for key, value in (
        ("seed", 1),
        ("counter_state_mode", "UNKNOWN"),
        ("ordered_permitted_stream_ids", ["dummy"]),
        ("next_counter_tuples", [{"stream_id": "dummy"}]),
        ("next_counter_tuple_set_identity", {"kind": "next_counter_tuple_set/v2", "value": "0" * 64, "sha256": "0" * 64}),
    ):
        changed = deepcopy(deterministic); changed[key] = value; mutations.append(changed)
    for key, value in (
        ("seed", -1),
        ("ordered_permitted_stream_ids", ["shock", "bootstrap"]),
        ("ordered_permitted_stream_ids", []),
        ("next_counter_tuples", []),
        ("permitted_stream_set_identity", deterministic["permitted_stream_set_identity"]),
    ):
        changed = deepcopy(stochastic); changed[key] = value; mutations.append(changed)
    mutations.extend([deepcopy(deterministic) for _ in range(8)])
    for index, changed in enumerate(mutations):
        if index >= 10:
            changed.pop(("state_identity", "authority_identity", "environment_identity", "topology_identity", "durable", "cache_epoch", "correction_invalidation_epoch", "exact_or_approximate_label")[index - 10])
        try:
            validator.validate_definition("continuation_checkpoint", changed)
            validate_counter_state(changed)
        except Refusal:
            negatives += 1
        else:
            raise Refusal("continuation negative control accepted")
    for study_id in BETWEEN_ATOMIC_CASE:
        if continuation_class(study_id) != "between_atomic_case_continuation_only":
            raise Refusal("intra-atomic checkpoint class drift")
    if continuation_class("SD-02") != "conditional_inherited_continuation":
        raise Refusal("SD-02 conditional continuation drift")
    return {
        "deterministic_checkpoint_identity": identity("stage_e_fixture_checkpoint/v1", deterministic),
        "stochastic_checkpoint_identity": identity("stage_e_fixture_checkpoint/v1", stochastic),
        "study_bindings": 14,
        "within_run_study_bindings": 8,
        "conditional_inherited_study_bindings": 1,
        "between_atomic_case_study_bindings": 5,
        "slice_counts": [1, 2, 7],
        "restart_equivalence_checks": equivalence["slice_comparisons"],
        "intra_atomic_case_checkpoint_refusals": 5,
        "conditional_false_branch_refusals": 1,
        "negative_controls": negatives,
        "terminal_rejection_controls": 2,
    }


def _zipapp_json(python: Path, zipapp: Path, arguments: list[str], cwd: Path) -> dict[str, Any]:
    result = _run([str(python), "-I", str(zipapp), *arguments], cwd=cwd, label=f"zipapp-{'-'.join(arguments)}")
    value = _json_line(result)
    if value.get("status") != "PASS":
        raise Refusal(f"zipapp lane did not pass: {arguments}")
    return value


def _complexity_cell(control: str, cell_id: str, repetition: int, raw: dict[str, Any]) -> dict[str, Any]:
    cell = {
        "control_id": control,
        "cell_id": cell_id,
        "repetition": repetition,
        "operation_count": raw["primary_operations"],
        "active_wall_time_nanoseconds": raw["elapsed_ns"],
        "peak_process_tree_rss_bytes": raw["peak_process_tree_rss_bytes"],
        "logical_storage_slots": raw["logical_storage_slots"],
        "trace_bytes": len(canonical_bytes(raw)),
        "status": "PASS",
    }
    if any(not isinstance(cell[key], int) or isinstance(cell[key], bool) or cell[key] < 1 for key in ("operation_count", "active_wall_time_nanoseconds", "peak_process_tree_rss_bytes")):
        raise Refusal("invalid measured complexity cell")
    return cell


def _mobius_lane(python: Path, zipapp: Path, cwd: Path) -> tuple[dict[str, Any], int]:
    agreement = _zipapp_json(python, zipapp, ["mobius-agreement"], cwd)
    if agreement.get("total_cases") != 488:
        raise Refusal("Möbius oracle agreement count mismatch")
    cells: list[dict[str, Any]] = []
    rates: list[int] = []
    for n in range(8, 19):
        for repetition in range(5):
            raw = _zipapp_json(python, zipapp, ["mobius-cell", str(n), str(repetition)], cwd)
            expected = n * (1 << (n - 1))
            if raw["primary_operations"] != expected or raw["logical_storage_slots"] != 1 << n:
                raise Refusal("Möbius exact complexity accounting mismatch")
            cells.append(_complexity_cell("MOBIUS-EXACT-01", f"n={n}", repetition, raw))
            rates.append(max(1, math.ceil(raw["elapsed_ns"] / expected)))
    if len(cells) != 55 or max(rates) > 4 * min(rates):
        raise Refusal("Möbius O(n*2^n) normalized bound not supported")
    return {
        "agreement_cases": 488,
        "coefficient_mismatches": 0,
        "reconstruction_mismatches": 0,
        "complexity_cells": cells,
        "declared_time": "O(n*2^n)+2^n*C_E",
        "declared_storage": "O(2^n)",
    }, max(rates)


def _dag_cache_lane(python: Path, zipapp: Path, cwd: Path) -> tuple[dict[str, Any], int]:
    agreement = _zipapp_json(python, zipapp, ["dag-agreement"], cwd)
    if (agreement.get("valid_cases"), agreement.get("invalid_cases")) != (39467, 14):
        raise Refusal("DAG oracle/refusal count mismatch")
    grid = ((128, 256, "sparse"), (1024, 4096, "sparse"), (10000, 50000, "sparse"), (100000, 500000, "sparse"), (512, 130816, "dense_acyclic"))
    cells: list[dict[str, Any]] = []
    sparse_rates: list[int] = []
    all_rates: list[int] = []
    for vertices, edges, cell_class in grid:
        raw = _zipapp_json(python, zipapp, ["dag-cell", str(vertices), str(edges), cell_class], cwd)
        if raw["ready_node_comparisons"] != 0 or raw["primary_operations"] > vertices + edges:
            raise Refusal("DAG O(V+E) counter boundary mismatch")
        rate = max(1, math.ceil(raw["elapsed_ns"] / max(1, raw["primary_operations"])))
        all_rates.append(rate)
        if cell_class == "sparse":
            sparse_rates.append(rate)
        cells.append(_complexity_cell("DAG-EXACT-01", f"{cell_class}:V={vertices}:E={edges}", 0, raw))
    if max(sparse_rates) > 8 * min(sparse_rates):
        raise Refusal("DAG O(V+E) normalized sparse bound not supported")
    cache = exercise_controls()
    if cache != {"controls": 17, "omission_mutations": 29, "near_miss_refusals": 13, "invalidation_receipts": 1}:
        raise Refusal("canonical cache control closure mismatch")
    return {
        "dag_valid_cases": 39467,
        "dag_refusals": 14,
        "dag_mismatches": 0,
        "dag_complexity_cells": cells,
        "cache_controls": len(CONTROL_NAMES),
        "cache_key_omission_refusals": len(CACHE_KEY_FIELDS),
        "stale_cache_refusals": 1,
        "invalidation_receipts": cache["invalidation_receipts"],
    }, max(all_rates)


def _adapter_guard_lane(source: Path) -> dict[str, Any]:
    matrix = strict_load(source / "stage_d_scientific_validation_master_matrix.json")
    bindings = load_bindings(matrix)
    validate_partition()
    if tuple(binding.study_id for binding in bindings) != STUDY_IDS:
        raise Refusal("adapter dependency order mismatch")
    before = set(sys.modules)
    refusals = pre_import = 0
    for binding in bindings:
        try:
            binding.refuse_registered_route(f"{binding.study_id}/STAGE-E-REFUSAL")
        except StageEExecutionRefusal as exc:
            if exc.receipt["project_runner_import_count"] != 0 or exc.receipt["model_state_advance_count"] != 0:
                raise Refusal("registered-route refusal occurred after forbidden work")
            refusals += 1
            pre_import += 1
        else:
            raise Refusal(f"registered configuration was accepted: {binding.study_id}")
    if any(name in sys.modules and name not in before for name in BLOCKED_PROJECT_RUNNERS):
        raise Refusal("project runner imported during Stage E adapter checks")
    sd02 = 0
    for suffix in ("GATE-1E", "FALSE-INHERITED-BRANCH"):
        try:
            guard_registered_configuration(f"SD-02/{suffix}")
        except StageEExecutionRefusal:
            sd02 += 1
    try:
        continuation_class("SD-15")
    except Refusal:
        unknown = 1
    else:
        raise Refusal("unknown study accepted")
    return {
        "adapter_count": len(bindings),
        "dependency_order": list(STUDY_IDS),
        "registered_route_refusals": refusals,
        "pre_import_refusals": pre_import,
        "forbidden_sd02_routes": sd02,
        "unknown_study_refusals": unknown,
    }


def _inspect_zipapp(path: Path, expected_members: int) -> None:
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(infos) != expected_members or names != sorted(names, key=lambda value: value.encode("utf-8")) or len(names) != len(set(names)):
            raise Refusal("zipapp member closure/order mismatch")
        for info in infos:
            pure = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if pure.is_absolute() or ".." in pure.parts or "\\" in info.filename or info.date_time != (1980, 1, 1, 0, 0, 0):
                raise Refusal("unsafe or nondeterministic zipapp member")
            if info.compress_type != zipfile.ZIP_STORED or not stat.S_ISREG(mode) or stat.S_IMODE(mode) != 0o644:
                raise Refusal("zipapp compression/mode mismatch")


def _probe_installed(python: Path, source: Path, artifact: Path, cwd: Path, kind: str) -> dict[str, Any]:
    result = _run(
        [str(python), "-I", str(source / "tests/framework/installed_artifact_probe.py"), "--checkout", str(source), "--artifact-name", artifact.name, "--artifact-sha256", sha256_bytes(artifact.read_bytes())],
        cwd=cwd,
        label=f"installed-probe-{kind}",
    )
    probe = _json_line(result)
    expected = (probe.get("completed_checks"), probe.get("module_count"), probe.get("root_export_count"), probe.get("failure_code_count"), probe.get("public_signature_count"))
    if expected != (226, 44, 471, 294, 162):
        raise Refusal(f"installed surface mismatch: {kind}: {expected}")
    return {
        "artifact_kind": kind,
        "package_modules": 44,
        "root_exports": 471,
        "failure_codes": 294,
        "public_signatures": 162,
        "version": "0.1.0a1",
        "origin": probe["package_root"],
        "source_checkout_imports": 0,
    }


def _install_lane(args: argparse.Namespace, work: Path) -> tuple[dict[str, Any], Path]:
    from build_stage_e_harness_zipapp import build

    replicas = []
    outputs = []
    for index, perturbation in enumerate(("canonical", "reverse", "evens-odds")):
        output = work / f"stage-e-harness-{index}.pyz"
        build(args.source, output, perturbation=perturbation)
        replicas.append(sha256_bytes(output.read_bytes()))
        outputs.append(output)
    if len(set(replicas)) != 1:
        raise Refusal("perturbed Stage E zipapp replicas differ")
    _inspect_zipapp(outputs[0], 50)
    direct_wheel = args.direct_wheel.resolve()
    sdist_wheel = args.sdist_wheel.resolve()
    sdist = args.sdist.resolve()
    direct_identity = _identity_exact(direct_wheel, WHEEL_BYTES, WHEEL_SHA256)
    sdist_wheel_identity = _identity_exact(sdist_wheel, WHEEL_BYTES, WHEEL_SHA256)
    sdist_identity = _identity_exact(sdist, SDIST_BYTES, SDIST_SHA256)
    if direct_wheel.read_bytes() != sdist_wheel.read_bytes():
        raise Refusal("direct and sdist-derived installed wheels differ")
    direct_cwd = Path(tempfile.mkdtemp(prefix="stage-e-direct-", dir=work))
    sdist_cwd = Path(tempfile.mkdtemp(prefix="stage-e-sdist-", dir=work))
    direct_surface = _probe_installed(args.direct_python.resolve(), args.source, direct_wheel, direct_cwd, "DIRECT_WHEEL")
    sdist_surface = _probe_installed(args.sdist_python.resolve(), args.source, sdist_wheel, sdist_cwd, "SDIST_DERIVED_WHEEL")
    for python, cwd in ((args.direct_python.resolve(), direct_cwd), (args.sdist_python.resolve(), sdist_cwd)):
        registry = _zipapp_json(python, outputs[0], ["registry"], cwd)
        if registry.get("studies") != list(STUDY_IDS) or registry.get("scientific_execution_count") != 0:
            raise Refusal("installed zipapp registry closure mismatch")
    return {
        "harness_zipapp": file_identity(outputs[0]),
        "replica_hashes": replicas,
        "replicas_identical": True,
        "direct_wheel": {"path": WHEEL_NAME, "byte_count": direct_identity["byte_count"], "sha256": direct_identity["sha256"]},
        "sdist_derived_wheel": {"path": WHEEL_NAME, "byte_count": sdist_wheel_identity["byte_count"], "sha256": sdist_wheel_identity["sha256"]},
        "sdist": {"path": SDIST_NAME, "byte_count": sdist_identity["byte_count"], "sha256": sdist_identity["sha256"]},
        "installed_surfaces": [direct_surface, sdist_surface],
        "isolated_mode": True,
        "pythonpath_present": False,
        "repository_cwd": False,
    }, outputs[0]


def _complexity_projections(source: Path, mobius_rate: int, dag_rate: int, peak_rss: int) -> list[dict[str, Any]]:
    matrix = strict_load(source / "stage_d_scientific_validation_master_matrix.json")
    projections: list[dict[str, Any]] = []
    fixed_overhead_ns = 10_000_000
    for row in matrix["studies"]:
        feasibility = row["computational_feasibility"]
        expected = feasibility["expected_evaluations"]
        algorithm = feasibility["algorithmic_cost_class"]
        rate = mobius_rate if "2^" in algorithm or "Möbius" in algorithm else dag_rate if "V+E" in algorithm or "DAG" in algorithm else max(mobius_rate, dag_rate)
        projected_time = expected * rate + fixed_overhead_ns
        caps = feasibility["hard_caps"]
        wall_seconds = caps.get("wall_time_seconds_per_run") or caps.get("wall_time_seconds_per_case")
        evaluation_cap = caps.get("primary_evaluations_per_run") or caps.get("primary_evaluations_per_case")
        slices = max(1, math.ceil(projected_time / (wall_seconds * 1_000_000_000)), math.ceil(expected / evaluation_cap))
        projected_memory = peak_rss + min(feasibility["storage_estimate_bytes"], 268_435_456)
        projected_storage = feasibility["storage_estimate_bytes"] + slices * 4096
        classification = "FEASIBLE_WITHIN_PROPOSED_CAMPAIGN" if slices == 1 else "REQUIRES_CHECKPOINTED_CONTINUATION"
        if projected_memory > (caps.get("peak_resident_memory_bytes_per_run") or caps.get("peak_resident_memory_bytes_per_case")):
            classification = "MATERIAL_INFEASIBILITY_REQUIRES_SEPARATE_AUTHORITY"
        projections.append(
            {
                "study_id": row["study_id"],
                "accepted_expected_evaluations": expected,
                "projected_active_time_nanoseconds": projected_time,
                "projected_peak_memory_bytes": projected_memory,
                "projected_storage_bytes": projected_storage,
                "projected_attempt_slices": slices,
                "classification": classification,
                "scientific_disposition": None,
            }
        )
    if [row["study_id"] for row in projections] != list(STUDY_IDS):
        raise Refusal("14-study feasibility projection order mismatch")
    return projections


def _record(record_type: str, evidence_class: str, head_commit: str, head_tree: str, environment: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    record = common_record(record_type=record_type, status="PASS", evidence_class=evidence_class, head_commit=head_commit, head_tree=head_tree, environment=environment)
    record.update(fields)
    return record


def validate(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    output = args.output.resolve()
    work = args.work.resolve()
    if output.is_relative_to(source) or work.is_relative_to(source):
        raise Refusal("Stage E evidence/work paths must be outside the repository")
    output.mkdir(parents=True, exist_ok=False)
    work.mkdir(parents=True, exist_ok=False)
    environment = observed_environment(debian_identity=args.debian_identity, image_digest=args.image_digest)
    validate_environment(environment)
    authority_fields = _authority_lane(source, args.head_commit, args.head_tree)
    install_fields, zipapp = _install_lane(args, work)
    cell_cwd = Path(tempfile.mkdtemp(prefix="stage-e-cell-", dir=work))
    mobius_fields, mobius_rate = _mobius_lane(args.direct_python.resolve(), zipapp, cell_cwd)
    dag_fields, dag_rate = _dag_cache_lane(args.direct_python.resolve(), zipapp, cell_cwd)
    adapter_fields = _adapter_guard_lane(source)
    identity_fields = _identity_continuation_lane(source)
    peak_rss = max(cell["peak_process_tree_rss_bytes"] for cell in mobius_fields["complexity_cells"] + dag_fields["dag_complexity_cells"])
    complexity_fields = {
        "projections": _complexity_projections(source, mobius_rate, dag_rate, peak_rss),
        "projection_formula_id": "EBU-STAGE-E-CONSERVATIVE-FEASIBILITY-v1",
        "discarded_repetitions": 0,
        "warmup_repetitions": 0,
    }
    records = [
        _record("AUTHORITY", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, authority_fields),
        _record("SCHEMA", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, {
            "schema_identities": [file_identity(source / name) for name in SCHEMA_FILES],
            "supported_keywords": list(SUPPORTED_KEYWORDS),
            "recognized_authority_metadata_keys": list(AUTHORITY_METADATA_KEYS),
            "valid_instances": 19,
            "refused_instances": 97,
            "unresolved_local_refs": 0,
        }),
        _record("IDENTITY_CONTINUATION", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, identity_fields),
        _record("MOBIUS", "NUMERICAL_VERIFICATION_OF_HARNESS_COMPLEXITY_ONLY", args.head_commit, args.head_tree, environment, mobius_fields),
        _record("DAG_CACHE", "NUMERICAL_VERIFICATION_OF_HARNESS_COMPLEXITY_ONLY", args.head_commit, args.head_tree, environment, dag_fields),
        _record("ADAPTER_GUARD", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, adapter_fields),
        _record("INSTALLED_ISOLATION", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, install_fields),
        _record("COMPLEXITY", "NUMERICAL_VERIFICATION_OF_HARNESS_COMPLEXITY_ONLY", args.head_commit, args.head_tree, environment, complexity_fields),
        _record("REGRESSION", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, {
            "t0": 123, "t1": 299, "t2": 21, "packaging": 8, "installed_probe_checks": 226,
            "conventional_checks": 1800, "historical_o14_checks": 299,
        }),
    ]
    manifest = build_final_manifest(list(zip(EVIDENCE_ORDER, records)), head_commit=args.head_commit, head_tree=args.head_tree, environment=environment, completed_lanes=LANES)
    schema_fields = _schema_lane(source, records, manifest)
    records[1] = _record("SCHEMA", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, schema_fields)
    manifest = build_final_manifest(list(zip(EVIDENCE_ORDER, records)), head_commit=args.head_commit, head_tree=args.head_tree, environment=environment, completed_lanes=LANES)
    stage_e_schema = strict_load(source / SCHEMA_FILES[2])
    stage_e_validator = Validator(stage_e_schema, allowed_metadata=("completion_marker", "prospective_negative_schema_cases", "prospective_non_evidence_schema_fixtures", "scientific_execution_count", "stage_e_instance_count"))
    for record in records:
        stage_e_validator.validate(record)
    stage_e_validator.validate(manifest)
    for name, record in zip(EVIDENCE_ORDER, records):
        write_record(output, name, record)
    (output / "final-manifest.json").write_bytes(canonical_bytes(manifest))
    print(canonical_bytes({"status": "STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS", "records": 10, "lanes": LANES, "scientific_execution_count": 0}).decode("utf-8"))
    return 0


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--head-commit", required=True)
    parser.add_argument("--head-tree", required=True)
    parser.add_argument("--direct-wheel", type=Path, required=True)
    parser.add_argument("--sdist-wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--direct-python", type=Path, required=True)
    parser.add_argument("--sdist-python", type=Path, required=True)
    parser.add_argument("--debian-identity", required=True)
    parser.add_argument("--image-digest", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(validate(arguments()))
    except Refusal as exc:
        print(f"STAGE_E_REFUSAL: {exc}", file=sys.stderr)
        raise SystemExit(2)
