# SD-03 Pre-Execution Readiness — Atomic generator and finite EBU chain

**Status: PROSPECTIVE. SD-03 is NOT ready to execute.** This document records
what the exact-rational oracle adapter now provides, and the prerequisites that
remain. It registers nothing, adopts nothing, and authorizes no run.

**No scientific execution occurred.** No registered case was run, no official
SD-03 output was produced, no scientific runner, model tick, trajectory,
simulation, AWS, Docker or external service was invoked, and no scientific
outcome was inspected.

---

## 1. The registered scale

From `stage_d_scientific_validation_master_matrix.json`, SD-03,
`computational_feasibility`:

| Quantity | Registered value |
|---|---|
| Case structure | 4 dimensions x 6 potential families x 4 action extents x 2 boundary modes |
| **Cases** | **192** |
| Projections per case | **7** (`primary_evaluations_per_run`) |
| **Evaluations** | **1,344** = 192 x 7 |
| Horizon | one finite action with seven declared chain projections |
| Algorithmic cost class | `O(C*d)`, excluding declared symbolic derivative cost |
| Storage estimate | 134,217,728 B (128 MiB) |
| Hard caps, per run | 600 s wall; 536,870,912 B RSS; 67,108,864 B trace; 7 primary evaluations; max depth 8 |
| Hard cap, study total | 1,073,741,824 B output |
| Seeds | none. `stochastic_rules: FORBIDDEN` |
| Uncertainty | "all registered values and comparisons are reduced-rational exact; tolerance and floating substitution are forbidden" |

The adapter reconciles these itself: `load_sd03_configuration` refuses unless
the parsed axes give exactly 192 cases and 192 x 7 equals the registered 1,344.

### The registered case axes

- **Dimensions** `d in {1,2,4,8}`, canonical zero-based indices, initial state
  `x_i = (i+1)/10`.
- **Six exact potentials:** `V0=0`; `V1=sum(i+1)*x_i`; `V2=sum(i+1)*x_i^2`;
  `V3=sum_{i<j}(i+1)(j+1)*x_i*x_j`; `V4=sum(i+1)*x_i^3`; `V5=(1+sum x_i)^4`.
- **Four action extents** `h in {-1,-1/2,1/2,1}`, displacement
  `Delta x_i = h*(-1)^i/(i+1)`.
- **Two boundary modes:** `CLOSED` with boundary contribution 0; `OPEN` with an
  explicit contribution `h/10` potential-unit included once.

None of this is chosen here. The adapter loads it from the canonical matrix
under digest verification and refuses any other file.

---

## 2. Adapter identity

| | |
|---|---|
| Module | `sd03_exact_oracle.py` |
| SHA-256 | `c16f9b2e280cd5b9af0fce28fdc4a5416e0bb95b4d6b262e6e8ebf5bc28cc38e` |
| Test suite | `test_sd03_exact_oracle.py` |
| SHA-256 | `d1e8bb26d60a48ac7e53de35b5998d615ca39062cf9dc3ac74258bf397a3f233` |
| Imports | `fractions`, `hashlib`, `itertools`, `json`, `dataclasses`, `typing` — stdlib only |
| Project modules imported | **none**, deliberately: an oracle that imported `d0_v29` or `ebu_quote_v30` would be checking those modules against themselves |
| Arithmetic | `fractions.Fraction` throughout; `float` is **refused**, not converted. This is a **type gate**: it stops a float entering, but a caller who deliberately stringifies one (`str(0.1+0.2)`) can still hand in a rounded rational. No check can distinguish that from an intended exact value. |
| Import purity | no module-scope call except frozen `Unit` exponent-vector constants |

### Input schema

| Object | Fields |
|---|---|
| `SD03Case` | `dimension: int`, `potential_id: str` (one of `V0`..`V5`), `extent: Fraction`, `boundary_mode: "CLOSED"\|"OPEN"` |
| `SD03Configuration` | `dimensions`, `potential_ids`, `extents`, `boundary_modes`, `matrix_sha256`, `registered_case_count`, `registered_evaluation_count` |
| `load_sd03_configuration(path)` | a filesystem path to the canonical matrix; refuses on digest mismatch |

### Output schema

| Object | Fields |
|---|---|
| `Unit` | exact integer exponent vector over `("state", "potential", "action_extent")` |
| `Quantity` | `value: Fraction`, `unit: Unit`; `+` and `-` refuse a unit mismatch |
| `ChainValue` | `projection: str`, `quantities: tuple[Quantity]`, `case_id: str` |
| `AccountingLedger` | `case_id`, `entries: ((owner, Quantity), ...)`, `total: Quantity`, `omitted_boundary_residual: Quantity` |
| `case_id` format | `d{dimension}\|{potential}\|h={extent}\|{mode}`, e.g. `d8\|V3\|h=-1/2\|OPEN` |

`ChainValue` carries its projection name, and `finite_ebu_of` accepts only a
value whose projection is `FINITE_EBU`. The registered falsifier "an
intermediate is reported as the final finite EBU" is therefore prevented
structurally rather than tested for.

**These are the adapter's own types, not the registered SD-03 record schemas.**
SD-03 registers `configuration_manifest/v1`, `run_manifest/v1`,
`checkpoint_record/v1`, `trace_row/v1`, `receipt/v1`, `computation_record/v1`,
`limit_decision/v1` and `output_manifest/v1`. **None of the eight is
implemented here** — see prerequisite P4.

---

## 3. Required authority hashes

Four of the five cited authorities are **not present on
`v3.0-local-ebu-foundation`**; they live on the SD programme lineage, which
split from this branch at `8793bda` on 2026-08-17. Each was read from its git
object. Every one is carried by a single undiverged blob across every ref.

| Authority | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| `stage_d_scientific_validation_master_matrix.json` | 148,183 | `e6cd44f8` | `081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81` |
| `ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md` | 41,359 | `82b82d3d` | `eb559a68163571d80bbe564d68a57a915e128090b1dbb26bfd9d1c4ec4a7b8d3` |
| `atomic_generator_foundation_contract.json` | 42,855 | `af244330` | `b204f06bd11e7c605acc8afadbf82021fe5e3c1030e1f3f4c3659e71afd5d8a4` |
| `ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md` | 115,771 | `875f069b` | `80d83942d20745b9edeb3c5c8c05d052a616ef97ac9edb1af494d568acf68669` |
| `atomic_interaction_declaration_contract.json` | 256,881 | `3343c149` | `565cc3947d9a3abc99ece694ec823ad0f945dbb1c7634586bcf43f2e36c2549a` |
| `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` (on this branch) | 40,027 | `09c97b66` | `b164b8079ebafbb86309f1c2a073c3467fc43356a719c95bd89227a1064e9d4a` |

Only the matrix digest is enforced in code (`SD03_MATRIX_SHA256`), because only
the matrix is machine-parsed. The other five are recorded so a future execution
can bind them.

---

## 4. The chain: four projections computable, three not

This is the principal finding of building the adapter, and it is a
**registration gap, not an implementation gap**.

| Link | State | Basis |
|---|---|---|
| `V` | **computable** | the six potentials, registered in `configuration.parameters` |
| `mu = grad V` | **computable** | registered as "mu=grad V"; taken by exact symbolic differentiation of the polynomial — no difference quotient, no step size |
| `f_e` | **REFUSED** | defined only on the edge model; needs `theta_e`, `M_e`, `eta_e` |
| `Psi_e` | **REFUSED** | the accumulated opposition whose derivative is `r_e(J_e) = theta_e + J_e/M_e`; needs `theta_e`, `M_e` — and its derivation is itself registered as pending future Part I work under separate authority |
| `J_e` | **REFUSED** | `J_e = M_e*(f_e - theta_e)` where positive; needs `theta_e`, `M_e` |
| `G_T` | **computable** | the generator authority defines `G_T` by `T_h(z) = z + h*G_T(z) + o(h)`; SD-03's declared `T_h` is exactly affine in `h`, so `G_T(x)_i = (-1)^i/(i+1)` with `o(h)` identically zero |
| `finite EBU` | **computable** | registered comparator "direct finite potential difference", taken as an exact endpoint difference |

**Two of the three registered comparators are implemented.** SD-03 registers
`["direct finite potential difference", "integrated generator chain",
"explicit boundary-accounting form"]`. The adapter provides all three:

| Comparator | Function | Uses |
|---|---|---|
| direct finite potential difference | `project(case, "FINITE_EBU")` | `V` at two endpoints |
| **integrated generator chain** | `integrated_generator_chain(case)` | `V`, `grad V` and `G_T` — `int_0^1 grad V(x + t*h*G_T(x)) . (h*G_T(x)) dt`, integrated **symbolically** term by term, never sampled |
| explicit boundary-accounting form | `accounting_ledger(case)` | the interior difference plus the declared boundary entry |

The second one matters more than its line count suggests. Without an
independent route the registered falsifier "chain value differs from its
independent definition" has nothing to fire on and the acceptance test "exact
cases agree exactly" is vacuous. It is available precisely because it needs
only the three computable links — no edge, no `eta`, no `M_e`, no `theta_e`.
`comparator_agreement(case)` returns both values and their exact difference;
24 covering probes across every dimension, potential and extent agree exactly.

**Why the three are refused rather than supplied.** SD-03's registered
configuration declares dimensions, potentials, action extents and boundary
modes. It declares **no edge, no threshold `theta_e`, no mobility `M_e` and no
efficiency `eta_e`**. The repository's edge law `f_e = mu_i - eta_e*mu_j`,
`J_e = M_e*[f_e - theta_e]_+` cannot be evaluated on an SD-03 case, and
substituting it would import a network model the study does not declare.
`project` raises `UnregisteredProjection` naming exactly what is missing.

That refusal is the design. The registered falsifier "chain value differs from
its independent definition" is precisely what an invented stand-in would trip.

---

## 5. What a future SD-03 execution will prove

Within the declared synthetic cases, and nothing wider:

1. **The derivative link is exact.** `mu` is the symbolic gradient of the
   declared `V`, at exact rational points, with no tolerance anywhere.
2. **The finite value is an endpoint difference.** `V(x + Delta x) - V(x)`,
   computed exactly — never a quadrature, never a series, never a surrogate.
2a. **Two independent routes agree exactly.** The direct endpoint difference
   and the integrated generator chain reach the same rational by different
   algebra, with no tolerance. This is what makes the registered falsifier
   "chain value differs from its independent definition" testable at all.
3. **The generator link closes.** `x + h*G_T(x)` reproduces the declared
   displacement exactly at all four registered extents, so the generator
   authority's `o(h)` really is zero for these cases.
4. **Units reconcile, and mismatches refuse.** Every quantity carries an exact
   exponent vector; combining incompatible units raises.
5. **Boundary accounting closes with one owner per term.** The interior
   difference and the declared boundary exchange are separate named entries,
   each counted once; omitting the boundary leaves exactly `h/10` as residual
   under `OPEN` and exactly zero under `CLOSED`.
6. **No intermediate can be reported as the score.** Structurally enforced.
7. **The registered controls behave.** Constant potential gives a zero
   gradient; the linear potential reproduces its exact finite difference; unit
   mismatch refuses; sign reversal is detected; the omitted boundary term
   leaves an explicit residual; an intermediate substituted for the finite EBU
   fails.

---

## 6. What SD-03 cannot prove, and who owns it instead

| Question | Owner | Why not SD-03 |
|---|---|---|
| Is the finite value in `potential-unit` or `EBU-unit`, and how do they relate? | **unregistered** | The matrix declares both units and no identification. The adapter carries the value in `potential-unit` and never relabels it. See P5. |
| When does a truncated Taylor expansion reproduce the finite effect, and when does it fail? | **SD-04** | SD-03 computes the exact finite difference and the exact gradient; the **gap between them** is SD-04's object. The adapter deliberately contains no series, no step size and no remainder term. The suite records that `finite difference == mu . Delta x` holds for the linear potential and fails for the cubic one — that observation is a boundary marker, not a measurement of the gap. |
| How do sequential, parallel, pairwise and higher-order actions differ? | **SD-05** | SD-03 registers exactly **one** finite action per case (`horizon: one declared finite action per case`). It has no second action, so no interaction quantity exists to measure. |
| Does exact Möbius inversion reconstruct every subset table, including a nonzero empty baseline? | **SD-06** | SD-03 has no subset lattice. One action means one subset. |
| Do these policies keep a stock viable over a long horizon? | **SD-01** | SD-03 has no trajectory, no time, no stock, no reserve and no policy. Its horizon is one action. |
| Are `f_e`, `Psi_e` and `J_e` correct? | **nobody yet** | They are unregistered for SD-03 (§4). Even after registration, validating an edge law needs a declared edge, which SD-03 does not have. |
| Is any of this true of anything real? | **nothing in the programme** | SD-03's `prospective_claim` permits at most `MATHEMATICAL_DERIVATION_PLUS_NUMERICAL_VERIFICATION`, and its non-claims are explicit: "mu is not voltage", "J_e is not automatically conserved", "finite EBU is not inferred from gradient alone". |

---

## 7. Cost readiness: laptop-scale, no AWS

**SD-03 needs no AWS resources and no benchmark.**

- 192 cases x 7 projections = **1,344 evaluations**. The registered cost class
  is `O(C*d)` with `d <= 8`.
- The registered storage estimate is **128 MiB**; the study-total output cap is
  1 GiB.
- The registered per-run caps — 600 s wall, 512 MiB RSS — are per *case*, where
  a case is one finite action in at most 8 dimensions.
- The heaviest object the adapter builds is `V5 = (1+sum x)^4` at `d = 8`,
  which expands to 495 monomials (`C(12,4)`, verified). Building it and taking
  its exact finite difference measured **7.6 ms** on this laptop — one
  isolated timing of one case, not a benchmark, and not one of the 192.

No host, no price, no budget and no benchmark is proposed here, and none is
needed. SD-03 is the cheapest stage in the programme.

---

## 8. Remaining SD-03 execution prerequisites

Execution is blocked on all of these. None is implementation work that could be
done without an author decision or a separate authorization.

| # | Prerequisite | Why it blocks |
|---|---|---|
| **P1** | **Register `f_e`, `Psi_e` and `J_e` for SD-03's declared domain** — or amend SD-03's chain to the four links it can evaluate. | Three of the seven registered projections cannot be computed. `primary_evaluations_per_run` is 7 and `expected_evaluations` is 1,344; with four links the honest figures are 4 and 768. Either the configuration gains the missing parameters or the chain declaration narrows. **This is the one gap that must close first.** |
| **P2** | **Accept the two atomic authorities.** Both carry `status: PROSPECTIVE_DOCUMENTATION_ONLY_UNIMPLEMENTED_UNAUDITED`, both record `candidate_self_accepts: false`, and the generator contract's next stage is `INDEPENDENT_AUTHORITY_AUDIT`, not begun. | SD-03's registered dependency is the *accepted* Atomic Generator and Interaction authorities. They are unaccepted candidates. |
| **P3** | **Register the sign of the `OPEN` boundary contribution.** The matrix declares "explicit contribution `h/10` potential-unit included once" and gives no direction. | The adapter records the boundary as a named additive ledger entry and asserts no direction. An accounting closure predicate needs one. |
| **P4** | **Implement the eight registered record schemas** (`configuration_manifest/v1`, `run_manifest/v1`, `checkpoint_record/v1`, `trace_row/v1`, `receipt/v1`, `computation_record/v1`, `limit_decision/v1`, `output_manifest/v1`). | The adapter computes values; it emits no registered record. Execution produces official outputs, which these schemas define. |
| **P4a** | **Register what the seventh projection IS under `OPEN`.** The matrix says the boundary contribution is "included once in the final finite ledger". The adapter's `FINITE_EBU` projection is the interior difference alone and is boundary-mode independent; the ledger total includes the boundary. Whether the registered seventh chain value is the interior difference or the ledger total is a choice no authority makes. | The two differ by exactly `h/10` under `OPEN`. A recorded "finite EBU" is ambiguous until this is fixed. |
| **P5** | **Register the `potential-unit` to `EBU-unit` identification.** The matrix lists both units; the adapter carries the finite value in `potential-unit` and declares no conversion. | The chain ends in an "EBU-unit" that nothing defines in terms of the potential. |
| **P6** | **Stage E acceptance.** `STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md` is a "prospective authority candidate only". | SD-03's `evidence.prerequisites` are level-2 exact derivations and level-3 interface conformance — the **lightest in the programme**, and they do not name an independent Stage E PASS. But the harness that would host the adapter is still a candidate. |

> **Correction.** An earlier draft of this document, and
> `SD_01_TO_14_MASTER_TEST_REGISTER.md` §5, say SD-03 is *the only* stage
> whose prerequisites omit an independent Stage E PASS. That is **false**:
> SD-03, SD-04, SD-05, SD-10, SD-11, SD-12 and SD-13 all omit it — seven of
> fourteen. SD-01, SD-02, SD-06, SD-07, SD-08, SD-09 and SD-14 require it.
> SD-03 remains the earliest executable stage, because SD-04 and SD-05 depend
> on SD-03 and SD-10 through SD-13 depend on stages further up the chain, and
> because SD-03 alone has no SD-stage prerequisite at all. The conclusion
> stands; the supporting claim was overstated. The register still carries the
> wrong sentence and needs a separate correction.
| **P7** | **Execution authorization for the 192 cases.** | The matrix status is `PROSPECTIVE_NO_EXECUTION_NO_OUTCOMES`; `stage_d_observations` records `configured_run_count: 0` and `executed_run_count: 0`. |

**P1 is the finding that matters.** Everything else is process. P1 says the
registered chain cannot be evaluated as registered, and no amount of
implementation fixes that.

---

## 9. Non-claims

- **No scientific execution occurred.** Zero of 192 registered cases were run;
  zero official outputs were produced. The suite touched 49 of the 192 case
  identifiers and performed 75 counted projections, all as isolated unit
  probes. The count is a **lower bound**, not a census: the counter wraps
  `project` and does not see direct polynomial evaluation. The decisive fact
  is structural — the adapter implements none of the eight registered record
  schemas and never opens a file for writing, so it cannot emit an official
  SD-03 output at all.
- **This adapter is not SD-03.** It is the oracle the matrix names as missing.
  Running SD-03 needs P1–P7.
- **Nothing here is registered or adopted.** The matrix and the cited
  authorities govern; this document and the adapter are subordinate to them.
- **No external validity.** Every value describes declared synthetic
  mathematical cases. `mu` is not voltage, `J_e` is not automatically
  conserved, and finite EBU is not inferred from the gradient alone.
- **No price, host, benchmark or budget** is proposed.
