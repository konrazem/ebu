from __future__ import annotations

import unittest

from stage_e_harness.growth import EPOCH_BRANCH_WITNESS, SAME_TICK_PHASES, growth_conformance
from stage_e_harness.recursive import recursive_conformance


class StageEDynamicGrowthConformanceTests(unittest.TestCase):
    def test_recursive_mobius_poset_and_transport_oracles(self) -> None:
        result = recursive_conformance()
        self.assertEqual(len(result["macro_cases"]), 270)
        self.assertEqual(len(result["poset_base_cases"]), 32)
        self.assertEqual(len(result["poset_correction_cases"]), 224)
        self.assertEqual(len(result["transport_scalar_cases"]), 90)
        self.assertEqual(len(result["transport_direct_cases"]), 15)
        self.assertEqual(len(result["transport_correction_cases"]), 180)
        self.assertEqual(len(result["transport_refusal_cases"]), 150)
        self.assertEqual(result["mismatch_count"], 0)

    def test_bounded_growth_reconstruction_and_event_order(self) -> None:
        result = growth_conformance()
        self.assertEqual(result["branch_witness"], EPOCH_BRANCH_WITNESS)
        self.assertEqual(result["same_tick_phases"], list(SAME_TICK_PHASES))
        self.assertEqual(result["microcase_count"], 6)
        self.assertTrue(all(case["stale_cache_hits"] == 0 for case in result["microcases"]))
        cases = {case["topology"]: case for case in result["microcases"]}
        for case in cases.values():
            self.assertLessEqual(case["incremental_operations"], case["full_operations"])
            self.assertLessEqual(case["reuse_operations"], case["full_operations"])
        for topology in ("broad_reconfiguration", "boundary_crossing"):
            self.assertTrue(cases[topology]["complete_invalidation"])
            self.assertEqual(cases[topology]["reuse_operations"], cases[topology]["incremental_operations"])
        for topology in ("recursive", "non_fibonacci_recursive", "random_nonrecursive", "alias_dependent"):
            self.assertFalse(cases[topology]["complete_invalidation"])
        self.assertEqual(result["registered_campaign_runs_executed"], 0)
        self.assertEqual(result["scientific_rows_populated"], 0)


if __name__ == "__main__":
    unittest.main()
