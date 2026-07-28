# V3.0 Gate 1D Attempt 2 — Tolerance-Corrected Regeneration (Gate 1D-A record)

**This is the corrected authoritative Gate 1D diagnostic rendering.** It is a
defect-correction regeneration of the identical registered 56-run study, NOT
an independent replication, NOT a new scientific study, and NOT a release
manifest. **Attempt 1 (the parent directory) remains the immutable historical
execution record**; its artifacts are byte-identical to their state at commit
`db08d2d` and its manifest's claims are not rewritten. Passing checks are
numerical validation at declared points, never proof; the bounded service
wrapper remains outside the V2.8 D0 theorem (open problem O13).

> ### Headline
> **Every scientific value of Gate 1D is bit-identical between Attempt 1 and
> Attempt 2.** The only differences (18 fields, all in the four W2
> conservative runs) are the reserve diagnostics corrected by the registered
> tolerance: the four one-ULP reserve "crossings" disappear (1 → 0) and the
> four labels change `destructive_service` → `physical_impossibility`,
> matching their near-certificate twins. **0 reserve crossings remain in all
> 56 runs**; the primary B-vs-D result (0 service-alignment failures in 14
> comparisons) is exactly unchanged; the W2 timestep-sensitivity of the
> outcome class reported by Attempt 1 is resolved as pure diagnostic
> artifact.

## Provenance (both attempts)

| Field | Attempt 1 | Attempt 2 |
|-------|-----------|-----------|
| Preregistration commit | `239074eb9fdfb2a57b1f07352cb250d388d7bff7` | same (plan unchanged) |
| Implementation commit | `a556b4f43ea002c27b77910c76e395e9d77d7144` | + correction `86853b0b6adff0fe024fcd696694973f56bb63fb` |
| Tests/runner commit (pushed before the run) | `5886cb10a674d3861deb47a848ce9d26bbb2a4a6` | `86853b0b6adff0fe024fcd696694973f56bb63fb` |
| Results commit | `db08d2d5278179b2a4f6e2cdb3a938251eb5c96e` | (this commit) |
| Exact command | `python3 exp_v30_service.py > results/v3.0/gate1d/v30_service_alignment_stdout.txt` | `python3 exp_v30_service_attempt2.py > results/v3.0/gate1d/attempt2/v30_service_alignment_stdout.txt` |
| Attempts | exactly one; exit 0 | exactly one; exit 0; **no Attempt 3 authorized or performed** |
| Plan canonical hash | `71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020` | identical (recomputed and enforced at run start) |
| Plan raw SHA-256 | `7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c` | identical |
| Equation version | `v3.0-gate0.1` | identical |
| Python | 3.14.2 | 3.14.2 |

The Attempt-2 runner `exp_v30_service_attempt2.py` changes **output routing
only**: it imports the frozen `exp_v30_service` unmodified and overrides its
three output paths to this directory. The plan-hash gate, the certificate
gate (`r_dt ≤ 1` for all 56 runs), the no-command-line-option rule, and the
fail-closed overwrite refusal all ran unchanged. The correction commit
`86853b0` was pushed to `origin/v3.0-local-ebu-foundation` **before** the
Attempt-2 trajectory was executed, per the Gate 1D-A authorization.

## What Gate 1D-A changed (and the only thing it changed)

`service_v30.run_arm`'s reserve-crossing counter previously used the exact
strict comparison `xa < R_eff <= xb` with no tolerance. It now uses the
shared diagnostic predicate pair

```
materially_below_reserve(x, R_eff):  x < R_eff - tol(R_eff)
reserve_crossing(xb, xa, R_eff):     (not materially_below_reserve(xb, R_eff))
                                     and materially_below_reserve(xa, R_eff)
```

with the **already-registered** tolerance `tol(v) = 1e-9 * (1 + |v|)`
(`service_v30.tol`). No new threshold was invented or tuned. The predicate is
used for all Gate-1D reserve-derived diagnostics (crossing counts, the
reserve-harm predicate, reserve-related classification and falsifier fields)
and for nothing else: it is not applied to physical state updates, P1C
budgets, accepted quantities, quotes, service, unmet demand, ledgers, Allee
or dead-source thresholds, or timestep certificates (AST- and
runtime-poison-asserted in test group G14). `p1c_v29.py`, `ebu_quote_v30.py`,
and the plan JSON are unmodified.

## Artifacts

### Attempt 2 (this directory)

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_service_alignment_summary.json` | `f2b065b5040ebb9151aca7de4a85831d054c89c21d690d61bfa4dabd42a96bc4` | 132 346 |
| `v30_service_alignment_trace.jsonl.gz` | `b509606eb10c7d94500b735edb5cb31ab81616e6114081661cdf3be821fd095b` | 64 119 |
| `v30_service_alignment_stdout.txt` | `4198d587ae3002daf387b1e3a1ef7c8b98c838e0c0812fc9a16038ea9722a319` | 16 683 |

### Attempt 1 (parent directory, verified byte-identical before and after Attempt 2)

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_service_alignment_summary.json` | `bd8de06658f68ff0d1b2aa337022daf4768d0ae620fb6a3cc79e88eeab41a867` | 132 358 |
| `v30_service_alignment_trace.jsonl.gz` | `3cb97610774ee94f9dab6c777c8b6d7a3496eeeaf254d580cdf30e3babbce3ab` | 64 119 |
| `v30_service_alignment_stdout.txt` | `dacf9891ccb912641f60889f8bf9066fe7623f6aeb2cb9611d93afb3b80e4fb8` | 16 710 |
| `MANIFEST.md` | `17868276c9deb839a135ee585b03d2e401a15e628f47040fede4413e8e744232` | 13 798 |

**56 run records, 56 unique identifiers, none missing, none extra, none
dropped** (verified against Attempt 1's identifier set). Trace: 56 gzip lines,
`gzip -t` clean, strict JSON throughout (`allow_nan=False`), every numeric
field finite. The **uncompressed trace is byte-identical to Attempt 1's**
(the `.gz` container differs only in its header); the compressed sizes are
equal at 64 119 bytes.

## Validation result (see `ATTEMPT_2_COMPARISON.md` for the full method)

All 56 runs compared field-by-field by exact run identifier: **every
scientific field is exactly identical** (bit-for-bit JSON equality — no
serialization tolerance was needed), including all state trajectories,
requested/accepted actions, delivered quantities, losses, service, unmet
demand, EBU quotes and settlements, action counts, burden, viability, P1C
classifications, physical overuse, ledger values and residuals, timestep
certificates and `r_dt`, domain status, all B-vs-C observational-identity
results, and all B-vs-D service-alignment comparisons.

The complete inventory of differences is 18 diagnostic fields in the four W2
conservative runs (crossing counts, reserve-harm flags, outcome classes, and
the two informational `*_crossed_reserve` flags in the W2-conservative D-arm
alignment record). Every expected narrow consequence occurred; nothing else
changed; no genuine reserve crossing was hidden (all 52 other Attempt-1
counts were already 0).

## Outcome classes (Attempt 2, 56 runs)

| Class | Attempt 1 | Attempt 2 |
|-------|-----------|-----------|
| `preserve_and_serve` | 48 | 48 |
| `physical_impossibility` | 4 | **8** |
| `destructive_service` | 4 (the ULP artifact) | **0** |

W2's outcome class is now timestep-consistent (`physical_impossibility` at
both registered timesteps), as the physics always was.

## Test and regression totals (kept separate)

- Gate-1D suite `test_v30_service.py`: **304 passed, 0 failed, 14 groups**
  (275 pre-existing checks unweakened + 29 new Gate 1D-A checks in group G14;
  G13's stale pre-execution existence guard repaired per the commit-`8eb1696`
  precedent, still 4 checks).
- Gate 1B: quote 184/184 (21 groups), audit 19/19. Gate 1C: adversary
  150/150 (12 groups), reproduction audit 47/47.
- Released suites, unchanged, no V2.9 study regenerated: test_energy_balance
  8; test_v22 7; test_v23 4; test_v24 5; test_v25 9; test_v26 15 (+33 prior);
  test_math 34; test_v28 132; test_v29 141; test_v29_behavior 108;
  test_v29_p1c 83; test_v29_d9_d10 114; test_v29_serialization 46.

## Scope and non-claims

Attempt 2 is a **defect-correction regeneration** under the narrow Gate 1D-A
authorization: it changes only which diagnostic tolerance the already-frozen
study applies to its reserve-boundary counter. It adds no evidence beyond
Attempt 1 about capability effects (Limitation 1 of the Attempt-1 manifest
stands: no registered world has a source with more than one out-edge, so
C1/C2 remain unquantified — open problem **O14**), makes no latency or
robustness claim (Gate 1E untouched), and authorizes no actor-economy work
(Gate 2 remains paused). Open problems O1–O14 are unchanged; **O15**
(tolerance discipline for diagnostic boundary counters) is now **addressed in
implementation** by the shared predicate, with the general discipline still
to be carried into future gates. Validation is not proof.
