"""Immutable I-3 network declarations and locally observable T0 validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, NoReturn

from .state import SystemState
from .actions import EffectiveInterval
from .primitives import Epoch
from .identity import ObjectRef
from .envelopes import CommonObjectEnvelope, validate_object_envelope
from .registry import NamespaceRegistrySnapshot
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
    return FailureInterfaceRef("ebu_framework.network", name, "1.0.0")


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


class RouteSemanticsStatus(StrEnum):
    PROVISIONAL_PART_VII = "PROVISIONAL_PART_VII"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("RouteSemanticsStatus")


class AvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    REPAIRING = "REPAIRING"
    UNRESOLVED = "UNRESOLVED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("AvailabilityStatus")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class Provider:
    envelope: CommonObjectEnvelope
    provider_kind_ref: ObjectRef
    offered_resource_type_refs: tuple[ObjectRef, ...]
    offered_service_type_refs: tuple[ObjectRef, ...]
    capability_refs: tuple[ObjectRef, ...]
    boundary_refs: tuple[ObjectRef, ...]
    availability_status: AvailabilityStatus

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.provider_kind_ref) is ObjectRef
            and all(
                _object_ref_tuple(values)
                for values in (
                    self.offered_resource_type_refs,
                    self.offered_service_type_refs,
                    self.capability_refs,
                    self.boundary_refs,
                )
            )
            and type(self.availability_status) is AvailabilityStatus
        ):
            _formation_failure("Provider")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class ProviderNetwork:
    envelope: CommonObjectEnvelope
    provider_refs: tuple[ObjectRef, ...]
    node_refs: tuple[ObjectRef, ...]
    edge_refs: tuple[ObjectRef, ...]
    resource_type_refs: tuple[ObjectRef, ...]
    service_type_refs: tuple[ObjectRef, ...]
    topology_snapshot_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                _object_ref_tuple(values)
                for values in (
                    self.provider_refs,
                    self.node_refs,
                    self.edge_refs,
                    self.resource_type_refs,
                    self.service_type_refs,
                )
            )
            and type(self.topology_snapshot_ref) is ObjectRef
        ):
            _formation_failure("ProviderNetwork")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class TopologySnapshot:
    envelope: CommonObjectEnvelope
    network_ref: ObjectRef
    valid_interval: EffectiveInterval
    provider_refs: tuple[ObjectRef, ...]
    node_refs: tuple[ObjectRef, ...]
    edge_refs: tuple[ObjectRef, ...]
    availability_record_refs: tuple[ObjectRef, ...]
    capacity_record_refs: tuple[ObjectRef, ...]
    delay_model_refs: tuple[ObjectRef, ...]
    conversion_refs: tuple[ObjectRef, ...]
    loss_refs: tuple[ObjectRef, ...]
    uncertainty_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.network_ref) is ObjectRef
            and type(self.valid_interval) is EffectiveInterval
            and all(
                _object_ref_tuple(values)
                for values in (
                    self.provider_refs,
                    self.node_refs,
                    self.edge_refs,
                    self.availability_record_refs,
                    self.capacity_record_refs,
                    self.delay_model_refs,
                    self.conversion_refs,
                    self.loss_refs,
                    self.uncertainty_refs,
                )
            )
        ):
            _formation_failure("TopologySnapshot")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class CapacityLocus:
    envelope: CommonObjectEnvelope
    network_ref: ObjectRef
    locus_kind: Literal["NODE", "EDGE", "PROVIDER"]
    locus_ref: ObjectRef
    resource_type_ref: ObjectRef
    service_type_ref: ObjectRef | Applicability
    boundary_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and all(
                type(value) is ObjectRef
                for value in (
                    self.network_ref,
                    self.locus_ref,
                    self.resource_type_ref,
                    self.boundary_ref,
                )
            )
            and type(self.locus_kind) is str
            and self.locus_kind in {"NODE", "EDGE", "PROVIDER"}
            and _object_or_applicability(self.service_type_ref)
        ):
            _formation_failure("CapacityLocus")

    def to_ecj1(self) -> dict[str, object]:
        return {
            field: _project(getattr(self, field))
            for field in self.__dataclass_fields__
            if field != "envelope"
        }


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class RoutePlan:
    envelope: CommonObjectEnvelope
    origin_ref: ObjectRef
    destination_ref: ObjectRef
    ordered_segment_refs: tuple[ObjectRef, ...]
    planning_epoch: Epoch
    information_snapshot_ref: ObjectRef
    expected_capacity_ref: ObjectRef | Applicability
    expected_delay_ref: ObjectRef | Applicability
    unfinished_suffix_refs: tuple[ObjectRef, ...]
    route_semantics_status: RouteSemanticsStatus | Applicability

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.origin_ref) is ObjectRef
            and type(self.destination_ref) is ObjectRef
            and _object_ref_tuple(self.ordered_segment_refs)
            and type(self.planning_epoch) is Epoch
            and type(self.information_snapshot_ref) is ObjectRef
            and _object_or_applicability(self.expected_capacity_ref)
            and _object_or_applicability(self.expected_delay_ref)
            and _object_ref_tuple(self.unfinished_suffix_refs)
            and (
                type(self.route_semantics_status) is RouteSemanticsStatus
                or type(self.route_semantics_status) is Applicability
            )
        ):
            _formation_failure("RoutePlan")

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


def _provider_network_collections(
    provider: Provider,
    network: ProviderNetwork,
    topology: TopologySnapshot,
) -> tuple[tuple[ObjectRef, ...], ...]:
    return (
        provider.offered_resource_type_refs,
        provider.offered_service_type_refs,
        provider.capability_refs,
        provider.boundary_refs,
        network.provider_refs,
        network.node_refs,
        network.edge_refs,
        network.resource_type_refs,
        network.service_type_refs,
        topology.provider_refs,
        topology.node_refs,
        topology.edge_refs,
        topology.availability_record_refs,
        topology.capacity_record_refs,
        topology.delay_model_refs,
        topology.conversion_refs,
        topology.loss_refs,
        topology.uncertainty_refs,
    )


def validate_provider_network(
    provider: Provider,
    network: ProviderNetwork,
    topology: TopologySnapshot,
    locus: CapacityLocus,
    /,
) -> None:
    for value, expected, name in (
        (provider, Provider, "Provider"),
        (network, ProviderNetwork, "ProviderNetwork"),
        (topology, TopologySnapshot, "TopologySnapshot"),
        (locus, CapacityLocus, "CapacityLocus"),
    ):
        if type(value) is not expected:
            _formation_failure(name)

    interface = "validate_provider_network"
    for record, position in (
        (provider, "argument 1 (provider)"),
        (network, "argument 2 (network)"),
        (topology, "argument 3 (topology)"),
        (locus, "argument 4 (locus)"),
    ):
        _object_content_check(record, interface, position)

    if locus.service_type_ref is Applicability.APPLICABLE:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    collections = _provider_network_collections(provider, network, topology)
    if any(not _ordered_refs(values) for values in collections):
        _failure(FailureCode.I3_COLLECTION_ORDER_INVALID, interface)
    if any(_duplicate_refs(values) for values in collections):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if not all(
        _object_hash_matches(record)
        for record in (provider, network, topology, locus)
    ):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


def validate_route_plan(route: RoutePlan, /) -> None:
    if type(route) is not RoutePlan:
        _formation_failure("RoutePlan")
    interface = "validate_route_plan"
    _object_content_check(route, interface, "argument 1 (route)")

    if any(
        value is Applicability.APPLICABLE
        for value in (
            route.expected_capacity_ref,
            route.expected_delay_ref,
            route.route_semantics_status,
        )
    ):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface)
    if _duplicate_refs(route.ordered_segment_refs):
        _failure(FailureCode.I3_DUPLICATE_MEMBER, interface)
    if route.route_semantics_status is not RouteSemanticsStatus.PROVISIONAL_PART_VII:
        _failure(FailureCode.PROVISIONAL_ROUTE_REQUIRED, interface)
    if not _object_hash_matches(route):
        _failure(FailureCode.HASH_MISMATCH, interface)
    return None


# Preserve the committed dependency edges without resolving opaque references.
_DEPENDENCY_SENTINELS = (SystemState, NamespaceRegistrySnapshot)


__all__ = (
    "Provider",
    "ProviderNetwork",
    "TopologySnapshot",
    "CapacityLocus",
    "RoutePlan",
    "RouteSemanticsStatus",
    "AvailabilityStatus",
    "validate_provider_network",
    "validate_route_plan",
)
