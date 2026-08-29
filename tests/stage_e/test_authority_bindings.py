from __future__ import annotations

import json
from pathlib import Path
import unittest

from stage_e_harness.canonical import assert_text_integrity, strict_load
from stage_e_harness.records import RELEASE_ZERO_COUNTERS, SCIENTIFIC_ZERO_COUNTERS


ROOT = Path(__file__).resolve().parents[2]


class StageEAuthorityBindingTests(unittest.TestCase):
    def test_closed_implementation_scope_and_predecessors(self) -> None:
        manifest = strict_load(ROOT / "stage_e_scientific_harness_implementation_path_manifest.json")
        scope = manifest["prospective_harness_implementation"]
        self.assertEqual(len(scope["modified_paths"]), 1)
        self.assertEqual(len(scope["new_paths"]), 45)
        self.assertEqual(len(set(scope["modified_paths"] + scope["new_paths"])), 46)
        predecessor = strict_load(ROOT / "stage_e_scientific_harness_predecessor_manifest.json")
        self.assertEqual(predecessor["source_count"], 17)
        self.assertEqual(len({row["path"] for row in predecessor["source_rows"]}), 17)

    def test_authority_text_and_zero_boundaries(self) -> None:
        contract = strict_load(ROOT / "stage_e_scientific_harness_contract.json")
        for path in contract["candidate_files"]:
            assert_text_integrity((ROOT / path).read_bytes())
        self.assertEqual(len(SCIENTIFIC_ZERO_COUNTERS), 11)
        self.assertTrue(all(value == 0 for value in SCIENTIFIC_ZERO_COUNTERS.values()))
        self.assertEqual(len(RELEASE_ZERO_COUNTERS), 6)
        self.assertTrue(all(value == 0 for value in RELEASE_ZERO_COUNTERS.values()))


if __name__ == "__main__":
    unittest.main()
