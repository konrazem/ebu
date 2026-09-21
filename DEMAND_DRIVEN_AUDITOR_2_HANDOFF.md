# Final demand-coupling correction — auditor 2 handoff

**Read-only, self-contained.** Records the counterexample, the corrected rule
and its proof, the plan-cap disposition, the decomposition oracle, and every
test identity. Authorizes nothing. No registered experiment was run.

| | |
|---|---|
| audited commit | `e37e8683d2d220a40bf6665c51cbc14be140d1f7` |
| correction commit | `48b2f67aed2340a3fdd905339f712c9caf05248e` |
| correction tree | `60127801e60e9771a1b5c88ba86c275c563b8944` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `9147a06b38fde3e55f3bf2e07c41ead4a2adc161aa27293b27da54c6471d17d0` |
| `gaussian_harness` (pinned) | `a9158eef…fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c…21c2` — unchanged |
| `homeostasis` (pinned) | `8b462401…c3c6` — unchanged |
| demand-driven conformance | 414 assertions, 0 failures, 128 groups |
| all eight suites | 917 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations and reports: **0 files changed** |

This handoff document is added by a later commit that changes no code.

Scope: only the coupling defect. The four resolved issues — additive economic
service, endogenous admission, cycle provenance, sink validation — were not
reopened, and their tests still pass unchanged.

---

## 1. The counterexample, reproduced before correction

Three independent one-unit deliveries `A→B`, `C→D`, `E→F`. Each source holds
one unit, each destination is one unit short, each delivery has a distinct
owner. Plan cap 2. Then two connecting routes of capacity `1/2` are added,
while the only permitted action quantity is `1`, so they can carry no action.

Measured at `e37e868` — pure calculation on a fixed state, no transition:

| configuration | executable actions | components | menus |
|---|---|---|---|
| three disconnected pairs | 3 | 3 | `[1, 1, 1]` |
| plus two unusable routes | **3** (identical) | **1** | **`[0]`** |

The reach of `P:r|B` became `coords {0..5}, owners {A, C, E}`. Two routes that
can carry nothing had destroyed all service.

**Mechanism.** `coupling.service_reach` called `enumeration.serving_groups`,
which does not apply irredundancy. For the demand at `B`, the padded plan
`{A→B 1, C→D 1}` completely serves `B` and is executable, so `C`, `D` and
owner `C` entered `B`'s reach. The unusable routes were what widened
`search_routes` — which is transport-closure based — far enough for such
padded plans to be enumerated at all. Three demands then merged into one
component needing three actions against a cap of two.

## 2. Frozen invariants

**Unusable-infrastructure invariance.** If a world modification changes
neither the set of physically executable actions nor any genuine binding
physical or account constraint, it must not change demand coupling,
complete-service possibilities, or admission. Adding or removing a route that
cannot carry any allowed action quantity must be behaviorally invisible.

**Decomposition invariance.** Demand decomposition is an implementation
factorization, not a restriction on the global feasible service set.

## 3. The corrected rule, and why it is sound

Coupling is derived from the **structural reach**
(`enumeration.structural_reach`): the tokens any *minimal* plan serving a
requirement could bind, computed from the world rather than from enumerated
plans. Neither raw transport connectivity nor serving plans are used.

**Soundness.** Let `G` be irredundant, executable, serving requirement set
`R`, and take `a ∈ G`. Irredundancy says `G \ {a}` fails to serve `R` or
cannot execute.

*Fails to serve:* some `c ∈ R` has `Δ_{G\a}[c] < req(c) ≤ Δ_G[c]`, so `a`
raises the increment at `c` — `a` **delivers into a requirement coordinate**,
as destination or as loss sink.

*Cannot execute:* the broken condition can only be a declared stock capacity
at `a`'s source. Quantum and route-capacity checks are per action and
unaffected by removal. Source-funding only relaxes when an outflow is removed.
Endpoint nonnegativity cannot break, because source-funding on `G` gives
`state[i] + Δ_S[i] ≥ state[i] − outflow_G[i] ≥ 0` for every subset `S`.
Removing `a` removes an outflow from its source, pushing that coordinate up
only.

So every action of every minimal plan either delivers into a requirement
coordinate or drains a capacity-bearing coordinate that receives inflow inside
the plan. `structural_reach` closes over exactly those two cases, making it a
sound **superset** of every minimal plan's support — it cannot under-couple —
while remaining free of the cap, free of padding, and blind to routes carrying
no action. With no declared stock capacities the second case is empty and the
computation is one pass.

**Coupling channels retained.** Shared service-delivery pool (same
destination, additive economic quantities); competing stock; shared executable
route and its capacity; shared hard physical constraint or potential-bearing
coordinate; one executable action serving several demands; shared owner
account. The last is required rather than conservative: joint affordability is
checked jointly at execution, so decoupling such demands would let the joint
gate discover a conflict it should have prevented.

**Unserviceable demands.** A demand with no physically realizable service
possibility binds nothing, and is coupled only to demands at its own
destination. Sound: if no plan serves it alone, none serves it jointly, since
the actions raising its increment come from the same structural reach and a
joint plan has no more of them available under the same limit. Its coordinate
set is empty, so a serviceable neighbour drawing supply from its destination
is not dragged in — that neighbour's plan can only leave an already-impossible
demand no more impossible.

**Genuine joint interactions are preserved**, not lost — see tests C, E, F in
§6, which are exactly the cases where a naive "drop redundant plans" fix would
have under-coupled.

## 4. Plan-size cap — disposition A

Full reasoning in `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`. Settled from
existing authority; no user decision required.

**A: a computational enumeration limit, not a physical simultaneity
constraint.** Three concurring sources:

1. `gaussian_harness/candidates.py`: "A finite menu is an experimental
   restriction, not a claim that every physically divisible quantity has been
   enumerated."
2. `max_group_size` is a field of `MenuSpecification`. The registered code
   keeps a separate `PhysicalRules` — "Declared hard physical bounds and
   topology" — and the cap was not put there.
3. `LOCAL_GAUSSIAN_EBU_STAGE_A_DECISION_PACKET.md` §C: "`m_max` is
   configuration, defaulting to 2 for the Stage-A fixture."

No source asserts a physical simultaneity limit.

Consequences implemented, none silently preserving the old semantics:

| consequence | where |
|---|---|
| coupling never reads the cap | `structural_reach` contains no reference to it; asserted by AST |
| an empty menu is not evidence of impossibility | `plans.serviceability` → `SERVICEABLE_WITHIN_CAP` / `SEARCH_INCOMPLETE_AT_PLAN_CAP` / `PHYSICALLY_IMPOSSIBLE` / `SEARCH_BUDGET_EXCEEDED` |
| the uncapped test is exact | minimal plans use only structural-reach routes, at most one action per route, so per-route choice over that set is a complete search |
| it fails closed | over its declared budget it returns `SEARCH_BUDGET_EXCEEDED` rather than a negative it did not establish |
| admission asks the physical question | `admission` calls `physically_serviceable`, not the capped test; asserted by AST |

Declared and **not** hidden: under A the cap bounds enumeration per plan, so a
decomposed epoch may execute more total actions than any single plan contains.
That asymmetry is held constant on both sides of the oracle so it cannot
contaminate the comparison, and is tested separately.

If a later study wants B, it must declare the limit as physics, apply it to
the combined executed set at the joint gate, and accept that it couples
demands. That is a model change needing its own authorization.

## 5. Decomposition oracle

`demand_driven_ebu/oracle.py` enumerates, over the whole world at once and
without forming any component, every executable irredundant plan completely
serving every demand, and returns canonical physical increments. The component
path runs beside it. Increments are compared, not plan orderings.

Both sides take the same explicit action bound, which removes the per-component
cap asymmetry from the comparison.

Verified on six world/state cases at bounds 2 and 3 — including the
counterexample world with and without the unusable routes — plus a mixed
economic/physical demand set. **All agree exactly.** Sizes ranged 4–18
outcomes per case.

## 6. Metamorphic results

| test | result |
|---|---|
| **A** add unusable routes | action set unchanged; coupling unchanged; serviceability unchanged; components stay `[1,1,1]` |
| **B** remove them | exact inverse; identical shape |
| **C** add usable `A→D` with binding capacity | `B` and `D` couple; the shared supplier coordinate is shown; `A` holds one unit and the joint plan `{A→B 1, A→D 1}` is shown non-executable; `F` stays independent |
| **D** add an irrelevant executable action serving no demand | coupling unchanged; serviceability unchanged |
| **E** one action serves an order and a shortfall at one coordinate | coupled; single-action plan exists; provenance names both |
| **F** two demands fed only from one one-unit stock | coupled; jointly unserviceable; classified `PHYSICALLY_IMPOSSIBLE` |
| **G** independent components | global and component feasible sets identical |
| **H** starved delivery beside two healthy ones | starved one `PHYSICALLY_IMPOSSIBLE`; other two keep their plans; nothing merged |

Additional: coupling identical at plan caps 1, 2 and 3; the cap reports
`SEARCH_INCOMPLETE_AT_PLAN_CAP` for a three-action requirement under a cap of
two, and raising the cap finds the plan; genuine impossibility still reports
`NO_COMPLETE_PHYSICAL_PLAN`; admission admits a beyond-cap-serviceable order
and then reports the search limit; no unusable route enters any reach.

## 7. Rehearsal

3,200 epochs, four policies, four replicates. **NON-CONFIRMATORY. Not
evidence.** Replays exactly; code identity stable; accounting, conservation,
nonnegativity, separability and capacity-source residuals all exactly zero.

| check | result |
|---|---|
| E/E double service events | 0 |
| economic demands served more than once | 0 |
| executed actions without demand provenance | 0 |
| raw arrival sequences identical across arms | True (404 each) |
| admitted counts by arm | 283 / 64 / 97 / 121 — endogenous, as required |
| epochs with an unserviceable component beside an executing one | 1040 |
| `SEARCH_INCOMPLETE_AT_PLAN_CAP` epochs by arm | 29 / 99 / 71 / 105 |
| `SEARCH_BUDGET_EXCEEDED` epochs | 0 |
| status coverage | all 800 epochs per arm accounted for; a warning fires otherwise |

The search-incomplete counts are the disposition working: those epochs were
previously reported as physical impossibility and are now correctly attributed
to the enumeration limit. A study freezing this world should raise the cap
until they are negligible, which is a methodological adjustment, not outcome
tuning.

Artifacts from `22fd229` and `e37e868` were replaced, not amended. No number
from either is citable.

## 8. Prohibited mutations — none performed

| prohibition | status |
|---|---|
| reopen resolved service/admission/provenance/sink work | not reopened; their tests unchanged and passing |
| modify a historical pinned artifact | 0 files changed under `gaussian_harness`, `capacity_v2`, `homeostasis`, `books`, `results/stage_a`, `results/stage_b`, `results/homeostasis`, and all preregistrations and registered reports |
| redesign EBU, Gaussian valuation or Capacity V1 | untouched |
| run a registered experiment | none run |
| choose the new primary endpoint | not chosen |
| broaden scope | limited to coupling, the cap disposition, the oracle, and the two wording corrections requested |

## 9. Wording corrections requested by the auditor

- The stale claim that over-coupling "only costs parallelism" is removed from
  `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` §6. The earlier correction pass
  had failed to apply this replacement; §6 is now rewritten in full and states
  that incorrect coupling can alter serviceability wherever complete-service,
  search-size, simultaneity or other joint constraints exist, and is therefore
  scientifically material.
- The stale inference that failure of the endpoint-saturation hypothesis makes
  `O95` unsuitable is corrected in the decision packet and in the auditor 1
  handoff. The hypothesis does not apply to the corrected model, so the
  aligned arm is not trivially perfect; endpoint suitability must be chosen
  from the scientific question before registered execution, and is not chosen
  here.

## 10. Readiness

> ## READY FOR PREREGISTRATION DESIGN

Against the five conditions:

| condition | status |
|---|---|
| auditor counterexample fixed | **yes** — permanent regression, both configurations identical |
| unusable-infrastructure invariance passes | **yes** — tests A, B, and the reach construction |
| global and component feasible sets agree in exhaustive fixtures | **yes** — six cases at two bounds, plus a mixed demand set |
| plan-size-cap semantics scientifically resolved | **yes** — A, from three concurring authority sources, with consequences implemented |
| no historical pinned artifact modified | **yes** — 0 changed |

Not permission to execute. The arrival law and the primary endpoint remain
unfrozen, and the open gates in
`DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md` §3 and §5 still stand.

## 11. Requested auditor disposition

1. Confirm the structural-reach soundness argument in §3, in particular the
   claim that endpoint nonnegativity cannot break under action removal, since
   the whole superset argument rests on it.
2. Confirm that disposition A is the correct reading of the three authority
   sources, and that admitting beyond-cap-serviceable demands is the right
   consequence rather than an avoidable stall.
3. Confirm the oracle's comparison basis — canonical increments at a shared
   bound — is the right equality to require.
4. Confirm that decoupling an unserviceable demand from a neighbour that draws
   supply from its destination is sound, since that asymmetry is the one place
   where the reach is deliberately not symmetric.
5. Note for the record whether the `SEARCH_INCOMPLETE_AT_PLAN_CAP` rate in the
   rehearsal should block preregistration design or merely inform the cap
   chosen for the registered world.

## 12. Files to read

| file | role |
|---|---|
| `demand_driven_ebu/enumeration.py` | structural reach, its soundness proof, uncapped serviceability |
| `demand_driven_ebu/coupling.py` | the invariants and the coupling rule |
| `demand_driven_ebu/oracle.py` | decomposition-free global feasible set |
| `demand_driven_ebu/plans.py` | `serviceability` four-way classification |
| `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` | the cap, settled from authority |
| `test_demand_driven_ebu.py` | audit section begins at "FINAL DEMAND-COUPLING CORRECTION" |
| `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` §6 | corrected coupling wording |
