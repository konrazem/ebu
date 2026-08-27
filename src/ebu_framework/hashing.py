"""Exact named I-0 hash projections constructible at I-1."""

from __future__ import annotations

import hashlib
from typing import Any, TypeVar

from .canonical import ECJ1Value, encode_ecj1
from .errors import Applicability, FailureCode, _fail
from .identity import (
    ArtifactByteHash,
    AugmentedClosedLoopReplayStateHash,
    AuthorizationUseKey,
    CanonicalScientificTracePayloadHash,
    CanonicalTracePrefixHash,
    CanonicalTraceRowHash,
    ExecutionSemanticsHash,
    InformationViewHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ProposalSetHash,
    RepresentedStateProjectionHash,
    ScientificId,
    SemanticVersion,
    SourceFileRawSha256,
    StatePayloadHash,
    _Digest,
)


_DigestT = TypeVar("_DigestT", bound=_Digest)


def _as_ecj1(value: Any) -> ECJ1Value:
    if isinstance(value, ObjectRef):
        return value.to_ecj1()
    if isinstance(value, (ScientificId, SemanticVersion, _Digest)):
        return str(value)
    if type(value) is dict:
        return {key: _as_ecj1(item) for key, item in value.items()}
    if type(value) is list:
        return [_as_ecj1(item) for item in value]
    if value is None or type(value) in (str, int, bool, float):
        return value
    return value


def _ordered(values: tuple[Any, ...] | list[Any], field: str) -> list[ECJ1Value]:
    if type(values) not in (tuple, list):
        _fail(
            FailureCode.CANONICALIZATION_FAILURE,
            f"{field} must be an explicitly ordered tuple or list",
        )
    return [_as_ecj1(value) for value in values]


def _exact(value: Any, expected: type[Any], field: str) -> Any:
    if type(value) is not expected:
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            f"{field} requires exact {expected.__name__}",
        )
    return value


def _hash_preimage(
    preimage: dict[str, ECJ1Value], digest_type: type[_DigestT]
) -> _DigestT:
    canonical = bytes(encode_ecj1(preimage))
    return digest_type.from_hex(hashlib.sha256(canonical).hexdigest())


def compute_object_content_hash(
    *,
    object_id: ScientificId,
    object_kind: str,
    schema_id: ScientificId,
    schema_version: SemanticVersion,
    object_version: SemanticVersion,
    authority_refs: tuple[ObjectRef, ...] | list[ObjectRef],
    supersedes_ref: ObjectRef | None,
    object_content_payload: ECJ1Value,
) -> ObjectContentHash:
    _exact(object_id, ScientificId, "object_id")
    _exact(schema_id, ScientificId, "schema_id")
    _exact(schema_version, SemanticVersion, "schema_version")
    _exact(object_version, SemanticVersion, "object_version")
    if type(object_kind) is not str or not object_kind:
        _fail(FailureCode.CANONICALIZATION_FAILURE, "object_kind must be text")
    refs = _ordered(authority_refs, "authority_refs")
    if not all(type(ref) is ObjectRef for ref in authority_refs):
        _fail(FailureCode.DIGEST_TYPE_MISMATCH, "authority_refs require ObjectRef")
    if supersedes_ref is not None and type(supersedes_ref) is not ObjectRef:
        _fail(FailureCode.DIGEST_TYPE_MISMATCH, "supersedes_ref requires ObjectRef")
    return _hash_preimage(
        {
            "authority_refs": refs,
            "hash_domain": "ebu.object-content.v1",
            "object_content_payload": _as_ecj1(object_content_payload),
            "object_id": str(object_id),
            "object_kind": object_kind,
            "object_version": str(object_version),
            "schema_id": str(schema_id),
            "schema_version": str(schema_version),
            "supersedes_ref": (
                None if supersedes_ref is None else supersedes_ref.to_ecj1()
            ),
        },
        ObjectContentHash,
    )


def compute_authorization_use_key(
    *,
    stage_authorization_ref: ObjectRef,
    requested_operation: str,
    target_object_refs: tuple[ObjectRef, ...],
    accepted_configuration_ref_or_not_applicable: ObjectRef | Applicability,
    accepted_execution_binding_ref_or_not_applicable: ObjectRef | Applicability,
    execution_identity_or_not_applicable: ExecutionIdentity | Applicability,
) -> AuthorizationUseKey:
    """Hash one exact authorization request without run-local use metadata."""

    _exact(stage_authorization_ref, ObjectRef, "stage_authorization_ref")
    if type(requested_operation) is not str or not requested_operation:
        _fail(
            FailureCode.CANONICALIZATION_FAILURE,
            "requested_operation must be nonempty text",
        )
    if type(target_object_refs) is not tuple or not target_object_refs or not all(
        type(reference) is ObjectRef for reference in target_object_refs
    ):
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "target_object_refs require a nonempty exact ObjectRef tuple",
        )
    ref_keys = tuple(bytes(encode_ecj1(reference.to_ecj1())) for reference in target_object_refs)
    if ref_keys != tuple(sorted(ref_keys)) or len(ref_keys) != len(set(ref_keys)):
        _fail(
            FailureCode.CANONICALIZATION_FAILURE,
            "target_object_refs must be ECJ-1 ordered and duplicate-free",
        )

    def optional_ref(value: object, field: str) -> ECJ1Value:
        if type(value) is ObjectRef:
            return value.to_ecj1()
        if value is Applicability.NOT_APPLICABLE:
            return Applicability.NOT_APPLICABLE.value
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            f"{field} requires ObjectRef or NOT_APPLICABLE",
        )

    execution: ECJ1Value
    if execution_identity_or_not_applicable is Applicability.NOT_APPLICABLE:
        execution = Applicability.NOT_APPLICABLE.value
    elif (
        type(execution_identity_or_not_applicable).__name__ == "ExecutionIdentity"
        and hasattr(execution_identity_or_not_applicable, "to_ecj1")
    ):
        execution = execution_identity_or_not_applicable.to_ecj1()
    else:
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "execution_identity_or_not_applicable requires ExecutionIdentity or NOT_APPLICABLE",
        )
    return _hash_preimage(
        {
            "hash_domain": "ebu.authorization-use-key.v1",
            "stage_authorization_ref": stage_authorization_ref.to_ecj1(),
            "requested_operation": requested_operation,
            "target_object_refs": [reference.to_ecj1() for reference in target_object_refs],
            "accepted_configuration_ref_or_not_applicable": optional_ref(
                accepted_configuration_ref_or_not_applicable,
                "accepted_configuration_ref_or_not_applicable",
            ),
            "accepted_execution_binding_ref_or_not_applicable": optional_ref(
                accepted_execution_binding_ref_or_not_applicable,
                "accepted_execution_binding_ref_or_not_applicable",
            ),
            "execution_identity_or_not_applicable": execution,
        },
        AuthorizationUseKey,
    )


def compute_state_payload_hash(
    *,
    state_schema_ref: ObjectRef,
    epoch: ECJ1Value,
    physical_state_x: ECJ1Value,
    topology_state_g: ECJ1Value,
    queue_and_transit_state_q: ECJ1Value,
    commitment_state_c: ECJ1Value,
    delayed_effect_state_ell: ECJ1Value,
    declared_external_inputs_applied: tuple[Any, ...] | list[Any],
) -> StatePayloadHash:
    _exact(state_schema_ref, ObjectRef, "state_schema_ref")
    return _hash_preimage(
        {
            "commitment_state_c": _as_ecj1(commitment_state_c),
            "declared_external_inputs_applied": _ordered(
                declared_external_inputs_applied,
                "declared_external_inputs_applied",
            ),
            "delayed_effect_state_ell": _as_ecj1(delayed_effect_state_ell),
            "epoch": _as_ecj1(epoch),
            "hash_domain": "ebu.state-payload.v1",
            "physical_state_x": _as_ecj1(physical_state_x),
            "queue_and_transit_state_q": _as_ecj1(queue_and_transit_state_q),
            "state_schema_ref": state_schema_ref.to_ecj1(),
            "topology_state_g": _as_ecj1(topology_state_g),
        },
        StatePayloadHash,
    )


def compute_policy_memory_payload_hash(
    *,
    policy_ref: ObjectRef,
    memory_schema_ref: ObjectRef,
    available_for_decision_epoch: ECJ1Value,
    resolution_state: str,
    memory_payload: ECJ1Value,
) -> PolicyMemoryPayloadHash:
    _exact(policy_ref, ObjectRef, "policy_ref")
    _exact(memory_schema_ref, ObjectRef, "memory_schema_ref")
    return _hash_preimage(
        {
            "available_for_decision_epoch": _as_ecj1(
                available_for_decision_epoch
            ),
            "hash_domain": "ebu.policy-memory-payload.v1",
            "memory_payload": _as_ecj1(memory_payload),
            "memory_schema_ref": memory_schema_ref.to_ecj1(),
            "policy_ref": policy_ref.to_ecj1(),
            "resolution_state": resolution_state,
        },
        PolicyMemoryPayloadHash,
    )


def compute_augmented_replay_state_hash(
    physical_state_payload_hash: StatePayloadHash,
    policy_memory_payload_hash: PolicyMemoryPayloadHash,
) -> AugmentedClosedLoopReplayStateHash:
    _exact(
        physical_state_payload_hash,
        StatePayloadHash,
        "physical_state_payload_hash",
    )
    _exact(
        policy_memory_payload_hash,
        PolicyMemoryPayloadHash,
        "policy_memory_payload_hash",
    )
    return _hash_preimage(
        {
            "hash_domain": "ebu.augmented-closed-loop-replay-state.v1",
            "physical_state_payload_hash": str(physical_state_payload_hash),
            "policy_memory_payload_hash": str(policy_memory_payload_hash),
        },
        AugmentedClosedLoopReplayStateHash,
    )


def compute_represented_state_projection_hash(
    *,
    source_state_payload_hash: StatePayloadHash,
    boundary_ref: ObjectRef,
    projection_contract_ref: ObjectRef,
    included_coordinate_ids: tuple[Any, ...] | list[Any],
    excluded_coordinate_ids_and_resolution_states: tuple[Any, ...] | list[Any],
    represented_state_payload: ECJ1Value,
) -> RepresentedStateProjectionHash:
    _exact(source_state_payload_hash, StatePayloadHash, "source_state_payload_hash")
    _exact(boundary_ref, ObjectRef, "boundary_ref")
    _exact(projection_contract_ref, ObjectRef, "projection_contract_ref")
    return _hash_preimage(
        {
            "boundary_ref": boundary_ref.to_ecj1(),
            "excluded_coordinate_ids_and_resolution_states": _ordered(
                excluded_coordinate_ids_and_resolution_states,
                "excluded_coordinate_ids_and_resolution_states",
            ),
            "hash_domain": "ebu.represented-state-projection.v1",
            "included_coordinate_ids": _ordered(
                included_coordinate_ids, "included_coordinate_ids"
            ),
            "projection_contract_ref": projection_contract_ref.to_ecj1(),
            "represented_state_payload": _as_ecj1(represented_state_payload),
            "source_state_payload_hash": str(source_state_payload_hash),
        },
        RepresentedStateProjectionHash,
    )


def compute_information_view_hash(
    *,
    policy_ref: ObjectRef,
    information_contract_ref: ObjectRef,
    decision_epoch: ECJ1Value,
    current_policy_memory_payload_hash_or_not_applicable: (
        PolicyMemoryPayloadHash | str
    ),
    ordered_visible_field_records: tuple[Any, ...] | list[Any],
    ordered_visible_object_refs: tuple[ObjectRef, ...] | list[ObjectRef],
) -> InformationViewHash:
    _exact(policy_ref, ObjectRef, "policy_ref")
    _exact(information_contract_ref, ObjectRef, "information_contract_ref")
    memory = current_policy_memory_payload_hash_or_not_applicable
    if type(memory) is PolicyMemoryPayloadHash:
        memory_value = str(memory)
    elif memory == "NOT_APPLICABLE":
        memory_value = "NOT_APPLICABLE"
    else:
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "current policy memory must be PolicyMemoryPayloadHash or NOT_APPLICABLE",
        )
    if not all(type(ref) is ObjectRef for ref in ordered_visible_object_refs):
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "ordered_visible_object_refs require ObjectRef",
        )
    return _hash_preimage(
        {
            "current_policy_memory_payload_hash_or_not_applicable": memory_value,
            "decision_epoch": _as_ecj1(decision_epoch),
            "hash_domain": "ebu.information-view.v1",
            "information_contract_ref": information_contract_ref.to_ecj1(),
            "ordered_visible_field_records": _ordered(
                ordered_visible_field_records, "ordered_visible_field_records"
            ),
            "ordered_visible_object_refs": _ordered(
                ordered_visible_object_refs, "ordered_visible_object_refs"
            ),
            "policy_ref": policy_ref.to_ecj1(),
        },
        InformationViewHash,
    )


def compute_proposal_set_hash(
    *,
    policy_ref_or_open_loop_schedule_ref: ObjectRef,
    decision_coordinate: ECJ1Value,
    information_view_hash_or_not_applicable: InformationViewHash | str,
    before_policy_memory_payload_hash_or_not_applicable: (
        PolicyMemoryPayloadHash | str
    ),
    after_policy_memory_payload_hash_or_not_applicable: (
        PolicyMemoryPayloadHash | str
    ),
    ordered_proposal_payloads: tuple[Any, ...] | list[Any],
) -> ProposalSetHash:
    _exact(
        policy_ref_or_open_loop_schedule_ref,
        ObjectRef,
        "policy_ref_or_open_loop_schedule_ref",
    )

    def optional_digest(value: Any, expected: type[_Digest], field: str) -> str:
        if type(value) is expected:
            return str(value)
        if value == "NOT_APPLICABLE":
            return "NOT_APPLICABLE"
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            f"{field} requires {expected.__name__} or NOT_APPLICABLE",
        )

    return _hash_preimage(
        {
            "after_policy_memory_payload_hash_or_not_applicable": optional_digest(
                after_policy_memory_payload_hash_or_not_applicable,
                PolicyMemoryPayloadHash,
                "after_policy_memory_payload_hash_or_not_applicable",
            ),
            "before_policy_memory_payload_hash_or_not_applicable": optional_digest(
                before_policy_memory_payload_hash_or_not_applicable,
                PolicyMemoryPayloadHash,
                "before_policy_memory_payload_hash_or_not_applicable",
            ),
            "decision_coordinate": _as_ecj1(decision_coordinate),
            "hash_domain": "ebu.proposal-set.v1",
            "information_view_hash_or_not_applicable": optional_digest(
                information_view_hash_or_not_applicable,
                InformationViewHash,
                "information_view_hash_or_not_applicable",
            ),
            "ordered_proposal_payloads": _ordered(
                ordered_proposal_payloads, "ordered_proposal_payloads"
            ),
            "policy_ref_or_open_loop_schedule_ref": (
                policy_ref_or_open_loop_schedule_ref.to_ecj1()
            ),
        },
        ProposalSetHash,
    )


def compute_execution_semantics_hash(
    *,
    accepted_configuration_ref: ObjectRef,
    implementation_refs: tuple[Any, ...] | list[Any],
    source_refs: tuple[Any, ...] | list[Any],
    implementation_entrypoint_semantics: ECJ1Value,
    science_affecting_runtime_constraints: ECJ1Value,
    science_affecting_operational_exclusions: ECJ1Value,
    policy_memory_transition_contracts_or_not_applicable: ECJ1Value,
    fault_injection_delivery_contracts_or_not_applicable: ECJ1Value,
    event_order_contract: ECJ1Value,
    arithmetic_and_numerical_policy_contracts: ECJ1Value,
    information_capability_contract: ECJ1Value,
    canonical_scientific_trace_schema_ref: ObjectRef,
    scientific_result_schema_ref: ObjectRef,
    stochastic_generator_and_stream_contract_or_not_applicable: ECJ1Value,
) -> ExecutionSemanticsHash:
    _exact(accepted_configuration_ref, ObjectRef, "accepted_configuration_ref")
    _exact(
        canonical_scientific_trace_schema_ref,
        ObjectRef,
        "canonical_scientific_trace_schema_ref",
    )
    _exact(scientific_result_schema_ref, ObjectRef, "scientific_result_schema_ref")
    return _hash_preimage(
        {
            "accepted_configuration_ref": accepted_configuration_ref.to_ecj1(),
            "arithmetic_and_numerical_policy_contracts": _as_ecj1(
                arithmetic_and_numerical_policy_contracts
            ),
            "canonical_scientific_trace_schema_ref": (
                canonical_scientific_trace_schema_ref.to_ecj1()
            ),
            "event_order_contract": _as_ecj1(event_order_contract),
            "fault_injection_delivery_contracts_or_not_applicable": _as_ecj1(
                fault_injection_delivery_contracts_or_not_applicable
            ),
            "hash_domain": "ebu.execution-semantics.v1",
            "implementation_entrypoint_semantics": _as_ecj1(
                implementation_entrypoint_semantics
            ),
            "implementation_refs": _ordered(
                implementation_refs, "implementation_refs"
            ),
            "information_capability_contract": _as_ecj1(
                information_capability_contract
            ),
            "policy_memory_transition_contracts_or_not_applicable": _as_ecj1(
                policy_memory_transition_contracts_or_not_applicable
            ),
            "science_affecting_operational_exclusions": _as_ecj1(
                science_affecting_operational_exclusions
            ),
            "science_affecting_runtime_constraints": _as_ecj1(
                science_affecting_runtime_constraints
            ),
            "scientific_result_schema_ref": scientific_result_schema_ref.to_ecj1(),
            "source_refs": _ordered(source_refs, "source_refs"),
            "stochastic_generator_and_stream_contract_or_not_applicable": _as_ecj1(
                stochastic_generator_and_stream_contract_or_not_applicable
            ),
        },
        ExecutionSemanticsHash,
    )


def compute_canonical_trace_row_hash(
    *,
    trace_schema_ref: ObjectRef,
    row_index: int,
    epoch: ECJ1Value,
    event_key: ECJ1Value,
    phase_ordinal: int,
    scientific_object_refs: tuple[Any, ...] | list[Any],
    predecessor_state_payload_hash: StatePayloadHash,
    successor_state_payload_hash: StatePayloadHash,
    information_view_hash_or_not_applicable: ECJ1Value,
    before_policy_memory_payload_hash_or_not_applicable: ECJ1Value,
    after_policy_memory_payload_hash_or_not_applicable: ECJ1Value,
    augmented_replay_state_hash_or_not_applicable: ECJ1Value,
    proposal_set_hash_or_not_applicable: ECJ1Value,
    admission_group_and_ownership_facts: ECJ1Value,
    typed_quantities: tuple[Any, ...] | list[Any],
    uncertainty_values: tuple[Any, ...] | list[Any],
    lifecycle_transitions: tuple[Any, ...] | list[Any],
    declared_scientific_or_model_faults: tuple[Any, ...] | list[Any],
    scientifically_relevant_failures: tuple[Any, ...] | list[Any],
    resolution_state: str,
    predecessor_trace_row_hash_or_genesis: CanonicalTraceRowHash | str,
) -> CanonicalTraceRowHash:
    _exact(trace_schema_ref, ObjectRef, "trace_schema_ref")
    _exact(predecessor_state_payload_hash, StatePayloadHash, "predecessor_state_payload_hash")
    _exact(successor_state_payload_hash, StatePayloadHash, "successor_state_payload_hash")
    predecessor = predecessor_trace_row_hash_or_genesis
    if type(predecessor) is CanonicalTraceRowHash:
        predecessor_value = str(predecessor)
    elif predecessor == "GENESIS":
        predecessor_value = "GENESIS"
    else:
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "predecessor trace row must be CanonicalTraceRowHash or GENESIS",
        )
    return _hash_preimage(
        {
            "admission_group_and_ownership_facts": _as_ecj1(
                admission_group_and_ownership_facts
            ),
            "after_policy_memory_payload_hash_or_not_applicable": _as_ecj1(
                after_policy_memory_payload_hash_or_not_applicable
            ),
            "augmented_replay_state_hash_or_not_applicable": _as_ecj1(
                augmented_replay_state_hash_or_not_applicable
            ),
            "before_policy_memory_payload_hash_or_not_applicable": _as_ecj1(
                before_policy_memory_payload_hash_or_not_applicable
            ),
            "declared_scientific_or_model_faults": _ordered(
                declared_scientific_or_model_faults,
                "declared_scientific_or_model_faults",
            ),
            "epoch": _as_ecj1(epoch),
            "event_key": _as_ecj1(event_key),
            "hash_domain": "ebu.canonical-trace-row.v1",
            "information_view_hash_or_not_applicable": _as_ecj1(
                information_view_hash_or_not_applicable
            ),
            "lifecycle_transitions": _ordered(
                lifecycle_transitions, "lifecycle_transitions"
            ),
            "phase_ordinal": phase_ordinal,
            "predecessor_state_payload_hash": str(predecessor_state_payload_hash),
            "predecessor_trace_row_hash_or_genesis": predecessor_value,
            "proposal_set_hash_or_not_applicable": _as_ecj1(
                proposal_set_hash_or_not_applicable
            ),
            "resolution_state": resolution_state,
            "row_index": row_index,
            "scientific_object_refs": _ordered(
                scientific_object_refs, "scientific_object_refs"
            ),
            "scientifically_relevant_failures": _ordered(
                scientifically_relevant_failures,
                "scientifically_relevant_failures",
            ),
            "successor_state_payload_hash": str(successor_state_payload_hash),
            "trace_schema_ref": trace_schema_ref.to_ecj1(),
            "typed_quantities": _ordered(typed_quantities, "typed_quantities"),
            "uncertainty_values": _ordered(
                uncertainty_values, "uncertainty_values"
            ),
        },
        CanonicalTraceRowHash,
    )


def compute_canonical_trace_prefix_hash(
    *,
    trace_header: ECJ1Value,
    ordered_rows: tuple[Any, ...] | list[Any],
    confirmed_row_count: int,
    last_confirmed_state_payload_hash: StatePayloadHash,
    last_confirmed_policy_memory_payload_hash_or_not_applicable: ECJ1Value,
    last_confirmed_augmented_replay_state_hash_or_not_applicable: ECJ1Value,
    completeness_state: str,
) -> CanonicalTracePrefixHash:
    _exact(
        last_confirmed_state_payload_hash,
        StatePayloadHash,
        "last_confirmed_state_payload_hash",
    )
    return _hash_preimage(
        {
            "completeness_state": completeness_state,
            "confirmed_row_count": confirmed_row_count,
            "hash_domain": "ebu.canonical-trace-prefix.v1",
            "last_confirmed_augmented_replay_state_hash_or_not_applicable": _as_ecj1(
                last_confirmed_augmented_replay_state_hash_or_not_applicable
            ),
            "last_confirmed_policy_memory_payload_hash_or_not_applicable": _as_ecj1(
                last_confirmed_policy_memory_payload_hash_or_not_applicable
            ),
            "last_confirmed_state_payload_hash": str(
                last_confirmed_state_payload_hash
            ),
            "ordered_rows": _ordered(ordered_rows, "ordered_rows"),
            "trace_header": _as_ecj1(trace_header),
        },
        CanonicalTracePrefixHash,
    )


def compute_canonical_trace_payload_hash(
    *,
    trace_schema_ref: ObjectRef,
    accepted_configuration_object_content_hash: ObjectContentHash,
    execution_semantics_hash: ExecutionSemanticsHash,
    initial_state_payload_hash: StatePayloadHash,
    initial_policy_memory_payload_hash_or_not_applicable: ECJ1Value,
    initial_augmented_replay_state_hash_or_not_applicable: ECJ1Value,
    ordered_external_scientific_input_payload_hashes: tuple[Any, ...] | list[Any],
    fault_schedule_object_content_hash_or_not_applicable: ECJ1Value,
    stochastic_stream_identities_and_draw_coordinates_or_not_applicable: ECJ1Value,
    ordered_rows: tuple[Any, ...] | list[Any],
    terminal_or_last_confirmed_state_payload_hash: StatePayloadHash,
    terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable: ECJ1Value,
    terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable: ECJ1Value,
    confirmed_row_count: int,
    trace_completeness_state: str,
) -> CanonicalScientificTracePayloadHash:
    _exact(trace_schema_ref, ObjectRef, "trace_schema_ref")
    _exact(
        accepted_configuration_object_content_hash,
        ObjectContentHash,
        "accepted_configuration_object_content_hash",
    )
    _exact(execution_semantics_hash, ExecutionSemanticsHash, "execution_semantics_hash")
    _exact(initial_state_payload_hash, StatePayloadHash, "initial_state_payload_hash")
    _exact(
        terminal_or_last_confirmed_state_payload_hash,
        StatePayloadHash,
        "terminal_or_last_confirmed_state_payload_hash",
    )
    return _hash_preimage(
        {
            "accepted_configuration_object_content_hash": str(
                accepted_configuration_object_content_hash
            ),
            "confirmed_row_count": confirmed_row_count,
            "execution_semantics_hash": str(execution_semantics_hash),
            "fault_schedule_object_content_hash_or_not_applicable": _as_ecj1(
                fault_schedule_object_content_hash_or_not_applicable
            ),
            "hash_domain": "ebu.canonical-scientific-trace-payload.v1",
            "initial_augmented_replay_state_hash_or_not_applicable": _as_ecj1(
                initial_augmented_replay_state_hash_or_not_applicable
            ),
            "initial_policy_memory_payload_hash_or_not_applicable": _as_ecj1(
                initial_policy_memory_payload_hash_or_not_applicable
            ),
            "initial_state_payload_hash": str(initial_state_payload_hash),
            "ordered_external_scientific_input_payload_hashes": _ordered(
                ordered_external_scientific_input_payload_hashes,
                "ordered_external_scientific_input_payload_hashes",
            ),
            "ordered_rows": _ordered(ordered_rows, "ordered_rows"),
            "stochastic_stream_identities_and_draw_coordinates_or_not_applicable": _as_ecj1(
                stochastic_stream_identities_and_draw_coordinates_or_not_applicable
            ),
            "terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable": _as_ecj1(
                terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable
            ),
            "terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable": _as_ecj1(
                terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable
            ),
            "terminal_or_last_confirmed_state_payload_hash": str(
                terminal_or_last_confirmed_state_payload_hash
            ),
            "trace_completeness_state": trace_completeness_state,
            "trace_schema_ref": trace_schema_ref.to_ecj1(),
        },
        CanonicalScientificTracePayloadHash,
    )


def compute_artifact_byte_hash(exact_artifact_bytes: bytes) -> ArtifactByteHash:
    if type(exact_artifact_bytes) is not bytes:
        _fail(
            FailureCode.DIGEST_TYPE_MISMATCH,
            "artifact input must be exact bytes",
        )
    length = len(exact_artifact_bytes)
    if length > 0xFFFFFFFFFFFFFFFF:
        _fail(FailureCode.ARTIFACT_TOO_LARGE, "artifact exceeds UINT64 length")
    framed = (
        b"ebu.artifact-bytes.v1"
        + b"\x00"
        + length.to_bytes(8, "big")
        + exact_artifact_bytes
    )
    return ArtifactByteHash.from_hex(hashlib.sha256(framed).hexdigest())


def compute_source_file_raw_sha256(
    exact_file_bytes: bytes,
) -> SourceFileRawSha256:
    if type(exact_file_bytes) is not bytes:
        _fail(FailureCode.DIGEST_TYPE_MISMATCH, "source input must be exact bytes")
    return SourceFileRawSha256.from_hex(hashlib.sha256(exact_file_bytes).hexdigest())


def _compute_authorization_use_key(
    *,
    stage_authorization_ref: ObjectRef,
    requested_operation: str,
    target_object_refs: tuple[ObjectRef, ...] | list[ObjectRef],
    accepted_configuration_ref_or_not_applicable: ObjectRef | str,
    accepted_execution_binding_ref_or_not_applicable: ObjectRef | str,
    execution_identity_or_not_applicable: ECJ1Value,
) -> AuthorizationUseKey:
    _exact(stage_authorization_ref, ObjectRef, "stage_authorization_ref")
    if not all(type(ref) is ObjectRef for ref in target_object_refs):
        _fail(FailureCode.DIGEST_TYPE_MISMATCH, "target_object_refs require ObjectRef")

    def ref_or_na(value: ObjectRef | str, field: str) -> ECJ1Value:
        if type(value) is ObjectRef:
            return value.to_ecj1()
        if value == "NOT_APPLICABLE":
            return "NOT_APPLICABLE"
        _fail(FailureCode.DIGEST_TYPE_MISMATCH, f"{field} requires ObjectRef or NOT_APPLICABLE")

    return _hash_preimage(
        {
            "accepted_configuration_ref_or_not_applicable": ref_or_na(
                accepted_configuration_ref_or_not_applicable,
                "accepted_configuration_ref_or_not_applicable",
            ),
            "accepted_execution_binding_ref_or_not_applicable": ref_or_na(
                accepted_execution_binding_ref_or_not_applicable,
                "accepted_execution_binding_ref_or_not_applicable",
            ),
            "execution_identity_or_not_applicable": _as_ecj1(
                execution_identity_or_not_applicable
            ),
            "hash_domain": "ebu.authorization-use-key.v1",
            "requested_operation": requested_operation,
            "stage_authorization_ref": stage_authorization_ref.to_ecj1(),
            "target_object_refs": _ordered(target_object_refs, "target_object_refs"),
        },
        AuthorizationUseKey,
    )


__all__ = (
    "compute_artifact_byte_hash",
    "compute_augmented_replay_state_hash",
    "compute_canonical_trace_payload_hash",
    "compute_canonical_trace_prefix_hash",
    "compute_canonical_trace_row_hash",
    "compute_execution_semantics_hash",
    "compute_information_view_hash",
    "compute_object_content_hash",
    "compute_policy_memory_payload_hash",
    "compute_proposal_set_hash",
    "compute_represented_state_projection_hash",
    "compute_source_file_raw_sha256",
    "compute_state_payload_hash",
    "compute_authorization_use_key",
)


# Framework I-5 additions are deliberately appended so every accepted I-1
# through I-4 hash declaration and callable above retains its original body.
from dataclasses import dataclass as _dataclass
from typing import Literal, NoReturn, TypeAlias

from .errors import (
    FailureInterfaceRef as _FailureInterfaceRef,
    FailureStage as _FailureStage,
    RetryClass as _RetryClass,
    ScientificStatusEffect as _ScientificStatusEffect,
)


def _i5_hash_failure(code: FailureCode, interface: str, summary: str) -> NoReturn:
    _fail(
        code,
        summary,
        stage=_FailureStage.I5,
        interface_ref=_FailureInterfaceRef(
            "ebu_framework.hashing", interface, "1.0.0"
        ),
        scientific_status_effect=_ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=_RetryClass.FORBIDDEN,
    )


def _i5_hash_formation(interface: str) -> NoReturn:
    _i5_hash_failure(
        FailureCode.I5_RECORD_FORMATION_INVALID,
        interface,
        f"{interface} rejected I5_RECORD_FORMATION_INVALID",
    )


def _i5_strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected_fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected_fields:
            _i5_hash_formation(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _valid_i5_digest_text(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 71
        and value.startswith("sha256:")
        and all(character in "0123456789abcdef" for character in value[7:])
    )


class _I5DigestBehavior:
    value: str

    def __post_init__(self) -> None:
        if not _valid_i5_digest_text(self.value):
            _i5_hash_formation(type(self).__name__)

    @classmethod
    def from_hex(cls, hexadecimal: str):
        return cls(value="sha256:" + hexadecimal)

    @property
    def hex_digest(self) -> str:
        return self.value[7:]

    def __str__(self) -> str:
        return self.value

    def to_ecj1(self) -> dict[str, str]:
        return {"value": self.value}


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class EventKeyDigest(_I5DigestBehavior):
    value: str


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class EventDeclarationDigest(_I5DigestBehavior):
    value: str


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class OwnershipDigest(_I5DigestBehavior):
    value: str


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class PhaseCommitDigest(_I5DigestBehavior):
    value: str


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class DurabilityEvidenceDigest(_I5DigestBehavior):
    value: str


@_i5_strict_formation
@_dataclass(frozen=True, slots=True, order=True, kw_only=True)
class RunEnvelopeDigest(_I5DigestBehavior):
    value: str


TraceDigest: TypeAlias = (
    CanonicalTraceRowHash
    | CanonicalTracePrefixHash
    | CanonicalScientificTracePayloadHash
)


def _i5_frame_fields(domain: bytes, fields: tuple[bytes, ...], /) -> bytes:
    if type(domain) is not bytes or not domain or type(fields) is not tuple:
        _i5_hash_failure(
            FailureCode.HASH_DOMAIN_MISMATCH,
            "_i5_frame_fields",
            "I-5 hash framing requires an exact nonempty byte domain and tuple",
        )
    if not all(type(field) is bytes for field in fields):
        _i5_hash_failure(
            FailureCode.HASH_DOMAIN_MISMATCH,
            "_i5_frame_fields",
            "I-5 hash fields must be exact bytes",
        )
    return b"".join(
        len(field).to_bytes(8, "big") + field for field in (domain, *fields)
    )


def _i5_digest(
    *,
    domain: bytes,
    fields: tuple[bytes, ...],
    digest_type: type,
    interface: str,
):
    preimage = _i5_frame_fields(domain, fields)
    hexadecimal = hashlib.sha256(preimage).hexdigest()
    result = digest_type(value="sha256:" + hexadecimal)
    if hashlib.sha256(preimage).hexdigest() != result.hex_digest:
        _i5_hash_failure(
            FailureCode.I5_HASH_COLLISION,
            interface,
            f"{interface} detected an inconsistent I-5 hash result",
        )
    return result


def _i5_visible_ascii(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.isascii()
        and all(0x21 <= ord(character) <= 0x7E for character in value)
    )


def _i5_scientific_id_text(value: object) -> bool:
    if type(value) is not str:
        return False
    fields = value.split(":")
    if len(fields) != 4 or fields[0] != "ebu":
        return False
    alphabet = frozenset(
        "abcdefghijklmnopqrstuvwxyz0123456789._-"
    )
    return all(
        bool(field)
        and field[0] in "abcdefghijklmnopqrstuvwxyz0123456789"
        and all(character in alphabet for character in field)
        for field in fields[1:]
    )


def compute_event_key_digest(
    *,
    epoch: int,
    phase_ordinal: int,
    declared_priority: int,
    group_or_scope_id: str,
    event_kind: str,
    primary_object_id: str,
    local_sequence: int,
) -> EventKeyDigest:
    if not (
        type(epoch) is int
        and epoch >= 0
        and type(phase_ordinal) is int
        and 1 <= phase_ordinal <= 10
        and type(declared_priority) is int
        and _i5_visible_ascii(group_or_scope_id)
        and _i5_visible_ascii(event_kind)
        and _i5_scientific_id_text(primary_object_id)
        and type(local_sequence) is int
        and local_sequence >= 0
    ):
        _i5_hash_failure(
            FailureCode.EVENT_KEY_INVALID,
            "compute_event_key_digest",
            "compute_event_key_digest rejected EVENT_KEY_INVALID",
        )
    fields = tuple(
        value.encode("utf-8", "strict")
        for value in (
            str(epoch),
            str(phase_ordinal),
            str(declared_priority),
            group_or_scope_id,
            event_kind,
            primary_object_id,
            str(local_sequence),
        )
    )
    return _i5_digest(
        domain=b"ebu.event-key.v1",
        fields=fields,
        digest_type=EventKeyDigest,
        interface="compute_event_key_digest",
    )


def compute_event_declaration_digest(
    *,
    event_key_digest: EventKeyDigest,
    event_ref: ObjectRef,
    declared_simultaneity_ref_or_not_applicable: ObjectRef | Applicability,
    payload_hash: ObjectContentHash,
    predecessor_event_key_digest_or_not_applicable: (
        EventKeyDigest | Applicability
    ),
) -> EventDeclarationDigest:
    simultaneity = declared_simultaneity_ref_or_not_applicable
    predecessor = predecessor_event_key_digest_or_not_applicable
    if not (
        type(event_key_digest) is EventKeyDigest
        and type(event_ref) is ObjectRef
        and (
            type(simultaneity) is ObjectRef
            or simultaneity is Applicability.NOT_APPLICABLE
        )
        and type(payload_hash) is ObjectContentHash
        and (
            type(predecessor) is EventKeyDigest
            or predecessor is Applicability.NOT_APPLICABLE
        )
    ):
        _i5_hash_failure(
            FailureCode.EVENT_IDENTITY_INVALID,
            "compute_event_declaration_digest",
            "compute_event_declaration_digest rejected EVENT_IDENTITY_INVALID",
        )
    fields = (
        str(event_key_digest).encode(),
        str(event_ref.object_id).encode(),
        (
            str(simultaneity.object_id).encode()
            if type(simultaneity) is ObjectRef
            else Applicability.NOT_APPLICABLE.value.encode()
        ),
        str(payload_hash).encode(),
        (
            str(predecessor).encode()
            if type(predecessor) is EventKeyDigest
            else Applicability.NOT_APPLICABLE.value.encode()
        ),
    )
    return _i5_digest(
        domain=b"ebu.event-declaration.v1",
        fields=fields,
        digest_type=EventDeclarationDigest,
        interface="compute_event_declaration_digest",
    )


def _i5_projection_digest(
    projection: ECJ1Value,
    *,
    domain: bytes,
    digest_type: type,
    interface: str,
    failure_code: FailureCode,
):
    if type(projection) is list and all(type(item) is str for item in projection):
        fields = tuple(item.encode("utf-8", "strict") for item in projection)
    else:
        try:
            fields = (bytes(encode_ecj1(projection)),)
        except Exception:
            _i5_hash_failure(
                failure_code,
                interface,
                f"{interface} rejected {failure_code.value}",
            )
    if not fields:
        _i5_hash_failure(
            failure_code,
            interface,
            f"{interface} rejected {failure_code.value}",
        )
    return _i5_digest(
        domain=domain,
        fields=fields,
        digest_type=digest_type,
        interface=interface,
    )


def compute_ownership_digest(
    projection_kind: Literal["CLAIM", "EPOCH"],
    projection: ECJ1Value,
    /,
) -> OwnershipDigest:
    if type(projection_kind) is not str or projection_kind not in {
        "CLAIM",
        "EPOCH",
    }:
        _i5_hash_failure(
            FailureCode.UPDATE_OWNERSHIP_CLAIM_INVALID,
            "compute_ownership_digest",
            "compute_ownership_digest rejected UPDATE_OWNERSHIP_CLAIM_INVALID",
        )
    return _i5_projection_digest(
        projection,
        domain=(
            b"ebu.ownership-claim.v1"
            if projection_kind == "CLAIM"
            else b"ebu.epoch-ownership.v1"
        ),
        digest_type=OwnershipDigest,
        interface="compute_ownership_digest",
        failure_code=FailureCode.UPDATE_OWNERSHIP_CLAIM_INVALID,
    )


def compute_phase_commit_digest(
    projection: ECJ1Value, /
) -> PhaseCommitDigest:
    return _i5_projection_digest(
        projection,
        domain=b"ebu.phase-commit.v1",
        digest_type=PhaseCommitDigest,
        interface="compute_phase_commit_digest",
        failure_code=FailureCode.PHASE_COMMIT_RECORD_INVALID,
    )


def compute_durability_evidence_digest(
    projection_without_evidence_digest: ECJ1Value, /
) -> DurabilityEvidenceDigest:
    return _i5_projection_digest(
        projection_without_evidence_digest,
        domain=b"ebu.durability-evidence.v1",
        digest_type=DurabilityEvidenceDigest,
        interface="compute_durability_evidence_digest",
        failure_code=FailureCode.DURABILITY_EVIDENCE_INCONSISTENT,
    )


def compute_run_envelope_digest(
    projection_without_envelope_digest: ECJ1Value, /
) -> RunEnvelopeDigest:
    return _i5_projection_digest(
        projection_without_envelope_digest,
        domain=b"ebu.run-envelope.v1",
        digest_type=RunEnvelopeDigest,
        interface="compute_run_envelope_digest",
        failure_code=FailureCode.RUN_TRACE_ENVELOPE_INVALID,
    )


__all__ += (
    "EventKeyDigest",
    "EventDeclarationDigest",
    "OwnershipDigest",
    "PhaseCommitDigest",
    "DurabilityEvidenceDigest",
    "RunEnvelopeDigest",
    "TraceDigest",
    "compute_event_key_digest",
    "compute_event_declaration_digest",
    "compute_ownership_digest",
    "compute_phase_commit_digest",
    "compute_durability_evidence_digest",
    "compute_run_envelope_digest",
)
