"""Inert interaction, topology, allocation, and institutional declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from itertools import combinations
from typing import Literal, NoReturn

from .atomic import (
    BoundaryHistoryEquivalenceWitness,
    StateTransformationGeneratorDeclaration,
)
from .causal import CausalIdentificationStatus
from .primitives import ClaimStatus, Quantity, ResolutionDetail, ResolutionState
from .numeric import (
    Binary64BitsV1,
    CoreNumberV1,
    DecimalV1,
    IntegerV1,
    RationalV1,
)
from .identity import ObjectRef
from .envelopes import CommonObjectEnvelope, validate_object_envelope
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureObjectRef,
    FailureStage,
    FrameworkError,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


_CORE_NUMBER_TYPES = (IntegerV1, RationalV1, DecimalV1, Binary64BitsV1)
_REGULARITY_CODES = (
    "RIGHT_DIFFERENTIABLE",
    "C1",
    "C2",
    "LOCAL_LIPSCHITZ",
    "STRONGLY_CONTINUOUS_LINEAR_SEMIGROUP",
    "BOUNDED_LINEAR_GENERATOR",
    "ORDERED_EVOLUTION_FAMILY",
    "NONSMOOTH",
    "UNRESOLVED",
)
_NONCLAIM_CODES = (
    "NO_EMPIRICAL_VALIDATION",
    "NO_CAUSAL_IDENTIFICATION",
    "NO_INSTITUTIONAL_ENDORSEMENT",
    "NO_SCIENTIFIC_EXECUTION",
    "NO_RUNTIME_BEHAVIOR",
    "NO_SETTLEMENT_ENTITLEMENT",
    "NO_PHYSICAL_PROPAGATION",
    "NO_PHYSICAL_PHASE_INTERFERENCE",
    "NO_WAVE_PROGRAMME",
    "NO_ELECTRICAL_VOLTAGE_PROGRAMME",
    "NO_UNIVERSAL_DIVISIBILITY",
    "NO_MINIMAL_TRANSACTION",
    "NO_UNIVERSAL_SCALAR_OBJECTIVE",
    "NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE",
    "NO_NEIGHBOURHOOD_COMMUTATIVITY_FROM_ONE_STATE",
    "NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED",
    "NO_CAUSAL_MEANING_FOR_INSTITUTIONAL_SHARE",
    "NO_PHYSICAL_CONSERVATION_FROM_MOBIUS_CLOSURE",
    "NO_AUTOMATIC_SETTLEMENT_PRICE",
    "NO_UNIVERSAL_MINIMAL_STATE",
)
_INTERACTION_TYPES = (
    "MOBIUS_FINITE",
    "SAME_BASELINE_NONADDITIVITY",
    "SERIAL_COMPARATOR",
    "MIXED_MARGINAL",
    "COMMUTATOR_ORDER",
    "SHARED_CONSTRAINT",
    "BOUNDARY_PRESERVED",
)
_InteractionType = Literal[
    "MOBIUS_FINITE",
    "SAME_BASELINE_NONADDITIVITY",
    "SERIAL_COMPARATOR",
    "MIXED_MARGINAL",
    "COMMUTATOR_ORDER",
    "SHARED_CONSTRAINT",
    "BOUNDARY_PRESERVED",
]


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.interaction", name, "1.0.0")


def _failure(
    code: FailureCode,
    interface: str,
    *,
    object_ref: FailureObjectRef | None = None,
) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I3,
        interface_ref=_interface(interface),
        object_refs=() if object_ref is None else (object_ref,),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I3_RECORD_FORMATION_INVALID, interface)


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected_fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected_fields:
            _formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _integer_or_applicability(value: object) -> bool:
    return type(value) is IntegerV1 or type(value) is Applicability


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _string_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is str for item in value)


def _ref_quantity_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 2
        and type(row[0]) is ObjectRef
        and type(row[1]) is Quantity
        for row in value
    )


def _subset_quantity_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 2
        and _object_ref_tuple(row[0])
        and type(row[1]) is Quantity
        for row in value
    )


def _pair_edge_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 4
        and type(row[0]) is ObjectRef
        and type(row[1]) is ObjectRef
        and type(row[2]) is str
        and type(row[3]) is ObjectRef
        for row in value
    )


def _hyperedge_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 3
        and _object_ref_tuple(row[0])
        and type(row[1]) is str
        and type(row[2]) is ObjectRef
        for row in value
    )


def _ref_pair_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 2
        and all(type(item) is ObjectRef for item in row)
        for row in value
    )


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


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class JointObjectiveDeclaration:
    envelope: CommonObjectEnvelope
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    feasibility_constraint_refs: tuple[ObjectRef, ...]
    objective_kind: Literal[
        "SCALAR", "VECTOR_PARETO", "VECTOR_LEXICOGRAPHIC", "VECTOR_EPSILON_CONSTRAINT"
    ]
    scalar_objective_ref: ObjectRef | Applicability
    vector_component_refs: tuple[ObjectRef, ...]
    component_unit_refs: tuple[ObjectRef, ...]
    selection_rule_ref: ObjectRef
    epsilon_constraint_refs: tuple[ObjectRef, ...]
    optimization_direction: Literal["MINIMIZE", "MAXIMIZE"]
    uncertainty_refs: tuple[ObjectRef, ...]
    existence_assumption_refs: tuple[ObjectRef, ...]
    regularity_assumption_refs: tuple[ObjectRef, ...]
    deterministic_tie_rule_ref: ObjectRef
    feasibility_first: bool
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.boundary_ref,
            self.horizon_ref,
            self.selection_rule_ref,
            self.deterministic_tie_rule_ref,
        )
        collections = (
            self.action_refs,
            self.feasibility_constraint_refs,
            self.vector_component_refs,
            self.component_unit_refs,
            self.epsilon_constraint_refs,
            self.uncertainty_refs,
            self.existence_assumption_refs,
            self.regularity_assumption_refs,
            self.provenance_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and all(_object_ref_tuple(value) for value in collections)
            and type(self.objective_kind) is str
            and self.objective_kind
            in {"SCALAR", "VECTOR_PARETO", "VECTOR_LEXICOGRAPHIC", "VECTOR_EPSILON_CONSTRAINT"}
            and _object_or_applicability(self.scalar_objective_ref)
            and type(self.optimization_direction) is str
            and self.optimization_direction in {"MINIMIZE", "MAXIMIZE"}
            and type(self.feasibility_first) is bool
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
        ):
            _formation_failure("JointObjectiveDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class FiniteSetInteractionWitness:
    envelope: CommonObjectEnvelope
    subset_protocol_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    initial_augmented_state_ref: ObjectRef
    boundary_ref: ObjectRef
    state_schema_ref: ObjectRef
    burden_definition_ref: ObjectRef
    value_unit_ref: ObjectRef
    value_dimension_ref: ObjectRef
    horizon_ref: ObjectRef
    exogenous_history_ref: ObjectRef
    action_removal_semantics: Literal["QUANTITY_FIXED", "RULE_REPLAYED"]
    constraint_refs: tuple[ObjectRef, ...]
    shared_constraint_resolver_ref: ObjectRef
    active_mode_refs: tuple[ObjectRef, ...]
    loss_account_refs: tuple[ObjectRef, ...]
    commitment_account_refs: tuple[ObjectRef, ...]
    process_account_refs: tuple[ObjectRef, ...]
    subset_values: tuple[tuple[tuple[ObjectRef, ...], Quantity], ...]
    empty_baseline: Quantity
    mobius_coefficients: tuple[tuple[tuple[ObjectRef, ...], Quantity], ...]
    normalization: Literal["RAW_WITH_EXPLICIT_EMPTY", "NORMALIZED_BY_EMPTY"]
    truncation_order: IntegerV1 | Applicability
    truncation_residuals: tuple[tuple[tuple[ObjectRef, ...], Quantity], ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.subset_protocol_ref,
            self.initial_augmented_state_ref,
            self.boundary_ref,
            self.state_schema_ref,
            self.burden_definition_ref,
            self.value_unit_ref,
            self.value_dimension_ref,
            self.horizon_ref,
            self.exogenous_history_ref,
            self.shared_constraint_resolver_ref,
        )
        collections = (
            self.action_refs,
            self.constraint_refs,
            self.active_mode_refs,
            self.loss_account_refs,
            self.commitment_account_refs,
            self.process_account_refs,
            self.provenance_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and all(_object_ref_tuple(value) for value in collections)
            and type(self.action_removal_semantics) is str
            and self.action_removal_semantics in {"QUANTITY_FIXED", "RULE_REPLAYED"}
            and _subset_quantity_rows(self.subset_values)
            and type(self.empty_baseline) is Quantity
            and _subset_quantity_rows(self.mobius_coefficients)
            and type(self.normalization) is str
            and self.normalization in {"RAW_WITH_EXPLICIT_EMPTY", "NORMALIZED_BY_EMPTY"}
            and _integer_or_applicability(self.truncation_order)
            and _subset_quantity_rows(self.truncation_residuals)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
        ):
            _formation_failure("FiniteSetInteractionWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SameBaselineNonadditivityWitness:
    envelope: CommonObjectEnvelope
    subset_protocol_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef
    empty_baseline: Quantity
    joint_value: Quantity
    singleton_values: tuple[tuple[ObjectRef, Quantity], ...]
    nonadditivity_value: Quantity
    value_unit_ref: ObjectRef
    value_dimension_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.subset_protocol_ref,
                    self.boundary_ref,
                    self.horizon_ref,
                    self.value_unit_ref,
                    self.value_dimension_ref,
                )
            )
            and _object_ref_tuple(self.action_refs)
            and all(
                type(value) is Quantity
                for value in (self.empty_baseline, self.joint_value, self.nonadditivity_value)
            )
            and _ref_quantity_rows(self.singleton_values)
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("SameBaselineNonadditivityWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SerialComparatorInteractionWitness:
    envelope: CommonObjectEnvelope
    comparison_protocol_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    parallel_schedule_ref: ObjectRef
    serial_comparator_ref: ObjectRef
    serial_order_refs: tuple[ObjectRef, ...]
    initial_augmented_state_ref: ObjectRef
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef
    exogenous_history_ref: ObjectRef
    parallel_value: Quantity
    serial_value: Quantity
    interaction_value: Quantity
    value_unit_ref: ObjectRef
    value_dimension_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.comparison_protocol_ref,
            self.parallel_schedule_ref,
            self.serial_comparator_ref,
            self.initial_augmented_state_ref,
            self.boundary_ref,
            self.horizon_ref,
            self.exogenous_history_ref,
            self.value_unit_ref,
            self.value_dimension_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and all(
                _object_ref_tuple(value)
                for value in (
                    self.action_refs,
                    self.serial_order_refs,
                    self.process_account_refs,
                    self.provenance_refs,
                )
            )
            and all(
                type(value) is Quantity
                for value in (self.parallel_value, self.serial_value, self.interaction_value)
            )
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
        ):
            _formation_failure("SerialComparatorInteractionWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class MixedMarginalWitness:
    envelope: CommonObjectEnvelope
    action_i_ref: ObjectRef
    action_j_ref: ObjectRef
    quantity_coordinate_i_ref: ObjectRef
    quantity_coordinate_j_ref: ObjectRef
    base_quantity_i: Quantity
    base_quantity_j: Quantity
    delta_i: Quantity
    delta_j: Quantity
    rectangle_value_00: Quantity
    rectangle_value_10: Quantity
    rectangle_value_01: Quantity
    rectangle_value_11: Quantity
    mixed_difference: Quantity
    normalized_mixed_marginal: Quantity | ResolutionDetail
    regularity_status: Literal[
        "C2_ON_COMPLETE_RECTANGLE",
        "NONSMOOTH_FINITE_DIFFERENCE_ONLY",
        "GENERALIZED_DERIVATIVE_SEPARATELY_AUTHORIZED",
        "UNRESOLVED",
    ]
    rectangle_domain_ref: ObjectRef
    active_mode_refs: tuple[ObjectRef, ...]
    topology_snapshot_ref: ObjectRef
    tolerance_ref: ObjectRef
    sign_convention_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.action_i_ref,
            self.action_j_ref,
            self.quantity_coordinate_i_ref,
            self.quantity_coordinate_j_ref,
            self.rectangle_domain_ref,
            self.topology_snapshot_ref,
            self.tolerance_ref,
            self.sign_convention_ref,
        )
        quantities = (
            self.base_quantity_i,
            self.base_quantity_j,
            self.delta_i,
            self.delta_j,
            self.rectangle_value_00,
            self.rectangle_value_10,
            self.rectangle_value_01,
            self.rectangle_value_11,
            self.mixed_difference,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and all(type(value) is Quantity for value in quantities)
            and type(self.normalized_mixed_marginal) in {Quantity, ResolutionDetail}
            and type(self.regularity_status) is str
            and self.regularity_status
            in {
                "C2_ON_COMPLETE_RECTANGLE",
                "NONSMOOTH_FINITE_DIFFERENCE_ONLY",
                "GENERALIZED_DERIVATIVE_SEPARATELY_AUTHORIZED",
                "UNRESOLVED",
            }
            and _object_ref_tuple(self.active_mode_refs)
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("MixedMarginalWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CommutatorWitness:
    envelope: CommonObjectEnvelope
    left_generator_ref: ObjectRef
    right_generator_ref: ObjectRef
    base_state_ref: ObjectRef
    boundary_ref: ObjectRef
    domain_ref: ObjectRef
    topology_ref: ObjectRef
    active_mode_refs: tuple[ObjectRef, ...]
    step_extent: Quantity
    composition_orientation: Literal["LEFT_AFTER_RIGHT_MINUS_RIGHT_AFTER_LEFT"]
    bracket_components: tuple[tuple[ObjectRef, Quantity], ...]
    order_difference_components: tuple[tuple[ObjectRef, Quantity], ...]
    remainder_components: tuple[tuple[ObjectRef, Quantity], ...]
    regularity_codes: tuple[str, ...]
    commutativity_scope: Literal["ONE_STATE", "DECLARED_NEIGHBOURHOOD"]
    commutativity_status: Literal[
        "COMMUTING_ON_DECLARED_NEIGHBOURHOOD",
        "NONCOMMUTING",
        "ZERO_AT_ONE_STATE_ONLY",
        "UNRESOLVED",
    ]
    remainder_meaning_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.left_generator_ref,
            self.right_generator_ref,
            self.base_state_ref,
            self.boundary_ref,
            self.domain_ref,
            self.topology_ref,
            self.remainder_meaning_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.active_mode_refs)
            and type(self.step_extent) is Quantity
            and type(self.composition_orientation) is str
            and self.composition_orientation == "LEFT_AFTER_RIGHT_MINUS_RIGHT_AFTER_LEFT"
            and _ref_quantity_rows(self.bracket_components)
            and _ref_quantity_rows(self.order_difference_components)
            and _ref_quantity_rows(self.remainder_components)
            and _string_tuple(self.regularity_codes)
            and type(self.commutativity_scope) is str
            and self.commutativity_scope in {"ONE_STATE", "DECLARED_NEIGHBOURHOOD"}
            and type(self.commutativity_status) is str
            and self.commutativity_status
            in {
                "COMMUTING_ON_DECLARED_NEIGHBOURHOOD",
                "NONCOMMUTING",
                "ZERO_AT_ONE_STATE_ONLY",
                "UNRESOLVED",
            }
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("CommutatorWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SharedConstraintFactor:
    envelope: CommonObjectEnvelope
    factor_kind: Literal["CAPACITY", "COMMITMENT", "AUTHORITY", "SAFETY", "VIABILITY", "OTHER_DECLARED"]
    action_refs: tuple[ObjectRef, ...]
    constraint_ref: ObjectRef
    constraint_unit_ref: ObjectRef | Applicability
    timing_contract_ref: ObjectRef
    hierarchy_kind: Literal["TREE", "DAG", "FEDERATION", "OVERLAPPING_AUTHORITY"]
    ownership_kind: Literal[
        "LOWEST_COMPLETE_COMMON_BOUNDARY", "DECLARED_FACTOR_BOUNDARY", "DISTRIBUTED_PROTOCOL"
    ]
    owner_boundary_ref: ObjectRef
    lowest_common_boundary_ref: ObjectRef | Applicability
    distributed_protocol_ref: ObjectRef | Applicability
    authority_ref: ObjectRef
    demand_visibility_refs: tuple[ObjectRef, ...]
    hidden_state_resolution: ResolutionDetail
    binding_resolution: ResolutionDetail
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.constraint_ref,
            self.timing_contract_ref,
            self.owner_boundary_ref,
            self.authority_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.factor_kind) is str
            and self.factor_kind
            in {"CAPACITY", "COMMITMENT", "AUTHORITY", "SAFETY", "VIABILITY", "OTHER_DECLARED"}
            and _object_ref_tuple(self.action_refs)
            and all(type(value) is ObjectRef for value in refs)
            and _object_or_applicability(self.constraint_unit_ref)
            and type(self.hierarchy_kind) is str
            and self.hierarchy_kind in {"TREE", "DAG", "FEDERATION", "OVERLAPPING_AUTHORITY"}
            and type(self.ownership_kind) is str
            and self.ownership_kind
            in {"LOWEST_COMPLETE_COMMON_BOUNDARY", "DECLARED_FACTOR_BOUNDARY", "DISTRIBUTED_PROTOCOL"}
            and _object_or_applicability(self.lowest_common_boundary_ref)
            and _object_or_applicability(self.distributed_protocol_ref)
            and _object_ref_tuple(self.demand_visibility_refs)
            and type(self.hidden_state_resolution) is ResolutionDetail
            and type(self.binding_resolution) is ResolutionDetail
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("SharedConstraintFactor")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InteractionTopologySnapshot:
    envelope: CommonObjectEnvelope
    boundary_ref: ObjectRef
    state_ref: ObjectRef
    horizon_ref: ObjectRef
    subset_protocol_ref: ObjectRef
    vertex_action_refs: tuple[ObjectRef, ...]
    structural_pair_edges: tuple[tuple[ObjectRef, ObjectRef, _InteractionType, ObjectRef], ...]
    structural_hyperedges: tuple[tuple[tuple[ObjectRef, ...], _InteractionType, ObjectRef], ...]
    active_pair_edges: tuple[tuple[ObjectRef, ObjectRef, _InteractionType, ObjectRef], ...]
    active_hyperedges: tuple[tuple[tuple[ObjectRef, ...], _InteractionType, ObjectRef], ...]
    factor_refs: tuple[ObjectRef, ...]
    factor_incidence: tuple[tuple[ObjectRef, ObjectRef], ...]
    boundary_node_refs: tuple[ObjectRef, ...]
    physical_transport_topology_ref: ObjectRef | Applicability
    institutional_constraint_topology_ref: ObjectRef | Applicability
    hidden_state_resolution: ResolutionDetail
    boundary_equivalence_ref: ObjectRef | Applicability
    exposed_interaction_pairs: tuple[tuple[ObjectRef, ObjectRef], ...]
    boundary_preservation_status: Literal[
        "NOT_ASSESSED", "PRESERVED_ALL_EXPOSED_SUBSETS", "NOT_PRESERVED"
    ]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (self.boundary_ref, self.state_ref, self.horizon_ref, self.subset_protocol_ref)
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.vertex_action_refs)
            and _pair_edge_rows(self.structural_pair_edges)
            and _hyperedge_rows(self.structural_hyperedges)
            and _pair_edge_rows(self.active_pair_edges)
            and _hyperedge_rows(self.active_hyperedges)
            and _object_ref_tuple(self.factor_refs)
            and _ref_pair_rows(self.factor_incidence)
            and _object_ref_tuple(self.boundary_node_refs)
            and _object_or_applicability(self.physical_transport_topology_ref)
            and _object_or_applicability(self.institutional_constraint_topology_ref)
            and type(self.hidden_state_resolution) is ResolutionDetail
            and _object_or_applicability(self.boundary_equivalence_ref)
            and _ref_pair_rows(self.exposed_interaction_pairs)
            and type(self.boundary_preservation_status) is str
            and self.boundary_preservation_status
            in {"NOT_ASSESSED", "PRESERVED_ALL_EXPOSED_SUBSETS", "NOT_PRESERVED"}
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("InteractionTopologySnapshot")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AllocationOptimalityWitness:
    envelope: CommonObjectEnvelope
    objective_ref: ObjectRef
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef
    selected_action_refs: tuple[ObjectRef, ...]
    selected_quantities: tuple[tuple[ObjectRef, Quantity], ...]
    selected_mode_refs: tuple[ObjectRef, ...]
    feasibility_certificate_ref: ObjectRef
    certificate_kind: Literal[
        "GLOBAL_DIRECT",
        "KKT_LOCAL",
        "KKT_GLOBAL_CONVEX",
        "COMBINATORIAL",
        "MIXED_INTEGER",
        "PARETO",
        "LEXICOGRAPHIC",
        "EPSILON_CONSTRAINT",
    ]
    constraint_qualification_refs: tuple[ObjectRef, ...]
    convexity_or_globality_refs: tuple[ObjectRef, ...]
    active_constraint_refs: tuple[ObjectRef, ...]
    marginal_values: tuple[tuple[ObjectRef, Quantity], ...]
    deterministic_tie_rule_ref: ObjectRef
    kkt_applicability: Literal[
        "APPLICABLE_LOCAL_ONLY",
        "APPLICABLE_GLOBAL_WITH_CONVEXITY",
        "INAPPLICABLE_DISCRETE_OR_NONSMOOTH",
        "NOT_USED",
    ]
    result_resolution: ResolutionDetail
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.objective_ref,
            self.boundary_ref,
            self.horizon_ref,
            self.feasibility_certificate_ref,
            self.deterministic_tie_rule_ref,
        )
        collections = (
            self.selected_action_refs,
            self.selected_mode_refs,
            self.constraint_qualification_refs,
            self.convexity_or_globality_refs,
            self.active_constraint_refs,
            self.provenance_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and all(_object_ref_tuple(value) for value in collections)
            and _ref_quantity_rows(self.selected_quantities)
            and type(self.certificate_kind) is str
            and self.certificate_kind
            in {
                "GLOBAL_DIRECT",
                "KKT_LOCAL",
                "KKT_GLOBAL_CONVEX",
                "COMBINATORIAL",
                "MIXED_INTEGER",
                "PARETO",
                "LEXICOGRAPHIC",
                "EPSILON_CONSTRAINT",
            }
            and _ref_quantity_rows(self.marginal_values)
            and type(self.kkt_applicability) is str
            and self.kkt_applicability
            in {
                "APPLICABLE_LOCAL_ONLY",
                "APPLICABLE_GLOBAL_WITH_CONVEXITY",
                "INAPPLICABLE_DISCRETE_OR_NONSMOOTH",
                "NOT_USED",
            }
            and type(self.result_resolution) is ResolutionDetail
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
        ):
            _formation_failure("AllocationOptimalityWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ScalarDecompositionWitness:
    envelope: CommonObjectEnvelope
    objective_ref: ObjectRef
    allocation_ref: ObjectRef
    decomposition_kind: Literal["AUMANN_SHAPLEY_RADIAL", "OTHER_DECLARED_PATH"]
    path_ref: ObjectRef
    baseline_value: Quantity
    selected_total: Quantity
    shares: tuple[tuple[ObjectRef, Quantity], ...]
    residual: Quantity
    closure_rule: Literal["SELECTED_TOTAL_EQUALS_BASELINE_PLUS_SHARES_PLUS_RESIDUAL"]
    differentiability_witness_ref: ObjectRef | Applicability
    path_provenance_refs: tuple[ObjectRef, ...]
    closure_resolution: ResolutionDetail
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in (self.objective_ref, self.allocation_ref, self.path_ref))
            and all(type(value) is Quantity for value in (self.baseline_value, self.selected_total, self.residual))
            and type(self.decomposition_kind) is str
            and self.decomposition_kind in {"AUMANN_SHAPLEY_RADIAL", "OTHER_DECLARED_PATH"}
            and _ref_quantity_rows(self.shares)
            and type(self.closure_rule) is str
            and self.closure_rule == "SELECTED_TOTAL_EQUALS_BASELINE_PLUS_SHARES_PLUS_RESIDUAL"
            and _object_or_applicability(self.differentiability_witness_ref)
            and _object_ref_tuple(self.path_provenance_refs)
            and type(self.closure_resolution) is ResolutionDetail
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("ScalarDecompositionWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InstitutionalAcceptanceRule:
    envelope: CommonObjectEnvelope
    jurisdiction_ref: ObjectRef
    boundary_ref: ObjectRef
    issuing_authority_ref: ObjectRef
    eligible_actor_refs: tuple[ObjectRef, ...]
    eligible_action_refs: tuple[ObjectRef, ...]
    decision_domain_ref: ObjectRef
    rule_expression_ref: ObjectRef
    priority_rule_ref: ObjectRef
    deterministic_tie_rule_ref: ObjectRef
    effective_horizon_ref: ObjectRef
    appeal_rule_ref: ObjectRef
    expiry_rule_ref: ObjectRef
    cancellation_rule_ref: ObjectRef
    provenance_authority_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.jurisdiction_ref,
            self.boundary_ref,
            self.issuing_authority_ref,
            self.decision_domain_ref,
            self.rule_expression_ref,
            self.priority_rule_ref,
            self.deterministic_tie_rule_ref,
            self.effective_horizon_ref,
            self.appeal_rule_ref,
            self.expiry_rule_ref,
            self.cancellation_rule_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.eligible_actor_refs)
            and _object_ref_tuple(self.eligible_action_refs)
            and _object_ref_tuple(self.provenance_authority_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("InstitutionalAcceptanceRule")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InstitutionalSettlementRule:
    envelope: CommonObjectEnvelope
    acceptance_rule_ref: ObjectRef
    jurisdiction_ref: ObjectRef
    boundary_ref: ObjectRef
    issuing_authority_ref: ObjectRef
    settlement_basis: Literal["INDEPENDENT_INSTITUTIONAL_RULE", "IDENTIFIED_CAUSAL_RULE"]
    causal_identification_requirement: Literal[
        "NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT", "IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM"
    ]
    causal_claim_status: Literal["NOT_MADE", "IDENTIFIED"]
    share_rule_ref: ObjectRef
    beneficiary_eligibility_ref: ObjectRef
    settlement_unit_ref: ObjectRef
    settlement_dimension_ref: ObjectRef
    physical_measurement_ref: ObjectRef
    explicit_residual_required: bool
    closure_rule: Literal["MEASURED_TOTAL_EQUALS_SHARE_TOTAL_PLUS_EXPLICIT_RESIDUAL"]
    residual_ownership_rule_ref: ObjectRef
    dispute_resolution_rule_ref: ObjectRef
    effective_horizon_ref: ObjectRef
    provenance_authority_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.acceptance_rule_ref,
            self.jurisdiction_ref,
            self.boundary_ref,
            self.issuing_authority_ref,
            self.share_rule_ref,
            self.beneficiary_eligibility_ref,
            self.settlement_unit_ref,
            self.settlement_dimension_ref,
            self.physical_measurement_ref,
            self.residual_ownership_rule_ref,
            self.dispute_resolution_rule_ref,
            self.effective_horizon_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.settlement_basis) is str
            and self.settlement_basis in {"INDEPENDENT_INSTITUTIONAL_RULE", "IDENTIFIED_CAUSAL_RULE"}
            and type(self.causal_identification_requirement) is str
            and self.causal_identification_requirement
            in {"NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT", "IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM"}
            and type(self.causal_claim_status) is str
            and self.causal_claim_status in {"NOT_MADE", "IDENTIFIED"}
            and type(self.explicit_residual_required) is bool
            and type(self.closure_rule) is str
            and self.closure_rule == "MEASURED_TOTAL_EQUALS_SHARE_TOTAL_PLUS_EXPLICIT_RESIDUAL"
            and _object_ref_tuple(self.provenance_authority_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("InstitutionalSettlementRule")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


_OBJECT_SURFACE = {
    JointObjectiveDeclaration: (
        "ebu:object-kind:atomic-interaction:joint-objective-declaration",
        "ebu:schema:atomic-interaction:joint-objective-declaration-v1",
    ),
    FiniteSetInteractionWitness: (
        "ebu:object-kind:atomic-interaction:finite-set-interaction-witness",
        "ebu:schema:atomic-interaction:finite-set-interaction-witness-v1",
    ),
    SameBaselineNonadditivityWitness: (
        "ebu:object-kind:atomic-interaction:same-baseline-nonadditivity-witness",
        "ebu:schema:atomic-interaction:same-baseline-nonadditivity-witness-v1",
    ),
    SerialComparatorInteractionWitness: (
        "ebu:object-kind:atomic-interaction:serial-comparator-interaction-witness",
        "ebu:schema:atomic-interaction:serial-comparator-interaction-witness-v1",
    ),
    MixedMarginalWitness: (
        "ebu:object-kind:atomic-interaction:mixed-marginal-witness",
        "ebu:schema:atomic-interaction:mixed-marginal-witness-v1",
    ),
    CommutatorWitness: (
        "ebu:object-kind:atomic-interaction:commutator-witness",
        "ebu:schema:atomic-interaction:commutator-witness-v1",
    ),
    SharedConstraintFactor: (
        "ebu:object-kind:atomic-interaction:shared-constraint-factor",
        "ebu:schema:atomic-interaction:shared-constraint-factor-v1",
    ),
    InteractionTopologySnapshot: (
        "ebu:object-kind:atomic-interaction:interaction-topology-snapshot",
        "ebu:schema:atomic-interaction:interaction-topology-snapshot-v1",
    ),
    AllocationOptimalityWitness: (
        "ebu:object-kind:atomic-interaction:allocation-optimality-witness",
        "ebu:schema:atomic-interaction:allocation-optimality-witness-v1",
    ),
    ScalarDecompositionWitness: (
        "ebu:object-kind:atomic-interaction:scalar-decomposition-witness",
        "ebu:schema:atomic-interaction:scalar-decomposition-witness-v1",
    ),
    InstitutionalAcceptanceRule: (
        "ebu:object-kind:atomic-interaction:institutional-acceptance-rule",
        "ebu:schema:atomic-interaction:institutional-acceptance-rule-v1",
    ),
    InstitutionalSettlementRule: (
        "ebu:object-kind:atomic-interaction:institutional-settlement-rule",
        "ebu:schema:atomic-interaction:institutional-settlement-rule-v1",
    ),
}


def _failure_object(record: object) -> FailureObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _record_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _object_content_mismatch(record: object) -> bool:
    stored = record.envelope.to_ecj1()["object_content_payload"]  # type: ignore[attr-defined]
    return stored != record.to_ecj1()  # type: ignore[attr-defined]


def _object_hash_matches(record: object) -> bool:
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def _surface_invalid(record: object) -> bool:
    expected_kind, expected_schema = _OBJECT_SURFACE[type(record)]
    envelope = record.envelope  # type: ignore[attr-defined]
    return (
        str(envelope.object_kind_id) != expected_kind
        or str(envelope.schema_id) != expected_schema
        or str(envelope.schema_version) != "1.0.0"
    )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _resolution_specs(resolution: ResolutionDetail) -> tuple[tuple[tuple[object, ...], str], ...]:
    return (
        (resolution.completed_part_refs, "ref"),
        (resolution.missing_part_refs, "ref"),
    )


def _collection_specs(record: object) -> tuple[tuple[tuple[object, ...], str], ...]:
    common = (
        (record.nonclaim_codes, "nonclaim"),  # type: ignore[attr-defined]
        (record.provenance_refs, "ref"),  # type: ignore[attr-defined]
    )
    if type(record) is JointObjectiveDeclaration:
        return (
            (record.action_refs, "ref"),
            (record.feasibility_constraint_refs, "ref"),
            (record.vector_component_refs, "ref"),
            (record.component_unit_refs, "semantic_ref"),
            (record.epsilon_constraint_refs, "ref"),
            (record.uncertainty_refs, "ref"),
            (record.existence_assumption_refs, "ref"),
            (record.regularity_assumption_refs, "ref"),
        ) + common
    if type(record) is FiniteSetInteractionWitness:
        return (
            (record.action_refs, "ref"),
            (record.constraint_refs, "ref"),
            (record.active_mode_refs, "ref"),
            (record.loss_account_refs, "ref"),
            (record.commitment_account_refs, "ref"),
            (record.process_account_refs, "ref"),
            (record.subset_values, "subset"),
            (record.mobius_coefficients, "subset"),
            (record.truncation_residuals, "subset"),
        ) + common
    if type(record) is SameBaselineNonadditivityWitness:
        return (
            (record.action_refs, "ref"),
            (record.singleton_values, "ref_row"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is SerialComparatorInteractionWitness:
        return (
            (record.action_refs, "ref"),
            (record.serial_order_refs, "semantic_ref"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is MixedMarginalWitness:
        specs = (
            (record.active_mode_refs, "ref"),
            (record.process_account_refs, "ref"),
        ) + common
        if type(record.normalized_mixed_marginal) is ResolutionDetail:
            specs += _resolution_specs(record.normalized_mixed_marginal)
        return specs
    if type(record) is CommutatorWitness:
        return (
            (record.active_mode_refs, "ref"),
            (record.bracket_components, "ref_row"),
            (record.order_difference_components, "ref_row"),
            (record.remainder_components, "ref_row"),
            (record.regularity_codes, "regularity"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is SharedConstraintFactor:
        return (
            (record.action_refs, "ref"),
            (record.demand_visibility_refs, "ref"),
        ) + _resolution_specs(record.hidden_state_resolution) + _resolution_specs(record.binding_resolution) + common
    if type(record) is InteractionTopologySnapshot:
        return (
            (record.vertex_action_refs, "ref"),
            (record.structural_pair_edges, "edge"),
            (record.structural_hyperedges, "hyperedge"),
            (record.active_pair_edges, "edge"),
            (record.active_hyperedges, "hyperedge"),
            (record.factor_refs, "ref"),
            (record.factor_incidence, "pair"),
            (record.boundary_node_refs, "ref"),
            (record.exposed_interaction_pairs, "pair"),
        ) + _resolution_specs(record.hidden_state_resolution) + common
    if type(record) is AllocationOptimalityWitness:
        return (
            (record.selected_action_refs, "ref"),
            (record.selected_quantities, "ref_row"),
            (record.selected_mode_refs, "ref"),
            (record.constraint_qualification_refs, "ref"),
            (record.convexity_or_globality_refs, "ref"),
            (record.active_constraint_refs, "ref"),
            (record.marginal_values, "ref_row"),
        ) + _resolution_specs(record.result_resolution) + common
    if type(record) is ScalarDecompositionWitness:
        return (
            (record.shares, "ref_row"),
            (record.path_provenance_refs, "ref"),
        ) + _resolution_specs(record.closure_resolution) + common
    if type(record) is InstitutionalAcceptanceRule:
        return (
            (record.eligible_actor_refs, "ref"),
            (record.eligible_action_refs, "ref"),
            (record.provenance_authority_refs, "ref"),
        ) + common
    if type(record) is InstitutionalSettlementRule:
        return ((record.provenance_authority_refs, "ref"),) + common
    if type(record) is StateTransformationGeneratorDeclaration:
        return (
            (record.state_coordinate_refs, "ref"),
            (record.derivative_component_units, "ref_row"),
            (record.regularity_codes, "regularity") if hasattr(record, "regularity_codes") else ((), "ref"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is BoundaryHistoryEquivalenceWitness:
        return (
            (record.process_account_preservation_refs, "ref"),
            (record.internal_topology_export_refs, "ref"),
        ) + _resolution_specs(record.resolution) + common
    return ()


def _collection_key(value: object, kind: str) -> object:
    if kind in {"ref", "semantic_ref"}:
        return _ref_key(value)  # type: ignore[arg-type]
    if kind == "ref_row":
        return _ref_key(value[0])  # type: ignore[index]
    if kind == "subset":
        subset = value[0]  # type: ignore[index]
        return (len(subset), tuple(_ref_key(item) for item in subset))
    if kind == "pair":
        return tuple(_ref_key(item) for item in value)  # type: ignore[arg-type]
    if kind == "edge":
        interaction = (
            (0, _INTERACTION_TYPES.index(value[2]))  # type: ignore[index]
            if value[2] in _INTERACTION_TYPES  # type: ignore[operator,index]
            else (1, value[2])  # type: ignore[index]
        )
        return (
            _ref_key(value[0]),  # type: ignore[index]
            _ref_key(value[1]),  # type: ignore[index]
            interaction,
            _ref_key(value[3]),  # type: ignore[index]
        )
    if kind == "hyperedge":
        interaction = (
            (0, _INTERACTION_TYPES.index(value[1]))  # type: ignore[index]
            if value[1] in _INTERACTION_TYPES  # type: ignore[operator,index]
            else (1, value[1])  # type: ignore[index]
        )
        return (
            len(value[0]),  # type: ignore[index]
            tuple(_ref_key(item) for item in value[0]),  # type: ignore[index]
            interaction,
            _ref_key(value[2]),  # type: ignore[index]
        )
    domain = _NONCLAIM_CODES if kind == "nonclaim" else _REGULARITY_CODES
    try:
        return (0, domain.index(value))  # type: ignore[arg-type]
    except ValueError:
        return (1, value)


def _collection_members_canonical(values: tuple[object, ...], kind: str) -> bool:
    if kind == "subset":
        return all(
            tuple(_ref_key(item) for item in row[0])
            == tuple(sorted(_ref_key(item) for item in row[0]))
            for row in values  # type: ignore[index]
        )
    if kind == "edge":
        return all(_ref_key(row[0]) < _ref_key(row[1]) for row in values)  # type: ignore[index]
    if kind == "hyperedge":
        return all(
            tuple(_ref_key(item) for item in row[0])
            == tuple(sorted(_ref_key(item) for item in row[0]))
            for row in values  # type: ignore[index]
        )
    return True


def _collections_ordered(
    records: tuple[object, ...],
    extra: tuple[tuple[tuple[object, ...], str], ...] = (),
) -> bool:
    for values, kind in tuple(spec for record in records for spec in _collection_specs(record)) + extra:
        if not _collection_members_canonical(values, kind):
            return False
        if kind == "semantic_ref":
            continue
        keys = tuple(_collection_key(value, kind) for value in values)
        if keys != tuple(sorted(keys)):
            return False
    return True


def _collections_duplicated(
    records: tuple[object, ...],
    extra: tuple[tuple[tuple[object, ...], str], ...] = (),
) -> bool:
    for values, kind in tuple(spec for record in records for spec in _collection_specs(record)) + extra:
        keys = tuple(_collection_key(value, kind) for value in values)
        if len(keys) != len(set(keys)):
            return True
        if kind in {"subset", "hyperedge"} and any(
            len(row[0]) != len({_ref_key(item) for item in row[0]})  # type: ignore[index]
            for row in values
        ):
            return True
    return False


def _implicit_absence(values: tuple[object, ...]) -> bool:
    return any(value is Applicability.APPLICABLE for value in values)


def _claims_invalid(
    record: object,
    allowed_claims: tuple[ClaimStatus, ...],
    required_nonclaims: tuple[str, ...],
) -> bool:
    codes = record.nonclaim_codes  # type: ignore[attr-defined]
    return (
        record.claim_status not in allowed_claims  # type: ignore[attr-defined]
        or any(code not in _NONCLAIM_CODES for code in codes)
        or not set(required_nonclaims).issubset(codes)
    )


def _forbidden_runtime_behavior(records: tuple[object, ...]) -> bool:
    for record in records:
        allowed = set(record.__dataclass_fields__) | {"to_ecj1"}  # type: ignore[attr-defined]
        for name in type(record).__dict__:
            if not name.startswith("_") and name not in allowed:
                return True
    return False


def _prohibited_interference_claim(records: tuple[object, ...]) -> bool:
    prohibited = {"WAVE", "PHASE_SUPERPOSITION", "PHYSICAL_INTERFERENCE", "ELECTRICAL_VOLTAGE"}
    return any(
        getattr(type(record), "_prohibited_interference_claim", None) in prohibited
        for record in records
    )


def _number_fraction(value: CoreNumberV1) -> Fraction:
    if type(value) is IntegerV1:
        return Fraction(value.value)
    if type(value) is RationalV1:
        return Fraction(value.numerator.value, value.denominator.value)
    if type(value) is DecimalV1:
        coefficient = value.coefficient.value
        exponent = value.exponent10.value
        return Fraction(coefficient * 10**exponent) if exponent >= 0 else Fraction(
            coefficient, 10 ** (-exponent)
        )
    bits = int(value.bits, 16)  # type: ignore[union-attr]
    sign = -1 if bits >> 63 else 1
    exponent = (bits >> 52) & 0x7FF
    fraction = bits & ((1 << 52) - 1)
    if exponent == 0:
        significand, power = fraction, -1074
    else:
        significand, power = (1 << 52) | fraction, exponent - 1075
    if power >= 0:
        return Fraction(sign * significand * 2**power)
    return Fraction(sign * significand, 2 ** (-power))


def _magnitude(quantity: Quantity) -> Fraction:
    return _number_fraction(quantity.magnitude)


def _units_match(quantities: tuple[Quantity, ...]) -> bool:
    return not quantities or all(item.unit_ref == quantities[0].unit_ref for item in quantities[1:])


def _dimensions_match(quantities: tuple[Quantity, ...]) -> bool:
    return not quantities or all(
        item.dimension_ref == quantities[0].dimension_ref for item in quantities[1:]
    )


def _resolution_failed(resolution: ResolutionDetail) -> bool:
    return resolution.state in {
        ResolutionState.FAILED,
        ResolutionState.UNRESOLVED,
        ResolutionState.OUT_OF_BOUNDARY,
    } or bool(resolution.missing_part_refs)


def _check_common_prefix(
    interface: str,
    records: tuple[object, ...],
    implicit_values: tuple[object, ...],
    extra_collections: tuple[tuple[tuple[object, ...], str], ...] = (),
) -> None:
    for record in records:
        if _object_content_mismatch(record):
            _failure(
                FailureCode.I3_OBJECT_CONTENT_MISMATCH,
                interface,
                object_ref=_failure_object(record),
            )
    if _implicit_absence(implicit_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    if not _collections_ordered(records, extra_collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if _collections_duplicated(records, extra_collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)


def _check_common_suffix(interface: str, records: tuple[object, ...]) -> None:
    if _forbidden_runtime_behavior(records):
        _failure(FailureCode.FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR, interface)
    if _prohibited_interference_claim(records):
        _failure(FailureCode.PROHIBITED_INTERFERENCE_CLAIM, interface)
    if any(not _object_hash_matches(record) for record in records):
        _failure(FailureCode.HASH_MISMATCH, interface)


def _objective_unit_mismatch(record: JointObjectiveDeclaration) -> bool:
    return record.objective_kind != "SCALAR" and len(record.vector_component_refs) != len(
        record.component_unit_refs
    )


def _objective_invalid(record: JointObjectiveDeclaration) -> bool:
    if _surface_invalid(record) or _claims_invalid(
        record,
        (ClaimStatus.DEFINITION, ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE),
        (
            "NO_EMPIRICAL_VALIDATION",
            "NO_UNIVERSAL_SCALAR_OBJECTIVE",
            "NO_CAUSAL_IDENTIFICATION",
            "NO_SETTLEMENT_ENTITLEMENT",
            "NO_RUNTIME_BEHAVIOR",
        ),
    ):
        return True
    if not record.feasibility_first or not record.action_refs or not record.feasibility_constraint_refs:
        return True
    if not record.uncertainty_refs or not record.existence_assumption_refs or not record.regularity_assumption_refs:
        return True
    if record.objective_kind == "SCALAR":
        return (
            type(record.scalar_objective_ref) is not ObjectRef
            or bool(record.vector_component_refs)
            or bool(record.component_unit_refs)
            or bool(record.epsilon_constraint_refs)
        )
    if (
        record.scalar_objective_ref is not Applicability.NOT_APPLICABLE
        or not record.vector_component_refs
        or len(record.vector_component_refs) != len(record.component_unit_refs)
    ):
        return True
    if record.objective_kind == "VECTOR_EPSILON_CONSTRAINT":
        return not record.epsilon_constraint_refs
    return bool(record.epsilon_constraint_refs)


def _subset_key(values: tuple[ObjectRef, ...]) -> tuple[tuple[str, str, str], ...]:
    return tuple(_ref_key(item) for item in values)


def _complete_subsets(actions: tuple[ObjectRef, ...]) -> tuple[tuple[ObjectRef, ...], ...]:
    return tuple(
        subset
        for size in range(len(actions) + 1)
        for subset in combinations(actions, size)
    )


def _subset_rows_map(
    rows: tuple[tuple[tuple[ObjectRef, ...], Quantity], ...]
) -> dict[tuple[tuple[str, str, str], ...], Quantity]:
    return {_subset_key(subset): quantity for subset, quantity in rows}


def _interaction_quantities(record: FiniteSetInteractionWitness) -> tuple[Quantity, ...]:
    return (
        record.empty_baseline,
        *(quantity for _, quantity in record.subset_values),
        *(quantity for _, quantity in record.mobius_coefficients),
        *(quantity for _, quantity in record.truncation_residuals),
    )


def _interaction_unit_mismatch(record: FiniteSetInteractionWitness) -> bool:
    return any(quantity.unit_ref != record.value_unit_ref for quantity in _interaction_quantities(record))


def _interaction_dimension_mismatch(record: FiniteSetInteractionWitness) -> bool:
    return any(
        quantity.dimension_ref != record.value_dimension_ref
        for quantity in _interaction_quantities(record)
    )


def _subset_protocol_incomplete(record: FiniteSetInteractionWitness) -> bool:
    action_keys = {_ref_key(item) for item in record.action_refs}
    represented = tuple(record.subset_values) + tuple(record.mobius_coefficients) + tuple(
        record.truncation_residuals
    )
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.ALGEBRAIC_IDENTITY, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_PHYSICAL_CONSERVATION_FROM_MOBIUS_CLOSURE",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or not record.action_refs
        or not record.process_account_refs
        or any(any(_ref_key(item) not in action_keys for item in subset) for subset, _ in represented)
    )


def _subset_lattice_incomplete(record: FiniteSetInteractionWitness) -> bool:
    complete = tuple(_subset_key(item) for item in _complete_subsets(record.action_refs))
    values = tuple(_subset_key(item) for item, _ in record.subset_values)
    coefficients = tuple(_subset_key(item) for item, _ in record.mobius_coefficients)
    if values != complete or coefficients != complete:
        return True
    empty_value = _subset_rows_map(record.subset_values).get(())
    if empty_value is None:
        return True
    if record.normalization == "RAW_WITH_EXPLICIT_EMPTY":
        return _magnitude(empty_value) != _magnitude(record.empty_baseline)
    return _magnitude(empty_value) != 0


def _mobius_closure_failure(record: FiniteSetInteractionWitness) -> bool:
    values = _subset_rows_map(record.subset_values)
    coefficients = _subset_rows_map(record.mobius_coefficients)
    complete = _complete_subsets(record.action_refs)
    for subset in complete:
        expected = Fraction(0)
        for size in range(len(subset) + 1):
            for inner in combinations(subset, size):
                expected += (-1) ** (len(subset) - len(inner)) * _magnitude(
                    values[_subset_key(inner)]
                )
        if _magnitude(coefficients[_subset_key(subset)]) != expected:
            return True
    for subset in complete:
        reconstructed = sum(
            (
                _magnitude(coefficients[_subset_key(inner)])
                for size in range(len(subset) + 1)
                for inner in combinations(subset, size)
            ),
            Fraction(0),
        )
        if reconstructed != _magnitude(values[_subset_key(subset)]):
            return True
    return False


def _truncation_residual_mismatch(record: FiniteSetInteractionWitness) -> bool:
    if type(record.truncation_order) is Applicability:
        return record.truncation_order is not Applicability.NOT_APPLICABLE or bool(
            record.truncation_residuals
        )
    order = record.truncation_order.value
    if order < 0 or order >= len(record.action_refs):
        return True
    residuals = _subset_rows_map(record.truncation_residuals)
    values = _subset_rows_map(record.subset_values)
    coefficients = _subset_rows_map(record.mobius_coefficients)
    required = tuple(subset for subset in _complete_subsets(record.action_refs) if len(subset) > order)
    if tuple(_subset_key(subset) for subset, _ in record.truncation_residuals) != tuple(
        _subset_key(subset) for subset in required
    ):
        return True
    for subset in required:
        truncated = sum(
            (
                _magnitude(coefficients[_subset_key(inner)])
                for size in range(min(order, len(subset)) + 1)
                for inner in combinations(subset, size)
            ),
            Fraction(0),
        )
        if _magnitude(residuals[_subset_key(subset)]) != _magnitude(
            values[_subset_key(subset)]
        ) - truncated:
            return True
    return False


def _same_baseline_quantities(record: SameBaselineNonadditivityWitness) -> tuple[Quantity, ...]:
    return (
        record.empty_baseline,
        record.joint_value,
        *(quantity for _, quantity in record.singleton_values),
        record.nonadditivity_value,
    )


def _same_baseline_invalid(record: SameBaselineNonadditivityWitness) -> bool:
    singleton_keys = tuple(_ref_key(reference) for reference, _ in record.singleton_values)
    action_keys = tuple(_ref_key(reference) for reference in record.action_refs)
    expected = _magnitude(record.joint_value) - sum(
        (_magnitude(quantity) for _, quantity in record.singleton_values), Fraction(0)
    ) + (len(record.action_refs) - 1) * _magnitude(record.empty_baseline)
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.ALGEBRAIC_IDENTITY, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or not record.action_refs
        or singleton_keys != action_keys
        or not record.process_account_refs
        or _magnitude(record.nonadditivity_value) != expected
    )


def _serial_invalid(record: SerialComparatorInteractionWitness) -> bool:
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.ALGEBRAIC_IDENTITY, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or not record.action_refs
        or {_ref_key(item) for item in record.serial_order_refs}
        != {_ref_key(item) for item in record.action_refs}
        or len(record.serial_order_refs) != len(record.action_refs)
        or not record.process_account_refs
        or _magnitude(record.interaction_value)
        != _magnitude(record.parallel_value) - _magnitude(record.serial_value)
    )


def _mixed_quantities(record: MixedMarginalWitness) -> tuple[Quantity, ...]:
    return (
        record.base_quantity_i,
        record.base_quantity_j,
        record.delta_i,
        record.delta_j,
        record.rectangle_value_00,
        record.rectangle_value_10,
        record.rectangle_value_01,
        record.rectangle_value_11,
        record.mixed_difference,
    )


def _mixed_unit_mismatch(record: MixedMarginalWitness) -> bool:
    values = (
        record.rectangle_value_00,
        record.rectangle_value_10,
        record.rectangle_value_01,
        record.rectangle_value_11,
        record.mixed_difference,
    )
    return (
        record.base_quantity_i.unit_ref != record.delta_i.unit_ref
        or record.base_quantity_j.unit_ref != record.delta_j.unit_ref
        or not _units_match(values)
    )


def _mixed_dimension_mismatch(record: MixedMarginalWitness) -> bool:
    values = (
        record.rectangle_value_00,
        record.rectangle_value_10,
        record.rectangle_value_01,
        record.rectangle_value_11,
        record.mixed_difference,
    )
    return (
        record.base_quantity_i.dimension_ref != record.delta_i.dimension_ref
        or record.base_quantity_j.dimension_ref != record.delta_j.dimension_ref
        or not _dimensions_match(values)
    )


def _mixed_invalid(record: MixedMarginalWitness) -> bool:
    difference = (
        _magnitude(record.rectangle_value_11)
        - _magnitude(record.rectangle_value_10)
        - _magnitude(record.rectangle_value_01)
        + _magnitude(record.rectangle_value_00)
    )
    if (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.action_i_ref == record.action_j_ref
        or record.quantity_coordinate_i_ref == record.quantity_coordinate_j_ref
        or _magnitude(record.delta_i) == 0
        or _magnitude(record.delta_j) == 0
        or _magnitude(record.mixed_difference) != difference
        or not record.process_account_refs
    ):
        return True
    if record.regularity_status == "C2_ON_COMPLETE_RECTANGLE":
        return type(record.normalized_mixed_marginal) is not Quantity or _magnitude(
            record.normalized_mixed_marginal
        ) != difference / (_magnitude(record.delta_i) * _magnitude(record.delta_j))
    if record.regularity_status == "NONSMOOTH_FINITE_DIFFERENCE_ONLY":
        return type(record.normalized_mixed_marginal) is not ResolutionDetail
    if record.regularity_status == "UNRESOLVED":
        return type(record.normalized_mixed_marginal) is not ResolutionDetail
    return False


def _commutator_rows(record: CommutatorWitness) -> tuple[tuple[ObjectRef, Quantity], ...]:
    return record.bracket_components + record.order_difference_components + record.remainder_components


def _commutator_unit_mismatch(
    record: CommutatorWitness,
    left: StateTransformationGeneratorDeclaration,
    right: StateTransformationGeneratorDeclaration,
) -> bool:
    return (
        record.step_extent.unit_ref != left.extent_unit_ref
        or record.step_extent.unit_ref != right.extent_unit_ref
        or any(
            order.unit_ref != remainder.unit_ref
            for (_, order), (_, remainder) in zip(
                record.order_difference_components, record.remainder_components, strict=False
            )
        )
    )


def _commutator_dimension_mismatch(
    record: CommutatorWitness,
    left: StateTransformationGeneratorDeclaration,
    right: StateTransformationGeneratorDeclaration,
) -> bool:
    return (
        record.step_extent.dimension_ref != left.extent_dimension_ref
        or record.step_extent.dimension_ref != right.extent_dimension_ref
        or any(
            order.dimension_ref != remainder.dimension_ref
            for (_, order), (_, remainder) in zip(
                record.order_difference_components, record.remainder_components, strict=False
            )
        )
    )


def _commutator_invalid(
    record: CommutatorWitness,
    left: StateTransformationGeneratorDeclaration,
    right: StateTransformationGeneratorDeclaration,
) -> bool:
    coordinates = tuple(_ref_key(item) for item in left.state_coordinate_refs)
    row_coordinates = tuple(
        tuple(_ref_key(reference) for reference, _ in rows)
        for rows in (
            record.bracket_components,
            record.order_difference_components,
            record.remainder_components,
        )
    )
    if (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_NEIGHBOURHOOD_COMMUTATIVITY_FROM_ONE_STATE",
                "NO_PHYSICAL_PROPAGATION",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.left_generator_ref != _record_ref(left)
        or record.right_generator_ref != _record_ref(right)
        or left is right
        or record.left_generator_ref == record.right_generator_ref
        or left.boundary_ref != right.boundary_ref
        or record.boundary_ref != left.boundary_ref
        or left.domain_ref != right.domain_ref
        or record.domain_ref != left.domain_ref
        or left.topology_ref != right.topology_ref
        or record.topology_ref != left.topology_ref
        or tuple(_ref_key(item) for item in right.state_coordinate_refs) != coordinates
        or any(items != coordinates for items in row_coordinates)
        or any(code not in _REGULARITY_CODES for code in record.regularity_codes)
        or not record.process_account_refs
    ):
        return True
    step_squared = _magnitude(record.step_extent) ** 2
    for (_, bracket), (_, order), (_, remainder) in zip(
        record.bracket_components,
        record.order_difference_components,
        record.remainder_components,
        strict=True,
    ):
        if _magnitude(order) != _magnitude(bracket) * step_squared + _magnitude(remainder):
            return True
    if record.commutativity_status == "NONCOMMUTING":
        return not any(_magnitude(quantity) != 0 for _, quantity in record.order_difference_components)
    if record.commutativity_status in {
        "COMMUTING_ON_DECLARED_NEIGHBOURHOOD",
        "ZERO_AT_ONE_STATE_ONLY",
    }:
        return any(_magnitude(quantity) != 0 for _, quantity in record.order_difference_components)
    return False


def _commutativity_scope_overclaim(record: CommutatorWitness) -> bool:
    return (
        record.commutativity_status == "COMMUTING_ON_DECLARED_NEIGHBOURHOOD"
        and record.commutativity_scope != "DECLARED_NEIGHBOURHOOD"
    ) or (
        record.commutativity_status == "ZERO_AT_ONE_STATE_ONLY"
        and record.commutativity_scope != "ONE_STATE"
    )


def _shared_visibility_missing(record: SharedConstraintFactor) -> bool:
    return (
        tuple(_ref_key(item) for item in record.demand_visibility_refs)
        != tuple(_ref_key(item) for item in record.action_refs)
        or _resolution_failed(record.hidden_state_resolution)
        or _resolution_failed(record.binding_resolution)
    )


def _shared_ownership_invalid(record: SharedConstraintFactor) -> bool:
    if _surface_invalid(record) or _claims_invalid(
        record,
        (
            ClaimStatus.DEFINITION,
            ClaimStatus.MODEL_DEPENDENT_RESULT,
            ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE,
        ),
        (
            "NO_EMPIRICAL_VALIDATION",
            "NO_CAUSAL_IDENTIFICATION",
            "NO_PHYSICAL_PROPAGATION",
            "NO_RUNTIME_BEHAVIOR",
        ),
    ) or len(record.action_refs) < 2:
        return True
    if record.ownership_kind == "LOWEST_COMPLETE_COMMON_BOUNDARY":
        return (
            record.hierarchy_kind != "TREE"
            or type(record.lowest_common_boundary_ref) is not ObjectRef
            or record.lowest_common_boundary_ref != record.owner_boundary_ref
            or record.distributed_protocol_ref is not Applicability.NOT_APPLICABLE
        )
    if record.ownership_kind == "DECLARED_FACTOR_BOUNDARY":
        return (
            record.lowest_common_boundary_ref is not Applicability.NOT_APPLICABLE
            or record.distributed_protocol_ref is not Applicability.NOT_APPLICABLE
        )
    return (
        record.hierarchy_kind not in {"FEDERATION", "OVERLAPPING_AUTHORITY"}
        or record.lowest_common_boundary_ref is not Applicability.NOT_APPLICABLE
        or type(record.distributed_protocol_ref) is not ObjectRef
    )


def _edge_actions(record: InteractionTopologySnapshot) -> tuple[tuple[ObjectRef, ...], ...]:
    pairs = tuple((row[0], row[1]) for row in record.structural_pair_edges + record.active_pair_edges)
    hypers = tuple(row[0] for row in record.structural_hyperedges + record.active_hyperedges)
    return pairs + hypers


def _topology_invalid(
    record: InteractionTopologySnapshot,
    factors: tuple[SharedConstraintFactor, ...],
    interactions: tuple[FiniteSetInteractionWitness, ...],
) -> bool:
    vertices = {_ref_key(item) for item in record.vertex_action_refs}
    factor_refs = tuple(_record_ref(item) for item in factors)
    interaction_refs = {_ref_key(_record_ref(item)) for item in interactions}
    structural_pairs = set(record.structural_pair_edges)
    structural_hypers = set(record.structural_hyperedges)
    if (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.DEFINITION, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_PHYSICAL_PROPAGATION",
                "NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED",
                "NO_PHYSICAL_PHASE_INTERFERENCE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or not record.vertex_action_refs
        or any(len(actions) < 2 for actions in _edge_actions(record))
        or any(any(_ref_key(item) not in vertices for item in actions) for actions in _edge_actions(record))
        or any(
            row[2] not in _INTERACTION_TYPES
            for row in record.structural_pair_edges + record.active_pair_edges
        )
        or any(
            row[1] not in _INTERACTION_TYPES
            for row in record.structural_hyperedges + record.active_hyperedges
        )
        or any(row not in structural_pairs for row in record.active_pair_edges)
        or any(row not in structural_hypers for row in record.active_hyperedges)
        or record.factor_refs != factor_refs
        or any(any(_ref_key(item) not in vertices for item in factor.action_refs) for factor in factors)
    ):
        return True
    expected_incidence = tuple(
        sorted(
            (
                (_record_ref(factor), action)
                for factor in factors
                for action in factor.action_refs
            ),
            key=lambda row: (_ref_key(row[0]), _ref_key(row[1])),
        )
    )
    if record.factor_incidence != expected_incidence:
        return True
    for left, right, kind, witness_ref in record.structural_pair_edges:
        if kind == "MOBIUS_FINITE" and _ref_key(witness_ref) not in interaction_refs:
            return True
        if kind == "SHARED_CONSTRAINT" and witness_ref not in factor_refs:
            return True
        if left == right:
            return True
    for actions, kind, witness_ref in record.structural_hyperedges:
        if kind == "MOBIUS_FINITE":
            matching = [item for item in interactions if _record_ref(item) == witness_ref]
            if not matching or tuple(actions) != matching[0].action_refs:
                return True
        if kind == "SHARED_CONSTRAINT" and witness_ref not in factor_refs:
            return True
    for interaction in interactions:
        if (
            interaction.boundary_ref != record.boundary_ref
            or interaction.horizon_ref != record.horizon_ref
            or interaction.subset_protocol_ref != record.subset_protocol_ref
        ):
            return True
    return False


def _hidden_topology_unresolved(
    record: InteractionTopologySnapshot, factors: tuple[SharedConstraintFactor, ...]
) -> bool:
    return _resolution_failed(record.hidden_state_resolution) or any(
        _resolution_failed(factor.hidden_state_resolution)
        or _resolution_failed(factor.binding_resolution)
        for factor in factors
    )


def _boundary_preservation_invalid(
    record: InteractionTopologySnapshot,
    interactions: tuple[FiniteSetInteractionWitness, ...],
    equivalence: BoundaryHistoryEquivalenceWitness | Applicability,
) -> bool:
    if record.boundary_preservation_status == "NOT_ASSESSED":
        return (
            record.boundary_equivalence_ref is not Applicability.NOT_APPLICABLE
            or equivalence is not Applicability.NOT_APPLICABLE
            or bool(record.exposed_interaction_pairs)
        )
    if record.boundary_preservation_status == "NOT_PRESERVED":
        return False
    if type(equivalence) is not BoundaryHistoryEquivalenceWitness:
        return True
    vertices = {_ref_key(item) for item in record.vertex_action_refs}
    interaction_action_sets = tuple(
        ({_ref_key(item) for item in interaction.action_refs}, interaction)
        for interaction in interactions
    )
    exposed_evidence = tuple(
        tuple(
            interaction
            for action_keys, interaction in interaction_action_sets
            if {_ref_key(left), _ref_key(right)}.issubset(action_keys)
        )
        for left, right in record.exposed_interaction_pairs
    )
    return (
        record.boundary_equivalence_ref != _record_ref(equivalence)
        or not record.exposed_interaction_pairs
        or any(
            _ref_key(left) not in vertices or _ref_key(right) not in vertices or left == right
            for left, right in record.exposed_interaction_pairs
        )
        or any(not evidence for evidence in exposed_evidence)
        or any(
            _interaction_unit_mismatch(interaction)
            or _interaction_dimension_mismatch(interaction)
            or _subset_protocol_incomplete(interaction)
            or _subset_lattice_incomplete(interaction)
            or _mobius_closure_failure(interaction)
            or _truncation_residual_mismatch(interaction)
            for evidence in exposed_evidence
            for interaction in evidence
        )
        or record.boundary_ref not in {equivalence.detailed_boundary_ref, equivalence.parent_boundary_ref}
        or record.horizon_ref != equivalence.horizon_ref
        or not equivalence.hidden_state_relation_preserved
        or not equivalence.all_admitted_histories_covered
        or equivalence.snapshot_equality_only
        or equivalence.one_state_generator_equality_only
        or not equivalence.internal_topology_export_refs
        or _resolution_failed(equivalence.resolution)
    )


def _allocation_unit_mismatch(record: AllocationOptimalityWitness) -> bool:
    selected = tuple(quantity for _, quantity in record.selected_quantities)
    marginal = tuple(quantity for _, quantity in record.marginal_values)
    return not _units_match(selected) or not _units_match(marginal)


def _allocation_invalid(
    record: AllocationOptimalityWitness, objective: JointObjectiveDeclaration
) -> bool:
    selected_keys = tuple(_ref_key(item) for item in record.selected_action_refs)
    quantity_keys = tuple(_ref_key(item) for item, _ in record.selected_quantities)
    marginal_keys = tuple(_ref_key(item) for item, _ in record.marginal_values)
    objective_keys = {_ref_key(item) for item in objective.action_refs}
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.objective_ref != _record_ref(objective)
        or record.boundary_ref != objective.boundary_ref
        or record.horizon_ref != objective.horizon_ref
        or not selected_keys
        or any(key not in objective_keys for key in selected_keys)
        or quantity_keys != selected_keys
        or marginal_keys != selected_keys
        or record.deterministic_tie_rule_ref != objective.deterministic_tie_rule_ref
        or not objective.feasibility_first
        or not record.feasibility_certificate_ref
        or _resolution_failed(record.result_resolution)
    )


def _certificate_inapplicable(
    record: AllocationOptimalityWitness, objective: JointObjectiveDeclaration
) -> bool:
    kind = record.certificate_kind
    kkt = record.kkt_applicability
    if kind == "KKT_LOCAL":
        return kkt != "APPLICABLE_LOCAL_ONLY" or not record.constraint_qualification_refs
    if kind == "KKT_GLOBAL_CONVEX":
        return (
            kkt != "APPLICABLE_GLOBAL_WITH_CONVEXITY"
            or not record.constraint_qualification_refs
            or not record.convexity_or_globality_refs
        )
    if kind in {"COMBINATORIAL", "MIXED_INTEGER"}:
        return kkt not in {"INAPPLICABLE_DISCRETE_OR_NONSMOOTH", "NOT_USED"}
    if kind == "PARETO":
        return objective.objective_kind != "VECTOR_PARETO" or kkt != "NOT_USED"
    if kind == "LEXICOGRAPHIC":
        return objective.objective_kind != "VECTOR_LEXICOGRAPHIC" or kkt != "NOT_USED"
    if kind == "EPSILON_CONSTRAINT":
        return objective.objective_kind != "VECTOR_EPSILON_CONSTRAINT" or kkt != "NOT_USED"
    return kkt != "NOT_USED"


def _decomposition_quantities(record: ScalarDecompositionWitness) -> tuple[Quantity, ...]:
    return (
        record.baseline_value,
        record.selected_total,
        *(quantity for _, quantity in record.shares),
        record.residual,
    )


def _decomposition_invalid(
    record: ScalarDecompositionWitness,
    objective: JointObjectiveDeclaration,
    allocation: AllocationOptimalityWitness,
) -> bool:
    expected = _magnitude(record.baseline_value) + sum(
        (_magnitude(quantity) for _, quantity in record.shares), Fraction(0)
    ) + _magnitude(record.residual)
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.ALGEBRAIC_IDENTITY, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_SETTLEMENT_ENTITLEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.objective_ref != _record_ref(objective)
        or record.allocation_ref != _record_ref(allocation)
        or allocation.objective_ref != record.objective_ref
        or objective.objective_kind != "SCALAR"
        or tuple(_ref_key(item) for item, _ in record.shares)
        != tuple(_ref_key(item) for item in allocation.selected_action_refs)
        or _magnitude(record.selected_total) != expected
        or _resolution_failed(record.closure_resolution)
        or (
            record.decomposition_kind == "AUMANN_SHAPLEY_RADIAL"
            and type(record.differentiability_witness_ref) is not ObjectRef
        )
    )


def _decomposition_provenance_incomplete(
    record: ScalarDecompositionWitness,
    objective: JointObjectiveDeclaration,
    allocation: AllocationOptimalityWitness,
) -> bool:
    required = {
        _ref_key(record.path_ref),
        _ref_key(record.objective_ref),
        _ref_key(record.allocation_ref),
        *(_ref_key(item) for item in allocation.selected_action_refs),
    }
    return not required.issubset({_ref_key(item) for item in record.path_provenance_refs})


def _acceptance_invalid(record: InstitutionalAcceptanceRule) -> bool:
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE,),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or not record.eligible_actor_refs
        or not record.eligible_action_refs
        or not record.provenance_authority_refs
        or record.issuing_authority_ref not in record.provenance_authority_refs
    )


def _settlement_unit_mismatch(record: InstitutionalSettlementRule) -> bool:
    return record.settlement_unit_ref not in record.provenance_authority_refs


def _settlement_dimension_mismatch(record: InstitutionalSettlementRule) -> bool:
    return record.settlement_dimension_ref not in record.provenance_authority_refs


def _settlement_invalid(
    record: InstitutionalSettlementRule, acceptance: InstitutionalAcceptanceRule
) -> bool:
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.INSTITUTIONAL_DESIGN_CHOICE,),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_MEANING_FOR_INSTITUTIONAL_SHARE",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.acceptance_rule_ref != _record_ref(acceptance)
        or record.jurisdiction_ref != acceptance.jurisdiction_ref
        or record.boundary_ref != acceptance.boundary_ref
        or record.issuing_authority_ref != acceptance.issuing_authority_ref
        or record.effective_horizon_ref != acceptance.effective_horizon_ref
        or not record.provenance_authority_refs
        or record.issuing_authority_ref not in record.provenance_authority_refs
    )


def _causal_settlement_conflation(record: InstitutionalSettlementRule) -> bool:
    if record.settlement_basis == "INDEPENDENT_INSTITUTIONAL_RULE":
        return (
            record.causal_identification_requirement
            != "NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT"
            or record.causal_claim_status != "NOT_MADE"
        )
    return (
        record.causal_identification_requirement
        != "IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM"
        or record.causal_claim_status != CausalIdentificationStatus.IDENTIFIED.value
    )


def _settlement_closure_missing(record: InstitutionalSettlementRule) -> bool:
    return not record.explicit_residual_required


def validate_joint_objective(record: JointObjectiveDeclaration, /) -> None:
    if type(record) is not JointObjectiveDeclaration:
        _formation_failure("JointObjectiveDeclaration")
    interface = "validate_joint_objective"
    records = (record,)
    _check_common_prefix(interface, records, (record.scalar_objective_ref,))
    if _objective_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _objective_invalid(record):
        _failure(FailureCode.OBJECTIVE_GRAMMAR_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_finite_set_interaction(record: FiniteSetInteractionWitness, /) -> None:
    if type(record) is not FiniteSetInteractionWitness:
        _formation_failure("FiniteSetInteractionWitness")
    interface = "validate_finite_set_interaction"
    records = (record,)
    _check_common_prefix(interface, records, (record.truncation_order,))
    if _interaction_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _interaction_dimension_mismatch(record):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _subset_protocol_incomplete(record):
        _failure(FailureCode.SUBSET_PROTOCOL_INCOMPLETE, interface)
    if _subset_lattice_incomplete(record):
        _failure(FailureCode.SUBSET_LATTICE_INCOMPLETE, interface)
    if _mobius_closure_failure(record):
        _failure(FailureCode.MOBIUS_CLOSURE_FAILURE, interface)
    if _truncation_residual_mismatch(record):
        _failure(FailureCode.TRUNCATION_RESIDUAL_MISMATCH, interface)
    _check_common_suffix(interface, records)
    return None


def validate_same_baseline_nonadditivity(
    record: SameBaselineNonadditivityWitness, /
) -> None:
    if type(record) is not SameBaselineNonadditivityWitness:
        _formation_failure("SameBaselineNonadditivityWitness")
    interface = "validate_same_baseline_nonadditivity"
    records = (record,)
    _check_common_prefix(interface, records, ())
    quantities = _same_baseline_quantities(record)
    if any(quantity.unit_ref != record.value_unit_ref for quantity in quantities):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if any(quantity.dimension_ref != record.value_dimension_ref for quantity in quantities):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _same_baseline_invalid(record):
        _failure(FailureCode.COMPARATOR_INTERACTION_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_serial_comparator_interaction(
    record: SerialComparatorInteractionWitness, /
) -> None:
    if type(record) is not SerialComparatorInteractionWitness:
        _formation_failure("SerialComparatorInteractionWitness")
    interface = "validate_serial_comparator_interaction"
    records = (record,)
    _check_common_prefix(interface, records, ())
    quantities = (record.parallel_value, record.serial_value, record.interaction_value)
    if any(quantity.unit_ref != record.value_unit_ref for quantity in quantities):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if any(quantity.dimension_ref != record.value_dimension_ref for quantity in quantities):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _serial_invalid(record):
        _failure(FailureCode.COMPARATOR_INTERACTION_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_mixed_marginal(record: MixedMarginalWitness, /) -> None:
    if type(record) is not MixedMarginalWitness:
        _formation_failure("MixedMarginalWitness")
    interface = "validate_mixed_marginal"
    records = (record,)
    _check_common_prefix(interface, records, ())
    if _mixed_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _mixed_dimension_mismatch(record):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _mixed_invalid(record):
        _failure(FailureCode.MIXED_MARGINAL_WITNESS_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_commutator(
    record: CommutatorWitness,
    left_generator: StateTransformationGeneratorDeclaration,
    right_generator: StateTransformationGeneratorDeclaration,
    /,
) -> None:
    if type(record) is not CommutatorWitness:
        _formation_failure("CommutatorWitness")
    if type(left_generator) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    if type(right_generator) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    interface = "validate_commutator"
    records = (record, left_generator, right_generator)
    _check_common_prefix(interface, records, ())
    if _commutator_unit_mismatch(record, left_generator, right_generator):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _commutator_dimension_mismatch(record, left_generator, right_generator):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _commutator_invalid(record, left_generator, right_generator):
        _failure(FailureCode.COMMUTATOR_WITNESS_INVALID, interface)
    if _commutativity_scope_overclaim(record):
        _failure(FailureCode.COMMUTATIVITY_SCOPE_OVERCLAIM, interface)
    _check_common_suffix(interface, records)
    return None


def validate_shared_constraint_factor(record: SharedConstraintFactor, /) -> None:
    if type(record) is not SharedConstraintFactor:
        _formation_failure("SharedConstraintFactor")
    interface = "validate_shared_constraint_factor"
    records = (record,)
    _check_common_prefix(
        interface,
        records,
        (
            record.constraint_unit_ref,
            record.lowest_common_boundary_ref,
            record.distributed_protocol_ref,
        ),
    )
    if _shared_visibility_missing(record):
        _failure(FailureCode.SHARED_BOUNDARY_VISIBILITY_MISSING, interface)
    if _shared_ownership_invalid(record):
        _failure(FailureCode.SHARED_CONSTRAINT_OWNERSHIP_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_interaction_topology_snapshot(
    record: InteractionTopologySnapshot,
    factors: tuple[SharedConstraintFactor, ...],
    interactions: tuple[FiniteSetInteractionWitness, ...],
    equivalence: BoundaryHistoryEquivalenceWitness | Applicability,
    /,
) -> None:
    if type(record) is not InteractionTopologySnapshot:
        _formation_failure("InteractionTopologySnapshot")
    if type(factors) is not tuple or not all(type(item) is SharedConstraintFactor for item in factors):
        _formation_failure("tuple[SharedConstraintFactor,...]")
    if type(interactions) is not tuple or not all(
        type(item) is FiniteSetInteractionWitness for item in interactions
    ):
        _formation_failure("tuple[FiniteSetInteractionWitness,...]")
    if type(equivalence) not in {BoundaryHistoryEquivalenceWitness, Applicability}:
        _formation_failure("BoundaryHistoryEquivalenceWitness|Applicability")
    interface = "validate_interaction_topology_snapshot"
    records: tuple[object, ...] = (record, *factors, *interactions)
    if type(equivalence) is BoundaryHistoryEquivalenceWitness:
        records += (equivalence,)
    factor_ref_values = tuple(_record_ref(item) for item in factors)
    interaction_ref_values = tuple(_record_ref(item) for item in interactions)
    _check_common_prefix(
        interface,
        records,
        (
            record.physical_transport_topology_ref,
            record.institutional_constraint_topology_ref,
            record.boundary_equivalence_ref,
            equivalence,
        ),
        ((factor_ref_values, "ref"), (interaction_ref_values, "ref")),
    )
    if _topology_invalid(record, factors, interactions):
        _failure(FailureCode.INTERACTION_TOPOLOGY_INVALID, interface)
    if _hidden_topology_unresolved(record, factors):
        _failure(FailureCode.HIDDEN_STATE_TOPOLOGY_UNRESOLVED, interface)
    if _boundary_preservation_invalid(record, interactions, equivalence):
        _failure(FailureCode.BOUNDARY_INTERACTION_PRESERVATION_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_allocation_optimality(
    record: AllocationOptimalityWitness, objective: JointObjectiveDeclaration, /
) -> None:
    if type(record) is not AllocationOptimalityWitness:
        _formation_failure("AllocationOptimalityWitness")
    if type(objective) is not JointObjectiveDeclaration:
        _formation_failure("JointObjectiveDeclaration")
    interface = "validate_allocation_optimality"
    records = (record, objective)
    _check_common_prefix(interface, records, ())
    if _allocation_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _allocation_invalid(record, objective):
        _failure(FailureCode.ALLOCATION_FEASIBILITY_INVALID, interface)
    if _certificate_inapplicable(record, objective):
        _failure(FailureCode.OPTIMALITY_CERTIFICATE_INAPPLICABLE, interface)
    _check_common_suffix(interface, records)
    return None


def validate_scalar_decomposition(
    record: ScalarDecompositionWitness,
    objective: JointObjectiveDeclaration,
    allocation: AllocationOptimalityWitness,
    /,
) -> None:
    if type(record) is not ScalarDecompositionWitness:
        _formation_failure("ScalarDecompositionWitness")
    if type(objective) is not JointObjectiveDeclaration:
        _formation_failure("JointObjectiveDeclaration")
    if type(allocation) is not AllocationOptimalityWitness:
        _formation_failure("AllocationOptimalityWitness")
    interface = "validate_scalar_decomposition"
    records = (record, objective, allocation)
    _check_common_prefix(interface, records, (record.differentiability_witness_ref,))
    quantities = _decomposition_quantities(record)
    if not _units_match(quantities):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if not _dimensions_match(quantities):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _decomposition_invalid(record, objective, allocation):
        _failure(FailureCode.SCALAR_DECOMPOSITION_INVALID, interface)
    if _decomposition_provenance_incomplete(record, objective, allocation):
        _failure(FailureCode.DECOMPOSITION_PROVENANCE_INCOMPLETE, interface)
    _check_common_suffix(interface, records)
    return None


def validate_institutional_acceptance_rule(record: InstitutionalAcceptanceRule, /) -> None:
    if type(record) is not InstitutionalAcceptanceRule:
        _formation_failure("InstitutionalAcceptanceRule")
    interface = "validate_institutional_acceptance_rule"
    records = (record,)
    _check_common_prefix(interface, records, ())
    if _acceptance_invalid(record):
        _failure(FailureCode.INSTITUTIONAL_RULE_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_institutional_settlement_rule(
    record: InstitutionalSettlementRule, acceptance_rule: InstitutionalAcceptanceRule, /
) -> None:
    if type(record) is not InstitutionalSettlementRule:
        _formation_failure("InstitutionalSettlementRule")
    if type(acceptance_rule) is not InstitutionalAcceptanceRule:
        _formation_failure("InstitutionalAcceptanceRule")
    interface = "validate_institutional_settlement_rule"
    records = (record, acceptance_rule)
    _check_common_prefix(interface, records, ())
    if _settlement_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _settlement_dimension_mismatch(record):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _settlement_invalid(record, acceptance_rule):
        _failure(FailureCode.INSTITUTIONAL_RULE_INVALID, interface)
    if _causal_settlement_conflation(record):
        _failure(FailureCode.CAUSAL_SETTLEMENT_CONFLATION, interface)
    if _settlement_closure_missing(record):
        _failure(FailureCode.SETTLEMENT_RESIDUAL_CLOSURE_MISSING, interface)
    _check_common_suffix(interface, records)
    return None


__all__ = (
    "JointObjectiveDeclaration",
    "FiniteSetInteractionWitness",
    "SameBaselineNonadditivityWitness",
    "SerialComparatorInteractionWitness",
    "MixedMarginalWitness",
    "CommutatorWitness",
    "SharedConstraintFactor",
    "InteractionTopologySnapshot",
    "AllocationOptimalityWitness",
    "ScalarDecompositionWitness",
    "InstitutionalAcceptanceRule",
    "InstitutionalSettlementRule",
    "validate_joint_objective",
    "validate_finite_set_interaction",
    "validate_same_baseline_nonadditivity",
    "validate_serial_comparator_interaction",
    "validate_mixed_marginal",
    "validate_commutator",
    "validate_shared_constraint_factor",
    "validate_interaction_topology_snapshot",
    "validate_allocation_optimality",
    "validate_scalar_decomposition",
    "validate_institutional_acceptance_rule",
    "validate_institutional_settlement_rule",
)
