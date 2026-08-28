from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from stage_e_harness.schema import AUTHORITY_METADATA_KEYS, SUPPORTED_KEYWORDS, Validator, audit_schema_vocabulary
from stage_e_harness.canonical import strict_load


ROOT = Path(__file__).resolve().parents[2]


class StageESchemaRecordTests(unittest.TestCase):
    def test_exact_derived_vocabulary_includes_min_properties(self) -> None:
        contract = strict_load(ROOT / "stage_e_scientific_harness_contract.json")
        profile = contract["schema_profile"]
        seen: set[str] = set()
        for name, metadata in profile["authority_metadata_keys_by_schema"].items():
            schema = strict_load(ROOT / name)
            seen.update(audit_schema_vocabulary(schema, allowed_metadata=metadata))
        self.assertEqual(tuple(key for key in SUPPORTED_KEYWORDS if key in seen), SUPPORTED_KEYWORDS)
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


if __name__ == "__main__":
    unittest.main()
