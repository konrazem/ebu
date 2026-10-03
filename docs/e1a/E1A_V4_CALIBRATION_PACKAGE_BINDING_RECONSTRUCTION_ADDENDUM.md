# E1a v4 — CALIBRATION PACKAGE BINDING: CORRECTIVE ADDENDUM

**REPORT-ONLY.** No authority file, no implementation file and no test changed. No
scientific RNG, no calibration draw, no trajectory, no campaign job.

**Corrects:** `docs/e1a/E1A_V4_CALIBRATION_PACKAGE_BINDING_AUTHORITY_RECONSTRUCTION.md`,
commit `9ada9017941ef1ff88aebb02efa1b1ca092378d8`.

The original reconstruction is **not rewritten and not amended**. It remains part of the
scientific record exactly as committed. This addendum sits above it: where the two
disagree, **this addendum controls**, and the corrected statements are marked below.

| coordinate | value |
|---|---|
| corrected report | `9ada9017941ef1ff88aebb02efa1b1ca092378d8` |
| starting HEAD for this addendum | `9ada9017941ef1ff88aebb02efa1b1ca092378d8` |
| branch | `gaussian/stage-a-environment` |
| working tree at start | clean |

---

## 1. Reason for correction

An independent audit **supports the central disposition** of the reconstruction:

```
CALIBRATION PACKAGE BINDING:
SHARED CONDITION + EXACT LOCK PROVENANCE

NEW HUMAN SCIENTIFIC DECISION REQUIRED:
NO
```

It did not clear the report as written, for two reasons. Both are accepted here.

| # | defect | where | correction |
|---|---|---|---|
| 1 | **unsupported F4 claim** — the report asserted that once F4 closes, two distinct realised `eta`/`a` packages *necessarily* carry distinct contract digests and therefore distinct calibration conditions | §1 summary; §12 in full; §11 Rule-A rationale ("a separation that frozen authority already guarantees one layer up") | §2 below |
| 2 | **overstated constructor classification** — the report classified the direct invalid-realisation condition construction as an *intentionally low-level constructor operating on already-validated parameters*, i.e. as an authorised API boundary | §13 heading "Classification"; §1 summary table | §8 below |

A third, smaller imprecision is corrected in passing: the reconstruction's §4 table
presented all **17** `canonical()` keys in one list under an "authority" column, which
reads as though all 17 are independently bound scientific inputs. They are not. See §4.

Everything else in the reconstruction stands: the two-package reproduction, the null-law
dependency trace, the θ0/θ1 reading, the `A -> condition` derivation finding, the lock and
terminal provenance findings, the Rule A / Rule B / Rule C classification, and the
independently confirmed C7/C8 defect.

---

## 2. Corrected F4 statement

### 2.1 What the reconstruction claimed

> **AFTER F4** (`eta`/`a` declared in frozen authority, so the contract digest moves with
> them) … So the transplant is not reachable in an officially sealed campaign: two distinct
> declared packages are two distinct contracts, hence two distinct analysis identities, two
> distinct conditions, and two distinct everything downstream.

### 2.2 Why that is not supported

The demonstration offered for it proved a weaker proposition than the one asserted. It
substituted two **fabricated** contract digests (`"a"*64`, `"b"*64`) into the realisation
and observed that the conditions then differ, with `first_difference = 'contract_sha256'`.
That establishes only:

```
IF two official packages carry different contract digests
THEN their CalibrationConditions differ.
```

It does **not** establish the antecedent. Nothing in current authority says that two
distinct *realised* `eta`/`a` pairs must carry two distinct contract digests. The report
supplied the antecedent by assumption — specifically, by assuming F4 will declare `eta` and
`a` as fixed per-field scalars frozen into the contract.

Authority does not say that, and the repository contains a direct counter-pattern. The
frozen generating model already realises Branch-A primitives **stochastically per
replicate under one contract digest**:

> `generating_model.branch_a`:
> `"model": "H_A = decorated H_true; its OWN seed family branch_a_measurement"`,
> `"per_mode_stiffness": "independent per mode"`, `"orientation": "trap-axis psi"`,
> `"thermometry": "T measured with sigma_T"`

`BranchAErrorModel.measure` perturbs `k_modes`, `rot_deg` and `T` from declared sigmas, so
two replicates under one frozen contract already realise different measured stiffness,
orientation and temperature. And the contract's own `values_not_set` list leaves exactly
the parallel knobs for the drag primitives undeclared:

> `not_declared_here`: `["the actual dynamic viscosity values", "the viscosity model eta(T)",`
> `"the actual bead radius", "measurement uncertainty for eta", "measurement uncertainty for a",`
> `"hardware provenance for those values"]`
> `remaining_open_item`: `"F4 - field construction / absolute drag inputs"`, `status: "OPEN"`

If F4 declares a measurement model with uncertainty for `eta` or `a` — the direct analogue
of the existing `sigma_k`, `sigma_psi_deg` and `sigma_T` — then realised `eta`/`a` pairs
vary **within one frozen contract digest**, and the auditor's two-package situation becomes
constructible inside a single officially sealed campaign. The reconstruction's §12 excluded
that possibility without authority.

### 2.3 The accurate statement

```
F4 remains responsible for declaring the official field-construction inputs and the
measurement source/model before execution.

Current authority does NOT establish that every distinct realised eta/a pair must produce
a different contract digest or a different CalibrationCondition.

A frozen F4 measurement model may in principle permit different realised values under one
contract, depending on the eventual authorised construction.
```

### 2.4 Consequence

**The exact-package provenance guarantee must not be justified by assumed contract-digest
separation.** Any sentence in the reconstruction that rests on that assumption is withdrawn,
including:

- §12 in full, as the structural argument it presents;
- the §1 summary line "the auditor's two packages can only coexist *because F4 is open*";
- the clause in §11 (Rule A) reading "a separation that frozen authority already guarantees
  one layer up".

The Rule A classification itself — **CONTRADICTS AUTHORITY** — does **not** depend on the
withdrawn argument. It rests independently on the closed enumerations in
`calibration.condition_binding.bound` (15 items) and `calibration.artifact_identity_fields`
(12 items), on the B1 invariant "every input that changes the null law, and nothing that
does not", and on `global_reuse_prohibition.basis` being declared "MATHEMATICAL, not merely
provenance". That classification stands.

---

## 3. The real exact-package guarantee

The guarantee does not come from F4 and does not come from the calibration condition. It
comes from the existing downstream provenance chain, which is in force today. Verified
against the implementation rather than paraphrased:

**Step 1 — the lock copies the actual publication's identities, not the caller's.**
`calibration_lock_envelope` writes:

```python
"branch_a_evidence_sha256": publication["branch_a_evidence_sha256"],
"publication_digest":       publication["publication_digest"],
"calibration_condition_sha256": condition.sha256,
"calibration_artifact_sha256":  artifact_sha256,
...
record["lock_digest"] = sealed_digest(record, "lock_digest")
```

and `publish_calibration_lock` obtains that `publication` from `verified_publication`, not
from its caller — so a lock cannot cite evidence that was never published.

**Step 2 — `verified_calibration_lock` checks the lock against the actual committed
publication.** It resolves the publication itself from the job's canonical coordinate slot
and requires equality on all three provenance keys:

```python
for key, category in (("branch_a_evidence_sha256", "Branch-A evidence hash"),
                      ("publication_digest",       "publication digest"),
                      ("calibration_condition_sha256", "calibration-condition identity")):
    if lock.get(key) != publication.get(key):
        raise CalibrationLockProvenanceMismatch(...)
```

**Step 3 — terminal verification resolves that verified lock.** `validate_job_record` is
"THE OFFICIAL terminal-record validator. It obtains its own provenance … A caller …
supplies NO provenance object: not the Branch-A publication, not the calibration lock, not
an expected artifact digest". It calls `verified_publication` and `verified_calibration_lock`
itself, then `_compare_terminal_to_verified_lock`, which checks the complete chain

```
publication -> condition -> locked artifact -> terminal record
```

together rather than as four unrelated fields.

**Step 4 — the evidence digest is exact at the primitive level.** Branch-A publication
schema `/3` places `viscosity` and `bead_radius` inside the hashing preimage, so
`branch_a_evidence_sha256` distinguishes any two distinct primitive pairs. This is what F2e
changed.

```
Therefore exact actual Branch-A publication provenance is preserved even when two different
Branch-A packages share the same CalibrationCondition.
```

This holds under present authority, with F4 open, and does not depend on any future F4
decision.

---

## 4. `CalibrationCondition` is a null-law identity

Unchanged from the reconstruction, restated with the §16 precision the audit asked for.

The plan's `calibration.condition_binding.bound` is a closed list of **15 scientific
condition items**:

```
field_id, H_normalised, n, dt, tau_modes, phi_modes, mode_blocks, theta_cap_deg,
alpha_1, replicates, gates, calibrator_identity, procedure_identity,
contract_sha256, plan_sha256
```

`CalibrationCondition.canonical()` emits **17** keys: those 15, plus two that have a
different role and are **not** items of the authority's bound inventory:

| key | role | not a bound scientific input because |
|---|---|---|
| `schema` | the artifact/condition **version tag**, `CALIBRATION_ARTIFACT_SCHEMA` | it declares which identity scheme is in force; the plan carries it separately as `calibration.artifact_schema`, not inside `condition_binding.bound` |
| `m` | the **derived mode count**, `len(H_A)` | it is a dimension of `H_normalised`, already bound; it is a structural consequence, not an independent declared input |

The reconstruction's §4 table should be read with that distinction. Calling all 17
"independently bound" would overstate the authority inventory.

The adopted invariant, from commit `5727e10` and frozen at
`calibration.condition_binding`, is unchanged:

> every input that changes the null law, **and nothing that does not**

with a reasoned `not_bound` map (`T_total` "exactly `n * dt`"; `N_ab` "exactly determined by
`(phi_modes, n)`"; `rank_tol` "never read on the calibration path"; `alpha_2` "block 2
only"; `sigma_k/sigma_cm/sigma_psi/sigma_T` "the calibrator never reads them").

**Null-law dependency result, preserved:**

```
ETA/A ENTER THE CALIBRATION NULL LAW INDEPENDENTLY OF THE CURRENT CONDITION:  NO
```

the only path being

```
eta, a  ->  gamma = 6 pi eta a  ->  tau_r = gamma / k_r  ->  phi_r = exp(-dt/tau_r)
        ->  N_ab(phi_a, phi_b, n)  ->  per-element variance of the surrogate S  ->  G1..G4
```

Once the complete bound condition is equal, no independent `eta`/`a` calibration dependency
was found. `BranchAErrorModel.measure` passes both primitives through unperturbed, and no
module outside `branch_a.py` (definition), `generate.py` (pass-through) and
`campaign_driver.py` (persistence and verification) reads them.

---

## 5. Limited reuse — condition equality is necessary, not sufficient

Preserved, and load-bearing. Identical `CalibrationCondition` does **not** automatically
grant artifact reuse. The plan's `calibration.limited_reuse_rule` requires, verbatim, all
four of:

```
1. the frozen case definition explicitly holds the calibration condition fixed across
   the relevant analyses
2. the complete CalibrationCondition digest is identical
3. the plan explicitly classifies that shared calibration as part of the case design
4. the resulting dependence is compatible with the statistical quantity being estimated
```

with

```
status:            "reuse is NOT categorically prohibited, but it is never implicit"
no_implicit_cache: "no cache-based reuse is permitted merely because two digests happen to
                    match. CampaignCalibrationLedger refuses a digest already locked to a
                    different (case, replicate, field) under REPLICATE_CONDITIONAL."
default:           "independent replicate-specific calibration for every repeated-experiment
                    operating-characteristic case"
```

**`cases_using_CASE_FIXED` is currently `[]`** — re-verified against the plan at this
commit. No case in the frozen plan declares shared calibration, so condition equality
authorises reuse nowhere in the current campaign.

The ledger enforces this mechanically. Reproduced in the original work: locking an artifact
to job `r0` and presenting the same artifact to job `r1` inside one campaign gives

```
CALIBRATION_REUSE_REFUSED: artifact 9a0f8a4c5babad57... is already locked to
('C2_geometry_false_rejection', 'sigma_psi_0p0', 0, 'theta0_circular')
```

even though the two conditions are byte-identical.

---

## 6. Two-package demonstration

Preserved exactly as independently verified, with pure deterministic fixtures and no draws.

```
Package A:   eta = 8.9e-4  = 0x1.d29dc725c3deep-11     a = 1e-6 = 0x1.0c6f7a0b5ed8dp-20
Package B:   eta = 4.45e-4 = 0x1.d29dc725c3deep-12     a = 2e-6 = 0x1.0c6f7a0b5ed8dp-19
```

| property | result |
|---|---|
| `eta_A != eta_B`, `a_A != a_B` | yes |
| same product | yes — exactly one binade apart, so halving and doubling are exact in binary64 |
| same `gamma` | **bit-exact**, `0x1.203616cc4437fp-26` |
| same `tau_modes` | **bit-exact**, `(0x1.5fd206d459465p-13, 0x1.5fd206d459465p-13)` |
| Branch-A evidence digests | **differ** — `1f265d6e…` vs `c642d45f…` |
| differing evidence preimage keys | exactly `['bead_radius', 'viscosity']`, nothing else |
| complete `CalibrationCondition` | **identical** — `4aa86af9…`, `first_difference` is `None` |
| calibration generator inputs at one coordinate | identical |
| calibration seed | identical — `ReplicateCalibration.calibration_seed` derives from `(CALIBRATION family, subcondition_id, replicate, field_id)` and never reads `eta`, `a`, `gamma` or `tau` |
| resulting artifact under the specified generator | **the same deterministic artifact** |

The final row is an **analytic result from the dependency graph**, obtained by reading
`generate_block1_artifact`, `surrogate_covariance_draw` and `calibration_seed`. No
calibration was generated to obtain it, and none is authorised in this stage.

> **Artifact equality here is scientific-condition equality, not substitution of Branch-A
> evidence.** The two packages do not merely share a null law; at a fixed coordinate the
> official driver would construct the identical artifact object for either. There is no
> package-A artifact that differs from the package-B artifact it would "replace".

---

## 7. Why the "transplant" does not substitute Branch-A provenance

The reconstruction's §3.4 is headed "The artifact transplants, at every layer" and
concludes "**CURRENT PACKAGE TRANSPLANT: REPRODUCED**". That wording is corrected here,
because read alone it suggests package A's Branch-A provenance can become package B's. **It
cannot, and does not.**

What was actually reproduced: a package-A-derived *artifact* is accepted by
`require_calibration`, `lock_calibration` and `verified_calibration_lock` for a job whose
published evidence is package B — because the condition they compare is identical.

What was **not** reproduced, and cannot be: any substitution of Branch-A evidence. In the
reproduction itself the resulting lock records **package B's** identities, copied from
package B's committed publication:

```
package A campaign   lock.branch_a_evidence_sha256 = 133b656afecc00c05057594c021e00cfde077556cf4425b026486ba438506b32
package B campaign   lock.branch_a_evidence_sha256 = cf735ac6161addadfbeeccf7736d1507768c5ffa126bbecd1a5bc23073d14b3d
differing lock keys  ['branch_a_evidence_sha256', 'publication_digest', 'lock_digest']
```

The lock for the package-B job cites package B's evidence hash and package B's publication
digest. Package A's provenance appears nowhere in it.

So the accurate characterisation is:

```
A calibration ARTIFACT may be shared between two Branch-A packages that induce the same
complete CalibrationCondition -- subject to the limited-reuse rule, which currently
authorises no sharing at all.

Branch-A PROVENANCE is never shared. The lock and the terminal record bind the exact actual
Branch-A publication of the experiment that was run.
```

---

## 8. Correction to the low-level constructor classification

### 8.1 What the reconstruction claimed

> **Classification.** This is **an intentionally low-level constructor operating on
> already-validated parameters**, not a reachable authority or runtime defect.

### 8.2 Why that is overstated

The audit found that current authority does not establish that classification. On review
this is correct: no authority document declares `BranchARealisation.calibration_condition`
to be a prevalidated API boundary, states that its caller owns primitive validation, or
exempts it from the design §3.1 sentence that a present-but-inadmissible primitive "can
NEVER yield … a valid calibration condition". The reconstruction derived the classification
from the repository's *layering* and from observed reachability, then stated it as a
settled property. Reachability evidence is not an authority classification.

Equally, it must not be called an implementation defect: no authority requires the
constructor to validate independently of its callers, so there is no adopted rule for it to
violate.

### 8.3 Corrected classification

```
LOW-LEVEL CONSTRUCTOR STATUS:
AUTHORITY UNSPECIFIED / CURRENT OFFICIAL PATH UNREACHABLE FOR INVALID REALISATION
```

### 8.4 Reachability evidence, which is what is actually established

Reproduced with pure fixtures, `eta = -8.9e-4`, `a = -1e-6`:

| path | result |
|---|---|
| `BranchAField(...)` | `status = 'BRANCH_A_INVALID'` — G6 fires correctly; `gamma = 1.6776104770169493e-08 > 0`, `tau > 0` |
| `BranchARealisation.calibration_condition(...)` called **directly** on that invalid realisation | **constructs** a condition, digest `4aa86af9…`, byte-identical to the legitimate one |
| `JobExecution.realise_branch_a` — official production | **REFUSES**, `BranchAMeasurementInvalid`, before this call is reached |
| `require_branch_a_measurement_invariants` via `verified_publication` — strict recovery | **REFUSES** the invalid publication, `BranchAMeasurementInvalid` |
| publication, lock, unblind | unreachable: no realisation and no publication exist |

```
No currently identified official path reaches the constructor with such invalid input.
```

### 8.5 No new human decision

Because every current official path refuses before the constructor, and because no authority
requires the constructor to be an independent validation boundary:

```
NEW HUMAN SCIENTIFIC DECISION REQUIRED:  NO    (for current F2 execution)
```

The residual is recorded as a **bounded API/authority observation only**. It is neither a
cleared design nor a defect. **If a future official or restart path is ever arranged to call
this constructor before primitive validation, the question must be revisited** — at that
point either authority must classify the boundary, or the constructor must validate.

---

## 9. Confirmed C7/C8 numerical-gating defect

Preserved unchanged. Independently confirmed with pure fixtures, not relayed:

```
C7_false_bridge           eta = a = 5e-324    requires_calibration = False
  field.status = 'VALID'    gamma = 0.0    tau = (0.0, 0.0)
  realise_branch_a      -> ACCEPTED
  publish_branch_a      -> PUBLISHED
  verified_publication  -> REFUSED   BRANCH_A_MEASUREMENT_INVALID
  unblind               -> UNBLINDED        [Branch-B unblind token issued]

C8_blinded_scale_control  eta = a = 5e-324    -- identical behaviour

C7_false_bridge           eta = a = 1e300
  publish_branch_a      -> REFUSED (canonical_float refuses inf)
```

Production publishes and issues the Branch-B unblind token for a record that strict
publication/recovery verification rejects, because the derived `gamma`/`tau` are unusable.
C7 and C8 require no calibration, so the `calibration_condition` guard that catches the same
state for Block-1 cases is never reached on their path. The overflow direction is already
closed at publication; the **underflow** direction is not.

```
C7/C8 NUMERICAL GATING DEFECT:
CONFIRMED

IMPLEMENTATION REPAIR REQUIRED
```

**Not repaired in this task.** No human scientific decision is required for it: it is a
production/recovery disagreement against an already-adopted rule.

---

## 10. F4 boundary

```
F4 remains responsible for the actual official eta/a construction, the measurement
source/model, and the associated provenance.
```

This addendum does **not** decide, and must not be read as deciding:

- the actual `eta` values;
- the actual `a` value;
- the viscosity model `eta(T)`;
- whether realised values vary under a frozen measurement model;
- measurement uncertainty for either primitive;
- hardware source or provenance.

All of those remain **F4 — field construction / absolute drag inputs, OPEN**, exactly as
design §3.1 and contract `branch_a_measured_input_domain.values_not_set` state. The
correction in §2 **removes** an assumption about F4's eventual content; it does not replace
it with a different one.

What §2 does establish is narrower and purely negative: the exact-package provenance
guarantee of §3 **does not depend on F4** and holds today with F4 open.

---

## 11. Final corrected disposition

```
CALIBRATION PACKAGE BINDING:
SHARED CONDITION + EXACT LOCK PROVENANCE

CALIBRATION CONDITION:
NULL-LAW EQUIVALENCE CLASS

CONDITION EQUALITY ALONE PERMITS REUSE:
NO

EXACT BRANCH-A PACKAGE EMBEDDED IN CONDITION:
NO / NOT REQUIRED BY AUTHORITY

CALIBRATION LOCK:
BINDS EXACT ACTUAL BRANCH-A PUBLICATION

TERMINAL PROVENANCE:
VERIFIES EXACT ACTUAL BRANCH-A PUBLICATION

F4 CONTRACT-DIGEST SEPARATION OF EVERY REALISED ETA/A PAIR:
NOT ESTABLISHED / NOT REQUIRED FOR THIS PROVENANCE GUARANTEE

DIRECT INVALID-REALISATION CONDITION CONSTRUCTION:
AUTHORITY UNSPECIFIED; CURRENT OFFICIAL PATH REFUSES BEFORE CALL

NEW HUMAN SCIENTIFIC DECISION REQUIRED:
NO

C7/C8 NUMERICAL GATING DEFECT:
CONFIRMED / IMPLEMENTATION REPAIR REQUIRED
```

### Neither extreme is adopted

| candidate | verdict |
|---|---|
| **A** — exact Branch-A package identity inside `CalibrationCondition` | **NOT ADOPTED.** Contradicts the closed `condition_binding.bound` (15 items) and `artifact_identity_fields` (12 items) enumerations, the B1 invariant, and `global_reuse_prohibition.basis` ("MATHEMATICAL, not merely provenance"). The earlier F2f criterion requiring it was **over-strong on this specific point**: `CalibrationCondition` is intentionally a null-law identity, not an exact Branch-A publication identity. The rest of that audit is unaffected, and its C7/C8 finding is confirmed. |
| **B** — unrestricted reuse whenever conditions match | **NOT ADOPTED.** Contradicts `limited_reuse_rule`, whose four conditions are all required, `no_implicit_cache`, and the ledger. `cases_using_CASE_FIXED` is empty. |
| **C** — shared condition + controlled reuse + exact lock/terminal provenance | **ADOPTED.** |

### Historical θ0/θ1 repair, preserved

Cross-use of a `theta0_circular` artifact for `theta1_power` was invalid **because the
calibration-relevant null law differed**, not merely because Branch-A package identities
differed. Verified from `E1A_V4_PREEXEC_REPAIR_REPORT.md` §B1 and commit `5727e10`: both
fields are isotropic, so their eigenvalue ratios are identical, while `tau = gamma/k` differs
by `2.1x` (`1.6776e-04` vs `7.9886e-05`), `phi` by `0.4890439` vs `0.2226539`, and the
per-element effective sizes by a factor of **`1.4748x`**. The superseded geometry signature
was identical for both (`d806758364fe1d5f…`). The B1 dependency table classifies `field_id`
as "changes null law? **no**", bound only "as provenance and fail-safe isolation", and
`e1a_v4/calibration.py` records that two fields "may share a name and differ in law, **or
differ in name and share one**". This precedent supports **null-law binding**, not
exact-package condition identity.

---

## 12. Identities and execution state

Report-only. Reports are outside every identity preimage, so no identity moved, and none was
artificially adjusted. Recomputed from an independent clean `git archive` extraction of the
addendum commit:

```
foundation sha256           6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507   UNCHANGED
baseline sha256             0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa   UNCHANGED
design sha256               25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6   UNCHANGED
contract sha256             d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4   UNCHANGED
plan sha256                 fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4   UNCHANGED
seed map sha256             c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af   UNCHANGED
analysis procedure identity 60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527   UNCHANGED
unsealed execution identity 442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b   UNCHANGED
```

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

Validation from the current tree, with nothing changed:

```
4,002 checks, 0 failures, 17 suites, 0 suite(s) not clean
static preflight: PASSED
```

**Standing open items, unchanged by this addendum:** F2 NOT YET CLEARED — the C7/C8
numerical-gating defect of §9 requires implementation repair, and the §8 constructor
residual is an unresolved authority question that is currently unreachable. F3–F8 OPEN.
F4 OPEN. The trajectory-bearing campaign-driver integration suite remains deferred and was
not run.
