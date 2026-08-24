"""Prospective Framework I-5 T3 declarations with fail-closed bodies."""

from __future__ import annotations

from dataclasses import dataclass
from enum import EnumType, StrEnum
from typing import NoReturn

from . import authorization as _authorization
from . import authorization_use as _authorization_use
from . import capabilities as _capabilities
from . import experiment as _experiment
from .events import EventKey, PhaseCommitRecord, PhaseOrdinal
from .ownership import EpochUpdateOwnership
from .durability import AtomicStoreRequest
from .traces import RunTraceEnvelopeV1
from . import actions as _actions
from .state import StatePayloadHash
from . import policy as _policy
from . import scheduling as _scheduling
from . import faults as _faults
from .identity import ObjectRef
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.execution", name, "1.0.0")


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.I5,
        interface_ref=_interface(interface),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I5_RECORD_FORMATION_INVALID, interface)


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


class _I5EnumType(EnumType):
    def __call__(cls, *args: object, **kwargs: object):
        if len(args) != 1 or kwargs or type(args[0]) is not str:
            _formation_failure(cls.__name__)
        try:
            return super().__call__(*args)
        except (TypeError, ValueError):
            _formation_failure(cls.__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class ProposalRecord:
    event_key: EventKey
    proposal_ref: ObjectRef
    common_pre_state_hash: StatePayloadHash
    proposed_update_refs: tuple[ObjectRef, ...]


class ScreeningDisposition(StrEnum, metaclass=_I5EnumType):
    ADMIT = "ADMIT"
    REJECT = "REJECT"
    DEFER = "DEFER"
    PARTIAL = "PARTIAL"


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class ScreeningResult:
    proposal_ref: ObjectRef
    disposition: ScreeningDisposition
    admitted_update_refs: tuple[ObjectRef, ...]
    reason_refs: tuple[ObjectRef, ...]


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class PhaseCommitRequest:
    phase_ordinal: PhaseOrdinal
    proposals: tuple[ProposalRecord, ...]
    screening_results: tuple[ScreeningResult, ...]
    ownership: EpochUpdateOwnership
    atomic_request: AtomicStoreRequest


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class T3EntryGuard:
    stage_authorization_ref: ObjectRef
    authorization_use_ref: ObjectRef
    execution_binding_ref: ObjectRef
    capability_ref: ObjectRef
    real_durability_backend_ref: ObjectRef | Applicability


@_strict_formation
@dataclass(frozen=True, slots=True, order=True, kw_only=True)
class ScientificExecutionLease:
    guard: T3EntryGuard
    lease_ref: ObjectRef
    operation: str
    consumed: bool


def _guard_formation(guard: object) -> bool:
    return (
        type(guard) is T3EntryGuard
        and type(guard.stage_authorization_ref) is ObjectRef
        and type(guard.authorization_use_ref) is ObjectRef
        and type(guard.execution_binding_ref) is ObjectRef
        and type(guard.capability_ref) is ObjectRef
        and (
            type(guard.real_durability_backend_ref) is ObjectRef
            or guard.real_durability_backend_ref
            is Applicability.NOT_APPLICABLE
        )
    )


def _require_i5_unavailable_backend(guard: T3EntryGuard, /) -> NoReturn:
    _failure(
        FailureCode.REAL_DURABILITY_BACKEND_UNAVAILABLE,
        "_require_i5_unavailable_backend",
    )


def validate_t3_entry_guard(guard: T3EntryGuard, /) -> None:
    interface = "validate_t3_entry_guard"
    if not _guard_formation(guard):
        _formation_failure(interface)
    if guard.real_durability_backend_ref is not Applicability.NOT_APPLICABLE:
        _failure(FailureCode.T3_ENTRY_GUARD_FAILED, interface)
    _require_i5_unavailable_backend(guard)


def validate_scientific_execution_lease(
    lease: ScientificExecutionLease, operation: str, /
) -> None:
    interface = "validate_scientific_execution_lease"
    if not (
        type(lease) is ScientificExecutionLease
        and type(lease.guard) is T3EntryGuard
        and type(lease.lease_ref) is ObjectRef
        and type(lease.operation) is str
        and bool(lease.operation)
        and type(lease.consumed) is bool
        and type(operation) is str
        and bool(operation)
    ):
        _formation_failure(interface)
    if lease.consumed or lease.operation != operation:
        _failure(FailureCode.SCIENTIFIC_EXECUTION_LEASE_INVALID, interface)
    validate_t3_entry_guard(lease.guard)


def begin_bound_scientific_execution(
    *, guard: T3EntryGuard, requested_operation: str
) -> ScientificExecutionLease:
    if type(requested_operation) is not str or not requested_operation:
        _formation_failure("begin_bound_scientific_execution")
    validate_t3_entry_guard(guard)


def propose_phase_updates(
    *,
    lease: ScientificExecutionLease,
    phase: PhaseOrdinal,
    state_ref: ObjectRef,
    adapter_ref: ObjectRef,
) -> tuple[ProposalRecord, ...]:
    validate_scientific_execution_lease(lease, "propose_phase_updates")
    _failure(
        FailureCode.EXECUTION_CALLBACK_FORBIDDEN,
        "propose_phase_updates",
    )


def screen_and_admit(
    *,
    lease: ScientificExecutionLease,
    proposals: tuple[ProposalRecord, ...],
    screening_adapter_ref: ObjectRef,
) -> tuple[ScreeningResult, ...]:
    validate_scientific_execution_lease(lease, "screen_and_admit")
    _failure(FailureCode.EXECUTION_CALLBACK_FORBIDDEN, "screen_and_admit")


def propose_joint_transition(
    *,
    lease: ScientificExecutionLease,
    proposals: tuple[ProposalRecord, ...],
    joint_adapter_ref: ObjectRef,
) -> ProposalRecord:
    validate_scientific_execution_lease(lease, "propose_joint_transition")
    _failure(
        FailureCode.EXECUTION_CALLBACK_FORBIDDEN,
        "propose_joint_transition",
    )


def commit_phase_updates(
    *, lease: ScientificExecutionLease, request: PhaseCommitRequest
) -> PhaseCommitRecord:
    validate_scientific_execution_lease(lease, "commit_phase_updates")
    _failure(
        FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
        "commit_phase_updates",
    )


def advance_epoch(
    *,
    lease: ScientificExecutionLease,
    epoch: int,
    initial_state_ref: ObjectRef,
    phase_input_refs: tuple[ObjectRef, ...],
) -> RunTraceEnvelopeV1:
    validate_scientific_execution_lease(lease, "advance_epoch")
    _failure(
        FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
        "advance_epoch",
    )


__all__ = (
    "ProposalRecord",
    "ScreeningDisposition",
    "ScreeningResult",
    "PhaseCommitRequest",
    "T3EntryGuard",
    "ScientificExecutionLease",
    "validate_t3_entry_guard",
    "validate_scientific_execution_lease",
    "begin_bound_scientific_execution",
    "propose_phase_updates",
    "screen_and_admit",
    "propose_joint_transition",
    "commit_phase_updates",
    "advance_epoch",
)
