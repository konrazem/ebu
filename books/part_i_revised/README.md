# Part I — full-length revised Gaussian explanatory edition

This is the current author-review revision of the supplied 296-page Part I,
not the earlier 69-page introductory candidate. It retains the original
teaching method and visual language while updating the introduction and
potential. The current continuity revision leads into the integrated Part II
and the eight-part forward series. The latest author brief sets a 200-page
minimum per current volume, with descriptive depth rather than padding.
See the integrated edition's review report for current artifact counts.

## Read the book

Final review artifact:
`../../output/pdf/EBP_Book_Part_I_Revised_Gaussian_Explanatory_Edition.pdf`.

There are 32 chapters, including eight worked practice studios, eleven vector
illustrations, a glossary and primary/project references. See
`../../BOOK_I_FULL_LENGTH_REVISION.md` and `EDITORIAL_CONTRACT.md` for the
editorial boundary. This is reconstructed editable source, not a recovered
original manuscript. Original Parts I–III and the short candidate are preserved.

## Build and inspect

Dependencies used: Python 3.12 with ReportLab, pypdf, pdfplumber and Pillow;
Tectonic 0.17; Poppler. No scientific EBU engine is imported. The Python runtime
provided by the desktop workspace contains the required packages. Tectonic's
binary path is explicit in `build_book.py`; adjust that path for another host.

From the repository root:

```sh
python3 books/part_i_revised/figures.py
python3 books/part_i_revised/build_book.py --offline
python3 books/part_i_revised/verify_arithmetic.py
python3 books/part_i_revised/revision_ledger.py
python3 books/part_i_revised/prepare_review.py
```

The offline build uses already cached TeX assets. A different host needs the
corresponding Tectonic bundle/font assets before that command can succeed.
The preparation build downloaded missing typesetting fonts once; subsequent
builds were offline. `SOURCE_DATE_EPOCH` is fixed in the builder, and shell
escape is disabled. Identical results are checked in the recorded environment,
not promised across arbitrary TeX/font versions.

`fontconfig.xml` points to macOS system fonts and a repository-local generated
cache to make Poppler review independent of an unwritable host cache. Adapt its
paths on another host. `prepare_review.py` checks every PDF page and renders all
pages plus overview sheets. The manuscript PDF is not altered by review.

`prepare_baseline.py` is optional: it extracts the original Part I and renders
style controls from the author's supplied absolute path. `revision_ledger.py`
checks the old outline directly against that PDF and checks the prior short
edition's manifest. Its preserved location is therefore required for those
provenance checks, but not for ordinary manuscript rendering.

## Records

- `review/revision_ledger.md`: all 533 original outline entries and their new
  subject-level destinations; no assertion of verbatim retention.
- `review/artifact_checks.json`: rendered extent, PDF identity, chapter starts,
  labels, dimensions, preserved PDF hashes and machine checks.
- `review/VERIFICATION_REPORT.md`: actual visual/arithmetic review coverage,
  limitations and exact changed-file inventory.
- `review/build_manifest.json`: source/artifact hashes for this revision.
- `intro_notes.md`, `core_notes.md`, `studio_notes.md`: scoped source and
  authoring reviews. Their interim counts are not final artifact counts.

Generated build caches and page images are ignored locally. Neither the PDF
nor these successful artifact checks authorizes an experiment, scientific code
implementation, AWS action, publication, commit or push.
