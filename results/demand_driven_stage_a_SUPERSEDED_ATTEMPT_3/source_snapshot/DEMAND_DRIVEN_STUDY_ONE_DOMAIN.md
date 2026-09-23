# The frozen Study-1 domain

**Identity** `EBU-DEMAND-DRIVEN-STUDY-1-DOMAIN-v1`
**Implementation** `demand_driven_ebu/study_one.py`
**Conformance** `test_demand_driven_ebu.py`, section *FIRST DEMAND-DRIVEN STUDY DOMAIN FREEZE*
**Status** no registered study has been executed. This document closes
generality questions and states what has been proved; it authorizes nothing.

---

## 1. What Study 1 supports

A world is a Study-1 world exactly when every condition below holds.
`study_one.domain_violations` returns one line per condition that fails, and
`study_one.require_domain` refuses the world.

### Physics

| # | condition | how it is checked |
|---|---|---|
| 1 | one homogeneous scalar resource | `len(world.resources) == 1` |
| 2 | every coordinate a stock with declared reference and scale | `role == STOCK` and `carries_potential` |
| 3 | `x_i >= 0` | `physical.can_happen_now` refuses any plan that would break it; the harness audits the residual to exactly `0` every epoch; `study_one.state_violations` checks a given state |
| 4 | exact conservation `sum_i x_i = M` | implied by 5 and 6; audited to exactly `0` every epoch; `state_violations(..., total=M)` checks a given state |
| 5 | lossless transfers, `eta = 1` | every `route.efficiency == 1` |
| 6 | no loss sinks | no `route.sink` |
| 7 | no irreversible sinks | no `ROLE_SINK` coordinate |
| 8 | no recoverable-waste model | follows from 6 and 7; `DemandWorld` already refuses any route exporting from a sink |
| 9 | no upper destination-storage capacities | every `coordinate.capacity is None` |
| 10 | fixed topology | `DemandWorld` is a frozen dataclass and no model path constructs a second world from a first |
| 11 | finite declared action quantities | `world.quanta` is a finite ascending tuple of positive exact rationals |
| 12 | exact rational/integer arithmetic | `fractions.Fraction` throughout; tolerance literally zero |
| 13 | complete **economic** service only | `plans.ServicePlan.__post_init__` refuses any incomplete economic allocation |
| 13a | **strong atomic physical service**: a plan serves a physical demand exactly when it makes genuine positive progress on **at least one** deficit that exists at the pre-action state, never on every one of them; the remainder is re-derived from the post-state | `service.serves_all` with `CoordinateRequirement.serves_physical`; attribution capped by `physical_progress`; irredundancy served-set relative in `enumeration.is_irredundant`; permanent regressions at `(5,4,3)`, `(2,6,4)`, `(1,4,7)` and `(0,6,6)` |
| 13b | **coexistence protection**: a new economic order may not starve an existing physical need | `admission.starved_ids` via `enumeration.physically_coexistent`; asked only by admission, never by a menu |
| 14 | no partial **economic** service, no backlog quantity, no P queue or residual object, no deadline, no service quality | no such field or symbol exists in the package; asserted by the conformance suite as a symbol check, not a prose check |
| 15 | no topology change during a run | `EconomyRun` holds one `world` for its lifetime |

### Computational

| # | condition | why |
|---|---|---|
| 16 | `max_plan_size >= len(usable_routes(world))` | makes the enumeration cap incapable of deciding anything |
| 17 | `plan_space(world) <= EXHAUSTIVE_BUDGET` | makes `SEARCH_UNRESOLVED` impossible rather than unobserved |

`plan_space(world) = prod_r (1 + n_r) - 1` over usable routes, where `n_r` is
the number of declared quanta that fit route `r`. A plan is a choice per route
of one permitted quantum or of nothing, minus the empty plan.

## 2. What is outside, and what that means

Everything below is **FUTURE UNSUPPORTED PHYSICS**. It is not a defect, not a
gap in Study 1, and not a blocker:

more than one resource; lossy transfer; loss sink; irreversible sink;
recoverable waste; upper destination-storage capacity; topology change during
a run; partial **economic** service; **economic** backlog quantity; deadline;
service quality.

Partial *physical* restoration is **not** on that list: it is supported, and it
is the declared P-demand semantics. Finding F-7 records the exhaustive evidence
that withdrew the earlier complete-service rule for physical restoration, and
`DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` §2.1 states the replacement.

The general loss-aware and capacity-aware framework stays **open for later
extension**. Two coupling artifacts are known to live in it, and they are kept
as permanent regressions rather than forgotten. Neither is repaired here,
because repairing them would be work inside a domain no study is yet declared
in, and because a silent repair would destroy the regression.

## 3. Route liveness

A route `r` is **usable** when some declared quantum fits its capacity, and
**live** at state `x` when in addition `x[source(r)] >= q_min(r)`, the smallest
declared quantum that fits.

### Theorem L1 (necessity, every domain)

*If `r` carries an action in any executable plan `G` at `x`, then `r` is live.*

The action moves a declared quantum `q <= cap(r)`, so `r` is usable.
Source-funding requires `x[source(r)]` to be at least the total that
coordinate sends in `G`, which is at least `q`, which is at least `q_min(r)`.
So `r` is live. **∎**

Consequence: filtering the structural reach on liveness removes no route any
executable plan could use, so the reach stays a **sound superset** of every
minimal plan's support in every domain, including loss-aware and
capacity-aware ones.

### Theorem L2 (sufficiency, Study-1 domain only)

*In a Study-1 world, if `r` is live at `x` then the singleton plan
`{(r, q_min(r))}` is executable.*

Its quantum is declared and fits the route capacity. Source funding holds by
liveness. The destination only gains, so nonnegativity holds there, and the
source ends at `x[source] - q_min >= 0`. Condition 9 means there is no storage
capacity to exceed. Condition 5 means the increment sums to exactly zero, so
conservation closes. Every clause of `can_happen_now` passes. **∎**

### Corollary L3 (action liveness, Study-1 domain only)

*An action `(r, q)` appears in some executable plan at `x` if and only if
`q <= cap(r)` and `x[source(r)] >= q`.*

Necessity is source-funding again. Sufficiency is the singleton `{(r, q)}`,
executable by the same five clauses as L2. This is the rule service
enumeration actually relies on: `_sized_groups` offers every declared quantum
that fits each live route's capacity and lets `can_happen_now` decide funding
per plan, which is exactly L3 applied plan by plan rather than pre-filtered.
Pre-filtering on L3 would be sound but would gain nothing, because a plan's
funding test is over the *total* a source sends, not over one action. **∎**

So in Study 1 the live route set is **exactly** the set of routes that can
act, and the structural reach is exactly the requirement coordinates together
with the sources of the live routes delivering into them — condition 9 makes
the capacity-relief limb of `structural_reach` empty, so the closure is one
pass.

### Where L2 fails, and the counterexamples kept for it

**F-5, destination storage capacity** — `fixtures.capacity_relief_world`.
Two unrelated one-unit deliveries, `A -> C` and `V -> W`. Declaring an upper
storage capacity of ten on `C` when only three units exist in the entire world
changes no executable action and no binding constraint. But a declared
capacity activates the relief limb, so `C -> Z` enters the reach of the demand
at `C`, `Z` follows, and `V -> Z` then drags in `V` and its owner. The two
demands merge: **two components become one**. Tightening this needs a third
liveness limb — destination headroom — which is not attempted.

**F-6, shared loss sink** — `fixtures.shared_sink_world`. Two unrelated
deliveries `A -> C` and `B -> D` over routes that each waste half into the
same audit sink `S`. The sink enters each reach as a delivery target, and then
every route depositing into that sink is pulled in behind it. The demands
merge, and the merged reach claims both owner accounts — though a sink may not
source a route and carries no capacity, so it cannot compete for anything.
Tightening this needs sinks excluded from the reach closure, which is not
attempted.

Both worlds are refused by `require_domain`. Both are permanent regressions in
the conformance suite, asserting the defect *is present* so that any future
repair must update them deliberately.

## 4. No scientific plan-size cap

`world.max_plan_size` is a **computational enumeration limit** and nothing
else (`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`). Condition 16 makes it
non-binding in Study 1: a plan uses each route at most once, and only a usable
route can carry an action, so no plan can have more actions than there are
usable routes.

Serviceability is already decided without the cap. What remains to show is
that the *pruning* the uncapped search uses is equivalent to walking the whole
finite plan space.

### Theorem P (pruning equivalence)

*`physically_serviceable` returns `SERVICEABLE` if and only if some plan in
the complete finite plan space serves the requirement set and is executable
(assuming the budget is not exhausted).*

`(=>)` The pruned space is a subset of the complete space, and the returned
plan is checked directly.

`(<=)` Suppose some complete executable plan exists. Take one minimal under
inclusion; call it `G'`. `G'` is irredundant by minimality. By the soundness
argument in `enumeration`, every action of an irredundant plan either delivers
into a requirement coordinate or drains a capacity-bearing coordinate that
receives inflow inside the plan — and in either case its route is in the
structural reach. Each such route is live by Theorem L1, because `G'`
executes. A plan uses each route at most once by construction. So `G'` lies
inside the pruned space, which enumerates every choice of at most one action
per live reach route, and the search finds it. **∎**

The suite checks this against an independent brute-force enumeration that
never consults `enumeration` at all, over all 91 integer states of the
Study-1 world and four order sizes, plus four further worlds.

A computational cap therefore cannot turn a serviceable demand into an
impossible one anywhere in the model: the capped menu search reports
`SEARCH_INCOMPLETE_AT_PLAN_CAP`, never `PHYSICALLY_IMPOSSIBLE`, and in Study 1
it cannot report even that.

## 5. Search verdicts

Exactly three, and they never collapse into each other:

| verdict | meaning |
|---|---|
| `PHYSICALLY_SERVICEABLE` | a complete valid service plan is proved to exist |
| `PHYSICALLY_IMPOSSIBLE` | exhaustive Study-1 search proves none exists |
| `SEARCH_BUDGET_EXCEEDED` | the computation established neither |

`UNRESOLVED` is never converted into scarcity, incompatibility, admission,
rejection or no-action. `admission.unserviceable_ids` blocks only on
`IMPOSSIBLE`; `admission.unresolved_ids` reports the undecided set separately;
`coupling.service_reach` empties a reach only on a *proved* impossibility and
gives an undecided demand its full reach.

### Reconciling "admission requires proof" with "never convert UNRESOLVED"

These two requirements look opposed, and the resolution is the third option
rather than either of them.

Admission may admit only what is **proved** serviceable. But an undecided
search may not be recorded as a rejection either, because that would convert a
computational limit into a scarcity finding about the physics of the world. So
an undecided search in a registered job is neither admitted nor rejected: it
**stops the job**. That is what §6 means by a computational integrity failure,
and it is the only disposition consistent with both rules.

Inside the frozen domain the case cannot arise (condition 17), so the rule has
no effect on any valid Study-1 run. Outside registered mode — exploratory work
only — the model admits the demand and flags it
`ADMITTED_BUT_UNRESOLVED_PHYSICAL` in the arrival lifecycle, which keeps the
uncertainty visible instead of resolving it either way. That is an exploratory
convenience and carries no scientific standing.

## 6. Registered failure semantics

For a registered Study-1 job, `SEARCH_UNRESOLVED` is a **computational
integrity failure**. The entire job is invalid.

- do **not** continue the trajectory;
- do **not** exclude only that epoch;
- do **not** resample;
- do **not** change the seed.

Correct the implementation and rerun the identical job with identical seeds.

`EconomyRun(registered=True)` enforces this. It refuses to start outside the
frozen domain, and raises `study_one.JobInvalid` — a `Refusal`, so nothing can
absorb it as a result — at the first undecided search, before admission and
again before service. The same run outside registered mode records
`SEARCH_BUDGET_EXCEEDED` as a declared epoch status instead, which is the
correct behaviour for exploratory work.

Readiness requires proving the failure *cannot occur* in the declared domain.
Condition 17 is that proof: the uncapped search evaluates at most one plan per
point of the complete plan space, and returns `UNRESOLVED` only after
exhausting the budget, so a space that fits inside the budget can never
exhaust it. For `study_one_world` the space is 80 against a budget of 200,000.

## 7. Independent progress, plans, outcomes and sampling

Four things were previously run together and are now kept apart by name. An
independent audit found a defect in each conflation.

### 7.1 Two different questions

**All-demands-complete solvability**, `oracle.all_complete_*`: *can every
active demand be completely satisfied in one epoch?* Mathematically useful,
and retained. It is **not** the runtime's execution semantics.

**Independent progress**, `oracle.global_progress`: what the epoch is actually
allowed to do. This is the scientific authority.

The distinction is not pedantic. The runtime deliberately lets an independent
component progress while another is proved impossible, so the first question
answers "no" and returns the empty set in exactly the situations the second
question is most interesting. The component path returned empty there too, and
the two agreed — **vacuously**. At `study_one_world`, state `(0, 6, 6)`:

| | |
|---|---|
| physical demand at `A` | 4 units short; one route in, largest quantum 2 ⇒ **proved impossible** |
| economic order at `C` | 1 unit, independent, **two complete plans** (`B->C` at 1 and at 2) |
| old all-complete comparison | `0 == 0` — PASS, having seen nothing |
| progress reference | `blocked = {P:r|A}`, `resolved = {E:…:r|C}`, **2 plans** |

### 7.2 The progress-plan family

Let the active demand parts be `C_1, ..., C_m` with complete-plan sets `P_k`.

    G_progress = product over k of ( P_k         if P_k is nonempty
                                   ; {BLOCKED_k} if impossibility is proved )

`BLOCKED_k` contributes no physical action and leaves its demands unresolved.
**Every part with a nonempty plan set contributes exactly one plan**: a
serviceable part acts, and there is no voluntary no-action. A blocked part is
not an actor choice — it is a physical fact about the state, and its demand
persists into the next epoch because the deviation that created it is still
there.

`SEARCH_UNRESOLVED` is neither branch. It is a computational integrity failure
and the job cannot proceed (§6).

`oracle.global_progress` computes this without calling `coupling` or `plans`:
it re-derives the partition from the frozen reach definition of §3 with
brute-force serviceability, enumerates each part by brute force, and then
enumerates the non-blocked demand set **with no partition at all** — that last
set is the reference, and the partitioned product is checked against it.

### Theorem D (decomposition equals the progress reference, Study-1 domain)

**Restated for strong atomic P-provenance.** The old statement compared the
partitioned product against *the plan set serving the union of the non-blocked
demands*. Under the current service predicate that object is the wrong one:
physical service is existential, so "serves the union" is satisfied by a plan
that progresses one deficit anywhere and leaves a whole live part untouched,
which is not what an epoch does. The theorem is therefore about **serving each
live part**, and each implication below has been rechecked under the current
definitions rather than re-worded.

> *In a Study-1 world with a non-binding cap, the product over live parts of
> their menus equals the set of plans that are executable, serve **every** live
> part in the sense of §3, and are minimal against that conjunction in the
> served-set-relative sense of §7 — enumerated over the whole world, forming no
> component.*

Write `R_k` for part `k`'s requirement coordinates, `reach_k` for its
structural reach, `served_k(G)` for the demands of part `k` that `G` serves,
and `served(G) = union_k served_k(G)`. Parts are the connected classes of the
reach-interaction graph, so distinct parts have disjoint coordinate, route and
owner sets. A blocked part has an empty reach (§3), so removing blocked parts
does not change the partition of the rest.

**Lemma 0 (subsets of executable plans are executable).** Unchanged, and it is
pure physics. Removing actions only lowers every source's outflow, so source
funding survives; nonnegativity survives because
`x[i] + delta_S[i] >= x[i] - outflow_G[i] >= 0`; per-action quantum and
route-capacity checks are unaffected; condition 9 removes the storage clause;
condition 5 keeps conservation closed. **∎**

**Lemma 1 (delivery, restated for the current minimality rule).** *If `G` is
minimal for part `k` and `a ∈ G`, then `a` delivers into a coordinate of `R_k`.*

This is the step the old proof took from Theorem P, and it has to be re-derived
because minimality changed. By Lemma 0, `G \ {a}` executes, so minimality can
only fail on the served set: `served_k(G \ {a}) ⊉ served_k(G)`, i.e. removing
`a` **drops** some demand `d` at a coordinate `c` that `G` served. A dropped
demand means the increment at `c` fell below its own threshold — below the
additive total if `d` is economic, to zero or less if `d` is physical. So
`delta_{G\{a}}[c] < delta_G[c]`, which happens only if `a` contributes
positively at `c`; condition 6 leaves no loss sink for it to arrive in
instead. So `a` delivers into `c ∈ R_k`, hence its route and its source lie in
`reach_k`. **∎**

`(⊆)` Let `G_k` be a minimal serving plan for each live part and
`G = union_k G_k`. By Lemma 1 every action of `G_k` has route and source in
`reach_k`, and its destination is in `R_k ⊆ reach_k`, so
`support(G_k) ⊆ reach_k`. Reaches are disjoint, so the supports are disjoint:
`delta_G` agrees with `delta_{G_k}` on `reach_k`. Service of part `k` is a
condition on `delta` at `R_k` alone, so `G` serves every live part, and `G`
executes because no two parts share a source.

For minimality, suppose a proper `S ⊂ G` executes, serves every part and has
`served(S) ⊇ served(G)`. Disjoint supports give
`delta_S = delta_{S ∩ G_k}` on `reach_k`, so `S ∩ G_k` serves part `k`, executes
by Lemma 0, and satisfies `served_k(S ∩ G_k) = served_k(S) ⊇ served_k(G_k)`.
Minimality of `G_k` forces `S ∩ G_k = G_k` for every `k`, hence `S = G`. **∎**

`(⊇)` Let `G` be executable, serve every live part, and be minimal against the
conjunction. For `a ∈ G`, Lemma 0 makes `G \ {a}` executable, so minimality
fails either because `G \ {a}` stops serving some part or because it serves
every part with a strictly smaller served set. **Both cases mean a demand `G`
served is lost**, so the argument of Lemma 1 applies verbatim: `a` delivers into
a requirement coordinate `c(a)`, which lies in exactly one part because `R_k`
are disjoint and an action has one destination (condition 6: no sink).

Put `G_k = {a : c(a) ∈ R_k}`; these partition `G`. An action of `G_j` has its
support in `reach_j`, disjoint from `reach_k`, so `delta_{G_k}` agrees with
`delta_G` on `R_k` and `G_k` serves part `k`; it executes by Lemma 0. If some
`S ⊂ G_k` executed, served part `k` and had `served_k(S) ⊇ served_k(G_k)`, then
`S ∪ (G \ G_k)` would execute, serve every part, satisfy
`served(S ∪ (G \ G_k)) ⊇ served(G)`, and be a proper subset of `G` —
contradicting `G`'s minimality. So each `G_k` is minimal, and `G` lies in the
product. **∎**

**Owner receipts agree**, not merely increments. Disjoint supports mean each
part's receipts are computed from the same baseline and the same actions on
either side, and the harness's joint closure gate independently checks that
every receipt is unchanged when parts are combined.

#### Exactly what "decomposition-free" means here, and what it does not

The reference is independent of the two modules the gate exists to check, and
**not** independent of everything:

| module | used by the reference? |
|---|---|
| `coupling` | **no** — `reference_partition` re-derives the partition from the frozen reach definition by brute force |
| `plans` | **no** — `plans_serving_every_part` enumerates over the whole world and implements its own minimality inline |
| `service` (`serves_all`, `served_ids`) | **yes, shared** |
| `enumeration` (`is_irredundant`, `live_routes`) | **yes, shared** — `is_irredundant` by the per-part menus, `live_routes` by both |
| `physical` (`can_happen_now`) | **yes, shared** |

So Theorem D and the epoch-by-epoch decomposition gate establish that
**`coupling` and `plans` reproduce the declared semantics**. They do **not**
establish that the service predicate itself is the right one: a defect in
`service.serves_all` or in `enumeration.is_irredundant` would move both sides
together and the gate would pass. That is what the conformance regressions and
the exhaustive enumerations are for, and it is stated here so the gate is not
read as more than it is.

#### Scope

Theorem D does **not** cover worlds outside the frozen domain: conditions 9 and
6 are each used twice above and condition 5 once, and F-5 and F-6 show the
partition itself can be wrong out there.

### 7.3 Plan identities and the outcome map

A **plan identity** is a canonical physical action set. `PlanGroup` sorts its
actions and refuses a repeated route, so two encodings of one action set are
one identity; `plans.enumerate_service_plans` refuses a menu carrying two
records of one identity.

Two genuinely different action sets are **two plans**, even when they produce
the same post-state, the same aggregate increment and the same owner receipts.

A **modeled outcome** is `Phi(plan)`: the exact physical increment together
with the settled owner receipts.

> **`Phi` is many-to-one.** An earlier version of this document claimed
> Theorem D made `(G_1, ..., G_K) -> G` a bijection *onto outcomes* and drew a
> sampling conclusion from it. **That claim was false and is withdrawn.** The
> bijection is onto **plan identities**; the outcome map is not injective.

`two_supplier_world` is the standing witness: suppliers `A` and `B` each hold
two, destinations `C` and `D` each need one, either supplier can serve either.

| | |
|---|---|
| distinct irredundant plan identities | **4** |
| distinct modeled outcomes | **3** |
| why | `{A->C, B->D}` and `{B->C, A->D}` differ as action sets but agree in increment, post-state and receipts — `C <-> D` is an automorphism |

### 7.4 The corrected sampling statement

**Frozen for Study 1: the random actor policy is uniform over distinct
canonical complete service plan identities.** It is *not* uniform over unique
aggregate outcomes.

The Cartesian-product statement holds over plan identities: a uniform draw
over a product of plan sets is exactly independent uniform draws over its
factors, and per-part draws use distinct RNG ordinals. The outcome law is its
pushforward, **with multiplicity**:

    P(outcome = o) = |{ plans G : Phi(G) = o }| / |all eligible plans|

In `two_supplier_world` that is `1/4, 1/2, 1/4` — never `1/3` each. Duplicate
plan *records* would change nothing, because identities are what is counted.

For `ALIGNED` and `HOSTILE`: first restrict to the plans attaining the
required extremal group EBU, then apply the frozen uniform tie-break over
those distinct plan identities, then derive outcome probabilities from that
plan distribution. In `two_supplier_world` the aligned tie set is the two
cross plans, which share one outcome, so its outcome law is a point mass; the
hostile tie set is the two same-supplier plans, whose outcomes differ, giving
`1/2, 1/2`. Same world, same mechanism, different induced laws — which is why
the tie set has to be computed over plans and not over outcomes.

### 7.5 `G_physical` is pre-affordability

Everything in 7.1 to 7.4 is computed **before any balance is consulted**.
`G_physical(x, D)` answers exactly one question — *which complete
demand-serving plans can physically execute now?* — and is blind to capacity
balances, to actor policy and to aligned/random/hostile preference by
construction: `plans_serving` and `global_progress` are never given a ledger
or a policy.

> **`G_physical` is not the runtime action distribution for an EBU arm.**
> An EBU arm never samples from it. Describing it as the runtime distribution
> was a verification defect: the comparison then checked a law the model does
> not have.

### 7.6 The policy-conditioned execution reference

A second layer takes the physical state, the active demands, **the node
balances and the policy identity**.

    G_affordable = { G in G_physical :
                     projected balance of every required owner stays >= 0 }

Affordability is **per account**, never a pooled total (Capacity V1,
`capacity.CapacityLedger.project`). A plan whose aggregate receipt is
comfortable but which drives one owner negative is refused.

| policy | eligible set | selection |
|---|---|---|
| `ebu_random` | `G_affordable` | uniform over canonical plan identities |
| `ebu_aligned` | `G_affordable` | `argmax E_G` **within** it, then the frozen uniform tie-break over tied identities |
| `ebu_hostile` | `G_affordable` | `argmin E_G` **within** it, same tie-break |
| `control_random_no_ebu` | `G_physical` | uniform; affordability **intentionally bypassed** |

Restricting before taking the extremum is not a detail. A hostile actor's
globally worst plan is frequently the one it cannot pay for, so the two orders
give different answers. In `three_supplier_world` at zero balances the three
plans price at `0`, `+1` and `-1`; the `-1` plan is unaffordable, so hostile
takes `0` — the globally worst plan is genuinely out of reach.

### 7.7 Zero-affordable semantics

If `G_physical` is nonempty but `G_affordable` is empty, the part is
`ALL_PLANS_EBU_UNAFFORDABLE`. No physical action occurs for it and its demand
**remains pending**. This is an intended EBU affordability outcome. It is
**not**:

- voluntary no-action — no policy may decline an eligible plan;
- physical impossibility — `PHYSICALLY_IMPOSSIBLE` is a different status;
- scarcity — that is an admission verdict about a different question;
- computational failure — `SEARCH_UNRESOLVED` invalidates the job instead.

All four are separately declared statuses and the suite asserts they are never
collapsed.

This is the ordinary case, not an edge case. At `study_one_world`, state
`(4, 4, 4)`, zero balances, one unit wanted at `C`: both physical plans exist
(`B->C` at one unit prices `E = -1`, at two units `E = -4`), every EBU arm has
an empty affordable set, no-action probability is exactly one, and the order
stays pending. The comparator executes normally with `1/2, 1/2`.

### 7.8 Mandatory action, conditioned on the eligible set

- for an EBU policy, if `G_affordable` is nonempty, **one nonempty plan must
  execute**;
- for the comparator, if `G_physical` is nonempty, one nonempty plan must
  execute.

There is no voluntary no-op anywhere. Inaction follows only from an empty
eligible set, and which set that is depends on the arm.

### 7.9 Verification levels

Two hierarchies, and the first is not a runtime verification.

**Physical, pre-affordability** (`oracle.progress_levels`): plan-set
equivalence, outcome support, and the random and extremal laws that
`G_physical` *would* induce. Useful for checking the physical layer; blind to
every arm's actual behaviour.

**Policy-conditioned** (`oracle.policy_levels`), which is what the harness
gate runs:

| level | what it compares |
|---|---|
| **A** physical eligibility | the same `G_physical`, and the same blocked split |
| **B** affordable plan set | the same `G_affordable` under these balances, and the same unaffordable/resolved split |
| **C** policy plan distribution | the same selection law over canonical plan identities, for this policy |
| **D** modeled outcome distribution | the same `Phi`-pushforward law, multiplicity preserved |

**Level A alone is not a runtime verification.** Two arms agree on `G_physical`
by construction and can still execute completely different laws —
`three_supplier_world` is a world where EBU-random and the comparator agree at
level A and differ at level C. Likewise **B alone proves neither C nor D**: a
flat law over the correct support is a different distribution from the correct
one, and `two_supplier_world` is a world where they differ.

`EconomyRun(decomposition_gate=True)` runs all four policy levels every epoch,
conditioned on that run's own balances and policy, and refuses on any
disagreement.

## 8. Unusable-infrastructure invariance

*A topology modification that adds and removes no executable atomic action and
changes no genuine binding constraint must leave all five of these unchanged:*
admission; serviceability; the complete plan set; EBU plan values;
affordability inputs.

Checked on both auditor counterexample families — capacity-`1/2` routes and
empty-source routes — with all five outputs compared, and with the executable
action set shown identical first so the premise of the invariance holds.

Inside Study 1 the invariance follows from Theorems L1 and L2: the reach reads
only live routes, liveness is exactly the ability to act, and the menu search
reads only reach routes. Outside Study 1 it does **not** hold: F-5 is a
counterexample to it.

## 9. Status

    STUDY-1 DOMAIN VERIFIED

is **NOT**

    GENERAL DEMAND-DRIVEN FRAMEWORK PROVED FOR ALL LOSS/CAPACITY/TOPOLOGY MODELS.

Everything proved above is proved for one resource, lossless routes, no
storage capacities, no sinks, a fixed topology and a non-binding enumeration
cap. The general loss-aware framework is **open for later extension**, with
`capacity_relief_world` (F-5) and `shared_sink_world` (F-6) already recording
two things any extension must fix.
