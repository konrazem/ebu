from __future__ import annotations

from pathlib import Path
import sys
import unittest

from stage_e_harness.canonical import Refusal, strict_load
from stage_e_harness.execution import BLOCKED_PROJECT_RUNNERS, StageEExecutionRefusal, guard_registered_configuration
from stage_e_harness.registry import STUDY_IDS, load_bindings, validate_partition


ROOT = Path(__file__).resolve().parents[2]


class StageEAdaptersAndGuardsTests(unittest.TestCase):
    def test_exact_adapter_registry_and_pre_import_refusals(self) -> None:
        matrix = strict_load(ROOT / "stage_d_scientific_validation_master_matrix.json")
        validate_partition()
        bindings = load_bindings(matrix)
        self.assertEqual(tuple(binding.study_id for binding in bindings), STUDY_IDS)
        before = set(sys.modules)
        for binding in bindings:
            with self.assertRaises(StageEExecutionRefusal) as caught:
                binding.refuse_registered_route(binding.study_id)
            self.assertEqual(caught.exception.receipt["project_runner_import_count"], 0)
        with self.assertRaises(StageEExecutionRefusal) as caught:
            guard_registered_configuration("SD-01-GROWTH-v1")
        self.assertEqual(caught.exception.receipt["project_runner_import_count"], 0)
        self.assertEqual(caught.exception.receipt["model_state_advance_count"], 0)
        with self.assertRaises(StageEExecutionRefusal):
            guard_registered_configuration("SD-01/NAMED-CONFIGURATION")
        self.assertFalse(any(name in sys.modules and name not in before for name in BLOCKED_PROJECT_RUNNERS))

    def test_unknown_study_refuses(self) -> None:
        from stage_e_harness.registry import continuation_class
        with self.assertRaises(Refusal):
            continuation_class("SD-15")


if __name__ == "__main__":
    unittest.main()
