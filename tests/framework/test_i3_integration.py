"""Complete deterministic T0 integration checks for the frozen I-3 authority."""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import fields, is_dataclass
from enum import StrEnum
import hashlib
import inspect
import json
from pathlib import Path
import re
from typing import get_args
import unittest

import ebu_framework as framework
import ebu_framework.actions as actions_module
import ebu_framework.artifacts as artifacts_module
import ebu_framework.causal as causal_module
import ebu_framework.commitments as commitments_module
import ebu_framework.conservation as conservation_module
import ebu_framework.distortion as distortion_module
import ebu_framework.experiment as experiment_module
import ebu_framework.faults as faults_module
import ebu_framework.ledger as ledger_module
import ebu_framework.network as network_module
import ebu_framework.observation as observation_module
import ebu_framework.policy as policy_module
import ebu_framework.scheduling as scheduling_module
import ebu_framework.settlement as settlement_module
import ebu_framework.state as state_module
from ebu_framework.canonical import parse_ecj1
from ebu_framework.errors import FailureCode, FrameworkError


_REPO_ROOT = Path(__file__).resolve().parents[2]
_ROOT_PATH = _REPO_ROOT / "src/ebu_framework/__init__.py"
_MECHANICAL_PATH = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_PATH = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_FIXTURE_PATH = _REPO_ROOT / "tests/framework/fixtures/i3_validation_v1.json"
_I4_MECHANICAL_PATH = _REPO_ROOT / "unified_python_research_framework_i4_contract.json"
_D2_MECHANICAL_PATH = _REPO_ROOT / "atomic_interaction_declaration_contract.json"

_MODULES = {
    "state": state_module,
    "conservation": conservation_module,
    "distortion": distortion_module,
    "actions": actions_module,
    "network": network_module,
    "commitments": commitments_module,
    "observation": observation_module,
    "scheduling": scheduling_module,
    "policy": policy_module,
    "causal": causal_module,
    "settlement": settlement_module,
    "ledger": ledger_module,
    "faults": faults_module,
    "experiment": experiment_module,
    "artifacts": artifacts_module,
}
_MODULE_NAMES = frozenset(f"ebu_framework.{name}" for name in _MODULES)
_PRODUCTION_PATHS = {
    name: _REPO_ROOT / f"src/ebu_framework/{name}.py" for name in _MODULES
}
_FORMATION_HELPERS = {
    name: module._formation_failure for name, module in _MODULES.items()
}
_DERIVED_EXCLUSIONS = {
    "SystemState": {"state_payload_hash"},
    "RepresentedState": {"represented_state_projection_hash"},
    "InformationView": {"information_view_hash"},
    "PolicyMemoryState": {"policy_memory_payload_hash"},
    "ExecutionBinding": {"execution_semantics_hash"},
}

_MECHANICAL_RAW_SHA256 = (
    "d8acef250314e1405b048a324c9f855010f7927cc8760e2f827bba85253d7979"
)
_MECHANICAL_CANONICAL_SHA256 = (
    "384f289fbd20524d193eed9d852334915bf41b8b18b5096f1b7fb8ca9788a534"
)
_VALIDATION_RAW_SHA256 = (
    "9ecd849f24ecd3e55883874263c10c181fea2e16a3000e87e4fc7fe02c2ccb2b"
)
_VALIDATION_CANONICAL_SHA256 = (
    "ba70b9915ebc5957225adc3f4806d89a540bec86560a29d63471613af2659079"
)
_FIXTURE_BYTE_COUNT = 24_179_582
_FIXTURE_SHA256 = (
    "e5790524bb7d63dcc18e15cd933d801c225253230f09b06d9828a703fc6218c5"
)
_COMPONENT_SHA256 = {
    "ids": "af04f10d692e4ffac66f5af1f3585d3dbaf6ace99417b683f0469c53e0238f85",
    "names": "31e566fd4f9dc5dd472944a8cdec25c87cf3bc04880822fca9003bdda1b5e5eb",
    "effective_inputs": (
        "cbcbe59249e866cd4a9d8eec74094fed4c506ac30d46ff2b106d02a1576dc596"
    ),
    "outcomes": (
        "5c6da4ad3fa3498db5a0c633e5ad889f18df621cf6b60d5ece9c9ca1883ed25b"
    ),
    "failure_ids": (
        "af857c4d3c73ca897dbac82c588b8558e8f40746e0059bbdcb582a475733c999"
    ),
    "successful_projections": (
        "a6d463d310f6289721531e2dfef0ef7944ee242eb5f9f245bbc47decbac90a7d"
    ),
    "predicate_truth_sets": (
        "8812d40f5eb8f79722cf6aefe2df0eff7adae0494415ec146b3e9ab950be9f89"
    ),
}
_FAILURE_FIELDS = {
    "canonical_trace_state",
    "durability_state",
    "event_key",
    "evidence_refs",
    "failure_code",
    "failure_id",
    "failure_ordinal",
    "human_summary",
    "interface_ref",
    "object_refs",
    "policy_memory_advance",
    "retry_class",
    "schema_id",
    "scientific_status_effect",
    "stage",
    "state_advance",
}


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON name: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _strict_load(path: Path, expected_type: type) -> tuple[bytes, object]:
    payload = path.read_bytes()
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in payload
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    text = payload.decode("utf-8", "strict")
    decoder = json.JSONDecoder(
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    value, end = decoder.raw_decode(text)
    assert not text[end:].strip()
    assert type(value) is expected_type
    return payload, value


def _canonical_bytes(value: object, *, final_lf: bool = False) -> bytes:
    suffix = "\n" if final_lf else ""
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + suffix
    ).encode("utf-8", "strict")


def _recursive_canonical_bytes(value: object) -> bytes:
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if type(value) is int:
        return str(value).encode("ascii")
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False).encode("utf-8", "strict")
    if type(value) is list:
        return b"[" + b",".join(_recursive_canonical_bytes(item) for item in value) + b"]"
    if type(value) is dict:
        members = []
        for key in sorted(value):
            assert type(key) is str
            members.append(
                _recursive_canonical_bytes(key)
                + b":"
                + _recursive_canonical_bytes(value[key])
            )
        return b"{" + b",".join(members) + b"}"
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")


def _digest_subject(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _direct_relative_imports(tree: ast.Module) -> list[str]:
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            if node.module is not None:
                imports.append(node.module)
            else:
                imports.extend(alias.name for alias in node.names)
    return imports


def _root_imports(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    result: dict[str, tuple[str, ...]] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module in _MODULES
        ):
            assert node.module not in result
            assert all(alias.name != "*" and alias.asname is None for alias in node.names)
            result[node.module] = tuple(alias.name for alias in node.names)
    return result


def _construct(descriptor: dict[str, object]) -> object:
    runtime_type = descriptor["runtime_type"]
    assert type(runtime_type) is str
    if runtime_type == "CanonicalBytes":
        utf8_hex = descriptor["utf8_hex"]
        assert type(utf8_hex) is str
        return bytes.fromhex(utf8_hex)
    if runtime_type == "tuple":
        members = descriptor["members"]
        assert type(members) is list
        return tuple(_construct(member) for member in members)
    if runtime_type in {"str", "bool", "int"}:
        value = descriptor["value"]
        assert type(value).__name__ == runtime_type
        return value

    runtime_class = getattr(framework, runtime_type)
    if isinstance(runtime_class, type) and issubclass(runtime_class, StrEnum):
        return runtime_class(descriptor["value"])
    if "constructor_arguments" not in descriptor:
        return runtime_class(value=descriptor["value"])

    constructor_arguments = descriptor["constructor_arguments"]
    assert type(constructor_arguments) is list
    keyword_arguments = {
        argument[0]: _construct(argument[2]) for argument in constructor_arguments
    }
    return runtime_class(**keyword_arguments)


def _assert_descriptor_runtime(
    value: object,
    descriptor: dict[str, object],
    vector_id: str,
) -> None:
    runtime_type = descriptor["runtime_type"]
    assert type(runtime_type) is str
    if runtime_type == "CanonicalBytes":
        assert type(value) is bytes, vector_id
        assert value.hex() == descriptor["utf8_hex"], vector_id
        return
    if runtime_type == "tuple":
        assert type(value) is tuple, vector_id
        members = descriptor["members"]
        assert type(members) is list
        assert len(value) == len(members), vector_id
        for actual_member, member_descriptor in zip(value, members, strict=True):
            _assert_descriptor_runtime(actual_member, member_descriptor, vector_id)
        return
    if runtime_type in {"str", "bool", "int"}:
        assert type(value).__name__ == runtime_type, vector_id
        assert value == descriptor["value"], vector_id
        return

    runtime_class = getattr(framework, runtime_type)
    assert type(value) is runtime_class, vector_id
    constructor_arguments = descriptor.get("constructor_arguments")
    if type(constructor_arguments) is list:
        for argument in constructor_arguments:
            field_name = argument[0]
            assert type(field_name) is str
            _assert_descriptor_runtime(
                getattr(value, field_name),
                argument[2],
                vector_id,
            )


def _project(value: object) -> object:
    if type(value) is bytes:
        return parse_ecj1(value)
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is tuple:
        return [_project(member) for member in value]
    value_type = type(value)
    if (
        value_type.__module__ == "ebu_framework.identity"
        and is_dataclass(value_type)
        and tuple(field.name for field in fields(value_type)) == ("value",)
    ):
        return str(value)
    if value_type.__module__ in _MODULE_NAMES and is_dataclass(value_type):
        excluded = {"envelope"} | _DERIVED_EXCLUSIONS.get(
            value_type.__name__, set()
        )
        return {
            field.name: _project(getattr(value, field.name))
            for field in fields(value)
            if field.name not in excluded
        }
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()
    return value


def _form_value(
    type_entries: dict[str, list[object]],
    module: str,
    qualname: str,
    descriptor: dict[str, object],
) -> object:
    value = _construct(descriptor)
    entry = type_entries[qualname]
    runtime_kind = entry[2]
    if runtime_kind == "TAGGED_UNION":
        accepted_types = get_args(getattr(framework, qualname))
        if type(value) not in accepted_types:
            _FORMATION_HELPERS[module.removeprefix("ebu_framework.")](qualname)
    elif type(value) is not getattr(framework, qualname):
        _FORMATION_HELPERS[module.removeprefix("ebu_framework.")](qualname)
    return value


def _capture_framework_error(callable_value: object) -> FrameworkError:
    try:
        callable_value()
    except FrameworkError as error:
        return error
    raise AssertionError("expected FrameworkError")


def _frame(value: str) -> bytes:
    encoded = value.encode("utf-8", "strict")
    return len(encoded).to_bytes(8, "big") + encoded


def _independent_failure_id(envelope: dict[str, object]) -> str:
    parts = [
        _frame("ebu.failure-id.v1"),
        _frame(envelope["failure_code"]),
        _frame(envelope["stage"]),
    ]
    interface = envelope["interface_ref"]
    if type(interface) is dict:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(interface["module"]),
                _frame(interface["qualname"]),
                _frame(interface["interface_version"]),
            )
        )
    else:
        assert interface == "NOT_APPLICABLE"
        parts.append(_frame("NOT_APPLICABLE"))
    object_refs = envelope["object_refs"]
    assert type(object_refs) is list
    parts.append(len(object_refs).to_bytes(8, "big"))
    for reference in object_refs:
        assert type(reference) is dict
        parts.extend(
            (
                _frame(reference["object_id"]),
                _frame(reference["object_version"]),
                _frame(reference["object_content_hash"]),
            )
        )
    event_key = envelope["event_key"]
    if type(event_key) is dict:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(str(event_key["epoch"])),
                _frame(str(event_key["phase_ordinal"])),
                _frame(str(event_key["declared_priority"])),
                _frame(event_key["group_or_scope_id"]),
                _frame(event_key["event_kind"]),
                _frame(event_key["primary_object_id"]),
                _frame(str(event_key["local_sequence"])),
            )
        )
    else:
        assert event_key == "NOT_APPLICABLE"
        parts.append(_frame("NOT_APPLICABLE"))
    parts.append(_frame(str(envelope["failure_ordinal"])))
    digest = hashlib.sha256(b"".join(parts)).hexdigest()
    return f"ebu:failure:core:sha256-{digest}"


def _record_ref_projection(record: object) -> dict[str, str]:
    envelope = record.envelope
    return {
        "object_content_hash": str(envelope.object_content_hash),
        "object_id": str(envelope.object_id),
        "object_version": str(envelope.object_version),
    }


def _scanned_records(
    scan_row: dict[str, object], arguments: list[object]
) -> list[object]:
    result: list[object] = []
    inspect_rows = scan_row["inspect"]
    assert type(inspect_rows) is list
    for item in inspect_rows:
        assert type(item) is str
        match = re.match(r"argument (\d+)", item)
        assert match is not None
        value = arguments[int(match.group(1)) - 1]
        if "[*]" in item:
            assert type(value) is tuple
            result.extend(value)
        elif hasattr(value, "envelope"):
            result.append(value)
    return result


def _assert_failure(
    error: FrameworkError,
    expected: dict[str, object],
    vector_id: str,
) -> None:
    actual = error.envelope.to_ecj1()
    assert set(actual) == _FAILURE_FIELDS
    assert len(actual) == 16
    assert actual == expected["failure_envelope_projection"], vector_id
    assert actual["failure_code"] == expected["failure_code"], vector_id
    assert actual["stage"] == expected["stage"] == "I-3", vector_id
    assert actual["failure_ordinal"] == expected["failure_ordinal"], vector_id
    assert actual["interface_ref"] == expected["interface_ref"], vector_id
    assert actual["object_refs"] == expected["object_refs"], vector_id
    assert actual["event_key"] == expected["event_key"], vector_id
    assert actual["state_advance"] == expected["state_advance"], vector_id
    assert actual["policy_memory_advance"] == expected["policy_memory_advance"], vector_id
    assert actual["canonical_trace_state"] == expected["canonical_trace_state"], vector_id
    assert actual["durability_state"] == expected["durability_state"], vector_id
    assert actual["retry_class"] == expected["retry_class"], vector_id
    assert actual["scientific_status_effect"] == expected[
        "scientific_status_effect"
    ], vector_id
    independent = _independent_failure_id(actual)
    assert independent == expected["failure_id"], vector_id
    assert actual["failure_id"] == {"value": independent}, vector_id


class I3IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mechanical_raw, mechanical = _strict_load(_MECHANICAL_PATH, dict)
        validation_raw, validation = _strict_load(_VALIDATION_PATH, dict)
        fixture_raw, fixture = _strict_load(_FIXTURE_PATH, list)
        cls.mechanical_raw = mechanical_raw
        cls.mechanical = mechanical
        cls.validation_raw = validation_raw
        cls.validation = validation
        cls.fixture_raw = fixture_raw
        cls.vectors = fixture

    def test_root_api_modules_import_graph_and_failure_inventory(self) -> None:
        mechanical = self.mechanical
        self.assertEqual(hashlib.sha256(self.mechanical_raw).hexdigest(), _MECHANICAL_RAW_SHA256)
        self.assertEqual(
            hashlib.sha256(_canonical_bytes(mechanical, final_lf=True)).hexdigest(),
            _MECHANICAL_CANONICAL_SHA256,
        )
        self.assertEqual(hashlib.sha256(self.validation_raw).hexdigest(), _VALIDATION_RAW_SHA256)
        self.assertEqual(
            hashlib.sha256(
                _canonical_bytes(self.validation, final_lf=True)
            ).hexdigest(),
            _VALIDATION_CANONICAL_SHA256,
        )

        root_exports = tuple(framework.__all__)
        prefix = root_exports[:127]
        suffix_types = tuple(mechanical["root_export_suffix_types"])
        suffix_callables = tuple(mechanical["root_export_suffix_callables"])
        suffix = suffix_types + suffix_callables
        _, i4_mechanical = _strict_load(_I4_MECHANICAL_PATH, dict)
        _, d2_mechanical = _strict_load(_D2_MECHANICAL_PATH, dict)
        d2_surface = d2_mechanical["proposed_surface"]
        d1_suffix = root_exports[219:237]
        d2_suffix = root_exports[237:261]
        i4_suffix = tuple(i4_mechanical["root_export_suffix_types"]) + tuple(
            i4_mechanical["root_export_suffix_callables"]
        )
        self.assertEqual(len(prefix), mechanical["accepted_root_prefix_count"])
        self.assertEqual(
            hashlib.sha256(
                b"".join(name.encode("utf-8") + b"\n" for name in prefix)
            ).hexdigest(),
            mechanical["accepted_root_prefix_lf_sha256"],
        )
        self.assertEqual(root_exports[127:219], suffix)
        self.assertEqual(
            d1_suffix, tuple(d2_surface["d1_root_export_suffix"])
        )
        self.assertEqual(
            d2_suffix, tuple(d2_surface["d2_root_export_suffix"])
        )
        self.assertEqual(root_exports[261:], i4_suffix)
        root_rule = i4_mechanical["root_export_rule"]
        for names, byte_key, digest_key in (
            (d1_suffix, "accepted_d1_suffix_lf_byte_count", "accepted_d1_suffix_lf_sha256"),
            (d2_suffix, "accepted_d2_suffix_lf_byte_count", "accepted_d2_suffix_lf_sha256"),
            (i4_suffix, "i4_suffix_lf_byte_count", "i4_suffix_lf_sha256"),
            (root_exports, "post_i4_lf_byte_count", "post_i4_lf_sha256"),
        ):
            projection = b"".join(name.encode("utf-8") + b"\n" for name in names)
            self.assertEqual(len(projection), root_rule[byte_key])
            self.assertEqual(hashlib.sha256(projection).hexdigest(), root_rule[digest_key])
        self.assertEqual(len(suffix_types), 69)
        self.assertEqual(len(suffix_callables), 23)
        self.assertEqual(len(root_exports[:219]), mechanical["post_i3_root_export_count"])
        self.assertEqual(len(root_exports), 309)
        self.assertEqual(len(root_exports), len(set(root_exports)))
        self.assertTrue(all(not name.startswith("_") for name in suffix))
        self.assertEqual(framework.__version__, "0.1.0a1")
        self.assertFalse(
            set(suffix) & {row[0] for row in mechanical["deferred_types"]}
        )
        self.assertFalse(
            set(suffix) & {row[0] for row in mechanical["deferred_callables"]}
        )

        root_source = _ROOT_PATH.read_text(encoding="utf-8", errors="strict")
        root_tree = ast.parse(root_source, filename=str(_ROOT_PATH))
        compile(root_tree, str(_ROOT_PATH), "exec", dont_inherit=True)
        self.assertEqual(
            _root_imports(root_tree),
            {
                name: tuple(exports)
                for name, exports in mechanical["module_exports"].items()
            },
        )
        for module_name, names in mechanical["module_exports"].items():
            module = _MODULES[module_name]
            self.assertEqual(tuple(module.__all__), tuple(names))
            for name in names:
                self.assertIs(getattr(framework, name), getattr(module, name))

        types = mechanical["types"]
        self.assertEqual(len(types), 69)
        for entry in types:
            name, module_name, runtime_kind, members_or_fields = entry[:4]
            runtime_value = getattr(_MODULES[module_name], name)
            if runtime_kind == "FROZEN_DATACLASS":
                self.assertTrue(is_dataclass(runtime_value))
                self.assertTrue(runtime_value.__dataclass_params__.frozen)
                expected_fields = tuple(row[0] for row in members_or_fields)
                self.assertEqual(tuple(field.name for field in fields(runtime_value)), expected_fields)
                self.assertEqual(tuple(runtime_value.__slots__), expected_fields)
            elif runtime_kind == "STRENUM":
                self.assertTrue(issubclass(runtime_value, StrEnum))
                self.assertEqual(tuple(runtime_value.__members__), tuple(members_or_fields))
                self.assertEqual(tuple(member.value for member in runtime_value), tuple(members_or_fields))
            else:
                self.assertEqual(runtime_kind, "TAGGED_UNION")
                self.assertEqual(
                    tuple(value.__name__ for value in get_args(runtime_value)),
                    ("ExactResidualExpectation", "UncertaintyAwareResidualExpectation"),
                )

        validators = mechanical["validators"]
        self.assertEqual(len(validators), 23)
        for validator in validators:
            runtime_validator = getattr(framework, validator["name"])
            signature = inspect.signature(runtime_validator)
            self.assertEqual(list(signature.parameters), validator["argument_order"])
            self.assertTrue(
                all(
                    parameter.kind is inspect.Parameter.POSITIONAL_ONLY
                    for parameter in signature.parameters.values()
                )
            )
            self.assertIn(signature.return_annotation, (None, "None"))

        dependency_graph: dict[str, tuple[str, ...]] = {}
        forbidden_calls = {
            "accept_experiment_configuration",
            "accept_execution_binding",
            "allocate_scientific_id",
            "allocate_settlement",
            "append_operational_ledger_entry",
            "append_scientific_ledger_entry",
            "deliver_declared_fault",
            "finalize_execution_result_manifest",
            "infer_causal_contributions",
            "measure_state",
            "policy_propose",
            "project_state",
            "publish_artifacts",
            "register_draft",
            "resolve_alias",
            "resolve_ref",
        }
        forbidden_import_roots = {
            "importlib",
            "multiprocessing",
            "os",
            "pkgutil",
            "random",
            "runpy",
            "secrets",
            "socket",
            "subprocess",
        }
        for module_name, path in _PRODUCTION_PATHS.items():
            raw = path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\r", raw)
            self.assertTrue(raw.endswith(b"\n") and not raw.endswith(b"\n\n"))
            source = raw.decode("utf-8", "strict")
            folded = source.casefold()
            self.assertNotIn("i3v-", folded)
            self.assertNotIn("i3_validation_v1", folded)
            self.assertNotIn("operational_durability_event", folded)
            tree = ast.parse(source, filename=str(path))
            compile(tree, str(path), "exec", dont_inherit=True)
            imports = tuple(_direct_relative_imports(tree))
            self.assertEqual(imports, tuple(mechanical["direct_imports"][module_name]))
            dependency_graph[module_name] = imports
            self.assertFalse(
                any(
                    isinstance(node, ast.ImportFrom)
                    and any(alias.name == "*" for alias in node.names)
                    for node in ast.walk(tree)
                )
            )
            imported_roots = {
                alias.name.split(".", 1)[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            called_names = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            called_attributes = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            self.assertTrue(imported_roots.isdisjoint(forbidden_import_roots))
            self.assertTrue(called_names.isdisjoint(forbidden_calls))
            self.assertTrue(called_attributes.isdisjoint({"import_module", "Popen", "run"}))

        self.assertEqual(len(dependency_graph), 15)
        self.assertEqual(sum(map(len, dependency_graph.values())), 91)
        visited: set[str] = set()
        active: set[str] = set()

        def visit(module_name: str) -> None:
            if module_name in visited:
                return
            self.assertNotIn(module_name, active)
            active.add(module_name)
            for dependency in dependency_graph[module_name]:
                if dependency in dependency_graph:
                    visit(dependency)
            active.remove(module_name)
            visited.add(module_name)

        for module_name in dependency_graph:
            visit(module_name)
        self.assertEqual(visited, set(dependency_graph))

        manifest = mechanical["future_implementation_manifest"]
        self.assertEqual(len(manifest), 23)
        manifest_paths = [row[1] for row in manifest]
        self.assertEqual(len(manifest_paths), len(set(manifest_paths)))
        self.assertTrue(all((_REPO_ROOT / path).exists() for path in manifest_paths))
        inventories = mechanical["substage_path_inventories"]
        self.assertEqual(
            {row["substage"]: row["path_count"] for row in inventories},
            {"I-3A": 5, "I-3B": 6, "I-3C": 5, "I-3D": 4, "I-3E": 3},
        )
        for inventory in inventories:
            owned = [row[1] for row in manifest if row[3] == inventory["substage"]]
            declared = (
                inventory["module_paths"]
                + inventory["fixture_paths"]
                + inventory["test_paths"]
            )
            self.assertEqual(owned, declared)

        compatibility = mechanical["failure_code_regression_compatibility"]
        historical = tuple(compatibility["historical_prefix"])
        i3_suffix = tuple(mechanical["failure_append_order"])
        complete = historical + i3_suffix
        failure_values = tuple(code.value for code in FailureCode)
        i4_failures = tuple(i4_mechanical["failure_append_order"])
        d2_failures = d2_mechanical["failure_contract"]
        self.assertEqual(failure_values[:53], historical)
        self.assertEqual(failure_values[53:88], i3_suffix)
        self.assertEqual(
            failure_values[88:102], tuple(d2_failures["d1_append_order"])
        )
        self.assertEqual(
            failure_values[102:124], tuple(d2_failures["d2_append_order"])
        )
        self.assertEqual(failure_values[124:], i4_failures)
        failure_rule = i4_mechanical["failure_rule"]
        for names, byte_key, digest_key in (
            (failure_values[88:102], "accepted_d1_suffix_lf_byte_count", "accepted_d1_suffix_lf_sha256"),
            (failure_values[102:124], "accepted_d2_suffix_lf_byte_count", "accepted_d2_suffix_lf_sha256"),
            (failure_values[124:], "suffix_lf_byte_count", "suffix_lf_sha256"),
            (failure_values, "resulting_inventory_lf_byte_count", "resulting_inventory_lf_sha256"),
        ):
            projection = b"".join(name.encode("ascii") + b"\n" for name in names)
            self.assertEqual(len(projection), failure_rule[byte_key])
            self.assertEqual(hashlib.sha256(projection).hexdigest(), failure_rule[digest_key])
        self.assertEqual((len(historical), len(i3_suffix), len(complete)), (53, 35, 88))
        for names, expected_bytes, expected_digest in (
            (
                historical,
                compatibility["historical_prefix_lf_byte_count"],
                "94b7d2b611f0d15b68ba296dec2156cf0bbdbd7dac97a534a157286386fdb7be",
            ),
            (
                i3_suffix,
                compatibility["accepted_i3a_suffix_lf_byte_count"],
                "0a65b1995b6ed86ba68266cc9bcaac48f2662fae2e1a60cd7672137d40cbcb2c",
            ),
            (
                complete,
                compatibility["current_inventory_lf_byte_count"],
                "0a9e0c22d74d0a1891af19546422296881d2fa6ba16319238def55578c9706d3",
            ),
        ):
            payload = b"".join(name.encode("ascii") + b"\n" for name in names)
            self.assertEqual(len(payload), expected_bytes)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected_digest)

    def test_complete_fixture_structure_identities_and_contract_coverage(self) -> None:
        vectors = self.vectors
        mechanical = self.mechanical
        validation = self.validation
        self.assertEqual(vectors, validation["vectors"])
        self.assertEqual(len(vectors), 544)
        self.assertEqual(len(self.fixture_raw), _FIXTURE_BYTE_COUNT)
        self.assertEqual(hashlib.sha256(self.fixture_raw).hexdigest(), _FIXTURE_SHA256)
        self.assertEqual(_canonical_bytes(vectors, final_lf=True), self.fixture_raw)
        self.assertEqual(_recursive_canonical_bytes(vectors) + b"\n", self.fixture_raw)
        self.assertEqual(self.fixture_raw.count(b"OPERATIONAL_DURABILITY_EVENT"), 0)

        component_subjects = {
            "ids": [vector["vector_id"] for vector in vectors],
            "names": [vector["name"] for vector in vectors],
            "effective_inputs": [
                vector["materialized_effective_input"] for vector in vectors
            ],
            "outcomes": [vector["expected"] for vector in vectors],
            "failure_ids": [
                vector["expected"]["failure_id"]
                for vector in vectors
                if vector["expected"]["kind"] == "FAILURE"
            ],
            "successful_projections": [
                vector["expected"]["successful_projection"]
                for vector in vectors
                if vector["expected"]["kind"] == "SUCCESS"
            ],
            "predicate_truth_sets": [
                [
                    vector["vector_id"],
                    vector["precedence_evidence"]["active_failure_codes"],
                ]
                for vector in vectors
            ],
        }
        self.assertEqual(
            {name: _digest_subject(subject) for name, subject in component_subjects.items()},
            _COMPONENT_SHA256,
        )

        category_counts = Counter(vector["category"] for vector in vectors)
        self.assertEqual(
            category_counts,
            {
                "FORMATION_POSITIVE": 69,
                "FORMATION_BOUNDARY": 69,
                "FORMATION_NEGATIVE": 69,
                "VALIDATOR_POSITIVE": 23,
                "VALIDATOR_BOUNDARY": 23,
                "ISOLATED_SINGLE_FAILURE": 145,
                "ADJACENT_PRECEDENCE_PAIR": 122,
                "MULTIPLY_INVALID_ALL_PRECEDENCE": 23,
                "OBJECT_CONTENT_SCAN_ORDER": 1,
            },
        )
        self.assertEqual(
            Counter(vector["expected"]["kind"] for vector in vectors),
            {"SUCCESS": 184, "FAILURE": 360},
        )

        cursor = 0
        for type_entry in mechanical["types"]:
            name, module_name = type_entry[:2]
            group = vectors[cursor : cursor + 3]
            self.assertEqual(
                [vector["category"] for vector in group],
                ["FORMATION_POSITIVE", "FORMATION_BOUNDARY", "FORMATION_NEGATIVE"],
            )
            for vector in group:
                self.assertEqual(
                    vector["expected_interface"],
                    {
                        "module": f"ebu_framework.{module_name}",
                        "qualname": name,
                        "interface_version": "1.0.0",
                    },
                )
                self.assertEqual(
                    vector["precedence_evidence"]["full_precedence"],
                    ["I3_RECORD_FORMATION_INVALID"],
                )
            self.assertEqual(group[0]["precedence_evidence"]["active_failure_codes"], [])
            self.assertEqual(group[1]["precedence_evidence"]["active_failure_codes"], [])
            self.assertEqual(
                group[2]["precedence_evidence"]["active_failure_codes"],
                ["I3_RECORD_FORMATION_INVALID"],
            )
            cursor += 3
        self.assertEqual(cursor, 207)

        for validator in mechanical["validators"]:
            precedence = validator["precedence"]
            group_count = 2 + len(precedence) + len(precedence) - 1 + 1
            if validator["name"] == "validate_provider_network":
                group_count += 1
            group = vectors[cursor : cursor + group_count]
            self.assertTrue(
                all(
                    vector["expected_interface"]
                    == {
                        "module": f"ebu_framework.{validator['module']}",
                        "qualname": validator["name"],
                        "interface_version": "1.0.0",
                    }
                    for vector in group
                )
            )
            self.assertTrue(
                all(
                    vector["precedence_evidence"]["full_precedence"] == precedence
                    for vector in group
                )
            )
            self.assertEqual(
                [group[0]["category"], group[1]["category"]],
                ["VALIDATOR_POSITIVE", "VALIDATOR_BOUNDARY"],
            )
            self.assertEqual(group[0]["precedence_evidence"]["active_failure_codes"], [])
            self.assertEqual(group[1]["precedence_evidence"]["active_failure_codes"], [])
            isolated = group[2 : 2 + len(precedence)]
            adjacent = group[
                2 + len(precedence) : 2 + len(precedence) + len(precedence) - 1
            ]
            multiply = group[2 + len(precedence) + len(precedence) - 1]
            self.assertEqual(
                [vector["precedence_evidence"]["active_failure_codes"] for vector in isolated],
                [[failure] for failure in precedence],
            )
            self.assertEqual(
                [vector["precedence_evidence"]["active_failure_codes"] for vector in adjacent],
                [precedence[index : index + 2] for index in range(len(precedence) - 1)],
            )
            self.assertEqual(
                multiply["precedence_evidence"]["active_failure_codes"], precedence
            )
            self.assertEqual(multiply["category"], "MULTIPLY_INVALID_ALL_PRECEDENCE")
            if validator["name"] == "validate_provider_network":
                scan = group[-1]
                self.assertEqual(scan["category"], "OBJECT_CONTENT_SCAN_ORDER")
                self.assertEqual(
                    scan["precedence_evidence"]["active_failure_codes"],
                    ["I3_OBJECT_CONTENT_MISMATCH"],
                )
            cursor += group_count
        self.assertEqual(cursor, 544)

        self.assertEqual(len(mechanical["collection_contracts"]), 133)
        self.assertEqual(len(mechanical["applicability_contracts"]), 43)
        self.assertEqual(len(mechanical["sum_type_contracts"]), 2)
        self.assertEqual(len(mechanical["object_content_scan_orders"]), 23)
        self.assertEqual(len(mechanical["paired_quantity_compatibility_inventory"]), 12)
        conservation = mechanical["conservation_requirement_table"]
        self.assertEqual([row[0] for row in conservation["rows"]], [f"C{i:02d}" for i in range(1, 25)])
        self.assertEqual(
            conservation["level_scan_order"], ["C01", "C02", "C04", "C05", "C14"]
        )
        self.assertEqual(
            conservation["evidence_scan_order"],
            ["C16", "C17", "C18", "C19", "C20", "C21", "C22"],
        )
        self.assertEqual(
            conservation["isolation_scan_order"],
            ["C06", "C07", "C09", "C10", "C11", "C12", "C15", "C23", "C24"],
        )
        self.assertEqual(
            set(mechanical["state_projection_contamination_ownership"]["reserved_direct_keys"]),
            state_module._RESERVED_PHYSICAL_KEYS,
        )
        validator_names = {validator["name"] for validator in mechanical["validators"]}
        self.assertTrue(
            all(row["owner_interface"] in validator_names for row in mechanical["collection_contracts"])
        )
        self.assertTrue(
            all(row["owner_interface"] in validator_names for row in mechanical["applicability_contracts"])
        )
        self.assertTrue(
            all(row["validator"] in validator_names for row in mechanical["paired_quantity_compatibility_inventory"])
        )
        self.assertEqual(sum(len(row["precedence"]) for row in mechanical["validators"]), 145)
        self.assertEqual(sum(len(row["precedence"]) - 1 for row in mechanical["validators"]), 122)

        collision_buckets: dict[bytes, list[dict[str, object]]] = defaultdict(list)
        outcome_by_input: dict[bytes, bytes] = {}
        for vector in vectors:
            effective_key = _canonical_bytes(
                [
                    vector["materialized_effective_input"]["interface"],
                    vector["materialized_effective_input"]["ordered_arguments"],
                ]
            )
            outcome_key = _canonical_bytes(vector["expected"])
            collision_buckets[effective_key].append(vector)
            previous = outcome_by_input.setdefault(effective_key, outcome_key)
            self.assertEqual(previous, outcome_key, vector["vector_id"])
        collisions = [bucket for bucket in collision_buckets.values() if len(bucket) > 1]
        self.assertEqual(len(collision_buckets), 543)
        self.assertEqual(len(collisions), 1)
        self.assertEqual(len(collisions[0]), 2)
        self.assertEqual(
            {vector["category"] for vector in collisions[0]},
            {"FORMATION_POSITIVE", "FORMATION_BOUNDARY"},
        )
        self.assertEqual(
            {vector["expected_interface"]["qualname"] for vector in collisions[0]},
            {"RouteSemanticsStatus"},
        )

    def test_all_544_vectors_execute_once_with_exact_outcomes(self) -> None:
        vectors = self.vectors
        mechanical = self.mechanical
        type_entries = {entry[0]: entry for entry in mechanical["types"]}
        validators = {
            validator["name"]: getattr(framework, validator["name"])
            for validator in mechanical["validators"]
        }
        scan_rows = {
            row["validator"]: row for row in mechanical["object_content_scan_orders"]
        }
        exercised: Counter[str] = Counter()
        success_count = 0
        failure_count = 0
        corrected_reached: set[str] = set()
        corrected = {
            "i3v-20-s05": ["FAULT_SCHEDULE_INVALID"],
            "i3v-20-a04": ["I3_DUPLICATE_MEMBER", "FAULT_SCHEDULE_INVALID"],
            "i3v-20-a05": ["FAULT_SCHEDULE_INVALID", "HASH_MISMATCH"],
            "i3v-20-m": [
                "I3_OBJECT_CONTENT_MISMATCH",
                "IMPLICIT_ABSENCE_FORBIDDEN",
                "I3_COLLECTION_ORDER_INVALID",
                "I3_DUPLICATE_MEMBER",
                "FAULT_SCHEDULE_INVALID",
                "HASH_MISMATCH",
            ],
        }

        for vector in vectors:
            vector_id = vector["vector_id"]
            exercised[vector_id] += 1
            effective_input = vector["materialized_effective_input"]
            interface = effective_input["interface"]
            self.assertEqual(interface, vector["expected_interface"])
            self.assertEqual(vector["expected_stage"], "I-3")
            expected = vector["expected"]
            active_codes = vector["precedence_evidence"]["active_failure_codes"]
            if expected["kind"] == "FAILURE":
                self.assertEqual(active_codes[0], expected["failure_code"], vector_id)
                self.assertEqual(
                    vector["precedence_evidence"]["expected_first_failure"],
                    expected["failure_code"],
                    vector_id,
                )
                self.assertEqual(
                    vector["precedence_evidence"]["expected_first_index"],
                    vector["precedence_evidence"]["full_precedence"].index(
                        expected["failure_code"]
                    ),
                    vector_id,
                )
            else:
                self.assertEqual(active_codes, [], vector_id)

            ordered_arguments = effective_input["ordered_arguments"]
            if vector["category"].startswith("FORMATION_"):
                self.assertEqual(len(ordered_arguments), 1)
                descriptor = ordered_arguments[0]["value"]
                if expected["kind"] == "SUCCESS":
                    value = _form_value(
                        type_entries,
                        interface["module"],
                        interface["qualname"],
                        descriptor,
                    )
                    _assert_descriptor_runtime(value, descriptor, vector_id)
                    projection = _project(value)
                    self.assertEqual(projection, descriptor["ecj1"], vector_id)
                    self.assertEqual(projection, expected["return_value"], vector_id)
                    self.assertEqual(projection, expected["successful_projection"], vector_id)
                    success_count += 1
                else:
                    error = _capture_framework_error(
                        lambda descriptor=descriptor, interface=interface: _form_value(
                            type_entries,
                            interface["module"],
                            interface["qualname"],
                            descriptor,
                        )
                    )
                    _assert_failure(error, expected, vector_id)
                    failure_count += 1
                continue

            arguments: list[object] = []
            for argument in ordered_arguments:
                descriptor = argument["value"]
                value = _construct(descriptor)
                _assert_descriptor_runtime(value, descriptor, vector_id)
                self.assertEqual(_project(value), descriptor["ecj1"], vector_id)
                arguments.append(value)
            if vector_id in corrected:
                self.assertEqual(interface["qualname"], "validate_fault_schedule_boundary")
                self.assertEqual(active_codes, corrected[vector_id])
                corrected_reached.add(vector_id)

            validator = validators[interface["qualname"]]
            if expected["kind"] == "SUCCESS":
                self.assertIs(validator(*arguments), expected["return_value"], vector_id)
                self.assertEqual(
                    [_project(argument) for argument in arguments],
                    expected["successful_projection"],
                    vector_id,
                )
                success_count += 1
            else:
                if expected["failure_code"] == "I3_OBJECT_CONTENT_MISMATCH":
                    scanned = _scanned_records(scan_rows[interface["qualname"]], arguments)
                    mismatches = [
                        record
                        for record in scanned
                        if parse_ecj1(record.envelope.object_content_payload) != _project(record)
                    ]
                    self.assertTrue(mismatches, vector_id)
                    self.assertEqual(
                        expected["object_refs"],
                        [_record_ref_projection(mismatches[0])],
                        vector_id,
                    )
                error = _capture_framework_error(
                    lambda validator=validator, arguments=arguments: validator(*arguments)
                )
                _assert_failure(error, expected, vector_id)
                failure_count += 1

        self.assertEqual(len(exercised), 544)
        self.assertEqual(set(exercised.values()), {1})
        self.assertEqual(success_count, 184)
        self.assertEqual(failure_count, 360)
        self.assertEqual(corrected_reached, set(corrected))
        self.assertEqual(
            sum(
                vector["expected"]["failure_code"] == "I3_OBJECT_CONTENT_MISMATCH"
                for vector in vectors
                if vector["expected"]["kind"] == "FAILURE"
            ),
            67,
        )


if __name__ == "__main__":
    unittest.main()
