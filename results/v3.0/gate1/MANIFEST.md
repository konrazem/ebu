# V3.0 Gate 1B Conformance Manifest — local signed EBU quote layer

**This is a gate conformance record, NOT a release manifest.** It records the
single authorized execution of the preregistered Q1–Q21 conformance suite for
the pure observational quote module. Passing checks are numerical validation
at declared fixture points, never proof. No behavioral trajectory was run;
Q22 (the V2.6 adversarial replay) is registered in the locked plan and was
**explicitly not run** — it belongs to Gate 1C under separate authorization.

## Provenance

| Field | Value |
|-------|-------|
| V2.9 baseline tag | `v2.9.0` (peeled `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0`) |
| V3.0 Gate 0 / 0.1 commits | `945d7ef` / `9eff5ef` |
| V3.0 Gate 1A review commit | `02fd026` (verdict: PASS WITH CORRECTIONS) |
| V3.0 Gate 1A preregistration commit | `a9c5909` |
| V3.0 Gate 1A.1 corrections commit | `d45f059` (Gate-1B starting HEAD) |
| Plan canonical hash (sorted-keys compact JSON, SHA-256) | `a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061` |
| Plan raw file SHA-256 | `5f01a1fd554bfb2f5e684dc318a805f2887d51274e456c98d1a1d5788d1a6f4f` |
| Python | 3.14.2 |

## Exact commands

```
python3 test_v30_quote.py   > results/v3.0/gate1/v30_quote_validation.txt
python3 audit_v30_quote.py  > results/v3.0/gate1/v30_quote_audit.txt
```

Both commands verify the canonical plan hash at start and fail closed on
mismatch. The released regression suites were run separately (below) and
their totals are kept separate from the V3.0 totals: a passing released
suite does not validate the quote law, and vice versa.

## Conformance totals (test_v30_quote.py)

**184 checks passed, 0 failed, in 21 groups (Q1–Q21).** Per group:
Q1: 5, Q2: 3, Q3: 4, Q4: 5, Q5: 6, Q6: 19, Q7: 6, Q8: 2, Q9: 21, Q10: 3,
Q11: 5, Q12: 10, Q13: 27, Q14: 3, Q15: 9, Q16: 6, Q17: 3, Q18: 14, Q19: 9,
Q20: 16, Q21: 8. (A check count is never a theorem count; several groups
aggregate hundreds of random cases into single checks.)

Audit (audit_v30_quote.py): **19 checks passed, 0 failed** — plan hash lock,
implementation/test independence, forbidden-identifier scan, strict
fail-closed serialization, equation-version consistency
(`v3.0-gate0.1`), schedule reproducibility and event-identifier determinism,
plan-to-test coverage with Q22 registered-not-executed, actor/wallet/health
modules absent, released V2.9 files unchanged relative to `v2.9.0`.

## Seed, fixtures, tolerances

- Conformance seed: **30001** (fresh). Behavioral seeds 0–9 and 100–139 not
  used anywhere in this gate.
- Frozen random ranges (plan `random_checks.ranges`): `x ∈ [0, 24]`,
  `α, β ∈ {0.5, 1, 2}`, `χ ∈ {0, 1}`, `R ∈ {0, 8}`,
  `η ∈ {0.5, 0.7, 0.9, 1.0}`, `Δt ∈ {0.2, 1.0}`, `c₀ ∈ {0, 0.05}`,
  `λ_L ∈ {0, 0.1}`; drives `u ∈ [−2, 2]` (not constrained by the plan;
  declared here).
- Random case counts as frozen: Q6 16 branch + 200 random; Q7 100 (+1
  labelled `c₀` case, 200 midpoints); Q8 100 × 5 settlement points; Q9 20;
  Q10 50 sequences + 10 cycles; Q11 50 + 1 negative control; Q12 10; Q13
  registered fixture + 20 variants; Q20 4; Q21 52 rebuilt twice.
- Tolerances: analytic `1e-9·(1+|expected|)`; identities `1e-9·(1+|V|)`;
  Q17 byte-identity = exact float tuple equality; strict JSON
  (`allow_nan=False`) fail-closed everywhere.
- Non-vacuity (F12 guard): enforced on Q6, Q7, Q8, Q10, Q11, Q13, Q21
  sample sets, plus a negative control proving an all-zero fixture set
  fails the guard.

## Worked-example results and maximum numerical residuals

| Fixture | Expected | Observed residual |
|---------|----------|-------------------|
| E1 exact | `+7.94` | `0.0` |
| E1 linear diagnostic | `+15.18` | `0.0` |
| E2 exact | `−5.52` | `8.9e-16` |
| E2 linear diagnostic | `−0.08` | `0.0` |
| E3 net (= −ΣC) | `−0.10`, state exactly restored | `5.3e-16`; state `[10.0, 10.0]` exact |
| Regeneration fixture | idle quote exactly `0` (g = 2, z = 12) | exact `0.0` |
| Split counterexample | independent `32` vs joint `20`, phantom `12` | `≤ 1e-12` |

Maximum residual over all identity checks (telescoping, driven identity,
oracle cross-checks): within the declared `1e-9`-scale tolerances; the
worked-example maximum is `8.9e-16`.

## Negative-control outcomes (all fired)

linear settlement would misprice E2 by `5.44` (detected); naive pre-tick
baseline credits natural regeneration by exactly `−δ_loc` (detected);
undriven theorem applied to a driven path omits a residual `> 1e-3`
(detected); duplicate settlement rejected with violation; independent frozen
split quotes issue 32 vs 20 actual (phantom 12 reproduced); positive raw
quote beyond P1C permission not quotable (domain error); P1C-permitted
action quoted negative; forbidden cost categories (`state_carried_burden`,
`monetary_cost`, `labour_cost`, `audit_penalty`, `fraud_penalty`,
`unspecified`) all rejected at construction and the numeric double-count
detected; stale-epoch settlement rejected; overexecution produced zero
issuance with mandatory violation record (overdraw recorded, O8 flagged
open); nine runtime poison probes plus a World-object probe all rejected;
zero-only fixture sets fail the non-vacuity guard.

## Scope and non-claims

The quote module is observational only: it mutates no physical state, holds
no wallet/health/price/market/debt state, evaluates no global functional,
performs no rollout, and does not replace or reinterpret P1C. This gate
validates local conformance of the implementation to the preregistered
equation at declared points. It does **not** prove incentive compatibility,
adversarial security (Q22 not run; the V2.6 seed-0 exploit remains the
standing falsifier), long-horizon behavior, economic viability, or any
theorem. Settlement for `q_meas > q_acc` implements only the registered
minimum fail-closed envelope; O8 remains open.

One pre-commit implementation defect was found by the suite's own Q18 scan
and fixed before any commit: a local parameter named `debt` in the
registry's rejection helper tripped the forbidden-identifier scan and was
renamed (`requires_physical_handling`); no equation or semantics changed.

## Released regression suites (separate totals; no V2.9 study regenerated)

All 13 released suites pass unchanged: test_energy_balance 8;
test_v22 7; test_v23 4; test_v24 5; test_v25 9; test_v26 15 (+33 prior);
test_math 34 checks; test_v28 132 checks; test_v29 141; test_v29_behavior
108; test_v29_p1c 83; test_v29_d9_d10 114; test_v29_serialization 46.

## Remaining open problems (none closed by this gate)

- **O1** persistent restoration pricing (capacity coordinate).
- **O2** drive-harvest bound under the P1C cap; V2.6 seed-0 standing
  falsifier (Gate 1C target).
- **O3** general multi-actor allocation; request-inflation incentives.
- **O4** joint quote-conservativity + P1C preservation/dissipation theorem.
- **O5** robust quoting under measurement margins (`z_rob`).
- **O6** accounting epochs for re-certification without arbitrage.
- **O7** social design of the actor economy (§19.5 register).
- **O8** overexecution settlement semantics beyond the minimum envelope.
- **O9** partially represented dissipation channels in `C_a`.
- Plus all inherited V2.9 open problems (joint constrained theorem,
  viability kernel `K∞`, C-2, attribution, verified-restoration predicate,
  scalarisation weights).
