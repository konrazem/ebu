## GATE 1 — Registered execution integrity

Audit performed read-only against a `git archive` export of the publication ref into the scratchpad. The repository working tree was not touched (`results/` untouched; no Stage A execution; no EconomyRun).

### §1 Scientific coordinate

| item | expected | observed |
|---|---|---|
| commit | `2c4b71d1…fe9e32` | **exact** (`refs/heads/publication/demand-driven-stage-a` on origin) |
| tree | `5afe3978…b78ebf` | **exact** |
| preregistration identity | `a74d8380…54bd17` | **exact** — recomputed independently, and byte-identical in all four attempt snapshots |

### §2 Registered manifest (reconstructed, not executed)

768 declared = 3 classes × 4 arms × 64 replicates; **768 completed, 0 failed, 0 unstarted**. 768 distinct `run_id`, 768 distinct `job_key`, all matching the manifest with byte-identical configuration strings. Seeds are `(1, 2, 3+k, 1000+k)` — a function of replicate alone, so pairing is exact across all 12 cells. Horizons 32/1/32 for A1/A2/A3. Disturbance quiet in all 11,066 epochs; no external displacement ever applied.

### §3 Conformance — three discrepancies, all reporting-level

| # | item | classification |
|---|---|---|
| D1 | `reserve_path` declared §7 as `t = 0..N` (length N+1); emitted length N (`t = 1..N`), omitting `B_total(0)` | **UNDECLARED DEVIATION** — non-substantive: the omitted element is the declared opening zero, and `B_total(t) = V(x₀) − V(x_t)` holds at **2,618/2,618** A1 checks, pinning it to exactly 0 |
| D2 | `capacity_source_residual` declared §7 "exactly 0 **at every epoch** and at the end"; runner checks it once *after* the epoch loop, and never persists it | **UNDECLARED DEVIATION** — non-substantive: I reconstructed the per-epoch quantity from `balance_total`/`potential_after` (external term provably 0) and it is exactly 0 at **11,066/11,066** epochs |
| D3 | §7 "gates verified at every epoch" vs §8 "gate *refusal* invalidates" | **DECLARED EXCEPTION** (§7 below) |

All other registered choices — world, initial states, disturbances, E-arrivals, arms, capacity initialisation, horizons, return rule, admission, affordability, pairing, per-epoch reporting, failure statuses — **EXACT MATCH**.

### §4–§6 Fixture integrity

**A1** — `x₀=(1,7,4)`, `V=9`, all 256; zero arrivals anywhere; opening menu exactly 2 plans; stop is the *first* `x*` post-state in every return, **0 episodes acted after reaching `x*`**; `terminal_no_active_demand` true on exactly the 192 returns; **0** `NO_COMPLETE_PHYSICAL_PLAN` epochs.
**A2** — `x₀=x*`, 1 epoch each; three EBU arms `ALL_PLANS_EBU_UNAFFORDABLE` with order `ADMITTED_BUT_EBU_UNAFFORDABLE`, state untouched, balances 0; control executes to `(4,3,5)`/`(4,2,6)` at EBU `−1`/`−4` — the declared values exactly.
**A3** — scripted arrival at **epoch 3 in all 256**, exactly one order each; all 256 ran the full 32 transitions (`HORIZON_REACHED` only); `prelude_reserve` records **per-owner vectors** (≥4 distinct, incl. totals 8 and 6 with `C=−2`) — not inferred from aggregate 9; `arrival_baseline` is `x*` in only 159/256, as §4 required it not to assume.

### §7 The accepted A3 exception — independently re-derived

| claim | verified |
|---|---|
| 4,737 exempted epochs, 192/256 A3 episodes | **exact** |
| per arm: 1,439 / 1,506 / 1,792 / **0** (`ebu_hostile`) | **exact** |
| epochs **outside** the three-part guard | **0** |
| active-demand epochs not decomposition-VERIFIED | **0** |
| gate refusals anywhere | **0** |

The `NOT_CHECKED` and `NO_ACTIVE_DEMAND` sets are exactly coextensive (4,737 = 4,737). Every exempted epoch is inert: `executed_group_id = "g:[]"`, EBU `0/1`, empty receipts/provenance/restoration/outcomes, state unmoved and **all at `x*`**. So the exception cannot alter any trajectory or endpoint — it decides only whether an episode is *reportable*. It was discovered by attempt 2 **halting** at `A3|control_random_no_ebu|k=0` after 512 jobs (execute.py `596cd870…`), i.e. before any complete 768-job set existed, and all four attempt digests match the published table exactly. One consequence the report does not draw: without it, the three restoring arms would have been wholly invalidated and only the non-restoring arm would have survived A3 — the exception **preserves** arm comparability rather than distorting it. Its per-arm asymmetry is caused by arm behaviour, not by differential treatment.

### §8 Artifact completeness

768 jobs / **11,066 epochs** / 4 attempt records ✓. All four residuals `0/1` and joint gate closed at all 11,066. Mass exactly 12, no negative stock, **0** state-chain breaks, **0** non-contiguous epoch indices, **0** duplicate run IDs, **0** orphan or misfiled episodes. Verifier **36/36**. Source snapshot **46/46** digests match, no extra or missing files, and the digest chain closes (`EXECUTION_INVENTORY.source_manifest_digest` = `SOURCE_MANIFEST.manifest_digest` = recomputed `939cc461…`). Protected packages recompute byte-identically.

One item needs stating precisely: **preflight is 76/76 against the published record**, not the 75/1 my run produced. The single failure is an artifact of my own extraction — the check asserts `tree_is_clean is False`, and my `git archive` export has no git repo, so it reports `true`. The preserved `SOURCE_MANIFEST.json` records `tree_is_clean: false` with the required note, satisfying the predicate. Relatedly: HEAD (`a6dbed5…`) does **not** identify the run state — Stage A was executed from an uncommitted working tree, so the 46 per-file digests plus snapshot are the sole provenance, and they verify completely.

---

# GATE 1 CONDITIONAL PASS

**Exact declared qualification:** registered execution integrity is established for all 768 jobs and 11,066 epochs, subject to three deviations from the frozen preregistration, none of which alters a recorded trajectory, endpoint value or arm comparability:

1. the **declared, author-accepted** §7/§8 decomposition-gate exception, verified exactly coextensive with its three-part guard at 4,737 epochs in 192 A3 episodes, with zero epochs outside it and zero active-demand epochs unverified;
2. **undeclared:** `reserve_path` omits its `t = 0` element against §7's `t = 0..N` — the omitted value is provably exactly 0;
3. **undeclared:** `capacity_source_residual` was enforced only at end-of-episode, not "at every epoch" as §7 requires, and is not persisted — the per-epoch requirement is nonetheless satisfied in fact at all 11,066 epochs, reconstructed independently here.

Items 2 and 3 are recorded for the register; neither is a basis for withholding the gate, and both should be declared rather than left implicit in any Stage-B protocol. The §7/§8 question remains unresolved in general, exactly as the publication states.

**READY FOR SCIENTIFIC GATE 2 — CONSTRUCT VALIDITY**

Gate 2 not begun. No outcome was interpreted, no arm compared, no metric derived, and no Dynamic EBU theory applied to these records.