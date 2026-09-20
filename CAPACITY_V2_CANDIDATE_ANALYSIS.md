# Capacity-V2 candidate analysis and selection

Screens candidate affordability mechanisms against
`EBU_CAPACITY_REQUIREMENTS_V2.md`, using the structural results of
`CURRENT_CAPACITY_FAILURE_THEOREMS.md`. No candidate was selected by simulating
outcomes; selection is by structural reasoning and the matrix below.

## 0. The two properties any candidate must produce

From the failure analysis:

- **Break Corollary 1.1.** V1 has no sink, so repair funds re-damage exactly.
  A candidate must introduce an explicitly accounted sink.
- **Break Theorem 5.** Bounded `V` plus an exactly conservative ledger forces
  `sum_i B_i` to absorb an unbounded external drift. A candidate must bound
  stored capacity by something that does not grow with `J`.

Any rule touches exactly one of four places: the potential, the forcing law, the
receipt rule, or the capacity state law. Candidates below are capacity state
laws unless stated.

## 1. Candidate families, with equations

### A — Persistent absolute capacity (V1, the control)

    B_i' = B_i + Delta B_i,   B_i >= 0

Retained as the registered negative control. Fails both properties by
Corollary 1.1 and Theorem 5.

### B — Physically derived local ceiling

    B_i' = min(B_i + Delta B_i, Phi_i(x')),   C += excess

with `Phi_i` a ceiling derived from local factor geometry. Two instantiations
were considered:

- **B1 (selected, see section 3):** `Phi_i = V_i(x_i)`, the cell's own current
  local potential.
- **B2 (rejected):** `Phi_i = q |mu_i|`, one quantum of local marginal.

**B2 is rejected on principle, not on outcome.** It is dimensionally valid and
parameter-free, but `q` is an *action-menu* quantity. The programme
reconciliation records the finite menu as "an experimental menu restriction, not
proof that all physically divisible quantities have been enumerated", so making
the capacity law depend on the menu would let an experimental convenience enter
a physical rule. `V_i` depends only on the declared field and the state.

### C — Finite-lifetime / decaying capacity

    B_i' = (1 - lambda) (B_i + Delta B_i)

Requires a timescale. The only measured candidate timescale in the programme is
the Stage-B relaxation lag of 32, which was **identical in both arms** and is
therefore a property of the physical process, not of the mechanism — and taking
it from a registered result would set a model parameter from observed outcomes.
No timescale is derivable from the declared objects (reference, scales, quanta,
topology) alone. **Rejected on R15.** Also breaks exact accounting unless a sink
term is added.

### D — Episodic / causally bounded capacity

Capacity tied to the external deviation lot that justified it, retired when the
episode closes. Attractive in principle, but identifying which external
disturbance a given repair discharges requires provenance that is not locally
available: a cell cannot know, from its own factor, which lot its receipt
belongs to. **Rejected on R8 (locality)**, with the note that its *local*
special case — retire `B_i` when `x_i = x*_i` — is exactly the knife-edge limit
of B1 and is subsumed by it.

### E — Relative / normalized affordability

    affordable iff B_i + Delta B_i >= 0  and  |Delta B_i| <= kappa * S_i

for some scale `S_i`. Leaves the account arithmetic and the V1 identity
untouched, which is its main attraction. But it requires `kappa`, and — decisively
— it does **not** bound `B_i`. Theorem 5 still applies: `sum_i B_i` still
diverges. It changes who may spend, not how much accumulates. **Rejected on R7
and R15.**

### F — Current-state headroom / reserve

Constrain destructive affordability by currently available physical headroom
rather than accumulated history. This is the right *intuition*, and B1 is its
concrete realization: `V_i` is precisely the locally measurable headroom in
Gaussian geometry — the deviation the cell is currently carrying. Treated as
realized by B1 rather than as a separate candidate.

## 2. Comparison matrix

No weighted score is computed. `Y` = yes, `N` = no, `~` = partial.

| Criterion | A (V1) | B1 | B2 | C decay | D episodic | E relative |
|---|---|---|---|---|---|---|
| 1. Stage-A cycling still possible | Y (Thm 2) | **N** (Thm V2-1) | N | ~ | N | Y |
| 2. Capacity bounded under stationary forcing | N (Thm 5) | **Y** | Y | Y | ~ | **N** |
| 3. Gate necessarily vanishes asymptotically | Y | **N** | N | N | N | Y |
| 4. Exact accounting possible | Y | **Y** (extended) | Y | only with sink | ~ | Y |
| 5. Locality preserved | Y | **Y** | Y | Y | **N** | Y |
| 6. Arbitrary constants required | none | **none** | none (but menu-dependent) | **lambda** | episode rules | **kappa** |
| 7. Physically interpretable | Y | Y | ~ | ~ | Y | ~ |
| 8. Action compositionality preserved | Y | Y | Y | Y | ~ | Y |
| 9. Implementable without touching historical engines | Y | **Y** | Y | Y | N | Y |
| 10. Falsifiable with random actors | Y | **Y** | Y | Y | Y | Y |

## 3. Selection

**Selected: B1 — deviation-bounded local capacity (DBLC).**

    affordability:  B_i + Delta B_i >= 0        (unchanged from V1)
    settlement:     B_i^raw = B_i + Delta B_i
    ceiling:        B_i'    = min(B_i^raw, V_i(x'))
    retirement:     C      += sum_i (B_i^raw - B_i')
    invariant:      B_i <= V_i(x_i) at every observation point
    exact ledger:   V + sum_i B_i + C = J

The ceiling is re-applied after external forcing as well, since forcing changes
`V_i`.

It is the only candidate that satisfies every hard constraint, introduces **no
new constant of any kind**, preserves locality and exact accounting, and
addresses both failure modes at their structural root.

Meaning: *a cell's licence to damage is limited by the deviation it is currently
carrying. Once a cell is back at its reference, its claim is settled and void.*

### Theorems obtainable for B1

**Theorem V2-1 (absorbing reference).** At `x = x*`: every `V_i = 0`, so the
invariant forces every `B_i = 0`. Any group with `delta_G != 0` has `E_G < 0`
because `x*` is the strict minimum of `V`, so `sum_a R_a < 0` and some owner has
`R_a < 0`, giving `B_i + Delta B_i < 0` — unaffordable. Groups with
`delta_G = 0` have `R_a = -mu^T delta_a = 0` since `mu(x*) = 0`, and leave `x`
unchanged. Therefore `x*` is **absorbing**. □

This is the exact negation of Theorem 2, which is what made Stage-A cycling
structurally unavoidable under V1.

**Theorem V2-2 (bounded capacity).** `sum_i B_i(t) <= sum_i V_i(x_t) = V(x_t)
<= V_max` for all `t`, with `V_max` derived (300 for the registered world). □

Contrast: V1 reached a median `sum_i B_i` of 5400 against the same ceiling of
300.

**Theorem V2-3 (settled local cycle).** If a closed excursion returns cell `i`
to `x*_i`, then `B_i = 0` at that moment, so the excursion's net capacity gain
is zero. More generally `Delta B_i <= V_i` over any excursion. □

Note the honest limitation: the strong form `Delta B_i <= 0` for *every* closed
local cycle is **not** provable, only the bounded form.

**Theorem V2-4 (exact extended ledger).** Settlement preserves
`V + sum B + C = J` exactly, and `C` is monotone nondecreasing.

*Proof.* Before capping, `V(x') + sum_i B_i^raw + C = J` by Theorem 1 applied to
the uncapped update. Capping moves `Delta = sum_i (B_i^raw - B_i') >= 0` from
`B` to `C`, leaving the sum unchanged. For forcing, `J` increases by
`V(z) - V(x)` while `V` increases by the same, and the subsequent cap again
moves mass from `B` to `C`. □

### Known limitation, recorded before execution

The ceiling is tight near the reference and slack far from it: for deviation
`d = |x_i - x*_i|` with `sigma = 1`, the ceiling is `d^2/2` while receipt
magnitudes scale like `d`, so the gate is slack once `d > 2`. The mechanism
therefore protects most strongly near the reference. Whether that is sufficient
under sustained forcing is an empirical question for Stage B-v2 and is **not**
assumed here.

### Why this is not a stop condition

`EBU_CAPACITY_REQUIREMENTS_V2.md` and the controlling protocol require a stop if
two or more genuinely distinct models remain equally defensible. They do not:
C, D and E each fail a hard constraint (R15, R8, R7 respectively), A is the
known-failing control, and B2 is a variant of the selected family dominated by a
stated principle rather than by taste. Selection proceeds.

## 4. What was deliberately not done

- No mechanism ranks actions by value; the chooser is unchanged.
- No candidate was simulated before selection.
- No registered Stage-A or Stage-B artifact, preregistration, code identity or
  result interpretation was touched.
