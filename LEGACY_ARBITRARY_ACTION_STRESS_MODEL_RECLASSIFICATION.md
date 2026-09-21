# Reclassification of the arbitrary-action behavioural studies

**Nothing is deleted, amended or reinterpreted.** Every preregistration,
manifest, raw artifact, hash, report and chronology remains exactly as frozen.
This document changes only **which claims those studies are cited for**, and it
does so because the environment they ran in has been corrected, not because
anything in them was done wrongly.

Companion: `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md` (the corrected model),
`DEMAND_DRIVEN_EVIDENCE_STATUS.md` (the consolidated status table).

---

## 1. What changed, and why it matters to these studies

In the studies below, an actor's menu each tick was the set of physically
feasible transfers, filtered by affordability. No demand had to exist for a
transfer to be a candidate. The corrected model admits a transfer into a menu
only when it is part of a complete, irredundant answer to a demand that
actually exists.

This is not a parameter change. It changes the **support of the actor's choice
distribution** and therefore every behavioural quantity measured on it:

- A random actor in the old environment sampled uniformly over feasible
  transfers. In the corrected economy it samples uniformly over
  *demand-serving plans*. These are different distributions over different
  sets, and the second is empty whenever no demand exists.
- A hostile actor in the old environment could pick the single most damaging
  feasible transfer. In the corrected economy it must still answer the
  obligation completely, and may only choose the most damaging *way of doing
  so*. Its reachable damage is bounded by the service contract.
- Idleness in the old environment was a deadlock or an affordability block. In
  the corrected economy the dominant form of inaction is the absence of any
  obligation, which is not a mechanism outcome at all.

So the old behavioural numbers answer a well-posed question about a
**stress-test environment**, and they answer it correctly. They do not answer
the corresponding question about the demand-driven economy, because that
economy's actors never faced those menus.

## 2. The studies

| study | frozen at | status |
|---|---|---|
| Stage A registered study | `STAGE_A_PREREGISTRATION.md`, tag `stage-a-preregistration`, `results/stage_a/` | **VALID HISTORICAL STRESS-TEST RESULT. SUPERSEDED FOR DEMAND-DRIVEN ECONOMIC CLAIMS.** |
| Stage B registered study | `STAGE_B_PREREGISTRATION.md`, tag `stage-b-preregistration`, `results/stage_b/` | as above |
| Homeostasis registered study | `HOMEOSTASIS_STUDY_PREREGISTRATION.md`, tag `homeostasis-preregistration`, `results/homeostasis/` (1,536 jobs, 12,582,912 arm-ticks) | as above |
| Stage-B exploratory homeostasis reanalysis | `STAGE_B_EXPLORATORY_HOMEOSTASIS_REANALYSIS.md` | exploratory, and additionally superseded for demand-driven claims |
| Restoring-drift exploratory analysis | `RESTORING_DRIFT_EXPLORATORY_REPORT.md` | as above |
| Capacity V2 candidate analysis and V2 gate bound | `CAPACITY_V2_CANDIDATE_ANALYSIS.md`, `v2_gate_bound.py` | as above |

"Valid historical stress-test result" is a real status, not a consolation. The
studies were correctly preregistered, correctly executed, exactly audited and
honestly reported, and they remain the authoritative evidence about the model
they ran.

## 3. Claims removed from the active evidence chain

The following claims are **no longer supported by any current evidence**. They
are not refuted; they are untested in the corrected economy.

| claim | previously cited to | now |
|---|---|---|
| EBU-random improves homeostasis in the intended economy | homeostasis study verdict 2 (64/64 paired replicates; `+0.053/+0.030/+0.014`) | **REQUIRES RERUN.** The result stands for the stress model. The corrected menu is a different sampling support. |
| EBU affordability is not a safety mechanism against a hostile actor under legitimate demand | homeostasis study verdict 3 | **REQUIRES RERUN.** The old hostile actor could choose unrelated damage; the corrected one cannot. The adverse finding may strengthen, weaken or reverse, and no direction may be presumed. |
| Capacity V1 fails, or degrades, under legitimate demand | homeostasis verdict 5; Stage-B falsification; `CURRENT_CAPACITY_FAILURE_THEOREMS.md` behavioural parts | **REQUIRES RERUN** for the behavioural part. The *exact* gate-erosion results below are unaffected. |
| Long-run capacity behaviour under demand-conditioned action menus | Stage B; the capacity sweep | **REQUIRES RERUN.** No menu in those studies was demand-conditioned. |
| Absolute homeostasis is absent at every load | homeostasis verdict 4 | **REQUIRES RERUN** as an economic claim; valid as a stress-model claim. |
| The aligned arm attains `O95 = 1` | homeostasis verdict 1 | **Already a theorem, not evidence** (`ENDPOINT_SATURATION_FINDING.md`), and it was registered as such in advance. Its *hypothesis* — forcing amplitude equals the action quantum, so exact reversal is always uniquely maximal and affordable — is **not** satisfied in the demand-driven model, where plans are multi-action and overshoot is permitted. The theorem is preserved; its conclusion does not transfer. |

## 4. What is preserved intact

Per contract section 34, work that does not depend on the action environment is
untouched and remains active. Specifically:

- the Local Gaussian potential, its marginals and curvature;
- exact finite EBU, the quadratic closed form, and the path-integral identity;
- simultaneous group valuation and common-path receipt closure `sum_a R_a = E_G`;
- the Möbius quadratic interaction diagnostic;
- physical conservation and boundary accounting machinery;
- exact rational arithmetic with tolerance zero;
- independence of valuation from capacity;
- the replay and counter-addressed RNG infrastructure;
- locality of valuation.

Also preserved, and explicitly **not** reclassified, are the exact
finite-state results of the restoring-tendency work, because they are
enumerations over a declared state space rather than measurements of a
behavioural process: the 496-state lattice analysis, Theorem R1 (the gate is
inactive once `B_i >= 29`), Theorem R2 (in that regime EBU-random and control
induce identical kernels), the capacity-drift sweep, and the Capacity V2
ceiling bound. These are theorems about *that* action menu. They remain true of
it, and they say nothing about the demand-conditioned menu, which is a
different menu.

The restoring-tendency **definitions** — `dV_actor = -E`, `dV_total`, the drift
objects `D_A` and `D_T`, and the demotion of `H95`/`H99` to occupancy
diagnostics — are model-independent and carry forward unchanged into the
demand-driven programme.

## 5. Chronology and auditability

The record must stay readable as history. For each superseded study the
following remain in place and unmodified: the preregistration and its tag, the
seed manifest, the execution manifest, the raw per-job artifacts, the analysis
output, the registered report including its verdict and its limitations
section, and the commit chronology.

A reader who wants to know what was believed and when can reconstruct it. A
reader who wants to know what is currently supported should read
`DEMAND_DRIVEN_EVIDENCE_STATUS.md`.

## 6. What this document does not do

- It does not claim the old results were wrong.
- It does not predict what the corrected economy will show.
- It does not authorize a rerun. The first demand-driven registered study is a
  candidate only; see `DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md`.
- It does not reinterpret any preregistered outcome. Where a verdict said
  "adverse finding", it still says that, about the model it ran.
