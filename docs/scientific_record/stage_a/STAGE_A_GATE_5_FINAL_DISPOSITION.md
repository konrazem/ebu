Coordinate re-verified. One new fact surfaced that sharpens the synthesis: **in A3 the affordability gate never bound** — every candidate plan was affordable in every one of the 256 episodes.

---

# STAGE A — FINAL SCIENTIFIC DISPOSITION

**Study:** `2c4b71d1…fe9e32` / tree `5afe3978…b78ebf` / preregistration `a74d8380…54bd17`. 768 jobs, 11,066 epochs, verifier 36/36, preflight 76/76.

## 1. Carried qualifications (none omitted)

**Gate 1** — (i) A3 decomposition-gate exception: 4,737 epochs in 192 episodes, all inert at `x*` (`g:[]`, EBU 0, state unmoved), 0 outside the three-part guard, 0 active-demand epochs unverified; (ii) `reserve_path` omits its registered `t=0` element, value pinned to 0 by the accounting identity; (iii) `capacity_source_residual` enforced only at end-of-episode and never persisted — reconstructed as exactly 0 at all 11,066 epochs.

**Gate 2** — (iv) uniform-over-plan-identities ≠ uniform-over-physical-outcomes (82/256 A3 arrival menus, shape 4 plans → 3 outcomes; exposed arms `control` 9 and `ebu_random` 9; outcome-invariant for aligned/hostile); (v) A3 `arrival_baseline` and `prelude_reserve` are endogenous and policy-dependent; (vi) `RESTORATION_COMPLETED` is narrowly defined.

**Gate 3** — (vii) no preregistered arm contrast, effect size, interval or test existed, so none was computed; (viii) no post-hoc confirmatory metric was introduced.

**Gate 4** — (ix) A1 is fixture-specific behavioural evidence; (x) the aligned policy is researcher-programmed, not an incentive theorem; (xi) hostile means no recovery *within horizon*, not impossibility; (xii) control recovery shows the EBU gate is not necessary for recovery in this fixture; (xiii) A2 demonstrates enforcement, not desirability; (xiv) A3 demonstrates the lifecycle, not whole-system equilibrium restoration; (xv) long-run homeostasis unresolved.

## 2. L / R / P — frozen status

| | status | source | Stage A's role |
|---|---|---|---|
| **L — equilibrium location** | **ESTABLISHED MATHEMATICALLY, before Stage A.** For the reference Gaussian with `x*` a reachable lattice point, `argmin W = {x*}`; under V1 accounting `C = I − W`, so `argmax C = argmin W` | synthesis §3–§4 | **None.** Stage A neither tests nor re-proves L |
| **R — accessibility** | **ESTABLISHED STRUCTURALLY, before Stage A.** Under the implemented atomic P rule, `x*` is reachable from all 91 states, monotonically, `x*` the unique absorbing state — by exhaustive enumeration, not simulation | synthesis §10–§12 | **None.** Stage A does not re-prove R, and R is explicitly *not* a recovery or affordability claim |
| **P — affordability + policy** | **This is Stage A's entire contribution**, and it is new: how declared local policy rules and the affordability gate behave on a fixture where L and R are already settled | Stage A | All of §3–§5 below |

The separation held throughout: the execution report itself states the 91/91 result "is a statement about reachability, **not** about recovery, affordability or policy behaviour."

## 3. A1 — final disposition

**OBSERVED (exact, `study-one-v1`, `x₀=(1,7,4)`, `V=9`, T=32, 64 paired replicates per arm):**

| arm | returned | `return_time` | terminal |
|---|---|---|---|
| `control_random_no_ebu` | **64/64** | 2–20 (33 at t=2) | `(4,4,4)`, `V=0`, `B_total=9` |
| `ebu_random` | **64/64** | 2–14 (33 at t=2) | `(4,4,4)`, `V=0`, `B_total=9` |
| `ebu_aligned` | **64/64** | **2 in all 64** | `(4,4,4)`, `V=0`, `B_total=9` |
| `ebu_hostile` | **0/64** | censored ×64 | 8 distinct non-equilibrium states, `V=1`(36)/`V=3`(28) |

**SUPPORTED:** in this fixture, the choice of local policy rule materially changes restoration trajectories — including whether the reference is reached at all within the registered horizon.

**NOT ESTABLISHED:** universal optimality of any rule; universal necessity of EBU; eventual non-recovery of hostile beyond t=32; emergent or self-interested cooperation; long-run stability.

**The negative result is not softened.** In **every** hostile episode, restoration did not occur within 32 transitions, on a fixture where `x*` is provably reachable from all 91 states. Hostile ended away from equilibrium in 64/64, holding `B_total` of 8 or 6.

## 4. A2 — final disposition

**OBSERVED:** identical fixture (`x₀=x*`), identical single order, identical 2-plan menu in all four arms, zero opening reserve. `control` executed 64/64 (33× `(4,3,5)` at EBU −1; 31× `(4,2,6)` at EBU −4), driving owner B to −1 or −4 and inducing a P-deficit. The three EBU arms recorded `affordable_count = 0`, refused execution, left the state exactly at `x*`, balances at 0, and retained the order as `ADMITTED_BUT_EBU_UNAFFORDABLE`.

**SUPPORTED:** *the capacity/affordability mechanism causally changes execution.* Menu, order and physics are held fixed; the gate is the only difference; the outcomes differ categorically.

**NOT SUPPORTED:** that the refusal is economically or socially desirable. A2 measures enforcement, not welfare, and cannot: its 1-epoch horizon makes the consequences of the control's negative balance unobservable by construction.

**Zero opening reserve is a deliberate fixture condition,** so A2 is a mechanism demonstration at a chosen operating point, not a general service theorem.

## 5. A3 — final disposition

**OBSERVED:** all 256 orders admitted and **served at epoch 3**, 0 pending epochs. All 256 reached `RESTORATION_COMPLETED` with `closure_count/tracked_count = 1/1`; `first_simultaneous_closure` ∈ {5, 6, 7}; every episode ran the full 32 transitions, so **no tracked-closure endpoint is horizon-censored**. Baselines and reserves were policy-dependent: aligned arrived at `(4,4,4)` with `B=9` in all 64; hostile at `(5,3,4)` with `B=8` in all 64; control and `ebu_random` spread over 4–5 baselines.

**SUPPORTED CLAIM, exactly:** the registered E-demand → physical consequence → endogenous P-demand → tracked-deficit-closure lifecycle **can execute successfully in `study-one-v1`**.

**NOT CLAIMED:** common-baseline arm comparison; whole-system equilibrium restoration; sustained closure; absence of newly created deficits; that reserve was necessary for every order; that EBU caused every restoration.

**One further boundary this audit establishes:** in A3 the affordability gate **never bound** — `plans == affordable` in every episode of every arm, and the paying owner held `B = 8` or `9` throughout. A3 therefore exercises the *lifecycle*, not the *gate*. The gate's operational evidence comes from A2 alone.

## 6. Accounting / capacity — three separate achievements

| | status |
|---|---|
| **A. Exact accounting closure** | **ESTABLISHED, within scope.** Four residuals exactly `0/1` at all 11,066 epochs; joint gate closed at all 11,066; `capacity_source_residual` reconstructed exactly 0 at all 11,066; `B_total(t) = V(x₀) − V(x_t)` at all 2,618 A1 checks; conservation and non-negativity violated 0 times |
| **B. Operational affordability gate** | **ESTABLISHED, within scope — and only by A2.** Categorical execute/refuse divergence at a zero-reserve equilibrium. Inert throughout A3 |
| **C. Reliable homeostasis** | **OPEN.** Nothing in Stage A addresses it. One displacement, one order, one schedule, 32 epochs, no repetition |

These are not combined into a single verdict.

## 7. Incentive status

> **Stage A did NOT prove that self-interested actors will choose aligned actions.**

All four policies were **researcher-declared rules**, not outcomes of any optimisation, preference or equilibrium argument. The aligned arm is `argmax E_G` because it was written that way. Stage A is therefore evidence about **the consequences of different local policy rules**, never about **the endogenous emergence of those rules**.

The hostile arm stands as useful negative/control evidence: **choosing locally adverse EBU-valued actions can prevent recovery within the registered horizon even where equilibrium remains physically accessible** — 0/64, on a graph where `x*` is reachable from all 91 states. This is a fixture-specific observation and is not a universal theorem.

## 8. What Stage A falsified / ruled out

| candidate claim | ruled out? | exact evidence |
|---|---|---|
| "all demand-serving policies behave equivalently" | **YES, in this fixture** | A1: 64/64 return for three arms vs 0/64 for hostile; `ebu_aligned` at `t=2` in all 64 vs control spread 2–20 |
| "the EBU affordability gate is merely decorative" | **YES, in this fixture** | A2: identical 2-plan menu, `affordable_count` 2 vs 0, execute vs refuse, state moved vs untouched |
| "physical accessibility alone guarantees behavioural recovery" | **YES — the sharpest falsification** | R gives `x*` reachable from all 91 states; hostile returned in 0/64 within T=32. Accessibility is not recovery |
| "aligned and hostile cannot be distinguished in this fixture" | **YES** | Disjoint stopping-reason sets; disjoint terminal-state sets; disjoint `return_time` support |
| "all A3 service necessarily requires positive previously earned reserve" | **NOT TESTED — neither ruled in nor out** | The gate never bound in A3 (all plans affordable everywhere); the paying owner always held `B = 8`/`9`. No A3 episode probed insufficient reserve. The A2-vs-A3 juxtaposition at `x*` (B=0 → 0 affordable; B=9 → 2 affordable) is suggestive but is **not a registered contrast** and is recorded as observation only |

## 9. What remains open

General restoring tendency; long-run stochastic homeostasis; endogenous incentive compatibility; robustness to larger graphs and other topologies; lossy routes (η < 1); sinks; heterogeneous resources and factors; changing fields; dynamic-capacity / entropy-like theory (untouched here by instruction); general service performance; the effect of random-plan multiplicity on outcome distributions; whether reserve is load-bearing for service; and behaviour beyond a 32-epoch horizon. **Stage B is not asserted to answer all of these** — several are domain or theory questions that no single study resolves.

## 10. Stage-B scientific purpose (no design)

Stage B is now justified to address exactly one question:

> In a **long-run stochastic economy** — repeated exogenous E-demand, endogenous P-demand, and declared actor-policy dynamics — **does a persistent restoring tendency emerge, conditional on policy?**

Kept strictly separate from universal incentive compatibility. Stage B may measure **policy-conditioned long-run behaviour**; it cannot by itself establish why real actors would adopt any policy.

## 11. Methodological constraints inherited (no numeric parameters)

No arbitrary forced actions; all actions demand-conditioned; strong atomic P provenance retained; E-orders additive and complete under current declared semantics; raw exogenous arrivals common across arms; no FIFO/global scheduler unless explicitly introduced and justified; independent-progress semantics; exact distinction between physical impossibility, search uncertainty and EBU affordability; **random-policy semantics declared explicitly — uniform over plan identities OR over unique outcomes, never left ambiguous**, and if uniform-over-plans, plan multiplicity is part of the policy definition; common inputs and pairing across arms where possible; all primary long-run endpoints preregistered before execution; no reuse of Stage-A outcomes to tune thresholds; L/R/P separation preserved; and — added by this audit — **persist every registered integrity field per epoch** so no endpoint needs reconstruction, and **declare in advance whether the affordability gate is expected to bind**, since in A3 it did not.

## 12. Claim-status table

| claim | status | evidence | scope | forbidden stronger wording |
|---|---|---|---|---|
| Equilibrium location `argmin W = {x*}` | **ESTABLISHED MATHEMATICALLY** | synthesis §3–4, pre-Stage A | reference Gaussian, reachable `x*` | "Stage A showed equilibrium is at `x*`" |
| 91/91 physical accessibility | **ESTABLISHED STRUCTURALLY** | exhaustive enumeration, pre-Stage A | frozen Study-1 graph, atomic P | "the system recovers from all 91 states" |
| Atomic-P refinement consistency | **ESTABLISHED STRUCTURALLY** | served-set-dominance irredundancy; existential provenance | declared semantics | "restoration is always legal" |
| Exact accounting closure | **OBSERVED IN STAGE A** | 4 residuals `0/1` × 11,066; identity at 2,618 checks | 768 episodes | "EBU accounting is exact in general" |
| Affordability gate operationality | **OBSERVED IN STAGE A** | A2: 2 vs 0 affordable, execute vs refuse | A2 only; inert in A3 | "the gate protects the system" |
| `ebu_aligned` A1 return | **OBSERVED IN STAGE A** | 64/64 at `t=2` | one fixture, one amplitude | "aligned is optimal" |
| `ebu_hostile` A1 non-return | **OBSERVED IN STAGE A** | 0/64 within T=32 | within horizon only | "hostile can never recover" |
| `control`/`ebu_random` A1 recovery | **OBSERVED IN STAGE A** | 64/64 each | one fixture | "EBU is unnecessary" |
| A3 lifecycle executes | **SUPPORTED WITH QUALIFICATION** | 256/256 served; closure at 5/6/7, uncensored | endogenous baselines; narrow label; gate never bound | "EBU restores the system after economic service" |
| General restoring tendency | **NOT SUPPORTED** | — | — | any claim of tendency |
| Incentive compatibility | **NOT SUPPORTED** | policies were declared, not derived | — | "EBU makes restoration self-interested" |
| Long-run homeostasis | **OPEN** | not addressed | — | any stability claim |
| Dynamic EBU capacity theory | **OPEN — and out of scope here** | not used by instruction | — | any use of it to reinterpret Stage A |

## 13. Official Stage-A scientific summary

**What was tested.** Three registered episode classes on the frozen `study-one-v1` world, four declared policy arms × 64 paired replicates = 768 episodes: A1, recovery from one declared 3-unit displacement with no economic demand; A2, one economic order at equilibrium from zero reserve; A3, the E-demand → physical consequence → endogenous P-demand → restoration chain with a scripted order at epoch 3.

**What was observed.** Execution integrity was complete: 768/768 jobs, 11,066 epochs, all residuals and gates exact, four attempt records preserved, one declared and fully bounded operational deviation. In A1, three arms returned to the reference in 64/64 and the hostile arm in 0/64 within 32 transitions. In A2, the three EBU arms found zero affordable plans and refused while the control executed, moving the state and driving a balance negative. In A3, all 256 orders were served at epoch 3 and all reached tracked-deficit closure within the horizon, from policy-dependent baselines, with the affordability gate never binding.

**What survives adversarial review.** That exact accounting closure holds across every recorded epoch; that the affordability gate causally changes execution at a zero-reserve equilibrium; that the registered chain lifecycle can execute end-to-end; and that local policy choice materially changes restoration trajectories in this fixture — including the decisive negative result that physical accessibility alone does not produce behavioural recovery.

**What failed or remains unresolved.** No incentive claim survives: the policies were written, not derived. No general restoring tendency, no long-run homeostasis, and no claim beyond one world, one displacement, one order and one schedule. Two registered integrity fields required reconstruction rather than being read. A3 did not exercise the gate it was partly built around, and whether earned reserve is load-bearing for service was not tested.

**Why continued research is justified.** Stage A discharged what it was designed to discharge — that the mechanism runs exactly, that the gate is operational, and that the chain closes — while leaving the programme's central empirical question untouched by construction. That question, whether a policy-conditioned restoring tendency persists under repeated stochastic demand, is now well-posed, is not answerable by enumeration, and has an environment whose L and R structure is fully known in advance. That is the correct precondition for a long-run study, and it is the reason to continue rather than a result that recommends it.

---

# 14. STAGE-A FINAL DISPOSITION

```
STAGE A SCIENTIFICALLY ACCEPTED WITH BOUNDED CLAIMS —
PROCEED TO STAGE-B PREREGISTRATION DESIGN
```

All fifteen carried qualifications remain attached to every claim above; the bounded claims are exactly those marked ESTABLISHED, OBSERVED or SUPPORTED WITH QUALIFICATION in §12, and nothing marked NOT SUPPORTED or OPEN may be cited as a Stage-A result.

Stage-B design not begun. No files modified; the audit ran read-only against a `git archive` export of the published tree.