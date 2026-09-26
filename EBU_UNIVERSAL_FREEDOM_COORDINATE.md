# EBU universal freedom coordinate — existence and cross-field calibration

**Subordinate to `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.** No programme
authority claimed. Continues `DYNAMIC_EBU_CAPACITY_SUFFICIENT_STATE_STUDY.md`
and `DYNAMIC_EBU_FREEDOM_STATE_THEORY.md`.

**Scope discipline.** No mechanism modified. Stage A/B not run. P-demand not
redesigned. Ownership not solved. No history vector, no source portfolio, no
field-history ledger. **No proof below uses `c_i >= 0`, `c_i + Delta F >= 0`, or
any pre-action affordability gate** — Q7 is answered by inspection of the
argument, not by assertion.

**Checks.** `dynamic_ebu_theory_checks.py` — **320 deterministic checks, 0
failures**, exact `Fraction`, tolerance literally zero, no randomized search.
The new section is tagged `FC-*`.

> **MODEL COORDINATE.** All figures computed against the current
> `demand_driven_ebu` (existential physical-service predicate): 91 states, 408
> menu edges. Where prose quotes a count, the `FC-*` check is the authority.

---

## 0. The result

**Existence is not the problem. Calibration is — and the problem is exactly one
positive function.**

Under the frozen architecture (§0 of the task: `theta` lives *inside* the state
`X`), the general solution of the actor-direction requirement is

```
        F(x, theta)  =  phi_theta( V_theta(x) ) ,      phi_theta strictly decreasing
```

and after the one available reduction (additivity over physically independent
subsystems, a Pexider equation — check `FC-09`)

```
        F(x, theta)  =  - alpha(theta) · V_theta(x)  +  beta(theta) ,   alpha > 0
        ==>   Delta F_actor  =  alpha(theta) · E_theta(G) .
```

`beta` never enters an actor credit. **`alpha(theta)` is the entire cross-field
calibration — the exchange rate between current EBU and universal freedom
units — and nothing in the declared EBU ontology constrains it.**

**What the architecture buys, for free.** Because `theta` is inside `X`:

- a credited increment `F(x1,theta) - F(x0,theta)` is a difference of a state
  function at a *fixed* field, so it is **never repriced** — the §9 property
  holds by construction, and the field at which it was earned need not be stored;
- the **total** around any mixed full-state cycle is exactly `0` — automatic.
  *(Checked: `FC-03`.)*

> **So the mixed-cycle test has no discriminating power on the total. All of its
> content sits in the actor-attributed part — and there it is decisive.**

**The decisive object.** Act `x* -> (5,4,3)` under `sigma = (1,1,1)`; let the
field move to `sigma = (1,2,3)`; reverse the action; let the field return. The
world is back to its exact starting state. With `alpha = 1` the actor-attributed
credit around the cycle is

```
        Lambda  =  -1  +  5/9  =  -4/9        (reversed: +4/9, repeatable)
```

*(Checked: `FC-04`.)* And **no choice of `alpha` repairs it**: `alpha = 1` leaves
**8040 of the 8281** state pairs with nonzero actor circulation, and `alpha`
tuned to close the witness pair (`9/5`) leaves **8066** — strictly worse.
*(Checked: `FC-05`.)* The reason is exact: the ratio each action *demands* is
`dV_ref/dV_cur`, and over the menu graph that takes **174 distinct values, 10 of
them negative**. Not one constant, and not even one sign. *(Checked: `FC-06`.)*

**Where calibration IS forced.** Exactly the field pairs with
`V_theta' = q V_theta + const` on each reachable component — condition **D**.

| witness | demanded ratio | closure |
|---|---|---|
| uniform `sigma -> 2 sigma` | the single value **4** | `alpha(2 sigma) = 4 alpha(sigma)` closes **all 8281** cycles |
| `x*` moved to `(5,5,5)` (along `span(sigma^2)`) | `V` shifts by the constant `3/2` | `alpha` unchanged closes **all 8281** |

*(Checked: `FC-07`, `FC-08`.)*

> **Condition D is necessary and sufficient for all three required theorems at
> once** — calibration (B), path-independence of the actor/field split (C), and
> vanishing actor circulation. This is the third independent route by which the
> programme arrives at D.

**And the missing datum is nameable.** `V_theta` is **dimensionless** — `sigma`
carries the material units, so `alpha` is a pure number and dimensional analysis
cannot touch it. `V_theta` is an *empirical* burden scale in exactly the sense
that a mercury column is an empirical temperature scale: it orders states
faithfully and fixes no unit. What promotes empirical temperature to absolute
temperature is the zeroth law plus Carnot's universality theorem — and **EBU
declares no cross-field coupling, no reversible cross-field process, and no
reference measure**, so no counterpart exists.

> **MISSING AXIOM.** An operational definition of the burden unit across fields.
> Equivalently, any *one* of: (a) a declared reference measure `p_theta` on the
> state space, giving `alpha = -d log p_theta / dV_theta`; (b) a declared
> standard action per field with declared equal freedom content; (c) a declared
> cross-field coupling whose joint equilibrium equates marginal freedoms; (d) a
> constitutive declaration of whether `sigma` is a **physical property of the
> world** or the **unit in which burden is measured**. (d) is the most primitive
> form, and §11A shows it is exactly what the simplest witness turns on.

---

## 1. Retained EBU

`E_theta(G) = V_theta(x_before) - V_theta(x_after)` is unchanged and not
redefined. The sign convention is retained: burden reduction gives positive
`Delta F`, burden increase negative. Under the reduction of §7 this is
`Delta F_actor = alpha(theta) E_theta(G)`, so the sign convention holds for every
admissible calibration, since `alpha > 0`.

---

## 2. Golden equilibrium requirement — satisfied, and non-binding

Required: `argmax_x F(x,theta) = argmin_x V_theta(x)` for each allowed field, and
`argmax F_theta = {x*(theta)}` for reachable Gaussian `x*`.

> **Proposition E.** For `F = phi_theta(V_theta)` with `phi_theta` strictly
> decreasing, `argmax_x F(·,theta) = argmin_x V_theta` — **identically, for every
> such `phi_theta`.**

Since `V_theta >= 0` with equality exactly at `x*(theta)`, the requirement holds
whenever `x*(theta)` is reachable, for every positive `sigma(theta)` and every
reference position. (Established in the companion study; unchanged here.)

> **This is the first and largest piece of the underdetermination.** The golden
> requirement pins the *location* of the maximum and says **nothing whatsoever**
> about the metric — precisely as §2 warns. Every `phi_theta` in an
> infinite-dimensional family satisfies it.

---

## 3. What "universal" must mean

A coordinate is **universal** iff it is determined up to a single **global**
affine gauge

```
        F -> a F + b ,        a > 0 ,   a and b independent of theta.
```

A `theta`-dependent recalibration `F_theta -> h_theta(F_theta)` is **not**
admitted as equivalent. The distinction is exactly the content of this document:
§7 shows the declared requirements admit the full `theta`-dependent family, and
§8 shows what would be needed to collapse it.

**Why the distinction is not pedantic.** Under a global gauge, a credit of `+3`
earned at `theta_0` and a credit of `+3` earned at `theta_1` denote the same
amount of freedom. Under a `theta`-dependent recalibration they do not, and
`c_i` — a single running scalar summing increments earned at many fields —
becomes a sum of incommensurable terms. **`c_i` is well posed exactly when the
gauge is global.**

---

## 4. Actor / field decomposition

For separated events the decomposition is as declared:

```
Delta F_actor = F(x1,theta0) - F(x0,theta0) ,     Delta F_field = F(x1,theta1) - F(x1,theta0)
```

and `Delta F_total = Delta F_actor + Delta F_field` telescopes because `F` is a
state function of the full `X`. The field term is never actor reward or blame.

**Simultaneous change — the general decomposition.** For a path
`gamma(t) = (x(t), theta(t))` in the full state space,

```
dF  =  (partial_x F) · dx   +   (partial_theta F) · dtheta ,
Delta F_actor := ∫_gamma (partial_x F) · dx ,   Delta F_field := ∫_gamma (partial_theta F) · dtheta .
```

The **sum** is always `F(end) - F(start)`, path independent. The **two parts
separately are not**, unless:

> **Theorem C-split.** The actor/field decomposition is path independent — hence
> well defined for simultaneous change — **iff** the actor one-form
> `omega_actor := (partial_x F) · dx` is closed on the full state space, i.e.
>
> ```
> partial^2 F / partial theta partial x  =  0    <=>    F(x,theta) = W(x) + g(theta) .
> ```

*Proof.* `omega_actor` is closed iff `partial_theta(partial_x F) = 0`; integrate
in `x` to get `F = W(x) + g(theta)`. Conversely that form gives
`omega_actor = dW`, exact. ∎

For `F = -alpha(theta) V_theta + beta(theta)` separability says
`alpha(theta) V_theta(x) - W(x)` is independent of `x` — i.e.
`V_theta = (1/alpha(theta))(W + const)`, which is **condition D**. *(Checked:
`FC-07`, where `4 V_(2 sigma) = V_(1,1,1)` identically.)*

> **So assigning the environmental component to the actor is avoidable exactly on
> condition D. Outside it, "what the actor did" during a field-moving execution
> is not a well-defined number — not because of bad bookkeeping, but because the
> integral depends on the interleaving.**

---

## 5. Feedback error

`epsilon := Delta F_actor_real - Delta F_hat_actor`, with environmental movement
excluded by construction.

> **Corollary (assumptions required).** `epsilon` is well defined iff
> `Delta F_actor_real` is, i.e. iff **either** the field is constant throughout
> execution (the separated-event case), **or** condition D holds (Theorem
> C-split). Under neither, `epsilon` inherits the path dependence of the split
> and is not a property of the executor at all.

This is a genuine restriction on any feedback/control layer built on `F`: it may
compare prediction to realization only across a field-constant execution window,
unless the field family is D.

---

## 6. Differential formulation

Let `A_X` be the allowed actor-displacement space at `X`. The requirement

```
dF |_A  =  - lambda(X) dV_theta |_A ,     lambda(X) > 0
```

is the statement that `F` strictly decreases exactly where current burden
increases, along allowed actions.

**Is scalar proportionality too restrictive?** No — at fixed `theta` it is
forced by the sign convention of §1 together with the demand that `F` change
*only* through the physics `V_theta` sees. The general relation
`dF|_A = -lambda dV_theta|_A + mu` with `mu` an extra one-form would credit
actors for a direction the current field prices at zero, contradicting §1's
convention at the zero locus. So proportionality is the content, not a
simplification.

**The prior theorem is not rediscovered.** That a *field-independent* `W(x)` with
`lambda_theta dV_theta|_A = dW|_A` requires the projected covectors to share one
positive ray, and fails for generic heterogeneous Gaussian change, is retained
from the companion work and used, not re-proved. The present setting is strictly
more general: `F` may depend on `theta`, which is precisely why existence now
succeeds and only calibration fails.

---

## 7. Characterization of all possible `F` — the underdetermination ladder

### 7A. On a fixed `theta` slice, must `F` be a monotone function of `V_theta`?

> **Yes, on each actor-connected component**, given §6. Along any actor path
> `dF` and `-dV_theta` have the same sign, so `F` is constant on the
> intersection of a `V_theta` level set with a component and strictly decreasing
> across levels. Hence `F = phi_theta(V_theta)` component-wise, `phi_theta`
> strictly decreasing.

> **No, if only §2 is imposed.** The golden equilibrium requirement constrains
> only the argmax and leaves `F` free to be non-monotone away from it. **§6 is
> doing the work here, and §2 is not.**

### 7B. Disconnected level sets — the extra finite compatibility

Level sets are **massively** disconnected on the actual graph: the 15 burden
levels split into **74** actor-connected components. *(Checked: `FC-01`.)*

> **Compatibility condition (finite).** For `F` to be a function of `V_theta`
> globally — not merely component-wise — it must take equal values on states of
> equal `V_theta` lying in different components:
>
> ```
> V_theta(u) = V_theta(v)   ==>   F(u) = F(v) ,     for all u, v on the slice.
> ```

This is a finite condition (74 components, 15 levels), it does **not** follow
from the differential requirement, and it is the same *finite* level-set
compatibility the programme already adopted in place of an infinitesimal
version. Without it, `F` acquires an additional free constant per component per
field — a further enlargement of the gauge, and one that would let two states of
identical current burden carry different freedom.

### 7C. How much `theta`-dependent gauge freedom remains — the ladder

| axioms granted | remaining freedom per field |
|---|---|
| §1, §2, §4, §6 only | an arbitrary strictly decreasing `phi_theta` — **infinite dimensional** |
| + finite level-set compatibility (7B) | still infinite dimensional, now globally defined |
| + **additivity over physically independent subsystems** | `phi_theta` affine (Pexider): **two numbers** `alpha(theta) > 0`, `beta(theta)` *(check `FC-09`)* |
| + `beta` never enters an actor credit | **one number** `alpha(theta) > 0` |
| + **ordinal invariance** (7D) | `alpha` fixed on condition-D orbits **only** *(checks `FC-07`, `FC-08`)* |
| + a declared measure / standard process / coupling | **fully fixed** — **NOT AVAILABLE** |

> **Honest caveat on the third rung.** Additivity requires *physically
> independent* subsystems. The companion study proved `F` is **not** additive
> across a shared conservation law (joint `W_max = 48` against a product-domain
> `16`), and Study-1 is a single conservation slice. **So the conservation-bound
> world cannot itself instantiate the axiom that buys the affine reduction.**
> The reduction is legitimate as a declaration about independent worlds; it is
> not derivable inside Study-1.

### 7D. Can two physically equivalent field descriptions generate different actor credits?

> **Yes — and this is the sharpest evidence that no calibration is currently
> justified.**

`sigma = (1,1,1)` and `sigma = (2,2,2)` induce the **identical ordering of all 91
states** (verified over all `91 x 91` comparisons) and the identical equilibrium.
Yet with `alpha = 1` the same physical action `x* -> (5,4,3)` is credited `-1`
under the first and `-1/4` under the second. *(Checked: `FC-10`.)*

Rival calibrations disagree just as sharply *within* one field pair: at
`sigma = (1,2,3)` that action is credited `-5/9` under `alpha = 1` and `-5/314`
under `alpha = 1/W_max`. Both satisfy every declared requirement; they differ by
a factor of `314/9`. *(Checked: `FC-10`.)*

**Ordinal invariance, and exactly how far it goes.** Adopt the axiom: *if two
field descriptions induce the same ordering on the state space, they must credit
every action identically.* If `V_theta' = psi(V_theta)` with `psi` increasing,
credit invariance for **all** actions forces `psi` affine, `V_theta' = q V_theta
+ const`, and then `alpha(theta') = alpha(theta)/q` — determined. But for a
heterogeneous change no such `psi` exists at all: **`V_(1,2,3)` is not a function
of `V_(1,1,1)`**, taking several values on 14 of the 15 reference levels (e.g.
level `48` maps to `{122/9, 152/9, 314/9}`). *(Checked: `FC-02`.)*

> **So ordinal invariance is a real calibration principle that applies to exactly
> the condition-D orbits and is vacuous elsewhere.** It cannot be stretched.

---

## 8. Cross-field calibration — the main theorem, and the import audit

### 8.1 The mixed cycle is the only probe, and what it measures

Total closure is automatic (`FC-03`), so the probe is the **actor circulation**

```
Lambda(x0, x1; theta0, theta1)
   =  -alpha(theta0) [V_theta0(x1) - V_theta0(x0)]
      + alpha(theta1) [V_theta1(x1) - V_theta1(x0)] .
```

> **Theorem B (calibration).** `Lambda = 0` for all `x0, x1` **iff**
> `alpha(theta1) V_theta1 = alpha(theta0) V_theta0 + const` on the reachable
> component — i.e. **iff condition D holds**, and then
> `alpha(theta1) = alpha(theta0)/q` is **forced**. If D fails, the ratio
> `dV_theta0/dV_theta1` demanded by individual actions is non-constant, so **no**
> `alpha` makes `Lambda` vanish.

*Proof.* `Lambda = 0` for all pairs says the two increment functions are
proportional with factor `alpha(theta0)/alpha(theta1)` on every realized pair,
which is exactly `V_theta1 = (alpha0/alpha1) V_theta0 + const`. ∎

**Exact status on the actual graph.** 174 distinct demanded ratios, 10 negative
(`FC-06`); 8040 of 8281 pairs uncloseable at `alpha = 1`, 8066 at the tuned
`9/5` (`FC-05`); and full closure for `sigma -> 2 sigma` at `alpha = 4` and for
`x* -> (5,5,5)` at unchanged `alpha` (`FC-07`, `FC-08`).

### 8.2 What the three legitimate readings of a nonzero `Lambda` are

§10 asks the mixed cycle to distinguish three things. It does:

| reading | diagnostic |
|---|---|
| **legitimate field exchange** | `Lambda != 0` with `alpha` calibrated — the actor genuinely operated across two different physical regimes. This is a **Carnot engine**: `F` is the state function that closes, `Delta F_actor` is the process quantity that does not, exactly as entropy closes while work does not |
| **inconsistent calibration** | `Lambda != 0` where a *single* `alpha` **could** have closed it — i.e. D holds but the declared `alpha` violates `alpha1 = alpha0/q`. Detectable and repairable |
| **hidden creation/destruction of units** | `Lambda != 0` with **no** `alpha` able to close it — the present case. Repeating the cycle `N` times returns the world to its exact initial state and moves `c_i` by `-4N/9` (or `+4N/9` reversed), without bound |

> **The third is not a bookkeeping error and it is not repaired by a gate.** No
> affordability rule is invoked anywhere here — the point is that an unboundedly
> repeatable credit accrued over a **null physical cycle** means the accumulated
> number is not measuring a physical quantity in one unit. That is precisely the
> failure of universality, stated without any appeal to `c_i >= 0`.

### 8.3 Import audit

| import | what it would supply | classification |
|---|---|---|
| **Carathéodory integrating factors / Pfaffian forms** | conversion of an inexact form into an exact one | **NOT APPLICABLE.** `dV_theta` is already exact, and here `F` is *defined* as a state function. Established in the companion study; unchanged |
| **Lieb–Yngvason axiomatic entropy** | `S` unique up to affine from accessibility | **NOT APPLICABLE.** A4/A5 have no referent on a fixed-total lattice; the Comparison Hypothesis fails on the actual graph. Established previously |
| **Empirical vs absolute temperature** | the distinction between an ordering scale and a calibrated unit | **DIRECT STRUCTURAL PARALLEL**, and the organizing idea of this document: `V_theta` is empirical, `alpha` is the analogue of `1/T` |
| **Carnot universality / zeroth law** | the theorem that promotes empirical to absolute temperature | **ANALOGY ONLY — and unavailable.** Carnot's universality is a consequence of the second law, which §9 forbids assuming; and EBU declares no cross-field reversible process and no two-reservoir contact to run it on |
| **Fluctuation theory, entropy Hessians (Einstein `P ~ exp(Delta S / k)`)** | ties the entropy *scale* to observable fluctuation magnitudes | **NOT APPLICABLE as declared** — EBU's dynamics is deterministic and declares no fluctuations. **But it names the missing datum most concretely: observable state fluctuations would fix `alpha`** |
| **Hessian / information geometry** | a canonical metric on the field manifold via the Fisher information of `p_theta` | **CONDITIONALLY DIRECT.** Immediately applicable *once a reference measure `p_theta` is declared*; with no measure declared there is no Fisher metric to compute |
| **Contact / symplectic thermodynamic geometry** | a Gibbs contact form making the first law a geometric identity | **NOT APPLICABLE.** Requires a declared contact structure and conjugate variables; EBU declares neither |
| **Dimensional analysis** | constraint from units | **NOT APPLICABLE, and this is a finding.** `V_theta = 1/2 sum ((x_i - x*_i)/sigma_i)^2` is **dimensionless** — `sigma` carries the material units — so `alpha` is a pure number and no dimensional argument can constrain it |
| **Conserved extensive variables** | a quantity `F` must be additive against | **AVAILABLE BUT INERT.** `M = sum_i x_i` is the unique linear conserved charge, and it does not couple to `V_theta` in any declared relation |
| **Constitutive relations** | the burden unit across fields | **THIS IS THE GAP.** The missing axiom is literally a constitutive declaration |

### 8.4 The calibration principle, stated as the theorem it would be

> **Theorem B' (what would suffice, and it is one thing in four dresses).**
> `alpha` is determined up to one global positive constant iff any one of:
>
> - **(a) declared reference measure.** A family `p_theta` on the state space
>   with `F := log p_theta` up to global affine. Then
>   `alpha(theta) = -d log p_theta / dV_theta`, and for `p_theta ∝ exp(-V_theta)`
>   this is `alpha ≡ 1`. Note what this does *not* do on its own: the
>   normalization `log Z_theta` enters only `beta`, which never touches an actor
>   credit — **the measure calibrates through its exponent, not its partition
>   function.**
> - **(b) declared standard action.** A family `G*(theta)` of actions declared to
>   carry equal freedom content; then `alpha(theta) = 1/E_theta(G*(theta))` up to
>   a global constant.
> - **(c) declared cross-field coupling.** Two regions held at `theta_1` and
>   `theta_2` exchanging material, with joint equilibrium declared to be where
>   total `F` is stationary; then `alpha(theta_1)/alpha(theta_2)` is *read off*
>   the equilibrium location — the EBU counterpart of thermal contact.
> - **(d) constitutive declaration.** A statement of whether `sigma` is a
>   physical property of the world or the unit of burden (§11A).
>
> **EBU declares none of (a)–(d), and no combination of §1, §2, §4, §6 implies
> any of them.**

---

## 9. The entropy property, precisely

The valuable property is: *once realized, `Delta S = S(B) - S(A)` is not repriced
when the system later changes.*

> **Theorem (permanence, unconditional).** For any `F` that is a state function
> of the full `X`, a credited increment `Delta F_actor = F(x1,theta) -
> F(x0,theta)` is evaluated once, at execution, from data then current. It is a
> difference of `F` at a fixed field, and no later field change revisits it.
> **The field at which a credit was earned need not be stored.**

*This is the architectural achievement of putting `theta` inside `X`, and it is
free — it holds for every admissible `phi_theta`.* It is the exact EBU analogue
of the entropy property, and it is delivered.

> **But permanence is not commensurability.** That `+3` earned at `theta_0` is
> never rewritten does not make it the *same quantity* as `+3` earned at
> `theta_1`. Entropy has both properties; `F` has the first unconditionally and
> the second only on condition D. **Local field change plays the role of changing
> temperature exactly as §9 hopes — and that is precisely why an absolute scale
> is needed and is missing.**

No second law is assumed anywhere, and no claim about drift toward larger `F` is
made; that question is outside this task and is untouched.

---

## 10. Mixed-cycle test — verdict

The cycle returns the complete physical state to its start. Total increments sum
to `0` (`FC-03`). Actor-attributed increments sum to `Lambda`, and on the witness
`Lambda = -4/9`, reversible to `+4/9` and repeatable (`FC-04`).

Applying §8.2's trichotomy to the declared Gaussian family:

| field pair | closure | verdict |
|---|---|---|
| `sigma -> c sigma` | `alpha` forced, all 8281 cycles close | **legitimate**, calibrated |
| `x*` along `span(sigma_i^2)` | `alpha` unchanged, all close | **legitimate**, calibrated |
| `sigma = (1,1,1) -> (1,2,3)` | no `alpha` closes; 174 demanded ratios, 10 negative | **hidden creation/destruction of units** |
| general moving `x*` | reorders states; no `psi`, no forced `alpha` | **hidden creation/destruction of units** |

---

## 11. Calibration witnesses

### A. `V1 = x^2/2` versus `V2 = a x^2/2`

The two induce the **identical ordering** of every state and the identical
equilibrium; they differ by the global positive factor `a`. With `alpha = 1` the
same action is credited `-1` and `-1/4` for `a = 1, 1/4`. *(Checked: `FC-10`.)*

> **Answer: undecidable without an additional constitutive axiom — option (c).**
>
> - Read `sigma` as a **physical property** (the world's actual tolerance): the
>   change is real, burden genuinely rescales, `alpha = 1` is right and the
>   factor is physical.
> - Read `sigma` as the **unit of burden**: the change is a ruler rescaling,
>   credits must be invariant, and `alpha(c sigma) = c^2 alpha(sigma)` is forced.
>
> Both are internally consistent. EBU's declaration of `V_theta` as "the burden
> field" with no independent operational access does not choose. **This is the
> single cleanest statement of the missing datum**, and note that it is the one
> case where *one* extra axiom settles the matter completely — because the two
> fields are ordinally equivalent.

### B. `sigma = (1,1,1) -> (1,2,3)`

| property | status |
|---|---|
| same equilibrium | **yes** — `argmin V = {x*}` under both |
| same ordering | **no** — `V_cur` is multivalued on 14 of 15 `V_ref` levels (`FC-02`) |
| same physical freedom unit | **no, and not fixable** — 174 demanded ratios, 10 negative (`FC-06`) |

A genuine physical change, ordinally inequivalent, and **uncalibrated**: ordinal
invariance has no purchase, so not even the §11A axiom would settle it.

### C. Moving `x*(theta)`

| move | status |
|---|---|
| along `span(sigma_i^2)` | `V` shifts by a constant (`3/2` for `x* -> (5,5,5)`), ordering and all EBU values unchanged, `alpha` unchanged, all cycles close — **calibrated and EBU-trivial** |
| general reachable move | equilibrium **tracks** `x*(theta)` correctly (golden requirement met), ordering changes, no forced `alpha` — **uncalibrated** |

---

## 12–13. Ownership and affordability — confirmations, not assumptions

**Ownership is not solved and is not needed.** `c_i` is allowed to retain
historical attribution; share diamonds are not treated as a failure anywhere
above. The question answered is only whether each credited increment is expressed
in one permanent unit, and the obstruction found — `Lambda != 0` with no `alpha`
available — is a statement about **units**, not about who owns what. It would
persist with a single actor.

**No affordability law is used.** No step in Theorems A, B, C, B', C-split or
Proposition E invokes `c_i >= 0`, `c_i + Delta F >= 0`, or a pre-action gate. The
minting argument of §8.2 deliberately concludes "the number is not measuring one
physical quantity", never "the action must be blocked". Q7 is therefore **NO**,
verified by inspection of every proof rather than asserted.

---

## 14. The three required theorems

> ### THEOREM A — EXISTENCE
>
> Under §6 (positive normalizer on actor directions) together with §7B's finite
> level-set compatibility, the universal current-state coordinates are exactly
>
> ```
> F(x, theta) = phi_theta( V_theta(x) ) ,      phi_theta strictly decreasing,
> ```
>
> and every such `F` satisfies §1's sign convention, §2's golden equilibrium
> requirement, §4's telescoping decomposition for separated events, and §9's
> permanence property. **Existence holds unconditionally for every Gaussian
> field family, fixed or moving `x*`, homogeneous or heterogeneous `sigma`.**
> Granting additivity over physically independent subsystems reduces the family
> to `F = -alpha(theta) V_theta + beta(theta)` with `alpha > 0` (Pexider;
> `FC-09`), with the caveat of §7C that a conservation-bound world cannot itself
> instantiate that axiom.

> ### THEOREM B — CALIBRATION / UNIQUENESS
>
> `beta(theta)` is a pure offset invisible to attribution. `alpha(theta)` is the
> whole calibration, and:
>
> **(i)** Nothing in §1, §2, §4 or §6 constrains `alpha`. Every positive
> `alpha(·)` yields a coordinate meeting all declared requirements.
> **(ii)** For a field pair, `alpha` is forced up to a global constant **iff**
> `V_theta' = q V_theta + const` on each reachable component (condition D), and
> then `alpha(theta') = alpha(theta)/q`.
> **(iii)** Outside D no `alpha` exists even making the actor circulation vanish:
> the demanded ratios take 174 distinct values, 10 negative.
>
> **Therefore `F` is determined only up to a `theta`-dependent recalibration, not
> up to a global affine gauge — except on condition-D orbits. The theorem cannot
> be completed from current EBU data, and the single missing item is the
> constitutive axiom of §8.4 in any one of its four forms.**

> ### THEOREM C — ATTRIBUTION CONSISTENCY
>
> **(i)** Credited increments are never repriced — unconditional (§9).
> **(ii)** Total mixed full-state cycles close — unconditional (`FC-03`).
> **(iii)** The actor/field split is path independent under simultaneous change
> **iff** `partial^2 F / partial theta partial x = 0`, i.e. `F = W(x) + g(theta)`
> (Theorem C-split), i.e. condition D.
> **(iv)** The actor-attributed circulation round every mixed cycle vanishes
> **iff** condition D (Theorem B).
>
> **(iii) and (iv) coincide. Attribution consistency in the full sense — separate,
> well-defined, closing — holds exactly on condition D**, and on the frozen
> Gaussian family for `n >= 3` that is exactly common `sigma` rescaling composed
> with reference motion along `span(sigma_i^2)`.

---

## 15. Final questions

**Q1. Does a universal freedom state coordinate exist mathematically?**
> **Yes — abundantly, and that is the problem.** An infinite-dimensional family
> per field satisfies every declared requirement; additivity cuts it to one
> positive number per field.

**Q2. Physically calibrated by the current EBU ontology, or underdetermined?**
> **Underdetermined**, by exactly one positive function `alpha(theta)`. Rival
> calibrations credit the same action `-5/9` and `-5/314`, both legally.

**Q3. What exact physical relation is missing?**
> An operational definition of the burden unit across fields: a declared
> reference measure (equivalently, observable fluctuation statistics fixing
> `alpha = -d log p_theta / dV_theta`), or a declared standard action, or a
> declared cross-field coupling, or a constitutive statement of whether `sigma`
> is a physical property or the unit of burden. Dimensional analysis cannot
> supply it — `V_theta` is dimensionless.

**Q4. Which dynamic Gaussian families already admit a common calibrated coordinate?**
> Exactly condition **D**: `V_theta' = q V_theta + const` on each reachable
> component. For `n >= 3` that is common `sigma` rescaling `sigma -> c sigma`
> (with `alpha -> c^2 alpha`) composed with reference motion along
> `span(sigma_1^2, ..., sigma_n^2)` (with `alpha` unchanged). Verified by full
> closure of all 8281 mixed cycles in both witnesses.

**Q5. Can a completed `Delta F` remain permanently fixed without storing the field?**
> **Yes, unconditionally** — it is a difference of a state function at a fixed
> field, computed once and never revisited. This is delivered by the
> architecture. **But permanence is not commensurability**: outside D the stored
> numbers are in field-dependent units and may not be summed meaningfully.

**Q6. Can environmental field change be separated from actor error exactly?**
> **For separated events, yes, always.** **For simultaneous change, only on
> condition D** (Theorem C-split); otherwise the split is path dependent and
> `epsilon` is not a property of the executor.

**Q7. Does any result require `c_i >= 0` or a pre-action capacity gate?**
> **NO.** No proof uses either; §12–13 records the verification.

**Q8. Does any result require a history/source vector?**
> **NO.** `F` is history free; `c_i` stores one scalar; no field-history ledger,
> source vector or receipt portfolio appears in any construction or proof.

### What this pass adds to the record

| item | status |
|---|---|
| repricing | **eliminated architecturally** by placing `theta` inside `X` — free, unconditional |
| mixed-cycle total closure | **automatic**; the test's power lies entirely in the actor circulation |
| the calibration object | **isolated**: one positive function `alpha(theta)`, the EBU analogue of `1/T` |
| the underdetermination | **fully exposed** as a five-rung ladder (§7C), with the honest caveat that the affine rung is not derivable inside a conservation-bound world |
| condition **D** | **shown necessary and sufficient for three separate requirements at once** — calibration, path-independent actor/field split, and vanishing actor circulation |
| the missing axiom | **named in four equivalent forms**, with `sigma`-as-property vs `sigma`-as-unit the most primitive |

---

## 16. FINAL VERDICT

```
UNIVERSAL FREEDOM COORDINATE EXISTS BUT REQUIRES [ a constitutive axiom fixing
the burden unit across fields -- equivalently any one of: a declared reference
measure p_theta on the state space, giving alpha(theta) = -d log p_theta /
dV_theta; a declared standard action per field of equal freedom content; a
declared cross-field coupling whose joint equilibrium equates marginal freedoms;
or a declaration of whether sigma is a physical property of the world or the
unit in which burden is measured.  Absent it, F is fixed only up to a
theta-dependent recalibration alpha(theta) > 0, which collapses to one global
affine gauge exactly on condition D -- V_theta' = q V_theta + const on each
reachable component, i.e. common sigma rescaling composed with reference motion
along span(sigma_i^2) -- and on no larger class; outside D no alpha closes the
mixed-cycle actor circulation, the demanded ratios taking 174 distinct values of
which 10 are negative ]
```

END TASK.
