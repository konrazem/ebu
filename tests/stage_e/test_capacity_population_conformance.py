from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import unittest

from stage_e_harness.capacity_population import capacity_fixture_conformance, rational
from stage_e_harness.canonical import Refusal, strict_load


ROOT = Path(__file__).resolve().parents[2]


class StageECapacityPopulationConformanceTests(unittest.TestCase):
    def test_canonical_reduced_rationals(self) -> None:
        self.assertEqual(rational({"numerator": "-3", "denominator": "4"}), Fraction(-3, 4))
        for invalid in (
            {"numerator": "2", "denominator": "2"},
            {"numerator": "-0", "denominator": "1"},
            {"numerator": "0", "denominator": "2"},
            {"numerator": "1", "denominator": "-2"},
        ):
            with self.assertRaises(Refusal):
                rational(invalid)

    def test_authority_fixtures_are_non_scientific_conformance_only(self) -> None:
        validation = strict_load(ROOT / "stage_d_dynamic_growth_campaign_validation_contract.json")
        result = capacity_fixture_conformance(validation["schema_fixtures"])
        self.assertEqual(result["fixture_count"], 44)
        self.assertEqual(result["scientific_rows_populated"], 0)
        self.assertEqual(result["registered_campaign_runs_executed"], 0)


if __name__ == "__main__":
    unittest.main()
