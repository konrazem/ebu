# SD-01 to SD-14 Master Test Register

**Status: PROSPECTIVE, DERIVED, SUBORDINATE. Not an authority.**

This register was reconstructed by static Git and document inspection only. It
registers nothing, adopts nothing, preregisters nothing, and authorizes no
execution. No model, tick, trajectory, benchmark, runner, test suite, Docker,
AWS, or SSO action was performed in producing it, and no result was inspected.

---

## 0. The canonical authority, and why this file exists anyway

**A single canonical register already exists.** It is not this file:

| | |
|---|---|
| File | `stage_d_scientific_validation_master_matrix.json` |
| Matrix id | `EBU-STAGE-D-MASTER-SCIENTIFIC-VALIDATION-MATRIX` |
| Version / status | `1.0.0-candidate` / `PROSPECTIVE_NO_EXECUTION_NO_OUTCOMES` |
| Git blob | `e6cd44f8b9e2e125403cb1359d819fc08afd2cb7` |
| SHA-256 of bytes | `081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81` |
| Size | 148,183 bytes |
| Path first added | `db5440a`, 2026-08-27, "Add Stage D scientific validation authority" |
| **This blob** first appears | `8936bb4`, 2026-08-27, "Correct Stage D hard-cap role binding" |

It does not stand alone. Four further documents govern with it, all carried by
the same 123 refs:

| File | Role |
|---|---|
| `STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md` | the normative human authority; freezes the questions, study order, configurations, controls, falsifiers and resource limits |
| `stage_d_scientific_validation_contract.json` | the governing machine contract |
| `stage_d_scientific_validation_evidence_schema.json` | the evidence schema |
| `stage_d_scientific_validation_predecessor_manifest.json` | the 39-row identity manifest the matrix's `predecessor_authority_reference_binding` requires every path-shaped dependency to match |

**Two additive amendments change SD-01 and are not in the matrix.** Neither is
referenced by it — `grep -i "growth\|continuation"` against the matrix returns
nothing — so reading the matrix alone gives an incomplete SD-01:

| Amendment | refs | Effect |
|---|---|---|
| `STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_AMENDMENT.md` | 99 | Creates **`SD-01-GROWTH-v1`**, "the second subcampaign of `SD-01`" — 8,192-tick runs, its own frozen question, its own output cap. "It completes before `SD-02` begins." It "does not create a fifteenth study or reorder `SD-01`". |
| `STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_AMENDMENT.md` | 117 | "supersedes the ambiguous use of `per scientific run`" for the wall-time, process-tree memory and primary-evaluation watchdogs; those become limits for **one bounded attempt slice**, under a separately frozen campaign envelope. |

**The programme has one version at every ref tip, but the file has been
corrected four times.** All 123 refs carry blob `e6cd44f8…` — there is no
competing version in play. The path's history holds five distinct blobs:

```
8856d23  2026-09-11  e6cd44f8b9  Revert "WIP: adopt the storage amendment ..."
8a24526  2026-09-11  4ccd67d441  WIP: adopt the storage amendment ...
8936bb4  2026-08-27  e6cd44f8b9  Correct Stage D hard-cap role binding
1a63d08  2026-08-27  0d1924a190  Correct Stage D scientific authority closure
96c9391  2026-08-27  f24ce7fe8a  Correct Stage D scientific validation authority
db5440a  2026-08-27  d6e2377133  Add Stage D scientific validation authority
```

The 2026-09-11 pair matters: it raised SD-01's `total_output_bytes` from
21,474,836,480 to 25,769,803,776 and was reverted the same day. **SD-01's
registered storage cap is live material, not settled background.**

**But it is unreachable from here.** The commit that introduced the path is not
an ancestor of `main` or of `v3.0-local-ebu-foundation`:

```
merge-base(v3.0-local-ebu-foundation, codex/sd01-stage-f-implementation)
  = 8793bda  2026-08-17  "Integrate Part I layout and distance emphasis"
  commits since, on v3.0-local-ebu-foundation :  12
  commits since, on the SD programme lineage  : 576
```

The two lineages split on 2026-08-17 and have not been rejoined. From this
branch the SD programme is invisible: `git grep "SD-01"` on
`v3.0-local-ebu-foundation` returns nothing at all.

**So this file is a navigation register, not a second authority.** It exists to
make the programme visible from the branch the current work is happening on,
and to say where that work belongs. Where it and the JSON matrix disagree, **the
JSON matrix wins.** Columns marked *(derived)* are this file's own reading, not
quotations from the matrix; columns marked *(matrix)* are taken from it. The
matrix has **no** `decision_boundary` field, so every such row here is a
condensation of `acceptance`, `falsifiers`, `prohibited_interpretations` and the
mandatory controls, and is labelled derived.

The right long-term fix is not to maintain two registers. It is to bring the
lineages together, or to state explicitly which one governs. **That is an author
decision this file does not make.**

---

## 1. The fourteen stages

Questions are quoted from the matrix. "Uniquely tests", "must not be retested"
and "cost readiness" are derived, the last two partly from each study's
`prohibited_interpretations`, `dependencies`, and `computational_feasibility`.

### SD-01 — Long-run homeostasis and viability

| Field | Value |
|---|---|
| **Question** *(matrix)* | Under the declared regenerative-source and demand families, which registered policies preserve viability, invariance, recursive feasibility, reserves, recovery, and regeneration over the complete horizon, including adversarial schedules and Allee thresholds? |
| **Uniquely tests** *(derived)* | Whether a policy keeps a stock viable over a long horizon. It is the **only** stage that tests long-run behaviour of a control policy. Nothing later re-opens it. |
| **Dependencies** *(matrix)* | accepted viability and constrained-control equations; accepted unit, boundary and conservation authority; future independently accepted Stage E long-run harness |
| **Run scale** *(matrix)* | 4 source regimes x 4 demand ratios x 2 shock schedules x 6 policies = **192 runs**, plus 4 controls = **196 trajectories**, **20,000 ticks** each; 39,120,000 expected evaluations; ~12 GB storage |
| **Implementation** *(matrix)* | **future** Stage E registered viability model adapter; **future** immutable trajectory and checkpoint writer; **future** model-local H0/H1/H2/H3 policy adapter — "no historical P1C interface or semantics". All three are marked `future` in the matrix; none exists. |
| **Must not be retested later** *(derived)* | Long-run viability, reserve protection, recursive feasibility and recovery. SD-09 revisits recovery **only** under infrastructure failure and fairness; SD-14 may not re-derive viability from a scenario aggregate. |
| **Decision boundary** *(derived)* | Every registered cell has a visible disposition; positive controls pass and negative controls fail in the registered direction; all six falsifiers false. Falsifiers include `x<0`, breach of the reserve floor where protection is claimed, empty `A_H3`, unreconciled conservation residual, and any silent clamp or post-outcome parameter change. |
| **Status** *(derived)* | **BLOCKED — operationally prepared, scientifically gated.** Its own current-state authority, `SD01_READINESS.md`, opens: "**SD-01 is not ready to run.** Local candidate validation passing is not readiness". Its `evidence.prerequisites` require an "independent Stage E PASS" that does not exist; its route packet is unsealed; execution is unauthorized. See §3 and §5. |
| **Also registered** *(derived)* | **`SD-01-GROWTH-v1`**, a second subcampaign of SD-01 (8,192-tick runs, its own frozen question and output cap), added by the dynamic-growth amendment and **absent from the matrix**. It "completes before `SD-02` begins". |
| **Cost readiness** *(derived)* | **Could need AWS.** Registered caps: 14,400 s wall **per run**, 4 GiB RSS **per run**, 5 GiB trace **per run**, and 20 GiB `total_output_bytes` — a **study total**, not a per-run figure, and the one the 2026-09-11 revert touched. The continuation amendment converts the three per-run watchdogs into per-attempt-slice limits. An SD-01 AWS execution profile and IAM role already exist; `SD01_READINESS.md` records that the measured envelope already exceeded four recorded limits. |

### SD-02 — Gate 1D-C, robust-P1C, and Gate 1E authority recovery

| Field | Value |
|---|---|
| **Question** *(matrix)* | Does the exact inherited Gate 1D-C protocol preserve its registered capability distinctions, and can robust-P1C and Gate 1E later be specified without inventing missing authority? |
| **Uniquely tests** *(derived)* | Preservation of an **inherited** protocol across a framework change; and whether two named authorities can be recovered rather than re-invented. |
| **Dependencies** *(matrix)* | the Gate 1D-C protocol, plan and finalization addendum; a **separate future** robust-P1C and Gate 1E authority amendment |
| **Run scale** *(matrix)* | 3 worlds x 5 arms x 2 timesteps = **30 Gate 1D-C runs**; **zero** robust-P1C and **zero** Gate 1E runs authorized |
| **Implementation** *(matrix)* | inherited Gate 1D-C official runner after future authorization; robust-P1C interface **FORBIDDEN_UNTIL_SEPARATE_AMENDMENT**; Gate 1E interface **FORBIDDEN_UNTIL_SEPARATE_AMENDMENT** |
| **Must not be retested later** *(derived)* | Gate 1D-C's capability distinctions. Explicitly prohibited: reading Gate 1D-C **as** Gate 1E, or treating missing authority **as** a negative scientific result. |
| **Decision boundary** *(derived)* | The 30 registered runs reproduce their registered distinctions; robustness claims require frozen uncertainty and coverage, which do not exist yet. |
| **Status** *(derived)* | **SPLIT.** The Gate 1D-C half is **executed on `v3.0-local-ebu-foundation`** — 30 runs, receipt bound to execution SHA `8793bda`, 17 hash-bound sources all matching. The SD lineage does not record it (`stage_d_observations.executed_run_count` is `0`). The robust-P1C and Gate 1E halves are **blocked on authorship**, not on compute. |
| **Cost readiness** *(derived)* | **Local / laptop-scale.** 6,000 evaluations. Already run locally once. |

### SD-03 — Atomic generator and finite EBU chain

| Field | Value |
|---|---|
| **Question** *(matrix)* | For declared finite actions, does the complete chain `V -> mu=grad V -> f_e -> Psi_e -> J_e -> G_T -> finite EBU` preserve units, boundaries, derivatives, generator semantics, and accounting without treating any intermediate as the final score? |
| **Uniquely tests** *(derived)* | That the **finite EBU chain is well-formed**. This is the validation of exact finite EBU itself. Every later stage that uses an EBU value depends on this and may not re-establish it. |
| **Dependencies** *(matrix)* | Atomic Generator Foundation authority + contract; Atomic Interaction Declaration authority + contract; Conservation and Boundary Accounting Foundation. **No SD-stage prerequisite.** |
| **Run scale** *(matrix)* | 4 dimensions x 6 potential families x 4 action extents x 2 boundary modes = **192 cases**; 1,344 evaluations; 128 MB |
| **Implementation** *(matrix)* | accepted atomic declarations and generator call surfaces; future Stage E **exact-rational** oracle adapter |
| **Must not be retested later** *(derived)* | Unit and boundary consistency of the chain. Prohibited readings: gradient as electrical voltage; generator as conservation proof; finite case as universal physics. |
| **Decision boundary** *(derived)* | Exact-rational agreement across the chain; no intermediate treated as the final score. |
| **Status** *(derived)* | **READY FOR IMPLEMENTATION** — its authorities exist; the exact-rational oracle adapter does not. |
| **Cost readiness** *(derived)* | **Local / laptop-scale.** 1,344 evaluations, 128 MB. |

### SD-04 — Finite Taylor expansion and order effects

| Field | Value |
|---|---|
| **Question** *(matrix)* | For the registered smooth finite cases, when do truncated Taylor terms, mixed marginals, commutators, and action order reproduce or fail to reproduce direct finite effects? |
| **Uniquely tests** *(derived)* | The **approximation boundary**: where a series truncation stops matching the exact finite effect. The only stage that licenses any approximate reading. |
| **Dependencies** *(matrix)* | **SD-03**; accepted Atomic Generator and Interaction authorities |
| **Run scale** *(matrix)* | 3 dimensions x 4 orders x 4 step sizes x 8 fields x 3 composition regimes = **1,152 cases**; 5,184 evaluations; 512 MB |
| **Implementation** *(matrix)* | future independent symbolic/exact coefficient oracle; accepted finite action composition interfaces |
| **Must not be retested later** *(derived)* | Order effects and truncation error. Prohibited: Taylor truncation as exact without remainder; small-step numerical behaviour as universal limit; **commutator as causal responsibility**. |
| **Decision boundary** *(derived)* | Registered agreement/disagreement per order and step size, against an independent exact coefficient oracle. |
| **Status** *(derived)* | **BLOCKED on SD-03.** |
| **Cost readiness** *(derived)* | **Local / laptop-scale.** |

### SD-05 — Sequential, parallel, pairwise, and higher-order interaction

| Field | Value |
|---|---|
| **Question** *(matrix)* | How do quantity-fixed, rule-replayed, sequential, parallel, pairwise, and higher-order finite actions differ under the registered baselines and order semantics? |
| **Uniquely tests** *(derived)* | **Multi-action interaction measurement.** This is where a joint effect is compared against its parts — where an interaction index such as a double-count belongs. |
| **Dependencies** *(matrix)* | **SD-03**, **SD-04**; Atomic Interaction Declaration authority; `SEQUENTIAL_PARALLEL_BRIDGE.md` |
| **Run scale** *(matrix)* | 16 families x two semantics x `sum(n! for n=3..6)` = **27,840 complete sequence cases**, plus 9 bridge fixtures; 4 GB |
| **Implementation** *(matrix)* | accepted finite action and interaction declarations; future direct permutation oracle; future accepted Möbius oracle/transform pair |
| **Must not be retested later** *(derived)* | Interaction magnitude and order sensitivity. Prohibited: **interaction as causal responsibility**; pairwise closure as universal; parallel result as sequential result. |
| **Decision boundary** *(derived)* | Exact agreement with a direct permutation oracle over the complete registered sequence set. Conformance profile `MOBIUS-EXACT-01`. |
| **Status** *(derived)* | **BLOCKED on SD-03 and SD-04.** |
| **Cost readiness** *(derived)* | **Needs a benchmark.** 27,849 evaluations is small, but 4 GB of trace and a complete permutation sweep should be measured before sizing. |

### SD-06 — Möbius decomposition, nonzero empty baseline, hypergraphs, feasible posets

| Field | Value |
|---|---|
| **Question** *(matrix)* | Does exact Möbius inversion reconstruct every registered subset table including nonzero `E(empty)`, and how do declared Boolean, hypergraph, and feasible-poset domains change the valid decomposition? |
| **Uniquely tests** *(derived)* | **Exact decomposition of a joint effect into subset contributions.** The only stage where allocating a joint value among actions is a licensed scientific object. |
| **Dependencies** *(matrix)* | **SD-05**; `MOBIUS-EXACT-01`; accepted Atomic Interaction authority |
| **Run scale** *(matrix)* | 488 shared agreement tables through `n=12`; 16 scientific tables at `n=16`; 32 finite feasible posets; Stage E complexity dimensions `n=8..18`; **78,555,354 evaluations**; 4 GB |
| **Implementation** *(matrix)* | future independently readable **direct subset oracle**; future bitmask fast Möbius transform; future finite-poset incidence oracle |
| **Must not be retested later** *(derived)* | Decomposition validity. Prohibited: universal scalability; Boolean lattice as universal scientific topology; **zero empty baseline by convention when it is nonzero**; sparse low-order result as full-order evidence. |
| **Decision boundary** *(derived)* | The optimized transform must reproduce the direct oracle **exactly** over the complete registered domain; a mismatch is a failure, not a tolerance. Exceeding a hard limit is `COMPUTATIONALLY_INCONCLUSIVE` — never silent approximation. |
| **Status** *(derived)* | **BLOCKED on SD-05.** |
| **Cost readiness** *(derived)* | **Needs a benchmark; could need AWS.** 78.5 M evaluations with `O(n*2^n)` time and `O(2^n)` storage at `n=18`. Mandatory control 3 requires measured complexity evidence. |

### SD-07 — Canonical equivalence, recursive motifs, conditional certified reuse

| Field | Value |
|---|---|
| **Question** *(matrix)* | When do declared topologies or recursive motif occurrences satisfy accepted canonical equivalence and A1–A8 reuse conditions, and do corrections invalidate exactly the affected certified entries? |
| **Uniquely tests** *(derived)* | When a previously computed result may be **reused** for a structurally equivalent case, and whether invalidation is exact. |
| **Dependencies** *(matrix)* | **SD-06**; Canonical Topology Motif Programme foundation + contracts; `DAG-EXACT-01`; `CANONICAL-CACHE-01` |
| **Run scale** *(matrix)* | 257 canonical declarations; 1,479,457 direct canonical candidate evaluations; 4,180 occurrence visits; motif level 32, invalidation depth 64; 4 GB |
| **Implementation** *(matrix)* | accepted canonical topology declarations; future independent small-graph oracle; future isolated research cache and invalidation harness |
| **Must not be retested later** *(derived)* | Equivalence certification. Prohibited: canonical identity as performance; Fibonacci as universal structure; **cache hit as scientific evidence**; topological reachability as causality. |
| **Decision boundary** *(derived)* | Reuse permitted **only** under a certificate whose cache key is complete for every result-affecting input, authority and version; near-miss negative controls must fail. |
| **Status** *(derived)* | **BLOCKED on SD-06.** |
| **Cost readiness** *(derived)* | **Needs a benchmark.** 1.48 M evaluations; `O(V+E)` traversal evidence required. |

### SD-08 — Routes, queues, congestion, delays, provenance, dependency traversal

| Field | Value |
|---|---|
| **Question** *(matrix)* | For the declared transport/service networks, how do route, queue, congestion, delay, and failure schedules affect delivered service and provenance without confusing graph reachability with physical causality? |
| **Uniquely tests** *(derived)* | Network-level service under congestion and delay, and the **reachability-vs-causality** boundary. |
| **Dependencies** *(matrix)* | **SD-07**; `DAG-EXACT-01`; accepted topology and conservation authorities |
| **Run scale** *(matrix)* | 8 topologies x 4 loads x 4 failure schedules x 3 queue disciplines = **384 runs**, 10,000 ticks; 3,840,000 evaluations; **16 GB** |
| **Implementation** *(matrix)* | future registered network model adapter; future direct/optimized DAG traversal pair; future queue and provenance trace adapter |
| **Must not be retested later** *(derived)* | Route/queue/delay effects on service. Prohibited: reachability as causality; simulated congestion as empirical infrastructure data; **route efficiency as fairness**. |
| **Decision boundary** *(derived)* | Direct and optimized traversal must agree exactly; provenance must be complete. |
| **Status** *(derived)* | **BLOCKED on SD-07.** |
| **Cost readiness** *(derived)* | **Could need AWS.** 16 GB output, 3.84 M evaluations. |

### SD-09 — Resilience, recovery, fairness, adaptive infrastructure

| Field | Value |
|---|---|
| **Question** *(matrix)* | Under declared infrastructure failures and reserve regimes, which policies restore service and how are burdens and access distributed across registered groups? |
| **Uniquely tests** *(derived)* | Recovery **under infrastructure failure**, and distribution of burden across groups. Distinct from SD-01: SD-01 asks whether the stock stays viable; SD-09 asks who bears the cost when the network breaks. |
| **Dependencies** *(matrix)* | **SD-08**; `DAG-EXACT-01`; **future explicit institutional fairness authority** |
| **Run scale** *(matrix)* | 6 failure families x 4 reserve regimes x 4 fairness rules x 16 seeds = **1,536 runs**, 5,000 ticks; 7,680,000 evaluations; **20 GB** |
| **Implementation** *(matrix)* | future SD-08 network adapter; future group-ledger and institutional-metric adapter; future DAG invalidation adapter |
| **Must not be retested later** *(derived)* | Fairness and recovery under failure. Prohibited: physical optimum as fair institution; aggregate recovery as universal group recovery; **simulation as empirical justice evidence**. |
| **Decision boundary** *(derived)* | Registered fairness rules evaluated per group; seed summary policy `REGISTERED-SEED-SUMMARY-01` — **no bootstrap, no confidence language, no population inference**. |
| **Status** *(derived)* | **BLOCKED on SD-08 and on a missing fairness authority.** |
| **Cost readiness** *(derived)* | **Could need AWS.** |

### SD-10 — CLCD inference, correction, feedback, memory, delay, stability, error cost, closure, diagnostics, propagation

| Field | Value |
|---|---|
| **Question** *(matrix)* | Across the registered continuous and discrete CLCD models, when do inference, correction, feedback, memory, and delay yield bounded/stable error, and what costs, closure failures, diagnostics, and propagation follow? |
| **Uniquely tests** *(derived)* | Closed-loop stability: whether correcting an error converges or oscillates. |
| **Dependencies** *(matrix)* | **SD-06**, **SD-07**; CLCD programme review and milestone/diagnostics authorities; `DAG-EXACT-01` |
| **Run scale** *(matrix)* | 144 continuous cells + 96 discrete cells = **240 cells**, 1,000 samples each; 57,696,000 evaluations; 4 GB |
| **Implementation** *(matrix)* | accepted `correction_protocol` and `correction_diagnostics` surfaces; future registered continuous/discrete CLCD adapters; future direct/optimized dependency propagation pair |
| **Must not be retested later** *(derived)* | Stability of the correction loop. Prohibited: numerical stability as universal theorem; **sensitivity as responsibility**; correction as free energy or service; Möbius interaction as conjugacy inference. |
| **Decision boundary** *(derived)* | Bounded error under the registered stability predicate per cell. |
| **Status** *(derived)* | **BLOCKED on SD-06 and SD-07.** |
| **Cost readiness** *(derived)* | **Needs a benchmark.** 57.7 M evaluations. |

### SD-11 — Correction receipts, closure, conservation, no-magical-gain accounting

| Field | Value |
|---|---|
| **Question** *(matrix)* | Do action, correction, propagation, and settlement receipts preserve all declared physical, represented, EBU, causal, and institutional ledgers without magical gain or double-counting? |
| **Uniquely tests** *(derived)* | That the **books close**: no ledger gains value from a correction. |
| **Dependencies** *(matrix)* | **SD-10**; Conservation and Boundary Accounting Foundation; CLCD diagnostics authority; `MOBIUS-EXACT-01`; `DAG-EXACT-01` |
| **Run scale** *(matrix)* | 64 cases x 256 events = **16,384 event evaluations** across 8 DAG families; 2 GB |
| **Implementation** *(matrix)* | accepted conservation and correction receipt surfaces; future independent exact ledger oracle; future dependency traversal oracle |
| **Must not be retested later** *(derived)* | Ledger closure. Prohibited: bookkeeping closure as physical isolation; correction as free gain; settlement as causal truth; **interaction allocation as responsibility**. |
| **Decision boundary** *(derived)* | Exact ledger reconciliation against an independent oracle; any unreconciled residual fails. |
| **Status** *(derived)* | **BLOCKED on SD-10.** |
| **Cost readiness** *(derived)* | **Local / laptop-scale.** 16,384 evaluations. |

### SD-12 — Cooperation, protected disclosure, contestability, privacy, retaliation, trust, learning

| Field | Value |
|---|---|
| **Question** *(matrix)* | Within declared agent models, how do protected disclosure and contestable coordination rules alter cooperation, service, burden, retaliation risk, privacy loss, and learning under complete accounting? |
| **Uniquely tests** *(derived)* | Multi-agent institutional rules under complete accounting. |
| **Dependencies** *(matrix)* | **SD-09**, **SD-10**, **SD-11**; **future explicit cooperation/disclosure institutional authority**; `DAG-EXACT-01` |
| **Run scale** *(matrix)* | 64 agents; 6 governance x 4 disclosure x 4 distribution x 32 seeds = **3,072 runs**, 1,000 ticks; **196,608,000 evaluations**; 20 GB |
| **Implementation** *(matrix)* | future registered agent-model adapter; future disclosure/privacy receipt adapter; future dependency/correction traversal adapter |
| **Must not be retested later** *(derived)* | Institutional rule effects. Prohibited: **simulated agents as empirical people**; cooperation as universal law; disclosure as costless; institutional rule as physical optimum. |
| **Decision boundary** *(derived)* | Registered per-group metrics under complete accounting; seed summary policy only. |
| **Status** *(derived)* | **BLOCKED on SD-09/10/11 and on a missing institutional authority.** |
| **Cost readiness** *(derived)* | **Could need AWS.** The largest evaluation count in the programme. |

### SD-13 — Quote, settlement, reserves, access, governance, appeals, fraud, responsibility, compensation

| Field | Value |
|---|---|
| **Question** *(matrix)* | For declared quote-error and institutional regimes, how do settlement, reserves, access, fraud controls, appeals, responsibility decisions, and compensation remain reconciled without rewriting history or conflating sensitivity with responsibility? |
| **Uniquely tests** *(derived)* | What happens when a **quote is wrong** and the institution must settle anyway. |
| **Dependencies** *(matrix)* | **SD-11**, **SD-12**; **future explicit settlement/governance authority**; `DAG-EXACT-01` |
| **Run scale** *(matrix)* | 128 service events/day x 365 days; 8 quote-error x 5 settlement x 4 reserve/access x 16 seeds = **2,560 runs**; 119,603,200 evaluations; 16 GB |
| **Implementation** *(matrix)* | future quote/settlement model adapter; accepted correction receipt surfaces; future fraud/appeal/governance adapter; future dependency traversal adapter |
| **Must not be retested later** *(derived)* | Settlement reconciliation. Prohibited: model rule as legal advice; sensitivity as responsibility; settlement as scientific truth; **correction as historical erasure**. |
| **Decision boundary** *(derived)* | Full reconciliation with no history rewrite. |
| **Status** *(derived)* | **BLOCKED on SD-11 and SD-12 and on a missing authority.** |
| **Cost readiness** *(derived)* | **Could need AWS.** |

### SD-14 — Complete-economy scenarios

| Field | Value |
|---|---|
| **Question** *(matrix)* | Can a declared multi-domain model connect household, hospital, enterprise, infrastructure, and ecology scenarios while preserving all physical, service, interaction, correction, provenance, fairness, settlement, and institutional boundaries? |
| **Uniquely tests** *(derived)* | Whether the preserved boundaries survive **composition**. It tests nothing new about any single mechanism. |
| **Dependencies** *(matrix)* | **SD-01, 03, 05, 06, 07, 08, 09, 10, 11, 12, 13** — eleven of the thirteen — plus a future complete-economy model and institutional authority |
| **Run scale** *(matrix)* | five domain updates and 12 cross-domain exchange evaluations per day; 5 scenario families x 6 institutional configurations x 32 seeds = **960 runs**, 365 ticks; 5,956,800 evaluations; 20 GB |
| **Implementation** *(matrix)* | **future** independently accepted integrated model adapters; **future** domain boundary and exchange adapters; **future** accepted oracle, DAG, cache, receipt and checkpoint harnesses |
| **Must not be retested later** *(derived)* | Nothing follows it. |
| **Decision boundary** *(derived)* | Every boundary preserved under composition. Prohibited: synthetic complete economy as empirical economy; integrated model as universal theory; physical optimum as institutional choice; **a failed or inconclusive prerequisite hidden by an aggregate outcome**. |
| **Status** *(derived)* | **BLOCKED on eleven predecessors.** |
| **Cost readiness** *(derived)* | **Could need AWS.** |

---

## 2. Dependency structure, and why no stage may substitute for an earlier one

```
   independent roots                the one long chain
   ----------------                ------------------

   SD-02  (Gate 1D-C preserved;    SD-03  finite EBU chain
          robust-P1C + Gate 1E       |
          blocked on authority)      v
          nothing depends on it    SD-04  order effects / truncation
                                     |
   SD-01  long-run viability          v
          |                        SD-05  multi-action interaction
          |                          |
          |                          v
          |                        SD-06  Mobius decomposition
          |                          |
          |                          v
          |                        SD-07  canonical reuse
          |                          |
          |                   +------+------+
          |                   v             v
          |                 SD-08         SD-10  closed-loop stability
          |                 routes          |
          |                   |             v
          |                   v           SD-11  ledger closure
          |                 SD-09           |
          |                 fairness        |
          |                   |             |
          |                   +------+------+
          |                          v
          |                        SD-12  institutions
          |                          |
          |                          v
          |                        SD-13  settlement
          |                          |
          +--------------------------+
                                     v
                                   SD-14  complete-economy composition
```

**The diagram is the transitive reduction** of `studies[].dependencies`:
redundant edges implied by transitivity are not drawn. SD-10 does depend
directly on SD-06 as well as SD-07, and SD-12 on SD-10 as well as SD-11; those
arrows are omitted because the paths already exist. The per-stage rows in §1 and
the table in §5 list the **direct** dependencies in full.

`SD-02` is off the critical path: nothing depends on it. `SD-01` feeds only
`SD-14`. The long chain is `SD-03` to `SD-07`, where it forks into
`SD-08` and `SD-10` and rejoins at `SD-12`.

**Why substitution is forbidden, stage by stage.** Each row states what a later
stage would silently assume if the earlier one were skipped:

| If you skip | and jump to | you would be assuming, untested |
|---|---|---|
| SD-03 | SD-05 | that the finite EBU chain is unit-consistent and boundary-closed — the thing SD-03 exists to check |
| SD-04 | SD-05 | that action order does not matter, or that a truncation is exact |
| SD-05 | SD-06 | that a joint effect differs from its parts in a measured way — SD-06 decomposes a number SD-05 has not yet established |
| SD-06 | SD-07 | that a decomposition is valid before knowing whether inversion reconstructs the table |
| SD-07 | SD-08 | that cached or reused results are equivalent, uncertified |
| SD-08 | SD-09 | that service under congestion is understood before asking who bears its cost |
| SD-10 | SD-11 | that a correction loop converges, before auditing what it wrote to the ledgers |
| SD-11 | SD-13 | that the books close, before settling on them |
| any | SD-14 | that a boundary preserved in isolation is preserved under composition — and mandatory control: a failed or inconclusive prerequisite **must not** be hidden by an aggregate outcome |

The structural reason generalizes a rule the matrix states narrowly. Mandatory
controls 1 and 2 require, **for the Möbius and topology paths specifically**,
that a direct small-case oracle be preserved as the normative reference and that
any optimized transform reproduce it exactly. Control 9 adds that an
approximation "must never be substituted for an exact registered study", and
SD-14's prohibitions forbid hiding "a failed or inconclusive prerequisite"
behind
an aggregate outcome.

Read together — and this reading is **derived, not quoted** — the principle is:
a result is valid only where a reference that could contradict it already
exists. A later stage has no oracle for an earlier stage's question. Running
them together does not merge two experiments; it deletes the reference the
second one needed.

---

## 3. Where the current work belongs

| Current work | SD stage | Assessment |
|---|---|---|
| **Exact finite EBU** — `ebu_quote_v30.py`, the endpoint difference `Delta_e(q) = V_loc(z) - V_loc(z + dt*S_e*q) - C_a(q)` | **SD-03** | The object SD-03 validates. It is **implemented and in use** on this branch but has **not** been validated as SD-03 requires: no exact-rational oracle, no 192-case sweep, no unit/boundary sweep. It is being *used* by work that is downstream of a stage that has not run. |
| **Taylor / action-order work** — the `linear_diagnostic` first-order term | **SD-04** | Not begun. `ebu_quote_v30.py` exposes the first-order term "ONLY as a diagnostic (`linear_diagnostic`)" and forbids it becoming a settlement value; `v30_o14_multi_edge_plan.json`'s `heuristic.settlement_form` says the linear diagnostic "is NEVER used for settlement or ranking". Both are consistent with SD-04 being unrun. |
| **Multi-action interaction** — `group_quote`, `naive_sum`, `double_count`, the O14 aggregate diagnostics | **SD-05** | `double_count` is exactly SD-05's object. It is currently recorded as a settlement-free diagnostic, which is the correct conservative handling while SD-05 is unrun. |
| **Möbius / inverse-Möbius** | **SD-06** | Not begun, and correctly deferred. |
| **Joint action budget / selection machinery** — `longhorizon_v30.py`: joint cap, set enumeration, set selectors, request shaping, checkpoint chain, L0 path | **none — it is implementation, not a stage** | It is Stage-E-shaped infrastructure. `stage_e_harness/` on the SD lineage contains substantive `checkpoint.py` (8.7 kB), `mobius.py` (8.4 kB), `dag.py` (12.9 kB), `cache.py` (10.9 kB), `oracles.py` and `registry.py` — overlapping in purpose with parts of this module. Its `adapters/sd01.py`..`sd14.py` are **98-byte row-binding stubs**, not model adapters: each is three lines delegating to `base.py`, which only validates a matrix row's key set. **No SD study has an implemented adapter.** So the duplication is in the supporting machinery, not in the science. |
| **N/H/X long-horizon recovery candidate** | **SD-01** | See §4. It is an **unregistered alternative parameterization of SD-01**. |
| **AWS cost modelling** — `V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md` | **outside SD-01–14 as a scientific stage** | Operational Stage F work. The matrix already carries per-study `computational_feasibility` and registered `hard_caps`, and SD-01 already has an AWS execution profile, an IAM role and staged artifacts. The new cost plan sizes a study that is itself an unregistered substitute for SD-01. |

**The pattern.** Work on this branch has been proceeding **downstream-first**:
SD-05-shaped interaction diagnostics and SD-01-shaped long-horizon design are
being built while SD-03 — the stage that validates the EBU chain they all rest
on — has not been run. That is the specific failure mode the programme ordering
exists to prevent.

---

## 4. Where the N/H/X long-run study belongs

**Its question is SD-01's.** It asks whether a policy keeps a regenerative stock
viable under shocks with recovery between episodes — the shape of SD-01's
question, though not its wording. SD-01 asks which *registered policies*
preserve
viability "including adversarial schedules and Allee thresholds"; the N/H/X
candidate asks whether repeated *exact-finite-EBU decisions* preserve
homeostasis, reserve protection, service and recovery.

**Its objects are not all SD-01's.** SD-01's registered equations are a
viability kernel, a single-stock balance `x_pre = x_t + g(x_t) - shock_t`,
robust one-step feasibility, and Allee regeneration. There is **no EBU, no edge
and no interaction term** in SD-01. The N/H/X candidate is a three-cell,
two-edge network with `m = 2` simultaneous actions, an exact joint EBU, and
`group_quote`/`naive_sum`/`double_count` — objects §3 assigns to **SD-03** and
**SD-05**. So the candidate straddles SD-01's question and SD-03/SD-05's
machinery, which is itself the problem: it would answer a long-run question
using apparatus two earlier stages have not yet validated.

SD-01 is **already registered**, with a different configuration:

| | Registered SD-01 | N/H/X candidate |
|---|---|---|
| Source | logistic and **Allee**, `rho in {0.3, 0.6}`, `K=20` | logistic only, `rho=1.0`, `K=8` |
| Horizon | **20,000 ticks** | 1,600 ticks |
| Runs | **196 trajectories** | 1 world x 4 arms |
| Policies | H0, H1, H2_eta(0.5/0.9/1.0), H3 | four EBU/non-EBU arms |
| Reserve | floor `R=5`, margin `max(0, x-5)` | `R_eff` reserve-binding |
| Shocks | outflow `min(4, ...)` at ticks 2500/5000/10000/15000 | 4 episodes, first tick of each |
| Status | registered, Stage F prepared | **PROPOSED, NOT ADOPTED** |

The registered SD-01 implementation interface says, in terms: **"model-local
H0/H1/H2/H3 policy adapter; no historical P1C interface or semantics"**. The
N/H/X candidate is built on P1C screening. Those are not the same study.

**It would substitute for SD-01, not contribute to it.** Running N/H/X would
answer SD-01's question with an unregistered configuration, on a branch the SD
programme cannot see, using an EBU chain SD-03 has not validated. Note that
SD-01
already has a registered way to grow: `SD-01-GROWTH-v1`, a second subcampaign
added by amendment rather than by re-parameterizing the first. That is the
registered mechanism for extending SD-01, and N/H/X did not use it.

This is a judgement about **process**, not about the design's quality. The N/H/X
candidate may well be a better long-run study than registered SD-01. Nothing
here
assesses that, and nothing here forbids amending SD-01. What it says is that
adopting a second parameterization of an already-registered question, outside
the
amendment path, is not a neutral act — the matrix's own falsifier list for SD-01
includes "post-outcome parameter change", and this is the same hazard one step
earlier.

**The narrow, defensible reading:** the mechanisms in `longhorizon_v30.py` — a
joint budget cap, set enumeration, a checkpoint chain — may be useful to SD-01's
adapter. The **study design** (N/H/X families, four arms, 1,600 ticks, `F=5`)
belongs nowhere in the SD programme unless an author amends SD-01's registered
configuration, which is a separate authorization.

---

## 4A. Where the prospective conservative-world study belongs: outside the fourteen

The **prospective stochastic sustained-demand conservative-world study** is
registered as a **separate prospective candidate**. It is recorded here only so
that it is discoverable from the register; it does **not** occupy a stage.

- **No SD number.** None is assigned, none is implied, and no stage row above is
  created, renamed or reserved for it.
- **Not SD-01.** It does not amend, replace or supersede SD-01 or any registered
  SD study, and it rewrites no historical study identity. Design section 45
  requires a prospective *new* registration or an explicit *approved* amendment;
  the candidate is a candidate for the former and is neither.
- **Not regenerative.** Its world is closed and lossless and **regeneration is
  absent from the physical plant** - which is precisely why it is not a second
  parameterization of SD-01's regenerative question (contrast section 4).
- **Nothing scientific is frozen**: parameters, controllers, metrics,
  thresholds, seeds, horizons, tolerances and oracle rules all remain unfrozen.
- **Identity registration is not preregistration, not execution permission and
  not scientific evidence.** AWS and scientific execution remain unauthorized
  (E5, coordinate W-2 clause 6).

Its five controller arms (C0-C4) are all `CANDIDATE_UNAPPROVED` and every
`build()` path fails closed. Identity and arms:
`V3.0_PROSPECTIVE_STUDY_CONTROLLER_DECISION_PACKET.md`,
`ebu_candidate_controllers.py`.

**Corrections recorded (this revision).** Two errors in the C3 arm, both fixed:

1. Its export was bounded by the *reserve coordinate* `[x_i - R_i]_+`, which on
   the illustrative fixture left the source **below its own lower homeostatic
   band**. The fixture claims that depended on it were false and are withdrawn,
   including a "dominates" claim - a category error while metric slot S-M is
   unfilled.
2. The first correction then removed C3's reserve awareness entirely, reasoning
   that the committed P1C layer already supplied it. **That was wrong.**
   `R_eff` is a PROVIDER/EXPORT FLOOR bounding what a source may send; `R`
   (`NodeSpec.reserve`) is the HOMEOSTATIC RESERVE COORDINATE. `R_eff` does not
   implement `R`, and nothing in the resolver moves resource toward a
   destination below its `R`.

C3 is now the **three-stage reserve-and-band-aware** non-field arm
(`C3-reserve-and-band-aware`): one source-side band-safe budget
`A_i = [x_i - L_i]_+`, spent lexicographically on destination reserve deficits,
then lower-band deficits, then ordinary service inside the upper band. Design
section 27's stated purpose is retained, so **CONFLICT-4 is resolved without a
design amendment**; CONFLICT-5 (no destination-side resolver) is contained for
the first study by a configuration-time topology restriction and remains open
in general.

**Execution-record correction.** The foundation suite previously printed
`Model-state advancement: NONE` while executing one `apply_joint` and one
conformance tick. That claim was false and is withdrawn; the accurate record is
**2 single synthetic transitions, 0 trajectories, no scientific evidence**.
Those two checks now live in a separate opt-in execution class off the default
CI path, and the default gate is static-only and machine-enforced.

Nothing about the study's status changed: no arm is approved, no parameter is
selected, and every `build()` path still fails closed.

---

## 5. Status summary and cost readiness

**One blocker is common to all fourteen** and is not repeated in the table:
`STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md` is a "prospective authority candidate
only", the matrix's own `status` is `PROSPECTIVE_NO_EXECUTION_NO_OUTCOMES`, and
`stage_d_observations` records `configured_run_count: 0` and
`executed_run_count: 0`. **Nothing in the programme has run.** The "Blocked by"
column lists what is additionally true of each stage.

| Stage | Status | Additionally blocked by | Cost readiness |
|---|---|---|---|
| SD-01 | **BLOCKED — operationally prepared, scientifically gated** | route packet unsealed; execution unauthorized; `evidence.prerequisites` require an "independent Stage E PASS" that does not exist; measured envelope already exceeded four recorded limits | could need AWS |
| SD-02 | **SPLIT** — Gate 1D-C executed on `v3.0-local-ebu-foundation`; rest blocked | missing robust-P1C and Gate 1E authority | local |
| SD-03 | **READY FOR IMPLEMENTATION** | exact-rational oracle adapter does not exist — but **no SD-stage prerequisite**, and it is the **only** stage whose `evidence.prerequisites` do not include an independent Stage E PASS | local |
| SD-04 | blocked | SD-03 | local |
| SD-05 | blocked | SD-03, SD-04 | needs a benchmark |
| SD-06 | blocked | SD-05 | benchmark; could need AWS |
| SD-07 | blocked | SD-06 | needs a benchmark |
| SD-08 | blocked | SD-07 | could need AWS |
| SD-09 | blocked | SD-08; missing fairness authority | could need AWS |
| SD-10 | blocked | SD-06, SD-07 | needs a benchmark |
| SD-11 | blocked | SD-10 | local |
| SD-12 | blocked | SD-09/10/11; missing institutional authority | could need AWS |
| SD-13 | blocked | SD-11, SD-12; missing settlement authority | could need AWS |
| SD-14 | blocked | eleven predecessors | could need AWS |

### Why SD-03 and not SD-01

SD-01 is order 1 and by far the most prepared: an AWS execution profile, an IAM
role, 11 hash-pinned staged artifacts, a computed campaign identity and 196
distinct run identities. None of that is scientific readiness. Its route packet
is unsealed, `execution_permitted` is false, and its own readiness document
opens "**SD-01 is not ready to run**". Its matrix prerequisites require an
independent Stage E PASS that does not exist, and its registered adapter, writer
and policy interfaces are all marked `future`.

The decisive evidence is in the matrix's own evidence ladder, which this
register would otherwise have ignored:

| Stage | `target_level` | `prerequisites` |
|---|---|---|
| SD-01 | 5 | level-2 derivation checks; level-3 harness conformance; level-4 numerical verification; **independent Stage E PASS** |
| SD-03 | **4** | level-2 exact derivations; level-3 interface conformance |

> **Correction (superseded claim retained for trace).** An earlier revision of
> this section stated: "SD-03 is the only stage in the programme that does not
> require an independent Stage E PASS." That claim is **false** and is
> superseded by `SD_03_PRE_EXECUTION_READINESS.md` §8, which records that
> SD-03, SD-04, SD-05, SD-10, SD-11, SD-12 and SD-13 **all** omit it — seven of
> fourteen. The sentence is corrected below; the conclusion it supported still
> stands, on different grounds.

**SD-03 is the earliest executable stage in the programme.** Seven of the
fourteen stages do not require an independent Stage E PASS, but SD-03 is the
only one of them with **no SD-stage prerequisite at all**: SD-04 and SD-05
depend on SD-03, and SD-10 through SD-13 depend on stages further up the chain.
SD-03 is therefore gated only behind work that can be done now: an
exact-rational oracle and an interface-conformance check, over 192 cases and
1,344 evaluations in 128 MiB, on a laptop.

> **Registered-scale caveat.** The 7-projection / 1,344-evaluation figures are
> the *registered* ones. `SD_03_PRE_EXECUTION_READINESS.md` prerequisite **P1**
> records that three of the seven chain projections (`f_e`, `Psi_e`, `J_e`)
> cannot be computed for SD-03's declared domain; if the chain is narrowed
> instead of extended, the honest figures become 4 and 768. P1 is unresolved.

It is also the stage that everything else needs. SD-04, SD-05 and SD-14 depend
on it directly; SD-06 through SD-13 depend on it transitively. And the exact
finite EBU it validates is already in use on this branch, in Gate 1D-C and in
the
long-horizon work — used, but not yet validated as the programme requires.

**No price, host, or dollar budget appears in this register, deliberately.**
"Could need AWS" is a statement about registered hard caps and output volume,
not a costing. Sizing any stage in currency requires a measured host speed
ratio, which does not exist for any stage.

---

## 6. Non-claims

- This file is **not** the canonical register and does not supersede
  `stage_d_scientific_validation_master_matrix.json`.
- Nothing here is registered, adopted, preregistered, or authorized to execute.
- No stage status here is a scientific result. "Executed" for Gate 1D-C means a
  run happened and produced a receipt, not that any hypothesis was settled.
- No prices, hosts, or budgets are proposed.
- The mapping in §3 and §4 is **derived**. An author may disagree; the matrix
  and the study authorities govern, not this reading.
