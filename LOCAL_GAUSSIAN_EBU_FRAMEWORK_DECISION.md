# Local Gaussian programme — framework decision

Status: **F2 adopted for planning only: reuse generic infrastructure and adapt or
isolate the scientific execution layers in a later authorized stage**.

No framework replacement, package import, code refactor, Gaussian implementation,
capacity mechanism, simulation or test execution is authorized by this decision.
See [CURRENT_SCIENTIFIC_AUTHORITY.md](CURRENT_SCIENTIFIC_AUTHORITY.md) and
[the baseline decision](GAUSSIAN_EBU_BASELINE_DECISION.md).

## 1. Question and decision

The existing `ebu-framework` contains useful immutable scientific objects,
identity/provenance machinery, typed boundaries, action/support declarations,
receipt separation and fail-closed execution gates. It is not fundamentally a
hinge-potential or service-optimizing controller framework.

It cannot run the proposed Gaussian programme unchanged: its scientific runtime
is deliberately unavailable, its imported event order differs, and no accepted
Gaussian action-owner/capacity contract exists. The appropriate disposition is
therefore **F2**, not a claim that existing runtime is already sufficient (F1)
and not an evidence-supported need to create a replacement framework (F3).

F2 here means preserving the generic core and historical semantics while
planning the smallest separately versioned domain adapters, event profile and
accounting services. It is not permission to bypass existing guards, rewrite
frozen interfaces or import every historical authority dependency into a new
study automatically.

## 2. Exact source locks

| Role | Source identity |
| --- | --- |
| Reconciliation parent | `924a4d9a801b96f265aa3f0adc40e2c09063e469` (tree `8f07ec999b40248ac0edcf25faf0bb6f92ef4705`) |
| Framework audit source | `a4af44afd3c878311ee373bc19e3be14b2aacec5`, cached `origin/framework-v0.1` at inspection |
| Framework package subtree | `4de85ed2935d1c35bdcc0f1259f0acb2df569fdd` |
| Independent matching package source | `660d6e5a56cb096fe6d1e4d202f592155d982c79`, cached `origin/main`; same package subtree |
| Framework specification blob | `fbcceb0ce05f6d98f345658cf4cd6a86f1789334` at both cached origin sources and local framework `4ab6f9ca…` |
| I-3C repaired settlement implementation | `4b4fc4a7012f8519b7b4caad6fc593e27db1c828` |
| I-3C repair integration | `a99319a1a420413bb4a88156a7218e113712da99` |
| Repaired `settlement.py` blob at inspected framework/main sources | `3c698e9b22995c7895cd7c1c79bc12d8f1d4e660` |

Unless stated otherwise, source paths below refer to the framework audit commit,
not files present in this checkout. They can be read without switching branches
using `git show <locked-commit>:<path>`. Remote-tracking state was not refreshed
over the network.

Source status must be reconstructed from implementation and Git history as well
as document headers. An authority document can correctly preserve the historical
stage at which it was written while its header is no longer a current global
implementation-status summary.

## 3. Preserved architectural principle

`UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` §1 separates physical
measurement, causal inference, policy choice and institutional settlement.
Section 3.2 separately types physical state, topology, policy, objective family,
constraints, measurement and institutional allocation. These principles fit
the new direction:

**EBU calculates; actors choose.**

The programme's affordability filter may depend on a computed receipt. That
does not make random actor selection an EBU maximizer. Equally, this distinction
does not make the receipt-to-capacity rule a consequence of an accounting
identity. That rule remains a declared prospective model component.

## 4. Source-level module and reuse map

| Responsibility | Existing evidence | Planning disposition and limit |
| --- | --- | --- |
| Identity, canonical bytes, numeric types and provenance | `identity.py`, `canonical.py`, `numeric.py`, `envelopes.py`, `hashing.py`, `registry.py` | Reuse immutable versioned records and explicit hash domains; do not introduce a parallel identity system |
| State and projection | `state.py:SystemState` (line 144), `RepresentedState` (212), `ProjectionContract` (276) | Generic schemas do not require L/U bands; use a separate Gaussian domain schema and keep nonphysical accounts distinct |
| Potential metadata | `distortion.py:DistortionModel`, `validate_distortion_model` | Already model-agnostic declaration; a potential evaluator/support adapter is still missing |
| Actions and supports | `actions.py:ActionDefinition` (200), `ActionInstance` (274), `WriteSupport`, `ConstraintSupport` | Reuse finite action declarations, typed quantities and supports; do not infer settlement ownership |
| Topology | `network.py:ProviderNetwork`, typed nodes/edges and capacity loci | Reuse physical network declarations; factor topology and action-interaction topology remain different objects |
| Conservation | `conservation.py:ConservationProfile` (139), account levels, exact/uncertainty residual expectations and validators | Reuse dimensional/boundary declarations; do not describe declaration validation as physical runtime closure |
| Physical service capacity | `commitments.py:CapacityRecord` (185), reservations/admission/queues | Preserve existing meaning; these are not earned EBU balances |
| Events and exactly-once effects | `events.py:EventKey`, `PhaseOrdinal`, `PhaseCommitRecord`; `ownership.py` | Reuse common-baseline/provenance ideas; the imported phase meaning requires explicit Gaussian-profile reconciliation |
| Policy information | `policy.py:InformationContract`, `InformationView`, `InformationReadSet`, `PolicyMemoryState` | Reuse declared information boundaries and replay records; not an absolute runtime-security proof |
| Joint-group measurement | `bridge.py:JointTransitionGroup`, `GroupMeasurement`, `SameBaselineNonadditivity`, `ComparatorInteraction` | Preserve group/endpoint/comparator distinctions; scientific callable routes remain unavailable |
| Mathematical decomposition | `interaction.py:ScalarDecompositionWitness` (858) | Reuse an explicit path and nonclaim record; mathematical shares alone are not earned/spendable capacity |
| Settlement separation | `settlement.py:Receipt`, `GroupReceipt`, `ChildActionRecord`, `SettlementShare`, `GroupResidual`, `validate_settlement_closure` | Preserve physical/causal/share separation and exact closure; new credit rule and beneficiary map require explicit authority |
| Ledger structure | `ledger.py:Ledger`, `LedgerEntry` | Reuse immutable ordered references; not an implemented balance/overdraft engine |
| Scientific configuration vs execution | `experiment.py:ExperimentConfiguration`, `ExecutionBinding`; authorization modules | Preserve separate scientific choices, execution identity and workflow permission |
| Audit/recovery | `traces.py`, `artifacts.py`, `durability.py`, `provenance.py`, `recovery.py`, `publication.py` | Reuse provenance and completeness contracts without assuming every real backend or scientific route is available |
| Random-stream arithmetic | `stage_e_harness/rng.py:Counter`, `exact_residue`, `categorical`, `bernoulli` | Candidate later reuse of addressed hash draws; Gaussian stream ownership/pairing is not supplied by this implementation |
| Scientific advancement | `execution.py:validate_t3_entry_guard`, `commit_phase_updates`, `advance_epoch` | Deliberately fail-closed; no runnable Gaussian engine is present |

### 4.1 What the potential module actually implements

`DistortionModel` has a domain schema, boundary, parameter references, codomain,
domain predicate, evaluation contract, numerical policy and scientific status.
Its file exports only `DistortionModel` and `validate_distortion_model`.
It neither hard-codes the hinge potential nor implements a generic numerical
`evaluate_distortion` function. Thus the existing declaration can describe a
new potential, but numerical Gaussian value/gradient/support evaluation is
future work.

### 4.2 What the execution modules actually implement

In `execution.py`, `validate_t3_entry_guard` reaches
`REAL_DURABILITY_BACKEND_UNAVAILABLE`; `advance_epoch` and
`commit_phase_updates` contain fail-closed scientific-advancement bodies.
In `bridge.py`, `_consume_bridge_execution_permit` refuses, and the scientific
`classify_joint_groups`/`compute_group_measurement` routes require that permit.
The separately named fixture routes are capability-scoped to frozen fixtures.

These are implemented guards and declarations, not absent software. They also
are not working scientific execution merely because their callable names exist.
No later adapter may call a private fixture helper to bypass this boundary.

## 5. Required authority reconciliations before dependent implementation

### F2-A — event ordering

Specification §3.3 imports the Dynamic Coordination foundation's ten-phase order
unchanged. Policy proposal precedes screening/admission, grouping follows
admission, and natural drive is phase 10. `events.py:PhaseOrdinal` retains the
ten ordinal slots. A replacement requires a prospective foundation revision or
an authority the foundation explicitly recognizes; configurations cannot reorder
the phases ad hoc.

The new programme requires external forcing first, followed by a frozen physical
state, EBU-blind candidate generation, joint physical feasibility, exact EBU/path
values, capacity affordability, random choice, execution, settlement and audit.

Record a separately named Gaussian event profile with exact precedence and
legacy-preservation boundaries before runtime implementation. Do not claim that
publishing a new diagram has already changed the historical phase contract, or
that renaming end-of-epoch natural drive supplies the new semantics.

### F2-B — action ownership and capacity eligibility

Specification §6.3 states that `requesting_actor_ref` is not causal credit and
`responsible_provider_ref` is not a settlement share. Neither field defines the
new `owner(a)` automatically. The experiment must explicitly define which cell
owns which action, how each action has exactly one owner, and how valid receipts
are aggregated for that owner.

The new intended same-event owner-level netting rule must be distinguished from
per-action pre-funding, global pooling and sequential debit order. Its arithmetic
can be written now as a prospective definition; its adoption cannot be inferred
from existing `ActionInstance` fields or from receipt closure. This audit found
no general capacity update implementation that settles that choice for the new
programme.

### F2-C — common-path attribution and spendability

Atomic Foundation F12 (`ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md`
§7) treats radial Aumann–Shapley decomposition as an optional path-dependent
mathematical decomposition. Closure does not establish causal identification,
physical observation, ownership or settlement entitlement.

The checkpointed `ebu_test_settlement.py` already distinguishes
`model_realised_constant_rate` from `endpoint_interpolation`.
`SimultaneousPathFieldAttribution` explicitly refuses settlement and ownership
readings for simultaneous groups. The new proposal may define a model-realised
constant-rate group path, but that must be a declared physical-model assumption,
not an inference from matching endpoints.

The Gaussian common-path formula and its sum identity can be analysed as
mathematics under explicit assumptions. Crediting the resulting numbers to
persistent spendable capacity is an additional prospective rule. Renaming the
amount from wallet credit to EBU capacity does not remove the need to declare
that rule and its scope. The new rule must not retroactively change historical
receipt meanings or be advertised as a theorem of fair/causal attribution.

The checkpointed single-action shortcut in
`SimultaneousPathFieldAttribution.require_reading` returns arbitrary readings
when `group_size <= 1`. Do not reuse this shortcut as authority for ownership or
credit: having no splitting problem does not prove those meanings. No repair to
that preserved candidate code is made in this reconciliation stage.

### F2-D — I-3C status correction: implemented repair, not an adopted Gaussian rule

The I-3C repair amendment's opening status still says documentation-only and
unimplemented. That was its authoring-stage boundary, not the final status of
every later branch.

The object database records:

- implementation `4b4fc4a7012f8519b7b4caad6fc593e27db1c828`;
- integration `a99319a1a420413bb4a88156a7218e113712da99`;
- repaired `settlement.py` at the inspected framework sources.

The implemented validator sums supplied share amounts, checks explicit
share-plus-residual closure, and rejects causal-contribution links when either
supplied causal status is not identified. It no longer rejects a valid
noncausal settlement merely because shares exist. The independent rule/causal
typing requirement remains; opaque references do not prove legitimate authority.

Consequently, both statements would be wrong:

1. “The I-3C repair is still unimplemented everywhere.”
2. “The repair authorizes Gaussian common-path values as spendable capacity.”

The repair is implemented on the framework lineage, absent with that package
from this current checkout, and scientifically narrower than the proposed new
capacity mechanism. Preserve the amendment bytes and report its later history
instead of rewriting its historical status text.

### F2-E — capacity is not physical service capacity or physical stock

`commitments.py:CapacityRecord` contains installed, available/usable, reserved,
admitted and completed physical/service quantities. It cannot be repurposed as
`B_i` without changing its meaning. `ledger.py` similarly defines ordered
entries, not earning/spending/nonnegative-balance behavior.

Keep the proposed replay objects distinct:

- physical resource state `x`;
- persistent local EBU capacity `B`;
- signed external-deviation audit ledger `J`;
- random-stream replay coordinates.

Link their versions and updates in a composite event record rather than making
capacity a physical conserved carrier. `J` is audit-only, not transferable,
spendable or a source of direct actor issuance.

### F2-F — stochastic scope and pairing

Specification §§8.1 and 8.12 reserve stochastic execution for a separately
defined stream, distribution, generator and replay contract. UQ-23/UQ-24 identify
stream ownership and cross-arm common-random-number pairing as scientific
choices.

Stage E's counter-hash implementation exposes `stream_id`, tick, event, draw and
attempt coordinates. It is a useful arithmetic candidate, not a ready Gaussian
forcing law. The later study must distinguish an identical raw exogenous draw
sequence from an identical realised forcing increment when physical feasibility
depends on each arm's evolved state. Independent seeds alone do not settle
state-dependent rejection, truncation or draw-consumption rules.

### F2-G — locality of value versus locality of selection

A factor-local exact group value does not by itself make global group enumeration
and random group selection a distributed local actor protocol. The future
design must declare the scope of group assembly, chooser identity, candidate
visibility and owner-level affordability checks.

No global `V` read is a necessary information restriction, not a complete proof
that every coordination decision is local. Preserve the separation rather than
silently granting remote state access to make the new loop convenient.

## 6. Current checkout implementation: reusable ideas and genuine coupling

The checkpointed candidate harness remains preserved, not silently converted.

| Current source | Coupling/evidence | Disposition |
| --- | --- | --- |
| `ebu_test_world.py:NodeSpec` | Requires `capacity`, `lower`, `upper`, `reserve`, `alpha`, `beta`, `chi` | Keep as old threshold-world model; do not fabricate L/U fields for Gaussian nodes |
| `ebu_test_settlement.py:potential`, `marginal_at` | Call `d0_v29.penalty` and `d0_v29.marginal` | Preserve legacy evaluators; later separate potential adapter |
| `ebu_test_settlement.py:path_breakpoints`, `path_integral` | Hinge crossing/piecewise integration | Preserve historical/candidate scope; quadratic Gaussian closed form is a distinct evaluator |
| `ebu_test_protocol.py:plan_tick`, `execute_tick` and outcome records | Controller/service/oracle study structure | Isolate from new controlling Gaussian experiment; reuse only independently reviewed generic pieces |
| `ebu_candidate_controllers.py` | C0–C4 policy definitions, views, opportunity constraints and refused builds | Superseded prospective study path; preserve definitions and guards, no new active imports |
| `longhorizon_v30.py:joint_exact_ebu`, `select_exact_ebu_joint` and source budgeting | D0/P1C and EBU-best or service-related selection | Preserve original context; do not route the new random-affordable experiment through this selector |
| `ebu_quote_v30.py:QuoteSchedule`, `EpochRegistry` | Local exact quotes/epoch integrity; explicitly no balances/wallet | Reuse mathematical/provenance ideas, not as an already implemented capacity account |

The source-locked generic framework and the current candidate harness are
different code families. This stage does not combine their APIs, copy a second
framework, or pronounce the checkpointed code accepted merely because it is now
committed.

## 7. Minimum later integration path

The roadmap should prepare these bounded extensions within the existing
framework architecture, not implement them in this stage:

1. A Gaussian domain schema and exact potential evaluation contract, with
   reference/scales/units/support metadata, preserving the threshold model.
2. A small value/gradient/affected-support adapter sufficient for the two model
   families; no giant abstraction or dense global covariance system.
3. A prospectively accepted forcing-first Gaussian event profile.
4. EBU-blind candidate generation and jointly feasible immutable group proposals.
5. Exact quadratic/group/path evaluation with physical-path assumptions and
   decomposition nonclaims separately recorded.
6. An explicit action-owner map, receipt-to-capacity rule and same-event netting
   rule; no direct transfers, genesis grants or global pool.
7. Typed persistent capacity and external-deviation audit state.
8. Independent nature/actor stream contracts and random-affordable selection,
   with a separately typed physical-random comparison.
9. A later authorized execution adapter that commits exactly the valued group
   and records independent physical/accounting audits.
10. Distinct foundation, integration, preregistration, Stage A execution/review
    and Stage B gates. A negative Stage A dynamics finding is not automatically
    a software defect or permission to change the model.

Physical conservation, loss infrastructure, atomic physical transformations and
historical engines remain preserved. The first Gaussian domain keeps losses
inert (`eta = 1`, `C_a = 0`); it does not solve or erase the broader loss-aware
runtime/valuation questions.

## 8. F1/F2/F3 comparison

| Outcome | Finding |
| --- | --- |
| F1: existing framework already fits unchanged | Not established: event semantics differ and required scientific services are not implemented |
| F2: reuse generic core, adapt/isolate scientific layers | Adopted for planning: concrete generic interfaces exist and targeted integration boundaries are identifiable |
| F3: freeze old framework and build a replacement | Not justified: no inspected core constraint makes the Gaussian model structurally impossible; a new framework would duplicate useful infrastructure |

If later source-level implementation design shows F2 is infeasible, it must
present that evidence and request a new decision before creating F3. Complexity
or the volume of historical authority files alone is not evidence of fundamental
incompatibility.

## 9. Validation scope and present readiness

This is a **source-inspected reuse disposition**, not a full framework
revalidation. The audit read both new handovers completely and inspected the
relevant framework specification/authority sections and implementation
interfaces. Complete source reads included `distortion.py`, `execution.py`,
`policy.py`, `settlement.py`, the I-3C repair amendment and Stage E RNG module;
other modules were inspected at their relevant declarations, validators and
call sites. The enormous historical validation corpora were not re-executed or
independently re-audited.

No suite, policy callback, state transition, runner, trajectory or scientific
experiment executed. There is no new empirical evidence and no fresh numerical
residual report. Passing results from earlier agents are not fresh validation
of the new programme.

The framework is source-locked for reuse planning and is not imported into this
checkout. Stage A Gaussian foundation implementation/readiness is not
established; Stage A experiment is not run; Stage B is not ready and not run.
Book structure reconciliation may proceed independently under accurate
definition/theorem/model/hypothesis labels. Book generation and all scientific
implementation remain later stages.
