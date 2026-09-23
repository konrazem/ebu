# Demand-driven EBU economy — scientific contract

**Model id `EBU-DEMAND-DRIVEN-ECONOMY-v1`. Status: IMPLEMENTED AND
CONFORMANCE-TESTED, NOT REGISTERED.** Nothing here is preregistered or frozen
as a study, no behavioural claim is adopted, and no result about this economy
exists. Building a model is not evidence about it.

Implementation: `demand_driven_ebu/`. Conformance gate:
`test_demand_driven_ebu.py`. Rehearsal: `demand_driven_rehearsal.py`
(non-confirmatory).

---

## Correction log

An independent read-only audit of commit `22fd229` found five defects. All
five are corrected here, and the corrected semantics are what this document
describes. Corrections are recorded in place, not erased.

| # | defect at `22fd229` | correction |
|---|---|---|
| 1 | Economic service was tested per demand against the plan increment, so two independent orders of `q = 2` at one destination were both reported served by `2` delivered units | Economic quantities are **additive** across separate orders. Service is decided over the whole requirement set, in `service`. §3 |
| 2 | — (confirmed correct) | E/P overlap remains legitimate: a physical shortfall is a post-state condition and draws nothing from the economic pool. The combined requirement is a **maximum**, not a sum. §3 |
| 3 | Coupling merged every demand in a transport-connected component, so an unserviceable demand froze serviceable ones that it could not possibly compete with | Coupling is decided from **actual binding constraints**, computed from the plans that individually serve each demand. §6 |
| 4 | The decision packet required admitted demand components to be identical across arms, which is impossible in a closed loop | Arms share an identical **raw arrival stream**; admission is endogenous and legitimately differs. Comparisons are reported over the common raw arrival set. §5a |
| 5 | An interval was classified actor-only when `sum dV_ext == 0` | Actor-only is decided from explicit **external-event provenance**. External events can cancel in the potential or permute stock at constant `V`. See the cycle theorem document. |
| 6 | A sink could be exported from by an ordinary route | A sink is irreversible: a world declaring a route out of one is refused at construction. §13 |
| 7 | The structural reach was described as *exact* in every world, which a later audit disproved with a destination-capacity/loss counterexample | Exactness is claimed **only** inside the frozen Study-1 domain. Elsewhere the reach is a sound superset that can over-couple; findings F-5 and F-6 record the two known cases. §6, §16 |
| 8 | Feasibility was defined by whatever the component decomposition produced | The decomposition-free **progress reference** is the authority; decomposition is an optimization, proved equal inside the frozen domain and gated epoch by epoch. §6, §16 |
| 9 | The global oracle asked "can every demand be served at once?", so when one component was blocked it compared empty against empty and passed vacuously | The authority is now the **progress** reference, which lets an independent part act while another is blocked. The narrow query survives as `F_all_complete` and is explicitly not runtime semantics. §6, §16 |
| 10 | Sampling was claimed to follow from a bijection onto outcomes | **Withdrawn.** The bijection is onto **plan identities**; `Phi: plan -> outcome` is many-to-one. The random actor is uniform over canonical plan identities and outcome probability carries plan multiplicity. §16 |
| 11 | The oracle compared pre-affordability physical plan sets as though they were runtime execution menus, so it checked a law no EBU arm samples from | The physical reference is kept and is explicitly pre-affordability. A **policy-conditioned** layer conditions on balances and policy: EBU arms select within `G_affordable`, the comparator bypasses it. Level A alone is declared not to be a runtime verification. §6, §16 |
| 12 | The combined requirement at a coordinate was `max(sum_d q_d, deficit_c)`, applying the **economic** completion contract to a **physical** condition. Exhaustive enumeration of the frozen Study-1 world showed this made 36 of its 91 states absorbing away from equilibrium, none of them for reasons of resource scarcity | The two contracts are separated and never collapsed into one threshold. Economic service stays complete and additive; physical service is **atomic** — genuine positive progress on the represented deficit, re-derived from the post-state. Finding **F-7**. §2.1, §3 |

## 0. The correction this model makes

Earlier behavioural studies let actors choose from broad sets of physically
possible transfers each tick. That is not the intended economy. A physical
action belongs in an economic decision set **only because it serves an existing
demand**:

> physically possible ≠ economically relevant candidate.

The corrected order is fixed and every stage is separated in code:

```
demand
  -> demand-serving plans
  -> can this plan actually happen right now?
  -> exact EBU valuation
  -> affordability
  -> actor choice
  -> execution
```

An actor may not spend capacity on an unrelated transfer merely because the
transfer is possible. This is a restriction on *where* capacity may be spent.
It is not a change to what EBU measures.

## 1. Plain language

Two phrases carry the model, and they are used in preference to
"physical feasibility", "candidate response" and "arbitrary state-changing
action", which are avoided in explanatory text.

**Demand-serving plan.** A set of physical actions that fully answers every
demand in one coupled group of obligations.

**Can this plan actually happen right now?** A plan can happen only if the
required stock already exists at its sources, the routes exist, the quantities
are available, hard capacities are respected, no stock becomes invalid,
conservation and declared loss rules close, and simultaneous actions do not
overuse the same shared stock.

## 2. The two demand classes

### 2.1 P — physical / homeostatic demand

P-demand comes from the physical state itself and is never independently
sampled. At a coordinate carrying a declared reference, a shortfall

```
x_i < x*_i,   required q_i = x*_i - x_i
```

*is* a physical need. In a closed world with `sum_i x_i = sum_i x*_i` local
shortfalls are accompanied by surpluses elsewhere, so the state contains
everything needed to reconstruct P-demand and no queue is required to remember
it.

- The shortfall persists ⟹ the demand persists, automatically.
- The shortfall is resolved ⟹ the demand disappears, automatically.
- P-demand cannot be rejected. A physical shortfall cannot be voted out of
  existence. It can only be resolved, left unresolved, be currently impossible
  to resolve, or be currently unaffordable to resolve.

A coordinate outside `V` — an audit-only loss sink — has no declared reference,
so it has no shortfall and generates no demand. Contract section 23 forbids
pretending otherwise, and the derivation cannot invent one because there is no
reference to compare against.

A surplus is not a demand. It is availability. This is a declared reading:
"need" is what you lack.

#### P-demand is served atomically, and that follows from the above

Because the shortfall *is* the state, a partial restoration loses nothing: the
remainder is still there, still visible, still a demand, at the next
derivation. So a plan serves the physical demand at `c` exactly when

```
delta_G[c] > 0
```

and **not** when it closes the whole deficit. A deficit of four restored by two
simply presents as a deficit of two next epoch:

```
deficit 4  ->  restore 2  ->  the state encodes deficit 2  ->  restore 2  ->  0
```

No backlog, no queue, no residual-demand object and no bookkeeping of any kind
is introduced, because none is needed — this is the atomic-action principle the
model already rests on, applied to the demand side.

**Attribution is capped; legality is not.** A plan delivering more than the
represented deficit is legal, and is credited with restoring only
`min(delta_G[c], deficit_c)`. The excess is not service. It is a physical fact
that the next derivation reads back as an opposite deviation.

**Provenance stays local.** Irredundancy — in the served-set-relative form of
§7 — keeps an action unrelated to a *currently* represented deficit illegal. It does not become legal
because it would help the state that some other action is about to create. The
permanent regression is `study_one_world` at `(5,4,3)`: the only deficit is at
`C`, the menu is exactly the two `B->C` restorations, and `A->B@1` enters no
menu until the next state, where `B` is the coordinate that is short.

**Refinement is preserved — CONDITIONALLY, and that is the exact strength of
the result.**

> **Conditional restorative refinement.** If a two-unit restorative action is
> legitimate and the declared quanta permit the split, then the first one-unit
> half is legitimate; and the second half is legitimate **for as long as a
> deficit remains at the destination**.

Exhaustively over the frozen Study-1 world:

| | count |
|---|---|
| legal two-unit singleton restorations | **152** |
| both halves legitimate, destination deficit still open after the first | **120** |
| first half **clears** the destination deficit, so the second has nothing left to progress | **32** |
| failures of the conditional statement | **0** |

**Unrestricted subdivision invariance is NOT claimed, and is not true.** The 32
cases are the guard working: once the deficit is closed, the second half is an
ordinary continuation with no demand to serve, and it is refused for exactly
the reason `A->B@1` is refused at `(5,4,3)`. No persistent demand, historical
entitlement or overshoot exception is introduced to obtain a stronger theorem.
Whether unrestricted subdivision invariance is wanted instead is an
**unresolved modeling decision**, recorded and not taken.

Two permanent regressions pin both halves of this:

- `(2,6,4)` — the withdrawn rule admitted `B->A@2` and refused its own half
  `B->A@1`; both are legal now;
- `(1,4,7)` — the second half is **neutral in EBU** (`0`, restoring `A` while
  deepening `B`) and **still legitimate**, because a deficit remains at `A`.
  Neutral value does not erase provenance.

This replaces the earlier rule that a physical demand was served only by
closing its whole deficit in one plan. That rule is **superseded for Study-1
physical restoration**; the exhaustive evidence that forced the change, and the
before/after enumeration, are recorded as finding **F-7**.

### 2.2 E — exogenous economic demand

E-demand is an external request `(resource, quantity, destination)`. It need
not correspond to any physical shortfall. EBU does not decide why society wants
the resource; it measures the physical consequence of the ways of supplying an
accepted request.

Economic demand **may exceed what physically exists**, and such a request is
valid. It is not truncated, regenerated smaller, or quietly supplied with the
missing quantity. It is there to reveal scarcity. Three outcomes are recorded
separately and never merged:

| outcome | meaning |
|---|---|
| `E_REJECTED_PHYSICAL_SCARCITY` | no complete physical plan exists; decided before EBU |
| `E_REJECTED_INCOMPATIBLE` | serviceable alone, not jointly with the admitted subset |
| `E_ADMITTED_BUT_EBU_UNAFFORDABLE` | plans exist, none affordable; the demand is **not** erased |
| `E_SERVED` | delivered in full |

## 3. The service contract

Service is decided over the **whole requirement set**, never one demand at a
time. Testing each demand independently against the plan's increment was the
audit's first defect: it let one delivered unit satisfy two separate orders.

**Economic quantities are additive.** Separate demand ids are separate
material obligations. For a plan `G` and destination `c` the **service pool**
is what `G` actually put there,

```
pool(G, c) = max(0, delta_G[c])
```

and an allocation assigns each order `s_d(G)` with

```
0 <= s_d(G) <= q_d,        sum_d s_d(G) <= pool(G, c)
```

Order `d` is completely served exactly when `s_d(G) = q_d`. Two independent
orders of two units therefore need four delivered units, never two.

The pool is **net, not gross**, and that is deliberate: a unit that arrives at
`c` and leaves again in the same plan is not present afterwards, so it is
available to nobody. Counting gross inflow would reintroduce the same
double-count one level down.

**Physical demand is not an economic quantity claim.** A shortfall at `c` is a
condition on the physical state. It draws nothing from the economic pool, and
nothing is subtracted between the two: the same two delivered units may fulfil
a two-unit order *and* restore a two-unit deficit, because both conditions ask
for the same units to be present afterwards.

**The two claims do not share a completion contract, and are never collapsed
into one threshold.** They are applied side by side:

```
serves_economic(G, c)   <=>   delta_G[c] >= sum_d q_d        complete, additive
serves_physical(G, c)   <=>   delta_G[c] >  0                atomic progress
```

### The service predicate, stated exactly

A plan `G` serves a requirement set `R` exactly when **both** hold:

1. **every** economic claim in `R` is completely served, under additive
   economic accounting — `delta_G[c] >= sum_d q_d` at every coordinate `c` of
   `R` carrying orders;
2. `G` serves **something**: either `R` contains an economic claim, which
   condition 1 has then served completely, **or** at least one physical demand
   present at the pre-action state receives strictly positive progress.

```
serves_all(G, R)  <=>   (all c in R : economic_total(c) == 0
                                      or delta_G[c] >= economic_total(c))
                   and  ( (exists c in R : economic_total(c) > 0)
                          or (exists c in R : deficit(c) > 0 and delta_G[c] > 0) )
```

**The guard on the economic clause is load-bearing, not decoration.** The
economic inequality is asserted only at coordinates that actually carry an
economic obligation. Written without the guard — `all c in R : delta_G[c] >=
economic_total(c)` — it reads `delta_G[c] >= 0` at every physical-only
coordinate, and so forbids a plan from *drawing stock out of* any coordinate
represented in `R`. That is exactly the restriction strong atomic provenance
removed, re-imposed through a quantifier.

A verified witness, reproduced as an isolated pure-function regression. At
Study-1 state `(2,3,7)` the derived requirement set is `A: deficit 2`,
`B: deficit 1`, both with `economic_total = 0`. The plan `B->A@1` has increment
`(1,-1,0)`. The implementation returns `serves_all = True` — correctly: it
progresses `A`'s pre-state deficit. The unguarded display returns **false**, on
the coordinate `B` that the plan draws from. The guarded form returns true and
agrees with the implementation. `serves_economic` in `service.py` has always
been vacuously true at `economic_total == 0`; only the displayed equation was
wrong, and only the equation is corrected here.

Four readings follow, and the second is the one an earlier revision of this
section got wrong:

- **an empty requirement set supplies no provenance.** `serves_all` is false on
  it, so no plan can be justified by a demand that does not exist;
- **economic-only service is legitimate and needs no physical progress.** A
  component holding one order and no shortfall is served by completing the
  order, full stop. The previous wording — "every economic claim complete *and*
  at least one physical claim progressed" — was a conjunction, and it excluded
  exactly that case, including Stage-A episode A2 at the reference state, where
  there is no physical claim at all;
- **a plan need not progress every physical demand in its component.** The
  physical side is existential by design (§2.1);
- **provenance is not a claim about consequences.** That a plan may be
  considered says nothing about whether it is beneficial. The exact EBU values
  the entire transition, `E = V(pre) - V(post)`, with every side effect at full
  weight, and affordability and every actor policy see that number.

This is the **menu** predicate. Admission's protection of an existing physical
need asks a different and strictly stronger question — whether some plan
completely serves the new orders *and* progresses every existing need — and
that coexistence question lives in §4 and nowhere else. The two are never
merged.

The earlier form `delta_G[c] >= max(sum_d q_d, deficit_c)` is **withdrawn**. It
imposed the economic contract on a physical condition, and finding F-7 records
what that cost. A single physical delivery may still do both at once — that is
the whole point of keeping them side by side rather than netting them.

Four consequences are deliberate.

1. **No double credit is possible.** Economic service is measured against a
   single shared pool per coordinate, so no delivered unit can be claimed by
   two orders; and the pool itself is a property of the plan's net increment,
   so there is no per-action credit ledger in which anything could be counted
   twice.
2. **E/P overlap stays legitimate.** The two claims are different kinds of
   statement and are never netted against each other.
3. **No partial ECONOMIC service.** Backlog quantity, fractional fulfilment of
   an order, deadlines and service quality do not exist. If complete economic
   service is impossible the order — and its component — remains unresolved.
   The allocator can report a partial fill, but only as a diagnostic that
   explains a shortfall; no completion predicate consults it. **Partial
   physical restoration is a different thing entirely and is the declared
   P-demand semantics** (§2.1): it introduces no backlog because the physical
   state already carries the remainder. The restoration record is likewise a
   diagnostic — the authoritative remainder is whatever the next derivation
   reads off the state.
4. **Overshoot is permitted.** Delivering more than required still delivers
   the requirement. This is what leaves a hostile actor a real choice: it may
   answer the obligation destructively. Forbidding overshoot would collapse
   the hostile policy into one that cannot act. **No no-overshoot rule is
   introduced by atomic P-service**, and any overshoot is represented in the
   resulting physical state and therefore in the next P-demand and in every
   EBU valuation that follows.

These semantics govern **everywhere**: admission compatibility, joint
serviceability, plan enumeration, plan validation, completion bookkeeping,
the service audit and the saved artifacts. They are not a patched final
predicate.

## 4. Admission — random compatible subset

Admission is an upstream **economic** policy. It is not EBU. It is given no
access to EBU values, the potential, capacity balances or future receipts, and
an AST check in the conformance gate asserts that the module names none of
them. It optimizes nothing: not quantity, not customer count, not value, not
price, not age.

A subset `S` of the arriving requests is **admissible** when, computed from
physics alone:

- every arrival in `S` is itself serviceable once admitted, and
- admitting `S` newly breaks no pre-existing obligation.

The second condition is asked as a **coexistence** question, not a
serviceability one:

```
is there a plan that completely serves these new orders
AND progresses every physical need that already exists?
```

That distinction became load-bearing with strong atomic provenance. A menu plan
is never obliged to progress every P-demand of its component, so serviceability
alone can no longer see that a new order would consume the stock an existing
need depends on. `admission.starved_ids` asks the conjunctive question, and it
is the **only** place the conjunction is asked: nothing in the runtime menu
inherits it.

The second condition is the protection of P-demand. A new *optional* economic
obligation must not be allowed to make an already-existing physical need
impossible when that is visible in advance. Obligations that are *already*
unserviceable are excluded from the comparison rather than treated as vetoes;
otherwise one stuck demand would freeze admission permanently.

The policy then enumerates the inclusion-maximal admissible subsets and picks
one **uniformly** with its own independent random stream.

**The sampling measure, stated rather than assumed.** The draw is uniform over
inclusion-maximal admissible *subsets*. That is **not** uniform over demands
and does not give every request the same marginal admission probability. With
`k` pairwise-incompatible arrivals the maximal subsets are the `k` singletons
and each request is admitted with probability `1/k`; a request compatible with
everything appears in every maximal subset and is admitted with probability
`1`. Marginal admission probability is a function of how a request sits in the
compatibility structure. Any study reporting admission rates must report the
induced per-demand marginals rather than assuming them flat. This is a
property of the declared rule, not a defect: the rule is required to be
arbitrary and EBU-blind, not fair.

Serviceability is decided under the additive semantics of §3. Two orders of
700 units against 1000 available stock are not jointly serviceable even though
each is serviceable alone.

**P-demand's priority is ontological, not social.** It cannot be rejected
because it is literally encoded by physical state, while an E-demand is a new
optional obligation being considered. This is model semantics. It is not a
claim that physical need outranks economic need morally.

## 5a. Comparison contract — identical raw arrivals, endogenous admission

Arms share an **identical exogenous arrival stream**, because arrivals are a
pure function of `(seed, epoch)`. Admission, by contrast, reads the physical
state, and prior actor behaviour leaves different arms in different states, so
**arms legitimately admit different subsets**. That is a closed-loop outcome,
not a leak: admission still inspects no EBU value, no capacity balance and no
future receipt.

An earlier version of the decision packet required admitted demand components
to be identical across arms. That requirement is withdrawn: it is unsatisfiable
in a closed loop, and enforcing it would mean feeding one arm's admission
decisions to another.

The consequence for measurement is strict. **A service rate computed over
admitted demands alone is never the primary whole-system comparison** — an arm
that admits little and serves all of it would score perfectly. Every comparison
is reported over the **common raw arrival set**, and each incoming demand
carries a lifecycle state:

`ARRIVED`, `ADMITTED`, `REJECTED_PHYSICAL_SCARCITY`, `REJECTED_INCOMPATIBLE`,
`SERVED`, `ADMITTED_BUT_UNRESOLVED_PHYSICAL`, `ADMITTED_BUT_EBU_UNAFFORDABLE`.

## 5. Active demands — no queue, no scheduler

```
D_t = D_t^P  ∪  D_t^E
```

is an **unordered** set. P-demands are re-derived from the state each epoch.
Admitted E-demands stay active until served. Rejected arrivals never become
obligations. Nothing is dropped merely because it was not served this epoch.

There is no FIFO, no oldest-first, no deadline, no scheduler priority, no
sorting by EBU and no service order. Insertion order is destroyed by a
canonical sort on demand id, the demand objects carry no age, deadline,
priority, position or rank field, and an AST scan over the model code asserts
that no scheduling identifier exists anywhere in it.

Both classes coexist. A system may hold three P-demands and two E-demands at
once. Neither class is processed before the other.

## 6. Coupling and components

Two invariants govern this section, and both are frozen.

**Unusable-infrastructure invariance.** If a world modification changes neither
the set of physically executable actions nor any genuine binding physical or
account constraint, it must not change demand coupling, complete-service
possibilities, or admission. Adding or removing a route that can carry no
allowed action quantity must be behaviorally invisible.

**Decomposition invariance.** Demand decomposition is an implementation
factorization, not a restriction on the global feasible service set.

**Incorrect coupling is scientifically material.** It does not merely cost
parallelism. Wherever complete-service, search-size, simultaneity or other
joint constraints exist, merging demands that do not interact can destroy
serviceability outright, because a component is served in full or not at all
and one unserviceable member takes the rest down with it. Coupling must
therefore preserve the global feasible-service set, and that is tested against
a decomposition-free oracle rather than argued.

An independent audit demonstrated the cost concretely. Three independent
one-unit deliveries with distinct owners, plus two connecting routes of
capacity `1/2` against a minimum action quantity of `1`: the executable action
set was unchanged, yet the three demands merged into one component needing
three actions where two were permitted, and **all service vanished**. Two
routes that can carry nothing had changed serviceability.

Coupling is consequently derived from the **structural reach** — a set of
tokens proved in `enumeration.structural_reach` to contain the support of
every *minimal* plan serving a demand, computed from the world and the frozen
baseline. It is free of the plan-size cap, free of padding, and blind to
routes that carry no action.

**It is a sound superset in every domain, and exact only inside the frozen
Study-1 domain.** Route liveness is necessary everywhere and sufficient only
there, so outside Study 1 the reach can over-couple. Two such artifacts are
known, kept as permanent regressions, and not repaired: a declared storage
capacity that cannot bind merges independent demands through the
capacity-relief limb (finding F-5), and two lossy routes merge through a
shared loss sink (finding F-6). Nothing in this contract claims exact
loss-aware or capacity-aware coupling. See §16 and
`DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md`.

Blindness to unusable routes has **two** limbs, and a second audit showed that
capacity alone is not enough. A route is invisible to the reach when it cannot
carry any allowed quantum *or* when its source cannot fund the smallest
quantum it could carry at the frozen baseline. Source-funding forbids a
coordinate from paying for an outflow with quantity arriving in the same
instant, so a route out of an empty stock carries no action in any plan at
this state — not even inside a simultaneous group. Two such routes, of ample
capacity but with empty sources, were enough to merge the three independent
deliveries again and destroy all service while the executable action set stayed
identical. The reach is therefore state-aware: a route can be usable in the
world and dead in the state. Neither raw
transport connectivity nor enumerated serving plans are used: the first merges
demands that never compete, and the second admits padded plans whose
unnecessary actions drag unrelated coordinates and owners into the reach.

Two demands are coupled when their service possibilities genuinely interact
through a shared service-delivery pool (the same destination, where economic
quantities are additive), competing stock, a shared executable route and its
hard capacity, a shared hard physical constraint or potential-bearing
coordinate, one executable action serving several demands, or a shared owner
account where joint settlement genuinely binds.

Accounts are held by **nodes**, not coordinates, and the owner of an action is
its **source** node. So a sand demand and a water demand supplied from the same
node are coupled through joint affordability even with no stock and no route in
common. That coupling is required rather than conservative: joint affordability
is checked jointly at execution, and decoupling such demands would let the
joint gate discover a conflict it should have prevented.

A demand **proved** to have no physically realizable service possibility binds
nothing and is coupled only to demands at its own destination. This is sound,
not lenient: if no plan serves it alone, no joint plan serves it either, since
the actions that would raise its increment come from the same structural reach
and a joint plan has no more of them available. Coupling it to a serviceable
neighbour would destroy that neighbour's service for nothing.

**Uncertainty is not impossibility.** The serviceability search returns three
answers — serviceable, impossible, and undecided when it exhausts its budget —
and all three are carried through coupling and admission. A demand whose
search was undecided keeps its **full** reach and is **not** rejected for
scarcity; the uncertainty is recorded instead. Emptying a reach or refusing a
demand on an undecided search would convert a computational limit into a
physical claim.

**Where a component still freezes**, it is a declared restriction, not
unavoidable scarcity. An order of 25 units at a coordinate that also carries a
two-unit shortfall freezes both, because they share a pool and the combined
requirement is `max(25, 2)`. The same order at a *different* coordinate freezes
nothing. And where genuine competition makes a component jointly unserviceable
while a sub-collection would be serviceable, it is the complete-service
contract — not physics — that forbids serving the subset.

**Enumeration stays generous.** The narrow reach decides coupling only; menus
are built over every route touching the component's transport closure. Breadth
in enumeration can only offer more valid plans, never delete one.

**Decomposition does not define feasibility.** The authority is the
decomposition-free **progress reference** `G_progress(x, D)`: the family of
things one epoch is allowed to do, where a part proved impossible is
`BLOCKED`, contributes no physical action and leaves its demands unresolved,
and **every other part contributes exactly one complete plan**. There is no
voluntary no-action.

A narrower query — *can every active demand be completely satisfied at once?*
— survives under the explicit name `F_all_complete`. It is mathematically
useful and is **not** runtime semantics. Conflating the two hid a defect: when
one component is blocked, `F_all_complete` is empty, the component path was
also empty, and the comparison passed on `0 == 0` having seen nothing.

That reference is **pre-affordability**: it reads no balance and no policy,
and it is deliberately not the runtime action distribution for an EBU arm. A
second layer conditions on the node balances and the policy identity —
`G_affordable` is the subset whose projected owner balances all stay
non-negative, the three EBU arms select within it, and the comparator
intentionally bypasses it and samples over `G_physical`.

Demand-component decomposition is a computational optimization, proved equal
to the progress reference inside the frozen Study-1 domain (Theorem D) and
checked epoch by epoch by `EconomyRun(decomposition_gate=True)` at four
**policy-conditioned** levels — physical eligibility, the affordable set under
this run's balances, the selection law this policy induces over canonical plan
identities, and the modeled-outcome law it pushes forward. Level A alone is
not a runtime verification. A disagreement refuses the run. Outside the frozen
domain the equality is unproved.

## 7. Service plans, and demand provenance

A plan enters a menu only if it **serves** its component in the sense of §3,
**can happen now**, and is **irredundant**.

### Irredundancy is served-set relative

> A plan `G` is **redundant** exactly when some proper subset `S ⊂ G` executes
> and serves **every demand `G` actually serves**. Merely serving *some*
> demand is not enough to establish redundancy.

```
redundant(G)  <=>  exists S ⊂ G :  executable(S)
                                   and serves_all(S, R)
                                   and served(S) ⊇ served(G)
```

The earlier form — "some proper subset already serves the component" — is
**withdrawn**. With the physical side existential it is far too strong: one
action satisfying the existential predicate would make every joint plan
redundant, and an economic order answered in the same epoch as a physical
restoration would collapse to the economic action alone, making one class wait
for the other. §3 forbids that in either direction.

**The prohibition on appended actions is unchanged in force.** An action bolted
onto a legitimate plan answers nothing new, so dropping it leaves `served`
unchanged, the subset dominates, and the padded plan is refused. Conversely, in
an irredundant plan every action is necessary for something: for each `a`,
either `G \ {a}` loses a demand that `G` serves, or `G \ {a}` cannot execute at
all. That set is the action's **provenance**, it is non-empty by construction,
and it may be many-to-many.

### The explanatory regression

State `(3,6,3)`, reference `(4,4,4)`. Two shortfalls stand, one unit at `A` and
one at `C`, and they are one coupled component.

| plan | serves | post-state | exact EBU |
|---|---|---|---|
| `{B->A@1, B->C@1}` | `P:r\|A`, `P:r\|C` | `(4,4,4)` | `+3` |
| `{B->A@1}` | `P:r\|A` only | `(4,5,3)` | `+2` |
| `{B->C@1}` | `P:r\|C` only | `(3,5,4)` | `+2` |

Neither singleton serves everything the joint plan serves, so neither
dominates it: **the joint plan is not redundant**, and all three are in the
menu. Under the withdrawn rule the joint plan would have been refused, and the
two needs could never have been answered in one epoch.

With no active demand there are no components, hence no plans, hence an empty
menu. Nothing needs to forbid the arbitrary transfer separately — it has
nowhere to come from. In the reference-state fixture, 18 transfers are
physically possible and every one of them is offered to no actor.

## 8. Valuation, capacity and choice

Valuation happens only after demand and physics:

```
E_G = V(x_pre) - V(x_pre + delta_G)
R_a = -mu(z)^T delta_a - (1/2) delta_a^T H delta_G,     sum_a R_a = E_G
```

on one frozen baseline and one common path. Simultaneous children are never
settled from same-baseline singleton quotes, and the conformance gate shows
those quotes do **not** sum to the group value while the common-path receipts
do.

Capacity is **V1, unchanged**: `B_i >= 0`, earned through positive receipts,
consumed by negative ones, no overdraft, no borrowing, no genesis grant, no
refill, no pooling, no direct transfer. Capacity never changes what EBU
measures — given the same pre-state, demand and plan, `V_pre`, `V_post`, `E_G`
and every receipt are identical whatever the balances are. The only thing
balances decide is affordable or not. This is enforced structurally (the
valuation module is never handed a ledger) and asserted metamorphically.

Actor policies choose only among equally complete answers to the same
obligation:

| policy | rule | reads EBU | applies affordability |
|---|---|---|---|
| `ebu_aligned` | `argmax E_G` | yes | yes |
| `ebu_random` | uniform | no | yes |
| `ebu_hostile` | `argmin E_G` | yes | yes |
| `control_random_no_ebu` | uniform, no filter | no | no |

The random and control policies reach their choice through a function whose
entire input is a count. They cannot see an EBU value because none is passed.

**No voluntary no-action.** If a component has a complete, executable,
affordable plan, one executes. Legitimate inaction exists only in three
physically distinct situations, logged separately: `NO_ACTIVE_DEMAND`,
`NO_COMPLETE_PHYSICAL_PLAN`, `ALL_PLANS_EBU_UNAFFORDABLE`.

## 9. Simultaneous execution and the joint gate

Every component with an affordable selected plan executes in the same epoch.
The selected plans are combined into one group, valued once, and the gate
checks that combining them changed nothing: the combined `E_G` must equal the
sum of the component values and every receipt must be unchanged. A discrepancy
means two supposedly independent components interact, which is a defect in the
dependency graph. The harness refuses loudly rather than sequencing them
quietly, because quiet sequencing would both hide the defect and invent a
service order this model does not have.

## 10. The epoch

```
 1 natural disturbance          x_t -> y_t, external deviation recorded
 2 derive P-demand from y_t
 3 economic arrivals            pure function of (seed, epoch)
 4 random compatible admission
 5 active demand set D_t
 6 demand-dependency components
 7 complete service plans
 8 can this plan actually happen now?
 9 exact EBU valuation
10 affordability
11 actor choice
12 joint closure gate
13 execution                    y_t + delta_G -> x_{t+1}
14 capacity settlement
15 P-demand re-derivation       cached representation discarded
16 audit                        exact residuals, tolerance zero
```

Steps 1–4 cannot see EBU. Step 9 cannot see capacity. Step 10 cannot change
what step 9 measured.

## 11. Starting state, and the bootstrap

A run begins at `x_0 = x*` with `B_i(0) = 0`, no P-demand and no admitted
E-demand, so no actor action occurs. **This is not voluntary abstention. There
is simply no obligation.** Then a natural disturbance, an economic arrival, or
both occur under their own independent declared processes.

No initial capacity is invented. At `B = 0` a nonnegative-EBU plan is
executable and earns capacity; a negative-EBU plan is not affordable. A first
economic demand may therefore be physically impossible, physically possible but
unaffordable, or serviceable. That is intentional: capacity is earned through
verified physical improvement.

One consequence is worth stating plainly because it shapes every trajectory:
**an economic action that moves the system away from its reference can only ever
be taken by an owner that has already earned capacity by moving it toward the
reference.** Consumption is financed by prior restoration, per owner, with no
pooling.

## 12. Randomness

Four separate counter-addressed streams: `natural_disturbance`,
`economic_arrival`, `economic_admission`, `actor_choice`. Every draw is a pure
function of its address, so no stream holds mutable state another could
advance. Aligned and hostile may use the actor stream for tie-breaking only.

Because no EBU parameter, capacity balance or policy name appears in a draw
address, two properties are structural rather than conventional, and both are
asserted: changing the actor policy cannot move the economic arrival sequence,
and neither can changing the actor seed. The rehearsal shows the identical 404
arrivals under all four policies.

## 13. Losses

Loss-aware actions never make quantity disappear. A lossy route must name the
sink that receives the difference, and every action's increment sums to exactly
zero over all coordinates.

A sink is **irreversible by declaration**: no ordinary route may deliver into
one as its destination, and none may draw from one as its source. A world that
declares either is refused at construction. A model that needs recoverable
waste must represent it as a stock with its own type, not as a sink.

A sink may be declared **inside `V`**, where the waste it accumulates is a real
deviation that EBU charges for, or **audit-only outside `V`**, where it exists
so conservation closes and nothing more. The single lossy action in the
fixtures costs `-12` with the sink inside `V` and `-10` with it outside; the
gap of `2` is exactly the sink's own potential term.

The baseline is `eta = 1`. Loss is exercised only by explicit fixtures.

## 14. External disturbance

Nature moves stock, serves no demand, is not valued, and earns nobody anything.
Only verified actor receipts change actor capacity, and the disturbance module
cannot reach a ledger. A disturbance whose source is short is **null** for that
epoch: not resampled, not clipped, not reversed, not reduced.

## 15. What this contract does not settle

- The arrival law's quantity, frequency, destination and multiplicity
  distributions. These are genuine scientific load parameters and are recorded
  as unresolved in `DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md`.
- Whether the demand-driven economy exhibits a persistent restoring tendency.
  That is the future primary dynamic test, and no registered study has run.
- Whether complete-service semantics are the right long-run contract **for
  economic demand**. Structural consequences found during implementation are
  recorded in `DEMAND_DRIVEN_MODEL_FINDINGS.md`; none of F-1 to F-6 is repaired
  here, because repairing F-1 to F-4 would be a model redesign and F-5 and F-6
  lie outside the frozen Study-1 domain. The question is **settled for physical
  demand**: F-7 withdrew complete service there and records the exhaustive
  evidence that forced it.
- Exact coupling in loss-aware and destination-capacity worlds. The structural
  reach is a sound superset there, not an exact set, and F-5 and F-6 are the
  two known over-coupling artifacts. Tightening them needs a destination-
  headroom liveness limb and sink exclusion from the reach closure. Neither is
  attempted; both are outside §16.

## 16. The frozen Study-1 domain

The first registered demand-driven study runs in a deliberately narrow
physical domain, frozen and machine-checked in `study_one` and set out in full
in `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md`: **one homogeneous scalar resource,
`x >= 0`, exact conservation, lossless transfers, no loss sinks, no
irreversible sinks, no recoverable waste, no upper destination-storage
capacities, fixed topology, finitely many declared action quantities, exact
rational arithmetic, complete ECONOMIC service only with no partial economic
service and no backlog quantity, atomic physical restoration with no queue and
no residual object, no deadlines, no topology change.** Two computational conditions join them: the plan-size
cap must be at least the usable route count, so it cannot bind; and the
complete finite plan space must fit inside the exhaustive budget, so
`SEARCH_UNRESOLVED` is impossible rather than merely unobserved.

Everything outside is **FUTURE UNSUPPORTED PHYSICS**. That is a statement
about what has been proved, not a defect and not a blocker to Study 1. The
general loss-aware framework stays open for later extension.

Three results hold inside the boundary and are claimed nowhere else.

- **Liveness (L1, L2).** A route can carry an action only if it is live — true
  in every domain, which is what keeps the reach sound. In Study 1 the
  converse also holds, so the live set is exactly the set of routes that can
  act.
- **Pruning equivalence (P).** The uncapped serviceability search over the
  live structural reach is equivalent to exhaustive enumeration of the
  complete finite plan space. No scientific search truncation exists, and a
  computational cap can never turn a serviceable demand into an impossible
  one.
- **Decomposition (D).** The component product equals the decomposition-free
  progress reference, including owner receipts.

**Independent progress is authoritative.** A part proved impossible stays
unresolved and contributes no action; every serviceable part executes one
complete plan. The scientific reference is `G_progress`, not "one plan serving
every active demand" — that narrower query lives on as `F_all_complete` and is
explicitly not runtime semantics.

**Physical eligibility and affordability are separate layers.** `G_physical`
answers only *which complete demand-serving plans can physically execute now?*
and never reads a balance or a policy. `G_affordable` is the subset whose
projected owner balances all stay non-negative — per account, never a pooled
total. EBU arms select **within** `G_affordable`; the comparator bypasses it
by design. Restricting before taking the extremum matters: a hostile actor's
globally worst plan is frequently the one it cannot pay for.

A part with physical plans but no affordable one is
`ALL_PLANS_EBU_UNAFFORDABLE` — no action, demand still pending. That is an
intended EBU outcome, and it is kept distinct from physical impossibility,
from admission scarcity and from computational failure. At the ordinary
starting state `(4, 4, 4)` with zero balances it is what every EBU arm does.

**Sampling is over plan identities.** The random actor draws uniformly over
distinct canonical complete service plan identities, never over unique
aggregate outcomes. Two different action sets are two plans even when they
produce the same post-state, increment and receipts, so `Phi: plan -> outcome`
is many-to-one and outcome probability carries plan multiplicity. In
`two_supplier_world` — four plan identities, three outcomes — the induced law
is `1/4, 1/2, 1/4`, not `1/3` each. Aligned and hostile first restrict to the
extremal-EBU plans, then tie-break uniformly over those plan identities.

**Registered failure semantics.** In a registered Study-1 job
`SEARCH_UNRESOLVED` is a computational integrity failure: the entire job is
invalid, the trajectory does not continue, the epoch is not excluded, nothing
is resampled and no seed changes. Fix the implementation and rerun the
identical job. `EconomyRun(registered=True)` refuses to start outside the
frozen domain and raises `JobInvalid` rather than recording the failure as a
result.

    STUDY-1 DOMAIN VERIFIED

is **not**

    GENERAL DEMAND-DRIVEN FRAMEWORK PROVED FOR ALL LOSS/CAPACITY/TOPOLOGY MODELS.
