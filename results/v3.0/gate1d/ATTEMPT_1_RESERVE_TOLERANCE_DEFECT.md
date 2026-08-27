# Gate 1D Attempt 1 — Reserve-Tolerance Diagnostic Defect (preservation note)

**Attempt 1 is the immutable historical execution record of Gate 1D.** This
note documents a diagnostic implementation defect found after Attempt 1
completed, records the exact affected values, and states why a single
tolerance-corrected regeneration (Attempt 2, under `attempt2/`) is authorized.
Nothing in this note rewrites, reinterprets, or supersedes any claim in the
original Attempt-1 `MANIFEST.md`, which already reports this defect in its
section "Implementation defect found after execution — NOT repaired, NOT
rerun".

## Attempt-1 provenance (unchanged)

| Field | Value |
|-------|-------|
| Attempt-1 results commit | `db08d2d5278179b2a4f6e2cdb3a938251eb5c96e` |
| Phase-A implementation commit | `a556b4f43ea002c27b77910c76e395e9d77d7144` |
| Phase-A tests/runner commit | `5886cb10a674d3861deb47a848ce9d26bbb2a4a6` |
| Preregistration commit | `239074eb9fdfb2a57b1f07352cb250d388d7bff7` |
| Exact original command | `python3 exp_v30_service.py > results/v3.0/gate1d/v30_service_alignment_stdout.txt` |
| Plan canonical hash | `71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020` |
| Plan raw SHA-256 | `7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c` |

## Attempt-1 artifacts (must remain byte-identical at these paths)

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_service_alignment_summary.json` | `bd8de06658f68ff0d1b2aa337022daf4768d0ae620fb6a3cc79e88eeab41a867` | 132 358 |
| `v30_service_alignment_trace.jsonl.gz` | `3cb97610774ee94f9dab6c777c8b6d7a3496eeeaf254d580cdf30e3babbce3ab` | 64 119 |
| `v30_service_alignment_stdout.txt` | `dacf9891ccb912641f60889f8bf9066fe7623f6aeb2cb9611d93afb3b80e4fb8` | 16 710 |
| `MANIFEST.md` | `17868276c9deb839a135ee585b03d2e401a15e628f47040fede4413e8e744232` | 13 798 |

## The defect

The reserve-crossing counter in `service_v30.run_arm` used the exact strict
comparison

```
xa[i] < configs[i].R_eff <= xb[i]
```

with **no numerical tolerance**, although the gate's registered tolerance rule
(`service_v30.tol`, `1e-9 * (1 + |value|)`) exists precisely for such
boundary diagnostics, and although P1C's own `reserve_boundary_ok` applies a
scale-aware tolerance (`num_tol * (1 + |R_eff|)`).

## Exactly affected Attempt-1 runs (4 of 56)

| Run identifier | reserve_crossings | outcome_class (Attempt 1) |
|----------------|-------------------|---------------------------|
| `W2_infeasible_2cell\|A_full_p1c\|conservative` | 1 | `destructive_service` |
| `W2_infeasible_2cell\|B_restricted_p1c\|conservative` | 1 | `destructive_service` |
| `W2_infeasible_2cell\|C_restricted_p1c_quote\|conservative` | 1 | `destructive_service` |
| `W2_infeasible_2cell\|D_restricted_quote_greedy\|conservative` | 1 | `destructive_service` |

Observed values, identical in all four runs:

- `R_eff = 8.0` (W2's single regenerative source, cell 0);
- minimum source stock `x = 7.999999999999999`
  (= `math.nextafter(8.0, -inf)`, exactly one ULP below `R_eff`);
- residual `R_eff − x = 8.881784197001252e-16` — one unit in the last place,
  not a material ecological reserve breach;
- registered tolerance at this scale:
  `tol_R = 1e-9 * (1 + |8.0|) = 9.000000000000001e-09`, roughly 1e7 times the
  observed residual.

Under the registered tolerance the correct reading is that P1C held the
reserve boundary to floating-point precision: 0 crossings, and the four runs
classify as `physical_impossibility` (W2 is the registered infeasible world),
exactly as their near-certificate twins already do.

## Affected fields (diagnostic only)

- `totals["reserve_crossings"]` (1 → 0 expected in the four runs above);
- `reserve_harm_predicate` fields derived from that count
  (`is_reserve_destruction`);
- `outcome_class` for the four runs
  (`destructive_service` → `physical_impossibility` expected);
- outcome-class aggregate counts;
- the alignment predicate's informational `baseline_crossed_reserve` /
  `actor_crossed_reserve` flags (identical for arms B and D, so no
  comparison was ever biased).

## NOT affected (verified in Attempt 1, required unchanged in Attempt 2)

Physical trajectories; P1C decisions and budgets; requested and accepted
actions; delivered quantities and losses; service and unmet demand; EBU
quotes and settlements; burden; viability; ledgers and residuals; timestep
certificates and `r_dt`; domain status; the B-versus-C observational
identity; and the primary B-versus-D service-alignment result (0 failures in
14 comparisons — arms A and B were affected identically by the defect, so
nothing was biased).

## Why one corrected regeneration is authorized

Attempt 1's execution discipline forbade repairing or re-running after
results were seen; the manifest therefore reported the defect and requested
authorization. That authorization has now been granted for Gate 1D-A,
narrowly: apply the **already-registered** tolerance
(`tol_R = 1e-9 * (1 + |R_eff|)`) to the reserve diagnostic, change nothing
else, and perform **exactly one** controlled regeneration (Attempt 2) into
the isolated directory `attempt2/`. No scientific parameter, world, policy,
timestep, threshold, equation, plan file, or classification precedence is
changed; the correction makes the diagnostic conform to the tolerance rule
the protocol had already registered (open problem O15 is the witness).

Attempt 1 remains the historical record. Attempt 2, if validated, becomes
the corrected authoritative diagnostic rendering of the same registered
study.
