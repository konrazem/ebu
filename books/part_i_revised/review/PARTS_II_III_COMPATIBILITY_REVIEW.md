# Parts II and III: compatibility with the Local Gaussian edition

Status: bounded read-only content audit and editorial recommendation. No
Part II/III manuscript was changed, no experiment was run, and no new result
or implementation acceptance is asserted.

## Answer

**Yes: both volumes need a compatibility revision if they are to be read as
the active continuation of the new Book I.** The potential, worked examples,
model-specific dynamics and current-programme language are not aligned with
the Gaussian direction. A formula-only search-and-replace would be wrong.
But **not all their mathematics becomes obsolete**: exact finite accounting,
local cancellation, telescoping, conditional proofs and reproducibility
principles survive at their stated scope. Historical studies must retain the
potential, controllers and results that were actually used.

The existing series plan's recommendation to preserve both PDFs is correct.
Its phrase “targeted future compatibility” should not be mistaken for “only
change a few symbols.” A coherent active Part II needs substantial, bounded
mathematical respecialization and new worked examples. Part III needs an
explicit split between preserved historical implementation/evidence and any
new programme specification. New implementation and evidence chapters cannot
be written as accomplished work before that work exists.

## Sources and scope

Audit checkout HEAD: `05f3cb02d0c48e60de98342edfac9c36f2cecc6f`.
The main Book I task's expected working changes were preserved. All page
numbers below are **one-based PDF pages**, not printed page numbers.

| Source | Pages | SHA-256 |
|---|---:|---|
| `/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_II_Unified_Explanatory_Edition.pdf` | 160 | `c36e3fad562455808775a3470b8c270faf089b2843dbe17b03635a31e1179095` |
| `/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_III_Unified_Explanatory_Edition.pdf` | 153 | `0ab9b352c0464c8a15bd603845c8f8aa3d71b06d470e12ea1b5e393cef154019` |
| `LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md` | — | `21a6ce38b13e8967074ca16eac4d1eea80c125cc5ba59e87e2f3950b1000c9ee` |
| `LOCAL_GAUSSIAN_EBU_BOOK_SERIES_RECONCILIATION.md` (working editorial version) | — | `440300dbbc197119fa52fc36add3687d4dca352b781039c27705eb869d446991` |

The programme reconciliation is committed at
`5a19951dd1ad837ff220cd36aaf69f6abdb0e67f`; its prospective status is retained.
The series plan's working addition concerns the Book I authoring brief, not
new scientific authority. This is a targeted content audit, not a fresh audit
of every historical result manifest, bibliography entry or PDF sentence.

## The actual mathematical change

Part II Equation (31.3), PDF 29, and Part III §46.4, PDF 21, use the hinge family

\[
v_i(x_i)=\alpha_i[L_i-x_i]_+^2+\beta_i[x_i-U_i]_+^2
          +\chi_i[R_i-x_i]_+^2.
\]

The current prospective specialization is

\[
V_i(x_i)=\tfrac12((x_i-x_i^*)/\sigma_i)^2,\qquad
\mu_i=(x_i-x_i^*)/\sigma_i^2,\quad \sigma_i>0.
\]

The old flat zero-burden band (Part II PDF 32) is not the new model's
single zero-deviation reference. The Gaussian Hessian is constant positive
diagonal, `H = diag(1/sigma_i^2)`; its Euclidean gradient Lipschitz constant
is `max_i 1/sigma_i^2`, not the old hinge curvature bound. This gives the
exact finite expansion

\[
E_G=-\mu(z)^T\delta_G-\tfrac12\delta_G^TH\delta_G-C_G.
\]

The first prospective domain is lossless, one homogeneous conserved scalar,
fixed reference/scales, and `C_G=0`. It does not silently contain Allee
regeneration, a gradient-flow selector, or a service optimizer. The old books
usually use `q` as a rate with `delta = Delta t S q`; the new convention uses
finite quantity with `delta = S q`. The chronology also needs an explicit
bridge: the new baseline is after the declared forcing, whereas the old D0
quote uses its particular frozen-drive no-action successor.

## Part II: exact disposition map

| Chapters; PDF pages | Finding and required treatment |
|---|---|
| 27–30; 12–28 | Retain state, units, vectors and action-graph foundations. Synchronize cross-references, finite quantity/rate notation, and physical/factor/interaction topology. |
| 31–32; 29–37 | Major active-model revision: potential, marginal, reference geometry and examples. Preserve the hinge model as a clearly identified historical/domain-specific family. The derivative identity for an action survives; `J=M[f-theta]_+` is a separate controller, not the Gaussian definition or the new actor policy. |
| 33–34; 38–46 | General local cancellation, finite-difference and path-integral identities survive under complete affected support and their regularity assumptions. Add exact Gaussian expansion and new examples. Qualify interpolation versus a model-realised physical path; do not automatically call every integral an observed path. |
| 35–36; 47–59 | Receipt-sum rearrangement and sequential telescoping survive with fixed potential, complete live states, declared burdens and external-change accounting. Retain historical one-action/disjoint-support assumptions where present; the newer group decomposition does not retroactively broaden those theorems. |
| 37; 60–64 | Substantive update: Gaussian cross terms and declared common-path attribution. Retain the old shared-source over-credit warning. Mathematical closure is not proof of ownership, fair shares, causal contribution or spending permission. |
| 38; 65–71 | Chain-rule dissipation remains a conditional theorem **if its exact threshold-mobility flow law is chosen**. It does not transfer to randomly selected affordable actions. Change flat-band rest-set discussion for any Gaussian specialization; preserve the historical theorem, not an implied universal controller. |
| 39–40; 72–84 | Descent-lemma and matrix-norm tools survive. Gaussian specialization needs its own curvature substitution and assumption check. Existing numerical timestep examples/certificates cannot simply certify a different actor process; they apply to their specified Euler flow. |
| 41; 85–94 | P1C's one-step reserve proof is not a consequence of the old potential and is not invalidated by changing it. Its regenerative source classification and export permission nevertheless do **not** become the new closed finite internal-transfer rule. Preserve as historical/domain-specific control mathematics. |
| 42; 95–103 | Keep properly conditional path and dynamic-programming reasoning; update references and avoid reviving superseded physical analogies or importing a planner into the random actor model. This row is architectural disposition, not a new section-by-section proof audit. |
| 43; 104–113 | Keep invariance/stability/attraction distinctions and conditional convergence/recurrence lemmas. Replace active flat-band examples and old “next programme” sequencing. Do not infer recovery from strict Gaussian geometry alone: the actual actor dynamics still require their own argument/evidence. |
| 44; 114–156 | The end-to-end laboratory is explicitly an old hinge/permission/selector model (PDF 115–120); it is not a ready Gaussian worked laboratory. Retain as a named historical example or create a separately labelled Gaussian counterpart with fresh arithmetic. Do not change its old calculated outputs under new formulas. |

Important distinction: the proofs in Chapters 38–41 need not be discarded or
all re-proved from scratch. Where their abstract hypotheses are retained,
the relevant theorem survives; what must be checked or re-derived is the
new specialization and whether the new programme actually satisfies those
hypotheses. “Every old theorem applies to the new experiment” would be false.

## Part III: exact disposition map

| Chapters; PDF pages | Finding and required treatment |
|---|---|
| 45, 47; 14–18, 26–30 | Keep evidence-level and software-boundary teaching, but identify the implementation/version being described. This is not evidence that the Gaussian runtime exists. |
| 46, 48; 19–25, 31–36 | Explicit old parameters, hinge potential, Allee/logistic drive, gradient-triggered flux and synchronous Euler engine. Preserve as historical code exposition or write a new separately scoped implementation chapter once authorized. A potential substitution alone leaves the wrong dynamics. |
| 49; 37–44 | Historical P1C source permission, including zero preservation-safe extraction from finite/irreversible stock (PDF 38). Preserve its theorem and known diagnostic limitation (PDF 43); do not silently use it as permission for conservative internal redistribution. |
| 50; 45–52 | Retain exact locality, finite evaluation and no-double-count principles. Update baseline/quantity conventions and active examples. Reconcile the loss-coordinate wording in §50.6 (PDF 47) against current authority before presenting a general loss/process-cost rule. The new first study is lossless; this does not authorize a loss-aware runtime. |
| 51; 53–59 | Retain request/acceptance/measurement/receipt distinctions and epoch integrity. Add the new distinction among field attribution, ownership and candidate balance policy. Old O3 status and “already certified contribution” examples need clear historical/conditional labels. |
| 52; 60–65 | Preserve falsifiability/conformance teaching. New checks and counts must come from the new implementation, not be inherited from the old one. |
| 53–59; 66–110 | Preserve D1–D10, Gate 1B/1C/1D and O14 as **historical model-specific evidence**, including nulls, corrections and failures. They must not become Gaussian study results by editorial relabelling. Example: old D5 varies `chi`, PDF 71; D9 compares soft/hard reserve mechanisms, PDF 75; O14's F13 and buffer plateau remain historical, PDF 106–110. |
| 60; 111–118 | Keep measurement, calibration, governance and privacy boundaries; replace active parameter cards based on L/U/alpha/beta/chi with correctly scoped reference/scale discussion. No new empirical calibration is implied. |
| 61; 119–132 | Preserve immutable-result and manifest discipline, old file paths and trace reconstructions as versioned historical examples. Add new provenance only when it exists. |
| 62; 133–149 | Substantial status/roadmap update required. The mathematical-core/evidence distinctions survive, but old “current” O3/O10/O11 and next-gate statements are time-bound. Reconcile later committed Gate 1D-C record separately; do not invent or rerun evidence for the new Gaussian programme. |

## Recommended next boundary

After Book I delivery, authorize **one Parts II/III section-level revision
plan**, with three labels on every retained or changed section:

1. general mathematics retained under stated assumptions;
2. active Gaussian specialization requiring revised exposition/derivation;
3. preserved historical model, implementation or evidence.

The plan should list dependency links, required new worked examples and
unresolved authority questions before any whole-volume authoring begins.
It should not run or design the next scientific campaign. Theory exposition
can be updated now; reporting unexecuted Gaussian implementation or results
as completed science cannot.

Validation: PDF text inspection and SHA-256 checks only. Complete targeted
reading covered Part II 29–94 and 104–113; selected laboratory pages and the
complete existing architectural map were inspected. Part III 19–25 and
31–59 were read completely, with targeted evidence/measurement/provenance/
claim-ledger pages across 66–149. No model-state advancement, scientific
execution, manuscript mutation, commit or push was performed by this audit.
