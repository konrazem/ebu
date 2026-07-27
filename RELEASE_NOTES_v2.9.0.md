# EBP V2.9.0 — Local preservation controller and behavioral validation

**Release scope:** documentation and validation of the completed V2.9 study.
P1C is a **candidate physical preservation controller in deterministic toy
worlds** — it is not a finished ecological economy, not a monetary system, and
not a proven general sustainability mechanism.

## Purpose of V2.9

V2.9 asks: *can a spatially local process determine how much a regenerative
source may safely export, preserve its certified reserve, and reveal
infeasible demand — without evaluating the whole world or simulating its
future?* In the deterministic fixtures tested, the answer is yes for one-step
reserve preservation and honest rationing; feasibility remains a separate
property no export rule can create, and long-horizon/stochastic viability
remains open.

## Implemented components (all new since v2.8.0)

| Component | File | What it is |
|-----------|------|------------|
| Exact synchronous local D0 law | `d0_v29.py` | frozen-state, loss-aware, unconstrained explicit-Euler engine (V2.8 Def 3.2); strict local decision API |
| P1K projection wrapper | `d0_v29.p1k_step` | **diagnostic only**: clamps the raw D0 proposal to `[0, K]`, recording shortfall/spill exactly; its ledger closes by construction and never certifies physical availability |
| P1C preservation controller | `p1c_v29.py` | source-local P/R/I/F classifier, robust aggregate safe-export budget (A4.5), proportional multi-edge allocation, synchronous update, post-loss service accounting, explicit unmet demand |
| Deterministic wind tunnel | `exp_v29.py` + `v29_deterministic_plan.json` | preregistered D1–D8 (24 runs, locked plan hash `af8f119b…`) |
| D9/D10 preservation study | `exp_v29_d9_d10.py` + `v29_d9_d10_plan.json` | preregistered, locked (plan hash `87ad0ae2…`); 144 runs, single authorized execution |
| Strict serialization | `serialization_v29.py` | fail-closed result writing (`allow_nan=False`); narrow normalization for two nullable diagnostics only |
| Design documents | `V2.9_BEHAVIORAL_PROTOCOL_DRAFT.md`, `V2.9_OBJECTIVE_ALIGNMENT_DRAFT.md` + `_REVIEW.md` | protocol, EBU/debt design candidates (not implemented), independent review ("pass with corrections"; scalar EBU **not yet justified**) |

## Theorem vs non-theorem

- **Theorem (one-step aggregate reserve preservation; review Thm 4.1).** If a
  regenerative source starts at or above `R_eff`, its no-export successor
  stays feasible, and aggregate accepted export obeys
  `Q ≤ [x + Δt·u − R_eff]₊/Δt`, the synchronous constrained successor stays
  at or above `R_eff`. One step, synchronous, margin-conditional.
- **Not a theorem:** infinite-horizon sustainability, global homeostasis,
  arbitrary scheduling, uncertain models beyond declared `ε` margins,
  complete service, or any EBU accounting property.
- **Feasibility is separate:** when natural decline alone would cross the
  reserve (state I), zero export cannot preserve it; P1C reports that state.
- **Outside V2.8:** the V2.8 finite-step burden inequality covers only the
  *unconstrained* D0 flux; P1C's capped flux is explicitly outside it. The
  joint constrained preservation-plus-dissipation theorem is **open**.
- Passing tests are numerical validation at declared points, never proof.

## Deterministic results (from committed artifacts)

**D1–D8** (24 runs): exact-D0 descent, loss-aware rest points, one-tick
causality, driven service and shock recovery all held as registered; **D5
failed to discriminate** (retained; motivated D9); D8's monotone-growth
sub-claim failed (recorded).

**D9** (Allee reserve stress, `R_eff = 11`): reserve-blind and soft-penalty
arms both **collapse**, crossing the reserve at tick 8; the soft penalty
delayed the Allee crossing (tick 24 vs 17; over-use 183.0 vs 201.8) but did
not prevent it. Both P1C arms: **safe rationing** — source held at exactly
11.0, zero reserve/Allee crossings, cap binding 193/200 ticks, delivered
130.82 with unmet 69.18 reported explicitly, zero one-step-preservation
violations over 200 eligible ticks. D9-C ≡ D9-D: the hard cap, not χ,
preserves.

**D10** (140-run phase map, 35 per policy): P0 35 safe_rationing (trivial —
no service); P1 25 collapse + 10 safe_service; soft identical to P1; **P1C 25
safe_service + 10 safe_rationing, zero collapse, zero physical over-use**
(P1/soft over-use in 25/35 points). Collapse tracks the registered analytic
boundaries (`d/g_max ≥ 0.9`, low `η`). 18 domain exits recorded, none
dropped. Preservation must be read together with service: P0 preserves by
serving nothing.

## Failures and negative controls

Attempt 1 of D9/D10 failed on harness integrity and is preserved
(`ATTEMPT_1_FAILURE.md`). D5 did not discriminate. D8's P4 arm overshot
exactly as registered at tick 1 but falsified its monotone-growth sub-claim.
The V2.6 guarded-ledger exploit (+260 EBU while all sources die) remains open
and constrains any future credit rule.

## Serialization incident and resolution

After the single Attempt-2 run, the two aggregate stability diagnostics
overflowed to infinity on 15 diverging runs and were post-processed to JSON
`null` under explicit authorization (no trajectory, classification, or other
metric changed; the study was not re-run). Three further domain-exit records
were natively undefined, so 18 records carry null diagnostic pairs
(reconciled in `results/v2.9/d9_d10/ATTEMPT_2_SERIALIZATION_REPAIR.md`).
Gate 2.4B made all future result writing **fail closed**
(`serialization_v29.py`, 46 regression checks).

## Limitations

Deterministic toy worlds only; no stochastic/confirmatory seed study for P1C;
no finite moving actor population, actor health/death, or complete society;
**no EBU issuance, ecological-debt ledger, wallets, exchange, or
scalarisation** (design candidates only; the independent review finds scalar
EBU not currently justified); reserve certification (`R_eff`) assumed given;
long-horizon viability open; not peer reviewed.

## Reproducibility

```bash
python3 test_v29.py                # 141 checks / 15 groups (D0 conformance)
python3 test_v29_behavior.py       # 108 / 9  (D1-D8)
python3 test_v29_p1c.py            #  83 / 12 (P1C conformance)
python3 test_v29_d9_d10.py         # 114 / 20 (D9/D10 harness)
python3 test_v29_serialization.py  #  46 / 6  (strict serialization)
venv/bin/python make_paper_v29.py  # rebuild the V2.9 PDF from committed artifacts
```

The committed studies are locked: `exp_v29.py` and `exp_v29_d9_d10.py`
recompute their canonical plan hashes, take no options, and refuse to
overwrite completed results. Committed with Python 3.14.2.

## Exact difference between V2.8 and V2.9

V2.8 was a **written discrete mathematical foundation** (no engine): the
finite-step burden inequality for the idealized unconstrained D0 law, plus
numerical validation. V2.9 **implements** that D0 law as a strict-locality
engine (`d0_v29.py`), adds the **P1C constrained preservation controller**
(outside the V2.8 theorem, with its own one-step reserve algebra), and runs
the first preregistered behavioral experiments (D1–D8, D9, D10) showing —
deterministically, in these fixtures — that hard local caps preserve where
soft penalties and unconstrained flow collapse. V2.8 proved a brick; V2.9
built and stress-tested the first wall segment. Neither is the building.

## Next research direction

The joint constrained preservation-plus-dissipation theorem; the
infinite-horizon controlled-invariant kernel; multi-source/multi-edge joint
invariance; a stochastic confirmatory study for P1C; and — before any EBU
layer — ecological-debt attribution and an operational verified-restoration
predicate. See `Foundation_v2.9_local_preservation.md` §16.
