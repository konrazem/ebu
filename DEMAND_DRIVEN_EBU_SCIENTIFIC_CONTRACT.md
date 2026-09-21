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
condition on the post-state, `x_c + delta_G[c] >= x*_c`. It draws nothing from
the economic pool, and nothing is subtracted between the two: the same two
delivered units may fulfil a two-unit order *and* close a two-unit deficit,
because both conditions ask for the same units to be present afterwards. So
the combined requirement at a coordinate is a **maximum**, not a sum:

```
delta_G[c]  >=  max( sum_d q_d ,  deficit_c )
```

Four consequences are deliberate.

1. **No double credit is possible.** Economic service is measured against a
   single shared pool per coordinate, so no delivered unit can be claimed by
   two orders; and the pool itself is a property of the plan's net increment,
   so there is no per-action credit ledger in which anything could be counted
   twice.
2. **E/P overlap stays legitimate.** The two claims are different kinds of
   statement and are never netted against each other.
3. **No partial service.** Backlog, fractional fulfilment, deadlines and
   service quality do not exist. If complete service is impossible the demand
   — and its component — remains unresolved. The allocator can report a
   partial fill, but only as a diagnostic that explains a shortfall; no
   completion predicate consults it.
4. **Overshoot is permitted.** Delivering more than required still delivers
   the requirement. This is what leaves a hostile actor a real choice: it may
   answer the obligation destructively. Forbidding overshoot would collapse
   the hostile policy into one that cannot act.

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

Two demands are connected when serving them could share or compete for the same
physical stock, the same source, the same route, the same hard capacity, the
same physical constraint, or **the same actor account**. Connected components
are the units resolved jointly.

Accounts are held by **nodes**, not coordinates, so account sharing is a real
coupling channel: a sand demand and a water demand both payable by node `A` are
coupled through joint affordability even though no stock and no route is
shared. Per-coordinate wallets would have removed that channel silently.

Footprints are computed conservatively, as everything any plan serving the
demand could possibly touch. Over-coupling costs parallelism; under-coupling
costs correctness. One impossible sand demand must not block an unrelated
water restoration, and it does not.

## 7. Service plans, and demand provenance

A plan enters a menu only if it is **complete**, **can happen now**, and is
**irredundant** — no proper subset of it already serves the whole component
while itself being executable.

Irredundancy is the structural guard against recreating the old environment.
If an action could be dropped and the component would still be served, the plan
containing it is not in the menu, so an unrelated transfer cannot be bolted onto
a legitimate plan. Conversely, in an irredundant plan every action is necessary
for something: for each `a` there is a demand that `G \ {a}` fails, or `G \ {a}`
cannot execute at all. That set is the action's **provenance**, it is non-empty
by construction, and it may be many-to-many.

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
- Whether complete-service semantics are the right long-run contract. Two
  structural consequences found during implementation are recorded in
  `DEMAND_DRIVEN_MODEL_FINDINGS.md`; neither is repaired here, because
  repairing them would be a model redesign.
