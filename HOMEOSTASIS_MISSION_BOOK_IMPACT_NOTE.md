# Homeostasis mission — book impact note

**No manuscript is edited by this note.** Mission section 32 permits only this
note, and only now that registered results exist. It records what the books
would have to say differently, and with what epistemic status, if and when a
separately authorized revision happens.

Every item is tagged with its class. The classes are not interchangeable and a
manuscript must not blur them:

- **DEFINITION** — a declared construction, true by stipulation.
- **THEOREM** — proved, with its assumptions.
- **CONFORMANCE** — software behaves as specified; says nothing about EBU.
- **EXPLORATORY** — measured, post-registered, not confirmatory.
- **REGISTERED** — measured under a preregistration frozen before execution.

---

## 1. New definitions the books do not currently carry

**DEFINITION — the homeostatic reference region.** Homeostasis as a
physical-state property: occupancy of a declared region around the reference,
excursion frequency, duration, severity, return behaviour and secular drift.
Explicitly *not* `V = 0` at every tick, and explicitly excluding every account
balance. Source: `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md`.

**THEOREM — effective dimension and the central chi-square reading.** One
conservation law on three cells gives `d = 2`, derived from the manifold and
the potential metric. `R^2 = 2V ~ chi^2_2` under the declared reference measure
**provided the reference satisfies the conservation law** — otherwise the
admissible set misses the origin and the statistic is noncentral. The books
should carry that proviso; it is the kind of clause that is easy to omit and
wrong to omit.

**THEOREM — exact quantiles, and a lattice collapse.** `r_p = -2 ln(1-p)` in
closed form for `d = 2`, enclosed in certified rationals. On the integer
lattice `R^2` is always even, so `H95` is exactly `R^2 in {0,2}` — *the
reference or one unit transfer away*, 7 of 496 admissible states. **A region
holding 95% of the reference measure holds 1.4% of the state lattice.** Any
manuscript reporting occupancy must state this, or a reader will badly
misjudge what a low number means.

## 2. Corrections to what the books may already imply

**REGISTERED, from Stage A, re-read.** The Stage-A recovery question was
answered and the answer was favourable: random EBU-affordable actors reached
`V = 0` in **128 of 128** replicates at a median of 3.5 ticks. Any text that
reads the Stage-A `REPEATED_CYCLING` classification as a recovery failure is
wrong; that classification describes continued mandatory action *after*
successful recovery. See `STAGE_A_RECOVERY_INTERPRETATION_CORRECTION.md`, which
also records what the correction does **not** repair — the primary endpoint's
structural `A_EBU <= 1` fault stands.

**THEOREM — a costless null action exists in the registered menu.** Three of
the 21 candidate groups are cancelling pairs: physically inert, free at the
reference, and away from it a **direct capacity transfer between owners** at
zero EBU cost. The V1 capacity exposition states that no direct capacity
transfer between owners exists. That claim is true of the *primitive
operations* and false of the *emergent behaviour*, and a manuscript should say
which it means. Source: `NET_ZERO_GROUPS_FINDING.md`.

**THEOREM — the aligned arm's result is a theorem, not evidence.** Where
forcing amplitude equals the action quantum and the actor moves after forcing
in the same tick, an EBU-maximizing actor returns the state to the reference
every tick, so `O95 = 1` identically. **No book may present the aligned arm's
perfect occupancy as an empirical demonstration that EBU produces homeostasis.**
It demonstrates that an actor who can exactly undo each disturbance, and is
incentivised to, does. Source: `ENDPOINT_SATURATION_FINDING.md`.

## 3. Registered results the books may now cite

All from `HOMEOSTASIS_REGISTERED_REPORT.md`: 1,536 jobs, 12.6 million
arm-ticks, integrity gate passed, all residuals exactly zero.

**REGISTERED — EBU affordability improves homeostasis under random actors,
reliably and slightly.** EBU-random beat the physical-random control in **64 of
64 paired replicates at every load and under both menu rules**. Occupancy
ratios 4.6× / 3.1× / 1.9× as load rises; absolute differences **+0.053, +0.030,
+0.014**, only the first clearing the registered meaningful effect size. Both
halves of that sentence must survive into any manuscript.

**REGISTERED — no policy achieved absolute homeostasis.** Every non-aligned arm
sits in the `not_localized` band. The best non-trivial occupancy anywhere was
0.0696. A book must not present relative improvement as localization.

**REGISTERED — the adverse result. EBU affordability is not a safety
mechanism against a deliberate adversary.** The gate bit hard — 7.02 affordable
groups of 21 against the control's 19.68 — and the hostile arm still reached
median `R^2` of 258–294 against the control's 126, with a median longest
excursion of 6,094 ticks of a 6,144-tick window. **Constraining a hostile
actor's menu did not constrain its damage; earning capacity from disturbances
funded it.** This is the single most important thing in this note for the books
to carry, because it is the result most likely to be quietly dropped.

**REGISTERED — the EBU arm is the one that degrades.** The divergence
signature fired in 24 of 64 EBU-random replicates against 1 of 64 controls.
Independently frozen, it reproduces the Stage-B capacity-growth falsification
on physical state.

**REGISTERED — the null-action loophole is immaterial to these conclusions.**
Running both menus as a factor moved occupancy by at most 0.006 and changed no
ordering.

## 4. Exploratory material, usable only as context

**EXPLORATORY — Stage B was an extreme disturbance regime.** Re-read through
the new region, both Stage-B arms spent 97–98% of the window outside `H95` and
the median replicate in both reached a simplex vertex. Post-registered; the
Stage-B registered conclusion is unchanged.

**EXPLORATORY — the Stage-B gate is a property of the poorest cell.** Carried
forward unchanged from the Stage-B disposition.

## 5. Conformance material that is not evidence

**CONFORMANCE — 477 assertions across six suites, 0 failures**, every exact
residual zero; the four-policy harness reproduces the registered Stage-A/B
harness tick for tick. **None of this is evidence about EBU**, and a manuscript
must not cite passing tests as scientific support.

## 6. What must not be written

- That EBU produces homeostasis. It produced a small reliable improvement under
  random actors and no absolute localization in any arm.
- That the aligned arm demonstrates the incentive works. That is Theorem A.
- That EBU affordability makes a system safe against hostile actors. The
  registered result is the opposite.
- That any of this generalizes past one three-cell world with a single quantum.
- That Capacity V2 has behavioural evidence. It has none.

## 7. Suggested placement, if a revision is authorized

The homeostatic region and its lattice collapse belong with the Gaussian
potential's introduction, since they change what "close to equilibrium" means
operationally. The four actor policies and the mandatory-action rule belong
wherever the books discuss actor freedom — the rule that an actor may not
preserve a system by refusing to act is a conceptual point, not a technical
one. The hostile result belongs wherever safety or adversarial robustness is
claimed or implied, and should be placed **before** any reader reaches an
optimistic reading of affordability.
