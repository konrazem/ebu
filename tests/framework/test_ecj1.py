"""V0 T0 checks for ECJ-1 and pinned Unicode 15.0.0 normalization."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ebu_framework.canonical import (
    DERIVED_NORMALIZATION_PROPS_SHA256,
    UNICODE_DATA_SHA256,
    _DERIVED_NORMALIZATION_PROPS_FILE,
    _UNICODE_DATA_FILE,
    _load_unicode_tables_from_paths,
    _normalize_nfc,
    encode_ecj1,
    parse_ecj1,
)
from ebu_framework.errors import FailureCode, FrameworkError
from safety import assert_safe_test_module, forbidden_import_guard


_HERE = Path(__file__).resolve().parent
_FIXTURES = _HERE / "fixtures"
_VECTORS = json.loads((_FIXTURES / "ecj1_vectors.json").read_text("utf-8"))
_NORMALIZATION_TEST = (
    _FIXTURES / "unicode" / "15.0.0" / "NormalizationTest.txt"
)


def _sequence(value: str) -> str:
    return "".join(chr(int(item, 16)) for item in value.split()) if value else ""


class ECJ1Tests(unittest.TestCase):
    check_count = 0

    def checked_equal(self, left, right) -> None:
        type(self).check_count += 1
        self.assertEqual(left, right)

    def test_frozen_asset_hashes(self) -> None:
        expected = {
            _UNICODE_DATA_FILE: UNICODE_DATA_SHA256,
            _DERIVED_NORMALIZATION_PROPS_FILE: DERIVED_NORMALIZATION_PROPS_SHA256,
            _NORMALIZATION_TEST: "fb9ac8cc154a80cad6caac9897af55a4e75176af6f4e2bb6edc2bf8b1d57f326",
        }
        for path, digest in expected.items():
            with self.subTest(path=path.name):
                self.checked_equal(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_valid_exact_vectors_and_strict_round_trip(self) -> None:
        with forbidden_import_guard():
            for vector in _VECTORS["valid"]:
                with self.subTest(vector=vector["id"]):
                    expected = bytes.fromhex(vector["canonical_hex"])
                    encoded = bytes(encode_ecj1(vector["value"]))
                    self.checked_equal(encoded, expected)
                    self.checked_equal(parse_ecj1(encoded), parse_ecj1(expected))
                    self.checked_equal(bytes(encode_ecj1(parse_ecj1(expected))), expected)

    def test_strict_parse_rejections(self) -> None:
        for vector in _VECTORS["invalid_parse"]:
            with self.subTest(vector=vector["id"]):
                with self.assertRaises(FrameworkError) as caught:
                    parse_ecj1(bytes.fromhex(vector["input_hex"]))
                self.checked_equal(
                    caught.exception.envelope.failure_code.value,
                    vector["failure_code"],
                )

    def test_encoder_type_cycle_and_normalized_key_rejections(self) -> None:
        cycle: list[object] = []
        cycle.append(cycle)
        cases = {
            "float": (1.0, FailureCode.FLOAT_FORBIDDEN),
            "tuple": ((1,), FailureCode.ECJ1_TYPE_UNSUPPORTED),
            "bytes": (b"x", FailureCode.ECJ1_TYPE_UNSUPPORTED),
            "cycle": (cycle, FailureCode.CYCLIC_OBJECT_GRAPH),
            "nfc-duplicate-name": (
                {"é": 1, "e\u0301": 2},
                FailureCode.DUPLICATE_OBJECT_NAME,
            ),
        }
        for vector in _VECTORS["invalid_encode"]:
            value, expected = cases[vector["id"]]
            with self.subTest(vector=vector["id"]):
                with self.assertRaises(FrameworkError) as caught:
                    encode_ecj1(value)
                self.checked_equal(caught.exception.envelope.failure_code, expected)

    def test_complete_unicode_15_normalization_corpus(self) -> None:
        corpus_cases = 0
        for raw_line in _NORMALIZATION_TEST.read_text("utf-8").splitlines():
            body = raw_line.split("#", 1)[0].strip()
            if not body or body.startswith("@"):
                continue
            columns = [item.strip() for item in body.split(";")]
            self.assertGreaterEqual(len(columns), 5)
            c1, c2, c3, c4, c5 = map(_sequence, columns[:5])
            expected = (
                (c1, c2),
                (c2, c2),
                (c3, c2),
                (c4, c4),
                (c5, c4),
            )
            for source, target in expected:
                self.checked_equal(_normalize_nfc(source), target)
            corpus_cases += 1
        self.assertGreater(corpus_cases, 0)
        type(self).check_count += 1

    def test_unicode_version_boundaries(self) -> None:
        self.checked_equal(_normalize_nfc("\U000323af"), "\U000323af")
        with self.assertRaises(FrameworkError) as caught:
            _normalize_nfc("\U0002ebf0")
        self.checked_equal(
            caught.exception.envelope.failure_code,
            FailureCode.UNASSIGNED_UNICODE_SCALAR,
        )

    def test_missing_and_corrupt_assets_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-i1-unicode-") as directory:
            root = Path(directory)
            good_unicode = root / "UnicodeData.txt"
            good_props = root / "DerivedNormalizationProps.txt"
            good_unicode.write_bytes(_UNICODE_DATA_FILE.read_bytes())
            good_props.write_bytes(_DERIVED_NORMALIZATION_PROPS_FILE.read_bytes())
            good_unicode.write_bytes(good_unicode.read_bytes() + b"corrupt")
            with self.assertRaises(FrameworkError) as caught:
                _load_unicode_tables_from_paths(good_unicode, good_props)
            self.checked_equal(
                caught.exception.envelope.failure_code,
                FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
            )
            with self.assertRaises(FrameworkError) as caught:
                _load_unicode_tables_from_paths(root / "missing.txt", good_props)
            self.checked_equal(
                caught.exception.envelope.failure_code,
                FailureCode.UNICODE_DATA_INTEGRITY_FAILURE,
            )

    def test_no_host_or_network_text_database_reachability(self) -> None:
        source_path = Path(__import__("ebu_framework.canonical").canonical.__file__)
        tree = ast.parse(source_path.read_text("utf-8"), filename=str(source_path))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        forbidden = {"unicodedata", "icu", "locale", "socket", "urllib", "requests"}
        self.checked_equal(imports.intersection(forbidden), set())
        self.assertGreater(assert_safe_test_module(Path(__file__)), 0)
        type(self).check_count += 1

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"V0_COMPLETED_CHECKS={cls.check_count}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
