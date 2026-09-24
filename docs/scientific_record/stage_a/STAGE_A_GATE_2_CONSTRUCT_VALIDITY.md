Audit complete. All work was read-only against the published export; the repository was not touched.

## GATE 2 — Construct validity

Coordinate re-verified: commit `2c4b71d1…`, tree `5afe3978…`, preregistration `a74d8380…`.

### Construct map

| | **A1 — pure P-restoration** | **A2 — isolated E-demand** | **A3 — E → consequence → restoration** |
|---|---|---|---|
| **Intended construct** | disturbance → endogenous P-demand → local restoration | EBU affordability/refusal at zero reserve | earned capacity → E-demand → displacement → induced P-demand → restoration |
| **Manipulated** | policy arm only | policy arm only | policy arm only |
| **Held constant** | `x₀=(1,7,4)`, quiet disturbance, zero arrivals (verified 0 across 2,618 epochs), horizon 32 | `x₀=x*`, one identical order (1 distinct payload / 256), horizon 1 | `x₀=(1,7,4)`, one identical order at epoch 3 (1 payload, epoch set `{3}`), horizon 32 |
| **Confounds considered** | one-shot restoration, endpoint saturation, E-contamination, post-recovery motion, menu artifacts, genesis/refill, unrelated actions | restoration, selection quality, long-run performance | endogenous prelude, arrival timing, assumed capacity, pre-scripted restoration |
| **Supported** | whether/how each arm returns, per episode | whether the gate binds at zero reserve, and that refusal ≠ impossibility ≠ absence | whether the deficits tracked at `x_{s+1}` close within the horizon |
| **Unsupported** | restoration in general or with any probability | any quality, ordering or long-run claim | equilibrium return; sustained restoration; absence of new deficits |
| **Disposition** | **VALID** | **VALID** | **VALID, with two declared interpretive constraints** |

### Findings

**A1 is clean and nontrivial.** Deficit 3 > max quantum 2, and neither opening plan reaches `x*` — `B->A@1 → (2,6,4)` and `B->A@2 → (3,5,4)`, EBU 5 and 8, exactly as preregistered — so ≥2 transitions are forced by construction. Amplitude 3 ∉ quanta `{1,2}`, avoiding the endpoint-saturation hypothesis, declared in advance for that reason. Both opening plans are affordable at zero balance, so A1 cannot stall at epoch 0. No arrivals, no external displacement, exact conservation (no genesis/refill), irredundancy blocks unrelated actions, 0 episodes acted after reaching `x*`. **No exact confound found.**

**A2 measures exactly one thing.** Pre-filter menu is 2 plans in all four arms; `affordable_count` is 2 for the control and 0 for the three EBU arms. The contrast is therefore clean — identical order, identical menu, identical physics, the gate as the only difference. It **can** support "does the affordability gate bind at zero reserve, and is refusal distinguished from impossibility and absence." It **cannot** support anything about restoration, selection quality or long-run performance, and its one-epoch horizon means the consequence of the control's negative balance is unobservable by construction.

**Fairness is structural, not conventional.** The RNG is counter-addressed — every draw is a pure function of `(model_id, world_id, seed, stream, epoch, event, draw, attempt)` — and policy appears in no address, so a policy cannot perturb the disturbance, arrival or admission streams. Menu enumeration happens before any policy branch; the single branch is `if entry.applies_affordability`. Search bound is `len(live_routes)`, state-only. `plans.py`, `enumeration.py`, `demand.py` and `service.py` contain no policy reference at all. Random and control are passed `None` for EBU values and *raise* if given them.

**Strong atomic P is coherent, with a decisive witness.** Provenance and valuation stay separate: state `(4,3,5) → (2,5,5)`, `V` rises 1→3, **EBU = −2**, yet provenance is valid (`P:r|B`, deficit 1, delivered 2, progress 1, overshoot 1). Attribution is capped at `min(delivered, deficit)`; legality is not. Side effects are fully valued (EBU = `V(pre)−V(post)` at all 11,066 epochs, Gate 1). Irredundancy is served-set dominance over *every* proper subset, so no unrelated-action leakage. No residual-demand object exists in the package. **No counterexample found.**

**§7 — the one undocumented consequence.** Duplicate plan *identities* are deduped and the code flags the risk explicitly. But distinct identities can share a post-state: `g:[A->B@2, B->C@1]` and `g:[A->B@2, B->C@2, C->B@1]` both land on `(3,4,5)` with EBU 0, and neither is dominated by a proper subset, so both are legitimately in the menu. **82 of 256** A3 arrival menus have shape *4 plans → 3 outcomes*, weighting the repeated outcome **1/2** instead of 1/3. A1 has **0 of 11**; A2 none. Aligned and hostile are outcome-invariant (duplicates necessarily share EBU, so an extremum set containing both maps to one post-state); only the two uniform samplers are exposed — 9 control and 9 `ebu_random` episodes. **Classification: acceptable nuisance, not a fatal confound** — the sampling universe is preregistered as plans, and Stage A declares no test. It is not documented anywhere and must be before any Stage-B comparison involving the uniform arms.

**L/R/P is preserved explicitly.** The execution report states the 91/91 result "is a statement about reachability, **not** about recovery, affordability or policy behaviour," and separates guarantees from observations from post-execution clarification.

**Outcome-blindness holds.** All four attempts carry the freeze-3 identity, so both preregistration corrections predate any registered epoch. The two runner corrections were forced by internal contradictions — a predicate unattainable by construction, and a column that marked the executed plan unaffordable inside the record executing it — both demonstrable without reference to any outcome, and the attempt 3→4 change left every epoch record identical.

---

# GATE 2 CONDITIONAL PASS

**Precise limitations**, all interpretive, none a construct defect:

1. **Plan-identity multiplicity (undocumented).** For the two uniform-sampling arms, uniform-over-plans is not uniform-over-physical-outcomes in 82 of 256 A3 arrival menus (repeated outcome weighted 1/2 vs 1/3). Outcome-invariant for aligned and hostile. Must be declared before any Stage-B comparison involving the uniform arms.
2. **A3's baseline is endogenous (declared).** The prelude is whatever the arm does, so `arrival_baseline` (5 distinct) and `prelude_reserve` (4 distinct) are policy-dependent. A3 is a **per-arm chain demonstration, not a common-baseline comparison**, and no cross-arm reading may treat epoch 3 as a controlled starting point.
3. **`RESTORATION_COMPLETED` is construct-narrow (disclosed).** It means simultaneous closure of the deficits tracked at `x_{s+1}` — not equilibrium return, not sustained closure, not absence of newly created deficits — and closure is horizon-censored. The frozen definition is correct; the word invites a broader reading, so Gate 3 must carry the definition with the label.

The three Gate-1 qualifications were re-examined and none creates a construct problem: the decomposition-gate exception touches only inert no-demand epochs at `x*` and cannot alter a trajectory; the two reporting items are recoverable and were independently verified.

**READY FOR SCIENTIFIC GATE 3 — PREREGISTERED RESULTS EXTRACTION**

Gate 3 not begun. No arm was ranked, no final outcomes compared, and no Dynamic EBU theory applied.