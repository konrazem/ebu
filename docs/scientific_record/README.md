# EBU scientific record — evidence bundle (candidate)

New explanatory material. The report bodies beside it are **verbatim historical
outputs** and are not summarized, corrected or reinterpreted here.

**This bundle is a candidate. It is not committed, not frozen, and carries no
repository authority yet.** An independent byte-level audit must inspect it first.

## Authoritative Stage-A coordinate

| | |
|---|---|
| branch | `origin/publication/demand-driven-stage-a` |
| commit | `2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32` |
| tree | `5afe39788ecc6bff675b0820eef1669fb8b78ebf` |
| `demand_driven_ebu` | `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48` |

All three were verified independently before recovery began.

## The evidence chain

```
Stage-A publication  (768 episodes, 11,066 epochs, published and verified)
      |
      v
Gate 1  registered execution integrity        -> CONDITIONAL PASS
      |
      v
Gate 2  construct validity                    -> CONDITIONAL PASS
      |
      v
Gate 3  preregistered results extraction      -> CONDITIONAL PASS
      |
      v
Gate 4  adversarial interpretation            -> CONDITIONAL PASS
      |
      v
Gate 5  final Stage-A scientific disposition  -> STAGE A SCIENTIFICALLY ACCEPTED
      |                                          WITH BOUNDED CLAIMS
      v
Foundation audit 1   "Face the Devil"         -> FOUNDATIONAL CORE SURVIVES
      |                                          DOUBLE-CHECK
      v
Foundation audit 2   independent skeptic      -> INDEPENDENT SKEPTIC CONFIRMS
      |                                          CORE
      |
      v
Physical foundation reconciliation gate       -> PHYSICAL EBU FOUNDATION
      |                                          RECONCILED
      v
Independent freeze audit                      -> CONDITIONAL PASS
      |
      v
Final freeze-closure audit                    -> FINAL FREEZE-CLOSURE
                                                 CONDITIONAL PASS
```

## What is in this bundle

### `stage_a/`

| file | role | recovered |
|---|---|---|
| `STAGE_A_GATE_1_EXECUTION_INTEGRITY.md` | Gate 1 | ✅ exact |
| `STAGE_A_GATE_2_CONSTRUCT_VALIDITY.md` | Gate 2 | ✅ exact |
| `STAGE_A_GATE_3_RESULTS_EXTRACTION.md` | Gate 3 | ✅ exact |
| `STAGE_A_GATE_4_ADVERSARIAL_INTERPRETATION.md` | Gate 4 | ✅ exact (external record) |
| `STAGE_A_GATE_5_FINAL_DISPOSITION.md` | Gate 5 | ✅ exact |
| `STAGE_A_PUBLICATION_REMOTE_VERIFICATION.md` | publication verification (optional) | ✅ exact |

### `physical_foundation/`

| file | role | recovered |
|---|---|---|
| `FOUNDATION_AUDIT_FACE_THE_DEVIL.md` | foundation audit 1 | ✅ exact |
| `FOUNDATION_INDEPENDENT_SKEPTIC_2.md` | foundation audit 2 | ✅ exact (external record) |
| `FOUNDATION_RECONCILIATION_GATE.md` | reconciliation gate | ✅ exact |
| `FOUNDATION_INDEPENDENT_FREEZE_AUDIT.md` | independent freeze audit | ✅ exact (external record) |
| `FOUNDATION_FINAL_FREEZE_CLOSURE_AUDIT.md` | final freeze-closure audit | ✅ exact |

Each recovered body has a `<filename>.meta.json` sidecar carrying its SHA-256,
byte count, source kind and provenance note. **Metadata is never inserted into a
body.** What the sidecar can name depends on the source kind — the two are not
equivalent, and the difference is recorded rather than smoothed over:

**A. `task_conversation_history`** — independently recoverable from the local
Claude session transcript. These sidecars name the exact session, zero-based
line index, message uuid and authoring timestamp, and those coordinates are
reproducible in this environment.

**B. `external_project_conversation_record`** — supplied verbatim from the
ChatGPT EBU project conversation and byte-fixed by SHA-256 after supply. These
sidecars carry **no** session, line, uuid or authoring timestamp, because the
local environment has none to record.

Every sidecar states which case applies, via `local_transcript_authenticated`
and an `authentication_note`.

**This is a provenance distinction only. It implies nothing about the
scientific content, rigour or standing of the reports concerned.**

`EVIDENCE_MANIFEST.json` lists all ten required reports plus the optional
publication verification, with hashes, byte counts, source kind and the final
disposition anchor verified present in each body.

`CROSS_REPORT_NOTES.md` is **archival metadata, not a historical report**. It
records two cross-report discrepancies (Gate 4 vs Gate 5 on A3 reserve
dependence; reconciliation vs Independent Skeptic 2 on the sink-force term) and
one authorship/recovery-independence limitation, without adjudicating any of
them.

## All ten required reports are preserved

**Stage-A Gates 1–5 are preserved. The required Physical Foundation audit chain
is preserved.**

Two provenances are recorded, and the distinction is deliberate:

- **Seven** bodies were extracted byte-for-byte from Claude session transcripts
  (`source_kind: task_conversation_history`). Their sidecars name the exact
  session, line index, message uuid and authoring timestamp.
- **Three** — Gate 4, the independent skeptic audit, and the independent freeze
  audit — were **not present in any Claude transcript**. They were supplied
  verbatim from the ChatGPT EBU project conversation record
  (`source_kind: external_project_conversation_record`). They did **not**
  originate in the Claude transcript, and their sidecars say so.

> **External-record limitation.** The supplied external historical records are
> byte-fixed and transparently sourced from the ChatGPT EBU project record.
> Their original ChatGPT transcript/UI source and original authoring timestamps
> were not independently authenticated by the local Claude environment.
>
> This applies to exactly:
> `STAGE_A_GATE_4_ADVERSARIAL_INTERPRETATION.md`,
> `FOUNDATION_INDEPENDENT_SKEPTIC_2.md`,
> `FOUNDATION_INDEPENDENT_FREEZE_AUDIT.md`.
> **They are not marked as locally transcript-verified.**

Nothing was reconstructed from a summary, a quotation, an expected disposition
or repository inference. Every body carries its own final disposition anchor,
verified present rather than inserted.

## Programme status

- **Stage A is complete. It must not be rerun.** Its numbers, artifacts and
  registered results are published and unchanged.
- **Stage B is paused.** See `STAGE_B_DESIGN_HISTORY_NOTE.md`.
- **The next programme step is an independent byte-level audit of this
  scientific-record evidence bundle.** The canonical Physical EBU Foundation
  freeze follows that audit; it is not begun here.

## Scope

This README adds no scientific claim, decides no gate, and resolves no
disagreement. Preserve first; interpret later.
