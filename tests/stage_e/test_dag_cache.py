from __future__ import annotations

from copy import deepcopy
import unittest

from stage_e_harness.cache import CACHE_KEY_FIELDS, base_key, exercise_controls, exercise_controls_detail, validate_key
from stage_e_harness.canonical import Refusal
from stage_e_harness.dag import agreement_suite, exact_oracle_case


class StageEDagCacheTests(unittest.TestCase):
    def test_dag_complete_and_adversarial_domain(self) -> None:
        self.assertEqual(agreement_suite(), {"complete_cases": 33867, "adversarial_cases": 1120, "hash_cases": 4480, "valid_cases": 39467, "invalid_cases": 14})
        result = exact_oracle_case(4, [(0, 1), (0, 2), (1, 3), (2, 3)], (0,))
        self.assertEqual(result.order, (0, 1, 2, 3))

    def test_cache_complete_key_controls_and_invalidation(self) -> None:
        self.assertEqual(len(CACHE_KEY_FIELDS), 29)
        self.assertEqual(exercise_controls(), {"controls": 17, "omission_mutations": 29, "near_miss_refusals": 13, "invalidation_receipts": 1})
        detail = exercise_controls_detail()
        self.assertEqual(detail["receipt"]["visited_keys"][0], detail["changed_seed_identity"])
        self.assertIn(detail["changed_seed_identity"], detail["declared_key_universe"])
        self.assertEqual(detail["receipt"]["invalidated_keys"], detail["expected_affected"])
        self.assertTrue(detail["dependency_edges"])
        self.assertTrue(detail["alias_edges"])
        key = base_key(); validate_key(key)
        changed = deepcopy(key); changed.pop("run_seed")
        with self.assertRaises(Refusal):
            validate_key(changed)


if __name__ == "__main__":
    unittest.main()
