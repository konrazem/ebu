# Dynamic EBU field theory I — the decisive scalar-capacity theorem

> **SUPERSEDED AS AUTHORITY by `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.**
> Retained as working history. Where this file conflicts with the synthesis, the
> synthesis governs. Do not cite this file as programme authority.


**Revision 3. Correction pass + decisive existence/no-go results.**

> **SUPERSEDED IN PART by `DYNAMIC_EBU_FIELD_THEORY_II_CANONICAL_ATOMIC_NORMALIZATION.md`.**
> Theory II withdraws Theorem DS (it answers existence of *some* ordering, not the
> canonical question), withdraws L3 as too restrictive, and drops L2 as redundant.
> Theory I's preserved results — fixed-field exact EBU, static V1, the
> scalar-revaluation theorem, the magnitude-faithful no-go under nonuniform global
> scaling, same-ruler cancellation and closed-cycle telescoping for a declared `W` —
> stand unchanged. Read Theory II §0 first.
**No simulation. No Stage A/B. No mechanism implementation.**

This report answers one question:

> Can a genuinely changing EBU field support **one persistent scalar capacity per
> actor**, with local exact finite settlement, no closed-cycle minting, no
> historical source/action vectors, and exact recovery of static V1?

**The answer is YES for a sign-aligned persistent wallet, with a complete
necessary-and-sufficient characterization (Theorem DS + Theorem AC), and NO for a
magnitude-faithful one under nonuniform field change (Theorem NU).** §14 states
the verdict; §15 gives the four mandatory separate answers.

Revision 1 contained a valid core surrounded by false generalizations; an
independent audit found them. Revision 2 corrected them. Revision 3 adds the
decisive theorems. §0.1 records every withdrawal.

Checks: `dynamic_ebu_theory_checks.py` — **143 checks, 0 failures, exact
`Fraction`, tolerance literally zero, every check deterministic and exhaustive
over its declared domain.** No randomized search anywhere.

---

## 0.1 Correction record

| # | Revision-1 claim | Disposition |
|---|---|---|
| 1 | S2: "connectivity forces `p` constant wherever `V` varies" | **DISPROVED.** Chain counterexample §5.1; replaced by Theorem EP (§5.2) |
| 2 | N2: edge-order compatibility "is exactly" Theorem II.2's criterion | **DISPROVED.** Conflated edge-local settlement with global representability (§3.3) |
| 3 | Theorem B (five-requirement impossibility) | **WITHDRAWN.** Rested on 1 and 2; the chain is an exact counterexample. Superseded by Theorem DS (§4) |
| 4 | F1 read as "the capacity coordinate cannot see the field at all" | **INTERPRETATION WITHDRAWN.** F1 gives explicit-`theta` independence at fixed `(x,y)`, not independence from physical state (§6.2) |
| 5 | "Capacity V2 puts field response in affordability" | **FACTUALLY WRONG about the code.** V2 affordability = V1; the ceiling is post-settlement retirement (§11) |
| 6 | "Any two-cell per-coordinate `sigma` change is a scalar revaluation" | **DISPROVED.** Dropped Theorem Q1's linear condition (§10B) |
| 7 | R3: "distinct profiles imply failure unless `f` affine" | **DISPROVED.** Witness with non-proportional profiles and common factor `37/6` (§12.3) |
| 8 | strictly increasing `f` ⟹ `f' > 0` | **FALSE.** `f(w)=w^3`, `f'(0)=0` (§3.5) |
| 9 | `W` unique up to positive affine in the monotone class | **FALSE.** Arbitrary increasing reparametrization (§3.4) |
| 10 | locality forces `W = sum_i W_i(x_i)` | **TOO STRONG.** Narrowed to factor-additive `W`; converse settled negatively by Theorem AC (§8) |
| 11 | G3 "suffices iff strongly connected" | **NECESSITY WITHDRAWN.** Directed tree counterexample (§6.1) |
| 12 | "Raw V1 mints" (unqualified) | **WORDING CORRECTED.** The grand total including the external field ledger closes at zero (§7) |
| 13 | "the class-B witness … 28 states" | **COUNT WRONG.** 3 cells at `M=8` have **45** states |
| 14 | `V1-1` contained `rw == rw`; `G6` asserted a hardcoded `True` | **TAUTOLOGIES REMOVED** |
| 15 | 20 000-trial randomized sweep offered as support | **REMOVED**, replaced by the exact certificate `R(V_0,C)` |

**Retained:** exact finite frozen-field EBU; actor/field telescoping under a
declared event order; the scalar-revaluation theorem and its normalized
settlement; static V1 recovery (now with its path hypothesis stated);
fixed-field aggregate closed-cycle telescoping; graph cycle-space exactness in
its properly stated form.

---

## 1. Frozen requirements R1–R10

A valid dynamic scalar capacity must satisfy:

| | requirement |
|---|---|
| **R1** | one persistent scalar `c_i` per actor |
| **R2** | no stored historical field vector, source portfolio, action-dependency vector or path history |
| **R3** | exact finite actions |
| **R4** | locality: settlement/admissibility use only declared local present physical information plus `c_i` |
| **R5** | a static field recovers Capacity V1 exactly after unit normalization |
| **R6** | actor-only closed cycles cannot increase aggregate `c` |
| **R7** | external field changes are separately accounted and not attributed to actors |
| **R8** | settlement stays **positively aligned** with current EBU action valuation wherever a conversion is claimed |
| **R9** | the same physical ruler is used on earning and spending |
| **R10** | theorems are stated on the **actual allowed-transition graph**, not on a complete graph |

**R5 is ambiguous and the disambiguation is decisive.** Two readings:

- **R5-limit** — in a world whose field never changes, the mechanism reproduces V1.
- **R5-uniform** — at *every* frozen instant of a dynamic trajectory, settlement
  equals that field's V1 settlement up to one positive constant per field.

R5-uniform is strictly stronger and, as §4.4 shows, forces Theorem I outright.
Both are answered.

---

## 2. Definitions

`G = (X, A)` the reachable action graph, one oriented edge per allowed finite
action; `C` a connected component. For each field `theta`,
`E_theta(e) = V_theta(x) - V_theta(y)` for `e : x -> y`. A **settlement cochain**
`s` is antisymmetric on reversible edges; it is **exact** iff `s(x->y) = W(x) - W(y)`.

Sign convention: *before minus after*, so positive means the action improved the
field.

**Two questions never again conflated:**

- **(EL)** edge-local settlement — does an exact `W` exist on the *allowed action
  graph*? Constrains adjacent pairs only.
- **(GR)** global representability — is `V_theta = f_theta(W)` at *every* state?
  Constrains all pairs.

**(GR) ⟹ (EL); (EL) does not imply (GR).** §5.1's chain is the witness.

---

## 3. Corrected foundations

### 3.1 Actor/field decomposition — RETAINED

`E_actor = V(x_t;theta_t) - V(x_{t+1};theta_t)`,
`E_field = V(x_{t+1};theta_t) - V(x_{t+1};theta_{t+1})`.

**Theorem D1.** `V(x_t;theta_t) - V(x_{t+1};theta_{t+1}) = E_actor + E_field`,
exactly (the terms telescope). ∎

**Theorem D2.** The split is **order dependent**: the two orders differ by the
mixed second difference, which vanishes identically iff `V(x;theta) = a(x)+b(theta)`.
Under Theorem I it equals `(p(theta_t)-p(theta_{t+1}))(W(x_t)-W(x_{t+1}))`.
*(Checked: `D1`, `D2`.)* Causal reading therefore requires a **declared event
order**, actors unable to move `theta`, and field motion recorded by
**provenance** rather than inferred from the potential.

### 3.2 Theorem I — exact scalar revaluation — RETAINED

**Theorem I.** `V_theta = p(theta) W + k_C(theta)` on `C` with `p > 0` **iff** the
centered family `{V_theta - V_theta(x_0)}` has rank `<= 1` and all members lie in
one open ray. Equivalently (Theorem I.5, on a connected component) the
**edge-ratio test**: `E_theta(e)/E_{theta_0}(e)` is independent of `e` and
positive, with zero-difference edges preserved.

**Consequences.** `E_theta = p(theta)[W(x)-W(y)]`; `Delta c = E_theta/p(theta) =
W(x)-W(y)`; fixed-field closed cycles telescope to zero; and (Theorem I.4) the
normalized sum telescopes for **any** field path sharing one `W`.

**Gauge, stated with its exact scope.** In **Theorem I's class only**, `(W,p,k)`
is unique up to `W -> aW+b`, `a>0`; setting `p(theta_0)=1` makes `W = V_{theta_0}`
up to a constant.

| family on the 3-cell conserved lattice (28 states) | Theorem I? | `p` |
|---|---|---|
| common `sigma` scaling `sigma -> 2 sigma` | **yes** | `1/4` |
| reference shift along `H^{-1} 1` | **yes** | `1`, `k = 3/8` |
| per-coordinate `sigma = (1,1,1) -> (1,1,2)` | **no** | — |
| generic moving reference | **no** | — |

*(Checked: `I-A`…`I-G`, exact on all 28 states and 126 oriented edges.)*

### 3.3 Lemma N2 — CORRECTED

**Lemma N1.** At a frozen `theta`, `s := E_theta` is already exact with
`W = V_theta`. So "there exist edge weights making the cochain exact" carries
**zero** information.

**Lemma N2′.** With unrestricted positive edge weights, a target `W` works iff on
**every edge** all fields agree with `W` on the sign of the difference — an
**adjacent-pair** condition only.

**Lemma N2″.** (EL) is **strictly weaker** than (GR). §5.1's chain has an exact
edge-local `W` with `W(a)=W(d)` while `V(a) != V(d)`, so `V` is not a function of
`W` and Theorem II.2's criterion fails. The states `a` and `d` are non-adjacent,
so no edge compares them. *(Checked: `W7`.)*

### 3.4 Gauge freedom — CORRECTED

| class | gauge freedom of `W` |
|---|---|
| Theorem I (scalar revaluation) | `W -> aW + b`, `a > 0` — **positive affine only** |
| Theorem II (monotone common `W`) | `W -> h(W)` for **any** strictly increasing `h` |

*Witness:* `h(w)=w^3+w` on `W=(0,1,2)` gives `(0,2,10)`: same ordinal structure,
settlement of `s0->s2` moves from `-2` to `-10`. *(Checked: `P2`.)*

**Consequence.** In the monotone class the field family does **not** determine a
settlement — `W` must be separately declared. Only in Theorem I's class is `W`
pinned by the physics up to units.

### 3.5 Positive derivative — CORRECTED

A strictly increasing differentiable `f` satisfies only `f' >= 0`. *Witness:*
`f(w)=w^3`, `f'(0)=0`. **Chord slopes stay strictly positive**, so `p_eff > 0`
survives; `p_local = f'(W) > 0` does not, and `dW = dV/f'` needs the explicit
assumption `f' != 0`. *(Checked: `P1`.)*

### 3.6 Theorem II and its finite criterion — RETAINED for (GR) only

**Theorem II.** `E_theta = p_eff * Delta W` exactly, with
`p_eff(theta;x,y) := [f_theta(W(x))-f_theta(W(y))]/[W(x)-W(y)] > 0`. `p_eff` is a
**chord slope on an ordered pair**, not a state price.

**Theorem II.2.** For finite `C`, **(GR)** holds iff all `V_theta` induce the same
weak order — same strict comparisons *and* same ties. *(Checked: `W1`.)*
**Scope: (GR) only.** Per §3.3 it must not be used for (EL).

**Theorem II.4 / II.5 (rigidity).** In the continuum, on a slice of dimension
`>= 2`, quadratic `V_1 = h(V_0)` with `h` increasing forces `h` affine (the level
set is Zariski dense in an irreducible quadric, so `V_0 - c` divides
`V_1 - h(c)`). **On a finite lattice this FAILS**: 3 cells at `M = 8` (**45**
states) with `V_0`: ref `(-6,-6,-12)`, `sigma=(1/4,4,5/4)` and `V_1`: ref
`(-3,21,3/4)`, `sigma=(1,8,8)` have identical weak orders and no `(p,k)`.
The exact per-world certificate

```
R(V_0, C) := dim { q quadratic on the slice : q constant on every level set of V_0 in C }
```

with `R = 2` **proves** rigidity. `R = 2` for ref `(2,2,2)`, `sigma=(1,1,1)`;
`R = 3` for `sigma=(1,1,2)`; `R = 6` for an injective reference.
*(Checked: `W2`–`W4`, `W6`.)*

---

## 4. THEOREM DS — the decisive existence theorem on the sparse action graph

This is the central new result. It is stated on the **actual allowed-transition
graph** (R10), never on a complete graph.

**Problem.** Given a finite reachable action graph `G=(X,A)` and a family of
fields `{V_theta}`, find **one** persistent settlement potential `W : X -> R` with

```
s(e) = W(x) - W(y),      and      s(e) = lambda_theta(e) E_theta(e),  lambda_theta(e) > 0
```

for every field and every action edge of nonzero EBU.

### 4.1 Edge classification (§3A)

For each edge `e`:
- **universally null** — `E_theta(e) = 0` for every `theta`;
- **universally active** — `E_theta(e) != 0` for every `theta`;
- **mixed** — zero under some field, nonzero under another.

### 4.2 The two readings of the mixed case (§3F)

- **Weak reading** — the conversion condition applies only where `E_theta(e) != 0`.
  A mixed edge then behaves as a strict edge: it settles a **nonzero** amount even
  under the field that values it at exactly zero.
- **Strong reading** — a field valuing an action at zero forces `s(e)=0`. Then a
  mixed edge is **contradictory**, so existence requires the **zero-set of
  `E_theta` to be the same for every field**.

*(Checked: `DS-F`, both readings, on the minimal two-state instance.)* The weak
reading is used below; the strong reading simply adds "no mixed edges".

### 4.3 Theorem DS

**Theorem DS (necessary and sufficient).** Such a `W` exists **iff**

> **(i) Common orientation.** For every edge, all fields whose EBU is nonzero
> there agree on its sign.
>
> **(ii) Acyclicity after equality contraction.** Contract every universally null
> edge; orient every remaining edge by its common EBU sign. The resulting digraph
> must be **acyclic**, and no oriented edge may fall inside a contracted class.

*Proof.* (⇒) `W` is constant on contracted classes (universally null edges settle
zero) and strictly decreasing along each oriented edge (positivity of `lambda`);
a directed cycle would give `W(x) > W(x)`, and an oriented edge inside a class
would give `W(x) > W(x)`.
(⇐) If the contracted digraph is acyclic, take any linear extension and assign
`W` strictly decreasing along it, constant on classes. Then `W(x)-W(y) > 0`
exactly on oriented edges and `= 0` on null edges, so
`lambda_theta(e) := [W(x)-W(y)]/E_theta(e) > 0` wherever `E_theta(e) != 0`. ∎

**Verified against an independent oracle, exhaustively.** A brute-force search
over integer `W` in `{0..n-1}` (complete, since a DAG always admits such a `W`)
was compared with the criterion over **every** two-field family drawn from a
declared value grid: **6561/6561** on a 4-path, **6561/6561** on a 4-ring,
**729/729** on a triangle — **13,851 exhaustive cases, full agreement**.
*(Checked: `DS`.)*

### 4.4 What Theorem DS does and does not deliver

| requirement | status under Theorem DS |
|---|---|
| R1 one persistent scalar | **yes** — `W` is a single state function |
| R2 no history | **yes** — `W` is a state function; nothing is stored |
| R3 exact finite | **yes** — `Delta c = W(x)-W(y)` exactly |
| R6 no closed-cycle minting | **yes** — a potential difference telescopes to zero |
| R7 external field separately accounted | **yes** — `W` is field-independent, so field motion settles zero to actors |
| R8 positive alignment | **yes** — by construction `sign(Delta c) = sign(E_theta)` |
| R9 same ruler earning/spending | **yes** — one `W` for both |
| R10 sparse graph | **yes** — stated on `G` |
| **R4 locality** | **NOT automatic** — see Theorem AC (§8) |
| **R5-limit** | **yes** — take `W := V_{theta_0}` in a static world |
| **R5-uniform** | **NO** — forces Theorem I |

**Why R5-uniform forces Theorem I.** If at every frozen field the settlement must
equal that field's V1 settlement up to one positive constant `p(theta)`, then
`W(x)-W(y) = E_theta(x->y)/p(theta)` for every edge and every field — which is
precisely the edge-ratio test, hence `V_theta = p(theta)W + k_C(theta)`.

**So the magnitudes of the changing field do not enter Theorem DS's settlement —
only the signs do.** That is exactly what R8 asks ("positively aligned"), and
exactly what makes the theorem so permissive. Demanding that magnitudes be
faithful is the stronger question answered negatively in §9.

---

## 5. The endpoint normalizer — exact graph characterization

### 5.1 The counterexample that disproved revision 1

Reversible chain `a <-> b <-> c <-> d`:

```
W = (9/4, 1/4, 1/4, 9/4)     V = (9/2, 1/2, 1/2, 5/2)     p = (2, 2, 1, 1)
```

On **every** orientation `[V(x)-V(y)]/p(x) = W(x)-W(y)` exactly, while `p` is not
constant, `W(a)=W(d)` and `V(a) != V(d)`. *(Checked: `E1`.)* The edge `b–c` has
`V(b)=V(c)`, so it is a **null bridge** linking two active regions with different
normalizers. Revision 1 silently assumed the active subgraph was connected.

**The same local data on a ring mints:** close it with a null edge `d–a`
(`V=(1,0,0,1)`, `p=(2,2,1,1)`) and the circulation is exactly `-1/2`.
*(Checked: `E3`.)* **The criterion is a property of the cycle space, not of
connectivity and not of whether `p` varies.**

### 5.2 Theorem EP — exact criterion and finite algorithm

**(a) Per-edge (antisymmetry).** `s` is well defined iff for every edge
`V(x)=V(y)` **or** `p(x)=p(y)`. So **`p` may change freely across `Delta V = 0`
edges**, and only there.

Split `E` into **active** (`Delta V != 0`) and **null**. By (a), `p` is constant
on each connected component of the active subgraph; let `K_1..K_r` carry
`p_1..p_r`.

**(b) Circulation.** For any closed walk `gamma`,
`∮ s = sum_j D_j(gamma)/p_j`, where `D_j` is the signed `V`-drop accumulated along
active edges of `gamma` inside `K_j`; and `sum_j D_j(gamma) = 0` always.

**(c) Criterion.** With `D := span{(D_j(gamma))_j : gamma in a cycle basis} ⊆ 1^perp`,

```
s is exact   <=>   (1/p_1, ..., 1/p_r) ⊥ D.
```

**(d) Corollaries.** Trivial cycle space (a tree) or `D = {0}` ⟹ **every** `p`
satisfying (a) works — the chain. One active component ⟹ always exact.
`D = 1^perp` ⟹ all `p_j` equal — the ring, and the only case where revision 1's
conclusion held.

**(e) Finite necessary-and-sufficient algorithm.**

1. Check (a) on every edge; fail ⟹ not exact.
2. Union-find the active components; read off `p_j`.
3. Set `W := V/p_j + c_j` on component `j` (and `W := c_v` on a vertex touched by
   no active edge).
4. Each null edge `{x,y}` imposes `c_{K(y)} - c_{K(x)} = base(x) - base(y)`.
   BFS the component graph; any inconsistency ⟹ not exact.
5. Return `W`.

*(Verified: the algorithm **accepts** the auditor's chain and reconstructs its `W`
up to an additive constant, **rejects** the ring, and agrees with actual exactness
on **every** admissible `(V,p)` assignment over a declared grid — 276/276 on the
4-ring, 384/384 on the 4-chain, 228/228 on a theta graph. `EP`.)*

---

## 6. Topological exactness

**Theorem G1.** On a connected component, zero circulation on every closed cycle
⟺ `W` exists, unique up to an additive constant. **Theorem G2.** A fundamental
cycle basis of size `m-n+1` suffices. *(3-cell lattice: `n=28`, `m=63`,
`m-n+1=36`, coboundary rank `27`. Checked: `G1`, `G2`, `G4`, `G5`.)*

**Cohomology.** Every 1-cochain on a graph is closed, so the right statement is
`s` exact ⟺ `s` annihilates `Z_1`; `H^1(G;R) ≅ R^{m-n+1}` and the circulation
vector over a basis *is* the class of `s`.

### 6.1 Directed graphs

**General criterion:** all directed paths with identical endpoints carry equal
settlement sums; equivalently, zero circulation on the **underlying undirected**
cycle space.

**Sufficiency — RETAINED.** Strong connectivity ⟹ zero sum on directed cycles
implies exactness (compose each path with a return path; closed walks decompose
into directed cycles). **Necessity — WITHDRAWN.** A directed tree (`a->b`, `a->c`)
is not strongly connected, has no directed cycle, and every cochain on it is
exact. *(Checked: `G7`.)* **Insufficiency in general — RETAINED:** the diamond
`a->b, a->c, b->d, c->d` has no directed cycle (verified by search) yet admits no
`W` when the two routes settle `2` and `3`. *(Checked: `G6`.)*

### 6.2 Extended state×field graph

Let `z=(x,theta)`; field-only edges carry actor settlement **zero**.

**Theorem F1.** Assume (i) field edges settle `0`; (ii) the cochain is
antisymmetric; (iii) circulation vanishes on every closed extended cycle; and
**(iv) traversability** — the field can move at both endpoint states and the
action is reversible, or the antisymmetric extension is used. Then
`s_theta(x->y) = s_{theta'}(x->y)` for all fields, and `s` is exact in `x`.

*Proof.* The plaquette circulation is `s_theta(x->y) - s_{theta'}(x->y)`; setting
it to zero gives explicit-`theta` independence, and Theorem G1 within one field
level gives exactness. ∎

**Theorem F2.** For raw `s_theta = p(theta) Delta W` the plaquette circulation is
exactly `[p(theta)-p(theta')][W(x)-W(y)]`, vanishing iff `p` is constant.

**Interpretation — CORRECTED.** F1 gives **explicit-`theta` independence at fixed
`(x,y)`**. It does **not** say the settlement is blind to physical state:
`W(x)-W(y)` depends on `x` and `y` throughout. Revision 1's reading ("the wallet
cannot see the field") and its conclusion ("field response can only come from
affordability") are both **withdrawn**. If field health is a function of the
physical state `x`, a settlement `W(x)-W(y)` may depend on it without touching F1.

---

## 7. Closed cycles and the external field ledger — WORDING CORRECTED

**Theorem A1 (fixed field).** Under Theorem I with `theta` fixed and `C_a = 0`,
`sum_i Delta c_i = W(x_0)-W(x_T) = 0` around a closed actor-only cycle.
**`Delta c_i = 0` is not required per actor** — capacity may redistribute.

**Theorem A2.** Normalization extends this to a moving field sharing one `W`
(Theorem I.4). Under Theorem DS it holds automatically, since `Delta c` is a
potential difference. **This is R6, satisfied structurally.**

**Theorem A3′ — corrected.** Raw unnormalized V1 settlement has nonzero
circulation **in the actor ledger** when `p` varies: with `W(x)=3`, `W(y)=1`, act
`x->y` at `p=2` and back at `p=1`, and the actor ledger gains `+2` with the state
*and* the field returning. **But the accounting closes:** the external field
contributions are `+1` and `-3`, totalling `-2`, so

```
actor ledger +2 ,  field ledger -2 ,  grand total 0   (exactly)
```

*(Checked: `N1`.)* **This is extraction from the external field ledger into the
actor ledger, not creation ex nihilo.** Revision 1's unqualified "minting" is
withdrawn. The load-bearing content survives: raw static V1 cannot be extended
through a moving field without additional accounting or normalization.

**Scope note.** This does not contradict
`DEMAND_DRIVEN_CLOSED_CYCLE_THEOREM.md`, whose scope declares the potential once
and never moves it. **Recommendation (not performed):** if a dynamic field is
adopted, that theorem should carry an explicit "the field did not move"
hypothesis and provenance should record field-change events. No document is
amended by this report.

---

## 8. THEOREM AC — locality is a genuine extra constraint

Theorem DS delivers *a* persistent scalar. R4 asks for a **factor-local** one.

**Locality, stated with factor support (not coordinate separability).** The
programme permits multi-coordinate factors. A receipt may depend only on factors
whose support meets the action's touched support.

**Theorem N4′(a).** A **factor-additive** `W(x) = sum_F W_F(x_F)` gives
factor-local settlement. *Witness:* `W = x_0 x_1 + (x_2^2 + x_3)` with factors
`{0,1}`, `{2,3}` is factor-additive but **not** coordinate-separable, and the
settlement of a `0->1` transfer is invariant across spectator values.
*(Checked: `L3`.)*

**Theorem N4′(b).** With factor-additive `W` and **nonlinear** `f_theta`,
`E_theta = f_theta(W(x)) - f_theta(W(y))` depends on the *total* `W`, hence on
untouched factors: with `W = sum x_i^2/2`, `f(w)=w^2/2`, a `0->1` transfer gives
`9/2`, `9`, `109/2` as an untouched coordinate takes `0,3,10`, against the affine
value `1` throughout. **Qualification:** a `Delta W = 0` group cannot exhibit it.
*(Checked: `L1`, `L2`.)*

**Theorem AC (factor-locality obstruction) — the key new negative result.**
Acyclicity does **not** imply factor-additive representability.

*Counterexample (double cancellation).* Two declared factors with values
`A ∈ {a,b,c}`, `B ∈ {p,q,r}`. Require

```
W(a,q) > W(b,p),      W(b,r) > W(c,q),      W(c,p) > W(a,r).
```

The six states are **distinct**, so the relation is a set of three disjoint
comparisons and is **trivially acyclic** — Theorem DS is satisfied. But adding the
first two inequalities gives `A_a + B_r > A_c + B_p`, i.e. `W(a,r) > W(c,p)`,
contradicting the third. **No factor-additive `W` exists, for any real values.**
*(Checked: `AC` — algebraically, and by exhaustive search over a `6^6` integer
grid.)*

**Consequence.** Under R4 the criterion is strictly stronger than Theorem DS:

> the contracted strict order must additionally be **additively representable over
> the declared factors**.

This is a finite system of strict linear inequalities in the factor values, so it
is **decidable by linear programming**, and its obstructions are exactly the
cancellation conditions of additive conjoint measurement — of which the
double-cancellation violation above is the smallest.

---

## 9. Revaluation: the same ruler, and the nonuniform no-go

### 9.1 Theorem SR (same-ruler revaluation) — PROVED

If current capacity and current action cost are revalued by the **same** positive
scalar, `B_current = q c` and `E_current = q Delta c` with `q > 0`, then

```
B_current + E_current >= 0     <=>     c + Delta c >= 0.
```

*Proof.* `q(c + Delta c) >= 0 ⟺ c + Delta c >= 0` since `q > 0`. ∎ The same holds
for an action-specific `q(e) > 0` provided the *same* `q(e)` revalues both sides.
*(Checked: `SR`, zero violations over the grid.)*

> **Consequence (recorded).** *Pure multiplicative revaluation changes nominal EBU
> magnitude but cannot change real affordability.* This is why the normalized
> coordinate is the right carrier: it makes the ruler the same by construction,
> and it is exactly R9.

### 9.2 Theorem NU (nonuniform single-wallet no-go) — PROVED

Suppose two actions available at a state rescale differently between fields:

```
E_theta'(e1)/E_theta(e1)  !=  E_theta'(e2)/E_theta(e2).
```

**Then no single current scalar ruler represents both.** Precisely: there are no
persistent settlements `Delta c_1, Delta c_2` and positive scalars `q_theta,
q_theta'` with `E_theta(e_i) = q_theta Delta c_i` and
`E_theta'(e_i) = q_theta' Delta c_i` for `i = 1,2`.

*Proof.* Dividing, `E_theta'(e_i)/E_theta(e_i) = q_theta'/q_theta`, which is
independent of `i` — contradicting nonuniformity. ∎

*(Checked: `NU` — with `E_theta=(2,3)`, `E_theta'=(4,3)` the ratios are `2` and
`1`; an exhaustive search over candidate settlements finds no admissible pair.
Under **uniform** rescaling `E''=(4,6)` the common ruler `q = 2` exists.)*

**Converse.** A single current scalar conversion exists at a state **iff** all
relevant nonzero locally available action values rescale by one common positive
factor — the *local* form of Theorem I. **Proved, not assumed.**

---

## 10. Gaussian specialization

**A. Common `sigma` scaling.** `sigma_i(theta) = c(theta) sigma_i` gives
`p = c^{-2}`, `W = V_{theta_0}`, `k = 0`. *(Checked: `I-A`.)*

**B. Unequal `sigma` changes — CORRECTED.** Use **both** conditions of Theorem Q1
(§10D). For `n >= 3` the quadratic condition alone forces `H_theta = p H_0`.
**For two cells it does not:** the quadratic condition gives only `c_1+c_2=0`, and
the **linear** condition then requires `c_1(u_1+u_2)=0` with
`u_1+u_2 = M - (x*_1+x*_2)`. Hence

> **two-cell criterion: either `H_theta` is already proportional to `H_0`, or the
> reference lies on the conservation slice, `x*_1 + x*_2 = M`.**

*Counterexample when it does not:* `x_1+x_2=2`, `x*=(0,0)` (off slice),
`V_0=(x_1^2+x_2^2)/2`, `V_1=x_1^2/2 + x_2^2/8` give `V_0=(2,1,2)` and
`V_1=(1/2,5/8,2)` on `(0,2),(1,1),(2,0)`: `V_0` **ties** the endpoints and `V_1`
**separates** them, so no `(p,k)` exists. With the reference on the slice,
`p = 5/8` exactly. *(Checked: `T1`–`T5`, five declared `(reference, M)` pairs.)*

**C. Moving `x*`.** Generically destroys Theorem I (a quadratic is constant only
if all coefficients vanish). A common `W` survives **only** on reachable sets
lying strictly on one side of **both** references (then both potentials are
strictly monotone, hence ordinally equivalent, with varying chord slopes and no
global `p`); a set **straddling** a reference has mismatched tie classes, so
common `W` is impossible — proved, not generic.

**D. Conservation-slice exceptions.** *(Theorem Q1.)* `V_theta - pV_0` is constant
on `x_c + T` iff `t^T A t = 0` and `t^T A u = 0` for all `t ∈ T`, with
`A = H_theta - pH_0`. **Theorem X1:** a reference shift along
`span(sigma_1^2,...,sigma_n^2)` changes `V` by one constant on the conservation
slice, so `p = 1` and **no EBU value changes at all**. *(Checked: `X1`–`X3`.)*

**E. Sparse action-graph exceptions.** Theorem DS applies: a world whose action
graph never compares two states cannot be constrained on that pair. §5.1's chain
is a Gaussian-independent instance; the general statement is Theorem DS (ii).

**F. Locally exact one-scalar wallet without global factorization.** By §9.2, a
single current ruler exists **at a state** iff the locally available nonzero
action values rescale by one common factor there. This is strictly weaker than
global factorization and can hold at some states and fail at others.

---

## 11. Capacity V2 — factual correction

Revision 1 said V2 "puts field response in the affordability predicate". **That is
wrong about the programme's own code.** From `capacity_v2/ledger.py`:

- **Affordability is unchanged from V1** — `project` refuses only on a negative
  projected balance. Its docstring: *"The ceiling is deliberately NOT part of
  affordability. It applies after settlement, so it can never cause a refusal and
  can never make an otherwise legal action illegal."*
- The ceiling `Phi_i = V_i(x_i)` is applied in `reconcile` **after** settlement,
  moving the excess into a **monotone retirement ledger**.

*Verified against the implementation:* a ledger holding `50` against a ceiling of
`0` still reports a debit of `1` as **affordable**; after `reconcile` the balance
is `0` and `retired` is `50`; only then does the unchanged affordability rule
refuse. *(Checked: `C1`–`C4`.)*

So field-state dependence in V2 enters through **post-settlement retirement**,
not affordability. Revision 1's further inference of a social/incentive conflict
is **withdrawn**: `B_i = 0` at the local reference does not by itself establish
anything about useful future action freedom, and no model mapping balances to
freedom is declared. **Classified OPEN.**

---

## 12. Simultaneous actions and receipts

**Hypothesis (PATH), now explicit.** Common-path receipts are integrals along
`x(s) = z + s delta_G`. A finite **vertex-level** certificate says nothing about
intermediate points. The representation used must hold at **every point of the
common path**. For the static case with `W := V_{theta_0}` this is trivial — the
identity holds identically as functions — but it is now stated.
*(Checked: `R0`, at nine sampled path points.)*

**Aggregate conversion — Case I.** Under (PATH) with `V_theta = p W + k`,
`grad V_theta = p grad W`, so `C_a = R_a/p` for **every** action and
`sum_a C_a = W(z) - W(z+delta_G)`. *(Checked: `R1` — group value and every
individual receipt rescale by exactly `p = 1/4`; residuals zero.)*

**Per-owner conversion — Case II.** `C_a = -∫ grad W(x+lambda delta_G)^T delta_a`
closes exactly on `Delta c_G`. *(Checked: `R2`.)*

**Theorem R3′ (per-group criterion).** A common scalar `p` with `R_a = p C_a` for
every action of a **given** group exists **iff**

```
∫_0^1 ( f'_theta(W(lambda)) - p ) omega_a(lambda) d lambda = 0   for every action a,
```

where `omega_a(lambda) = -grad W(x+lambda delta_G)^T delta_a`.

- **Affine `f` is sufficient for every group.**
- **Special-group cancellation is real.** Revision 1 claimed distinct profiles
  force failure unless `f` is affine; **false**. With `W = sum x_i^2/2`,
  `f(w)=w^2/2`, baseline `(3,0,2,1)`, group `{0->1 by 1, 2->3 by 2}`:
  `Delta W = 0`, profiles `3-2s` and `2-8s` (**not** proportional), yet
  `C_a = (2,-2)`, `R_a = (37/3,-37/3)` and both ratios equal **`37/6`**.
  *(Checked: `R4`.)* For `f(w)=w^2/2` with quadratic `W`, a common factor exists
  precisely when the profiles are proportional **or** `Delta W = 0`, with value
  `W(x) + (grad W . delta_G)/6`.
- **Failure is also real:** with `sigma=(1,1,2,1)`, `V=W^2/2`, baseline
  `(9,23/2,10,19/2)`, group `{0->1 by 1, 2->3 by 1/2}`, the ratios `575/168` and
  `1333/576` differ. *(Checked: `R3`.)*
- **Universal conversion theorem — OPEN.** Whether a common factor for *every*
  group forces `f` affine needs explicit richness assumptions on the available
  `omega_a` family. **Not inferred from one counterexample.**

---

## 13. Three objects, and the freedom question

### 13.1 Keep A, B, C separate

| | object |
|---|---|
| **A** | the carried historical settlement coordinate `c_i` |
| **B** | a nominal/current EBU representation of that coordinate, *if one exists* |
| **C** | the actual current action freedom / admissible action set |

**A exists** exactly under Theorem DS (+ Theorem AC for R4).
**B exists at a state** exactly under the local uniformity condition of §9.2 —
and **fails** under nonuniform rescaling (Theorem NU).
**C is determined by A**, the declared settlement rule and the declared
affordability predicate: `C = { e : c + Delta c(e) >= 0 }`.

**Can B alone determine C?** **No, and it is not needed.** `C` follows from `A`
directly. When `B` exists, Theorem SR guarantees it yields the *same* `C`, because
a common positive factor cannot change the sign of `c + Delta c`. When `B` does
not exist (nonuniform change), `C` is still well defined from `A`. **So the
nominal representation is a convenience, never the carrier.**

### 13.2 Theorem FB — `V` alone contains no finite freedom budget

**Question.** Given only current `V` (or local factor potentials), gradients and
marginals, conserved quantities, the current state and the allowed local actions —
is there a **unique** finite scalar "remaining disturbance freedom" `H(x,theta)`?

**Invariances any such `H` must satisfy.** The declared structure is invariant
under `V -> aV + b` with `a > 0` (`b` is pure gauge; `a` is the unit, fixed by the
capacity-unit declaration). So `H` must be **shift invariant** and **scale
covariant**: it can depend on `V` only through differences.

**Theorem FB.** These data do **not** determine `H`. Exhibit two candidates, both
derivable from the listed data and both satisfying both invariances:

```
H_1(x) = max_{z in C} V(z) - V(x)          (global reachable maximum)
H_2(x) = max_{y ~ x}  V(y) - V(x)          (one-step local maximum)
```

They differ at **22 of 28** states of the 3-cell world, and induce **different
admissible action sets** at **3** states — e.g. at `x = (0,3,3)`, `|A_{H_1}| = 4`
against `|A_{H_2}| = 2`. *(Checked: `FB`, including the shift and scale checks.)*
Hence `H` is **not unique**, and selecting one is a **physical declaration, not a
derivation**. ∎

**What `V` does and does not supply.**

> A potential supplies an **ordering** of states and **exact burden differences**
> between them. A finite *freedom budget* additionally requires a **distinguished
> level** — a zero of `H` — and no such level is singled out by `V`, its
> gradients, the conservation constraints or the local action menu.

Note also that `H_1` is **global** (it reads the whole reachable component) and so
violates R4 even where it is well defined.

### 13.3 Minimal extra physical structure

If a freedom budget is wanted, the minimum additional object is a **declared,
current-state, localizable viability level** `Lambda` against which remaining
freedom is measured, giving `H = Lambda - V` up to units. Candidates, **evaluated,
not adopted**:

| candidate | assessment |
|---|---|
| hard viability / safety boundary | works; must be declared per factor to satisfy R4 |
| conserved reserve / headroom | works if declared locally; closest to the existing conservation structure |
| barrier function | equivalent to declaring `Lambda` implicitly; adds no independent content |
| physically measured critical threshold | works; is an empirical declaration, not a derivation |
| recoverability / viability set | works but is generally **global** (needs reachability), conflicting with R4 unless declared locally |

**No such object is invented here.** The requirement is only characterized:
current-state based, localizable, and declared.

---

## 14. FINAL DECISIVE VERDICT

> ## DYNAMIC SCALAR CAPACITY SOLVED UNDER AXIOMS R1–R10

**The necessary-and-sufficient rule.** For a declared field family on a declared
allowed-transition graph `G`, a persistent scalar capacity satisfying R1–R10
exists **if and only if**:

> **(L1) Common orientation.** On every action edge, all fields whose EBU is
> nonzero there agree on its sign.
>
> **(L2) Acyclicity after equality contraction.** Contract every edge that *every*
> field values at zero; orient the rest by their common EBU sign; the resulting
> digraph must be acyclic, with no oriented edge inside a contracted class.
>
> **(L3) Factor-additive representability (this is R4).** The resulting strict
> order must be representable as `W(x) = sum_F W_F(x_F)` over the declared
> factors — a finite system of strict linear inequalities, decidable by linear
> programming, whose obstructions are exactly the cancellation conditions.

Settlement is then `Delta c = W(x) - W(y)`: exact, finite, history-free,
field-independent, telescoping to zero on closed cycles, and reducing to V1
exactly when the field is static and `W := V_{theta_0}`.

**L1 ∧ L2 is complete for R1–R3 and R5-limit, R6–R10** (Theorem DS, verified
against an independent oracle on 13,851 exhaustive cases). **L3 is strictly
stronger** and is not implied: Theorem AC exhibits an acyclic order with no
factor-additive representation.

### The exact boundary — what is NOT obtainable

Two strictly stronger asks are **impossible in general**, with exact
counterexamples:

1. **A magnitude-faithful wallet (R5-uniform).** If settlement must equal each
   field's own V1 settlement up to one positive constant per field, the family is
   forced into the scalar-revaluation class `V_theta = p(theta) W + k_C(theta)`.
   Theorem DS uses only the **signs** of the changing field, never its magnitudes.
2. **A single current nominal ruler under nonuniform change.** Theorem NU: if two
   locally available actions rescale by different factors, no pair of positive
   rulers represents both. A single current scalar conversion exists at a state
   **iff** all locally available nonzero action values rescale by one common
   positive factor.

### The minimal structure that must be added

For a **freedom budget** — as opposed to a settlement coordinate — `V` is
provably insufficient (Theorem FB). The minimum addition is a **declared,
current-state, localizable viability level / reserve / boundary**. Nothing in the
present declarations supplies one, and none is invented here.

---

## 15. The four mandatory answers

**1. Is dynamic SETTLEMENT solved?**
> **YES.** Necessary and sufficient: L1 ∧ L2 (Theorem DS), plus L3 for R4-locality
> (Theorem AC, decidable by LP). Settlement is `Delta c = W(x) - W(y)` — exact,
> finite, history-free, no closed-cycle minting, and V1 in the static limit.

**2. Is dynamic REVALUATION solved?**
> **Solved as a characterization, and the answer is negative in general.** A
> single current scalar ruler exists at a state **iff** all locally available
> nonzero action values rescale by one common positive factor (§9.2). Under
> nonuniform rescaling it **does not exist** (Theorem NU). Where it does exist,
> Theorem SR guarantees it changes no affordability decision — so revaluation is
> nominal, never real.

**3. Is dynamic ACTION FREEDOM solved?**
> **Partly.** The *admissible action set* is fully determined by the carried
> coordinate plus the declared affordability predicate, so it inherits answer 1.
> A *field-health-dependent freedom budget* is **NOT** solved and is **not
> derivable from `V`** (Theorem FB).

**4. If not, exactly what physical quantity is missing?**
> **A declared, current-state, localizable viability level** `Lambda` — a
> boundary, reserve, headroom or measured critical threshold — against which
> remaining freedom is measured, giving `H = Lambda - V` up to units. `V` supplies
> only an **ordering** and **exact burden differences**; a finite budget
> additionally needs a **distinguished zero**, and `V`, its gradients, the
> conservation constraints and the local action menu do not single one out.

---

## 16. Theorem status table

**P** = PROVED · **PH** = PROVED UNDER STATED EXTRA HYPOTHESES ·
**DS** = DISPROVED AS STATED · **CO** = COUNTEREXAMPLE ONLY / UNIVERSAL CLAIM OPEN ·
**O** = OPEN · **DO** = DESIGN OBJECTIVE

| # | Statement | Status |
|---|---|---|
| **DS** | **Persistent `W` exists iff common orientation + acyclicity after contraction** | **P** (13,851 exhaustive cases vs independent oracle) |
| DS-F | Mixed zero/nonzero edges: weak reading admits them; strong reading forces a field-independent zero-set | **P** |
| **AC** | **Acyclicity does NOT imply factor-additive representability** | **P** (double cancellation) |
| **EP** | **Endpoint criterion `(1/p_j) ⊥ D`, with a finite n&s algorithm** | **P** (888 exhaustive assignments) |
| **NU** | **Nonuniform rescaling ⟹ no single current scalar ruler** | **P** |
| NU-conv | A current ruler exists iff locally available values share one factor | **P** |
| **SR** | **Same-ruler revaluation never changes real affordability** | **P** |
| **FB** | **`V` alone does not determine a freedom budget** | **P** (two derivable candidates, different admissible sets) |
| D1, D2 | Exact decomposition; order dependence | **P** |
| I, I.1–I.5 | Scalar revaluation; tests; normalized settlement; field-path independence | **P** |
| I-gauge | Positive-affine uniqueness — **Theorem I's class only** | **P** |
| II | `E = p_eff Delta W`, `p_eff > 0` as a **chord-slope** statement | **P** |
| II.2 | Finite **global representability** ⟺ identical weak order | **P** (scope (GR) only) |
| II.2-misuse | II.2 characterizes edge-local normalizability | **DS** |
| II.4 | Continuum quadratic rigidity at slice dim `>= 2` | **P** |
| II.5 | The same rigidity on a finite lattice | **DS** (45-state witness) |
| R-cert | `R(V_0,C)=2` certifies rigidity per world | **P** |
| **S2** | **"Connectivity forces `p` constant where `V` varies"** | **DS** |
| S1, S3, S4 | Antisymmetry criterion; symmetric weights mint on triangles; `lambda` determined by `W` | **P** |
| G1, G2 | Zero circulation ⟺ exact; `m-n+1` basis suffices | **P** |
| G3-suff / G3-insuff | Strong connectivity sufficient / directed checking insufficient in general | **P** |
| **G3-nec** | **"…iff strongly connected"** | **DS** (directed tree) |
| N1, N2′, N2″ | Vacuity at fixed field; edge-local obstruction; (EL) strictly weaker than (GR) | **P** |
| **N2** | **Edge-order compatibility "is exactly" II.2's criterion** | **DS** |
| **N3** | **`W` unique up to positive affine in the monotone class** | **DS** |
| N3′ | Monotone class has full increasing-reparametrization gauge freedom | **P** |
| **N4** | **Locality forces coordinate separability** | **DS** |
| N4′(a),(b) | Factor-additive `W` is local; nonlinear `f` with `Delta W != 0` is not | **P** |
| N4′(c) | Locality forces `W` factor-additive | **settled negatively by AC** |
| **P1** | **Strictly increasing ⟹ `f' > 0`** | **DS** (`w^3`) |
| P1′ | `p_eff > 0` survives; `p_local` needs `f' != 0` explicitly | **P** |
| X1, X2 | Invisible reference motion; generic moving reference destroys revaluation | **P** |
| Q1 | Compression criterion — **both** conditions | **P** |
| **Q2-2cell** | **"Any two-cell per-coordinate `sigma` change is a revaluation"** | **DS** |
| Q2′-2cell | Holds iff `H` proportional, or reference on the conservation slice | **P** |
| Q2-n≥3 | `n >= 3` forces `H_theta = p H_0` | **P** |
| Q3 | Monotone transforms buy nothing for quadratics (continuum, dim `>= 2`) | **P** |
| R0 | (PATH) must hold along the common path, not just at vertices | **P** |
| R1, R2 | Case I and Case II receipt closure | **PH** (under PATH) |
| **R3** | **"Distinct profiles ⟹ failure unless `f` affine"** | **DS** (factor `37/6`) |
| R3′ | Per-group common-factor criterion | **P** |
| R3″ | A common factor can fail to exist | **CO** |
| R3‴ | "Common factor for **all** groups ⟹ `f` affine" | **O** |
| A1, A2 | Fixed-field closure; normalization extends it | **P** |
| **A3** | **"Raw V1 mints"** (unqualified) | **DS as wording** |
| A3′ | Nonzero actor-ledger circulation; external ledger pays; grand total zero | **P** |
| F1 | Extended-graph conditions ⟹ explicit-`theta` independence + exactness | **PH** (traversability) |
| **F1-interp** | **"The wallet cannot see the field at all"** | **DS** |
| F2 | Plaquette circulation `= (p-p')(W(x)-W(y))` | **P** |
| **B** | **Five-requirement impossibility / exclusivity of class A** | **WITHDRAWN**, superseded by DS |
| V1, V1.1 | Static V1 is the exact limit; the unit changes no decision | **P** |
| M1–M3 | Möbius rescaling; local screen; nonquadratic certificate | **P** |
| **V2-desc** | **"V2 places field response in affordability"** | **DS** — wrong about the code |
| V2′ | V2 affordability = V1; ceiling is post-settlement retirement | **P** (verified against code) |
| **V2-conflict** | **"V2 contradicts the preserved freedom sentence"** | **WITHDRAWN** → **O** |
| — | Relation between restoration, retained capacity and useful future freedom | **O** |
| — | Whether any physically motivated dynamic family satisfies L1–L3 | **O** |
| — | Capacity gives an autonomous actor a legitimate region of decentralized freedom | **DO** |

---

## 17. WHAT IS NOW SAFE TO USE — authority map

### BOX A — STATIC STUDY AUTHORITY (fixed-field Stage A/B)

Exact finite frozen-field EBU; common-path receipt closure; the static V1
settlement identity `Delta c_i = receipt_i` at `p = 1` including per-owner
receipts; unit invariance of affordability; fixed-field aggregate closed-cycle
telescoping; graph cycle-space exactness and the `m-n+1` basis test; the
actor/field decomposition under a declared event order.

**Nothing in BOX A depends on any statement corrected or withdrawn in revisions 2
or 3.**

### BOX B — DYNAMIC FIELD RESULTS PROVED

Theorem DS (with its exhaustive verification); Theorem AC; Theorem EP and its
finite algorithm; Theorem SR; Theorem NU and its converse; Theorem FB; Theorem I
and Corollaries I.1–I.5; Theorem II with `p_eff` as a chord slope; Theorem II.2
for (GR) only; Theorem II.4 and the `R(V_0,C)` certificate; G1/G2, G3-sufficiency
and G3-insufficiency; Theorem Q1 with **both** conditions and the corrected
two-cell criterion; Theorem X1; R1/R2 under (PATH); R3′; A3′; F1 as
explicit-`theta` independence; V2′.

### BOX C — DYNAMIC FIELD QUESTIONS OPEN

1. Which *physically motivated* dynamic field families satisfy L1–L3? A modelling
   question; no family is invented here.
2. Field-health-dependent decentralized freedom, and **where in the mechanism it
   may legitimately enter** — F1 does **not** settle this.
3. The exact role of affordability versus retirement versus another
   state-dependent gate, given that V2's ceiling is retirement (§11).
4. R3‴: does a common receipt factor for *every* group force `f` affine?
5. The relation between restoration, retained capacity and useful future action
   freedom.
6. Across disconnected reachable components, is a **common** `p` declared?

> **BOX A safe does NOT mean BOX C solved.** Dynamic *settlement* is solved
> (BOX B); a dynamic *freedom budget* is not, and requires the declared physical
> level of §13.3.

---

## 18. Stage A/B gate

**Q-A. Does any finding invalidate the fixed-field static identity — `theta`
constant, `p = 1`, `Delta c_i = receipt_i`?**

> **NO COUNTEREXAMPLE FOUND / STATIC IDENTITY RETAINED.** Every correction and
> every new theorem concerns a state-dependent normalizer, a moving or nonuniform
> field, a nonaffine transform, an off-slice two-cell geometry, factor-locality,
> or a freedom budget. At `theta` constant with `p = 1` and `W := V_{theta_0}`,
> (PATH) holds identically and the identity is exact including per-owner receipts.
> *(Checked: `R0`, `V1-1`, `V1-2`, `V1-3`.)*

**Q-B. Is general Dynamic EBU capacity theory solved?**

> **Dynamic SETTLEMENT is solved** (Theorem DS + AC, §14). **Dynamic REVALUATION
> is characterized and generally negative** (Theorem NU). **Dynamic FREEDOM is
> not solved and requires one declared physical datum** (Theorem FB, §13.3).

**This task does not authorize Stage A/B execution.**
