# V3.0 Gate 1C — Adversarial Replay Record (preregistered Q22)

**This is a gate falsification-search record, NOT a release manifest and NOT a
security assessment.** It records the single authorized execution of the
preregistered Q22 adversarial replay against the V3.0 local signed EBU quote.

> **Headline.** **No profitable persistent-harm exploit was found** — 0 in 36
> production-arm runs and 0 in 12 red-team-oracle searches — **within the
> declared fixtures, seeds, action menu, search depth, width, and predicate.**
> This is **not** a proof of security, not "exploit-free", not "proven safe",
> and not a guarantee. Three limitations below (all 36 runs left the physical
> domain; an uncertified timestep; a baseline-relative predicate that cannot
> see service degradation) materially bound what the negative result means.

## Provenance

| Field | Value |
|-------|-------|
| V2.9 baseline tag | `v2.9.0` (peeled `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0`) |
| Gate 1A review / preregistration | `02fd026` / `a9c5909` |
| Gate 1A.1 corrections | `d45f059` |
| Gate 1B implementation / validation / results | `3c436a3` / `16169f8` / `aabc2cd` |
| **Gate 1C Phase-A harness commit (pushed before any Q22 run)** | **`38fe6bf16959a5282e24ca1c91e309174db6905b`** |
| Plan canonical hash | `a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061` |
| Plan raw SHA-256 | `5f01a1fd554bfb2f5e684dc318a805f2887d51274e456c98d1a1d5788d1a6f4f` |
| Equation version | `v3.0-gate0.1` |
| Python | 3.14.2 |
| Attempts | **exactly one**; exit code 0; complete study; nothing rerun |

## Exact command

```
venv/bin/python exp_v30_adversary.py > results/v3.0/gate1c/v30_adversarial_stdout.txt
```

The runner recomputes and enforces the canonical plan hash, takes no
command-line option, and refuses to overwrite a completed study. The project
venv is used because the released `exp_v26.random_allee_world` layout
generator imports matplotlib (the same convention as `test_v25.py` /
`test_v26.py`).

## Artifacts

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_adversarial_summary.json` | `7114ea702132a0b95ca00e5cda6afc2ccd9d70207bc0dc450b2e5b4fefe42263` | 80 505 |
| `v30_adversarial_trace.jsonl.gz` | `e4c09e8aa54e0ddc87bf37be77138f7cf87abaed277349eaddd4e5755897b0fd` | 40 001 |
| `v30_adversarial_stdout.txt` | `14592386d905f7b1b50ff478f76dc83df3ebec18760befc5578968a9e74e779a` | 9 476 |

Trace: 48 gzip lines (36 arm histories + 12 oracle beams), 181 826 bytes
uncompressed, `gzip -t` clean. Strict JSON everywhere (`allow_nan=False`); no
NaN or Infinity in any record. Every registered run appears exactly once; no
run was dropped.

## Frozen search method and constants

Provenance of every constant is recorded in `adversary_v30.GATE1C_SEMANTICS`
and reproduced in the summary: **plan-named** — `DEPTH=10`, `WIDTH=40`,
`TAIL=20`, `QUANTS=(0.5, 1.0)`, `COALITION=[0,1]`, layout seeds `0..11`;
**released V2.6 machinery** — `H_RUN = DEPTH*3 = 30`, `MARGIN=1.0`,
`DELTA=3.0` (so `R_eff = A + DELTA = 11`), `CHI=1.0`, `LAM_L=0.1`, `A=8`,
5×5 grid, `src_frac=0.4`, actor `q_max=3.0`, `M=0.6`, `θ=0.05`, `η=0.95`;
**tick fidelity** — `dt = 1.0` (V2.6 advances in unit ticks; dt was not a free
parameter and was never chosen to suit an outcome).

Layout translation is a mechanical parameter-for-parameter map of
`exp_v26.random_allee_world` onto `d0_v29`/`p1c_v29` objects; Allee sources
become `regenerative` with `R_eff = 11`, non-regenerating cells become
`finite` (P1C therefore gives them a **zero** preservation-safe export
budget — a determined consequence of P1C typing, not a design choice). All 12
layout signatures are distinct and match the released generator's masks.

## Arms, coverage, and information boundaries

12 layouts × 3 arms = **36 runs**, plus 12 oracle searches and 3 historical
controls.

- **A — P1C physical baseline**: P1C only, no EBU-guided selection, no quoting.
- **B — P1C + observational exact quote**: identical accepted physical actions,
  quoted and settled observationally.
- **C — exact-quote-maximizing adversary** (production-local): each configured
  source compares committed exact quotes over **its own** permitted menu
  (own out-edges × registered quantity fractions, capped by its own P1C
  budget), proposes **one** action per source per micro-step, and the **real
  P1C** executes the selection. Verified by AST that this path reads no
  `V_total`, no global metric, no baseline, no wallet/health/price.
- **Red-team ORACLE** (separately labelled, reported separately): a beam search
  that uses **global harm as an external testing objective**. This information
  is **not** available to any production actor and oracle results are never
  presented as production behaviour.

## Results — EBU and physical state side by side

Per-arm means over the 12 layouts (full per-run records in the summary):

| Arm | cum. EBU | positive | negative | actions | final burden | final viab. % | served | reserve x | Allee x | dead src | overuse |
|-----|---------|----------|----------|---------|--------------|---------------|--------|-----------|---------|----------|---------|
| A — P1C baseline | +0.00 | 0.00 | 0.00 | 704 | 1466.1 | 50.0 | 247.3 | **0** | **0** | **0** | **0.0** |
| B — P1C + observational quote | +8.50 | 8.50 | 0.00 | 25 (quoted) | 1466.1 | 50.0 | 247.3 | **0** | **0** | **0** | **0.0** |
| C — quote-maximizing adversary | **+243.60** | 243.60 | 0.00 | 285 | **1561.7** | **42.3** | **166.0** | **0** | **0** | **0** | **0.0** |

**Seed 0 (the standing-falsifier layout):** A `EBU +0.000`, burden 3268.5,
viability 20%, 0 dead; B `EBU +0.309` (1 quotable action), identical physics;
C `EBU +196.564`, burden 3354.6, viability 20%, 0 dead, 0 reserve crossings.
Predicate: `harm_persistent = False` in all three (mean tail harm ≈ −1571,
−1571, −1513 — i.e. far *better* than doing nothing).

**Zero protocol violations and zero duplicate-settlement attempts** across all
36 runs; **physical overuse was exactly 0.0 everywhere** (P1C's aggregate cap
never exceeded).

## Observational identity

Arm B was **byte-identical** to arm A on **all 12 layouts** (max |diff| =
0.000e+00 in every case). Falsifier **F6 not triggered**.

## Historical positive controls (released V2.6 code, unmodified)

| Control | Outcome |
|---------|---------|
| V2.6 **naive**-ledger red-team | **exploit rediscovered** — net EBU `+15.35`, persistent harm `True`, mean tail harm `+102.91` (positive control PASSED: the search is strong enough to find a known failure) |
| V2.6 **guarded** red-team (3×3 hand-built fixture) | no exploit — net `+0.91`, persistent `False` (reproduces V2.6's own published finding for this fixture) |
| V2.6 **seed-0 guarded** standing falsifier | **reproduced exactly** — net `+260.13`, exploit `True`, **5/5 sources dead**, viability at end **0%** |

The seed-0 contrast is the substantive comparison: under the V2.5/V2.6
guarded ledger the coalition earns +260 EBU **while every source dies**; under
P1C + the V3.0 exact quote on the same layout family the adversary earns
comparable EBU (+196 to +291) with **zero reserve crossings, zero Allee
crossings, and zero dead sources**.

## Mechanism of the negative result (why no exploit was found)

P1C physically forbids the harm channel the V2.6 exploit used. Across all 36
runs no source ever crossed its certified reserve or its Allee threshold and
no source died, so the burden of an attacked world never rose persistently
above a **no-action** world by the registered margin. The negative result is
therefore attributable to the **physical permission layer**, not demonstrated
to be a property of the quote equation itself.

## Limitations that materially bound this result (reported, not tuned away)

1. **All 36 runs recorded a domain exit** (35 during the attack horizon,
   median tick 14; 1 in the tail). Cause: P1C/D0 are *unconstrained* — with
   standing demand and no supply, consumer cells drain below 0 and are only
   flagged, never clipped (the V2.9 P1-vs-P1K distinction). Consequently a
   large part of every trajectory lies outside the physical domain, and the
   "no exploit found" conclusion is correspondingly weaker. Nothing was
   dropped or rerun.
2. **Uncertified timestep.** `dt = 1.0` (V2.6 tick fidelity) against a V2.8
   one-edge certificate of `0.438`, i.e. `r_dt = 2.283 > 1`. This is an
   overshoot-permitting regime, reported per run rather than adjusted.
3. **Baseline-relative predicate.** The registered predicate compares the
   attacked tail burden against a **no-action** baseline. In these worlds
   serving demand always beats doing nothing, so mean tail harm is strongly
   negative (≈ −1500) and the predicate **cannot detect degradation relative
   to the serving baseline**. This matters here: **arm C earns +243.60 EBU on
   average while serving less (166.0 vs 247.3), leaving a higher burden
   (1561.7 vs 1466.1) and lower viability (42.3% vs 50.0%) than the plain P1C
   baseline that earns nothing.** Under the preregistered predicate this is
   *not* an exploit, and the predicate was **not** redefined after seeing the
   result — but it is a genuine surprise and is registered below as a new
   open problem.
4. **Arm-B quote coverage is a small minority of accepted flow.** P1C accepts
   many out-edges per source per tick, and the first-model
   one-action-per-source-per-micro-step rule forbids independently quoting
   them (that is exactly the Q13 phantom-credit hazard). Between 382 and 792
   accepted flows per layout were therefore recorded as
   `unquotable_multi_edge` and only 0–43 actions per layout were quoted. This
   is open problem **O3**, not a defect.

## Falsifier status

**F10** (the standing Gate-1C falsifier: positive cumulative exact EBU with
persistent physical harm under P1C within the registered search space) was
**not triggered**. **F6** (observational quote changing the trajectory) was
**not triggered**. No other registered falsifier applies to this gate.

## Scope and non-claims

No exploit found means only: none within the declared fixtures, seeds, action
menu, search depth, width, and predicate. Not a security proof; not
exploit-freedom; not a guarantee. Cumulative signed EBU is an **evaluation
variable** of this gate, never a wallet. No actor economy, wallet, health,
need, price, transfer, market, or learning exists. Passing checks are
numerical validation at declared points, never proof.

## Test and regression totals (kept separate)

- Gate 1C pre-execution suite `test_v30_adversary.py`: **150 checks passed, 0
  failed, 12 groups** — run before the study; contains an AST check proving it
  executes no full-horizon study.
- Gate 1B `test_v30_quote.py`: 184 passed / 0 failed (21 groups);
  `audit_v30_quote.py`: 19 passed / 0 failed.
- Released suites (unchanged, no V2.9 study regenerated): test_energy_balance
  8; test_v22 7; test_v23 4; test_v24 5; test_v25 9; test_v26 15 (+33 prior);
  test_math 34; test_v28 132; test_v29 141; test_v29_behavior 108;
  test_v29_p1c 83; test_v29_d9_d10 114; test_v29_serialization 46.

## Open problems after this gate (none closed)

**O2 is narrowed, not closed**: the V2.6 drive-harvest exploit family was not
reproducible under P1C in these fixtures, but the bound remains unproved and
the search was limited as described above.

New from this gate:

- **O10 — serving-baseline predicate.** The registered no-action baseline
  cannot detect an actor that earns EBU while degrading service, burden, and
  viability relative to the *serving* baseline (arm C vs arm A above). A
  future gate should preregister a serving-baseline harm predicate.
- **O11 — quote-maximizing selection vs service.** Why quote-greedy selection
  under-serves relative to unconstrained P1C flow, and whether that is a
  functional defect of the local quote objective or an artifact of the
  one-action-per-source restriction and `r_dt > 1`.
- **O12 — bounded physical domain for adversarial replay.** A clipped/P1K-style
  variant so adversarial trajectories stay inside `[0, K]`.

Still open unchanged: **O1** persistent restoration, **O3** multi-actor
allocation (also the arm-B coverage limitation), **O4** joint theorem, **O5**
robust quoting, **O6** accounting epochs, **O7** actor-economy social design,
**O8** overexecution settlement, **O9** partially represented dissipation,
plus all inherited V2.9 open problems.
