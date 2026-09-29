# E1a v4 — contract ↔ plan conformance report

## Result

**The four audited escape routes are closed at static preflight.** Before this
correction, a simultaneous change to the plan's Markdown and JSON could remove
`theta3_temperature`, duplicate `theta0_circular`, replace the relaxation rule,
or set `theta1_power.beta_true = 2.0` and still pass plan coherence. The
pre-repair probes reproduced all four acceptances. With the new independent
contract check, all four keep Markdown/JSON coherence but refuse with the
specific contract code. No random object or model state was created.

Work commit: `174cd3f79c9cf3ac8524e3ea3b3b268d8440e7d1`

Audit-count clarification (separate, not amended):
`e6ccd0bf1517975317f82a1d87767c6b880a7f1f`

Final code tree: `a784997108f2851010a7c5910dc7191f38dcbc77`

## Authority and check order

The frozen physical foundation and working theory baseline constrain E1a. For
this validation package, the adopted design contract is upstream of the
validation plan; the plan's JSON and Markdown must agree with each other and
with that contract. The analysis implementation remains bound by its separate
identity. Plan coherence is checked first, then contract conformance, then seal
agreement, frozen source identities, and the remaining preflight gates. Both
checks are required; agreement of two wrong plan renderings is insufficient.

On a direct `run(execute=True)` call, the canonical driver is checked **before**
preflight; then the execution gate checks seal, identity and authorisation. The
CLI first displays a full preflight, checks its authorisation flag, then calls
that direct execute path. The preflight-only command is unchanged. This report
does not call the execute path.

## Exact fields, reference and physical parameters

The contract JSON is the ordering source. The plan must have these four IDs
once each, in this order, with no extra field:

| ID | stiffness (µN/m) | temperature (K) | orientation | reference |
|---|---:|---:|---:|---|
| `theta0_circular` | 100, 100 | 298 | 0° | yes |
| `theta1_power` | 210, 210 | 298 | 0° | no |
| `theta2_ellipse` | 150, 60 | 298 | 30° | no |
| `theta3_temperature` | 100, 100 | 318 | 0° | no |

Every field's stiffness, temperature, orientation and reference flag is
compared with its own contract entry. Missing, renamed, extra and duplicate
IDs refuse separately; the plan must retain exactly the contract's one
reference field. Mutations of every physical field parameter were tested.

## Relaxation, beta and sampling

The contract's Stokes-drag rule is bound to all four plan fields:

\[
\gamma(T)=6\pi\eta(T)a,\qquad \tau_r=\gamma(T)/k_r.
\]

The shorter plan rendering is admitted only as that exact algebraic rule. A
static pure-function check confirms that the unchanged Branch-A implementation
returns per-mode times, not a common constant. No OU generator was changed.

The ordinary field prediction is `beta_true = 1`, specific to this thermal
benchmark. The case inventory is:

| Case | Underlying beta authority | Exception? |
|---|---|---|
| C1 complete bridge | contract prediction, 1 | no |
| C2 geometry size | contract prediction, 1 | no |
| C3 G5 block | contract prediction, 1 | no |
| C4 surrogate validity | contract prediction, 1 | no |
| C5 Branch-A plug-in grid | contract prediction, 1 | no |
| C6 mode boundary | contract prediction, 1 | no |
| C7 false bridge | contract's four declared alternative vectors | **yes, only here** |
| C8 blinded scale | underlying bridge remains 1; measured branch reads `1/c` | **not a beta-truth override** |

C7's four alternatives are the exact frozen vectors: `(1,1.06,1,1)`,
`(1,0.93,1.05,1)`, `(1,1,1,1.10)`, and `(1,1.025,1,1)`. C8's paired scale
factors remain `1.07` and `0.90`. A C7 change is refused; C8 cannot be used to
grant arbitrary beta truth elsewhere.

The contract binds `dt = 0.00012 s` and `T_total = 240 s`. The plan's
`n_samples = 2,000,000` is derived by `int(round(T_total/dt))`, not an
independent parameter. The primary orientation uncertainty remains 0.5°;
the three secondary/stress settings are bound separately. C5's full 3×4
uncertainty grid is bound to the contract's declared grid.

## Contract binding inventory

The machine-generated inventory examines **206** leaves in the explicitly
declared execution-relevant contract sections. It contains **272** path/reason
records because one contract leaf may govern several plan entries:

| Relationship | Records |
|---|---:|
| `EXACT` | 44 |
| `DERIVED` | 100 |
| `CASE_SPECIFIC_ALLOWED_OVERRIDE` | 5 |
| `NOT_APPLICABLE` to an independent plan scalar | 123 |
| Unclassified execution-relevant leaves | **0** |

`NOT_APPLICABLE` does **not** remove contract authority. Each such leaf has an
explicit path and reason; formulas, entropy meanings, prohibitions and
interpretations remain binding in the contract or analysis layer, rather than
being copied into a second plan scalar. Adding an unknown contract leaf fails
closed instead of inheriting that classification.

The contract's inherited C2 3% upper-bound requirement was reviewed, not
silently discarded. The later plan's nominal-inflation pass set is stricter:
at most 5/400 rejections, for which the one-sided 95% Clopper–Pearson upper
bound is `0.02610179906691329 < 0.03`. The conformance check derives and
enforces this implication. The eventual campaign report must still make the
contract's upper-bound fact available; the driver/reporting stage has not
begun. This is not a new size rule or a claim that nominal size was proved.

## Mutation and Section-4 audit

All **43/43 directly mutable** `EXACT` mappings and **100/100** `DERIVED`
mappings were changed in valid-looking ways on temporary copies. The 44th
`EXACT` mapping is the complete field-ID list, covered by the separate
missing/duplicate/renamed/extra-field mutations. The Markdown was regenerated
from the changed JSON; plan coherence passed, and contract conformance refused.
The five C7 exception rows were also mutated and refused. Exhaustive field
membership mutations covered each missing, duplicate and renamed field, plus
an extra field and missing/multiple references.

The older one-sided generating-model test no longer replaces the first matching
token anywhere in the document. It changes the named primitive, renders only
the anchor-delimited Section 4 region, and asserts that the intended canonical
path changed. Its JSON-only and Section-4-only results remain **38/38** and
**38/38** refusals.

## Scientific rules and identities

**NO E1a SCIENTIFIC DECISION RULE CHANGED.** Contract, design, baseline, field
set, P1–P4 decisions, C1–C8 cases, thresholds, seeds, OU generator and analysis
modules are unchanged. The new pre-driver execution identity moves because
the validation code is part of its preimage; it is **not** a final seal.

| Identity | SHA-256 / value |
|---|---|
| foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| plan Markdown | `fab1b2411cba064a5ca046c8a04ed192ee3a755db40f5b822ed4daa81f4fb680` |
| plan JSON | `45911bf9cb19db298e8f2d09da86d1e23de35b609cd8271e6da61952cb99e169` |
| seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` |
| analysis identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` |
| **pre-driver** execution identity | `f76359623c451f49a5bd4dea2db6532360a2b94259fbfb5321174a948544ff1f` |

Plan version remains `1.9.0`; result and manifest schema versions remain
`e1a_v4_validation_result/2` and `e1a_v4_validation_manifest/2`.

## Static validation

No stochastic or model-advancing test was called. The applicable pure suites:

| Suite | Checks passed | Failed |
|---|---:|---:|
| bounded E1a implementation | 122 | 0 |
| dispositions | 64 | 0 |
| size semantics | 78 | 0 |
| pre-execution repair | 126 | 0 |
| calibration scope | 105 | 0 |
| case scope | 113 | 0 |
| pre-execution corrections | 37 | 0 |
| plan coherence | 112 | 0 |
| generating-model coherence | 112 | 0 |
| **new contract-plan conformance** | **75** | **0** |
| pre-execution: five static groups only | 96 | 0 |
| coherence hardening: seven static groups only | 121 | 0 |
| **Total executed** | **1,161** | **0** |

The two omitted groups invoke `run(execute=True)` to prove a refusal. They
were **not run** because this stage forbids calling an execution runner, even
one expected to refuse. A skipped group is not counted as a pass. All tested
static checks completed. Staged-diff whitespace check passed.

## Execution state and next boundary

```text
execution_authorised = false
official campaign driver = ABSENT
final execution seal = NOT FROZEN
RNG OBJECTS = 0
RANDOM DRAWS = 0
TRAJECTORIES = 0
VALIDATION CAMPAIGN = NOT RUN
```

The E1a v4 official campaign-driver implementation is the **next possible
stage**, **READY FOR FINAL INDEPENDENT RE-AUDIT**, and **NOT STARTED** here.
The final seal, execution authorisation and campaign remain separate later
boundaries. The 3% contract diagnostic should be visible in the eventual
report despite its redundancy as a release gate.

CONTRACT-PLAN CONFORMANCE COMMITTED
