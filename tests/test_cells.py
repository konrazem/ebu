"""One economic cell: field, slope, inverse stiffness, validation, immutability.

Expected values are the owner's Step 1 table (x_star = 100 J, K = 1/100 per J),
worked by hand:

    x = 20:   Phi = (1/100)(-80)^2 / 2 = 32,   m = (1/100)(-80) = -4/5
    x = 100:  Phi = 0,                         m = 0
    x = 180:  Phi = (1/100)(80)^2 / 2 = 32,    m = +4/5
    x = 0:    Phi = (1/100)(-100)^2 / 2 = 50,  m = -1
    c = 1/K = 100 in every row.
"""

import dataclasses
import unittest
from fractions import Fraction

from ebu_core.cells import (
    Cell,
    CellDesign,
    CellEvaluation,
    evaluate_cell,
    imbalance_field,
    inverse_stiffness,
    make_cell,
    slope,
)

F = Fraction

# (x, expected Phi in J, expected m)
TABLE = [
    (20, F(32), F(-4, 5)),
    (100, F(0), F(0)),
    (180, F(32), F(4, 5)),
    (0, F(50), F(-1)),
]


def table_cell(x, *, x_star=100, K="1/100", cell_id="A", resource_key="usable-electrical-J"):
    return make_cell(cell_id=cell_id, resource_key=resource_key, x=x, x_star=x_star, K=K)


class StepOneTableTests(unittest.TestCase):
    def test_table_rows(self):
        for x, phi, m in TABLE:
            with self.subTest(x=x):
                cell = table_cell(x)
                self.assertEqual(imbalance_field(cell), phi)
                self.assertEqual(slope(cell), m)
                self.assertEqual(inverse_stiffness(cell), F(100))

    def test_table_rows_with_other_exact_spellings(self):
        # Same cells written as text and Fractions must give identical results.
        for x, phi, m in TABLE:
            for x_in, x_star_in, k_in in [
                (str(x), "100", F(1, 100)),
                (F(x), F(100), "0.01"),
                (f"{x}/1", "1e2", "1e-2"),
            ]:
                with self.subTest(x=x_in, x_star=x_star_in, K=k_in):
                    cell = table_cell(x_in, x_star=x_star_in, K=k_in)
                    self.assertEqual(imbalance_field(cell), phi)
                    self.assertEqual(slope(cell), m)
                    self.assertEqual(inverse_stiffness(cell), F(100))

    def test_results_are_exact_fractions(self):
        for x, _, _ in TABLE:
            with self.subTest(x=x):
                result = evaluate_cell(table_cell(x))
                self.assertIs(type(result.phi), Fraction)
                self.assertIs(type(result.m), Fraction)
                self.assertIs(type(result.c), Fraction)

    def test_evaluate_cell_returns_all_three_for_that_cell(self):
        cell = table_cell(20)
        result = evaluate_cell(cell)
        self.assertIsInstance(result, CellEvaluation)
        self.assertIs(result.cell, cell)
        self.assertEqual((result.phi, result.m, result.c), (F(32), F(-4, 5), F(100)))

    def test_empty_cell_retains_its_field(self):
        empty = table_cell(0)
        self.assertEqual(empty.x, 0)
        self.assertEqual(imbalance_field(empty), F(50))
        # Still an ordinary cell with its design intact; nothing removed it.
        self.assertEqual(empty.design, CellDesign("A", "usable-electrical-J", 100, "1/100"))

    def test_equal_departures_above_and_below_reference(self):
        below, above = table_cell(20), table_cell(180)
        self.assertEqual(imbalance_field(below), imbalance_field(above))
        self.assertEqual(slope(below), -slope(above))


class AwkwardRationalTests(unittest.TestCase):
    """A non-table case, worked by hand.

    x = 5/2, x_star = -1/3, K = 3/100, so x - x_star = 17/6 and
        Phi = (3/100)(289/36)/2 = 289/2400
        m   = (3/100)(17/6)     = 17/200
        c   = 100/3
    """

    def setUp(self):
        self.cell = make_cell(cell_id="B", resource_key="r", x="2.5", x_star="-1/3", K="3e-2")

    def test_values(self):
        self.assertEqual(imbalance_field(self.cell), F(289, 2400))
        self.assertEqual(slope(self.cell), F(17, 200))
        self.assertEqual(inverse_stiffness(self.cell), F(100, 3))

    def test_field_equals_half_c_times_slope_squared(self):
        # Phi = c m^2 / 2 (EBU Real Limits, chapter 6), checked on every fixture.
        cells = [self.cell] + [table_cell(x) for x, _, _ in TABLE]
        for cell in cells:
            with self.subTest(cell=cell):
                c, m = inverse_stiffness(cell), slope(cell)
                self.assertEqual(imbalance_field(cell), c * m * m / 2)


class ValidationTests(unittest.TestCase):
    def test_nonpositive_stiffness_is_rejected(self):
        for k in [0, "0", "0/5", "-0.0", "-1/100", F(-1, 3)]:
            with self.subTest(K=k):
                with self.assertRaisesRegex(ValueError, "K"):
                    table_cell(20, K=k)

    def test_invalid_numeric_inputs_are_rejected(self):
        type_errors = [dict(x=20.0), dict(x=True), dict(x_star=100.0), dict(x_star=False), dict(K=0.01)]
        for bad in type_errors:
            with self.subTest(**{k: repr(v) for k, v in bad.items()}):
                with self.assertRaises(TypeError):
                    table_cell(**{"x": 20, **bad})
        value_errors = [dict(x="nan"), dict(x_star="inf"), dict(K="1/0"), dict(x="1e")]
        for bad in value_errors:
            with self.subTest(**bad):
                with self.assertRaises(ValueError):
                    table_cell(**{"x": 20, **bad})

    def test_identifiers_must_be_nonempty_unpadded_strings(self):
        for name in ["cell_id", "resource_key"]:
            for bad in ["", "   ", " A", "A ", "A\n"]:
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(ValueError):
                        table_cell(20, **{name: bad})
            for bad in [7, None, b"A"]:
                with self.subTest(field=name, value=bad):
                    with self.assertRaises(TypeError):
                        table_cell(20, **{name: bad})

    def test_cell_requires_a_cell_design(self):
        with self.assertRaises(TypeError):
            Cell(design="A", x=20)

    def test_evaluators_require_a_cell(self):
        design = CellDesign("A", "r", 100, "1/100")
        for fn in [imbalance_field, slope, inverse_stiffness, evaluate_cell]:
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(TypeError):
                    fn(design)

    def test_make_cell_is_keyword_only(self):
        # Prevents silently swapping x and x_star by position.
        with self.assertRaises(TypeError):
            make_cell("A", "r", 20, 100, "1/100")


class ImmutabilityTests(unittest.TestCase):
    def setUp(self):
        self.cell = table_cell(20)

    def test_stored_numbers_are_normalised_fractions(self):
        self.assertIs(type(self.cell.x), Fraction)
        self.assertIs(type(self.cell.design.x_star), Fraction)
        self.assertIs(type(self.cell.design.K), Fraction)
        self.assertEqual(self.cell.K, F(1, 100))
        self.assertEqual(self.cell.x_star, F(100))

    def test_records_cannot_be_modified(self):
        attempts = [
            (self.cell, "x", F(40)),
            (self.cell, "design", CellDesign("A", "r", 0, 1)),
            (self.cell.design, "K", F(1)),
            (self.cell.design, "x_star", F(0)),
            (self.cell.design, "cell_id", "Z"),
            (evaluate_cell(self.cell), "phi", F(0)),
        ]
        for record, name, value in attempts:
            with self.subTest(record=type(record).__name__, field=name):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(record, name, value)

    def test_records_cannot_gain_attributes(self):
        for record in [self.cell, self.cell.design, evaluate_cell(self.cell)]:
            with self.subTest(record=type(record).__name__):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    record.extra = 1

    def test_cell_convenience_properties_are_read_only(self):
        for name in ["cell_id", "resource_key", "x_star", "K"]:
            with self.subTest(property=name):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(self.cell, name, F(1))

    def test_evaluation_leaves_the_cell_unchanged(self):
        before = (self.cell.x, self.cell.design)
        evaluate_cell(self.cell)
        self.assertEqual((self.cell.x, self.cell.design), before)

    def test_equal_records_compare_equal_and_hash_equal(self):
        twin = make_cell(cell_id="A", resource_key="usable-electrical-J", x="20", x_star="100", K=F(1, 100))
        self.assertEqual(self.cell, twin)
        self.assertEqual(hash(self.cell), hash(twin))


if __name__ == "__main__":
    unittest.main()
