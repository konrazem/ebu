# Stage B re-read through the homeostatic reference region

**Class: EXPLORATORY POST-REGISTERED HOMEOSTASIS ANALYSIS.**

The metrics used here did not exist when Stage B was frozen, executed or
reported. Nothing below is confirmatory. No hypothesis is tested, no p-value is
computed, and `STAGE_B_REGISTERED_REPORT.md` is not modified, reinterpreted or
superseded. Its registered conclusion stands exactly as written.

Mission section 16 asks this analysis for one narrow purpose: **to learn how
severe the Stage-B continuous forcing actually was, relative to the region the
new study will measure against.** The answer turns out to matter for the
design.

Source: the 128 immutable artifacts in `results/stage_b/ticks/`. Script:
`stage_b_homeostasis_reanalysis.py`. Output:
`results/exploratory/STAGE_B_HOMEOSTASIS_REANALYSIS.json`. Window: the
registered post-burn-in window, ticks 2048–8191, three blocks of 2048.

---

## 1. Results

Medians over 64 replicates per arm. `H95` is `R^2 <= 5`, `H99` is `R^2 <= 9`;
the physical simplex boundary is at `R^2 = 150` and the vertex maximum is
`R^2 = 600`.

| | EBU affordability, random actor | Physical-feasibility random control |
|---|---|---|
| `O95` | **0.0308** | **0.0155** |
| `O99` | 0.0768 | 0.0420 |
| mean `V` | 59.73 | 76.54 |
| median `R^2` | **98** | **126** |
| p95 `R^2` | 340 | 392 |
| max `R^2` | **600** | **600** |
| mean `R` | 9.88 | 11.39 |
| exits from `H95` | 102 | 55.5 |
| ticks outside `H95` | 5954.5 / 6144 | 6049 / 6144 |
| longest excursion | 551 ticks | 813 ticks |
| replicates never in `H95` | 0 | 0 |

Late-window movement, by replicate:

| | EBU arm | Control |
|---|---|---|
| block median `O95` | 0.0371 → 0.0269 → 0.0254 | 0.0151 → 0.0139 → 0.0164 |
| block median `R^2` | 96 → 98 → 98 | 126 → 126 → 126 |
| falling occupancy | **52 / 64** | 24 / 64 |
| rising median `R^2` | 45 / 64 | 24 / 64 |

## 2. What this says

**Stage B was not a mild homeostasis test. It was an extreme one.** Under
forcing at every tick, both arms spent roughly 97–98% of the analysis window
outside `H95`, and the *median* replicate in *both* arms reached `R^2 = 600` —
a simplex vertex, all 30 units in one cell, the furthest physically reachable
state. The median operating radius, `R^2` of 98 and 126, sits well past the
`R^2 = 9.21` scale of `H99` and approaches the inscribed physical boundary at
150. Neither arm was localized around the reference in any absolute sense.

**The EBU arm was nonetheless better on every homeostasis measure**: twice the
`O95`, lower median and mean radius, lower peak percentile, and a longest
excursion shorter by about a third. This is exactly the distinction mission
section 15 insists on — *relative regulation* without *absolute homeostasis*.
Reporting only the ratio would be misleading; reporting only the absolute level
would hide a consistent difference.

**Note the exit-count inversion.** The EBU arm exits `H95` almost twice as
often as the control (102 versus 55.5) while spending *less* time outside it.
More exits with less time outside means the EBU arm returns more often and
stays away for shorter stretches. Exit counts must therefore not be read as a
damage measure on their own.

**The late-window asymmetry is consistent with the registered falsification.**
Occupancy fell from the first to the last block in 52 of 64 EBU replicates
against 24 of 64 controls, and the control's median radius did not move at all
across blocks. The registered Stage-B finding was that capacity grows without
bound — to roughly 5400 against a ceiling of `V_max = 300` — so the
affordability gate progressively stops binding and the EBU arm drifts toward
control behaviour. The occupancy decline observed here is what that would look
like measured on the physical state. **This is a consistency observation, not a
test**: no causal claim is made, and an alternative explanation has not been
excluded.

## 3. Consequences for the new study design

1. **`p_force = 1` is a saturating load, not a middle of a range.** At every
   tick both arms are pinned far outside the region and both reach the simplex
   vertices. Any policy contrast at that load is a contrast between two
   non-homeostatic processes. The mission's lower loads of `1/4` and `1/2` are
   where a homeostatic regime, if one exists at all, is more likely to be
   visible — so the three loads are not a ladder around a working point but a
   search for whether a working point exists.
2. **An absolute-homeostasis criterion must not be set at `O95 >= 0.95`
   reflexively.** The best arm here achieved `O95 = 0.031`. Mission section 15
   already warns against equating the region's name with a pass rule, and this
   is the empirical reason why.
3. **Floor and ceiling effects are a live risk at `p_force = 1`.** With `O95`
   at 1.5–3% in both arms, the metric has little room to separate policies
   downward. The hostile arm in particular may be indistinguishable from the
   control at that load for reasons of measurement range rather than physics.

## 4. Non-claims

- This is exploratory and post-registered. It is not evidence for or against
  any hypothesis, and it establishes no property of EBU.
- It does not revise, weaken or strengthen the Stage-B registered conclusion.
- It measures the physical state only. Capacity, receipts, settlement and the
  deviation ledger appear in none of these metrics.
- The consistency between falling occupancy and the registered capacity-growth
  finding is an observation, not a demonstrated mechanism.
