# EBU Book 1 — combined theoretical integration report

5 October 2026. Author-review manuscript.

**COMBINED BOOK 1 THEORETICAL INTEGRATION COMPLETE — INDEPENDENT BOOK AUDIT REQUIRED**

The continuous *What an Economy Must Keep Alive* manuscript has been rewritten throughout as the theoretical foundation of EBU. The result contains **304 PDF pages, 49 chapters, five technical appendices, 17 diagrams and 50 bibliography entries**. The detailed, linked contents occupies 12 pages. All 49 existing chapter files and all five appendices were revised. Feedback and memory were integrated into the existing dynamic argument; no additional chapter was appended in this combined rewrite.

The recurring water, clinic, restoration and shared-infrastructure examples now connect state, valuation, history, interaction, response, probability, entropy and actor accounting. Major developments explain their motivating problem, mathematical result, useful capability, accounting consequence and practical meaning. The closing chapters develop a balanced monetary comparison and prospective societal uses. Proved mathematics is presented confidently under its assumptions; repeated generic evidence warnings were removed. Physical calibration and institutional choices retain their specific scope.

Book 1 contains definitions, essential proofs, derivations, counterexamples, conceptual examples and the theoretical architecture. Later books own implementation, test designs, simulations, campaigns, apparatus, application-specific calibration and results. Length has no fixed ceiling. The author's permission to exceed 600 pages is preserved in the series plan; it was not converted into a minimum or used to pad the manuscript. The final length follows the current cleared material and its explanation.

## 1. Delivery and version identity

| Item | Final disposition |
| --- | --- |
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `codex/book-one-continuity` |
| Starting scientific commit specified by the combined brief | `f3ef451773e5c421952c67382ea0a7d5b6565da8` |
| Verified feedback audit tree | `445780d0a82a568ad33711677e506d01501e7d98` |
| Earlier book checkpoint preserved as the direct parent | `7bff728f88a8ae168e92ecbf488d3a4616b7e2f5` |
| Book 1 content commit | `fd4fbd3fb11560311bd1ad9e97aa455ad00fc83d` |
| Work-report commit | Separate following commit containing this report; full SHA returned in the delivery message. Its own hash cannot be embedded in its preimage. |
| Editable manuscript | `books/one_book/book.tex`, with its chapter, appendix and figure sources |
| Final PDF | `output/pdf/EBU_What_an_Economy_Must_Keep_Alive.pdf` |
| Book structure file modified | **YES**: assign complete cleared theory to Book 1, preserve later evidence/application responsibilities and historical numbering, remove a fixed page requirement |
| Content scope | 68 files: 65 modified files and three new static vector diagrams |
| Push | **NO** |
| Independent book audit | **REQUIRED; not performed by this authoring task** |

The original R-stage, S-MG and feedback commits were not amended. The earlier local book checkpoint is retained, rather than rewritten out of history. This content commit builds on that checkpoint and incorporates the later combined brief and authorial steering. No published history was rewritten.

The earlier 272-page checkpoint followed an interim request to improve only the contents. The subsequent combined brief and explicit request to rewrite the whole book superseded that limited pass. This report describes the final whole-book revision, not the earlier contents-only checkpoint.

## 2. Context, selected edition and authority

### The selected Book writer manuscript

The author selected the recent continuous edition from the chat titled **Book writer**, rather than a new concatenation of the older volumes. Its local session identity is `01a0aa6d-5aff-78a3-8b49-4fbc9cd47af6`. Read-only recovery of that session supplied the preferences for a continuous explanatory voice, a money/history opening, purposeful examples, preserved depth and no repeated facsimile or practice-studio padding.

The selected source directory is:

`/Users/konrad.grzyb/Documents/Codex/2026-10-02/can-you-do-the-audit-of/book-i-worktree/books/one_book`

Its containing worktree was on `codex/book-i-rebuild` at `a6e94d4c9d25daff75588203b6c00247a2596a3a`, with known uncommitted work and an untracked `one_book` directory. That source was copied and treated as read-only. Therefore the source edition is identified by its actual file hashes, not falsely attributed in full to that commit. `books/one_book/BASE_EDITION_MANIFEST.json` records all 48 imported source/figure files. All 48 original files remain byte-identical.

The supplied PDF at `/Users/konrad.grzyb/Documents/EBU/v5-gauss/EBU_What_an_Economy_Must_Keep_Alive.pdf` matched the selected edition's PDF: 160 pages, 593,891 bytes, SHA-256 `d4ae499d8f57bc912cd32f717105d334398cb7f6d4261c6e1c0cdc5c9dc21d73`. Neither that PDF nor the original source worktree was overwritten. The new repository PDF is a separate output.

### Lead EBU Project and access limits

The author identified [Lead EBU Project](https://chatgpt.com/share/6ac2f0c8-4f8c-83ed-914f-d3755233f6d4) as historical context. A complete fresh retrieval of that shared conversation could not be verified: the web reader returned a cache miss, the app's thread service returned `Transport closed`, and browser control reported that no browser was available. This report does **not** claim complete live access to that chat. The supplied task documents, recovered Book writer context, repository authority hierarchy and cleared reports provided the operative specification for the rewrite. The later authorial instructions were explicit enough to continue without discarding completed work.

Chat context does not supersede the frozen physical foundation or silently authorize experiments. No messages were sent to other chats or people, and no new chats, subagents, campaigns or automations were created.

### Governing source hierarchy

The frozen physical foundation was read before the working theory baseline. Those remain controlling. Cleared reports provide scoped developments within that hierarchy; historical drafts provide provenance and explanatory material.

| Source | Role in this edition |
| --- | --- |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` and metadata | Complete finite transition, physical boundary, fixed-field definition and actor-registration boundary |
| `docs/theory/EBU_THEORY_BASELINE.md` | Established, conditional and open scientific scope; execution pause |
| `docs/theory/EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md`, repaired at `6c1d0822790dc98e249a30ff5e8fa28202723e82` | Path regularity, canonical and entropy scope, field-change and registration semantics |
| `docs/theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md`, `a7655f30bde7b798ca98eacd9138f93b36abf733` | Coalition, recursion, discrete Taylor, mixed derivatives, degree, composite and generator hierarchy |
| `docs/theory/EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md`, same commit | Classical antecedents, equation conventions and source-access limitations |
| `docs/theory/EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md`, `f3ef451773e5c421952c67382ea0a7d5b6565da8` | Pending tank, roots, memory, native units, storage and oscillation/interaction reconciliation |
| Existing sequential–parallel, local Gaussian and topology material | Rebased history versus same-baseline alternatives, exact support, capacity and route interfaces |
| Author-selected continuous Book writer edition | Explanatory voice, recurring examples, source apparatus, typography and build workflow |

The combined brief supplies the later independent-clearance disposition for the R-stage, S-MG and feedback inputs. Historical audit-pending footers in those reports were not altered. Clearance of the inputs is not claimed to clear this new manuscript.

## 3. Editorial decisions and preservation

The central reading route is now visible in the chapter order: state and potential → finite action and regular paths → histories and cycles → simultaneous outcomes and interaction → generated response, feedback and memory → nonlinear composition → canonical calibration and entropy → changing fields and uncertainty → actor records and institutional meaning.

Within the existing 49-chapter framework, motion and generators now precede the general composite-response chapters. The existing generator-orders chapter was rewritten as **Feedback, memory and interaction through time**. The former experimental-bridge chapter became **From laws to a coherent model**: it retains the complete theoretical specification while leaving experimental protocols to later books. The implementation chapter now explains conceptual interfaces rather than presenting a software validation programme. The conclusion states what the theory establishes and distinguishes mathematics, EBU synthesis and the open application programme.

Every chapter beginning and ending was reviewed for the developing question. Missing transitions after several early exercise sections were repaired. Chapter descriptions, recurring examples and practical interpretation were revised in place. This is a rewrite throughout the book with useful derivations retained, not a claim that every sound sentence had to be replaced.

The body remains 11 point at the selected 450 × 666 bp trim. Navy chapter headings, teal teaching boxes and the established margins remain. Contents typography is separate from the body: bold chapter entries, smaller indented section entries, dotted leaders, page numbers and links. A few near-empty ending pages were removed through concise prose and contents spacing, without removing a theorem or shrinking the body font.

The original 11 diagrams are unchanged. Six integration diagrams are present: three from the preceding integration, two of those updated, and three newly added for generators, memory and modes. Older books, their PDFs, historical facsimiles, source inventories and result artifacts remain preserved. The current edition is a subject-level theoretical integration, not a sentence-by-sentence archival merger of all former volumes.

### Relation to the previous Part II material

| Earlier subject | Book 1 treatment and later-book boundary |
| --- | --- |
| Domain, units, geometry, feasibility and quotation | Chapters 8–21 carry the necessary theory and teaching examples |
| Joint value, attribution, sequential history and external change | Chapters 22–30, 40 and 43; physical joint value precedes allocation |
| Capacity invariant and ownership | Chapter 45 proves the conditional invariant and separates institutional permission |
| Dynamics and numerical limits | Chapters 31–35 and Appendix C contain the theoretical response, descent and finite-step distinctions |
| Implementation objects, chronology and commitment | Chapters 18 and 43–47 specify their mathematical responsibilities; software execution remains in later books |
| Test protocols, random-stream validation and extensive certificates | Deferred to the implementation/evidence volumes; not inserted as a Book 1 campaign |
| Historical engine and empirical findings | Preserved in their original sources and manifests; not promoted to results for the new Gaussian or feedback programme |

Part VII retains advanced coordination, identification and system-dynamics applications. Its necessary introductory theory is now in Book 1. No later manuscript was authored or renumbered.

## 4. Chapter-to-chapter continuity map

This is the authorial continuity review requested in the steering update. It records the intended teaching function and observable coverage for the later independent auditor. It is **not** the independent book audit or a scientific promotion of the manuscript.

Page numbers below are printed main-matter pages. Each entry identifies the existing source file and the question, theory, example, capability, accounting meaning, social relevance, limitation and next question.

### 1. What does an economy keep alive?

Source: `books/one_book/chapters/01.tex`; starts p. 1.

**Question:** What should an economy maintain?

**Theory and example:** Physical function versus exchange records. Example: Clinic water and maintenance.

**Capability:** Names the physical question behind the account. **Accounting implication:** Separates a payment from the condition left behind.

**Practical/social relevance:** Makes continuing service visible. **Limit:** A motivation does not select a potential.

**Next question:** How do incentives affect the next action?

### 2. What money rewards, and what it cannot see

Source: `books/one_book/chapters/02.tex`; starts p. 4.

**Question:** Why can a useful repair lose a payment comparison?

**Theory and example:** Physical possibility, consequence and institutional incentive. Example: Workshop choosing between an order and a repair.

**Capability:** Locates the decision at which physical information could help. **Accounting implication:** Keeps financial and physical records distinct.

**Practical/social relevance:** Supports maintenance without misdescribing money. **Limit:** The account does not determine a contract or duty.

**Next question:** Why can an available resource remain inaccessible?

### 3. Scarcity is more than an empty store

Source: `books/one_book/chapters/03.tex`; starts p. 7.

**Question:** What kind of scarcity is present?

**Theory and example:** Quantity, route, timing and entitlement distinctions. Example: Water behind a locked gate or already in transit.

**Capability:** Identifies the obstacle before prescribing more supply. **Accounting implication:** Requires a state that represents the relevant constraint.

**Practical/social relevance:** Avoids wasteful correction and blaming unmet need on its recipient. **Limit:** A physical description does not settle rights.

**Next question:** How does the boundary expand to planetary resources?

### 4. The planet inside the account

Source: `books/one_book/chapters/04.tex`; starts p. 10.

**Question:** How should large physical claims enter an account?

**Theory and example:** Observation, projection, boundary and scope. Example: Planetary assessments and local water consequences.

**Capability:** Connects claims to defined quantities and periods. **Accounting implication:** Distinguishes recorded change from forecast.

**Practical/social relevance:** Helps make long consequences visible. **Limit:** An assessment is not a calibrated EBU field.

**Next question:** Can local relations give coherent global consequences?

### 5. How does the world know which way to go?

Source: `books/one_book/chapters/05.tex`; starts p. 13.

**Question:** How can local information support a consistent whole?

**Theory and example:** Stationary-path analogy versus exact state differential. Example: Light paths followed by alternative delivery routes.

**Capability:** Separates route accumulation from endpoint comparison. **Accounting implication:** Avoids charging twice for one represented effect.

**Practical/social relevance:** Supports comparison of resource use and timing. **Limit:** Optical analogy is not an EBU motion law.

**Next question:** Why does physical conservation still leave a maintenance problem?

### 6. Energy, life and functional balance

Source: `books/one_book/chapters/06.tex`; starts p. 16.

**Question:** Why does useful function require continuing work?

**Theory and example:** Conservation, thermodynamics and homeostasis. Example: Body temperature and a supplied clinic tank.

**Capability:** Explains function sustained through flow. **Accounting implication:** Keeps energy and carrier accounts beneath valuation.

**Practical/social relevance:** Makes maintenance a continuing service requirement. **Limit:** Homeostasis is not a theorem that this controller works.

**Next question:** Which reference should the system approach?

### 7. Equilibrium is not a maximum

Source: `books/one_book/chapters/07.tex`; starts p. 19.

**Question:** Is a stable operating point necessarily desirable?

**Theory and example:** Reference, equilibrium and stability. Example: Driven tank with a persistent shortage.

**Capability:** Distinguishes convergence from valued condition. **Accounting implication:** Does not label every stable state a restored state.

**Practical/social relevance:** Helps assess what a policy stabilizes. **Limit:** A reference does not guarantee recovery.

**Next question:** How can a complete action receive a signed value?

### 8. What an Energy Balance Unit is

Source: `books/one_book/chapters/08.tex`; starts p. 23.

**Question:** What exactly is one finite EBU comparison?

**Theory and example:** E = V(pre) − V(post); path representation preview. Example: Four-unit two-tank transfer.

**Capability:** Defines a consistent signed amount. **Accounting implication:** Complete transition before attribution or payment.

**Practical/social relevance:** Connects local work to represented physical improvement. **Limit:** The chosen potential still needs a justified meaning.

**Next question:** How is the physical world represented as states and routes?

### 9. Cells, nodes, and edges

Source: `books/one_book/chapters/09.tex`; starts p. 28.

**Question:** Which changes can the network express?

**Theory and example:** State vectors, incidence directions and distinct graphs. Example: Source, pipe, receiver and pending stock.

**Capability:** Makes the possible transformations explicit. **Accounting implication:** Separates locations, valuation dependencies and action interactions.

**Practical/social relevance:** Supports local cooperation around shared resources. **Limit:** An incidence column supplies neither feasibility nor timing.

**Next question:** Do quantities and boundaries reconcile?

### 10. Quantities, boundaries, and one physical change

Source: `books/one_book/chapters/10.tex`; starts p. 37.

**Question:** Where did every represented quantity go?

**Theory and example:** Carrier conservation; gross versus net movement. Example: Lossy route with a named sink.

**Capability:** Prevents hidden creation and displaced loss. **Accounting implication:** Records sources, destinations, pending stock and boundary terms.

**Practical/social relevance:** Makes resource efficiency physically intelligible. **Limit:** A zero conservation residual does not prove each component correct.

**Next question:** Which reference and scale value the complete change?

### 11. Declaring a reference and a scale

Source: `books/one_book/chapters/11.tex`; starts p. 45.

**Question:** What makes deviations comparable?

**Theory and example:** Declared references, scales and unit invariance. Example: Unequal tank needs and litre/unit conversion.

**Capability:** Fixes the ruler before valuation. **Accounting implication:** Keeps native burden units separate from dimensionless EBU.

**Practical/social relevance:** Allows different service needs without requiring equal stocks. **Limit:** A scale is not automatically uncertainty or equilibrium variance.

**Next question:** What potential follows from those declarations?

### 12. Homeostasis as a Gaussian landscape

Source: `books/one_book/chapters/12.tex`; starts p. 54.

**Question:** What does the Gaussian field establish?

**Theory and example:** Quadratic potential, gradient, Hessian and convexity. Example: Two equal-total states with different distribution.

**Capability:** Gives transparent geometry and exact finite formulas. **Accounting implication:** Separates field value from control policy.

**Practical/social relevance:** Enables simple, inspectable accounts. **Limit:** A bowl does not move the system or prove recovery.

**Next question:** How is a derivative restricted to a physical edge?

### 13. From a marginal to an edge field

Source: `books/one_book/chapters/13.tex`; starts p. 64.

**Question:** What does the local field tell a transfer?

**Theory and example:** Directional derivative; force, mobility and flux distinction. Example: Lossless edge and valued arrival sink.

**Capability:** Relates local advice to a complete physical direction. **Accounting implication:** Keeps derivative, dispatch rule and finite receipt separate.

**Practical/social relevance:** Avoids treating a shortage signal as a complete delivery mechanism. **Limit:** Initial slope is not the finite action value.

**Next question:** Why does integrating the changing slope give one endpoint amount?

### 14. Why the whole path has one endpoint value

Source: `books/one_book/chapters/path.tex`; starts p. 74.

**Question:** Why can an action be split without manufacturing value?

**Theory and example:** Fixed-field path theorem with regularity. Example: One restoration performed in many small steps.

**Capability:** Makes endpoint value independent of admissible evaluation path. **Accounting implication:** Refinement preserves the complete receipt.

**Practical/social relevance:** Improves auditability and removes a simple accounting exploit. **Limit:** Equal endpoints do not imply equal service or time exposure.

**Next question:** What is the exact finite correction in a quadratic?

### 15. Finite changes and curvature

Source: `books/one_book/chapters/14.tex`; starts p. 78.

**Question:** How much does the full movement change the field?

**Theory and example:** Exact quadratic expansion and cross terms. Example: Oversupply and a shared source.

**Capability:** Includes curvature at finite size. **Accounting implication:** Subdividing a transfer cannot erase its correction.

**Practical/social relevance:** Discourages redundant delivery within the model. **Limit:** A favourable quote does not establish permission.

**Next question:** Is the proposed transition physically possible?

### 16. Permission before value

Source: `books/one_book/chapters/15.tex`; starts p. 87.

**Question:** What makes a coalition comparison admissible?

**Theory and example:** State domain, shared capacity and trajectory constraints. Example: Two individually feasible withdrawals exceeding one source.

**Capability:** Defines meaningful alternatives before valuation. **Accounting implication:** Infeasible corners are not zero-valued observations.

**Practical/social relevance:** Protects reliable service and shared resources. **Limit:** Endpoint feasibility alone may miss a transient violation.

**Next question:** How is the accepted change valued exactly?

### 17. The exact local signed EBU quote

Source: `books/one_book/chapters/16.tex`; starts p. 90.

**Question:** How can a local quote equal a global difference?

**Theory and example:** Complete-support cancellation and finite valuation. Example: Two-tank quote with omitted energy carrier contrasted.

**Capability:** Computes the exact amount from affected factors. **Accounting implication:** One total under one field and complete boundary.

**Practical/social relevance:** Reduces unnecessary computation while exposing missing burdens. **Limit:** Locality depends on the actual potential and response.

**Next question:** How does a proposal become an identified outcome?

### 18. From a pre-action schedule to a measured record

Source: `books/one_book/chapters/17.tex`; starts p. 93.

**Question:** What does a receipt say actually happened?

**Theory and example:** Frozen schedule, event identity, background and corrections. Example: Delivery shortfall and an expired quote.

**Capability:** Preserves proposal and observed execution separately. **Accounting implication:** Prevents duplicate credit and automatic credit for ring-down.

**Practical/social relevance:** Makes disagreements and corrections traceable. **Limit:** A hash does not establish sensor truth.

**Next question:** How should positive, zero and negative signs be interpreted?

### 19. Positive, zero and negative EBU in real needs

Source: `books/one_book/chapters/18.tex`; starts p. 101.

**Question:** Does a negative action value rank a person's needs?

**Theory and example:** Sign of state change versus service and access. Example: Rural clinic with a burdensome available route.

**Capability:** Explains the action without judging its recipient. **Accounting implication:** Retains signed physical consequences and separate access rules.

**Practical/social relevance:** Guides investment toward better feasible options. **Limit:** A scalar does not rank all human needs.

**Next question:** How can a large system compute this locally?

### 20. Local actions and exact global identities

Source: `books/one_book/chapters/19.tex`; starts p. 109.

**Question:** When is local computation exact?

**Theory and example:** Affected-factor cancellation and aggregation counterexample. Example: Five-cell transfer and a coupled neighbour.

**Capability:** Identifies the precise read support. **Accounting implication:** Reconciles local receipts to the declared global potential.

**Practical/social relevance:** Can reduce calculation and unnecessary disclosure. **Limit:** Coarse totals can discard the valued distribution.

**Next question:** How are coupled functions represented?

### 21. Beyond isolated coordinates

Source: `books/one_book/chapters/24.tex`; starts p. 116.

**Question:** How can one function depend on several resources?

**Theory and example:** Factorized potential and coupled Hessian. Example: Water and energy jointly supporting service.

**Capability:** Extends locality to coupled functions. **Accounting implication:** Evaluates every changed factor once.

**Practical/social relevance:** Makes shared service dependencies visible. **Limit:** A scalar and its factorization do not settle model adequacy.

**Next question:** How do complete events join into a history?

### 22. Action receipts and exact closure

Source: `books/one_book/chapters/20.tex`; starts p. 120.

**Question:** Why does a complete history close?

**Theory and example:** Sequential telescoping. Example: Successive reservoir replenishments.

**Capability:** Reconstructs net change from joined records. **Accounting implication:** Actual successor becomes the next baseline.

**Practical/social relevance:** Supports reliable history and detection of duplicate entries. **Limit:** Closure does not identify a missing physical cause.

**Next question:** What happens on damage–repair loops?

### 23. Closed cycles, splitting and external change

Source: `books/one_book/chapters/21.tex`; starts p. 124.

**Question:** Can cycling or splitting create value?

**Theory and example:** Cycle-zero and refinement invariance. Example: Damage, exact repair and genuine external wear.

**Capability:** Distinguishes restoration from a manufactured loop. **Accounting implication:** Includes negative events and external-change lines.

**Practical/social relevance:** Protects maintenance accounting from selective history. **Limit:** Aggregate closure does not assign responsibility.

**Next question:** Why do simultaneous quotes fail to add?

### 24. Several actors on one nonlinear field

Source: `books/one_book/chapters/22.tex`; starts p. 127.

**Question:** Why is the sum of isolated quotes sometimes wrong?

**Theory and example:** Quadratic group cross term and parallel/serial distinction. Example: Two couriers sharing one source.

**Capability:** Values the actual joint change. **Accounting implication:** Joint total first; interaction is already inside it.

**Practical/social relevance:** Prevents several claims on the same improvement. **Limit:** Two-action formulas do not explain every larger dependence.

**Next question:** What alternatives define a complete coalition landscape?

### 25. A landscape of possible groups

Source: `books/one_book/chapters/coalitions.tex`; starts p. 131.

**Question:** What exactly is being compared in a group claim?

**Theory and example:** Boolean coalition table, drift centering and feasible posets. Example: Water and energy repair alternatives.

**Capability:** Holds baseline, field, horizon and protocol fixed. **Accounting implication:** Separates no-action background from incremental action value.

**Practical/social relevance:** Makes coordinated projects explainable. **Limit:** Missing or infeasible corners cannot be invented.

**Next question:** How are lower-order contributions removed exactly?

### 26. Finding the part that only a group contributes

Source: `books/one_book/chapters/mobius.tex`; starts p. 135.

**Question:** Which part belongs specifically to a coalition?

**Theory and example:** Möbius inversion and reconstruction proof. Example: Three equal transfers with pair effects but zero triple.

**Capability:** Provides a lossless hierarchy. **Accounting implication:** Prevents interactions being paid again on top of group total.

**Practical/social relevance:** Makes cooperation and competition legible. **Limit:** A positive coefficient is not automatic entitlement.

**Next question:** What does each higher order mean in ordinary language?

### 27. When the relationship itself changes

Source: `books/one_book/chapters/recursion.tex`; starts p. 139.

**Question:** How does another action change a relationship?

**Theory and example:** Recursive finite differences and contextual interactions. Example: Water, refrigeration and enabling electrical supply.

**Capability:** Teaches higher order as context changing context. **Accounting implication:** Explains a triple as the change in a pair.

**Practical/social relevance:** Focuses coordination on dependencies that matter. **Limit:** A coefficient remains relative to its declared table.

**Next question:** Can all orders be written in one exact expression?

### 28. An exact Taylor language for finite choices

Source: `books/one_book/chapters/discrete_taylor.tex`; starts p. 143.

**Question:** Why call a finite table a Taylor landscape?

**Theory and example:** Unique multilinear pseudo-Boolean representation. Example: Complete quadratic three-action table.

**Capability:** Reconstructs every Boolean vertex exactly. **Accounting implication:** Separates exact representation from a chosen interpolation.

**Practical/social relevance:** Permits transparent reduced accounts when structure warrants them. **Limit:** The extension between vertices is an additional convention.

**Next question:** How does finite interaction connect to continuous curvature?

### 29. From finite interaction to continuous curvature

Source: `books/one_book/chapters/continuous_taylor.tex`; starts p. 147.

**Question:** What physical geometry can explain interaction?

**Theory and example:** Repeated FTC; local Taylor term and remainder. Example: Coupled-curvature pair and large versus small transfers.

**Capability:** Connects exact finite contrasts to smooth derivatives. **Accounting implication:** Keeps finite value distinct from a local approximation.

**Practical/social relevance:** Allows efficient approximations with explicit error limits. **Limit:** Requires regularity and the declared additive response.

**Next question:** When do higher orders vanish exactly?

### 30. What a quadratic can and cannot explain

Source: `books/one_book/chapters/degree.tex`; starts p. 151.

**Question:** What can a quadratic explain completely?

**Theory and example:** Polynomial degree ceiling and pair-only theorem. Example: Cubic/quartic contrasts and the quadratic null.

**Capability:** Predicts zero triple and above under affine response. **Accounting implication:** Uses proved structure to simplify the hierarchy.

**Practical/social relevance:** A nonzero triple diagnoses a failure of the combined assumptions. **Limit:** Quadratic potential alone is insufficient.

**Next question:** Which motion law actually produces the endpoint?

### 31. Why a field is not a motion law

Source: `books/one_book/chapters/25.tex`; starts p. 155.

**Question:** Why does a field not move the system by itself?

**Theory and example:** Declared mobility, descent and finite-step limits. Example: Gradient flow versus a driven pipeline.

**Capability:** Separates valuation from response policy. **Accounting implication:** A suggested direction is not an executed transaction.

**Practical/social relevance:** Supports useful control without hiding its design choices. **Limit:** Continuous descent does not guarantee any finite numerical step.

**Next question:** What common interface supplies endpoints from motion?

### 32. A generator supplies the movement

Source: `books/one_book/chapters/generators.tex`; starts p. 159.

**Question:** How can a law of change feed the same finite account?

**Theory and example:** Generator → flow → endpoint → coalition. Example: Natural drift and noncommuting actions.

**Capability:** Values timed response without redefining EBU. **Accounting implication:** Fixes initial state, controls, background and horizon.

**Practical/social relevance:** Allows services with different mechanisms to share an account. **Limit:** Well-posedness and admissibility are required.

**Next question:** What happens when correction is still in transit?

### 33. Feedback, memory and interaction through time

Source: `books/one_book/chapters/generator_orders.tex`; starts p. 163.

**Question:** Why can correction oscillate while interaction stops at pairs?

**Theory and example:** Pipeline modes, hidden-state memory, storage and affine feedback theorem. Example: Tank with pending delivery; burden rises while storage falls.

**Capability:** Separates stability, valuation and coalition order. **Accounting implication:** Carries pending state and initial memory; no new actor credits for relaxation.

**Practical/social relevance:** Can inform reduction of duplicate dispatch and persistent shortage. **Limit:** Residence lag is not pure delay; native B is not EBU calibration.

**Next question:** What if action endpoints no longer superpose?

### 34. When actions change one another's physical effects

Source: `books/one_book/chapters/composite.tex`; starts p. 175.

**Question:** Where can high-order interaction enter a simple field?

**Theory and example:** Exact composite contrast −Δ(V∘x). Example: Quadratic field with a triple; nonlinear cancellation.

**Capability:** Identifies response nonlinearity as a possible origin. **Accounting implication:** Resolver and saturation rules belong in the table.

**Practical/social relevance:** Locates a shared constraint rather than assigning unexplained synergy. **Limit:** Nonlinearity need not produce nonzero higher orders.

**Next question:** How do geometry and response derivatives combine?

### 35. Two sources of interaction, one measurable total

Source: `books/one_book/chapters/origins.tex`; starts p. 178.

**Question:** Can a coefficient be split uniquely into causes?

**Theory and example:** Pair, triple and partition chain rules. Example: Mixed example with 9/4 and 7/4 contributions.

**Capability:** Explains contributions under a declared smooth extension. **Accounting implication:** Preserves the invariant finite total.

**Practical/social relevance:** Helps target a response bottleneck or missing valuation factor. **Limit:** Origin split depends on coordinates/interpolation.

**Next question:** Which dependencies force joint calculation?

### 36. Which connections matter for interaction?

Source: `books/one_book/chapters/topology.tex`; starts p. 182.

**Question:** Which connections matter mathematically?

**Theory and example:** State, path, coalition and interaction structures; support cancellation. Example: Two distant pumps using one reserve.

**Capability:** Separates physical distance from dependency and coalition order. **Accounting implication:** Computes only justified local factors and orders.

**Practical/social relevance:** Can make multi-site coordination tractable. **Limit:** Arbitrary tables still require exponentially many corners.

**Next question:** Why should the numerical scale have physical meaning?

### 37. When a potential is also a probability landscape

Source: `books/one_book/chapters/equilibrium_bridge.tex`; starts p. 187.

**Question:** What supplies an independent physical ruler?

**Theory and example:** Canonical normalization, β_bridge=1, Hessian/covariance scope. Example: Thermal energy scale contrasted with deterministic tank.

**Capability:** Connects potential to relative surprisal. **Accounting implication:** Distinguishes a calibrated unit from arbitrary rescaling.

**Practical/social relevance:** Motivates a coherent denomination for intended physical comparisons. **Limit:** Density alone does not imply reversibility or cross-field validity.

**Next question:** What happens when the coalition transform is applied to log density?

### 38. Interaction as a contrast of probabilities

Source: `books/one_book/chapters/probability_interactions.tex`; starts p. 192.

**Question:** How does probability express the same interaction?

**Theory and example:** Canonical log-density Möbius identity. Example: Explicit pair and triple product ratios.

**Capability:** Carries the finite hierarchy into a statistical representation. **Accounting implication:** Normalizer cancels under one fixed measure.

**Practical/social relevance:** Makes a second reading of shared effects possible. **Limit:** Endpoint density is not action-choice probability or entropy interaction.

**Next question:** When does thermodynamic entropy describe the same quantity?

### 39. The entropy connection and its boundary

Source: `books/one_book/chapters/entropy.tex`; starts p. 196.

**Question:** Which entropy change equals k_B E?

**Theory and example:** Accepted conservative single-reservoir P4 relation. Example: Medium/system sign balance and driven ring boundary.

**Capability:** Connects endpoint value, probability and heat in their joint scope. **Accounting implication:** Preserves units and signs in interaction contrasts.

**Practical/social relevance:** Prevents hidden work or currents being priced as equilibrium restoration. **Limit:** Nonequilibrium does not inherit the endpoint-only heat formula.

**Next question:** How can the field change while history persists?

### 40. When the yardstick changes

Source: `books/one_book/chapters/26.tex`; starts p. 200.

**Question:** What changes when the ruler changes?

**Theory and example:** State/parameter differential and finite ordering split. Example: 2030 restoration, 2040 field and scale-change loop.

**Capability:** Separates new action prices from old entries. **Accounting implication:** Field evolution is not an actor action; history is not repriced.

**Practical/social relevance:** Supports learning without retrospective windfalls. **Limit:** Persistent cross-field claims need a justified conversion.

**Next question:** How does uncertain input affect an exact contrast?

### 41. How much confidence belongs beside an interaction?

Source: `books/one_book/chapters/uncertainty.tex`; starts p. 204.

**Question:** How certain is a computed interaction?

**Theory and example:** Covariance propagation and deterministic bound. Example: Reused baseline giving variance 8 rather than 7.

**Capability:** Quantifies uncertainty without weakening the identity. **Accounting implication:** Keeps shared calibration dependence visible.

**Practical/social relevance:** Allows participants to challenge the correct source of error. **Limit:** A significant triple does not identify its physical cause.

**Next question:** How do all representations form one hierarchy?

### 42. What is the glue?

Source: `books/one_book/chapters/continuity.tex`; starts p. 208.

**Question:** What holds the complete theory together?

**Theory and example:** Central endpoint, interaction and dynamic continuity statements. Example: One comparison followed through all layers.

**Capability:** Gathers conditions and capabilities in one place. **Accounting implication:** Distinguishes carrier conservation, receipt closure and institutional balance.

**Practical/social relevance:** Explains how exactness supports efficient maintenance. **Limit:** Stronger representations retain their extra assumptions.

**Next question:** How may a known joint total be attributed?

### 43. Dividing a result does not define an entitlement

Source: `books/one_book/chapters/attribution.tex`; starts p. 214.

**Question:** How can a joint value be divided transparently?

**Theory and example:** Common-path allocation and Shapley-style dividend division. Example: Unequal transfers and a shared-source fan-out.

**Capability:** Makes an allocation reproducible. **Accounting implication:** Group value precedes attribution; no extra synergy pool.

**Practical/social relevance:** Supports cooperation and understandable disputes. **Limit:** Neither allocation is an automatic causal or moral entitlement.

**Next question:** How do records compose over distance and time?

### 44. Routes, resource accounts and learning

Source: `books/one_book/chapters/23.tex`; starts p. 219.

**Question:** How do linked services keep a complete account?

**Theory and example:** Ordered routes, loss carriers and vectors of resource accounts. Example: Clinic route with fuel, electricity and pending arrival.

**Capability:** Retains each transformation and its units. **Accounting implication:** Avoids a hidden mega-action or arbitrary resource conversion.

**Practical/social relevance:** Supports maintenance, access and lower avoidable burden. **Limit:** Distance alone is not a valuation law.

**Next question:** Could the history alter future capacity to act?

### 45. From a signed history to a capacity institution

Source: `books/one_book/chapters/institutions.tex`; starts p. 228.

**Question:** What additional rules create a capacity institution?

**Theory and example:** Conditional aggregate invariant; ownership and netting. Example: Two owners with +3 and −1; essential clinic service.

**Capability:** Separates signed history from spendable permission. **Accounting implication:** States the capacity update and external account explicitly.

**Practical/social relevance:** Allows honest burden records alongside protected access. **Limit:** An invariant does not choose fairness or ensure institutional stability.

**Next question:** Which interfaces preserve these meanings in an account?

### 46. The interfaces of a reproducible account

Source: `books/one_book/chapters/implementation.tex`; starts p. 232.

**Question:** What must an implementation preserve conceptually?

**Theory and example:** Typed roles, exact support, event identity and reconciliation. Example: One transfer with three equivalent value calculations.

**Capability:** Defines responsibilities before software details. **Accounting implication:** Preserves field, response, event and attribution versions.

**Practical/social relevance:** Makes correction and explanation possible. **Limit:** Implementation correctness and empirical observation are separate later tasks.

**Next question:** How do these declarations form one coherent model?

### 47. From laws to a coherent model

Source: `books/one_book/chapters/experimental_bridge.tex`; starts p. 236.

**Question:** How is the whole theoretical specification assembled?

**Theory and example:** Domain, field, response, coalition and institutional interfaces. Example: Maintained clinic water service.

**Capability:** Connects all laws to one declared service. **Accounting implication:** Uses exact simplifications only where their premises hold.

**Practical/social relevance:** Balances resource consequence, timing and essential access. **Limit:** The model does not supply its own empirical calibration.

**Next question:** What could such an account add to an economy?

### 48. From a calculation to an EBU system

Source: `books/one_book/chapters/27.tex`; starts p. 241.

**Question:** Why might this architecture matter outside the example?

**Theory and example:** Physical/event layers and careful monetary comparison. Example: Restoration, workshop purchase, shared infrastructure and long-lived reserves.

**Capability:** Explains prospective uses and limits concretely. **Accounting implication:** Registered outcomes, current-field pricing and persistent history.

**Practical/social relevance:** Could inform restoration, coordination and intergenerational decisions. **Limit:** Does not solve rights, welfare, monetary policy or enforcement.

**Next question:** What is established, and what work follows?

### 49. What the theory establishes

Source: `books/one_book/chapters/28.tex`; starts p. 251.

**Question:** What has the theoretical book established?

**Theory and example:** Established mathematics, EBU synthesis and open programme. Example: Return to clinic homeostasis and continuing maintenance.

**Capability:** Leaves the reader with one connected foundation. **Accounting implication:** Keeps proved laws, architecture and institutional choices legible.

**Practical/social relevance:** Shows how physical information can support useful service. **Limit:** Physical breadth and social effectiveness remain application questions.

**Next question:** Later books develop implementations, designs, simulations and results

### Appendices and supporting material

| Section | Question and contribution | Example / capability | Boundary and next use |
| --- | --- | --- | --- |
| A — Finite differences, regularity and exact checks | Why do the finite and continuous formulas agree? Induction, repeated FTC and remainder derivation | Mixed cubic, interpolation dependence and constrained quadratic geometry | The regularity and affine-domain assumptions remain explicit; supports Chapters 27–30 |
| B — The all-order composite chain rule | How do derivatives distribute between response and potential? Partition formula and induction | Pair/triple/fourth order; integrated composite contrast | A decomposition through an extension is not a unique causal origin; supports Chapters 34–35 |
| C — Feedback, memory and generator proofs | Why do the dynamic statements follow? Lie words, affine solution, hidden-state elimination, true delay, storage and branch bounds | Exact pending-tank solution and zero-triple proof; pure-gradient contrast; stochastic observable scope | No trajectory or campaign is executed; supports Chapters 31–33 |
| D — Density, current and thermodynamic scope | Why does a density not specify reversibility or heat? | Rotating Gaussian and driven jump ring | Canonical, current and P4 statements keep separate hypotheses; supports Chapters 37–39 |
| E — Following one claim all the way through | Can one endpoint table be followed through every representation? | One nonlinear table, exact polynomial, conditional density/entropy and monotone dynamic realization | Allocation and physical interpretation need their own declarations; consolidates the main argument |
| Preface and reading route | Why is this one developing book? | Connects the clinic and water narrative to the central question | Defines Book 1's theory responsibility and later-book boundary |
| Glossary and symbol guide | Which layer and units does a symbol belong to? | Pending stock, residence time versus horizon, native burden versus storage and EBU | Helps prevent notation from silently identifying different quantities |
| References and edition note | Where do the results and status come from? | Versioned source map and classical citations | Records the independent-audit requirement once without repeating a generic warning beside every result |

## 5. Theory-coverage review

Every cleared theoretical layer listed in the authorial update is present. These locations are a coverage record, not a substitute for the later independent audit.

| Required layer | Integrated location and exact scope |
| --- | --- |
| Physical state and boundary | Chapters 8–11, 16 and 47: complete carrier, sinks, pending quantities and admissible domain |
| State potential and finite EBU | Chapters 8, 12, 17 and 42: `E = V(pre) − V(post)` is primary |
| Path/potential theorem | Chapter 14 and Appendix A: supplied single-valued potential, fixed field, sufficient regularity; no extra simply-connected premise when V is supplied |
| Sequential topology and telescoping | Chapters 22–23: joined actual endpoints, signed history and external lines |
| Cycle-zero and refinement | Chapters 14–15 and 23: splitting cannot manufacture net value; complete damage–repair cycle closes |
| Sequential/parallel bridge | Chapters 24–25 and 32: rebased additions versus same-baseline alternatives; serial and simultaneous endpoints need not agree |
| Coalition topology | Chapter 25 and 36.2: complete Boolean table versus the actual feasible poset |
| Möbius interaction | Chapter 26: alternating sum, inversion proof, singleton/pair/triple examples and exact reconstruction |
| Recursive synergy | Chapter 27 and recursion diagram: effect → changed effect → changed relationship → changed higher relationship |
| Discrete Taylor / pseudo-Boolean representation | Chapter 28: unique multilinear vertex polynomial without finite-table remainder; interpolation has separate meaning |
| Mixed finite differences and continuous derivative bridge | Chapter 29 and Appendix A: exact repeated FTC on the full additive parallelotope; local Taylor approximation and explicit remainder are separate |
| Polynomial degree and quadratic pair-only theorem | Chapter 30: degree ceiling for the composite under affine response; pair `−h_iᵀ H h_j`; higher orders vanish |
| Nonlinear response and composite V∘x | Chapters 34–35 and Appendix B: nonlinearity can create interaction or cancel; exact object is the composite finite contrast |
| Generator as interface | Chapters 31–32: well-posed response supplies endpoints at one declared horizon; valuation needs no universal generator classification |
| Empty-coalition drift | Chapters 25, 32 and 47: raw versus relative tables; nonempty coefficients agree; background does not create actor credit |
| Short-time control-affine result | Chapter 33 and Appendix C: leading mixed Lie-word expression with regularity/remainder conditions; no universal all-time degree ceiling |
| Feedback and oscillation | Chapter 33: explicit maintained-source branch, operating point and roots; `4ντ > 1` gives complex modes, not a universal economic oscillation law |
| Hidden-state memory | Chapter 33 and Appendix C: causal kernel, initial pending-state term and input convolution; general kernel `B exp(Dr) C` |
| Residence lag versus true delay | Chapter 33 and Appendix C: one-compartment residence model differs from history-dependent fixed travel time |
| Stability versus valuation | Chapter 33 and Appendix C: storage decrease and receiver-burden increase can occur at the same state |
| Affine feedback / zero triple | Chapter 33 and Appendix C: common linear operator plus additive controls gives affine endpoint at every admissible horizon; fixed quadratic then stops at pairs |
| Oscillation versus Möbius | Chapter 33, Appendix E and four-quadrant figure: oscillatory zero-triple and monotone nonzero-triple examples; independent classifications |
| Native B versus EBU | Chapters 11, 33 and 40: native burden, normalized potential and storage have distinct roles; frequency does not identify the burden scale or separate w and M |
| Loss-sink directional clarification | Chapters 10, 13, 33, 44 and 47: source, pending, receiver and sink directions; shortage dispatch is not automatically the complete immediate gradient |
| Equilibrium bridge and β_bridge=1 | Chapter 37: `V=(U−U*)/(k_B T)`, one fixed reference measure and canonical density; exact normalization is distinguished from a cross-field physical claim |
| Density versus reversibility | Chapter 37 and Appendix D: stationary density can coexist with current; detailed balance and heat balance need their own premises |
| Hessian and covariance | Chapter 37: local Hessian identity differs from global full-support Gaussian inverse covariance; constrained tangent directions are explicit |
| Probability representation and interaction | Chapter 38: endpoint log-density ratio and alternating pair/triple products; not action selection probabilities or information entropy |
| Entropy / P4 interaction | Chapter 39 and Appendix D: accepted fixed conservative overdamped single-reservoir scope, medium `k_B E`, system `−k_B E`; no omitted work channels |
| Field-change semantics | Chapter 40: physical and parameter terms, finite ordering and separate controller revisions |
| Nonequilibrium boundaries | Chapters 31, 33, 37–39 and Appendix D: driven response and current do not inherit universal equilibrium or endpoint-only heat claims |
| Registration and non-repricing | Chapters 18, 40, 45–48: field evolution is not a registered actor event; old entries persist; current conditions value new actions |
| Joint before attribution | Chapters 24–28 and 43: decomposition is inside the group value; common-path/Shapley allocation adds a declared rule |
| Uncertainty | Chapter 41: `cᵀ C c`, shared-baseline covariance, common calibration and deterministic triangle bound |
| Topology and small motifs | Chapter 36: separate state/path/coalition/interaction structures and physical network; factor-support cancellation; no universal compression of missing corners |
| Conceptual economic/social implications | Chapters 1–4, 19, 43–49; substantial treatment in 48.2–48.12, including monetary coexistence and institutional limits |
| Prior-art language | Chapters 26, 35 and 38, source map and references: classical mathematics credited; EBU synthesis is not advertised as the invention of Möbius inversion, feedback or Boltzmann algebra |

### Particularly important reconciliations

The pending model is declared rather than inferred from an accounting identity. On the maintained-source, uncapped branch,

`Ẋ = Q/τ − h`, `Q̇ = ν(L−X) − Q/τ`, `ν = 2wM`.

Its operating point is `Q*=τh`, `X*=L−h/ν`; the receiver burden is positive there when consumption is nonzero. Deviations have roots `[-1 ± sqrt(1−4ντ)]/(2τ)`. Complex roots describe possible damped modes; excitation and the observable still matter. A storage function establishes stability without being equated to raw receiver burden or the EBU denomination. The worked single-state counterexample gives `V̇_B=+1` and `Ė_B=−1/2`.

For additive inputs through one common linear response, the endpoint is affine at every admissible horizon. A quadratic potential therefore has zero triple and higher interactions even when the response oscillates. The explicit three-action example proves branch admissibility analytically and gives pair `−r²` and triple zero. A monotone nonadditive response gives a nonzero triple in the converse direction. No sampled curve is used to establish either result.

The memory reduction retains its initial-condition term. The book distinguishes residence time `τ` from evaluation horizon `T_f`, and native burden `B` from dimensionless EBU and controller storage. A pending-aware alternative controller changes both modes and operating point; real roots alone are not described as proof of better service.

The canonical bridge supplies a physical ruler within its precise scope. A stable deterministic tank does not supply a temperature, invariant density or P4 heat balance. Conversely, a canonical density does not select a motion law or prove reversibility. These distinctions let the representations connect without making them interchangeable.

## 6. Practical-meaning review

| Reader's question | Concrete answer now taught |
| --- | --- |
| Why is path independence useful? | A restoration's value cannot be increased merely by subdividing or narrating its path differently; timing and exposure still have separate meanings. |
| Why is telescoping useful? | Complete histories reconcile to the net state difference, making omissions, stale baselines and duplicate entries detectable. |
| Why coalition interaction? | Shared resources and enabling combinations make joint outcomes nonadditive; the total must be valued jointly. |
| Why higher-order recursion? | A triple says how a third action changes a pair relationship, making irreducible dependence understandable for coordination. |
| Why pending state? | Identical current availability can hide very different deliveries already on the way; the response must retain that information. |
| Why do oscillations matter? | Repeated correction during residence time can alternate over- and under-correction; the response law identifies the relevant modes. |
| Why is stability insufficient? | A controller can settle reliably at persistent shortage, and a decreasing storage function can coexist with rising valued burden. |
| Why physical calibration? | Internal consistency does not choose the numerical size of the unit. The canonical scale supplies a physical benchmark in its domain. |
| Why separate physical evolution and actor records? | A field revision, natural arrival or repeated observation is not automatically a fresh actor contribution. |
| Why complement money? | Exchange, financing and physical consequence answer different questions. A physical account can inform a contract or public choice without becoming a currency. |
| Which problems could the framework help represent? | Restoration, depletion, shared infrastructure, sinks, energy/water timing, supply chains and future capacity; each is explained through a structural feature rather than an invented measured EBU. |
| What does it not solve? | Fairness, legitimacy, ownership, welfare aggregation, responsibility, market design, taxation, monetary policy, financial stability and legal enforcement require additional institutions. |

Chapter 48 compares monetary and EBU accounts across eight dimensions: recorded object, unit, changing prices, physical consequences, joint effects, pending effects, history, and rights/fairness. It acknowledges existing environmental accounting, including SEEA, rather than constructing a comparison with an artificially empty monetary ledger. It states that an incomplete EBU boundary can omit external consequences too.

The restoration example distinguishes money spent from physical improvement. The purchase example follows possible source, energy, sink and pending effects without inventing numerical EBU. Joint infrastructure can be beneficial, adverse or additive; no sign is assumed from its cooperative label. The intergenerational discussion separates changed present capability from a forecast of future service and keeps rights explicit.

## 7. Figures and sources

| Figure | Source file under `books/one_book/figures/` | Role |
| --- | --- | --- |
| 27.1 | `recursion.pdf` | Visual progression from pair relationship to triple and fourth order |
| 32.1 | `generator_bridge.pdf` | Response supplies endpoints; temporal modes and coalition valuation are distinct branches |
| 33.1 | `feedback_memory.pdf` | Explicit pending stock versus memory kernel and initial history |
| 33.2 | `modes_and_interaction.pdf` | Four algebraic combinations of temporal behaviour and interaction order |
| 35.1 | `interaction_origins.pdf` | Potential and response compose into one finite contrast; origin split is not unique |
| 42.1 | `continuity_chain.pdf` | Endpoint, history, coalition, canonical and narrower P4 continuity |

All six are deterministic vector teaching diagrams. Eleven inherited diagrams remain byte-identical. `integration_figures.py` is the only edited Python file: it draws book schematics. **Scientific code was not modified.** The existing `build_book.py` remains byte-identical to the selected source edition. This distinction is explicit because the task's requested “CODE MODIFIED: NO” applies to the protected scientific runtime, while its allowed scope includes book figure source.

The bibliography contains 50 entries. It credits the repository theory inputs and classical sources for incidence algebra, game dividends, pseudo-Boolean and multilinear representations, context-dependent interactions, log-linear models, partition chain rules, control response, linear feedback and stochastic thermodynamics. No priority or novelty proof is claimed. The source note retains limitations on full access to original Harsanyi chapters and other monographs, and the Jansma sign conventions are not imported without deriving the book's own signs.

For the new monetary comparison, the [IMF money explanation](https://www.imf.org/en/publications/fandd/issues/series/back-to-basics/money) supports money's conventional functions, the [IMF externalities explanation](https://www.imf.org/en/publications/fandd/issues/series/back-to-basics/externalities) supports the distinction between private and external consequences, and the [UN SEEA overview](https://seea.un.org/en/methodology/seea-central-framework) supports the description of integrated physical and monetary environmental accounts. The SEEA overview was available through the indexed official-source excerpt; a subsequent direct open returned 403. No full manual review is claimed. The monetary and externalities material was opened through the web reader.

The [Åström–Murray author chapter page](https://www.fbswiki.org/wiki/index.php/Linear_Systems) and [Caltech Feynman Chapter 24](https://www.feynmanlectures.caltech.edu/I_24.html) were inspected for standard linear response and damped-oscillation context. The tank derivations themselves remain explicit in the book. External URLs have not all been network-tested; absence of broken manuscript references does not mean every external website was successfully fetched.

## 8. Build and editorial verification

The established multi-file book workflow was used from the repository root:

```sh
/opt/homebrew/bin/python3 books/one_book/build_book.py
```

The unchanged builder uses cached Tectonic resources, untrusted mode and deterministic rendering, with `SOURCE_DATE_EPOCH=1789776000`. No LaTeX installation, new scientific dependency or replacement book pipeline was introduced. The final repository-location build and the reviewed scratch PDF are byte-identical, including after source newline cleanup.

| Check | Result |
| --- | --- |
| Book build | **PASS** |
| Total PDF pages | 304: 15 front-matter pages plus 289 numbered body/back-matter pages |
| Detailed contents | 12 pages, with chapter and section hierarchy, appendices and back matter |
| Chapters / appendices | 49 / 5; existing framework preserved |
| Bibliography | 50 entries |
| Internal link annotations | 653 |
| Named PDF destinations | 1,188 |
| Undefined references / citations | **NONE / NONE** |
| Duplicate labels / unresolved internal destinations | **NONE / NONE** |
| Unresolved `??` or replacement characters | **NONE** |
| TeX overflow, underflow, missing-character or reference warnings | **NONE** |
| External link annotations | 51; not all network-tested |
| Source whitespace check | **PASS** after removing redundant final blank lines |
| Original source files / inherited diagrams | 48 / 11 unchanged |
| Protected tracked files at the combined checkpoint | 2,918 unchanged; no mismatches |
| Original 2,901-file pre-book inventory | Only the subsequently authorized series-structure file changed |
| Scientific identity check | **PASS**; no scientific imports or execution |
| Final PDF bytes | 1,113,756 |
| Final PDF SHA-256 | `8d6ddaef67411974e857d7a7f6656eb1cbbbed0688f63b04c3cba14816fd3b58` |

All pages were rendered. The complete rendered draft was reviewed through contact sheets, followed by readable-page inspection of the new diagrams, theorem layouts, monetary comparison, contents and final corrected endings. The final 304-page version was rendered again; the affected pages were rechecked. This is editorial/layout verification, not the requested later independent mathematical and continuity audit.

### Constructed teaching arithmetic

Exact symbolic/rational checks supported the manuscript's examples. They are static arithmetic and proof aids, not scientific studies. The earlier integration checks covered 127 basis tables through six labels and 5,461 reconstruction equalities, 81 contextual identities, 70 polynomial ceiling monomials, composite derivatives through fourth order, cubic/quartic contrasts, interpolation dependence, short-time Lie expressions, probability-normalizer cancellation and shared-baseline covariance.

The feedback integration added 13 exact checks: dimensions, operating-flow balance, opposite burden/storage signs at the specified single state, storage cross-term cancellation, the closed-form step-response differential identity and initial conditions, analytic branch bounds, pair and triple formulas, the linear-potential pair null, a monotone triple and nonlinear cancellation. The feedback checks used no positive-time trajectory samples, scientific modules or RNG.

No theorem's physical applicability is established by these arithmetic checks. The book supplies proofs under stated assumptions; experiments and application validation remain in later volumes. The checks are not an independent audit certificate and are not promoted to scientific authority.

## 9. Protected scientific identities

The foundation remains 49,098 bytes. The execution seal remains `PRE_DRIVER`, with `execution_authorised = false`; official results for the paused programme remain absent. The static identity verifier inspected file/AST/JSON identities without importing scientific modules. Twelve analysis-source and nineteen validation-source identities retain their frozen aggregate checks. No model state was stepped.

| Protected item | SHA-256 |
| --- | --- |
| analysis | `60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527` |
| baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| design | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| execution | `442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b` |
| foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| plan | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| plan_markdown | `2d40781593c607de31e68f42e713641a97335e198ed3453bbe677e76682f0d93` |
| rstage_report | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |
| seed_map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| `docs/theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md` | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| `docs/theory/EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md` | `ac8128659ff0955ef16197c37c5698f6039c2f4d074c25e2f9c48ef2e89199ff` |
| `docs/theory/EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md` | `a18d11d309efcb4490e8dc0b7a86a327026c0a58a755e649722d9a9071882c18` |

These hashes identify preserved inputs. They are not newly adopted authority documents or amended execution permissions.

## 10. Exact changed-file inventory

The content commit changes only the following 68 paths. The report is a separate 69th delivery path in its following commit. The three new paths are the generator, memory and modes diagrams; all other listed paths already existed at the preceding book checkpoint. Build intermediates, scratch drafting helpers, rendered review images and temporary arithmetic tools are not committed.

```text
EBU_FUTURE_BOOKS_STRUCTURE.md
books/one_book/README.md
books/one_book/appendices/calculus.tex
books/one_book/appendices/generators.tex
books/one_book/appendices/partitions.tex
books/one_book/appendices/probability.tex
books/one_book/appendices/worked_review.tex
books/one_book/book.tex
books/one_book/chapters/01.tex
books/one_book/chapters/02.tex
books/one_book/chapters/03.tex
books/one_book/chapters/04.tex
books/one_book/chapters/05.tex
books/one_book/chapters/06.tex
books/one_book/chapters/07.tex
books/one_book/chapters/08.tex
books/one_book/chapters/09.tex
books/one_book/chapters/10.tex
books/one_book/chapters/11.tex
books/one_book/chapters/12.tex
books/one_book/chapters/13.tex
books/one_book/chapters/14.tex
books/one_book/chapters/15.tex
books/one_book/chapters/16.tex
books/one_book/chapters/17.tex
books/one_book/chapters/18.tex
books/one_book/chapters/19.tex
books/one_book/chapters/20.tex
books/one_book/chapters/21.tex
books/one_book/chapters/22.tex
books/one_book/chapters/23.tex
books/one_book/chapters/24.tex
books/one_book/chapters/25.tex
books/one_book/chapters/26.tex
books/one_book/chapters/27.tex
books/one_book/chapters/28.tex
books/one_book/chapters/attribution.tex
books/one_book/chapters/coalitions.tex
books/one_book/chapters/composite.tex
books/one_book/chapters/continuity.tex
books/one_book/chapters/continuous_taylor.tex
books/one_book/chapters/degree.tex
books/one_book/chapters/discrete_taylor.tex
books/one_book/chapters/entropy.tex
books/one_book/chapters/equilibrium_bridge.tex
books/one_book/chapters/experimental_bridge.tex
books/one_book/chapters/generator_orders.tex
books/one_book/chapters/generators.tex
books/one_book/chapters/implementation.tex
books/one_book/chapters/institutions.tex
books/one_book/chapters/mobius.tex
books/one_book/chapters/origins.tex
books/one_book/chapters/path.tex
books/one_book/chapters/probability_interactions.tex
books/one_book/chapters/recursion.tex
books/one_book/chapters/topology.tex
books/one_book/chapters/uncertainty.tex
books/one_book/edition_note.tex
books/one_book/figures/continuity_chain.pdf
books/one_book/figures/feedback_memory.pdf
books/one_book/figures/generator_bridge.pdf
books/one_book/figures/interaction_origins.pdf
books/one_book/figures/modes_and_interaction.pdf
books/one_book/frontmatter.tex
books/one_book/glossary.tex
books/one_book/integration_figures.py
books/one_book/theory_sources.tex
output/pdf/EBU_What_an_Economy_Must_Keep_Alive.pdf
```

The report path is `EBU_BOOK_1_COMBINED_THEORETICAL_INTEGRATION_REPORT.md`. The content change totals 1,531 insertions and 670 deletions across the textual diff, plus binary PDF updates/additions. Source lines often contain full paragraphs; these counts are not page or word counts.

## 11. Required final disposition

| Required field | Disposition |
| --- | --- |
| BOOK 1 CONTENT COMMIT | `fd4fbd3fb11560311bd1ad9e97aa455ad00fc83d` |
| WORK REPORT COMMIT | Separate following local commit; full SHA in the final delivery |
| STARTING COMMIT | `f3ef451773e5c421952c67382ea0a7d5b6565da8`; existing book checkpoint `7bff728f88a8ae168e92ecbf488d3a4616b7e2f5` retained |
| BOOK 1 FILES MODIFIED | Exact inventory in Section 10 |
| BOOK STRUCTURE FILE MODIFIED | YES; complete theory assigned to Book 1, later books own designs/results, no page ceiling |
| BOOK BUILD | PASS |
| BROKEN REFERENCES | NONE internally; external-site availability not comprehensively tested |
| PATH / POTENTIAL | INTEGRATED |
| SEQUENTIAL / PARALLEL BRIDGE | INTEGRATED |
| MÖBIUS INTERACTION | INTEGRATED |
| RECURSIVE SYNERGY | INTEGRATED |
| DISCRETE-TAYLOR | INTEGRATED |
| MIXED-DERIVATIVE / TAYLOR CONNECTION | INTEGRATED |
| POLYNOMIAL DEGREE / QUADRATIC PAIR-ONLY | INTEGRATED |
| COMPOSITE V∘x | INTEGRATED |
| GENERATOR AS INTERFACE | INTEGRATED |
| FEEDBACK / OSCILLATION | INTEGRATED |
| MEMORY KERNEL | INTEGRATED, including initial condition and forcing |
| OSCILLATION VS MÖBIUS | INTEGRATED |
| AFFINE FEEDBACK / ZERO-TRIPLE RESULT | INTEGRATED |
| NATIVE B VS EBU | INTEGRATED |
| LOSS-SINK DIRECTIONAL CLARIFICATION | INTEGRATED |
| EQUILIBRIUM beta_bridge | INTEGRATED |
| DENSITY VS REVERSIBILITY | INTEGRATED |
| LOG-PROBABILITY INTERACTION | INTEGRATED |
| ENTROPY / P4 INTERACTION | INTEGRATED |
| FIELD-CHANGE SEMANTICS | INTEGRATED |
| ACTOR REGISTRATION | INTEGRATED |
| PRIOR-ART LANGUAGE | INTEGRATED |
| CENTRAL FIGURES | Six integration diagrams; 17 total |
| AUTHORITY MODIFIED | NO |
| E1a DESIGN MODIFIED | NO |
| SD-10 EXECUTED | NO |
| CODE MODIFIED | Scientific code: NO. Book-only static figure source: YES, as allowed by the brief. Existing builder: unchanged. |
| SCIENTIFIC RNG | NOT USED |
| MODEL TRAJECTORY | NOT RUN |
| OFFICIAL LONG-RUN CAMPAIGN | NOT RUN |
| REAL OPTICAL-TRAP EXPERIMENT | NOT RUN |
| EXECUTION AUTHORISED | FALSE |
| PUSH | NO |
| WORKTREE | Clean after the content commit; final clean-state verification accompanies the report commit and delivery. |
| STATUS | COMBINED BOOK 1 THEORETICAL INTEGRATION COMPLETE — INDEPENDENT BOOK AUDIT REQUIRED |

The next required review is the separate independent book audit, covering mathematical correctness, continuity, readability, motivation, theory coverage, examples, accounting meaning, social comparison and scope. This authoring task stops after the local report delivery; it does not initiate that audit, an experiment or a push.
