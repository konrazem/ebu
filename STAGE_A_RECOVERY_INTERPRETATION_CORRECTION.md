# Stage-A recovery: interpretation correction

**Status: interpretation correction note. No artifact, preregistration,
analysis or report is modified by it.**

`STAGE_A_PREREGISTRATION.md`, `stage_a_analysis.py`, `results/stage_a/` and
`STAGE_A_REGISTERED_REPORT.md` remain exactly as frozen and executed. This note
adds a reading of evidence that already exists; it removes nothing and rewrites
nothing.

---

## 1. The conflation being corrected

The registered Stage-A protocol ran each replicate for the full horizon
`H = 256` post-shock actor ticks and classified the **whole** trajectory. The
mission statement (section 0) identifies that this mixed two separate
questions:

- **A.** Can random EBU-affordable actors recover from a one-time disturbance?
- **B.** What happens if mandatory actions continue *after* the system has
  already returned to exact equilibrium while actors retain earned capacity?

Under the frozen classification, an EBU replicate that reached `V = 0` quickly
and was then moved away again by later mandatory actions was classified
`REPEATED_CYCLING`. That classification is factually correct about the
256-tick trajectory. It is **not** a statement that recovery failed.

## 2. The corrected recovery semantics

For all future one-shock recovery experiments (mission section 10):

> **The first tick satisfying `V = 0` terminates the recovery trial
> successfully.**

The trial does not continue past that tick, and later mandatory actions are not
counted against recovery. If no `V = 0` occurs before the frozen horizon, the
outcome is `NOT_RECOVERED_WITHIN_HORIZON`.

## 3. What the existing registered evidence already says

First equilibrium-hitting time `T_0 = inf{t : V(t) = 0}` was **registered
before execution** as a frozen secondary diagnostic
(`STAGE_A_PREREGISTRATION.md` section 11, censored at `H+1 = 257`). It is not a
new metric invented after the fact.

Re-derived independently for this note from the immutable per-tick artifacts in
`results/stage_a/ticks/` (256 files), and matching `ANALYSIS_RESULTS.json`
exactly:

| Arm | Reached `V = 0` within `H` | Median `T_0` among reachers | Range |
|---|---|---|---|
| EBU affordability, random actor | **128 / 128** | **3.5 ticks** | 2 – 28 |
| Physical-feasibility random control | 63 / 128 | 22 ticks | 2 – 243 |

Deadlock total was `0` in both arms; all accounting, conservation and
nonnegativity residuals were exactly `0`.

### The corrected reading

> **In the registered Stage-A world, random EBU-affordable actors recovered
> from a one-time conservative disturbance in 128 of 128 replicates, at a
> median of 3.5 post-shock ticks.**

Under the corrected semantics of section 2, every EBU replicate is a
`RECOVERED` trial. The `REPEATED_CYCLING` classification recorded in the
registered report describes question **B**, the continued-demand behaviour
after successful recovery, and is retained unchanged for that purpose.

## 4. What this correction does *not* do

1. **It does not repair the Stage-A primary endpoint.** The registered report's
   own finding stands: the primary statistic `A_r` was structurally bounded by
   `A_EBU <= 1` because `V + sum_i B_i = D` with `B >= 0`, while the control had
   no such bound. That comparison remains near-uninformative and the correction
   does not rehabilitate it.
2. **It does not make the cross-arm `T_0` contrast clean.** The same structural
   constraint that bounded `A_EBU` also confines the EBU arm to `V <= D = 4`,
   a small neighbourhood from which reaching `V = 0` is easier. The `128/128`
   versus `63/128` contrast is therefore *not* an uncontaminated comparison of
   policies. The within-arm statement in section 3 — that the EBU arm recovered
   in every replicate — does not depend on the comparison and is unaffected.
3. **It does not weaken the Stage-B falsification.** Stage B tested the
   continuing-demand question under continuous forcing and found capacity
   growing to roughly `5400` against a potential ceiling of `V_max = 300`, with
   the arm difference decaying below the registered meaningful effect size.
   That result is untouched. Section 0 of the mission explicitly separates the
   two questions; recovery succeeding does not imply persistent-demand
   homeostasis, and the mission does not claim it does.
4. **It authorizes no rerun.** The registered Stage-A recovery question has been
   answered in its registered world. Mission section 10 is explicit that it must
   not be re-run merely to reproduce the same number.
5. **It is not evidence about the homeostasis mission.** Stage A measured
   `V = 0`, not occupancy of the reference region defined in
   `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md`. No `O95` claim is derived here.

## 5. Scope

Applies to: the interpretation of first-hitting behaviour in Stage A, and the
design of any future one-shock recovery trial.

Does not apply to: the Stage-A primary endpoint, the Stage-B registered
conclusion, Capacity V2, or any claim about behaviour under continuing
disturbance.
