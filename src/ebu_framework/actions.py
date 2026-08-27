"""Immutable I-3 action declarations and locally observable T0 validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import sys
from typing import Literal, NoReturn

from .state import SystemState
from .primitives import Instant, Quantity, ResolutionDetail
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
    return FailureInterfaceRef("ebu_framework.actions", name, "1.0.0")


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


def _quantity_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is Quantity for item in value)


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


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


class ActionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    ACCEPTED = "ACCEPTED"
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    UNRESOLVED = "UNRESOLVED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("ActionStatus")


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class EffectiveInterval:
    start: Instant
    end: Instant
    clock_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.start) is Instant
            and type(self.end) is Instant
            and type(self.clock_ref) is ObjectRef
        ):
            _formation_failure("EffectiveInterval")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "start": self.start.to_ecj1(),
            "end": self.end.to_ecj1(),
            "clock_ref": self.clock_ref.to_ecj1(),
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
class WriteSupport:
    coordinate_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not _object_ref_tuple(self.coordinate_refs):
            _formation_failure("WriteSupport")

    def to_ecj1(self) -> dict[str, object]:
        return {"coordinate_refs": _project(self.coordinate_refs)}


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConstraintSupport:
    constraint_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not _object_ref_tuple(self.constraint_refs):
            _formation_failure("ConstraintSupport")

    def to_ecj1(self) -> dict[str, object]:
        return {"constraint_refs": _project(self.constraint_refs)}


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ActionDefinition:
    envelope: CommonObjectEnvelope
    action_type_ref: ObjectRef
    transformation_contract_ref: ObjectRef
    predecessor_state_schema_ref: ObjectRef
    input_quantity_refs: tuple[ObjectRef, ...]
    output_quantity_refs: tuple[ObjectRef, ...]
    write_support: WriteSupport
    constraint_support: ConstraintSupport
    prerequisite_refs: tuple[ObjectRef, ...]
    domain_predicate_ref: ObjectRef
    physical_effect_refs: tuple[ObjectRef, ...]
    conversion_refs: tuple[ObjectRef, ...]
    loss_refs: tuple[ObjectRef, ...]
    resource_use_refs: tuple[ObjectRef, ...]
    burden_refs: tuple[ObjectRef, ...]
    completion_condition_refs: tuple[ObjectRef, ...]
    failure_condition_refs: tuple[ObjectRef, ...]
    compatible_boundary_refs: tuple[ObjectRef, ...]
    horizon_refs: tuple[ObjectRef, ...]
    semantics_kind: Literal[
        "DETERMINISTIC_DECLARATION", "STOCHASTIC_DECLARATION"
    ]

    def __post_init__(self) -> None:
        ref_fields = (
            self.action_type_ref,
            self.transformation_contract_ref,
            self.predecessor_state_schema_ref,
            self.domain_predicate_ref,
        )
        ref_collections = (
            self.input_quantity_refs,
            self.output_quantity_refs,
            self.prerequisite_refs,
            self.physical_effect_refs,
            self.conversion_refs,
            self.loss_refs,
            self.resource_use_refs,
            self.burden_refs,
            self.completion_condition_refs,
            self.failure_condition_refs,
            self.compatible_boundary_refs,
            self.horizon_refs,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in ref_fields)
            and all(_object_ref_tuple(value) for value in ref_collections)
            and type(self.write_support) is WriteSupport
            and type(self.constraint_support) is ConstraintSupport
            and type(self.semantics_kind) is str
            and self.semantics_kind
            in {"DETERMINISTIC_DECLARATION", "STOCHASTIC_DECLARATION"}
        ):
            _formation_failure("ActionDefinition")

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
class ActionInstance:
    envelope: CommonObjectEnvelope
    definition_ref: ObjectRef
    requesting_actor_ref: ObjectRef
    responsible_provider_ref: ObjectRef
    requested_quantities: tuple[Quantity, ...]
    accepted_quantities: tuple[Quantity, ...] | ResolutionDetail
    placement_ref: ObjectRef
    route_ref: ObjectRef | Applicability
    effective_interval: EffectiveInterval
    write_support: WriteSupport
    constraint_support: ConstraintSupport
    prerequisite_refs: tuple[ObjectRef, ...]
    deadline_and_horizon_ref: ObjectRef
    commitment_refs: tuple[ObjectRef, ...]
    reservation_refs: tuple[ObjectRef, ...]
    measurement_contract_ref: ObjectRef
    boundary_ref: ObjectRef
    status: ActionStatus

    def __post_init__(self) -> None:
        ref_fields = (
            self.definition_ref,
            self.requesting_actor_ref,
            self.responsible_provider_ref,
            self.placement_ref,
            self.deadline_and_horizon_ref,
            self.measurement_contract_ref,
            self.boundary_ref,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(type(value) is ObjectRef for value in ref_fields)
            and _quantity_tuple(self.requested_quantities)
            and (
                _quantity_tuple(self.accepted_quantities)
                or type(self.accepted_quantities) is ResolutionDetail
            )
            and _object_or_applicability(self.route_ref)
            and type(self.effective_interval) is EffectiveInterval
            and type(self.write_support) is WriteSupport
            and type(self.constraint_support) is ConstraintSupport
            and _object_ref_tuple(self.prerequisite_refs)
            and _object_ref_tuple(self.commitment_refs)
            and _object_ref_tuple(self.reservation_refs)
            and type(self.status) is ActionStatus
        ):
            _formation_failure("ActionInstance")

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
    stored = record.envelope.to_ecj1()["object_content_payload"]  # type: ignore[attr-defined]
    projected = record.to_ecj1()  # type: ignore[attr-defined]
    if stored != projected:
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


def _definition_collections(
    definition: ActionDefinition,
) -> tuple[tuple[ObjectRef, ...], ...]:
    return (
        definition.input_quantity_refs,
        definition.output_quantity_refs,
        definition.write_support.coordinate_refs,
        definition.constraint_support.constraint_refs,
        definition.prerequisite_refs,
        definition.physical_effect_refs,
        definition.conversion_refs,
        definition.loss_refs,
        definition.resource_use_refs,
        definition.burden_refs,
        definition.completion_condition_refs,
        definition.failure_condition_refs,
        definition.compatible_boundary_refs,
        definition.horizon_refs,
    )


def _instance_collections(
    instance: ActionInstance,
) -> tuple[tuple[ObjectRef, ...], ...]:
    return (
        instance.write_support.coordinate_refs,
        instance.constraint_support.constraint_refs,
        instance.prerequisite_refs,
        instance.commitment_refs,
        instance.reservation_refs,
    )


def _interval_reversed(interval: EffectiveInterval) -> bool:
    return interval.end.tick.value < interval.start.tick.value


def validate_action_definition(definition: ActionDefinition, /) -> None:
    if type(definition) is not ActionDefinition:
        _formation_failure("ActionDefinition")
    interface = "validate_action_definition"
    _object_content_check(definition, interface, "argument 1 (definition)")

    collections = _definition_collections(definition)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if not definition.completion_condition_refs:
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)
    if not _object_hash_matches(definition):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_action_instance(
    instance: ActionInstance,
    route: RoutePlan | Applicability,
    /,
) -> None:
    if type(instance) is not ActionInstance:
        _formation_failure("ActionInstance")

    network_module = sys.modules.get("ebu_framework.network")
    route_plan_type = (
        None if network_module is None else getattr(network_module, "RoutePlan", None)
    )
    route_is_plan = route_plan_type is not None and type(route) is route_plan_type
    if not route_is_plan and type(route) is not Applicability:
        _formation_failure("RoutePlan")
    interface = "validate_action_instance"
    _object_content_check(instance, interface, "argument 1 (instance)")
    if route_is_plan:
        _object_content_check(route, interface, "argument 2 (route)")

    if instance.route_ref is Applicability.APPLICABLE or route is Applicability.APPLICABLE:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)

    collections = _instance_collections(instance)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if _interval_reversed(instance.effective_interval):
        _failure(FailureCode.ACTION_DECLARATION_INVALID, interface)

    paired = False
    if type(instance.route_ref) is ObjectRef and route_is_plan:
        route_ref = ObjectRef(
            object_id=route.envelope.object_id,  # type: ignore[union-attr]
            object_version=route.envelope.object_version,  # type: ignore[union-attr]
            object_content_hash=route.envelope.object_content_hash,  # type: ignore[union-attr]
        )
        paired = (
            instance.route_ref == route_ref
            and route.route_semantics_status.value  # type: ignore[union-attr]
            == "PROVISIONAL_PART_VII"
        )
    elif (
        instance.route_ref is Applicability.NOT_APPLICABLE
        and route is Applicability.NOT_APPLICABLE
    ):
        paired = True
    if not paired:
        _failure(FailureCode.PROVISIONAL_ROUTE_REQUIRED, interface)

    if not _object_hash_matches(instance) or (
        route_is_plan and not _object_hash_matches(route)
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


_DEPENDENCY_SENTINEL = SystemState


__all__ = (
    "ActionDefinition",
    "ActionInstance",
    "EffectiveInterval",
    "WriteSupport",
    "ConstraintSupport",
    "ActionStatus",
    "validate_action_definition",
    "validate_action_instance",
)
