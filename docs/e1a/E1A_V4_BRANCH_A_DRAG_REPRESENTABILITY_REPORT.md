# E1a v4 — Branch-A shared-drag representability repair

Bounded verifier-conformance correction to the Branch-A shared-drag existence
test. Continues the persisted-publication waterfall from the relaxation-domain
repair (work `729dadd`, report `0a41b6c`), which the independent audit reviewed
read-only.

| | |
|---|---|
| Work commit | `ccd056f012ad4e5dd36819c2a4891bac0e0f8d26` |
| Work tree | `6f122df00beaa146a9ac2a4bf0fe452643d842be` |
| Parent | `0a41b6cf8bab78384f748c2ad94e476eb5d98a99` |
| Files changed | `e1a_v4/validation/campaign_driver.py`, `test_e1a_v4_terminal_calibration.py` |
| Scientific modules touched | NONE |
| Frozen authority touched | NONE |

---

## Auditor counterexample

Reproduced against the unmodified verifier at `0a41b6c` **before** any edit, on a
correctly committed and re-digested Branch-A publication with all other
provenance valid.

```text
k_modes_measured = (1e-4, 1e-4)
tau_modes        = (2**-1074, 2**-1074)

  single_gamma_feasible  -> True
  verified_publication   -> ACCEPT
```

The prior predicate proved only that **some real number** gamma satisfies every
mode's rounding constraint. For this record that real region is genuinely
non-empty — and it lies entirely below the smallest positive representable value:

```text
exact real gamma region   = [2**-1075 * 1e-4, 1.5 * 2**-1074 * 1e-4]
                          ~ [2.47e-328, 7.41e-328]

smallest positive binary64 = 2**-1074 ~ 4.94e-324
```

The auditor's arithmetic is confirmed exactly:

```text
gamma_fp = 0                 -> tau = 0.0
gamma_fp = 2**-1074          -> tau = 4.9407e-320     (>> 2**-1074)
```

So the region contains infinitely many positive reals and **no** binary64. No
production drag value produces the stored relaxation times.

As in the previous repair, the restart path did refuse — but on
`CALIBRATION_LOCK_PROVENANCE_MISMATCH`, the lock digest chain, not as a
measurement. That is not coverage of this defect: a forgery published before the
lock is taken never meets that check.

---

## Production arithmetic

Traced by executing `e1a_v4/branch_a.py`, not by reading the expression.

```python
@property
def gamma(self) -> float:
    return 6.0 * math.pi * self.viscosity * self.bead_radius

@property
def tau_modes(self) -> tuple[float, ...]:
    return tuple(self.gamma / k for k in self.k_modes)
```

`gamma` is a **rounded binary64 product chain** — three left-to-right roundings —
evaluating to one float:

```text
6.0 * pi              = 0x1.2d97c7f3321d2p+4
      * eta           = 0x1.12dc1555e5befp-6
      * a             = 0x1.203616cc4437fp-26   <- the value that divides
```

Verified that this float is **not** the exact real `6·π·η·a`: the product chain
rounds. So the object entering the relaxation calculation is a finite binary64,
and each recorded relaxation time is

```text
tau_r = fl(gamma_fp / k_fp)
```

with no other rounded computation between the drag value and the division.

---

## Correct predicate

> There exists **one finite representable** gamma such that, for every mode,
> `float64(gamma / k_r)` equals the recorded `tau_r`.

The previous predicate answered the strictly weaker question `∃ gamma ∈ ℝ`. The
two are not equivalent near the representational boundaries, and the gap is the
defect.

The bridge between the two statements is exact rather than approximate: IEEE
division is **correctly rounded**, so `fl(g / k_r) == tau_r` holds exactly when
the real quotient `g / k_r` lies in the rounding cell of `tau_r`. The interval
formulation is therefore a faithful restatement of the production map, not an
approximation of it.

---

## Exact interval method

Unchanged where it was correct, extended where it was insufficient.

1. **Real gamma cells.** Each recorded `tau_r` has an exact rational rounding
   cell (`_rounding_interval`, preserved from the previous repair, including the
   `2**1024` virtual-binade endpoint at max-finite). Scaling by the exact
   binary64 rational value of `k_r` gives that mode's gamma region `G_r`, with
   the endpoint order flipped for a negative stiffness.
2. **Intersection.** `G = ∩_r G_r`, in exact `Fraction` arithmetic.
3. **Binary64 witness existence.** `G` must contain a finite binary64.

Step 3 is new. Steps 1 and 2 are the previous work, retained.

The intersection is formed **first** and the witness sought once inside it. Asking
each mode separately whether *some* representable gamma works would be a
different and much weaker test, because the modes share one drag coefficient —
see the multi-mode control below.

Persisted stiffnesses are treated as their exact binary64 rational values via
`Fraction`, never as the decimal text a reader sees, so the predicate stays
aligned with the arithmetic production actually performed.

No tolerance, `epsilon`, `rtol`, `atol` or `isclose` appears anywhere on this
path; the tests assert that by source inspection over all four functions.

---

## Representability helper

`interval_contains_binary64(lower, upper, lower_closed=, upper_closed=)` decides
membership in **closed form**. No float space is enumerated:

```text
witness = smallest finite binary64 satisfying the lower bound
          (strict or non-strict, as the endpoint requires)
accept  <=> witness exists and satisfies the upper bound
```

If the smallest qualifying value fails the upper bound, no larger one can pass,
so one candidate decides the question.

**The `float(Fraction)` trap (§11) is handled explicitly.** Conversion rounds to
**nearest-even**, so it does *not* by itself yield "the smallest float at or above
this rational" — it can land on either side. `_smallest_binary64_at_least`
therefore corrects it exactly: step outward with `nextafter` until the bound is
satisfied, then step back inward while it still is. Every comparison is made in
`Fraction`, never in floating point, and each phase moves at most a couple of
ulps because the nearest-even result is already within one ulp. This is proved by
test, not asserted from intuition about rounding direction.

**Endpoint semantics** are carried exactly through both bounds, so a float lying
exactly on an *excluded* endpoint is not counted as a witness. All four
open/closed combinations are tested directly, including singleton intervals.

**Boundaries.**

| region | handling |
|---|---|
| zero and subnormals | `nextafter` exact; an interval inside `(0, 2**-1074)` has no witness, one reaching `2**-1074` does |
| subnormal/normal transition at `2**-1022` | no constant-spacing assumption; tested both sides |
| max finite | a bound above every finite binary64 returns "none" rather than raising; an interval reaching max-finite finds it |
| beyond `-MAX` | the smallest finite float is the witness |

**Cross-checked against ground truth.** The closed-form helper was compared
against an explicit walk over the floats surrounding each anchor, on **640
interval/endpoint combinations** spanning zero, the smallest subnormal, the
normal transition, ordinary magnitudes, `1e300` and max-finite. Zero
disagreements. The verifier never enumerates; the test may, over a bounded
neighbourhood, and does.

---

## Positive controls

Real production outputs must not be rejected. Computed through the **actual**
production division:

- **57 `(gamma_fp, k_fp)` tuples** — eleven representative finite drag values
  from the smallest subnormal, through `2**-1022` and its predecessor, ordinary
  and large magnitudes, up to max-finite, against six stiffness pairs including
  equal, unequal, very small and large — all **accepted**. Tuples whose quotient
  is zero or non-finite are excluded because `canonical_float` refuses them, so
  they are not serializable records in the first place.
- An **unforged production publication** is accepted end to end by
  `verified_publication`, and restart accepts it.
- Every previously cleared positive control still passes, including genuine
  shared-gamma records over equal, unequal, very small and large stiffnesses at
  three gammas each.

The subnormal-gamma rows matter: the repair rejects records whose region holds no
float, and must still accept records produced *by* a subnormal float.

---

## Negative controls

| case | over the reals | representable | result |
|---|---|---|---|
| auditor fixture `k=(1e-4,1e-4)`, `tau=(2**-1074,2**-1074)` | non-empty | none | REFUSE |
| interval strictly between two adjacent floats | non-empty | none | no witness |
| interval inside `(0, 2**-1074)` | non-empty | none | no witness |
| interval inside the last subnormal gap below `2**-1022` | non-empty | none | no witness |
| interval wholly above max finite | non-empty | none | no witness |
| singleton at a float, either endpoint open | empty | — | no witness |

### Multi-mode: one gamma must serve every mode

The sharpest control, because a per-mode check would pass it:

```text
k   = (1.0, 2.0)
tau = (1.0, nextafter(0.5, +inf))

  mode A alone  -> admits a representable gamma
  mode B alone  -> admits a representable gamma
  intersection  -> exactly the single point 1 + 2**-53
                   which is a midpoint between adjacent floats, not representable
  verdict       -> REFUSE
```

---

## Scope boundary

```text
absolute gamma not selected
eta/radius realizability not decided
negative-stiffness sign-domain authority remains open
```

- **No gamma is chosen.** The witness is a pure internal decision value. It is not
  persisted, not compared against authority, not treated as a measurement, and
  not returned. Tests assert the predicate and helper name no drag coefficient of
  their own, and that `gamma` remains absent from the published evidence schema.
- **Upstream `eta`/radius realizability is out of scope.** This repair concerns
  the binary64 gamma value that actually reaches `tau = gamma / k`. Whether every
  candidate gamma is itself expressible as `6·π·η·a` for authorised `eta` and `a`
  belongs to the open field-construction stage. Current frozen code does not
  require it here, and it is deliberately not attempted.
- **The gamma sign domain is untouched.** The `tau > 0` requirement — equivalent
  to assuming `gamma > 0`, and disclosed in the previous report as
  SHARED-DRAG DOMAIN AUTHORITY REQUIRED — is unchanged. The representability
  test is sign-agnostic and did not need to resolve it, so the §6 stop condition
  was not reached.
- **The parity divergence count is asserted unchanged** at exactly two rows (the
  negative-stiffness class). A test pins the divergence set by equality, so it
  cannot silently grow or silently disappear as a side effect of this change.

---

## Previous repair regressions

All four previously cleared cases re-run and still fixed:

| audited case | status |
|---|---|
| zero stiffness (`+0.0` and `-0.0`) non-realizable | still REFUSE |
| max-finite `tau` boundary | still handled, no uncoded exception, still ACCEPT |
| subnormal-temperature production failure | still coded REFUSE |
| `H_A` overflow production failure | still coded REFUSE |

The new helper does **not** reintroduce a `gamma = 0` escape: zero stiffness is
rejected by the production-domain clause before any interval arithmetic runs.
Also retained: `H_A` and `branch_a_status` exact reconstruction, the
order-preserving inconsistent `tau` forgery, the shuffled-pairing forgery,
equal-stiffness/equal-relaxation, external authority and identity checks, and all
finiteness and domain checks.

The invariant inventory stays at five entries; `TAU_SINGLE_GAMMA` now records the
representability requirement in its verification text.

No new refusal code. `BRANCH_A_MEASUREMENT_INVALID` is semantically exact — a
persisted record production could never have produced — and
`e1a_v4/validation/refusals.py` is unmodified.

---

## Execution identity

Computed twice from independent clean `git archive` extractions of the work
commit, never from the working tree. Both agree.

```text
UNSEALED EXECUTION IDENTITY
  4569904a4f6fd33ccf47e80fcd3a72c2f16d57e4eb89dc6c5c3dd31445cf3da9

  previous (pre-repair)
  ced091f07577c9acdc4839bc2d069e327157ccb2812224a5a85af76373970405
```

| | |
|---|---|
| Official campaign driver | PRESENT |
| Final execution seal | NOT FROZEN (`state = PRE_DRIVER`, `expected_execution_identity = None`) |
| Execution authorised | FALSE |
| Analysis identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **unmoved** |
| Planned jobs | 53,200 |
| Calibration artifacts | 46,000 |

---

## Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

This is verifier conformance only. `e1a_v4/branch_a.py` is a
`SCIENTIFIC_MODULES` entry and is **not modified**; its production behaviour is
reused by calling it. Verified unchanged: physical foundation, theory baseline,
prospective design, design contract, Markdown plan, JSON plan, seed map, and all
12 `SCIENTIFIC_MODULES`. `git diff --name-only 0a41b6c ccd056f` touches exactly
two files, neither a scientific module nor frozen authority.

---

## Open issues

Listed, not resolved:

- negative-stiffness / shared-drag sign-domain authority
- field construction / absolute drag coefficient (`eta`, `a`)
- generator identity
- C3/C4 field-to-replicate reduction
- PRNG authority
- C6 inputs
- remaining C8 inputs
- diagnostic aggregator authority

Carried forward from the previous report and still open: rounding-cell endpoints
are **closed**, so an implied gamma landing exactly on a cell midpoint is
accepted where round-half-to-even would not. Measure-zero and conservative in the
accepting direction. The exact open/closed machinery now exists in
`interval_contains_binary64`, so tightening it is a clean separate bounded task;
it was not done here because §7 directs that the existing cell construction be
preserved.

---

## Tests

All pure. Each suite was run with `e1a_v4.validation.generate.ou_observations`
replaced by a counter that aborts on first call, so the trajectory count is
measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 491 | 491 | 0 | no — 0 calls |
| `test_e1a_v4_release_authority.py` | 225 | 225 | 0 | no — 0 calls |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | no — 0 calls |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | no — 0 calls |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | no — 0 calls |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no — 0 calls |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no — 0 calls |
| **total** | **1,546** | **1,546** | **0** | **0 trajectories** |

The terminal-calibration suite grows from 434 checks in 16 groups to 491 checks
in 17 groups. The new group is `H1  the shared drag value must be representable`.

**Known deferred test.** `test_e1a_v4_campaign_driver.py` was **not run** — it is
the trajectory-bearing integration suite and this stage forbids it. Its runtime
status is **not claimed**. Static verification only: it byte-compiles, and all 61
symbols it imports from the campaign driver resolve against the committed module.
No public signature changed.

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

BRANCH-A DRAG REPRESENTABILITY REPAIR COMMITTED
