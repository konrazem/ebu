from __future__ import annotations

from fractions import Fraction
import unittest

from stage_e_harness.canonical import Refusal
from stage_e_harness.mobius import agreement_suite, exact_case, fast_coefficients


class StageEMobiusOracleTests(unittest.TestCase):
    def test_complete_registered_small_case_domain(self) -> None:
        result = agreement_suite()
        self.assertEqual((result["deterministic_cases"], result["randomized_cases"], result["total_cases"]), (104, 384, 488))

    def test_nonzero_empty_set_and_reduced_rational_exactness(self) -> None:
        result = exact_case([Fraction(7, 3), Fraction(10, 3), Fraction(4, 3), Fraction(13, 3)], 2)
        self.assertEqual(result.counters.subset_count, 4)
        with self.assertRaises(Refusal):
            fast_coefficients([0] * (1 << 19), 19)


if __name__ == "__main__":
    unittest.main()
