# Stage-A registered preregistration (FROZEN except seeds)

Protocol id: `EBU-STAGE-A-V1`
Status: **FROZEN.** Every scientific decision below is fixed. The only item
deliberately left unmaterialized is the concrete seed values, which are derived
mechanically from this document's own commit SHA (section 12).

Superseded candidate: `LOCAL_GAUSSIAN_EBU_STAGE_A_PREREGISTRATION_CANDIDATE.md`
is retained as the review draft. Where the two differ, this document governs.

After this commit exists, no frozen decision here is edited in place. A
correction requires an explicit amendment document, a new preregistration
identity, and retention of this record.

## 1. Question and hypothesis

After one conservative external disturbance, with forcing then OFF, does the
EBU capacity-affordability constraint change post-shock deviation dynamics
relative to a matched physical-random control?

EBU calculates; actors choose. This measures a dynamical consequence of an
accounting constraint, not the performance of a controller.

## 2. Frozen physical model

| Item | Frozen value |
|---|---|
| Potential family | `EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1`, `V_i = 1/2((x_i-x*_i)/sigma_i)^2` |
| Cells `n` | 3 |
| Reference `x*` | (10, 10, 10) exact |
| Scales `sigma` | (1, 1, 1) exact |
| Declared mass `M` | 30 exact |
| Initial state `x_0` | `x*`, so `V_0 = 0`, `B_i(0) = 0`, `J_0 = 0` |
| Topology | complete directed graph, 6 edges |
| Action quantum set | {1} exact |
| Max group size `m_max` | 2 |
| Candidate groups | 21 (6 singletons, 15 pairs), exhaustive deterministic |
| Upper bound | none; the fixed-mass simplex already bounds the state |
| Process burden `C_G` | 0 (lossless first model) |

These are the parameters of the reviewed candidate, carried over unchanged.
They were selected on minimality grounds before any trajectory was observed and
have **not** been adjusted since (see section 13).

## 3. Frozen action, ownership and capacity rules

- Atomic action: transfer quantum `q` along a declared edge,
  `delta_a = q(e_dst - e_src)`; exactly mass-conserving.
- **Ownership**: `owner(a) = src(a)`. Exactly one owner per action, declared,
  never inferred from framework actor/provider reference fields.
- **Valuation**: `E_G = V(z) - V(z + delta_G)` from one frozen baseline `z`;
  receipts on the common path `x(s) = z + s delta_G`,
  `R_a = -mu(z)^T delta_a - 1/2 delta_a^T H delta_G`, with `sum_a R_a = E_G`.
- **Capacity**: `B_i >= 0`, zero genesis, same-event signed netting
  `Delta B_i = sum_{a: owner(a)=i} R_a`, affordable iff `B_i + Delta B_i >= 0`
  for every owner, atomic all-or-nothing settlement. No borrowing, issuance,
  refill, pooling or transfer.

## 4. Frozen event order

`EBU-GAUSSIAN-EVENT-PROFILE-v1`: external forcing, freeze pre-action state,
generate candidate groups, physical feasibility, exact EBU valuation, capacity
affordability, seeded random actor choice, exact execution, capacity
settlement, audit.

Feasibility is source-funded and decided before valuation, with no access to
EBU, capacity, global `V` or actor preference.

## 5. Frozen empty-group and deadlock semantics

The empty group is **not** a member of the actor's random-choice menu. Choice
is among nonempty physically feasible affordable groups.

If there is no affordable nonempty group:

- no actor action executes;
- the tick is recorded explicitly;
- if `V > 0` the tick is classified `DEADLOCK`;
- if `V = 0` the tick is classified `IDLE` (equilibrium quiescence), which is
  explicitly **not** deadlock-away-from-equilibrium.

No fallback action is ever injected. An always-affordable empty candidate would
convert genuine absence of affordable physical response into an ordinary random
choice and would obscure the deadlock phenomenon Stage A exists to measure.

The shock tick carries status `FORCING_ONLY` and is excluded from deadlock
counts: the actor is never invited to choose there.

## 6. Frozen external shock

Exactly one conservative disturbance per replicate, at tick 0, drawn from the
forcing stream only:

- edge index: uniform over the 6 canonically sorted edges, draw index 0;
- magnitude: uniform over the frozen alphabet {2}, draw index 1;
- `u_0 = s(e_p - e_q)`, hence `1^T u_0 = 0` exactly.

The generator never inspects EBU, capacity, actor RNG or expected ease of
recovery. After tick 0, `u_t = 0` for all `t >= 1`.

`D_r = V(z_0)`. **A zero-deviation shock is impossible under this frozen
generator**: from `x_0 = x*` with `s = 2` and `p != q`,
`D_r = 1/2(s^2/sigma_p^2 + s^2/sigma_q^2) = 4 > 0` for every edge. No
resampling or rejection rule is therefore required. The runtime asserts
`D_r > 0` and fails closed if it is ever violated.

Because the world is symmetric, `D_r = 4` exactly for every replicate. This is
a recorded limitation: the registered design varies the shock *address* across
replicates but not its magnitude.

## 7. Frozen arms

- **Arm A** `ebu_affordability_random_actor`.
- **Arm B** `physical_feasibility_random_actor`, the matched control, which
  removes **only** the EBU-capacity affordability gate.

Arm B retains identical candidate generation, group semantics, physical
feasibility, random choice, execution, conservation and the same shock. It
records a signed shadow ledger for measurement only and never filters on it.
Arm B is a scientific control, not an inferior controller.

Both arms use the matched forcing seed and matched actor seed of their
replicate.

## 8. Frozen sample size and horizon

- Replicates: **N = 128** paired.
- Horizon: **H = 256** post-shock actor ticks, `t = 1..256`.
- Tick 0 is the external shock event and is forcing-only.
- Total ticks per run: 257.

No early stopping for any reason: not on reaching equilibrium, not on a
trajectory looking bad, not on significance being reached, not on significance
appearing impossible. `N` and `H` are not changed after any result is seen.

## 9. Frozen exact invariants

Every post-shock tick of every EBU-arm replicate must satisfy, at exact
equality with **zero tolerance**:

1. `V_r(t) + sum_i B_{i,r}(t) = D_r`
2. `sum_i x_i(t) = M`
3. `x_i(t) >= 0`
4. `sum_a R_a = E_G` for the executed group
5. `B_i(t) >= 0`

Both arms must satisfy 2, 3 and 4. Arm B's shadow ledger satisfies the
analogue of 1 but not 5, by design.

Any nonzero residual is a **foundation/software failure**, not a scientific
finding, and halts interpretation.

## 10. Frozen primary endpoint and test

Normalized cumulative deviation, per arm per replicate:

    A_r = (1 / (H * D_r)) * sum_{t=1}^{H} V_r(t)

computed exactly as a rational. Both arms of a pair use the same `D_r`.

Primary paired contrast: `Delta_r = A_r^EBU - A_r^CTRL`. Negative means lower
cumulative deviation under EBU affordability.

**Primary confirmatory test: exact two-sided paired sign test** on the nonzero
`Delta_r`.

- Null: `P(Delta_r < 0) = P(Delta_r > 0) = 1/2` conditional on non-tied pairs.
- Alternative: two-sided. This is not changed to one-sided after seeing
  direction.
- `alpha = 0.05`, frozen.
- Ties (`Delta_r = 0`) are reported and omitted from the sign-test denominator
  per the standard exact definition.
- The p-value is computed exactly from integer binomial counts, not normal
  approximation.

Reported: counts negative, positive and tied; exact p-value; median and mean
paired difference; and the full distribution of paired differences.

Statistical significance alone is not sufficient for a broad EBU claim. Effect
magnitude and trajectory diagnostics must accompany it.

## 11. Frozen secondary diagnostics — descriptive only

No independent significance claim is attached to any of these. No multiplicity
correction is performed because no confirmatory inference is drawn from them.

First equilibrium-hitting time `T_0 = inf{t : V(t) = 0}`, censored at `H+1` if
never reached; equilibrium occupancy `O_0 = (1/H) sum_t 1[V(t)=0]`; terminal
normalized deviation `V(H)/D_r`; minimum normalized deviation
`min_t V(t)/D_r`; deadlock count; first deadlock time; counts of executed
events with positive and with negative `E_G`; capacity trajectory and total;
equilibrium departures after previously reaching `V=0`; and repeated
restoration-destruction cycle counts.

### Frozen trajectory classification

Deterministic, evaluated in this order on `V(1..H)`; first match wins. A
*departure* is a `t` in `1..H-1` with `V(t) = 0` and `V(t+1) > 0`.

1. `DEADLOCKED_AWAY_FROM_EQUILIBRIUM` — `V(H) > 0` and ticks `H-7..H` are all `DEADLOCK`.
2. `REACHED_AND_STAYED` — some `V(t) = 0` and `V(u) = 0` for all `u` from the first such `t` to `H`.
3. `REPEATED_CYCLING` — departures >= 4.
4. `REACHED_AND_LEFT` — 1 <= departures <= 3.
5. `PARTIAL_RECOVERY` — `V(t) > 0` for all `t` and `V(H) < D_r`.
6. `NEVER_REACHED_EQUILIBRIUM` — `V(t) > 0` for all `t` and `V(H) >= D_r`.
7. `OTHER_REGISTERED_PATTERN` — fallback; should never fire and is reported if it does.

No trajectory is classified by hand after inspection.

## 12. Frozen seed-derivation rule (materialized only after this commit)

Seeds are **not** manually selected. For replicate `r = 0..127` and stream name
`S` in {`FORCING`, `ACTOR`}, the seed is the first 8 bytes, big-endian
unsigned, of

    SHA256( ASCII( "EBU-STAGE-A-V1" | C_pre | rrr | S ) )

where:

- `|` is the single ASCII byte `0x7C` used as an unambiguous separator;
- `C_pre` is the full 40-character lowercase hex SHA-1 of **this document's
  preregistration commit**;
- `rrr` is the replicate index in decimal, zero-padded to exactly 3 digits;
- `S` is the literal uppercase stream name;
- the whole preimage is encoded ASCII with no trailing newline.

Example preimage: `EBU-STAGE-A-V1|<C_pre>|000|FORCING`.

The same derived pair is used for both arms of a replicate.

The seed manifest is materialized only after this commit is immutable and is
committed separately. Seeds are never regenerated because results look
surprising. **If a derived seed coincides with a seed exposed during
conformance, it is kept.** There is no result-dependent seed exclusion.

## 13. Prior exploratory conformance exposure

**Disclosed, not hidden.** Before registration, the harness was run for
software conformance on this same 3-cell world at these `(forcing_seed,
actor_seed)` pairs, for at most 8 ticks each:

    (11, 29)   (11, 30)   (11, 31)   (3, 7)

Purpose: software conformance only. Model parameters were selected on
minimality grounds beforehand and were **not** subsequently tuned to those
outcomes. These short trajectories are **not confirmatory evidence** and are
not part of the registered study.

Official registered seeds are generated mechanically from `C_pre` by section
12 and are **not** manually selected either to include or to avoid these
pairs.

## 14. Frozen failure handling, exclusion and stopping policy

- **Exclusion policy: none on scientific grounds.** No replicate is dropped
  because of its outcome.
- A foundation-integrity failure (nonzero exact residual, negative EBU-arm
  capacity, missing or duplicate replicate, code or configuration identity
  mismatch, replay mismatch, unregistered fallback) invalidates the **study**,
  halts scientific interpretation, and is preserved as incident evidence.
- **Stopping policy**: run all 128 replicates over the full 256-tick horizon.
  No interim inspection informs later replicates.

## 15. Structural bound is not a result

In the EBU arm, `V + sum B = D` with `B >= 0` implies `V <= D`, hence
`0 <= A_r^EBU <= 1`. This is an exact structural property of the accepted
accounting and affordability model. It does **not** establish convergence,
return to zero, damping, stationarity or superiority to control, and is
reported separately from observed dynamics. The control arm carries no such
bound. Both arms live on a bounded fixed-mass simplex, so no claim of the form
"EBU keeps the system bounded" may be drawn.

## 16. Frozen code and configuration identity

- `gaussian_harness` code identity at registration:
  `a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55`
  (SHA-256 over the package's sorted `*.py` names and bytes).
- Configuration identity: SHA-256 over a canonical JSON serialization of the
  section 2 and 3 parameters, materialized with the seed manifest.
- Analysis implementation is frozen before execution and lives outside
  `gaussian_harness`, so freezing it does not perturb the code identity above.

Execution requires the code identity to match this value exactly.

## 17. Non-claims

Whatever this study shows, it does not establish that EBU is stable, that the
capacity rule is correct causal or ethical attribution, that the common-path
receipt is a fair share, that the reference is an optimum, or that any real
economy behaves this way. It concerns one synthetic three-cell lossless world,
one shock magnitude, one potential and one action menu.

A negative or null Stage-A result is not permission to change the mechanism and
does not authorize Stage B.
