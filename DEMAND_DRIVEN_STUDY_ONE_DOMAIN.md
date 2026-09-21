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
| 13 | complete demand service only | `plans.ServicePlan.__post_init__` refuses any incomplete allocation |
| 14 | no partial service, no backlog quantity, no deadline, no service quality | no such field or symbol exists in the package; asserted by the conformance suite |
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
a run; partial service; backlog quantity; deadline; service quality.

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

## 7. The global exact plan set is the authority

Define `F_global(x, D)` as the set of canonical outcomes of every executable,
completely-serving, irredundant plan for the whole active demand set `D` at
state `x`, enumerated over the whole world at once with no component ever
formed. Each outcome is a pair: the exact physical increment, and the settled
owner receipts.

`F_global` is the scientific authority. Demand-component decomposition is a
computational optimization and **does not define feasibility**.

### Theorem D (decomposition equals global, Study-1 domain)

*In a Study-1 world with a non-binding cap,
`combine(F_components) == F_global`.*

Write `K` for the components, `R_k` for component `k`'s requirement
coordinates, and `reach_k` for its structural reach. Components are the
connected classes of the reach-interaction graph, so distinct components have
disjoint coordinate sets, disjoint route sets and disjoint owner sets.

*Subsets of executable plans are executable.* Removing actions only lowers
every source's outflow, so source funding survives; nonnegativity survives
because `x[i] + delta_S[i] >= x[i] - outflow_G[i] >= 0`; per-action quantum
and route-capacity checks are unaffected; condition 9 removes the storage
clause; condition 5 keeps conservation closed.

`(⊆)` Let `G_k` be an irredundant complete plan for each component and
`G = union_k G_k`. By Theorem P's soundness step and condition 9, every action
of `G_k` delivers into a coordinate of `R_k`, so its route lies in `reach_k`
and its source in `reach_k`. Reaches are disjoint, so the `G_k` use disjoint
routes and disjoint source coordinates: the increments have disjoint supports,
source funding does not interact, and `G` is executable and serves everything.
If some proper `S ⊂ G` served everything and executed, then `S ∩ G_k` would
serve component `k` (disjoint supports) and would execute (subset), so
irredundancy of each `G_k` forces `S = G`. Hence `G ∈ F_global`.

`(⊇)` Let `G ∈ F_global`. For `a ∈ G`, irredundancy means `G \ {a}` fails to
serve or fails to execute; the second is impossible because subsets execute,
so `a` delivers into some requirement coordinate `c(a)`, which belongs to
exactly one component. Put `G_k = {a : c(a) ∈ R_k}`. An action of `G_j` has
its source in `reach_j`, which is disjoint from `reach_k`, so no action
outside `G_k` touches component `k`'s coordinates: `delta_{G_k}` agrees with
`delta_G` on `R_k` and `G_k` serves component `k` completely. `G_k` executes
as a subset. If some `S ⊂ G_k` served component `k` and executed, then
`S ∪ (G \ G_k)` would serve everything and execute, contradicting `G`'s
irredundancy. So each `G_k` is in component `k`'s menu and `G` is their union.
**∎**

Two consequences worth stating, because passing fixtures would not establish
them:

- **Owner receipts agree**, not merely increments. Disjoint supports mean each
  component's receipts are computed from the same baseline and the same
  actions on either side; the harness's joint closure gate additionally checks
  every receipt is unchanged when components are combined, and refuses
  otherwise.
- **Sampling agrees.** A uniform draw over a Cartesian product is exactly
  independent uniform draws over its factors, and Theorem D makes the map
  `(G_1, ..., G_K) -> G` a bijection onto `F_global`. Per-component draws use
  distinct RNG ordinals, so they are independent.

What Theorem D does **not** cover: worlds outside the frozen domain. Condition
9 is used twice (subsets execute; the relief limb is empty) and condition 5
once. Outside the domain the equality is unproved, and F-5 and F-6 show the
component structure itself can be wrong there.

`EconomyRun(decomposition_gate=True)` checks the equality epoch by epoch
against `oracle.agree`, which enumerates both sides at a common action bound.
A disagreement raises rather than being recorded.

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
