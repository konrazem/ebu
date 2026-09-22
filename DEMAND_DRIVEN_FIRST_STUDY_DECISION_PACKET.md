# First demand-driven registered study — decision packet

**Status: DECISION PACKET. NOT A PREREGISTRATION, NOT FROZEN, NOT
AUTHORIZED.** No seed is derived, no hypothesis is registered and no execution
is permitted by this document. Its purpose is to name the choices that are
genuinely scientific so that none of them is made silently inside an
implementation.

Prerequisite reading: `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md`,
`DEMAND_DRIVEN_MODEL_FINDINGS.md`,
`LEGACY_ARBITRARY_ACTION_STRESS_MODEL_RECLASSIFICATION.md`.

---

## 1. The question the study would ask

> Does the demand-driven EBU economy exhibit a persistent restoring tendency
> toward the declared physical reference under coexisting economic and
> physical demand?

Measured with the restoring-tendency objects already defined and carried over
unchanged: `dV_ext`, `dV_actor = -E`, `dV_total`, the drift objects `D_A` and
`D_T`, and `H95`/`H99` as **occupancy diagnostics only**, never as viability
or failure boundaries.

The study must **not** be run until the questions in §3 are answered, because
each of them can change the answer.

## 2. What is already settled and needs no decision

| item | decided | where |
|---|---|---|
| economic admission policy | random compatible-subset admission, EBU-blind | contract §4 |
| actor policies | aligned, random, hostile | contract §8 |
| comparator | no-EBU random plan selection over the **same** admitted demand components | contract §8 |
| capacity semantics | V1, unchanged | contract §8 |
| service contract | complete service only | contract §3 |
| no scheduler, no queue, no priority | frozen | contract §5 |
| loss baseline | `eta = 1` | contract §13 |
| stream separation | four counter-addressed streams | contract §12 |
| numeric policy | exact rational, tolerance 0 | implementation |

Explicitly **out of scope** for the first corrected study, per contract
section 44: priority admission, market admission, reject-conflict admission,
and institutional admission rules. The mechanism must not depend on which
admission policy is in force, and testing that dependence is a later study.

## 3. Unresolved scientific load parameters

These are real choices. Each row must be decided by declaration before
freezing, and none may be inferred from a favourable local outcome.

### 3.1 Economic arrival law

| parameter | why it is scientific | candidate range |
|---|---|---|
| **quantity distribution** | sets how often a request exceeds what exists, and therefore the scarcity-rejection rate. Economic quantities are **additive** across orders, so several small requests at one destination can be jointly unserviceable while each is serviceable alone | a finite declared alphabet; at least one quantum reachable by a single action and at least one beyond the plan-size cap |
| **arrival frequency** | sets the ratio of economic to physical obligations, which is the central exposure of the study | per-epoch Bernoulli rate; suggested factor levels `1/8`, `1/4`, `1/2` |
| **destination distribution** | see finding F-3: concentrating demand on nodes that never earn produces unaffordability that is an artefact of the distribution, not the mechanism | uniform over stock nodes, versus a declared skewed alternative; **at least one of each** |
| **number of simultaneous arrivals** | the admission rule only does anything when arrivals can conflict; with one slot per epoch, admission is a formality | at least 2 slots, so inclusion-maximal subsets can be non-trivial |
| **resource types** | one resource cannot exhibit independent components; two disjoint resources is the minimum that tests contract §19 | 2 resources on disjoint node sets, plus optionally a shared-node pair to exercise account coupling |

### 3.2 World and disturbance

| parameter | note |
|---|---|
| cells per resource, topology | the registered stress world used 3 cells complete; keeping it eases comparison but is not required |
| reference and scales | must be declared synthetic with no real-world calibration |
| transfer quanta and plan-size cap | jointly determine what "complete service" can reach; F-2 shows the cap can create a recurrent level above the floor |
| disturbance frequency and quantum | the external deviation term in the capacity-source identity; must be separable from the arrival rate |
| horizon and replicates | must be chosen against a declared power argument, not copied from the stress study |

### 3.3 Decisions forced by the findings

These are not optional; a study frozen without them cannot be interpreted.

1. **Stuck-component reporting (F-1).** The fraction of epochs in which a
   component has an unserviceable member must be a declared reported metric.
   Without it, a run that froze early and a run that regulated well can produce
   similar aggregate occupancy.
2. **Floor-relative restoring tendency (F-2).** If any arm is lossy, the
   reference is unreachable by construction and restoring tendency must be
   redefined against the reachable floor. That definition does not exist.
   Simplest resolution: keep the first study lossless and defer loss entirely.
3. **Per-owner capacity reporting (F-3).** Aggregate `B_total` is insufficient;
   the distribution across owners must be reported, because affordability binds
   per owner.
4. **Capacity-regime reporting.** Carried over from the case library's
   mandatory rule: any mechanism with an account layer must report at at least
   two declared capacity regimes, because a single regime was provably
   insufficient to characterise V1 in the stress model.
5. **Induced admission marginals (audit correction 5).** Uniform choice over
   inclusion-maximal compatible subsets is not uniform over demands. The
   per-demand marginal admission probability induced by the declared arrival
   law must be reported, not assumed flat.
6. **Search completeness rule (auditor 2, disposition 5) — RESOLVED by the
   Study-1 freeze, option 1.** The requirement stands as written: the study
   must declare, outcome-blind and before execution, either a cap proved
   sufficient or an explicit computational-failure rule, and **raising the cap
   until an observed rate looks negligible is not permitted.** Study 1 takes
   the first branch and proves it rather than observing it: domain condition
   16 requires `max_plan_size >= len(usable_routes)`, so
   `SEARCH_INCOMPLETE_AT_PLAN_CAP` is zero by construction and
   `study_one.require_domain` refuses any world where it is not. The decision
   that remains is only *which world* Stage B uses; it must pass that check.
   See `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` §4a and §4b.
7. **Undecided-search disposition — RESOLVED by the Study-1 freeze.**
   `SEARCH_UNRESOLVED` in a registered Study-1 job is a **computational
   integrity failure**: the entire job is invalid, the trajectory does not
   continue, the epoch is not excluded, nothing is resampled and no seed
   changes; the implementation is corrected and the identical job is rerun.
   Domain condition 17 makes it impossible in the first place, by requiring
   the complete plan space to fit inside the exhaustive budget.
   `EconomyRun(registered=True)` enforces both.
8. **Study-1 domain conformance.** Every world used by a registered Stage-A or
   Stage-B job must pass `study_one.require_domain`. `sandwater-v1` does not;
   neither does any lossy or capacity-bearing fixture. Choosing the Stage-B
   world is therefore also a domain decision. See
   `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md`.

## 4. Proposed arm structure, for decision

| factor | levels |
|---|---|
| actor policy | aligned, random, hostile, no-EBU comparator |
| arrival frequency | 3 levels (§3.1) |
| destination distribution | 2 levels (§3.1) |

Nested coupling is recommended, exactly as adopted for the homeostasis study:
one counter-addressed raw arrival process shared across frequency levels, with
each level thresholding the same per-epoch variate so the sparse schedule is a
subset of the dense one. This isolates the causal effect of arrival frequency
and removes schedule mismatch from the comparison. Frequency must then be
absent from the seed preimage.

### 4.1 Comparison contract — corrected

An earlier version of this packet required the comparator to see the **same
admitted demand components** as the EBU arms. **That requirement is
withdrawn.** It is unsatisfiable in a closed loop: admission reads the physical
state, and prior actor behaviour puts different arms in different states, so
identical admitted sets could only be produced by feeding one arm's admission
decisions to another.

The registered study will instead use:

> **identical exogenous E-demand arrival streams across arms, with endogenous
> admission.**

Arrivals are a pure function of `(seed, epoch)` and are therefore identical
across arms by construction — the rehearsal confirms 404 identical arrivals in
every arm. Admission may differ, and those differences are legitimate
closed-loop outcomes, not confounds. Admission remains EBU-blind: it inspects
no EBU value, no capacity balance and no future receipt.

**Reporting requirement.** All comparisons are reported over the **common raw
arrival set**, never over admitted demands alone. An arm that admits little and
serves all of it would otherwise score perfectly. Each incoming demand carries
a lifecycle state, and all of them must be reported:

`ARRIVED`, `ADMITTED`, `REJECTED_PHYSICAL_SCARCITY`, `REJECTED_INCOMPATIBLE`,
`SERVED`, `ADMITTED_BUT_UNRESOLVED_PHYSICAL`, `ADMITTED_BUT_EBU_UNAFFORDABLE`.

The admitted-only service rate may be reported as a secondary diagnostic. It
may never be the primary whole-system performance comparison.

## 5. Inferential plan — to be compact

Predefine one primary endpoint and a small secondary battery; report effect
sizes first; do not create dozens of independent p-values; do not summarize
everything as one "EBU score". The primary endpoint must be a physical-state
quantity and must exclude every account quantity, as in the previous mission.

The primary endpoint is **not yet chosen**.

One stale inference is corrected here. The endpoint-saturation theorem's
hypothesis — forcing amplitude equal to the action quantum, so exact reversal
is always uniquely maximal — does **not** hold in the corrected model, where
plans are multi-action and overshoot is permitted. That means the theorem no
longer applies, so the aligned arm is not trivially perfect by construction.
It does **not** by itself make `O95` unsuitable: endpoint suitability depends
on what the study intends to measure, not on whether some earlier theorem
happens to apply.

The endpoint must therefore be chosen from the scientific question before
registered execution, and outcome-blind. It is deliberately not chosen in this
packet.

## 6. Readiness

| gate | state |
|---|---|
| corrected model implemented | **yes** — `demand_driven_ebu/`, identity recorded in the final report |
| independent audit defects corrected | **yes** — all five, see `DEMAND_DRIVEN_AUDIT_CORRECTION_HANDOFF.md` |
| exact conformance passing | **yes** — 935 assertions, 0 failures, tolerance 0 |
| closed-cycle theorem proved and verified | **yes** |
| small local rehearsal run | **yes** — deterministic replay, all residuals 0 |
| Study-1 physical domain frozen and machine-checked | **yes** — `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` |
| exhaustive search completeness proved for the domain | **yes** — Theorem P; `SEARCH_UNRESOLVED` impossible |
| the decomposition-free **progress** reference established as the feasibility authority | **yes** — Theorem D, gated epoch by epoch at four levels |
| sampling unit frozen as the canonical plan identity | **yes** — outcome probability carries plan multiplicity |
| Stage-A fixtures chosen | **no** — `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` §4, A1–A4 |
| arrival law declared | **no** — §3.1 |
| findings-forced decisions taken | **no** — §3.3 |
| primary endpoint chosen | **no** — §5 |
| power argument | **no** |
| preregistration frozen | **no** |

> **Verdict: READY FOR DEMAND-DRIVEN STAGE-A/B PREREGISTRATION DESIGN, NOT
> READY for a registered behavioural experiment.**
> The machinery is ready and its search completeness is now proved rather than
> observed; the science is not. What is missing is a set of
> declared load parameters and one endpoint decision, none of which may be
> chosen from observed outcomes.

## 7. What must not happen next

- No registered execution without a frozen preregistration and a two-commit
  seed derivation.
- No selection of the arrival law from rehearsal trajectories.
- No reuse of the stress model's horizon, replicate count or endpoint by
  default merely because they exist.
- No AWS. Measured locally: the Study-1 world runs 3,200 epochs in 22.5 s
  *including* an independent brute-force reference enumeration, the
  affordability filter and all four verification levels every epoch,
  and the larger `sandwater-v1` rehearsal world runs 3,200 epochs in 180 s.
  A first study of this shape has no infrastructure argument for the cloud.
  (An earlier draft of this packet said "ten seconds"; that figure was wrong
  and is corrected here.)
- No registered Stage-A or Stage-B execution in the task that produced the
  Study-1 freeze. The freeze closes generality questions and proves
  completeness; it authorizes design work only.
