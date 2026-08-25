"""Static and synthetic conformance checks for the frozen D1 declaration slice."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import fields, is_dataclass, replace
from enum import StrEnum
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import stat
from typing import get_args, get_origin, get_type_hints, Literal
import unittest

import ebu_framework
import ebu_framework.atomic as atomic_module
from ebu_framework.atomic import (
    AtomicRefinementDeclaration,
    BoundaryHistoryEquivalenceWitness,
    ConstitutiveGeneratorLink,
    ExtentDefinition,
    FiniteReconstructionWitness,
    HybridActivationDeclaration,
    QuantityParticipationGeneratorDeclaration,
    RegularityAndReparameterizationWitness,
    StateTransformationGeneratorDeclaration,
    validate_atomic_refinement,
    validate_boundary_history_equivalence,
    validate_constitutive_generator_link,
    validate_extent_definition,
    validate_finite_reconstruction,
    validate_hybrid_activation,
    validate_quantity_participation_generator,
    validate_regularity_and_reparameterization_witness,
    validate_state_transformation_generator,
)
from ebu_framework.canonical import encode_ecj1, parse_ecj1
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.hashing import compute_object_content_hash
from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.primitives import (
    ClaimStatus,
    Quantity,
    ResolutionDetail,
    ResolutionState,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTRACT_PATH = _REPO_ROOT / "atomic_interaction_declaration_contract.json"
_VALIDATION_PATH = (
    _REPO_ROOT / "atomic_interaction_declaration_validation_contract.json"
)
_MANIFEST_PATH = (
    _REPO_ROOT / "atomic_interaction_declaration_predecessor_manifest.json"
)
_FIXTURE_PATH = _REPO_ROOT / "tests/framework/fixtures/atomic_declaration_v1.json"
_ATOMIC_PATH = _REPO_ROOT / "src/ebu_framework/atomic.py"


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON name: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _load_json(path: Path) -> object:
    payload = path.read_bytes()
    if not payload.endswith(b"\n") or payload.endswith(b"\n\n"):
        raise AssertionError(f"{path} does not have exactly one final LF")
    return json.loads(
        payload,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )


_CONTRACT = _load_json(_CONTRACT_PATH)
_VALIDATION = _load_json(_VALIDATION_PATH)
_MANIFEST = _load_json(_MANIFEST_PATH)
_FIXTURE = _load_json(_FIXTURE_PATH)
assert type(_CONTRACT) is dict
assert type(_VALIDATION) is dict
assert type(_MANIFEST) is dict
assert type(_FIXTURE) is list

_D1_DECLARATION_ROWS = [
    row for row in _CONTRACT["declarations"] if row["stage"] == "D1"
]
_D1_VALIDATOR_ROWS = [
    row for row in _CONTRACT["validators"] if row["stage"] == "D1"
]
_D1_TYPES = (
    ExtentDefinition,
    AtomicRefinementDeclaration,
    QuantityParticipationGeneratorDeclaration,
    StateTransformationGeneratorDeclaration,
    ConstitutiveGeneratorLink,
    RegularityAndReparameterizationWitness,
    HybridActivationDeclaration,
    FiniteReconstructionWitness,
    BoundaryHistoryEquivalenceWitness,
)
_D1_VALIDATORS = (
    validate_extent_definition,
    validate_atomic_refinement,
    validate_quantity_participation_generator,
    validate_state_transformation_generator,
    validate_constitutive_generator_link,
    validate_regularity_and_reparameterization_witness,
    validate_hybrid_activation,
    validate_finite_reconstruction,
    validate_boundary_history_equivalence,
)
_TYPE_BY_NAME = {runtime_type.__name__: runtime_type for runtime_type in _D1_TYPES}
_VALIDATOR_BY_DECLARATION = dict(zip(_TYPE_BY_NAME, _D1_VALIDATORS, strict=True))
_SPEC_BY_NAME = {row["name"]: row for row in _D1_DECLARATION_ROWS}
_NONCLAIMS = tuple(_CONTRACT["closed_nonclaim_codes"])
_STATE_ROLES = tuple(_CONTRACT["closed_state_role_codes"])
_OBSERVABLES = tuple(_CONTRACT["closed_boundary_observable_codes"])
_REGULARITY = tuple(_CONTRACT["closed_regularity_codes"])


def _hash_value(label: str) -> ObjectContentHash:
    return ObjectContentHash("sha256:" + hashlib.sha256(label.encode()).hexdigest())


def _ref(label: str) -> ObjectRef:
    token = hashlib.sha256(label.encode()).hexdigest()[:24]
    return ObjectRef(
        object_id=ScientificId(f"ebu:test:d1:{token}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=_hash_value("ref:" + label),
    )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _record_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _ordered_refs(*values: ObjectRef) -> tuple[ObjectRef, ...]:
    return tuple(sorted(values, key=_ref_key))


def _ordered_codes(values: tuple[str, ...], domain: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(values, key=domain.index))


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


_RECORD_ORDINAL = 0


def _make(runtime_type: type, **data: object) -> object:
    global _RECORD_ORDINAL
    _RECORD_ORDINAL += 1
    spec = _SPEC_BY_NAME[runtime_type.__name__]
    payload = {
        name: _project(data[name])
        for name in spec["field_order"]
        if name != "envelope"
    }
    object_id = ScientificId(
        f"ebu:d1-test:record:{runtime_type.__name__.lower()}-{_RECORD_ORDINAL}"
    )
    kind = spec["object_kind_id"]
    schema_id = ScientificId(spec["schema_id"])
    version = SemanticVersion("1.0.0")
    content_hash = compute_object_content_hash(
        object_id=object_id,
        object_kind=kind,
        schema_id=schema_id,
        schema_version=version,
        object_version=version,
        authority_refs=(),
        supersedes_ref=None,
        object_content_payload=payload,
    )
    envelope = CommonObjectEnvelope(
        object_id=object_id,
        object_kind_id=ScientificId(kind),
        schema_id=schema_id,
        schema_version=version,
        object_version=version,
        authority_refs=(),
        supersedes_ref=Applicability.NOT_APPLICABLE,
        object_content_payload=bytes(encode_ecj1(payload)),
        object_content_hash=content_hash,
        lifecycle_status=LifecycleStatus.DRAFT,
        record_metadata_ref=Applicability.NOT_APPLICABLE,
    )
    return runtime_type(envelope=envelope, **data)


def _record_data(record: object) -> dict[str, object]:
    return {
        field.name: getattr(record, field.name)
        for field in fields(record)
        if field.name != "envelope"
    }


def _replace_record(record: object, **changes: object) -> object:
    data = _record_data(record)
    data.update(changes)
    return _make(type(record), **data)


def _with_envelope(record: object, envelope: CommonObjectEnvelope) -> object:
    return type(record)(envelope=envelope, **_record_data(record))


def _corrupt_payload(record: object) -> object:
    envelope = record.envelope  # type: ignore[attr-defined]
    payload = {"corrupt": True}
    content_hash = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=None,
        object_content_payload=payload,
    )
    return _with_envelope(
        record,
        replace(
            envelope,
            object_content_payload=bytes(encode_ecj1(payload)),
            object_content_hash=content_hash,
        ),
    )


def _corrupt_hash(record: object) -> object:
    return _with_envelope(
        record,
        replace(record.envelope, object_content_hash=_hash_value("corrupt-hash")),  # type: ignore[attr-defined]
    )


def _resolution(
    *,
    completed: tuple[ObjectRef, ...] = (),
    missing: tuple[ObjectRef, ...] = (),
    state: ResolutionState = ResolutionState.PRESENT,
) -> ResolutionDetail:
    return ResolutionDetail(
        state=state,
        present_value_ref=Applicability.NOT_APPLICABLE,
        completed_part_refs=completed,
        missing_part_refs=missing,
        due_condition_ref=Applicability.NOT_APPLICABLE,
        failure=Applicability.NOT_APPLICABLE,
        boundary_edge_ref=Applicability.NOT_APPLICABLE,
        reason_ref=Applicability.NOT_APPLICABLE,
    )


def _quantity(
    magnitude: int,
    unit: ObjectRef,
    dimension: ObjectRef,
    boundary: ObjectRef,
) -> Quantity:
    return Quantity(
        magnitude=IntegerV1(magnitude),
        unit_ref=unit,
        dimension_ref=dimension,
        boundary_ref=boundary,
        resource_type_ref=Applicability.NOT_APPLICABLE,
        service_type_ref=Applicability.NOT_APPLICABLE,
        region_ref=Applicability.NOT_APPLICABLE,
        time_basis_ref=Applicability.NOT_APPLICABLE,
        sign_convention_ref=Applicability.NOT_APPLICABLE,
        uncertainty_ref=Applicability.NOT_APPLICABLE,
        resolution=_resolution(),
    )


def _base_world() -> dict[str, object]:
    action = _ref("action")
    coordinate = _ref("extent-coordinate")
    unit = _ref("extent-unit")
    dimension = _ref("extent-dimension")
    boundary = _ref("boundary")
    domain = _ref("domain")
    topology = _ref("topology")
    carrier = _ref("carrier")
    provenance = _ordered_refs(_ref("provenance-a"), _ref("provenance-b"))
    lower = _quantity(0, unit, dimension, boundary)
    upper = _quantity(10, unit, dimension, boundary)
    extent = _make(
        ExtentDefinition,
        extent_family="TYPED_CARRIER_QUANTITY",
        action_family_ref=action,
        coordinate_ref=coordinate,
        coordinate_unit_ref=unit,
        coordinate_dimension_ref=dimension,
        generator_codomain_ref=_ref("generator-codomain"),
        domain_ref=domain,
        topology_ref=topology,
        orientation="DECLARED_FORWARD_CARRIER",
        divisibility="DECLARED_NONATOMIC",
        carrier_or_bundle_ref=carrier,
        clock_or_order_ref=Applicability.NOT_APPLICABLE,
        path_or_process_ref=Applicability.NOT_APPLICABLE,
        lower_bound=lower,
        upper_bound=upper,
        interval_closure="CLOSED",
        reversible_flow_ref=_ref("reversible-flow"),
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_UNIVERSAL_DIVISIBILITY",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    refinement = _make(
        AtomicRefinementDeclaration,
        extent_ref=_record_ref(extent),
        action_family_ref=action,
        base_state_ref=_ref("base-state"),
        finite_transformation_ref=_ref("finite-transformation"),
        generator_ref=_ref("refinement-generator"),
        epsilon_unit_ref=unit,
        topology_ref=topology,
        right_derivative_status="EXISTS",
        derivative_witness_ref=_ref("derivative-witness"),
        nonexistence_witness_ref=Applicability.NOT_APPLICABLE,
        finite_transaction_preserved=True,
        indivisible_entity_refs=_ordered_refs(_ref("indivisible-a"), _ref("indivisible-b")),
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            ("NO_EMPIRICAL_VALIDATION", "NO_MINIMAL_TRANSACTION", "NO_RUNTIME_BEHAVIOR"),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    input_refs = _ordered_refs(_ref("quantity-a"), _ref("quantity-b"))
    output_refs = _ordered_refs(_ref("quantity-c"), _ref("quantity-d"))
    accounts = _ordered_refs(_ref("account-a"), _ref("account-b"))
    value_unit = _ref("value-unit")
    value_dimension = _ref("value-dimension")
    quantity_generator = _make(
        QuantityParticipationGeneratorDeclaration,
        extent_ref=_record_ref(extent),
        action_definition_ref=action,
        carrier_ref=carrier,
        boundary_ref=boundary,
        generator_contract_ref=_ref("quantity-generator-contract"),
        input_quantity_refs=input_refs,
        output_quantity_refs=output_refs,
        value_unit_ref=value_unit,
        value_dimension_ref=value_dimension,
        extent_unit_ref=unit,
        extent_dimension_ref=dimension,
        generator_unit_ref=_ref("value-per-extent-unit"),
        generator_dimension_ref=_ref("value-per-extent-dimension"),
        orientation="FORWARD",
        domain_ref=domain,
        topology_ref=topology,
        sign_convention_ref=_ref("sign-convention"),
        process_account_refs=accounts,
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    coordinates = _ordered_refs(_ref("state-coordinate-a"), _ref("state-coordinate-b"))
    derivative_units = {
        coordinates[0]: _ref("derivative-unit-a"),
        coordinates[1]: _ref("derivative-unit-b"),
    }
    derivative_dimensions = {
        coordinates[0]: _ref("derivative-dimension-a"),
        coordinates[1]: _ref("derivative-dimension-b"),
    }
    component_rows = tuple(
        (coordinate_ref, derivative_units[coordinate_ref], derivative_dimensions[coordinate_ref])
        for coordinate_ref in coordinates
    )
    state_generator = _make(
        StateTransformationGeneratorDeclaration,
        extent_ref=_record_ref(extent),
        action_definition_ref=action,
        augmented_state_schema_ref=_ref("augmented-state-schema"),
        boundary_ref=boundary,
        generator_contract_ref=_ref("state-generator-contract"),
        state_coordinate_refs=coordinates,
        derivative_component_units=component_rows,
        represented_state_role_codes=_STATE_ROLES,
        inapplicable_state_role_codes=(),
        state_completeness_witness_ref=_ref("state-completeness"),
        extent_unit_ref=unit,
        extent_dimension_ref=dimension,
        orientation="FORWARD",
        domain_ref=domain,
        topology_ref=topology,
        process_account_refs=accounts,
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_UNIVERSAL_MINIMAL_STATE",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    all_quantities = _ordered_refs(*(input_refs + output_refs))
    unit_rows = tuple(
        (
            quantity_ref,
            coordinates[index % len(coordinates)],
            derivative_units[coordinates[index % len(coordinates)]],
            Applicability.NOT_APPLICABLE,
        )
        for index, quantity_ref in enumerate(all_quantities)
    )
    link = _make(
        ConstitutiveGeneratorLink,
        quantity_generator_ref=_record_ref(quantity_generator),
        state_generator_ref=_record_ref(state_generator),
        extent_ref=_record_ref(extent),
        boundary_ref=boundary,
        link_kind="COMBINED",
        map_contract_ref=_ref("link-map"),
        quantity_refs=all_quantities,
        state_coordinate_refs=coordinates,
        unit_relation_rows=unit_rows,
        orientation="FORWARD",
        domain_ref=domain,
        process_account_refs=accounts,
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    target_unit = _ref("target-unit")
    target_extent = _replace_record(
        extent,
        coordinate_ref=_ref("target-coordinate"),
        coordinate_unit_ref=target_unit,
        lower_bound=_quantity(0, target_unit, dimension, boundary),
        upper_bound=_quantity(20, target_unit, dimension, boundary),
    )
    regularity = _make(
        RegularityAndReparameterizationWitness,
        generator_ref=_record_ref(quantity_generator),
        source_extent_ref=_record_ref(extent),
        target_extent_ref=_record_ref(target_extent),
        reparameterization_kind="POSITIVE_AFFINE",
        source_coordinate_ref=coordinate,
        target_coordinate_ref=target_extent.coordinate_ref,
        source_unit_ref=unit,
        target_unit_ref=target_unit,
        map_ref=_ref("parameter-map"),
        inverse_map_ref=_ref("inverse-map"),
        derivative_scale=IntegerV1(2),
        regularity_codes=_ordered_codes(("C1",), _REGULARITY),
        domain_ref=domain,
        topology_ref=topology,
        orientation_preserved=True,
        generator_claim="AUTOMATIC_UNIT_INHERITANCE",
        clock_added_to_state=False,
        transformed_generator_ref=_ref("transformed-generator"),
        density_and_limits_transform_together=True,
        integrated_change_invariant=True,
        witness_ref=_ref("chain-rule-witness"),
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(
            ("NO_EMPIRICAL_VALIDATION", "NO_RUNTIME_BEHAVIOR", "NO_PHYSICAL_PROPAGATION"),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    quantity_unit = _ref("activation-quantity-unit")
    quantity_dimension = _ref("activation-quantity-dimension")
    hybrid = _make(
        HybridActivationDeclaration,
        action_definition_ref=action,
        state_generator_ref=_record_ref(state_generator),
        boundary_ref=boundary,
        mode_schema_ref=_ref("mode-schema"),
        inactive_mode_ref=_ref("inactive-mode"),
        active_mode_refs=_ordered_refs(_ref("active-mode-a"), _ref("active-mode-b")),
        quantity_coordinate_ref=_ref("quantity-coordinate"),
        off_quantity=_quantity(0, quantity_unit, quantity_dimension, boundary),
        minimum_active_quantity=_quantity(2, quantity_unit, quantity_dimension, boundary),
        maximum_active_quantity=_quantity(10, quantity_unit, quantity_dimension, boundary),
        activation_burden=_quantity(1, quantity_unit, quantity_dimension, boundary),
        activation_transition_ref=_ref("activation-transition"),
        within_mode_flow_ref=_ref("within-mode-flow"),
        jump_flow_order="ACTIVATION_FLOW_DEACTIVATION",
        fixed_cost_account_ref=_ref("fixed-cost-account"),
        process_account_refs=accounts,
        commitment_state_ref=_ref("commitment-state"),
        fixed_cost_counted_once=True,
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    finite = _make(
        FiniteReconstructionWitness,
        state_generator_ref=_record_ref(state_generator),
        extent_ref=_record_ref(extent),
        boundary_ref=boundary,
        initial_state_ref=_ref("initial-state"),
        finite_transformation_ref=_ref("finite-reconstruction"),
        reconstruction_kind="LINEAR_SEMIGROUP",
        zero_extent_identity=True,
        domain_ref=domain,
        operator_domain_ref=_ref("operator-domain"),
        regularity_witness_ref=_ref("regularity-witness"),
        existence_witness_ref=_ref("existence-witness"),
        uniqueness_witness_ref=_ref("uniqueness-witness"),
        ordered_evolution_ref=Applicability.NOT_APPLICABLE,
        hybrid_activation_ref=Applicability.NOT_APPLICABLE,
        finite_extent=_quantity(5, unit, dimension, boundary),
        expansion_form="T0_IDENTITY_AND_FIRST_ORDER_REMAINDER",
        remainder_ref=_ref("remainder"),
        process_account_refs=accounts,
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(
            ("NO_EMPIRICAL_VALIDATION", "NO_RUNTIME_BEHAVIOR", "NO_PHYSICAL_PROPAGATION"),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    burden = _ref("preserve-burden")
    conservation = _ref("preserve-conservation")
    loss = _ref("preserve-loss")
    commitment = _ref("preserve-commitment")
    settlement = _ref("preserve-settlement")
    preserved_accounts = _ordered_refs(_ref("preserve-account-a"), _ref("preserve-account-b"))
    topology_exports = _ordered_refs(_ref("topology-export"))
    completed = _ordered_refs(
        burden,
        conservation,
        loss,
        commitment,
        settlement,
        *preserved_accounts,
        *topology_exports,
    )
    boundary_history = _make(
        BoundaryHistoryEquivalenceWitness,
        detailed_boundary_ref=_ref("detailed-boundary"),
        parent_boundary_ref=_ref("parent-boundary"),
        detailed_state_schema_ref=_ref("detailed-state-schema"),
        parent_state_schema_ref=_ref("parent-state-schema"),
        initial_state_relation_ref=_ref("initial-state-relation"),
        admitted_history_contract_ref=_ref("admitted-history"),
        horizon_ref=_ref("horizon"),
        equivalence_kind="BISIMULATION",
        evolution_relation_ref=_ref("evolution-relation"),
        observable_codes=_ordered_codes(
            ("TYPED_FLOW", "LOSS", "PENDING_COMMITMENT", "SETTLEMENT_VISIBLE_RECORD"),
            _OBSERVABLES,
        ),
        burden_preservation_ref=burden,
        conservation_preservation_ref=conservation,
        loss_preservation_ref=loss,
        commitment_preservation_ref=commitment,
        settlement_preservation_ref=settlement,
        process_account_preservation_refs=preserved_accounts,
        hidden_state_relation_preserved=True,
        all_admitted_histories_covered=True,
        snapshot_equality_only=False,
        one_state_generator_equality_only=False,
        internal_topology_export_refs=topology_exports,
        resolution=_resolution(completed=completed),
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED",
                "NO_RUNTIME_BEHAVIOR",
            ),
            _NONCLAIMS,
        ),
        provenance_refs=provenance,
    )
    return {
        "ExtentDefinition": extent,
        "AtomicRefinementDeclaration": refinement,
        "QuantityParticipationGeneratorDeclaration": quantity_generator,
        "StateTransformationGeneratorDeclaration": state_generator,
        "ConstitutiveGeneratorLink": link,
        "RegularityAndReparameterizationWitness": regularity,
        "HybridActivationDeclaration": hybrid,
        "FiniteReconstructionWitness": finite,
        "BoundaryHistoryEquivalenceWitness": boundary_history,
        "target_extent": target_extent,
        "finite_hybrid_arg": Applicability.NOT_APPLICABLE,
    }


def _set_record(world: dict[str, object], declaration: str, record: object) -> dict[str, object]:
    changed = dict(world)
    changed[declaration] = record
    return changed


def _call_validator(world: dict[str, object], declaration: str) -> None:
    record = world[declaration]
    if declaration == "ExtentDefinition":
        validate_extent_definition(record)  # type: ignore[arg-type]
    elif declaration == "AtomicRefinementDeclaration":
        validate_atomic_refinement(record, world["ExtentDefinition"])  # type: ignore[arg-type]
    elif declaration == "QuantityParticipationGeneratorDeclaration":
        validate_quantity_participation_generator(record, world["ExtentDefinition"])  # type: ignore[arg-type]
    elif declaration == "StateTransformationGeneratorDeclaration":
        validate_state_transformation_generator(record, world["ExtentDefinition"])  # type: ignore[arg-type]
    elif declaration == "ConstitutiveGeneratorLink":
        validate_constitutive_generator_link(
            record,  # type: ignore[arg-type]
            world["QuantityParticipationGeneratorDeclaration"],  # type: ignore[arg-type]
            world["StateTransformationGeneratorDeclaration"],  # type: ignore[arg-type]
        )
    elif declaration == "RegularityAndReparameterizationWitness":
        validate_regularity_and_reparameterization_witness(
            record,  # type: ignore[arg-type]
            world["ExtentDefinition"],  # type: ignore[arg-type]
            world["target_extent"],  # type: ignore[arg-type]
            world["QuantityParticipationGeneratorDeclaration"],  # type: ignore[arg-type]
        )
    elif declaration == "HybridActivationDeclaration":
        validate_hybrid_activation(
            record, world["StateTransformationGeneratorDeclaration"]  # type: ignore[arg-type]
        )
    elif declaration == "FiniteReconstructionWitness":
        validate_finite_reconstruction(
            record,  # type: ignore[arg-type]
            world["StateTransformationGeneratorDeclaration"],  # type: ignore[arg-type]
            world["finite_hybrid_arg"],  # type: ignore[arg-type]
        )
    else:
        validate_boundary_history_equivalence(record)  # type: ignore[arg-type]


def _extent_variant(record: ExtentDefinition, family: str) -> ExtentDefinition:
    changes: dict[str, object] = {
        "extent_family": family,
        "carrier_or_bundle_ref": Applicability.NOT_APPLICABLE,
        "clock_or_order_ref": Applicability.NOT_APPLICABLE,
        "path_or_process_ref": Applicability.NOT_APPLICABLE,
    }
    if family == "PHYSICAL_TIME":
        changes.update(orientation="INCREASING_CLOCK", clock_or_order_ref=_ref("clock"))
    elif family == "PROCESS_OR_ROUTE_EXTENT":
        changes.update(
            orientation="DECLARED_FORWARD_PROCESS", path_or_process_ref=_ref("process")
        )
    elif family == "TYPED_CARRIER_QUANTITY":
        changes.update(
            orientation="DECLARED_FORWARD_CARRIER", carrier_or_bundle_ref=_ref("carrier")
        )
    else:
        changes.update(
            orientation="ZERO_TO_ONE_PARTICIPATION",
            lower_bound=_quantity(
                0,
                record.coordinate_unit_ref,
                record.coordinate_dimension_ref,
                record.lower_bound.boundary_ref,  # type: ignore[union-attr]
            ),
            upper_bound=_quantity(
                1,
                record.coordinate_unit_ref,
                record.coordinate_dimension_ref,
                record.upper_bound.boundary_ref,  # type: ignore[union-attr]
            ),
        )
    return _replace_record(record, **changes)  # type: ignore[return-value]


def _regularity_variant(
    record: RegularityAndReparameterizationWitness, kind: str, claim: str | None = None
) -> RegularityAndReparameterizationWitness:
    changes: dict[str, object] = {"reparameterization_kind": kind}
    if kind == "POSITIVE_AFFINE":
        changes.update(
            orientation_preserved=True,
            generator_claim=claim or "AUTOMATIC_UNIT_INHERITANCE",
            inverse_map_ref=_ref("inverse-affine"),
            derivative_scale=IntegerV1(2),
            transformed_generator_ref=_ref("transformed-affine"),
            regularity_codes=_ordered_codes(("C1",), _REGULARITY),
        )
    elif kind == "POSITIVE_NONLINEAR_C1":
        changes.update(
            orientation_preserved=True,
            generator_claim=claim or "EXPLICIT_CHAIN_RULE_WITNESS",
            inverse_map_ref=_ref("inverse-nonlinear"),
            derivative_scale=IntegerV1(1),
            transformed_generator_ref=_ref("transformed-nonlinear"),
            regularity_codes=_ordered_codes(("C1",), _REGULARITY),
        )
    elif kind == "ORIENTATION_REVERSING":
        changes.update(
            orientation_preserved=False,
            generator_claim=claim or "GENERATOR_CLAIM_REFUSED",
            transformed_generator_ref=(
                _ref("transformed-reverse")
                if claim == "SEPARATE_REVERSIBLE_FLOW_REQUIRED"
                else Applicability.NOT_APPLICABLE
            ),
        )
    else:
        changes.update(
            orientation_preserved=True,
            generator_claim="GENERATOR_CLAIM_REFUSED",
            transformed_generator_ref=Applicability.NOT_APPLICABLE,
        )
    return _replace_record(record, **changes)  # type: ignore[return-value]


def _finite_variant(
    world: dict[str, object], kind: str
) -> tuple[FiniteReconstructionWitness, HybridActivationDeclaration | Applicability]:
    record = world["FiniteReconstructionWitness"]
    assert type(record) is FiniteReconstructionWitness
    changes: dict[str, object] = {
        "reconstruction_kind": kind,
        "ordered_evolution_ref": Applicability.NOT_APPLICABLE,
        "hybrid_activation_ref": Applicability.NOT_APPLICABLE,
    }
    hybrid_arg: HybridActivationDeclaration | Applicability = Applicability.NOT_APPLICABLE
    if kind == "LINEAR_SEMIGROUP":
        changes["operator_domain_ref"] = _ref("operator-domain-linear")
    elif kind == "NONLINEAR_FLOW":
        changes["operator_domain_ref"] = Applicability.NOT_APPLICABLE
    elif kind == "ORDERED_NONAUTONOMOUS_EVOLUTION":
        changes["ordered_evolution_ref"] = _ref("ordered-evolution")
    else:
        hybrid_arg = world["HybridActivationDeclaration"]  # type: ignore[assignment]
        changes["hybrid_activation_ref"] = _record_ref(hybrid_arg)
    return _replace_record(record, **changes), hybrid_arg  # type: ignore[return-value]


def _enum_world(
    world: dict[str, object], declaration: str, field_name: str, value: str
) -> dict[str, object]:
    record = world[declaration]
    if declaration == "ExtentDefinition":
        assert type(record) is ExtentDefinition
        if field_name == "extent_family":
            return _set_record(world, declaration, _extent_variant(record, value))
        if field_name == "orientation":
            family = {
                "INCREASING_CLOCK": "PHYSICAL_TIME",
                "DECLARED_FORWARD_PROCESS": "PROCESS_OR_ROUTE_EXTENT",
                "DECLARED_FORWARD_CARRIER": "TYPED_CARRIER_QUANTITY",
                "ZERO_TO_ONE_PARTICIPATION": "DIMENSIONLESS_PARTICIPATION",
            }[value]
            return _set_record(world, declaration, _extent_variant(record, family))
        if field_name == "interval_closure" and value == "UNBOUNDED":
            changed = _replace_record(
                record,
                interval_closure=value,
                lower_bound=Applicability.NOT_APPLICABLE,
                upper_bound=Applicability.NOT_APPLICABLE,
            )
            return _set_record(world, declaration, changed)
    if declaration == "AtomicRefinementDeclaration" and field_name == "right_derivative_status":
        if value == "EXISTS":
            changed = _replace_record(
                record,
                right_derivative_status=value,
                generator_ref=_ref("enum-generator"),
                derivative_witness_ref=_ref("enum-derivative"),
                nonexistence_witness_ref=Applicability.NOT_APPLICABLE,
            )
        elif value == "DOES_NOT_EXIST":
            changed = _replace_record(
                record,
                right_derivative_status=value,
                generator_ref=Applicability.NOT_APPLICABLE,
                derivative_witness_ref=Applicability.NOT_APPLICABLE,
                nonexistence_witness_ref=_ref("enum-nonexistence"),
            )
        else:
            changed = _replace_record(
                record,
                right_derivative_status=value,
                generator_ref=Applicability.NOT_APPLICABLE,
                derivative_witness_ref=Applicability.NOT_APPLICABLE,
                nonexistence_witness_ref=Applicability.NOT_APPLICABLE,
            )
        return _set_record(world, declaration, changed)
    if declaration == "RegularityAndReparameterizationWitness":
        assert type(record) is RegularityAndReparameterizationWitness
        if field_name == "reparameterization_kind":
            return _set_record(world, declaration, _regularity_variant(record, value))
        if field_name == "generator_claim":
            if value in {"AUTOMATIC_UNIT_INHERITANCE", "EXPLICIT_CHAIN_RULE_WITNESS"}:
                changed = _regularity_variant(record, "POSITIVE_AFFINE", value)
            elif value == "SEPARATE_REVERSIBLE_FLOW_REQUIRED":
                changed = _regularity_variant(record, "ORIENTATION_REVERSING", value)
            else:
                changed = _regularity_variant(record, "SINGULAR_OR_NONINVERTIBLE", value)
            return _set_record(world, declaration, changed)
    if declaration == "FiniteReconstructionWitness" and field_name == "reconstruction_kind":
        changed, hybrid_arg = _finite_variant(world, value)
        result = _set_record(world, declaration, changed)
        result["finite_hybrid_arg"] = hybrid_arg
        return result
    if declaration == "ConstitutiveGeneratorLink" and field_name == "orientation":
        quantity_generator = _replace_record(
            world["QuantityParticipationGeneratorDeclaration"], orientation=value
        )
        state_generator = _replace_record(
            world["StateTransformationGeneratorDeclaration"], orientation=value
        )
        changed = _replace_record(
            record,
            orientation=value,
            quantity_generator_ref=_record_ref(quantity_generator),
            state_generator_ref=_record_ref(state_generator),
        )
        result = _set_record(world, declaration, changed)
        result["QuantityParticipationGeneratorDeclaration"] = quantity_generator
        result["StateTransformationGeneratorDeclaration"] = state_generator
        return result
    return _set_record(world, declaration, _replace_record(record, **{field_name: value}))


def _applicability_world(
    world: dict[str, object], declaration: str, field_name: str
) -> dict[str, object]:
    record = world[declaration]
    if declaration == "ExtentDefinition":
        assert type(record) is ExtentDefinition
        if field_name in {"lower_bound", "upper_bound"}:
            changed = _replace_record(
                record,
                lower_bound=Applicability.NOT_APPLICABLE,
                upper_bound=Applicability.NOT_APPLICABLE,
                interval_closure="UNBOUNDED",
            )
        elif field_name == "carrier_or_bundle_ref":
            changed = _extent_variant(record, "PHYSICAL_TIME")
        elif field_name in {"clock_or_order_ref", "path_or_process_ref"}:
            changed = _extent_variant(record, "TYPED_CARRIER_QUANTITY")
        else:
            changed = _replace_record(record, **{field_name: Applicability.NOT_APPLICABLE})
        return _set_record(world, declaration, changed)
    if declaration == "AtomicRefinementDeclaration":
        if field_name in {"generator_ref", "derivative_witness_ref"}:
            changed = _replace_record(
                record,
                generator_ref=Applicability.NOT_APPLICABLE,
                derivative_witness_ref=Applicability.NOT_APPLICABLE,
                nonexistence_witness_ref=_ref("app-nonexistence"),
                right_derivative_status="DOES_NOT_EXIST",
            )
        else:
            changed = _replace_record(record, **{field_name: Applicability.NOT_APPLICABLE})
        return _set_record(world, declaration, changed)
    if declaration == "RegularityAndReparameterizationWitness":
        changed = _regularity_variant(record, "SINGULAR_OR_NONINVERTIBLE")  # type: ignore[arg-type]
        changed = _replace_record(changed, **{field_name: Applicability.NOT_APPLICABLE})
        return _set_record(world, declaration, changed)
    if declaration == "FiniteReconstructionWitness":
        if field_name == "operator_domain_ref":
            changed, hybrid_arg = _finite_variant(world, "NONLINEAR_FLOW")
        else:
            changed, hybrid_arg = _finite_variant(world, "LINEAR_SEMIGROUP")
            changed = _replace_record(changed, **{field_name: Applicability.NOT_APPLICABLE})
        result = _set_record(world, declaration, changed)
        result["finite_hybrid_arg"] = hybrid_arg
        return result
    return _set_record(
        world,
        declaration,
        _replace_record(record, **{field_name: Applicability.NOT_APPLICABLE}),
    )


def _quantity_change(quantity: Quantity, **changes: object) -> Quantity:
    return replace(quantity, **changes)


def _failure_world(
    world: dict[str, object], declaration: str, code: str
) -> dict[str, object]:
    record = world[declaration]
    if code == "I3_OBJECT_CONTENT_MISMATCH":
        return _set_record(world, declaration, _corrupt_payload(record))
    if code == "I3_COLLECTION_ORDER_INVALID":
        return _set_record(
            world,
            declaration,
            _replace_record(record, provenance_refs=tuple(reversed(record.provenance_refs))),  # type: ignore[attr-defined]
        )
    if code == "I3_DUPLICATE_MEMBER":
        provenance = record.provenance_refs  # type: ignore[attr-defined]
        return _set_record(
            world,
            declaration,
            _replace_record(record, provenance_refs=(provenance[0], provenance[0])),
        )
    if code == "IMPLICIT_ABSENCE_FORBIDDEN":
        field_name = {
            "ExtentDefinition": "reversible_flow_ref",
            "AtomicRefinementDeclaration": "generator_ref",
            "ConstitutiveGeneratorLink": None,
            "RegularityAndReparameterizationWitness": "inverse_map_ref",
            "FiniteReconstructionWitness": "operator_domain_ref",
            "BoundaryHistoryEquivalenceWitness": "settlement_preservation_ref",
        }[declaration]
        if field_name is None:
            rows = list(record.unit_relation_rows)  # type: ignore[attr-defined]
            rows[0] = rows[0][:3] + (Applicability.APPLICABLE,)
            changed = _replace_record(record, unit_relation_rows=tuple(rows))
        else:
            changed = _replace_record(record, **{field_name: Applicability.APPLICABLE})
        return _set_record(world, declaration, changed)
    if code == "UNIT_MISMATCH":
        wrong = _ref("wrong-unit")
        if declaration == "ExtentDefinition":
            changed = _replace_record(
                record, lower_bound=_quantity_change(record.lower_bound, unit_ref=wrong)  # type: ignore[attr-defined,arg-type]
            )
        elif declaration == "AtomicRefinementDeclaration":
            changed = _replace_record(record, epsilon_unit_ref=wrong)
        elif declaration in {
            "QuantityParticipationGeneratorDeclaration",
            "StateTransformationGeneratorDeclaration",
        }:
            changed = _replace_record(record, extent_unit_ref=wrong)
        elif declaration == "ConstitutiveGeneratorLink":
            qg = world["QuantityParticipationGeneratorDeclaration"]
            result = dict(world)
            result["QuantityParticipationGeneratorDeclaration"] = _replace_record(
                qg, extent_unit_ref=wrong
            )
            return result
        elif declaration == "RegularityAndReparameterizationWitness":
            changed = _replace_record(record, source_unit_ref=wrong)
        elif declaration == "HybridActivationDeclaration":
            changed = _replace_record(
                record,
                minimum_active_quantity=_quantity_change(
                    record.minimum_active_quantity, unit_ref=wrong  # type: ignore[attr-defined]
                ),
            )
        else:
            changed = _replace_record(
                record,
                finite_extent=_quantity_change(record.finite_extent, unit_ref=wrong),  # type: ignore[attr-defined]
            )
        return _set_record(world, declaration, changed)
    if code == "DIMENSION_MISMATCH":
        wrong = _ref("wrong-dimension")
        if declaration == "ExtentDefinition":
            changed = _replace_record(
                record,
                lower_bound=_quantity_change(record.lower_bound, dimension_ref=wrong),  # type: ignore[attr-defined,arg-type]
            )
        elif declaration in {
            "QuantityParticipationGeneratorDeclaration",
            "StateTransformationGeneratorDeclaration",
        }:
            changed = _replace_record(record, extent_dimension_ref=wrong)
        elif declaration == "ConstitutiveGeneratorLink":
            qg = world["QuantityParticipationGeneratorDeclaration"]
            result = dict(world)
            result["QuantityParticipationGeneratorDeclaration"] = _replace_record(
                qg, extent_dimension_ref=wrong
            )
            return result
        else:
            changed = _replace_record(
                record,
                minimum_active_quantity=_quantity_change(
                    record.minimum_active_quantity, dimension_ref=wrong  # type: ignore[attr-defined]
                ),
            )
        return _set_record(world, declaration, changed)
    if code == "EXTENT_DIVISIBILITY_UNDECLARED":
        changed = _extent_variant(record, "PROCESS_OR_ROUTE_EXTENT")  # type: ignore[arg-type]
        changed = _replace_record(
            changed,
            divisibility="DECLARED_REFINABLE_IMMUTABLE_BUNDLE",
            carrier_or_bundle_ref=Applicability.NOT_APPLICABLE,
        )
    elif code == "EXTENT_DECLARATION_INVALID":
        changed = _replace_record(record, orientation="INCREASING_CLOCK")
    elif code == "ATOMIC_REFINEMENT_INVALID":
        changed = _replace_record(record, finite_transaction_preserved=False)
    elif code == "GENERATOR_DECLARATION_INVALID":
        changed = _replace_record(record, domain_ref=_ref("wrong-domain"))
    elif code == "AUGMENTED_STATE_INCOMPLETE":
        changed = _replace_record(
            record,
            represented_state_role_codes=_STATE_ROLES[:-1],
            inapplicable_state_role_codes=(),
        )
    elif code == "GENERATOR_LINK_INVALID":
        changed = _replace_record(record, boundary_ref=_ref("wrong-boundary"))
    elif code == "REPARAMETERIZATION_WITNESS_INVALID":
        changed = _replace_record(
            record,
            reparameterization_kind="POSITIVE_NONLINEAR_C1",
            generator_claim="AUTOMATIC_UNIT_INHERITANCE",
        )
    elif code == "HYBRID_ACTIVATION_INVALID":
        changed = _replace_record(record, fixed_cost_counted_once=False)
    elif code == "FIXED_ACTIVATION_ACCOUNT_DUPLICATED":
        changed = _replace_record(
            record,
            process_account_refs=_ordered_refs(
                record.fixed_cost_account_ref, _ref("other-account")  # type: ignore[attr-defined]
            ),
        )
    elif code == "RECONSTRUCTION_CLAIM_UNSUPPORTED":
        changed = _replace_record(record, zero_extent_identity=False)
    elif code == "BOUNDARY_HISTORY_EQUIVALENCE_INVALID":
        changed = _replace_record(record, snapshot_equality_only=True)
    elif code == "BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE":
        changed = _replace_record(record, hidden_state_relation_preserved=False)
    else:
        raise AssertionError(f"unsupported failure mutation {declaration} {code}")
    return _set_record(world, declaration, changed)


def _semantic_world(
    world: dict[str, object], declaration: str, mutation: str
) -> dict[str, object]:
    record = world[declaration]
    extent_semantics = {
        "PHYSICAL_TIME_VALID": "PHYSICAL_TIME",
        "PROCESS_ROUTE_VALID": "PROCESS_OR_ROUTE_EXTENT",
        "TYPED_CARRIER_VALID": "TYPED_CARRIER_QUANTITY",
        "DIMENSIONLESS_PARTICIPATION_VALID": "DIMENSIONLESS_PARTICIPATION",
    }
    if mutation in extent_semantics:
        return _set_record(
            world, declaration, _extent_variant(record, extent_semantics[mutation])  # type: ignore[arg-type]
        )
    if mutation == "DIVISIBILITY_NOT_DECLARED":
        return _failure_world(world, declaration, "EXTENT_DIVISIBILITY_UNDECLARED")
    if mutation == "COORDINATE_ORIENTATION_MISMATCH":
        return _failure_world(world, declaration, "EXTENT_DECLARATION_INVALID")
    if mutation == "MISSING_UNIT":
        return _failure_world(world, declaration, "UNIT_MISMATCH")
    if mutation == "INCOMPATIBLE_DIMENSION":
        return _failure_world(world, declaration, "DIMENSION_MISMATCH")
    if mutation == "RIGHT_DERIVATIVE_EXISTS":
        return _enum_world(world, declaration, "right_derivative_status", "EXISTS")
    if mutation == "RIGHT_DERIVATIVE_DOES_NOT_EXIST":
        return _enum_world(world, declaration, "right_derivative_status", "DOES_NOT_EXIST")
    if mutation == "GENERATOR_WITH_UNDECLARED_DIVISIBILITY":
        extent = _replace_record(world["ExtentDefinition"], divisibility="NOT_DIVISIBLE")
        changed = dict(world)
        changed["ExtentDefinition"] = extent
        changed[declaration] = _replace_record(record, extent_ref=_record_ref(extent))
        return changed
    if mutation in {"QUANTITY_GENERATOR_VALID", "AUGMENTED_STATE_COMPLETE", "GENERATOR_LINK_VALID", "HYBRID_VALID", "T0_IDENTITY_VALID", "HISTORY_EQUIVALENCE_VALID"}:
        return world
    if mutation == "AUGMENTED_STATE_ROLE_MISSING":
        return _failure_world(world, declaration, "AUGMENTED_STATE_INCOMPLETE")
    if mutation == "GENERATOR_LINK_MISMATCH":
        return _failure_world(world, declaration, "GENERATOR_LINK_INVALID")
    if mutation == "POSITIVE_AFFINE_VALID":
        return _set_record(world, declaration, _regularity_variant(record, "POSITIVE_AFFINE"))  # type: ignore[arg-type]
    if mutation == "POSITIVE_NONLINEAR_C1_VALID":
        return _set_record(world, declaration, _regularity_variant(record, "POSITIVE_NONLINEAR_C1"))  # type: ignore[arg-type]
    if mutation == "ORIENTATION_REVERSAL_REFUSED_INHERITANCE":
        return _set_record(world, declaration, _regularity_variant(record, "ORIENTATION_REVERSING"))  # type: ignore[arg-type]
    if mutation == "INVALID_AUTOMATIC_INHERITANCE":
        return _failure_world(world, declaration, "REPARAMETERIZATION_WITNESS_INVALID")
    if mutation == "HIDDEN_FIXED_ACTIVATION":
        return _failure_world(world, declaration, "HYBRID_ACTIVATION_INVALID")
    if mutation == "BELOW_MINIMUM_ACTIVE_BUNDLE":
        changed = _replace_record(
            record,
            maximum_active_quantity=_quantity_change(
                record.maximum_active_quantity, magnitude=IntegerV1(1)  # type: ignore[attr-defined]
            ),
        )
        return _set_record(world, declaration, changed)
    if mutation == "DUPLICATED_FIXED_ACTIVATION":
        return _failure_world(world, declaration, "FIXED_ACTIVATION_ACCOUNT_DUPLICATED")
    if mutation.startswith("VALID_RECONSTRUCTION:"):
        kind = mutation.split(":", 1)[1]
        changed, hybrid_arg = _finite_variant(world, kind)
        result = _set_record(world, declaration, changed)
        result["finite_hybrid_arg"] = hybrid_arg
        return result
    if mutation == "T0_NOT_IDENTITY":
        return _failure_world(world, declaration, "RECONSTRUCTION_CLAIM_UNSUPPORTED")
    if mutation == "UNSUPPORTED_ORDINARY_EXPONENTIAL":
        changed = _replace_record(record, operator_domain_ref=Applicability.NOT_APPLICABLE)
        return _set_record(world, declaration, changed)
    if mutation == "SNAPSHOT_ONLY":
        return _failure_world(world, declaration, "BOUNDARY_HISTORY_EQUIVALENCE_INVALID")
    if mutation == "ONE_STATE_GENERATOR_ONLY":
        return _set_record(
            world,
            declaration,
            _replace_record(record, one_state_generator_equality_only=True),
        )
    if mutation.startswith("MISSING_PRESERVATION:"):
        role = mutation.split(":", 1)[1]
        target = {
            "BURDEN": record.burden_preservation_ref,
            "CONSERVATION": record.conservation_preservation_ref,
            "LOSS": record.loss_preservation_ref,
            "COMMITMENT": record.commitment_preservation_ref,
            "PROCESS_ACCOUNT": record.process_account_preservation_refs[0],
            "SETTLEMENT_WHEN_VISIBLE": record.settlement_preservation_ref,
        }[role]
        assert type(target) is ObjectRef
        changed = _replace_record(
            record,
            resolution=_resolution(
                completed=record.resolution.completed_part_refs,
                missing=(target,),
                state=ResolutionState.PARTIAL,
            ),
        )
        return _set_record(world, declaration, changed)
    raise AssertionError(f"unhandled semantic mutation {mutation}")


def _precedence_world(
    world: dict[str, object], declaration: str, active: tuple[str, ...]
) -> tuple[dict[str, object], bool]:
    changed = dict(world)
    attach_runtime = "FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR" in active
    structural = {
        "I3_OBJECT_CONTENT_MISMATCH",
        "I3_COLLECTION_ORDER_INVALID",
        "I3_DUPLICATE_MEMBER",
        "FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR",
        "HASH_MISMATCH",
    }
    for code in reversed(tuple(code for code in active if code not in structural)):
        changed = _failure_world(changed, declaration, code)
    record = changed[declaration]
    ordered = "I3_COLLECTION_ORDER_INVALID" in active
    duplicated = "I3_DUPLICATE_MEMBER" in active
    if ordered and duplicated:
        provenance = record.provenance_refs  # type: ignore[attr-defined]
        record = _replace_record(
            record,
            provenance_refs=(provenance[1], provenance[0], provenance[0]),
        )
        changed = _set_record(changed, declaration, record)
    elif ordered:
        record = _replace_record(
            record,
            provenance_refs=tuple(reversed(record.provenance_refs)),  # type: ignore[attr-defined]
        )
        changed = _set_record(changed, declaration, record)
    elif duplicated:
        provenance = record.provenance_refs  # type: ignore[attr-defined]
        record = _replace_record(
            record, provenance_refs=(provenance[0], provenance[0])
        )
        changed = _set_record(changed, declaration, record)
    if "I3_OBJECT_CONTENT_MISMATCH" in active:
        record = _corrupt_payload(changed[declaration])
        changed = _set_record(changed, declaration, record)
    if "HASH_MISMATCH" in active:
        record = _corrupt_hash(changed[declaration])
        changed = _set_record(changed, declaration, record)
    return changed, attach_runtime


def _mutated_world(
    world: dict[str, object], vector: dict[str, object]
) -> tuple[dict[str, object], bool]:
    declaration = vector["declaration"]
    category = vector["category"]
    mutation = vector["mutation"]
    assert type(declaration) is str and type(category) is str and type(mutation) is str
    record = world[declaration]
    if category == "DECLARATION_SUCCESS":
        return world, False
    if category == "ENUM_MEMBER_BOUNDARY":
        field_name, value = mutation.removeprefix("VALID_ENUM:").split("=", 1)
        return _enum_world(world, declaration, field_name, value), False
    if category == "COLLECTION_DUPLICATE":
        field_name = mutation.split(":", 1)[1]
        values = getattr(record, field_name)
        if not values:
            self_value = _STATE_ROLES[-1]
            values = (self_value,)
        changed = _replace_record(record, **{field_name: (values[0], values[0])})
        return _set_record(world, declaration, changed), False
    if category == "COLLECTION_ORDER":
        field_name = mutation.split(":", 1)[1]
        values = getattr(record, field_name)
        companion_changes: dict[str, object] = {}
        if len(values) < 2 and field_name == "inapplicable_state_role_codes":
            values = _STATE_ROLES[-2:]
            companion_changes["represented_state_role_codes"] = _STATE_ROLES[:-2]
        elif len(values) < 2 and field_name == "regularity_codes":
            values = ("C1", "C2")
        elif len(values) < 2 and field_name == "internal_topology_export_refs":
            values = _ordered_refs(_ref("topology-export-a"), _ref("topology-export-b"))
        changed = _replace_record(record, **{field_name: tuple(reversed(values))})
        if companion_changes:
            changed = _replace_record(changed, **companion_changes)
        return _set_record(world, declaration, changed), False
    if category == "APPLICABILITY_BOUNDARY":
        field_name = mutation.split(":", 1)[1]
        return _applicability_world(world, declaration, field_name), False
    if category == "CLAIM_STATUS_ALLOWED":
        status = ClaimStatus(mutation.split(":", 1)[1])
        return _set_record(
            world, declaration, _replace_record(record, claim_status=status)
        ), False
    if category == "CLAIM_STATUS_REJECTED":
        changed = _replace_record(
            record, claim_status=ClaimStatus.OBSERVED_REGISTERED_RESULT
        )
        return _set_record(world, declaration, changed), False
    if category == "NONCLAIM_REQUIRED":
        required = tuple(_SPEC_BY_NAME[declaration]["required_nonclaim_codes"])
        remaining = tuple(code for code in record.nonclaim_codes if code != required[0])
        return _set_record(
            world, declaration, _replace_record(record, nonclaim_codes=remaining)
        ), False
    if category == "OBJECT_CONTENT":
        return _set_record(world, declaration, _corrupt_payload(record)), False
    if category == "HASH":
        return _set_record(world, declaration, _corrupt_hash(record)), False
    if category == "FORBIDDEN_RUNTIME":
        return world, True
    if category in {"ADJACENT_PRECEDENCE", "MULTIPLY_INVALID_PRECEDENCE"}:
        return _precedence_world(
            world, declaration, tuple(vector["active_predicates"])
        )
    if category == "SEMANTIC":
        return _semantic_world(world, declaration, mutation), False
    raise AssertionError(f"unhandled vector category {category}")


class AtomicDeclarationContractTests(unittest.TestCase):
    def test_exact_declaration_shapes_and_signatures(self) -> None:
        self.assertEqual(
            [runtime_type.__name__ for runtime_type in _D1_TYPES],
            [row["name"] for row in _D1_DECLARATION_ROWS],
        )
        for runtime_type, row in zip(_D1_TYPES, _D1_DECLARATION_ROWS, strict=True):
            with self.subTest(declaration=runtime_type.__name__):
                self.assertTrue(is_dataclass(runtime_type))
                self.assertEqual(
                    [field.name for field in fields(runtime_type)], row["field_order"]
                )
                parameters = runtime_type.__dataclass_params__
                self.assertTrue(parameters.frozen)
                self.assertTrue(parameters.eq)
                self.assertFalse(parameters.order)
                self.assertFalse(parameters.unsafe_hash)
                self.assertEqual(tuple(runtime_type.__slots__), tuple(row["field_order"]))
                signature = inspect.signature(runtime_type)
                self.assertTrue(
                    all(
                        parameter.kind is inspect.Parameter.KEYWORD_ONLY
                        for parameter in signature.parameters.values()
                    )
                )
                self.assertTrue(
                    all(
                        parameter.default is inspect.Parameter.empty
                        for parameter in signature.parameters.values()
                    )
                )
                annotations = get_type_hints(runtime_type)
                for field_row in row["fields"]:
                    field_name, expected_type = field_row[:2]
                    annotation = annotations[field_name]
                    base_expected = expected_type.split("@", 1)[0]
                    with self.subTest(
                        declaration=runtime_type.__name__, field=field_name
                    ):
                        if base_expected.startswith("LiteralDomain["):
                            domain = base_expected.removeprefix("LiteralDomain[").removesuffix("]")
                            self.assertIs(get_origin(annotation), Literal)
                            self.assertEqual(
                                get_args(annotation),
                                tuple(_CONTRACT["closed_domains"][domain]),
                            )
                        elif base_expected == "CommonObjectEnvelope":
                            self.assertIs(annotation, CommonObjectEnvelope)
                        elif base_expected == "ObjectRef":
                            self.assertIs(annotation, ObjectRef)
                        elif base_expected == "ObjectRef|Applicability":
                            self.assertEqual(set(get_args(annotation)), {ObjectRef, Applicability})
                        elif base_expected == "Quantity|Applicability":
                            self.assertEqual(set(get_args(annotation)), {Quantity, Applicability})
                        elif base_expected == "CoreNumberV1|Applicability":
                            self.assertEqual(
                                set(get_args(annotation)),
                                {IntegerV1, atomic_module.RationalV1, atomic_module.DecimalV1, atomic_module.Binary64BitsV1, Applicability},
                            )
                        elif base_expected == "Quantity":
                            self.assertIs(annotation, Quantity)
                        elif base_expected == "ClaimStatus":
                            self.assertIs(annotation, ClaimStatus)
                        elif base_expected == "ResolutionDetail":
                            self.assertIs(annotation, ResolutionDetail)
                        elif base_expected == "bool":
                            self.assertIs(annotation, bool)
                        elif base_expected == "tuple[str,...]":
                            self.assertEqual(get_args(annotation), (str, Ellipsis))
                        elif base_expected == "tuple[ObjectRef,...]":
                            self.assertEqual(get_args(annotation), (ObjectRef, Ellipsis))
                        else:
                            self.assertIs(get_origin(annotation), tuple)
                            self.assertIs(get_args(annotation)[1], Ellipsis)
                            row_annotation = get_args(annotation)[0]
                            self.assertIs(get_origin(row_annotation), tuple)
        for validator, row in zip(_D1_VALIDATORS, _D1_VALIDATOR_ROWS, strict=True):
            with self.subTest(validator=validator.__name__):
                self.assertEqual(validator.__name__, row["name"])
                self.assertTrue(
                    all(
                        parameter.kind is inspect.Parameter.POSITIONAL_ONLY
                        for parameter in inspect.signature(validator).parameters.values()
                    )
                )
                self.assertEqual(
                    str(inspect.signature(validator))
                    .replace("'", "")
                    .replace(" | ", "|"),
                    row["signature"],
                )

    def test_keyword_only_and_exact_formation(self) -> None:
        world = _base_world()
        for runtime_type in _D1_TYPES:
            record = world[runtime_type.__name__]
            kwargs = {field.name: getattr(record, field.name) for field in fields(record)}
            with self.subTest(declaration=runtime_type.__name__, boundary="positional"):
                with self.assertRaises(FrameworkError) as raised:
                    runtime_type(*kwargs.values())
                self.assertIs(
                    raised.exception.envelope.failure_code,
                    FailureCode.I3_RECORD_FORMATION_INVALID,
                )
            with self.subTest(declaration=runtime_type.__name__, boundary="unknown"):
                with self.assertRaises(FrameworkError) as raised:
                    runtime_type(**kwargs, unknown_field=True)
                self.assertIs(
                    raised.exception.envelope.failure_code,
                    FailureCode.I3_RECORD_FORMATION_INVALID,
                )

    def test_ecj1_projection_contains_every_non_envelope_field(self) -> None:
        world = _base_world()
        for row in _D1_DECLARATION_ROWS:
            record = world[row["name"]]
            expected = {
                name: _project(getattr(record, name))
                for name in row["field_order"]
                if name != "envelope"
            }
            with self.subTest(declaration=row["name"]):
                self.assertEqual(record.to_ecj1(), expected)
                self.assertNotIn("envelope", record.to_ecj1())
                self.assertEqual(
                    parse_ecj1(record.envelope.object_content_payload), expected
                )

    def test_all_frozen_vectors_reach_the_intended_boundary(self) -> None:
        constructor_calls = validator_calls = predicate_calls = 0
        outcomes: Counter[str] = Counter()
        for vector in _FIXTURE:
            declaration = vector["declaration"]
            category = vector["category"]
            mutation = vector["mutation"]
            expected_result = vector["expected_result"]
            expected_failure = vector["first_failure"]
            runtime_type = _TYPE_BY_NAME[declaration]
            world = _base_world()
            record = world[declaration]
            constructor_calls += 1
            validator_calls += vector["validator_calls"]
            predicate_calls += vector["expected_predicate_calls"]
            outcomes[expected_result] += 1
            with self.subTest(vector=vector["id"], mutation=mutation):
                if category in {"FORMATION_MISSING_FIELD", "FORMATION_WRONG_TYPE"}:
                    kwargs = {
                        field.name: getattr(record, field.name) for field in fields(record)
                    }
                    field_name = mutation.split(":", 1)[1]
                    if category == "FORMATION_MISSING_FIELD":
                        del kwargs[field_name]
                    else:
                        kwargs[field_name] = None
                    with self.assertRaises(FrameworkError) as raised:
                        runtime_type(**kwargs)
                    self.assertEqual(
                        raised.exception.envelope.failure_code.value,
                        expected_failure,
                    )
                    continue
                if category == "ENUM_OUT_OF_DOMAIN":
                    field_name = mutation.removeprefix("INVALID_ENUM:").split("=", 1)[0]
                    kwargs = {
                        field.name: getattr(record, field.name) for field in fields(record)
                    }
                    kwargs[field_name] = "OUTSIDE_CLOSED_DOMAIN"
                    with self.assertRaises(FrameworkError) as raised:
                        runtime_type(**kwargs)
                    self.assertEqual(
                        raised.exception.envelope.failure_code.value,
                        expected_failure,
                    )
                    continue
                if category == "VALIDATOR_BYPASS":
                    self.assertEqual(expected_result, "NO_ACCEPTED_RESULT")
                    self.assertEqual(expected_failure, "VALIDATOR_BYPASS_FORBIDDEN")
                    self.assertEqual(vector["validator_calls"], 0)
                    continue
                changed_world, attach_runtime = _mutated_world(world, vector)
                if expected_result == "SUCCESS":
                    _call_validator(changed_world, declaration)
                    continue
                runtime_member = "execute_generator"
                if attach_runtime:
                    setattr(runtime_type, runtime_member, lambda self: None)
                try:
                    with self.assertRaises(FrameworkError) as raised:
                        _call_validator(changed_world, declaration)
                    self.assertEqual(
                        raised.exception.envelope.failure_code.value,
                        expected_failure,
                    )
                finally:
                    if attach_runtime:
                        delattr(runtime_type, runtime_member)
        self.assertEqual(constructor_calls, 731)
        self.assertEqual(validator_calls, 327)
        self.assertEqual(predicate_calls, 1870)
        self.assertEqual(outcomes, Counter(SUCCESS=108, FAILURE=614, NO_ACCEPTED_RESULT=9))

    def test_fixture_identity_counts_and_collision_analysis(self) -> None:
        raw = _FIXTURE_PATH.read_bytes()
        self.assertEqual(len(raw), 469664)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "6b4ecac191320e4ee6b02763249fdc9db14b7fb19091814ca10c6703e36acda9",
        )
        self.assertEqual(_FIXTURE, _VALIDATION["d1_vectors"])
        self.assertEqual(bytes(encode_ecj1(_FIXTURE)) + b"\n", raw)
        self.assertEqual([row["id"] for row in _FIXTURE], _VALIDATION["d1_case_order"])
        identities = [
            json.dumps(
                {
                    key: row[key]
                    for key in (
                        "stage",
                        "declaration",
                        "category",
                        "baseline_profile",
                        "mutation",
                    )
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            for row in _FIXTURE
        ]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertEqual(sum(row["constructor_calls"] for row in _FIXTURE), 731)
        self.assertEqual(sum(row["validator_calls"] for row in _FIXTURE), 327)
        self.assertEqual(sum(row["expected_predicate_calls"] for row in _FIXTURE), 1870)
        self.assertTrue(
            all(
                row["opaque_reference_resolution_calls"] == 0
                and row["runtime_behavior_calls"] == 0
                and row["model_state_advances"] == 0
                and row["scientific_execution"] is False
                for row in _FIXTURE
            )
        )

    def test_exact_failure_and_root_export_inventories(self) -> None:
        compatibility = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
        )
        i5_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i5_contract.json"
        )
        post_i5_compatibility = _load_json(
            _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
        )
        i6_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i6_contract.json"
        )
        i7_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i7_contract.json"
        )
        assert type(compatibility) is dict
        assert type(i5_contract) is dict
        assert type(post_i5_compatibility) is dict
        current_surface = compatibility["current_surface"]
        post_i5_surface = post_i5_compatibility["current_surface"]
        failure_slices = current_surface["failure_slices"]
        export_slices = current_surface["root_export_slices"]
        failures = tuple(code.value for code in FailureCode)
        self.assertEqual(len(failures), 256)
        self.assertEqual(failures[:88], tuple(_CONTRACT["current_surface"]["failure_order"]))
        self.assertEqual(failures[88:102], tuple(failure_slices[2]["values"]))
        self.assertEqual(
            failures[88:102], tuple(_CONTRACT["failure_contract"]["d1_append_order"])
        )
        self.assertEqual(failures[102:124], tuple(failure_slices[3]["values"]))
        self.assertEqual(failures[124:185], tuple(failure_slices[4]["values"]))
        self.assertEqual(
            (failures[:185], failures[185:227], failures[:227]),
            (
                tuple(current_surface["failure_order"]),
                tuple(i5_contract["failure_append_order"]),
                tuple(post_i5_surface["failure_order"]),
            ),
        )
        self.assertEqual(
            failures[227:232], tuple(i6_contract["failure_inventory"]["append_order"])
        )
        self.assertEqual(
            failures[232:], tuple(i7_contract["failure_inventory"]["append_order"])
        )
        failure_projection = ("\n".join(failures) + "\n").encode()
        failure_prefix_projection = ("\n".join(failures[:102]) + "\n").encode()
        self.assertEqual(
            (
                len(failure_prefix_projection),
                hashlib.sha256(failure_prefix_projection).hexdigest(),
            ),
            (
                2563,
                "0c395c7f1291999df805a5357ec83332f5ee96c5b1b35432953e2542027544f9",
            ),
        )
        self.assertEqual(
            (
                len(("\n".join(failures[:227]) + "\n").encode()),
                hashlib.sha256(("\n".join(failures[:227]) + "\n").encode()).hexdigest(),
                len(("\n".join(failures[185:227]) + "\n").encode()),
                hashlib.sha256(
                    ("\n".join(failures[185:227]) + "\n").encode()
                ).hexdigest(),
            ),
            (
                5997,
                "4cb1daceb30c0f106e7ba288980d379da2403236593948b4be47247704555ae4",
                1103,
                "b70fccfca86d4b7118bf80593794b40a2ad8f3848dbe4ff0963741e4e56f3681",
            ),
        )
        self.assertEqual(
            (len(failure_projection), hashlib.sha256(failure_projection).hexdigest()),
            (
                i7_contract["failure_inventory"]["future_lf"]["byte_count"],
                i7_contract["failure_inventory"]["future_lf"]["sha256"],
            ),
        )
        exports = tuple(ebu_framework.__all__)
        self.assertEqual(len(exports), 419)
        self.assertEqual(
            exports[:219], tuple(_CONTRACT["current_surface"]["root_export_order"])
        )
        self.assertEqual(exports[219:237], tuple(export_slices[2]["values"]))
        self.assertEqual(
            exports[219:237],
            tuple(_CONTRACT["proposed_surface"]["d1_root_export_suffix"]),
        )
        self.assertEqual(exports[237:261], tuple(export_slices[3]["values"]))
        self.assertEqual(exports[261:309], tuple(export_slices[4]["values"]))
        self.assertEqual(
            (exports[:309], exports[309:391], exports[:391]),
            (
                tuple(current_surface["root_export_order"]),
                tuple(i5_contract["root_export_suffix_types"])
                + tuple(i5_contract["root_export_suffix_callables"]),
                tuple(post_i5_surface["root_export_order"]),
            ),
        )
        self.assertEqual(
            exports[391:407], tuple(i6_contract["root_exports"]["append_order"])
        )
        self.assertEqual(
            exports[407:], tuple(i7_contract["root_exports"]["append_order"])
        )
        export_projection = ("\n".join(exports) + "\n").encode()
        export_prefix_projection = ("\n".join(exports[:237]) + "\n").encode()
        self.assertEqual(
            (
                len(export_prefix_projection),
                hashlib.sha256(export_prefix_projection).hexdigest(),
            ),
            (
                5012,
                "b78004bc3368d2d7bd8a50de9829bb1b693bffc6a96a8663336aea7922c41d29",
            ),
        )
        self.assertEqual(
            (
                len(("\n".join(exports[:391]) + "\n").encode()),
                hashlib.sha256(("\n".join(exports[:391]) + "\n").encode()).hexdigest(),
                len(("\n".join(exports[309:391]) + "\n").encode()),
                hashlib.sha256(
                    ("\n".join(exports[309:391]) + "\n").encode()
                ).hexdigest(),
            ),
            (
                8625,
                "f27ed982d7e646be870404239ad617d181df8276728f9a3f1fc878c5bbfa46db",
                1787,
                "0b593d0d045da2ce3ffb46bc192ceb1b7aea58d2212bb14981ac716dbd02f508",
            ),
        )
        self.assertEqual(
            (len(export_projection), hashlib.sha256(export_projection).hexdigest()),
            (
                i7_contract["root_exports"]["future_lf"]["byte_count"],
                i7_contract["root_exports"]["future_lf"]["sha256"],
            ),
        )

    def test_exact_direct_imports_and_acyclic_graph(self) -> None:
        tree = ast.parse(_ATOMIC_PATH.read_text(encoding="utf-8"))
        direct = [
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom) and node.level == 1
        ]
        self.assertEqual(
            direct, ["primitives", "numeric", "identity", "envelopes", "errors"]
        )
        package_dir = _REPO_ROOT / "src/ebu_framework"
        modules = {path.stem for path in package_dir.glob("*.py") if path.name != "__init__.py"}
        graph: dict[str, set[str]] = {name: set() for name in modules}
        for name in modules:
            module_tree = ast.parse(
                (package_dir / f"{name}.py").read_text(encoding="utf-8")
            )
            for node in ast.walk(module_tree):
                if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module in modules:
                    graph[name].add(node.module)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                self.fail(f"import cycle reaches {name}")
            if name in visited:
                return
            visiting.add(name)
            for dependency in graph[name]:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)

        for name in graph:
            visit(name)

    def test_existing_public_signatures_and_predecessor_bytes_are_preserved(self) -> None:
        compatibility = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
        )
        compatibility_manifest = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_predecessor_manifest.json"
        )
        assert type(compatibility) is dict
        assert type(compatibility_manifest) is dict
        compatibility_paths = frozenset(
            compatibility["future_implementation"]["exact_paths"]
        )
        reconciled = {
            row["path"]: row
            for row in compatibility_manifest["repeated_historical_lock_reconciliation"]
        }
        current_rows = {
            row["path"]: row for row in compatibility_manifest["rows"]
        }
        post_i5_compatibility = _load_json(
            _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
        )
        assert type(post_i5_compatibility) is dict
        i5_candidate_rows = {
            row["path"]: row
            for row in post_i5_compatibility["implementation_candidate_lock"]["rows"]
        }
        i5_reconciled = {
            row["path"]: row
            for row in post_i5_compatibility["historical_byte_contract"]
            ["legacy_loop_reconciliation_control_flow"]["path_routes_in_order"]
        }
        post_i5_legacy_paths = frozenset(
            post_i5_compatibility["future_implementation"]["legacy_test_paths"]
        )
        import subprocess

        for module_name, function_name, expected in _CONTRACT["current_surface"]["public_function_signatures"]:
            function = getattr(importlib.import_module(f"ebu_framework.{module_name}"), function_name)
            actual = str(inspect.signature(function)).replace("'", "")
            actual = actual.replace(
                "<ExactConversion.NOT_APPLICABLE: NOT_APPLICABLE>",
                "ExactConversion.NOT_APPLICABLE",
            )
            self.assertEqual(actual, expected)
        excluded = {
            "src/ebu_framework/__init__.py",
            "src/ebu_framework/capabilities.py",
            "src/ebu_framework/commitments.py",
            "src/ebu_framework/errors.py",
            "src/ebu_framework/execution.py",
            "src/ebu_framework/network.py",
        }
        for row in _MANIFEST["rows"]:
            if row["path"] in excluded:
                continue
            path = _REPO_ROOT / row["path"]
            with self.subTest(path=row["path"]):
                payload = path.read_bytes()
                comparison_payload = payload
                current_base_payload = None
                current_row = None
                i5_route = i5_reconciled.get(row["path"])
                candidate_row = i5_candidate_rows.get(row["path"])
                historical_byte_count = (
                    i5_route["historical_byte_count"]
                    if i5_route is not None
                    else row["byte_count"]
                )
                historical_raw_sha256 = (
                    i5_route["historical_raw_sha256"]
                    if i5_route is not None
                    else row["raw_sha256"]
                )
                if row["path"] in compatibility_paths:
                    comparison_payload = subprocess.run(
                        ["git", "cat-file", "blob", row["git_object"]],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    current_row = current_rows[row["path"]]
                elif row["path"] in reconciled:
                    reconciliation = reconciled[row["path"]]
                    comparison_payload = subprocess.run(
                        [
                            "git",
                            "cat-file",
                            "blob",
                            reconciliation["historical_git_object"],
                        ],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    current_row = current_rows[row["path"]]
                elif i5_route is not None:
                    comparison_payload = subprocess.run(
                        [
                            "git",
                            "cat-file",
                            "blob",
                            i5_route["historical_git_object"],
                        ],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    current_row = current_rows[row["path"]]
                if current_row is not None:
                    current_base_payload = subprocess.run(
                        ["git", "cat-file", "blob", current_row["git_object"]],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    tree_row = subprocess.run(
                        [
                            "git",
                            "ls-tree",
                            _MANIFEST["authority"]["base_commit"],
                            "--",
                            row["path"],
                        ],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.split()
                    self.assertEqual(tree_row[2], row["git_object"])
                if len(comparison_payload) != historical_byte_count:
                    predecessor = _load_json(
                        _REPO_ROOT
                        / "unified_python_research_framework_i6_predecessor_manifest.json"
                    )
                    accepted_row = next(
                        item for item in predecessor["rows"] if item["path"] == row["path"]
                    )
                    self.assertEqual(
                        (len(payload), hashlib.sha256(payload).hexdigest()),
                        (accepted_row["byte_count"], accepted_row["raw_sha256"]),
                    )
                else:
                    self.assertEqual(len(comparison_payload), historical_byte_count)
                if current_base_payload is not None:
                    self.assertEqual(len(current_base_payload), current_row["byte_count"])
                    if (
                        row["path"] not in compatibility_paths
                        and row["path"] not in post_i5_legacy_paths
                    ):
                        self.assertEqual(
                            (
                                len(payload),
                                "100755"
                                if path.stat().st_mode & stat.S_IXUSR
                                else "100644",
                            ),
                            (
                                (candidate_row or current_row)["byte_count"],
                                (candidate_row or current_row)["mode"],
                            ),
                        )
                if len(comparison_payload) == historical_byte_count:
                    self.assertEqual(
                        hashlib.sha256(comparison_payload).hexdigest(),
                        historical_raw_sha256,
                    )
                if current_base_payload is not None:
                    self.assertEqual(
                        hashlib.sha256(current_base_payload).hexdigest(),
                        current_row["raw_sha256"],
                    )
                    if (
                        row["path"] not in compatibility_paths
                        and row["path"] not in post_i5_legacy_paths
                    ):
                        self.assertEqual(
                            hashlib.sha256(payload).hexdigest(),
                            (candidate_row or current_row)["raw_sha256"],
                        )
                mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
                self.assertEqual(mode, row["mode"])

    def test_no_d2_surface_or_prohibited_reachability(self) -> None:
        compatibility = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
        )
        assert type(compatibility) is dict
        current_surface = compatibility["current_surface"]
        source = _ATOMIC_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        d2_names = tuple(_CONTRACT["proposed_surface"]["d2_root_export_suffix"])
        root_exports = tuple(ebu_framework.__all__)
        self.assertEqual(root_exports[237:261], d2_names)
        self.assertEqual(
            tuple(
                root_exports[row["start"] : row["stop"]]
                for row in current_surface["root_export_slices"]
            ),
            tuple(
                tuple(row["values"]) for row in current_surface["root_export_slices"]
            ),
        )
        i5_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i5_contract.json"
        )
        post_i5_compatibility = _load_json(
            _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
        )
        i6_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i6_contract.json"
        )
        i7_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i7_contract.json"
        )
        self.assertEqual(
            (root_exports[:309], root_exports[309:391], root_exports[:391]),
            (
                tuple(current_surface["root_export_order"]),
                tuple(i5_contract["root_export_suffix_types"])
                + tuple(i5_contract["root_export_suffix_callables"]),
                tuple(post_i5_compatibility["current_surface"]["root_export_order"]),
            ),
        )
        self.assertEqual(
            root_exports[391:407], tuple(i6_contract["root_exports"]["append_order"])
        )
        self.assertEqual(
            root_exports[407:], tuple(i7_contract["root_exports"]["append_order"])
        )
        interaction_payload = (
            _REPO_ROOT / "src/ebu_framework/interaction.py"
        ).read_bytes()
        self.assertEqual(
            (len(interaction_payload), hashlib.sha256(interaction_payload).hexdigest()),
            (
                100478,
                "198f1a63e09d682b94a5fb127eec6445ac18f9241c84acbdb5e05c7c8ee54804",
            ),
        )
        forbidden_imports = {
            "asyncio",
            "importlib",
            "multiprocessing",
            "random",
            "secrets",
            "socket",
            "subprocess",
            "threading",
            "urllib",
        }
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            (node.module or "").split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.level == 0
        }
        self.assertFalse(imported & forbidden_imports)
        prohibited_calls = {
            "__import__",
            "eval",
            "exec",
            "open",
            "optimize",
            "resolve_ref",
            "run",
            "settle",
            "simulate",
            "step",
        }
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertFalse(called & prohibited_calls)


if __name__ == "__main__":
    unittest.main()
