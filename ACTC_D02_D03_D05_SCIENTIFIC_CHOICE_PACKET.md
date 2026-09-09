# ACTC D02/D03/D05 — prospective scientific-choice packet

Status: **LOCAL OPTIONS FOR STUDY-AUTHOR DECISION; UNSEALED; NOT EXECUTABLE**.
Packet ID: `ACTC-D02-D03-D05-CHOICES-v1`.
Committed baseline: `531836aab8cdfd52224408e5768d9c0a19d6988a`.
Baseline tree: `f9d2fecf822a54e4acaa5c8a6242cac47a0a3587`.

## Purpose and authority

The smallest useful next input is three complete author declarations: one
primary question and endpoint; one system with equations and typed boundary;
and one identified empirical source with admissibility rules. These are
compound declarations, not three yes/no answers. This packet offers choices
for them without adopting any. All 25 original slots remain null and
UNRESOLVED. Answering these three declarations alone cannot seal the later
study packet or authorize implementation or execution.

The complete [ACTC authority](ADAPTIVE_CALIBRATION_AND_TOPOLOGY_CONTROL_AUTHORITY.md)
and [contract](adaptive_calibration_and_topology_control_contract.json) govern.
The [static decision amendment](ACTC_STATIC_DECISION_DERIVATION_AMENDMENT.md)
classifies every complete slot as C and supplies conditional PB01–PB03.
This packet is additive documentation, not an amendment selecting scientific
values. SD-01, SD-10, the campaign queue and all prior files remain unchanged.

Source aliases below use the exact path, commit, raw SHA-256 and byte count in
ACTC_JSON `/source_manifest`. ACTC and ACTC_JSON mean their committed bytes at
the baseline above; AMEND means the committed amendment there. Specific
locators below refine those identities. New option labels and question
templates are prospective proposals constrained by those sources, not claims
that the sources selected an endpoint, model or dataset.

| Alias | Committed source and principal locators used here |
|---|---|
| ACTC_JSON | [ACTC contract](adaptive_calibration_and_topology_control_contract.json), `/required_preregistration/1`, `/required_preregistration/2`, `/required_preregistration/4` (D02, D03, D05), and dependent slots |
| CIIF | [Inference and feedback review](COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW.md), §§9–12, 16–17 |
| CLCD | [Correction dynamics authority](CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY.md), §§4, 10–12, 14, 19 |
| CLCD_JSON | [Correction dynamics contract](closed_loop_correction_dynamics_milestone_contract.json), `/protocol_schema` |
| TOPO | [Topology foundation](CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md), §§3.1–3.3, 9 |
| BALANCE | [Boundary accounting foundation](CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md), §§3–4, 9, 13 |
| STAGE_D | [Scientific validation contract](stage_d_scientific_validation_contract.json), `/universal_study_fields`, `/evidence_levels`, `/evidence_nonpromotion_rule`, `/claim_traceability_chain`, `/stage_boundary` |

No recommended scientific default is justified by these committed sources.
Every option below is unselected. Options across the three declarations are
compatible only when their stated observation, domain and attribution
conditions hold. Alternatives within a table are choices, not instructions
to combine incompatible accounts or create multiple primary endpoints.

## Declaration 1 — D02: one primary question and one endpoint

Choose one row and complete its named quantities. Each row supplies a
falsifiable question template and a candidate single endpoint; no row is the
adopted question. Prediction, control performance and accounting closure
remain separate. The claim applies only to the declared system, information
boundary, conditions and comparison, never to universal adaptive benefit.

| Option | Primary question and candidate endpoint | Units and author-supplied definition | Consequence and dependencies |
|---|---|---|---|
| Q1 — predictive calibration | Does empirical parameter calibration reduce the mean absolute prediction error of **[one measured observable]** against **[one registered reference configuration]** on **[independent assessment records]**, according to **[author's claim rule]**? Candidate endpoint: mean absolute prediction error over the declared assessment records. | Same units as the named observable; author names the prediction target, forecast lead, assessment set, missing-record handling and between-arm aggregation. The mean-absolute choice is a proposed endpoint, not a CIIF requirement. | Tests predictive accuracy, not physical benefit or causal effectiveness. Requires D03–D08, D14, D17–D19 and D25. Calibration exposure and policy/topology differences must allow attribution of this contrast. Basis: CIIF §9; ACTC mechanisms and controls; AMEND D02. |
| Q2 — policy response | Does bounded online policy adjustment reduce peak overshoot of **[one observable relative to one declared reference]** against **[fixed-policy control]** under **[declared conditions]**, according to **[author's claim rule]**? Candidate endpoint: peak overshoot of that observable. | Observable units; author defines direction, reference, observation window, initial-state domain and aggregation across comparisons. No percentage normalization or overshoot sign convention is assumed. | Tests a named response, not all stability properties. Topology/calibration behavior must be matched or explicitly isolated. Requires D03–D04, D09–D12, D14, D16–D19 and D25; D05–D08 for calibration. Basis: CLCD §§10–12; CIIF §16; ACTC controls. |
| Q3 — topology response | Does bounded topology adaptation reduce recovery time of **[one named observable]** against **[fixed-topology control]** after **[declared condition]**, according to **[author's claim rule]**? Candidate endpoint: recovery duration under one declared recovery definition. | Declared time unit; author defines reference, norm, tolerance, entry/persistence rule, starting event, horizon, non-recovery handling and aggregation. No tolerance, horizon or duration is selected. | Tests recovery for the named conditions, not a best topology or physical conservation. Policy/calibration behavior must be matched or explicitly isolated. Requires D03–D04, D10–D14, D16–D19 and D25; D05–D09 for other mechanisms. Basis: CLCD §§10, 12; CIIF §16; TOPO §9; ACTC controls. |

These questions can be falsified by a valid comparison that contradicts the
author's registered endpoint claim. That sentence supplies no acceptance
threshold or statistical decision rule. The author must select and write the
full rule before D02 can close. Two compatible rule families are:

| Option | Units | Consequence and dependency |
|---|---|---|
| I1 — directional claim | Endpoint-contrast units; uncertainty and categorical dispositions separately declared | Ask whether the endpoint changes in the claimed direction. Author supplies the exact contrast, uncertainty procedure and mutually exclusive acceptance/falsified/inconclusive predicates. Does not establish a minimum practically meaningful benefit. Depends on D14, D17–D19, D25. |
| I2 — minimum meaningful benefit | A prospectively supplied margin in endpoint units, or a justified dimensionless normalization with its reference scale | Ask whether benefit reaches an author-justified margin. Author supplies its value and rationale as well as uncertainty and all three disposition predicates. Needs a domain justification absent from committed sources. Same dependencies as I1. |

I1/I2 are proposed ways to complete the open claim slot, not committed
interpretation rules. Neither is preferred. Failed, incomplete, interrupted
or unresolved evidence cannot be described as a pass; exact treatment remains
the author's D19/D25 declaration (ACTC result requirements; STAGE_D evidence
nonpromotion). Accounting or matching failures cannot become adaptive benefit.

Both fixed-policy and fixed-topology controls are already mandatory for every
row. Fixed policy means fixed policy parameters, not constant output. Fixed
topology includes weights if they are part of its declaration. D17 must still
name exact configurations, reference values, calibration exposure and the
primary contrast; the other required control remains present even when it is
not the primary comparator. No arm count or factorial design follows. A
single doubly fixed baseline cannot isolate both adaptive effects. Joint
claims or multiple primary endpoints require a separately declared expanded
design; they are outside this requested single-primary-question packet.

## Declaration 2 — D03: system, equations and typed boundary

Name the real or represented system first. A model class is not a system
identity, a fitted model or evidence that its equations describe that system.
CLCD_JSON `/protocol_schema/model_classes` permits the following grouped
options. A family selection must include the indicated subtype; it does not
complete D03 without explicit equations and their domain evidence.

| Option | Permitted equation family | Units | Consequence and dependencies |
|---|---|---|---|
| M1 — continuous | Specify `CONTINUOUS_LINEAR` or `CONTINUOUS_NONLINEAR`. CIIF §11 supplies the linear forms `dx/dt = A x` and `d[x;c]/dt = K[x;c]`, `K = [[A,B],[C,D]]`; §10.2 supplies the general uncorrected form `de/dt = f(e)`. Author must supply the actual equations, inputs and adaptive coupling; these forms select none. | Each derivative has its state-component units per declared time. Linear entry `(i,j)` has output-state units divided by input-state units and time. Nonlinear terms require the same dimensional compatibility. | Linear fixed-coefficient formulas apply only under their assumptions. A nonlinear or time-varying adaptive law needs its own justified analysis. D04, D07–D13, D16, D20 and D23 depend on the actual equations. |
| M2 — discrete | Specify `DISCRETE_IMMEDIATE` or `DISCRETE_ONE_STEP_DELAY`. Declare full uncorrected/corrected updates, sample interval and available history. CLCD §10's scalar immediate/delayed recurrences are examples of these classes, not ACTC equations or gains. | Update outputs have state-component units; tick index counts updates, and tick duration has a declared time unit. Delay history retains typed state units. | The subtypes differ in state/history and action timing. No scalar stability interval transfers to an adaptive system. Same dependencies as M1, with D11 and D23 explicitly covering pending effects/history. |
| M3 — separately declared extension | Specify `DECLARED_EXTENSION`, its exact identity, equations and justification if M1/M2 do not represent the intended system. This is a prospective declaration path, not approval of an unnamed hybrid, delay or switching model. | Full component, time, input and coefficient units must be supplied; mixed clocks require explicit mappings. | Additional domain/applicability and stability arguments are required before use. D04, D07–D13, D16, D20, D22–D23 cannot inherit support from existing diagnostics. |

Now select the intended boundary/account level. These alternatives may be
used with any equation family when the physical assumptions hold; levels
must not be exchanged to obtain a stronger interpretation. Separate accounts
may coexist only with explicit boundaries and meanings (BALANCE §§3, 9).

| Option | Typed boundary declaration | Units | Consequence and dependencies |
|---|---|---|---|
| B1 — represented stock | Name represented coordinates and every modeled source/outflow; list omitted destinations, reservoirs and conversions. | A declared unit per stock coordinate; transfer amounts compatible with those coordinates. | Can support a represented-stock closure claim only. Does not assert physically complete inventory or isolation. Requires D04, D14–D17, D21–D22. Basis: BALANCE §§3.1, 4. |
| B2 — open control volume | Name the outer boundary, internal transformations and exchanges across it, including correction flows relevant to the question. | Typed inventories and exchange amounts; rates need a declared time basis and conversion to transition amounts. | Can support closure for the stated inventory and exchanges; does not establish isolation or completeness beyond that declaration. Same dependencies as B1. Basis: BALANCE §§3.2, 4.1. |
| B3 — isolated physical system | Identify the physical quantity, all relevant carrier forms and evidence of zero external exchange for that quantity. | Quantity-specific inventory/transfer units and explicit compatible mappings across carriers. | Admissible only with physical completeness and isolation established. Conservation alone cannot imply stability, efficiency or service success. Same dependencies as B1, with stronger boundary evidence. Basis: BALANCE §§3.3, 4.2. |

For a BALANCE §4 account, retain exactly the typed structure
`y[k+1]-y[k] = S_tilde J[k] + B phi[k]` and
`r_q[k] = c_q^T (y[k+1]-y[k]-S_tilde J[k]-B phi[k])`.
Here `J[k]` and `phi[k]` are transition amounts. For M1, the author must declare
how continuous flows supply interval amounts; this account is not a solver
or a continuous dynamics equation. The symbol `B` here is a boundary map,
not CIIF's feedback block, and accounting `y` is not automatically an
observation variable. Name those roles separately in the eventual model.

AMEND PB03 fixes only dimensions: `r_q` and its absolute tolerance have units
of the selected quantity; a relative tolerance multiplying a declared
quantity scale is dimensionless. No quantity, scale or tolerance is selected.
PB01 requires exact equality if an exact symbolic account is selected;
measured/numerical profiles still need all BALANCE §4.3 declarations. An
exact symbolic ledger does not eliminate empirical measurement uncertainty.

Specify topology meaning within this same system declaration:

| Option | Typed relation | Units | Consequence and dependencies |
|---|---|---|---|
| T1 — structural layer | Name the affected layer(s) of `Theta=(P,C,O,H,B)` and each relation's meaning: prerequisites, shared-factor incidence, order, interaction support, or parent/port/boundary/dependency structure. | Relation labels/counts and fixed semantic unit annotations; no physical weight unit follows from support. | Must explain how a permitted structural edit affects the declared dynamics before claiming response benefit. Requires D09–D10, D13, D16–D17, D20, D22. Basis: TOPO §§3.1–3.3, 9. |
| T2 — physical relation graph | Declare a separately typed physical graph, vertex/edge meanings, measured or modeled coefficient roles and applicable weight schema. If structural topology is also used, explicitly map the two. | Physical weight and weight-change units from the equations; relation counts separately. | Physical connectivity is not inferred from structural support. Policy updates that change link weights need coupled-action attribution. Same dependencies as T1. Basis: ACTC mechanisms and topology requirements; TOPO §§3.1–3.2, 9. |

T1 and T2 can coexist as separate typed objects; they cannot be collapsed into
one untyped graph. Existing topology v1 forbids floats and unknown fields.
AMEND PB02 applies only if its existing exhaustive canonicalizer is selected:
`0 <= n <= 8` permutable vertices; larger inputs yield
`CANONICAL_TOPOLOGY_SIZE_UNSUPPORTED`, with no heuristic identity. This does
not choose graph size. Weights or another identity domain require an
applicable separately declared schema or prospectively authorized extension.

To complete this declaration the author supplies system identity, intended
domain evidence, selected M subtype/B/T options, typed physical/scientific/
correction state (CIIF §12), units/signs, full uncorrected dynamics, initial-state
domain including required history, external inputs and boundary terms.
Identify how calibration parameters, policy settings and topology enter the
model without identifying them with one another. Exact laws, bounds and timing
remain dependent D07–D13 declarations, not defaults hidden in this packet.

## Declaration 3 — D05: empirical source and admissibility

The committed ACTC authority identifies no empirical dataset and authorizes
no acquisition. No records were acquired or inspected for this packet.
Accordingly the following are admissibility paths, not verified available
datasets. A source category alone cannot close D05. Choosing a named source
also does not authorize its acquisition or analysis in this task.

| Option | Source path and admissibility condition | Units | Consequence and dependencies |
|---|---|---|---|
| E1 — existing author-controlled observations | Author identifies existing empirical records from the intended system, their custodian, stable version and authorized availability. Include only prospectively defined records with traceable observation provenance. | Recorded observable units, resolution/uncertainty units, observation and release times, sample counts. | Potentially direct domain match; access, missingness, selection and independent assessment still need explicit rules. D03–D04, D06–D08, D17, D22 and D25 depend on these metadata. |
| E2 — existing external observational archive | Author identifies a particular versioned empirical archive, provider and lawful access route, with documented measurement process and relevance to the chosen system. A public label alone is insufficient. | Source units and documented conversions to D04; timestamps, resolution/uncertainty and counts as for E1. | May improve reproducibility of access, but domain transfer and measurement mismatch require justification; observational records alone do not identify intervention effects. Same dependencies as E1. |
| E3 — prospective empirical collection | Author names the intended measurement source/custodian and proposed collection protocol if existing records cannot meet the question. Record that availability is pending. | Prospective measured quantities and instrument/time units; no invented sample size, measurement accuracy or collected values. | Requires separate acquisition authority and eventual provenance/availability evidence. D05 remains incomplete while records are unavailable; calibration and empirical claims remain blocked. Adds collection feasibility dependencies to D04, D06–D08, D22 and D24. |

All three paths derive their restrictions from ACTC D05–D08 and its calibration
definition, CIIF §9, TOPO §9 (domain responsibility), and STAGE_D's empirical
observation level and nonpromotion rule. These sources do not endorse a
specific archive or promise access. Synthetic or simulated observations,
including outputs of another EBU study, cannot replace empirical records.
Empirical calibration of a simulation also does not promote its later outputs
from scientific simulation to empirical observation or audited interpretation.

The D05 author declaration must name the source/custodian and exact release
or record identity; provenance from actual measurement; population/system,
coverage and time range; available variables and units; permitted access/use;
and inclusion/exclusion criteria with reasons. State known resolution,
uncertainty, missingness and observation/release latency, or explicitly mark
them unknown and identify what evidence is needed. Unknown metadata are not
zero uncertainty, complete coverage or instantaneous availability.

Specify which records can inform calibration and when they become available;
identify an independent assessment source/partition for later D06 binding.
The smallest compatible information-boundary choices are a declared held-out
partition or time-ordered assessment with explicit historical availability
(AMEND D06). Partition labels have no physical units; cutoffs have time units
and sample sizes are counts. Held-out assessment requires justified separation
and applicability; time-ordered assessment must prevent future-data leakage.
Neither selects split sizes, cutoffs or an online validation algorithm. Final
selection and details remain D06 and must match exposure across D17 arms.

## Compatibility and what remains before sealing

The menu is not a guaranteed Cartesian product. Every Q option requires
observable support in D04/D05 and an identifiable calibration model in D07.
Q2 needs a meaningful overshoot reference; Q3 needs a meaningful recovery
event and norm. Continuous and discrete systems can support either when
their definitions and clocks are explicit. A structural T1 edit without a
declared dynamical effect cannot support a policy/topology response claim.
B3 cannot accompany material external exchange of its allegedly isolated
quantity. Any E path must match the chosen system or supply domain-transfer
justification; E3 cannot presently support a completed empirical binding.

No control comparison may change the outer boundary, initial stored resources
or terminal accounting horizon to claim improvement. External input and
service-demand budgets must match or use declared normalization; relevant
flows, correction costs, internal cancellation, residual/observability limits
and hidden-input/omitted-loss falsifiers are required (BALANCE §13; ACTC
controls). Separate typed costs remain required even if the primary endpoint
is not a cost metric. No scalar trade-off weights follow.

| Author input now | Dependent work enabled, not resolved |
|---|---|
| D02 question, endpoint and claim-rule declaration | D14–D15 metric/cost definitions; D17 contrast; D19 terminal treatment; D25 claim-specific sufficiency and independent audit |
| D03 system, equations, units, boundary and topology meaning | D04 observables; D07–D13 estimand/action/timing/bounds; D16 adaptive stability/viability; D20–D23 numerics, closure, evidence and recovery |
| D05 named empirical source and admission/availability declaration | D04 measurement contract; D06 partition/availability; D07–D08 identifiability/estimator; D17 matched exposure; D22 provenance/privacy/retention; D24 feasibility |

Thus three declarations are the minimum first decision set, not sufficient
authority for a seal. Every slot must subsequently be explicitly resolved:
D01 registration; D04 observables; D06–D08 information/estimand/estimator;
D09–D13 policy/topology actions, timing and bounds; D14–D16 metrics, costs and
adaptive stability/viability; D17–D19 controls, randomness and stopping;
D20–D24 numerical/closure/evidence/recovery/resource contracts; D25 independent
audit and claim disposition. No slot closes merely because it has a dependency
or a mechanically derivable subfield. D02/D03/D05 themselves stay open until
their complete author declarations and cross-slot requirements are explicit.

The later binding packet requires prospective closure, appropriate registration,
implementation and validation stages and independent binding review under ACTC
and Stage F authority. Sealing is not execution permission. No implementation,
scientific validation, execution, interpretation or publication stage begins
here. See the [static validation record](ACTC_D02_D03_D05_CHOICE_VALIDATION.md).

## Plain-English choices and exact next task

1. **What should the study test?** Choose prediction accuracy (Q1), policy
   overshoot (Q2), or topology recovery time (Q3); name one endpoint and primary
   comparator, and supply the claim rule (I1 or I2 with full dispositions).
2. **What system does it describe?** Name the system and equations; select
   continuous/discrete/extension and its subtype (M), represented/open/isolated
   boundary (B), and structural/physical topology meaning (T); supply units,
   initial-state domain, inputs and domain evidence.
3. **Which real measurements may it use?** Identify author-held records (E1),
   a specific external archive/version (E2), or a pending collection (E3),
   with provenance, admissibility and availability. Missing records keep
   empirical calibration blocked.

**Next exact task:** obtain these three completed declarations from the study
author, then prepare a local, additive D02/D03/D05 decision receipt citing this
baseline and the exact author answers. Statically check their compatibility
and record which dependent slots remain unresolved. Do not seal the study,
acquire data, implement a controller or execute scientific behavior in that
receipt task. The decision receipt has not begun.
