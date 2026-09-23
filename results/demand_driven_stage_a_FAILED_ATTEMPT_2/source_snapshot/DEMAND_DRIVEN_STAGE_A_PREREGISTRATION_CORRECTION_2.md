# Stage-A preregistration — correction 2, pre-execution

**Registration:** `EBU-DEMAND-DRIVEN-STAGE-A-v1`
**Document corrected:** `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md`
**Status:** authorized pre-execution correction and re-freeze.

| | |
|---|---|
| freeze 1 identity (superseded) | `72a950721a81a7e0e2dba28e1a1a47124769a3378a4d28cd34d7e1f8aace78de` |
| freeze 2 identity (superseded) | `36fb53b6a3fca61be79391d1ab02927f148fa0d13f526f9b0895903f0fa91c75` |
| **freeze 3 identity (current)** | `a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17` |
| epochs executed under freeze 1 | **zero** |
| epochs executed under freeze 2 | **zero** |
| mechanism identity, unchanged throughout | `demand_driven_ebu` = `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48` |

Recomputed by `scripts/stage_a_preregistration_identity.py`, which executes no
model code.

---

## Why this correction exists

Freeze 2 left reporting definitions that were either ambiguous or false. Every
one of them would have had to be settled **during or after** execution, which is
exactly when a definition can be chosen to suit an outcome. They are settled
here instead, before the first registered epoch, with zero epochs executed under
any superseded identity.

Nothing in the environment, prelude, policies, arms, seeds, horizons, opening
balances, episode definitions or physical semantics was touched.

---

## What changed

### 1. A1 stopping precedence (§2)

The three stop conditions are **not mutually exclusive**, and freeze 2 declared
no precedence. Now: evaluated **S1, S2, S3**, first match wins, applied
identically at every transition including the last.

The tie that matters is at `t + 1 == T`. A return there satisfies S1 and S3
simultaneously; S1 wins and the episode records `RETURNED_TO_REFERENCE` with
`return_time = T`. An unaffordable stall there satisfies S2 and S3; S2 wins.

### 2. The `N == T` claim is withdrawn (§7, A1)

Freeze 2 asserted that `transitions_recorded` equals `T` **only** when the stop
was `HORIZON_REACHED`. That is **false**: a return or an unaffordable stall
occurring on the final permitted transition also produces `N == T`. Reading the
stopping reason off `N` would therefore have misclassified exactly those
episodes.

`N` is now reported beside the declared maximum `T`, never in place of it;
`horizon` is an explicit field; and `stopping_reason` is the only source of the
stopping reason.

### 3. A3 stop conditions, declared separately (§4)

Freeze 2 gave A3 no stop conditions of its own. Inheriting A1's S1 would have
been **fatal to the class**: A3's order arrives at epoch 3, and an arm that
reached `x*` during the prelude would have stopped at epoch 1 or 2 and the order
would never have arrived at all.

A3 now stops only at the horizon or on an §8 integrity failure. It runs all 32
transitions, so the post-arrival observation window is the same length in every
arm and no arm's window is shortened by its own behaviour.

### 4. Restoration timestamps, defined exactly (§4)

"Whether an induced deficit returns to zero" did not say **which** deficit.
With more than one open coordinate, "any" and "all" are different claims.

- `tracked_deficits` — frozen at the post-service state `x_{s+1}`;
- `first_closure[c]` — per tracked coordinate, independently;
- `first_simultaneous_closure` — over the **whole** tracked set, and explicitly
  **not** `max(first_closure)`: a coordinate may close, reopen and close again,
  so the maximum of the per-coordinate firsts can name an index at which the
  set is not jointly clear. A regression exercises exactly that sequence;
- `closure_count` — so partial closure is visible as partial.

**An empty tracked set is never a demonstrated restoration.** If serving the
order left no deficit, there was nothing to restore, and reporting it as
`RESTORATION_COMPLETED` would count the absence of a demand as evidence the
mechanism met one.

### 5. The label map, deterministic and exhaustive (§4)

Ordered decision table `L1 … L5`; every episode matches exactly one row. The
four chain facts — admission status, service epoch, **dated** pendency, and the
restoration facts — are recorded **separately** from the label, so no single
label has to carry four different questions.

`ORDER_PENDING_NO_COMPLETE_PLAN` is added. §2 already declares a blocked
economic component an **ordinary** A2/A3 outcome rather than an integrity
failure, and the four-label set had nowhere to put it. This is a **reporting**
addition: no new physics, no new predicate, no new mechanism, and §8 is not
weakened — a non-equilibrium `NO_COMPLETE_PHYSICAL_PLAN` in a **P-only**
component remains an integrity failure in A1.

`SERVED_WITHOUT_RESTORATION` carries a mandatory
`served_without_restoration_reason`, so the label is not lossy.

---

## A separate correction, outside this document

`DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` §3's **displayed equation** asserted
the economic inequality at every coordinate of `R`:

```
all c in R : delta_G[c] >= economic_total(c)
```

At a physical-only coordinate `economic_total(c) = 0`, so the clause read
`delta_G[c] >= 0` and forbade a plan from drawing stock **out of** any
represented coordinate — reintroducing through a quantifier the restriction
strong atomic provenance had removed.

Verified witness: at `(2,3,7)` the requirement set is `A: deficit 2`,
`B: deficit 1`, both economic-free. The plan `B->A@1` has increment `(1,-1,0)`.
The implementation returns `serves_all = True`; the unguarded display returned
**false** on coordinate `B`.

The equation is now guarded — `economic_total(c) == 0 or delta_G[c] >=
economic_total(c)` — and **the mechanism was not touched**: `serves_economic`
has always been vacuously true at `economic_total == 0`. Only the equation was
wrong, and only the equation was corrected. An isolated pure-function regression
transcribes the displayed equation and checks it against the implementation on
the witness and on **every executable plan at every state of the frozen
domain** — 3582 pairs, zero disagreements — and separately confirms that the
superseded form contradicts the implementation on the witness.

---

## What was verified before the re-freeze

All execution-free, with `EconomyRun.run_epoch` and `EconomyRun.run` guarded to
raise for the whole of the preflight module:

- 768 declared jobs constructed; **768 / 768** distinct run identities;
  identical on rebuild;
- declared fixtures, arms, seeds, zero opening balances, `registered=True`,
  `decomposition_gate=True` checked against this document;
- A1 precedence and both final-transition ties, on **synthetic** records;
- A3 non-inheritance of S1;
- restoration timestamps on a **synthetic close-and-reopen** sequence, where
  `first_simultaneous_closure = 7` while `max(first_closure) = 6`;
- the empty and unclosed tracked-set cases;
- all five labels reachable, non-overlapping, dated pendency;
- no float anywhere in a produced report;
- the four protected package identities unchanged;
- preflight refuses on a protected-package mismatch and on an existing output
  location.

**No registered episode was executed at any point before this re-freeze.**
