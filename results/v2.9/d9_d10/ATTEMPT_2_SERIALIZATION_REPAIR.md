# V2.9 Gate 2.4B — Attempt-2 serialization repair audit

This note documents, for the permanent audit trail, exactly what the
post-run serialization repair of the Attempt-2 D9/D10 result summary did and
did not touch, and reconciles the repair count reported in `MANIFEST.md`
(15 runs) with the null count observable in the committed summary (18 records).

**The physical experiment was NOT rerun.** No trajectory was regenerated, no
physical step function was called, and no scientific value (state, flow,
service, unmet demand, crossing, classification, `O_physical`, ledger residual,
timestep, or certificate datum) was altered by the repair or by this audit.
Everything below was derived from the already-committed artifacts only.

## Provenance

| Field | Value |
|-------|-------|
| Attempt-2 implementation commit | `12faa5390e6c8edb3d566e2e624a632aa4114dad` |
| Attempt-2 result commit | `2074786d4c5c8a8ea64b9f3c20008ce011667093` |
| Canonical plan hash (unchanged) | `87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a` |
| Plan file | `v29_d9_d10_plan.json` (Amendment 5; parameters unchanged) |

## Committed artifacts audited (hashes at result commit `2074786d`)

| File | SHA-256 | Bytes |
|------|---------|-------|
| `v29_d9_d10_summary.json` | `55603b5751b5b945e66165614d6c9993a6f4defadfb8aa2143f50558d536d3b4` | 267 848 |
| `v29_d9_d10_trace.jsonl.gz` | `4b1ef577c64e000566e464362703da34ddd98eacdd3fa35812523b63b3da3da5` | 2 852 962 |
| `v29_d9_d10_stdout.txt` | `c9537419b657671878df4abc05b0c44b36f4d401d0840512057c497aad528b8a` | 4 587 |
| `MANIFEST.md` (pre-clarification) | `6f62d0b93225eeefca35064fc1be69d0d3e8df4baa4c1ccc69c0ea31ed36d575` | 4 071 |
| `ATTEMPT_1_FAILURE.md` | `8040017632a8911702144ef0423e4d8de22b55ca2f2e6ab4bf45d687e050555d` | 4 367 |
| `ATTEMPT_1_stdout.txt` | `79d1def9fc5bc81672ce112639f01ba39f931407dee8c2463464fdcb4b8571ab` | 513 |

**Pre-repair summary SHA: not preserved.** The repair was applied to the
in-workspace summary before its first and only commit (`git log` shows exactly
one commit touching `v29_d9_d10_summary.json`). The invalid pre-repair file
(which would have contained bare `Infinity` tokens) no longer exists, so no
pre-repair hash can be stated; none is fabricated here.

## What is null, exactly

18 of the 144 aggregate records carry `stability_tau = null` and
`stability_amp = null` (36 null fields; no other field of any record is null
outside its ordinary schema-nullable slots such as `domain_exit_tick` on
completed runs). The 18 records are exactly the 18 `terminal_status =
"domain_exit"` runs. JSON paths: `runs[i].stability_tau` and
`runs[i].stability_amp` for
`i ∈ {37, 38, 41, 42, 53, 54, 57, 58, 61, 69, 70, 73, 74, 77, 78, 81, 121, 122}`.

## Reconciliation: 15 reported overflow repairs vs 18 null records

Both numbers are correct; they count different things. `MANIFEST.md` reported
the 15 runs whose diagnostics were **repaired** (overflowed to `inf` and were
post-processed to `null`). The remaining 3 records were **natively `None`**
from the harness — the frozen stability classifier
(`exp_v29_d9_d10.stability_class`) returns `("unclassified", None, None)`
whenever fewer than 4 valid post-burn-in samples exist, and those 3 runs hit
their domain exit *before* the burn-in of 100 ticks completed
(`valid_ticks` 82/88/98 < 100 → empty diagnostic window). Their `null`s were
serialized directly by the original run and were never touched by the repair.
15 repaired + 3 natively null = 18.

This distinction was reconstructed **deterministically from committed
artifacts only**: the diagnostics were recomputed by applying the frozen
classifier and the evaluation-only functional `V_total` to the per-tick
`x_after` states already stored in the committed trace (a pure re-evaluation
of recorded states — not a trajectory regeneration). The recomputation
reproduces `inf`/`inf` for exactly the 15 repaired runs, `None`/`None` for
exactly the 3 early-exit runs, and the committed `stability_class` for all 18.

### Category 1 — overflow repair (15 runs): `stability_tau` and `stability_amp`
overflowed to `+inf` on diverging trajectories (post-burn-in window populated,
state functional `V` at ~10¹⁵⁶–10³⁰⁵ scale); replaced with `null` by the
authorized Gate-2.4A post-processing. Reason: `overflow_on_diverging_trajectory`.

| Run ID | Domain-exit tick | Valid ticks |
|--------|-----------------|-------------|
| `D10-core/dg=0.9/eta=0.5/soft` | 184 | 183 |
| `D10-core/dg=0.9/eta=0.7/P1` | 147 | 146 |
| `D10-core/dg=0.9/eta=0.7/soft` | 263 | 262 |
| `D10-core/dg=1.0/eta=0.5/soft` | 161 | 160 |
| `D10-core/dg=1.0/eta=0.7/P1` | 123 | 122 |
| `D10-core/dg=1.0/eta=0.7/soft` | 209 | 208 |
| `D10-core/dg=1.0/eta=0.9/P1` | 251 | 250 |
| `D10-core/dg=1.1/eta=0.5/soft` | 145 | 144 |
| `D10-core/dg=1.1/eta=0.7/P1` | 108 | 107 |
| `D10-core/dg=1.1/eta=0.7/soft` | 178 | 177 |
| `D10-core/dg=1.1/eta=0.9/P1` | 179 | 178 |
| `D10-core/dg=1.1/eta=0.9/soft` | 283 | 282 |
| `D10-core/dg=1.1/eta=1.0/P1` | 283 | 282 |
| `D10-slice=rho/level=0.3/P1` | 161 | 160 |
| `D10-slice=rho/level=0.3/soft` | 233 | 232 |

### Category 2 — natively undefined, not a repair (3 runs): domain exit before
burn-in end (100 ticks) left an empty post-burn diagnostic window; the harness
itself emitted `None`. Reason: `undefined_after_domain_exit`.

| Run ID | Domain-exit tick | Valid ticks |
|--------|-----------------|-------------|
| `D10-core/dg=0.9/eta=0.5/P1` | 99 | 98 |
| `D10-core/dg=1.0/eta=0.5/P1` | 89 | 88 |
| `D10-core/dg=1.1/eta=0.5/P1` | 83 | 82 |

## Confirmations

- All fields other than the 30 repaired diagnostic values (15 runs × 2 fields)
  remain the untouched scientific output of the single Attempt-2 execution;
  the 6 null fields of Category 2 are likewise the harness's own output.
- The trace (`v29_d9_d10_trace.jsonl.gz`) was **not regenerated or edited**;
  it contains 144 rows, one per registered run, all values strictly finite.
- The canonical plan hash and every plan parameter are unchanged.
- No `stability_class`, `primary_classification`, service, stock, crossing,
  `O_physical`, or ledger value differs from what the run produced.
- Validated at Gate 2.4B: 144 unique run IDs (D9 = 4, D10 = 140), 18 domain
  exits, no sixth accepted classification, strict JSON throughout (no
  `NaN`/`Infinity` token), gzip trace readable and complete.

## Future-proofing installed at this gate

`serialization_v29.py` now makes result writes fail closed
(`allow_nan=False`); `normalize_aggregate_diagnostics()` is the only
sanctioned normalization (the two stability diagnostics above, with recorded
reasons); non-finite values anywhere else raise a hard
`NonFiniteFieldError`. Regression coverage: `test_v29_serialization.py`
(6 groups, 46 checks), which also re-validates the committed artifacts
without running any trajectory.
