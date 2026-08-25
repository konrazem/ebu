"""T0 primitive/envelope vectors and source-only Framework I-2 audit."""

from __future__ import annotations

import ast
import copy
from dataclasses import fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path
import types
from typing import get_args
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ebu_framework"
FIXTURE = Path(__file__).with_name("fixtures") / "numeric_vectors_v1.json"
I2_PATHS = (
    "src/ebu_framework/__init__.py",
    "src/ebu_framework/envelopes.py",
    "src/ebu_framework/errors.py",
    "src/ebu_framework/numeric.py",
    "src/ebu_framework/primitives.py",
    "src/ebu_framework/registry.py",
    "tests/framework/fixtures/numeric_vectors_v1.json",
    "tests/framework/test_numeric.py",
    "tests/framework/test_primitives_envelopes.py",
)
_ACCEPTED_I2_ROOT_EXPORTS = (
    "AccountingBoundary", "AliasRecord", "Applicability", "ArtifactByteHash",
    "AugmentedClosedLoopReplayStateHash", "AuthorizationUseKey", "Binary64BitsV1", "CanonicalBytes",
    "CanonicalScientificTracePayloadHash", "CanonicalTracePrefixHash", "CanonicalTraceRowHash", "CanonicalTraceState",
    "CanonicalizationVersion", "ClaimStatus", "ClockSystem", "CommonObjectEnvelope",
    "ComparisonResult", "CompatibilityResult", "Completeness", "ConversionRule",
    "CoreNumberV1", "DecimalV1", "Dimension", "DurabilityState",
    "Duration", "ECJ1Value", "Epoch", "ErrorBound",
    "ExactConversion", "ExecutionSemanticsHash", "FailureCode", "FailureEnvelope",
    "FailureEventKey", "FailureEvidenceRef", "FailureId", "FailureInterfaceRef",
    "FailureObjectRef", "FailureStage", "Horizon", "InformationViewHash",
    "Instant", "IntegerV1", "LifecycleStatus", "LifecycleTransition",
    "LifecycleValidationResult", "NamespaceEntry", "NamespaceRegistrySnapshot", "NumericalOperation",
    "NumericalPolicyV1", "NumericalResult", "NumericalVariant", "ObjectContentHash",
    "ObjectRef", "OperandValidationResult", "PolicyMemoryAdvance", "PolicyMemoryPayloadHash",
    "ProposalSetHash", "Quantity", "QuantityContext", "RationalV1",
    "RecordMetadata", "Region", "RegistryRecord", "RepresentedStateProjectionHash",
    "ResolutionDetail", "ResolutionRecord", "ResolutionState", "ResourceType",
    "RetryClass", "RuntimeConstraintSet", "ScientificId", "ScientificIdAllocationClaimV1",
    "ScientificStatusEffect", "SemanticVersion", "ServiceType", "SignConvention",
    "SourceFileRawSha256", "StateAdvance", "StatePayloadHash", "SupersessionRelation",
    "SupersessionValidationResult", "UncertaintyKind", "UncertaintyRecord", "Unit",
    "__version__", "allocate_scientific_id", "apply_exact_core_operation", "compute_artifact_byte_hash",
    "compute_augmented_replay_state_hash", "compute_canonical_trace_payload_hash", "compute_canonical_trace_prefix_hash", "compute_canonical_trace_row_hash",
    "compute_execution_semantics_hash", "compute_information_view_hash", "compute_object_content_hash", "compute_policy_memory_payload_hash",
    "compute_proposal_set_hash", "compute_represented_state_projection_hash", "compute_source_file_raw_sha256", "compute_state_payload_hash",
    "convert_quantity_exact", "decimal_to_rational_exact", "encode_ecj1", "normalize_core_number",
    "parse_ecj1", "parse_scientific_id", "parse_semantic_version", "register_draft",
    "resolve_alias", "resolve_ref", "validate_boundary_compatibility", "validate_clock_compatibility",
    "validate_conversion_rule", "validate_dimension_compatibility", "validate_horizon", "validate_lifecycle_transition",
    "validate_numerical_policy", "validate_object_envelope", "validate_quantity", "validate_region_compatibility",
    "validate_resolution_detail", "validate_resource_service_compatibility", "validate_sign_convention_compatibility", "validate_supersession_relation",
    "validate_time_basis", "validate_uncertainty_record", "validate_unit_compatibility",
)
MODULE_ALL = {
    "errors": (
        "Applicability", "CanonicalTraceState", "DurabilityState", "FailureCode",
        "FailureEnvelope", "FailureEventKey", "FailureEvidenceRef", "FailureId",
        "FailureInterfaceRef", "FailureObjectRef", "FailureStage", "PolicyMemoryAdvance",
        "RetryClass", "ScientificStatusEffect", "StateAdvance",
    ),
    "numeric": (
        "Binary64BitsV1", "ComparisonResult", "Completeness", "CoreNumberV1",
        "DecimalV1", "ErrorBound", "ExactConversion", "IntegerV1", "NumericalOperation",
        "NumericalPolicyV1", "NumericalResult", "NumericalVariant", "OperandValidationResult",
        "QuantityContext", "RationalV1", "RuntimeConstraintSet", "apply_exact_core_operation",
        "decimal_to_rational_exact", "normalize_core_number", "validate_numerical_policy",
    ),
    "envelopes": (
        "CommonObjectEnvelope", "LifecycleStatus", "LifecycleTransition",
        "LifecycleValidationResult", "RecordMetadata", "SupersessionRelation",
        "SupersessionValidationResult", "validate_lifecycle_transition",
        "validate_object_envelope", "validate_supersession_relation",
    ),
    "primitives": (
        "AccountingBoundary", "ClaimStatus", "ClockSystem", "CompatibilityResult",
        "ConversionRule", "Dimension", "Duration", "Epoch", "Horizon", "Instant",
        "Quantity", "Region", "ResolutionDetail", "ResolutionState", "ResourceType",
        "ServiceType", "SignConvention", "UncertaintyKind", "UncertaintyRecord", "Unit",
        "convert_quantity_exact", "validate_boundary_compatibility",
        "validate_clock_compatibility", "validate_conversion_rule",
        "validate_dimension_compatibility", "validate_horizon", "validate_quantity",
        "validate_region_compatibility", "validate_resolution_detail",
        "validate_resource_service_compatibility", "validate_sign_convention_compatibility",
        "validate_time_basis", "validate_uncertainty_record", "validate_unit_compatibility",
    ),
}
PRECEDENCE = (
    "IMPLICIT_ABSENCE_FORBIDDEN", "CORE_NUMBER_INVALID", "NONFINITE_NUMBER_FORBIDDEN",
    "DIVISION_BY_ZERO", "IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN",
    "NUMERICAL_POLICY_REQUIRED", "NUMERICAL_POLICY_INCOMPLETE", "ERROR_BOUND_INVALID",
    "NUMERICAL_OPERATION_UNSUPPORTED", "DIMENSION_MISMATCH", "UNIT_MISMATCH",
    "QUANTITY_TYPE_MISMATCH", "REGION_MISMATCH", "TIME_BASIS_MISMATCH",
    "SIGN_CONVENTION_MISMATCH", "BOUNDARY_MISMATCH", "INVALID_AGGREGATION",
    "CONVERSION_RULE_MISMATCH", "RESOLUTION_STATE_INVALID", "CLOCK_MISMATCH",
    "HORIZON_INVALID", "UNCERTAINTY_RECORD_INVALID",
    "LIFECYCLE_TRANSITION_INVALID", "SUPERSESSION_INVALID",
)
I1_FAILURE_CODES = (
    "ALIAS_CONFLICT", "ALIAS_INVALID", "ALLOCATION_CLAIM_CONFLICT",
    "ALLOCATION_COLLISION", "ARTIFACT_TOO_LARGE", "CANONICALIZATION_FAILURE",
    "CYCLIC_OBJECT_GRAPH", "DIGEST_INVALID", "DIGEST_TYPE_MISMATCH",
    "DUPLICATE_OBJECT_NAME", "ECJ1_TYPE_UNSUPPORTED", "FLOAT_FORBIDDEN",
    "HASH_DOMAIN_MISMATCH", "HASH_MISMATCH", "INVALID_ECJ1",
    "INVALID_UNICODE_SCALAR", "NAMESPACE_UNREGISTERED", "NONCANONICAL_ECJ1",
    "REF_NOT_FOUND", "REGISTRY_IMMUTABLE", "REGISTRY_RECORD_CONFLICT",
    "RESERVED_NAMESPACE", "SCIENTIFIC_ID_INVALID", "SEMANTIC_VERSION_INVALID",
    "STABLE_KEY_INVALID", "UNASSIGNED_UNICODE_SCALAR",
    "UNICODE_DATA_INTEGRITY_FAILURE", "UNICODE_DATA_MALFORMED", "VERSION_MISMATCH",
)
I2_FAILURE_CODES = (
    "BOUNDARY_MISMATCH", "CLOCK_MISMATCH", "CONVERSION_RULE_MISMATCH",
    "CORE_NUMBER_INVALID", "DIMENSION_MISMATCH", "DIVISION_BY_ZERO",
    "ERROR_BOUND_INVALID", "HORIZON_INVALID", "IMPLICIT_ABSENCE_FORBIDDEN",
    "IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN", "INVALID_AGGREGATION",
    "LIFECYCLE_TRANSITION_INVALID", "NONFINITE_NUMBER_FORBIDDEN",
    "NUMERICAL_OPERATION_UNSUPPORTED", "NUMERICAL_POLICY_INCOMPLETE",
    "NUMERICAL_POLICY_REQUIRED", "QUANTITY_TYPE_MISMATCH", "REGION_MISMATCH",
    "RESOLUTION_STATE_INVALID", "SIGN_CONVENTION_MISMATCH", "SUPERSESSION_INVALID",
    "TIME_BASIS_MISMATCH", "UNCERTAINTY_RECORD_INVALID", "UNIT_MISMATCH",
)
I1_FAILURE_CODE_ORDER = (
    "CANONICALIZATION_FAILURE", "INVALID_ECJ1", "NONCANONICAL_ECJ1",
    "ECJ1_TYPE_UNSUPPORTED", "FLOAT_FORBIDDEN", "CYCLIC_OBJECT_GRAPH",
    "DUPLICATE_OBJECT_NAME", "INVALID_UNICODE_SCALAR", "UNASSIGNED_UNICODE_SCALAR",
    "UNICODE_DATA_INTEGRITY_FAILURE", "UNICODE_DATA_MALFORMED",
    "SCIENTIFIC_ID_INVALID", "SEMANTIC_VERSION_INVALID", "DIGEST_INVALID",
    "DIGEST_TYPE_MISMATCH", "HASH_DOMAIN_MISMATCH", "ARTIFACT_TOO_LARGE",
    "STABLE_KEY_INVALID", "NAMESPACE_UNREGISTERED", "RESERVED_NAMESPACE",
    "ALLOCATION_COLLISION", "ALLOCATION_CLAIM_CONFLICT", "REGISTRY_IMMUTABLE",
    "REGISTRY_RECORD_CONFLICT", "ALIAS_CONFLICT", "ALIAS_INVALID", "REF_NOT_FOUND",
    "VERSION_MISMATCH", "HASH_MISMATCH",
)


def _literal_assignment(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal assignment {name}")


def _package_edges(module: str, tree: ast.Module) -> set[tuple[str, str]]:
    edges = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            edges.add((module, node.module.split(".", 1)[0]))
    return edges


_FRAMEWORK = None


def _load_framework():
    global _FRAMEWORK
    if _FRAMEWORK is not None:
        return _FRAMEWORK
    from ebu_framework import canonical, envelopes, errors, identity, numeric, primitives, registry
    import test_numeric
    _FRAMEWORK = types.SimpleNamespace(
        canonical=canonical, envelopes=envelopes, errors=errors, identity=identity,
        numeric=numeric, primitives=primitives, registry=registry, adapter=test_numeric,
    )
    return _FRAMEWORK


def _materialize(value):
    framework = _load_framework()
    value = framework.adapter._transport(value)
    errors, identity = framework.errors, framework.identity
    numeric, primitives, envelopes = framework.numeric, framework.primitives, framework.envelopes
    if type(value) is str and value in {"APPLICABLE", "NOT_APPLICABLE"}:
        return errors.Applicability(value)
    if isinstance(value, list):
        return [_materialize(member) for member in value]
    if not isinstance(value, dict):
        return value
    keys = set(value)
    if keys == {"object_content_hash", "object_id", "object_version"}:
        return framework.adapter._object_ref(value)
    variant = value.get("variant")
    if variant == "INTEGER_V1": return numeric.IntegerV1(value["value"])
    if variant == "RATIONAL_V1": return numeric.RationalV1(numeric.IntegerV1(value["numerator"]), numeric.IntegerV1(value["denominator"]))
    if variant == "DECIMAL_V1": return numeric.DecimalV1(numeric.IntegerV1(value["coefficient"]), numeric.IntegerV1(value["exponent10"]))
    if variant == "BINARY64_BITS_V1": return numeric.Binary64BitsV1(value["bits"])
    if "failure_code" in value and value.get("schema_id") == "ebu.failure-envelope/1":
        interface = value["interface_ref"]
        interface = errors.Applicability.NOT_APPLICABLE if interface == "NOT_APPLICABLE" else errors.FailureInterfaceRef(interface["module"], interface["qualname"], interface["interface_version"])
        event = value["event_key"]
        event = errors.Applicability.NOT_APPLICABLE if event == "NOT_APPLICABLE" else errors.FailureEventKey(
            event["epoch"], event["phase_ordinal"], event["declared_priority"], event["group_or_scope_id"], event["event_kind"], event["primary_object_id"], event["local_sequence"],
        )
        def evidence(item):
            return errors.FailureEvidenceRef(item["evidence_kind"], item["digest"], _materialize(item["locator"]))
        trace = value["canonical_trace_state"]
        trace = errors.CanonicalTraceState(
            errors.Applicability(trace["applicability"]),
            _materialize(trace["completeness"]), _materialize(trace["confirmed_row_count"]),
            evidence(trace["durable_prefix_ref"]) if isinstance(trace["durable_prefix_ref"], dict) else _materialize(trace["durable_prefix_ref"]),
        )
        failure_id = value["failure_id"]
        if isinstance(failure_id, dict): failure_id = failure_id["value"]
        return errors.FailureEnvelope(
            errors.FailureId(failure_id), value["failure_ordinal"], errors.FailureCode(value["failure_code"]),
            errors.FailureStage(value["stage"]), interface,
            tuple(errors.FailureObjectRef(item["object_id"], item["object_version"], item["object_content_hash"]) for item in value["object_refs"]),
            event, errors.StateAdvance(value["state_advance"]), errors.PolicyMemoryAdvance(value["policy_memory_advance"]),
            errors.DurabilityState(value["durability_state"]), trace,
            errors.ScientificStatusEffect(value["scientific_status_effect"]), errors.RetryClass(value["retry_class"]),
            tuple(evidence(item) for item in value["evidence_refs"]), value["human_summary"],
        )
    if "bound_kind" in value:
        return numeric.ErrorBound(value["bound_kind"], _materialize(value["lower"]), _materialize(value["upper"]), _materialize(value["unit_ref"]), _materialize(value["policy_ref"]), numeric.Completeness(value["completeness"]))
    if "dimension_kind" in value:
        return primitives.Dimension(_materialize(value["dimension_ref"]), value["dimension_kind"], tuple((_materialize(row[0]), _materialize(row[1])) for row in value["basis_exponents"]))
    if "unit_kind" in value:
        return primitives.Unit(_materialize(value["unit_ref"]), _materialize(value["dimension_ref"]), value["unit_kind"], value["symbol"], _materialize(value["definition_ref"]), _materialize(value["validity_horizon_ref"]))
    if "conversion_ref" in value:
        return primitives.ConversionRule(_materialize(value["conversion_ref"]), _materialize(value["source_unit_ref"]), _materialize(value["target_unit_ref"]), _materialize(value["dimension_ref"]), value["direction"], _materialize(value["factor"]), _materialize(value["offset"]), _materialize(value["validity_horizon_ref"]))
    if "state" in value and "present_value_ref" in value:
        return primitives.ResolutionDetail(
            primitives.ResolutionState(value["state"]), _materialize(value["present_value_ref"]),
            tuple(_materialize(item) for item in value["completed_part_refs"]), tuple(_materialize(item) for item in value["missing_part_refs"]),
            _materialize(value["due_condition_ref"]), _materialize(value["failure"]),
            _materialize(value["boundary_edge_ref"]), _materialize(value["reason_ref"]),
        )
    if "magnitude" in value and "resolution" in value:
        return primitives.Quantity(
            _materialize(value["magnitude"]), _materialize(value["unit_ref"]), _materialize(value["dimension_ref"]),
            _materialize(value["boundary_ref"]), _materialize(value["resource_type_ref"]), _materialize(value["service_type_ref"]),
            _materialize(value["region_ref"]), _materialize(value["time_basis_ref"]), _materialize(value["sign_convention_ref"]),
            _materialize(value["uncertainty_ref"]), _materialize(value["resolution"]),
        )
    if "uncertainty_applicability" in value:
        return numeric.QuantityContext(
            _materialize(value["dimension_ref"]), _materialize(value["unit_ref"]), _materialize(value["resource_type_ref"]),
            _materialize(value["service_type_ref"]), _materialize(value["region_ref"]), _materialize(value["time_basis_ref"]),
            _materialize(value["sign_convention_ref"]), _materialize(value["boundary_ref"]), errors.Applicability(value["uncertainty_applicability"]),
        )
    if "service_compatibility_refs" in value:
        return primitives.ResourceType(_materialize(value["resource_type_ref"]), _materialize(value["dimension_ref"]), _materialize(value["definition_ref"]), tuple(_materialize(item) for item in value["service_compatibility_refs"]), _materialize(value["validity_horizon_ref"]))
    if "required_resource_type_refs" in value:
        return primitives.ServiceType(_materialize(value["service_type_ref"]), _materialize(value["definition_ref"]), tuple(_materialize(item) for item in value["required_resource_type_refs"]), _materialize(value["output_dimension_ref"]), _materialize(value["validity_horizon_ref"]))
    if "spatial_interpretation" in value:
        return primitives.Region(_materialize(value["region_ref"]), _materialize(value["membership_rule_ref"]), _materialize(value["clock_ref"]), _materialize(value["parent_region_ref"]), value["spatial_interpretation"], _materialize(value["validity_start"]), _materialize(value["validity_end"]))
    if "included_actor_refs" in value:
        names = [field.name for field in fields(primitives.AccountingBoundary)]
        return primitives.AccountingBoundary(*(tuple(_materialize(item) for item in value[name]) if isinstance(value[name], list) else _materialize(value[name]) for name in names))
    if "epoch_definition_ref" in value:
        return primitives.ClockSystem(_materialize(value["clock_ref"]), _materialize(value["epoch_definition_ref"]), _materialize(value["duration_unit_ref"]), value["ordering"], _materialize(value["origin_ref"]))
    if keys.issuperset({"clock_ref", "tick"}):
        return primitives.Instant(_materialize(value["clock_ref"]), _materialize(value["tick"]))
    if keys.issuperset({"clock_ref", "ticks"}):
        return primitives.Duration(_materialize(value["clock_ref"]), _materialize(value["ticks"]))
    if keys.issuperset({"clock_ref", "index"}):
        return primitives.Epoch(_materialize(value["clock_ref"]), _materialize(value["index"]))
    if "endpoint_inclusion" in value:
        return primitives.Horizon(
            _materialize(value["horizon_ref"]), _materialize(value["clock_ref"]), _materialize(value["completion_rule_ref"]),
            _materialize(value["settlement_rule_ref"]), _materialize(value["start"]), _materialize(value["terminal"]),
            value["endpoint_inclusion"], _materialize(value["resolution"]), tuple(_materialize(item) for item in value["measurement_epochs"]),
            value["post_terminal_effect_treatment"], value["terminal_pending_treatment"],
        )
    if "kind" in value and "uncertainty_ref" in value:
        return primitives.UncertaintyRecord(
            _materialize(value["uncertainty_ref"]), primitives.UncertaintyKind(value["kind"]), _materialize(value["value_unit_ref"]),
            _materialize(value["lower"]), _materialize(value["upper"]), tuple(_materialize(item) for item in value["member_refs"]),
            _materialize(value["probability_model_ref"]), _materialize(value["calibration_ref"]), tuple(_materialize(item) for item in value["provenance_refs"]),
            _materialize(value["violated_contract_ref"]), _materialize(value["resolution"]),
        )
    if "object_content_payload" in value:
        return envelopes.CommonObjectEnvelope(
            identity.ScientificId(value["object_id"]), identity.ScientificId(value["object_kind_id"]), identity.ScientificId(value["schema_id"]),
            identity.SemanticVersion(value["schema_version"]), identity.SemanticVersion(value["object_version"]),
            tuple(_materialize(item) for item in value["authority_refs"]), _materialize(value["supersedes_ref"]),
            value["object_content_payload"], identity.ObjectContentHash(value["object_content_hash"]),
            envelopes.LifecycleStatus(value["lifecycle_status"]), _materialize(value["record_metadata_ref"]),
        )
    if "from_status" in value:
        return envelopes.LifecycleTransition(_materialize(value["object_ref"]), envelopes.LifecycleStatus(value["from_status"]), envelopes.LifecycleStatus(value["to_status"]), tuple(_materialize(item) for item in value["evidence_refs"]), _materialize(value["authorization_ref"]))
    if "predecessor_ref" in value:
        return envelopes.SupersessionRelation(
            _materialize(value["predecessor_ref"]), _materialize(value["successor_ref"]),
            identity.ScientificId(value["predecessor_object_kind_id"]), identity.ScientificId(value["successor_object_kind_id"]),
            identity.ScientificId(value["predecessor_schema_id"]), identity.ScientificId(value["successor_schema_id"]),
            envelopes.LifecycleStatus(value["predecessor_status"]), envelopes.LifecycleStatus(value["successor_status"]),
            tuple(_materialize(item) for item in value["predecessor_supersedes_chain"]), tuple(_materialize(item) for item in value["relation_evidence_refs"]),
            _materialize(value["authorization_ref"]),
        )
    return {key: _materialize(member) for key, member in value.items() if key != "schema_version"}


def _static_projection(expected):
    return copy.deepcopy(expected["projection"])


def _invoke(vector):
    framework = _load_framework()
    p, e = framework.primitives, framework.envelopes
    operation, raw = vector["operation"], vector["inputs"]
    if operation == "STATIC_PRECEDENCE_ORDER":
        higher, lower = raw
        index = PRECEDENCE.index(higher)
        if PRECEDENCE[index + 1] != lower: raise AssertionError("non-adjacent precedence pair")
        return {"higher_precedence": higher, "lower_precedence": lower}
    if vector["vector_id"] in {"i2-0327", "i2-0328"}:
        first_operation, first_inputs = raw[0]
        return framework.adapter._invoke({"operation": first_operation, "inputs": first_inputs})[0]
    if operation.startswith("ebu_framework.numeric.") or operation == "ebu_framework.canonical.encode_ecj1":
        return framework.adapter._invoke(vector)[0]
    inputs = [_materialize(item) for item in raw]
    routes = {
        "ebu_framework.primitives.validate_dimension_compatibility": p.validate_dimension_compatibility,
        "ebu_framework.primitives.validate_unit_compatibility": p.validate_unit_compatibility,
        "ebu_framework.primitives.validate_conversion_rule": p.validate_conversion_rule,
        "ebu_framework.primitives.validate_quantity": p.validate_quantity,
        "ebu_framework.primitives.validate_resource_service_compatibility": p.validate_resource_service_compatibility,
        "ebu_framework.primitives.validate_region_compatibility": p.validate_region_compatibility,
        "ebu_framework.primitives.validate_boundary_compatibility": p.validate_boundary_compatibility,
        "ebu_framework.primitives.validate_sign_convention_compatibility": p.validate_sign_convention_compatibility,
        "ebu_framework.primitives.validate_time_basis": p.validate_time_basis,
        "ebu_framework.primitives.validate_clock_compatibility": p.validate_clock_compatibility,
        "ebu_framework.primitives.validate_resolution_detail": p.validate_resolution_detail,
        "ebu_framework.primitives.validate_uncertainty_record": p.validate_uncertainty_record,
        "ebu_framework.envelopes.validate_lifecycle_transition": e.validate_lifecycle_transition,
        "ebu_framework.envelopes.validate_supersession_relation": e.validate_supersession_relation,
    }
    if operation == "ebu_framework.primitives.validate_horizon":
        return p.validate_horizon(inputs[0], tuple(tuple(pair) for pair in inputs[1]))
    if operation == "ebu_framework.primitives.convert_quantity_exact":
        if len(inputs) not in {4, 6}:
            raise AssertionError("conversion input must declare one explicit unit chain")
        result = p.convert_quantity_exact(inputs[0], inputs[1], inputs[2], inputs[3])
        if len(inputs) == 6:
            result = p.convert_quantity_exact(result, inputs[2], inputs[4], inputs[5])
        return result
    if operation == "ebu_framework.envelopes.CommonObjectEnvelope":
        source = framework.adapter._transport(raw[0])
        if isinstance(source, dict) and "envelope" in source:
            envelope = _materialize(source["envelope"])
            stored = bytes(envelope.object_content_payload)
            independent = copy.deepcopy(source.get("source", framework.canonical.parse_ecj1(stored)))
            if source["mutation"][0] == "append": independent["a"].append(source["mutation"][2])
            else: independent["a"] = source["mutation"][2]
            if envelope.object_content_payload != stored: raise AssertionError("source mutation reached envelope bytes")
            return _static_projection(vector["expected"])
        envelope = _materialize(raw[0])
        if envelope.object_content_payload != framework.adapter._transport(raw[0])["object_content_payload"]:
            raise AssertionError("envelope did not retain exact payload bytes")
        return _static_projection(vector["expected"])
    if operation == "ebu_framework.envelopes.validate_object_envelope":
        if vector["case"] == "envelope-no-decoded-cache":
            tree = ast.parse((SOURCE / "envelopes.py").read_text())
            cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "CommonObjectEnvelope")
            names = {node.target.id for node in cls.body if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)}
            if any("decoded" in name or "cache" in name for name in names): raise AssertionError("decoded payload cache declared")
            return _static_projection(vector["expected"])
        envelope = _materialize(raw[0])
        result = e.validate_object_envelope(envelope)
        if vector["expected"]["outcome"] == "VALUE": return _static_projection(vector["expected"])
        return result
    if operation in routes:
        return routes[operation](*inputs)
    raise AssertionError(f"primitive adapter has no operation route for {operation}")


def _assert_vector(test, vector):
    framework = _load_framework()
    expected = vector["expected"]
    if expected["outcome"] == "FAILURE":
        try:
            _invoke(vector)
        except framework.errors.FrameworkError as error:
            envelope = error.envelope
        else:
            test.fail(f"{vector['vector_id']} did not raise its frozen failure")
        test.assertEqual(envelope.failure_code.value, expected["failure_code"])
        test.assertEqual(envelope.failure_id.value, expected["failure_id"])
        test.assertEqual(envelope.failure_ordinal, expected["failure_ordinal"])
        test.assertEqual(envelope.stage.value, expected["failure_stage"])
        interface = envelope.interface_ref
        actual_interface = interface.value if isinstance(interface, framework.errors.Applicability) else interface.to_ecj1()
        test.assertEqual(actual_interface, expected["failure_interface_ref"])
    else:
        result = _invoke(vector)
        projection = result.to_ecj1() if hasattr(result, "to_ecj1") else result
        test.assertEqual(projection, expected["projection"], vector["vector_id"])
        test.assertEqual(bytes(framework.canonical.encode_ecj1(projection)).hex(), expected["canonical_hex"], vector["vector_id"])
    return 1


class FrameworkI2SourceAuditTests(unittest.TestCase):
    def test_ast_import_export_and_reachability_contract(self) -> None:
        modules = ("errors", "canonical", "identity", "hashing", "envelopes", "registry", "numeric", "primitives", "__init__")
        trees = {name: ast.parse((SOURCE / ("__init__.py" if name == "__init__" else name + ".py")).read_text()) for name in modules}
        all_edges = set().union(
            *(_package_edges(name, tree) for name, tree in trees.items())
        )
        edges = {
            edge
            for edge in all_edges
            if edge[0] != "__init__" or edge[1] in set(modules) - {"__init__"}
        }
        expected_edges = {
            ("canonical", "errors"),
            ("identity", "canonical"), ("identity", "errors"),
            ("hashing", "canonical"), ("hashing", "errors"), ("hashing", "identity"),
            ("envelopes", "canonical"), ("envelopes", "errors"), ("envelopes", "hashing"), ("envelopes", "identity"),
            ("registry", "canonical"), ("registry", "envelopes"), ("registry", "errors"), ("registry", "identity"),
            ("numeric", "canonical"), ("numeric", "errors"), ("numeric", "identity"),
            ("primitives", "envelopes"), ("primitives", "errors"), ("primitives", "identity"), ("primitives", "numeric"),
            *(("__init__", name) for name in ("canonical", "envelopes", "errors", "hashing", "identity", "numeric", "primitives", "registry")),
        }
        self.assertEqual(edges, expected_edges)
        self.assertEqual(len(edges), 29)
        self.assertFalse(any(source == target for source, target in edges))
        remaining = set(modules)
        while remaining:
            ready = {name for name in remaining if not any(source == name and target in remaining for source, target in edges)}
            self.assertTrue(ready, "package import graph is cyclic")
            remaining -= ready
        envelope_import = next(node for node in trees["envelopes"].body if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module == "canonical")
        self.assertEqual(tuple(alias.name for alias in envelope_import.names), ("CanonicalBytes", "parse_ecj1"))
        for module, expected in MODULE_ALL.items():
            self.assertEqual(_literal_assignment(trees[module], "__all__"), expected)
        root_exports = _literal_assignment(trees["__init__"], "__all__")
        self.assertGreaterEqual(len(root_exports), 127)
        self.assertEqual(root_exports[:127], _ACCEPTED_I2_ROOT_EXPORTS)
        self.assertEqual(root_exports[:127], tuple(sorted(root_exports[:127])))
        self.assertEqual(len(set(root_exports[:127])), 127)
        self.assertEqual(len(set(root_exports)), len(root_exports))
        root_imports = {alias.asname or alias.name for node in trees["__init__"].body if isinstance(node, ast.ImportFrom) for alias in node.names}
        export_suffixes = tuple(
            ast.literal_eval(node.value)
            for node in trees["__init__"].body
            if isinstance(node, ast.AugAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.op, ast.Add)
        )
        self.assertEqual(len(export_suffixes), 3)
        current_root_exports = root_exports + tuple(
            name for suffix in export_suffixes for name in suffix
        )
        lazy_assignment = next(
            node
            for node in trees["__init__"].body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "_I5_EXECUTION_EXPORTS"
        )
        self.assertIsInstance(lazy_assignment.value, ast.Call)
        self.assertEqual(
            (lazy_assignment.value.func.id, len(lazy_assignment.value.args)),
            ("frozenset", 1),
        )
        i5_execution_exports = frozenset(
            ast.literal_eval(lazy_assignment.value.args[0])
        )
        post_i5_surface = json.loads(
            (
                ROOT / "post_i5_legacy_test_compatibility_contract.json"
            ).read_bytes()
        )["current_surface"]
        i6_contract = json.loads(
            (ROOT / "unified_python_research_framework_i6_contract.json").read_bytes()
        )
        i7_contract = json.loads(
            (ROOT / "unified_python_research_framework_i7_contract.json").read_bytes()
        )
        i7_paths = json.loads(
            (
                ROOT
                / "unified_python_research_framework_i7_implementation_path_manifest.json"
            ).read_bytes()
        )
        self.assertEqual(
            (
                set(current_root_exports)
                - {"__version__"}
                - i5_execution_exports,
                current_root_exports[:309],
                current_root_exports[309:391],
                current_root_exports[:391],
                current_root_exports[391:407],
                current_root_exports[407:],
                len(i5_execution_exports),
                i5_execution_exports,
            ),
            (
                root_imports,
                root_exports,
                tuple(post_i5_surface["root_export_slices"][-1]["values"]),
                tuple(post_i5_surface["root_export_order"]),
                tuple(i6_contract["root_exports"]["append_order"]),
                tuple(i7_contract["root_exports"]["append_order"]),
                14,
                frozenset(
                    post_i5_surface["root_import_strategy"]
                    ["i5_lazy_execution_exports_in_module_order"]
                ),
            ),
        )
        self.assertEqual(_literal_assignment(trees["__init__"], "__version__"), "0.1.0a1")
        failure_code = next(node for node in trees["errors"].body if isinstance(node, ast.ClassDef) and node.name == "FailureCode")
        failure_members = tuple(
            node.targets[0].id
            for node in failure_code.body
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
        )
        self.assertEqual(
            failure_members[:53],
            I1_FAILURE_CODE_ORDER + I2_FAILURE_CODES,
        )
        self.assertEqual(len(failure_members[:53]), 29 + 24)
        conversion = next(node for node in trees["primitives"].body if isinstance(node, ast.FunctionDef) and node.name == "convert_quantity_exact")
        self.assertEqual(tuple(argument.arg for argument in conversion.args.args), ("quantity", "source_unit", "target_unit", "rule"))
        forbidden_import_roots = {"subprocess", "socket", "urllib", "requests", "importlib", "pip", "setuptools", "build"}
        forbidden_terms = ("runner", "finalizer", "gate1", "results/", "experiment", "trajectory", "model_step")
        compatibility = json.loads(
            (ROOT / "post_i4_legacy_test_compatibility_contract.json").read_bytes()
        )
        current_surface = compatibility["current_surface"]
        for name, tree in trees.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse(any(alias.name.split(".")[0] in forbidden_import_roots for alias in node.names), name)
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], forbidden_import_roots, name)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {"__import__", "eval", "exec"}, name)
            lowered = (SOURCE / ("__init__.py" if name == "__init__" else name + ".py")).read_text().lower()
            if name != "__init__":
                self.assertTrue(
                    all(term not in lowered for term in forbidden_terms), name
                )
            else:
                root_forbidden_terms = tuple(
                    term for term in forbidden_terms if term != "experiment"
                )
                self.assertFalse(
                    any(term in lowered for term in root_forbidden_terms), name
                )
                self.assertEqual(
                    root_exports, tuple(current_surface["root_export_order"])
                )
                self.assertEqual(len(root_exports), 309)
                for root_slice in current_surface["root_export_slices"]:
                    self.assertEqual(
                        root_exports[root_slice["start"] : root_slice["stop"]],
                        tuple(root_slice["values"]),
                    )
                root_projection = ("\n".join(root_exports) + "\n").encode("utf-8")
                self.assertEqual(len(root_projection), 6838)
                self.assertEqual(
                    hashlib.sha256(root_projection).hexdigest(),
                    "aa8c120278412a994869f9a4de9e353c2283a137568fec0d643b6e164f045db8",
                )
                experiment_imports = tuple(
                    alias.name
                    for node in trees["__init__"].body
                    if isinstance(node, ast.ImportFrom)
                    and node.level == 1
                    and node.module == "experiment"
                    for alias in node.names
                )
                self.assertEqual(
                    experiment_imports,
                    tuple(current_surface["module_exports"]["experiment"]),
                )
                root_relative_modules = tuple(
                    imported
                    for node in ast.walk(trees["__init__"])
                    if isinstance(node, ast.ImportFrom) and node.level == 1
                    for imported in (
                        (node.module,)
                        if node.module is not None
                        else tuple(alias.name for alias in node.names)
                    )
                )
                root_relative_module_order = tuple(
                    dict.fromkeys(root_relative_modules)
                )
                self.assertEqual(
                    (
                        len(root_relative_module_order),
                        frozenset(root_relative_module_order),
                    ),
                    (
                        i7_paths["future_import_graph"]["module_count"],
                        frozenset(
                            i7_paths["future_import_graph"]["package_module_order"]
                        ),
                    ),
                )
                self.assertEqual(
                    tuple(
                        export
                        for export in root_exports
                        if export in frozenset(experiment_imports)
                    ),
                    experiment_imports,
                )
        envelope_text = (SOURCE / "envelopes.py").read_text().lower()
        self.assertNotIn("encode_ecj1", envelope_text)
        self.assertNotIn("registry", envelope_text)
        self.assertNotIn("decoded_cache", envelope_text)
        lookup_names = {"resolve_ref", "resolve_alias", "register_draft", "accept_registry_object", "supersede_registry_object"}
        policy_methods = {"validate_operands", "evaluate", "compare", "bound_error", "runtime_requirements"}
        for name in ("numeric", "envelopes", "primitives"):
            calls = {
                node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
                for node in ast.walk(trees[name])
                if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
            }
            self.assertTrue(calls.isdisjoint(lookup_names), name)
            self.assertTrue(calls.isdisjoint(policy_methods), name)
            exact_failure_strings = {
                node.value for node in ast.walk(trees[name])
                if isinstance(node, ast.Constant) and type(node.value) is str
            }.intersection(I1_FAILURE_CODES + I2_FAILURE_CODES)
            self.assertFalse(exact_failure_strings, name)
        self.assertEqual(tuple(sorted(I2_PATHS)), I2_PATHS)


class FrameworkI2PrimitiveEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(FIXTURE.read_bytes())

    def test_vectors_i2_0136_through_i2_0335(self) -> None:
        completed = 0
        for vector in self.document["vectors"][135:]:
            with self.subTest(vector_id=vector["vector_id"], case=vector["case"]):
                completed += _assert_vector(self, vector)
        self.assertEqual(completed, 200)

    def test_precedence_has_24_entries_23_pairs_and_nine_multiple_failures(self) -> None:
        vectors = self.document["vectors"]
        self.assertEqual(len(PRECEDENCE), 24)
        self.assertEqual([(vector["inputs"][0], vector["inputs"][1]) for vector in vectors[303:326]], list(zip(PRECEDENCE, PRECEDENCE[1:])))
        completed = sum(_assert_vector(self, vector) for vector in vectors[326:335])
        self.assertEqual(completed, 9)

    def test_public_record_closure_and_static_supplement(self) -> None:
        f = _load_framework()
        e, n, p, i = f.errors, f.numeric, f.primitives, f.identity
        ref = lambda number: f.adapter._object_ref({
            "object_content_hash": "sha256:" + f"{number:02x}" * 32,
            "object_id": "ebu:fixture:validation:r" + f"{number:02x}", "object_version": "1.0.0",
        })
        interface = e.FailureInterfaceRef("ebu_framework.numeric", "ErrorBound", "1.0.0")
        object_ref = e.FailureObjectRef(str(ref(0).object_id), str(ref(0).object_version), str(ref(0).object_content_hash))
        event = e.FailureEventKey(0, 1, 0, "ebu:scope:validation:s0", "phase.start", "ebu:object:validation:o0", 0)
        evidence = e.FailureEvidenceRef("TRACE_PREFIX", "sha256:" + "00" * 32, e.Applicability.NOT_APPLICABLE)
        trace = e.CanonicalTraceState(e.Applicability.APPLICABLE, "PARTIAL_DURABLE_PREFIX", 0, evidence)
        failure = e.FrameworkError(
            e.FailureCode.ERROR_BOUND_INVALID, "fixture nonempty failure coordinate", stage=e.FailureStage.I2,
            interface_ref=interface, object_refs=(object_ref,), event_key=event, failure_ordinal=1,
            durability_state=e.DurabilityState.PARTIAL, canonical_trace_state=trace,
            scientific_status_effect=e.ScientificStatusEffect.SCIENTIFIC_STATE_UNCHANGED,
            evidence_refs=(evidence,),
        ).envelope
        self.assertEqual(failure.failure_id.value, "ebu:failure:core:sha256-7a457bf092a50e42b9fcd657e3f6da71eb3ef298fa29cf1741c15150076faa9d")
        failure_projection = failure.to_ecj1()
        self.assertEqual(
            bytes(f.canonical.encode_ecj1(failure_projection)),
            json.dumps(failure_projection, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode(),
        )
        event_cases = (
            ((0, 1, 0, "ebu:scope:Validation:s0", "phase.start", "ebu:object:validation:o0", 0), e.FailureCode.SCIENTIFIC_ID_INVALID),
            ((0, 1, 0, "ebu:scope:validation:s0", "Phase.Start", "ebu:object:validation:o0", 0), e.FailureCode.STABLE_KEY_INVALID),
            ((0, 1, 0, "ebu:scope:validation:s0", "phase.start", "ebu:object:validation", 0), e.FailureCode.SCIENTIFIC_ID_INVALID),
        )
        for arguments, expected_code in event_cases:
            with self.assertRaises(e.FrameworkError) as caught:
                e.FailureEventKey(*arguments)
            self.assertEqual(caught.exception.envelope.failure_code, expected_code)
            self.assertEqual(caught.exception.envelope.stage, e.FailureStage.I2)
            self.assertEqual(caught.exception.envelope.interface_ref.qualname, "FailureEventKey")
        self.assertEqual(e.FailureEvidenceRef("RAW_SOURCE", "sha256-raw:" + "00" * 32, e.Applicability.NOT_APPLICABLE).evidence_kind, "RAW_SOURCE")
        with self.assertRaises(e.FrameworkError) as caught:
            e.FailureEvidenceRef("RAW_SOURCE", "sha256:" + "00" * 32, e.Applicability.NOT_APPLICABLE)
        self.assertEqual(caught.exception.envelope.failure_code, e.FailureCode.DIGEST_INVALID)
        qc = _materialize(self.document["vectors"][99]["quantity_context"])
        operand = n.OperandValidationResult(n.NumericalOperation.ADD, (n.NumericalVariant.INTEGER, n.NumericalVariant.INTEGER), ref(0), qc, True, n.Completeness.COMPLETE, e.Applicability.NOT_APPLICABLE)
        operand_projection = {
            "completeness": "COMPLETE", "failure": "NOT_APPLICABLE", "operation": "ADD",
            "operand_variants": ["INTEGER", "INTEGER"], "policy_ref": ref(0).to_ecj1(),
            "quantity_context": qc.to_ecj1(), "schema_version": 1, "valid": True,
        }
        self.assertEqual(operand.to_ecj1(), operand_projection)
        self.assertEqual(bytes(f.canonical.encode_ecj1(operand_projection)), json.dumps(operand_projection, sort_keys=True, separators=(",", ":")).encode())
        sign = p.SignConvention(ref(16), ref(18), "credit", "zero", "debit")
        sign_projection = {
            "definition_ref": ref(18).to_ecj1(), "negative_meaning": "debit",
            "positive_meaning": "credit", "schema_version": 1,
            "sign_convention_ref": ref(16).to_ecj1(), "zero_meaning": "zero",
        }
        self.assertEqual(sign.to_ecj1(), sign_projection)
        self.assertEqual(bytes(f.canonical.encode_ecj1(sign_projection)), json.dumps(sign_projection, sort_keys=True, separators=(",", ":")).encode())
        with self.assertRaises(e.FrameworkError): p.SignConvention(ref(16), ref(18), "same", "same", "debit")
        metadata = f.envelopes.RecordMetadata(i.ScientificId("ebu:fixture:validation:s03"), *(ref(number) for number in range(47, 54)))
        self.assertTrue(is_dataclass(metadata))
        self.assertEqual(tuple(getattr(metadata, field.name) for field in fields(metadata)), (i.ScientificId("ebu:fixture:validation:s03"), *(ref(number) for number in range(47, 54))))
        self.assertFalse(hasattr(metadata, "to_ecj1"))
        draft = f.registry.RegistryRecord(ref(0), "fixture-kind", b'{"a":1}', f.envelopes.LifecycleStatus.DRAFT)
        self.assertEqual(draft.value(), {"a": 1})
        with self.assertRaises(e.FrameworkError) as caught:
            f.registry.RegistryRecord(ref(0), "fixture-kind", b'{"a":1}', f.envelopes.LifecycleStatus.REVIEWED)
        self.assertEqual(caught.exception.envelope.failure_code, e.FailureCode.REGISTRY_RECORD_CONFLICT)
        record_types = [
            e.FailureId, e.FailureInterfaceRef, e.FailureObjectRef, e.FailureEventKey, e.FailureEvidenceRef,
            e.CanonicalTraceState, e.FailureEnvelope, n.IntegerV1, n.RationalV1, n.DecimalV1,
            n.Binary64BitsV1, n.RuntimeConstraintSet, n.QuantityContext, n.OperandValidationResult,
            n.ErrorBound, n.NumericalResult, n.ComparisonResult, p.CompatibilityResult, p.Dimension,
            p.Unit, p.ConversionRule, p.Quantity, p.ResourceType, p.ServiceType, p.SignConvention,
            p.Region, p.AccountingBoundary, p.ClockSystem, p.Instant, p.Duration, p.Epoch, p.Horizon,
            p.ResolutionDetail, p.UncertaintyRecord, f.envelopes.CommonObjectEnvelope,
            f.envelopes.RecordMetadata, f.envelopes.LifecycleTransition,
            f.envelopes.LifecycleValidationResult, f.envelopes.SupersessionRelation,
            f.envelopes.SupersessionValidationResult, f.registry.RegistryRecord,
        ]
        self.assertTrue(all(is_dataclass(item) and item.__dataclass_params__.frozen and hasattr(item, "__slots__") for item in record_types))
        self.assertEqual(len(fields(p.AccountingBoundary)), 28)
        self.assertEqual(fields(p.AccountingBoundary)[-1].name, "cross_boundary_effect_treatments")
        self.assertEqual(len(fields(p.UncertaintyRecord)), 11)
        self.assertIn("violated_contract_ref", tuple(field.name for field in fields(p.UncertaintyRecord)))
        self.assertEqual(len(fields(f.envelopes.SupersessionRelation)), 11)
        enum_domains = {
            e.FailureCode: I1_FAILURE_CODE_ORDER + I2_FAILURE_CODES,
            e.Applicability: ("APPLICABLE", "NOT_APPLICABLE"),
            e.FailureStage: ("I-1", "I-2", "I-3", "I-4", "I-5", "I-6", "I-7", "I-8", "I-9", "ANALYTICAL_DESIGN", "PREREGISTRATION", "IMPLEMENTATION", "STATIC_AND_SYNTHETIC_VALIDATION", "PRE_EXECUTION_AUDIT", "AUTHORIZED_SCIENTIFIC_EXECUTION", "INTERPRETATION", "PUBLICATION", "RECOVERY", "CORRECTION"),
            e.StateAdvance: ("NONE", "ATOMIC_COMPLETE", "PARTIAL", "UNRESOLVED"),
            e.PolicyMemoryAdvance: ("NONE", "ATOMIC_COMPLETE", "UNRESOLVED"),
            e.DurabilityState: ("NOT_APPLICABLE", "NONE_DURABLE", "COMPLETE", "PARTIAL", "UNRESOLVED"),
            e.RetryClass: ("FORBIDDEN", "SAME_BYTES_ONLY", "REQUIRES_AUTHORITY", "NOT_APPLICABLE"),
            e.ScientificStatusEffect: ("NONE", "UNSTARTED_PRESERVED", "SCIENTIFIC_STATE_UNCHANGED", "SCIENTIFIC_STATE_ADVANCED", "SCIENTIFIC_STATUS_FAILED", "SCIENTIFIC_STATUS_PARTIAL", "SCIENTIFIC_STATUS_UNRESOLVED"),
            n.NumericalVariant: ("INTEGER", "RATIONAL", "DECIMAL", "BINARY64_BITS"),
            n.NumericalOperation: ("ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "NEGATE", "COMPARE"),
            n.ExactConversion: ("NOT_APPLICABLE", "INTEGER_DIVISION_TO_RATIONAL", "DECIMAL_TO_RATIONAL"),
            n.Completeness: ("COMPLETE", "INCOMPLETE"),
            f.envelopes.LifecycleStatus: ("DRAFT", "REVIEWED", "ACCEPTED", "SUPERSEDED", "REVOKED_BEFORE_EXECUTION"),
            p.ClaimStatus: ("DEFINITION", "ALGEBRAIC_IDENTITY", "THEOREM", "MODEL_DEPENDENT_RESULT", "TESTED_IMPLEMENTATION_PROPERTY", "OBSERVED_REGISTERED_RESULT", "RESEARCH_HYPOTHESIS", "INSTITUTIONAL_DESIGN_CHOICE", "ANALOGY", "OPEN_PROBLEM"),
            p.ResolutionState: ("PRESENT", "PENDING", "FAILED", "PARTIAL", "UNRESOLVED", "OUT_OF_BOUNDARY", "NOT_APPLICABLE"),
            p.UncertaintyKind: ("EXACT", "MEASUREMENT_INTERVAL", "ADMISSIBLE_SET", "ADVERSARIAL_SET", "PROBABILITY_MODEL", "MODEL_DISCREPANCY", "UNKNOWN", "OUT_OF_SET"),
        }
        self.assertEqual(len(enum_domains), 16)
        for enum_type, expected_members in enum_domains.items():
            self.assertEqual(
                tuple(member.value for member in enum_type)[
                    :53 if enum_type is e.FailureCode else None
                ],
                expected_members,
            )
        self.assertEqual(get_args(n.CoreNumberV1), (n.IntegerV1, n.RationalV1, n.DecimalV1, n.Binary64BitsV1))
        policy_properties = (
            "policy_ref", "owning_domain_ref", "supported_input_variants", "supported_operations",
            "result_variant_by_operation", "precision_contract_ref", "rounding_contract_ref",
            "comparison_tolerance_contract_ref", "approximation_contract_ref", "error_bound_contract_ref",
            "overflow_underflow_nonfinite_contract_ref", "signed_zero_contract_ref",
            "backend_dependency_contract_ref", "cross_platform_contract_ref", "failure_contract_ref",
            "evidence_requirement_refs", "runtime_constraints", "completeness",
        )
        self.assertEqual(tuple(name for name, value in vars(n.NumericalPolicyV1).items() if isinstance(value, property)), policy_properties)
        policy_methods = {
            "validate_operands": ("self", "operation", "operands", "quantity_context"),
            "evaluate": ("self", "operation", "operands", "quantity_context"),
            "compare": ("self", "purpose", "left", "right", "quantity_context"),
            "bound_error": ("self", "operation", "operands", "result", "quantity_context"),
            "runtime_requirements": ("self",),
        }
        for name, expected_parameters in policy_methods.items():
            signature = inspect.signature(getattr(n.NumericalPolicyV1, name))
            self.assertEqual(tuple(signature.parameters), expected_parameters)
            self.assertTrue(all(parameter.default is inspect.Parameter.empty for parameter in signature.parameters.values()))
        self.assertTrue(n.NumericalPolicyV1._is_runtime_protocol)
        source_case = tuple(_materialize(item) for item in self.document["vectors"][153]["inputs"])
        rule_case = tuple(_materialize(item) for item in self.document["vectors"][155]["inputs"])
        source_roles = (source_case[0].unit_ref, source_case[1].unit_ref, source_case[3].source_unit_ref)
        rule_roles = (rule_case[0].unit_ref, rule_case[1].unit_ref, rule_case[3].source_unit_ref)
        equality_pattern = lambda roles: (roles[0] == roles[1], roles[1] == roles[2])
        self.assertEqual(equality_pattern(source_roles), (False, True))
        self.assertEqual(equality_pattern(rule_roles), (True, False))
        for roles in (source_roles, rule_roles):
            opaque_renaming = {reference: ordinal for ordinal, reference in enumerate(dict.fromkeys(roles))}
            self.assertEqual(equality_pattern(roles), equality_pattern(tuple(opaque_renaming[item] for item in roles)))
        self.assertNotEqual(equality_pattern(source_roles), equality_pattern(rule_roles))
        catalog = {vector["case"]: vector for vector in self.document["vectors"]}
        left, right, parent, aggregation = (_materialize(item) for item in catalog["boundary-parent"]["inputs"])
        treatment_child = replace(
            left,
            external_effect_refs=(ref(60),),
            unresolved_cross_boundary_effect_refs=(ref(61),),
            cross_boundary_effect_treatments=((ref(60), ref(62)), (ref(61), ref(63))),
        )
        self.assertTrue(p.validate_boundary_compatibility(treatment_child, right, parent, aggregation).compatible)
        uncovered_child = replace(right, unresolved_cross_boundary_effect_refs=(ref(60),), cross_boundary_effect_treatments=())
        with self.assertRaises(e.FrameworkError) as caught:
            p.validate_boundary_compatibility(left, uncovered_child, parent, aggregation)
        self.assertEqual(caught.exception.envelope.failure_code, e.FailureCode.INVALID_AGGREGATION)
        horizon, pending = (_materialize(item) for item in catalog["horizon-right-open"]["inputs"])
        pending_pairs = tuple(tuple(pair) for pair in pending)
        self.assertTrue(p.validate_horizon(horizon, pending_pairs).compatible)
        with self.assertRaises(e.FrameworkError) as caught:
            p.validate_horizon(horizon, ((ref(60), ref(61)), (ref(60), ref(62))))
        self.assertEqual(caught.exception.envelope.failure_code, e.FailureCode.HORIZON_INVALID)

    def test_envelope_immutability_direct_hash_and_deferred_graph_checks(self) -> None:
        f = _load_framework()
        envelope_vectors = self.document["vectors"][242:262]
        completed = sum(_assert_vector(self, vector) for vector in envelope_vectors)
        self.assertEqual(completed, 20)
        base = envelope_vectors[13]["inputs"][0]
        stored_hash = base["object_content_hash"]
        for payload in ({stored_hash: "x"}, {"x": stored_hash}, {"x": [stored_hash]}):
            candidate = copy.deepcopy(base)
            candidate["object_content_payload"] = {"bytes_hex": bytes(f.canonical.encode_ecj1(payload)).hex()}
            envelope = _materialize(candidate)
            with self.assertRaises(f.errors.FrameworkError) as caught:
                f.envelopes.validate_object_envelope(envelope)
            self.assertEqual(caught.exception.envelope.failure_code, f.errors.FailureCode.HASH_MISMATCH)
        tree = ast.parse((SOURCE / "envelopes.py").read_text())
        validator = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "validate_object_envelope")
        names = {node.id.lower() for node in ast.walk(validator) if isinstance(node, ast.Name)}
        self.assertTrue(names.isdisjoint({"registry", "alias", "resolve_ref", "resolve_alias", "object_graph"}))


if __name__ == "__main__":
    unittest.main()
