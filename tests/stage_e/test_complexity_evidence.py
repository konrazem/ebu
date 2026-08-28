from __future__ import annotations

import unittest

from stage_e_harness.canonical import Refusal
from stage_e_harness.dag import complexity_cell as dag_cell
from stage_e_harness.mobius import complexity_cell as mobius_cell


class StageEComplexityEvidenceTests(unittest.TestCase):
    def test_mobius_exact_operation_and_storage_counters(self) -> None:
        cell = mobius_cell(8, 0)
        self.assertEqual(cell["primary_operations"], 8 * (1 << 7))
        self.assertEqual(cell["logical_storage_slots"], 1 << 8)
        self.assertGreater(cell["peak_process_tree_rss_bytes"], 0)
        with self.assertRaises(Refusal):
            mobius_cell(19, 0)

    def test_dag_exact_linear_counters(self) -> None:
        cell = dag_cell(128, 256, "sparse")
        self.assertLessEqual(cell["primary_operations"], 128 + 256)
        self.assertEqual(cell["ready_node_comparisons"], 0)
        self.assertGreater(cell["peak_process_tree_rss_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
