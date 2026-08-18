# Unified Python Research Framework I-4 Authority Amendment

Status: prospective documentation-only authority candidate; unimplemented;
production disabled.

## 1. Decision

This amendment prospectively closes Framework I-4 external authorization,
local single-use, registry/configuration/binding acceptance, operational-ledger
append, and synthetic information-capability mechanics. Its mechanical
rendering is `unified_python_research_framework_i4_contract.json`. The
validation authority is
`unified_python_research_framework_i4_validation_contract.json`. The closed
predecessor inventory is
`unified_python_research_framework_i4_predecessor_manifest.json`.

The UQ-25 pair prospectively selects `PyNaCl==1.6.2` with the exact
`cffi==2.1.1` and `pycparser==3.0` closure. The governance pair defines a
future production-bootstrap requirement but supplies no instance.

This task creates authority documents only. It authorizes no Python edit,
fixture installation, dependency installation, provider import, protected
operation, production bootstrap, test execution, commit, integration, or
push.

## 2. Authority coordinates and narrow precedence

The exact base is merge commit
`eaafbb50f30f3ed3e1300bc9d96456f570d17e13`, subject “Integrate Framework
I-3E root exports fixture and integration,” with ordered parents
`4ab0da08a55dd3c9db197ab669a4e0d3050bb1fa` and
`dac8717017e8ba6d6c46b17d031095f3b898762f`.

The following predecessor identities are mandatory:

| Source | Raw SHA-256 |
|---|---|
| `AGENTS.md` | `2538964de3ff0b328ce5b10efa4396a0f870f6f10b6d31b86d174cc607d8820e` |
| Specification | `713b3ceb694721710ffeca8b9efc7cb1c54317ed922a2ba5e352b01faa8c82fa` |
| Implementation plan | `7dfc8da2b8c31e8b66b867bc7c894f4f6218420391e21c6443c48645c884a336` |
| I-1 amendment | `a27aedf955c1e7bbf7039efc905951f516e070a2f36dc24b23c72d75f6a2f448` |
| I-1 contract | `edf2bd33361e7b2b2e083a10535c87e1e1cbbd36d21c2a3f3004f12b1743c351` |
| I-3 amendment | `eaa3c80efa6ff0beae6f3ad8da3be67fb61f3cc5223b2067c256732ebf7bdfbc` |
| I-3 contract raw | `d8acef250314e1405b048a324c9f855010f7927cc8760e2f827bba85253d7979` |
| I-3 contract canonical | `384f289fbd20524d193eed9d852334915bf41b8b18b5096f1b7fb8ca9788a534` |
| I-3 validation raw | `9ecd849f24ecd3e55883874263c10c181fea2e16a3000e87e4fc7fe02c2ccb2b` |
| I-3 validation canonical | `ba70b9915ebc5957225adc3f4806d89a540bec86560a29d63471613af2659079` |

Within I-4 only, this amendment and its contract supersede inconsistent
planning prose about names, operations, fields, ownership, paths, provider
closure, validation, and activation. They do not reopen accepted I-1, I-2, or
I-3 behavior. The specification and plan remain authoritative outside that
narrow scope. The dependency pair governs only UQ-25. The governance pair
governs only the requirements for a later bootstrap. A Markdown/JSON mismatch
is an integrity failure; it is never permission to select convenient clauses.

## 3. Accepted predecessor boundary

I-4 begins from exactly:

- 219 ordered root exports, LF-framed digest
  `b79f89d46e7817d7ea8ba819497641754007bf52e712372ac50b41ef06d66c3d`;
- 88 ordered failure codes, LF-framed digest
  `0a9e0c22d74d0a1891af19546422296881d2fa6ba16319238def55578c9706d3`;
- 15 I-3 modules and 91 exact direct package-import edges;
- 23 accepted I-3 implementation paths;
- 544 I-3 validation vectors; and
- byte-identical `i3_validation_v1.json` at 24,179,582 bytes and SHA-256
  `e5790524bb7d63dcc18e15cd933d801c225253230f09b06d9828a703fc6218c5`.

Every predecessor blob, byte length, raw digest, stage owner, classification,
and permitted future disposition appears exactly once in the predecessor
manifest. An implementation must stop before editing if any non-null identity
does not match.

## 4. Exact I-4 scope and nonclaims

I-4 may later implement:

- PureEdDSA Ed25519 verification against a pinned external trust profile;
- issuer registry, delegation, trusted-time, and revocation validation;
- one exact operation and exact target set per `StageAuthorization`;
- validation records containing only checks safely completed in fail-fast
  order;
- durable local SQLite compare-and-consume with an authorization-use ledger
  row in the same transaction;
- authorized registry acceptance and supersession;
- authorized experiment-configuration and execution-binding acceptance;
- authorized operational-ledger append; and
- fabricated validation-namespace information views with exact visibility,
  availability, age, current-memory, traversal, and read-set restrictions.

I-4 does not supply scientific semantics, perform registry inference, prove an
opaque reference, create a scientific lease, implement T2/T3, invoke a policy,
measure or project state, enter a run, advance an epoch, finalize a result,
recover or publish an artifact, correct a result, or perform a Gate operation.
It makes no distributed single-use claim.

## 5. Resolved planning contradictions

| Question | Resolution | Safety reason |
|---|---|---|
| Envelope name | Only `AuthorizationAuthenticityEnvelopeV1` exists. The unversioned name is neither a type nor alias. | The signature vocabulary remains versioned and closed. |
| Operation cardinality | `StageAuthorization.authorized_operation` is one `AuthorizedOperation`, never a tuple or set. | One consumption cannot union permissions. |
| Execution operation | `EXECUTE_BOUND_RUN` is retained; `ADVANCE_SCIENTIFIC_STATE` is absent. | Authority governs entry to one bound run; internal advance requires a later live lease. |
| Missing mutations | Add `ACCEPT_REGISTRY_OBJECT`, `SUPERSEDE_REGISTRY_OBJECT`, and `APPEND_OPERATIONAL_LEDGER_ENTRY`. | Every I-4 mutation has its own exact grant. |
| Execution identity | Preserve the accepted separate `ExecutionIdentity` record. Do not add identity to `ExecutionBinding`. | Run identity remains outside deterministic binding content while authorization still matches it exactly. |
| T2/T3 names | `T2FixtureCapability` is absent until I-6; `ScientificExecutionLease` is absent until I-5. | I-4 exposes no constructor or token that escalates beyond T1. |
| Accepted modules | Narrowly extend registry, experiment, ledger, and hashing; preserve identity, envelopes, policy, observation, safety, and absent `validation.py`. | Accepted records and validation semantics remain frozen outside named hooks. |

The closed operation order is:

```text
ACCEPT_REGISTRY_OBJECT
SUPERSEDE_REGISTRY_OBJECT
ACCEPT_EXPERIMENT_CONFIGURATION
ACCEPT_EXECUTION_BINDING
APPEND_OPERATIONAL_LEDGER_ENTRY
EXECUTE_BOUND_RUN
FINALIZE_EXECUTION_RESULT_MANIFEST
RECOVER_EXECUTION_ARTIFACTS
CREATE_CORRECTION_RECORD
PUBLISH_ARTIFACTS
```

Only the first five operations have I-4 mutation callables. The other five may
be checked with synthetic authorization records, but their entry interfaces
remain absent and owned by later stages.

## 6. T1 validation versus production activation

Synthetic validation is confined to the reserved `ebu:*:validation:*` namespace,
records marked `SYNTHETIC_NONSCIENTIFIC`, fixed authority bytes, a temporary
qualified local SQLite directory, and deterministic injected time/challenge
values. It can exercise inert acceptance transitions and use consumption. It
cannot accept a real object or construct a later-stage capability.

Production has no injected challenge, clock, provider transcript, filesystem
classification, profile, key, endpoint, or service. It creates exactly 32
challenge bytes with `secrets.token_bytes(32)` and calls real services only
after an installed profile pin and dependency receipt pass. A production
profile rejects every validation key and namespace. A validation profile
cannot be installed as production.

Until a separately authorized governance bootstrap instance is schema-valid,
independently approved, installed, and operator-pinned, every protected
production interface fails `PRODUCTION_BOOTSTRAP_MISSING` before provider,
service, SQLite, registry, or ledger mutation.

## 7. Trust, signatures, and evidence

The sole signature profile is `EBU-Authorization-Ed25519-V1`:

- public keys are exactly 32 bytes and signatures exactly 64 bytes;
- base64url is canonical, URL-safe, unpadded, and round-trips exactly;
- key IDs are `ed25519:` plus lowercase raw SHA-256 hex of public-key bytes;
- both the public key and signature `R` are canonical edwards25519 points and
  reject small order;
- the little-endian scalar `S` is strictly less than RFC 8032 `L`;
- messages are exact ECJ-1 bytes;
- Ed25519ctx, Ed25519ph, prehash, multipart, fallback, and negotiation reject
  before provider construction; and
- structural precheck failure makes zero provider calls. An admissible
  signature makes exactly one `VerifyKey` construction and one `verify` call,
  with no retry.

The exact authorization, trust-evidence, and trusted-time signature-message
fields and hash domains are in the contract. Signatures, proof hashes, and
authenticity-envelope references never enter the signed object's content hash
or its own signature message.

The trust profile contains exactly three issuer roots with threshold two,
three revocation roots with threshold two, and three time keys with one
signature. Root proofs contain exactly two distinct, ordered proofs. Surplus,
duplicate, missing, or reordered proofs reject.

Issuer and revocation sequences begin at zero with `GENESIS`. A successor is
exactly prior sequence plus one and names the exact prior ref. Lower sequence
is rollback; a jump is a gap; unequal content at the same sequence is
equivocation. These states and time-service sequences are durably persisted
before a protected operation.

Delegation is a zero-to-four credential leaf-to-root chain. Every credential
and proof is positional. Issuer/key continuity, common trust and revocation
authority, temporal overlap, exclusions, strict subset attenuation, decrement
of remaining depth, no repeated credential, no repeated issuer/key pair, and
no cycle are mandatory. Parent scope union and joint delegation are absent.

## 8. Exact validation and consumption boundary

Validation order is:

1. strict formation, ECJ-1, object hashes, proof hashes, and use-key
   reconstruction;
2. installed trust pin, supported profile, provider receipt, and namespace;
3. issuer roots, snapshot continuity, signer key, and durable state;
4. authorization message and signature;
5. delegation and effective ceiling;
6. fresh trusted time;
7. current revocation;
8. exact stage, one operation, targets, configuration, binding, separate
   execution identity, exclusions, interval, and lifecycle;
9. predecessor evidence;
10. binding/configuration, execution-identity, and policy-memory consistency;
11. atomic single-use consumption.

Every ordered subcheck is mechanical in the contract. A pass appends one
`PASS` check. The first failure appends one `FAIL` check and stops. No
unperformed check appears. `validate_stage_authorization` ends after step 10
as `VALIDATED_NOT_CONSUMED`. `consume_stage_authorization` alone performs step
11.

A constructed `AuthorizationUseRecord` has no authority. Every protected
mutation resolves its exact use key, row, and coupled operational-ledger row
from the configured store. Consumption remains permanent if a subsequent
registry or ledger mutation fails.

## 9. SQLite local single-use contract

The database path is explicit, absolute, normalized, non-symlinked, and ends
in `authorization-use-v1.sqlite3`. No environment, current-directory, or
default fallback exists. Only local APFS, ext4, XFS, and NTFS qualify.
Network, distributed, FUSE, overlay, tmpfs, ramdisk, FAT/exFAT, and unknown
filesystems reject.

The accepted SQLite line is `3.46.0 <= sqlite3.sqlite_version < 4.0.0`.
Schema version, application ID, strict tables, indices, constraints, exact DDL
lines, and connection-setting order are frozen mechanically. The connection
uses rollback journal `DELETE`, `synchronous=FULL`, foreign keys, trusted
schema off, in-memory temp store, zero busy timeout, and `BEGIN IMMEDIATE`.

The transaction inserts the exact use row, derives and inserts its
predecessor-linked operational-ledger row, and commits before any target
mutation. Uniqueness conflict means already consumed only after one exact
read-only coupling check. Lock, I/O, full, corrupt, not-a-database, schema,
setting, or durability uncertainty is unresolved.

If commit outcome is ambiguous, at most one new-connection read-only recheck
is allowed. Exact coupled rows mean consumed; any missing, partial,
mismatching, or unreadable state remains unresolved. The insertion is never
retried. No interface deletes or resets a consumed key.

Synthetic cleanup closes every connection, proves realpath containment, and
removes only the database and its `-journal`, `-wal`, and `-shm` siblings
inside the freshly created temporary directory. Production cleanup is absent.

## 10. Registry, configuration, binding, and ledger acceptance

`accept_registry_object` accepts an exact already-validated DRAFT or REVIEWED
candidate and appends an immutable ACCEPTED registry state without changing
content.

`supersede_registry_object` requires an ACCEPTED predecessor, DRAFT or REVIEWED
successor, and the accepted I-2 supersession validator. It atomically appends
predecessor SUPERSEDED and successor ACCEPTED states.

`accept_experiment_configuration` reruns the accepted I-3 validator against
the exact candidate and supplied fault-schedule witness, then appends an
ACCEPTED state without content change.

`accept_execution_binding` reruns the accepted I-3 binding validator, resolves
the exact already-ACCEPTED configuration, and requires exact
`accepted_configuration_ref` equality before appending ACCEPTED.

`append_operational_ledger_entry` is limited to `LedgerKind.OPERATIONAL` and
requires exact predecessor, next ordinal, new entry, and head. Scientific
ledger append remains I-5.

## 11. Information capability mechanics

I-4 implements only `build_synthetic_information_view`. A production
`build_information_view` and live `validate_information_read_set` remain
absent T3 behavior.

The synthetic factory checks, in order, explicit visibility, availability no
later than injected now, maximum age, stateless/stateful current-memory
applicability, traversal prohibition, and attempted read-set subset/order/
uniqueness. It creates `AccessCapability` only after every check. The
capability constructor is private and rejects copying, pickling, subclassing,
direct construction, and replacement. I-4 factories create only T1 synthetic
capabilities.

No alias, registry, object graph, attribute, mapping-key, path, URI, callback,
descriptor, or nested-reference traversal is allowed.

## 12. Failure, export, and import closure

The 61-code I-4 suffix begins at ordinal 89 and ends at ordinal 149.
`FailureEnvelope` retains the accepted 16-field projection. Every code's
summary, retry class, durability state, scientific effect, and evidence rule
is frozen in the contract. No I-4 failure reports state or policy-memory
advance.

The exact 48-name root suffix contains 33 types followed by 15 callables. It
is appended after the accepted 219 names, producing 267 exports. Its
LF-framed digest is
`2b5919d755c747e7ff8f7ffe75bf4e7d6234954be83027defbe4f6e57784f421`;
the complete 267-name digest is
`90461e517d22fb8ec750acb19f397abb6cae0b6bf66952b9269e8546d5efe2ac`.

The four I-4 modules add exactly 28 direct package edges. All 91 accepted I-3
edges remain byte-identical, giving 119 I-3-plus-I-4 edges. The graph is
acyclic. Provider imports exist only in `trust.py`; SQLite imports only in
`authorization_use.py`; OS randomness only in the production trusted-time
path. The complete module `__all__` tuples are mechanical.

## 13. Closed implementation path manifest

Later implementation may create exactly eight paths:

```text
src/ebu_framework/trust.py
src/ebu_framework/authorization.py
src/ebu_framework/authorization_use.py
src/ebu_framework/capabilities.py
tests/framework/fixtures/authorization_vectors_v1.json
tests/framework/test_authorization.py
tests/framework/test_authorization_use.py
tests/framework/test_capabilities.py
```

It may modify exactly ten paths:

```text
pyproject.toml
requirements-framework.lock
src/ebu_framework/__init__.py
src/ebu_framework/errors.py
src/ebu_framework/hashing.py
src/ebu_framework/registry.py
src/ebu_framework/experiment.py
src/ebu_framework/ledger.py
tests/framework/test_i3_integration.py
tests/framework/test_primitives_envelopes.py
```

`identity.py`, `envelopes.py`, `policy.py`, `observation.py`, and
`tests/framework/safety.py` are named immutable predecessors.
`validation.py`, execution/event/durability/trace/Bridge/Dynamic/provenance/
recovery/publication modules, and their later tests remain deferred or
forbidden.

## 14. Narrow historical compatibility authority

Two accepted tests contain final-snapshot assumptions that cannot survive an
append-only I-4 API.

In `tests/framework/test_i3_integration.py`, future implementation replaces
the whole tail assertion with exact `[127:219]` I-3 and `[219:]` I-4 suffix
assertions. Failure inventory changes from exact whole 88 to exact `[:53]`,
`[53:88]`, and `[88:]` assertions. All authority hashes, fixture checks,
module exports, import graph, projection, collision, reachability, and
predecessor checks remain.

In `tests/framework/test_primitives_envelopes.py`, future implementation
changes the exact root length to at least 127 and applies the accepted
sortedness/uniqueness assertions to `root_exports[:127]` while retaining
whole-root uniqueness and root import/export equality. The exact 53-code
failure prefix and every other check remain.

This authority is not permission to edit either test now and is not a general
relaxation.

## 15. UQ-25 and package closure

The dependency decision selected `PyNaCl==1.6.2`. The complete CPython 3.14
closure is `cffi==2.1.1` and `pycparser==3.0`. Exactly 23 wheels are admitted
for standard/free-threaded CPython on the six frozen OS/architecture targets;
sdists and source builds are prohibited.

The prospective `pyproject.toml` change replaces only:

```toml
dependencies = []
```

with:

```toml
dependencies = ["PyNaCl==1.6.2"]
```

The proposed lock is exactly 2,036 LF bytes with SHA-256
`8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a`.
No actual package or lock file changes in this task.

## 16. Synthetic validation authority

V4, V5, and V11 contain 126 exact vectors:

| Category | Count |
|---|---:|
| provider | 20 |
| issuer | 10 |
| delegation | 12 |
| time | 9 |
| revocation | 12 |
| scope | 15 |
| single use | 11 |
| transition | 6 |
| information | 12 |
| precedence | 10 |
| reachability | 9 |

Outcomes are 21 success, 100 failure, and 5 static pass. Every failure has an
exact derived `FailureId`. Every vector freezes provider/service/SQLite/
mutation/model-step call counts and safely completed checks. There are zero
effective-input collisions and zero conflicting outcomes.

The future fixture is the canonical projection defined by the validation
contract: 132,231 bytes, one final LF, SHA-256
`10ab53cd9d612c88ef77ad8ee9416e18def2c88ac0eb71f9cb3c25c409e3d0aa`.
Two independent standard-library routes must reconstruct identical bytes.
This task does not create that fixture.

## 17. Lifecycle and authorization boundaries

The lifecycle is strictly:

1. this uncommitted candidate;
2. fresh independent authority audit;
3. separately authorized authority commit/integration, if accepted;
4. separately authorized implementation from the exact accepted authority;
5. separate static/T1 synthetic implementation audit;
6. separately authorized implementation commit/integration;
7. a separately designed and approved real governance-bootstrap instance;
8. separately authorized bootstrap installation and operator pin; and
9. only then a separately authorized protected production operation.

No step authorizes its successor. Dependency installation, real service
contact, production key creation, bootstrap, protected operation, scientific
execution, publication, recovery, and Gate behavior remain separate.

## 18. Present nonclaims and completion boundary

No real private key, public trust root, credential, endpoint, issuer, pin,
configuration, binding, authorization, use, accepted object, result, or
scientific artifact is created. No dependency is installed or imported. No
native library is loaded. No protected operation, model step, policy,
measurement, simulation, trajectory, runner, finalizer, publication,
recovery, or Gate operation runs.

The only next possible stage is a fresh independent I-4 authority audit. It
has not begun.
