"""V1 T0 checks for every I-0 hash projection constructible at I-1."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from ebu_framework.errors import FailureCode, FrameworkError
from ebu_framework.hashing import (
    _compute_authorization_use_key,
    compute_artifact_byte_hash,
    compute_augmented_replay_state_hash,
    compute_canonical_trace_payload_hash,
    compute_canonical_trace_prefix_hash,
    compute_canonical_trace_row_hash,
    compute_execution_semantics_hash,
    compute_information_view_hash,
    compute_object_content_hash,
    compute_policy_memory_payload_hash,
    compute_proposal_set_hash,
    compute_represented_state_projection_hash,
    compute_source_file_raw_sha256,
    compute_state_payload_hash,
)
from ebu_framework.identity import (
    AugmentedClosedLoopReplayStateHash,
    CanonicalTraceRowHash,
    ExecutionSemanticsHash,
    InformationViewHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ScientificId,
    SemanticVersion,
    StatePayloadHash,
)
from safety import assert_safe_test_module, synthetic_ref


_HERE = Path(__file__).resolve().parent
_VECTORS = json.loads(
    (_HERE / "fixtures" / "hash_preimages_v1.json").read_text("utf-8")
)
_EXPECTED = _VECTORS["expected"]
_H0 = _VECTORS["synthetic_hashes"]["h0"]
_H1 = _VECTORS["synthetic_hashes"]["h1"]
_H2 = _VECTORS["synthetic_hashes"]["h2"]
_V = SemanticVersion("1.0.0")


class HashPreimageTests(unittest.TestCase):
    check_count = 0

    def checked_hash(self, name: str, actual: object) -> None:
        type(self).check_count += 1
        self.assertEqual(str(actual), _EXPECTED[name])

    def setUp(self) -> None:
        self.authority = synthetic_ref(
            "ebu:authority:validation:authority-a", "1"
        )
        self.schema = synthetic_ref("ebu:schema:validation:schema-a", "2")
        self.object_ref = synthetic_ref(
            "ebu:fixture:validation:object-a", "0"
        )
        self.policy_ref = synthetic_ref(
            "ebu:policy:validation:policy-a", "1"
        )
        self.memory_schema_ref = synthetic_ref(
            "ebu:schema:validation:memory-a", "2"
        )
        self.trace_schema_ref = synthetic_ref(
            "ebu:schema:validation:trace-a", "2"
        )
        self.result_schema_ref = synthetic_ref(
            "ebu:schema:validation:result-a", "2"
        )
        self.config_ref = synthetic_ref(
            "ebu:configuration:validation:config-a", "0"
        )

    def test_object_state_memory_and_replay_projections(self) -> None:
        self.checked_hash(
            "object_content",
            compute_object_content_hash(
                object_id=self.object_ref.object_id,
                object_kind="fixture",
                schema_id=self.schema.object_id,
                schema_version=_V,
                object_version=_V,
                authority_refs=(self.authority,),
                supersedes_ref=None,
                object_content_payload={"alpha": 1},
            ),
        )
        self.checked_hash(
            "state_payload",
            compute_state_payload_hash(
                state_schema_ref=self.schema,
                epoch=0,
                physical_state_x={"x": 1},
                topology_state_g=[],
                queue_and_transit_state_q=[],
                commitment_state_c=[],
                delayed_effect_state_ell=[],
                declared_external_inputs_applied=(),
            ),
        )
        self.checked_hash(
            "policy_memory_payload",
            compute_policy_memory_payload_hash(
                policy_ref=self.policy_ref,
                memory_schema_ref=self.memory_schema_ref,
                available_for_decision_epoch=0,
                resolution_state="PRESENT",
                memory_payload={"counter": 0},
            ),
        )
        self.checked_hash(
            "augmented_replay_state",
            compute_augmented_replay_state_hash(
                StatePayloadHash(_H0), PolicyMemoryPayloadHash(_H1)
            ),
        )

    def test_projection_view_proposal_and_semantics(self) -> None:
        self.checked_hash(
            "represented_state_projection",
            compute_represented_state_projection_hash(
                source_state_payload_hash=StatePayloadHash(_H0),
                boundary_ref=self.object_ref,
                projection_contract_ref=self.schema,
                included_coordinate_ids=("x",),
                excluded_coordinate_ids_and_resolution_states=(),
                represented_state_payload={"x": 1},
            ),
        )
        self.checked_hash(
            "information_view",
            compute_information_view_hash(
                policy_ref=self.policy_ref,
                information_contract_ref=self.schema,
                decision_epoch=0,
                current_policy_memory_payload_hash_or_not_applicable=(
                    PolicyMemoryPayloadHash(_H1)
                ),
                ordered_visible_field_records=(
                    {"availability_epoch": 0, "field_id": "x", "value": 1},
                ),
                ordered_visible_object_refs=(self.object_ref,),
            ),
        )
        self.checked_hash(
            "proposal_set",
            compute_proposal_set_hash(
                policy_ref_or_open_loop_schedule_ref=self.policy_ref,
                decision_coordinate={"epoch": 0, "sequence": 0},
                information_view_hash_or_not_applicable=InformationViewHash(_H0),
                before_policy_memory_payload_hash_or_not_applicable=(
                    PolicyMemoryPayloadHash(_H1)
                ),
                after_policy_memory_payload_hash_or_not_applicable=(
                    PolicyMemoryPayloadHash(_H2)
                ),
                ordered_proposal_payloads=({"proposal_id": "p0"},),
            ),
        )
        self.checked_hash(
            "execution_semantics",
            compute_execution_semantics_hash(
                accepted_configuration_ref=self.config_ref,
                implementation_refs=(),
                source_refs=(),
                implementation_entrypoint_semantics={"entry": "none"},
                science_affecting_runtime_constraints={},
                science_affecting_operational_exclusions=[],
                policy_memory_transition_contracts_or_not_applicable="NOT_APPLICABLE",
                fault_injection_delivery_contracts_or_not_applicable="NOT_APPLICABLE",
                event_order_contract={"version": "dynamic-v0.1"},
                arithmetic_and_numerical_policy_contracts=[],
                information_capability_contract={},
                canonical_scientific_trace_schema_ref=self.trace_schema_ref,
                scientific_result_schema_ref=self.result_schema_ref,
                stochastic_generator_and_stream_contract_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
            ),
        )

    def test_trace_row_prefix_and_payload_projections(self) -> None:
        self.checked_hash(
            "canonical_trace_row",
            compute_canonical_trace_row_hash(
                trace_schema_ref=self.trace_schema_ref,
                row_index=0,
                epoch=0,
                event_key=[0, 1, 0, "scope", "event", "object", 0],
                phase_ordinal=1,
                scientific_object_refs=(self.object_ref,),
                predecessor_state_payload_hash=StatePayloadHash(_H0),
                successor_state_payload_hash=StatePayloadHash(_H1),
                information_view_hash_or_not_applicable="NOT_APPLICABLE",
                before_policy_memory_payload_hash_or_not_applicable="NOT_APPLICABLE",
                after_policy_memory_payload_hash_or_not_applicable="NOT_APPLICABLE",
                augmented_replay_state_hash_or_not_applicable="NOT_APPLICABLE",
                proposal_set_hash_or_not_applicable="NOT_APPLICABLE",
                admission_group_and_ownership_facts={},
                typed_quantities=(),
                uncertainty_values=(),
                lifecycle_transitions=(),
                declared_scientific_or_model_faults=(),
                scientifically_relevant_failures=(),
                resolution_state="PRESENT",
                predecessor_trace_row_hash_or_genesis="GENESIS",
            ),
        )
        self.checked_hash(
            "canonical_trace_prefix",
            compute_canonical_trace_prefix_hash(
                trace_header={"schema": "v1"},
                ordered_rows=(),
                confirmed_row_count=0,
                last_confirmed_state_payload_hash=StatePayloadHash(_H0),
                last_confirmed_policy_memory_payload_hash_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
                last_confirmed_augmented_replay_state_hash_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
                completeness_state="PARTIAL_DURABLE_PREFIX",
            ),
        )
        self.checked_hash(
            "canonical_trace_payload",
            compute_canonical_trace_payload_hash(
                trace_schema_ref=self.trace_schema_ref,
                accepted_configuration_object_content_hash=ObjectContentHash(_H0),
                execution_semantics_hash=ExecutionSemanticsHash(_H1),
                initial_state_payload_hash=StatePayloadHash(_H0),
                initial_policy_memory_payload_hash_or_not_applicable="NOT_APPLICABLE",
                initial_augmented_replay_state_hash_or_not_applicable="NOT_APPLICABLE",
                ordered_external_scientific_input_payload_hashes=(),
                fault_schedule_object_content_hash_or_not_applicable="NOT_APPLICABLE",
                stochastic_stream_identities_and_draw_coordinates_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
                ordered_rows=(),
                terminal_or_last_confirmed_state_payload_hash=StatePayloadHash(_H0),
                terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
                terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable=(
                    "NOT_APPLICABLE"
                ),
                confirmed_row_count=0,
                trace_completeness_state="COMPLETE",
            ),
        )

    def test_artifact_raw_source_and_authorization_use_domains(self) -> None:
        artifact = bytes.fromhex(_VECTORS["artifact"]["bytes_hex"])
        self.assertEqual(
            (
                b"ebu.artifact-bytes.v1"
                + b"\x00"
                + len(artifact).to_bytes(8, "big")
                + artifact
            ).hex(),
            _VECTORS["artifact"]["frame_hex"],
        )
        type(self).check_count += 1
        self.assertEqual(
            str(compute_artifact_byte_hash(artifact)),
            _VECTORS["artifact"]["expected"],
        )
        type(self).check_count += 1
        self.assertEqual(
            str(compute_source_file_raw_sha256(artifact)),
            _VECTORS["raw_source"]["expected"],
        )
        type(self).check_count += 1
        self.checked_hash(
            "authorization_use_key",
            _compute_authorization_use_key(
                stage_authorization_ref=self.authority,
                requested_operation="VALIDATE_SYNTHETIC",
                target_object_refs=(self.object_ref,),
                accepted_configuration_ref_or_not_applicable="NOT_APPLICABLE",
                accepted_execution_binding_ref_or_not_applicable="NOT_APPLICABLE",
                execution_identity_or_not_applicable="NOT_APPLICABLE",
            ),
        )

    def test_metadata_exclusion_self_field_exclusion_and_typed_domains(self) -> None:
        arguments = dict(
            object_id=self.object_ref.object_id,
            object_kind="fixture",
            schema_id=self.schema.object_id,
            schema_version=_V,
            object_version=_V,
            authority_refs=(self.authority,),
            supersedes_ref=None,
            object_content_payload={"alpha": 1},
        )
        first = compute_object_content_hash(**arguments)
        record_a = {**arguments, "object_content_hash": first, "storage_uri": "/a"}
        record_b = {**arguments, "object_content_hash": first, "storage_uri": "/b"}
        self.assertEqual(
            compute_object_content_hash(**{key: record_a[key] for key in arguments}),
            compute_object_content_hash(**{key: record_b[key] for key in arguments}),
        )
        type(self).check_count += 1
        with self.assertRaises(TypeError):
            compute_object_content_hash(**record_a)
        type(self).check_count += 1
        with self.assertRaises(FrameworkError) as caught:
            compute_augmented_replay_state_hash(
                ObjectContentHash(_H0), PolicyMemoryPayloadHash(_H1)
            )
        self.assertEqual(
            caught.exception.envelope.failure_code,
            FailureCode.DIGEST_TYPE_MISMATCH,
        )
        type(self).check_count += 1
        self.assertNotEqual(
            ObjectContentHash(_H0),
            StatePayloadHash(_H0),
        )
        type(self).check_count += 1

    def test_static_non_reachability(self) -> None:
        self.assertGreater(assert_safe_test_module(Path(__file__)), 0)
        type(self).check_count += 1

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"V1_HASH_COMPLETED_CHECKS={cls.check_count}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
