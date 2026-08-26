"""Deterministic T0 conformance checks for the frozen I-3B authority slice."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import fields, is_dataclass
from enum import StrEnum
import inspect
import json
from pathlib import Path
import unittest

import ebu_framework.actions as actions_module
from ebu_framework.actions import (
    ActionDefinition,
    ActionInstance,
    ActionStatus,
    ConstraintSupport,
    EffectiveInterval,
    WriteSupport,
    validate_action_definition,
    validate_action_instance,
)
import ebu_framework.commitments as commitments_module
from ebu_framework.commitments import (
    CapacityRecord,
    Commitment,
    Reservation,
    validate_capacity_record,
    validate_commitment,
    validate_reservation,
)
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
import ebu_framework.network as network_module
from ebu_framework.network import (
    AvailabilityStatus,
    CapacityLocus,
    Provider,
    ProviderNetwork,
    RoutePlan,
    RouteSemanticsStatus,
    TopologySnapshot,
    validate_provider_network,
    validate_route_plan,
)
from ebu_framework.numeric import IntegerV1
import ebu_framework.observation as observation_module
from ebu_framework.observation import (
    Measurement,
    MeasurementContract,
    validate_measurement,
)
from ebu_framework.primitives import (
    Epoch,
    Instant,
    Quantity,
    ResolutionDetail,
    ResolutionState,
    UncertaintyKind,
    UncertaintyRecord,
)
import ebu_framework.scheduling as scheduling_module
from ebu_framework.scheduling import (
    ComparatorKind,
    ComparatorSchedule,
    CoordinationEventDeclaration,
    Schedule,
    validate_schedule,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_MECHANICAL_CONTRACT = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_CONTRACT = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_MODULES = {
    "actions": actions_module,
    "network": network_module,
    "commitments": commitments_module,
    "observation": observation_module,
    "scheduling": scheduling_module,
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
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    parsed = json.loads(
        payload,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    assert type(parsed) is dict
    return parsed


_RUNTIME_TYPES: dict[str, object] = {
    "ActionDefinition": ActionDefinition,
    "ActionInstance": ActionInstance,
    "ActionStatus": ActionStatus,
    "Applicability": Applicability,
    "AvailabilityStatus": AvailabilityStatus,
    "CapacityLocus": CapacityLocus,
    "CapacityRecord": CapacityRecord,
    "Commitment": Commitment,
    "CommonObjectEnvelope": CommonObjectEnvelope,
    "ComparatorKind": ComparatorKind,
    "ComparatorSchedule": ComparatorSchedule,
    "ConstraintSupport": ConstraintSupport,
    "CoordinationEventDeclaration": CoordinationEventDeclaration,
    "EffectiveInterval": EffectiveInterval,
    "Epoch": Epoch,
    "Instant": Instant,
    "IntegerV1": IntegerV1,
    "LifecycleStatus": LifecycleStatus,
    "Measurement": Measurement,
    "MeasurementContract": MeasurementContract,
    "ObjectContentHash": ObjectContentHash,
    "ObjectRef": ObjectRef,
    "Provider": Provider,
    "ProviderNetwork": ProviderNetwork,
    "Quantity": Quantity,
    "Reservation": Reservation,
    "ResolutionDetail": ResolutionDetail,
    "ResolutionState": ResolutionState,
    "RoutePlan": RoutePlan,
    "RouteSemanticsStatus": RouteSemanticsStatus,
    "Schedule": Schedule,
    "ScientificId": ScientificId,
    "SemanticVersion": SemanticVersion,
    "TopologySnapshot": TopologySnapshot,
    "UncertaintyKind": UncertaintyKind,
    "UncertaintyRecord": UncertaintyRecord,
    "WriteSupport": WriteSupport,
}
_ENUM_TYPES = {
    "ActionStatus",
    "Applicability",
    "AvailabilityStatus",
    "ComparatorKind",
    "LifecycleStatus",
    "ResolutionState",
    "RouteSemanticsStatus",
    "UncertaintyKind",
}
_VALUE_TYPES = {
    "ObjectContentHash",
    "ScientificId",
    "SemanticVersion",
}
_FORMATION_HELPERS = {
    "ebu_framework.actions": actions_module._formation_failure,
    "ebu_framework.network": network_module._formation_failure,
    "ebu_framework.commitments": commitments_module._formation_failure,
    "ebu_framework.observation": observation_module._formation_failure,
    "ebu_framework.scheduling": scheduling_module._formation_failure,
}
_VALIDATORS = {
    "validate_action_definition": validate_action_definition,
    "validate_action_instance": validate_action_instance,
    "validate_provider_network": validate_provider_network,
    "validate_route_plan": validate_route_plan,
    "validate_commitment": validate_commitment,
    "validate_reservation": validate_reservation,
    "validate_capacity_record": validate_capacity_record,
    "validate_measurement": validate_measurement,
    "validate_schedule": validate_schedule,
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


def test_i3b_runtime_and_static_inventory() -> None:
    contract = _load_contract(_MECHANICAL_CONTRACT)
    i7_paths = _load_contract(
        _REPO_ROOT
        / "unified_python_research_framework_i7_implementation_path_manifest.json"
    )
    module_exports = contract["module_exports"]
    direct_imports = contract["direct_imports"]
    assert type(module_exports) is dict and type(direct_imports) is dict

    annotations: dict[str, list[tuple[str, str]]] = {}
    for module_name, path in _PRODUCTION_PATHS.items():
        source = path.read_text(encoding="utf-8")
        assert "entropy" not in source.casefold()
        tree = ast.parse(source, filename=str(path))
        annotations.update(_class_annotations(tree))
        expected_exports = i7_paths["module_exports"].get(
            module_name, module_exports[module_name]
        )
        assert tuple(_MODULES[module_name].__all__) == tuple(expected_exports)
        assert _direct_relative_imports(tree) == direct_imports[module_name]

    types = contract["types"]
    assert type(types) is list
    selected_types = [entry for entry in types if entry[1] in _MODULES]
    assert len(selected_types) == 22
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
            assert [name for name, _ in annotations[name]] == expected_fields
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
            expected_members = list(members_or_fields) + (
                ["ISOLATED"] if name == "AvailabilityStatus" else []
            )
            assert list(runtime_value.__members__) == expected_members
            assert [member.value for member in runtime_value] == expected_members

    validators = contract["validators"]
    assert type(validators) is list
    selected_validators = [
        validator for validator in validators if validator["module"] in _MODULES
    ]
    assert len(selected_validators) == 9
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
    assert len(collection_rows) == 56
    assert len(applicability_rows) == 7
    assert len(paired_rows) == 6
    assert len(scan_rows) == 9
    assert [row["scan_position"] for row in paired_rows] == [0, 0, 1, 2, 3, 0]

    dependency_graph = {
        name: tuple(direct_imports[name]) for name in contract["module_exports"]
    }
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

    compatibility = _load_contract(
        _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
    )
    failures = tuple(code.value for code in FailureCode)
    i6 = _load_contract(
        _REPO_ROOT / "unified_python_research_framework_i6_contract.json"
    )
    i7 = _load_contract(
        _REPO_ROOT / "unified_python_research_framework_i7_contract.json"
    )
    i8 = _load_contract(
        _REPO_ROOT / "unified_python_research_framework_i8_contract.json"
    )
    failure_slices = compatibility["current_surface"]["failure_slices"]
    failure_projection = ("\n".join(failures) + "\n").encode("utf-8")
    import hashlib

    assert failures[53:88] == tuple(contract["failure_append_order"])
    assert tuple(
        failures[row["start"] : row["stop"]] for row in failure_slices
    ) == tuple(tuple(row["values"]) for row in failure_slices)
    assert (
        failures[:185],
        failures[185:227],
        failures[:227],
    ) == (
        tuple(compatibility["current_surface"]["failure_order"]),
        tuple(
            _load_contract(
                _REPO_ROOT / "unified_python_research_framework_i5_contract.json"
            )["failure_append_order"]
        ),
        tuple(
            _load_contract(
                _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
            )["current_surface"]["failure_order"]
        ),
    )
    assert failures[227:232] == tuple(i6["failure_inventory"]["append_order"])
    assert failures[232:256] == tuple(i7["failure_inventory"]["append_order"])
    assert failures[256:] == tuple(i8["failure_inventory"]["future_values"][256:])
    assert len(failures) == i8["failure_inventory"]["future_total"] == 280
    assert (
        len(("\n".join(failures[:227]) + "\n").encode("utf-8")),
        hashlib.sha256(("\n".join(failures[:227]) + "\n").encode("utf-8")).hexdigest(),
        len(("\n".join(failures[185:227]) + "\n").encode("utf-8")),
        hashlib.sha256(
            ("\n".join(failures[185:227]) + "\n").encode("utf-8")
        ).hexdigest(),
    ) == (
        5997,
        "4cb1daceb30c0f106e7ba288980d379da2403236593948b4be47247704555ae4",
        1103,
        "b70fccfca86d4b7118bf80593794b40a2ad8f3848dbe4ff0963741e4e56f3681",
    )
    assert (len(failure_projection), hashlib.sha256(failure_projection).hexdigest()) == (
        i8["failure_inventory"]["future_lf"]["byte_count"],
        i8["failure_inventory"]["future_lf"]["sha256"],
    )


def test_i3b_committed_authority_vectors() -> None:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    selected = [
        vector
        for vector in vectors
        if vector["materialized_effective_input"]["interface"]["module"]
        in _MODULE_NAMES
    ]
    assert len(selected) == 185
    assert Counter(vector["category"] for vector in selected) == {
        "FORMATION_POSITIVE": 22,
        "FORMATION_BOUNDARY": 22,
        "FORMATION_NEGATIVE": 22,
        "VALIDATOR_POSITIVE": 9,
        "VALIDATOR_BOUNDARY": 9,
        "ISOLATED_SINGLE_FAILURE": 50,
        "ADJACENT_PRECEDENCE_PAIR": 41,
        "MULTIPLY_INVALID_ALL_PRECEDENCE": 9,
        "OBJECT_CONTENT_SCAN_ORDER": 1,
    }

    effective_outcomes: dict[bytes, bytes] = {}
    exercised: Counter[str] = Counter()
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
                "interface": effective_input["interface"],
                "ordered_arguments": effective_input["ordered_arguments"],
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
            else:
                raised = _capture_framework_error(
                    lambda: _form_value(
                        interface["module"], interface["qualname"], descriptor
                    )
                )
                assert raised.envelope.to_ecj1() == expected[
                    "failure_envelope_projection"
                ], vector_id
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
        else:
            raised = _capture_framework_error(lambda: validator(*arguments))
            actual_envelope = raised.envelope.to_ecj1()
            assert actual_envelope == expected[
                "failure_envelope_projection"
            ], vector_id
            assert actual_envelope["failure_code"] == expected["failure_code"]
            assert actual_envelope["failure_id"]["value"] == expected["failure_id"]

    assert len(exercised) == 185
    assert set(exercised.values()) == {1}
    assert len(effective_outcomes) == 184


class I3BDeclarationsTests(unittest.TestCase):
    def test_i3b_runtime_and_static_inventory(self) -> None:
        test_i3b_runtime_and_static_inventory()

    def test_i3b_committed_authority_vectors(self) -> None:
        test_i3b_committed_authority_vectors()


if __name__ == "__main__":
    unittest.main()
