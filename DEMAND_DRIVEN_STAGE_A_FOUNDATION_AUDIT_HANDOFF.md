# Auditor handoff — strong atomic P-provenance and Stage-A registration integrity

**Read-only, self-contained.** Everything needed to check this pass is named
below; no prior conversation is required.

**Nothing was committed.** `AGENTS.md` permits commits only when explicitly
authorized, and no authorization was given.

**No Stage A ran.** No Stage-A epoch, trajectory, arm outcome or aggregate was
generated. The only thing done to a Stage-A fixture was object *construction*,
which sets an opening state and a zero ledger and advances nothing. Epochs were
executed only inside the conformance suite, on its own synthetic fixtures,
exactly as that suite has always done.

---

## The question

> **Does the final implementation satisfy strong atomic P-provenance, and is
> the registered Stage-A protocol collision-free, unambiguous and executable?**

Requested verdict:

```
STAGE-A FOUNDATION ACCEPTED — RUN REGISTERED STAGE A
```

or

```
RETURN FOR CORRECTION
```

---

## 1. The six audit findings, and what was done

| # | finding | correction | where to check |
|---|---|---|---|
| 1 | sequential refinement could still fail: a newly created P-demand was forced into a joint-service component | **strong atomic provenance** — progress on *at least one* pre-state P-demand, never on every one | `service.serves_all`; contract §2.1; §2 below |
| 2 | A1/A3 run-id collision | run identity rebound to the complete declared episode, arrival and disturbance laws included | `harness.EconomyRun.configuration`; §4 below |
| 3 | A3 claimed all 9 units of prelude capacity belong to `B` | **withdrawn**; aggregate retained as an identity, owner vector declared policy-dependent and read from the record | preregistration §4 |
| 4 | A1 stop semantics ambiguous, and required an extra epoch | one epoch convention, one return-time definition, `T` = transitions, no extra epoch | preregistration §2 |
| 5 | `PhysicalService` quantities were not recorded anywhere | persisted on `EpochRecord.restoration` at the epoch they happen | `harness.EpochRecord`; §5 below |
| 6 | one tautological affordability regression | replaced by three exact fixtures: all / some / none affordable | §6 below |

---

## 2. Strong atomic P-provenance — the rule, and the three things it must not break

**The rule.** A plan has legitimate physical provenance exactly when it makes
strict positive progress on **at least one** P-demand existing at the
pre-action state. Deficits that remain, worsen or are newly created are
represented in the post-state and re-derived for the next decision. Economic
service is untouched: complete, additive, no partial fulfilment, no backlog.

**Provenance and valuation are never collapsed.** Provenance answers *why may
this action be considered*; EBU answers *what is the complete physical
consequence*, as `E = V(pre) - V(post)` over the whole transition with every
side effect at full weight. At `(2,3,7)` the plan `B->A@1` restores `A`,
deepens `B`, is legitimate, and is worth exactly `0`. Affordability and every
policy see that number. `value_group` is never told which demand supplied the
provenance — checked by signature.

**(a) Refinement.** `(1,4,7)`, `x* = (4,4,4)`: `B->A@2` is legitimate and worth
`+2`. Split into `B->A@1` twice, the first half is worth `+2` and creates a new
deficit at `B`; the second half is worth `0` and **stays legitimate**. Neutral
EBU does not erase provenance. Exhaustively: **152** legitimate two-unit
restorations exist in the frozen world and **zero** lose legitimacy when split.

**(b) No unrelated-action leak.** Over all 91 states and all **420** menu
plans, every plan progresses some deficit existing at its own pre-state — zero
exceptions. At `(5,4,3)` the menu is still exactly the two `B->C` restorations;
`A->B@1` is executable there and still illegal, and becomes legitimate only at
`(5,3,4)`, where a `B`-deficit exists.

**(c) Coupling.** P-coupling survives as a physical-conflict relation — shared
stock, shared routes, joint executability — and no longer carries a
joint-service contract. **Two consequences were followed through rather than
absorbed, and these are the parts to attack hardest:**

1. **Irredundancy became served-set relative.** A proper subset makes a plan
   redundant only when it executes *and* answers everything the plan answers. A
   plain "does some subset serve?" test collapses every joint plan — an
   economic order and a physical restoration answered in one epoch would reduce
   to the economic action alone, making one class wait for the other. The guard
   is unchanged in force: a bolted-on action answers nothing new, so dropping
   it preserves the served set and the padded plan is refused.
2. **Contract §6 protection moved to a coexistence question.** Serviceability
   can no longer see that a new order would starve an existing need, because a
   plan serving the order need not progress the need. `admission.starved_ids`
   asks whether *some* plan completely serves the new orders **and** progresses
   every existing need. It is the **only** place the conjunction is asked, and
   nothing in the runtime menu inherits it. The witness: `protect-v1`, one unit
   of stock, an order of 3 at `C` beside a shortfall of 3 at `B` — serviceable,
   not coexistent, and refused.

---

## 3. The recomputed accessibility result

Rebuilt from the implemented successor map over all 91 states. **The `<=5`
bound and the 91/91 results were not forced**: strong provenance both adds
edges (restore one deficit, deepen another) and removes them (a joint plan is
redundant when a subset answers everything it answers). These are what the
enumeration returned.

| quantity | withdrawn complete-service | first atomic rule | **implemented strong rule** |
|---|---|---|---|
| menu plans offered | 99 | 226 | **420** |
| distinct successor edges | 99 | 226 | **408** — 327 down, 33 neutral, 48 up |
| absorbing states | 37 (36 non-equilibrium) | 1 | **1 — `x*` alone** |
| `x*` reachable at all | 31 / 91 | 91 / 91 | **91 / 91** |
| by burden-nonincreasing paths | 31 / 91 | 91 / 91 | **91 / 91** |
| by strict descent alone | 23 / 91 | 83 / 91 | **89 / 91** |
| longest burden-nonincreasing distance | — | 5 | **5** |
| plateau-locked states | 4 | 2 | **2** — `(3,4,5)`, `(5,4,3)` |
| plateau components with no lower exit | 36 | 0 | **0** |

`x*` remains the only absorbing state, and no exact physical reason was found
for any other.

> **This is a PHYSICAL / DEMAND-MENU result.** It does not say every state is
> EBU-affordably recoverable, that any policy reaches equilibrium, or that
> recovery probability is 1. L (location, proved), R (accessibility, settled)
> and P (policy dynamics, open) are kept apart throughout, and P is what Stage
> A and Stage B exist to observe.

**One direction of the over-coupling artifact reversed, and is recorded.**
Merging independent needs used to make service harder; it now makes it easier,
because "serve the component" is existential. On `sandwater-v1` at
`(8,12,10,4,8)` the correct decomposition offers 18 outcomes and the
over-coupled one offers 27 — the 9 extra being exactly those with zero
increment at one of the two requirement coordinates. The runtime authority is
unaffected: `global_progress` and `component_progress` agree exactly.

**The decomposition-free reference had to be restated.** "Serves the union of
every part" and "serves each part" stopped being the same condition when
physical service became existential, so `oracle.plans_serving_every_part`
enumerates over the whole world and tests the parts, with minimality taken
against the conjunction. Per-part minimality would return nothing at all.

---

## 4. Registered run identity

`run_id = sha256(configuration)[:16]`, where `configuration` serializes:

```
MODEL_ID | registration | episode | world | policy | opening-state digest
        | disturbance descriptor | arrival descriptor | seeds | replicate
        | registered flag | decomposition-gate flag
```

Every process object carries an exact `descriptor` in rational form; a scripted
schedule serializes its **contents epoch by epoch**; a process without a
descriptor is **refused**, not reduced to its class name.

Checked by construction alone, **zero epochs executed**:

- **768 / 768** distinct run identities across `3 episodes x 4 arms x 64 replicates`;
- rebuilding every job reproduces the identical 768 identities;
- changing episode, replicate, registration, opening state, disturbance law or
  arrival law each changes the identity;
- A1 and A3 share world, policy, opening state and all four seeds and are
  nevertheless distinct, with `ScriptedArrivals(script={3:[r|C|1/1]})` appearing
  verbatim in A3's configuration.

---

## 5. A1 semantics, terminal statuses, and reporting

**Epoch convention.** `epoch t`: observe `x_t`, process, produce `x_{t+1}`. `T`
is the **number of transitions**, never a maximum index.

**Return time** = `min { t+1 : x_{t+1} = x* }`. The episode stops immediately
after recording that transition. **No extra epoch is executed to observe
`NO_ACTIVE_DEMAND`**; that status is derived from the post-state.

**Terminal statuses.** `RETURNED_TO_REFERENCE`, `NO_AFFORDABLE_SOLUTION`,
`HORIZON_REACHED`. **`NO_COMPLETE_PHYSICAL_PLAN` at a non-equilibrium state is
no longer listed as a normal terminal condition** — `x*` is the only absorbing
state, so it cannot arise from the declared physics; it is an integrity failure
that invalidates the job.

**Reporting.** `EpochRecord.restoration` persists the selected plans'
`PhysicalService` records — represented deficit, delivered, credited progress,
remainder, overshoot — at the epoch they happen. A regression checks they equal
the candidate plan's own records verbatim, and that the remainder is what the
next derivation reads off the new state rather than a stored obligation.

---

## 6. Affordability, with concrete fixtures

The tautology is gone. Three exact cases, all at zero opening balances:

| case | fixture | result |
|---|---|---|
| **all** affordable | `(1,7,4)` | 2 of 2 — both restorations earn (`+5`, `+8`) |
| **some** affordable | `(4,3,5)` | 3 of 4 — the excluded plan is exactly `A->B@2`, whose owner would reach `-2` |
| **none** affordable | `x*` + one order of 1 at `C` | 0 of 2 — both cost (`-1`, `-4`) and no reserve has been earned |

---

## 7. Change set and verification

**Package:** `service.py` (the predicate, `serves_jointly`, `served_ids`),
`enumeration.py` (served-set-relative irredundancy, `physically_coexistent`),
`admission.py` (`starved_ids` and the protection limb), `oracle.py`
(`plans_serving_jointly`, `plans_serving_every_part`, the narrow query),
`plans.py` (accurate `served`, precise provenance), `harness.py` (configuration
identity, persisted restoration), `arrivals.py` / `disturbance.py` /
`fixtures.py` (canonical descriptors), `study_one.py` (domain wording).

**Documents:** contract (correction-log rows 12–14, §2.1, §3, §4, §6), findings
F-7, Study-1 domain (conditions 13a/13b), readiness, the Stage-A
preregistration, the synthesis (status wording only), the sufficient-state
companion study (figures recomputed), and this handoff.

**Not touched:** `gaussian_harness`, `capacity_v2`, `homeostasis` — all three
code identities asserted unchanged by the conformance suite — `books/`, and
every committed result artifact and manifest.

| suite | result |
|---|---|
| `test_demand_driven_ebu.py` | **1045 passed, 0 failed, 209 groups** |
| `dynamic_ebu_theory_checks.py` | **288 deterministic checks, 0 failed** |
| `test_gaussian_foundation.py` | 65 / 0 |
| `test_capacity_v2_foundation.py` | 61 / 0 |
| `test_homeostasis_foundation.py` | 146 / 0 |
| `test_restoring_tendency.py` | 26 / 0 |
| `test_study_harness.py` | 120 / 0 |
| `test_study_protocol_schema.py` | 68 / 0 |
| `test_gaussian_harness.py` | 68 / 0 |
| `test_capacity_v2_harness.py` | 28 / 0 |
| `test_homeostasis_harness.py` | 109 / 0 |

Exact rational arithmetic throughout; every tolerance literally zero; no
randomized search anywhere in the checks added by this pass.

**Retained regressions**, all still passing: additive E-orders, E/P overlap,
atomic P, overshoot permitted, no unrelated provenance, independent progress,
the three search verdicts, coupling invariance, conservation, exact EBU, receipt
closure, replay construction, and every previous auditor counterexample.

**Preregistration identity.**
`DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` →
`72a950721a81a7e0e2dba28e1a1a47124769a3378a4d28cd34d7e1f8aace78de`,
recomputed by `scripts/stage_a_preregistration_identity.py`, which executes no
model code. The document records:

> **Zero registered Stage-A epochs have been executed under this
> preregistration.**

---

## 7a. Reconciliation pass (post-audit), execution-free

The audit confirmed the implementation and found that four documents did not
describe it. A bounded reconciliation pass corrected the documents. **No line of
`demand_driven_ebu` changed**: its identity is still
`f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48`, and no
document was made true by changing the mechanism.

| finding | correction |
|---|---|
| contract §3 stated the predicate as a conjunction, excluding economic-only service (A2 at equilibrium) | §3 now states it exactly: **every** economic claim complete, **and** the plan serves something — an economic claim exists and is complete, **or** at least one pre-state physical demand is progressed. An empty requirement set supplies no provenance |
| contract §7 still described the withdrawn irredundancy rule | replaced by served-set-relative redundancy, with the `(3,6,3)` regression: `{B->A@1, B->C@1}` serves both needs, each singleton serves one, and the joint plan is **not** redundant |
| Theorem D was stated against "serves the union" | restated against "serves each live part", with **every implication rechecked** rather than re-worded. Lemma 1 (delivery) had to be re-derived from served-set minimality; both inclusions survive. The dependency surface is now declared: the reference is independent of `coupling` and `plans`, and **shares** `service.serves_all` / `served_ids` and `enumeration.is_irredundant`, so the gate cannot catch a defect in the predicate itself |
| A3 asserted `-1`/`-4` "regardless of path" | demoted to equilibrium-conditional examples; analytical witness added that the arrival baseline need not be `x*`; affordability decided per owner from the recorded vector; four non-chain outcomes defined |
| A1 reporting contradicted §2 | one epoch convention, one return-time definition, `NO_PHYSICAL_SOLUTION` removed, horizon distinguished from transitions recorded, the physical-impossibility integrity claim scoped to A1 |
| refinement claimed as unrestricted | restated as **conditional restorative refinement**: 152 legal two-unit restorations, 120 with both halves legitimate, 32 where the first half clears the deficit and the second is correctly refused, **0** failures of the conditional statement |

Preregistration identity: superseded `72a9507…`, **proposed** `36fb53b6…`,
recorded in `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION_CORRECTION_1.md`. Freeze 2
is proposed and **not claimed as authorized**: `AGENTS.md` defines no procedure
for re-freezing an uncommitted, unexecuted preregistration, and the author's
confirmation is the authorization required.

## 8. Where an auditor should push hardest

1. **Served-set-relative irredundancy.** It is the subtlest change here. Try to
   find a padded plan it admits, or a legitimate joint plan it refuses.
2. **The coexistence limb.** It is the one place a conjunction survives. Check
   it has not leaked into `service_reach`, into any menu, or into
   `physically_serviceable`.
3. **That the accessibility result is nowhere overstated** as affordability,
   policy behaviour or recovery probability.
4. **The Stage-A arrival schedule decision.** A3 uses `ScriptedArrivals`, whose
   prohibition was scoped — in a prior pass — to registered *behavioural
   comparisons* rather than to Stage-A mechanism episodes. That is a
   declaration, not a code change, and it remains the one judgement call in the
   protocol. A1 and A2 use declared process objects only.
