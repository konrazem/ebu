# E1a v4 — PRE-IMPLEMENTATION CLOSURE REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**Pre-implementation closure PASSED.** Both issues raised by the reviewer are closed:
the finite-bath heat-capacity inconsistency, and handoff-report provenance. The unpushed
parent commit was audited and is safe to publish. **No E1a decision rule changed.**

Implementation is still not started and is not authorised by this task.

---

## Parent-commit audit

Disposition of `8c4810383b4995c50f47dbc06c902a307f0fdd72`: **SAFE AND INTENDED to publish
as an ancestor of `c16eb6bf`.**

```
$ git show --no-ext-diff --stat 8c481038
 docs/e1a/E1A_V4_REPORT.md | 2975 +++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 2975 insertions(+)

$ git show --no-ext-diff --format= --name-status 8c481038
A	docs/e1a/E1A_V4_REPORT.md
```

1. **What produced it.** The E1a v4 review-gap task that assembled the correction packet,
   its addendum, the deterministic checking scripts and the command transcripts into one
   self-contained report, committed at the author's explicit instruction to commit findings.
2. **Files changed.** Exactly one, added: `docs/e1a/E1A_V4_REPORT.md`. Change kinds present
   in the diff: `A` only. No modification, rename or deletion of anything pre-existing.
3. **Scientific semantics.** **No change.** It records analysis; it defines no rule, asserts
   no authority, and supersedes nothing. It is self-described as a task artifact.
4. **Foundation or baseline authority.** **Untouched.** The commit contains no path under
   `docs/physical_foundation/` or `docs/theory/`, no source code, no results, no books, no
   configuration.
5. **Already-reviewed content.** Yes. Its contents are the packet and addendum the reviewer
   received, plus transcripts of the deterministic checks. The blob is identical in the
   commit, at `HEAD`, on disk (`b807f78cafcf7ac91dd037b29973a90509c783a6`) and to the
   external reviewer bundle copy.
6. **Safe to publish.** Yes. It is additive, documentation-only, and later authority depends
   on it: the design document and contract cite it by commit as provenance and as the target
   of two supersession notices, so removing or rewriting it would break those references.

No unexpected or unrelated work was found. Nothing was rewritten or removed. Not pushed.

---

## Thermodynamic correction

The derivation takes both `dS_res/dE` and `d2S_res/dE2` **at constant volume**, so the
remainder is governed by `C_V`. The illustration used `c_P`. That was internally
inconsistent, and is corrected by making the authoritative result symbolic:

```
Delta S_constr = k_B E_theta + O( U^2 / (T^2 C_V) )

epsilon_bath   ~  U / (2 T C_V)
```

**Ensemble and boundary assumptions, now stated explicitly:** microcanonical composite of
bead plus a single thermal reservoir at fixed total energy; the bead **held at `x`** so its
configurational entropy at fixed `x` is an `x`-independent constant and cancels in the
difference; reservoir temperature **defined** by `dS_res/dE|_V = 1/T`; second derivative
`d2S_res/dE2|_V = -1/(T^2 C_V)`; large-reservoir regime `C_V >> U/T`. **Both derivatives are
constant-volume quantities, so substituting `C_P` is not licensed by the derivation.**

**Option A was taken.** No numerical heat-capacity value remains in the design document, the
contract or the baseline, and no decision rule depends on one. The order-of-magnitude
illustration moved to `docs/e1a/finite_bath_remainder.py`, relabelled **NON-NORMATIVE**,
where `C_V` is **derived rather than substituted** via the exact relation
`c_P - c_V = T v alpha^2 / kappa_T` with sourced `alpha = 2.57e-4 K^-1` and
`kappa_T = 4.525e-10 Pa^-1` (CRC Handbook 97th ed.; `kappa_T` after Kell 1975). The
`c_P`/`c_V` gap is quantified at **1.055%**, of an already `~1e-20` quantity. The conclusion
is unchanged in substance across all three passes: `3 N k_B` gave `2.491e-20`, `c_P` gave
`8.2791e-21`, corrected `C_V` gives `8.3665e-21`.

**The finite-bath example remains not a statistical endpoint.** The statistical E1a design is
unchanged.

---

## Authority integrity

**Did any E1a decision rule change?**

```
NO
```

29 of 29 decision rules verified byte-identical against `c16eb6b`: P2 margin, coverage
factor, comparison count, multiplicity treatment and rule; P3 margin, coverage factor, scope
and rule; P1 `alpha_geom`, `alpha_1`, `alpha_2`, procedure and gate list; P4 classification
and mandatory status; `theta_cap` and the merge rule; pipeline target; reported bound; every
budget term; forbidden and authorised Branch-A routes; `rank_tol`; refusal statuses; the four
fields; the uncertainty scenario; forbidden mechanisms; authorization boundaries.

Changed fields were exactly: the finite-bath block, the three rebound hashes, the contract
version (`1.0.0` → `1.0.1`), and one supersession notice.

Entropy wording verified intact in both active documents — `Delta s_med = +k_B E`,
`Delta s_sys = -k_B E`, `Delta s_tot = 0` under the declared static-equilibrium conditions,
with the constrained-macrostate quantity kept distinct, `Delta S_total` absent from both, and
no generalisation to driven fields, imposed actor actions, nonequilibrium initial conditions
or omitted work inputs. **The frozen physical foundation is unmodified.**

---

## Validation

All checks deterministic: parsing, hashing, arithmetic, string comparison. Both scripts were
scanned for RNG, trajectory and runner tokens before execution; neither contains any.

```
$ python3 docs/e1a/validate_e1a_v4_contract.py
1. FROZEN FOUNDATION UNCHANGED
  [PASS] foundation sha256 equals the frozen value  -- 6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507

2. CONTRACT HASH BINDINGS RESOLVE
  [PASS] contract -> foundation hash matches file
  [PASS] contract -> baseline hash matches file
  [PASS] contract -> design hash matches file
  [PASS] contract -> design byte count matches
  [PASS] baseline meta sha256 matches baseline
  [PASS] baseline meta byte_count matches
  [PASS] baseline meta records the v4 design hash

3. EVERY ADOPTED NUMERICAL CONSTANT PRESENT IN BOTH MARKDOWN AND CONTRACT
  [PASS] delta_cross: contract == 0.02  -- contract=0.02
  [PASS] delta_cross: present in design markdown  -- delta_cross = 2%
  [PASS] z_cross: contract == 1.959963985  -- contract=1.959963985
  [PASS] z_cross: present in design markdown  -- 1.959963985
  [PASS] delta_abs: contract == 0.05  -- contract=0.05
  [PASS] delta_abs: present in design markdown  -- delta_abs = 0.05
  [PASS] z_abs: contract == 1.959963985  -- contract=1.959963985
  [PASS] z_abs: present in design markdown  -- z_abs = 1.959963985
  [PASS] alpha_geom: contract == 0.005  -- contract=0.005
  [PASS] alpha_geom: present in design markdown  -- alpha_geom = alpha_1 + alpha_2 = 0.005
  [PASS] alpha_1: contract == 0.004  -- contract=0.004
  [PASS] alpha_1: present in design markdown  -- alpha_1 = 0.004
  [PASS] alpha_2: contract == 0.001  -- contract=0.001
  [PASS] alpha_2: present in design markdown  -- alpha_2 = 0.001
  [PASS] theta_cap_deg: contract == 5.0  -- contract=5.0
  [PASS] theta_cap_deg: present in design markdown  -- theta_cap = 5 degrees
  [PASS] pipeline target: contract == 0.9  -- contract=0.9
  [PASS] pipeline target: present in design markdown  -- >= 90%
  [PASS] reported bound: contract == 0.9055  -- contract=0.9055
  [PASS] reported bound: present in design markdown  -- 0.9055
  [PASS] rank_tol: contract == 1e-12  -- contract=1e-12
  [PASS] rank_tol: present in design markdown  -- rank_tol = 1e-12
  [PASS] sigma_k: contract == 0.0034  -- contract=0.0034
  [PASS] sigma_k: present in design markdown  -- 0.34%
  [PASS] sigma_cm: contract == 0.0115  -- contract=0.0115
  [PASS] sigma_cm: present in design markdown  -- 1.15%
  [PASS] T_total_s: contract == 240.0  -- contract=240.0
  [PASS] T_total_s: present in design markdown  -- 240 s

4. BUDGET ARITHMETIC IS INTERNALLY CONSISTENT
  [PASS] 1 - sum(budget terms) == raw_union_expression  -- 1-0.09453903 = 0.90546097
  [PASS] reported_lower_bound == round(max(0, raw), 4)
  [PASS] 4 x alpha_geom term matches alpha_geom
  [PASS] alpha_1 + alpha_2 == alpha_geom
  [PASS] raw union expression exceeds the 0.90 target

5. THE SUPERSEDED FIXED-B0 RULE HAS NOT RETURNED
  [PASS] contract lists fixed-B0 as forbidden
  [PASS] design markdown marks fixed-B0 forbidden
  [PASS] no authorised occurrence of V = Delta U / B0

6. NO POWER-SPECTRUM / CORNER-FREQUENCY BRANCH-A CALIBRATION IS AUTHORISED
  [PASS] power-spectrum route listed forbidden
  [PASS] corner-frequency route listed forbidden
  [PASS] equipartition route listed forbidden
  [PASS] corner-frequency NOT in the authorised list
  [PASS] power-spectrum NOT in the authorised list
  [PASS] authorised list is exactly the two mechanical/thermometry routes  -- ['force_displacement_with_stokes_drag', 'independent_calibrated_thermometry']
  [PASS] design markdown marks corner-frequency FORBIDDEN for E1a
  [PASS] design markdown carries the supersession notice

7. NO TOTAL-ENTROPY-PRODUCTION OVERCLAIM IN ACTIVE BASELINE E1a TEXT
  [PASS] 'Delta S_total' absent from the baseline
  [PASS] 'total entropy increase' absent from the baseline
  [PASS] baseline states Delta s_tot = 0
  [PASS] baseline states Delta s_med = + k_B E_theta
  [PASS] baseline states Delta s_sys = - k_B E_theta
  [PASS] baseline carries the explicit prohibition
  [PASS] baseline keeps the four objects distinct
  [PASS] contract prohibition present
  [PASS] contract lists the four distinct objects

8. P4 CLASSIFIED AS A DETERMINISTIC CHECK, STILL MANDATORY
  [PASS] P4 mandatory
  [PASS] P4 classified deterministic
  [PASS] P4 does not read Branch-B data
  [PASS] P4 contributes zero stochastic failure probability
  [PASS] P4 budget term is zero
  [PASS] design markdown carries the same classification

9. THE 0.9055 QUALIFICATIONS ARE RECORDED, NOT OMITTED
  [PASS] not claimed as demonstrated empirical power
  [PASS] not claimed as an unconditional lower bound
  [PASS] union inequality labelled an exact theorem
  [PASS] all four standing qualifications present
  [PASS] required interpretation says validation remains mandatory
  [PASS] design markdown carries the required interpretation verbatim
  [PASS] scenario labelled sufficient, not necessary

10. FINITE-BATH RESULT IS SYMBOLIC IN C_V AND NON-NORMATIVE NUMERICALLY
  [PASS] authoritative form is SYMBOLIC ONLY
  [PASS] no numerical value in the design
  [PASS] no decision rule depends on it
  [PASS] not a statistical endpoint
  [PASS] heat capacity is C_V, constant volume
  [PASS] C_P substitution explicitly not licensed
  [PASS] ensemble and boundary assumptions recorded
  [PASS] non-normative illustration declared
  [PASS] that note exists on disk
  [PASS] the note declares itself NOT NORMATIVE
  [PASS] the note derives C_V rather than substituting C_P
  [PASS] the note quantifies the C_P/C_V gap
  [PASS] design markdown states the symbolic result
  [PASS] design markdown says C_P is not licensed
  [PASS] design markdown carries the correction notice
  [PASS] no numeric heat-capacity/remainder value '3.019634e20' in the design markdown
  [PASS] no numeric heat-capacity/remainder value '3.019634e20' in the baseline
  [PASS] no numeric heat-capacity/remainder value '8.2791e-21' in the design markdown
  [PASS] no numeric heat-capacity/remainder value '8.2791e-21' in the baseline
  [PASS] no numeric heat-capacity/remainder value '4.1816' in the design markdown
  [PASS] no numeric heat-capacity/remainder value '4.1816' in the baseline
  [PASS] no numeric heat-capacity/remainder value '2.988113e+20' in the design markdown
  [PASS] no numeric heat-capacity/remainder value '2.988113e+20' in the baseline
  [PASS] no numeric heat-capacity/remainder value '8.3665e-21' in the design markdown
  [PASS] no numeric heat-capacity/remainder value '8.3665e-21' in the baseline
  [PASS] baseline states the symbolic form
  [PASS] baseline forbids the C_P substitution

10b. HANDOFF-REPORT PROVENANCE POLICY IS DOCUMENTED
  [PASS] adoption report is tracked on disk
  [PASS] report carries a provenance section
  [PASS] report states it was generated after the clean-status check
  [PASS] report does not claim its own commit SHA
  [PASS] two-commit convention documented

11. AUTHORIZATION BOUNDARIES ARE CLOSED
  [PASS] analytical design ADOPTED
  [PASS] implementation NOT STARTED
  [PASS] synthetic validation NOT STARTED
  [PASS] preregistration NOT AUTHORISED
  [PASS] physical execution NOT AUTHORISED
  [PASS] baseline status reflects adoption, not validation
  [PASS] baseline no longer claims 'no new design decision is required'

============================================================================
  113 / 113 checks passed
============================================================================
```

```
$ python3 docs/e1a/finite_bath_remainder.py
A. AUTHORITATIVE SYMBOLIC RESULT
     Delta S_constr = k_B E_theta + O( U^2 / (T^2 C_V) )
     epsilon_bath   ~  U / (2 T C_V)          C_V at CONSTANT VOLUME, by construction
   No numerical heat-capacity value is required by the E1a design.

B. ONE CONCRETE RESERVOIR - C_V DERIVED, NOT SUBSTITUTED
   volume                1 mm^3 = 1 uL = 1.000e-09 m^3   (identical volumes)
   rho                         = 997.0 kg m^-3
   c_P                         = 4.1816 J g^-1 K^-1
   alpha                       = 2.570e-04 K^-1
   kappa_T                     = 4.5250e-10 Pa^-1
   c_P - c_V = T v alpha^2/kappa_T = 0.043650 J g^-1 K^-1
   c_V                         = 4.137950 J g^-1 K^-1
   c_P / c_V                   = 1.010549   ->  c_P exceeds c_V by 1.055 %
   mass of 1 uL                = 0.000997 g
   C_V                         = 4.125536e-03 J/K
   C_V / k_B                   = 2.988113e+20
   epsilon_bath at U = 5 k_B T  = E/(2 C_V/k_B) = 8.3665e-21

   SIZE OF THE APPROXIMATION IF C_P WERE USED INSTEAD (it is NOT used):
     C_P/k_B = 3.019634e+20   ->  epsilon = 8.2791e-21
     relative difference = 1.055 %  of an already ~1e-20 quantity.
     Adequate for an order-of-magnitude illustration, but the derivation calls for
     C_V, so C_V is what is reported. The gap is stated, not assumed away.

   SUPERSEDED VALUES, for the record:
     3 N k_B estimate   C/k_B = 1.004e20,  epsilon = 2.491e-20   (unjustified for a liquid)
     c_P-based pass     C/k_B = 3.0196e+20,  epsilon = 8.2791e-21   (inconsistent with the derivation)
     CORRECTED (C_V)    C/k_B = 2.9881e+20,  epsilon = 8.3665e-21

   CONCLUSION, unchanged in substance across all three: epsilon_bath is ~1e-20 for any
   macroscopic reservoir, so Delta S_constr = k_B E holds to first order in U/(T C_V).
   The correction changes the number, not the conclusion. NOT a statistical endpoint.
```

```
$ git diff --check
[clean]
```

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **4 commits behind local; not pushed** |
| starting local HEAD | `fea828e19c6deab17995974ab45baabb3c0198b9` |
| audited unpushed parent | `8c4810383b4995c50f47dbc06c902a307f0fdd72` |
| design-adoption commit | `c16eb6bf6973c75509cbcbadb33a6c558435ce34` |
| **new closure commit** | `f8a13fde3a9559a01123b0adb484e8bddf040b80` |
| **tree SHA** | `a59ca197138bccb6de4e4b49a2acdbbae9083fc9` |
| parent SHA | `fea828e19c6deab17995974ab45baabb3c0198b9` |
| frozen foundation sha256 | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |
| working baseline sha256 | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| design document sha256 | `f20bc885bf400ce3429120e4a0e42915ba2fb15249d88914fd7e55eb1b373f68` |
| contract sha256 | `89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c` |

Committed files:

```
M	docs/e1a/E1A_V4_ADOPTION_REPORT.md
M	docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md
M	docs/e1a/e1a_v4_design_contract.json
M	docs/e1a/finite_bath_remainder.py
M	docs/e1a/validate_e1a_v4_contract.py
M	docs/theory/EBU_THEORY_BASELINE.md
M	docs/theory/EBU_THEORY_BASELINE.meta.json
```

Working tree **clean**. `c16eb6b` was not amended. `8c48103` was not rewritten. History is a
linear chain `c0099d8 → 8c48103 → c16eb6b → fea828e → f8a13fd`. **Not pushed.**

---

## Report provenance

This report was **generated after** the closure commit `f8a13fd` and is committed separately,
following the convention documented in `docs/e1a/E1A_V4_ADOPTION_REPORT.md`:

```
scientific / design work  ->  work commit
handoff report            ->  generated after the work commit, then its own report commit
```

No SHA in this document was asserted before it existed.

---

## Execution boundary

**No stochastic work occurred.** No random draws, no OU trajectories, no stochastic
calibration, no synthetic validation campaign, no model stepping, no simulation runner, no
real data, no physical apparatus work. No preregistration. No E1b. No Stage B. Work was
limited to inspection, deterministic parsing, arithmetic, hashing and schema checks.

---

## Next possible stage

```
E1a v4 bounded implementation
READY FOR AUTHORISATION
NOT STARTED
```

It requires separate authorisation and has not begun. The synthetic validation campaign of
design §15 follows implementation as a further, separate authorisation. Preregistration and
physical execution remain unauthorised.

---

```
PRE-IMPLEMENTATION CLOSURE COMMITTED
```
