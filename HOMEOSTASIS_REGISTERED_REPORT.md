# Homeostasis registered study — report

**Registered evidence.** Executed under `HOMEOSTASIS_STUDY_PREREGISTRATION.md`,
frozen at commit `50a3265220e4f52280cdb3b13c3cbd056c5dee5f`
(tag `homeostasis-preregistration`) with seeds derived from that commit's own
hash. Analysis and integrity gate were frozen before execution.

| | |
|---|---|
| jobs | 1,536 of 1,536 |
| arm-ticks | 12,582,912 |
| wall time | 43.9 min, 12 workers, local |
| integrity gate | **PASSED** |
| accounting / conservation / nonnegativity residuals | **exactly 0** |
| negative capacity in affordability arms | 0 |
| unregistered statuses | 0 |
| missing or conflicting payloads | 0 |

---

## 1. Registered design verification

`results/homeostasis/FORCING_COUPLING_VERIFICATION.json`. The section 6
coupling held exactly in the executed data:

- `schedule(1/4) ⊆ schedule(1/2) ⊆ schedule(1)` in **512 of 512** cells, 0 failures;
- raw edge and orientation identical on every shared tick, **0 mismatches**;
- realized frequencies **0.2504 / 0.4996 / 1.0000** of 8192 ticks;
- arms differ in `NULL_FORCING` count in **384 of 384** cells, confirming
  arm-specific admissibility was preserved as an observed consequence of arms
  occupying different states, not suppressed into a common applied stream.

Mandatory action held absolutely: **0 `PHYSICAL_NO_ACTION_AVAILABLE` ticks**
across 12.6 million. 1,369 ticks were `AFFORDABILITY_BLOCKED` — an
affordability outcome, correctly distinguished from physical impossibility.

## 2. Primary endpoint `O95`, by load and menu

Medians over 64 replicates. Registered menu (21 groups) first; strict menu (18
groups) in parentheses.

| load | aligned | EBU-random | control | hostile |
|---|---|---|---|---|
| `1/4` | 1.0000 (1.0000) | **0.0696** (0.0644) | 0.0152 (0.0151) | 0.0001 (0.0002) |
| `1/2` | 1.0000 (1.0000) | **0.0439** (0.0431) | 0.0143 (0.0155) | 0.0003 (0.0011) |
| `1` | 1.0000 (1.0000) | **0.0289** (0.0273) | 0.0151 (0.0147) | 0.0005 (0.0008) |

**The menu factor changed nothing.** Removing the three net-zero groups moved
`O95` by at most 0.006 anywhere and altered no ordering, at any load, for any
arm. The loophole was used — null-action rates of 13.6–13.9% for the random
arms and 75.0% / 50.0% / 0.0% for the aligned arm as load rises — but it does
not drive the results. The concern raised in `NET_ZERO_GROUPS_FINDING.md` is
empirically resolved: it is a real property of the mechanism and an immaterial
one for these conclusions.

## 3. Registered contrasts

All nine contrasts in each menu are Holm-significant at `alpha = 0.05` with
`p = 1.084e-19` — the exact floor of a 64-replicate two-sided sign test,
meaning **every one of the 64 paired replicates fell the same way**. Effect
sizes, registered menu:

| load | `A` vs `R` | `R` vs `C` | `H` vs `R` |
|---|---|---|---|
| `1/4` | +0.9304 ✓δ | **+0.0528 ✓δ** | −0.0668 ✓δ |
| `1/2` | +0.9561 ✓δ | +0.0299 | −0.0435 |
| `1` | +0.9711 ✓δ | +0.0137 | −0.0271 |

`✓δ` marks a median difference of at least `delta_meaningful = 0.05`.

## 4. Secondary metrics — descriptive

Registered menu, medians over 64 replicates. `H95` is `R^2 <= 5`; the simplex
vertex is `R^2 = 600`; the analysis window is 6,144 ticks.

| load | arm | median `R^2` | mean `R` | p95 `R^2` | time outside `H95` | exits | longest excursion | affordable groups |
|---|---|---|---|---|---|---|---|---|
| `1/4` | aligned | 0 | 0.00 | 0 | 0 | 0 | 0 | 20.96 |
| | EBU-random | 56 | 7.77 | 218 | 5716.5 | 173 | 322.5 | 17.97 |
| | control | 126 | 11.33 | 386 | 6050.5 | 45 | 1028.5 | 19.68 |
| | hostile | 258 | 15.73 | 488 | 6143.5 | 0.5 | **6094.5** | **7.02** |
| `1` | aligned | 0 | 0.00 | 0 | 0 | 0 | 0 | 20.99 |
| | EBU-random | 98 | 9.90 | 338 | 5966.5 | 97.5 | 576.5 | 18.39 |
| | control | 126 | 11.42 | 386 | 6051.5 | 54 | 880.0 | 19.37 |
| | hostile | 294 | 16.19 | 542 | 6141.0 | 2 | 4031.0 | **7.26** |

## 5. Hypotheses

| | statement | outcome |
|---|---|---|
| **H1** | `O95(A) > O95(R)` at some load | **true, but by Theorem A, not by evidence** |
| **H2** | `O95(R) > O95(C)` at some load | **true at every load, unanimous** |
| **H3** | `O95(H) < O95(R)` at some load | **true at every load, unanimous** |
| **H4** | rising load reduces `O95` in **all four** arms | **false** |

H4 fails and the pattern is informative. Only EBU-random declines with load
(0.0696 → 0.0439 → 0.0289). The aligned arm is pinned at 1 by Theorem A. The
control is **flat** at ~0.015 — it is already so far out that more disturbance
changes nothing. And the hostile arm *rises* slightly (0.0001 → 0.0005),
because heavier forcing supplies more capacity-earning opportunities than a
destructive actor can spend. **The EBU arm is the only one with anything left
to lose.**

## 6. Verdict (mission section 30)

### 1. Signal — does maximizing EBU point actors toward homeostasis?

**Yes, and it is a theorem rather than a finding.** The aligned arm held
`O95 = 1.0000` in all six cells, exactly as `ENDPOINT_SATURATION_FINDING.md`
proved in advance: forcing amplitude equals the action quantum, so exact
reversal is always available, uniquely maximal, and affordable from zero
capacity. The registered execution confirms the theorem; it adds no
independent evidence. **H1 must not be cited as empirical support.**

### 2. Stupid-proofing — does EBU improve homeostasis under random actors?

**Yes, consistently, and by a small absolute margin.** EBU-random beat the
control in **64 of 64 paired replicates at every load and under both menus** —
about 4.6× the occupancy at `p = 1/4`, 3.1× at `1/2`, 1.9× at `1`. Median
radius fell from 126 to 56 and mean `R` from 11.33 to 7.77 at the mildest load.

But the absolute difference is **+0.053, +0.030 and +0.014**, and only the
first clears the registered `delta_meaningful = 0.05`. The registered range
caveat applies as written: at heavy load there is little room for an absolute
difference of 0.05 to appear. **This is the study's genuine empirical content,
and the honest summary is that EBU affordability produces a reliable,
directionally clear, and small improvement.**

### 3. Hostile safety — how far can hostile affordable actors push the system?

**Further than an unconstrained random actor. This is the study's adverse
finding and it is unambiguous.**

The affordability gate bit hard: the hostile arm had only **7.02 affordable
groups of 21** against the control's 19.68. It was materially constrained in
what it could choose — and it still reached median `R^2` of **258–294 against
the control's 126**, mean `R` of 15.7–16.2 against 11.3, and spent 6143.5 of
6144 ticks outside `H95`. At `p = 1/4` its median longest excursion was
**6094.5 ticks — essentially the entire analysis window**, with a median of
**0.5 exits**: it leaves the region once and does not come back.

> **EBU affordability restricts a hostile actor's menu without restricting its
> damage.** On this evidence it is not a safety mechanism against a deliberate
> adversary; by earning capacity from disturbances it strictly funds one, and
> the resulting process is worse than randomness on every physical-state
> measure recorded.

### 4. Absolute homeostasis — which policies keep the system inside the region?

**None, except the arm for which it is a theorem.** Every non-aligned arm falls
in the registered `not_localized` band (`O95 < 0.05`), except EBU-random at
`p = 1/4`, which reaches 0.0696 — `weakly_localized`. No arm approaches the
`localized` band of `O95 >= 0.50` at any load. Relative regulation is real;
absolute homeostasis is absent.

### 5. Divergence and operating envelope

The registered divergence predicate — `O95` strictly falling and block median
`R^2` strictly rising across all three late blocks — fired most in the
**EBU-random** arm: 24 of 64 replicates at `p = 1/4`, against 1 of 64 for the
control. At the median its blocks show `O95` 0.0864 → 0.0664 → 0.0552 with
median `R^2` 42 → 56 → 72.

This is the physical-state signature of the registered Stage-B falsification:
capacity accumulates, the affordability gate progressively stops binding, and
the EBU arm drifts toward control behaviour. The two studies were frozen
independently and agree. **The EBU arm is the one that degrades**, because it
is the only one that had regulation to lose.

Operating envelope: EBU-random's advantage is largest at the mildest load and
decays monotonically with it. **There is no load at which any arm achieves
absolute homeostasis in this world.**

## 7. Limitations and non-claims

1. **One world.** Three cells, `sigma = (1,1,1)`, one quantum, complete
   topology. Nothing generalizes beyond it.
2. **H1 carries no evidential weight** (Theorem A, registered in advance).
3. **Q3's contrast is floor-limited on `O95`.** Both `H` and `C` read near
   zero, so the hostile finding rests on the descriptive radius metrics of
   section 4, which are secondary and carry no significance claim. It is a
   clear and consistent signal, not a tested hypothesis.
4. **Capacity V1 only.** V2 was not substituted anywhere; nothing here is
   evidence about V2.
5. **`p = 1.084e-19` is a floor, not a magnitude.** It means every replicate
   agreed, and says nothing about effect size — which is why effect sizes are
   reported first.
6. **Statistical significance is not a broad EBU claim.** The `R` vs `C`
   improvement is unanimous and small; the hostile result is adverse; absolute
   homeostasis was not achieved by any arm.
7. **Analysis defect, disclosed.** `homeostasis_report.py` raised a
   `TypeError` on first execution: three integer-valued *descriptive secondary*
   metrics were passed to `exact_median`, whose even-sample branch divides by
   two and produced a float. The fix coerced those three inputs to `Fraction`
   in the reporting layer. It was applied **before any result had been read**,
   touched no registered definition, no primary endpoint, no contrast and no
   inferential rule, and did not modify the pinned `homeostasis` package.

## 8. What this does not settle

The mechanism question is untouched. The hostile finding and the EBU-random
drift both point at the same place as Stage B did — unbounded capacity
accumulation under V1 — and Capacity V2 exists with theorems and static
conformance but **no registered behavioural evidence**. A V1-versus-V2 study
is the obvious next one, and it is not authorized here.
