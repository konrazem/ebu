# Study-1 domain freeze — auditor handoff

**Read-only and self-contained.** Records the frozen domain, the three
theorems proved inside it, the registered failure semantics, the two
out-of-domain counterexamples retained as regressions, and the conformance
identities. **Authorizes nothing.** No registered Stage-A or Stage-B
experiment was run, the arrival law is unfrozen, and the primary endpoint is
unchosen.

| | |
|---|---|
| previous handoff commit | `66e8ea7704d0ff0cc51681185720170e494045f7` |
| Study-1 freeze commit | `8b3657af8c90e0b9fe0642f6d454d732da697500` |
| freeze tree | `24fc101843375745c5afbf9e9e7fa81e2a06ce25` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `967a59f420aff524276a7c7f3dc5ea18aa07324ca512254b03341a52590fccff` |
| `gaussian_harness` (pinned) | `a9158eef…fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c…21c2` — unchanged |
| `homeostasis` (pinned) | `8b462401…c3c6` — unchanged |
| demand-driven conformance | 592 assertions, 0 failures, 162 groups |
| all eight suites | 1,095 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations, reports and books: **0 files changed** |

Scope: the Study-1 domain freeze only. The corrections from the three earlier
audit passes — additive service, endogenous admission, cycle provenance, sink
validation, coupling from the structural reach, uncertainty propagation,
reach liveness — were not reopened, and their tests pass unchanged.

---

## 1. The one question put to you

> **Is the declared Study-1 domain internally complete and free of known
> construct-validity and search-truncation artifacts?**

That is the whole request. You are **not** asked to prove or assess
unrestricted future generality, and nothing below claims any. Two known
artifacts outside the domain are documented rather than fixed, and they are
outside the question deliberately.

## 2. The frozen domain

`demand_driven_ebu/study_one.py`, identity
`EBU-DEMAND-DRIVEN-STUDY-1-DOMAIN-v1`. Seventeen conditions, each separately
checked by `domain_violations` and separately exercised by the conformance
suite.

**Physics (1–15).** One homogeneous scalar resource; every coordinate a
valued stock; `x_i >= 0`; exact conservation `sum_i x_i = M`; lossless
transfers `eta = 1`; no loss sinks; no irreversible sinks; no recoverable
waste; **no upper destination-storage capacities**; fixed topology; finitely
many declared action quantities; exact rational arithmetic; complete service
only; no partial service, backlog quantity, deadline or service quality; no
topology change.

**Computational (16–17).** `max_plan_size >= len(usable_routes)`, so the
enumeration cap cannot bind on anything; and
`plan_space(world) <= EXHAUSTIVE_BUDGET`, so an undecided search is
impossible.

`plan_space(world) = prod_r (1 + n_r) - 1` over usable routes. For the
declared rehearsal world `study-one-v1`: 3 coordinates, 4 usable routes, 2
quanta, 8 atomic actions, **complete plan space 80 against a budget of
200,000**, cap 4 against 4 usable routes.

Everything outside is declared **FUTURE UNSUPPORTED PHYSICS** and is not a
blocker. `EconomyRun(registered=True)` refuses to start outside the domain;
`sandwater-v1`, `loss-v1` and `audit-sink-v1` are all refused.

## 3. What is proved, and where

Full proofs in `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` §3, §4 and §7.

| | statement | scope |
|---|---|---|
| **L1** | a route carries an action in an executable plan **only if** it is live (usable, and its source funds its smallest usable quantum) | **every domain** — this is what keeps the structural reach a sound superset everywhere |
| **L2** | in a Study-1 world, every live route **does** carry an action, namely its singleton minimum plan | **Study-1 only** |
| **P** | the pruned serviceability search over the live structural reach is equivalent to complete enumeration of the whole finite plan space | Study-1 |
| **D** | `combine(F_components) == F_global`, including settled owner receipts and sampling probabilities | Study-1 |

L2's proof uses conditions 5 and 9 (lossless, no storage capacity). P's proof
uses the reach-soundness argument plus L1. D's proof uses condition 9 twice —
subsets of executable plans are executable, and the capacity-relief limb is
empty — and condition 5 once.

**Cross-checks rather than assertions.** Theorem P is checked against a
brute-force enumeration written independently of `enumeration`, over **all 91
integer states** of `study-one-v1` and four order sizes, plus four further
worlds. Theorem D is checked by `oracle.agree` at a common action bound, in
the conformance suite and again on every epoch of the Study-1 rehearsal.

## 4. Registered failure semantics

`SEARCH_UNRESOLVED` in a registered Study-1 job is a **computational
integrity failure**. The entire job is invalid:

- the trajectory does not continue;
- the epoch is not excluded;
- nothing is resampled;
- no seed is changed;
- the implementation is corrected and the identical job is rerun.

`study_one.JobInvalid` is a `Refusal` subclass, so nothing can absorb it as a
result. It is raised before admission and again before service. Condition 17
makes it unreachable inside the domain; it exists so that if the construction
is ever wrong the run stops instead of quietly recording a computational limit
as physics. The conformance suite forces it by cutting the budget to one
without cutting the domain condition, and asserts the message states all four
prohibitions.

Outside registered mode the three-way distinction is preserved as before:
`SEARCH_BUDGET_EXCEEDED` is a declared epoch status, is reported separately
from scarcity, and is never converted into rejection or no-action; the demand
is flagged `ADMITTED_BUT_UNRESOLVED_PHYSICAL` so the uncertainty stays visible.

**The apparent conflict is worth flagging explicitly.** "Admission requires
proved serviceability" and "UNRESOLVED must never become admission or
rejection" cannot both be satisfied by admitting or by rejecting. The
resolution is the third option: in a registered job an undecided search
**stops the job**. Inside the frozen domain the case cannot arise, so this
changes no valid Study-1 run; the exploratory admit-and-flag behaviour above
carries no scientific standing. `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` §5 sets
this out.

## 5. Two artifacts retained, not repaired — both OUTSIDE the domain

Both reproduce by pure calculation on a fixed state. Both are permanent
regressions that assert the defect **is present**, so any future repair has to
update them deliberately. Both worlds are refused by `require_domain`.

**F-5, non-binding storage capacity changes coupling**
(`fixtures.capacity_relief_world`). Two unrelated one-unit deliveries,
`A -> C` and `V -> W`, three units of resource in the entire world. Declaring
an upper storage capacity of **ten** on `C` changes no executable action —
verified action by action — and no binding constraint. But a declared capacity
activates the capacity-relief limb of `structural_reach`, so `C -> Z` enters
the reach of the demand at `C`, `Z` follows, and `V -> Z` drags in `V` and its
owner.

| | without the capacity | with it |
|---|---|---|
| inside the Study-1 domain | yes | no |
| executable actions | identical | identical |
| components | **2** | **1** |

This is a counterexample to unusable-infrastructure invariance itself, outside
the domain. Tightening it needs a third liveness limb — destination headroom —
which is not attempted.

**F-6, two lossy routes couple through a shared sink**
(`fixtures.shared_sink_world`). `A -> C` and `B -> D`, each wasting half into
the same audit sink `S`. The sink enters each reach as a delivery target and
then pulls in every route depositing into it. Components go from **2** to
**1**, and the merged reach claims both owner accounts, so affordability
settles jointly and service becomes all-or-nothing. The coupling is spurious
on the model's own terms: a sink may not source a route and carries no
capacity, so it can never compete for anything. Tightening it needs sinks
excluded from the reach closure. Not attempted.

## 6. Documentation corrected

The claim that the structural reach is *the exact set of tokens any minimal
plan could bind* was **general and wrong**, and your destination-capacity/loss
counterexample is what disproves it. It is replaced everywhere by: a sound
superset in every domain, exact only inside the frozen Study-1 domain.

Corrected in `enumeration` (module docstring and `live_routes`), `coupling`
(module docstring), and contract §6, with §16 added and two rows added to the
contract's correction log. The conformance suite asserts the superseded phrase
is gone and the domain-restricted phrasing is present, so the correction
cannot silently regress.

## 7. Rehearsal — NON-CONFIRMATORY

`demand_driven_rehearsal.py` now runs two blocks. Neither is evidence.

**Study-1 block**, `study-one-v1`, registered semantics **on**, decomposition
gate **on**: 3,200 epochs (4 policies × 4 replicates × 200), 15.9 s per pass,
run twice. Replay deterministic. Worst residual anywhere — accounting,
conservation, nonnegativity, separability, capacity-source — **exactly 0**.
`SEARCH_UNRESOLVED` **0**. `SEARCH_INCOMPLETE_AT_PLAN_CAP` **0**.
`combine(F_components) == F_global` verified on **3,020** epochs; 180 had
nothing to decompose. 517 raw arrivals per arm, identical across arms.

**General block**, `sandwater-v1`, unchanged and **byte-identical to the
previous run** — the expected result, since that world has no storage
capacities, no sinks and no undecided searches, so neither the freeze nor the
registered semantics can move it. It retains
`SEARCH_INCOMPLETE_AT_PLAN_CAP` 29/99/71/105 by arm and 0
`SEARCH_BUDGET_EXCEEDED`, which is exactly why it is **not** a Study-1 world.

## 8. Prohibited mutations — none performed

No registered historical artifact, preregistration, result file, book or PDF
was touched. `gaussian_harness`, `capacity_v2` and `homeostasis` code
identities are unchanged and asserted in the conformance suite. No AWS. No
registered experiment. The arrival law and the primary endpoint remain
unfrozen, as instructed.

## 9. Status

    READY FOR DEMAND-DRIVEN STAGE-A/B PREREGISTRATION DESIGN

and explicitly

    STUDY-1 DOMAIN VERIFIED  is NOT
    GENERAL DEMAND-DRIVEN FRAMEWORK PROVED FOR ALL LOSS/CAPACITY/TOPOLOGY MODELS.

Still open and deliberately untaken: Stage-A fixtures A1–A4; the stochastic
arrival law; the optional disturbance law; the arm set; the restoring-drift
endpoint; replicate count and horizon with a power argument; and the seven
findings-forced reporting decisions. All listed in
`DEMAND_DRIVEN_STUDY_ONE_READINESS.md` §4.

## 10. Files to read

| file | what it carries |
|---|---|
| `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` | the freeze, theorems L1, L2, P, D, the failure semantics, the non-claim |
| `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` | the finite completeness argument, the measured runtime, the Stage-A/B decisions still required |
| `demand_driven_ebu/study_one.py` | the domain predicate, `plan_space`, `completeness_bound`, `JobInvalid` |
| `demand_driven_ebu/enumeration.py` | liveness, the reach, the size-ordered budgeted search, the pruning-equivalence argument |
| `demand_driven_ebu/harness.py` | registered mode and the decomposition gate |
| `demand_driven_ebu/fixtures.py` | `study_one_world`, `capacity_relief_world`, `shared_sink_world` |
| `test_demand_driven_ebu.py` | section *FIRST DEMAND-DRIVEN STUDY DOMAIN FREEZE* |
| `DEMAND_DRIVEN_MODEL_FINDINGS.md` | F-5 and F-6 |
| `DEMAND_DRIVEN_EVIDENCE_STATUS.md` §4a | what is proved, and the scope of each result |
| `DEMAND_DRIVEN_PLAN_CAP_DISPOSITION.md` §4b | why Study 1 takes the proved-cap branch |

This coordinate block is completed by a later commit that changes no code.
