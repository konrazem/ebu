# Auditor handoff — atomic P-demand implementation and the Stage-A freeze

**Self-contained.** Everything needed to check this pass is named below. No
prior conversation is required, and nothing here depends on one.

**Nothing was committed.** `AGENTS.md` permits commits only when explicitly
authorized, and no authorization was given. The working tree carries the change
set listed in §7.

**No Stage A ran.** No Stage-A epoch, trajectory, arm outcome or aggregate was
generated. The only thing executed against the Stage-A fixtures was object
*construction*, which sets an opening state and a zero ledger and advances
nothing.

---

## 1. What was changed, in one paragraph

The requirement at a coordinate was `max(sum_d q_d, deficit_c)` — one threshold
carrying both the economic and the physical claim. That collapse applied the
**economic** completion contract to a **physical** condition. It is withdrawn.
Economic service is unchanged: complete, additive across separate orders, no
partial fulfilment and no backlog. Physical service is now **atomic**: a plan
serves a physical demand exactly when it makes genuine positive progress on the
represented deficit, attribution is capped at that deficit, overshoot stays
permitted, and the remainder is re-derived from the post-state because the
physical state is the only record there has ever been. Irredundancy is
untouched, so no unrelated transfer became legal. Recorded as finding **F-7**.

---

## 2. The evidence that forced it

Exhaustive static enumeration of the frozen `study-one-v1` graph: all 91
integer states, edges from the decomposition-free progress reference. No policy,
no trajectory, no RNG.

| | withdrawn rule | implemented rule |
|---|---|---|
| absorbing physical states | 37 (**36** away from equilibrium) | **1 — `x*` alone** |
| `x*` reachable at all | 31 / 91 | **91 / 91** |
| `x*` reachable by burden-nonincreasing paths | 31 / 91 | **91 / 91** |
| `x*` reachable by strict descent alone | 23 / 91 | 83 / 91 |
| longest burden-nonincreasing distance to `x*` | — | **5** |
| plateau-locked states | 4 | **2** — `(3,4,5)`, `(5,4,3)` |
| successor edges | 99 (80 down, 13 neutral, 6 up) | 226 |

**None of the 36 was resource scarcity.** `sum_i x_i = 12 = sum_i x*_i` at every
state. 28 came from a deficit exceeding what one plan could deliver into its
coordinate (`A` and `C` have one inbound route each, largest quantum 2); 8 were
joint complete-service conflicts where each deficit was serviceable alone and
the pair was not.

### Three independent reasons the old rule was a semantic error

1. **The ontology never asked for it.** Contract §2.1 declares P-demand
   state-derived, with no cache and no queue. The residual of a partial
   restoration is already recorded — in the state.
2. **It was not refinement-consistent.** At `(2,6,4)` the plan `{B->A@2}` was
   legal and its physically valid half `{B->A@1}` was not, so splitting a legal
   restoration into legal sub-restorations destroyed its provenance. That
   contradicts the project's own atomic-action principle.
3. **It was the economic contract applied to a physical condition.** An order
   has an identity and a lifecycle, so its residual would need a backlog
   quantity against that id. A deficit has neither.

---

## 3. Where to look, and what to check

| claim | check it here |
|---|---|
| the predicate itself | `demand_driven_ebu/service.py` — `CoordinateRequirement.serves_economic` / `serves_physical` / `physical_progress` / `physical_remainder`, and `serves_all`. **`required_delta` no longer exists**; a conformance check asserts its absence |
| attribution record | `service.PhysicalService`, built by `physical_services`, carried on `plans.ServicePlan.restoration`. Its `__post_init__` refuses progress above the represented deficit and requires `progress + remainder == deficit` |
| no completeness check on restoration | `plans.ServicePlan.__post_init__` — economic allocations must be complete, restoration records must merely carry positive progress. The asymmetry is commented in place |
| provenance stays local | `test_demand_driven_ebu.py::test_incremental_restoration_buys_no_unrelated_provenance` — `(5,4,3)` |
| refinement consistency | `::test_p_restoration_is_refinement_consistent` — `(2,6,4)` |
| incremental restoration | `::test_atomic_p_service_is_progress_not_completion` — `(0,6,6)` |
| residual re-derived, no new object | `::test_p_residual_is_re_derived_from_the_state` — a **symbol** check over module namespaces and dataclass fields, not a prose check |
| overshoot unchanged | `::test_overshoot_stays_permitted_and_lands_in_the_state` |
| the two contracts stay apart | `::test_the_two_completion_contracts_stay_separate` |
| accessibility oracle | `::test_study_one_is_wholly_accessible_under_atomic_p_service` |
| accessibility is not affordability or policy | `::test_accessibility_is_not_affordability_and_not_policy` |
| the withdrawn rule's enumeration, reproduced | `dynamic_ebu_theory_checks.py::section_study_one`, `S1-01`..`S1-25`. The package no longer implements complete P-service, so the historical rule is reimplemented there from first principles rather than deleted |
| implementation matches the analysis | `S1-24`: the package's successor map equals the module's independent atomic enumeration on **all 91 states**, and differs from the withdrawn one |

---

## 4. The five conformance witnesses that had to move, and why

Each existed to demonstrate a property that is still true; each needed a new
witness because its old one depended on the withdrawn rule. **No property was
weakened and none was deleted.** Please check these five hardest.

| test | old witness | new witness | why it had to move |
|---|---|---|---|
| `test_already_stuck_demands_do_not_freeze_admission` | `sandwater` at `(3,10,10,4,8)`: a seven-unit shortfall at `sand\|A` no single plan could close | `(3,0,0,4,8)`: **both** sources that can reach `sand\|A` are empty, so no route into it is live | a deep shortfall is no longer unserviceable; emptiness of its sources is physical and survives any completion contract |
| `test_an_impossible_component_does_not_block_an_independent_one` | same | same | same |
| `test_impossible_sand_cannot_freeze_independent_water` | same | same | same |
| `test_the_three_legitimate_inactions_are_distinguished` | `(3,10,10,6,6)` | `(10,10,10,0,0)`: both water coordinates empty | `NO_COMPLETE_PHYSICAL_PLAN` is now reached the only way it should ever have been — the resource is not there |
| `test_the_cap_never_reports_physical_impossibility` | a three-unit **physical** shortfall against a cap of two | the same requirement carried by an **economic order** | complete service is now the economic contract, so it is an economic requirement that can need more actions than a cap allows |
| `test_search_uncertainty_never_becomes_impossibility` | three **physical** requirements on `wide_supply_world` | the same three as **economic orders** | all three verdicts still reproduce exactly: `SERVICEABLE`, `IMPOSSIBLE`, `SEARCH_BUDGET_EXCEEDED` |
| `_study_one_blocked_case` (7 dependent tests) | `(0,6,6)`: blocked P at `A`, live E at `C` | `(0,0,12)`: blocked P at `A` because `B` is empty, live component at `B` holding both its shortfall and an economic order | the pairing the tests need — one proved-impossible part beside one that must still act — is preserved exactly |
| `test_blocked_and_unresolved_are_still_different_things` | an undecided **physical** search under a budget of 1 | an undecided **economic** search | a physical claim is settled by the first plan that delivers anything, so it can no longer exhaust a budget. The blocked case now asserts something stronger: its reach carries **no route at all** |
| `test_policies_choose_among_equally_complete_answers`, `fixture_f14_f15_f16` | menu of 5, affordable 4 | menu of 6, affordable 5 | the two single-unit deliveries became legitimate; the two-action plan built from them became redundant and dropped out |
| `test_decomposition_does_not_restrict_the_global_feasible_set` | `max_plan_size=2` | `max_plan_size=1` | under atomic service each component needs one action, so a cap of two no longer binds and could not exhibit the binding case |

---

## 5. Three things an auditor should try hardest to break

1. **That irredundancy really still bites.** The claim is that incremental
   restoration bought *no* new provenance. The sharpest probe is `(5,4,3)`: the
   strictly burden-decreasing plan `{A->B@1, B->C@1}` exists, is executable, and
   lands on `x*` — and must still be **refused**, because dropping `A->B@1`
   leaves a plan that still serves `C`. If that plan ever enters a menu, the
   guard is gone.
2. **That the E contract is genuinely untouched.** `ServicePlan.__post_init__`
   still refuses an incomplete economic allocation; `served_economic_ids` is
   unchanged; two orders of two units at one coordinate still require four
   delivered units. A plan serving only the physical claim at a coordinate that
   also carries an unserved order must not mark that order served.
3. **That the accessibility result is not overstated anywhere.** It is a
   physical / demand-menu statement. Search the change set for any sentence
   that turns it into a claim about affordability, policy behaviour or recovery
   probability. `test_accessibility_is_not_affordability_and_not_policy` and
   the preregistration §0 are where the boundary is asserted; the synthesis
   §9's L / R / P separation is where it is named.

---

## 6. The one declared decision that needs a reviewer's eye

`fixtures.ScriptedArrivals` carried the sentence *"No study may use it."* Stage-A
episode class **A3** needs one economic order at one declared epoch and none at
any other, which the declared stochastic `ArrivalProcess` cannot express: it
fires per epoch with a fixed probability and has no epoch window.

The prohibition's own stated rationale is that *"the registered arrival law is a
declared stochastic process whose parameters are still unresolved"* — which is a
statement about the **registered behavioural comparison**, Stage B. Stage A is a
mechanism demonstration carrying no hypothesis and making no comparison.

So the scope statement was made precise rather than removed: registered
behavioural comparisons still may not use it; a Stage-A isolated mechanism
episode may, and the preregistration declares the schedule epoch by epoch. **No
behaviour changed — this is a docstring and a declaration.** If a reviewer
judges Stage A may not use a deterministic schedule, A3 must instead wait for an
epoch-windowed arrival process, which would be a package change outside this
pass's authorization. A1 and A2 are unaffected: both run on declared
`DisturbanceProcess` / `ArrivalProcess` objects with no scripted fixture at all.

---

## 7. Change set and verification

### Files changed

| file | change |
|---|---|
| `demand_driven_ebu/service.py` | the predicate split; `required_delta` removed; `PhysicalService` and `physical_services` added; module contract rewritten |
| `demand_driven_ebu/plans.py` | `ServicePlan.restoration`; the deliberate absence of a completeness check on it |
| `demand_driven_ebu/study_one.py` | domain declaration: complete **economic** service only, atomic physical service; `FUTURE_UNSUPPORTED_PHYSICS` entries narrowed to "partial economic service" and "economic backlog quantity" |
| `demand_driven_ebu/fixtures.py` | `ScriptedArrivals` scope statement made precise (§6) |
| `test_demand_driven_ebu.py` | 8 new regression groups; 11 witnesses relocated (§4) |
| `DEMAND_DRIVEN_MODEL_FINDINGS.md` | finding **F-7**, with the full withdrawn-rule enumeration retained |
| `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` | correction-log row 12; §2.1 atomic P-service; §3 the two predicates; §15, §16 |
| `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` | conditions 13 / 13a / 14; §2 unsupported-physics list |
| `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` | accessibility structure restated against the implemented rule |
| `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` | **new**, frozen |
| `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md` | status and cross-reference wording only; no theorem changed |
| `dynamic_ebu_theory_checks.py` | withdrawn rule reimplemented locally; `S1-24`/`S1-25` cross-check the implementation |

**Not touched:** `gaussian_harness`, `capacity_v2`, `homeostasis` (all three code
identities asserted unchanged by the conformance suite), `books/`, and every
committed result artifact and manifest.

### Verification run

| suite | result |
|---|---|
| `test_demand_driven_ebu.py` | **985 passed, 0 failed, 198 groups** |
| `dynamic_ebu_theory_checks.py` | **265 deterministic checks, 0 failed** |
| `test_gaussian_foundation.py` | 65 passed, 0 failed |
| `test_capacity_v2_foundation.py` | 61 passed, 0 failed |
| `test_homeostasis_foundation.py` | 146 passed, 0 failed |
| `test_restoring_tendency.py` | 26 passed, 0 failed |
| `test_study_harness.py` | 120 passed, 0 failed |
| `test_study_protocol_schema.py` | 68 passed, 0 failed |
| `test_gaussian_harness.py` | 68 passed, 0 failed |
| `test_capacity_v2_harness.py` | 28 passed, 0 failed |
| `test_homeostasis_harness.py` | 109 passed, 0 failed |

Exact rational arithmetic throughout; every tolerance literally zero; no
randomized search in any check added by this pass.

Static validation of the preregistration: all **768** declared episodes
(3 classes x 4 arms x 64 replicates) construct, the declared arrival schedules
reproduce exactly, the disturbance never fires — and **0 epochs were executed**.

---

## 8. What remains open

- **Stage B is unfrozen**: arrival law, disturbance law, arm set, endpoint,
  replicate count and reporting decisions are all still open, exactly as
  `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` §4 records them. Stage A's replicate
  count is **not** inherited by it.
- F-1 to F-6 remain unrepaired, and F-1 and F-4 are now scoped to economic
  complete service, the only place that contract survives.
- The policy-dynamics question — whether any arm actually takes the
  burden-nonincreasing paths that exist — is untouched. That is the whole point
  of Stage A and Stage B.
