"""Exact-number handling and the fixed denomination (core Step 1).

Expected values are written independently of the implementation: either as
literal fractions or from the exact SI defining constants h and nu_Cs.
"""

import unittest
from decimal import Decimal
from fractions import Fraction

from ebu_core.exact import W_CS, W_CS_TEXT, to_exact


class DenominationTests(unittest.TestCase):
    def test_text_is_the_specified_literal(self):
        self.assertEqual(W_CS_TEXT, "6.091102297113866550e-24")

    def test_value_is_the_exact_fraction(self):
        self.assertIs(type(W_CS), Fraction)
        self.assertEqual(W_CS, Fraction(6091102297113866550, 10**42))

    def test_equals_planck_constant_times_cesium_frequency(self):
        # Independent check: both are exact SI defining constants.
        h = Fraction(662607015, 10**42)  # 6.62607015e-34 J s
        nu_cs = 9192631770  # Hz
        self.assertEqual(W_CS, h * nu_cs)

    def test_a_float_route_would_not_be_exact(self):
        # W's reduced denominator contains factors of 5, so no binary float
        # can equal it. This is why floats are rejected as inputs.
        self.assertNotEqual(Fraction(float(W_CS_TEXT)), W_CS)


class AcceptedInputTests(unittest.TestCase):
    CASES = [
        (20, Fraction(20)),
        (-7, Fraction(-7)),
        (0, Fraction(0)),
        (Fraction(1, 100), Fraction(1, 100)),
        ("20", Fraction(20)),
        ("-0.5", Fraction(-1, 2)),
        ("+3", Fraction(3)),
        (".5", Fraction(1, 2)),
        ("5.", Fraction(5)),
        ("0.01", Fraction(1, 100)),
        ("1e-2", Fraction(1, 100)),
        ("1E-2", Fraction(1, 100)),
        ("2E+3", Fraction(2000)),
        ("1/100", Fraction(1, 100)),
        ("-4/5", Fraction(-4, 5)),
        ("+4/5", Fraction(4, 5)),
        ("6/4", Fraction(3, 2)),
        ("0/7", Fraction(0)),
        ("-0", Fraction(0)),
    ]

    def test_accepted_inputs_become_exact_fractions(self):
        for given, expected in self.CASES:
            with self.subTest(given=given):
                result = to_exact(given)
                self.assertIs(type(result), Fraction)
                self.assertEqual(result, expected)

    def test_fraction_subclass_is_normalised_to_plain_fraction(self):
        class TaggedFraction(Fraction):
            pass

        result = to_exact(TaggedFraction(3, 4))
        self.assertIs(type(result), Fraction)
        self.assertEqual(result, Fraction(3, 4))


class RejectedInputTests(unittest.TestCase):
    WRONG_TYPES = [
        True,
        False,
        0.5,
        1.0,
        float("nan"),
        float("inf"),
        float("-inf"),
        Decimal("0.5"),
        Decimal("NaN"),
        1 + 0j,
        None,
        [1],
        b"1",
        object(),
    ]

    MALFORMED_TEXT = [
        "",
        " ",
        " 1",
        "1 ",
        "1\n",
        "nan",
        "NaN",
        "inf",
        "-inf",
        "Infinity",
        "1/",
        "/2",
        "1//2",
        "1/2/3",
        "1.5/2",
        "1/-2",
        "1/+2",
        "1/2e3",
        "abc",
        "1e",
        "e5",
        "1e2.5",
        ".",
        "-",
        "--1",
        "1_000",
        "0x10",
        "1,5",
        "١٢",  # Arabic-Indic digits: Fraction() alone would accept these
        "１",  # fullwidth digit one
    ]

    def test_wrong_kinds_of_value_raise_type_error(self):
        for given in self.WRONG_TYPES:
            with self.subTest(given=given):
                with self.assertRaises(TypeError):
                    to_exact(given)

    def test_malformed_or_nonfinite_text_raises_value_error(self):
        for given in self.MALFORMED_TEXT:
            with self.subTest(given=given):
                with self.assertRaises(ValueError):
                    to_exact(given)

    def test_zero_denominator_is_rejected(self):
        for given in ["1/0", "0/0", "-3/000"]:
            with self.subTest(given=given):
                with self.assertRaisesRegex(ValueError, "zero denominator"):
                    to_exact(given)

    def test_error_message_names_the_argument(self):
        with self.assertRaisesRegex(TypeError, "^K:"):
            to_exact(0.01, "K")
        with self.assertRaisesRegex(ValueError, "^x_star:"):
            to_exact("nan", "x_star")


if __name__ == "__main__":
    unittest.main()
