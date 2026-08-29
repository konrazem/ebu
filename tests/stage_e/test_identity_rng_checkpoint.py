from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from stage_e_harness.canonical import Refusal, canonical_bytes, canonical_digest, strict_load
from stage_e_harness.checkpoint import continuation_equivalence, validate_counter_state
from stage_e_harness.rng import Counter, bernoulli, categorical, exact_residue, u64


ROOT = Path(__file__).resolve().parents[2]


class StageEIdentityRngCheckpointTests(unittest.TestCase):
    def test_canonical_round_trip_and_counter_vectors(self) -> None:
        value = {"z": [3, 2, 1], "a": {"β": 7}}
        self.assertEqual(canonical_digest(value), canonical_digest(strict_loads_for_test(canonical_bytes(value))))
        counter = Counter("SD-09", "NON-SCIENTIFIC-VECTOR", 17, "shock", 3, 1, 0)
        self.assertEqual([u64(counter, index) for index in range(4)], [u64(counter, index) for index in range(4)])
        self.assertEqual(exact_residue(counter, 1000).draw_status, "READY")
        self.assertIsInstance(bernoulli(counter, 1, 1000)[0], bool)
        self.assertIn(categorical(counter, (("a", 1), ("b", 49)), 50)[0], {"a", "b"})

    def test_deterministic_and_stochastic_checkpoint_closure(self) -> None:
        deterministic = strict_load(ROOT / "tests/stage_e/fixtures/deterministic_empty_checkpoint.json")
        stochastic = strict_load(ROOT / "tests/stage_e/fixtures/stochastic_checkpoint.json")
        validate_counter_state(deterministic)
        validate_counter_state(stochastic)
        changed = deepcopy(deterministic); changed["ordered_permitted_stream_ids"] = ["dummy"]
        with self.assertRaises(Refusal):
            validate_counter_state(changed)

    def test_synthetic_slice_equivalence(self) -> None:
        self.assertEqual(continuation_equivalence(tuple(f"SD-{index:02d}" for index in range(1, 15))), {"studies": 14, "slice_comparisons": 42})


def strict_loads_for_test(data: bytes):
    from stage_e_harness.canonical import strict_loads
    return strict_loads(data)


if __name__ == "__main__":
    unittest.main()
