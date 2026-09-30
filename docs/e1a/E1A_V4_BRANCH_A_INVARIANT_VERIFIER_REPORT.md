# E1a v4 — Branch-A Record Domain and Intra-Measurement Invariants

**Stage.** Bounded driver / provenance correction. Pre-execution.
**Starting HEAD.** `91e9f5ae258fd3e81166a2644e368b865a96dfd7`
**Work commit.** `630282a821cba30d901df665b43a467de1fdc65c`
**Work tree.** `6c5efc13e2b18b7287cc55f72dee814de0a08b6b`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

---

## 1. Auditor blocker — valid fields individually ≠ valid measurement jointly

The field-authority repair verified each embedded field against its own
authority. That is necessary and **not sufficient**. Every field can be
well-formed and externally authorised, the record can be correctly re-digested
and durably committed, and the *combination* can still be one the production
constructor could never have produced.

Reproduced before editing, on the shared publication verifier:

| forged record | shared verifier | restart |
|---|---|---|
| `H_A` changed, primitives untouched | ACCEPT ← DEFECT | (lock digest tripped) |
| `T_measured = -1` | ACCEPT ← DEFECT | (lock digest tripped) |
| `T_measured = 0` | ACCEPT ← DEFECT | (lock digest tripped) |
| `scale_factor = -1` | ACCEPT ← DEFECT | (lock digest tripped) |
| `scale_factor = 0` | ACCEPT ← DEFECT | (lock digest tripped) |
| asymmetric published `H_A` | ACCEPT ← DEFECT | (lock digest tripped) |
| `branch_a_status` inconsistent with `H_U` | ACCEPT ← DEFECT | (lock digest tripped) |
| `T_measured = NaN` / `+inf` | refused, **UNCODED** | refused, **UNCODED** |
| equal k, unequal tau | already refused | already refused |

### Two corrections to the auditor's framing

Both recorded rather than quietly absorbed.

**The equal-stiffness tau case was already refused** — by the existing
pairing-order rule, not by any gamma relation: doubling one tau made the stored
sequence increase, and the stored order must be non-increasing. So that case did
not demonstrate the gap. The case that genuinely escaped is an **order-preserving
rescale on unequal stiffnesses**: shrinking the larger tau by 20% on
`theta2_ellipse` keeps the sequence non-increasing and still breaks the relation.
That escape was confirmed, and it is now its own permanent regression.

**NaN and +inf did refuse, but uncoded**, from `canonical_float` in the
scientific layer during recovery. Correct fail-closed behaviour, anonymous
diagnosis. Recovery now maps a non-coded production refusal onto the same coded
category.

Also: the "restart accepted" column is more nuanced than the brief implies. For
the publication forgeries, restart refused — but with
`CALIBRATION_LOCK_PROVENANCE_MISMATCH`, because forging the publication moved its
digest away from the lock. That is an incidental catch by a different check, not
the invariant. The shared verifier was the weak point, and it is where the fix
went.

---

## 2. Constructor invariant inventory

Derived by reading `e1a_v4/branch_a.py`, not assumed.

| field / relation | primitive or derived | production rule | read-verification rule |
|---|---|---|---|
| `T_measured` | primitive measured | `__post_init__`: `T <= 0` → Refusal | finite and `> 0`; NaN/inf refuse |
| `scale_factor` | primitive measured | `__post_init__`: `scale_factor <= 0` → Refusal | finite and `> 0`; NaN/inf refuse |
| `k_modes_measured` | primitive measured | no positivity rule (a negative k yields `BRANCH_A_INVALID` status, not a refusal) | finite floats; **not** required positive |
| `rot_deg_measured` | primitive measured | no domain rule | finite float |
| `H_U` symmetry | derived | `__post_init__`: `is_symmetric(H_U)` → Refusal (`tol=1e-12`, production's own) | the production constructor is called; its refusal is re-raised coded |
| `x_star` dimension | primitive | `__post_init__`: length must match `H_U` | supplied as `[0.0]*m` on reconstruction; not persisted |
| `H_A` | **derived** | `H = stiffness_matrix(k, psi) * scale / (k_B T)` | recomputed via the reconstructed field's own `.H`; compared **exactly** |
| `branch_a_status` | **derived** | `BRANCH_A_INVALID` iff `min eig(H_U) <= 0` | recomputed via `.status`; compared exactly |
| `tau_modes` | **derived** | `tau_r = gamma / k_r`, one shared `gamma = 6 pi eta a`, carried with ascending k | exact rational feasibility that **some** gamma yields every recorded tau, plus equal-k ⟹ equal-tau, plus the non-increasing pairing |

`BRANCH_A_MEASUREMENT_INVARIANTS` declares the four joint constraints in code:
`H_A_FROM_PRIMITIVES`, `STATUS_FROM_H_U`, `TAU_SINGLE_GAMMA`, `PRODUCTION_DOMAIN`.

**Coverage, machine-checked:** every field classified `DERIVED` is covered either
by a joint invariant or by a recomputed expectation in the field-authority layer
(`n_samples` takes the second route). Uncovered: **none**.

---

## 3. Domain checks on measured fields

Enforced exactly as production enforces them, and no further. `k_modes_measured`
is deliberately **not** required positive, because production does not require it
— a negative stiffness produces a `BRANCH_A_INVALID` status, which is a
legitimate publishable outcome, not a refusal. Inventing positivity there would
have rejected records the design permits.

On NaN and the infinities: production's rule is "temperature must be positive",
and `NaN <= 0.0` is `False`, so a NaN slips through the production comparison
itself. Requiring a *finite* value is the faithful reading of "positive", not an
additional requirement.

---

## 4. H_A — exact production dependency and recomputation

```text
H_U = stiffness_matrix(k_modes_measured, rot_deg_measured)
H_A = H_U * scale_factor / (K_B * T_measured)
```

All four inputs are persisted, so `H_A` is fully recomputable.

**Method: reuse, not reimplementation.** `reconstructed_branch_a_field` builds a
real `BranchAField` from the persisted primitives and reads its own `.H`. This
gets three things at once — the production domain rules re-applied, the derived
`H_A`, and the derived `status` — with no formula restated in the verifier.

`viscosity` and `bead_radius` are not persisted (the acknowledged-open
field-construction gap) and enter **only** `gamma`, which is never recomputed.
Neutral positive placeholders keep the constructor's own checks meaningful
without inventing a drag coefficient, and nothing derived from them is compared
against anything.

`e1a_v4/branch_a.py` **is** in `SCIENTIFIC_MODULES` and was **not modified**. The
analysis identity does not move for a provenance repair.

---

## 5. Relaxation invariant

The adopted model has one shared drag coefficient per measurement:

```text
tau_r = gamma / k_r        with gamma = 6 pi eta a
```

so `tau_r * k_r = gamma` for every mode of one measurement.

**Absolute gamma stays unresolved and is not needed.** It is not persisted, and
its inputs are the open field-construction gap. The verifier therefore tests only
that **some** gamma exists — never which one. No gamma is chosen, estimated or
frozen.

**Mode ordering was handled explicitly**, since it has been a defect source
before. `from_branch_a_field` stores `tau` carried with **ascending** k
(`sorted(zip(k_modes, tau_modes))`), while `k_modes_measured` is stored in
**source** order — for `theta2_ellipse` that is `[1.5e-4, 6.0e-5]`, descending.
The verifier sorts k ascending before pairing, matching production exactly.

---

## 6. Numeric comparison — no tolerance was introduced

| quantity | how finite precision is handled |
|---|---|
| `H_A` | recomputed through production code and compared **exactly**. Sound because every persisted float is an exact `float.hex()` and the operation order is production's. |
| `branch_a_status` | recomputed, exact string comparison. |
| `n_samples`, `dt`, identities, seeds | exact equality against authority (unchanged). |
| `H_U` symmetry | production's own pre-existing `is_symmetric(tol=1e-12)`, applied by calling the constructor. **Not a new bound.** |
| `tau_modes` | **exact rational feasibility.** No epsilon. |

### The tau test, and why exact product equality would have been wrong

`gamma` cannot be recomputed, so §19's preferred route is unavailable, and the
repository has no general numeric-equivalence policy to inherit. Rather than
invent an epsilon — explicitly forbidden — the check is formulated so that **no
tolerance is needed at all**:

For each mode, round-to-nearest maps a contiguous real interval to the stored
`tau_r`; its endpoints are the midpoints to the adjacent floats. Computed in
`fractions.Fraction`, those bounds are **exact**. Each mode therefore constrains
gamma to `[lo_r * k_r, hi_r * k_r]`, and a valid record is one whose intervals
intersect. This is the exact statement of the production relation, not an
approximation of it. Closed endpoints make the test conservative at a tie: it can
only ever accept marginally more, never reject a genuine value. The degenerate
case that closure would let through — equal k, adjacent taus — is closed
separately by the exact rule **equal stiffnesses ⟹ equal relaxation times**,
which follows because one gamma divided by one k gives one float.

**A naive product-equality check would have rejected real measurements.** Measured
over genuine fixtures rather than assumed: for unequal stiffnesses the products
`tau_r * k_r` are not bit-identical, and the suite asserts that at least one
genuine fixture exhibits it. That is precisely why the interval formulation is
required.

Because no tolerance exists, there is no bound to justify a posteriori and
nothing was tuned after observing fixture failures.

---

## 7. Positive controls

Four **complete, internally consistent, non-nominal** measurements — differing
temperature, stiffness, orientation, scale and gamma — all ACCEPT:

```text
warmer, softer, rotated, scaled       k=(8.7e-5, 1.93e-4)  17.5 deg  301.44 K  1.0037
cooler, stiffer, unrotated            k=(2.4e-4, 2.4e-4)    0.0 deg  288.13 K  0.9912
strongly elliptic, large rotation     k=(5.1e-5, 3.3e-4)   42.7 deg  318.66 K  1.0500
very small drag, unequal stiffness    k=(1.1e-4, 7.9e-5)    5.0 deg  297.00 K  1.0000
```

None is the nominal contract state, and each uses an arbitrary positive fixture
gamma that is never treated as authority. Every contract field's real production
publication also verifies, and terminal validation accepts it.

**One previously passing assertion changed, and is more correct.** A measured
temperature changed *alone* now refuses, because `H_A` is derived from it. The
"observations may vary" control accordingly requires a complete consistent
measurement — which is what the four fixtures above provide.

---

## 8. Negative mutation audit

Every forgery below is durably committed with the evidence digest, envelope
digest, calibration lock and terminal record all consistently recomputed.

```text
derived-field audit          3 DERIVED fields changed alone, primitives fixed
                             0 unexpected passes
domain audit                10 invalid-domain values across T_measured,
                             scale_factor and rot_deg_measured
                             0 unexpected passes
joint-relation audit         H_A inconsistency, equal-k unequal-tau,
                             order-preserving product break, shuffled pairing,
                             asymmetric H_A, inconsistent status
                             0 unexpected passes
```

All refuse with `BRANCH_A_MEASUREMENT_INVALID` on the shared verifier **and** on
restart. No downstream re-digesting launders an invalid measurement.

---

## 9. Previous external-authority checks

Re-asserted in the new group so they cannot silently regress:

```text
embedded package identities (contract, plan, analysis, schema)  still refuse
Branch-A seed                                                   still refuses
common-mode seed                                                still refuses
dt                                                              still refuses
n_samples                                                       still refuses
calibration route                                               still refuses
planned-job restart requirement                                 still enforced
persisted calibration-lock verification                         still enforced
```

---

## 10. Refusal code

One added: `BRANCH_A_MEASUREMENT_INVALID`, as a **subclass** of
`BranchAProvenanceMismatch`, so every existing handler still catches it while the
diagnosis stays distinguishable — "wrong authority value" and "impossible
measurement" are different faults. 63 codes total.

---

## 11. Execution identity

Computed after the work commit, from a clean `git archive` of
`630282a821cba30d901df665b43a467de1fdc65c`, run twice, identical:

```text
DRIVER-PRESENT / UNSEALED execution identity
ad870b15352fb9a7e08c5b29106b9bfb03bd84889327786fcfd0e550139c10d8
```

Moved from the pre-repair `6887239f4afc5c8bae3c8fcb67810a8107e054f0384c119e8d29b8c819e77575`,
as expected. **NOT FINAL. NOT FROZEN. NOT AN AUTHORISATION.**

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |

---

## 12. Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

No `SCIENTIFIC_MODULES` entry modified — intersection with the work commit's
changed paths: **NONE**, `branch_a.py` included. No frozen authority file touched
— **NONE**. Campaign structure unchanged: **53,200 jobs**, **46,000 calibration
artifacts**.

Changed files, all three:

```text
e1a_v4/validation/campaign_driver.py   the invariant inventory, the production
                                       reconstruction, the exact tau feasibility
e1a_v4/validation/refusals.py          one new code (63 total)
test_e1a_v4_terminal_calibration.py    group F1; one E1 assertion corrected
```

---

## 13. Tests

Pure/static only, each run under an instrumented `ou_observations`.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 376 | 376 | 0 | no (measured 0) |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no (measured 0) |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no (measured 0) |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | no (measured 0) |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | no (measured 0) |
| `test_e1a_v4.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | no (measured 0) |
| **total** | **1,206** | **1,206** | **0** | **0 trajectories** |

The terminal-calibration suite grew from 14 groups / 316 checks to **15 groups /
376 checks**, the new group being `F1`.

### Deferred trajectory suite

`test_e1a_v4_campaign_driver.py` was **not run and not modified**. Verified
statically: it byte-compiles, and all 18 call sites of the changed functions bind
against current signatures. **Runtime status unverified and not claimed — KNOWN
DEFERRED TEST.**

---

## 14. Open issues — listed, not resolved

```text
generator identity authority          open (classified OPEN_UNRESOLVED)
C3/C4 field-to-replicate reduction    open, still fails closed
PRNG authority                        open
field construction authority          open (gamma: eta, a) -- which is why the
                                      relaxation check is scale-free in gamma
C6 implementation inputs              open
remaining C8 implementation inputs    open
diagnostic aggregator authority       open
```

**Next stage, NOT begun and NOT authorised.** An independent re-audit. The seal
stays `PRE_DRIVER`, `execution_authorised` stays false.

---

## 15. Safety

```text
REAL RNG OBJECTS = 0
REAL RANDOM DRAWS = 0
DETERMINISTIC TEST TRAJECTORIES = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
CALIBRATION EXECUTIONS = 0
OFFICIAL CAMPAIGN JOBS = 0
```

No results directory exists. The seal reports `state: PRE_DRIVER`,
`expected_execution_identity: null`, `execution_authorised: false`,
`random_draws: 0`, `trajectories: 0`.

---

BRANCH-A INVARIANT VERIFIER REPAIR COMMITTED
