# Uncertainty propagation and state-dependent reach — auditor handoff

**Read-only, self-contained.** Records the two counterexamples, the corrected
rules, the oracle strengthening, test identities, and the dispositions taken
on the auditor's five points. Authorizes nothing. No registered experiment was
run.

| | |
|---|---|
| audited commit | `cc66123064cd73f6a31c34c92ff68fc6efa3f1ad` |
| correction commit | `b8ea65bdd8f1df26e25f8c2330bd628f4618b407` |
| correction tree | `da20ec4dc9b860e90a625e565a32dfe14d576a1d` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `bcb7cf38b0c2c876666b18b095d0ae7c2c57b77eabff54252e22951786555731` |
| `gaussian_harness` (pinned) | `a9158eef…fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c…21c2` — unchanged |
| `homeostasis` (pinned) | `8b462401…c3c6` — unchanged |
| demand-driven conformance | 449 assertions, 0 failures, 136 groups |
| all eight suites | 952 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations and reports: **0 files changed** |

This handoff is added by a later commit that changes no code.

Scope: uncertainty propagation and state-dependent over-coupling only. The
four earlier corrections — additive service, endogenous admission, cycle
provenance, sink validation — were not reopened and their tests pass
unchanged. The original unusable-route counterexample remains fixed.

---

## 1. Counterexample 1 — search uncertainty became impossibility

Nineteen independent one-unit suppliers, each with its own route to one
destination requesting one unit. Measured at `cc66123`, pure calculation:

| check | at `cc66123` | now |
|---|---|---|
| complete executable one-action plans | 19 | 19 |
| menu size | 19 | 19 |
| `physically_serviceable` | `SEARCH_BUDGET_EXCEEDED` | `PHYSICALLY_SERVICEABLE` |
| coupling reach | **empty** | full |
| admission classification | **blocked** | not blocked |
| recorded as undecided | — | no |

Two independent faults, both fixed.

**The search manufactured the uncertainty.** It pre-computed the worst-case
space as a product over reach routes, saw `2^19`, and refused before trying.
It now enumerates in **increasing plan size** and is bounded by the **work it
actually does**: it returns `SERVICEABLE` on the first plan found, so this
case is answered in one evaluation, and the budget is spent only on
requirements that cannot be satisfied. `SEARCH_BUDGET_EXCEEDED` is now rare
and genuine.

**The callers collapsed the verdict.** Coupling emptied the reach for any
non-serviceable answer; admission blocked on any non-serviceable answer. Both
now preserve three answers:

| verdict | coupling | admission |
|---|---|---|
| `PHYSICALLY_SERVICEABLE` | full structural reach | not blocked |
| `PHYSICALLY_IMPOSSIBLE` | empty reach; coupled only by shared pool | blocked |
| `SEARCH_BUDGET_EXCEEDED` | **full** structural reach | **not** blocked; recorded as undecided |

`Reach.verdict` carries the answer that produced it, so an audit can
distinguish a reach empty because the demand is *proved* impossible from one
full because the search could not decide. `AdmissionDecision.unresolved`
records undecided demands, and `admission.classify` exposes the per-demand
verdict directly.

All three verdicts are shown reachable and distinct: 19 suppliers / 1 unit →
serviceable; 16 suppliers / 100 units → impossible (space fully enumerated);
20 suppliers / 100 units → undecided.

## 2. Counterexample 2 — a sound superset still over-coupled

Same three deliveries `A→B`, `C→D`, `E→F`, sources `A=C=E=1`, destinations
`B=D=F=0`. Added `B→D` and `D→F`, **capacity 1**, carrying the only permitted
quantum — so a capacity-only usability test calls them usable. But `B` and `D`
hold nothing, and source-funding forbids a coordinate paying for an outflow
with quantity arriving in the same instant, so neither can carry an action
here, not even inside a simultaneous group.

| configuration | executable actions | components | menus (at `cc66123`) | menus (now) |
|---|---|---|---|---|
| without added routes | 3 | 3 | `[1,1,1]` | `[1,1,1]` |
| with empty-source routes | **3** (identical) | 1 → **3** | **`[0]`** | **`[1,1,1]`** |

**Correction.** Blindness to unusable infrastructure has two limbs, not one. A
route is invisible to the reach when it can carry no allowed quantum **or**
when its source cannot fund the smallest quantum it could carry at the frozen
baseline. `enumeration.live_routes` implements the second, and
`structural_reach` is built from live routes.

**Soundness.** Source-funding requires a coordinate to already hold the total
it sends, so a route carrying an action of quantity `q` needs
`state[source] >= q >= min usable quantum`. Liveness is therefore a
*necessary* condition for a route to appear in any executable plan, and
filtering on it removes no route that could appear. The reach remains a sound
superset of every minimal plan's support.

The reach is consequently **state-aware**: a route can be usable in the world
and dead in the state, and liveness tracks the state in both directions. When
`B` and `D` are funded the added routes become live and may legitimately
couple the demands — which is correct, since `B` then holds stock `D` could
draw on.

## 3. Oracle strengthening, and what it exposed

Per disposition 3, the oracle now compares each outcome as a pair — canonical
physical increment **and** settled owner receipts — because equal physical
outcomes do not by themselves establish equal receipts, and receipts drive
affordability.

That immediately exposed a comparison artifact rather than a model defect: the
component side enumerated at the world's own cap of 2 while the global side
searched to bound 3, so a legitimate three-action plan appeared only on the
global side. Comparing increments alone had hidden it, because that plan's
increment was also reachable in two actions with **different owners**.

The oracle now rebuilds the world at the comparison bound and equalises the
cap on both sides, which isolates the decomposition question it exists to
answer. The per-component asymmetry remains real, declared in
`DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md`, and tested separately.

Agreement after equalisation: 12 sandwater world/state cases at bounds 2 and
3, three counterexample-world variants at bounds 2 and 3, and a mixed
economic/physical demand set — **all agree exactly, receipts included**.

As the auditor notes, and as the oracle's own docstring now states, this is
agreement on the cases enumerated and **not a general decomposition proof**.

## 4. Dispositions taken on the auditor's five points

1. **Nonnegativity argument accepted** as holding under the declared
   source-funded model, and accepted that it addresses under-coupling only.
   The two over-coupling counterexamples were treated as the live risk and are
   the subject of §2.
2. **Plan-cap interpretation.** The disposition is unchanged — a menu
   restriction, not physical law — but its presentation is corrected. §3.3 of
   the disposition now states explicitly that admitting beyond-cap obligations
   is a **declared design choice**, not the only policy compelled by the
   authority sources; refusing them with an explicit non-scarcity reason is
   equally coherent under (A), and a study may adopt it provided it does not
   record the refusal as scarcity.
3. **Oracle comparison.** Extended to receipts (§3). The docstring now records
   that passing the fixtures is not a general proof, and that sampling
   probabilities are not established by it — the product structure of
   independent menus, which is what makes component-wise uniform choice equal
   global uniform choice, is tested separately.
4. **Decoupling impossible demands.** Retained for *proved* impossibility,
   subject to the shared-pool rule, and **withdrawn for undecided searches**,
   which now keep their full reach (§1).
5. **Search-incomplete rates.** They do not block preregistration design, and
   are not treated as doing so. `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` §4a
   and decision-packet §3.3 items 6–7 now require, outcome-blind and before
   any confirmatory run, either a cap proved sufficient for the declared world
   and arrival law — with the run asserting a zero rate and failing closed
   otherwise — or an explicit computational-failure rule fixing a maximum rate
   and the disposition of a run exceeding it. **Raising the cap until an
   observed rate looks negligible is explicitly forbidden.** The rate falsifies
   the search, never the mechanism.

## 5. Tests added

| test | asserts |
|---|---|
| `test_a_wide_but_easy_requirement_is_not_refused_on_its_search_space` | counterexample 1: 19 plans, serviceable, non-empty reach, not blocked, not undecided |
| `test_search_uncertainty_never_becomes_impossibility` | all three verdicts reachable and distinct; undecided keeps full reach and is not blocked; `classify` carries the verdict |
| `test_an_undecided_demand_is_not_rejected_for_scarcity` | an undecided order is admitted with the uncertainty recorded, not rejected |
| `test_empty_source_routes_cannot_change_serviceability` | counterexample 2: usable-but-dead routes, identical executable set, coupling and serviceability unchanged |
| `test_a_route_becomes_live_when_its_source_is_funded` | liveness tracks the state both ways, and may then legitimately couple |
| `test_the_structural_reach_is_state_aware` | the reach is built from live routes |
| `test_the_oracle_compares_receipts_not_only_increments` | outcomes are (increment, receipts) pairs and both sides agree |
| `test_the_oracle_equalises_the_plan_cap_on_both_sides` | the comparison rebuilds the world at the bound |

All earlier coupling tests, including metamorphic A–H and the original
unusable-route counterexample, are unchanged and pass.

## 6. Rehearsal

3,200 epochs, four policies, four replicates. **NON-CONFIRMATORY. Not
evidence.** Replays exactly; identity stable; accounting, conservation,
nonnegativity, separability and capacity-source residuals all exactly zero;
zero double service; zero unprovenanced actions; raw arrivals identical across
arms; **zero `SEARCH_BUDGET_EXCEEDED` epochs**. Results are byte-identical to
the previous run, which is expected: in this world no route is unusable or
dead and no search was undecided, so neither correction can change it.

`SEARCH_INCOMPLETE_AT_PLAN_CAP` remains 29 / 99 / 71 / 105 by arm. Under §4a
that is now a declared gate rather than something to tune away.

## 7. Prohibited mutations — none performed

| prohibition | status |
|---|---|
| reopen resolved service/admission/provenance/sink work | not reopened; tests unchanged and passing |
| modify a historical pinned artifact | 0 files changed under the pinned packages, `books`, the registered result directories, all preregistrations and registered reports |
| redesign EBU, Gaussian valuation or Capacity V1 | untouched |
| run a registered experiment | none run |
| choose the primary endpoint | not chosen; arrival law still unfrozen |
| broaden scope | limited to the two defects, the oracle strengthening, and the four document corrections the dispositions called for |

## 8. Readiness

> ## READY FOR PREREGISTRATION DESIGN

Against the five stated conditions:

| condition | status |
|---|---|
| auditor counterexample fixed | **yes** — the original unusable-route case and both second-pass cases, all permanent regressions |
| unusable-infrastructure invariance passes | **yes** — both limbs: capacity and source funding |
| global/component feasible sets agree in exhaustive fixtures | **yes** — receipts included, cap equalised, all cases |
| plan-size-cap semantics scientifically resolved | **yes** — disposition A, with the admission consequence now labelled a design choice and a completeness gate required before confirmatory execution |
| no historical pinned artifact modified | **yes** — 0 changed |

Not permission to execute, and the qualification the auditor asked for is
recorded rather than glossed: the oracle establishes agreement on enumerated
fixtures, not a general decomposition theorem. The arrival law and the primary
endpoint remain unfrozen, and the gates in
`DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md` §3 and §5 — now including the
search-completeness rule — still stand.

## 9. Requested auditor disposition

1. Confirm that liveness — usable by capacity **and** fundable by its source
   at the frozen baseline — is the right necessary condition, and that no
   third limb is needed for a route to be behaviorally invisible.
2. Confirm that carrying `UNRESOLVED` as a *full* reach and a *non*-rejection
   is the right conservative direction in both callers.
3. Confirm the oracle's cap equalisation is legitimate isolation rather than
   concealment of the per-component asymmetry.
4. Confirm the §4a completeness rule is strong enough to stand as a
   preregistration gate.

## 10. Files to read

| file | role |
|---|---|
| `demand_driven_ebu/enumeration.py` | `live_routes`, `structural_reach`, the work-budgeted size-ordered search |
| `demand_driven_ebu/coupling.py` | three-way verdict handling, `Reach.verdict` |
| `demand_driven_ebu/admission.py` | `classify`, `unserviceable_ids`, `unresolved_ids` |
| `demand_driven_ebu/oracle.py` | receipts in the comparable, `at_bound` |
| `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` | §3.3 design choice, §3.4 three verdicts, §4a completeness gate |
| `test_demand_driven_ebu.py` | section "AUDITOR 2, SECOND PASS" |
