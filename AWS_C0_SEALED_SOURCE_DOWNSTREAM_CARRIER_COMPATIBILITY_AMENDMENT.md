# AWS-C0 sealed-source downstream carrier compatibility amendment

## Scope and authority

The user explicitly authorized implementing, validating, and locally
committing this prospective compatibility correction and exactly one fresh
replacement atomic full-preflight and packet. The exact 778-byte authority
statement has SHA-256
`399ea646b531873609c297c09f01670083353a7648e735613b4412e948451c1b`.
The corresponding JSON contract is the mechanical source of truth.

## Defect

`aws_c0_preparation_packet/v7` and
`aws_c0_preparation_authorization/v6` correctly replace eight redundant
artifact writes with eight exact existing S3 VersionId receipts. They cannot,
however, bind the preserved downstream launch and closure schemas, which still
require packet/v6 and authorization/v5. Continuing with those older identities
would be either a validation failure or an attempt replay.

## Prospective correction

The versioned successors are packet/v8, preparation-authorization/v7,
launch/v8, preparation-closure/v7, live-packet/v8, and
live-authorization/v8. Each is cloned from its immediate predecessor and changes
only transitive carrier-kind bindings. Packet/v8 additionally binds the exact
canonical identity of
`aws_c0_sealed_source_downstream_carrier_compatibility_contract.json`.

Every historical schema remains present and byte-identical. Packet/v7 and its
eight staged objects remain terminal preserved evidence and are not replayed,
overwritten, or deleted.

## Preserved boundaries

The exact eight sealed artifact versions, logical 24-object set, sixteen fresh
record count, zero new artifact puts, AWS actions, IAM permissions, stopped
existing `t3.small`, one-smoke limit, USD 50 ceiling, scientific content, and
all denial boundaries are unchanged. The fresh preflight may temporarily add
only regional `ec2:DescribeSecurityGroups`; it must remove that permission and
dispose temporary credentials after success or failure.

No instance start, deployment, platform smoke, scientific execution, push,
merge, publication, or release is authorized before the fresh packet receives
its separately required exact packet-bound authorization.

Any mismatch between this amendment and its JSON contract is an integrity
failure.
