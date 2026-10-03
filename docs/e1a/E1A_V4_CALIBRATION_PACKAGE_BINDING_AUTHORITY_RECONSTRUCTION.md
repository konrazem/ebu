# E1a v4 — CALIBRATION PACKAGE BINDING: AUTHORITY RECONSTRUCTION

**READ-ONLY.** No authority file, no implementation file and no test changed in this
task. Nothing was executed that advances model state: no scientific RNG, no
calibration draw, no trajectory, no campaign job. Every reproduction below uses
the existing pure deterministic fixture mechanisms.

**Scope.** One question, derived from repository authority rather than preference:

> When two distinct valid Branch-A primitive packages contain different `eta`/`a`
> values but induce exactly the same calibration-relevant physical/statistical
> condition, MUST their calibration-condition identities remain distinct? Or may
> one calibration artifact be reused because the declared calibration condition is
> scientifically identical?

This task follows the independent F2f audit, which returned `F2 NOT CLEARED` for two
reasons. It addresses **only the second** — calibration artifact reuse across distinct
primitive packages. The first (C7/C8 numerical gating) is recorded in section 13 and
deliberately not repaired here.

| coordinate | value |
|---|---|
| starting HEAD | `5b9542eee3498ec8b8e1e3f124d95714b5fa4404` |
| branch | `gaussian/stage-a-environment` |
| working tree at start | clean |
| latest F2 work commit | `7f0647624c4a415071411c719fd615a54357f452` |
| latest F2 report commit | `5b9542eee3498ec8b8e1e3f124d95714b5fa4404` |

---

## 1. Summary of findings

| question | finding |
|---|---|
| is the auditor's transplant reproducible today? | **yes**, end to end, with pure fixtures |
| do the two packages' Branch-A evidence identities differ? | **yes** — and in exactly the two expected keys |
| are their `CalibrationCondition` identities equal? | **yes**, byte-identical; `first_difference` is `None` |
| does an artifact built at package A verify against package B? | **yes**, at `require_calibration`, at `lock_calibration` and at `verified_calibration_lock` |
| do `eta`/`a` enter the Block-1 null law independently of `gamma`/`tau`? | **NO INDEPENDENT NULL-LAW EFFECT FOUND** |
| would the official driver produce a *different* artifact for the two packages? | **no** — every generator input and the calibration seed are bit-identical, so the artifact is the same object, not a substitute |
| does the calibration **lock** bind the exact Branch-A package? | **yes** — `branch_a_evidence_sha256`, which under schema `/3` contains `eta` and `a` |
| is cross-coordinate artifact sharing possible? | **no** — `CampaignCalibrationLedger` refuses it (`CALIBRATION_REUSE_REFUSED`) |
| does authority decide the question? | **yes** |
| new human scientific decision required? | **NO** |

**Disposition: C — shared condition plus exact lock provenance.** The
`CalibrationCondition` is the *null law*, and authority says so in terms; exact
package provenance is carried one layer out, at the calibration lock and the terminal
record, where it is already enforced and where schema `/3` has now made it exact.

The decisive structural fact is in section 12: the auditor's two packages can only
coexist *because F4 is open*. Authority already requires the Branch-A field-construction
inputs to be declared in frozen authority before the seal is frozen, and
`CalibrationCondition` already binds `contract_sha256`. The moment F4 closes, two
distinct official `eta`/`a` packages necessarily carry two distinct contract digests
and therefore two distinct calibration conditions.

---

## 2. Authority read, in order

1. `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` — contains **no**
   occurrence of "calibrat". It fixes no rule on this question.
2. `docs/theory/EBU_THEORY_BASELINE.md` — §14 fixes the authorised and forbidden
   Branch-A calibration *routes* and the thermometry route. It says nothing about
   calibration-artifact identity.
3. `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` — §3.1 (G6, the passive-drag domain), §7
   (P3), §12.1 and §14.
4. `docs/e1a/e1a_v4_design_contract.json` — `branch_a_measured_input_domain`.
5. `docs/e1a/e1a_v4_synthetic_validation_plan.json` — `calibration`, in particular
   `condition_binding`, `calibration_scope_disposition`, `global_reuse_prohibition`,
   `limited_reuse_rule`, `artifact_identity_fields`, `ordering`, and
   `driver_requirements.branch_a_provenance`. **This is where the question is decided.**
6. Implementation, as evidence and not as authority: `e1a_v4/calibration.py`,
   `e1a_v4/validation/calibrate.py`, `e1a_v4/validation/campaign_driver.py`,
   `e1a_v4/validation/scope.py`, `e1a_v4/branch_a.py`, `e1a_v4/world.py`,
   `e1a_v4/validation/generate.py`.
7. Historical record: `docs/e1a/E1A_V4_PREEXEC_REPAIR_REPORT.md` §B1, commit
   `5727e10`, `docs/e1a/E1A_V4_PREEXEC_CORRECTION_ADOPTION_REPORT.md`,
   `docs/e1a/E1A_V4_CALIBRATION_SCOPE_REPORT.md`,
   `docs/e1a/E1A_V4_TERMINAL_CALIBRATION_PROVENANCE_REPORT.md`,
   `docs/e1a/E1A_V4_CALIBRATION_LOCK_VERIFIER_REPORT.md`.

No chat summary was used as authority.

---

## 3. Package-transplant reproduction

### 3.1 The two primitive packages

```
Package A:   eta = 8.9e-4  = 0x1.d29dc725c3deep-11     a = 1e-6 = 0x1.0c6f7a0b5ed8dp-20
Package B:   eta = 4.45e-4 = 0x1.d29dc725c3deep-12     a = 2e-6 = 0x1.0c6f7a0b5ed8dp-19
```

`eta_A != eta_B` and `a_A != a_B`. Both differ by exactly one binade, so the products
agree **bit-exactly** and not merely to tolerance — halving and doubling are exact in
binary64, and `BranchAField.gamma` evaluates `((6*pi) * eta) * a` left to right, so the
rounded result is the same double:

```
gamma_A = gamma_B = 0x1.203616cc4437fp-26
tau_A   = tau_B   = (0x1.5fd206d459465p-13, 0x1.5fd206d459465p-13)
```

Both fields are built through `build_field` on the frozen `theta0_circular` contract
spec with the authorised route, and both carry `status = VALID`.

### 3.2 Evidence identities differ

```
evidence A = 1f265d6eb35a23db4d176629da03255578cf3db6c7e6591404d56d332365981e
evidence B = c642d45ff81e0a956d4f12c67fcbb992a3b8e942381ec7092b5ec7a4109bf746
differing preimage keys = ['bead_radius', 'viscosity']
```

Exactly the two keys schema `/3` added, and nothing else. Temperature, orientation,
`H_A`, `k_modes`, `tau_modes`, `scale_factor`, `n_samples`, `dt`, route, status and every
package identity are identical.

### 3.3 Condition identities are equal

```
condition A = 4aa86af9709ef96bd12ca54ae817f95d0fff50d0138c6e1a4622534efad778bd
condition B = 4aa86af9709ef96bd12ca54ae817f95d0fff50d0138c6e1a4622534efad778bd
condA.first_difference(condB) = None
```

`first_difference` returning `None` is the complete answer to the section-9 equivalence
test: **every** component of the declared condition preimage is identical, not merely the
ones the audit named.

### 3.4 The artifact transplants, at every layer

Driving two sandboxed campaigns to the calibration lock — package A in one, package B in
the other, same job coordinate, pure fixture artifacts, no draws:

```
require_calibration(artifact_A, condition_B)          -> ACCEPTED
JobExecution.lock_calibration(artifact_A) on package B -> ACCEPTED
verified_calibration_lock(... package B campaign ...)  -> ACCEPTED
```

The two lock records differ in exactly `branch_a_evidence_sha256`,
`publication_digest` and the derived `lock_digest`; the locked
`calibration_artifact_sha256` is identical.

**CURRENT PACKAGE TRANSPLANT: REPRODUCED.**

### 3.5 What the transplant is not

Two bounds matter before the finding is weighed.

**Bound 1 — the ledger refuses cross-coordinate sharing.** Inside one campaign,
locking an artifact to job `r0` and then presenting the same artifact to job `r1`:

```
CALIBRATION_REUSE_REFUSED: artifact 9a0f8a4c5babad57... is already locked to
('C2_geometry_false_rejection', 'sigma_psi_0p0', 0, 'theta0_circular')
```

So artifacts are not reusable across jobs even when the conditions agree. The transplant
exists only *at one coordinate*.

**Bound 2 — at one coordinate the two artifacts are the same object.** The official
runner builds the artifact from a `CalibrationRequest` whose every field is taken from
the condition plus `measured.H`, and seeds it with
`provider.generator(execution.calibration_seed(), "calibration")`.
`ReplicateCalibration.calibration_seed` derives from
`(CALIBRATION family, subcondition_id, replicate, field_id)` — it never reads `eta`, `a`,
`gamma` or `tau`. Every generator input and the RNG seed are therefore bit-identical
between packages A and B, so `generate_block1_artifact` returns the **same artifact**.

This is an analytic result from the dependency graph; no calibration was generated to
obtain it. It means the "transplant" substitutes nothing: there is no package-A artifact
that differs from the package-B artifact it would replace.

---

## 4. The current condition preimage, field by field

`CalibrationCondition.canonical()` emits 17 keys. Source and authority for each:

| field | scientific meaning | source | why it affects calibration | authority |
|---|---|---|---|---|
| `schema` | artifact/condition version tag | `CALIBRATION_ARTIFACT_SCHEMA` | version break is not reinterpretable | plan `calibration.artifact_schema` |
| `field_id` | which declared field | realisation | **does not** change the law; bound as fail-safe isolation | plan `condition_binding.bound`; B1 table |
| `m` | mode count | `len(H_A)` | dimension of every gate | B1 table (implicit in `H_A`) |
| `H_normalised` | `H_A / tr(H_A)` — eigenvalue ratios **and** orientation | realisation `H_A` | all four gates; G1 reads laboratory-frame elements | B1 table rows 2–3 |
| `n` | record length in samples | plan `generating_model.branch_b` | enters `N_ab`, hence every per-element variance | B1 table |
| `dt` | sampling interval | plan `generating_model.branch_b` | `phi_r = exp(-dt/tau_r)` | B1 table |
| `tau_modes` | per-mode relaxation times | realisation (`gamma/k_r`) | `phi_r` | B1 table |
| `phi_modes` | `exp(-dt/tau_r)` | derived, cross-checked | `N_ab` | B1 table |
| `mode_blocks` | G3 resolvability partition | derived from the four above + `theta_cap` | G3 is evaluated per block | B1 table |
| `theta_cap_deg` | resolvability cap | plan `adopted_rules_unchanged` | determines `mode_blocks` | B1 table |
| `alpha_1` | Block-1 allocation | plan `adopted_rules_unchanged` | determines the stored critical `p_min` | design §5 |
| `replicates` | `R_cal` | plan `calibration.replicates` | resolution of the empirical null | B1 table |
| `gates` | `(G1,G2,G3,G4)` | frozen constant | the set `p_min` minimises over | B1 table |
| `calibrator_identity` | which generator produced the draws | `GENERATOR_IDENTITY` | a different generator is a different null | B1 table |
| `procedure_identity` | analysis procedure identity | binding | authority provenance | plan `calibration.binds_to` |
| `contract_sha256` | design contract digest | binding | authority provenance | plan `calibration.binds_to` |
| `plan_sha256` | validation plan digest | binding | authority provenance | plan `calibration.binds_to` |

**Confirmed absent from the preimage:** `viscosity`, `bead_radius`, `gamma`,
`branch_a_evidence_sha256`. The reported fact is accurate: the preimage carries the
relaxation/correlation information but not the primitives and not the publication digest.

---

## 5. The earlier calibration-identity repair — what invariant was actually adopted

The repair is commit `5727e10`, documented at `docs/e1a/E1A_V4_PREEXEC_REPAIR_REPORT.md`
§B1 and frozen into the plan at `calibration.condition_binding`.

The adopted invariant, in the plan's and the commit's own words:

> `CalibrationCondition`, **which binds every input that changes the null law** and
> documents, with reasons, the ones it deliberately does not.

and in `e1a_v4/calibration.py`:

> Every input that changes the Block-1 null law, **and nothing that does not.**

So the adopted rule is **neither** of the two candidates section 7 of the brief offers as
examples. It is not "bind every physical quantity"; it is not "bind the exact Branch-A
publication". It is:

```
ARTIFACT IDENTITY BINDS EXACTLY THE INPUTS THAT CHANGE THE NULL LAW,
PLUS field_id AS A NAMED FAIL-SAFE, AND EXPLICITLY NOTHING ELSE.
```

The "explicitly nothing else" half is not incidental — it is enumerated. The plan's
`condition_binding.not_bound` map gives a reason for each exclusion, and every reason is
of the same form: *this quantity does not change the null law, or is exactly determined by
something already bound.*

```
T_total   : "exactly n * dt"
N_ab      : "exactly determined by (phi_modes, n); the primitives are bound instead,
             which is strictly stronger"
rank_tol  : "never read on the calibration path"
alpha_2   : "block 2 only"
sigma_k / sigma_cm / sigma_psi / sigma_T : "the calibrator never reads them"
```

A further explicit statement, from `calibration.artifact_identity_fields`, is the closed
list of what identifies an artifact in the campaign manifest:

```
case_id, replicate_id, field_id, calibration_condition_sha256, artifact_sha256,
analysis_procedure_identity, contract_sha256, calibrator_identity, R_cal, alpha_1,
calibration_seed_identity, artifact_schema
```

**No Branch-A evidence digest appears.** Package provenance is carried by
`(case_id, replicate_id, field_id)` — the coordinate — not by the package hash.

---

## 6. The theta0 / theta1 precedent — why it was invalid

The brief asks whether the superseded `theta0 -> theta1` reuse was invalid because the
null distribution differed or merely because publication identities differed. Authority
answers without ambiguity: **the null distribution differed.**

From the B1 report:

| | `theta0_circular` | `theta1_power` |
|---|---|---|
| `k` (µN/m) | 100, 100 | 210, 210 |
| `tau` (s) | `1.6776e-04` | `7.9886e-05` |
| `phi` | `0.4890439` | `0.2226539` |
| `N_11` | `1,227,983` | `1,811,067` |
| geometry signature | `d806758364fe1d5f…` | `d806758364fe1d5f…` — **same** |

> **Effective sizes differ by `1.4748x`, and the superseded check could not see it.**

And the plan states the basis of the standing prohibition in terms:

> `global_reuse_prohibition.basis`: **"MATHEMATICAL, not merely provenance: the Block-1
> null law moves with the realised `H_A`"**
> `global_reuse_prohibition.insufficient`: `["a matching field name", "a nominal H", "an eigenvalue ratio"]`
> `global_reuse_prohibition.required`: **"the complete repaired `CalibrationCondition` must match"**

The B1 dependency table classifies `field_id` as **"changes null law? no"**, bound only
"as provenance and fail-safe isolation". The implementation docstring is blunter:

> `field_id` …… provenance and fail-safe isolation. **NOT the mathematical protection:
> two fields may share a name and differ in law, or differ in name and share one.**

That last clause — *differ in name and share one* — is authority explicitly contemplating
two distinct objects with one null law. The theta0/theta1 precedent therefore **supports
condition-equivalence**, and cannot be cited for package-identity binding.

---

## 7. Null-law dependency: do `eta` and `a` enter anywhere else?

Traced from the declared generator and the declared synthetic model, by reading the code,
not by sampling.

**Readers of `viscosity` / `bead_radius` in the whole package:**

| module | occurrences | nature |
|---|---|---|
| `e1a_v4/branch_a.py` | 11 | definition, G6 domain check, `gamma`, `tau_modes`, `blinded` pass-through |
| `e1a_v4/validation/generate.py` | 1 | pass-through only — `BranchAErrorModel.measure` copies both unchanged |
| `e1a_v4/validation/campaign_driver.py` | 29 | persistence, authority table, recovery, invariants — no science path |
| `e1a_v4/validation/coherence.py` | 1 | a comment |

`BranchAErrorModel.measure` perturbs `k_modes`, `rot_deg`, `T` and the common-mode scale.
It does **not** perturb `eta` or `a`, and it does not recompute `eta(T)` from the measured
temperature — that model is F4 and undeclared.

**The chain into the null law:**

```
eta, a  ->  gamma = 6 pi eta a  ->  tau_r = gamma / k_r  ->  phi_r = exp(-dt/tau_r)
        ->  N_ab(phi_a, phi_b, n)  ->  per-element variance of the surrogate S  ->  G1..G4
```

`surrogate_covariance_draw(H_A, n, phis, rng)` reads `H_A`, `n`, `phis`. `generate_block1_artifact`
additionally reads `replicates` and `mode_blocks`. `World` reads `field.tau_modes` and
`field.H`; `truth_from_field` reads `field.H` and `field.tau_modes`. None of these reads
`viscosity` or `bead_radius`.

There is no second path: no diffusion constant, no mobility, no Reynolds or Péclet
quantity, no uncertainty model keyed on `eta` or `a` anywhere in the declared procedure.

**NO INDEPENDENT NULL-LAW EFFECT FOUND.**

A corollary worth stating explicitly, because it changes the character of the finding:
since the calibration seed is also independent of `eta` and `a`, the official driver
produces a **bit-identical** artifact for packages A and B. The two packages do not merely
share a null law — at a fixed coordinate they share the artifact itself.

---

## 8. `A -> CalibrationCondition` provenance — derive, or embed?

The brief asks which of two readings this rule carries. The plan answers directly, under
`driver_requirements.branch_a_provenance`:

> `closed_by_this_adoption`: "condition-consistency enforcement: the lock refuses an
> absent or mismatched separately supplied realised condition"
> `NOT_closed`: "end-to-end Branch-A provenance enforcement"
> `why`: "matching a separately supplied condition is not, by itself, proof that the
> condition came from that replicate's actual Branch-A measurement. A caller passing a
> copy of the artifact's own condition still satisfies the check."
> `requirement`: **"the official campaign driver MUST construct the realised
> `CalibrationCondition` mechanically from its OWN Branch-A measurement result, and that
> construction must itself be audited. Until then this is enforcement of consistency, not
> of provenance."**

The stated remedy is **construction**, not **embedding**. Authority requires the condition
to be *derived from* the realisation; it nowhere requires the realisation's identity to
appear *inside* the condition.

The implementation satisfies the stated remedy. `BranchARealisation.calibration_condition`
is a function of the realisation and the frozen plan alone — the caller supplies no `H`,
no `n`, no temporal law and no identity — and `JobExecution.calibration_condition` derives
it from the published object rather than accepting an argument. The plan's declared
provenance chain agrees:

> `calibration_scope_disposition.chain`: `H_true,theta -> H_A,theta,r -> C_theta,r -> Branch-B analysis_theta,r`

The condition hangs off `H_A`, not off the package.

**A -> CONDITION PROVENANCE AUTHORITY: DERIVE THE CONDITION VALUES FROM A. NOT EMBED A's IDENTITY.**

---

## 9. Lock provenance

`calibration_lock_envelope` writes, as one sealed object:

```
branch_a_evidence_sha256     <- copied FROM the committed publication
publication_basename         <- derived from the coordinates
publication_digest           <- copied FROM the committed publication
calibration_condition_sha256 <- the condition derived from that published evidence
calibration_artifact_sha256  <- the locked artifact
artifact_field_id, artifact_schema, artifact_replicates, artifact_alpha_1
analysis_procedure_identity
package_identities { contract, plan, seed_map, analysis, execution }
lock_digest                  <- sealed_digest over all of the above
```

`verified_calibration_lock` then requires the lock's `branch_a_evidence_sha256`,
`publication_digest` and `calibration_condition_sha256` all to equal the **verified**
committed publication's, resolved from the job's canonical coordinate slot and not from a
caller argument.

So lock validity guarantees **both** halves of the brief's section-13 question:

```
artifact matches condition          AND     artifact use is bound to the exact
                                            Branch-A publication, by its evidence digest
```

And under schema `/3` that evidence digest contains `viscosity` and `bead_radius` inside
the hashing preimage. The lock's package binding is therefore **exact today** — this is
precisely what F2e changed. Before F2e the evidence digest could not distinguish
`eta<0, a<0` from a legitimate pair; now it distinguishes any two distinct primitive pairs.

**LOCK PROVENANCE AUTHORITY: THE LOCK BINDS THE EXACT BRANCH-A PACKAGE, AND ALREADY DOES.**

---

## 10. Terminal provenance

`docs/e1a/E1A_V4_TERMINAL_CALIBRATION_PROVENANCE_REPORT.md` §3.1 records the chain the
repair adopted:

```
committed Branch-A publication
      -> the CalibrationCondition derived from that published evidence
      -> the artifact calibrated at that condition, and LOCKED
      -> the terminal record that names it
```

and §3.2:

> the lock's condition, evidence hash and publication digest must equal the committed
> publication's; the locked artifact's field must be this job's field; and the lock's
> package identities must be the current ones.

Read precisely, hop 2 is a **derivation** requirement — "the condition derived from that
published evidence" — not an injectivity requirement. A condition that is derivable from
the published evidence satisfies it, and the auditor's condition is derivable from package
B's published evidence (and, separately, from package A's).

The report also states where the chain terminates:

> the lock record, not the artifact, is the terminus of the chain.

That is the layering answer: the artifact is not asked to carry package identity, because
the lock record is the object that does.

**TERMINAL PROVENANCE AUTHORITY: TRACE TO THE EXACT ACTUAL BRANCH-A PUBLICATION, VIA THE
LOCK RECORD — SATISFIED.**

---

## 11. Candidate-rule comparison

### Rule A — exact-package binding in the condition / artifact identity

> Every `CalibrationCondition` / calibration artifact must bind the exact Branch-A evidence
> digest. Two physically equivalent packages with different primitive provenance still
> require different calibration identities/artifacts.

**CONTRADICTS AUTHORITY.**

- `calibration.condition_binding.bound` is a **closed 15-item enumeration**. No evidence
  digest, no `eta`, no `a`. The companion `not_bound` map gives a reason for each exclusion,
  and every reason is "does not change the null law" or "exactly determined by something
  already bound". Rule A does not fit that organising principle and cannot be adopted
  without amending the frozen plan.
- `calibration.artifact_identity_fields` is likewise closed and carries no evidence digest.
- `calibration_scope_disposition.chain` routes the condition through `H_A`, not the package.
- `global_reuse_prohibition.basis` is declared **"MATHEMATICAL, not merely provenance"**,
  and `.required` is "the complete repaired `CalibrationCondition` must match".
- The B1 invariant is "every input that changes the null law, **and nothing that does not**".

Rule A is not merely unrequired; adopting it would require a prospective amendment to
frozen authority, would move `calibration_condition_sha256` for every artifact, and would
contradict the stated basis of the existing prohibition.

### Rule B — scientific-condition binding, as stated

> Calibration identity depends only on the complete declared condition. Two different
> Branch-A packages may legitimately share an artifact **if and only if** their complete
> `CalibrationCondition` is identical.

**CONTRADICTS AUTHORITY — the "if" half only.** The "only if" half is REQUIRED.

Condition identity is **necessary but explicitly not sufficient**. The plan's
`limited_reuse_rule` requires four conditions, *all* of them:

```
1. the frozen case definition explicitly holds the calibration condition fixed
   across the relevant analyses
2. the complete CalibrationCondition digest is identical
3. the plan explicitly classifies that shared calibration as part of the case design
4. the resulting dependence is compatible with the statistical quantity being estimated
```

with

```
no_implicit_cache: "no cache-based reuse is permitted merely because two digests happen
                    to match. CampaignCalibrationLedger refuses a digest already locked
                    to a different (case, replicate, field) under REPLICATE_CONDITIONAL."
default:           "independent replicate-specific calibration for every repeated-
                    experiment operating-characteristic case"
cases_using_CASE_FIXED: []
```

`cases_using_CASE_FIXED` is **empty**. No case in the frozen plan declares shared
calibration, so no reuse is authorised anywhere in the current campaign, whatever the
digests say. Rule B's biconditional would authorise exactly the implicit sharing the plan
forbids by name.

### Rule C — shared condition plus exact lock provenance

> `CalibrationCondition` may be shared across scientifically identical packages, but the
> calibration lock / terminal provenance must separately bind the artifact use to the exact
> Branch-A package.

**REQUIRED — and already satisfied.** Authority chain:

| step | authority |
|---|---|
| the condition is the null law, and binds exactly that | plan `calibration.condition_binding`; B1 repair `5727e10`; `global_reuse_prohibition.basis` "MATHEMATICAL, not merely provenance" |
| `eta`/`a` reach the null law only through `gamma -> tau -> phi` | design §3.1 "`gamma` and `tau` are DERIVED"; contract `derived_quantities.*.independent_rule: false`; dependency trace, section 7 |
| the condition must be **constructed from** the job's own Branch-A result | plan `driver_requirements.branch_a_provenance.requirement` |
| artifact use is bound to the exact publication at the lock | lock envelope + `verified_calibration_lock`; terminal-provenance chain |
| that binding is exact for the primitives | schema `/3` places `viscosity` and `bead_radius` inside the evidence preimage (F2e) |
| sharing is never implicit | `limited_reuse_rule`, `no_implicit_cache`, `CampaignCalibrationLedger`, `cases_using_CASE_FIXED: []` |

### Rule D — unspecified

**CONTRADICTS AUTHORITY.** Authority decides the question; sections 5, 6, 8, 9 and 11 give
the chain. Rule D does not apply.

---

## 12. The structural answer: this is an F4 artefact, not a calibration-identity gap

The auditor's scenario requires two *different admissible* `eta`/`a` packages to be
simultaneously constructible as official Branch-A inputs at one coordinate. Today they are,
because `eta` and `a` are free arguments to `build_field` — F4 is OPEN, and design §3.1
says so in terms:

> **What this does not declare.** The actual dynamic viscosity values, the viscosity model
> `eta(T)`, the actual bead radius … Those remain **F4 — field construction / absolute drag
> inputs**, which is **OPEN**.

But authority does not leave them free. The contract's own disposition for an undeclared
input states the lifecycle:

> `the Branch-A field construction inputs must be declared in frozen authority, and thereby
> enter the execution identity, BEFORE the seal is frozen`

And `CalibrationCondition` already binds `contract_sha256`. Demonstrated directly:

```
TODAY   (eta/a free arguments, one contract digest)
  condition A = 4aa86af9709ef96bd12ca54ae817f95d0fff50d0138c6e1a4622534efad778bd
  condition B = 4aa86af9709ef96bd12ca54ae817f95d0fff50d0138c6e1a4622534efad778bd      EQUAL

AFTER F4 (eta/a declared in frozen authority, so the contract digest moves with them)
  condition A' = ba56b7b3096275acbebbcf30f820d965e875068f4150707dcdc8d887941b35ae
  condition B' = f92d1931651093dc9a5a3f6b883bb75c5163596164f9bf1172c350995fd90236   NOT EQUAL
  first_difference = 'contract_sha256'
```

So the transplant is not reachable in an officially sealed campaign: two distinct declared
packages are two distinct contracts, hence two distinct analysis identities, two distinct
conditions, and two distinct everything downstream. **The right place to close the
auditor's scenario is F4, where authority already puts it — not the calibration condition.**

This is also why Rule A would be the wrong repair: it would duplicate, inside the null-law
identity, a separation that frozen authority already guarantees one layer up, and it would
do so by contradicting the enumerated binding the B1 repair adopted.

---

## 13. Section 17 / 18 — the double-negative direct condition construction

### What reproduces

```
BranchAField(eta=-8.9e-4, a=-1e-6).status      = 'BRANCH_A_INVALID'   (G6 fires correctly)
  .gamma = 1.6776104770169493e-08  (> 0)
  .tau   = (0.00016776104770169494, 0.00016776104770169494)

BranchARealisation.from_branch_a_field(...)    -> branch_a_status = 'BRANCH_A_INVALID'
BranchARealisation.calibration_condition(...)  -> CONSTRUCTS 4aa86af9709ef96b...
```

The constructed condition digest is **byte-identical to the legitimate packages A and B**,
because the condition sees only `tau`, which is positive.

### What blocks it

| path | result |
|---|---|
| `JobExecution.realise_branch_a` (official production) | **REFUSED** `BranchAMeasurementInvalid` — the F2e primitive gate |
| `require_branch_a_measurement_invariants` (official recovery / `verified_publication`) | **REFUSED** `BranchAMeasurementInvalid` — the F2e `PRIMITIVE_DRAG_DOMAIN` invariant |
| publication, lock, unblind | unreachable, since no realisation and no publication exist |

### Classification

This is **an intentionally low-level constructor operating on already-validated
parameters**, not a reachable authority or runtime defect. No official or restart path can
reach it without passing a primitive-domain check first. `CalibrationCondition` itself is a
*derived* object: its own `__post_init__` validates only its own inputs (dimensions, `n`,
`dt > 0`, `tau > 0`, `phi == exp(-dt/tau)`, block partition), and it never receives `eta` or
`a`. Under the repository's layering, `e1a_v4/calibration.py` is a SCIENTIFIC_MODULE
expressing the null law; primitive admissibility belongs upstream, in `branch_a.py` and the
validation layer, which is where F2e put it.

**Recorded tension, not repaired here.** Design §3.1 says a present-but-inadmissible
primitive "can NEVER yield … a valid calibration condition". The bridging method
`BranchARealisation.calibration_condition` — which is in the VALIDATION layer, not the
scientific one, and already carries a coded `tau` guard — still constructs a condition from
a realisation whose own `branch_a_status` is `BRANCH_A_INVALID`. A one-line status or
primitive-domain guard there would make the design sentence true of the constructor as well
as of the lifecycle. That is an implementation hardening with no authority change and no
analysis-identity movement, and it is **deliberately left for the repair stage**, as this
task is read-only.

---

## 14. C7/C8 downstream numerical gating — recorded only

Independently confirmed here rather than relayed, with pure fixtures:

```
C7_false_bridge          eta = a = 5e-324   requires_calibration = False
  field.status = 'VALID'   gamma = 0.0   tau = (0.0, 0.0)
  realise_branch_a      -> ACCEPTED
  publish_branch_a      -> PUBLISHED
  verified_publication  -> REFUSED  BRANCH_A_MEASUREMENT_INVALID
  unblind               -> UNBLINDED        [Branch B released]

C8_blinded_scale_control eta = a = 5e-324   -- identical behaviour

C7_false_bridge          eta = a = 1e300
  publish_branch_a      -> REFUSED (canonical_float refuses inf)
```

Production publishes and unblinds a record that the strict recovery verifier refuses.
Because C7 and C8 require no calibration, the `calibration_condition` guard that catches the
same condition for Block-1 cases is never reached on their path. The overflow direction is
already closed at publication; the **underflow** direction is not.

```
C7/C8 DOWNSTREAM NUMERICAL GATING: CONFIRMED IMPLEMENTATION DEFECT
```

Not repaired in this task, and no human scientific decision is required for it — the
production/recovery disagreement is a defect against an already-adopted rule.

---

## 15. Final disposition

```
DISPOSITION C — SHARED CONDITION + EXACT LOCK PROVENANCE

CALIBRATION CONDITION:
MAY BE SHARED

LOCK / TERMINAL USE:
MUST BIND EXACT BRANCH-A PACKAGE

NEW HUMAN SCIENTIFIC DECISION REQUIRED:
NO
```

**Authority chain, exactly:**

1. `e1a_v4_synthetic_validation_plan.json` → `calibration.condition_binding` — a closed
   15-item `bound` list and a reasoned `not_bound` map. The adopted invariant is "every
   input that changes the null law, and nothing that does not."
2. `E1A_V4_PREEXEC_REPAIR_REPORT.md` §B1 + commit `5727e10` — the theta0/theta1 defect was
   invalid **because the null law differed by 1.4748x**, not because publication identities
   differed; `field_id` is classified "changes null law? no" and bound only as a fail-safe.
3. `calibration.global_reuse_prohibition.basis` — "**MATHEMATICAL, not merely provenance**";
   `.required` — "the complete repaired `CalibrationCondition` must match".
4. Design §3.1 and contract `branch_a_measured_input_domain.derived_quantities` —
   `gamma` and `tau` are DERIVED, `independent_rule: false`; `eta` and `a` reach the
   procedure only through them. Dependency trace confirms no second path.
5. `calibration.calibration_scope_disposition.chain` — `H_A -> C -> Branch-B analysis`.
   The condition hangs off the realised `H_A`.
6. `driver_requirements.branch_a_provenance.requirement` — the driver must **construct** the
   condition from its own Branch-A result. Derivation, not embedding.
7. Lock envelope + `verified_calibration_lock` + terminal-provenance chain — artifact use is
   bound to the exact committed publication by `branch_a_evidence_sha256`, which under
   schema `/3` contains `eta` and `a`.
8. `calibration.limited_reuse_rule` + `CampaignCalibrationLedger` +
   `cases_using_CASE_FIXED: []` — sharing is never implicit, and no case currently declares
   it, so condition equality authorises nothing on its own.

**Does terminal provenance need any separate exact-package binding beyond what exists?** No.
It already binds the exact publication, and F2e made that binding exact at the primitive
level. The one remaining gap in this area is F4, not calibration identity.

**What this reconstruction does not do.** It does not clear F2; it resolves one of the two
F2f blockers as "no defect, authority decides it" and independently confirms the other as a
real implementation defect. It authorises no execution, freezes no seal, and repairs
nothing.

---

## 16. Execution state

```
OFFICIAL CAMPAIGN            NOT RUN
OFFICIAL RESULTS             NONE          (results/e1a_v4_validation does not exist)
SCIENTIFIC RNG DRAWS         0
OFFICIAL TRAJECTORIES        0
CALIBRATION EXECUTIONS       0
CAMPAIGN JOBS                0
FINAL EXECUTION SEAL         NOT FROZEN    (seal state PRE_DRIVER)
EXECUTION AUTHORISED         FALSE
TRAJECTORY INTEGRATION       DEFERRED / NOT RUN
```

**Validation run from the current tree, with nothing changed:**

```
4,002 checks, 0 failures, 17 suites, 0 suite(s) not clean
static preflight: PASSED

contract sha256             d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4
design sha256               25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6
plan sha256                 fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4
seed map sha256             c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af
analysis procedure identity 60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527
unsealed execution identity 442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b
```

Every identity is unchanged from the F2e coordinate. No seed was drawn.

**Standing open items, unchanged by this task:** F2 NOT YET CLEARED (C7/C8 gating, and the
section-13 constructor hardening); F3–F8 OPEN; F4 OPEN and now identified as the correct
home for the auditor's package-separation concern; the trajectory-bearing campaign-driver
integration suite remains deferred and was not run.
