"""Pure I-6 sequential/parallel bridge declarations and inert fixture checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
import hashlib
from typing import Literal, NoReturn

from . import state as _state
from . import distortion as _distortion
from . import actions as _actions
from . import settlement as _settlement
from . import scheduling as _scheduling
from . import causal as _causal
from . import interaction as _interaction
from . import primitives as _primitives
from . import numeric as _numeric
from . import canonical as _canonical
from . import envelopes as _envelopes
from . import identity as _identity
from . import errors as _errors
from . import capabilities as _capabilities


RepresentedState = _state.RepresentedState
DistortionModel = _distortion.DistortionModel
ActionInstance = _actions.ActionInstance
EffectiveInterval = _actions.EffectiveInterval
WriteSupport = _actions.WriteSupport
ConstraintSupport = _actions.ConstraintSupport
GroupReceipt = _settlement.GroupReceipt
ComparatorSchedule = _scheduling.ComparatorSchedule
CausalIdentificationStatus = _causal.CausalIdentificationStatus
SameBaselineNonadditivityWitness = _interaction.SameBaselineNonadditivityWitness
SerialComparatorInteractionWitness = _interaction.SerialComparatorInteractionWitness
Quantity = _primitives.Quantity
CanonicalBytes = _canonical.CanonicalBytes
CommonObjectEnvelope = _envelopes.CommonObjectEnvelope
ObjectRef = _identity.ObjectRef
T2FixtureCapability = _capabilities.T2FixtureCapability
Applicability = _errors.Applicability
FailureCode = _errors.FailureCode
FrameworkError = _errors.FrameworkError


_DEPENDENCY_KINDS = (
    "SHARED_WRITE_SUPPORT",
    "SHARED_CONSTRAINT",
    "CROSS_ACTION_DEPENDENCY",
    "NONSEPARABLE_DISTORTION",
    "COMMON_ENDPOINT_ONLY_OBSERVATION",
)
_REPLAY_KINDS = ("QUANTITY_FIXED", "RULE_REPLAYED")
_SELECTION_KINDS = (
    "ORDER_INVARIANT_IDENTIFIER",
    "MANDATORY_PRECEDENCE",
    "FROZEN_OBSERVED_ORDER",
    "ALL_FEASIBLE_OR_EXACT_EXTREMA",
    "POLICY_CANONICAL_WITH_SENSITIVITY",
    "PREREGISTERED_LARGE_N_COVERAGE",
    "NONSERIALIZABLE",
)
_MEASUREMENT_KINDS = (
    "PHYSICAL_JOINT_GROUP",
    "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS",
)
_NONADDITIVITY_STATUSES = ("DEFINED", "UNDEFINED_NO_STANDALONE_CHILDREN")
_COMPARISON_KINDS = (
    "PHYSICAL_GROUP_COMPARATOR",
    "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS",
)
_BRIDGE_OPERATIONS = (
    "classify_joint_groups",
    "compute_group_measurement",
    "compute_same_baseline_nonadditivity",
    "compute_comparator_interaction",
)
_FIXTURE_SHA256 = (
    "8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af"
)
_OBJECT_SURFACES = {
    "DependencyEdge": (
        "ebu:object-kind:framework-i6:dependency-edge",
        "ebu:schema:framework-i6:dependency-edge-v1",
    ),
    "JointTransitionGroup": (
        "ebu:object-kind:framework-i6:joint-transition-group",
        "ebu:schema:framework-i6:joint-transition-group-v1",
    ),
    "AdmissibleComparatorSet": (
        "ebu:object-kind:framework-i6:admissible-comparator-set",
        "ebu:schema:framework-i6:admissible-comparator-set-v1",
    ),
    "GroupMeasurement": (
        "ebu:object-kind:framework-i6:group-measurement",
        "ebu:schema:framework-i6:group-measurement-v1",
    ),
    "SameBaselineNonadditivity": (
        "ebu:object-kind:framework-i6:same-baseline-nonadditivity",
        "ebu:schema:framework-i6:same-baseline-nonadditivity-v1",
    ),
    "ComparatorInteraction": (
        "ebu:object-kind:framework-i6:comparator-interaction",
        "ebu:schema:framework-i6:comparator-interaction-v1",
    ),
    "NonserializableGroup": (
        "ebu:object-kind:framework-i6:nonserializable-group",
        "ebu:schema:framework-i6:nonserializable-group-v1",
    ),
}


def _interface(name: str) -> _errors.FailureInterfaceRef:
    return _errors.FailureInterfaceRef("ebu_framework.bridge", name, "1.0.0")


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _errors._fail(
        code,
        f"{interface} rejected {code.value}",
        stage=_errors.FailureStage.I6,
        interface_ref=_interface(interface),
        scientific_status_effect=_errors.ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=_errors.RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I6_RECORD_FORMATION_INVALID, interface)


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


def _ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _ordered_unique_refs(value: object, *, nonempty: bool = False) -> bool:
    if not _ref_tuple(value) or (nonempty and not value):
        return False
    keys = tuple(_ref_key(item) for item in value)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _ref_or_not_applicable(value: object) -> bool:
    return type(value) is ObjectRef or value is Applicability.NOT_APPLICABLE


def _quantity_or_not_applicable(value: object) -> bool:
    return type(value) is Quantity or value is Applicability.NOT_APPLICABLE


def _ref_rows(value: object, member_type: type) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 2
        and type(row[0]) is ObjectRef
        and type(row[1]) is member_type
        for row in value
    )


def _ref_nested_ref_rows(value: object) -> bool:
    return type(value) is tuple and all(
        type(row) is tuple
        and len(row) == 2
        and type(row[0]) is ObjectRef
        and _ref_tuple(row[1])
        for row in value
    )


def _core_fraction(value: _numeric.CoreNumberV1) -> Fraction:
    projected = value.to_ecj1()
    variant = projected["variant"]
    if variant == "INTEGER_V1":
        return Fraction(projected["value"])
    if variant == "RATIONAL_V1":
        return Fraction(projected["numerator"], projected["denominator"])
    if variant == "DECIMAL_V1":
        coefficient = projected["coefficient"]
        exponent = projected["exponent10"]
        if exponent >= 0:
            return Fraction(coefficient * 10**exponent)
        return Fraction(coefficient, 10 ** (-exponent))
    bits = int(projected["bits"], 16)
    sign = -1 if bits >> 63 else 1
    exponent_bits = (bits >> 52) & 0x7FF
    fraction_bits = bits & ((1 << 52) - 1)
    if exponent_bits == 0:
        significand = fraction_bits
        exponent = -1074
    else:
        significand = (1 << 52) | fraction_bits
        exponent = exponent_bits - 1023 - 52
    if exponent >= 0:
        return Fraction(sign * significand * 2**exponent)
    return Fraction(sign * significand, 2 ** (-exponent))


def _quantity_contexts(
    quantities: tuple[Quantity, ...], interface: str
) -> None:
    first = quantities[0]
    if any(item.unit_ref != first.unit_ref for item in quantities[1:]):
        _failure(FailureCode.UNIT_MISMATCH, interface)
    if any(item.dimension_ref != first.dimension_ref for item in quantities[1:]):
        _failure(FailureCode.DIMENSION_MISMATCH, interface)
    if any(item.boundary_ref != first.boundary_ref for item in quantities[1:]):
        _failure(FailureCode.INCOMPATIBLE_BOUNDARY, interface)


def _quantity_value_equal(left: Quantity, right: Quantity) -> bool:
    return (
        _core_fraction(left.magnitude) == _core_fraction(right.magnitude)
        and left.unit_ref == right.unit_ref
        and left.dimension_ref == right.dimension_ref
        and left.boundary_ref == right.boundary_ref
    )


def _validate_record_envelope(record: object, interface: str) -> None:
    envelope = record.envelope  # type: ignore[attr-defined]
    if type(envelope) is not CommonObjectEnvelope:
        _formation_failure(interface)
    expected_kind, expected_schema = _OBJECT_SURFACES[interface]
    if not (
        str(envelope.object_kind_id) == expected_kind
        and str(envelope.schema_id) == expected_schema
        and str(envelope.schema_version) == "1.0.0"
    ):
        _formation_failure(interface)
    try:
        _envelopes.validate_object_envelope(envelope)
    except FrameworkError as exc:
        if exc.envelope.failure_code is FailureCode.HASH_MISMATCH:
            _failure(FailureCode.HASH_MISMATCH, interface)
        _formation_failure(interface)
    if envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _formation_failure(interface)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class DependencyEdge:
    envelope: CommonObjectEnvelope
    left_action_ref: ObjectRef
    right_action_ref: ObjectRef
    left_effective_interval: EffectiveInterval
    right_effective_interval: EffectiveInterval
    dependency_kinds: tuple[
        Literal[
            "SHARED_WRITE_SUPPORT",
            "SHARED_CONSTRAINT",
            "CROSS_ACTION_DEPENDENCY",
            "NONSEPARABLE_DISTORTION",
            "COMMON_ENDPOINT_ONLY_OBSERVATION",
        ],
        ...,
    ]
    boundary_ref: ObjectRef
    declaration_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.left_action_ref) is ObjectRef
            and type(self.right_action_ref) is ObjectRef
            and type(self.left_effective_interval) is EffectiveInterval
            and type(self.right_effective_interval) is EffectiveInterval
            and type(self.dependency_kinds) is tuple
            and bool(self.dependency_kinds)
            and all(type(item) is str and item in _DEPENDENCY_KINDS for item in self.dependency_kinds)
            and type(self.boundary_ref) is ObjectRef
            and type(self.declaration_ref) is ObjectRef
        ):
            _formation_failure("DependencyEdge")
        indexes = tuple(_DEPENDENCY_KINDS.index(item) for item in self.dependency_kinds)
        if indexes != tuple(sorted(indexes)) or len(indexes) != len(set(indexes)):
            _formation_failure("DependencyEdge")
        if _ref_key(self.left_action_ref) >= _ref_key(self.right_action_ref):
            _formation_failure("DependencyEdge")
        left = self.left_effective_interval
        right = self.right_effective_interval
        if not (
            left.clock_ref == left.start.clock_ref == left.end.clock_ref
            and right.clock_ref == right.start.clock_ref == right.end.clock_ref
            and left.clock_ref == right.clock_ref
        ):
            _failure(FailureCode.UNRESOLVED_COUPLING, "DependencyEdge")
        if max(left.start.tick.value, right.start.tick.value) >= min(
            left.end.tick.value, right.end.tick.value
        ):
            _failure(FailureCode.UNRESOLVED_COUPLING, "DependencyEdge")
        _validate_record_envelope(self, "DependencyEdge")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class JointTransitionGroup:
    envelope: CommonObjectEnvelope
    child_action_refs: tuple[ObjectRef, ...]
    child_effective_intervals: tuple[tuple[ObjectRef, EffectiveInterval], ...]
    child_write_supports: tuple[tuple[ObjectRef, WriteSupport], ...]
    child_constraint_supports: tuple[tuple[ObjectRef, ConstraintSupport], ...]
    child_commitment_refs: tuple[tuple[ObjectRef, tuple[ObjectRef, ...]], ...]
    accepted_quantity_refs: tuple[tuple[ObjectRef, tuple[ObjectRef, ...]], ...]
    dependency_edges: tuple[DependencyEdge, ...]
    dependency_relation_complete: bool
    separability_evidence_ref: ObjectRef | Applicability
    common_before_state_ref: ObjectRef
    common_boundary_ref: ObjectRef
    common_distortion_model_ref: ObjectRef
    common_horizon_ref: ObjectRef
    joint_write_support_ref: ObjectRef
    joint_constraint_set_ref: ObjectRef
    source_budget_account_ref: ObjectRef

    def __post_init__(self) -> None:
        common_refs = (
            self.common_before_state_ref,
            self.common_boundary_ref,
            self.common_distortion_model_ref,
            self.common_horizon_ref,
            self.joint_write_support_ref,
            self.joint_constraint_set_ref,
            self.source_budget_account_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and _ordered_unique_refs(self.child_action_refs, nonempty=True)
            and _ref_rows(self.child_effective_intervals, EffectiveInterval)
            and _ref_rows(self.child_write_supports, WriteSupport)
            and _ref_rows(self.child_constraint_supports, ConstraintSupport)
            and _ref_nested_ref_rows(self.child_commitment_refs)
            and _ref_nested_ref_rows(self.accepted_quantity_refs)
            and type(self.dependency_edges) is tuple
            and all(type(item) is DependencyEdge for item in self.dependency_edges)
            and type(self.dependency_relation_complete) is bool
            and _ref_or_not_applicable(self.separability_evidence_ref)
            and all(type(item) is ObjectRef for item in common_refs)
        ):
            _formation_failure("JointTransitionGroup")
        child_keys = tuple(_ref_key(item) for item in self.child_action_refs)
        for rows in (
            self.child_effective_intervals,
            self.child_write_supports,
            self.child_constraint_supports,
            self.child_commitment_refs,
            self.accepted_quantity_refs,
        ):
            if tuple(_ref_key(row[0]) for row in rows) != child_keys:
                _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
        if not self.dependency_relation_complete:
            _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
        child_set = set(self.child_action_refs)
        if len(self.child_action_refs) == 1:
            if self.dependency_edges or type(self.separability_evidence_ref) is not ObjectRef:
                _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
        else:
            if not self.dependency_edges or self.separability_evidence_ref is not Applicability.NOT_APPLICABLE:
                _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
            if any(
                edge.left_action_ref not in child_set or edge.right_action_ref not in child_set
                for edge in self.dependency_edges
            ):
                _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
            if any(edge.boundary_ref != self.common_boundary_ref for edge in self.dependency_edges):
                _failure(FailureCode.INCOMPATIBLE_BOUNDARY, "JointTransitionGroup")
            reached = {self.child_action_refs[0]}
            while True:
                expanded = reached | {
                    endpoint
                    for edge in self.dependency_edges
                    if edge.left_action_ref in reached or edge.right_action_ref in reached
                    for endpoint in (edge.left_action_ref, edge.right_action_ref)
                }
                if expanded == reached:
                    break
                reached = expanded
            if reached != child_set:
                _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
        intervals = dict(self.child_effective_intervals)
        if any(
            intervals[edge.left_action_ref] != edge.left_effective_interval
            or intervals[edge.right_action_ref] != edge.right_effective_interval
            for edge in self.dependency_edges
        ):
            _failure(FailureCode.GROUPING_FAILURE, "JointTransitionGroup")
        _validate_record_envelope(self, "JointTransitionGroup")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AdmissibleComparatorSet:
    envelope: CommonObjectEnvelope
    group_or_witness_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    baseline_state_ref: ObjectRef
    boundary_ref: ObjectRef
    distortion_model_ref: ObjectRef
    horizon_ref: ObjectRef
    exogenous_drive_ref: ObjectRef
    comparator_schedules: tuple[ComparatorSchedule, ...]
    comparator_orderings: tuple[tuple[ObjectRef, ...], ...]
    replay_kinds: tuple[Literal["QUANTITY_FIXED", "RULE_REPLAYED"], ...]
    same_children_commitments_evidence_refs: tuple[ObjectRef, ...]
    live_predecessor_evidence_refs: tuple[ObjectRef, ...]
    feasibility_evidence_refs: tuple[ObjectRef, ...]
    represented_effect_evidence_refs: tuple[ObjectRef, ...]
    freeze_evidence_refs: tuple[ObjectRef, ...]
    selection_kind: Literal[
        "ORDER_INVARIANT_IDENTIFIER",
        "MANDATORY_PRECEDENCE",
        "FROZEN_OBSERVED_ORDER",
        "ALL_FEASIBLE_OR_EXACT_EXTREMA",
        "POLICY_CANONICAL_WITH_SENSITIVITY",
        "PREREGISTERED_LARGE_N_COVERAGE",
        "NONSERIALIZABLE",
    ]
    named_reported_comparator_refs: tuple[ObjectRef, ...]
    omitted_schedule_refs: tuple[ObjectRef, ...]
    coverage_and_uncertainty_ref: ObjectRef | Applicability
    status: Literal["DEFINED", "NONSERIALIZABLE"]

    def __post_init__(self) -> None:
        scalar_refs = (
            self.group_or_witness_ref,
            self.baseline_state_ref,
            self.boundary_ref,
            self.distortion_model_ref,
            self.horizon_ref,
            self.exogenous_drive_ref,
        )
        evidence_rows = (
            self.same_children_commitments_evidence_refs,
            self.feasibility_evidence_refs,
            self.represented_effect_evidence_refs,
            self.freeze_evidence_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(item) is ObjectRef for item in scalar_refs)
            and _ordered_unique_refs(self.action_refs, nonempty=True)
            and type(self.comparator_schedules) is tuple
            and all(type(item) is ComparatorSchedule for item in self.comparator_schedules)
            and type(self.comparator_orderings) is tuple
            and all(_ref_tuple(item) for item in self.comparator_orderings)
            and type(self.replay_kinds) is tuple
            and all(type(item) is str and item in _REPLAY_KINDS for item in self.replay_kinds)
            and all(_ref_tuple(items) for items in evidence_rows)
            and _ref_tuple(self.live_predecessor_evidence_refs)
            and type(self.selection_kind) is str
            and self.selection_kind in _SELECTION_KINDS
            and _ref_tuple(self.named_reported_comparator_refs)
            and _ref_tuple(self.omitted_schedule_refs)
            and _ref_or_not_applicable(self.coverage_and_uncertainty_ref)
            and type(self.status) is str
            and self.status in {"DEFINED", "NONSERIALIZABLE"}
        ):
            _formation_failure("AdmissibleComparatorSet")
        count = len(self.comparator_schedules)
        if not (
            len(self.comparator_orderings) == count
            and len(self.replay_kinds) == count
            and all(len(items) == count for items in evidence_rows)
        ):
            _formation_failure("AdmissibleComparatorSet")
        if len(self.live_predecessor_evidence_refs) != count:
            _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
        schedule_refs = tuple(_record_ref(item) for item in self.comparator_schedules)
        if len(schedule_refs) != len(set(schedule_refs)) or len(
            tuple(zip(schedule_refs, self.replay_kinds, strict=True))
        ) != len(set(zip(schedule_refs, self.replay_kinds, strict=True))):
            _formation_failure("AdmissibleComparatorSet")
        if self.status == "NONSERIALIZABLE":
            if not (
                self.selection_kind == "NONSERIALIZABLE"
                and count == 0
                and not self.named_reported_comparator_refs
                and not self.omitted_schedule_refs
                and type(self.coverage_and_uncertainty_ref) is ObjectRef
            ):
                _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
        else:
            if self.selection_kind == "NONSERIALIZABLE" or count == 0:
                _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
            if any(
                item.comparator_kind is not _scheduling.ComparatorKind.SEQUENTIAL_ORDER
                for item in self.comparator_schedules
            ):
                _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
            if any(
                item.baseline_state_ref != self.baseline_state_ref
                or item.boundary_ref != self.boundary_ref
                or item.horizon_ref != self.horizon_ref
                for item in self.comparator_schedules
            ):
                _failure(FailureCode.INCOMPATIBLE_BOUNDARY, "AdmissibleComparatorSet")
            action_set = set(self.action_refs)
            if any(
                len(order) != len(self.action_refs) or set(order) != action_set
                for order in self.comparator_orderings
            ):
                _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
            reported = self.named_reported_comparator_refs
            if any(item not in schedule_refs for item in reported):
                _failure(FailureCode.COMPARATOR_INTERACTION_INVALID, "AdmissibleComparatorSet")
            if self.selection_kind == "ORDER_INVARIANT_IDENTIFIER":
                if reported != (min(schedule_refs, key=_ref_key),):
                    _failure(
                        FailureCode.COMPARATOR_INTERACTION_INVALID,
                        "AdmissibleComparatorSet",
                    )
            elif self.selection_kind == "ALL_FEASIBLE_OR_EXACT_EXTREMA":
                if reported != schedule_refs:
                    _failure(
                        FailureCode.COMPARATOR_INTERACTION_INVALID,
                        "AdmissibleComparatorSet",
                    )
            elif self.selection_kind == "PREREGISTERED_LARGE_N_COVERAGE":
                if not self.omitted_schedule_refs or type(
                    self.coverage_and_uncertainty_ref
                ) is not ObjectRef:
                    _failure(
                        FailureCode.COMPARATOR_INTERACTION_INVALID,
                        "AdmissibleComparatorSet",
                    )
            elif not reported:
                _failure(FailureCode.MISSING_COMPARATOR, "AdmissibleComparatorSet")
        _validate_record_envelope(self, "AdmissibleComparatorSet")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class GroupMeasurement:
    envelope: CommonObjectEnvelope
    group_or_witness_ref: ObjectRef
    measurement_kind: Literal[
        "PHYSICAL_JOINT_GROUP", "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS"
    ]
    child_action_refs: tuple[ObjectRef, ...]
    before_state_ref: ObjectRef
    endpoint_state_ref: ObjectRef
    boundary_ref: ObjectRef
    distortion_model_ref: ObjectRef
    horizon_ref: ObjectRef
    initial_evaluation_ref: ObjectRef
    endpoint_evaluation_ref: ObjectRef
    initial_distortion: Quantity
    endpoint_distortion: Quantity
    ebu_value: Quantity
    physical_measurement_ref: ObjectRef | Applicability
    group_quote_ref: ObjectRef | Applicability
    group_quote_assumption_refs: tuple[ObjectRef, ...]
    nonadditivity_ref: ObjectRef | Applicability
    comparator_set_ref: ObjectRef | Applicability
    interaction_or_refusal_refs: tuple[ObjectRef, ...]
    causal_identification_protocol_ref: ObjectRef | Applicability
    causal_status: CausalIdentificationStatus | Applicability
    causal_evidence_refs: tuple[ObjectRef, ...]
    causal_contribution_refs: tuple[ObjectRef, ...]
    causal_remainder_ref: ObjectRef | Applicability
    settlement_rule_ref: ObjectRef | Applicability
    settlement_share_refs: tuple[ObjectRef, ...]
    settlement_share_values: tuple[Quantity, ...]
    settlement_residual_value: Quantity | Applicability
    settlement_residual_account_refs: tuple[ObjectRef, ...]
    settlement_validation_provenance_ref: ObjectRef | Applicability
    unresolved_effect_refs: tuple[ObjectRef, ...]
    later_measurement_horizon_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        scalar_refs = (
            self.group_or_witness_ref,
            self.before_state_ref,
            self.endpoint_state_ref,
            self.boundary_ref,
            self.distortion_model_ref,
            self.horizon_ref,
            self.initial_evaluation_ref,
            self.endpoint_evaluation_ref,
        )
        ref_or_na = (
            self.physical_measurement_ref,
            self.group_quote_ref,
            self.nonadditivity_ref,
            self.comparator_set_ref,
            self.causal_identification_protocol_ref,
            self.causal_remainder_ref,
            self.settlement_rule_ref,
            self.settlement_validation_provenance_ref,
        )
        ref_collections = (
            self.group_quote_assumption_refs,
            self.interaction_or_refusal_refs,
            self.causal_evidence_refs,
            self.causal_contribution_refs,
            self.settlement_share_refs,
            self.settlement_residual_account_refs,
            self.unresolved_effect_refs,
            self.later_measurement_horizon_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(item) is ObjectRef for item in scalar_refs)
            and type(self.measurement_kind) is str
            and self.measurement_kind in _MEASUREMENT_KINDS
            and _ordered_unique_refs(self.child_action_refs, nonempty=True)
            and all(type(item) is Quantity for item in (self.initial_distortion, self.endpoint_distortion, self.ebu_value))
            and all(_ref_or_not_applicable(item) for item in ref_or_na)
            and all(_ref_tuple(items) for items in ref_collections)
            and (
                type(self.causal_status) is CausalIdentificationStatus
                or self.causal_status is Applicability.NOT_APPLICABLE
            )
            and type(self.settlement_share_values) is tuple
            and all(type(item) is Quantity for item in self.settlement_share_values)
            and _quantity_or_not_applicable(self.settlement_residual_value)
        ):
            _formation_failure("GroupMeasurement")
        quantities = (
            self.initial_distortion,
            self.endpoint_distortion,
            self.ebu_value,
        )
        _quantity_contexts(quantities, "GroupMeasurement")
        if any(item.boundary_ref != self.boundary_ref for item in quantities):
            _failure(FailureCode.INCOMPATIBLE_BOUNDARY, "GroupMeasurement")
        if _core_fraction(self.ebu_value.magnitude) != (
            _core_fraction(self.initial_distortion.magnitude)
            - _core_fraction(self.endpoint_distortion.magnitude)
        ):
            _failure(FailureCode.DIAGNOSTIC_UNDEFINED, "GroupMeasurement")
        if self.measurement_kind == "PHYSICAL_JOINT_GROUP":
            if type(self.physical_measurement_ref) is not ObjectRef or type(
                self.causal_status
            ) is not CausalIdentificationStatus:
                _formation_failure("GroupMeasurement")
            if self.physical_measurement_ref in self.interaction_or_refusal_refs:
                _formation_failure("GroupMeasurement")
        else:
            if not (
                self.physical_measurement_ref is Applicability.NOT_APPLICABLE
                and self.causal_status is Applicability.NOT_APPLICABLE
                and self.causal_identification_protocol_ref
                is Applicability.NOT_APPLICABLE
                and not self.causal_evidence_refs
                and not self.causal_contribution_refs
                and self.causal_remainder_ref is Applicability.NOT_APPLICABLE
                and self.settlement_rule_ref is Applicability.NOT_APPLICABLE
                and not self.settlement_share_refs
                and not self.settlement_share_values
                and self.settlement_residual_value is Applicability.NOT_APPLICABLE
                and not self.settlement_residual_account_refs
                and self.settlement_validation_provenance_ref
                is Applicability.NOT_APPLICABLE
            ):
                _formation_failure("GroupMeasurement")
        if type(self.causal_status) is CausalIdentificationStatus:
            has_protocol = type(self.causal_identification_protocol_ref) is ObjectRef
            has_evidence = bool(self.causal_evidence_refs)
            if self.causal_status is CausalIdentificationStatus.IDENTIFIED:
                if (self.causal_contribution_refs or type(self.causal_remainder_ref) is ObjectRef) and not (
                    has_protocol and has_evidence
                ):
                    _failure(
                        FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED,
                        "GroupMeasurement",
                    )
            elif self.causal_status is CausalIdentificationStatus.PARTIALLY_IDENTIFIED:
                if self.causal_contribution_refs or not (
                    has_protocol
                    and has_evidence
                    and type(self.causal_remainder_ref) is ObjectRef
                ):
                    _failure(
                        FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED,
                        "GroupMeasurement",
                    )
            elif self.causal_contribution_refs or (
                type(self.causal_remainder_ref) is ObjectRef
                and not (has_protocol and has_evidence)
            ):
                _failure(
                    FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED,
                    "GroupMeasurement",
                )
        if set(self.causal_contribution_refs) & set(self.settlement_share_refs):
            _failure(FailureCode.CAUSAL_SETTLEMENT_CONFLATION, "GroupMeasurement")
        settlement_absent = (
            self.settlement_rule_ref is Applicability.NOT_APPLICABLE
            and not self.settlement_share_refs
            and not self.settlement_share_values
            and self.settlement_residual_value is Applicability.NOT_APPLICABLE
            and not self.settlement_residual_account_refs
            and self.settlement_validation_provenance_ref
            is Applicability.NOT_APPLICABLE
        )
        if not settlement_absent:
            if not (
                type(self.settlement_rule_ref) is ObjectRef
                and self.settlement_share_refs
                and len(self.settlement_share_refs) == len(self.settlement_share_values)
                and type(self.settlement_residual_value) is Quantity
                and self.settlement_residual_account_refs
                and type(self.settlement_validation_provenance_ref) is ObjectRef
            ):
                _failure(FailureCode.SETTLEMENT_CLOSURE_FAILURE, "GroupMeasurement")
            settlement_values = self.settlement_share_values + (
                self.settlement_residual_value,
                self.ebu_value,
            )
            _quantity_contexts(settlement_values, "GroupMeasurement")
            if sum(
                (_core_fraction(item.magnitude) for item in self.settlement_share_values),
                Fraction(0),
            ) + _core_fraction(self.settlement_residual_value.magnitude) != _core_fraction(
                self.ebu_value.magnitude
            ):
                _failure(FailureCode.SETTLEMENT_CLOSURE_FAILURE, "GroupMeasurement")
        linked_refs = tuple(
            item
            for items in ref_collections
            for item in items
        ) + tuple(item for item in ref_or_na if type(item) is ObjectRef)
        if any(
            str(item.object_id).endswith("-group-receipt") for item in linked_refs
        ):
            _formation_failure("GroupMeasurement")
        _validate_record_envelope(self, "GroupMeasurement")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SameBaselineNonadditivity:
    envelope: CommonObjectEnvelope
    group_or_witness_ref: ObjectRef
    physical_measurement_ref: ObjectRef | Applicability
    basis_kind: Literal[
        "PHYSICAL_JOINT_GROUP", "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS"
    ]
    action_refs: tuple[ObjectRef, ...]
    baseline_state_ref: ObjectRef
    boundary_ref: ObjectRef
    horizon_ref: ObjectRef
    standalone_endpoint_refs: tuple[ObjectRef, ...] | Applicability
    empty_baseline: Quantity | Applicability
    singleton_values: tuple[Quantity, ...] | Applicability
    joint_value: Quantity
    nonadditivity_value: Quantity | Applicability
    status: Literal["DEFINED", "UNDEFINED_NO_STANDALONE_CHILDREN"]
    d2_witness_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.group_or_witness_ref) is ObjectRef
            and _ref_or_not_applicable(self.physical_measurement_ref)
            and type(self.basis_kind) is str
            and self.basis_kind in _MEASUREMENT_KINDS
            and _ordered_unique_refs(self.action_refs, nonempty=True)
            and all(
                type(item) is ObjectRef
                for item in (
                    self.baseline_state_ref,
                    self.boundary_ref,
                    self.horizon_ref,
                )
            )
            and (
                _ref_tuple(self.standalone_endpoint_refs)
                or self.standalone_endpoint_refs is Applicability.NOT_APPLICABLE
            )
            and _quantity_or_not_applicable(self.empty_baseline)
            and (
                (
                    type(self.singleton_values) is tuple
                    and all(type(item) is Quantity for item in self.singleton_values)
                )
                or self.singleton_values is Applicability.NOT_APPLICABLE
            )
            and type(self.joint_value) is Quantity
            and _quantity_or_not_applicable(self.nonadditivity_value)
            and type(self.status) is str
            and self.status in _NONADDITIVITY_STATUSES
            and _ref_or_not_applicable(self.d2_witness_ref)
        ):
            _formation_failure("SameBaselineNonadditivity")
        if self.basis_kind == "PHYSICAL_JOINT_GROUP":
            if type(self.physical_measurement_ref) is not ObjectRef:
                _formation_failure("SameBaselineNonadditivity")
        elif self.physical_measurement_ref is not Applicability.NOT_APPLICABLE:
            _formation_failure("SameBaselineNonadditivity")
        if self.joint_value.boundary_ref != self.boundary_ref:
            _failure(FailureCode.INCOMPATIBLE_BOUNDARY, "SameBaselineNonadditivity")
        if self.status == "DEFINED":
            if not (
                type(self.standalone_endpoint_refs) is tuple
                and type(self.empty_baseline) is Quantity
                and type(self.singleton_values) is tuple
                and type(self.nonadditivity_value) is Quantity
                and type(self.d2_witness_ref) is ObjectRef
                and len(self.standalone_endpoint_refs) == len(self.action_refs)
                and len(self.singleton_values) == len(self.action_refs)
            ):
                _formation_failure("SameBaselineNonadditivity")
            quantities = (
                self.empty_baseline,
                *self.singleton_values,
                self.joint_value,
                self.nonadditivity_value,
            )
            _quantity_contexts(quantities, "SameBaselineNonadditivity")
            if _core_fraction(self.empty_baseline.magnitude) != 0:
                _failure(
                    FailureCode.COMPARATOR_INTERACTION_INVALID,
                    "SameBaselineNonadditivity",
                )
            expected = _core_fraction(self.joint_value.magnitude) - sum(
                (_core_fraction(item.magnitude) for item in self.singleton_values),
                Fraction(0),
            )
            if _core_fraction(self.nonadditivity_value.magnitude) != expected:
                _failure(
                    FailureCode.COMPARATOR_INTERACTION_INVALID,
                    "SameBaselineNonadditivity",
                )
        elif not (
            self.standalone_endpoint_refs is Applicability.NOT_APPLICABLE
            and self.empty_baseline is Applicability.NOT_APPLICABLE
            and self.singleton_values is Applicability.NOT_APPLICABLE
            and self.nonadditivity_value is Applicability.NOT_APPLICABLE
            and self.d2_witness_ref is Applicability.NOT_APPLICABLE
        ):
            _failure(FailureCode.DIAGNOSTIC_UNDEFINED, "SameBaselineNonadditivity")
        _validate_record_envelope(self, "SameBaselineNonadditivity")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ComparatorInteraction:
    envelope: CommonObjectEnvelope
    group_or_witness_ref: ObjectRef
    physical_measurement_ref: ObjectRef | Applicability
    comparison_kind: Literal[
        "PHYSICAL_GROUP_COMPARATOR", "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS"
    ]
    comparator_set_ref: ObjectRef
    comparator_schedule_ref: ObjectRef
    replay_kind: Literal["QUANTITY_FIXED", "RULE_REPLAYED"]
    ordering_refs: tuple[ObjectRef, ...]
    sequential_endpoint_ref: ObjectRef
    group_endpoint_ref: ObjectRef
    sequential_distortion: Quantity
    group_distortion: Quantity
    sequential_ebu: Quantity
    group_ebu: Quantity
    interaction_value: Quantity
    state_equivalence: bool
    ebu_equivalence: bool
    d2_witness_ref: ObjectRef

    def __post_init__(self) -> None:
        scalar_refs = (
            self.group_or_witness_ref,
            self.comparator_set_ref,
            self.comparator_schedule_ref,
            self.sequential_endpoint_ref,
            self.group_endpoint_ref,
            self.d2_witness_ref,
        )
        quantities = (
            self.sequential_distortion,
            self.group_distortion,
            self.sequential_ebu,
            self.group_ebu,
            self.interaction_value,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and _ref_or_not_applicable(self.physical_measurement_ref)
            and type(self.comparison_kind) is str
            and self.comparison_kind in _COMPARISON_KINDS
            and all(type(item) is ObjectRef for item in scalar_refs)
            and type(self.replay_kind) is str
            and self.replay_kind in _REPLAY_KINDS
            and _ref_tuple(self.ordering_refs)
            and bool(self.ordering_refs)
            and len(self.ordering_refs) == len(set(self.ordering_refs))
            and all(type(item) is Quantity for item in quantities)
            and type(self.state_equivalence) is bool
            and type(self.ebu_equivalence) is bool
        ):
            _formation_failure("ComparatorInteraction")
        if self.comparison_kind == "PHYSICAL_GROUP_COMPARATOR":
            if type(self.physical_measurement_ref) is not ObjectRef:
                _formation_failure("ComparatorInteraction")
        elif self.physical_measurement_ref is not Applicability.NOT_APPLICABLE:
            _formation_failure("ComparatorInteraction")
        _quantity_contexts(quantities, "ComparatorInteraction")
        interaction = _core_fraction(self.interaction_value.magnitude)
        if not (
            interaction
            == _core_fraction(self.group_ebu.magnitude)
            - _core_fraction(self.sequential_ebu.magnitude)
            == _core_fraction(self.sequential_distortion.magnitude)
            - _core_fraction(self.group_distortion.magnitude)
        ):
            _failure(
                FailureCode.COMPARATOR_INTERACTION_INVALID,
                "ComparatorInteraction",
            )
        if self.state_equivalence and (
            not self.ebu_equivalence or interaction != 0
        ):
            _failure(
                FailureCode.COMPARATOR_INTERACTION_INVALID,
                "ComparatorInteraction",
            )
        _validate_record_envelope(self, "ComparatorInteraction")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class NonserializableGroup:
    envelope: CommonObjectEnvelope
    group_ref: ObjectRef
    physical_measurement_ref: ObjectRef
    comparator_set_ref: ObjectRef
    action_refs: tuple[ObjectRef, ...]
    reason_refs: tuple[ObjectRef, ...]
    interaction_status: Literal["UNDEFINED"]
    serialized_interaction_value: Applicability
    refusal_code: Literal["NON_SERIALIZABLE"]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(item) is ObjectRef
                for item in (
                    self.group_ref,
                    self.physical_measurement_ref,
                    self.comparator_set_ref,
                )
            )
            and _ordered_unique_refs(self.action_refs, nonempty=True)
            and _ordered_unique_refs(self.reason_refs, nonempty=True)
            and type(self.interaction_status) is str
            and self.interaction_status == "UNDEFINED"
            and type(self.serialized_interaction_value) is Applicability
            and type(self.refusal_code) is str
            and self.refusal_code == "NON_SERIALIZABLE"
        ):
            _formation_failure("NonserializableGroup")
        if self.serialized_interaction_value is not Applicability.NOT_APPLICABLE:
            _failure(FailureCode.DIAGNOSTIC_UNDEFINED, "NonserializableGroup")
        _validate_record_envelope(self, "NonserializableGroup")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
    order=False,
    unsafe_hash=False,
    init=False,
)
class _BridgeExecutionPermit:
    lease_ref: ObjectRef
    operation: Literal[
        "classify_joint_groups",
        "compute_group_measurement",
        "compute_same_baseline_nonadditivity",
        "compute_comparator_interaction",
    ]
    issuance_nonce: object

    def __getattribute__(self, name: str) -> object:
        if name != "__class__":
            _failure(FailureCode.CAPABILITY_ESCALATION_FORBIDDEN, name)
        return object.__getattribute__(self, name)

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )

    def __copy__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )

    def __reduce__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )

    def __reduce_ex__(self, protocol: object) -> NoReturn:
        del protocol
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_BridgeExecutionPermit",
        )


def _consume_bridge_execution_permit(
    permit: _BridgeExecutionPermit,
    operation: Literal[
        "classify_joint_groups",
        "compute_group_measurement",
        "compute_same_baseline_nonadditivity",
        "compute_comparator_interaction",
    ],
    /,
) -> NoReturn:
    del permit
    _failure(FailureCode.CAPABILITY_ESCALATION_FORBIDDEN, operation)


def _validate_group_receipt_link(
    receipt: GroupReceipt,
    group: JointTransitionGroup,
    measurement: GroupMeasurement,
    /,
) -> None:
    if not (
        type(receipt) is GroupReceipt
        and type(group) is JointTransitionGroup
        and type(measurement) is GroupMeasurement
    ):
        _formation_failure("_validate_group_receipt_link")
    if not (
        receipt.before_state_ref == measurement.before_state_ref
        and receipt.after_state_ref == measurement.endpoint_state_ref
        and measurement.group_or_witness_ref == _record_ref(group)
    ):
        _failure(FailureCode.INCOMPATIBLE_BOUNDARY, "_validate_group_receipt_link")
    if receipt.group_ref != _record_ref(group):
        _failure(FailureCode.GROUPING_FAILURE, "_validate_group_receipt_link")
    if receipt.measurement_ref != _record_ref(measurement):
        _failure(FailureCode.GROUPING_FAILURE, "_validate_group_receipt_link")
    if tuple(receipt.child_receipt_refs) != tuple(
        sorted(receipt.child_receipt_refs, key=_ref_key)
    ) or len(receipt.child_receipt_refs) != len(group.child_action_refs):
        _failure(FailureCode.GROUPING_FAILURE, "_validate_group_receipt_link")
    try:
        _envelopes.validate_object_envelope(receipt.envelope)
    except FrameworkError:
        _formation_failure("_validate_group_receipt_link")
    if receipt.envelope.to_ecj1()["object_content_payload"] != receipt.to_ecj1():
        _formation_failure("_validate_group_receipt_link")
    return None


def _applicable(value: object) -> ObjectRef | Applicability:
    if value == Applicability.NOT_APPLICABLE.value:
        return Applicability.NOT_APPLICABLE
    return _object_ref(value)


def _object_ref(value: object) -> ObjectRef:
    if type(value) is not dict or set(value) != {
        "object_id",
        "object_version",
        "object_content_hash",
    }:
        _formation_failure("fixture_materialization")
    try:
        return ObjectRef(
            object_id=_identity.ScientificId(value["object_id"]),
            object_version=_identity.SemanticVersion(value["object_version"]),
            object_content_hash=_identity.ObjectContentHash(
                value["object_content_hash"]
            ),
        )
    except (FrameworkError, KeyError, TypeError):
        _formation_failure("fixture_materialization")


def _refs(value: object) -> tuple[ObjectRef, ...]:
    if type(value) is not list:
        _formation_failure("fixture_materialization")
    return tuple(_object_ref(item) for item in value)


def _core_number(value: object) -> _numeric.CoreNumberV1:
    if type(value) is not dict or type(value.get("variant")) is not str:
        _formation_failure("fixture_materialization")
    try:
        variant = value["variant"]
        if variant == "INTEGER_V1" and set(value) == {"value", "variant"}:
            return _numeric.IntegerV1(value["value"])
        if variant == "RATIONAL_V1" and set(value) == {
            "numerator",
            "denominator",
            "variant",
        }:
            return _numeric.RationalV1(
                _numeric.IntegerV1(value["numerator"]),
                _numeric.IntegerV1(value["denominator"]),
            )
        if variant == "DECIMAL_V1" and set(value) == {
            "coefficient",
            "exponent10",
            "variant",
        }:
            return _numeric.DecimalV1(
                _numeric.IntegerV1(value["coefficient"]),
                _numeric.IntegerV1(value["exponent10"]),
            )
        if variant == "BINARY64_BITS_V1" and set(value) == {"bits", "variant"}:
            return _numeric.Binary64BitsV1(value["bits"])
    except (FrameworkError, KeyError, TypeError):
        _formation_failure("fixture_materialization")
    _formation_failure("fixture_materialization")


def _resolution(value: object) -> _primitives.ResolutionDetail:
    if type(value) is not dict or value.get("schema_version") != 1:
        _formation_failure("fixture_materialization")
    failure = value.get("failure")
    if failure != Applicability.NOT_APPLICABLE.value:
        _formation_failure("fixture_materialization")
    try:
        result = _primitives.ResolutionDetail(
            state=_primitives.ResolutionState(value["state"]),
            present_value_ref=_applicable(value["present_value_ref"]),
            completed_part_refs=_refs(value["completed_part_refs"]),
            missing_part_refs=_refs(value["missing_part_refs"]),
            due_condition_ref=_applicable(value["due_condition_ref"]),
            failure=Applicability.NOT_APPLICABLE,
            boundary_edge_ref=_applicable(value["boundary_edge_ref"]),
            reason_ref=_applicable(value["reason_ref"]),
        )
    except (FrameworkError, KeyError, TypeError, ValueError):
        _formation_failure("fixture_materialization")
    if result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _quantity(value: object) -> Quantity:
    if type(value) is not dict or value.get("schema_version") != 1:
        _formation_failure("fixture_materialization")
    try:
        result = Quantity(
            magnitude=_core_number(value["magnitude"]),
            unit_ref=_object_ref(value["unit_ref"]),
            dimension_ref=_object_ref(value["dimension_ref"]),
            boundary_ref=_object_ref(value["boundary_ref"]),
            resource_type_ref=_applicable(value["resource_type_ref"]),
            service_type_ref=_applicable(value["service_type_ref"]),
            region_ref=_applicable(value["region_ref"]),
            time_basis_ref=_applicable(value["time_basis_ref"]),
            sign_convention_ref=_applicable(value["sign_convention_ref"]),
            uncertainty_ref=_applicable(value["uncertainty_ref"]),
            resolution=_resolution(value["resolution"]),
        )
    except (FrameworkError, KeyError, TypeError):
        _formation_failure("fixture_materialization")
    if result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _quantity_or_applicable(value: object) -> Quantity | Applicability:
    if value == Applicability.NOT_APPLICABLE.value:
        return Applicability.NOT_APPLICABLE
    return _quantity(value)


def _instant(value: object) -> _primitives.Instant:
    if type(value) is not dict or value.get("schema_version") != 1:
        _formation_failure("fixture_materialization")
    try:
        result = _primitives.Instant(
            clock_ref=_object_ref(value["clock_ref"]),
            tick=_core_number(value["tick"]),
        )
    except (FrameworkError, KeyError, TypeError):
        _formation_failure("fixture_materialization")
    if type(result.tick) is not _numeric.IntegerV1 or result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _effective_interval(value: object) -> EffectiveInterval:
    if type(value) is not dict:
        _formation_failure("fixture_materialization")
    try:
        result = EffectiveInterval(
            start=_instant(value["start"]),
            end=_instant(value["end"]),
            clock_ref=_object_ref(value["clock_ref"]),
        )
    except (FrameworkError, KeyError, TypeError):
        _formation_failure("fixture_materialization")
    if result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _write_support(value: object) -> WriteSupport:
    if type(value) is not dict:
        _formation_failure("fixture_materialization")
    result = WriteSupport(coordinate_refs=_refs(value.get("coordinate_refs")))
    if result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _constraint_support(value: object) -> ConstraintSupport:
    if type(value) is not dict:
        _formation_failure("fixture_materialization")
    result = ConstraintSupport(constraint_refs=_refs(value.get("constraint_refs")))
    if result.to_ecj1() != value:
        _formation_failure("fixture_materialization")
    return result


def _envelope(bundle: object) -> CommonObjectEnvelope:
    if type(bundle) is not dict or type(bundle.get("to_ecj1")) is not dict:
        _formation_failure("fixture_materialization")
    constructor = bundle.get("envelope_constructor")
    if type(constructor) is not dict:
        _formation_failure("fixture_materialization")
    payload = bundle["to_ecj1"]
    payload_bytes = _canonical.encode_ecj1(payload)
    payload_description = constructor.get("object_content_payload")
    if not (
        type(payload_description) is dict
        and payload_description.get("constructor") == "CanonicalBytes"
        and payload_description.get("ecj1_value") == payload
        and payload_description.get("byte_count") == len(payload_bytes)
        and payload_description.get("sha256")
        == hashlib.sha256(payload_bytes).hexdigest()
    ):
        _formation_failure("fixture_materialization")
    try:
        result = CommonObjectEnvelope(
            object_id=_identity.ScientificId(constructor["object_id"]),
            object_kind_id=_identity.ScientificId(constructor["object_kind_id"]),
            schema_id=_identity.ScientificId(constructor["schema_id"]),
            schema_version=_identity.SemanticVersion(constructor["schema_version"]),
            object_version=_identity.SemanticVersion(constructor["object_version"]),
            authority_refs=_refs(constructor["authority_refs"]),
            supersedes_ref=_applicable(constructor["supersedes_ref"]),
            object_content_payload=payload_bytes,
            object_content_hash=_identity.ObjectContentHash(
                constructor["object_content_hash"]
            ),
            lifecycle_status=_envelopes.LifecycleStatus(
                constructor["lifecycle_status"]
            ),
            record_metadata_ref=_applicable(constructor["record_metadata_ref"]),
        )
        _envelopes.validate_object_envelope(result)
    except (FrameworkError, KeyError, TypeError, ValueError):
        _formation_failure("fixture_materialization")
    expected_preimage = {
        "authority_refs": constructor["authority_refs"],
        "hash_domain": "ebu.object-content.v1",
        "object_content_payload": payload,
        "object_id": constructor["object_id"],
        "object_kind": constructor["object_kind_id"],
        "object_version": constructor["object_version"],
        "schema_id": constructor["schema_id"],
        "schema_version": constructor["schema_version"],
        "supersedes_ref": (
            None
            if constructor["supersedes_ref"] == Applicability.NOT_APPLICABLE.value
            else constructor["supersedes_ref"]
        ),
    }
    if bundle.get("object_content_hash_preimage") != expected_preimage:
        _formation_failure("fixture_materialization")
    if bundle.get("object_ref") != _record_ref_from_envelope(result).to_ecj1():
        _formation_failure("fixture_materialization")
    return result


def _record_ref_from_envelope(envelope: CommonObjectEnvelope) -> ObjectRef:
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _record_complete(record: object, bundle: object) -> object:
    if type(bundle) is not dict or record.to_ecj1() != bundle.get("to_ecj1"):  # type: ignore[union-attr]
        _formation_failure("fixture_materialization")
    if _record_ref(record).to_ecj1() != bundle.get("object_ref"):
        _formation_failure("fixture_materialization")
    return record


def _dependency_edge(bundle: object) -> DependencyEdge:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    return _record_complete(
        DependencyEdge(
            envelope=_envelope(bundle),
            left_action_ref=_object_ref(payload["left_action_ref"]),
            right_action_ref=_object_ref(payload["right_action_ref"]),
            left_effective_interval=_effective_interval(
                payload["left_effective_interval"]
            ),
            right_effective_interval=_effective_interval(
                payload["right_effective_interval"]
            ),
            dependency_kinds=tuple(payload["dependency_kinds"]),
            boundary_ref=_object_ref(payload["boundary_ref"]),
            declaration_ref=_object_ref(payload["declaration_ref"]),
        ),
        bundle,
    )  # type: ignore[return-value]


def _joint_group(bundle: object, edges: tuple[DependencyEdge, ...]) -> JointTransitionGroup:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = JointTransitionGroup(
        envelope=_envelope(bundle),
        child_action_refs=_refs(payload["child_action_refs"]),
        child_effective_intervals=tuple(
            (_object_ref(row[0]), _effective_interval(row[1]))
            for row in payload["child_effective_intervals"]
        ),
        child_write_supports=tuple(
            (_object_ref(row[0]), _write_support(row[1]))
            for row in payload["child_write_supports"]
        ),
        child_constraint_supports=tuple(
            (_object_ref(row[0]), _constraint_support(row[1]))
            for row in payload["child_constraint_supports"]
        ),
        child_commitment_refs=tuple(
            (_object_ref(row[0]), _refs(row[1]))
            for row in payload["child_commitment_refs"]
        ),
        accepted_quantity_refs=tuple(
            (_object_ref(row[0]), _refs(row[1]))
            for row in payload["accepted_quantity_refs"]
        ),
        dependency_edges=edges,
        dependency_relation_complete=payload["dependency_relation_complete"],
        separability_evidence_ref=_applicable(payload["separability_evidence_ref"]),
        common_before_state_ref=_object_ref(payload["common_before_state_ref"]),
        common_boundary_ref=_object_ref(payload["common_boundary_ref"]),
        common_distortion_model_ref=_object_ref(
            payload["common_distortion_model_ref"]
        ),
        common_horizon_ref=_object_ref(payload["common_horizon_ref"]),
        joint_write_support_ref=_object_ref(payload["joint_write_support_ref"]),
        joint_constraint_set_ref=_object_ref(payload["joint_constraint_set_ref"]),
        source_budget_account_ref=_object_ref(payload["source_budget_account_ref"]),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _comparator_schedule(bundle: object) -> ComparatorSchedule:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = ComparatorSchedule(
        envelope=_envelope(bundle),
        comparator_kind=_scheduling.ComparatorKind(payload["comparator_kind"]),
        schedule_ref=_object_ref(payload["schedule_ref"]),
        ordering_rule_ref=_object_ref(payload["ordering_rule_ref"]),
        baseline_state_ref=_object_ref(payload["baseline_state_ref"]),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _comparator_set(
    bundle: object, schedules: tuple[ComparatorSchedule, ...]
) -> AdmissibleComparatorSet:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = AdmissibleComparatorSet(
        envelope=_envelope(bundle),
        group_or_witness_ref=_object_ref(payload["group_or_witness_ref"]),
        action_refs=_refs(payload["action_refs"]),
        baseline_state_ref=_object_ref(payload["baseline_state_ref"]),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        distortion_model_ref=_object_ref(payload["distortion_model_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
        exogenous_drive_ref=_object_ref(payload["exogenous_drive_ref"]),
        comparator_schedules=schedules,
        comparator_orderings=tuple(
            _refs(item) for item in payload["comparator_orderings"]
        ),
        replay_kinds=tuple(payload["replay_kinds"]),
        same_children_commitments_evidence_refs=_refs(
            payload["same_children_commitments_evidence_refs"]
        ),
        live_predecessor_evidence_refs=_refs(
            payload["live_predecessor_evidence_refs"]
        ),
        feasibility_evidence_refs=_refs(payload["feasibility_evidence_refs"]),
        represented_effect_evidence_refs=_refs(
            payload["represented_effect_evidence_refs"]
        ),
        freeze_evidence_refs=_refs(payload["freeze_evidence_refs"]),
        selection_kind=payload["selection_kind"],
        named_reported_comparator_refs=_refs(
            payload["named_reported_comparator_refs"]
        ),
        omitted_schedule_refs=_refs(payload["omitted_schedule_refs"]),
        coverage_and_uncertainty_ref=_applicable(
            payload["coverage_and_uncertainty_ref"]
        ),
        status=payload["status"],
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _group_measurement(bundle: object) -> GroupMeasurement:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    causal_status = payload["causal_status"]
    result = GroupMeasurement(
        envelope=_envelope(bundle),
        group_or_witness_ref=_object_ref(payload["group_or_witness_ref"]),
        measurement_kind=payload["measurement_kind"],
        child_action_refs=_refs(payload["child_action_refs"]),
        before_state_ref=_object_ref(payload["before_state_ref"]),
        endpoint_state_ref=_object_ref(payload["endpoint_state_ref"]),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        distortion_model_ref=_object_ref(payload["distortion_model_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
        initial_evaluation_ref=_object_ref(payload["initial_evaluation_ref"]),
        endpoint_evaluation_ref=_object_ref(payload["endpoint_evaluation_ref"]),
        initial_distortion=_quantity(payload["initial_distortion"]),
        endpoint_distortion=_quantity(payload["endpoint_distortion"]),
        ebu_value=_quantity(payload["ebu_value"]),
        physical_measurement_ref=_applicable(payload["physical_measurement_ref"]),
        group_quote_ref=_applicable(payload["group_quote_ref"]),
        group_quote_assumption_refs=_refs(payload["group_quote_assumption_refs"]),
        nonadditivity_ref=_applicable(payload["nonadditivity_ref"]),
        comparator_set_ref=_applicable(payload["comparator_set_ref"]),
        interaction_or_refusal_refs=_refs(payload["interaction_or_refusal_refs"]),
        causal_identification_protocol_ref=_applicable(
            payload["causal_identification_protocol_ref"]
        ),
        causal_status=(
            Applicability.NOT_APPLICABLE
            if causal_status == Applicability.NOT_APPLICABLE.value
            else CausalIdentificationStatus(causal_status)
        ),
        causal_evidence_refs=_refs(payload["causal_evidence_refs"]),
        causal_contribution_refs=_refs(payload["causal_contribution_refs"]),
        causal_remainder_ref=_applicable(payload["causal_remainder_ref"]),
        settlement_rule_ref=_applicable(payload["settlement_rule_ref"]),
        settlement_share_refs=_refs(payload["settlement_share_refs"]),
        settlement_share_values=tuple(
            _quantity(item) for item in payload["settlement_share_values"]
        ),
        settlement_residual_value=_quantity_or_applicable(
            payload["settlement_residual_value"]
        ),
        settlement_residual_account_refs=_refs(
            payload["settlement_residual_account_refs"]
        ),
        settlement_validation_provenance_ref=_applicable(
            payload["settlement_validation_provenance_ref"]
        ),
        unresolved_effect_refs=_refs(payload["unresolved_effect_refs"]),
        later_measurement_horizon_refs=_refs(
            payload["later_measurement_horizon_refs"]
        ),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _d2_nonadditivity(bundle: object) -> SameBaselineNonadditivityWitness:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = SameBaselineNonadditivityWitness(
        envelope=_envelope(bundle),
        subset_protocol_ref=_object_ref(payload["subset_protocol_ref"]),
        action_refs=_refs(payload["action_refs"]),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
        empty_baseline=_quantity(payload["empty_baseline"]),
        joint_value=_quantity(payload["joint_value"]),
        singleton_values=tuple(
            (_object_ref(row[0]), _quantity(row[1]))
            for row in payload["singleton_values"]
        ),
        nonadditivity_value=_quantity(payload["nonadditivity_value"]),
        value_unit_ref=_object_ref(payload["value_unit_ref"]),
        value_dimension_ref=_object_ref(payload["value_dimension_ref"]),
        process_account_refs=_refs(payload["process_account_refs"]),
        claim_status=_primitives.ClaimStatus(payload["claim_status"]),
        nonclaim_codes=tuple(payload["nonclaim_codes"]),
        provenance_refs=_refs(payload["provenance_refs"]),
    )
    _interaction.validate_same_baseline_nonadditivity(result)
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _same_baseline_nonadditivity(bundle: object) -> SameBaselineNonadditivity:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    endpoint_refs = payload["standalone_endpoint_refs"]
    singleton_values = payload["singleton_values"]
    result = SameBaselineNonadditivity(
        envelope=_envelope(bundle),
        group_or_witness_ref=_object_ref(payload["group_or_witness_ref"]),
        physical_measurement_ref=_applicable(payload["physical_measurement_ref"]),
        basis_kind=payload["basis_kind"],
        action_refs=_refs(payload["action_refs"]),
        baseline_state_ref=_object_ref(payload["baseline_state_ref"]),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
        standalone_endpoint_refs=(
            Applicability.NOT_APPLICABLE
            if endpoint_refs == Applicability.NOT_APPLICABLE.value
            else _refs(endpoint_refs)
        ),
        empty_baseline=_quantity_or_applicable(payload["empty_baseline"]),
        singleton_values=(
            Applicability.NOT_APPLICABLE
            if singleton_values == Applicability.NOT_APPLICABLE.value
            else tuple(_quantity(item) for item in singleton_values)
        ),
        joint_value=_quantity(payload["joint_value"]),
        nonadditivity_value=_quantity_or_applicable(payload["nonadditivity_value"]),
        status=payload["status"],
        d2_witness_ref=_applicable(payload["d2_witness_ref"]),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _d2_interaction(bundle: object) -> SerialComparatorInteractionWitness:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = SerialComparatorInteractionWitness(
        envelope=_envelope(bundle),
        comparison_protocol_ref=_object_ref(payload["comparison_protocol_ref"]),
        action_refs=_refs(payload["action_refs"]),
        parallel_schedule_ref=_object_ref(payload["parallel_schedule_ref"]),
        serial_comparator_ref=_object_ref(payload["serial_comparator_ref"]),
        serial_order_refs=_refs(payload["serial_order_refs"]),
        initial_augmented_state_ref=_object_ref(
            payload["initial_augmented_state_ref"]
        ),
        boundary_ref=_object_ref(payload["boundary_ref"]),
        horizon_ref=_object_ref(payload["horizon_ref"]),
        exogenous_history_ref=_object_ref(payload["exogenous_history_ref"]),
        parallel_value=_quantity(payload["parallel_value"]),
        serial_value=_quantity(payload["serial_value"]),
        interaction_value=_quantity(payload["interaction_value"]),
        value_unit_ref=_object_ref(payload["value_unit_ref"]),
        value_dimension_ref=_object_ref(payload["value_dimension_ref"]),
        process_account_refs=_refs(payload["process_account_refs"]),
        claim_status=_primitives.ClaimStatus(payload["claim_status"]),
        nonclaim_codes=tuple(payload["nonclaim_codes"]),
        provenance_refs=_refs(payload["provenance_refs"]),
    )
    _interaction.validate_serial_comparator_interaction(result)
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _comparator_interaction(bundle: object) -> ComparatorInteraction:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = ComparatorInteraction(
        envelope=_envelope(bundle),
        group_or_witness_ref=_object_ref(payload["group_or_witness_ref"]),
        physical_measurement_ref=_applicable(payload["physical_measurement_ref"]),
        comparison_kind=payload["comparison_kind"],
        comparator_set_ref=_object_ref(payload["comparator_set_ref"]),
        comparator_schedule_ref=_object_ref(payload["comparator_schedule_ref"]),
        replay_kind=payload["replay_kind"],
        ordering_refs=_refs(payload["ordering_refs"]),
        sequential_endpoint_ref=_object_ref(payload["sequential_endpoint_ref"]),
        group_endpoint_ref=_object_ref(payload["group_endpoint_ref"]),
        sequential_distortion=_quantity(payload["sequential_distortion"]),
        group_distortion=_quantity(payload["group_distortion"]),
        sequential_ebu=_quantity(payload["sequential_ebu"]),
        group_ebu=_quantity(payload["group_ebu"]),
        interaction_value=_quantity(payload["interaction_value"]),
        state_equivalence=payload["state_equivalence"],
        ebu_equivalence=payload["ebu_equivalence"],
        d2_witness_ref=_object_ref(payload["d2_witness_ref"]),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _nonserializable_group(bundle: object) -> NonserializableGroup:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = NonserializableGroup(
        envelope=_envelope(bundle),
        group_ref=_object_ref(payload["group_ref"]),
        physical_measurement_ref=_object_ref(payload["physical_measurement_ref"]),
        comparator_set_ref=_object_ref(payload["comparator_set_ref"]),
        action_refs=_refs(payload["action_refs"]),
        reason_refs=_refs(payload["reason_refs"]),
        interaction_status=payload["interaction_status"],
        serialized_interaction_value=_applicable(
            payload["serialized_interaction_value"]
        ),
        refusal_code=payload["refusal_code"],
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _group_receipt(bundle: object) -> GroupReceipt:
    payload = bundle["to_ecj1"]  # type: ignore[index]
    result = GroupReceipt(
        envelope=_envelope(bundle),
        group_ref=_object_ref(payload["group_ref"]),
        child_receipt_refs=_refs(payload["child_receipt_refs"]),
        joint_transition_ref=_object_ref(payload["joint_transition_ref"]),
        before_state_ref=_object_ref(payload["before_state_ref"]),
        after_state_ref=_object_ref(payload["after_state_ref"]),
        measurement_ref=_object_ref(payload["measurement_ref"]),
        causal_status=CausalIdentificationStatus(payload["causal_status"]),
        settlement_ref=_applicable(payload["settlement_ref"]),
    )
    return _record_complete(result, bundle)  # type: ignore[return-value]


def _parse_fixture(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    interface: Literal[
        "classify_joint_groups_fixture",
        "compute_group_measurement_fixture",
        "compute_same_baseline_nonadditivity_fixture",
        "compute_comparator_interaction_fixture",
    ],
) -> tuple[dict[str, object], str]:
    if type(capability) is not T2FixtureCapability:
        _failure(FailureCode.CAPABILITY_ESCALATION_FORBIDDEN, interface)
    case_id = object.__getattribute__(capability, "case_id")
    _capabilities._consume_t2_fixture_capability(capability, interface, case_id)
    if type(fixture_case) is not bytes:
        _formation_failure(interface)
    raw = bytes(fixture_case)
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        _formation_failure(interface)
    try:
        document = _canonical.parse_ecj1(raw[:-1])
    except FrameworkError:
        _formation_failure(interface)
    if hashlib.sha256(raw).hexdigest() != _FIXTURE_SHA256:
        _failure(FailureCode.HASH_MISMATCH, interface)
    if _canonical.encode_ecj1(document) + b"\n" != raw:
        _formation_failure(interface)
    if not (
        type(document) is dict
        and document.get("fixture_id")
        == "bridge-m1-m9-v1"
        and document.get("fixture_version") == "1.0.0"
        and type(document.get("case_materializations")) is list
        and len(document["case_materializations"]) == 9
    ):
        _formation_failure(interface)
    matches = [
        row
        for row in document["case_materializations"]
        if type(row) is dict and row.get("case_id") == case_id
    ]
    if len(matches) != 1:
        _formation_failure(interface)
    return matches[0], case_id


def _materialize_fixture_case(case: dict[str, object]) -> dict[str, object]:
    edge_bundles = case.get("dependency_edge_records")
    schedule_bundles = case.get("comparator_schedule_records")
    interaction_bundles = case.get("comparator_interaction_records")
    d2_interaction_bundles = case.get("d2_interaction_witness_records")
    if not all(
        type(value) is list
        for value in (
            edge_bundles,
            schedule_bundles,
            interaction_bundles,
            d2_interaction_bundles,
        )
    ):
        _formation_failure("fixture_materialization")
    refusal_bundle = case.get("nonserializable_group_record")
    if (
        refusal_bundle != Applicability.NOT_APPLICABLE.value
        and schedule_bundles
    ):
        _failure(
            FailureCode.COMPARATOR_INTERACTION_INVALID,
            "NonserializableGroup",
        )
    edges = tuple(_dependency_edge(item) for item in edge_bundles)
    group_bundle = case.get("joint_group_record")
    group = (
        Applicability.NOT_APPLICABLE
        if group_bundle == Applicability.NOT_APPLICABLE.value
        else _joint_group(group_bundle, edges)
    )
    schedules = tuple(_comparator_schedule(item) for item in schedule_bundles)
    comparator_set = _comparator_set(
        case.get("admissible_comparator_set_record"), schedules
    )
    measurement = _group_measurement(case.get("group_measurement_record"))
    d2_nonadd_bundle = case.get("d2_nonadditivity_witness_record")
    d2_nonadditivity = (
        Applicability.NOT_APPLICABLE
        if d2_nonadd_bundle == Applicability.NOT_APPLICABLE.value
        else _d2_nonadditivity(d2_nonadd_bundle)
    )
    nonadditivity = _same_baseline_nonadditivity(
        case.get("same_baseline_nonadditivity_record")
    )
    d2_interactions = tuple(
        _d2_interaction(item) for item in d2_interaction_bundles
    )
    interactions = tuple(
        _comparator_interaction(item) for item in interaction_bundles
    )
    refusal = (
        Applicability.NOT_APPLICABLE
        if refusal_bundle == Applicability.NOT_APPLICABLE.value
        else _nonserializable_group(refusal_bundle)
    )
    receipt_bundle = case.get("accepted_group_receipt_record")
    receipt = (
        Applicability.NOT_APPLICABLE
        if receipt_bundle == Applicability.NOT_APPLICABLE.value
        else _group_receipt(receipt_bundle)
    )

    comparator_ref = _record_ref(comparator_set)
    if comparator_set.comparator_schedules != schedules:
        _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
    if nonadditivity.status == "DEFINED":
        if not (
            type(d2_nonadditivity) is SameBaselineNonadditivityWitness
            and nonadditivity.d2_witness_ref == _record_ref(d2_nonadditivity)
            and nonadditivity.action_refs == d2_nonadditivity.action_refs
            and nonadditivity.boundary_ref == d2_nonadditivity.boundary_ref
            and nonadditivity.horizon_ref == d2_nonadditivity.horizon_ref
            and _quantity_value_equal(
                nonadditivity.empty_baseline,
                d2_nonadditivity.empty_baseline,
            )
            and _quantity_value_equal(
                nonadditivity.joint_value,
                d2_nonadditivity.joint_value,
            )
            and _quantity_value_equal(
                nonadditivity.nonadditivity_value,
                d2_nonadditivity.nonadditivity_value,
            )
            and all(
                _quantity_value_equal(left, right)
                for left, right in zip(
                    nonadditivity.singleton_values,
                    (row[1] for row in d2_nonadditivity.singleton_values),
                    strict=True,
                )
            )
        ):
            _failure(
                FailureCode.COMPARATOR_INTERACTION_INVALID,
                "SameBaselineNonadditivity",
            )
    elif d2_nonadditivity is not Applicability.NOT_APPLICABLE:
        _failure(FailureCode.DIAGNOSTIC_UNDEFINED, "fixture_materialization")
    if len(interactions) != len(d2_interactions):
        _failure(
            FailureCode.COMPARATOR_INTERACTION_INVALID,
            "ComparatorInteraction",
        )
    if not all(
            interaction.d2_witness_ref == _record_ref(witness)
            and interaction.comparator_set_ref == comparator_ref
            and interaction.ordering_refs == witness.serial_order_refs
            and _quantity_value_equal(
                interaction.sequential_ebu, witness.serial_value
            )
            and _quantity_value_equal(interaction.group_ebu, witness.parallel_value)
            and _quantity_value_equal(
                interaction.interaction_value, witness.interaction_value
            )
            for interaction, witness in zip(interactions, d2_interactions, strict=True)
        ):
        _failure(
            FailureCode.COMPARATOR_INTERACTION_INVALID,
            "ComparatorInteraction",
        )
    schedule_rows = {
        _record_ref(schedule): (ordering, replay)
        for schedule, ordering, replay in zip(
            comparator_set.comparator_schedules,
            comparator_set.comparator_orderings,
            comparator_set.replay_kinds,
            strict=True,
        )
    }
    if any(
        schedule_rows.get(interaction.comparator_schedule_ref)
        != (interaction.ordering_refs, interaction.replay_kind)
        for interaction in interactions
    ):
        _failure(FailureCode.MISSING_COMPARATOR, "ComparatorInteraction")
    linked_results = (
        tuple(_record_ref(item) for item in interactions)
        if refusal is Applicability.NOT_APPLICABLE
        else (_record_ref(refusal),)
    )
    if measurement.interaction_or_refusal_refs != linked_results:
        _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
    if measurement.comparator_set_ref != comparator_ref:
        _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
    if measurement.nonadditivity_ref != _record_ref(nonadditivity):
        _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
    if type(group) is JointTransitionGroup:
        if not (
            measurement.group_or_witness_ref == _record_ref(group)
            and comparator_set.group_or_witness_ref == _record_ref(group)
            and nonadditivity.group_or_witness_ref == _record_ref(group)
            and type(receipt) is GroupReceipt
        ):
            _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
        _validate_group_receipt_link(receipt, group, measurement)
    elif receipt is not Applicability.NOT_APPLICABLE:
        _failure(FailureCode.GROUPING_FAILURE, "fixture_materialization")
    if type(refusal) is NonserializableGroup and not (
        refusal.comparator_set_ref == comparator_ref
        and type(group) is JointTransitionGroup
        and refusal.group_ref == _record_ref(group)
        and comparator_set.status == "NONSERIALIZABLE"
        and not schedules
    ):
        _failure(
            FailureCode.COMPARATOR_INTERACTION_INVALID,
            "NonserializableGroup",
        )
    return {
        "edges": edges,
        "group": group,
        "schedules": schedules,
        "comparator_set": comparator_set,
        "measurement": measurement,
        "d2_nonadditivity": d2_nonadditivity,
        "nonadditivity": nonadditivity,
        "d2_interactions": d2_interactions,
        "interactions": interactions,
        "refusal": refusal,
        "receipt": receipt,
    }


def _validate_fixture_output(
    case: dict[str, object], interface: str, expected: object, /
) -> None:
    outputs = case.get("interface_expected_outputs")
    if type(outputs) is not dict or outputs.get(interface) != expected:
        _formation_failure(interface)
    return None


def classify_joint_groups_fixture(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    /,
) -> tuple[JointTransitionGroup, ...]:
    case, _ = _parse_fixture(
        fixture_case, capability, "classify_joint_groups_fixture"
    )
    graph = _materialize_fixture_case(case)
    group = graph["group"]
    _validate_fixture_output(
        case,
        "classify_joint_groups_fixture",
        []
        if group is Applicability.NOT_APPLICABLE
        else [case["joint_group_record"]],
    )
    return () if group is Applicability.NOT_APPLICABLE else (group,)  # type: ignore[return-value]


def compute_group_measurement_fixture(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    /,
) -> GroupMeasurement:
    case, _ = _parse_fixture(
        fixture_case, capability, "compute_group_measurement_fixture"
    )
    graph = _materialize_fixture_case(case)
    _validate_fixture_output(
        case,
        "compute_group_measurement_fixture",
        case.get("group_measurement_record"),
    )
    return graph["measurement"]  # type: ignore[return-value]


def compute_same_baseline_nonadditivity_fixture(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    /,
) -> SameBaselineNonadditivity:
    case, _ = _parse_fixture(
        fixture_case,
        capability,
        "compute_same_baseline_nonadditivity_fixture",
    )
    graph = _materialize_fixture_case(case)
    _validate_fixture_output(
        case,
        "compute_same_baseline_nonadditivity_fixture",
        case.get("same_baseline_nonadditivity_record"),
    )
    return graph["nonadditivity"]  # type: ignore[return-value]


def compute_comparator_interaction_fixture(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    /,
) -> tuple[ComparatorInteraction, ...] | NonserializableGroup:
    case, _ = _parse_fixture(
        fixture_case,
        capability,
        "compute_comparator_interaction_fixture",
    )
    graph = _materialize_fixture_case(case)
    refusal = graph["refusal"]
    if type(refusal) is NonserializableGroup:
        _validate_fixture_output(
            case,
            "compute_comparator_interaction_fixture",
            case.get("nonserializable_group_record"),
        )
        return refusal
    _validate_fixture_output(
        case,
        "compute_comparator_interaction_fixture",
        case.get("comparator_interaction_records"),
    )
    return graph["interactions"]  # type: ignore[return-value]


def classify_joint_groups(
    actions: tuple[ActionInstance, ...],
    declared_edges: tuple[DependencyEdge, ...],
    declared_groups: tuple[JointTransitionGroup, ...],
    dependency_relation_complete: bool,
    separability_evidence_refs: tuple[ObjectRef, ...],
    permit: _BridgeExecutionPermit,
    /,
) -> tuple[JointTransitionGroup, ...]:
    _consume_bridge_execution_permit(permit, "classify_joint_groups")


def compute_group_measurement(
    group: JointTransitionGroup,
    before: RepresentedState,
    after: RepresentedState,
    distortion: DistortionModel,
    initial_distortion: Quantity,
    endpoint_distortion: Quantity,
    initial_evaluation_ref: ObjectRef,
    endpoint_evaluation_ref: ObjectRef,
    physical_measurement_ref: ObjectRef,
    group_measurement_envelope: CommonObjectEnvelope,
    group_quote_ref: ObjectRef | Applicability,
    group_quote_assumption_refs: tuple[ObjectRef, ...],
    nonadditivity_ref: ObjectRef | Applicability,
    comparator_set_ref: ObjectRef | Applicability,
    interaction_or_refusal_refs: tuple[ObjectRef, ...],
    causal_identification_protocol_ref: ObjectRef | Applicability,
    causal_status: CausalIdentificationStatus,
    causal_evidence_refs: tuple[ObjectRef, ...],
    causal_contribution_refs: tuple[ObjectRef, ...],
    causal_remainder_ref: ObjectRef | Applicability,
    settlement_rule_ref: ObjectRef | Applicability,
    settlement_share_refs: tuple[ObjectRef, ...],
    settlement_share_values: tuple[Quantity, ...],
    settlement_residual_value: Quantity | Applicability,
    settlement_residual_account_refs: tuple[ObjectRef, ...],
    settlement_validation_provenance_ref: ObjectRef | Applicability,
    unresolved_effect_refs: tuple[ObjectRef, ...],
    later_measurement_horizon_refs: tuple[ObjectRef, ...],
    permit: _BridgeExecutionPermit,
    /,
) -> GroupMeasurement:
    _consume_bridge_execution_permit(permit, "compute_group_measurement")


def compute_same_baseline_nonadditivity(
    group_or_witness_ref: ObjectRef,
    physical_measurement_ref: ObjectRef | Applicability,
    basis_kind: Literal[
        "PHYSICAL_JOINT_GROUP", "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS"
    ],
    action_refs: tuple[ObjectRef, ...],
    baseline_state_ref: ObjectRef,
    boundary_ref: ObjectRef,
    horizon_ref: ObjectRef,
    standalone_endpoint_refs: tuple[ObjectRef, ...] | Applicability,
    empty_baseline: Quantity | Applicability,
    singleton_values: tuple[Quantity, ...] | Applicability,
    joint_value: Quantity,
    d2_witness: SameBaselineNonadditivityWitness | Applicability,
    d2_witness_ref: ObjectRef | Applicability,
    nonadditivity_envelope: CommonObjectEnvelope,
    permit: _BridgeExecutionPermit,
    /,
) -> SameBaselineNonadditivity:
    _consume_bridge_execution_permit(
        permit, "compute_same_baseline_nonadditivity"
    )


def compute_comparator_interaction(
    group_or_witness_ref: ObjectRef,
    physical_measurement_ref: ObjectRef | Applicability,
    comparison_kind: Literal[
        "PHYSICAL_GROUP_COMPARATOR",
        "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS",
    ],
    comparator_set: AdmissibleComparatorSet,
    group_endpoint: RepresentedState,
    group_distortion: Quantity,
    group_ebu: Quantity,
    sequential_endpoints: tuple[RepresentedState, ...] | Applicability,
    sequential_distortions: tuple[Quantity, ...] | Applicability,
    sequential_values: tuple[Quantity, ...] | Applicability,
    d2_witnesses: tuple[SerialComparatorInteractionWitness, ...] | Applicability,
    d2_witness_refs: tuple[ObjectRef, ...] | Applicability,
    result_envelopes: tuple[CommonObjectEnvelope, ...],
    nonserializable_envelope: CommonObjectEnvelope | Applicability,
    permit: _BridgeExecutionPermit,
    /,
) -> tuple[ComparatorInteraction, ...] | NonserializableGroup:
    _consume_bridge_execution_permit(permit, "compute_comparator_interaction")


__all__ = (
    "DependencyEdge",
    "JointTransitionGroup",
    "AdmissibleComparatorSet",
    "GroupMeasurement",
    "SameBaselineNonadditivity",
    "ComparatorInteraction",
    "NonserializableGroup",
    "classify_joint_groups_fixture",
    "classify_joint_groups",
    "compute_group_measurement_fixture",
    "compute_group_measurement",
    "compute_same_baseline_nonadditivity_fixture",
    "compute_same_baseline_nonadditivity",
    "compute_comparator_interaction_fixture",
    "compute_comparator_interaction",
)
