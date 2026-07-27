# V2.9 Release Manifest — local preservation controller and behavioral validation

Overarching provenance record for the V2.9.0 release packaging (Release Gate 1).
**Validation is not proof**: every check count below is numerical validation at
declared fixture points; the only proved statement introduced by V2.9 is the
one-step aggregate reserve-preservation theorem (Gate-2.1B review, Thm 4.1),
itself not peer reviewed. No general stability, sustainability, dominance, or
monetary claim is made.

## Git provenance

| Field | Value |
|-------|-------|
| V2.8 baseline tag | `v2.8.0` (annotated, tag object `7842d35c222716e0edfdc74a668363cd25dc4e98`) |
| V2.8 baseline peeled commit | `05ba91212753b2016548a3aaaadd669386a9a9bf` (= `origin/main` at packaging time) |
| V2.9 branch | `v2.9-local-law-validation` |
| First V2.9 commit | `2324b54` "V2.9 design: preregister local-law behavioral validation" |
| Deterministic (D1–D8) result commit | `6d17f9e` "V2.9 results: record preregistered deterministic runs" |
| D9/D10 Attempt-2 implementation commit | `12faa5390e6c8edb3d566e2e624a632aa4114dad` |
| D9/D10 result commit | `2074786d4c5c8a8ea64b9f3c20008ce011667093` |
| Serialization audit commits (Gate 2.4B) | `84d87eb` (fail-closed writers + tests), `f0bb668` (repair audit note) |
| Pre-packaging HEAD | `f0bb668b14e793c07a44f3747f9de93bd619a335` |
| Packaging commits | `aac747d` (foundation doc + PDF), `4418d82` (notes/README/citation/CI), `3af0914` (this manifest), plus the follow-up commit recording these SHAs |

## Plans and hashes (canonical sorted-keys SHA-256, enforced at run time)

| Plan | Canonical hash | Raw file SHA-256 |
|------|----------------|------------------|
| `v29_deterministic_plan.json` | `af8f119b4af433290e6fc2546913868421e2f4adcaa467eb6d4d31e5e4856aa2` | `a1a5ccaa2b7a740b0a33941350e33459f161041dae4d0bd751c89fa297ad9e8f` |
| `v29_d9_d10_plan.json` (Amendment 5) | `87ad0ae2eb3cca6d86a56378c4a76508b29d7a63cb39ac74f5a362be1004c34a` | `a931bc09e2a7cbb86f12c3c805fbb851aae84e09e240558c8cc2176183dff5bd` |

## Exact commands (deterministic; no options, no seeds)

```
python3 exp_v29.py         > results/v2.9/deterministic/v29_deterministic_stdout.txt   # run once (locked)
python3 exp_v29_d9_d10.py  > results/v2.9/d9_d10/v29_d9_d10_stdout.txt                 # run exactly once (Attempt 2)
venv/bin/python make_paper_v29.py   # rebuilds the V2.9 PDF from committed artifacts
```

Python for the committed runs: **3.14.2**. Both harnesses recompute their plan
hash, refuse any command-line option, and refuse to overwrite completed results.

## Test totals (all suites pass at packaging time; separate on purpose)

| Suite | Checks | Scope |
|-------|--------|-------|
| `test_energy_balance.py` | 8 tests | V2.0 core |
| `test_v22.py` | 7 tests | V2.2 ledger + safe law |
| `test_v23.py` | 4 tests | V2.3 regeneration |
| `test_v24.py` | 5 tests | V2.4 harvest rules |
| `test_v25.py` | 9 tests | V2.5 EBU ledger |
| `test_v26.py` | 15 tests (+ reruns the 33 prior) | V2.6 adversarial search |
| `test_math.py` | 34 checks / 8 groups | V2.7 mathematics |
| `test_v28.py` | 132 checks / 11 groups | V2.8 discrete validation |
| `test_v29.py` | 141 checks / 15 groups | V2.9 D0 conformance |
| `test_v29_behavior.py` | 108 checks / 9 groups | V2.9 deterministic behavior (D1–D8) |
| `test_v29_p1c.py` | 83 checks / 12 groups | P1C conformance |
| `test_v29_d9_d10.py` | 114 checks / 20 groups | D9/D10 preregistration/harness |
| `test_v29_serialization.py` | 46 checks / 6 groups | serialization audit (validates committed results) |

A check count is never a theorem count.

## Deterministic run counts

- D1–D8 wind tunnel: **24 runs** (D1:2, D2:3, D3:4, D4:3, D5:4, D6:3, D7:3, D8:2).
- D9/D10 study: **144 runs** (D9 = 4 arms; D10 = 140 = 80 core + 60 secondary),
  all present exactly once; **18 domain exits recorded, none dropped**.

## Artifact paths and SHA-256 hashes (at packaging time)

| Artifact | SHA-256 | Bytes |
|----------|---------|-------|
| `results/v2.9/deterministic/v29_deterministic_summary.json` | `5501fbc289b087bd31e86337c27f60ecb2582ab75c7919148b870787a5c70c7c` | 35 925 |
| `results/v2.9/deterministic/v29_deterministic_trace.json` | `c6f79056940ef6780ffad5b334efcb61e41fe9465a3d6a28fdf1960df6c458fc` | 5 599 639 |
| `results/v2.9/deterministic/v29_deterministic_stdout.txt` | `7a5fa39e4936d270fb6e0e8c068fc58aee34585654d8fe979d9f16c81c0389b1` | 19 508 |
| `results/v2.9/d9_d10/v29_d9_d10_summary.json` | `55603b5751b5b945e66165614d6c9993a6f4defadfb8aa2143f50558d536d3b4` | 267 848 |
| `results/v2.9/d9_d10/v29_d9_d10_trace.jsonl.gz` | `4b1ef577c64e000566e464362703da34ddd98eacdd3fa35812523b63b3da3da5` | 2 852 962 |
| `results/v2.9/d9_d10/v29_d9_d10_stdout.txt` | `c9537419b657671878df4abc05b0c44b36f4d401d0840512057c497aad528b8a` | 4 587 |
| `results/v2.9/d9_d10/ATTEMPT_1_FAILURE.md` | `8040017632a8911702144ef0423e4d8de22b55ca2f2e6ab4bf45d687e050555d` | 4 367 |
| `results/v2.9/d9_d10/ATTEMPT_1_stdout.txt` | `79d1def9fc5bc81672ce112639f01ba39f931407dee8c2463464fdcb4b8571ab` | 513 |
| `Energy_Balance_Project_Foundation_v2.9.pdf` | `e06f9cc384ec952652300336d54b8c0c1a05ae2302bb8d9cc8fbb2f2d0a27673` | 275 536 |

(The `MANIFEST.md` and `ATTEMPT_2_SERIALIZATION_REPAIR.md` companion documents
are prose and carry their own history; the repair audit records the result-time
hashes.)

## Attempt provenance (D9/D10)

- **Attempt 1 failed** (Gate-2.4A harness-integrity defect, found before any
  scientific use) and is preserved: `ATTEMPT_1_FAILURE.md`, `ATTEMPT_1_stdout.txt`.
  It produced no scientific result.
- **Attempt 2 ran exactly once** (implementation commit `12faa53…`); **no
  physical trajectory was regenerated afterwards**.

## Serialization repair provenance

15 diverging runs had `stability_tau`/`stability_amp` overflow to `inf`;
authorized post-processing replaced those two diagnostic fields with JSON
`null` (nothing else changed; no rerun). 3 further domain-exit records were
natively undefined (exit before burn-in), so the committed summary holds 18
null diagnostic pairs = 15 repairs + 3 native. Full reconciliation, exact run
IDs, and reasons: `results/v2.9/d9_d10/ATTEMPT_2_SERIALIZATION_REPAIR.md`.
Gate 2.4B installed strict fail-closed serialization
(`serialization_v29.py`); the pre-repair (never-committed) summary was not
preserved, so no pre-repair hash exists.

## D9/D10 headline results (committed values)

- **D9**: D9-A (reserve-blind) and D9-B (soft) both **collapse**, reserve
  crossed at tick 8; soft delays the Allee crossing (tick 24 vs 17) and
  reduces over-use (183.045 vs 201.845) but does not preserve. D9-C/D9-D
  (P1C): **safe rationing**, source held at exactly `R_eff = 11`, zero
  reserve/Allee crossings, cap binding 193/200 ticks, delivered 130.82 /
  unmet 69.18, `O_physical ≤ 10⁻⁹`, zero one-step-preservation violations on
  200 eligible ticks; D9-C ≡ D9-D on every recorded metric.
- **D10** (35 runs/policy): P0 → 35 safe_rationing (no service; not success);
  P1 → 25 collapse + 10 safe_service (over-use in 25/35); soft → identical to
  P1; **P1C → 25 safe_service + 10 safe_rationing, zero collapse, zero
  over-use**. Collapse tracks the registered analytic boundaries
  (`d/g_max ≥ 0.9`, low `η`; safe service ≈ `d/g_max ≤ η` and `< 1`).

## Epistemic scope

- **Theorem (unreviewed)**: one-step aggregate reserve preservation under
  explicit hypotheses (state P, feasibility, budget-capped export).
- **Algebraic**: soft reserve penalty vanishes at the boundary (no barrier);
  zero export cannot preserve an infeasible state.
- **Numerical conformance**: all suite checks listed above.
- **Deterministic observation**: every D1–D10 result; limited strictly to the
  registered fixtures.
- **Design candidates only (no code)**: ecological-debt vector, restoration
  credit, EBU issuance/wallets; scalar EBU explicitly **not yet justified**
  (independent review).
- **Open problems**: joint constrained preservation+dissipation theorem;
  infinite-horizon controlled-invariant kernel; multi-source joint invariance;
  stochastic/adversarial robustness of P1C; debt attribution and verified
  restoration predicate; reserve certification of `R_eff` itself.

## Validation is not proof

All 144 + 24 committed runs are deterministic observations. Passing test
suites validate the implementation and the committed artifacts at declared
points; they do not prove any theorem, and no claim of general stability,
stochastic robustness, scale invariance, actor-level success, or monetary
validity of EBU is made or implied.
