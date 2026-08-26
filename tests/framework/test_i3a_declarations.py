"""Deterministic T0 conformance checks for the independently selected I-3A slice."""

from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass
from enum import StrEnum
import inspect
import json
from pathlib import Path
from typing import get_args
import unittest

from ebu_framework.canonical import parse_ecj1
import ebu_framework.conservation as conservation_module
from ebu_framework.conservation import (
    BoundaryFlowChannelDeclaration,
    BoundaryFlowDirection,
    BoundaryFlowRollupRole,
    ConservationAccountLevel,
    ConservationEvidence,
    ConservationProfile,
    ConservationProfileSelection,
    ConservedQuantityDeclaration,
    CoordinateCoefficient,
    ExactResidualExpectation,
    InternalTransformationOrInvariantDeclaration,
    ResidualExpectation,
    TransformationDeclarationKind,
    UncertaintyAwareResidualExpectation,
    validate_conservation_profile,
    validate_conservation_profile_selection,
)
import ebu_framework.distortion as distortion_module
from ebu_framework.distortion import DistortionModel, validate_distortion_model
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    RepresentedStateProjectionHash,
    ScientificId,
    SemanticVersion,
    StatePayloadHash,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.primitives import (
    ClaimStatus,
    Epoch,
    Quantity,
    ResolutionDetail,
    ResolutionState,
)
import ebu_framework.state as state_module
from ebu_framework.state import (
    ProjectionContract,
    RepresentedState,
    SystemState,
    validate_projection_contract,
    validate_state_record,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_MECHANICAL_CONTRACT = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_CONTRACT = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_I3A_MODULES = (
    "ebu_framework.state",
    "ebu_framework.conservation",
    "ebu_framework.distortion",
)
_PRODUCTION_PATHS = {
    "state": _REPO_ROOT / "src/ebu_framework/state.py",
    "conservation": _REPO_ROOT / "src/ebu_framework/conservation.py",
    "distortion": _REPO_ROOT / "src/ebu_framework/distortion.py",
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
    "Applicability": Applicability,
    "BoundaryFlowChannelDeclaration": BoundaryFlowChannelDeclaration,
    "BoundaryFlowDirection": BoundaryFlowDirection,
    "BoundaryFlowRollupRole": BoundaryFlowRollupRole,
    "ClaimStatus": ClaimStatus,
    "CommonObjectEnvelope": CommonObjectEnvelope,
    "ConservationAccountLevel": ConservationAccountLevel,
    "ConservationEvidence": ConservationEvidence,
    "ConservationProfile": ConservationProfile,
    "ConservationProfileSelection": ConservationProfileSelection,
    "ConservedQuantityDeclaration": ConservedQuantityDeclaration,
    "CoordinateCoefficient": CoordinateCoefficient,
    "DistortionModel": DistortionModel,
    "Epoch": Epoch,
    "ExactResidualExpectation": ExactResidualExpectation,
    "IntegerV1": IntegerV1,
    "InternalTransformationOrInvariantDeclaration": (
        InternalTransformationOrInvariantDeclaration
    ),
    "LifecycleStatus": LifecycleStatus,
    "ObjectContentHash": ObjectContentHash,
    "ObjectRef": ObjectRef,
    "ProjectionContract": ProjectionContract,
    "Quantity": Quantity,
    "RepresentedState": RepresentedState,
    "RepresentedStateProjectionHash": RepresentedStateProjectionHash,
    "ResolutionDetail": ResolutionDetail,
    "ResolutionState": ResolutionState,
    "ScientificId": ScientificId,
    "SemanticVersion": SemanticVersion,
    "StatePayloadHash": StatePayloadHash,
    "SystemState": SystemState,
    "TransformationDeclarationKind": TransformationDeclarationKind,
    "UncertaintyAwareResidualExpectation": (
        UncertaintyAwareResidualExpectation
    ),
}
_ENUM_TYPES = {
    "Applicability",
    "BoundaryFlowDirection",
    "BoundaryFlowRollupRole",
    "ClaimStatus",
    "ConservationAccountLevel",
    "LifecycleStatus",
    "ResolutionState",
    "TransformationDeclarationKind",
}
_VALUE_TYPES = {
    "ObjectContentHash",
    "RepresentedStateProjectionHash",
    "ScientificId",
    "SemanticVersion",
    "StatePayloadHash",
}
_FORMATION_HELPERS = {
    "ebu_framework.state": state_module._formation_failure,
    "ebu_framework.conservation": conservation_module._formation_failure,
    "ebu_framework.distortion": distortion_module._formation_failure,
}
_VALIDATORS = {
    "validate_state_record": validate_state_record,
    "validate_projection_contract": validate_projection_contract,
    "validate_conservation_profile_selection": (
        validate_conservation_profile_selection
    ),
    "validate_conservation_profile": validate_conservation_profile,
    "validate_distortion_model": validate_distortion_model,
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
    if runtime_type == "str":
        value = descriptor["value"]
        assert type(value) is str
        return value
    if runtime_type == "bool":
        value = descriptor["value"]
        assert type(value) is bool
        return value
    if runtime_type == "int":
        value = descriptor["value"]
        assert type(value) is int
        return value

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
    if type(value) is bytes:
        return parse_ecj1(value)
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is tuple:
        return [_project(member) for member in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _form_value(
    module: str, qualname: str, descriptor: dict[str, object]
) -> object:
    value = _construct(descriptor)
    if qualname == "ResidualExpectation":
        accepted_types = get_args(ResidualExpectation)
        if type(value) not in accepted_types:
            _FORMATION_HELPERS[module](qualname)
        return value
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


_I1_I2_FAILURE_PREFIX = (
    "CANONICALIZATION_FAILURE",
    "INVALID_ECJ1",
    "NONCANONICAL_ECJ1",
    "ECJ1_TYPE_UNSUPPORTED",
    "FLOAT_FORBIDDEN",
    "CYCLIC_OBJECT_GRAPH",
    "DUPLICATE_OBJECT_NAME",
    "INVALID_UNICODE_SCALAR",
    "UNASSIGNED_UNICODE_SCALAR",
    "UNICODE_DATA_INTEGRITY_FAILURE",
    "UNICODE_DATA_MALFORMED",
    "SCIENTIFIC_ID_INVALID",
    "SEMANTIC_VERSION_INVALID",
    "DIGEST_INVALID",
    "DIGEST_TYPE_MISMATCH",
    "HASH_DOMAIN_MISMATCH",
    "ARTIFACT_TOO_LARGE",
    "STABLE_KEY_INVALID",
    "NAMESPACE_UNREGISTERED",
    "RESERVED_NAMESPACE",
    "ALLOCATION_COLLISION",
    "ALLOCATION_CLAIM_CONFLICT",
    "REGISTRY_IMMUTABLE",
    "REGISTRY_RECORD_CONFLICT",
    "ALIAS_CONFLICT",
    "ALIAS_INVALID",
    "REF_NOT_FOUND",
    "VERSION_MISMATCH",
    "HASH_MISMATCH",
    "BOUNDARY_MISMATCH",
    "CLOCK_MISMATCH",
    "CONVERSION_RULE_MISMATCH",
    "CORE_NUMBER_INVALID",
    "DIMENSION_MISMATCH",
    "DIVISION_BY_ZERO",
    "ERROR_BOUND_INVALID",
    "HORIZON_INVALID",
    "IMPLICIT_ABSENCE_FORBIDDEN",
    "IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN",
    "INVALID_AGGREGATION",
    "LIFECYCLE_TRANSITION_INVALID",
    "NONFINITE_NUMBER_FORBIDDEN",
    "NUMERICAL_OPERATION_UNSUPPORTED",
    "NUMERICAL_POLICY_INCOMPLETE",
    "NUMERICAL_POLICY_REQUIRED",
    "QUANTITY_TYPE_MISMATCH",
    "REGION_MISMATCH",
    "RESOLUTION_STATE_INVALID",
    "SIGN_CONVENTION_MISMATCH",
    "SUPERSESSION_INVALID",
    "TIME_BASIS_MISMATCH",
    "UNCERTAINTY_RECORD_INVALID",
    "UNIT_MISMATCH",
)


def test_i3a_runtime_and_static_inventory() -> None:
    contract = _load_contract(_MECHANICAL_CONTRACT)
    module_exports = contract["module_exports"]
    direct_imports = contract["direct_imports"]
    assert type(module_exports) is dict and type(direct_imports) is dict

    runtime_modules = {
        "state": state_module,
        "conservation": conservation_module,
        "distortion": distortion_module,
    }
    trees: dict[str, ast.Module] = {}
    annotations: dict[str, list[tuple[str, str]]] = {}
    for module_name, path in _PRODUCTION_PATHS.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        trees[module_name] = tree
        annotations.update(_class_annotations(tree))
        assert tuple(runtime_modules[module_name].__all__) == tuple(
            module_exports[module_name]
        )
        assert _direct_relative_imports(tree) == direct_imports[module_name]

    types = contract["types"]
    assert type(types) is list
    selected_types = [entry for entry in types if entry[1] in runtime_modules]
    assert len(selected_types) == 18
    for entry in selected_types:
        name, module_name, formation, members_or_fields = entry[:4]
        runtime_value = getattr(runtime_modules[module_name], name)
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
            declared_annotations = annotations[name]
            expected_annotations = [
                (field_spec[0], field_spec[1].split("/", 1)[0])
                for field_spec in members_or_fields
            ]
            assert [name for name, _ in declared_annotations] == expected_fields
            assert [
                _normalized_annotation(annotation)
                for _, annotation in declared_annotations
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
        elif formation == "STRENUM":
            assert issubclass(runtime_value, StrEnum)
            assert list(runtime_value.__members__) == members_or_fields
            assert [member.value for member in runtime_value] == members_or_fields
        else:
            assert formation == "TAGGED_UNION"
            assert get_args(runtime_value) == (
                ExactResidualExpectation,
                UncertaintyAwareResidualExpectation,
            )

    validators = contract["validators"]
    assert type(validators) is list
    selected_validators = [
        validator
        for validator in validators
        if validator["module"] in runtime_modules
    ]
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

    failure_suffix = contract["failure_append_order"]
    assert type(failure_suffix) is list and len(failure_suffix) == 35
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
    assert tuple(
        failures[row["start"] : row["stop"]] for row in failure_slices
    ) == tuple(tuple(row["values"]) for row in failure_slices)
    assert failures[:53] == _I1_I2_FAILURE_PREFIX
    assert failures[53:88] == tuple(failure_suffix)
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

    contamination = contract["state_projection_contamination_ownership"]
    assert type(contamination) is dict
    assert set(contamination["reserved_direct_keys"]) == (
        state_module._RESERVED_PHYSICAL_KEYS
    )

    conservation_table = contract["conservation_requirement_table"]
    assert type(conservation_table) is dict
    rows = conservation_table["rows"]
    assert type(rows) is list
    assert [row[0] for row in rows] == [
        f"C{index:02d}" for index in range(1, 25)
    ]
    assert rows[2][5] == "NOT_APPLICABLE"
    scan_functions = (
        (
            conservation_module._profile_invalid_row,
            ("DIRECT_SELF_PARENT", "C08", "C13"),
        ),
        (
            conservation_module._level_requirement_row,
            tuple(conservation_table["level_scan_order"]),
        ),
        (
            conservation_module._evidence_requirement_row,
            tuple(conservation_table["evidence_scan_order"]),
        ),
        (
            conservation_module._isolation_invalid_row,
            tuple(conservation_table["isolation_scan_order"]),
        ),
    )
    for scan_function, expected_rows in scan_functions:
        source = inspect.getsource(scan_function)
        positions = [source.index(f'"{row}"') for row in expected_rows]
        assert positions == sorted(positions)

    paired_rows = [
        row
        for row in contract["paired_quantity_compatibility_inventory"]
        if row["validator"] == "validate_conservation_profile"
    ]
    assert paired_rows == [
        {
            "validator": "validate_conservation_profile",
            "left_path": "profile.conserved_quantities[i].unit_ref",
            "right_path": (
                "profile.conserved_quantities[i]."
                "coordinate_coefficients[j].unit_ref"
            ),
            "unit_relation": "EXACT_OBJECT_REF_EQUAL",
            "dimension_relation": "NOT_COMPARED_RIGHT_HAS_NO_DIMENSION_REF",
            "clock_or_interval_relation": "NONE",
            "failure_code": "CONSERVATION_UNIT_MISMATCH",
            "scan_position": "LEXICOGRAPHIC_i_j_FROM_ZERO",
        }
    ]


def test_i3a_committed_authority_vectors() -> None:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    selected = [
        vector
        for vector in vectors
        if vector["materialized_effective_input"]["interface"]["module"]
        in _I3A_MODULES
    ]
    assert len(selected) == 138
    expected_counts = {
        "FORMATION_POSITIVE": 18,
        "FORMATION_BOUNDARY": 18,
        "FORMATION_NEGATIVE": 18,
        "VALIDATOR_POSITIVE": 5,
        "VALIDATOR_BOUNDARY": 5,
        "ISOLATED_SINGLE_FAILURE": 37,
        "ADJACENT_PRECEDENCE_PAIR": 32,
        "MULTIPLY_INVALID_ALL_PRECEDENCE": 5,
    }
    assert {
        category: sum(vector["category"] == category for vector in selected)
        for category in expected_counts
    } == expected_counts

    exercise_counts: dict[str, int] = {}
    for vector in selected:
        vector_id = vector["vector_id"]
        exercise_counts[vector_id] = exercise_counts.get(vector_id, 0) + 1
        effective_input = vector["materialized_effective_input"]
        interface = effective_input["interface"]
        assert interface == vector["expected_interface"]
        assert vector["expected_stage"] == "I-3"
        ordered_arguments = effective_input["ordered_arguments"]
        expected = vector["expected"]

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
                        interface["module"],
                        interface["qualname"],
                        descriptor,
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
            assert actual_envelope["failure_id"]["value"] == expected[
                "failure_id"
            ]

    assert len(exercise_counts) == 138
    assert set(exercise_counts.values()) == {1}
    assert {
        "i3v-01-s06",
        "i3v-01-a05",
        "i3v-01-a06",
        "i3v-01-m",
    } <= set(exercise_counts)


class I3ADeclarationsTests(unittest.TestCase):
    def test_i3a_runtime_and_static_inventory(self) -> None:
        test_i3a_runtime_and_static_inventory()

    def test_i3a_committed_authority_vectors(self) -> None:
        test_i3a_committed_authority_vectors()


if __name__ == "__main__":
    unittest.main()
