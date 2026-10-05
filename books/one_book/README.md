# What an Economy Must Keep Alive — continuous Book 1

This editable author-review edition rewrites the author's 160-page **Book
writer** manuscript throughout. Its 49 chapters and five appendices connect
all cleared theory needed for the EBU architecture, retaining the original
explanatory tone, physical examples, trim and body typography. The final
integration is a continuous argument, not a collection of appended reports.

Book 1 owns definitions, essential proofs, derivations, counterexamples,
conceptual examples and accounting/social implications. Later books own
implementation, experimental design, simulations, validation campaigns,
results and application-specific calibration. There is no fixed page target
or ceiling; any later split should preserve the argument.

## Build and outputs

From the repository root:

```sh
python3 books/one_book/build_book.py
```

The unchanged builder uses cached Tectonic resources in deterministic mode.
It writes `output/pdf/EBU_What_an_Economy_Must_Keep_Alive.pdf`; local diagnostics
stay in the ignored `books/one_book/build/` directory. The master is `book.tex`.
No EBU scientific module is imported or executed. The detailed linked contents
lists chapters, numbered sections, appendices, glossary and references.

The six integration diagrams are committed under `figures/`:
`recursion`, `interaction_origins`, `continuity_chain`, `generator_bridge`,
`feedback_memory` and `modes_and_interaction`. Their deterministic ReportLab
source is `integration_figures.py`. They are static teaching schematics,
not plots of simulated or measured data. Eleven inherited diagrams remain
unchanged. An ordinary book build does not regenerate figures.

## Reading route

| Chapters | Role |
| --- | --- |
| 1–13 | Motivation, state and boundary, reference, potential and directional field |
| 14–24 | Paths, finite change, permission, locality, sequential history and joint value |
| 25–30 | Coalition tables, Möbius recursion, discrete and continuous Taylor, degree ceilings |
| 31–35 | Motion, generators, feedback, memory, oscillation and composite response |
| 36–42 | Topology, canonical calibration, probability, entropy, field change, uncertainty and continuity |
| 43–49 | Attribution, routes, institutions, theoretical interfaces, system synthesis and social meaning |
| A–E | Calculus, partition chain rule, dynamic proofs, probability scope and worked comparisons |

Chapter 48 includes the monetary-accounting comparison, prospective public
uses, registration architecture and institutional boundaries. Chapter 49
separates established mathematics, EBU synthesis and the open physical/social
programme. Chapter introductions and endings carry the developing question
through the existing framework.

## Provenance and status

`BASE_EDITION_MANIFEST.json` identifies the exact 48-file source edition.
The older books, original PDFs and the source worktree remain unchanged.
The import is a subject-level integration, not a sentence-by-sentence archival
merger. `EBU_FUTURE_BOOKS_STRUCTURE.md` assigns the complete theoretical
foundation to Book 1 while preserving historical numbering and later volumes.

The root report `EBU_BOOK_1_COMBINED_THEORETICAL_INTEGRATION_REPORT.md` records
the chapter-by-chapter continuity map, theoretical and practical coverage,
input identities, changes and build checks. It also identifies the content
commit. The final report commit is recorded in the delivery message because
a file cannot contain the hash of its own commit.

The frozen foundation and working baseline retain precedence. The R-stage,
S-MG and feedback inputs have the independent clearance supplied in the
author's brief; this new manuscript still requires its separate independent
book audit. Proved theory is stated within its hypotheses. The physical and
institutional applications are prospective where appropriate. Build and
editorial checks do not substitute for that independent audit.

No experiment, scientific random stream, trajectory, campaign or optical-trap
run is part of this task. E1a execution remains unauthorized. No push is made.
