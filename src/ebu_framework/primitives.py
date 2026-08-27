"""Immutable I-2 scientific primitives and argument-only compatibility checks."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
import unicodedata

from .envelopes import CompatibilityResult
from .errors import (
    Applicability,
    FailureCode,
    FailureEnvelope,
    FailureInterfaceRef,
    FailureStage,
    _fail,
)
from .identity import ObjectRef
from .numeric import (
    Binary64BitsV1,
    CoreNumberV1,
    DecimalV1,
    ExactConversion,
    IntegerV1,
    NumericalOperation,
    QuantityContext,
    RationalV1,
    apply_exact_core_operation,
)


CompatibilityResult.__module__ = __name__


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.primitives", name, "1.0.0")


def _failure(code: FailureCode, interface: str, summary: str) -> "NoReturn":
    _fail(
        code,
        summary,
        stage=FailureStage.I2,
        interface_ref=_interface(interface),
    )


from typing import NoReturn  # noqa: E402


def _conditional(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_unique_refs(values: tuple[ObjectRef, ...], *, nonempty: bool = False) -> bool:
    if type(values) is not tuple or not all(type(item) is ObjectRef for item in values):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return (not nonempty or bool(values)) and keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    if type(value) is tuple:
        return [_project(item) for item in value]
    return value


def _success(
    labels: tuple[str, ...],
    *,
    conversion: ObjectRef | Applicability = Applicability.NOT_APPLICABLE,
    parent: ObjectRef | Applicability = Applicability.NOT_APPLICABLE,
) -> CompatibilityResult:
    return CompatibilityResult(
        True,
        labels,
        conversion,
        parent,
        Applicability.NOT_APPLICABLE,
    )


def _core_type(value: object) -> bool:
    return type(value) in (IntegerV1, RationalV1, DecimalV1, Binary64BitsV1)


def _same_core_compare(left: CoreNumberV1, right: CoreNumberV1) -> int:
    if type(left) is not type(right) or type(left) is Binary64BitsV1:
        raise TypeError("comparison is not available for these exact core values")
    if type(left) is IntegerV1:
        a, b = left.value, right.value
    elif type(left) is RationalV1:
        a = left.numerator.value * right.denominator.value
        b = right.numerator.value * left.denominator.value
    else:
        exponent = min(left.exponent10.value, right.exponent10.value)
        a = left.coefficient.value * 10 ** (left.exponent10.value - exponent)
        b = right.coefficient.value * 10 ** (right.exponent10.value - exponent)
    return (a > b) - (a < b)


class ClaimStatus(StrEnum):
    DEFINITION = "DEFINITION"
    ALGEBRAIC_IDENTITY = "ALGEBRAIC_IDENTITY"
    THEOREM = "THEOREM"
    MODEL_DEPENDENT_RESULT = "MODEL_DEPENDENT_RESULT"
    TESTED_IMPLEMENTATION_PROPERTY = "TESTED_IMPLEMENTATION_PROPERTY"
    OBSERVED_REGISTERED_RESULT = "OBSERVED_REGISTERED_RESULT"
    RESEARCH_HYPOTHESIS = "RESEARCH_HYPOTHESIS"
    INSTITUTIONAL_DESIGN_CHOICE = "INSTITUTIONAL_DESIGN_CHOICE"
    ANALOGY = "ANALOGY"
    OPEN_PROBLEM = "OPEN_PROBLEM"


class ResolutionState(StrEnum):
    PRESENT = "PRESENT"
    PENDING = "PENDING"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"
    OUT_OF_BOUNDARY = "OUT_OF_BOUNDARY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class UncertaintyKind(StrEnum):
    EXACT = "EXACT"
    MEASUREMENT_INTERVAL = "MEASUREMENT_INTERVAL"
    ADMISSIBLE_SET = "ADMISSIBLE_SET"
    ADVERSARIAL_SET = "ADVERSARIAL_SET"
    PROBABILITY_MODEL = "PROBABILITY_MODEL"
    MODEL_DISCREPANCY = "MODEL_DISCREPANCY"
    UNKNOWN = "UNKNOWN"
    OUT_OF_SET = "OUT_OF_SET"


@dataclass(frozen=True, slots=True)
class Dimension:
    dimension_ref: ObjectRef
    dimension_kind: str
    basis_exponents: tuple[tuple[ObjectRef, RationalV1], ...]

    def __post_init__(self) -> None:
        if type(self.dimension_ref) is not ObjectRef or type(self.dimension_kind) is not str or self.dimension_kind not in {"PHYSICAL", "DECLARED_INSTITUTIONAL"}:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Dimension", "dimension identity or kind is invalid")
        if type(self.basis_exponents) is not tuple or not self.basis_exponents or not all(
            type(pair) is tuple and len(pair) == 2 and type(pair[0]) is ObjectRef and type(pair[1]) is RationalV1
            for pair in self.basis_exponents
        ):
            _failure(FailureCode.CORE_NUMBER_INVALID, "Dimension", "basis exponents require exact nonempty pairs")
        refs = tuple(_ref_key(pair[0]) for pair in self.basis_exponents)
        if refs != tuple(sorted(refs)) or len(refs) != len(set(refs)) or any(pair[1].numerator.value == 0 for pair in self.basis_exponents):
            _failure(FailureCode.DIMENSION_MISMATCH, "Dimension", "basis exponents must be ordered, unique, and nonzero")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "basis_exponents": [[ref.to_ecj1(), exponent.to_ecj1()] for ref, exponent in self.basis_exponents],
            "dimension_kind": self.dimension_kind,
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "schema_version": 1,
        }


@dataclass(frozen=True, slots=True)
class Unit:
    unit_ref: ObjectRef
    dimension_ref: ObjectRef
    unit_kind: str
    symbol: str
    definition_ref: ObjectRef
    validity_horizon_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.unit_ref, self.dimension_ref, self.definition_ref)):
            _failure(FailureCode.CORE_NUMBER_INVALID, "Unit", "unit refs must be exact ObjectRef values")
        if type(self.unit_kind) is not str or self.unit_kind not in {"BASE", "DERIVED", "DECLARED_INSTITUTIONAL"}:
            _failure(FailureCode.UNIT_MISMATCH, "Unit", "unit kind is outside the closed domain")
        if type(self.symbol) is not str or not self.symbol or unicodedata.normalize("NFC", self.symbol) != self.symbol:
            _failure(FailureCode.UNIT_MISMATCH, "Unit", "unit symbol must be nonempty NFC text")
        if not _conditional(self.validity_horizon_ref):
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, "Unit", "unit horizon applicability must be typed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "definition_ref": self.definition_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "schema_version": 1,
            "symbol": self.symbol,
            "unit_kind": self.unit_kind,
            "unit_ref": self.unit_ref.to_ecj1(),
            "validity_horizon_ref": _project(self.validity_horizon_ref),
        }


@dataclass(frozen=True, slots=True)
class ConversionRule:
    conversion_ref: ObjectRef
    source_unit_ref: ObjectRef
    target_unit_ref: ObjectRef
    dimension_ref: ObjectRef
    direction: str
    factor: RationalV1 | DecimalV1
    offset: RationalV1 | DecimalV1 | Applicability
    validity_horizon_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.conversion_ref, self.source_unit_ref, self.target_unit_ref, self.dimension_ref)):
            _failure(FailureCode.CORE_NUMBER_INVALID, "ConversionRule", "conversion refs must be exact ObjectRef values")
        if type(self.direction) is not str or type(self.factor) not in {RationalV1, DecimalV1}:
            _failure(FailureCode.CORE_NUMBER_INVALID, "ConversionRule", "conversion direction and factor have invalid runtime types")
        if type(self.offset) not in {RationalV1, DecimalV1, Applicability} or not _conditional(self.validity_horizon_ref):
            _failure(FailureCode.CORE_NUMBER_INVALID, "ConversionRule", "conversion conditional fields have invalid runtime types")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "conversion_ref": self.conversion_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "direction": self.direction,
            "factor": self.factor.to_ecj1(),
            "offset": _project(self.offset),
            "schema_version": 1,
            "source_unit_ref": self.source_unit_ref.to_ecj1(),
            "target_unit_ref": self.target_unit_ref.to_ecj1(),
            "validity_horizon_ref": _project(self.validity_horizon_ref),
        }


@dataclass(frozen=True, slots=True)
class ResolutionDetail:
    state: ResolutionState
    present_value_ref: ObjectRef | Applicability
    completed_part_refs: tuple[ObjectRef, ...]
    missing_part_refs: tuple[ObjectRef, ...]
    due_condition_ref: ObjectRef | Applicability
    failure: FailureEnvelope | Applicability
    boundary_edge_ref: ObjectRef | Applicability
    reason_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if type(self.state) is not ResolutionState or not all(
            _conditional(value)
            for value in (
                self.present_value_ref,
                self.due_condition_ref,
                self.boundary_edge_ref,
                self.reason_ref,
            )
        ):
            _failure(FailureCode.CORE_NUMBER_INVALID, "ResolutionDetail", "resolution state or applicability has invalid runtime type")
        if type(self.completed_part_refs) is not tuple or not all(type(item) is ObjectRef for item in self.completed_part_refs) or type(self.missing_part_refs) is not tuple or not all(type(item) is ObjectRef for item in self.missing_part_refs):
            _failure(FailureCode.CORE_NUMBER_INVALID, "ResolutionDetail", "resolution parts must be exact ObjectRef tuples")
        if not (type(self.failure) is FailureEnvelope or type(self.failure) is Applicability):
            _failure(FailureCode.CORE_NUMBER_INVALID, "ResolutionDetail", "resolution failure union is invalid")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "boundary_edge_ref": _project(self.boundary_edge_ref),
            "completed_part_refs": [item.to_ecj1() for item in self.completed_part_refs],
            "due_condition_ref": _project(self.due_condition_ref),
            "failure": _project(self.failure),
            "missing_part_refs": [item.to_ecj1() for item in self.missing_part_refs],
            "present_value_ref": _project(self.present_value_ref),
            "reason_ref": _project(self.reason_ref),
            "schema_version": 1,
            "state": self.state.value,
        }


@dataclass(frozen=True, slots=True)
class Quantity:
    magnitude: CoreNumberV1
    unit_ref: ObjectRef
    dimension_ref: ObjectRef
    boundary_ref: ObjectRef
    resource_type_ref: ObjectRef | Applicability
    service_type_ref: ObjectRef | Applicability
    region_ref: ObjectRef | Applicability
    time_basis_ref: ObjectRef | Applicability
    sign_convention_ref: ObjectRef | Applicability
    uncertainty_ref: ObjectRef | Applicability
    resolution: ResolutionDetail

    def __post_init__(self) -> None:
        if not _core_type(self.magnitude) or not all(type(value) is ObjectRef for value in (self.unit_ref, self.dimension_ref, self.boundary_ref)):
            _failure(FailureCode.CORE_NUMBER_INVALID, "Quantity", "quantity magnitude and mandatory refs must be typed")
        if not all(_conditional(value) for value in (self.resource_type_ref, self.service_type_ref, self.region_ref, self.time_basis_ref, self.sign_convention_ref, self.uncertainty_ref)) or type(self.resolution) is not ResolutionDetail:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Quantity", "quantity conditional coordinates must be typed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "magnitude": _project(self.magnitude),
            "region_ref": _project(self.region_ref),
            "resolution": self.resolution.to_ecj1(),
            "resource_type_ref": _project(self.resource_type_ref),
            "schema_version": 1,
            "service_type_ref": _project(self.service_type_ref),
            "sign_convention_ref": _project(self.sign_convention_ref),
            "time_basis_ref": _project(self.time_basis_ref),
            "uncertainty_ref": _project(self.uncertainty_ref),
            "unit_ref": self.unit_ref.to_ecj1(),
        }


@dataclass(frozen=True, slots=True)
class ResourceType:
    resource_type_ref: ObjectRef
    dimension_ref: ObjectRef
    definition_ref: ObjectRef
    service_compatibility_refs: tuple[ObjectRef, ...]
    validity_horizon_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.resource_type_ref, self.dimension_ref, self.definition_ref)) or not _ordered_unique_refs(self.service_compatibility_refs) or not _conditional(self.validity_horizon_ref):
            _failure(FailureCode.QUANTITY_TYPE_MISMATCH, "ResourceType", "resource declaration is malformed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "definition_ref": self.definition_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "resource_type_ref": self.resource_type_ref.to_ecj1(),
            "schema_version": 1,
            "service_compatibility_refs": [item.to_ecj1() for item in self.service_compatibility_refs],
            "validity_horizon_ref": _project(self.validity_horizon_ref),
        }


@dataclass(frozen=True, slots=True)
class ServiceType:
    service_type_ref: ObjectRef
    definition_ref: ObjectRef
    required_resource_type_refs: tuple[ObjectRef, ...]
    output_dimension_ref: ObjectRef | Applicability
    validity_horizon_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if type(self.service_type_ref) is not ObjectRef or type(self.definition_ref) is not ObjectRef or not _ordered_unique_refs(self.required_resource_type_refs, nonempty=True) or not _conditional(self.output_dimension_ref) or not _conditional(self.validity_horizon_ref):
            _failure(FailureCode.QUANTITY_TYPE_MISMATCH, "ServiceType", "service declaration is malformed")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "definition_ref": self.definition_ref.to_ecj1(),
            "output_dimension_ref": _project(self.output_dimension_ref),
            "required_resource_type_refs": [item.to_ecj1() for item in self.required_resource_type_refs],
            "schema_version": 1,
            "service_type_ref": self.service_type_ref.to_ecj1(),
            "validity_horizon_ref": _project(self.validity_horizon_ref),
        }


@dataclass(frozen=True, slots=True)
class SignConvention:
    sign_convention_ref: ObjectRef
    definition_ref: ObjectRef
    positive_meaning: str
    zero_meaning: str
    negative_meaning: str

    def __post_init__(self) -> None:
        if type(self.sign_convention_ref) is not ObjectRef or type(self.definition_ref) is not ObjectRef:
            _failure(FailureCode.CORE_NUMBER_INVALID, "SignConvention", "sign convention refs must be typed")
        meanings = (self.positive_meaning, self.zero_meaning, self.negative_meaning)
        if not all(type(item) is str and item and unicodedata.normalize("NFC", item) == item for item in meanings) or len(set(meanings)) != 3:
            _failure(FailureCode.SIGN_CONVENTION_MISMATCH, "SignConvention", "sign meanings must be nonempty, NFC, and distinct")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "definition_ref": self.definition_ref.to_ecj1(),
            "negative_meaning": self.negative_meaning,
            "positive_meaning": self.positive_meaning,
            "schema_version": 1,
            "sign_convention_ref": self.sign_convention_ref.to_ecj1(),
            "zero_meaning": self.zero_meaning,
        }


@dataclass(frozen=True, slots=True)
class Instant:
    clock_ref: ObjectRef
    tick: IntegerV1

    def __post_init__(self) -> None:
        if type(self.clock_ref) is not ObjectRef or type(self.tick) is not IntegerV1:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Instant", "instant requires exact clock and tick")
        if self.tick.value < 0:
            _failure(FailureCode.CLOCK_MISMATCH, "Instant", "instant tick must be nonnegative")

    def to_ecj1(self) -> dict[str, object]:
        return {"clock_ref": self.clock_ref.to_ecj1(), "schema_version": 1, "tick": self.tick.to_ecj1()}


@dataclass(frozen=True, slots=True)
class Duration:
    clock_ref: ObjectRef
    ticks: IntegerV1

    def __post_init__(self) -> None:
        if type(self.clock_ref) is not ObjectRef or type(self.ticks) is not IntegerV1:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Duration", "duration requires exact clock and ticks")

    def to_ecj1(self) -> dict[str, object]:
        return {"clock_ref": self.clock_ref.to_ecj1(), "schema_version": 1, "ticks": self.ticks.to_ecj1()}


@dataclass(frozen=True, slots=True)
class Epoch:
    clock_ref: ObjectRef
    index: IntegerV1

    def __post_init__(self) -> None:
        if type(self.clock_ref) is not ObjectRef or type(self.index) is not IntegerV1:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Epoch", "epoch requires exact clock and index")
        if self.index.value < 0:
            _failure(FailureCode.CLOCK_MISMATCH, "Epoch", "epoch index must be nonnegative")

    def to_ecj1(self) -> dict[str, object]:
        return {"clock_ref": self.clock_ref.to_ecj1(), "index": self.index.to_ecj1(), "schema_version": 1}


@dataclass(frozen=True, slots=True)
class Region:
    region_ref: ObjectRef
    membership_rule_ref: ObjectRef
    clock_ref: ObjectRef
    parent_region_ref: ObjectRef | Applicability
    spatial_interpretation: str
    validity_start: Instant
    validity_end: Instant

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.region_ref, self.membership_rule_ref, self.clock_ref)) or not _conditional(self.parent_region_ref) or type(self.validity_start) is not Instant or type(self.validity_end) is not Instant:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Region", "region fields have invalid runtime types")
        if type(self.spatial_interpretation) is not str or self.spatial_interpretation not in {"PHYSICAL", "NETWORK_NODE_SET", "INSTITUTIONAL"}:
            _failure(FailureCode.REGION_MISMATCH, "Region", "region spatial interpretation is invalid")
        if type(self.parent_region_ref) is ObjectRef and self.parent_region_ref == self.region_ref:
            _failure(FailureCode.INVALID_AGGREGATION, "Region", "region cannot parent itself")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "clock_ref": self.clock_ref.to_ecj1(),
            "membership_rule_ref": self.membership_rule_ref.to_ecj1(),
            "parent_region_ref": _project(self.parent_region_ref),
            "region_ref": self.region_ref.to_ecj1(),
            "schema_version": 1,
            "spatial_interpretation": self.spatial_interpretation,
            "validity_end": self.validity_end.to_ecj1(),
            "validity_start": self.validity_start.to_ecj1(),
        }


@dataclass(frozen=True, slots=True)
class AccountingBoundary:
    boundary_ref: ObjectRef
    state_schema_ref: ObjectRef
    distortion_ref: ObjectRef
    clock_ref: ObjectRef
    initial_epoch_ref: ObjectRef
    horizon_ref: ObjectRef
    definition_ref: ObjectRef
    parent_boundary_ref: ObjectRef | Applicability
    comparator_ref: ObjectRef | Applicability
    objective_ref: ObjectRef | Applicability
    institutional_rule_ref: ObjectRef | Applicability
    included_resource_type_refs: tuple[ObjectRef, ...]
    included_service_type_refs: tuple[ObjectRef, ...]
    included_provider_refs: tuple[ObjectRef, ...]
    included_actor_refs: tuple[ObjectRef, ...]
    included_node_refs: tuple[ObjectRef, ...]
    included_edge_refs: tuple[ObjectRef, ...]
    included_region_refs: tuple[ObjectRef, ...]
    included_lifecycle_stage_refs: tuple[ObjectRef, ...]
    external_effect_refs: tuple[ObjectRef, ...]
    commitment_refs: tuple[ObjectRef, ...]
    reservation_refs: tuple[ObjectRef, ...]
    queue_refs: tuple[ObjectRef, ...]
    measurement_refs: tuple[ObjectRef, ...]
    natural_drive_refs: tuple[ObjectRef, ...]
    external_input_refs: tuple[ObjectRef, ...]
    unresolved_cross_boundary_effect_refs: tuple[ObjectRef, ...]
    cross_boundary_effect_treatments: tuple[tuple[ObjectRef, ObjectRef], ...]

    def __post_init__(self) -> None:
        required = (self.boundary_ref, self.state_schema_ref, self.distortion_ref, self.clock_ref, self.initial_epoch_ref, self.horizon_ref, self.definition_ref)
        if not all(type(value) is ObjectRef for value in required) or not all(_conditional(value) for value in (self.parent_boundary_ref, self.comparator_ref, self.objective_ref, self.institutional_rule_ref)):
            _failure(FailureCode.CORE_NUMBER_INVALID, "AccountingBoundary", "boundary refs have invalid runtime types")
        collections = (
            self.included_resource_type_refs, self.included_service_type_refs, self.included_provider_refs,
            self.included_actor_refs, self.included_node_refs, self.included_edge_refs, self.included_region_refs,
            self.included_lifecycle_stage_refs, self.external_effect_refs, self.commitment_refs, self.reservation_refs,
            self.queue_refs, self.measurement_refs, self.natural_drive_refs, self.external_input_refs,
            self.unresolved_cross_boundary_effect_refs,
        )
        if not all(_ordered_unique_refs(values) for values in collections):
            _failure(FailureCode.INVALID_AGGREGATION, "AccountingBoundary", "boundary ref collections must be ordered and duplicate-free")
        pairs = self.cross_boundary_effect_treatments
        if type(pairs) is not tuple or not all(type(pair) is tuple and len(pair) == 2 and type(pair[0]) is ObjectRef and type(pair[1]) is ObjectRef for pair in pairs):
            _failure(FailureCode.INVALID_AGGREGATION, "AccountingBoundary", "boundary treatments require exact pairs")
        keys = tuple(_ref_key(pair[0]) for pair in pairs)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)) or len(pairs) != len(set(pairs)):
            _failure(FailureCode.INVALID_AGGREGATION, "AccountingBoundary", "boundary treatment effect keys must be ordered and unique")

    def to_ecj1(self) -> dict[str, object]:
        result = {field: _project(getattr(self, field)) for field in self.__dataclass_fields__}
        result["schema_version"] = 1
        return result


@dataclass(frozen=True, slots=True)
class ClockSystem:
    clock_ref: ObjectRef
    epoch_definition_ref: ObjectRef
    duration_unit_ref: ObjectRef
    ordering: str
    origin_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.clock_ref, self.epoch_definition_ref, self.duration_unit_ref)) or type(self.ordering) is not str or self.ordering != "DISCRETE_TOTAL" or not _conditional(self.origin_ref):
            _failure(FailureCode.CLOCK_MISMATCH, "ClockSystem", "clock system declaration is invalid")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "clock_ref": self.clock_ref.to_ecj1(), "duration_unit_ref": self.duration_unit_ref.to_ecj1(),
            "epoch_definition_ref": self.epoch_definition_ref.to_ecj1(), "ordering": self.ordering,
            "origin_ref": _project(self.origin_ref), "schema_version": 1,
        }


@dataclass(frozen=True, slots=True)
class Horizon:
    horizon_ref: ObjectRef
    clock_ref: ObjectRef
    completion_rule_ref: ObjectRef
    settlement_rule_ref: ObjectRef
    start: Instant
    terminal: Instant
    endpoint_inclusion: str
    resolution: Duration
    measurement_epochs: tuple[Epoch, ...]
    post_terminal_effect_treatment: str
    terminal_pending_treatment: str

    def __post_init__(self) -> None:
        if not all(type(value) is ObjectRef for value in (self.horizon_ref, self.clock_ref, self.completion_rule_ref, self.settlement_rule_ref)) or type(self.start) is not Instant or type(self.terminal) is not Instant or type(self.resolution) is not Duration:
            _failure(FailureCode.CORE_NUMBER_INVALID, "Horizon", "horizon fields have invalid runtime types")
        if type(self.endpoint_inclusion) is not str or type(self.post_terminal_effect_treatment) is not str or type(self.terminal_pending_treatment) is not str or type(self.measurement_epochs) is not tuple or not all(type(item) is Epoch for item in self.measurement_epochs):
            _failure(FailureCode.CORE_NUMBER_INVALID, "Horizon", "horizon strings and epochs require exact runtime types")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "clock_ref": self.clock_ref.to_ecj1(), "completion_rule_ref": self.completion_rule_ref.to_ecj1(),
            "endpoint_inclusion": self.endpoint_inclusion, "horizon_ref": self.horizon_ref.to_ecj1(),
            "measurement_epochs": [item.to_ecj1() for item in self.measurement_epochs],
            "post_terminal_effect_treatment": self.post_terminal_effect_treatment,
            "resolution": self.resolution.to_ecj1(), "schema_version": 1,
            "settlement_rule_ref": self.settlement_rule_ref.to_ecj1(), "start": self.start.to_ecj1(),
            "terminal": self.terminal.to_ecj1(), "terminal_pending_treatment": self.terminal_pending_treatment,
        }


@dataclass(frozen=True, slots=True)
class UncertaintyRecord:
    uncertainty_ref: ObjectRef
    kind: UncertaintyKind
    value_unit_ref: ObjectRef | Applicability
    lower: Quantity | Applicability
    upper: Quantity | Applicability
    member_refs: tuple[ObjectRef, ...]
    probability_model_ref: ObjectRef | Applicability
    calibration_ref: ObjectRef | Applicability
    provenance_refs: tuple[ObjectRef, ...]
    violated_contract_ref: ObjectRef | Applicability
    resolution: ResolutionDetail

    def __post_init__(self) -> None:
        if type(self.uncertainty_ref) is not ObjectRef or type(self.kind) is not UncertaintyKind or not _conditional(self.value_unit_ref) or not (type(self.lower) is Quantity or type(self.lower) is Applicability) or not (type(self.upper) is Quantity or type(self.upper) is Applicability):
            _failure(FailureCode.CORE_NUMBER_INVALID, "UncertaintyRecord", "uncertainty identity/bound fields have invalid runtime types")
        if not _ordered_unique_refs(self.member_refs) or not _conditional(self.probability_model_ref) or not _conditional(self.calibration_ref) or not _ordered_unique_refs(self.provenance_refs) or not _conditional(self.violated_contract_ref) or type(self.resolution) is not ResolutionDetail:
            _failure(FailureCode.CORE_NUMBER_INVALID, "UncertaintyRecord", "uncertainty collection/applicability fields are invalid")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "calibration_ref": _project(self.calibration_ref), "kind": self.kind.value,
            "lower": _project(self.lower), "member_refs": [item.to_ecj1() for item in self.member_refs],
            "probability_model_ref": _project(self.probability_model_ref),
            "provenance_refs": [item.to_ecj1() for item in self.provenance_refs],
            "resolution": self.resolution.to_ecj1(), "schema_version": 1,
            "uncertainty_ref": self.uncertainty_ref.to_ecj1(), "upper": _project(self.upper),
            "value_unit_ref": _project(self.value_unit_ref), "violated_contract_ref": _project(self.violated_contract_ref),
        }


def validate_dimension_compatibility(left: Dimension, right: Dimension) -> CompatibilityResult:
    interface = "validate_dimension_compatibility"
    labels = ("dimension_ref", "basis_exponents")
    if type(left) is not Dimension or type(right) is not Dimension or left.dimension_ref != right.dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface, "dimension refs differ")
    if left.basis_exponents != right.basis_exponents:
        _failure(FailureCode.DIMENSION_MISMATCH, interface, "dimension basis vectors differ")
    return _success(labels)


def _rule_checks(rule: ConversionRule, source_ref: ObjectRef, target_ref: ObjectRef, source_dimension: ObjectRef, target_dimension: ObjectRef, interface: str) -> None:
    if (type(rule.factor) is RationalV1 and rule.factor.numerator.value == 0) or (type(rule.factor) is DecimalV1 and rule.factor.coefficient.value == 0):
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "conversion factor must be nonzero")
    if type(rule.offset) is Applicability:
        if rule.offset is not Applicability.NOT_APPLICABLE:
            _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "offset applicability is invalid")
    elif type(rule.offset) is not type(rule.factor):
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "factor and offset variants differ")
    forward = rule.source_unit_ref == source_ref and rule.target_unit_ref == target_ref
    reverse = rule.source_unit_ref == target_ref and rule.target_unit_ref == source_ref
    if rule.direction == "FORWARD_ONLY":
        valid_direction = forward
    elif rule.direction == "BIDIRECTIONAL":
        valid_direction = forward or reverse
    else:
        valid_direction = False
    if not valid_direction:
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "conversion direction or endpoints do not match")
    if not (rule.dimension_ref == source_dimension == target_dimension):
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "conversion dimensions do not match")
    if type(rule.validity_horizon_ref) is Applicability and rule.validity_horizon_ref is not Applicability.NOT_APPLICABLE:
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "conversion horizon applicability is invalid")


def validate_conversion_rule(rule: ConversionRule, source_unit: Unit, target_unit: Unit) -> CompatibilityResult:
    if type(rule) is not ConversionRule or type(source_unit) is not Unit or type(target_unit) is not Unit:
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, "validate_conversion_rule", "conversion validation requires typed arguments")
    _rule_checks(rule, source_unit.unit_ref, target_unit.unit_ref, source_unit.dimension_ref, target_unit.dimension_ref, "validate_conversion_rule")
    return _success(("factor_nonzero", "offset_variant", "direction", "dimension", "validity_horizon"))


def validate_unit_compatibility(source: Unit, target: Unit, conversion_or_not_applicable: ConversionRule | Applicability) -> CompatibilityResult:
    interface = "validate_unit_compatibility"
    labels = ("dimension", "unit_identity_or_conversion")
    if type(source) is not Unit or type(target) is not Unit or source.dimension_ref != target.dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface, "unit dimensions differ")
    if source.unit_ref == target.unit_ref:
        return _success(labels)
    if type(conversion_or_not_applicable) is not ConversionRule:
        _failure(FailureCode.UNIT_MISMATCH, interface, "different units require an exact conversion rule")
    _rule_checks(conversion_or_not_applicable, source.unit_ref, target.unit_ref, source.dimension_ref, target.dimension_ref, interface)
    return _success(labels, conversion=conversion_or_not_applicable.conversion_ref)


def _resolution_valid(record: ResolutionDetail) -> bool:
    na = Applicability.NOT_APPLICABLE
    empty = not record.completed_part_refs and not record.missing_part_refs
    if record.state is ResolutionState.PRESENT:
        return type(record.present_value_ref) is ObjectRef and empty and record.due_condition_ref is na and record.failure is na and record.boundary_edge_ref is na and record.reason_ref is na
    if record.state is ResolutionState.PENDING:
        return type(record.due_condition_ref) is ObjectRef and empty and record.present_value_ref is na and record.failure is na and record.boundary_edge_ref is na and record.reason_ref is na
    if record.state is ResolutionState.FAILED:
        return type(record.failure) is FailureEnvelope and empty and record.present_value_ref is na and record.due_condition_ref is na and record.boundary_edge_ref is na and record.reason_ref is na
    if record.state is ResolutionState.PARTIAL:
        return bool(record.completed_part_refs) and bool(record.missing_part_refs) and record.present_value_ref is na and record.due_condition_ref is na and record.failure is na and record.boundary_edge_ref is na and record.reason_ref is na
    if record.state is ResolutionState.UNRESOLVED:
        return type(record.reason_ref) is ObjectRef and record.present_value_ref is na and empty and record.due_condition_ref is na and record.failure is na and record.boundary_edge_ref is na
    if record.state is ResolutionState.OUT_OF_BOUNDARY:
        return type(record.boundary_edge_ref) is ObjectRef and type(record.reason_ref) is ObjectRef and record.present_value_ref is na and empty and record.due_condition_ref is na and record.failure is na
    return record.state is ResolutionState.NOT_APPLICABLE and type(record.reason_ref) is ObjectRef and record.present_value_ref is na and empty and record.due_condition_ref is na and record.failure is na and record.boundary_edge_ref is na


def _resolution_tuples_valid(record: ResolutionDetail) -> bool:
    return _ordered_unique_refs(record.completed_part_refs) and _ordered_unique_refs(record.missing_part_refs) and not set(record.completed_part_refs).intersection(record.missing_part_refs)


def validate_resolution_detail(record: ResolutionDetail) -> CompatibilityResult:
    if type(record) is not ResolutionDetail or not _resolution_valid(record):
        _failure(FailureCode.RESOLUTION_STATE_INVALID, "validate_resolution_detail", "resolution state and payload contradict")
    if not _resolution_tuples_valid(record):
        _failure(FailureCode.RESOLUTION_STATE_INVALID, "validate_resolution_detail", "resolution tuples are unordered, duplicated, or overlapping")
    return _success(("state_payload_relation", "tuple_order_and_disjointness"))


def validate_quantity(quantity: Quantity, expected_context: QuantityContext) -> CompatibilityResult:
    interface = "validate_quantity"
    labels = ("resolution", "dimension", "unit", "resource_service_type", "region", "time_basis", "sign_convention", "boundary", "uncertainty_applicability")
    if (
        type(quantity) is not Quantity
        or type(expected_context) is not QuantityContext
        or not _resolution_valid(quantity.resolution)
        or not _resolution_tuples_valid(quantity.resolution)
        or quantity.resolution.state is not ResolutionState.PRESENT
    ):
        _failure(FailureCode.RESOLUTION_STATE_INVALID, interface, "quantity resolution is invalid")
    if quantity.dimension_ref != expected_context.dimension_ref:
        _failure(FailureCode.DIMENSION_MISMATCH, interface, "quantity dimension differs")
    if quantity.unit_ref != expected_context.unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface, "quantity unit differs")
    if quantity.resource_type_ref != expected_context.resource_type_ref or quantity.service_type_ref != expected_context.service_type_ref:
        _failure(FailureCode.QUANTITY_TYPE_MISMATCH, interface, "quantity resource/service coordinates differ")
    if quantity.region_ref != expected_context.region_ref:
        _failure(FailureCode.REGION_MISMATCH, interface, "quantity region differs")
    if quantity.time_basis_ref != expected_context.time_basis_ref:
        _failure(FailureCode.TIME_BASIS_MISMATCH, interface, "quantity time basis differs")
    if quantity.sign_convention_ref != expected_context.sign_convention_ref:
        _failure(FailureCode.SIGN_CONVENTION_MISMATCH, interface, "quantity sign convention differs")
    if quantity.boundary_ref != expected_context.boundary_ref:
        _failure(FailureCode.BOUNDARY_MISMATCH, interface, "quantity boundary differs")
    uncertainty_ok = (
        quantity.uncertainty_ref is Applicability.NOT_APPLICABLE
        if expected_context.uncertainty_applicability is Applicability.NOT_APPLICABLE
        else type(quantity.uncertainty_ref) is ObjectRef
    )
    if not uncertainty_ok:
        _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "quantity uncertainty applicability differs")
    return _success(labels)


def convert_quantity_exact(
    quantity: Quantity,
    source_unit: Unit,
    target_unit: Unit,
    rule: ConversionRule,
) -> Quantity:
    interface = "convert_quantity_exact"
    if (
        type(quantity) is not Quantity
        or not _resolution_valid(quantity.resolution)
        or not _resolution_tuples_valid(quantity.resolution)
        or quantity.resolution.state is not ResolutionState.PRESENT
    ):
        _failure(FailureCode.RESOLUTION_STATE_INVALID, interface, "quantity is not intrinsically present and valid")
    if type(source_unit) is not Unit or quantity.unit_ref != source_unit.unit_ref:
        _failure(FailureCode.UNIT_MISMATCH, interface, "quantity unit differs from the explicit source unit")
    if type(target_unit) is not Unit or not (
        quantity.dimension_ref == source_unit.dimension_ref == target_unit.dimension_ref
    ):
        _failure(FailureCode.DIMENSION_MISMATCH, interface, "quantity, source, and target dimensions differ")
    if type(rule) is not ConversionRule:
        _failure(FailureCode.CONVERSION_RULE_MISMATCH, interface, "conversion requires an exact rule")
    _rule_checks(
        rule,
        source_unit.unit_ref,
        target_unit.unit_ref,
        source_unit.dimension_ref,
        target_unit.dimension_ref,
        interface,
    )
    if type(quantity.magnitude) is not type(rule.factor) or (
        type(rule.offset) is not Applicability
        and type(rule.offset) is not type(quantity.magnitude)
    ):
        _failure(
            FailureCode.IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,
            interface,
            "exact conversion arithmetic cannot mix numeric variants",
        )
    multiplied = apply_exact_core_operation(NumericalOperation.MULTIPLY, (quantity.magnitude, rule.factor))
    magnitude = multiplied.value
    if type(rule.offset) is not Applicability:
        added = apply_exact_core_operation(NumericalOperation.ADD, (magnitude, rule.offset))
        magnitude = added.value
    return replace(quantity, magnitude=magnitude, unit_ref=target_unit.unit_ref)


def validate_resource_service_compatibility(resource: ResourceType, service: ServiceType) -> CompatibilityResult:
    interface = "validate_resource_service_compatibility"
    if type(resource) is not ResourceType or type(service) is not ServiceType or service.service_type_ref not in resource.service_compatibility_refs:
        _failure(FailureCode.QUANTITY_TYPE_MISMATCH, interface, "resource does not declare the service")
    if resource.resource_type_ref not in service.required_resource_type_refs:
        _failure(FailureCode.QUANTITY_TYPE_MISMATCH, interface, "service does not declare the resource")
    return _success(("resource_declares_service", "service_declares_resource"))


def validate_region_compatibility(left: Region, right: Region, parent_or_not_applicable: Region | Applicability, aggregation_rule_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult:
    interface = "validate_region_compatibility"
    labels = ("identity_or_parent", "declared_parent_links", "clock", "validity_interval", "distinct_children", "aggregation_rule")
    if left.region_ref == right.region_ref and parent_or_not_applicable is Applicability.NOT_APPLICABLE:
        return _success(labels)
    if type(parent_or_not_applicable) is not Region:
        _failure(FailureCode.REGION_MISMATCH, interface, "different regions require a supplied parent")
    if left.parent_region_ref != parent_or_not_applicable.region_ref or right.parent_region_ref != parent_or_not_applicable.region_ref:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "children do not declare the supplied parent")
    if not (left.clock_ref == right.clock_ref == parent_or_not_applicable.clock_ref):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "parent and child region clocks differ")
    if not (
        parent_or_not_applicable.validity_start.tick.value <= left.validity_start.tick.value
        and parent_or_not_applicable.validity_start.tick.value <= right.validity_start.tick.value
        and parent_or_not_applicable.validity_end.tick.value >= left.validity_end.tick.value
        and parent_or_not_applicable.validity_end.tick.value >= right.validity_end.tick.value
    ):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "parent interval does not cover both children")
    if left.region_ref == right.region_ref:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "aggregation children must be distinct")
    if type(aggregation_rule_or_not_applicable) is not ObjectRef:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "aggregation rule is absent")
    return _success(labels, parent=parent_or_not_applicable.region_ref)


def _treatment_coverage(boundary: AccountingBoundary) -> bool:
    declared = {item for item in boundary.external_effect_refs + boundary.unresolved_cross_boundary_effect_refs}
    mapped = {pair[0] for pair in boundary.cross_boundary_effect_treatments}
    return declared == mapped


def validate_boundary_compatibility(left: AccountingBoundary, right: AccountingBoundary, parent_or_not_applicable: AccountingBoundary | Applicability, aggregation_rule_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult:
    interface = "validate_boundary_compatibility"
    labels = ("identity_or_parent", "declared_parent_links", "state_schema", "distortion", "clock", "horizon", "cross_boundary_treatment", "distinct_children", "aggregation_rule")
    if left.boundary_ref == right.boundary_ref and parent_or_not_applicable is Applicability.NOT_APPLICABLE:
        return _success(labels)
    if type(parent_or_not_applicable) is not AccountingBoundary:
        _failure(FailureCode.BOUNDARY_MISMATCH, interface, "different boundaries require a supplied parent")
    if left.parent_boundary_ref != parent_or_not_applicable.boundary_ref or right.parent_boundary_ref != parent_or_not_applicable.boundary_ref:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "children do not declare the supplied parent")
    if not (left.state_schema_ref == right.state_schema_ref == parent_or_not_applicable.state_schema_ref):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "boundary state schemas differ")
    if not (left.distortion_ref == right.distortion_ref == parent_or_not_applicable.distortion_ref):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "boundary distortion refs differ")
    if not (left.clock_ref == right.clock_ref == parent_or_not_applicable.clock_ref):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "boundary clocks differ")
    if not (left.horizon_ref == right.horizon_ref == parent_or_not_applicable.horizon_ref):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "boundary horizons differ")
    if not _treatment_coverage(left) or not _treatment_coverage(right):
        _failure(FailureCode.INVALID_AGGREGATION, interface, "declared cross-boundary effects lack exact treatment coverage")
    if left.boundary_ref == right.boundary_ref:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "aggregation children must be distinct")
    if type(aggregation_rule_or_not_applicable) is not ObjectRef:
        _failure(FailureCode.INVALID_AGGREGATION, interface, "aggregation rule is absent")
    return _success(labels, parent=parent_or_not_applicable.boundary_ref)


def validate_sign_convention_compatibility(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult:
    interface = "validate_sign_convention_compatibility"
    left_na = left_or_not_applicable is Applicability.NOT_APPLICABLE
    right_na = right_or_not_applicable is Applicability.NOT_APPLICABLE
    if left_na != right_na or not ((left_na and right_na) or (type(left_or_not_applicable) is ObjectRef and type(right_or_not_applicable) is ObjectRef)):
        _failure(FailureCode.SIGN_CONVENTION_MISMATCH, interface, "sign applicability differs")
    if not left_na and left_or_not_applicable != right_or_not_applicable:
        _failure(FailureCode.SIGN_CONVENTION_MISMATCH, interface, "sign refs differ")
    return _success(("applicability", "identity"))


def validate_time_basis(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: ObjectRef | Applicability, rate_required: bool) -> CompatibilityResult:
    interface = "validate_time_basis"
    if type(rate_required) is not bool:
        _failure(FailureCode.TIME_BASIS_MISMATCH, interface, "rate_required must be exact bool")
    applicable = type(left_or_not_applicable) is ObjectRef and type(right_or_not_applicable) is ObjectRef
    absent = left_or_not_applicable is Applicability.NOT_APPLICABLE and right_or_not_applicable is Applicability.NOT_APPLICABLE
    if (rate_required and not applicable) or (not rate_required and not absent):
        _failure(FailureCode.TIME_BASIS_MISMATCH, interface, "time-basis applicability differs")
    if applicable and left_or_not_applicable != right_or_not_applicable:
        _failure(FailureCode.TIME_BASIS_MISMATCH, interface, "time-basis refs differ")
    return _success(("applicability", "identity"))


def validate_clock_compatibility(left: ClockSystem, right: ClockSystem) -> CompatibilityResult:
    if type(left) is not ClockSystem or type(right) is not ClockSystem or left.clock_ref != right.clock_ref:
        _failure(FailureCode.CLOCK_MISMATCH, "validate_clock_compatibility", "clock refs differ")
    return _success(("clock_ref",))


def validate_horizon(horizon: Horizon, pending_effect_due_pairs: tuple[tuple[ObjectRef, ObjectRef], ...]) -> CompatibilityResult:
    interface = "validate_horizon"
    labels = ("clock_refs", "endpoint_order", "endpoint_inclusion", "resolution", "measurement_epochs", "post_terminal_effect_treatment", "terminal_pending_treatment")
    if type(horizon) is not Horizon or not (
        horizon.start.clock_ref == horizon.clock_ref == horizon.terminal.clock_ref == horizon.resolution.clock_ref
        and all(item.clock_ref == horizon.clock_ref for item in horizon.measurement_epochs)
    ):
        _failure(FailureCode.CLOCK_MISMATCH, interface, "horizon clock refs differ")
    if horizon.start.tick.value > horizon.terminal.tick.value:
        _failure(FailureCode.HORIZON_INVALID, interface, "horizon endpoints are reversed")
    if horizon.endpoint_inclusion not in {"CLOSED", "LEFT_CLOSED_RIGHT_OPEN"}:
        _failure(FailureCode.HORIZON_INVALID, interface, "endpoint inclusion is invalid")
    if horizon.resolution.ticks.value <= 0:
        _failure(FailureCode.HORIZON_INVALID, interface, "horizon resolution must be positive")
    indexes = tuple(item.index.value for item in horizon.measurement_epochs)
    if any(left >= right for left, right in zip(indexes, indexes[1:])) or any(index < horizon.start.tick.value or index > horizon.terminal.tick.value for index in indexes):
        _failure(FailureCode.HORIZON_INVALID, interface, "measurement epochs are unordered or outside the declared endpoints")
    if horizon.post_terminal_effect_treatment not in {"REMAIN_PENDING", "OUT_OF_BOUNDARY"}:
        _failure(FailureCode.HORIZON_INVALID, interface, "post-terminal treatment is invalid")
    if type(pending_effect_due_pairs) is not tuple or not all(type(pair) is tuple and len(pair) == 2 and type(pair[0]) is ObjectRef and type(pair[1]) is ObjectRef for pair in pending_effect_due_pairs):
        _failure(FailureCode.HORIZON_INVALID, interface, "pending effect/due declarations require exact pairs")
    keys = tuple(_ref_key(pair[0]) for pair in pending_effect_due_pairs)
    pairs_valid = keys == tuple(sorted(keys)) and len(keys) == len(set(keys))
    if horizon.terminal_pending_treatment == "REQUIRE_NONE_PENDING":
        pending_valid = not pending_effect_due_pairs
    elif horizon.terminal_pending_treatment == "ALLOW_EXPLICIT_PENDING":
        pending_valid = pairs_valid
    else:
        pending_valid = False
    if not pending_valid:
        _failure(FailureCode.HORIZON_INVALID, interface, "terminal pending treatment or supplied pairs are invalid")
    return _success(labels)


def _quantity_coordinates_match(left: Quantity, right: Quantity) -> bool:
    return all(
        getattr(left, name) == getattr(right, name)
        for name in (
            "unit_ref", "dimension_ref", "boundary_ref", "resource_type_ref", "service_type_ref",
            "region_ref", "time_basis_ref", "sign_convention_ref",
        )
    )


def validate_uncertainty_record(record: UncertaintyRecord) -> CompatibilityResult:
    interface = "validate_uncertainty_record"
    labels = ("resolution", "kind_fields", "unit_coordinates", "bound_order", "provenance")
    if type(record) is not UncertaintyRecord or not _resolution_valid(record.resolution) or not _resolution_tuples_valid(record.resolution):
        _failure(FailureCode.RESOLUTION_STATE_INVALID, interface, "uncertainty resolution is invalid")
    na = Applicability.NOT_APPLICABLE
    bounds = type(record.lower) is Quantity and type(record.upper) is Quantity
    no_bounds = record.lower is na and record.upper is na
    no_members = not record.member_refs
    no_model = record.probability_model_ref is na
    resolution_for_kind = True
    kind_fields_ok = True
    if record.kind is UncertaintyKind.EXACT:
        resolution_for_kind = record.resolution.state is ResolutionState.PRESENT
        kind_fields_ok = no_bounds and no_members and no_model
    elif record.kind is UncertaintyKind.MEASUREMENT_INTERVAL:
        kind_fields_ok = bounds and no_members and no_model and type(record.calibration_ref) is ObjectRef
    elif record.kind in {UncertaintyKind.ADMISSIBLE_SET, UncertaintyKind.ADVERSARIAL_SET}:
        kind_fields_ok = no_bounds and bool(record.member_refs) and no_model
    elif record.kind is UncertaintyKind.PROBABILITY_MODEL:
        kind_fields_ok = no_bounds and no_members and type(record.probability_model_ref) is ObjectRef
    elif record.kind is UncertaintyKind.MODEL_DISCREPANCY:
        kind_fields_ok = (bounds or bool(record.member_refs)) and no_model
    elif record.kind is UncertaintyKind.UNKNOWN:
        resolution_for_kind = record.resolution.state is ResolutionState.UNRESOLVED
        kind_fields_ok = no_bounds and no_members and no_model
    elif record.kind is UncertaintyKind.OUT_OF_SET:
        resolution_for_kind = type(record.resolution.present_value_ref) is ObjectRef
        kind_fields_ok = no_bounds and no_members and no_model and type(record.violated_contract_ref) is ObjectRef
    if record.kind is not UncertaintyKind.OUT_OF_SET and record.violated_contract_ref is not na:
        kind_fields_ok = False
    if not resolution_for_kind and not kind_fields_ok:
        _failure(FailureCode.RESOLUTION_STATE_INVALID, interface, "resolution and uncertainty fields are both contradictory")
    if not resolution_for_kind or not kind_fields_ok:
        _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "uncertainty kind fields contradict")
    if bounds:
        lower = record.lower
        upper = record.upper
        if not _quantity_coordinates_match(lower, upper) or record.value_unit_ref != lower.unit_ref:
            _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "uncertainty bound coordinates differ")
        if type(lower.magnitude) is not type(upper.magnitude) or type(lower.magnitude) is Binary64BitsV1:
            _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "uncertainty bounds are not exactly orderable")
        if _same_core_compare(lower.magnitude, upper.magnitude) > 0:
            _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "uncertainty bounds are reversed")
    provenance_ok = True
    if record.kind in {UncertaintyKind.PROBABILITY_MODEL, UncertaintyKind.MODEL_DISCREPANCY}:
        provenance_ok = bool(record.provenance_refs)
    if record.kind is UncertaintyKind.OUT_OF_SET:
        provenance_ok = type(record.violated_contract_ref) is ObjectRef and record.violated_contract_ref in record.provenance_refs
    if not provenance_ok:
        _failure(FailureCode.UNCERTAINTY_RECORD_INVALID, interface, "uncertainty provenance is incomplete")
    return _success(labels)


__all__ = (
    "AccountingBoundary",
    "ClaimStatus",
    "ClockSystem",
    "CompatibilityResult",
    "ConversionRule",
    "Dimension",
    "Duration",
    "Epoch",
    "Horizon",
    "Instant",
    "Quantity",
    "Region",
    "ResolutionDetail",
    "ResolutionState",
    "ResourceType",
    "ServiceType",
    "SignConvention",
    "UncertaintyKind",
    "UncertaintyRecord",
    "Unit",
    "convert_quantity_exact",
    "validate_boundary_compatibility",
    "validate_clock_compatibility",
    "validate_conversion_rule",
    "validate_dimension_compatibility",
    "validate_horizon",
    "validate_quantity",
    "validate_region_compatibility",
    "validate_resolution_detail",
    "validate_resource_service_compatibility",
    "validate_sign_convention_compatibility",
    "validate_time_basis",
    "validate_uncertainty_record",
    "validate_unit_compatibility",
)
