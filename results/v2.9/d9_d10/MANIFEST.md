# V2.9 Gate 2.4 — D9/D10 locked preservation study (result manifest)

**This is the Attempt-2 result set** (the single authorized rerun after the
Gate-2.4A harness-integrity correction). Attempt 1 failed and is preserved
separately (`ATTEMPT_1_FAILURE.md`, `ATTEMPT_1_stdout.txt`); it produced no
scientific result. This is a **deterministic** study; **no general dominance,
universal sustainability, or proof** is claimed from it.

## Provenance

| Field | Value |
|-------|-------|
| Canonical plan hash | `87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a` (unchanged; recomputed and enforced by the harness at run time) |
| Plan | `v29_d9_d10_plan.json` (Amendment 5) |
| Harness | `exp_v29_d9_d10.py` |
| Implementation commit (Attempt 2) | `12faa5390e6c8edb3d566e2e624a632aa4114dad` |
| Python | 3.14.2 |
| Command | `python3 exp_v29_d9_d10.py > results/v2.9/d9_d10/v29_d9_d10_stdout.txt` (run exactly once) |
| Registered runs | 144 (D9 = 4 arms, D10 = 140 = 80 core + 60 secondary) |

## Artifacts

| File | Content |
|------|---------|
| `v29_d9_d10_summary.json` | one aggregate record per run (144), plan hash, tolerances, provenance |
| `v29_d9_d10_trace.jsonl.gz` | full per-tick trace (gzip, stdlib; 13.8 MB uncompressed JSONL, no data discarded — trace exceeds the 10 MiB threshold so the registered compression rule applies) |
| `v29_d9_d10_stdout.txt` | study report captured directly from the run command |
| `ATTEMPT_1_FAILURE.md`, `ATTEMPT_1_stdout.txt` | preserved failed first attempt (audit trail) |

## Post-processing (authorized, no regeneration)

After the single run, on the 15 diverging D10 runs whose state functional `V`
reaches ~10²⁵⁰, the two **diagnostic** floats `stability_tau` and
`stability_amp` overflowed to `inf` and would serialize as JSON `Infinity`
(violating the plan's JSON-safety requirement). Under explicit authorization
(post-process only, no regeneration) those two fields were replaced with `null`
in `v29_d9_d10_summary.json`. **Nothing else was changed**: no trajectory, no
`stability_class` (still correct), no `primary_classification`, no other metric,
and the study was **not** re-run. A `post_processing` note is embedded in the
summary. The trace was already JSON-safe (per-tick records are all finite;
non-finite successors are recorded as `terminal_status = domain_exit` in the
aggregate, never serialized as numeric rows).

## Note on `max_ledger_residual`

The maximum **absolute** per-tick ledger residual is 128, on a run that reached
`-5.9e250` before its domain exit; **relative to that state scale this is ~2e-249**
(machine precision). The maximum **scale-aware** ledger residual across all 144
runs is **1.1e-15**. The physical stock/loss ledger closes to machine precision;
the large absolute values only reflect the enormous pre-overflow state
magnitudes on diverging unconstrained runs.

## Headline results (deterministic; limited to these fixtures)

- **D9 (Allee reserve-stress) discriminated cleanly** (unlike the
  non-discriminating Gate-2 D5): reserve-blind (D9-A) and soft (D9-B) both
  **collapse**, crossing the reserve at tick 8; the soft penalty delayed the
  Allee crossing (tick 24 vs 17) and reduced over-use but did **not** prevent
  the reserve crossing. Both hard-cap arms (D9-C soft+cap, D9-D blind+cap)
  **preserve** the source at exactly `R_eff = 11` with zero reserve/Allee
  crossings, rationing service, and **zero one-step-preservation-theorem
  violations** over 200 eligible ticks. D9-C ≡ D9-D: the hard cap, not `chi`,
  does the preserving.
- **D10 phase map**: P0 all safe_rationing; **P1 and soft identical** (25
  collapse, 10 safe_service; 25/35 with physical over-use `O_physical > 0`);
  **P1C never collapses and never over-uses** (25 safe_service, 10 safe_rationing).
  Collapse tracks `d/g_max ≳ 0.9` and low `eta`, as the analytic
  feasibility/deliverable boundaries predicted.

`O_physical` is a **physical over-use diagnostic, not issued EBU or ecological
debt**; no debt ledger, wallet, or scalarisation exists in this study.
