# Study-1 policy-conditioned oracle — final auditor handoff

**Read-only and self-contained.** Records one correction: the verification
layer now conditions on capacity balances and policy identity, so it checks
the law each arm actually samples from instead of a pre-affordability set no
EBU arm ever sees. **Authorizes nothing.** No registered experiment was run,
the arrival law is unfrozen, and the primary endpoint is unchosen.

| | |
|---|---|
| previous handoff commit | `d99e36b` |
| branch | `gaussian/stage-a-environment` |
| `demand_driven_ebu` code identity | `999158b0ace4cbfa333943a7b7a119a1d3d247c410cafd87d6038cac4c46cbad` |
| `gaussian_harness` (pinned) | `a9158eef…fe55` — unchanged |
| `capacity_v2` (pinned) | `8976da3c…21c2` — unchanged |
| `homeostasis` (pinned) | `8b462401…c3c6` — unchanged |
| demand-driven conformance | 935 assertions, 0 failures, 190 groups |
| all eight suites | 1,438 assertions, 0 failures |
| registered artifacts | `results/stage_a`, `results/stage_b`, `results/homeostasis`, all preregistrations, reports and books: **0 files changed** |

Unchanged, as instructed: demand semantics, service accounting, admission,
Capacity V1, the EBU equations, plan enumeration, and the frozen Study-1
physical domain.

---

## 1. The one question put to you

> **Within the frozen Study-1 domain, does the policy-conditioned oracle now
> faithfully reproduce physical eligibility, affordability, mandatory
> inaction, and RANDOM/ALIGNED/HOSTILE/CONTROL execution distributions?**

Requested response: **STUDY-1 FOUNDATION ACCEPTED**, or one exact in-domain
counterexample.

## 2. The defect

Runtime affordability was correct. The global physical reference was correct
within its declared scope. What was wrong was that the oracle compared
**pre-affordability** plan sets as though they were runtime execution menus,
so levels C and D checked a distribution the model never samples from.

The symptom was visible in the previous pass and I mis-handled it: a
mandatory-action regression failed under `ebu_random` at zero balances, and I
switched the test to the comparator rather than asking why the EBU arm could
not act. The answer was that every plan was unaffordable — which is the
ordinary case, not an edge case.

## 3. What is kept

`G_physical(x, D)` survives unchanged as a distinct object answering exactly
one question: *which complete demand-serving plans can physically execute
now?* It is structurally blind to capacity, to policy and to
aligned/random/hostile preference — `plans_serving` and `global_progress` are
never passed a ledger or a policy, asserted from source in the suite, and
their output is shown identical across all four policies and across rich and
poor balances.

It is **not** described as the runtime action distribution for an EBU arm
anywhere.

## 4. What is added

A second layer taking state, demands, **balances and policy**:

    G_affordable = { G in G_physical :
                     projected balance of every required owner stays >= 0 }

| policy | eligible set | selection |
|---|---|---|
| `ebu_random` | `G_affordable` | uniform over canonical plan identities |
| `ebu_aligned` | `G_affordable` | `argmax E_G` **within** it, then the frozen uniform tie-break |
| `ebu_hostile` | `G_affordable` | `argmin E_G` **within** it, same tie-break |
| `control_random_no_ebu` | `G_physical` | uniform; affordability **intentionally bypassed** |

Restricting before taking the extremum is the substantive part. A hostile
actor's globally worst plan is frequently the one it cannot pay for, so the
two orders give different answers — demonstrated below.

## 5. Zero-affordable semantics

`G_physical` nonempty and `G_affordable` empty ⇒ `ALL_PLANS_EBU_UNAFFORDABLE`.
No physical action for that part; its demand **remains pending**. Kept
distinct from all three of its neighbours, and the suite asserts none is
collapsed into another:

    PHYSICALLY_IMPOSSIBLE   SEARCH_UNRESOLVED
    ALL_PLANS_EBU_UNAFFORDABLE   EXECUTED

plus the admission-specific `E_REJECTED_PHYSICAL_SCARCITY` and
`E_REJECTED_INCOMPATIBLE`, which are answers to a different question.

## 6. Mandatory action

- EBU arm: `G_affordable` nonempty ⇒ **one nonempty plan must execute**;
- comparator: `G_physical` nonempty ⇒ one nonempty plan must execute.

No voluntary no-op exists anywhere. Inaction follows only from an empty
eligible set, and which set that is depends on the arm.

## 7. Your fixtures, computed

### Ordinary starting state — `study_one_world`, `(4,4,4)`, zero balances, one unit wanted at `C`

| | |
|---|---|
| physical plans | **2** — `B->C q=1` at `E = -1`, `B->C q=2` at `E = -4` |
| `ebu_random` / `ebu_aligned` / `ebu_hostile` | affordable set **empty**, `ALL_PLANS_EBU_UNAFFORDABLE`, **no-action probability exactly 1**, order pending |
| `control_random_no_ebu` | both plans, `1/2, 1/2` by its frozen plan rule |

Confirmed end to end in the runtime as well: epoch status
`ALL_PLANS_EBU_UNAFFORDABLE`, executed group `g:[]`, state bit-identical
before and after, demand still held and reported
`ADMITTED_BUT_EBU_UNAFFORDABLE`, residuals exactly zero.

### Partial affordability — `three_supplier_world`, zero balances

Three suppliers, one unit each into `T`, priced by their own distance from
reference: exact EBUs `0`, `+1`, `-1`.

| policy | eligible | selects |
|---|---|---|
| `ebu_random` | 2 of 3 | uniform over 2 |
| `ebu_aligned` | 2 of 3 | the `+1` plan |
| `ebu_hostile` | 2 of 3 | the `0` plan — **not** the globally worst `-1` |
| `control_random_no_ebu` | 3 | uniform over 3 |

The `-1` plan is the one whose owner cannot pay. This is the case the old
oracle got wrong.

### Full affordability — same world, balances 9 each

`G_affordable == G_physical`, and `ebu_random`'s plan law equals the
comparator's exactly, as do the induced outcome laws. That is the regime where
the gate binds on nothing.

### Owner-specific affordability — `two_supplier_world`, balances `A = 0, B = 5`

Aggregate capacity is 5 and no plan costs more than 3, so a pooled test would
pass all four plans. Only **one** is affordable: every other plan draws on
owner `A`, who holds nothing. Affordability is per account, as Capacity V1
declares.

### Independent progress with an unaffordable component — `split_world`

Two disconnected deliveries, balances `A = 0, C = 1`. The part at `B` is
`UNAFFORDABLE` — no action, demand pending. The part at `D` executes. Nothing
is blocked, and `B` does not freeze `D`. Confirmed in the runtime: one
component `ALL_PLANS_EBU_UNAFFORDABLE`, the other `EXECUTED`, one demand
served, one still held, residuals exactly zero.

## 8. Verification levels

Two hierarchies, and the first is explicitly not a runtime verification.

**Pre-affordability** (`oracle.progress_levels`) — plan-set equivalence,
outcome support, and the laws `G_physical` *would* induce. The C and D
constants there are now named `C_PREAFFORDABILITY_RANDOM_LAW` and
`D_PREAFFORDABILITY_EXTREMAL_SETS` so they cannot be misread.

**Policy-conditioned** (`oracle.policy_levels`), which the harness gate runs:

| level | compares |
|---|---|
| **A** physical eligibility | the same `G_physical`, same blocked split |
| **B** affordable plan set | the same `G_affordable` under these balances, same unaffordable/resolved split |
| **C** policy plan distribution | the same selection law over canonical plan identities, for this policy |
| **D** modeled outcome distribution | the same `Phi`-pushforward law, multiplicity preserved |

**Level A alone is not called a runtime verification**, and the suite shows
why rather than asserting it: in `three_supplier_world`, `ebu_random` and the
comparator agree at level A and have different execution laws.

## 8a. Rehearsal — NON-CONFIRMATORY

Re-run because the gate path changed. `study-one-v1`, registered semantics on,
four-level policy-conditioned gate on, all four arms: 3,200 epochs, **22.5 s
per pass**, run twice. Replay deterministic; code identity stable across the
run. Worst residual anywhere **exactly 0**. `SEARCH_UNRESOLVED` **0**.
`SEARCH_INCOMPLETE_AT_PLAN_CAP` **0**. All four policy levels agreed on
**3,020** epochs; 180 had nothing to decompose.

The per-arm counts are unchanged from the previous run, which is the expected
result: this correction changes what is *verified*, not what the mechanism
does. The comparator shows zero `ALL_PLANS_EBU_UNAFFORDABLE` epochs in every
replicate, because it bypasses the gate by design, while the three EBU arms
show 220, 166 and 48 — the affordability outcome the old oracle could not
see.

## 9. Status

    READY FOR DEMAND-DRIVEN STAGE-A/B PREREGISTRATION DESIGN

with no remaining known in-domain construct, search or verification artifact.
This does **not** certify future loss or storage-capacity domains: F-5 and F-6
remain open, unrepaired and out of domain by declaration.

## 10. Files to read

| file | what it carries |
|---|---|
| `demand_driven_ebu/oracle.py` | `G_physical`, the policy-conditioned layer, `affordable_subset`, the four policy levels |
| `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` §7.5–7.9 | pre-affordability, the execution reference, zero-affordable semantics, mandatory action, the levels |
| `demand_driven_ebu/fixtures.py` | `three_supplier_world`, `split_world`, `ledger_of` |
| `test_demand_driven_ebu.py` | section *FINAL STUDY-1 POLICY-CONDITIONED ORACLE CORRECTION* |
| `demand_driven_ebu/harness.py` | the policy-conditioned gate |
| `demand_driven_ebu/capacity.py` | Capacity V1, unchanged: per-owner projection |
