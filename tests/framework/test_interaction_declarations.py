"""Static and synthetic conformance checks for the frozen D2 declaration slice."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import fields, is_dataclass, replace
from enum import StrEnum
import hashlib
import importlib
import inspect
from itertools import combinations
import json
from pathlib import Path
import stat
from typing import get_args, get_origin, get_type_hints, Literal
import unittest

import ebu_framework
import ebu_framework.interaction as interaction_module
from ebu_framework.atomic import (
    BoundaryHistoryEquivalenceWitness,
    StateTransformationGeneratorDeclaration,
)
from ebu_framework.canonical import encode_ecj1, parse_ecj1
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.hashing import compute_object_content_hash
from ebu_framework.identity import ObjectContentHash, ObjectRef, ScientificId, SemanticVersion
from ebu_framework.interaction import (
    AllocationOptimalityWitness,
    CommutatorWitness,
    FiniteSetInteractionWitness,
    InstitutionalAcceptanceRule,
    InstitutionalSettlementRule,
    InteractionTopologySnapshot,
    JointObjectiveDeclaration,
    MixedMarginalWitness,
    SameBaselineNonadditivityWitness,
    ScalarDecompositionWitness,
    SerialComparatorInteractionWitness,
    SharedConstraintFactor,
    validate_allocation_optimality,
    validate_commutator,
    validate_finite_set_interaction,
    validate_institutional_acceptance_rule,
    validate_institutional_settlement_rule,
    validate_interaction_topology_snapshot,
    validate_joint_objective,
    validate_mixed_marginal,
    validate_same_baseline_nonadditivity,
    validate_scalar_decomposition,
    validate_serial_comparator_interaction,
    validate_shared_constraint_factor,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.primitives import ClaimStatus, Quantity, ResolutionDetail, ResolutionState


_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTRACT_PATH = _REPO_ROOT / "atomic_interaction_declaration_contract.json"
_VALIDATION_PATH = _REPO_ROOT / "atomic_interaction_declaration_validation_contract.json"
_MANIFEST_PATH = _REPO_ROOT / "atomic_interaction_declaration_predecessor_manifest.json"
_FIXTURE_PATH = _REPO_ROOT / "tests/framework/fixtures/interaction_declaration_v1.json"
_INTERACTION_PATH = _REPO_ROOT / "src/ebu_framework/interaction.py"


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
    return json.loads(payload, object_pairs_hook=_strict_object, parse_constant=_reject_constant)


_CONTRACT = _load_json(_CONTRACT_PATH)
_VALIDATION = _load_json(_VALIDATION_PATH)
_MANIFEST = _load_json(_MANIFEST_PATH)
_FIXTURE = _load_json(_FIXTURE_PATH)
_CLCD = _load_json(_REPO_ROOT / "closed_loop_correction_diagnostics_contract.json")
assert type(_CONTRACT) is dict
assert type(_VALIDATION) is dict
assert type(_MANIFEST) is dict
assert type(_FIXTURE) is list

_D2_ROWS = [row for row in _CONTRACT["declarations"] if row["stage"] == "D2"]
_D2_VALIDATOR_ROWS = [row for row in _CONTRACT["validators"] if row["stage"] == "D2"]
_D2_TYPES = (
    JointObjectiveDeclaration,
    FiniteSetInteractionWitness,
    SameBaselineNonadditivityWitness,
    SerialComparatorInteractionWitness,
    MixedMarginalWitness,
    CommutatorWitness,
    SharedConstraintFactor,
    InteractionTopologySnapshot,
    AllocationOptimalityWitness,
    ScalarDecompositionWitness,
    InstitutionalAcceptanceRule,
    InstitutionalSettlementRule,
)
_D2_VALIDATORS = (
    validate_joint_objective,
    validate_finite_set_interaction,
    validate_same_baseline_nonadditivity,
    validate_serial_comparator_interaction,
    validate_mixed_marginal,
    validate_commutator,
    validate_shared_constraint_factor,
    validate_interaction_topology_snapshot,
    validate_allocation_optimality,
    validate_scalar_decomposition,
    validate_institutional_acceptance_rule,
    validate_institutional_settlement_rule,
)
_TYPE_BY_NAME = {runtime_type.__name__: runtime_type for runtime_type in _D2_TYPES}
_SPEC_BY_NAME = {row["name"]: row for row in _D2_ROWS}
_VALIDATOR_BY_DECLARATION = dict(zip(_TYPE_BY_NAME, _D2_VALIDATORS, strict=True))
_NONCLAIMS = tuple(_CONTRACT["closed_nonclaim_codes"])
_STATE_ROLES = tuple(_CONTRACT["closed_state_role_codes"])
_OBSERVABLES = tuple(_CONTRACT["closed_boundary_observable_codes"])
_REGULARITY = tuple(_CONTRACT["closed_regularity_codes"])
_INTERACTION_TYPES = tuple(_CONTRACT["closed_domains"]["INTERACTION_TYPE"])


def _hash_value(label: str) -> ObjectContentHash:
    return ObjectContentHash("sha256:" + hashlib.sha256(label.encode()).hexdigest())


def _ref(label: str) -> ObjectRef:
    token = hashlib.sha256(label.encode()).hexdigest()[:24]
    return ObjectRef(
        object_id=ScientificId(f"ebu:test:d2:{token}"),
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
    spec = next(row for row in _CONTRACT["declarations"] if row["name"] == runtime_type.__name__)
    payload = {name: _project(data[name]) for name in spec["field_order"] if name != "envelope"}
    object_id = ScientificId(
        f"ebu:d2-test:record:{runtime_type.__name__.lower()}-{_RECORD_ORDINAL}"
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
    return {field.name: getattr(record, field.name) for field in fields(record) if field.name != "envelope"}


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


def _quantity(magnitude: int, unit: ObjectRef, dimension: ObjectRef, boundary: ObjectRef) -> Quantity:
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


def _quantity_change(quantity: Quantity, **changes: object) -> Quantity:
    return replace(quantity, **changes)


def _base_world() -> dict[str, object]:
    provenance = _ordered_refs(_ref("provenance-a"), _ref("provenance-b"))
    actions = _ordered_refs(_ref("action-a"), _ref("action-b"))
    boundary = _ref("boundary")
    horizon = _ref("horizon")
    value_unit = _ref("value-unit")
    value_dimension = _ref("value-dimension")
    quantity_unit = _ref("quantity-unit")
    quantity_dimension = _ref("quantity-dimension")
    marginal_unit = _ref("marginal-unit")
    marginal_dimension = _ref("marginal-dimension")
    extent_unit = _ref("extent-unit")
    extent_dimension = _ref("extent-dimension")
    domain = _ref("flow-domain")
    topology = _ref("flow-topology")
    state_schema = _ref("state-schema")
    coordinates = _ordered_refs(_ref("state-coordinate-a"), _ref("state-coordinate-b"))
    accounts = _ordered_refs(_ref("account-a"), _ref("account-b"))

    def state_generator(label: str) -> StateTransformationGeneratorDeclaration:
        return _make(
            StateTransformationGeneratorDeclaration,
            extent_ref=_ref("extent"),
            action_definition_ref=_ref(f"generator-action-{label}"),
            augmented_state_schema_ref=state_schema,
            boundary_ref=boundary,
            generator_contract_ref=_ref(f"generator-contract-{label}"),
            state_coordinate_refs=coordinates,
            derivative_component_units=tuple(
                (coordinate, _ref(f"derivative-unit-{index}"), _ref(f"derivative-dimension-{index}"))
                for index, coordinate in enumerate(coordinates)
            ),
            represented_state_role_codes=_STATE_ROLES,
            inapplicable_state_role_codes=(),
            state_completeness_witness_ref=_ref(f"state-completeness-{label}"),
            extent_unit_ref=extent_unit,
            extent_dimension_ref=extent_dimension,
            orientation="FORWARD",
            domain_ref=domain,
            topology_ref=topology,
            process_account_refs=accounts,
            claim_status=ClaimStatus.DEFINITION,
            nonclaim_codes=_ordered_codes(
                (
                    "NO_EMPIRICAL_VALIDATION",
                    "NO_CAUSAL_IDENTIFICATION",
                    "NO_RUNTIME_BEHAVIOR",
                    "NO_UNIVERSAL_MINIMAL_STATE",
                ),
                _NONCLAIMS,
            ),
            provenance_refs=provenance,
        )  # type: ignore[return-value]

    left_generator = state_generator("left")
    right_generator = state_generator("right")
    objective = _make(
        JointObjectiveDeclaration,
        boundary_ref=boundary,
        horizon_ref=horizon,
        action_refs=actions,
        feasibility_constraint_refs=_ordered_refs(_ref("feasibility-a"), _ref("feasibility-b")),
        objective_kind="SCALAR",
        scalar_objective_ref=_ref("scalar-objective"),
        vector_component_refs=(),
        component_unit_refs=(),
        selection_rule_ref=_ref("selection-rule"),
        epsilon_constraint_refs=(),
        optimization_direction="MINIMIZE",
        uncertainty_refs=_ordered_refs(_ref("uncertainty-a"), _ref("uncertainty-b")),
        existence_assumption_refs=_ordered_refs(_ref("existence-a"), _ref("existence-b")),
        regularity_assumption_refs=_ordered_refs(_ref("regularity-a"), _ref("regularity-b")),
        deterministic_tie_rule_ref=_ref("tie-rule"),
        feasibility_first=True,
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["JointObjectiveDeclaration"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    subset_values = (
        ((), _quantity(5, value_unit, value_dimension, boundary)),
        ((actions[0],), _quantity(8, value_unit, value_dimension, boundary)),
        ((actions[1],), _quantity(9, value_unit, value_dimension, boundary)),
        (actions, _quantity(15, value_unit, value_dimension, boundary)),
    )
    mobius = (
        ((), _quantity(5, value_unit, value_dimension, boundary)),
        ((actions[0],), _quantity(3, value_unit, value_dimension, boundary)),
        ((actions[1],), _quantity(4, value_unit, value_dimension, boundary)),
        (actions, _quantity(3, value_unit, value_dimension, boundary)),
    )
    finite = _make(
        FiniteSetInteractionWitness,
        subset_protocol_ref=_ref("subset-protocol"),
        action_refs=actions,
        initial_augmented_state_ref=_ref("initial-state"),
        boundary_ref=boundary,
        state_schema_ref=state_schema,
        burden_definition_ref=_ref("burden-definition"),
        value_unit_ref=value_unit,
        value_dimension_ref=value_dimension,
        horizon_ref=horizon,
        exogenous_history_ref=_ref("exogenous-history"),
        action_removal_semantics="QUANTITY_FIXED",
        constraint_refs=_ordered_refs(_ref("constraint-a"), _ref("constraint-b")),
        shared_constraint_resolver_ref=_ref("shared-resolver"),
        active_mode_refs=_ordered_refs(_ref("mode-a"), _ref("mode-b")),
        loss_account_refs=_ordered_refs(_ref("loss-a"), _ref("loss-b")),
        commitment_account_refs=_ordered_refs(_ref("commitment-a"), _ref("commitment-b")),
        process_account_refs=accounts,
        subset_values=subset_values,
        empty_baseline=_quantity(5, value_unit, value_dimension, boundary),
        mobius_coefficients=mobius,
        normalization="RAW_WITH_EXPLICIT_EMPTY",
        truncation_order=Applicability.NOT_APPLICABLE,
        truncation_residuals=(),
        claim_status=ClaimStatus.ALGEBRAIC_IDENTITY,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["FiniteSetInteractionWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    same_baseline = _make(
        SameBaselineNonadditivityWitness,
        subset_protocol_ref=finite.subset_protocol_ref,
        action_refs=actions,
        boundary_ref=boundary,
        horizon_ref=horizon,
        empty_baseline=_quantity(5, value_unit, value_dimension, boundary),
        joint_value=_quantity(15, value_unit, value_dimension, boundary),
        singleton_values=tuple(
            (action, _quantity(value, value_unit, value_dimension, boundary))
            for action, value in zip(actions, (8, 9), strict=True)
        ),
        nonadditivity_value=_quantity(3, value_unit, value_dimension, boundary),
        value_unit_ref=value_unit,
        value_dimension_ref=value_dimension,
        process_account_refs=accounts,
        claim_status=ClaimStatus.ALGEBRAIC_IDENTITY,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["SameBaselineNonadditivityWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    serial = _make(
        SerialComparatorInteractionWitness,
        comparison_protocol_ref=_ref("comparison-protocol"),
        action_refs=actions,
        parallel_schedule_ref=_ref("parallel-schedule"),
        serial_comparator_ref=_ref("serial-comparator"),
        serial_order_refs=tuple(reversed(actions)),
        initial_augmented_state_ref=finite.initial_augmented_state_ref,
        boundary_ref=boundary,
        horizon_ref=horizon,
        exogenous_history_ref=finite.exogenous_history_ref,
        parallel_value=_quantity(15, value_unit, value_dimension, boundary),
        serial_value=_quantity(12, value_unit, value_dimension, boundary),
        interaction_value=_quantity(3, value_unit, value_dimension, boundary),
        value_unit_ref=value_unit,
        value_dimension_ref=value_dimension,
        process_account_refs=accounts,
        claim_status=ClaimStatus.ALGEBRAIC_IDENTITY,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["SerialComparatorInteractionWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    mixed = _make(
        MixedMarginalWitness,
        action_i_ref=actions[0],
        action_j_ref=actions[1],
        quantity_coordinate_i_ref=_ref("quantity-coordinate-i"),
        quantity_coordinate_j_ref=_ref("quantity-coordinate-j"),
        base_quantity_i=_quantity(0, quantity_unit, quantity_dimension, boundary),
        base_quantity_j=_quantity(0, quantity_unit, quantity_dimension, boundary),
        delta_i=_quantity(2, quantity_unit, quantity_dimension, boundary),
        delta_j=_quantity(3, quantity_unit, quantity_dimension, boundary),
        rectangle_value_00=_quantity(5, value_unit, value_dimension, boundary),
        rectangle_value_10=_quantity(7, value_unit, value_dimension, boundary),
        rectangle_value_01=_quantity(8, value_unit, value_dimension, boundary),
        rectangle_value_11=_quantity(16, value_unit, value_dimension, boundary),
        mixed_difference=_quantity(6, value_unit, value_dimension, boundary),
        normalized_mixed_marginal=_quantity(1, marginal_unit, marginal_dimension, boundary),
        regularity_status="C2_ON_COMPLETE_RECTANGLE",
        rectangle_domain_ref=_ref("rectangle-domain"),
        active_mode_refs=_ordered_refs(_ref("mixed-mode-a"), _ref("mixed-mode-b")),
        topology_snapshot_ref=_ref("topology-snapshot"),
        tolerance_ref=_ref("tolerance"),
        sign_convention_ref=_ref("sign-convention"),
        process_account_refs=accounts,
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["MixedMarginalWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    bracket = tuple(
        (coordinate, _quantity(value, _ref("bracket-unit"), _ref("bracket-dimension"), boundary))
        for coordinate, value in zip(coordinates, (1, 0), strict=True)
    )
    order_difference = tuple(
        (coordinate, _quantity(value, _ref("state-unit"), _ref("state-dimension"), boundary))
        for coordinate, value in zip(coordinates, (4, 0), strict=True)
    )
    remainder = tuple(
        (coordinate, _quantity(0, _ref("state-unit"), _ref("state-dimension"), boundary))
        for coordinate in coordinates
    )
    commutator = _make(
        CommutatorWitness,
        left_generator_ref=_record_ref(left_generator),
        right_generator_ref=_record_ref(right_generator),
        base_state_ref=_ref("commutator-state"),
        boundary_ref=boundary,
        domain_ref=domain,
        topology_ref=topology,
        active_mode_refs=_ordered_refs(_ref("commutator-mode-a"), _ref("commutator-mode-b")),
        step_extent=_quantity(2, extent_unit, extent_dimension, boundary),
        composition_orientation="LEFT_AFTER_RIGHT_MINUS_RIGHT_AFTER_LEFT",
        bracket_components=bracket,
        order_difference_components=order_difference,
        remainder_components=remainder,
        regularity_codes=_ordered_codes(("C2", "LOCAL_LIPSCHITZ"), _REGULARITY),
        commutativity_scope="ONE_STATE",
        commutativity_status="NONCOMMUTING",
        remainder_meaning_ref=_ref("remainder-meaning"),
        process_account_refs=accounts,
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["CommutatorWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    factor = _make(
        SharedConstraintFactor,
        factor_kind="CAPACITY",
        action_refs=actions,
        constraint_ref=_ref("shared-constraint"),
        constraint_unit_ref=_ref("constraint-unit"),
        timing_contract_ref=_ref("timing-contract"),
        hierarchy_kind="TREE",
        ownership_kind="LOWEST_COMPLETE_COMMON_BOUNDARY",
        owner_boundary_ref=boundary,
        lowest_common_boundary_ref=boundary,
        distributed_protocol_ref=Applicability.NOT_APPLICABLE,
        authority_ref=_ref("factor-authority"),
        demand_visibility_refs=actions,
        hidden_state_resolution=_resolution(completed=_ordered_refs(_ref("hidden-a"), _ref("hidden-b"))),
        binding_resolution=_resolution(completed=_ordered_refs(_ref("binding-a"), _ref("binding-b"))),
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["SharedConstraintFactor"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    structural_pair = (actions[0], actions[1], "SHARED_CONSTRAINT", _record_ref(factor))
    structural_hyper = (actions, "MOBIUS_FINITE", _record_ref(finite))
    topology_snapshot = _make(
        InteractionTopologySnapshot,
        boundary_ref=boundary,
        state_ref=finite.initial_augmented_state_ref,
        horizon_ref=horizon,
        subset_protocol_ref=finite.subset_protocol_ref,
        vertex_action_refs=actions,
        structural_pair_edges=(structural_pair,),
        structural_hyperedges=(structural_hyper,),
        active_pair_edges=(structural_pair,),
        active_hyperedges=(structural_hyper,),
        factor_refs=(_record_ref(factor),),
        factor_incidence=tuple((_record_ref(factor), action) for action in actions),
        boundary_node_refs=_ordered_refs(_ref("boundary-node-a"), _ref("boundary-node-b")),
        physical_transport_topology_ref=_ref("physical-topology"),
        institutional_constraint_topology_ref=_ref("institutional-topology"),
        hidden_state_resolution=_resolution(completed=_ordered_refs(_ref("topology-hidden-a"), _ref("topology-hidden-b"))),
        boundary_equivalence_ref=Applicability.NOT_APPLICABLE,
        exposed_interaction_pairs=(),
        boundary_preservation_status="NOT_ASSESSED",
        claim_status=ClaimStatus.DEFINITION,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["InteractionTopologySnapshot"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    selected_quantities = tuple(
        (action, _quantity(value, quantity_unit, quantity_dimension, boundary))
        for action, value in zip(actions, (2, 3), strict=True)
    )
    marginal_values = tuple(
        (action, _quantity(value, marginal_unit, marginal_dimension, boundary))
        for action, value in zip(actions, (4, 5), strict=True)
    )
    allocation = _make(
        AllocationOptimalityWitness,
        objective_ref=_record_ref(objective),
        boundary_ref=boundary,
        horizon_ref=horizon,
        selected_action_refs=actions,
        selected_quantities=selected_quantities,
        selected_mode_refs=_ordered_refs(_ref("selected-mode-a"), _ref("selected-mode-b")),
        feasibility_certificate_ref=_ref("feasibility-certificate"),
        certificate_kind="GLOBAL_DIRECT",
        constraint_qualification_refs=_ordered_refs(_ref("qualification-a"), _ref("qualification-b")),
        convexity_or_globality_refs=_ordered_refs(_ref("globality-a"), _ref("globality-b")),
        active_constraint_refs=objective.feasibility_constraint_refs,
        marginal_values=marginal_values,
        deterministic_tie_rule_ref=objective.deterministic_tie_rule_ref,
        kkt_applicability="NOT_USED",
        result_resolution=_resolution(completed=_ordered_refs(_ref("result-a"), _ref("result-b"))),
        claim_status=ClaimStatus.THEOREM,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["AllocationOptimalityWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    path_ref = _ref("decomposition-path")
    path_provenance = _ordered_refs(path_ref, _record_ref(objective), _record_ref(allocation), *actions)
    decomposition = _make(
        ScalarDecompositionWitness,
        objective_ref=_record_ref(objective),
        allocation_ref=_record_ref(allocation),
        decomposition_kind="AUMANN_SHAPLEY_RADIAL",
        path_ref=path_ref,
        baseline_value=_quantity(5, value_unit, value_dimension, boundary),
        selected_total=_quantity(13, value_unit, value_dimension, boundary),
        shares=tuple(
            (action, _quantity(value, value_unit, value_dimension, boundary))
            for action, value in zip(actions, (3, 4), strict=True)
        ),
        residual=_quantity(1, value_unit, value_dimension, boundary),
        closure_rule="SELECTED_TOTAL_EQUALS_BASELINE_PLUS_SHARES_PLUS_RESIDUAL",
        differentiability_witness_ref=_ref("differentiability"),
        path_provenance_refs=path_provenance,
        closure_resolution=_resolution(completed=_ordered_refs(_ref("closure-a"), _ref("closure-b"))),
        claim_status=ClaimStatus.ALGEBRAIC_IDENTITY,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["ScalarDecompositionWitness"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    issuing_authority = _ref("issuing-authority")
    acceptance = _make(
        InstitutionalAcceptanceRule,
        jurisdiction_ref=_ref("jurisdiction"),
        boundary_ref=boundary,
        issuing_authority_ref=issuing_authority,
        eligible_actor_refs=_ordered_refs(_ref("actor-a"), _ref("actor-b")),
        eligible_action_refs=actions,
        decision_domain_ref=_ref("decision-domain"),
        rule_expression_ref=_ref("rule-expression"),
        priority_rule_ref=_ref("priority-rule"),
        deterministic_tie_rule_ref=_ref("institutional-tie-rule"),
        effective_horizon_ref=horizon,
        appeal_rule_ref=_ref("appeal-rule"),
        expiry_rule_ref=_ref("expiry-rule"),
        cancellation_rule_ref=_ref("cancellation-rule"),
        provenance_authority_refs=_ordered_refs(issuing_authority, _ref("authority-provenance")),
        claim_status=ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["InstitutionalAcceptanceRule"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    settlement_unit = _ref("settlement-unit")
    settlement_dimension = _ref("settlement-dimension")
    settlement = _make(
        InstitutionalSettlementRule,
        acceptance_rule_ref=_record_ref(acceptance),
        jurisdiction_ref=acceptance.jurisdiction_ref,
        boundary_ref=boundary,
        issuing_authority_ref=issuing_authority,
        settlement_basis="INDEPENDENT_INSTITUTIONAL_RULE",
        causal_identification_requirement="NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT",
        causal_claim_status="NOT_MADE",
        share_rule_ref=_ref("share-rule"),
        beneficiary_eligibility_ref=_ref("beneficiary-eligibility"),
        settlement_unit_ref=settlement_unit,
        settlement_dimension_ref=settlement_dimension,
        physical_measurement_ref=_ref("physical-measurement"),
        explicit_residual_required=True,
        closure_rule="MEASURED_TOTAL_EQUALS_SHARE_TOTAL_PLUS_EXPLICIT_RESIDUAL",
        residual_ownership_rule_ref=_ref("residual-ownership"),
        dispute_resolution_rule_ref=_ref("dispute-resolution"),
        effective_horizon_ref=horizon,
        provenance_authority_refs=_ordered_refs(
            issuing_authority, settlement_unit, settlement_dimension, _ref("settlement-provenance")
        ),
        claim_status=ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE,
        nonclaim_codes=_ordered_codes(tuple(_SPEC_BY_NAME["InstitutionalSettlementRule"]["required_nonclaim_codes"]), _NONCLAIMS),
        provenance_refs=provenance,
    )
    preserved = _ordered_refs(
        _ref("preserve-burden"),
        _ref("preserve-conservation"),
        _ref("preserve-loss"),
        _ref("preserve-commitment"),
        _ref("preserve-settlement"),
        _ref("preserve-account-a"),
        _ref("preserve-account-b"),
        _ref("topology-export-a"),
        _ref("topology-export-b"),
    )
    equivalence = _make(
        BoundaryHistoryEquivalenceWitness,
        detailed_boundary_ref=boundary,
        parent_boundary_ref=_ref("parent-boundary"),
        detailed_state_schema_ref=state_schema,
        parent_state_schema_ref=_ref("parent-state-schema"),
        initial_state_relation_ref=_ref("initial-relation"),
        admitted_history_contract_ref=_ref("admitted-history"),
        horizon_ref=horizon,
        equivalence_kind="BISIMULATION",
        evolution_relation_ref=_ref("evolution-relation"),
        observable_codes=_ordered_codes(
            ("TYPED_FLOW", "LOSS", "PENDING_COMMITMENT", "SETTLEMENT_VISIBLE_RECORD"),
            _OBSERVABLES,
        ),
        burden_preservation_ref=preserved[0],
        conservation_preservation_ref=preserved[1],
        loss_preservation_ref=preserved[2],
        commitment_preservation_ref=preserved[3],
        settlement_preservation_ref=preserved[4],
        process_account_preservation_refs=_ordered_refs(preserved[5], preserved[6]),
        hidden_state_relation_preserved=True,
        all_admitted_histories_covered=True,
        snapshot_equality_only=False,
        one_state_generator_equality_only=False,
        internal_topology_export_refs=_ordered_refs(preserved[7], preserved[8]),
        resolution=_resolution(completed=preserved),
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
        runtime_type.__name__: value
        for runtime_type, value in zip(
            _D2_TYPES,
            (
                objective,
                finite,
                same_baseline,
                serial,
                mixed,
                commutator,
                factor,
                topology_snapshot,
                allocation,
                decomposition,
                acceptance,
                settlement,
            ),
            strict=True,
        )
    } | {
        "left_generator": left_generator,
        "right_generator": right_generator,
        "topology_factors": (factor,),
        "topology_interactions": (finite,),
        "topology_equivalence": Applicability.NOT_APPLICABLE,
        "boundary_equivalence": equivalence,
    }


def _set_record(world: dict[str, object], declaration: str, record: object) -> dict[str, object]:
    changed = dict(world)
    changed[declaration] = record
    return changed


def _call_validator(world: dict[str, object], declaration: str) -> None:
    record = world[declaration]
    if declaration == "CommutatorWitness":
        validate_commutator(record, world["left_generator"], world["right_generator"])  # type: ignore[arg-type]
    elif declaration == "InteractionTopologySnapshot":
        validate_interaction_topology_snapshot(
            record,  # type: ignore[arg-type]
            world["topology_factors"],  # type: ignore[arg-type]
            world["topology_interactions"],  # type: ignore[arg-type]
            world["topology_equivalence"],  # type: ignore[arg-type]
        )
    elif declaration == "AllocationOptimalityWitness":
        validate_allocation_optimality(record, world["JointObjectiveDeclaration"])  # type: ignore[arg-type]
    elif declaration == "ScalarDecompositionWitness":
        validate_scalar_decomposition(
            record,  # type: ignore[arg-type]
            world["JointObjectiveDeclaration"],  # type: ignore[arg-type]
            world["AllocationOptimalityWitness"],  # type: ignore[arg-type]
        )
    elif declaration == "InstitutionalSettlementRule":
        validate_institutional_settlement_rule(record, world["InstitutionalAcceptanceRule"])  # type: ignore[arg-type]
    else:
        _VALIDATOR_BY_DECLARATION[declaration](record)  # type: ignore[arg-type]


def _objective_variant(world: dict[str, object], kind: str) -> dict[str, object]:
    record = world["JointObjectiveDeclaration"]
    if kind == "SCALAR":
        changed = _replace_record(
            record,
            objective_kind=kind,
            scalar_objective_ref=_ref("scalar-objective-variant"),
            vector_component_refs=(),
            component_unit_refs=(),
            epsilon_constraint_refs=(),
        )
    else:
        components = _ordered_refs(_ref("component-a"), _ref("component-b"))
        units = (_ref("component-unit-a"), _ref("component-unit-b"))
        epsilon = (
            _ordered_refs(_ref("epsilon-a"), _ref("epsilon-b"))
            if kind == "VECTOR_EPSILON_CONSTRAINT"
            else ()
        )
        changed = _replace_record(
            record,
            objective_kind=kind,
            scalar_objective_ref=Applicability.NOT_APPLICABLE,
            vector_component_refs=components,
            component_unit_refs=units,
            epsilon_constraint_refs=epsilon,
        )
    return _set_record(world, "JointObjectiveDeclaration", changed)


def _mobius_values(
    actions: tuple[ObjectRef, ...], values: dict[tuple[ObjectRef, ...], int]
) -> dict[tuple[ObjectRef, ...], int]:
    coefficients: dict[tuple[ObjectRef, ...], int] = {}
    for size in range(len(actions) + 1):
        for subset in combinations(actions, size):
            coefficients[subset] = sum(
                (-1) ** (len(subset) - inner_size) * values[inner]
                for inner_size in range(len(subset) + 1)
                for inner in combinations(subset, inner_size)
            )
    return coefficients


def _finite_variant(
    world: dict[str, object],
    label: str,
) -> dict[str, object]:
    record = world["FiniteSetInteractionWitness"]
    actions = record.action_refs
    normalization = "RAW_WITH_EXPLICIT_EMPTY"
    empty = 0
    values: dict[tuple[ObjectRef, ...], int]
    truncation: IntegerV1 | Applicability = Applicability.NOT_APPLICABLE
    if label == "PURE_THREE_WAY_ZERO_PAIRS":
        actions = _ordered_refs(*actions, _ref("action-c"))
        a, b, c = actions
        values = {
            (): 0,
            (a,): 1,
            (b,): 2,
            (c,): 3,
            (a, b): 3,
            (a, c): 4,
            (b, c): 5,
            (a, b, c): 9,
        }
    elif label in {"NORMALIZED_EMPTY_BASELINE", "NORMALIZED_BY_EMPTY"}:
        a, b = actions
        normalization = "NORMALIZED_BY_EMPTY"
        empty = 5
        values = {(): 0, (a,): 3, (b,): 4, (a, b): 10}
    else:
        a, b = actions
        pair = {"ZERO_PAIR": 3, "NEGATIVE_PAIR": 2}.get(label, 4)
        if label in {"NONZERO_EMPTY_BASELINE", "EXACT_FULL_RECONSTRUCTION", "EXACT_TRUNCATION_RESIDUAL"}:
            empty = 5
            values = {(): 5, (a,): 8, (b,): 9, (a, b): 15}
        else:
            values = {(): 0, (a,): 1, (b,): 2, (a, b): pair}
        if label == "EXACT_TRUNCATION_RESIDUAL":
            truncation = IntegerV1(1)
    coefficients = _mobius_values(actions, values)
    ordered_subsets = tuple(
        subset
        for size in range(len(actions) + 1)
        for subset in combinations(actions, size)
    )
    value_rows = tuple(
        (subset, _quantity(values[subset], record.value_unit_ref, record.value_dimension_ref, record.boundary_ref))
        for subset in ordered_subsets
    )
    coefficient_rows = tuple(
        (subset, _quantity(coefficients[subset], record.value_unit_ref, record.value_dimension_ref, record.boundary_ref))
        for subset in ordered_subsets
    )
    residuals: tuple[tuple[tuple[ObjectRef, ...], Quantity], ...] = ()
    if type(truncation) is IntegerV1:
        residuals = tuple(
            (
                subset,
                _quantity(
                    values[subset]
                    - sum(
                        coefficients[inner]
                        for inner_size in range(truncation.value + 1)
                        for inner in combinations(subset, inner_size)
                    ),
                    record.value_unit_ref,
                    record.value_dimension_ref,
                    record.boundary_ref,
                ),
            )
            for subset in ordered_subsets
            if len(subset) > truncation.value
        )
    changed = _replace_record(
        record,
        action_refs=actions,
        subset_values=value_rows,
        empty_baseline=_quantity(empty, record.value_unit_ref, record.value_dimension_ref, record.boundary_ref),
        mobius_coefficients=coefficient_rows,
        normalization=normalization,
        truncation_order=truncation,
        truncation_residuals=residuals,
    )
    return _set_record(world, "FiniteSetInteractionWitness", changed)


def _zero_commutator(world: dict[str, object], status: str, scope: str) -> dict[str, object]:
    record = world["CommutatorWitness"]
    bracket = tuple((ref, _quantity_change(quantity, magnitude=IntegerV1(0))) for ref, quantity in record.bracket_components)
    order = tuple((ref, _quantity_change(quantity, magnitude=IntegerV1(0))) for ref, quantity in record.order_difference_components)
    changed = _replace_record(
        record,
        bracket_components=bracket,
        order_difference_components=order,
        commutativity_status=status,
        commutativity_scope=scope,
    )
    return _set_record(world, "CommutatorWitness", changed)


def _factor_variant(world: dict[str, object], ownership: str, hierarchy: str) -> dict[str, object]:
    record = world["SharedConstraintFactor"]
    lowest: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    distributed: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    if ownership == "LOWEST_COMPLETE_COMMON_BOUNDARY":
        hierarchy = "TREE"
        lowest = record.owner_boundary_ref
    elif ownership == "DISTRIBUTED_PROTOCOL":
        if hierarchy not in {"FEDERATION", "OVERLAPPING_AUTHORITY"}:
            hierarchy = "FEDERATION"
        distributed = _ref("distributed-protocol")
    changed = _replace_record(
        record,
        hierarchy_kind=hierarchy,
        ownership_kind=ownership,
        lowest_common_boundary_ref=lowest,
        distributed_protocol_ref=distributed,
    )
    return _set_record(world, "SharedConstraintFactor", changed)


def _preserved_topology(world: dict[str, object]) -> dict[str, object]:
    record = world["InteractionTopologySnapshot"]
    equivalence = world["boundary_equivalence"]
    actions = record.vertex_action_refs
    changed = _replace_record(
        record,
        boundary_equivalence_ref=_record_ref(equivalence),
        exposed_interaction_pairs=((actions[0], actions[1]),),
        boundary_preservation_status="PRESERVED_ALL_EXPOSED_SUBSETS",
    )
    result = _set_record(world, "InteractionTopologySnapshot", changed)
    result["topology_equivalence"] = equivalence
    return result


def _allocation_variant(world: dict[str, object], kind: str, kkt: str | None = None) -> dict[str, object]:
    objective_kind = {
        "PARETO": "VECTOR_PARETO",
        "LEXICOGRAPHIC": "VECTOR_LEXICOGRAPHIC",
        "EPSILON_CONSTRAINT": "VECTOR_EPSILON_CONSTRAINT",
    }.get(kind, "SCALAR")
    changed = _objective_variant(world, objective_kind)
    objective = changed["JointObjectiveDeclaration"]
    record = changed["AllocationOptimalityWitness"]
    default_kkt = {
        "KKT_LOCAL": "APPLICABLE_LOCAL_ONLY",
        "KKT_GLOBAL_CONVEX": "APPLICABLE_GLOBAL_WITH_CONVEXITY",
        "COMBINATORIAL": "INAPPLICABLE_DISCRETE_OR_NONSMOOTH",
        "MIXED_INTEGER": "INAPPLICABLE_DISCRETE_OR_NONSMOOTH",
    }.get(kind, "NOT_USED")
    updated = _replace_record(
        record,
        objective_ref=_record_ref(objective),
        boundary_ref=objective.boundary_ref,
        horizon_ref=objective.horizon_ref,
        deterministic_tie_rule_ref=objective.deterministic_tie_rule_ref,
        certificate_kind=kind,
        kkt_applicability=default_kkt if kkt is None else kkt,
    )
    return _set_record(changed, "AllocationOptimalityWitness", updated)


def _enum_world(world: dict[str, object], declaration: str, field_name: str, value: str) -> dict[str, object]:
    record = world[declaration]
    if declaration == "JointObjectiveDeclaration" and field_name == "objective_kind":
        return _objective_variant(world, value)
    if declaration == "FiniteSetInteractionWitness" and field_name == "normalization":
        return _finite_variant(world, value)
    if declaration == "MixedMarginalWitness" and field_name == "regularity_status":
        normalized: Quantity | ResolutionDetail = record.normalized_mixed_marginal  # type: ignore[attr-defined]
        if value != "C2_ON_COMPLETE_RECTANGLE":
            normalized = _resolution(state=ResolutionState.UNRESOLVED)
        return _set_record(
            world,
            declaration,
            _replace_record(record, regularity_status=value, normalized_mixed_marginal=normalized),
        )
    if declaration == "CommutatorWitness" and field_name in {"commutativity_scope", "commutativity_status"}:
        status = value if field_name == "commutativity_status" else record.commutativity_status  # type: ignore[attr-defined]
        scope = value if field_name == "commutativity_scope" else record.commutativity_scope  # type: ignore[attr-defined]
        if status == "COMMUTING_ON_DECLARED_NEIGHBOURHOOD":
            return _zero_commutator(world, status, "DECLARED_NEIGHBOURHOOD")
        if status == "ZERO_AT_ONE_STATE_ONLY":
            return _zero_commutator(world, status, "ONE_STATE")
        if status == "NONCOMMUTING":
            scope = scope if scope in {"ONE_STATE", "DECLARED_NEIGHBOURHOOD"} else "ONE_STATE"
            return _set_record(world, declaration, _replace_record(record, commutativity_status=status, commutativity_scope=scope))
        if status == "UNRESOLVED":
            return _zero_commutator(world, status, scope)
        if field_name == "commutativity_scope" and value == "DECLARED_NEIGHBOURHOOD":
            return _set_record(world, declaration, _replace_record(record, commutativity_scope=value))
    if declaration == "SharedConstraintFactor" and field_name in {"hierarchy_kind", "ownership_kind"}:
        if field_name == "ownership_kind":
            return _factor_variant(world, value, record.hierarchy_kind)  # type: ignore[attr-defined]
        ownership = record.ownership_kind  # type: ignore[attr-defined]
        if value == "DAG":
            ownership = "DECLARED_FACTOR_BOUNDARY"
        elif value in {"FEDERATION", "OVERLAPPING_AUTHORITY"}:
            ownership = "DISTRIBUTED_PROTOCOL"
        else:
            ownership = "LOWEST_COMPLETE_COMMON_BOUNDARY"
        return _factor_variant(world, ownership, value)
    if declaration == "InteractionTopologySnapshot" and field_name == "boundary_preservation_status":
        if value == "PRESERVED_ALL_EXPOSED_SUBSETS":
            return _preserved_topology(world)
        return _set_record(
            world,
            declaration,
            _replace_record(record, boundary_preservation_status=value),
        )
    if declaration == "AllocationOptimalityWitness" and field_name == "certificate_kind":
        return _allocation_variant(world, value)
    if declaration == "AllocationOptimalityWitness" and field_name == "kkt_applicability":
        kind = {
            "APPLICABLE_LOCAL_ONLY": "KKT_LOCAL",
            "APPLICABLE_GLOBAL_WITH_CONVEXITY": "KKT_GLOBAL_CONVEX",
            "INAPPLICABLE_DISCRETE_OR_NONSMOOTH": "COMBINATORIAL",
            "NOT_USED": "GLOBAL_DIRECT",
        }[value]
        return _allocation_variant(world, kind, value)
    if declaration == "ScalarDecompositionWitness" and field_name == "decomposition_kind":
        differentiability = (
            record.differentiability_witness_ref  # type: ignore[attr-defined]
            if value == "AUMANN_SHAPLEY_RADIAL"
            else Applicability.NOT_APPLICABLE
        )
        return _set_record(
            world,
            declaration,
            _replace_record(record, decomposition_kind=value, differentiability_witness_ref=differentiability),
        )
    if declaration == "InstitutionalSettlementRule" and field_name in {
        "settlement_basis",
        "causal_identification_requirement",
        "causal_claim_status",
    }:
        causal = value in {
            "IDENTIFIED_CAUSAL_RULE",
            "IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM",
            "IDENTIFIED",
        }
        return _set_record(
            world,
            declaration,
            _replace_record(
                record,
                settlement_basis="IDENTIFIED_CAUSAL_RULE" if causal else "INDEPENDENT_INSTITUTIONAL_RULE",
                causal_identification_requirement=(
                    "IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM"
                    if causal
                    else "NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT"
                ),
                causal_claim_status="IDENTIFIED" if causal else "NOT_MADE",
            ),
        )
    return _set_record(world, declaration, _replace_record(record, **{field_name: value}))


def _nested_enum_world(
    world: dict[str, object], field_name: str, value: str
) -> dict[str, object]:
    record = world["InteractionTopologySnapshot"]
    actions = record.vertex_action_refs
    factor = world["SharedConstraintFactor"]
    finite = world["FiniteSetInteractionWitness"]
    witness = _record_ref(factor) if value == "SHARED_CONSTRAINT" else _record_ref(finite)
    if "pair" in field_name:
        row = (actions[0], actions[1], value, witness)
    else:
        row = (actions, value, witness)
    changes: dict[str, object] = {field_name: (row,)}
    if field_name.startswith("structural_"):
        active_name = field_name.replace("structural_", "active_")
        changes[active_name] = ()
    elif field_name.startswith("active_"):
        structural_name = field_name.replace("active_", "structural_")
        changes[structural_name] = (row,)
    return _set_record(world, "InteractionTopologySnapshot", _replace_record(record, **changes))


def _collection_seed(world: dict[str, object], declaration: str, field_name: str) -> tuple[object, ...]:
    record = world[declaration]
    current = getattr(record, field_name)
    if len(current) >= 2:
        return current
    spec = next(row for row in _SPEC_BY_NAME[declaration]["fields"] if row[0] == field_name)[1]
    first, second = _ordered_refs(_ref(f"{declaration}-{field_name}-a"), _ref(f"{declaration}-{field_name}-b"))
    boundary = getattr(record, "boundary_ref", _ref("collection-boundary"))
    unit = _ref(f"{field_name}-unit")
    dimension = _ref(f"{field_name}-dimension")
    if "@CANONICAL_EDGE" in spec:
        actions = world["FiniteSetInteractionWitness"].action_refs  # type: ignore[attr-defined]
        return (
            (actions[0], actions[1], "MOBIUS_FINITE", _record_ref(world["FiniteSetInteractionWitness"])),
            (actions[0], actions[1], "SHARED_CONSTRAINT", _record_ref(world["SharedConstraintFactor"])),
        )
    if "@CANONICAL_HYPEREDGE" in spec:
        actions = world["FiniteSetInteractionWitness"].action_refs  # type: ignore[attr-defined]
        return (
            (actions, "MOBIUS_FINITE", _record_ref(world["FiniteSetInteractionWitness"])),
            (actions, "SHARED_CONSTRAINT", _record_ref(world["SharedConstraintFactor"])),
        )
    if "tuple[tuple[tuple[ObjectRef" in spec:
        action = world["FiniteSetInteractionWitness"].action_refs[0]  # type: ignore[attr-defined]
        return (
            ((), _quantity(0, unit, dimension, boundary)),
            ((action,), _quantity(1, unit, dimension, boundary)),
        )
    if "tuple[tuple[ObjectRef,Quantity]" in spec:
        return (
            (first, _quantity(1, unit, dimension, boundary)),
            (second, _quantity(2, unit, dimension, boundary)),
        )
    if "tuple[tuple[ObjectRef,ObjectRef]" in spec:
        return ((first, second), (second, first))
    if "tuple[str" in spec:
        domain = _REGULARITY if field_name == "regularity_codes" else _NONCLAIMS
        return (domain[0], domain[1])
    return (first, second)


def _collection_world(
    world: dict[str, object], declaration: str, field_name: str, duplicate: bool
) -> dict[str, object]:
    record = world[declaration]
    seed = _collection_seed(world, declaration, field_name)
    values = (seed[0], seed[0]) if duplicate else tuple(reversed(seed))
    return _set_record(world, declaration, _replace_record(record, **{field_name: values}))


def _failure_world(world: dict[str, object], declaration: str, code: str) -> dict[str, object]:
    record = world[declaration]
    if code == "I3_OBJECT_CONTENT_MISMATCH":
        return _set_record(world, declaration, _corrupt_payload(record))
    if code == "I3_COLLECTION_ORDER_INVALID":
        return _collection_world(world, declaration, "provenance_refs", False)
    if code == "I3_DUPLICATE_MEMBER":
        return _collection_world(world, declaration, "provenance_refs", True)
    if code == "IMPLICIT_ABSENCE_FORBIDDEN":
        field_name = {
            "JointObjectiveDeclaration": "scalar_objective_ref",
            "FiniteSetInteractionWitness": "truncation_order",
            "SharedConstraintFactor": "constraint_unit_ref",
            "InteractionTopologySnapshot": "physical_transport_topology_ref",
            "ScalarDecompositionWitness": "differentiability_witness_ref",
        }[declaration]
        return _set_record(
            world, declaration, _replace_record(record, **{field_name: Applicability.APPLICABLE})
        )
    if code == "UNIT_MISMATCH":
        wrong = _ref("wrong-unit")
        if declaration == "JointObjectiveDeclaration":
            changed = _objective_variant(world, "VECTOR_PARETO")
            record = changed[declaration]
            return _set_record(
                changed,
                declaration,
                _replace_record(record, component_unit_refs=(record.component_unit_refs[0],)),  # type: ignore[attr-defined]
            )
        quantity_field = {
            "FiniteSetInteractionWitness": "empty_baseline",
            "SameBaselineNonadditivityWitness": "joint_value",
            "SerialComparatorInteractionWitness": "parallel_value",
            "MixedMarginalWitness": "delta_i",
            "CommutatorWitness": "step_extent",
            "ScalarDecompositionWitness": "selected_total",
        }.get(declaration)
        if quantity_field is not None:
            quantity = getattr(record, quantity_field)
            return _set_record(
                world,
                declaration,
                _replace_record(record, **{quantity_field: _quantity_change(quantity, unit_ref=wrong)}),
            )
        if declaration == "AllocationOptimalityWitness":
            rows = list(record.selected_quantities)  # type: ignore[attr-defined]
            rows[0] = (rows[0][0], _quantity_change(rows[0][1], unit_ref=wrong))
            return _set_record(world, declaration, _replace_record(record, selected_quantities=tuple(rows)))
        return _set_record(world, declaration, _replace_record(record, settlement_unit_ref=wrong))
    if code == "DIMENSION_MISMATCH":
        wrong = _ref("wrong-dimension")
        quantity_field = {
            "FiniteSetInteractionWitness": "empty_baseline",
            "SameBaselineNonadditivityWitness": "joint_value",
            "SerialComparatorInteractionWitness": "parallel_value",
            "MixedMarginalWitness": "delta_i",
            "CommutatorWitness": "step_extent",
            "ScalarDecompositionWitness": "selected_total",
        }.get(declaration)
        if quantity_field is not None:
            quantity = getattr(record, quantity_field)
            return _set_record(
                world,
                declaration,
                _replace_record(record, **{quantity_field: _quantity_change(quantity, dimension_ref=wrong)}),
            )
        return _set_record(world, declaration, _replace_record(record, settlement_dimension_ref=wrong))
    if code == "OBJECTIVE_GRAMMAR_INVALID":
        changed = _replace_record(record, feasibility_first=False)
    elif code == "SUBSET_PROTOCOL_INCOMPLETE":
        changed = _replace_record(record, process_account_refs=())
    elif code == "SUBSET_LATTICE_INCOMPLETE":
        changed = _replace_record(record, subset_values=record.subset_values[:-1])  # type: ignore[attr-defined]
    elif code == "MOBIUS_CLOSURE_FAILURE":
        rows = list(record.mobius_coefficients)  # type: ignore[attr-defined]
        rows[-1] = (rows[-1][0], _quantity_change(rows[-1][1], magnitude=IntegerV1(99)))
        changed = _replace_record(record, mobius_coefficients=tuple(rows))
    elif code == "TRUNCATION_RESIDUAL_MISMATCH":
        world = _finite_variant(world, "EXACT_TRUNCATION_RESIDUAL")
        record = world[declaration]
        rows = list(record.truncation_residuals)  # type: ignore[attr-defined]
        rows[-1] = (rows[-1][0], _quantity_change(rows[-1][1], magnitude=IntegerV1(99)))
        changed = _replace_record(record, truncation_residuals=tuple(rows))
    elif code == "COMPARATOR_INTERACTION_INVALID":
        if declaration == "SameBaselineNonadditivityWitness":
            changed = _replace_record(
                record,
                nonadditivity_value=_quantity_change(record.nonadditivity_value, magnitude=IntegerV1(99)),  # type: ignore[attr-defined]
            )
        else:
            changed = _replace_record(record, serial_order_refs=record.serial_order_refs[:-1])  # type: ignore[attr-defined]
    elif code == "MIXED_MARGINAL_WITNESS_INVALID":
        changed = _replace_record(
            record,
            mixed_difference=_quantity_change(record.mixed_difference, magnitude=IntegerV1(99)),  # type: ignore[attr-defined]
        )
    elif code == "COMMUTATOR_WITNESS_INVALID":
        changed = _replace_record(record, domain_ref=_ref("wrong-domain"))
    elif code == "COMMUTATIVITY_SCOPE_OVERCLAIM":
        return _zero_commutator(world, "COMMUTING_ON_DECLARED_NEIGHBOURHOOD", "ONE_STATE")
    elif code == "SHARED_BOUNDARY_VISIBILITY_MISSING":
        changed = _replace_record(record, demand_visibility_refs=())
    elif code == "SHARED_CONSTRAINT_OWNERSHIP_INVALID":
        changed = _replace_record(record, hierarchy_kind="DAG")
    elif code == "INTERACTION_TOPOLOGY_INVALID":
        changed = _replace_record(record, structural_hyperedges=())
    elif code == "HIDDEN_STATE_TOPOLOGY_UNRESOLVED":
        changed = _replace_record(
            record,
            hidden_state_resolution=_resolution(
                missing=_ordered_refs(_ref("missing-hidden-a"), _ref("missing-hidden-b")),
                state=ResolutionState.UNRESOLVED,
            ),
        )
    elif code == "BOUNDARY_INTERACTION_PRESERVATION_INVALID":
        preserved = _preserved_topology(world)
        finite = preserved["FiniteSetInteractionWitness"]
        incomplete = _replace_record(finite, subset_values=finite.subset_values[:-1])  # type: ignore[attr-defined]
        topology = preserved[declaration]
        structural_hyperedges = tuple(
            (actions, kind, _record_ref(incomplete) if witness == _record_ref(finite) else witness)
            for actions, kind, witness in topology.structural_hyperedges  # type: ignore[attr-defined]
        )
        active_hyperedges = tuple(
            (actions, kind, _record_ref(incomplete) if witness == _record_ref(finite) else witness)
            for actions, kind, witness in topology.active_hyperedges  # type: ignore[attr-defined]
        )
        preserved = _set_record(
            preserved,
            declaration,
            _replace_record(
                topology,
                structural_hyperedges=structural_hyperedges,
                active_hyperedges=active_hyperedges,
            ),
        )
        preserved["FiniteSetInteractionWitness"] = incomplete
        preserved["topology_interactions"] = (incomplete,)
        return preserved
    elif code == "ALLOCATION_FEASIBILITY_INVALID":
        changed = _replace_record(record, selected_action_refs=_ordered_refs(_ref("foreign-a"), _ref("foreign-b")))
    elif code == "OPTIMALITY_CERTIFICATE_INAPPLICABLE":
        world = _allocation_variant(world, "KKT_GLOBAL_CONVEX")
        record = world[declaration]
        changed = _replace_record(record, convexity_or_globality_refs=())
    elif code == "SCALAR_DECOMPOSITION_INVALID":
        changed = _replace_record(
            record,
            selected_total=_quantity_change(record.selected_total, magnitude=IntegerV1(99)),  # type: ignore[attr-defined]
        )
    elif code == "DECOMPOSITION_PROVENANCE_INCOMPLETE":
        changed = _replace_record(
            record,
            path_provenance_refs=tuple(
                item for item in record.path_provenance_refs if item != record.path_ref  # type: ignore[attr-defined]
            ),
        )
    elif code == "INSTITUTIONAL_RULE_INVALID":
        if declaration == "InstitutionalAcceptanceRule":
            changed = _replace_record(record, eligible_actor_refs=())
        else:
            changed = _replace_record(record, effective_horizon_ref=_ref("wrong-horizon"))
    elif code == "CAUSAL_SETTLEMENT_CONFLATION":
        changed = _replace_record(record, causal_claim_status="IDENTIFIED")
    elif code == "SETTLEMENT_RESIDUAL_CLOSURE_MISSING":
        changed = _replace_record(record, explicit_residual_required=False)
    else:
        raise AssertionError(f"unsupported failure mutation {declaration} {code}")
    return _set_record(world, declaration, changed)


def _precedence_world(
    world: dict[str, object], declaration: str, active: tuple[str, ...]
) -> tuple[dict[str, object], bool, str | None]:
    changed = dict(world)
    attach_runtime = "FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR" in active
    prohibited = next(
        (value for value in ("WAVE", "PHASE_SUPERPOSITION", "PHYSICAL_INTERFERENCE", "ELECTRICAL_VOLTAGE") if "PROHIBITED_INTERFERENCE_CLAIM" in active),
        None,
    )
    structural = {
        "I3_OBJECT_CONTENT_MISMATCH",
        "I3_COLLECTION_ORDER_INVALID",
        "I3_DUPLICATE_MEMBER",
        "FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR",
        "PROHIBITED_INTERFERENCE_CLAIM",
        "HASH_MISMATCH",
    }
    for code in reversed(tuple(code for code in active if code not in structural)):
        changed = _failure_world(changed, declaration, code)
    if "I3_COLLECTION_ORDER_INVALID" in active and "I3_DUPLICATE_MEMBER" in active:
        record = changed[declaration]
        provenance = record.provenance_refs  # type: ignore[attr-defined]
        changed = _set_record(
            changed,
            declaration,
            _replace_record(record, provenance_refs=(provenance[1], provenance[0], provenance[0])),
        )
    elif "I3_COLLECTION_ORDER_INVALID" in active:
        changed = _failure_world(changed, declaration, "I3_COLLECTION_ORDER_INVALID")
    elif "I3_DUPLICATE_MEMBER" in active:
        changed = _failure_world(changed, declaration, "I3_DUPLICATE_MEMBER")
    if "I3_OBJECT_CONTENT_MISMATCH" in active:
        changed = _failure_world(changed, declaration, "I3_OBJECT_CONTENT_MISMATCH")
    if "HASH_MISMATCH" in active:
        changed = _set_record(changed, declaration, _corrupt_hash(changed[declaration]))
    return changed, attach_runtime, prohibited


def _semantic_world(
    world: dict[str, object], declaration: str, mutation: str
) -> tuple[dict[str, object], str | None]:
    record = world[declaration]
    if mutation == "SCALAR_OBJECTIVE_VALID":
        return _objective_variant(world, "SCALAR"), None
    if mutation.startswith("VECTOR_OBJECTIVE_VALID:"):
        return _objective_variant(world, mutation.split(":", 1)[1]), None
    if mutation == "FEASIBILITY_FIRST_FALSE":
        return _failure_world(world, declaration, "OBJECTIVE_GRAMMAR_INVALID"), None
    if mutation == "SCALAR_VECTOR_ARM_CONTRADICTION":
        return _set_record(
            world,
            declaration,
            _replace_record(record, vector_component_refs=_ordered_refs(_ref("contradiction-a"), _ref("contradiction-b"))),
        ), None
    if mutation.startswith("INTERACTION_VALID:"):
        label = mutation.split(":", 1)[1]
        if label == "QUANTITY_FIXED_PROTOCOL":
            return _set_record(world, declaration, _replace_record(record, action_removal_semantics="QUANTITY_FIXED")), None
        if label == "RULE_REPLAYED_PROTOCOL":
            return _set_record(world, declaration, _replace_record(record, action_removal_semantics="RULE_REPLAYED")), None
        return _finite_variant(world, label), None
    if mutation == "MISSING_EMPTY_BASELINE":
        return _set_record(world, declaration, _replace_record(record, subset_values=record.subset_values[1:])), None  # type: ignore[attr-defined]
    if mutation == "INCOMPLETE_SUBSET_LATTICE":
        return _failure_world(world, declaration, "SUBSET_LATTICE_INCOMPLETE"), None
    if mutation == "INADMISSIBLE_REQUIRED_SUBSET":
        rows = list(record.subset_values)  # type: ignore[attr-defined]
        rows[-1] = ((_ref("foreign-action"),), rows[-1][1])
        return _set_record(world, declaration, _replace_record(record, subset_values=tuple(rows))), None
    if mutation == "INCOMPLETE_PROCESS_ACCOUNTS":
        return _failure_world(world, declaration, "SUBSET_PROTOCOL_INCOMPLETE"), None
    if mutation == "MOBIUS_COEFFICIENT_WRONG":
        return _failure_world(world, declaration, "MOBIUS_CLOSURE_FAILURE"), None
    if mutation == "TRUNCATION_RESIDUAL_WRONG":
        return _failure_world(world, declaration, "TRUNCATION_RESIDUAL_MISMATCH"), None
    if mutation == "MIXED_VALUE_UNITS":
        return _failure_world(world, declaration, "UNIT_MISMATCH"), None
    if mutation in {"SAME_BASELINE_VALID", "SERIAL_COMPARATOR_VALID", "SMOOTH_C2_VALID", "TREE_LCA_VALID", "ACCEPTANCE_RULE_VALID", "SCALAR_GLOBAL_VALID", "AUMANN_SHAPLEY_VALID", "UNIDENTIFIED_INSTITUTIONAL_SETTLEMENT_VALID", "STRUCTURAL_VS_ACTIVE_VALID"}:
        if mutation == "STRUCTURAL_VS_ACTIVE_VALID":
            return _set_record(world, declaration, _replace_record(record, active_pair_edges=())), None
        return world, None
    if mutation == "BASELINE_MISMATCH":
        return _failure_world(world, declaration, "COMPARATOR_INTERACTION_INVALID"), None
    if mutation == "SERIAL_ORDER_MISSING":
        return _failure_world(world, declaration, "COMPARATOR_INTERACTION_INVALID"), None
    if mutation == "NONSMOOTH_VALID":
        return _set_record(
            world,
            declaration,
            _replace_record(
                record,
                regularity_status="NONSMOOTH_FINITE_DIFFERENCE_ONLY",
                normalized_mixed_marginal=_resolution(state=ResolutionState.UNRESOLVED),
            ),
        ), None
    if mutation == "NONSMOOTH_C2_OVERCLAIM":
        return _set_record(
            world,
            declaration,
            _replace_record(record, regularity_status="NONSMOOTH_FINITE_DIFFERENCE_ONLY"),
        ), None
    if mutation == "COMMUTING_VALID":
        return _zero_commutator(world, "COMMUTING_ON_DECLARED_NEIGHBOURHOOD", "DECLARED_NEIGHBOURHOOD"), None
    if mutation == "NONCOMMUTING_VALID":
        return world, None
    if mutation == "ONE_STATE_ZERO_VALID":
        return _zero_commutator(world, "ZERO_AT_ONE_STATE_ONLY", "ONE_STATE"), None
    if mutation == "ONE_STATE_TO_NEIGHBOURHOOD_OVERCLAIM":
        return _failure_world(world, declaration, "COMMUTATIVITY_SCOPE_OVERCLAIM"), None
    if mutation == "DAG_AUTOMATIC_LCA":
        return _set_record(world, declaration, _replace_record(record, hierarchy_kind="DAG")), None
    if mutation == "FACTOR_BOUNDARY_VALID":
        return _factor_variant(world, "DECLARED_FACTOR_BOUNDARY", "DAG"), None
    if mutation == "FEDERATION_DISTRIBUTED_VALID":
        return _factor_variant(world, "DISTRIBUTED_PROTOCOL", "FEDERATION"), None
    if mutation == "MISSING_BOUNDARY_VISIBILITY":
        return _failure_world(world, declaration, "SHARED_BOUNDARY_VISIBILITY_MISSING"), None
    if mutation == "PURE_HYPEREDGE_VALID":
        changed = _finite_variant(world, "PURE_THREE_WAY_ZERO_PAIRS")
        finite = changed["FiniteSetInteractionWitness"]
        hyperedge = (
            finite.action_refs,  # type: ignore[attr-defined]
            "MOBIUS_FINITE",
            _record_ref(finite),
        )
        topology = _replace_record(
            record,
            vertex_action_refs=finite.action_refs,  # type: ignore[attr-defined]
            structural_pair_edges=(),
            structural_hyperedges=(hyperedge,),
            active_pair_edges=(),
            active_hyperedges=(hyperedge,),
        )
        changed = _set_record(changed, declaration, topology)
        changed["topology_interactions"] = (finite,)
        return changed, None
    if mutation == "HIDDEN_STATE_TOPOLOGY_FAILURE":
        return _failure_world(world, declaration, "HIDDEN_STATE_TOPOLOGY_UNRESOLVED"), None
    if mutation == "TOPOLOGY_TYPES_DISTINCT":
        actions = record.vertex_action_refs  # type: ignore[attr-defined]
        rows = []
        for interaction_type in _INTERACTION_TYPES:
            witness = (
                _record_ref(world["FiniteSetInteractionWitness"])
                if interaction_type == "MOBIUS_FINITE"
                else _record_ref(world["SharedConstraintFactor"])
                if interaction_type == "SHARED_CONSTRAINT"
                else _ref(f"typed-witness-{interaction_type.lower()}")
            )
            rows.append((actions[0], actions[1], interaction_type, witness))
        return _set_record(
            world,
            declaration,
            _replace_record(record, structural_pair_edges=tuple(rows), active_pair_edges=()),
        ), None
    if mutation == "BOUNDARY_PRESERVATION_VALID":
        return _preserved_topology(world), None
    if mutation == "BOUNDARY_PRESERVATION_INVALID":
        return _failure_world(world, declaration, "BOUNDARY_INTERACTION_PRESERVATION_INVALID"), None
    if mutation == "VECTOR_PARETO_VALID":
        return _allocation_variant(world, "PARETO"), None
    if mutation == "KKT_LOCAL_MARGINAL_EQUALIZATION_VALID":
        return _allocation_variant(world, "KKT_LOCAL"), None
    if mutation == "KKT_INAPPLICABLE":
        return _allocation_variant(world, "KKT_LOCAL", "INAPPLICABLE_DISCRETE_OR_NONSMOOTH"), None
    if mutation == "KKT_GLOBAL_UNSUPPORTED":
        return _failure_world(world, declaration, "OPTIMALITY_CERTIFICATE_INAPPLICABLE"), None
    if mutation == "OTHER_PATH_VALID":
        return _set_record(
            world,
            declaration,
            _replace_record(
                record,
                decomposition_kind="OTHER_DECLARED_PATH",
                differentiability_witness_ref=Applicability.NOT_APPLICABLE,
            ),
        ), None
    if mutation == "DECOMPOSITION_NONCLOSURE":
        return _failure_world(world, declaration, "SCALAR_DECOMPOSITION_INVALID"), None
    if mutation == "MISSING_PATH_PROVENANCE":
        return _failure_world(world, declaration, "DECOMPOSITION_PROVENANCE_INCOMPLETE"), None
    if mutation == "IDENTIFIED_CAUSAL_SETTLEMENT_VALID":
        return _enum_world(world, declaration, "settlement_basis", "IDENTIFIED_CAUSAL_RULE"), None
    if mutation == "CAUSAL_RELABEL_REJECT":
        return _failure_world(world, declaration, "CAUSAL_SETTLEMENT_CONFLATION"), None
    if mutation == "RESIDUAL_CLOSURE_MISSING":
        return _failure_world(world, declaration, "SETTLEMENT_RESIDUAL_CLOSURE_MISSING"), None
    if mutation.startswith("PROHIBITED_CLAIM:"):
        return world, mutation.split(":", 1)[1]
    raise AssertionError(f"unhandled semantic mutation {declaration} {mutation}")


def _applicability_world(
    world: dict[str, object], declaration: str, field_name: str
) -> dict[str, object]:
    record = world[declaration]
    if declaration == "JointObjectiveDeclaration":
        return _objective_variant(world, "VECTOR_PARETO")
    if declaration == "SharedConstraintFactor" and field_name == "lowest_common_boundary_ref":
        return _factor_variant(world, "DECLARED_FACTOR_BOUNDARY", "DAG")
    if declaration == "ScalarDecompositionWitness":
        return _set_record(
            world,
            declaration,
            _replace_record(
                record,
                decomposition_kind="OTHER_DECLARED_PATH",
                differentiability_witness_ref=Applicability.NOT_APPLICABLE,
            ),
        )
    return _set_record(
        world,
        declaration,
        _replace_record(record, **{field_name: Applicability.NOT_APPLICABLE}),
    )


def _mutated_world(
    world: dict[str, object], vector: dict[str, object]
) -> tuple[dict[str, object], bool, str | None]:
    declaration = vector["declaration"]
    category = vector["category"]
    mutation = vector["mutation"]
    assert type(declaration) is str and type(category) is str and type(mutation) is str
    if category == "DECLARATION_SUCCESS":
        return world, False, None
    if category == "ENUM_MEMBER_BOUNDARY":
        if mutation.startswith("VALID_ENUM:"):
            field_name, value = mutation.removeprefix("VALID_ENUM:").split("=", 1)
            return _enum_world(world, declaration, field_name, value), False, None
        _, field_name, value = mutation.split(":", 2)
        return _nested_enum_world(world, field_name, value), False, None
    if category == "APPLICABILITY_BOUNDARY":
        return _applicability_world(world, declaration, mutation.split(":", 1)[1]), False, None
    if category == "COLLECTION_ORDER":
        return _collection_world(world, declaration, mutation.split(":", 1)[1], False), False, None
    if category == "COLLECTION_DUPLICATE":
        return _collection_world(world, declaration, mutation.split(":", 1)[1], True), False, None
    if category == "CLAIM_STATUS_ALLOWED":
        status = ClaimStatus(mutation.split(":", 1)[1])
        return _set_record(world, declaration, _replace_record(world[declaration], claim_status=status)), False, None
    if category == "CLAIM_STATUS_REJECTED":
        status = ClaimStatus(mutation.split(":", 1)[1])
        return _set_record(world, declaration, _replace_record(world[declaration], claim_status=status)), False, None
    if category == "NONCLAIM_REQUIRED":
        record = world[declaration]
        required = _SPEC_BY_NAME[declaration]["required_nonclaim_codes"][0]
        changed = _replace_record(
            record,
            nonclaim_codes=tuple(code for code in record.nonclaim_codes if code != required),  # type: ignore[attr-defined]
        )
        return _set_record(world, declaration, changed), False, None
    if category == "OBJECT_CONTENT":
        return _set_record(world, declaration, _corrupt_payload(world[declaration])), False, None
    if category == "HASH":
        return _set_record(world, declaration, _corrupt_hash(world[declaration])), False, None
    if category == "FORBIDDEN_RUNTIME":
        return world, True, None
    if category in {"ADJACENT_PRECEDENCE", "MULTIPLY_INVALID_PRECEDENCE"}:
        return _precedence_world(
            world, declaration, tuple(vector["active_predicates"])
        )
    if category == "SEMANTIC":
        changed, prohibited = _semantic_world(world, declaration, mutation)
        return changed, False, prohibited
    if category == "VALIDATOR_BYPASS":
        return world, False, None
    raise AssertionError(f"unhandled vector category {category}")


class InteractionDeclarationContractTests(unittest.TestCase):
    def test_exact_declaration_shapes_and_signatures(self) -> None:
        self.assertEqual([item.__name__ for item in _D2_TYPES], [row["name"] for row in _D2_ROWS])
        for runtime_type, row in zip(_D2_TYPES, _D2_ROWS, strict=True):
            with self.subTest(declaration=runtime_type.__name__):
                self.assertTrue(is_dataclass(runtime_type))
                self.assertEqual([field.name for field in fields(runtime_type)], row["field_order"])
                parameters = runtime_type.__dataclass_params__
                self.assertTrue(parameters.frozen)
                self.assertTrue(parameters.eq)
                self.assertFalse(parameters.order)
                self.assertFalse(parameters.unsafe_hash)
                self.assertEqual(tuple(runtime_type.__slots__), tuple(row["field_order"]))
                signature = inspect.signature(runtime_type)
                self.assertTrue(
                    all(item.kind is inspect.Parameter.KEYWORD_ONLY for item in signature.parameters.values())
                )
                self.assertTrue(
                    all(item.default is inspect.Parameter.empty for item in signature.parameters.values())
                )
                annotations = get_type_hints(runtime_type)
                for field_row in row["fields"]:
                    field_name, expected_type = field_row[:2]
                    annotation = annotations[field_name]
                    base_expected = expected_type.split("@", 1)[0]
                    with self.subTest(declaration=runtime_type.__name__, field=field_name):
                        if base_expected.startswith("LiteralDomain["):
                            domain = base_expected.removeprefix("LiteralDomain[").removesuffix("]")
                            self.assertIs(get_origin(annotation), Literal)
                            self.assertEqual(get_args(annotation), tuple(_CONTRACT["closed_domains"][domain]))
                        elif base_expected == "CommonObjectEnvelope":
                            self.assertIs(annotation, CommonObjectEnvelope)
                        elif base_expected == "ObjectRef":
                            self.assertIs(annotation, ObjectRef)
                        elif base_expected == "ObjectRef|Applicability":
                            self.assertEqual(set(get_args(annotation)), {ObjectRef, Applicability})
                        elif base_expected == "IntegerV1|Applicability":
                            self.assertEqual(set(get_args(annotation)), {IntegerV1, Applicability})
                        elif base_expected == "Quantity|ResolutionDetail":
                            self.assertEqual(set(get_args(annotation)), {Quantity, ResolutionDetail})
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
                            if "LiteralDomain[INTERACTION_TYPE]" in base_expected:
                                nested = get_args(row_annotation)
                                literal = nested[2] if "ObjectRef,ObjectRef" in base_expected else nested[1]
                                self.assertIs(get_origin(literal), Literal)
                                self.assertEqual(get_args(literal), _INTERACTION_TYPES)
        for validator, row in zip(_D2_VALIDATORS, _D2_VALIDATOR_ROWS, strict=True):
            with self.subTest(validator=validator.__name__):
                self.assertEqual(validator.__name__, row["name"])
                self.assertTrue(
                    all(
                        parameter.kind is inspect.Parameter.POSITIONAL_ONLY
                        for parameter in inspect.signature(validator).parameters.values()
                    )
                )
                actual = str(inspect.signature(validator)).replace("'", "").replace(" | ", "|")
                actual = actual.replace(", ...", ",...")
                self.assertEqual(actual, row["signature"])

    def test_keyword_only_exact_formation_and_ecj1_projection(self) -> None:
        world = _base_world()
        for runtime_type in _D2_TYPES:
            record = world[runtime_type.__name__]
            kwargs = {field.name: getattr(record, field.name) for field in fields(record)}
            with self.subTest(declaration=runtime_type.__name__, boundary="positional"):
                with self.assertRaises(FrameworkError) as raised:
                    runtime_type(*kwargs.values())
                self.assertIs(raised.exception.envelope.failure_code, FailureCode.I3_RECORD_FORMATION_INVALID)
            with self.subTest(declaration=runtime_type.__name__, boundary="unknown"):
                with self.assertRaises(FrameworkError) as raised:
                    runtime_type(**kwargs, unknown_field=True)
                self.assertIs(raised.exception.envelope.failure_code, FailureCode.I3_RECORD_FORMATION_INVALID)
            expected = {
                name: _project(getattr(record, name))
                for name in _SPEC_BY_NAME[runtime_type.__name__]["field_order"]
                if name != "envelope"
            }
            self.assertEqual(record.to_ecj1(), expected)
            self.assertNotIn("envelope", record.to_ecj1())
            self.assertEqual(parse_ecj1(record.envelope.object_content_payload), expected)

    def test_all_frozen_vectors_reach_the_intended_boundary(self) -> None:
        constructor_calls = validator_calls = predicate_calls = 0
        outcomes: Counter[str] = Counter()
        baseline = _base_world()
        for vector in _FIXTURE:
            declaration = vector["declaration"]
            category = vector["category"]
            mutation = vector["mutation"]
            expected_result = vector["expected_result"]
            expected_failure = vector["first_failure"]
            runtime_type = _TYPE_BY_NAME[declaration]
            world = dict(baseline)
            record = world[declaration]
            constructor_calls += vector["constructor_calls"]
            validator_calls += vector["validator_calls"]
            predicate_calls += vector["expected_predicate_calls"]
            outcomes[expected_result] += 1
            with self.subTest(vector=vector["id"], mutation=mutation):
                if category in {"FORMATION_MISSING_FIELD", "FORMATION_WRONG_TYPE"}:
                    kwargs = {field.name: getattr(record, field.name) for field in fields(record)}
                    field_name = mutation.split(":", 1)[1]
                    if category == "FORMATION_MISSING_FIELD":
                        del kwargs[field_name]
                    else:
                        kwargs[field_name] = None
                    with self.assertRaises(FrameworkError) as raised:
                        runtime_type(**kwargs)
                    self.assertEqual(raised.exception.envelope.failure_code.value, expected_failure)
                    continue
                if category == "ENUM_OUT_OF_DOMAIN":
                    kwargs = {field.name: getattr(record, field.name) for field in fields(record)}
                    if mutation.startswith("INVALID_ENUM:"):
                        field_name = mutation.removeprefix("INVALID_ENUM:").split("=", 1)[0]
                        kwargs[field_name] = "OUTSIDE_CLOSED_DOMAIN"
                        with self.assertRaises(FrameworkError) as raised:
                            runtime_type(**kwargs)
                        self.assertEqual(raised.exception.envelope.failure_code.value, expected_failure)
                    else:
                        _, field_name = mutation.split(":", 1)
                        rows = list(kwargs[field_name])
                        row = list(rows[0])
                        row[2 if "pair" in field_name else 1] = "OUTSIDE_CLOSED_DOMAIN"
                        rows[0] = tuple(row)
                        changed = _replace_record(record, **{field_name: tuple(rows)})
                        changed_world = _set_record(world, declaration, changed)
                        with self.assertRaises(FrameworkError) as raised:
                            _call_validator(changed_world, declaration)
                        self.assertEqual(raised.exception.envelope.failure_code.value, expected_failure)
                    continue
                if category == "VALIDATOR_BYPASS":
                    self.assertEqual(expected_result, "NO_ACCEPTED_RESULT")
                    self.assertEqual(expected_failure, "VALIDATOR_BYPASS_FORBIDDEN")
                    self.assertEqual(vector["validator_calls"], 0)
                    continue
                changed_world, attach_runtime, prohibited = _mutated_world(world, vector)
                runtime_member = "execute_generator"
                if attach_runtime:
                    setattr(runtime_type, runtime_member, lambda self: None)
                if prohibited is not None:
                    setattr(runtime_type, "_prohibited_interference_claim", prohibited)
                try:
                    if expected_result == "SUCCESS":
                        _call_validator(changed_world, declaration)
                    else:
                        with self.assertRaises(FrameworkError) as raised:
                            _call_validator(changed_world, declaration)
                        self.assertEqual(raised.exception.envelope.failure_code.value, expected_failure)
                finally:
                    if attach_runtime:
                        delattr(runtime_type, runtime_member)
                    if prohibited is not None:
                        delattr(runtime_type, "_prohibited_interference_claim")
        self.assertEqual(constructor_calls, 1043)
        self.assertEqual(validator_calls, 527)
        self.assertEqual(predicate_calls, 3224)
        self.assertEqual(outcomes, Counter(SUCCESS=167, FAILURE=864, NO_ACCEPTED_RESULT=12))

    def test_fixture_identity_counts_and_combined_projection(self) -> None:
        raw = _FIXTURE_PATH.read_bytes()
        self.assertEqual(len(raw), 662163)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "33f577a28f1964ad79c80a2909512e196825f875f30959c8752d8190fed29399",
        )
        self.assertEqual(_FIXTURE, _VALIDATION["d2_vectors"])
        self.assertEqual(bytes(encode_ecj1(_FIXTURE)) + b"\n", raw)
        self.assertEqual(
            json.dumps(
                _FIXTURE,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n",
            raw,
        )
        self.assertEqual([row["id"] for row in _FIXTURE], _VALIDATION["d2_case_order"])
        identities = [
            json.dumps(
                {
                    key: row[key]
                    for key in ("stage", "declaration", "category", "baseline_profile", "mutation")
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            for row in _FIXTURE
        ]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertEqual(sum(row["constructor_calls"] for row in _FIXTURE), 1043)
        self.assertEqual(sum(row["validator_calls"] for row in _FIXTURE), 527)
        self.assertEqual(sum(row["expected_predicate_calls"] for row in _FIXTURE), 3224)
        self.assertEqual(_VALIDATION["combined_projection"]["vector_count"], 1774)
        self.assertEqual(_VALIDATION["combined_projection"]["success_count"], 275)
        self.assertEqual(_VALIDATION["combined_projection"]["failure_or_no_result_count"], 1499)
        self.assertEqual(_VALIDATION["combined_projection"]["validator_call_count"], 854)
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
        i8_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i8_contract.json"
        )
        assert type(compatibility) is dict
        assert type(i5_contract) is dict
        assert type(post_i5_compatibility) is dict
        current_surface = compatibility["current_surface"]
        post_i5_surface = post_i5_compatibility["current_surface"]
        failures = tuple(code.value for code in FailureCode)
        expected_failures = tuple(
            _CONTRACT["current_surface"]["failure_order"]
            + _CONTRACT["failure_contract"]["d1_append_order"]
            + _CONTRACT["failure_contract"]["d2_append_order"]
        )
        self.assertEqual(failures[:124], expected_failures)
        self.assertEqual(
            failures[124:185],
            tuple(current_surface["failure_slices"][4]["values"]),
        )
        self.assertEqual(
            (failures[:185], failures[185:227], failures[:227]),
            (
                tuple(current_surface["failure_order"]),
                tuple(i5_contract["failure_append_order"]),
                tuple(post_i5_surface["failure_order"]),
            ),
        )
        self.assertEqual((len(failures), len(set(failures))), (294, 294))
        self.assertEqual(
            failures[227:232], tuple(i6_contract["failure_inventory"]["append_order"])
        )
        self.assertEqual(
            failures[232:256], tuple(i7_contract["failure_inventory"]["append_order"])
        )
        self.assertEqual(
            failures[256:280], tuple(i8_contract["failure_inventory"]["future_values"][256:])
        )
        self.assertEqual(failures[280:], tuple(_CLCD["failure_suffix"]))
        failure_prefix_projection = (
            "\n".join(failures[:124]) + "\n"
        ).encode("utf-8")
        failure_projection = ("\n".join(failures) + "\n").encode("utf-8")
        self.assertEqual(
            (
                len(failure_prefix_projection),
                hashlib.sha256(failure_prefix_projection).hexdigest(),
            ),
            (
                3242,
                "115490be2e724f70efe15cec77f9ec2ee5cd5f7c41b7b37a5e5054dc7fea14f0",
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
                7945,
                "bde7371b5d4fd34a537e1d7137ca98c79b5e22d4b1e6678b295da6f321179a2c",
            ),
        )
        exports = tuple(ebu_framework.__all__)
        expected_exports = tuple(
            _CONTRACT["current_surface"]["root_export_order"]
            + _CONTRACT["proposed_surface"]["d1_root_export_suffix"]
            + _CONTRACT["proposed_surface"]["d2_root_export_suffix"]
        )
        self.assertEqual(exports[:261], expected_exports)
        self.assertEqual(
            exports[261:309],
            tuple(current_surface["root_export_slices"][4]["values"]),
        )
        self.assertEqual(
            (exports[:309], exports[309:391], exports[:391]),
            (
                tuple(current_surface["root_export_order"]),
                tuple(i5_contract["root_export_suffix_types"])
                + tuple(i5_contract["root_export_suffix_callables"]),
                tuple(post_i5_surface["root_export_order"]),
            ),
        )
        self.assertEqual((len(exports), len(set(exports))), (471, 471))
        self.assertEqual(
            exports[391:407], tuple(i6_contract["root_exports"]["append_order"])
        )
        self.assertEqual(
            exports[407:419], tuple(i7_contract["root_exports"]["append_order"])
        )
        self.assertEqual(
            exports[419:444], tuple(i8_contract["root_exports"]["append_order"])
        )
        self.assertEqual(exports[444:], tuple(_CLCD["root_export_suffix"]))
        export_prefix_projection = ("\n".join(exports[:261]) + "\n").encode(
            "utf-8"
        )
        export_projection = ("\n".join(exports) + "\n").encode("utf-8")
        self.assertEqual(
            (
                len(export_prefix_projection),
                hashlib.sha256(export_prefix_projection).hexdigest(),
            ),
            (
                5724,
                "1506b3b72fd2be9227aab349f7e84e69e3a77c7233fc8da3d244d7471292f4d9",
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
                10526,
                "804ff437fc0adfdb8980e976c099814c2ece2142d4e40ade3a577b3e14fc1bc9",
            ),
        )
        self.assertEqual(interaction_module.__all__, tuple(_CONTRACT["proposed_surface"]["d2_root_export_suffix"]))

    def test_exact_imports_graphs_and_inertness(self) -> None:
        compatibility = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
        )
        post_i5_compatibility = _load_json(
            _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
        )
        i6_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i6_contract.json"
        )
        i6_paths = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i6_implementation_path_manifest.json"
        )
        i7_paths = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i7_implementation_path_manifest.json"
        )
        i8_paths = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i8_implementation_path_manifest.json"
        )
        i9_contract = _load_json(
            _REPO_ROOT / "post_i9_ci_durability_correction_contract.json"
        )
        stage_c_contract = _load_json(
            _REPO_ROOT / "framework_alpha_packaging_release_candidate_contract.json"
        )
        assert type(compatibility) is dict
        assert type(post_i5_compatibility) is dict
        current_surface = compatibility["current_surface"]
        post_i5_surface = post_i5_compatibility["current_surface"]
        tree = ast.parse(_INTERACTION_PATH.read_text(encoding="utf-8"))
        direct = [
            node.module for node in tree.body if isinstance(node, ast.ImportFrom) and node.level == 1
        ]
        self.assertEqual(direct, ["atomic", "causal", "primitives", "numeric", "identity", "envelopes", "errors"])
        package_dir = _REPO_ROOT / "src/ebu_framework"
        modules = {path.stem for path in package_dir.glob("*.py") if path.name != "__init__.py"}
        graph: dict[str, set[str]] = {name: set() for name in modules}
        for name in modules:
            module_tree = ast.parse((package_dir / f"{name}.py").read_text(encoding="utf-8"))
            for node in ast.walk(module_tree):
                if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module in modules:
                    graph[name].add(node.module)
                elif (
                    isinstance(node, ast.ImportFrom)
                    and node.level == 1
                    and node.module is None
                ):
                    graph[name].update(
                        alias.name for alias in node.names if alias.name in modules
                    )
        expected_graph = {
            name: set(values) for name, values in _CONTRACT["proposed_surface"]["post_d2_direct_imports"].items()
        }
        ordered_graph: dict[str, list[str]] = {}
        for name in current_surface["package_module_order"]:
            module_tree = ast.parse(
                (package_dir / f"{name}.py").read_text(encoding="utf-8")
            )
            ordered_graph[name] = []
            for node in module_tree.body:
                if not isinstance(node, ast.ImportFrom) or node.level != 1:
                    continue
                if node.module in modules:
                    if node.module not in ordered_graph[name]:
                        ordered_graph[name].append(node.module)
                elif node.module is None:
                    for alias in node.names:
                        if (
                            alias.name in modules
                            and alias.name not in ordered_graph[name]
                        ):
                            ordered_graph[name].append(alias.name)
        current_inventory = stage_c_contract["test_inventory_reconciliation"][
            "exact_current_import_inventory"
        ]
        current_module_order = tuple(
            i8_paths["future_import_graph"]["package_module_order"]
        ) + tuple(current_inventory["suffix_module_order"])
        current_ordered_graph: dict[str, list[str]] = {}
        current_module_exports: dict[str, tuple[str, ...]] = {}
        for name in current_module_order:
            module_tree = ast.parse(
                (package_dir / f"{name}.py").read_text(encoding="utf-8")
            )
            current_ordered_graph[name] = []
            for node in module_tree.body:
                if isinstance(node, ast.ImportFrom) and node.level == 1:
                    if node.module in modules:
                        if node.module not in current_ordered_graph[name]:
                            current_ordered_graph[name].append(node.module)
                    elif node.module is None:
                        for alias in node.names:
                            if (
                                alias.name in modules
                                and alias.name not in current_ordered_graph[name]
                            ):
                                current_ordered_graph[name].append(alias.name)
            all_assignment = next(
                node
                for node in module_tree.body
                if isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "__all__"
            )
            module_exports = tuple(ast.literal_eval(all_assignment.value))
            for node in module_tree.body:
                if (
                    isinstance(node, ast.AugAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == "__all__"
                    and isinstance(node.op, ast.Add)
                ):
                    module_exports += tuple(ast.literal_eval(node.value))
            current_module_exports[name] = module_exports
        current_module_order_projection = (
            "\n".join(current_module_order) + "\n"
        ).encode("utf-8")
        current_package_projection = (
            json.dumps(
                [
                    [name, current_ordered_graph[name]]
                    for name in current_module_order
                ],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        current_extension_order = post_i5_surface["extension_module_order"]
        current_extension_projection = (
            json.dumps(
                [
                    [name, current_ordered_graph[name]]
                    for name in current_extension_order
                ],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        current_module_export_projection = (
            json.dumps(
                [
                    [name, list(current_module_exports[name])]
                    for name in current_module_order
                ],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(
            tuple(ordered_graph), tuple(current_surface["package_module_order"])
        )
        self.assertEqual(
            (set(graph), tuple(current_ordered_graph)),
            (set(current_module_order), current_module_order),
        )
        self.assertEqual(len(graph), current_inventory["current_module_count"])
        self.assertEqual(
            {name: graph[name] for name in expected_graph}, expected_graph
        )
        expected_current_graph = {
            name: list(values)
            for name, values in i8_paths["future_import_graph"]["direct_imports"].items()
        }
        expected_current_graph["validation"] = list(
            i9_contract["accepted_i9_frozen_inventory"]["graph"]["validation_direct_imports"]
        )
        expected_current_graph["correction_protocol"] = list(
            current_inventory["suffix_direct_imports"]["correction_protocol"]
        )
        expected_current_graph["correction_diagnostics"] = list(
            current_inventory["suffix_direct_imports"]["correction_diagnostics"]
        )
        self.assertEqual(
            expected_current_graph["validation"],
            current_inventory["suffix_direct_imports"]["validation"],
        )
        self.assertEqual(
            set(expected_current_graph["correction_protocol"]),
            set(_CLCD["import_boundary"]["correction_protocol"]),
        )
        self.assertEqual(
            set(expected_current_graph["correction_diagnostics"]),
            set(_CLCD["import_boundary"]["correction_diagnostics"]),
        )
        expected_current_exports = {
            name: tuple(values) for name, values in i8_paths["module_exports"].items()
        }
        expected_current_exports["validation"] = ()
        expected_current_exports["correction_protocol"] = tuple(_CLCD["root_export_suffix"][:20])
        expected_current_exports["correction_diagnostics"] = tuple(_CLCD["root_export_suffix"][20:])
        self.assertEqual(
            sum(len(values) for values in current_ordered_graph.values()),
            current_inventory["current_direct_edge_count"],
        )
        self.assertEqual(current_ordered_graph, expected_current_graph)
        self.assertEqual(current_module_exports, expected_current_exports)
        self.assertEqual(
            {
                name: len(current_module_exports[name])
                for name in current_inventory["suffix_module_order"]
            },
            current_inventory["suffix_module_export_counts"],
        )
        for projection, identity in (
            (current_module_order_projection, current_inventory["module_order_lf"]),
            (current_package_projection, current_inventory["direct_import_projection"]),
            (
                current_module_export_projection,
                current_inventory["module_export_projection"],
            ),
        ):
            self.assertEqual(
                (len(projection), hashlib.sha256(projection).hexdigest()),
                (identity["byte_count"], identity["sha256"]),
            )
        self.assertEqual(sum(len(values) for values in ordered_graph.values()), 152)
        self.assertEqual(sum(len(values) for values in expected_graph.values()), 124)
        self.assertEqual(
            sum(
                len(ordered_graph[name])
                for name in ("trust", "authorization", "authorization_use", "capabilities")
            ),
            28,
        )
        current_expected_graph = {
            name: set(values)
            for name, values in current_surface["package_direct_imports"].items()
        }
        self.assertEqual(
            ordered_graph, current_surface["package_direct_imports"]
        )
        package_projection = (
            json.dumps(
                [
                    [name, ordered_graph[name]]
                    for name in current_surface["package_module_order"]
                ],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(
            (len(package_projection), hashlib.sha256(package_projection).hexdigest()),
            (
                2119,
                "39067eb9b252c6b47e7dc6e640721b0c3aea6f134ab9c78e5c032874adf8082c",
            ),
        )
        extension_order = current_surface["extension_module_order"]
        extension_projection = (
            json.dumps(
                [[name, ordered_graph[name]] for name in extension_order],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(len(extension_order), 21)
        self.assertEqual(
            sum(len(ordered_graph[name]) for name in extension_order), 131
        )
        self.assertEqual(
            (
                len(extension_projection),
                hashlib.sha256(extension_projection).hexdigest(),
            ),
            (
                1776,
                "5fb42598a0ec166ff9a60ad4033d1f90a53ee176d99bb5bef43b4536f39d32be",
            ),
        )
        i3_plus_extension = {
            "state",
            "conservation",
            "distortion",
            "actions",
            "network",
            "commitments",
            "observation",
            "scheduling",
            "policy",
            "causal",
            "settlement",
            "ledger",
            "faults",
            "experiment",
            "artifacts",
            "atomic",
            "interaction",
        }
        self.assertEqual(len(i3_plus_extension), 17)
        self.assertEqual(
            sum(len(graph[name]) for name in i3_plus_extension),
            103,
        )
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
        self.assertEqual(len(visited), 42)
        forbidden_imports = {
            "asyncio", "importlib", "multiprocessing", "random", "secrets", "socket", "subprocess", "threading", "urllib"
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
            "__import__", "eval", "exec", "open", "optimize", "resolve_ref", "run", "settle", "simulate", "step"
        }
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertFalse(called & prohibited_calls)

    def test_predecessor_signatures_and_d1_bytes_are_preserved(self) -> None:
        compatibility = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
        )
        post_i5_compatibility = _load_json(
            _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
        )
        i5_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i5_contract.json"
        )
        compatibility_manifest = _load_json(
            _REPO_ROOT / "post_i4_legacy_test_compatibility_predecessor_manifest.json"
        )
        i4_contract = _load_json(
            _REPO_ROOT / "unified_python_research_framework_i4_contract.json"
        )
        assert type(compatibility) is dict
        assert type(post_i5_compatibility) is dict
        assert type(i5_contract) is dict
        assert type(compatibility_manifest) is dict
        assert type(i4_contract) is dict
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

        signature_rows = _CONTRACT["current_surface"]["public_function_signatures"]
        self.assertEqual(len(signature_rows), 65)
        signature_projection = (
            "\n".join("\t".join(row) for row in signature_rows) + "\n"
        ).encode("utf-8")
        self.assertEqual(len(signature_projection), 11404)
        self.assertEqual(
            hashlib.sha256(signature_projection).hexdigest(),
            "a61da9d09db7a010d71b1bb57b50abb8232db90367f90869b47c970e69e372a5",
        )
        for module_name, function_name, expected in signature_rows:
            function = getattr(importlib.import_module(f"ebu_framework.{module_name}"), function_name)
            actual = str(inspect.signature(function)).replace("'", "")
            actual = actual.replace(
                "<ExactConversion.NOT_APPLICABLE: NOT_APPLICABLE>",
                "ExactConversion.NOT_APPLICABLE",
            )
            self.assertEqual(actual, expected)
        signature_segments = (
            [
                ["I-3", "PUBLIC_FUNCTION", *row]
                for row in _CONTRACT["current_surface"][
                    "public_function_signatures"
                ]
            ],
            [
                [
                    "D1" if row[0] == "atomic" else "D2",
                    "CALLABLE" if row[1].startswith("validate_") else "TYPE",
                    *row,
                ]
                for row in _CONTRACT["proposed_surface"]["new_signatures"]
            ],
            [
                ["I-4", "TYPE", row["module"], row["name"], row]
                for row in i4_contract["types"]
            ],
            [
                ["I-4", "CALLABLE", row["module"], row["name"], row]
                for row in i4_contract["callables"]
            ],
        )
        combined_signatures = [
            row for segment in signature_segments for row in segment
        ]
        combined_projection = (
            json.dumps(
                combined_signatures,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(tuple(len(segment) for segment in signature_segments), (65, 42, 33, 15))
        self.assertEqual(
            Counter(row[0] for row in signature_segments[1]),
            Counter(D1=18, D2=24),
        )
        self.assertEqual(len(combined_signatures), 155)
        self.assertEqual(
            (len(combined_projection), hashlib.sha256(combined_projection).hexdigest()),
            (
                55808,
                "e5b7a1157aac297d48f2058ca308cfa7c5bc9c3fd1c6040fd68369e27a2ddd2b",
            ),
        )
        signature_contract = post_i5_compatibility["current_surface"][
            "combined_signature_projection"
        ]
        i5_signature_rows = [
            ["I-5", "TYPE", row["module"], row["name"], row]
            for row in i5_contract["types"]
        ] + [
            ["I-5", "CALLABLE", row["module"], row["name"], row]
            for row in i5_contract["callables"]
        ]
        current_signature_rows = combined_signatures + i5_signature_rows
        i5_signature_projection = (
            json.dumps(
                i5_signature_rows,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        current_signature_projection = (
            json.dumps(
                current_signature_rows,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(
            (
                combined_signatures,
                i5_signature_rows,
                current_signature_rows,
                tuple(len(segment) for segment in signature_segments)
                + (len(i5_contract["types"]), len(i5_contract["callables"])),
            ),
            (
                signature_contract["predecessor_rows"],
                signature_contract["i5_rows"],
                signature_contract["current_rows"],
                (65, 42, 33, 15, 50, 32),
            ),
        )
        self.assertEqual(
            (
                len(combined_signatures),
                len(i5_signature_rows),
                len(current_signature_rows),
                (
                    len(i5_signature_projection),
                    hashlib.sha256(i5_signature_projection).hexdigest(),
                ),
                (
                    len(current_signature_projection),
                    hashlib.sha256(current_signature_projection).hexdigest(),
                ),
            ),
            (
                155,
                82,
                237,
                (
                    62204,
                    "24898c5185da5fb0af7b4b19d46569ab38eb0c4c811c81a2f543a7332a3cd8bc",
                ),
                (
                    118010,
                    "083a429b0fd36dda80d62a9113fe81e758c17c210385d10e76dc2c2a80dbdaba",
                ),
            ),
        )
        grouped_signatures = (
            signature_segments[0]
            + [row for row in signature_segments[1] if row[0] == "D1"]
            + [row for row in signature_segments[1] if row[0] == "D2"]
            + signature_segments[2]
            + signature_segments[3]
        )
        grouped_projection = (
            json.dumps(
                grouped_signatures,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(len(grouped_signatures), 155)
        self.assertEqual(
            (len(grouped_projection), hashlib.sha256(grouped_projection).hexdigest()),
            (
                55808,
                "2f5d9bc38522ab03e363adc8bdd4ef001c8083934cdbdf711b13549decdcdfc6",
            ),
        )
        self.assertEqual(
            sorted(
                json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                for row in grouped_signatures
            ),
            sorted(
                json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                for row in combined_signatures
            ),
        )
        self.assertNotEqual(grouped_signatures, combined_signatures)
        self.assertNotEqual(
            hashlib.sha256(grouped_projection).hexdigest(),
            hashlib.sha256(combined_projection).hexdigest(),
        )
        locks = {
            "src/ebu_framework/atomic.py": (70230, "57e4e7b41207c5b7e69c901a0ad5c00bfdfbfac63ee1dc9065d0b6dcc13e88d9"),
            "tests/framework/fixtures/atomic_declaration_v1.json": (469664, "6b4ecac191320e4ee6b02763249fdc9db14b7fb19091814ca10c6703e36acda9"),
            "tests/framework/test_atomic_declarations.py": (73074, "4f448accb50529d9507de996aa13cad741f8287449ceb4bf0dd3a38b58d030b5"),
        }
        for path, (size, digest) in locks.items():
            if path == "tests/framework/test_atomic_declarations.py":
                lock_row = subprocess.run(
                    [
                        "git",
                        "ls-tree",
                        "297535d787355b9911fc01ae5b777a553aa9815b",
                        "--",
                        path,
                    ],
                    cwd=_REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.split()
                self.assertEqual(lock_row[2], "100c73218021f9b4fae64ee20761738c4f28e523")
                payload = subprocess.run(
                    ["git", "cat-file", "blob", lock_row[2]],
                    cwd=_REPO_ROOT,
                    check=True,
                    capture_output=True,
                ).stdout
            else:
                payload = (_REPO_ROOT / path).read_bytes()
            self.assertEqual((len(payload), hashlib.sha256(payload).hexdigest()), (size, digest))
        excluded = {
            "src/ebu_framework/__init__.py",
            "src/ebu_framework/artifacts.py",
            "src/ebu_framework/capabilities.py",
            "src/ebu_framework/commitments.py",
            "src/ebu_framework/errors.py",
            "src/ebu_framework/execution.py",
            "src/ebu_framework/experiment.py",
            "src/ebu_framework/network.py",
            "src/ebu_framework/traces.py",
        }
        stage_c_contract = _load_json(
            _REPO_ROOT / "framework_alpha_packaging_release_candidate_contract.json"
        )
        stage_c_predecessor = _load_json(
            _REPO_ROOT
            / "framework_alpha_packaging_release_candidate_predecessor_manifest.json"
        )
        stage_c_reconciliation = stage_c_contract["test_inventory_reconciliation"][
            "atomic_and_interaction_predecessor_preservation_reconciliation"
        ]
        artifact_reconciliation = stage_c_contract["test_inventory_reconciliation"][
            "artifact_predecessor_preservation_reconciliation"
        ]
        exact_stage_c_paths = (
            ".github/workflows/tests.yml",
            "EBU_FUTURE_BOOKS_STRUCTURE.md",
            "build_backend/ebu_build_backend.py",
            "tests/framework/safety.py",
        )
        stage_c_modified_paths = (
            ".github/workflows/tests.yml",
            "build_backend/ebu_build_backend.py",
        )
        current_byte_preserved_paths = (
            "EBU_FUTURE_BOOKS_STRUCTURE.md",
            "tests/framework/safety.py",
        )
        self.assertEqual(
            (
                tuple(stage_c_reconciliation["exact_reconciled_paths"]),
                tuple(artifact_reconciliation["exact_reconciled_paths"]),
                tuple(artifact_reconciliation["stage_c_modified_paths"]),
                tuple(artifact_reconciliation["current_byte_preserved_paths"]),
                tuple(row["path"] for row in artifact_reconciliation["rows"]),
            ),
            (
                exact_stage_c_paths,
                exact_stage_c_paths,
                stage_c_modified_paths,
                current_byte_preserved_paths,
                exact_stage_c_paths,
            ),
        )
        accepted_stage_c_base_commit = stage_c_contract["predecessor_evidence"][
            "predecessor_test_authority_correction"
        ]["accepted_inventory_scope_integration_commit"]
        self.assertEqual(
            accepted_stage_c_base_commit,
            "c540d032ff22a4cd3be42f31564ac7023706e32d",
        )
        stage_c_reconciliation_rows = {
            row["path"]: row for row in artifact_reconciliation["rows"]
        }
        stage_c_predecessor_rows = {
            row["path"]: row for row in stage_c_predecessor["controlling_paths"]
        }
        for row in _MANIFEST["rows"]:
            if row["path"] in excluded:
                continue
            path = _REPO_ROOT / row["path"]
            with self.subTest(path=row["path"]):
                payload = path.read_bytes()
                if row["path"] in exact_stage_c_paths:
                    frozen = stage_c_reconciliation_rows[row["path"]]
                    historical_payload = subprocess.run(
                        ["git", "cat-file", "blob", row["git_object"]],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    self.assertEqual(
                        (
                            len(historical_payload),
                            hashlib.sha256(historical_payload).hexdigest(),
                        ),
                        (row["byte_count"], row["raw_sha256"]),
                    )
                    i8_payload = subprocess.run(
                        ["git", "cat-file", "blob", frozen["i8_git_object"]],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    self.assertEqual(
                        (len(i8_payload), hashlib.sha256(i8_payload).hexdigest()),
                        (frozen["i8_byte_count"], frozen["i8_raw_sha256"]),
                    )
                    accepted_stage_c_base = (
                        frozen["accepted_stage_c_base_mode"],
                        frozen["accepted_stage_c_base_git_object"],
                        frozen["accepted_stage_c_base_byte_count"],
                        frozen["accepted_stage_c_base_raw_sha256"],
                    )
                    if row["path"] in stage_c_modified_paths:
                        stage_c_row = stage_c_predecessor_rows[row["path"]]
                        self.assertEqual(
                            (
                                stage_c_row["mode"],
                                stage_c_row["git_object"],
                                stage_c_row["byte_count"],
                                stage_c_row["raw_sha256"],
                            ),
                            accepted_stage_c_base,
                        )
                    base_tree_row = subprocess.run(
                        [
                            "git",
                            "ls-tree",
                            accepted_stage_c_base_commit,
                            "--",
                            row["path"],
                        ],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.split()
                    self.assertEqual(
                        (base_tree_row[0], base_tree_row[2]),
                        accepted_stage_c_base[:2],
                    )
                    base_payload = subprocess.run(
                        ["git", "cat-file", "blob", base_tree_row[2]],
                        cwd=_REPO_ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    self.assertEqual(
                        (len(base_payload), hashlib.sha256(base_payload).hexdigest()),
                        accepted_stage_c_base[2:],
                    )
                    mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
                    self.assertEqual(
                        (frozen["i8_mode"], row["mode"], mode),
                        ("100644", "100644", "100644"),
                    )
                    if row["path"] in current_byte_preserved_paths:
                        self.assertEqual(
                            (mode, len(payload), hashlib.sha256(payload).hexdigest()),
                            (
                                frozen["accepted_stage_c_base_mode"],
                                frozen["accepted_stage_c_base_byte_count"],
                                frozen["accepted_stage_c_base_raw_sha256"],
                            ),
                        )
                    else:
                        self.assertIn(row["path"], stage_c_modified_paths)
                    continue
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


if __name__ == "__main__":
    unittest.main()
