# E1a v4 — PRE-EXECUTION CORRECTION ADOPTION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**The correction candidate is ADOPTED.** Every critical deterministic claim was
independently reproduced before adoption, none by reading the candidate's prose.

The auditor's uncommitted working tree contained **only** E1a v4 validation-package
changes plus the candidate document and its new gate. **No unrelated user work was mixed
in**, so nothing had to be preserved or set aside, and nothing was reset, stashed,
checked out or cleaned.

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
execution_authorised = false   RNG OBJECTS 0   RANDOM DRAWS 0   TRAJECTORIES 0
```

One correction is **material to the scientific answer** and would have biased the one
field the campaign most depends on for geometry. The rest close fail-open paths.

---

## Rotated OU defect

### The superseded recurrence

```
x_{k+1}[i] = phi_i x_k[i] + sqrt(1 - phi_i^2) (L z)_i        L = chol(Sigma)
```

In matrix form `F_old = diag(phi)` and `Q_old = D Sigma D` with
`D = diag(sqrt(1-phi_i^2))`, so

```
(F_old Sigma F_old^T + Q_old)_ij = [ phi_i phi_j + sqrt((1-phi_i^2)(1-phi_j^2)) ] Sigma_ij
```

For `i = j` the bracket is exactly `1` — **the diagonal is preserved**, which is why the
defect could hide. For `i != j` it is strictly less than 1 whenever `phi_i != phi_j`. The
error is therefore invisible unless the field is **both anisotropic** (so `phi_i != phi_j`)
**and rotated** (so `Sigma_ij != 0`).

### The corrected recurrence

```
F = R diag(phi_i) R^T            Q = Sigma - F Sigma F^T
Q_eig,ii = (1 - phi_i^2) / (beta lambda_i)          Sigma = (beta H_true)^-1
```

implemented by evolving independent eigenmodes of `H_true` and rotating back.

### Reproduced, deterministically, with no trajectory

Probe: `theta2_ellipse`, `k = (150, 60) uN/m` at `30°` — **the only declared field that is
both rotated and anisotropic**.

| | |
|---|---|
| corrected: `|F Sigma F^T + Q - Sigma| / |Sigma|` | **`0.000e+00`** |
| `Q_eig[0][0]` vs `(1-phi^2)/(beta lambda)` | agree to `1.6e-16` |
| `Q_eig` off-diagonal | `9.2e-33` |
| **superseded**: residual | **`1.958e-02`** relative to `max|Sigma|` |
| superseded off-diagonal factor | **`0.935926747418`** — a **6.4% under-estimate** |
| superseded diagonal error | `1.6e-16` — preserved, hence invisible |

Control, confirming the diagnosis rather than assuming it:

| field | superseded residual | why |
|---|---|---|
| `theta0_circular` | `1.5e-16` | isotropic, `phi_1 = phi_2` |
| `theta1_power` | `0.0e+00` | isotropic |
| anisotropic at `rot = 0` | `1.8e-16` | `Sigma` diagonal |
| **`theta2_ellipse` at `rot = 30°`** | **`1.96e-02`** | **both** |

This matters because `S` is the sample covariance and `K = S^-1`; a 6.4% distortion of the
cross-covariance would have biased G1–G4 on exactly the field whose geometry the gates are
most sensitive to. **No trajectory was generated to establish any of this** — it is pure
algebra on the transition operator.

---

## Modal ordering

`tau_true` is ordered **with ascending `H` eigenvalues**, the `jacobi` convention, and the
pairing is *enforced* rather than assumed: under isotropic Stokes drag `tau_i = gamma/k_i`
and `lambda_i = k_i/(k_B T)`, so `lambda_i tau_i = gamma/(k_B T)` must be **constant across
modes**. Any independent re-sorting breaks that invariant and is refused.

Verified on `theta2_ellipse`:

| mode | `lambda` | recovered `k` | `tau` | `gamma/k` | match |
|---|---|---|---|---|---|
| 0 | `1.458316e+16` | `60.000 uN/m` | `2.796017e-04` | `2.796017e-04` | yes |
| 1 | `3.645791e+16` | `150.000 uN/m` | `1.118407e-04` | `1.118407e-04` | yes |

`lambda` ascending pairs with `tau` **descending**, as `tau = gamma/k` requires;
`lambda_i tau_i` is constant; and a deliberately swapped order is **REFUSED**
("modal relaxation times are not paired with H_true eigenmodes"). The same invariant now
guards `CalibrationRequest.condition()`.

---

## Beta covariance

`Sigma = (beta H)^-1`, never a hard-coded `H^-1`.

| `beta` | `Q diag(sd^2) Q^T` vs `(beta H)^-1` | `|F Sigma F^T + Q - Sigma| / |Sigma|` | `Sigma` vs `H^-1` |
|---|---|---|---|
| 1.0 | `4.2e-16` | `0.0e+00` | `0.0e+00` (identical, as it must be) |
| 1.06 | `1.1e-16` | `0.0e+00` | `0.0566` ≈ `1/beta - 1` |
| 0.93 | `2.0e-16` | `9.8e-17` | `0.0753` |
| 1.10 | `2.3e-16` | `0.0e+00` | `0.0909` |
| 1.025 | `2.2e-16` | `0.0e+00` | `0.0244` |

The last four are exactly the frozen false-bridge alternatives. **None is altered** — this
verifies the generator honours their declared truth, it does not change them.

---

## C2 completeness

`classify_campaign` refuses any C2 field map that is not **exactly** the four declared
fields. Verified: each of the four absent individually → REFUSE; empty map → REFUSE; an
**extra** unknown field → REFUSE. A missing row is never read as a clean zero-rejection
row. Thresholds untouched: 6 rejections in any field still fails.

## C7 completeness

Both the campaign classifier **and** the direct `g2_campaign_pass` helper refuse any
alternative map that is not exactly the four declared alternatives. Verified: each of the
four absent individually — the **hard** `hard_1_025` and each easy alternative — → REFUSE
in both; extra alternative → REFUSE; out-of-range count `401` → REFUSE. Thresholds
untouched: `R = 400`, CP upper `<= 0.025`, `4/400` passes and `5/400` fails, never pooled.

## Calibration lock

| presented | outcome |
|---|---|
| no condition argument | **REFUSE** |
| explicit `None` | **REFUSE** |
| wrong type (a string) | **REFUSE** |
| a *different* field's condition | **REFUSE** |
| subtly mismatched (`alpha_1` differs) | **REFUSE** |
| the matching realised condition | accept |

A self-consistent artifact carrying a copy of its own condition is **no longer sufficient**.

---

## Remaining provenance requirement

**This closes condition-consistency enforcement. It does NOT close end-to-end Branch-A
provenance.** The supplied condition is still caller-provided: a driver that passed a copy
of the artifact's own condition would satisfy the check while proving nothing physical.

> **MANDATORY DRIVER REQUIREMENT, NOT YET SATISFIED.** The official campaign driver must
> construct the realised `CalibrationCondition` **mechanically from its own Branch-A
> measurement result**, and that construction must itself be audited. Until then this is
> enforcement of consistency, not of provenance.

Recorded in the plan under `driver_requirements.branch_a_provenance`.

---

## Seed scopes

A case may request only the field scopes in its own frozen `fields_affected`, and the
`experiment` scope is **reserved to the `branch_a_measurement` family**.

### C6 literal scope token — inspected, not assumed

Token: `'synthetic two-mode field at the declared rho'`

| requirement | finding |
|---|---|
| corresponds to C6's actual frozen synthetic object | **yes** — it *is* C6's own `fields_affected` entry, not invented here |
| stable and machine-readable | **yes** — exact-match string |
| cannot collide with a physical field id | **yes** — disjoint from `theta0..3` |
| reproduces serial/parallel stream identity | **yes** |
| does not silently make C6 a four-field case | **yes** — one scope; artifacts `400 x 3 x 1 = 1,200` |

C6 cannot borrow any of `theta0..3`; an unknown token refuses; `experiment` refuses for a
non-Branch-A family. The rho values are the **subcondition**, not the scope, so one token
correctly serves all three.

---

## Stream inventory

Derived independently from `case x subcondition x replicate x family x scope`, **not**
copied:

| case | R | subs | fams | fields | per replicate | streams |
|---|---:|---:|---:|---:|---:|---:|
| C1 | 300 | 4 | 3 | 4 | 13 | 15,600 |
| C2 | 400 | 4 | 3 | 4 | 13 | 20,800 |
| C3 | 400 | 4 | 3 | 4 | 13 | 20,800 |
| C4 | 2,000 | 1 | 3 | 4 | 13 | 26,000 |
| C5 | 400 | 12 | 3 | 4 | 13 | 62,400 |
| C6 | 400 | 3 | 3 | **1** | **4** | 4,800 |
| C7 | 400 | 4 | **2** | 4 | 9 | 14,400 |
| C8 | 200 | 1 | **2** | 4 | 9 | 1,800 |
| | | | | | **TOTAL** | **166,600** |

`per replicate = families x fields + 1 if branch_a_measurement is allowed` (the one
experiment scope).

```
expected    : 166,600
enumerated  : 166,600
unique      : 166,600
collisions  : 0
planner semantics == inventory enumeration : TRUE
```

**Why this differs from the previous 204,000.** That figure was a broader Cartesian
product which (a) gave C6 four physical field scopes it does not declare, and (b) counted
the `experiment` scope in **every** family rather than only `branch_a_measurement`. The
older count enumerated combinations the planner never authorised; it was not an
undercount now.

### Intentional sharing is intact

Restricting scopes did not make every stream independent:

- the Branch-A **common mode** is one experiment-scoped draw, **identical across all four
  fields** of a `(case, subcondition, replicate)`, distinct from every per-field stream,
  and different across subconditions and replicates — so it still cancels in the P2 ratio
  and not in P3;
- the four per-field Branch-A streams remain mutually distinct;
- **C8's two scale factors still share one base replicate stream**; C8 declares one
  subcondition, `paired_scale_control`, and still reaches its common mode.

---

## Output schema

Markdown, JSON and implementation now agree on `e1a_v4_validation_result/2` and
`e1a_v4_validation_manifest/2`, on the 25 record fields including `subcondition_id`, and on
the reproduction recipe naming subcondition and declared scope. `bind_execution` now calls
`require_output_schema_agreement`, so a Markdown/JSON disagreement **refuses before any RNG
exists**; a wrong version and a missing `subcondition_id` are both verified to refuse.

---

## Test-count reconciliation

| suite | previous | candidate | now | delta | reason |
|---|---:|---:|---:|---:|---|
| `validate_e1a_v4_contract.py` | 113 | 113 | **113** | 0 | unchanged |
| `test_e1a_v4.py` | 122 | 122 | **122** | 0 | unchanged |
| `test_e1a_v4_preexec.py` | 94 | 94 | **94** | 0 | unchanged |
| `test_e1a_v4_dispositions.py` | 64 | 64 | **64** | 0 | unchanged |
| `test_e1a_v4_size_semantics.py` | 78 | 78 | **78** | 0 | unchanged |
| `test_e1a_v4_repair.py` | 126 | 126 | **126** | 0 | unchanged |
| `test_e1a_v4_calibration_scope.py` | 102 | 105 | **105** | **+3** | auditor added scope checks |
| `test_e1a_v4_case_scope.py` | 112 | 113 | **113** | **+1** | auditor added a scope check |
| `test_e1a_v4_preexec_corrections.py` | — | 3 groups | **37** | **new** | new gate, now numbered |
| **total** | **811** | — | **852** | **+41** | |

**The 696 figure is arithmetic, not lost coverage.**

```
113 + 94 + 64 + 78 + 126 + 105 + 113 = 693      (seven suites)
693 + 3 (the correction gate's GROUP count)     = 696
```

The auditor's "eight static/pure checks" omitted **`test_e1a_v4.py`** (the
bounded-implementation gate, 122 checks) and counted the correction gate's three *groups*
as if they were checks. **No previously relevant regression coverage disappeared**: every
one of the earlier 811 checks still runs, and four were added. The complete current static
suite is **852 checks across nine suites, 0 failures**.

At adoption the correction gate's bare `assert` statements became counted `verify` calls —
the same boolean conditions, now reported like every other suite and no longer removable by
`python3 -O` — and its completeness coverage was expanded to test each field and each
alternative individually plus extra-key rejection, taking it from 3 groups to 37 checks.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Read from the contract file itself: `delta_cross = 0.02`, `delta_abs = 0.05`,
`z_cross = z_abs = 1.959963985`, `alpha_geom = 0.005`, `alpha_1 = 0.004`,
`alpha_2 = 0.001`, `theta_cap = 5°`, `rank_tol = 1e-12`, primary `sigma_psi = 0.5°`,
complete-pipeline target `>= 0.90`. Derived thresholds recomputed: G1 **188/200**, G2
**4/400**, C2 **5/400**, C3 **2/400**, C4 **13/2000**. The four false-bridge alternatives
are unchanged.

---

## Identity reseal

| item | old | new | outcome |
|---|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | *same* | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | *same* | **UNCHANGED** |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | *same* | **UNCHANGED** |
| **analysis procedure identity** | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | *same* | **UNCHANGED** |
| **seed-map file** | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | *same* | **UNCHANGED** |
| **every seed value** | master `13785910525869478477`, 5 families | *same* | **UNCHANGED** |
| validation plan JSON | `db4ba663c21945413d94de02062e21263e42a9ea4d0432ac9bb749a1bf9d165d` | `7d2395e7bf357cc569c4c93344846fc20dd7a78ac7adc67cdd3743a3746a1af6` | changed |
| validation plan Markdown | `63fe9f669d7911e0c3ea5f685e43ea3c7a0f150fe290a405ec10a332cf5d3745` | `6e590e87d5001b380a27e34da5405600807e8e4f41170e32912c42fb7b2ffccd` | changed |
| **execution identity** | `ff79156c4b878e42598d9c19943bd4532d82b60b4e9aa1b0af269bb8b56b69cb` | `e973ce655a0798bb9da47026cc98bb601973fbe75c4ce55a34da2e5bada55037` | **RESEALED** |
| result / manifest schema | `/2` | `/2` | unchanged in JSON and code; the **Markdown** was corrected from `/1` |
| plan version | `1.5.0` | `1.6.0` | changed |

The **analysis procedure identity did not move** because the candidate touches only
`e1a_v4/validation/`; `git diff --name-only` confirms no analysis-layer module changed. The
**seed map is byte-identical** — the candidate's claim, verified, and nothing required it
to change: restricting *which* scopes a case may request does not alter the derivation of
any stream. The execution identity was resealed because it binds the validation module
hashes and the plan.

---

## Execution state

```
execution_authorised = false

RNG OBJECTS = 0

RANDOM DRAWS = 0

TRAJECTORIES = 0

CALIBRATION EXECUTION = NOT RUN

VALIDATION CAMPAIGN = NOT RUN
```

The official execute command refuses at the `execution_authorised` gate, before any
generator is constructed.

---

## Remaining blocker

```
OFFICIAL CAMPAIGN DRIVER NOT YET IMPLEMENTED / AUDITED
```

Still true, and it is the dominant open item. With it:

- **end-to-end Branch-A provenance is not enforced** — the driver must build the realised
  condition from its own Branch-A result;
- a passing static preflight is **not** an execution clearance.

---

## Post-adoption follow-up: the new invariant caught a latent mispairing

Running the complete package after adoption, `docs/e1a/e1a_v4_execution_feasibility_probe.py`
**failed**:

```
Refusal: calibration tau_modes are not paired with ascending H_A eigenmodes
```

This is the newly adopted invariant working, not a regression. The probe built its
`CalibrationRequest` with `tau_modes` in **declared stiffness order**
(`theta2_ellipse`: `k = (150, 60)`) while `jacobi` returns eigenvalues **ascending**
(`60` first) — the exact mispairing correction A exists to prevent, latent in a committed
artifact of the package and invisible until the invariant existed.

The probe now orders `tau` with ascending eigenvalues, the same one-line rule
`truth_from_field` uses. Isotropic fields were unaffected, which is why it had passed.

Fixed in a follow-up commit; the adoption itself is unchanged.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting coordinate | `c1f2ca13693c6f23e31c9828e063876c500012bf` |
| **work commit** | `8ea81eae353477be0e9b63d0675de40e20c1eca4` |
| **work tree SHA** | `d58afb9e2e4f1f78985c2494106ad0bdf897e5a4` |
| report commit | *this file's commit* |

The candidate document is committed verbatim with an adoption banner; no earlier report is
rewritten.

---

## Next stage

```
E1a v4 official campaign-driver implementation
READY FOR AUTHORISATION
NOT STARTED
```

Preregistration, physical execution, E1b and Stage B remain unauthorised and unstarted.

---

```
PRE-EXECUTION CORRECTION ADOPTED
```
