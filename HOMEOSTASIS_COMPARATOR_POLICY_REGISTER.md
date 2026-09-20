# Comparator policy register for the homeostasis mission

**Status: audit of comparators that already exist in this repository.** Mission
section 17 is explicit that no comparator heuristic may be invented from
memory, so every entry below cites a committed source. Nothing here is adopted;
classification is a recommendation for the author.

The four core arms of mission section 7 remain mandatory and are not optional
alternatives to anything in this register.

Classification vocabulary (mission section 17): **CORE CONFIRMATORY**,
**SECONDARY BENCHMARK**, **HISTORICAL ONLY**, **SUPERSEDED**, **INVALID FOR
CURRENT QUESTION**.

---

## 1. Summary

| # | Policy | Authority | Uses EBU/V? | Hidden homeostatic intelligence? | Class |
|---|---|---|---|---|---|
| 1 | `physical_feasibility_random_actor` | `gaussian_harness.harness`, registered Stage A/B | no | no | **CORE CONFIRMATORY** |
| 2 | `ebu_affordability_random_actor` | `gaussian_harness.harness`, registered Stage A/B | affordability only | no | **CORE CONFIRMATORY** |
| 3 | Arm B, `B_restricted_matched_non_ebu` | `longhorizon_v30`, DECLARED, not adopted | no (uses force `f_e`) | **yes — it is a gradient rule** | **INVALID FOR CURRENT QUESTION** (degenerate here) |
| 4 | Arm S, `S_restricted_local_service_priority` | `longhorizon_v30`, DECLARED, not adopted | no | no | **INVALID FOR CURRENT QUESTION** (undefined on this world) |
| 5 | Arm D, `D_restricted_exact_total_quote_greedy` | `longhorizon_v30`, DERIVED, not adopted | yes | yes, by construction | **SUPERSEDED** by core arm A |
| 6 | Arm A, `A_full_multi_edge_p1c` / `A_full_p1c` | `longhorizon_v30`, `service_v30` | no | yes | **HISTORICAL ONLY** |
| 7 | `B_restricted_p1c`, `C_restricted_p1c_quote`, `D_restricted_quote_greedy` | `service_v30.ARMS` | mixed | yes | **HISTORICAL ONLY** |
| 8 | C0 | `ebu_candidate_controllers`, `CANDIDATE_UNAPPROVED` | no | no | **INVALID FOR CURRENT QUESTION** (it is abstention) |
| 9 | C1, C2 | `ebu_candidate_controllers`, `CANDIDATE_UNAPPROVED` | no | partly | **INVALID FOR CURRENT QUESTION** (needs demand) |
| 10 | C3 | `ebu_candidate_controllers`, `CANDIDATE_UNAPPROVED` | no | **yes — explicitly** | **INVALID FOR CURRENT QUESTION** (needs bands/reserves) |
| 11 | C4 | `ebu_candidate_controllers`, `CANDIDATE_UNAPPROVED` | no (uses `mu`, `f_e`) | yes | **INVALID FOR CURRENT QUESTION** (hinge potential) |

**Net result: no existing comparator is added to the core study.** Entry 3 is
the only one that was a serious candidate, and section 3 below shows it is
mathematically degenerate in the registered world.

---

## 2. Entries

### 1. `physical_feasibility_random_actor` — CORE CONFIRMATORY

- **Authority:** `gaussian_harness/harness.py`, `ARM_CONTROL`; registered and
  executed in Stage A (`STAGE_A_PREREGISTRATION.md`) and Stage B.
- **Information access:** physical state, topology, menu. No EBU, no potential,
  no balance reaches its chooser — `uniform_index` receives a count.
- **Choice rule:** uniform over physically feasible groups; no affordability
  filter.
- **Uses EBU/V:** no. EBU is computed for measurement and cannot reach the
  choice.
- **Hidden homeostatic intelligence:** none. This is the baseline.
- **Valid:** yes. It is mission arm C, unchanged.

### 2. `ebu_affordability_random_actor` — CORE CONFIRMATORY

- **Authority:** `gaussian_harness/harness.py`, `ARM_EBU`; registered Stage A/B.
- **Information access:** as above, plus the affordability projection of owned
  receipts against balances.
- **Choice rule:** uniform over *affordable* feasible groups.
- **Uses EBU/V:** affordability only; the chooser still receives only a count.
- **Hidden homeostatic intelligence:** none.
- **Valid:** yes. It is mission arm R, unchanged. The conformance suite asserts
  the new harness reproduces it tick for tick.

### 3. Arm B, matched non-EBU comparator — INVALID FOR CURRENT QUESTION

- **Authority:** `longhorizon_v30.PROSPECTIVE_ARMS` / `DECLARED_SET_SCORES` and
  `V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md` section 13a. Marked
  **DECLARED, not derived**, in a document that still reads **PROPOSED, NOT
  ADOPTED**; `service_v30.DERIVED_SEMANTICS["arm_B_selection"]` carries the
  one-action form.
- **Information access:** local marginals `mu` at both endpoints, the loss
  factor `eta`, edge parameters, accepted quantities.
- **Choice rule:** rank by member force `f_e = mu_i - eta*mu_j`, descending
  lexicographic; accepted quantity is the next tie level.
- **Uses EBU/V:** no. It never evaluates a finite EBU or a quote.
- **Hidden homeostatic intelligence:** **yes, unambiguously.** `f_e` is the
  steepest-descent direction of the potential, so "largest force" is a gradient
  rule. The Stage-A controlling task forbade implementing a gradient-following
  controller; importing this arm would reintroduce one under another name. That
  alone does not disqualify it as an openly declared *benchmark* — but it
  disqualifies it as a *control*.

- **Why it is nevertheless invalid here — it is degenerate.** In the registered
  world this comparator cannot be distinguished from EBU-aligned. For a single
  transfer of `q` on edge `i -> j`,

  ```
  E_G = q f_e - (q^2/2)(1/sigma_i^2 + 1/sigma_j^2)
  ```

  With `sigma = (1,1,1)` and the single quantum `q = 1`, the curvature term is
  the constant `1` for **every** candidate, so `E_G = f_e - 1` identically and
  the two rankings coincide. Verified by enumeration: over all 496 admissible
  lattice states, `argmax` of exact EBU equals `argmax` of force on **496/496**.

  A comparator that provably selects what the treatment arm selects measures
  nothing. It would become informative only if the curvature term varied across
  candidates — that is, under **non-uniform `sigma`** or a **multi-valued
  quantum set**. Recorded as a concrete design option for a later study that
  wants to isolate the exact finite curvature term; not usable in this one.

### 4. Arm S, stock-blind service priority — INVALID FOR CURRENT QUESTION

- **Authority:** `longhorizon_v30.DECLARED_SET_SCORES`, DECLARED, not adopted.
- **Choice rule:** rank by total accepted delivered service to destinations
  with positive declared demand.
- **Why invalid:** the Gaussian conservative world has **no demand and no
  service**. Every destination has demand zero, so the score is identically
  zero and the rule degenerates to its tie-break, an edge-identifier ordering.
  It is not a policy here; it is a fixed permutation. Reinstating it would
  require adding a demand model, which is a different study.

### 5. Arm D, exact-EBU greedy — SUPERSEDED

- **Authority:** `longhorizon_v30`, marked **DERIVED**; not adopted.
- **Choice rule:** highest strictly positive exact joint EBU, **otherwise
  rest**.
- **Why superseded:** the "otherwise rest" act condition is voluntary
  abstention, which mission section 6 forbids outright. Mission arm A is the
  same selection rule with mandatory action substituted for the rest branch,
  and is its valid successor. Note also `longhorizon_v30.OPEN_LAUNCH_GATES`:
  the multi-action settlement form is unresolved there and blocks execution;
  the Gaussian programme resolved it separately with common-path receipts.

### 6–7. P1C arms — HISTORICAL ONLY

- **Authority:** `service_v30.ARMS`, `longhorizon_v30.ARM_ROLES`; historical
  Gate-1D work.
- **Why historical:** all are bound to the threshold/hinge D0 potential, the
  P1C resolver, reserves, bands, demand and a service model. None is defined on
  the Local Gaussian conservative world. They retain their own authority and
  results and are neither superseded nor reusable here.

### 8. C0 — INVALID FOR CURRENT QUESTION

- **Authority:** `ebu_candidate_controllers.c0_candidate_proposal`,
  `CANDIDATE_UNAPPROVED`.
- **Choice rule:** *"propose zero on every out-edge, unconditionally."*
- **Why invalid:** this is exactly the abstention mission section 6 prohibits.
  Including it would answer the mission's central question by construction: a
  policy that never acts trivially preserves whatever state it starts in.

### 9. C1, C2 — INVALID FOR CURRENT QUESTION

- **Choice rule:** C1 splits the source stock equally across out-edges with
  positive demand, capped by demand; C2 asks for the whole opportunity and
  scales proportionally.
- **Why invalid:** both read `demand_here` and `edge_caps`, neither of which
  exists in this world. With demand identically zero C1 proposes nothing — a
  second abstention — and C2 reduces to a fixed proportional split.

### 10. C3 — INVALID FOR CURRENT QUESTION

- **Choice rule:** three-stage lexicographic control serving destination
  reserve deficits, then lower-band deficits, then ordinary demand.
- **Hidden homeostatic intelligence:** **explicit, not hidden.** It is a
  homeostatic band-and-reserve controller by design.
- **Why invalid:** requires per-node `L`, `U`, `R` bands and demand. The
  Gaussian world declares a reference and a scale, not bands. Its own
  `P1C_BINDING_ANALYSIS` also records that its stage ordering is only a
  proposal-level priority that the stage-blind resolver may not honour.

### 11. C4 — INVALID FOR CURRENT QUESTION

- **Choice rule:** the committed local law — `f_e = mu_i - eta mu_j`, flux
  `J_e = M_e [f_e - theta_e]_+`, quantity `dt J_e`, clipped and renormalised.
- **Why invalid as written:** it calls `d0_v29.marginal` with `alpha, beta,
  chi, L, U, R, K`, i.e. the hinge potential. It is not defined on the Gaussian
  field.
- **Note:** re-expressed on the Gaussian potential it collapses onto entry 3
  and inherits the same degeneracy.

---

## 3. Recommendation

1. **Run the core four arms only.** No existing comparator survives the audit
   as a usable addition, and mission section 17 warns against letting
   comparator proliferation delay the core study.
2. **Record entry 3's degeneracy as a design lever, not a loss.** That
   `argmax E_G = argmax f_e` on 496/496 states in this world is itself a
   finding: in an isotropic unit-quantum world the exact finite curvature term
   changes no decision. A later study wanting to isolate curvature should vary
   `sigma` or widen the quantum set, at which point arm B becomes a genuine
   non-EBU comparator rather than a relabelling of arm A.
3. **Do not resurrect C0 or arm D's rest branch under any framing.** Both are
   abstention, and mission section 6 makes the mandatory-action rule central to
   the interpretation.
4. If a secondary benchmark is wanted later, it must be added **after** the
   core design is frozen and must declare its information access and whether it
   embeds homeostatic intelligence, as every entry above does.
