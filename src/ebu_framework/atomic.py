"""Inert atomic, finite, hybrid, and recursive EBU declarations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import Literal, NoReturn

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
_STATE_ROLE_CODES = (
    "STOCK",
    "CONVERSION",
    "LOSS",
    "BURDEN",
    "COMMITMENT",
    "RESERVATION",
    "QUEUE",
    "IN_TRANSIT",
    "DELAYED_EFFECT",
    "MODE",
    "TOPOLOGY",
    "CLOCK",
    "POLICY_MEMORY",
)
_BOUNDARY_OBSERVABLE_CODES = (
    "ACCEPT_REJECT",
    "PERMISSION",
    "RESERVATION",
    "TYPED_FLOW",
    "CONVERSION",
    "LOSS",
    "OUTFLOW",
    "TIMING",
    "COMPLETION",
    "PENDING_COMMITMENT",
    "DELAYED_EFFECT",
    "MEMORY",
    "PHYSICAL_RECEIPT",
    "RESIDUAL",
    "SETTLEMENT_VISIBLE_RECORD",
)
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


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.atomic", name, "1.0.0")


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


def _quantity_or_applicability(value: object) -> bool:
    return type(value) is Quantity or type(value) is Applicability


def _number_or_applicability(value: object) -> bool:
    return type(value) in _CORE_NUMBER_TYPES or type(value) is Applicability


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _string_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is str for item in value)


def _component_unit_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 3
        and all(type(item) is ObjectRef for item in row)
        for row in value
    )


def _unit_relation_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 4
        and all(type(item) is ObjectRef for item in row[:3])
        and _object_or_applicability(row[3])
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
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ExtentDefinition:
    envelope: CommonObjectEnvelope
    extent_family: Literal[
        "PHYSICAL_TIME",
        "PROCESS_OR_ROUTE_EXTENT",
        "TYPED_CARRIER_QUANTITY",
        "DIMENSIONLESS_PARTICIPATION",
    ]
    action_family_ref: ObjectRef
    coordinate_ref: ObjectRef
    coordinate_unit_ref: ObjectRef
    coordinate_dimension_ref: ObjectRef
    generator_codomain_ref: ObjectRef
    domain_ref: ObjectRef
    topology_ref: ObjectRef
    orientation: Literal[
        "INCREASING_CLOCK",
        "DECLARED_FORWARD_PROCESS",
        "DECLARED_FORWARD_CARRIER",
        "ZERO_TO_ONE_PARTICIPATION",
    ]
    divisibility: Literal[
        "DECLARED_NONATOMIC",
        "DECLARED_REFINABLE_IMMUTABLE_BUNDLE",
        "NOT_DIVISIBLE",
    ]
    carrier_or_bundle_ref: ObjectRef | Applicability
    clock_or_order_ref: ObjectRef | Applicability
    path_or_process_ref: ObjectRef | Applicability
    lower_bound: Quantity | Applicability
    upper_bound: Quantity | Applicability
    interval_closure: Literal[
        "UNBOUNDED", "CLOSED", "LEFT_CLOSED_RIGHT_OPEN", "OPEN"
    ]
    reversible_flow_ref: ObjectRef | Applicability
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.action_family_ref,
            self.coordinate_ref,
            self.coordinate_unit_ref,
            self.coordinate_dimension_ref,
            self.generator_codomain_ref,
            self.domain_ref,
            self.topology_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.extent_family) is str
            and self.extent_family
            in {
                "PHYSICAL_TIME",
                "PROCESS_OR_ROUTE_EXTENT",
                "TYPED_CARRIER_QUANTITY",
                "DIMENSIONLESS_PARTICIPATION",
            }
            and type(self.orientation) is str
            and self.orientation
            in {
                "INCREASING_CLOCK",
                "DECLARED_FORWARD_PROCESS",
                "DECLARED_FORWARD_CARRIER",
                "ZERO_TO_ONE_PARTICIPATION",
            }
            and type(self.divisibility) is str
            and self.divisibility
            in {
                "DECLARED_NONATOMIC",
                "DECLARED_REFINABLE_IMMUTABLE_BUNDLE",
                "NOT_DIVISIBLE",
            }
            and _object_or_applicability(self.carrier_or_bundle_ref)
            and _object_or_applicability(self.clock_or_order_ref)
            and _object_or_applicability(self.path_or_process_ref)
            and _quantity_or_applicability(self.lower_bound)
            and _quantity_or_applicability(self.upper_bound)
            and type(self.interval_closure) is str
            and self.interval_closure
            in {"UNBOUNDED", "CLOSED", "LEFT_CLOSED_RIGHT_OPEN", "OPEN"}
            and _object_or_applicability(self.reversible_flow_ref)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("ExtentDefinition")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class AtomicRefinementDeclaration:
    envelope: CommonObjectEnvelope
    extent_ref: ObjectRef
    action_family_ref: ObjectRef
    base_state_ref: ObjectRef
    finite_transformation_ref: ObjectRef
    generator_ref: ObjectRef | Applicability
    epsilon_unit_ref: ObjectRef
    topology_ref: ObjectRef
    right_derivative_status: Literal["EXISTS", "DOES_NOT_EXIST", "UNRESOLVED"]
    derivative_witness_ref: ObjectRef | Applicability
    nonexistence_witness_ref: ObjectRef | Applicability
    finite_transaction_preserved: bool
    indivisible_entity_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.extent_ref,
            self.action_family_ref,
            self.base_state_ref,
            self.finite_transformation_ref,
            self.epsilon_unit_ref,
            self.topology_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_or_applicability(self.generator_ref)
            and type(self.right_derivative_status) is str
            and self.right_derivative_status
            in {"EXISTS", "DOES_NOT_EXIST", "UNRESOLVED"}
            and _object_or_applicability(self.derivative_witness_ref)
            and _object_or_applicability(self.nonexistence_witness_ref)
            and type(self.finite_transaction_preserved) is bool
            and _object_ref_tuple(self.indivisible_entity_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("AtomicRefinementDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class QuantityParticipationGeneratorDeclaration:
    envelope: CommonObjectEnvelope
    extent_ref: ObjectRef
    action_definition_ref: ObjectRef
    carrier_ref: ObjectRef
    boundary_ref: ObjectRef
    generator_contract_ref: ObjectRef
    input_quantity_refs: tuple[ObjectRef, ...]
    output_quantity_refs: tuple[ObjectRef, ...]
    value_unit_ref: ObjectRef
    value_dimension_ref: ObjectRef
    extent_unit_ref: ObjectRef
    extent_dimension_ref: ObjectRef
    generator_unit_ref: ObjectRef
    generator_dimension_ref: ObjectRef
    orientation: Literal["FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"]
    domain_ref: ObjectRef
    topology_ref: ObjectRef
    sign_convention_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.extent_ref,
            self.action_definition_ref,
            self.carrier_ref,
            self.boundary_ref,
            self.generator_contract_ref,
            self.value_unit_ref,
            self.value_dimension_ref,
            self.extent_unit_ref,
            self.extent_dimension_ref,
            self.generator_unit_ref,
            self.generator_dimension_ref,
            self.domain_ref,
            self.topology_ref,
            self.sign_convention_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.input_quantity_refs)
            and _object_ref_tuple(self.output_quantity_refs)
            and type(self.orientation) is str
            and self.orientation in {"FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"}
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("QuantityParticipationGeneratorDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class StateTransformationGeneratorDeclaration:
    envelope: CommonObjectEnvelope
    extent_ref: ObjectRef
    action_definition_ref: ObjectRef
    augmented_state_schema_ref: ObjectRef
    boundary_ref: ObjectRef
    generator_contract_ref: ObjectRef
    state_coordinate_refs: tuple[ObjectRef, ...]
    derivative_component_units: tuple[tuple[ObjectRef, ObjectRef, ObjectRef], ...]
    represented_state_role_codes: tuple[str, ...]
    inapplicable_state_role_codes: tuple[str, ...]
    state_completeness_witness_ref: ObjectRef
    extent_unit_ref: ObjectRef
    extent_dimension_ref: ObjectRef
    orientation: Literal["FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"]
    domain_ref: ObjectRef
    topology_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.extent_ref,
            self.action_definition_ref,
            self.augmented_state_schema_ref,
            self.boundary_ref,
            self.generator_contract_ref,
            self.state_completeness_witness_ref,
            self.extent_unit_ref,
            self.extent_dimension_ref,
            self.domain_ref,
            self.topology_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.state_coordinate_refs)
            and _component_unit_rows(self.derivative_component_units)
            and _string_tuple(self.represented_state_role_codes)
            and _string_tuple(self.inapplicable_state_role_codes)
            and type(self.orientation) is str
            and self.orientation in {"FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"}
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("StateTransformationGeneratorDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConstitutiveGeneratorLink:
    envelope: CommonObjectEnvelope
    quantity_generator_ref: ObjectRef
    state_generator_ref: ObjectRef
    extent_ref: ObjectRef
    boundary_ref: ObjectRef
    link_kind: Literal["INCIDENCE", "CONSTITUTIVE", "COMBINED"]
    map_contract_ref: ObjectRef
    quantity_refs: tuple[ObjectRef, ...]
    state_coordinate_refs: tuple[ObjectRef, ...]
    unit_relation_rows: tuple[
        tuple[ObjectRef, ObjectRef, ObjectRef, ObjectRef | Applicability], ...
    ]
    orientation: Literal["FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"]
    domain_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.quantity_generator_ref,
            self.state_generator_ref,
            self.extent_ref,
            self.boundary_ref,
            self.map_contract_ref,
            self.domain_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.link_kind) is str
            and self.link_kind in {"INCIDENCE", "CONSTITUTIVE", "COMBINED"}
            and _object_ref_tuple(self.quantity_refs)
            and _object_ref_tuple(self.state_coordinate_refs)
            and _unit_relation_rows(self.unit_relation_rows)
            and type(self.orientation) is str
            and self.orientation in {"FORWARD", "SEPARATELY_DECLARED_REVERSIBLE"}
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("ConstitutiveGeneratorLink")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class RegularityAndReparameterizationWitness:
    envelope: CommonObjectEnvelope
    generator_ref: ObjectRef
    source_extent_ref: ObjectRef
    target_extent_ref: ObjectRef
    reparameterization_kind: Literal[
        "POSITIVE_AFFINE",
        "POSITIVE_NONLINEAR_C1",
        "ORIENTATION_REVERSING",
        "SINGULAR_OR_NONINVERTIBLE",
        "NON_C1",
    ]
    source_coordinate_ref: ObjectRef
    target_coordinate_ref: ObjectRef
    source_unit_ref: ObjectRef
    target_unit_ref: ObjectRef
    map_ref: ObjectRef
    inverse_map_ref: ObjectRef | Applicability
    derivative_scale: CoreNumberV1 | Applicability
    regularity_codes: tuple[str, ...]
    domain_ref: ObjectRef
    topology_ref: ObjectRef
    orientation_preserved: bool
    generator_claim: Literal[
        "AUTOMATIC_UNIT_INHERITANCE",
        "EXPLICIT_CHAIN_RULE_WITNESS",
        "SEPARATE_REVERSIBLE_FLOW_REQUIRED",
        "GENERATOR_CLAIM_REFUSED",
    ]
    clock_added_to_state: bool
    transformed_generator_ref: ObjectRef | Applicability
    density_and_limits_transform_together: bool
    integrated_change_invariant: bool
    witness_ref: ObjectRef
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.generator_ref,
            self.source_extent_ref,
            self.target_extent_ref,
            self.source_coordinate_ref,
            self.target_coordinate_ref,
            self.source_unit_ref,
            self.target_unit_ref,
            self.map_ref,
            self.domain_ref,
            self.topology_ref,
            self.witness_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.reparameterization_kind) is str
            and self.reparameterization_kind
            in {
                "POSITIVE_AFFINE",
                "POSITIVE_NONLINEAR_C1",
                "ORIENTATION_REVERSING",
                "SINGULAR_OR_NONINVERTIBLE",
                "NON_C1",
            }
            and _object_or_applicability(self.inverse_map_ref)
            and _number_or_applicability(self.derivative_scale)
            and _string_tuple(self.regularity_codes)
            and type(self.orientation_preserved) is bool
            and type(self.generator_claim) is str
            and self.generator_claim
            in {
                "AUTOMATIC_UNIT_INHERITANCE",
                "EXPLICIT_CHAIN_RULE_WITNESS",
                "SEPARATE_REVERSIBLE_FLOW_REQUIRED",
                "GENERATOR_CLAIM_REFUSED",
            }
            and type(self.clock_added_to_state) is bool
            and _object_or_applicability(self.transformed_generator_ref)
            and type(self.density_and_limits_transform_together) is bool
            and type(self.integrated_change_invariant) is bool
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("RegularityAndReparameterizationWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class HybridActivationDeclaration:
    envelope: CommonObjectEnvelope
    action_definition_ref: ObjectRef
    state_generator_ref: ObjectRef
    boundary_ref: ObjectRef
    mode_schema_ref: ObjectRef
    inactive_mode_ref: ObjectRef
    active_mode_refs: tuple[ObjectRef, ...]
    quantity_coordinate_ref: ObjectRef
    off_quantity: Quantity
    minimum_active_quantity: Quantity
    maximum_active_quantity: Quantity
    activation_burden: Quantity
    activation_transition_ref: ObjectRef
    within_mode_flow_ref: ObjectRef
    jump_flow_order: Literal[
        "ACTIVATION_THEN_FLOW",
        "FLOW_THEN_DEACTIVATION",
        "ACTIVATION_FLOW_DEACTIVATION",
    ]
    fixed_cost_account_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    commitment_state_ref: ObjectRef
    fixed_cost_counted_once: bool
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.action_definition_ref,
            self.state_generator_ref,
            self.boundary_ref,
            self.mode_schema_ref,
            self.inactive_mode_ref,
            self.quantity_coordinate_ref,
            self.activation_transition_ref,
            self.within_mode_flow_ref,
            self.fixed_cost_account_ref,
            self.commitment_state_ref,
        )
        quantities = (
            self.off_quantity,
            self.minimum_active_quantity,
            self.maximum_active_quantity,
            self.activation_burden,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and _object_ref_tuple(self.active_mode_refs)
            and all(type(value) is Quantity for value in quantities)
            and type(self.jump_flow_order) is str
            and self.jump_flow_order
            in {
                "ACTIVATION_THEN_FLOW",
                "FLOW_THEN_DEACTIVATION",
                "ACTIVATION_FLOW_DEACTIVATION",
            }
            and _object_ref_tuple(self.process_account_refs)
            and type(self.fixed_cost_counted_once) is bool
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("HybridActivationDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class FiniteReconstructionWitness:
    envelope: CommonObjectEnvelope
    state_generator_ref: ObjectRef
    extent_ref: ObjectRef
    boundary_ref: ObjectRef
    initial_state_ref: ObjectRef
    finite_transformation_ref: ObjectRef
    reconstruction_kind: Literal[
        "LINEAR_SEMIGROUP",
        "NONLINEAR_FLOW",
        "ORDERED_NONAUTONOMOUS_EVOLUTION",
        "HYBRID_JUMP_FLOW",
    ]
    zero_extent_identity: bool
    domain_ref: ObjectRef
    operator_domain_ref: ObjectRef | Applicability
    regularity_witness_ref: ObjectRef
    existence_witness_ref: ObjectRef
    uniqueness_witness_ref: ObjectRef | Applicability
    ordered_evolution_ref: ObjectRef | Applicability
    hybrid_activation_ref: ObjectRef | Applicability
    finite_extent: Quantity
    expansion_form: Literal["T0_IDENTITY_AND_FIRST_ORDER_REMAINDER"]
    remainder_ref: ObjectRef
    process_account_refs: tuple[ObjectRef, ...]
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.state_generator_ref,
            self.extent_ref,
            self.boundary_ref,
            self.initial_state_ref,
            self.finite_transformation_ref,
            self.domain_ref,
            self.regularity_witness_ref,
            self.existence_witness_ref,
            self.remainder_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.reconstruction_kind) is str
            and self.reconstruction_kind
            in {
                "LINEAR_SEMIGROUP",
                "NONLINEAR_FLOW",
                "ORDERED_NONAUTONOMOUS_EVOLUTION",
                "HYBRID_JUMP_FLOW",
            }
            and type(self.zero_extent_identity) is bool
            and _object_or_applicability(self.operator_domain_ref)
            and _object_or_applicability(self.uniqueness_witness_ref)
            and _object_or_applicability(self.ordered_evolution_ref)
            and _object_or_applicability(self.hybrid_activation_ref)
            and type(self.finite_extent) is Quantity
            and type(self.expansion_form) is str
            and self.expansion_form == "T0_IDENTITY_AND_FIRST_ORDER_REMAINDER"
            and _object_ref_tuple(self.process_account_refs)
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("FiniteReconstructionWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class BoundaryHistoryEquivalenceWitness:
    envelope: CommonObjectEnvelope
    detailed_boundary_ref: ObjectRef
    parent_boundary_ref: ObjectRef
    detailed_state_schema_ref: ObjectRef
    parent_state_schema_ref: ObjectRef
    initial_state_relation_ref: ObjectRef
    admitted_history_contract_ref: ObjectRef
    horizon_ref: ObjectRef
    equivalence_kind: Literal[
        "SEMICONJUGACY", "BISIMULATION", "OTHER_PROVED_HISTORY_WITNESS"
    ]
    evolution_relation_ref: ObjectRef
    observable_codes: tuple[str, ...]
    burden_preservation_ref: ObjectRef
    conservation_preservation_ref: ObjectRef
    loss_preservation_ref: ObjectRef
    commitment_preservation_ref: ObjectRef
    settlement_preservation_ref: ObjectRef | Applicability
    process_account_preservation_refs: tuple[ObjectRef, ...]
    hidden_state_relation_preserved: bool
    all_admitted_histories_covered: bool
    snapshot_equality_only: bool
    one_state_generator_equality_only: bool
    internal_topology_export_refs: tuple[ObjectRef, ...]
    resolution: ResolutionDetail
    claim_status: ClaimStatus
    nonclaim_codes: tuple[str, ...]
    provenance_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        refs = (
            self.detailed_boundary_ref,
            self.parent_boundary_ref,
            self.detailed_state_schema_ref,
            self.parent_state_schema_ref,
            self.initial_state_relation_ref,
            self.admitted_history_contract_ref,
            self.horizon_ref,
            self.evolution_relation_ref,
            self.burden_preservation_ref,
            self.conservation_preservation_ref,
            self.loss_preservation_ref,
            self.commitment_preservation_ref,
        )
        booleans = (
            self.hidden_state_relation_preserved,
            self.all_admitted_histories_covered,
            self.snapshot_equality_only,
            self.one_state_generator_equality_only,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in refs)
            and type(self.equivalence_kind) is str
            and self.equivalence_kind
            in {"SEMICONJUGACY", "BISIMULATION", "OTHER_PROVED_HISTORY_WITNESS"}
            and _string_tuple(self.observable_codes)
            and _object_or_applicability(self.settlement_preservation_ref)
            and _object_ref_tuple(self.process_account_preservation_refs)
            and all(type(value) is bool for value in booleans)
            and _object_ref_tuple(self.internal_topology_export_refs)
            and type(self.resolution) is ResolutionDetail
            and type(self.claim_status) is ClaimStatus
            and _string_tuple(self.nonclaim_codes)
            and _object_ref_tuple(self.provenance_refs)
        ):
            _formation_failure("BoundaryHistoryEquivalenceWitness")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


_OBJECT_SURFACE = {
    ExtentDefinition: (
        "ebu:object-kind:atomic-interaction:extent-definition",
        "ebu:schema:atomic-interaction:extent-definition-v1",
    ),
    AtomicRefinementDeclaration: (
        "ebu:object-kind:atomic-interaction:atomic-refinement-declaration",
        "ebu:schema:atomic-interaction:atomic-refinement-declaration-v1",
    ),
    QuantityParticipationGeneratorDeclaration: (
        "ebu:object-kind:atomic-interaction:quantity-participation-generator-declaration",
        "ebu:schema:atomic-interaction:quantity-participation-generator-declaration-v1",
    ),
    StateTransformationGeneratorDeclaration: (
        "ebu:object-kind:atomic-interaction:state-transformation-generator-declaration",
        "ebu:schema:atomic-interaction:state-transformation-generator-declaration-v1",
    ),
    ConstitutiveGeneratorLink: (
        "ebu:object-kind:atomic-interaction:constitutive-generator-link",
        "ebu:schema:atomic-interaction:constitutive-generator-link-v1",
    ),
    RegularityAndReparameterizationWitness: (
        "ebu:object-kind:atomic-interaction:regularity-and-reparameterization-witness",
        "ebu:schema:atomic-interaction:regularity-and-reparameterization-witness-v1",
    ),
    HybridActivationDeclaration: (
        "ebu:object-kind:atomic-interaction:hybrid-activation-declaration",
        "ebu:schema:atomic-interaction:hybrid-activation-declaration-v1",
    ),
    FiniteReconstructionWitness: (
        "ebu:object-kind:atomic-interaction:finite-reconstruction-witness",
        "ebu:schema:atomic-interaction:finite-reconstruction-witness-v1",
    ),
    BoundaryHistoryEquivalenceWitness: (
        "ebu:object-kind:atomic-interaction:boundary-history-equivalence-witness",
        "ebu:schema:atomic-interaction:boundary-history-equivalence-witness-v1",
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


def _collection_specs(record: object) -> tuple[tuple[tuple[object, ...], str], ...]:
    common = (
        (record.nonclaim_codes, "nonclaim"),  # type: ignore[attr-defined]
        (record.provenance_refs, "ref"),  # type: ignore[attr-defined]
    )
    if type(record) is ExtentDefinition:
        return common
    if type(record) is AtomicRefinementDeclaration:
        return ((record.indivisible_entity_refs, "ref"),) + common
    if type(record) is QuantityParticipationGeneratorDeclaration:
        return (
            (record.input_quantity_refs, "ref"),
            (record.output_quantity_refs, "ref"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is StateTransformationGeneratorDeclaration:
        return (
            (record.state_coordinate_refs, "ref"),
            (record.derivative_component_units, "ref_row"),
            (record.represented_state_role_codes, "state_role"),
            (record.inapplicable_state_role_codes, "state_role"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is ConstitutiveGeneratorLink:
        return (
            (record.quantity_refs, "ref"),
            (record.state_coordinate_refs, "ref"),
            (record.unit_relation_rows, "ref_row"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is RegularityAndReparameterizationWitness:
        return ((record.regularity_codes, "regularity"),) + common
    if type(record) is HybridActivationDeclaration:
        return (
            (record.active_mode_refs, "ref"),
            (record.process_account_refs, "ref"),
        ) + common
    if type(record) is FiniteReconstructionWitness:
        return ((record.process_account_refs, "ref"),) + common
    if type(record) is BoundaryHistoryEquivalenceWitness:
        return (
            (record.observable_codes, "observable"),
            (record.process_account_preservation_refs, "ref"),
            (record.internal_topology_export_refs, "ref"),
            (record.resolution.completed_part_refs, "ref"),
            (record.resolution.missing_part_refs, "ref"),
        ) + common
    return ()


def _collection_key(value: object, kind: str) -> object:
    if kind == "ref":
        return _ref_key(value)  # type: ignore[arg-type]
    if kind == "ref_row":
        return _ref_key(value[0])  # type: ignore[index]
    domains = {
        "state_role": _STATE_ROLE_CODES,
        "observable": _BOUNDARY_OBSERVABLE_CODES,
        "regularity": _REGULARITY_CODES,
        "nonclaim": _NONCLAIM_CODES,
    }
    domain = domains[kind]
    try:
        return (0, domain.index(value))  # type: ignore[arg-type]
    except ValueError:
        return (1, value)


def _collections_ordered(records: tuple[object, ...]) -> bool:
    for record in records:
        for values, kind in _collection_specs(record):
            keys = tuple(_collection_key(value, kind) for value in values)
            if keys != tuple(sorted(keys)):
                return False
    return True


def _collections_duplicated(records: tuple[object, ...]) -> bool:
    for record in records:
        for values, kind in _collection_specs(record):
            keys = tuple(_collection_key(value, kind) for value in values)
            if len(keys) != len(set(keys)):
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


def _quantity_units_match(quantities: tuple[Quantity, ...]) -> bool:
    first = quantities[0]
    return all(quantity.unit_ref == first.unit_ref for quantity in quantities[1:])


def _quantity_dimensions_match(quantities: tuple[Quantity, ...]) -> bool:
    first = quantities[0]
    return all(
        quantity.dimension_ref == first.dimension_ref for quantity in quantities[1:]
    )


def _extent_unit_mismatch(record: ExtentDefinition) -> bool:
    bounds = tuple(
        value
        for value in (record.lower_bound, record.upper_bound)
        if type(value) is Quantity
    )
    return any(bound.unit_ref != record.coordinate_unit_ref for bound in bounds)


def _extent_dimension_mismatch(record: ExtentDefinition) -> bool:
    bounds = tuple(
        value
        for value in (record.lower_bound, record.upper_bound)
        if type(value) is Quantity
    )
    return any(bound.dimension_ref != record.coordinate_dimension_ref for bound in bounds)


def _extent_invalid(record: ExtentDefinition) -> bool:
    if _surface_invalid(record) or _claims_invalid(
        record,
        (ClaimStatus.DEFINITION,),
        ("NO_EMPIRICAL_VALIDATION", "NO_UNIVERSAL_DIVISIBILITY", "NO_RUNTIME_BEHAVIOR"),
    ):
        return True
    arms = {
        "PHYSICAL_TIME": (
            "INCREASING_CLOCK",
            type(record.clock_or_order_ref) is ObjectRef,
            record.carrier_or_bundle_ref is Applicability.NOT_APPLICABLE,
            record.path_or_process_ref is Applicability.NOT_APPLICABLE,
        ),
        "PROCESS_OR_ROUTE_EXTENT": (
            "DECLARED_FORWARD_PROCESS",
            record.clock_or_order_ref is Applicability.NOT_APPLICABLE,
            record.carrier_or_bundle_ref is Applicability.NOT_APPLICABLE,
            type(record.path_or_process_ref) is ObjectRef,
        ),
        "TYPED_CARRIER_QUANTITY": (
            "DECLARED_FORWARD_CARRIER",
            record.clock_or_order_ref is Applicability.NOT_APPLICABLE,
            type(record.carrier_or_bundle_ref) is ObjectRef,
            record.path_or_process_ref is Applicability.NOT_APPLICABLE,
        ),
        "DIMENSIONLESS_PARTICIPATION": (
            "ZERO_TO_ONE_PARTICIPATION",
            record.clock_or_order_ref is Applicability.NOT_APPLICABLE,
            record.carrier_or_bundle_ref is Applicability.NOT_APPLICABLE,
            record.path_or_process_ref is Applicability.NOT_APPLICABLE,
        ),
    }
    expected_orientation, *applicability = arms[record.extent_family]
    if record.orientation != expected_orientation or not all(applicability):
        return True
    if record.interval_closure == "UNBOUNDED":
        if not (
            record.lower_bound is Applicability.NOT_APPLICABLE
            and record.upper_bound is Applicability.NOT_APPLICABLE
        ):
            return True
    elif not (
        type(record.lower_bound) is Quantity and type(record.upper_bound) is Quantity
    ):
        return True
    if type(record.lower_bound) is Quantity and type(record.upper_bound) is Quantity:
        if _number_fraction(record.lower_bound.magnitude) > _number_fraction(
            record.upper_bound.magnitude
        ):
            return True
    if record.extent_family == "DIMENSIONLESS_PARTICIPATION":
        if not (
            type(record.lower_bound) is Quantity
            and type(record.upper_bound) is Quantity
            and _number_fraction(record.lower_bound.magnitude) == 0
            and _number_fraction(record.upper_bound.magnitude) == 1
        ):
            return True
    return False


def _extent_divisibility_invalid(record: ExtentDefinition) -> bool:
    return (
        record.divisibility == "DECLARED_REFINABLE_IMMUTABLE_BUNDLE"
        and record.carrier_or_bundle_ref is Applicability.NOT_APPLICABLE
    )


def _refinement_invalid(
    record: AtomicRefinementDeclaration, extent: ExtentDefinition
) -> bool:
    if _surface_invalid(record) or _claims_invalid(
        record,
        (ClaimStatus.DEFINITION, ClaimStatus.MODEL_DEPENDENT_RESULT),
        ("NO_EMPIRICAL_VALIDATION", "NO_MINIMAL_TRANSACTION", "NO_RUNTIME_BEHAVIOR"),
    ):
        return True
    if not (
        record.extent_ref == _record_ref(extent)
        and record.action_family_ref == extent.action_family_ref
        and record.epsilon_unit_ref == extent.coordinate_unit_ref
        and record.topology_ref == extent.topology_ref
        and record.finite_transaction_preserved
    ):
        return True
    if record.right_derivative_status == "EXISTS":
        return not (
            type(record.generator_ref) is ObjectRef
            and type(record.derivative_witness_ref) is ObjectRef
            and record.nonexistence_witness_ref is Applicability.NOT_APPLICABLE
            and extent.divisibility != "NOT_DIVISIBLE"
        )
    if record.right_derivative_status == "DOES_NOT_EXIST":
        return not (
            record.generator_ref is Applicability.NOT_APPLICABLE
            and record.derivative_witness_ref is Applicability.NOT_APPLICABLE
            and type(record.nonexistence_witness_ref) is ObjectRef
        )
    return not (
        record.generator_ref is Applicability.NOT_APPLICABLE
        and record.derivative_witness_ref is Applicability.NOT_APPLICABLE
        and record.nonexistence_witness_ref is Applicability.NOT_APPLICABLE
    )


def _generator_orientation_valid(orientation: str, extent: ExtentDefinition) -> bool:
    return orientation == "FORWARD" or (
        orientation == "SEPARATELY_DECLARED_REVERSIBLE"
        and type(extent.reversible_flow_ref) is ObjectRef
    )


def _quantity_generator_invalid(
    record: QuantityParticipationGeneratorDeclaration, extent: ExtentDefinition
) -> bool:
    carrier_matches = (
        type(extent.carrier_or_bundle_ref) is not ObjectRef
        or record.carrier_ref == extent.carrier_or_bundle_ref
    )
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.DEFINITION, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.extent_ref != _record_ref(extent)
        or not carrier_matches
        or record.domain_ref != extent.domain_ref
        or record.topology_ref != extent.topology_ref
        or not _generator_orientation_valid(record.orientation, extent)
        or not (record.input_quantity_refs or record.output_quantity_refs)
    )


def _state_generator_invalid(
    record: StateTransformationGeneratorDeclaration, extent: ExtentDefinition
) -> bool:
    component_coordinates = tuple(row[0] for row in record.derivative_component_units)
    return (
        _surface_invalid(record)
        or record.extent_ref != _record_ref(extent)
        or record.domain_ref != extent.domain_ref
        or record.topology_ref != extent.topology_ref
        or not _generator_orientation_valid(record.orientation, extent)
        or not record.state_coordinate_refs
        or component_coordinates != record.state_coordinate_refs
    )


def _augmented_state_incomplete(
    record: StateTransformationGeneratorDeclaration,
) -> bool:
    represented = set(record.represented_state_role_codes)
    inapplicable = set(record.inapplicable_state_role_codes)
    return (
        _claims_invalid(
            record,
            (ClaimStatus.DEFINITION, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_UNIVERSAL_MINIMAL_STATE",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or bool(represented & inapplicable)
        or represented | inapplicable != set(_STATE_ROLE_CODES)
    )


def _link_unit_mismatch(
    record: ConstitutiveGeneratorLink,
    quantity_generator: QuantityParticipationGeneratorDeclaration,
    state_generator: StateTransformationGeneratorDeclaration,
) -> bool:
    component_units = {
        row[0]: row[1] for row in state_generator.derivative_component_units
    }
    return quantity_generator.extent_unit_ref != state_generator.extent_unit_ref or any(
        row[1] not in component_units or component_units[row[1]] != row[2]
        for row in record.unit_relation_rows
    )


def _link_invalid(
    record: ConstitutiveGeneratorLink,
    quantity_generator: QuantityParticipationGeneratorDeclaration,
    state_generator: StateTransformationGeneratorDeclaration,
) -> bool:
    expected_quantities = tuple(
        sorted(
            set(
                quantity_generator.input_quantity_refs
                + quantity_generator.output_quantity_refs
            ),
            key=_ref_key,
        )
    )
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.DEFINITION,),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_CAUSAL_IDENTIFICATION",
                "NO_INSTITUTIONAL_ENDORSEMENT",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.quantity_generator_ref != _record_ref(quantity_generator)
        or record.state_generator_ref != _record_ref(state_generator)
        or record.extent_ref != quantity_generator.extent_ref
        or record.extent_ref != state_generator.extent_ref
        or record.boundary_ref != quantity_generator.boundary_ref
        or record.boundary_ref != state_generator.boundary_ref
        or record.orientation != quantity_generator.orientation
        or record.orientation != state_generator.orientation
        or record.domain_ref != quantity_generator.domain_ref
        or record.domain_ref != state_generator.domain_ref
        or record.quantity_refs != expected_quantities
        or record.state_coordinate_refs != state_generator.state_coordinate_refs
        or tuple(row[0] for row in record.unit_relation_rows) != record.quantity_refs
        or record.process_account_refs != quantity_generator.process_account_refs
        or record.process_account_refs != state_generator.process_account_refs
    )


def _reparameterization_invalid(
    record: RegularityAndReparameterizationWitness,
    source_extent: ExtentDefinition,
    target_extent: ExtentDefinition,
    generator: QuantityParticipationGeneratorDeclaration
    | StateTransformationGeneratorDeclaration,
) -> bool:
    if (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            ("NO_EMPIRICAL_VALIDATION", "NO_RUNTIME_BEHAVIOR", "NO_PHYSICAL_PROPAGATION"),
        )
        or record.generator_ref != _record_ref(generator)
        or record.source_extent_ref != _record_ref(source_extent)
        or record.target_extent_ref != _record_ref(target_extent)
        or generator.extent_ref != _record_ref(source_extent)
        or record.source_coordinate_ref != source_extent.coordinate_ref
        or record.target_coordinate_ref != target_extent.coordinate_ref
        or record.domain_ref != source_extent.domain_ref
        or record.domain_ref != target_extent.domain_ref
        or record.topology_ref != source_extent.topology_ref
        or record.topology_ref != target_extent.topology_ref
        or source_extent.coordinate_dimension_ref
        != target_extent.coordinate_dimension_ref
        or any(code not in _REGULARITY_CODES for code in record.regularity_codes)
        or record.clock_added_to_state
    ):
        return True
    positive = record.reparameterization_kind in {
        "POSITIVE_AFFINE",
        "POSITIVE_NONLINEAR_C1",
    }
    if positive:
        if not (
            record.orientation_preserved
            and type(record.inverse_map_ref) is ObjectRef
            and type(record.derivative_scale) in _CORE_NUMBER_TYPES
            and _number_fraction(record.derivative_scale) > 0
            and type(record.transformed_generator_ref) is ObjectRef
            and record.density_and_limits_transform_together
            and record.integrated_change_invariant
        ):
            return True
        if record.reparameterization_kind == "POSITIVE_AFFINE":
            return record.generator_claim not in {
                "AUTOMATIC_UNIT_INHERITANCE",
                "EXPLICIT_CHAIN_RULE_WITNESS",
            }
        return (
            "C1" not in record.regularity_codes
            or record.generator_claim != "EXPLICIT_CHAIN_RULE_WITNESS"
        )
    if record.reparameterization_kind == "ORIENTATION_REVERSING":
        return (
            record.orientation_preserved
            or record.generator_claim
            not in {
                "SEPARATE_REVERSIBLE_FLOW_REQUIRED",
                "GENERATOR_CLAIM_REFUSED",
            }
            or (
                record.generator_claim == "SEPARATE_REVERSIBLE_FLOW_REQUIRED"
                and not (
                    type(source_extent.reversible_flow_ref) is ObjectRef
                    and type(target_extent.reversible_flow_ref) is ObjectRef
                )
            )
        )
    return not (
        record.generator_claim == "GENERATOR_CLAIM_REFUSED"
        and record.transformed_generator_ref is Applicability.NOT_APPLICABLE
    )


def _hybrid_invalid(
    record: HybridActivationDeclaration,
    state_generator: StateTransformationGeneratorDeclaration,
) -> bool:
    quantities = (
        record.off_quantity,
        record.minimum_active_quantity,
        record.maximum_active_quantity,
        record.activation_burden,
    )
    represented_roles = set(state_generator.represented_state_role_codes)
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.DEFINITION, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.state_generator_ref != _record_ref(state_generator)
        or record.action_definition_ref != state_generator.action_definition_ref
        or record.boundary_ref != state_generator.boundary_ref
        or any(quantity.boundary_ref != record.boundary_ref for quantity in quantities)
        or not record.active_mode_refs
        or record.inactive_mode_ref in record.active_mode_refs
        or not {"MODE", "COMMITMENT"}.issubset(represented_roles)
        or _number_fraction(record.off_quantity.magnitude) != 0
        or _number_fraction(record.minimum_active_quantity.magnitude) <= 0
        or _number_fraction(record.maximum_active_quantity.magnitude)
        < _number_fraction(record.minimum_active_quantity.magnitude)
        or _number_fraction(record.activation_burden.magnitude) < 0
        or not record.fixed_cost_counted_once
    )


def _reconstruction_invalid(
    record: FiniteReconstructionWitness,
    state_generator: StateTransformationGeneratorDeclaration,
    hybrid: HybridActivationDeclaration | Applicability,
) -> bool:
    if (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            ("NO_EMPIRICAL_VALIDATION", "NO_RUNTIME_BEHAVIOR", "NO_PHYSICAL_PROPAGATION"),
        )
        or record.state_generator_ref != _record_ref(state_generator)
        or record.extent_ref != state_generator.extent_ref
        or record.boundary_ref != state_generator.boundary_ref
        or record.domain_ref != state_generator.domain_ref
        or record.finite_extent.dimension_ref != state_generator.extent_dimension_ref
        or record.finite_extent.boundary_ref != record.boundary_ref
        or _number_fraction(record.finite_extent.magnitude) < 0
        or not record.zero_extent_identity
    ):
        return True
    if record.reconstruction_kind == "LINEAR_SEMIGROUP":
        return not (
            type(record.operator_domain_ref) is ObjectRef
            and record.ordered_evolution_ref is Applicability.NOT_APPLICABLE
            and record.hybrid_activation_ref is Applicability.NOT_APPLICABLE
            and hybrid is Applicability.NOT_APPLICABLE
        )
    if record.reconstruction_kind == "NONLINEAR_FLOW":
        return not (
            record.ordered_evolution_ref is Applicability.NOT_APPLICABLE
            and record.hybrid_activation_ref is Applicability.NOT_APPLICABLE
            and hybrid is Applicability.NOT_APPLICABLE
        )
    if record.reconstruction_kind == "ORDERED_NONAUTONOMOUS_EVOLUTION":
        return not (
            type(record.ordered_evolution_ref) is ObjectRef
            and record.hybrid_activation_ref is Applicability.NOT_APPLICABLE
            and hybrid is Applicability.NOT_APPLICABLE
        )
    return not (
        type(record.hybrid_activation_ref) is ObjectRef
        and type(hybrid) is HybridActivationDeclaration
        and record.hybrid_activation_ref == _record_ref(hybrid)
    )


def _history_equivalence_invalid(
    record: BoundaryHistoryEquivalenceWitness,
) -> bool:
    return (
        _surface_invalid(record)
        or _claims_invalid(
            record,
            (ClaimStatus.THEOREM, ClaimStatus.MODEL_DEPENDENT_RESULT),
            (
                "NO_EMPIRICAL_VALIDATION",
                "NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED",
                "NO_RUNTIME_BEHAVIOR",
            ),
        )
        or record.detailed_boundary_ref == record.parent_boundary_ref
        or any(code not in _BOUNDARY_OBSERVABLE_CODES for code in record.observable_codes)
        or not record.all_admitted_histories_covered
        or record.snapshot_equality_only
        or record.one_state_generator_equality_only
        or record.resolution.state
        in {ResolutionState.FAILED, ResolutionState.UNRESOLVED, ResolutionState.OUT_OF_BOUNDARY}
    )


def _boundary_account_incomplete(
    record: BoundaryHistoryEquivalenceWitness,
) -> bool:
    required_refs = {
        record.burden_preservation_ref,
        record.conservation_preservation_ref,
        record.loss_preservation_ref,
        record.commitment_preservation_ref,
        *record.process_account_preservation_refs,
        *record.internal_topology_export_refs,
    }
    if type(record.settlement_preservation_ref) is ObjectRef:
        required_refs.add(record.settlement_preservation_ref)
    missing = set(record.resolution.missing_part_refs)
    return (
        not record.hidden_state_relation_preserved
        or not record.process_account_preservation_refs
        or bool(required_refs & missing)
        or (
            type(record.settlement_preservation_ref) is ObjectRef
            and "SETTLEMENT_VISIBLE_RECORD" not in record.observable_codes
        )
    )


def _check_common_prefix(
    interface: str,
    records: tuple[object, ...],
    implicit_values: tuple[object, ...],
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
    if not _collections_ordered(records):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if _collections_duplicated(records):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)


def _check_common_suffix(interface: str, records: tuple[object, ...]) -> None:
    if _forbidden_runtime_behavior(records):
        _failure(FailureCode.FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR, interface)
    if any(not _object_hash_matches(record) for record in records):
        _failure(FailureCode.HASH_MISMATCH, interface)


def validate_extent_definition(record: ExtentDefinition, /) -> None:
    if type(record) is not ExtentDefinition:
        _formation_failure("ExtentDefinition")
    interface = "validate_extent_definition"
    records = (record,)
    _check_common_prefix(
        interface,
        records,
        (
            record.carrier_or_bundle_ref,
            record.clock_or_order_ref,
            record.path_or_process_ref,
            record.lower_bound,
            record.upper_bound,
            record.reversible_flow_ref,
        ),
    )
    if _extent_unit_mismatch(record):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _extent_dimension_mismatch(record):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _extent_invalid(record):
        _failure(FailureCode.EXTENT_DECLARATION_INVALID, interface)
    if _extent_divisibility_invalid(record):
        _failure(FailureCode.EXTENT_DIVISIBILITY_UNDECLARED, interface)
    _check_common_suffix(interface, records)
    return None


def validate_atomic_refinement(
    record: AtomicRefinementDeclaration, extent: ExtentDefinition, /
) -> None:
    if type(record) is not AtomicRefinementDeclaration:
        _formation_failure("AtomicRefinementDeclaration")
    if type(extent) is not ExtentDefinition:
        _formation_failure("ExtentDefinition")
    interface = "validate_atomic_refinement"
    records = (record, extent)
    _check_common_prefix(
        interface,
        records,
        (
            record.generator_ref,
            record.derivative_witness_ref,
            record.nonexistence_witness_ref,
        ),
    )
    if record.epsilon_unit_ref != extent.coordinate_unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _refinement_invalid(record, extent):
        _failure(FailureCode.ATOMIC_REFINEMENT_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_quantity_participation_generator(
    record: QuantityParticipationGeneratorDeclaration,
    extent: ExtentDefinition,
    /,
) -> None:
    if type(record) is not QuantityParticipationGeneratorDeclaration:
        _formation_failure("QuantityParticipationGeneratorDeclaration")
    if type(extent) is not ExtentDefinition:
        _formation_failure("ExtentDefinition")
    interface = "validate_quantity_participation_generator"
    records = (record, extent)
    _check_common_prefix(interface, records, ())
    if record.extent_unit_ref != extent.coordinate_unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if record.extent_dimension_ref != extent.coordinate_dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _quantity_generator_invalid(record, extent):
        _failure(FailureCode.GENERATOR_DECLARATION_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_state_transformation_generator(
    record: StateTransformationGeneratorDeclaration,
    extent: ExtentDefinition,
    /,
) -> None:
    if type(record) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    if type(extent) is not ExtentDefinition:
        _formation_failure("ExtentDefinition")
    interface = "validate_state_transformation_generator"
    records = (record, extent)
    _check_common_prefix(interface, records, ())
    if record.extent_unit_ref != extent.coordinate_unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if record.extent_dimension_ref != extent.coordinate_dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _state_generator_invalid(record, extent):
        _failure(FailureCode.GENERATOR_DECLARATION_INVALID, interface)
    if _augmented_state_incomplete(record):
        _failure(FailureCode.AUGMENTED_STATE_INCOMPLETE, interface)
    _check_common_suffix(interface, records)
    return None


def validate_constitutive_generator_link(
    record: ConstitutiveGeneratorLink,
    quantity_generator: QuantityParticipationGeneratorDeclaration,
    state_generator: StateTransformationGeneratorDeclaration,
    /,
) -> None:
    if type(record) is not ConstitutiveGeneratorLink:
        _formation_failure("ConstitutiveGeneratorLink")
    if type(quantity_generator) is not QuantityParticipationGeneratorDeclaration:
        _formation_failure("QuantityParticipationGeneratorDeclaration")
    if type(state_generator) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    interface = "validate_constitutive_generator_link"
    records = (record, quantity_generator, state_generator)
    _check_common_prefix(
        interface, records, tuple(row[3] for row in record.unit_relation_rows)
    )
    if _link_unit_mismatch(record, quantity_generator, state_generator):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if quantity_generator.extent_dimension_ref != state_generator.extent_dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _link_invalid(record, quantity_generator, state_generator):
        _failure(FailureCode.GENERATOR_LINK_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_regularity_and_reparameterization_witness(
    record: RegularityAndReparameterizationWitness,
    source_extent: ExtentDefinition,
    target_extent: ExtentDefinition,
    generator: QuantityParticipationGeneratorDeclaration
    | StateTransformationGeneratorDeclaration,
    /,
) -> None:
    if type(record) is not RegularityAndReparameterizationWitness:
        _formation_failure("RegularityAndReparameterizationWitness")
    if type(source_extent) is not ExtentDefinition or type(target_extent) is not ExtentDefinition:
        _formation_failure("ExtentDefinition")
    if type(generator) not in {
        QuantityParticipationGeneratorDeclaration,
        StateTransformationGeneratorDeclaration,
    }:
        _formation_failure("QuantityParticipationGeneratorDeclaration|StateTransformationGeneratorDeclaration")
    interface = "validate_regularity_and_reparameterization_witness"
    records = (record, source_extent, target_extent, generator)
    _check_common_prefix(
        interface,
        records,
        (
            record.inverse_map_ref,
            record.derivative_scale,
            record.transformed_generator_ref,
        ),
    )
    if (
        record.source_unit_ref != source_extent.coordinate_unit_ref
        or record.target_unit_ref != target_extent.coordinate_unit_ref
    ):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _reparameterization_invalid(
        record, source_extent, target_extent, generator
    ):
        _failure(FailureCode.REPARAMETERIZATION_WITNESS_INVALID, interface)
    _check_common_suffix(interface, records)
    return None


def validate_hybrid_activation(
    record: HybridActivationDeclaration,
    state_generator: StateTransformationGeneratorDeclaration,
    /,
) -> None:
    if type(record) is not HybridActivationDeclaration:
        _formation_failure("HybridActivationDeclaration")
    if type(state_generator) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    interface = "validate_hybrid_activation"
    records = (record, state_generator)
    _check_common_prefix(interface, records, ())
    quantities = (
        record.off_quantity,
        record.minimum_active_quantity,
        record.maximum_active_quantity,
        record.activation_burden,
    )
    if not _quantity_units_match(quantities):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if not _quantity_dimensions_match(quantities):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if _hybrid_invalid(record, state_generator):
        _failure(FailureCode.HYBRID_ACTIVATION_INVALID, interface)
    if record.fixed_cost_account_ref in record.process_account_refs:
        _failure(FailureCode.FIXED_ACTIVATION_ACCOUNT_DUPLICATED, interface)
    _check_common_suffix(interface, records)
    return None


def validate_finite_reconstruction(
    record: FiniteReconstructionWitness,
    state_generator: StateTransformationGeneratorDeclaration,
    hybrid: HybridActivationDeclaration | Applicability,
    /,
) -> None:
    if type(record) is not FiniteReconstructionWitness:
        _formation_failure("FiniteReconstructionWitness")
    if type(state_generator) is not StateTransformationGeneratorDeclaration:
        _formation_failure("StateTransformationGeneratorDeclaration")
    if type(hybrid) is not HybridActivationDeclaration and type(hybrid) is not Applicability:
        _formation_failure("HybridActivationDeclaration|Applicability")
    interface = "validate_finite_reconstruction"
    records = (
        (record, state_generator, hybrid)
        if type(hybrid) is HybridActivationDeclaration
        else (record, state_generator)
    )
    _check_common_prefix(
        interface,
        records,
        (
            record.operator_domain_ref,
            record.uniqueness_witness_ref,
            record.ordered_evolution_ref,
            record.hybrid_activation_ref,
            hybrid,
        ),
    )
    if record.finite_extent.unit_ref != state_generator.extent_unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if _reconstruction_invalid(record, state_generator, hybrid):
        _failure(FailureCode.RECONSTRUCTION_CLAIM_UNSUPPORTED, interface)
    _check_common_suffix(interface, records)
    return None


def validate_boundary_history_equivalence(
    record: BoundaryHistoryEquivalenceWitness, /
) -> None:
    if type(record) is not BoundaryHistoryEquivalenceWitness:
        _formation_failure("BoundaryHistoryEquivalenceWitness")
    interface = "validate_boundary_history_equivalence"
    records = (record,)
    _check_common_prefix(interface, records, (record.settlement_preservation_ref,))
    if _history_equivalence_invalid(record):
        _failure(FailureCode.BOUNDARY_HISTORY_EQUIVALENCE_INVALID, interface)
    if _boundary_account_incomplete(record):
        _failure(FailureCode.BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE, interface)
    _check_common_suffix(interface, records)
    return None


__all__ = (
    "ExtentDefinition",
    "AtomicRefinementDeclaration",
    "QuantityParticipationGeneratorDeclaration",
    "StateTransformationGeneratorDeclaration",
    "ConstitutiveGeneratorLink",
    "RegularityAndReparameterizationWitness",
    "HybridActivationDeclaration",
    "FiniteReconstructionWitness",
    "BoundaryHistoryEquivalenceWitness",
    "validate_extent_definition",
    "validate_atomic_refinement",
    "validate_quantity_participation_generator",
    "validate_state_transformation_generator",
    "validate_constitutive_generator_link",
    "validate_regularity_and_reparameterization_witness",
    "validate_hybrid_activation",
    "validate_finite_reconstruction",
    "validate_boundary_history_equivalence",
)
