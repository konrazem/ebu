# Gate 1D-A — Attempt 1 versus Attempt 2 comparison record

## Authorization and reason

Attempt 1's manifest reported a post-execution diagnostic defect — the
reserve-crossing counter in `service_v30.run_arm` used the exact strict
comparison `xa < R_eff <= xb` with no tolerance, mislabelling a one-ULP
residual (`min stock 7.999999999999999` vs `R_eff = 8.0`, difference
`8.881784197001252e-16`) as a reserve crossing in four W2 conservative runs —
and, per the gate's discipline, was **not** corrected or rerun; authorization
was requested. Gate 1D-A granted a narrow authorization: apply the
**already-registered** tolerance (`service_v30.tol`, `1e-9 * (1 + |value|)`)
to the reserve diagnostic only, preserve Attempt 1 unchanged, and perform
**exactly one** controlled regeneration (Attempt 2). Attempt 2 is a
**defect-correction regeneration, not an independent replication**, and this
validation is **not proof**.

## Provenance

| Field | Value |
|-------|-------|
| Correction commit (pushed before the Attempt-2 run) | `86853b0b6adff0fe024fcd696694973f56bb63fb` |
| Exact official command | `python3 exp_v30_service_attempt2.py > results/v3.0/gate1d/attempt2/v30_service_alignment_stdout.txt` |
| Executions | exactly one; exit code 0; complete; nothing inspected mid-run, tuned, or rerun; no Attempt 3 |
| Plan canonical hash (recomputed, enforced, unchanged) | `71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020` |
| Plan raw SHA-256 (unchanged) | `7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c` |

Attempt-1 artifact hashes (verified byte-identical before and after the
Attempt-2 run): summary `bd8de066…41a867` (132 358 B), trace
`3cb97610…bce3ab` (64 119 B), stdout `dacf9891…e4fb8` (16 710 B), manifest
`17868276…744232` (13 798 B) — full digests in `MANIFEST.md` here and in
`../ATTEMPT_1_RESERVE_TOLERANCE_DEFECT.md`.

Attempt-2 artifact hashes: summary `f2b065b5…a96bc4` (132 346 B), trace
`b509606e…fd095b` (64 119 B), stdout `4198d587…22a319` (16 683 B).

## Comparison method (exact)

1. Both summaries loaded with strict JSON (`parse_constant` raising on any
   NaN/Infinity — none present).
2. Run-count and identifier validation: exactly 56 runs in each attempt,
   56 unique `run_id`s, identical sets, no duplicates, none dropped.
3. Top-level provenance fields (`plan_id`, both plan hashes,
   `equation_version`, `gate`, `n_runs`, `registered_dts`,
   `derived_semantics`, `non_claims`) required identical.
4. Per-run, field-by-field comparison keyed by exact `run_id`, with an
   explicit allow-list; **any** difference outside the allow-list fails the
   validation. Equality is exact bit-for-bit JSON value equality — the
   declared serialization tolerance was never needed.
5. Nested predicate dicts (`reserve_harm_predicate`,
   `service_alignment_predicate`) compared subfield-by-subfield with their
   own allow-lists; `is_service_alignment_failure` required identical in all
   14 B-vs-D comparisons.
6. Traces decompressed (`gzip -t` clean) and required **byte-identical
   uncompressed content** (56 lines, matching run order, strict JSON).
7. Expected narrow consequences asserted directly (below), including that no
   run outside the four W2 conservative runs had or gained a crossing.

Allow-list (the only fields permitted to differ): per-run
`reserve_crossings`; `reserve_harm_predicate.reserve_crossings` and
`.is_reserve_destruction`; `service_alignment_predicate
.baseline_crossed_reserve`, `.actor_crossed_reserve`,
`.preservation_justified`; `outcome_class`; top-level
`outcome_class_counts`. (No first-crossing-tick or time-below-reserve field
exists in this study's records.)

Result: **PASS — 0 violations.**

## Confirmed unchanged (exactly identical in all 56 runs)

All state trajectories (uncompressed trace byte-identical; `final_state`
equal); all requested and accepted actions and delivered quantities
(`action_opportunities`, `proposed_actions`, `accepted_actions`,
`quoted_actions`, `quote_coverage`, `voluntary_rests`, `p1c_rejections`);
all losses (`transport_loss`); all service and unmet demand (totals,
post-burn-in sums and means, `service_ratio`); all EBU quotes and
settlements (`ebu_total`, `ebu_positive`, `ebu_negative`); all burden and
viability values; all P1C state classifications and `physical_overuse`
(0.0 everywhere); all ledger values and residuals
(`max_ledger_residual`, `negative_corrections_total`); all timestep
certificates and `r_dt`; all domain-status values (`negative_state`,
`domain_failure_tick`, `terminal_status` — 0 domain exits in both attempts);
all Allee crossings (0) and dead sources (0); the B-vs-C observational
identity (all 14 comparisons identical in both attempts); and **the primary
B-vs-D service-alignment result: 0 failures in 14 comparisons, identical
verdict fields, deficit +0.000 and D/B ratio 1.0000 everywhere, in both
attempts**. `capacity_cost_relative_mean` and the failure/domain/negative
lists (all empty) are unchanged.

## Complete inventory of differences (18 fields, all diagnostic)

The four corrected runs, before → after:

| Run | reserve_crossings | outcome_class |
|-----|-------------------|---------------|
| `W2_infeasible_2cell\|A_full_p1c\|conservative` | 1 → 0 | `destructive_service` → `physical_impossibility` |
| `W2_infeasible_2cell\|B_restricted_p1c\|conservative` | 1 → 0 | `destructive_service` → `physical_impossibility` |
| `W2_infeasible_2cell\|C_restricted_p1c_quote\|conservative` | 1 → 0 | `destructive_service` → `physical_impossibility` |
| `W2_infeasible_2cell\|D_restricted_quote_greedy\|conservative` | 1 → 0 | `destructive_service` → `physical_impossibility` |

Per run that is 4 × (`reserve_crossings`,
`reserve_harm_predicate.reserve_crossings`,
`reserve_harm_predicate.is_reserve_destruction` True → False,
`outcome_class`) = 16 fields, plus 2 informational flags in the
W2-conservative D-arm alignment record
(`service_alignment_predicate.baseline_crossed_reserve` and
`.actor_crossed_reserve`, True → False; arms B and D corrected identically,
so no comparison is biased). `preservation_justified` was False in both
attempts (permitted to differ; did not). Top-level `outcome_class_counts`:
`{destructive_service: 4, physical_impossibility: 4, preserve_and_serve: 48}`
→ `{physical_impossibility: 8, preserve_and_serve: 48}`. The stdout files
differ only in the four W2 rows' `Rx`/class columns, the class-count block,
the crossings-total line, and the output paths.

## Expected narrow consequences — all occurred, none forced

- the four one-ULP W2 crossings disappear (1 → 0): **yes**;
- the four labels change `destructive_service` → `physical_impossibility`,
  matching their near-certificate twins: **yes** — W2's outcome class is now
  timestep-consistent;
- no genuine material crossing disappears: **yes** — all 52 other Attempt-1
  counts were already 0, so **0 reserve crossings remain in Attempt 2** and
  nothing was hidden (the regression suite separately proves a genuine
  breach still counts and still classifies `destructive_service`);
- the primary B-vs-D result is exactly unchanged: **yes** — 0
  service-alignment failures in all 14 comparisons;
- no domain exits remain: **yes** — 0 of 56 in both attempts;
- no physical trajectory changes: **yes** — uncompressed traces
  byte-identical, every scientific field bit-identical.

No other change of any kind was observed; no stop condition fired; no other
implementation defect appeared.

## Test totals

Gate-1D suite `test_v30_service.py` 304/0 in 14 groups (29 new Gate 1D-A
checks in G14; no existing test, falsifier, tolerance, or assertion
weakened). Gate 1B quote 184/0 and audit 19/0; Gate 1C adversary 150/0 and
reproduction audit 47/0. Released suites unchanged and passing:
test_energy_balance 8; test_v22 7; test_v23 4; test_v24 5; test_v25 9;
test_v26 15 (+33 prior); test_math 34; test_v28 132; test_v29 141;
test_v29_behavior 108; test_v29_p1c 83; test_v29_d9_d10 114;
test_v29_serialization 46.

## Status of the two attempts

**Attempt 2 is the corrected authoritative Gate 1D diagnostic rendering.
Attempt 1 remains the immutable historical execution record**, byte-identical
at its original paths, with its manifest's claims unmodified. Validation is
numerical checking at declared points, never proof; no scientific parameter
changed; no new scientific claim is made beyond Attempt 1's, and Attempt 1's
limitations (including the unquantified C1/C2 capability effect, O14) apply
to Attempt 2 in full.
