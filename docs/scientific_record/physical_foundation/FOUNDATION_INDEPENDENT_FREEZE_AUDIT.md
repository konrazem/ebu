The mathematical core survives this audit. I found **no counterexample to the correctly scoped identities**, and the published Stage-A values remain unchanged.

However, I cannot approve the final canonical document unseen: the attachment supplies the audit instructions, but not the actual reconciliation text or its source coordinate. There are also several qualifications that must accompany the frozen equations.

## 1. Authority and independent verification

I audited the specified Git objects, without changing branches:

| Item | Verified value |
|---|---|
| Publication commit | `2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32` |
| Publication tree | `5afe39788ecc6bff675b0820eef1669fb8b78ebf` |
| `demand_driven_ebu` identity | `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48` |

Independent verification completed:

- **2,768 exact-arithmetic checks; zero mismatches.**
- **66,396 checks against saved Stage-A records; zero mismatches.**
- All **768 episodes and 11,066 recorded epochs** covered.
- No runner, simulation, state-advancing function or scientific experiment executed.

These checks support the derivations below; they are not substitutes for their assumptions.

## 2. Critical finding: both sink branches already exist

This is resolved directly from the published implementation.

[PhysicalAction.increment](/Users/konrad.grzyb/code/ebu/demand_driven_ebu/physical.py:74) implements:

\[
\Delta_s=-q,\qquad
\Delta_d=\eta q,\qquad
\Delta_\ell=(1-\eta)q.
\]

[Route validation](/Users/konrad.grzyb/code/ebu/demand_driven_ebu/world.py:116) requires a declared sink when \(0<\eta<1\). That sink must already be a coordinate of the declared world, belong to the same resource, and have the sink role.

Both declarations already exist:

- `sink_audit_only`: physically tracked, excluded from valuation.
- `sink_in_potential`: physically tracked and valued.

They were **not invented by the equations in this reconciliation brief**.

Starting from the actual increment,

\[
\frac{dx}{dq}=(-1,\eta,1-\eta),
\]

the chain rule gives:

\[
f=-\nabla V^\top\frac{dx}{dq}
=\mu_s-\eta\mu_d-(1-\eta)\mu_\ell.
\]

Therefore:

| Declared valuation | Exact force |
|---|---|
| Audit-only sink, \(\mu_\ell=0\) | \(f=\mu_s-\eta\mu_d\) |
| Valued sink | \(f=\mu_s-\eta\mu_d-(1-\eta)\mu_\ell\) |
| Lossless route | \(f=\mu_s-\mu_d\) |

For an audit-only coordinate, the implemented potential is independent of that coordinate, so its mathematical partial derivative is zero.

**Freeze recommendation:** include both loss-aware formulas as explicitly conditional corollaries. Neither is a newly invented model extension. But neither should be presented as a loss-aware experimental result: the [Study-1 domain](/Users/konrad.grzyb/code/ebu/DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md:25) explicitly excludes lossy routes and sinks.

The known out-of-domain coupling limitations remain open.

### One genuine wording correction

The [valuation module](/Users/konrad.grzyb/code/ebu/demand_driven_ebu/valuation.py:23) says a valued sink “makes a lossy plan cost EBU.” That is too broad if understood as the sign of the **whole plan**.

In the existing `loss_world`, with state \((20,0,10,0)\), transferring one unit at \(\eta=1/2\) gives:

\[
E=\frac{57}{4}>0.
\]

Restoration elsewhere outweighs the sink contribution. Furthermore, with a nonzero sink reference, even the sink contribution need not always be adverse.

Correct statement: **a valued sink contributes its declared change in potential; the total endpoint difference determines the action’s sign.**

## 3. General core and Gaussian specialization

The hierarchy is sound:

1. The declared physical transition determines \(\Delta x\).
2. \(V\) is a constitutive field hypothesis.
3. \(\mu=\nabla_xV\) is a mathematical definition.
4. \(E=V_{\rm pre}-V_{\rm post}\) defines finite EBU.
5. \(f=-\nabla V^\top dx/dq\) is the directional derivative along a declared action.

Conservation alone does **not** uniquely derive the choice of \(V\) or the EBU definition.

For fixed \(\theta\), a single-valued \(C^1\) potential and a piecewise-smooth path inside its domain:

\[
E=-\int_\gamma\nabla V\cdot dx.
\]

**Presentation correction:** “differentiable” alone is not a sufficient general regularity statement for this integral identity. \(C^1\) is a simple sufficient condition; the Gaussian satisfies it.

For symmetric Gaussian \(H\),

\[
V(x)=\frac12(x-x^*)^\top H(x-x^*),
\qquad \mu=H(x-x^*).
\]

Direct expansion gives:

\[
V(x+\Delta)-V(x)
=\mu^\top\Delta+\frac12\Delta^\top H\Delta.
\]

Independently, along \(x+\lambda\Delta\),

\[
\nabla V=\mu+\lambda H\Delta,
\]

whose exact integral gives:

\[
\boxed{E=-\mu^\top\Delta-\frac12\Delta^\top H\Delta}.
\]

Both derivations agreed exactly in the independent checks.

### The two-coordinate formula is not the general definition

For a lossless transfer between two separable Gaussian coordinates:

\[
E=q\left[
\frac{x_s-x_s^*}{\sigma_s^2}
-\frac{x_d-x_d^*}{\sigma_d^2}
\right]
-\frac{q^2}{2}
\left[\frac1{\sigma_s^2}+\frac1{\sigma_d^2}\right].
\]

The Study-1 formula

\[
E=q(x_s-x_d-q)
\]

follows with equal references and unit scales in the chosen coordinates.

Exact counterexamples to using it generally, with \(x=(6,4)\), \(q=1\):

| References; scales | Correct \(E\) | Simplified formula |
|---|---:|---:|
| \((0,0)\); \((2,1)\) | \(-25/8\) | \(1\) |
| \((5,4)\); \((1,1)\) | \(0\) | \(1\) |

**Classification: STUDY-1 SPECIALIZATION ONLY**, not an equation needed to define EBU.

## 4. Finite value, refinement and simultaneous attribution

### Differential force is not finite value

For reference \((4,4)\), state \((6,4)\), unit scales and transfer \(q\):

\[
E=2q-q^2,\qquad E_{\rm linear}=2q.
\]

At \(q=3\), the linear estimate is \(+6\), while exact EBU is \(-3\).

At the reference:

\[
\mu=0,\qquad E=-\frac12\Delta^\top H\Delta.
\]

Strict negativity requires positive curvature along \(\Delta\). It holds for nonzero increments in the fully valued Study-1 Gaussian. With audit-only coordinates, the full-state Hessian has zero directions, so the unrestricted claim “every nonzero increment gives \(E<0\)” would be false.

### Refinement

Updated-baseline endpoint differences telescope:

\[
E(x,\Delta_1+\Delta_2)
=E(x,\Delta_1)+E(x+\Delta_1,\Delta_2).
\]

For quadratic \(V\), quoting both pieces from the original baseline instead gives:

\[
E(x,\Delta_1+\Delta_2)
-E(x,\Delta_1)-E(x,\Delta_2)
=-\Delta_1^\top H\Delta_2.
\]

The sign in the brief is correct.

### Common-path receipts

For fixed additive increments and \(D=\sum_a\Delta_a\),

\[
R_a=-\int_0^1\nabla V(x+\lambda D)^\top\Delta_a\,d\lambda.
\]

Summing inside the integral proves:

\[
\sum_aR_a=E_G.
\]

This establishes **closure**, not unique physical attribution, fairness or ownership.

### Shapley equivalence: quadratic only

For a quadratic potential, each pair interaction is divided equally by permutation-averaged marginal contributions. This gives exactly:

\[
R_a=-\mu^\top\Delta_a-\frac12\Delta_a^\top HD.
\]

Thus the stated Shapley equivalence holds for the fixed-additive subset game. Every required subset value must be defined; a physical interpretation additionally requires admissible subsets.

It is not general. For \(V(x)=x^3\), baseline \(0\), increments \(1\) and \(2\):

- Common-path receipts: \((-9,-18)\).
- Shapley receipts: \((-10,-17)\).
- Both total \(-27\).

## 5. Factors, conservation and accounting

For a declared factorization \(V=\sum_\alpha\phi_\alpha\):

- Coordinate separability is unnecessary.
- Unchanged factors cancel.
- Every affected coupled factor must be reevaluated in full.
- Möbius decomposition rearranges the same subset values; it creates no additional EBU.
- Quadratic \(V\) with **fixed additive increments** has interaction order at most two. Independently resolving a different action vector for each subset does not inherit that conclusion automatically.

Physical conservation is already implemented, **per resource**:

\[
-q+q=0,
\qquad
-q+\eta q+(1-\eta)q=0.
\]

Loss-aware full-state conservation is not merely an optional future idea. Its broader demand/coupling study domain, however, remains unsupported.

Separately, assuming exact settlement \(\Delta C=E\), fixed \(V\), and no unaccounted external state or balance changes:

\[
C_{t+1}+V(x_{t+1})=C_t+V(x_t).
\]

This is an **accounting theorem**, not physical carrier conservation. It requires no account-sign restriction.

Individual attribution can remain historical. At reference \((4,4,4)\):

- \(B\to C\), one unit: \(E=-1\), attributed to \(B\).
- Reverse \(C\to B\): \(E=+1\), attributed to \(C\).

The physical state returns and aggregate EBU is zero, but the attribution vector changes by \((0,-1,+1)\). That does not invalidate aggregate exactness; it prevents treating those individual balances as functions of current physical state alone.

## 6. Layer separation and remaining physics

None of the audited foundational identities requires the following:

| Rule or concept | Required? |
|---|---|
| \(B_i\ge0\) | NOT REQUIRED |
| Affordability | NOT REQUIRED |
| No borrowing | NOT REQUIRED |
| No pooling | NOT REQUIRED |
| Complete service | NOT REQUIRED |
| Persistent orders | NOT REQUIRED |
| No partial service | NOT REQUIRED |
| FIFO | NOT REQUIRED |
| Backlog | NOT REQUIRED |
| Price | NOT REQUIRED |
| Utility | NOT REQUIRED |
| Welfare | NOT REQUIRED |

Those may define later models, but cannot be promoted into premises of the physical valuation identities.

The proposed five-layer hierarchy is appropriate. Two cautions:

- Calling \(f\) a “force” does not prove it is a measured mechanical force or establish a dynamical response law.
- Mathematical exactness of a chosen Gaussian does not establish its physical validity.

The physical origin of \(V\), measurement of \(\sigma\), covariance/susceptibility relations, changing fields, environmental valuation, entropy, rate-function interpretation and universal \(\kappa\) all remain **NON-BLOCKING OPEN PHYSICS QUESTIONS** for freezing a clearly conditional mathematical core.

For entropy compatibility, require spatially constant \(S_{\rm eq}\) and constant nonzero \(\kappa\), at fixed \(\theta\):

\[
S=S_{\rm eq}-\kappa V
\implies
\nabla S=-\kappa\mu,\qquad
\frac{\Delta S}{\kappa}=E.
\]

Positive \(\kappa\) is needed for the intended entropy-deficit interpretation. Variable \(\kappa\) or \(S_{\rm eq}\) introduces extra derivative terms.

**MATHEMATICALLY COMPATIBLE, PHYSICALLY UNPROVED.** Defining a normalizable distribution proportional to \(e^{-V}\) does not independently validate \(V\).

## 7. Freeze-candidate equation table

| Equation | Layer and scope | Status; verification | Recommendation |
|---|---|---|---|
| Declared \(\Delta x\), per-resource conservation | 1; declared transition model | Implemented model; exact increment checks | Freeze with model scope |
| \(\mu=\nabla V\) | 2; differentiable \(V\) | Definition | Freeze |
| \(E=V_{\rm pre}-V_{\rm post}\) | 2; same declared field | Finite EBU definition; saved-record agreement | Freeze |
| \(E=-\int\nabla V\cdot dx\) | 2; sufficient regularity, fixed field | General theorem; chain rule | Freeze with regularity |
| \(f=-\nabla V^\top dx/dq\) | 2; differentiable action path | General chain-rule identity | Freeze |
| \(f=\mu_s-\eta\mu_d\) | 2; constant efficiency, unvalued sink | Conditional corollary; exact checks | Conditional branch |
| \(f=\mu_s-\eta\mu_d-(1-\eta)\mu_\ell\) | 2; valued sink | Conditional corollary; exact checks | Conditional branch |
| Gaussian finite formula | 2; fixed quadratic \(V\) | Theorem; two derivations | Freeze |
| \(E=q(x_s-x_d-q)\) | 2; Study-1 assumptions | Specialization; counterexamples outside scope | Freeze only with assumptions |
| \(\sum_aR_a=E_G\) | 3; declared common-path convention | Closure theorem | Freeze without uniqueness claim |
| \(C+V=\mathrm{constant}\) | 3; declared settlement and closure assumptions | Accounting theorem | Freeze as accounting only |

## 8. Stage A and final freeze conditions

**STAGE A UNCHANGED** for the published implementation and saved numerical records checked here. Study 1 is lossless, uses no sink, and every saved epoch’s EBU agrees with independent endpoint evaluation.

I cannot separately certify the unnamed Gate-1–Gate-5 reports or the absent reconciliation document. Those are source-identification gaps, not mathematical failures.

Remaining items:

- **BLOCKER:** supply the exact reconciliation text and immutable identity before certifying that document or issuing an unrestricted “NO THEORY MODIFICATION FOUND.”
- **BLOCKER:** identify the Gate-1–Gate-5 records if their individual non-interference certification is part of the freeze.
- **PRESENTATION CORRECTION ONLY:** state sufficient path-integral regularity; retain sink/domain qualifications; qualify strict negativity with curvature; do not claim valued losses necessarily make total EBU negative; state the entropy constants explicitly.
- **NON-BLOCKING OPEN PHYSICS QUESTION:** the physical interpretations listed above.

No files changed. Starting and final local HEAD: `6538f919dbc4b394a4a4977494d0332e251fd2e8`. The ten existing untracked theory files were untouched. Nothing committed, pushed or executed; Stage B was not begun.

**INDEPENDENT FREEZE AUDIT CONDITIONAL PASS — identify and inspect the exact canonical reconciliation and gate records, and attach the regularity, sink-domain, curvature and entropy qualifications above before freeze.**
