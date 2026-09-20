# Homeostasis mission — registered study preregistration CANDIDATE

**Status: CANDIDATE. Not frozen, not registered, not executed.**

One decision is open and it is the author's, not this task's: the menu-rule
question of `NET_ZERO_GROUPS_FINDING.md` section 5. Everything that does not
depend on that answer is specified below and implemented. When the answer is
given, section 11 lists exactly what changes and the packet can be frozen.

Local gates already passed: conformance (mission 18), rehearsal (19). AWS
equivalence (21) is blocked and reported in `AWS_EXECUTION_DISPOSITION.md`;
section 10 below registers local execution instead.

---

## 1. The question

> Under continuing physical disturbance and mandatory physical action, does EBU
> keep the physical system statistically localized around its declared Gaussian
> homeostatic reference — and how does that change when actors are hostile,
> random, or aligned with the EBU signal?

Homeostasis is a **physical-state property**. No capacity, receipt, settlement
or deviation-ledger quantity enters any primary or secondary metric.

## 2. World, frozen

| Item | Value | Source |
|---|---|---|
| cells | 3 | registered Stage A/B |
| reference `x*` | `(10, 10, 10)` | registered Stage A/B |
| scales `sigma` | `(1, 1, 1)` | registered Stage A/B |
| conserved mass `M` | 30 | registered Stage A/B |
| topology | complete directed graph, 6 edges | registered Stage A/B |
| action quanta | `{1}` | registered Stage A/B |
| max group size | 2 | registered Stage A/B |
| potential | `EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1` | unchanged |
| capacity | **V1, unchanged** | mission section 8 |
| numerics | exact rational, tolerance 0 | frozen G0 policy |
| initial state | `x*`, `B = 0`, `J = 0` | registered Stage A/B |

Capacity V2 is **not** substituted (mission sections 8 and 31). The question
isolated here is actor response to the EBU signal, so capacity semantics, the
forcing law and the field model are all held fixed.

## 3. Homeostatic region, frozen

From `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md`, derived not assumed:

- effective dimension `d = 2`, derived from the manifold and the potential metric;
- `R^2 = 2V ~ chi^2_2` under the declared reference measure;
- `H95 = { R^2 <= 2 ln 20 }`, `H99 = { R^2 <= 2 ln 100 }`, decided against
  certified rational enclosures;
- on the integer lattice these collapse exactly to `R^2 in {0,2}` and
  `R^2 in {0,2,6,8}`;
- the physical boundary at `R^2 = 150` excludes under `3.3e-34` of reference
  mass, so no constrained-quantile correction is applied.

## 4. Arms, frozen

Four core policies (mission section 7), identical in world, topology, forcing,
candidate generation, feasibility and mandatory-action rule:

| Arm | Policy id | Affordability | Selection |
|---|---|---|---|
| C | `control_random` | no | uniform over feasible |
| H | `ebu_hostile` | yes | `argmin E_G`, ties by actor RNG |
| R | `ebu_random` | yes | uniform over affordable |
| A | `ebu_aligned` | yes | `argmax E_G`, ties by actor RNG |

**Mandatory action.** If any nonempty physically feasible group exists, one
executes. No abstain, wait or no-op exists in the menu or in any policy.
`PHYSICAL_NO_ACTION_AVAILABLE` (no feasible group) is recorded separately from
`AFFORDABILITY_BLOCKED` (feasible but none affordable).

Per `HOMEOSTASIS_COMPARATOR_POLICY_REGISTER.md`, **no secondary benchmark arm
is included**: no existing comparator survives the audit, and the one serious
candidate is provably degenerate in this world.

## 5. Disturbance loads, frozen

Frequency varies; amplitude does not. Quantum `q0 = 1` throughout.

```
p_force in { 1/4, 1/2, 1 }
```

realized exactly by one uniform residue modulo 4 on the forcing stream at draw
index 2; the edge is drawn at index 0, which reproduces the Stage-B address.

**NULL_FORCING rule, unchanged from Stage B.** Per-arm admissibility: if the
drawn source holds less than `q0`, the draw is recorded and not applied. No
resample, no clip, no reversal, no substitution, no magnitude change. Arms pair
on common raw draws, not on common applied forcing.

## 6. Hypotheses — qualitative, registered before execution

These are hypotheses, not expectations, and **no hypothesis failure will cause
the model to be modified** (mission section 14).

- **H1** `O95(A) > O95(R)` under at least one load.
- **H2** `O95(R) > O95(C)` under at least one load.
- **H3** `O95(H) < O95(R)` under at least one load.
- **H4** increasing load reduces `O95` in all four arms.

## 7. Primary endpoint and inferential plan, frozen

**Primary endpoint:** `O95`, the 95% reference homeostatic occupancy over the
analysis window, per replicate per arm.

**Effect size is reported first**, before any test: the median paired
difference in `O95`, with a distribution-free sign-based confidence interval,
computed exactly from integer order statistics.

**Three contrasts, each load answered separately** (mission section 13 and 25):

1. `A` versus `R` — incentive validity
2. `R` versus `C` — robustness / stupid-proofing
3. `H` versus `R` — hostile safety

**Test:** exact two-sided paired sign test on the per-replicate `O95`
difference. Distribution-free, exact from integer binomial counts, matching
Stage A/B practice. Arms are paired within a replicate because they share
seeds.

**Multiplicity:** Holm within each load over its three contrasts, family-wise
`alpha = 0.05`. Loads are **not** pooled and no combined score is computed
(mission section 25). Total: nine tests, not dozens.

**Meaningful effect size:** `delta_meaningful = 0.05` absolute in `O95`.

> **Registered range caveat.** The exploratory Stage-B reanalysis found `O95`
> near 0.031 and 0.016 at `p_force = 1`. If the new study reproduces that
> regime, an absolute difference of 0.05 has little room to appear at the
> highest load, and a null result there may reflect the measurement range
> rather than an absence of effect. This is registered **before execution** and
> must not be re-derived afterwards as an excuse for a null.

**Secondary metrics — descriptive only, no independent significance claim and
no multiplicity correction:** the full battery of `homeostasis/metrics.py`,
reported per arm per load. Mean/median/p90/p95/p99/max `R`; `H95` exits; time
outside `H95`; excursion count, duration and peak severity; return time;
proportion outside `H99`; late-window `O95` and mean `V` by block.

## 8. Result categories, frozen

Per mission section 15, and deliberately **not** defined as `V != 0`.

**Relative regulation.** A contrast whose median paired `O95` difference
exceeds `delta_meaningful` with a Holm-significant sign test.

**Absolute homeostasis — descriptive bands, not a pass rule.** Mission section
15 warns against equating `O95 >= 0.95` with a pass condition merely because
the region is called "95%". No pass threshold is registered. Three landmarks
are registered for description only:

| Band | `O95` | Justification |
|---|---|---|
| localized | `>= 0.50` | the region contains the modal behaviour: the process is inside it more often than not |
| partially localized | `0.20 – 0.50` | the region is visited routinely but is not where the process lives |
| not localized | `< 0.05` | the regime the exploratory Stage-B reanalysis found |

**Divergence / loss of homeostasis.** Registered predicate, evaluated per
replicate: `O95` strictly falls across all three late blocks **and** the block
median `R^2` strictly rises across all three. Reported as the fraction of
replicates satisfying it, per arm per load. A majority of replicates satisfying
it is the registered signature of secular drift.

**Incentive failure.** `A` does not exceed `R` by `delta_meaningful` at any
load, despite affordable restorative options existing — measured, not assumed,
by the recorded `n_affordable` and the executed EBU sign.

## 9. Matrix and horizon, frozen

```
4 policies  x  3 loads  x  64 replicates  x  8192 ticks  =  6,291,456 arm-ticks
burn-in 2048    analysis window 6144    three late blocks of 2048
```

Unchanged from mission section 23 and from the registered Stage-B structure.
No early stopping for any reason, including reaching equilibrium or a
trajectory looking bad. `N` is not changed after results are seen.

## 10. Execution, seeds and integrity

**Execution host: local.** `AWS_EXECUTION_DISPOSITION.md` records that no AWS
execution path exists for this code and that section 21's equivalence gate
cannot be run. The matrix is roughly 2.4 hours of single-threaded CPU. The job
architecture is host-agnostic, so moving it later costs a hash comparison.

**Seeds (mission section 24).** Frozen without concrete seeds; derived after
the freeze commit as the first 8 bytes big-endian of

```
SHA256("EBU-HOMEOSTASIS-v1|<preregistration_commit>|<load_id>|<replicate:03d>|<STREAM>")
```

with `STREAM` in `{FORCING, ACTOR}`. Matched across all four policies and both
menu rules within a load and replicate, so arms are paired. No seed is
manually selected or excluded.

> **Recorded design alternative, for the author.** Section 24 lists the load as
> a seed input, and the rule above follows it, making the three loads
> independent processes. The harness also supports **omitting** the load from
> the preimage, which makes the schedules *nested* — every tick forced at 1/4
> is also forced at 1/2 and at 1 — a common-random-numbers design that would
> sharpen the load comparison of Q5 by removing schedule variation between
> loads. The nesting is implemented and conformance-tested. The literal rule is
> registered here; switching is a one-line change to the preimage and must be
> decided before the freeze, not after.

**Job identity and integrity (sections 22, 27, 28).** Every
replicate/policy/load/menu combination is an independent deterministic job
under `homeostasis/jobs.py`. Payload hashes are a pure function of job
identity; envelopes are excluded. A failed job is re-run under its exact
identity with no new seed and no parameter change; a retry producing a
different payload hash stops the run as a reproducibility failure. Before any
aggregate interpretation: all expected jobs present, no conflicting duplicate
payloads, all identities valid, accounting and conservation residuals exactly
zero, no negative capacity in the affordability arms, mandatory-action rule
respected, no voluntary no-op, no unregistered fallback.

## 11. The one open decision, and what it changes

`NET_ZERO_GROUPS_FINDING.md` establishes that three of the 21 registered
candidate groups are cancelling pairs: physically inert, always affordable at
the reference, and a costless capacity-transfer channel away from it. Mission
section 6 makes mandatory action *"central to the scientific interpretation"*,
and a costless null action defeats it in substance while satisfying it in form.

**Options, both implemented:**

- **`MENU_WITH_NET_ZERO`** — 21 groups, exactly the registered Stage-A/B world.
  Preserves comparability; keeps a costless null action in the menu.
- **`MENU_STRICT_PHYSICAL`** — 18 groups. Makes mandatory action bite; runs the
  comparison in a world that is not quite the registered one.
- **Both, as a registered factor** — doubles the matrix to about 4.8 hours and
  measures the loophole's effect directly rather than assuming it.

**What changes on the answer:** section 2's menu row, section 9's arm count if
both are run, and the seed preimage's coverage. Nothing else. `null_action` is
recorded per tick under every option.

## 12. Non-claims

- Passing conformance is not evidence about EBU.
- The rehearsal is non-confirmatory and selects nothing.
- The Stage-B reanalysis is exploratory and post-registered.
- A significant contrast is relative regulation, not absolute homeostasis, and
  the two are reported separately.
- Nothing here licenses a claim about economies, institutions or real systems.
