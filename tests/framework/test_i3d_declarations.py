"""Deterministic T0 conformance checks for the frozen I-3D authority slice."""

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

import ebu_framework.artifacts as artifacts_module
from ebu_framework.artifacts import (
    ArtifactRecord,
    ExecutionResultManifest,
    validate_execution_result_manifest,
)
from ebu_framework.conservation import ConservationProfileSelection
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus, parse_ecj1
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
import ebu_framework.experiment as experiment_module
from ebu_framework.experiment import (
    ExecutionBinding,
    ExecutionIdentity,
    ExecutionMode,
    ExperimentConfiguration,
    OperationalExclusion,
    validate_execution_binding,
    validate_experiment_configuration,
)
import ebu_framework.faults as faults_module
from ebu_framework.faults import (
    FaultClass,
    FaultDirectiveV1,
    FaultScheduleClass,
    FaultScheduleV1,
    FaultTargetCoordinate,
    validate_fault_schedule_boundary,
)
from ebu_framework.identity import (
    ArtifactByteHash,
    ExecutionSemanticsHash,
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.hashing import (
    compute_execution_semantics_hash,
    compute_object_content_hash,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.policy import MemoryMode
from ebu_framework.primitives import Epoch, ResolutionDetail, ResolutionState


_REPO_ROOT = Path(__file__).resolve().parents[2]
_MECHANICAL_CONTRACT = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_CONTRACT = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_MODULES = {
    "faults": faults_module,
    "experiment": experiment_module,
    "artifacts": artifacts_module,
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
    "ArtifactByteHash": ArtifactByteHash,
    "ArtifactRecord": ArtifactRecord,
    "CommonObjectEnvelope": CommonObjectEnvelope,
    "ConservationProfileSelection": ConservationProfileSelection,
    "Epoch": Epoch,
    "ExecutionBinding": ExecutionBinding,
    "ExecutionIdentity": ExecutionIdentity,
    "ExecutionMode": ExecutionMode,
    "ExecutionResultManifest": ExecutionResultManifest,
    "ExecutionSemanticsHash": ExecutionSemanticsHash,
    "ExperimentConfiguration": ExperimentConfiguration,
    "FaultClass": FaultClass,
    "FaultDirectiveV1": FaultDirectiveV1,
    "FaultScheduleClass": FaultScheduleClass,
    "FaultScheduleV1": FaultScheduleV1,
    "FaultTargetCoordinate": FaultTargetCoordinate,
    "IntegerV1": IntegerV1,
    "LifecycleStatus": LifecycleStatus,
    "MemoryMode": MemoryMode,
    "ObjectContentHash": ObjectContentHash,
    "ObjectRef": ObjectRef,
    "OperationalExclusion": OperationalExclusion,
    "ResolutionDetail": ResolutionDetail,
    "ResolutionState": ResolutionState,
    "ScientificId": ScientificId,
    "SemanticVersion": SemanticVersion,
}
_ENUM_TYPES = {
    "Applicability",
    "ExecutionMode",
    "FaultClass",
    "FaultScheduleClass",
    "LifecycleStatus",
    "MemoryMode",
    "ResolutionState",
}
_VALUE_TYPES = {
    "ArtifactByteHash",
    "ExecutionSemanticsHash",
    "ObjectContentHash",
    "ScientificId",
    "SemanticVersion",
}
_FORMATION_HELPERS = {
    "ebu_framework.faults": faults_module._formation_failure,
    "ebu_framework.experiment": experiment_module._formation_failure,
    "ebu_framework.artifacts": artifacts_module._formation_failure,
}
_VALIDATORS = {
    "validate_fault_schedule_boundary": validate_fault_schedule_boundary,
    "validate_experiment_configuration": validate_experiment_configuration,
    "validate_execution_binding": validate_execution_binding,
    "validate_execution_result_manifest": validate_execution_result_manifest,
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
    if type(value) in {
        ArtifactByteHash,
        ExecutionSemanticsHash,
        ObjectContentHash,
        ScientificId,
        SemanticVersion,
    }:
        return str(value)
    value_type = type(value)
    if value_type.__module__ in _MODULE_NAMES and is_dataclass(value_type):
        excluded = {"envelope"}
        if value_type is ExecutionBinding:
            excluded.add("execution_semantics_hash")
        return {
            field.name: _project(getattr(value, field.name))
            for field in fields(value)
            if field.name not in excluded
        }
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
    assert envelope["event_key"] == "NOT_APPLICABLE"
    parts.append(_frame("NOT_APPLICABLE"))
    parts.append(_frame(str(envelope["failure_ordinal"])))
    digest = hashlib.sha256(b"".join(parts)).hexdigest()
    return f"ebu:failure:core:sha256-{digest}"


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(value) for value in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(value) for value in values)
    return len(keys) != len(set(keys))


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _object_hash_matches(record: object) -> bool:
    envelope = record.envelope  # type: ignore[attr-defined]
    supersedes = (
        envelope.supersedes_ref
        if type(envelope.supersedes_ref) is ObjectRef
        else None
    )
    recomputed = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=supersedes,
        object_content_payload=parse_ecj1(envelope.object_content_payload),
    )
    return recomputed == envelope.object_content_hash


def _content_mismatch(record: object) -> bool:
    return parse_ecj1(record.envelope.object_content_payload) != _project(record)  # type: ignore[attr-defined]


def _scanned_records(
    interface: str,
    arguments: list[object],
) -> list[tuple[object, str]]:
    if interface == "validate_fault_schedule_boundary":
        return [(arguments[0], "argument 1 (schedule)")]
    if interface == "validate_experiment_configuration":
        records = [(arguments[0], "argument 1 (configuration)")]
        if type(arguments[1]) is FaultScheduleV1:
            records.append((arguments[1], "argument 2 (fault_schedule)"))
        return records
    if interface == "validate_execution_binding":
        return [(arguments[0], "argument 1 (binding)")]
    manifest = [(arguments[0], "argument 1 (manifest)")]
    manifest.extend(
        (artifact, f"argument 2 (artifacts), member {index}")
        for index, artifact in enumerate(arguments[1])  # type: ignore[arg-type]
    )
    return manifest


def _directive_key(directive: FaultDirectiveV1) -> tuple[bytes, int, int, str]:
    target = json.dumps(
        _project(directive.target_coordinate),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8", "strict")
    return (
        target,
        directive.declared_priority.value,
        directive.local_sequence.value,
        str(directive.fault_id),
    )


def _fault_target_valid(directive: FaultDirectiveV1) -> bool:
    target = directive.target_coordinate
    def present(value: object, expected: type) -> bool:
        return type(value) is expected or value is Applicability.APPLICABLE

    def absent(value: object) -> bool:
        return value in {
            Applicability.NOT_APPLICABLE,
            Applicability.APPLICABLE,
        }

    if directive.fault_class is FaultClass.SCIENTIFIC_MODEL_EVENT:
        return (
            target.target_kind == "MODEL_EVENT"
            and present(target.epoch, Epoch)
            and present(target.phase_ordinal, IntegerV1)
            and present(target.scope_ref, ObjectRef)
            and present(target.event_kind_ref, ObjectRef)
            and present(target.primary_object_ref, ObjectRef)
            and absent(target.durability_boundary_ref)
            and absent(target.occurrence_ordinal)
        )
    return (
        target.target_kind == "DURABILITY_BOUNDARY"
        and absent(target.epoch)
        and absent(target.phase_ordinal)
        and absent(target.scope_ref)
        and absent(target.event_kind_ref)
        and absent(target.primary_object_ref)
        and present(target.durability_boundary_ref, ObjectRef)
        and present(target.occurrence_ordinal, IntegerV1)
    )


def _optional_refs(values: tuple[ObjectRef, ...]) -> object:
    return (
        [_project(value) for value in values]
        if values
        else Applicability.NOT_APPLICABLE.value
    )


def _execution_hash_matches(binding: ExecutionBinding) -> bool:
    recomputed = compute_execution_semantics_hash(
        accepted_configuration_ref=binding.accepted_configuration_ref,
        implementation_refs=binding.implementation_refs,
        source_refs=binding.source_refs,
        implementation_entrypoint_semantics=_project(
            binding.entrypoint_semantics_ref
        ),
        science_affecting_runtime_constraints=[
            _project(reference) for reference in binding.runtime_constraint_refs
        ],
        science_affecting_operational_exclusions=[
            _project(exclusion)
            for exclusion in binding.operational_exclusions
            if exclusion.science_affecting
        ],
        policy_memory_transition_contracts_or_not_applicable=_optional_refs(
            binding.policy_memory_transition_contract_refs
        ),
        fault_injection_delivery_contracts_or_not_applicable=_optional_refs(
            binding.fault_delivery_contract_refs
        ),
        event_order_contract=_project(binding.event_order_contract_ref),
        arithmetic_and_numerical_policy_contracts=[
            _project(reference)
            for reference in binding.numerical_policy_contract_refs
        ],
        information_capability_contract=_project(
            binding.information_capability_contract_ref
        ),
        canonical_scientific_trace_schema_ref=binding.trace_schema_ref,
        scientific_result_schema_ref=binding.result_schema_ref,
        stochastic_generator_and_stream_contract_or_not_applicable=_project(
            binding.stochastic_contract_ref
        ),
    )
    return recomputed == binding.execution_semantics_hash


def _exclusion_key(value: OperationalExclusion) -> tuple[tuple[str, str, str], bytes]:
    projection = json.dumps(
        _project(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8", "strict")
    return _ref_key(value.property_ref), projection


def _artifact_completeness_matches(
    manifest: ExecutionResultManifest,
    artifacts: tuple[ArtifactRecord, ...],
) -> bool:
    artifact_refs = tuple(_envelope_ref(artifact) for artifact in artifacts)
    artifact_kinds = {artifact.artifact_kind_ref for artifact in artifacts}
    required = set(manifest.required_artifact_kind_refs)
    missing = set(manifest.missing_artifact_kind_refs)
    if (
        manifest.ordered_artifact_refs != artifact_refs
        or missing != required - artifact_kinds
    ):
        return False
    if manifest.completeness.state is ResolutionState.PRESENT:
        return (
            type(manifest.terminal_state_ref) is ObjectRef
            and manifest.terminal_state_ref == manifest.last_confirmed_state_ref
        )
    if manifest.completeness.state in {
        ResolutionState.PARTIAL,
        ResolutionState.FAILED,
        ResolutionState.UNRESOLVED,
    }:
        return (
            manifest.terminal_state_ref is Applicability.NOT_APPLICABLE
            and type(manifest.last_confirmed_state_ref) is ObjectRef
        )
    return (
        manifest.terminal_state_ref is Applicability.NOT_APPLICABLE
        and manifest.last_confirmed_state_ref is Applicability.NOT_APPLICABLE
    )


def _independent_active_codes(
    interface: str,
    arguments: list[object],
) -> list[str]:
    active: list[str] = []
    scanned = _scanned_records(interface, arguments)
    if any(_content_mismatch(record) for record, _ in scanned):
        active.append("I3_OBJECT_CONTENT_MISMATCH")

    if interface == "validate_fault_schedule_boundary":
        schedule = arguments[0]
        assert type(schedule) is FaultScheduleV1
        applicability = tuple(
            value
            for directive in schedule.ordered_fault_directives
            for value in (
                directive.target_coordinate.epoch,
                directive.target_coordinate.phase_ordinal,
                directive.target_coordinate.scope_ref,
                directive.target_coordinate.event_kind_ref,
                directive.target_coordinate.primary_object_ref,
                directive.target_coordinate.durability_boundary_ref,
                directive.target_coordinate.occurrence_ordinal,
            )
        )
        if any(value is Applicability.APPLICABLE for value in applicability):
            active.append("IMPLICIT_ABSENCE_FORBIDDEN")
        keys = tuple(_directive_key(value) for value in schedule.ordered_fault_directives)
        if keys != tuple(sorted(keys)):
            active.append("I3_COLLECTION_ORDER_INVALID")
        if len(schedule.ordered_fault_directives) != len(
            set(schedule.ordered_fault_directives)
        ):
            active.append("I3_DUPLICATE_MEMBER")
        if any(
            not _fault_target_valid(directive)
            for directive in schedule.ordered_fault_directives
        ):
            active.append("FAULT_SCHEDULE_INVALID")
        if not _object_hash_matches(schedule):
            active.append("HASH_MISMATCH")
        return active

    if interface == "validate_experiment_configuration":
        configuration, fault_schedule = arguments
        assert type(configuration) is ExperimentConfiguration
        collections = (
            configuration.scientific_foundation_refs,
            configuration.action_definition_refs,
            configuration.schedule_refs,
            configuration.comparator_refs,
            configuration.parameter_refs,
            configuration.numerical_policy_refs,
            configuration.metric_refs,
            configuration.classification_rule_refs,
            configuration.analysis_rule_refs,
            configuration.seed_refs,
        )
        applicability = (
            configuration.policy_ref,
            configuration.initial_policy_memory_ref,
            configuration.fault_schedule_ref,
            fault_schedule,
        )
        if any(value is Applicability.APPLICABLE for value in applicability):
            active.append("IMPLICIT_ABSENCE_FORBIDDEN")
        if any(not _ordered_refs(values) for values in collections):
            active.append("I3_COLLECTION_ORDER_INVALID")
        if any(_duplicate_refs(values) for values in collections):
            active.append("I3_DUPLICATE_MEMBER")
        if any(not values for values in collections):
            active.append("CONFIGURATION_INCOMPLETE")
        stateless = configuration.policy_memory_mode is MemoryMode.STATELESS
        policy_absent = configuration.policy_ref is Applicability.NOT_APPLICABLE
        memory_absent = (
            configuration.initial_policy_memory_ref
            is Applicability.NOT_APPLICABLE
        )
        if stateless != (policy_absent and memory_absent) or (
            not stateless and (policy_absent or memory_absent)
        ):
            active.append("POLICY_MEMORY_NOT_APPLICABLE")
        configured = configuration.fault_schedule_ref
        if type(configured) is ObjectRef:
            available = (
                type(fault_schedule) is FaultScheduleV1
                and configured == _envelope_ref(fault_schedule)
            )
        else:
            available = fault_schedule is Applicability.NOT_APPLICABLE
        if not available:
            active.append("FAULT_EXTENSION_UNAVAILABLE")
        if any(not _object_hash_matches(record) for record, _ in scanned):
            active.append("HASH_MISMATCH")
        return active

    if interface == "validate_execution_binding":
        binding = arguments[0]
        assert type(binding) is ExecutionBinding
        collections = (
            binding.implementation_refs,
            binding.source_refs,
            binding.runtime_constraint_refs,
            binding.policy_memory_transition_contract_refs,
            binding.fault_delivery_contract_refs,
            binding.numerical_policy_contract_refs,
        )
        if binding.stochastic_contract_ref is Applicability.APPLICABLE:
            active.append("IMPLICIT_ABSENCE_FORBIDDEN")
        exclusion_keys = tuple(
            _exclusion_key(value) for value in binding.operational_exclusions
        )
        if any(not _ordered_refs(values) for values in collections) or (
            exclusion_keys != tuple(sorted(exclusion_keys))
        ):
            active.append("I3_COLLECTION_ORDER_INVALID")
        if any(_duplicate_refs(values) for values in collections) or len(
            binding.operational_exclusions
        ) != len(set(binding.operational_exclusions)):
            active.append("I3_DUPLICATE_MEMBER")
        if not _execution_hash_matches(binding):
            active.append("EXECUTION_SEMANTICS_PROJECTION_FAILURE")
        if not _object_hash_matches(binding):
            active.append("HASH_MISMATCH")
        return active

    manifest, artifacts = arguments
    assert type(manifest) is ExecutionResultManifest
    assert type(artifacts) is tuple
    applicability = (
        manifest.terminal_state_ref,
        manifest.last_confirmed_state_ref,
        manifest.policy_memory_ref,
    ) + tuple(
        value
        for artifact in artifacts
        for value in (artifact.schema_ref, artifact.content_ref)
    )
    if any(value is Applicability.APPLICABLE for value in applicability):
        active.append("IMPLICIT_ABSENCE_FORBIDDEN")
    artifact_refs = tuple(_envelope_ref(artifact) for artifact in artifacts)
    same_members = set(manifest.ordered_artifact_refs) == set(artifact_refs)
    if (
        (same_members and manifest.ordered_artifact_refs != artifact_refs)
        or not _ordered_refs(manifest.required_artifact_kind_refs)
        or not _ordered_refs(manifest.missing_artifact_kind_refs)
    ):
        active.append("I3_COLLECTION_ORDER_INVALID")
    if (
        _duplicate_refs(manifest.ordered_artifact_refs)
        or _duplicate_refs(manifest.required_artifact_kind_refs)
        or _duplicate_refs(manifest.missing_artifact_kind_refs)
        or len(artifacts) != len(set(artifacts))
    ):
        active.append("I3_DUPLICATE_MEMBER")
    if not _artifact_completeness_matches(manifest, artifacts):
        active.append("ARTIFACT_COMPLETENESS_INVALID")
    if any(not _object_hash_matches(record) for record, _ in scanned):
        active.append("HASH_MISMATCH")
    return active


def _independent_failure_envelope(
    interface: dict[str, object],
    failure_code: str,
    arguments: list[object],
) -> dict[str, object]:
    qualname = interface["qualname"]
    assert type(qualname) is str
    object_refs: list[dict[str, str]] = []
    summary = f"{qualname} rejected {failure_code}"
    if failure_code == "I3_OBJECT_CONTENT_MISMATCH":
        for record, position in _scanned_records(qualname, arguments):
            if _content_mismatch(record):
                envelope = record.envelope  # type: ignore[attr-defined]
                object_refs.append(
                    {
                        "object_content_hash": str(envelope.object_content_hash),
                        "object_id": str(envelope.object_id),
                        "object_version": str(envelope.object_version),
                    }
                )
                summary += f" at {position}"
                break
    projection: dict[str, object] = {
        "canonical_trace_state": {
            "applicability": "NOT_APPLICABLE",
            "completeness": "NOT_APPLICABLE",
            "confirmed_row_count": "NOT_APPLICABLE",
            "durable_prefix_ref": "NOT_APPLICABLE",
        },
        "durability_state": "NOT_APPLICABLE",
        "event_key": "NOT_APPLICABLE",
        "evidence_refs": [],
        "failure_code": failure_code,
        "failure_id": {"value": ""},
        "failure_ordinal": 0,
        "human_summary": summary,
        "interface_ref": {
            "module": interface["module"],
            "qualname": qualname,
            "interface_version": interface["interface_version"],
        },
        "object_refs": object_refs,
        "policy_memory_advance": "NONE",
        "retry_class": "FORBIDDEN",
        "schema_id": "ebu.failure-envelope/1",
        "scientific_status_effect": "UNSTARTED_PRESERVED",
        "stage": "I-3",
        "state_advance": "NONE",
    }
    projection["failure_id"] = {"value": _independent_failure_id(projection)}
    return projection


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


def _runtime_and_static_inventory() -> None:
    contract = _load_contract(_MECHANICAL_CONTRACT)
    module_exports = dict(contract["module_exports"])
    module_exports["faults"] = _load_contract(
        _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
    )["current_surface"]["module_exports"]["faults"]
    direct_imports = contract["direct_imports"]
    assert type(module_exports) is dict and type(direct_imports) is dict

    annotations: dict[str, list[tuple[str, str]]] = {}
    forbidden_calls = {
        "accept_experiment_configuration",
        "accept_execution_binding",
        "allocate_settlement",
        "append_operational_ledger_entry",
        "append_scientific_ledger_entry",
        "deliver_declared_fault",
        "evaluate_distortion",
        "finalize_execution_result_manifest",
        "infer_causal_contributions",
        "measure_state",
        "policy_propose",
        "project_state",
        "publish_artifacts",
    }
    for module_name, path in _PRODUCTION_PATHS.items():
        source = path.read_text(encoding="utf-8")
        assert "entropy" not in source.casefold()
        assert "i3v-" not in source.casefold()
        assert "operational_durability_event" not in source.casefold()
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec", dont_inherit=True)
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert called_names.isdisjoint(forbidden_calls)
        imported_roots = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        assert imported_roots.isdisjoint(
            {"os", "random", "secrets", "socket", "subprocess"}
        )
        annotations.update(_class_annotations(tree))
        assert tuple(_MODULES[module_name].__all__) == tuple(
            module_exports[module_name]
        )
        assert _direct_relative_imports(tree) == direct_imports[module_name]

    types = contract["types"]
    assert type(types) is list
    selected_types = [entry for entry in types if entry[1] in _MODULES]
    assert len(selected_types) == 12
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
    assert len(selected_validators) == 4
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
    assert len(collection_rows) == 22
    assert len(applicability_rows) == 17
    assert len(paired_rows) == 0
    assert len(scan_rows) == 4

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
    failure_slices = compatibility["current_surface"]["failure_slices"]
    failure_projection = ("\n".join(failures) + "\n").encode("utf-8")
    assert (len(failures), tuple(row["stop"] for row in failure_slices)) == (
        256,
        (53, 88, 102, 124, 185),
    )
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
    assert failures[227:232] == tuple(i6["failure_inventory"]["append_order"])
    assert failures[232:] == tuple(i7["failure_inventory"]["append_order"])
    assert (len(failure_projection), hashlib.sha256(failure_projection).hexdigest()) == (
        i7["failure_inventory"]["future_lf"]["byte_count"],
        i7["failure_inventory"]["future_lf"]["sha256"],
    )
    assert "OPERATIONAL_DURABILITY_EVENT" not in FaultClass.__members__


def _committed_authority_vectors() -> None:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    selected = [
        vector
        for vector in vectors
        if vector["materialized_effective_input"]["interface"]["module"]
        in _MODULE_NAMES
    ]
    assert len(selected) == 96
    assert Counter(vector["category"] for vector in selected) == {
        "FORMATION_POSITIVE": 12,
        "FORMATION_BOUNDARY": 12,
        "FORMATION_NEGATIVE": 12,
        "VALIDATOR_POSITIVE": 4,
        "VALIDATOR_BOUNDARY": 4,
        "ISOLATED_SINGLE_FAILURE": 26,
        "ADJACENT_PRECEDENCE_PAIR": 22,
        "MULTIPLY_INVALID_ALL_PRECEDENCE": 4,
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
            {"interface": interface, "ordered_arguments": ordered_arguments},
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

        active_codes = vector["precedence_evidence"]["active_failure_codes"]
        assert type(active_codes) is list
        if expected["kind"] == "FAILURE":
            assert active_codes[0] == expected["failure_code"], vector_id
        else:
            assert active_codes == [], vector_id

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
                assert active_codes == ["I3_RECORD_FORMATION_INVALID"], vector_id
                independent_envelope = _independent_failure_envelope(
                    interface,
                    "I3_RECORD_FORMATION_INVALID",
                    [],
                )
                assert independent_envelope == expected[
                    "failure_envelope_projection"
                ], vector_id
                assert independent_envelope["failure_id"]["value"] == expected[
                    "failure_id"
                ], vector_id
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
        independently_active = _independent_active_codes(
            interface["qualname"],
            arguments,
        )
        assert independently_active == active_codes, vector_id
        if expected["kind"] == "SUCCESS":
            assert validator(*arguments) is expected["return_value"], vector_id
            assert [_project(argument) for argument in arguments] == expected[
                "successful_projection"
            ], vector_id
            success_count += 1
        else:
            independent_envelope = _independent_failure_envelope(
                interface,
                independently_active[0],
                arguments,
            )
            assert independent_envelope == expected[
                "failure_envelope_projection"
            ], vector_id
            assert independent_envelope["failure_id"]["value"] == expected[
                "failure_id"
            ], vector_id
            raised = _capture_framework_error(lambda: validator(*arguments))
            _assert_failure(raised, expected, vector_id)
            failure_count += 1

    assert len(exercised) == 96
    assert set(exercised.values()) == {1}
    assert len(effective_outcomes) == 96
    assert success_count == 32
    assert failure_count == 64
    repaired = {
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
    selected_by_id = {vector["vector_id"]: vector for vector in selected}
    for vector_id, active_codes in repaired.items():
        vector = selected_by_id[vector_id]
        assert vector["materialized_effective_input"]["interface"]["qualname"] == (
            "validate_fault_schedule_boundary"
        )
        assert vector["precedence_evidence"]["active_failure_codes"] == active_codes


class I3DDeclarationsTests(unittest.TestCase):
    def test_i3d_runtime_and_static_inventory(self) -> None:
        _runtime_and_static_inventory()

    def test_i3d_committed_authority_vectors(self) -> None:
        _committed_authority_vectors()


if __name__ == "__main__":
    unittest.main()
