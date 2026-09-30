# E1a v4 — Branch-A relaxation domain repair

Bounded constructor/read-domain correction to the Branch-A relaxation
verification mechanism. Continues the persisted-publication waterfall from the
Branch-A invariant verifier repair (work `630282a`, report `61efb8d`), which the
independent audit reviewed read-only at `61efb8d`.

| | |
|---|---|
| Work commit | `729daddb0cf4e86b348a2a7bb426a478de07edb6` |
| Work tree | `e654b4e9742b00403593dd4e45189b2017f8da04` |
| Parent | `61efb8d2a6e0ca63bf73747564fa4dfee5157a9a` |
| Files changed | `e1a_v4/validation/campaign_driver.py`, `test_e1a_v4_terminal_calibration.py` |
| Scientific modules touched | NONE |
| Frozen authority touched | NONE |

---

## Auditor findings

Both counterexamples were reproduced against the unmodified verifier at
`61efb8d` **before** any edit, on a correctly committed and re-digested Branch-A
publication fixture with all other provenance left valid.

### 1. A relaxation tuple production cannot create was ACCEPTED

```text
k_modes_measured = (0, 0)
tau_modes        = (1, 1)

  shared publication verifier -> ACCEPT
  restart                     -> refused, but on the calibration-lock chain,
                                 not as a measurement
```

The exact gamma-interval test admitted `gamma = 0`. Scaling the rounding
interval of `tau` by a zero stiffness collapses it to the single point `0`, so
the intersection over both modes is non-empty and `gamma = 0` presents itself as
a witness — while production evaluates `tau_r = gamma / k_r` and raises
`ZeroDivisionError` under **every** gamma. The witness was for an operation
production cannot perform.

The restart refusal in that reproduction is worth naming precisely, because it
could be mistaken for existing coverage: it was `CALIBRATION_LOCK_PROVENANCE_MISMATCH`,
raised because re-forging the publication breaks the lock's digest chain. The
measurement itself was not rejected, and a forgery published before the lock is
taken would not have met that check at all.

### 2. The largest finite relaxation value raised an UNCODED exception

```text
k_modes_measured = (1.0, 2.0)
tau_modes        = (MAX_FINITE, MAX_FINITE / 2)

  -> OverflowError: cannot convert Infinity to integer ratio
```

`math.nextafter(MAX_FINITE, +inf)` is `inf`, and `Fraction(inf)` refuses. The
exception escaped the read verifier raw, from both the publication path and the
restart path.

### Two further members of the same class, found by sweep

The audited cases are both instances of one defect: *the persisted record must
lie in the image of the production constructor and serializer*. Sweeping the
boundary of that image found two more escapes, each reachable from **finite,
individually well-formed** persisted primitives:

```text
T_measured = 5e-324 (or 1e-310)   -> ZeroDivisionError
      K_B * T underflows to zero, so production's own H property raises

k = 1e300 with T = 1e-300, or scale_factor = MAX_FINITE
                                  -> uncoded Refusal
      H_U * scale / (K_B T) overflows to infinity, which canonical_float refuses
```

Both are repaired here. They were not separately named by the auditor; they are
in scope because §16 requires that no raw overflow or division exception escape
the read verifier for malformed persisted evidence.

---

## Production domain

Determined by **executing** `e1a_v4/branch_a.py`, not by reading the formula.
`BranchAField.tau_modes` is a property computing `gamma / k` per mode, and
`BranchARealisation.from_branch_a_field` reads it, so a stiffness that cannot be
divided by fails at publication rather than at construction.

| stiffness | constructs? | `.tau_modes` | serializes? | status |
|---|---|---|---|---|
| `k > 0` | yes | finite | yes | `VALID` |
| `k < 0` | yes | finite, negative | **yes** | `BRANCH_A_INVALID` |
| `k == +0.0` | yes | `ZeroDivisionError` | **no** | — |
| `k == -0.0` | yes | `ZeroDivisionError` | **no** | — |
| `k` non-finite | **no** — `H_U must be symmetric` | — | no | — |
| `k` subnormal | yes | may overflow to `inf` | no — `canonical_float` refuses | `VALID` |
| `k` large | yes | finite | yes | `VALID` |

The decisive distinction, and the one this repair is built on:

- a **negative** stiffness is a measurement production **can** publish. It drives
  `min eig(H_U) <= 0`, so `__post_init__` sets `BRANCH_A_INVALID` — a legitimate
  recorded outcome, not a refusal.
- a **zero** stiffness has no publishable form **at all**. Construction succeeds
  and the record still cannot exist, because the relaxation property raises.

`+0.0` and `-0.0` are the same problem: Python raises `ZeroDivisionError` for
both divisors, and `k == 0.0` is true of `-0.0`, so one comparison covers both.
This is asserted rather than assumed.

Two further production-domain facts, same method:

- `K_B * T` underflows to zero for a subnormal `T`, so `.H` raises.
- `H_U * scale / (K_B T)` overflows to `inf` for a large stiffness or scale, and
  `canonical_float` refuses to let a non-finite value enter a calibration
  identity.

---

## Shared-gamma verifier

The predicate was:

> Does some gamma exist whose IEEE-rounded divisions are compatible with all
> persisted `(k_r, tau_r)` pairs?

It is now:

> Does some gamma exist such that **every mode's division is defined in
> production** and `fl(gamma / k_r)` equals the recorded `tau_r` for all `r`?

The domain clause is not decoration — it is the entire first defect. A witness
gamma is only a witness if production could have executed every division that
produced the record. `single_gamma_feasible` therefore returns `False` for a zero
stiffness before any interval arithmetic happens, and
`require_branch_a_measurement_invariants` raises the coded refusal with the
production reason spelled out.

The rest of the method is unchanged: each recorded `tau` constrains gamma to an
exact rational interval, and a valid record is one whose intervals intersect.

---

## Gamma domain

**What frozen authority declares.** The design contract fixes the *form*:

```text
relaxation_time_rule:
  "tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a;
   a single tau_c for all fields is WRONG and is not used"
```

**What frozen authority does not declare.** The values `eta` and `a`. The driver
already records this and already refuses an official campaign on that ground
(`UNDECLARED_FIELD_INPUTS`): the Branch-A field construction inputs —
`calibration_route`, `viscosity` and `bead_radius` — are not in the frozen
contract or plan, and must enter the execution identity before the seal is
frozen.

**What production enforces.** Nothing. `BranchAField` applies no validation to
`viscosity`, `bead_radius` or the derived `gamma`. Confirmed by execution:
`eta = 0` yields `tau = 0.0` and `eta < 0` yields negative relaxation times, and
both serialize.

**What this verifier enforces.** Only what is independent of that open question:

- every mode's division must be **defined** (`k_r != 0`);
- some shared gamma must **exist**.

**The absolute drag coefficient remains unresolved and is NOT chosen.** No gamma
value, sign, bound or default is written into the verifier. The tests assert
this positively: the same stiffnesses are feasible at gammas spanning twenty
orders of magnitude, and the predicate's source contains no drag coefficient of
its own.

### SHARED-DRAG DOMAIN AUTHORITY REQUIRED

One consequence of the open domain is raised here rather than resolved, because
resolving it in either direction would be choosing the domain after seeing tests.

The verifier requires `tau_r > 0` for every mode. That check pre-dates this task
and is **left exactly as it was**. It is strictly stronger than anything
production enforces, and it is equivalent to assuming `gamma > 0`: under an
unconstrained gamma, a negative stiffness with a positive gamma yields a negative
relaxation time and production serializes the record. The constructor-parity
table below therefore shows exactly one divergence — the negative-stiffness class
is production-serializable and read-refused.

This is disclosed, not repaired. It is left refusing because that is the
fail-closed direction, because weakening it would open a new acceptance path for
forged negative relaxation times, and because the correct rule follows from the
field-construction authority item that frozen authority has yet to settle.
Deciding it requires declaring the domain of `eta` and `a`.

The two audited defects were repairable without it, so this does not block the
repair: the verifier enforces operation-definedness and shared-gamma existence
without choosing gamma.

---

## IEEE interval implementation

No tolerance, epsilon, `rtol`, `atol` or `isclose` appears anywhere on this path;
the tests assert that by source inspection.

The rounding cell of a float is `[(prev + v)/2, (v + next)/2]` in exact
`Fraction` arithmetic. The failure was only at the outermost finite values, and
the fix is exact rather than defensive:

```text
MAX_FINITE = 2**1024 - 2**971 ,  ulp of that binade = 2**971
=> the value the format WOULD hold next, with unbounded exponent range, is
   exactly 2**1024
```

So the cell of `MAX_FINITE` is an ordinary **finite** rational interval,
`[MAX - 2**970, 2**1024 - 2**970]`, and its upper endpoint is precisely the IEEE
overflow threshold. `_neighbour` returns that exact successor when `nextafter`
saturates to infinity. **This is not a large-finite sentinel standing in for
infinity** — it is the exact mathematical successor, so the arithmetic stays
exact. The most negative finite float is handled symmetrically.

| value | handling |
|---|---|
| `MAX_FINITE` | outer endpoint `2**1024`, exact; cell finite |
| `-MAX_FINITE` | outer endpoint `-2**1024`, exact; cell finite |
| `0.0` | `nextafter` exact both ways; cell symmetric about zero |
| smallest subnormal | `nextafter` exact; no special case |
| smallest normal, and just below it | `nextafter` exact across the binade edge |

Only the two outermost finite values reach the virtual binade at all; the zero
and subnormal neighbourhoods need no special case, and the routine is now total
over every finite float. The endpoints are asserted against closed-form exact
values in the tests, not merely checked for non-explosion.

One property is unchanged and re-stated for the record: the endpoints are
**closed**, so a gamma landing exactly on a rounding midpoint is accepted where
round-half-to-even would send it to the neighbour. That is conservative in the
accepting direction on a measure-zero set and can never reject a genuine
production value. It is listed under open issues rather than silently tightened.

---

## Zero-stiffness result

The forged record refuses with `BRANCH_A_MEASUREMENT_INVALID` from both the
shared publication verifier and the restart path.

It refuses because `tau_r = gamma / k_r` is undefined for `k_r = 0` under every
drag coefficient, so production raises before any such record exists.

**No synthetic invalid representation was invented for zero stiffness.** Genuine
production does not represent this condition at all: it has no publishable form,
because the failure occurs while deriving the relaxation times that the evidence
record requires. This is deliberately different from how production represents a
negative stiffness, which *is* representable, as `branch_a_status =
BRANCH_A_INVALID`, and which remains accepted by the constructor.

---

## Coded errors

No raw numeric exception escapes the read verifier for malformed persisted
evidence. Each condition below is checked with a precise exception set —
`(Refusal, ZeroDivisionError, OverflowError)` around the specific production
expression — not a broad `except Exception`, and a `CodedRefusal` is re-raised
unchanged rather than reclassified.

| persisted evidence (all fields finite and well formed) | before | after |
|---|---|---|
| `tau = MAX_FINITE` | `OverflowError` | `ACCEPT` (realizable) |
| `k = (0, 0)`, `tau = (1, 1)` | `ACCEPT` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |
| `k = (0, k2)` | refused incidentally, by interval disjointness | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]`, by domain |
| `k = (-0.0, k2)` | `ACCEPT` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |
| `T = 5e-324` | `ZeroDivisionError` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |
| `T = 1e-310` | `ZeroDivisionError` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |
| `k = 1e300`, `T = 1e-300` | uncoded `Refusal` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |
| `scale_factor = MAX_FINITE` | uncoded `Refusal` | `REFUSE[BRANCH_A_MEASUREMENT_INVALID]` |

No new refusal code was added, and `e1a_v4/validation/refusals.py` is unmodified
by this commit. The existing `BRANCH_A_MEASUREMENT_INVALID` is semantically exact
for every one of these — each is a persisted record the production constructor
could never have produced — so the refusal vocabulary is unchanged.

A correction to the previous report while the chain is being read: it recorded
the vocabulary as "63 total". The file declares **78 distinct codes** across 80
classes, and is byte-identical at `630282a` and at this commit, so that figure
was a miscount rather than a change. Nothing followed from it.

### The largest finite relaxation time is ACCEPTED, and why

`tau = MAX_FINITE` is **not** rejected for being large. `gamma = 6 pi eta a`
reaches `MAX_FINITE` from finite `eta` and `a`, so `tau = gamma / k` can be the
largest finite float and production serializes the record. This is verified by
running the production path at `gamma = MAX_FINITE` and confirming the recorded
relaxation time really is `MAX_FINITE`. The requirement was *no uncoded
exception*, not rejection, and the constructor-realizability rule decides which
of the two applies.

---

## Constructor/verifier parity

Whether each row is serializable is **measured** by running the production
constructor, derived properties and serializer — never declared in the table.
Where production can write the record, the untouched produced record is read
back; where it cannot, the equivalent forged persisted record is read.

| representative input | production | read verifier |
|---|---|---|
| ordinary positive, equal stiffnesses | serializes, `VALID` | ACCEPT |
| ordinary positive, unequal stiffnesses | serializes, `VALID` | ACCEPT |
| very small nonzero stiffness (`1e-300`) | serializes, `VALID` | ACCEPT |
| large magnitude stiffness (`1e10`) | serializes, `VALID` | ACCEPT |
| one negative stiffness | serializes, `BRANCH_A_INVALID` | REFUSE — **known divergence** |
| both stiffnesses negative | serializes, `BRANCH_A_INVALID` | REFUSE — **known divergence** |
| zero stiffness mixed with a real one | `ZeroDivisionError` | forgery REFUSES |
| both stiffnesses zero | `ZeroDivisionError` | forgery REFUSES |
| negative zero stiffness | `ZeroDivisionError` | forgery REFUSES |

The two divergent rows are the `tau > 0` consequence described under
**SHARED-DRAG DOMAIN AUTHORITY REQUIRED**. The test asserts that this set is
*exactly* those two rows, so the divergence cannot silently grow, and a future
authority decision has a single place to land.

---

## Previous invariants

All retained and re-asserted, with the boundary conditions this repair touched:

- **`H_A` exact reconstruction** — recomputed through the production constructor's
  own `.H` property and compared exactly. Unchanged, and now additionally coded
  when the derivation itself cannot be performed.
- **`branch_a_status` reconstruction** — recomputed from the eigenvalues of `H_U`.
  Unchanged.
- **External authority** — package, seed, plan, contract and route checks, and
  every previously repaired embedded-identity forgery, all still refuse.
- **Domains** — `T_measured`, `scale_factor`, finiteness of every persisted float.
  Unchanged.
- **Order-preserving forgery** — unequal stiffnesses, relaxation sequence left in
  permitted order, one value rescaled enough to break common-gamma
  realizability: still `REFUSE`. Re-asserted inside the new group specifically to
  prove the added domain clause did not make the predicate coarser.
- **Equal stiffness ⟹ equal relaxation time** — unchanged.
- **Positive controls** — genuine shared-gamma records over equal, unequal, very
  small and large stiffnesses, at three gammas each, all still ACCEPT. The exact
  method did not become stricter.

The invariant inventory grows from four entries to five: `H_A_FROM_PRIMITIVES`,
`STATUS_FROM_H_U`, `TAU_SINGLE_GAMMA`, **`RELAXATION_DOMAIN`**, `PRODUCTION_DOMAIN`.

### Unverified constructor invariants

Not zero, and deliberately stated:

1. The gamma **sign/zero** domain — see SHARED-DRAG DOMAIN AUTHORITY REQUIRED.
2. Rounding-cell endpoints are **closed**, so an implied gamma landing exactly on
   a midpoint is accepted where round-half-to-even would not. Measure-zero and
   conservative in the accepting direction.
3. The feasibility test asks for a **real** shared gamma, not a *representable*
   one. Requiring a float witness would be strictly stronger; the gap is an
   interval narrower than one ulp.
4. `viscosity` and `bead_radius` are not persisted, so the recorded relaxation
   times cannot be tied to a specific field construction at all until that
   authority is declared.

---

## Open issues

Listed, not resolved:

- generator identity
- field construction / absolute drag coefficient (`eta`, `a`), including the
  shared-drag domain question raised above
- C3/C4 field-to-replicate reduction rule
- PRNG authority
- C6 inputs
- remaining C8 inputs
- diagnostic aggregator authority

---

## Execution identity

Computed twice from independent clean `git archive` extractions of the work
commit `729dadd`, never from the working tree. Both computations agree.

```text
UNSEALED EXECUTION IDENTITY
  ced091f07577c9acdc4839bc2d069e327157ccb2812224a5a85af76373970405

  previous (pre-repair)
  ad870b15352fb9a7e08c5b29106b9bfb03bd84889327786fcfd0e550139c10d8
```

The identity moves because this repair changes provenance verification code
inside the validation layer, which is exactly what the identity binds.

| | |
|---|---|
| Official campaign driver | PRESENT |
| Final execution seal | NOT FROZEN (`state = PRE_DRIVER`, `expected_execution_identity = None`) |
| Execution authorised | FALSE |
| Analysis identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **unmoved** |
| Contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| Plan | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` |
| Seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` |
| Planned jobs | 53,200 |
| Calibration artifacts | 46,000 |

---

## Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

`e1a_v4/branch_a.py` is a `SCIENTIFIC_MODULES` entry and is **not modified**. The
expectations are obtained by *calling* it — the constructor, `.H`, `.status` and
`.tau_modes` are production's own — so no production formula is restated in the
verifier and the analysis identity does not move. No change to a scientific
module was required, so the §33 stop condition was not reached.

Verified unchanged: physical foundation, theory baseline, prospective design,
design contract, Markdown plan, JSON plan, seed map, `SCIENTIFIC_MODULES` (12
entries). `git diff --name-only 61efb8d 729dadd` touches exactly two files, and
neither is a scientific module or frozen authority.

---

## Tests

All pure. Each suite was run with `e1a_v4.validation.generate.ou_observations`
replaced by a counter that aborts on first call, so the trajectory count is
measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 434 | 434 | 0 | no — 0 calls |
| `test_e1a_v4_release_authority.py` | 225 | 225 | 0 | no — 0 calls |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | no — 0 calls |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | no — 0 calls |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | no — 0 calls |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no — 0 calls |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no — 0 calls |
| **total** | **1,489** | **1,489** | **0** | **0 trajectories** |

The terminal-calibration suite grows from 376 checks in 15 groups to 434 checks
in 16 groups. The new group is `G1  the relaxation domain: production
realizability`.

**Known deferred test.** `test_e1a_v4_campaign_driver.py` was **not run** — it is
the trajectory-bearing integration suite and this stage forbids it. Its runtime
status is **not claimed**. Static verification only: it byte-compiles, and all 61
symbols it imports from the campaign driver resolve against the committed module.
No public signature changed in this repair.

---

## Safety

```text
REAL RNG OBJECTS                 = 0
REAL RANDOM DRAWS                = 0
DETERMINISTIC TEST TRAJECTORIES  = 0
OFFICIAL CAMPAIGN TRAJECTORIES   = 0
CALIBRATION EXECUTIONS           = 0
OFFICIAL CAMPAIGN JOBS           = 0
```

Nothing was pushed. The execution seal was not frozen and execution was not
authorised.

---

BRANCH-A RELAXATION DOMAIN REPAIR COMMITTED
