# Unified Python Research Framework Specification

**Version:** 0.1.1
**Status:** Phase B specification checkpoint; prospective authority-hash reconciliation; implementation not authorized
**Date:** 2026-08-12
**Authority reconciliation date:** 2026-08-13
**Language:** English
**Purpose:** Specify one versioned, typed, reproducible Python research
framework for Parts IV–IX without implementing it or authorizing scientific
execution.

---

## 1. Executive decision

The project should use one research framework with one scientific object
model, one deterministic event contract, one provenance system, and explicit
stage boundaries. Parts IV–IX may extend that framework, but they must not
create disconnected state definitions, execution engines, receipts, or result
formats.

This document is a specification. It contains definitions, interface
contracts, state-transition tables, pseudocode, registers, and static examples
only. It creates no implementation, JSON schema, accepted experiment
configuration, preregistration, result, or publication authority.

The central architectural rule is:

> Physical measurement, causal inference, policy choice, and institutional
> settlement are four different operations. No framework convenience may
> collapse one into another.

The central dependency rule is:

> Earlier scientific foundations flow into later framework layers. Execution,
> results, interpretation, and institutional decisions may not flow backward
> and silently redefine an earlier foundation.

## 2. Authority, reconciliation, and scope

### 2.1 Authority registers and immutable foundation evidence

#### 2.1.1 Original v0.1 reconciliation record — historical

The original v0.1 specification was reconciled against the following
committed sources at repository `HEAD`
`640d7607b9e2b63ded1170a7b2af605258d91f4c`:

| Source | Required version or role | SHA-256 verified during the original v0.1 task | Historical authority used in v0.1 |
|---|---|---|---|
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | Future-books architecture | `1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558` | Part ordering, framework purpose, required scientific objects, reproducibility, workflow, and stop conditions |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | v0.2 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | Part VI definitions, grouping, comparators, physical group measurement, causal limits, receipt closure, and batching |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | v0.1 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | Part VIII dynamic state, seven-layer separation, deterministic event order, network evolution, objectives, uncertainty, and framework requirements |

This table is immutable historical evidence of what the original v0.1 task
verified. In particular, the books-structure hash beginning `1e4df33b` is
retained only as an original verification hash. It is not a current v0.1.1
implementation authority.

The planning register at that time contained older references to a working
bridge v0.1 because that register predated the committed bridge v0.2. The
original v0.1 task explicitly named v0.2, and the dynamic foundation
explicitly imports v0.2 at commit
`2676912a3d16f7a630cc6f113331e3aa236727e0`. This is an explained version
pointer, not a scientific conflict. This specification uses v0.2 and does
not edit the planning register.

The dynamic foundation states that this specification had not yet begun. The
original v0.1 task separately authorized creating this specification, so that
earlier status statement is satisfied rather than contradicted.

No other mismatch was found among the three sources for the scope of this
document during the original v0.1 reconciliation. If a later review finds a
conflict, the framework must fail closed:
the bridge controls its imported Part VI objects, the dynamic foundation
controls its imported state and event order, and neither may be selectively
rewritten here.

#### 2.1.2 Current v0.1.1 prospective authority register

Revision v0.1.1 prospectively replaces only the active books-structure
authority pointer. The reconciliation began from repository `HEAD`
`dc2620c83718c8fdac67066bd308a4fd6b50b5f9`, where the books-structure
commit changes only `EBU_FUTURE_BOOKS_STRUCTURE.md`. The current authority
set is:

| Source | Current version or role | Current required raw SHA-256 | Current authority used by v0.1.1 |
|---|---|---|---|
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | Current future-books architecture, including the K1–K6 planning programme | `4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c` | Parts IV–IX ordering and future research dependencies, subject to the boundary in §2.1.4 |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | v0.2 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | Unchanged Part VI definitions, grouping, comparators, physical group measurement, causal limits, receipt closure, and batching |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | v0.1 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | Unchanged Part VIII dynamic state, seven-layer separation, deterministic event order, network evolution, objectives, uncertainty, and framework requirements |

The `4dcccf8d...` books-structure hash is the only active books-structure
authority for this specification revision. The superseded `1e4df33b...`
value remains solely in explicitly historical records. This prospective
pointer update changes no imported bridge or dynamic-coordination semantics,
framework object, interface, invariant, event phase, test classification, or
implementation permission.

#### 2.1.3 Immutable `foundation-v0.1.0` evidence

The existing signed tag is immutable historical evidence and is not moved or
reinterpreted by this revision:

| Evidence | Exact identity | Historical meaning |
|---|---|---|
| Signed tag object | `foundation-v0.1.0` / `90646d3c7e1ff2201eab4739e894598b80782b79` | Original documentation/foundation milestone only |
| Tag target | `fa08920a56485962b368bfa032fa284f455413eb` | Unchanged commit named by the signed tag |
| Original specification bytes | `4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38` | Original v0.1 whole-file SHA-256; not the current v0.1.1 specification hash |
| Original I-0 plan bytes | `a1cebfa63528e49d9bada3c6564c7d40616369a45afd97640ff937ae07389674` | Original plan whole-file SHA-256 at the milestone; not a hash of a later amendment |
| Books-structure bytes at the milestone | `1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558` | Original books-structure verification hash; historical only |

Revision v0.1.1 is later prospective documentation. It was not present at,
verified during, or incorporated into `foundation-v0.1.0`.

#### 2.1.4 K1–K6 circuit-network programme boundary

The K1–K6 circuit-network programme adopted through the current books
structure is future Part VI/Part VIII planning only. It:

- does not change I-1 core semantics or the I-0 plan's closed implementation
  file manifest;
- requires a separately authorized future framework/domain extension before
  any adapter, model, fixture, or implementation is added; and
- does not derive or validate EBU from Kirchhoff's laws. Kirchhoff-style
  closure and flow relations remain conditional comparisons or domain models
  whose own assumptions and falsifiers must be frozen prospectively.

No K1–K6 object, electrical constitutive law, resistance-like parameter,
adapter, implementation file, or validation fixture is introduced by this
authority-hash reconciliation.

### 2.2 Preserved Gate 1D-C incident boundary

The following incident record is preserved exactly:

> One official invocation occurred. No receipt was created. No model state
> advanced. The study remains `UNSTARTED`.

This specification does not investigate, modify, retry, invoke, finalize, or
reinterpret Gate 1D-C. It does not authorize a second invocation. Gate 1D-C
protocols, plans, implementation, operational contracts, and incident records
remain outside the work performed here.

### 2.3 Authorized and excluded work

Authorized here:

- specify conceptual Python module boundaries;
- specify typed scientific records and lifecycle states;
- specify deterministic execution and later stochastic extension contracts;
- specify reproducibility, provenance, publication, recovery, and correction
  boundaries;
- specify workflow stages and test categories;
- record decisions, invariants, threats, open questions, and a proposed later
  implementation sequence.

Not authorized here:

- Python implementation or package creation;
- JSON schemas or configuration instances;
- parameter selection for a scientific study;
- preregistration or modification of any frozen preregistration;
- model stepping, simulation, trajectory generation, runner or finalizer use;
- execution of scientific functions under the label of testing;
- scientific interpretation, result publication, commit, or push.

### 2.4 Normative language and claim status

`MUST`, `MUST NOT`, `SHALL`, and `SHALL NOT` are normative requirements for a
future conforming implementation. `SHOULD` records a preferred design that may
be changed only prospectively with a reason. `MAY` marks an extension point.

The framework SHALL preserve the future-books claim-status vocabulary:
definition, algebraic identity, theorem, model-dependent result, tested
implementation property, observed registered result, research hypothesis,
institutional design choice, analogy, and open problem. Artifact metadata
SHALL carry claim status where an artifact supports a claim.

## 3. Exact scientific dependency boundaries

### 3.1 Sequential–Parallel Bridge import

The framework SHALL import the definitions of
`SEQUENTIAL_PARALLEL_BRIDGE.md` v0.2 unchanged. The bridge remains the sole
authority for the meaning of:

- represented field distortion;
- transition EBU;
- action transformation;
- effective interval, write support, and constraint support;
- compatible accounting boundary;
- dependency edge, joint-transition group, and parallel group;
- admissible comparator set;
- quantity-fixed and rule-replayed comparators;
- group EBU;
- same-baseline field non-additivity;
- comparator-relative interaction;
- state equivalence and EBU equivalence;
- causally identified child contribution;
- institutional settlement share and group residual;
- group receipt, child action record, receipt batch, committed field, delayed
  EBU component, and nonserializable group.

The imported core equations are:

\[
\boxed{EBU(X_0\rightarrow X_1)=D(X_0)-D(X_1)}
\]

\[
\boxed{EBU_{\mathrm{seq},\pi}=D(X_0)-D(X_{\pi})}
\]

\[
\boxed{EBU_G=D(X_0)-D(X_G)}
\]

\[
\boxed{N_G=EBU_G-\sum_{i\in G}
\left[D(X_0)-D(X_i^{(0)})\right]}
\]

\[
\boxed{I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}
=D(X_{\pi})-D(X_G)}
\]

and institutional settlement closure is:

\[
\boxed{\sum_{i\in G}S_i+R_G=M_G},
\qquad M_G=EBU_G.
\]

These formulas are imports, not locally redefined alternatives. A future
implementation SHALL expose bridge-owned interfaces and SHALL record the exact
bridge source version and hash used by every accepted configuration.

The exact bridge dependency-graph grouping rule is normative. A framework
adapter may encode it, but may not weaken it to “same time,” “same batch,” or
“same provider.” Minimal joint-transition groups remain the connected
components of the bridge-defined dependency graph, including its transitive
closure and compatible-boundary requirement.

### 3.2 Dynamic Coordination Foundation import

The framework SHALL import the dynamic coordination state unchanged:

\[
\boxed{Z_k=(x_k,g_k,q_k,c_k,\ell_k)}.
\]

The components retain their v0.1 meanings:

- `x_k`: typed physical stocks, field variables, accumulated resource use,
  physical condition, and required clock-dependent quantities;
- `g_k`: provider-network topology and node or edge condition;
- `q_k`: admitted but unserved demand, congestion queues, and in-transit
  payloads not already represented in `x_k`;
- `c_k`: accepted commitments, reservations, deadlines, and outstanding
  obligations;
- `ell_k`: delayed-effect events with due epochs, typed payloads or
  transformations, provenance, and unresolved status.

When policy memory affects later decisions, the augmented closed-loop state
also retains its imported meaning:

\[
\widetilde Z_k=(Z_k,m_k^\mu).
\]

The framework representation of this imported pair SHALL use the exact
physical `StatePayloadHash` and the separately typed
`PolicyMemoryPayloadHash` defined in §§4.3 and 6.4. Controller memory remains
informational policy state; it is never inserted into `x_k`, `g_k`, `q_k`,
`c_k`, or `ell_k` merely to make replay convenient.

For a bridge accounting boundary `B`, the required projection remains:

\[
X_k^{\mathcal B}=\Psi_{\mathcal B}(Z_k).
\]

The framework SHALL keep the following seven layers separately typed even if
one audit view joins their references:

| Layer | Imported role | Forbidden conflation |
|---|---|---|
| Physical state `x_k` | Stocks, conditions, burdens, physical clocks | Measurement or ledger balance |
| Network topology `g_k` | Providers, typed connections, availability | Route-selection policy |
| Coordination policy `mu` | Rule mapping permitted information to proposals | Physical law or causal contribution |
| Objective family `J` | Declared criteria for comparing histories | Feasibility, morality, or universal scalar |
| Constraints `F_k` | Physical, safety, contractual, informational, and institutional admissibility | Objective to maximize |
| Measurements `y_k` | Time-stamped calibrated observations with uncertainty and provenance | Complete physical state |
| Institutional allocation `lambda` | Priority, access, settlement, residual, responsibility, or ownership assignment | Group EBU or identified causality |

### 3.3 Exact deterministic within-epoch order

The dynamic foundation's v0.1 within-epoch order is imported unchanged as the
default deterministic event contract:

1. Mature delayed effects and arrivals due at the start of epoch `k`.
2. Apply declared exogenous topology changes, failures, repairs, and capacity
   deratings effective at `k`.
3. Record the resulting state and make the permitted measurement available to
   the policy.
4. Propose starts, stops, reservations, releases, routes, and reroutes using
   only permitted information.
5. Screen prerequisites, deadlines, commitments, safety constraints,
   topology, and capacity.
6. Admit, reject, defer, or partially accept requests using the frozen
   allocation and queue disciplines.
7. Build joint-transition groups using the imported Part VI rule and form the
   exact joint-transition proposal for every accepted group without yet
   mutating physical state.
8. Validate a disjoint update-ownership record, then commit each proposed
   physical transition, completed flow, conversion, loss, consumption,
   congestion effect, expiry, resource use, and physical coordination burden
   exactly once while recording the corresponding accounts.
9. Register new in-transit payloads and delayed-effect events; update
   commitments, reservations, and unresolved statuses.
10. Apply declared natural drive for the remainder of the epoch and produce
    the end-of-epoch record.

A future replacement requires a prospective revision of the dynamic
foundation or an authority it explicitly recognizes. A configuration cannot
reorder these phases ad hoc.

### 3.4 Part VII route boundary

Part VII route semantics are not frozen. Until a separate Part VII foundation
is approved:

- `ProviderNetwork` may represent typed nodes, directed connections,
  availability, capacity, and declared delays as specified by the dynamic
  foundation;
- `RouteRef` and `RoutePlan` are provisional interface records;
- an edge is only a model-declared typed connection;
- graph distance is not automatically geographic or physical distance;
- reachability is not delivery;
- edge delay, loss, conversion, and risk are declared model parameters, not
  universal laws;
- a path does not identify causal contribution, actor credit, settlement, or
  institutional responsibility;
- rerouting may replace only an unfinished suffix and may not rewrite
  completed segments or effects.

A route operation requiring an unfrozen physical meaning SHALL return an
explicit `UNRESOLVED` or `OUT_OF_BOUNDARY` result. It SHALL NOT invent a
default Part VII law.

### 3.5 Scientific authority direction

The allowed dependency direction is:

```text
frozen foundations and protocols
        |
        v
typed registries and versioned scientific objects
        |
        v
accepted configuration / preregistration
        |
        v
implementation + permitted validation evidence
        |
        v
accepted execution binding + pre-execution audit
        |
        v
external authorization -> execution -> immutable traces and results
        |
        v
interpretation -> figures -> evidence ledger -> publication
```

Policy and institutional settlement may consume physical and causal records,
but they may not redefine them. Results may challenge a hypothesis through an
authorized interpretation stage, but they may not mutate the preregistration,
foundation, accepted configuration, implementation identity, or original
result artifact.

## 4. Framework conformance model

### 4.1 Conforming research package

A research package conforms to v0.1 only if it:

1. uses pinned versions and hashes for every scientific dependency;
2. represents quantities, boundaries, horizons, and statuses explicitly;
3. separates proposal construction from physical-state commitment;
4. applies the imported grouping and comparator rules unchanged;
5. enforces the exact deterministic event phases;
6. prevents policies from accessing future or outcome data;
7. makes all accepted configurations, accepted execution bindings, and
   produced result artifacts immediately immutable;
8. produces a reconstructible canonical scientific trace, separate run
   envelope, and pre-publication execution/result provenance manifest;
9. records failures, partials, pending effects, unresolved terms, and
   out-of-boundary effects without replacing them with zero;
10. enforces external workflow authorization before every protected
    interface, including any scientific execution;
11. pins initial policy memory, durably records every stateful memory
    transition, and keeps it separate from physical state; and
12. limits full deterministic trace equality to normally completed or
    equal-schedule declared-fault executions while preserving any durable
    prefix from undeclared operational failure.

### 4.2 Common object envelope

Every versioned framework object SHALL have a common conceptual envelope:

| Field | Type | Requirement |
|---|---|---|
| `object_id` | `ScientificId` | Stable logical identity; never inferred from a label or path |
| `object_kind` | registered enum | Determines the applicable schema family |
| `schema_id` | `ScientificId` | Identifies the record contract |
| `schema_version` | `SemanticVersion` | Pins the contract used to validate the object |
| `object_version` | `SemanticVersion` | Pins the immutable object-content version |
| `authority_refs` | ordered `ObjectRef[]` | Pinned normative foundations, protocols, or parent objects; never an operation-granting `StageAuthorization` |
| `supersedes_ref` | optional `ObjectRef` | Points to an earlier immutable version; never overwrites it |
| `object_content_payload` | kind-specific immutable value | Complete hash-worthy scientific or operational meaning governed by the named schema |
| `object_content_hash` | `ObjectContentHash` | Hash of the canonical object-content preimage defined in §4.3; never part of its own preimage |
| `lifecycle_status` | typed status | Draft, accepted, superseded, or other kind-specific registry state; excluded from the object-content preimage |
| `record_metadata_ref` | optional `RecordMetadataRef` | Storage and other non-content provenance metadata excluded from scientific hashes |

An `ObjectRef` SHALL contain `object_id`, `object_version`, and
`object_content_hash`. A logical identifier without version and hash is not
sufficient inside an accepted configuration, execution binding, or result.
Common-envelope `authority_refs` identify normative dependencies; they do not
grant workflow permission. An operation-granting `StageAuthorization` always
travels as an external input to the interface it authorizes.

### 4.3 Non-self-referential hash projections

Every hash SHALL name its projection and domain. A conforming implementation
SHALL NOT hash a serialized record containing the field in which that same
hash is stored.

The canonical object-content preimage is exactly the canonical serialization
of:

```text
ObjectContentPreimageV1 = {
    hash_domain: "ebu.object-content.v1",
    object_id,
    object_kind,
    schema_id,
    schema_version,
    object_version,
    authority_refs,
    supersedes_ref,
    object_content_payload
}
```

The object content hash is:

```text
ObjectContentHash = SHA-256(CANONICAL(ObjectContentPreimageV1))
```

`object_content_hash` itself, lifecycle status, signatures, authorization
records, record-creation time, ingestion time, wall-clock time, host and
process metadata, storage location, database keys, cache metadata,
publication metadata, and presentation annotations are excluded from this
preimage. `object_content_payload` SHALL NOT contain the same object's
`object_content_hash` directly, through an alias, or through an embedded copy
of the enclosing record.

For `SystemState`, a second independent projection identifies the exact
scientific state payload:

```text
StatePayloadPreimageV1 = {
    hash_domain: "ebu.state-payload.v1",
    state_schema_ref,
    epoch,
    physical_state_x,
    topology_state_g,
    queue_and_transit_state_q,
    commitment_state_c,
    delayed_effect_state_ell,
    declared_external_inputs_applied
}

StatePayloadHash = SHA-256(CANONICAL(StatePayloadPreimageV1))
```

The `StatePayloadHash` preimage excludes `state_payload_hash`, object identity,
object version, predecessor links, update-ownership records, trace references,
storage metadata, and run provenance. The `SystemState` object's
`ObjectContentPreimageV1` contains the state payload values and the scientific
references required by its schema, not either derived hash field. Thus the
object content hash and state payload hash are independently reproducible and
neither is self-referential.

For a stateful policy, policy memory has its own independent payload
projection:

```text
PolicyMemoryPayloadPreimageV1 = {
    hash_domain: "ebu.policy-memory-payload.v1",
    policy_ref,
    memory_schema_ref,
    available_for_decision_epoch,
    resolution_state,
    memory_payload
}

PolicyMemoryPayloadHash =
    SHA-256(CANONICAL(PolicyMemoryPayloadPreimageV1))
```

The preimage excludes `policy_memory_payload_hash`, the memory object's
identity and version, predecessor-memory and decision-record links, object
content hash, trace references, durability metadata, storage metadata, and run
provenance. The `PolicyMemoryState` object-content preimage contains the
actual memory payload and its scientific lineage references, not either
derived hash field.

For one active stateful policy in a closed-loop arm, the replay state is
identified by both independent payload hashes:

```text
AugmentedClosedLoopReplayStatePreimageV1 = {
    hash_domain: "ebu.augmented-closed-loop-replay-state.v1",
    physical_state_payload_hash,
    policy_memory_payload_hash
}

AugmentedClosedLoopReplayStateHash =
    SHA-256(CANONICAL(AugmentedClosedLoopReplayStatePreimageV1))
```

This hash identifies the replay pair; it does not merge policy memory into
physical state or permit either component hash to substitute for the other.
An open-loop schedule or explicitly stateless policy uses no augmented hash
and records `policy_memory_ref=NOT_APPLICABLE`. A multi-controller extension
must prospectively define a canonical composite memory object rather than
silently ordering several memory hashes.

`RecordMetadata` is a non-scientific envelope that MAY contain storage URI,
database identity, ingestion and wall-clock timestamps, host/process
metadata, cache location, transport metadata, presentation annotations, and
operational provenance. Changing that metadata SHALL NOT change an object
content, physical-state-payload, policy-memory-payload, or augmented-replay-
state hash. When provenance changes scientific interpretation or
reproducibility, it SHALL be represented as a separately content-hashed
scientific provenance object and referenced explicitly from the applicable
object-content payload or execution binding; it must not be hidden in
`RecordMetadata`.

Artifact bytes have a third distinct, binary-framed identity:

```text
ArtifactBytePreimageV1 =
    UTF8("ebu.artifact-bytes.v1")
    || 0x00
    || UINT64_BE(length(exact_artifact_bytes))
    || exact_artifact_bytes

ArtifactByteHash = SHA-256(ArtifactBytePreimageV1)
```

An artifact object's content hash covers its scientific artifact record; its
`ArtifactByteHash` covers the referenced bytes. Neither substitutes for a
`StatePayloadHash`. A conventional raw SHA-256 used for an external source
file SHALL be labelled as such and is not an `ArtifactByteHash`.

### 4.4 Identifier and version grammar

A `ScientificId` SHALL use ASCII and the form:

```text
ebu:<kind>:<namespace>:<local-id>
```

Each segment SHALL begin with a lowercase alphanumeric character and may then
contain lowercase alphanumerics, `.`, `_`, or `-`. A segment SHALL NOT encode
a mutable file path, display name, current branch, or database row number.

`SemanticVersion` SHALL use `MAJOR.MINOR.PATCH`:

- `MAJOR`: incompatible scientific or schema meaning;
- `MINOR`: backward-compatible added meaning;
- `PATCH`: clarification that does not change scientific content.

Draft content may be revised in place only before acceptance and only when no
other accepted object refers to it. Acceptance immediately freezes the exact
`ObjectContentPreimageV1`, `object_content_hash`, object version, and every
scientific field; immutability does not wait for execution to begin. Any
correction or change creates a new version and a `supersedes_ref`.

### 4.5 Explicit completeness and resolution states

Absence SHALL be typed. The following `ResolutionState` values are common
across objects:

| State | Meaning | Required accompanying record |
|---|---|---|
| `PRESENT` | Value is available within the declared boundary | Value and provenance |
| `PENDING` | Value or effect is expected later | Due condition or review horizon |
| `FAILED` | Required operation or measurement failed | Failure code, stage, and evidence |
| `PARTIAL` | A declared subset completed | Completed and missing portions |
| `UNRESOLVED` | Evidence is insufficient to select a valid value | Reason, owner if any, and next permitted resolution stage |
| `OUT_OF_BOUNDARY` | Effect is known to lie outside the declared account | Boundary edge and non-inclusion statement |
| `NOT_APPLICABLE` | Contract proves the field does not apply | Applicability reason |

`null`, an empty list, zero, `NaN`, and omission SHALL NOT substitute for one
of these states. `UNKNOWN` may exist as an uncertainty classification, but
shall not erase whether a field is pending, failed, unresolved, or outside the
boundary.

## 5. Typed scientific primitives

### 5.1 Quantity and dimensional type

A `Quantity` SHALL contain:

| Field | Meaning |
|---|---|
| `magnitude` | Exact integer, exact rational, or declared decimal value; binary floating-point is not a canonical interchange form |
| `unit_ref` | Versioned unit definition |
| `dimension_ref` | Versioned physical or declared institutional dimension |
| `resource_type_ref` | Optional but mandatory for resource-bearing quantities |
| `region_ref` | Region or node when spatial identity matters |
| `time_basis` | Required for rates |
| `sign_convention_ref` | Required when positive and negative carry scientific meaning |
| `uncertainty_ref` | Measurement or model uncertainty, when present |
| `resolution_state` | Explicit completeness state |

Addition and comparison require compatible dimensions, units, resource types,
regions or a declared parent aggregation, time bases, and accounting
boundaries. Conversion requires a pinned `ConversionRule`; a price, policy
weight, or settlement rate is not a physical conversion coefficient.

### 5.2 Registries

The framework SHALL maintain versioned registries for:

- dimensions;
- units and exact or bounded unit conversions;
- resource and service types;
- sign conventions;
- regions, nodes, edges, providers, and actors;
- accounting boundaries;
- clock systems, epochs, and horizons;
- uncertainty meanings;
- claim statuses and artifact kinds;
- failure and resolution codes.

A registry entry is a scientific object and follows the immutability rules.
Aliases are presentation-only and SHALL resolve to one pinned entry before an
accepted configuration is hashed.

### 5.3 Region and accounting boundary

A `Region` SHALL declare stable identity, membership rule, optional parent,
spatial interpretation, and validity interval. A changing membership creates a
new region version.

An `AccountingBoundary` SHALL declare:

1. included state schema and distortion version;
2. resource and service types with units;
3. included providers, actors, nodes, edges, and regions;
4. initial epoch, evaluation horizon, and later-effect treatment;
5. lifecycle stages and external physical effects;
6. topology, route, and failure scope;
7. commitments, reservations, queues, and coordination overhead;
8. measurement systems, observation ages, uncertainty, and missing variables;
9. natural drive and external inputs;
10. objective and comparator references when the boundary is used for a
    comparison;
11. institutional rules, kept separately typed; and
12. unresolved cross-boundary effects.

Values from incompatible boundaries SHALL NOT be added. A compatible parent
boundary must be accepted first.

### 5.4 Time and horizon

`Instant`, `Duration`, `Epoch`, and `Horizon` are distinct types.

A `Horizon` SHALL declare clock reference, start, terminal point, endpoint
inclusion, resolution, measurement epochs, completion rule, settlement rule,
and treatment of effects due after the terminal point. Pending effects after
the horizon remain pending or are explicitly out of boundary; they are not
zero.

An event timestamp and its record-creation timestamp SHALL be different
fields. Observation time, availability time, decision time, action start,
completion, verification, and settlement time SHALL not be conflated.

### 5.5 Uncertainty primitives

The type system SHALL distinguish:

| Kind | Meaning |
|---|---|
| `EXACT` | Exact under the declared representation |
| `MEASUREMENT_INTERVAL` | Bounded observation error with units and calibration provenance |
| `ADMISSIBLE_SET` | Prospectively declared deterministic or robust set |
| `PROBABILITY_MODEL` | Pinned distribution and parameter provenance |
| `MODEL_DISCREPANCY` | Declared mismatch between model and represented system |
| `ADVERSARIAL_SET` | Declared bounded adversarial choice |
| `UNKNOWN` | No justified set or distribution is available |
| `OUT_OF_SET` | Realized or supplied value lies outside the accepted uncertainty contract |

A range SHALL NOT imply a probability distribution. Uncertainty in unlike
dimensions SHALL not be aggregated without a declared, dimensionally valid
mapping.

## 6. Versioned scientific object schemas

The following are typed record specifications, not JSON schemas and not
implementation classes.

### 6.1 `SystemState` and `RepresentedState`

`SystemState` records the complete declared dynamic state `Z_k` for one schema
version. It does not claim to contain all of reality.

| `SystemState` field | Contract |
|---|---|
| `state_ref` | Common immutable object envelope |
| `epoch` | Exact scientific epoch |
| `physical_state` | Typed `x_k` entries |
| `topology_state_ref` | Versioned `g_k` snapshot |
| `queue_and_transit_state` | Typed `q_k` entries |
| `commitment_state` | Typed `c_k` entries |
| `delayed_effect_state` | Typed `ell_k` entries |
| `external_input_refs` | Inputs applied up to this state |
| `update_ownership_ref` | Epoch-wide proof record covering every state-mutating phase |
| `predecessor_state_ref` | Required except for an accepted initial state |
| `state_payload_hash` | Independent `StatePayloadHash` from §4.3 |

`state_payload_hash` is a derived sibling validation field. It is excluded
from both its own preimage and the `SystemState` object-content preimage; the
latter hashes the actual state payload values and scientific references.
`SystemState` contains only the imported physical coordination state `Z_k`.
It SHALL NOT contain policy memory; an augmented closed-loop replay state
references the physical and memory payload hashes separately.

`RepresentedState` is the result of a pinned boundary projection
`Psi_B(SystemState)`. It SHALL record source state, boundary, projection
version, included and excluded coordinates, missing-variable statuses, and
projection hash.

Invariants:

- projection does not mutate `SystemState`;
- every coordinate required by the distortion domain is `PRESENT` or the
  projection fails closed;
- equal represented distortion does not imply equal represented state;
- omitted relevant effects are reported, not silently dropped.

### 6.2 `DistortionModel`

| Field | Contract |
|---|---|
| `distortion_ref` | Immutable identity and version |
| `domain_schema_ref` | Exact `RepresentedState` schema |
| `boundary_ref` | Compatible accounting boundary |
| `parameter_refs` | Frozen parameter objects with dimensions |
| `codomain` | Declared scalar type and unit or dimension |
| `domain_predicate` | Static admissibility conditions |
| `evaluation_contract_ref` | Pinned mathematical evaluation contract; no implementation artifact identity |
| `numerical_policy_ref` | Arithmetic, precision, rounding, and tolerance rules |
| `scientific_status` | Definition, theorem-supported model, model-dependent, or other claim status |

An evaluation outside the declared domain SHALL return `OUT_OF_BOUNDARY` or a
typed domain failure. It SHALL NOT extrapolate silently. A distortion model
change creates a new version; a result may never be re-evaluated under a new
version and presented as the original result.

### 6.3 `Action` (`ActionDefinition`) and `ActionInstance`

The versioned `Action` scientific object is represented by an
`ActionDefinition`: the imported bridge transformation contract plus typed
metadata:

- action type and transformation version;
- required predecessor-state schema;
- typed input and output quantities;
- write and constraint supports;
- prerequisites and domain predicate;
- declared physical effects, conversions, losses, resource use, and burdens;
- completion and failure conditions;
- compatible boundaries and horizons;
- deterministic or later stochastic semantics.

`ActionInstance` binds that definition to a request:

| Field | Contract |
|---|---|
| `action_instance_ref` | Stable versioned identity |
| `definition_ref` | Pinned `ActionDefinition` |
| `requesting_actor_ref` | Actor identity; not causal credit |
| `responsible_provider_ref` | Provider identity; not settlement share |
| `requested_quantities` | Typed quantities |
| `accepted_quantities` | Typed quantities or explicit unresolved state |
| `placement_ref` | Provider/node/region reference |
| `route_ref` | Optional and provisional under Part VII boundary |
| `effective_interval` | Imported bridge meaning |
| `write_support` | Imported bridge meaning |
| `constraint_support` | Imported bridge meaning |
| `prerequisite_refs` | Frozen requirements |
| `deadline_and_horizon` | Typed time contract |
| `commitment_refs` | Accepted obligations |
| `reservation_refs` | Supporting capacity claims |
| `measurement_contract_ref` | Required observations and uncertainty |
| `boundary_ref` | Compatible boundary |
| `status` | Explicit lifecycle state |

Action lifecycle:

| From | Event | To | Required record |
|---|---|---|---|
| `PROPOSED` | request screened | `REJECTED`, `DEFERRED`, `PARTIALLY_ACCEPTED`, or `ACCEPTED` | Admission decision |
| `PARTIALLY_ACCEPTED` | actor/provider accepts conditions | `RESERVED` or `CANCELLED` | Accepted quantity and conditions |
| `ACCEPTED` | capacity support acquired | `RESERVED` | Reservation references |
| `RESERVED` | start conditions met | `ACTIVE` | Start event and live predecessor state |
| `ACTIVE` | all completion conditions met | `COMPLETED` | Completion evidence |
| `ACTIVE` | only a declared subset completes | `PARTIAL` | Completed and missing effects |
| Any nonterminal | declared failure | `FAILED` | Failure and physical consequence record |
| Any permitted nonterminal | valid cancellation or expiry | `CANCELLED` or `EXPIRED` | Rule, actor, and retained consequences |
| Any state lacking required evidence | resolution cannot be completed | `UNRESOLVED` | Missing evidence and open obligations |

No lifecycle transition deletes the preceding record.

### 6.4 `Schedule` and `Policy`

A `Schedule` is a finite, immutable arrangement of action instances and
coordination events. It SHALL declare starts, completions, precedence, allowed
overlap, placements, provisional routes, reservations, capacity allocation,
queue discipline, failure/rerouting rules, measurement epochs, horizon, and
bridge comparator references.

An accepted open-loop schedule is complete before evolution. It has no access
to later observations.

A `Policy` SHALL declare:

| Field | Contract |
|---|---|
| `policy_ref` | Immutable version |
| `decision_interface_ref` | Typed input view and output proposal schema |
| `information_contract_ref` | Visible fields, observation ages, privacy restrictions, and availability times |
| `memory_mode` | Exactly `STATELESS` or `STATEFUL` |
| `memory_schema_ref` | Required for `STATEFUL`; `NOT_APPLICABLE` for `STATELESS` |
| `objective_ref` | Declared objective family; not hidden in code |
| `constraint_refs` | Hard admissibility conditions |
| `tie_break_rule_ref` | Total deterministic ordering when required |
| `failure_behavior` | Fail closed, fallback, or unresolved rule |
| `decision_rule_ref` | Pinned scientific decision rule or declarative algorithm contract; no implementation artifact identity |

A policy returns proposals. It does not mutate physical state, admit its own
requests, perform settlement, or read privileged engine internals.
Implementation and source artifacts that realize a policy are mapped to the
policy interface only in a later `ExecutionBinding`; they are never added to
the accepted `Policy` or scientific configuration.

#### 6.4.1 `PolicyMemoryState` and memory transition

A `PolicyMemoryState` is a separately typed immutable scientific object that
represents the decision-relevant \(m_k^\mu\) imported from the Dynamic
Coordination foundation. It may contain filters, learned parameters whose
update rule is scientifically frozen, prior permitted messages, internal
policy clocks, unresolved policy decisions, or an equivalent sufficient
statistic. It is informational policy state, not physical state,
measurement, causal attribution, or institutional settlement.

| Field | Contract |
|---|---|
| `policy_memory_ref` | Common immutable object envelope |
| `policy_ref` | Exact stateful `Policy` reference |
| `memory_schema_ref` | Exact schema declared by the policy |
| `available_for_decision_epoch` | Epoch at which this memory may be consumed; initial memory uses epoch `0` |
| `memory_payload` | Complete typed decision-relevant memory or explicit resolution state |
| `resolution_state` | Normally `PRESENT`; any other state invokes the policy's frozen failure behavior before proposal use |
| `predecessor_memory_ref` | Exact prior memory reference; `NOT_APPLICABLE` only for accepted initial memory |
| `originating_decision_ref` | Exact decision record that produced it; `NOT_APPLICABLE` only for accepted initial memory |
| `policy_memory_payload_hash` | Independent non-self-referential `PolicyMemoryPayloadHash` from §4.3 |

A decision at epoch `k` consumes the exact memory whose
`available_for_decision_epoch=k` and returns a new `PolicyMemoryState` for
epoch `k+1`. Even when the payload is unchanged, the next epoch and lineage
produce a new immutable object; the prior memory is never mutated. A
stateful policy SHALL produce exactly one next-memory state for every
successfully committed policy decision, including an explicit carry-forward
state when its values do not change.

`policy_propose` SHALL return a `PolicyDecisionRecord`, proposal set, and
candidate next memory without mutating `Z_k`. Before screening or admission,
the execution layer SHALL validate the before/after memory hashes, schema,
epoch, predecessor, permitted information read set, and policy reference,
then atomically and durably append the decision record, next memory, and
corresponding canonical policy-decision trace row or its transactional row
material. The decision record contains the exact information-view hash,
proposal hash, before-memory hash, after-memory hash, and decision coordinate.
A failed durability operation advances none of the durable policy memory,
decision record, or canonical row and stops before physical admission.
Policy-memory transition ownership is separate from physical
`EpochUpdateOwnership`.

### 6.5 `ProviderNetwork`, `Provider`, and provisional `RoutePlan`

`ProviderNetwork` follows the imported provisional structure
`g_k=(V_k,E_k,m_k)` and SHALL contain:

- stable provider, node, and edge identities;
- resource and service types;
- direction and connection type;
- topology validity interval;
- availability/degradation/failure/repair state;
- installed and usable capacity references;
- declared delay, conversion, loss, and uncertainty references;
- versioned topology-change events.

A `Provider` may offer, transform, store, measure, route, or accept a typed
resource or service. Provider identity SHALL NOT imply ownership, causal
contribution, permission, priority, or settlement.

A provisional `RoutePlan` SHALL record a requested typed origin, destination,
ordered segment references, planning epoch, information snapshot, expected
capacity and delay under declared models, unfinished suffix, and route status.
It SHALL carry `route_semantics_status=PROVISIONAL_PART_VII`. Route-derived
physical claims unavailable under the current foundation remain unresolved.

### 6.6 Commitments and reservations

A `Commitment` SHALL contain provider, beneficiary, typed service or quantity,
time window, conditions, guarantee class, status, breach rule, and references
to its quote and supporting reservations.

A `Reservation` SHALL contain action, capacity locus, resource type, interval,
reserved quantity, admission-time capacity snapshot, uncertainty rule,
priority rule reference, release condition, and status. It is a capacity claim,
not material stock or completed service.

For applicable resource `r`, capacity locus `e`, and epoch `k`, admission must
respect the imported condition:

\[
\sum_i R_{i,e,r,k}\leq U_{e,r,k}.
\]

If later capacity falls below commitments, the framework records a
`RESERVATION_SHORTFALL`; it does not edit the original reservation or make the
inequality disappear.

### 6.7 Capacity, queues, congestion, and admission

A `CapacityRecord` SHALL distinguish installed, availability factor, usable,
reserved, admitted, and completed capacity. For applicable flows:

\[
0\leq\sum_i f_{i,e,r,k}\leq U_{e,r,k}.
\]

An `AdmissionDecision` SHALL partition a newly presented compatible request
quantity:

\[
b_{e,r,k}=a_{e,r,k}+j_{e,r,k}+d_{e,r,k},
\]

where `a` is admitted to the queue, `j` rejected, and `d` left pending outside
the queue.

For the foundation's lossless single queue, the queue record SHALL preserve:

\[
q_{e,r,k+1}=q_{e,r,k}+a_{e,r,k}-f_{e,r,k}-z_{e,r,k}.
\]

Rejected or not-yet-admitted demand is never subtracted from the admitted
queue. Priority and allocation rules are separate policy or institutional
objects and SHALL be pinned.

`Congestion` is present only when load or a queue meets a binding capacity or
service rule and changes completion, delay, loss, or feasibility. High
utilization alone is not congestion.

### 6.8 Delays, in-transit items, and delayed effects

A `DelayRecord` SHALL contain total elapsed duration, typed component
durations, the non-overlap or explicit-additivity rule, state/load dependence,
and provenance. Overlapping causal annotations SHALL not be summed as elapsed
time twice.

An `InTransitRecord` SHALL preserve payload, origin, destination, current
segment, dispatch epoch, earliest arrival, route-plan version, action and
group provenance, and present status.

A `DelayedEffect` SHALL contain due epoch, typed state change or measurement
obligation, originating provenance, causal-status field, boundary, and status:
`SCHEDULED`, `MATURED`, `PENDING`, `CANCELLED`, `FAILED`, or `UNRESOLVED`.
Provenance linkage alone does not establish causal attribution.

### 6.9 Measurement and observation

A `Measurement` SHALL contain measured object and coordinate, value or
explicit resolution state, unit, measurement epoch, availability epoch,
calibration reference, uncertainty, instrument/method version, operator or
automated process identity, boundary, and raw-evidence reference where
permitted.

The physical state and its measurement remain different objects. A policy may
see only measurements available under its information contract. Later
measurements may correct a provisional record through an authorized
correction, but may not be backfilled into an earlier policy input.

### 6.10 Quote

A `Quote` SHALL contain:

- quote identifier and version;
- observation and state references used;
- action or group request;
- distortion, boundary, parameter, and uncertainty versions;
- active committed-field snapshot;
- accepted quantities and conditions;
- predicted value or envelope with units;
- guarantee class and institutional responsibility;
- issue time, validity interval, expiry, and acceptance status;
- unresolved or out-of-boundary terms;
- scientific computation-dependency references when computed; observed
  source/runtime instance provenance remains in a separately hashed provenance
  record or non-scientific run metadata as applicable.

Quote lifecycle is `DRAFT -> ISSUED -> ACCEPTED | REJECTED | EXPIRED`, with
`WITHDRAWN`, `FAILED`, and `UNRESOLVED` available only through declared rules.
An accepted quote is immutable. Actual measurement does not rewrite it.

### 6.11 Receipt and group receipt

A `Receipt` SHALL preserve request, quote, acceptance, action definition and
instance, predecessor and endpoint states, measurements, physical EBU,
status, uncertainty, delayed-effect horizon, actor lines, institutional
settlement, residual, and provenance. When a closed-loop decision led to the
action, it SHALL also reference the immutable policy decision and its
before/after memory payload hashes; those informational references do not
enter physical EBU or settlement closure.

A group receipt SHALL additionally preserve every bridge-required field,
including child actions, effective intervals, supports, dependency edges,
grouping decision, accepted quantity vector, group endpoint, `M_G`, optional
`N_G`, admissible comparators, optional interaction values, causal-evidence
status, settlement rule, child shares, and `R_G`.

Physical measurement, causal contribution, and settlement SHALL occupy
different fields with different types. If causal evidence is insufficient,
the child causal status is `UNRESOLVED` or `UNIDENTIFIED`; an allocation rule
does not fill it.

Receipt lifecycle:

| Status | Meaning |
|---|---|
| `OPEN` | Execution or required observation is ongoing |
| `PROVISIONAL` | Immediate record exists; later effects or verification remain pending |
| `SETTLED` | Declared settlement horizon and closure conditions are met |
| `FAILED` | Required receipt production or underlying action failed; consequences retained |
| `PARTIAL` | Only a declared portion completed or was observed |
| `UNRESOLVED` | Closure is impossible with current evidence |
| `CORRECTED_BY` | Original immutable record points to a separately authorized correction |

### 6.12 Ledger and evidence ledger

A `Ledger` is an append-only ordered collection of immutable entries. Each
entry's scientific or institutional payload SHALL contain its predecessor
entry object-content hash, pinned object references, applicable scientific
event time, responsible actor/authority identity when semantically relevant,
operation, and status transition. The entry has its own non-self-referential
object content hash. Record/ingestion time, host process identity, storage
location, and transport details belong in `RecordMetadata` or a run envelope,
not in the scientific entry preimage. A ledger view may aggregate entries but
may not replace them.

Distinct ledgers SHALL exist, or be distinctly typed, for:

- physical measurements and transitions;
- quotes and commitments;
- reservations and queues;
- receipts and physical closure;
- causal claims and evidence;
- institutional settlement and residuals;
- experiment workflow and authorization;
- publication and correction;
- evidence linking claims, results, summaries, figures, and manuscripts.

An `EvidenceLedgerEntry` SHALL state the claim, claim status, supporting and
contradicting artifact references, derivation or analysis version, figure or
table references, limitations, and authorization stage. A figure may never be
its own sole provenance.

### 6.13 `ExperimentConfiguration`

An `ExperimentConfiguration` uses the common envelope for identity, schema,
version, and its derived object content hash. Its `object_content_payload`
SHALL contain all and only the scientific choices required to interpret a
future run:

- scientific question, hypotheses, falsifiers, nonclaims, and claim statuses;
- worlds, arms, comparators, controls, and ordering;
- pinned state, distortion, action, schedule or policy, provider-network, and
  provisional route objects;
- exact accepted initial `PolicyMemoryState` reference for every stateful
  policy arm, or `NOT_APPLICABLE` for an open-loop or stateless arm;
- boundary, units, regions, horizons, event-order version, and natural drive;
- uncertainty sets or probability models;
- metrics, tolerances, missing-data rules, outcome classifications, and
  analysis plan;
- deterministic or stochastic execution mode;
- exact accepted `FaultSchedule` reference for a prospectively declared
  fault-injection study, otherwise `NOT_APPLICABLE`;
- scientific seeds and random-stream ownership if stochastic; and
- scientific measurement, observation, and derived-analysis requirements.

The scientific configuration SHALL NOT contain, directly or transitively
through its referenced scientific objects, implementation-artifact hashes,
result-producing source-code or dependency hashes, an execution identity,
runtime or host constraints, an execution entry point, storage destinations,
an artifact publication contract, an execution authorization, or operational
exclusions. Pinned hashes of normative scientific foundations, protocols, and
scientific object definitions remain required authority references; they are
not implementation bindings. The later operational bindings do not belong to
preregistered scientific content.

For a stateful policy, the initial memory reference SHALL match the exact
policy and memory schema, have `available_for_decision_epoch=0`, have no
predecessor or originating decision, be `PRESENT`, and pin both object content
and policy-memory payload hashes. Acceptance fails if it is absent or if a
stateless policy supplies one. A fault schedule may enter the configuration
only prospectively as a named scientific study input; an undeclared runtime
interruption or durability failure may never be backfilled as that schedule.

Lifecycle:

| Status | Mutation rule |
|---|---|
| `DRAFT` | May change with recorded draft history |
| `REVIEWED` | Review evidence attached; still not executable |
| `ACCEPTED` | Immediately immutable; object content hash frozen |
| `SUPERSEDED` | Remains immutable and points to replacement |
| `REVOKED_BEFORE_EXECUTION` | Cannot execute; reason retained |

An `ACCEPTED` transition immediately freezes the configuration's complete
scientific payload and object content hash. From that moment it cannot acquire
or change a parameter, comparator, tolerance, seed, metric, classification,
analysis rule, initial policy memory, fault schedule, or any other scientific
field, whether or not implementation or execution has begun. Revision
requires a new version and hash.

### 6.14 `ExecutionBinding`

An `ExecutionBinding` is created only after an `ExperimentConfiguration` is
accepted and a candidate implementation exists. It binds one exact execution
identity to the operational materials needed to execute that immutable
science. It is not part of the preregistration and may not add or reinterpret
a scientific choice.

| Field | Contract |
|---|---|
| common object envelope | Binding identity, schema, object version, and derived object content hash; a binding never embeds a self-`ObjectRef` |
| `accepted_configuration_ref` | Exact configuration ID, version, and object content hash; status must be `ACCEPTED` |
| `implementation_refs` | Exact implementation artifact and dependency hashes, mapped to the scientific interfaces they realize |
| `source_refs` | Source commit and exact result-producing source-file hashes |
| `execution_identity` | Exact unique identity for the one bound invocation/run |
| `entrypoint_contract` | Exact entry point and non-secret argument contract |
| `runtime_constraints` | Interpreter, OS/architecture, dependency, locale, time-zone, arithmetic, parallelism, and environment constraints that must hold |
| `artifact_contract` | Required canonical scientific trace or durable prefix, trace completeness, run envelope, result, summary, manifest, figure, and evidence-ledger artifacts and their schemas; storage/publication targets remain operational metadata |
| `operational_exclusions` | Explicit functions, configurations, gates, paths, fallbacks, and execution modes the binding forbids |
| `preflight_contract` | Static/runtime identity checks required before any model state can advance |
| `execution_semantics_hash` | Hash of the replay-relevant projection defined below; not the binding's object content hash |

The binding's `object_content_payload` contains the accepted-configuration
reference through `preflight_contract`. Its own `object_content_hash` and the
sibling derived `execution_semantics_hash` are excluded from that preimage;
all source values from which the latter is derived remain included. The
independently derived replay projection is:

```text
ExecutionSemanticsPreimageV1 = {
    hash_domain: "ebu.execution-semantics.v1",
    accepted_configuration_ref,
    implementation_refs,
    source_refs,
    implementation_entrypoint_semantics,
    runtime_constraints_that_can_affect_science,
    operational_exclusions_that_can_affect_science,
    policy_memory_transition_contracts_if_applicable,
    fault_injection_delivery_semantics_if_applicable,
    event_order_and_arithmetic_contracts,
    canonical_scientific_trace_schema,
    scientific_result_schema,
    stochastic_generator_and_stream_contract_if_applicable
}

ExecutionSemanticsHash =
    SHA-256(CANONICAL(ExecutionSemanticsPreimageV1))
```

The projection includes every binding field classified prospectively as able
to alter scientific behavior, including applicable entrypoint and exclusion
semantics. It excludes `execution_identity`, wall-clock and host-instance
observations, process identifiers, storage locations, publication targets,
and other run-instance metadata. Two execution bindings may therefore have
different object content hashes and execution identities but the same
`ExecutionSemanticsHash`. The exact science-affecting versus run-metadata
classification must be frozen under UQ-36 before the first accepted binding.

Lifecycle is `DRAFT -> REVIEWED -> ACCEPTED`, with `SUPERSEDED` or
`REVOKED_BEFORE_EXECUTION` recorded externally without mutation. Acceptance
immediately makes the binding immutable. A binding mismatch cannot be repaired
by editing the accepted scientific configuration.

### 6.15 Results, traces, manifests, and publication records

A `ResultArtifact` SHALL distinguish its canonical scientific result payload
from its run envelope. The scientific payload contains the accepted
configuration reference, execution-semantics hash, typed scientific values,
completeness state, boundary, horizon, row count or equivalent extent, and
scientific derivation references. For a stateful policy it also contains the
initial and terminal or last-confirmed policy-memory payload hashes and
augmented replay-state hashes. The run envelope contains the execution
binding reference, exact execution identity, runtime provenance, wall-clock
timestamps, host/process metadata, storage reference, and artifact byte hash.
Run-envelope fields are not part of the deterministic scientific replay
projection.

Result status SHALL distinguish:

- `COMPLETE`;
- `FAILED_BEFORE_STATE_ADVANCE`;
- `FAILED_AFTER_PARTIAL_ADVANCE`;
- `PARTIAL`;
- `UNRESOLVED`;
- `OUT_OF_BOUNDARY`;
- `RECOVERED_IDENTICAL`;
- `CORRECTED_BY_NEW_ARTIFACT`.

A `SummaryArtifact` is derived from pinned row-level results and analysis code.
A `FigureArtifact` is derived from pinned results or summaries and figure code.
Neither may mutate its inputs or be relabelled as raw observation.

An `ExecutionResultManifest` is the framework's immutable pre-publication
provenance manifest and fulfills the planning register's required
`ProvenanceManifest` role. It SHALL be finalized before publication and
enumerate, in a frozen order:

1. accepted configuration reference and object content hash;
2. accepted execution-binding reference and object content hash;
3. execution-semantics hash and exact execution identity;
4. external execution-authorization reference and object content hash, plus
   the applicable immutable authenticity and validation evidence references;
5. protocols, plans, foundations, and schema versions;
6. source commit, exact source-file hashes, implementation artifacts, and
   dependency locks;
7. interpreter, operating system, architecture, locale, time zone, and
   relevant environment;
8. execution command identity without secrets;
9. event-order and arithmetic versions;
10. seed and random-stream registry;
11. initial physical-state and applicable initial policy-memory object and
    payload hashes, plus the exact fault schedule or `NOT_APPLICABLE`;
12. other input artifacts;
13. canonical scientific trace payload or preserved durable-prefix artifact,
    trace completeness, and run-envelope artifacts, each with
    its distinct hash;
14. terminal or last-confirmed physical/policy-memory and augmented
    replay-state hashes when applicable;
15. scientific results, summaries, diagnostics, and failure records;
16. figures and evidence-ledger entries intended for publication; and
17. pre-publication recovery or correction relations.

The manifest itself is immutable and content-addressed. It SHALL NOT contain a
publication destination, publication timestamp, write-once confirmation, or
publication receipt because none can exist before the manifest is finalized.
A manifest with a missing required pre-publication artifact is `PARTIAL` or
`UNRESOLVED`, not complete. That partial or unresolved manifest remains
immutable; later completion creates a new manifest version that references it
rather than upgrading it in place.

A `PublicationRecord` is a separate immutable post-publication record. It
SHALL reference the exact `ExecutionResultManifest`, publication-stage
authorization plus its authenticity/validation evidence, published artifact
byte hashes, destinations, publisher identity, publication timestamps,
write-once/byte-identity checks, and the durable publication receipt. It may
be added to a publication ledger but may not be inserted retroactively into
the pre-publication manifest.

### 6.16 External `StageAuthorization`

A `StageAuthorization` is an external immutable authority record. It is never
embedded in, or included in the object-content payload of, the object it
authorizes. In particular, neither `ExperimentConfiguration` nor
`ExecutionBinding` contains its authorization.

The common envelope supplies the authorization identity, schema, version, and
derived object content hash; that hash is not in its own preimage. The
authorization's `object_content_payload` SHALL contain:

- issuer identity, claimed credential/key identity, and required authenticity
  profile;
- issuer authority scope and any delegation-chain references;
- authorized stage and exact allowed operation set;
- exact target-object references and object content hashes;
- exact `ExperimentConfiguration` reference and object content hash when a
  configuration exists, mandatory for configuration acceptance and every
  later stage;
- exact `ExecutionBinding` reference and object content hash when a binding
  exists, mandatory for binding acceptance, scientific execution, and
  publication;
- exact execution identity, mandatory for scientific execution and any
  operation on that execution's artifacts;
- explicit exclusions and maximum invocation or single-use conditions;
- issue time, `not_before`, expiry, and decision-time clock contract;
- revocation-registry reference and required revocation status check;
- exact predecessor-stage evidence references and hashes.

An `AuthorizationAuthenticityEnvelope` is separate from the
`StageAuthorization` preimage. It SHALL reference the exact authorization ID,
version, and object content hash and carry the signature or equivalent proof,
proof-byte hash, issuer credential chain, and trust-profile evidence required
by the eventual trust mechanism. Because it is created over an already
computed authorization hash, neither the proof nor a reference to its own
envelope is placed in `ObjectContentPreimageV1` for that authorization. The
authorization-validation input is an external evidence bundle containing the
authorization, its authenticity envelope, trusted issuer/scope evidence, and
current revocation evidence.

Issuance or acceptance freezes the authorization content immediately.
Revocation is recorded by the external revocation authority and does not
mutate the authorization object.

For an acceptance operation, the authorization references the exact draft
content hash and the interface atomically records its accepted status without
changing that content. For later operations, the referenced configuration and
binding must already be accepted. An earlier-stage authorization for which no
configuration or execution binding can yet exist uses the applicable
`NOT_APPLICABLE` references and authorizes only its exact earlier-stage
objects. It cannot authorize scientific execution. The concrete trust,
signature, issuer-registry, delegation, and revocation mechanism is
deliberately unresolved in UQ-35 and must be frozen in I-0 before the
authorization interface is implemented.

## 7. Conceptual Python module boundaries

The names below specify responsibility boundaries for a later implementation.
They do not create modules in this stage.

| Conceptual namespace | Owns | May import | Must not own |
|---|---|---|---|
| `ebu_framework.identity` | Stable identifiers, object references, semantic versions, content hashes | Standard primitives only | Scientific state or policy |
| `ebu_framework.types` | Dimensions, units, quantities, time, regions, boundaries, statuses | `identity` | Domain-specific distortion or allocation |
| `ebu_framework.registry` | Immutable typed registries and alias resolution | `identity`, `types` | Mutable accepted configurations |
| `ebu_framework.state` | Physical `SystemState`, `RepresentedState`, projection contracts | `identity`, `types`, `registry` | Policy memory, distortion evaluation, policy, settlement |
| `ebu_framework.distortion` | Versioned `D(X)` contracts and evaluations | `state`, `types` | Action execution or policy choice |
| `ebu_framework.actions` | Imported action definitions, action instances, supports, lifecycle | `state`, `types` | Policy objectives, grouping operations, or settlement |
| `ebu_framework.bridge` | Exact adapter to Sequential–Parallel Bridge v0.2 | `state`, `distortion`, `actions` | Redefinition of bridge terms |
| `ebu_framework.network` | Providers, topology, capacity loci, provisional route references | `types`, `state`, `registry` | Final Part VII route laws |
| `ebu_framework.commitments` | Commitments, reservations, admission decisions, queues | `types`, `actions`, `network` | Physical action transformation |
| `ebu_framework.observation` | Measurements, calibration, uncertainty, availability time | `types`, `state` | Hidden completion of missing state |
| `ebu_framework.scheduling` | Open-loop schedules, comparator schedules, event declarations | `actions`, `network`, `commitments` | State mutation |
| `ebu_framework.policy` | Closed-loop policy interface, information views, immutable policy-memory states, memory payload hashes, and decision transitions | `identity`, `observation`, `scheduling`, `types` | Physical-state mutation or direct access to future engine state |
| `ebu_framework.execution` | Event ordering, proposal construction, policy-decision/memory durability orchestration, epoch-wide physical update ownership, atomic phase commits | `identity`, `types`, `state`, `distortion`, `actions`, `bridge`, `network`, `commitments`, `observation`, `scheduling`, `policy`, `authorization` | Reclassification of policy memory as physical state, causal inference, or institutional allocation |
| `ebu_framework.causal` | Separately authorized causal models and identified contributions | `identity`, `types`; immutable evidence only through `ObjectRef` | Physical remeasurement or settlement policy |
| `ebu_framework.settlement` | Quotes, guarantees, institutional shares, residuals | `identity`, `types`; physical and causal records only through `ObjectRef` | Mutation of physical records or causal status |
| `ebu_framework.ledger` | Append-only event, receipt, settlement, and evidence ledgers | `identity`, `types` | Scientific transformation logic |
| `ebu_framework.experiment` | Scientific configurations, execution bindings, stage identities, arms, and comparator registry | `identity`, `types`; scientific dependencies only through pinned `ObjectRef` | Embedded authorization, hidden defaults, or outcome-driven mutation |
| `ebu_framework.authorization` | External stage-authority records and authorization validation | `identity`, `types`, `experiment` | Mutation of an authorized object or inference of scientific permission from existence |
| `ebu_framework.artifacts` | Canonical scientific traces and durable prefixes, completeness classifications, run envelopes, results, summaries, figures, and pre-publication execution/result manifests | `experiment`, `ledger`, `identity`, `types` | Publication confirmation, policy decisions, or scientific execution |
| `ebu_framework.validation` | Static, synthetic, and exact-fixture harness classifications | Reviewed public interfaces; no module may import `validation` to perform science | Scientific-run authorization |
| `ebu_framework.publication` | Write-once publication, post-publication records, recovery, and correction workflows | `artifacts`, `ledger`, `experiment`, `authorization`, `identity` | Result editing, interpretation, pre-publication-manifest mutation, or runner invocation |

### 7.1 Dependency direction rule

Imports SHALL follow the `May import` column and SHALL be acyclic at the
scientific-authority level. Generic immutable `ObjectRef` use does not grant
authority to call or reinterpret the referenced module. Utility-level cycles
hidden behind runtime import tricks are nonconforming.

In particular:

- `policy` may propose schedules but may not import `execution` internals;
- `state` owns physical `Z_k` while `policy` owns `PolicyMemoryState`; neither
  may absorb the other's payload for convenience;
- `execution` may emit measurements and traces but may not import `causal` or
  `settlement` to decide physics;
- `causal` may consume immutable result references but may not change them;
- `settlement` may consume physical or causal references but may not fill an
  unidentified causal field;
- `authorization` validates external authority but may not be embedded in the
  configuration or binding it authorizes;
- `publication` may publish accepted artifacts but may not trigger a runner;
- `validation` may classify and invoke only functions permitted by its stage;
- Parts IV–IX SHALL extend these namespaces through registered plugins or
  adapters, not fork the core scientific object model.

### 7.2 Interface contract template

Every public scientific interface SHALL document:

1. owner module;
2. scientific purpose and claim status;
3. typed inputs and version/hash requirements;
4. required authorization stage;
5. preconditions and information boundary;
6. deterministic ordering and arithmetic contract;
7. outputs and their completeness states;
8. state mutation, if any;
9. postconditions and invariants;
10. failure codes and whether any state advanced;
11. trace and provenance obligations;
12. whether the interface is static, synthetic-operational, or scientific.

An undocumented fallback is forbidden.

### 7.3 Core interface catalogue

| Interface | Inputs | Preconditions | Outputs | Postconditions | Failure states |
|---|---|---|---|---|---|
| `resolve_ref` | Pinned `ObjectRef` | Registry available | Immutable object | ID, version, and hash all match | `REF_NOT_FOUND`, `VERSION_MISMATCH`, `HASH_MISMATCH` |
| `compute_object_content_hash` | Object envelope and object-content payload | Canonical serializer version pinned | `ObjectContentHash` | Hash field and non-content metadata excluded from preimage | `CANONICALIZATION_FAILURE`, `HASH_DOMAIN_MISMATCH` |
| `compute_state_payload_hash` | Exact `Z_k` payload projection | State schema and epoch pinned | `StatePayloadHash` | Object identity, ownership, provenance, and derived hashes excluded | `STATE_PROJECTION_FAILURE`, `CANONICALIZATION_FAILURE` |
| `compute_policy_memory_payload_hash` | Exact policy, memory schema, decision epoch, resolution, and memory payload projection | Policy and memory schema pinned | `PolicyMemoryPayloadHash` | Own hash, object identity, lineage, trace, durability, and run metadata excluded | `POLICY_MEMORY_PROJECTION_FAILURE`, `CANONICALIZATION_FAILURE` |
| `compute_augmented_closed_loop_replay_state_hash` | Physical state payload hash and policy-memory payload hash | Both component hashes valid for the same stateful decision epoch | `AugmentedClosedLoopReplayStateHash` | Component meanings remain distinct and both are replay inputs | `POLICY_MEMORY_NOT_APPLICABLE`, `EPOCH_MISMATCH`, `HASH_MISMATCH` |
| `validate_quantity` | `Quantity`, expected type | Registries pinned | Validation record | Dimensions, units, type, region, and time basis compatible | `DIMENSION_MISMATCH`, `UNIT_MISMATCH`, `BOUNDARY_MISMATCH` |
| `project_state` | `SystemState`, boundary, projection | Source state immutable | `RepresentedState` | Required coordinates present; source unchanged | `MISSING_COORDINATE`, `OUT_OF_BOUNDARY`, `PROJECTION_FAILURE` |
| `evaluate_distortion` | Distortion model, represented state | Domain and versions match | Typed distortion evaluation | Deterministic under declared numerical policy | `DOMAIN_FAILURE`, `NUMERICAL_FAILURE`, `VERSION_MISMATCH` |
| `classify_joint_groups` | Accepted actions, effective intervals, supports, boundary, horizon | Bridge v0.2 pinned | Group partition and dependency evidence | Exact imported rule and transitive closure applied | `INCOMPATIBLE_BOUNDARY`, `UNRESOLVED_COUPLING`, `GROUPING_FAILURE` |
| `build_schedule` | Action refs and coordination events | No execution; all refs resolvable | Draft or accepted schedule | Ordering, overlap, and comparator declarations explicit | `INADMISSIBLE_SCHEDULE`, `MISSING_COMPARATOR` |
| `policy_propose` | Permitted information view and exact current `PolicyMemoryState`, or explicit stateless mode | Closed-loop execution authorized; view and memory available at decision epoch; no future data | `PolicyDecisionRecord`, proposals, and exactly one candidate next memory for stateful mode | Read set is permitted; before/after hashes, schema, predecessor, and next epoch are explicit; `Z_k` unchanged | `INFORMATION_VIOLATION`, `POLICY_MEMORY_MISMATCH`, `POLICY_FAILURE`, `UNRESOLVED` |
| `commit_policy_decision` | Validated policy decision and candidate next memory | Exact before-memory remains current; decision coordinate unused; applicable declared durability fault known | Durable decision record, next immutable memory, and canonical decision trace row, or typed failure | Decision, memory, and trace row append atomically; physical state and physical update ownership unchanged | `POLICY_MEMORY_TRANSITION_CONFLICT`, `POLICY_MEMORY_DURABILITY_FAILURE`, `DECLARED_FAULT_TERMINAL`, `UNRESOLVED_DURABILITY` |
| `screen_and_admit` | Proposals, constraints, capacity, queue rule | Phase 5/6 snapshot frozen | Admission decisions | Presented quantity partition and capacity rules close | `CAPACITY_VIOLATION`, `PREREQUISITE_FAILURE`, `RULE_UNDEFINED` |
| `propose_phase_updates` | Current immutable state plus due-event, topology-event, registration/status, or natural-drive inputs for phase 1, 2, 9, or 10 | Correct phase and predecessor state payload hash; no mutation | Immutable transition proposals and epoch ownership claims | Every proposed state effect typed; phase-9 proposal excludes any phase-8 committed physical effect | `PHASE_MISMATCH`, `TRANSFORMATION_FAILURE`, `DUPLICATE_EFFECT`, `UNRESOLVED_EFFECT` |
| `propose_joint_transition` | Common pre-state, one joint group, exogenous inputs | No state mutation; grouping accepted | Transition proposal and ownership claims | Every proposed effect typed and owned once | `TRANSFORMATION_FAILURE`, `UNRESOLVED_EFFECT` |
| `commit_phase_updates` | One mutating phase's proposals and epoch ownership record | Ownership is disjoint across all prior/current mutating phases; validation complete | Successor state, extended ownership record, scientific trace rows | Atomic phase commit; no effect omitted or duplicated | `UPDATE_OWNERSHIP_CONFLICT`, `PHASE_OWNERSHIP_MISMATCH`, `COMMIT_FAILURE`, `PARTIAL_ADVANCE` |
| `measure_state` | State ref, measurement contract | Measurement epoch reached | Measurement records | State unchanged; availability time explicit | `MEASUREMENT_FAILED`, `PARTIAL`, `UNRESOLVED` |
| `compute_group_measurement` | Pinned before/after projections and distortion | Compatible boundary | `M_G` and optional bridge diagnostics | Imported equations preserved | `INCOMPATIBLE_BOUNDARY`, `DIAGNOSTIC_UNDEFINED` |
| `infer_causal_contributions` | Results and causal model | Separate authorization and identifiability contract | Contributions plus remainder/status | No physical or settlement records altered | `UNIDENTIFIED`, `MODEL_FAILURE`, `OUT_OF_BOUNDARY` |
| `allocate_settlement` | Physical measurement, quote, allocation rule | Institutional rule accepted | Shares and residual | `sum(S_i)+R_G=M_G` under declared arithmetic | `CLOSURE_FAILURE`, `RULE_UNDEFINED` |
| `accept_experiment_configuration` | Draft scientific configuration and external preregistration authorization-evidence bundle | Configuration object hash valid; every stateful arm pins valid initial memory; authorization matches exact configuration and acceptance operation | Immutable accepted `ExperimentConfiguration` | Acceptance freezes content immediately; memory mode and initial-memory/fault-schedule applicability close; no implementation or execution fields present | `AUTHORIZATION_INVALID`, `CONFIGURATION_INCOMPLETE`, `POLICY_MEMORY_MISMATCH`, `FAULT_SCHEDULE_MISMATCH`, `NONSCIENTIFIC_FIELD_PRESENT`, `HASH_MISMATCH` |
| `accept_execution_binding` | Draft binding, accepted configuration ref, and external pre-execution authorization-evidence bundle | Configuration exact and immutable; authorization matches exact configuration/binding hashes and acceptance operation; binding adds no science | Immutable accepted `ExecutionBinding` | Full binding and execution-semantics projections hash correctly; acceptance freezes binding immediately | `AUTHORIZATION_INVALID`, `CONFIGURATION_NOT_ACCEPTED`, `SCIENTIFIC_DRIFT`, `HASH_MISMATCH` |
| `validate_stage_authorization` | External authorization-evidence bundle, exact configuration/binding refs, operation, execution identity, decision time | Trust and revocation mechanisms configured | Authorization validation record | Authorization hash, external proof, issuer scope, operation scope, time, revocation, predecessor evidence, hashes, and execution identity all valid | `AUTHENTICITY_INVALID`, `ISSUER_SCOPE_INVALID`, `OPERATION_NOT_AUTHORIZED`, `AUTHORIZATION_NOT_YET_VALID`, `AUTHORIZATION_EXPIRED`, `AUTHORIZATION_REVOKED`, `PREDECESSOR_EVIDENCE_INVALID`, `EXECUTION_IDENTITY_MISMATCH` |
| `advance_epoch` | Current physical state, current policy memory or `NOT_APPLICABLE`, exact fault schedule or `NOT_APPLICABLE`, exact accepted configuration/binding, external execution authorization-evidence bundle | Full authorization validation passes; physical/memory predecessor pair and fault schedule match exact replay inputs | Immutable successor physical state, next policy memory or `NOT_APPLICABLE`, augmented replay-state hash when applicable, trace rows, and commit evidence | Imported phase order and physical ownership hold; memory decision is separately durable; completeness and any durable prefix explicit | `AUTHORIZATION_INVALID`, `PREDECESSOR_MISMATCH`, `POLICY_MEMORY_MISMATCH`, `FAULT_SCHEDULE_MISMATCH`, `UPDATE_OWNERSHIP_CONFLICT`, `PARTIAL_ADVANCE`, `UNRESOLVED_DURABILITY` |
| `finalize_execution_result_manifest` | Accepted artifact inventory and external finalization authorization-evidence bundle | Authorization matches exact configuration/binding/execution identity and operation; required pre-publication artifacts or confirmed prefix write-once and hashable | Immutable `ExecutionResultManifest` | Ordered inventory records trace completeness and terminal/last-confirmed physical-memory pair; complete or explicitly partial; no publication confirmation fields | `AUTHORIZATION_INVALID`, `MISSING_ARTIFACT`, `HASH_MISMATCH`, `UNRESOLVED_DURABILITY` |
| `publish_artifacts` | Execution/result manifest and external publication authorization-evidence bundle | No runner active; authorization, hashes, and exact execution identity verified | Immutable `PublicationRecord` | Byte-identical write-once publication recorded separately from manifest | `ALREADY_EXISTS_DIFFERENT`, `AUTHORIZATION_INVALID`, `EXECUTION_IDENTITY_MISMATCH`, `WRITE_FAILURE` |

## 8. Execution architecture

### 8.1 Execution modes

The framework SHALL declare one of two modes:

| Mode | v0.1 specification status | Contract |
|---|---|---|
| `DETERMINISTIC` | Required first implementation mode | Normally completed executions with identical replay inputs and semantics produce the byte-identical canonical scientific trace payload qualified in §8.3; declared fault studies additionally require an identical fault schedule; undeclared operational interruption follows prefix/failure rules |
| `STOCHASTIC` | Later extension point | All randomness comes from owned, recorded streams; distribution, generator, seed derivation, and draw accounting are pinned |

A missing stochastic implementation SHALL fail with `MODE_NOT_SUPPORTED`. It
shall not silently run deterministically or use process-global randomness.

“Deterministic” does not mean static, certain, linear, or failure-free. A
deterministic configuration may contain a frozen failure history or
disturbance sequence.

### 8.1.1 Prospectively declared fault schedules

A `FaultSchedule` is an immutable versioned study input used only when fault
injection is declared before execution. It SHALL contain:

- exact identity, object version, schema, and object content hash;
- study classification, including whether each fault is a scientific/model
  event or a declared operational/durability-boundary injection;
- stable fault IDs, typed targets, and injected effects or failure codes;
- exact epoch and phase for model events, or exact named durable-write
  boundary for operational injections;
- deterministic trigger predicates using only replay inputs, never candidate
  outcomes or undeclared wall-clock timing;
- total ordering for coincident injections;
- continuation, recovery, and terminal rules; and
- the expected canonical-trace completeness classification.

The accepted configuration pins this schedule for a scientific
fault-injection study. An inert T1 durability study instead pins it in its
separately authorized validation configuration and does not thereby become a
scientific experiment. The applicable implementation and delivery mechanism
is pinned by the execution semantics. A fault that was not prospectively
listed is not retroactively part of the schedule.

Scientific/model fault events enter the ordinary scientific external-input
and event-order contracts. A declared operational/durability fault remains an
operational event, but its exact schedule is a replay input for the declared
fault study and determines the prospectively expected prefix boundary and
completeness class. Host-specific symptoms and storage diagnostics remain
run-specific evidence.

### 8.2 Event identity and total order

Every event SHALL have an immutable `EventKey`:

```text
(epoch, phase_ordinal, declared_priority, group_or_scope_id,
 event_kind, primary_object_id, local_sequence)
```

Requirements:

- `phase_ordinal` is exactly `1` through `10` from §3.3;
- every later field uses a prospectively frozen total ordering;
- `local_sequence` is assigned before state mutation and is not based on an
  outcome;
- equal keys are invalid rather than resolved by container iteration order;
- map, set, thread, or process scheduling order SHALL not determine science;
- the trace records both declared simultaneity and deterministic serialization
  used for bookkeeping.

Events declared simultaneous within a joint-transition group use one common
pre-state and one joint proposal. Their physical meaning SHALL not depend on
the bookkeeping order of child identifiers.

### 8.3 Canonical scientific trace and run envelope

The trace has two immutable projections that SHALL NOT be conflated.

`CanonicalScientificTracePayloadV1` contains only replay-relevant scientific
content:

- hash domain and canonical trace schema version;
- accepted `ExperimentConfiguration` object content hash;
- `ExecutionSemanticsHash`, but not the full execution-binding hash;
- initial `StatePayloadHash`; initial `PolicyMemoryPayloadHash` and
  `AugmentedClosedLoopReplayStateHash` for a stateful policy, otherwise an
  explicit `NOT_APPLICABLE` memory marker;
- ordered scientific external-input payload hashes;
- exact `FaultSchedule` object content hash for a prospectively declared
  fault-injection study, otherwise `NOT_APPLICABLE`;
- frozen stochastic stream identities and draw coordinates when applicable;
- deterministically ordered rows containing epoch, `EventKey`, phase, stable
  scientific object references, predecessor and successor state payload
  hashes, permitted-information-view scientific hash, policy-memory before and
  after payload hashes for every stateful decision, proposal/admission/group
  and update-ownership facts, typed scientific quantities, uncertainty
  values, scientific lifecycle transitions, declared scientific/model faults,
  and scientifically relevant failures; and
- terminal or last-confirmed-durable `StatePayloadHash`, corresponding
  terminal or last-confirmed `PolicyMemoryPayloadHash` and augmented replay
  hash when applicable, confirmed row count, and explicit trace completeness
  state.

It SHALL exclude execution identity, the full execution-binding hash,
wall-clock timestamps, record/ingestion times, host name or host instance,
process and worker identifiers, runtime observation logs, storage paths,
database keys, cache metadata, publication destinations, publication times,
publisher identity, and publication receipts.

`RunTraceEnvelopeV1` SHALL reference the canonical scientific trace payload
hash and may contain the exact execution-binding reference, execution
identity, wall-clock start and finish, observed host/runtime/process metadata,
storage references, operational logs, undeclared interruption or durability
failure evidence, and other run-specific provenance. The envelope is
immutable evidence but is not the deterministic replay target. Publication
provenance belongs later in `PublicationRecord`, not in either trace
projection.

Trace completeness SHALL use at least these explicit states:

| State | Meaning |
|---|---|
| `COMPLETE` | The configured terminal horizon and required finalization point were reached |
| `DECLARED_FAULT_TERMINAL` | A prospectively declared fault study reached its scheduled fault-terminal boundary and preserved the required canonical payload or prefix |
| `PARTIAL_DURABLE_PREFIX` | An undeclared interruption or durability failure left a known, hash-valid canonical scientific prefix |
| `NO_DURABLE_TRACE` | No canonical scientific trace payload or row became durable |
| `UNRESOLVED_DURABILITY` | The last durable canonical row or state/memory pair cannot be established |

For `PARTIAL_DURABLE_PREFIX`, every confirmed canonical row and its last
physical/memory hashes remain immutable. Those rows SHALL be the exact byte
prefix of any later authorized byte-identical recovery or completion; failure
diagnostics are not inserted into the scientific rows. `NO_DURABLE_TRACE` and
`UNRESOLVED_DURABILITY` are recorded in the run envelope and failure evidence
when no trustworthy canonical payload with that status can itself be
finalized.

For two normally completed deterministic executions, the exact replay
requirement is:

```text
given equal:
    ExperimentConfiguration.object_content_hash
    ExecutionSemanticsHash
    initial StatePayloadHash
    initial PolicyMemoryPayloadHash, or NOT_APPLICABLE
    ordered external scientific input payload hashes
    stochastic stream identities and draw values, if any
    FaultSchedule = NOT_APPLICABLE

and both trace completeness states are COMPLETE

require byte equality of:
    CANONICAL(CanonicalScientificTracePayloadV1)
```

For a prospectively declared deterministic fault-injection study, replace the
`FaultSchedule=NOT_APPLICABLE` condition with equality of the exact
`FaultSchedule` object content hash and replace the normal-completion condition
with equality of the prospectively expected `COMPLETE` or
`DECLARED_FAULT_TERMINAL` state. The same byte-equality requirement then
applies only when the execution semantics deliver each fault at the same
declared coordinate. A model-fault study that continues to the horizon uses
`COMPLETE`; a study whose declared terminal condition is the fault boundary
uses `DECLARED_FAULT_TERMINAL`.

An undeclared process interruption, host loss, storage error, torn-write
hazard, or other operational durability failure is not a scientific replay
input and is not evidence against scientific determinism. It creates
run-specific failure evidence, preserves any known durable canonical
scientific prefix, and assigns the applicable explicit completeness state. No
full-trace byte-equality claim is made between that interrupted run and a
normally completed execution, or between runs interrupted at different
undeclared operational points.

The trace payload hash is exactly:

```text
CanonicalScientificTracePayloadHash =
    SHA-256(CANONICAL(CanonicalScientificTracePayloadV1))
```

The hash field is not part of `CanonicalScientificTracePayloadV1`. The
corresponding canonical scientific trace payload hashes SHALL also be equal.
Byte identity of `RunTraceEnvelopeV1`, the full execution binding, host
metadata, wall-clock time, storage metadata, or publication records is neither
required nor expected. For interrupted runs, the retained prefix is governed
by the prefix rule above rather than the normally completed full-payload rule.

### 8.4 Static pseudocode for one deterministic epoch

The following is specification pseudocode. It is not executable code and was
not run:

```text
function specify_epoch_transition(
    current_state,
    current_policy_memory_or_not_applicable,
    epoch,
    accepted_config,
    accepted_binding,
    declared_fault_schedule_or_not_applicable,
    external_authorization_evidence_bundle
):
    require accepted_config.status == ACCEPTED
    require accepted_binding.status == ACCEPTED
    require accepted_binding.accepted_configuration_ref
            == exact_ref(accepted_config)
    require verify_object_content_hash(accepted_config)
    require verify_object_content_hash(accepted_binding)
    require verify_execution_semantics_hash(accepted_binding)
    require declared_fault_schedule_or_not_applicable
            == accepted_config.fault_schedule_ref_or_not_applicable

    authority = validate_stage_authorization(
        external_authorization_evidence_bundle,
        exact_ref(accepted_config),
        exact_ref(accepted_binding),
        operation = ADVANCE_SCIENTIFIC_STATE,
        execution_identity = accepted_binding.execution_identity,
        decision_time = trusted_authorization_clock_now()
    )
    require authority == VALID

    if epoch == 0:
        require current_state.state_payload_hash
                == accepted_config.initial_state_payload_hash
        require exact_ref_or_not_applicable(current_policy_memory_or_not_applicable)
                == accepted_config.initial_policy_memory_ref_or_not_applicable
    else:
        require current_state.state_payload_hash
                == durable_predecessor_state_payload_hash(
                    accepted_binding.execution_identity,
                    epoch
                )
        require policy_memory_payload_hash_or_not_applicable(
                    current_policy_memory_or_not_applicable
                )
                == durable_predecessor_policy_memory_payload_hash_or_not_applicable(
                    accepted_binding.execution_identity,
                    epoch
                )
    require event_order_version == dynamic_foundation_v0_1
    require validate_policy_memory_mode_and_hashes(
        accepted_config,
        current_policy_memory_or_not_applicable,
        epoch
    )

    working = immutable_reference(current_state)
    working_memory = immutable_reference_or_not_applicable(
        current_policy_memory_or_not_applicable
    )
    ownership = begin_epoch_update_ownership(epoch, working.state_payload_hash)
    scheduled_faults = exact_declared_faults_for_epoch_or_empty(
        declared_fault_schedule_or_not_applicable,
        epoch
    )
    scheduled_model_faults = scheduled_faults.scientific_model_events
    scheduled_operational_injections =
        scheduled_faults.operational_durability_events
    require operational injections are delivered only by their named
            durability-boundary wrappers, never as scientific model inputs

    phase_1 = propose_due_arrivals_and_delayed_effects(
        working, epoch, scheduled_model_faults.for_phase(1)
    )
    working, ownership = commit_phase_updates(
        phase = 1, working, phase_1, ownership,
        declared_operational_injection =
            scheduled_operational_injections.at("phase-1-commit")
    )

    phase_2 = propose_exogenous_topology_and_capacity_events(
        working, epoch, scheduled_model_faults.for_phase(2)
    )
    working, ownership = commit_phase_updates(
        phase = 2, working, phase_2, ownership,
        declared_operational_injection =
            scheduled_operational_injections.at("phase-2-commit")
    )

    measurement = create_permitted_measurement_view(
        working, epoch, scheduled_model_faults.for_phase(3)
    )

    if accepted_config.uses_stateful_policy:
        decision, proposals, candidate_next_memory = policy_propose(
            measurement,
            working_memory,
            scheduled_model_faults.for_phase(4)
        )
        require decision.before_policy_memory_payload_hash
                == working_memory.policy_memory_payload_hash
        require candidate_next_memory.available_for_decision_epoch == epoch + 1
        require candidate_next_memory.predecessor_memory_ref
                == exact_ref(working_memory)
        require verify_policy_memory_payload_hash(candidate_next_memory)
        durable_decision, durable_policy_trace_row =
            commit_policy_decision_memory_and_trace_row_atomically(
                decision,
                candidate_next_memory,
                scheduled_operational_injections.at(
                    "policy-decision-memory-commit"
                )
            )
        require durable_decision == COMPLETE
        require durable_policy_trace_row.before_memory_hash
                == working_memory.policy_memory_payload_hash
        require durable_policy_trace_row.after_memory_hash
                == candidate_next_memory.policy_memory_payload_hash
        working_memory = immutable_reference(candidate_next_memory)
    else if accepted_config.uses_stateless_policy:
        decision, proposals = policy_propose_without_memory(
            measurement,
            scheduled_model_faults.for_phase(4)
        )
        durable_decision =
            durably_append_stateless_policy_decision_and_trace_row(
                decision,
                scheduled_operational_injections.at(
                    "policy-decision-commit"
                )
            )
        require durable_decision == COMPLETE
        require working_memory == NOT_APPLICABLE
    else:
        proposals = declared_open_loop_events(epoch)
        require working_memory == NOT_APPLICABLE

    screened = screen_constraints_without_state_mutation(
        working, proposals, scheduled_model_faults.for_phase(5)
    )
    admissions = apply_frozen_admission_and_queue_rules(
        working, screened, scheduled_model_faults.for_phase(6)
    )

    grouping_inputs = apply_declared_nonmutating_fault_inputs(
        admissions.accepted, scheduled_model_faults.for_phase(7)
    )
    groups = bridge_v0_2_exact_grouping(grouping_inputs)
    transitions = for_each_group_against_common_pre_state(
        propose_exact_joint_transition(
            working, group, scheduled_model_faults.for_phase(8)
        )
    )
    working, ownership = commit_phase_updates(
        phase = 8, working, transitions, ownership,
        declared_operational_injection =
            scheduled_operational_injections.at("phase-8-commit")
    )

    registrations = propose_phase_9_registrations_and_status_changes(
        working, admissions, transitions, scheduled_model_faults.for_phase(9)
    )
    require no registration applies a physical effect committed in phase 8
    working, ownership = commit_phase_updates(
        phase = 9, working, registrations, ownership,
        declared_operational_injection =
            scheduled_operational_injections.at("phase-9-commit")
    )

    natural_drive = propose_natural_drive_for_remainder(
        working, scheduled_model_faults.for_phase(10)
    )
    working, ownership = commit_phase_updates(
        phase = 10, working, natural_drive, ownership,
        declared_operational_injection =
            scheduled_operational_injections.at("phase-10-commit")
    )

    require ownership covers every state mutation in phases 1, 2, 8, 9, 10
    require no ownership key or physical effect was committed more than once
    require working_memory was never written into physical state Z

    return immutable_end_state_memory_and_canonical_scientific_trace_rows(
        working,
        working_memory,
        augmented_closed_loop_replay_state_hash_or_not_applicable(
            working.state_payload_hash,
            policy_memory_payload_hash_or_not_applicable(working_memory)
        ),
        ownership
    )
```

The policy decision, next-memory, and corresponding canonical trace-row append
is one informational durability transaction. It neither belongs to physical
update ownership nor authorizes a physical mutation. If that transaction
fails, screening does not begin, no partial policy-decision row is accepted,
and the before-memory state remains the durable current memory.

Undeclared interruption handling is specified statically as:

```text
function classify_undeclared_interruption(durable_evidence):
    prefix = longest_hash_valid_canonical_scientific_prefix(durable_evidence)

    if prefix is known:
        freeze prefix rows and last physical/policy-memory payload hashes
        trace_completeness = PARTIAL_DURABLE_PREFIX
    else if evidence proves no trace row became durable:
        trace_completeness = NO_DURABLE_TRACE
    else:
        trace_completeness = UNRESOLVED_DURABILITY

    record interruption details only in run-specific failure evidence
    do not classify the interruption as a scientific-determinism violation
    return trace_completeness
```

The authorization line is normative for a future runner. Validation harnesses
must not bypass it by calling lower-level transition functions on a scientific
configuration.

### 8.5 Proposal, ownership, and atomic phase commit

Every state-mutating phase—1, 2, 8, 9, and 10—SHALL use the same proposal,
ownership, and atomic phase-commit discipline. Phases 3 through 7 construct
measurements, decisions, admissions, groups, and proposals without mutating
`Z_k`. A stateful policy's phase-4 informational memory transition is
separately and atomically durable under §6.4.1; it is not a physical phase
commit and does not enter `EpochUpdateOwnership`.

The discipline uses three immutable record types:

1. `TransitionProposal`: expected predecessor `StatePayloadHash`, typed state
   deltas or successor projection, phase, effects, applicable child actions or
   exogenous event, ownership claims, and failure conditions;
2. `EpochUpdateOwnership`: every state coordinate, flow, conversion, loss,
   consumption, expiry, resource use, burden, topology mutation, queue or
   transit registration, commitment/reservation/status change, delayed-effect
   mutation, and natural-drive term mapped to exactly one `(epoch, phase,
   proposal)` owner;
3. `PhaseCommitRecord`: validated proposal hashes, ownership claims, actual
   predecessor and successor `StatePayloadHash` values, atomicity status, and
   canonical scientific trace references.

The epoch ownership record accumulates across phases. A later phase SHALL be
validated against all ownership already committed in the epoch, not merely
against other proposals in the same phase.

The policy-memory decision transaction has its own single owner: the exact
`(execution identity, policy, decision epoch)` coordinate. Duplicate or
conflicting next-memory commits fail with
`POLICY_MEMORY_TRANSITION_CONFLICT`. A physical proposal may reference a
committed policy decision, but it may not copy the memory payload into `Z_k`
or claim physical ownership of the memory transition.

Phase responsibilities are exact:

| Phase | State mutations requiring ownership |
|---|---|
| 1 | Apply due arrivals/delayed physical effects; remove or mature their pending records; update affected queues/transit/statuses |
| 2 | Apply topology, failure, repair, isolation, and capacity-derating changes effective at the epoch |
| 8 | Apply accepted immediate group transitions, completed flows, conversions, losses, consumption, expiry, resource use, congestion effects, and physical coordination burdens |
| 9 | Register new in-transit payloads and future delayed effects; update queues, commitments, reservations, releases, breaches, and unresolved statuses |
| 10 | Apply each declared natural-drive state change for the remainder of the epoch |

A phase-8 proposal may declare that it will cause a later payload or effect,
but the insertion of the new in-transit or delayed-effect record into `q_k` or
`ell_k` is owned and committed in phase 9. Phase 9 registers that future
obligation; it SHALL NOT reapply any immediate physical effect, flow, loss,
conversion, resource use, burden, expiry, or congestion update already owned
and committed in phase 8. The eventual physical maturation of a registered
future effect is owned by phase 1 of its due epoch.

If two supposedly separate groups claim the same update, the framework SHALL
fail before mutation with `UPDATE_OWNERSHIP_CONFLICT`. It SHALL not select one
by iteration order. If the conflict reflects physical coupling, the grouping
input is invalid and must be corrected prospectively in an earlier authorized
stage.

If a storage or runtime failure occurs during any phase commit, recovery SHALL
determine whether zero or all mutations of that phase became durable while
retaining all earlier durable phase commits. An ambiguous partial advance is
`FAILED_AFTER_PARTIAL_ADVANCE` and cannot be retried as though nothing
happened without a separately authorized recovery decision.

### 8.6 Open-loop schedules and closed-loop policies

| Property | Open-loop schedule | Closed-loop policy |
|---|---|---|
| Decisions | Frozen before evolution | Computed at each decision epoch |
| Inputs after start | None, except frozen exogenous event realization | Only the permitted information view |
| Memory | `NOT_APPLICABLE`; schedule itself remains an input object | Initial accepted `PolicyMemoryState` plus immutable before/after memory transitions |
| Reproducibility | Schedule object content hash and event order | Policy object content hash, execution-semantics hash, augmented replay-state hashes, view hash, memory transitions, tie-breaks |
| Leakage risk | Outcome-dependent preconstruction | Future fields or privileged engine access |
| Required trace | Declared versus applied events | Input view, read set, proposal, memory before/after |

A study comparing them SHALL freeze whether exogenous histories are shared,
paired, or separately sampled and shall record stream ownership accordingly.
For a stateful arm it SHALL also freeze the exact initial policy-memory object;
reusing only the same physical initial state with a different memory state is
not an equal replay input.

### 8.7 Information-boundary contract

Each policy decision receives an immutable `InformationView` containing only:

- fields explicitly permitted by the policy contract;
- observations whose `availability_epoch` is no later than the decision;
- active commitments and reservations permitted to that policy;
- declared local or shared topology and queue information;
- exact immutable policy memory carried from earlier permitted decisions,
  whose available epoch matches the current decision; no candidate next
  memory or later memory object;
- no result classification, future failure, future measurement, future random
  draw, hidden state, or other arm's non-shared private data.

The engine SHALL log the view hash and the policy's actual read set. Direct
object references that permit traversal to future state are forbidden.

Static leakage rule:

```text
for every value read by decision d at epoch k:
    require value.available_at <= k
    require value.field_id in d.information_contract.allowed_fields
    require value.provenance not in forbidden_result_or_future_namespaces
```

A violation fails before a proposal can be admitted. Redacting a leaked value
from the output after the decision does not repair the violation.

### 8.8 Simultaneous and joint-transition grouping

Temporal simultaneity and physical grouping remain distinct:

| Case | Framework treatment |
|---|---|
| Overlap only, disjoint supports/constraints, separability demonstrated | Separate transitions may share an event epoch; batching allowed |
| Shared write support or binding constraint | Bridge joint-transition group |
| One action affects another's feasibility, completion, or measurement | Bridge joint-transition group |
| Nonseparable distortion over changed coordinates | Bridge joint-transition group |
| Common endpoint only observable | Bridge joint-transition group |
| Same receipt batch only | Separate physical records |
| Incompatible boundaries | No group value; register unresolved parent boundary |

Group construction occurs after admission because accepted quantities and
binding reservations matter. It occurs before transition construction because
all child effects require the common pre-state.

### 8.9 Capacity admission and queue processing

Admission SHALL proceed in a frozen order:

1. resolve presented request identities and typed quantities;
2. validate prerequisites and accepted commitments;
3. calculate usable capacity from installed capacity and the declared
   availability state;
4. account for active reservations exactly once;
5. apply the frozen allocation and queue discipline with deterministic
   tie-breaking;
6. emit admitted, rejected, deferred, and partially accepted quantities;
7. verify request partition and capacity invariants;
8. only then permit joint-group construction.

If capacity changes after admission, the original decision stays immutable and
a shortfall/failure/rerouting event is added. Historical admission is not
recalculated using later knowledge.

### 8.10 Congestion, failures, and rerouting

Congestion effects SHALL be explicit transition inputs or owned effects; they
may include additional queue time, throughput reduction, loss, expiry, or
resource burden. A generic “congestion penalty” without units, boundary, and
mechanism is invalid.

Topology status SHALL distinguish `AVAILABLE`, `DEGRADED`, `FAILED`,
`ISOLATED`, and `REPAIRING`. A failed edge has zero usable capacity unless a
separately declared degraded mode applies.

Rerouting SHALL:

- use only information available at its decision epoch;
- preserve completed route segments and their effects;
- replace only the unfinished suffix;
- retain the failed reservation and obligation status;
- account for added delay, resource use, loss, and coordination cost;
- remain provisional where final Part VII semantics are required.

Payload beyond a failed segment, stranded payload, physically lost payload,
rejected demand, and pending demand are distinct states.

### 8.11 Delayed effects and natural drive

At each horizon, every delayed effect is exactly one of matured, pending,
cancelled, failed, or unresolved. Maturation is a physical evolution event;
causal attribution is separate.

Natural drive SHALL be a versioned scientific object or accepted input. It is
applied in phase 10 for the declared remainder of the epoch. If a domain
requires drive at another sub-epoch location, that is a prospective change to
the event foundation, not a local switch.

A transformation that already owns a loss, conversion, burden, or resource
use prevents natural drive or an operational handler from applying that same
effect again.

### 8.12 Later stochastic execution

Stochastic execution SHALL add randomness without changing object meanings,
event phases, information boundaries, or publication rules. It must specify:

- probability model and parameter versions;
- pseudorandom generator family and implementation version;
- master seed representation;
- domain-separated stream-derivation rule;
- stream owner and purpose;
- draw index or counter convention;
- whether exogenous streams are shared across arms;
- treatment of rejected proposals and unused draws;
- replay and cross-platform guarantees.

The proposed stream identity is:

```text
(experiment_id, arm_id, replicate_id,
 component_kind, component_id, purpose, stream_version)
```

No component may use an unnamed global stream. Adding an unrelated component
must not shift another owner's random sequence. The generator and exact
derivation algorithm remain unresolved for the implementation stage and must
be frozen before any stochastic preregistration.

## 9. Invariant register

Every future implementation SHALL map each invariant to static checks,
synthetic operational checks, exact fixtures, or a declared proof obligation.
Passing a test does not convert an invariant into an empirical physical claim.

| ID | Invariant | Enforcement boundary |
|---|---|---|
| I-001 | Every accepted reference pins ID, version, and object content hash | Object resolution |
| I-002 | Acceptance immediately freezes configurations, execution bindings, and result artifacts | Artifact store |
| I-003 | A correction creates a new object and preserves the original | Publication/correction |
| I-004 | Quantities combine only under compatible dimensions, units, types, regions, time bases, and boundaries | Type validation |
| I-005 | Pending, failed, partial, unresolved, and out-of-boundary are never encoded as zero or absence | Schema validation |
| I-006 | `SystemState` records declared state; measurement is a separate object | State/observation boundary |
| I-007 | `RepresentedState` is a non-mutating pinned projection | Projection interface |
| I-008 | Distortion evaluates only within its declared domain and boundary | Distortion interface |
| I-009 | Sequential actions use live predecessor states | Bridge/execution |
| I-010 | Joint groups follow the exact bridge dependency rule and transitive closure | Grouping interface |
| I-011 | Every group transition uses one common pre-state | Transition proposal |
| I-012 | A receipt batch never implies physical grouping | Receipt validation |
| I-013 | Group EBU is endpoint measurement, not child causal allocation | Receipt types |
| I-014 | Comparator-relative interaction names every comparator or is undefined | Bridge result validation |
| I-015 | No serial comparator is invented for a nonserializable group | Comparator interface |
| I-016 | Same-baseline non-additivity and comparator interaction remain distinct | Bridge types |
| I-017 | Causal contributions require a declared identified causal model | Causal module |
| I-018 | Settlement shares plus explicit residual close to physical group measurement | Settlement validation |
| I-019 | Policy and institutional choices never overwrite physical or causal records | Module authority |
| I-020 | Dynamic state retains `x`, `g`, `q`, `c`, and `ell` under their imported meanings | State schema |
| I-021 | Decision-relevant policy memory is represented by a separately typed immutable `PolicyMemoryState`, never hidden in or omitted from the augmented closed-loop replay state | Policy validation |
| I-022 | The ten within-epoch phases execute in the imported order | Event engine |
| I-023 | Every mutation in phases 1, 2, 8, 9, and 10 has exactly one epoch-wide update owner | Commit validation |
| I-024 | Proposal and ownership construction precede every state-mutating phase commit | Event engine |
| I-025 | Each mutating phase commit is atomic or the result is an explicit partial-advance failure retaining earlier durable phases | Durability layer |
| I-026 | Presented requests partition into admitted, rejected, and outside-queue pending quantities | Admission validation |
| I-027 | Rejected demand never enters or leaves the admitted queue | Queue validation |
| I-028 | Completed compatible flow never exceeds usable capacity | Capacity validation |
| I-029 | Reservations are claims, not stock or delivered flow | Type system |
| I-030 | Later capacity loss creates a shortfall record without rewriting admission | Ledger |
| I-031 | Rerouting changes only an unfinished suffix | Network audit |
| I-032 | Completed route effects remain immutable | Network/ledger |
| I-033 | Delay components are non-overlapping or explicitly additive | Delay validation |
| I-034 | Effects due after a horizon remain pending or explicitly excluded | Horizon validation |
| I-035 | Natural drive is owned and applied exactly once in phase 10 | Event ownership |
| I-036 | A policy reads no value unavailable at its decision epoch | Information boundary |
| I-037 | Open-loop schedules do not adapt to generated state | Schedule validation |
| I-038 | Event ordering never depends on map, set, thread, or process iteration | Deterministic engine |
| I-039 | Normally completed deterministic executions with equal §8.3 replay inputs and semantics produce byte-identical canonical scientific trace payloads; run envelopes are excluded | Reproducibility |
| I-040 | Random streams are explicitly owned and versioned | Stochastic extension |
| I-041 | Runtime and source provenance cover every result-producing dependency through binding, run envelope, and manifest without entering the scientific configuration | Manifest validation |
| I-042 | A figure is traceable to immutable results and figure-building source | Evidence ledger |
| I-043 | Publication is write-once at a content-addressed identity and creates a separate immutable publication record | Publication layer |
| I-044 | Recovery never converts ambiguous execution into a fresh uncounted execution | Recovery layer |
| I-045 | Scientific execution requires a valid external authorization matching exact configuration, binding, operation, and execution identity and cannot be invoked as a test | Stage gate |
| I-046 | Part VII-dependent semantics remain provisional until separately frozen | Network/route interface |
| I-047 | An unsupported execution mode fails closed | Runner entry |
| I-048 | A pre-publication execution/result manifest cannot be complete when a required artifact is absent or hash-mismatched | Manifest validation |
| I-049 | Every derived hash excludes its own field and uses a named canonical projection and hash domain | Hash validation |
| I-050 | Object content, physical-state payload, policy-memory payload, augmented replay-state, execution-semantics, trace-payload, and artifact-byte hashes remain distinct | Type/hash validation |
| I-051 | Non-scientific storage, wall-clock, host, process, and publication metadata do not alter object content, physical-state, policy-memory, or augmented replay-state hashes | Hash validation |
| I-052 | `ExperimentConfiguration` contains scientific choices only and no implementation hashes, execution binding, or authorization | Configuration validation |
| I-053 | `ExecutionBinding` pins one accepted configuration, implementation/source identity, execution identity, runtime constraints, artifact contract, and exclusions without adding science | Binding validation |
| I-054 | `StageAuthorization` and its non-recursive authenticity evidence remain external to authorized objects and are validated for authenticity, issuer/operation scope, time, revocation, predecessor evidence, exact hashes, and execution identity | Authorization boundary |
| I-055 | Canonical scientific trace payload or confirmed durable prefix and run-specific trace envelope are separate immutable artifacts | Trace validation |
| I-056 | Phase 9 registers future/transit/status state but never reapplies an immediate effect owned in phase 8 | Epoch ownership validation |
| I-057 | `ExecutionResultManifest` is immutable and finalized before publication without publication confirmation fields | Manifest validation |
| I-058 | Publication facts exist only in a separate post-publication `PublicationRecord` | Publication validation |
| I-059 | The core numeric substrate and numerical-policy interface do not silently freeze future domain-owned precision, tolerance, or approximation rules | Type and domain-policy validation |
| I-060 | `PolicyMemoryPayloadHash` is non-self-referential and excludes object identity, lineage, trace, durability, storage, and run metadata | Hash and policy validation |
| I-061 | Every accepted stateful-policy configuration pins an exact accepted initial memory at decision epoch zero; open-loop and stateless arms record memory as `NOT_APPLICABLE` | Configuration validation |
| I-062 | A stateful augmented closed-loop replay state is identified by both physical-state and policy-memory payload hashes without merging their meanings | Replay-state validation |
| I-063 | Every committed stateful policy decision atomically and durably records exactly one next memory, its before/after hashes, and its canonical trace row without mutating `Z_k` or physical update ownership | Policy decision durability |
| I-064 | Canonical scientific traces record initial, before/after, and terminal or last-confirmed policy-memory hashes and applicable augmented replay-state hashes | Trace validation |
| I-065 | A deterministic fault-injection replay claim additionally requires the identical prospectively declared `FaultSchedule` and fault-delivery semantics | Reproducibility |
| I-066 | Undeclared operational interruption or durability failure is run-specific evidence, not a scientific-determinism violation or retroactive fault schedule | Failure classification |
| I-067 | Every known durable canonical scientific trace prefix and its last confirmed physical/policy-memory pair are immutable and explicitly classified | Recovery and trace durability |

## 10. Reproducibility and artifact durability

### 10.1 Canonical configuration serialization

The future framework SHALL define one canonical byte serialization before any
configuration, execution binding, state, authorization, result, or manifest
can be accepted. The v0.1 requirements are:

- UTF-8 text with Unicode normalized to NFC;
- one declared canonical media type and serializer version;
- object keys sorted by a specified Unicode code-point rule;
- arrays retain scientifically declared order;
- mathematical sets serialize as arrays sorted by a declared stable key;
- no insignificant whitespace;
- integers use minimal base-10 spelling;
- the core numeric substrate defines canonical integers, rationals, normalized
  decimals, and any permitted encoded floating value without claiming to fix
  the precision, tolerance, or numeric semantics of every future domain;
- `NaN`, positive infinity, and negative infinity are forbidden;
- timestamps use one declared UTC representation and precision;
- units, dimensions, regions, boundaries, horizons, statuses, and object
  references are explicit rather than inferred from field names;
- aliases are resolved before serialization;
- secrets and host-specific storage paths are excluded from scientific
  content and captured separately when operationally necessary.

Canonical JSON is a possible implementation choice, but this document does
not create a JSON schema or freeze the exact canonicalization standard. That
choice is UQ-03 in the unresolved register. Domain-owned numerical policies
SHALL pin their own precision, rounding, tolerance, approximation, and
cross-platform requirements through the common numerical-policy interface;
I-0 freezes that core interface and substrate, not every future domain value.

Every object content hash, physical-state payload hash, policy-memory payload
hash, augmented closed-loop replay-state hash, execution-semantics hash,
canonical scientific trace payload hash, and artifact byte hash SHALL use its
separate domain and exact non-self-referential projection. Configuration
identity uses `ObjectContentHash` from §4.3; it is not the hash of a stored
record containing `object_content_hash`, lifecycle, authorization, or storage
metadata.

Hash verification occurs at object and configuration acceptance, initial
policy-memory validation, binding, preflight, execution entry, every policy
memory transition, result/manifest finalization, and publication as
applicable. A mismatch fails closed.

### 10.2 Seeds and random-stream ownership

A deterministic configuration SHALL state `randomness=NONE` and SHALL not
instantiate a pseudorandom generator.

A stochastic configuration SHALL record:

- master seed as fixed-width bytes or canonical lowercase hexadecimal;
- generator family, version, and platform guarantees;
- stream-derivation version;
- complete stream registry;
- each stream owner and purpose;
- counter/draw consumption in the trace or a replay-equivalent contract;
- shared-stream relationships across arms and replicates;
- seed disclosure and privacy rules.

Seeds are reproducibility inputs, not permission to explore unregistered
outcomes. Failed and rejected events SHALL have a frozen draw-consumption rule
so recovery or control flow cannot shift later streams invisibly.

### 10.3 Runtime and source provenance

Runtime provenance SHALL capture at minimum:

- repository URL or identity, branch as contextual metadata, and source commit;
- dirty-tree state and exact hashes of all result-producing source files;
- Python implementation and full version;
- operating system, kernel, architecture, CPU-relevant numerical features,
  locale, and time zone;
- locked dependency names, versions, source hashes, and wheel/build identities;
- arithmetic backend, precision, rounding, tolerance, and parallelism settings;
- environment variables that can alter science, with secrets redacted but
  presence and source recorded;
- entry point and invoked arguments in a non-secret canonical form;
- process and worker topology when it can affect ordering;
- container or environment image digest when used;
- clock source and timestamp precision;
- configuration, protocol, plan, schema, foundation, and implementation hashes.

Prospectively required source, implementation, dependency, arithmetic, and
runtime constraints that can affect science belong in `ExecutionBinding` and
its execution-semantics projection. Observed run-instance facts—actual host,
process IDs, wall-clock timestamps, storage locations, and runtime logs—belong
in `RunTraceEnvelopeV1` and `ExecutionResultManifest`. Undeclared process,
host, or durability interruption evidence belongs there as run-specific
failure evidence and is not retroactively promoted to a scientific fault
schedule. Publication facts belong only in `PublicationRecord`. None of these
operational facts is added to the accepted scientific
`ExperimentConfiguration`.

Provenance capture is part of preflight. If required provenance cannot be
captured, scientific execution SHALL not begin.

### 10.4 Trace payload and run-envelope contract

Every state-affecting or decision-relevant event SHALL emit a canonical
scientific trace row containing:

- accepted configuration object content hash and execution-semantics hash in
  the trace header, not repeated as run identity in every row;
- initial physical-state payload hash, applicable initial policy-memory
  payload and augmented replay-state hashes, and exact fault-schedule hash or
  `NOT_APPLICABLE` in the header;
- epoch and full deterministic `EventKey`;
- phase ordinal;
- event, action, group, actor, provider, region, provisional route, and
  resource references as scientifically applicable;
- predecessor and successor `StatePayloadHash` values;
- permitted-information-view scientific hash for policy events;
- before and after `PolicyMemoryPayloadHash` values and the resulting
  `AugmentedClosedLoopReplayStateHash` for every stateful policy decision;
- proposal, admission, epoch-wide ownership, phase-commit, measurement, and
  scientifically relevant failure references;
- typed requested, admitted, rejected, deferred, completed, lost, expired, and
  pending quantities as applicable;
- capacity and reservation scientific snapshot references;
- uncertainty and random-stream/draw coordinates;
- scientific lifecycle status before and after; and
- resolution state;
- terminal or last-confirmed physical/policy-memory hashes, confirmed row
  count, and trace completeness in the footer.

Canonical scientific rows are append-only and deterministically ordered. They
exclude execution identity, wall-clock, host/process/runtime observations,
storage and publication metadata. Those fields belong to the separate
`RunTraceEnvelopeV1`, which references the canonical scientific trace payload
hash and the exact execution binding. The exact byte-identical replay
projection is only `CANONICAL(CanonicalScientificTracePayloadV1)` under the
normal-completion or declared-fault conditions in §8.3. An undeclared
operational interruption does not enter a scientific row: its run envelope
links the immutable longest hash-valid scientific prefix and records
`PARTIAL_DURABLE_PREFIX`, `NO_DURABLE_TRACE`, or
`UNRESOLVED_DURABILITY` as applicable. A summary or run envelope is not a
substitute for a missing canonical scientific trace or confirmed prefix.

### 10.5 Summaries, figures, and evidence

Every derived artifact SHALL record:

```text
immutable input artifact hashes
    + derivation/analysis source hash
    + accepted analysis configuration object content hash
    + execution-semantics or analysis-numerical-policy hash
    -> canonical scientific derived payload

exact derived artifact bytes
    -> ArtifactByteHash

run-specific runtime/host/storage provenance
    -> separate immutable run/derivation envelope
```

Run-specific provenance is linked to the derived artifact but is excluded from
the canonical scientific payload and its object-content preimage. A runtime
constraint that can change scientific values must already be pinned through
the applicable execution semantics or analysis numerical policy; it is not
demoted to non-scientific metadata after the fact.

Figure metadata SHALL include the future-books evidence label: schematic,
mathematically derived, tested implementation, observed in a registered run,
research hypothesis, or institutional design choice.

An evidence ledger SHALL connect each presented claim to exact result rows or
summaries, analysis, figure, limitations, and claim status. A change in figure
styling that does not alter data still produces a new figure artifact version;
it does not alter the source result.

### 10.6 Write-once publication and separate publication record

Publication SHALL use a content-addressed destination or an equivalent
write-once key. Before writing, the publisher SHALL verify:

1. publication-stage authorization authenticity and full §11.3 validation;
2. exact accepted configuration, execution binding, execution identity, and
   their match to the external authorization;
3. immutable pre-publication `ExecutionResultManifest` status and hash;
4. every required object-content and artifact-byte hash;
5. that no runner or scientific execution is being triggered;
6. destination absence or byte identity with the intended artifact; and
7. durable creation of a separate immutable `PublicationRecord`.

If a destination already contains different bytes, publication fails with
`ALREADY_EXISTS_DIFFERENT`. Overwrite is forbidden. Publication facts SHALL
not be backfilled into the pre-publication manifest.

### 10.7 Recovery boundary

Recovery is operational reconstruction from durable evidence, not a new
scientific run. A recovery procedure SHALL first classify the durable state:

| Durable evidence | Recovery classification | Permitted action under recovery authority |
|---|---|---|
| No scientific state advanced and no execution receipt | `NO_DURABLE_EXECUTION_RECEIPT` | Stop; any invocation decision belongs to the applicable study authority |
| Complete canonical artifact already durable and hash-matching | `RECOVERED_IDENTICAL` | Reattach or republish byte-identical references only |
| Hash-valid canonical trace prefix with known durable physical and policy-memory hashes | `FAILED_AFTER_PARTIAL_ADVANCE` plus `PARTIAL_DURABLE_PREFIX` | Preserve the exact prefix and state/memory pair; do not restart as a fresh run |
| Proof that no trace or policy decision became durable | `NO_DURABLE_TRACE` | Preserve run-specific failure evidence; any retry requires its own applicable authority |
| Ambiguous trace, physical-state, or policy-memory durability or inconsistent hashes | `UNRESOLVED_DURABILITY` | Preserve every confirmed prefix, quarantine the ambiguous suffix, and require separate correction/recovery decision |
| Complete result but incomplete publication | `PUBLICATION_INCOMPLETE` | Publish existing immutable artifacts if separately authorized |

Recovery SHALL never reset invocation counts, erase failure evidence, or
manufacture a missing receipt. Recovery or completion of publication creates
or recovers a separate `PublicationRecord`; it does not add fields to an
existing `ExecutionResultManifest`. It may extend only an exact confirmed
canonical prefix under a separately authorized recovery contract, and it may
not relabel an undeclared operational interruption as a violation of
scientific determinism or as a prospectively declared fault.

### 10.8 Correction boundary

A correction requires its own authorization and produces:

- a new immutable artifact with a new identity/version/hash;
- a correction record naming the original;
- reason, scope, authority, and method;
- whether scientific execution was or was not repeated;
- a new corrected pre-publication manifest when required, linked to rather
  than replacing the original manifest, plus an evidence-ledger relation;
- preservation of the original publication and its historical claims.

Corrections SHALL not overwrite raw results, accepted configurations,
original manifests, or original figures. A reinterpretation is not a data
correction and belongs to an interpretation stage.

## 11. Scientific workflow separation

### 11.1 Stage state machine

The framework SHALL represent these separately authorized stages:

```text
ANALYTICAL_DESIGN
    -> PREREGISTRATION
    -> IMPLEMENTATION
    -> STATIC_AND_SYNTHETIC_VALIDATION
    -> PRE_EXECUTION_AUDIT
    -> AUTHORIZED_SCIENTIFIC_EXECUTION
    -> INTERPRETATION
    -> PUBLICATION
```

An arrow identifies a possible dependency, not automatic authorization. A
stage may stop, fail, or require revision. Revision to an earlier stage
creates new versioned artifacts and does not rewrite accepted history.

Recovery and correction are separately authorized operational workflows, not
shortcuts between scientific stages. Recovery reconstructs already durable
evidence. Correction creates linked new artifacts. Neither authorizes a model
step, rerun, reinterpretation, or publication unless that operation also has
its own applicable stage authority.

### 11.2 Stage permissions

| Stage | Permitted outputs | Forbidden actions |
|---|---|---|
| Analytical design | Definitions, equations, assumptions, static examples, theorem candidates, open questions | Candidate outcome inspection, scientific run |
| Preregistration | Accepted immutable scientific `ExperimentConfiguration` containing hypotheses, falsifiers, worlds, arms, parameters, metrics, tolerances, classifications, analysis plan, stateful-policy initial memory, and any prospective scientific fault schedule | Missing or mutable initial policy memory, retroactive fault schedule, result-producing implementation/source-code/dependency hashes, execution authorization, tuning from results, implementation-dependent relaxation |
| Implementation | Code matching accepted design, implementation and source provenance | Scientific execution, alteration of accepted configuration |
| Static and synthetic validation | Parsing, type/schema checks, algebra checks, pure static fixtures, authorized synthetic operational checks | Registered worlds, candidate trajectories, outcome inference |
| Pre-execution audit | Construct and accept the separate `ExecutionBinding`; verify configuration/binding/source/runtime/artifact, initial-memory, fault-delivery, and trace-prefix contracts without advancing state | Embedded authorization, scientific model step, invocation count consumption unless the applicable protocol defines otherwise |
| Authorized scientific execution | Exact accepted configuration and binding plus external authorization for their exact hashes and execution identity; durable physical/memory transitions and traces/results | Tuning, interpretation-driven rerun, hidden fallback, retroactive fault declaration |
| Interpretation | Analysis of immutable registered results under accepted plan | Result mutation, retroactive hypotheses |
| Publication | Write-once artifacts, figures, evidence ledger, claims and limitations | Runner invocation, overwrite, silent correction |

### 11.3 Authorization record

Each authorized operation SHALL receive the external immutable
`StageAuthorization` and separate authorization-evidence bundle satisfying
§6.16. The configuration and execution binding do not contain, confer, or
imply that authorization.

Authorization validation SHALL complete before the authorized interface is
entered and SHALL verify all of the following against immutable evidence:

1. the authorization object's content hash and canonical preimage;
2. authenticity under the configured trust mechanism;
3. issuer identity, issuer authority scope, and any delegation chain;
4. the requested stage and exact operation are within operation scope;
5. exact configuration ID, version, object content hash, and the lifecycle
   status required by the requested operation—draft content for its atomic
   acceptance, accepted content for every later operation;
6. exact execution-binding ID, version, object content hash, and required
   lifecycle status when a binding exists—draft content for its atomic
   acceptance, accepted content for scientific execution and publication;
7. exact execution identity for execution or any run-specific artifact
   operation;
8. `not_before`, expiry, decision-time clock rules, and temporal validity;
9. current revocation status against the pinned revocation authority;
10. invocation/single-use limits and explicit exclusions;
11. exact predecessor-stage evidence identities, hashes, and accepted status;
12. consistency between the binding's configuration reference and the
    supplied configuration.

Failure of any check is an authorization failure, not an unresolved permission
to proceed. The concrete authenticity, trust-anchor, issuer registry,
delegation, trusted-clock, and revocation mechanism remains UQ-35 for I-0; an
implementation SHALL NOT substitute “file exists,” a username string, or a
repository permission for that missing mechanism.

A generic repository permission or existence of later-stage files is not
scientific authorization. The runner SHALL require an external authorization
specific to the exact accepted configuration, exact accepted execution
binding, exact execution identity, and requested state-advancing operation.

### 11.4 Fail-closed stage guard pseudocode

```text
function authorize_call(
    interface,
    configuration_or_not_applicable,
    binding_or_not_applicable,
    exact_execution_identity_or_not_applicable,
    requested_operation,
    external_authorization_evidence_bundle,
    decision_time
):
    authorization = external_authorization_evidence_bundle.authorization
    require verify_object_content_hash(authorization)
    require authenticity_envelope_matches_exact_authorization_hash(
        external_authorization_evidence_bundle.authenticity_envelope,
        exact_ref(authorization)
    )
    require verify_authorization_authenticity(
        external_authorization_evidence_bundle
    )
    require issuer_scope_covers(
        external_authorization_evidence_bundle,
        requested_operation,
        exact_ref_or_not_applicable(configuration_or_not_applicable),
        exact_ref_or_not_applicable(binding_or_not_applicable)
    )
    require requested_operation
            in authorization.allowed_operations
    require decision_time within authorization temporal validity
    require revocation_evidence_is_current_and_not_revoked(
        external_authorization_evidence_bundle.revocation_evidence,
        exact_ref(authorization),
        decision_time
    )
    require predecessor_stage_evidence_exact_and_accepted(
        external_authorization_evidence_bundle
    )
    require exact object hashes and execution identity match authorization
    require requested operation not explicitly excluded
    require invocation and single-use conditions remain available

    if interface.accepts_experiment_configuration:
        require configuration_or_not_applicable.status == DRAFT
        require binding_or_not_applicable == NOT_APPLICABLE
    else if configuration_or_not_applicable != NOT_APPLICABLE:
        require configuration_or_not_applicable.status == ACCEPTED

    if interface.accepts_execution_binding:
        require binding_or_not_applicable.status == DRAFT
        require configuration_or_not_applicable.status == ACCEPTED
        require binding_or_not_applicable.accepted_configuration_ref
                == exact_ref(configuration_or_not_applicable)
    else if binding_or_not_applicable != NOT_APPLICABLE:
        require binding_or_not_applicable.status == ACCEPTED

    if interface.can_advance_model_state:
        require authorization.stage
                == AUTHORIZED_SCIENTIFIC_EXECUTION
        require configuration_or_not_applicable.status == ACCEPTED
        require binding_or_not_applicable.status == ACCEPTED
        require exact_execution_identity_or_not_applicable
                == binding_or_not_applicable.execution_identity

    if interface.can_publish:
        require authorization.stage == PUBLICATION
        require configuration_or_not_applicable.status == ACCEPTED
        require binding_or_not_applicable.status == ACCEPTED

    return immutable_authorization_validation_record(VALID)
```

Naming a scientific runner `test_*`, `fixture_*`, `preview_*`, or `dry_run_*`
does not change `can_advance_model_state`.

## 12. Testing and validation taxonomy

### 12.1 Class T0 — static schema and algebra checks

T0 checks do not advance model state. They may verify:

- Markdown and registry syntax;
- identifier, version, reference, and hash consistency;
- dimensions, units, boundary compatibility, and exact conversions;
- equation signs and hand arithmetic;
- canonical serialization fixtures;
- policy-memory payload and augmented replay-state hash fixtures;
- configuration initial-memory and fault-schedule applicability checks;
- object lifecycle transition tables;
- dependency acyclicity;
- configuration completeness without constructing a scientific world state;
- symbolic closure equations;
- source-to-specification cross-references.

T0 may run during a specification or implementation stage when authorized.

### 12.2 Class T1 — synthetic operational checks

T1 checks exercise operational mechanisms on clearly artificial records that
are not registered worlds, arms, or candidate scientific trajectories.
Examples include:

- rejecting a duplicate event key;
- detecting a hash mismatch;
- refusing an incompatible unit addition;
- validating an append-only ledger chain;
- applying a prospectively declared validation-only fault schedule to a
  filesystem interruption around an inert dummy artifact;
- validating an immutable synthetic policy-memory before/after transition
  without calling a scientific policy;
- confirming that a policy sandbox cannot see a fabricated future-only field;
- detecting overlapping update ownership without applying a scientific
  transformation.

T1 may touch framework plumbing but SHALL not call a scientific transition,
distortion, policy, runner, or experiment function with a registered or
candidate scientific state. A fault schedule does not make a T1 check
scientific only when its targets and inputs remain inert and no scientific
function is reachable.

### 12.3 Class T2 — exact analytical fixtures

T2 implements values already derived and frozen analytically. It may compare
pure-function outputs on isolated synthetic individual states with exact
expected values, provided the stage explicitly authorizes those checks.

The first proposed fixtures should come from already frozen hand arithmetic,
such as bridge M1–M9 and the dynamic foundation's static capacity and queue
identities. Using those fixtures during this specification stage is not
authorized; this document only names the later category.

T2 SHALL NOT:

- step an engine through a trajectory;
- search parameters or schedules;
- inspect unregistered candidate outcomes;
- use a frozen experiment world as a “fixture”;
- infer empirical support from a passing implementation check.

### 12.4 Class T3 — scientific experiments

Any check that advances a model state, calls a scientific runner, produces a
trajectory, evaluates a registered arm, samples a scientific disturbance, or
inspects a candidate outcome is T3 unless a frozen protocol explicitly and
prospectively classifies a narrowly isolated pure function otherwise.
A fault-injection schedule applied to a registered scientific configuration,
state, policy, or runner is T3 even when the injected event is intended to
terminate execution early.

T3 requires accepted preregistration, completed implementation and validation,
pre-execution audit, and separate scientific-execution authorization. A T3
call remains a scientific execution when invoked by a unit-test framework.

### 12.5 Anti-disguise decision table

| Question | If yes |
|---|---|
| Does the call use a registered or candidate scientific world, arm, policy, seed, or configuration? | Classify T3 |
| Can it advance `Z_k`, even by one epoch or substep? | Classify T3 |
| Can it produce or inspect a trajectory or endpoint used to assess a hypothesis? | Classify T3 |
| Does it choose parameters, tolerances, comparators, worlds, or schedules using outputs? | Forbidden outside a separately authorized design process; T3 evidence cannot tune a frozen plan |
| Does it call a runner, simulation entry point, finalizer, or scientific policy loop? | Classify T3 |
| Does it inject a fault into a registered scientific state, policy-memory transition, or execution? | Classify T3 and require the accepted fault schedule |
| Is it limited to parsing, hashing, typing, algebra, or an isolated exact static fixture? | T0 or T2, subject to stage authority |
| Does it exercise only inert durability or authorization plumbing? | T1, provided no scientific function is reachable |

A validation report SHALL list executed interface classifications, not merely
test filenames.

## 13. Static examples

These examples are declarative arithmetic and state tables only. They were not
executed.

### 13.1 Accepted-object immutability

Suppose configuration `ebu:config:part-vi:matrix-v1` version `1.0.0` has hash
`sha256:aaa...` and becomes `ACCEPTED`. A tolerance change cannot retain
version `1.0.0` or hash `aaa...`. It requires a new object version, for
example `1.1.0`, a new hash, and `supersedes_ref` pointing to the original.
The original remains accepted historical evidence unless separately revoked
before execution.

### 13.2 Explicit missing-state example

At horizon `H`, a delayed ecological measurement is due after `H`. The result
field is:

| Field | Incorrect | Correct |
|---|---|---|
| Later effect | `0` | `PENDING`, with due horizon and provenance |

The correct record does not claim complete closure at `H`.

### 13.3 Queue closure example

For one compatible queue, let previous admitted backlog be `2 crates`, new
presented demand `5 crates`, admitted `3`, rejected `1`, and pending outside
the queue `1`. The request partition is:

\[
5=3+1+1.
\]

If completed flow is `4 crates` and no admitted demand expires, the next
queue is:

\[
q_{k+1}=2+3-4-0=1\ \text{crate}.
\]

Subtracting the rejected or outside-pending crates again would be a typed
accounting error.

### 13.4 Information leakage example

A failure occurs at epoch `7` and is measured at epoch `7`. A policy decision
at epoch `6` cannot receive that failure value merely because a complete
frozen exogenous history exists in the engine. The engine may use the history
to evolve the physical state at the declared phase; the policy view excludes
the future entry until its availability epoch.

### 13.5 Physical, causal, and settlement separation

A group endpoint gives physical measurement `M_G = 12 EBU`. No child causal
model is identified. An accepted institutional rule assigns `S_1 = 5 EBU`
and `S_2 = 6 EBU`. Closure requires:

\[
R_G=12-5-6=1\ \mathrm{EBU}.
\]

The record states:

| Record | Value/status |
|---|---|
| Physical group measurement | `12 EBU`, `PRESENT` |
| Child causal contributions | `UNIDENTIFIED` |
| Institutional shares | `5 EBU`, `6 EBU` |
| Explicit residual | `1 EBU` |

The allocation does not convert `5` and `6` into measured causal facts.

### 13.6 Simultaneous but separate actions

Two actions share an epoch but have disjoint write supports, constraint
supports, and observation models; the distortion is proven additively
separable over their changed coordinates. They may remain separate physical
transitions. If they are stored in one receipt batch, the batch changes
neither their group status nor their physical values.

### 13.7 Provisional route example

A route plan lists three typed edge references and a declared delay model.
The framework may validate identities, capacity-unit compatibility, and that
rerouting preserves completed segments. It may not claim that graph length is
physical distance or that the chosen path assigns causal credit. Those fields
remain `UNRESOLVED` pending a Part VII foundation.

### 13.8 Non-self-referential hash example

Suppose an accepted object has object-content payload `P`. Its object content
hash is computed from the domain tag, identity/schema/version fields,
authority and supersession references, and `P`. The stored
`object_content_hash`, storage URI `/store/a`, ingestion time, and host
`worker-1` are absent from the preimage.
Moving the bytes to `/store/b` on `worker-2` changes record metadata but leaves
the object content hash unchanged. Changing `P` changes the hash and requires a
new object version after acceptance.

For a `SystemState`, its state payload hash is independently computed from the
typed `(epoch, x, g, q, c, ell, external-inputs-applied)` projection. Neither
hash contains itself or the other derived hash field.

### 13.9 Configuration, binding, and authorization example

An accepted configuration `C` freezes hypotheses, worlds, parameters, metrics,
and analysis. Later binding `B` references the exact hash of `C`, pins source
and implementation hashes, execution identity `run-17`, runtime constraints,
artifact contract, and operational exclusions. External authorization `A`
references the exact hashes of `C` and `B`, the operation
`ADVANCE_SCIENTIFIC_STATE`, and execution identity `run-17`.

`C` does not contain `B` or `A`; `B` does not contain `A`. Authorization `A`
cannot be reused with another binding or `run-18`, and changing a scientific
parameter requires a new configuration rather than a binding edit.

### 13.10 Deterministic trace projection example

Two separately authorized normally completed replay bindings use different
execution identities, wall-clock times, hosts, and storage paths but have
equal accepted configuration hashes, equal execution-semantics hashes, equal
initial physical and applicable policy-memory payload hashes, equal ordered
scientific inputs, and no fault schedule. Their canonical scientific trace
payload bytes must be identical. Their run-envelope bytes are expected to
differ.

### 13.11 Cross-phase ownership example

An action's immediate consumption is committed in phase 8. Phase 9 registers a
new delayed measurement obligation and updates its commitment status. The
epoch ownership record assigns immediate consumption to phase 8 and the new
obligation/status records to phase 9. Phase 9 cannot consume the resource a
second time. When the delayed obligation matures at a future epoch, its due
state change is owned by phase 1 of that future epoch.

### 13.12 Manifest and publication example

The immutable `ExecutionResultManifest` lists configuration, binding,
authorization, trace, run envelope, results, and intended publishable
artifacts. It contains no destination or publication receipt. After a
separately authorized write succeeds, `PublicationRecord` references that
unchanged manifest and records destinations, published byte hashes,
write-once checks, publisher identity, and receipt time.

### 13.13 Stateful policy-memory replay example

A stateful policy begins with accepted memory `M_0`, available at epoch `0`,
and physical state `S_0`. The accepted configuration pins both payload hashes.
At epoch `0`, the policy consumes `M_0`, proposes action set `P_0`, and returns
candidate memory `M_1` for epoch `1`. The durable decision row records:

| Field | Static value |
|---|---|
| Physical predecessor | `StatePayloadHash(S_0)` |
| Memory before | `PolicyMemoryPayloadHash(M_0)` |
| Proposal | `ObjectContentHash(P_0)` |
| Memory after | `PolicyMemoryPayloadHash(M_1)` |
| Physical mutation by memory commit | `NONE` |

The augmented replay state uses the physical and memory payload hashes. Two
runs with identical `S_0` but different `M_0` values do not have equal replay
inputs. If the memory transaction fails before atomic durability, `M_0`
remains current and screening does not start.

### 13.14 Declared fault and undeclared interruption example

Runs `A` and `B` normally complete with equal configuration, execution
semantics, initial physical/memory hashes, external inputs, and stochastic
inputs; their canonical scientific trace payload bytes must match. Runs `C`
and `D` are a prospectively declared fault study and additionally use the same
`FaultSchedule`; if the declared delivery semantics reach the same scheduled
fault-terminal boundary, their canonical fault-terminal payload bytes must
match.

Run `E` instead loses its host at an undeclared point after seven canonical
rows are known durable. Those seven rows and their final confirmed
physical/memory hashes are preserved as `PARTIAL_DURABLE_PREFIX`. The host
loss belongs in the run-specific failure evidence. The absent suffix is not a
scientific-determinism violation and the host loss is not retroactively added
to a fault schedule.

## 14. Failure semantics and responsibility

### 14.1 Failure envelope

Every failed interface call SHALL return or durably record a typed failure
envelope:

| Field | Meaning |
|---|---|
| `failure_id` | Stable unique identity |
| `failure_code` | Registered machine-readable code |
| `stage` | Workflow stage at failure |
| `interface_ref` | Interface and implementation version |
| `object_refs` | Inputs involved, with versions and hashes |
| `event_key` | Present if failure occurred during event processing |
| `state_advance` | Physical-state advance: `NONE`, `ATOMIC_COMPLETE`, `PARTIAL`, or `UNRESOLVED` |
| `policy_memory_advance` | `NONE`, `ATOMIC_COMPLETE`, or `UNRESOLVED`; separately classified from physical state |
| `durability_state` | Which records are known durable |
| `canonical_trace_state` | Completeness class, confirmed row count, and durable-prefix hash/reference when known |
| `scientific_status_effect` | Explicit effect, including none |
| `retry_class` | `FORBIDDEN`, `SAME_BYTES_ONLY`, `REQUIRES_AUTHORITY`, or `NOT_APPLICABLE` |
| `evidence_refs` | Logs, hashes, receipts, or environmental evidence |
| `human_summary` | Non-authoritative explanation |

A raised exception without this envelope is insufficient for a scientific or
publication boundary. A human message may not override `state_advance` or
`retry_class`.

### 14.2 Failure layers

| Layer | Example | Owner | Required response |
|---|---|---|---|
| Reference integrity | Hash mismatch | `identity`/`registry` | Fail before use |
| Authorization | Invalid authenticity, issuer/operation scope, time, revocation, predecessor evidence, object hash, or execution identity | `authorization` | Fail before entering the authorized interface |
| Type integrity | Unit or boundary mismatch | `types` | Fail before arithmetic |
| Scientific domain | Distortion outside domain | `distortion` | Explicit unresolved/out-of-boundary; no extrapolation |
| Information boundary | Future field read | `policy`/stage gate | Fail decision before admission |
| Admission | Capacity or prerequisite failure | `commitments` | Reject, defer, partial, or unresolved under frozen rule |
| Grouping | Incompatible boundary or uncertain coupling | `bridge` | No invented group value |
| Proposal | Transformation cannot specify all owned effects | `actions`/`execution` | Fail before mutation |
| Policy memory | Before-memory mismatch, duplicate transition, or non-atomic decision/memory append | `policy`/`execution` | Preserve prior memory unless an atomic next-memory record is proven durable; do not mutate physical state |
| Commit | Ownership conflict | `execution` | Fail before mutation |
| Durability | Undeclared interruption or ambiguous partial write | execution/artifact store | Preserve the longest confirmed canonical prefix and state/memory pair; classify run-specific partial or unresolved evidence without declaring scientific nondeterminism |
| Measurement | Missing or failed instrument | `observation` | Record failed/partial/unresolved measurement |
| Causal inference | Identifiability absent | `causal` | Return `UNIDENTIFIED`; do not allocate causality |
| Settlement | Shares fail closure | `settlement` | Reject settlement; preserve physical receipt |
| Manifest | Missing required artifact | `artifacts` | Partial/unresolved manifest |
| Publication | Different bytes at destination | `publication` | Refuse overwrite |

### 14.3 Preconditions and postconditions by responsibility

Physical modules own state transition and measurement. Their postconditions
are typed state and physical records, not causal or institutional conclusions.

Causal modules own only claims justified by a pinned intervention or causal
model. Their postconditions include identification status and any causal
remainder. They cannot rewrite endpoint measurement.

Policy modules own proposals under declared information. Their postconditions
are decisions and separately typed immutable memory updates, not physical
state changes or proof that the proposal is feasible or beneficial. The
execution durability layer atomically records the decision and next memory
before physical screening.

Institutional modules own priority, access, guarantee, settlement, residual,
appeal, and correction rules. Their postconditions are institutional records
that reference, but never replace, physical and causal records.

Authorization modules own validation of external authority records. They do
not create scientific permission from an object's presence and do not mutate
the configuration, binding, result, manifest, or publication record they
authorize.

## 15. Decision register

`ACCEPTED` decisions are normative for v0.1. `PROVISIONAL` decisions expose a
stable interface but await a named foundation. `DEFERRED` decisions must be
resolved before the feature they govern can be scientifically used.

| ID | Status | Decision | Rationale and consequence |
|---|---|---|---|
| DR-001 | `ACCEPTED` | Use one framework and object model for Parts IV–IX | Prevents incompatible scripts and disconnected scientific authority |
| DR-002 | `ACCEPTED` | Import Sequential–Parallel Bridge v0.2 unchanged | Preserves the frozen Part VI meanings and equations |
| DR-003 | `ACCEPTED` | Import `Z_k`, augmented policy state, and the ten event phases unchanged from Dynamic Coordination v0.1 | Gives deterministic dynamic semantics without local reinterpretation |
| DR-004 | `PROVISIONAL` | Expose provider graphs and route references while keeping route meaning subordinate to a future Part VII foundation | Supports integration without freezing premature distance or route laws |
| DR-005 | `ACCEPTED` | Separate physical state, topology, policy, objectives, constraints, measurements, and institutional allocation | Preserves the dynamic foundation's seven layers |
| DR-006 | `ACCEPTED` | Separate physical measurement, causal inference, policy decision, and settlement in both types and modules | Prevents scientific and institutional category errors |
| DR-007 | `ACCEPTED` | Pin all accepted references by logical ID, semantic version, and non-self-referential object content hash | Makes provenance and immutability checkable |
| DR-008 | `ACCEPTED` | Allow in-place revision only for unreferenced drafts; acceptance freezes scientific content immediately | Protects accepted scientific objects before execution exists |
| DR-009 | `ACCEPTED` | Use explicit resolution states instead of null/zero omission | Preserves pending and incomplete effects |
| DR-010 | `ACCEPTED` | Treat units, resource types, regions, boundaries, and horizons as types, not comments | Makes invalid aggregation fail closed |
| DR-011 | `ACCEPTED` | Implement deterministic mode before stochastic mode | Establishes auditable semantics before random-stream complexity |
| DR-012 | `ACCEPTED` | Use one common pre-state for a joint-transition group and atomic proposal/commit separation | Preserves bridge measurement and prevents order artifacts |
| DR-013 | `ACCEPTED` | Carry one epoch-wide update-ownership record across mutating phases 1, 2, 8, 9, and 10 | Prevents duplicate due effects, topology changes, group effects, registrations, statuses, or drive |
| DR-014 | `ACCEPTED` | Make policy information views immutable, capability-limited, and traceable | Prevents future-data and cross-arm leakage |
| DR-015 | `ACCEPTED` | Keep open-loop and closed-loop interfaces distinct | Makes adaptation and memory scientifically visible |
| DR-016 | `ACCEPTED` | Record admission, rejection, deferral, and partial acceptance separately | Preserves queue and service accounting |
| DR-017 | `ACCEPTED` | Do not infer congestion from utilization alone | Requires a declared binding mechanism |
| DR-018 | `ACCEPTED` | Preserve completed route segments during rerouting | Prevents retrospective rewriting |
| DR-019 | `ACCEPTED` | Use named non-self-referential canonical projections and SHA-256 for object, physical state, policy memory, augmented replay state, semantics, trace, and artifact identities | Supports cross-system integrity checks without hash recursion or metadata contamination |
| DR-020 | `DEFERRED` | Select the exact canonical serialization standard | Must be frozen during implementation before accepted configs exist |
| DR-021 | `ACCEPTED` | Use owned random streams; forbid process-global randomness | Prevents component-order changes from shifting stochastic histories |
| DR-022 | `DEFERRED` | Select generator, seed derivation, and draw accounting | Required before stochastic implementation or preregistration |
| DR-023 | `ACCEPTED` | Require a canonical scientific trace payload or confirmed durable prefix, separate run envelope, and pre-publication execution/result manifest; summaries cannot substitute | Preserves reconstructibility and qualifies deterministic replay exactly |
| DR-024 | `ACCEPTED` | Use write-once publication, a separate post-publication record, and new-object corrections | Preserves historical scientific evidence without circular manifest publication claims |
| DR-025 | `ACCEPTED` | Treat recovery as reconstruction from durable evidence, including an exact canonical prefix and physical/policy-memory pair, not fresh execution | Prevents invocation laundering, lost policy state, and silent reruns |
| DR-026 | `ACCEPTED` | Make workflow stages independently authorized by external records validated against exact objects and operations | Protects information and scientific boundaries without embedding authority in science |
| DR-027 | `ACCEPTED` | Classify by capability, not function name, when separating tests from experiments | Prevents disguised scientific execution |
| DR-028 | `ACCEPTED` | Use exact frozen static fixtures before dynamic or stochastic studies | Gives implementation checks without outcome search |
| DR-029 | `ACCEPTED` | Make unsupported modes and undefined semantics fail closed | Prevents silent scientific fallback |
| DR-030 | `ACCEPTED` | Extend Parts IV–IX through adapters and registered domain packages | Preserves one core framework while allowing book-specific science |
| DR-031 | `ACCEPTED` | Split preregistered `ExperimentConfiguration` from later immutable `ExecutionBinding` | Keeps scientific choices independent of implementation, runtime, and execution authorization |
| DR-032 | `ACCEPTED` | Keep authenticity proof outside the authorization hash preimage and require authenticity, issuer/operation scope, temporal validity, revocation, predecessor evidence, exact hashes, and exact execution identity | Makes authorization a validated capability rather than a label or recursive signature record |
| DR-033 | `ACCEPTED` | Phase 9 may register future effects and statuses but may not apply an effect already committed in phase 8 | Preserves single ownership across immediate and delayed mechanics |
| DR-034 | `ACCEPTED` | Finalize an immutable execution/result manifest before publication and create publication evidence afterward in `PublicationRecord` | Removes impossible post-publication confirmation from the manifest preimage |
| DR-035 | `ACCEPTED` | I-0 freezes only the core numeric substrate and the interface for later domain-owned numerical policies | Avoids premature claims about every future domain quantity |
| DR-036 | `ACCEPTED` | Represent stateful policy memory as a separately typed immutable object with its own non-self-referential payload hash and pair it with the physical-state hash for closed-loop replay | Implements the imported augmented state without conflating informational and physical state |
| DR-037 | `ACCEPTED` | Require each stateful policy proposal to return exactly one next memory and atomically durably record decision plus memory before screening | Makes history-dependent policy replay complete without granting the policy physical mutation authority |
| DR-038 | `ACCEPTED` | Require full canonical trace byte equality for normally completed equal-input deterministic runs and require an identical prospective fault schedule for declared fault studies | Avoids both overclaiming determinism and exempting declared injected faults from replay |
| DR-039 | `ACCEPTED` | Treat undeclared operational interruption and durability failure as run-specific evidence while preserving every confirmed canonical prefix and completeness class | Separates scientific determinism from operational completion and prevents prefix loss |

## 16. Threat model

The threat model covers accidental error, implementation convenience,
scientific bias, operational failure, and institutional misuse. It does not
assume malicious intent is required for a threat to matter.

| ID | Threat | Failure mechanism | Required control | Residual risk |
|---|---|---|---|---|
| TM-001 | Foundation drift | Local code subtly changes an imported bridge definition | Pinned source hash, bridge conformance interfaces, exact fixtures | A later legitimate foundation revision requires explicit migration |
| TM-002 | Stale version pointer | Planning text refers to superseded foundation version | Accepted source register and fail-closed version resolution | Human summaries may remain stale outside accepted configs |
| TM-003 | Incomplete state | Relevant resource use, burden, queue, commitment, or delayed effect omitted | Boundary register, projection completeness, unresolved status | Reality can contain unknown effects not yet represented |
| TM-004 | False scalar aggregation | Unlike resources or institutional values are added | Dimensional/resource typing and declared conversion rules | A declared scalarization may still embody contestable values |
| TM-005 | Boundary laundering | Burden is moved outside the reported region or horizon | Parent-boundary references and out-of-boundary ledger | No finite boundary captures all reality |
| TM-006 | Same-baseline double counting | Children evaluated independently against `X_0` are summed as settlement | Exact group EBU and separate `N_G` diagnostic | Causal division may remain unidentified |
| TM-007 | Comparator shopping | Sequential order selected after outcomes | Preregistered comparator set and full range when required | Large comparator sets may be computationally difficult |
| TM-008 | Batch/group conflation | Shared storage or receipt processing is treated as interaction | Separate `ReceiptBatch` and `JointTransitionGroup` types | Operational UI may still confuse users |
| TM-009 | Allocation masquerading as causality | Institutional shares are labelled physical contributions | Separate modules/types and causal identification status | Institutions may publicly overstate allocations despite records |
| TM-010 | Future-data leakage | Policy reads future failures, future/candidate memory, full state, outcomes, or another arm | Capability-limited views, memory availability epochs, and read-set trace | Side channels in implementation require security review |
| TM-011 | Outcome-driven plan mutation | Parameters or tolerances change after candidate inspection | Accepted immutable config and stage ledger | Unauthorized external notes could influence a new design |
| TM-012 | Nondeterministic container order | Hash maps, sets, workers, or races resolve ties | Total event keys and canonical scientific trace ordering | Numerical libraries can retain platform differences |
| TM-013 | Duplicate physical update | Different phases or action/operations layers apply the same effect | Epoch-wide update ownership and atomic phase validation | Incorrectly specified ownership can omit rather than duplicate |
| TM-014 | Partial-commit ambiguity | Crash leaves unknown model-state advance | Transactional durability, predecessor/successor hashes, failure envelope | Some storage systems cannot guarantee atomicity without additional design |
| TM-015 | Retry laundering | Failed or partial execution is presented as no invocation | Durable invocation/authorization ledger and recovery rules | External commands outside framework remain governance risk |
| TM-016 | Silent stochastic fallback | Missing stream or model uses global/default randomness | Unsupported-mode failure, complete stream registry | Third-party libraries may consume hidden randomness |
| TM-017 | Seed coupling | Added component shifts all later draws | Domain-separated owned streams | Generator changes still require migration |
| TM-018 | Queue accounting error | Rejected or pending demand is subtracted from admitted queue | Typed partition and queue identities | Multiclass queues need additional frozen equations |
| TM-019 | Capacity double sale | Separate ledgers reserve the same capacity | One reconciled reservation authority per capacity version | Distributed reconciliation and network partitions remain open |
| TM-020 | Retrospective reroute | Completed losses or delays are erased after path change | Immutable segment history and suffix-only rerouting | Final route semantics remain provisional |
| TM-021 | Horizon truncation | Pending delayed harm is reported as zero | Explicit pending/out-of-boundary states and horizon ledger | Very long or unknown effects remain unresolved |
| TM-022 | Measurement/state conflation | Observation is treated as exact physical state | Separate measurement objects with age and uncertainty | Some state remains structurally unobservable |
| TM-023 | Recovery modifies science | Recovery re-runs or recomputes rather than restores | Evidence-classified recovery and same-bytes rule | Manual operational intervention needs audit |
| TM-024 | Result overwrite | Correction replaces original file | Content-addressed write-once publication plus separate publication record | External mirrors may not honor immutability |
| TM-025 | Figure detachment | Plot cannot be linked to trace and analysis | Figure manifest and evidence ledger | Visual framing choices still affect interpretation |
| TM-026 | Scientific execution disguised as a test | Runner called from unit-test harness or one-tick fixture | Capability classification and stage gate at scientific functions | A poorly classified new interface could bypass the gate |
| TM-027 | Policy objective hidden in code | Tie-breaks or weights encode unregistered values | Versioned objectives, constraints, and tie-break rules | Complex code review remains necessary |
| TM-028 | Institutional power hidden as physics | Priority/privacy/governance choice presented as EBU law | Separate institutional layer and claim status | Downstream communication may ignore labels |
| TM-029 | Secret/provenance conflict | Reproduction needs environment data containing credentials | Redacted value with presence/source and science-relevant hash | Some proprietary dependencies may remain irreproducible |
| TM-030 | Part-specific fork | A later book creates its own runner/state/receipt semantics | Core extension interface and conformance audit | A genuinely incompatible scientific model may require a future major version |
| TM-031 | Self-referential or metadata-sensitive hash | Hash field, storage path, timestamp, or host metadata enters its own scientific preimage | Named hash domains and exact projections excluding derived fields and non-scientific metadata | Canonical serializer defects remain possible until I-0 fixtures exist |
| TM-032 | Configuration contamination | Implementation hash, runtime condition, authorization, or execution ID is frozen as preregistered science | Separate immutable `ExperimentConfiguration` and `ExecutionBinding` | A binding can still accidentally introduce scientific drift without review |
| TM-033 | Embedded, recursive, or forged authority | Authorized object contains its own permission, authorization hashes its own proof, or validation trusts an unchecked issuer label | External `StageAuthorization`, separate exact-hash authenticity envelope, and scope/time/revocation/evidence validation | Concrete trust and revocation mechanism remains UQ-35 |
| TM-034 | Wrong-run authorization | Valid authority for one binding or execution identity is reused for another | Exact configuration/binding hashes, exact operation, and exact execution-identity match | Distributed single-use enforcement remains part of trust design |
| TM-035 | False deterministic mismatch or false equality | Wall-clock, host, run ID, storage metadata, initial policy memory, fault schedule, or scientific rows are misclassified in the replay target | Exact canonical scientific trace projection, complete replay-input list, qualified completion rule, and separate run envelope | Platform-dependent numerical semantics remain subject to domain policy |
| TM-036 | Phase-9 duplicate application | A delayed/transit registration reapplies a phase-8 physical effect | Cross-phase ownership record and phase-9 registration-only invariant | Incorrect effect identifiers can hide duplication |
| TM-037 | Circular publication manifest | Pre-publication manifest requires a receipt or destination that exists only after publication | Immutable `ExecutionResultManifest` followed by separate `PublicationRecord` | External publication systems may return incomplete evidence |
| TM-038 | Premature numeric freeze | Core implementation claims one precision/tolerance policy is valid for every future domain | Core substrate plus domain-owned numerical-policy interface | Domain policies still require separate scientific review |
| TM-039 | Hidden or mutable policy memory | A history-dependent policy reuses process-local state absent from configuration and trace | Immutable `PolicyMemoryState`, pinned initial memory, non-self-referential payload hash, and before/after trace rows | Third-party policy code may retain undeclared hidden state |
| TM-040 | Memory/physics conflation | Controller memory is inserted into `Z_k` or physical update ownership | Separate policy-memory type, module authority, and augmented hash pair | A domain may misclassify a genuinely physical controller component as informational |
| TM-041 | Torn policy decision | Proposal, next memory, and canonical decision row disagree, or memory advances twice | Atomic decision/next-memory/trace-row append and unique decision-coordinate ownership | Storage primitive remains UQ-26 |
| TM-042 | Fault-schedule laundering | An injected fault differs between replays or an undeclared failure is labelled prospective after observation | Accepted exact `FaultSchedule`, delivery-semantics hash, trace header, and no-retroactive-declaration rule | External faults outside the framework remain governance risk |
| TM-043 | Operational failure misreported as scientific nondeterminism | A host/storage interruption truncates one run and is compared as a full scientific trace, or its valid prefix is discarded | Completion-qualified equality, run-specific failure envelope, immutable longest valid prefix, and explicit completeness state | Ambiguous storage durability can remain unresolved |

## 17. Unresolved-question register

No item below is answered by this specification. Resolution requires the
named future stage and must not be inferred during implementation merely for
convenience.

| ID | Unresolved question | Needed before | Owning future authority |
|---|---|---|---|
| UQ-01 | What is the minimal yet sufficient physical and closed-loop state for each domain? | Scientific model acceptance | Part-specific analytical design |
| UQ-02 | Which canonical core numeric substrate and numerical-policy interface are required, while leaving each future domain's precision, tolerance, approximation, and cross-platform guarantees to its own accepted policy? | Core implementation acceptance | I-0 implementation plan plus later domain scientific review |
| UQ-03 | Which exact canonical serialization standard and version should be frozen? | First accepted framework configuration | Implementation stage |
| UQ-04 | Should `ScientificId` allocation be centralized, namespaced by study, or content-derived for selected objects? | Registry implementation | Implementation stage |
| UQ-05 | How are schema migrations proven not to alter accepted scientific meaning? | First schema major/minor migration | Separate migration protocol |
| UQ-06 | Which continuous-time or hybrid-time formulation can supersede the discrete event contract when needed? | Continuous-time studies | New analytical foundation |
| UQ-07 | How should simultaneous events be interpreted when physical order cannot be resolved by a discrete epoch? | Domains with sub-epoch interaction | Analytical design; possibly Dynamic Coordination revision |
| UQ-08 | How is uncertain or delayed coupling incorporated into the bridge dependency graph? | Dynamic grouping under imperfect knowledge | Sequential–Parallel Bridge revision or extension |
| UQ-09 | Which evidence proves that apparently disjoint simultaneous actions are separable? | Omitting a joint group in accepted config | Part VI preregistration |
| UQ-10 | Does any purpose-independent comparator exist for noncommuting actions? | Claiming one canonical interaction | Part VI research programme |
| UQ-11 | How are large admissible comparator sets covered without outcome-dependent search? | Many-action execution | Part VI preregistration |
| UQ-12 | When are child causal contributions identifiable in dynamic groups? | Publishing child causal values | Causal protocol |
| UQ-13 | Which settlement rules are acceptable when contributions are unidentified? | Institutional execution | Part IX institutional design |
| UQ-14 | What exact route, segment, distance, loss, delay, actor, and closure semantics will Part VII freeze? | Nonprovisional route science | Part VII analytical foundation |
| UQ-15 | How should multi-resource conversion, coproducts, and loss registries be governed? | Cross-resource scientific configurations | Domain foundations |
| UQ-16 | Which queue disciplines are admissible physically and institutionally? | Queue-policy preregistration | Parts VII–IX as applicable |
| UQ-17 | How are distributed reservation ledgers reconciled under communication failure? | Distributed capacity guarantees | Dynamic Coordination implementation/design |
| UQ-18 | How should pending delayed effects constrain a finite-horizon quote or settlement? | Multi-horizon settlement | Parts VII and IX |
| UQ-19 | When does provenance linkage justify causal attribution for a delayed effect? | Delayed causal claims | Causal protocol |
| UQ-20 | What natural-drive interface and submodels are required by Parts IV–VIII? | First dynamic scientific config | Part-specific design |
| UQ-21 | Which objective-vector comparison rule is appropriate for each study? | Preregistration | Study-specific analytical design |
| UQ-22 | How should privacy, autonomy, contestability, and institutional labor be represented without invented physical units? | Society-scale study | Parts VIII–IX institutional design |
| UQ-23 | Which pseudorandom generator, stream derivation, counter convention, and replay guarantee are required? | Stochastic implementation | Separate stochastic specification |
| UQ-24 | How should common random numbers and shared exogenous histories be assigned across arms? | Stochastic preregistration | Study-specific preregistration |
| UQ-25 | Which third-party libraries can meet deterministic arithmetic and provenance requirements? | Dependency lock acceptance | Implementation audit |
| UQ-26 | What durable storage primitive gives atomic physical phase commitment, atomic policy-decision/next-memory/trace-row append, epoch-wide ownership durability, and trace/state/memory consistency while preserving earlier confirmed evidence after failure? | Runner implementation | Operational implementation design |
| UQ-27 | Which publication store provides enforceable write-once semantics and a durable separate `PublicationRecord` without mutating the pre-publication manifest? | Publication implementation | Publication protocol |
| UQ-28 | Who may authorize corrections, and what classifications distinguish data, analysis, figure, and interpretation corrections? | Correction workflow activation | Governance/correction protocol |
| UQ-29 | What is the minimum canonical scientific trace and durable-prefix granularity that preserves physical and policy-memory reconstruction without unacceptable cost or privacy exposure, and which additional facts belong only in the run envelope? | Trace implementation acceptance | Implementation plus study governance |
| UQ-30 | How should secrets, proprietary dependencies, restricted measurements, and non-scientific storage provenance be represented in bindings, run envelopes, and manifests without entering scientific hash projections? | Restricted-data study | Security and governance protocol |
| UQ-31 | Which exact static fixtures are in scope for the first implementation validation without beginning a scientific study? | Validation plan | Separately authorized implementation validation design |
| UQ-32 | Which theorem-candidate proof obligations should be machine-checkable, and with what tooling? | Formal verification work | Part V/VIII proof programme |
| UQ-33 | How should framework plugins be certified to preserve core event and authority semantics? | First Part-specific plugin | Implementation conformance protocol |
| UQ-34 | When does a genuinely incompatible domain require framework v1.0 rather than an extension? | Proposed incompatible model | New specification authority |
| UQ-35 | Which concrete trust anchors, signatures or equivalent non-recursive authenticity envelope, issuer registry, delegation model, trusted clock, revocation mechanism, and single-use enforcement validate `StageAuthorization`? | Authorization-interface implementation | I-0 implementation plan and governance review |
| UQ-36 | Which runtime constraints belong in `ExecutionSemanticsPreimageV1` because they can affect science, and which are run-instance metadata excluded from deterministic replay? | First accepted execution binding | I-0 implementation plan plus implementation audit |
| UQ-37 | How should several asynchronous or interacting controllers be represented as one canonical composite `PolicyMemoryState`, with a frozen decision order and no hidden cross-controller memory? | Multi-controller closed-loop configuration | Part-specific analytical design plus framework extension review |
| UQ-38 | Which exact fault kinds, target coordinates, delivery acknowledgements, and terminal rules are admissible for scientific and inert durability fault schedules? | First fault-injection study | Separate fault-injection specification and applicable study preregistration |
| UQ-39 | How should sensitive policy-memory payloads be encrypted, access-controlled, retained, or disclosed while preserving content-hash verification, authorized replay, and evidence-ledger requirements? | Restricted-memory study | Security, privacy, and study-governance protocol |

## 18. Extension points for Parts IV–IX

Extensions SHALL register new types, models, metrics, and adapters against the
core interfaces. They SHALL reuse core identity, quantity, boundary, horizon,
state, event, trace, result, manifest, workflow, and publication contracts.

| Part | Allowed extension point | Required inherited foundation | Must not create |
|---|---|---|---|
| IV — outcome measurement | Measurement instruments, observation-age models, uncertainty sets, robust quote envelopes, outcome metrics | Core state/measurement separation and workflow stages | Gate-specific hidden runner, mutable metric, or post-result world tuning |
| V — homeostasis | Viable sets, natural drive, controller models, proof obligations, long-horizon metrics | Core dynamic state and information boundary | Empirical “forever” claim from simulation or silent state reduction |
| VI — sequential/parallel | Bridge adapter, comparator records, joint groups, group receipts, exact fixtures | Sequential–Parallel Bridge v0.2 unchanged | Alternative group EBU, unnamed comparator, or causal allocation by default |
| VII — across distance | Future route/segment/actor semantics, route receipts, cross-boundary settlement horizons | Part VI bridge plus a separately frozen Part VII foundation | Graph-distance law or route credit invented by the framework |
| VIII — dynamic coordination | Policies, schedules, provider placement, topology, capacity, resilience, pattern diagnostics | Dynamic Coordination v0.1 and future accepted revisions | Assumed waves, scaling, fractals, synchronization, or collective benefit |
| IX — economy | Quotes, guarantees, institutional residuals, access, reserves, appeals, privacy/governance records | Immutable physical and causal evidence from earlier layers | Money/EBU equivalence, physical law from policy choice, or overwritten residual |

### 18.1 Extension registration contract

Every extension SHALL provide:

- owning Part and scientific question;
- imported source hashes;
- new object types and registry entries;
- interfaces implemented and their classifications;
- state coordinates and boundary additions;
- policy-memory schema, initial state, transition ownership, and composite
  ordering when applicable;
- event-phase participation and update ownership;
- fault-schedule types and delivery coordinates when applicable;
- information inputs and outputs;
- invariants and failure states;
- exact static fixtures and proof obligations;
- artifact and provenance additions;
- compatibility with earlier accepted objects;
- explicit nonclaims and unresolved questions.

An extension that requires changing an imported definition or event phase is
not a plugin. It requires a prospectively authorized foundation/specification
revision.

## 19. Separately authorized implementation-stage proposal — original v0.1 sequence

The original v0.1 specification proposed I-0 followed by I-1–I-10. That
sequence is preserved below as historical design evidence. I-0 planning was
later completed in `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md`;
its current v0.2.1 authority/status section governs readiness. I-1 remains
blocked there by the unresolved PEP 517/stdlib-only packaging contradiction.
Any implementation still requires separate explicit authorization and would
not authorize preregistration, pre-execution audit, scientific execution,
interpretation, publication, or any Gate 1D-C action.

The proposed implementation sequence is:

### I-0 — Reconfirm authority and freeze an implementation plan

- verify clean tree, branch, local and remote heads, and applicable guidance;
- re-hash this specification and its three authoritative sources;
- resolve UQ-02 only for the canonical core numeric substrate and the interface
  that later domain-owned numerical policies must implement; explicitly leave
  future domain precision, tolerance, and approximation choices unfrozen;
- resolve UQ-03 and UQ-04 for canonicalization and identity;
- resolve UQ-35 by selecting the concrete authorization authenticity, trust,
  issuer-scope, clock, delegation, revocation, single-use mechanism, and
  non-recursive external authenticity-envelope format;
- resolve UQ-36 by freezing the execution-semantics versus run-metadata
  classification;
- freeze the base fault-schedule type boundary and leave study-specific fault
  kinds and terminal rules to UQ-38;
- freeze exact non-self-referential preimages for object content, physical
  state payload, policy-memory payload, augmented closed-loop replay state,
  execution semantics, canonical scientific trace, and artifact bytes;
- enumerate exact implementation files before editing;
- classify every planned interface as T0, T1, T2, or T3-capable;
- freeze a validation plan that cannot reach scientific execution.

Deliverable: an accepted implementation plan and file manifest. No code yet.

### I-1 — Implement identity, canonicalization, and immutable registries

- `ScientificId`, semantic versions, `ObjectRef`, and content hashes;
- canonical serializer, named hash domains, and non-self-referential object,
  physical-state-payload, policy-memory-payload, augmented-replay-state,
  execution-semantics, trace-payload, and artifact-byte hashing;
- explicit separation of object-content and scientific payloads from
  `RecordMetadata`;
- immutable registry storage and alias resolution;
- explicit resolution and failure envelopes;
- T0 canonical byte, hash-preimage exclusion, and metadata-invariance fixtures.

Exit criterion: byte-level canonicalization and reference integrity are
deterministic on the supported platforms.

### I-2 — Implement typed primitives and object envelopes

- dimensions, units, quantities, resource types, regions, boundaries, time,
  horizons, uncertainty, and statuses;
- the core numeric substrate and common domain numerical-policy interface,
  without selecting domain-owned precision or tolerance values;
- common immutable envelope and supersession relations;
- T0 dimensional, boundary, and lifecycle validation;
- no domain distortion or transition functions.

Exit criterion: invalid aggregation and implicit absence fail closed.

### I-3 — Implement declarative scientific records

- state and represented-state records;
- distortion and action contracts without scientific domain implementations;
- schedules, policies, providers, topology, commitments, reservations, queues,
  delays, measurements, quotes, receipts, ledgers, configurations, results,
  immutable `PolicyMemoryState` and policy-decision records, fault schedules,
  execution bindings, external stage authorizations and separate authenticity
  envelopes, canonical scientific traces and completeness states, run
  envelopes, pre-publication execution/result manifests, and post-publication
  records;
- acceptance transitions that freeze configuration and binding content
  immediately;
- append-only dummy ledgers and inert artifact storage.

Exit criterion: all v0.1 schemas can be represented and validated without
advancing model state.

### I-4 — Implement workflow authorization and information capabilities

- external stage authorizations, separate authenticity/evidence bundles, and
  interface classifications;
- authenticity, issuer/delegation scope, operation scope, temporal validity,
  revocation, predecessor-evidence, exact configuration/binding hash, and
  exact execution-identity validation;
- capability-limited policy views;
- availability-time, current-memory-only, and read-set enforcement;
- initial policy-memory applicability and exact-hash validation;
- anti-disguise guard at every state-advancing interface;
- T1 checks using inert fabricated records only.

Exit criterion: unauthorized protected operations, including state
advancement, are impossible through public or validation interfaces in the
reviewed threat model.

### I-5 — Implement the deterministic event kernel

- exact ten phase ordinals;
- total `EventKey` ordering;
- immutable transition proposals for phases 1, 2, 8, 9, and 10;
- atomic separately owned phase-4 policy-decision/next-memory/trace-row
  durability that cannot mutate physical state;
- epoch-wide cross-phase update-ownership validation;
- phase-9 registration/status contracts that reject duplicate phase-8
  effects;
- atomic phase-commit abstraction and typed partial-failure handling;
- base declared-fault delivery hooks at named model-event and durability
  coordinates, with undeclared interruptions kept run-specific;
- natural-drive hook fixed to phase 10;
- no scientific action transformations or accepted experiment worlds.

Exit criterion: inert T1 events demonstrate ordering, ownership conflict
rejection, and durability classification without scientific execution.

### I-6 — Implement the exact Bridge v0.2 adapter

- imported grouping rule and transitive closure;
- comparator types and undefined/nonserializable handling;
- group measurement, `N_G`, interaction, causal-status separation, and
  settlement closure interfaces;
- only after separate validation authorization, implement the frozen exact T2
  bridge fixtures; do not run trajectories or begin the deterministic
  parallel-testing programme.

Exit criterion: an independent conformance review finds no local redefinition
of the bridge.

### I-7 — Implement Dynamic Coordination records and deterministic mechanics

- provider topology and status transitions;
- capacity, admission, queue, reservation, shortfall, congestion, in-transit,
  delayed-effect, failure, rerouting-suffix, and natural-drive ownership;
- open-loop and closed-loop proposal interfaces;
- stateful policy before/after memory transitions and augmented replay-state
  construction;
- provisional route guards that fail on unfrozen Part VII semantics;
- exact T0/T1 checks and separately authorized T2 static fixtures only.

Exit criterion: the implementation matches the imported dynamic state and
event-order foundation, including no-double-application rules.

### I-8 — Implement provenance, result durability, recovery, and publication

- completion-qualified byte-identical canonical scientific trace payload
  contract, stateful-memory hashes, declared-fault replay inputs, immutable
  durable prefixes, and separate run-specific failure envelope;
- source/runtime/environment provenance bound at the correct scientific or
  run-specific layer;
- immutable pre-publication `ExecutionResultManifest`, summaries, figures, and
  evidence-ledger references;
- content-addressed write-once dummy publication creating a separate immutable
  `PublicationRecord` without mutating the manifest;
- recovery and correction records using inert artifacts;
- no real result publication.

Exit criterion: an inert artifact can be created, interrupted, classified,
recovered byte-identically where valid, published with a separate record, and
refused overwrite where bytes differ.

### I-9 — Conduct a separately authorized implementation audit

- inspect the complete implementation diff;
- verify dependency direction and absence of circular scientific authority;
- verify the configuration/binding/external-authorization split and every
  authorization-validation dimension;
- verify each named hash preimage is non-self-referential and unaffected by
  excluded storage/run/publication metadata;
- verify accepted stateful configurations pin initial memory and every policy
  decision atomically records before/after hashes without physical mutation;
- verify deterministic equality targets only normally completed canonical
  scientific payloads or equal-schedule declared-fault terminal payloads;
- verify undeclared interruptions preserve confirmed prefixes and remain
  run-specific rather than determinism failures;
- verify phase-wide update ownership and phase-8/phase-9 non-duplication;
- verify pre-publication manifest and post-publication record separation;
- map every invariant and threat to evidence or an explicit open item;
- run only the accepted T0, T1, and T2 validation plan;
- confirm no registered world, runner, trajectory, scientific policy loop, or
  Gate 1D-C function was reached;
- produce an implementation-validation report and immutable provenance.

Exit criterion: implementation fidelity is accepted. This still does not
authorize scientific execution.

### I-10 — Propose later domain and stochastic specifications

Only after deterministic implementation acceptance:

- propose, but do not assume, a Part VII route foundation and adapter;
- propose a stochastic engine specification resolving UQ-23 and UQ-24;
- propose a multi-controller composite-memory extension resolving UQ-37 where
  required;
- propose a separate fault-injection specification resolving UQ-38 before any
  such study;
- propose part-specific preregistrations in dependency order;
- retain analytical design, preregistration, implementation changes,
  pre-execution audit, scientific execution, interpretation, and publication
  as separate authorizations.

No I-1–I-10 implementation step in this proposal has begun. I-0 is preserved
through the later plan rather than treated as future work. The next possible
work is the separately authorized prospective packaging-plan amendment named
by that plan; implementation itself remains unperformed.

## 20. Document revision history

### 20.1 Original v0.1 specification — historical

The original v0.1 whole-file SHA-256 is
`4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38`.
It used the then-current books-structure hash
`1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558`
and remains immutable evidence in `foundation-v0.1.0`. Neither value is a
current implementation authority.

### 20.2 Revision v0.1.1 — current prospective amendment

Revision v0.1.1 adopts the books-structure hash
`4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c`
as current authority and adds only the K1–K6 scope boundary needed to prevent
future planning from silently entering I-1. It changes no scientific
definition, core semantic, closed implementation manifest, dependency,
backend, validation fixture, or stage authorization. Its exact whole-file
SHA-256 is recorded in the prospectively amended I-0 plan rather than inside
this file, which cannot self-record its current raw hash without changing it.
