# Structural findings from implementing the demand-driven model

**Status: STRUCTURAL CONSEQUENCES OF THE FROZEN CONTRACT, NOT BEHAVIOURAL
EVIDENCE.** Each item below is a property of the declared semantics,
demonstrated exactly on a small declared fixture. None is a finding about how
the demand-driven economy behaves in general, none is generalizable from the
fixture it is shown on, and none may be cited as a result. No registered study
of this model exists.

Nothing here is repaired. Repairing any of them would be a model redesign,
which this task explicitly excludes. They are recorded so the first registered
study is designed with them visible rather than discovered mid-run.

**Revised after the independent audit of commit `22fd229`.** F-1 was partly an
artifact of an over-broad coupling rule and is rewritten below; F-2, F-3 and
F-4 are unchanged in substance. The audit's corrections are described in
`DEMAND_DRIVEN_AUDIT_CORRECTION_HANDOFF.md`.

**F-7 is the one exception to "nothing here is repaired."** It was recorded and
then acted on, because exhaustive enumeration showed the rule it describes was
not a consequence of the physics at all. The finding is kept in full, with the
evidence that produced it, and the superseding decision is stated inside it.
Everything else in this ledger stands unrepaired.

---

## F-1 A stuck obligation freezes only what it genuinely competes with

**Superseded in part by the audit correction pass.** As first written, this
finding said that any unserviceable demand freezes its whole component. That
was true of the code at commit `22fd229`, but it was largely an artifact of a
coupling rule that merged every demand in a transport-connected component. The
rule has been narrowed to actual binding constraints, and the artifact is gone.
What remains is a smaller and genuinely structural restriction, stated below.
The original text is not retained as a current finding because it would
misdescribe the model; the defect and its correction are recorded in
`DEMAND_DRIVEN_AUDIT_CORRECTION_HANDOFF.md`.

**What was an artifact.** In `sandwater-v1` at state `(8, 12, 10, 6, 6)`, the
shortfall `P:sand|A` has five complete executable plans. Add an unserviceable
order for 25 units of sand at `C` and, under the old rule, the coupled
component's menu dropped to zero: the shortfall was frozen by a demand it could
not possibly compete with. Under the corrected rule the order is a singleton
component with no plans, the shortfall keeps all five, and the two are resolved
independently in the same epoch.

**What is genuinely structural.** Demands that *do* share a binding constraint
are still resolved together or not at all, and the complete-service contract
then propagates one demand's impossibility to its partners. The sharpest case
is a shared service-delivery pool. The same 25-unit order placed at `A` — the
coordinate that carries the shortfall — freezes both, because the two claims
draw on one pool and the combined requirement is `max(25, 2) = 25`, which no
plan reaches.

This freeze is **a declared complete-service and allocation restriction, not
unavoidable physical scarcity.** The stock to close the two-unit shortfall
exists and is reachable; what forbids using it is the contract's refusal of
partial service, which requires the 25-unit order to be met in the same plan.
Nothing physical prevents the restoration.

**Why admission does not prevent it.** Admission refuses an arrival that is
unserviceable at the moment of admission, and refuses one that would newly
break an existing obligation. It cannot bind the future: a natural
disturbance, an irreversible loss, or the actor's own previous choice can make
an already-admitted demand unserviceable afterwards.

**What it means for study design.** The stuck-component fraction must be a
declared reported metric, and it must distinguish the two cases above, because
only one of them is about physics. In the rehearsal, 959 of 3,200 epochs had an
unserviceable component sitting beside an executing one — which is the
corrected behaviour working, and under the old rule would have been 959 epochs
of unnecessary freezing.

**Candidate remedies, all out of scope here.** Demand expiry; partial service
with backlog; an admission rule with a serviceability horizon. Each changes the
frozen service contract and needs its own authorization.

## F-2 Irreversible loss makes complete restoration permanently impossible

Every action conserves quantity over all coordinates, so loss does not destroy
quantity — it moves it somewhere it cannot come back from. In a closed world
the represented stock total then falls permanently below the reference total,
and **at least one shortfall can never be closed**. P-demand at that coordinate
is therefore permanent.

This is not a defect in the loss accounting; it is what irreversibility means
in a conserved world. It does interact with the mandatory-action rule in a way
worth stating.

**Exact worked example, on the `loss-v1` fixture only.** After the economic
action of contract section 28 wastes two units, the reachable potential floor
is exactly `3` — verified by enumerating every executable plan. But the floor
state `(9, 9, 10)` still carries two shortfalls of one unit each, and serving
both completely requires two units drawn from the third cell, which lands at
`V = 4`. Under mandatory complete service the system therefore **leaves** the
floor whenever it reaches it:

> the mandatory-action rule plus complete service produces a recurrent level
> strictly above the reachable potential floor.

Driving the fixture for twelve epochs with no disturbance and no arrivals, the
aligned policy sits at `V = 4` throughout, never visiting `3`.

**Illustrative only.** The other policies on the same twelve epochs show
oscillation and, for the no-EBU comparator, escalation followed by a jammed
`NO_COMPLETE_PHYSICAL_PLAN`. These are single deterministic paths on one
four-coordinate fixture with one lossy route. They are not evidence about
hostile safety, comparator behaviour or anything else, and must not be quoted
as such. They are recorded because they show the mechanism is *capable* of
these regimes, which is what a study must be powered to distinguish.

**Design consequence.** The contract's `eta = 1` baseline is doing real work.
A lossy registered study is a different scientific object from a lossless one,
because in the lossy world the reference is unreachable by construction and
"restoring tendency" has to be redefined against the reachable floor rather
than against `x*`. That redefinition does not exist yet and is a prerequisite
for any lossy study.

## F-3 Consumption is financed per owner by prior restoration

At `B_i = 0` a negative-EBU plan is unaffordable, and there is no pooling,
borrowing or transfer. An economic action that moves the system away from its
reference can therefore only ever be taken by an owner that has **already**
earned capacity by moving it toward the reference.

This is Capacity V1 working as declared rather than a surprise, but it has a
consequence the earlier arbitrary-action studies could not exhibit: in the
demand-driven economy, **which** economic demands can be served depends on
*which node* happens to hold capacity, not on aggregate wealth. The conformance
gate shows a plan being refused to a poor owner while an identical plan from a
richer owner is affordable, with the EBU value identical in both cases.

**Design consequence.** The first registered study's arrival law must declare
its destination distribution deliberately, because an arrival law that
concentrates demand on nodes that never earn will report unaffordability that
is an artefact of the destination distribution rather than of the mechanism.
This is recorded as an unresolved load parameter in the decision packet.

## F-4 Admission's serviceability test is one-epoch and state-dependent

The admission rule asks whether the obligations are serviceable **now**, in the
current physical state, in one epoch. It does not ask whether they could be
served eventually, and it cannot, because the frozen contract has no notion of
service across epochs.

Two consequences follow. An arrival that is briefly unserviceable is rejected
outright rather than deferred — there is no deferral in the model. And because
the test reads the physical state, the *number of admitted demands* legitimately
differs between actor policies even though the *arrival sequence* is identical
across them. The rehearsal shows exactly this: 404 identical arrivals under all
four policies, but 152 to 309 admissions depending on the policy. That is not a
stream leak; it is admission responding to the physical state the policy
produced. The stream-separation property that must hold, and does, is that the
arrival sequence itself is untouched.

---

## F-5 A storage capacity that cannot bind still changes coupling

**OUTSIDE THE STUDY-1 DOMAIN. Not repaired. Permanent regression.**

`fixtures.capacity_relief_world`, reproduced by pure calculation on a fixed
state. Two unrelated one-unit deliveries, `A -> C` and `V -> W`, with three
units of resource in the entire world. Declaring an upper storage capacity of
ten on `C` changes no executable action and no genuine binding constraint —
the capacity cannot be reached by any trajectory. But a declared capacity
activates the capacity-relief limb of `structural_reach`, which conservatively
assumes a route out of a capacity-bearing requirement coordinate might be
needed to make room. So `C -> Z` enters the reach of the demand at `C`, `Z`
follows it, and `V -> Z` then drags in `V` and its owner account. **Two
independent components become one.**

This is a genuine violation of unusable-infrastructure invariance, and it is a
*tightness* failure rather than a soundness failure: the reach remains a
superset of every minimal plan's support, it is simply larger than it needs to
be. Tightening it would require a third liveness limb — destination headroom —
which is not attempted, because Study 1 declares no storage capacities and
`study_one.require_domain` refuses this world. The regression asserts the
defect *is present*, so any future repair has to update it deliberately.

## F-6 Two lossy routes couple through a shared sink

**OUTSIDE THE STUDY-1 DOMAIN. Not repaired. Permanent regression.**

`fixtures.shared_sink_world`. Two unrelated deliveries `A -> C` and `B -> D`,
each over a route wasting half of what it carries into the same audit sink
`S`. The sink is a delivery target of both routes, so it enters each demand's
reach; the closure then pulls in every route depositing into that sink, and
the demand at `C` acquires `B`, `D` and owner `B`. The two merge, and the
merged reach claims both owner accounts — so their affordability is settled
jointly and their service becomes all-or-nothing together.

The coupling is spurious on the model's own terms. A sink is irreversible, may
not be the source of any route, and carries no capacity, so it can never
compete for anything. Tightening this would require excluding sinks from the
reach closure. Not attempted, same reason as F-5: Study 1 is lossless.

---

## F-7 Complete-service P-demand made 36 of 91 Study-1 states absorbing

**SUPERSEDED FOR STUDY-1 PHYSICAL RESTORATION. The rule was withdrawn and
replaced; the evidence below is retained in full and is not deleted.**

### The old semantics, enumerated exactly

`study_one_world` — three stocks in a line `A <-> B <-> C`, one resource,
references `x* = (4,4,4)`, conserved total `M = 12`, declared quanta `{1, 2}`,
one action per route per plan. **91 integer states.** Edges are the successor
states of the decomposition-free progress reference, evaluated at every state.
No policy ran, no trajectory was generated, and no arrival law was sampled.

Under the withdrawn rule — *a plan serves a physical demand only if it closes
the whole deficit in one step* — the exhaustive result was:

| quantity | count |
|---|---|
| physical states | **91** |
| equilibrium | **`(4,4,4)`** |
| absorbing states (empty menu) | **37** |
| — of which the equilibrium itself | **1** |
| — **absorbing away from equilibrium** | **36** |
| states from which `x*` is reachable at all | **31 / 91** |
| states from which `x*` is reachable by burden-nonincreasing paths | **31 / 91** |
| states from which `x*` is reachable by strict descent alone | **23 / 91** |
| distinct successor edges | **99** (80 descending, 13 neutral, 6 ascending) |

### None of the 36 was resource scarcity

`sum_i x_i = 12 = sum_i x*_i` at **every** state, so the material needed to
reach the reference always existed somewhere in the world. The two causes were:

| cause | count |
|---|---|
| a deficit larger than any single plan could deliver into that coordinate — `A` and `C` have one inbound route each and the largest declared quantum is 2, so a shortfall of 3 or more there was `PHYSICALLY_IMPOSSIBLE` | **28** |
| **joint complete-service conflict** — each deficit serviceable alone, the pair not: `(2,2,8)`, `(2,3,7)`, `(3,1,8)`, `(3,2,7)`, `(7,2,3)`, `(7,3,2)`, `(8,1,3)`, `(8,2,2)` | **8** |
| genuine physical scarcity or topology | **0** |

Canonical witness `(0,6,6)`: the shortfall at `A` is four units, the only route
into `A` carries at most two, and the menu was empty for ever. Sharpest witness
`(2,2,8)`: `A` can be served alone and `B` can be served alone, but `A` would
have to both receive two units and fund `B`'s two from a stock of two.

### Why it was a semantic error and not a physical one

Three independent reasons, each sufficient:

1. **The ontology does not ask for it.** Contract §2.1 declares P-demand
   state-derived: the shortfall persists exactly as long as the deficit does,
   and `derive_physical_demands` reads it off the state with no cache and no
   queue. The residual of a partial restoration is therefore already recorded —
   *in the state* — so nothing is lost by restoring incrementally and nothing
   needs storing.
2. **It was not refinement-consistent.** At `(2,6,4)` the plan `{B->A@2}` was
   legal and its physically valid half `{B->A@1}` was not. Splitting a legal
   restoration into legal sub-restorations destroyed its demand provenance,
   which contradicts the project's own atomic-action principle.
3. **It was the economic contract applied to a physical condition.** An
   economic order has an identity and a lifecycle, so partial fulfilment would
   need a backlog quantity against that id. A physical deficit has neither.
   `service.CoordinateRequirement.required_delta` collapsed both into
   `max(economic_total, physical_deficit)`; that collapse is what carried the
   economic contract across, and it is now removed.

This is the same family as F-1 — *a declared complete-service and allocation
restriction, not unavoidable physical scarcity* — but for P-demand alone, and
far more severe than F-1's statement suggested.

### What replaced it

    E-demand    complete service only, additive across separate orders,
                no partial service and no backlog quantity. UNCHANGED.

    P-demand    served by genuine positive progress on **at least one**
                pre-state deficit; re-derived from the post-state; attribution
                capped at the pre-action deficit; overshoot permitted and
                represented in the state; irredundancy retained in
                served-set-relative form, so no unrelated transfer becomes
                legal.

### The second correction: at least one, not every one

The first implementation of the atomic rule required progress on **every**
P-demand of a coupled component. An independent audit found that this still
breaks sequential refinement, and it is right. At `(1,4,7)` the plan `B->A@2`
is legal and worth `+2`. Split into `B->A@1` twice: the first half is worth
`+2` and **creates a new deficit at `B`**; the "every one" rule then refuses
the second half for not progressing the deficit the first half had just made.
A restoration legal whole and illegal in halves is not atomic.

So provenance is existential: **at least one** pre-state P-demand progressed.

What this buys is **conditional** restorative refinement, and the finding is
recorded at that strength and no higher. Of the **152** legal two-unit
singleton restorations in the frozen world, **120** have both one-unit halves
legitimate; in the other **32** the first half clears the destination deficit
outright, so the second half has nothing left to progress and is correctly
refused. There are **zero** failures of the conditional statement — *the second
half stays legitimate for as long as a deficit remains at the destination*.
Unrestricted subdivision invariance is **not** claimed, and no persistent
demand, historical entitlement or overshoot exception was introduced to obtain
it; whether it is wanted is an unresolved modeling decision.
Coupling survives for genuine physical conflict, competing stock and joint
executability; it no longer carries a contract that one plan must progress
every P-demand it touches. Two consequences were followed through rather than
absorbed:

* **irredundancy became served-set relative.** A proper subset makes a plan
  redundant only when it executes *and* answers everything the plan answers. A
  plain "does some subset serve?" test would collapse every joint plan — an
  economic order and a physical restoration answered in one epoch would reduce
  to the economic action alone, making one class wait for the other.
* **contract §6 protection moved to a coexistence question.** Serviceability
  can no longer see that a new order would starve an existing need, because a
  plan serving the order need not progress the need. `admission.starved_ids`
  asks instead whether *some* plan completely serves the new orders and
  progresses every existing need. It is the only place the conjunction is
  asked.

**Over-coupling now fails in the opposite direction.** Merging two independent
needs used to make service harder — complete service of the union, all or
nothing. It now makes it *easier*: "serve the component" is satisfied by
progressing either one, so a merged menu gains plans that leave one need
entirely unserved. On `sandwater-v1` at `(8,12,10,4,8)` the correctly
decomposed form offers 18 outcomes and the over-coupled one offers 27, the 9
extra being exactly those with zero increment at one of the two requirement
coordinates. The runtime authority is unaffected: `global_progress` and
`component_progress` agree exactly, checked every epoch.

Re-enumerated against the implemented semantics, on the same 91 states:

| quantity | withdrawn rule | implemented rule |
|---|---|---|
| menu plans offered | 99 | **420** |
| distinct successor edges | 99 | **408** (327 down, 33 neutral, 48 up) |
| absorbing states | 37 (36 non-equilibrium) | **1 — `x*` alone** |
| `x*` reachable at all | 31 / 91 | **91 / 91** |
| `x*` reachable by burden-nonincreasing paths | 31 / 91 | **91 / 91** |
| `x*` reachable by strict descent alone | 23 / 91 | **89 / 91** |
| longest burden-nonincreasing distance to `x*` | — | **5 steps** |
| plateau-locked states | 4 | **2** — `(3,4,5)` and `(5,4,3)` |
| plateau components with no lower exit | 36 | **0** |

**This is a physical / demand-menu accessibility result.** It does not say that
every state is EBU-affordably recoverable, that any policy reaches equilibrium,
or that recovery probability is 1. Those are Stage-A questions.

### Where the evidence lives

The withdrawn rule is no longer implemented anywhere, so its enumeration is
reproduced from first principles in `dynamic_ebu_theory_checks.py`
(`section_study_one`, checks `S1-01` to `S1-25`), which also verifies that the
package's successor map now equals the atomic enumeration on all 91 states. The
derivation is in `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md` §10–§12. Permanent
regressions live in `test_demand_driven_ebu.py`: `(5,4,3)` for locality of
provenance, `(2,6,4)` for refinement consistency, `(0,6,6)` for incremental
restoration, and the 91-state accessibility oracle.

---

## What would change these

F-5 and F-6 are consequences of the structural reach being a sound *superset*
rather than an exact set outside the frozen Study-1 domain. Both would be
changed by extending the liveness rule — destination headroom for F-5, sink
exclusion for F-6 — and both are the price of not doing that work inside a
domain no study is declared in. Inside Study 1 the reach is exact: route
liveness is necessary and sufficient there, and the relief limb is empty.
See `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` sections 3 and 8.

F-1 and F-4 are consequences of complete-service semantics — F-1 now in its
narrowed form, after the coupling artifact was removed, and both now scoped to
**economic** complete service, which is the only place that contract survives
(F-7). F-2 is a consequence of
conservation plus irreversibility. F-3 is a consequence of Capacity V1's
no-pooling rule. Each would be altered only by changing the corresponding
frozen rule, which is a redesign and is not authorized here.

A fifth item that is *not* a finding but is worth recording beside them:
economic quantities are additive across separate orders, so several
individually serviceable requests at one destination can be jointly
unserviceable. In the rehearsal this raised scarcity rejections sharply
relative to the defective build, which is the corrected semantics working
rather than a change in the world.
