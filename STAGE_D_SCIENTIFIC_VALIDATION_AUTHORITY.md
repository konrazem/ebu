# EBU Stage D Scientific-Validation Authority

**Status:** prospective scientific-validation authority candidate; documentation and strict-JSON records only; no harness implementation, model execution, outcome inspection, result, figure, book, or publication

**Authority version:** 1.0.0-candidate

**Accepted software-alpha base:** `fb9ae7b6dae14550a702e060600132faec539eca`

**Accepted software-alpha tree:** `1e3f02e4efc2ce5b0ca3c15fb8a95c3df98c277d`

**Released main coordinate:** `660d6e5a56cb096fe6d1e4d202f592155d982c79`

**Signed alpha tag object:** `b140d4a31f60316cd23058305ae17f4698de86bc`

**Signed alpha tag target:** `fb9ae7b6dae14550a702e060600132faec539eca`

**Public prerelease:** `framework-v0.1.0-alpha.1`, GitHub release `377771658`

**Stage C release disposition:** `STAGE_C_RELEASE_EXECUTION_PASS`

**Scope:** one tracked scientific-validation matrix, its mechanical contract, evidence schemas, predecessor locks, and fail-closed validation contract

---

## 1. Decision

Stage D freezes the prospective scientific questions, evidence boundaries,
study order, configurations, controls, falsifiers, resource limits,
traceability, and interpretation rules required before any new EBU scientific
harness or campaign may exist. It begins with long-run homeostasis and
viability and covers the remaining programme in dependency order.

This authority does not implement a harness and does not run even one model
step. It contains no measured wall time, measured memory, candidate outcome,
simulation result, empirical observation, figure, or book text. A field named
`future_measurement_method` describes later Stage E instrumentation; it is not
a measurement made in Stage D.

The machine-readable sources are:

1. `stage_d_scientific_validation_contract.json` — programme, stage, evidence,
   computation, and traceability rules;
2. `stage_d_scientific_validation_master_matrix.json` — complete ordered study
   records;
3. `stage_d_scientific_validation_evidence_schema.json` — immutable future
   configuration, run, trace, receipt, output, computation, and cache evidence
   schemas;
4. `stage_d_scientific_validation_predecessor_manifest.json` — exact accepted
   source and release locks; and
5. `stage_d_scientific_validation_validation_contract.json` — positive and
   fail-closed static validation rules.

A disagreement among this document and those JSON files is an integrity
failure requiring refusal. No source may be selected opportunistically.

## 2. Authority and evidence precedence

Repository and Git evidence controls accepted status. The predecessor
manifest freezes the exact base tree and every directly controlling source.
The accepted Atomic Generator and Interaction authorities control generators,
finite subsets, baselines, interaction, topology layers, causality, and
settlement separation. The Canonical Topology / Motif authority controls
canonical identity, A1–A8, Fibonacci's conditional role, correction locality,
and the current refusal of runtime cache reuse. The coupled
interaction–inference–feedback review and accepted CLCD authorities control
Möbius/conjugacy separation, memory, feedback, delay, correction closure, and
dependency propagation. Conservation authority controls account levels,
typed residuals, boundary exchange, and no-double-counting. Domain/model
authority selects scientific dependency and topology; generic framework code
must not infer scientific meaning.

The evidence levels remain distinct:

1. institutional or normative declaration;
2. mathematical theorem or derivation;
3. static or synthetic implementation test;
4. numerical verification;
5. registered scientific simulation;
6. empirical observation; and
7. independently audited interpretation.

No level may be reported as a stronger level. In particular, exact arithmetic
or a passing harness does not establish a scientific outcome; a registered
simulation is not empirical observation; and institutional design choices do
not become physical laws.

## 3. Stage boundary

### 3.1 Stage D — authority only

Stage D may inspect, hash, strictly parse, compare, derive algebra, audit
schemas, and create these six authority files. It may not import a project
runner, call a transition, model step, trajectory, Gate, experiment,
simulation, optimizer, benchmark, result writer, renderer, or book generator.
All execution and outcome counters are exactly zero.

### 3.2 Stage E — future harness only after independent PASS and integration

Only a later separately authorized Stage E may implement accepted protocols,
direct oracles, optimized algorithms, instrumentation, static/synthetic
conformance cases, numerical verification, and immutable run-envelope
mechanics. Stage E may measure implementation wall time and peak memory only
for the preregistered conformance/performance cells. It may not execute or
inspect registered scientific outcomes.

### 3.3 Stage F — registered science only

Only Stage F may execute the registered campaigns, in the matrix order, after
the applicable Stage E harness has passed an independent audit and immutable
code/configuration identities have been sealed. Negative, null,
contradictory, timed-out, resource-exhausted, and inconclusive results remain
visible and must not trigger tuning or silent replacement.

### 3.4 Stages G and H

Stage G independently reconstructs results, accounting, controls,
uncertainty, falsifiers, tables, and figures from frozen outputs. Stage H
revises and generates Parts I–IX only after required evidence passes, with Part
IX last. Publication remains separately authorized.

## 4. Universal study record

Every matrix row contains, without omission:

- a precise question and bounded prospective claim;
- evidence classes and the strongest permitted disposition;
- owning equations, definitions, authority sources, and implementation
  interfaces;
- model/domain authority, units, typed state, dependency/topology authority,
  and boundary;
- initial conditions, parameters, comparators, positive controls, negative
  controls, seeds, stochastic rules, and uncertainty rules;
- exact proposed problem size, horizon, subset/hyperedge order, and expected
  evaluation count;
- stopping rules, falsifiers, acceptance criteria, and distinct
  `COMPUTATIONALLY_INCONCLUSIVE` criteria;
- conservation, physical closure, represented-stock closure, EBU accounting,
  causal, and institutional no-double-counting rules;
- immutable configuration, run, trace, receipt, computation, and output
  schemas;
- provenance, recovery, checkpoint/restart, and independent result-audit
  obligations; and
- eventual book destination and prohibited interpretations.

Missing, null, changed, non-finite, outcome-derived, or unsealed required
content refuses execution. The sole exception is the Gate 1E recovery row:
because no controlling Gate 1E protocol exists in the accepted tree, that row
is explicitly `AUTHORITY_RECOVERY_REQUIRED` and executable fields are frozen
to `FORBIDDEN_UNTIL_SEPARATE_AMENDMENT`, not guessed from memory.

## 5. Computational-feasibility gate

The reference environment is the immutable Stage C linux/amd64 OCI manifest
`sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab`
with CPython 3.14.4 final, executable SHA-256
`353d0275b5ca0447ebfc6ecae7d80a7a7e7a627d4669fdcc3f836f0b8d804c79`,
SQLite 3.46.1 / `(3,46,1)`, runtime source ID ending `alt1`, provenance-only
upstream ID ending `1e33`, and Debian package
`libsqlite3-0:amd64=3.46.1-7+deb13u1`. Its lineage is
`python:3.14.4-trixie` at docker-library/python revision
`6cc07b27ad0df3769bbd1a2a1000a842634681d2`, hosted by `ubuntu-24.04`, with
future registered operations offline. Stage E must record the complete future
environment and reject a mismatch; Stage D does not execute it.

Each future computation record carries the mathematical cost class, exact
input dimensions, exact operation/evaluation accounting rule, expected
evaluations, measured Stage E wall time and peak resident memory, storage and
trace estimates, checkpoint/restart design, parallel boundary, hard caps,
timeout/resource disposition, and exact-versus-approximate label.

The global caps are upper bounds, not resource reservations or evidence of
feasibility: 14,400 seconds wall time per scientific run, 4,294,967,296 bytes
peak resident memory per process tree, 21,474,836,480 bytes total immutable
study output, 5,368,709,120 bytes per trace, 50,000,000 declared primary
evaluations per run, and recursion/dependency depth 100,000 unless a stricter
study cap applies. Stage E must refuse a protocol whose measured conformance
projection cannot fit its exact study caps.

If an exact study exceeds a frozen limit, the only permitted dispositions are
fail-closed refusal before execution or `COMPUTATIONALLY_INCONCLUSIVE` with a
limit-decision receipt. Neither disposition is positive or negative
scientific evidence.

Every stochastic matrix row uses the same frozen counter-hash rule rather
than mutable library PRNG state. The SHA-256 preimage is exactly
`EBU-STAGE-F-RNG-v1|study_id|configuration_id|seed|stream_id|tick|event_index|draw_index`
with canonical decimal integers and no whitespace. The first eight digest
bytes form an unsigned 64-bit integer. An exact rational Bernoulli draw
`p_num/p_den` succeeds only below `floor(p_num*2^64/p_den)`; categorical draws
use frozen cumulative rational thresholds. Each row names its streams and
probabilities. Unknown streams, draw-order changes, reused preimages, mutable
PRNG state, and undeclared continuous-distribution transforms refuse. Stage D
performs zero draws.

## 6. Mandatory Möbius/topology controls — verbatim user authority

The following text is retained verbatim and is mechanically represented in
the contract, matrix, evidence schema, and validation contract:

1. Preserve a direct, independently understandable small-case Möbius/topology oracle as the normative correctness reference.
2. Any optimized bitmask/fast Möbius transform must reproduce the direct oracle exactly over the complete registered small-case domain and declared randomized/adversarial cross-check domain; a mismatch is a refusal, not a tolerance or approximation case.
3. Require measured complexity evidence for the optimized Möbius path against declared `O(n*2^n)` time and `O(2^n)` storage expectations, with registered dimensions, instrumentation, environment, thresholds, and nonclaim boundaries.
4. Require dependency-DAG traversal evidence against `O(V+E)` time, including sparse/dense, disconnected, deep-chain, wide-frontier, invalid-cycle, duplicate-edge and ordering controls.
5. Permit recursive motif or cache reuse only when equivalence is certified under the controlling canonical/topology authority; cache keys must be complete for every result-affecting input/authority/version/environment dimension; corrections or authority changes must deterministically invalidate affected entries.
6. Register positive reuse cases, non-equivalent near-miss negative controls, incomplete-key collision falsifiers, stale-cache/correction-invalidation tests, and provenance/receipt requirements.
7. Define explicit hard limits for exact Möbius/topology studies: maximum n/subset count, vertices, edges, memory, wall time, trace/output size and recursion/depth as applicable. Values must be justified before execution and bound to the reference environment.
8. If a requested exact study exceeds a hard limit or resource budget, fail closed or classify it `COMPUTATIONALLY_INCONCLUSIVE`. Do not silently approximate, truncate, sample, alter topology, weaken equivalence, or convert the outcome into positive/negative scientific evidence.
9. Any separately proposed approximation requires its own preregistered authority, error bounds, controls, evidence class and interpretation rules; it must never be substituted for an exact registered study after outcomes are visible.
10. Record the oracle/optimized implementation identities, complexity observations, cache/equivalence certificates, invalidation receipts, limit decisions and inconclusive classifications in the traceability chain through eventual results and books.

These controls apply to every relevant study rather than only to the row named
Möbius. The validation contract enumerates the applicable study IDs and
requires each row to bind the shared controls.

## 7. Exact Möbius boundary

The normative direct oracle implements the definition

\[
I_{\mathrm{raw}}(S)=\sum_{T\subseteq S}(-1)^{|S|-|T|}E(T),
\qquad I_{\mathrm{raw}}(\varnothing)=E(\varnothing),
\]

using exact integers or reduced rationals and an independently readable
subset enumeration. It is the correctness reference even if slower.

The future optimized bitmask transform may use the standard in-place Boolean
fast Möbius transform. Its declared arithmetic cost is `O(n*2^n)`, storage is
`O(2^n)`, and complete subset-value acquisition remains an additional
`2^n * C_E` cost for per-subset evaluation cost `C_E`. It does not solve the
arbitrary-table query lower bound.

The shared oracle-agreement domain is exactly the matrix's 488 registered
cases: eight exact deterministic/adversarial table families at every
dimension `n=0..12`, plus 32 declared pseudorandom integer-table seeds at each
`n=1..12`. Every coefficient and reconstruction must agree bit-for-bit. One
mismatch refuses the optimized implementation and every dependent study.

The eight families are frozen as zero, constant seven, cardinality, weighted
additive, weighted pairwise, full-set spike, empty-set spike, and signed
cardinality cube, with their exact formulas in the mechanical contract. The
32 seed values are the integers 0 through 31. They do not depend on a library
PRNG: every value is derived from the first eight bytes of SHA-256 over the
contract's exact `EBU-SD06-MOBIUS-v1|n|seed|mask` UTF-8 preimage and mapped to
the integer interval `[-1000,1000]`. Thus the randomized/adversarial domain is
prospectively complete and reproducible rather than selected in Stage E.

The optimized complexity cells are dimensions `n=8..18`, five repetitions
per dimension, in frozen order. They may be measured only in Stage E. The
hard exact limit is `n=18`, `2^18=262144` subsets, 536,870,912 bytes peak
resident memory, 120 seconds wall time per case, and 268,435,456 bytes combined
trace/output. No universal scalability claim is permitted.

Stage E must record exactly `n*2^(n-1)` butterfly subtractions, at most `2^n`
live table slots and at most `4*n+64` auxiliary scalar slots. For `n=14..18`,
the largest median of `wall_nanoseconds/(n*2^n)` may be no more than four
times the smallest median; each cell must also remain within the hard caps.
Failure is `BOUND_NOT_SUPPORTED` and refuses dependent optimized studies. At
`n=18` the prospectively expected count is 2,359,296 butterfly subtractions;
this count and the caps justify the boundary without constituting a Stage D
measurement.

For an infeasible subset family, a Boolean value must not be invented. A
feasible-poset study uses only its separately declared finite incidence
domain and exact Möbius function. Sparse or low-order hyperedge restrictions
are exact only when proved or declared as the scientific domain; otherwise
they are an approximation requiring separate authority.

## 8. Dependency-DAG boundary

The normative direct affected-record oracle enumerates explicit paths for
small graphs with at most 12 vertices. The future optimized traversal is a
deterministic queue/topological algorithm with declared `O(V+E)` time and
`O(V+E)` representation storage. It must return exactly the same affected
vertex set and deterministic topological order as the direct oracle on every
registered small case.

The Stage E cells include sparse, dense, disconnected, deep-chain,
wide-frontier, invalid-cycle, duplicate-edge, and input-order-permutation
controls. Optimized dimensions are sparse graphs at `(V,E)=(128,256)`,
`(1024,4096)`, `(10000,50000)`, and `(100000,500000)`, plus a dense acyclic
case `(512,130816)`. Duplicate edges refuse; cycles refuse before an affected
order is certified; disconnected nodes remain unaffected; ordering is the
lexicographically least ready-node order over canonical IDs.

The hard limits are 100,000 vertices, 500,000 edges, depth 100,000,
1,073,741,824 bytes peak resident memory, 120 seconds wall time, and
268,435,456 bytes combined trace/output. Traversal reachability does not prove
physical propagation, causality, or scientific topology.

The exact agreement domain contains all 33,867 combinations of every
canonical forward-edge DAG and every source subset for `n=0..5`. At each
`n=6..12`, eight frozen adversarial graph families and 32 SHA-256-derived
graphs are crossed with five source sets and four input-edge orders, adding
1,120 and 4,480 exact agreement cases. The hash-derived edge preimage is
`EBU-SD-DAG-v1|n|seed|i|j`, seeds are `0..31`, and an allowed forward edge is
included exactly when the first digest byte is even. One cycle and one
duplicate-edge refusal control are injected for each `n=6..12`.

Stage E must observe no more than `V` vertex enqueues, `E` edge inspections,
and `6*V+2*E` logical storage slots. Across the four sparse complexity cells,
the largest median `wall_nanoseconds/(V+E)` may be no more than eight times
the smallest. The dense cell is recorded separately and must satisfy the
exact operation/storage and hard caps. Threshold failure is
`BOUND_NOT_SUPPORTED` and refuses dependent optimized traversal. These
prospective thresholds are not Stage D benchmark results.

## 9. Canonical equivalence, motifs, and conditional reuse

Canonical identity remains exhaustive only for the accepted
`0 <= vertices <= 8` canonical topology schema. It is not performance.
Recursive motif reuse requires all A1–A8 conditions and a query-specific
boundary-sufficiency certificate. The Fibonacci recurrence is one exact
ordered substitution example only.

The complete future cache key includes canonical topology ID; motif,
occurrence, composition, and boundary-summary versions; complete initial
augmented-state and admissible-history digest; query and horizon; units,
boundary, removal and feasibility semantics; numerical policy; framework,
authority, protocol, configuration, code, dependency, environment, and
evidence identities; alias closure; and correction/invalidation epoch.
Leaving out any result-affecting dimension is a collision falsifier.

Positive reuse cases, non-equivalent near misses, ordered-child swaps,
boundary changes, history changes, incomplete keys, aliases, stale cache
entries, corrected evidence, authority-version changes, and environment
changes are mandatory controls. Corrections traverse the complete explicit
dependency/alias DAG and issue invalidation receipts before any recomputation.

No production runtime cache is authorized by Stage D. Stage E may implement
only isolated research/conformance cache mechanics after independent Stage D
acceptance. Scientific reuse remains conditional and Stage F may use it only
when every certificate and receipt is present.

Exact motif limits are canonical vertices 8, hyperedge order 4, expanded
oracle level 16, compressed comparison level 32, expanded occurrence count
3,524,578, recursion depth 64, 1,073,741,824 bytes memory, 120 seconds per
case, and 268,435,456 bytes combined trace/output. Exceeding any limit refuses
or yields `COMPUTATIONALLY_INCONCLUSIVE`.

## 10. Registered programme order

| Order | Study ID | Programme | Principal evidence destination |
|---:|---|---|---|
| 1 | SD-01 | Long-run homeostasis, viability, invariance, recursive feasibility, stability, recovery, reserves, regeneration, adversarial schedules, and Allee thresholds | Part V |
| 2 | SD-02 | Gate 1D-C, robust-P1C alignment, and Gate 1E authority recovery | Part IV |
| 3 | SD-03 | Atomic generator and finite chain `V -> mu=grad V -> f_e -> Psi_e -> J_e -> G_T -> finite EBU` | Parts I, II, VI |
| 4 | SD-04 | Finite Taylor expansion, mixed marginals, commutators, and order effects | Parts II and VI |
| 5 | SD-05 | Sequential, parallel, pairwise, many-action, and higher-order interaction | Part VI |
| 6 | SD-06 | Boolean Möbius, nonzero `E(empty)`, hypergraphs, feasible posets, and omitted-order accounting | Part VI and proofs appendix |
| 7 | SD-07 | Canonical equivalence, recursive motifs, conditional Fibonacci example, certified reuse, cache invalidation, and negative controls | Part VI and short Part VIII cross-reference |
| 8 | SD-08 | Routes, queues, congestion, delays, provenance, and dependency traversal | Part VII |
| 9 | SD-09 | Resilience, recovery, fairness, coordination overhead, topology failures, and adaptive infrastructure | Parts VII and VIII |
| 10 | SD-10 | CLCD inference, correction, feedback, memory, delay, stability, error cost, closure, diagnostics, and propagation | Part VIII |
| 11 | SD-11 | Correction receipts, physical/conservation closure, represented closure, no-magical-gain, and no-double-counting | Parts VIII and IX |
| 12 | SD-12 | Cooperation, protected disclosure, contestability, privacy, retaliation, trust, and learning hypotheses | Part IX |
| 13 | SD-13 | Quote, residual, settlement, reserves, access, governance, appeals, fraud, responsibility, and compensation separation | Part IX |
| 14 | SD-14 | Complete-economy scenarios across household, hospital, enterprise, infrastructure, and ecology | Part IX last |

No study may run out of order unless a prospective amendment proves that all
dependencies are satisfied and receives independent audit before outcomes are
visible. A preceding null or negative result does not automatically prohibit a
later study; its declared dependency and acceptance rules decide.

## 11. Gate 1D-C and Gate 1E preservation

Gate 1D-C retains its exact existing protocol and plan: three worlds, five
executable arms, two timesteps, 30 runs, 200 ticks, 50 burn-in ticks, and 20
persistence ticks. Stage D neither edits nor executes it. Its incident,
invocation count, execution/finalization contracts, compatibility addenda,
and any future permission must be reconstructed before an official action.

No accepted-tree file defines the complete Gate 1E scope. Stage D therefore
does not invent parameters or reinterpret it. SD-02 records Gate 1E as
`AUTHORITY_RECOVERY_REQUIRED`; all execution fields refuse until a separate
prospective amendment identifies the controlling historical source or obtains
new user authority. Robust-P1C uncertainty claims likewise require exact
observation, delay, uncertainty, margin, coverage, and calibration authority
before execution.

## 12. Traceability and immutable evidence

Every future claim follows:

`equation -> configuration -> code -> test -> immutable run/trace -> table/figure -> claim disposition`.

Configuration identities include the complete dependency closure and are
sealed before Stage F. Run manifests bind configuration, code, environment,
seeds, authorization, start/end, checkpoints, exit status, and output hashes.
Trace rows bind sequence, simulated time, typed state/input/output, topology,
subset/hyperedge, correction/cache events, conservation residuals, and a
prefix hash. Receipts preserve actions and corrections separately. Outputs
carry units, uncertainty, evidence label, source digest, and claim owner.

Möbius/topology traces additionally bind oracle and optimized implementation
identities, agreement results, operation counts, complexity observations,
equivalence certificates, complete cache keys, hits/misses, alias/dependency
closure, invalidation receipts, hard-limit decisions, and
`COMPUTATIONALLY_INCONCLUSIVE` classifications.

Checkpoint restart must reproduce the uninterrupted continuation exactly from
the checkpoint identity. A mismatch creates a new failed run record; it does
not overwrite the original or continue under the same run ID.

## 13. Conservation and no-double-counting

Every study declares one of reduced represented-stock, open control-volume,
or isolated boundary-complete accounting. Isolation is never inferred.
Physical conservation, represented-stock closure, EBU accounting, causal
inference, correction cost, and institutional settlement are separate
ledgers. Internal roll-up transfers cancel exactly once. Omitted boundary
flows, duplicate process accounts, hidden loss, phantom service, retrospective
quote rewriting, magical correction gain, or using one joint benefit/cost in
multiple accounts are falsifiers.

An unexplained residual remains explicit. A policy may not zero it. A
correction action has its own inputs, outputs, loss, burden, cost, and receipt;
it does not negate the original receipt.

## 14. Interpretation, figures, and books

Stage D freezes only future destinations. It generates no figure or book.
Every later visual must be labelled exactly as schematic, mathematically
derived, tested implementation, observed in a registered run, research
hypothesis, or institutional design choice. Run-derived figures carry run ID,
code coordinate, configuration identity, units, uncertainty, evidence label,
and source-data digest.

Canonical identity is not performance. Interaction is not causality.
Sensitivity or estimation is not responsibility. Positive recursive surplus
is not fairness. A physical optimum does not select an institution. A modelled
cooperation result is not empirical human behaviour. The complete-economy
simulation is a model test only.

Wave, phase-interference, electrical-voltage, physical superposition,
topological-wave, universal Fibonacci/fractal, and speculative-credit
programmes remain excluded.

## 15. Approximation boundary

Every matrix study is labelled `EXACT`, `MODEL_EXACT_NUMERICAL`, or
`SEPARATE_APPROXIMATION_AUTHORITY_REQUIRED`. No exact registered study may be
silently approximated, sampled, truncated, sparsified, reduced to a different
poset, assigned a weaker equivalence, or replaced after outcomes are visible.

Any approximation programme requires a separate preregistered authority with
its own mathematical target, error norm and bound, comparator, positive and
negative controls, calibration/validation split, seeds, resource limits,
evidence class, falsifiers, and interpretation rules. Approximate results may
never be reported as the exact study's disposition.

## 16. Independent audits and stop conditions

Before Stage E, an independent auditor must reproduce exact base/release/source
identities, strict JSON and text integrity, six-path scope, matrix order and
field closure, every cost/limit rule, all 488 Möbius agreement cases as
prospective declarations only, DAG control closure, cache-key closure,
schema/ref integrity, exclusions, and zero execution/output state.

Stop and return failure for a dirty or mismatched base, duplicate JSON key,
non-finite value, missing study field, unknown study, unbound authority,
unjustified or absent hard limit, missing negative control, tolerance in exact
oracle agreement, incomplete cache key, dynamic approximation fallback,
performance/result value in Stage D, executable Gate 1E configuration,
scientific code/result/figure/book path, or any model-state advance.

After independent PASS, only normal non-force integration of the exact
authority candidate may be proposed. Stage E remains separately authorized.

## 17. Completion marker

This candidate is complete for independent Stage D authority audit only when
all six files strictly validate, the worktree is clean at one immutable commit,
the feature ref matches that commit, and the audit handoff records exact raw
and canonical identities. It authorizes no implementation or execution.

`STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY_CANDIDATE_COMPLETE`
