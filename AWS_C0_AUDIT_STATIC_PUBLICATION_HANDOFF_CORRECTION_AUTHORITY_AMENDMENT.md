# AWS-C0 audit/static publication handoff correction authority

Status: **PROPOSED AUTHORITY ONLY — NO AWS, DEPLOYMENT, CONTAINER, OR
SCIENTIFIC EXECUTION AUTHORITY**.

This additive authority is based only on commit
`6059cbdcd2ee03085c9c03b4f872b4a46241b775`, tree
`5c84e633b590b5b84d0a8a85824db4e1addbb827`. It adds exactly the six
mode-`100644` files named by its implementation-path manifest. It does not
modify, delete, rename, stage, commit, deploy, publish, or execute anything.

## Narrow defect and correction

The accepted `aws_c0_material_runtime_static_validation/v2` design makes the
static-validation root depend on a future S3 coordinate for the authority-audit
root without defining a public, deterministic handoff that can first create
the audit bytes, conditionally publish them, and only then create the static
root. A single invocation cannot truthfully predict its own or a predecessor's
future S3 VersionId. This authority replaces the AUDIT-category root with
`aws_c0_audit_static_handoff_authority_audit/v3` and the STATIC-category root
with `aws_c0_material_runtime_static_validation/v3`, without adding categories
or pre-live slots.

Audit-v3 embeds, but does not separately publish, complete canonical bytes for
`aws_c0_material_runtime_authority_audit/v2`. Those embedded bytes must
validate exactly against `$defs/authority_audit_v2` in the accepted
material-correction evidence schema (mode `100644`, blob
`fe9a08b2e93a9e50094c57b3b6d41f3b82082098`, 769841 bytes, SHA-256
`c8edb270401e0edd740a4eb4fa6da0c10410d28c0b891e0c38b03148c097fe99`).
That includes its accepted base and diagnostic, full authority fields,
`record_class`, all four authority IDs, all three Stage/science false fields,
the exact ten zero-science counters, `observed_utc`, `record_sha256`, and the
accepted 6/1/14 path structure. Audit-v3 then binds the actual handoff-authority
candidate/integration, handoff-reachability candidate/integration, and final
implementation candidate/integration commits, trees, complete parent arrays,
literal path rows, modes, blobs, SHA-256 values, and ancestry. These coordinates
are filled only after final integration; this prospective authority predicts
none of them.

The correction also versions the cyclic dispatch-request profile as
`aws_c0_ssm_dispatch_request/v2`. The semantic request never contains the two
fields which transport its own canonical bytes and digest. Those two fields
exist only in the outer SendCommand parameter envelope.

The fixed programme invariants remain:

- 21 pre-live objects, with audit-v3 and static-v3 occupying the same two
  pre-live slots previously occupied by audit-v2 and static-v2;
- 12 semantic evidence-root categories, with AUDIT using audit-v3 and STATIC
  using static-v3;
- 22 cost dimensions and the accepted 63-row read plan;
- Stage E is accepted and finished;
- Stage F remains frozen behind its separate AWS/Linux binding, scientific packet,
  validation, and authorization;
- zero model, simulation, trajectory, Gate, scientific runner, interpretation,
  or publication work.

## Deterministic public CLI

The future `scripts/validate_aws_c0_static.py` interface has exactly two modes.
Arguments are parsed from `argv` only. The implementation must not read an
environment variable, stdin, a socket, a metadata endpoint, a credential
provider, a network service, or an undeclared file. Unknown, duplicate,
missing, reordered-as-value, empty, or mode-inapplicable arguments refuse.

### Mode A: authority audit

```text
--mode authority-audit --source <absolute-final-implementation-integration-repository> --output <exclusive-absolute-path>
```

The source must be a normalized, non-symlink repository path whose HEAD is the
final corrected implementation integration commit. That integration commit
must have the exact accepted reachability integration as first parent and the
exact implementation candidate as second parent. The implementation candidate
must have the reachability integration as its sole parent. The accepted
authority candidate/integration and reachability candidate/integration must
have the exact path sets, modes, bytes, hashes, trees, and parents prescribed
by the applicable authorities. The nonaccepted diagnostic sibling must not be
an ancestor, parent, merge input, cherry-pick source, or byte source.

Mode A emits one canonical
`aws_c0_audit_static_handoff_authority_audit/v3` root candidate after the final
implementation integration exists. Its embedded prior audit-v2 bytes are
validated against the frozen prior schema and reconstructed exactly; they are
not another pre-live object. Audit-v3 contains no
publication key, S3 observation, VersionId, PUT response, or predicted
publication identity. Only after `record_sha256` exists is the publication key
derived out of band as
`rehearsal/aws-c0/prelive/authority-audit/<record_sha256>.json`.

Its `observed_utc` is not a wall clock. Both modes read the exact final
integration HEAD commit object's committer epoch seconds and convert them with
the frozen POSIX-UTC, proleptic-Gregorian, no-leap-second algorithm to
`YYYY-MM-DDTHH:MM:SSZ`. Static-v3 uses the same value for `observed_utc` and
`created_utc`. The modes refuse different source HEADs, environment time,
filesystem time, malformed signed-int64 input, or an epoch outside years
0001--9999.

### Mode B: static validation

```text
--mode static-validation --source <same-absolute-repository> --authority-audit-record <exact-local-canonical-file> --authority-audit-receipt <exact-local-canonical-provisional-put-observation-file> --output <exclusive-absolute-path>
```

Mode B first repeats the Mode-A source and ancestry checks. It strictly parses
the audit-v3 record, validates it against this closed schema and validates its
embedded prior audit-v2 bytes against the frozen prior schema, requires
canonical UTF-8 JSON with no final LF, recomputes
the root digest by omitting only `record_sha256`, and requires byte-for-byte
equality with a newly reconstructed audit-v3 candidate. It then strictly parses
an `aws_c0_provisional_conditional_put_observation/v1`. That observation binds a
structurally valid SigV4 `PutObject` request, constrained role session and
session policy, `If-None-Match: *`, deterministic key, VersionId, byte count,
raw SHA-256, ChecksumSHA256, status and response headers. It is deliberately
provisional: it is not claimed to be cryptographically authenticated or
non-fabricable.

Only after those checks does Mode B execute every case in the four accepted
validation contracts (324) and this correction contract (28), exactly once,
for 352 distinct case receipts. It then emits one canonical
`aws_c0_material_runtime_static_validation/v3` root candidate binding the
audit-v3 identity, closed input observation, and provisional PUT
coordinate; all five validation-contract identities; all case receipts and
ordered groups; the exact 14 implementation rows; scope counts
156/170/106/120; validator software/configuration/protocol identities and their
closed canonical preimages; each validation-contract and case-constructor
identity with its closed canonical preimage; the full
common/Stage fields and ten zero-science counters; and PASS gates. It contains
no publication observation for itself.

## Output and failure protocol

Both modes write only the requested output. The output path must be absolute,
normalized, absent, and not a symlink. The implementation creates an exclusive
temporary regular file in the destination directory, writes exactly one
compact sorted NFC canonical JSON value with no final LF, fsyncs it, installs it
without replacement, fsyncs the directory, and removes only its own temporary
file on failure. A pre-existing destination is never replaced. Every refusal
is nonzero and leaves no new destination or partial output. Stdout and stdin
are not alternate data channels.

## Acyclic preparation and publication chronology

Before the first preparation approval, the preparation packet may bind only:

1. the two exact CLI modes and argument schemas;
2. canonical/root/observation derivation algorithms and validator identities;
3. local output-path requirements and deterministic S3 key formulas;
4. the audit/static input schemas;
5. the exact once-only staging plan and rollback plan.

It must not contain predicted audit bytes, audit identity, provisional PUT
observation, VersionId, authenticated readback observation, static-v3 bytes,
static-v3 identity, or static-v3 publication observation.

After approval, the operator or separately authorized preparation workflow:

1. runs Mode A against the final implementation integration source;
2. conditionally puts the exact audit bytes at
   `rehearsal/aws-c0/prelive/authority-audit/<record_sha256>.json` with S3
   checksum mode and `If-None-Match: *`, retaining only the provisional
   structural observation;
3. runs Mode B with those exact local audit bytes and provisional observation;
4. conditionally puts the exact static-v3 bytes at
   `rehearsal/aws-c0/prelive/static-validation/<record_sha256>.json` with S3
   checksum mode and `If-None-Match: *`, retaining its provisional observation;
5. independently reads both records by exact VersionId with authenticated
   SigV4 GETs, recomputes their complete bytes, identities and checksums, and
   scans every bounded version-history page to prove exactly one matching
   version and no matching delete marker;
6. makes preparation closure and live packet bind both provisional coordinates
   and both authenticated readback observations as four complete embedded
   objects, with every identity, bucket, key, VersionId, byte count, raw hash,
   checksum and root identity recomputed and cross-bound. These embedded
   observations do not add pre-live objects; the exact count remains 21.

Every authenticated GET and ListObjectVersions observation carries exact
requested/completed UTC, approved preparation authorization, role, session,
session-policy and credential-source identities, session expiry and sealed
accounting bounds. Its decoded request binds `AWS4-HMAC-SHA256`, exact
credential scope, signed headers, signature, `x-amz-date`, canonical-request,
string-to-sign and payload hashes. Its response binds authenticated TLS server
name, protocol, peer-certificate hash, hostname and chain verification,
response-header hash and request ID. The validator recomputes ordering and
cross-session equality; wrong scope, signature, credential source, session,
expiry or time ordering refuses.

All PutObject, GetObject and ListObjectVersions requests use temporary role
credentials, so both signed-header lists include `x-amz-security-token` and
must be exactly equal. No raw session token, access secret, or secret-derived
key is persisted. While the ephemeral credential remains in memory, the
runtime records the exact non-secret canonical header map, token SHA-256 and
byte count, approved role-session and credential-source identities, canonical
request and string-to-sign hashes, credential scope, Authorization signature,
request ID, and a successful recomputation disposition, then records
zeroization. The signed Host is exactly
`<bucket>.s3.us-east-1.amazonaws.com`; it equals the canonical Host and TLS
server name. Dates, content length, checksum, checksum mode and
`If-None-Match: *` cross-bind where applicable. Later offline validation cannot
rederive a secret signature; it validates this constrained runtime attestation
together with authenticated exact-version TLS response and complete bounded
version-history evidence, without claiming cryptographic non-fabricability.

No root contains its own future publication observation. Conditional PUT plus
the later all-page uniqueness proof supplies exactly-once evidence. No
latest-object lookup is evidence. A fabricated but structurally valid
provisional observation may be used to construct static-v3, but cannot pass the
later independently authenticated readback gate. Final PASS, launch, retrieval
and final manifest require that upgrade. Failure is typed and cannot fabricate
a missing root or readback.

## Acyclic SSM dispatch envelope

`aws_c0_ssm_dispatch_request/v2` binds the document name/version, target,
attempt, and this exact ordered 21-field semantic parameter set:

1. `ArtifactBucket`
2. `ArtifactPrefix`
3. `LaunchRequestKey`
4. `LaunchRequestVersionId`
5. `LaunchRequestSha256`
6. `LaunchRequestBytes`
7. `LivePacketKey`
8. `LivePacketVersionId`
9. `LivePacketSha256`
10. `LivePacketBytes`
11. `LiveAuthorizationKey`
12. `LiveAuthorizationVersionId`
13. `LiveAuthorizationSha256`
14. `LiveAuthorizationBytes`
15. `RehearsalId`
16. `AttemptId`
17. `Region`
18. `WorkflowExecutionArn`
19. `SsmClientRequestToken`
20. `SsmExpectedCommandNotBeforeUtc`
21. `SsmExpectedCommandNotAfterUtc`

The semantic set excludes only
`SsmDispatchRequestCanonicalJsonBase64` and `SsmDispatchRequestSha256`. The
actual SendCommand parameter map is exactly the semantic set plus those two
transport fields. The Base64 field is the strict Base64 encoding of the
canonical dispatch-v2 preimage bytes; the SHA field is their lowercase SHA-256.
Neither transport field may occur anywhere in the semantic preimage, so no
fixed point is sought or accepted.

The controller receives those two values through the already explicit CLI,
decodes and verifies them, and writes the root-owned exclusive `0600` source
sidecar. The sidecar binds the semantic set, outer transport envelope, and the
three closed canonical source preimages for launch-v3, live-packet-v3 and
live-authorization-v3. Each source preimage binds exact bucket, key, VersionId,
byte count, SHA-256, rehearsal and attempt; opaque source identities refuse. No
environment file, metadata service, socket, stdin, or other hidden transport is
permitted. The controller receives every one of the 21 semantic values and the
two transport values as explicit arguments and writes exactly
`EXCLUSIVE_REGULAR_NO_SYMLINK`. The supervisor's completion observation
projects the actual SendCommand parameters back to the 21-field semantic set,
recomputes the dispatch identity, cross-binds the exact key, VersionId,
SHA-256, and byte count for launch-v3, live-packet-v3, and
live-authorization-v3, then verifies attempt/workflow/token/time and both
transport fields. Any unknown, extra, missing, duplicate, range-invalid, or
mismatched field refuses.

All integer values use the exact signed-int64 domain
`[-9223372036854775808, 9223372036854775807]`; `9223372036854775808` refuses.
The three preserved bootstrap kinds are exactly
`aws_c0_operator_bootstrap_packet/v1`,
`aws_c0_operator_bootstrap_authorization/v1`, and
`aws_c0_operator_bootstrap_closure/v1`.

## Validation and future path scope

The additive validation contract has exactly 8 positive and 20 negative cases.
Every coordinate has a deterministic local constructor, exact expected result
and code, and its own receipt; multi-axis rows contain independently executed
subcases whose ordered receipts are folded into one coordinate receipt. There
are exactly 104 independent subcases, and every `subcase_id`, callable
`operator_id`, selector, and expected code is globally unique; each also keeps
a separate stable base error class. The combined exact total is 324 + 28 = 352.

Every novel identity has a closed canonical preimage. This includes audit-v3,
its input wrapper, SigV4 and TLS evidence, validator software, validator
configuration, output protocol, each validation-contract file, each case
constructor, and each of the three versioned source identities. Opaque,
context-free, or digest-only identity claims refuse.

After this authority is separately accepted and integrated, reachability may
modify only `tests/framework/test_validation_reachability.py`, add no path, and
introduce exactly:

- `AWS_C0_AUDIT_STATIC_PUBLICATION_HANDOFF_CORRECTION_AUTHORITY_ONLY`
- `AWS_C0_AUDIT_STATIC_PUBLICATION_HANDOFF_CORRECTION_CLOSED_IMPLEMENTATION`

The later implementation still adds the same exact 14 mode-`100644` paths.
Frozen scopes are 156/170 globally and 106/120 in the descendant scope.
Globs, ignore-based scope, computed path discovery, a second reachability path,
additional implementation paths, Stage-F activation, or scientific behavior
must refuse.

Completion marker:
`AWS_C0_AUDIT_STATIC_PUBLICATION_HANDOFF_CORRECTION_AUTHORITY_COMPLETE`.
