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
| Actual first crashing run (forensically determined) | **`D10-core/dg=0.9/eta=0.5/P1`** at tick 55 (source cell 0 → `-inf`) — the 38th run in registered order |
| Exception | `ValueError: x[0] must be finite, got -inf` raised inside `d0_v29.d0_step` |
| Preserved stdout | `ATTEMPT_1_stdout.txt` (header only; per-run output is printed only after all runs, so the header was all that reached stdout) |

## Correction to an earlier assumption (important for accuracy)

An earlier report and the first version of this file stated the crash was on
`D9-A`. **That was an incorrect assumption** drawn from the bare traceback, which
only showed a `P1`/`soft`-policy `d0_v29.d0_step` call and gave no run id.
Forensic reconstruction (running the corrected harness with Attempt-1's exact
per-policy timestep, writing nothing to `results/`) shows:

- **`D9-A` is bounded**, not divergent: its source declines monotonically through
  the reserve and settles at a finite `-4.175`; it never reaches `-inf`.
- The **first** run to reach a non-finite state under Attempt-1's timestep was
  **`D10-core/dg=0.9/eta=0.5/P1`** at **tick 55** (dt = 0.3616). D9-A/B/C/D and
  the earlier D10 grid points (`d/g_max` = 0.25, 0.5) all completed (bounded)
  before that run crashed.

## What happened

The harness executed the registered runs in order (D9 first, then D10). All four
D9 arms and the low-demand D10 grid points completed with bounded states. At
`D10-core/dg=0.9/eta=0.5/P1`, the **shared-timestep defect** (Gate 2.4A §4) gave
the `P1` arm a timestep of **0.3616** — derived from that policy's own `chi = 0`
certificate rather than the most restrictive certificate shared across the four
paired policies. Under that too-large timestep the driven explicit-Euler update
diverged, the source overflowed to `-inf` at tick 55, and on the next tick the
frozen engine `d0_v29.d0_step` correctly rejected the non-finite state. The
harness — which did **not** handle a domain exit (Gate 2.4A §3) — propagated the
exception and terminated. Because per-run output is printed only after all runs,
only the stdout header had been written. **No `v29_d9_d10_summary.json`, no
trace, and no classification of any run existed.**

Both defects (the too-large per-policy timestep, §4; and the unhandled domain
exit, §3) are corrected in Attempt 2: paired policies now share the most
restrictive timestep, and a non-finite successor is recorded as a `domain_exit`
(retaining the last finite state) with the run continuing to completion.

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
