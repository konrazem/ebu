# Capacity-V2 Stage-B readiness

Status: **readiness assessment and design sketch. NOT a preregistration. NOT
authorized to execute.**

Proposed protocol id: `EBU-CAPACITY-V2-STAGE-B-V1`. A frozen preregistration
must be written and committed, and seeds derived from it, before any run.

## 1. Why the scientific weight sits here

Under forcing off, both V2 success properties are theorems: absorption
(Theorem V2-5) and bounded capacity (Theorem V2-2). Stage A-v2 therefore
measures timing, not mechanism.

Under sustained forcing no comparable theorem is available, and the decisive
contrast with the registered V1 result lives here:

| | V1 (registered) | V2 (predicted) |
|---|---|---|
| `sum_i B_i` | diverges; median terminal 5400 | bounded by `V <= V_max = 300` (Theorem V2-2) |
| `rho_reject` | halved across the window, 0.0662 → 0.0332 | **open** |
| Arm difference | self-attenuated, -0.0747 → -0.0448 | **open** |

**Primary question:** does the affordability gate remain active under
stationary forcing instead of self-attenuating, and does the arm difference
persist?

This is genuinely open. Theorem V2-2 bounds capacity, which removes V1's
divergence mechanism, but it does **not** prove the gate stays binding.

## 2. The known structural concern, recorded before execution

The ceiling is `V_i = d^2/(2 sigma_i^2)` for deviation `d`, while receipt
magnitudes scale like `d`. So the ceiling exceeds the receipt scale once
`d > 2` (for `sigma = 1`): **the gate is tight near the reference and slack far
from it.** V2 licenses damage in proportion to deviation already carried.

Whether that is protective or permissive under sustained drive is exactly what
Stage B-v2 must measure. It should not be assumed either way, and a result
showing V2 permits larger excursions than V1 is an admissible outcome.

## 3. Proposed design — inherit registered Stage B unchanged

Physical world, forcing law (`q0 = 1`, edge uniform over 6 sorted edges,
amplitude fixed), per-arm `NULL_FORCING` rule, `H = 8192`, burn-in 2048, three
2048-tick blocks, `N = 64` paired, common normalization `V_max = 300`, primary
endpoint `L_r` and `Delta_r`, exact two-sided paired sign test at `alpha = 0.05`
with a sign-based median CI, and `delta_meaningful = 0.05` kept separate from
`alpha`.

Inheriting the registered Stage-B design unchanged is deliberate: it makes the
V1/V2 comparison a difference of mechanism and nothing else.

## 4. Mandatory diagnostics, beyond registered Stage B

- **`rho_reject` by block** — the decisive contrast. V1 halved; the registered
  question is whether V2 does not.
- **`sum_i B_i` against its bound `V(x)`** every tick, and its peak.
- **Retirement ledger `C`** growth by block; `C` must absorb the whole external
  drift and be monotone.
- **Ceiling slack fraction** — the fraction of ticks with `V_i > m_max R_max`
  for each cell, which directly measures the section-2 concern.
- Late-window stationarity per object, as registered Stage B: `V` and `sum B`
  separately, with `J` and `C` excluded as stationarity candidates by
  construction.

## 5. Exact invariants — zero tolerance

`V + sum_i B_i + C = J`; `sum_i x_i = 30`; `x_i >= 0`; `B_i <= V_i`;
`sum_a R_a = E_G`; `B_i >= 0` in the treated arm; `C` monotone.

## 6. Readiness status

| Item | Status |
|---|---|
| Mechanism implemented on an isolated model path | **READY** (`capacity_v2`) |
| Static conformance | **READY** — 61 assertions, 0 failures, residuals exactly 0 |
| Harness conformance | **READY** — 28 assertions, 0 failures, 729 ticks |
| Continuous-forcing path | **READY** — see section 7 |
| V1 isolation | **READY** — `gaussian_harness` identity still `a9158eef...` |
| Frozen preregistration | **NOT WRITTEN** |
| Seed manifest | **NOT DERIVED** |
| Frozen analysis implementation | **NOT WRITTEN** |
| Execution authorization | **ABSENT** |

## 7. Prior exposure disclosure

A continuous-forcing conformance probe was run at the non-registered seed pair
`(777, 888)` for 800 ticks in both arms, to confirm the path executes and the
invariants hold. Observed and disclosed in full:

- all four residuals exactly 0 in both arms; `C` monotone in both;
- `sum_i B_i <= V` held every tick in both arms;
- treated arm: peak `sum_i B_i = 9/2`, ending `J = 840`, `C = 840`, `V = 0`;
- control arm: 17 `NULL_FORCING` ticks, ending `V = 193`,
  `sum_i B_i = -8371/2`.

`rho_reject` trends and the paired endpoint were deliberately **not** computed,
because those are the quantities Stage B-v2 will preregister. The quantities
above are either proved invariants or raw ledger totals.

This is one probe at one non-registered seed and is **not** evidence. It does
not license any claim about the primary question in section 1.

## 8. Unresolved decisions for the author

1. Whether Stage A-v2 should run at all, given that its qualitative outcome is
   a theorem. A defensible alternative is to skip directly to Stage B-v2 and
   cite Theorems V2-1, V2-2 and V2-5 for the forcing-off regime.
2. Whether to re-run **V1** under the Stage B-v2 configuration as a third arm,
   giving a direct three-way V1 / V2 / control comparison in one registered
   study rather than across two preregistrations.
3. Confirmation that the section-2 slack concern is acceptable as a declared
   limitation rather than grounds for revising the ceiling before testing it.
