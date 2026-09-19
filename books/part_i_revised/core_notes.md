# Core revision report: chapters 08–16

Authored within the parent task's full-length Part I revision. Starting
repository HEAD inspected as `05f3cb0`; existing `books/` work was expected and
preserved. This subtask changes only `chapters/08.tex` through `chapters/16.tex`
and this note. No commit or push; no model imports, state transitions,
trajectories, scientific runs, or runtime edits.

## Sources read

- Repository `AGENTS.md` and the complete `EDITORIAL_CONTRACT.md`.
- The complete extracted original chapters 01–10, including original prose,
  derivations, worked examples, units teaching, exercises and misconceptions.
- Complete `LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md`.
- `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md` section 6, including cost categories,
  finite/local identity, tangent inequality, path integral, activation branch,
  schedule commitment, and overexecution boundary.
- `SEQUENTIAL_PARALLEL_BRIDGE.md` sections 4–7, including live predecessor
  telescoping, joint endpoints, comparator dependence, and same-baseline
  non-additivity.

## Chapter and word inventory

Whitespace word counts include LaTeX commands and math tokens; they are a
consistent authoring-volume measure, not a claim of prose-only word count.

| File | Chapter subject | Words |
|---|---|---:|
| 08.tex | Physical action; Ridge/Vale account; measurement and model scope | 2652 |
| 09.tex | Cells, vectors, incidence, paths, cuts, label permutations | 2621 |
| 10.tex | Quantity/rate, conservation, forcing baseline, explicit loss boundary | 2474 |
| 11.tex | Reference, scale, mass compatibility, units, granularity | 2556 |
| 12.tex | Gaussian geometry, derivative, gradient, Hessian, bounded domain | 2565 |
| 13.tex | Directional field, signs, changing slope, graph and policy separation | 2631 |
| 14.tex | Exact finite expansion, schedules, integrals, curvature and groups | 2637 |
| 15.tex | Physical admissibility, joint constraints, menu and capacity boundaries | 2554 |
| 16.tex | Exact local quote, costs, schedule, zero branch and evidence meaning | 2478 |
| **Total** | | **23168** |

## Disposition of original teaching

Original chapters 1–3 retain their principal pedagogical purpose: physical
actions below invoices, declared state, Ridge and Vale, vectors, transpose,
incidence, units, source sharing, process chains, explicit boundaries, and
auditable records. All calculations in the new instructional core are
rewritten for finite quantities and the homogeneous lossless domain.

Original chapter 4's patient calculus bridge, finite-versus-marginal lesson,
local/global separation, calibration warnings and worked potential tables are
retained and expanded using fixed Gaussian references and positive scales.
Its hinge/flat-band formula is removed from this edition's core.

Original chapter 5's Allee/logistic/reserve derivations, chapter 7's autonomous
force–flux dissipation law, chapter 8's timestep-error certificates, and chapter
9's P1C extraction rule are not reintroduced as active Gaussian authority.
Their durable lessons about complete state, units, overshoot, joint resources,
and permission are taught with the current finite model. Historical theorem
statements are not declared false or overwritten.

Original chapter 6's chain-rule field derivation and sign instruction survive,
without converting the field into an implicit controller. Original chapter
10's finite quote, local cancellation, cost-category discipline, zero branch,
precommitted schedule, and exact-versus-linear comparison survive and are
expanded under Gaussian geometry. Greedy selection is explicitly not imported.

## Mathematical and interpretive checks

- Main fixture remains `z=(18,2)`, reference `(10,10)`, scales `(2,2)`;
  `V=16`, `mu=(2,-2)`, `H=diag(1/4,1/4)`, `E(q)=4q-q^2/4`.
- Pure arithmetic independently checked endpoint and polynomial values at
  `q=0,2,4,6,8,12,16,17,18`; all agree. In particular `q=17` gives `-4.25`.
- Main quantities are source-side stock amounts; time is integrated once when
  rates are introduced. Cost-free main model remains `C=0`.
- Shared-source example has initial `V=6.75`, final `V=.75`, joint value 6,
  standalone sum 7, fixed-increment cross correction -1.
- Cancellation comparison explicitly switches to `(10,10)` so both
  standalone reverse quantities are admissible. It does not use the main
  `(18,2)` baseline where a four-unit Vale withdrawal would be impossible.
- Gaussian reference geometry is not presented as an observed distribution,
  a restoring plant, a selector, or a proved economic outcome.
- Extended loss example distinguishes conservation from component validity
  and does not claim loss-aware runtime readiness. Definition-6.4 coordinate
  rationale remains a reconciliation boundary, not silently reinterpreted.
- Curvature identity is exact; full cost-schedule concavity is conditional on
  convex costs; fixed activation includes a separate zero branch.
- Nonnegative endpoints are not declared sufficient for all simultaneous
  paths. Source-only aggregate availability is always conditional on the
  stated event semantics, not adopted as an unlicensed universal resolver.
- Capacity balances and same-event netting/ownership remain prospective,
  separately registered policy. Neither a field maximum nor local derivative
  is installed as actor selection.

Structural checks passed for all nine files: matched LaTeX environments and
balanced raw brace counts. Final compilation and visual page review are the
parent task's responsibility. No numerical study or model execution was used
to verify these illustrative calculations.
