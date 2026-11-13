# Tests

Begin with the mathematical invariant checks in [implementation requirements](../docs/IMPLEMENTATION_REQUIREMENTS.md). Add experimental runners only after their model and comparison are specified.

## Step 1 checks

- `test_exact.py`: the exact denomination (including `W_CS == h * nu_Cs`), accepted exact inputs, and rejection of floats, booleans, nonfinite values, malformed text and zero denominators.
- `test_cells.py`: the owner's one-cell table (`x_star = 100`, `K = 1/100`, `x` = 20, 100, 180, 0), an empty cell keeping its field, a hand-worked rational case, `Phi = c m^2 / 2`, rejection of `K <= 0` and bad inputs, and immutability.

Expected values are worked by hand, not recomputed by the code under test.

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```
