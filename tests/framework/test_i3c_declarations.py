"""Deterministic T0 conformance checks for the frozen I-3C authority slice."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import fields, is_dataclass
from enum import StrEnum
import hashlib
import inspect
import json
from pathlib import Path
import unittest

import ebu_framework.causal as causal_module
from ebu_framework.causal import (
    CausalIdentificationStatus,
    CausalRemainder,
    validate_causal_remainder,
)
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import (
    InformationViewHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ScientificId,
    SemanticVersion,
)
import ebu_framework.ledger as ledger_module
from ebu_framework.ledger import Ledger, LedgerEntry, LedgerKind, validate_ledger
from ebu_framework.numeric import IntegerV1
import ebu_framework.policy as policy_module
from ebu_framework.policy import (
    InformationContract,
    InformationReadSet,
    InformationView,
    MemoryMode,
    PolicyMemoryState,
    validate_information_view,
    validate_policy_memory_state,
)
from ebu_framework.primitives import (
    Duration,
    Epoch,
    Instant,
    Quantity,
    ResolutionDetail,
    ResolutionState,
)
import ebu_framework.settlement as settlement_module
from ebu_framework.settlement import (
    ChildActionRecord,
    GroupReceipt,
    GroupResidual,
    Quote,
    Receipt,
    SettlementClosureRecord,
    SettlementShare,
    validate_settlement_closure,
)
from ebu_framework.actions import EffectiveInterval


_REPO_ROOT = Path(__file__).resolve().parents[2]
_MECHANICAL_CONTRACT = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_CONTRACT = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_MODULES = {
    "policy": policy_module,
    "causal": causal_module,
    "settlement": settlement_module,
    "ledger": ledger_module,
}
_MODULE_NAMES = frozenset(f"ebu_framework.{name}" for name in _MODULES)
_PRODUCTION_PATHS = {
    name: _REPO_ROOT / f"src/ebu_framework/{name}.py" for name in _MODULES
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


def _load_contract(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    text = payload.decode("utf-8", "strict")
    decoder = json.JSONDecoder(
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    parsed, end = decoder.raw_decode(text)
    assert not text[end:].strip()
    assert type(parsed) is dict
    return parsed


_RUNTIME_TYPES: dict[str, object] = {
    "Applicability": Applicability,
    "CausalIdentificationStatus": CausalIdentificationStatus,
    "CausalRemainder": CausalRemainder,
    "ChildActionRecord": ChildActionRecord,
    "CommonObjectEnvelope": CommonObjectEnvelope,
    "Duration": Duration,
    "EffectiveInterval": EffectiveInterval,
    "Epoch": Epoch,
    "GroupReceipt": GroupReceipt,
    "GroupResidual": GroupResidual,
    "InformationContract": InformationContract,
    "InformationReadSet": InformationReadSet,
    "InformationView": InformationView,
    "InformationViewHash": InformationViewHash,
    "Instant": Instant,
    "IntegerV1": IntegerV1,
    "Ledger": Ledger,
    "LedgerEntry": LedgerEntry,
    "LedgerKind": LedgerKind,
    "LifecycleStatus": LifecycleStatus,
    "MemoryMode": MemoryMode,
    "ObjectContentHash": ObjectContentHash,
    "ObjectRef": ObjectRef,
    "PolicyMemoryPayloadHash": PolicyMemoryPayloadHash,
    "PolicyMemoryState": PolicyMemoryState,
    "Quantity": Quantity,
    "Quote": Quote,
    "Receipt": Receipt,
    "ResolutionDetail": ResolutionDetail,
    "ResolutionState": ResolutionState,
    "ScientificId": ScientificId,
    "SemanticVersion": SemanticVersion,
    "SettlementClosureRecord": SettlementClosureRecord,
    "SettlementShare": SettlementShare,
}
_ENUM_TYPES = {
    "Applicability",
    "CausalIdentificationStatus",
    "LedgerKind",
    "LifecycleStatus",
    "MemoryMode",
    "ResolutionState",
}
_VALUE_TYPES = {
    "InformationViewHash",
    "ObjectContentHash",
    "PolicyMemoryPayloadHash",
    "ScientificId",
    "SemanticVersion",
}
_FORMATION_HELPERS = {
    "ebu_framework.policy": policy_module._formation_failure,
    "ebu_framework.causal": causal_module._formation_failure,
    "ebu_framework.settlement": settlement_module._formation_failure,
    "ebu_framework.ledger": ledger_module._formation_failure,
}
_VALIDATORS = {
    "validate_information_view": validate_information_view,
    "validate_policy_memory_state": validate_policy_memory_state,
    "validate_causal_remainder": validate_causal_remainder,
    "validate_settlement_closure": validate_settlement_closure,
    "validate_ledger": validate_ledger,
}


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
        return descriptor["value"]

    runtime_class = _RUNTIME_TYPES[runtime_type]
    if runtime_type in _ENUM_TYPES:
        return runtime_class(descriptor["value"])  # type: ignore[operator]
    if runtime_type in _VALUE_TYPES:
        return runtime_class(value=descriptor["value"])  # type: ignore[operator]

    constructor_arguments = descriptor["constructor_arguments"]
    assert type(constructor_arguments) is list
    keyword_arguments = {
        argument[0]: _construct(argument[2]) for argument in constructor_arguments
    }
    return runtime_class(**keyword_arguments)  # type: ignore[operator]


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is tuple:
        return [_project(member) for member in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _form_value(module: str, qualname: str, descriptor: dict[str, object]) -> object:
    value = _construct(descriptor)
    expected_type = _RUNTIME_TYPES[qualname]
    if type(value) is not expected_type:
        _FORMATION_HELPERS[module](qualname)
    return value


def _capture_framework_error(callable_value: object) -> FrameworkError:
    try:
        callable_value()  # type: ignore[operator]
    except FrameworkError as error:
        return error
    raise AssertionError("expected FrameworkError")


def _normalized_annotation(value: str) -> str:
    return "".join(value.replace('"', "'").split())


def _class_annotations(tree: ast.Module) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            result[node.name] = [
                (item.target.id, ast.unparse(item.annotation))
                for item in node.body
                if isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
            ]
    return result


def _direct_relative_imports(tree: ast.Module) -> list[str]:
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            if node.module is not None:
                imports.append(node.module)
            else:
                imports.extend(alias.name for alias in node.names)
    return imports


def _frame(value: str) -> bytes:
    encoded = value.encode("utf-8", "strict")
    return len(encoded).to_bytes(8, "big") + encoded


def _independent_failure_id(envelope: dict[str, object]) -> str:
    parts = [
        _frame("ebu.failure-id.v1"),
        _frame(envelope["failure_code"]),  # type: ignore[arg-type]
        _frame(envelope["stage"]),  # type: ignore[arg-type]
    ]
    interface = envelope["interface_ref"]
    if type(interface) is dict:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(interface["module"]),  # type: ignore[arg-type]
                _frame(interface["qualname"]),  # type: ignore[arg-type]
                _frame(interface["interface_version"]),  # type: ignore[arg-type]
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
                _frame(reference["object_id"]),  # type: ignore[arg-type]
                _frame(reference["object_version"]),  # type: ignore[arg-type]
                _frame(reference["object_content_hash"]),  # type: ignore[arg-type]
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
                _frame(event_key["group_or_scope_id"]),  # type: ignore[arg-type]
                _frame(event_key["event_kind"]),  # type: ignore[arg-type]
                _frame(event_key["primary_object_id"]),  # type: ignore[arg-type]
                _frame(str(event_key["local_sequence"])),
            )
        )
    else:
        assert event_key == "NOT_APPLICABLE"
        parts.append(_frame("NOT_APPLICABLE"))
    parts.append(_frame(str(envelope["failure_ordinal"])))
    digest = hashlib.sha256(b"".join(parts)).hexdigest()
    return f"ebu:failure:core:sha256-{digest}"


def _assert_failure(
    error: FrameworkError,
    expected: dict[str, object],
    vector_id: str,
) -> None:
    actual = error.envelope.to_ecj1()
    expected_projection = expected["failure_envelope_projection"]
    assert type(expected_projection) is dict
    assert len(actual) == 16
    assert actual == expected_projection, vector_id
    assert actual["failure_code"] == expected["failure_code"], vector_id
    failure_id = actual["failure_id"]
    assert type(failure_id) is dict
    independently_derived = _independent_failure_id(actual)
    assert independently_derived == expected["failure_id"], vector_id
    assert failure_id["value"] == independently_derived, vector_id


def test_i3c_runtime_and_static_inventory() -> None:
    contract = _load_contract(_MECHANICAL_CONTRACT)
    module_exports = contract["module_exports"]
    direct_imports = contract["direct_imports"]
    assert type(module_exports) is dict and type(direct_imports) is dict

    annotations: dict[str, list[tuple[str, str]]] = {}
    for module_name, path in _PRODUCTION_PATHS.items():
        source = path.read_text(encoding="utf-8")
        assert "entropy" not in source.casefold()
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec", dont_inherit=True)
        annotations.update(_class_annotations(tree))
        assert tuple(_MODULES[module_name].__all__) == tuple(
            module_exports[module_name]
        )
        assert _direct_relative_imports(tree) == direct_imports[module_name]

    types = contract["types"]
    assert type(types) is list
    selected_types = [entry for entry in types if entry[1] in _MODULES]
    assert len(selected_types) == 17
    for entry in selected_types:
        name, module_name, formation, members_or_fields = entry[:4]
        runtime_value = getattr(_MODULES[module_name], name)
        if formation == "FROZEN_DATACLASS":
            assert is_dataclass(runtime_value)
            parameters = runtime_value.__dataclass_params__
            assert parameters.frozen is True
            assert parameters.eq is True
            assert parameters.order is False
            assert parameters.unsafe_hash is False
            expected_fields = [field_spec[0] for field_spec in members_or_fields]
            assert [field.name for field in fields(runtime_value)] == expected_fields
            assert tuple(runtime_value.__slots__) == tuple(expected_fields)
            signature = inspect.signature(runtime_value)
            assert all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY
                for parameter in signature.parameters.values()
            )
            expected_annotations = [
                (field_spec[0], field_spec[1].split("/", 1)[0])
                for field_spec in members_or_fields
            ]
            assert [field_name for field_name, _ in annotations[name]] == expected_fields
            assert [
                _normalized_annotation(annotation)
                for _, annotation in annotations[name]
            ] == [
                _normalized_annotation(annotation)
                for _, annotation in expected_annotations
            ]
            for invalid_arguments in ({}, {"unknown_field": None}):
                raised = _capture_framework_error(
                    lambda invalid_arguments=invalid_arguments: runtime_value(
                        **invalid_arguments
                    )
                )
                assert raised.envelope.to_ecj1()["failure_code"] == (
                    "I3_RECORD_FORMATION_INVALID"
                )
        else:
            assert formation == "STRENUM"
            assert issubclass(runtime_value, StrEnum)
            assert list(runtime_value.__members__) == members_or_fields
            assert [member.value for member in runtime_value] == members_or_fields

    validators = contract["validators"]
    assert type(validators) is list
    selected_validators = [
        validator for validator in validators if validator["module"] in _MODULES
    ]
    assert len(selected_validators) == 5
    assert [validator["name"] for validator in selected_validators] == list(
        _VALIDATORS
    )
    for validator in selected_validators:
        signature = inspect.signature(_VALIDATORS[validator["name"]])
        assert list(signature.parameters) == validator["argument_order"]
        assert all(
            parameter.kind is inspect.Parameter.POSITIONAL_ONLY
            for parameter in signature.parameters.values()
        )
        assert signature.return_annotation in (None, "None")

    selected_interfaces = frozenset(_VALIDATORS)
    collection_rows = [
        row
        for row in contract["collection_contracts"]
        if row["owner_interface"] in selected_interfaces
    ]
    applicability_rows = [
        row
        for row in contract["applicability_contracts"]
        if row["owner_interface"] in selected_interfaces
    ]
    paired_rows = [
        row
        for row in contract["paired_quantity_compatibility_inventory"]
        if row["validator"] in selected_interfaces
    ]
    scan_rows = [
        row
        for row in contract["object_content_scan_orders"]
        if row["validator"] in selected_interfaces
    ]
    assert len(collection_rows) == 31
    assert len(applicability_rows) == 10
    assert len(paired_rows) == 5
    assert len(scan_rows) == 5
    assert [row["scan_position"] for row in paired_rows] == [
        0,
        1,
        0,
        1,
        "2_PLUS_CANONICAL_SHARE_INDEX_i",
    ]

    dependency_graph = {
        name: tuple(direct_imports[name]) for name in contract["module_exports"]
    }
    assert len(dependency_graph) == 15
    assert sum(len(dependencies) for dependencies in dependency_graph.values()) == 91
    visited: set[str] = set()
    active: set[str] = set()

    def visit(module: str) -> None:
        if module in visited:
            return
        assert module not in active
        active.add(module)
        for dependency in dependency_graph[module]:
            if dependency in dependency_graph:
                visit(dependency)
        active.remove(module)
        visited.add(module)

    for module in dependency_graph:
        visit(module)
    assert len(visited) == 15

    assert len(FailureCode) == 88
    assert tuple(code.value for code in FailureCode)[-35:] == tuple(
        contract["failure_append_order"]
    )


def test_i3c_committed_authority_vectors() -> None:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    selected = [
        vector
        for vector in vectors
        if vector["materialized_effective_input"]["interface"]["module"]
        in _MODULE_NAMES
    ]
    assert len(selected) == 125
    assert Counter(vector["category"] for vector in selected) == {
        "FORMATION_POSITIVE": 17,
        "FORMATION_BOUNDARY": 17,
        "FORMATION_NEGATIVE": 17,
        "VALIDATOR_POSITIVE": 5,
        "VALIDATOR_BOUNDARY": 5,
        "ISOLATED_SINGLE_FAILURE": 32,
        "ADJACENT_PRECEDENCE_PAIR": 27,
        "MULTIPLY_INVALID_ALL_PRECEDENCE": 5,
    }

    effective_outcomes: dict[bytes, bytes] = {}
    exercised: Counter[str] = Counter()
    success_count = 0
    failure_count = 0
    for vector in selected:
        vector_id = vector["vector_id"]
        exercised[vector_id] += 1
        effective_input = vector["materialized_effective_input"]
        interface = effective_input["interface"]
        assert interface == vector["expected_interface"]
        assert vector["expected_stage"] == "I-3"
        ordered_arguments = effective_input["ordered_arguments"]
        expected = vector["expected"]

        effective_key = json.dumps(
            {
                "interface": interface,
                "ordered_arguments": ordered_arguments,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        outcome_key = json.dumps(
            expected,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        previous = effective_outcomes.setdefault(effective_key, outcome_key)
        assert previous == outcome_key, vector_id

        if vector["category"].startswith("FORMATION_"):
            assert len(ordered_arguments) == 1
            descriptor = ordered_arguments[0]["value"]
            if expected["kind"] == "SUCCESS":
                value = _form_value(
                    interface["module"], interface["qualname"], descriptor
                )
                projection = _project(value)
                assert projection == descriptor["ecj1"], vector_id
                assert projection == expected["return_value"], vector_id
                assert projection == expected["successful_projection"], vector_id
                success_count += 1
            else:
                raised = _capture_framework_error(
                    lambda: _form_value(
                        interface["module"], interface["qualname"], descriptor
                    )
                )
                _assert_failure(raised, expected, vector_id)
                failure_count += 1
            continue

        arguments = []
        for argument in ordered_arguments:
            descriptor = argument["value"]
            value = _construct(descriptor)
            assert _project(value) == descriptor["ecj1"], vector_id
            arguments.append(value)
        validator = _VALIDATORS[interface["qualname"]]
        if expected["kind"] == "SUCCESS":
            assert validator(*arguments) is expected["return_value"], vector_id
            assert [_project(argument) for argument in arguments] == expected[
                "successful_projection"
            ], vector_id
            success_count += 1
        else:
            raised = _capture_framework_error(lambda: validator(*arguments))
            _assert_failure(raised, expected, vector_id)
            failure_count += 1

    assert len(exercised) == 125
    assert set(exercised.values()) == {1}
    assert len(effective_outcomes) == 125
    assert success_count == 44
    assert failure_count == 81


class I3CDeclarationsTests(unittest.TestCase):
    def test_i3c_runtime_and_static_inventory(self) -> None:
        test_i3c_runtime_and_static_inventory()

    def test_i3c_committed_authority_vectors(self) -> None:
        test_i3c_committed_authority_vectors()


if __name__ == "__main__":
    unittest.main()
