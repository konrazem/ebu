# The primary endpoint saturates for two of the four arms

**Status: pre-execution design finding, with a proof for one half and strong
rehearsal evidence for the other.** It is reported before any registered study
is frozen, precisely so that the endpoint question is settled in advance rather
than rationalised after a result.

No registered artifact is modified. The evidence below is a theorem plus a
conformance probe plus the non-confirmatory rehearsal.

---

## 1. Theorem A — EBU-aligned occupancy is `1` by construction

**Setting.** The registered world: `sigma = (1,1,1)`, action quanta `{1}`, max
group size 2, forcing quantum `q0 = 1`, and the canonical event order in which
external forcing precedes the actor's choice *within the same tick*. Occupancy
is measured on `state_after`.

**Claim.** From `x = x*`, the EBU-aligned actor returns the state to `x*` (or
to a point inside `H95`) on every tick, at every load. Hence `O95 = 1`
identically.

**Proof.**

*Forced tick.* Forcing moves one unit along `i -> j`, so `z = e_j - e_i`,
`V = 1`, `R^2 = 2`. Consider the reversing singleton `j -> i` at `q = 1`, with
`delta = e_i - e_j`. Since `mu = z`,

```
E_G = -mu^T delta - (1/2) delta^T H delta = -((-1)(1) + (1)(-1)) - (1/2)(1+1) = 2 - 1 = 1
```

which is the exact drop `V: 1 -> 0`. No candidate can exceed it, because
`V >= 0` and `V = 0` is attained, and the reversal is the unique group reaching
`V = 0` from this state. So the aligned actor selects it.

*Affordability.* The single action's owner is its source `j`, and
`R_a = E_G = +1`, so the projected balance is `0 + 1 >= 0`. The reversal is
affordable from zero capacity, at every such tick. Forcing is always admissible
here because every cell holds `10 >= 1` at `x*`.

*Unforced tick.* The state is already `x*`. With net-zero groups in the menu
the maximum is the inert group at `E_G = 0`, so the state does not move. With
the strict menu every group is a real move with `E_G = -1` by symmetry, so the
actor moves to `R^2 = 2` — which is **inside** `H95` — and reverses on the next
tick.

In every case `R^2 <= 2 < 5`, so the state never leaves `H95`. **QED.**

**Verification.** 28,800 ticks across 2 menu rules, 3 loads and 12 seeds: the
maximum `R^2` ever observed after the actor acted was **2**, and the maximum
`V` was **1**. The rehearsal independently reports `O95 = 1.0000` for the
aligned arm in all six load/menu cells.

## 2. Floor saturation — EBU-hostile

Not a theorem; strong and consistent rehearsal evidence. Median `O95` for the
hostile arm was `0.0000` in five of the six load/menu cells and `0.0016` in the
sixth, with median `R^2` between 210 and 266 and peaks at 542 against a vertex
maximum of 600. The hostile arm is pinned far outside the region.

Unlike Theorem A this depends on the capacity economy — the hostile actor must
first earn capacity from disturbances before it can fund damage — so it is
recorded as an empirical regularity, not proved.

## 3. Consequence: `O95` cannot discriminate the four arms

Rehearsal medians, `O95` (**REHEARSAL / NON-CONFIRMATORY**):

| load | control | hostile | EBU-random | aligned |
|---|---|---|---|---|
| `1/4` | 0.0146 | 0.0000 | 0.1549 | **1.0000** |
| `1/2` | 0.0111 | 0.0000 | 0.0967 | **1.0000** |
| `1` | 0.0150 | 0.0000 | 0.0589 | **1.0000** |

Two arms sit at the ceiling and the floor. Of the three registered contrasts:

- **`A` vs `R` (incentive validity)** — degenerate. `H1` is true by Theorem A
  before a single tick runs. Executing 6.3 million arm-ticks to observe a
  theorem produces no evidence.
- **`H` vs `R` (hostile safety)** — floor-limited. Both a mild and a severe
  hostile effect look like `0.0000`, so the contrast cannot measure *how much*
  protection remains, which is the actual question in mission section 13 Q3.
- **`R` vs `C` (stupid-proofing)** — **this one has range and is the study's
  real empirical content.**

## 4. A metric that does not saturate

Median `R^2` over the analysis window is already in the frozen battery of
`homeostasis/metrics.py`, is a pure physical-state quantity, is exact, and
separates all four arms monotonically (**REHEARSAL / NON-CONFIRMATORY**):

| load | aligned | EBU-random | control | hostile |
|---|---|---|---|---|
| `1/4` | 0 | 21 | 122 | 236 |
| `1/2` | 0 | 42 | 114 | 260 |
| `1` | 0 | 62 | 128 | 266 |

It has range at both extremes: a hostile arm that was twice as destructive, or
an aligned arm that overshot, would both be visible. `O95` would record neither.

## 5. What this does and does not mean

- **Theorem A is not a defect in EBU.** It says that when an actor *can*
  exactly undo each disturbance and is incentivised to, it does. That the EBU
  signal points the right way in the easy case is a genuine sanity result — it
  is simply one that is proved rather than measured.
- **It is a defect in the experiment as specified**, because the primary
  endpoint's headline contrast is settled a priori.
- **The cause is the quantum ratio, not the incentive.** Forcing amplitude
  equals the action quantum, and the actor moves after forcing in the same
  tick, so exact reversal is always available. Mission section 12 freezes
  `q = 1` and varies frequency rather than amplitude — which is exactly what
  preserves the degeneracy across all three loads. A disturbance larger than
  one action quantum, or several disturbed edges per tick, would make Q1
  genuinely empirical. Section 12 reserves any other amplitude to *"current
  authority"*, so this is not a change this task may make.
- **It does not affect Q2.** The `R` versus `C` contrast is unaffected and
  retains its range.

## 6. Recommendation

1. **Record Theorem A as the answer to Q1** and stop treating `A` versus `R` as
   an empirical contrast in this world.
2. **Elevate median `R^2` to a co-primary endpoint** alongside `O95`, with the
   same three contrasts and the same Holm-within-load correction. It is already
   frozen in the metric battery, so this adds no new machinery.
3. **Keep `O95` as primary** as mission section 4 directs, and report the
   saturation alongside it rather than quietly substituting a metric that looks
   better.
4. **For a later study**, make Q1 empirical by breaking exact reversibility —
   a forcing amplitude exceeding the action quantum is the smallest change that
   does it. This requires author authority over `q`.
