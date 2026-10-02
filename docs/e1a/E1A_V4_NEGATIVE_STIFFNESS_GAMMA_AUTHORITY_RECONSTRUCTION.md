# E1a v4 — negative-stiffness / γ-sign authority reconstruction (F2)

**READ-ONLY.** No scientific authority, implementation or verifier was modified.
This report determines what existing authority says about the admissible domain
of the Branch-A measured quantities, and whether a new human scientific decision
is required.

```text
COORDINATE
  HEAD    1bcdd582ddb4b899902dc188b6fcb17320c6d3b9
  TREE    76ffe15cefd430a083a7905aaf4e4dbb5efba111
  tree    clean
  F1      DRIVER / CLASSIFIER IMPLEMENTATION INDEPENDENTLY CLEARED
```

---

## Headline

```text
NEGATIVE STIFFNESS   EXPLICITLY SPECIFIED by the prospective design
ZERO STIFFNESS       already cleared; unchanged by this reconstruction
ETA, BEAD RADIUS     UNSPECIFIED  -> new human scientific decision required
GAMMA                UNSPECIFIED  (a consequence of the above)
RELAXATION TIME      implementation-only; derivable once eta and a are fixed
```

The repository already *knows* the drag domain is open: the driver carries a
coded `UNDECLARED_FIELD_INPUTS` refusal naming `viscosity` and `bead_radius`, and
`E1A_V4_BRANCH_A_RELAXATION_DOMAIN_REPORT.md` carries a section headed
**"SHARED-DRAG DOMAIN AUTHORITY REQUIRED"** that deliberately declined to resolve
it. This reconstruction confirms that position still holds at HEAD, and adds one
case that earlier work did not record.

---

## 1. Authority inventory

| source | what it says about these domains | classification |
|---|---|---|
| `EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | "This sign correction is guaranteed for a **positive-definite** quadratic potential. It is **not** a universal sign theorem for arbitrary nonconvex potentials." | positive-definiteness as a **premise of a theorem**, not a measurement-domain rule |
| `EBU_THEORY_BASELINE.md` §5 | "**For symmetric positive definite `H`:** … `lambda_r` = mode stiffnesses, `sigma_r = 1/sqrt(lambda_r)`" | same — conditional scaffolding |
| `EBU_THEORY_BASELINE.md` (coarse-graining theorem) | "with quadratic `V_x`, `H_x` **positive definite** and `A` of full row rank" | same |
| `E1A_V4_PROSPECTIVE_DESIGN.md` §14 | `REFUSED_BRANCH_A_INVALID   H not symmetric / **not positive definite** / dimension mismatch` | **EXPLICIT CONTROLLING AUTHORITY** for the stiffness domain |
| `E1A_V4_PROSPECTIVE_DESIGN.md` §3 | `tau_r = gamma(T)/k_r` with `gamma = 6 pi eta(T) a` | relation only — **no domain** |
| `e1a_v4_design_contract.json` `relaxation_time_rule` | "`tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a`; a single `tau_c` for all fields is WRONG and is not used" | relation only — **no domain**. The string `"positive"` occurs **zero** times in the contract |
| `e1a_v4_design_contract.json` refusal vocabulary | lists `REFUSED_BRANCH_A_INVALID` | confirms the status exists |
| validation plan (JSON + Markdown) | per-field `tau_rule` repeated verbatim; declared `k_uN_per_m`, `T_K` | relation only — **no domain for η, a, γ** |
| `E1A_V4_BRANCH_A_RELAXATION_DOMAIN_REPORT.md` | "**What frozen authority does not declare.** The values `eta` and `a`." + "SHARED-DRAG DOMAIN AUTHORITY REQUIRED" | report — **records the gap**, is not itself controlling authority |

**The foundation and baseline never state that a measured E1a field must be
positive definite.** They state what follows *if* it is. That distinction is the
whole of this reconstruction: the E1a prospective design supplies the missing
measurement-domain rule for stiffness, and nothing supplies one for η or a.

---

## 2. Physical quantity / domain table

| symbol | meaning | relation | source of value | declared domain | implementation check | verifier check |
|---|---|---|---|---|---|---|
| `T` | calibrated temperature, K | — | plan `T_K` (298, 318) | none stated | `T <= 0 -> Refusal` | reconstructed via constructor |
| `k_r` | per-mode stiffness, N/m | `H_U = R diag(k) Rᵀ` | plan `k_uN_per_m` | **not positive definite → invalid** (design §14) | `min eig(H_U) <= 0 -> BRANCH_A_INVALID` | status recomputed and compared |
| `λ_i` | eigenvalues of `H_U` | eigen-decomposition | derived | same as `k_r` | via `jacobi` | same |
| `η` | viscosity `η(T)`, Pa·s | — | **driver argument, undeclared** | **NONE** | **none** | not persisted |
| `a` | bead radius, m | — | **driver argument, undeclared** | **NONE** | **none** | not persisted |
| `γ` | Stokes drag coefficient | `γ = 6πηa` | derived from η, a | **NONE** | **none** | reconstructed only as an *interval* from (k, τ) |
| `τ_r` | per-mode relaxation time | `τ_r = γ / k_r` | derived | **NONE** | none at construction | **`τ ≤ 0 → refuse`** in four places |

η and a are **not persisted in the Branch-A publication preimage**.
`reconstructed_branch_a_field` substitutes neutral placeholders (`viscosity=1.0`,
`bead_radius=1.0`) and documents them as "the acknowledged OPEN
field-construction inputs". Downstream, γ exists only as the interval that
`single_gamma_feasible` reconstructs from the recorded `(k_r, τ_r)` pairs.

### The τ > 0 assumption, located

Four implementation sites, **no authority**:

```text
e1a_v4/effective_size.py      phi_of           dt <= 0 or tau <= 0 -> Refusal
e1a_v4/calibration.py         CalibrationCondition  any tau <= 0  -> Refusal
e1a_v4/world.py               WorldConfig      dt >= min(tau_modes) -> Refusal
e1a_v4/validation/campaign_driver.py
                              require_branch_a_measurement_invariants
                                               any tau <= 0 -> BRANCH_A_MEASUREMENT_INVALID
```

---

## 3. Production / recovery consistency

Reproduced at HEAD by pure construction and property reads. No RNG, no
trajectory, no campaign job.

| condition | production status | artifact | recovery verifier | authority |
|---|---|---|---|---|
| `k > 0`, `η > 0`, `a > 0` | `VALID` | published | **ACCEPTED** | design §14 |
| `k < 0` (one mode) | `BRANCH_A_INVALID` | published | REFUSED | design §14 — explicit |
| `k < 0` (both modes) | `BRANCH_A_INVALID` | published | REFUSED | design §14 — explicit |
| `k == +0.0` | `BRANCH_A_INVALID` | **not serializable** (`ZeroDivisionError`) | no record exists | design §14 + cleared zero-stiffness work |
| `k == -0.0` | `BRANCH_A_INVALID` | **not serializable** | no record exists | same |
| `η < 0` (γ < 0) | **`VALID`** | published | REFUSED | **none** |
| `a < 0` (γ < 0) | **`VALID`** | published | REFUSED | **none** |
| **`η < 0` AND `a < 0`** (γ > 0) | **`VALID`** | published | **ACCEPTED** | **none** |
| `η == 0` (γ == 0) | **`VALID`** | published | REFUSED | **none** |
| `a == 0` (γ == 0) | **`VALID`** | published | REFUSED | **none** |

### Divergences

1. **Negative stiffness** — production publishes a `BRANCH_A_INVALID` record;
   recovery refuses it outright. Already disclosed in the relaxation-domain
   report, deliberately left refusing as the fail-closed direction.
2. **γ < 0 and γ = 0** — production marks the field **`VALID`** and publishes;
   recovery refuses. The status does not record the problem at all, because
   `__post_init__` validates only `H_U`, `T` and `scale_factor`.
3. **`η < 0` AND `a < 0`** — *not recorded by earlier work*. Two physically
   impossible measured quantities multiply to a positive γ, giving positive τ
   and a `VALID` status. The evidence record is **byte-identical** to a
   legitimate measurement:

```text
legitimate (eta>0, a>0): k=(1e-04, 1e-04)  tau=(1.8849555921538757e-04, …)
impossible (eta<0, a<0): k=(1e-04, 1e-04)  tau=(1.8849555921538757e-04, …)
identical: True        eta / a in the publication preimage: NO
```

   No downstream check can distinguish them, **by construction**, because η and
   a are never persisted. This case is the reason the decision below must name η
   and a individually: a rule stated only on γ would not close it.

---

## 4. OU analytical domain analysis

Analytical only — no trajectory was generated.

```text
mode:  dz = -(lambda/gamma) z dt + noise      tau = gamma / lambda
one-step factor  phi = exp(-dt/tau)           stationary variance ∝ 1/lambda
```

| λ | τ (γ > 0) | φ = exp(−dt/τ) | contraction? | stationary variance |
|---|---|---|---|---|
| `λ > 0` | `+1.885e-04` | `0.588` | **yes** | `+1e+04` — positive |
| `λ < 0` | `−1.885e-04` | `1.700` | **no — expansion** | `−1e+04` — negative |
| `λ = 0` | undefined | undefined | — | `H` singular; none exists |

A negative mode stiffness gives `|φ| > 1`, so the recursion diverges, and a
negative stationary "variance", which is not a covariance. **The declared
equilibrium OU model has no valid instance for λ ≤ 0.**

This is *evidence for interpretation*, not authority. It is consistent with the
design's explicit rule rather than a substitute for it.

---

## 5. Historical provenance

| assumption | entered at | date | prospective scientific decision? |
|---|---|---|---|
| `min eig(H_U) <= 0 -> BRANCH_A_INVALID` | `e4b73d7` "Implement adopted E1a v4 analysis pipeline" | 2026-09-28 | implements design §14, which **pre-dates it** |
| `phi_of` refuses `tau <= 0` | `e4b73d7` | 2026-09-28 | **no** |
| `CalibrationCondition` refuses `tau <= 0` | `5727e10` "Repair E1a v4 validation calibration and seed enforcement" | 2026-09-28 | **no** |
| recovery refuses `tau <= 0` | `630282a` "Verify E1a Branch-A measurement invariants on recovery" | 2026-09-30 | **no** |

Every document touching `viscosity` is a **report**, never controlling authority.
The stiffness rule has prospective authority behind it; **the τ/γ positivity
assumptions have never had a scientific decision** — they have always been
implementation artifacts.

---

## 6. Candidate-rule comparison

| rule | classification | why |
|---|---|---|
| **A** — all retained `λ_i > 0`, `γ > 0`, therefore `τ_i > 0`; nonpositive invalidates Branch-A | **λ part REQUIRED; γ part COMPATIBLE BUT NOT REQUIRED** | design §14 forces the λ clause. Nothing in controlling authority states `γ > 0` |
| **B** — `λ = 0` has special already-authorised handling, `λ < 0` invalid, `γ > 0` required | **COMPATIBLE BUT NOT REQUIRED** | authority gives `λ = 0` and `λ < 0` the *same* scientific verdict (both "not positive definite"). The zero case differs only in **publishability**, which is a numerical fact, not a second scientific category. γ clause still unsupported |
| **C** — negative `λ_i` is a valid measured unstable field that merely cannot enter the equilibrium benchmark | **CONTRADICTS AUTHORITY** | design §14 assigns `REFUSED_BRANCH_A_INVALID` — the Branch-A *measurement* is invalid for E1a. No "valid but out-of-domain field" category exists anywhere in the repository |
| **D** — negative or zero γ admitted under some sign convention | **UNRESOLVED** | authority neither admits nor forbids it; it says nothing about η, a or γ sign |
| **E** — authority does not determine one or more of these domains | **REQUIRED** | true for η, a and γ |

### The §19 derivation, premise by premise

```text
P1  declared benchmark = equilibrium stable trap, confining in every mode
    PRESENT — design §14: "H ... not positive definite" -> REFUSED_BRANCH_A_INVALID

P2  Stokes drag for a physical bead in an ordinary viscous fluid -> gamma > 0
    MISSING — authority names the route ("force_displacement_with_stokes_drag")
    and the relation (gamma = 6 pi eta(T) a) and stops. It never states
    eta > 0, a > 0, or gamma > 0.

P3  therefore tau_i = gamma / lambda_i > 0
    NOT REACHABLE — P2 is absent.
```

Premise P2 is **not completed here**. Two reasons beyond the instruction not to:
the repository has already adjudicated this question against completion
(`UNDECLARED_FIELD_INPUTS`, "SHARED-DRAG DOMAIN AUTHORITY REQUIRED"); and the
`η < 0 ∧ a < 0` case above shows that even granting `γ > 0` would leave a record
that no layer can distinguish from a legitimate one. Whether "bead radius" and
"viscosity of an ordinary fluid" *imply* positivity is exactly the scientific
judgement reserved for the author.

### §8 / §9 — what the stiffness rule means

For `λ_i < 0`, controlling authority selects option **B — measurement-invalid /
Branch-A invalid**. On the three-way distinction of §9 it is interpretation (1):
the instrument returned a value that invalidates the Branch-A measurement for
E1a. Authority does **not** support interpretation (3), a valid measurement of a
genuinely unstable field; no such category is declared.

### Zero stiffness and temperature

`λ = 0` is "not positive definite" and therefore already covered by design §14 as
`BRANCH_A_INVALID`. The separately cleared production fact — that it has no
publishable form at all, because `τ = γ/0` raises under every γ — is reproduced
here unchanged and is **not reopened**. `T > 0` is enforced by production as a
hard `Refusal`; the plan declares `T_K` as 298 and 318. Temperature semantics are
not reopened, and no conclusion here depends on them.

---

## 7. Disposition

```text
F2 DOMAIN AUTHORITY:
PARTIALLY SPECIFIED
```

| sub-question | result | human decision |
|---|---|---|
| negative stiffness `λ_i < 0` | **EXPLICITLY SPECIFIED** — `REFUSED_BRANCH_A_INVALID` | **NO** |
| zero stiffness `λ_i = 0` | **EXPLICITLY SPECIFIED** (not positive definite) + already-cleared non-publishability | **NO** |
| positive-definite / stable trap | **EXPLICIT** for the measured field via design §14 | **NO** |
| temperature `T` | not reopened | **NO** |
| viscosity `η` domain | **UNSPECIFIED** | **YES** |
| bead radius `a` domain | **UNSPECIFIED** | **YES** |
| drag coefficient `γ` domain | **UNSPECIFIED** (consequence of η, a) | **YES** |
| relaxation time `τ` domain | implementation-only; **derivable** once η, a and λ are fixed | **NO, once the above is decided** |

```text
NEW HUMAN SCIENTIFIC DECISION REQUIRED:
YES   (for the eta / bead-radius domain only)
```

### The smallest exact decision required

> **Declare the admissible domain of the Branch-A measured quantities `η`
> (viscosity) and `a` (bead radius) for the E1a optical-trap benchmark —
> specifically whether each must be strictly positive — and state the Branch-A
> verdict for a measurement whose `η` or `a` falls outside that domain.**

It must be stated on **η and a individually, not on γ**, because `γ > 0` alone
does not exclude `η < 0 ∧ a < 0`, which is byte-indistinguishable downstream.

Once that is declared, `γ > 0` and `τ_r > 0` follow mechanically from the frozen
relation `τ_r = γ(T)/k_r`, `γ = 6πη(T)a` together with the already-explicit
`λ_i > 0`, and the four implementation τ-positivity sites acquire the authority
they currently lack. **No rule is chosen here.**

This decision is adjacent to, but narrower than, the standing
`UNDECLARED_FIELD_INPUTS` item, which requires η and a to be *declared values* in
frozen authority before the seal is frozen. F2 asks only for their *domain*.

---

## 8. Execution state

```text
OFFICIAL RESULTS            NONE  (results/e1a_v4_validation does not exist)
FINAL EXECUTION SEAL        NOT FROZEN  (state PRE_DRIVER,
                                         expected_execution_identity null)
EXECUTION AUTHORISED        FALSE
OFFICIAL CAMPAIGN           NOT RUN
TRAJECTORY-BEARING SUITE    DEFERRED / NOT RUN
REAL RNG OBJECTS            0
SCIENTIFIC RANDOM DRAWS     0
OU TRAJECTORIES             0
CALIBRATION EXECUTIONS      0
OFFICIAL CAMPAIGN JOBS      0
```

No controlling authority file, implementation file or verifier was modified by
this task. `F1` remains independently cleared and untouched. `F3`–`F8` remain
open.

---

```text
F2 NEGATIVE-STIFFNESS / GAMMA-SIGN AUTHORITY RECONSTRUCTION COMPLETE
```
