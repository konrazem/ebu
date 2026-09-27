# E1a v4 — DESIGN ADOPTION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

The corrected E1a v4 statistical design is now **authoritative repository record**.
Future implementation no longer depends on conversational decisions or scratchpad
artifacts.

Adopted **prospectively** — adoption is not evidence that the rules perform as intended:

- central endpoint `K_theta = beta H_theta`, one field-independent beta across the four
  declared fields, with the thermal normalisation and the benchmark-specific prediction
  `beta = 1` at every tested field preserved unchanged;
- **P2** cross-field commensurability at `delta_cross = 2%`, `z_cross = 1.959963985`,
  **no Bonferroni**, recorded explicitly as an **intersection–union equivalence test**,
  per-comparison and conjunctive across the three comparisons against the common
  reference field;
- **P3** absolute calibration **mandatory** at `delta_abs = 5%`, `z_abs = 1.959963985`,
  applied to **every tested field**, fail-closed on any non-`ESTIMATED` field;
- **P1** geometry gate at `alpha_geom = 0.5%`, split `alpha_1 = 0.4%` / `alpha_2 = 0.1%`
  across a **union-valid two-block** procedure with **no independence asserted** between
  blocks;
- **P4** reclassified as a deterministic consistency check, still mandatory;
- mode-resolution `theta_cap = 5°`;
- complete-pipeline target **≥ 90%** true-bridge success for the declared scenario, with
  false-bridge controls defined separately.

**Implementation is not started. Synthetic validation is not started. Preregistration is
not authorised. No physical execution.**

---

## Authority changes

| file | change | why |
|---|---|---|
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | **new**, 26,650 B | authoritative prospective design; all 18 required sections |
| `docs/e1a/e1a_v4_design_contract.json` | **new**, 15,290 B | machine-readable decision rules so implementation never scrapes constants from prose; hash-bound to the foundation, the baseline and the design document |
| `docs/e1a/validate_e1a_v4_contract.py` | **new** | deterministic conformance validation of everything above |
| `docs/e1a/finite_bath_remainder.py` | **new** | corrected finite-reservoir remainder calculation |
| `docs/theory/EBU_THEORY_BASELINE.md` | **modified** | entropy correction (§4, §14.3); status correction (§14.5, status table, §24) |
| `docs/theory/EBU_THEORY_BASELINE.meta.json` | **modified** | new hash and byte count; status; next gate; three retracted claims; two evidence reports; v4 design binding |

`docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` is **not modified**.

The Markdown/JSON pair is normative together: the JSON is the mechanical schema and
ordering source, the Markdown its normative human rendering. Any mismatch is an integrity
failure requiring fail-closed refusal, not a licence to choose one selectively.

---

## Scientific corrections

**Entropy.** The baseline stated `Delta S_total = k_B E_theta` and "+5 k_B of total
entropy increase". Under the declared static-equilibrium conditions — conservative
overdamped dynamics, fixed field, fixed temperature, a single reservoir, the stationary
equilibrium distribution at both times, and no omitted work input — the correct
bookkeeping is

```
Delta s_med = + k_B E_theta      entropy delivered to the thermal reservoir
Delta s_sys = - k_B E_theta      stochastic system entropy
Delta s_tot = 0                  TOTAL stochastic entropy production
```

These are **trajectory identities**, distinct from the ensemble-average
entropy-production rate. A separately derived **constrained-macrostate** reading also
yields `k_B E`, with remainder ratio `U/(2 T C)`. **Medium entropy, stochastic system
entropy, total entropy production and the constrained-macrostate deficit are four
different objects and are never equated.** No generalisation is claimed to imposed actor
actions, driven transitions or nonequilibrium initial distributions. Core EBU equations
are unchanged.

**P4 classification.** `DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK`. It
evaluates a closed-form identity on declared constants, never reads Branch-B data,
remains **mandatory**, and contributes **no stochastic failure probability** once passed.
Its algebraic pass is **not** experimental evidence.

**Units.** The superseded scratch calculation treated 1 mm³ and 1 µL as different volumes
— the row labelled "1 µL" used `1e-9 × 1e3` m³, which is 1 mL — and estimated the heat
capacity of liquid water by a generic `3 N k_B` Dulong–Petit expression not justified for
a liquid. Corrected: **1 mm³ = 1 µL = 1e-9 m³ exactly**; `c_p = 4.1816 J g⁻¹ K⁻¹`,
`rho = 997.0 kg m⁻³` at 298.15 K (CRC Handbook of Chemistry and Physics, 97th ed.;
equivalently NIST Chemistry WebBook, liquid water at 25 °C). `C/k_B = 3.019634e20`,
remainder ratio `8.2791e-21`, against the superseded `2.491e-20`. The conclusion is
unchanged in substance. **Not a statistical endpoint.**

**Anti-circularity.** Branch A obtains stiffness and field information **without** using
the position-fluctuation dataset Branch B tests. The **corner-frequency /
fluctuation-spectrum route** `k = 2 pi f_c gamma` is now marked **FORBIDDEN for E1a** — it
is the power-spectrum method under another name. Authorised Branch-A routes are exactly
force–displacement with Stokes drag, and independent calibrated thermometry.
Equipartition remains forbidden as tautological. The historical statement in
`docs/e1a/E1A_V4_REPORT.md` is **superseded by notice, not erased**.

**0.9055.** Recorded with its required interpretation: under the declared
Gaussian/log-linear uncertainty model, surrogate calibration model and stated
approximations, the provisional analytical complete-pipeline budget is approximately
0.9055; this exceeds the prospective 0.90 design target but **does not certify achieved
pipeline power**, and the full stochastic validation gate **remains mandatory**. The union
inequality is preserved as an **exact theorem**; its inputs are labelled separately
(nominal allocation, approximate probability, proved bound, quantified-but-unestablished
event). `sigma_k <= 0.34%` and `sigma_cm <= 1.15%` are a **sufficient hypothetical
candidate scenario**, **not** necessary instrument limits.

---

## Adopted prospective constants

| constant | value | endpoint | classification |
|---|---:|---|---|
| `delta_cross` | 0.02 | P2 | author-stated requirement, adopted here |
| `z_cross` | 1.959963985 | P2 | proposed design setting; **no Bonferroni** (IUT) |
| comparisons | 3 | P2 | conjunctive against the common reference |
| `delta_abs` | 0.05 | P3 | **proposed design setting, adopted prospectively; never historically committed** |
| `z_abs` | 1.959963985 | P3 | proposed design setting |
| P3 scope | every tested field | P3 | conjunctive, fail-closed |
| `alpha_geom` | 0.005 | P1 | nominal design allocation |
| `alpha_1` / `alpha_2` | 0.004 / 0.001 | P1 | two-block union bound, no independence asserted |
| `theta_cap` | 5° | P1 | proposed; subject to boundary size/power validation |
| `rank_tol` | 1e-12 | refusal | proposed design setting |
| pipeline target | ≥ 0.90 | all | prospective target |
| provisional budget | 0.9055 | all | approximate analytical calculation |
| `sigma_k` | 0.34% | scenario | **hypothetical instrument scenario** |
| `sigma_cm` | 1.15% | scenario | **hypothetical instrument scenario** |
| `sigma_fs` derived | 0.242747% | scenario | `sqrt(sigma_k^2/m + (sigma_T/T)^2)` |
| `sigma_T` | 0.1 K | scenario | hypothetical |
| `T_total` / `dt` | 240 s / 1.2e-4 s | scenario | hypothetical |
| `pi_P2` / `pi_P3` / `pi(P2∧P3)` | 0.9685 / 0.9544 / 0.9256 | — | approximate probabilities |

---

## Validation

Every check is deterministic: parsing, hashing, arithmetic, string comparison. Both
scripts were inspected for RNG, trajectory and runner tokens before execution; neither
contains any.

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

10. FINITE-BATH UNITS CORRECTION APPLIED
  [PASS] 1 mm^3 == 1 uL == 1e-9 m^3
  [PASS] heat capacity is sourced, not 3 N k_B
  [PASS] remainder is not a statistical endpoint
  [PASS] design markdown carries the correction notice

11. AUTHORIZATION BOUNDARIES ARE CLOSED
  [PASS] analytical design ADOPTED
  [PASS] implementation NOT STARTED
  [PASS] synthetic validation NOT STARTED
  [PASS] preregistration NOT AUTHORISED
  [PASS] physical execution NOT AUTHORISED
  [PASS] baseline status reflects adoption, not validation
  [PASS] baseline no longer claims 'no new design decision is required'

============================================================================
  85 / 85 checks passed
============================================================================
```

```
$ python3 docs/e1a/finite_bath_remainder.py
A. SYMBOLIC (option A of the review): remainder/leading = U / (2 T C), C the
   reservoir heat capacity at constant volume. No numerical value is required for
   the E1a design; the expression alone shows the correction vanishes as C grows.

B. ONE SOURCED VALUE (option B of the review)
   volume                1 mm^3 = 1 uL = 1.000e-09 m^3   (identical volumes)
   density               rho   = 997.0 kg m^-3        [CRC 97th ed., water, 25 C]
   specific heat         c_p   = 4.1816 J g^-1 K^-1  [CRC 97th ed., water, 25 C]
   mass                        = 0.000997 g
   heat capacity         C     = 4.169055e-03 J/K
   C / k_B                     = 3.019634e+20
   remainder/leading at U = 5 k_B T  =  E/(2 C/k_B) = 8.2791e-21

   SUPERSEDED VALUE, for the record: the scratch calculation reported 2.491e-20
   for '1 mm^3' using C/k_B = 3 N k_B = 1.004e20, and a second row labelled '1 uL'
   that was in fact 1 mL. Corrected C/k_B is 3.0196e+20, a factor 3.008 larger,
   and the corrected remainder is 8.2791e-21.

   CONCLUSION, unchanged in substance: the finite-bath correction is ~1e-20 for any
   macroscopic reservoir, so Delta S_constr = k_B E holds to first order in U/(T C).
   The correction changes the number, not the conclusion. NOT a statistical endpoint.
```

```
$ git diff --check
[clean]
```

---

## Repository identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| starting HEAD (this task) | `8c4810383b4995c50f47dbc06c902a307f0fdd72` |
| reviewer's last-checked remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` |
| **final commit SHA** | `c16eb6bf6973c75509cbcbadb33a6c558435ce34` |
| **final tree SHA** | `bbe36068054fe3df5fe75194c11983e8cfcb3d4a` |
| intended remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **2 commits behind local; not pushed** |
| frozen foundation sha256 | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |
| working baseline sha256 | `9b9f22d7…1b732a` → `089024de1aba9f224150dfa64dab82e4c0111e573d1f1b7831728533edc1d96c` |
| design document sha256 | `a1e07232b75546c098403ec69213004599eb195d88fbf5eb3da92876aade1af9` |
| contract sha256 | `6c2db6abfd3851b65ff7aa0bbdaee2788f4e0d81149df95815b5ab174c0e9d4f` |

---

## Git status

Files in commit `c16eb6b`:

```
docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md     | 550 ++++++++++++++++++++++++++++++
 docs/e1a/e1a_v4_design_contract.json      | 336 ++++++++++++++++++
 docs/e1a/finite_bath_remainder.py         |  62 ++++
 docs/e1a/validate_e1a_v4_contract.py      | 170 +++++++++
 docs/theory/EBU_THEORY_BASELINE.md        |  80 ++++-
 docs/theory/EBU_THEORY_BASELINE.meta.json |  33 +-
 6 files changed, 1203 insertions(+), 28 deletions(-)
```

Working tree **clean**. Nothing modified, nothing untracked, nothing staged. History was
not amended or rewritten. **Not pushed** — push requires separate authorisation.

---

## Report provenance

Determined, not guessed:

| question | answer |
|---|---|
| is this file tracked? | **TRACKED AND COMMITTED**, in `fea828e` |
| when was it generated? | **AFTER** the clean-status check it reports |
| does it claim its own commit SHA? | **No.** Every SHA above is the *design-adoption* commit `c16eb6b`; this report was committed separately afterwards |

The "working tree clean" line under **Git status** describes the tree **at commit `c16eb6b`**,
which is what that section is about. This report file did not exist at that moment; it was
written afterwards and committed on its own. Neither statement is self-referential, and no SHA
in this document was asserted before it existed.

**Convention adopted, and followed from here on:**

```
scientific / design work  ->  work commit
handoff report            ->  generated after the work commit, then its own report commit
```

So an E1a task produces two commits: the work commit, then the report commit. Reports stay
inside the repository as tracked artifacts at `docs/e1a/`, are marked task artifacts rather than
authority tier, and are never written so as to assert a SHA that does not yet exist.

---

## Execution boundary

**No stochastic experiment and no synthetic campaign ran.** No random draws, no OU
trajectories, no stochastic calibration, no model stepping, no simulation runner, no real
data, no physical apparatus work. No preregistration. No E1b. No Stage B. Work was
limited to inspection, deterministic parsing, arithmetic, hashing and schema checks.

---

## Next possible stage

```
E1a v4 bounded implementation
NOT STARTED
```

It requires separate authorisation. The synthetic validation campaign of design §15
follows implementation and is a further, separate authorisation. Preregistration and
physical execution remain unauthorised.

---

```
DESIGN AUTHORITY ADOPTED AND COMMITTED
```
