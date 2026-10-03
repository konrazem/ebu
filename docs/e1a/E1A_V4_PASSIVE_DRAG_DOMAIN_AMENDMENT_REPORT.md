# E1a v4 — passive-drag domain authority amendment report (F2c)

Bounded prospective authority stage. The approved F2 rule is now explicit and
load-bearing in frozen authority. **No runtime implementation was performed.**

---

## Starting coordinate

```text
STARTING HEAD    a58e6bcf17192fdf1e2295581d664b3d21bbf338
STARTING TREE    92dc1e05d756a613113c9608978b9f7aac91c14c
WORKTREE         clean -- no tracked or untracked change, no unrelated book files
BRANCH           gaussian/stage-a-environment
```

```text
WORK COMMIT      0b7bf417c246fb03acc377fbf8fec7fd4ca874c6
WORK TREE        042c9b28c5534edd8b29615722c26a9d7bab75d5
```

The work landed in **two** commits, neither amended:

| commit | tree | content |
|---|---|---|
| `a8b8c815b0f96ef36650be29a5de138fa26ad02d` | `774eb965ebda2bab2fba8c20fd485ac93471d345` | the amendment itself |
| `0b7bf417c246fb03acc377fbf8fec7fd4ca874c6` | `042c9b28c5534edd8b29615722c26a9d7bab75d5` | three added nested-key regressions, test-only |

The second changed no authority document, no scientific module and no validation
module, so every identity below is identical at both commits — verified by
recomputing from clean `git archive` extractions of each.

The F2 reconstruction report `a58e6bc` established the gap this stage closes; the
integrated audited coordinate before it was `1bcdd58` / tree `76ffe15`.

---

## Status of this change

```text
OFFICIAL CAMPAIGN RESULTS OBSERVED   NO
FINAL EXECUTION SEAL                 NOT FROZEN   (state PRE_DRIVER)
EXECUTION AUTHORISED                 FALSE
OFFICIAL SYNTHETIC CAMPAIGN          NOT RUN
TRAJECTORIES                         0
SCIENTIFIC RANDOM DRAWS              0
CALIBRATION EXECUTIONS               0
OFFICIAL CAMPAIGN JOBS               0
```

`results/e1a_v4_validation` does not exist, in the working tree and in the
committed tree. No outcome has been inspected, so this rule is adopted without any
possibility of post-outcome tuning.

---

## Files changed

| file | role | why |
|---|---|---|
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | **authority** | new §3.1 states the rule normatively for humans; §14 gains a cross-reference distinguishing the three verdicts |
| `docs/e1a/e1a_v4_design_contract.json` | **authority** | new `branch_a_measured_input_domain`; version `1.1.0 -> 1.2.0`; rebound design digest and byte count |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | **authority** | one execution-facing restatement, disposition `G6`, preflight-check entry, version `1.15.0 -> 1.16.0`, rebound identities |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | **authority** | regenerated generated regions, identity rows, seed table, version line |
| `docs/e1a/e1a_v4_seed_map.json` | identity | rederived from the amended contract digest by its own committed algorithm |
| `docs/theory/EBU_THEORY_BASELINE.meta.json` | identity | sidecar records the new design hash, byte count, contract version and status |
| `e1a_v4/validation/drag_domain.py` | **new, binding** | the approved rule, pinned; renderers; totality, scope and F4 checks; the conformance entry point; pure domain predicates |
| `e1a_v4/contract.py` | schema loading | accept contract minor `1.2`; require the new section (fail closed on its absence) |
| `e1a_v4/validation/contract_plan.py` | binding | EXACT contract→plan row for the restatement; `DELEGATED_TO_DRAG_DOMAIN_AUTHORITY`; the section joins the leaf-totality sweep |
| `e1a_v4/validation/coherence.py` | binding | the restatement is classified `BOTH` and rendered in the generated section 4 |
| `e1a_v4/validation/plan.py` | binding | `bind_execution` calls the new check; the module joins `VALIDATION_MODULES` |
| `e1a_v4/validation/refusals.py` | codes | three coded refusals registered; 68 → 71 codes |
| `test_e1a_v4_drag_domain.py` | **new tests** | 151 checks, 77 of them coherent wrong-authority mutations |
| 9 earlier-stage suites + `e1a_v4_execution_feasibility_probe.py` | identity pins | repointed; see **Identity pins** below |

Not changed, deliberately: `EBU_PHYSICAL_FOUNDATION_CANONICAL.md`,
`EBU_THEORY_BASELINE.md`, `branch_a.py`, `campaign_driver.py`, `calibrate.py`,
`generate.py`, `endpoints.py`, `geometry.py`, `calibration.py`, `world.py`,
`effective_size.py`, `numerics.py`, `seeds.py`, `status.py`, `identity.py`,
`e1a_v4_execution_seal.json`, `test_e1a_v4_campaign_driver.py`.

---

## Authority placement

| candidate | authority it carries | does the rule belong here? |
|---|---|---|
| `E1A_V4_PROSPECTIVE_DESIGN.md` | E1a physical and refusal semantics; §14 already owns `REFUSED_BRANCH_A_INVALID`, §3 already owns the Stokes relation | **YES.** This is a physical-domain decision for one benchmark; the design is its normative human home |
| `e1a_v4_design_contract.json` | "the mechanical schema and ordering source" for the design; the two are a normative pair whose mismatch is an integrity failure | **YES.** A rule stated only in the Markdown would break the pair. The contract is the machine authority for E1a decision rules, per baseline §14 |
| `E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` / `.json` | execution-facing representation; ranks **below** the contract | **RESTATEMENT ONLY.** The plan may not create a design-level physical rule. It carries one derived rendering, bound EXACT to the contract, plus the prospective disposition record |
| `EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | the frozen finite EBU theorem | **NO.** It mentions positive-definiteness only as a *premise of a theorem*, never as a measurement-domain rule, and E1a makes no universal viscosity claim |
| `EBU_THEORY_BASELINE.md` | working theory; Gaussian Level-1 physics | **NO.** Same reasoning. Its **sidecar** records the new design hash, exactly as at the G1–G3 adoption `1a0c00e` |
| verifier code alone | — | **NO.** The rule is in frozen authority; code holds the *expected* rendering so the authority cannot validate itself |

### Disposition numbering

The plan's `authority_gaps` convention is a sequential `G1 … G5`, each with
`id / gap / affects / status / resolution`, rendered into the generated
release-rules region. `G6` continues that sequence. `G4` is the C3/C4 per-field
size amendment and is scientifically unrelated; it was not reused. `G6` records
`affects: Branch-A field construction, every case`, which is honest — unlike
G1–G5 this is not a per-case validation gap.

---

## The scientific decision

```text
eta(T_theta) in R ,   0 < eta(T_theta) < infinity        Pa s
a            in R ,   0 < a            < infinity        m
```

Both **required**, both **finite**, both **strictly** positive, both bound
**individually**. "Finite real" excludes NaN, `+infinity` and `-infinity`, and
excludes truthy or non-numeric representations — `bool` subclasses `int`, so a
flag is not a measurement and the predicate rejects `True` and `False`.

### Missing input

```text
eta or a absent, undeclared, or not supplied through the authorised
field-construction source
  -> UNDECLARED_FIELD_INPUTS
```

The existing input-availability lifecycle, unchanged. Meaning: *we do not possess
the required physical input.* Missing is resolved **first** — an input we do not
possess has no value to be outside a domain — and a placeholder may not substitute
for it in any path that can produce an official valid Branch-A package. The
driver's existing `UNDECLARED_FIELD_INPUTS` refusal still blocks an official
campaign, because `eta` and `a` are still not *declared values* in frozen
authority.

### Present-invalid input

```text
eta or a present and nonfinite, zero or negative
  -> REFUSED_BRANCH_A_INVALID
```

The existing Branch-A-invalid refusal. Meaning: *we possess a value, but it is
outside the admissible physical domain.* No new category was invented; a mutation
to `VALID`, to `UNDECLARED_FIELD_INPUTS`, or to an invented
`REFUSED_DRAG_DOMAIN` all refuse.

### Gamma

```text
gamma(T_theta) = 6 pi eta(T_theta) a          relation UNALTERED
status         = DERIVED
physical domain = finite and strictly positive FOR ADMISSIBLE PRIMITIVES
independent_rule = false
```

The executable representation must additionally be finite and strictly positive
under the already-cleared representability rules — but failing *that* is a
different verdict, below.

### Tau

```text
tau_r = gamma(T_theta)/k_r                    relation UNALTERED
status = DERIVED
physical domain = finite and strictly positive FOR ADMISSIBLE PRIMITIVES
                  AND ADMISSIBLE STIFFNESS
independent_rule = false
```

`tau_r > 0` follows from `gamma > 0` together with the already-explicit
`lambda_r > 0`. The four implementation sites that have asserted `tau > 0` since
2026-09-28 with no prospective decision behind them now have the authority they
lacked. A mutation declaring either derived quantity an independent rule refuses,
so the architecture cannot decay into four unrelated positivity choices.

### Stiffness

```text
H not symmetric / not positive definite / dimension mismatch
  -> REFUSED_BRANCH_A_INVALID
```

Quoted from design §14 and **unchanged**. `lambda_r < 0` and `lambda_r = 0` were
already invalid and are not reopened; no negative-stiffness category and no
"valid unstable trap" branch exists. Reproduced behaviourally at the committed
tree: `k = (-1e-4, 1e-4) -> BRANCH_A_INVALID`, `k = (0.0, 1e-4) ->
BRANCH_A_INVALID`, `k = (1e-4, 1e-4) -> VALID`.

### Numerical representability

```text
primitives admissible, derived gamma or tau not representable in binary64
  -> BRANCH_A_MEASUREMENT_INVALID        existing semantics, UNCHANGED
```

The physical-domain check **precedes** the representability checks, and neither is
ever substituted for the other. Binary64 drag representability, the common
representable gamma, underflow/overflow, ties-to-even and relaxation
representability are untouched, untuned and not reopened. A mutation that labels a
representability failure as an `eta`/`a` physical invalidity refuses.

---

## The double-negative attack

Why a `gamma`-only rule is insufficient, executed rather than asserted:

```text
eta = -8.9e-04   a = -1e-06

gamma = 6 pi eta a   = 1.6776104770169493e-08    > 0   FINITE
tau   = gamma / 1e-4 = 0.0001677610477016949     > 0   FINITE

gamma-only rule  ACCEPTS          tau-only rule  ACCEPTS
approved rule    REFUSED_BRANCH_A_INVALID
```

A `gamma`-only rule also accepts the legitimate pair `eta = 8.9e-04, a = 1e-06`,
so it cannot be distinguished from the approved rule by what it accepts — only by
what it fails to refuse. Because neither primitive is persisted in the Branch-A
publication preimage, the resulting record is byte-identical to a legitimate
measurement and **no downstream check can recover them**. Authority therefore
names both insufficient rules explicitly:

```text
gamma > 0 alone, with the primitive eta and a domains unrestricted
tau_r > 0 alone, with the primitive eta and a domains unrestricted
```

and mutations that remove the primitive rules in favour of either one refuse with
`BRANCH_A_DOMAIN_AUTHORITY_MISMATCH`.

---

## F4 boundary

```text
ACTUAL ETA/A VALUES NOT SET
F4 REMAINS OPEN
```

The amendment declares an admissible **domain** and nothing else. It sets no
viscosity value, no viscosity model `eta(T)`, no bead radius, no measurement
uncertainty for either and no hardware provenance; the authority enumerates
exactly those six as *not declared here*. Enforcement is mechanical rather than
editorial: the only number permitted anywhere in the authority block is the
declared lower bound itself, asserted by walking every numeric leaf. Exactly two
numbers appear in the whole amendment, both `0`, both the lower bound. Inserting a
viscosity value, a bead-radius upper bound, a viscosity model, or erasing the
open-item record, all refuse with `BRANCH_A_DOMAIN_SCOPE_VIOLATION`. Field
construction is **not** marked execution-ready.

---

## Mutation tests

`test_e1a_v4_drag_domain.py` — **151 checks, 0 failures, 0 unexpected passes.**
77 are coherent scientifically wrong mutations, every one refused:

| refusal code | count |
|---|---:|
| `BRANCH_A_DOMAIN_AUTHORITY_MISMATCH` | 67 |
| `BRANCH_A_DOMAIN_SCOPE_VIOLATION` | 7 |
| `BRANCH_A_DOMAIN_UNCLASSIFIED` | 3 |

Every required class is covered, against both the **pinned rule object** and the
**contract document**:

| class | refused |
|---|:--:|
| `eta` positive → `eta >= 0` | ✓ |
| `a` positive → `a >= 0` | ✓ |
| `eta` positive → unrestricted | ✓ |
| `a` positive → unrestricted | ✓ |
| finite required → nonfinite allowed | ✓ |
| `eta` rule removed | ✓ |
| `a` rule removed | ✓ |
| gamma-only validation | ✓ |
| tau-only validation | ✓ |
| double-negative primitives treated valid | ✓ |
| missing `eta` treated as a physically invalid value | ✓ |
| missing `a` treated as a physically invalid value | ✓ |
| invalid `eta` treated as missing input | ✓ |
| invalid `a` treated as missing input | ✓ |
| invalid `eta`/`a` → `VALID` | ✓ |
| invalid `eta`/`a` → wrong refusal code | ✓ |
| gamma positivity made independent | ✓ |
| tau positivity made independent | ✓ |
| negative stiffness made valid | ✓ |
| zero stiffness made valid | ✓ |
| representability failure mislabelled an `eta`/`a` invalidity | ✓ |
| F4 values inserted into F2 authority | ✓ |

Also covered: each primitive made optional; each given an upper bound; the
approved rule text reworded; the Stokes relation altered inside the amendment; the
insufficient-rule record dropped; the scope broadened; the non-universality
disclaimer dropped; the whole section deleted; a required key removed; an
unclassified key added at the top level and at three greater depths — inside a
primitive, inside its domain and inside a disposition; each of the seven approved
clauses deleted from the design
document; the plan restatement weakened or deleted; the `G6` resolution reworded,
its status downgraded, its gap statement erased, the whole disposition deleted.

### No self-validation

Two probes check the property the whole construction exists for:

- **coherent drift** — plan JSON and Markdown both weakened to `>= 0` and the
  Markdown regenerated so the two agree: still refused;
- **fully propagated weakening** — contract *and* design document *and* plan all
  edited to `>= 0` and regenerated, so `require_contract_plan_conformance`
  **accepts** the package: the pinned rule still refuses it.

The candidate authority therefore cannot define its own expected `eta`/`a` domain,
and human and machine representations cannot coherently drift together away from
the approved rule.

---

## Coherence and conformance

```text
PREFLIGHT PASSED  (from the committed tree)
  contract sha256             d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4
  plan sha256                 c213b5d393422aad5fddb7cb3e482eab9ac10e0cfdca33cc3f91eb3c55e5bb8b
  seed map sha256             c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af
  analysis procedure identity 8cf86c96f12d762985f5104f44e8fc2010d61de48858a373ac78d6901e4eef9d
  execution seal state        PRE_DRIVER
  expected execution identity None
  execution_authorised        False
  RANDOM DRAWS 0   TRAJECTORIES 0
```

Contract→plan binding inventory, over actual contract leaves:

```text
execution_relevant_contract_leaves     268
execution_relevant_contract_bindings   341
unclassified_execution_relevant          0
  EXACT                                 45
  DERIVED                              100
  CASE_SPECIFIC_ALLOWED_OVERRIDE         5
  DELEGATED_TO_RELEASE_AUTHORITY        18
  DELEGATED_TO_DRAG_DOMAIN_AUTHORITY    61
  NOT_APPLICABLE                       112
```

The 61 new leaves are **bound**, not excused: `DELEGATED_TO_DRAG_DOMAIN_AUTHORITY`
names which layer binds them instead of letting them read as "not applicable", and
`drag_domain` then compares the block against the generated expectation key by key.
Added keys refuse at every depth — at the top level through the block
specification's totality check, and deeper through the exact comparison, each
asserted by its own probe. Markdown↔JSON coherence, the
normative-section registry, strict JSON, the generated-region byte-exact
re-renders and the authority-block equality all pass with the new key included;
section 4 renders the restatement as a declared Branch-A row, so a Markdown-only
or JSON-only edit refuses.

---

## Identities

| identity | before | after |
|---|---|---|
| physical foundation | `6d9aed24…` | `6d9aed24…` **unchanged** |
| theory baseline | `0a01b356…` | `0a01b356…` **unchanged** |
| design contract | `91d6ae76…` | `d7215ae4…` |
| contract version | `1.1.0` | `1.2.0` |
| prospective design | `e59dcff6…` | `25b637c3…` (29,330 → 34,799 bytes) |
| plan JSON | `dcf0c575…` | `c213b5d3…` |
| plan version | `1.15.0` | `1.16.0` |
| plan Markdown | `5b76c309…` | `dcbff1b7…` |
| seed map | `95870d7d…` | `c25f2da8…` |
| master seed | `13785910525869478477` | `4447657248690327258` |
| analysis procedure identity | `dd2ed732…` | `8cf86c96…` |
| execution identity (pre-driver diagnostic) | `92a28e45…` | `c7d2c3f3…` |

The execution identity is a **pre-driver diagnostic, not a seal**; it is not frozen
and `expected_execution_identity` remains `null`. It moved because the analysis
identity, the plan JSON, the plan Markdown, the seed map and the validation-module
set all moved. Its `before` value is the one computed from a clean extraction of
the starting commit `a58e6bc`.

Recomputed **twice** from independent clean `git archive` extractions of
`a8b8c815`, never from the working tree. Both agree exactly.

### The seed map moved, and this was expected to be reported honestly

The task brief anticipated `seed map unchanged`. **That expectation does not hold,
and the seed map was not artificially preserved.** `master_seed` is derived as
`DOMAIN|master|contract_sha256|campaign`, so amending the contract necessarily
moves it and every family seed below it:

```text
blinded_scale_control   11987123625083329897 -> 4960422446143947757
branch_a_measurement       62746336670861162 -> 1811775803831601789
calibration              6644164099584621674 -> 8836406515865678278
confirmatory             9827224290341944517 -> 5546981702450283376
validation               5088042359768187837 -> 1626264448266406929
```

Every value rederives from the committed algorithm, none was hand-edited, and
preflight recomputes the derivation and refuses a seed map that does not reproduce.
`drawn_in_this_stage` is `false` and **no seed was ever drawn, from the old values
or the new**. This is exactly what the design-level precedent `1a0c00e` did when
it closed G1–G3.

### The analysis identity moved, for a real reason

`procedure_identity` hashes `contract_sha256`, `design_sha256` and the twelve
`SCIENTIFIC_MODULES`. Amending the contract and the design moves it by
construction. Exactly one scientific module changed:

```text
e1a_v4/contract.py   4e1b595e… -> b43b85a4…
```

and only to accept contract minor `1.2` and to require the new section — authority
loading, not scientific behaviour. The other eleven are byte-identical. The
identity was **not** preserved artificially, and it did not move for verifier or
report code.

---

## Current implementation lag

The runtime remains **behind** this authority, and the suite asserts the lag
rather than hiding it. `BranchAField.__post_init__` validates `H_U`, `T` and
`scale_factor` only, so production marks every inadmissible drag input `VALID`:

| input | authority | production status |
|---|---|---|
| `eta < 0` | `REFUSED_BRANCH_A_INVALID` | `VALID` |
| `a < 0` | `REFUSED_BRANCH_A_INVALID` | `VALID` |
| `eta < 0` **and** `a < 0` | `REFUSED_BRANCH_A_INVALID` | `VALID`, and the record is byte-identical to a legitimate one |
| `eta = 0` | `REFUSED_BRANCH_A_INVALID` | `VALID` |
| `a = 0` | `REFUSED_BRANCH_A_INVALID` | `VALID` |
| `eta = ±inf` | `REFUSED_BRANCH_A_INVALID` | `VALID` |
| `eta = NaN` | `REFUSED_BRANCH_A_INVALID` | `VALID` |

Recovery refuses `gamma <= 0` indirectly, through the pre-existing `tau > 0`
clause, but **not** the double-negative case and **not** on the ground that the
measurement was inadmissible. No production or recovery module imports the new
authority module, and a regression asserts that too: wiring it in would be
implementing F2e without its independent audit.

```text
F2 AUTHORITY AMENDED
F2 RUNTIME RECONCILIATION REQUIRED
EXECUTION REMAINS BLOCKED
```

### Identity pins repointed

25 pinned identity literals across nine earlier-stage suites and
`e1a_v4_execution_feasibility_probe.py` were repointed, and 22 assertion labels
that said "did NOT change" / "is unchanged" were **reworded** rather than left
asserting something false. In every case the scientific content those blocks also
assert — the adopted rules, replicate counts, thresholds, `sigma_psi`, the C7
alternatives, the C8 scale factors — is unchanged and still passes, which is the
evidence that this amendment moved authority identity and no decision rule.

`test_e1a_v4_campaign_driver.py` was deliberately **reverted and left untouched**:
it is the known deferred trajectory-bearing suite, it was already carrying plan
digests stale from before this task (`PLAN_JSON_SHA256 = dcb35075…` while the
pre-amendment plan was `dcf0c575…`), and half-maintaining it would have
misrepresented it as current. All of its pins will need repointing when that suite
is un-deferred.

---

## Static and pure tests

One coherent run of the sixteen permitted suites, from the **committed tree**:

| suite | checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 1,237 |
| `test_e1a_v4_driver_endpoints.py` | 626 |
| `test_e1a_v4_terminal_calibration.py` | 538 |
| `test_e1a_v4_drag_domain.py` | **151** |
| `test_e1a_v4_coherence_hardening.py` | 138 |
| `test_e1a_v4_size_semantics.py` | 138 |
| `test_e1a_v4_repair.py` | 126 |
| `test_e1a_v4.py` | 122 |
| `test_e1a_v4_case_scope.py` | 114 |
| `test_e1a_v4_generating_model.py` | 113 |
| `test_e1a_v4_plan_coherence.py` | 113 |
| `test_e1a_v4_calibration_scope.py` | 105 |
| `test_e1a_v4_preexec.py` | 105 |
| `test_e1a_v4_contract_plan.py` | 76 |
| `test_e1a_v4_dispositions.py` | 64 |
| `test_e1a_v4_preexec_corrections.py` | 52 |
| **Total** | **3,818** |

```text
SUITES            16
CHECKS            3818
FAILURES          0
UNCLEAN SUITES    0
TRAJECTORY COUNT  0
CAMPAIGN JOBS     0
```

Every suite exited successfully and printed exactly one parseable completion
summary; the total excludes no crashed or incomplete suite. `git diff --check`
passes. F1 is preserved: per-field C2, C3 G5, C4 Block-1, structured refusals,
whole-record integrity, C1/C7 compositions and C8 paired evidence preflight all
pass unchanged, and no F1 scientific behaviour was modified.

The trajectory-bearing `test_e1a_v4_campaign_driver.py` remains **DEFERRED and NOT
RUN**. Its 102 imported package names were confirmed to still resolve after the
new refusal codes and module were added.

---

## Execution state

```text
OFFICIAL RESULTS       NONE   (results/e1a_v4_validation does not exist)
OFFICIAL CAMPAIGN      NOT RUN
TRAJECTORIES           0
SCIENTIFIC RNG OBJECTS 0
FINAL EXECUTION SEAL   NOT FROZEN
EXECUTION AUTHORISED   FALSE
```

---

## Next stage

```text
F2d INDEPENDENT AUTHORITY AUDIT
READY
```

F2e runtime reconciliation, F3–F8 and the deferred trajectory-bearing integration
suite all remain open and are not begun.

---

```text
PASSIVE-DRAG DOMAIN AUTHORITY AMENDMENT COMMITTED
```
