# D9/D10 Attempt 1 — failed execution (audit record)

**This file documents the FIRST, FAILED execution attempt of the locked D9/D10
study. Attempt 2 (after the Gate-2.4A harness correction) is NOT the original
first execution.** No complete result, trace, or scientific classification was
produced by Attempt 1.

## Provenance

| Field | Value |
|-------|-------|
| Starting commit | `4efdeb340b94c583e89e1eaa982d56a71d3b1c17` (Phase-A harness + tests) |
| Canonical plan hash | `87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a` (unchanged) |
| Command | `python3 exp_v29_d9_d10.py > results/v2.9/d9_d10/v29_d9_d10_stdout.txt` |
| Time | 2026-07-27 (local; exact tick not recorded) |
| First (and only) run reached | `D9-A` (reserve-blind Allee arm) — the first registered run |
| Exception | `ValueError: x[0] must be finite, got -inf` raised inside `d0_v29.d0_step` |
| Preserved stdout | `ATTEMPT_1_stdout.txt` (header only; the run crashed before any summary/trace) |

## What happened

The harness executed the registered runs in order and began `D9-A`. Within that
run a cell state diverged (numerical overflow) to `-inf`; on the following tick
the frozen engine `d0_v29.d0_step` correctly rejected the non-finite state, and
the harness — which did **not** handle a domain exit — propagated the exception
and terminated. Only the stdout header had been printed. **No
`v29_d9_d10_summary.json`, no trace, and no classification of any run existed.**

## Why a harness correction was authorized (Gate 2.4A)

Gate spec §14 requires the harness to "write every run, including failures or
domain exits; never drop a run." The Attempt-1 harness violated this: it crashed
instead of recording the domain exit. An independent audit additionally found
that the harness (a) derived the D10 timestep from each policy's own `chi`
(confounding the four-policy comparison at a grid point), (b) did not apply the
registered `reserve_tol = 1e-9` to reserve-crossing detection, (c) omitted the
registered `dead_source_indicator` (D9) and `stability_class` (D10) aggregate
metrics, and (d) could return a sixth `unclassified` outcome. Gate 2.4A
authorizes correcting these harness-integrity defects and performing exactly one
authorized rerun (Attempt 2), **without changing any registered scientific
parameter or the canonical plan hash**.

## Integrity statement

- No registered dynamical parameter was changed.
- The canonical plan hash is unchanged.
- Attempt 1 produced no scientific result; nothing from it is reported as data.
- Attempt 2 is a distinct, corrected execution and is labelled as such.
