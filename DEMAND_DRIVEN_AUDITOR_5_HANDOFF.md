# Study-1 oracle and sampling semantics — final auditor handoff

**Read-only and self-contained.** Records two corrections: the scientific
reference now matches the runtime's independent-progress semantics, and the
sampling unit is the canonical plan identity rather than the unique outcome.
**Authorizes nothing.** No registered experiment was run, the arrival law is
unfrozen, and the primary endpoint is unchosen.

| | |
|---|---|
| previous handoff commit | `4fd8b6947a47e2e3f2d06d8dd2c3dbdf0ba55ef2` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `3c2bfbbdfca29d612132d8673dec085e772f2c6a2c9f93bd676980317fe64e61` |
| `gaussian_harness` (pinned) | `a9158eef…fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c…21c2` — unchanged |
| `homeostasis` (pinned) | `8b462401…c3c6` — unchanged |
| demand-driven conformance | 692 assertions, 0 failures, 176 groups |
| all eight suites | 1,195 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations, reports and books: **0 files changed** |

Scope: the oracle's reference semantics and the sampling claim. The frozen
Study-1 domain was **not** reopened, and demand, service, admission and
capacity semantics were **not** modified.

---

## 1. The one question put to you

> **Within the frozen Study-1 domain, does the implementation now faithfully
> realize: independent progress of serviceable demand components; persistence
> of blocked demands; complete exact search; random sampling over canonical
> plan identities; and correct induced outcome probabilities?**

Requested response: **STUDY-1 FOUNDATION ACCEPTED**, or one exact in-domain
counterexample.

## 2. Defect 1 — the reference asked the wrong question

The runtime deliberately lets an independent component progress while another
is proved impossible. The old oracle asked instead *"is there one plan serving
every active demand?"*, which answers **no** in exactly those situations. The
component path also returned empty there, so the two agreed — vacuously, on
`0 == 0`, having compared nothing.

Reproduced on the fixed state you specified, `study_one_world` at
`(A, B, C) = (0, 6, 6)`:

| | |
|---|---|
| physical demand at `A` | 4 units short; one route in, largest quantum 2 ⇒ **proved impossible** |
| economic order at `C` | 1 unit, independent, **two complete plans** (`B->C` at 1 and at 2) |
| old comparison | `all_complete_global = 0`, `all_complete_components = 0` ⇒ **PASS** |

### What replaces it

`oracle.global_progress` is now the authority. For parts `C_1, ..., C_m` with
complete-plan sets `P_k`,

    G_progress = product over k of ( P_k         if P_k is nonempty
                                   ; {BLOCKED_k} if impossibility is proved )

`BLOCKED_k` contributes no physical action and leaves its demands unresolved.
**Every part with a nonempty plan set contributes exactly one plan** — a
serviceable part acts, and there is no voluntary no-action. On the fixture:

| | |
|---|---|
| `blocked` | `{P:r|A}` |
| `resolved` | `{E:000000:000:r|C}` |
| reference plans | **2**, both `B->C` |
| runtime plans | **2**, identical |
| all four levels | pass, on a **non-empty** comparison |

The vacuous pass is now structurally impossible for the progress reference.

**Independence of the reference.** `global_progress` calls neither `coupling`
nor the pruned search — asserted from source in the suite. It re-derives the
partition from the frozen Study-1 reach definition using **brute-force**
serviceability, enumerates each part by brute force, and then enumerates the
non-blocked demand set **with no partition at all**; that last set is the
reference, and the partitioned product is checked against it. What it
re-derives is the frozen *definition*; it does not independently justify the
choice of definition, and it is exact only inside the Study-1 domain.

**The narrow query survives**, per your §4, under the explicit name
`all_complete_plans` / `all_complete_outcomes`, answering *can every active
demand be completely satisfied in one epoch?* Its docstring states the
question and disclaims runtime equivalence. It was not deleted.

**One thing the new internal check caught immediately.** Comparing the
partitioned product against the decomposition-free set at an artificially
small action bound reports the *declared per-component asymmetry* — a
decomposed epoch may hold more total actions than any single capped plan — as
a decomposition defect. Both sides now carry the same bound. Inside the
Study-1 domain the bound is the live route count, so nothing is removed at
all and the question does not arise; it arises only for out-of-domain worlds
compared at a hand-chosen bound.

## 3. Defect 2 — the sampling claim rested on a false bijection

The previous document stated that Theorem D made
`(G_1, ..., G_K) -> G` a bijection **onto outcomes**, and concluded that
uniform plan sampling induces a uniform outcome law. **That claim was false
and is withdrawn.** The bijection is onto **plan identities**. The outcome map

    Phi(plan) -> (exact physical increment, settled owner receipts)

is **many-to-one**.

### Frozen

> **The Study-1 random actor policy is uniform over distinct canonical
> complete service plan identities** — never over unique aggregate outcomes.

A plan identity is a canonical physical action set. `PlanGroup` sorts its
actions and refuses a repeated route, so two encodings of one action set are
one identity, and `plans.enumerate_service_plans` now **refuses** a menu
carrying two records of one identity rather than relying on it not happening.
Two genuinely different action sets stay two plans even when they agree in
post-state, increment and receipts.

### Your fixture, computed

`two_supplier_world`: suppliers `A`, `B` each hold 2; destinations `C`, `D`
each need 1; either supplier can serve either.

| | |
|---|---|
| distinct irredundant plan identities | **4** |
| distinct modeled outcomes | **3** |
| induced random law | **1/4, 1/2, 1/4** |

`{A->C, B->D}` and `{B->C, A->D}` are different action sets that agree in
increment, post-state and receipts, because `C <-> D` is an automorphism of
the state and potential. So

    P(outcome = o) = |{ plans G : Phi(G) = o }| / |all eligible plans|

and outcome probability carries plan multiplicity. It is **not** `1/3` each.
Duplicate plan *records* change nothing, because identities are what is
counted — asserted by feeding the menu to the canonicaliser twice.

### Aligned and hostile

First restrict to the plans attaining the extremal group EBU, then apply the
frozen uniform tie-break over those **plan identities**, then derive outcome
probabilities from that plan distribution. In this world the two behave
oppositely, which is exactly why the tie set must be computed over plans:

| policy | EBU | tie set | induced outcome law |
|---|---|---|---|
| aligned | `-2` | the two **cross** plans | a point mass — they share one outcome |
| hostile | `-3` | the two **same-supplier** plans | `1/2, 1/2` — their outcomes differ |

## 4. The four verification levels

Separate, because none implies the next.

| level | compares |
|---|---|
| **A** plan-set equivalence | the same distinct plan identities, and the same blocked/resolved split |
| **B** outcome support | the same `Phi` images |
| **C** induced random law | the same outcome probabilities, multiplicity included |
| **D** aligned/hostile | the same tie sets and the same induced outcomes |

**B alone proves neither C nor D**, and the suite demonstrates it rather than
asserting it: a flat law over the correct support of `two_supplier_world` has
the same support as the correct law and is a different distribution.

`EconomyRun(decomposition_gate=True)` runs all four every epoch and refuses on
any disagreement.

## 5. Mandatory action, persistence, integrity

Exact regressions, all on the `(0, 6, 6)` fixture:

- the serviceable component **executes one nonempty plan** — epoch status
  `EXECUTED`, executed group not `g:[]`;
- the blocked component reports `NO_COMPLETE_PHYSICAL_PLAN`, contributes no
  action, and **its coordinate is bit-identical before and after**;
- the blocked demand **persists** into the next epoch, because the deviation
  that created it is still there;
- `SEARCH_UNRESOLVED` remains a registered-job integrity failure and is
  distinct from `BLOCKED`: `BLOCKED` is a reference marker and never a search
  verdict.

## 6. Documentation corrected

`DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` §7 was rewritten to distinguish
all-demands-complete solvability, independent-progress runtime semantics, plan
identities, modeled outcomes and outcome probabilities. The false bijection
claim is removed and marked withdrawn in place. Contract §6 and §16, the
evidence-status table and the readiness report carry the same correction, and
the contract's correction log gains rows 9 and 10 naming both defects.

## 7. Prohibited mutations — none performed

The frozen Study-1 domain was not reopened. Demand, service, admission and
capacity semantics were not modified. No registered historical artifact,
preregistration, result file, book or PDF was touched. `gaussian_harness`,
`capacity_v2` and `homeostasis` identities are unchanged and asserted in the
suite. No AWS. No registered experiment.

## 7a. Rehearsal — NON-CONFIRMATORY

Re-run because the gate path changed materially. `study-one-v1`, registered
semantics on, four-level decomposition gate on: 3,200 epochs, **25.4 s per
pass**, run twice. Replay deterministic; code identity stable across the run.
Worst residual anywhere — accounting, conservation, nonnegativity,
separability, capacity-source — **exactly 0**. `SEARCH_UNRESOLVED` **0**.
`SEARCH_INCOMPLETE_AT_PLAN_CAP` **0**. All four levels agreed on **3,020**
epochs; 180 had nothing to decompose.

The general `sandwater-v1` block is byte-identical to its previous run, as
expected: these corrections change the reference and the claim, not that
world's behaviour.

## 8. Status

    READY FOR DEMAND-DRIVEN STAGE-A/B PREREGISTRATION DESIGN

with no remaining known in-domain construct or search artifact. This does
**not** certify future loss or storage-capacity domains: F-5 and F-6 remain
open, unrepaired and out of domain by declaration.

## 9. Files to read

| file | what it carries |
|---|---|
| `demand_driven_ebu/oracle.py` | the three questions kept apart, `Phi`, the progress reference, the four levels |
| `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` §7 | independent progress, Theorem D restated, plan identities, the corrected sampling statement |
| `demand_driven_ebu/fixtures.py` | `blocked_neighbour_state`, `two_supplier_world` |
| `test_demand_driven_ebu.py` | section *FINAL STUDY-1 ORACLE + SAMPLING SEMANTICS CORRECTION* |
| `demand_driven_ebu/plans.py` | the canonical-identity refusal |
| `demand_driven_ebu/harness.py` | the four-level decomposition gate |
