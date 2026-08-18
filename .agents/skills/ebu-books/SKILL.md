---
name: ebu-books
description: Handle an explicitly invoked EBU book-planning, manuscript, readability, mathematical-explanation, rendering, or integration stage under committed authority. Use only when the user invokes $ebu-books; do not use for framework or unrelated repository work.
---

# EBU Books

Use this workflow only when the user explicitly invokes `$ebu-books`.

## Establish the book stage

1. Select exactly one primary profile from
   [references/profiles.md](references/profiles.md) and read it before acting.
2. Distinguish a book-plan or revision-brief task from manuscript generation.
   Planning authority does not permit manuscript changes, regeneration,
   rendering, or PDF creation.
3. Require explicit authorization naming the affected sources and outputs
   before generating or revising a manuscript or PDF.

## Reconstruct the governing plan

1. Establish current Git state and locate the committed planning authority.
   Treat `EBU_FUTURE_BOOKS_STRUCTURE.md` and
   `PART_I_EXPLANATORY_VISUAL_AND_INSTITUTIONAL_REVISION_PLAN.md` as the
   integrated source for series structure, reader-comprehension requirements,
   the `\(\Psi_e\)` explanation, bounded Onsager context, regeneration
   sequence, and pagination calibration.
2. Read only the portions relevant to the selected profile and affected parts.
   Reconcile overlapping requirements rather than relying on chat or an old
   page estimate.
3. Preserve accepted manuscripts, equations, evidence labels, qualifications,
   nonclaims, hashes, and regeneration or revision boundaries required by the
   active authority.

## Preserve reader comprehension

For every important passage, explain concretely for an intelligent reader new
to EBU:

1. the question and relevant physical, mathematical, or declared objects;
2. every symbol and unit before calculation;
3. the calculation;
4. the physical or operational interpretation;
5. why the result matters to EBU;
6. assumptions, limitations, and conditions that make it inapplicable; and
7. a numerical or physical example when useful and practical.

Perform the dedicated human-readability pass after drafting. Replace compressed
claims, define terms at first use, connect sections, and explain caveats without
removing them. Do not sacrifice mathematical precision, accepted signs, units,
domains, constraints, or qualifications for simpler prose.

## Keep pagination categories separate

Report current historical pages, pages added to an existing part, the complete
estimated size of each individual part, the cross-series planning subtotal,
excluded or unresolved components, and the eventual complete-series total as
distinct quantities. Treat calibration from reviewed rendered samples as the
gate for a new estimate. Never describe `86–123` or another scenario increment
as the size of an individual book.

Run `scripts/check_text_integrity.py` on changed text files when applicable.
Stop at the authorized book stage and report exact changes, checks, rendered or
generated artifacts, pagination categories, limitations, and later work not
begun.
