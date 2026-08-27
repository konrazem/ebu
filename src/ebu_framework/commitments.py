"""Immutable I-3 commitment declarations and pure T0 consistency checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import Literal, NoReturn, get_args

from .actions import ActionInstance, EffectiveInterval
from .network import CapacityLocus
from .primitives import CoreNumberV1, Epoch, Quantity
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


_CORE_NUMBER_TYPES = get_args(CoreNumberV1)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.commitments", name, "1.0.0")


def _failure(
    code: FailureCode,
    interface: str,
    *,
    summary: str | None = None,
    object_ref: FailureObjectRef | None = None,
) -> NoReturn:
    _fail(
        code,
        summary or f"{interface} rejected {code.value}",
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


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
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
class Commitment:
    envelope: CommonObjectEnvelope
    provider_ref: ObjectRef
    beneficiary_ref: ObjectRef
    service_or_quantity_ref: ObjectRef
    time_window: EffectiveInterval
    condition_refs: tuple[ObjectRef, ...]
    guarantee_class_ref: ObjectRef
    status_ref: ObjectRef
    breach_rule_ref: ObjectRef
    quote_ref: ObjectRef
    reservation_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.provider_ref,
                    self.beneficiary_ref,
                    self.service_or_quantity_ref,
                    self.guarantee_class_ref,
                    self.status_ref,
                    self.breach_rule_ref,
                    self.quote_ref,
                )
            )
            and type(self.time_window) is EffectiveInterval
            and _object_ref_tuple(self.condition_refs)
            and _object_ref_tuple(self.reservation_refs)
        ):
            _formation_failure("Commitment")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Reservation:
    envelope: CommonObjectEnvelope
    action_ref: ObjectRef
    capacity_locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    interval: EffectiveInterval
    reserved_quantity: Quantity
    capacity_snapshot_ref: ObjectRef
    uncertainty_rule_ref: ObjectRef
    priority_rule_ref: ObjectRef
    release_condition_ref: ObjectRef
    status_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.action_ref,
                    self.capacity_locus_ref,
                    self.resource_type_ref,
                    self.capacity_snapshot_ref,
                    self.uncertainty_rule_ref,
                    self.priority_rule_ref,
                    self.release_condition_ref,
                    self.status_ref,
                )
            )
            and type(self.interval) is EffectiveInterval
            and type(self.reserved_quantity) is Quantity
        ):
            _formation_failure("Reservation")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CapacityRecord:
    envelope: CommonObjectEnvelope
    capacity_locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    epoch: Epoch
    installed: Quantity
    availability_factor: CoreNumberV1
    usable: Quantity
    reserved: Quantity
    admitted: Quantity
    completed: Quantity

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.capacity_locus_ref) is ObjectRef
            and type(self.resource_type_ref) is ObjectRef
            and type(self.epoch) is Epoch
            and all(
                type(value) is Quantity
                for value in (
                    self.installed,
                    self.usable,
                    self.reserved,
                    self.admitted,
                    self.completed,
                )
            )
            and type(self.availability_factor) in _CORE_NUMBER_TYPES
        ):
            _formation_failure("CapacityRecord")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


def _failure_object(record: object) -> FailureObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _object_content_check(record: object, interface: str, position: str) -> None:
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH at {position}"
            ),
            object_ref=_failure_object(record),
        )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _object_hash_matches(record: object) -> bool:
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def _interval_reversed(interval: EffectiveInterval) -> bool:
    return interval.end.tick.value < interval.start.tick.value


def _core_fraction(value: CoreNumberV1) -> Fraction:
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


def _quantity_units_match(left: Quantity, right: Quantity) -> bool:
    return left.unit_ref == right.unit_ref and left.dimension_ref == right.dimension_ref


def _capacity_arithmetic_invalid(record: CapacityRecord) -> bool:
    installed, usable, reserved, admitted, completed = (
        _core_fraction(quantity.magnitude)
        for quantity in (
            record.installed,
            record.usable,
            record.reserved,
            record.admitted,
            record.completed,
        )
    )
    factor = _core_fraction(record.availability_factor)
    return (
        min(installed, usable, reserved, admitted, completed, factor) < 0
        or usable > installed
    )


def validate_commitment(record: Commitment, /) -> None:
    if type(record) is not Commitment:
        _formation_failure("Commitment")
    interface = "validate_commitment"
    _object_content_check(record, interface, "argument 1 (record)")
    collections = (record.condition_refs, record.reservation_refs)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if _interval_reversed(record.time_window):
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_reservation(record: Reservation, capacity: CapacityRecord, /) -> None:
    if type(record) is not Reservation:
        _formation_failure("Reservation")
    if type(capacity) is not CapacityRecord:
        _formation_failure("CapacityRecord")
    interface = "validate_reservation"
    _object_content_check(record, interface, "argument 1 (record)")
    _object_content_check(capacity, interface, "argument 2 (capacity)")

    if _interval_reversed(record.interval) or _core_fraction(record.reserved_quantity.magnitude) < 0:
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _quantity_units_match(record.reserved_quantity, capacity.usable):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    capacity_ref = ObjectRef(
        object_id=capacity.envelope.object_id,
        object_version=capacity.envelope.object_version,
        object_content_hash=capacity.envelope.object_content_hash,
    )
    if not (
        record.capacity_locus_ref == capacity.capacity_locus_ref
        and record.resource_type_ref == capacity.resource_type_ref
        and record.capacity_snapshot_ref == capacity_ref
    ):
        _failure(FailureCode.RESERVATION_CAPACITY_MISMATCH, interface)
    if not _object_hash_matches(record) or not _object_hash_matches(capacity):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_capacity_record(record: CapacityRecord, /) -> None:
    if type(record) is not CapacityRecord:
        _formation_failure("CapacityRecord")
    interface = "validate_capacity_record"
    _object_content_check(record, interface, "argument 1 (record)")

    if any(
        not _quantity_units_match(record.installed, quantity)
        for quantity in (
            record.usable,
            record.reserved,
            record.admitted,
            record.completed,
        )
    ):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    if _capacity_arithmetic_invalid(record):
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _object_hash_matches(record):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def _i7_failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I7,
        interface_ref=FailureInterfaceRef(
            "ebu_framework.commitments", interface, "1.0.0"
        ),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _i7_formation_failure(interface: str) -> NoReturn:
    _i7_failure(FailureCode.I7_RECORD_FORMATION_INVALID, interface)


def _strict_i7_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected_fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected_fields:
            _i7_formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _quantity_context(quantity: Quantity) -> tuple[object, ...]:
    return (
        quantity.unit_ref,
        quantity.dimension_ref,
        quantity.boundary_ref,
        quantity.resource_type_ref,
        quantity.service_type_ref,
        quantity.region_ref,
        quantity.time_basis_ref,
        quantity.sign_convention_ref,
        quantity.uncertainty_ref,
    )


def _quantities_share_context(values: tuple[Quantity, ...]) -> bool:
    return bool(values) and all(
        _quantity_context(value) == _quantity_context(values[0])
        for value in values[1:]
    )


def _nonnegative_quantities(values: tuple[Quantity, ...]) -> bool:
    return all(_core_fraction(value.magnitude) >= 0 for value in values)


def _i7_content_hash_check(record: object, interface: str) -> None:
    if record.envelope.to_ecj1()["object_content_payload"] != record.to_ecj1():  # type: ignore[attr-defined]
        _i7_failure(FailureCode.HASH_MISMATCH, interface)
    if not _object_hash_matches(record):
        _i7_failure(FailureCode.HASH_MISMATCH, interface)


@_strict_i7_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AdmissionDecision:
    envelope: CommonObjectEnvelope
    decision_epoch: Epoch
    request_ref: ObjectRef
    capacity_record_ref: ObjectRef
    topology_snapshot_ref: ObjectRef
    commitment_ref: ObjectRef | Applicability
    policy_decision_ref: ObjectRef | Applicability
    presented: Quantity
    admitted_to_queue: Quantity
    rejected: Quantity
    pending_outside_queue: Quantity
    disposition: Literal["ADMIT", "REJECT", "DEFER", "PARTIAL"]
    allocation_rule_ref: ObjectRef
    queue_rule_ref: ObjectRef
    admissibility_evidence_refs: tuple[ObjectRef, ...]
    domain_authority_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.decision_epoch) is Epoch
            and all(
                type(value) is ObjectRef
                for value in (
                    self.request_ref,
                    self.capacity_record_ref,
                    self.topology_snapshot_ref,
                    self.allocation_rule_ref,
                    self.queue_rule_ref,
                    self.domain_authority_ref,
                )
            )
            and _object_or_applicability(self.commitment_ref)
            and _object_or_applicability(self.policy_decision_ref)
            and all(
                type(value) is Quantity
                for value in (
                    self.presented,
                    self.admitted_to_queue,
                    self.rejected,
                    self.pending_outside_queue,
                )
            )
            and type(self.disposition) is str
            and self.disposition in {"ADMIT", "REJECT", "DEFER", "PARTIAL"}
            and _object_ref_tuple(self.admissibility_evidence_refs)
        ):
            _i7_formation_failure("AdmissionDecision")
        _validate_admission_decision(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_i7_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class QueueRecord:
    envelope: CommonObjectEnvelope
    capacity_locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    epoch: Epoch
    opening_queue: Quantity
    admitted_arrival: Quantity
    completed_flow: Quantity
    expired_cancelled_abandoned: Quantity
    closing_queue: Quantity
    rejected_outside_queue: Quantity
    pending_outside_queue: Quantity
    admission_decision_refs: tuple[ObjectRef, ...]
    queue_discipline_ref: ObjectRef
    priority_rule_ref: ObjectRef
    congestion_ref: ObjectRef | Applicability
    domain_authority_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.epoch) is Epoch
            and all(
                type(value) is ObjectRef
                for value in (
                    self.capacity_locus_ref,
                    self.resource_type_ref,
                    self.queue_discipline_ref,
                    self.priority_rule_ref,
                    self.domain_authority_ref,
                )
            )
            and all(
                type(value) is Quantity
                for value in (
                    self.opening_queue,
                    self.admitted_arrival,
                    self.completed_flow,
                    self.expired_cancelled_abandoned,
                    self.closing_queue,
                    self.rejected_outside_queue,
                    self.pending_outside_queue,
                )
            )
            and _object_ref_tuple(self.admission_decision_refs)
            and _object_or_applicability(self.congestion_ref)
        ):
            _i7_formation_failure("QueueRecord")
        _validate_queue_record(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_i7_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ReservationShortfall:
    envelope: CommonObjectEnvelope
    epoch: Epoch
    capacity_record_ref: ObjectRef
    reservation_refs: tuple[ObjectRef, ...]
    affected_commitment_refs: tuple[ObjectRef, ...]
    reserved_total: Quantity
    usable_capacity: Quantity
    shortfall: Quantity
    allocation_rule_ref: ObjectRef
    disposition_refs: tuple[ObjectRef, ...]
    status: Literal["IMPAIRED", "BREACHED", "REROUTE_PROPOSED", "UNRESOLVED"]
    domain_authority_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.epoch) is Epoch
            and all(
                type(value) is ObjectRef
                for value in (
                    self.capacity_record_ref,
                    self.allocation_rule_ref,
                    self.domain_authority_ref,
                )
            )
            and all(
                _object_ref_tuple(values)
                for values in (
                    self.reservation_refs,
                    self.affected_commitment_refs,
                    self.disposition_refs,
                )
            )
            and all(
                type(value) is Quantity
                for value in (
                    self.reserved_total,
                    self.usable_capacity,
                    self.shortfall,
                )
            )
            and type(self.status) is str
            and self.status
            in {"IMPAIRED", "BREACHED", "REROUTE_PROPOSED", "UNRESOLVED"}
        ):
            _i7_formation_failure("ReservationShortfall")
        _validate_reservation_shortfall(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_i7_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CongestionRecord:
    envelope: CommonObjectEnvelope
    capacity_locus_ref: ObjectRef
    epoch: Epoch
    requested_load: Quantity
    admitted_load: Quantity
    completed_flow: Quantity
    usable_capacity: Quantity
    opening_queue: Quantity
    closing_queue: Quantity
    binding_rule_ref: ObjectRef
    effect_kinds: tuple[
        Literal["COMPLETION", "DELAY", "LOSS", "FEASIBILITY"], ...
    ]
    effect_refs: tuple[ObjectRef, ...]
    queue_record_ref: ObjectRef | Applicability
    status: Literal["BINDING_CAPACITY_INTERACTION"]
    domain_authority_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.epoch) is Epoch
            and all(
                type(value) is ObjectRef
                for value in (
                    self.capacity_locus_ref,
                    self.binding_rule_ref,
                    self.domain_authority_ref,
                )
            )
            and all(
                type(value) is Quantity
                for value in (
                    self.requested_load,
                    self.admitted_load,
                    self.completed_flow,
                    self.usable_capacity,
                    self.opening_queue,
                    self.closing_queue,
                )
            )
            and type(self.effect_kinds) is tuple
            and all(
                type(value) is str
                and value in {"COMPLETION", "DELAY", "LOSS", "FEASIBILITY"}
                for value in self.effect_kinds
            )
            and _object_ref_tuple(self.effect_refs)
            and _object_or_applicability(self.queue_record_ref)
            and type(self.status) is str
            and self.status == "BINDING_CAPACITY_INTERACTION"
        ):
            _i7_formation_failure("CongestionRecord")
        _validate_congestion_record(self)

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


def _validate_admission_decision(decision: AdmissionDecision, /) -> None:
    interface = "AdmissionDecision"
    if type(decision) is not AdmissionDecision:
        _i7_formation_failure(interface)
    quantities = (
        decision.presented,
        decision.admitted_to_queue,
        decision.rejected,
        decision.pending_outside_queue,
    )
    presented, admitted, rejected, pending = (
        _core_fraction(value.magnitude) for value in quantities
    )
    partition = admitted + rejected + pending
    disposition_valid = {
        "ADMIT": admitted == presented and rejected == 0 and pending == 0,
        "REJECT": admitted == 0 and rejected == presented and pending == 0,
        "DEFER": admitted == 0 and rejected == 0 and pending == presented,
        "PARTIAL": partition == presented
        and sum(value > 0 for value in (admitted, rejected, pending)) >= 2,
    }[decision.disposition]
    if not (
        _quantities_share_context(quantities)
        and _nonnegative_quantities(quantities)
        and presented == partition
        and disposition_valid
        and bool(decision.admissibility_evidence_refs)
        and _ordered_refs(decision.admissibility_evidence_refs)
        and not _duplicate_refs(decision.admissibility_evidence_refs)
    ):
        _i7_failure(FailureCode.ADMISSION_BALANCE_FAILURE, interface)
    _i7_content_hash_check(decision, interface)
    return None


def _validate_queue_record(record: QueueRecord, /) -> None:
    interface = "QueueRecord"
    if type(record) is not QueueRecord:
        _i7_formation_failure(interface)
    quantities = (
        record.opening_queue,
        record.admitted_arrival,
        record.completed_flow,
        record.expired_cancelled_abandoned,
        record.closing_queue,
        record.rejected_outside_queue,
        record.pending_outside_queue,
    )
    opening, admitted, completed, expired, closing, rejected, pending = (
        _core_fraction(value.magnitude) for value in quantities
    )
    correct_closing = opening + admitted - completed - expired
    outside_mutation = correct_closing - rejected - pending
    if (rejected != 0 or pending != 0) and closing == outside_mutation:
        _i7_failure(FailureCode.REJECTED_DEMAND_QUEUE_MUTATION, interface)
    if not (
        _quantities_share_context(quantities)
        and _nonnegative_quantities(quantities)
        and closing == correct_closing
    ):
        _i7_failure(FailureCode.QUEUE_BALANCE_FAILURE, interface)
    if not (
        record.admission_decision_refs
        and _ordered_refs(record.admission_decision_refs)
        and not _duplicate_refs(record.admission_decision_refs)
    ):
        _i7_failure(FailureCode.QUEUE_BALANCE_FAILURE, interface)
    _i7_content_hash_check(record, interface)
    return None


def _validate_reservation_shortfall(record: ReservationShortfall, /) -> None:
    interface = "ReservationShortfall"
    if type(record) is not ReservationShortfall:
        _i7_formation_failure(interface)
    quantities = (
        record.reserved_total,
        record.usable_capacity,
        record.shortfall,
    )
    reserved, usable, shortfall = (
        _core_fraction(value.magnitude) for value in quantities
    )
    if not (
        _quantities_share_context(quantities)
        and _nonnegative_quantities(quantities)
        and shortfall == max(Fraction(0), reserved - usable)
        and shortfall > 0
    ):
        _i7_failure(FailureCode.RESERVATION_SHORTFALL_INVALID, interface)
    if not (
        record.reservation_refs
        and record.affected_commitment_refs
        and all(
            _ordered_refs(values) and not _duplicate_refs(values)
            for values in (
                record.reservation_refs,
                record.affected_commitment_refs,
                record.disposition_refs,
            )
        )
    ):
        _i7_failure(FailureCode.COMMITMENT_STATE_MISMATCH, interface)
    _i7_content_hash_check(record, interface)
    return None


def _validate_congestion_record(record: CongestionRecord, /) -> None:
    interface = "CongestionRecord"
    if type(record) is not CongestionRecord:
        _i7_formation_failure(interface)
    quantities = (
        record.requested_load,
        record.admitted_load,
        record.completed_flow,
        record.usable_capacity,
        record.opening_queue,
        record.closing_queue,
    )
    requested, admitted, completed, usable, opening, closing = (
        _core_fraction(value.magnitude) for value in quantities
    )
    if not (
        _quantities_share_context(quantities)
        and _nonnegative_quantities(quantities)
        and completed <= usable
    ):
        _i7_failure(FailureCode.CAPACITY_COMPLIANCE_FAILURE, interface)
    effect_order = ("COMPLETION", "DELAY", "LOSS", "FEASIBILITY")
    effect_indices = tuple(effect_order.index(value) for value in record.effect_kinds)
    if not (
        admitted <= requested
        and opening >= 0
        and closing >= 0
        and record.effect_kinds
        and len(record.effect_kinds) == len(record.effect_refs)
        and effect_indices == tuple(sorted(effect_indices))
        and len(effect_indices) == len(set(effect_indices))
        and _ordered_refs(record.effect_refs)
        and not _duplicate_refs(record.effect_refs)
    ):
        _i7_failure(FailureCode.CONGESTION_DECLARATION_INVALID, interface)
    _i7_content_hash_check(record, interface)
    return None


_DEPENDENCY_SENTINELS = (ActionInstance, CapacityLocus)


__all__ = (
    "Commitment",
    "Reservation",
    "CapacityRecord",
    "validate_commitment",
    "validate_reservation",
    "validate_capacity_record",
    "AdmissionDecision",
    "QueueRecord",
    "ReservationShortfall",
    "CongestionRecord",
)
