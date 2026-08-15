# Unified Python Research Framework Specification

**Version:** 0.1.10
**Status:** Prospective complete I-3 mechanical authority with corrected implementation-path/substage ownership; accepted and implemented I-2 remains unchanged; I-3 is specification-ready and unimplemented; no framework implementation, scientific execution, Gate, publication, or release authority
**Date:** 2026-08-12
**Authority reconciliation date:** 2026-08-15
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
retained only as an original verification hash. It is not a current v0.1.2
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

#### 2.1.2 Current v0.1.10 prospective authority register

Revision v0.1.2 prospectively replaced only the active books-structure
authority pointer. Revision v0.1.3 preserved those imported scientific
authorities and added the prospective I-2 contracts in §21. Revision v0.1.4
preserved those authorities and corrected only the validation-case collision
recorded in §20.5. Revision v0.1.5 preserved those authorities and corrected
only the supersession coordinates and constructor-versus-validator authority
recorded in §20.6. Revision v0.1.6 preserves those authorities and corrects
only the I-2 predicate-observability defects recorded in §20.7. Revision
v0.1.7 preserves those authorities and corrects only the exact-conversion
source-unit authority defect recorded in §20.8. Revision v0.1.8 replaced the
active books-structure pointer, registers the conservation and boundary-
accounting foundation as current planning authority, and records accepted I-2
as unchanged implementation history. Revision v0.1.9 adopted the complete
prospective I-3 Markdown/mechanical/validation authority in §22, without
implementing it or changing I-2. Revision v0.1.10 corrects only the complete
implementation-path/substage ownership bijection. The v0.1.2
reconciliation began from repository `HEAD`
`c3965c87554911c526592ac9688d4c35f0c49516`, whose first-parent merge diff
changes only `EBU_FUTURE_BOOKS_STRUCTURE.md`. The current authority
set is:

| Source | Current version or role | Current required raw SHA-256 | Current authority used by v0.1.10 |
|---|---|---|---|
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | Current future-books architecture, including K1–K6, literature/originality, and conservation-accounting planning | `0c8eeb402b201e81e20c0167f5b66d93ccb9d6d847d1c4c145891e145c9ec26f` | Parts IV–IX ordering and future research dependencies, subject to the boundaries in §§2.1.4–2.1.6 |
| `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` | v0.1 conceptual and algebraic planning foundation | `b164b8079ebafbb86309f1c2a073c3467fc43356a719c95bd89227a1064e9d4a` | Three account levels, typed boundary-accounting interpretation, historical-model compatibility, and prospective I-3/I-5 planning limits in §2.1.6 |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | v0.2 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | Unchanged Part VI definitions, grouping, comparators, physical group measurement, causal limits, receipt closure, and batching |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | v0.1 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | Unchanged Part VIII dynamic state, seven-layer separation, deterministic event order, network evolution, objectives, uncertainty, and framework requirements |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md` | v1.0.1 normative human I-3 rendering | `b5e54fad02a232acc89b4d69613f93026dbd0a10d400b0751072475e32173fee` | Narrow prospective I-3 authority, later-stage ownership reconciliation, and exact implementation-path/substage ownership |
| `unified_python_research_framework_i3_contract.json` | v1.0.1 mechanical I-3 contract | `817513d43726cbb23a4f61a711700248724aa491dad654ad0c2c6ce703dc8c16` | Exact I-3 types, fields, validators, failures, projections, exports, imports, 23-path ownership bijection, stages, and nonclaims |
| `unified_python_research_framework_i3_validation_contract.json` | v1.0.0 validation contract | `0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0` | Exact prospective validation-corpus generation, ordering, effective inputs, coverage, collision rule, count, bytes, and digest |

The books-structure hash in this table is the only active books-structure
authority value for this specification revision, and the conservation-
foundation hash in this table is its only active value. The active I-1
packaging authorities and accepted I-2 implementation evidence remain frozen
without amendment; the v0.1.7 design-time locks retained in §21 are historical
inputs to that accepted implementation, not current planning-authority
pointers. Superseded values remain solely in explicitly historical records.
This prospective I-3 authority update changes no imported bridge or dynamic-
coordination semantic, framework object, interface, invariant, event phase,
accepted I-1/I-2 test classification, implementation byte, or current
implementation permission.

#### 2.1.3 Immutable signed foundation evidence

Both existing signed tags are immutable historical evidence and are not moved
or reinterpreted by this revision:

| Evidence | Exact identity | Historical meaning |
|---|---|---|
| Signed tag object | `foundation-v0.1.0` / `90646d3c7e1ff2201eab4739e894598b80782b79` | Original documentation/foundation milestone only |
| Tag target | `fa08920a56485962b368bfa032fa284f455413eb` | Unchanged commit named by the signed tag |
| Original specification bytes | `4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38` | Original v0.1 whole-file SHA-256; not a later specification hash |
| Original I-0 plan bytes | `a1cebfa63528e49d9bada3c6564c7d40616369a45afd97640ff937ae07389674` | Original plan whole-file SHA-256 at the milestone; not a hash of a later amendment |
| Books-structure bytes at the milestone | `1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558` | Original books-structure verification hash; historical only |
| Signed tag object | `foundation-v0.1.1` / `29060d72ce2fac10ab85e52330c1a375c1d5cb5b` | Reconciled documentation/foundation milestone only |
| Tag target | `fae76042746e55b9fe5ec5c62de0f47fbc5ccb47` | Unchanged commit named by the signed tag |
| Specification bytes at `foundation-v0.1.1` | `a52b0232595719afd554d842aefb16d6dba0e039ced75c4aed05b358964c6de1` | Historical v0.1.1 whole-file SHA-256 |
| I-0 plan bytes at `foundation-v0.1.1` | `d89fe92ac6cafd8990588e72d294bcf547cbb478d4b43b638a380e38116ba42e` | Historical v0.2.1 whole-file SHA-256 |
| Books-structure bytes at `foundation-v0.1.1` | `4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c` | Historical v0.1.1/v0.2.1 authority hash |

Revision v0.1.2 is later prospective documentation. It was not present at,
verified during, or incorporated into either signed foundation tag.

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

#### 2.1.5 Literature and originality extension boundary

The books-structure revision adds bibliography and citation policy, prior-art
and nearest-antecedent mapping, candidate-contribution boundaries, explicit
bibliography/endnote page reserves, and literature checkpoints before
manuscript generation. These are documentation and manuscript-governance
additions only. They change no imported Bridge definition, Dynamic
Coordination semantic, framework object, interface, invariant, event phase,
implementation manifest, packaging rule, scientific definition, Gate rule,
or execution permission.

In particular, the revision preserves the required distinction among the
measured joint physical transition, causal inference about contributions,
policy choice, and institutional settlement. A literature classification or
candidate-contribution label cannot convert one of those operations into
another or supply scientific evidence for it.

#### 2.1.6 Conservation and boundary-accounting extension boundary

The conservation foundation accepts three first-class levels of account:

1. **reduced represented-stock**;
2. **open control-volume**; and
3. **isolated boundary-complete**.

The first two remain fully supported scientific cases rather than incomplete
defaults awaiting conversion to the third. Existing D0, P1C, service,
Gate 1D-C, and other historical models remain unchanged reduced represented-
stock or open control-volume models under their existing declared boundaries.
They are not retroactively reclassified as isolated, boundary-complete
physical systems.

This reconciliation preserves every existing equation, algorithm, constant,
theorem, test, result, protocol, Gate rule, and interpretation boundary. It
also preserves accepted and implemented I-2 exactly: no I-2 type, callable,
field, validator, failure code, precedence rule, fixture, import edge, export,
API count, path, or implementation hash is changed or reinterpreted.

The prospective I-3 authority in §22 now defines optional declarative
boundary/conservation profiles in a dedicated future `conservation.py`
module. Reduced represented-stock and open control-volume accounts remain
first-class. An isolated boundary-complete profile requires explicit local
zero-exchange and boundary/carrier evidence declarations, but I-3 does not
establish their scientific truth. Historical configurations require no
profile and no migration. A separately authorized I-5 may later calculate and
compare residuals under the selected profile. Neither stage may impose a
universal zero-residual requirement or a hidden framework-wide numerical
tolerance.

Physical conservation, represented-stock closure, EBU accounting, causal
inference, policy, and institutional settlement remain distinct operations
and claim types. Section 22 plus its three named authority files closes exact
prospective I-3 types, callables, fields, validators, manifests, fixture
authority, projections, errors, imports, exports, and stage nonclaims. It
authorizes no implementation, accepted object, scientific use, executable
workflow, or domain numerical policy.

Detailed Bridge and Dynamic Coordination amendments remain separately
authorized and unstarted. This planning reconciliation makes no scientific,
experimental, empirical, novelty, or result claim.

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
| `object_content_payload` | `CanonicalBytes` | Unique immutable canonical ECJ-1 bytes for the complete hash-worthy scientific or operational payload governed by the named schema |
| `object_content_hash` | `ObjectContentHash` | Hash of the canonical object-content preimage defined in §4.3; never part of its own preimage |
| `lifecycle_status` | typed status | Draft, accepted, superseded, or other kind-specific registry state; excluded from the object-content preimage |
| `record_metadata_ref` | optional `RecordMetadataRef` | Storage and other non-content provenance metadata excluded from scientific hashes |

An `ObjectRef` SHALL contain `object_id`, `object_version`, and
`object_content_hash`. A logical identifier without version and hash is not
sufficient inside an accepted configuration, execution binding, or result.
Common-envelope `authority_refs` identify normative dependencies; they do not
grant workflow permission. An operation-granting `StageAuthorization` always
travels as an external input to the interface it authorizes.

`object_content_payload` stores bytes, not a decoded ECJ-1 tree. Its exact
runtime type is the already-public `CanonicalBytes` and exact immutable
`bytes`; `bytearray`, `memoryview`, mutable containers, subclasses, and every
other type are rejected without coercion. A logical payload is encoded once
before construction. The resulting bytes are the sole payload state retained
by the envelope. Each validation or hashing operation obtains and discards a
fresh temporary logical value through `parse_ecj1`; no mutable decoded value
is stored, cached, or returned as envelope state.

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

For an envelope, the `object_content_payload` term in
`ObjectContentPreimageV1` is the logical ECJ-1 value freshly parsed from the
stored `CanonicalBytes`. It is not the byte sequence projected as an ECJ-1
string, hexadecimal value, integer array, or nested JSON text. The parsed
logical value is passed to the unchanged I-1 `compute_object_content_hash`,
which performs the single canonical encoding required by this preimage. The
payload is never double-encoded.

Every later statement that an object's `object_content_payload` "contains"
fields or values refers to this freshly parsed logical ECJ-1 value. It does not
change the common-envelope storage type: the envelope retains only the unique
canonical bytes from which that logical value is reconstructed.

`object_content_hash` itself, lifecycle status, signatures, authorization
records, record-creation time, ingestion time, wall-clock time, host and
process metadata, storage location, database keys, cache metadata,
publication metadata, and presentation annotations are excluded from this
preimage. `object_content_payload` SHALL NOT contain the same object's
exact stored `object_content_hash` string as an object name, object value, or
array member at any recursive depth. I-2 makes no alias-resolution,
embedded-record-identity, indirect-cycle, or registry/object-graph-cycle
claim; those stronger checks require later registry authority.

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

The following are semantic record specifications, not JSON schemas and not
implementation classes. For I-3, the exact retained/deferred inventory,
runtime kinds, field order/types, projections, validators, failures, exports,
imports, and stage ownership are superseded narrowly by §22 and its contracts.
This semantic catalogue remains interpretive context and cannot restore a
name or behavior deferred by §22.

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
| DR-040 | `ACCEPTED` | Make every I-2 T0 predicate decidable only from exact declared argument values and treat refs as identities rather than implicit lookups | Prevents validator outcomes from depending on registries, hidden state, fixture knowledge, or construction history; stronger semantic claims are deferred |
| DR-041 | `ACCEPTED` | Require `convert_quantity_exact` to receive an explicit source `Unit` as well as quantity, target unit, and rule | Makes quantity/source and rule/source disagreements locally distinguishable while preserving opaque refs, exact arithmetic, and callable count |

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
| TM-044 | Predicate-by-reference overclaim | A T0 validator treats an opaque ref as proof of lifecycle, role, contents, completeness, disjointness, treatment adequacy, or an indirect graph cycle | Exact argument-only predicate contract, explicit role fields/pairs where locally decidable, and named deferred claims | Later registry/domain stages must establish the stronger semantics without weakening I-2 identity checks |
| TM-045 | Conversion authority inferred from an opaque ref | A quantity/source mismatch and a rule/source mismatch collapse to the same effective arguments, so failure code depends on fixture identity, literal value, or patch history | Explicit source-unit argument, role-position equality checks, unchanged rule validator, and opaque-renaming audit | Referenced unit/rule contents beyond declared identities remain outside I-2 and subject to the unchanged UQ-40 boundary |

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
| UQ-40 | Which accepted registry/domain evidence establishes policy and contract roles/lifecycle/content, region membership disjointness, global pending/effect completeness, treatment adequacy, true out-of-set violation, and indirect alias/object-graph cycle freedom? | Any claim stronger than I-2 declaration-shape and identity validation | I-4 registry design plus applicable domain analytical/governance authority |

Revision v0.1.7 does not resolve, narrow, or expand UQ-40. Exact equality at
the newly explicit source-unit argument is an I-2 identity check, not a claim
about the contents, lifecycle, role, or scientific adequacy of any referenced
unit or rule.

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
its current authority/status section governs its documentation locks.
Revision v0.2.1 recorded the then-unresolved PEP 517/stdlib-only packaging
contradiction. The existing packaging amendment and matching contract
prospectively resolved that contradiction within their narrow scope. This
reconciliation neither repeats nor redefines that solution. This
specification does not itself authorize integration, I-2, preregistration,
pre-execution audit, scientific execution, interpretation, release,
publication, or any Gate 1D-C action.

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
Exact quantity conversion additionally fails closed unless the supplied
quantity, explicit source unit, explicit target unit, and supplied conversion
rule provide every locally observable identity and dimension witness required
by §21.

### I-3 — Implement declarative scientific records

- implement only the exact 69 immutable declarative types and 23 supplied-
  value T0 validators in §22 and the I-3 contract;
- implement the optional declaration-only conservation profile without
  residual calculation;
- preserve the accepted 127-entry root prefix and append the exact 92-name
  I-3 suffix;
- reconstruct and validate the exact 544-vector static fixture;
- perform no authorization, acceptance, state mutation, scientific callback,
  route/delay behavior, trace/durability behavior, finalization, publication,
  or correction.

Exit criterion: all retained I-3 declarations form, project, hash, and validate
under the closed corpus and audit, every deferred name remains unreachable,
the direct import graph is acyclic, and every accepted I-1/I-2 byte and API
prefix remains unchanged.

### I-4 — Implement workflow authorization and information capabilities

- external stage authorizations, separate authenticity/evidence bundles,
  real configuration/binding accepted-status transitions, and
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

This original sequence records stage boundaries rather than current branch
state. I-0 is preserved through the later plan rather than treated as future
work. Actual implementation and integration status comes from reviewed Git
history and retained stage evidence, not from this specification. I-2 was
subsequently accepted exactly on feature commit
`351417c39fa26b9045e7c162a9897a7c38e4e1d1` and integrated without amendment
by merge commit `ede89d8af6b89da491e03c352efcf1868a913f6f`. Revision v0.1.10
does not reopen that accepted implementation. It grants only the prospective
I-3 authority in §22 and grants no implementation, I-5, framework-alpha,
scientific-execution, Gate, publication, or release authority.

## 20. Document revision history

### 20.1 Original v0.1 specification — historical

The original v0.1 whole-file SHA-256 is
`4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38`.
It used the then-current books-structure hash
`1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558`
and remains immutable evidence in `foundation-v0.1.0`. Neither value is a
current implementation authority.

### 20.2 Revision v0.1.1 — historical prospective amendment

Revision v0.1.1 adopts the books-structure hash
`4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c`
as its then-current authority and adds only the K1–K6 scope boundary needed to prevent
future planning from silently entering I-1. It changes no scientific
definition, core semantic, closed implementation manifest, dependency,
backend, validation fixture, or stage authorization. Its historical exact
whole-file SHA-256 is
`a52b0232595719afd554d842aefb16d6dba0e039ced75c4aed05b358964c6de1`.

### 20.3 Revision v0.1.2 — historical prospective reconciliation

Revision v0.1.2 adopts the literature-extended books structure through the
single active authority lock in §2.1.2. The update adds bibliography and
citation policy, prior-art and nearest-antecedent mapping,
candidate-contribution boundaries, bibliography/endnote page reserves, and
literature checkpoints before manuscript generation.

It changes no imported Bridge definition, Dynamic Coordination semantic,
framework object, interface, invariant, event phase, implementation manifest,
packaging rule, scientific definition, Gate rule, execution permission, or
the distinction among physical measurement, causal inference, policy, and
settlement. It repeats no packaging solution and grants no integration, I-2,
framework-alpha, scientific-execution, publication, or release authority. Its
exact whole-file SHA-256 is recorded in the prospectively reconciled I-0 plan
rather than inside this file, which cannot self-record its current raw hash
without changing it.

### 20.4 Revision v0.1.3 — historical prospective I-2 authority amendment

Revision v0.1.3 introduced the prospective Framework I-2 authority in §21. The
v0.1.2 whole-file SHA-256
`32bc5b9d1983b3b46242d0ccc9323636847d1c8cfeea641f64796f0665916f69`
is immutable historical evidence. Revision v0.1.3 changes no I-1 bytes,
imported scientific definition, Gate record, result, package, or accepted
milestone. Its exact whole-file SHA-256 is
`44ae0d5587b24bbca32acda822cddfdc7db76795f81337cd8fc7951bf2946193`.

### 20.5 Revision v0.1.4 — historical prospective I-2 validation correction

Revision v0.1.4 corrects only the Block-5 collision between validation cases
16 and 34. It makes case 34 an explicit typed-applicability contradiction,
keeps case 16 as structural omission, and states explicitly that validation
uses only the resulting declaration rather than patch history. It changes no
other case, expected outcome, count, API, dependency, scientific definition,
Gate record, package, I-1 byte, or accepted milestone. Its raw SHA-256 is
`25250235e5cb2b61ab0ec6c330245766084cf7b2528d323c70018a99dd1c8380`.

### 20.6 Revision v0.1.5 — historical prospective I-2 authority correction

Revision v0.1.5 replaces the supersession model's singular kind and schema
coordinates with independently observable predecessor and successor
coordinates and freezes an exact constructor-versus-validator responsibility
contract. It also makes the supersession authorization rejection an explicit
typed-not-applicable candidate at the validator boundary. It preserves every
fixture ID, case name, predicate label, expected outcome and code, block and
outcome count, public API count, dependency, scientific definition, Gate
record, package, I-1 byte, and accepted milestone. Its raw SHA-256 is recorded
in historical implementation-plan v0.2.5. Its exact whole-file SHA-256 is
`9486619dd0e5632e0efadfe1353cbf71923b8ba789923cac790797259d756928`.

### 20.7 Revision v0.1.6 — historical prospective I-2 predicate-observability correction

Revision v0.1.6 corrects all eight known I-2 predicate-observability defects:
numerical-policy identity and ownership, exact-comparison tolerance,
standalone conversion context, declared region parent links, boundary
cross-effect treatment, horizon pending due declarations, out-of-set
violated-contract role, and direct envelope hash occurrence. It preserves
scientific meaning, public type and callable counts, dependencies, Gate
state, I-1 bytes, and accepted milestones. Its raw SHA-256 is recorded in
historical implementation-plan v0.2.6. Its exact whole-file SHA-256 is
`884767698f26ca75b59ab51d3d95a06e7f2996ae7071145b2f5564baed6787d2`.

### 20.8 Revision v0.1.7 — historical prospective I-2 source-unit authority correction

Revision v0.1.7 adds an explicit supplied source `Unit` to
`convert_quantity_exact` so quantity/source disagreement and
rule/source disagreement have different locally observable argument
witnesses. It changes only that callable's argument structure, the ten
conversion-vector input recipes `i2-0149` through `i2-0158`, their adapter
instructions, and dependent prospective authority text. It preserves every
vector ID, name, expected outcome and code, block/outcome count, public type
and callable count, export, path, dependency, scientific definition, UQ-40
deferral, Gate record, package, I-1 byte, and accepted milestone. Its raw
SHA-256 is
`01f7392459af3eaccbd6966b1504fa1206997722677415d080b0b6883d8081ca`,
also recorded in implementation-plan v0.2.7. That value is historical and is
not the current specification hash.

### 20.9 Revision v0.1.8 — historical prospective conservation-authority reconciliation

Revision v0.1.8 adopts the conservation-extended books structure and the
conservation and boundary-accounting foundation through the active hashes in
§2.1.2. It records the reduced represented-stock, open control-volume, and
isolated boundary-complete account levels; preserves reduced/open models as
first-class cases; and records optional future I-3 profile and I-5 profile-
specific residual responsibilities under separate prospective authority.

It changes no equation, algorithm, constant, theorem, test, result, protocol,
Gate rule, interpretation boundary, I-2 inventory, failure code, precedence,
fixture, import graph, API, path, implementation byte, or implementation
hash. It creates no implementation authority, universal zero-residual rule,
hidden numerical tolerance, Bridge or Dynamic Coordination amendment, or
scientific claim. Its exact whole-file SHA-256 is recorded only in the
prospectively reconciled implementation plan; this file does not contain its
own current hash.

### 20.10 Revision v0.1.9 — historical prospective I-3 authority closure

Revision v0.1.9 adopts
`UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md` v1.0.0,
`unified_python_research_framework_i3_contract.json` v1.0.0, and
`unified_python_research_framework_i3_validation_contract.json` v1.0.0 as the
narrow complete prospective authority for I-3. Section 22 records their
precedence and closed counts.

The revision resolved the old I-3/I-4/I-5/I-7/I-8 ownership contradictions,
adds optional conservation declaration authority, preserves the accepted I-2
API/helper name and bytes, and authorizes no implementation or scientific
execution. The exact v0.1.8 whole-file hash remains historical in the active
plan. Its exact whole-file SHA-256 is
`3eb023e4a729fe5205f4edf476d1347cc2584a99467648ce552c98954bd976e4`.

### 20.11 Revision v0.1.10 — current prospective I-3 path-ownership correction

Revision v0.1.10 adopts amendment v1.0.1 and mechanical contract v1.0.1 to
assign every frozen I-3 implementation path to exactly one of I-3A–I-3E. It
preserves validation contract v1.0.0 byte-identically and changes only
implementation-path/substage ownership. It changes no public type, callable,
field, enum, tagged union, signature, projection, hash domain, failure code,
ordinal, predicate, precedence, envelope, failure ID, vector, corpus count,
corpus byte, corpus hash, import edge, export, accepted I-1/I-2 path or
semantic, scientific definition, equation, model, result, protocol, Gate
state, interpretation, or execution permission. This file does not contain
its own current v0.1.10 whole-file hash; the plan records that hash after
these bytes are final.

## 21. Normative prospective Framework I-2 amendment

This section is retained as the complete normative design authority that was
implemented and accepted at
`351417c39fa26b9045e7c162a9897a7c38e4e1d1` and integrated at
`ede89d8af6b89da491e03c352efcf1868a913f6f`. Its v0.1.7 source locks and
future-tense implementation instructions are historical acceptance inputs,
not active current-authority pointers. Revision v0.1.10 changes none of
its inventories, predicates, fixtures, precedence, API, dependencies,
implementation paths, or hashes. Its separate I-3 authority exists only in
§22 and supplies no authority for I-5.

### 21.1 Authority, precedence, and authorization boundary

This section freezes the complete I-2 design needed to implement common
failures, exact core numbers, typed primitives, immutable envelopes, and pure
lifecycle validation in a later separately authorized task. Within that
narrow scope it supersedes incomplete or provisional I-2 details in earlier
sections. It does not supersede ECJ-1, any I-1 hash preimage, identity or
registry semantics, the I-1 packaging amendment/contract, imported scientific
foundations, or later-stage contracts. A conflict outside this scope fails
closed.

The prospective I-2 input locks are:

| Source or accepted evidence | Exact identity |
|---|---|
| Future-books structure | raw SHA-256 `120496aa0d304561e16b3556bbbd5300c651a3082a297fd21f6bad6034746255` |
| Sequential–Parallel Bridge v0.2 | raw SHA-256 `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` |
| Dynamic Coordination Foundation v0.1 | raw SHA-256 `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` |
| Specification v0.1.2 | historical raw SHA-256 `32bc5b9d1983b3b46242d0ccc9323636847d1c8cfeea641f64796f0665916f69` |
| Implementation plan v0.2.2 | historical raw SHA-256 `3422a0887b82637ce323de7015869770ffa59408cb11907f7266ed0e95a22a9c` |
| I-1 packaging amendment v1.1.1 | raw SHA-256 `a27aedf955c1e7bbf7039efc905951f516e070a2f36dc24b23c72d75f6a2f448` |
| I-1 packaging contract v1.1.1 | raw SHA-256 `edf2bd33361e7b2b2e083a10535c87e1e1cbbd36d21c2a3f3004f12b1743c351` |
| Accepted combined I-1 raw-hash/path/blob manifest | SHA-256 `f7b1b7abc9a71b090320b8dc468d57e3a7e39f4f2a045b7a5946a4174882fee8` |

The last row is historical audit corroboration, not an I-2 semantic input.
Commit `ed75790b20c7d6b86cedc4d9dbeb269f32cca9ea` introduced exactly 22 I-1
implementation paths. The complete feature range from
`fae76042746e55b9fe5ec5c62de0f47fbc5ccb47` through `ed75790...` contains
those 22 paths plus the packaging amendment and mechanical contract, hence 24
paths total. The original serialization recipe that produced the aggregate
digest is not committed. The historical digest is preserved but is not
independently reproducible and is neither recreated nor redefined here.
Current integrity is checked directly from Git path/blob identities, raw
hashes, and byte sizes.

The signed `foundation-v0.1.2` tag remains immutable: tag object
`63a3f71401e1cc91e85cdff89dbd4d8d38fcbd57`, peeled target
`38aae5e8c59d0bced598f2918f76dbee6df7481c`, and signing-key fingerprint
`SHA256:PmHC6U5rPJ+Jv7sCyjyF2UYLM6wgE8+iG5T6eGwHFCQ`. These are evidence, not
I-2 implementation authority.

At the v0.1.7 design freeze this amendment authorized no Python edit, test,
build, installation, acceptance mutation, scientific operation, Gate
operation, commit, push, release, or publication, and I-2 remained
unimplemented. The later accepted implementation and integration commits
named above satisfy that historical stage without altering this contract.
Revision v0.1.10 authorizes no change to the accepted I-2 implementation and
no implementation stage. Its prospective I-3 design authority is disjoint
from this implemented I-2 contract.

### 21.2 Common failure architecture

#### 21.2.1 Closed failure types

`errors.py` remains the sole owner of machine failure codes and the common
failure envelope. Module-local failure enums, application-defined subclasses
with new code domains, and free-form machine failure strings are forbidden.
Human prose is allowed only in `human_summary` and cannot affect failure
classification or permission.

The exact public supporting types are immutable `dataclass(frozen=True,
slots=True)` records unless stated as `StrEnum`:

| Type | Exact fields or values |
|---|---|
| `Applicability` | `StrEnum`: `APPLICABLE`, `NOT_APPLICABLE` |
| `FailureId` | one `value: str`, exactly `ebu:failure:core:sha256-` plus 64 lowercase hexadecimal digits |
| `FailureStage` | `StrEnum`: `I-1`, `I-2`, `I-3`, `I-4`, `I-5`, `I-6`, `I-7`, `I-8`, `I-9`, `ANALYTICAL_DESIGN`, `PREREGISTRATION`, `IMPLEMENTATION`, `STATIC_AND_SYNTHETIC_VALIDATION`, `PRE_EXECUTION_AUDIT`, `AUTHORIZED_SCIENTIFIC_EXECUTION`, `INTERPRETATION`, `PUBLICATION`, `RECOVERY`, `CORRECTION` |
| `FailureInterfaceRef` | `module: str`, `qualname: str`, `interface_version: str`; each is nonempty ASCII, contains no control/whitespace, and `interface_version` is `MAJOR.MINOR.PATCH` |
| `FailureObjectRef` | `object_id: str`, `object_version: str`, `object_content_hash: str`; each string must satisfy the corresponding `ScientificId`, `SemanticVersion`, or `ObjectContentHash` lexical grammar without importing `identity.py` |
| `FailureEventKey` | `epoch: int`, `phase_ordinal: int`, `declared_priority: int`, `group_or_scope_id: str`, `event_kind: str`, `primary_object_id: str`, `local_sequence: int`; booleans are rejected as integers, phase is `1..10`, and every other integer is nonnegative. `group_or_scope_id` and `primary_object_id` each match the exact `ScientificId` lexical grammar below; `event_kind` matches the exact one-segment grammar below. |
| `FailureEvidenceRef` | `evidence_kind: str` in `OBJECT`, `ARTIFACT`, `RAW_SOURCE`, `TRACE_PREFIX`, `AUTHORIZATION`, `OPERATIONAL_LOG`; `digest: str` is exactly `sha256-raw:` plus 64 lowercase hex digits for `RAW_SOURCE` and exactly `sha256:` plus 64 lowercase hex digits for every other kind; `locator: str | Applicability`, where `NOT_APPLICABLE` is the only non-string value and locator text is nonempty canonical UTF-8 without controls |
| `CanonicalTraceState` | fields `applicability: Applicability`, `completeness: str | Applicability`, `confirmed_row_count: int | Applicability`, `durable_prefix_ref: FailureEvidenceRef | Applicability`; the applicable completeness domain is exactly `COMPLETE`, `DECLARED_FAULT_TERMINAL`, `PARTIAL_DURABLE_PREFIX`, `NO_DURABLE_TRACE`, `UNRESOLVED_DURABILITY` |
| `ScientificStatusEffect` | `StrEnum`: `NONE`, `UNSTARTED_PRESERVED`, `SCIENTIFIC_STATE_UNCHANGED`, `SCIENTIFIC_STATE_ADVANCED`, `SCIENTIFIC_STATUS_FAILED`, `SCIENTIFIC_STATUS_PARTIAL`, `SCIENTIFIC_STATUS_UNRESOLVED` |

The typed pre-trace value is exactly:

```text
CanonicalTraceState(
    applicability=NOT_APPLICABLE,
    completeness=NOT_APPLICABLE,
    confirmed_row_count=NOT_APPLICABLE,
    durable_prefix_ref=NOT_APPLICABLE
)
```

No other combination with `applicability=NOT_APPLICABLE` is valid. When
applicable, `confirmed_row_count` is a nonnegative exact `int`; a durable
prefix reference is required exactly for `PARTIAL_DURABLE_PREFIX`, optional
only as typed `NOT_APPLICABLE` for the other applicable states, and must have
kind `TRACE_PREFIX` when present.

For `FailureEventKey`, the exact full-string ASCII grammars are:

```text
SCIENTIFIC_ID := "ebu:" SEGMENT ":" SEGMENT ":" SEGMENT
SEGMENT       := [a-z0-9][a-z0-9._-]*
EVENT_KIND    := [a-z0-9][a-z0-9._-]*
```

`group_or_scope_id` and `primary_object_id` match `SCIENTIFIC_ID`;
`event_kind` matches `EVENT_KIND`. Empty strings, uppercase ASCII,
whitespace, controls, extra or missing colon-delimited fields, and non-ASCII
characters are rejected. `errors.py` reproduces only these lexical checks so
it can remain standard-library-only; it does not import `identity.py`.
Invalid group/scope or primary-object identifiers fail
`SCIENTIFIC_ID_INVALID`; an invalid event kind fails `STABLE_KEY_INVALID`.

`FailureEnvelope` has exactly these fields, in this declaration and canonical
projection order:

| Field | Exact Python type | Construction rule |
|---|---|---|
| `failure_id` | `FailureId` | Derived by §21.2.2; caller cannot supply a conflicting value |
| `failure_ordinal` | `int` | Exact nonnegative integer; boolean rejected; default `0` only for one fail-fast boundary invocation |
| `failure_code` | `FailureCode` | Exact shared enum member |
| `stage` | `FailureStage` | Resolved explicitly under §21.2.3 |
| `interface_ref` | `FailureInterfaceRef | Applicability` | Exact ref or typed `NOT_APPLICABLE` |
| `object_refs` | `tuple[FailureObjectRef, ...]` | Immutable, duplicate-free, lexicographically ordered by the three fields |
| `event_key` | `FailureEventKey | Applicability` | Exact key or typed `NOT_APPLICABLE` |
| `state_advance` | `StateAdvance` | Exact enum; default `NONE` |
| `policy_memory_advance` | `PolicyMemoryAdvance` | Exact enum; default `NONE` |
| `durability_state` | `DurabilityState` | Exact enum; pre-durability default `NOT_APPLICABLE` |
| `canonical_trace_state` | `CanonicalTraceState` | Exact typed pre-trace value until trace handling applies |
| `scientific_status_effect` | `ScientificStatusEffect` | Default `NONE`; never inferred from summary text |
| `retry_class` | `RetryClass` | Default `NOT_APPLICABLE`; protected operations must override explicitly |
| `evidence_refs` | `tuple[FailureEvidenceRef, ...]` | Immutable, duplicate-free, ordered by `(evidence_kind,digest,locator)` |
| `human_summary` | `str` | Nonempty NFC Unicode 15.0 text without controls other than LF; non-authoritative |

`None`, `Any`, an unconstrained machine string, a dictionary, or an omitted
conditional value is invalid for every field. Empty `object_refs` and
`evidence_refs` mean an exactly empty collection, not an implicit absent
value.

The canonical projection is an ECJ-1 object named
`FailureEnvelopeProjectionV1` containing `schema_id` equal to
`ebu.failure-envelope/1` followed by the exact fields above. Records project
to ECJ-1 objects using their field names; enums project to their values;
tuples project to ordered arrays. The projection excludes exception class,
Python traceback and frame objects, wall/monotonic time, PID/thread/host,
memory addresses, storage/cache paths, environment, presentation metadata,
and any later record that refers to the envelope. Those facts may be separate
evidence references but cannot silently enter the canonical projection or the
failure identity.

The exact static `FailureEventKey` basis is assigned directly to
`tests/framework/test_primitives_envelopes.py`; it does not enter the JSON
fixture because no unrelated projection category is added. The four cases,
in order, have no implementation-selected value:

| Case name | Exact constructor arguments after the case name | Expected |
|---|---|---|
| `failure-event-key-valid` | `(0,1,0,"ebu:scope:validation:s0","phase.start","ebu:object:validation:o0",0)` | exact successful construction and field equality |
| `failure-event-key-invalid-group-or-scope-id` | `(0,1,0,"ebu:scope:Validation:s0","phase.start","ebu:object:validation:o0",0)` | `SCIENTIFIC_ID_INVALID` |
| `failure-event-key-invalid-event-kind` | `(0,1,0,"ebu:scope:validation:s0","Phase.Start","ebu:object:validation:o0",0)` | `STABLE_KEY_INVALID` |
| `failure-event-key-invalid-primary-object-id` | `(0,1,0,"ebu:scope:validation:s0","phase.start","ebu:object:validation",0)` | `SCIENTIFIC_ID_INVALID` |

The constructor argument order is the `FailureEventKey` field order. Each
failure is stage I-2 at
`ebu_framework.errors.FailureEventKey/1.0.0`, with empty object refs,
not-applicable event coordinate, and ordinal zero. These are exact static
test values; alternatives are not conforming.

#### 21.2.2 Stable, non-recursive `failure_id`

`failure_id` is the stable identity of a failure occurrence coordinate. It is
not random, sequential, time-derived, or content-addressed from its enclosing
envelope. Define `FRAME(x) = UINT64_BE(len(UTF8(x))) || UTF8(x)` and
`COUNT(n) = UINT64_BE(n)`. `FailureIdPreimageV1` is the exact byte
concatenation:

```text
FRAME("ebu.failure-id.v1")
|| FRAME(failure_code.value)
|| FRAME(stage.value)
|| FRAME("APPLICABLE" if interface_ref is present else "NOT_APPLICABLE")
|| [FRAME(module) || FRAME(qualname) || FRAME(interface_version), if applicable]
|| COUNT(len(object_refs))
|| for each ordered object_ref:
       FRAME(object_id) || FRAME(object_version) || FRAME(object_content_hash)
|| FRAME("APPLICABLE" if event_key is present else "NOT_APPLICABLE")
|| [FRAME(decimal(epoch)) || FRAME(decimal(phase_ordinal))
    || FRAME(decimal(declared_priority)) || FRAME(group_or_scope_id)
    || FRAME(event_kind) || FRAME(primary_object_id)
    || FRAME(decimal(local_sequence)), if applicable]
|| FRAME(decimal(failure_ordinal))
```

Decimal integers use minimal unsigned ASCII. The digest is raw SHA-256 of
these bytes and the ID is
`ebu:failure:core:sha256-<lowercase-full-64-hex>`. `failure_id`, summary,
advance/durability/trace classifications, evidence, metadata, and exception
details are excluded from the preimage. Thus later evidence can describe the
same occurrence without recursive or unstable identity. A boundary that may
emit more than one failure at the same interface/object/event coordinate must
assign prospective monotonically increasing ordinals in its deterministic
validation order; reuse of one coordinate/ordinal for different codes is
invalid.

#### 21.2.3 Construction, legacy preservation, and import-cycle rule

`FrameworkError` remains an internal `ValueError` carrying `.envelope`, and
its string remains exactly `"<FAILURE_CODE>: <human_summary>"`. `_fail`
remains private. New I-2 code must call `_fail` with an explicit
`stage=FailureStage.I2` and exact `interface_ref`; it may use ordinal zero only
because every I-2 public boundary is fail-fast and emits at most one failure.

The private constructor boundary is exactly:

```text
_fail(
    code: FailureCode,
    summary: str,
    *,
    stage: FailureStage | Applicability = NOT_APPLICABLE,
    interface_ref: FailureInterfaceRef | Applicability = NOT_APPLICABLE,
    object_refs: tuple[FailureObjectRef, ...] = (),
    event_key: FailureEventKey | Applicability = NOT_APPLICABLE,
    failure_ordinal: int = 0,
    state_advance: StateAdvance = NONE,
    policy_memory_advance: PolicyMemoryAdvance = NONE,
    durability_state: DurabilityState = NOT_APPLICABLE,
    canonical_trace_state: CanonicalTraceState = PRE_TRACE_NOT_APPLICABLE,
    scientific_status_effect: ScientificStatusEffect = NONE,
    retry_class: RetryClass = NOT_APPLICABLE,
    evidence_refs: tuple[FailureEvidenceRef, ...] = ()
) -> NoReturn
```

`FrameworkError` receives the same arguments and constructs exactly one
envelope. A caller never supplies `failure_id`; it is computed after all
identity-coordinate fields validate. The `stage=NOT_APPLICABLE` default is an
internal compatibility sentinel, not a valid stored stage, and is resolved
only by the four-module legacy rule below. Every other default above is the
typed value shown; there is no wall time, randomness, process state, implicit
lookup, or mutable counter.

The complete accepted I-1 audit found 95 `_fail` calls: 23 in `canonical.py`,
14 in `hashing.py`, 13 in `identity.py`, and 45 in `registry.py`. Every call
uses exactly two positional arguments and no keyword. The only direct
`FrameworkError` construction is the one inside `_fail`; no I-1 test directly
constructs `FailureEnvelope` or `FrameworkError` or depends on the old
untyped default fields.

Therefore I-2 selects the backward-compatible outcome. `errors.py` contains a
closed legacy-source map for exactly
`ebu_framework.canonical`, `ebu_framework.hashing`,
`ebu_framework.identity`, and `ebu_framework.registry`. An omitted stage is
accepted only when the immediate caller module is in that map, and resolves
to `FailureStage.I1`; interface is the typed `NOT_APPLICABLE`, ordinal is
zero, and every other field receives the typed deterministic pre-trace
defaults above. Any omitted stage from `numeric`, `envelopes`, `primitives`,
or a later module fails as an internal contract error and cannot construct a
mislabelled envelope. This preserves every existing I-1 code, summary,
exception string, and fail-fast meaning without editing an I-1 caller while
preventing a universal `"I-1"` default for I-2.

`errors.py` imports only the standard library. It performs its own closed
lexical checks and binary failure-ID framing; it must not import `canonical`,
`identity`, `hashing`, `registry`, `numeric`, `envelopes`, or `primitives`.
The other modules may import `errors`; no reverse edge is allowed.

#### 21.2.4 I-2 failure codes, meanings, and precedence

All 29 existing I-1 members and meanings are retained unchanged. I-2 adds
exactly these 24 members; no additional code is required:

| Code | Exact meaning |
|---|---|
| `CORE_NUMBER_INVALID` | A core-number constructor or operation received the wrong exact Python type, arity, tag, lexical form, denominator, or other structural invariant not covered by the more specific nonfinite code |
| `NONFINITE_NUMBER_FORBIDDEN` | A syntactically valid binary64 bit pattern has an all-ones exponent, or another canonical numeric input explicitly represents NaN or infinity |
| `DIVISION_BY_ZERO` | A valid divisor is mathematical zero, including either binary64 signed-zero bit pattern before policy dispatch |
| `NUMERICAL_OPERATION_UNSUPPORTED` | The requested operation is outside `NumericalOperation` or the exact core matrix marks it unsupported rather than policy-governed |
| `NUMERICAL_POLICY_REQUIRED` | The matrix permits the operation only under a separately accepted domain policy, but none is supplied; in I-2 this always refuses because no policy can be accepted |
| `NUMERICAL_POLICY_INCOMPLETE` | A supplied policy declaration lacks or contradicts a condition required by its declared operation/variant applicability |
| `ERROR_BOUND_INVALID` | An `ErrorBound` violates its kind-specific exact bounds, unit applicability, structural completeness, nonnegativity, or ordering relation after the higher-precedence absence, mixed-variant, and required-policy checks; it also covers use of an incomplete bound as the bound of a complete result |
| `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` | Operands have different variants or a result would require an unrequested cross-variant conversion |
| `DIMENSION_MISMATCH` | Dimension refs or exact basis-exponent vectors differ where equality is required |
| `UNIT_MISMATCH` | Unit refs differ and no exact, direction-valid conversion rule is explicitly supplied |
| `QUANTITY_TYPE_MISMATCH` | Resource/service applicability or exact type refs are incompatible |
| `REGION_MISMATCH` | Region refs differ and no explicit valid common-parent aggregation is supplied |
| `TIME_BASIS_MISMATCH` | Rate/non-rate applicability, time-basis refs, or duration bases are incompatible |
| `SIGN_CONVENTION_MISMATCH` | Sign-convention applicability or exact refs differ |
| `BOUNDARY_MISMATCH` | Mandatory boundary refs differ and no explicit valid common-parent aggregation is supplied |
| `INVALID_AGGREGATION` | An aggregation is undeclared, uses an invalid parent/membership relation, duplicates a child, or would require weighting/scalarization not supplied by an accepted rule |
| `CONVERSION_RULE_MISMATCH` | Conversion direction, source/target, dimension, factor/offset representation, or composition chain does not match the quantities |
| `IMPLICIT_ABSENCE_FORBIDDEN` | A required or conditionally applicable coordinate is omitted, `None`, empty, zero, or otherwise lacks its typed applicability marker |
| `RESOLUTION_STATE_INVALID` | A resolution/completeness record has an invalid state/payload relation, including completed-and-missing data represented as pending or unresolved |
| `CLOCK_MISMATCH` | Clock refs differ where one clock is required, or an instant/duration/epoch is applied to the wrong clock |
| `HORIZON_INVALID` | Start/terminal ordering, endpoint inclusion, completion rule, or post-terminal-effect treatment is absent or contradictory |
| `UNCERTAINTY_RECORD_INVALID` | An uncertainty record violates its kind-specific required/forbidden fields, units, provenance, or bound order |
| `LIFECYCLE_TRANSITION_INVALID` | A proposed lifecycle edge is not in the closed graph or violates immutable-source predicates |
| `SUPERSESSION_INVALID` | A supersession relation changes logical identity/schema, does not increase version, repeats content, branches/cycles ancestry, or otherwise fails §21.5.7 |

Input construction and strict ECJ-1/I-1 validation happen first; an I-1
failure raised there is never replaced by an I-2 code. For already
constructed inputs, every I-2 public boundary evaluates applicable checks in
this exact first-failure order:

```text
IMPLICIT_ABSENCE_FORBIDDEN
CORE_NUMBER_INVALID
NONFINITE_NUMBER_FORBIDDEN
DIVISION_BY_ZERO
IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN
NUMERICAL_POLICY_REQUIRED
NUMERICAL_POLICY_INCOMPLETE
ERROR_BOUND_INVALID
NUMERICAL_OPERATION_UNSUPPORTED
DIMENSION_MISMATCH
UNIT_MISMATCH
QUANTITY_TYPE_MISMATCH
REGION_MISMATCH
TIME_BASIS_MISMATCH
SIGN_CONVENTION_MISMATCH
BOUNDARY_MISMATCH
INVALID_AGGREGATION
CONVERSION_RULE_MISMATCH
RESOLUTION_STATE_INVALID
CLOCK_MISMATCH
HORIZON_INVALID
UNCERTAINTY_RECORD_INVALID
LIFECYCLE_TRANSITION_INVALID
SUPERSESSION_INVALID
```

Inapplicable checks are skipped, not treated as passes. Constructors apply
the same relative order to the subset they own. Validation never aggregates
several failures into a result whose order depends on container iteration.

### 21.3 Exact numeric substrate

#### 21.3.1 Shapes, projections, and constructors

`CoreNumberV1` is the closed runtime union
`IntegerV1 | RationalV1 | DecimalV1 | Binary64BitsV1`. Each variant is an
immutable exact-type checked record and projects as follows:

| Type | Exact Python fields | Exact ECJ-1 projection | Constructor behavior |
|---|---|---|---|
| `IntegerV1` | `value: int` | `{"variant":"INTEGER_V1","value":value}` | Reject `bool` and non-exact `int`; all Python integers accepted; zero has one representation |
| `RationalV1` | `numerator: IntegerV1`, `denominator: IntegerV1` | `{"denominator":d,"numerator":n,"variant":"RATIONAL_V1"}` using the nested integer values | Reject wrong types and denominator zero; normalize sign to a positive denominator, divide by `gcd(abs(n),d)`, and force zero to `0/1` |
| `DecimalV1` | `coefficient: IntegerV1`, `exponent10: IntegerV1` | `{"coefficient":c,"exponent10":e,"variant":"DECIMAL_V1"}` using nested integer values | Reject wrong types; while nonzero coefficient is divisible by 10, divide it by 10 and increment exponent; force zero to coefficient `0`, exponent `0` |
| `Binary64BitsV1` | `bits: str` | `{"bits":bits,"variant":"BINARY64_BITS_V1"}` | Require exactly 16 lowercase ASCII hex digits; reject uppercase/short/long/nonhex rather than normalize; reject exponent-all-ones as nonfinite; retain `0000000000000000` and `8000000000000000` distinctly |

Record construction performs only the normalization explicitly listed. It
does not parse decimal text, accept a Python `float`, infer a variant, or
convert variants. `normalize_core_number(value: CoreNumberV1) ->
CoreNumberV1` requires an exact union member and reconstructs its unique
normal form; because public constructors already normalize, it is idempotent.
Passing raw containers, `bool`, `float`, `Decimal`, `Fraction`, NumPy values,
or subclasses fails `CORE_NUMBER_INVALID`, except Python `float` at a
canonical boundary retains I-1 `FLOAT_FORBIDDEN` and an explicit nonfinite
encoding uses `NONFINITE_NUMBER_FORBIDDEN`.

`decimal_to_rational_exact(value: DecimalV1) -> RationalV1` is the sole I-2
cross-variant conversion. It computes `c*10^e/1` for `e>=0` and
`c/10^(-e)` otherwise, then applies rational normalization. It is total,
explicit, exact, and never called implicitly by an operation.

#### 21.3.2 Closed operation and conversion enums

`NumericalVariant` has exactly `INTEGER`, `RATIONAL`, `DECIMAL`, and
`BINARY64_BITS`. `NumericalOperation` has exactly `ADD`, `SUBTRACT`,
`MULTIPLY`, `DIVIDE`, `NEGATE`, and `COMPARE`. `ExactConversion` has exactly
`NOT_APPLICABLE`, `INTEGER_DIVISION_TO_RATIONAL`, and
`DECIMAL_TO_RATIONAL`. The last is used only by
`decimal_to_rational_exact`; it is invalid as an implicit mixed-operation
flag.

`exact_conversion` must be exact `ExactConversion.NOT_APPLICABLE` for every
matrix cell except a nondivisible `Integer/Integer` `DIVIDE`, where
`INTEGER_DIVISION_TO_RATIONAL` is required. Supplying
`INTEGER_DIVISION_TO_RATIONAL` for a divisible division or any other cell, or
supplying `DECIMAL_TO_RATIONAL` to this operation interface, fails
`NUMERICAL_OPERATION_UNSUPPORTED`; no unused conversion request is ignored.

The exact callable is:

```text
apply_exact_core_operation(
    operation: NumericalOperation,
    operands: tuple[CoreNumberV1, ...],
    *,
    exact_conversion: ExactConversion = NOT_APPLICABLE
) -> NumericalResult | ComparisonResult
```

Unary `NEGATE` takes one operand. `COMPARE` and all other operations take two.
Wrong arity is `CORE_NUMBER_INVALID`. All operands must be exact union members
and already reconstruct to their canonical normal forms. `COMPARE` returns
one of `LESS`, `EQUAL`, or `GREATER`; it has no unordered result because
nonfinite numbers do not exist.

The complete matrix is:

| Operation | `Integer/Integer` | `Rational/Rational` | `Decimal/Decimal` | `Binary64/Binary64` | Any mixed pair |
|---|---|---|---|---|---|
| `ADD` | lossless `IntegerV1` | lossless reduced `RationalV1` | lossless normalized `DecimalV1` after exact exponent alignment | `NUMERICAL_POLICY_REQUIRED` | `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` |
| `SUBTRACT` | lossless `IntegerV1` | lossless reduced `RationalV1` | lossless normalized `DecimalV1` | `NUMERICAL_POLICY_REQUIRED` | `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` |
| `MULTIPLY` | lossless `IntegerV1` | lossless reduced `RationalV1` | lossless normalized `DecimalV1` | `NUMERICAL_POLICY_REQUIRED` | `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` |
| `DIVIDE` | zero divisor fails; divisible result is lossless `IntegerV1`; otherwise succeeds as reduced `RationalV1` only when `INTEGER_DIVISION_TO_RATIONAL` is explicitly supplied, else `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` | zero divisor fails; otherwise lossless reduced `RationalV1` | zero divisor fails; a finite base-10 quotient succeeds losslessly as normalized `DecimalV1`; a repeating quotient is `NUMERICAL_POLICY_REQUIRED` | either signed-zero divisor is `DIVISION_BY_ZERO`; every other valid pair is `NUMERICAL_POLICY_REQUIRED` | zero-divisor check precedes `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN`; otherwise mixed refusal |
| `COMPARE` | exact | exact by cross-products | exact by integer coefficient/exponent alignment | `NUMERICAL_POLICY_REQUIRED` | `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN` |

| Unary operation | `Integer` | `Rational` | `Decimal` | `Binary64` |
|---|---|---|---|---|
| `NEGATE` | lossless; zero unchanged | lossless; zero remains `0/1` | lossless; zero remains `(0,0)` | `NUMERICAL_POLICY_REQUIRED`, including signed-zero handling |

For finite decimal division, reduce the coefficient fraction first. After
removing sign, the reduced denominator must factor entirely into 2s and 5s;
otherwise the quotient is repeating. The exact exponent is formed with
integer powers of 2, 5, and 10 and then normalized. Core arithmetic has no
overflow, precision, or rounding limit other than available Python integer
memory; resource exhaustion remains an operational failure, not a numeric
result.

No I-2 function evaluates binary64 arithmetic, converts binary64 to text or a
different variant, equates its signed zeros, chooses a rounding mode, or uses
host floating-point. `Binary64BitsV1` is exact stored-bit data only.

### 21.4 Numerical-policy protocol

#### 21.4.1 Common policy records

`Completeness` is a `StrEnum` with exactly `COMPLETE` and `INCOMPLETE`.
`NumericalPolicyV1` is a runtime-checkable protocol whose properties are
read-only; an implementation object may not permit assignment to any declared
field. Its exact required properties are:

| Property | Exact type and rule |
|---|---|
| `policy_ref` | `ObjectRef`; required declared policy identity only; no lifecycle, kind, role, or acceptance claim is made in I-2 |
| `owning_domain_ref` | `ObjectRef`; required declared owner identity; must differ exactly from `policy_ref`; no owner lifecycle, kind, or role is resolved in I-2 |
| `supported_input_variants` | nonempty, duplicate-free tuple of `NumericalVariant` in enum order |
| `supported_operations` | nonempty, duplicate-free tuple of `NumericalOperation` in enum order |
| `result_variant_by_operation` | tuple of `(NumericalOperation, NumericalVariant)` with exactly one row per supported non-`COMPARE` operation and no other row |
| `precision_contract_ref` | `ObjectRef | Applicability`; explicit applicability required |
| `rounding_contract_ref` | `ObjectRef | Applicability`; required for any potentially inexact result |
| `comparison_tolerance_contract_ref` | `ObjectRef | Applicability`; exact `ObjectRef` required whenever `COMPARE` is supported; I-2 proves only its declared presence and does not resolve its contents |
| `approximation_contract_ref` | `ObjectRef | Applicability`; required when approximation is allowed |
| `error_bound_contract_ref` | `ObjectRef | Applicability`; required whenever a result can be approximate |
| `overflow_underflow_nonfinite_contract_ref` | `ObjectRef`; always required |
| `signed_zero_contract_ref` | `ObjectRef | Applicability`; always required if binary64 is supported, otherwise exact typed `NOT_APPLICABLE` |
| `backend_dependency_contract_ref` | `ObjectRef`; always required before evaluation |
| `cross_platform_contract_ref` | `ObjectRef`; always required before evaluation |
| `failure_contract_ref` | `ObjectRef`; always required |
| `evidence_requirement_refs` | nonempty, duplicate-free, ObjectRef-ordered tuple |
| `runtime_constraints` | `RuntimeConstraintSet`; required and complete before evaluation |
| `completeness` | `Completeness`; validation derives, rather than trusts, this value |

Every property exists; typed `NOT_APPLICABLE` is the sole absence form.
`None`, omission, empty text, an empty required tuple, or a fabricated core
default is `IMPLICIT_ABSENCE_FORBIDDEN`. A policy is complete exactly when
all unconditional fields and every conditional field implied by its variant
and operation sets are applicable, its result mapping closes, its refs are
distinct where semantics require, runtime constraints are complete, and its
declared `completeness` is `COMPLETE`. A declaration marked complete that
fails any predicate is `NUMERICAL_POLICY_INCOMPLETE`; a declaration marked
incomplete validates only as an incomplete refusal record.
There is no core/framework-placeholder classification at this boundary.
`policy_ref` and `owning_domain_ref` equality alone is the observable owner
identity violation. Policy and owner lifecycle, kind, role, or registry
status, and tolerance-contract contents, are deferred to a later authorized
registry/domain stage.
Structural omission is therefore implicit absence, whereas an explicitly
present typed `NOT_APPLICABLE` value is evaluated against the field's
applicability predicate. Validation uses only the resulting declaration and
never the operations or patch history used to construct it.

The canonical declaration projection is an ECJ-1 object named
`NumericalPolicyV1ProjectionV1`. It contains `schema_id` equal to
`ebu.numerical-policy/1`, followed by every property in the table above in
that exact table order. Enums project to their exact values, refs to their
I-1 `ObjectRef` projections, tuples to ordered arrays, mapping rows to
two-element arrays, and typed `NOT_APPLICABLE` to the string
`NOT_APPLICABLE`. Protocol implementation class, method objects, Python
module/qualname, cache, backend instance, validation result, and record
metadata are excluded. Every policy property is therefore present in the
projection; absence is never expressed by omission or JSON null.

Each immutable §21.4.1 support/result record has `to_ecj1()` with
`schema_version` equal to integer `1` followed by its fields in the exact
declaration order below. Enums project to values, refs to I-1 ref objects,
core numbers to §21.3 projections, nested records recursively, tuples to
ordered arrays, booleans to ECJ-1 booleans, and typed `NOT_APPLICABLE` to the
string `NOT_APPLICABLE`. No field is omitted and JSON null is forbidden.
Validation failures and record/implementation metadata never enter a
successful result projection except the explicitly declared `failure` union.

`RuntimeConstraintSet` is assigned to I-2 `numeric.py`, not deferred to I-3.
It is an immutable record with `constraint_refs: tuple[ObjectRef, ...]`,
`applicability: Applicability`, and `completeness: Completeness`. Applicable
sets require a nonempty duplicate-free ObjectRef-ordered tuple; not-applicable
sets require an empty tuple and `COMPLETE`. It is non-scientific structure:
it records requirements chosen elsewhere and chooses none.

`QuantityContext` is immutable with exact fields
`dimension_ref: ObjectRef`, `unit_ref: ObjectRef`,
`resource_type_ref: ObjectRef | Applicability`,
`service_type_ref: ObjectRef | Applicability`,
`region_ref: ObjectRef | Applicability`,
`time_basis_ref: ObjectRef | Applicability`,
`sign_convention_ref: ObjectRef | Applicability`, and
`boundary_ref: ObjectRef`, and
`uncertainty_applicability: Applicability`. Every conditional ref is
explicitly applicable or the exact `NOT_APPLICABLE` member; boundary is never
conditional. `uncertainty_applicability` is an explicit applicability field:
`NOT_APPLICABLE` requires `Quantity.uncertainty_ref` to be exactly typed
`NOT_APPLICABLE`, and `APPLICABLE` requires it to be an exact `ObjectRef`.
`Applicability.APPLICABLE` is valid only in this explicit field and is never
a substitute reference. Applicability is not inferred from magnitude, unit,
resolution, resource, service, region, boundary, or caller context. A
mismatch fails `UNCERTAINTY_RECORD_INVALID`. I-2 neither resolves nor
evaluates the referenced uncertainty record.

`OperandValidationResult` fields are `operation: NumericalOperation`,
`operand_variants: tuple[NumericalVariant, ...]`,
`policy_ref: ObjectRef`, `quantity_context: QuantityContext`,
`valid: bool`, `completeness: Completeness`, and
`failure: FailureEnvelope | Applicability`. `valid=True` requires complete and
typed `NOT_APPLICABLE` failure; `valid=False` requires one exact failure.

`ErrorBound` fields are `bound_kind: str` in `EXACT_ZERO`, `ABSOLUTE`,
`RELATIVE`, `ULP`, `INTERVAL`; `lower: CoreNumberV1 | Applicability`,
`upper: CoreNumberV1 | Applicability`, `unit_ref: ObjectRef | Applicability`,
`policy_ref: ObjectRef | Applicability`, and `completeness: Completeness`.
Construction performs exact structural validation, separately from any later
authenticity, acceptance, generation, or execution of the referenced policy:

- `EXACT_ZERO` requires `lower` and `upper` to be exact `IntegerV1(0)` and
  requires `unit_ref` and `policy_ref` to be exact typed `NOT_APPLICABLE`;
- `ABSOLUTE`, `RELATIVE`, `ULP`, and `INTERVAL` require an exact applicable
  `policy_ref`;
- `ABSOLUTE` and `INTERVAL` require an exact applicable `unit_ref`;
- `RELATIVE` and `ULP` require `unit_ref` to be exact typed
  `NOT_APPLICABLE`;
- `ULP` requires both bounds to be exact `IntegerV1` values;
- every other nonzero kind requires both bounds to use the same exact variant
  from `IntegerV1`, `RationalV1`, or `DecimalV1`;
- a `Binary64BitsV1` bound cannot be structurally ordered in I-2 and fails
  `NUMERICAL_POLICY_REQUIRED`;
- mixed variants fail `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN`;
- for every nonzero kind, I-2 uses only the exact core comparison rules to
  require `0 <= lower <= upper`; it does not invoke or resolve the policy;
- a missing required policy fails `NUMERICAL_POLICY_REQUIRED`, and a missing
  required unit fails `IMPLICIT_ABSENCE_FORBIDDEN`;
- an otherwise malformed kind-specific field, negative lower bound, reversed
  relation, forbidden applicable unit/policy, or incomplete-bound use in a
  complete result fails `ERROR_BOUND_INVALID`.

The policy reference records applicability and provenance only. I-2 does not
establish its authenticity, acceptance, or scientific adequacy and cannot
call a provider. `Completeness.COMPLETE` means exactly that the structural
fields and exact inequalities above are complete; it does not mean the
referenced policy is accepted or scientifically validated. An otherwise
well-shaped `ErrorBound` may carry `Completeness.INCOMPLETE` only as an
incomplete refusal/evidence record. It cannot be the `error_bound` of a
`NumericalResult` whose completeness is `COMPLETE`; that relation fails
`ERROR_BOUND_INVALID`. Exact core operations return only `EXACT_ZERO` with
`COMPLETE`.

`NumericalResult` fields are `value: CoreNumberV1`,
`operation: NumericalOperation`, `operand_variants:
tuple[NumericalVariant, ...]`, `policy_ref: ObjectRef | Applicability`,
`rounding_evidence_ref: ObjectRef | Applicability`,
`error_bound: ErrorBound`, and `completeness: Completeness`. Exact core results
use typed not-applicable policy/rounding, `EXACT_ZERO`, and `COMPLETE`.

`ComparisonResult` fields are `ordering: str` in `LESS`, `EQUAL`, `GREATER`,
`purpose: str` in `EXACT_CORE`, `DOMAIN_DECISION`, `TOLERANCE_CLASSIFICATION`,
`policy_ref: ObjectRef | Applicability`, `error_bound: ErrorBound | Applicability`,
and `completeness: Completeness`. Core compare uses `EXACT_CORE` and typed
not-applicable policy/error bound. Domain purposes require both.

#### 21.4.2 Exact protocol methods and I-2 prohibition

Every future concrete `NumericalPolicyV1` provider exposes exactly:

```text
validate_operands(
    operation: NumericalOperation,
    operands: tuple[CoreNumberV1, ...],
    quantity_context: QuantityContext
) -> OperandValidationResult

evaluate(
    operation: NumericalOperation,
    operands: tuple[CoreNumberV1, ...],
    quantity_context: QuantityContext
) -> NumericalResult

compare(
    purpose: str,
    left: CoreNumberV1,
    right: CoreNumberV1,
    quantity_context: QuantityContext
) -> ComparisonResult

bound_error(
    operation: NumericalOperation,
    operands: tuple[CoreNumberV1, ...],
    result: NumericalResult,
    quantity_context: QuantityContext
) -> ErrorBound

runtime_requirements() -> RuntimeConstraintSet
```

No additional positional/keyword parameter, variadic argument, default,
callback, global context, or hidden backend access is permitted. I-2 may
define the protocol and `validate_numerical_policy(policy) -> Completeness`,
which inspects shape and cross-field completeness only. I-2 must not
instantiate a default provider, call any of these five methods, accept a
policy into a production registry, or choose/execute precision, tolerance,
approximation, rounding, backend, signed-zero equivalence, overflow,
underflow, nonfinite, or cross-platform behavior. Consequently every
policy-required core request fails `NUMERICAL_POLICY_REQUIRED` during I-2.

### 21.5 Typed primitive and envelope schemas

#### 21.5.1 Common rules and projections

Every I-2 record below is immutable and provides `to_ecj1()` containing
exactly its listed fields plus a `schema_version` literal `1`. Field names are
sorted by ECJ-1 at encoding; tuples project to their declared order. Derived
validation results and non-scientific `RecordMetadata` never enter the
scientific record projection. Exact type identity rather than `isinstance`
coercion applies at the boundary assigned in §21.8.6, and `bool` is rejected
where `int` is named. The word “invariant” in the schema tables states a
condition required for validation or use; it does not by itself assign that
condition to construction.

The governing boundary rule is:

> Construction produces an immutable, structurally well-formed candidate. It
> does not imply semantic validity, lifecycle acceptance, scientific
> acceptance or registry acceptance. Where a public `validate_*` callable
> exists, every predicate assigned to that callable is evaluated there—not
> duplicated or pre-empted by construction.

The complete formation and validation ownership assignment is §21.8.6. A
candidate retained for validator testing is never described as valid,
accepted, or usable as scientific authority before that validator succeeds.

Every T0 validator predicate is decidable solely from the exact declared
values of that validator's arguments. An `ObjectRef` proves only its declared
identity at that argument coordinate. No predicate may resolve the ref,
consult a registry or envelope, infer hidden lifecycle/kind/role/content,
use fixture-specific knowledge, inspect patch or construction history, or
read any other hidden or mutable state. When a stronger claim requires such
information, that claim is explicitly deferred rather than inferred.

Every conditional reference coordinate is a closed tagged union
`ObjectRef | Applicability`: an exact ref means applicable, and the only
permitted `Applicability` value in that union is `NOT_APPLICABLE`.
`APPLICABLE` is stored only in records that have a separate explicit
`applicability` field. Omission, `None`, zero, empty string/tuple, or a
free-form absence reason is forbidden. The schemas do not infer
applicability from another coordinate.

`CompatibilityResult` is the common immutable return record with
`compatible: bool`, `checked_predicates: tuple[str, ...]` in the exact
function-defined order, `conversion_rule_ref: ObjectRef | Applicability`,
`parent_ref: ObjectRef | Applicability`, and
`failure: FailureEnvelope | Applicability`. Success requires typed
not-applicable failure; failure requires exactly one envelope. It describes
compatibility only and performs no aggregation or scientific operation.

#### 21.5.2 Dimensions, units, conversions, and quantities

| Type | Exact fields and invariants |
|---|---|
| `Dimension` | `dimension_ref: ObjectRef`; `dimension_kind: str` in `PHYSICAL`, `DECLARED_INSTITUTIONAL`; `basis_exponents: tuple[tuple[ObjectRef,RationalV1], ...]`, nonempty, unique and ObjectRef-ordered, with nonzero exponents. There is no implicit universal scalar/dimensionless entry. |
| `Unit` | `unit_ref: ObjectRef`; `dimension_ref: ObjectRef`; `unit_kind: str` in `BASE`, `DERIVED`, `DECLARED_INSTITUTIONAL`; `symbol: str` nonempty NFC; `definition_ref: ObjectRef`; `validity_horizon_ref: ObjectRef | Applicability`. Identity is exact `unit_ref`, not symbol equality. |
| `ConversionRule` | `conversion_ref`, `source_unit_ref`, `target_unit_ref`, `dimension_ref`: `ObjectRef`; `direction: str` in `FORWARD_ONLY`, `BIDIRECTIONAL`; `factor: RationalV1 | DecimalV1`, nonzero; `offset: RationalV1 | DecimalV1 | Applicability`; `validity_horizon_ref: ObjectRef | Applicability`. Factor and applicable offset use the same variant. Typed not-applicable offset means exact zero offset. |
| `Quantity` | `magnitude: CoreNumberV1`; `unit_ref`, `dimension_ref`, `boundary_ref`: `ObjectRef`; `resource_type_ref`, `service_type_ref`, `region_ref`, `time_basis_ref`, `sign_convention_ref`, `uncertainty_ref`: `ObjectRef | Applicability`; `resolution: ResolutionDetail`. Only `NOT_APPLICABLE` may occupy a conditional union. `boundary_ref` is mandatory and never inferred. |

Dimensions are compatible only when exact `dimension_ref` values and complete
basis-exponent vectors match. Units are identical only on exact `unit_ref`;
they are compatible for conversion only when dimensions match and a supplied
rule names the exact source/target in an allowed direction. For both unit
compatibility and standalone rule validation, `FORWARD_ONLY` requires the
declared `source_unit_ref` to equal the supplied source `unit_ref` and the
declared `target_unit_ref` to equal the supplied target `unit_ref`;
`BIDIRECTIONAL` permits exactly that orientation or its exact reversal. The
rule, source unit, and target unit must declare one identical `dimension_ref`.
The rule's `validity_horizon_ref` must be an exact `ObjectRef` or exact
`NOT_APPLICABLE`; `APPLICABLE` is forbidden at this union coordinate, and I-2
does not resolve or compare horizon contents. Exact conversion
computes `target = source * factor + offset`, treating typed not-applicable
offset as exact zero. All operations must succeed through §21.3 without a
policy; otherwise conversion is refused. The returned quantity changes only
magnitude and unit ref; every other coordinate is byte-for-byte identical.
`convert_quantity_exact` takes its source coordinate from the explicitly
supplied `source_unit`; it requires exact equality between
`quantity.unit_ref` and `source_unit.unit_ref` and never infers or looks up a
unit from either opaque ref. Its target coordinate comes from the explicitly
supplied `target_unit`. Across the ordered `target_unit` and
`conversion_rule` checks, the quantity, source-unit, target-unit, and rule
dimensions are all compared: disagreement among the first three fails
`DIMENSION_MISMATCH`, while a rule-declared dimension that disagrees with the
already compatible explicit units fails the `dimension` predicate of
`validate_conversion_rule` with `CONVERSION_RULE_MISMATCH`. No literal
fixture reference is privileged.

Two forward affine rules `A->B` and `B->C` may compose only when the explicit
unit chain supplies `A`, `B`, and `C`, the middle unit/dimension/horizon match,
and all exact operations are supported. The
composed factor is `f_BC*f_AB`; offset is `f_BC*o_AB+o_BC`. Direction is
forward unless both inputs are bidirectional and both factors have exact
nonzero inverses in their existing variants. No implicit inverse, float,
policy, exchange rate, price, domain weight, or settlement value is a unit
conversion.

Quantity compatibility checks, in order, resolution, dimension, unit,
resource/service type, region, time basis, sign convention, boundary, then
uncertainty applicability. At the final check, exact
`QuantityContext.uncertainty_applicability=NOT_APPLICABLE` requires exact
typed `Quantity.uncertainty_ref=NOT_APPLICABLE`, while `APPLICABLE` requires
an exact `ObjectRef`; a mismatch fails `UNCERTAINTY_RECORD_INVALID`. The
validator does not resolve or evaluate that reference. Addition, comparison,
or aggregation is invalid unless every applicable coordinate is compatible.
I-2 validates this predicate but exposes no public quantity-addition or
aggregation callable.

#### 21.5.3 Resources, services, sign, regions, and boundaries

| Type | Exact fields and invariants |
|---|---|
| `ResourceType` | `resource_type_ref`, `dimension_ref`, `definition_ref`: `ObjectRef`; `service_compatibility_refs: tuple[ObjectRef,...]`, duplicate-free and ordered; `validity_horizon_ref: ObjectRef | Applicability` |
| `ServiceType` | `service_type_ref`, `definition_ref`: `ObjectRef`; `required_resource_type_refs: tuple[ObjectRef,...]`, nonempty, duplicate-free and ordered; `output_dimension_ref: ObjectRef | Applicability`; `validity_horizon_ref: ObjectRef | Applicability` |
| `SignConvention` | `sign_convention_ref`, `definition_ref`: `ObjectRef`; `positive_meaning`, `zero_meaning`, `negative_meaning`: nonempty NFC strings; the three meanings must be pairwise distinct |
| `Region` | `region_ref`, `membership_rule_ref`, `clock_ref`: `ObjectRef`; `parent_region_ref: ObjectRef | Applicability`; `spatial_interpretation: str` in `PHYSICAL`, `NETWORK_NODE_SET`, `INSTITUTIONAL`; `validity_start`, `validity_end`: `Instant`; parent cannot equal self |
| `AccountingBoundary` | `boundary_ref`, `state_schema_ref`, `distortion_ref`, `clock_ref`, `initial_epoch_ref`, `horizon_ref`, `definition_ref`: `ObjectRef`; `parent_boundary_ref`, `comparator_ref`, `objective_ref`, `institutional_rule_ref`: `ObjectRef | Applicability`; `included_resource_type_refs`, `included_service_type_refs`, `included_provider_refs`, `included_actor_refs`, `included_node_refs`, `included_edge_refs`, `included_region_refs`, `included_lifecycle_stage_refs`, `external_effect_refs`, `commitment_refs`, `reservation_refs`, `queue_refs`, `measurement_refs`, `natural_drive_refs`, `external_input_refs`, `unresolved_cross_boundary_effect_refs`: duplicate-free ObjectRef-ordered tuples; `cross_boundary_effect_treatments: tuple[tuple[ObjectRef, ObjectRef], ...]`, exact `(effect_ref, treatment_ref)` pairs ordered by `effect_ref`, with unique effect keys and no duplicate pair |

Resource/service compatibility requires the quantity's resource and service
applicability markers to agree with the expected type. When both apply, the
exact resource ref must occur in the service's ordered required-resource
tuple and the service ref in the resource's compatibility tuple. Either
one-sided declaration is `QUANTITY_TYPE_MISMATCH`.

Region equality is exact ref equality. Parent aggregation requires a supplied
parent region, each child's exact `parent_region_ref` equalling the supplied
parent's `region_ref`, the same clock and a parent validity interval covering
both children, distinct child region refs, and an exact aggregation-rule ref.
“The same clock” means exact equality among the parent and both children's
declared `clock_ref` values; interval coverage is decided only from their
declared `validity_start` and `validity_end` values.
The opaque `membership_rule_ref` is preserved but never resolved, so I-2 does
not prove child disjointness or real-world membership. Parent acceptance and
membership/disjointness evidence are external I-4 concerns. Boundary parent
aggregation analogously requires each child's exact `parent_boundary_ref`
equal the supplied parent's `boundary_ref`, compatible
state/distortion/clock/horizon contracts, distinct child refs, and an exact
aggregation-rule ref. In addition, each child boundary's treatment-map effect
keys must equal the exact set union of that child's `external_effect_refs`
and `unresolved_cross_boundary_effect_refs`; no effect may be missing or
extra. This proves only coverage of the supplied declarations, not real-world
effect completeness or treatment adequacy. The validators return
compatibility only; I-2 creates no aggregated quantity. Missing declared
treatment coverage, domain conversion, scalarization, or a declared parent
link is `INVALID_AGGREGATION`; membership overlap is not decided in I-2.

Sign conventions are compatible only when both are typed not-applicable or
both apply with the exact same ref. No automatic sign flip exists; a sign
change is a separately declared domain transformation unavailable in I-2.

#### 21.5.4 Time and horizons

| Type | Exact fields and invariants |
|---|---|
| `ClockSystem` | `clock_ref`, `epoch_definition_ref`, `duration_unit_ref`: `ObjectRef`; `ordering: str` exactly `DISCRETE_TOTAL`; `origin_ref: ObjectRef | Applicability` |
| `Instant` | `clock_ref: ObjectRef`; `tick: IntegerV1`; tick is nonnegative |
| `Duration` | `clock_ref: ObjectRef`; `ticks: IntegerV1`; ticks is strictly positive |
| `Epoch` | `clock_ref: ObjectRef`; `index: IntegerV1`; index is nonnegative |
| `Horizon` | `horizon_ref`, `clock_ref`, `completion_rule_ref`, `settlement_rule_ref`: `ObjectRef`; `start`, `terminal`: `Instant`; `endpoint_inclusion: str` in `CLOSED`, `LEFT_CLOSED_RIGHT_OPEN`; `resolution: Duration`; `measurement_epochs: tuple[Epoch,...]`, strictly increasing and inside the included interval; `post_terminal_effect_treatment: str` in `REMAIN_PENDING`, `OUT_OF_BOUNDARY`; `terminal_pending_treatment: str` in `ALLOW_EXPLICIT_PENDING`, `REQUIRE_NONE_PENDING` |

Clock compatibility is exact clock-ref equality. A rate requires an applicable
time-basis ref; a non-rate requires typed not-applicable. I-2 does not infer a
rate from a unit symbol or dimension. Horizons require same-clock fields,
`start <= terminal`, positive resolution, unambiguous endpoint inclusion, and
an explicit post-terminal rule. At a closed terminal point, effects due there
are inside; at a right-open terminal they remain pending/out-of-boundary under
the named rule. Pending effects are never zero. `REQUIRE_NONE_PENDING` fails
unless the supplied pending-effect/due-condition pair tuple is empty;
`ALLOW_EXPLICIT_PENDING` accepts the exact supplied pair tuple after checking
that every item is an exact `(effect_ref, due_condition_ref)` pair, pairs are
ordered by `effect_ref`, and effect keys are unique. This validates only the
caller-supplied declarations. Global pending-effect completeness and whether
a due condition is substantively correct are deferred; I-2 does not discover
or resolve either ref. Pair formation/order/uniqueness and the selected
treatment relation are all owned by the existing
`terminal_pending_treatment` predicate and fail `HORIZON_INVALID`.

#### 21.5.5 Resolution and uncertainty

`ResolutionState` has exactly `PRESENT`, `PENDING`, `FAILED`, `PARTIAL`,
`UNRESOLVED`, `OUT_OF_BOUNDARY`, and `NOT_APPLICABLE`.
`ResolutionDetail` fields are `state: ResolutionState`,
`present_value_ref: ObjectRef | Applicability`,
`completed_part_refs: tuple[ObjectRef,...]`,
`missing_part_refs: tuple[ObjectRef,...]`,
`due_condition_ref: ObjectRef | Applicability`,
`failure: FailureEnvelope | Applicability`,
`boundary_edge_ref: ObjectRef | Applicability`, and
`reason_ref: ObjectRef | Applicability`.

The exact state predicates are: `PRESENT` requires a value and no completed,
missing, due, failure, boundary, or reason fields; `PENDING` requires due and
no completed/missing/value/failure; `FAILED` requires failure;
`PARTIAL` requires nonempty disjoint completed and missing tuples;
`UNRESOLVED` requires reason and no claim that a value is present;
`OUT_OF_BOUNDARY` requires boundary edge and reason; `NOT_APPLICABLE`
requires reason and no value/effect tuple. A completed obligation whose value
is missing is `PARTIAL` with a missing part, not `PENDING`; insufficient
evidence to determine whether completion occurred is `UNRESOLVED`.

`UncertaintyKind` retains exactly the eight values in §5.5.
`UncertaintyRecord` fields are `uncertainty_ref: ObjectRef`,
`kind: UncertaintyKind`, `value_unit_ref: ObjectRef | Applicability`,
`lower: Quantity | Applicability`, `upper: Quantity | Applicability`,
`member_refs: tuple[ObjectRef,...]`,
`probability_model_ref: ObjectRef | Applicability`,
`calibration_ref: ObjectRef | Applicability`,
`provenance_refs: tuple[ObjectRef,...]`,
`violated_contract_ref: ObjectRef | Applicability`, and
`resolution: ResolutionDetail`.

Kind predicates are closed: `EXACT` has no bounds/set/model and must be
`PRESENT`; `MEASUREMENT_INTERVAL` requires same-coordinate ordered lower and
upper quantities plus calibration; `ADMISSIBLE_SET` and `ADVERSARIAL_SET`
require nonempty ordered member refs and forbid probability model;
`PROBABILITY_MODEL` requires its exact model ref and provenance;
`MODEL_DISCREPANCY` requires interval or set evidence and provenance;
`UNKNOWN` requires `UNRESOLVED` and no invented bound/model. `OUT_OF_SET`
requires an exact `violated_contract_ref`, requires that same exact ref occur
in `provenance_refs`, and requires a present supplied value reference through
resolution. Every other kind requires exact typed `NOT_APPLICABLE` at
`violated_contract_ref`. I-2 proves only these declared roles and identities;
it does not resolve the contract or establish that the value truly violates
it. A range never implies a distribution.

#### 21.5.6 Common object envelope and metadata

`CommonObjectEnvelope` is immutable with exact fields `object_id:
ScientificId`, `object_kind_id: ScientificId`, `schema_id: ScientificId`,
`schema_version: SemanticVersion`, `object_version: SemanticVersion`,
`authority_refs: tuple[ObjectRef,...]`, `supersedes_ref: ObjectRef |
Applicability`, `object_content_payload: CanonicalBytes`,
`object_content_hash: ObjectContentHash`, `lifecycle_status:
LifecycleStatus`, and `record_metadata_ref: ObjectRef | Applicability`.

Authority refs are duplicate-free and ordered. `object_kind_id` replaces the
earlier unconstrained “registered enum” placeholder with a registered
`ScientificId`. The payload accepts exact `bytes` only, typed through the
existing `CanonicalBytes`. `bytearray`, `memoryview`, `dict`, `list`, all
subclasses, and every other runtime type fail without conversion. Construction
passes the exact bytes to the unchanged `parse_ecj1` boundary. Malformed,
noncanonical, duplicate-key, nonfinite, invalid-Unicode, and otherwise invalid
bytes therefore fail through the applicable existing I-1 canonical failure
semantics before an I-2 envelope check.

The canonical bytes are the sole authoritative payload representation stored
inside the envelope. A caller may encode a mutable source tree before
construction, but later mutation of that source cannot change the stored
bytes, projection, or hash. A separately parsed tree is also independent and
may be mutated and discarded without changing the envelope. No constructor,
property, validator, closure, slot, or private cache may retain or expose a
decoded mutable payload tree.

The validator's `direct_content_hash_exclusion` predicate recursively walks
the freshly parsed ECJ-1 payload and rejects any exact string occurrence of
the envelope's stored `object_content_hash`, whether it occurs as an object
name, object value, or array member at any depth. This is only a direct stored-hash
occurrence check. It does not resolve aliases or refs, traverse a registry or
object graph, or claim to detect indirect/semantic cycles; those checks are
deferred to a later registry stage.

`validate_object_envelope` checks exact field types and ordering, calls
`parse_ecj1` to obtain one fresh temporary logical ECJ-1 value, passes that
logical value as `object_content_payload` to the unchanged
`compute_object_content_hash`, discards the temporary value, and compares the
result with the stored exact `ObjectContentHash`. The stored bytes are never
projected as a string, hex, integer array, or nested JSON text. The logical
payload, stored canonical bytes, complete `ObjectContentPreimageV1`, and
resulting `ObjectContentHash` are four distinct concepts.

The object-content projection otherwise remains exactly I-1: `object_kind`
is the string form of `object_kind_id`, and typed not-applicable supersession
projects as ECJ-1 `null` only inside the preimage adapter.
`object_content_hash` is excluded from its own preimage, and the direct
occurrence predicate above is checked before final recomputation. Lifecycle, record
metadata, validation/failure records, signatures, storage, time,
host/process, publication, and presentation data remain excluded. A
recomputation mismatch uses the existing exact `HASH_MISMATCH` code and
meaning at the I-2 validator coordinate. No edit to `canonical.py` or
`hashing.py` is required or authorized.

The one new direct dependency `envelopes -> canonical` is authorized only for
`CanonicalBytes` and `parse_ecj1`. `envelopes.py` must not import
`encode_ecj1`, canonicalization helpers, Unicode tables/assets, or any other
canonical name; must not normalize arbitrary input; and must not import
`registry`. `canonical`, `hashing`, and `identity` must not import
`envelopes`. Dynamic import is forbidden in production and validation code.

`RecordMetadata` is immutable non-scientific structure with
`metadata_id: ScientificId`, `storage_locator`, `database_identity`,
`ingestion_time_ref`, `host_process_ref`, `transport_ref`,
`presentation_annotation_ref`, and `operational_provenance_ref`, where every
field after `metadata_id` is `ObjectRef | Applicability`. It has no scientific
canonical projection and is referenced only outside object-content preimages.
Changing it cannot change an object hash.

#### 21.5.7 Lifecycle and supersession

`LifecycleStatus` has exactly `DRAFT`, `REVIEWED`, `ACCEPTED`, `SUPERSEDED`,
and `REVOKED_BEFORE_EXECUTION`. `LifecycleTransition` is immutable with
`object_ref: ObjectRef`, `from_status: LifecycleStatus`, `to_status:
LifecycleStatus`, `evidence_refs: tuple[ObjectRef,...]`, and
`authorization_ref: ObjectRef | Applicability`.

Every `LifecycleTransition.evidence_refs` value must be an exact tuple, must
be nonempty, must contain no duplicate, and must be lexicographically ordered
by `(object_id, object_version, object_content_hash)`. The checked predicate
`evidence_order` means all four requirements exactly. Violation of any one
fails `LIFECYCLE_TRANSITION_INVALID`.

The closed graph is:

```text
DRAFT -> REVIEWED
REVIEWED -> DRAFT
REVIEWED -> ACCEPTED
ACCEPTED -> SUPERSEDED
ACCEPTED -> REVOKED_BEFORE_EXECUTION
```

No self-edge or other edge is valid. I-2 `validate_lifecycle_transition`
checks only graph shape. It requires typed not-applicable authorization for
`DRAFT <-> REVIEWED`; it requires an applicable external authorization ref
for the other three edges but does not validate that authority, mutate a
registry, or create the target status.

`LifecycleValidationResult` is immutable with `valid: bool`, `transition:
LifecycleTransition`, `checked_predicates: tuple[str,...]`, and `failure:
FailureEnvelope | Applicability`. Checked-predicate strings come only from
the closed graph-check implementation order. Success requires the exact
`NOT_APPLICABLE` failure marker; failure requires one envelope.

`SupersessionRelation` is immutable with exactly these eleven fields in this
order: `predecessor_ref: ObjectRef`, `successor_ref: ObjectRef`,
`predecessor_object_kind_id: ScientificId`, `successor_object_kind_id:
ScientificId`, `predecessor_schema_id: ScientificId`, `successor_schema_id:
ScientificId`, `predecessor_status: LifecycleStatus`, `successor_status:
LifecycleStatus`, `predecessor_supersedes_chain: tuple[ObjectRef,...]`,
`relation_evidence_refs: tuple[ObjectRef,...]`, and `authorization_ref:
ObjectRef | Applicability`.

Validation requires equal logical `object_id`; exact equality between
`predecessor_object_kind_id` and `successor_object_kind_id` for predicate
`object_kind_id`; exact equality between `predecessor_schema_id` and
`successor_schema_id` for predicate `schema_id`; strictly greater semantic
version under numeric major/minor/patch ordering; different content hashes;
predecessor `ACCEPTED`; successor `REVIEWED`; the predecessor absent from its
own chain; successor absent from the full chain; unique contiguous ancestry
ending at the predecessor; nonempty evidence; and an applicable authorization
ref. These kind and schema predicates use only the corresponding two declared
fields. They perform no registry, dynamic-import, envelope, inferred-metadata,
patch-history, or other external mutable-state lookup. At this unconditionally
required validator coordinate, explicit typed `Applicability.NOT_APPLICABLE`
is forbidden absence and fails `authorization_applicable` with
`IMPLICIT_ABSENCE_FORBIDDEN`; no constructor default, `None`, missing-field
sentinel, raw mapping, or object bypass participates. The validator returns a
`SupersessionValidationResult` and mutates nothing. After I-4-authorized
mutation, the predecessor may be represented by a new immutable registry
status record `SUPERSEDED`; its accepted content bytes remain unchanged.

`SupersessionValidationResult` is immutable with `valid: bool`, `relation:
SupersessionRelation`, `checked_predicates: tuple[str,...]`, and `failure:
FailureEnvelope | Applicability`. Predicate labels come only from the closed
§21.5.7 validation order. Success requires exact `NOT_APPLICABLE`; failure
requires one envelope. Both lifecycle result records are validation evidence
and never enter an object-content preimage.

`ClaimStatus` retains the ten values in §2.4 as exact `StrEnum` members:
`DEFINITION`, `ALGEBRAIC_IDENTITY`, `THEOREM`, `MODEL_DEPENDENT_RESULT`,
`TESTED_IMPLEMENTATION_PROPERTY`, `OBSERVED_REGISTERED_RESULT`,
`RESEARCH_HYPOTHESIS`, `INSTITUTIONAL_DESIGN_CHOICE`, `ANALOGY`, and
`OPEN_PROBLEM`.

### 21.6 Compatibility predicates and public T0 behavior

The exact I-2 compatibility callables and check order are:

```text
validate_dimension_compatibility(left: Dimension, right: Dimension) -> CompatibilityResult
validate_unit_compatibility(source: Unit, target: Unit, conversion_or_not_applicable: ConversionRule | Applicability) -> CompatibilityResult
validate_conversion_rule(
    rule: ConversionRule,
    source_unit: Unit,
    target_unit: Unit,
) -> CompatibilityResult
convert_quantity_exact(
    quantity: Quantity,
    source_unit: Unit,
    target_unit: Unit,
    rule: ConversionRule,
) -> Quantity
validate_quantity(quantity: Quantity, expected_context: QuantityContext) -> CompatibilityResult
validate_resource_service_compatibility(resource: ResourceType, service: ServiceType) -> CompatibilityResult
validate_region_compatibility(left: Region, right: Region, parent_or_not_applicable: Region | Applicability, aggregation_rule_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult
validate_boundary_compatibility(left: AccountingBoundary, right: AccountingBoundary, parent_or_not_applicable: AccountingBoundary | Applicability, aggregation_rule_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult
validate_sign_convention_compatibility(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: ObjectRef | Applicability) -> CompatibilityResult
validate_time_basis(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: ObjectRef | Applicability, rate_required: bool) -> CompatibilityResult
validate_clock_compatibility(left: ClockSystem, right: ClockSystem) -> CompatibilityResult
validate_horizon(
    horizon: Horizon,
    pending_effect_due_pairs: tuple[tuple[ObjectRef, ObjectRef], ...],
) -> CompatibilityResult
validate_uncertainty_record(record: UncertaintyRecord) -> CompatibilityResult
validate_resolution_detail(record: ResolutionDetail) -> CompatibilityResult
validate_object_envelope(envelope: CommonObjectEnvelope) -> CompatibilityResult
validate_lifecycle_transition(transition: LifecycleTransition) -> LifecycleValidationResult
validate_supersession_relation(relation: SupersessionRelation) -> SupersessionValidationResult
```

| Callable | Predicate and output |
|---|---|
| `validate_dimension_compatibility(left, right)` | Exact ref and basis-vector equality -> `CompatibilityResult` |
| `validate_unit_compatibility(source, target, conversion_or_not_applicable)` | Dimension first; exact unit identity succeeds without conversion; otherwise applies the same direction, endpoint, three-way dimension, and declared horizon-union rules as standalone conversion validation -> result |
| `validate_conversion_rule(rule, source_unit, target_unit)` | Nonzero factor, offset variant, declared direction plus exact supplied endpoints, three-way declared dimension equality, and exact horizon-union form; returns `CompatibilityResult` |
| `convert_quantity_exact(quantity, source_unit, target_unit, rule)` | Intrinsic quantity-required state, exact quantity/source identity, quantity/source/target dimension compatibility, exact supplied rule validation, exact core multiply/add, unchanged coordinates -> new immutable `Quantity` |
| `validate_quantity(quantity, expected_context)` | Resolution then dimension, unit, type, region, time, sign, boundary, uncertainty -> result |
| `validate_resource_service_compatibility(resource, service)` | Symmetric exact registry declarations -> result |
| `validate_region_compatibility(left, right, parent_or_not_applicable, aggregation_rule_or_not_applicable)` | Exact identity or explicit valid common parent only |
| `validate_boundary_compatibility(left, right, parent_or_not_applicable, aggregation_rule_or_not_applicable)` | Exact identity or explicit valid common parent only |
| `validate_sign_convention_compatibility(left_or_na, right_or_na)` | Both not applicable or exact same ref |
| `validate_time_basis(left_or_na, right_or_na, rate_required)` | Applicability predicate then exact ref equality |
| `validate_clock_compatibility(left, right)` | Exact clock ref equality |
| `validate_horizon(horizon, pending_effect_due_pairs)` | All §21.5.4 ordering/inclusion predicates plus exact ordered unique supplied effect/due-ref pairs -> result |
| `validate_uncertainty_record(record)` | Closed kind-specific rules -> result |
| `validate_resolution_detail(record)` | Closed state-specific rules -> result |
| `validate_object_envelope(envelope)` | Exact fields, ordering, lifecycle, recursive direct stored-hash occurrence exclusion, and I-1 content-hash recomputation -> validation result |
| `validate_lifecycle_transition(transition)` | Pure closed-graph validation; no mutation |
| `validate_supersession_relation(relation)` | Pure immutable predicates in §21.5.7; no mutation |

These functions are T0. Every predicate uses only the exact declared values
of the listed arguments; an `ObjectRef` proves identity only. They accept
already supplied immutable records, do not look up aliases, registry entries,
envelopes, kinds, roles, lifecycle, or content, do not infer missing refs or
inspect fixture/patch history, do not invoke a domain policy, and
do not add/compare/aggregate scientific magnitudes except the exact arithmetic
inside an explicitly supplied unit conversion. No compatibility success is
permission to perform scientific aggregation.

`convert_quantity_exact` evaluates the following locally witnessed checks in
the printed order. The labels are fixture rejection/evidence labels rather
than a new public result projection:

| Check or rejection label | Exact argument evidence and owner | Failure |
|---|---|---|
| `quantity_valid` | `quantity`, including `validate_resolution_detail(quantity.resolution)` followed by the intrinsic exact-conversion requirement that its resolution is `PRESENT` with the required present payload; no synthetic `QuantityContext` is invented | the intrinsic owning code, including `RESOLUTION_STATE_INVALID` |
| `source_unit` | exact comparison of `quantity.unit_ref` with `source_unit.unit_ref` | `UNIT_MISMATCH` |
| `target_unit` | exact comparison of `quantity.dimension_ref`, `source_unit.dimension_ref`, and `target_unit.dimension_ref` in that order | `DIMENSION_MISMATCH` |
| `conversion_rule` | call `validate_conversion_rule(rule, source_unit, target_unit)` or faithfully reuse its ordered `factor_nonzero`, `offset_variant`, `direction`, `dimension`, and `validity_horizon` predicates; the rule dimension is thereby compared with both explicit unit dimensions | `CONVERSION_RULE_MISMATCH` |
| `exact_arithmetic` | `quantity.magnitude`, `rule.factor`, and `rule.offset`, through only the exact §21.3 operations | the existing exact-arithmetic refusal code |
| `reverse_not_explicit` | the explicit `source_unit`, explicit `target_unit`, and unchanged rule direction/endpoints; it is a named rejection witness of the `conversion_rule` check, not a hidden inverse path | `CONVERSION_RULE_MISMATCH` |

Constructor-owned formation still precedes these checks. Once formed inputs
reach the callable, no lookup, hidden state, fixture ID, patch/construction
history, inferred reference content, or literal-reference privilege may
affect the result.

For deterministic result projection and fixture generation, successful
`checked_predicates` tuples are frozen below. A failure includes the labels
through the first failed predicate and no later label. Unit conversion returns
the supplied rule's `conversion_ref`; region/boundary parent success returns
the supplied parent ref. Every other `conversion_rule_ref` or `parent_ref` is
typed `NOT_APPLICABLE`.

| Callable | Exact successful predicate-label tuple |
|---|---|
| `validate_dimension_compatibility` | `dimension_ref`, `basis_exponents` |
| `validate_unit_compatibility` | `dimension`, `unit_identity_or_conversion` |
| `validate_conversion_rule` | `factor_nonzero`, `offset_variant`, `direction`, `dimension`, `validity_horizon` |
| `validate_quantity` | `resolution`, `dimension`, `unit`, `resource_service_type`, `region`, `time_basis`, `sign_convention`, `boundary`, `uncertainty_applicability` |
| `validate_resource_service_compatibility` | `resource_declares_service`, `service_declares_resource` |
| `validate_region_compatibility` | `identity_or_parent`, `declared_parent_links`, `clock`, `validity_interval`, `distinct_children`, `aggregation_rule` |
| `validate_boundary_compatibility` | `identity_or_parent`, `declared_parent_links`, `state_schema`, `distortion`, `clock`, `horizon`, `cross_boundary_treatment`, `distinct_children`, `aggregation_rule` |
| `validate_sign_convention_compatibility` | `applicability`, `identity` |
| `validate_time_basis` | `applicability`, `identity` |
| `validate_clock_compatibility` | `clock_ref` |
| `validate_horizon` | `clock_refs`, `endpoint_order`, `endpoint_inclusion`, `resolution`, `measurement_epochs`, `post_terminal_effect_treatment`, `terminal_pending_treatment` |
| `validate_uncertainty_record` | `resolution`, `kind_fields`, `unit_coordinates`, `bound_order`, `provenance` |
| `validate_resolution_detail` | `state_payload_relation`, `tuple_order_and_disjointness` |
| `validate_object_envelope` | `exact_field_types`, `authority_ref_order`, `payload_canonical_bytes`, `lifecycle_status`, `direct_content_hash_exclusion`, `object_content_hash` |
| `validate_lifecycle_transition` | `closed_edge`, `authorization_applicability`, `evidence_order` |
| `validate_supersession_relation` | `logical_object_id`, `object_kind_id`, `schema_id`, `version_increase`, `content_change`, `lifecycle_pair`, `predecessor_not_in_own_ancestry`, `successor_not_in_ancestry`, `unique_linear_ancestry`, `ancestry_ends_at_predecessor`, `evidence_nonempty`, `authorization_applicable` |

Within I-2, branch/cycle ancestry is only the locally decidable property of
one proposed ordered `predecessor_supersedes_chain`: the tuple is linear and
duplicate-free, excludes the successor, and ends at the predecessor. Detecting
a competing registry relation requires I-4 lookup/mutation authority and is
not claimed by I-2.

### 21.7 Registry acceptance dependency resolution

The conservative resolution is normative:

1. I-2 implements only pure T0 lifecycle and immutable supersession
   validation.
2. Production mutation from draft/reviewed to accepted is deferred to I-4,
   after external authorization records, validation, and single-use handling
   exist.
3. `accept_registry_object` and `supersede_registry_object` are assigned to
   I-4 and are absent from the post-I-2 public API.
4. I-2 cannot synthesize an acceptance result, fabricate or bypass authority,
   or insert an accepted numerical policy into a production registry.
5. Existing I-1 `register_draft`, `resolve_ref`, and `resolve_alias` semantics
   remain unchanged. I-2 may replace `RegistryRecord.lifecycle_status: str`
   with exact `LifecycleStatus` while retaining `DRAFT` as the only status
   accepted by `register_draft`.

The only authorized I-2 change to `registry.py` is that type strengthening and
the minimal imports/checks it requires. Acceptance/supersession mutation is
not hidden there.

### 21.8 Validation contract

The future `numeric_vectors_v1.json` is the single ECJ-1 document determined
by §§21.8.1–21.8.5. It contains exactly 335 vectors. The first ID is
`i2-0001`; the terminal ID is `i2-0335`. Its bytes are exactly
`encode_ecj1(top_level_object)` with no trailing LF. Canonical top-level key
order is:

```text
fixture_class
implementation_plan_raw_sha256
schema_id
schema_version
specification_raw_sha256
vectors
```

Values are exactly `T0_STATIC_I2`, the eventual committed plan v0.2.7 raw
SHA-256 as 64 lowercase hexadecimal digits,
`ebu:fixture:validation:i2-numeric-vectors-v1`, `1.0.0`, the eventual
committed specification v0.1.7 raw SHA-256 in the same form, and the vector
array. The two hashes occur only in those two authority fields. This is not
self-reference: the fixture is a later I-2 artifact created after both
authority files are committed; the plan does not embed its own hash.

Each vector has canonical key order `case`, `category`, `expected`, `inputs`,
`operation`, `quantity_context`, `vector_id`. `category` is one of
`NORMAL_FORM`, `CONSTRUCTOR`, `EXACT_OPERATION`, `EXACT_CONVERSION`,
`POLICY_REFUSAL`, `COMPATIBILITY`, `ENVELOPE`, `LIFECYCLE`, `PRECEDENCE`.
`quantity_context` is the fully expanded catalog projection `QC0` only where
this section says so and otherwise the string `NOT_APPLICABLE`; the alias text
`QC0` is never written into the fixture.

Expected objects have one of these exact canonical key sets:

```text
VALUE         canonical_hex,outcome,projection,returned_type
COMPARISON    canonical_hex,outcome,projection
COMPATIBILITY canonical_hex,outcome,projection
FAILURE       failure_code,failure_id,failure_interface_ref,
              failure_ordinal,failure_stage,outcome
```

`NA` means the exact ECJ-1 string `NOT_APPLICABLE`. The four constructors are
exactly:

```text
VALUE(p,t) = {"canonical_hex":HEX_ECJ(p),"outcome":"VALUE",
              "projection":p,"returned_type":t}
COMPARISON(p) = {"canonical_hex":HEX_ECJ(p),"outcome":"COMPARISON",
                 "projection":p}
COMPATIBILITY(p) = {"canonical_hex":HEX_ECJ(p),
                    "outcome":"COMPATIBILITY","projection":p}
FAILURE(c,s,i) = {"failure_code":c,"failure_id":FAILURE_ID(c,s,i),
                  "failure_interface_ref":i,"failure_ordinal":0,
                  "failure_stage":s,"outcome":"FAILURE"}
IF(op) = {"interface_version":"1.0.0",
          "module":op with its final dot-component removed,
          "qualname":op's final dot-component}
```

`HEX_ECJ` and `FAILURE_ID` are the closed derivations below, not stored
formula text. `IF` is valid only for a fully qualified operation string in the
closed §21.8.5 table; both string operations have no `IF`. Failure object refs
are the empty tuple and event key is typed
`NOT_APPLICABLE`. Failure interface is either
`{"interface_version":"1.0.0","module":M,"qualname":Q}` from the closed
interface table or the string `NOT_APPLICABLE`. `failure_id` is the exact
§21.2.2 result for those coordinates; the generator writes the derived
64-digit ID, not a formula or placeholder. Unknown/duplicate keys, an extra,
missing, duplicated, reordered, or renumbered vector, or a derived-value
mismatch is nonconforming.

#### 21.8.1 Exact catalog and transport grammar

`ECJ(x)` means the unique ECJ-1 bytes of `x`; `HEX_ECJ(x)` means the lowercase
even-length hexadecimal encoding of `ECJ(x)`. These definitions are the exact
canonical-hex entries for every catalog projection below. All catalog text is
ASCII; no host Unicode or locale operation participates.

For `0 <= n <= 63`, in increasing integer order:

```text
R(n) = {
  "object_content_hash":"sha256:" + HEX2(n) repeated 32 times,
  "object_id":"ebu:fixture:validation:r" + HEX2(n),
  "object_version":"1.0.0"
}
SID(n) = "ebu:fixture:validation:s" + HEX2(n)
```

`HEX2` is exactly two lowercase hexadecimal digits. The ordered reference
catalog is `R(0)..R(63)` followed by `SID(0)..SID(63)`; each entry is the
projection shown and has canonical hex `HEX_ECJ(the projection)`.

The exact numeric projections and ordered numeric catalog are:

```text
I(x)   = {"value":x,"variant":"INTEGER_V1"}
Q(n,d) = {"denominator":d,"numerator":n,"variant":"RATIONAL_V1"}
D(c,e) = {"coefficient":c,"exponent10":e,"variant":"DECIMAL_V1"}
B(h)   = {"bits":h,"variant":"BINARY64_BITS_V1"}

I0=I(0), I1=I(1), I2=I(2), I3=I(3), I6=I(6), IN1=I(-1)
Q0=Q(0,1), Q12=Q(1,2), Q13=Q(1,3), Q34=Q(3,4), Q2=Q(2,1)
D0=D(0,0), D03=D(3,-1), D12=D(12,-1), D125M3=D(125,-3), D2=D(2,0)
BP0=B("0000000000000000"), BN0=B("8000000000000000")
B1=B("3ff0000000000000"), B2=B("4000000000000000")
```

Each catalog item has the displayed projection and
`canonical_hex=HEX_ECJ(projection)`. The finite binary64 basis, in order, is:

```text
0000000000000000 8000000000000000 0000000000000001
000fffffffffffff 0010000000000000 7fefffffffffffff
8000000000000001 800fffffffffffff 8010000000000000
ffefffffffffffff
```

The nonfinite basis, in order, is:

```text
7ff0000000000000 fff0000000000000 7ff8000000000000
fff8000000000000 7ff0000000000001 fff0000000000001
```

The finite basis detects disagreements at both signed zeros and both signs of
the subnormal, normal, and maximum-finite boundaries. The nonfinite basis
detects disagreements for both infinities and both signs of quiet/signaling
NaN. The general all-ones-exponent rule is established by constructor logic;
the finite vectors are not exhaustive proof over all 64-bit strings.

The primitive catalog uses the exact §21.4–§21.5 `to_ecj1()` field names,
always adds `schema_version:1`, projects tuples as arrays and `NA` as the
string `NOT_APPLICABLE`. Constructor expressions below are the projection
grammar, not Python calls:

```text
RES_PRESENT=(PRESENT,R(20),[],[],NA,NA,NA,NA)
RES_PENDING=(PENDING,NA,[],[],R(21),NA,NA,NA)
RES_FAILED=(FAILED,NA,[],[],NA,FAIL0,NA,NA)
RES_PARTIAL=(PARTIAL,NA,[R(22)],[R(23)],NA,NA,NA,NA)
RES_UNRESOLVED=(UNRESOLVED,NA,[],[],NA,NA,NA,R(24))
RES_OUT=(OUT_OF_BOUNDARY,NA,[],[],NA,NA,R(25),R(24))
RES_NA=(NOT_APPLICABLE,NA,[],[],NA,NA,NA,R(24))
DIM0=(R(0),PHYSICAL,[[R(1),Q(1,1)]])
DIM1=(R(2),PHYSICAL,[[R(1),Q(1,1)]])
UNIT_A=(R(3),R(0),BASE,"a",R(4),NA)
UNIT_B=(R(5),R(0),DERIVED,"b",R(6),NA)
UNIT_C=(R(7),R(0),DERIVED,"c",R(8),NA)
RULE_AB=(R(9),R(3),R(5),R(0),FORWARD_ONLY,Q2,NA,NA)
RULE_BC=(R(10),R(5),R(7),R(0),FORWARD_ONLY,Q2,Q(1,1),NA)
RULE_AFFINE=(R(11),R(3),R(5),R(0),FORWARD_ONLY,D2,D(1,0),NA)
RULE_BC_DEC=(R(60),R(5),R(7),R(0),FORWARD_ONLY,D2,D(1,0),NA)
QC0=(R(0),R(3),R(12),R(13),R(14),R(15),R(16),R(17),NOT_APPLICABLE)
QC_U=QC0 with uncertainty_applicability APPLICABLE
QTY0=(I2,R(3),R(0),R(17),R(12),R(13),R(14),R(15),R(16),NA,RES_PRESENT)
QTY1=QTY0 with magnitude I3
QTY_R=QTY0 with magnitude Q12
QTY_D=QTY0 with magnitude D12
QTY_U=QTY0 with uncertainty_ref R(63)
RESOURCE0=(R(12),R(0),R(18),[R(13)],NA)
SERVICE0=(R(13),R(19),[R(12)],R(0),NA)
CLOCK_A=(R(26),R(27),R(28),DISCRETE_TOTAL,NA)
CLOCK_B=(R(29),R(30),R(28),DISCRETE_TOTAL,NA)
INSTANT0=(R(26),I0); INSTANT2=(R(26),I2); DURATION1=(R(26),I1)
EPOCH0=(R(26),I0); EPOCH2=(R(26),I2)
REGION_P=(R(31),R(32),R(26),NA,PHYSICAL,INSTANT0,INSTANT2)
REGION_L=(R(33),R(34),R(26),R(31),PHYSICAL,INSTANT0,INSTANT2)
REGION_R=(R(35),R(36),R(26),R(31),PHYSICAL,INSTANT0,INSTANT2)
BOUNDARY_P=(R(37),R(38),R(39),R(26),R(40),R(41),R(42),
            NA,NA,NA,NA,[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[])
BOUNDARY_L=BOUNDARY_P with boundary_ref R(43), parent_boundary_ref R(37)
BOUNDARY_R=BOUNDARY_P with boundary_ref R(44), parent_boundary_ref R(37)
HORIZON0=(R(41),R(26),R(45),R(46),INSTANT0,INSTANT2,CLOSED,
          DURATION1,[EPOCH0,EPOCH2],REMAIN_PENDING,REQUIRE_NONE_PENDING)
METADATA0=(SID(3),R(47),R(48),R(49),R(50),R(51),R(52),R(53))
TRANSITION0=(R(54),DRAFT,REVIEWED,[R(55)],NA)
```

`QC0` and `QC_U` expand in the exact nine-field `QuantityContext` declaration
order; their final values are respectively the literal strings
`NOT_APPLICABLE` and `APPLICABLE`. `QTY_U` expands in the exact `Quantity`
field order. Alias text is never written into fixture bytes.

Each all-caps enum/status/kind token in this grammar projects as the identical
ASCII string. Each named record tuple expands by the corresponding exact field
order in §§21.4–21.5 and then adds `schema_version:1`; a catalog alias is fully
expanded before insertion. Parenthesized non-record inputs become arrays in
displayed order. No alias name, constructor notation, or patch instruction is
written into a successful projection.

`BOUNDARY_P/L/R` have the exact 28 §21.5.3 fields: seven required refs,
four conditional refs, the 16 listed collection fields, then
`cross_boundary_effect_treatments=[]`. No omitted field or alternate empty
collection is permitted. These empty baselines make the treatment-key set
equal the empty union of each baseline's two effect-ref sets.

The baseline payload is `PAYLOAD0=BYTES("7b2261223a317d")`, canonical bytes
for `{"a":1}`. `PAYLOAD1=BYTES("7b2261223a327d")` is canonical bytes for
`{"a":2}`, and `PAYLOAD_LIST=BYTES("7b2261223a5b315d7d")` is canonical bytes
for `{"a":[1]}`. `ENVELOPE(payload,hash,status,metadata)` is the exact fixture
input object with the eleven §21.5.6 field names and values
`SID(0),SID(1),SID(2),"1.0.0","1.0.0",[R(0)],NA,payload,hash,status,metadata`
in that field order. `ENVELOPE0=ENVELOPE(PAYLOAD0,HASH0,DRAFT,NA)`. `HASH0` is
exactly
`sha256:c44ef029ee7da9fcb13875d1e11a53a3768512aa58171677cd2e08f3eae0f548`,
the I-1 content hash of that logical payload and those preimage fields.
`HASH1` is exactly
`sha256:16e2f140f4b064c5833cdce029d92d170b5a5c2295e459b4d2d472b8fd90c438`
for `PAYLOAD1`; `HASH_LIST` is exactly
`sha256:dbb7229367b16470bcdbfc18e2fd73be2083ace6eca6106d93c13d771cbea8ea`
for `PAYLOAD_LIST`.

Successful-result helpers are exact projection constructors, fully expanded
before insertion:

```text
EZ={"bound_kind":"EXACT_ZERO","completeness":"COMPLETE","lower":I0,
    "policy_ref":NA,"schema_version":1,"unit_ref":NA,"upper":I0}
EB(k,l,u,unit,policy,c)={"bound_kind":k,"completeness":c,"lower":l,
    "policy_ref":policy,"schema_version":1,"unit_ref":unit,"upper":u}
EB_ABSOLUTE=EB(ABSOLUTE,Q0,Q12,R(3),R(60),COMPLETE)
EB_RELATIVE=EB(RELATIVE,D0,D03,NA,R(60),COMPLETE)
EB_ULP=EB(ULP,I0,I3,NA,R(60),COMPLETE)
EB_INTERVAL=EB(INTERVAL,I1,I3,R(3),R(60),COMPLETE)
EB_INCOMPLETE=EB(ABSOLUTE,Q0,Q12,R(3),R(60),INCOMPLETE)
NR(op,variants,value)={"completeness":"COMPLETE","error_bound":EZ,
  "operand_variants":variants,"operation":op,"policy_ref":NA,
  "rounding_evidence_ref":NA,"schema_version":1,"value":value}
CR(order)={"completeness":"COMPLETE","error_bound":NA,"ordering":order,
  "policy_ref":NA,"purpose":"EXACT_CORE","schema_version":1}
OK(labels,conversion,parent)={"checked_predicates":labels,"compatible":true,
  "conversion_rule_ref":conversion,"failure":NA,"parent_ref":parent,
  "schema_version":1}
LIFE_OK(transition)={"checked_predicates":["closed_edge",
  "authorization_applicability","evidence_order"],"failure":NA,
  "schema_version":1,"transition":transition,"valid":true}
SUPER_OK(relation)={"checked_predicates":["logical_object_id",
  "object_kind_id","schema_id","version_increase","content_change",
  "lifecycle_pair","predecessor_not_in_own_ancestry",
  "successor_not_in_ancestry","unique_linear_ancestry",
  "ancestry_ends_at_predecessor","evidence_nonempty",
  "authorization_applicable"],"failure":NA,"relation":relation,
  "schema_version":1,"valid":true}
ASSERT(label)={"assertion":label,"satisfied":true}
```

For a failed validator result, the fixture's expected value is `FAILURE`, not
a partially populated result record. `ASSERT` is fixture-only evidence and has
returned type `STATIC_ASSERTION_V1`; it is not a public framework projection.

`SUPER0` is `(R56v100,R56v101,SID(4),SID(4),SID(5),SID(5),ACCEPTED,
REVIEWED,[R56v090,R56v100],[R(57)],R(58))`. All three versioned refs use object ID
`ebu:fixture:validation:r38`; versions are `0.9.0`, `1.0.0`, `1.0.1`;
their digests are respectively `90`, `10`, and `11` repeated 32 times.
`FAIL0` is the complete default/pre-trace I-2 `FailureEnvelope` with code
`RESOLUTION_STATE_INVALID`, interface
`ebu_framework.primitives.ResolutionDetail/1.0.0`, ordinal zero, empty refs,
not-applicable event, and summary `fixture resolution failure`.

Invalid Python input uses only these exact transport objects:

```text
PY(type,value)={"python_value":{"type":type,"value":value}}
BYTES(hex)={"bytes_hex":hex}
PATCH(base,ops)={"literal":base,"patches":ops}
replace-or-append=["replace"|"append", JSON-Pointer, ECJ-1 value]
remove=["remove", JSON-Pointer]
```

Allowed `PY` types are `BOOL`, `FLOAT`, `INT_SUBCLASS`, `BYTES_SUBCLASS`,
`BYTEARRAY`, `MEMORYVIEW`, `DICT`, `LIST`, and `POLICY_PROVIDER_RAISES`.
The last type has the exact `POLICY0` properties and five protocol methods
that each raise `AssertionError("POLICY_METHOD_CALLED")`. Patch operations are applied in
array order to a deep copy of the named catalog projection. Array indexes are
decimal; object paths use RFC 6901 escaping. No patch may name a missing path
except `append` with final array index `-`. These transport objects are static
fixture data, not public framework types.

Every vector's `inputs` value is an array. Catalog records and successful
projections are recursively expanded; `PY`, `BYTES`, and `PATCH` remain the
displayed transport objects. A displayed input tuple becomes one array in the
same order. A displayed list is a nested array. An omitted optional argument
never disappears: the exact typed `NA` marker is written. Object fields use
the canonical ECJ-1 order at encoding. These rules, plus the block-specific
shapes below, are the only input translation rules.

#### 21.8.2 Exact sequence and numeric/policy blocks

Set `next_id=1`. Iterate the blocks and cases below in textual order. Emit
`i2-` plus four-digit decimal `next_id`, then increment. There is no filter or
conditional inclusion.

| Block | Category | Count | Closed ID range |
|---:|---|---:|---|
| 1 | `NORMAL_FORM` | 18 | `i2-0001`–`i2-0018` |
| 2 | `CONSTRUCTOR` | 35 | `i2-0019`–`i2-0053` |
| 3 | `EXACT_OPERATION` | 42 | `i2-0054`–`i2-0095` |
| 4 | `EXACT_CONVERSION` | 4 | `i2-0096`–`i2-0099` |
| 5 | `POLICY_REFUSAL` | 36 | `i2-0100`–`i2-0135` |
| 6 | `COMPATIBILITY` | 107 | `i2-0136`–`i2-0242` |
| 7 | `ENVELOPE` | 20 | `i2-0243`–`i2-0262` |
| 8 | `LIFECYCLE` | 41 | `i2-0263`–`i2-0303` |
| 9 | `PRECEDENCE` | 32 | `i2-0304`–`i2-0335` |

Block 1 order is `integer-zero`, `integer-negative`,
`rational-reduce-positive`, `rational-negative-denominator`, `rational-zero`,
`decimal-strip-positive`, `decimal-strip-negative`, `decimal-zero`, then
`binary-` plus the ten finite bit strings from §21.8.1. Raw constructor inputs
are `0`, `-1`, `(6,8)`, `(3,-4)`, `(0,-5)`, `(1200,-2)`, `(-1200,-2)`,
`(0,99)`, then each bit string. Expected projections are respectively I0,
`I(-1)`, `Q(3,4)`, `Q(-3,4)`, Q0, `D(12,0)`, `D(-12,0)`, D0, then the exact
`B(bits)` values. For `IntegerV1`, a bare integer is its one constructor
argument. For `RationalV1` and `DecimalV1`, each displayed bare integer expands
to `I(integer)` before becoming one of the two arguments. Binary input is its
one string argument. Returned types are `IntegerV1` for cases 1–2,
`RationalV1` for 3–5, `DecimalV1` for 6–8, and `Binary64BitsV1` for 9–18;
each expected object is `VALUE(projection,that exact type string)`.

Block 2 order is:

```text
integer-bool integer-subclass rational-wrong-numerator
rational-zero-denominator decimal-wrong-exponent binary-uppercase
binary-short binary-long binary-nonhex binary-positive-infinity
binary-negative-infinity binary-positive-qnan binary-negative-qnan
binary-positive-snan binary-negative-snan python-float-canonical-boundary
normalize-raw-dictionary normalize-number-subclass
```

Inputs are, in order, `PY(BOOL,"true")`, `PY(INT_SUBCLASS,"1")`,
`(PY(FLOAT,"1.0"),I2)`, `(I1,I0)`, `(I1,PY(BOOL,"true"))`,
`3FF0000000000000`, `000000000000000`, `00000000000000000`,
`000000000000000g`, then the six nonfinite strings in §21.8.1,
`PY(FLOAT,"1.0")`, `PY(DICT,{"a":1})`, and an integer subclass record.
The final integer subclass record is exactly `PY(INT_SUBCLASS,"1")`; its
operation, unlike case 2, is `normalize_core_number`.
Cases 1–9 and 17–18 fail `CORE_NUMBER_INVALID`; cases 10–15 fail
`NONFINITE_NUMBER_FORBIDDEN`; case 16 fails unchanged I-1
`FLOAT_FORBIDDEN`, stage `I-1`, interface `NOT_APPLICABLE`.

Block-2 cases 19–35 are this exact closed `ErrorBound` basis, in the displayed
order. Each `ErrorBound` input array is in declaration order
`[bound_kind,lower,upper,unit_ref,policy_ref,completeness]`. Each success is
`VALUE(the displayed fully expanded bound,"ErrorBound")`; each failure uses
the displayed code, stage `I-2`, and `IF(operation)`.

| Case | Exact input array | Operation | Expected |
|---|---|---|---|
| `error-bound-exact-zero-success` | `[EXACT_ZERO,I0,I0,NA,NA,COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `VALUE(EZ,"ErrorBound")` |
| `error-bound-absolute-success` | `[ABSOLUTE,Q0,Q12,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `VALUE(EB_ABSOLUTE,"ErrorBound")` |
| `error-bound-relative-success` | `[RELATIVE,D0,D03,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `VALUE(EB_RELATIVE,"ErrorBound")` |
| `error-bound-ulp-success` | `[ULP,I0,I3,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `VALUE(EB_ULP,"ErrorBound")` |
| `error-bound-interval-success` | `[INTERVAL,I1,I3,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `VALUE(EB_INTERVAL,"ErrorBound")` |
| `error-bound-binary64-refusal` | `[ABSOLUTE,BP0,B1,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF(operation))` |
| `error-bound-reversed-refusal` | `[INTERVAL,I3,I1,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-negative-refusal` | `[RELATIVE,IN1,I1,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-mixed-variant-refusal` | `[ABSOLUTE,I0,Q12,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF(operation))` |
| `error-bound-missing-policy-refusal` | `[ABSOLUTE,Q0,Q12,R(3),NA,COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF(operation))` |
| `error-bound-missing-unit-refusal` | `[ABSOLUTE,Q0,Q12,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(IMPLICIT_ABSENCE_FORBIDDEN,"I-2",IF(operation))` |
| `error-bound-relative-unit-refusal` | `[RELATIVE,D0,D03,R(3),R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-ulp-noninteger-refusal` | `[ULP,Q0,Q12,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-exact-zero-nonzero-refusal` | `[EXACT_ZERO,I0,I1,NA,NA,COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-exact-zero-unit-refusal` | `[EXACT_ZERO,I0,I0,R(3),NA,COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-exact-zero-policy-refusal` | `[EXACT_ZERO,I0,I0,NA,R(60),COMPLETE]` | `ebu_framework.numeric.ErrorBound` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |
| `error-bound-incomplete-bound-refusal` | `[I1,ADD,[INTEGER,INTEGER],NA,NA,EB_INCOMPLETE,COMPLETE]` | `ebu_framework.numeric.NumericalResult` | `FAILURE(ERROR_BOUND_INVALID,"I-2",IF(operation))` |

The last row constructs the structurally representable `EB_INCOMPLETE` and
then refuses it as the bound of a complete result. These 17 cases are the
complete finite `ErrorBound` basis for I-2; no other case is conditionally
selected. Every comparison is exact core comparison and no policy method is
called.

Block 3 first performs the closed nested iteration:

```text
operations=(ADD,SUBTRACT,MULTIPLY,DIVIDE,COMPARE)
cells=(INTEGER,RATIONAL,DECIMAL,BINARY64_BITS,MIXED)
for operation in operations:
    for cell in cells: emit matrix-<operation>-<cell>
for variant in (INTEGER,RATIONAL,DECIMAL,BINARY64_BITS):
    emit matrix-NEGATE-<variant>
```

Cell inputs are `(I6,I3)`, `(Q12,Q13)`, `(D12,D03)`, `(B1,B2)`, and
`(I6,Q13)`; negate inputs are I6, Q12, D12, B1. Expected values/failures are
the following closed table. `inputs` is exactly
`[operation,[expanded operands],NA]`; the third element is the
`exact_conversion` argument.

| Operation | Integer | Rational | Decimal | Binary64 bits | Mixed |
|---|---|---|---|---|---|
| `ADD` | `VALUE(NR(ADD,[INTEGER,INTEGER],I(9)),"NumericalResult")` | `VALUE(NR(ADD,[RATIONAL,RATIONAL],Q(5,6)),"NumericalResult")` | `VALUE(NR(ADD,[DECIMAL,DECIMAL],D(15,-1)),"NumericalResult")` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |
| `SUBTRACT` | `VALUE(NR(SUBTRACT,[INTEGER,INTEGER],I3),"NumericalResult")` | `VALUE(NR(SUBTRACT,[RATIONAL,RATIONAL],Q(1,6)),"NumericalResult")` | `VALUE(NR(SUBTRACT,[DECIMAL,DECIMAL],D(9,-1)),"NumericalResult")` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |
| `MULTIPLY` | `VALUE(NR(MULTIPLY,[INTEGER,INTEGER],I(18)),"NumericalResult")` | `VALUE(NR(MULTIPLY,[RATIONAL,RATIONAL],Q(1,6)),"NumericalResult")` | `VALUE(NR(MULTIPLY,[DECIMAL,DECIMAL],D(36,-2)),"NumericalResult")` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |
| `DIVIDE` | `VALUE(NR(DIVIDE,[INTEGER,INTEGER],I2),"NumericalResult")` | `VALUE(NR(DIVIDE,[RATIONAL,RATIONAL],Q(3,2)),"NumericalResult")` | `VALUE(NR(DIVIDE,[DECIMAL,DECIMAL],D(4,0)),"NumericalResult")` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |
| `COMPARE` | `COMPARISON(CR(GREATER))` | `COMPARISON(CR(GREATER))` | `COMPARISON(CR(GREATER))` | `FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` | `FAILURE(IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |

The unary cases use `inputs=[NEGATE,[operand],NA]` and expected values, in
variant order, `VALUE(NR(NEGATE,[INTEGER],I(-6)),"NumericalResult")`,
`VALUE(NR(NEGATE,[RATIONAL],Q(-1,2)),"NumericalResult")`,
`VALUE(NR(NEGATE,[DECIMAL],D(-12,-1)),"NumericalResult")`, and
`FAILURE(NUMERICAL_POLICY_REQUIRED,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))`. This produces
all 25 binary and four unary cells.

The final 13 Block-3 cases and exact `(inputs -> expected)` are:

```text
integer-nondivisible-no-conversion (I1,I2,NA)->IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN
integer-nondivisible-explicit-rational (I1,I2,INTEGER_DIVISION_TO_RATIONAL)->Q(1,2)
integer-divisible-unused-conversion (I6,I3,INTEGER_DIVISION_TO_RATIONAL)->NUMERICAL_OPERATION_UNSUPPORTED
rational-zero-divisor (Q12,Q0)->DIVISION_BY_ZERO
decimal-zero-divisor (D12,D0)->DIVISION_BY_ZERO
decimal-repeating-division (D(1,0),D(3,0))->NUMERICAL_POLICY_REQUIRED
binary-positive-zero-divisor (B1,BP0)->DIVISION_BY_ZERO
binary-negative-zero-divisor (B1,BN0)->DIVISION_BY_ZERO
wrong-unary-arity (NEGATE,[I1,I2])->CORE_NUMBER_INVALID
wrong-binary-arity (ADD,[I1])->CORE_NUMBER_INVALID
unknown-operation (POWER,[I1,I2])->NUMERICAL_OPERATION_UNSUPPORTED
unused-integer-conversion-on-add (ADD,[I1,I2],INTEGER_DIVISION_TO_RATIONAL)->NUMERICAL_OPERATION_UNSUPPORTED
decimal-conversion-flag-on-divide (DIVIDE,[D12,D03],DECIMAL_TO_RATIONAL)->NUMERICAL_OPERATION_UNSUPPORTED
```

These displayed triples are the exact input arrays. A two-item display gains
the final `NA` conversion marker. A successful value expands to the exact `NR`
wrapper with the operation and operand variants shown; the sole success is
`VALUE(NR(DIVIDE,[INTEGER,INTEGER],Q12),"NumericalResult")`.

Block 4 order and outcomes are `decimal-positive-exponent: D(12,2)->Q(1200,1)`,
`decimal-negative-exponent: D125M3->Q(1,8)`, `decimal-zero-to-rational: D0->Q0`, and
`decimal-wrong-type: I1->CORE_NUMBER_INVALID`. Each `inputs` is the one-item
array containing the expanded left side. The first three expected objects are
`VALUE` with returned type `RationalV1`; the fourth is `FAILURE` at the derived
I-2 interface.

`POLICY0` is the exact §21.4.1 projection: `schema_id` is
`ebu.numerical-policy/1`, followed in property order by `policy_ref=R(0)`,
`owning_domain_ref=R(1)`, variants `[INTEGER]`, operations `[ADD,COMPARE]`,
result map `[[ADD,INTEGER]]`, precision R(2), rounding NA, comparison tolerance
R(3), approximation NA, error bound NA, overflow/underflow/nonfinite R(4),
signed zero NA, backend R(5), cross-platform R(6), failure R(7), evidence
`[R(8),R(9)]`, runtime constraints `([R(10)],APPLICABLE,COMPLETE)`, and
declared `COMPLETE`. The nested runtime-constraint record expands with its
three named fields and `schema_version:1`.

Block 5 order is:

```text
complete-exact-policy declared-incomplete-policy missing-policy-ref
missing-owning-domain-ref owner-identity-equals-policy-identity empty-variants
duplicate-variants unordered-variants empty-operations duplicate-operations
unordered-operations missing-result-row duplicate-result-row extra-result-row
compare-result-row missing-precision-contract missing-binary-rounding-contract
missing-compare-tolerance-contract missing-approximation-contract
missing-error-bound-contract missing-nonfinite-contract
missing-binary-signed-zero-contract signed-zero-without-binary
missing-backend-contract missing-cross-platform-contract
missing-failure-contract empty-evidence duplicate-evidence unordered-evidence
missing-runtime-constraints applicable-empty-runtime-constraints
not-applicable-nonempty-runtime incomplete-runtime-constraints
false-complete-declaration policy-required-operation-refuses
policy-provider-never-invoked
```

Each of cases 1–34 has `inputs=[PATCH(POLICY0,ops)]`, where `ops` is exactly the
following list; `[]` means no patch. In the table, `replace P V`, `remove P`,
and `append P V` are exact shorthand for the transport arrays just defined,
and semicolons separate consecutive patch-array entries:

```text
BINARY_ADD_PATCHES = [
  ["replace","/supported_input_variants",["BINARY64_BITS"]],
  ["replace","/supported_operations",["ADD"]],
  ["replace","/result_variant_by_operation",[["ADD","BINARY64_BITS"]]]
]
```

When the table uses this name, those three arrays are copied in that order
into `ops`; the name is never written into the fixture.

| Cases | Exact patch operations in array order |
|---|---|
| 1 | `[]` |
| 2 | `replace /completeness "INCOMPLETE"` |
| 3, 4 | `remove /policy_ref`; `remove /owning_domain_ref` respectively |
| 5 | `replace /owning_domain_ref R(0)` |
| 6, 7, 8 | `replace /supported_input_variants []`; `[INTEGER,INTEGER]`; `[RATIONAL,INTEGER]` respectively |
| 9, 10, 11 | `replace /supported_operations []`; `[ADD,COMPARE,ADD]`; `[COMPARE,ADD]` respectively |
| 12, 13, 14, 15 | `replace /result_variant_by_operation []`; `[[ADD,INTEGER],[ADD,INTEGER]]`; `[[ADD,INTEGER],[SUBTRACT,INTEGER]]`; `[[ADD,INTEGER],[COMPARE,INTEGER]]` respectively |
| 16 | `remove /precision_contract_ref` |
| 17 | `BINARY_ADD_PATCHES`, then `replace /rounding_contract_ref NA` |
| 18 | `replace /comparison_tolerance_contract_ref NA` |
| 19 | `BINARY_ADD_PATCHES`, then `replace /approximation_contract_ref NA` |
| 20 | `BINARY_ADD_PATCHES`, then `replace /error_bound_contract_ref NA` |
| 21 | `remove /overflow_underflow_nonfinite_contract_ref` |
| 22 | `BINARY_ADD_PATCHES`, then `replace /signed_zero_contract_ref NA` |
| 23 | `replace /signed_zero_contract_ref R(11)` |
| 24, 25, 26 | remove `/backend_dependency_contract_ref`, `/cross_platform_contract_ref`, `/failure_contract_ref` respectively |
| 27, 28, 29 | replace `/evidence_requirement_refs` with `[]`, `[R(8),R(9),R(8)]`, `[R(9),R(8)]` respectively |
| 30 | `remove /runtime_constraints` |
| 31 | replace `/runtime_constraints` with `([],APPLICABLE,COMPLETE)` |
| 32 | replace it with `([R(10)],NOT_APPLICABLE,COMPLETE)` |
| 33 | replace it with `([R(10)],APPLICABLE,INCOMPLETE)` |
| 34 | `replace /precision_contract_ref NA` |

Case 1 expects `VALUE("COMPLETE","Completeness")`; case 2 expects
`VALUE("INCOMPLETE","Completeness")`. Cases 3–4, 16, 21, 24–26, and 30
fail `IMPLICIT_ABSENCE_FORBIDDEN`. Cases 5–15, 17–20, 22–23, 27–29, and 31–34
fail `NUMERICAL_POLICY_INCOMPLETE`. Case 35 has exact input
`[ADD,[B1,B2],NA]`. Case 36 has exact input
`[PY(POLICY_PROVIDER_RAISES,POLICY0),[ADD,[B1,B2],NA]]`; its operation is the
static orchestration string `STATIC_POLICY_NONINVOCATION`, which performs the
nested exact-operation call and asserts the provider's five methods remain
uncalled. Both expect `NUMERICAL_POLICY_REQUIRED` at the
`apply_exact_core_operation` I-2 interface. Block-5 `quantity_context` is QC0;
all earlier contexts are NA.

Case 5 is named `owner-identity-equals-policy-identity` and proves only the
exact declared-identity inequality. There is no placeholder-owner case or
fixture-only placeholder classification.

For `POLICY0`, case 16 structurally omits `precision_contract_ref` and
therefore represents forbidden implicit absence. Case 34 retains that field
but gives it the explicit typed value `NOT_APPLICABLE`; because precision is
required for this policy while `completeness` remains `COMPLETE`, the resulting
declaration is instead numerically incomplete. A validator determines either
outcome from the resulting declaration alone. Patch history, including whether
a value was removed or replaced, is never a validation input.

#### 21.8.3 Exact compatibility block

Block 6 concatenates the following rows. For each row, emit the success cases
in listed order, named `<prefix>-<success-name>`, then one case per predicate
or rejection label in the exact order printed in that row, named
`<prefix>-reject-<label>`. For rows that say “labels from §21.6,” use that
tuple's order. Resolution rejection labels are the seven state names and
uncertainty rejection labels are the eight kind names printed in their rows,
not the shorter successful-predicate tuples. A rejection applies the exact
patch after its label to the baseline fixed below. Counts sum to 107; these
rules also freeze every Block-6 case name and therefore every ID-to-case
mapping.

| Prefix | Success cases | Ordered predicate label -> exact patch -> code | Count |
|---|---|---|---:|
| `dimension` | `equal` using DIM0,DIM0 | `dimension_ref` -> right `/dimension_ref`=R(63) -> `DIMENSION_MISMATCH`; `basis_exponents` -> right `/basis_exponents/0/1`=Q(-1,1) -> `DIMENSION_MISMATCH` | 3 |
| `unit` | `identity` UNIT_A,UNIT_A,NA; `conversion` UNIT_A,UNIT_B,RULE_AB | `dimension` -> target `/dimension_ref`=R(63) -> `DIMENSION_MISMATCH`; `unit_identity_or_conversion` -> UNIT_A,UNIT_B,NA -> `UNIT_MISMATCH` | 4 |
| `conversion-rule` | `valid` `[RULE_AB,UNIT_A,UNIT_B]` | each rejection keeps UNIT_A and UNIT_B and patches only RULE_AB: `factor_nonzero` -> `/factor`=Q0; `offset_variant` -> `/offset`=D0; `direction` -> `/direction`=`SIDEWAYS`; `dimension` -> `/dimension_ref`=R(63); `validity_horizon` -> `/validity_horizon_ref`=`APPLICABLE`; all -> `CONVERSION_RULE_MISMATCH` | 6 |
| `convert` | `exact` `[QTY_R,UNIT_A,UNIT_B,RULE_AB]`; `affine` `[QTY_D,UNIT_A,UNIT_B,RULE_AFFINE]`; `compose-exact` `[QTY_R,UNIT_A,UNIT_B,RULE_AB,UNIT_C,RULE_BC]`; `compose-affine` `[QTY_D,UNIT_A,UNIT_B,RULE_AFFINE,UNIT_C,RULE_BC_DEC]` | six rejections in order: `quantity_valid` keeps explicit source UNIT_A and patches only QTY_R `/resolution`=RES_PENDING -> `RESOLUTION_STATE_INVALID`; `source_unit` keeps source UNIT_A and patches only QTY_R `/unit_ref`=R(63) -> `UNIT_MISMATCH`; `target_unit` keeps source UNIT_A and patches only UNIT_B `/dimension_ref`=R(63) -> `DIMENSION_MISMATCH`; `conversion_rule` keeps source UNIT_A and patches only RULE_AB `/source_unit_ref`=R(63) -> `CONVERSION_RULE_MISMATCH`; `exact_arithmetic` uses QTY0, UNIT_A, UNIT_B, unchanged RULE_AB -> `IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN`; `reverse_not_explicit` uses QTY_R with unit R(5), explicit source UNIT_B, target UNIT_A, and unchanged forward-only RULE_AB -> `CONVERSION_RULE_MISMATCH` | 10 |
| `quantity` | `valid` `[QTY0,QC0]`, then `valid-with-uncertainty` `[QTY_U,QC_U]` | the nine §21.6 labels against `[QTY0,QC0]`; replace respectively `/resolution`=RES_PENDING, `/dimension_ref`, `/unit_ref`, `/resource_type_ref`, `/region_ref`, `/time_basis_ref`, `/sign_convention_ref`, `/boundary_ref`, `/uncertainty_ref` with R(63); codes respectively `RESOLUTION_STATE_INVALID`, `DIMENSION_MISMATCH`, `UNIT_MISMATCH`, `QUANTITY_TYPE_MISMATCH`, `REGION_MISMATCH`, `TIME_BASIS_MISMATCH`, `SIGN_CONVENTION_MISMATCH`, `BOUNDARY_MISMATCH`, `UNCERTAINTY_RECORD_INVALID`; then `uncertainty-unexpected` input `[QTY_U,QC0]` and `uncertainty-required` input `[QTY0,QC_U]`, both -> `UNCERTAINTY_RECORD_INVALID` | 13 |
| `resource-service` | `symmetric` RESOURCE0,SERVICE0 | `resource_declares_service` -> RESOURCE0 `/service_compatibility_refs`=[]; `service_declares_resource` -> SERVICE0 `/required_resource_type_refs`=[R(63)]; both -> `QUANTITY_TYPE_MISMATCH` | 3 |
| `region` | `identity` REGION_L,REGION_L,NA,NA; `parent` REGION_L,REGION_R,REGION_P,R(59) | labels from §21.6; patches in label order: supplied parent=NA; right `/parent_region_ref`=R(63); right `/clock_ref`=R(63); parent `/validity_end/tick`=I1; replace right with REGION_L; aggregation=NA. `identity_or_parent` -> `REGION_MISMATCH`, the other five -> `INVALID_AGGREGATION` | 8 |
| `boundary` | `identity` BOUNDARY_L,BOUNDARY_L,NA,NA; `parent` BOUNDARY_L,BOUNDARY_R,BOUNDARY_P,R(59) | labels from §21.6; patches in label order: supplied parent=NA; right `/parent_boundary_ref`=R(63); right `/state_schema_ref`=R(63); right `/distortion_ref`=R(63); right `/clock_ref`=R(63); right `/horizon_ref`=R(63); right `/unresolved_cross_boundary_effect_refs`=[R(60)]; replace right with BOUNDARY_L; aggregation=NA. `identity_or_parent` -> `BOUNDARY_MISMATCH`, the other eight -> `INVALID_AGGREGATION` | 11 |
| `sign` | `both-na`; `same` R(16),R(16) | `applicability` -> R(16),NA; `identity` -> R(16),R(63); both -> `SIGN_CONVENTION_MISMATCH` | 4 |
| `time` | `nonrate-na`; `rate-same` R(15),R(15) | `applicability` -> rate true with NA,NA; `identity` -> rate true with R(15),R(63); both -> `TIME_BASIS_MISMATCH` | 4 |
| `clock` | `same` CLOCK_A,CLOCK_A | `clock_ref` -> CLOCK_A,CLOCK_B -> `CLOCK_MISMATCH` | 2 |
| `horizon` | `closed` `[HORIZON0,[]]`; `right-open` is the fully expanded `HORIZON0` with `/endpoint_inclusion`=`LEFT_CLOSED_RIGHT_OPEN`, `/post_terminal_effect_treatment`=`OUT_OF_BOUNDARY`, and `/terminal_pending_treatment`=`ALLOW_EXPLICIT_PENDING`, input beside pending effect/due pairs `[[R(60),R(61)]]` | labels from §21.6 use, in order: `replace /clock_ref R(63)`; `replace /start/tick I3`; `replace /endpoint_inclusion "OPEN"`; `replace /resolution/ticks I0`; `replace /measurement_epochs [EPOCH2,EPOCH0]`; `replace /post_terminal_effect_treatment "DROP"`; `replace /terminal_pending_treatment "UNKNOWN"`; all -> `HORIZON_INVALID` except `clock_refs` -> `CLOCK_MISMATCH` | 9 |
| `resolution` | one valid case for each state in order `PRESENT,PENDING,FAILED,PARTIAL,UNRESOLVED,OUT_OF_BOUNDARY,NOT_APPLICABLE` | in the same order: `replace /present_value_ref NA`; `replace /completed_part_refs [R(22)]`; `replace /failure NA`; `replace /missing_part_refs [R(22)]`; `replace /present_value_ref R(20)`; `replace /reason_ref NA`; `replace /present_value_ref R(20)`; all -> `RESOLUTION_STATE_INVALID` | 14 |
| `uncertainty` | one valid case for kinds in §5.5 order `EXACT,MEASUREMENT_INTERVAL,ADMISSIBLE_SET,ADVERSARIAL_SET,PROBABILITY_MODEL,MODEL_DISCREPANCY,UNKNOWN,OUT_OF_SET` | in the same order: `replace /resolution RES_PENDING`; `replace /lower QTY1`, then `replace /upper QTY0`; `replace /member_refs []`; `replace /probability_model_ref R(60)`; `replace /probability_model_ref NA`; `replace /provenance_refs []`; `replace /lower QTY0`; `replace /violated_contract_ref NA`; all -> `UNCERTAINTY_RECORD_INVALID` | 16 |

Rejection baselines are exact: `dimension-equal`; `unit-conversion` for both
unit rejections; `conversion-rule-valid`; the explicit convert input named in
each rejection; `[QTY0,QC0]` for the nine quantity predicate rejections and
the two exact mismatch inputs printed in the quantity row;
`resource-service-symmetric`;
`region-parent`; `boundary-parent`; the complete two-argument sign/time input
printed after the label; `clock-same`; `horizon-closed`; and the valid record
with the same state or kind for resolution/uncertainty. There is no baseline
selection by an implementer.

For non-convert prefixes, a success input is the expanded argument array
printed in the row; each rejection input is that array with the stated
argument projection patched. Each success expected value is
`COMPATIBILITY(OK(labels,conversion,parent))`, using the exact full successful
label tuple in §21.6. Unit conversion success sets `conversion` to the rule ref;
region/boundary parent success sets `parent` to the parent ref; all other
coordinates are NA. A failed case uses the displayed code at the derived I-2
interface and includes predicate labels only in runtime evidence, not in the
fixture's `FAILURE` expected object.

Exact and affine convert successes use RULE_AB/RULE_AFFINE with explicitly
supplied UNIT_A and UNIT_B. Composition successes interpret the six-item
input as two calls to `convert_quantity_exact`: first
`(quantity,UNIT_A,UNIT_B,first_rule)`, then
`(returned_quantity,UNIT_B,UNIT_C,second_rule)`. The fixture adapter must use
that supplied unit chain and must not invent, infer, or resolve a unit. Exact
expected quantities are QTY_R with magnitude Q(1,1), unit R(5); QTY_D with
magnitude D(34,-1), unit R(5); QTY_R with magnitude Q(3,1), unit R(7); and
QTY_D with magnitude D(78,-1), unit R(7), in success-case order. Each is
wrapped by `VALUE(expanded-quantity,"Quantity")`. The last two are checked
against `factor=f_BC*f_AB`, `offset=f_BC*o_AB+o_BC`. This is test orchestration
through the existing callable, not a new production composition path. Every
returned quantity preserves all coordinates except magnitude and unit ref.

Relative to the historical v0.1.6/v0.2.6 fixture, the only logical vector
changes are the `inputs` of `i2-0149` through `i2-0158`: each direct case
inserts UNIT_A or its explicitly named reverse source before the target, and
each composition case inserts UNIT_A before UNIT_B while reusing UNIT_B as
the explicit source of the second call. All ten IDs, case names, categories,
operations, quantity contexts, expected outcomes, failure codes, failure
coordinates/IDs, and successful projections remain unchanged. The two
top-level authority-hash fields change mechanically after v0.1.7 and v0.2.7
are finalized; there are zero added or removed vectors.

The source anchor also closes the historical effective-input ambiguity. In
`i2-0154`, the role equality graph contains
`quantity.unit_ref != source_unit.unit_ref` while
`source_unit.unit_ref == rule.source_unit_ref`; in `i2-0156`, it contains
`quantity.unit_ref == source_unit.unit_ref` while
`source_unit.unit_ref != rule.source_unit_ref`. Any bijective renaming of
opaque ref values preserves those role-position equalities and inequalities,
so the two cases cannot become equivalent under opaque-reference renaming.
They therefore witness `UNIT_MISMATCH` and `CONVERSION_RULE_MISMATCH`
respectively without fixture identity, lookup, inferred contents, or patch
history.

The exact quantity-row case order is:

```text
quantity-valid
quantity-valid-with-uncertainty
quantity-reject-resolution
quantity-reject-dimension
quantity-reject-unit
quantity-reject-resource_service_type
quantity-reject-region
quantity-reject-time_basis
quantity-reject-sign_convention
quantity-reject-boundary
quantity-reject-uncertainty_applicability
quantity-uncertainty-unexpected
quantity-uncertainty-required
```

The first two cases succeed with the complete `validate_quantity` predicate
tuple. The nine `quantity-reject-*` cases use `[PATCH(QTY0,[the table's one
exact replace]),QC0]`. Their fixture `quantity_context` is QC0. The
`valid-with-uncertainty` and `uncertainty-required` contexts are QC_U; the
`uncertainty-unexpected` context is QC0. Every QC0/QC_U value is fully
expanded before encoding.

The eight valid uncertainty tuples, in kind order and exact field order after
`uncertainty_ref`, are:

```text
EXACT:                (R(3),NA,NA,[],NA,NA,[R(62)],NA,RES_PRESENT)
MEASUREMENT_INTERVAL: (R(3),QTY0,QTY1,[],NA,R(62),[R(61)],NA,RES_PRESENT)
ADMISSIBLE_SET:       (NA,NA,NA,[R(60),R(61)],NA,NA,[R(62)],NA,RES_PRESENT)
ADVERSARIAL_SET:      (NA,NA,NA,[R(60),R(61)],NA,NA,[R(62)],NA,RES_PRESENT)
PROBABILITY_MODEL:    (R(3),NA,NA,[],R(60),NA,[R(62)],NA,RES_PRESENT)
MODEL_DISCREPANCY:    (R(3),QTY0,QTY1,[],NA,NA,[R(62)],NA,RES_PRESENT)
UNKNOWN:              (NA,NA,NA,[],NA,NA,[],NA,RES_UNRESOLVED)
OUT_OF_SET:           (R(3),NA,NA,[],NA,NA,[R(62)],R(62),RES_PRESENT)
```

Each tuple is preceded by `uncertainty_ref=R(59)` and its displayed kind.
The resulting expanded records are named `U_EXACT`, `U_MEASUREMENT_INTERVAL`,
`U_ADMISSIBLE_SET`, `U_ADVERSARIAL_SET`, `U_PROBABILITY_MODEL`,
`U_MODEL_DISCREPANCY`, `U_UNKNOWN`, and `U_OUT_OF_SET` in that order.
Block-6 `quantity_context` is QC0 for every `convert-*`; it is selected for
each `quantity-*` exactly by the preceding paragraph; all other Block-6 cases
use NA. Block 5 uses fully expanded QC0. Every occurrence therefore contains
the ninth `uncertainty_applicability` field.

#### 21.8.4 Envelope, lifecycle, and precedence blocks

Block 7 order is:

```text
envelope-valid-canonical-bytes envelope-source-mutation-invariant
envelope-parsed-tree-mutation-invariant envelope-dictionary-rejected
envelope-list-rejected envelope-bytearray-rejected
envelope-memoryview-rejected envelope-bytes-subclass-rejected
envelope-noncanonical-rejected envelope-malformed-rejected
envelope-duplicate-key-rejected envelope-nonfinite-rejected
envelope-invalid-unicode-rejected envelope-exact-hash
envelope-metadata-invariant envelope-lifecycle-invariant
envelope-byte-change-invalid envelope-byte-change-valid-different-hash
envelope-hash-mismatch envelope-no-decoded-cache
```

The exact inputs and outcomes are:

| Cases | Exact input array | Exact expected outcome |
|---|---|---|
| 1 | `[ENVELOPE0]` | `VALUE(ASSERT("STORES_EXACT_CANONICAL_BYTES"),"STATIC_ASSERTION_V1")` |
| 2 | `[{"envelope":ENVELOPE(PAYLOAD_LIST,HASH_LIST,DRAFT,NA),"mutation":["append","/a",2],"source":{"a":[1]}}]` | `VALUE(ASSERT("SOURCE_MUTATION_INVARIANT"),"STATIC_ASSERTION_V1")` |
| 3 | `[{"envelope":ENVELOPE0,"mutation":["replace","/a",2],"parsed_from":PAYLOAD0}]` | `VALUE(ASSERT("PARSED_TREE_MUTATION_INVARIANT"),"STATIC_ASSERTION_V1")` |
| 4–8 | `[ENVELOPE(v,HASH0,DRAFT,NA)]`, with `v` in order `PY(DICT,{"a":1})`, `PY(LIST,[1])`, `PY(BYTEARRAY,"7b2261223a317d")`, `PY(MEMORYVIEW,"7b2261223a317d")`, `PY(BYTES_SUBCLASS,"7b2261223a317d")` | `FAILURE(INVALID_ECJ1,"I-1",NA)` |
| 9–13 | `[ENVELOPE(BYTES(h),HASH0,DRAFT,NA)]`, with `h` from the invalid-byte list below | the corresponding I-1 `FAILURE` below |
| 14 | `[ENVELOPE0]` | `COMPATIBILITY(OK(the validate_object_envelope labels,NA,NA))` |
| 15 | `[ENVELOPE(PAYLOAD0,HASH0,DRAFT,R(47))]` | the same successful `COMPATIBILITY` |
| 16 | `[ENVELOPE(PAYLOAD0,HASH0,REVIEWED,NA)]` | the same successful `COMPATIBILITY` |
| 17 | `[ENVELOPE(BYTES("7b2261223a317c"),HASH0,DRAFT,NA)]` | `FAILURE(INVALID_ECJ1,"I-1",NA)` |
| 18 | `[ENVELOPE(PAYLOAD1,HASH1,DRAFT,NA)]` | `VALUE(ASSERT("VALID_BYTE_CHANGE_DIFFERENT_HASH"),"STATIC_ASSERTION_V1")` |
| 19 | `[ENVELOPE(PAYLOAD0,"sha256:0000000000000000000000000000000000000000000000000000000000000000",DRAFT,NA)]` | `FAILURE(HASH_MISMATCH,"I-2",IF("ebu_framework.envelopes.validate_object_envelope"))` |
| 20 | `[{"module_path":"src/ebu_framework/envelopes.py"}]` | `VALUE(ASSERT("NO_MUTABLE_DECODED_PAYLOAD_STATE"),"STATIC_ASSERTION_V1")` |

Case 2 first encodes the source shown, constructs the envelope, applies the
mutation to that original source list, and compares stored bytes/HASH_LIST.
Case 3 parses PAYLOAD0 to a separate tree, applies the mutation, discards that
tree, and compares stored bytes/HASH0. The test scripts are fixture
orchestration; neither mutation reaches an envelope field.

Invalid byte hex values are: noncanonical
`7b2262223a322c2261223a317d`, malformed `7b`, duplicate-key
`7b2261223a312c2261223a327d`, nonfinite `7b2261223a4e614e7d`, invalid UTF-8
`7b2261223aff7d`. Expected unchanged I-1 codes are respectively
`NONCANONICAL_ECJ1`, `INVALID_ECJ1`, `DUPLICATE_OBJECT_NAME`, `INVALID_ECJ1`,
`INVALID_ECJ1`; stage is I-1 and interface NA.

Metadata and lifecycle cases change only `record_metadata_ref` and
`lifecycle_status` and retain HASH0. Invalid byte change replaces terminal
`7d` with `7c`. Valid byte change replaces ASCII `1` with `2` and requires a
different recomputed hash. Hash mismatch stores `sha256:` plus 64 zeroes and
fails `HASH_MISMATCH` at
`ebu_framework.envelopes.validate_object_envelope/1.0.0`, stage I-2. The last
case is an AST assertion that no field, slot, closure, property, or cache in
`CommonObjectEnvelope` retains `dict`, `list`, or a decoded payload.

Block 8 first iterates the status tuple `(DRAFT,REVIEWED,ACCEPTED,SUPERSEDED,
REVOKED_BEFORE_EXECUTION)` row-major over `(from,to)`, producing 25 cases named
`lifecycle-<from>-to-<to>`. Exactly the five §21.5.7 edges succeed. Every
other cell fails `LIFECYCLE_TRANSITION_INVALID`. Each input is the one-item
array containing `(R(54),from,to,[R(55)],authorization)`, expanded as a
`LifecycleTransition`; `authorization` is NA exactly when `to` is DRAFT or
REVIEWED and R(58) otherwise. A valid edge expects
`COMPATIBILITY(LIFE_OK(expanded transition))`; every invalid cell expects the
derived I-2 `FAILURE`. This exact target rule also fixes invalid-cell bytes and
ensures no absence defect masks the graph result.

Immediately after those 25 cells, emit these three cases in this exact order:

| Case | Exact input array | Expected |
|---|---|---|
| `lifecycle-reject-evidence-empty` | `[PATCH(TRANSITION0,[["replace","/evidence_refs",[]]])]` | `FAILURE(LIFECYCLE_TRANSITION_INVALID,"I-2",IF("ebu_framework.envelopes.validate_lifecycle_transition"))` |
| `lifecycle-reject-evidence-duplicate` | `[PATCH(TRANSITION0,[["replace","/evidence_refs",[R(55),R(55)]]])]` | same failure coordinate and code |
| `lifecycle-reject-evidence-unsorted` | `[PATCH(TRANSITION0,[["replace","/evidence_refs",[R(56),R(55)]]])]` | same failure coordinate and code |

The cases respectively isolate nonemptiness, duplicate-freedom, and exact
lexicographic ordering. Supersession cases follow them.

The final 13 Block-8 cases are `supersession-valid`, followed by one rejection
for each successful predicate label in §21.6 order:

```text
logical_object_id object_kind_id schema_id version_increase content_change
lifecycle_pair predecessor_not_in_own_ancestry successor_not_in_ancestry
unique_linear_ancestry ancestry_ends_at_predecessor evidence_nonempty
authorization_applicable
```

The valid case input is `[SUPER0]` and expects
`COMPATIBILITY(SUPER_OK(SUPER0))`. Each rejection input is
`[PATCH(SUPER0,[the exact operation below])]`:

| Predicate/case suffix | Exact patch operation | Expected code |
|---|---|---|
| `logical_object_id` | `["replace","/successor_ref/object_id","ebu:fixture:validation:r3f"]` | `SUPERSESSION_INVALID` |
| `object_kind_id` | `["replace","/successor_object_kind_id",SID(63)]` | `SUPERSESSION_INVALID` |
| `schema_id` | `["replace","/successor_schema_id",SID(63)]` | `SUPERSESSION_INVALID` |
| `version_increase` | `["replace","/successor_ref/object_version","1.0.0"]` | `SUPERSESSION_INVALID` |
| `content_change` | `["replace","/successor_ref/object_content_hash","sha256:" + "10" repeated 32 times]` | `SUPERSESSION_INVALID` |
| `lifecycle_pair` | `["replace","/predecessor_status","REVIEWED"]` | `LIFECYCLE_TRANSITION_INVALID` |
| `predecessor_not_in_own_ancestry` | `["replace","/predecessor_supersedes_chain",[R56v090,R56v100,R56v100]]` | `SUPERSESSION_INVALID` |
| `successor_not_in_ancestry` | `["replace","/predecessor_supersedes_chain",[R56v090,R56v101,R56v100]]` | `SUPERSESSION_INVALID` |
| `unique_linear_ancestry` | `["replace","/predecessor_supersedes_chain",[R56v090,R56v090,R56v100]]` | `SUPERSESSION_INVALID` |
| `ancestry_ends_at_predecessor` | `["replace","/predecessor_supersedes_chain/1",R(63)]` | `SUPERSESSION_INVALID` |
| `evidence_nonempty` | `["replace","/relation_evidence_refs",[]]` | `SUPERSESSION_INVALID` |
| `authorization_applicable` | `["replace","/authorization_ref",NA]` | `IMPLICIT_ABSENCE_FORBIDDEN` |

The string concatenation in the `content_change` literal is resolved before
fixture construction to the exact 71-character digest string. Each failure
uses the derived I-2 supersession-validator interface. No alternative patch,
array position, reference, or digest conforms.

Block 9 first iterates the exact 24-code precedence list from §21.2.4 by
adjacent indexes `(0,1)` through `(22,23)`. Case name is
`adjacent-<higher>-before-<lower>`, operation `STATIC_PRECEDENCE_ORDER`, input
the two code strings, expected projection
`{"higher_precedence":higher,"lower_precedence":lower}`. No failure ID is
created because this is a static order assertion, not a fabricated public
boundary.

The last nine cases have these exact inputs and expected first failures. A
call pair is the two-element array `[operation-string,input-array]`; an ordered
batch is an array of call pairs evaluated from index zero and stopped at the
first failure.

| Case | Exact `inputs` array | Expected |
|---|---|---|
| `multiple-float-plus-absence` | `[["ebu_framework.canonical.encode_ecj1",[PY(FLOAT,"1.0")]],["ebu_framework.numeric.validate_numerical_policy",[PATCH(POLICY0,[["remove","/policy_ref"]])]]]` | `FAILURE(FLOAT_FORBIDDEN,"I-1",NA)` |
| `multiple-nonfinite-plus-zero-divisor` | `[["ebu_framework.numeric.Binary64BitsV1",["7ff0000000000000"]],["ebu_framework.numeric.apply_exact_core_operation",[DIVIDE,[B1,BP0],NA]]]` | `FAILURE(NONFINITE_NUMBER_FORBIDDEN,"I-2",IF("ebu_framework.numeric.Binary64BitsV1"))` |
| `multiple-mixed-plus-zero-divisor` | `[DIVIDE,[I1,Q0],NA]` | `FAILURE(DIVISION_BY_ZERO,"I-2",IF("ebu_framework.numeric.apply_exact_core_operation"))` |
| `multiple-missing-plus-incomplete-policy` | `[PATCH(POLICY0,[["remove","/policy_ref"],["replace","/supported_input_variants",[BINARY64_BITS]],["replace","/supported_operations",[ADD]],["replace","/result_variant_by_operation",[[ADD,BINARY64_BITS]]],["replace","/rounding_contract_ref",NA]])]` | `FAILURE(IMPLICIT_ABSENCE_FORBIDDEN,"I-2",IF("ebu_framework.numeric.validate_numerical_policy"))` |
| `multiple-dimension-plus-unit` | `[PATCH(QTY0,[["replace","/dimension_ref",R(63)],["replace","/unit_ref",R(63)]]),QC0]` | `FAILURE(DIMENSION_MISMATCH,"I-2",IF("ebu_framework.primitives.validate_quantity"))` |
| `multiple-region-plus-boundary` | `[PATCH(QTY0,[["replace","/region_ref",R(63)],["replace","/boundary_ref",R(63)]]),QC0]` | `FAILURE(REGION_MISMATCH,"I-2",IF("ebu_framework.primitives.validate_quantity"))` |
| `multiple-clock-plus-horizon` | `[PATCH(HORIZON0,[["replace","/start/clock_ref",R(63)],["replace","/endpoint_inclusion","OPEN"]]),[]]` | `FAILURE(CLOCK_MISMATCH,"I-2",IF("ebu_framework.primitives.validate_horizon"))` |
| `multiple-resolution-plus-uncertainty` | `[PATCH(U_EXACT,[["replace","/resolution",RES_PENDING],["replace","/lower",QTY1]])]` | `FAILURE(RESOLUTION_STATE_INVALID,"I-2",IF("ebu_framework.primitives.validate_uncertainty_record"))` |
| `multiple-lifecycle-plus-supersession` | `[PATCH(SUPER0,[["replace","/predecessor_status","REVIEWED"],["replace","/successor_ref/object_id","ebu:fixture:validation:r3f"]])]` | `FAILURE(LIFECYCLE_TRANSITION_INVALID,"I-2",IF("ebu_framework.envelopes.validate_supersession_relation"))` |

Every `IF` is fully expanded before encoding. Only the first two rows use an
ordered two-call batch; every other row is one public boundary with both
defects. No production composite validator is added.

#### 21.8.5 Exact derivation and closure rules

The `operation` and failure-interface table is closed:

| Cases | Exact operation string |
|---|---|
| integer/rational/decimal/binary normal or constructor | `ebu_framework.numeric.IntegerV1`, `RationalV1`, `DecimalV1`, or `Binary64BitsV1` selected by the case prefix |
| `normalize-*` | `ebu_framework.numeric.normalize_core_number` |
| `python-float-canonical-boundary` | `ebu_framework.canonical.encode_ecj1` |
| Block 2 cases 19–34 | `ebu_framework.numeric.ErrorBound` |
| Block 2 case 35 | `ebu_framework.numeric.NumericalResult` |
| Block 3 | `ebu_framework.numeric.apply_exact_core_operation` |
| Block 4 | `ebu_framework.numeric.decimal_to_rational_exact` |
| Block 5 cases 1–34 | `ebu_framework.numeric.validate_numerical_policy` |
| Block 5 case 35 | `ebu_framework.numeric.apply_exact_core_operation` |
| Block 5 case 36 | `STATIC_POLICY_NONINVOCATION` |
| Block-6 prefix `dimension`, `unit`, `conversion-rule`, `convert`, `quantity`, `resource-service`, `region`, `boundary`, `sign`, `time`, `clock`, `horizon`, `resolution`, `uncertainty` | the correspondingly ordered callable `validate_dimension_compatibility`, `validate_unit_compatibility`, `validate_conversion_rule`, `convert_quantity_exact`, `validate_quantity`, `validate_resource_service_compatibility`, `validate_region_compatibility`, `validate_boundary_compatibility`, `validate_sign_convention_compatibility`, `validate_time_basis`, `validate_clock_compatibility`, `validate_horizon`, `validate_resolution_detail`, `validate_uncertainty_record` in `ebu_framework.primitives`; the convert adapter dispatches four-item inputs directly and six-item composition inputs as two consecutive four-argument calls over the supplied unit chain |
| Block 7 cases 1–13 | `ebu_framework.envelopes.CommonObjectEnvelope` |
| Block 7 cases 14–20 | `ebu_framework.envelopes.validate_object_envelope` |
| lifecycle cells | `ebu_framework.envelopes.validate_lifecycle_transition` |
| supersession cases | `ebu_framework.envelopes.validate_supersession_relation` |
| adjacent precedence | `STATIC_PRECEDENCE_ORDER` |
| multiply-invalid | operation string of the higher-precedence source case |

For an ordinary I-2 failure, `IF(operation)` supplies the interface. The
static noninvocation case and ordered batches instead use the explicitly named
nested failing operation. Interface version is `1.0.0`. I-1 canonical
failures use interface NA. Module, qualname, stage, code, empty refs, NA event,
and ordinal zero are the complete FailureId coordinates.

Successful numeric projections are derived only by the exact §21.3 integer
algebra. Exact result wrappers use the §21.4.1 `EXACT_ZERO` error bound,
typed NA policy/rounding, and `COMPLETE`. Comparison uses `EXACT_CORE`, typed
NA policy/error bound, and `COMPLETE`. Compatibility/lifecycle/supersession
success projections use the exact fields and predicate labels in §§21.5–21.6.
Every successful projection is inserted literally into the generated vector
and its hex is `HEX_ECJ(projection)`.

`returned_type` is the exact public type name of the projected numeric,
`ErrorBound`, or Quantity result. Policy cases 1–2 use `Completeness`; every `ASSERT` projection
uses `STATIC_ASSERTION_V1`. Matrix compare uses the `COMPARISON` shape;
validators returning `CompatibilityResult`, `LifecycleValidationResult`, or
`SupersessionValidationResult` use `COMPATIBILITY`. No other returned-type
label is permitted.

Generation uses ordered arrays and the loop orders printed above. It uses no
dictionary/set traversal, locale, host Unicode behavior, filesystem order,
time, randomness, network, implementation-selected value, or unspecified
default. After substituting only the two committed authority hashes, two
implementations of this recipe must yield byte-identical `ECJ(top_level)`.
The generator must assert the nine block counts, total 335, first/terminal
IDs, gap-free order, unique cases, derived failure IDs, and every canonical
hex before writing.

The exact derived structural totals are block counts
`18,35,42,4,36,107,20,41,32`, 335 vectors, IDs `i2-0001` through
`i2-0335`, 335 unique IDs, 335 unique cases, 121 success/static projections,
and 214 failures. The final prospective byte count, fixture SHA-256, and
two-route identity are computed and reported externally only after the
specification hash is installed in the plan and the plan's external raw hash
is known. They are not embedded here because the fixture binds both document
hashes and the specification must not recursively bind the fixture digest.
The document-authority hashes remain the only values inserted into the future
fixture's two authority fields; the prospective fixture digest is not an
authority input.

Unbounded integers, the infinite rational/decimal domains, the full binary64
bit space, and arbitrary ancestry graphs are governed by the mathematical
constructor/predicate rules. The declared finite bases detect implementation
disagreement but do not constitute empirical proof over an infinite domain.

The I-2 portion of V3 is limited to static construction and projection of
`CommonObjectEnvelope` with exact canonical payload bytes and no decoded
cache, `RecordMetadata`, `LifecycleTransition`, `SupersessionRelation`, and
the strengthened draft-only `RegistryRecord`.
Configuration, binding, state, action, policy memory, fault, result,
authorization, and artifact records remain I-3 or later and are unreachable.

The I-2 AST/import/export audit reads source as bytes/text and uses AST only;
it imports no production module. It verifies the exact root export tuple and
count frozen by plan v0.2.7, module `__all__` subsets, the exact 29-edge DAG
in that plan and its acyclicity, no dynamic imports, no module-local failure
enum/string code, and no imports or calls reaching scientific modules, legacy
experiment/runner/finalizer modules, `results/`, or any Gate path. It proves
that `envelopes.py` imports exactly `CanonicalBytes` and `parse_ecj1` from
`canonical`, imports neither `encode_ecj1` nor canonical internals nor
`registry`, and retains no decoded mutable tree. It also proves no package,
dependency, network, subprocess, T1 mutation, T2 fixture evaluation, or T3
operation is reachable. `tests/framework/safety.py` remains unchanged; the
new tests perform this exact I-2 audit directly and may reuse its existing
guards without extending it.

No framework module import, test runner, package hook, build, installation,
policy method, model function, trajectory, or scientific operation is part of
this authority-amendment validation.

#### 21.8.6 Complete public-record closure audit

The prospective I-2 authority has been re-audited across every public record
used by the 335 vectors or the static supplement, not only the repaired
coordinates. Every concrete record remains an immutable
`dataclass(frozen=True,slots=True)` and every public I-2 callable and
constructor is T0. In the tables below, `C(T)` means the constructor failure
interface `ebu_framework.<owner>.T/1.0.0`; `V(f)` means the public validator
interface `ebu_framework.<owner>.f/1.0.0`. Constructor formation means exactly
the named required arguments are present, immutable storage is established,
an exact tuple rather than a mutable sequence is supplied where named, and
the exact runtime member types named in the formation column are supplied;
there is no coercion, subclass acceptance, `None`, hidden sentinel, unchecked
flag, or post-construction mutation. A closed string domain or cross-field
relation is not a formation check unless the table assigns it to construction.

| Owner and public record | Exact construction-time formation checks and owner | Exact explicit-validator checks and owner | Can a semantically invalid but structurally well-formed candidate exist? Exact coverage |
|---|---|---|---|
| `errors.FailureId` | Exact `str` and the §21.2.1 failure-ID lexical grammar; `C(FailureId)` | None | No after construction; all 214 derived failure IDs and `failure-support-nonempty-coordinate` |
| `errors.FailureInterfaceRef` | Three required exact strings, nonempty ASCII/no control or whitespace, semantic-version lexical form; `C(FailureInterfaceRef)` | None | No; every derived I-2 `IF(...)` and the supplement interface |
| `errors.FailureObjectRef` | Three required exact strings and the copied scientific-ID, semantic-version, and content-hash lexical grammars; `C(FailureObjectRef)` | None | No; nonempty-coordinate supplement |
| `errors.FailureEventKey` | Seven required fields, exact non-boolean integers, integer ranges, and the copied ID/event lexical grammars; `C(FailureEventKey)` | None | No; four named event-key supplement cases and all derived fixture coordinates |
| `errors.FailureEvidenceRef` | Three required fields; exact kind, kind-specific digest domain, and locator union/lexical form; `C(FailureEvidenceRef)` | None | No; `FAIL0`, raw-source success/refusal, and nonempty-coordinate supplement |
| `errors.CanonicalTraceState` | Four required exact union fields and all applicability/completeness/count/durable-prefix relations; `C(CanonicalTraceState)` | None | No; `FAIL0` and nonempty-coordinate supplement |
| `errors.FailureEnvelope` | Exact fifteen-field types, tuple member types/order/uniqueness, summary text, stage/advance/trace relations, and §21.2.2 derived ID equality; `C(FailureEnvelope)` through the private `_fail`/`FrameworkError` boundary | None | No; `FAIL0`, all 214 fixture failures, and nonempty-coordinate supplement |
| `numeric.IntegerV1` | Exact non-boolean built-in `int`; `C(IntegerV1)` | None | No; Blocks 1–4 and all nested numeric records |
| `numeric.RationalV1` | Two exact `IntegerV1` fields, nonzero denominator, and intrinsic sign/GCD/zero normalization; `C(RationalV1)` | None | No; Blocks 1–4 and nested factors, quantities, and bounds |
| `numeric.DecimalV1` | Two exact `IntegerV1` fields and intrinsic trailing-zero/zero normalization; `C(DecimalV1)` | None | No; Blocks 1–4 and nested factors, quantities, and bounds |
| `numeric.Binary64BitsV1` | Exact built-in `str`, sixteen lowercase hex digits, and finite exponent; `C(Binary64BitsV1)` | None | No; Blocks 1–3, 5, and nonfinite precedence |
| `numeric.RuntimeConstraintSet` | Three required fields, exact tuple/member and enum types only; `C(RuntimeConstraintSet)` | Applicable/nonapplicable tuple relation, nonempty/order/uniqueness, and completeness are nested policy-completeness checks at `V(validate_numerical_policy)` | Yes; `POLICY0` and Block-5 cases 31–33 |
| `numeric.QuantityContext` | Nine required fields with exact ref/conditional-union/applicability runtime types; `C(QuantityContext)` | Its agreement with a `Quantity`, including uncertainty applicability, is owned by `V(validate_quantity)`; policy shape merely projects the supplied context | Yes; QC0/QC_U in Blocks 5–6 and the two quantity uncertainty mismatch cases |
| `numeric.OperandValidationResult` | Seven required exact field/container types plus `valid`/`completeness`/`failure` result consistency; `C(OperandValidationResult)` | None | No after construction; `operand-validation-result-valid` supplement |
| `numeric.ErrorBound` | All six required fields and every exact kind, applicability, variant, policy, unit, completeness, nonnegativity, and order rule in §21.4.1; this constructor is itself the frozen operation, `C(ErrorBound)` | None | An explicitly `INCOMPLETE` refusal/evidence record may exist, but it is not a complete bound; Block-2 cases 19–34 and `EB_INCOMPLETE` |
| `numeric.NumericalResult` | Seven required exact fields and exact-core/result completeness, policy/rounding, and complete-bound relations; `C(NumericalResult)` | None | No invalid constructed result; Block-2 case 35 and Block-3 success projections |
| `numeric.ComparisonResult` | Six required exact fields and ordering/purpose/policy/bound/completeness relations; `C(ComparisonResult)` | None | No invalid constructed result; three Block-3 comparison successes |
| `numeric.NumericalPolicyV1` protocol declaration | No concrete public record constructor exists. The fixture adapter creates an ordinary read-only property provider from the resulting declaration; it is never a raw mapping and never claims protocol conformance before validation. | Property availability/runtime types, tuple order/uniqueness, result-map closure, exact inequality of declared policy/owner identities, all unconditional and conditional applicability (including mandatory tolerance-ref presence for `COMPARE`), nested runtime constraints, and declared completeness; `V(validate_numerical_policy)`. It resolves no ref or lifecycle/kind/role/content. | Yes, necessarily; all Block-5 cases 1–34. Missing properties reach the validator as absent provider attributes and explicit `NOT_APPLICABLE` values remain present typed values. Its five methods are never invoked. |
| `primitives.CompatibilityResult` | Five required exact fields and compatible/failure/ref result consistency; `C(CompatibilityResult)` | None | No invalid constructed result; all Block-6 successes and Block-7 case 14–16 success projections |
| `primitives.Dimension` | Three required exact fields; closed kind; exact nonempty tuple of exact `(ObjectRef,RationalV1)` pairs, ordered/unique refs, nonzero exponents; `C(Dimension)` | Pairwise ref and complete-basis equality; `V(validate_dimension_compatibility)` | Yes relative to another dimension; all `dimension-*` cases and nested dimension catalog values |
| `primitives.Unit` | Six required exact fields; closed kind, nonempty NFC symbol, and exact ref/conditional-union types; `C(Unit)` | Dimension then exact identity or supplied conversion relation; `V(validate_unit_compatibility)`. `convert_quantity_exact` additionally compares the quantity ref with its explicit source unit and compares quantity/source/target dimensions before rule validation. | Yes relative to another unit/rule; all `unit-*` and `convert-*` cases. Every convert case supplies source and target units explicitly. |
| `primitives.ConversionRule` | Eight required fields; exact ref/numeric/string/conditional-union runtime types only; `C(ConversionRule)` | `factor_nonzero`, `offset_variant`, direction/orientation against the two supplied units, three-way dimension equality, and exact horizon-union form; `V(validate_conversion_rule)` and the same ordered checks inside unit validation and `convert_quantity_exact` | Yes; all six `conversion-rule-*` cases supply `[rule,source_unit,target_unit]`, and all `convert-*` cases supply the rule with explicit source/target units. The standalone dimension rejection patches only the rule's declared dimension; `i2-0156` patches only the rule source ref. |
| `primitives.Quantity` | Eleven required fields and exact core/ref/conditional-union/`ResolutionDetail` runtime types only; `C(Quantity)` | The nine ordered quantity-context predicates at `V(validate_quantity)`; intrinsic required state, then exact unit identity against the explicit source, are the first checks inside `convert_quantity_exact` | Yes; all `quantity-*`, `convert-*`, and nested uncertainty cases. `i2-0154` changes only the quantity unit ref while the explicit source remains UNIT_A. |
| `primitives.ResourceType` | Five required exact fields and exact ordered, duplicate-free tuple/member and conditional-union types; `C(ResourceType)` | Symmetric service declaration; `V(validate_resource_service_compatibility)` | Yes relative to a service; all `resource-service-*` cases |
| `primitives.ServiceType` | Five required exact fields and exact nonempty ordered, duplicate-free tuple/member and conditional-union types; `C(ServiceType)` | Symmetric resource declaration; `V(validate_resource_service_compatibility)` | Yes relative to a resource; all `resource-service-*` cases |
| `primitives.SignConvention` | Five required exact fields; nonempty NFC meanings and pairwise distinction; `C(SignConvention)` | Ref applicability/identity only, on refs rather than records; `V(validate_sign_convention_compatibility)` | The record itself is complete after construction, but two refs may be incompatible; `sign-*` fixture cases and both sign supplement cases |
| `primitives.Region` | Seven required fields; exact runtime types, closed spatial domain, and parent-not-self; `C(Region)` | The six ordered identity/common-parent predicates, including exact declared parent links but excluding membership-rule resolution or disjointness; `V(validate_region_compatibility)` | Yes relative to other records/arguments; all `region-*` cases. The first rejection supplies typed `NOT_APPLICABLE`, not an `ObjectRef` in the `Region | Applicability` argument. |
| `primitives.AccountingBoundary` | Twenty-eight required fields, exact ref/conditional-union types, exact ordered duplicate-free tuple/member types, and exact ordered unique effect/treatment pairs; `C(AccountingBoundary)` | The nine ordered identity/common-parent predicates, including exact declared parent links and exact supplied effect-key coverage; `V(validate_boundary_compatibility)` | Yes relative to other records/arguments; all `boundary-*` cases. Empty baselines have empty maps; the unresolved-effect rejection leaves that map empty and fails coverage. The first rejection supplies typed `NOT_APPLICABLE`, not an `ObjectRef` in the parent argument. |
| `primitives.ClockSystem` | Five required exact fields, exact `DISCRETE_TOTAL`, and exact conditional-union type; `C(ClockSystem)` | Pairwise clock-ref equality; `V(validate_clock_compatibility)` | Yes relative to another clock; all `clock-*` and nested horizon cases |
| `primitives.Instant` | Exact `ObjectRef` and `IntegerV1`, with intrinsic nonnegative tick; `C(Instant)` | Cross-clock and endpoint order are owned by `V(validate_horizon)` | Yes relative to a horizon; all horizon catalog and cases |
| `primitives.Duration` | Exact `ObjectRef` and `IntegerV1` only; `C(Duration)` | Same-clock and strictly-positive horizon resolution are predicate `clock_refs`/`resolution` at `V(validate_horizon)` | Yes; `horizon-reject-resolution` constructs the exact zero-tick candidate and reaches `V(validate_horizon)` |
| `primitives.Epoch` | Exact `ObjectRef` and nonnegative `IntegerV1`; `C(Epoch)` | Cross-clock, strict ordering, and included-interval checks are predicate `measurement_epochs` at `V(validate_horizon)` | Yes relative to a horizon; all horizon measurement-epoch cases |
| `primitives.Horizon` | Eleven required fields and exact record/ref/string/tuple member runtime types only; `C(Horizon)` | All seven ordered horizon predicates plus formation/order/unique-key checks for the supplied exact effect/due-ref pairs; `V(validate_horizon)` | Yes; all nine `horizon-*` cases, including the right-open declared pair and invalid closed-domain strings that remain exact strings; global completeness is not claimed |
| `primitives.ResolutionDetail` | Eight required fields and exact enum/ref/tuple/failure union runtime types only; `C(ResolutionDetail)` | `state_payload_relation` and `tuple_order_and_disjointness`; `V(validate_resolution_detail)` | Yes; all fourteen `resolution-*` cases and invalid nested resolution candidates consumed first by quantity, conversion, uncertainty, and precedence validators |
| `primitives.UncertaintyRecord` | Eleven required fields and exact enum/ref/quantity/tuple/resolution runtime types only; `C(UncertaintyRecord)` | The five ordered kind/state/unit/bound/provenance predicates, including exact kind-specific violated-contract role and identity; `V(validate_uncertainty_record)` | Yes; all sixteen `uncertainty-*` cases and the two quantity-context uncertainty mismatches |
| `envelopes.CommonObjectEnvelope` | Eleven required properties and immutable capture; exact built-in payload bytes (no subclass or mutable/container substitute) and a successful unchanged `parse_ecj1` canonical parse are constructor formation owned by the frozen `CommonObjectEnvelope` operation. These raw-input failures retain their I-1 code/stage and not-applicable interface. | `exact_field_types` for the remaining stored fields and captured payload representation, `authority_ref_order`, an independent fresh-parse `payload_canonical_bytes` integrity check, `lifecycle_status`, `direct_content_hash_exclusion`, and `object_content_hash`; `V(validate_object_envelope)`. Direct exclusion recursively detects the exact stored hash string only; it performs no alias, ref, registry, or graph traversal. | Yes for validator-owned semantics. Block-7 cases 1–13 are constructor-boundary formation cases; structurally formed cases 14–16 and 18–19 reach the validator; case 17 reaches and fails the constructor prerequisite because its bytes are malformed; case 20 is the no-cache AST assertion. Hash mismatch reaches only the final validator predicate; metadata/lifecycle variations remain successful and excluded from the hash. |
| `envelopes.RecordMetadata` | Eight required exact ID/ref/conditional-union fields; `C(RecordMetadata)` | None; it has no scientific projection or acceptance meaning | No additional semantic validity is claimed; `record-metadata-valid` supplement and Block-7 metadata ref |
| `envelopes.LifecycleTransition` | Five required fields and exact ref/status/tuple-member/authorization-union runtime types only; `C(LifecycleTransition)` | `closed_edge`, `authorization_applicability`, and all evidence requirements under `evidence_order`; `V(validate_lifecycle_transition)` | Yes; all 25 graph cells and three evidence rejections form candidates and reach that validator |
| `envelopes.LifecycleValidationResult` | Four required exact fields plus valid/failure/checked-predicate consistency; `C(LifecycleValidationResult)` | None | No invalid constructed result; five Block-8 lifecycle success projections |
| `envelopes.SupersessionRelation` | Exactly the eleven required fields in §21.5.7 and exact ref/ID/status/tuple-member/authorization-union runtime types only; `C(SupersessionRelation)` | All twelve ordered supersession predicates, including direct predecessor/successor kind and schema equality and explicit authorization applicability; `V(validate_supersession_relation)` | Yes; the valid case and all twelve isolated rejections form candidates and reach that validator |
| `envelopes.SupersessionValidationResult` | Four required exact fields plus valid/failure/checked-predicate consistency; `C(SupersessionValidationResult)` | None | No invalid constructed result; `supersession-valid` success projection |
| `registry.RegistryRecord` | Existing I-1 fields plus exact `LifecycleStatus`; draft-only record construction and unchanged value parsing; `C(RegistryRecord)` with `REGISTRY_RECORD_CONFLICT` for nondraft | `register_draft` retains the same draft-only registry acceptance boundary and adds no mutation here | A nondraft constructor candidate is refused rather than retained; both named registry supplement cases |

The 16 closed public enums, `CoreNumberV1` union, and
`NumericalPolicyV1` method signatures retain their exact §21.2–§21.6 domains.
They are types rather than additional public records and are covered by the
static member/signature assertions below. No validator silently reconstructs
a record, catches a constructor failure and relabels it, consults patch
history, or invokes `__new__`, mutation, an unchecked/test mode, a registry,
an envelope lookup, a dynamic import, or other external state.

The complete fixture reachability audit is closed as follows:

| Block | Candidate construction and exact public boundary reached | Audit result |
|---:|---|---|
| 1 | Intrinsic numeric constructors | All 18 reach their named constructor and produce the frozen normal forms. |
| 2 | Numeric, bound, and result constructors, plus the unchanged I-1 canonical boundary | All 35 reach the operation in §21.8.5; each malformed constructor input fails there and `EB_INCOMPLETE` forms before `NumericalResult` refuses it. |
| 3 | Already formed core operands reach `apply_exact_core_operation` | All 42 reach the exact-operation interface; arity, operation, zero, mixed variant, conversion, and policy predicates retain precedence. |
| 4 | Already formed numeric candidates reach `decimal_to_rational_exact` | All four reach that interface; the wrong exact union member is rejected there. |
| 5 | Read-only declaration providers reach `validate_numerical_policy`; exact operands reach the core operation | All 36 reach their declared boundary. Missing properties and present typed-not-applicable properties remain distinguishable from resulting declaration shape alone; no policy method is called. |
| 6 | Signature-correct immutable record candidates reach the 13 named primitive validators or `convert_quantity_exact` | All 107 reach their declared boundary. Standalone conversion-rule cases supply the rule and both units; all ten quantity conversions supply explicit source/target units, and composition uses only the supplied unit chain; both parent validators receive typed parent arguments; horizon cases supply exact effect/due-ref pairs; and uncertainty records include the explicit violated-contract role. Every patch preserves the declared runtime signature; named semantic predicates, including zero duration and invalid closed-domain strings, are validator-owned. |
| 7 | Cases 1–13 reach the `CommonObjectEnvelope` formation boundary; cases 14–16 and 18–19 first form and then reach `validate_object_envelope`; case 17 reaches the constructor prerequisite and case 20 reaches the static AST assertion | All 20 retain their intended owner. Case 17's malformed bytes fail at construction with unchanged I-1 identity even though the orchestration operation is the validator; constructor byte/type/canonical failures cannot be relabelled; validator hash failure cannot be pre-empted; source/parsed-tree mutation, metadata/lifecycle exclusion, byte-change, and no-cache boundaries remain distinct. |
| 8 | Exact `LifecycleTransition` and eleven-field `SupersessionRelation` candidates reach their named validators | All 41 reach the assigned interface. Empty/duplicate/unsorted evidence, invalid graph edges, every ancestry relation, direct kind/schema inequalities, lifecycle pair, and typed-not-applicable authorization are validator-owned. |
| 9 | Static precedence assertions or the explicitly named higher-precedence public boundary | All 32 reach the frozen boundary and retain the same first failure. |

Thus every one of the 335 vectors has all declared inputs available at its
public operation; every named predicate is computable from those arguments;
no validator outcome is pre-empted by candidate construction; no semantic
predicate has two failure owners; and no two byte-identical effective input
and operation pairs have incompatible expected outcomes. The audit requires
no new public type, callable, tenth path, dependency edge, package change, or
API-count change.

The complete predicate-observability audit was repeated for revision v0.1.7,
including every boundary that can distinguish two I-1/I-2 failure codes:

| Boundary group | Complete local witness |
|---|---|
| Common failure support and I-1-preserving formation | Exact constructor arguments, immediate closed legacy caller map where applicable, and the explicit failure coordinate; no later validator relabels an I-1 formation failure |
| Core-number constructors, normalization, and decimal conversion | Exact input runtime type and literal numeric/bit fields; finite/nonfinite, structural, and wrong-union distinctions require no external state |
| `ErrorBound`, `NumericalResult`, and comparison/result construction | Exact declared kind, variants, bounds, applicability refs, completeness, and result fields supplied to the owning constructor |
| `apply_exact_core_operation` | Exact operation, ordered operands, variants/zero values, arity, and explicit conversion flag; the 23 adjacent and nine multiply-invalid cases witness the frozen first-failure order |
| `validate_numerical_policy` | The read-only provider's exact resulting property availability and values, including structural absence versus a present typed `NOT_APPLICABLE`; no method call, placeholder class, registry fact, or patch history |
| Dimension, unit, rule, quantity, resource/service, sign, time, clock, horizon, resolution, and uncertainty validators | The exact listed record/ref/context/pair arguments and their locally compared fields; all stronger ref-content claims remain deferred |
| `convert_quantity_exact` | Quantity, explicit source unit, explicit target unit, and rule; the role-equality proof above distinguishes `i2-0154` from `i2-0156` under every opaque-ref renaming |
| Region and boundary parent validators | Both children, typed parent-or-not-applicable, and aggregation ref, including declared parent links, intervals/contracts, and supplied treatment pairs only |
| Envelope, lifecycle, and supersession validators | The supplied immutable candidate's exact bytes/fields and independently parsed logical payload where specified; all status, evidence, ancestry, kind/schema, authorization, and direct-hash-occurrence distinctions are argument-local |

No other failure-code distinction lacks an explicit argument witness. The
audit makes no registry/domain-content claim and leaves every UQ-40 deferral
unchanged.

The exact non-fixture static supplement is assigned to
`tests/framework/test_primitives_envelopes.py`. Catalog names in this list are
expanded by §21.8.1 before construction; no alias text enters a public
projection:

```text
failure-support-nonempty-coordinate:
  interface = FailureInterfaceRef("ebu_framework.numeric","ErrorBound","1.0.0")
  object = FailureObjectRef(R(0).object_id,R(0).object_version,
                            R(0).object_content_hash)
  event = FailureEventKey(0,1,0,"ebu:scope:validation:s0","phase.start",
                          "ebu:object:validation:o0",0)
  evidence = FailureEvidenceRef("TRACE_PREFIX","sha256:" + "00"*32,NA)
  trace = CanonicalTraceState(APPLICABLE,"PARTIAL_DURABLE_PREFIX",0,evidence)
  envelope coordinates = (ERROR_BOUND_INVALID,I-2,interface,[object],event,
                          ordinal 1,NONE,NONE,PARTIAL,trace,
                          SCIENTIFIC_STATE_UNCHANGED,NOT_APPLICABLE,
                          [evidence],"fixture nonempty failure coordinate")
  derived failure_id =
    ebu:failure:core:sha256-7a457bf092a50e42b9fcd657e3f6da71eb3ef298fa29cf1741c15150076faa9d

failure-evidence-raw-source-valid:
  FailureEvidenceRef("RAW_SOURCE","sha256-raw:" + "00"*32,NA)
failure-evidence-wrong-domain-refused:
  FailureEvidenceRef("RAW_SOURCE","sha256:" + "00"*32,NA)
  -> DIGEST_INVALID

operand-validation-result-valid:
  OperandValidationResult(ADD,[INTEGER,INTEGER],R(0),QC0,true,COMPLETE,NA)
  -> exact seven-field §21.4.1 projection

sign-convention-valid:
  SignConvention(R(16),R(18),"credit","zero","debit")
  -> exact five-field §21.5.3 projection
sign-convention-duplicate-meaning:
  SignConvention(R(16),R(18),"same","same","debit")
  -> SIGN_CONVENTION_MISMATCH

record-metadata-valid:
  RecordMetadata(SID(3),R(47),R(48),R(49),R(50),R(51),R(52),R(53))
  -> exact field equality, immutability, and no scientific projection

registry-record-draft-valid:
  RegistryRecord(R(0),"fixture-kind",BYTES("7b2261223a317d"),DRAFT)
  -> exact construction and unchanged I-1 value parsing
registry-record-nondraft-refused:
  RegistryRecord(R(0),"fixture-kind",BYTES("7b2261223a317d"),REVIEWED)
  -> REGISTRY_RECORD_CONFLICT

conversion-source-anchor-opaque-renaming:
  i2-0154 roles = (quantity.unit_ref=R(63),source.unit_ref=R(3),
                   rule.source_unit_ref=R(3))
  i2-0156 roles = (quantity.unit_ref=R(3),source.unit_ref=R(3),
                   rule.source_unit_ref=R(63))
  -> STATIC_ASSERTION_V1("CONVERSION_SOURCE_ANCHOR_DISTINGUISHES_FAILURES")
     after any bijective opaque-ref renaming; no lookup or literal-value rule

boundary-treatment-pair-formation:
  child = BOUNDARY_L with external_effect_refs=[R(60)],
          unresolved_cross_boundary_effect_refs=[R(61)],
          cross_boundary_effect_treatments=[[R(60),R(62)],[R(61),R(63)]]
  -> exact pair/member types, effect-ref order, unique effect keys, no duplicate
boundary-treatment-coverage-refused:
  BOUNDARY_L with unresolved_cross_boundary_effect_refs=[R(60)] and
  cross_boundary_effect_treatments=[] in the parent-comparison input
  -> INVALID_AGGREGATION at cross_boundary_treatment

horizon-pending-pair-formation:
  validate_horizon(right-open HORIZON0,[[R(60),R(61)]])
  -> exact pair/member types, effect-ref order, unique effect keys
horizon-pending-pair-duplicate-refused:
  validate_horizon(right-open HORIZON0,
                   [[R(60),R(61)],[R(60),R(62)]])
  -> HORIZON_INVALID

envelope-direct-content-hash-occurrence-refused:
  canonical payload contains the envelope's exact stored object_content_hash
  string as a recursively nested object name, object value, or array member
  -> HASH_MISMATCH at direct_content_hash_exclusion before recomputation
envelope-alias-resolution-deferred:
  static AST/import assertion: validate_object_envelope performs no registry,
  alias, ObjectRef-target, or object-graph resolution
  -> STATIC_ASSERTION_V1("ALIAS_AND_GRAPH_CYCLE_DETECTION_DEFERRED")
```

The supplement also asserts the exact declared member tuples, in their
documented order, for all 16 public enums in `errors`, `numeric`, `envelopes`,
and `primitives`; it asserts `CoreNumberV1` has exactly the four named union
members and that `NumericalPolicyV1` has exactly the properties and five
method signatures in §21.4. Every success projection is checked against
independently encoded canonical hex where a projection exists. Every failure
uses the exact code shown and the owning constructor or validator interface at
stage I-2.

This closure audit found no missing public field, runtime type, enum member,
applicability rule, projection coordinate, immutability rule, constructor or
validation behavior, failure meaning/precedence, capability class, owner, or
deterministic fixture/static-test route. Revision v0.1.7 changes only the
argument structure of the existing `convert_quantity_exact` callable; it
changes no public type/callable name or count, owner, capability, dependency
edge, root export, or future path. The totals remain 84 public types, 42
public callables, `__version__`,
127 root exports, 29 DAG edges, and nine future implementation paths. The
failure domain is 29 retained I-1 plus 24 I-2 codes, with 24 I-2 precedence
entries.

### 21.9 Scientific neutrality, roadmap, and Gate preservation

I-2 contains no domain numerical policy, EBU quote rule, distortion, action,
transition, trajectory, controller, topology, equilibrium/homeostasis rule,
routing/settlement rule, parameter search/optimization, stochastic semantic,
or wave, interference, spectral, Taylor, Fibonacci-like, recursive, fractal,
or self-similar model. It supplies representation and validation only.

The single planning order remains:

1. Framework I-1 through I-9.
2. Part IV local measurement and outcome discrimination.
3. Part V long-run viability and homeostasis.
4. Part VI sequential and parallel actions.
5. Part VII routes and infrastructure.
6. Part VIII topology, timing, waves, spectra, interaction hierarchies,
   recurrence, hierarchy, and fractal hypotheses.
7. Part IX institutional application and settlement.

Future structural candidates should be derived where possible from declared
mathematics, compared with simpler baselines, and tested against a
homeostasis-preservation gate. This is planning context only and grants no
scientific work.

Gate 1D-C is preserved exactly: one cumulative official runner invocation;
no receipt; no result directory; no model-state advance; scientific state
`UNSTARTED`. This amendment does not inspect, investigate, correct, retry,
invoke, finalize, or reinterpret it and never describes the cumulative
invocation count as zero.

## 22. Normative prospective Framework I-3 authority

### 22.1 Sources, precedence, and status

The complete corrected I-3 authority is the agreement of:

1. `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md` v1.0.1 at raw SHA-256 `b5e54fad02a232acc89b4d69613f93026dbd0a10d400b0751072475e32173fee`;
2. `unified_python_research_framework_i3_contract.json` v1.0.1 at raw SHA-256 `817513d43726cbb23a4f61a711700248724aa491dad654ad0c2c6ce703dc8c16` and canonical SHA-256 `a295ad157ec471776b0c0cf9dca3b1a2d2512ba2bb1cbbcb243e548feec770e4`; and
3. `unified_python_research_framework_i3_validation_contract.json` v1.0.0 at raw SHA-256 `0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0` and canonical SHA-256 `88283fe2efda6c769688985805d3654d6deb5016195ea119f337b2fd843dd8ec`.

The amendment is the normative human rendering; the first JSON is the mechanical schema and ordering source; the second JSON is the fully materialized validation source. Any mismatch fails closed. Version 1.0.1 narrowly supersedes v1.0.0 only for implementation-path/substage ownership. The historical v1.0.0/v0.1.9 hashes are preserved in §20.10 and the amendment. This correction changes no public type or callable; field, enum, tagged union, signature, projection, or hash domain; failure code, ordinal, predicate, precedence, envelope, or failure ID; vector, corpus count, corpus bytes, or corpus hash; import graph or export inventory; accepted I-1/I-2 path or semantic; or scientific definition, equation, model, result, protocol, Gate state, interpretation, or execution permission.

I-3 remains specification-ready and unimplemented. This revision authorizes no I-3A implementation, fixture installation, test execution, registry acceptance, scientific use, state advance, or I-4–I-8 behavior.

### 22.2 Closed mechanical inventory

| Inventory | Exact value |
|---|---:|
| Retained public types | 69 |
| Historical retained / new conservation types | 55 / 14 |
| Public pure validators | 23 |
| Appended I-3 failure codes | 35 |
| Accepted root prefix / appended suffix / final root count | 127 / 92 / 219 |
| I-3 modules / direct acyclic imports | 15 / 91 |
| Future implementation paths | 23 |
| Ownership rows / distinct implementation substages | 23 / 5 |
| Substage path counts I-3A / I-3B / I-3C / I-3D / I-3E | 5 / 6 / 5 / 4 / 3 |
| Historical / separately deferred types | 25 / 8 |
| Fully materialized validation vectors | 544 |

The exact 92-name suffix remains 69 retained types followed by 23 validators. The exact type fields, enum members, unions, hash exclusions, projections, module exports, direct imports, deferred names, and 23-path prospective manifest are those in the mechanical contract and its complete amendment rendering. `conservation.py` remains dedicated; reduced and open profiles are first-class; historical models require no migration.

| Substage | Exact module paths | Exact fixture paths | Exact test paths | Count |
|---|---|---|---|---:|
| `I-3A` | `src/ebu_framework/errors.py`; `src/ebu_framework/state.py`; `src/ebu_framework/conservation.py`; `src/ebu_framework/distortion.py` | — | `tests/framework/test_i3a_declarations.py` | 5 |
| `I-3B` | `src/ebu_framework/actions.py`; `src/ebu_framework/network.py`; `src/ebu_framework/commitments.py`; `src/ebu_framework/observation.py`; `src/ebu_framework/scheduling.py` | — | `tests/framework/test_i3b_declarations.py` | 6 |
| `I-3C` | `src/ebu_framework/policy.py`; `src/ebu_framework/causal.py`; `src/ebu_framework/settlement.py`; `src/ebu_framework/ledger.py` | — | `tests/framework/test_i3c_declarations.py` | 5 |
| `I-3D` | `src/ebu_framework/faults.py`; `src/ebu_framework/experiment.py`; `src/ebu_framework/artifacts.py` | — | `tests/framework/test_i3d_declarations.py` | 4 |
| `I-3E` | `src/ebu_framework/__init__.py` | `tests/framework/fixtures/i3_validation_v1.json` | `tests/framework/test_i3_integration.py` | 3 |

The flattened table is a bijection with the exact 23-path manifest: every frozen path appears once, there are exactly five distinct substages, no path is missing or duplicated, no outside path is admitted, and every substage inventory agrees with its ownership rows. After a substage path is accepted, no later substage may modify it without a separate prospective correction.

`errors.py` is owned by I-3A. I-3A appends the complete already-frozen 35-code I-3 suffix exactly once and installs all 35 codes together. Every accepted I-1/I-2 code, ordinal, string, compatibility rule, caller behavior, and byte outside that append-only suffix remains unchanged. I-3B–I-3D consume the inert identifiers already installed and do not modify `errors.py`; installation does not implement or authorize associated behavior. I-3E only verifies the suffix and preservation evidence. `errors.py` remains standard-library-only with its frozen import restrictions.

I-3E owns installation and audit of the exact 92-name root suffix, complete 544-vector fixture, complete projection integration, import audit, and full T0 validation. It does not reopen accepted I-3A–I-3D implementations.

### 22.3 Exact validator signatures and failure precedence

| Interface | Exact positional-only signature | Exact precedence |
|---|---|---|
| `validate_state_record` | `(record: SystemState, projection_contract: ProjectionContract, predecessor_epoch: Epoch\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `PHYSICAL_POLICY_MEMORY_CONFLATION` → `STATE_PROJECTION_FAILURE` → `MISSING_COORDINATE` → `EPOCH_MISMATCH` → `HASH_MISMATCH` |
| `validate_projection_contract` | `(represented: RepresentedState, contract: ProjectionContract, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `STATE_PROJECTION_FAILURE` → `MISSING_COORDINATE` → `HASH_MISMATCH` |
| `validate_conservation_profile_selection` | `(selection: ConservationProfileSelection, /) -> None` | `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` |
| `validate_conservation_profile` | `(profile: ConservationProfile, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONSERVATION_PROFILE_INVALID` → `CONSERVATION_QUANTITY_DUPLICATE` → `CONSERVATION_COORDINATE_DUPLICATE` → `CONSERVATION_FLOW_CHANNEL_DUPLICATE` → `CONSERVATION_UNIT_MISMATCH` → `CONSERVATION_LEVEL_REQUIREMENT_MISSING` → `CONSERVATION_EVIDENCE_INCOMPLETE` → `CONSERVATION_ISOLATION_INVALID` → `CONSERVATION_TOLERANCE_UNDECLARED` → `HASH_MISMATCH` |
| `validate_distortion_model` | `(model: DistortionModel, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `DISTORTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_action_definition` | `(definition: ActionDefinition, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_action_instance` | `(instance: ActionInstance, route: RoutePlan\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `PROVISIONAL_ROUTE_REQUIRED` → `HASH_MISMATCH` |
| `validate_provider_network` | `(provider: Provider, network: ProviderNetwork, topology: TopologySnapshot, locus: CapacityLocus, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `HASH_MISMATCH` |
| `validate_route_plan` | `(route: RoutePlan, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_DUPLICATE_MEMBER` → `PROVISIONAL_ROUTE_REQUIRED` → `HASH_MISMATCH` |
| `validate_commitment` | `(record: Commitment, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_reservation` | `(record: Reservation, capacity: CapacityRecord, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `ACTION_DECLARATION_INVALID` → `CONSERVATION_UNIT_MISMATCH` → `RESERVATION_CAPACITY_MISMATCH` → `HASH_MISMATCH` |
| `validate_capacity_record` | `(record: CapacityRecord, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `CONSERVATION_UNIT_MISMATCH` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_measurement` | `(measurement: Measurement, contract: MeasurementContract, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `EPOCH_MISMATCH` → `CONSERVATION_UNIT_MISMATCH` → `MEASUREMENT_CONTRACT_MISMATCH` → `HASH_MISMATCH` |
| `validate_schedule` | `(record: Schedule\|ComparatorSchedule\|CoordinationEventDeclaration, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INADMISSIBLE_SCHEDULE` → `MISSING_COMPARATOR` → `HASH_MISMATCH` |
| `validate_information_view` | `(contract: InformationContract, view: InformationView, read_set: InformationReadSet\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INFORMATION_VIEW_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_policy_memory_state` | `(record: PolicyMemoryState, mode: MemoryMode, predecessor_epoch: Epoch\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `POLICY_MEMORY_NOT_APPLICABLE` → `EPOCH_MISMATCH` → `HASH_MISMATCH` |
| `validate_causal_remainder` | `(record: CausalRemainder, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONSERVATION_UNIT_MISMATCH` → `CAUSAL_ATTRIBUTION_UNRESOLVED` → `HASH_MISMATCH` |
| `validate_settlement_closure` | `(closure: SettlementClosureRecord, quote: Quote, receipt: Receipt, group_receipt: GroupReceipt, child_actions: tuple[ChildActionRecord,...], residual: GroupResidual, shares: tuple[SettlementShare,...], causal_status: CausalIdentificationStatus, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `SETTLEMENT_LINK_INVALID` → `CONSERVATION_UNIT_MISMATCH` → `SETTLEMENT_CLOSURE_FAILURE` → `CAUSAL_ATTRIBUTION_UNRESOLVED` → `HASH_MISMATCH` |
| `validate_ledger` | `(ledger: Ledger, entries: tuple[LedgerEntry,...], /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `LEDGER_LINK_INVALID` → `HASH_MISMATCH` |
| `validate_fault_schedule_boundary` | `(schedule: FaultScheduleV1, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `FAULT_SCHEDULE_INVALID` → `HASH_MISMATCH` |
| `validate_experiment_configuration` | `(configuration: ExperimentConfiguration, fault_schedule: FaultScheduleV1\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONFIGURATION_INCOMPLETE` → `POLICY_MEMORY_NOT_APPLICABLE` → `FAULT_EXTENSION_UNAVAILABLE` → `HASH_MISMATCH` |
| `validate_execution_binding` | `(binding: ExecutionBinding, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `EXECUTION_SEMANTICS_PROJECTION_FAILURE` → `HASH_MISMATCH` |
| `validate_execution_result_manifest` | `(manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ARTIFACT_COMPLETENESS_INVALID` → `HASH_MISMATCH` |

The precedence matrix contains exactly 145 validator/failure sites. The appended failure order is: `I3_RECORD_FORMATION_INVALID`, `I3_OBJECT_CONTENT_MISMATCH`, `I3_COLLECTION_ORDER_INVALID`, `I3_DUPLICATE_MEMBER`, `STATE_PROJECTION_FAILURE`, `MISSING_COORDINATE`, `POLICY_MEMORY_NOT_APPLICABLE`, `EPOCH_MISMATCH`, `CONSERVATION_PROFILE_INVALID`, `CONSERVATION_LEVEL_REQUIREMENT_MISSING`, `CONSERVATION_QUANTITY_DUPLICATE`, `CONSERVATION_COORDINATE_DUPLICATE`, `CONSERVATION_FLOW_CHANNEL_DUPLICATE`, `CONSERVATION_UNIT_MISMATCH`, `CONSERVATION_EVIDENCE_INCOMPLETE`, `CONSERVATION_ISOLATION_INVALID`, `CONSERVATION_TOLERANCE_UNDECLARED`, `PHYSICAL_POLICY_MEMORY_CONFLATION`, `DISTORTION_DECLARATION_INVALID`, `ACTION_DECLARATION_INVALID`, `RESERVATION_CAPACITY_MISMATCH`, `MEASUREMENT_CONTRACT_MISMATCH`, `INADMISSIBLE_SCHEDULE`, `MISSING_COMPARATOR`, `PROVISIONAL_ROUTE_REQUIRED`, `INFORMATION_VIEW_DECLARATION_INVALID`, `CAUSAL_ATTRIBUTION_UNRESOLVED`, `SETTLEMENT_LINK_INVALID`, `SETTLEMENT_CLOSURE_FAILURE`, `LEDGER_LINK_INVALID`, `FAULT_SCHEDULE_INVALID`, `FAULT_EXTENSION_UNAVAILABLE`, `CONFIGURATION_INCOMPLETE`, `EXECUTION_SEMANTICS_PROJECTION_FAILURE`, `ARTIFACT_COMPLETENESS_INVALID`.

`POLICY_MEMORY_PROJECTION_FAILURE` and `POLICY_MEMORY_MISMATCH` are deferred to I-4/I-5 because their predicates require accepted pairing or transition state. I-3 retains only locally observable policy-memory applicability, mode, direct predecessor epoch, object-content, and hash predicates. The four paired local failures added by the correction are `RESERVATION_CAPACITY_MISMATCH`, `MEASUREMENT_CONTRACT_MISMATCH`, `INFORMATION_VIEW_DECLARATION_INVALID`, and `SETTLEMENT_LINK_INVALID`.

Every validator receives all values needed for each retained predicate. State and represented-state validators receive a direct `ProjectionContract`; state and policy-memory validators receive an exact predecessor-epoch witness; action instance receives the direct `RoutePlan`; settlement receives closure, quote, receipt, group receipt, child actions, residual, shares, and causal status. No opaque target is resolved.

`I3_OBJECT_CONTENT_MISMATCH` scans every supplied enveloped I-3 record in exact positional-signature order. A directly supplied record is inspected at its argument position; an argument explicitly frozen as an ordered tuple/list-like collection of enveloped records is inspected member-by-member in canonical tuple order before the next argument. Enums, scalar witnesses, `Applicability`, primitive records, and non-enveloped values are skipped. Each freshly parsed stored payload is compared byte-logically with the exact canonical projection excluding `envelope` and `derived_exclusions`; the earliest unequal record emits the failure and blocks later precedence predicates. Its validator is the `interface_ref`, its exact stored object ID/version/content hash is the sole `object_refs` member, and `human_summary` identifies the deterministic argument/member position. Registry lookup, opaque-reference resolution, inferred content, patch history, and fixture identity do not participate. Stored-hash recomputation remains the later `HASH_MISMATCH` predicate and occurs only after all projection comparisons succeed.

The mechanical scan inventory covers all 23 validators. In particular, `validate_provider_network` scans `Provider`, `ProviderNetwork`, `TopologySnapshot`, and `CapacityLocus`; `validate_information_view` scans `InformationContract`, `InformationView`, and an applicable `InformationReadSet`; settlement scans closure, quote, receipt, group receipt, every child action in tuple order, residual, and every share in tuple order; ledger scans its ledger and every entry in tuple order; and result-manifest validation scans the manifest and every artifact in tuple order. `validate_conservation_profile_selection` has no enveloped record to scan. Formation failures are separate: no formation vector emits this code, and the 69 formation-negative envelopes retain empty object refs because formation fails before a valid supplied enveloped-record identity exists.

The uncertainty-aware tolerance field is `ObjectRef|Applicability`; `NOT_APPLICABLE` reaches `CONSERVATION_TOLERANCE_UNDECLARED`, while malformed `APPLICABLE` reaches `IMPLICIT_ABSENCE_FORBIDDEN`. Conservation contamination is inspected only as reserved direct keys in physical state payload; opaque referenced targets retain an explicit nonclaim. `LedgerEntry.ledger_id: ScientificId` avoids a content-hash cycle.

Every ordered or duplicate-free tuple and every applicability/sum union has an exact formation/validator owner in the mechanical contract. Route segment order is semantic rather than canonical. Order witnesses contain two distinct wrong-order members; duplicate witnesses contain equal members.

### 22.4 Fully materialized validation authority

The `vectors` array is normative and contains complete recursive runtime descriptors and full ordered arguments. It requires no baseline, default, primary-type, paired-record, cardinality, omitted-field, or patch-history inference.

| Coverage | Exact count |
|---|---:|
| Type formation positive / boundary / negative | 69 / 69 / 69 |
| Validator positive / boundary | 23 / 23 |
| Isolated validator failure sites | 145 |
| Isolated failure sites including 69 constructors | 214 |
| Adjacent precedence pairs | 122 |
| Multiply-invalid validators | 23 |
| Object-content scan-order cases | 1 |
| **Total vectors** | **544** |

Two independent standard-library-only external implementations reconstructed byte-identical canonical vector bytes: **24104258 bytes**, exactly one final LF, SHA-256 `fbdaffc00e88b9f20a14b443d7f18f854f625413e4b11475088102f60600c01b`. They agreed on ordered IDs, names, effective inputs, outcomes, failure IDs, successful projections, object-content scan order/evidence, bytes, newline, digest, and collision audit. The audit found 543 unique effective inputs, one benign identical input (the sole one-member enum positive/boundary formation), and zero conflicting outcomes.

All 67 validator-level `I3_OBJECT_CONTENT_MISMATCH` outcomes carry the earliest mismatching record and a rederived failure ID. The six provider-network and information-view vectors retain their declared first failure while now identifying `CapacityLocus` and `InformationReadSet`, respectively. The additional `i3v-08-o01` case contains matching `Provider`, mismatching `ProviderNetwork`, matching `TopologySnapshot`, and mismatching `CapacityLocus`; signature order selects `ProviderNetwork` as the sole failure object evidence.

`APPLICABLE` plus empty conservation `profile_refs` has the isolated outcome `IMPLICIT_ABSENCE_FORBIDDEN`. `CONSERVATION_PROFILE_INVALID` uses the distinct self-parent profile condition. The future repository fixture is absent and unimplemented.

### 22.5 Conservation, stages, and nonclaims

There is no universal zero-residual rule or hidden tolerance. Exact expected residual may be nonzero. I-3 declares but does not compute conservation residuals, measurements, routes, causal contributions, settlement allocations, traces, or results. Physical state, policy memory, causal attribution, and settlement remain distinct. Residual behavior is I-5, Bridge behavior I-6, Dynamic behavior I-7, and finalization/publication behavior I-8.

The review decomposition and exclusive path inventories are those in §22.2. Every §22 authority must be independently accepted before I-3A begins. A fresh independent audit remains required; independent audit/commit and I-3A implementation have not begun.
