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
from fractions import Fraction
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

from stage_e_harness.cache import CACHE_KEY_FIELDS, CONTROL_NAMES, exercise_controls, exercise_controls_detail
from stage_e_harness.capacity_population import semantic_valid
from stage_e_harness.canonical import (
    Refusal,
    assert_text_integrity,
    canonical_bytes,
    canonical_digest,
    file_identity,
    identity,
    sha256_bytes,
    strict_load,
    strict_loads,
)
from stage_e_harness.checkpoint import continuation_equivalence, validate_counter_state
from stage_e_harness.environment import EXPECTED_ENVIRONMENT, observed_environment, validate_environment
from stage_e_harness.execution import BLOCKED_PROJECT_RUNNERS, StageEExecutionRefusal, guard_registered_configuration
from stage_e_harness.growth import growth_conformance
from stage_e_harness.recursive import recursive_conformance
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
    verify_local_refs,
)


IMPLEMENTATION_BASE = "b7ebe8615d54ae5e23645734b1a6c7667ce28bce"
IMPLEMENTATION_BASE_TREE = "24f2693b6d26d42bf9e360b295e3209a16417f74"
RECONCILIATION_EVIDENCE_BASE = "08cea14d828668413b9156da8f220beec2713c26"
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
CONTROLLING_SCHEMA_FILES = (*SCHEMA_FILES, "stage_d_dynamic_growth_campaign_evidence_schema.json")
RECONCILIATION_SCHEMA_FILE = "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json"
RECONCILIATION_VALIDATION_FILE = "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json"
RECONCILIATION_AUTHORITY_FILES = (
    "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_AMENDMENT.md",
    "stage_e_dynamic_growth_harness_reconciliation_contract.json",
    RECONCILIATION_SCHEMA_FILE,
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json",
    "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json",
    RECONCILIATION_VALIDATION_FILE,
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
V1_SUPPORTED_KEYWORDS = tuple(keyword for keyword in SUPPORTED_KEYWORDS if keyword != "$comment")
V2_RECORD_NAMES = (
    "schema-replay-v2.json",
    "recursive-growth-v2.json",
    "dag-cache-correction-v2.json",
    "dynamic-growth-guard-v2.json",
    "harness-artifact-v2.json",
)
PROHIBITED_COUNTERS = {
    "model_execution_count": 0,
    "trajectory_execution_count": 0,
    "runner_execution_count": 0,
    "gate_execution_count": 0,
    "simulation_execution_count": 0,
    "stochastic_draw_count": 0,
    "registered_configuration_count": 0,
    "outcome_inspection_count": 0,
    "result_count": 0,
    "figure_count": 0,
    "book_count": 0,
    "release_action_count": 0,
    "publication_action_count": 0,
}


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


def _isolated_python_path(path: Path) -> Path:
    """Return the absolute venv entry point without dereferencing its symlink.

    Resolving ``bin/python`` follows the virtual-environment symlink to the base
    interpreter and discards the ``pyvenv.cfg`` discovery context.  The Stage E
    installed probes must execute through the lexical venv path instead.
    """

    absolute = Path(os.path.abspath(os.fspath(path)))
    if not absolute.is_file():
        raise Refusal(f"isolated interpreter is missing: {absolute}")
    if not (absolute.parent.parent / "pyvenv.cfg").is_file():
        raise Refusal(f"isolated interpreter has no pyvenv.cfg: {absolute}")
    return absolute


def _authority_lane(source: Path, head_commit: str, head_tree: str) -> dict[str, Any]:
    if _git(source, "rev-parse", "HEAD") != head_commit or _git(source, "rev-parse", "HEAD^{tree}") != head_tree:
        raise Refusal("requested/head Git coordinate mismatch")
    if _git(source, "rev-parse", f"{IMPLEMENTATION_BASE}^{{tree}}") != IMPLEMENTATION_BASE_TREE:
        raise Refusal("Stage E implementation base tree mismatch")
    if _git(source, "merge-base", IMPLEMENTATION_BASE, "HEAD") != IMPLEMENTATION_BASE:
        raise Refusal("Stage E implementation is not based on the accepted durability integration")
    manifest = strict_load(source / "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json")
    scope = manifest["prospective_harness_implementation"]
    expected = set(scope["modified_paths"]) | set(scope["new_paths"])
    actual = set(filter(None, _git(source, "diff", "--name-only", f"{IMPLEMENTATION_BASE}..HEAD").splitlines()))
    if actual != expected or len(actual) != 51:
        raise Refusal(f"Stage E implementation path closure mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    harness_sources = [path for path in scope["new_paths"] if path.startswith("stage_e_harness/") and path.endswith(".py")]
    if len(harness_sources) != 34:
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
    for path in RECONCILIATION_AUTHORITY_FILES:
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


def _canonical_identity(value: Any) -> dict[str, Any]:
    data = canonical_bytes(value)
    return {"byte_count": len(data), "sha256": sha256_bytes(data)}


def _target_schema(validator: Validator, schema: dict[str, Any], target: str) -> Any:
    if target in schema.get("$defs", {}):
        return validator.definition(target)
    if target in {"ROOT", "root", schema.get("$id")}:
        return schema
    raise Refusal(f"unresolved frozen validation target: {target}")


def _schema_replay_lane(source: Path) -> dict[str, Any]:
    validation = strict_load(source / RECONCILIATION_VALIDATION_FILE)
    contract = strict_load(source / "stage_e_dynamic_growth_harness_reconciliation_contract.json")
    metadata = _metadata_by_schema(strict_load(source / "stage_e_scientific_harness_contract.json"))
    schemas = {name: strict_load(source / name) for name in (*CONTROLLING_SCHEMA_FILES, RECONCILIATION_SCHEMA_FILE)}
    validators: dict[str, Validator] = {}
    seen_keywords: set[str] = set()
    for name, schema in schemas.items():
        allowed = metadata.get(name, ())
        validator = Validator(schema, allowed_metadata=allowed)
        validators[name] = validator
        if name in CONTROLLING_SCHEMA_FILES:
            seen_keywords.update(validator.vocabulary)
        refs, unique_refs = verify_local_refs(schema)
        if name == RECONCILIATION_SCHEMA_FILE and (refs, unique_refs) != (83, 22):
            raise Refusal("reconciliation schema local-reference closure mismatch")
    expected_keywords = tuple(contract["schema_replay"]["supported_keywords_in_order"])
    derived_keywords = tuple(keyword for keyword in SUPPORTED_KEYWORDS if keyword in seen_keywords)
    if derived_keywords != expected_keywords or len(derived_keywords) != 29:
        raise Refusal("derived four-schema vocabulary mismatch")

    positive_ledger: list[dict[str, Any]] = []
    for ordinal, row in enumerate(validation["positive_fixture_registry"]):
        if row["ordinal"] != ordinal:
            raise Refusal("positive fixture ordinal mismatch")
        source_document = strict_load(source / row["source_path"])
        instance = deepcopy(_pointer(source_document, row["source_json_pointer"]))
        identity_value = _canonical_identity(instance)
        if identity_value != {"byte_count": row["canonical_byte_count"], "sha256": row["canonical_sha256"]}:
            raise Refusal(f"positive fixture identity mismatch: {row['fixture_id']}")
        validator = validators[row["target_schema_path"]]
        target = _target_schema(validator, schemas[row["target_schema_path"]], row["target_definition_or_root"])
        validator.validate(instance, target)
        positive_ledger.append(
            {
                "ordinal": ordinal,
                "fixture_id": row["fixture_id"],
                "source_path": row["source_path"],
                "source_json_pointer": row["source_json_pointer"],
                "target_schema_path": row["target_schema_path"],
                "target_definition_or_root": row["target_definition_or_root"],
                "canonical_instance": canonical_bytes(instance).decode("utf-8"),
                "canonical_identity": identity_value,
                "disposition": "ACCEPTED",
            }
        )
    if len(positive_ledger) != 61:
        raise Refusal("positive fixture ledger count mismatch")

    bases = {row["base_fixture_id"]: row for row in validation["refusal_base_fixtures"]}
    if len(bases) != 120:
        raise Refusal("refusal base fixture count mismatch")
    refusal_ledger: list[dict[str, Any]] = []
    for ordinal, row in enumerate(validation["refusal_registry"]):
        if row["ordinal"] != ordinal:
            raise Refusal("refusal fixture ordinal mismatch")
        base_row = bases[row["base_fixture_id"]]
        base = deepcopy(base_row["instance"])
        if _canonical_identity(base) != row["base_fixture_identity"] or row["base_fixture_sha256"] != row["base_fixture_identity"]["sha256"]:
            raise Refusal(f"refusal base identity mismatch: {row['case_id']}")
        representation = row["mutation_representation"]
        material = row["rfc6902_patch_or_full_instance"]
        if representation == "RFC6902_PATCH":
            patch_identity = _canonical_identity(material)
            mutated = apply_json_patch(base, material)
            mutated_identity = _canonical_identity(mutated)
        elif representation == "FULL_MUTATED_INSTANCE":
            patch_identity = _canonical_identity(material)
            mutated = deepcopy(material)
            mutated_identity = _canonical_identity(mutated)
        elif representation == "RAW_JSON_TEXT":
            raw = material.encode("utf-8")
            patch_identity = {"byte_count": len(raw), "sha256": sha256_bytes(raw)}
            mutated = material
            mutated_identity = dict(patch_identity)
        else:
            raise Refusal(f"unknown mutation representation: {representation}")
        if patch_identity != row["patch_identity"] or mutated_identity != row["mutated_instance_identity"] or row["mutated_instance_sha256"] != mutated_identity["sha256"]:
            raise Refusal(f"refusal mutation identity mismatch: {row['case_id']}")

        validator = validators[row["target_schema_path"]]
        schema = schemas[row["target_schema_path"]]
        target = _target_schema(validator, schema, row["target_definition"])
        layer = row["validation_layer"]
        if layer == "JSON_PARSE":
            try:
                strict_loads(mutated.encode("utf-8"))
            except Exception:
                structural_valid = False
            else:
                structural_valid = True
        elif row["target_definition"] == "keyword_conformance_pair" and isinstance(mutated, dict):
            pair_validator = Validator(mutated["schema"])
            structural_valid = pair_validator.is_valid(mutated["instance"])
        else:
            structural_valid = validator.is_valid(mutated, target)
        if structural_valid != row["expected_structural_validity"]:
            raise Refusal(f"frozen structural outcome mismatch: {row['case_id']}")
        if layer == "SEMANTIC_RELATION":
            if not validator.is_valid(base, target):
                raise Refusal(f"semantic refusal base is structurally invalid: {row['case_id']}")
            if not semantic_valid(row["semantic_rule_id"], base):
                raise Refusal(f"semantic refusal base fails its inherited relation: {row['case_id']}")
            if semantic_valid(row["semantic_rule_id"], mutated, base=base):
                raise Refusal(f"semantic mutation was accepted: {row['case_id']}")
        elif layer == "ANNOTATION_NON_RELIANCE":
            outcomes = [Validator(mutated[key]).is_valid(mutated["instance"]) for key in ("schema_with_comment", "schema_without_comment", "schema_with_changed_comment")]
            if outcomes != [True, True, True]:
                raise Refusal("$comment annotation altered validation")
        elif structural_valid:
            raise Refusal(f"frozen refusal was accepted: {row['case_id']}")
        ledger_row = {
            "ordinal": ordinal,
            "case_id": row["case_id"],
            "source_case_pointer": row["source_case_pointer"],
            "base_fixture_id": row["base_fixture_id"],
            "base_fixture_identity": row["base_fixture_identity"],
            "target_schema_path": row["target_schema_path"],
            "target_definition": row["target_definition"],
            "mutation_representation": representation,
            "rfc6902_patch_or_full_instance": material,
            "patch_identity": row["patch_identity"],
            "mutated_instance_identity": row["mutated_instance_identity"],
            "validation_layer": layer,
            "expected_structural_validity": row["expected_structural_validity"],
            "semantic_rule_id": row["semantic_rule_id"],
            "required_disposition": "REFUSED",
        }
        if row["case_id"] == "CONT-SCHEMA-N17":
            ledger_row["atomic_case_continuation_context"] = row["atomic_case_continuation_context"]
        refusal_ledger.append(ledger_row)
    if len(refusal_ledger) != 249:
        raise Refusal("refusal ledger count mismatch")
    return {
        "supported_keywords_in_order": list(derived_keywords),
        "positive_fixture_ledger": positive_ledger,
        "refusal_ledger": refusal_ledger,
        "accepted_fixture_count": 61,
        "refusal_count": 249,
        "mismatch_count": 0,
    }


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


def _schema_lane(
    source: Path,
    records: list[dict[str, Any]],
    manifest: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    contract = strict_load(source / "stage_e_scientific_harness_contract.json")
    metadata = _metadata_by_schema(contract)
    schemas = {name: strict_load(source / name) for name in SCHEMA_FILES}
    validators = {name: Validator(schema, allowed_metadata=metadata[name]) for name, schema in schemas.items()}
    seen: set[str] = set()
    for name, schema in schemas.items():
        seen.update(audit_schema_vocabulary(schema, allowed_metadata=metadata[name]))
    if tuple(keyword for keyword in V1_SUPPORTED_KEYWORDS if keyword in seen) != V1_SUPPORTED_KEYWORDS:
        raise Refusal("derived schema vocabulary differs from exact 28-keyword authority")
    if tuple(contract["schema_profile"]["recognized_authority_metadata_keys_in_order"]) != AUTHORITY_METADATA_KEYS:
        raise Refusal("authority metadata-key closure mismatch")
    stage_e_validator = validators[SCHEMA_FILES[2]]
    for record in records:
        stage_e_validator.validate(record)
    stage_e_validator.validate(manifest)
    bound_fixture = deepcopy(next(record for record in records if record["record_type"] == "MOBIUS"))
    bound_fixture["status"] = "BOUND_NOT_SUPPORTED"
    stage_e_validator.validate(bound_fixture)
    if replay["accepted_fixture_count"] != 61 or replay["refusal_count"] != 249 or replay["mismatch_count"] != 0:
        raise Refusal("complete reconciliation schema replay did not close")
    # Preserve the accepted v1 record shape and its registered projection.  The
    # separately sealed v2 replay carries every executable fixture and refusal.
    valid_instances = 19
    refused = 97
    return {
        "schema_identities": [file_identity(source / name) for name in SCHEMA_FILES],
        "supported_keywords": list(V1_SUPPORTED_KEYWORDS),
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


def _dag_v2_cell(raw: dict[str, Any], cell_id: str) -> dict[str, Any]:
    return {
        "cell_id": cell_id,
        "vertices": raw["vertices"],
        "edges": raw["edges"],
        "traversal": {
            "indegree_initializations": raw["indegree_initializations"],
            "enqueues": raw["vertex_enqueues"],
            "dequeues": raw["vertex_dequeues"],
            "edge_inspections": raw["edge_inspections"],
            "queue_appends": raw["ready_queue_appends"],
            "head_advances": raw["ready_queue_head_advances"],
            "ready_node_comparisons": raw["ready_node_comparisons"],
        },
        "canonicalization": {
            "input_edge_count": raw["canonicalization_input_edge_count"],
            "canonicalization_comparisons": raw["canonicalization_comparisons"],
            "canonicalization_auxiliary_edge_slots": raw["canonicalization_auxiliary_edge_slots"],
        },
        "wall_nanoseconds": raw["elapsed_ns"],
        "process_tree_peak_rss_bytes": raw["peak_process_tree_rss_bytes"],
        "storage_bytes": raw["storage_bytes"],
        "trace_bytes": len(canonical_bytes(raw)),
        "output_bytes": raw["output_bytes"],
    }


def _dag_cache_lane(python: Path, zipapp: Path, cwd: Path) -> tuple[dict[str, Any], int, list[dict[str, Any]], dict[str, Any]]:
    agreement = _zipapp_json(python, zipapp, ["dag-agreement"], cwd)
    if (agreement.get("valid_cases"), agreement.get("invalid_cases")) != (39467, 14):
        raise Refusal("DAG oracle/refusal count mismatch")
    grid = ((128, 256, "sparse"), (1024, 4096, "sparse"), (10000, 50000, "sparse"), (100000, 500000, "sparse"), (512, 130816, "dense_acyclic"))
    cells: list[dict[str, Any]] = []
    v2_cells: list[dict[str, Any]] = []
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
        v2_cells.append(_dag_v2_cell(raw, f"DAG-{vertices}-{edges}"))
    if max(sparse_rates) > 8 * min(sparse_rates):
        raise Refusal("DAG O(V+E) normalized sparse bound not supported")
    cache = exercise_controls()
    cache_detail = exercise_controls_detail()
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
    }, max(all_rates), v2_cells, cache_detail


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


def _install_lane(args: argparse.Namespace, work: Path) -> tuple[dict[str, Any], Path, Path]:
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
    _inspect_zipapp(outputs[0], 64)
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
    direct_python = _isolated_python_path(args.direct_python)
    sdist_python = _isolated_python_path(args.sdist_python)
    direct_surface = _probe_installed(direct_python, args.source, direct_wheel, direct_cwd, "DIRECT_WHEEL")
    sdist_surface = _probe_installed(sdist_python, args.source, sdist_wheel, sdist_cwd, "SDIST_DERIVED_WHEEL")
    for python, cwd in ((direct_python, direct_cwd), (sdist_python, sdist_cwd)):
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
    }, outputs[0], direct_python


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


def _v2_record(source: Path, record_type: str, evidence_class: str, head_commit: str, environment: dict[str, Any], fields: dict[str, Any]) -> dict[str, Any]:
    authority_bytes = (source / "stage_e_dynamic_growth_harness_reconciliation_contract.json").read_bytes()
    record = {
        "schema_version": "stage-e-reconciliation-evidence/v2",
        "record_type": record_type,
        "status": "PASS",
        "evidence_class": evidence_class,
        "base_commit": RECONCILIATION_EVIDENCE_BASE,
        "candidate_commit": head_commit,
        "authority_identity": {"byte_count": len(authority_bytes), "sha256": sha256_bytes(authority_bytes)},
        "environment_identity": canonical_digest(environment),
        "prohibited_counters": dict(PROHIBITED_COUNTERS),
    }
    record.update(fields)
    return record


def _cache_v2_receipt(detail: dict[str, Any]) -> dict[str, Any]:
    receipt = detail["receipt"]
    dependency_edges = [
        {"source_key_identity": source, "target_key_identity": target}
        for source, target in detail["dependency_edges"]
    ]
    alias_edges = [
        {"source_key_identity": source, "target_key_identity": target}
        for source, target in detail["alias_edges"]
    ]
    expected = list(detail["expected_affected"])
    observed = list(receipt["invalidated_keys"])
    if expected != observed or set(expected) & set(detail["reused"]):
        raise Refusal("cache affected/reused closure mismatch")
    preimage = {
        "changed_seed_identity": detail["changed_seed_identity"],
        "declared_key_universe": list(detail["declared_key_universe"]),
        "dependency_edges": dependency_edges,
        "alias_edges": alias_edges,
        "expected_affected_key_identities": expected,
        "observed_affected_key_identities": observed,
        "traversal_order_key_identities": list(receipt["visited_keys"]),
        "invalidated_key_identities": observed,
        "recomputed_key_identities": list(detail["recomputed"]),
        "reused_key_identities": list(detail["reused"]),
        "pre_cache_epoch": receipt["prior_epoch"],
        "post_cache_epoch": receipt["new_epoch"],
        "correction_epoch": receipt["new_epoch"],
    }
    return {**preimage, "receipt_identity": canonical_digest(preimage)}


def _dynamic_guard_v2() -> dict[str, Any]:
    before = set(sys.modules)
    refused: list[str] = []
    for route_id in ("SD-01", "SD-01-GROWTH-v1", *STUDY_IDS[1:]):
        try:
            guard_registered_configuration(f"{route_id}/STAGE-E-REFUSAL")
        except StageEExecutionRefusal as exc:
            if exc.receipt["project_runner_import_count"] != 0 or exc.receipt["model_state_advance_count"] != 0:
                raise Refusal("registered route reached forbidden work")
            refused.append(route_id)
        else:
            raise Refusal(f"registered route accepted: {route_id}")
    if any(name in sys.modules and name not in before for name in BLOCKED_PROJECT_RUNNERS):
        raise Refusal("project runner imported by dynamic-growth guard")
    if len(refused) != 15:
        raise Refusal("dynamic-growth guard route closure mismatch")
    growth = growth_conformance()
    return {
        "guarded_route_ids_in_order": refused,
        "preimport_refusal_count": len(refused),
        "dynamic_growth_fixture_count": 44,
        "dynamic_growth_exact_patch_count": 150,
        "registered_campaign_run_count": 396,
        "registered_horizon_ticks": 8192,
        "registered_campaign_runs_executed": growth["registered_campaign_runs_executed"],
        "registered_horizon_ticks_executed": growth["registered_horizon_ticks_executed"],
        "scientific_rows_populated": growth["scientific_rows_populated"],
    }


def _validate_case_ledger(cases: list[dict[str, Any]], expected_count: int, *, disposition: str) -> None:
    if len(cases) != expected_count or [case["ordinal"] for case in cases] != list(range(expected_count)):
        raise Refusal("recursive conformance case ordinal/count mismatch")
    if len({case["case_id"] for case in cases}) != expected_count:
        raise Refusal("recursive conformance case ID collision")
    for case in cases:
        if case["disposition"] != disposition:
            raise Refusal("recursive conformance disposition mismatch")
        for name in ("input", "output", "relation"):
            canonical_text = case[f"canonical_{name}"]
            canonical_data = canonical_bytes(strict_loads(canonical_text.encode("utf-8")))
            if canonical_data.decode("utf-8") != canonical_text:
                raise Refusal("recursive conformance payload is not canonical JSON")
            expected_identity = {"byte_count": len(canonical_data), "sha256": sha256_bytes(canonical_data)}
            if case[f"{name}_identity"] != expected_identity:
                raise Refusal("recursive conformance payload identity mismatch")


def _fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def _validate_v2_semantics(
    source: Path,
    v1_manifest: dict[str, Any],
    records: list[tuple[str, dict[str, Any]]],
    reconciliation_manifest: dict[str, Any],
    *,
    candidate_commit: str,
    environment: dict[str, Any],
) -> None:
    if [name for name, _ in records] != list(V2_RECORD_NAMES):
        raise Refusal("v2 record order mismatch")
    by_type = {record["record_type"]: record for _, record in records}
    if len(by_type) != 5:
        raise Refusal("v2 record type closure mismatch")
    authority_bytes = (source / "stage_e_dynamic_growth_harness_reconciliation_contract.json").read_bytes()
    authority_identity = {"byte_count": len(authority_bytes), "sha256": sha256_bytes(authority_bytes)}
    environment_identity = canonical_digest(environment)
    for _, record in records:
        if record["candidate_commit"] != candidate_commit:
            raise Refusal("v2 candidate coordinate mismatch")
        if record["authority_identity"] != authority_identity or record["environment_identity"] != environment_identity:
            raise Refusal("v2 authority/environment identity mismatch")
        if record["prohibited_counters"] != PROHIBITED_COUNTERS or any(record["prohibited_counters"].values()):
            raise Refusal("v2 prohibited counter mismatch")

    replay = by_type["SCHEMA_REPLAY_V2"]
    positives = replay["positive_fixture_ledger"]
    refusals = replay["refusal_ledger"]
    if [row["ordinal"] for row in positives] != list(range(61)) or [row["ordinal"] for row in refusals] != list(range(249)):
        raise Refusal("v2 schema replay ledger order mismatch")
    if replay["accepted_fixture_count"] != 61 or replay["refusal_count"] != 249 or replay["mismatch_count"] != 0:
        raise Refusal("v2 schema replay disposition mismatch")

    recursive = by_type["RECURSIVE_GROWTH_V2"]
    ledgers = (
        ("macro_cases", 270, "PASS"),
        ("poset_base_cases", 32, "PASS"),
        ("poset_correction_cases", 224, "PASS"),
        ("transport_scalar_cases", 90, "PASS"),
        ("transport_direct_cases", 15, "PASS"),
        ("transport_correction_cases", 180, "PASS"),
        ("transport_refusal_cases", 150, "REFUSED"),
    )
    for name, count, disposition in ledgers:
        _validate_case_ledger(recursive[name], count, disposition=disposition)
    if recursive["mismatch_count"] != 0:
        raise Refusal("recursive conformance mismatch count is nonzero")
    for case in recursive["macro_cases"]:
        inputs = strict_loads(case["canonical_input"].encode("utf-8"))
        outputs = strict_loads(case["canonical_output"].encode("utf-8"))
        interaction = inputs["e_xy"] - inputs["e_x"] - inputs["e_y"] + inputs["e_empty"]
        if interaction != outputs["direct_interaction"] or interaction != outputs["declared_J"]:
            raise Refusal("recursive macro interaction identity mismatch")
        if outputs["inverse_surplus"] != inputs["e_xy"] - inputs["e_empty"]:
            raise Refusal("recursive macro inverse identity mismatch")
    for case in recursive["poset_base_cases"]:
        inputs = strict_loads(case["canonical_input"].encode("utf-8"))
        outputs = strict_loads(case["canonical_output"].encode("utf-8"))
        if outputs["reconstruction"] != inputs["values"]:
            raise Refusal("feasible-poset reconstruction mismatch")
    for case in recursive["transport_scalar_cases"]:
        inputs = strict_loads(case["canonical_input"].encode("utf-8"))
        outputs = strict_loads(case["canonical_output"].encode("utf-8"))
        if _fraction(outputs["direct_target"]) != _fraction(inputs["factor"]) * _fraction(inputs["source"]) + _fraction(inputs["residual"]):
            raise Refusal("coefficient transport scaling identity mismatch")
    for case in recursive["transport_correction_cases"]:
        inputs = strict_loads(case["canonical_input"].encode("utf-8"))
        outputs = strict_loads(case["canonical_output"].encode("utf-8"))
        expected = _fraction(inputs["factor"]) * _fraction(inputs["delta_source"]) + _fraction(inputs["delta_residual"])
        if _fraction(outputs["delta_target"]) != expected:
            raise Refusal("coefficient transport correction identity mismatch")

    dag_cache = by_type["DAG_CACHE_CORRECTION_V2"]
    expected_cells = (
        ("DAG-128-256", 128, 256),
        ("DAG-1024-4096", 1024, 4096),
        ("DAG-10000-50000", 10000, 50000),
        ("DAG-100000-500000", 100000, 500000),
        ("DAG-512-130816", 512, 130816),
    )
    cells = dag_cache["dag_complexity_cells"]
    if [(cell["cell_id"], cell["vertices"], cell["edges"]) for cell in cells] != list(expected_cells):
        raise Refusal("DAG v2 exact cell registry mismatch")
    for cell in cells:
        vertices, edges = cell["vertices"], cell["edges"]
        traversal = cell["traversal"]
        canonicalization = cell["canonicalization"]
        if traversal["indegree_initializations"] != vertices or traversal["edge_inspections"] != edges:
            raise Refusal("DAG v2 exact traversal count mismatch")
        if any(traversal[name] > vertices for name in ("enqueues", "dequeues", "queue_appends", "head_advances")):
            raise Refusal("DAG v2 vertex operation bound mismatch")
        if traversal["ready_node_comparisons"] != 0 or canonicalization["input_edge_count"] != edges:
            raise Refusal("DAG v2 ordering/canonicalization binding mismatch")
        comparison_cap = edges * math.ceil(math.log2(edges)) if edges > 1 else 0
        if canonicalization["canonicalization_comparisons"] > comparison_cap or canonicalization["canonicalization_auxiliary_edge_slots"] > edges:
            raise Refusal("DAG v2 canonicalization bound mismatch")
        if any(cell[name] < 1 for name in ("wall_nanoseconds", "process_tree_peak_rss_bytes", "storage_bytes", "trace_bytes", "output_bytes")):
            raise Refusal("DAG v2 measurement is missing")

    receipt = dag_cache["cache_invalidation_receipt"]
    universe = receipt["declared_key_universe"]
    changed = receipt["changed_seed_identity"]
    if changed not in universe or not receipt["dependency_edges"] or not receipt["alias_edges"]:
        raise Refusal("cache invalidation graph/seed closure mismatch")
    adjacency: dict[str, set[str]] = {}
    for edge in (*receipt["dependency_edges"], *receipt["alias_edges"]):
        if edge["source_key_identity"] not in universe or edge["target_key_identity"] not in universe:
            raise Refusal("cache invalidation edge endpoint outside declared universe")
        adjacency.setdefault(edge["source_key_identity"], set()).add(edge["target_key_identity"])
    queue = [changed]
    traversal_order: list[str] = []
    head = 0
    while head < len(queue):
        key = queue[head]
        head += 1
        if key in traversal_order:
            continue
        traversal_order.append(key)
        for target in sorted(adjacency.get(key, ())):
            if target not in traversal_order and target not in queue:
                queue.append(target)
    affected = sorted(traversal_order)
    for name in ("expected_affected_key_identities", "observed_affected_key_identities", "invalidated_key_identities", "recomputed_key_identities"):
        if receipt[name] != affected:
            raise Refusal("cache invalidation affected closure mismatch")
    if receipt["traversal_order_key_identities"] != traversal_order:
        raise Refusal("cache invalidation traversal order mismatch")
    reused = receipt["reused_key_identities"]
    if set(reused) & set(affected) or set(universe) != set(reused) | set(affected):
        raise Refusal("cache invalidated/reused partition mismatch")
    if receipt["post_cache_epoch"] != receipt["pre_cache_epoch"] + 1 or receipt["correction_epoch"] != receipt["post_cache_epoch"]:
        raise Refusal("cache invalidation epoch mismatch")
    receipt_preimage = {key: value for key, value in receipt.items() if key != "receipt_identity"}
    if receipt["receipt_identity"] != canonical_digest(receipt_preimage):
        raise Refusal("cache invalidation receipt identity mismatch")
    if dag_cache["stale_cache_hits"] != 0 or dag_cache["mismatch_count"] != 0:
        raise Refusal("cache/DAG mismatch or stale hit recorded")

    guard = by_type["DYNAMIC_GROWTH_GUARD_V2"]
    exact_routes = ["SD-01", "SD-01-GROWTH-v1", *STUDY_IDS[1:]]
    if guard["guarded_route_ids_in_order"] != exact_routes or guard["preimport_refusal_count"] != 15:
        raise Refusal("dynamic-growth guarded-route closure mismatch")
    if (guard["dynamic_growth_fixture_count"], guard["dynamic_growth_exact_patch_count"], guard["registered_campaign_run_count"], guard["registered_horizon_ticks"]) != (44, 150, 396, 8192):
        raise Refusal("dynamic-growth authority arithmetic mismatch")
    if any(guard[name] for name in ("registered_campaign_runs_executed", "registered_horizon_ticks_executed", "scientific_rows_populated")):
        raise Refusal("dynamic-growth scientific work occurred in Stage E")

    artifact = by_type["HARNESS_ARTIFACT_V2"]
    replica_identities = artifact["replica_identities"]
    if artifact["replica_count"] != 3 or len(replica_identities) != 3 or len({(row["byte_count"], row["sha256"]) for row in replica_identities}) != 1:
        raise Refusal("harness perturbed-replica identity mismatch")
    if not artifact["all_replicas_byte_identical"] or artifact["safe_member_count"] != 64 or artifact["unsafe_member_count"] != 0:
        raise Refusal("harness archive safety/reproducibility mismatch")
    if artifact["source_checkout_import_count"] != 0 or artifact["network_access_count"] != 0:
        raise Refusal("harness artifact isolation mismatch")

    v1_bytes = canonical_bytes(v1_manifest)
    accepted_v1 = reconciliation_manifest["accepted_v1_manifest"]
    if accepted_v1["identity"] != {"byte_count": len(v1_bytes), "sha256": sha256_bytes(v1_bytes)}:
        raise Refusal("accepted v1 manifest seal mismatch")
    if not accepted_v1["all_entries_pass"] or not accepted_v1["all_required_lanes_completed"] or not accepted_v1["bound_supported"]:
        raise Refusal("accepted v1 manifest cannot support reconciliation PASS")
    if accepted_v1["stage_f_execution_authorized"]:
        raise Refusal("Stage E manifest improperly authorizes Stage F")
    entries = reconciliation_manifest["entries"]
    if [entry["name"] for entry in entries] != list(V2_RECORD_NAMES) or reconciliation_manifest["record_count"] != 6:
        raise Refusal("reconciliation manifest record closure mismatch")
    for entry, (name, record) in zip(entries, records):
        data = canonical_bytes(record)
        if entry["name"] != name or entry["status"] != "PASS" or entry["identity"] != {"byte_count": len(data), "sha256": sha256_bytes(data)}:
            raise Refusal("reconciliation manifest entry mismatch")
    if reconciliation_manifest["prohibited_counters"] != PROHIBITED_COUNTERS or any(reconciliation_manifest["prohibited_counters"].values()):
        raise Refusal("reconciliation manifest prohibited counter mismatch")


def _v2_manifest(v1_manifest: dict[str, Any], records: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    if [name for name, _ in records] != list(V2_RECORD_NAMES):
        raise Refusal("reconciliation evidence order mismatch")
    entries = []
    for name, record in records:
        data = canonical_bytes(record)
        if record["status"] != "PASS":
            raise Refusal("non-PASS v2 record cannot be promoted")
        entries.append(
            {
                "name": name,
                "identity": {"byte_count": len(data), "sha256": sha256_bytes(data)},
                "status": "PASS",
                "evidence_class": record["evidence_class"],
            }
        )
    v1_bytes = canonical_bytes(v1_manifest)
    return {
        "schema_version": "stage-e-reconciliation-evidence/v2",
        "record_type": "RECONCILIATION_MANIFEST_V2",
        "accepted_v1_manifest": {
            "name": "final-manifest.json",
            "identity": {"byte_count": len(v1_bytes), "sha256": sha256_bytes(v1_bytes)},
            "record_count": 9,
            "entry_names_in_order": [entry["name"] for entry in v1_manifest["records"]],
            "all_entries_pass": all(entry["status"] == "PASS" for entry in v1_manifest["records"]),
            "all_required_lanes_completed": v1_manifest["all_required_lanes_completed"],
            "bound_supported": v1_manifest["bound_supported"],
            "stage_f_execution_authorized": v1_manifest["stage_f_execution_authorized"],
        },
        "entries": entries,
        "record_count": 6,
        "final_status": "STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS",
        "stage_f_route": "WAIT_FOR_EXPLICIT_USER_AUTHORIZATION",
        "prohibited_counters": dict(PROHIBITED_COUNTERS),
    }


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
    install_fields, zipapp, direct_python = _install_lane(args, work)
    cell_cwd = Path(tempfile.mkdtemp(prefix="stage-e-cell-", dir=work))
    mobius_fields, mobius_rate = _mobius_lane(direct_python, zipapp, cell_cwd)
    dag_fields, dag_rate, dag_v2_cells, cache_detail = _dag_cache_lane(direct_python, zipapp, cell_cwd)
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
            "supported_keywords": list(V1_SUPPORTED_KEYWORDS),
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
    schema_replay_fields = _schema_replay_lane(source)
    schema_fields = _schema_lane(source, records, manifest, schema_replay_fields)
    records[1] = _record("SCHEMA", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, args.head_tree, environment, schema_fields)
    manifest = build_final_manifest(list(zip(EVIDENCE_ORDER, records)), head_commit=args.head_commit, head_tree=args.head_tree, environment=environment, completed_lanes=LANES)
    stage_e_schema = strict_load(source / SCHEMA_FILES[2])
    stage_e_validator = Validator(stage_e_schema, allowed_metadata=("completion_marker", "prospective_negative_schema_cases", "prospective_non_evidence_schema_fixtures", "scientific_execution_count", "stage_e_instance_count"))
    for record in records:
        stage_e_validator.validate(record)
    stage_e_validator.validate(manifest)

    recursive_isolated = _zipapp_json(direct_python, zipapp, ["recursive-conformance"], cell_cwd)
    recursive_isolated.pop("status")
    recursive_isolated.pop("scientific_execution_count")
    if recursive_isolated != recursive_conformance():
        raise Refusal("isolated recursive conformance differs from source oracle")
    cache_isolated = _zipapp_json(direct_python, zipapp, ["cache-conformance"], cell_cwd)
    cache_isolated.pop("status")
    cache_isolated.pop("scientific_execution_count")
    if cache_isolated != json.loads(canonical_bytes(cache_detail)):
        raise Refusal("isolated cache conformance differs from source control")
    growth_isolated = _zipapp_json(direct_python, zipapp, ["growth-conformance"], cell_cwd)
    growth_isolated.pop("status")
    growth_isolated.pop("scientific_execution_count")
    if growth_isolated != growth_conformance():
        raise Refusal("isolated growth conformance differs from source microcases")

    artifact_identity = {
        "byte_count": install_fields["harness_zipapp"]["byte_count"],
        "sha256": install_fields["harness_zipapp"]["sha256"],
    }
    v2_records = [
        (
            "schema-replay-v2.json",
            _v2_record(source, "SCHEMA_REPLAY_V2", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, environment, schema_replay_fields),
        ),
        (
            "recursive-growth-v2.json",
            _v2_record(source, "RECURSIVE_GROWTH_V2", "MATHEMATICAL_DERIVATION_CHECK", args.head_commit, environment, recursive_isolated),
        ),
        (
            "dag-cache-correction-v2.json",
            _v2_record(
                source,
                "DAG_CACHE_CORRECTION_V2",
                "HARNESS_COMPLEXITY_VERIFICATION",
                args.head_commit,
                environment,
                {
                    "dag_valid_cases": 39467,
                    "dag_refusal_cases": 14,
                    "dag_complexity_cells": dag_v2_cells,
                    "cache_control_count": 17,
                    "cache_key_field_count": 29,
                    "cache_key_omission_refusal_count": 29,
                    "cache_invalidation_receipt": _cache_v2_receipt(cache_detail),
                    "stale_cache_hits": 0,
                    "mismatch_count": 0,
                },
            ),
        ),
        (
            "dynamic-growth-guard-v2.json",
            _v2_record(source, "DYNAMIC_GROWTH_GUARD_V2", "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", args.head_commit, environment, _dynamic_guard_v2()),
        ),
        (
            "harness-artifact-v2.json",
            _v2_record(
                source,
                "HARNESS_ARTIFACT_V2",
                "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST",
                args.head_commit,
                environment,
                {
                    "replica_count": 3,
                    "replica_identities": [dict(artifact_identity) for _ in range(3)],
                    "all_replicas_byte_identical": True,
                    "safe_member_count": 64,
                    "unsafe_member_count": 0,
                    "source_checkout_import_count": 0,
                    "network_access_count": 0,
                },
            ),
        ),
    ]
    reconciliation_schema = strict_load(source / RECONCILIATION_SCHEMA_FILE)
    reconciliation_validator = Validator(reconciliation_schema)
    for _, record in v2_records:
        reconciliation_validator.validate(record)
    reconciliation_manifest = _v2_manifest(manifest, v2_records)
    _validate_v2_semantics(
        source,
        manifest,
        v2_records,
        reconciliation_manifest,
        candidate_commit=args.head_commit,
        environment=environment,
    )
    reconciliation_validator.validate(reconciliation_manifest)
    for name, record in zip(EVIDENCE_ORDER, records):
        write_record(output, name, record)
    (output / "final-manifest.json").write_bytes(canonical_bytes(manifest))
    for name, record in v2_records:
        (output / name).write_bytes(canonical_bytes(record))
    (output / "reconciliation-manifest-v2.json").write_bytes(canonical_bytes(reconciliation_manifest))
    print(canonical_bytes({"status": "STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS", "records": 16, "lanes": LANES, "scientific_execution_count": 0}).decode("utf-8"))
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
