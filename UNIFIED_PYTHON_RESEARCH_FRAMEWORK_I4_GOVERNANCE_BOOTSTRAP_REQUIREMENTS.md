# Unified Python Research Framework I-4 Governance Bootstrap Requirements

Status: prospective requirements only; no bootstrap instance exists; production
authorization remains disabled.

## 1. Purpose and authority boundary

This document defines the governance evidence that a later, separately
authorized Framework I-4 production bootstrap must supply. Its mechanical
companion is
`unified_python_research_framework_i4_governance_bootstrap_schema.json`.
Together they specify requirements; they do not provide an instance, trust
root, public key, service address, credential, secret, installation command,
operator pin, approval, or activation record.

The I-4 authority amendment and mechanical contract remain authoritative for
authorization semantics. This pair is authoritative only for the production
governance bootstrap boundary. A conflict between this document and its JSON
Schema is an integrity failure. A conflict with the I-4 authorization
semantics is also an integrity failure. Neither permits selective adoption.

Creating, reviewing, approving, installing, pinning, replacing, or activating
a bootstrap instance is outside this documentation stage. Until all later
lifecycle stages have been separately authorized and completed, every
protected production interface must fail `PRODUCTION_BOOTSTRAP_MISSING` before
provider, service, SQLite, registry, or ledger effects.

## 2. Artifact and review rules

A candidate bootstrap instance must:

- be strict UTF-8 JSON with no byte-order mark, duplicate member, non-finite
  number, carriage return, or trailing data;
- conform to JSON Schema Draft 2020-12 and the complete companion schema;
- use schema version 1 and a unique scientific bootstrap identifier;
- remain `DRAFT` during preparation and become
  `INDEPENDENTLY_REVIEWED` only through recorded independent review;
- become `APPROVED_FOR_SEPARATELY_AUTHORIZED_INSTALLATION` only after all five
  required approval records are valid and the scientific boundary is
  unchanged; and
- receive a raw SHA-256 digest, an ECJ-1 canonical digest, byte length, custody
  record, and immutable evidence reference before installation is considered.

Schema validity is necessary but insufficient. Independent reviewers must also
verify cross-reference identity, date ordering, key uniqueness, custodian
independence, issuer ceilings, sequence genesis, filesystem qualification,
evidence availability, and absence of prohibited content. JSON Schema format
annotations such as `uri` do not replace that review.

The reserved `https://ebu.invalid/` schema identifier names this requirements
schema only. It is deliberately non-live and is not a production service
endpoint.

## 3. Trust profile

The instance must identify one immutable trust-profile registry object by
exact object reference and content hash. Its signature profile is exactly
`EBU-Authorization-Ed25519-V1`.

The trust profile contains exactly:

- three distinct production issuer-root public keys with threshold two;
- three distinct production revocation-root public keys with threshold two;
- three distinct production trusted-time public keys, of which one valid
  response signature is required by the I-4 contract;
- maximum delegation depth four;
- maximum trusted-time response age 30 seconds; and
- maximum revocation-object lifetime 300 seconds.

Each public root supplies an `ed25519:` key ID derived from its actual 32-byte
public key, canonical unpadded base64url public bytes, an exact validity
interval, and immutable custody-evidence references. The same physical or
logical key must not silently fill multiple independent roots or roles.

Validation-namespace keys, fixed synthetic validation keys, and any key used
by the I-4 validation fixture are forbidden. Reviewers must compare the real
root inventory against the validation contract rather than relying only on a
name pattern. Every public key and signature remains subject to the structural
and profile checks in the I-4 mechanical contract.

## 4. Custody and key lifecycle

Every issuer root, revocation root, and trusted-time key must have a named
accountable custodian, an approved custody-policy reference, and evidence of a
qualified hardware boundary. The assignments must cover all configured keys
and explicitly record which key holders are independent of one another.

The bootstrap must demonstrate separation of duties sufficient to prevent one
person or one administrative failure domain from satisfying a two-of-three
root threshold. The same independence requirement applies to the authorities
that approve key lifecycle actions.

Four independently reviewable procedures are mandatory:

- routine key rotation;
- ordinary revocation;
- suspected or confirmed compromise response; and
- emergency replacement.

Each procedure identifies its governing authority, requires at least two
approvers, and references durable evidence. Procedures must define detection,
containment, notification, effective time, sequence handling, evidence
preservation, dependent-profile replacement, and rollback prevention.
Compromise response must fail closed while key status is uncertain. Emergency
replacement does not permit an in-place trust-pin rewrite; it requires new
authority and the pin lifecycle in section 7.

Private keys and hardware-bound signing credentials are never stored in the
bootstrap instance or this repository. The instance contains only public
material and evidence references.

## 5. Issuer governance and ceilings

At least one production issuer must be enumerated. Every issuer entry binds:

- a stable issuer identity and legal-identity evidence;
- a plain-language governance role;
- its exact active public keys;
- the maximum stages and exactly enumerated operations it may authorize;
- allowed target-namespace prefixes and target-kind identifiers;
- whether delegation is allowed and, if so, a maximum depth no greater than
  four;
- explicit exclusions; and
- approval-record references.

Operation ceilings are selected only from the closed I-4 vocabulary:

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

An issuer ceiling is a maximum, not a grant to any caller and not evidence that
the named stage is implemented. Each actual authorization remains limited to
one exact operation and exact targets under the I-4 contract. Delegated scope
must strictly attenuate its parent; issuers may not combine parent scopes,
broaden exclusions, or exceed the profile depth.

Every production namespace must be real, owned, and reviewed. The synthetic
validation namespace is forbidden even if an issuer record would otherwise
pass schema validation.

## 6. Registry, time, and revocation services

The instance identifies three production services: issuer registry, trusted
time, and revocation. Each uses an organization-controlled HTTPS endpoint,
transport-security evidence, and operator-monitoring evidence. Localhost,
loopback, reserved validation endpoints, and example or invalid domains are
forbidden.

The issuer-registry and revocation services each supply:

- a stable service identity;
- an exact initial sequence;
- an immutable genesis snapshot reference;
- independent genesis evidence;
- acknowledgement of the exact predecessor rule; and
- evidence for transport security and operational monitoring.

Their initial sequence and genesis material must be mutually consistent with
the I-4 `GENESIS` rule. Review must establish that no prior production history
is being omitted. Once accepted, sequence state cannot be reset by reinstall,
restore, replacement, or disaster recovery.

The trusted-time service supplies its service identity, endpoint, initial
sequence, genesis evidence, transport-security evidence, and monitoring
evidence. Its key set is the exact time-key set in the trust profile. Operators
must monitor freshness, monotonic sequence, replay, equivocation, endpoint
identity, and key status. Local wall-clock time is not a substitute for a
validated response.

## 7. Operator trust-pin ceremony

Installation requires a two-person operator ceremony. The two operators must
independently receive and compare the exact profile object reference and exact
profile content hash over at least two distinct out-of-band digest channels.
The bootstrap records the evidence for those confirmations, the reviewed
installation command, and a post-install readback of the effective pin.

The ceremony must verify the bytes actually installed, not a filename, mutable
location, display label, or latest-version pointer. A mismatch, missing
channel, missing operator, unreadable pin, or uncertain write outcome stops the
installation. Rollback is forbidden. Any replacement, including emergency
replacement, requires a new approved authority artifact and a new ceremony.

This requirements document supplies neither an installation command nor pin
bytes. Merely producing a schema-valid instance cannot activate production.

## 8. Authorization-use store

The production authorization-use database must have one explicit normalized
absolute path ending in `authorization-use-v1.sqlite3`. The path may not be
derived from the environment, current directory, implicit default, temporary
directory, symlink, or network location.

Only qualified local APFS, ext4, XFS, or NTFS storage is eligible. The
bootstrap records the filesystem kind and qualification evidence and
affirmatively rejects network filesystems. Overlay, FUSE, tmpfs, ramdisk,
FAT/exFAT, distributed, and unknown storage remain ineligible under the I-4
contract.

The instance records:

- a SQLite version on the accepted `3.46.0 <= version < 4.0.0` line;
- schema version 1;
- the dedicated owner and group identities;
- file mode `0600` and directory mode `0700`;
- access-control review evidence; and
- durability qualification evidence.

Operators must independently confirm the exact schema, application ID,
connection settings, local-durability properties, directory ancestry,
ownership, permissions, and absence of alternate database paths before the
pin may become effective. Schema validity does not prove filesystem behavior.

## 9. Backup, recovery, and permanence

The bootstrap references an approved encrypted-backup policy, retention
policy, disaster authority, and completed restore-test evidence. Backup
custody must preserve the same access and separation-of-duties boundary as the
live store.

Consumption is permanent. Restore, failover, operator error, disaster
recovery, schema migration, or profile replacement must never make a consumed
use key available again. Recovery must preserve and verify the exact coupled
authorization-use and operational-ledger rows. A missing row, partial pair,
mismatch, unreadable store, uncertain chronology, or inability to prove the
latest durable state fails closed and requires separate recovery authority.

No bootstrap approval may waive the I-4 ambiguous-commit rules or authorize a
second mutation attempt.

## 10. Audit and monitoring

The instance identifies a real append-only remote audit destination and an
access-review frequency. It requires monitoring for registry and revocation
sequence progression, equivocation, trusted-time freshness and sequence, pin
identity, store health, failed authorization attempts, ambiguous outcomes,
and operator access.

Audit configuration must preserve scientific-data minimization and must not
become an alternate authorization channel. Logs may record hashes, stable
identifiers, decisions, and evidence references, but may not contain private
keys, credentials, secrets, or unapproved scientific payloads.

The bootstrap references immutable records for:

- the exact dependency receipt matching the UQ-25 decision;
- security review;
- license and notice review; and
- independent authority audit.

Operational monitoring evidence must cover detection ownership, escalation,
retention, clock source, access, and tested incident response. An unavailable
or untrusted required service causes fail-closed rejection; monitoring cannot
convert uncertainty into authorization.

## 11. Required approvals

Five distinct review domains must record `APPROVED` decisions: security,
license, governance, operations, and scientific boundary. Every approval names
the accountable approver, role, exact decision time, and immutable record
reference.

Approvers must review the same raw and canonical bootstrap identities. The
security approval covers keys, provider receipt, endpoints, storage, access,
monitoring, incident handling, and backup. The license approval covers the
exact PyNaCl, libsodium, cffi, and pycparser artifacts and notices. Governance
covers identities, custody, thresholds, delegation, ceilings, replacement,
and evidence. Operations covers service readiness, the pin ceremony, local
durability, backup, restore, and monitoring. Scientific-boundary approval
confirms that the bootstrap neither changes frozen scientific semantics nor
authorizes execution by itself.

One person may not silently approve incompatible roles where independence is
required. Any material change after approval invalidates the affected
approvals and requires a new reviewed instance.

## 12. Prohibited content and nonclaims

The bootstrap instance must attest that it contains no private key,
credential, secret, validation key, or placeholder and does not self-activate.
Reviewers must verify that attestation against the actual bytes and referenced
delivery process.

The instance must not contain bearer tokens, passwords, session material,
private service credentials, signing seeds, recovery secrets, hardware-module
unlock data, synthetic test keys, or unresolved sample values. Public service
endpoints and public keys belong only in the future reviewed instance, never
in this requirements candidate.

Neither this document nor a future instance:

- authorizes dependency installation or code implementation;
- grants an operation or consumes an authorization;
- creates a capability or scientific-execution lease;
- proves a provider, endpoint, filesystem, backup, or operator is trustworthy;
- changes I-1 through I-3 behavior or any scientific hypothesis;
- authorizes a model tick, trajectory, experiment, interpretation,
  publication, correction, or recovery; or
- permits distributed single-use claims.

## 13. Separately authorized lifecycle

The earliest possible subsequent work is preparation of a real bootstrap
instance under new authority. It must be followed by independent security,
license, governance, operations, and scientific-boundary review. Installation
and the two-person pin ceremony require another explicit authorization after
approval. Production activation requires implementation acceptance and its
own authorization after successful permitted validation.

No later lifecycle stage has begun. A missing, inconsistent, expired,
unavailable, unapproved, altered, or unverifiable requirement leaves
production disabled.
