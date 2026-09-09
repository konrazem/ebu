# Adaptive calibration and topology control — local scientific-design authority

Status: **LOCAL DESIGN AUTHORITY WITH OPEN PREREGISTRATION; NOT EXECUTABLE**.
Authority ID: `ACTC-LOCAL-SCIENTIFIC-DESIGN-v1`.
Source revision: `1e98dacbf1793850b68123ed2f09f88136cfda0c`.

## Scope and precedence

The user authorizes local design for a future Stage F study named **adaptive
calibration and topology control**. This authority records source-derived
mechanism definitions, prospective requirements and unresolved declaration
slots. It is not complete preregistration: no objective, empirical value,
threshold, hypothesis, controller, topology or success claim is selected.
No route ID, campaign position, AWS resource or execution identity is assigned.

The [companion contract](adaptive_calibration_and_topology_control_contract.json)
contains all 25 open decisions and raw-byte source locks. Each scientific value
is explicitly null. It changes no source's scope or precedence. SD-01/SD-10
parameters, controls, seeds, horizons and predicates are not defaults for this
study. The Stage F queue and SD-01 readiness gap remain unchanged.

The separate [SD-01 approval receipt](sd01_static_analysis_approval.json) records
the user's acceptance of the exact independently reviewed static derivation
and ambiguity analysis. No candidate tuple or missing selector is adopted.
The original draft, derivation, checks and review remain byte-identical.

## Derivation of the three distinct mechanisms

| Mechanism | Source-to-definition chain | Missing study binding |
|---|---|---|
| Empirical calibration | CIIF §9 separates exact inversion of a complete fixed table, metric-dependent adjoint sensitivity and estimation from noisy/incomplete data. It requires the estimator's noise, weighting, regularization, identifiability, validation and falsification contract. CIIF §12 locates estimates, uncertainty and versions in scientific state. Thus calibration estimates declared model parameters from admissible empirical observations and retains scientific evidence. | Observations, estimand, information boundary and estimator: D04–D08. |
| Online policy adjustment | CIIF §11 distinguishes diagnosis from physical feedback changing state or the generator. CLCD §4 requires a correction law, gain, delay, saturation and constraints; §14 requires separate correction records. Thus policy adjustment changes a declared bounded policy parameter with a declared dynamical effect and action evidence. | Law, inputs, domains, bounds, cadence and constraints: D09, D11–D12, D16. |
| Bounded topology adaptation | TOPO §3.1 separates structural layers and denies that support alone is a physical edge, measured coefficient or authority. TOPO §9 requires domain meaning; CIIF §17 denies automatic best-topology selection. Thus adaptation applies declared permitted edits or weight actions in a named typed relation domain with explicit bounds and dynamical meaning. | Graph/layer, legal edits, weights, initial state and constraints: D03, D10–D11, D13, D16. |

These are role definitions, not new model equations. A calibrated model
coefficient does not automatically become a controller setting. If a number has
both roles, the estimate and its application need distinct meanings and records.
If a policy changes a link weight, the protocol must identify the coupled
policy/topology action rather than call it an isolated policy intervention.
Whether such overlap is allowed remains D09–D10 and D17.

CIIF's conditional weighted Tikhonov example is not a selected estimator.
Estimation from simulated outputs is not empirical calibration. Stage D's
evidence levels separate derivation, tests, numerical verification, scientific
simulation, empirical observation and independent audited interpretation.
Evidence cannot be promoted merely by relabeling it.

## Reusable topology, dynamics and accounting requirements

TOPO §3.1 defines `Θ=(P,C,O,H,B)`: prerequisites/admissibility; shared-factor
incidence; precedence/concurrency/commutation evidence; structural interaction
support; parent/port/boundary/dependency structure. Layers cannot be collapsed
into an untyped graph. A physical transport network needs its own typed meaning;
structural support is not measured weight, causality or settlement authority.
Cycles forbidden in strict order or provenance DAGs do not imply that all
physical graphs must be acyclic.

Canonical topology schema v1 permits integer numbers only and rejects unknown
fields and floats (TOPO §3.2). Weights need an applicable declared schema or a
separately versioned extension; this document inserts no weight fields into v1.
The exact canonicalizer's supported size is an implementation scope bound, not
this study's graph size or permission for a heuristic fallback (TOPO §3.3).

CIIF §12 and CLCD §4 require typed physical, scientific and correction state,
uncorrected/corrected dynamics, observation maps or named observation processes,
units, clocks, delays and applicability conditions. Fixed-coefficient stability
examples are not adaptive-system bounds. CLCD §10 requires further analysis
for different delays; changing parameters or topology also requires a justified
model-specific argument under D16. No gain interval, Lyapunov function,
switching rule, viability set or threshold is transferred here.

BALANCE §4 supplies the typed account
`y[k+1]-y[k] = S_tilde J[k] + B phi[k]` and residual
`r_q[k] = c_q^T (y[k+1]-y[k]-S_tilde J[k]-B phi[k])`.
The conservation condition `c_q^T S_tilde = 0` applies only to the declared
quantity and internal map. It neither asserts isolation nor chooses a residual
tolerance. BALANCE §4.3 requires a named measurement/numerical tolerance profile.
BALANCE §9 separates physical conservation, represented stock, EBU accounting,
causal attribution and institutional settlement. Stock viability, service
fulfillment and accounting closure cannot silently share an assertion.

All three mechanisms need applicable typed resource/cost records. CLCD §14
requires immutable original and correction receipts, boundary closure, internal
transfers canceled exactly once and no erasure of unexplained residuals. CIIF
§16 permits physical work only with declared conjugate variables, units, signs
and boundary; otherwise use typed action/cost. Neither monetary conversions
nor a scalar optimization objective follow from these definitions.

## Required control arms

The user requires fixed-policy and fixed-topology controls. A fixed-policy arm
holds its declared policy parameters at a registered reference; its output
may still respond to changing observed state. A fixed-topology arm holds its
declared topology, including weights where part of that declaration, at its
registered reference. Whether calibration or another mechanism remains adaptive
in each arm must be specified. These definitions do not choose settings,
a factorial design or an arm count. D17 binds exact configurations and contrasts.

BALANCE §13 requires a common outer boundary, equal external input/service-demand
budgets or explicit normalization, the same initial stored resources and terminal
accounting horizon, all relevant flows, internal cancellation, a declared
residual/observability profile and a falsifier for apparent improvement from
hidden inputs, omitted loss, changed boundaries or incomplete terminal inventory.
D17 must also declare matched calibration exposure and information availability.
No unmeasured difference is evidence of adaptive benefit.

## Open preregistration decisions

Every row is one unresolved declaration slot. IDs have prefix `ACTC-`. No null
is a runtime default and no numerical choice is requested now. Scientific
execution remains blocked until every slot has explicit prospective authority.

| ID / slot | Exact missing decision | Why needed |
|---|---|---|
| ACTC-D01 / `registration` | Which route identity, placement and prerequisite dispositions govern this future study? | The existing queue does not register this named study. |
| ACTC-D02 / `scientific_question_and_claim` | Which falsifiable question and prospective claim, acceptance and inconclusive interpretations will be tested? | A title and mechanism classes do not determine an objective or success predicate. |
| ACTC-D03 / `model_domain` | Which system, typed state, units, boundary, initial-state domain and uncorrected dynamics define the study? | Legal actions and accounting depend on the system and boundary. |
| ACTC-D04 / `observables` | Which observation map or measured quantities, units, resolution, uncertainty, latency and missingness rules are available to each mechanism? | Observation can hide modes; the foundations select no measurement process. |
| ACTC-D05 / `empirical_observations` | Which empirical records and inclusion/provenance rules are admissible for calibration? | No dataset is supplied or authorized for acquisition; simulated data are not empirical observations. |
| ACTC-D06 / `calibration_information_boundary` | Which calibration/validation partition and time-availability rule governs fitting and action inputs? | Independent assessment needs a declared boundary against evaluation or future-data leakage. |
| ACTC-D07 / `calibration_estimand` | Which model parameters are estimated under which identifiable observation-to-parameter model? | An estimated model coefficient is not automatically a policy gain or link weight. |
| ACTC-D08 / `calibration_estimator` | Which estimator, noise, weighting, regularization and uncertainty/validation contract maps observations to estimates? | Exact inversion, sensitivity and estimation are distinct; none is selected here. |
| ACTC-D09 / `policy_actions` | Which policy parameters may change by which update law and available inputs, with which effect on physical dynamics? | A diagnostic or estimate does not specify an intervention. |
| ACTC-D10 / `topology_actions` | Which topology layer or separately typed physical graph may change through which edits or weight updates, with which dynamical meanings? | Structural support does not identify physical edges, measured weights or a best topology. |
| ACTC-D11 / `update_timing` | Which cadence, observation-to-action delay, event ordering and application timing govern the three mechanisms? | Changing delay or update order changes the system; no schedule is supplied. |
| ACTC-D12 / `parameter_bounds` | Which admissible domains and change bounds apply separately to estimates and policy parameters, including constraint/saturation behavior? | Bounded policy adaptation is required but no legal values or bound-handling rule is frozen for this model. |
| ACTC-D13 / `topology_bounds` | Which topology domain, edit/weight bounds and structural invariants constrain topology actions? | No initial graph, legal edge set, weight domain or change budget is supplied. |
| ACTC-D14 / `error_metrics` | Which prediction, control and closure errors, references, units, aggregation and uncertainty treatment define the error metrics? | These errors answer different questions; no common loss or tolerance follows. |
| ACTC-D15 / `cost_metrics` | Which typed resource/cost quantities, ownership, aggregation and comparison rules account for all three mechanisms? | Correction accounting does not select monetary weights or a scalar objective across incompatible units. |
| ACTC-D16 / `stability_viability` | Which model-specific stability/viability constraints and admissibility checks apply to the complete adaptive system and action sequence? | Fixed-gain or fixed-topology results do not establish adaptive stability; closure does not establish viability. |
| ACTC-D17 / `control_arms` | Which exact fixed-policy and fixed-topology arms, reference configurations and matched calibration exposure identify the contrasts? | Both controls are required, but their settings and crossing are absent; a doubly fixed baseline alone cannot separate both adaptive effects. |
| ACTC-D18 / `seeds_and_randomness` | Which deterministic/stochastic declaration, seed set, streams and between-arm coupling will be frozen? | Neither randomness nor seed zero is implied; existing seeds belong to their own studies. |
| ACTC-D19 / `stopping_rules` | Which horizon, stopping rules, terminal classifications and treatment of incomplete/interrupted observations are preregistered? | Other studies cannot supply early-stop criteria or terminal interpretation. |
| ACTC-D20 / `numerical_contract` | Which numerical representation, method, precision, error controls and conformance criteria implement the chosen model and estimator? | Existing matrix/scalar diagnostics and serialization profiles have limited scope. |
| ACTC-D21 / `closure_profile` | Which quantities, boundary flows, residual uncertainty/tolerances and failure dispositions define the accounting profiles? | A typed balance does not select a conserved quantity, completeness assumption or tolerance. |
| ACTC-D22 / `evidence_schema` | Which exact versioned configuration, observation, estimate, action, topology, checkpoint, output and manifest schemas, paths and retention rules realize the evidence? | Conceptual fields are not runtime schemas; applicability and privacy depend on the domain. |
| ACTC-D23 / `recovery_semantics` | Which checkpoint state and resume/restart rules preserve information history and the adaptation schedule after interruption? | Estimates, pending actions, topology versions, clocks and any random state need model-specific recovery. |
| ACTC-D24 / `resource_envelope` | Which compute/storage envelope and hard cost cap bound the registered design? | Sizing requires dimensions, arms, cadence and horizon; another route cap cannot authorize this study. |
| ACTC-D25 / `audit_and_claim_disposition` | Which independent result audit and claim-to-artifact sufficiency rules resolve each future claim? | An evidence ladder does not supply study-specific acceptance or publication authority. |

## Result and evidence requirements

CLCD §12 requires comparative outputs where applicable: trajectories/equilibria,
roots/spectra, damping/frequency/period, mode visibility, named-observable
overshoot, recovery under a declared norm/tolerance, delay sensitivity,
correction action or justified work, physical feedback influence or a justified
nonlinear counterpart, receipt status, closure/residual, dependency invalidation,
numerical errors and failed checks. D03/D16/D22 must preregister applicability;
a spectrum or equilibrium is not meaningful for every adaptive system.

The future evidence declaration must bind source/protocol/configuration
identities, observation provenance and availability, estimate versions and
uncertainty, policy/topology versions, action status, lifecycle times, delays,
pending effects, resource ownership, residuals, dependencies and terminal status
(CIIF §§12,17; CLCD §§4,14–15). A rejected proposal must be distinguishable from an
applied action; admissibility/handling remains D12/D13/D16. These are conceptual
roles, not silently added fields in an existing runtime schema. Exact filenames,
encoding, privacy, retention and required applicability remain D22.

Original and correction records remain immutable with version linkage. In a
declared complete acyclic provenance graph, changed records invalidate or mark
pending reachable dependents. Recalculation uses each accepted protocol and
emits new versions (CLCD §15). An incomplete graph cannot certify outside
records unaffected. This does not authorize recomputation or physical actions now.

Recovery must preserve the estimator history, policy state, topology version,
pending actions, clocks, evidence prefix and any random state needed for replay
(D23). Failures, interruptions and unresolved checks must remain visible. Seeds,
stream coupling and information boundaries must be registered before any draw;
stopping and incomplete-outcome rules before any model advance (D06/D18/D19).
D24 must bind sizing and a hard cap before resource authorization. No AWS
resources, execution command or result destination are selected by this draft.

Stage D's claim traceability is equation → configuration → code → test →
immutable run/trace → table/figure → claim disposition. D25 must instantiate
independent result audit and claim sufficiency without promoting evidence levels.
There are no new scientific results, success claims or publication permissions.

## Locked sources and closure

The JSON pins full commit, raw SHA-256, byte count and locators for every source.
References import only the definitions described above, not another study's
scientific settings or its operational permission.

| Source | Committed file | Locations |
|---|---|---|
| CIIF | [COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW.md](COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW.md) | §9; §11–12; §15–17 |
| TOPO | [CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md](CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md) | §3.1–3.3; §9; §13–14 |
| BALANCE | [CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md](CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md) | §4; §9; §13 |
| CLCD | [CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY.md](CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY.md) | §3–4; §10–12; §14–16; §19–20 |
| CLCD_JSON | [closed_loop_correction_dynamics_milestone_contract.json](closed_loop_correction_dynamics_milestone_contract.json) | /programme_layers; /protocol_schema; /comparative_output_order |
| CLCD_B | [CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY.md](CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY.md) | inert implementation and scientific boundary |
| STAGE_D | [stage_d_scientific_validation_contract.json](stage_d_scientific_validation_contract.json) | /stage_boundary; /evidence_levels; /evidence_nonpromotion_rule; /claim_traceability_chain; /universal_study_fields |
| MATRIX | [stage_d_scientific_validation_master_matrix.json](stage_d_scientific_validation_master_matrix.json) | /studies/9 (SD-10; scope boundary, no numerical inheritance) |
| STAGE_F | [STAGE_F_ROUTE_LEVEL_BINDING_AUTHORITY_CORRECTION.md](STAGE_F_ROUTE_LEVEL_BINDING_AUTHORITY_CORRECTION.md) | Narrow correction; Per-route gate; Dependencies |

All 25 decisions remain unresolved. This document is neither a complete CLCD
protocol nor a Stage F binding packet. A future route needs prospective
scientific closure, registration, appropriate implementation and validation,
independent binding review and separate exact execution authorization. Campaign
dependencies are not bypassed and AWS-C0 is not reopened.

Only source inspection, strict parsing, hashing, document construction, static
cross-reference validation and local Git work were performed for this increment.
No model/runner import, model advance, stochastic draw, outcome inspection,
simulation, AWS action, data acquisition, external communication or publication
occurred. See [validation](ACTC_LOCAL_DESIGN_VALIDATION.md).
