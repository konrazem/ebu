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

For every important mathematical passage in Parts I-IX, answer these eight
mandatory questions in this exact order:

1. What are we trying to determine?
2. Which physical, mathematical, or declared objects are involved?
3. What does every symbol mean, and what unit does it use?
4. What calculation is performed?
5. What does the result mean physically or operationally?
6. Why is this calculation needed in EBU?
7. Which assumptions, domains, tolerances, or limitations restrict the result?
8. What would make the equation inapplicable?

Also include a numerical or physical example when useful and practical; this
remains outside the eight-step checklist.

Perform the dedicated human-readability pass after drafting. Replace compressed
claims, define terms at first use, connect sections, and explain caveats without
removing them. Do not sacrifice mathematical precision or alter accepted
equations, signs, units, domains, constraints, qualifications, evidence labels,
or nonclaims for simpler prose.

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
