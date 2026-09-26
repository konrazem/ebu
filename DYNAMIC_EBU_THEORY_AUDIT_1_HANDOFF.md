# Dynamic EBU field theory — independent-audit handoff 1

Read-only handoff for the independent auditor. Covers revision 3 of
`DYNAMIC_EBU_FIELD_THEORY_I_FINITE_REVALUATION.md` and its check module.

## 1. Working-tree identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| HEAD at time of writing | `a6dbed5` (unchanged by this work) |
| files added | `DYNAMIC_EBU_FIELD_THEORY_I_FINITE_REVALUATION.md`, `dynamic_ebu_theory_checks.py`, this handoff |
| files modified | **none** |
| protected packages touched | **none** (`demand_driven_ebu`, `gaussian_harness`, `capacity_v2`, `homeostasis` all unchanged) |
| committed | **no** — `AGENTS.md:137` requires explicit authorization |
| checks | **143 deterministic, 0 failed**, exact `Fraction`, tolerance zero |
| randomized search | **none anywhere** |

Foundation suites re-run unchanged: `test_gaussian_foundation` 65/0,
`test_capacity_v2_foundation` 61/0, `test_homeostasis_foundation` 146/0,
`test_restoring_tendency` 26/0, `test_demand_driven_ebu` 935/0 — **1,233
assertions, 0 failures**. The three `*_harness` suites were **not** run: they
refuse without `EBU_ALLOW_MODEL_TRANSITIONS=1`, this task forbids behavioural
simulation, and no package code changed.

## 2. Every theorem withdrawn

| tag | withdrawn claim | why |
|---|---|---|
| S2 | "connectivity forces `p` constant wherever `V` varies" | null bridges join active components with different `p` |
| N2 | edge-order compatibility "is exactly" Theorem II.2's criterion | conflated edge-local settlement (EL) with global representability (GR) |
| **B** | five-requirement impossibility / exclusivity of the scalar class | rested on S2 and N2; exact counterexample; superseded by Theorem DS |
| F1-interp | "the capacity coordinate cannot see the field at all" | F1 gives explicit-`theta` independence at fixed `(x,y)` only |
| V2-desc | "Capacity V2 places field response in affordability" | factually wrong about `capacity_v2/ledger.py` |
| V2-conflict | "V2 contradicts the preserved freedom sentence" | mis-stated mechanism + unproved balance→freedom mapping |
| Q2-2cell | "any two-cell per-coordinate `sigma` change is a scalar revaluation" | dropped Theorem Q1's linear condition |
| R3 | "distinct `omega_a` profiles ⟹ failure unless `f` affine" | cancellation witness with a common factor |
| N3 | `W` unique up to positive affine in the monotone class | arbitrary increasing reparametrization |
| N4 | locality forces coordinate separability | multi-coordinate factors are permitted |
| P1 | strictly increasing `f` ⟹ `f' > 0` | `f(w)=w^3`, `f'(0)=0` |
| G3-nec | "directed checking suffices **iff** strongly connected" | directed tree |
| A3 | "raw V1 mints" (unqualified) | grand total including the field ledger closes at zero |

Also corrected: the class-B witness has **45** states, not 28; the check module
had a `rw == rw` tautology and a hardcoded `True`; a 20,000-trial randomized
sweep was removed and replaced by the exact certificate `R(V_0,C)`.

## 3. New deterministic counterexamples (all exact)

| # | counterexample | refutes |
|---|---|---|
| 1 | chain `a<->b<->c<->d`, `W=(9/4,1/4,1/4,9/4)`, `V=(9/2,1/2,1/2,5/2)`, `p=(2,2,1,1)` | S2, N2, **Theorem B** |
| 2 | the same data on a **ring** — circulation exactly `-1/2` | shows the criterion is about the cycle space |
| 3 | `x_1+x_2=2`, `x*=(0,0)`, `V_0=(2,1,2)`, `V_1=(1/2,5/8,2)` | Q2-2cell |
| 4 | `W=sum x_i^2/2`, `f=w^2/2`, baseline `(3,0,2,1)`, group `{0→1 by 1, 2→3 by 2}`: profiles `3-2s`, `2-8s` non-proportional, common factor **`37/6`** | R3 |
| 5 | `f(w)=w^3` at `w=0` | P1 |
| 6 | directed tree `a→b`, `a→c` | G3-nec |
| 7 | double cancellation: `W(a,q)>W(b,p)`, `W(b,r)>W(c,q)`, `W(c,p)>W(a,r)` | **Theorem AC** — acyclic but not factor-additive |
| 8 | `E_theta=(2,3)`, `E_theta'=(4,3)` — ratios `2` and `1` | **Theorem NU** |
| 9 | `H_1 = max_C V - V`, `H_2 = max_{y~x} V(y) - V` — different admissible sets at 3 of 28 states | **Theorem FB** |
| 10 | moving field: actor ledger `+2`, field ledger `-2`, grand total `0` | A3 wording |

## 4. Corrected and new theorems

**Theorem DS (decisive existence, necessary and sufficient).** On the actual
allowed-transition graph, one persistent `W` with `s(e)=W(x)-W(y)` and
`s(e)=lambda_theta(e)E_theta(e)`, `lambda>0`, exists **iff** (i) all fields agree
on the sign of every edge's EBU where any is nonzero, and (ii) after contracting
universally-null edges the strict orientation is acyclic, with no oriented edge
inside a contracted class. *Verified against an independent brute-force oracle on
**13,851 exhaustive cases** (6561 + 6561 + 729), full agreement.*

**Theorem AC.** Acyclicity does **not** imply factor-additive representability, so
R4-locality is a genuine extra constraint — decidable by linear programming, with
cancellation conditions as obstructions.

**Theorem EP.** Endpoint rule `[V(x)-V(y)]/p(x)`: antisymmetric iff per edge
`ΔV=0` or `p(x)=p(y)`; then exact iff `(1/p_j) ⊥ D` over active components. A
finite n&s algorithm is given; it **accepts the auditor's chain**, reconstructs
its `W` up to an additive constant, **rejects the ring**, and agrees with
exactness on **888 exhaustive assignments**.

**Theorem SR.** Same-ruler revaluation never changes real affordability.

**Theorem NU.** Nonuniform rescaling of two locally available actions ⟹ no single
current scalar ruler. Converse: a ruler exists at a state iff all locally
available nonzero values share one positive factor.

**Theorem FB.** `V` alone does not determine a finite freedom budget; two
derivable, invariance-respecting candidates give different admissible sets.

**Also corrected:** Q1 retained with **both** conditions; two-cell criterion =
`H` proportional **or** reference on the conservation slice; R3′ per-group
common-factor criterion; N2′/N2″; N3′ gauge table; N4′(a)(b); G3 sufficiency only;
A3′ with the external ledger; F1 as explicit-`theta` independence; V2′ verified
against `capacity_v2/ledger.py`.

## 5. Exact statement of static V1 recovery

Freeze `theta_0`, declare the unit `p(theta_0)=1`, take `W := V_{theta_0}`. Then
hypothesis (PATH) holds **identically as an identity of functions**, and for every
group `G` from baseline `z`:

```
C_a = R_a / p(theta_0) = R_a            for every action a
sum_a C_a = E_G = V(z) - V(z + delta_G)
Delta c_i = sum_{a : owner(a)=i} R_a    = the Capacity-V1 settlement, exactly
```

Verified against `gaussian_harness.valuation.value_group`, with the receipts first
asserted **nonzero** so the statement is not vacuous. Rescaling the unit by any
`a>0` changes no affordability decision.

**Nothing corrected in revisions 2 or 3 touches a fixed-field statement.**

## 6. Final verdict recorded in the report

> **DYNAMIC SCALAR CAPACITY SOLVED UNDER AXIOMS R1–R10**, with the n&s rule
> L1 (common orientation) ∧ L2 (acyclicity after contraction) ∧ L3 (factor-additive
> representability = R4).

with the exact boundary: a **magnitude-faithful** wallet (R5-uniform) forces the
scalar-revaluation class, and a **single current nominal ruler** is impossible
under nonuniform rescaling (NU). Settlement uses only the **signs** of the
changing field, never its magnitudes.

Four separated answers: **settlement solved**; **revaluation characterized and
generally negative**; **action freedom** solved only as an admissible set, not as
a budget; **missing physical quantity** = a declared, current-state, localizable
viability level.

## 7. Exact open dynamic questions

1. Which physically motivated dynamic field families satisfy L1–L3?
2. Where may field-health dependence legitimately enter the mechanism? (F1 does
   not settle this.)
3. Affordability vs retirement vs another state-dependent gate, given V2's ceiling
   is retirement.
4. R3‴: does a common receipt factor for *every* group force `f` affine?
5. Relation between restoration, retained capacity and useful future freedom.
6. Across disconnected reachable components, is a common `p` declared?

## 8. The two questions put to the auditor

1. **Is the STATIC fixed-field bridge now mathematically sound?**
2. **Does the corrected report contain any remaining false universal dynamic
   claim?**

Requested response — one of:

```
STATIC BRIDGE ACCEPTED; DYNAMIC THEORY CORRECTLY LEFT OPEN
```

or

```
RETURN FOR CORRECTION
```

with **one exact counterexample**.
