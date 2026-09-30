# E1a v4 — Branch-A ties-to-even midpoint repair

Bounded implementation correction to the shared-drag rounding-cell endpoints.

## Result

The auditor's midpoint counterexample was **reproduced at the audited head and
closed**. `k = (2.0, 6.0)` with `tau = (2**-1074, 2**-1074)` was accepted; it is
now refused with the coded measurement category by both the shared publication
verifier and restart.

This closes the residual the two preceding reports carried forward as an open
item — that rounding-cell endpoints were treated as closed, and that a drag value
landing exactly on a midpoint could be counted as a witness.

## Starting coordinate

```text
ccd056f012ad4e5dd36819c2a4891bac0e0f8d26
c4788c5648e5f5060f4bc2ba28f82356c1200cd9
4569904a4f6fd33ccf47e80fcd3a72c2f16d57e4eb89dc6c5c3dd31445cf3da9
```

| | |
|---|---|
| Work commit | `c8b2cc9c901e8c3a77783ae77ebc6f815cd0d351` |
| Work tree | `59273c48237fe0ee7ce0b7001ee3ab6a94cfa1a8` |
| Files changed | `e1a_v4/validation/campaign_driver.py`, `test_e1a_v4_terminal_calibration.py` |
| Scientific modules touched | NONE |
| Frozen authority touched | NONE |

---

## Root cause

```text
midpoint positions correct
midpoint ownership incomplete
```

The exact rational endpoint *locations* `(prev+y)/2` and `(y+next)/2` were and
remain correct. Both were treated as **included** in `y`'s cell. IEEE-754
binary64 division rounds to nearest with **ties to even**, so a real landing
exactly on a midpoint belongs to exactly one of the two neighbours — never both.

### The counterexample, reproduced before editing

With `m = 2**-1074`, the smallest positive binary64:

```text
cell(m) endpoints, as multiples of m :  lo = 1/2      hi = 3/2
G_1 = cell(m) * 2                    :  [1m, 3m]
G_2 = cell(m) * 6                    :  [3m, 9m]
intersection                         :  [3m, 3m]  -- a single point
```

`3m` is representable, so a closed-endpoint intersection accepted it. Production
disagrees, verified by executing the real division:

```text
fl(3m / 2) = 2m      the tie at 1.5m goes to the even neighbour, 2m
fl(3m / 6) = 0       the tie at 0.5m goes to the even neighbour, 0
```

Neither is the stored `m`. At the audited head:

```text
single_gamma_feasible  -> True
verified_publication   -> ACCEPT
restart                -> CALIBRATION_LOCK_PROVENANCE_MISMATCH
```

As in the two preceding repairs, the restart refusal was on the **lock digest
chain**, not on the measurement, so it was not coverage of this defect.

---

## IEEE ties-to-even rounding cells

For a finite binary64 `y`:

```text
significand even  ->  both midpoints round back to y   ->  cell CLOSED
significand odd   ->  both midpoints go to a neighbour ->  cell OPEN
```

One flag covers both endpoints because **adjacent floats always differ in the
last significand bit**: within a binade the significand increments by one, and at
a binade edge, at the subnormal/normal edge and at zero the lower neighbour's
significand is all ones against the upper one's zero. So a tie is always between
an even and an odd candidate and always resolves to exactly one of them.

`2**-1074` has an **odd** significand, so its cell is open at both ends — which
is precisely why `3m` is not a witness.

Ownership is read from the bit pattern (`struct`), so it is exact by construction
and involves no arithmetic and no comparison.

---

## Boundary coverage

§6 warns against assuming a parity rule holds uniformly. It was validated against
an **independent oracle** — `float(Fraction)`, a correctly-rounded ties-to-even
conversion, a different mechanism from the bit-level rule under test.

| region | values | disagreements |
|---|---|---|
| zero / subnormal (`0, m, 2m, 3m, 4m, 5m, 17m`) | 7 | 0 |
| subnormal / normal transition around `2**-1022` | 3 | 0 |
| ordinary normal | 10 | 0 |
| power-of-two / binade edge (`0.5, 1.0, 2.0, 4.0, 2**60` and predecessors) | 9 | 0 |
| large finite and max finite | 3 | 0 |
| negative values, including `-0.0` | 5 | 0 |
| **920 CONSECUTIVE floats** — 400 from zero up through the subnormals, 400 from `1.0`, 60 across the `2.0` binade edge, 60 across the normal/subnormal transition | 920 | **0** |

The max-finite cell still uses the exact `2**1024` overflow threshold from the
earlier repair; no `inf -> Fraction` failure is reintroduced. Max finite has an
odd significand, so its cell is open — asserted directly.

---

## Common drag predicate

> There exists **one finite binary64** production gamma such that actual binary64
> division yields **every** persisted `tau` exactly.

The architecture from the representability repair is preserved unchanged:

```text
exact tau rounding cell, now WITH ties-to-even open/closed ownership
        -> mapped to gamma space by the exact binary64 rational value of k
        -> intersected across ALL modes first
        -> one binary64 witness sought in the intersection
        -> replayed through the actual production division
```

Ownership is carried through the scaling — an exact nonzero rational maps
endpoints to endpoints and cannot change whether one is included, including
through the order reversal a negative stiffness causes — and through the
intersection, where a tie on an endpoint takes the **conjunction**. A singleton
intersection therefore survives only if **every** contributor includes the point;
one contributor excluding it makes the intersection empty. That is exactly the
auditor's case, and it is asserted in both forms (both contributors excluding,
and only one excluding).

---

## Production replay

After the exact machinery returns a witness `gamma_fp`, a final guard replays it
through the real operation and requires exact equality on every mode:

```text
gamma_fp / k_r == tau_r     for all r,  no tolerance
```

The interval arithmetic is exact, so this should always agree; it is kept as an
independent confirmation through the operation itself rather than through a model
of it. It is deliberately **not a search**: if the witness the exact machinery
produced fails to reproduce the record, that is a defect in this verifier, and it
fails closed rather than trying neighbouring floats and hiding the defect. A test
asserts the replay is present and that no `nextafter` scan appears in the
predicate.

The witness is **verifier-local**: never persisted, never compared against
authority, never treated as a measurement or as field-construction authority.

---

## No tolerance

```text
NO EPSILON / RTOL / ATOL INTRODUCED
```

Asserted by source inspection over all six functions on this path:
`single_gamma_feasible`, `_rounding_cell`, `_significand_is_even`,
`binary64_in_interval`, `interval_contains_binary64`,
`_smallest_binary64_at_least`. No `isclose`, no `rtol`, no `atol`, no numeric
literal tolerance. No product-equality shortcut: the interval path is asserted
structurally intact.

---

## Regressions

| case | result |
|---|---|
| **auditor midpoint** `k=(2,6)`, `tau=(m,m)` | coded REFUSE, publication **and** restart |
| **real-nonempty / float-empty** `k=(1e-4,1e-4)`, `tau=(m,m)` | still REFUSE |
| interval strictly between two adjacent floats | still no witness |
| **common-witness** `k=(1.0,2.0)`, `tau=(1.0, nextafter(0.5))` | still REFUSE |
| zero stiffness, `+0.0` and `-0.0` | still REFUSE |
| mixed zero / nonzero stiffness | still REFUSE |
| max-finite `tau` | still total, no uncoded exception, still ACCEPT |
| subnormal-temperature impossible `H` | still coded REFUSE |
| `H_A` overflow impossible record | still coded REFUSE |
| order-preserving inconsistent shared-drag tuple | still REFUSE |
| `H_A` and `branch_a_status` exact reconstruction | unchanged |
| external authority, identity, seed, plan, route checks | unchanged |

---

## Positive controls

The tightening removes acceptances; it must remove only impossible ones.

- **161 genuine `(gamma_fp, k_fp)` tuples** — seventeen representative drag
  values from `2**-1074` through the subnormals, `2**-1022` and its predecessor,
  ordinary and large magnitudes up to max-finite, against eleven stiffness pairs
  including equal, anisotropic, very small, very large, the binade-edge pair
  `(0.5, 0.25)` and the auditor's own `(2.0, 6.0)` — **all accepted**. The grid
  is 187 combinations; 26 are skipped because their quotient underflows to zero
  or is non-finite, so `canonical_float` refuses them and they are not
  serializable records at all. The work commit message quotes the grid size, 187,
  rather than the 161 actually exercised; the suite prints the exercised count.
- **Exhaustive subnormal sweep**: every drag value `1m` through `300m` against
  four stiffness pairs, 1,192 tuples — **all accepted**. This is the region the
  tightening actually changed, so it is swept rather than sampled.
- The **neighbouring genuine records** at the auditor's own stiffnesses are
  accepted: `gamma = 4m, 6m, 12m` at `k = (2, 6)` all round-trip.
- An unforged production publication is still accepted end to end, and restart
  accepts it.

Zero genuine records rejected.

---

## Open issues

Listed, not resolved:

- negative-stiffness / shared-drag sign-domain authority
  (`SHARED-DRAG DOMAIN AUTHORITY REQUIRED`, carried forward unchanged; the parity
  divergence set is asserted still to be exactly the two negative-stiffness rows)
- absolute drag / field construction (`eta`, `radius`)
- generator identity
- C3/C4 field-to-replicate reduction
- PRNG authority
- C6 inputs
- remaining C8 inputs
- diagnostic aggregator authority

The closed-endpoint residual carried by the two preceding reports is **no longer
open** — it is what this repair fixed.

---

## Execution identity

Computed twice from independent clean `git archive` extractions of the work
commit, never from the working tree. Both agree.

```text
UNSEALED EXECUTION IDENTITY
  2d1ae73233f7dc972ddcab000010d4fac703d29b2eb55408c48c8812982b473c

  previous (pre-repair)
  4569904a4f6fd33ccf47e80fcd3a72c2f16d57e4eb89dc6c5c3dd31445cf3da9
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

`e1a_v4/branch_a.py` is a `SCIENTIFIC_MODULES` entry and is **not modified**.
Verified unchanged: physical foundation, theory baseline, prospective design,
design contract, Markdown plan, JSON plan, seed map, and all 12
`SCIENTIFIC_MODULES`. `git diff --name-only c4788c5 c8b2cc9` touches exactly two
files, neither a scientific module nor frozen authority. No new refusal code;
`refusals.py` is unmodified.

---

## Tests

All pure. Each suite was run with `e1a_v4.validation.generate.ou_observations`
replaced by a counter that aborts on first call, so the trajectory count is
measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 538 | 538 | 0 | no — 0 calls |
| `test_e1a_v4_release_authority.py` | 225 | 225 | 0 | no — 0 calls |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | no — 0 calls |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | no — 0 calls |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4.py` | 122 | 122 | 0 | no — 0 calls |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | no — 0 calls |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no — 0 calls |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no — 0 calls |
| **total** | **1,593** | **1,593** | **0** | **0 trajectories** |

The terminal-calibration suite grows from 491 checks in 17 groups to 538 in 18.
The new group is `I1  ties to even: who owns an exact midpoint`.

**Known deferred test.** `test_e1a_v4_campaign_driver.py` was **not run** — it is
the trajectory-bearing suite and this stage forbids it. Its runtime status is
**not claimed**. Static verification only: it byte-compiles, and all 61 symbols it
imports from the campaign driver resolve against the committed module. No public
signature changed; `interval_contains_binary64` keeps its name and boolean
result, with the witness exposed through the new `binary64_in_interval`.

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

BRANCH-A TIES-TO-EVEN REPAIR COMMITTED
