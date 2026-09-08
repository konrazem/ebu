# AWS-C0 runtime-artifact compatibility successor amendment

## Scope and authority

The user explicitly authorized this prospective correction, local validation
and commit, exactly two new private content-addressed S3 artifact versions, and
one fresh packet. The exact 812-byte authority statement has SHA-256
`831bbf1b4159414dd755f6a563acc7698c23d946c3944f747acb380bdb0f3c58`.
The corresponding JSON contract is the mechanical source of truth.

## Defect

Packet/v8 correctly introduces a transitive v8/v7 downstream carrier chain,
but its preserved controller and finalizer VersionIds contain the predecessor
v7/v6 runtime. Those bytes must reject the new chain. The packet/v8 Gate 1
refusal remains terminal evidence and is not replayed.

## Prospective correction

The versioned successors are packet/v9, preparation-authorization/v8,
launch/v9, preparation-closure/v8, live-packet/v9, and
live-authorization/v9. Packet/v9 binds the exact canonical identity of
`aws_c0_runtime_artifact_compatibility_successor_contract.json`.

Its eight artifact receipts consist of the six unchanged exact historical
versions plus exactly two fresh immutable successors: the committed controller
bytes and the deterministic finalizer archive built from the committed
finalizer source. Both successors use fresh content-addressed keys,
`If-None-Match: *`, versioned readback, exact length, SHA-256, and checksum
verification. No other artifact is uploaded, copied, overwritten, or deleted.

Every historical schema, packet, receipt, VersionId, and evidence file remains
unchanged. The logical pre-live object count remains 24; the fresh object count
is 18 because two runtime artifacts are new and the other six are reused.

## Preserved boundaries

AWS actions and permissions, the stopped existing `t3.small`, one-smoke limit,
USD 50 ceiling, scientific content, cleanup requirements, and all denial
boundaries are unchanged. No deployment, smoke, scientific execution, push,
merge, public publication, or release is authorized before the fresh packet
receives its exact packet-specific authorization.

Any mismatch between this amendment and its JSON contract is an integrity
failure.
