# AWS-C0 Material Identity and Runtime Validation Correction Authority Amendment

Status: **PROSPECTIVE AUTHORITY ONLY — NO IMPLEMENTATION, DEPLOYMENT, AWS,
CONTAINER, OR SCIENTIFIC EXECUTION AUTHORITY**

Authority identifier:
`EBU-AWS-C0-MATERIAL-IDENTITY-RUNTIME-VALIDATION-CORRECTION-AUTHORITY-v1`.

The exact accepted base is commit
`6eb39db6606159812b0995b7dbf2fb09948360ad`, tree
`75b8c651a12ba973c9c1ce81bd4355c463e306f5`. This amendment adds exactly
the six authority files named by its implementation-path manifest, all mode
`100644`. It changes no accepted file and authorizes no commit, merge, push,
AWS call, network call, Docker or systemd operation, package installation, or
scientific execution.

## 1. Narrow correction boundary

All accepted AWS-C0 authorities remain in force. The preparation object count
remains exactly 21, the evidence-root category count remains exactly 12, and
the cost vector remains exactly 22 dimensions. Stage E remains accepted and
finished. Stage F remains frozen and requires its own AWS/Linux binding,
scientific packet, validation, and explicit execution authorization.

This amendment closes one representational gap: retrieval-v2 already had to
verify all 21 pre-live objects, but its allowed `record_or_object_identity`
kinds did not name the three existing operator-bootstrap records or the eight
raw implementation artifacts. It also makes adversarial validation of the
already-authorized runtime requirements mandatory. It does not weaken or
replace any prior requirement.

It replaces the authority-audit and corrected-static-validation root schemas
with `aws_c0_material_runtime_authority_audit/v2` and
`aws_c0_material_runtime_static_validation/v2`. Their semantic root-category
positions do not change. Launch-v3, retrieval, and final-manifest validation
must use the v2 identities; the corrected retrieval and final-manifest schemas
are `aws_c0_retrieval_verification/v3` and `aws_c0_final_manifest/v3` because
their closed material-set fields change. Start becomes
`aws_c0_start_receipt/v4` to bind the new runtime-start-attestation bundle.
Within the unchanged 21-object preparation set, live-packet-v3 replaces
live-packet-v2. Later live-authorization-v3 and safe-close-v2 replace their
v2 and v1 predecessors. Two new non-roots are produced only after execution
starts: runtime-start-attestation-bundle-v1 and
ssm-completion-observation-v1. The remaining root-category versions are
unchanged.

Audit-v2 is produced only after the relevant Git events exist. It binds the
accepted base, rejected diagnostic coordinate and parent, exact candidate and
integration coordinates, six authority path hash/mode rows, the later one-path
reachability candidate/integration coordinate and row, the same fourteen
implementation candidate/integration rows, parents, trees, modes, hashes, and
an explicit ancestry audit. This prospective document names targets and
derivation rules only; it never predicts a future commit, tree, blob, VersionId,
or receipt.

Static-validation-v2 is the exact canonical `--output` root. It binds all four
validation contracts, validator software and configuration identities, the
exact fourteen implementation hash/mode rows, scope counts 150/164/100/114,
and four ordered contract groups containing the exact 66, 84, 108, and 66
case-ID sequences: exactly 324 distinct closed per-case receipts plus group
and total recomputed aggregates.
PASS requires every case PASS, every path and ancestry predicate PASS, all
zero-science counters zero, and no skipped, generic, marker-only, or
unexercised coordinate.

## 2. Exact eleven material identities

The existing 21-object arithmetic remains:

1. eight implementation artifacts;
2. three operator-bootstrap records;
3. preparation-packet-v2 and preparation-authorization-v2;
4. private infrastructure snapshot, authority audit, corrected static
   validation, cost-model-v2, closure-seed-v1, launch-v3,
   preparation-closure-v2, and live-packet-v3.

The eight artifacts use the single identity kind
`aws_c0_implementation_artifact/v1`. Its identity SHA-256 is the SHA-256 of
the canonical `aws_c0_implementation_artifact_preimage/v1`, which binds:

- the exact ordered artifact position, implementation path, and role;
- complete published artifact byte count and SHA-256;
- mode `100644`;
- the accepted implementation commit and tree;
- the exact publication key; and
- the exact S3 bucket/key/VersionId/byte-count/SHA-256/checksum receipt.

The artifact receipt SHA-256 and byte count must equal the published artifact
byte fields, and its key must equal the publication key. The eight ordered
path/role pairs are frozen in the contract. A generated ZIP, OCI archive, or
runtime-policy object is identified by its sealed artifact-output path; its
source/build derivation remains bound by the prior reproducible-build packet.
OCI manifest digest and image-config identity are distinct values and may
never be substituted for one another.

The three bootstrap objects retain their existing kinds, in exact order:

1. `aws_c0_operator_bootstrap_packet/v1`;
2. `aws_c0_operator_bootstrap_authorization/v1`; and
3. `aws_c0_operator_bootstrap_closure/v1`.

Each bootstrap verification row embeds its complete canonical record bytes.
The identity, complete-byte SHA-256, byte count, publication key, and exact S3
receipt must all agree. A generic bootstrap kind or opaque digest refuses.

## 3. Non-tautological retrieval closure

Retrieval must verify exactly the 21 pre-live objects by exact version and
complete bytes. The expected set is derived from the sealed packet and this
authority's ordered composition before any observed result count is known.
`expected_object_count = len(verified_objects)` is forbidden.

The expected total is computed from independent sealed inputs:

```text
expected_coordinate_union = disjoint_union(
    pre_live_set,
    additional_root_set,
    live_authorization_set,
    safe_close_set,
    ssm_completion_observation_set,
    resource_use_set,
    derived_usage_observation_set,
    synthetic_manifest_set,
    runtime_start_attestation_bundle_set,
    attempt_claim_set,
    checkpoint_payload_set,
    packet_declared_other_material_set)
```

Every set is an exact ordered array of identity plus immutable object receipt;
its declared count equals its array length. Coordinate identity is the tuple
of bucket identity, key, and VersionId. Every pair of sets must be disjoint,
every identity must be unique in the union, and the observed verified set must
equal the independently constructed expected union. `pre_live_set` is exactly
21 and already contains audit-v2, static-v2, snapshot, and launch, so those
four roots are forbidden from `additional_root_set`. The latter contains the
other roots available before retrieval: start-v4, every heartbeat, every
checkpoint, the terminal when present, finalizer, and cost.

Complete attempts require one live authorization, safe-close receipt,
successful SSM-completion observation, resource-use closure,
runtime-start-attestation bundle, and durable attempt claim. The derived-usage
set is exactly the non-null usage-observation receipts referenced by the 22
resource-use rows, so its sealed count is from zero through 22 without future
prediction.
There is one checkpoint payload per checkpoint. The synthetic-manifest set is
one only for SUCCESS and empty for FAIL-AFTER-CHECKPOINT and TIMEOUT. Every
packet-declared other material object is an exact coordinate already carried
by live-packet-v3, then counted and verified. With one heartbeat, one
checkpoint, no derived-usage or other material, and SUCCESS the exact FULL
union is 35; the two fully evidenced failure modes have 34. No unknown, overlapping,
duplicate, unversioned, latest-selected, delete-marked, or omitted coordinate
is permitted.

For a genuine missing-terminal HISTORY_FALLBACK, the additional-root formula
is `H + C + 3 + terminal_present`, with `terminal_present = 0`; FULL has
`terminal_present = 1`. Other conditional sets are counted exactly when their
coordinates exist and their absence is enumerated; no single fallback total
is fabricated. The synthetic-manifest
identity is non-null with a singleton set only for SUCCESS and is exactly null
with an empty set for both failure modes.

Retrieval-verification-v3 is a complete root schema, not a coverage fragment.
It binds root-common, the fixed 12 semantic categories, exact predecessor and
publication orders, the material-coverage union, S3/history transcripts, cost
identity and receipt, dispositions, and complete/incomplete failure union.
Cost bytes are published before retrieval bytes, while the semantic manifest
order remains retrieval then cost. A fully evidenced FAIL-AFTER-CHECKPOINT or
TIMEOUT has all required roots and empty missing categories; a genuinely absent
terminal is HISTORY_FALLBACK and never receives a fabricated terminal.

Final-manifest-v3 is likewise a complete root. It binds the eleven prior-root
identities in semantic order, offsets, retrieval-v3, cost-v2, safe-close-v2,
SSM completion, terminal outcome, completeness, and final disposition. Its
publication target is predeclared, but its future Put receipt is bound only by
the later non-root final-manifest-publication-observation-v1 and returned via
the closure response. PASS and fully evidenced FAIL use FULL; missing material
uses INCOMPLETE/HISTORY_FALLBACK.

## 4. Mandatory runtime and adversarial validation

The future validator and exact unit target must execute one distinct witness
or falsifier for every validation coordinate. A case identifier, mutation
fixture, validator function, expected refusal/result, and observed result are
bound one-to-one. Counting case identifiers, searching marker strings, or
routing unrelated themes to a generic malformed-launch/helper check is not
case execution.

The additive cases require concrete adversarial witnesses for all of the
following:

- no CloudFormation parameter, environment value, or workflow input may
  predict a resource's own ARN, VersionId, digest, or other future output;
- `states:DescribeExecution` and `states:GetExecutionHistory` use an exact
  execution ARN, or a separately proven valid resource wildcard plus exact
  request/condition binding; a state-machine ARN is not a substitute;
- every service-level failure after StartInstances converges on the single
  non-reentrant stop observation and a constructible closure response;
- an ASL payload template cannot contain both `field` and `field.$` for one
  logical output field;
- safe-close verifies one accepted, null-failure, same-attempt start-v4 and
  one fresh same-attempt heartbeat zero with null predecessor, exact receipts,
  and the exact RUNNING execution;
- every root is validated against its complete closed schema and all
  cross-bindings before PASS; unknown or extra material objects refuse;
- every cost integer is nonnegative, every denominator is positive, every
  range/product/sum is bounded, and the selected rational is proven at least
  every applicable authenticated observed price/tier/minimum;
- the pre-start runtime check exact-version-fetches every bound object and
  freshly reconstructs every required control through the sealed 63-row
  action/resource plan; hashing stored preimages is insufficient. The 63 rows
  are the closed allowed universe, while the reconstruction plan explicitly
  states which rows each required control consumes and proves full coverage;
- OCI manifest digest, config identity, and runtime container identity remain
  distinct and cross-bound;
- S3 uses checksum mode, authenticates the returned checksum and VersionId,
  consumes every version page, and refuses duplicate coordinates, delete
  markers, unexpected versions, latest/HEAD substitution, or missing headers;
- SSM command, systemd invocation, and container observations are
  authenticated, exact, and cross-bound rather than inferred from labels;
- API-call, transition, request, Lambda-duration, and instance-running maxima
  contain every reachable path before all sealed deadlines;
- SSM command timeout contains the controller's complete bounded download,
  validation, exclusive-write, and nonblocking handoff work; and
- `scripts/validate_aws_c0_static.py --source <repo> --output <path>` accepts
  only those arguments, writes exactly one deterministic canonical receipt to
  the requested path using exclusive creation, prints no substitute receipt,
  and returns nonzero without a PASS receipt on refusal. A refusal leaves no
  partial, temporary, destination, or PASS file behind.

The contract freezes IDs R01 through R63 as ordered structural objects, not
labels. Every row has exact action, resource selector, use/condition,
pagination-bound binding, control owner, and reconstruction output kind. Each
of the eleven controls has an exact ordered row list. Its row observations are
CALLED with authenticated exact request/response bytes or NOT_CALLED with a
false sealed condition; ALWAYS rows cannot be skipped. One closed tagged union
defines the eleven output preimages, kinds, freshness fields, and dispositions.
Each output carries both the strict base64 canonical bytes and a decoded JSON
value validated against its exact closed control-specific schema. The validator
must decode, canonicalize, compare full bytes, recompute byte count, SHA-256,
identity and kind, and recompute `freshness_seconds <= max_freshness_seconds`.
CALLED rows require authenticated HTTP-200 API success receipts; NOT_CALLED is
permitted only for a declared false condition and has no receipt or fabricated
row output.
Unknown rows, generic strings, unaccounted rows, stale results, and undeclared
reads refuse.

Live-packet-v3 contains the complete pre-start plan and reconstruction set and
their one-way identities; neither includes the other's future identity.
Runtime-start-attestation-bundle-v1 is published after handoff without an
embedded self identity, record SHA, or object receipt. Start-v4 binds its
complete-byte identity and exact receipt. The bundle binds live-packet-v3 and
its reconstruction-set identity, the exact predeclared SSM dispatch-request
identity and preimage, systemd invocation, and distinct OCI
manifest/config/container identities with
fixed named hardening fields. It cannot claim the command's future terminal
status or AWS-generated CommandId. The request preimage binds document version,
target, canonical parameters, attempt, client request token, expected command
time bounds, and the canonical workflow execution identity/ARN.

This correction explicitly extends the inherited SSM/controller interface;
there is no ambient or hidden transport. The SSM document adds only
`WorkflowExecutionArn`, `SsmDispatchRequestCanonicalJsonBase64`, and
`SsmDispatchRequestSha256`, all with `interpolationType: ENV_VAR` and closed
patterns. `prepare-request` receives the corresponding three explicit flags in
the exact argv frozen by the contract. It exclusively writes the existing
root-owned mode-0600 `<attempt>.source.json` sidecar, now binding those complete
request bytes/hash/identity and workflow ARN/identity in addition to the launch
bucket/key/VersionId/hash and rehearsal/attempt. `run` cross-verifies the launch
request, sidecar, and predeclared request before runtime start. The final SSM
command remains only the fixed nonblocking systemd handoff.

Step Functions obtains CommandId from SendCommand. After GetCommandInvocation
reaches a terminal result, the supervisor publishes
ssm-completion-observation-v1 binding that actual CommandId and command identity
to the predeclared request. Safe-close-v2 alone combines an accepted
start-v4, fresh same-attempt heartbeat zero with null predecessor, exact
successful SSM completion, RUNNING workflow, and equal attempt/prefix/workflow
and dispatch-request bindings. The sole workflow-execution identity kind in
start-v4, the runtime bundle, completion, safe-close-v2, retrieval-v3, and
final-manifest-v3 is `aws_step_functions_standard_execution/v1`. This chronology
is acyclic and adds neither a pre-live object nor a
root category. Refused or failed start-v4 records retain every start-v3 field
but null all success-only attestations and carry a typed phase and code. The
legacy `ssm_command_identity` field is null in start-v4 because CommandId does
not yet exist; its replacement is the exact predeclared dispatch-request
identity and preimage.

A TIMEOUT can be a complete outcome failure only when a durable terminal root
records `AWS_C0_SYNTHETIC_FAIL`, phase `WORKER_TIMEOUT`, the sealed timeout
code, exact final sequences, and null synthetic manifest. It then follows the
full stopped/retrieved/costed/manifested chain and returns FULL with final FAIL.
A truly absent terminal is different: it produces HISTORY_FALLBACK,
INCOMPLETE, a null terminal coordinate, and an exact missing-terminal category.
The validator has distinct positive and negative witnesses for both paths.
The additive table is exactly 20 positive plus 46 negative coordinates, still
66 total; together with the preserved 258 it produces exactly 324 distinct
case receipts. Every additive row carries its exact base fixture, operator ID,
target file and JSON/AST selector, unique deterministic constructor and
arguments, expected disposition, and expected code. Rebalancing the two
classes does not remove a semantic axis.

The existing P07, P12, P16, and N41 coordinates have explicit independent
subcases for the dispatch-request/CommandId boundary, successful completion,
canonical workflow kind, every safe-close predicate, each retrieval set,
observed-usage coordinates exactly once, maximum-substitution rows carrying no
usage coordinate, and separate derived-count, derived-hash, and derived-set
mismatch refusals. The case count remains unchanged: each coordinate emits one
top-level receipt that records the exact subcase count and hashes the ordered
receipts of every distinct callable. A generic helper cannot substitute for
multiple named subcases.

## 5. Diagnostic classification and future sequence

Commit `475fc1f59e04bc4f76132acf8c37a4bfea2eafde`, tree
`3eb779aaf06b928c62e9d8081c25c9607bbdf6bb`, sole parent
`6eb39db6606159812b0995b7dbf2fb09948360ad`, is classified exactly as
`NONACCEPTED_MATERIAL_IDENTITY_RUNTIME_VALIDATION_BLOCKED_DESIGN_SOURCE`.
It is diagnostic evidence only and must never be a base, parent, ancestor,
merge input, cherry-pick source, or accepted implementation source.

After separate audit and acceptance, the only permitted sequence is:

1. integrate these exact six authority files;
2. modify only `tests/framework/test_validation_reachability.py`, adding zero
   unique paths;
3. separately audit and integrate that reachability correction; and
4. build the corrected implementation in the same exact 14 new paths already
   authorized by the predecessor authority.

The sealed reachability scope counts are global 150 at authority-only and 164
at completed implementation, and descendant 100 at authority-only and 114 at
completed implementation. The reachability step changes no unique-path count.

Completion marker:
`AWS_C0_MATERIAL_IDENTITY_RUNTIME_VALIDATION_CORRECTION_AUTHORITY_COMPLETE`.
