# V3.0 Gate 1D-B / O14 — Multi-Out-Edge Capability Study (record)

**This is a gate study record, NOT a release manifest.** It records the single
official execution of the locked 60-run O14 multi-out-edge capability study
(plan `v30_o14_multi_edge_plan.json`) by the corrected fail-closed runner.
Passing checks are numerical validation at declared points, never proof. The
bounded service wrapper remains **outside the V2.8 D0 theorem** (O13); the
exact-total-quote greedy rule is a candidate heuristic, not a theorem; **O3
(aggregate multi-edge settlement) remains open** — nothing here settles it.

> ### Headline
> **With genuinely multi-out-edge worlds (2–4 simultaneous outgoing choices
> per source), exact-total-quote maximization again produced no service
> misalignment: post-burn-in delivered service of arm D equals arm B exactly
> in all 6 worlds at both certified timesteps** (deficit +0.000, D/B ratio
> 1.0000, 0 alignment failures in 12 comparisons) — even in W2, where B and D
> provably select **different destinations** from tick 1, and in W5, where D
> switched its selected edge 37/33 times tracking the registered reversal.
>
> **The A-vs-B capability cost is exactly 0.000 in all 12 world-timestep
> pairs — including W4 and W6 where the one-action restriction genuinely
> binds** (arm-A min σ = 0.283/0.283 in W4, 0.215/0.000 in W6). The binding
> restriction (H2 supported) produced no measurable post-burn-in service
> loss (H3 not supported), because destination-stock buffering absorbs the
> delivery pattern differences under bounded, demand-capped service.
>
> **Falsifier F13 FIRED: all six worlds are non-discriminating** under the
> registered discriminator (nonzero A-vs-B capability cost, or D/B service
> ratio ≠ 1). This is a reported scientific outcome of the registered
> design, not a defect: the worlds successfully created binding restrictions
> (F4 did not fire) and divergent choices (t0 divergence and W5 switching
> observed), yet none of it changed post-burn-in delivered service.
>
> The only under-service in a feasible world came from **arm S** (the
> registered volume comparator) in W1: its declared stock-buffer blindness
> cost it 4.315/5.000 post-burn-in service units — separating
> restriction-generic loss (zero, B) from heuristic-specific loss (S's own).

## Provenance (both execution attempts)

| Field | Attempt 1 (failed preflight) | Attempt 2 (this record) |
|-------|------------------------------|-------------------------|
| Runner state | `35a850f77dbe9f2391ef7dcb0663b7aab4fb8a36` (defective substring guard) | `4939e1f99935185952f3e1c82a6993a4388839f4` (corrected AST guard) |
| Exact command | `mkdir -p results/v3.0/gate1db && set -o noclobber && python3 exp_v30_o14.py > results/v3.0/gate1db/v30_o14_stdout.txt` | `mkdir -p results/v3.0/gate1db; set -o noclobber; python3 exp_v30_o14.py > results/v3.0/gate1db/v30_o14_stdout.txt` |
| Exit status | **1** (preflight self-match: `FATAL: exp_v30_o14.py imports a randomness module`) | **0** (complete study) |
| Trajectories run | **none** — failure preceded the banner, the sentinels and `execute_registered_study()` | 60 of 60, frozen order, no retry/rerun/subset |
| Artifacts | one 0-byte stdout file (SHA-256 `e3b0c442…52b855`), removed under separate authorization after recording | `v30_o14_stdout.txt`, `v30_o14_trace.jsonl.gz`, `v30_o14_summary.json` (below) |
| Record | `V3.0_GATE1D_B_O14_RUNNER_CORRECTION.md` (sole record of the event) | this manifest |

The runner was therefore invoked twice in the historical audit chain, but the
**corrected runner was invoked exactly once**, and **exactly one scientific
execution ever occurred** — attempt 1 ran no trajectory, wrote no scientific
byte, and could never have passed its own defective preflight
(root cause and evidence in `V3.0_GATE1D_B_O14_RUNNER_CORRECTION.md`).

| Field | Value |
|-------|-------|
| Branch | `v3.0-local-ebu-foundation` (HEAD == origin, clean tree at start) |
| Preregistration commit | `446386f88d10ee0052d1821726904e4aa5bee008` |
| Implementation commit | `919421c9be0975b9a4a23e9ad9f5e90781d2272f` |
| Runner-preparation commit | `35a850f77dbe9f2391ef7dcb0663b7aab4fb8a36` |
| Fail-closed correction commit (pushed before this run) | `4939e1f99935185952f3e1c82a6993a4388839f4` |
| Execution SHA (this run) | `4939e1f99935185952f3e1c82a6993a4388839f4` |
| Plan canonical hash (recomputed & enforced at run start) | `2524ba268db004969e04f9c8636cc240b643f0f7685507edf65350ea98a37745` |
| Plan raw SHA-256 | `00c4dd472eb332e57865f845e41265032fa69ef3535bb170a8ade013f783d22a` |
| Equation version | `v3.0-gate0.1` |
| Python / OS | 3.14.2 / macOS 26.5.2 (Darwin, arm64) |
| Attempts of the corrected runner | **exactly one**; nothing rerun, tuned, filtered or suppressed |

Protocol (`V3.0_GATE1D_B_O14_MULTI_EDGE_PROTOCOL.md`), plan and `o14_v30.py`
were verified byte-identical to their preregistered/locked commits before
execution; the pre-execution suite passed **299/299 in 17 groups**; the
committed `preflight()` was independently verified read-only (returned the 60
registered specifications, created no file, printed nothing, ran no
trajectory) before the output directory was created.

## Artifacts (immutable; written by the runner, unmodified)

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `v30_o14_summary.json` | `4c258f822d5cd4ae5d9a5fe70909cf5a00a305ae4d34b26dc67491429ea68327` | 221 894 |
| `v30_o14_trace.jsonl.gz` | `77d190caced2bdc22427213e2b0ca5a481fb537593848560d80c5ea0a8f5991d` | 4 569 832 |
| `v30_o14_stdout.txt` | `dff9b2329082898904f5a11ba6858e31404b9e3901d1f86da4b848d8362caacc` | 9 949 |

Dependencies (state at the execution SHA):

| File | SHA-256 | Bytes |
|------|---------|-------|
| `v30_o14_multi_edge_plan.json` | `00c4dd472eb332e57865f845e41265032fa69ef3535bb170a8ade013f783d22a` | 34 959 |
| `V3.0_GATE1D_B_O14_MULTI_EDGE_PROTOCOL.md` | `b64701b6c955370d72c45a0bd9481d87966e48c2e00fe1a14add7539f441050a` | 33 065 |
| `o14_v30.py` (implementation) | `6d23ce9d481345c5f1d01dd7dd42b1742301fe67e1587b1f6da68af6c4f6eccb` | 39 974 |
| `exp_v30_o14.py` (corrected runner) | `4bd5915e89187935b26d8b36714555bf49b714e6afd702bb3baaa2d30c5cb296` | 37 695 |
| `test_v30_o14.py` (corrected suite) | `9bb5d1228ae1912197f3a43860fef036806c08851bf28781134d735df6751bc0` | 79 208 |
| `V3.0_GATE1D_B_O14_RUNNER_CORRECTION.md` | `3153c445e03fa4e3431ac036c53562853d33ea80536d5d46c829101f432587c9` | 9 739 |

**60 run records, 60 unique identifiers** — the complete registered Cartesian
product (6 worlds × arms A/B/C/D/S × 2 timesteps), frozen order preserved,
none missing, extra, duplicated or dropped; **no arm E**. Trace: **12 000
rows** (200 ordered ticks × 60 runs), 39 509 083 bytes uncompressed,
`gzip -t` clean, one strict-JSON object per row, plan hash on every row.
Strict JSON throughout (`allow_nan=False`); every numeric field finite. All
per-run aggregates (service, EBU, unmet, demand, reserve crossings)
reconstruct from the trace rows to < 1e-9.

## Bounded service and physical integrity (all 60 runs)

- **0 domain failures; no negative state** anywhere;
- `service ≤ available`, `service ≤ demand`; `unmet = demand − service`
  exactly; unmet demand reported, never hidden;
- max |ledger residual| = **1.03e-14**; non-negativity corrections 0.0;
- **physical overuse ≤ 3.0e-14 total** (within the registered 1e-9-scale
  tolerance; P1C cap never materially exceeded);
- **0 reserve crossings in all 60 runs** (corrected Gate 1D-A scale-aware
  tolerance); 0 Allee crossings; 0 dead sources;
- request-shaping identity held every tick (executed `q_acc` = selected menu
  `q_acc`; any violation would have raised before this record existed).

## Certified timesteps

Per-world certificates recomputed by the released `d0_v29` functions at run
start and equal to the locked plan values exactly; all six worlds bind on the
Gershgorin certificate. `r_dt` exactly **0.5** (conservative) and **0.9**
(near-certificate) in every run; `r_dt ≤ 1` in **all 60 runs** (F11 clean).
One shared timestep per paired world across all five arms.

## Required analyses

### A versus B — capability cost of the one-action restriction (C1)

**Exactly 0.000 post-burn-in in all 6 worlds at both timesteps.** The
restriction **genuinely binds** in W4 (arm-A min σ 0.2826/0.2831) and W6
(0.2145/0.0000) — the direct C1 measurement Gate 1D could not make — yet
buffered bounded service erased the difference: arm A spreads deliveries over
2–4 destinations per tick while B serves one per micro-step, and
destination-stock buffering plus the demand cap make the post-burn-in service
identical. H2 supported, H3 not supported, F4 not fired.

### B versus C — observational identity (F1)

**Physically identical in all 12 paired comparisons** (max |Δx| exactly
0.0e+00 over every tick of every pair), while arm C accumulated positive
observational EBU (+53.8 to +1180.6). **F1 not fired.** Quote coverage 1.0
over accepted actions in arms C and D (47 976 positive-quote candidate
evaluations, 0 zero, 0 negative).

### B versus D — PRIMARY alignment comparison (C3)

| World | dt | pbi service B | pbi service D | D/B ratio | failure |
|-------|----|---------------|---------------|-----------|---------|
| W1_eta_split | cons / near | 51.680 / 93.023 | 51.680 / 93.023 | 1.0000 / 1.0000 | False / False |
| W2_severity_split | cons / near | 13.523 / 24.342 | 13.523 / 24.342 | 1.0000 / 1.0000 | False / False |
| W3_volume_split | cons / near | 15.013 / 27.024 | 15.013 / 27.024 | 1.0000 / 1.0000 | False / False |
| W4_budget_bind | cons / near | 37.422 / 67.360 | 37.422 / 67.360 | 1.0000 / 1.0000 | False / False |
| W5_reversal | cons / near | 34.698 / 62.456 | 34.698 / 62.456 | 1.0000 / 1.0000 | False / False |
| W6_infeasible | cons / near | 51.024 / 91.843 | 51.024 / 91.843 | 1.0000* / 1.0000 | False / False |

\* 0.9999999999999999 — one ULP, inside the registered `1e-9·(1+|v|)`
tolerance.

**0 service-alignment failures in 12 comparisons** under the Gate 1D
predicate applied verbatim (thresholds untouched). Unlike Gate 1D, this
result now covers **genuine destination choice**: in W2 the exact total quote
and the force provably rank different edges from t0 at both timesteps (D's
EBU differs from C's: 52.15 vs 53.83 cons, 83.97 vs 87.49 near — D took
different actions than B), and in W5 D's selected edge switched 37/33 times
(B's force rule: 39/35). Choice divergence occurred; service divergence did
not. D earned +52.1 to +1180.6 EBU with zero reserve crossings and zero
overuse (H4; F5, F6, F8 not fired).

### S versus B and D — registered secondary attribution

Arm S (η·q_acc volume score toward demanding destinations, stock-blind by
declared limitation) matched B and D everywhere **except W1**, where it
under-served (pbi 47.364 vs 51.680 cons; 88.023 vs 93.023 near; unmet 4.315 /
5.000) and was classified `distributive_or_policy_under_service` at both
timesteps — the only under-service in any feasible world. Attribution:
service loss in these worlds is **heuristic-specific, not
restriction-generic** (B, C and D under the same one-action restriction lost
nothing), and the quote heuristic (D) was not the loser — the volume
heuristic (S) was.

### Timestep sensitivity

Alignment verdict consistent across both timesteps in all 6 worlds (failure
False at both everywhere).

## Outcome classes (60 runs)

| Class | Count | Runs |
|-------|-------|------|
| `preserve_and_serve` | **48** | all A/B/C/D runs of W1–W5 + W1–W5 S runs except W1 |
| `physical_impossibility` | 10 | all 10 W6 runs (registered infeasible world; explicit unmet demand 67.09/120.76–120.77 pbi; **0 reserve crossings**) |
| `distributive_or_policy_under_service` | 2 | `O14_W1_eta_split|S|conservative`, `O14_W1_eta_split|S|near_certificate` |

No `numerical_or_domain_failure`, `systemic_collapse`,
`destructive_service`, `safe_rationing_physical_scarcity`,
`preserve_but_under_serve` or `unclassified`.

## O3 settlement-free aggregate diagnostic (arm A; nothing settled)

2 399 arm-A action ticks, **all** with ≥ 2 simultaneous actions. Total group
quote **+3 894.460**, naive independent per-edge sum **+3 910.750**, measured
double-count **+16.289** (614 ticks strictly positive; min per-tick
double-count −4.9e-15, within tolerance). **Naive ≥ group held (Prop 10.2;
F9 not fired)** — the naive sum over-credits, confirming the registered
convexity argument on live data. **Arm A settled and allocated nothing; its
EBU is exactly 0.0 in every tick of all 12 runs. O3 remains open.**

## Hypotheses (frozen evaluation rules)

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| H1 B ≡ C byte-identical | **supported** | 12 of 12 identical pairs |
| H2 restriction binds somewhere | **supported** | W4 and W6 at both dts (min σ_A 0.283/0.283, 0.215/0.000) |
| H3 nonzero A-vs-B capability cost somewhere | **not supported** | no world-dt with cost > 1e-9 (post-burn-in cost exactly 0 everywhere) |
| H4 D preserves reserves, no overuse | **supported** | 0 crossings, 0.0 overuse over all D runs |
| H5 quote choice adapts at W5 reversal | **supported** | D selected-edge switches 37 (cons) / 33 (near) |
| H6 per-unit vs total rank differently | **supported** | 4 798 divergent candidate-ranking ticks |
| H7 no persistent D under-service in feasible worlds | **supported** | 0 failures |
| H8 W6 exposes scarcity as explicit unmet demand | **supported** | pbi unmet 67.087–120.775 in all 10 W6 runs |
| H9 rest / all-negative-quote states reportable | **supported** | 4 voluntary rests recorded; quote sign counts recorded |
| H10 naive sum ≠ aggregate quote without proof | **supported** | 2 399 multi-action ticks, 614 strictly positive double-counts |

## Falsifiers

**F13 FIRED — all worlds non-discriminating** (evidence:
`discriminating_worlds = []`; no world-dt showed a capability cost > 1e-9 or
a D/B service ratio away from 1). Reported, not absorbed: the registered
discriminator was outcome-level service, and the study shows that binding
restrictions and divergent choices did not move it. The design's
choice-level discrimination did occur (W2 t0 divergence, W5 switching, S's
W1 under-service) and is recorded above.

F1–F12, F14, F15 **not fired**: no B/C physical difference (F1); per-tick
menu/budget/timestep identity asserted structurally (F2/F12); every world had
≥ 2 simultaneously active out-edges — max 2/2/2/4/2/3 (F3); the restriction
bound in W4/W6 (F4); no positive-EBU persistent deficit (F5); no D reserve
crossing or overuse (F6); information boundary AST- and poison-enforced
before execution (F7); no per-unit ranking divergence in D's executed
selections (F8, 0 hits); no negative double-count beyond tolerance (F9); no
stale/out-of-range quote (F10, 0 hits); no `r_dt > 1` (F11); plan hash locked
and predicates verbatim (F14); static graphs only (F15).

## Limitations that bound the conclusion

1. **Outcome-level non-discrimination is a property of these worlds'
   buffered, demand-capped service semantics**, not proof of harmlessness of
   quote-greedy choice: destination stocks absorbed every delivery-pattern
   difference over the 150-tick post-burn-in window. Worlds with tighter
   buffers, perishable stock or service drawn directly from flows could
   discriminate; none is registered here (F14 forbids adding one post hoc).
2. **O3 remains open** — the +16.29 measured double-count quantifies the
   naive-sum over-credit but no aggregate settlement rule is validated.
3. **Idealized study**: τ = 0, exact observations, no noise (Gate 1E
   untouched). Six small deterministic worlds, 200 ticks, no stochastic
   layouts (numerical validation only; O12/O13 theorem-less).
4. Arm S's loss is specific to its declared stock-blindness; it is not a
   general statement about volume heuristics.

## Test and regression totals (kept separate from the study)

- O14 pre-execution suite `test_v30_o14.py` (corrected): **299 passed, 0
  failed, 17 groups**, run at the execution SHA immediately before this
  study; AST-proven to drive no registered-horizon trajectory.
- The correction-gate regression battery
  (`V3.0_GATE1D_B_O14_RUNNER_CORRECTION.md` §9) covers the released suites;
  none is re-run or altered by this record.

## Status of the open registrations

- **O14 — addressed by this study**: every registered world gave the source
  2–4 simultaneously active out-edges; the C1 capability cost is now
  **measured** (zero post-burn-in, with the restriction demonstrably
  binding), closing Gate 1D's Limitation 1 for these families.
- **O10** — the serving-baseline predicate ran on genuine multi-edge choice
  and again did not fire; still validated only where it did not fire.
- **O11** — no quote-choice service misalignment found under matched
  capability, now including genuine destination choice (W2/W5); the
  buffered-service caveat above bounds the claim.
- **O3, O12, O13** — open and untouched. **O15** — corrected tolerance
  discipline carried through (0 spurious crossings; W6 near σ reached 0.0
  with the source held at its reserve to 1e-14).

## Actor economy and excluded layers

**Gate 1E and Gate 2 remain paused and untouched.** No migration, diffusion,
convection, mobile actors, wallets, markets, prices, health or learning work
is authorized by this record; cumulative signed EBU remains an evaluation
variable, not a wallet.
