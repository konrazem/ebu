# Stage-B scientific disposition

Classifies what the registered Stage-B study established. It changes no model,
no code and no manuscript.

Sources: `STAGE_B_REGISTERED_REPORT.md`, preregistration
`4c826a9be4c6306fa57698eb23c1076ebf75b970`, artifacts commit `5391518e`.

## 1. What is now established

### 1.1 Foundation (highest confidence)

The mechanism is exactly implementable and exactly auditable under sustained
drive. `V_t + sum_i B_i(t) = J_t` and `sum_i x_i = 30` held as literal rational
equalities in **all 1,048,576** executed ticks across both arms, with zero
tolerance anywhere. Full-horizon replay is byte-identical. This is now
established over two independent registered studies at the same code identity.

### 1.2 Scientific: the constraint binds, but transiently

Under continuous conservative forcing the EBU affordability gate produced lower
time-averaged physical deviation than the matched physical-random control in
64/64 replicates, on a normalization that is bounded in both arms and cannot
force the ordering. Median effect 5.6 percentage points of the physically
available deviation range.

That effect **decays within the study**: -0.0747, -0.0484, -0.0448 across the
three 2048-tick blocks, falling below the preregistered practical threshold of
0.05 in the final two.

### 1.3 The central finding: the mechanism self-attenuates

The registered falsification target of section 2 of the preregistration is
**confirmed**. Three diagnostics move together and in the predicted direction:

| Diagnostic | Block 1 | Block 2 | Block 3 |
|---|---|---|---|
| Median paired difference | -0.0747 | -0.0484 | -0.0448 |
| EBU `rho_reject` | 0.0662 | 0.0497 | 0.0332 |
| EBU ending `B_tot` | 2997 | 4254 | 5400 |

The cause was derived before execution and is structural rather than
incidental: for the quadratic potential,
`D_ext = mu^T u + (1/2) u^T H u`, and with `q0 = 1`, `sigma = 1` the curvature
term is exactly `+1` on every applied forcing event. So `J` has positive
secular drift by construction. Physical conservation bounds `V` by
`V_max = 300`. Therefore the drift must accumulate in `sum_i B_i`, and it does:
median terminal capacity 5400 against a deviation ceiling of 300.

As capacity accumulates, fewer candidate groups are refused, and the
constrained arm drifts toward the unconstrained one.

**This is a property of the accepted mechanism, not a defect and not a software
failure.** It is the kind of finding Stage B existed to discover.

## 2. What is NOT established

- **Not** that EBU is stable, convergent or damping. It is not, in either study.
- **Not** that the arm difference reaches zero. It is still clearly negative in
  block 3 (61/64 replicates). The horizon does not reach a limit and no
  extrapolation is registered.
- **Not** a stationary joint process. The EBU arm's physical marginal was still
  drifting (`NO EVIDENCE OF LATE-WINDOW STATIONARITY`), and the accounts are
  plainly nonstationary in both arms.
- **Not** anything about deadlock frequency: zero deadlock ticks in both studies.
- **Not** anything about forcing-intensity dependence: one fixed amplitude by
  design.
- **Not** generalizable beyond one synthetic 3-cell lossless world with one
  potential, quantum 1 and `m_max = 2`.

## 3. Relationship to Stage A

Stage A and Stage B agree on the foundation and disagree usefully on what the
dynamics look like, because they asked different questions.

| | Stage A (single shock) | Stage B (continuous forcing) |
|---|---|---|
| Regime | transient | recurrent, still drifting |
| EBU dynamics | perpetual cycling, never settled | lower deviation level, same relaxation timescale as control |
| Primary test | structurally forced, near-uninformative | not forced; ranges overlap |
| Capacity | bounded by `D = 4` | unbounded secular growth to 5400 |
| Deadlock | none | none |

Stage A's design fault was corrected and the correction worked: Stage B's
primary comparison carries real information, and it is the *effect magnitude
and its decay* that matter, not the p-value.

## 4. Disposition

**GATE: foundation integrity — PASS.**

**GATE: scientific dynamical result — the mechanism binds transiently and
self-attenuates under sustained drive.**

**GATE: model change requirement — NO model change is authorized.**

Nothing observed contradicts the frozen model. Every exact invariant held. The
capacity growth is a consequence of the declared potential, the declared
forcing law and the declared accounting identity acting together, all of which
were accepted before execution.

A finding that a mechanism has a property one might not want is **evidence
about that mechanism**, not permission to replace it mid-programme. Per section
20 of the controlling protocol and section 18 of the preregistration, no
capacity decay, expiry, cap, demurrage, taxation, pooling or borrowing has been
added, and none may be retrofitted into Stage A or Stage B.

## 5. What this motivates

The secular-capacity result is a well-identified scientific motivation for a
**separately authorized** comparative study of alternative capacity
formulations. Those alternatives would constitute a **new model**, not a patch.

They are enumerated, with their stated risks and the falsifiable questions each
raises, in `NEXT_STUDY_MECHANISM_ALTERNATIVES_PACKET.md`. That document
implements nothing and authorizes nothing.

An honest framing for any such study: the present mechanism's constraint decays
because the accounting identity converts curvature-driven potential injection
into permanent spendable capacity. Any candidate alternative must be evaluated
on whether it changes that, at what cost to the exactness and auditability that
both registered studies have now demonstrated twice over.
