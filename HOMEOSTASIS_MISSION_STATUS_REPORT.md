# Homeostasis mission — status report

**No registered study has been executed. No registered scientific evidence
about EBU exists from this work.** Everything below is a theorem, a conformance
result, an exploratory post-registered re-reading of immutable Stage-B
artifacts, or a non-confirmatory rehearsal — each labelled.

Two of the mission's own stop conditions (section 33) were reached and are
reported rather than worked around.

---

## 1. Repository

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| start coordinate | `d300aa8c33f9f6dc62395db7ddc1640a52cec21d` |
| commits added | 9 |
| files changed | 22, **all additions** |
| working tree | clean |

**Immutability verified.** Zero changes to `gaussian_harness`, `capacity_v2`,
`books/`, `results/stage_a/`, `results/stage_b/`, both preregistrations, both
registered reports, and every Stage-A/Stage-B registry, executor and analysis
module. Tags `stage-a-preregistration` (`025eee1`) and
`stage-b-preregistration` (`4c826a9`) intact. A conformance check asserts
`gaussian_harness`'s registered code identity `a9158eef…` on every run.

## 2. Homeostasis definition (mission 2–5)

`GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md`, `homeostasis/region.py`.

- **Effective dimension `d = 2`, derived** from the state manifold and the
  potential metric — one conservation law on three cells. The derivation checks
  that the reference satisfies the law, because otherwise `R^2` would be
  noncentral chi-square and every quantile would be wrong; such a world is
  refused.
- `R^2 = 2V ~ chi^2_2` under the declared reference measure.
- Quantiles **derived in closed form, not tabulated**: `r_p = -2 ln(1-p)`,
  reduced to two `atanh` series with certified tails and enclosed in exact
  rational bounds about `1e-63` wide. Membership is exactly decided; an
  undecidable comparison refuses.
- **Assumptions and limits recorded:** the region defines geometry, not a pass
  rule; the reference distribution is continuous while the physical state is a
  coarse lattice; `d = 2` is specific to this world.
- **Truncation immaterial:** the physical boundary is at `R^2 = 150` against
  `H99` at `9.21`, excluding under `3.3e-34` of reference mass. No constrained
  quantile correction is needed.
- **Lattice collapse:** `R^2` is always an even integer, so
  `H95 <=> R^2 in {0,2}` and `H99 <=> R^2 in {0,2,6,8}`. `H95` is exactly *the
  reference or one unit transfer away* — 7 of 496 admissible states, 1.4% of
  the lattice while carrying 95% of the reference measure.

## 3. Policy implementation (mission 6–9)

`homeostasis/policies.py`, `homeostasis/harness.py`.

Four core arms — control-random, EBU-hostile (`argmin E_G`), EBU-random,
EBU-aligned (`argmax E_G`) — on one physical world, with Capacity **V1
unchanged** and no V2 anywhere in the programme (mission 8 and 31, verified).

- **Mandatory action:** no abstain, wait or no-op exists in any policy or in
  the menu. `PHYSICAL_NO_ACTION_AVAILABLE` is kept distinct from
  `AFFORDABILITY_BLOCKED`; both are reachable and tested.
- **Information boundary is structural:** the uniform selector takes an integer
  count and has no candidate, value, potential or balance in scope. Asserted by
  AST, not by convention.
- **Capacity does not change EBU measurement:** `value_group` has no ledger
  parameter, and `E_G` and per-action receipts are identical across four
  capacity vectors while affordability and projections differ.
- **Faithfulness to the registered harness:** EBU-random reproduces the
  registered Stage-A/B EBU arm and control-random reproduces its control, tick
  for tick over 48 ticks on identical seeds.

## 4. Existing evidence, re-read

**Stage-A recovery correction** (`STAGE_A_RECOVERY_INTERPRETATION_CORRECTION.md`).
First-hitting time was a *pre-registered* diagnostic, re-derived independently
from the 256 immutable artifacts and matching the frozen analysis: the EBU arm
reached `V = 0` in **128/128** replicates at a median of 3.5 ticks; the control
in 63/128. Under corrected first-hit semantics every EBU replicate is a
successful recovery. The note records what it does *not* do: it does not repair
the primary endpoint's structural `A_EBU <= 1` fault, does not make the
cross-arm contrast clean, and does not weaken Stage B.

**Stage-B exploratory homeostasis reanalysis**
(`STAGE_B_EXPLORATORY_HOMEOSTASIS_REANALYSIS.md`). Post-registered, not
confirmatory. Stage B was an **extreme** test: both arms spent 97–98% of the
window outside `H95` and the median replicate in *both* reached `R^2 = 600`, a
simplex vertex. The EBU arm was better on every measure (`O95` 0.031 vs 0.016)
without being localized in any absolute sense. Occupancy fell across late
blocks in 52/64 EBU replicates versus 24/64 controls — consistent with the
registered capacity-growth falsification, recorded as an observation, not a
test.

## 5. Local validation (mission 18–19)

**Six suites, 477 assertions, 0 failures**, every residual exactly `0`:

| suite | assertions | class |
|---|---|---|
| Local Gaussian foundation | 65 | static/pure |
| Local Gaussian harness | 68 | transition, opt-in |
| Capacity-V2 foundation | 61 | static/pure |
| Capacity-V2 harness | 28 | transition, opt-in |
| **Homeostasis foundation** | **146** | static/pure |
| **Homeostasis transition** | **109** | transition, opt-in |

**Rehearsal** (`results/rehearsal/`, REHEARSAL / NON-CONFIRMATORY): 192 runs,
393,216 ticks, 494 s, **replay deterministic**, worst residual across every run
exactly `0`. An earlier attempt was invalidated by its own integrity check when
the package changed mid-run; the run now pins code identity and fails loudly.

## 6. AWS (mission 20–22)

`AWS_EXECUTION_DISPOSITION.md`. **No AWS API, SSO or console call was made.**

What exists is one completed **non-scientific infrastructure rehearsal** from
2026-09-01 on the unmerged `aws/campaign-orchestration` branch. **No EBU
scientific code has ever executed on AWS**, no execution binding exists for
this code on any host, the Step Functions/Batch backend is a design, the `aws/`
tree is not at HEAD, and its branch forbids merging.

**Section 21's equivalence gate cannot be run: one of its two sides does not
exist.** This is mission stop condition 33.

The local half is complete: `homeostasis/jobs.py` separates job identity,
canonical payload and execution envelope, with the payload hash covering the
first two and never the third. Proven by conformance: payload hash is a pure
function of identity; retries are idempotent; reversed order and a different
executor, host, attempt and start time change nothing; the module imports no
clock, host or entropy source; a manifest reports divergent payloads for one
identity as a conflict rather than merging them.

**Recommendation: execute locally.** The matrix is ~2.2 hours single-threaded
at the measured 1.25 ms/tick, and the project's own cost plan already concluded
this study does not need AWS.

## 7. Registration status (mission 23–25)

`HOMEOSTASIS_STUDY_PREREGISTRATION_CANDIDATE.md` — **CANDIDATE, not frozen.**
World, region, arms, loads, hypotheses, matrix, seed rule and integrity gate
are specified. `homeostasis_analysis.py` is frozen before any result exists and
reproduces the registered Stage-B sign test and median interval exactly (checked
on 300 random samples).

Comparators audited in `HOMEOSTASIS_COMPARATOR_POLICY_REGISTER.md`: **none is
added**. The one serious candidate is degenerate — with `sigma = (1,1,1)` and a
single quantum, `E_G = f_e - 1` identically, so `argmax` of exact EBU equals
`argmax` of force on **496/496** lattice states.

## 8. Two findings that block the freeze

**Net-zero groups** (`NET_ZERO_GROUPS_FINDING.md`). Three of the 21 registered
candidate groups are cancelling pairs: nonempty, feasible, physically inert,
free at the reference where every other group is unaffordable, and away from it
a **costless capacity transfer between owners** — which the V1 capacity
docstring says does not exist. They satisfy mandatory action in form while
defeating it in substance. Present in the registered Stage-A/B world, which
they do not invalidate.

**Endpoint saturation** (`ENDPOINT_SATURATION_FINDING.md`). **Theorem A**: in
this world the EBU-aligned arm has `O95 = 1` identically, because forcing
amplitude equals the action quantum and the actor moves after forcing within
the tick, so exact reversal is always available, uniquely maximal and always
affordable. Verified over 28,800 ticks: maximum `R^2` ever observed was 2. The
hostile arm saturates at the floor. So `H1` is true before a tick runs and only
the `R` versus `C` contrast retains range.

## 9. Verdict structure (mission 30) — current evidential status

1. **Signal.** *Does maximizing EBU point actors toward homeostasis?*
   **Yes, provably, in this world — and that is the problem.** Theorem A. It is
   a theorem, not evidence, and it holds because exact reversal is always
   available. Nothing is learned by running it.
2. **Stupid-proofing.** *Does EBU improve homeostasis under random actors?*
   **No registered evidence.** Exploratory Stage-B: `O95` 0.031 vs 0.016.
   Rehearsal: EBU-random 5–13× the control at every load in both menus. This is
   the study's real empirical content and it is not yet answered.
3. **Hostile safety.** *How far can hostile affordable actors push the system?*
   **No registered evidence.** Rehearsal signal, and it is adverse: the hostile
   arm sits at median `R^2` 207–277 against the control's 120–130, i.e.
   **further out than the unconstrained control**, with peaks at 542 of a
   possible 600. Affordability appears to fund a deliberate actor rather than
   confine it.
4. **Absolute homeostasis.** **No registered evidence.** Everything seen so far
   says no, except where it is a theorem: Stage B ≤ 0.031; rehearsal
   EBU-random ≤ 0.12.
5. **Divergence.** **No registered evidence.** Stage-B reanalysis: falling
   late-window occupancy in 52/64 EBU replicates. Rehearsal: EBU-random's block
   occupancy declines across blocks at every load. Consistent with capacity
   growth; untested.

## 10. Not done, deliberately

- **No registered study executed.** Mission 26 authorizes AWS execution after
  seven gates; gate 3 cannot pass, and local registered execution is not
  separately authorized.
- **No preregistration frozen.** Two open decisions (section 8).
- **No book impact note.** Mission 32 requires registered results first; none
  exist.
- **No Capacity V2 in this study** (mission 8, 31), verified by inspection.
