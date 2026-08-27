"""Exact one-at-a-time Framework I-7 synthetic fixture validation."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ebu_framework import capabilities, canonical, dynamic, errors
from ebu_framework.identity import SourceFileRawSha256


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/framework/fixtures/dynamic_static_v1.json"
CONTRACT = ROOT / "unified_python_research_framework_i7_validation_contract.json"
FIXTURE_PATH = "tests/framework/fixtures/dynamic_static_v1.json"
FIXTURE_HASH = SourceFileRawSha256(
    "sha256-raw:cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d"
)
INTERFACE = "validate_dynamic_static_identity"


class DynamicStaticIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FIXTURE.read_bytes()
        cls.document = json.loads(cls.raw)
        cls.cases = {
            row["case_id"]: row for row in cls.document["cases"]
        }
        validation = json.loads(CONTRACT.read_text(encoding="utf-8"))
        assignments = validation["failure_identity_contract"]["assignments"]
        coordinates = {
            row["coordinate_id"]: row
            for row in validation["failure_identity_contract"]["coordinates"]
        }
        cls.failures = {
            row["vector_id"]: coordinates[row["coordinate_ref"]]
            for row in assignments
        }

    def _issue(self, case_id: str) -> capabilities.T2FixtureCapability:
        return capabilities._issue_t2_fixture_capability(
            fixture_path=FIXTURE_PATH,
            fixture_raw_sha256=FIXTURE_HASH,
            case_id=case_id,
            authorized_interface=INTERFACE,
        )

    def _case_bytes(self, case: dict[str, object]) -> bytes:
        return bytes(canonical.encode_ecj1(case))

    def _assert_failure(self, vector_id: str, operation: object) -> None:
        expected = self.failures[vector_id]
        with self.assertRaises(errors.FrameworkError) as raised:
            operation()  # type: ignore[operator]
        envelope = raised.exception.envelope
        self.assertEqual(envelope.failure_code.value, expected["failure_code"])
        self.assertEqual(envelope.stage, errors.FailureStage.I7)
        self.assertEqual(str(envelope.failure_id), expected["failure_id"])
        self.assertEqual(envelope.interface_ref.module, expected["module"])
        self.assertEqual(envelope.interface_ref.qualname, expected["qualname"])
        self.assertEqual(envelope.state_advance, errors.StateAdvance.NONE)

    def test_frozen_fixture_identity(self) -> None:
        self.assertEqual(len(self.raw), 2244)
        self.assertEqual(
            hashlib.sha256(self.raw).hexdigest(),
            "cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d",
        )
        self.assertEqual(
            self.raw,
            json.dumps(
                self.document,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n",
        )
        self.assertEqual(tuple(self.cases), ("DC1", "DC2", "DC3", "DC4", "DC5", "DC6"))

    def test_i7v_021_through_i7v_026_exact_successes(self) -> None:
        real_owner = dynamic.validate_dynamic_static_identity
        for index, case_id in enumerate(self.cases, start=21):
            with self.subTest(vector_id=f"I7V-{index:03d}"), patch.object(
                dynamic,
                "validate_dynamic_static_identity",
                wraps=real_owner,
            ) as owner:
                capability = self._issue(case_id)
                result = dynamic.validate_dynamic_static_identity(
                    self._case_bytes(self.cases[case_id]), capability
                )
                self.assertIsNone(result)
                self.assertEqual(owner.call_count, 1)
                self.assertNotIn(
                    id(capability), capabilities._ISSUED_T2_CAPABILITY_IDS
                )

    def test_i7v_060_identity_projection_mismatch(self) -> None:
        case = copy.deepcopy(self.cases["DC2"])
        case["expected"]["total_closing_queue"] = 3
        capability = self._issue("DC2")
        real_owner = dynamic.validate_dynamic_static_identity
        with patch.object(
            dynamic, "validate_dynamic_static_identity", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-060",
                lambda: dynamic.validate_dynamic_static_identity(
                    self._case_bytes(case), capability
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_061_capacity_identity_failure(self) -> None:
        case = copy.deepcopy(self.cases["DC1"])
        case["inputs"]["capacities"][0] = 1
        capability = self._issue("DC1")
        real_owner = dynamic.validate_dynamic_static_identity
        with patch.object(
            dynamic, "validate_dynamic_static_identity", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-061",
                lambda: dynamic.validate_dynamic_static_identity(
                    self._case_bytes(case), capability
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_062_capacity_compliance_failure(self) -> None:
        case = copy.deepcopy(self.cases["DC1"])
        case["inputs"]["accepted"][0] = 4
        capability = self._issue("DC1")
        real_owner = dynamic.validate_dynamic_static_identity
        with patch.object(
            dynamic, "validate_dynamic_static_identity", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-062",
                lambda: dynamic.validate_dynamic_static_identity(
                    self._case_bytes(case), capability
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_063_queue_balance_failure(self) -> None:
        case = copy.deepcopy(self.cases["DC6"])
        case["expected"]["coordinated_closing_queue"] = 1
        capability = self._issue("DC6")
        real_owner = dynamic.validate_dynamic_static_identity
        with patch.object(
            dynamic, "validate_dynamic_static_identity", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-063",
                lambda: dynamic.validate_dynamic_static_identity(
                    self._case_bytes(case), capability
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_064_delay_decomposition_failure(self) -> None:
        case = copy.deepcopy(self.cases["DC3"])
        case["expected"]["arrival_epochs"][1] = 4
        capability = self._issue("DC3")
        real_owner = dynamic.validate_dynamic_static_identity
        with patch.object(
            dynamic, "validate_dynamic_static_identity", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-064",
                lambda: dynamic.validate_dynamic_static_identity(
                    self._case_bytes(case), capability
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_065_exact_issuer_wrong_hash(self) -> None:
        wrong_hash = SourceFileRawSha256("sha256-raw:" + "0" * 64)
        real_owner = capabilities._issue_t2_fixture_capability
        with patch.object(
            capabilities, "_issue_t2_fixture_capability", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-065",
                lambda: capabilities._issue_t2_fixture_capability(
                    fixture_path=FIXTURE_PATH,
                    fixture_raw_sha256=wrong_hash,
                    case_id="DC1",
                    authorized_interface=INTERFACE,
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_066_exact_issuer_unallowlisted_pair(self) -> None:
        real_owner = capabilities._issue_t2_fixture_capability
        with patch.object(
            capabilities, "_issue_t2_fixture_capability", wraps=real_owner
        ) as owner:
            self._assert_failure(
                "I7V-066",
                lambda: capabilities._issue_t2_fixture_capability(
                    fixture_path=FIXTURE_PATH,
                    fixture_raw_sha256=FIXTURE_HASH,
                    case_id="M1",
                    authorized_interface=INTERFACE,
                ),
            )
            self.assertEqual(owner.call_count, 1)


if __name__ == "__main__":
    unittest.main()
