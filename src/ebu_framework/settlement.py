"""Immutable I-3 settlement declarations and local closure validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import NoReturn

from .actions import ActionInstance, EffectiveInterval
from .observation import Measurement
from .causal import CausalIdentificationStatus
from .primitives import Instant, Quantity, ResolutionDetail, ResolutionState
from .numeric import CoreNumberV1
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


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.settlement", name, "1.0.0")


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


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _project(value: object) -> object:
    if type(value) is Applicability:
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


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Quote:
    envelope: CommonObjectEnvelope
    observation_refs: tuple[ObjectRef, ...]
    state_refs: tuple[ObjectRef, ...]
    request_ref: ObjectRef
    distortion_ref: ObjectRef
    boundary_ref: ObjectRef
    parameter_refs: tuple[ObjectRef, ...]
    uncertainty_refs: tuple[ObjectRef, ...]
    committed_field_snapshot_ref: ObjectRef
    accepted_quantity_refs: tuple[ObjectRef, ...]
    predicted_value: Quantity | ResolutionDetail
    guarantee_class_ref: ObjectRef
    issuer_ref: ObjectRef
    issue_time: Instant
    valid_interval: EffectiveInterval
    expiry: Instant
    acceptance_status_ref: ObjectRef
    unresolved_term_refs: tuple[ObjectRef, ...]
    computation_dependency_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and _object_ref_tuple(self.observation_refs)
            and _object_ref_tuple(self.state_refs)
            and all(
                type(value) is ObjectRef
                for value in (
                    self.request_ref,
                    self.distortion_ref,
                    self.boundary_ref,
                    self.committed_field_snapshot_ref,
                    self.guarantee_class_ref,
                    self.issuer_ref,
                    self.acceptance_status_ref,
                )
            )
            and _object_ref_tuple(self.parameter_refs)
            and _object_ref_tuple(self.uncertainty_refs)
            and _object_ref_tuple(self.accepted_quantity_refs)
            and type(self.predicted_value) in (Quantity, ResolutionDetail)
            and type(self.issue_time) is Instant
            and type(self.valid_interval) is EffectiveInterval
            and type(self.expiry) is Instant
            and _object_ref_tuple(self.unresolved_term_refs)
            and _object_ref_tuple(self.computation_dependency_refs)
        ):
            _formation_failure("Quote")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Receipt:
    envelope: CommonObjectEnvelope
    quote_ref: ObjectRef
    action_or_group_ref: ObjectRef
    before_state_ref: ObjectRef
    after_state_ref: ObjectRef
    measurement_refs: tuple[ObjectRef, ...]
    completion_status_ref: ObjectRef
    delivered_quantity_refs: tuple[ObjectRef, ...]
    distortion_value: Quantity | ResolutionDetail
    loss_refs: tuple[ObjectRef, ...]
    outflow_refs: tuple[ObjectRef, ...]
    unresolved_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.quote_ref,
                    self.action_or_group_ref,
                    self.before_state_ref,
                    self.after_state_ref,
                    self.completion_status_ref,
                )
            )
            and _object_ref_tuple(self.measurement_refs)
            and _object_ref_tuple(self.delivered_quantity_refs)
            and type(self.distortion_value) in (Quantity, ResolutionDetail)
            and _object_ref_tuple(self.loss_refs)
            and _object_ref_tuple(self.outflow_refs)
            and _object_ref_tuple(self.unresolved_refs)
        ):
            _formation_failure("Receipt")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class GroupReceipt:
    envelope: CommonObjectEnvelope
    group_ref: ObjectRef
    child_receipt_refs: tuple[ObjectRef, ...]
    joint_transition_ref: ObjectRef
    before_state_ref: ObjectRef
    after_state_ref: ObjectRef
    measurement_ref: ObjectRef
    causal_status: CausalIdentificationStatus
    settlement_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.group_ref) is ObjectRef
            and _object_ref_tuple(self.child_receipt_refs)
            and all(
                type(value) is ObjectRef
                for value in (
                    self.joint_transition_ref,
                    self.before_state_ref,
                    self.after_state_ref,
                    self.measurement_ref,
                )
            )
            and type(self.causal_status) is CausalIdentificationStatus
            and _object_or_applicability(self.settlement_ref)
        ):
            _formation_failure("GroupReceipt")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ChildActionRecord:
    envelope: CommonObjectEnvelope
    group_receipt_ref: ObjectRef
    action_ref: ObjectRef
    completion_status_ref: ObjectRef
    measurement_refs: tuple[ObjectRef, ...]
    causal_contribution_ref: ObjectRef | Applicability
    settlement_share_ref: ObjectRef | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.group_receipt_ref) is ObjectRef
            and type(self.action_ref) is ObjectRef
            and type(self.completion_status_ref) is ObjectRef
            and _object_ref_tuple(self.measurement_refs)
            and _object_or_applicability(self.causal_contribution_ref)
            and _object_or_applicability(self.settlement_share_ref)
        ):
            _formation_failure("ChildActionRecord")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SettlementShare:
    envelope: CommonObjectEnvelope
    beneficiary_ref: ObjectRef
    amount: Quantity
    rule_ref: ObjectRef
    evidence_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.beneficiary_ref) is ObjectRef
            and type(self.amount) is Quantity
            and type(self.rule_ref) is ObjectRef
            and _object_ref_tuple(self.evidence_refs)
        ):
            _formation_failure("SettlementShare")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class GroupResidual:
    envelope: CommonObjectEnvelope
    group_receipt_ref: ObjectRef
    measured_total: Quantity
    share_total: Quantity
    residual: Quantity
    arithmetic_policy_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.group_receipt_ref) is ObjectRef
            and type(self.measured_total) is Quantity
            and type(self.share_total) is Quantity
            and type(self.residual) is Quantity
            and type(self.arithmetic_policy_ref) is ObjectRef
        ):
            _formation_failure("GroupResidual")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class SettlementClosureRecord:
    envelope: CommonObjectEnvelope
    group_residual_ref: ObjectRef
    share_refs: tuple[ObjectRef, ...]
    closure_resolution: ResolutionDetail
    validated_arithmetic_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.group_residual_ref) is ObjectRef
            and _object_ref_tuple(self.share_refs)
            and type(self.closure_resolution) is ResolutionDetail
            and type(self.validated_arithmetic_ref) is ObjectRef
        ):
            _formation_failure("SettlementClosureRecord")

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


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _ordered_records(values: tuple[object, ...]) -> bool:
    keys = tuple(_ref_key(_envelope_ref(record)) for record in values)
    return keys == tuple(sorted(keys))


def _duplicate_records(values: tuple[object, ...]) -> bool:
    return any(
        left == right
        for index, left in enumerate(values)
        for right in values[index + 1 :]
    )


def _object_hash_matches(record: object) -> bool:
    try:
        validate_object_envelope(record.envelope)  # type: ignore[attr-defined]
    except FrameworkError:
        return False
    return True


def _quantity_units_match(left: Quantity, right: Quantity) -> bool:
    return left.unit_ref == right.unit_ref and left.dimension_ref == right.dimension_ref


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


def _settlement_links_match(
    closure: SettlementClosureRecord,
    quote: Quote,
    receipt: Receipt,
    group_receipt: GroupReceipt,
    child_actions: tuple[ChildActionRecord, ...],
    residual: GroupResidual,
    shares: tuple[SettlementShare, ...],
) -> bool:
    receipt_ref = _envelope_ref(receipt)
    group_ref = _envelope_ref(group_receipt)
    share_refs = tuple(_envelope_ref(share) for share in shares)
    return (
        receipt.quote_ref == _envelope_ref(quote)
        and group_receipt.child_receipt_refs == (receipt_ref,)
        and all(child.group_receipt_ref == group_ref for child in child_actions)
        and residual.group_receipt_ref == group_ref
        and closure.group_residual_ref == _envelope_ref(residual)
        and closure.share_refs == share_refs
    )


def validate_settlement_closure(
    closure: SettlementClosureRecord,
    quote: Quote,
    receipt: Receipt,
    group_receipt: GroupReceipt,
    child_actions: tuple[ChildActionRecord, ...],
    residual: GroupResidual,
    shares: tuple[SettlementShare, ...],
    causal_status: CausalIdentificationStatus,
    /,
) -> None:
    scalar_arguments = (
        (closure, SettlementClosureRecord, "SettlementClosureRecord"),
        (quote, Quote, "Quote"),
        (receipt, Receipt, "Receipt"),
        (group_receipt, GroupReceipt, "GroupReceipt"),
        (residual, GroupResidual, "GroupResidual"),
    )
    for value, expected, name in scalar_arguments:
        if type(value) is not expected:
            _formation_failure(name)
    if not (
        type(child_actions) is tuple
        and all(type(item) is ChildActionRecord for item in child_actions)
    ):
        _formation_failure("ChildActionRecord")
    if not (
        type(shares) is tuple
        and all(type(item) is SettlementShare for item in shares)
    ):
        _formation_failure("SettlementShare")
    if type(causal_status) is not CausalIdentificationStatus:
        _formation_failure("CausalIdentificationStatus")

    interface = "validate_settlement_closure"
    for record, position in (
        (closure, "argument 1 (closure)"),
        (quote, "argument 2 (quote)"),
        (receipt, "argument 3 (receipt)"),
        (group_receipt, "argument 4 (group_receipt)"),
    ):
        _object_content_check(record, interface, position)
    for index, record in enumerate(child_actions):
        _object_content_check(
            record,
            interface,
            f"argument 5 (child_actions), member {index}",
        )
    _object_content_check(residual, interface, "argument 6 (residual)")
    for index, record in enumerate(shares):
        _object_content_check(
            record,
            interface,
            f"argument 7 (shares), member {index}",
        )

    applicability_values = (group_receipt.settlement_ref,) + tuple(
        value
        for child in child_actions
        for value in (
            child.causal_contribution_ref,
            child.settlement_share_ref,
        )
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    ref_collections = (
        quote.observation_refs,
        quote.state_refs,
        quote.parameter_refs,
        quote.uncertainty_refs,
        quote.accepted_quantity_refs,
        quote.unresolved_term_refs,
        quote.computation_dependency_refs,
        receipt.measurement_refs,
        receipt.delivered_quantity_refs,
        receipt.loss_refs,
        receipt.outflow_refs,
        receipt.unresolved_refs,
        group_receipt.child_receipt_refs,
        closure.share_refs,
    ) + tuple(child.measurement_refs for child in child_actions) + tuple(
        share.evidence_refs for share in shares
    )
    if (
        any(not _ordered_refs(values) for values in ref_collections)
        or not _ordered_records(child_actions)
        or not _ordered_records(shares)
    ):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if (
        any(_duplicate_refs(values) for values in ref_collections)
        or _duplicate_records(child_actions)
        or _duplicate_records(shares)
    ):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)

    if not _settlement_links_match(
        closure,
        quote,
        receipt,
        group_receipt,
        child_actions,
        residual,
        shares,
    ):
        _failure(FailureCode.SETTLEMENT_LINK_INVALID, interface)

    comparison_quantities = (residual.share_total, residual.residual) + tuple(
        share.amount for share in shares
    )
    if any(
        not _quantity_units_match(residual.measured_total, quantity)
        for quantity in comparison_quantities
    ):
        _failure(FailureCode.CONSERVATION_UNIT_MISMATCH, interface)
    if (
        sum(
            (_core_fraction(share.amount.magnitude) for share in shares),
            Fraction(),
        )
        != _core_fraction(residual.share_total.magnitude)
        or _core_fraction(residual.measured_total.magnitude)
        != _core_fraction(residual.share_total.magnitude)
        + _core_fraction(residual.residual.magnitude)
        or bool(shares)
        != (
            closure.closure_resolution.state is ResolutionState.PRESENT
        )
    ):
        _failure(FailureCode.SETTLEMENT_CLOSURE_FAILURE, interface)

    if (
        causal_status is not CausalIdentificationStatus.IDENTIFIED
        or group_receipt.causal_status is not CausalIdentificationStatus.IDENTIFIED
    ) and any(
        type(child.causal_contribution_ref) is ObjectRef
        for child in child_actions
    ):
        _failure(FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED, interface)
    if causal_status is CausalIdentificationStatus.IDENTIFIED and not child_actions:
        _failure(FailureCode.CAUSAL_ATTRIBUTION_UNRESOLVED, interface)

    records = (
        closure,
        quote,
        receipt,
        group_receipt,
    ) + child_actions + (residual,) + shares
    if any(not _object_hash_matches(record) for record in records):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINELS = (ActionInstance, Measurement)


__all__ = (
    "Quote",
    "Receipt",
    "GroupReceipt",
    "ChildActionRecord",
    "SettlementShare",
    "GroupResidual",
    "SettlementClosureRecord",
    "validate_settlement_closure",
)
