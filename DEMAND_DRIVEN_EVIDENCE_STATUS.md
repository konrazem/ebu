# Current scientific evidence status after the demand-driven correction

**One row per claim. No claim is left ambiguous.** Three statuses are used and
they are mutually exclusive:

- **FOUNDATION STILL ACTIVE** — independent of the action environment; carries
  forward unchanged.
- **HISTORICAL STRESS-TEST ONLY** — correctly established about the
  arbitrary-action model it ran in; not evidence about the demand-driven
  economy; not deleted, not reinterpreted.
- **REQUIRES RERUN UNDER THE DEMAND-DRIVEN MODEL** — the question is open
  again; no direction of result may be presumed.

Companions: `LEGACY_ARBITRARY_ACTION_STRESS_MODEL_RECLASSIFICATION.md`,
`DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md`.

---

## 1. Foundation still active

| claim | source | note |
|---|---|---|
| Local Gaussian Level-1 potential, marginals, diagonal curvature | `gaussian_harness/potential.py` | reused by the new model and cross-checked against it exactly |
| Exact finite EBU `E = V(z) - V(z+delta)` | `gaussian_harness/valuation.py` | definitional |
| Quadratic closed form equals the finite value exactly | conformance, both models | not a first-order approximation |
| Path-integral identity for common-path receipts | conformance, both models | every quadrature rule exact in rationals |
| Simultaneous group valuation `E_G = V(x) - V(x + delta_G)` | contract §8 | |
| Receipt closure `sum_a R_a = E_G` | conformance, both models | exact, tolerance 0 |
| Same-baseline singleton quotes do **not** sum to the group value | conformance | why children are never settled from them |
| Möbius quadratic interaction diagnostic | `gaussian_harness/valuation.py` | diagnostic, issues nothing |
| Physical conservation and boundary accounting | contract §13 | extended with explicit sinks, inside or outside `V` |
| Exact rational arithmetic, tolerance literally zero | both models | |
| Valuation is independent of capacity | metamorphic conformance in both models | structurally enforced |
| Replay determinism and counter-addressed RNG | both models | extended from two streams to four |
| Locality of valuation | both models | |
| Closed-cycle no issuance, and its simultaneous-group extension | `DEMAND_DRIVEN_CLOSED_CYCLE_THEOREM.md` §2 | proved for the corrected model and verified exactly |
| Capacity-source identity `delta B = V(x_0) - V(x_T) + sum dV_ext` | same, §1 | residual 0 in all four arms |
| An economic arrival issues no capacity | same, §5 | an arrival moves no stock |
| Restoring-tendency definitions: `dV_actor = -E`, `dV_total`, `D_A`, `D_T` | `EBU_RESTORING_TENDENCY_FOUNDATION.md` | model-independent; carry forward |
| `H95`/`H99` are occupancy diagnostics, not viability boundaries | same | the demotion stands |
| No Foster-Lyapunov theorem is available, for three independent reasons | same §10 | unchanged; the corrected model does not repair any of the three |
| Gaussian reference region derivation, `d = 2`, exact chi-square quantiles | `GAUSSIAN_HOMEOSTASIS_REFERENCE_REGION.md` | geometry, not behaviour |

## 2. Historical stress-test only

These are valid results about the arbitrary-action environment. They are
preserved with their hashes, preregistrations, manifests and reports intact.

| claim | source | valid about |
|---|---|---|
| Stage A registered outcomes | `STAGE_A_REGISTERED_REPORT.md`, `results/stage_a/` | the Stage-A arbitrary-action world |
| Stage B registered outcomes, including the capacity-erosion falsification | `STAGE_B_REGISTERED_REPORT.md`, `results/stage_b/` | the Stage-B world |
| Homeostasis study: EBU-random beat control 64/64 at every load and menu; `+0.053/+0.030/+0.014` absolute | `HOMEOSTASIS_REGISTERED_REPORT.md` §6.2 | the registered stress world |
| Homeostasis study: hostile reached median `R^2` 258–294 against control 126, and did not return | same §6.3 | same |
| Homeostasis study: no arm achieves absolute homeostasis at any load | same §6.4 | same |
| Homeostasis study: the divergence predicate fired most in the EBU-random arm | same §6.5 | same |
| Aligned `O95 = 1` | `ENDPOINT_SATURATION_FINDING.md` | a **theorem**, whose hypothesis (forcing amplitude = action quantum, exact reversal uniquely maximal) is **not satisfied** in the corrected model |
| Net-zero group corollaries | `NET_ZERO_GROUPS_FINDING.md` | the registered menu; the corrected model's irredundancy rule excludes cancelling pairs from every menu by construction |
| Comparator degeneracy: argmax force ranking coincides with exact EBU on 496/496 states | `HOMEOSTASIS_COMPARATOR_POLICY_REGISTER.md` | that isotropic unit-quantum world |

### Exact results that are theorems about the old menu

Preserved as theorems, true of the menu they quantify over, silent about the
demand-conditioned menu:

| result | source |
|---|---|
| 496-state lattice enumeration; inward-drift fractions by regime | `exact_state_drift.py`, `EBU_RESTORING_TENDENCY_FOUNDATION.md` |
| Theorem R1: the affordability gate is inactive once `B_i >= 29` | same |
| Theorem R2: in that regime EBU-random and control induce identical kernels | same |
| Capacity-drift sweep: mean `g_T` from `-18.425` at `B=0` to `-3.384` at `B=29` | `capacity_drift_sweep.py` |
| Capacity V2 ceiling bound: gate still binds at 418/496 states; hostile `+17.495` | `v2_gate_bound.py` |

## 3. Requires rerun under the demand-driven model

| claim | previously supported by | why it is open again |
|---|---|---|
| EBU-random improves homeostasis in the intended economy | homeostasis §6.2 | the random actor now samples over demand-serving plans, a different support |
| EBU affordability is not a safety mechanism against a hostile actor | homeostasis §6.3 | the corrected hostile actor cannot choose unrelated damage; its reachable damage is bounded by the service contract |
| Capacity V1 degrades as capacity accumulates, under legitimate demand | Stage B, homeostasis §6.5 | the gate-erosion mechanism is exact for the old menu; whether it reproduces when menus are demand-conditioned is untested |
| Long-run capacity behaviour under demand-conditioned menus | Stage B | no menu in any completed study was demand-conditioned |
| Absolute homeostasis is absent at every load | homeostasis §6.4 | as an economic claim only |
| A restoring operating region exists, and where | `RESTORING_DRIFT_EXPLORATORY_REPORT.md` | exploratory, and on the old menu |
| Whether Capacity V2 materially changes hostile safety | `v2_gate_bound.py` | the bound is exact for the old menu; the V1-vs-V2 study candidate predates this correction and its world must be revisited |

## 4. Not evidence at all, and never presented as such

| item | status |
|---|---|
| The demand-driven conformance gate (273 assertions) | conformance. Establishes that the implementation obeys its contract. Says nothing about behaviour. |
| The demand-driven rehearsal (3,200 epochs) | **NON-CONFIRMATORY**. Infrastructure observation only. Not tuned to, not interpreted, not citable. |
| `DEMAND_DRIVEN_MODEL_FINDINGS.md` F-1 to F-4 | structural consequences of the frozen contract, shown exactly on declared fixtures. Not behavioural findings, not generalizable from those fixtures. |
| The `loss-v1` twelve-epoch policy paths | illustrative single deterministic paths on one fixture. Explicitly not evidence about hostile safety or comparator behaviour. |
| The case library | defines questions and environments. Its ledger is **empty**; no case has a recorded run under any mechanism. |

## 5. Summary

Every mathematical result survives the correction. Every behavioural result
survives as a statement about the stress model and none survives as a statement
about the demand-driven economy. The corrected model exists, is conformance-
tested and is deterministic, and no study of it has been designed, frozen or
run.
