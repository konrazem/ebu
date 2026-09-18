# Local Gaussian programme — baseline decision

Status: **adopted for repository and documentation reconciliation only**.

This decision preserves existing scientific history and prospective work. It
does not accept a Gaussian study protocol, authorize a framework import or
implementation, or authorize model execution. The governing scope is indexed in
[CURRENT_SCIENTIFIC_AUTHORITY.md](CURRENT_SCIENTIFIC_AUTHORITY.md).

## 1. Scope and evidence date

The source inspection began on 2026-09-18 in the existing checkout at
`/Users/konrad.grzyb/code/ebu`. Both author-supplied programme handovers were read
completely. Their instructions to continue into implementation and experiments
are superseded for this task by the author's explicit stopping point:
reconcile the project and book architecture, clean the repository, then stop
before book generation or Claude's later test-environment implementation.

The initial branch was `v3.0-local-ebu-foundation`, at
`36373aa44c2fe065ed54c186c8037e541805f87f`, with tree
`6edbcff54654b550e8c9042aee636184ace75b50`. It was 18 commits ahead of its
cached tracking reference and contained known uncommitted Claude work.

The author explicitly authorized a labelled local checkpoint and separate local
reconciliation commits, with no push. That checkpoint is:

- commit: `924a4d9a801b96f265aa3f0adc40e2c09063e469`;
- tree: `8f07ec999b40248ac0edcf25faf0bb6f92ef4705`;
- parent: `36373aa44c2fe065ed54c186c8037e541805f87f`;
- subject: `Preserve Claude prospective harness and design checkpoint`.

The checkpoint records provenance and recoverability. It does **not** promote
the preserved candidate documents, code or reported checks into accepted
scientific authority, registered results or execution permission.

## 2. Inspected branch coordinates

Remote-tracking references in this table are **cached local references**, not a
fresh query of GitHub. No fetch, pull or network Git command was performed.
The exact commits, rather than potentially moving branch names, are the source
locks for this decision.

| Reference at inspection | Commit | Root tree |
| --- | --- | --- |
| `main` | `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0` | `1e976ce5b308752c36a688698f6533e7f2962ca4` |
| `origin/main` | `660d6e5a56cb096fe6d1e4d202f592155d982c79` | `1e3f02e4efc2ce5b0ca3c15fb8a95c3df98c277d` |
| `framework-v0.1` | `4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e` | `591ad275116e9dc28bf0443aae80142e5ad86ec5` |
| `origin/framework-v0.1` | `a4af44afd3c878311ee373bc19e3be14b2aacec5` | `619b59875cfa4c6ad4a7da4f6a1aaaa465d3f23a` |
| Initial `v3.0-local-ebu-foundation` | `36373aa44c2fe065ed54c186c8037e541805f87f` | `6edbcff54654b550e8c9042aee636184ace75b50` |
| `origin/v3.0-local-ebu-foundation` | `f2c60e1f34126dfc976674187c9ca1d0ceb06ba8` | `adbd022a46d7f291bde014dff9c742b24574d63f` |

### 2.1 Ancestry and divergence

For each pair, the two counts are commits unique to the left and right side,
respectively; they are not counts of changed files.

| Pair | Merge base | Left-only / right-only |
| --- | --- | --- |
| local `main` / local `framework-v0.1` | `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0` | 0 / 141 |
| local `main` / initial V3 | `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0` | 0 / 74 |
| local framework / initial V3 | `8793bda07ff7470c6362d2ef3b21c41825ae98ed` | 86 / 19 |
| cached origin main / initial V3 | `8793bda07ff7470c6362d2ef3b21c41825ae98ed` | 135 / 19 |
| cached origin framework / initial V3 | `8793bda07ff7470c6362d2ef3b21c41825ae98ed` | 249 / 19 |
| cached origin main / cached origin framework | `fb9ae7b6dae14550a702e060600132faec539eca` | 1 / 115 |

Local `main` is 190 commits behind cached `origin/main`. Local
`framework-v0.1` is 163 commits behind its cached origin reference. Thus neither
local branch name is a reliable proxy for the newest locally available source.

## 3. What the candidate bases contain and lack

### Initial V3 plus checkpoint

The V3 lineage includes the Gate 1D-C result/finalization commit `f2c60e1`, the
18 subsequent local commits and now the author-approved Claude checkpoint.
Its 19 commits after the common `8793bda` ancestor include:

- Gate 1D-C execution receipt, start record, manifest, summary, stdout and trace;
- D5 software benchmark implementation and records, not Gaussian scientific
  evidence;
- the SD-01–14 reconstructed register and SD-03 oracle/readiness work;
- conservative-world and long-horizon candidate designs and implementations;
- future-books changes and the preserved, still prospective controller/world
  harness work (the harness itself is in the additional checkpoint commit,
  not one of the 19 pre-checkpoint V3-only commits).

It does not track `src/ebu_framework` or `stage_e_harness`. Their absence from
this checkout does not mean that the repository object database lacks them.

### Local main

Local `main` ends at the V2.9 integration at `e1c6000`. It lacks the subsequent
V3, framework and current prospective work. It is not a suitable reconciliation
base merely because its branch name is `main`.

### Local framework and cached origin main/framework

The framework lineages contain the typed framework, atomic/interactions
declarations, bridge, conservation and dynamic-coordination foundations,
framework amendments and tests. The newer cached origin framework additionally
contains Stage D/E/F authority and harness work not found on the older local
framework tip. These sources have their own prospective/implemented/evidence
statuses; their presence is not execution authorization.

These framework lineages diverged before Gate 1D-C finalization on V3. Moving the
checkout to them without an explicit integration would remove the 19 V3-only
commits' files from the working tree and omit the new Claude checkpoint. This
would not erase the Git objects, but it would be a materially incomplete active
working base.

## 4. Exact framework-core source relationship

The package subtrees provide a useful narrower comparison:

| Source | `src/ebu_framework` tree object |
| --- | --- |
| local framework `4ab6f9ca…` | `b53a6f7baaf8277c4392d73e284fc526c6ac1261` |
| cached origin main `660d6e5a…` | `4de85ed2935d1c35bdcc0f1259f0acb2df569fdd` |
| cached origin framework `a4af44af…` | `4de85ed2935d1c35bdcc0f1259f0acb2df569fdd` |

The two cached origin references have byte-identical framework package trees.
Their surrounding programmes are not identical. The framework specification
blob at all three framework-bearing coordinates is
`fbcceb0ce05f6d98f345658cf4cd6a86f1789334`.

The source lock for the reuse audit is
`a4af44afd3c878311ee373bc19e3be14b2aacec5`; the equality above is an independent
cross-check, not a claim that all Stage D/E/F or book documents match across
branches. The companion
[framework decision](LOCAL_GAUSSIAN_EBU_FRAMEWORK_DECISION.md) records the actual
implementation and authority distinctions.

## 5. Adopted reconciliation base

Use the checkpoint `924a4d9a801b96f265aa3f0adc40e2c09063e469` as the preserved
baseline within the dedicated local reconciliation branch:

`codex/local-gaussian-reconciliation`.

This choice preserves the entire existing checkout lineage, immutable result
records and prospective work without pretending that the framework sources
already belong to that lineage. The current authority index may point to
source-locked external-lineage documents. Such a pointer is not a merge, an
imported implementation, accepted evidence, or an execution grant.

No wholesale merge, cherry-pick or replacement with the framework branch is part
of this stage. A later explicitly authorized integration must inspect exact
source, dependency, API, test and authority scopes. The old result engines and
their source identities remain reproducible at their original commits.

The current reconciliation may supersede old prospective *planning roles*, but
must not rewrite historical results or claim that those results used Gaussian
geometry or the new capacity mechanism.

## 6. Why no accepted evidence is lost

1. The dedicated branch descends from the complete initial V3 history.
2. Claude's previously uncommitted work has an explicit labelled checkpoint.
3. Framework and programme sources stay recoverable at exact committed
   coordinates; no branch deletion or history rewrite is required.
4. Historical evidence is retained with its original model and interpretation.
5. New programme status is expressed through an index and reconciliation
   documents, not retrospective edits of old execution records.
6. No local or remote commit is treated as a scientific acceptance merely
   because it is committed.

## 7. Validation class, limits and stopping point

Evidence for this decision consists of read-only Git status, reference/tree
resolution, merge-base and left/right counts, first-parent history, path/tree
comparison and targeted source inspection. No software suite or scientific
model was run during the baseline audit. Previous reported test counts were
not revalidated.

The selected base is trustworthy for the authorized documentation reconciliation;
it is not a pre-execution certification. The active framework is **source-locked
for reuse planning, not imported into this checkout**. Scientific implementation,
book generation, Stage A and Stage B remain unbegun in this task.

The author-approved checkpoint and subsequent reconciliation commits are local
only. Final branch/commit cleanliness is reported by the stage controller after
the separate documentation commits; this document does not predict their SHAs.
