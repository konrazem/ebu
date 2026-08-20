# Unified Python Research Framework I-3C Settlement-Causality Repair Authority Amendment

Status: **prospective documentation-only authority candidate; unimplemented;
current fail-closed runtime remains controlling**.

## 1. Decision and authorization boundary

This amendment freezes the narrow Framework I-3C settlement-causality repair
accepted prospectively by §12 of
`ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md` and by
`atomic_generator_foundation_contract.json.i3c_settlement_causality_repair`.
It corrects the future meaning of the affected settlement predicates without
editing or executing the current framework.

This stage creates exactly four prospective authority documents:

1. `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3C_SETTLEMENT_CAUSALITY_REPAIR_AUTHORITY_AMENDMENT.md`
2. `unified_python_research_framework_i3c_settlement_causality_repair_contract.json`
3. `unified_python_research_framework_i3c_settlement_causality_repair_validation_contract.json`
4. `unified_python_research_framework_i3c_settlement_causality_repair_predecessor_manifest.json`

The Markdown is the normative human rendering. The first JSON document is the
mechanical rule and ordering source. The second JSON document supplies the
closed prospective validation order and projected supplemental fixture. The
predecessor manifest supplies the complete accepted-tree identity. A mismatch
among the four is an integrity failure and requires fail-closed refusal.

No implementation, existing fixture, test, package, result, manuscript, book,
or PDF is modified here. No framework behavior, test suite, transition,
simulation, trajectory, Gate operation, model-state advance, scientific
execution, interpretation, publication, commit, push, merge, tag, or pull
request is authorized.

## 2. Exact checkpoint and precedence

The accepted target is local, remote-tracking, and freshly queried live branch
`framework-v0.1` at
`ff23d70c022a5c5cf3cb130b55568680de87ae97`. That commit is the controlling
atomic-authority merge. Its accepted atomic-authority parent feature is
`d0d1eddcf6d5e3b0393dfc4d66db7d63f1c0de47`.

The accepted I-3C implementation feature is
`5ec122d45ebe617ebc1d761bc5d1f5172b736c41`, integrated by
`95f3c1990d32859dd091756a68571959406f2c1b`. The accepted I-3E fixture feature
is `dac8717017e8ba6d6c46b17d031095f3b898762f`, integrated by
`eaafbb50f30f3ed3e1300bc9d96456f570d17e13`.

Precedence is deliberately narrow:

1. The atomic amendment and contract control the prospective scientific and
   institutional separation in this repair.
2. This package supplies the exact Framework I-3C predicate, preservation,
   validation, and future-path mechanics needed to implement that repair.
3. It supersedes only the current over-broad non-`IDENTIFIED` settlement
   predicate and the directly necessary completeness of share arithmetic and
   explicit closure.
4. The accepted I-3 authority retains precedence for every unaffected
   declaration, signature, constructor, projection, collection rule,
   applicability rule, link rule, unit rule, failure identifier, precedence
   position, export, import edge, and nonclaim.
5. The current implementation and historical 544-vector fixture remain
   controlling executable behavior until a separately authorized repair is
   implemented and independently audited. No caller may bypass the current
   validator.

Any conflict outside this narrow scope requires refusal rather than selective
interpretation.

## 3. Reconstructed accepted predecessor

The accepted I-3 package freezes 69 types, 23 validators, 88 ordered failure
codes, 219 ordered root exports, 15 modules, 91 direct package-import edges,
133 collection contracts, 43 applicability contracts, 12 paired-quantity
rows, and 544 validation vectors.

The immutable historical fixture is
`tests/framework/fixtures/i3_validation_v1.json`: 24,179,582 bytes, SHA-256
`e5790524bb7d63dcc18e15cd933d801c225253230f09b06d9828a703fc6218c5`.
Strict reconstruction established 184 successes, 360 failures, 543 unique
effective inputs, one benign identical-input collision for the one-member
`RouteSemanticsStatus` positive/boundary pair, and zero conflicting outcomes.
Its canonical bytes are identical under the two independent encoders frozen
by the validation contract.

The settlement slice contains 20 historical vectors. Its accepted first-
failure order is:

```text
I3_OBJECT_CONTENT_MISMATCH
IMPLICIT_ABSENCE_FORBIDDEN
I3_COLLECTION_ORDER_INVALID
I3_DUPLICATE_MEMBER
SETTLEMENT_LINK_INVALID
CONSERVATION_UNIT_MISMATCH
SETTLEMENT_CLOSURE_FAILURE
CAUSAL_ATTRIBUTION_UNRESOLVED
HASH_MISMATCH
```

The current `src/ebu_framework/settlement.py` causal predicate fires whenever
the directly supplied causal status is non-`IDENTIFIED` and any of the
following is true: shares are nonempty, closure resolution is `PRESENT`, a
child causal-contribution reference is an `ObjectRef`, or a child settlement-
share reference is an `ObjectRef`. That predicate rejects the accepted
noncausal institutional-share case even when the causal-contribution field is
`NOT_APPLICABLE`, every settlement share has a typed `rule_ref`, units agree,
and exact share-plus-residual closure holds.

The current implementation also checks
`measured_total = share_total + residual`, but it does not separately check
that `share_total` is the exact sum of the supplied share amounts or require a
`PRESENT` closure whenever shares are supplied. Those are directly necessary
closure obligations for this repair and add no causal meaning.

## 4. Distinct meanings

The following meanings are non-interchangeable:

| Layer | Exact meaning in this repair | Forbidden inference |
|---|---|---|
| Physical group measurement | The immutable group endpoint measurement referenced by the group receipt and represented locally by `GroupResidual.measured_total` | Settlement may not recompute, replace, or relabel it |
| Mathematical decomposition | A declared arithmetic or optimization decomposition, including marginal, shadow-price, interaction, or Aumann-Shapley values | It is not causality or entitlement |
| Causal contribution | A child causal claim represented by `ChildActionRecord.causal_contribution_ref` and supported only under identified causality | No amount or provenance link silently supplies it |
| Institutional settlement share | `SettlementShare.amount`, governed by its mandatory institutional `rule_ref` | It is not a measured causal contribution |
| Explicit residual | `GroupResidual.residual`, retained even when zero | It may not be silently omitted or assigned causal meaning |
| Arithmetic closure | Exact accepted arithmetic linking actual supplied shares, declared share total, residual, and measured total | It is not physical conservation or causal identification |
| Rule provenance | The mandatory `SettlementShare.rule_ref` plus independently accepted institutional declaration | An opaque reference alone does not prove target role or legitimacy |

Physical records remain immutable. I-3 does not resolve opaque references and
does not prove that a referenced target is truly institutional, causal,
complete, accepted, or scientifically valid. That external classification is
a fail-closed precondition, not an invitation to infer target meaning inside
the local validator.

## 5. Preserved declaration surface

The repair adds no type, enum member, field, failure code, export, or import
edge. The following declarations remain byte-shape compatible:

- `CausalIdentificationStatus` remains exactly `IDENTIFIED`,
  `PARTIALLY_IDENTIFIED`, and `UNIDENTIFIED`;
- `GroupReceipt` retains `causal_status` and `settlement_ref`;
- `ChildActionRecord` retains distinct `causal_contribution_ref` and
  `settlement_share_ref` fields;
- `SettlementShare` retains `beneficiary_ref`, `amount`, mandatory
  `rule_ref: ObjectRef`, and `evidence_refs`;
- `GroupResidual` retains `measured_total`, `share_total`, `residual`, and
  `arithmetic_policy_ref`;
- `SettlementClosureRecord` retains `group_residual_ref`, `share_refs`,
  `closure_resolution`, and `validated_arithmetic_ref`; and
- `validate_settlement_closure` retains its exact eight-argument
  positional-only signature and exact nine-code precedence.

`NOT_APPLICABLE` is not a new causal-status enum value. The required
not-applicable case uses the already accepted
`ChildActionRecord.causal_contribution_ref = Applicability.NOT_APPLICABLE`
where permitted. It may coexist with independently authorized settlement.

## 6. Frozen corrected semantics

Let `nonidentified` be true when either the supplied `causal_status` argument
or `group_receipt.causal_status` is not `IDENTIFIED`. Treating either direct
status as identified may not bypass a nonidentified status in the other.

Let `causal_claim` be true when any child
`causal_contribution_ref` is an `ObjectRef`. A settlement share is causally
relabeled when its share, amount, or evidence is represented through such a
causal-contribution link under nonidentified causality. An opaque
`SettlementShare.evidence_refs` target is not classified by lookup in I-3;
external evidence typing remains a required fail-closed precondition.

Let the exact share sum be the sum of every supplied `SettlementShare.amount`
in canonical share order under the accepted exact numeric rules. No binary
floating approximation, implicit conversion, hidden tolerance, or default
unit conversion is introduced.

The prospective predicates are:

1. Constructor formation still requires every share `rule_ref` to be an exact
   `ObjectRef`. Missing or malformed rule references fail formation.
2. An independently accepted rule declaration must classify every share
   `rule_ref` as institutional before the share can be accepted. I-3 does not
   infer that classification from opaque bytes.
3. Existing object-content, applicability, collection-order, duplicate, and
   settlement-link predicates run unchanged and in the same order.
4. Existing unit and dimension compatibility runs before arithmetic closure.
5. `SETTLEMENT_CLOSURE_FAILURE` fires when any of these is true after unit
   compatibility succeeds:
   - exact supplied share amounts do not sum to `residual.share_total`;
   - `residual.measured_total` does not equal
     `residual.share_total + residual.residual` under accepted exact
     arithmetic;
   - shares are supplied but `closure.closure_resolution.state` is not
     `PRESENT`; or
   - no shares are supplied but closure is incorrectly asserted `PRESENT`,
     preserving the historical rule.
6. `CAUSAL_ATTRIBUTION_UNRESOLVED` fires when `nonidentified` and
   `causal_claim` or causal relabeling is present.
7. It does not fire merely because group settlement linkage, child
   `settlement_share_ref` links, institutional numeric shares, a zero or
   nonzero explicit residual, or a `PRESENT` arithmetic closure exists.
8. The historical identified-causality requirement for nonempty child actions
   remains unchanged.
9. No settlement path may mutate or replace the physical measurement. A
   registry or identity attempt to replace the accepted physical record fails
   before settlement validation under its existing owner.
10. A path that omits the governing validator has no accepted settlement
    result. No success, receipt acceptance, registry activation, or scientific
    claim may be inferred from bypass.

## 7. Allowed combinations

Subject to all earlier predicates and external institutional-rule acceptance,
the following are prospectively allowed:

- `UNIDENTIFIED` with no child causal claim and no settlement;
- `UNIDENTIFIED` with child causal contribution `NOT_APPLICABLE`, valid child
  settlement links, institutional shares, compatible units, `PRESENT`
  closure, and exact zero or nonzero residual;
- `PARTIALLY_IDENTIFIED` under the same nonidentified causal prohibition;
- a not-applicable child causal field with independently authorized
  institutional settlement;
- zero residual when shares exactly close the measured total;
- nonzero explicit residual when shares partially allocate the measured
  total; and
- every historically accepted `IDENTIFIED` combination whose other predicates
  remain satisfied.

## 8. Rejected combinations and failure ownership

The following are prospectively rejected:

| Condition | Owner or outcome |
|---|---|
| Numeric or linked child causal contribution while either direct status is nonidentified | `CAUSAL_ATTRIBUTION_UNRESOLVED` |
| Institutional share represented or linked as causal-identification evidence under nonidentified causality | `CAUSAL_ATTRIBUTION_UNRESOLVED` |
| Missing or malformed `SettlementShare.rule_ref` | `I3_RECORD_FORMATION_INVALID` |
| Well-formed rule reference not independently accepted as institutional | Fail closed before share acceptance; no opaque-target inference |
| Shares without `PRESENT` explicit closure | `SETTLEMENT_CLOSURE_FAILURE` |
| Incompatible unit or dimension | `CONSERVATION_UNIT_MISMATCH` |
| Share-total mismatch or measured-total closure mismatch | `SETTLEMENT_CLOSURE_FAILURE` |
| Negative amount where an already-declared numeric rule forbids it | That existing numeric-rule failure, before settlement acceptance |
| Otherwise malformed numeric amount | Existing formation or numeric failure |
| Settlement attempt to replace immutable physical measurement | Existing identity/registry owner; no settlement acceptance |
| Omission or bypass of `validate_settlement_closure` | Fail closed with no accepted result |
| Any unlisted failure reordering | Authority-integrity failure |

Negative amounts are not made universally invalid by this repair. A charge,
credit, reversal, or signed allocation remains governed by its existing unit,
sign-convention, quantity, and institutional rules. The repair neither creates
nor weakens a sign rule.

## 9. Failure precedence

Formation remains outside and before validator entry. Within
`validate_settlement_closure`, the exact accepted order remains:

```text
I3_OBJECT_CONTENT_MISMATCH
< IMPLICIT_ABSENCE_FORBIDDEN
< I3_COLLECTION_ORDER_INVALID
< I3_DUPLICATE_MEMBER
< SETTLEMENT_LINK_INVALID
< CONSERVATION_UNIT_MISMATCH
< SETTLEMENT_CLOSURE_FAILURE
< CAUSAL_ATTRIBUTION_UNRESOLVED
< HASH_MISMATCH
```

This repair changes the truth set of the last two affected semantic predicates,
not their positions. In particular, link failure precedes unit failure; unit
failure precedes closure failure; closure failure precedes causal failure; and
causal failure precedes hash failure. No unrelated active failure set or first
failure may change.

## 10. Exact future implementation path scope

A later implementation stage may change exactly these paths and no others:

| State | Path | Exact future purpose |
|---|---|---|
| `MODIFIED` | `src/ebu_framework/settlement.py` | Narrow the causal predicate and complete exact share/closure arithmetic only |
| `MODIFIED` | `tests/framework/test_i3c_declarations.py` | Add static/runtime conformance for the accepted supplemental vectors while retaining historical-vector coverage |
| `NEW` | `tests/framework/fixtures/i3c_settlement_causality_repair_v1.json` | Materialize the separately projected supplemental vector array byte-for-byte |

The future implementation must not modify `causal.py`, `errors.py`,
`__init__.py`, `test_i3_integration.py`, either accepted I-3 JSON contract, the
historical 544-vector fixture, any unrelated module/test/fixture, any package
or lock file, or any authority document. No new dependency is permitted.

The projected supplemental fixture is the validation contract's
`supplemental_vectors` array encoded with the frozen canonical profile and one
final LF. Its identity is:

- vector count: `36`;
- success count: `9`;
- rejected/fail-closed count: `27`;
- canonical bytes: `34418`;
- SHA-256: `f4857cd3b36e2154143617ea7bb4b7cff45cb29292df0fa837effa4c6ec7cb58`;
- unique effective semantic inputs: `36`;
- identical-input collisions: `0`; and
- conflicting outcomes: `0`.

The historical fixture remains byte-identical and separate. The supplemental
fixture neither replaces nor appends bytes to it.

## 11. Complete preservation boundary

The future repair must preserve unchanged:

- physical group measurement and immutable receipt history;
- finite transition, conservation, quote, receipt, and `GroupReceipt`
  semantics;
- lifecycle ordering;
- identities, canonicalization, provenance, governance, and failure-envelope
  construction;
- all historical receipts, artifacts, and results;
- all 544 historical fixture vectors and bytes;
- all unrelated failure identifiers, ordinals, and precedence;
- the complete 219-name root export order and 15-module/91-edge import graph;
- the accepted atomic-generator and parallel-interaction authority;
- wave/phase and electrical-voltage exclusions;
- all books, manuscripts, and PDFs; and
- every predecessor path, mode, object type, Git object, raw byte count, and
  raw SHA-256 in the predecessor manifest.

The complete predecessor projection has `245` rows, `58124` canonical bytes,
and SHA-256
`7352c46cfa77e5ac1a83e94229b78740f776ac49268382294eeee52be9dad74d`.

## 12. Nonclaims and fail-closed behavior

This package does not claim that a settlement amount, marginal value, shadow
price, interaction coefficient, Aumann-Shapley share, provenance link, or
arithmetic closure identifies causality. It does not create entitlement,
liability, fairness, ownership, residual ownership, dispute resolution,
scientific evidence, or empirical validation.

It does not prove an opaque `rule_ref` institutional or an opaque
`evidence_ref` causal. It supplies no causal model, settlement rule, physical
measurement, registry acceptance, authorization, implementation, result, or
scientific conclusion.

Until an independently audited repair is integrated, the current runtime
remains deliberately fail-closed and the affected noncausal-share path remains
unavailable. No compatibility shim, caller-side omission, direct helper call,
monkey patch, alternate validator, fixture-specific branch, or status mismatch
may be used to bypass it.

## 13. Validation and completion boundary

Only static documentation validation is authorized: strict duplicate-key JSON
parsing, independent canonical encodings, hashing, exact arithmetic over
declared synthetic values, complete Git-tree reconstruction, predicate-order
inspection, UTF-8/LF/whitespace/Markdown checks, exact path-scope inspection,
and `git diff --check`.

The independent authority audit is the next possible stage. It has not begun.
Repair implementation, candidate audit, integration, atomic declaration
design, Framework I-4 implementation, book revision, and scientific execution
are separate later stages and remain unbegun.

READY_FOR_INDEPENDENT_I3C_SETTLEMENT_CAUSALITY_REPAIR_AUTHORITY_AUDIT
