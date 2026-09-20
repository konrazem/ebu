# Local Gaussian EBU — Stage-A implementation decision packet (G0)

Status: **implementation decision packet**. It resolves only the details that
must be concrete in code to build the Stage-A environment. It registers no
parameters, runs no study, and claims no evidence about EBU stability.

Base coordinate: `0d8726a712ed6cb6d989f73b84a7e24bdea64894`
(tree `cb7ebfc4c1198093867fd6bae2e30d22988e8b5d`), branch
`gaussian/stage-a-environment`.

Authority consumed: `AGENTS.md`, `CURRENT_SCIENTIFIC_AUTHORITY.md`,
`LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md`,
`LOCAL_GAUSSIAN_EBU_FRAMEWORK_DECISION.md`,
`LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md`.

This packet answers roadmap gate G0 and the reconciliation's G1–G5 gates at
implementation resolution only. Stage-A execution (roadmap G4) stays
unauthorized.

## 0. Framework disposition actually used

F2 is confirmed by evidence, not assumption. The source-locked framework
package subtree `4de85ed2935d1c35bdcc0f1259f0acb2df569fdd` is **installed**
in this checkout's virtual environment as `ebu_framework 0.1.0a1`. All 45
packaged source files hash-match the locked subtree byte-for-byte, and
`settlement.py` matches the I-3C repaired blob
`3c698e9b22995c7895cd7c1c79bc12d8f1d4e660` recorded in the framework
decision.

Integration method: **import the pinned installed distribution**. No
vendoring, no second framework, no lineage merge, no edit to any framework
module. `framework-v0.1` is not an ancestor of this branch and stays that
way. Historical engines (`d0_v29.py`, `ebu_test_*.py`, `longhorizon_v30.py`,
`ebu_quote_v30.py`) are neither imported nor modified by the new code.

## A. Exact event order

Registered as a separately named profile `EBU-GAUSSIAN-EVENT-PROFILE-v1`,
ten ordered phases per tick:

1. external forcing
2. freeze physical pre-action state `z`
3. generate physical candidate groups (EBU-blind)
4. physical feasibility
5. exact EBU valuation
6. capacity affordability
7. seeded random actor choice
8. exact execution
9. capacity settlement
10. audit

Per framework decision F2-A this profile does **not** amend
`ebu_framework.events.PhaseOrdinal` or the Dynamic Coordination ten-phase
chronology. Those keep their historical meaning; the Gaussian profile is a
new, separately named object. EBU calculates; EBU does not choose. No
max-EBU, min-V, service-first, least-harm, preservation, gradient-following
or restorative-fallback selector exists anywhere in the new code.

## B. Action ownership and capacity attribution

Atomic action `a` is a transfer of a declared nonnegative rational quantity
`q_a` from source cell `src(a)` to destination cell `dst(a)`, so
`delta_a = q_a (e_dst - e_src)`.

**`owner(a) = src(a)`** — exactly one owner per action, declared on the
action definition, never inferred from framework
`requesting_actor_ref`/`responsible_provider_ref` (F2-B forbids that
inference). The owner is the cell that moves its own stock.

Same-event signed netting over owned receipts:
`Delta B_i = sum over a in G with owner(a)=i of R_a`.
Settlement is atomic and all-or-nothing: either every owner's balance is
updated or none is. No per-action pre-funding, no sequential debit order, no
global pool, no borrowing, no refill, no issuance, no direct transfer.

This is a declared prospective model rule, not a consequence of group
closure.

## C. Simultaneous-group generation

Exhaustive deterministic enumeration (task §12), no proposal heuristics and
therefore **no third RNG stream**.

The atomic menu is every `(src, dst, q)` with `src != dst` on a declared
edge set and `q` from a declared finite quantum set. Candidate groups are
all subsets of size `1..m_max` of that menu in canonical order, where
canonical order sorts atomic actions by `(src, dst, q)` and groups
lexicographically by their sorted action-id tuples. `m_max` is configuration,
defaulting to 2 for the Stage-A fixture.

A group may contain at most one action per `(src,dst)` pair. The empty group
is handled under decision I, not enumerated here.

## D. Random choice semantics

Uniform over the canonically ordered affordable candidate list, drawn with
the exact counter-hash categorical sampler at equal integer weights
(denominator = list length). Selection is by **index only**.

The chooser is structurally blind: it receives a list of opaque candidate
identities and a count. It never receives, and cannot reach, `E`, its sign,
`V`, `mu`, equilibrium distance, balances or future forcing. No homeostatic
preference is encoded.

## E. Information-access boundaries

| Stage | May read | Must not read |
|---|---|---|
| Candidate generation | `x`, edges, quanta, `m_max` | `V`, `mu`, `E`, `B`, `J` |
| Physical feasibility | `x`, topology, bounds, group | `E`, `B`, global `V`, actor preference |
| Valuation | `z` restricted to affected factors | `B`, `J`, actor identity |
| Affordability | `R_a`, `owner`, `B` | `V`, `mu`, future forcing |
| Actor choice | affordable candidate ids, count | everything numeric above |
| Audit | everything | — (audit never feeds runtime choice) |

Enforced structurally by call signatures and asserted by tests.

## F. Disturbance construction

`u_ext = S xi` with `1^T u_ext = 0` exactly. Concretely the forcing stream
draws an ordered distinct cell pair `(p,q)` and a magnitude `s` from a
declared finite rational set, giving `u_ext = s (e_p - e_q)`. Mass is
conserved exactly by construction. Forcing is applied to `x` only; it never
credits any `B_i`. Stage A applies exactly one shock at `t=0` and then
`u_ext = 0` for all `t > 0`.

## G. Comparison-arm pairing

Arm A: EBU affordability filter + uniform random actor.
Arm B: physical feasibility only + uniform random actor (the matched
physical-random scientific control, not an inferior controller).

Both arms share `forcing_seed` and `actor_seed` and the identical physical
layer, menu construction, feasibility rule and canonical ordering. Because
Stage A forces only at `t=0` from an identical initial state `x*`, the
applied shock is provably identical in both arms — this is common applied
forcing, not merely common raw draws, and the distinction the reconciliation
warns about does not bite for Stage A. Under Stage B's continuous forcing it
would, and the packet does not promise it there.

Actor streams are counter-addressed, so each arm's draw sequence is
independently reproducible even though realized affordable sets and chosen
actions differ between arms.

## H. Numeric representation and tolerance

**Author-ratified as the G0 Exact Arithmetic Decision.** The Stage-A
conformance world uses rationally representable state values, equilibrium
references, Gaussian scales, transfer quantities, forcing amplitudes,
capacities and ledgers. Quadratic potential values, marginals, finite EBU,
simultaneous-group EBU and common-path receipts are therefore evaluated
exactly. Foundation invariants use exact equality, not floating tolerances.
Floating-point tolerance is reserved for later empirical statistics or model
extensions that genuinely require approximate numerics.

**Exact rational arithmetic** (`fractions.Fraction`) is the frozen policy.
All configuration inputs (`x0`, `x*`, `sigma`, quanta, magnitudes) are
rationals. `V`, `mu`, `E`, `R_a`, `B`, `J` are then exactly representable,
because the model is a rational function of rational inputs.

- dtype: `fractions.Fraction` (arbitrary-precision exact)
- comparison tolerance: **0** (exact equality)
- invariant tolerance: **0**
- integration tolerance: **0**

Integration is exact rather than approximate: for quadratic `V`, `grad V`
along `x(s) = z + s delta_G` is affine in `s`, so the integrand
`-grad V(x(s))^T delta_a` is affine in `s` and the trapezoid, midpoint,
Simpson and composite rules all return the exact integral in rational
arithmetic. Numerical path closure is therefore an exact identity, and
reported residuals are exact zeros rather than small floats.

Floating point has no role in the Stage-A conformance world. A float64
shadow may be computed for presentation only and never participates in
feasibility, affordability, selection or any invariant decision. Approximate
numerics are reserved for later empirical statistics or model extensions that
genuinely require them.

Inputs are validated rather than coerced: `numerics.exact` refuses a `float`
outright instead of converting it, because a binary64 literal such as `0.1` is
not the decimal the author wrote and adopting the binary value silently would
make an exact identity depend on representation error.

## I. No-action and deadlock semantics

The empty group is always physically feasible, has `E = 0` and no receipts,
and is always affordable. To keep that from making deadlock unobservable and
from injecting an arbitrary menu-size-dependent do-nothing mass into the
process, the frozen rule is:

- the uniform sampling menu contains only **non-empty** candidates;
- if the non-empty affordable set is empty, the tick executes the empty
  group (state, balances and audit unchanged) and records status
  `DEADLOCK` when `V > 0`, or `IDLE` when `V = 0`;
- no fallback restorative action is ever invoked.

Recorded alternative, not adopted: including the empty group in the uniform
menu. It changes the stochastic process, so it is flagged in the
preregistration as a declared choice for author confirmation at the G3
freeze. It does not block implementation.

`DEADLOCK` is a scientific dynamical status, never a software failure.

## J. Exact reproducibility protocol

Two mandatory independent streams, `forcing` and `actor`, with separate
seeds, implemented as a **stateless counter-hash sampler** adopting the
Stage E arithmetic (`stage_e_harness/rng.py` at `a4af44a`) under a new
Gaussian rule id `EBU-GAUSSIAN-RNG-v1`. Stage E's module is not modified,
imported or re-executed; only its exact-residue design is adopted.

Statelessness is the mechanism that satisfies "no shared mutable RNG": a
draw is a pure function of
`(study_id, configuration_id, seed, stream_id, tick, event_index,
draw_index, attempt_index)`. The forcing stream cannot observe `B`, `E`,
`V` or the actor stream because it is a hash of its own coordinates only.

Replay: a run is fully determined by configuration plus the two seeds, so
re-running yields a byte-identical event log. Logs carry every field in task
§34, per event rather than as aggregate summaries.

## Classification of failures

Software failure (exception, nondeterminism, schema break, replay break),
mathematical conformance failure (finite/analytic mismatch, receipt
mismatch, accounting residual), physical failure (conservation or
feasibility violation) and affordability failure (negative executed
capacity) are defects. Non-recovery, cycling, plateau, deadlock and
instability are **scientific dynamical results**, not defects, and no test
asserts recovery.

## Open items deliberately left to the G3 freeze

1. Empty-group menu membership (decision I alternative).
2. Stage-A parameter values: cell count, `sigma`, quanta, `m_max`, shock
   magnitude, horizon, replicate count, seeds.
3. Registered metrics, falsifiers and acceptance criteria.

None blocks building the environment; all are outcome-blind and must be
frozen before any Stage-A run.
