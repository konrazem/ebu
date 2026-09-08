# SD-01 preparation scope

This additive package preserves the pinned Stage D/E/F sources and existing
Stage E execution guard. It is an **unsealed preparation**, not a complete
execution adapter or a passing Stage F binding packet. Two exact control
choices remain in `SD01_CONTROL_DECISIONS.md`.

`adapter.py` implements the derivable source, shock, H0/H1/H2/H3 and ordered
stock-balance equations. It has no campaign driver, control defaults or
execution authorization. It has only been parsed and reviewed, never imported
or called during preparation. Its transition dictionaries are internal values,
not accepted scientific evidence records. Full numerical conformance and
schema-bound trace/receipt composition remain required after the control
binding is resolved.

`mechanics.py` implements strict canonical metadata, declared identity
preimages, write-once content-addressed storage, predecessor-linked checkpoint
bundles, exact version/hash/length retrieval, result-key layout, and integer
hard-budget admission arithmetic. Tests use only arbitrary byte payloads and
metadata. These are reusable local primitives; they are not certificates for
the inherited Windows host, AWS storage, a production finalizer, or the full
v2 checkpoint schema. A corrupt checkpoint refuses; recovery cannot silently
skip it or retry a failed scientific attempt. Exact binary64 state must be
serialized as bit strings by the future runner, preserving signed zero.

`record_validation.py` reuses the frozen Stage E schema validator for complete
caller-supplied v2 records, with no invented defaults; this validates structure,
not the complete cross-record execution binding. `fold_attempts` retains all
failed-work deltas in canonical run/ordinal order and rejects counter resets.
Recovery metadata checks require every inherited recovery condition.

`build.py` checks the immutable source bytes, parses all Stage D/E/F JSON,
projects the 192 scientific cells without constructing a model state, retains
four visibly unresolved control slots, and extracts the complete frozen
scientific row and operational contracts. It downloads nothing. Commit all
implementation sources before building. For later byte-identical reconstruction,
pass `--implementation-revision` with the dossier’s pinned implementation commit.
Supply the accepted Stage E archive separately; the builder checks its frozen archive
hash and all nine base-manifest member hashes and linkage. The retained Stage E
projection is not an SD-01 benchmark. Its 33 projected slices cannot be used as
an executable allocation for 196 distinct trajectories.

The proposed operational layout uses one serial worker, an 8 GiB host and the
unchanged 4 GiB per-process cap, exact per-run 1,000-tick checkpoint boundaries,
and separate objects for every immutable trace/receipt/checkpoint/attempt.
One object manifest records exact S3 key, VersionId, SHA-256 and byte count;
retrieval verifies every byte before publishing an audit manifest. No bucket,
AWS instance or paid resource is allocated. No existing AWS-C0 resource is
assumed to authorize science. The live authorized budget is zero. The cost
arithmetic cannot be called an enforced cloud spend ceiling until all service
prices, bounded quantities, storage-retention and retrieval duration, watchdogs,
finalizer, and durable reservations are bound and independently verified.

Static build:

    python3 -B -m sd01_preparation.build --stage-e-archive /path/to/9708926559.zip --output /fresh/path/dossier.json

Synthetic mechanics checks:

    python3 -B -m unittest discover -s tests/sd01_preparation -v

Neither command imports the scientific adapter. `execution_authorization`
always refuses, including supplied dictionaries claiming approval. Frozen
route readiness files remain historical evidence and are not rewritten to
hide the inherited gap. No later route, result audit, book work, commit push,
release, publication or scientific execution is authorized by these files.
