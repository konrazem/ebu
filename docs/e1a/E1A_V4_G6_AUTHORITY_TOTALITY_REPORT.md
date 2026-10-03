# E1a v4 — G6 authority-gap totality repair report (F2c-r1)

Bounded repair of the one blocking defect the independent F2d audit found in the
F2c passive-drag amendment. **Verifier and test only.** No authority document, no
scientific module and no runtime behaviour was changed, and the approved
scientific decision was not reconsidered.

---

## Starting coordinate

```text
STARTING HEAD    d399d12360c9ac65bc7fe845d59355d3de1a0bad
STARTING TREE    2ac7ac20c2ae60265e71f27e593cb7858a3ae8b6
WORKTREE         clean -- no tracked or untracked change
BRANCH           gaussian/stage-a-environment
```

```text
WORK COMMIT      40f154c7f247779c26cfcf423936c5d66e09a1d6
WORK TREE        2fe11687db4825139429be04d10f2a4c8eedc925
```

The coordinate the audit reported was verified independently and matched exactly.

---

## The F2d blocker, reproduced before editing

Reproduced against the audited HEAD `d399d12`, in an isolated candidate copy,
**before any edit**:

```text
EXACT G6 PATH      plan["authority_gaps"][5]     (record with id == "G6")
ORIGINAL KEY SET   ['affects', 'gap', 'id', 'resolution', 'status']
MUTATED KEY SET    ['affects', 'gap', 'id', 'passive_drag_exception',
                    'resolution', 'status']
NEW KEY / VALUE    "passive_drag_exception":
                   "Zero viscosity is permitted for this field."
```

Behaviour of the unmodified package:

| check | result |
|---|---|
| strict JSON parse (duplicate-key aware) | **valid** |
| Markdown regeneration through the normal repository path | **succeeded** |
| `require_plan_authority_coherence` | **ACCEPTED** |
| `require_passive_drag_domain_authority` | **ACCEPTED** |
| full static preflight `bind_execution` | **ACCEPTED** |
| the clause present in the generated normative Markdown | **no** |
| the key name present anywhere in the Markdown | **no** |

A candidate could therefore carry a clause contradicting an approved prospective
scientific decision, inside frozen authority, rendered nowhere and compared by
nothing. This exact attack is now a permanent regression in two suites.

### The defect was broader than the one reported case

Measured at the audited HEAD before editing, by the same method:

| probe | pre-repair behaviour |
|---|---|
| G6 + `passive_drag_exception` | **ACCEPTED**, silent |
| G6 + a benign `note2` | **ACCEPTED**, silent |
| G6 + an unknown **nested child object** | **ACCEPTED**, silent |
| G6 + an unknown **list** value | **ACCEPTED**, silent |
| **G1** + an unknown key | **ACCEPTED**, silent |
| an **appended bogus `G7` disposition** | **ACCEPTED**, *and rendered into the normative Markdown as new science* |
| G6 missing a required key | refused only as an **uncoded `KeyError`** |
| G6 key renamed | refused only as an **uncoded `KeyError`** |
| G6 value given the wrong type | refused incidentally, via a regex parse |

So the same hole was open on every disposition, at nested and list depth, and one
level up at the container. Two of the "refusals" were uncaught exceptions rather
than coded refusals, which this repository deliberately distinguishes.

---

## Root cause

```text
authority_gaps record membership was never itself normative
```

Every reader of a disposition record iterated the same hard-coded four-key tuple
`("gap", "affects", "status", "resolution")`:

| reader | consequence of a fifth key |
|---|---|
| `coherence.normative_json_view` | never entered the normative JSON view |
| `coherence._human_rendered_keys` | never entered the human-rendered key set |
| `coherence.render_release_rules_region` | never rendered into the Markdown |
| `drag_domain.require_passive_drag_domain_authority` | never compared — it checked only the four known G6 fields |

Because the five legitimate fields still matched their approved text **exactly**,
every value comparison passed. The extra field was not weighed and found
acceptable; it was never looked at. The record could expand its own scientific
authority surface — self-authorising authority.

Markdown↔JSON coherence could not catch it either: the Markdown agreed with the
JSON about everything the specification knew about, and the specification did not
know about the sixth key.

---

## Final architecture

### Canonical gap schema, pinned above the candidate

`e1a_v4/validation/coherence.py`:

```text
AUTHORITY_GAP_SPEC            every permitted key -> (leaf type, reason)
AUTHORITY_GAP_VIEW_KEYS       derived from the spec; `id` is the path selector
RENDERED_AUTHORITY_GAP_KEYS   what the renderer actually emits
AUTHORITY_GAP_IDS             the approved roster, in order
```

`e1a_v4/validation/drag_domain.py`:

```text
DISPOSITION_RECORD_KEYS       ("affects", "gap", "id", "resolution", "status")
```

Neither is derived from the candidate. `allowed_keys = candidate_G6.keys()` does
not appear anywhere, and a test asserts it.

### Required and allowed keys

G6 — and every other disposition — has **no optional fields**, so the candidate
key set must equal the canonical key set exactly:

| outcome | refusal |
|---|---|
| unknown extra key, any record | `PLAN_SURFACE_UNDECLARED` |
| missing required key | `PLAN_RELEASE_RULE_MISMATCH` |
| renamed key | `PLAN_SURFACE_UNDECLARED` (the new name is unknown) |
| wrong scalar type, including `bool` where text is declared | `PLAN_RELEASE_RULE_MISMATCH` |
| record that is not an object | `PLAN_RELEASE_RULE_MISMATCH` |
| same, seen by the independent G6 layer | `BRANCH_A_DOMAIN_AUTHORITY_MISMATCH` |

### Recursive totality

`_require_record_totality` is recursive by construction. A specification entry is
either a **leaf type** or a **nested specification**. A value that is a container
where a leaf is declared is an unclassified descendant:

```text
known parent + unknown child = REFUSE
```

A classified parent never authorises arbitrary descendants. Earlier F1 hardening
found exactly that defect one nesting level deeper on three separate occasions;
it is closed here before it can appear rather than after.

### List totality

**No authority-carrying list exists inside any disposition record today** — the
inventory below confirms every value is a flat string. The machinery still refuses
a list where a leaf is declared, so a future list must be given its own
specification before it can be carried. The `authority_gaps` **container** is
itself a list whose membership carries authority, and its membership and order are
bound by `AUTHORITY_GAP_IDS`.

### Free text inside G6

Every string-valued field in G6 is already **generated from the pinned rule** in
`drag_domain` and compared exactly — `gap` from `render_disposition_gap()`,
`resolution` from `render_disposition_resolution()`, `affects` and `status` from
pinned constants. There is no field in which free prose can sit. Combined with
key-set equality, there is no place for explanatory text that could change how a
competent reader interprets the eta domain, the a domain, either disposition, the
gamma or tau derivation, the benchmark scope or the representability separation.
No keyword blacklist is used anywhere, and a benign `note2` refuses identically to
a clause saying zero viscosity is permitted — the mechanism cannot tell them apart
and does not need to.

### No silently-omitted declared field

`require_authority_gap_totality` asserts `set(RENDERED_AUTHORITY_GAP_KEYS) ==
set(AUTHORITY_GAP_SPEC)`, so a key cannot be declared and then left out of the
rendering. Of the two options the task allows, the package now realises **both**:
unknown content is rejected *before* rendering, and every declared field is
rendered and compared.

### Reject before rendering

`render_release_rules_region` calls the totality check first. The renderer is
reachable on its own — the regeneration path calls it directly — so it must not be
the one place a malformed record becomes an uncoded `KeyError`. After the repair,
regenerating a plan with a missing, renamed or extra G6 key refuses with a code.

### Two independent layers

`coherence` enforces the schema generically for all six dispositions.
`drag_domain` independently checks the G6 record's own key set and value types
with its own refusal code. Neither is load-bearing alone, and the test suite
asserts the refusal at each layer separately.

---

## Scope

```text
ALL AUTHORITY_GAPS RECORDS, not G6 only
```

Inventory of the committed plan, taken before designing anything:

| id | keys | status | nested objects or lists |
|---|---|---|:--:|
| G1 | `affects, gap, id, resolution, status` | `CLOSED PROSPECTIVELY` | none |
| G2 | same | `CLOSED PROSPECTIVELY` | none |
| G3 | same | `CLOSED PROSPECTIVELY` | none |
| G4 | same | `CLOSED PROSPECTIVELY` | none |
| G5 | same | `CLOSED PROSPECTIVELY` | none |
| G6 | same | `CLOSED PROSPECTIVELY` | none |

All six share **one** flat schema — exactly five string fields — and there is no
nested structure anywhere. There are therefore no gap generations with legitimately
different shapes, so one common specification is correct: it discards no
provenance field, reinterprets nothing, and alters no scientific content of
G1–G5. The defect class was demonstrated open on G1 as well, so fixing only G6
would have left the audit's own finding reproducible one record away.

The `authority_gaps` container roster is bound too. That is one level above the
reported defect and is disclosed as such: an appended bogus disposition was
accepted *and rendered*, which is the same self-authorising class at container
scope. Closing it required no scientific change and leaving it open would have
shipped a repair that still admits a brand-new contrary disposition.

---

## Scientific non-change

```text
NO F2 SCIENTIFIC DECISION CHANGED
```

No authority document was touched — `git status` over `docs/` was empty
throughout. Re-verified at the committed tree:

| property | result |
|---|---|
| `eta(T_theta)` domain | finite, strictly `> 0` — **unchanged** |
| bead radius `a` domain | finite, strictly `> 0` — **unchanged** |
| bound individually, never through `gamma` | **unchanged** |
| missing `eta` or `a` | `UNDECLARED_FIELD_INPUTS` |
| present nonfinite / zero / negative | `REFUSED_BRANCH_A_INVALID` |
| `gamma = 6 pi eta a`, `tau_r = gamma/k_r` | derived, relations unaltered |
| negative and zero stiffness | existing invalid rule, not reopened |
| representability semantics | existing, separate, unchanged |
| statistical thresholds, case roster, replicate counts | unchanged |

### Double-negative regression

```text
eta = -8.9e-04 , a = -1e-06
gamma = 1.6776104770169493e-08   > 0   FINITE
tau   = 0.0001677610477016949    > 0   FINITE
gamma-only rule   ACCEPTS
approved rule     REFUSED_BRANCH_A_INVALID
```

### Missing versus invalid

```text
missing eta            -> UNDECLARED_FIELD_INPUTS
missing a              -> UNDECLARED_FIELD_INPUTS
eta = 0.0              -> REFUSED_BRANCH_A_INVALID
eta = -1.0             -> REFUSED_BRANCH_A_INVALID
eta = +inf / -inf      -> REFUSED_BRANCH_A_INVALID
eta = NaN              -> REFUSED_BRANCH_A_INVALID
eta > 0 and a > 0      -> ADMISSIBLE
```

The totality repair did not collapse them.

### Representability separation

With `eta = a = 5e-324`, both finite and strictly positive:

```text
primitive domain verdict     ADMISSIBLE
derived gamma                underflows to 0.0
authority verdict            BRANCH_A_MEASUREMENT_INVALID
explicitly NOT               REFUSED_BRANCH_A_INVALID
```

Physically admissible primitives with an unrepresentable derived quantity keep the
existing numerical semantics and are never relabelled an invalid measurement.

### F4

```text
F4 - field construction / absolute drag inputs = OPEN
```

Six inputs enumerated as not declared here. The only numbers anywhere in the
authority block remain `[0, 0]` — both the declared lower bound. No viscosity
value, bead radius, viscosity model, uncertainty or hardware source was
introduced.

---

## Identity preservation

Recomputed **twice** from independent clean `git archive` extractions of
`40f154c7`, never from the working tree. Both agree exactly.

| identity | audited F2 candidate | after this repair | |
|---|---|---|---|
| physical foundation | `6d9aed24…` | `6d9aed24…` | **unchanged** |
| theory baseline | `0a01b356…` | `0a01b356…` | **unchanged** |
| prospective design | `25b637c3…` | `25b637c3…` | **unchanged** |
| design contract | `d7215ae4…` | `d7215ae4…` | **unchanged** |
| plan JSON | `c213b5d3…` | `c213b5d3…` | **unchanged** |
| plan Markdown | `dcbff1b7…` | `dcbff1b7…` | **unchanged** |
| seed map | `c25f2da8…` | `c25f2da8…` | **unchanged** |
| master seed | `4447657248690327258` | `4447657248690327258` | **unchanged** |
| all five family seeds | — | — | **unchanged**, `drawn_in_this_stage: false` |
| analysis procedure identity | `8cf86c96…` | `8cf86c96…` | **unchanged** |

The twelve `SCIENTIFIC_MODULES` on disk all still match the plan's frozen hashes,
and neither `coherence.py` nor `drag_domain.py` is in that preimage — which is why
the analysis identity could not move and did not. No historical identity pin
needed repointing; the 25 pins moved by F2c were left exactly as the audit
cleared them.

### Execution identity

```text
BEFORE  c7d2c3f303f281ceff8b8f5a2fc8a33e288f2749da504064ce74897b07fed37c
AFTER   e2838a3f96fa1fe3bd79e788d6171b9ef903c1e112ae10abc57e0ea08487f0a8
```

Moved, as expected: `e1a_v4/validation/coherence.py` and
`e1a_v4/validation/drag_domain.py` are both in `VALIDATION_MODULES`. This is the
**unsealed pre-driver diagnostic**, not a seal. `expected_execution_identity`
remains `null` and the seal state remains `PRE_DRIVER`.

---

## Runtime lag

```text
F2e STILL REQUIRED
```

Unchanged by this repair and re-measured at the committed tree. Production still
marks every inadmissible drag input `VALID`:

| input | production | authority |
|---|---|---|
| `eta < 0` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `a < 0` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `eta < 0` and `a < 0` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `eta = 0` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `a = 0` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `eta = inf` | `VALID` | `REFUSED_BRANCH_A_INVALID` |
| `eta = NaN` | `VALID` | `REFUSED_BRANCH_A_INVALID` |

**7 of 7 behind authority.** `branch_a.py`, production acceptance, recovery
acceptance, calibration locking and Branch-B launch were not touched, and no
production or recovery module imports the authority module. Closing this is F2e,
after its own independent audit.

---

## Report-only correction

The F2d audit corrected a claim in the previous report. That correction is
accepted and recorded here rather than erased:

```text
docs/e1a/E1A_V4_PASSIVE_DRAG_DOMAIN_AMENDMENT.md:214: new blank line at EOF
```

Verified independently per commit:

| commit | `git diff --check` |
|---|---|
| `a8b8c81` — the amendment work commit | **clean** |
| `0b7bf41` — the test-only follow-up | **clean** |
| `d399d12` — the record and report commit | **one finding**, the blank line above |

The earlier report's statement that `git diff --check` passes was true of the work
commits it was describing, but it was written as an unqualified claim and the
report commit itself was never re-checked. **The claim overstated what had been
verified, and the audit was right to flag it.**

The amendment record's bytes are left intact. This repair does not touch that file
for any structural reason, and editing it purely to erase an audit note would be
cosmetic. The file is a record-class document and is not bound into any identity
preimage, so its trailing byte affects no hash. `git diff --check` on the present
work commit is **clean**.

---

## Tests

From the **committed tree** `40f154c7`:

| suite | checks | |
|---|---:|---|
| `test_e1a_v4_release_authority.py` | 1,237 | |
| `test_e1a_v4_driver_endpoints.py` | 626 | |
| `test_e1a_v4_terminal_calibration.py` | 538 | |
| `test_e1a_v4_drag_domain.py` | **170** | +19 |
| `test_e1a_v4_coherence_hardening.py` | **178** | +40 |
| `test_e1a_v4_size_semantics.py` | 138 | |
| `test_e1a_v4_repair.py` | 126 | |
| `test_e1a_v4.py` | 122 | |
| `test_e1a_v4_case_scope.py` | 114 | |
| `test_e1a_v4_generating_model.py` | 113 | |
| `test_e1a_v4_plan_coherence.py` | 113 | |
| `test_e1a_v4_calibration_scope.py` | 105 | |
| `test_e1a_v4_preexec.py` | 105 | |
| `test_e1a_v4_contract_plan.py` | 76 | |
| `test_e1a_v4_dispositions.py` | 64 | |
| `test_e1a_v4_preexec_corrections.py` | 52 | |
| **Total** | **3,877** | **+59** |

```text
SUITES            16
CHECKS            3877
FAILURES          0
UNCLEAN SUITES    0
SCIENTIFIC RNG    0
TRAJECTORY COUNT  0
CAMPAIGN JOBS     0
```

Every suite exited successfully and printed exactly one parseable completion
summary; the total excludes no crashed or incomplete suite. The hardened runner
rule is preserved: a suite with no clean summary line counts as unclean.

### New coverage

43 of the 59 added checks are refused attacks; the remaining 16 assert the committed shape, the pinned constants and the no-self-validation property:

| group | refusals |
|---|---:|
| generic authority-gap totality (`PLAN_SURFACE_UNDECLARED`) | 19 |
| generic authority-gap totality (`PLAN_RELEASE_RULE_MISMATCH`) | 8 |
| G6 record shape, independent layer (`BRANCH_A_DOMAIN_AUTHORITY_MISMATCH`) | 16 |

Covered: the exact `passive_drag_exception` attack; a benign `note2`; seven
contrary extra clauses (zero viscosity permitted, negative bead radius
permitted, gamma-only sufficient, tau-only sufficient, missing eta treated as
zero, invalid eta treated as undeclared, overflow making eta invalid); unknown
nested child object; unknown list value; a declared key turned into an object or
a list; wrong scalar type; a `bool` where text is declared; missing required key;
renamed key; a record replaced by a bare string; `authority_gaps` replaced by a
mapping; an unknown key on **each** of G1–G5; an appended bogus `G7`; a deleted
disposition; a reordered roster; a duplicated disposition; and a
no-self-validation test that mutates the candidate, rebuilds every
checker and renderer structure against it, and asserts the canonical schema,
roster and rendered-key set are unchanged and that no view key is derived from an
unapproved field.

### Preserved F2 attacks

All previously refusing drag-domain variants still refuse: `eta >= 0`, `a >= 0`,
finiteness removed, each rule removed, gamma-only, tau-only, double-negative
accepted, dispositions swapped, invalid primitive declared `VALID`, negative
stiffness valid, zero stiffness valid, representability failure mislabelled a
primitive invalidity, each primitive made optional or given an upper bound, the
approved text reworded, the Stokes relation altered, scope broadened, disclaimer
dropped, F4 values inserted, and the fully-propagated contract+design+plan
weakening. Drag-domain checking was strengthened, not weakened.

### Deferred suite

`test_e1a_v4_campaign_driver.py` was **not modified** and **not run**. It remains
KNOWN DEFERRED with pins stale from before F2c, and is not treated as validation
evidence. Its 102 imported package names were confirmed to still resolve after the
new module constants were added.

---

## Execution state

```text
OFFICIAL CAMPAIGN      NOT RUN
OFFICIAL RESULTS       NONE   (results/e1a_v4_validation does not exist)
OFFICIAL TRAJECTORIES  0
SCIENTIFIC RANDOM DRAWS 0
CALIBRATION EXECUTIONS 0
FINAL EXECUTION SEAL   NOT FROZEN   (state PRE_DRIVER)
EXECUTION AUTHORISED   FALSE
```

---

## Next stage

```text
F2d RE-AUDIT READY
```

F2e runtime reconciliation, F3–F8 and the deferred trajectory-bearing integration
suite all remain open and are not begun.

---

```text
G6 AUTHORITY-GAP TOTALITY REPAIR COMMITTED
```
