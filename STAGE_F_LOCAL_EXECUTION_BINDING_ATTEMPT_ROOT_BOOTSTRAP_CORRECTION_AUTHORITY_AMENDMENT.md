# EBU Stage F local execution-binding attempt-root bootstrap correction authority amendment

Status: **PROSPECTIVE OUTCOME-BLIND AUTHORITY CANDIDATE ONLY**

Authority ID:
`EBU-STAGE-F-LOCAL-EXECUTION-BINDING-ATTEMPT-ROOT-BOOTSTRAP-CORRECTION-AUTHORITY-v4`

Required current target: commit
`06a1b1400d5bd15cdfb50363333602c58b5ac692`, tree
`ca0bd70c96c0a6d9542ce9656be78a11465662f3`.

This amendment corrects one mechanical launch-authority contradiction: the
accepted ordinary mutation ticket required a future realized root-protection
epoch and future ledger transaction while also being required before
`CreateDirectoryW`. The exact future epoch cannot exist until the attempted
root has been created and its file identity, parent-watch record, USN record
and execution-attempt genesis have been observed. Fabricating or post-hoc
rebinding that digest is forbidden.

This package replaces that cyclic launch edge with a typed, single-use,
pre-create bootstrap ticket and an acyclic evidence chain. It does not
authorize Stage F execution and changes no scientific authority, study, route,
model, parameter, seed, stream, topology, oracle, control, falsifier, hard
limit, checkpoint rule, continuation rule or terminal scientific disposition.

`STAGE_F_LOCAL_EXECUTION_BINDING_ATTEMPT_ROOT_BOOTSTRAP_CORRECTION_CANDIDATE_COMPLETE`

## 1. Exact additive authority scope

The candidate adds exactly these six mode-`100644` regular files, in this
order:

1. `STAGE_F_LOCAL_EXECUTION_BINDING_ATTEMPT_ROOT_BOOTSTRAP_CORRECTION_AUTHORITY_AMENDMENT.md`;
2. `stage_f_local_execution_binding_attempt_root_bootstrap_correction_contract.json`;
3. `stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json`;
4. `stage_f_local_execution_binding_attempt_root_bootstrap_correction_implementation_path_manifest.json`;
5. `stage_f_local_execution_binding_attempt_root_bootstrap_correction_predecessor_manifest.json`;
6. `stage_f_local_execution_binding_attempt_root_bootstrap_correction_validation_contract.json`.

No accepted path is modified, deleted, renamed or mode-changed. Any seventh
candidate path, private host evidence in Git, symlink, submodule, ignored-state
exclusion, force-push or history rewrite refuses the candidate. These files are
prospective until a fixed-coordinate independent authority audit passes and
the exact audited commit is normally integrated.

The required target integrates the accepted v3 authority candidate
`b6452dcf69cb9ee46ce01b03f86d97a80c348713`, tree
`bd9e8610b70b9f06f15fb18d9045d2cb933e173a`, at commit
`1f4650411ea360d82df3e9f0708af32a58608729`, and its accepted reachability
candidate `4dc2d9d5fac43bb91699a0727eb36f7266996122` at the required target.
All eighteen accepted Stage F authority files and the accepted reachability
blob remain immutable.

The accepted Stage E integration remains exactly commit
`c43ead831c3e4021405985134ed564b761bb1aed`, tree
`212777d569af527ce9532ea6c836ff2225465d87`, exact-target CI run
`33231168021`, sealed artifact `9708926559`, SHA-256
`2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345`.

## 2. Precedence and narrow supersession

Precedence is:

1. exact accepted Stage D and Stage E scientific authority and evidence;
2. the required target and its eighteen accepted Stage F authority files;
3. this independently accepted and integrated six-file correction;
4. a later implementation reconstructed under all twenty-four integrated
   Stage F authority files;
5. retained private host evidence and independent audit receipts; and
6. the separate post-packet user authorization required before science.

Only the legacy `CREATE_ATTEMPT_ROOT` mutation-ticket route and its bootstrap
watch/USN/epoch/ledger joins are superseded. Every ordinary v3
`stage_f_authorized_mutation_ticket/v1` field, kind, operation, single-use rule
and scientific-authority resolution remains unchanged, except that
`CREATE_ATTEMPT_ROOT` is removed from its operation enum and always refuses.

The registered campaign order remains exactly `SD-01`, nested
`SD-01-GROWTH-v1`, then `SD-02` through `SD-14`. Nested growth remains part of
`SD-01`, so the order still contains fifteen route projections and fourteen
independent studies.

## 3. Canonical identity and privacy rules

Canonical JSON remains UTF-8 NFC with recursively sorted keys, comma/colon
separators, integer-only numbers, no insignificant whitespace and no final LF.
Duplicate keys, floats, nonfinite values, invalid UTF-8, non-NFC strings,
noncanonical Base64, trailing data or an unresolved local reference refuse.

Every identity `value` and `sha256` equals the SHA-256 of its declared complete
canonical preimage. For records carrying a self digest, the only omitted field
is respectively `bootstrap_protection_sha256`, `ticket_sha256`,
`watch_observation_sha256`, `usn_observation_sha256`,
`creation_observation_sha256`, `genesis_sha256`, `epoch_sha256` or
`ledger_sha256`. No future identity, null substitution, second omission or
presentation serialization is part of that digest rule.

Private campaign-parent and attempt-root path material and the private
transaction nonce remain only in retained private evidence. Public records may
carry their digest identities but never raw personal paths, user/profile names,
credentials, device serials or private preimage bytes.

## 4. Exact acyclic bootstrap graph

The validator constructs and hashes only already formed preimages. The closed
dependency graph is:

`B/T -> W,U,G,R -> E -> L`

where `B` is typed bootstrap protection, `T` is the typed pre-create ticket,
`W` is the typed parent-watch creation observation, `U` is the typed USN
creation range, `G` is execution-attempt genesis, `R` is the independent raw
creation observation, `E` is the realized root-protection epoch, and `L` is
ledger genesis. A private bootstrap-transaction preimage is formed before `B`
and its identity is repeated throughout this graph.

No `B`, `T`, `W`, `U`, `G` or `R` preimage contains a future epoch identity,
ledger-genesis identity or ledger-entry identity. `E` contains no future
ledger identity. Only `L`, formed after `E`, joins the realized epoch to the
new continuously held ledger.

## 5. Bootstrap protection and pre-create ticket

`stage_f_attempt_root_bootstrap_protection/v1` binds:

- the complete private bootstrap-transaction preimage and identity;
- exact campaign-parent and proposed attempt-root private path identities;
- holder PID, process-creation FILETIME and thread ID;
- the held campaign-parent anchor;
- a pending `ANCHOR_SELF_DIRECT` nonrecursive parent watch with its exact
  handle, buffer, event, OVERLAPPED and DWORD-output resources;
- the retained NTFS volume handle and exact successful raw START
  `FSCTL_QUERY_USN_JOURNAL` observation and watermark; and
- an exact `GetFileAttributesW` absent result
  `INVALID_FILE_ATTRIBUTES`/`ERROR_FILE_NOT_FOUND` completed only after the
  parent watch was pending.

Only after that complete protection and absence evidence exists may the
controller issue one `stage_f_attempt_root_mutation_ticket/v1`. The ticket is
fixed to operation `CREATE_ATTEMPT_ROOT`, exact actor, transaction, protection,
parent and attempt path identities, `CreateDirectoryW`, watch action
`FILE_ACTION_ADDED`, required USN reason bit `0x00000100`, inherited permitted
USN mask `0x80000100`, issue and expiry UTC, and
`single_use_required=true`.

The ticket contains explicit false future-identity flags and no root epoch,
ledger, watch, USN, creation or genesis identity. It must be unexpired and
immediately precede the one exact create call. Issue before pending protection
or absence, issue after create, expiry, zero consumption, reuse, cross-path use
or post-hoc rebinding refuses.

## 6. Parallel post-create evidence

After the one successful `CreateDirectoryW`, four evidence branches are formed
without depending on one another's future digest:

- `W` uses the complete typed
  `stage_f_attempt_root_watch_completion_observation` and
  `stage_f_attempt_root_watch_observation`. It retains the exact parent-watch
  resources, cycle, DWORD preimage/postimage, raw notification buffer and
  parsed `FILE_ACTION_ADDED` record. There is exactly one bootstrap-ticket
  match, zero ordinary-ticket matches and zero refused protected records.
- `U` uses the complete typed `stage_f_attempt_root_usn_range` and
  `stage_f_attempt_root_usn_observation`. It retains the original START query,
  ordered raw `FSCTL_READ_USN_JOURNAL` calls, END query, exact DWORD and buffer
  images, complete terminal range and the one matching creation record. There
  is exactly one bootstrap-ticket match, zero ordinary-ticket matches and no
  pre-ledger ledger-bijection assertion.
- `G` is `stage_f_execution_attempt_genesis/v1`, extended only with the exact
  transaction, protection, ticket and call interval. Its attempt path, parent
  watch, file ID, volume serial, created UTC and one-call consumption reconcile
  with the other branches.
- `R` is `stage_f_attempt_root_creation_observation/v1`, retaining the exact
  call inputs/result/interval and the post-create root anchor, file ID and
  volume serial.

Every branch repeats the exact same transaction, protection, ticket, actor,
path and created-object facts. Omission, duplication, reordered raw records,
wrong reason/action, parent or child reference substitution, watch resource
splice, journal gap, pre-existing-root relabeling or cross-attempt evidence
refuses.

## 7. Realized epoch and ledger-genesis closure

Only after `W`, `U`, `G` and `R` are complete is
`stage_f_root_protection_epoch/v1` hashed. It embeds the complete bootstrap
protection and ticket, all four post-create branches, the newly held attempt-
root anchor and subtree watch, immutable locks and continuous USN evidence. It
recomputes every path, actor, transaction, ticket, timestamp, file ID, volume,
watch and USN equality and proves the bootstrap ticket was consumed exactly
once.

Only after that realized epoch exists may the controller create the ledger and
form `stage_f_evidence_ledger/v1` genesis. Ledger genesis binds the exact
bootstrap transaction, protection, ticket, watch, USN, creation, execution
genesis and realized epoch identities; its held ledger-file identity and
append evidence follow the unchanged ledger rules. The ledger closes the
bootstrap transaction but is not retroactively inserted into any pre-ledger
preimage.

## 8. Effective schema and validation controls

The complete effective schema is
`stage_f_local_execution_binding_attempt_root_bootstrap_correction_schema.json`.
It has exactly 243 definitions and 52 root variants. Relative to v3 it adds 15
definitions, changes 28 and removes zero. It has exactly 2588 literal local
`$ref` occurrences and zero unresolved references. Relative to the original
143-definition v1 schema it adds 100 definitions, changes 28 and removes zero.
The contract and validation contract freeze the strict NFC UTF-8 definition
lists and every exact count.

Every historical BEC-001 through BEC-184 control is preserved byte-for-byte
and object-for-object. Exactly BEC-185 through BEC-196 are appended: one valid
bootstrap positive and nine negatives for protection splicing, issue order or
expiry, ticket reuse, genesis/epoch substitution, watch mismatch, USN mismatch,
ledger closure or future-identity cycles, legacy-ticket/post-hoc rebinding, and
privacy or nonzero science, followed by one valid current-v4 provenance positive
and one negative covering a v4 authority-row or downstream-v3 consumer splice.
The effective totals are 196 cases: 33 positive and 163 negative.

Authority drafting and audit may use only strict static parsing, hashing,
schema/meta-schema validation, definition/reference/count comparison, Git-
object inspection, AST/source inspection and deterministic in-memory synthetic
controls. They may not import the project, probe the host, contact Docker or
execute scientific behavior.

## 9. Successor provenance identities

After exact integration, the authority-set, implementation and validator
preimages use kinds `stage_f_binding_authority_set/v4`,
`stage_f_binding_implementation/v4` and `stage_f_binding_validator/v4`. The
authority set contains exactly twenty-four rows: accepted v1, v2, v3 and this
v4 package, six rows each. The implementation still contains exactly fourteen
rows. The validator still contains seven source members and the five-member
deterministic `ZIP_STORED` zipapp recipe.

The local bundle, validation receipt, readiness, independent audit, sealed
packet, post-packet authorization receipt and campaign authorization use their
declared `/v3` successor kinds and directly repeat the three v4 identities.
The bundle embeds all three complete v4 preimages. A v3 foundation identity,
an eighteen-row authority preimage, a v2 consumer, missing preimage or mismatched
direct identity refuses.

## 10. Exact later implementation scope

After authority integration, corrected reachability integration and their
independent fixed-coordinate passes, a later implementation may modify exactly
these fourteen paths and no fifteenth path:

- `.github/workflows/tests.yml`;
- `scripts/validate_stage_e_harness.py`;
- `scripts/build_stage_f_local_binding.py`;
- `scripts/validate_stage_f_local_binding.py`;
- `stage_f_binding/__init__.py`;
- `stage_f_binding/canonical.py`;
- `stage_f_binding/binding.py`;
- `stage_f_binding/durability.py`;
- `stage_f_binding/locked_zipapp_bootstrap.py`;
- `tests/stage_f_binding/__init__.py`;
- `tests/stage_f_binding/fixtures/negative_cases.json`;
- `tests/stage_f_binding/fixtures/synthetic_private_host_manifest.json`;
- `tests/stage_f_binding/test_binding_privacy_and_authorization.py`;
- `tests/stage_f_binding/test_durability_and_no_science.py`.

That implementation must internally produce—not merely validate caller-
supplied objects for—the exact raw capacity, host, suspended-process, Docker,
intent/handoff, containment and release evidence required by the accepted
authority. The bootstrap correction does not waive those independent-audit
findings and does not authorize any live host mutation during implementation
or candidate audit.

The historical authority-only closure is 70 unique paths and historical
completed closure is 82. Adding this six-file package yields 76 active
authority-only paths and twenty-four active Stage F authority rows. The later
twelve new implementation paths yield 88 completed unique paths; the other
two implementation paths overlap accepted Stage E and the reachability path is
already counted.

## 11. Required gates and zero-science boundary

The mandatory order is:

1. fixed-coordinate independent audit of this six-file authority candidate;
2. normal integration of the exact audited candidate;
3. exact one-path static reachability correction and independent audit;
4. corrected fourteen-path implementation and independent audit;
5. implementation integration and exact-target CI;
6. private/public host-binding audit;
7. per-route scientific-authority and runner closure;
8. complete campaign-binding audit and sealed packet; and
9. a new explicit post-packet user authorization before scientific execution.

No model, trajectory, runner, Gate, simulation, scientific RNG draw, outcome
inspection, result, figure, book, release, publication or Stage G action is
authorized by this candidate. Independent acceptance means only that this
exact prospective mechanical authority is ready for integration.
