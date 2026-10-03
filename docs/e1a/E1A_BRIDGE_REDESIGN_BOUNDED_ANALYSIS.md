# E1a — BOUNDED REDESIGN ANALYSIS

## Direct Boltzmann bridge vs the Hessian-centric E1a-v4 programme

**Status:** ANALYSIS ONLY. **NOT AUTHORITATIVE.** Decides nothing.
**Execution:** NOT AUTHORISED. No RNG, no calibration, no trajectory, no campaign job.
**Authority changed:** none. **Implementation changed:** none. **Tests changed:** none.
**E1a-v4:** PRESERVED. Not rejected, not deleted, not rewritten.

Responds to the redesign proposal "EBU E1a BRIDGE REDESIGN ANALYSIS" by answering its §46
questions from repository evidence, and by comparing its Options A–D. Where a claim could
be checked against the committed code or the frozen plan, it was checked; where it could
not, that is said.

| coordinate | value |
|---|---|
| analysed at HEAD | `bd9a3a111068e5be72bcdf21c5bd15b82da73012` |
| branch | `gaussian/stage-a-environment` |
| plan version | `1.17.0` |
| working tree | clean |

---

## 0. Headline findings

Three results dominate everything else, and two of them are not in the proposal.

**F-1 — The proposal's "remarkably direct estimator" is the estimator E1a-v4 already uses.**
Verified bit-exactly. §13's `β̂ = d / tr(S_z)` and design §4's `β̂ = m / tr(H_A S)` are the
same number, because `tr(H^{1/2} S H^{1/2}) = tr(H S)` by cyclicity. The redesign's
statistical core is therefore **not new** — it is a change of representation. Its real gains
lie elsewhere (F-3, and the non-Gaussian path).

**F-2 — The experiment is systematics-limited, not statistics-limited, by an order of
magnitude.** Under the frozen scenario `σ_stat ≈ 0.09%` against `σ_cm = 1.15%` and
`σ_fs = 0.243%`. Deleting the statistical term from the P3 band entirely changes it by
**0.3%**. The absolute `β = 1` test is set almost wholly by Branch-A common-mode
calibration. Neither the proposal nor the current plan states this.

**F-3 — The single largest available simplification is not the one the proposal argues
for.** It is replacing the Monte-Carlo-calibrated Block-1 min-p null with a direct method
(exact OU likelihood, or block bootstrap). That removes the 46,000 calibration artifacts
and with them `CalibrationCondition`, calibration locks, the reuse ledger, lock recovery
and reconciliation — i.e. essentially the whole subsystem that consumed F1 and F2. The
proposal lists "exact Gaussian/OU likelihood" as one of four options in §22 without noting
what choosing it eliminates.

A fourth finding is a defect in the **current** programme, independent of the redesign:

**F-4 — Under Route A as specified, the synthetic validation does not model the dependency
it most needs to.** "Force–displacement with Stokes drag" obtains the laboratory `H_U` from
a known viscous force `F = 6πηa·v`, so real `k` and `γ` are correlated through `ηa`. The
v4 synthetic model treats them as independent: `build_field` takes `k_modes` from the
contract spec and `η`/`a` as separate arguments, and `BranchAErrorModel.measure` perturbs
`k` by `sigma_k` with no `η`/`a` term. The declared uncertainty budget
`σ_fs = sqrt(σ_k²/m + (σ_T/T)²)` likewise contains no drag term, while the contract lists
"measurement uncertainty for eta" and "measurement uncertainty for a" as **not declared**.
So the current campaign cannot exercise the Route-A error propagation the real experiment
would have.

---

## 1. F-1 in full — the estimator identity

The proposal's §13 derives

```
z = H^{1/2}(x - x*) ,   Cov(z) = (1/β) I ,   β̂ = d / tr(S_z)
```

and calls it "a remarkably direct estimator". It is the existing one. By cyclicity of the
trace,

```
tr(S_z) = tr(H^{1/2} S H^{1/2}) = tr(S H) = tr(H_A S)
```

so `d / tr(S_z) ≡ m / tr(H_A S)`, which is design §4 verbatim. Checked numerically on a
deterministic SPD pair, no RNG:

```
H = [[2.5, 0.7], [0.7, 1.3]]      S = [[0.41, -0.18], [-0.18, 0.86]]
redesign §13   β̂ = d / tr(S_z)   = 1.0576414595452142
E1a-v4  §4     β̂ = m / tr(H_A S) = 1.0576414595452142
tr(S_z) = tr(H_A S) = 1.891        relative difference 0.0
```

The energy form is the same estimator again: `V = ½‖z‖²`, so `E[V] = d/(2β)` and
`β̂ = d / (2 V̄)`, which for `d = 2` is `β̂ = 1/V̄`. And for a harmonic `V` the Boltzmann
likelihood of §24 has `ln Z(β) = (d/2)ln(2π/β) − ½ln|H|`, giving
`dℓ/dβ = 0 ⟹ β̂ = (d/2)/V̄` — the MLE coincides with the moment estimator.

**Consequences.**

- Option D's estimation layer is E1a-v4's estimation layer. Nothing about sample size,
  bias or uncertainty improves by adopting it.
- The proposal's §21 worry ("using only `V̄` could miss geometry errors") applies equally
  to the current `β̂`; it is not a new hazard introduced by the energy form.
- `β̂` is a ratio estimator and is **biased**: `E[1/X] ≠ 1/E[X]`. Design §4 already handles
  this with the exact finite-sample identity `β̂ = mβ / tr(G M)`. The redesign inherits the
  issue and must carry that identity forward; §13 does not mention it.

---

## 2. F-2 in full — the experiment is systematics-limited

Computed from the frozen scenario (`dt = 1.2e-4 s`, `T_total = 240 s`, `n = 2,000,000`,
`η = 8.9e-4`, `a = 1e-6`) through the production `sigma_stat` and `N_element`:

| field | `k` (µN/m) | `σ_stat` | `σ_fs` / `σ_stat` | `σ_cm` / `σ_stat` |
|---|---|---|---:|---:|
| `theta0_circular` | 100, 100 | 0.090% | 2.69× | 12.74× |
| `theta1_power` | 210, 210 | 0.074% | 3.27× | 15.48× |
| `theta2_ellipse` | 150, 60 | 0.097% | 2.51× | 11.90× |
| `theta3_temperature` | 100, 100 | 0.090% | 2.69× | 12.74× |

against the declared `σ_fs = 0.243%` and `σ_cm = 1.15%`.

Effect on the decision bands (`z = 1.959963985`):

```
theta0  P3 half-width h = 0.02310 ;  with σ_stat removed ENTIRELY: 0.02304   (−0.29%)
theta2  P3 half-width h = 0.02311 ;  with σ_stat removed ENTIRELY: 0.02304   (−0.34%)
```

**Record-length sensitivity.** `σ_cm` cancels in the P2 ratio and does not in P3, so the
two endpoints behave completely differently:

| `n` | `T_total` (s) | `σ_stat` | P3 `h` (δ_abs = 0.05) | P2 `h_j` (δ_cross = 0.02) |
|---:|---:|---:|---:|---:|
| 2,000,000 | 240.0 | 0.00090 | 0.02310 | 0.00721 |
| 1,000,000 | 120.0 | 0.00128 | 0.02317 | 0.00766 |
| 400,000 | 48.0 | 0.00202 | 0.02337 | 0.00888 |
| 200,000 | 24.0 | 0.00285 | 0.02371 | 0.01060 |
| 100,000 | 12.0 | 0.00404 | 0.02436 | 0.01340 |
| 50,000 | 6.0 | 0.00571 | 0.02561 | 0.01772 |
| 20,000 | 2.4 | 0.00902 | 0.02904 | **0.02677** |

P3 stays inside `δ_abs = 0.05` even at a **2.4-second** record. P2 is the binding endpoint:
`h_j` passes `δ_cross = 0.02` somewhere between `n = 50,000` and `n = 20,000`.

**This reframes the whole programme.** The absolute `β = 1` claim — the one the proposal
calls the core EBU question — is limited by how well the common-mode Branch-A scale is
known, not by how long the bead is watched. Any redesign that reduces software burden but
leaves `σ_cm = 1.15%` untouched does not improve the primary scientific result.

---

## 3. F-3 in full — what the redesign could actually remove

The 46,000 calibration artifacts exist for one reason: the Block-1 decision is `min-p` over
four correlated statistics `G1–G4`, whose joint null has no closed form and is therefore
**Monte-Carlo-calibrated at each replicate's realised `H_A`**.

| case | R | subconditions | artifacts | role |
|---|---:|---:|---:|---|
| `C1_true_bridge_complete` | 300 | 4 | 4,800 | primary |
| `C2_geometry_false_rejection` | 400 | 4 | 6,400 | primary |
| `C3_g5_block` | 400 | 4 | 6,400 | primary |
| `C4_surrogate_validity` | 2,000 | 1 | 8,000 | primary |
| `C5_plug_in_branch_a` | 400 | 12 | 19,200 | primary |
| `C6_mode_resolution_boundary` | 400 | 3 | 1,200 | primary |
| `C7_false_bridge` | 400 | 4 | 0 | negative control |
| `C8_blinded_scale_control` | 200 | 1 | 0 | positive control |
| **total** | | | **46,000** | |

The proposal's `S_z = I` is **one** statistic, not four. For a Gaussian record it is a
sphericity hypothesis on the whitened covariance, and the OU process is a linear Gaussian
state-space model with an **exact available likelihood**. Adopting the exact-likelihood
route of §22 therefore removes, as a chain:

```
surrogate covariance draw          ->  no approximation to validate  ->  C4 disappears (8,000 artifacts)
Monte-Carlo min-p null             ->  no artifact to produce
no artifact                        ->  no CalibrationCondition identity
no condition identity              ->  no calibration lock, no lock digest, no lock store
no lock                            ->  no reuse ledger, no limited-reuse rule, no CASE_FIXED question
no lock                            ->  no lock recovery, no restart lock reconciliation
no eta/a in the uncertainty model  ->  F4's drag inputs leave the primary analysis (see §5)
```

That is substantially the entire subsystem audited across F1 and F2 — including the
package-binding question just resolved at `9ada901` / `bd9a3a1`. **The proposal does not
claim this.** It is the strongest argument available for a redesign, and it is checkable.

It also retires design §12.1's standing qualification #1, that "the surrogate calibration
law is approximate for correlated observations — the exact law is `3/2` times more skewed
than any covariance-matched surrogate". An exact likelihood has no surrogate to be skewed
relative to.

**What it does not remove, and must not be claimed to remove.** Asymptotic `χ²` for a
likelihood-ratio statistic is still an approximation at finite effective sample size with
correlated data, so achieved size must still be demonstrated. `C2` survives in some form
under every option.

**What it costs.** `G1–G5` are *diagnostic*: they distinguish shape disagreement from
spread, from principal-angle error, from eigenvalue-ratio error, from non-Gaussianity. A
single likelihood-ratio says the bridge failed, not how. §14's `G = S_z / s` recovers part
of this. That is a real trade-off, not a free win.

---

## 4. F-4 in full — the unmodelled Route-A dependency

Design §2.1 authorises exactly one mechanical route: **"force–displacement with Stokes
drag"**. In a real apparatus that means applying a known viscous force, `F = γv = 6πηa·v`,
and reading the displacement, so

```
k_measured = F / Δx = 6π η a v / Δx
```

— the laboratory stiffness is a **function of η and a**. Their uncertainties therefore
propagate into `σ_k`, and `σ_k` enters both decision bands through
`σ_fs = sqrt(σ_k²/m + (σ_T/T)²)`.

The synthetic model does not represent this:

| element | what it does | consequence |
|---|---|---|
| `build_field` | `k_modes` comes from the contract spec (`k_uN_per_m`); `viscosity` and `bead_radius` are independent arguments | `H_U` has no `η`/`a` dependence |
| `BranchAErrorModel.measure` | perturbs `k_modes`, `rot_deg`, `T` by `σ_k`, `σ_psi_deg`, `σ_T`; passes `η`, `a` through **unchanged** | no `η`/`a` error enters `H_A` |
| `σ_fs` formula (contract) | `sqrt(σ_k²/m + (σ_T/T)²)` | no drag term |
| contract `values_not_set` | "measurement uncertainty for eta", "measurement uncertainty for a" → **not declared**, F4 OPEN | the term that would appear has no declared value |

So under Route A the declared Branch-A uncertainty budget is **structurally incomplete**,
and the synthetic campaign — however many replicates it runs — cannot detect that, because
its generator does not contain the dependency. Given F-2, this matters more than it looks:
`σ_fs` is the term that sets the P2 band, and P2 is the binding endpoint.

This is a finding about the **current** programme. It is not caused by the redesign and is
not cured by changing representation. It is, however, a strong argument for taking
proposal §10 question 4 (Route A vs Route B) seriously on *scientific* grounds rather than
software grounds — which is exactly what the proposal says should happen.

---

## 5. Where `η` and `a` actually enter — and what that means for F4

Established by direct dependency trace in the committed reconstruction (`9ada901`,
corrected at `bd9a3a1`) and unchanged here:

```
η, a  ->  γ = 6π η a  ->  τ_r = γ / k_r  ->  φ_r = exp(−dt/τ_r)  ->  N_ab(φ_a, φ_b, n)
      ->  per-element variance of the surrogate S  ->  the Block-1 null
      ->  and, separately, σ_stat(φ, n)
```

They touch **nothing else** — not `H_A`, not `β̂`, not `G1–G4`, not `G5`. The only other
reader is the synthetic trajectory generator, which has no laboratory counterpart.

Combining this with F-2 and F-3 gives a conclusion neither document states:

> In the *current* design, `η` and `a` are required **only** to compute the temporal
> correlation that sets a term contributing **0.3%** of the P3 band — and the
> Block-1 surrogate null, which a direct method would remove. In a laboratory experiment
> there is no synthetic generator. So if the correlation time is estimated from the
> Branch-B record for **uncertainty quantification only**, `η` and `a` leave the primary
> analysis entirely, under **either** Branch-A route.

Two cautions, both necessary.

1. **This is legitimate only for uncertainty, never for the point estimate.** Design §2.1
   forbids the corner-frequency route `k = 2π f_c γ` because it reconstructs `H` from the
   Branch-B fluctuation record. Estimating an autocorrelation time to size an error bar
   does not produce `H` and does not make `β = 1` tautological. The boundary is sharp and
   must be written into any redesigned preregistration, not left implicit.
2. **It does not rescue Route A.** Under Route A, `η` and `a` are still needed for `H_U`
   itself (F-4). The escape above applies to the *uncertainty model*; Route A's dependence
   is in the *measurement*. Only Route B removes both.

**F4 is therefore not eliminated by the redesign.** It is relocated: under Route B plus a
record-based correlation estimate, F4 reduces to declaring the force-calibration model;
under Route A it remains, and gains the missing uncertainty term of F-4.

---

## 6. The §46 questions, answered

**1. Is the direct Boltzmann bridge scientifically equivalent to the current E1a target?**
For the harmonic benchmark, **yes, and exactly so**. `K = Σ⁻¹` for a Gaussian, so
`K = βH ⟺ H^{1/2}ΣH^{1/2} = β⁻¹I ⟺ S_z = β⁻¹I`. Outside the Gaussian family they are
*not* equivalent: `−ln p = βV + C` is strictly stronger than equality of curvature at a
point. The proposal is right that the current test is a local consequence of a global
statement; for the first benchmark the distinction has no empirical content, and for
anharmonic successors it has a great deal.

**2. Is the Gaussian whitened-covariance estimator sufficient for the first benchmark?**
Yes for the scale. By F-1 it *is* the current estimator. It is not sufficient alone for
geometry — `tr` discards everything but the mean eigenvalue — which is why §14's
`G = S_z/s` or an equivalent must accompany it. The single statement `S_z = I` carries
both, and is a genuine expositional improvement over five gates plus a two-block union
bound.

**3. Should direct Boltzmann likelihood be primary and K/H secondary?**
On the evidence, **yes as the stated hypothesis, with no change to the first experiment's
arithmetic**. The benefit is not statistical (F-1) but (a) it names what is being tested,
(b) it extends to anharmonic `V` where `Z(β)` must be computed numerically and curvature
equality is insufficient, and (c) it makes the Gaussian case visibly a special case rather
than the definition. Recommend recording it as the hypothesis and `K = βH` as an exact
Gaussian corollary and diagnostic.

**4. Which Branch-A route is most independent and feasible?**
**Not answerable from the repository** — feasibility is an apparatus question and no
apparatus characterisation is committed. What the repository *does* establish is F-4:
Route A's `η`/`a` dependence of `H_U` is real, is currently unmodelled, and its uncertainty
contribution is undeclared. That is a reason to analyse Route B seriously, not a reason to
adopt it. **Flagged as requiring experimental input this analysis cannot supply.**

**5. Which E1a-v4 controls remain scientifically necessary?**

| case | verdict | reason |
|---|---|---|
| `C2` geometry false-rejection | **NECESSARY under every option** | you declare a gate at `α_geom = 0.005`; achieved size under *correlated* data must be demonstrated, whatever the statistic |
| `C5` plug-in Branch-A | **NECESSARY under every option** | design §12.1 item 3: calibration conditions on measured `H_A`, not `H_true`. Representation-independent |
| `C7` false bridge | **NECESSARY** | negative control; acceptance of a known-false bridge is the error that matters |
| `C8` blinded scale | **NECESSARY, and more so than recorded** | it probes `σ_cm`, which by F-2 is the dominant systematic in P3 |
| `C3` G5 block | **NECESSARY, and arguably promoted** | under `p ∝ e^{−βV}` the Gaussian form is an assumption, so non-Gaussianity is a primary falsifier, not a side gate |
| `C6` mode resolution | **changes form, shrinks** | near-degenerate `H` makes `H^{1/2}` ill-conditioned; becomes a conditioning question, not a principal-angle blocking rule |
| `C4` surrogate validity | **ELIMINABLE** | exists only because the null is a covariance-matched surrogate. A direct method removes the object it validates (F-3): 8,000 artifacts |
| `C1` complete pipeline ≥ 0.90 | **not necessary for a first scientific result** | an operating-characteristic claim about an implemented pipeline; necessary for a release claim, not to learn whether `β = 1` |

**6. Which are software-certification rather than core science?**
Restart/recovery across malformed artifacts, authority-gap mutation classes, execution
sealing, publication transaction mechanics, structured-refusal record integrity, the
calibration lock and ledger. All are infrastructure for a certified automated campaign.
None is needed to learn whether `β = 1` in a laboratory. Branch-A/Branch-B separation,
blinding order and seed-family disjointness are **not** in this group — they are
anti-circularity, and they are core science.

**7. What sample size is required?**
Answered quantitatively in F-2. P3 is insensitive: it passes at `n = 20,000` (2.4 s). P2
binds and saturates: `h_j` crosses `δ_cross = 0.02` between `n = 50,000` and `n = 20,000`,
and gains almost nothing above `n ≈ 10⁶`. **`n ≈ 2×10⁵–10⁶` (24–120 s per field) retains
essentially all the power of the declared `n = 2×10⁶`.** The declared record is comfortable
but not required, and lengthening it further cannot improve the absolute `β = 1` result.

**8. How should temporal correlation be handled?**
It must be handled, but F-2 bounds how much care it deserves for the *bands*: it moves the
P3 half-width by 0.3%. Recommended, in order: exact OU likelihood (which also delivers F-3);
failing that, block bootstrap with a predeclared block length; `N_eff` as the current design
does it is adequate but inherits the surrogate issue. **Thinning is not recommended** — it
discards information to buy an independence assumption that the exact likelihood does not
need. Whichever is chosen, the §5 caution applies: record-based correlation estimates may
size uncertainty and must never enter the point estimate.

**9. How should Branch-A uncertainty be propagated?**
By F-2 this is *the* dominant term and deserves the most care in the redesign — the
opposite of the proposal's emphasis. The current design propagates `σ_k`, `σ_psi`, `σ_T`
through `σ_fs` and `σ_cm` analytically, with `σ_cm` cancelling in P2 and not in P3; that
structure is sound and should survive. Two changes are indicated: (a) add the drag term
Route A requires (F-4), or adopt Route B and remove the need; (b) state explicitly that
`σ_cm`, not sampling, sets the floor on the absolute claim.

**10. Which equivalence margins should survive?**
`δ_abs = 5%` and `δ_cross = 2%` are both comfortable against the computed bands
(`h ≈ 0.023` vs 0.05; `h_j ≈ 0.0072` vs 0.02) and neither is strained by any record length
down to `n ≈ 10⁵`. **No margin change is indicated by this analysis.** Design §7.1 already
records that `δ_abs = 5%` was adopted prospectively and was never historical authority; that
disclosure should carry forward verbatim. `α_geom = 0.005` is a gate allocation and only
means something if achieved size is demonstrated (question 5, `C2`).

**11. Which field arms are necessary?**
All four, and they are not interchangeable. `θ0` sets the absolute benchmark. `θ1`
(stiffness) is the only arm that changes `τ` without changing geometry and is therefore the
one that exposed the original `theta0`/`theta1` calibration defect. `θ2` (ellipse +
rotation) is the **only** arm that can distinguish geometry agreement from scalar variance
agreement — without it `S_z = I` degenerates to a single scalar test. `θ3` (temperature)
is the only arm that tests the `k_B T` normalisation, which is precisely the "common ruler"
claim. Dropping any one removes a distinct falsifier.

**12. What synthetic validation is sufficient before laboratory execution?**
The proposal's S0–S6 is a reasonable skeleton but is a *reduced* `C1–C8`, not a replacement
for calibrated gates. Mapping: S0–S3 ≈ `C1` reduced; S4 ≈ `C8`; S5 ≈ `C7` plus the geometry
arm; S6 ≈ `C2` + `C4`. **`C5` (plug-in `H_A`) has no S-counterpart and must be added** —
analysing with measured rather than true `H_A` is a bias source no amount of record length
removes. A defensible minimum is: estimator recovery at known truth, hidden-scale recovery,
a geometry mismatch that must be detected, achieved size under correlated OU data, and
plug-in `H_A`. That is five objects, not eight cases and 46,000 artifacts.

**13. What result gates progression to nonequilibrium Stage A/B?**
**Proposal only; this analysis decides nothing.** A coherent gate would be: all four fields
accept P3 at `δ_abs`; all three cross-field comparisons accept at `δ_cross`; the geometry
diagnostic consistent with `I` in every field; and the blinded-scale control recovering
`1/c`. Note the honest caveat from the proposal's own §5.1: passing this is consistent with
equilibrium statistical mechanics being correct and the apparatus being well calibrated. It
does not establish anything new about EBU. Only the **nonequilibrium** extension (§34) tests
a statement that is not already a theorem.

**14. Which topology experiments are unaffected?**
Those that are consequences of the definition `E = V_pre − V_post` alone — path and
sequential composition, parallel motif algebra, telescoping identities, graph invariants.
They are mathematical properties of a defined potential structure and no experimental
calibration result can falsify them. **Not verified against the topology sources in this
analysis**; the claim is reported from the proposal and is logically sound, but the
corresponding files were not read and this is not an audit of them.

**15. Which require successful cross-field calibration first?**
Any that attach *physical* EBU magnitudes to transitions across different fields, and any
actor/capacity simulation that accumulates EBU earned under one field with EBU earned under
another. The proposal's §39 is correct: if `β` varies by field, fixed-field topology stays
valid while cross-field accumulation does not. That is the real dependency, and it argues
for the bridge benchmark preceding Stage B — with the §33 caveat that the bridge validates
the ruler and not any later use of it.

---

## 7. Options A–D compared

| | A: continue v4 | B: minimal Gaussian cov/Hessian | C: direct Boltzmann likelihood | D: hybrid |
|---|---|---|---|---|
| scientific target | `K = βH` | `S_z = I` | `p ∝ e^{−βV}` | Boltzmann primary, `S_z = I` estimator, `K = βH` diagnostic |
| estimator | `m/tr(H_A S)` | **identical** (F-1) | identical for Gaussian `V` (MLE = moment) | identical |
| calibration artifacts | 46,000 | 46,000 unless the null method also changes | 0 with exact likelihood | **0 if F-3 adopted; 46,000 if not** |
| `C4` surrogate case | required | required | eliminated | eliminated |
| non-Gaussian path | none | none | native | native |
| diagnostic resolution | highest (G1–G5) | reduced | reduced | reduced, partly recovered by `G = S_z/s` |
| `σ_cm` floor on P3 | unchanged | unchanged | unchanged | **unchanged** |
| F4 `η`/`a` burden | full | full | reduced to the uncertainty model | reduced; eliminated under Route B |
| work already done | fully reusable | mostly reusable | estimator reusable | fully reusable as Track V |

**The decisive observation is the bottom-but-one row.** No option improves the absolute
`β = 1` result, because all four share `σ_cm = 1.15%`. The options differ in **software and
provenance burden**, in **non-Gaussian extensibility**, and in **diagnostic resolution** —
not in the precision of the primary scientific claim.

**Assessment of the proposal's recommendation.** Option D is defensible, but **not for the
reason given**. §48 argues it is strongest because it "preserves the key insight
`p ∝ e^{−βV}` rather than treating Hessian equality as the whole theory". By F-1 that
insight costs and buys nothing arithmetically in the first benchmark. Option D is strongest
if and only if it is taken **together with F-3** — replacing the Monte-Carlo surrogate null
with a direct method. Option D with the surrogate retained is Option A with new vocabulary.

**Recommended framing, as a proposal for independent review:**

```
Option D + F-3  :  Boltzmann bridge as the stated hypothesis
                   S_z = I as the Gaussian implementation (= the existing estimator)
                   exact OU likelihood or block bootstrap in place of the surrogate null
                   K = βH retained as an exact Gaussian diagnostic
                   C2, C3, C5, C7, C8 retained in reduced form; C4 eliminated
                   E1a-v4 retained as Track V infrastructure
```

with the precondition that **F-4 is resolved first**, because it is a defect in the
Branch-A uncertainty budget under the currently authorised route and it affects every
option equally.

---

## 8. What this analysis does not do

- It **does not** decide anything. The proposal is not authoritative and neither is this.
- It **does not** change authority, implementation, tests, the plan, the contract, the seal
  or any identity.
- It **does not** audit the topology sources; question 14's answer is reported, not verified.
- It **does not** assess apparatus feasibility (question 4), which needs experimental input.
- It **does not** claim E1a-v4 was wasted. F-1 shows its estimator is already the right one;
  F-2 and F-3 were only computable *because* the frozen plan states its uncertainty
  scenario and case structure precisely enough to evaluate.
- It **does not** resolve the open F2 items. The C7/C8 underflow defect is confirmed and
  unrepaired; the `BranchARealisation.calibration_condition` constructor question is
  authority-unspecified. Both stand.

---

## 9. State

```
OFFICIAL CAMPAIGN     NOT RUN          SCIENTIFIC RNG DRAWS   0
OFFICIAL RESULTS      NONE             OFFICIAL TRAJECTORIES  0
EXECUTION SEAL        NOT FROZEN       CALIBRATION EXECUTIONS 0
EXECUTION AUTHORISED  FALSE            CAMPAIGN JOBS          0
```

Identities unchanged — reports are outside every preimage:

```
contract   d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4
design     25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6
plan       fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4
seed map   c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af
analysis   60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527
execution  442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b
```

4,002 checks, 0 failures, 17 suites, 0 unclean; static preflight PASSED.

**Next step:** independent review of this analysis and of the proposal. No implementation,
no authority amendment and no execution follows from either until that review completes.
