"""Inert Framework I-7 dynamic declarations and synthetic validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, NoReturn

from . import network as _network
from . import commitments as _commitments
from . import scheduling as _scheduling
from . import policy as _policy
from . import events as _events
from . import ownership as _ownership
from . import state as _state
from . import primitives as _primitives
from . import identity as _identity
from . import envelopes as _envelopes
from . import canonical as _canonical
from . import capabilities as _capabilities
from . import errors as _errors


Applicability = _errors.Applicability
CanonicalBytes = _canonical.CanonicalBytes
CommonObjectEnvelope = _envelopes.CommonObjectEnvelope
Duration = _primitives.Duration
Epoch = _primitives.Epoch
FailureCode = _errors.FailureCode
FrameworkError = _errors.FrameworkError
ObjectRef = _identity.ObjectRef
PhaseOrdinal = _events.PhaseOrdinal
Quantity = _primitives.Quantity
RoutePlan = _network.RoutePlan
T2FixtureCapability = _capabilities.T2FixtureCapability
TopologyChangeEvent = _network.TopologyChangeEvent


def _interface(name: str) -> _errors.FailureInterfaceRef:
    return _errors.FailureInterfaceRef("ebu_framework.dynamic", name, "1.0.0")


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _errors._fail(
        code,
        f"{interface} rejected {code.value}",
        stage=_errors.FailureStage.I7,
        interface_ref=_interface(interface),
        scientific_status_effect=_errors.ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=_errors.RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I7_RECORD_FORMATION_INVALID, interface)


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


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_unique_refs(values: tuple[ObjectRef, ...], *, nonempty: bool = False) -> bool:
    if nonempty and not values:
        return False
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _project(value: object) -> object:
    if type(value) is Applicability:
        return value.value
    if type(value) is PhaseOrdinal:
        return value.value
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _content_hash_check(record: object, interface: str) -> None:
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _failure(FailureCode.HASH_MISMATCH, interface)
    try:
        _envelopes.validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        _failure(FailureCode.HASH_MISMATCH, interface)


def _quantity_fraction(quantity: Quantity):
    return _commitments._core_fraction(quantity.magnitude)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class DelayRecord:
    envelope: CommonObjectEnvelope
    subject_ref: ObjectRef
    dispatch_epoch: Epoch
    arrival_epoch: Epoch
    base_delay: Duration | Applicability
    queue_delay: Duration | Applicability
    processing_delay: Duration | Applicability
    failure_delay: Duration | Applicability
    total_delay: Duration
    decomposition_kind: Literal[
        "NONOVERLAPPING_ADDITIVE_COMPONENTS",
        "TOTAL_ONLY_WITH_CAUSE_ANNOTATIONS",
    ]
    cause_annotation_refs: tuple[ObjectRef, ...]
    event_convention_ref: ObjectRef
    numerical_policy_ref: ObjectRef
    domain_authority_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.subject_ref) is ObjectRef
            and type(self.dispatch_epoch) is Epoch
            and type(self.arrival_epoch) is Epoch
            and all(
                type(value) is Duration or type(value) is Applicability
                for value in (
                    self.base_delay,
                    self.queue_delay,
                    self.processing_delay,
                    self.failure_delay,
                )
            )
            and type(self.total_delay) is Duration
            and type(self.decomposition_kind) is str
            and self.decomposition_kind
            in {
                "NONOVERLAPPING_ADDITIVE_COMPONENTS",
                "TOTAL_ONLY_WITH_CAUSE_ANNOTATIONS",
            }
            and _object_ref_tuple(self.cause_annotation_refs)
            and all(
                type(value) is ObjectRef
                for value in (
                    self.event_convention_ref,
                    self.numerical_policy_ref,
                    self.domain_authority_ref,
                )
            )
        ):
            _formation_failure("DelayRecord")
        _validate_delay_record(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class InTransitRecord:
    envelope: CommonObjectEnvelope
    payload_ref: ObjectRef
    originating_action_ref: ObjectRef
    route_plan_ref: ObjectRef
    completed_segment_refs: tuple[ObjectRef, ...]
    unfinished_suffix_refs: tuple[ObjectRef, ...]
    dispatch_epoch: Epoch
    expected_arrival_epoch: Epoch
    current_locus_ref: ObjectRef
    quantity: Quantity
    status: Literal["IN_TRANSIT", "STRANDED", "ARRIVED", "LOST"]
    topology_snapshot_ref: ObjectRef
    delay_record_ref: ObjectRef
    completion_or_loss_ref: ObjectRef | Applicability
    provenance_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.payload_ref,
                    self.originating_action_ref,
                    self.route_plan_ref,
                    self.current_locus_ref,
                    self.topology_snapshot_ref,
                    self.delay_record_ref,
                    self.provenance_ref,
                )
            )
            and _object_ref_tuple(self.completed_segment_refs)
            and _object_ref_tuple(self.unfinished_suffix_refs)
            and type(self.dispatch_epoch) is Epoch
            and type(self.expected_arrival_epoch) is Epoch
            and type(self.quantity) is Quantity
            and type(self.status) is str
            and self.status in {"IN_TRANSIT", "STRANDED", "ARRIVED", "LOST"}
            and _object_or_applicability(self.completion_or_loss_ref)
        ):
            _formation_failure("InTransitRecord")
        _validate_in_transit_record(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class DelayedEffect:
    envelope: CommonObjectEnvelope
    originating_action_ref: ObjectRef
    effect_kind_ref: ObjectRef
    due_epoch: Epoch
    payload_or_transformation_ref: ObjectRef
    destination_coordinate_ref: ObjectRef
    status: Literal["MATURED", "PENDING", "CANCELLED", "FAILED", "UNRESOLVED"]
    represented_in_state_ref: ObjectRef | Applicability
    maturity_record_ref: ObjectRef | Applicability
    cancellation_rule_ref: ObjectRef | Applicability
    failure_consequence_ref: ObjectRef | Applicability
    measurement_obligation_ref: ObjectRef | Applicability
    provenance_ref: ObjectRef
    causal_identification_protocol_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.originating_action_ref,
                    self.effect_kind_ref,
                    self.payload_or_transformation_ref,
                    self.destination_coordinate_ref,
                    self.provenance_ref,
                )
            )
            and type(self.due_epoch) is Epoch
            and type(self.status) is str
            and self.status
            in {"MATURED", "PENDING", "CANCELLED", "FAILED", "UNRESOLVED"}
            and all(
                _object_or_applicability(value)
                for value in (
                    self.represented_in_state_ref,
                    self.maturity_record_ref,
                    self.cancellation_rule_ref,
                    self.failure_consequence_ref,
                    self.measurement_obligation_ref,
                    self.causal_identification_protocol_ref,
                )
            )
        ):
            _formation_failure("DelayedEffect")
        _validate_delayed_effect(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class DynamicUpdateRecord:
    envelope: CommonObjectEnvelope
    epoch: Epoch
    phase_ordinal: PhaseOrdinal
    predecessor_state_ref: ObjectRef
    successor_state_ref: ObjectRef | Applicability
    x_update_refs: tuple[ObjectRef, ...]
    g_update_refs: tuple[ObjectRef, ...]
    q_update_refs: tuple[ObjectRef, ...]
    c_update_refs: tuple[ObjectRef, ...]
    ell_update_refs: tuple[ObjectRef, ...]
    matured_effect_refs: tuple[ObjectRef, ...]
    topology_change_refs: tuple[ObjectRef, ...]
    admission_decision_refs: tuple[ObjectRef, ...]
    queue_record_refs: tuple[ObjectRef, ...]
    reservation_shortfall_refs: tuple[ObjectRef, ...]
    congestion_record_refs: tuple[ObjectRef, ...]
    delay_record_refs: tuple[ObjectRef, ...]
    in_transit_record_refs: tuple[ObjectRef, ...]
    delayed_effect_refs: tuple[ObjectRef, ...]
    policy_memory_before_ref: ObjectRef | Applicability
    policy_memory_after_ref: ObjectRef | Applicability
    policy_decision_ref: ObjectRef | Applicability
    augmented_replay_state_ref: ObjectRef | Applicability
    commitment_snapshot_before_ref: ObjectRef
    commitment_snapshot_after_ref: ObjectRef | Applicability
    ownership_ref: ObjectRef
    physical_commit_ref: ObjectRef | Applicability
    status: Literal["PROPOSED", "COMMITTED", "REFUSED"]

    def __post_init__(self) -> None:
        collections = (
            self.x_update_refs,
            self.g_update_refs,
            self.q_update_refs,
            self.c_update_refs,
            self.ell_update_refs,
            self.matured_effect_refs,
            self.topology_change_refs,
            self.admission_decision_refs,
            self.queue_record_refs,
            self.reservation_shortfall_refs,
            self.congestion_record_refs,
            self.delay_record_refs,
            self.in_transit_record_refs,
            self.delayed_effect_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.epoch) is Epoch
            and type(self.phase_ordinal) is PhaseOrdinal
            and type(self.predecessor_state_ref) is ObjectRef
            and all(_object_ref_tuple(values) for values in collections)
            and all(
                _object_or_applicability(value)
                for value in (
                    self.successor_state_ref,
                    self.policy_memory_before_ref,
                    self.policy_memory_after_ref,
                    self.policy_decision_ref,
                    self.augmented_replay_state_ref,
                    self.commitment_snapshot_after_ref,
                    self.physical_commit_ref,
                )
            )
            and type(self.commitment_snapshot_before_ref) is ObjectRef
            and type(self.ownership_ref) is ObjectRef
            and type(self.status) is str
            and self.status in {"PROPOSED", "COMMITTED", "REFUSED"}
        ):
            _formation_failure("DynamicUpdateRecord")
        _validate_dynamic_update(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class NaturalDriveContract:
    envelope: CommonObjectEnvelope
    epoch: Epoch
    phase_ordinal: PhaseOrdinal
    model_ref: ObjectRef
    predecessor_state_ref: ObjectRef
    exogenous_input_refs: tuple[ObjectRef, ...]
    typed_balance_term_refs: tuple[ObjectRef, ...]
    proposed_update_ref: ObjectRef
    ownership_ref: ObjectRef
    numerical_policy_ref: ObjectRef
    domain_authority_ref: ObjectRef
    semantics_status: Literal["DOMAIN_DECLARED_PROPOSAL_ONLY"]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.epoch) is Epoch
            and type(self.phase_ordinal) is PhaseOrdinal
            and all(
                type(value) is ObjectRef
                for value in (
                    self.model_ref,
                    self.predecessor_state_ref,
                    self.proposed_update_ref,
                    self.ownership_ref,
                    self.numerical_policy_ref,
                    self.domain_authority_ref,
                )
            )
            and _object_ref_tuple(self.exogenous_input_refs)
            and _object_ref_tuple(self.typed_balance_term_refs)
            and type(self.semantics_status) is str
            and self.semantics_status == "DOMAIN_DECLARED_PROPOSAL_ONLY"
        ):
            _formation_failure("NaturalDriveContract")
        _validate_natural_drive(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


def _validate_delay_record(record: DelayRecord, /) -> None:
    interface = "DelayRecord"
    if type(record) is not DelayRecord:
        _formation_failure(interface)
    components = (
        record.base_delay,
        record.queue_delay,
        record.processing_delay,
        record.failure_delay,
    )
    clocks_valid = (
        record.dispatch_epoch.clock_ref == record.arrival_epoch.clock_ref
        == record.total_delay.clock_ref
    )
    arrival_valid = (
        record.arrival_epoch.index.value
        == record.dispatch_epoch.index.value + record.total_delay.ticks.value
    )
    if record.decomposition_kind == "NONOVERLAPPING_ADDITIVE_COMPONENTS":
        decomposition_valid = all(type(value) is Duration for value in components)
        if decomposition_valid:
            decomposition_valid = (
                all(value.clock_ref == record.total_delay.clock_ref for value in components)  # type: ignore[union-attr]
                and all(value.ticks.value >= 0 for value in components)  # type: ignore[union-attr]
                and sum(value.ticks.value for value in components)  # type: ignore[union-attr]
                == record.total_delay.ticks.value
            )
    else:
        decomposition_valid = (
            all(value is Applicability.NOT_APPLICABLE for value in components)
            and _ordered_unique_refs(record.cause_annotation_refs, nonempty=True)
        )
    if not (
        clocks_valid
        and record.total_delay.ticks.value >= 0
        and arrival_valid
        and decomposition_valid
        and _ordered_unique_refs(record.cause_annotation_refs)
    ):
        _failure(FailureCode.DELAY_DECOMPOSITION_INVALID, interface)
    _content_hash_check(record, interface)
    return None


def _validate_in_transit_record(record: InTransitRecord, /) -> None:
    interface = "InTransitRecord"
    if type(record) is not InTransitRecord:
        _formation_failure(interface)
    quantity = _quantity_fraction(record.quantity)
    status_valid = (
        record.status in {"IN_TRANSIT", "STRANDED"}
        and quantity > 0
        and record.completion_or_loss_ref is Applicability.NOT_APPLICABLE
    ) or (
        record.status in {"ARRIVED", "LOST"}
        and type(record.completion_or_loss_ref) is ObjectRef
        and quantity >= 0
    )
    if not (
        record.dispatch_epoch.clock_ref == record.expected_arrival_epoch.clock_ref
        and record.expected_arrival_epoch.index.value
        >= record.dispatch_epoch.index.value
        and status_valid
        and _ordered_unique_refs(record.completed_segment_refs)
        and _ordered_unique_refs(record.unfinished_suffix_refs)
    ):
        _failure(FailureCode.IN_TRANSIT_STATE_INVALID, interface)
    if set(record.completed_segment_refs).intersection(record.unfinished_suffix_refs):
        _failure(FailureCode.COMPLETED_ROUTE_REWRITE_FORBIDDEN, interface)
    _content_hash_check(record, interface)
    return None


def _validate_delayed_effect(record: DelayedEffect, /) -> None:
    interface = "DelayedEffect"
    if type(record) is not DelayedEffect:
        _formation_failure(interface)
    na = Applicability.NOT_APPLICABLE
    represented = record.represented_in_state_ref
    maturity = record.maturity_record_ref
    cancellation = record.cancellation_rule_ref
    consequence = record.failure_consequence_ref
    arms = {
        "MATURED": (
            type(represented) is ObjectRef
            and type(maturity) is ObjectRef
            and cancellation is na
            and consequence is na
        ),
        "PENDING": represented is na and maturity is na and cancellation is na and consequence is na,
        "CANCELLED": (
            represented is na
            and maturity is na
            and type(cancellation) is ObjectRef
            and consequence is na
        ),
        "FAILED": (
            represented is na
            and maturity is na
            and cancellation is na
            and type(consequence) is ObjectRef
        ),
        "UNRESOLVED": represented is na and maturity is na and cancellation is na and consequence is na,
    }
    if not arms[record.status]:
        _failure(FailureCode.DELAYED_EFFECT_STATUS_INVALID, interface)
    if record.causal_identification_protocol_ref is Applicability.APPLICABLE:
        _failure(FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED, interface)
    _content_hash_check(record, interface)
    return None


def _validate_dynamic_update(record: DynamicUpdateRecord, /) -> None:
    interface = "DynamicUpdateRecord"
    if type(record) is not DynamicUpdateRecord:
        _formation_failure(interface)
    components = (
        record.x_update_refs,
        record.g_update_refs,
        record.q_update_refs,
        record.c_update_refs,
        record.ell_update_refs,
    )
    other_collections = (
        record.matured_effect_refs,
        record.topology_change_refs,
        record.admission_decision_refs,
        record.queue_record_refs,
        record.reservation_shortfall_refs,
        record.congestion_record_refs,
        record.delay_record_refs,
        record.in_transit_record_refs,
        record.delayed_effect_refs,
    )
    if not any(components) or any(
        not _ordered_unique_refs(values) for values in components + other_collections
    ):
        _failure(FailureCode.DYNAMIC_STATE_INCOMPLETE, interface)
    flattened = tuple(reference for values in components for reference in values)
    if len(flattened) != len(set(flattened)):
        _failure(FailureCode.UPDATE_DOUBLE_APPLICATION_FORBIDDEN, interface)
    memory_refs = (
        record.policy_memory_before_ref,
        record.policy_memory_after_ref,
        record.policy_decision_ref,
        record.augmented_replay_state_ref,
    )
    if not (
        all(value is Applicability.NOT_APPLICABLE for value in memory_refs)
        or all(type(value) is ObjectRef for value in memory_refs)
    ):
        _failure(FailureCode.POLICY_MEMORY_PAIR_MISMATCH, interface)
    commitment_pair_valid = (
        record.phase_ordinal is PhaseOrdinal.PHASE_9
        and bool(record.c_update_refs)
        and type(record.commitment_snapshot_after_ref) is ObjectRef
    ) or (
        not (
            record.phase_ordinal is PhaseOrdinal.PHASE_9
            and bool(record.c_update_refs)
        )
        and record.commitment_snapshot_after_ref
        is Applicability.NOT_APPLICABLE
    )
    if not commitment_pair_valid:
        _failure(FailureCode.COMMITMENT_STATE_MISMATCH, interface)
    status_valid = (
        record.status == "COMMITTED"
        and type(record.successor_state_ref) is ObjectRef
        and type(record.physical_commit_ref) is ObjectRef
    ) or (
        record.status in {"PROPOSED", "REFUSED"}
        and record.successor_state_ref is Applicability.NOT_APPLICABLE
        and record.physical_commit_ref is Applicability.NOT_APPLICABLE
    )
    if not status_valid:
        _failure(FailureCode.DYNAMIC_STATE_INCOMPLETE, interface)
    _content_hash_check(record, interface)
    return None


def _validate_natural_drive(record: NaturalDriveContract, /) -> None:
    interface = "NaturalDriveContract"
    if type(record) is not NaturalDriveContract:
        _formation_failure(interface)
    if record.phase_ordinal is not PhaseOrdinal.PHASE_10:
        _failure(FailureCode.NATURAL_DRIVE_PHASE_INVALID, interface)
    if not (
        _ordered_unique_refs(record.exogenous_input_refs, nonempty=True)
        and _ordered_unique_refs(record.typed_balance_term_refs, nonempty=True)
        and record.proposed_update_ref not in record.typed_balance_term_refs
    ):
        _failure(FailureCode.DYNAMIC_STATE_INCOMPLETE, interface)
    _content_hash_check(record, interface)
    return None


@dataclass(
    frozen=True,
    slots=True,
    eq=False,
    order=False,
    unsafe_hash=False,
    init=False,
)
class _DynamicExecutionPermit:
    lease_ref: ObjectRef
    operation: Literal["propose_reroute"]
    issuance_nonce: object

    def __getattribute__(self, name: str) -> object:
        if name != "__class__":
            _failure(
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                "_DynamicExecutionPermit",
            )
        return object.__getattribute__(self, name)

    def __init__(self, *args: object, **kwargs: object) -> None:
        del args, kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )

    def __init_subclass__(cls, **kwargs: object) -> None:
        del kwargs
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )

    def __copy__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )

    def __reduce__(self) -> NoReturn:
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )

    def __reduce_ex__(self, protocol: object) -> NoReturn:
        del protocol
        _failure(
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            "_DynamicExecutionPermit",
        )


def _validate_route_guard(
    route: RoutePlan,
    completed_segment_refs: tuple[ObjectRef, ...],
    proposed_unfinished_suffix_refs: tuple[ObjectRef, ...],
    /,
) -> None:
    interface = "_validate_route_guard"
    if not (
        type(route) is RoutePlan
        and _object_ref_tuple(completed_segment_refs)
        and _object_ref_tuple(proposed_unfinished_suffix_refs)
    ):
        _formation_failure(interface)
    if not (
        _ordered_unique_refs(completed_segment_refs)
        and _ordered_unique_refs(proposed_unfinished_suffix_refs)
        and route.ordered_segment_refs[: len(completed_segment_refs)]
        == completed_segment_refs
        and not set(completed_segment_refs).intersection(
            proposed_unfinished_suffix_refs
        )
    ):
        _failure(FailureCode.COMPLETED_ROUTE_REWRITE_FORBIDDEN, interface)
    if route.route_semantics_status is _network.RouteSemanticsStatus.PROVISIONAL_PART_VII:
        _failure(FailureCode.ROUTE_SEMANTICS_UNRESOLVED, interface)
    _failure(FailureCode.ROUTE_SEMANTICS_UNRESOLVED, interface)


def _consume_dynamic_execution_permit(
    permit: _DynamicExecutionPermit,
    operation: Literal["propose_reroute"],
    /,
) -> NoReturn:
    del permit, operation
    _failure(
        FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
        "_consume_dynamic_execution_permit",
    )


def _exact_fixture_case(value: object) -> dict[str, object]:
    if type(value) is not dict or set(value) != {
        "case_id",
        "expected",
        "feature",
        "inputs",
        "owner",
        "unit",
    }:
        _formation_failure("validate_dynamic_static_identity")
    if not (
        type(value["case_id"]) is str
        and value["case_id"] in {"DC1", "DC2", "DC3", "DC4", "DC5", "DC6"}
        and type(value["feature"]) is str
        and type(value["inputs"]) is dict
        and type(value["expected"]) is dict
        and value["owner"] == "validate_dynamic_static_identity"
        and type(value["unit"]) is str
        and bool(value["unit"])
    ):
        _formation_failure("validate_dynamic_static_identity")
    return value


def _ints(value: object, length: int) -> bool:
    return (
        type(value) is list
        and len(value) == length
        and all(type(item) is int for item in value)
    )


def _validate_dc1(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    if set(inputs) != {"accepted", "capacities"} or not (
        _ints(inputs.get("accepted"), 2) and _ints(inputs.get("capacities"), 2)
    ):
        _formation_failure("validate_dynamic_static_identity")
    accepted = inputs["accepted"]
    capacities = inputs["capacities"]
    if capacities != [3, 4]:
        _failure(FailureCode.CAPACITY_IDENTITY_FAILURE, "validate_dynamic_static_identity")
    checks = [accepted[index] <= capacities[index] for index in range(2)]
    if any(value < 0 for value in accepted + capacities) or not all(checks):
        _failure(FailureCode.CAPACITY_COMPLIANCE_FAILURE, "validate_dynamic_static_identity")
    return {"capacity_checks": checks, "compatible_total": sum(accepted)}


def _validate_dc2(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    keys = {"admitted", "capacity", "expired", "opening_queues", "requests", "served"}
    if set(inputs) != keys or not (
        all(_ints(inputs[name], 2) for name in keys - {"capacity"})
        and type(inputs["capacity"]) is int
    ):
        _formation_failure("validate_dynamic_static_identity")
    if sum(inputs["served"]) > inputs["capacity"] or min(
        inputs["capacity"], *inputs["served"]
    ) < 0:
        _failure(FailureCode.CAPACITY_COMPLIANCE_FAILURE, "validate_dynamic_static_identity")
    if sum(inputs["requests"]) != sum(inputs["admitted"]):
        _failure(FailureCode.ADMISSION_BALANCE_FAILURE, "validate_dynamic_static_identity")
    closing = [
        inputs["opening_queues"][index]
        + inputs["admitted"][index]
        - inputs["served"][index]
        - inputs["expired"][index]
        for index in range(2)
    ]
    if min(*closing, *inputs["opening_queues"], *inputs["admitted"], *inputs["expired"]) < 0:
        _failure(FailureCode.QUEUE_BALANCE_FAILURE, "validate_dynamic_static_identity")
    return {
        "capacity_compliant": True,
        "closing_queues": closing,
        "total_closing_queue": sum(closing),
        "total_completed": sum(inputs["served"]),
        "total_presented": sum(inputs["requests"]),
    }


def _validate_dc3(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    keys = {"capacity", "deadline_epoch", "delay_epochs", "dispatch_epochs", "horizon_epoch", "quantity"}
    if set(inputs) != keys or not (
        _ints(inputs["dispatch_epochs"], 2)
        and all(type(inputs[name]) is int for name in keys - {"dispatch_epochs"})
    ):
        _formation_failure("validate_dynamic_static_identity")
    arrivals = [value + inputs["delay_epochs"] for value in inputs["dispatch_epochs"]]
    return {
        "arrival_epochs": arrivals,
        "pending_at_horizon": [
            0 if arrival <= inputs["horizon_epoch"] else inputs["quantity"]
            for arrival in arrivals
        ],
        "usable_at_deadline": [
            min(inputs["quantity"], inputs["capacity"])
            if arrival <= inputs["deadline_epoch"]
            else 0
            for arrival in arrivals
        ],
    }


def _validate_dc4(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    keys = {"alternate_capacity", "alternate_delay_epochs", "failed_primary_capacity", "request"}
    if set(inputs) != keys or not all(type(inputs[name]) is int for name in keys):
        _formation_failure("validate_dynamic_static_identity")
    dispatched = min(inputs["request"], inputs["alternate_capacity"])
    return {
        "counterfactual_arrival_epoch": inputs["alternate_delay_epochs"],
        "counterfactual_dispatched": dispatched,
        "live_reroute_outcome": "REFUSE",
        "route_semantics": "PROVISIONAL_PART_VII",
        "shortfall": inputs["request"] - dispatched,
    }


def _validate_dc5(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    keys = {"available_epoch_0", "demand", "end_epoch_dissipation", "storage"}
    if set(inputs) != keys or not all(type(inputs[name]) is int for name in keys):
        _formation_failure("validate_dynamic_static_identity")
    overlap = min(inputs["available_epoch_0"], inputs["demand"])
    return {
        "epoch_1_transfer": min(inputs["storage"], inputs["demand"]),
        "overlap_transfer": overlap,
    }


def _validate_dc6(case: dict[str, object]) -> dict[str, object]:
    inputs = case["inputs"]
    keys = {
        "capacity_per_epoch",
        "coordinated_admitted",
        "coordinated_expired",
        "coordinated_opening_queue",
        "coordinated_served",
        "per_provider_release",
        "separate_epoch_service",
    }
    if set(inputs) != keys or not (
        _ints(inputs["per_provider_release"], 2)
        and _ints(inputs["separate_epoch_service"], 2)
        and all(
            type(inputs[name]) is int
            for name in keys - {"per_provider_release", "separate_epoch_service"}
        )
    ):
        _formation_failure("validate_dynamic_static_identity")
    closing = (
        inputs["coordinated_opening_queue"]
        + inputs["coordinated_admitted"]
        - inputs["coordinated_served"]
        - inputs["coordinated_expired"]
    )
    if closing < 0:
        _failure(FailureCode.QUEUE_BALANCE_FAILURE, "validate_dynamic_static_identity")
    separate = sum(inputs["separate_epoch_service"])
    coordinated = inputs["coordinated_served"]
    return {
        "coordinated_closing_queue": closing,
        "coordinated_total": coordinated,
        "separate_total": separate,
        "service_difference_coordinated_minus_separate": coordinated - separate,
    }


_FIXTURE_VALIDATORS = {
    "DC1": _validate_dc1,
    "DC2": _validate_dc2,
    "DC3": _validate_dc3,
    "DC4": _validate_dc4,
    "DC5": _validate_dc5,
    "DC6": _validate_dc6,
}


def validate_dynamic_static_identity(
    fixture_case: CanonicalBytes,
    capability: T2FixtureCapability,
    /,
) -> None:
    interface = "validate_dynamic_static_identity"
    if type(fixture_case) is not bytes or type(capability) is not T2FixtureCapability:
        _formation_failure(interface)
    try:
        parsed = _canonical.parse_ecj1(fixture_case)
    except FrameworkError:
        _formation_failure(interface)
    case = _exact_fixture_case(parsed)
    case_id = case["case_id"]
    _capabilities._consume_t2_fixture_capability(
        capability,
        "validate_dynamic_static_identity",
        case_id,
    )
    actual = _FIXTURE_VALIDATORS[case_id](case)
    if case_id == "DC3" and case["expected"].get("arrival_epochs") != actual["arrival_epochs"]:
        _failure(FailureCode.DELAY_DECOMPOSITION_INVALID, interface)
    if case_id == "DC6" and case["expected"].get("coordinated_closing_queue") != actual["coordinated_closing_queue"]:
        _failure(FailureCode.QUEUE_BALANCE_FAILURE, interface)
    if case["expected"] != actual:
        _failure(FailureCode.DYNAMIC_STATIC_IDENTITY_MISMATCH, interface)
    return None


def propose_reroute(
    route: RoutePlan,
    topology_change: TopologyChangeEvent,
    transit: InTransitRecord,
    proposed_unfinished_suffix_refs: tuple[ObjectRef, ...],
    permit: _DynamicExecutionPermit,
    /,
) -> RoutePlan:
    if not (
        type(route) is RoutePlan
        and type(topology_change) is TopologyChangeEvent
        and type(transit) is InTransitRecord
        and _object_ref_tuple(proposed_unfinished_suffix_refs)
        and type(permit) is _DynamicExecutionPermit
    ):
        _formation_failure("propose_reroute")
    _consume_dynamic_execution_permit(permit, "propose_reroute")
    _validate_route_guard(
        route,
        transit.completed_segment_refs,
        proposed_unfinished_suffix_refs,
    )


_DEPENDENCY_SENTINELS = (
    _scheduling.Schedule,
    _policy.PolicyMemoryState,
    _ownership.EpochUpdateOwnership,
    _state.SystemState,
)


__all__ = (
    "DelayRecord",
    "InTransitRecord",
    "DelayedEffect",
    "DynamicUpdateRecord",
    "NaturalDriveContract",
    "validate_dynamic_static_identity",
    "propose_reroute",
)
