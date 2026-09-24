# Cross-report notes

**Classification: `archival_metadata`. This is NOT a historical report.**

It was written during the byte-audit correction pass, after the historical
bodies were recovered and byte-fixed. It records observations *about* the
preserved reports. It does not adjudicate them, does not decide which historical
wording should have been used, and does not re-derive any mathematics.

**No historical body was altered when this file was created.** All eleven body
SHA-256 values were recomputed before and after and are identical.

---

## Discrepancy 1 — Gate 4 and Gate 5 on A3 reserve dependence

**Gate 4** (`STAGE_A_GATE_4_ADVERSARIAL_INTERPRETATION.md`, §B.3) provided a
concrete counterexample to the universal claim that A3 service necessarily
depends on positive previously earned reserve. It cited the registered candidate
table for `A3|ebu_random|k=10` — arrival state `(5,4,3)`, plan `B→C@1`,
post-state `(5,3,4)`, receipt to B of `0` — and concluded that "earned reserve
financed every A3 service" is too strong, while noting that other recorded plans
genuinely do require prior owner balances.

**Gate 5** (`STAGE_A_GATE_5_FINAL_DISPOSITION.md`) later classified the
universal claim

> "all A3 service necessarily requires positive previously earned reserve"

as **NOT TESTED — neither ruled in nor out**.

**These historical formulations are not identical.** One reports a specific
counterexample to a universal claim; the other classifies that universal claim
as untested.

The archive records the discrepancy. It does **not** decide which
characterization was correct, whether either should be amended, or what the
underlying scientific position ought to be. Both historical bodies remain
unchanged and byte-fixed.

---

## Discrepancy 2 — Reconciliation and Independent Skeptic 2 on the sink-force term

**The reconciliation** (`FOUNDATION_RECONCILIATION_GATE.md`) summarized
Independent Skeptic 2 as asserting `f_e = mu_s - eta mu_d` with no third term,
and elsewhere recorded the valued-sink three-term form as "not stated" by either
audit.

**The recovered Independent Skeptic 2**
(`FOUNDATION_INDEPENDENT_SKEPTIC_2.md`, §3, "Essential qualification")
explicitly contains the valued-sink qualification and the corresponding third
term, including a worked example.

**The reconciliation itself disclosed the reason.** Its own scope limitation
states that it held the full text of only one of the two audits and that
Audit B's positions were available to it "only as reproduced in this brief's
controlling text," with affected rows marked "(via brief)".

The archive therefore preserves this as a **source-availability discrepancy**:
the reconciliation characterized a report it did not hold in full. It is
recorded here rather than corrected in either body.

This note does **not** re-adjudicate the underlying mathematics, and takes no
position on the sink-force branches.

---

## Authorship and recovery-independence limitation

`FOUNDATION_FINAL_FREEZE_CLOSURE_AUDIT.md` was authored in the same Claude
session that later performed this scientific record recovery and its own
self-checks.

**Classification:**

- **BYTE PROVENANCE SOUND** — the body was extracted byte-for-byte from the
  session transcript, and its hash is reproducible in this environment.
- **RECOVERY / SELF-CHECK INDEPENDENCE LIMITED** — the recovery pass that
  preserved and verified this report shares an author with the report itself.

**This does not by itself establish that the freeze-closure audit was
scientifically non-independent from the reconciliation author.** It records a
structural limitation of the recovery arrangement, not a finding about the
report's content, reasoning or conclusions.

A reviewer wanting independent assurance on that report specifically should
obtain it from a party that did not author it.

---

## Scope of this note

Recorded here: two cross-report discrepancies and one authorship limitation.

Not done here: adjudication, correction, re-derivation, reinterpretation, or any
change to a historical body. Preserve first; interpret later.
