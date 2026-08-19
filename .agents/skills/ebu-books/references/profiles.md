# EBU Books Profiles

Select one primary profile from the user's requested stage. A planning brief,
manuscript mutation, PDF render, and integration are separate permissions.

## Book-plan or revision-brief update only

**Expected inputs**

- The exact planning document, affected parts or topics, requested decision,
  base identity, and authorized paths.
- The relevant integrated book-planning sections and any accepted foundations
  allocated to those parts.

**Permitted scope**

- Edit only the named planning register, revision brief, or documentation.
- Use read-only manuscript or PDF evidence only when the request supplies or
  authorizes that evidence gathering.

**Minimum checks**

- Reconcile series allocation, overlap controls, dependencies, stop conditions,
  reader-comprehension rules, regeneration sequence, and affected nonclaims.
- Preserve the distinction between prospective plans, historical baselines,
  tested implementation properties, and observed scientific results.
- Keep all pagination categories separate and identify unresolved baselines.
- Run the text-integrity utility and inspect the complete authorized diff.

**Prohibited operations**

- Do not revise or generate manuscripts, run generators, render PDFs, or change
  templates, figures, scientific code, protocols, or results.
- Do not turn a plan into manuscript or publication authority.

**Expected output or report**

- Report the planning decisions, exact documentation changes, integrity and
  consistency checks, current unknowns, and the next review or manuscript stage
  as not begun.

## Manuscript regeneration

**Expected inputs**

- Explicit manuscript authority naming each part, source baseline and hash,
  regeneration or revision mode, accepted planning checkpoint, toolchain,
  authorized paths, and desired outputs.
- Explicit PDF authority as well when PDF generation is requested.

**Permitted scope**

- Change only the named manuscript, generator, asset, or output paths and only
  to the degree the active authority permits.
- Follow the exact authorized mode: the integrated Part I-only revision modifies
  the accepted manuscript rather than replacing it, while coordinated
  framework-alpha regeneration remains a separate permission.
- Revise Part I and regenerate Parts II–III at the framework-alpha trilogy
  checkpoint, or generate Parts IV–IX, only when their committed evidence gate
  and authorized sequence permit it.

**Minimum checks**

- Verify source and artifact identities, preservation rules, affected concept
  allocation, accepted equations, claim labels, citations, and nonclaims before
  generation.
- Apply the complete reader-comprehension and mathematical-explanation order to
  every drafted section, followed by a dedicated human-readability pass.
- Compare content inventories and redlines where preservation authority
  requires them; fail on unexplained deletion or rewrite.
- Run text integrity, authorized manuscript tests, and any separately permitted
  render validation.

**Prohibited operations**

- Do not start without explicit manuscript authority or infer PDF permission
  from source-edit permission.
- Do not alter scientific protocols, results, equations, parameters, or
  framework behavior to improve the narrative.
- Do not regenerate a part whose dependency or evidence gate remains open.

**Expected output or report**

- Identify generated or revised artifacts and baselines, preservation evidence,
  readability and mathematical checks, unresolved content, pagination by the
  required categories, and any rendering or integration stage not begun.

## Human-readability audit

**Expected inputs**

- The exact candidate sections or manuscript, intended reader, governing
  planning checkpoint, and whether the task is read-only or also authorizes
  narrowly scoped corrections.

**Permitted scope**

- Audit prose, examples, transitions, captions, tables, and their relationship
  to equations.
- Make corrections only when the request explicitly combines audit and editing.

**Minimum checks**

- Verify concrete objects and changes, first-use definitions, ordinary-language
  expansion of compressed claims, examples where practical, continuity, and
  explained qualifications and nonclaims.
- Confirm that readers can state what each important result means and why it
  matters to EBU.
- Distinguish readability defects from mathematical or scientific disputes;
  route the latter to the appropriate separate review.

**Prohibited operations**

- Do not delete caveats, simplify away precision, or rewrite accepted science.
- Do not generate a new manuscript or PDF during a read-only audit.
- Do not claim automated wording checks substitute for human reading.

**Expected output or report**

- Lead with findings by severity and location, explain the reader impact, state
  the audit disposition and scope, and list any authorized corrections made.

## Mathematical-explanation audit

**Expected inputs**

- The exact passages, accepted equations and scientific authority, symbol and
  unit conventions, and audit acceptance criteria.

**Permitted scope**

- Review mathematical exposition and surrounding prose read-only unless exact
  corrections are separately authorized.
- Recompute local algebra or arithmetic only where it cannot advance model
  state or inspect an experimental outcome.

**Minimum checks**

- For each important passage, check the question, objects, symbol and unit
  definitions, calculation, physical or operational meaning, EBU purpose,
  assumptions, limits, and inapplicability.
- Verify examples agree with the equation and that signs, domains, thresholds,
  positive-part laws, evidence labels, and qualifications remain exact.
- For `\(\Psi_e\)` or Onsager material, read the corresponding integrated-plan
  sections and preserve their explanatory order and bounded comparison.

**Prohibited operations**

- Do not change an accepted equation or scientific claim to improve exposition.
- Do not infer physical validation from analogy, dimensional consistency, or
  implementation tests.
- Do not execute models, trajectories, or scientific callbacks.

**Expected output or report**

- Give location-specific findings, corrected explanation only when authorized,
  checks completed, and unresolved mathematical or scientific questions.

## Rendering and PDF inspection

**Expected inputs**

- The existing PDF to inspect or explicit authority to render a named manuscript
  with a specified toolchain and output path.
- The applicable layout candidates, baseline PDF, page convention, and visual
  acceptance criteria.

**Permitted scope**

- Inspect an existing PDF read-only.
- Render and change output artifacts only when manuscript/PDF generation is
  explicit; change layout sources only when separately included.

**Minimum checks**

- Compare representative prose-, mathematics-, figure-, table-, and
  reference-heavy pages under every authorized candidate layout.
- Inspect headings, line length, margins and gutter, equations, captions,
  tables, page breaks, blank areas, clipping, repeated furniture, accessibility,
  and complete-page coverage required by the plan.
- Report observed page counts separately from estimates and scenario additions.

**Prohibited operations**

- Do not render merely because a planning or audit task mentions a PDF.
- Do not select a layout winner in advance or compress explanations to reach a
  page target.
- Do not describe a scenario increment as an individual volume size.

**Expected output or report**

- Report inspected or rendered artifacts, visual findings, exact observed page
  counts, unresolved defects, separated pagination categories, and whether a
  final PDF was authorized and produced.

## Documentation or manuscript integration

**Expected inputs**

- Explicit integration authority naming the accepted candidate, target branch,
  expected base or parentage, permitted Git operations, and validation evidence.

**Permitted scope**

- Integrate only the accepted documentation, manuscript, and explicitly named
  generated artifacts.
- Perform only the authorized merge, fast-forward, cherry-pick, commit, or
  normal push.

**Minimum checks**

- Verify candidate acceptance, identities, ancestry, exact diff, clean target,
  text integrity, required preservation evidence, and artifact hashes.
- Confirm integration introduces no framework, protocol, result, unintended
  manuscript, or unexplained binary change.
- Recheck rendered artifacts only when that validation is authorized and needed
  to establish integration fidelity.

**Prohibited operations**

- Do not rewrite candidate content, resolve substantive conflicts without renewed
  review, force-push, tag, release, or publish without explicit permission.
- Do not begin another manuscript, rendering, scientific, or publication stage.

**Expected output or report**

- Report starting, candidate, and final identities; exact files; validation and
  artifact evidence; commit and push status; and all later work as not begun.
