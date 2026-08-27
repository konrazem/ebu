# EBU Stage D Completion-Oriented Checkpoint-Continuation Authority Amendment

**Status:** prospective additive authority candidate; documentation and strict-JSON records only; no Stage E implementation, scientific execution, transform, benchmark, outcome inspection, result, figure, book, release, or publication

**Authority version:** 1.0.0-candidate

**Exact accepted base:** `d000015cbf3e3238e34f961c4916626c930ba90f`

**Exact accepted base tree:** `8bff192813649300a8aa8b298c441b851cea26d7`

## 1. Purpose and narrow precedence

This amendment resolves one ambiguity in the accepted Stage D scientific-
validation authority: how a finite registered study may continue over several
bounded operating-system attempts while preserving one immutable scientific
identity, exact checkpoints, and cumulative resource accounting.

The six accepted Stage D authority files at the exact base remain byte-for-
byte unchanged. Their questions, models, configuration domains, study order,
evidence classes, numerical policies, stochastic rules, uncertainty rules,
problem-size limits, topology authority, exact-versus-approximate labels,
falsifiers, controls, and interpretation boundaries remain controlling.

For a future continuation-enabled campaign only, this amendment prospectively
supersedes the ambiguous use of `per scientific run` for wall-time, process-
tree memory, and primary-evaluation watchdogs. Those values become maximum
limits for one bounded attempt slice. A separately frozen campaign envelope
governs cumulative resources across every slice. No attempt limit or campaign
limit resets, disappears, or becomes a scientific outcome.

Accepted `run_manifest/v1` and `checkpoint_record/v1` records remain valid
historical schemas. A continuation-enabled campaign must use the versioned
records in this amendment. It may not mix `v1` terminality with `v2`
continuation or reinterpret an existing `v1` run after execution.

This amendment grants no Stage E implementation or Stage F execution. It must
receive an independent authority PASS and normal integration before a later
durability or harness authority may rely on it.

## 2. Exact candidate scope

The candidate adds exactly five regular mode-`100644` files:

1. `STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_AMENDMENT.md`;
2. `stage_d_completion_oriented_continuation_contract.json`;
3. `stage_d_completion_oriented_continuation_evidence_schema.json`;
4. `stage_d_completion_oriented_continuation_predecessor_manifest.json`;
5. `stage_d_completion_oriented_continuation_validation_contract.json`.

No accepted authority, implementation, test, workflow, fixture, package,
result, figure, manuscript, release, or publication file may change in the
authority candidate.

## 3. Identity hierarchy

The hierarchy is closed and ordered:

1. `study_id` is one of the accepted `SD-01` through `SD-14` identifiers.
2. `campaign_id` identifies the complete finite registered study campaign:
   the ordered configuration set, study authority, code, installed artifact,
   environment, algorithms, numerical and uncertainty policies, stochastic
   rule, allowed streams and seeds, topology/dependency authority, exact-or-
   approximate label, horizons, controls, falsifiers, checkpoint policy, and
   campaign budget.
3. `scientific_run_id` identifies one exact registered configuration/seed/
   horizon cell inside the campaign. It is immutable across all slices.
4. `attempt_id` identifies one bounded process attempt for one scientific run.
   It is the digest-bound tuple `(campaign_id, scientific_run_id,
   attempt_ordinal, incoming_checkpoint_identity, attempt_binding_identity)`.
5. `checkpoint_id` identifies the complete durable continuation state after a
   declared atomic boundary.

Changing any result-affecting campaign or run field creates a different
campaign or scientific run. It cannot be called continuation. Changing only
the attempt ordinal, start timestamp, or process allocation within the frozen
parallel boundary does not change scientific identity, but it remains recorded
in the attempt manifest and cumulative ledger.

`attempt_binding_identity` is not opaque. It is the canonical digest of one
closed `attempt_binding/v2` record. That record binds the campaign, scientific
run, exact campaign execution-binding identity, attempt ordinal, incoming
checkpoint, all five frozen campaign execution-policy identities, the complete
actual process allocation, its allocation identity, and the policy-conformance
receipt. The attempt manifest embeds that record and repeats its digest identity
so an auditor can reconstruct both the binding and `attempt_id` without an
external convention.

## 4. Attempt binding and frozen campaign envelope

Before Stage F execution, every campaign must carry an independently audited,
outcome-blind `campaign_execution_binding/v2`. It freezes:

- exact campaign and scientific-run membership and order;
- exact code commit/tree and installed-artifact hash;
- exact authority, configuration, schema, algorithm, oracle, environment,
  topology/dependency, numerical, stochastic, uncertainty, seed-set, stream-
  set, cache-key and invalidation-policy identities;
- exact checkpoint cadence and atomicity boundary;
- exact attempt slice wall-time, process-tree peak-memory, primary-evaluation,
  emitted-byte, and depth watchdogs;
- exact campaign maximum attempts, cumulative active wall time, cumulative
  primary evaluations, cumulative newly emitted trace bytes, cumulative
  output bytes, maximum process-tree peak memory, maximum calendar duration,
  and any stricter study-specific dimensions;
- exact parallelization boundary, worker allocation policy, storage location,
  durability and restart rules;
- exact terminal and infeasibility rules.

Those five execution policies are carried as the distinct required identities
`parallelization_boundary_identity`, `worker_allocation_policy_identity`,
`storage_location_identity`, `durability_policy_identity`, and
`restart_policy_identity`. All five are part of the campaign identity preimage.
An omitted, changed, aliased, or post-start policy identity creates a different
campaign and cannot validate as continuation.

Each attempt embeds a closed `process_allocation/v2` record containing the
ordered worker allocations. Every worker row records its ordinal, worker and
host identities, process identity and index, thread count, CPU allocation,
nullable accelerator allocation, and memory limit. The allocation also binds
the scheduler allocation and the exact policy-conformance receipt. Worker
ordinals are unique, contiguous from zero, and agree with `worker_count`;
process identities and indices cannot be duplicated. The allocation digest is
recomputed canonically and must equal both `process_allocation_identity` in the
attempt binding and the embedded allocation's digest. Actual allocation must
conform to the frozen parallelization boundary and worker-allocation policy;
out-of-policy, missing, or digest-mismatched allocation refuses the attempt.

For both execution-binding digests, the declared preimage fields are assembled
as one closed object and serialized using the same canonical JSON rule used for
the counter tuple set: recursively sorted keys, comma/colon separators, no
insignificant whitespace or final LF, UTF-8 without ASCII forcing, and integer-
only numbers. `process_allocation_identity` has kind
`process_allocation/v2`; `attempt_binding_identity` has kind
`attempt_binding/v2`. In each identity both `value` and `sha256` equal the
reconstructed 64-lowercase-hex digest. The embedded record's `allocation_sha256`
or `binding_sha256` must equal that same digest.

Stage E feasibility measurements may inform this binding, but the complete
binding must be sealed and independently audited before any Stage F outcome is
visible. It may not be enlarged after execution begins. A later enlargement
requires a new prospective authority and a new campaign identity; it cannot
resume or replace the earlier campaign after outcomes are visible.

Attempt watchdogs are upper bounds and may be stricter than the accepted
Stage D values. For continuation-enabled `v2` campaigns, they may never exceed
the accepted Stage D wall-time, memory, and primary-evaluation values for the
applicable study/control profile. The campaign envelope may be larger than one
attempt for cumulative active wall time, cumulative evaluations, and
cumulative actual physical writes only when the larger values are
prospectively justified from Stage E feasibility evidence and independently
accepted before Stage F. Durable logical output and problem dimensions do not
expand merely because physical retries are counted.

Problem dimensions are never sliceable. Maximum `n`, subset count, hyperedge
order, vertices, edges, recursion/dependency depth, agent count, canonical
level, per-case trace/output limit, and other exact problem-size dimensions
remain the accepted Stage D limits for the complete case. A campaign envelope
cannot authorize a larger problem.

The accepted total immutable output limit per study and final trace/output
limits remain cumulative logical-byte ceilings. Re-emitting or retrying bytes
does not create extra logical allowance. Actual bytes written during failed or
repeated attempts are also counted separately in the resource ledger.

## 5. Completion-oriented attempt protocol

An attempt begins only after all identities and the incoming checkpoint have
been verified. Attempt ordinal zero begins from the frozen initial state.
Every later ordinal must equal the previous terminal attempt ordinal plus one
and must consume the previous accepted outgoing checkpoint. Skipped, repeated,
forked, or concurrently active ordinals refuse.

A normal slice ends voluntarily before its watchdog limit at the next exact
authorized checkpoint boundary. It records
`CHECKPOINTED_CONTINUATION_REQUIRED`, emits no scientific disposition, and
permits the next attempt only after the checkpoint, trace prefix, receipt
prefix, cumulative ledger, cache epoch, dependency closure, state, numerical
policy, stochastic counter state, and continuation receipt all validate.

The restarted suffix must be byte-identical to an uninterrupted suffix for the
complete registered conformance domain. A mismatch is
`CONTINUATION_EQUIVALENCE_FAILURE`; it invalidates the attempt and suspends the
campaign. It is not tolerated, approximated, or converted into an outcome.

A clean slice boundary is not a timeout, resource exhaustion, scientific
result, positive result, negative result, null result, or computationally
inconclusive disposition. It is operational continuation evidence only.

## 6. Cumulative accounting that never resets

Every terminal attempt emits an immutable `run_resource_ledger/v2` for its
scientific run and an immutable `campaign_resource_ledger/v2` for the complete
campaign. For run attempt ordinal `k`, the run ledger must be derived from
ordinal `k-1` and the exact attempt delta:

- `attempt_count = k + 1`;
- cumulative active wall time is the integer sum of every attempt's monotonic
  active nanoseconds, including failed/repeated work;
- cumulative primary evaluations are the integer sum of every attempted
  evaluation, including work discarded after the last durable checkpoint;
- cumulative physical bytes written are the sum of every attempt's emitted
  bytes, including duplicates;
- durable logical trace and output bytes are monotone high-water values and
  cannot decrease or be double-counted for allowance;
- run peak process-tree memory is the maximum observed attempt peak in that
  scientific run;
- checkpoint, trace, receipt, invalidation, and cache-epoch prefixes are
  append-only;
- the run ledger identity chains to its predecessor and attempt
  manifest.

The campaign ledger is reconstructed from every terminal attempt manifest and
latest run ledger in the campaign, ordered by frozen scientific-run order and
then attempt ordinal. It carries campaign-wide sums, maxima, physical/logical
byte counts, calendar duration, active-attempt count, and the exact set of run
ledger identities. Parallel run attempts may execute only within the frozen
parallel boundary; their immutable deltas are folded at an accounting barrier
in that canonical order. Completion order, worker identity, or scheduling
cannot change the campaign ledger. A missing, duplicated, or concurrently
lost delta refuses the accounting barrier and every later attempt.

No restart may reset a run or campaign clock, evaluation counter, byte counter,
peak-memory observation, attempt count, stochastic counter, cache epoch,
correction epoch, or receipt/trace prefix. Missing or non-monotone accounting
refuses the next attempt.

Queued time and deliberate offline time between attempts are not active
compute time, but they count toward the separately frozen maximum campaign
calendar duration. Suspending a campaign does not erase either counter.

## 7. Cache, equivalence, correction, and authority invalidation

The accepted 29-field result-affecting cache key remains mandatory. A
continuation checkpoint additionally seals the campaign identity, scientific
run identity, incoming/outgoing attempt ordinals, exact next stochastic
counter tuple per stream, cache epoch, correction invalidation epoch,
dependency/alias closure, authority versions, code and installed-artifact
identities, environment, numerical and uncertainty policies, topology, and
exact-or-approximate label.

A correction, authority change, algorithm change, environment change, cache-
key change, equivalence-certificate change, topology/dependency change,
numerical-policy change, stochastic-rule/seed/stream/counter change, or
uncertainty-policy change deterministically invalidates every affected cache
entry and checkpoint. It cannot continue under the prior campaign identity.
Invalidation receipts precede recomputation. An unaffected entry may survive
only when the accepted dependency and alias DAG proves it unaffected and the
complete key is unchanged.

Near-equivalence, incomplete-key collisions, stale-cache reuse, missing
invalidation receipts, or alias/dependency omissions refuse continuation.

## 8. Stochastic checkpoint rule and terminal rejection cap

The accepted counter-hash rule remains exact. Each checkpoint carries every
permitted stream's next tuple `(stream_id, tick, event_index, draw_index,
attempt_index, draw_status)`. Attempt slicing does not alter a draw preimage or
consume a new scientific draw merely because an operating-system attempt
changed.

The checkpoint repeats the closed `ordered_permitted_stream_ids` array bound by
`permitted_stream_set_identity`. The tuple array is complete and canonical: it
contains exactly one tuple for every listed permitted stream, contains no other
stream, has no duplicate `stream_id`, and is ordered by ascending UTF-8 bytes of
`stream_id`; its stream-id projection equals that array exactly. A continuation
checkpoint may contain only `READY` tuples with
`attempt_index` in `0..999999`. The required
`next_counter_tuple_set_identity` is SHA-256 over the UTF-8 canonical JSON
serialization, without a final LF, of the closed object
`{"permitted_stream_set_identity": <the complete identity object>,
"ordered_permitted_stream_ids": <the ordered unique string array>,
"next_counter_tuples": <the ordered tuple array>}`; keys at every object level
are lexicographically sorted, separators are exactly comma and colon with no
insignificant whitespace, strings are emitted as UTF-8 JSON without ASCII
forcing, and all numbers are integers. Its identity kind is exactly
`next_counter_tuple_set/v2`, and both its `value` and `sha256` equal the
64-lowercase-hex digest. Omission, stream-set mismatch, tuple-set digest
mismatch, missing/extra/duplicate/misordered stream, or terminal tuple in a
continuation checkpoint refuses continuation.

`READY` permits draw attempt indices `0..999999`. Exactly 1,000,000 rejected
draw attempts seals `TERMINAL_REJECTION_CAP`. That state is terminal
`COMPUTATIONALLY_INCONCLUSIVE` for the scientific run. It cannot be continued,
retried with another attempt ordinal, mapped to an outcome, bypassed with a new
stream, sampled, truncated, or hidden inside a new campaign bearing the same
scientific identity.

## 9. Attempt failures, recovery, and terminal states

The closed attempt terminal states are:

- `CHECKPOINTED_CONTINUATION_REQUIRED` — clean non-scientific slice boundary;
- `SCIENTIFIC_RUN_TERMINAL` — the registered horizon/stopping/falsifier rule
  reached with the accepted Stage D scientific disposition;
- `ATTEMPT_WATCHDOG_TIMEOUT` — attempt wall-time watchdog fired;
- `ATTEMPT_RESOURCE_EXHAUSTED` — memory/evaluation/byte/depth watchdog fired;
- `IMPLEMENTATION_OR_DURABILITY_FAILURE` — code, checkpoint, trace, receipt,
  schema, hash, or exact-restart defect;
- `IDENTITY_OR_AUTHORITY_REFUSAL` — required identity or permission mismatch;
- `TERMINAL_REJECTION_CAP` — the accepted stochastic terminal cap;
- `CAMPAIGN_BUDGET_EXHAUSTED` — a cumulative campaign limit was reached;
- `CAMPAIGN_CALENDAR_DEADLINE_REACHED` — the frozen campaign duration ended;
- `MATHEMATICAL_OR_MATERIAL_INFEASIBILITY` — separately established under
  Section 10.

Timeout or resource exhaustion does not silently answer or erase the
registered question. The attempt's evidence and cumulative cost remain. No
automatic retry is allowed. A recovery may resume from the last previously
accepted durable checkpoint under the same code and environment only after a
prospectively applicable recovery rule classifies the failure as transient,
proves that no post-checkpoint state was accepted, and records an independent
recovery disposition. The failed work remains in cumulative accounting.

A deterministic implementation defect suspends the campaign. Fixing code or
changing the environment creates a new campaign identity and requires new
prospective authority. It cannot continue the old campaign or overwrite its
record.

`CAMPAIGN_BUDGET_EXHAUSTED`, `CAMPAIGN_CALENDAR_DEADLINE_REACHED`, an
unrecoverable attempt failure, and `TERMINAL_REJECTION_CAP` produce
`COMPUTATIONALLY_INCONCLUSIVE` or `NOT_A_SCIENTIFIC_OUTCOME` as mechanically
specified. They are neither positive nor negative scientific evidence. The
question remains explicitly unresolved.

## 10. Mathematical or material infeasibility

An infeasibility finding is not a scientific outcome and cannot be inferred
from one slow or failed attempt. It requires a separate immutable record that
binds the exact campaign, problem dimensions, algorithms, cost derivation,
Stage E measurements, attempted slices, cumulative ledger, available frozen
environment, storage and scheduling constraints, alternatives considered, and
why none can complete without violating accepted authority.

`MATHEMATICAL_INFEASIBILITY` requires a derivation or theorem establishing the
conflict. `MATERIAL_INFEASIBILITY` requires independently auditable resource or
permission evidence. Both require independent audit before terminal campaign
classification. Neither may be presented as evidence for or against the
registered scientific claim.

## 11. Atomic exact studies and finite-computation boundary

Continuation does not authorize arbitrary-`N` completion. The accepted finite
dimensions and hard problem limits remain exact. In particular, Boolean
Möbius work retains `O(n*2^n)` transform arithmetic plus subset-evaluation cost
and `O(2^n)` storage, with the accepted maximum `n`, subset count, and
hyperedge order. No universal scalable solution is claimed.

An atomic Möbius table transform, direct-oracle case, finite-poset inversion,
canonical case, or other matrix-declared atomic case may not be checkpointed
inside the atomic operation. It must finish within its accepted per-case caps
or become visibly inconclusive. A multi-slice campaign may continue only at
the next absent atomic case identity. It may not resume a partial coefficient
array, sample, truncate, sparsify, alter the poset/topology, weaken exactness,
or substitute an approximation.

Any approximation programme remains separately preregistered, with its own
authority, error bounds, controls, evidence class, and interpretation rules.

## 12. Stage E and Stage F boundaries

After independent acceptance and integration of this amendment, a separately
authorized Stage E may implement only the schemas, ledgers, exact checkpoint
mechanics, synthetic continuation controls, oracle/optimized conformance, and
preregistered feasibility measurement allowed by the accepted Stage D
authority. Stage E may not run a registered scientific campaign or inspect a
candidate scientific outcome.

Before Stage F, an immutable execution binding must freeze the exact campaign
envelope using accepted Stage E feasibility evidence. Stage F alone may run a
registered campaign, and only after an independent harness audit and a
separate explicit execution gate.

Stages G and H remain forbidden until their predecessor evidence passes.
Wave/phase-interference and electrical-voltage programmes remain excluded.

## 13. Fail-closed validation and negative cases

The mechanical contract and evidence schema must refuse at least:

1. an attempt without the exact campaign/run/binding/checkpoint identities;
2. an omitted or changed campaign parallelization, worker-allocation, storage,
   durability, or restart-policy identity;
3. a missing, digest-mismatched, duplicated, or out-of-policy actual process
   allocation or policy-conformance receipt;
4. a skipped, repeated, forked, or concurrently active attempt ordinal;
5. a reset/decrease/omission in any cumulative counter;
6. replacing cumulative accounting with per-slice-only accounting;
7. exceeding a slice watchdog without the recorded terminal state;
8. exceeding a campaign budget and continuing;
9. enlarging a campaign envelope after execution begins;
10. changing code, artifact, authority, environment, algorithm, topology,
   numerical/stochastic/uncertainty policy, seed, stream set, cache key,
   invalidation epoch, exactness label, model, horizon, or scientific meaning;
11. continuing from a missing, corrupt, stale, forked, or non-durable checkpoint;
12. omitting or mismatching the canonical next-counter tuple-set identity;
13. a missing, extra, duplicate, misordered, or terminal-cap tuple in a
    continuation checkpoint;
14. a restarted suffix that differs from uninterrupted execution;
15. using a clean slice boundary as scientific evidence;
16. retrying or continuing after `TERMINAL_REJECTION_CAP`;
17. partial continuation of a declared atomic exact case;
18. silent approximation, truncation, sampling, topology alteration, or
    arbitrary-`N` completion claim;
19. an unaudited infeasibility finding;
20. a result, figure, book, release, or publication permission.

## 14. Candidate evidence boundary

This authority candidate may be validated only with Git inspection, strict
UTF-8/JSON parsing, canonicalization, hashing, schema inspection, closed-set
comparison, integer arithmetic, static cross-reference checks, and exact path-
scope checks. It may not import or run the EBU framework, a project runner,
model, state transition, Gate, transform, benchmark, stochastic draw,
trajectory, simulation, result writer, renderer, or book generator.

All candidate counters for model state advance, trajectory, simulation, Gate,
transform, benchmark, stochastic draw, scientific outcome inspection, result,
figure, book, release, and publication are exactly zero.

## 15. Independent audit and stop condition

AUDITOR 2 must independently verify the exact base/tree/live ref, five-file
scope, preserved accepted bytes, predecessor rows, raw/canonical identities,
normative/mechanical agreement, schema closure and negative cases, identity
hierarchy, non-resetting cumulative accounting, narrow supersession, finite-
problem boundary, stochastic terminal cap, evidence nonpromotion, and zero-
execution boundary.

An independent PASS authorizes only later normal integration if the user
separately permits it. It does not authorize durability implementation, Stage
E, Stage F, outcomes, results, figures, books, main merge, tag, release,
package-index upload, or publication.

`STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_CANDIDATE_COMPLETE`
