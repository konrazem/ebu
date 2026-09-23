# Registered Stage A — execution report

**Registration:** `EBU-DEMAND-DRIVEN-STAGE-A-v1`
**Preregistration identity (freeze 3):**
`a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17`
**Mechanism identity, unchanged throughout:** `demand_driven_ebu` =
`f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48`
**Result, of the final attempt (attempt 4):** 768 declared, **768 completed,
0 failed, 0 unstarted**, 11,066 saved epochs. Those counts describe **attempt 4
only**; three earlier attempts exist, are preserved, and are inventoried in §6.

Artifacts: `results/demand_driven_stage_a/`.

**Independent audit.** An independent audit verified all 768 final jobs and all
11,066 saved epochs — physical increments, exact potentials, action receipts,
owner balances, conservation, and aggregate capacity telescoping — and confirmed
that all 768 final epoch sequences equal attempt 3. That is a verification of
**these saved records**: it establishes that what was recorded is internally
exact and consistent. It is **not** a universal correctness proof of the
mechanism, and nothing here should be read as one.

---

## 1. What was run

Three episode classes over the frozen Study-1 world, four policy arms, 64
replicates each: `3 x 4 x 64 = 768` episodes, every one with a distinct run
identity, zero opening balances, `registered=True` and `decomposition_gate=True`.

| class | opening | arrivals | horizon |
|---|---|---|---|
| A1 | `(1,7,4)` | none | 32 |
| A2 | `x* = (4,4,4)` | one stochastic slot, probability 1 | 1 |
| A3 | `(1,7,4)` | one scripted order, one unit at `C`, epoch 3 | 32 |

---

## 2. Observed outcomes

Everything in this section is an **observation about these 768 episodes in this
one world**. None of it is a theorem, a probability, or a comparative result.
§9 of the preregistration governs, and its non-claims are unchanged.

### A1 — pure P-disturbance recovery

| arm | stopping reason | return times observed |
|---|---|---|
| `control_random_no_ebu` | 64 × `RETURNED_TO_REFERENCE` | 2 (×33), 3 (×15), 4 (×6), 5 (×4), 6, 7 (×2), 12, 14, 20 |
| `ebu_random` | 64 × `RETURNED_TO_REFERENCE` | 2 (×33), 3 (×14), 4 (×6), 6 (×5), 7, 8 (×2), 10, 12, 14 |
| `ebu_aligned` | 64 × `RETURNED_TO_REFERENCE` | **2 in every replicate** |
| `ebu_hostile` | 64 × `HORIZON_REACHED` | none within 32 |

`ebu_aligned` returned at the burden-nonincreasing geodesic distance, which was
declared as design arithmetic before any run: **2**. `ebu_hostile` did not
return inside the horizon in any replicate. No episode stopped on
`NO_AFFORDABLE_SOLUTION`, consistent with the declared structural fact that A1
cannot stall on affordability at its first epoch.

### A2 — isolated economic demand at equilibrium

| arm | epoch status | order lifecycle | physical consequence |
|---|---|---|---|
| `control_random_no_ebu` | 64 × `EXECUTED` | 64 × `SERVED` | `B->C@1` (×33, `dV = 1`), `B->C@2` (×31, `dV = 4`) |
| `ebu_random` | 64 × `ALL_PLANS_EBU_UNAFFORDABLE` | 64 × `ADMITTED_BUT_EBU_UNAFFORDABLE` | **none**, `dV = 0` |
| `ebu_aligned` | 64 × `ALL_PLANS_EBU_UNAFFORDABLE` | 64 × `ADMITTED_BUT_EBU_UNAFFORDABLE` | **none**, `dV = 0` |
| `ebu_hostile` | 64 × `ALL_PLANS_EBU_UNAFFORDABLE` | 64 × `ADMITTED_BUT_EBU_UNAFFORDABLE` | **none**, `dV = 0` |

This is the declared, expected-by-construction mechanical outcome, and the two
control post-states reproduce the declared menu exactly: EBU `-1` and `-4` at
`x*`. The order was **admitted and not erased** in all three constrained arms,
and the physical state was untouched — an unaffordable demand is recorded as
distinct from an impossible one and from an absent one.

### A3 — the `E -> P -> restoration` chain

All 256 episodes: **`RESTORATION_COMPLETED`**. The order was admitted and
served at epoch 3 in every episode, with **no** pending epoch in any of them.

#### What `RESTORATION_COMPLETED` does and does not mean

The label and its definition are **frozen and unchanged**. Protocol §4 defines
it as: the order was served, the tracked deficit set was nonempty, and
`first_simultaneous_closure` is defined — where `tracked_deficits` is frozen at
the post-service state `x_{s+1}` and closure is evaluated over **that** set.

So the label means exactly one thing:

> every deficit that existed **immediately after economic service** was
> simultaneously at zero at some later post-state index, within the horizon.

It does **not** mean, and was never defined to mean, any of the following:

- **return to equilibrium.** The tracked set is the deficits present at
  `x_{s+1}`, not the whole deviation. Closing them says nothing about `V`;
- **sustained restoration.** Closure is evaluated at a single index. A
  coordinate may reopen immediately afterwards, and the label does not look;
- **absence of newly created deficits.** Deficits arising at coordinates
  outside the tracked set — including ones the restoring transition itself
  creates — are not in the set and cannot prevent the label;
- **that the episode ended anywhere in particular.** A3 runs to the horizon
  regardless.

#### The hostile witness — the clearest case of the distinction

`A3|ebu_hostile|k=0`, run id `31ba9fef7ec9f577`, read from its saved record:

```
x_0 = (1,7,4) V=9   x_1 = (2,6,4) V=4   x_2 = (3,5,4) V=1   x_3 = (5,3,4) V=1
x_4 = (5,1,6) V=7   <- order served at epoch 3; tracked set frozen here: {B: 3}
x_5 = (4,2,6) V=4
x_6 = (2,4,6) V=4   <- first_simultaneous_closure = 6
...
x_32 = (2,4,6) V=4  <- terminal
```

At `x_6 = (2,4,6)` the tracked coordinate `B` is back to `4`, so the tracked set
is jointly clear and the frozen definition is satisfied: this **is**
`RESTORATION_COMPLETED`, correctly. But `V = 4`, not `0`. `A` stands at `2` — a
**newly created** deficit, outside the tracked set — and `C` at `6`. The arm
then oscillates `(4,2,6) <-> (2,4,6)` for the remaining 26 epochs and **never
reaches `x*`**.

**All 64 `ebu_hostile` replicates close their tracked deficit at exactly
`(2,4,6)` with `V = 4`.** None returns to equilibrium.

#### Equilibrium return — post-execution descriptive clarification

The following counts are **not a preregistered endpoint**. The protocol's §7
declares no equilibrium-return endpoint for A3, and no threshold, test or
comparison is declared anywhere in Stage A. They are a **descriptive
clarification computed after execution** from the saved epoch records alone,
reported so that the frozen label is not misread. They are **not** an
inferential comparison between arms, and they change no frozen classification:
every episode's recorded `order_outcome` stands exactly as written.

"Returned to equilibrium" below means: some post-service post-state equals
`x* = (4,4,4)`.

| arm | tracked-deficit closure | returned to equilibrium after service |
|---|---|---|
| `control_random_no_ebu` | 64 / 64 | **64 / 64** |
| `ebu_random` | 64 / 64 | **63 / 64** |
| `ebu_aligned` | 64 / 64 | **64 / 64** |
| `ebu_hostile` | 64 / 64 | **0 / 64** |

All four arms have 64/64 tracked-deficit closures. The two columns come apart
entirely in `ebu_hostile`, and by one replicate in `ebu_random`: `k=47` closes
its tracked deficit at `x_5 = (3,4,5)` with `V = 1`, never reaches `x*`, and
ends at `(5,4,3)` with `V = 1` — also correctly labelled
`RESTORATION_COMPLETED`.

This is the whole point of the distinction: **64/64 closure and 0/64
equilibrium return are both true of `ebu_hostile` simultaneously**, because they
are answers to different questions. Reading the first as the second would be an
error the frozen definition never licensed.

| arm | arrival baseline `x_3` | reserve at arrival | first simultaneous closure |
|---|---|---|---|
| `control_random_no_ebu` | `(4,4,4)` ×48, `(5,3,4)` ×9, `(5,4,3)` ×4, `(3,5,4)` ×2, `(5,5,2)` ×1 | 9 (×48), 8 (×15), 6 (×1) | 5 (×50), 6 (×13), 7 (×1) |
| `ebu_random` | `(4,4,4)` ×47, `(5,3,4)` ×9, `(5,4,3)` ×6, `(3,5,4)` ×2 | 9 (×47), 8 (×17) | 5 (×50), 6 (×12), 7 (×2) |
| `ebu_aligned` | `(4,4,4)` in all 64 | 9 in all 64 | **5 in all 64** |
| `ebu_hostile` | `(5,3,4)` in all 64 | 8 in all 64 | **6 in all 64** |

Two corrections made before execution are **confirmed by the executed runs**:

1. **The arrival baseline is not `x*`.** Freeze 1 assumed it was. `ebu_hostile`
   arrived at `(5,3,4)` in all 64 replicates, and three other baselines occur
   in the stochastic arms. Correction 1 demoted the `-1` / `-4` figures to
   equilibrium-conditional examples; that was necessary.
2. **The 9 earned units are not all owner `B`'s.** Freeze 1 claimed they were.
   Replicates are recorded with `(A: 1, B: 8, C: 0)`. Correction 1 withdrew the
   universal claim; that too was necessary.

The analytical witness protocol §4 constructed by hand is reproduced
**exactly** by the `ebu_hostile` arm: baseline `(5,3,4)`, pre-arrival vector
`(0, 8, 0)`, and the four-plan menu

| plan | post-state | EBU | receipts | affordable |
|---|---|---|---|---|
| `{A->B@2, B->C@1}` | `(3,4,5)` | `0` | `A: +1, B: -1` | yes |
| `{A->B@2, B->C@2, C->B@1}` | `(3,4,5)` | `0` | `A: +1, B: -2, C: +1` | yes |
| `B->C@1` | `(5,2,5)` | `-2` | `B: -2` | yes |
| `B->C@2` | `(5,1,6)` | `-6` | `B: -6` | yes |

`ebu_hostile` selected `B->C@2`, the `argmin`, as its rule requires.

---

## 3. Observations versus guarantees

**Mathematical guarantees** (proved, independent of these runs): the service
predicate and its guarded economic clause; served-set-relative irredundancy;
Theorem D over the frozen domain; **conditional** restorative refinement;
768/768 identity uniqueness by construction; and the 91/91 accessibility
result, which is a statement about reachability, **not** about recovery,
affordability or policy behaviour.

**Observations** (the 768 episodes of attempt 4 only): every number in §2. In
particular "all 256 A3 episodes are `RESTORATION_COMPLETED`" is an observation
about one world, one displacement, one order, one schedule and 64 replicates per
arm — and, as §2 sets out, it is a statement about **closure of the deficits
tracked immediately after service**, not about equilibrium return. `ebu_hostile`
is 64/64 on the first and 0/64 on the second. It is **not** evidence that any
arm restores in general or with any probability, and no comparison between arms
is offered as a tested result. Stage A carries no hypothesis and performs no
test.

**Neither category** (post-execution descriptive clarification): the
equilibrium-return counts in §2. They were computed after execution, answer no
preregistered question, and are reported only so the frozen label is not
misread.

**Disposed by author acceptance, and in neither category**: whether the
runner's integrity predicate conformed to the frozen protocol. See §5. Verified
numerical integrity does not settle it, and the acceptance is bounded rather
than a precedence ruling.

---

## 4. Integrity

Verified after execution by `python3 -m demand_driven_stage_a.verify`
(read-only; runs no model code): **36 checks, 0 failed**.

- attempt 4: 768 completed, 0 failed, 0 unstarted; no halt on an integrity
  failure. 11,066 saved epochs (A1 2,618; A2 256; A3 8,192);
- all four residuals exactly `0` at every epoch of all 768 episodes;
- the joint gate closed at every epoch; the decomposition gate `VERIFIED` at
  every epoch that carried active demand (see §5 for the no-demand epochs and
  the open protocol question);
- mass exactly `12` and every stock nonnegative at every recorded state;
- epoch EBU equals `V(pre) - V(post)` exactly at every epoch;
- every recorded run identity equals the one the registry rebuilds today;
- the source snapshot reproduces all 46 manifested files byte for byte;
- the four protected package identities unchanged before, after and now.

### Exactness, scoped precisely

Exact rational arithmetic throughout the mechanism and the reports. **Every
scientific quantity** — states, potentials, EBU, receipts, balances, residuals,
deficits, restoration ledgers — is stored as `numerator/denominator` and passes
through no float at any point.

The claim is scoped to scientific quantities, and one exclusion is recorded
rather than glossed: `EXECUTION_INVENTORY.json` carries
`elapsed_seconds` as a float (wall-clock duration, `58.844`). A scan of the
complete artifact set finds it is **the only float anywhere**:

| artifact | floats |
|---|---|
| `EPISODES_A1/A2/A3.json.gz` | none |
| `JOB_MANIFEST.json`, `SOURCE_MANIFEST.json`, `PREFLIGHT.json` | none |
| `EXECUTION_INVENTORY.json` | `elapsed_seconds` only — **runtime metadata, not a scientific quantity** |

Nothing scientific is derived from it and no report reads it.

### Independent audit

An independent audit verified all 768 final jobs and all 11,066 saved epochs:
physical increments, exact potentials, action receipts, owner balances,
conservation, and aggregate capacity telescoping; and it confirmed that all 768
final epoch sequences equal attempt 3.

**What that establishes, and what it does not.** It establishes that the saved
records are internally exact and mutually consistent, and that the attempt-4
correction altered no trajectory. It is **not** a proof that the mechanism is
correct in general, nor that the frozen protocol was implemented faithfully —
§5 records one question of exactly that kind, closed by a bounded author
acceptance rather than by proof. Verified numerical integrity and protocol
conformance are separate claims and are kept separate here.

---

## 5. Post-execution protocol-deviation record

One deviation from the frozen preregistration exists in the **runner**, not in
the protocol. It is recorded here in full. **The frozen preregistration has not
been touched**: its identity is still
`a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17`.

### The two frozen requirements, quoted exactly

`DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` §7, the A3 reporting table, line 658:

> | `joint_gate`, `decomposition_gate` | must be verified at every epoch |

`DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` §8, "Integrity conditions that
invalidate a job", line 671:

> - a joint-gate or decomposition-gate refusal;

The first requires the gates to be *verified* at **every** epoch. The second
invalidates a job on a gate *refusal*. These are different predicates, and in
A3 they diverge.

### Why they diverge

`EconomyRun._check_decomposition` returns `DECOMPOSITION_NOT_CHECKED` when
`not self.decomposition_gate or not found`. The gate flag is `True` for every
registered job, so the reachable case is `not found` — **no demand components**,
which occurs exactly when the active demand set is empty. A gate **defect** is
never a status: `_check_decomposition` raises `Refusal` on disagreement, so a
refusal reaches the runner as an exception.

A1 never records such an epoch, because it stops on reaching `x*`. A3
necessarily does, because protocol §4 declares that A3 does **not** stop there
and runs to the horizon. Under protocol §7 read literally, every A3 episode that
ever reaches `x*` would be invalid — which is unattainable by construction
rather than a property of any outcome. Measured against the saved records, that
is **192 of the 256** A3 episodes and **4,737** epochs, not all of them; the
counts are broken out below.

### An unchecked no-demand epoch is not a gate refusal

| | refusal | `DECOMPOSITION_NOT_CHECKED` at a no-demand epoch |
|---|---|---|
| what happened | the component path and the decomposition-free policy-conditioned reference **disagreed** | there were no components, so no comparison was defined |
| how it surfaces | `Refusal` raised, job aborts | a recorded status |
| what it evidences | a real defect in decomposition | that the epoch had nothing to decompose |
| is anything unverified? | yes — a disagreement was found | no — there was no claim to verify |

The premise is checked against the mechanism on a declared state, executing
nothing: at `x*`, `derive_physical_demands` returns `()`, and `components` on an
empty active set returns `()`.

### The exception, exactly as implemented

Introduced in `demand_driven_stage_a/execute.py`, in
`epoch_integrity_failures`:

```python
if record.decomposition_gate != DECOMPOSITION_VERIFIED:
    no_demand = (
        record.epoch_status == STATUS_NO_ACTIVE_DEMAND
        and not record.active_physical
        and not record.active_economic
    )
    if not (record.decomposition_gate == DECOMPOSITION_NOT_CHECKED and no_demand):
        bad.append(
            f"epoch {record.epoch}: decomposition gate {record.decomposition_gate}"
        )
```

The guard is conjunctive and narrow: the status must be exactly
`DECOMPOSITION_NOT_CHECKED`, the epoch status exactly `NO_ACTIVE_DEMAND`, **and**
both active demand tuples empty. Any non-`VERIFIED` gate at an epoch that
carried demand still invalidates the job, and a regression confirms it.

### When it was introduced, and which attempts it affected

Between attempt 2 and attempt 3 — that is, **after** an epoch had been executed
under freeze 3, which is what makes this a post-execution deviation rather than
a pre-execution correction.

| attempt | `execute.py` sha256 | exception present | outcome |
|---|---|---|---|
| 1 | `6f67e3a96c3b4d87…` | no | halted at job 1 (unrelated tooling defect) |
| 2 | `596cd8700ccdfa63…` | no | **halted at A3 job 1 on this discrepancy**, after 512 jobs |
| 3 | `ab26e107a003f45e…` | **yes** | 768 completed; superseded for an unrelated reporting defect |
| 4 | `f6a8641c8d7e75d5…` | **yes** | final reported set |

`demand_driven_ebu` was `f4e31a2a3f0fa019…` and `unchanged=True` in all four
saved manifests. `reporting.py` was `8ade00855d0ea04d…` for attempts 1–3 and
`25c14290c3e33b54…` for attempt 4; that change is the affordability column
(§6), unrelated to this deviation.

### Scope of the exception, measured

The exception is **not** invoked across A3 as a whole. Counted from the saved
records:

| class | episodes with ≥1 exempted epoch | exempted epochs |
|---|---|---|
| A1 | 0 / 256 | 0 |
| A2 | 0 / 256 | 0 |
| A3 | **192 / 256** | **4,737** |
| **total** | **192 / 768** | **4,737 of 11,066** |

By arm within A3:

| arm | episodes | exempted epochs |
|---|---|---|
| `control_random_no_ebu` | 64 / 64 | 1,439 |
| `ebu_random` | 64 / 64 | 1,506 |
| `ebu_aligned` | 64 / 64 | 1,792 |
| `ebu_hostile` | **0 / 64** | **0** |

A1 and A2 contribute nothing: A1 stops on reaching `x*` and A2 is a single
epoch. `ebu_hostile` contributes nothing either, and for a substantive reason —
it never returns to equilibrium (§2), so it never reaches an epoch with no
active demand. The exception is reached only by arms that restore.

**Every `DECOMPOSITION_NOT_CHECKED` epoch in all 768 episodes satisfies the full
three-part guard; zero fall outside it.** So the exception is exactly
coextensive with the accepted scope, and no epoch relies on anything broader.

### Author disposition — ACCEPTED, narrowly scoped

Recorded here as the author's disposition. It is **separate from, and does not
alter, the frozen requirements quoted above**, which stand unchanged in the
sealed preregistration.

> The author accepts the documented no-demand decomposition-check exception as
> a **narrowly scoped post-execution operational deviation**.

The acceptance applies **only** where all three hold together:

1. `decomposition_gate` is `DECOMPOSITION_NOT_CHECKED`;
2. `epoch_status` is `NO_ACTIVE_DEMAND`; and
3. both active demand sets are empty.

It expressly does **not**:

- waive any active-demand check, anywhere;
- waive or soften any gate refusal;
- establish general precedence of protocol §8 over protocol §7;
- amend the frozen preregistration, whose identity is unchanged at
  `a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17`;
- authorize Stage B.

The protocol §7 / §8 question is therefore **not resolved in general**. It is
disposed of for this execution, at this scope, by author acceptance — not by a
precedence ruling. Any future study must read the frozen text afresh.

### What the acceptance does and does not rest on

- **Verified, numerical, independent of the disposition.** The 768 final jobs
  and 11,066 saved epochs are internally exact and consistent, independently
  audited; the decomposition gate is `VERIFIED` at **every epoch that carried
  active demand** across all 768; no epoch anywhere recorded a gate refusal.
- **Disposed by acceptance, not proved.** That an exempted epoch is
  operationally acceptable despite protocol §7's literal "every epoch". The
  4,737 epochs are the ones covered.

These are recorded separately and must not be merged: the first would survive a
different disposition, the second would not.

---

## 6. Attempt history

Execution was attempted **four** times. **Every attempt is preserved on disk
permanently; none was deleted or overwritten, and none is to be** (§8). Each
correction was to the *runner*, never to the mechanism, the protocol or the
seeds. The frozen preregistration
was **not** amended after the first epoch ran.

The reported result set is **attempt 4 alone**. The headline counts "768
completed, 0 failed, 0 unstarted" describe attempt 4 and no other attempt;
attempts 1 and 2 did not complete, and attempt 3 completed but is superseded.

| attempt | jobs completed | jobs failed | jobs unstarted | disposition | preserved at |
|---|---|---|---|---|---|
| 1 | 0 | 1 | 767 | halted — tooling defect | `results/demand_driven_stage_a_FAILED_ATTEMPT_1/` |
| 2 | 512 | 1 | 255 | halted — protocol §7/§8 discrepancy (§5); **retain permanently** | `results/demand_driven_stage_a_FAILED_ATTEMPT_2/` |
| 3 | 768 | 0 | 0 | complete; **superseded** for a derived-column defect | `results/demand_driven_stage_a_SUPERSEDED_ATTEMPT_3/` |
| **4** | **768** | **0** | **0** | **reported set** | `results/demand_driven_stage_a/` |

Attempt 3 is superseded, **not** invalid: its 768 epoch sequences are the ones
reported, byte for byte. Only a derived reporting column differed.

### Attempt 2 — the decomposition-gate predicate

Recorded in full in **§5**, including the exact quotations, the guard, the
measured scope (192 A3 episodes, 4,737 epochs), the affected attempts and their
source identities. Its disposition is **closed by bounded author acceptance**,
recorded in §5 separately from the frozen requirements.

### Attempt 3 — the affordability column

The A3 `candidate_table` decided affordability against the arrival epoch's
**closing** balances rather than the pre-arrival vector protocol §4 declares.
That subtracts the chosen plan's own cost before asking whether that plan was
affordable, and it reported `B->C@2` as unaffordable **inside the record that
executes it** — a self-contradiction within one artifact.

The column now uses the recorded pre-arrival owner vector and the mechanism's
own `CapacityLedger.is_affordable`, rather than a re-implementation of the rule,
and so also respects the control arm's unconstrained ledger.

**This changed no trajectory, and the distinction is load-bearing.**

| | attempt 3 | attempt 4 |
|---|---|---|
| epoch records (all 768 jobs, 11,066 epochs) | — | **identical**, verified record by record and confirmed by the independent audit |
| `candidate_table.affordable_per_owner` / `affordable` | computed against closing balances — **wrong** | computed against the recorded pre-arrival vector via the mechanism's own `CapacityLedger.is_affordable` |

What changed is **derived reporting** recomputed from unchanged saved
trajectories. What did not change is anything the mechanism produced: no state,
potential, receipt, balance, residual, gate status, plan choice or stopping
reason differs between the two attempts. A permanent check now refuses any
report that marks the executed plan unaffordable.

### On correcting a runner mid-study

No parameter, world, tolerance, classification, hypothesis, seed, horizon,
policy or episode definition was changed at any point, and nothing was changed
to make an outcome more favourable. No recorded `order_outcome`, stopping reason
or other frozen classification was altered, then or since. The two substantive
corrections were both forced by internal contradictions — a predicate
unattainable by construction, and a column contradicting its own record — and
both are demonstrable without reference to any outcome. All 768 episodes in the
reported set were produced by a single uninterrupted run of one runner version.

That said, one of those corrections was made **after** epochs had run under the
current freeze, and it turns on reading protocol §8 rather than protocol §7.
That reading is still **not** ratified: §5 records the author's acceptance of it
as a narrowly scoped operational deviation, which is not the same as declaring
protocol §8 governing. It is kept separate from the verified numerical
integrity, which does not depend on it.

---

## 7. Scope

Stage B was not started. No AWS, no cloud execution, no parameter search, no
mechanism redesign, no book changes. Nothing was committed or pushed.

---

## 8. Closeout status

> ## Execution and numerical audit complete;
> ## accepted with a documented operational deviation.

| item | status |
|---|---|
| registered execution | **complete** — attempt 4, 768/768, 11,066 saved epochs |
| numerical integrity | **verified**, independently audited over all jobs and epochs |
| frozen preregistration | **untouched**, identity `a74d8380…` |
| mechanism | **untouched**, identity `f4e31a2a…` |
| all four attempts | **preserved permanently**, none overwritten |
| A3 endpoint meaning | **clarified** (§2); frozen label and definition unchanged |
| equilibrium-return counts | **recorded** as post-execution description, not an endpoint |
| protocol §7 / §8 integrity-predicate discrepancy | **CLOSED by author acceptance** — narrowly scoped operational deviation (§5) |

**No open items remain.** Stage A is closed.

### What the closure does not carry forward

The acceptance in §5 is bounded, and the boundary is part of the closure:

- it covers only `DECOMPOSITION_NOT_CHECKED` + `NO_ACTIVE_DEMAND` + both active
  demand sets empty — **192 A3 episodes, 4,737 of 11,066 epochs**;
- it waives **no** active-demand check and **no** gate refusal;
- it establishes **no** general precedence of protocol §8 over protocol §7;
- it amends **nothing** in the frozen preregistration;
- it authorizes **no** Stage B work.

Stage B remains unauthorized and unfrozen. Its arrival law, disturbance law, arm
set, endpoint and replicate count are all still open, and nothing in this
closeout bears on any of them.

### Permanent preservation

The deviation record (§5) and the complete attempt history (§6) are to be
**retained permanently**, together with all four attempt directories:

```
results/demand_driven_stage_a/                      attempt 4 -- the reported set
results/demand_driven_stage_a_SUPERSEDED_ATTEMPT_3/ superseded, trajectories identical
results/demand_driven_stage_a_FAILED_ATTEMPT_2/     halted on the §7/§8 discrepancy
results/demand_driven_stage_a_FAILED_ATTEMPT_1/     halted on a tooling defect
```

None of these is to be deleted, pruned or overwritten. The failed and superseded
attempts are the evidence that the deviation was found, recorded and bounded
rather than absorbed silently; a closure that kept only the successful attempt
would not be auditable.
