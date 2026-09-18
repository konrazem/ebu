> **Current-scope notice — 18 September 2026.** Preserved review of an earlier prospective package. Its findings retain that scope; this is not acceptance or review of the new Gaussian programme.
>
> Current navigation: [CURRENT_SCIENTIFIC_AUTHORITY.md](CURRENT_SCIENTIFIC_AUTHORITY.md).
> The pre-existing body below is preserved unchanged from checkpoint `924a4d9`.

# Conservative World Adoption Package — Independent Review Record

**Status: REVIEW RECORD — an honest account of what was checked, what was
found, what was repaired, and what remains open. Not an adoption; not an
approval; not a scientific record; not an execution authorization.**

**No scientific execution occurred.** No model, world, tick, transition loop,
viability-kernel computation, trajectory, parameter search, benchmark, test
suite, runner, or simulation was executed by the author or by any review
stream. No SD-01, SD-03, Gate 1E, AWS, Docker, SSO, or publication action
occurred. The only computation performed was reading, static parsing, SHA-256
hashing, exact rational arithmetic, and binomial coefficients.

**Subject of review:** `CONSERVATIVE_WORLD_ADOPTION_PACKAGE_CANDIDATE.md`.
**Predecessor also reviewed:** `CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md`,
committed at `0726ccd`.

---

## 1. Review streams and their scope

Four bounded read-only streams were run, plus the author's own verification.
Each stream was instructed not to write, edit, stage, commit, or execute
anything, and none did.

| # | Stream | Scope | Outcome |
|---|---|---|---|
| 1 | **Authority auditor** | Every `file:line` citation, every quoted string, both hash claims, and eight status-boundary claims in the predecessor memo | 2 critical, 5 major, 7 minor findings; both hashes verified exactly; all eight status boundaries verified |
| 2 | **Mathematical reviewer** | 21 named checks on conservation, finite-state, update-order, viability, and information-pattern correctness in the candidate | 2 critical, 5 major, 9 minor findings; 13 of 21 checks sound |
| 3 | **EBU boundary reviewer** | 10 named checks that the candidate invents no EBU equation, unit, account, permission, settlement, or surrogate objective | 9 of 10 PASS; 1 critical, 2 major, 6 minor findings |
| 4 | **Critical editor** | 8 scans: overclaim vocabulary, hidden numerical selection, registration language, frozen/book authority, internal contradictions, whether the package decides anything, header self-consistency, inherited predecessor defects | 1 critical, 6 major, 7 minor findings; scans 1, 2, 3, 6 found nothing reportable |
| — | **Author verification** | Independent re-derivation of both critical mathematical findings and adjudication of every stream finding | 2 stream findings **rejected as incorrect** (§4) |

> **Findings were treated as evidence, not as instructions.** Two were rejected
> after direct verification against repository bytes. One stream's central
> mathematical claim was accepted only after the author reproduced the
> counterexample independently.

---

## 2. Material findings, and their disposition

### 2.1 Critical — repaired

| ID | Finding | Verified how | Disposition |
|---|---|---|---|
| **CR-1** | **The viability oracle was mathematically vacuous.** Every transition family had lower bound `0`, so a "do nothing" action was always available; with a state-only safe set `K`, the no-op's successor *is* the current state, so the stationary all-no-op policy keeps every `s ∈ K` in `K` forever. Hence `K⁺ ⊆ V_∞` and `V_∞ ⊆ V_0 = K⁺`, giving `V_∞ = K⁺` exactly, with the recursion stabilising at `k = 1`. The oracle would have certified every legal safe state, distinguished nothing, and been answerable by inspection without executing anything. Diagnostic category 1 would have coincided with `s ∉ K` and been unreachable from a legal start. All four failure mechanisms would have been elective. | Author re-derived the argument directly; it is a two-line consequence of the quantifier structure | **REPAIRED.** Consumption is now **mandatory** — an equality `u_a = min(d_a(t), buf_a)`, not a bound (§C.8, §C.8.1). The degeneracy result is stated explicitly in §C.8.1 so the reason the fix is necessary is on the record. §C.9 was rewritten: the no-op is no longer a state-preserving fallback. |
| **CR-2** | **Per-family feasibility caps do not compose.** Each cap is a unilateral bound read off the frozen pre-state; applied simultaneously they can produce an illegal successor. Two counterexamples built only from cap-satisfying components: a capacity breach (`acc_i' = 10 > κ_i = 5`) and a negativity breach (`acc_i' = −5`). In both, **`Q` is still exactly conserved**, so a check looking only at `ΔQ_B` reports clean while the state is illegal. The natural defensive reflex — clamping — creates or destroys exactly the excess tokens and is the one way this design can actually break conservation. | Author reproduced both counterexamples by exact static arithmetic | **REPAIRED.** §C.8.3 adds composed legality as a normative condition on the tuple, states that per-family caps are necessary but not sufficient, forbids clamping, requires the residual to be computed on the unclamped successor, and requires `min(q_{i→j}, q_{j→i}) = 0`. §D.1's pass/fail/refusal rows now test composed legality. |
| **CR-3** | **The ranking-invariance claim in the EBU gate was false.** The candidate asserted that "a ranking is invariant under any strictly increasing identification, so ordering survives". The ranked object is a *difference* of potentials minus a cost, not a level. Whether a monotone `φ` preserves order depends on **where `φ` is applied**, which SD-03 prerequisite **P5** leaves unregistered. This was the single sentence making an EBU step look partly reachable. | Author reproduced the reversal in exact rational arithmetic with `φ(x) = x³`: two actions ranked `1 ≻ 2` under identity and `2 ≻ 1` under `φ` | **REPAIRED.** F.3's `[R]` column changed from "partial" to **BLOCKS**. New §F.3a gives the counterexample, identifies the true invariance class (positive scaling applied uniformly to `V_loc` and `C_a`), and records that P5 leaves both the identification and its point of application open. §F.1a bullets corrected. |
| **CR-4** | **The status header contradicted the package's own §K and the repository state.** "No existing file was modified … the books register … and all code, tests … are unchanged" reads as a claim about repository state, which is false: five tracked paths carry pre-existing uncommitted user modifications. | `git status --short`, `git diff --stat` | **REPAIRED.** The header now says "No existing file was modified **by this package**", enumerates the pre-existing dirty paths, states none was made or touched here, and notes each was verified byte-identical. |

### 2.2 Major — repaired

| ID | Finding | Disposition |
|---|---|---|
| **MJ-1** | **World A was not autonomous.** Deleting actors removed only the draw and consumption components; mobilisation, recovery and transport amounts remained free, making World A a nondeterministic transition *relation*, not a map. "Every forward orbit is eventually periodic" and "the orbit's eventual period" were therefore not well-formed, and `Inv(K₀)` would silently have become *controlled* invariance — the object §D.2 insists it is not. | **REPAIRED.** §C.8.2 declares the autonomous/control split: mobilisation, recovery and transport are fixed by a declared deterministic autonomous rule; consumption is mandatory; **the draw `w_a` is the only control input**. §C.13 step 7 now names the selector. §D.2's frozen inputs now require the autonomous rule. |
| **MJ-2** | **`C_a` named two different objects.** The token world's consumption family was `C_a(u)`, colliding exactly with the EBU quote law's action-process cost `C_a` — the collision F.4 exists to prevent. `V_i`, `M_i`, `D_a` collided with `V_loc`/`V_∞`, `M_e`, and `D(φ)`. | **REPAIRED.** All five families renamed to three-letter mnemonics (`MOB`, `REC`, `TRN`, `CON`, `DRW`). §C.8 records the reserved single letters and states the earlier collision explicitly. |
| **MJ-3** | **§D.1 was a tautology under the likely table format.** If an entry is a tuple of transition families, `ΔQ_B = 0` holds identically by construction, so D.1 could not fail and §H.4's stop condition could not trigger — while the failure mode that *is* reachable (CR-2) was in none of D.1's lists. The table format was undeclared. | **REPAIRED.** §C.8.4 requires the format to be declared and tabulates what D.1 must check under each. D.1 relabelled honestly: under the recommended family-tuple format, `ΔQ_B = 0` is recorded rather than tested and the substantive test is composed legality. |
| **MJ-4** | **Finiteness of the state space was assumed, never argued.** `lat_i` and `deg_i` carry no individual bound; finiteness comes solely from the conserved-total constraint. Every termination and maximality claim rests on it. | **REPAIRED before the review returned** — the author had independently added the argument to §C.7. Recorded here because the stream found it independently. |
| **MJ-5** | **`L = lcm(2, p)` assumed one common demand period.** §C.10 declares a schedule per actor and then a period in the singular; with heterogeneous periods the phase modulus is wrong and the transition is not well defined on `S⁺`. | **REPAIRED before the review returned** — the author had independently changed this to `L = lcm(2, p_1, …, p_A)`. Recorded here because the stream found it independently. |
| **MJ-6** | **`§A.5` and `§H.1` disagreed on what was being decided** — three decisions listed versus four required, with no line for the implementation plan; and the information-pattern block was a one-option ballot, which is not a decision. | **REPAIRED.** §A.5 now lists four decisions and states the information pattern is not one. §H.1 adds the account-level choice and an implementation-plan line, and recasts Form D as an acknowledgement. |
| **MJ-7** | **"Accessible stock can rise only by mobilisation" was false as written** — transport raises `acc_j` with no mobilisation and no latent debit. True only of the world-wide total. Stated as an absolute under the heading "Regeneration cannot cheat". | **REPAIRED** in §A.3 and §C.8. |
| **MJ-8** | **§F.1a's third bullet omitted F.5–F.7**, which the table marks as blocking in the same `[M]` column. | **REPAIRED.** |
| **MJ-9** | **The Level 3 account-level declaration conflicted with the package's own non-claims.** The foundation defines Level 3 over *physical* carriers; §B.1 denies `Q` is one. The foundation's Level 1 is defined for exactly a declared reduced stock ledger. | **REPAIRED, and converted into an author decision.** New §B.0 tabulates both readings, states that `W0` has Level 3's structure with Level 1's epistemic standing and that the foundation defines no cell for that combination, records Level 1 as this package's preference, and adds the choice to §H.1. |

### 2.3 Minor — repaired

Repaired without further comment: no-op property 4 restated (§C.9); capacity
ceiling removed from `K` (§C.11); well-posedness condition
`Σ R_i + Σ β_a ≤ Q₀` added (§C.11.1); the one-tick draw-to-consume latency and
its interaction with the safe-set choice stated (§C.11.2, §C.11.3); quantifier
naming in the Form D collapse sentence corrected and the `V^B ⊆ V^A` inclusion
given its one-line justification (§E.2); Form B's `A_adm` defined for a
phase-dependent `K` (§E.2); `J_e`-to-token-flow implication removed (F.6);
F.5 restated as *unregistered* rather than *inapplicable*, with the
applicability observation marked as the author's (F.5); `O3`/`O8` no longer
presented as the account-layer unblockers (§A.6); `buf_a` explicitly declared
not an account (§C.3); the foundation's five-ledger separation cited (§B field
8, §B.1); the `ALLOWED_COST_CATEGORY` string literal quoted exactly (F.4);
`§19` rationale reworded (§B field 10); `κ`/`A` collisions with `d0_v29.Cell`
noted (§C.4); the uncited comparative claim about the CA literature attributed
to the predecessor (§A.4); the `§D.1` implementation-authorization gap closed
(§A.6, §H.3); and one dangling internal cross-reference removed.

---

## 3. Findings repaired *before* the reviews returned

Recorded for completeness, because they were also found independently by the
streams and it would be misleading to present them as caught only by review:

| Finding | Found by | Repaired |
|---|---|---|
| `d0_v29.Cell` declares **fourteen** fields, not seven; the seven belong to `d0_v29.LocalView` | Stream 1 (critical), and the author acted on it on receipt | §C.4 now cites `LocalView` and records `Cell`'s extra fields — `s, d, lam, kappa, source, rho, A` — as **exactly the non-conservative drive `W0` excludes**, which strengthens the design rather than merely correcting it |
| `EBU_FUTURE_BOOKS_STRUCTURE.md:1077` is a **working-tree** line; at HEAD the sentence is at line **982** | Stream 1 (major) | §K added; all citations moved to HEAD lines; the predecessor's identical defect recorded, not repaired (it is committed) |
| State-space finiteness argument missing | Author, then Stream 2 | §C.7 |
| Per-actor demand periods | Author, then Stream 2 | §C.6, §C.10 |
| Emphasis added inside a quotation from the conservation foundation §14.2 | Author | §B preamble; quotation now verbatim |

---

## 4. Findings REJECTED after verification

> **Two streams independently reached the same wrong conclusion. Both were
> rejected on evidence.** This is recorded in full because a review record that
> deletes its own errors is not a review record.

### 4.1 `OPEN_CONTROL_VOLUME` is **not** a fabricated identifier

**The finding (streams 3 and 4, both rated MAJOR):** the string
`OPEN_CONTROL_VOLUME` "appears nowhere in the repository except this line";
backticked SCREAMING_SNAKE presents an invented identifier as a registered
attribute; SD-01 has no registered "conservation class".

**Why both streams reached it:** both grepped the working tree and the tracked
file set. The canonical Stage D matrix is **not** on this branch — the SD
programme lineage split and has not rejoined — so a grep of this checkout
returns nothing, correctly.

**Verification that rejects the finding:**

| Check | Result |
|---|---|
| `git cat-file -t e6cd44f8b9e2e125403cb1359d819fc08afd2cb7` | `blob` |
| `git cat-file -s …` | `148183` bytes |
| SHA-256 of the blob's bytes | `081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81` — matches the digest recorded in the repository |
| `studies[study_id=="SD-01"].conservation_accounting.class` | `"OPEN_CONTROL_VOLUME"` |
| `studies[study_id=="SD-01"].model_domain.boundary` | `"open control volume; every declared shock and external replenishment is a boundary exchange"` |
| `studies[study_id=="SD-01"].model_domain.model` | `"one-stock regenerative resource with explicit demand, loss, reserve, shock, and policy ledgers"` |
| Literal occurrences of `OPEN_CONTROL_VOLUME` in the blob | 2 |

The claim is accurate, including "one-stock" and "declared boundary exchanges",
both of which the streams also challenged.

**Action taken anyway.** Two independent reviewers concluding "fabricated" is
strong evidence the *citation* was under-specified even though the *fact* was
right. New **§G.1a** states the provenance in full — blob hash, size, SHA-256,
the exact reproduction command, the three fields — and states explicitly that a
working-tree grep returns nothing and that this is expected.

### 4.2 The `K₁` direction correction in the predecessor is sound

**The finding (stream 2, raised as a caveat):** the predecessor's correction of
the repository's phrase "one-step conservative *inner* estimate" may be unfair,
since `K₁ ⊆ S` makes "inner" defensible relative to `S`.

**Adjudication: the caveat is fair and the predecessor already handles it.** The
predecessor names its referent explicitly ("the viability kernel"), and relative
to `K∞` the containment `K∞ ⊆ K₁` makes `K₁` an **outer** approximation, hence
not a safety certificate. The predecessor labels the point as its own reading
and disputes no substantive claim. **No change made**, and the adoption package
does not repeat it as an established defect.

---

## 5. Claims checked against repository bytes

Every one of the following was read from the file or git object named and
compared character by character.

### 5.1 Citations in the candidate — all verified

`ebu_quote_v30.py:24–26`, `:28`, `:56–68`; `d0_v29.py:188–194`, `:70–94`,
`:172–182`; `p1c_v29.py:19`; `V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:5`, `:1141`;
`v30_o14_multi_edge_plan.json:140`, `:194`; `EBU_FUTURE_BOOKS_STRUCTURE.md:364`
(identical at HEAD and in the working tree) and the I-3 sentence at HEAD line
**982**; `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §3.3, §4.1, §4.2,
§4.3, §8, §9, §11, §14.2; `SD_03_PRE_EXECUTION_READINESS.md` §4 and prerequisite
P5; `AGENTS.md` execution-safety and post-outcome-tuning clauses;
`v30_quote_validation_plan.json` falsifier **F5**.

### 5.2 Hash and integrity claims — all verified

| Claim | Recomputed | Verdict |
|---|---|---|
| Canonical-JSON SHA-256 of `v30_quote_validation_plan.json` | `a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061` | matches the digest `ebu_quote_v30.py` itself claims |
| Canonical Stage D matrix blob `e6cd44f8…`: type, size, SHA-256 | `blob`, `148183`, `081f2e99…8bdb81` | all three match |
| The six protected dirty paths, before and after all work | see §7 | byte-identical |

### 5.3 Status boundaries — all verified

The V3 finite EBU quote law is a **candidate design, not accepted**
(`V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md:1141`, "Candidate designs (not adopted as
truth)"). `V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md` is **"PROPOSED,
NOT ADOPTED"** at line 3, identical at HEAD and in the working tree. **O3** is
open. **O8** is open. **No wallet, account, balance or settlement substrate
exists** on this lineage. **SD-03 refuses `f_e`, `Ψ_e`, `J_e`** (its P1) and the
`potential-unit → EBU-unit` identification is unregistered (its P5). **SD-01's
registered conservation class is `OPEN_CONTROL_VOLUME`** (§4.1). The I-3
boundary/conservation profile is gated behind "a later, separate I-3
authorization".

---

## 6. Required scans

### 6.1 Overclaim vocabulary — PASS

Scanned for *adopted, validated, implemented, verified, passed, proved, proven,
established, confirmed, demonstrates, shows that, guarantees, ensures, SD-01*.
Every hit is either negated, qualified, or describes a future conditional step.
Representative negations carried in the candidate: "**A transition table has not
been adopted, instantiated, enumerated, or verified**"; "**This condition has not
been checked, because no table has been adopted**"; "**World A is not currently
passed. `Inv(K₀)` has not been computed**"; "**World C is not currently passed.
`V_∞` has not been computed**". The two genuine overclaims found — MJ-7 and the
header (CR-4) — are repaired.

One claim is deliberately **weaker** than a reader might expect and is flagged
here as the most important honesty point in the package: mandatory consumption
makes `V_∞ ⊊ K⁺` *possible*, but the package explicitly does **not** claim the
resulting world is decision-sensitive. §C.8.1 states that it could still be
trivially survivable or trivially doomed, and that which of the three it is, is
exactly what §D.2 and §D.3 would determine.

### 6.2 No scientific parameter values selected — PASS

Every numeric token in the candidate was tallied and classified. All resolve to:
structural constants (`N ∈ 2ℤ`, `N ≥ 4`, `N/2`, period `2`, ring distance `≥ 2`,
`A ≤ ⌊N/2⌋`, `3N + A`, coefficient `1`, `lcm(2, p_1, …, p_A)`, residual exactly
`0`, `C(0) = 0`, at most one actor per block); citation line numbers; section and
identifier numbers; version and hash strings; and the **counterexample values in
§C.8.3**, which exist only to demonstrate that per-family caps fail to compose
and select nothing.

**No value is proposed for `κ_i`, `R_i`, `β_a`, `ν_a`, `m_i`, `ψ_i`, `c_{ij}`,
`Q₀`, `N`, `A`, the horizon, the demand schedule, or any regime.** The
predecessor's §10.4 illustrative instance and its numeric state-space table were
**not** carried forward.

### 6.3 EBU bridge remains open — PASS

Ten gate items, all recorded as missing, unregistered, open, or requiring a
declaration; none filled in. No equation, unit, conversion, wallet, account,
permission, settlement rule, penalty, weight, reward, per-unit score, or
surrogate objective is introduced anywhere. The oracle carries **no** objective.
After CR-3's repair, the gate blocks a ranking-only smoke test as well as any
magnitude or settlement claim, and blocks nothing in the non-EBU verification
ladder §D.1–§D.4 — which remains the package's substantive finding.

### 6.4 Conservation is not collapsed into EBU — PASS

This was the check stream 3 reported the candidate handles best. `Q` is a token
count; §B.1, §F.1b and §I each deny it is, relates to, or bounds any EBU
quantity. The foundation's §9 five-ledger separation is now cited directly, and
`Q` is stated to serve exactly one of the five. The conservation proposition's
limits are stated with the foundation's own counterexample: "a lossless
two-state system can conserve a sum while deviations grow in opposite
directions. Conservation alone does not prove Lyapunov stability."

### 6.5 Deterministic demand removes the information-order ambiguity — PASS

Verified as sound. With a deterministic preregistered schedule, `D(φ)` is a
singleton, so Forms A, B and D coincide and there is no hidden information for
the ordering to allocate. The one implicit requirement — that the controller
observes the phase `φ`, not only the token state `s` — is discharged by the
augmented state (§C.6) and by the "fully observed" declaration (§B field 8). The
trap of using an optimistic Form A for a controller that must commit before
demand is revealed, and the resulting misattribution of a category-1 failure to
category 2, is correctly described (§E.3).

### 6.6 The package does not decide — PASS

§A.7's three options are unselected and unmarked; §A.1 states "Nothing in this
package makes it"; §H.2 caps acceptance at three things; §J declines outright to
propose the `Q`↔EBU relation. The one pre-selection found (MJ-6, the
single-option information-pattern ballot) is repaired by recasting it as an
acknowledgement.

### 6.7 No registration or book integration — PASS

§B's preamble states the package does not exercise and does not request the I-3
authorization, and that reusing the *shape* of a gated profile is not adding
one. §G.2 and §G.3 state that neither conceptual home is claimed, occupied, or
requested, and that the Part V resemblance "is a resemblance, not a placement,
and it confers no book slot". §G.1 states plainly that the substrate is not
SD-01 and satisfies no SD prerequisite.

---

## 7. Protected working tree

| Path | State | SHA-256 before | After |
|---|---|---|---|
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | modified (pre-existing) | `fad9756f…39df4` | identical |
| `V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md` | modified (pre-existing) | `3acab84c…b8435` | identical |
| `V3.0_LONG_HORIZON_STUDY_DECISION_PACKET.md` | modified (pre-existing) | `4ef7a903…5766e` | identical |
| `longhorizon_v30.py` | modified (pre-existing) | `8952bf0e…2bd06` | identical |
| `test_v30_longhorizon.py` | modified (pre-existing) | `a5f6ef09…10012b` | identical |
| `V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md` | untracked (pre-existing) | `f3dec182…93ef` | identical |

**All six verified byte-identical** by `shasum -a 256 -c` against a record taken
before any writing. No protected path was modified, staged, formatted, renamed,
moved, reverted, stashed, deleted, or committed. No `git clean`, `git reset`,
`git checkout --`, or worktree operation was used. The worktree count was 115
before and after.

---

## 8. Defects in the predecessor, recorded and NOT repaired

`CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md` is committed at `0726ccd` and is **not
edited by this package**. These are recorded so they are not silently inherited:

| # | Defect | Inherited? |
|---|---|---|
| 1 | §5.2 attributes seven per-cell parameters to `d0_v29.Cell`; `Cell` declares fourteen, and the seven belong to `LocalView` | **No** — candidate cites `LocalView` and records `Cell`'s extra fields |
| 2 | §13.1 presents "delivery capacity is not resource stock" as a quotation; the registered amendment says "A coefficient constrains delivery capacity; it never creates resource stock". The substantive point is supported; the quoted string is not in the repository | **No** — candidate does not quote it |
| 3 | §2 cites `EBU_FUTURE_BOOKS_STRUCTURE.md:1077`, a working-tree line; at HEAD the sentence is at 982 | **No** — §K records it; candidate uses 982 |
| 4 | §12.2 attributes "never a quadrature, never a series, never a surrogate" to `ebu_quote_v30.py`; it is at `SD_03_PRE_EXECUTION_READINESS.md:171` and is a forward-looking SD-03 statement | **No** |
| 5 | §14 truncates the `AGENTS.md` tuning rule before "unless a separate protocol explicitly authorizes it", then labels it exceptionless | **No** — candidate does not quote it |
| 6 | §9.3 truncates Impossibility 6.4 before "without design-time `R_i^eff` certification", converting a conditional impossibility into an absolute one | **No** |
| 7 | §5.6 equates "16 sites" with 18 coordinates; under its own `3N + A` scheme 16 sites is `48 + A`, and the true count is ~`3.6 × 10²²`, so "five orders outside" should be ~fourteen. Error is in the safe direction | **No** — candidate carries only the symbolic bound |
| 8 | §5.6 rows 3–4 use a coordinate scheme ("3 stock coords + 2 reservoir coords") that §5.2 never defines | **No** — numeric table dropped |
| 9 | §5.6 tabulates `N = 2`, where `P_odd = P_even` and the alternation is vacuous | **No** — candidate requires `N ≥ 4` |
| 10 | §6.1 titled "four transition types", tabulates five; §6.3 says five | **No** — candidate says five throughout |
| 11 | §6.2 step 4 cross-references "(§6.4)" for the block specification; §6.4 is the local flow law | **No** — candidate points at §C.8 |
| 12 | §12.2 and F.3's ancestor carry the incorrect ranking-invariance sentence (CR-3) | **No** — §F.3a corrects and attributes it |
| 13 | §5.5 assumes one shared demand period | **No** — candidate uses per-actor periods |

**Recommendation:** defects 1–7 and 12 are substantive enough that the
predecessor should receive a correction pass under its own authorization. That
is **not** done here, and this review does not authorize it.

---

## 9. What remains open

| Open item | Why it cannot be closed here |
|---|---|
| Whether the world is **decision-sensitive** | Mandatory consumption makes a non-trivial kernel possible; whether some policies survive and others do not is determined only by §D.2/§D.3, which are unauthorized and unperformed |
| The entire **EBU bridge** (ten items, §F) | Requires acceptance of the quote law, a `V_loc` coordinate declaration, a `C_a` declaration, a registered unit identification with its point of application, and — for the permission diagnostic — an account substrate that does not exist |
| Diagnostic **category 4** (permission-blocked) | No account, wallet, balance, permission or settlement layer exists. It must not be simulated or approximated |
| The **account level** (Level 1 vs Level 3) | The foundation defines no cell for a closed ledger over a non-physical carrier; §B.0 puts the choice to the author |
| The **safe-set declaration** (rationing vs service) | Changes the kernel; must be recorded before anything is computed |
| The **autonomous rule** and the **table format** | Both required at adoption; neither selected here |
| How viability **scales past the tiny world** | Exact enumeration is infeasible at 16 sites; the package says so and does not solve it |
| Correction of the **predecessor memo** | Requires its own authorization |

---

## 10. Recommendation

> ### `READY FOR AUTHOR REVIEW`

**Basis.** Four critical findings were identified and all four are repaired.
Nine major and sixteen minor findings are repaired. Two findings were rejected
on verified evidence and the rejection is recorded in full, together with a
strengthening change made because the objection, though wrong, revealed an
under-specified citation. Every repository citation, both hash claims, and all
status boundaries verify against repository bytes. No scientific parameter value
is selected. The EBU bridge is open in every one of its ten items and is
narrower after review than before, because CR-3's repair removed the only route
that had looked partly reachable. All six protected dirty paths are
byte-identical.

**The qualification that belongs in the recommendation, not in a footnote.**
CR-1 was a defect in the *design*, not in its presentation: as originally
specified, the centrepiece of the package — the viability oracle — would have
been mathematically vacuous. It is repaired by making consumption mandatory,
and the repair is principled rather than patched. But the repair establishes
only that a non-trivial kernel is **possible**. Whether the world is actually
decision-sensitive is unknown and is not knowable without the computations §D.2
and §D.3 describe, which this package does not authorize. **An author reading
this should understand that they are being asked to adopt a substrate whose
scientific interest is not yet established, and that establishing it is the
next authorized step and not this one.**

`NEEDS CORRECTION` was considered and rejected because no material finding
remains unrepaired. `NO-GO` was considered and rejected because no finding
showed the recommended family to be unsound — CR-1 and CR-2 were defects in the
specification of the family, both closable with no new mathematics, and both
closed.
