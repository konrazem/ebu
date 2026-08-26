"""Typed, deterministic framework failure values.

The I-2 extension keeps the accepted I-1 ``_fail(code, summary)`` call shape
closed to the four I-1 caller modules while requiring every newer boundary to
name its stage and interface explicitly.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import inspect
import re
import unicodedata
from typing import NoReturn


_SEGMENT_RE = re.compile(r"[a-z0-9][a-z0-9._-]*", re.ASCII)
_SCIENTIFIC_ID_RE = re.compile(
    r"ebu:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*",
    re.ASCII,
)
_SEMANTIC_VERSION_RE = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII
)
_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}", re.ASCII)
_RAW_DIGEST_RE = re.compile(r"sha256-raw:[0-9a-f]{64}", re.ASCII)
_FAILURE_ID_RE = re.compile(r"ebu:failure:core:sha256-[0-9a-f]{64}", re.ASCII)
_LEGACY_I1_MODULES = frozenset(
    {
        "ebu_framework.canonical",
        "ebu_framework.hashing",
        "ebu_framework.identity",
        "ebu_framework.registry",
    }
)
_I4_FAILURE_ORDINAL: ContextVar[int] = ContextVar(
    "ebu_i4_failure_ordinal", default=0
)
_I4_ORDERED_CHECK_NAME: ContextVar[str | None] = ContextVar(
    "ebu_i4_ordered_check_name", default=None
)


class FailureCode(StrEnum):
    """The closed I-1 plus I-2 machine-readable failure domain."""

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
    BOUNDARY_MISMATCH = "BOUNDARY_MISMATCH"
    CLOCK_MISMATCH = "CLOCK_MISMATCH"
    CONVERSION_RULE_MISMATCH = "CONVERSION_RULE_MISMATCH"
    CORE_NUMBER_INVALID = "CORE_NUMBER_INVALID"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    DIVISION_BY_ZERO = "DIVISION_BY_ZERO"
    ERROR_BOUND_INVALID = "ERROR_BOUND_INVALID"
    HORIZON_INVALID = "HORIZON_INVALID"
    IMPLICIT_ABSENCE_FORBIDDEN = "IMPLICIT_ABSENCE_FORBIDDEN"
    IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN = (
        "IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN"
    )
    INVALID_AGGREGATION = "INVALID_AGGREGATION"
    LIFECYCLE_TRANSITION_INVALID = "LIFECYCLE_TRANSITION_INVALID"
    NONFINITE_NUMBER_FORBIDDEN = "NONFINITE_NUMBER_FORBIDDEN"
    NUMERICAL_OPERATION_UNSUPPORTED = "NUMERICAL_OPERATION_UNSUPPORTED"
    NUMERICAL_POLICY_INCOMPLETE = "NUMERICAL_POLICY_INCOMPLETE"
    NUMERICAL_POLICY_REQUIRED = "NUMERICAL_POLICY_REQUIRED"
    QUANTITY_TYPE_MISMATCH = "QUANTITY_TYPE_MISMATCH"
    REGION_MISMATCH = "REGION_MISMATCH"
    RESOLUTION_STATE_INVALID = "RESOLUTION_STATE_INVALID"
    SIGN_CONVENTION_MISMATCH = "SIGN_CONVENTION_MISMATCH"
    SUPERSESSION_INVALID = "SUPERSESSION_INVALID"
    TIME_BASIS_MISMATCH = "TIME_BASIS_MISMATCH"
    UNCERTAINTY_RECORD_INVALID = "UNCERTAINTY_RECORD_INVALID"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    I3_RECORD_FORMATION_INVALID = "I3_RECORD_FORMATION_INVALID"
    I3_OBJECT_CONTENT_MISMATCH = "I3_OBJECT_CONTENT_MISMATCH"
    I3_COLLECTION_ORDER_INVALID = "I3_COLLECTION_ORDER_INVALID"
    I3_DUPLICATE_MEMBER = "I3_DUPLICATE_MEMBER"
    STATE_PROJECTION_FAILURE = "STATE_PROJECTION_FAILURE"
    MISSING_COORDINATE = "MISSING_COORDINATE"
    POLICY_MEMORY_NOT_APPLICABLE = "POLICY_MEMORY_NOT_APPLICABLE"
    EPOCH_MISMATCH = "EPOCH_MISMATCH"
    CONSERVATION_PROFILE_INVALID = "CONSERVATION_PROFILE_INVALID"
    CONSERVATION_LEVEL_REQUIREMENT_MISSING = (
        "CONSERVATION_LEVEL_REQUIREMENT_MISSING"
    )
    CONSERVATION_QUANTITY_DUPLICATE = "CONSERVATION_QUANTITY_DUPLICATE"
    CONSERVATION_COORDINATE_DUPLICATE = "CONSERVATION_COORDINATE_DUPLICATE"
    CONSERVATION_FLOW_CHANNEL_DUPLICATE = (
        "CONSERVATION_FLOW_CHANNEL_DUPLICATE"
    )
    CONSERVATION_UNIT_MISMATCH = "CONSERVATION_UNIT_MISMATCH"
    CONSERVATION_EVIDENCE_INCOMPLETE = "CONSERVATION_EVIDENCE_INCOMPLETE"
    CONSERVATION_ISOLATION_INVALID = "CONSERVATION_ISOLATION_INVALID"
    CONSERVATION_TOLERANCE_UNDECLARED = (
        "CONSERVATION_TOLERANCE_UNDECLARED"
    )
    PHYSICAL_POLICY_MEMORY_CONFLATION = "PHYSICAL_POLICY_MEMORY_CONFLATION"
    DISTORTION_DECLARATION_INVALID = "DISTORTION_DECLARATION_INVALID"
    ACTION_DECLARATION_INVALID = "ACTION_DECLARATION_INVALID"
    RESERVATION_CAPACITY_MISMATCH = "RESERVATION_CAPACITY_MISMATCH"
    MEASUREMENT_CONTRACT_MISMATCH = "MEASUREMENT_CONTRACT_MISMATCH"
    INADMISSIBLE_SCHEDULE = "INADMISSIBLE_SCHEDULE"
    MISSING_COMPARATOR = "MISSING_COMPARATOR"
    PROVISIONAL_ROUTE_REQUIRED = "PROVISIONAL_ROUTE_REQUIRED"
    INFORMATION_VIEW_DECLARATION_INVALID = (
        "INFORMATION_VIEW_DECLARATION_INVALID"
    )
    CAUSAL_ATTRIBUTION_UNRESOLVED = "CAUSAL_ATTRIBUTION_UNRESOLVED"
    SETTLEMENT_LINK_INVALID = "SETTLEMENT_LINK_INVALID"
    SETTLEMENT_CLOSURE_FAILURE = "SETTLEMENT_CLOSURE_FAILURE"
    LEDGER_LINK_INVALID = "LEDGER_LINK_INVALID"
    FAULT_SCHEDULE_INVALID = "FAULT_SCHEDULE_INVALID"
    FAULT_EXTENSION_UNAVAILABLE = "FAULT_EXTENSION_UNAVAILABLE"
    CONFIGURATION_INCOMPLETE = "CONFIGURATION_INCOMPLETE"
    EXECUTION_SEMANTICS_PROJECTION_FAILURE = (
        "EXECUTION_SEMANTICS_PROJECTION_FAILURE"
    )
    ARTIFACT_COMPLETENESS_INVALID = "ARTIFACT_COMPLETENESS_INVALID"
    EXTENT_DECLARATION_INVALID = "EXTENT_DECLARATION_INVALID"
    EXTENT_DIVISIBILITY_UNDECLARED = "EXTENT_DIVISIBILITY_UNDECLARED"
    ATOMIC_REFINEMENT_INVALID = "ATOMIC_REFINEMENT_INVALID"
    GENERATOR_DECLARATION_INVALID = "GENERATOR_DECLARATION_INVALID"
    GENERATOR_LINK_INVALID = "GENERATOR_LINK_INVALID"
    AUGMENTED_STATE_INCOMPLETE = "AUGMENTED_STATE_INCOMPLETE"
    REPARAMETERIZATION_WITNESS_INVALID = "REPARAMETERIZATION_WITNESS_INVALID"
    HYBRID_ACTIVATION_INVALID = "HYBRID_ACTIVATION_INVALID"
    FIXED_ACTIVATION_ACCOUNT_DUPLICATED = "FIXED_ACTIVATION_ACCOUNT_DUPLICATED"
    RECONSTRUCTION_CLAIM_UNSUPPORTED = "RECONSTRUCTION_CLAIM_UNSUPPORTED"
    BOUNDARY_HISTORY_EQUIVALENCE_INVALID = (
        "BOUNDARY_HISTORY_EQUIVALENCE_INVALID"
    )
    BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE = (
        "BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE"
    )
    FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR = (
        "FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR"
    )
    VALIDATOR_BYPASS_FORBIDDEN = "VALIDATOR_BYPASS_FORBIDDEN"
    OBJECTIVE_GRAMMAR_INVALID = "OBJECTIVE_GRAMMAR_INVALID"
    SUBSET_PROTOCOL_INCOMPLETE = "SUBSET_PROTOCOL_INCOMPLETE"
    SUBSET_LATTICE_INCOMPLETE = "SUBSET_LATTICE_INCOMPLETE"
    MOBIUS_CLOSURE_FAILURE = "MOBIUS_CLOSURE_FAILURE"
    TRUNCATION_RESIDUAL_MISMATCH = "TRUNCATION_RESIDUAL_MISMATCH"
    COMPARATOR_INTERACTION_INVALID = "COMPARATOR_INTERACTION_INVALID"
    MIXED_MARGINAL_WITNESS_INVALID = "MIXED_MARGINAL_WITNESS_INVALID"
    COMMUTATOR_WITNESS_INVALID = "COMMUTATOR_WITNESS_INVALID"
    COMMUTATIVITY_SCOPE_OVERCLAIM = "COMMUTATIVITY_SCOPE_OVERCLAIM"
    SHARED_CONSTRAINT_OWNERSHIP_INVALID = "SHARED_CONSTRAINT_OWNERSHIP_INVALID"
    SHARED_BOUNDARY_VISIBILITY_MISSING = "SHARED_BOUNDARY_VISIBILITY_MISSING"
    INTERACTION_TOPOLOGY_INVALID = "INTERACTION_TOPOLOGY_INVALID"
    HIDDEN_STATE_TOPOLOGY_UNRESOLVED = "HIDDEN_STATE_TOPOLOGY_UNRESOLVED"
    BOUNDARY_INTERACTION_PRESERVATION_INVALID = (
        "BOUNDARY_INTERACTION_PRESERVATION_INVALID"
    )
    ALLOCATION_FEASIBILITY_INVALID = "ALLOCATION_FEASIBILITY_INVALID"
    OPTIMALITY_CERTIFICATE_INAPPLICABLE = "OPTIMALITY_CERTIFICATE_INAPPLICABLE"
    SCALAR_DECOMPOSITION_INVALID = "SCALAR_DECOMPOSITION_INVALID"
    DECOMPOSITION_PROVENANCE_INCOMPLETE = "DECOMPOSITION_PROVENANCE_INCOMPLETE"
    INSTITUTIONAL_RULE_INVALID = "INSTITUTIONAL_RULE_INVALID"
    CAUSAL_SETTLEMENT_CONFLATION = "CAUSAL_SETTLEMENT_CONFLATION"
    SETTLEMENT_RESIDUAL_CLOSURE_MISSING = "SETTLEMENT_RESIDUAL_CLOSURE_MISSING"
    PROHIBITED_INTERFERENCE_CLAIM = "PROHIBITED_INTERFERENCE_CLAIM"
    I4_RECORD_FORMATION_INVALID = "I4_RECORD_FORMATION_INVALID"
    PRODUCTION_BOOTSTRAP_MISSING = "PRODUCTION_BOOTSTRAP_MISSING"
    TRUST_PROFILE_PIN_MISMATCH = "TRUST_PROFILE_PIN_MISMATCH"
    SIGNATURE_PROFILE_UNSUPPORTED = "SIGNATURE_PROFILE_UNSUPPORTED"
    KEY_ID_MISMATCH = "KEY_ID_MISMATCH"
    PUBLIC_KEY_INVALID = "PUBLIC_KEY_INVALID"
    SIGNATURE_ENCODING_INVALID = "SIGNATURE_ENCODING_INVALID"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    ROOT_THRESHOLD_NOT_MET = "ROOT_THRESHOLD_NOT_MET"
    ROOT_PROOF_ORDER_INVALID = "ROOT_PROOF_ORDER_INVALID"
    ISSUER_REGISTRY_INVALID = "ISSUER_REGISTRY_INVALID"
    ISSUER_REGISTRY_ROLLBACK = "ISSUER_REGISTRY_ROLLBACK"
    ISSUER_REGISTRY_GAP = "ISSUER_REGISTRY_GAP"
    ISSUER_REGISTRY_EQUIVOCATION = "ISSUER_REGISTRY_EQUIVOCATION"
    ISSUER_KEY_INVALID = "ISSUER_KEY_INVALID"
    DELEGATION_CHAIN_INVALID = "DELEGATION_CHAIN_INVALID"
    DELEGATION_SCOPE_ESCALATION = "DELEGATION_SCOPE_ESCALATION"
    DELEGATION_DEPTH_EXCEEDED = "DELEGATION_DEPTH_EXCEEDED"
    DELEGATION_CYCLE = "DELEGATION_CYCLE"
    TRUSTED_TIME_UNAVAILABLE = "TRUSTED_TIME_UNAVAILABLE"
    TRUSTED_TIME_CHALLENGE_MISMATCH = "TRUSTED_TIME_CHALLENGE_MISMATCH"
    TRUSTED_TIME_STALE = "TRUSTED_TIME_STALE"
    TRUSTED_TIME_SEQUENCE_INVALID = "TRUSTED_TIME_SEQUENCE_INVALID"
    REVOCATION_UNAVAILABLE = "REVOCATION_UNAVAILABLE"
    REVOCATION_SNAPSHOT_EXPIRED = "REVOCATION_SNAPSHOT_EXPIRED"
    REVOCATION_ROLLBACK = "REVOCATION_ROLLBACK"
    REVOCATION_GAP = "REVOCATION_GAP"
    REVOCATION_EQUIVOCATION = "REVOCATION_EQUIVOCATION"
    AUTHORIZATION_REVOKED = "AUTHORIZATION_REVOKED"
    AUTHORIZATION_SCOPE_MISMATCH = "AUTHORIZATION_SCOPE_MISMATCH"
    AUTHORIZATION_STAGE_MISMATCH = "AUTHORIZATION_STAGE_MISMATCH"
    AUTHORIZATION_OPERATION_MISMATCH = "AUTHORIZATION_OPERATION_MISMATCH"
    AUTHORIZATION_TARGET_MISMATCH = "AUTHORIZATION_TARGET_MISMATCH"
    AUTHORIZATION_CONFIGURATION_MISMATCH = "AUTHORIZATION_CONFIGURATION_MISMATCH"
    AUTHORIZATION_BINDING_MISMATCH = "AUTHORIZATION_BINDING_MISMATCH"
    AUTHORIZATION_EXECUTION_IDENTITY_MISMATCH = (
        "AUTHORIZATION_EXECUTION_IDENTITY_MISMATCH"
    )
    AUTHORIZATION_PREDECESSOR_MISMATCH = "AUTHORIZATION_PREDECESSOR_MISMATCH"
    AUTHORIZATION_LIFECYCLE_MISMATCH = "AUTHORIZATION_LIFECYCLE_MISMATCH"
    AUTHORIZATION_EXCLUSION_MATCH = "AUTHORIZATION_EXCLUSION_MATCH"
    BINDING_CONFIGURATION_MISMATCH = "BINDING_CONFIGURATION_MISMATCH"
    AUTHORIZATION_USE_ALREADY_CONSUMED = "AUTHORIZATION_USE_ALREADY_CONSUMED"
    AUTHORIZATION_USE_UNRESOLVED = "AUTHORIZATION_USE_UNRESOLVED"
    AUTHORIZATION_USE_STORE_UNSUPPORTED = "AUTHORIZATION_USE_STORE_UNSUPPORTED"
    AUTHORIZATION_USE_LEDGER_FAILURE = "AUTHORIZATION_USE_LEDGER_FAILURE"
    REGISTRY_ACCEPTANCE_INVALID = "REGISTRY_ACCEPTANCE_INVALID"
    REGISTRY_SUPERSESSION_INVALID = "REGISTRY_SUPERSESSION_INVALID"
    INFORMATION_CAPABILITY_INVALID = "INFORMATION_CAPABILITY_INVALID"
    INFORMATION_NOT_VISIBLE = "INFORMATION_NOT_VISIBLE"
    INFORMATION_NOT_AVAILABLE = "INFORMATION_NOT_AVAILABLE"
    INFORMATION_TOO_OLD = "INFORMATION_TOO_OLD"
    CURRENT_MEMORY_MISMATCH = "CURRENT_MEMORY_MISMATCH"
    INFORMATION_TRAVERSAL_FORBIDDEN = "INFORMATION_TRAVERSAL_FORBIDDEN"
    INFORMATION_READ_SET_DENIED = "INFORMATION_READ_SET_DENIED"
    VALIDATION_NAMESPACE_FORBIDDEN = "VALIDATION_NAMESPACE_FORBIDDEN"
    VALIDATION_KEY_FORBIDDEN = "VALIDATION_KEY_FORBIDDEN"
    DEPENDENCY_INTEGRITY_FAILURE = "DEPENDENCY_INTEGRITY_FAILURE"
    SQLITE_VERSION_UNSUPPORTED = "SQLITE_VERSION_UNSUPPORTED"
    SQLITE_SCHEMA_MISMATCH = "SQLITE_SCHEMA_MISMATCH"
    CAPABILITY_ESCALATION_FORBIDDEN = "CAPABILITY_ESCALATION_FORBIDDEN"
    POLICY_MEMORY_PROJECTION_FAILURE = "POLICY_MEMORY_PROJECTION_FAILURE"
    POLICY_MEMORY_MISMATCH = "POLICY_MEMORY_MISMATCH"
    I5_RECORD_FORMATION_INVALID = "I5_RECORD_FORMATION_INVALID"
    PHASE_ORDINAL_INVALID = "PHASE_ORDINAL_INVALID"
    EVENT_KEY_INVALID = "EVENT_KEY_INVALID"
    EVENT_KEY_DUPLICATE = "EVENT_KEY_DUPLICATE"
    EVENT_ORDER_INVALID = "EVENT_ORDER_INVALID"
    EVENT_IDENTITY_INVALID = "EVENT_IDENTITY_INVALID"
    PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER = (
        "PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER"
    )
    PHASE_PREDECESSOR_MISMATCH = "PHASE_PREDECESSOR_MISMATCH"
    PHASE_COMMIT_RECORD_INVALID = "PHASE_COMMIT_RECORD_INVALID"
    UPDATE_OWNERSHIP_CLAIM_INVALID = "UPDATE_OWNERSHIP_CLAIM_INVALID"
    INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN = (
        "INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN"
    )
    UPDATE_OWNERSHIP_CONFLICT = "UPDATE_OWNERSHIP_CONFLICT"
    OWNERSHIP_ORDER_INVALID = "OWNERSHIP_ORDER_INVALID"
    PHASE_OWNERSHIP_MISMATCH = "PHASE_OWNERSHIP_MISMATCH"
    ATOMIC_COMMIT_REQUEST_INVALID = "ATOMIC_COMMIT_REQUEST_INVALID"
    EXPECTED_TRACE_PREFIX_MISMATCH = "EXPECTED_TRACE_PREFIX_MISMATCH"
    COMMIT_REJECTED = "COMMIT_REJECTED"
    COMMIT_AMBIGUOUS = "COMMIT_AMBIGUOUS"
    DURABILITY_UNAVAILABLE = "DURABILITY_UNAVAILABLE"
    DURABILITY_EVIDENCE_MISSING = "DURABILITY_EVIDENCE_MISSING"
    DURABILITY_EVIDENCE_INCONSISTENT = "DURABILITY_EVIDENCE_INCONSISTENT"
    POLICY_MEMORY_TRANSACTION_INVALID = "POLICY_MEMORY_TRANSACTION_INVALID"
    PHYSICAL_PHASE_TRANSACTION_INVALID = "PHYSICAL_PHASE_TRANSACTION_INVALID"
    TRACE_ROW_INVALID = "TRACE_ROW_INVALID"
    TRACE_ROW_PREDECESSOR_MISMATCH = "TRACE_ROW_PREDECESSOR_MISMATCH"
    TRACE_ROW_GAP = "TRACE_ROW_GAP"
    TRACE_PREFIX_INVALID = "TRACE_PREFIX_INVALID"
    TRACE_PREFIX_NOT_LITERAL = "TRACE_PREFIX_NOT_LITERAL"
    TRACE_PREFIX_MUTATION_FORBIDDEN = "TRACE_PREFIX_MUTATION_FORBIDDEN"
    TRACE_EXTENSION_IDENTITY_INVALID = "TRACE_EXTENSION_IDENTITY_INVALID"
    TRACE_COMPLETENESS_INVALID = "TRACE_COMPLETENESS_INVALID"
    TRACE_EQUIVOCAL = "TRACE_EQUIVOCAL"
    TRACE_EVIDENCE_MISSING = "TRACE_EVIDENCE_MISSING"
    MINIMUM_TRACE_INCOMPLETE = "MINIMUM_TRACE_INCOMPLETE"
    RUN_TRACE_ENVELOPE_INVALID = "RUN_TRACE_ENVELOPE_INVALID"
    SCIENTIFIC_EXECUTION_LEASE_INVALID = "SCIENTIFIC_EXECUTION_LEASE_INVALID"
    T3_ENTRY_GUARD_FAILED = "T3_ENTRY_GUARD_FAILED"
    REAL_DURABILITY_BACKEND_UNAVAILABLE = (
        "REAL_DURABILITY_BACKEND_UNAVAILABLE"
    )
    EXECUTION_CALLBACK_FORBIDDEN = "EXECUTION_CALLBACK_FORBIDDEN"
    SCIENTIFIC_STATE_ADVANCE_FORBIDDEN = "SCIENTIFIC_STATE_ADVANCE_FORBIDDEN"
    I5_HASH_COLLISION = "I5_HASH_COLLISION"
    FAULT_HOOK_INVALID = "FAULT_HOOK_INVALID"
    I6_RECORD_FORMATION_INVALID = "I6_RECORD_FORMATION_INVALID"
    INCOMPATIBLE_BOUNDARY = "INCOMPATIBLE_BOUNDARY"
    UNRESOLVED_COUPLING = "UNRESOLVED_COUPLING"
    GROUPING_FAILURE = "GROUPING_FAILURE"
    DIAGNOSTIC_UNDEFINED = "DIAGNOSTIC_UNDEFINED"
    I7_RECORD_FORMATION_INVALID = "I7_RECORD_FORMATION_INVALID"
    DYNAMIC_STATE_INCOMPLETE = "DYNAMIC_STATE_INCOMPLETE"
    TOPOLOGY_LAYER_CONFLATION = "TOPOLOGY_LAYER_CONFLATION"
    TOPOLOGY_PROVENANCE_INVALID = "TOPOLOGY_PROVENANCE_INVALID"
    DOMAIN_DYNAMIC_AUTHORITY_MISSING = "DOMAIN_DYNAMIC_AUTHORITY_MISSING"
    AVAILABILITY_TRANSITION_INVALID = "AVAILABILITY_TRANSITION_INVALID"
    CAPACITY_IDENTITY_FAILURE = "CAPACITY_IDENTITY_FAILURE"
    CAPACITY_COMPLIANCE_FAILURE = "CAPACITY_COMPLIANCE_FAILURE"
    ADMISSION_BALANCE_FAILURE = "ADMISSION_BALANCE_FAILURE"
    QUEUE_BALANCE_FAILURE = "QUEUE_BALANCE_FAILURE"
    REJECTED_DEMAND_QUEUE_MUTATION = "REJECTED_DEMAND_QUEUE_MUTATION"
    RESERVATION_SHORTFALL_INVALID = "RESERVATION_SHORTFALL_INVALID"
    CONGESTION_DECLARATION_INVALID = "CONGESTION_DECLARATION_INVALID"
    DELAY_DECOMPOSITION_INVALID = "DELAY_DECOMPOSITION_INVALID"
    IN_TRANSIT_STATE_INVALID = "IN_TRANSIT_STATE_INVALID"
    DELAYED_EFFECT_STATUS_INVALID = "DELAYED_EFFECT_STATUS_INVALID"
    UPDATE_DOUBLE_APPLICATION_FORBIDDEN = (
        "UPDATE_DOUBLE_APPLICATION_FORBIDDEN"
    )
    NATURAL_DRIVE_PHASE_INVALID = "NATURAL_DRIVE_PHASE_INVALID"
    POLICY_MEMORY_PAIR_MISMATCH = "POLICY_MEMORY_PAIR_MISMATCH"
    COMMITMENT_STATE_MISMATCH = "COMMITMENT_STATE_MISMATCH"
    ROUTE_SEMANTICS_UNRESOLVED = "ROUTE_SEMANTICS_UNRESOLVED"
    COMPLETED_ROUTE_REWRITE_FORBIDDEN = (
        "COMPLETED_ROUTE_REWRITE_FORBIDDEN"
    )
    DYNAMIC_NUMERICAL_POLICY_UNACCEPTED = (
        "DYNAMIC_NUMERICAL_POLICY_UNACCEPTED"
    )
    DYNAMIC_STATIC_IDENTITY_MISMATCH = "DYNAMIC_STATIC_IDENTITY_MISMATCH"
    I8_RECORD_FORMATION_INVALID = "I8_RECORD_FORMATION_INVALID"
    SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7 = (
        "SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7"
    )
    PROVENANCE_INVENTORY_INVALID = "PROVENANCE_INVENTORY_INVALID"
    EXECUTION_SEMANTICS_CLASSIFICATION_INVALID = (
        "EXECUTION_SEMANTICS_CLASSIFICATION_INVALID"
    )
    TRACE_FINALIZATION_INVALID = "TRACE_FINALIZATION_INVALID"
    MISSING_ARTIFACT = "MISSING_ARTIFACT"
    MANIFEST_COMPLETENESS_INVALID = "MANIFEST_COMPLETENESS_INVALID"
    MANIFEST_MUTATION_FORBIDDEN = "MANIFEST_MUTATION_FORBIDDEN"
    AMBIGUOUS_PREFIX = "AMBIGUOUS_PREFIX"
    RECOVERY_RUN_BINDING_MISMATCH = "RECOVERY_RUN_BINDING_MISMATCH"
    RECOVERY_AUTHORIZATION_MISMATCH = "RECOVERY_AUTHORIZATION_MISMATCH"
    RECOVERY_EXECUTION_FORBIDDEN = "RECOVERY_EXECUTION_FORBIDDEN"
    ALREADY_EXISTS_DIFFERENT = "ALREADY_EXISTS_DIFFERENT"
    WRITE_ONCE_STORE_INVALID = "WRITE_ONCE_STORE_INVALID"
    PUBLICATION_AUTHORIZATION_MISMATCH = (
        "PUBLICATION_AUTHORIZATION_MISMATCH"
    )
    PUBLICATION_RECORD_INVALID = "PUBLICATION_RECORD_INVALID"
    CORRECTION_AUTHORIZATION_MISMATCH = (
        "CORRECTION_AUTHORIZATION_MISMATCH"
    )
    CORRECTION_AS_OVERWRITE_FORBIDDEN = (
        "CORRECTION_AS_OVERWRITE_FORBIDDEN"
    )
    CORRECTION_RECORD_INVALID = "CORRECTION_RECORD_INVALID"
    REAL_FINALIZATION_AUTHORITY_UNAVAILABLE = (
        "REAL_FINALIZATION_AUTHORITY_UNAVAILABLE"
    )
    REAL_RECOVERY_BACKEND_UNAVAILABLE = (
        "REAL_RECOVERY_BACKEND_UNAVAILABLE"
    )
    REAL_PUBLICATION_BACKEND_UNAVAILABLE = (
        "REAL_PUBLICATION_BACKEND_UNAVAILABLE"
    )
    REAL_CORRECTION_AUTHORITY_UNAVAILABLE = (
        "REAL_CORRECTION_AUTHORITY_UNAVAILABLE"
    )
    I8_HASH_COLLISION = "I8_HASH_COLLISION"


class Applicability(StrEnum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FailureStage(StrEnum):
    I1 = "I-1"
    I2 = "I-2"
    I3 = "I-3"
    I4 = "I-4"
    I5 = "I-5"
    I6 = "I-6"
    I7 = "I-7"
    I8 = "I-8"
    I9 = "I-9"
    ANALYTICAL_DESIGN = "ANALYTICAL_DESIGN"
    PREREGISTRATION = "PREREGISTRATION"
    IMPLEMENTATION = "IMPLEMENTATION"
    STATIC_AND_SYNTHETIC_VALIDATION = "STATIC_AND_SYNTHETIC_VALIDATION"
    PRE_EXECUTION_AUDIT = "PRE_EXECUTION_AUDIT"
    AUTHORIZED_SCIENTIFIC_EXECUTION = "AUTHORIZED_SCIENTIFIC_EXECUTION"
    INTERPRETATION = "INTERPRETATION"
    PUBLICATION = "PUBLICATION"
    RECOVERY = "RECOVERY"
    CORRECTION = "CORRECTION"


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


class ScientificStatusEffect(StrEnum):
    NONE = "NONE"
    UNSTARTED_PRESERVED = "UNSTARTED_PRESERVED"
    SCIENTIFIC_STATE_UNCHANGED = "SCIENTIFIC_STATE_UNCHANGED"
    SCIENTIFIC_STATE_ADVANCED = "SCIENTIFIC_STATE_ADVANCED"
    SCIENTIFIC_STATUS_FAILED = "SCIENTIFIC_STATUS_FAILED"
    SCIENTIFIC_STATUS_PARTIAL = "SCIENTIFIC_STATUS_PARTIAL"
    SCIENTIFIC_STATUS_UNRESOLVED = "SCIENTIFIC_STATUS_UNRESOLVED"


def _support_interface(name: str) -> "FailureInterfaceRef":
    return FailureInterfaceRef._trusted("ebu_framework.errors", name, "1.0.0")


def _support_failure(code: FailureCode, name: str, summary: str) -> NoReturn:
    _fail(
        code,
        summary,
        stage=FailureStage.I2,
        interface_ref=_support_interface(name),
    )


@dataclass(frozen=True, slots=True, order=True)
class FailureId:
    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str or _FAILURE_ID_RE.fullmatch(self.value) is None:
            _support_failure(
                FailureCode.DIGEST_INVALID,
                "FailureId",
                "failure ID must use the full lowercase failure digest grammar",
            )

    def __str__(self) -> str:
        return self.value

    def to_ecj1(self) -> dict[str, str]:
        return {"value": self.value}


@dataclass(frozen=True, slots=True, order=True)
class FailureInterfaceRef:
    module: str
    qualname: str
    interface_version: str

    @classmethod
    def _trusted(cls, module: str, qualname: str, version: str) -> "FailureInterfaceRef":
        instance = object.__new__(cls)
        object.__setattr__(instance, "module", module)
        object.__setattr__(instance, "qualname", qualname)
        object.__setattr__(instance, "interface_version", version)
        return instance

    def __post_init__(self) -> None:
        for field_name, value in (
            ("module", self.module),
            ("qualname", self.qualname),
            ("interface_version", self.interface_version),
        ):
            if (
                type(value) is not str
                or not value
                or not value.isascii()
                or any(character.isspace() or ord(character) < 0x20 for character in value)
            ):
                _support_failure(
                    FailureCode.STABLE_KEY_INVALID,
                    "FailureInterfaceRef",
                    f"{field_name} must be nonempty visible ASCII",
                )
        if _SEMANTIC_VERSION_RE.fullmatch(self.interface_version) is None:
            _support_failure(
                FailureCode.SEMANTIC_VERSION_INVALID,
                "FailureInterfaceRef",
                "interface_version must be MAJOR.MINOR.PATCH",
            )

    def to_ecj1(self) -> dict[str, str]:
        return {
            "interface_version": self.interface_version,
            "module": self.module,
            "qualname": self.qualname,
        }


@dataclass(frozen=True, slots=True, order=True)
class FailureObjectRef:
    object_id: str
    object_version: str
    object_content_hash: str

    def __post_init__(self) -> None:
        if type(self.object_id) is not str or _SCIENTIFIC_ID_RE.fullmatch(self.object_id) is None:
            _support_failure(
                FailureCode.SCIENTIFIC_ID_INVALID,
                "FailureObjectRef",
                "object_id has invalid ScientificId syntax",
            )
        if type(self.object_version) is not str or _SEMANTIC_VERSION_RE.fullmatch(self.object_version) is None:
            _support_failure(
                FailureCode.SEMANTIC_VERSION_INVALID,
                "FailureObjectRef",
                "object_version has invalid semantic-version syntax",
            )
        if type(self.object_content_hash) is not str or _DIGEST_RE.fullmatch(self.object_content_hash) is None:
            _support_failure(
                FailureCode.DIGEST_INVALID,
                "FailureObjectRef",
                "object_content_hash has invalid digest syntax",
            )

    def to_ecj1(self) -> dict[str, str]:
        return {
            "object_content_hash": self.object_content_hash,
            "object_id": self.object_id,
            "object_version": self.object_version,
        }


@dataclass(frozen=True, slots=True, order=True)
class FailureEventKey:
    epoch: int
    phase_ordinal: int
    declared_priority: int
    group_or_scope_id: str
    event_kind: str
    primary_object_id: str
    local_sequence: int

    def __post_init__(self) -> None:
        for field_name, value in (
            ("epoch", self.epoch),
            ("declared_priority", self.declared_priority),
            ("local_sequence", self.local_sequence),
        ):
            if type(value) is not int or value < 0:
                _support_failure(
                    FailureCode.CORE_NUMBER_INVALID,
                    "FailureEventKey",
                    f"{field_name} must be a nonnegative exact integer",
                )
        if type(self.phase_ordinal) is not int or not 1 <= self.phase_ordinal <= 10:
            _support_failure(
                FailureCode.CORE_NUMBER_INVALID,
                "FailureEventKey",
                "phase_ordinal must be an exact integer from 1 through 10",
            )
        if type(self.group_or_scope_id) is not str or _SCIENTIFIC_ID_RE.fullmatch(self.group_or_scope_id) is None:
            _support_failure(
                FailureCode.SCIENTIFIC_ID_INVALID,
                "FailureEventKey",
                "group_or_scope_id has invalid ScientificId syntax",
            )
        if type(self.event_kind) is not str or _SEGMENT_RE.fullmatch(self.event_kind) is None:
            _support_failure(
                FailureCode.STABLE_KEY_INVALID,
                "FailureEventKey",
                "event_kind has invalid segment syntax",
            )
        if type(self.primary_object_id) is not str or _SCIENTIFIC_ID_RE.fullmatch(self.primary_object_id) is None:
            _support_failure(
                FailureCode.SCIENTIFIC_ID_INVALID,
                "FailureEventKey",
                "primary_object_id has invalid ScientificId syntax",
            )

    def to_ecj1(self) -> dict[str, int | str]:
        return {
            "declared_priority": self.declared_priority,
            "epoch": self.epoch,
            "event_kind": self.event_kind,
            "group_or_scope_id": self.group_or_scope_id,
            "local_sequence": self.local_sequence,
            "phase_ordinal": self.phase_ordinal,
            "primary_object_id": self.primary_object_id,
        }


@dataclass(frozen=True, slots=True, order=True)
class FailureEvidenceRef:
    evidence_kind: str
    digest: str
    locator: str | Applicability

    def __post_init__(self) -> None:
        kinds = {
            "OBJECT",
            "ARTIFACT",
            "RAW_SOURCE",
            "TRACE_PREFIX",
            "AUTHORIZATION",
            "OPERATIONAL_LOG",
        }
        if type(self.evidence_kind) is not str or self.evidence_kind not in kinds:
            _support_failure(
                FailureCode.STABLE_KEY_INVALID,
                "FailureEvidenceRef",
                "evidence_kind is outside the closed domain",
            )
        digest_pattern = _RAW_DIGEST_RE if self.evidence_kind == "RAW_SOURCE" else _DIGEST_RE
        if type(self.digest) is not str or digest_pattern.fullmatch(self.digest) is None:
            _support_failure(
                FailureCode.DIGEST_INVALID,
                "FailureEvidenceRef",
                "evidence digest has the wrong domain or lexical form",
            )
        if type(self.locator) is str:
            if not self.locator or any(ord(character) < 0x20 for character in self.locator):
                _support_failure(
                    FailureCode.STABLE_KEY_INVALID,
                    "FailureEvidenceRef",
                    "locator text must be nonempty and contain no controls",
                )
            try:
                self.locator.encode("utf-8", "strict")
            except UnicodeError:
                _support_failure(
                    FailureCode.INVALID_UNICODE_SCALAR,
                    "FailureEvidenceRef",
                    "locator must be canonical UTF-8 text",
                )
        elif self.locator is not Applicability.NOT_APPLICABLE:
            _support_failure(
                FailureCode.IMPLICIT_ABSENCE_FORBIDDEN,
                "FailureEvidenceRef",
                "locator must be text or typed NOT_APPLICABLE",
            )

    def to_ecj1(self) -> dict[str, str]:
        return {
            "digest": self.digest,
            "evidence_kind": self.evidence_kind,
            "locator": (
                self.locator if type(self.locator) is str else self.locator.value
            ),
        }


@dataclass(frozen=True, slots=True)
class CanonicalTraceState:
    applicability: Applicability
    completeness: str | Applicability
    confirmed_row_count: int | Applicability
    durable_prefix_ref: FailureEvidenceRef | Applicability

    def __post_init__(self) -> None:
        if type(self.applicability) is not Applicability:
            _support_failure(
                FailureCode.RESOLUTION_STATE_INVALID,
                "CanonicalTraceState",
                "trace applicability must be typed",
            )
        if self.applicability is Applicability.NOT_APPLICABLE:
            if not (
                self.completeness is Applicability.NOT_APPLICABLE
                and self.confirmed_row_count is Applicability.NOT_APPLICABLE
                and self.durable_prefix_ref is Applicability.NOT_APPLICABLE
            ):
                _support_failure(
                    FailureCode.RESOLUTION_STATE_INVALID,
                    "CanonicalTraceState",
                    "not-applicable trace state must use the exact pre-trace form",
                )
            return
        completeness_domain = {
            "COMPLETE",
            "DECLARED_FAULT_TERMINAL",
            "PARTIAL_DURABLE_PREFIX",
            "NO_DURABLE_TRACE",
            "UNRESOLVED_DURABILITY",
        }
        if type(self.completeness) is not str or self.completeness not in completeness_domain:
            _support_failure(
                FailureCode.RESOLUTION_STATE_INVALID,
                "CanonicalTraceState",
                "applicable trace completeness is invalid",
            )
        if type(self.confirmed_row_count) is not int or self.confirmed_row_count < 0:
            _support_failure(
                FailureCode.CORE_NUMBER_INVALID,
                "CanonicalTraceState",
                "confirmed_row_count must be a nonnegative exact integer",
            )
        if self.completeness == "PARTIAL_DURABLE_PREFIX":
            if type(self.durable_prefix_ref) is not FailureEvidenceRef or self.durable_prefix_ref.evidence_kind != "TRACE_PREFIX":
                _support_failure(
                    FailureCode.RESOLUTION_STATE_INVALID,
                    "CanonicalTraceState",
                    "a partial durable prefix requires a TRACE_PREFIX reference",
                )
        elif self.durable_prefix_ref is not Applicability.NOT_APPLICABLE:
            _support_failure(
                FailureCode.RESOLUTION_STATE_INVALID,
                "CanonicalTraceState",
                "this trace completeness requires typed NOT_APPLICABLE prefix",
            )

    def to_ecj1(self) -> dict[str, object]:
        def project(value: object) -> object:
            if isinstance(value, StrEnum):
                return value.value
            if type(value) is FailureEvidenceRef:
                return value.to_ecj1()
            return value

        return {
            "applicability": self.applicability.value,
            "completeness": project(self.completeness),
            "confirmed_row_count": project(self.confirmed_row_count),
            "durable_prefix_ref": project(self.durable_prefix_ref),
        }


_PRE_TRACE_NOT_APPLICABLE = CanonicalTraceState(
    applicability=Applicability.NOT_APPLICABLE,
    completeness=Applicability.NOT_APPLICABLE,
    confirmed_row_count=Applicability.NOT_APPLICABLE,
    durable_prefix_ref=Applicability.NOT_APPLICABLE,
)


def _frame(value: str) -> bytes:
    encoded = value.encode("utf-8", "strict")
    return len(encoded).to_bytes(8, "big") + encoded


def _derive_failure_id(
    failure_code: FailureCode,
    stage: FailureStage,
    interface_ref: FailureInterfaceRef | Applicability,
    object_refs: tuple[FailureObjectRef, ...],
    event_key: FailureEventKey | Applicability,
    failure_ordinal: int,
) -> FailureId:
    parts = [_frame("ebu.failure-id.v1"), _frame(failure_code.value), _frame(stage.value)]
    if type(interface_ref) is FailureInterfaceRef:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(interface_ref.module),
                _frame(interface_ref.qualname),
                _frame(interface_ref.interface_version),
            )
        )
    else:
        parts.append(_frame("NOT_APPLICABLE"))
    parts.append(len(object_refs).to_bytes(8, "big"))
    for reference in object_refs:
        parts.extend(
            (
                _frame(reference.object_id),
                _frame(reference.object_version),
                _frame(reference.object_content_hash),
            )
        )
    if type(event_key) is FailureEventKey:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(str(event_key.epoch)),
                _frame(str(event_key.phase_ordinal)),
                _frame(str(event_key.declared_priority)),
                _frame(event_key.group_or_scope_id),
                _frame(event_key.event_kind),
                _frame(event_key.primary_object_id),
                _frame(str(event_key.local_sequence)),
            )
        )
    else:
        parts.append(_frame("NOT_APPLICABLE"))
    parts.append(_frame(str(failure_ordinal)))
    digest = hashlib.sha256(b"".join(parts)).hexdigest()
    return FailureId(f"ebu:failure:core:sha256-{digest}")


@dataclass(frozen=True, slots=True)
class FailureEnvelope:
    failure_id: FailureId
    failure_ordinal: int
    failure_code: FailureCode
    stage: FailureStage
    interface_ref: FailureInterfaceRef | Applicability
    object_refs: tuple[FailureObjectRef, ...]
    event_key: FailureEventKey | Applicability
    state_advance: StateAdvance
    policy_memory_advance: PolicyMemoryAdvance
    durability_state: DurabilityState
    canonical_trace_state: CanonicalTraceState
    scientific_status_effect: ScientificStatusEffect
    retry_class: RetryClass
    evidence_refs: tuple[FailureEvidenceRef, ...]
    human_summary: str

    def __post_init__(self) -> None:
        if type(self.failure_code) is not FailureCode or type(self.stage) is not FailureStage:
            raise TypeError("failure code and stage must use their exact enums")
        if type(self.failure_ordinal) is not int or self.failure_ordinal < 0:
            raise TypeError("failure_ordinal must be a nonnegative exact integer")
        if not (
            type(self.interface_ref) is FailureInterfaceRef
            or self.interface_ref is Applicability.NOT_APPLICABLE
        ):
            raise TypeError("invalid failure interface coordinate")
        if type(self.object_refs) is not tuple or not all(
            type(reference) is FailureObjectRef for reference in self.object_refs
        ):
            raise TypeError("object_refs must be an exact FailureObjectRef tuple")
        object_keys = tuple(
            (item.object_id, item.object_version, item.object_content_hash)
            for item in self.object_refs
        )
        if object_keys != tuple(sorted(object_keys)) or len(object_keys) != len(set(object_keys)):
            raise TypeError("object_refs must be ordered and duplicate-free")
        if not (
            type(self.event_key) is FailureEventKey
            or self.event_key is Applicability.NOT_APPLICABLE
        ):
            raise TypeError("invalid failure event coordinate")
        for value, expected in (
            (self.state_advance, StateAdvance),
            (self.policy_memory_advance, PolicyMemoryAdvance),
            (self.durability_state, DurabilityState),
            (self.canonical_trace_state, CanonicalTraceState),
            (self.scientific_status_effect, ScientificStatusEffect),
            (self.retry_class, RetryClass),
        ):
            if type(value) is not expected:
                raise TypeError(f"failure field must be exact {expected.__name__}")
        if type(self.evidence_refs) is not tuple or not all(
            type(reference) is FailureEvidenceRef for reference in self.evidence_refs
        ):
            raise TypeError("evidence_refs must be an exact FailureEvidenceRef tuple")
        evidence_keys = tuple(
            (
                item.evidence_kind,
                item.digest,
                item.locator.value if type(item.locator) is Applicability else item.locator,
            )
            for item in self.evidence_refs
        )
        if evidence_keys != tuple(sorted(evidence_keys)) or len(evidence_keys) != len(set(evidence_keys)):
            raise TypeError("evidence_refs must be ordered and duplicate-free")
        if (
            type(self.human_summary) is not str
            or not self.human_summary
            or unicodedata.normalize("NFC", self.human_summary) != self.human_summary
            or any(ord(character) < 0x20 and character != "\n" for character in self.human_summary)
        ):
            raise TypeError("human_summary must be nonempty NFC text without controls")
        expected_id = _derive_failure_id(
            self.failure_code,
            self.stage,
            self.interface_ref,
            self.object_refs,
            self.event_key,
            self.failure_ordinal,
        )
        if self.failure_id != expected_id:
            raise TypeError("failure_id does not match the failure occurrence coordinate")

    def to_ecj1(self) -> dict[str, object]:
        def project(value: object) -> object:
            if isinstance(value, StrEnum):
                return value.value
            if type(value) in {FailureId, FailureInterfaceRef, FailureObjectRef, FailureEventKey, FailureEvidenceRef, CanonicalTraceState}:
                return value.to_ecj1()  # type: ignore[union-attr]
            return value

        return {
            "canonical_trace_state": self.canonical_trace_state.to_ecj1(),
            "durability_state": self.durability_state.value,
            "event_key": project(self.event_key),
            "evidence_refs": [item.to_ecj1() for item in self.evidence_refs],
            "failure_code": self.failure_code.value,
            "failure_id": self.failure_id.to_ecj1(),
            "failure_ordinal": self.failure_ordinal,
            "human_summary": self.human_summary,
            "interface_ref": project(self.interface_ref),
            "object_refs": [item.to_ecj1() for item in self.object_refs],
            "policy_memory_advance": self.policy_memory_advance.value,
            "retry_class": self.retry_class.value,
            "schema_id": "ebu.failure-envelope/1",
            "scientific_status_effect": self.scientific_status_effect.value,
            "stage": self.stage.value,
            "state_advance": self.state_advance.value,
        }


class FrameworkError(ValueError):
    """Internal exception carrying one typed immutable failure envelope."""

    def __init__(
        self,
        code: FailureCode,
        summary: str,
        *,
        stage: FailureStage,
        interface_ref: FailureInterfaceRef | Applicability = Applicability.NOT_APPLICABLE,
        object_refs: tuple[FailureObjectRef, ...] = (),
        event_key: FailureEventKey | Applicability = Applicability.NOT_APPLICABLE,
        failure_ordinal: int = 0,
        state_advance: StateAdvance = StateAdvance.NONE,
        policy_memory_advance: PolicyMemoryAdvance = PolicyMemoryAdvance.NONE,
        durability_state: DurabilityState = DurabilityState.NOT_APPLICABLE,
        canonical_trace_state: CanonicalTraceState = _PRE_TRACE_NOT_APPLICABLE,
        scientific_status_effect: ScientificStatusEffect = ScientificStatusEffect.NONE,
        retry_class: RetryClass = RetryClass.NOT_APPLICABLE,
        evidence_refs: tuple[FailureEvidenceRef, ...] = (),
    ) -> None:
        failure_id = _derive_failure_id(
            code, stage, interface_ref, object_refs, event_key, failure_ordinal
        )
        self.envelope = FailureEnvelope(
            failure_id=failure_id,
            failure_ordinal=failure_ordinal,
            failure_code=code,
            stage=stage,
            interface_ref=interface_ref,
            object_refs=object_refs,
            event_key=event_key,
            state_advance=state_advance,
            policy_memory_advance=policy_memory_advance,
            durability_state=durability_state,
            canonical_trace_state=canonical_trace_state,
            scientific_status_effect=scientific_status_effect,
            retry_class=retry_class,
            evidence_refs=evidence_refs,
            human_summary=summary,
        )
        super().__init__(f"{code.value}: {summary}")


def _fail(
    code: FailureCode,
    summary: str,
    *,
    stage: FailureStage | Applicability = Applicability.NOT_APPLICABLE,
    interface_ref: FailureInterfaceRef | Applicability = Applicability.NOT_APPLICABLE,
    object_refs: tuple[FailureObjectRef, ...] = (),
    event_key: FailureEventKey | Applicability = Applicability.NOT_APPLICABLE,
    failure_ordinal: int = 0,
    state_advance: StateAdvance = StateAdvance.NONE,
    policy_memory_advance: PolicyMemoryAdvance = PolicyMemoryAdvance.NONE,
    durability_state: DurabilityState = DurabilityState.NOT_APPLICABLE,
    canonical_trace_state: CanonicalTraceState = _PRE_TRACE_NOT_APPLICABLE,
    scientific_status_effect: ScientificStatusEffect = ScientificStatusEffect.NONE,
    retry_class: RetryClass = RetryClass.NOT_APPLICABLE,
    evidence_refs: tuple[FailureEvidenceRef, ...] = (),
) -> NoReturn:
    if stage is Applicability.NOT_APPLICABLE:
        frame = inspect.currentframe()
        caller = None if frame is None or frame.f_back is None else frame.f_back.f_globals.get("__name__")
        del frame
        if caller not in _LEGACY_I1_MODULES:
            raise RuntimeError("I-2 and later failures must declare stage and interface")
        resolved_stage = FailureStage.I1
    elif type(stage) is FailureStage:
        resolved_stage = stage
    else:
        raise RuntimeError("failure stage must be explicit or use the closed I-1 sentinel")
    raise FrameworkError(
        code,
        summary,
        stage=resolved_stage,
        interface_ref=interface_ref,
        object_refs=object_refs,
        event_key=event_key,
        failure_ordinal=failure_ordinal,
        state_advance=state_advance,
        policy_memory_advance=policy_memory_advance,
        durability_state=durability_state,
        canonical_trace_state=canonical_trace_state,
        scientific_status_effect=scientific_status_effect,
        retry_class=retry_class,
        evidence_refs=evidence_refs,
    )


@contextmanager
def _i4_validation_context(failure_ordinal: int, ordered_check_name: str):
    """Bind the event-local coordinates used by one authorized synthetic vector."""

    if type(failure_ordinal) is not int or failure_ordinal < 0:
        raise TypeError("I-4 validation failure ordinal must be nonnegative")
    if type(ordered_check_name) is not str or not ordered_check_name:
        raise TypeError("I-4 validation check name must be nonempty text")
    ordinal_token = _I4_FAILURE_ORDINAL.set(failure_ordinal)
    check_token = _I4_ORDERED_CHECK_NAME.set(ordered_check_name)
    try:
        yield
    finally:
        _I4_ORDERED_CHECK_NAME.reset(check_token)
        _I4_FAILURE_ORDINAL.reset(ordinal_token)


_I4_REQUIRES_AUTHORITY = frozenset({FailureCode.PRODUCTION_BOOTSTRAP_MISSING})
_I4_NOT_APPLICABLE_RETRY = frozenset(
    {
        FailureCode.TRUSTED_TIME_UNAVAILABLE,
        FailureCode.TRUSTED_TIME_CHALLENGE_MISMATCH,
        FailureCode.TRUSTED_TIME_STALE,
        FailureCode.TRUSTED_TIME_SEQUENCE_INVALID,
        FailureCode.REVOCATION_UNAVAILABLE,
        FailureCode.REVOCATION_SNAPSHOT_EXPIRED,
        FailureCode.AUTHORIZATION_USE_UNRESOLVED,
        FailureCode.AUTHORIZATION_USE_STORE_UNSUPPORTED,
        FailureCode.AUTHORIZATION_USE_LEDGER_FAILURE,
    }
)
_I4_UNRESOLVED_DURABILITY = frozenset(
    {
        FailureCode.TRUSTED_TIME_SEQUENCE_INVALID,
        FailureCode.REVOCATION_ROLLBACK,
        FailureCode.REVOCATION_GAP,
        FailureCode.REVOCATION_EQUIVOCATION,
        FailureCode.AUTHORIZATION_USE_UNRESOLVED,
        FailureCode.AUTHORIZATION_USE_LEDGER_FAILURE,
    }
)


def _i4_fail(
    code: FailureCode,
    module: str,
    interface: str,
    ordered_check_name: str,
    *,
    object_refs: tuple[FailureObjectRef, ...] = (),
    evidence_refs: tuple[FailureEvidenceRef, ...] = (),
) -> NoReturn:
    """Raise one normalized fail-closed I-4 failure envelope."""

    check_name = _I4_ORDERED_CHECK_NAME.get() or ordered_check_name
    summary = (
        f"{interface} rejected {code.value}"
        if code is FailureCode.I4_RECORD_FORMATION_INVALID
        else f"{interface} rejected {code.value} at {check_name}"
    )
    retry = (
        RetryClass.REQUIRES_AUTHORITY
        if code in _I4_REQUIRES_AUTHORITY
        else RetryClass.NOT_APPLICABLE
        if code in _I4_NOT_APPLICABLE_RETRY
        else RetryClass.FORBIDDEN
    )
    durability = (
        DurabilityState.UNRESOLVED
        if code in _I4_UNRESOLVED_DURABILITY
        else DurabilityState.NONE_DURABLE
        if code is FailureCode.AUTHORIZATION_USE_ALREADY_CONSUMED
        else DurabilityState.NOT_APPLICABLE
    )
    _fail(
        code,
        summary,
        stage=FailureStage.I4,
        interface_ref=FailureInterfaceRef(module, interface, "1.0.0"),
        object_refs=object_refs,
        failure_ordinal=_I4_FAILURE_ORDINAL.get(),
        durability_state=durability,
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=retry,
        evidence_refs=evidence_refs,
    )


__all__ = (
    "Applicability",
    "CanonicalTraceState",
    "DurabilityState",
    "FailureCode",
    "FailureEnvelope",
    "FailureEventKey",
    "FailureEvidenceRef",
    "FailureId",
    "FailureInterfaceRef",
    "FailureObjectRef",
    "FailureStage",
    "PolicyMemoryAdvance",
    "RetryClass",
    "ScientificStatusEffect",
    "StateAdvance",
)
