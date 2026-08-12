# EBU Future Books Structure and Research Dependency Register

**Status:** Detailed working architecture for Parts IV-IX  
**Created:** 2026-08-10  
**Regenerated:** 2026-08-12  
**Extended:** 2026-08-13 with the circuit-network analogy programme
**Language:** English  
**Purpose:** Preserve the complete future-book architecture, chapter purposes, transitions, overlap controls, scientific dependencies, figure expectations, and research stop conditions in one handoff document.

---

## 1. Executive decision

Parts I-III already exist. The future series should contain six further books in this final reading order:

1. **Part IV - *When Outcomes Must Discriminate***
2. **Part V - *Homeostasis Through Time***
3. **Part VI - *Sequential and Parallel EBU Dynamics***
4. **Part VII - *Across Distance***
5. **Part VIII - *Dynamic Coordination Fields and Society Geometry***
6. **Part IX - *The Action-Accounted Economy***

The scientific progression is:

> **measurement -> time -> multiple actions -> distance -> coordination -> economy**

This order replaces the earlier planning order in which *Sequential and Parallel EBU Dynamics* and *Dynamic Coordination Fields and Society Geometry* were numbered VIII and IX while *Across Distance* and *The Action-Accounted Economy* retained their old VI and VII numbers. Those old numbers made the reading sequence discontinuous. The titles and scientific purposes are preserved; only the order of the ungenerated books changes.

The key editorial decision is also fixed:

> Future books must begin at the unresolved boundary left by Parts I-III. They must not repeat existing introductory chapters merely because an earlier outline was written before the Unified Explanatory Editions expanded.

Part IV and Part V remain separate. Part IV validates outcome measurement, latency, and uncertainty. Part V develops the conditional long-run homeostasis theorem. They have a direct transition but different evidence standards, different completion dates, and different manuscript-generation gates.

---

## 2. Authority, continuity, and scientific status

### 2.1 Sources used for this regenerated register

This architecture was reconciled against the project files available in the current workspace:

- `EBP_Book_Part_I_Unified_Explanatory_Edition.pdf` - 296 pages;
- `EBP_Book_Part_II_Unified_Explanatory_Edition.pdf` - 160 pages;
- `EBP_Book_Part_III_Unified_Explanatory_Edition.pdf` - 153 pages;
- `SEQUENTIAL_PARALLEL_BRIDGE.md` - committed analytical foundation v0.2;
- `DYNAMIC_COORDINATION_FOUNDATION.md` - committed analytical foundation v0.1;
- `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` - committed framework specification v0.1;
- `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` - committed I-0 implementation plan v0.1;
- the Gate 1D-C outcome-discrimination protocol and frozen JSON plan;
- the previous `EBU_FUTURE_BOOKS_STRUCTURE.md` planning register.

Electrical-network theory is a comparison domain for the future Part VI and
Part VIII research programmes, not an authority that proves EBU. The relevant
comparison begins with Kirchhoff-style potential-difference closure and
node-flow conservation, then tests exactly where nonlinear, capacity-limited,
and dynamic networks cease to behave like ideal linear circuits.

The Git repository and its history remain the final authority for committed study status, original Task 2, robust-P1C, Gate 1E, Gate 2, locks, hashes, and official results. This planning document does not authorize an experiment, edit a locked protocol, or convert a proposed result into an observed result.

### 2.2 Continuity rule

An accepted book allocation, equation, theorem candidate, research dependency, evidence gate, or stop condition should be recorded here and then synchronized with the authoritative repository. Conversation summaries are supporting context, not the scientific source of truth.

When a later result changes the outline, the register should be revised explicitly. A new result must not silently rewrite the historical meaning of an earlier registered study.

### 2.3 Claim-status vocabulary

Every important statement in the future manuscripts must be labelled internally as one of the following:

- **Definition** - fixes the meaning of a term or mathematical object.
- **Algebraic identity** - follows exactly from adopted definitions.
- **Theorem** - proved under explicit assumptions.
- **Model-dependent result** - follows inside a declared model but is not universal.
- **Tested implementation property** - supported by code tests, not by itself a physical result.
- **Observed registered result** - measured in a preregistered official execution.
- **Research hypothesis** - a falsifiable proposition awaiting evidence.
- **Institutional design choice** - a governance or allocation rule, not a law of physics.
- **Analogy** - explanatory only, with its failure boundary stated.
- **Open problem** - important and deliberately unresolved.

### 2.4 Figure-status labels

Every figure must carry one of these evidence labels:

- **Schematic**
- **Mathematically derived**
- **Tested implementation**
- **Observed in a registered run**
- **Research hypothesis**
- **Institutional design choice**

This is especially important for gravity, charge, Fermat, diffusion, entropy, waves, cooperation, behavioural change, and economic transition.

### 2.5 Standard descriptive chapter pattern

Every future chapter should normally contain:

1. a genuine physical need;
2. one plain-language question;
3. an intuitive diagram;
4. definitions and units before notation;
5. the main equation explained first in words;
6. a complete numerical example;
7. the corresponding Python architecture or trace path;
8. the registered test, theorem, or hypothesis;
9. a failure case, counterexample, or negative control;
10. a closing ledger: what was established, what was not, and what follows next.

Python-generated figures are explanatory evidence, not decoration. Each important result should normally connect:

> equation -> configuration -> code -> test -> trace -> result figure -> claim

---

## 3. Overlap audit against Parts I-III

The Unified Explanatory Editions already contain many subjects that appeared as full chapters in the recovered future outline. The future books must cite these foundations and move directly to the new scientific boundary.

| Future area | Existing foundation that must not be rewritten as new | Genuine future frontier |
|---|---|---|
| Outcome discrimination | Part III Chapters 58-59 already explain Gate 1D, O14, behavioural differences, buffering, multiplexing, the flat outcome, and F13. Chapter 60 introduces measurement, latency, uncertainty, and privacy. | A new discriminating instrument, Gate 1D-C execution and result, robust-P1C alignment, Gate 1E, and a completed local evidence ledger. |
| Long-run homeostasis | Part II Chapter 43 and Part III Sections 62.17-62.18 already introduce invariance, stability, attraction, and the boundary of the missing theorem. | The actual constrained theorem programme, proofs, assumptions, adversarial simulations, and counterexamples. |
| Sequential actions and simultaneity | Part I already introduces several actors on a nonlinear field; Part II Chapter 37 introduces composition, simultaneity, and shared sources; Part III contains exact quote and receipt telescoping examples. | A general sequential-parallel bridge, named comparators, true interaction, many-action systems, group receipts, allocation, batching, and shared-capacity experiments. |
| Distance, gravity, Fermat, and Bellman | Part I already treats route epochs and warns that distance is not the formula. Part II Sections 30.7 and 32.7 and Chapter 42 already explain why the graph is not gravity, why EBU is not \(q_1q_2/r^2\), Bellman reasoning, Fermat as an analogy, long-range medicine, and route redesign. Part III Section 62.9 repeats the frontier. | Typed time-dependent routes, changing live states, replanning, congestion, multi-resource paths, uncertainty, provisional settlement, route-wide group effects, cooperation experiments, and adaptive infrastructure. |
| Receipts and actor closure | Part II Chapter 35 and Part III Chapter 51 already define action receipts, actor lines, exact closure, and why actor signs are not zero-sum. | Group and route receipts, causal identifiability, O3, binding quotes, residual allocation, institutional reserves, products, supply histories, and economy-scale settlement. |
| Money and the economy | Parts I-III already explain that EBU is not money, a price, a wallet, or buyer-to-seller transfer. Part III Chapters 50-51 and Sections 62.12-62.16 introduce necessary high-burden actions, poverty, collaboration, games, and the economy as a research destination. | A complete institutional synthesis: binding quotes, access, priority, common services, privacy safeguards, enterprise, governance, pilots, behavioural studies, and a functioning economy simulation. |

### 3.1 Consolidation rule for the old *Across Distance* opening

The following recovered chapter ideas are already substantially present in Parts I-II and must not remain separate future chapters:

- Why distance alone is not an EBU formula.
- Why EBU is not \(q_1q_2/r^2\).
- What the gravity analogy helps explain and where it fails.
- Fermat's principle without a “knowing photon.”
- Bellman recursion in plain language.

They are consolidated into one short bridge chapter in the new Part VII:

> **Known Route Foundations and the Unresolved Boundary**

That chapter will cite the existing explanations and then move immediately to time dependence, congestion, changing states, uncertainty, group effects, and adaptive networks.

---

## 4. Final future-series map, sizes, and transitions

Global chapter numbers are not yet frozen. Part-local labels such as IV.1 and V.1 are authoritative for planning. If the present chapter counts survive manuscript development, the provisional global ranges would be 63-77, 78-93, 94-112, 113-130, 131-148, and 149-170.

| Part | Working title | Central question | Chapters | Words | Python/result figures | Estimated pages |
|---|---|---|---:|---:|---:|---:|
| IV | *When Outcomes Must Discriminate* | Can local EBU decisions be measured with an outcome instrument that is sensitive under delay and uncertainty? | 15 | 38,000-48,000 | 25-35 | 190-250 |
| V | *Homeostasis Through Time* | Under what assumptions is the viable region invariant, stable, or attractive over an unbounded future? | 16 | 48,000-62,000 | 35-50 | 240-320 |
| VI | *Sequential and Parallel EBU Dynamics* | How do multiple actions combine, when is parallel execution genuinely different from a named sequential comparison, and which network-potential analogies remain valid? | 19 | 52,000-72,000 | 40-65 | 270-380 |
| VII | *Across Distance* | How do verified actions compose through changing routes, actors, capacities, regions, and infrastructure? | 18 | 55,000-75,000 | 40-60 | 290-400 |
| VIII | *Dynamic Coordination Fields and Society Geometry* | How should providers and actions be timed, placed, and connected across a dynamic network, including systems with storage, switching, and propagation? | 18 | 60,000-84,000 | 52-80 | 330-470 |
| IX | *The Action-Accounted Economy* | How can verified physical action accounting support institutions without pretending that institutional choices are laws of physics? | 22 | 70,000-95,000 | 40-65 | 390-540 |

These estimates include the descriptive tone of Parts I-III, worked examples, proofs, code architecture, exercises, counterexamples, and Python-derived figures. They are not targets to inflate. If a claim can be made clearly in fewer pages, it should be.

The combined provisional range for Parts IV-IX is now approximately
1,710-2,360 pages. The increase is confined mainly to the dedicated Part VI
circuit-network chapter and the Part VIII storage, switching, and
lumped-versus-distributed comparisons.

### 4.1 Why Parts IV and V remain separate

Part IV is experimental and metrological. Part V is mathematical and dynamical. Part IV can be completed after Gate 1D-C, robust-P1C alignment, and the relevant Gate 1E work. Part V may require a longer theorem programme.

Merging them would probably produce a 410-540-page volume and would delay publication of a completed experimental result until the long-run theorem was also ready. The merge question should be reopened only if the completed, illustrated Part IV falls below approximately 150 pages after overlap removal.

### 4.2 Complete transition chain

| Transition | What the earlier part establishes | Question inherited by the next part |
|---|---|---|
| III -> IV | Exact local equations, tested implementation, and O14's genuine behavioural difference with a flat service outcome. | Was the outcome instrument insensitive, and how can a sensitive instrument remain valid under latency and uncertainty? |
| IV -> V | A validated observation-quote-execution-settlement cycle with stated sensitivity and uncertainty boundaries. | If one transition is measurable and conservatively feasible, does repeating controlled transitions preserve viability through time? |
| V -> VI | A conditional one-action or conservatively serialized long-run theorem. | What changes when actions overlap, share sources, occur in different orders, or must be measured as a group? |
| VI -> VII | Exact multiple-action composition, interaction definitions, group receipts, and an explicit O3 boundary. | How do those action groups propagate through routes whose states, capacities, actors, and needs change during execution? |
| VII -> VIII | Dynamic routing, cooperation, shared capacity, resilience, and infrastructure adaptation. | Can timing, placement, topology, phase, and scheduling systematically improve the whole network? |
| VIII -> IX | Tested coordination mechanisms and their physical, fairness, resilience, autonomy, and uncertainty limits. | How should measurement, access, guarantees, responsibility, privacy, enterprise, and governance use those results? |

One recurring region should connect all six future books. Its hospital first exposes O14 buffering, then encounters delayed measurements and drought, then several simultaneous needs, then distant medicine and flood repairs, then network redesign, and finally a complete action-accounted institutional day.

---

## 5. Part IV - *When Outcomes Must Discriminate*

**Central question:** Can local EBU decisions be tested with an outcome instrument that is demonstrably sensitive, and can the local decision cycle remain valid when observations are delayed or uncertain?

**What this book must not repeat:** the full histories of Gate 1D, O14, multi-edge capability, buffering, temporal multiplexing, or the basic measurement list already explained in Part III Chapters 58-60.

**Opening transition from Part III:** O14 showed that policies selected different actions, but destination buffering and bounded service produced the same measured service outcome. Part IV asks whether the policy was ineffective or the instrument was unable to reveal its effect.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| IV.1 | **The Boundary Inherited from O14** | Gives a concise, cross-referenced reconstruction of the exact unresolved claim: behavioural discrimination was observed, outcome discrimination was not. Separates the registered O14 result from every later interpretation. | One causal chain from policy choice to buffered service; one claim-status table; no retelling of the entire O14 study. |
| IV.2 | **Behavioural Difference Is Not Outcome Difference** | Defines capability, choice, behaviour, physical transition, service outcome, and outcome discrimination. Explains why different selected actions can coexist with equal endpoint service. | Paired trajectories with different actions but equal outcome; a units table for every metric. |
| IV.3 | **How Buffers, Caps, and Windows Flatten Results** | Derives the conditions under which destination stock, service caps, demand windows, and temporal multiplexing create a plateau. Converts the O14 explanation into a general instrument-design lesson. | Plateau diagrams, sensitivity boundary plots, and counterexamples where the plateau disappears. |
| IV.4 | **The Outcome Metric as a Scientific Instrument** | Treats a simulation outcome channel like a measurement instrument. Defines non-vacuity, sensitivity, identifiability, resolution, tolerance, and the difference between “no effect” and “unable to detect an effect.” | Instrument-response curves, detection thresholds, and a falsifier tree. |
| IV.5 | **Designing Worlds Whose Outcomes Must Change** | Shows how to construct test worlds in which declared policy differences are analytically forced into measurable outcome channels. Prevents parameter tuning after results are seen. | World schematics, analytical lower bounds, and counter-worlds that remain non-discriminating. |
| IV.6 | **Gate 1D-C: Questions, Worlds, Arms, and Comparators** | Presents the preregistered DC worlds, capability discipline, arms, primary comparisons, and nonclaims in plain language. Explains why the capability-superset arm is not automatically the alignment comparator. | Protocol map, arm table, world diagrams, frozen analytical predictions, and plan-hash provenance. |
| IV.7 | **Positive Controls, Negative Controls, and Falsifiers** | Explains how positive controls prove that the instrument can fire, negative controls detect unintended physical changes, and falsifiers prevent a convenient reinterpretation of a failed study. | Control matrix, PC response plots, and hypothesis/falsifier ledgers. |
| IV.8 | **From Frozen Algebra to Fail-Closed Code** | Maps equations and frozen parameters into an implementation that cannot inspect outcomes while constructing the plan. Separates design, implementation, pre-execution tests, and official execution. | Equation-to-function map, information-boundary diagram, test groups, and provenance trace. |
| IV.9 | **The Preflight Incident and the Integrity of an Unstarted Study** | Records the operational incident without converting it into a scientific result. Explains why a stopped preflight, preserved failure, and separate authorization protect the study. Repository evidence must determine the final incident chronology. | Failure timeline, expected-versus-observed preflight contract, and an explicit `UNSTARTED` scientific status card. |
| IV.10 | **The Official Gate 1D-C Result** | Reports the single authorized execution exactly as committed. This chapter must not be written as a result chapter until the execution exists. It reports nulls and falsifier activations as results rather than repairing them. | Official summary plots, trace-derived figures, execution manifest, and claim table. |
| IV.11 | **Consequences for O10, O11, and F13** | Updates only the claims directly affected by Gate 1D-C. Distinguishes instrument sensitivity, quote-greedy under-service, outcome alignment, and execution integrity. | Before-and-after claim ledger with no broad safety claim. |
| IV.12 | **Every Physical Observation Has an Age** | Introduces observation timestamps, quote epochs, action start, completion, verification, and settlement horizons. Shows how a numerically exact state can still be physically stale. | Observation-quote-execution-settlement timelines and age-of-information plots. |
| IV.13 | **Uncertainty Has Units** | Represents measurement uncertainty in the same physical units as the observed quantity. Separates stock uncertainty, rate uncertainty, timing uncertainty, model uncertainty, and numerical tolerance. | Interval diagrams, dimensional audits, and examples of invalid mixed-unit margins. |
| IV.14 | **Robust P1C, Conservative Permission, and Quote Envelopes** | Aligns the robust-P1C diagnostic before making nonzero-uncertainty claims. Derives conservative no-export feasibility and exact or bounded quote envelopes under declared uncertainty sets. | Robust-budget envelopes, feasible/infeasible regions, and worst-case quote bands. |
| IV.15 | **Gate 1E and the Completed Local-Foundation Ledger** | Executes and reports the repository-defined latency/uncertainty gate without redefining its scope from memory. Closes the local measurement foundation and lists every remaining assumption inherited by Part V. | Gate 1E result figures, final local evidence ledger, and a transition diagram into long-run dynamics. |

### Part IV generation gate

Generate Part IV only after:

1. the Gate 1D-C preflight incident is reconciled in the repository;
2. execution is separately authorized and completed once under the frozen design;
3. the robust-P1C diagnostic is aligned before nonzero-uncertainty claims;
4. the relevant Gate 1E work is completed and committed;
5. all result figures are rebuilt from committed data.

**Closing transition to Part V:** Part IV can establish that one action cycle is observable, discriminating, and conservatively bounded. It cannot establish that repeated cycles remain safe or approach homeostasis. That becomes the exact question of Part V.

---

## 6. Part V - *Homeostasis Through Time*

**Central question:** Under what explicit assumptions does the constrained system remain viable, stable, or attracted toward a homeostatic region over an unbounded horizon?

**Protected role:** This is the principal long-run theorem book. It must not be compressed into a few simulation chapters or replaced by the sentence “EBU enforces homeostasis.”

**What this book must not repeat:** Part II Chapter 43 and Part III Sections 62.17-62.18 already introduce invariance, Lyapunov stability, attraction, and the missing theorem. Part V must do the theorem work.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| V.1 | **From a Reliable Transition to a Long-Run Question** | Imports the validated local transition from Part IV and states the new scope. Defines what would count as preservation, viability, stability, attraction, recovery, and failure across time. | Dependency map from Part IV results to Part V assumptions. |
| V.2 | **Why One Safe Tick Does Not Prove a Safe Future** | Gives explicit counterexamples in which every isolated action looks feasible while repeated demand, delay, depletion, or controller interaction eventually causes failure. | Short-horizon-safe/long-horizon-failed trajectories. |
| V.3 | **The Complete Constrained State Transition** | Defines the state, natural drive, regeneration, controlled action, service, reserve, measurement, and update order needed by the theorem. All state variables and units are declared before proof. | State-transition diagram, dimensional table, and reference implementation interface. |
| V.4 | **Safe Sets, Viable Sets, Target Sets, and Recovery Basins** | Separates four regions that are often called “safe” without distinction. Shows why being inside a reserve boundary is not the same as having a feasible future or converging to a target. | Nested-set diagrams and two-dimensional viable-kernel examples. |
| V.5 | **Genuine Need, Bounded Service, and Physical Impossibility** | States demand assumptions and distinguishes a genuine need from guaranteed physical feasibility. Defines unmet need, degraded service, rationing, and explicit impossibility without changing the physical history. | Feasibility maps and infeasible-demand counterexamples. |
| V.6 | **Recursive Feasibility** | Asks whether a feasible decision today leaves at least one feasible decision tomorrow. Develops the controller and reserve conditions needed for recursive feasibility. | Feasible-action-set evolution and recursive-feasibility failures. |
| V.7 | **The Long-Run Theorem Dependency Structure** | Lists every theorem assumption: regeneration, connectivity, timestep, observation, delay, bounded disturbance, demand, controller action set, and multi-action scope. Prevents hidden assumptions from appearing inside the proof. | Formal dependency graph and assumption-removal table. |
| V.8 | **Forward Invariance of the Viable Region** | Proves the conditional implication that a state beginning in the declared viable region remains there under the stated controller and disturbance bounds. | Derived boundary maps and proof-to-test correspondence. |
| V.9 | **What Mathematical Induction Means by “Forever”** | Explains the base case and inductive step in physical language. Clarifies that an unbounded theorem horizon is not a forecast of every real future and depends on assumptions continuing to hold. | Induction timeline and assumption-validity overlay. |
| V.10 | **Lyapunov Stability in Physical Language** | Defines stability around a set, not only a point. Distinguishes non-increase of a candidate function from actual convergence and explains what a Lyapunov proof does and does not provide. | Lyapunov landscapes and stable-but-not-attractive examples. |
| V.11 | **Attraction, Recovery, and Convergence** | Develops stronger conditions under which trajectories approach a target region or return after a disturbance. Separates finite recovery, asymptotic convergence, and practical neighbourhoods. | Recovery basins, convergence traces, and non-converging invariant cycles. |
| V.12 | **Persistent Disturbances and Practical Stability** | Replaces ideal zero-disturbance claims with bounded-disturbance tubes, input-to-state style reasoning, and explicit residual neighbourhoods. | Disturbance tubes, worst-case envelopes, and noise-amplitude sweeps. |
| V.13 | **Regeneration, Delay, Reserve Boundaries, and Allee Danger** | Tests how logistic regeneration, Allee thresholds, delayed action, and reserve certification interact. Shows why current stock is not identical to future regenerative capacity. | Bifurcation-like regime maps and delayed-collapse counterexamples. |
| V.14 | **Coupled Resources and Interacting Fields** | Extends the theorem cautiously from one represented resource to coupled water, energy, material, health, or ecological fields. Refuses unjustified scalar aggregation and states when separate accounts are required. | Coupled-state diagrams and failure of a misleading single scalar. |
| V.15 | **Long-Horizon Simulations as Theorem Adversaries** | Uses Python sweeps, boundary searches, disturbances, and assumption-removal experiments to attack the proof and find counterexamples. Simulation supports scope testing; it does not supply the word “forever.” | Phase portraits, parameter maps, adversarial seeds, and theorem-failure plots. |
| V.16 | **The Strongest Homeostasis Theorem Actually Earned** | States the final theorem at exactly the scope supported by proof and tests. If shared-source settlement remains unresolved, it may use one action per source or conservative serialization and must say so. Ends by exposing the multiple-action boundary inherited by Part VI. | Final theorem box, assumptions table, evidence ledger, and boundary cases. |

### Target conclusion

The desired conclusion remains conditional:

> Under explicitly stated regeneration, feasibility, connectivity, measurement, timestep, controller, and disturbance assumptions, the viable region may be forward invariant and trajectories may approach or remain within a bounded homeostatic neighbourhood.

The exact wording must follow the theorem actually proved. If attraction is not established, the book must stop at invariance or practical stability.

**Closing transition to Part VI:** A conservative theorem can serialize actions or allow one action per source. Real systems contain overlapping actions, shared capacity, simultaneous repair, group service, and order dependence. Part VI asks how the accounting and dynamics change when the single-action abstraction is removed.

---

## 7. Part VI - *Sequential and Parallel EBU Dynamics*

**Central question:** How do several actions combine, when does parallel execution produce a genuinely different physical result from a declared sequential comparison, and which parts of electrical-network reasoning can supply useful models without being mistaken for EBU laws?

**Foundation:** `SEQUENTIAL_PARALLEL_BRIDGE.md` v0.2 is the committed analytical checkpoint. This book must test it, preserve its distinctions, and amend it prospectively if later evidence exposes an error before manuscript generation.

### 7.1 Core theory that must be preserved

Let \(X_t\in\mathcal X\) be the complete represented state and let \(D(X)\) be the declared distortion function. For a transition:

\[
\boxed{EBU(X_0\rightarrow X_1)=D(X_0)-D(X_1)}
\]

For a sequential order \(\pi\):

\[
\boxed{EBU_{\mathrm{seq},\pi}=D(X_0)-D(X_{\pi})}
\]

For a parallel group \(G\):

\[
\boxed{EBU_G=D(X_0)-D(X_G)}
\]

The parallel interaction must name its sequential comparator:

\[
\boxed{I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}=D(X_{\pi})-D(X_G)}
\]

These equations preserve one endpoint-based foundation while making genuinely new parallel behaviour visible.

The following findings are already part of the working theory checkpoint:

1. **Sequential telescoping is an algebraic identity.** Correctly measured consecutive differences cancel their intermediate states.
2. **Every sequential action must use the live predecessor state.** Evaluating each action independently against the original state double counts or misallocates nonlinear change.
3. **Parallel group EBU is the change from one common before-state to one common after-state.** Grouping must preserve child identities.
4. **A parallel interaction is comparator-relative.** There is no honest unnamed interaction when sequential orders reach different endpoints.
5. **Equal final distortion implies zero EBU interaction.** Identical states are sufficient but not necessary; different states can have equal distortion.
6. **A nonlinear cross-term is not proof of true parallel interaction.** The same cross-term may already appear in a correct sequential calculation.
7. **Cancellation does not erase resource use.** If opposing target effects cancel but both consume resources, the complete state must retain that consumption.
8. **Group EBU does not automatically identify individual causal EBU.** Measurement and allocation must remain separate.
9. **Individual settlement shares are rules unless causal evidence identifies them.** The rule must not be mislabelled as physics.
10. **Receipt batching is beneficial only conditionally.** Shared measurement saves resources only when group-coordination cost is smaller than repeated baseline measurement cost.
11. **Delayed effects require explicit settlement horizons.** Immediate and later EBU are different temporal accounts, not contradictions.

For receipt batching, the working resource-cost model is:

\[
K_{\mathrm{separate}}=nK_0+\sum_{i=1}^{n}K_i,
\]

\[
K_{\mathrm{group}}=K_0+\sum_{i=1}^{n}K_i+K_G,
\]

so the modelled saving is:

\[
\boxed{K_{\mathrm{separate}}-K_{\mathrm{group}}=(n-1)K_0-K_G}
\]

and grouping is cheaper only if:

\[
\boxed{K_G<(n-1)K_0.}
\]

This is a conditional model to test, not a universal EBU law.

### 7.2 Network-potential and Kirchhoff analogy programme

The circuit comparison has one exact algebraic core and several conditional
physical models. It is valuable enough for a dedicated Part VI chapter, but
its claim status is **Analogy** until a named domain supplies and validates
the required physical constitutive laws.

Treat \(D(X)\) provisionally as a scalar node potential on a directed graph of
represented states. For an edge \(e:u\rightarrow v\), define:

\[
\Delta D_e=D(X_u)-D(X_v).
\]

For any consecutive state path \(P\), the directed differences telescope:

\[
\boxed{\sum_{e\in P}\Delta D_e=D(X_{\mathrm{start}})-D(X_{\mathrm{end}}).}
\]

For a closed path that returns to the same complete represented state under
the same distortion model and accounting boundary:

\[
\boxed{\sum_{e\in C}\Delta D_e=0.}
\]

This is the EBU analogue of potential-difference closure used in
Kirchhoff-style voltage accounting. Here it follows from a scalar state
function; it is not evidence that \(D\) is electrical voltage or that EBU has
been derived from electromagnetism. A nonzero measured loop residual is a
diagnostic for inconsistent endpoints, changed boundaries, omitted state,
unrepresented external drive, measurement error, or implementation error. It
must not be interpreted automatically as created or destroyed physical value.

The parallel comparison is equally precise but easy to misuse. Circuit
branches between the same two nodes share one voltage difference; their branch
currents, not their voltage drops, combine through node conservation.
Correspondingly, an EBU joint group has one common before-to-after distortion
difference. Its same-baseline child values are not automatically additive.
For a genuinely conserved typed resource at a source node, a separate
stock-flow equation may be tested:

\[
\boxed{
\sum_j\int_{t_0}^{t_1}f^{\mathrm{in}}_j(t)\,dt
-\sum_k\int_{t_0}^{t_1}f^{\mathrm{out}}_k(t)\,dt
-L_{[t_0,t_1]}
=s(t_1)-s(t_0).
}
\]

Here \(s\) is the stored resource, the \(f\) terms are typed flow rates, and
\(L_{[t_0,t_1]}\) is typed loss over the same declared interval and boundary.
A discrete model may use the corresponding integrated transferred quantities.
This Kirchhoff-current-like balance can constrain simultaneous actions
attached to one source, but it does not make EBU itself a conserved current or
token.

The future deterministic programme should specify at least these models:

| Model | Circuit structure used | EBU question | Required limitation or falsifier |
|---|---|---|---|
| **K1 - State-potential path ledger** | Directed node potentials and voltage-drop closure | Do sequential EBU records telescope and do closed state cycles close under one complete \(D\) and boundary? | Any unexplained residual fails ledger closure; closure alone does not validate the physical meaning of \(D\). |
| **K2 - Ideal common-terminal branches** | Parallel branches with a common terminal difference and separately conserved flows | When a domain legitimately maps actions to branches joining the same complete represented terminals, do they share one endpoint difference while typed flows close separately, without summing voltage-like EBU drops? | Different complete endpoints, coupling, source change, or capacity conflict invalidates the ideal-branch model. |
| **K3 - Finite shared source** | A current-limited source or source with internal impedance feeding simultaneous loads | How do source depletion, capacity allocation, node-condition change, and quantity-fixed versus rule-replayed comparators affect several actions attached to one source? | A model that omits source stock, loss, allocation, or voltage/field sag is incomplete; allocation differences are not automatically simultaneity effects. |
| **K4 - Nonlinear branch or observable** | Nonlinear constitutive response, saturation, or a quadratic power/energy-like observable | When does \(N_G\neq0\) record failure of naive superposition while \(I_{G\mid\pi}=0\) still holds for endpoint-equivalent execution? | A cross-term alone cannot establish causal synergy or a uniquely parallel mechanism. |
| **K5 - Switched storage and dynamic network** | Capacitor/inductor-like memory, switches, delay, recovery, and finite horizon | When do order, timing, stored state, and horizon make sequential schedules differ from simultaneous execution? | If the storage/memory state or external drive is omitted, any apparent order effect is uninterpretable. |
| **K6 - Loss-aware cancellation** | Opposing branch effects with heat, wear, leakage, or source consumption retained | Can target effects cancel while the complete state still records resource use and irreversible burden? | Returning only the visible target coordinate to baseline is not a closed-state cycle. |

No universal resistance, conductance, capacitance, inductance, voltage,
current, power, or energy interpretation is introduced here. In particular,
the familiar series- and parallel-resistance formulae require an independently
validated constitutive relation between potential difference and flow. A
future domain may propose an action-impedance or conductance model only by
declaring its units, state variables, boundary, linearity range, conservation
law, and falsifiers. The physical use of Kirchhoff's voltage law must also
respect the electrical model's own validity conditions; a time-varying or
distributed electromagnetic system cannot be simplified to an ordinary
lumped static loop merely to resemble EBU.

The circuit chapter receives approximately 4,000-7,000 words, 5-10 figures,
and 20-40 illustrated pages inside the revised Part VI budget. Its essential
figures are a state-potential path, a common-terminal branch diagram, a
finite-source capacity/sag model, a nonlinear-superposition counterexample,
and a switched-storage order comparison.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| VI.1 | **From One Transition to a System of Actions** | Bridges from the conservative scope of Part V and audits what Parts I-II already established. Defines the genuinely unresolved many-action boundary without repeating the basic receipt chapters. | Existing/future boundary map and a two-action physical story. |
| VI.2 | **Actions, Transformations, Schedules, and Common State** | Defines action transformations, start and finish times, commitments, schedules, and the represented state required for several actions. Extends deterministic notation toward delayed and stochastic variants. | Action-lifecycle timeline and formal object map. |
| VI.3 | **Sequential Telescoping Beyond Two Actions** | Derives the \(n\)-action telescoping identity and includes natural-drive residuals when drive acts between action epochs. States exactly what telescoping proves and what it cannot identify causally. | Cancellation diagrams, numeric chains, and omitted-state failures. |
| VI.4 | **Path Dependence, Order, and Serializability** | Distinguishes endpoint dependence from ledger allocation dependence. Compares physical scheduling with serializability and transaction ideas without treating computer-science analogies as physical proofs. | Order-permutation examples and serializable/non-serializable cases. |
| VI.5 | **What Counts as a Parallel Group** | Defines temporal overlap, shared sources, shared fields, shared constraints, and common accounting boundaries. Tests whether overlap in time alone is enough to require group measurement. | Interval-overlap diagrams and group-boundary counterexamples. |
| VI.6 | **The Sequential-Parallel Bridge** | Derives \(I_{G\mid\pi}\) and explains why the comparator is part of the scientific statement. Provides positive, zero, and negative interaction examples. | Endpoint triangle diagrams and interaction plots. |
| VI.7 | **State Equivalence and EBU Equivalence** | Shows that identical endpoints imply identical EBU, while equal distortion can hide different states and future capacities. Explains when endpoint EBU alone is insufficient for later dynamics. | Equal-D/different-state contours and future-divergence examples. |
| VI.8 | **Commuting and Non-Commuting Actions** | Defines when action order changes the endpoint. Develops comparator sets or ranges for non-commuting actions and shows why “the sequential result” may not exist uniquely. | Commutator examples, order matrices, and comparator-range plots. |
| VI.9 | **Nonlinear Cross-Terms Are Not Automatically Interaction** | Corrects the tempting but false inference that every \(ab\) term proves parallel synergy. Separates shared nonlinear evaluation from endpoint-changing simultaneity. | Symbolic expansions and matched-endpoint simulations. |
| VI.10 | **Network Potentials, Kirchhoff Models, and Their Limits** | Develops K1-K6: potential-path closure, common-terminal branches, finite shared sources, nonlinear response, switched storage, and loss-aware cancellation. Shows why voltage-like differences, conserved flows, causal contributions, and settlement shares are different objects and why equivalent-resistance formulae do not transfer without a validated constitutive law. | Circuit/EBU mapping table, loop-closure diagnostics, shared-source flow/sag figures, nonlinear and dynamic counterexamples, and explicit analogy-failure cards. |
| VI.11 | **Synergy, Interference, Redundancy, and Capacity Conflict** | Builds an operational taxonomy based on endpoint differences relative to declared comparators. Requires each label to correspond to a measurable physical mechanism. | Paired positive/negative/zero interaction worlds. |
| VI.12 | **Cancellation Without Annihilation** | Uses a state containing target deviation and resource use to show why opposite effects can cancel while physical costs remain. Extends the example to waste, heat, wear, time, and attention. | Resource-retaining cancellation plots and incomplete-state failures. |
| VI.13 | **The Deterministic Two-Action Test Matrix** | Registers the minimal controlled matrix: endpoint equivalence, nonlinear no-interaction, positive interaction, negative interaction, cancellation, redundancy, capacity conflict, and both sequential orders. | Full expected-results table, traces, and falsifiers. |
| VI.14 | **Many-Action Systems and Higher-Order Interaction** | Generalizes the bridge to \(n\) actions and introduces pairwise, triple, and higher-order decompositions as analytical tools. Taylor or inclusion-exclusion-like decompositions must not be mistaken for unique causal allocation. | Interaction-order diagrams and scaling experiments. |
| VI.15 | **Choosing the Sequential Comparator** | Compares reservation order, start-time order, physically natural order, best and worst feasible schedules, a policy-defined canonical order, and a reported range. No canonical rule is selected without purpose-specific tests. | Comparator decision table and sensitivity analysis. |
| VI.16 | **Shared Sources, Reservations, and the Committed Field** | Extends the state to include already accepted actions and source budgets. Connects group action physics to O3 and the K3 finite-source model, and shows why independently valid quotes can conflict at execution. | Shared-source capacity, flow, and field-sag maps plus stale-commitment failures. |
| VI.17 | **Group Measurement and Causal Identifiability** | Separates the objectively measured group endpoint from estimates of individual causal contribution. Defines when separate meters, controlled interventions, or validated causal models make contributions identifiable. | Identifiable/non-identifiable examples and causal-evidence ladder. |
| VI.18 | **Group Quotes, Child Receipts, and Allocation Closure** | Defines one group record that preserves every child action, actor, provider, promise, and residual. Tests the closure condition for actor shares plus institutional accounts while refusing to disguise allocation as measurement. | Group-receipt schema, closure equations, and allocation counterexamples. |
| VI.19 | **Receipt Batching, Settlement Horizons, and the Many-Action Ledger** | Tests the batching inequality, delayed effects, provisional records, and later settlement. Closes the evidence ledger and identifies what must be carried into route-wide action chains. | Cost break-even plots, open/settled receipt timelines, and final claim ledger. |

### Open problems that must remain visible

- the exact overlap condition defining a group;
- the canonical comparator, if one exists;
- individual causal attribution when actions are inseparable;
- O3 shared-source settlement and allocation;
- joining or leaving a group after a quote is issued;
- large-\(n\) scaling, stochastic actions, and incomplete observation;
- delayed and cross-boundary effects whose causal chains overlap;
- which domains, if any, justify a measurable action impedance, conductance,
  capacitance, or other constitutive analogue;
- when a Kirchhoff-style graph is a faithful physical model rather than only
  a ledger-consistency visualization;
- how distributed, time-varying, or field-coupled electrical cases should be
  represented without importing an invalid lumped-circuit approximation.

**Closing transition to Part VII:** Part VI can define and test multiple actions inside a declared boundary. A medicine route crosses many boundaries, actors, clocks, capacities, and changing states. Part VII composes the many-action theory across distance.

---

## 8. Part VII - *Across Distance*

**Central question:** How do verified actions compose across typed, time-dependent routes, multiple actors, shared infrastructure, and regional disruption?

**What this book must not repeat:** the elementary claims that distance alone is not EBU, EBU is not \(q_1q_2/r^2\), Fermat is an analogy, or Bellman recursion can plan a path. Those foundations already exist in Parts I-II.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| VII.1 | **Known Route Foundations and the Unresolved Boundary** | Consolidates the prior gravity, Fermat, Bellman, and distance material into one concise bridge with exact cross-references. States the new frontier: live time-dependent routes, congestion, uncertainty, group effects, and infrastructure adaptation. | One “already established/new work” table and one route schematic. |
| VII.2 | **The Planet as a Typed, Time-Dependent Graph** | Defines nodes, edges, carriers, capacities, states, permissions, and epochs. A geographic kilometre is separated from travel time, energy, loss, risk, and service effect. | Layered graph maps and edge-type tables. |
| VII.3 | **A Route as a Composition of Verified Local Actions** | Builds an end-to-end route from local quote-execute-verify-settle epochs. Uses sequential telescoping and the K1 path-ledger closure diagnostic while preserving intermediate losses, actors, and state changes. It does not claim that a transport route is an electrical circuit. | Route receipt chain, potential-difference-style closure diagram, and endpoint-versus-segment audit. |
| VII.4 | **When Live States Break a Static Shortest Path** | Shows why a route chosen at departure can become infeasible or inferior after stocks, weather, capacity, or need change. Defines safe replanning without rewriting completed segments. | Dynamic shortest-path traces and route-switch examples. |
| VII.5 | **Urgency, Perishability, and an Evolving Need** | Places time, decay, patient condition, service delay, and opportunity cost inside the represented state. Explains why urgent air transport can outperform slower rail without declaring air universally best. | Delay-harm curves and mode comparisons. |
| VII.6 | **Capacity, Congestion, and Shared Infrastructure** | Models queues, shared cold chains, warehouses, ports, roads, and source budgets. Connects route congestion to the many-action framework of Part VI and tests typed source-node stock-flow closure without treating EBU as the conserved flow. | Capacity phase maps, source-node balance diagrams, and congestion externality plots. |
| VII.7 | **Multi-Resource Routes Without False Scalar Collapse** | Tracks medicine, cooling energy, packaging, staff time, vehicle wear, and ecological effects as typed accounts. States when aggregation weights are declarations rather than physical identities. | Multi-layer Sankey-like accounts and scalar-collapse counterexamples. |
| VII.8 | **Uncertainty and Robust Route Feasibility** | Extends Part IV uncertainty envelopes across multiple segments and growing observation age. Tests worst-case feasibility, safety margins, and route failure probabilities without mixing them with prices. | Uncertainty propagation bands and robust-route maps. |
| VII.9 | **Quote, Reserve, Execute, Verify, and Settle Across a Route** | Defines reservations, expiry, segment confirmation, route-wide guarantees, re-quotation, and settlement boundaries. Prevents double settlement when routes are replanned. | Lifecycle sequence, quote epochs, and duplicate-prevention examples. |
| VII.10 | **Delayed and Cross-Boundary Effects** | Distinguishes immediate, delivery-time, and later-horizon EBU. Defines provisional receipts and open causal chains for effects that arrive after the apparent route completion. | Settlement-horizon plots and boundary-crossing traces. |
| VII.11 | **Route Actors and Exact Closure** | Extends actor receipt closure from existing sequential examples to route-wide child records. Separates physical route closure from monetary balance-sheet closure and institutional guarantees. | Actor-route matrix and closure audit. |
| VII.12 | **Joint Effects and O3 Across a Route** | Examines shared warehouses, consolidated loads, simultaneous handling, and shared-source withdrawals. Uses Part VI interaction and identifiability rules rather than inventing independent actor values. | Group-route examples and unresolved-allocation cases. |
| VII.13 | **Medicine Produced Only Far Away** | Provides the complete recurring case: the medicine is needed regardless of its EBU; the receipt records physical consequence; access and guarantees are separate; urgency changes the route comparison. | Full numerical route, patient-delay model, and receipt set. |
| VII.14 | **A Pump After a Flood, and a Region Under Disruption** | Adds replacement pumps, food, heat, and repair under damaged infrastructure. Tests multiple simultaneous genuine needs, scarcity, prioritization pressure, and route failure. | Disruption maps, recovery traces, and competing-needs scenarios. |
| VII.15 | **Cooperation Without Requiring Altruism** | Tests the claim that shared transport, tools, storage, or repair may meet the same needs with less verified burden. Treats cooperation as a material hypothesis, not a moral assumption. | Cooperative versus separate-action experiments. |
| VII.16 | **Fairness, Free-Riding, Access, and Resilience** | Tests whether physically efficient cooperation remains stable and fair under unequal access, strategic use, provider failure, and regional dependency. Keeps efficiency separate from institutional acceptability. | Distributional metrics, failure tests, and free-riding scenarios. |
| VII.17 | **Infrastructure Alternatives Are Accounted Actions** | Compares storage, local production, hospitals, rail, roads, air, sea, tunnels, and shared cold chains while accounting for construction, maintenance, land, and transition burden. | Lifecycle comparison plots and break-even surfaces. |
| VII.18 | **Adaptive Networks and the Route Evidence Ledger** | Tests whether repeated costly receipts are useful signals for structural redesign. Closes the route, cooperation, and infrastructure claim ledger and passes placement/scheduling questions to Part VIII. | Adaptive-network experiments and final evidence table. |

### Collaboration claim to preserve

> EBU does not require people to become altruistic. It may make cooperation materially advantageous whenever shared action meets the same genuine needs with less verified physical burden. Whether that advantage produces stable, fair, and resilient collaboration must be demonstrated rather than assumed.

**Closing transition to Part VIII:** Part VII can compare and adapt routes. The next question is larger: how should the whole provider network be timed, placed, and connected so that many actions coordinate efficiently without sacrificing resilience, fairness, or autonomy?

---

## 9. Part VIII - *Dynamic Coordination Fields and Society Geometry*

**Central question:** How should providers and their actions be arranged across time, sequence, space, and network structure to improve verified system outcomes?

**Central principle:**

> System performance depends not only on what actors do, but also on their relative timing, sequence, location, and structure.

For provider placement \(P\), schedule \(\sigma\), and horizon \(T\):

\[
EBU_G(P,\sigma;T)=D(X_0)-D\!\left(X_G(P,\sigma;T)\right).
\]

Relative to a declared reference schedule \(\rho\), define coordination advantage:

\[
\boxed{C_{\sigma\mid\rho}(T)=EBU_\sigma(T)-EBU_\rho(T)=D(X_\rho(T))-D(X_\sigma(T)).}
\]

The provisional design problem is:

\[
\boxed{(P^*,\sigma^*)=\arg\max_{P,\sigma}EBU_G(P,\sigma;T)}
\]

subject to resource, capacity, fairness, resilience, uncertainty, autonomy, measurement-cost, and coordination-cost constraints.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| VIII.1 | **From Dynamic Routes to a Coordination Field** | Shows why locally good routes can still create system-wide peaks, conflicts, or fragility. Defines the new object: a network of providers whose actions interact through timing and structure. | Local-versus-system outcome example and dependency map. |
| VIII.2 | **State, Providers, Schedules, and Evaluation Horizons** | Defines the minimal dynamic coordination model: provider nodes, actions, capacities, delays, schedules, commitments, state, and horizon. Separates physical variables from policy variables. | Object diagram, units table, and reference configuration. |
| VIII.3 | **Actions as Time-Dependent Signals** | Represents action intensity, duration, start time, and recovery as signals acting on a field. Establishes when continuous, discrete, pulse, or event-based descriptions are appropriate. Uses switched storage and RC/RL-like models as declared analogies for memory and delay, never as automatic electrical identities. | Signal plots, matched discrete/continuous examples, and switched-storage response comparisons. |
| VIII.4 | **Coordination Advantage Requires a Reference** | Derives \(C_{\sigma\mid\rho}\) and imports the comparator discipline from Part VI. Shows why an apparently good schedule has no interpretable advantage until the reference is declared. | Reference-schedule comparisons and sign examples. |
| VIII.5 | **One Objective Is Not Enough** | Defines total EBU, peak distortion, recovery time, unmet need, resource use, resilience, fairness, autonomy, uncertainty, and coordination cost. Uses Pareto frontiers where no single scalar is justified. | Metric dashboard and Pareto plots. |
| VIII.6 | **Sequence, Timing, and Scheduling** | Tests order, start-time offsets, batching, maintenance windows, and shared capacity. Connects schedule optimization to many-action interaction without assuming that maximum simultaneity is best. | Gantt-like schedules, capacity traces, and optimality counterexamples. |
| VIII.7 | **Phase Distribution and Peak Reduction** | Studies whether shifting action phases reduces peaks or causes harmful delay. Defines phase only where periodic or quasi-periodic structure exists. | Phase sweeps, peak maps, and phase-response curves. |
| VIII.8 | **Provider Placement and Geometry** | Compares centralized, distributed, near-need, near-source, and hybrid placement under transport, response-time, capacity, and failure constraints. | Spatial layouts and placement trade-off surfaces. |
| VIII.9 | **Topology Comparison Under Common Rules** | Compares line, ring, hub, lattice, modular, small-world, hierarchical, recursive, distributed, learned, and circuit-inspired graphs under identical objectives and constraints. No attractive topology or electrical analogy is privileged in advance. | Common-benchmark topology panels and performance tables. |
| VIII.10 | **Propagation, Delay, and Causal Reach** | Tests how disturbances and actions propagate through edges with distance-dependent or state-dependent delays. Defines causal reach, distinguishes propagation from simultaneous correlation, and separates valid lumped-network models from distributed or time-varying cases that require richer field equations. | Space-time plots, delay-versus-distance tests, and lumped-versus-distributed failure examples. |
| VIII.11 | **When the Word “Wave” Is Earned** | Requires propagation, distance-dependent delay, amplitude and phase, reproducible reinforcement or cancellation, and identifiable modes before calling a pattern a wave. Provides non-wave counterexamples. | Space-time heatmaps, interference experiments, and falsifier checklist. |
| VIII.12 | **Graph Spectra and Coordination Modes** | Uses eigenvalues and eigenvectors as analytical tools for network modes, synchronization, bottlenecks, and recovery. Clearly separates mathematical modes from observed physical propagation. | Spectral plots and mode reconstruction tests. |
| VIII.13 | **Interaction Hierarchies Across Space and Time** | Extends pairwise and higher-order interaction diagnostics from Part VI to distributed schedules. Taylor expansions and interaction decompositions remain tools, not automatic causal allocations. | Pair/triple interaction maps and truncation-error plots. |
| VIII.14 | **Resilience, Failure, and Recovery** | Tests node loss, edge loss, delayed information, correlated failure, reserve exhaustion, and adversarial load. Compares efficiency under normal operation with graceful degradation. | Failure cascades, recovery trajectories, and resilience frontiers. |
| VIII.15 | **Scaling Laws, Saturation, and Regime Change** | Searches for linear, sublinear, superlinear, saturating, and threshold behaviour as system size grows. Fits alternatives and reports uncertainty rather than choosing a power law because it looks plausible. | Log-log and linear comparisons, residuals, and regime maps. |
| VIII.16 | **Sequences, Periodicity, and Recurrence Hypotheses** | Tests Fibonacci-like recurrences, other integer sequences, oscillations, and periodic schedules against null and alternative models. A recognizable sequence is a hypothesis, not evidence of a law. | Model-comparison plots and out-of-sample predictions. |
| VIII.17 | **Modularity, Hierarchy, Self-Similarity, and Fractal Hypotheses** | Compares modular, hierarchical, recursive, and self-similar organization. A fractal claim requires scale range, reproducible scaling, and predictive value beyond simpler alternatives. | Multiscale network plots and competing-model evidence. |
| VIII.18 | **Society-Scale Coordination Experiments and the Evidence Ledger** | Runs the strongest surviving models at larger scale with fairness, autonomy, privacy, uncertainty, and coordination cost included. States what coordination can inform before institutions choose how to use it. | Society-scale simulations, sensitivity analyses, and final claim ledger. |

### Non-negotiable research discipline

- Waves are not assumed.
- Fibonacci-like sequences are not assumed.
- Power laws are not assumed.
- Fractals are not assumed.
- Centralization is not assumed to be efficient.
- Decentralization is not assumed to be resilient.
- The best physical objective is not assumed to be the best institution.
- A circuit analogy is not assumed to be an electrical derivation of EBU.
- Kirchhoff closure, linear superposition, and equivalent-resistance formulae
  are not assumed outside their explicitly declared model conditions.

Candidate patterns must compete against simpler models using the same data, objectives, constraints, and validation rules.

**Closing transition to Part IX:** Part VIII identifies physically promising coordination mechanisms and their limits. Part IX must decide how an institution can quote, measure, guarantee, contest, and learn from those actions without converting a physical model into unaccountable social power.

---

## 10. Part IX - *The Action-Accounted Economy*

**Central question:** What would a complete action-accounted economy require, and how could it be introduced while preserving access, contestability, privacy, responsibility, and scientific honesty?

This is the final synthesis. It is not “EBU as another price.” It is an economy in which verified actions carry their physical consequences while institutional rules determine access, allocation, guarantees, and governance.

### 10.1 Binding quote and institutional residual programme

Before an action, the institution issues a quote from the declared state and action:

\[
Q_t=F(S_t,a_t).
\]

After execution, the actual represented transition is measured:

\[
A_t=G(S_t,a_t,S_{t+1}).
\]

The residual is:

\[
\boxed{\varepsilon_t=A_t-Q_t.}
\]

The physical result and the responsibility allocation must remain separate. If a compliant actor accepts a valid quote of \(+100\) EBU and the actual represented result is \(-256\) EBU, the institution can preserve physical closure as:

\[
\underbrace{+100}_{\text{binding actor settlement}}
+
\underbrace{(-356)}_{\text{institutional residual}}
=
\underbrace{-256}_{\text{actual represented effect}}.
\]

Honouring the quote does not erase energy, material, time, infrastructure wear, or ecological effect. It assigns the model or measurement error to the institution that chose the boundary, sensors, model, and guarantee.

The action record should support these states:

- `QUOTED`
- `ACCEPTED`
- `IN_PROGRESS`
- `SETTLED`
- `FAILED`
- `PARTIAL`
- `UNRESOLVED`

Fraud, sensor manipulation, material actor deviation, and knowingly experimental actions require declared procedures. They must not be hidden inside ordinary institutional model error.

### Detailed chapter structure

| Ch. | Working title | What the chapter does | Required evidence and figures |
|---|---|---|---|
| IX.1 | **From a Physical Action Equation to an Economy** | Summarizes the validated chain from Parts I-VIII and separates established science from the institutional choices still required. Defines the minimum evidence needed before broader adoption. | Series dependency map and claim-status ledger. |
| IX.2 | **Money and EBU Answer Different Questions** | Explains money as a system of claims, prices, and exchange while EBU records represented physical transition consequences. Shows why both can coexist during observation and transition phases. | Side-by-side transaction examples and non-equivalence table. |
| IX.3 | **An EBU Transaction Is Not Buyer-to-Seller Payment** | Reuses, without re-proving, actor closure to explain why several actors may receive positive lines and why actor balances need not be equal and opposite. Prevents EBU from being described as a conserved token. | Actor-line diagrams and monetary-closure comparison. |
| IX.4 | **The Complete Economic Action Record** | Integrates request, permission, quote, acceptance, commitments, child actions, route segments, measurements, physical settlement, actor lines, and residuals into one auditable record. | Full record schema and end-to-end lifecycle. |
| IX.5 | **Products and Services as Verified Supply Histories** | Replaces a single product label with a versioned chain of material, energy, transport, labour, maintenance, loss, and uncertainty records. Defines boundaries to prevent both omission and infinite regress. | Product provenance graph and complete/incomplete history examples. |
| IX.6 | **What Must Be Measured to Define the Field** | Specifies sensors, local state, calibration, uncertainty, timing, provenance, and missing variables. Explains why there is no single planetary EBU sensor. | Measurement architecture and calibration trace. |
| IX.7 | **The Binding Pre-Action Quote** | Treats the quote as a coordination interface and limited institutional guarantee. Defines truthful disclosure, accepted conditions, expiry, declared bounds, and the committed field. | Quote envelope, actor decision story, and contract-state diagram. |
| IX.8 | **Actual Settlement and the Visible Residual** | Measures the actual transition without rewriting the accepted quote. Defines the residual as evidence about institutional self-knowledge and preserves physical closure. | Quote-versus-actual distributions and residual ledger. |
| IX.9 | **Institutional Reserves, Nested Responsibility, and Risk Pooling** | Assigns ordinary model and measurement residuals to providers, higher institutions, or prospectively funded reserves. Tests reserve solvency and prevents unlimited hidden socialization of errors. | Nested account diagrams, reserve simulations, and insolvency cases. |
| IX.10 | **Failure, Deviation, Fraud, Unresolved Outcomes, and Appeals** | Defines settlement for no action, partial action, system-caused failure, actor deviation, manipulation, and uncertainty. Adds correction and appeal procedures without pretending to have written a complete legal code. | Decision tree, disputed-record examples, and audit trail. |
| IX.11 | **Privacy, Measurement Power, and Constitutional Safeguards** | Treats observability as a source of institutional power. Develops data minimization, local computation, purpose limitation, access controls, contestability, independent audit, and governance limits. | Information-flow diagrams and privacy-threat models. |
| IX.12 | **Necessary Actions with Very High Physical Burden** | Repeats the essential moral boundary: negative EBU records burden; it does not morally prohibit medicine, heat, disability support, or emergency rescue. | Necessary-action cases with separate physical and access ledgers. |
| IX.13 | **Scarcity, Impossibility, Priority, and Rationing** | Separates what is physically impossible from how an institution chooses priority. Compares transparent rationing rules without presenting any one rule as a physical theorem. | Feasibility frontiers and institutional-choice tables. |
| IX.14 | **Access, Guarantees, Pooling, Borrowing, Poverty, and Dependency** | Develops mechanisms that allow necessary action without rewriting its physical history. Tests unequal starting conditions, disability, care dependence, regional disadvantage, and catastrophic need. | Distributional simulations and access stress tests. |
| IX.15 | **Public Infrastructure, Common Services, and Stewardship** | Accounts for hospitals, water, transport, storage, knowledge, maintenance, and ecological restoration as continuing service systems. Separates ownership, use, stewardship, and public guarantees. | Infrastructure lifecycle accounts and stewardship examples. |
| IX.16 | **The Smallest-Action Incentive** | Develops the repeated question: how can the same genuine need be met with a better verified physical result? Tests prevention, maintenance, reuse, redesign, local production, and demand reduction without sacrificing the need. | Alternative-action frontiers and improvement loops. |
| IX.17 | **Initiative, Enterprise, and the Restaurant Case** | Demonstrates that EBU can recognize useful creation, innovation, coordination, labour, risk, and service. Decomposes founder, worker, supplier, customer, public-infrastructure, knowledge-common, and ecological contributions without assuming unlimited ownership reward. | Complete restaurant action history, participant lines, and counterfactual alternatives. |
| IX.18 | **Competition, Cooperation, Motivation, and Adaptive Preferences** | Treats motivation as plural: security, autonomy, mastery, recognition, belonging, curiosity, care, ambition, and personal benefit. Tests whether institutions change preferences without assuming universal altruism. | Behavioural study designs and competing institutional scenarios. |
| IX.19 | **Verification, Gaming, Rebound, Missing Burdens, and Contestability** | Tests Goodhart-like gaming, boundary manipulation, rebound effects, strategic reporting, omitted externalities, and institutional capture. Requires visible residuals and challenge mechanisms. | Red-team scenarios, missing-burden cases, and detection metrics. |
| IX.20 | **Why Organizations Might Adopt Observational EBU Today** | Defines low-risk adoption beside money: monitoring, procurement, maintenance, infrastructure comparison, and internal learning. Describes benefits of calculability without claiming a completed economy. | Pilot ladder, organizational dashboards, and adoption criteria. |
| IX.21 | **A Complete Functioning EBU-Economy Simulation** | Integrates needs, actions, quotes, groups, routes, coordination, access, reserves, privacy constraints, fraud, learning, and institutional failure in one reproducible Python model. It is a model test, not evidence that society will behave identically. | Full architecture, scenario results, sensitivity analysis, and failure catalogue. |
| IX.22 | **One Needs-Based Day, Predictions, Transition, and Future Actions** | Follows one day across household, hospital, enterprise, infrastructure, and ecology. States testable predictions, nonclaims, transition stages, constitutional limits, and the final research programme. | Narrative-system trace, final evidence ledger, and staged transition map. |

### 10.2 Enterprise and motivation boundary

EBU must not be described as a system in which a person cannot earn EBU by creating something useful. Initiative, innovation, coordination, labour, stewardship, and continuing service may be real contributions. The open problem is how to distinguish these contributions from an unlimited permanent reward for ownership alone.

The restaurant's total represented contribution is not identical to revenue or popularity. A provisional descriptive decomposition may include:

\[
V_{\mathrm{restaurant}}=
B_{\mathrm{nutrition}}+B_{\mathrm{hospitality}}+B_{\mathrm{community}}+B_{\mathrm{learning}}
-C_{\mathrm{resources}}-C_{\mathrm{labour\ burden}}-C_{\mathrm{ecology}}-C_{\mathrm{externalities}}.
\]

This is not yet an authoritative EBU equation. It is a checklist of contributions and burdens that must be reconciled with the established formalism.

### 10.3 Long-term destination statement

> Present evidence establishes a physical action-accounting foundation. Institutional use can expand as measurement, closure, safety, incentives, and social consequences are validated across progressively wider domains.

Part IX must present the long-term destination positively while making clear that physics does not select a constitution, a rationing rule, a founder reward, a privacy regime, or a political system.

---

## 11. Cross-volume concept allocation

| Concept | Primary home | Supporting references |
|---|---|---|
| Outcome sensitivity and instrument validation | Part IV | Part III Chapters 58-59 |
| Observation age, uncertainty, robust permission, Gate 1E | Part IV | Part III Chapter 60 |
| Recursive feasibility, invariance, stability, attraction | Part V | Part II Chapter 43; Part III 62.17-62.18 |
| Sequential telescoping and parallel interaction | Part VI | Part II Chapter 37; `SEQUENTIAL_PARALLEL_BRIDGE.md` |
| Network-potential closure, shared-source flow models, and circuit-analogy limits | Part VI | Part VIII extends storage, switching, propagation, and topology tests |
| Group receipts, causal identifiability, O3, batching | Part VI | Part II Chapter 35; Part III Chapter 51 |
| Dynamic routes, route actors, cooperation, adaptive infrastructure | Part VII | Part II Chapter 42; Part III 62.9-62.11 |
| Timing, placement, topology, waves, spectra, scaling | Part VIII | Parts VI-VII provide prerequisites |
| Binding quotes, residuals, reserves, enterprise, governance | Part IX | Parts III-IV and VI-VIII provide prerequisites |
| Access, poverty, disability, rationing, common services | Part IX | Part III 62.12-62.16 introduces the boundary |

The allocation rule is:

> A later book may summarize an earlier result in one bridge section, but it may not re-present an established explanation as a new theorem or new chapter programme.

---

## 12. Unified Python research framework

The committed `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` and
`UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` now govern this
programme. The project should use that one reproducible framework rather than
disconnected scripts with incompatible state definitions. The conceptual
inventory below is retained as the books' view of the framework; it does not
override the specification's exact types, interfaces, stages, or closed file
manifest.

### 12.1 Required scientific objects

- `SystemState` - physical stocks, burdens, commitments, clocks, and uncertainty.
- `DistortionModel` - declared \(D(X)\), units, parameters, and domain.
- `Action` - actor, provider, support, transformation, timing, resource use, and declared conditions.
- `Schedule` - sequence, start times, overlap, reservations, and comparator.
- `ExecutionEngine` - sequential, parallel, delayed, and stochastic transitions.
- `ProviderNetwork` - nodes, edges, types, capacities, efficiencies, delays, and failure states.
- `Quote` - epoch, assumptions, envelope, expiry, and guarantee.
- `Receipt` - child records, observed endpoint, physical EBU, actor lines, residuals, and status.
- `Ledger` - persistent quote, commitment, execution, verification, correction, and settlement history.
- `ExperimentConfig` - frozen worlds, arms, hypotheses, falsifiers, seeds, and analysis plan.
- `ProvenanceManifest` - code commit, configuration hash, environment, trace paths, summaries, and figures.

### 12.2 Required execution modes

- one action;
- sequential chains;
- overlapping and parallel groups;
- provider graphs and routes;
- schedules and delays;
- shared capacities and congestion;
- deterministic and stochastic dynamics;
- exact and uncertain observation;
- provisional and multi-horizon settlement;
- institutional residuals and reserves;
- adaptive networks and policy comparisons.

### 12.3 Reproducibility requirements

Every registered run should produce or reference:

- a frozen human-readable configuration;
- a canonical configuration hash;
- explicit random seeds;
- an immutable execution manifest;
- row-level traces;
- machine-readable summaries;
- figure-building scripts that read committed results;
- tests connecting equations to implementation;
- an evidence ledger connecting figures to claims.

The framework must be implemented only under its separately authorized I-1
through I-9 stages. Its specification and I-0 plan are accepted, but I-1
readiness remains blocked by the authority-hash reconciliation and PEP 517
packaging contradiction recorded in §§14-15. No code should be written until
those planning amendments are accepted.

### 12.4 Future circuit-inspired domain adapters

K1-K6 do not add an I-1 core type or silently expand the accepted framework
file manifest. They identify possible later Part VI/Part VIII domain adapters:

- a state-potential graph projection for path and loop closure;
- a typed resource-flow conservation model with stock and loss;
- a domain-owned constitutive branch relation between declared potential-like
  difference and flow;
- a finite-source capacity/internal-impedance model; and
- a switched-storage dynamic model with explicit memory and horizon.

Before any such adapter is implemented, the applicable framework extension
stage must freeze its types, units, numerical policy, capability class,
constitutive assumptions, falsifiers, and exact files. The adapter must fail
closed when the analogy's conditions do not hold. It must not expose a generic
“apply Kirchhoff” function, manufacture an action resistance, or treat EBU as
voltage, current, power, energy, or a conserved token.

---

## 13. Research and manuscript-generation sequence

The documentation foundation through the framework specification and I-0 plan
was accepted at `foundation-v0.1.0`. This circuit-network extension is later
planning work and is not retroactively part of that immutable tag. If accepted
and committed, its new raw hash must first be reconciled prospectively in the
framework specification and I-0 plan, both of which pin the pre-extension
hash. Only the resulting internally consistent authority set can be audited as
a documentation patch milestone such as `foundation-v0.1.1`; the existing tag
must not move.

### Phase A - Repository reconciliation and freeze

1. Confirm the repository root, branch, HEAD, status, and applicable `AGENTS.md` instructions.
2. Verify the Parts I-III manuscripts and their authoritative paths.
3. Reconcile this register with the repository roadmap and Git history.
4. Recover original Task 2, robust-P1C, Gate 1E, and Gate 2 scopes without redefining them from memory.
5. Verify all locked protocols, plans, hashes, and study status.
6. Map `ebu_resource_metabolism_chapter.tex` to its intended location.
7. Commit the reconciled planning register only after authorization.

### Phase B - Foundation notes

1. Maintain the committed `SEQUENTIAL_PARALLEL_BRIDGE.md` v0.2 after its independent equation and example review.
2. Maintain `DYNAMIC_COORDINATION_FOUNDATION.md` v0.1 with state, network, schedule, objectives, constraints, theorem candidates, and falsifiers.
3. Preserve the common notation and claim-status vocabulary.
4. Preserve the accepted unified Python framework specification and I-0 implementation plan.
5. Review this K1-K6 circuit-network extension as a prospective documentation patch; do not treat it as an observed result or framework implementation authority.

### Phase C - Execute studies in dependency order

1. Prospectively amend the framework specification and I-0 plan to recognize the accepted new hash of this books structure, then amend the I-0 packaging contract to select either an exact audited third-party PEP 517 backend and complete dependency lock, or an explicitly manifested stdlib-only in-tree backend with frozen hooks and package-data behaviour.
2. Implement and audit framework stages I-1 through I-9 under their separate authorizations; no stage inherits permission from the plan or from a previous stage.
3. Reconcile the Gate 1D-C incident and obtain separate authority for any correction or second official invocation.
4. Complete Gate 1D-C once under the applicable frozen design and new authority, without erasing the existing invocation history.
5. Align robust-P1C before making nonzero-uncertainty claims.
6. Complete Gate 1E in its repository-defined scope.
7. Develop the Part V constrained transition, viable-set, recursive-feasibility, invariance, Lyapunov, disturbance, and counterexample programme.
8. Preregister and execute the deterministic two-action sequential-parallel test matrix.
9. Prospectively specify, preregister, and test K1-K6, including path closure, common-terminal branches, finite shared sources, nonlinear superposition failure, switched storage, and loss-aware cancellation. These tests must compete against non-circuit explanations and retain every analogy limitation.
10. Execute many-action, comparator, shared-source, O3, group-receipt, allocation, batching, and delayed-settlement studies.
11. Execute dynamic route, actor, congestion, uncertainty, cooperation, fairness, and adaptive-infrastructure studies.
12. Execute timing, phase, placement, topology, propagation, spectral, resilience, scaling, and pattern-discovery studies, including only those dynamic circuit analogies that survive K1-K6.
13. Execute quote, residual, reserve, access, enterprise, behaviour, governance, fraud, transition, and complete-economy simulation studies.

### Phase D - Generate books only at evidence-complete checkpoints

1. Generate Part IV after Gate 1D-C, robust-P1C alignment, and relevant Gate 1E results are committed.
2. Generate Part V after the strongest constrained homeostasis theorem and adversarial simulations meet their declared threshold.
3. Generate Part VI after the sequential-parallel bridge, two-action matrix, K1-K6 circuit-network model suite, many-action core, group receipts, and O3 boundary are validated. The manuscript must include both the useful correspondence and the failed analogies.
4. Generate Part VII after route composition, actor closure, congestion, cooperation, fairness, and adaptive-network studies are complete.
5. Generate Part VIII after Dynamic Coordination, storage/switching and lumped-versus-distributed network comparisons, wave diagnostics, topology comparison, resilience, scaling, and pattern tests are complete.
6. Generate Part IX last, after the quote, residual, reserve, access, governance, behavioural, transition, and complete-economy programme can synthesize the surviving results.
7. Perform a coordinated audit of Parts I-III only after Parts IV-IX are stable.

### Phase E - Final series audit

- replace “trilogy” with the correct series description;
- add a two-page map of all nine parts;
- update the closing bridge in Part III;
- add precise forward and backward cross-references;
- create a cumulative symbol, theorem, evidence, and subject index;
- audit equations, units, signs, notation, citations, and claim status;
- audit every future chapter for overlap with Parts I-III;
- rebuild all result figures from committed data;
- record genuine errata without rewriting historical evidence.

---

## 14. Current stop conditions

1. Gate 1D-C remains scientifically **UNSTARTED**. One official runner invocation occurred and stopped during preflight; no receipt was created, no model state advanced, and the result directory remained absent. Its cumulative invocation count is one, and any correction or second invocation requires separate prospective authority.
2. This register does not authorize a Gate 1D-C rerun or any other experimental execution.
3. Any future Gate 1D-C incident-remedy or reauthorization task must begin by read-only verification of the complete applicable protocol, plan, compatibility contracts, implementation, incident evidence, artifact absence/presence, and cumulative invocation count.
4. Gate 1E remains untouched by Gate 1D-C and must retain its repository-defined scope.
5. Gate 2 remains paused and must not be redefined from memory.
6. The historical design-time commit `26de9f653c267c59d310f4642deaf710ab493a3e` is not an instruction to reset the repository.
7. No future result chapter may be written as if a preregistered study has already produced its intended result.
8. No theorem may claim more than its explicit assumptions support.
9. No allocation rule may be presented as a physically measured causal contribution unless identifiability evidence exists.
10. No wave, power law, Fibonacci recurrence, fractal, behavioural transformation, or economy-wide benefit may be assumed in advance.
11. No Kirchhoff law, circuit topology, superposition principle, or equivalent-resistance formula may be presented as validation or derivation of EBU. Each use must declare whether it is an algebraic correspondence, a domain model, or an explanatory analogy.
12. I-1 remains blocked until the new authority hash is reconciled in the framework specification and I-0 plan and the packaging contract is amended prospectively. `pyproject.toml` cannot silently rely on an implicit build backend while the framework dependency lock is declared stdlib-only.
13. No framework integration or I-1 branch should be created merely to work around that planning contradiction.

---

## 15. Immediate next deliverables

1. **Circuit-network planning review** - audit this one-file K1-K6 extension, its equations, chapter renumbering, page budgets, cross-volume placement, nonclaims, and dependency changes before committing it.
2. **Planning-amendment commit** - if the review passes, commit only this books-structure change. Do not tag yet, because the committed framework specification and I-0 plan will still pin its prior hash.
3. **Authority and packaging amendment** - prospectively update the specification and I-0 plan to adopt the new accepted books-structure hash, and revise the closed I-0 packaging contract to resolve the PEP 517 backend contradiction, including exact files, dependencies, package-data handling, hooks, validation, and threat controls. Do not begin implementation in that task.
4. **Foundation documentation patch checkpoint** - only after the complete authority set is internally consistent, audit and tag the exact accepted commit as `foundation-v0.1.1`; never move `foundation-v0.1.0`.
5. **I-1 implementation** - only after the amended plan and applicable foundation tag are accepted, recreate the framework branch setup from that exact accepted foundation commit and implement I-1 under separate authority.
6. **Deterministic parallel-testing specification** - later incorporate M1-M9 and K1-K6 with exact models, expected outcomes, comparators, tolerances, and falsifiers before any circuit-inspired scientific execution.
7. **Gate 1D-C incident remedy and reauthorization** - remain separate from framework and circuit-model work; no scientific execution is implied here.

---

## 16. Revision history

### 16.1 Regenerated architecture - 2026-08-12

This revision makes five structural corrections:

1. It changes the future reading order to IV measurement, V time, VI multiple actions, VII distance, VIII coordination, IX economy.
2. It consolidates duplicated distance/gravity/Fermat/Bellman chapters into one route-foundation bridge.
3. It gives every future chapter a specific purpose, evidence requirement, and transition role.
4. It integrates the complete sequential-parallel bridge, including comparator-relative interaction, nonlinear cross-term correction, group receipts, allocation limits, batching, and delayed settlement.
5. It preserves binding quotes, residuals, reserves, enterprise, adaptive preferences, access, privacy, and governance inside the final economic synthesis rather than allowing any one programme to replace the purpose of Part IX.

This is now the preferred handoff architecture, subject to repository reconciliation and later evidence-driven revision.

### 16.2 Circuit-network extension - 2026-08-13

This extension:

1. updates the authority register from Bridge v0.1 to the committed Bridge v0.2, Dynamic Coordination v0.1, framework specification v0.1, and I-0 plan v0.1;
2. identifies the exact potential-difference correspondence between sequential EBU telescoping and Kirchhoff-style path closure while refusing an electrical derivation claim;
3. adds K1-K6 for state-potential closure, common-terminal branches, finite shared sources, nonlinear response, switched storage, and loss-aware cancellation;
4. adds one dedicated Part VI chapter, shifts its later chapter numbers, and revises the Part VI and Part VIII word, figure, and page budgets;
5. carries only the appropriate flow, storage, switching, topology, and propagation questions into Parts VII-VIII;
6. records a future adapter boundary without expanding I-1 or the closed framework file manifest;
7. makes the K1-K6 specification and falsification programme a prerequisite for the relevant Part VI and Part VIII manuscript claims; and
8. replaces stale immediate deliverables with the authority-hash reconciliation, documentation-patch, and packaging-amendment prerequisites discovered after `foundation-v0.1.0`.

The extension is planning authority only after review and acceptance. It does
not alter the committed Bridge, framework specification, I-0 plan, Gate 1D-C
sources, or any scientific result.
