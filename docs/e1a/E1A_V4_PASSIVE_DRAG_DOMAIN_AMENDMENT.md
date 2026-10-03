# E1a v4 — passive-drag input domain amendment (disposition G6)

**A genuine prospective scientific protocol amendment to the E1a benchmark design.**
It declares the admissible domain of the two Branch-A MEASURED primitives the frozen
Stokes relation consumes. It changes no statistical decision rule, no threshold, no
endpoint, no margin, no coverage factor, no replicate count and no field.

---

## Timing

```text
DECIDED                           PROSPECTIVELY, BEFORE EXECUTION
OFFICIAL CAMPAIGN RESULTS OBSERVED   NO
OFFICIAL SYNTHETIC CAMPAIGN          NOT RUN
TRAJECTORIES                         0
SCIENTIFIC RANDOM DRAWS              0
FINAL EXECUTION SEAL                 NOT FROZEN  (state PRE_DRIVER)
EXECUTION AUTHORISED                 FALSE
```

No outcome has been inspected, so this rule is adopted without any possibility of
post-outcome tuning. `results/e1a_v4_validation` does not exist.

---

## The previous authority gap

| sub-question | before this amendment |
|---|---|
| negative stiffness `lambda_r < 0` | **EXPLICITLY INVALID** — design §14, `REFUSED_BRANCH_A_INVALID` |
| zero stiffness `lambda_r = 0` | **EXPLICITLY INVALID** — "not positive definite" covers it |
| viscosity `eta(T_theta)` domain | **UNSPECIFIED** |
| bead radius `a` domain | **UNSPECIFIED** |
| drag coefficient `gamma` domain | **UNSPECIFIED** — a consequence of the two above |
| relaxation time `tau_r` domain | implementation-only; four code sites, no authority |

The frozen design fixed the *form* — `gamma(T_theta) = 6 pi eta(T_theta) a` and `tau_r = gamma(T_theta)/k_r` —
and the contract's `relaxation_time_rule` restated it. The string `"positive"` occurred
**zero** times in the contract. The repository had already recorded the gap twice: the
driver carries a coded `UNDECLARED_FIELD_INPUTS` refusal naming `viscosity` and
`bead_radius`, and `E1A_V4_BRANCH_A_RELAXATION_DOMAIN_REPORT.md` carries a section headed
**SHARED-DRAG DOMAIN AUTHORITY REQUIRED** that deliberately declined to resolve it.
`E1A_V4_NEGATIVE_STIFFNESS_GAMMA_AUTHORITY_RECONSTRUCTION.md` (F2) established that no
existing authority closed it and that a new human decision was required.

---

## The human decision

> For every E1a field, the Branch-A dynamic-viscosity input eta(T_theta) must be a finite real number strictly greater than zero. The bead-radius input a must be a finite real number strictly greater than zero.

Formally, for every declared field:

```text
eta(T_theta) in R ,   0 < eta(T_theta) < infinity        Pa s
a            in R ,   0 < a            < infinity        m
```

**"Finite real"** means of the declared real numeric representation, and not NaN, not +infinity and not -infinity. A truthy or non-numeric representation is not a number and is never admissible.

### Primitive domains, machine-readable

| primitive | symbol | unit | required | finite | lower bound | inclusive | upper bound |
|---|---|---|:--:|:--:|---:|:--:|:--:|
| `viscosity` | `eta(T_theta)` | Pa s | yes | yes | `0` | no | none |
| `bead_radius` | `a` | m | yes | yes | `0` | no | none |

### The rule binds each primitive INDIVIDUALLY

eta and a are each authoritative domain objects and are validated INDIVIDUALLY. A rule stated only on the product gamma is INSUFFICIENT: eta < 0 together with a < 0 gives gamma = 6 pi eta a > 0 and would masquerade as an admissible passive-drag construction. Neither eta nor a is persisted in the Branch-A publication preimage, so no downstream check can recover them.

Reproduced, not asserted — `eta = -8.9e-4`, `a = -1e-6`:

```text
gamma = 6 pi eta a   = 1.6776104770169493e-08    > 0   FINITE
tau   = gamma / 1e-4 = 0.0001677610477016949     > 0   FINITE
gamma-only rule      ACCEPTS
tau-only rule        ACCEPTS
approved rule        REFUSED_BRANCH_A_INVALID
```

Neither `eta` nor `a` is persisted in the Branch-A publication preimage, so the resulting
record is byte-identical to a legitimate one and no downstream check can recover them.
Both insufficient rules are therefore **named in authority**:

- `gamma > 0 alone, with the primitive eta and a domains unrestricted`
- `tau_r > 0 alone, with the primitive eta and a domains unrestricted`

---

## Missing input and invalid input are different states

| state | meaning | verdict |
|---|---|---|
| `eta` or `a` absent, undeclared, or not supplied through the authorised field-construction source | we do not possess the required physical input | `UNDECLARED_FIELD_INPUTS` |
| `eta` or `a` present and nonfinite, zero or negative | we possess a value, but it is outside the admissible physical domain | `REFUSED_BRANCH_A_INVALID` |
| primitives admissible, derived `gamma` or `tau` not representable in binary64 | the measurement is physically admissible; the executable representation is not obtainable | `BRANCH_A_MEASUREMENT_INVALID` |

All three are **existing repository spellings**. No new refusal category is created.
Missing is resolved FIRST and is never relabelled: an input we do not possess has no
value to be outside a domain. A neutral placeholder value MAY NOT substitute for the actual required measured field-construction input in any path that can produce an official valid Branch-A package. The existing UNDECLARED_FIELD_INPUTS lifecycle is preserved.

---

## Derived quantities

```text
primitive physical domain     eta finite and > 0
                              a   finite and > 0

existing physical domain      lambda_r > 0          design §14, UNCHANGED

derived                       gamma(T_theta) = 6 pi eta(T_theta) a  > 0
                              tau_r = gamma(T_theta)/k_r            > 0
```

`gamma` and `tau` positivity is **DERIVED**. This is one decision and one pre-existing
rule with two consequences, not four unrelated positivity choices. Neither derived
quantity becomes a separately measured primitive and neither acquires an independent
physical sign convention. The frozen Stokes and relaxation relations are unaltered.

---

## Physical admissibility and numerical representability stay distinct

the PHYSICAL-DOMAIN check on eta and a PRECEDES the numerical representability checks on the derived gamma and tau. The two are never conflated and neither is ever substituted for the other.

Physically admissible primitives whose computed binary64 `gamma` or `tau` underflows,
overflows or is otherwise unrepresentable keep the existing `BRANCH_A_MEASUREMENT_INVALID`
semantics and are never relabelled as an invalid `eta` or `a` measurement. The previously
cleared binary64 drag-representability, common-representable-`gamma`, underflow/overflow,
ties-to-even and relaxation-representability rules are **unchanged**, untuned and not
reopened.

---

## Consequence

A present but inadmissible primitive drag input can NEVER yield a VALID Branch-A status, a valid Branch-A publication, a valid calibration condition, a valid calibration lock or a valid Branch-B input. This is DERIVED from the existing REFUSED_BRANCH_A_INVALID lifecycle and introduces no second lifecycle.

---

## Scope

This is a statement about the declared E1a passive equilibrium optical-trap benchmark ONLY. This is NOT a universal physical assertion: negative effective viscosity, negative effective transport coefficients and active-matter effective parameters are OUTSIDE this benchmark, not denied by it.

---

## Non-effects

Unchanged by this amendment:

- `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` — **byte-identical**;
- `docs/theory/EBU_THEORY_BASELINE.md` — **byte-identical** (only its sidecar records the
  new design hash, as at the G1–G3 adoption);
- the stiffness rule: `H not symmetric / not positive definite / dimension mismatch -> REFUSED_BRANCH_A_INVALID`. Every retained mode satisfies lambda_r > 0; lambda_r < 0 and lambda_r = 0 were already invalid and are NOT reopened by this amendment. No
  negative-stiffness category and no "valid unstable trap" branch is created;
- `P1`, `P2`, `P3`, `P4`, `delta_cross`, `delta_abs`, both `z` factors, `alpha_geom`,
  `alpha_1`, `alpha_2`, `theta_cap`, `rank_tol`, the four declared fields, every
  replicate count, every integer boundary and the complete-pipeline target;
- the frozen `relaxation_time_rule` text itself;
- F1 semantics — per-field C2, C3 G5, C4 Block-1, structured refusals, whole-record
  integrity, C1/C7 compositions, C8 paired evidence;
- the actual viscosity values, the viscosity model `eta(T)`, the actual bead radius,
  measurement uncertainty for either, and their hardware provenance.

---

## What remains OPEN

```text
F4 - field construction / absolute drag inputs
OPEN
```

This amendment supplies an admissible **domain** and nothing else. It does not make
field construction execution-ready, and the driver's `UNDECLARED_FIELD_INPUTS` refusal
still blocks an official campaign because `eta` and `a` are still not *declared values*
in frozen authority. A machine check refuses any number appearing anywhere in this
authority other than the declared lower bound itself.

---

## Runtime reconciliation is NOT done here

The runtime remains knowingly behind this authority. `BranchAField.__post_init__`
validates `H_U`, `T` and `scale_factor` only, so production still marks every
inadmissible drag input `VALID`:

```text
eta < 0   a < 0   eta < 0 AND a < 0   eta = 0   a = 0   eta = inf   eta = nan
                     all seven -> status VALID
```

Closing that is **F2e**, a separate authorised stage requiring its own independent audit.
A regression asserts the lag rather than hiding it, and asserts that no production or
recovery module imports the new authority module.

```text
F2 AUTHORITY AMENDED
F2 RUNTIME RECONCILIATION REQUIRED
EXECUTION REMAINS BLOCKED
```

---

## Next stage

```text
F2d INDEPENDENT AUTHORITY AUDIT
NOT STARTED
```

