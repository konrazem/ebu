# Source

The new implementation belongs here. Its first scope is specified in [implementation requirements](../docs/IMPLEMENTATION_REQUIREMENTS.md).

## `ebu_core` — Step 1: one cell

| Module | Contents |
|---|---|
| `exact.py` | `to_exact()` turns ints (not bools), `Fraction`s and strict ASCII decimal, scientific or `a/b` text into exact `Fraction`s, and rejects floats, nonfinite values and malformed text. Defines `W_CS` exactly from its decimal text. |
| `cells.py` | Immutable `CellDesign` (`cell_id`, `resource_key`, `x_star`, `K > 0`) and `Cell` (design plus `x`); `make_cell()`; `imbalance_field()`, `slope()`, `inverse_stiffness()` and `evaluate_cell()`. |
| `__init__.py` | Public exports. |

No physical-feasibility, capacity, lifecycle or resource-compatibility rule is applied. `resource_key` is an application's declaration, not proof of interchangeability. Resource actions, contributions and split/merge are later steps.
