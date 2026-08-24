# Post-I-5 Legacy-Test Compatibility Authority Amendment

Status: **prospective documentation-only compatibility authority candidate; unimplemented; unaudited; no project test or scientific execution**.

## 1. Decision and narrow supersession

This package creates prospective authority only for a later exact reconciliation of legacy tests with the accepted additive I-5 implementation candidate. It creates this Markdown file and the three companion JSON files; it edits no existing file and grants no present implementation, test-edit, commit, push, merge, or execution permission.

The mechanical contract is the schema and ordering source, this Markdown is its normative human rendering, the validation contract freezes every affected AST site and neighboring assertion, and the predecessor manifest freezes all 278 base-tree rows. Any disagreement fails closed.

This package narrowly supersedes only the accepted I-5 contract's `compatibility_test_changes_required=false`, its stated reason, and dependent exclusion of existing compatibility tests. Direct static inspection of the eleven-path candidate proves that those premises are false for twelve legacy methods. No scientific, behavioral, failure, export, graph, signature, vector, safety, or nonclaim rule of I-5 is changed.

## 2. Checkpoint and read-only evidence

Local, tracking, and live `framework-v0.1` all resolve to `905d9ee69276a7763b2bdb133bad330751232a42`, tree `22e036252a440d3d6bb963d85914b26315858cd5`. Its ordered parents are `98b9dea874ca57e4ed5f8aaea1584514af0e3823` and accepted I-5 authority feature `c711fe013fea585e78dfc93258a994cea71a3dfa`. Local, tracking, and live I-5 authority refs all resolve to that feature. The new authority branch was absent locally, in tracking refs, and live at the start.

The read-only implementation evidence is `/private/tmp/ebu-framework-i5-implementation-fqOZ12/worktree` on `framework/i-5-event-durability-trace` at `905d9ee69276a7763b2bdb133bad330751232a42` with an empty index. Its exact eleven locks are:

| Path | Mode | Bytes | Raw SHA-256 |
|---|---:|---:|---|
| `src/ebu_framework/events.py` | `100644` | 11258 | `83eef65c47e143b47c855e158b4cb6a46e0bfd9a9296b5f8997d304a7abb515e` |
| `src/ebu_framework/ownership.py` | `100644` | 8691 | `67d1ce391f2b7178153e4d2c973a8c12ee9a92e399db23f06b4c22f333eb3224` |
| `src/ebu_framework/durability.py` | `100644` | 16613 | `2da53d1f3b26c9e8e48e4afe21156404ad838b1c5094e7b8c2e35f35386cb796` |
| `src/ebu_framework/traces.py` | `100644` | 26179 | `835c28128f0446edd8445b8f9828e66ba213d1327be13f6a933d85df99027b8d` |
| `src/ebu_framework/execution.py` | `100644` | 8046 | `b96bbe15130da9bd6d0b91bf74b32ce341f643ee61a9dd3f0cc6306e97f51c82` |
| `src/ebu_framework/hashing.py` | `100644` | 42322 | `4608c40523a8cd07560a28afd4e21a226e81c443985f259a38ab1949f281734a` |
| `src/ebu_framework/faults.py` | `100644` | 15332 | `237e4114ee515b8986e9fb7f3f283f8dc02ede48ffe216413f148f1d2f909cd8` |
| `src/ebu_framework/errors.py` | `100644` | 43640 | `4bc41cbb43f3c05bed579719b07bbe9b077397fbdb8e54538c52263b4993058a` |
| `src/ebu_framework/__init__.py` | `100644` | 23412 | `481daefdd9db22f2fc1e615741068bf9a341a1d1aa04d5562a3a176ec1f5d4ef` |
| `tests/framework/test_event_ownership.py` | `100644` | 24792 | `cfbd5e19cae8f100e2ff1bd3dc2b514ba85541ace7dbcc15c03d48deeaae8c1b` |
| `tests/framework/test_inert_durability.py` | `100644` | 5143 | `6d34c7ec212157b09fd338d8dabb18673374fb42d6d19b72d8a92c82b508d6b6` |

These are evidence locks only. This package does **not** claim that I-5 implementation passed an independent audit.

The eight legacy-test starting locks are:

| Path | Mode | Git blob | Bytes | Raw SHA-256 |
|---|---:|---|---:|---|
| `tests/framework/test_atomic_declarations.py` | `100644` | `1f5ba06d3c6fe6b947362d9a75d126bf5e66e0c3` | 79614 | `2d6061f90fdcaf72e7b45b5434fc4fc294302d0ba07e2e80d2a2dafd1dd8995b` |
| `tests/framework/test_i3_integration.py` | `100644` | `3fec019497106039a7432199c0b4bc077a4d777f` | 46128 | `9aac14f63ad7a4edb8bc52766b93e1b7b638fc5837fe7cbe0b5991dcceefb699` |
| `tests/framework/test_i3a_declarations.py` | `100644` | `2b481b6f94f4907da094c3692e5eef925ef4e83a` | 22058 | `208bfc48888e428be4dccd82767f5d8b1ce7f2e6664014d40c386c23c580ad4b` |
| `tests/framework/test_i3b_declarations.py` | `100644` | `38fb8a20a799100a6d5a7245f7238349b045b0e7` | 19299 | `57651b19a2050ab0df068398042d30ae91a8560ff9c8df04949294b4805c4e13` |
| `tests/framework/test_i3c_declarations.py` | `100644` | `ab61f4c5f38ad84a9b848667c1f57d2742f8299f` | 50972 | `4356f6a75c08a1bca1f0a36392434f1ce760e89b27368356593316d2c5428409` |
| `tests/framework/test_i3d_declarations.py` | `100644` | `106b48ec5cf24b8c2e751f3a2c0ad94d38eca978` | 41797 | `0c32690a41485339e97a4f0c07f3c53ffffba2173fcb90575c9d0cfcea706824` |
| `tests/framework/test_interaction_declarations.py` | `100644` | `5e0019123fab7a48a31b788917043fd979029fc3` | 107519 | `f54626bcdc15de08f4c45ec21b355361dff263d5a3941f454a5b4f2a1fa090d0` |
| `tests/framework/test_primitives_envelopes.py` | `100644` | `d15e4d78a9410b11bb7887f93cde00f56957e3a9` | 51789 | `7e00045ea6f97467853a80857be13af77e849a8d743d1126ecd3ba80d24dd3a2` |

## 3. Exact reconciled surface

The exact failure and root slices are:

```text
Failures: [0:53] I-1/I-2 | [53:88] I-3 | [88:102] D1 | [102:124] D2 | [124:185] I-4 | [185:227] I-5
Exports:  [0:127] I-1/I-2 | [127:219] I-3 | [219:237] D1 | [237:261] D2 | [261:309] I-4 | [309:391] I-5
```

Every historical slice retains its exact values, order, length, LF byte count, and SHA-256 from the accepted post-I-4 contract. The I-5 failure suffix is 42 values, 1,103 LF bytes, SHA-256 `b70fccfca86d4b7118bf80593794b40a2ad8f3848dbe4ff0963741e4e56f3681`; the current 227-code projection is 5,997 bytes, SHA-256 `4cb1daceb30c0f106e7ba288980d379da2403236593948b4be47247704555ae4`.

The I-5 root suffix is 82 values, 1,787 LF bytes, SHA-256 `0b593d0d045da2ce3ffb46bc192ceb1b7aea58d2212bb14981ac716dbd02f508`; the current 391-name projection is 8,625 bytes, SHA-256 `f27ed982d7e646be870404239ad617d181df8276728f9a3f1fc878c5bbfa46db`.

The root source retains the exact 309-name historical static assignment and appends the exact 82-name I-5 suffix with `__all__ +=`. Exactly 68 I-5 names are eager top-level relative imports. The exact 14 `execution` module exports are the only lazy names, named by `_I5_EXECUTION_EXPORTS` and resolved by `__getattr__`; their exact module order is mechanical in the contract.

The exact package graph is 34 modules, 192 direct edges, zero cycles, and a 2,619-byte canonical projection with SHA-256 `96055fd0d2dc4dd0f3bcbf2cb169967c7bceffc8d70b50252e154b5649c38bcb`. The exact extension graph is 26 modules, 171 direct edges, zero cycles, and a 2,276-byte canonical projection with SHA-256 `91968c5320599969fb29824dfed009174e2c3de6136d6aaa59eb36f2ef439909`.

The 34 exact module-local export tuples contain 390 symbol occurrences. Their 9,927-byte canonical projection has SHA-256 `94ba72bd338598f463e0f638407314533cac8d3174db92c27bc05bbadd6ec765`.

All 155 predecessor signature rows remain in their accepted order and projection: 55,808 canonical bytes, SHA-256 `e5b7a1157aac297d48f2058ca308cfa7c5bc9c3fd1c6040fd68369e27a2ddd2b`. I-5 appends exactly 50 type rows and 32 callable rows: 62,204 canonical bytes, SHA-256 `24898c5185da5fb0af7b4b19d46569ab38eb0c4c811c81a2f543a7332a3cd8bc`. The exact 237-row aggregate is 118,010 canonical bytes, SHA-256 `083a429b0fd36dda80d62a9113fe81e758c17c210385d10e76dc2c2a80dbdaba`. Sorting, regrouping, segment reordering, and order-insensitive acceptance are forbidden.

A legacy test may no longer treat 185 failures, 309 exports, or 29 modules as terminal. It must continue proving those exact post-I-4 prefixes and then prove the exact I-5 suffix and current aggregate.

## 4. Twelve methods and fourteen observed instances

The fourteen reported observed failures are independently reproduced without importing framework/provider modules or running tests:

```text
10 ordinary first-reached failures
+ 2 predecessor methods × 2 changed-path subtests (hashing.py and faults.py)
= 14 observed failure instances
```

Static inspection finds 47 distinct stale AST assertion sites and 49 stale evaluation instances; 35 are masked by earlier failures. The accounting is `14 first-reached + 35 masked = 49 evaluations across 47 AST sites`: the eight changed-path loop evaluations previously attributed to four shared hashing/faults sites are instead classified across four hashing sites and four distinct faults sites. Masked sites are still frozen for complete reconciliation but do not increase the observed count.

| ID | Source path | Stable method | Stale AST sites | Stale evaluations | Observed failures |
|---|---|---|---:|---:|---:|
| `M01` | `tests/framework/test_primitives_envelopes.py` | `FrameworkI2SourceAuditTests::test_ast_import_export_and_reachability_contract` | 2 | 2 | 1 |
| `M02` | `tests/framework/test_i3_integration.py` | `I3IntegrationTests::test_root_api_modules_import_graph_and_failure_inventory` | 7 | 9 | 1 |
| `M03` | `tests/framework/test_i3a_declarations.py` | `I3ADeclarationsTests::test_i3a_runtime_and_static_inventory` | 3 | 3 | 1 |
| `M04` | `tests/framework/test_i3b_declarations.py` | `I3BDeclarationsTests::test_i3b_runtime_and_static_inventory` | 3 | 3 | 1 |
| `M05` | `tests/framework/test_i3c_declarations.py` | `I3CDeclarationsTests::test_i3c_runtime_and_static_inventory` | 3 | 3 | 1 |
| `M06` | `tests/framework/test_i3d_declarations.py` | `I3DDeclarationsTests::test_i3d_runtime_and_static_inventory` | 3 | 3 | 1 |
| `M07` | `tests/framework/test_atomic_declarations.py` | `AtomicDeclarationContractTests::test_exact_failure_and_root_export_inventories` | 6 | 6 | 1 |
| `M08` | `tests/framework/test_atomic_declarations.py` | `AtomicDeclarationContractTests::test_existing_public_signatures_and_predecessor_bytes_are_preserved` | 4 | 4 | 2 |
| `M09` | `tests/framework/test_atomic_declarations.py` | `AtomicDeclarationContractTests::test_no_d2_surface_or_prohibited_reachability` | 1 | 1 | 1 |
| `M10` | `tests/framework/test_interaction_declarations.py` | `InteractionDeclarationContractTests::test_exact_failure_and_root_export_inventories` | 6 | 6 | 1 |
| `M11` | `tests/framework/test_interaction_declarations.py` | `InteractionDeclarationContractTests::test_exact_imports_graphs_and_inertness` | 5 | 5 | 1 |
| `M12` | `tests/framework/test_interaction_declarations.py` | `InteractionDeclarationContractTests::test_predecessor_signatures_and_d1_bytes_are_preserved` | 4 | 4 | 2 |

The predecessor methods have separate per-path first-failure mappings: M08 reaches `faults.py` site `A44` at line 1745 and `hashing.py` site `A28` at line 1749; M12 reaches `faults.py` site `A46` at line 2301 and `hashing.py` site `A42` at line 2305. A single shared first-stale line for either method is forbidden.

Each method retains exact historical-prefix proof, adds the applicable I-5 suffix/current proof, preserves every neighboring assertion under its frozen AST projection, forbids deletion/skip/mute/expected-failure/metadata-only or broad bypasses, and is expected to pass only with exact reconciliation.

## 5. Assertion-level disposition

| Site | Method | Base lines | Stale evaluations | Observed failures | Required replacement |
|---|---|---:|---:|---:|---|
| `A01` | `M01` | `443:443` | 1 | 1 | Retain exact eager import/export equality for the accepted eager surface.; Recognize only the exact 14-name _I5_EXECUTION_EXPORTS lazy set and prove those names are the execution-owned part of the 82-name I-5 suffix.; Reconstruct the complete 391-name root order from the 309-name assignment plus exact 82-name += suffix. |
| `A02` | `M01` | `518:524` | 1 | 0 | Retain the exact 29-module post-I-4 prefix and add the exact five I-5 modules.; Require 34 unique relative module imports and the exact current module order. |
| `A03` | `M02` | `523:523` | 1 | 1 | Apply all post-I-4 expectations to root_exports[:309], not to the later suffix or whole aggregate.; Require root_exports[309:391] to equal the exact I-5 suffix and require the exact 391-name current projection. |
| `A04` | `M02` | `532:532` | 1 | 0 | Apply all post-I-4 expectations to root_exports[:309], not to the later suffix or whole aggregate.; Require root_exports[309:391] to equal the exact I-5 suffix and require the exact 391-name current projection. |
| `A05` | `M02` | `533:533` | 1 | 0 | Apply all post-I-4 expectations to root_exports[:309], not to the later suffix or whole aggregate.; Require root_exports[309:391] to equal the exact I-5 suffix and require the exact 391-name current projection. |
| `A06` | `M02` | `537:537` | 1 | 0 | Apply all post-I-4 expectations to root_exports[:309], not to the later suffix or whole aggregate.; Require root_exports[309:391] to equal the exact I-5 suffix and require the exact 391-name current projection. |
| `A07` | `M02` | `726:726` | 1 | 0 | Apply the I-4 suffix lock to failures[124:185] and the post-I-4 aggregate lock to failures[:185].; Require failures[185:227] to equal the exact I-5 suffix and require the exact 227-code current projection. |
| `A08` | `M02` | `735:735` | 2 | 0 | Apply the I-4 suffix lock to failures[124:185] and the post-I-4 aggregate lock to failures[:185].; Require failures[185:227] to equal the exact I-5 suffix and require the exact 227-code current projection. |
| `A09` | `M02` | `736:736` | 2 | 0 | Apply the I-4 suffix lock to failures[124:185] and the post-I-4 aggregate lock to failures[:185].; Require failures[185:227] to equal the exact I-5 suffix and require the exact 227-code current projection. |
| `A10` | `M03` | `441:441` | 1 | 1 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A11` | `M03` | `442:442` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A12` | `M03` | `448:451` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A13` | `M04` | `422:422` | 1 | 1 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A14` | `M04` | `423:423` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A15` | `M04` | `424:427` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A16` | `M05` | `1086:1089` | 1 | 1 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A17` | `M05` | `1094:1094` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A18` | `M05` | `1095:1098` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A19` | `M06` | `923:926` | 1 | 1 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A20` | `M06` | `931:931` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A21` | `M06` | `932:935` | 1 | 0 | Retain exact historical failure slices [0:53], [53:88], [88:102], [102:124], and [124:185].; Add exact I-5 slice [185:227] and exact 227-code current order, length, LF byte count, and SHA-256. |
| `A22` | `M07` | `1565:1565` | 1 | 1 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A23` | `M07` | `1573:1573` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A24` | `M07` | `1586:1592` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A25` | `M07` | `1594:1594` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A26` | `M07` | `1605:1605` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A27` | `M07` | `1618:1624` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A28` | `M08` | `1749:1749` | 1 | 1 | For `hashing.py`, retain its existing historical reconstruction and post-I-4 current-row route; separately compare current bytes, mode, size, and SHA-256 with the exact frozen I-5 candidate identity; permit no broad exclusion or generic later-stage bypass. |
| `A29` | `M08` | `1760:1763` | 1 | 0 | For `hashing.py`, retain its existing historical reconstruction and post-I-4 current-row route; separately compare current bytes, mode, size, and SHA-256 with the exact frozen I-5 candidate identity; permit no broad exclusion or generic later-stage bypass. |
| `A30` | `M09` | `1787:1787` | 1 | 1 | Retain exact D2 and all post-I-4 root slices through [261:309].; Add exact I-5 [309:391] and exact 391-name aggregate while leaving reachability assertions unchanged. |
| `A31` | `M10` | `1844:1844` | 1 | 1 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A32` | `M10` | `1845:1845` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A33` | `M10` | `1860:1866` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A34` | `M10` | `1878:1878` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A35` | `M10` | `1879:1879` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A36` | `M10` | `1894:1900` | 1 | 0 | Retain every historical failure slice through [124:185] and root slice through [261:309] with existing prefix projections.; Add exact I-5 failure [185:227] and root [309:391] suffixes plus exact whole-current projections. |
| `A37` | `M11` | `1951:1953` | 1 | 1 | Retain the exact 29-module/152-edge package prefix graph and 21-module/131-edge extension prefix graph.; Add only events, ownership, durability, traces, and execution with their exact edges; require 34/192 and 26/171 current graphs and zero cycles. |
| `A38` | `M11` | `1954:1954` | 1 | 0 | Retain the exact 29-module/152-edge package prefix graph and 21-module/131-edge extension prefix graph.; Add only events, ownership, durability, traces, and execution with their exact edges; require 34/192 and 26/171 current graphs and zero cycles. |
| `A39` | `M11` | `1958:1961` | 1 | 0 | Retain the exact 29-module/152-edge package prefix graph and 21-module/131-edge extension prefix graph.; Add only events, ownership, durability, traces, and execution with their exact edges; require 34/192 and 26/171 current graphs and zero cycles. |
| `A40` | `M11` | `1975:1975` | 1 | 0 | Retain the exact 29-module/152-edge package prefix graph and 21-module/131-edge extension prefix graph.; Add only events, ownership, durability, traces, and execution with their exact edges; require 34/192 and 26/171 current graphs and zero cycles. |
| `A41` | `M11` | `2062:2062` | 1 | 0 | Retain the exact 29-module/152-edge package prefix graph and 21-module/131-edge extension prefix graph.; Add only events, ownership, durability, traces, and execution with their exact edges; require 34/192 and 26/171 current graphs and zero cycles. |
| `A42` | `M12` | `2305:2305` | 1 | 1 | For `hashing.py`, retain its existing historical reconstruction and post-I-4 current-row route; separately compare current bytes, mode, size, and SHA-256 with the exact frozen I-5 candidate identity; retain the complete signature proof and permit no broad exclusion. |
| `A43` | `M12` | `2316:2319` | 1 | 0 | For `hashing.py`, retain its existing historical reconstruction and post-I-4 current-row route; separately compare current bytes, mode, size, and SHA-256 with the exact frozen I-5 candidate identity; retain the complete signature proof and permit no broad exclusion. |
| `A44` | `M08` | `1745:1745` | 1 | 1 | For `faults.py`, add the exact I-5 reconciliation entry; reconstruct and validate the historical manifest blob, then separately compare current bytes, mode, size, and SHA-256 with the frozen I-5 candidate identity; never compare the current I-5 payload directly with the historical size or hash. |
| `A45` | `M08` | `1750:1753` | 1 | 0 | For `faults.py`, add the exact I-5 reconciliation entry; reconstruct and validate the historical manifest blob, then separately compare current bytes, mode, size, and SHA-256 with the frozen I-5 candidate identity; never compare the current I-5 payload directly with the historical size or hash. |
| `A46` | `M12` | `2301:2301` | 1 | 1 | Apply the exact `faults.py` historical/candidate split used by M08, retain the complete signature proof, and permit no wildcard, directory, broad excluded-set, or generic later-stage bypass. |
| `A47` | `M12` | `2306:2309` | 1 | 0 | Apply the exact `faults.py` historical/candidate split used by M08, retain the complete signature proof, and permit no wildcard, directory, broad excluded-set, or generic later-stage bypass. |

The validation contract records for every site the exact historical source, source and AST identities, why only the terminal premise is superseded, the exact replacement invariant, first-reached/masked accounting, the neighboring-assertion seal, prohibited weakening, and expected result.

## 6. Historical bytes and exact boundary

Historical predecessor blobs remain immutable Git evidence. A later test must reconstruct them at their historical commits. Current working-tree equality remains mandatory for every path outside the exact accepted I-5 boundary.

The I-5 candidate may modify only `src/ebu_framework/hashing.py`, `src/ebu_framework/faults.py`, `src/ebu_framework/errors.py`, and `src/ebu_framework/__init__.py`, and add only the five I-5 modules plus two I-5 tests. The two repeated legacy predecessor loops already exclude only `errors.py` and `__init__.py`. Their new reconciliation is limited to exact, separate `hashing.py` and `faults.py` routes; neither file may simply be added to a broad excluded set.

For `hashing.py`, both M08 and M12 retain the existing post-I-4 historical reconstruction and accepted-current-row proof. The prospective reconciliation adds a separate candidate row for the current working file and requires mode `100644`, 42,322 bytes, and SHA-256 `4608c40523a8cd07560a28afd4e21a226e81c443985f259a38ab1949f281734a`. It must not replace either historical proof or compare the I-5 payload directly with an obsolete row.

For `faults.py`, both methods add the exact I-5 reconciliation entry that reconstructs historical Git object `3aded2e1b639fad96db6dcc9c220ecfe57288653` and continues validating mode `100644`, 12,750 bytes, and SHA-256 `bfcb44b528e7ea3ad0c4e4997f08b21cb5ee739654d46f91a8f9062d55dabf5e` against the historical manifest. A separate candidate row then requires current mode `100644`, 15,332 bytes, and SHA-256 `237e4114ee515b8986e9fb7f3f283f8dc02ede48ffe216413f148f1d2f909cd8`. The current I-5 payload must never be compared directly with the historical byte count or hash.

Only the exact per-path reconciliation-row and candidate-row support flow needed for these routes may change. The genuinely unaffected neighbor assertions remain AST-identical and in relative order: M08 seals 7 assertions under a 1,726-byte LF projection with SHA-256 `5a55848d9eede6bf515737582b4eb708f2320698c1ef29a09853fdb4ccb65158`; M12 seals 22 assertions under a 7,919-byte LF projection with SHA-256 `71a8a5da5d5a39c1ec9c8af63bee64fd01b2465e4e4b9f8ba90152c1ccd1d63e`. No directory exclusion, wildcard, broad excluded-set, or generic later-stage bypass is permitted.

A later combined candidate may contain exactly the accepted eleven I-5 paths plus the eight named legacy tests: 19 paths total. The eleven I-5 paths must match the frozen candidate identities. No production path beyond those eleven, no twentieth path, and no test deletion, skip, mute, weakening, expected failure, or metadata-only conversion is authorized.

All 278 base rows—including every non-I-5 predecessor byte and mode—are frozen in the predecessor manifest. Four existing I-5-modified paths and eight starting legacy tests are the only base paths that a separately authorized combined implementation may change; seven I-5 paths are exact additions; the other 266 base paths remain byte-identical and mode-identical.

## 7. Static acceptance and nonclaims

Acceptance is static only and requires strict duplicate/non-finite/trailing-data rejecting JSON parses; byte-identical output from independent Python and Ruby canonical encoders; two independent 278-row predecessor reconstructions; source/AST reconstruction of failures, exports, graphs, module exports, and all signature segments; exact 12-method/47-site/49-evaluation/14-instance accounting with 35 masked evaluations; the four per-path predecessor first-failure mappings and separate `hashing.py`/`faults.py` routes; unaffected-neighbor seals; exact 19-path closure; Markdown/JSON agreement; scope and text-integrity utilities; `git diff --check`; exactly four untracked authority files; empty index; no residue; and byte-identical before/after locks for both excluded worktrees.

This authority does not claim an independent I-5 implementation audit. It changes no model, simulation, durability backend, SQLite operation, scientific execution, result, book, manuscript, rendering, recovery, finalization, or publication. No framework/provider module may be imported and no project test may run during this stage.

## 8. Lifecycle and completion

1. post-I-5 compatibility authority drafting;
2. independent post-I-5 compatibility authority audit;
3. separately authorized authority commit and feature push;
4. independent authority integration;
5. separately authorized exact 19-path combined implementation;
6. independent combined implementation audit;
7. separately authorized implementation commit/push/integration; and
8. only then clean broad discovery and accepted I-5 evidence.

No step authorizes its successor. This task completes only the prospective draft if all static checks pass. The next possible stage is an independent authority audit and has not begun.

`READY_FOR_FRESH_INDEPENDENT_POST_I5_LEGACY_TEST_COMPATIBILITY_AUTHORITY_REAUDIT`
