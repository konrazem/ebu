# Book I introductory edition: verification and completion report

## Delivered result

**Complete candidate for author review:** *Why EBU? Life, Balance, and the Accounting of Physical Action*. The PDF has 69 pages: four front-matter pages and numbered pages 1-65. It contains all 18 requested chapters, six labelled explanatory figures, 17 worked exercises, a glossary, symbol table and linked bibliography. The rendered extraction contains approximately 20,148 whitespace-delimited words, including navigation, references and mathematical fragments; this is a descriptive count, not a length target.

The new LaTeX manuscript follows the motivation-to-equation progression. It teaches the declared lossless homogeneous-resource Gaussian world, exact finite changes, affected support, simultaneous groups, common-path accounting and scoped sequence identities. Biological analogy, physical inventory, monetary claims, actor choice and institutional permissions remain distinct. No executed Gaussian evidence is claimed.

## Repository and authorisation

- Starting and final branch: `codex/local-gaussian-reconciliation`.
- Starting SHA: `05f3cb02d0c48e60de98342edfac9c36f2cecc6f`.
- Final SHA: `05f3cb02d0c48e60de98342edfac9c36f2cecc6f`.
- The handover tree was clean before authoring. The final tree has only this new untracked edition directory; every previously tracked file and the index remain unchanged.
- A read-only live remote query at the start found no matching branch on origin; the local branch has no upstream. There is no intended remote update for this task. The initial sandbox DNS failure was followed by a successful approved read-only query.
- No branch switch, staging, commit, push, merge or publication occurred.
- The direct author request supersedes the previous stage's stop-before-generation boundary only for Book I authoring, reference research, static mathematical checking and candidate rendering. Later stages remain unauthorised.

## Preservation and documentary provenance

All twelve locked repository documents were rehashed successfully. All three original PDFs were rehashed and their page counts checked after the book work:

| Preserved artifact | Pages | SHA-256 |
|---|---:|---|
| `EBP_Book_Part_III_Unified_Explanatory_Edition.pdf` | 153 | `0ab9b352c0464c8a15bd603845c8f8aa3d71b06d470e12ea1b5e393cef154019` |
| `EBP_Book_Part_II_Unified_Explanatory_Edition.pdf` | 160 | `c36e3fad562455808775a3470b8c270faf089b2843dbe17b03635a31e1179095` |
| `EBP_Book_Part_I_Unified_Explanatory_Edition.pdf` | 296 | `335ed5c6d3541d48a61438e213a8a1148eb196649da83392a4ba0741ce65a4ad` |

Their original directory is `/Users/konrad.grzyb/Documents/EBU/v4/`. None was overwritten, regenerated or moved. Parts II and III remain byte-identical. The baseline first volume was used as a preserved content source, not misrepresented as recovered editable source.

The disposition ledger covers every one of its 533 ordered outline entries: 286 rewritten, 103 condensed, 120 relocated in teaching responsibility, 10 retained and rewritten, and 14 omitted from the new introductory progression. Parent chapter entries cover unbookmarked intervening prose. “Relocated” does not mean that any content was inserted into a later PDF. The inventory was compared in order with the baseline PDF bookmarks. This is a section-level editorial disposition, not a line-by-line scientific audit of all 296 historical pages.

## Verification completed

- Read the applicable repository guidance, eight handover/reconciliation sources and relevant exact mathematical passages. The source/claim ledger records narrower theorem scopes and the unresolved historical dissipation boundary.
- Verified selected factual statements against primary institutional sources or author/publisher records. IPCC observation and scenario figures retain their periods, units and uncertainty. The final published IPBES SPM replaced an initial advance-version copy for the citation and method check. Unresolved competing hunger headlines were omitted; no unsupported quantity was retained.
- Checked the complete manuscript for narrative progression, recurring examples, notation, units, sign conventions, institutional separation, simultaneous-action scope and prospective/observed distinctions.
- Completed 86 exact rational-arithmetic and coefficient checks. These evaluate individual declared states and expressions; they do not advance a scientific model. General derivations and limits are recorded in `mathematical_review.md`.
- Completed the structural/provenance checks listed individually in `review/edition_checks.json`: source hashes, all original PDFs, full baseline inventory, 18 complete chapters, unique labels, resolved citations/cross-references, six existing figures, page numbering, no blank pages, no unresolved-reference/replacement glyphs and all extracted characters inside page bounds.
- The accepted Tectonic log contains no underfull/overfull boxes, missing-character diagnostics, unresolved references or compilation warnings/errors. Initial cache-only attempts failed when standard fonts were absent; the fonts were retrieved, and subsequent builds completed. Failed attempts were not counted as verification passes.
- Inspected every rendered page. After the full 69-page visual pass, seven revised pages were reinspected and the other 62 final PNGs matched the inspected images byte for byte. See `review/visual_review.md` and its per-page JSON hashes. Final rasterisation completed without diagnostics.
- Rebuilt offline with identical declared inputs. The book PDF and all six figure PDFs were byte-identical. `review/reproducibility.json` records both candidate digests.
- Inspected the new source changes and ran `git diff --check`; separately checked new text files with `git diff --no-index --check` because unstaged untracked files are absent from ordinary Git diffs. Final check details are in the manifest.

Candidate PDF SHA-256: `1ef1a48b40e92dd5e3690c0997b083ae4022b512f13c267c2f9135a1ad57c3f6`.

## Exact changed files and purpose

Every path below is new, under `books/book_i_introductory_edition/`. There are no modifications or deletions of pre-existing repository files. The manifest supplies each file's full SHA-256, excluding only its own self-hash. Ignored working files are described separately below.

| New relative path | Purpose |
|---|---|
| `.gitignore` | Keep local build and raster intermediates out of version control. |
| `BUILD.md` | Tool versions, commands and reproduction boundaries. |
| `README.md` | Reader entry point, scope and deliverable map. |
| `VERIFICATION_REPORT.md` | This stage-completion report and exact changed-file inventory. |
| `baseline_section_inventory.json` | All 533 ordered baseline bookmarks with dispositions. |
| `book.tex` | Front matter, layout, macros and manuscript assembly. |
| `build.py` | Deterministic book-only build and atomic candidate replacement. |
| `build_manifest.json` | Delivered-file digests, toolchain and source-review provenance. |
| `claim_source_ledger.md` | Selected factual claims and mathematical source/assumption locks. |
| `content_disposition.md` | Human-readable old-to-new section ledger. |
| `figures/finite_value.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures/group.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures/quadratic.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures/regulation.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures/transfer.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures/two_records.pdf` | Generated vector schematic or static formula illustration; no trajectory. |
| `figures.py` | Editable deterministic drawing source for all six figures. |
| `manuscript/01.tex` | Complete chapter 1 of the new introductory manuscript. |
| `manuscript/02.tex` | Complete chapter 2 of the new introductory manuscript. |
| `manuscript/03.tex` | Complete chapter 3 of the new introductory manuscript. |
| `manuscript/04.tex` | Complete chapter 4 of the new introductory manuscript. |
| `manuscript/05.tex` | Complete chapter 5 of the new introductory manuscript. |
| `manuscript/06.tex` | Complete chapter 6 of the new introductory manuscript. |
| `manuscript/07.tex` | Complete chapter 7 of the new introductory manuscript. |
| `manuscript/08.tex` | Complete chapter 8 of the new introductory manuscript. |
| `manuscript/09.tex` | Complete chapter 9 of the new introductory manuscript. |
| `manuscript/10.tex` | Complete chapter 10 of the new introductory manuscript. |
| `manuscript/11.tex` | Complete chapter 11 of the new introductory manuscript. |
| `manuscript/12.tex` | Complete chapter 12 of the new introductory manuscript. |
| `manuscript/13.tex` | Complete chapter 13 of the new introductory manuscript. |
| `manuscript/14.tex` | Complete chapter 14 of the new introductory manuscript. |
| `manuscript/15.tex` | Complete chapter 15 of the new introductory manuscript. |
| `manuscript/16.tex` | Complete chapter 16 of the new introductory manuscript. |
| `manuscript/17.tex` | Complete chapter 17 of the new introductory manuscript. |
| `manuscript/18.tex` | Complete chapter 18 of the new introductory manuscript. |
| `manuscript/bibliography.tex` | Linked bibliography and editorial provenance note. |
| `manuscript/glossary.tex` | Glossary and symbol table. |
| `mathematical_review.md` | Derivations, dimensional checks and scientific limits. |
| `render_review.py` | Immutable PDF snapshot and isolated page rendering. |
| `requirements.txt` | Pinned authoring and document-inspection Python packages. |
| `review/edition_checks.json` | Completed structural, provenance and scope checks. |
| `review/mathematics_checks.json` | All 86 exact fixed-state/coefficient checks. |
| `review/reproducibility.json` | Byte-identical offline book and figure rebuild comparison. |
| `review/visual_review.json` | Per-page image hashes and visual-review findings. |
| `review/visual_review.md` | Complete readable page-by-page visual review. |
| `source_locks.json` | Starting repository, governing sources and preserved PDF identities. |
| `verify_edition.py` | Read-only checks of provenance, references, PDF structure and scope. |
| `verify_mathematics.py` | Exact arithmetic on separately declared illustrative states. |
| `why_ebu_book_i_candidate.pdf` | Complete 69-page candidate book for author review. |

Ignored working material stays within this edition: `build/` contains source PDF research copies, TeX intermediates, authoring/verification helper records, immutable visual snapshots and logs; `review/pages/` contains regenerated PNGs for visual QA. These are not historical result artifacts or required scientific inputs. They are not proposed for version control. No source PDF was copied over its original.

## Limitations and unresolved questions

- This is a candidate, not author acceptance, independent specialist peer review, publication, a print-production proof or PDF/UA certification.
- Some factual statements deliberately use an official overview, publisher abstract or official indexed passage rather than claiming a complete report audit; the exact scope is explicit in the claim ledger and bibliography. No external dataset was reanalysed. The evidence is dated and is not described as a live 2026 dashboard.
- The bibliography and ledger identify online sources; external publications are not repackaged as part of the deliverable. Toolchain and input locks support reproduction, but identical bytes on a different renderer or future TeX bundle are not claimed.
- Scientific questions remain open: reference/scale calibration, adequacy of represented state, measurement uncertainty, the lossy-process valuation boundary, a physical action-time model, ownership, permissions, affordability and actual recovery or institutional usefulness. These are preserved as boundaries, not resolved by exposition.
- Original editable sources for the preserved trilogy have not been recovered. This new edition makes no such provenance claim.

## Next boundary

The next possible stage is author review of this complete Book I candidate, followed by separately authorised editorial revisions or specialist review. Author acceptance, later-volume modification, experimental design/implementation/execution and publication have not begun.

**No scientific model execution. No experimental implementation. No AWS. No modification of historical results.**
