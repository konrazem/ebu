# Demand-driven EBU — Stage-A preregistration (FROZEN)

**Identity** `EBU-DEMAND-DRIVEN-STAGE-A-v1`
**Domain** `EBU-DEMAND-DRIVEN-STUDY-1-DOMAIN-v1`, world `study-one-v1`
**Model** `EBU-DEMAND-DRIVEN-ECONOMY-v1`
**Status** **FROZEN. NOT EXECUTED.** No Stage-A trajectory has been generated.
No epoch of any episode below has been run, and nothing in this document was
chosen from an observed outcome.

Stage A is a set of **isolated mechanism demonstrations**. It carries no
hypothesis, makes no comparison between arms a success or a failure, and
produces no evidence about whether a demand-driven EBU economy exhibits a
restoring tendency. That question belongs to Stage B and is untouched here.

---

## 0. What changed since the last readiness note, and why this can be frozen now

Stage A was previously blocked by a structural fact rather than a missing
decision: under the withdrawn complete-service P-demand rule, `x* = (4,4,4)`
was reachable from only **31 of the 91** Study-1 states, and **36** states were
absorbing away from equilibrium — none of them for want of resource. A
"P-disturbance recovery" episode was therefore not well posed across the
natural amplitude range: an amplitude of 3 or more at `A` or `C` could never
recover, whatever any actor did.

That rule was withdrawn and replaced with atomic physical service
(`DEMAND_DRIVEN_MODEL_FINDINGS.md` F-7; contract §2.1 and §3). Under the
implemented rule, on the same exhaustive 91-state enumeration:

| | withdrawn rule | implemented rule |
|---|---|---|
| absorbing physical states | 37 (36 away from equilibrium) | **1 — `x*` alone** |
| `x*` reachable at all | 31 / 91 | **91 / 91** |
| `x*` reachable by burden-nonincreasing paths | 31 / 91 | **91 / 91** |
| longest burden-nonincreasing distance to `x*` | — | **5 steps** |
| states needing a plateau step first | 4 | **2** — `(3,4,5)`, `(5,4,3)` |

> **This is a PHYSICAL / DEMAND-MENU accessibility result and nothing more.** It
> does **not** say that every state is EBU-affordably recoverable, that any
> policy reaches equilibrium, or that recovery probability is 1. Stage A exists
> precisely because those are separate questions. The three are kept apart
> throughout:
>
> | | question | status |
> |---|---|---|
> | **L** | where aggregate reserve is maximal | PROVED (`EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md` §3–§4) |
> | **R** | whether the allowed actions provide a path there | SETTLED by exhaustive enumeration (§10–§12 there; F-7 here) |
> | **P** | whether actor policies take such paths | **OPEN — this is what Stage A and Stage B observe** |

---

## 1. The frozen environment

`fixtures.study_one_world()`, accepted by `study_one.require_domain`:

- three stocks in a line, `A <-> B <-> C`; one homogeneous resource `r`;
- references `x* = (4, 4, 4)`, scales `sigma = (1, 1, 1)`, conserved total `M = 12`;
- four routes `A->B`, `B->A`, `B->C`, `C->B`, each of capacity 6;
- declared action quanta `{1, 2}`; one action per route per plan;
- plan-size cap 4 (equal to the usable route count, so it cannot bind);
- complete plan space 80, far inside the exhaustive budget, so
  `SEARCH_UNRESOLVED` is impossible rather than unobserved;
- 91 reachable integer states; `A` and `C` are **not** adjacent.

Every run is started with `registered=True` and `decomposition_gate=True`.
Arithmetic is exact `Fraction`; every tolerance is literally zero.

**Opening capacity is zero for every owner.** No episode below grants,
borrows, pools or invents capacity. Where an episode needs reserve, it is
earned inside the episode by a physically justified prelude declared in
advance (A3).

---

## 2. Episode class A1 — pure P-disturbance recovery

### Declared fixture

| item | value |
|---|---|
| initial physical state | `x_0 = (1, 7, 4)` |
| how `x_0` is obtained | one declared **conservative** displacement of **3 units from `A` to `B`**, applied to the reference `x* = (4,4,4)` |
| opening balances | `B_i(0) = 0` for `A`, `B`, `C` |
| disturbance process | `fixtures.quiet_disturbance(world)` — a declared `DisturbanceProcess` with firing probability `0`. Nature does nothing during the episode |
| arrival process | `fixtures.no_arrivals()` — no economic demand at any epoch |
| horizon `T` | **32 epochs** |

`V(x_0) = 9` exactly; the represented deficit is `3` units at `A`.

### Why amplitude 3, declared before any run

Two structural reasons, neither derived from an outcome:

1. **It is not a declared action quantum.** The quanta are `{1, 2}`. An
   amplitude equal to an action quantum recreates the endpoint-saturation
   theorem's hypothesis by accident, which the readiness note has required
   avoiding since before this pass.
2. **It is exactly the amplitude class the withdrawn rule could not serve.**
   A three-unit shortfall at `A` or `C` was permanently unserviceable under
   complete service and is served incrementally now. Choosing it makes the
   episode demonstrate the mechanism the correction introduced, rather than
   avoiding the region where the correction matters.

The displacement direction `A -> B` (rather than `A -> C`) is chosen because
`A` and `C` are not adjacent, so a displacement into `C` would place the
surplus two routes away from the deficit and confound "does the actor restore"
with "can the surplus reach the deficit at all". `B` is adjacent to `A`.

### Structural quantities, declared as design arithmetic

These are properties of the state graph, computed by exhaustive enumeration
before any trajectory exists. They are **not** predictions about any arm.

- the burden-nonincreasing geodesic distance from `x_0` to `x*` is **2**;
- the menu at `x_0` holds exactly two plans, `B->A@1` and `B->A@2`, with exact
  EBU `5` and `8`. Both are credited wholly to owner `B` **at this state**,
  because the deficit is at `A` and `B->A` is the only route into it; that is a
  fact about `x_0`, not about the episode (§4);
- both are affordable from zero balances, so **A1 cannot stall on
  affordability at its first epoch**;
- the horizon `T = 32` exceeds six times the graph's burden-nonincreasing
  diameter to `x*` (which is 5). It is a containment bound, not an expectation.

### Epoch convention, frozen

One convention, used everywhere in this document and nowhere contradicted:

```
epoch t :  observe the pre-state x_t
           derive P-demand, admit, enumerate, choose, execute
           produce the post-state x_{t+1}
```

`T` is the **number of transitions**, never a maximum index. An episode of
`T = 32` executes at most 32 epochs, indexed `t = 0 .. 31`, and produces at
most the post-states `x_1 .. x_32`.

**Return time** is the first post-state index that equals the reference:

```
return_time = min { t + 1 : x_{t+1} = x* }     (undefined if no such t)
```

The episode **stops immediately after recording that transition**. No further
actor epoch is executed. In particular Stage A does **not** run an extra epoch
merely to observe `NO_ACTIVE_DEMAND`: that status is a fact about `x*`, it is
derived rather than executed, and the record carries
`terminal_no_active_demand = true` computed from the post-state with no
physical action taken.

### Stop conditions

The episode stops at the **first** transition at which any of these holds, and
the stopping reason is recorded:

| # | condition | recorded as |
|---|---|---|
| S1 | `x_{t+1} == x*` | `RETURNED_TO_REFERENCE` |
| S2 | the epoch's status is `ALL_PLANS_EBU_UNAFFORDABLE` | `NO_AFFORDABLE_SOLUTION` |
| S3 | `t + 1 == T` | `HORIZON_REACHED` |

S2 and S3 are legitimate recorded outcomes, not failures.

**Precedence, frozen, because the conditions are not mutually exclusive.** The
table is evaluated **in order, S1 then S2 then S3**, after each transition is
recorded, and the **first** condition that holds supplies the single
`stopping_reason`. The order is declared here and is applied identically at
every transition, including the last permitted one.

The tie that matters is on the final permitted transition, `t + 1 == T`. If the
arm returns to `x*` exactly there, S1 and S3 both hold; S1 wins and the episode
records `RETURNED_TO_REFERENCE` with `return_time = T`. If the epoch instead
reports `ALL_PLANS_EBU_UNAFFORDABLE` there, S2 and S3 both hold; S2 wins and
the episode records `NO_AFFORDABLE_SOLUTION`. **`HORIZON_REACHED` is recorded
only when the horizon is the first condition to hold** — that is, when the arm
neither returned nor stalled on affordability at any transition up to and
including `T`.

A return is therefore never reclassified as a horizon outcome merely because it
happened at the last permitted moment.

### `NO_COMPLETE_PHYSICAL_PLAN` is NOT a normal A1 terminal condition

Exhaustive enumeration establishes that **`x*` is the only absorbing state of
the implemented Study-1 graph**: at every one of the other 90 states some
component has a plan. A non-equilibrium `NO_COMPLETE_PHYSICAL_PLAN` would
therefore contradict the declared physical model, and it is **not listed as a
successful terminal condition**. If one ever occurs it can only have come from
search or enumeration semantics — which are already job-integrity failures
(§8) — and the job is invalid rather than reported.

**Scope of that claim, stated exactly.** The enumeration was run over the
**P-only** graph: 91 states, physical demand alone, no economic demand at any
state. A1 is a P-only episode by construction — its arrival process is
`no_arrivals()` — so the claim applies to A1 in full. It does **not** extend to
A2 or A3, where an admitted economic order is present: an economic claim can
become unserviceable after admission (finding F-4), and a legitimately blocked
economic component reporting `NO_COMPLETE_PHYSICAL_PLAN` is an ordinary
recorded outcome there, not an integrity failure.

`x = x*` gives `NO_ACTIVE_DEMAND`, and that is the only inaction Stage A
expects to see on the physical side.

## 3. Episode class A2 — isolated economic demand

### Declared fixture

| item | value |
|---|---|
| initial physical state | `x_0 = x* = (4, 4, 4)` |
| opening balances | `B_i(0) = 0` |
| disturbance process | `quiet_disturbance` |
| arrival process | `ArrivalProcess.declare((("r", "C", 1),), 1, 1, 1)` — one slot, probability 1, alphabet of one kind |
| horizon `T` | **1 epoch** |
| admission | the frozen EBU-blind random admission, unchanged |

A2 is a **single-epoch** episode, so exactly one order ever arrives and the
declared stochastic arrival process is used unmodified.

### Structural quantities, declared as design arithmetic

At `x*` there is no physical demand, so the order stands alone. Its component
menu is exactly two plans:

| plan | post-state | exact EBU | receipt | affordable at zero balances |
|---|---|---|---|---|
| `B->C@1` | `(4, 3, 5)` | `-1` | `B: -1` | **no** |
| `B->C@2` | `(4, 2, 6)` | `-4` | `B: -4` | **no** |

So the declared, expected-by-construction mechanical outcome is
`ALL_PLANS_EBU_UNAFFORDABLE`, with the order recorded as
`E_ADMITTED_BUT_EBU_UNAFFORDABLE` and **not erased**.

> **This is the point of A2, and no capacity is invented to avoid it.** From a
> zero-reserve equilibrium, every way of serving an economic request moves the
> system away from its reference and therefore costs EBU that nobody has yet
> earned. A2 demonstrates that the gate is real, that an unaffordable demand is
> distinguished from an impossible one and from an absent one, and that the
> physical state is untouched when nothing is affordable.

A2 is identical across all four arms except that `control_random_no_ebu`
applies no affordability filter and will therefore execute one of the two
plans. That divergence is the mechanism demonstration, not a comparison.

---

## 4. Episode class A3 — the `E -> P -> restoration` chain

### Declared fixture

| item | value |
|---|---|
| initial physical state | `x_0 = (1, 7, 4)` — the **same** declared displacement as A1 |
| opening balances | `B_i(0) = 0` |
| disturbance process | `quiet_disturbance` |
| arrival schedule | `fixtures.ScriptedArrivals({3: (("r", "C", 1),)})` — exactly one order, of one unit at `C`, at **epoch 3**, and none at any other epoch |
| horizon `T` | **32 epochs** |

### The prelude, declared before any outcome is seen

A3 needs earned reserve, and none is granted. The reserve is earned by the
**declared external displacement plus whatever restoration the arm actually
performs** during epochs 0, 1 and 2. The prelude is therefore physically
justified in exactly the sense the design requires: the capacity that pays for
the economic event is capacity created by restoring a deviation nature made.

The prelude length of **three epochs** is fixed from structure, not from
behaviour: the burden-nonincreasing geodesic from `x_0` to `x*` is 2, and the
prelude is that bound plus one epoch of margin.

> **An arm that has not restored by epoch 3 is a recorded outcome, not a
> failure of the fixture.** Whether each arm holds reserve when the order
> arrives is part of what A3 observes. No arm is given capacity to make its
> episode "work".

### Structural quantities, declared as design arithmetic

**Aggregate, retained as an identity, with its assumptions named.** While
nature is quiet and no external event occurs,

```
B_total(t) - B_total(0)  =  V(x_0) - V(x_t)      for every t
```

so an arm that has reached `x*` has created exactly `V(x_0) - V(x*) = 9` units
of aggregate capacity. That is an identity conditional on (i) a quiet
disturbance process, (ii) no admitted economic service before epoch 3, and
(iii) `B_total(0) = 0`. It is **not** a prediction that any arm has reached
`x*` by epoch 3.

**Per-owner allocation: WITHDRAWN as a universal claim.** The first freeze said
all 9 units belong to owner `B`. False in general: while the deficit sits at
`A` only `B` can source into it, but an arm that carries the system past the
reference creates a deficit at `B`, and then `A->B` and `C->B` are legitimate
and owners `A` and `C` earn. All three owners appear in receipts among the
states reachable inside the three prelude epochs.

**Everything about the arrival epoch is likewise path-conditional.** The
figures `-1` and `-4`, and the post-states `(4,3,5)` and `(4,2,6)`, are
**equilibrium-conditional examples only**: they hold if and only if the arm
happens to stand at `x* = (4,4,4)` when the order arrives. They are retained
below as an illustration and must not be read as A3's declared menu.

#### An analytical witness that the arrival baseline need not be `x*`

Constructed by isolated pure-function evaluation on declared synthetic states.
**No prelude was executed**, and this is not a prediction about any arm; it is
a demonstration that the preregistration may not assume `x*`.

```
(1,7,4) --B->A@1--> (2,6,4) --B->A@1--> (3,5,4) --B->A@2--> (5,3,4)
   V=9      EBU +5      V=4     EBU +3     V=1     EBU  0      V=1
```

Each step is a legitimate single-action menu plan at its own baseline, and
every receipt goes to `B`, so the pre-arrival account vector on this path is

```
(B_A, B_B, B_C) = (0, 8, 0)      B_total = 8 = V(x_0) - V(x_3) = 9 - 1
```

At that baseline `(5,3,4)` there is a **pre-existing** one-unit deficit at `B`,
`V = 1`, and the one-unit order at `C` is admitted — it is neither starved nor
unserviceable. Its component is `{E@C, P:r|B}`, and the menu holds **four**
plans:

| plan | post-state | aggregate EBU | owner receipts | serves | deficit worsened |
|---|---|---|---|---|---|
| `B->C@1` | `(5,2,5)` | `-2` | `B: -2` | the order only | `B` (pre-existing, deepened) |
| `B->C@2` | `(5,1,6)` | `-6` | `B: -6` | the order only | `B` (pre-existing, deepened) |
| `{A->B@2, B->C@1}` | `(3,4,5)` | `0` | `A: +1`, `B: -1` | order **and** `P:r\|B` | `A` (newly created) |
| `{A->B@2, B->C@2, C->B@1}` | `(3,4,5)` | `0` | `A: +1`, `B: -2`, `C: +1` | order **and** `P:r\|B` | `A` (newly created) |

With `(0, 8, 0)` all four are affordable, and affordability is decided **per
owner**, not against `B_total`. The last two share an increment and a
post-state and are nonetheless two plan identities — the many-to-one outcome
map the oracle documents.

> Note what this shows about A3's own question. On this baseline the order can
> be served in a way that **also restores** the standing physical need, or in a
> way that **deepens** it. Both are legitimate. Which happens is the
> policy-dynamics question Stage A exists to observe, and the preregistration
> takes no position on it.

#### What A3 therefore declares

1. **Record the actual pre-arrival physical state `x_3` and the complete
   owner-balance vector `(B_A(3), B_B(3), B_C(3))`.** Both are recorded, never
   predicted.
2. **Derive everything from that recorded baseline**: admission outcome,
   component structure, the exact menu, exact aggregate EBU and exact per-owner
   receipts for every candidate, and affordability **per owner** for each
   complete candidate plan.
3. **Distinguish pre-existing deficits from those newly created or worsened by
   the selected transition.** The report records, for the executed plan, the
   pre-state deficit vector, the post-state deficit vector, and which
   coordinates moved in which direction. At `(5,3,4)` the `B` deficit is
   pre-existing and the `A` deficit in the last two rows is newly created.
4. **Report the three non-chain cases as themselves, not as a failed chain.**

| case | recorded as | what is reported |
|---|---|---|
| the order is refused at admission | `ORDER_REJECTED` | the rejection reason (`E_REJECTED_PHYSICAL_SCARCITY` or `E_REJECTED_INCOMPATIBLE`), the baseline that produced it, and the physical state, which is unchanged by a rejection |
| the order is admitted and no candidate is affordable | `ORDER_PENDING_UNAFFORDABLE` | the menu, the exact per-owner shortfall against each candidate, and that the order is **not** erased |
| the order is served and no physical deficit follows, or none is restored within the horizon | `SERVED_WITHOUT_RESTORATION` | the post-service deficit vector — possibly empty — and the burden path to the horizon |
| the order is served and the induced deficit returns to zero | `RESTORATION_COMPLETED` | the epoch at which it closed and the receipts along the way |

**None of these is a failure of the fixture**, and the prelude, the policies,
the timing and the opening balances are **not** adjusted to make any of them
more likely. In particular nothing is changed to force equilibrium before the
order arrives.

### A3 stop conditions, declared separately from A1's

**A3 does not inherit A1's stop conditions, and in particular not S1.** A1 stops
the moment it reaches `x*`, because returning is the whole of A1's question. A3
asks what happens when an economic order arrives at **epoch 3**, so an episode
that stopped on reaching `x*` during the prelude would terminate before the
order ever arrived, and the class would observe nothing it exists to observe.
Reaching `x*` at epoch 0, 1 or 2 is an ordinary recorded event in A3 and is
**not** a stop.

Frozen, and deliberately minimal:

| # | condition | recorded as |
|---|---|---|
| A3-S1 | `t + 1 == T`, with `T = 32` | `HORIZON_REACHED` |
| A3-S2 | an §8 integrity condition holds | the job is **invalid**, not reported |

That is the complete list. **A3 runs all 32 transitions unless the job is
invalid.** It does not stop on reaching `x*`, it does not stop when the order is
served, and it does not stop when an induced deficit closes: the horizon is the
only ordinary terminal condition, so the observation window after the order is
the same length in every arm and every replicate, and no arm's window is
shortened by its own behaviour.

Epochs after the chain has resolved are recorded as they occur. At `x*` with no
active demand the epoch status is `NO_ACTIVE_DEMAND` and nothing executes;
these epochs are inert by construction, and running them costs nothing and
biases nothing. A stall in which every candidate stays unaffordable likewise
runs to the horizon and is recorded at every epoch rather than truncated.

### Restoration timestamps, defined exactly

The loose phrase "whether an induced deficit returns to zero" is **withdrawn**.
It does not say *which* deficit, and with more than one open coordinate "any"
and "all" are different claims. Both are now defined, and reported separately.

Let `s` be the epoch at which the order is served — the single epoch whose
executed transition completes it — and `x_{s+1}` the post-service state.

```
tracked_deficits  =  { c : deficit_c(x_{s+1}) > 0 }
```

frozen at that moment. It is the set of coordinates carrying a P-demand
**derived from the post-service state**, and it is not re-opened by deficits
that appear later for unrelated reasons.

| quantity | definition |
|---|---|
| `tracked_deficits` | the set above, with its exact per-coordinate deficits at `s + 1`. Possibly **empty** |
| `first_closure[c]` | for each tracked `c`, the least post-state index `u > s` with `deficit_c(x_u) == 0`, or `None` if no such `u <= N` exists. Per coordinate, independently |
| `first_simultaneous_closure` | the least post-state index `u > s` at which **every** tracked coordinate simultaneously has `deficit_c(x_u) == 0`, or `None`. Defined only when `tracked_deficits` is nonempty |
| `closure_count` | how many tracked coordinates have a defined `first_closure` — recorded so partial closure is visible as partial |

**`first_simultaneous_closure` is not `max(first_closure[c])`, and is never
computed as one.** A coordinate may close, reopen as the arm keeps acting, and
close again; the maximum of the per-coordinate firsts can therefore name an
index at which the tracked set is not jointly clear. The simultaneous quantity
is evaluated by testing the whole tracked set at each index in turn.

**An empty tracked set is never a demonstrated restoration.** If serving the
order leaves no physical deficit at all, there was nothing to restore, and the
episode is recorded as `SERVED_WITHOUT_RESTORATION` with
`served_without_restoration_reason = NO_INDUCED_DEFICIT`. Reporting that as
`RESTORATION_COMPLETED` would count the absence of a demand as evidence that
the mechanism met one, and it is explicitly forbidden here.

### The four chain facts are recorded separately, never merged

Admission, service, pendency and physical restoration are four different facts
about the order, and one label cannot carry all four. Each is recorded in its
own field, and the summary label is derived from them rather than substituted
for them:

| field | what it records |
|---|---|
| `order_admission_status` | admitted, or the exact rejection reason, and the epoch of the admission decision |
| `order_service_epoch` | `s`, the epoch whose executed transition completed the order, or `None` if it was never served |
| `order_pending_epochs` | every epoch at which the order was held and unserved, with the reason at each — `ALL_PLANS_EBU_UNAFFORDABLE` or `NO_COMPLETE_PHYSICAL_PLAN` — so a pendency is never reported as a single undated status |
| `restoration_facts` | `tracked_deficits`, `first_closure`, `first_simultaneous_closure`, `closure_count`, and the per-epoch restoration ledger |

### The summary label, deterministic and exhaustive

Evaluated in order; the first matching row supplies `order_outcome`. Every
episode matches exactly one row, and the fifth row exists because §2 already
declares that a blocked economic component is an **ordinary** A3 outcome rather
than an integrity failure, while the earlier four-label set had nowhere to put
it.

| # | condition | `order_outcome` |
|---|---|---|
| L1 | the order was refused at admission | `ORDER_REJECTED` |
| L2 | admitted, never served, and at every pending epoch the recorded reason was `ALL_PLANS_EBU_UNAFFORDABLE` | `ORDER_PENDING_UNAFFORDABLE` |
| L3 | admitted, never served, and at least one pending epoch recorded `NO_COMPLETE_PHYSICAL_PLAN` | `ORDER_PENDING_NO_COMPLETE_PLAN` |
| L4 | served, and `tracked_deficits` is nonempty and `first_simultaneous_closure` is defined | `RESTORATION_COMPLETED` |
| L5 | served, and otherwise | `SERVED_WITHOUT_RESTORATION` |

`L5` carries a mandatory `served_without_restoration_reason`, so the label is
not lossy:

| reason | when |
|---|---|
| `NO_INDUCED_DEFICIT` | `tracked_deficits` is empty — serving the order created no shortfall |
| `INDUCED_DEFICIT_UNCLOSED` | `tracked_deficits` is nonempty and `first_simultaneous_closure` is `None` by the horizon. `closure_count` and `first_closure` record how far it got |

`ORDER_PENDING_NO_COMPLETE_PLAN` is a **reporting** addition. It introduces no
new physics, no new predicate and no new mechanism: it names a case §2 already
admits as ordinary in A2 and A3. Its presence does not weaken §8 — a
non-equilibrium `NO_COMPLETE_PHYSICAL_PLAN` in a **P-only** component remains an
integrity failure, and this label applies only to the admitted economic order's
component.

**None of these is a failure of the fixture**, and none of the frozen labels was
chosen or reordered after seeing an outcome: no episode had been executed when
this section was written.

### Use of a deterministic arrival schedule

A3 is the only episode needing an arrival at one declared epoch and at no
other, which the declared stochastic `ArrivalProcess` cannot express — it fires
per epoch with a fixed probability and has no epoch window. It therefore uses
`fixtures.ScriptedArrivals` with the schedule declared in full above.

**This is a proposed Stage-A-only mechanism-demonstration fixture, and four
things are true of it:**

1. **its schedule is fixed independently of any observed outcome.** It was
   written before any epoch was executed, and nothing in it was chosen from a
   trajectory;
2. **it is not evidence about a stochastic economic arrival law.** One declared
   order at one declared epoch says nothing about quantity, frequency,
   destination or multiplicity distributions;
3. **it supplies no authorization and no arrival-law decision for Stage B.**
   Stage B still requires the declared stochastic law, whose parameters remain
   unresolved in `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` §4 (B1);
4. **the scope declaration permitting it is a modeling disposition, not a
   mathematical theorem.** `fixtures.ScriptedArrivals` previously read "no study
   may use it"; that prohibition was scoped to registered *behavioural
   comparisons*, on the reasoning that its stated rationale — unresolved
   stochastic load parameters — is a Stage-B concern. **That reasoning is a
   judgement, and it is the one judgement call in this protocol.** It is not
   proved and is not presented as proved.

No stochastic process replaces it, and its scope is not broadened.

## 5. Policy arms

Exactly four, frozen, with the package's own identifiers:

| arm | rule | reads EBU to choose | applies affordability |
|---|---|---|---|
| `control_random_no_ebu` | uniform over complete plans, no affordability filter | no | **no** |
| `ebu_random` | uniform over affordable complete plans | no | yes |
| `ebu_aligned` | `argmax E_G` over affordable complete plans | yes | yes |
| `ebu_hostile` | `argmin E_G` over affordable complete plans | yes | yes |

**Every arm runs the identical physical and demand episode.** A1, A2 and A3 are
each defined by an initial state, a disturbance process and an arrival
schedule, all independent of policy, so the pairing is exact by construction.

Every arm chooses only **how** to serve demand that already exists. There is no
unrelated action available to any of them, because no such plan enters a menu,
and there is no voluntary no-op: when a component has an affordable complete
plan, one executes. The three legitimate inactions — `NO_ACTIVE_DEMAND`,
`NO_COMPLETE_PHYSICAL_PLAN`, `ALL_PLANS_EBU_UNAFFORDABLE` — are logged
separately and are never collapsed.

`ebu_aligned` and `ebu_hostile` break ties uniformly through the actor counter,
so all four arms are stochastic in general and all four are replicated.

---

## 6. Replicate and seed structure

| seed | role | value |
|---|---|---|
| `natural_seed` | disturbance draws | `1` (inert: the process never fires) |
| `arrival_seed` | arrival draws | `2` |
| `admission_seed` | random compatible-subset admission | `3 + k` |
| `actor_seed` | policy choice and tie-breaking | `1000 + k` |

`k` is the replicate index, `k = 0, ..., 63`. **64 replicates per arm per
episode class**, giving `4 arms x 3 classes x 64 = 768` episodes.

The replicate count is fixed here for containment and exact reproducibility,
not from a power calculation: Stage A carries no hypothesis and performs no
test, so there is nothing to power. Stage B's replicate count is a separate,
still-open decision and is **not** inherited from this number.

Every episode is fully replayable from
`(world_id, policy, natural_seed, arrival_seed, admission_seed, actor_seed,
initial_state)`, which is exactly what `EconomyRun.run_id` hashes.

---

## 6a. Run identity

Every registered Stage-A job is identified by
`sha256(configuration)[:16]`, where `EconomyRun.configuration` is the canonical
serialization of the **complete declared episode**:

```
MODEL_ID | registration | episode | world | policy | opening state digest
        | disturbance descriptor | arrival descriptor | seeds | replicate
        | registered flag | decomposition-gate flag
```

Every process object carries an exact `descriptor` in rational form, and a
scripted schedule serializes its **contents epoch by epoch**; a process without
a descriptor is refused rather than reduced to its class name. Serialization is
deterministic: the same configuration always produces the same identity, and
any difference in any listed field produces a different one.

**The collision this corrects.** A1 and A3 share world, policy, opening state
and all four seeds, and differ only in their arrival law — A1's empty process
against A3's one-order schedule. The previous identity read neither law and
assigned both jobs the same id.

Frozen requirement, checked by construction alone with **no epoch executed**:

> across all `3 x 4 x 64 = 768` declared jobs, `run_id` uniqueness is
> **768 / 768**, and rebuilding every job reproduces the identical 768
> identities.

## 7. Primary questions

Episode-native, frozen before execution. **Occupancy inside `O95` is not a
Stage-A endpoint and is not preregistered here.** No threshold is declared,
because Stage A declares no test.

### A1 — pure P-disturbance recovery

> **Whether and how each arm returns to `x*` after one declared displacement.**

Reported per episode, all exact:

| quantity | definition |
|---|---|
| `stopping_reason` | exactly one of `RETURNED_TO_REFERENCE`, `NO_AFFORDABLE_SOLUTION`, `HORIZON_REACHED`. **`NO_PHYSICAL_SOLUTION` is not a member**: §2 withdraws non-equilibrium physical impossibility as a normal A1 outcome |
| `return_time` | the first **post-state index** `t + 1` with `x_{t+1} == x*`, or `None`. Same definition as §2, no other |
| `transitions_recorded` | `N`, the number of transitions **actually executed**, reported beside the declared maximum `T` and never in place of it. `N <= T` always. `N == T` whenever the episode ran to the last permitted transition, which includes a return or an unaffordable stall occurring exactly at `T` as well as `HORIZON_REACHED` — the earlier claim that `N == T` identifies `HORIZON_REACHED` is **withdrawn**, because it is false in both tie cases §2 now resolves. The stopping reason is read from `stopping_reason`, never inferred from `N` |
| `horizon` | `T`, the declared maximum, recorded explicitly in every episode record so that `N` is never read as if it were the horizon |
| `burden_path` | the exact sequence `V(x_0) .. V(x_N)`, of length `N + 1` |
| `restoring_drift` | the exact sequence `V(x_t) - V(x_{t+1})` for `t = 0 .. N-1` |
| `plateau_crossings` | the transitions with `V(x_{t+1}) == V(x_t)` and a nonempty executed group |
| `terminal_state` | `x_N` |
| `terminal_no_active_demand` | derived from `x_N`, **not executed**: true exactly when `x_N == x*`. No further epoch is run to observe it |
| `reserve_path` | `B_total(t)` for `t = 0 .. N`, and the per-owner balances |
| `restoration_ledger` | `EpochRecord.restoration`, **persisted at the epoch it happened**: represented deficit, delivered, credited progress, remainder, overshoot, per progressed P-demand. No post-hoc reconstruction is used, and none is relied on |

### A2 — isolated economic demand

> **The admission / service / unaffordability outcome of one economic request,
> and its physical consequence.**

| quantity | definition |
|---|---|
| `arrival_state` | the order's lifecycle status at the end of the epoch |
| `epoch_status` | the declared epoch status |
| `menu_size` and `affordable_count` | for the order's component |
| `physical_consequence` | `x_1 - x_0`, and `V(x_1) - V(x_0)` |
| `induced_p_demand` | the P-demands derived from `x_1` |
| `receipts` | per-owner, exact |

### A3 — the `E -> P -> restoration` chain

> **Whether the physical demand created by serving an economic request is
> restored, and exactly how reserve circulates while it is.**

| quantity | definition |
|---|---|
| `prelude_reserve` | `B_total(3)` **and the per-owner vector** `(B_A(3), B_B(3), B_C(3))` at the arrival epoch, recorded rather than predicted (§4) |
| `arrival_baseline` | the recorded pre-arrival physical state `x_3`, which is **not assumed to be `x*`** (§4) |
| `order_admission` | admitted, or the exact rejection reason |
| `candidate_table` | for every plan in the order's component at that baseline: identity, post-state, exact aggregate EBU, exact per-owner receipts, the demands it serves, and affordability decided **per owner** against the recorded vector |
| `order_admission_status`, `order_service_epoch`, `order_pending_epochs` | the three chain facts, recorded separately (§4) |
| `order_outcome` | derived by the ordered decision table in §4, which is deterministic and exhaustive: one of `ORDER_REJECTED`, `ORDER_PENDING_UNAFFORDABLE`, `ORDER_PENDING_NO_COMPLETE_PLAN`, `RESTORATION_COMPLETED`, `SERVED_WITHOUT_RESTORATION`. Each is reported as itself, never as a failed chain |
| `served_without_restoration_reason` | mandatory whenever `order_outcome == SERVED_WITHOUT_RESTORATION`: `NO_INDUCED_DEFICIT` or `INDUCED_DEFICIT_UNCLOSED` (§4) |
| `deficit_provenance` | the pre-state and post-state deficit vectors for the executed transition, and which coordinates were **pre-existing**, **newly created** or **deepened** |
| `induced_deficit` | the P-demands derived from the post-service state |
| `restoration_outcome` | the exact restoration facts of §4: `tracked_deficits` frozen at the post-service state, `first_closure[c]` per tracked coordinate, `first_simultaneous_closure` over the whole tracked set, and `closure_count`. "Any deficit closed" and "all tracked deficits closed" are reported as the two different quantities they are, and an **empty** tracked set is never reported as a restoration |
| `stopping_reason`, `transitions_recorded`, `horizon` | A3 stops only at the horizon or on an §8 integrity failure (§4). It does **not** inherit A1's return stop, so the post-arrival observation window is the same length in every arm |
| `capacity_source_residual` | must be exactly `0` at every epoch and at the end |
| `accounting_residual`, `conservation_residual`, `nonnegativity_residual`, `separability_residual` | must each be exactly `0` at every epoch |
| `joint_gate`, `decomposition_gate` | must be verified at every epoch |

---

## 8. Integrity conditions that invalidate a job

Not outcomes. A job hitting any of these produced no valid data; the
implementation is corrected and the identical job is rerun with the identical
seeds.

- `SEARCH_UNRESOLVED` anywhere (`study_one.JobInvalid`);
- any of the four residuals nonzero at any epoch;
- `capacity_source_residual() != 0`;
- a joint-gate or decomposition-gate refusal;
- a state violating `x >= 0` or `sum_i x_i = 12`;
- **`NO_COMPLETE_PHYSICAL_PLAN` at any state other than `x*`, in episode A1
  only.** The enumeration that proves `x*` is the only absorbing state was run
  over the P-only graph, and A1 is the only P-only episode. In A2 and A3 a
  blocked economic component reporting that status is an ordinary recorded
  outcome, not an integrity failure (§2);
- a duplicate `run_id` among the declared jobs, which construction alone rules
  out at 768/768 (§6a).

---

## 9. What Stage A will not be allowed to claim

- that any arm restores in general, or with any probability;
- that EBU produces a restoring tendency;
- that the 91/91 accessibility result implies recovery;
- anything about a world other than `study-one-v1`;
- anything comparative between arms as a tested result.

Stage A is a mechanism demonstration. Every comparison is Stage B's, and Stage
B remains unfrozen: its arrival law, disturbance law, arm set, endpoint,
replicate count and reporting decisions are all still open, exactly as
`DEMAND_DRIVEN_STUDY_ONE_READINESS.md` §4 records them.

---

## 10. Freeze

This document is frozen as of the implementation pass that adopted **strong
atomic P-provenance** and rebound the registered run identity. It was written
before any Stage-A epoch was executed; no trajectory, no arm outcome and no
aggregate from any Stage-A episode existed when any choice above was made, and
no behavioural outcome was inspected at any point.

**Zero registered Stage-A epochs have been executed under this
preregistration.**

### Correction record

**This document has been corrected twice, both times before any execution.**
Each correction is recorded here rather than applied silently, and **every
superseded identity is retained**.

| | |
|---|---|
| freeze 1 identity | `72a950721a81a7e0e2dba28e1a1a47124769a3378a4d28cd34d7e1f8aace78de` |
| epochs executed under freeze 1 | **zero** |
| freeze 2 identity | `36fb53b6a3fca61be79391d1ab02927f148fa0d13f526f9b0895903f0fa91c75` |
| epochs executed under freeze 2 | **zero** |
| correction records | `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION_CORRECTION_1.md`, `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION_CORRECTION_2.md` |

#### Correction 1 (freeze 1 → freeze 2)

Changes made, all pre-execution and none derived from an observed outcome:

1. **§2** — one epoch convention stated and used everywhere; return time
   defined once, as the first post-state index; `T` declared as a transition
   count and distinguished from the number of transitions actually recorded;
   the non-equilibrium physical-impossibility integrity claim **scoped** to A1,
   the only P-only episode.
2. **§4** — the `-1` / `-4` figures and their post-states demoted to
   equilibrium-conditional examples; an analytical witness added showing the
   arrival baseline need not be `x*`, with the exact four-plan menu at
   `(5,3,4)`; the pre-arrival owner vector declared recorded rather than
   predicted; pre-existing deficits distinguished from newly created or
   deepened ones; reporting defined for rejection, pending-unaffordable and
   served-without-restoration.
3. **§4** — the deterministic arrival schedule restated as a proposed
   Stage-A-only fixture, with its four scope limits and an explicit statement
   that the permitting declaration is a modeling disposition, not a theorem.
4. **§7** — the A1 reporting table reconciled with §2 (`NO_PHYSICAL_SOLUTION`
   removed, return time and horizon corrected, derived terminal status added);
   the A3 reporting table rebuilt around the recorded baseline.
5. **§8** — the integrity list scoped to A1 for physical impossibility.

#### Correction 2 (freeze 2 → freeze 3)

Reporting definitions finished **before the first registered epoch**, so that
no definition could be settled after an outcome was visible. All pre-execution;
none derived from an observed outcome, because none existed.

1. **§2 stop conditions** — the three conditions are not mutually exclusive, so
   the precedence **S1, S2, S3** is declared explicitly and the tie on the final
   permitted transition is resolved: a return or an unaffordable stall at
   `t + 1 == T` outranks the horizon.
2. **§7 (A1)** — the claim that `N == T` identifies `HORIZON_REACHED` is
   **withdrawn**; it is false in both tie cases above. `N` is reported beside
   the declared maximum `T`, never in place of it, and the stopping reason is
   read from `stopping_reason` rather than inferred from `N`. `horizon` added as
   an explicit reported field.
3. **§4 (A3) stop conditions** — declared separately from A1's, because A3 must
   **not** inherit S1: its order arrives at epoch 3, and an episode stopping on
   reaching `x*` would terminate during the prelude and observe nothing. A3
   runs all 32 transitions unless the job is invalid, so the post-arrival
   window is the same length in every arm.
4. **§4 (A3) restoration timestamps** — "whether an induced deficit returns to
   zero" is withdrawn as ambiguous. `tracked_deficits` is frozen at the
   post-service state; `first_closure[c]` is per coordinate;
   `first_simultaneous_closure` is evaluated over the **whole** tracked set and
   is explicitly **not** `max(first_closure)`, since a coordinate may close and
   reopen. An **empty** tracked set is never reported as a restoration.
5. **§4 (A3) label map** — made ordered, deterministic and exhaustive, with the
   four chain facts (admission, service epoch, dated pendency, restoration)
   recorded **separately** from the label. `ORDER_PENDING_NO_COMPLETE_PLAN`
   added: §2 already declares a blocked economic component an ordinary A3
   outcome, and the four-label set had nowhere to put it. It is a reporting
   addition and changes no physics, predicate or mechanism.
6. **§7 (A3)** — the reporting table rebuilt on those definitions.

Nothing in the **environment, prelude, policies, arms, seeds, horizons, opening
balances, episode definitions or physical semantics** was changed by either
correction. No correction was made to make a document true of a mechanism that
does not behave that way: the mechanism is byte-identical to the audited
coordinate, `demand_driven_ebu` =
`f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48`.

### Authorization note

`AGENTS.md` defines a correction procedure for *committed* result artifacts and
manifests, and the repository's convention for amending a frozen prospective
source is a separate addendum with explicitly narrow precedence. It defines no
general procedure for re-freezing a preregistration that is **uncommitted** and
under which **no epoch has executed**, which is this case.

> **The author has authorized this pre-execution correction and re-freeze**, on
> the conditions applied here: previous identities retained, correction history
> preserved in full, and zero epochs executed under any superseded identity.
> Freeze 3 below is therefore an **authorized** re-freeze, not a proposed one.

The authorization covers the documented pre-execution correction only. It is
not authorization to amend this document after an epoch has run: any such
change would require a separate correction stage under `AGENTS.md`.

### Cryptographic identity

The identity below is the SHA-256 of this file's bytes with the identity line
itself normalized, so it is stable under its own recording. It is recomputed by
`scripts/stage_a_preregistration_identity.py`, which reads the file and prints
the digest; that script executes no model code.

```
PREREGISTRATION_SHA256 = a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17
```

**At the moment of this freeze, zero registered Stage-A epochs had been
executed.** Execution status after the freeze is recorded in
`results/demand_driven_stage_a/EXECUTION_INVENTORY.json`, never by editing this
document: these bytes are sealed by the identity above and are not amended once
an epoch has run.
