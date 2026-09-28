# E1a v4 — PRE-EXECUTION REPAIR REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**All three independent-audit findings were reproduced, and all three are repaired.**

| | finding | reproduced? | repaired? |
|---|---|---|---|
| **B1** | calibration identity incomplete — a `theta0_circular` artifact was accepted for `theta1_power`, and the stored `field_id` was never compared | **yes** | **yes** |
| **B2** | Block-1 threshold was `O(R_cal^2)` and was rebuilt on every P1 evaluation | **yes** | **yes** |
| **B3** | seed-family enforcement was a symmetry check on the caller's own arguments, not a case-level permission | **yes** | **yes** |

The auditor was correct on every point. Each was reproduced deterministically **before**
any code changed.

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
execution_authorised = false   RANDOM DRAWS 0   TRAJECTORIES 0
```

Two things were found during the repair that the audit did not name, both recorded below
rather than quietly fixed: **G1 depends on eigenvector orientation** (a further gap in the
superseded signature), and **the trace normalisation is scale-invariant in exact arithmetic
but not bit-exact** (so the new digest is fail-closed about scale by one ulp).

One question is **open and deliberately not decided here**: whether the campaign calibrates
one artifact per field or one per replicate at that replicate's measured `H_A`. That is a
specification decision. This repair makes either choice mechanically safe and affordable.

---

## B1 — calibration identity

### The original defect

`require_calibration` verified two things: the procedure identity, and a `branch_a_signature`
built from `H_A`'s **eigenvalue ratios** and `n`:

```python
ratios = ",".join(f"{v / base:.12e}" for v in lam)
return hashlib.sha256(f"E1A-V4-GEOM|{ratios}|n={n}".encode("utf-8")).hexdigest()
```

That is not the null law. The Block-1 surrogate draws `S` with per-element variance
`Sigma_aa Sigma_bb (1 + [a==b]) / N_ab`, and `N_ab` depends on the temporal correlation
`phi_r = exp(-dt/tau_r)`. Nothing in the signature saw it. The artifact's `field_id` was
stored and never compared.

### Minimal deterministic reproduction

No RNG. `theta0_circular` and `theta1_power` are both **isotropic**, so their eigenvalue
ratios are identical — while `tau_r = gamma/k_r` differs by `2.1x` because the stiffnesses
are `100` and `210 uN/m`:

| | `theta0_circular` | `theta1_power` |
|---|---|---|
| `k` (uN/m) | 100, 100 | 210, 210 |
| `tau` (s) | `1.6776e-04` | `7.9886e-05` |
| `phi` | `0.4890439` | `0.2226539` |
| `N_11` | `1,227,983` | `1,811,067` |
| geometry signature | `d806758364fe1d5f…` | `d806758364fe1d5f…` — **same** |

**Effective sizes differ by `1.4748x`, and the superseded check could not see it.**

```
>> theta0 artifact ACCEPTED for theta1_power   [DEFECT REPRODUCED]
>> artifact.field_id = 'theta0_circular', requested field_id = 'theta1_power'
   -> field_id never compared
```

### Complete null-law dependency table

Traced from `generate_block1_artifact` and `surrogate_covariance_draw`, not assumed.

| quantity | used by | changes null law? | previously bound? | repair |
|---|---|:--:|:--:|---|
| `field_id` | provenance | no | **no** | **bound** as provenance and fail-safe isolation |
| `H_A` eigenvalue ratios | `sig_modal`, all four gates | **yes** | yes | bound via `H_normalised` |
| `H_A` eigenvector orientation | **G1** (laboratory-frame elements) | **yes** | **no** | bound via `H_normalised` |
| `H_A` overall scale | cancels in every gate | no | — | not bound as such; see note |
| `n` | `N_ab`, every per-element variance | **yes** | yes | bound |
| `dt` | `phi_r = exp(-dt/tau_r)` | **yes** | **no** | **bound** (primitive) |
| `tau_r` | `phi_r` | **yes** | **no** | **bound** (primitive) |
| `phi_r` | `N_ab` | **yes** | **no** | **bound** (sufficient reduction) |
| `N_ab` | per-element variance | yes | no | **not bound** — exactly determined by `(phi, n)`; binding the primitives is strictly stronger |
| mode/block resolvability | **G3** per block | **yes** | **no** | **bound** as a derived cross-check |
| `theta_cap_deg` | resolvability blocks | **yes** | **no** | **bound** |
| `alpha_1` | stored critical `p_min` | **yes** | yes | bound |
| `replicates` | resolution of the empirical null | **yes** | **no** | **bound** |
| gate set | what `p_min` minimises over | **yes** | **no** | **bound** |
| calibrator identity | which generator produced the draws | **yes** | no | **bound** |
| analysis procedure identity | authority | — | yes | bound |
| contract / plan sha256 | authority | — | partly | bound |
| `T_total` | — | no | no | **not bound** — exactly `n * dt` |
| `rank_tol` | never read on this path | no | no | **not bound** |
| `alpha_2` | block 2 only | no | no | **not bound** |
| `delta_cross`, `delta_abs`, `z_*` | P2 and P3 only | no | no | **not bound** |
| `sigma_k`, `sigma_cm`, `sigma_psi`, `sigma_T` | the calibrator never reads them | no | no | **not bound** |

Two entries deserve their own note.

**Orientation, not named by the audit.** G1 is
`max_ij |tn(H)_ij - tn(K)_ij|` — an elementwise comparison in the **laboratory frame**. Under
a common rotation the difference matrix transforms as `D -> R D R^T`, and `max|D_ij|` is not
invariant. Measured with a fixed deterministic supplier:

| rotation | G1 | G2 | G3max | G4 |
|---|---|---|---|---|
| 0° | `5.344146406649e-05` | `1.000281027716` | `7.143566e-03` | `1.516137486705e-04` |
| 30° | `5.350825559106e-05` | `1.000281027716` | `7.143566e-03` | `1.516137486705e-04` |
| 45° | `5.344146406644e-05` | `1.000281027716` | `7.143566e-03` | `1.516137486709e-04` |

G2, G3 and G4 are orientation-invariant; **G1 is not**. Since G1 enters `p_min`, orientation
is a null-law input, and the superseded ratio-only signature was blind to it.

**Scale, and an honest limit.** Every gate is invariant to `H_A -> c H_A`; measured at
`c = 7.3`, G1/G2/G4 agree to `~1e-12` relative. So `H_A / tr(H_A)` is the canonical
representative. But the normalisation is **not bit-exact**: `normalised_H(7.3*H)` differs
from `normalised_H(H)` in the last ulp —

```
base    0x1.36db6db6db6dbp-1      scaled  0x1.36db6db6db6dcp-1
```

— so the digest does **not** identify the two. That is deliberate and recorded rather than
hidden: rounding the canonicalisation to force agreement would make a human-formatted string
the scientific identity, which is forbidden. The residue is fail-closed by one ulp, which is
the conservative direction, and costs nothing because no cross-field reuse is permitted.

### Old versus new signature

| | superseded | repaired |
|---|---|---|
| implementation | `branch_a_signature(H_A, n)` | `CalibrationCondition` |
| binds | eigenvalue ratios, `n` | the 15 fields above |
| blind to | `dt`, `tau`, `phi`, orientation, `theta_cap`, blocks, `R`, gate set, `field_id` | — |
| float encoding | `f"{v:.12e}"`, rounded text | `float.hex()`, exact and round-trippable |
| `field_id` | stored, never compared | validated |

`branch_a_signature` is **retained as provenance only**, and its docstring now says so.

### Artifact schema change

`e1a_v4_block1_calibration/2`. A schema-1 artifact is **refused, not reinterpreted**. No
official stochastic artifact exists, so the break is free to make explicit now — which is
exactly why now is the time to make it.

### Cross-field regression result

```
[PASS] the audited pair really do share a geometry signature
[PASS] yet their temporal laws differ materially  -- N_11 1,227,983 vs 1,811,067 = 1.4748x
[PASS] the repaired binding refuses theta0's artifact for theta1
[PASS] and refuses it even when the field NAME is forced to agree
[PASS] field_id alone is still checked, as fail-safe provenance
```

**Why the repaired artifact cannot be wrongly reused.** The digest covers `dt`, `tau_modes`
and `phi_modes` directly. Two fields with equal eigenvalue ratios but different relaxation
times produce different `phi_modes`, hence different preimages, hence different digests, and
`require_calibration` refuses with the first differing component named. Forcing the names to
agree does not help, because the name is one field among fifteen. Conversely, `field_id` is
checked independently, so a mathematically identical condition under a different field name
is also refused — fail-closed in both directions, as section 5 of the task requires.

---

## B2 — calibration runtime

### Old algorithm and complexity

```python
for i in range(r):                       # R iterations
    for gate in gates:                   # x 4
        p = (1 + sum(1 for j, d in enumerate(draws) if j != i and d >= obs)) / r   # x R
```

`O(R^2)` per artifact — about `10^10` float comparisons at `R_cal = 50000`. Worse,
`critical_p_min()` called `p_min_null()` **unconditionally on every P1 evaluation**, so the
whole quadratic computation was repeated per analysed field per replicate.

### New algorithm and equivalence argument

```
1 + #{j != i : d_j >= d_i}  =  #{j : d_j >= d_i}
```

The excluded term `j = i` contributes exactly `1`, because `d_i >= d_i` always holds. Both
sides are **integer counts**, so this is an identity, not an approximation, and it is
unaffected by ties: a tied value is counted on both sides alike. The right-hand side is one
`bisect_left` on the ascending marginal, so the full null distribution costs `O(R log R)`.

The `>=` convention, the Besag–Clifford `(1 + count)/(R + 1)` p-value and the
`floor(alpha_1 * R) - 1` quantile are all **unchanged**. Only the cost changed.

**Tie handling** is verified on hand-written fixtures rather than argued: all distinct,
two-way tie, multiple ties, all equal, ascending, descending, repeated extrema, `R = 1`,
`R = 2` equal, `R = 2` distinct, small mixed, negatives, and a fixture where the four gates
differ so `p_min` is not a single column. **Exact equality in every case.**

**Non-finite inputs** are **refused as an invalid calibration artifact**, never sorted —
NaN, `+inf` and `-inf`, both as null draws and as an observed statistic.

### Artifact reuse

Finalised **once**, at artifact construction, and stored: the sorted null marginals per
gate, the `p_min` null distribution, and the critical `p_min`. `p1_geometry` reads the
stored threshold.

Reuse is **proved, not asserted**: a counting wrapper around `ge_counts` shows that one P1
evaluation performs exactly **4** lookups — one per gate. A rebuild would cost `4R` more.

### Measured benchmarks

**MEASURED BENCHMARK.** macOS-26.6.1-arm64, CPython 3.14.2, 14 CPUs, pure Python (numpy and
scipy are absent). Deterministic van der Corput arrays; no RNG. Median of 3 repetitions
(2 at `R = 50000` for the superseded form).

| R | superseded `O(R^2)` | repaired finalisation | speedup | exact match |
|---:|---:|---:|---:|:--:|
| 1 000 | `0.1585 s` | `0.0014 s` | 113x | **yes** |
| 10 000 | `17.8104 s` | `0.0179 s` | 995x | **yes** |
| 50 000 | **`415.5725 s`** | **`0.4543 s`** | **915x** | **yes** |

| operation | measured |
|---|---|
| generate + finalise one artifact at `R_cal = 50000` | `3.008 s` wall, `2.792 s` CPU |
| one P1 use of a finalised artifact | `1.94 us` |
| one compatibility check | `22.99 us`, constant in `R` |

### Campaign projection, and its assumptions

**BENCHMARK-BASED PROJECTION** built on the measured per-unit costs. Derived from the
declared case structure, not assumed:

```
C1 300x4 + C2 400x4 + C3 400x4 + C4 2000x4 + C5 400x12x4
  + C6 400x3 + C7 400x4x4 + C8 200x4  =  40,000 field-replicates
```

so **40 000 P1 evaluations**. Reuse is mechanical, proved by the 4-lookup test above.

| architecture | artifact builds | repaired | superseded |
|---|---:|---:|---:|
| four locked per-field artifacts | 4 | **13 s** | ~28 min |
| one artifact per field-replicate | 40 000 | **33.4 core-hours** | **193.6 core-days** |

**PARALLELISM ASSUMPTION** — "2.4 hours at 14-way" assumes 14 workers, perfect scaling, no
I/O and no scheduling overhead.

**NOT MEASURED END-TO-END** — no campaign, calibration or trajectory has been run. Branch-B
trajectory generation is excluded from every figure above and is the larger term under
either architecture.

### Correction to the earlier report

`docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md` is **not rewritten**; a supersession banner
was added to it and its findings are untouched. The corrections:

| earlier wording | correct classification |
|---|---|
| "192 core-days" | **BENCHMARK-BASED PROJECTION** resting on a quadratic extrapolation and an assumed artifact count |
| "13.7 days at 14-way parallelism" | **PROJECTION + PARALLELISM ASSUMPTION** |
| "one artifact costs ~415 s" | was a **PROJECTION**; now **MEASURED** at `415.5725 s` |
| "four locked artifacts cost about 28 minutes" | **PROJECTION** |
| "**infeasible**" | **withdrawn.** No explicit resource ceiling was part of the study. The supported statement is "**very expensive under the previous implementation**" |

The projection was accurate — `415.0 s` projected against `415.5725 s` measured — but it was
reported as though it were a measurement, and that is the error being corrected.

---

## B3 — seed-family enforcement

### What the old function actually enforced

```python
def stream(self, consumer, requested):
    if consumer is not requested:
        raise Refusal(...)
    return self.families[requested.value]
```

It compares **the caller's own two arguments**. Passing the same family twice satisfies it.
There is no `case_id` parameter, so no case could ever be consulted. Reproduced:

```
stream() accepted branch_a_measurement with no case in scope -> 62746336670861162
replicate_seed(C1_true_bridge_complete, rep 0)               -> 7318848234191750116
>> a C1 Branch-A seed is derivable; stream() takes no case_id  [DEFECT REPRODUCED]
```

### What the previous report incorrectly claimed

`docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md` and the surrounding material described family
separation as an enforced architectural boundary — "a consumer declares which family it may
read, and `stream_for` refuses any other". That describes a **specification requirement
honoured by convention**, not a mechanically enforced rule. The distinction matters because
the whole point of the family split is that it cannot be bypassed by a caller. The claim is
corrected here rather than restated.

### Per-case allowed families

Derived from the frozen generator design — `generating_model.branch_a`, `truth_visibility`
and disposition G3 — not invented.

| case | stochastic components | required families | previous declaration | corrected |
|---|---|---|---|---|
| C1 | Branch-B trajectories; Branch-A measurement | `validation`, `branch_a_measurement` | `validation` | **both** |
| C2 | Branch-B; Branch-A | `validation`, `branch_a_measurement` | `validation` | **both** |
| C3 | Branch-B; Branch-A | `validation`, `branch_a_measurement` | `validation` | **both** |
| C4 | calibration surrogate; Branch-B; Branch-A | `calibration`, `validation`, `branch_a_measurement` | `calibration + validation` | **all three** |
| C5 | Branch-B; Branch-A sweep | `validation`, `branch_a_measurement` | `validation + branch_a_measurement` | unchanged |
| C6 | Branch-B at three rho; Branch-A | `validation`, `branch_a_measurement` | `validation` | **both** |
| C7 | Branch-B per alternative; Branch-A | `validation`, `branch_a_measurement` | `validation` | **both** |
| C8 | paired blinded Branch-B; Branch-A | `blinded_scale_control`, `branch_a_measurement` | `blinded_scale_control` | **both** |

`confirmatory` is declared in the seed map and authorised for **no case**.

**C1 specifically.** Disposition G3 asserts the primary `>= 0.90` claim at
`sigma_psi = 0.5 deg`. `sigma_psi` does not appear in `sigma_fs = sqrt(sigma_k^2/m +
(sigma_T/T)^2)`, nor in `delta_cross`, `delta_abs` or any half-width. Its **only** channel is
a realised rotation reaching G3. So C1 must draw Branch-A measurement error, and must draw it
from its own family — otherwise G3's primary, secondary and stress scenarios would be
indistinguishable and the disposition would assert nothing. This is the already-frozen
independence requirement made mechanical, not a new scientific decision.

### New enforcement

`CaseSeedAccess`, reached through `ExecutionBinding.case_access` / `runner.case_seed_access`.
It is built **from the frozen plan**, so authorisation comes from the committed case
declaration rather than from the caller. `family_seed` and `replicate_seed` remain importable
and unchanged: **a derivation is not an authorisation**, and the boundary is where
authorisation is decided.

The official route returns the **identical seed** when the family is authorised — verified —
so the repair changes who may ask, never what the answer is.

### Regression tests

C1 may obtain `validation` and `branch_a_measurement`, and the two streams differ; C1 may not
obtain `calibration`, `blinded_scale_control` or `confirmatory`; C4 and C5 receive exactly
their required families; only C8 reaches `blinded_scale_control`; an unknown case ID refuses;
a bare string is not a declared family; a plan case lacking the key refuses at load; and the
auditor's own demonstration is kept as a test — the low-level API still derives the seed, and
the official case-scoped route refuses it for a case that does not declare the family.

**Seed derivation is not a draw.** It constructs no generator and draws no number. Seed
derivation, RNG construction, random draw and trajectory generation remain separately
reported.

---

## Authority changes

| file | change |
|---|---|
| `e1a_v4/calibration.py` | `CalibrationCondition`, schema `/2`, exact `O(R log R)` threshold, finalise-once, `require_calibration` on the full condition, `p_min_null_reference` retained for tests, non-finite refusal, `float.hex()` canonicalisation |
| `e1a_v4/endpoints.py` | `p1_geometry` takes the condition instead of `(H_A, n, phi_modes, field_id)`; reads the stored threshold |
| `e1a_v4/validation/calibrate.py` | `CalibrationRequest` carries `dt` and `tau_modes`; builds and binds the condition |
| `e1a_v4/validation/seeds.py` | `CaseSeedAccess`, `ALLOWED_FAMILIES_KEY` |
| `e1a_v4/validation/plan.py` | validates `allowed_seed_families` at load; `ExecutionBinding.case_access` |
| `e1a_v4/validation/runner.py` | `case_seed_access`, the official seed route |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | v1.3.0: per-case families, condition binding, threshold algorithm, artifact reuse, runtime correction, repair record |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | normative rendering of all of the above |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md` | supersession banner only; **no finding altered** |
| `docs/e1a/e1a_v4_execution_feasibility_probe.py` | updated to the repaired API; original preserved at `58388d7` |
| `test_e1a_v4.py` | updated for the repaired calibration API |
| `test_e1a_v4_repair.py` | **new** — 125 checks |

**The design contract was NOT changed.** The dependency audit found no missing core-contract
field: every repaired quantity belongs to the validation package, not to the E1a decision
rules.

---

## Identity rebound

Determined by the defined hashing recipes, not forced in either direction.

| item | old | new | outcome |
|---|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | *same* | **UNCHANGED** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | *same* | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | *same* | **UNCHANGED** |
| seed map | `28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87` | *same* | **UNCHANGED** |
| **every seed value** | master `13785910525869478477` | *same* | **UNCHANGED** |
| analysis procedure identity | `af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4` | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | changed |
| validation plan JSON | `c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9` | `6075e7a0015628fd9d05d095aaed0ebbe4924aaa7b64268fc5a5df00b3a8c347` | changed |
| validation plan Markdown | `940c01b78a49301b2cd54a2ccdce1a6b99e279075247b79769314b09120d5cf1` | `1ffc54364716fe4dc5b39f6aba68a42d55141375317e7d2e14bbb0edc726fc6e` | changed |
| execution identity | `88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837` | `4ce4669c0296774e0780e5ddf2668a1cef3f28e8cfafd72ac529f527a62d1550` | changed |
| calibration artifact schema | `e1a_v4_block1_calibration/1` | `e1a_v4_block1_calibration/2` | changed |
| plan version | `1.2.0` | `1.3.0` | changed |

The analysis identity moved because `calibration.py` and `endpoints.py` changed — expected,
and the correct outcome rather than something to suppress. **The contract did not move, and
because the committed seed derivation binds only to the contract identity, every seed value
is bit-identical.** No seed was hand-edited, and no seed was consumed.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Asserted by fixture, not by claim: `delta_cross = 0.02`, `delta_abs = 0.05`,
`z_cross = z_abs = 1.959963985`, `alpha_geom = 0.005`, `alpha_1 = 0.004`, `alpha_2 = 0.001`,
`theta_cap = 5 deg`, `rank_tol = 1e-12`, primary `sigma_psi = 0.5 deg`, complete-pipeline
target `>= 0.90`, all eight replicate counts (300 / 400 / 400 / 2000 / 400 / 400 / 400 / 200),
the G1 and G2 criteria, the G3 disposition, the C2/C3/C4 size semantics, the false-bridge
alternatives, the seed-derivation algorithm, the complete-pass denominator and the final
ten-point conjunction are all unchanged.

---

## Static tests

| suite | passed | failed |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` | **113** | 0 |
| `test_e1a_v4.py` | **122** | 0 |
| `test_e1a_v4_preexec.py` | **93** | 0 |
| `test_e1a_v4_dispositions.py` | **64** | 0 |
| `test_e1a_v4_size_semantics.py` | **78** | 0 |
| `test_e1a_v4_repair.py` | **125** | 0 |
| **total** | **595** | **0** |

`test_e1a_v4.py` rose from 119 to 122 and `test_e1a_v4_repair.py` is new; no check was
removed or weakened.

```
$ python3 -m e1a_v4.validation.runner --preflight-only
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : 6075e7a0015628fd9d05d095aaed0ebbe4924aaa7b64268fc5a5df00b3a8c347
  seed map sha256            : 28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87
  analysis procedure identity: dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
  execution identity         : 4ce4669c0296774e0780e5ddf2668a1cef3f28e8cfafd72ac529f527a62d1550
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)

$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
EXECUTION REFUSED: the frozen validation plan has execution_authorised = false.
The synthetic-validation campaign is a separate authorised stage. No random number
has been drawn.
  RANDOM DRAWS: 0   TRAJECTORIES: 0

$ git diff --check
[clean]
```

---

## Execution state

```
execution_authorised = false

RANDOM DRAWS = 0

TRAJECTORIES = 0

CALIBRATION EXECUTION = NOT RUN

VALIDATION CAMPAIGN = NOT RUN
```

---

## Superseded provenance

The pre-execution package previously described as ready for execution — work commit
`8615405`, report commit `a233811` — is **SUPERSEDED BEFORE EXECUTION**. No stochastic
evidence existed, so nothing scientific is retracted: this is a prospective software and
specification repair.

Preserved in full, none rewritten:

- `docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md` (commit `b4b2575`)
- `docs/e1a/E1A_V4_VALIDATION_DISPOSITION_REPORT.md` (commit `dd52c61`)
- `docs/e1a/E1A_V4_SIZE_VALIDATION_REPORT.md` (commit `a233811`)
- `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md` (commit `80e33a4`) — supersession banner
  added; **no finding altered**
- `docs/e1a/e1a_v4_execution_feasibility_probe.py` — original form preserved at `58388d7`

No previous commit is amended and no history is rewritten.

### Still open, and NOT decided by this repair

Whether the campaign calibrates **one artifact per field** or **one per replicate at that
replicate's measured `H_A`** remains a specification decision, recorded in
`docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md`. Both arms are now mechanically safe — the
condition refuses a mismatched artifact in either direction — and both are affordable: 13 s
and 33.4 core-hours respectively. The repair removes the cost objection that made the choice
look forced. It does not make the choice.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting coordinate | `80e33a4cacaa4426a9738c8ab9b7d2a8468fe5cb` |
| **work commit** | `5727e10b0b946c9e1b3d2401a6544cc1326a23fd` |
| **work tree SHA** | `db575a123a30d084a606b542c3e870f95bf6121a` |
| report commit | *this file's commit* |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — unchanged |

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR INDEPENDENT RE-AUDIT
NOT STARTED
```

Execution is **not** authorised. The re-audit should in particular examine the two findings
this repair added beyond the audit's scope — the G1 orientation dependence and the one-ulp
scale residue — and decide the open calibration-architecture question. Preregistration,
physical execution, E1b and Stage B remain unauthorised and unstarted.

---

```
PRE-EXECUTION VALIDATION REPAIR COMMITTED
```
