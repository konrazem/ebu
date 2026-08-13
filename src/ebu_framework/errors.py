"""Typed I-1 failure values.

The framework raises :class:`FrameworkError` internally so callers can inspect
the immutable :class:`FailureEnvelope`.  The exception is intentionally not a
package-root export; protected-boundary behavior belongs to later stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class FailureCode(StrEnum):
    """Machine-readable failures constructible during I-1."""

    CANONICALIZATION_FAILURE = "CANONICALIZATION_FAILURE"
    INVALID_ECJ1 = "INVALID_ECJ1"
    NONCANONICAL_ECJ1 = "NONCANONICAL_ECJ1"
    ECJ1_TYPE_UNSUPPORTED = "ECJ1_TYPE_UNSUPPORTED"
    FLOAT_FORBIDDEN = "FLOAT_FORBIDDEN"
    CYCLIC_OBJECT_GRAPH = "CYCLIC_OBJECT_GRAPH"
    DUPLICATE_OBJECT_NAME = "DUPLICATE_OBJECT_NAME"
    INVALID_UNICODE_SCALAR = "INVALID_UNICODE_SCALAR"
    UNASSIGNED_UNICODE_SCALAR = "UNASSIGNED_UNICODE_SCALAR"
    UNICODE_DATA_INTEGRITY_FAILURE = "UNICODE_DATA_INTEGRITY_FAILURE"
    UNICODE_DATA_MALFORMED = "UNICODE_DATA_MALFORMED"
    SCIENTIFIC_ID_INVALID = "SCIENTIFIC_ID_INVALID"
    SEMANTIC_VERSION_INVALID = "SEMANTIC_VERSION_INVALID"
    DIGEST_INVALID = "DIGEST_INVALID"
    DIGEST_TYPE_MISMATCH = "DIGEST_TYPE_MISMATCH"
    HASH_DOMAIN_MISMATCH = "HASH_DOMAIN_MISMATCH"
    ARTIFACT_TOO_LARGE = "ARTIFACT_TOO_LARGE"
    STABLE_KEY_INVALID = "STABLE_KEY_INVALID"
    NAMESPACE_UNREGISTERED = "NAMESPACE_UNREGISTERED"
    RESERVED_NAMESPACE = "RESERVED_NAMESPACE"
    ALLOCATION_COLLISION = "ALLOCATION_COLLISION"
    ALLOCATION_CLAIM_CONFLICT = "ALLOCATION_CLAIM_CONFLICT"
    REGISTRY_IMMUTABLE = "REGISTRY_IMMUTABLE"
    REGISTRY_RECORD_CONFLICT = "REGISTRY_RECORD_CONFLICT"
    ALIAS_CONFLICT = "ALIAS_CONFLICT"
    ALIAS_INVALID = "ALIAS_INVALID"
    REF_NOT_FOUND = "REF_NOT_FOUND"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    HASH_MISMATCH = "HASH_MISMATCH"


class StateAdvance(StrEnum):
    NONE = "NONE"
    ATOMIC_COMPLETE = "ATOMIC_COMPLETE"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"


class PolicyMemoryAdvance(StrEnum):
    NONE = "NONE"
    ATOMIC_COMPLETE = "ATOMIC_COMPLETE"
    UNRESOLVED = "UNRESOLVED"


class DurabilityState(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NONE_DURABLE = "NONE_DURABLE"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"


class RetryClass(StrEnum):
    FORBIDDEN = "FORBIDDEN"
    SAME_BYTES_ONLY = "SAME_BYTES_ONLY"
    REQUIRES_AUTHORITY = "REQUIRES_AUTHORITY"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True, slots=True)
class FailureEnvelope:
    """Immutable failure classification without domain behavior."""

    failure_code: FailureCode
    human_summary: str
    stage: str = "I-1"
    interface_ref: str = "NOT_APPLICABLE"
    object_refs: tuple[Any, ...] = ()
    event_key: Any | None = None
    state_advance: StateAdvance = StateAdvance.NONE
    policy_memory_advance: PolicyMemoryAdvance = PolicyMemoryAdvance.NONE
    durability_state: DurabilityState = DurabilityState.NOT_APPLICABLE
    scientific_status_effect: str = "NONE"
    retry_class: RetryClass = RetryClass.NOT_APPLICABLE
    evidence_refs: tuple[Any, ...] = ()


class FrameworkError(ValueError):
    """Internal exception carrying a typed, immutable failure envelope."""

    def __init__(
        self,
        code: FailureCode,
        summary: str,
        *,
        interface_ref: str = "NOT_APPLICABLE",
        object_refs: tuple[Any, ...] = (),
    ) -> None:
        self.envelope = FailureEnvelope(
            failure_code=code,
            human_summary=summary,
            interface_ref=interface_ref,
            object_refs=object_refs,
        )
        super().__init__(f"{code.value}: {summary}")


def _fail(
    code: FailureCode,
    summary: str,
    *,
    interface_ref: str = "NOT_APPLICABLE",
    object_refs: tuple[Any, ...] = (),
) -> "NoReturn":
    raise FrameworkError(
        code,
        summary,
        interface_ref=interface_ref,
        object_refs=object_refs,
    )


from typing import NoReturn  # noqa: E402  (keeps the public imports compact)


__all__ = (
    "DurabilityState",
    "FailureCode",
    "FailureEnvelope",
    "PolicyMemoryAdvance",
    "RetryClass",
    "StateAdvance",
)
