# EBU

A research framework for economic cells, resource actions and transferable EBU.

Start with the three books:

1. [EBU Economic Cells](docs/books/EBU_ECONOMIC_CELLS.md)
2. [EBU Between Economic Cells](docs/books/EBU_BETWEEN_ECONOMIC_CELLS.md)
3. [EBU Real Limits](docs/books/EBU_REAL_LIMITS.md)

[The current model](docs/CURRENT_MODEL.md) states the equations and assumptions to implement. [Open questions](docs/OPEN_QUESTIONS.md) records the choices still requiring a defined model. [Implementation requirements](docs/IMPLEMENTATION_REQUIREMENTS.md) identifies the first modules and mathematical checks.

The repository is prepared for a new implementation. The source and test directories currently contain their requirements; a runnable framework has not yet been built.

## Scope

The working model uses independent quadratic cell fields. Actors choose resource actions; EBU evaluates their identified contributions. Existing EBU can circulate between actors.

Cell design stays fixed during ordinary resource actions. Division, combination and redesign are separate operations. Handling limits and whole resource units are explicit application inputs.

The mathematics is conditional on the declared field and action model. Physical calibration, lifecycle rules and beneficial long-run behaviour remain research questions.

## Earlier work

The previous repository contents remain in Git history and a separate local backup. Earlier result files retain their original scientific scope. They are not results for this new framework.

[Migration provenance](docs/provenance/MIGRATION.md) explains the restart and recovery. Copied book editions use local links; their original source hashes are recorded in [sources.json](docs/provenance/sources.json).
