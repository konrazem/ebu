# Audit correction pass — independent auditor handoff

**Read-only handoff. Self-contained.** It records what the five audited
defects were, what the corrected semantics are, and what was verified. It
authorizes nothing and claims no behavioural result.

| | |
|---|---|
| audited commit | `22fd229063dc6ecf13e6b83d6aec275042489e7b` |
| corrections commit | `3382b072cd0079a5d662b712700997b2ec54a1d6` |
| corrections tree | `9ba490cf68fbedaa2d265384a170cb6fc1c59128` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `4363727e50a11aeba09411466319cc56fa501edf504a1cb0011a4fdfcd88caa0` |
| `gaussian_harness` (pinned) | `a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c44a121d1b9c058795a9ee38b05999e2cf674e70134d18222e70221c2` — unchanged |
| `homeostasis` (pinned) | `8b462401a00ed8624fbd649e460b9e44e6adf8ba749ca1fa3872e9a6ddd4c3c6` — unchanged |
| conformance | 365 assertions, 0 failures, 113 groups, tolerance literally zero |
| all eight suites | 868 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations and reports: **0 files changed** |

This document is added by a later commit that changes no code.

---

## 1. The observed regression

At `22fd229`, in `sandwater-v1` at state `(14, 10, 6, 6, 6)`, two independent
economic orders of `q = 2` sand at `C`:

```
menu plan                              delivered to C   both reported served
g:[r:sand:0->2@2/1]                          2                 True
g:[r:sand:1->2@2/1]                          2                 True
g:[r:sand:0->2@1/1, r:sand:1->2@1/1]         2                 True
```

Two units satisfied four units of obligation. The cause was a per-demand
predicate, `completely_serves(d, increment) == increment[d.coordinate] >=
d.required_delta`, evaluated once per demand against the same increment.

After correction, the same component's menu contains only plans delivering at
least 4, and deliveries of 2 and 3 serve **neither** order:

```
requirement at C: economic_total = 4, physical_deficit = 0, required = 4
delivery 2 -> served ()
delivery 3 -> served ()
delivery 4 -> served (E:...:000, E:...:001)
```

Regression test: `test_separate_orders_are_separate_material_obligations`,
with the menu-level companion
`test_the_additive_rule_governs_the_menu_not_only_the_predicate`.

## 2. Corrected semantics

### 2.1 Additive economic obligations (`demand_driven_ebu/service.py`)

For plan `G` and destination coordinate `c`:

```
pool(G, c) = max(0, delta_G[c])
0 <= s_d(G) <= q_d          for each order d at c
sum_d s_d(G) <= pool(G, c)
d completely served  <=>  s_d(G) = q_d
```

The pool is **net, not gross**: a unit that arrives at `c` and leaves again in
the same plan is not present afterwards and serves nobody. Taking gross inflow
would reintroduce the same double-count one level down. Verified by
`test_the_pool_is_net_not_gross`.

The allocator returns full allocation when the pool suffices and a canonical
diagnostic fill when it does not. The partial fill explains a shortfall and is
never consulted by any completion predicate; `ServicePlan.__post_init__`
refuses any plan carrying an incomplete allocation, so a partial fill cannot
reach a menu.

`demand.completely_serves` and `demand.coverage` were **deleted**, not
deprecated, so no call site can reach for the defective predicate again.

### 2.2 E/P overlap (correction 2, confirmed legitimate)

A physical shortfall is a condition on the post-state, not a second economic
quantity claim. Nothing is subtracted between the two. The combined
requirement at a coordinate is a **maximum**:

```
delta_G[c] >= max( sum_d q_d , deficit_c )
```

So one two-unit delivery may fulfil a two-unit order *and* close a two-unit
deficit. Two economic orders still add to each other. Verified by
`test_physical_demand_draws_nothing_from_the_economic_pool` and hand-check D.

### 2.3 Same semantics everywhere (correction 3)

Requirements drive admission compatibility, joint serviceability
(`enumeration.has_serving_group`), plan enumeration
(`enumeration.irredundant_serving_groups`), plan validation (`ServicePlan`),
completion bookkeeping (`harness`, via `service.served_economic_ids`), the
service audit, and the saved rehearsal artifact.

## 3. Admission comparison correction (correction 4)

The previous decision-packet requirement that **admitted demand components be
identical across arms** is withdrawn. It is unsatisfiable in a closed loop:
admission reads the physical state, and prior actor behaviour leaves arms in
different states.

The registered contract is now:

> identical exogenous E-demand arrival streams across arms, with endogenous
> admission.

Admission remains EBU-blind — an AST check asserts the module names no EBU,
capacity or valuation symbol. Differences in admission are legitimate
closed-loop outcomes.

Every incoming demand carries a lifecycle state, tracked in
`EconomyRun.arrival_ledger`: `ARRIVED`, `ADMITTED`,
`REJECTED_PHYSICAL_SCARCITY`, `REJECTED_INCOMPATIBLE`, `SERVED`,
`ADMITTED_BUT_UNRESOLVED_PHYSICAL`, `ADMITTED_BUT_EBU_UNAFFORDABLE`.

**The admitted-only service rate is never the primary whole-system
comparison** — an arm that admits little and serves all of it would score
perfectly. `test_admitted_only_service_rate_is_not_the_whole_system_measure`
computes both rates and shows they differ.

### 3.1 Sampling measure (correction 5)

Random compatible-subset admission is retained as the only economic allocation
policy. No FIFO, pricing, utility, social priority, EBU ranking or scheduling
was added.

The measure is uniform over inclusion-maximal admissible **subsets**, which is
**not** uniform over demands. With `k` pairwise-incompatible arrivals each is
admitted with probability `1/k`; a request compatible with everything appears
in every maximal subset and is admitted with probability `1`. Both limbs are
exercised by `test_uniform_over_subsets_is_not_uniform_over_demands`. A study
reporting admission rates must report the induced per-demand marginals.

## 4. Coupling invariant (correction 6)

> **Demand decomposition is an implementation factorization, not a restriction
> on the global feasible service set.**

Coupling is decided from actual binding constraints, computed from the plans
that individually serve each demand (`coupling.service_reach`): shared
service-delivery pool, competing stock, shared route, shared potential-bearing
coordinate, shared owner account. Membership of a transport-connected
component is no longer sufficient.

A demand with no individually-serving plan has an empty reach and couples with
nothing — sound, because a joint plan has *fewer* actions available for it
under the same plan-size cap, so it can compete for nothing.

**Before and after**, `sandwater-v1` at `(8, 12, 10, 6, 6)` with an
unserviceable 25-unit order:

| order placed at | components | menu sizes |
|---|---|---|
| `C` (different coordinate) | `c:[E:…sand|C]`, `c:[P:sand|A]` | 0, **5** |
| `A` (shared pool with the shortfall) | `c:[E:…sand|A, P:sand|A]` | 0 |
| `A`, order of 3 instead of 25 | `c:[E:…sand|A, P:sand|A]` | 5 |

At `22fd229` the first row was a single component with menu size 0: the
serviceable shortfall was frozen by a demand it could not compete with.

**Remaining freezing is classified.** Row two still freezes both demands. That
is the **declared complete-service and allocation restriction**, not physical
scarcity — the stock to close the two-unit shortfall exists and is reachable;
what forbids using it is the refusal of partial service. Recorded as finding
F-1 in `DEMAND_DRIVEN_MODEL_FINDINGS.md`, which was rewritten because its
stronger form was partly the coupling artifact.

Three proofs are in the gate:

- `test_impossible_sand_cannot_freeze_independent_water` — the impossible sand
  component is reported unserviceable while the water component executes in the
  same epoch and the water shortfall is actually closed.
- `test_decomposition_does_not_restrict_the_global_feasible_set` — the menu of
  a deliberately over-coupled merged component equals, exactly, the product of
  the component menus restricted to the plan-size cap.
- `test_an_unserviceable_demand_freezes_nothing` — the serviceable demand keeps
  all five plans.

**One qualification, stated rather than hidden.** The plan-size cap is declared
**per component plan**. With a binding cap the decomposed form admits strictly
more total actions than a merged evaluation would (10 combinations versus 8 in
the test world). Decomposition therefore never restricts the feasible set; it
is the merged view that would. The equivalence above is asserted in the form
that is actually true.

**Enumeration stays generous.** The narrow reach decides coupling only; menus
are built over every route touching the component's transport closure
(`enumeration.search_routes`), so over-coupling cannot delete a valid plan.

## 5. Cycle provenance (correction 7)

`cycles.actor_only` reads `EpochRecord.external_events` — identities recorded
whenever nature actually moved stock — and nothing else. It never infers
actor-only status from `sum dV_ext == 0`. An economic arrival is not an
external physical event.

Three fixtures:

| fixture | `sum dV_ext` | state returned | external events | verdict |
|---|---|---|---|---|
| two cancelling events, routeless world | `0` | yes | 2 | **not** actor-only |
| permutation at constant `V` | `0` | n/a | 1 | **not** actor-only |
| genuine actor-only window, arrivals inside | `0` | yes | 0 | actor-only, `delta B_total = 0` |

The first row is exactly the configuration the superseded test would have
certified as a closed actor-only cycle: state returned, potential term zero,
no loss. The routeless world is used so the actor cannot act and nothing
confounds the window. `test_actor_only_is_not_inferred_from_the_potential_term`
asserts by AST that the classifier reads `external_events` and none of
`external_deviation`, `external_total`, `potential_after`.

The no-issuance theorem itself is unchanged and preserved.

## 6. Sink validation (correction 8)

A sink is irreversible by declaration. `DemandWorld` refuses, at construction,
any route whose **source** is a sink (as it already refused any whose
destination is one). A model needing recoverable waste must declare a stock
with its own type, not a sink. Verified for both sink kinds by
`test_a_route_out_of_a_sink_is_refused_at_construction`, and
`test_no_declared_world_exports_from_a_sink` sweeps every fixture world.

## 7. Capacity theorem re-check (correction 9)

Re-run against the corrected service semantics, with up to three simultaneous
economic orders per epoch, 30 epochs, all four arms:

| quantity | result |
|---|---|
| `delta B_total - [V(x_0) - V(x_T) + sum dV_ext]` | `0` exactly, every arm |
| window telescoping residual | `0` |
| duplicate action receipts within an epoch | none |
| `sum_a R_a - E_G` | `0` exactly |
| economic demands served more than once | none |
| capacity created by an arrival (two orders, same destination) | `0`; state untouched |

## 8. Admission hand-checks (correction 10)

| case | setup | result |
|---|---|---|
| A | two `q = 700` orders, 1000 available | each serviceable alone; **not** jointly admitted; second rejected `E_REJECTED_INCOMPATIBLE` |
| B | two `q = 500` orders, 1000 available | both admitted, jointly serviceable |
| C | `q = 1000`, 560 available | rejected `E_REJECTED_PHYSICAL_SCARCITY`, before EBU, quantity not truncated |
| D | `q = 2` order plus `q = 2` deficit at one destination, 2 delivered | order served **and** shortfall resolved by the same two units |

## 9. Rehearsal (correction 11)

`demand_driven_rehearsal.py`, 200 epochs × 4 replicates × 4 policies = 3,200
epochs. **NON-CONFIRMATORY. Not evidence.** No behavioural reading is offered
and none is permitted.

| audit check | result |
|---|---|
| E/E double service events | **0** |
| economic demands served more than once | **0** |
| executed actions without demand provenance | **0** |
| raw arrival sequences identical across arms | **True** (404 each) |
| admitted counts by arm | 280 / 114 / 111 / 167 — differ, as endogenous admission requires |
| epochs with an unserviceable component beside an executing one | 959 — the coupling correction working; all 959 would have frozen at `22fd229` |
| accounting / conservation / nonnegativity / separability / capacity-source residuals | all exactly `0` |
| replay determinism | exact, code identity stable across run and replay |

Arrival lifecycle over the common raw set (1,616 = 4 arms × 404):
`REJECTED_PHYSICAL_SCARCITY` 938, `SERVED` 627,
`ADMITTED_BUT_UNRESOLVED_PHYSICAL` 38,
`ADMITTED_BUT_EBU_UNAFFORDABLE` 7, `REJECTED_INCOMPATIBLE` 6.

Scarcity rejections rose sharply against the defective build. That is the
additive rule biting, not a change in the world.

The `22fd229` rehearsal artifact was **replaced**, not amended: that build
mis-counted additive service, so no number from it is citable.

## 10. Verification summary

| suite | assertions | failures |
|---|---|---|
| Local Gaussian foundation | 65 | 0 |
| Local Gaussian harness | 68 | 0 |
| Capacity-V2 foundation | 61 | 0 |
| Capacity-V2 harness | 28 | 0 |
| Homeostasis foundation | 146 | 0 |
| Homeostasis transition | 109 | 0 |
| Restoring tendency | 26 | 0 |
| **Demand-driven conformance** | **365** | **0** |
| total | **868** | **0** |

All arithmetic exact rational, tolerance literally zero.

## 11. Scientific readiness (correction 12)

> ## READY FOR PREREGISTRATION DESIGN

The five audited defects are corrected, each with a regression test, and the
whole gate passes. What this verdict **does** mean: the model's semantics are
now consistent across admission, enumeration, validation, completion, audit
and artifacts, and the machinery is sound enough to design a registered study
against.

What it does **not** mean, and must not be read as: it is not permission to
run one. The long-run arrival law and the restoring-tendency endpoint remain
**unfrozen** by explicit instruction. The endpoint-saturation hypothesis does
not apply to the corrected model, so the aligned arm is not trivially perfect;
that fact does not by itself rule `O95` in or out, and endpoint suitability
must be chosen from the scientific question before registered execution. The
gates in `DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md` §3 and §5 are still
open, and no registered behavioural experiment was run.

**Superseded in part.** A second independent audit found that coupling was
still derived from padded serving plans, so physically unusable routes could
change serviceability. See `DEMAND_DRIVEN_AUDITOR_2_HANDOFF.md`.

## 12. Files an auditor should read

| file | role |
|---|---|
| `demand_driven_ebu/service.py` | additive allocation; the correction's core |
| `demand_driven_ebu/enumeration.py` | shared plan primitives; narrow reach vs generous search |
| `demand_driven_ebu/coupling.py` | binding-constraint coupling and the invariant |
| `demand_driven_ebu/cycles.py` | `actor_only` provenance classifier |
| `demand_driven_ebu/world.py` | sink irreversibility validation |
| `demand_driven_ebu/harness.py` | arrival ledger, external-event provenance, set-level service |
| `test_demand_driven_ebu.py` | the gate; audit section begins at "AUDIT CORRECTION PASS" |
| `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` | corrected semantics, with a correction log |
| `DEMAND_DRIVEN_MODEL_FINDINGS.md` | F-1 rewritten; F-2 to F-4 unchanged |
