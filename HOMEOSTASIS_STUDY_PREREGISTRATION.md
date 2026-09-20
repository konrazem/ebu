# Homeostasis mission — registered study preregistration

**Status: FROZEN. Seeds are deliberately absent and are derived from this
document's own commit.**

This supersedes `HOMEOSTASIS_STUDY_PREREGISTRATION_CANDIDATE.md`, which is
retained unchanged as the pre-decision record. The four open decisions it
carried have been taken by the author and are recorded in section 12.

Nothing in this document may be altered after its freeze commit. If
implementation or results conflict with it, the conflict is reported; the
preregistration is not edited to make anything pass.

| | |
|---|---|
| protocol | `EBU-HOMEOSTASIS-v1` |
| study | `ebu-homeostasis-v1` |
| configuration | `cfg-3cell-homeostasis-v1` |
| configuration identity | `8d3c305b838ececa262563b235fa1b04dd12b0b09ac44108674440784c054889` |
| `homeostasis` code identity | `8b462401a00ed8624fbd649e460b9e44e6adf8ba749ca1fa3872e9a6ddd4c3c6` |
| `gaussian_harness` code identity | `a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55` |

---

## 1. The question

> Under continuing physical disturbance and mandatory physical action, does EBU
> keep the physical system statistically localized around its declared Gaussian
> homeostatic reference — and how does that change when actors are hostile,
> random, or aligned with the EBU signal?

Homeostasis is a **physical-state property**. No capacity, receipt, settlement
or deviation-ledger quantity enters any primary or secondary metric.

## 2. World, frozen

Unchanged from registered Stage A and Stage B: 3 cells, reference `(10,10,10)`,
scales `(1,1,1)`, conserved mass `M = 30`, complete directed topology,
action quanta `{1}`, max group size 2, potential
`EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1`, initial state `x*` with `B = 0`, `J = 0`,
exact rational arithmetic with tolerance `0`.

**Capacity V1, unchanged.** Capacity V2 is not substituted anywhere (mission 8
and 31). The question isolated here is actor response to the EBU signal, so
capacity semantics, the forcing law and the field model are all held fixed.

## 3. Homeostatic region, frozen

From `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md`: effective dimension `d = 2`
**derived** from the manifold and the potential metric; `R^2 = 2V ~ chi^2_2`
under the declared reference measure; `H95 = {R^2 <= 2 ln 20}` and
`H99 = {R^2 <= 2 ln 100}` decided against certified rational enclosures, which
collapse exactly on the integer lattice to `R^2 in {0,2}` and `R^2 in {0,2,6,8}`.
The physical boundary at `R^2 = 150` excludes under `3.3e-34` of reference
mass, so no constrained-quantile correction is applied.

## 4. Arms, frozen

| Arm | Policy id | Affordability | Selection |
|---|---|---|---|
| C | `control_random` | no | uniform over feasible |
| H | `ebu_hostile` | yes | `argmin E_G`, ties by actor RNG |
| R | `ebu_random` | yes | uniform over affordable |
| A | `ebu_aligned` | yes | `argmax E_G`, ties by actor RNG |

**Mandatory action.** If any nonempty physically feasible group exists, one
executes. No abstain, wait or no-op exists in any policy or in the menu.
`PHYSICAL_NO_ACTION_AVAILABLE` is recorded separately from
`AFFORDABILITY_BLOCKED`.

**No secondary benchmark arm**, per `HOMEOSTASIS_COMPARATOR_POLICY_REGISTER.md`.

## 5. Menu rule — registered as a factor

Both declared menus are run as a crossed factor:

- `with_net_zero_groups` — the registered 21-group Stage-A/B menu;
- `strict_physical_change` — the same menu with the three cancelling pairs
  removed structurally, before any policy sees them.

`NET_ZERO_GROUPS_FINDING.md` proves these three groups are physically inert,
free at the reference, and a costless capacity transfer between owners away
from it. Running both measures the loophole's effect rather than assuming it.
`null_action` is recorded per tick under both.

## 6. Disturbance loads — one shared process, thresholded

Frequency varies; amplitude does not. Quantum `q0 = 1` throughout.

```
p_force in { 1/4, 1/2, 1 }
```

**One counter-addressed raw forcing process is shared across all three loads.**
The per-tick uniform variate is drawn once, at an address that does not mention
the load, and each load is realized by **thresholding that same variate**
(residue modulo 4 below `4p`). Therefore

```
schedule(1/4)  subset of  schedule(1/2)  subset of  schedule(1)
```

and on a tick shared by two loads the raw edge and orientation proposal is
**identical**, because the edge is drawn at its own address which also does not
mention the load.

> **Registered rationale.** This is a common-random-numbers design adopted
> before execution specifically **to isolate the causal effect of forcing
> frequency**. Two loads differ only in which subset of one fixed disturbance
> stream is delivered, never in the disturbances themselves. This is why the
> load is deliberately absent from the seed preimage in section 10, a
> deliberate and recorded departure from mission section 24's literal listing.

**NULL_FORCING, unchanged from Stage B.** Per-arm admissibility: if the drawn
source holds less than `q0` **in that arm's state**, the draw is recorded and
not applied. No resample, no clip, no reversal, no substitution, no magnitude
change. Arms share raw draws, not applied forcing, and arm-specific
`NULL_FORCING` is **preserved as an observed consequence of arms occupying
different states** — it is data, not a defect.

## 7. Hypotheses — qualitative, registered before execution

Hypotheses, not expectations. **No hypothesis failure will cause the model to
be modified** (mission 14).

- **H1** `O95(A) > O95(R)` under at least one load.
- **H2** `O95(R) > O95(C)` under at least one load.
- **H3** `O95(H) < O95(R)` under at least one load.
- **H4** increasing load reduces `O95` in all four arms.

## 8. Primary endpoint and inferential plan, frozen

**Primary endpoint: `O95`**, the 95% reference homeostatic occupancy over the
analysis window, per replicate per arm. It is the sole primary endpoint, as
mission section 4 directs. No co-primary is registered.

> **Registered saturation finding — recorded before execution.**
> `ENDPOINT_SATURATION_FINDING.md` **proves** (Theorem A) that in this world
> the EBU-aligned arm has `O95 = 1` identically: forcing amplitude equals the
> action quantum and the actor moves after forcing within the tick, so exact
> reversal is always available, is the unique maximiser at `E_G = 1`, and is
> always affordable from zero capacity. Verified over 28,800 conformance ticks.
> The rehearsal also found the hostile arm at the floor.
>
> Therefore **`H1` is true before any tick runs**, the `A` versus `R` contrast
> is not empirical in this world, and `H` versus `R` is floor-limited. The
> study's genuine empirical content is `R` versus `C`. This is registered here,
> in advance, and must not be re-derived afterwards as a post-hoc explanation
> of any result.

**Effect size is reported first**, before any test: the median paired
difference in `O95`, with a distribution-free sign-based confidence interval
computed exactly from integer order statistics.

**Three contrasts, each load answered separately** (mission 13, 25):

1. `A` vs `R` — incentive validity
2. `R` vs `C` — robustness / stupid-proofing
3. `H` vs `R` — hostile safety

**Test:** exact two-sided paired sign test on the per-replicate `O95`
difference, reproducing the frozen Stage-B definition exactly. Arms are paired
within a replicate because they share seeds.

**Multiplicity:** Holm within each load over its three contrasts, family-wise
`alpha = 0.05`. Loads are not pooled; menus are reported separately. No
combined score is produced.

**Meaningful effect size:** `delta_meaningful = 0.05` absolute in `O95`.

> **Registered range caveat.** The exploratory Stage-B reanalysis found `O95`
> near 0.031 and 0.016 at `p_force = 1`. If this study reproduces that regime,
> a 0.05 absolute difference has little room to appear at the highest load, and
> a null result there may reflect measurement range rather than absence of
> effect. Registered before execution.

**Secondary metrics — descriptive only, no significance claim, no multiplicity
correction:** the full frozen battery of `homeostasis/metrics.py`, reported per
arm per load per menu. Mean/median/p90/p95/p99/max `R`; `H95` exits; time
outside `H95`; excursion count, duration and peak severity; return time;
proportion outside `H99`; late-window `O95` and mean `V` by block; and the
per-tick `null_action` rate. Median `R^2` is reported descriptively for all
arms and is **not** a primary endpoint.

## 9. Result categories, frozen

Deliberately not defined as `V != 0`.

**Relative regulation.** A contrast whose median paired `O95` difference
exceeds `delta_meaningful` with a Holm-significant sign test.

**Absolute homeostasis — descriptive bands, not a pass rule.** No pass
threshold is registered; mission section 15 warns against equating
`O95 >= 0.95` with a pass condition merely because the region is called "95%".

| Band | `O95` | Justification |
|---|---|---|
| localized | `>= 0.50` | the region contains the modal behaviour |
| partially localized | `0.20 – 0.50` | visited routinely, not where the process lives |
| not localized | `< 0.05` | the regime the Stage-B reanalysis found |

**Divergence.** Registered predicate per replicate: `O95` strictly falls across
all three late blocks **and** block median `R^2` strictly rises across all
three. Reported as the fraction of replicates satisfying it.

**Incentive failure.** `A` does not exceed `R` by `delta_meaningful` at any
load despite affordable restorative options existing, measured by the recorded
`n_affordable` and executed EBU sign.

## 10. Matrix, seeds and execution

```
2 menus x 4 policies x 3 loads x 64 replicates x 8192 ticks = 12,582,912 arm-ticks
1,536 independent deterministic jobs
burn-in 2048    analysis window 6144    three late blocks of 2048
```

No early stopping for any reason. `N` is not changed after results are seen.

**Seeds, materialized only after this commit.** For replicate `r = 0..63` and
stream `S` in `{FORCING, ACTOR}`:

```
seed = first 8 bytes, big-endian, of
       SHA256("EBU-HOMEOSTASIS-v1|<this commit sha>|<r:03d>|<S>")
```

**The load is absent from the preimage**, by the design of section 6. Seeds are
matched across all four policies, both menus and all three loads within a
replicate. No seed is manually selected or excluded, and no seed is regenerated
because a result is surprising.

**Execution host: local.** `AWS_EXECUTION_DISPOSITION.md` records that no AWS
execution path exists for this code and that mission section 21's equivalence
gate cannot be run. Jobs are independent and deterministic, so they may be
executed in parallel; `homeostasis/jobs.py` proves order-independence and
envelope-independence of every payload hash.

**Integrity gate before any aggregate interpretation (mission 28):** all 1,536
jobs present; no duplicate identity with conflicting payload hashes; both code
identities and the configuration identity matching; accounting, conservation
and nonnegativity residuals exactly `0` on every tick; no negative capacity in
the affordability arms; mandatory-action rule respected; no voluntary no-op; no
unregistered fallback. If integrity fails, partial results are not interpreted.

**Failure handling (mission 27).** A failed job is re-run under its exact
immutable identity, with no new seed and no parameter change. A retry producing
a different payload hash stops the run as a reproducibility failure.

## 11. Non-claims

- Passing conformance is not evidence about EBU.
- The rehearsal is non-confirmatory and selected nothing.
- The Stage-B reanalysis is exploratory and post-registered.
- A significant contrast is relative regulation, not absolute homeostasis.
- Theorem A means `H1` carries no empirical weight in this world.
- Nothing here licenses a claim about economies, institutions or real systems.

## 12. Decisions taken by the author before freeze

1. **Menu rule:** run both menus as a registered factor.
2. **Endpoint:** `O95` is the primary homeostasis endpoint; median `R^2`
   remains a descriptive secondary.
3. **Execution:** freeze and execute locally now.
4. **Load coupling:** one shared raw forcing process thresholded per load, with
   the load omitted from the seed preimage, to isolate the causal effect of
   forcing frequency.
