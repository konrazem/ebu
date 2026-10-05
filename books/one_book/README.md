# What an Economy Must Keep Alive — continuous Book 1

This editable edition extends the author's 160-page one-volume manuscript
from the **Book writer** chat. It contains 49 chapters and five technical
appendices. The opening voice, physical examples, trim and body typography
are retained; the cleared path, coalition, Möbius, generator, probability and
entropy hierarchy is developed through the middle of the book.

## Build and outputs

From the repository root, run:

```sh
python3 books/one_book/build_book.py
```

The unchanged existing builder uses cached Tectonic resources and deterministic
mode. It writes `output/pdf/EBU_What_an_Economy_Must_Keep_Alive.pdf` and keeps
local diagnostics in `books/one_book/build/`. The LaTeX master is `book.tex`.
No EBU scientific module is imported or executed. The contents lists chapters,
numbered sections and appendices, with linked destinations and page numbers.

The three new vector teaching diagrams are committed under `figures/`.
`integration_figures.py` regenerates them with ReportLab from the existing
book-artifact environment; it draws fixed schematics, not simulation data.
The 11 inherited diagrams are retained from the identified source edition.
No figure regeneration is needed for an ordinary book build.

## Reading route and source map

| Chapters | Role |
| --- | --- |
| 1–13 | Motivation, state, equilibrium, declared potential and local field |
| 14–24 | Paths, finite change, permission, locality, sequential closure and joint value |
| 25–32 | Coalition tables, Möbius recursion, discrete and continuous Taylor, degree and nonlinear response |
| 33–39 | Dynamics, generators, topology, canonical density, probability and P4 entropy |
| 40–42 | Field change, uncertainty and the central continuity hierarchy |
| 43–49 | Attribution, routes, conditional institutions, implementation, future studies and evidence limits |
| Appendices A–E | Calculus, the partition chain rule, generator proofs, thermodynamic scope and a worked review |

The integration report at the repository root records chapter-level provenance,
validation, input identities and the relationship to the earlier Part II.
`BASE_EDITION_MANIFEST.json` records the exact imported source edition.

The older separate books, original PDFs and the source worktree are untouched.
The old historical facsimiles and eight practice studios are not reproduced.
This is substantive integration, not a sentence-by-sentence archival merger.
The existing eight-part future-book map is preserved; this author-selected
one-volume deliverable does not renumber the later programme.

## Scientific status

The frozen physical foundation and working theory baseline retain precedence.
The governing finite identity is `E = V(pre) - V(post)` for a complete declared
transition under a fixed field. A generator supplies endpoints; it is not a
prerequisite for finite valuation. Probability and entropy representations
require their additional stated assumptions. Actor attribution, economic
benefit and institutional rules remain conditional and separate.

This is an author-review manuscript. A successful build and editorial checks
do not constitute the required independent book audit or experimental
validation. E1a execution remains unauthorised. No scientific random stream,
model trajectory, campaign or physical experiment is run by this book build.
