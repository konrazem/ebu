# Integrated Part II — Mathematics, Implementation and Evidence

Current replacement for the abbreviated separate II/III drafts. Main chapters
33–62 follow Part I's 1–32, with one contents list and continuous new folios.
The eight-part forward plan is in `../../EBU_FUTURE_BOOKS_STRUCTURE.md`.

Read `EDITORIAL_CONTRACT.md` for authority and preservation boundaries.
Original PDFs remain untouched. Editable revised chapters and extended worked
sections form the current argument. Detailed historical proofs and evidence
are integrated at their relevant chapters, with original assumptions and
numbering clearly identified. They are not Gaussian results or new execution.

The delivered page count is separated into new typeset material and historical
readings in `review/build_outputs.json`. This is not a claim that every old
sentence was rewritten. See the source coverage ledger for actual disposition.

## Build and review

Use the bundled Python with pypdf, pdfplumber, ReportLab and Pillow; Tectonic
and Poppler paths are explicit in the book tools. No EBU model is imported.

```sh
python3 books/part_i_revised/build_book.py --offline
python3 books/part_ii_integrated/build_book.py
python3 books/part_ii_integrated/verify_examples.py
python3 books/part_ii_integrated/review_book.py
```

The builder checks both original PDF hashes, derives the shared style from
Part I, prepares labelled readings, and typesets offline. `prepare_sources.py`
records the initial one-time migration of the earlier drafts and intentionally
refuses to overwrite an edited chapter. It is **not** a normal rebuild step.

`chapters/` and `extensions/` are editable manuscript sources; the builder
places each extension before its chapter's closing recap. `readings.json`
declares exact original page ranges and interpretation bridges. Generated
caches and review images are ignored. `review/VERIFICATION_REPORT.md` records
actual inspection and known limitations, not a claim of independent peer review.

Output: `../../output/pdf/EBP_Book_Part_II_Integrated_Gaussian_Explanatory_Edition.pdf`.
The earlier separate revised II and III outputs remain preserved intermediate
drafts, not the current books to read.
