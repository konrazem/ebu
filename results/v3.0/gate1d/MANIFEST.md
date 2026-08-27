# V3.0 Gate 1D — Bounded Capability-Matched Service-Alignment Study (record)

**This is a gate study record, NOT a release manifest.** It records the single
authorized execution of the locked 56-run Gate-1D study. Passing checks are
numerical validation at declared points, never proof. The bounded service
wrapper is **outside the V2.8 D0 theorem** (open problem O13).

> ### Headline
> **After equalizing action capability, exact-quote maximization did not reduce
> service at all: arm D was identical to arm B on every physical metric in all
> 7 worlds at both certified timesteps** (service deficit 0.000, D/B service
> ratio exactly 1.0000, 0 service-alignment failures in 14 paired
> comparisons). Bounded service removed **every** domain exit (0 of 56, versus
> 36 of 36 in Gate 1C).
>
> **But the study cannot quantify the Gate-1C capability effect**: no
> registered world contains a source with more than one out-edge, so the
> one-action-per-source restriction was structurally non-binding and the A-vs-B
> capacity cost is exactly 0.000 everywhere (see Limitations).
>
> **A post-execution implementation defect was found and NOT repaired**: the
> reserve-crossing counter lacks a tolerance, so a one-ULP breach
> (8.88e-16) mislabels 4 runs. Per the gate's discipline the study was not
> corrected and not rerun; authorization is requested.

## Provenance

| Field | Value |
|-------|-------|
| V2.9 baseline tag | `v2.9.0` (peeled `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0`) |
| Gate-1D preregistration commit | `239074eb9fdfb2a57b1f07352cb250d388d7bff7` |
| **Phase-A implementation commit** | **`a556b4f43ea002c27b77910c76e395e9d77d7144`** |
| **Phase-A tests/runner commit (pushed before any run)** | **`5886cb10a674d3861deb47a848ce9d26bbb2a4a6`** |
| Plan canonical hash | `71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020` |
| Plan raw SHA-256 | `7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c` |
| Gate-1 quote plan (still locked) | `a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061` |
| Equation version | `v3.0-gate0.1` |
| Python | 3.14.2 |
| Attempts | **exactly one**; exit code 0; complete study; nothing rerun or tuned |

## Exact command

```
python3 exp_v30_service.py > results/v3.0/gate1d/v30_service_alignment_stdout.txt
```

No command-line option or scientific override is accepted; the canonical plan
hash is enforced; every paired run is gated on `r_dt ≤ 1` before execution;
completed results are never overwritten.

## Artifacts

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_service_alignment_summary.json` | `bd8de06658f68ff0d1b2aa337022daf4768d0ae620fb6a3cc79e88eeab41a867` | 132 358 |
| `v30_service_alignment_trace.jsonl.gz` | `3cb97610774ee94f9dab6c777c8b6d7a3496eeeaf254d580cdf30e3babbce3ab` | 64 119 |
| `v30_service_alignment_stdout.txt` | `dacf9891ccb912641f60889f8bf9066fe7623f6aeb2cb9611d93afb3b80e4fb8` | 16 710 |

**56 run records, 56 unique identifiers, none missing, none extra, none
dropped.** Trace: 56 gzip lines (full 200-tick series per run), 925 056 bytes
uncompressed, `gzip -t` clean. Strict JSON throughout (`allow_nan=False`); every
numeric field finite.

## Bounded service and physical integrity

The registered 10-step order is implemented, with demand moved from the drive
term to the saturating service step (steps 2 and 7). Results across all 56 runs:

- **no negative state** anywhere; **0 domain failures** (Gate 1C: 36 of 36);
- `service ≤ available` and `service ≤ demand` at every tick (no phantom stock);
- `unmet = demand − service` exactly; unmet demand reported, never hidden;
- non-negativity corrections recorded explicitly, total 0.0 (none needed);
- **max |ledger residual| = 8.77e-15** for
  `Σx' − Σx = dt·Σu − loss − Σservice + Σcorrections`;
- **physical overuse exactly 0.0** in every run (P1C cap never exceeded);
- Allee crossings 0; dead sources 0.

## Certified timesteps

Both registered timesteps used unchanged: conservative `dt =
0.1845018450184502`, near-certificate `dt = 0.3321033210332103`. Per-world
certificates recomputed to the registered values; `r_dt` ranged **0.334–0.500**
(conservative) and **0.601–0.900** (near-certificate) — `r_dt ≤ 1` in **all 56
runs**. Every paired arm in a world shared one timestep.

## Required analysis

### A versus B — action-capacity cost

**Exactly 0.000 (0.00 %) in all 7 worlds at both timesteps**, with identical
action counts (e.g. W1 199/199, W3 371/371, W6 398/398). The restriction cost
nothing **because it never bound**: see Limitations.

### B versus C — observational identity

**Byte-identical in all 14 paired comparisons** (max |Δx| = 0.000e+00), while
arm C accumulated large positive EBU (+121 to +1551). Falsifier **F1 not
triggered**.

### B versus D — PRIMARY service-alignment comparison

| World | dt | service B | service D | deficit | persistent | D EBU | rests | failure |
|-------|----|-----------|-----------|---------|-----------|-------|-------|---------|
| W1 | cons / near | 27.675 / 49.815 | 27.675 / 49.815 | +0.000 | False | +121.4 / +211.7 | 1 / 1 | **False** |
| W2 | cons / near | 71.967 / 129.122 | 71.967 / 129.122 | +0.000 | False | +892.0 / +1550.9 | 2 / 1 | **False** |
| W3 | cons / near | 27.675 / 49.815 | 27.675 / 49.815 | +0.000 | False | +175.6 / +323.5 | 29 / 17 | **False** |
| W4 | cons / near | 69.188 / 124.539 | 69.188 / 124.539 | +0.000 | False | +498.5 / +924.8 | 1 / 1 | **False** |
| W5 | cons / near | 74.723 / 134.502 | 74.723 / 134.502 | +0.000 | False | +441.4 / +771.8 | 1 / 1 | **False** |
| W6 | cons / near | 55.351 / 99.631 | 55.351 / 99.631 | +0.000 | False | +266.7 / +507.2 | 2 / 2 | **False** |
| W7 | cons / near | 55.627 / 100.129 | 55.627 / 100.129 | +0.000 | False | +244.8 / +476.2 | 1 / 1 | **False** |

**0 service-alignment failures in 14 comparisons.** Arm D selected the same
physical action as arm B in every tick of every world: the exact quote and the
loss-aware force ranked the single available candidate identically, and both
took the full accepted quantity. Arm D's EBU equals arm C's exactly, confirming
that D's chosen actions are B's executed actions.

## Outcome classes (56 runs)

| Class | Count |
|-------|-------|
| `preserve_and_serve` | **48** |
| `physical_impossibility` | 4 (W2 near-certificate — the registered infeasible world) |
| `destructive_service` | 4 (W2 conservative — **see the defect below**) |

No `numerical_or_domain_failure`, no `systemic_collapse`, no
`distributive_or_policy_under_service`, no `safe_rationing`, no `unclassified`.

## Timestep sensitivity

The **alignment verdict is consistent** across both timesteps in all 7 worlds
(failure = False at both; D/B service ratio 1.0000 at both). The **outcome
class of W2 differs** between timesteps (`destructive_service` at conservative,
`physical_impossibility` at near-certificate) — and that difference is entirely
produced by the one-ULP counter defect below, not by physics.

## Implementation defect found after execution — NOT repaired, NOT rerun

The reserve-crossing counter in `service_v30.run_arm` tests
`x_after < R_eff <= x_before` with **no tolerance**, whereas P1C's own
`reserve_boundary_ok` uses `num_tol·(1+|R_eff|)`. In the four W2 conservative
runs the source's minimum stock is `7.999999999999999` against `R_eff = 8.0` —
a breach of **8.881784197001252e-16**, one unit in the last place. All four runs
are therefore counted as having 1 reserve crossing and classified
`destructive_service`, when the correct physical reading is that P1C held the
boundary to floating-point precision and the runs are
`physical_impossibility` (as their near-certificate twins are).

Scope: this affects only the diagnostic crossing counter and the resulting
class label for those 4 runs. It does **not** touch the physics, the P1C
allocation, the quote equation, the bounded service update, the ledger, or the
primary B-vs-D comparison (0 alignment failures either way; arm A and arm B are
affected identically, so no comparison is biased). Per the gate's execution
discipline the study was **not corrected and not rerun**; authorization is
requested before any repair or re-execution.

## Limitations that bound the conclusion

1. **The capability effect (C1) is not quantified.** No registered world
   contains a source with more than one out-edge (out-edge counts per source:
   W1 {0:1}, W2 {0:1}, W3 {0:1, 1:1}, W4 {0:1}, W5 {0:1}, W6 {0:1, 1:1},
   W7 {0:1}). The one-action-per-source restriction was therefore structurally
   non-binding, the shared menu reduced to one edge × two quantity fractions,
   and A ≡ B exactly. The Gate-1C mismatch — 5×5 grid sources with up to four
   out-edges and a 0.425× action ratio — **cannot be reproduced in these
   worlds**. The Gate-1C gap is attributed to C1/C2 by *elimination* (no gap
   appears once capability is matched and coverage is complete), **not** by
   direct measurement.
2. **Quote coverage is complete here (1.0 for arms C and D)**, unlike Gate 1C's
   3.25 %. That removes C2 as a confounder in this study but equally means C2's
   Gate-1C magnitude is not measured here.
3. **Idealized study**: `τ = 0`, `ε_x = ε_u = 0`, exact deterministic local
   observations, no sensor noise. **No real-world latency or robustness claim
   is made.** Gate 1E remains a future design/proof stage.
4. Seven small deterministic worlds, no stochastic layouts, 200 ticks. The
   bounded wrapper's guarantees rest on numerical validation only (O13).

## Attribution of the Gate-1C surprise (C1–C7)

- **C4 unbounded consumer dynamics — CONFIRMED as an artifact.** Bounded
  service removed all 36 Gate-1C domain exits: 0 of 56 runs left the physical
  domain, with unmet demand recorded explicitly instead.
- **C5 uncertified timestep — REMOVED as a confounder.** All 56 runs ran at
  `r_dt ≤ 1`; the alignment verdict is timestep-consistent.
- **C6 predicate blindness — CONFIRMED and corrected.** The serving-baseline
  predicate was implemented and is demonstrably able to fire (negative controls
  in the pre-execution suite); it reported no failure here.
- **C1 capability mismatch and C2 quote coverage — CONSISTENT with being the
  Gate-1C cause, but not quantified** (Limitation 1).
- **C3 genuine objective misalignment — NOT supported in these worlds.** With
  matched capability and full coverage, exact-quote maximization made exactly
  the baseline's physical choices.
- **C7 interaction — cannot be excluded**, since C1/C2 were not varied.

## Hypotheses

Supported here: **H1** (B≡C byte-identical), **H2** (the gap disappears under
identical capability — though capability was non-binding), **H4** (bounded
service removed domain exits without hiding unmet demand), **H5** (certified
timestep; verdict timestep-consistent), **H6** (P1C prevented all Allee
crossings and source deaths; the only reserve "crossings" are the ULP artifact),
**H8** (the serving-baseline predicate is implemented and non-vacuous).
**H3** not triggered (no residual gap). **H9** untestable here (capacity
restriction non-binding). **H7** and **H10** stand as stated; **H10** explicitly
not tested (τ = 0).

## Falsifiers

**None triggered.** F1 (no trajectory change), F2 (no negative stock), F3 (no
hidden unmet demand), F4 (menus/capacity equal by construction and asserted),
F5 (no `r_dt > 1`), F6 (no genuine reserve crossing beyond one ULP), F7 (no
positive-EBU under-service), F8/F13 (survival and domain status reported
separately; no domain exit occurred), F9 (no threshold changed after results —
the predicate operationalization was declared before implementation), F10 (56
of 56 runs recorded), F11 (AST-verified boundary; no actor-economy identifiers),
F12 (feasible and infeasible worlds classified distinctly), F14 (tolerance kept
at the 1e-9 scale; the ULP defect is reported, not absorbed), F15 (no
robustness claim).

## Test and regression totals (kept separate)

- Gate-1D pre-execution suite `test_v30_service.py`: **275 passed, 0 failed, 13
  groups** (run before the study; AST-proven to drive no 200-tick trajectory).
- Gate 1B: quote 184/184, audit 19/19. Gate 1C: adversary 150/150, reproduction
  audit 47/47.
- Released suites, unchanged, no V2.9 study regenerated: test_energy_balance 8;
  test_v22 7; test_v23 4; test_v24 5; test_v25 9; test_v26 15 (+33 prior);
  test_math 34; test_v28 132; test_v29 141; test_v29_behavior 108;
  test_v29_p1c 83; test_v29_d9_d10 114; test_v29_serialization 46.

## Actor economy

**Gate 2 remains paused.** No outcome of this gate authorizes progression: even
with no misalignment detected here, actor implementation requires separate
authorization, the capability effect is unquantified (Limitation 1), and the
Gate-1E uncertainty programme (latency, stale observations, measurement and
regeneration uncertainty, quote expiry, robust margins, interval quotes) is
entirely open.

## Open problems

Unchanged and open: **O1**–**O9**, **O10** (predicate now implemented but
validated only in worlds where it did not fire), **O11** (the object of this
study — no misalignment found under matched capability, but see Limitation 1),
**O12** (addressed: bounded service implemented; theorem still missing),
**O13** (constrained/saturated descent theorem for the bounded wrapper).

New from this gate:

- **O14 — multi-out-edge capability worlds.** A world family in which sources
  genuinely have several out-edges is required to measure C1/C2 directly and to
  test the aggregate-quote extension (O3).
- **O15 — tolerance discipline for diagnostic boundary counters.** Crossing and
  boundary counters must use the same scale-aware tolerance as P1C's own
  `reserve_boundary_ok`; the ULP defect above is the witness.
