**Stage A does not justify declaring the project dead. It also does not establish the project’s central promise of reliable, self-sustaining homeostasis.** It establishes a narrower, useful result: the implemented accounting, affordability and demand-serving mechanisms operate in the registered world, while recovery remains policy-dependent.

The attachment contains the **Gate-4 specification**, not a completed Gate-4 report. I therefore performed the interpretation audit directly. I verified the pinned publication commit `2c4b71d…`, tree `5afe397…`, preregistration identity and registered outcome counts from the committed artifacts. I did not independently review the separate Gate-1–3 reports, which were not supplied.

No files changed and no experiments ran.

## A. Supported claims

**[STRONGLY SUPPORTED]** The published results support the following bounded statements. “Strongly supported” here concerns these recorded episodes—not generalization to other economies.

| Candidate claim                      | Evidence                                                                                 | Strongest warranted status   | Surviving explanation                                       | Allowed wording                                                                   | Forbidden wording                                           |
| ------------------------------------ | ---------------------------------------------------------------------------------------- | ---------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| A1 recovery occurs                   | Control, random and aligned returned in 64/64 episodes each                              | DESCRIPTIVE ONLY             | Small world and demand-menu geometry                        | “These arms recovered in these episodes.”                                         | “Recovery is guaranteed.”                                   |
| Aligned restores rapidly             | All aligned returns took two transitions                                                 | SUPPORTED WITH QUALIFICATION | Explicit maximization of EBU plus favorable geometry        | “The declared greedy rule attained the fixture’s two-step bound.”                 | “EBU creates generally optimal behavior.”                   |
| Hostile fails to recover             | No return within 32 transitions in 64 episodes                                           | DESCRIPTIVE ONLY             | Selection rule, plateaus, menus and finite horizon          | “Hostile did not recover within the horizon.”                                     | “Hostile can never recover.”                                |
| Random recovery needs EBU            | Control also recovered in 64/64 A1 episodes                                              | NOT SUPPORTED                | Physical demand and random action already permit recovery   | “The affordability gate was not necessary for these observed control recoveries.” | “EBU is necessary—or universally unnecessary—for recovery.” |
| A2 affordability gate is operational | Identical opening fixture; constrained arms have zero affordable plans; control executes | STRONGLY SUPPORTED           | Zero balances and negative receipts, intentionally selected | “The gate blocks these otherwise executable plans.”                               | “Blocking this service is socially desirable.”              |
| A3 lifecycle operates                | All orders served at epoch 3; tracked deficits subsequently closed                       | STRONGLY SUPPORTED           | Declared prelude, menus and narrow endpoint                 | “The registered lifecycle completed under each arm.”                              | “Every arm restored the whole system.”                      |
| Capacity accounting closes           | Exact recorded receipts, balances and telescoping                                        | STRONGLY SUPPORTED           | Settlement implements the accounting identity               | “These records obey the identity.”                                                | “Accounting closure guarantees stability.”                  |
| EBU induces cooperative incentives   | Policies are programmed, not learned or chosen by economic actors                        | NOT SUPPORTED                | Directly imposed selection rules                            | “Behavior differs under the declared policies.”                                   | “Self-interested actors will become restorative.”           |
| Equilibrium is accessible            | Earlier exhaustive accessibility result                                                  | SUPPORTED WITH QUALIFICATION | A property of the declared action graph                     | “Accessibility and policy realization are separate.”                              | “Stage A proves every actor reaches equilibrium.”           |
| Long-run homeostasis follows         | No registered long-run restoring-tendency test                                           | NOT SUPPORTED                | Finite, isolated episodes                                   | “Long-run behavior remains unresolved.”                                           | “Future survival is secured.”                               |

These limits follow directly from the [frozen protocol, especially §§7–9](https://github.com/konrazem/ebu/blob/2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32/DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md).

## B. Rejected overclaims—and important corrections to the audit framing

### 1. Aligned success is not an incentive theorem

**[STRONGLY SUPPORTED]** `ebu_aligned` explicitly selects the affordable plan with greatest EBU. With fixed potential, that selects the greatest immediate potential reduction among those plans. The selection rule is supplied by the researcher; the experiment does not explain why a real actor would choose it. See the [policy implementation](https://github.com/konrazem/ebu/blob/2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32/demand_driven_ebu/policies.py).

**[SUPPORTED WITH QUALIFICATION]** The two-step return is nevertheless meaningful as a mechanism demonstration. Geometry does not force every policy to take that path—the hostile arm does not. What is demonstrated is **this rule operating on this geometry**, not either factor in isolation.

### 2. A3’s endogenous baseline does not automatically destroy causal interpretation

**[SUPPORTED WITH QUALIFICATION]** The arms begin from the same declared initial conditions. Their different arrival states and balances are consequences of the policy applied during the prelude.

Therefore:

- A full-episode policy contrast can have a mechanistic interpretation within the model.
- It cannot isolate a **post-arrival** policy effect while pretending arrival states and balances were held equal.
- Stage A still supplies no preregistered inferential comparison or general treatment-effect estimate.

Calling all A3 comparisons “invalid because the baselines differ” would be an overcorrection.

### 3. A3 service is not universally dependent on previously earned reserve

**[STRONGLY SUPPORTED]** The registered candidate table for `A3|ebu_random|k=10` provides a direct counterexample:

- Arrival state: `(5,4,3)`.
- Plan: `B→C@1`.
- Post-state: `(5,3,4)`.
- Receipt to B: **0**.
- The plan serves the economic order and progresses C’s existing physical deficit.

That particular plan requires no positive prior balance. This is arithmetic on a saved candidate table, not a new simulation. Consequently, “earned reserve financed every A3 service” is too strong. Other recorded plans genuinely require prior owner balances.

### 4. The control is not “an economy without EBU valuation”

**[STRONGLY SUPPORTED]** Control still has EBU valuations and signed shadow accounting. It bypasses affordability and selects uniformly over plans. Its cleanest contrast is with **`ebu_random`**: the same random-selection rule, with versus without the affordability constraint.

Comparing control directly with aligned changes **both** affordability and selection. It cannot identify either effect alone. See [capacity accounting](https://github.com/konrazem/ebu/blob/2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32/demand_driven_ebu/capacity.py).

### 5. Plan multiplicity is a declared sampling property, not automatically a defect

**[STRONGLY SUPPORTED]** I confirmed the **82/256** A3 menus with four plans and three physical outcomes: nine control, nine random and 64 hostile.

**[SUPPORTED WITH QUALIFICATION]** Uniform-over-plans is not uniform-over-physical-states. Moreover, the two plans reaching the same physical state can produce **different owner receipts**, so they are not duplicates of the complete economic outcome.

This does not invalidate Stage A or automatically require changing Stage B’s policy. It requires an explicit choice of what the random policy represents. No retrospective reweighting is warranted.

## C. Surviving alternative explanations

**[SUPPORTED WITH QUALIFICATION]** Here, “survives” means the explanation remains compatible with the evidence—not that its separate causal contribution has been measured.

| Explanation                                                                      | Assessment                                                                                                             |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Three-cell topology, conserved total 12, quanta `{1,2}`, fixed Gaussian geometry | **FULLY SURVIVES:** all outcomes are conditional on this environment.                                                  |
| Menu asymmetry, irredundancy and plateau structure                               | **FULLY SURVIVES:** these determine which restorative, neutral and damaging choices exist.                             |
| Explicit policy extrema                                                          | **FULLY SURVIVES:** immediate preferences are programmed; successful recovery is not emergent actor motivation.        |
| Zero initial reserve                                                             | **FULLY SURVIVES:** it is central to A2’s blockade. The gate is real, but usefulness is not established.               |
| Finite horizon                                                                   | **PARTLY SURVIVES:** it limits claims about eventual recovery; it does not erase the observed 32-transition nonreturn. |
| Random plan multiplicity                                                         | **FULLY SURVIVES:** it shapes the random policy’s outcome probabilities, without invalidating that declared policy.    |
| Deterministic fixture design                                                     | **FULLY SURVIVES:** 64 seeds do not constitute 64 different environments.                                              |
| “The gate is merely decorative bookkeeping”                                      | **REJECTED BY EVIDENCE:** A2 shows it changes whether an executable action occurs.                                     |

## D. Stage-A scientific interpretation

**A1 — [DESCRIPTIVE ONLY].** The declared policies produce different recovery trajectories in one recovery fixture. Aligned reaches equilibrium quickly; hostile does not within the horizon; random and control recover in all recorded replicates. “Random lies between aligned and hostile” is, at most, a description of these return outcomes—not a general ordering of policy quality.

**A2 — [STRONGLY SUPPORTED].** Zero-balance affordability blocks the registered negative-EBU service plans. This demonstrates enforcement, not desirability, long-run service adequacy or restoration.

**A3 — [STRONGLY SUPPORTED].** The economic-service → physical-consequence → tracked-deficit-closure lifecycle operates in the registered episodes. Closure indices **5, 6 and 7 are post-state indices**, under the frozen convention. No tracked-closure event is horizon-censored, but sustained closure and equilibrium recovery remain different questions.

**Overall — [SUPPORTED WITH QUALIFICATION].** Stage A supplies P-level observations—affordability and actor-policy behavior. It neither re-proves L, the equilibrium location, nor converts R, physical accessibility, into a recovery guarantee. Its internal interpretability survives its small scope; its external validity is not established.

### What this means for the project

**[SUPPORTED WITH QUALIFICATION]** Continuing research is justified, but claiming that EBU already makes arbitrary actors reliably restorative is not. The hostile results are substantive negative evidence against that stronger reading, not an inconvenience to repair away.

**[NOT SUPPORTED]** Neither “the project is dead” nor “the central economic mechanism is proven” follows from Stage A. Exact accounting, enforceable affordability and reliable homeostasis are three different achievements. Stage A demonstrates the first two in scope; it leaves the third unresolved.

**GATE 4 CONDITIONAL PASS — Stage A supports fixture-specific mechanism and behavioral interpretation, not demonstrated incentive compatibility, general restoring tendency, or long-run stability.**

**READY FOR SCIENTIFIC GATE 5 — FINAL STAGE-A DISPOSITION**
