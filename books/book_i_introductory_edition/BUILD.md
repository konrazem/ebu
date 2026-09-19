# Build and review the new Book I

This is a new LaTeX authoring system, not the recovered build system of the
preserved trilogy. Work from this directory. The build reads only the new
manuscript and its figure generator. It never imports scientific model code.

## Dependencies

- Python 3.12 (preparation used 3.12.14).
- ReportLab 4.4.9 for six vector figures, including its bundled Bitstream Vera
  regular and bold fonts. The used diagram fonts are embedded in the PDFs.
- Tectonic 0.17.0 for the LaTeX book; Latin Modern text and Computer Modern math.
- pypdf 6.10.0 and pdfplumber 0.11.9 for optional editorial verification.
- Poppler `pdftoppm` for raster review. The preparation environment's exact
  versions and dependency hashes are recorded in `build_manifest.json`.

No additional scientific dependency was introduced. The preparation used the
existing Codex document runtime and installed Tectonic. A fresh machine needs
these authoring tools and Tectonic's standard package/font bundle. The first
build may retrieve standard typesetting files; later builds can use the cache.
Fonts and package files from that bundle are identified in the manifest.

## Commands

From `books/book_i_introductory_edition/`, with the required Python environment
active and Tectonic on PATH:

```sh
python3 build.py
python3 verify_mathematics.py
python3 verify_edition.py
python3 render_review.py
```

For an offline rebuild once Tectonic's bundle files are cached:

```sh
python3 build.py --only-cached
```

Set `BOOK_TECTONIC` to a renderer executable path if needed. In the preparation
environment the complete offline build command from the repository root is:

```sh
BOOK_TECTONIC=/opt/homebrew/bin/tectonic /Users/konrad.grzyb/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 books/book_i_introductory_edition/build.py --only-cached
```

The builder runs the diagram authoring script, then Tectonic with untrusted
input mode, deterministic mode and `SOURCE_DATE_EPOCH=1789776000` (19 September
2026 00:00 UTC). It does not enable shell escape. Successful output replaces
only this edition's `why_ebu_book_i_candidate.pdf`, using an atomic replacement.
It never writes to the preserved PDFs. Temporary TeX files and logs stay in
the ignored `build/` directory.

The mathematical checker evaluates separately declared fixed states with exact
rational arithmetic and checks elementary polynomial coefficients. It does
not simulate the listed actions. The edition checker verifies source locks,
preserved PDFs, the complete baseline outline inventory, references, page
labels and PDF bounds. It expects the recorded repository HEAD and local source
paths; adapt those checks deliberately for a relocated review copy, rather
than interpreting a missing source PDF as successful verification.

`render_review.py` copies the candidate to an immutable snapshot, supplies a
local Fontconfig configuration/cache and renders at 100 dpi to
`review/pages/<PDF-hash-prefix>/`. This avoids reading a file during replacement
and keeps iterations separate. Its images must then be visually inspected.
Text extraction and bounds checks are not substitutes for that inspection.

## Reproduction boundaries

`source_locks.json` identifies the starting scientific/editorial records and
the three untouched PDFs. `build_manifest.json` identifies all delivered
files, the candidate digest and the exact typesetting dependencies used here.
A repeat offline build was compared byte for byte; see `VERIFICATION_REPORT.md`.
Identical bytes on a different toolchain or a future package bundle are not
claimed. Match the recorded inputs and versions before assessing a mismatch.

External sources are cited, not bundled as a substitute for the publishers'
copies. Downloaded IPCC/IPBES research copies remain ignored build inputs for
the citation review and are not required to typeset the book. Their official
URLs and inspected-file digests are recorded in the manifest.

After editing the manuscript, rerun the relevant static checks and inspect all
changed rendered pages; if pagination or fonts change globally, inspect every
page. The delivered review and manifest describe the delivered candidate only.
Refreshing hashes does not certify a new manuscript's scientific or visual
quality. Author review is the next boundary; publication and experiments need
separate authorisation.
