# EBU

A research framework for economic cells, resource actions and transferable EBU.

Start with the three books:

1. [EBU Economic Cells](docs/books/EBU_ECONOMIC_CELLS.md)
2. [EBU Between Economic Cells](docs/books/EBU_BETWEEN_ECONOMIC_CELLS.md)
3. [EBU Real Limits](docs/books/EBU_REAL_LIMITS.md)

[The current model](docs/CURRENT_MODEL.md) states the equations and assumptions to implement. [Open questions](docs/OPEN_QUESTIONS.md) records the choices still requiring a defined model. [Implementation requirements](docs/IMPLEMENTATION_REQUIREMENTS.md) identifies the first modules and mathematical checks.

## Status: core Step 1

`src/ebu_core` is an exact calculator for **one economic cell**. Given its resource amount `x` (J), reference `x_star` (J) and stiffness `K` (1/J), it returns the imbalance field `Phi = K (x - x_star)^2 / 2` (J), the slope `m = K (x - x_star)` and the inverse stiffness `c = 1/K` (J). All values are exact `fractions.Fraction`s; floats are rejected. The fixed denomination `W_CS = 6.091102297113866550e-24` J per EBU is defined exactly but not yet used.

```python
from ebu_core import make_cell, evaluate_cell

cell = make_cell(cell_id="A", resource_key="usable-electrical-J", x=20, x_star=100, K="1/100")
result = evaluate_cell(cell)
# result.phi == 32, result.m == Fraction(-4, 5), result.c == 100
```

Run the tests (standard library only, no dependencies):

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Resource actions, EBU contributions, attribution, split/merge and accounts are not implemented yet.

## Scope

The working model uses independent quadratic cell fields. Actors choose resource actions; EBU evaluates their identified contributions. Existing EBU can circulate between actors.

Cell design stays fixed during ordinary resource actions. Division, combination and redesign are separate operations. Handling limits and whole resource units are explicit application inputs.

The mathematics is conditional on the declared field and action model. Physical calibration, lifecycle rules and beneficial long-run behaviour remain research questions.

## Earlier work

The previous repository contents remain in Git history and a separate local backup. Earlier result files retain their original scientific scope. They are not results for this new framework.

[Migration provenance](docs/provenance/MIGRATION.md) explains the restart and recovery. Copied book editions use local links; their original source hashes are recorded in [sources.json](docs/provenance/sources.json).
