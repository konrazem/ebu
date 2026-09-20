# EBU homeostasis test hierarchy

**Status: structural definition.** It registers no experiment and asserts no
result. It says what each level tests, what evidence class can satisfy it, and
what passing it does **not** license.

**The levels do not collapse into one pass/fail statistic.** There is no
aggregate "EBU score", and a mechanism that satisfies levels 0–2 has not
thereby satisfied level 3.

Current status is recorded per level for Capacity V1 and V2. Status is
evidence, not endorsement.

---

## Level 0 — exact EBU measurement

**Question.** Is the finite action valuation exact, and do simultaneous-group
receipts close?

**Satisfied by.** Conformance and theorem. Exact rational identity
`E = V(z) - V(z+d)`, common-path receipts summing to the group value with zero
residual, quadrature agreeing with the closed form.

**V1: SATISFIED** — `test_gaussian_foundation.py`, 65 assertions, residuals
exactly 0. **V2: SATISFIED** — valuation is shared and unmodified.

**Does not license.** Anything about dynamics. Exact arithmetic is a property
of the ruler, not of the system being measured.

## Level 1 — signal validity

**Question.** Does `arg max E_G` select the most restorative action available
among the admissible candidates?

**Satisfied by.** Theorem or exhaustive enumeration. On one frozen candidate
set `arg max E_G = arg min V_post`, so the question is whether that identity
holds at every state.

**V1: SATISFIED** — verified by enumeration over lattice states,
`test_restoring_tendency.py`. **V2: SATISFIED** — valuation unchanged; V2
alters affordability only.

**Does not license.** Any claim that following the signal produces homeostasis.
Where the forcing amplitude equals the action quantum, perfect aligned
behaviour is a theorem about the quantum ratio (`ENDPOINT_SATURATION_FINDING.md`
Theorem A), not evidence about the signal.

## Level 2 — actor restoring drift

**Question.** Does the actor layer tend inward as deviation grows —
`D_A(S) < 0` at large deviation?

**Satisfied by.** Exact enumeration over the complete state, or registered
measurement. Must be reported **per capacity regime**; a single regime is
insufficient.

**V1: SATISFIED IN THE LOW-CAPACITY REGIME, FAILS AT SATURATION.** Exactly:
EBU-random restores from 99.8% of states at `B = 0` and 34.5% at `B_i >= 29`,
the latter being identical to the control by Theorem R2. **V2: BOUNDED, NOT
MEASURED** — at its ceiling bound it restores from 87.7% of states; where it
actually sits inside that bound is unmeasured.

**Does not license.** Any closed-loop claim. The actor layer can pull inward
while the total process drifts outward.

## Level 3 — closed-loop restoring drift

**Question.** Under disturbance plus mandatory action, is there inward drift
outside a recurrent operating region — `D_T(Y) < 0` at large deviation?

**Satisfied by.** Exact enumeration or registered measurement, per capacity
regime, with the operating region located rather than assumed.

**V1: SATISFIED IN THE LOW-CAPACITY REGIME ONLY.** Mean high-deviation drift
decays monotonically from `-18.4` at `B = 0` to exactly the control's `-3.4` at
`B_i = 29`. **V2: BOUNDED AT `-8.2`, NOT MEASURED.**

**Does not license.** Long-run stability. One-step drift is not a Lyapunov
condition, and no Foster–Lyapunov theorem is available for this model
(`EBU_RESTORING_TENDENCY_FOUNDATION.md` §10).

## Level 4 — shock recovery

**Question.** After a large disturbance ends, does the system return toward the
reference, and how does return depend on the account state it carries?

**Satisfied by.** Registered measurement under `RT-C02` and `RT-C07`.

**V1: PARTIAL.** The registered Stage-A study found 128/128 first-hit recovery
from a one-quantum-scale shock under random EBU actors, but with the primary
endpoint structurally compromised. Return from deep shells under continuous
forcing was measured exploratorily: 49 ticks for EBU-random, 120 for control,
1248 for hostile with 50 of 232 episodes never returning. **Large isolated
shocks with forcing off (`RT-C02`) have not been run.** **V2: NOT RUN.**

**Does not license.** Persistent-demand conclusions. Recovery from a finite
disturbance and regulation under continuing disturbance are different
questions, and the programme has conflated them before.

## Level 5 — stochastic homeostasis

**Question.** Under persistent disturbance, does the process remain recurrent
and bounded around a stable operating distribution?

**Satisfied by.** Registered measurement with late-window drift diagnostics,
plus a stated argument about what recurrence means on a compact state space.

**V1: NOT SATISFIED.** The registered study found sustained outward late-window
movement in the EBU-random arm at every load (mean `V` rising 33 → 44, 44 → 53,
55 → 63), which the exact analysis explains as migration from the
low-capacity regime toward the saturated one. The physical state is confined to
a compact simplex, so this is OUTWARD DRIFT, not divergence. **V2: NOT RUN.**

**Does not license.** Anything about other topologies or scales.

## Level 6 — hostile safety

**Question.** Does affordability prevent high-deviation capture or physical
failure under adversarial choice?

**Satisfied by.** Registered measurement under `RT-C10`, at a minimum of two
capacity regimes.

**V1: NOT SATISFIED — ADVERSE.** The registered study found the hostile arm
further out than the *unconstrained* control on every physical-state measure,
with 7–9× the high-deviation occupancy and a median longest excursion covering
essentially the whole analysis window. The exact analysis shows why:
affordability restrains a hostile actor only while it is poor, and at
saturation it restores from 0.6% of states with drift `+28.6`. **V2: BOUNDED,
STILL ADVERSE** — at its ceiling bound the hostile arm restores from 6.7% of
states with drift `+17.5`.

**Does not license.** Presenting V2 as a fix for hostile safety. Its bound is
an improvement and is not a solution.

## Level 7 — topology and scale robustness

**Question.** Do levels 1–6 persist across network structures and sizes?

**Satisfied by.** Registered measurement under `RT-C11` and on worlds with
different cell counts and topologies.

**V1: NOT RUN. V2: NOT RUN.** Every result in the programme is from one
three-cell complete-topology world with `sigma = (1,1,1)` and a single quantum.

**Does not license.** Nothing yet; nothing has been attempted at this level.

---

## Summary

| level | V1 | V2 |
|---|---|---|
| 0 exact measurement | satisfied | satisfied |
| 1 signal validity | satisfied | satisfied |
| 2 actor drift | low-capacity only | bounded, not measured |
| 3 closed-loop drift | low-capacity only | bounded, not measured |
| 4 shock recovery | partial | not run |
| 5 stochastic homeostasis | **not satisfied** | not run |
| 6 hostile safety | **not satisfied, adverse** | bounded, still adverse |
| 7 topology and scale | not run | not run |

The hierarchy is not a ladder a mechanism climbs once. A mechanism can satisfy
levels 0–3 in one capacity regime and fail them in another, which is exactly
what Capacity V1 does, so **every level from 2 upward must be reported per
capacity regime**.
