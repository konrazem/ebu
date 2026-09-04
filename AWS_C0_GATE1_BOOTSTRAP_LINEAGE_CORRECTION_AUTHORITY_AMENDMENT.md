# AWS-C0 Gate 1 Bootstrap-Lineage Correction Authority Amendment

## 1. Status and boundary

This amendment is a repository-local, non-scientific correction authority. It
preserves every earlier AWS-C0 authority, packet, authorization, closure, and
failure record as historical evidence. It authorizes no AWS call, credential
or session use, CloudFormation action, scientific execution, commit, push,
merge, publication, deployment, or release.

Its sole purpose is to correct the prospective Gate 1 lineage contract after
the successful Gate 0 bootstrap and later preparation-session renewal acquired
different schema versions from the failed original Gate 0 attempt.

## 2. Sealed diagnosis

The committed Gate 1 packet-v3 plan requires three canonical candidates with
kinds `aws_c0_operator_bootstrap_packet/v1`,
`aws_c0_operator_bootstrap_authorization/v1`, and
`aws_c0_operator_bootstrap_closure/v1`. The only v1 closure has complete-byte
SHA-256 `5250c649ca14685f46f627504c7014793b479e4b5c43d4bda8246ad8ebc27d4b`
and disposition `AWS_C0_OPERATOR_BOOTSTRAP_FAIL`, with failure
`STS_SET_SOURCE_IDENTITY_ACCESS_DENIED` and no preparation operator identity.
It cannot support a Gate 1 preparation packet.

The actual successful bootstrap is the exact V5 chain:

1. `aws_c0_operator_bootstrap_packet/v4`, SHA-256
   `d77b2cd6e5301dd69f9c10447e1c1030e369852522944b1ff7c9ccbcb19b4c9c`;
2. `aws_c0_operator_bootstrap_authorization/v5`, SHA-256
   `7905547086c37e44d7c3d6f1c55ca99cf97acc73a157a3e15580e6187e1ae109`;
3. `aws_c0_operator_bootstrap_closure/v5`, SHA-256
   `0a1b93360e8b0ae685e33bfa5f45924dee6f1ebe2e1905ff388690c5182d2f5f`,
   disposition `AWS_C0_OPERATOR_BOOTSTRAP_PASS`.

The issued preparation session was produced by the exact V6 renewal chain:

4. `aws_c0_operator_session_renewal_packet/v1`, SHA-256
   `7866fb59d3eb31a6c13c294102d291ab4fbe483030b49970a66b146fcf45f4e7`;
5. `aws_c0_operator_session_renewal_authorization/v1`, SHA-256
   `7030750a6cd3db5120baeae48bb85c1259cc2169758c75d898e6a83d53c1b9a0`;
6. `aws_c0_operator_session_renewal_closure/v1`, SHA-256
   `c9a8eaf846569363cb4f405670b48ee85a891498f48f690f5145601ccde5388b`.
   This independently approved sealed closure binds predecessor closure
   SHA-256
   `1391085e39d1809e67ed4b3139634764d87d5824c28e7c517ff940a2ec7b428f`.

Relabeling any of these records as v1, rewriting the failed v1 record, or
omitting part of either successful three-record chain is forbidden.

## 3. Corrected lineage and arithmetic

The corrected preparation packet carries six canonical lineage candidates in
the exact order above. Each candidate binds its complete canonical record
bytes, exact existing schema kind, complete-byte SHA-256 identity, and a
prospective content-addressed publication target. No candidate contains a
predicted VersionId or PutObject receipt.

The complete pre-live set therefore increases from 21 to 24 objects:

| Class | Count |
|---|---:|
| implementation artifacts | 8 |
| successful V5 bootstrap records | 3 |
| successful V6 renewal records | 3 |
| preparation packet and authorization | 2 |
| private snapshot, authority audit, static validation | 3 |
| cost model and closure seed | 2 |
| launch, preparation closure, live packet | 3 |
| **total** | **24** |

The live packet consequently binds exactly 23 predecessor object receipts and
is the twenty-fourth pre-live object. No hidden lineage capsule, receipt
substitution, identity-only omission, or arithmetic compatibility alias is
permitted.

The corrected ordered kind sequence is:

1. eight occurrences of `aws_c0_implementation_artifact/v1`;
2. `aws_c0_operator_bootstrap_packet/v4`;
3. `aws_c0_operator_bootstrap_authorization/v5`;
4. `aws_c0_operator_bootstrap_closure/v5`;
5. `aws_c0_operator_session_renewal_packet/v1`;
6. `aws_c0_operator_session_renewal_authorization/v1`;
7. `aws_c0_operator_session_renewal_closure/v1`;
8. `aws_c0_preparation_packet/v4`;
9. `aws_c0_preparation_authorization/v3`;
10. `aws_c0_private_infrastructure_snapshot/v1`;
11. `aws_c0_audit_static_handoff_authority_audit/v4`;
12. `aws_c0_material_runtime_static_validation/v4`;
13. `aws_c0_cost_model/v2`;
14. `aws_c0_closure_seed/v1`;
15. `aws_c0_launch_request/v5`;
16. `aws_c0_preparation_closure/v4`; and
17. `aws_c0_live_packet/v5`.

## 4. Version preservation and direct upgrades

The accepted packet-v3, preparation-authorization-v2, launch-v4,
preparation-closure-v3, and live-packet-v4 schemas remain immutable. The
corrected meanings use packet-v4, preparation-authorization-v3, launch-v5,
preparation-closure-v4, and live-packet-v5. Any later record that directly
constrains one of these kinds must receive its own versioned upgrade before it
is used. This amendment authorizes the bounded local implementation and
validation of those upgrades only in the exact six modified paths sealed below;
it does not authorize AWS or scientific use.

The directly affected live authorization therefore advances from v4 to v5.
The exact downstream version map in the correction contract additionally
closes the controller chain through source-sidecar-v4, SSM request/identity-v2,
attempt-claim-v2, and start-receipt-v6, and the finalizer chain through
safe-close-v4, resource-use-v2, finalizer-v3, cost-v3, retrieval-v5,
final-manifest-v5, publication-observation-v3, final-S3-aggregate-v2,
closure-response-v4, and publication-upgrade-binding-v5.
The additive negative registry uses
`aws_c0_static_negative_case_execution/v5` and preserves all 352 historical
cases while appending exactly `C0-G1-LINEAGE-N01` through
`C0-G1-LINEAGE-N06`, for 358 cases total.

The future preparation authorization statement must receive a new statement
version and bind the complete packet-v4 SHA-256, implementation commit and
tree, exact session and role controls, `pre_live_object_count=24`, accounting
end, and cost ceiling. It remains preparation-only and must deny live
execution, replay, delete, terminate, and scientific execution.

## 5. Canonical and validation requirements

All correction evidence and future control records are duplicate-key-free
UTF-8 NFC JSON, recursively ordered by Unicode code point, compact with comma
and colon separators, integer-only and finite, with no trailing data or final
line feed. Every identity has exactly `kind`, `sha256`, and `value`, with the
last two equal. Canonical candidates hash their complete decoded canonical
bytes; the decoded record schema must equal the candidate identity kind.

Local validation must positively prove the exact six-record order, all six
complete-byte hashes, the V5 PASS disposition, V6 credential issuance and
exact V5-closure predecessor binding, the 24/23 arithmetic, the version-upgrade
map, no mutation of historical schemas, and zero scientific counters. It must
negatively refuse the failed v1 closure, relabeling, omission, duplication,
reordering, a 21/20 compatibility value, a hidden capsule, digest mismatch,
noncanonical bytes, predicted AWS receipts, AWS access, and scientific work.

## 6. Authorized local implementation scope

This authority directly permits the bounded local implementation and validation
of exactly twelve paths: creation of the six additive authority-package files
and modification of the six existing implementation paths named in
`aws_c0_gate1_bootstrap_lineage_correction_implementation_path_manifest.json`.
No other addition, modification, deletion, or rename is permitted.
CloudFormation is not part of this correction because the defect is confined
to evidence lineage, schema versions, exact record counts, and their local and
runtime validation.

`AWS_C0_GATE1_BOOTSTRAP_LINEAGE_CORRECTION_AUTHORITY_CANDIDATE_COMPLETE`
