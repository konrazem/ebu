# ACTC static decision derivation amendment

Status: **LOCAL STATIC DESIGN ONLY; PREREGISTRATION INCOMPLETE**.
Amendment ID: `ACTC-STATIC-DECISION-DERIVATION-v1`.
Base commit: `dfbc3285781de156f41db86933500cccda95bebf`.
Base tree: `3d9a6d3e476239efb74c23a21d2be90070012879`.

## Scope and classification rule

This additive amendment records one bounded local derivation and review pass
authorized after the base commit. It supplements
[ACTC authority](ADAPTIVE_CALIBRATION_AND_TOPOLOGY_CONTROL_AUTHORITY.md) and its
[contract](adaptive_calibration_and_topology_control_contract.json). Their
historical bytes and all SD-01 records remain unchanged. The three bindings
below apply to future ACTC declarations only under their stated conditions.
They select no model, estimator, controller, topology, threshold, dataset or
route. The adaptive study remains a separate future route with no execution
identity; the existing campaign queue and SD-01 predicates are preserved.

Classify the **complete missing decision** in each original slot:

- **A:** a unique answer follows mechanically from committed, applicable inputs.
- **B:** an applicable frozen source already supplies the complete answer, but
  ACTC has not bound it.
- **C:** at least one prospective study choice remains after all applicable
  source constraints are applied.

C means a genuine new choice needed for scientific preregistration. D01 also
needs registration authority; D22–D24 include evidence, operational and budget
choices. These are not all numerical scientific hypotheses. A filename can be
chosen conventionally, but that does not derive a complete evidence schema;
a cost estimate can become mechanical once its study inputs are declared,
but that does not select a spending cap.

**Whole-slot result: A = 0, B = 0, C = 25.** A compound slot is not closed by
binding one of its constraints. The partial A/B bindings below are recorded
separately so they need not be decided again. All original values remain null
and UNRESOLVED; no null is a default. Choices in the table are prospective
option families within the frozen constraints, not an exhaustive enumeration,
an adopted design, or permission to implement or execute them.

## Exact source citations

The following aliases refer to committed bytes, not mutable external sources.
For CIIF, TOPO, BALANCE, CLCD, CLCD_JSON, CLCD_B, STAGE_D, MATRIX and STAGE_F,
use the exact path, commit, raw SHA-256 and byte count in the base contract's
`/source_manifest` (all at
`1e98dacbf1793850b68123ed2f09f88136cfda0c`). Their bytes are also unchanged at
the base commit. Section and JSON-pointer citations below refine those locks.

`ACTC` means the complete base authority at the base commit, raw SHA-256
`6c347858e89a91557391b893f6a64573b4fa9fc8e0c07ee9aac0dec8154e71ff`.
`ACTC_JSON` means the base contract at the base commit, raw SHA-256
`546f906a77fedf649dfd5651d3cd5e7fab97588ef0f58d08e1cf01b655b414ef`.
Its `/required_preregistration/0` through `/required_preregistration/24`
are respectively D01 through D25. ACTC's “Scope and precedence” prohibits
inheriting SD-01/SD-10 settings. MATRIX `/studies/9/configuration` is explicitly
SD-10's fixed continuous/discrete study, not an ACTC parameter source.

## Smallest source-derived bindings

### ACTC-PB01 — B: exact symbolic closure uses equality

Applies to D20/D21 **if an exact symbolic account is declared**.
BALANCE §4.3, lines 187–199, explicitly requires exact equality for that case.
ACTC's “Reusable topology, dynamics and accounting requirements” currently
names measurement/numerical profiles without spelling out this branch.

Derivation: (1) identify whether the declared account is exact symbolic;
(2) if so, import the source's equality requirement; (3) compare the symbolic
balance exactly. An approximate residual cannot be accepted under that branch.
This is an equality rule, not a newly selected empirical tolerance. Measured or
floating-point accounts still require the full named profile in BALANCE §4.3;
their tolerance and failure disposition remain C. No account type is selected.

### ACTC-PB02 — B: existing topology-v1 size behavior is conditional

Applies to D13/D20/D22 **if CANONICAL_TOPOLOGY_SCHEMA_V1 and its exhaustive
canonicalizer are selected**. TOPO §3.3, lines 123–154, freezes support at
`0 <= n <= 8`, where `n` counts permutable vertices; for `n > 8` the response
is `CANONICAL_TOPOLOGY_SIZE_UNSUPPORTED`, with no heuristic identity.

Derivation: (1) identify the selected identity schema and canonicalizer;
(2) for this existing v1 implementation import its exact supported domain and
failure; (3) refuse to treat an unsupported size as a valid v1 identity.
This binds an existing implementation limit, not the ACTC graph size or edit
budget. TOPO §3.2 still forbids floats and unknown fields in v1. A weighted
physical graph needs its applicable separately declared schema; a differently
versioned extension needs its own prospective authority.

### ACTC-PB03 — A: balance-residual and tolerance dimensions

Applies to D14/D21 **when the BALANCE §4 account is used**. BALANCE §4,
lines 112–167, defines the type-compatible state increment, internal amounts,
boundary amounts and map `c_q` into units of a selected quantity `q`.

Derivation: (1) each summand of
`y[k+1]-y[k]-S_tilde J[k]-B phi[k]` has its declared state-component units;
(2) applying `c_q^T` gives `r_q[k]` in units of `q`; (3) an absolute tolerance
compared directly to that residual must also have units of `q`; (4) a relative
tolerance multiplying a declared scale in units of `q` is dimensionless.
`J[k]` and `phi[k]` are transition amounts, so `r_q[k]` is an amount residual,
not a rate unless a separately declared time normalization is applied. No
quantity, normalization, reference scale, uncertainty or tolerance value follows.

## Remaining decision table

Each row has class C under the whole-slot rule. “Units” describes required
dimensions, not a selection of physical units or a claim of dimensionlessness.
The final column states the unresolved freedom and its exact source basis.

| Decision / slot | Class | Units to declare | Permitted option families, conditional on domain and authority | Scientific consequence | Why no unique committed answer / source |
|---|---|---|---|---|---|
| ACTC-D01 / `registration` | C | Identifiers/order: no physical units | Prospectively register a distinct route with explicit placement and prerequisites; otherwise retain unregistered status | Determines dependency eligibility and the scope of later evidence | Neither a route ID nor placement exists. STAGE_F “Narrow correction”, “Per-route gate”, “Dependencies”; ACTC “Scope and precedence”. |
| ACTC-D02 / `scientific_question_and_claim` | C | Endpoint units from D14/D15; predicates categorical | A bounded predictive-calibration, policy-response or topology-comparison question, or explicitly separated joint claims, with falsifiers and acceptance/inconclusive rules | Determines what a comparison could establish | Mechanism names select no endpoint, effect or success criterion. STAGE_D `/universal_study_fields`; CLCD §19; ACTC_JSON `/required_preregistration/1`. |
| ACTC-D03 / `model_domain` | C | State-component, flow, time and boundary units | CLCD_JSON `/protocol_schema/model_classes`: continuous linear/nonlinear, discrete immediate/one-step delay, or declared extension, with explicit domain evidence | Determines valid interventions, initial conditions and applicable analysis | No ACTC system, equations or boundary selected. CLCD §4; CIIF §12. Existing examples do not supply the domain. |
| ACTC-D04 / `observables` | C | Measurement units, resolution/uncertainty units and latency time | Declared observation map or named measurement process with per-mechanism availability and missingness rules | Determines visible modes, identifiability and action information | No sensor/process/map or uncertainty model selected. CIIF §§11–12; CLCD §§4,11. |
| ACTC-D05 / `empirical_observations` | C | Record quantities from D04; timestamps; counts | Explicitly identified admissible empirical records with inclusion/provenance rules; if unavailable, calibration remains blocked | Determines empirical relevance and selection bias | No dataset or acquisition authority exists; simulated records cannot fill this slot as empirical evidence. CIIF §9; STAGE_D `/evidence_levels`; ACTC “Derivation of the three distinct mechanisms”. |
| ACTC-D06 / `calibration_information_boundary` | C | Time and sample counts; partition labels | Declared held-out or time-ordered assessment design with explicit fitting/action availability; any online validation rule must preserve independent assessment | Determines leakage and validity of comparative assessment | No partition, cutoff or allowed history is supplied. ACTC_JSON `/required_preregistration/5`; CIIF §9; CLCD §4. |
| ACTC-D07 / `calibration_estimand` | C | Units of each model coefficient | A declared identifiable parameter subset of D03 under D04/D05; parameter roles recorded separately from application | Determines meaning and identifiability of estimates | No observation-to-parameter model or parameter subset selected. CIIF §§9,12; ACTC mechanism-role separation. |
| ACTC-D08 / `calibration_estimator` | C | Estimate units; noise/weight/regularizer units consistent with the chosen estimator | A justified estimator with noise, weighting, regularization, uncertainty, validation and falsification contract; the conditional Tikhonov example is only one possible family | Determines bias, uncertainty and reproducibility of inference | Neither estimator nor hyperparameters follow from inversion or sensitivity. CIIF §9, especially the conditional example and final requirement. |
| ACTC-D09 / `policy_actions` | C | Policy-parameter and action units; update-rate units where used | Declared bounded policy updates with available inputs and a defined physical effect; overlap with topology must be explicit | Determines the intervention and attribution of its effects | No update law, target or permitted coupling selected. CIIF §11; CLCD §4; ACTC mechanism-role separation. |
| ACTC-D10 / `topology_actions` | C | Relation labels/counts; declared physical weight units | Edits in a named P/C/O/H/B layer or a separately typed physical graph; weight updates only under an applicable schema | Determines what a changed edge or weight physically/structurally means | Layer meanings do not select a graph, legal edit or dynamics. TOPO §§3.1–3.2,9; CIIF §17.3. |
| ACTC-D11 / `update_timing` | C | Time/ticks; ordered event indices | Explicit periodic or event-conditioned updates with observation/action delays, order and pending-effect rules | Changes the adaptive system and stability conditions | No schedule or ordering follows from fixed-delay examples. CLCD §§4,10; CIIF §15; ACTC_JSON `/required_preregistration/10`. |
| ACTC-D12 / `parameter_bounds` | C | Parameter units; change units or units per time | Declared estimate domains and bounded policy domains, with explicit constraint/saturation handling justified under D16 | Determines legal actions, bias from constraints and viability | No model-specific limits or handling rule is frozen. CLCD §§4,10; ACTC_JSON `/required_preregistration/11`. |
| ACTC-D13 / `topology_bounds` | C | Vertex/edge/edit counts; weight and weight-change units | Declared initial graph, legal relations, structural invariants and bounded edit/weight actions; PB02 applies only to selected existing v1 canonicalization | Determines reachable structures and admissibility | A canonicalizer limit is not a scientific graph domain or change budget. TOPO §§3.1–3.3,9; ACTC_JSON `/required_preregistration/12`. |
| ACTC-D14 / `error_metrics` | C | Prediction/control units or explicitly normalized units; closure quantity units under PB03 | Separately declared prediction, control and closure metrics, references, aggregation and uncertainty treatment | Determines which changes count as error reduction | No common loss, norm, reference or aggregation is fixed. CIIF §§9,16; CLCD §12; BALANCE §§4,9. |
| ACTC-D15 / `cost_metrics` | C | Each typed resource/cost unit; physical work only with conjugate variables | Separate typed accounts; any scalar comparison requires declared compatible conversions/weights and ownership | Determines whether apparent benefit omits burdens or double-counts them | Closure cannot select prices, resource weights or a scalar objective. CIIF §16; CLCD §14; BALANCE §§4,13. |
| ACTC-D16 / `stability_viability` | C | State/norm units, time and admissibility predicates | A model-specific stability/viability argument covering parameter/topology changes, delays, constraints and the allowed action sequence | Determines admissible adaptive behavior and the scope of any stability claim | Fixed-coefficient examples do not cover an unselected adaptive law. CLCD §§9–10,19; BALANCE §9; ACTC reusable requirements. |
| ACTC-D17 / `control_arms` | C | Matched state/resource, input/service, time and information units | Exact configurations containing both fixed-policy and fixed-topology controls; separately declared crossings and calibration exposure, with isolation of the claimed contrasts | Determines whether policy and topology effects can be distinguished | Both control roles are already mandatory, but references, crossing and calibration settings are absent. ACTC “Required control arms”; BALANCE §13. No arm count is derived. |
| ACTC-D18 / `seeds_and_randomness` | C | Seeds/stream IDs: no physical units; variate units by role | Explicit deterministic declaration or preregistered stochastic streams, seeds and between-arm coupling | Determines reproducibility and comparative uncertainty | Neither randomness nor a seed convention is selected. ACTC_JSON `/required_preregistration/17`; MATRIX `/studies/9/configuration` belongs only to SD-10. |
| ACTC-D19 / `stopping_rules` | C | Horizon time/ticks; stopping-metric units | Preregistered horizon and terminal rules, with explicit failure/interruption/incomplete-observation treatment | Determines censoring, terminal comparability and interpretation | No horizon or outcome classification selected; failures cannot be relabeled as passes. CLCD §§4,12; BALANCE §13; ACTC result/evidence requirements. |
| ACTC-D20 / `numerical_contract` | C | Precision representation; step time; error-control units | A method/representation justified for D03/D08 with conformance criteria; exact symbolic accounts obey PB01; selected topology v1 obeys PB02 | Determines numerical validity and applicable error claims | Serialization and inert scalar/matrix diagnostics do not specify an adaptive solver or estimator. CLCD §4; CLCD_B §§6,9–10,19; TOPO §§3.2–3.3. |
| ACTC-D21 / `closure_profile` | C | Selected quantity units; PB03 absolute/relative dimensions | Named physical/represented/accounting profiles; exact symbolic equality under PB01 or explicitly declared measured/numerical tolerances | Determines what closure establishes and how residual failures are treated | No quantity, boundary completeness, uncertainty or tolerance is selected. BALANCE §§4.1–4.3,9; CLCD §14. |
| ACTC-D22 / `evidence_schema` | C | Typed field units, timestamps, bytes and retention time | Versioned schemas preserving the mandatory identities, observations, estimates, actions, topology, outputs and lineage; domain-specific privacy/applicability and exact paths required | Determines whether claims and information histories can be reconstructed | Conceptual roles and existing CLCD protocol fields do not bind an ACTC runtime schema. CIIF §§12,17.1; CLCD §§4,12,14–15; ACTC result/evidence requirements. |
| ACTC-D23 / `recovery_semantics` | C | Clock units, event indices and checkpoint bytes | Replay-preserving resume or explicitly classified restart, retaining estimator/policy/topology history, pending actions and any random state | Determines whether interruption changes the scientific experiment | Replay obligations are fixed, but sufficient checkpoint contents and restart treatment depend on D03/D06/D09–D11/D18/D19. ACTC recovery paragraph; CIIF §12; CLCD §§4,14–15. |
| ACTC-D24 / `resource_envelope` | C | Evaluation counts, time, bytes and cost in a declared currency/unit | Prospective sizing from declared dimensions/arms/cadence/horizon plus an explicitly authorized hard cap; otherwise retain blocked resource status | Determines feasibility and potential resource-driven incompleteness | Missing design dimensions prevent a unique estimate; an estimate does not authorize expenditure. ACTC_JSON `/required_preregistration/23`; STAGE_F “Per-route gate”. Other-route caps are not inherited. |
| ACTC-D25 / `audit_and_claim_disposition` | C | Categorical dispositions; metric units from D02/D14/D15 | Independent reconstruction and claim-specific artifact sufficiency under the frozen evidence ladder, with prospective acceptance/falsified/unresolved interpretations | Determines the strength and reproducibility of each eventual claim | Traceability and nonpromotion are already bound; exact claim tests and sufficient evidence depend on the unselected claims/design. STAGE_D `/stage_boundary/stage_g`, `/claim_traceability_chain`, `/evidence_nonpromotion_rule`, `/universal_study_fields`; ACTC result/evidence requirements. |

## Bounded review and next local task

The local author reviewed each whole-slot classification against its source
constraints and checked the three partial bindings for conditional scope.
No independent review or scientific validation is claimed. In particular:
PB01 does not select a zero empirical tolerance; PB02 does not select eight
vertices; PB03 does not select a conserved quantity. Required control types,
immutable evidence, nonpromotion and stage separation were already bound and
are not newly counted as unresolved decisions or newly closed slots.

The exact next local task is to prepare a **prospective ACTC scientific-choice
packet for D02, D03 and D05**: an explicit falsifiable question and endpoint,
the intended system/equations/typed boundary, and an identified admissible
empirical-data source with provenance and availability. Obtain those scientific
choices from the study authority; do not select them by importing SD-01 or
SD-10 examples. Use the table to state consequences and dependent slots.
No dataset acquisition, controller implementation or execution is part of
that task. Remaining slots can then be revisited against actual declared
inputs; repeated source searches cannot supply these missing study choices.

See [static validation record](ACTC_STATIC_DECISION_DERIVATION_VALIDATION.md)
and [reproduction check](actc_static_decision_derivation_check.py). This
amendment does not seal a binding packet or authorize any later stage.
