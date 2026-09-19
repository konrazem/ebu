# Revised Gaussian Parts II and III

Author-review books, not an adopted scientific protocol or runtime. Read
`EDITORIAL_CONTRACT.md` for the scientific and preservation boundaries.

Part II contains 14 new chapters (33–46) and 30 selected historical proof
pages. Part III contains 14 new chapters (47–60) and 45 historical evidence
pages. They are reconstructed editable revisions, not recovered original
manuscripts or exhaustive reprints. The originals remain unchanged.

The original serif body, navy headings, explanatory sequence, equations and
teaching boxes inform the layout. The author's subsequent request reduces
chapter titles to 18 points and section headings to 12 points throughout
the new cores; the shared body remains 11 points. Historical appendix chapter
titles are visually reduced without rewriting their scientific body content.

Onsager's origins and limits are explained in revised Part I Chapter 13,
Part II Chapters 37 and 44, and Part III Chapter 56. The 1931 primary papers
are cited. The historical EBU law is explicitly Onsager-type, not a theorem
that an economy obeys thermodynamic reciprocity.

## Build and review

From the repository root, using Python with pypdf, pdfplumber, ReportLab and
Pillow, plus Tectonic and Poppler:

```sh
python3 books/parts_ii_iii_revised/verify_arithmetic.py
python3 books/parts_ii_iii_revised/build_books.py
python3 books/parts_ii_iii_revised/review_books.py
python3 books/parts_ii_iii_revised/finalize_records.py
```

The build invokes setup, verifies both original PDF hashes, shares Book I's
layout, compiles offline and appends the historical excerpts. The scripts
contain this workspace's absolute runtime/source paths; another host must
configure equivalent locations and a populated TeX cache. No model is imported.

Outputs are under `output/pdf/` at the repository root. The review directory
contains the original outline inventory, subject disposition, PDF checks,
source manifest and completed verification report. Rendered images and build
caches are ignored. Output PDFs are ordinary PDFs, not certified PDF/A or
fully tagged accessibility editions.
