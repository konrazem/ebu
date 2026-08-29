from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from scripts.validate_stage_e_harness import (
    EVIDENCE_ORDER,
    V2_RECORD_NAMES,
    _cache_v2_receipt,
    _dynamic_guard_v2,
    _schema_replay_lane,
    _v2_manifest,
    _v2_record,
    _validate_v2_semantics,
)
from stage_e_harness.cache import exercise_controls_detail
from stage_e_harness.schema import AUTHORITY_METADATA_KEYS, SUPPORTED_KEYWORDS, Validator, audit_schema_vocabulary
from stage_e_harness.canonical import strict_load
from stage_e_harness.recursive import recursive_conformance


ROOT = Path(__file__).resolve().parents[2]


class StageESchemaRecordTests(unittest.TestCase):
    def test_exact_derived_vocabulary_includes_min_properties(self) -> None:
        contract = strict_load(ROOT / "stage_e_scientific_harness_contract.json")
        profile = contract["schema_profile"]
        reconciliation = strict_load(ROOT / "stage_e_dynamic_growth_harness_reconciliation_contract.json")
        seen: set[str] = set()
        for name, metadata in profile["authority_metadata_keys_by_schema"].items():
            schema = strict_load(ROOT / name)
            seen.update(audit_schema_vocabulary(schema, allowed_metadata=metadata))
        dynamic_schema = strict_load(ROOT / "stage_d_dynamic_growth_campaign_evidence_schema.json")
        seen.update(audit_schema_vocabulary(dynamic_schema, allowed_metadata=()))
        self.assertEqual(tuple(key for key in SUPPORTED_KEYWORDS if key in seen), SUPPORTED_KEYWORDS)
        self.assertEqual(tuple(reconciliation["schema_replay"]["supported_keywords_in_order"]), SUPPORTED_KEYWORDS)
        self.assertIn("$comment", seen)
        self.assertIn("minProperties", seen)
        self.assertEqual(tuple(profile["recognized_authority_metadata_keys_in_order"]), AUTHORITY_METADATA_KEYS)

    def test_accepted_stage_d_fixtures_and_profile_substitution_refusal(self) -> None:
        schema = strict_load(ROOT / "stage_d_scientific_validation_evidence_schema.json")
        validator = Validator(schema, allowed_metadata=("prospective_negative_schema_cases", "prospective_non_evidence_schema_fixtures", "schema_version", "stage_d_instance_count", "verbatim_user_mobius_topology_controls"))
        fixtures = schema["prospective_non_evidence_schema_fixtures"]
        for name, definition in (("valid_configuration_manifest", "configuration_manifest"), ("valid_limit_decision", "limit_decision"), ("valid_computation_record", "computation_record"), ("valid_run_manifest", "run_manifest")):
            validator.validate_definition(definition, fixtures[name])
        substituted = deepcopy(fixtures["valid_configuration_manifest"])
        substituted["hard_caps"] = deepcopy(schema["$defs"]["hard_caps"]["oneOf"][13]["const"])
        self.assertFalse(validator.is_valid(substituted, validator.definition("configuration_manifest")))

    def test_stage_e_negative_fixture_inventory(self) -> None:
        fixture = strict_load(ROOT / "tests/stage_e/fixtures/schema_negative_cases.json")
        self.assertEqual(fixture["fixture_class"], "NON_SCIENTIFIC_SYNTHETIC_FIXTURE")
        self.assertEqual(len(fixture["cases"]), 24)

    def test_reconciliation_cross_record_semantic_closure(self) -> None:
        environment = {"fixture": "NON_SCIENTIFIC_SEMANTIC_CLOSURE"}
        candidate = "0" * 40
        dag_cells = []
        for cell_id, vertices, edges in (
            ("DAG-128-256", 128, 256),
            ("DAG-1024-4096", 1024, 4096),
            ("DAG-10000-50000", 10000, 50000),
            ("DAG-100000-500000", 100000, 500000),
            ("DAG-512-130816", 512, 130816),
        ):
            dag_cells.append(
                {
                    "cell_id": cell_id,
                    "vertices": vertices,
                    "edges": edges,
                    "traversal": {
                        "indegree_initializations": vertices,
                        "enqueues": vertices,
                        "dequeues": vertices,
                        "edge_inspections": edges,
                        "queue_appends": vertices,
                        "head_advances": vertices,
                        "ready_node_comparisons": 0,
                    },
                    "canonicalization": {
                        "input_edge_count": edges,
                        "canonicalization_comparisons": 0,
                        "canonicalization_auxiliary_edge_slots": edges,
                    },
                    "wall_nanoseconds": 1,
                    "process_tree_peak_rss_bytes": 1,
                    "storage_bytes": 1,
                    "trace_bytes": 1,
                    "output_bytes": 1,
                }
            )
        fields = (
            ("SCHEMA_REPLAY_V2", _schema_replay_lane(ROOT)),
            ("RECURSIVE_GROWTH_V2", recursive_conformance()),
            (
                "DAG_CACHE_CORRECTION_V2",
                {
                    "dag_valid_cases": 39467,
                    "dag_refusal_cases": 14,
                    "dag_complexity_cells": dag_cells,
                    "cache_control_count": 17,
                    "cache_key_field_count": 29,
                    "cache_key_omission_refusal_count": 29,
                    "cache_invalidation_receipt": _cache_v2_receipt(exercise_controls_detail()),
                    "stale_cache_hits": 0,
                    "mismatch_count": 0,
                },
            ),
            ("DYNAMIC_GROWTH_GUARD_V2", _dynamic_guard_v2()),
            (
                "HARNESS_ARTIFACT_V2",
                {
                    "replica_count": 3,
                    "replica_identities": [{"byte_count": 1, "sha256": "0" * 64} for _ in range(3)],
                    "all_replicas_byte_identical": True,
                    "safe_member_count": 64,
                    "unsafe_member_count": 0,
                    "source_checkout_import_count": 0,
                    "network_access_count": 0,
                },
            ),
        )
        records = [
            (
                name,
                _v2_record(ROOT, record_type, "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST", candidate, environment, record_fields),
            )
            for name, (record_type, record_fields) in zip(V2_RECORD_NAMES, fields)
        ]
        v1_manifest = {
            "records": [{"name": name, "status": "PASS"} for name in EVIDENCE_ORDER],
            "all_required_lanes_completed": True,
            "bound_supported": True,
            "stage_f_execution_authorized": False,
        }
        reconciliation_manifest = _v2_manifest(v1_manifest, records)
        _validate_v2_semantics(
            ROOT,
            v1_manifest,
            records,
            reconciliation_manifest,
            candidate_commit=candidate,
            environment=environment,
        )


if __name__ == "__main__":
    unittest.main()
