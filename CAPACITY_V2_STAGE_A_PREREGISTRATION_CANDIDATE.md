# Capacity-V2 Stage-A preregistration CANDIDATE

Status: **candidate for author review. NOT FROZEN. NOT AUTHORIZED TO EXECUTE.**

Proposed protocol id: `EBU-CAPACITY-V2-STAGE-A-V1`.

This task's scope was theory, candidate derivation, static conformance and
comparative experimental-design preparation. It contains no execution
authorization section, and the programme treats design, preregistration,
implementation and execution as separate authorization boundaries. So this
document prepares the study and stops.

Model under test: `EBU-CAPACITY-V2-DEVIATION-BOUNDED-LOCAL-v1`. The registered
V1 mechanism, its artifacts and its preregistrations are untouched.

## 1. An honest statement of what this study can and cannot discover

**The qualitative outcome is already proved.** Stating it plainly so the study
is not later presented as an empirical discovery of something derived:

**Theorem V2-5 (almost-sure absorption, forcing off).** Under V2 on the
registered integer lattice with `q = 1`, from any reachable state the process
reaches `x*` and remains there almost surely.

*Proof.* (i) A restorative singleton has `Delta B_owner = E > 0`, so it is
affordable from any nonnegative balance — the ceiling applies after settlement
and never causes a refusal. (ii) By Lemma 2.2 of the failure analysis, whenever
`V > 0` some cell is at least one unit above its reference and some at least
one below, and moving one unit between them has `E = (x_i - x_j) - 1 >= 1 > 0`
and reduces the L1 distance to `x*` by 2. So a strictly restorative singleton
always exists and is always affordable while `V > 0`. (iii) Uniform random
choice assigns positive probability to every affordable group, so the finite
restorative path has positive probability. (iv) By Theorem V2-1, `x*` is
absorbing. A finite Markov chain with an absorbing state reachable from every
state is absorbed almost surely. □

Consequently the **presence** of absorption is not in question. What this study
can genuinely measure is:

- the **distribution of time to absorption**, which no theorem gives;
- whether absorption occurs within a declared horizon;
- the **paired comparison against the physical-random control**, whose
  behaviour is not constrained by any of these theorems;
- deadlock, which theory predicts cannot occur here but which must be observed
  rather than assumed.

A conformance probe at non-registered seeds (disclosed in section 8) absorbed
in 40/40 runs at each of three shock sizes, consistent with the theorem.

## 2. Frozen physical world — identical to registered Stage A

3 cells, `x* = (10,10,10)`, `sigma = (1,1,1)`, `M = 30`, complete directed
graph, transfer quantum `{1}`, `m_max = 2`, 21 candidate groups, `C_G = 0`,
`owner(a) = src(a)`, exact rational arithmetic at zero tolerance,
`EBU-GAUSSIAN-EVENT-PROFILE-v1`.

Deliberately identical so that any difference from registered Stage A is
attributable to the capacity state law and nothing else.

## 3. Frozen mechanism

    affordability:  B_i + Delta B_i >= 0        (unchanged from V1)
    settlement:     B_i^raw = B_i + Delta B_i
    ceiling:        B_i'    = min(B_i^raw, V_i(x'))
    retirement:     C      += sum_i (B_i^raw - B_i')
    invariant:      B_i <= V_i(x_i) at every observation point
    exact ledger:   V + sum_i B_i + C = J

The ceiling is re-imposed after external forcing. No decay, expiry, absolute
cap, demurrage, pooling, borrowing or value-ranked selection exists.

## 4. Frozen arms, shock, horizon, replicates

- **Arm A** `capacity_v2_affordability_random_actor`.
- **Arm B** `physical_feasibility_random_actor`, the matched control, which
  removes only the affordability gate and keeps a signed shadow ledger measured
  under the same ceiling.
- One conservative shock at tick 0, forcing-only, drawn exactly as registered
  Stage A: edge uniform over the 6 sorted edges, magnitude from `{2}`, so
  `D_r = 4` for every replicate.
- Horizon **H = 256** post-shock actor ticks. Tick 0 is the shock.
- **N = 128** paired replicates, matching registered Stage A.

## 5. Frozen exact invariants — zero tolerance

1. `V_t + sum_i B_i(t) + C_t = J_t`
2. `sum_i x_i = 30`
3. `x_i >= 0`
4. `B_i <= V_i(x_i)` (the ceiling invariant)
5. `sum_a R_a = E_G`
6. Arm A only: `B_i >= 0`
7. `C_t` monotone nondecreasing

Any nonzero residual is a foundation failure and halts interpretation.

## 6. Frozen endpoints

**Primary (the question the theorems leave open):** time to absorption

    T_r = first t in 1..H with V_r(t) = 0, censored at H+1 if never reached.

Reported as a distribution with explicit censoring, never as a mean over
censored values.

**Primary paired contrast:** `L_r` as in registered Stage B — mean `V/V_max`
over `t = 1..H` with the common `V_max = 300` — and
`Delta_r = L_r^V2 - L_r^CTRL`, tested by an exact two-sided paired sign test at
`alpha = 0.05` with a sign-based median confidence interval. `V_max` is a
common physical bound, so the ordering is not structurally forced.

**Practical threshold:** `delta_meaningful = 0.05` on the `V/V_max` scale,
declared in advance and kept separate from `alpha`.

**Mandatory secondary, descriptive:** absorption fraction; whether any replicate
left the reference after reaching it (theory says none may — an occurrence
would falsify the implementation, not the theory); deadlock ticks; peak
`sum_i B_i` against the bound `V(x)`; terminal `C`; and the registered-Stage-A
comparison of trajectory classes, reported descriptively only.

## 7. Frozen success distinction

Per the controlling distinction, and declared before results:

- **A — damping / convergence:** here *proved* by Theorem V2-5, so observing it
  is confirmation of the implementation, not evidence for the mechanism.
- **B — persistent bounded protection:** `sum_i B_i <= V <= V_max` at all times,
  also proved (Theorem V2-2).

Because both are theorems in the forcing-off regime, **Stage A-v2 is primarily a
software-conformance and quantitative-timing study.** The scientific weight of
the V2 programme sits in Stage B-v2, where no comparable theorem is available.
This must not be restated after results.

## 8. Prior exposure disclosure

Conformance probes on this world at non-registered seeds: `(11,29)` for 96
ticks, and `(100+k, 500+k)` for `k = 0..39` at shock magnitudes 2, 4 and 6 for
up to 600 ticks. Purpose: software conformance and checking Theorem V2-5. No
parameter was tuned afterwards; the world is inherited unchanged from
registered Stage A.

Registered seeds must be derived mechanically from this document's frozen
commit by the established rule, with the protocol id changed:

    first 8 bytes big-endian of SHA256(ASCII("EBU-CAPACITY-V2-STAGE-A-V1|<C_pre>|rrr|STREAM"))

streams `FORCING` and `ACTOR`, `rrr` zero-padded to 3 digits, `|` = `0x7C`, no
trailing newline. No result-dependent inclusion or exclusion.

## 9. Non-claims

This study will not establish that EBU is stable, that the capacity rule is
correct causal or ethical attribution, or that any real economy behaves this
way. It concerns one synthetic 3-cell lossless world, one shock magnitude, one
potential and one action menu. Absorption here is a lattice-and-menu-dependent
theorem, not a general property of the mechanism.
