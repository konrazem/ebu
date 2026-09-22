# Study-1 readiness: the finite completeness argument, and what is still open

**Status: READY FOR DEMAND-DRIVEN STAGE-A/B PREREGISTRATION DESIGN.**
This is not permission to execute. No registered study has run, the arrival
law is unfrozen, and the primary endpoint is unchosen.

Companion documents: `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` (the freeze and the
three theorems), `DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md` (the decisions
still required), `DEMAND_DRIVEN_MODEL_FINDINGS.md` (F-1 to F-6).

---

## 1. Gates

| gate | state |
|---|---|
| Study-1 physical domain frozen and machine-checked | **yes** — `study_one.domain_violations`, 17 conditions |
| documentation corrected: no general loss/capacity-aware exactness claimed | **yes** — contract §6 and §16, `enumeration`, `coupling` |
| route liveness proved where it is claimed | **yes** — L1 necessary everywhere, L2 sufficient in the domain |
| out-of-domain counterexamples retained, not forgotten | **yes** — F-5, F-6, both permanent regressions |
| plan-size cap classified computational, and non-binding in Study 1 | **yes** — domain condition 16 |
| exhaustive enumeration, or a pruning proved equivalent | **yes** — Theorem P, plus a brute-force cross-check |
| three search verdicts maintained and never collapsed | **yes** |
| `SEARCH_UNRESOLVED` proved impossible in the declared domain | **yes** — domain condition 17 |
| registered failure semantics implemented | **yes** — `JobInvalid`, `EconomyRun(registered=True)` |
| the decomposition-free **progress** reference is the authority; decomposition proved equal and gated at four levels | **yes** — Theorem D, `decomposition_gate=True` |
| independent progress: a blocked part contributes nothing, every serviceable part acts | **yes** — `oracle.global_progress`, mandatory-action regressions |
| sampling unit frozen as the canonical plan identity, with the induced outcome law carrying multiplicity | **yes** — `two_supplier_world`, `1/4, 1/2, 1/4` |
| the oracle is policy-conditioned: physical eligibility, affordability, mandatory inaction, and each arm's execution law | **yes** — `oracle.policy_levels`, run by the gate every epoch |
| `ALL_PLANS_EBU_UNAFFORDABLE` kept distinct from impossibility, scarcity and computational failure | **yes** — four separate declared statuses |
| unusable-infrastructure invariance across all five outputs | **yes** |
| additive service, provenance, sinks, closed cycle, actor-only | **yes** — carried forward unchanged |
| exact conformance passing | **yes** — 935 assertions, 0 failures, tolerance 0 |
| Study-1 rehearsal clean | **yes** — 3,200 epochs, 0 unresolved, 0 incomplete, residuals exactly 0 |
| arrival law declared | **no** — §4 |
| primary endpoint chosen | **no** — §4 |
| findings-forced decisions taken | **no** — packet §3.3 |
| power argument | **no** |
| preregistration frozen | **no** |

## 2. The finite completeness argument

For the declared Study-1 rehearsal world `study-one-v1` — three stocks in a
line `A <-> B <-> C`, four routes, quanta `{1, 2}`, total resource 12,
references `(4, 4, 4)`. Every number below is computed by
`study_one.completeness_bound`, not asserted.

| quantity | value |
|---|---|
| coordinates | 3 |
| usable routes | 4 |
| declared quanta | 2 |
| **maximum number of atomic actions** | **8** = `sum_r |{q <= cap(r)}|` |
| **maximum exact search space** (complete plan space) | **80** = `3^4 - 1` |
| exhaustive budget | 200,000 |
| plan-size cap | 4 |
| cap binds | **no** (`4 >= 4` usable routes) |
| `SEARCH_UNRESOLVED` possible | **no** |

**Maximum possible active demand count.** Physical demand is derived per
coordinate and is unique there, so `|D^P| <= 3`. Economic demand accumulates
only while admitted and unserved, so `|D^E|` is bounded by the arrival law and
the horizon, which are not yet frozen. This does **not** enter the search
bound: `service.requirements` aggregates the whole demand set into at most one
requirement per coordinate, so the requirement set has at most 3 members
however many demands are active, and the plan space is a property of the world
alone. The demand count enters only linearly, through the number of
per-demand reach computations.

**The enumeration algorithm actually used.**

1. `structural_reach` selects the live routes delivering into the requirement
   coordinates. In Study 1 the capacity-relief limb is empty, so this is one
   pass.
2. `physically_serviceable` enumerates plans over those routes, at most one
   action per route, **in increasing plan size**, and returns `SERVICEABLE` on
   the first complete executable plan. Size order matters: a wide but easy
   requirement is answered in a handful of evaluations rather than after a
   walk through the large end of the space.
3. Exhausting the space without a hit returns `IMPOSSIBLE`. Exhausting the
   *budget* first returns `UNRESOLVED` — which condition 17 makes unreachable
   here, because the whole space is 80 against a budget of 200,000.
4. Menus are enumerated over the component's transport closure with the
   plan-size cap, which cannot bind, and filtered by complete service,
   executability and irredundancy. Irredundancy inspects every proper subset:
   at most `2^4 = 16` per candidate.

**Why no scientific search truncation exists.** Three separate limits could in
principle truncate, and all three are neutralised:

- the *plan-size cap* cannot bind (condition 16), so it removes no plan;
- the *structural-reach pruning* is proved equivalent to complete enumeration
  (Theorem P) and cross-checked against a brute force that never consults
  `enumeration`, over all 91 integer states of this world and four order
  sizes;
- the *exhaustive budget* cannot be reached (condition 17).

Nothing else narrows the space. Serviceability is therefore decided by exact
exhaustive enumeration of the complete finite plan space in every Study-1
state.

**Expected worst-case runtime, locally.** Measured, not estimated:
`demand_driven_rehearsal.py`, 4 policies × 4 replicates × 200 epochs = 3,200
epochs, **22.5 s per pass with the four-level policy-conditioned gate on**,
run twice for the replay check. Roughly 7 ms per epoch *including* an
independent brute-force reference enumeration, the affordability filter and
all four verification levels every epoch; without the gate the same run is
several times faster. A registered study of 64 replicates × 4 arms × 8,192
epochs would be about 2.1 million epochs, or roughly 4 CPU-hours at this rate
with the gate on — comfortably local, and the gate is a conformance
instrument that a confirmatory run need not carry every epoch. **No AWS.**

## 3. Study-1 rehearsal, executed

Non-confirmatory. Infrastructure observations only; nothing here is evidence
about the mechanism.

| | |
|---|---|
| world | `study-one-v1`, inside the frozen domain |
| registered failure semantics | ON |
| decomposition gate | ON |
| epochs | 3,200 (4 policies × 4 replicates × 200) |
| wall time | 22.5 s per pass, run twice (four-level policy-conditioned gate) |
| replay deterministic | **yes** |
| worst residual anywhere (accounting, conservation, nonnegativity, separability, capacity-source) | **exactly 0** |
| `SEARCH_UNRESOLVED` epochs | **0** |
| `SEARCH_INCOMPLETE_AT_PLAN_CAP` epochs | **0** |
| epochs where the component path matched the policy-conditioned reference at all four levels | 3,020 |
| epochs with nothing to decompose | 180 |
| raw arrivals per arm | 517, identical across arms |

The general (non-Study-1) rehearsal on `sandwater-v1` was re-run unchanged and
is **byte-identical to the previous run**, which is the expected result: that
world has no storage capacities, no sinks and no undecided searches, so
neither the domain freeze nor the registered semantics can move it. It retains
`SEARCH_INCOMPLETE_AT_PLAN_CAP` of 29/99/71/105 by arm and 0
`SEARCH_BUDGET_EXCEEDED` — which is precisely why it is **not** a Study-1
world: its plan-size cap binds.

## 4. Decisions still required before preregistration

Deliberately not taken here. None may be chosen from observed outcomes.

### Stage A — isolated mechanism checks

| # | decision | note |
|---|---|---|
| A1 | the isolated **P disturbance** fixture: which coordinate, what amplitude, how many epochs of recovery | must be inside the frozen domain; amplitude must not be set equal to the action quantum, or the endpoint-saturation theorem's hypothesis is recreated by accident |
| A2 | the isolated **E demand** fixture: destination, quantity, arrival epoch | one order, no physical shortfall, so E and P are cleanly separated |
| A3 | the **E -> P -> restoration cycle** fixture: the order that creates a shortfall, and the recovery that closes it | the closed-cycle theorem already fixes what capacity may be issued; the fixture fixes what is observed |
| A4 | what Stage A **reports** | Stage A is a mechanism demonstration, not a comparison; it must not carry hypotheses |

### Stage B — the registered behavioural comparison

| # | decision | note |
|---|---|---|
| B1 | **stochastic E-arrival law**: quantity, frequency, destination and multiplicity distributions | packet §3.1; must be declared before any trajectory is inspected, and **not** chosen to make enumeration cheap |
| B2 | whether to include a **natural physical disturbance law**, and if so its pair set, amplitude and rate | optional; nested coupling across rates is recommended, as adopted for the homeostasis study |
| B3 | **actor policies** | aligned, random, hostile and the no-EBU comparator are implemented; the arm set is still a decision |
| B4 | **restoring-drift endpoint** | packet §5. Not chosen. The endpoint-saturation theorem's hypothesis fails in this model, which means the aligned arm is not trivially perfect — it does **not** by itself make `O95` unsuitable. Suitability depends on what the study intends to measure |
| B5 | **replicate count and horizon**, with a power argument | no default may be inherited from the stress model merely because it exists |
| B6 | the **findings-forced reporting decisions** | packet §3.3, items 1–7, all still open |

### Domain conditions a Stage-B world must satisfy

Any world used must pass `study_one.require_domain`. In particular its
plan-size cap must be at least its usable route count, and its complete plan
space must fit inside the exhaustive budget. `sandwater-v1` does **not**
qualify, and neither does any lossy or capacity-bearing fixture.

## 5. What this readiness does not say

    STUDY-1 DOMAIN VERIFIED

is **NOT**

    GENERAL DEMAND-DRIVEN FRAMEWORK PROVED FOR ALL LOSS/CAPACITY/TOPOLOGY MODELS.

The three theorems are proved for one resource, lossless routes, no storage
capacities, no sinks, a fixed topology and a non-binding enumeration cap.
Outside that boundary the structural reach is a sound superset rather than an
exact set, and F-5 and F-6 are two demonstrated over-coupling artifacts. The
general loss-aware framework is **open for later extension**, and those two
counterexamples are what any extension has to fix first.

Nor is this evidence about the mechanism. Everything above is infrastructure:
what the model computes, that it computes it exactly, and that the searches it
runs are complete. Whether a demand-driven EBU economy exhibits a restoring
tendency is untouched, and remains the question no registered study has asked.
