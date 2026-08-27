# Framework Alpha Packaging and Release-Candidate Authority Amendment

Status: `PROSPECTIVE_UNAUDITED_AUTHORITY_CANDIDATE`

Authority version: `1.0.0`

Required predecessor commit:
`3c0b8939b9902e05584501e31d74e2bcb57c302a`

Required predecessor tree:
`e5d1fc2746253d73474b60c86c145293fb8ee1ef`

Proposed authority branch:
`framework/stage-c-packaging-release-candidate-authority`

Runtime-identity correction branch:
`framework/stage-c-sqlite-runtime-authority-correction`

## 1. Purpose and boundary

This amendment prospectively authorizes one narrow implementation stage: make
the already accepted EBU framework source tree distributable without changing
framework or scientific behavior, public APIs, project identity, version,
accepted runtime dependency metadata, dependency lock, equations, protocols,
results, or manuscripts. It also freezes the packaging and installed-artifact
validation needed for an alpha release candidate and replaces the preview
Ubuntu T1 environment with a stable, immutable environment.

Authority drafting, independent authority audit, authority integration,
implementation, independent candidate audit, target integration, alpha release
preparation, main merge, tagging, release, registered or full-horizon scientific
execution, results interpretation, book generation, and publication remain
separate gates. This
document authorizes only the later implementation and validation described
here after an independent `PASS` and accepted authority coordinate exist. It
does not itself accept, implement, integrate, release, or publish anything.

The matching mechanical sources are:

- `framework_alpha_packaging_release_candidate_contract.json`;
- `framework_alpha_packaging_release_candidate_predecessor_manifest.json`;
- `framework_alpha_packaging_release_candidate_validation_contract.json`; and
- `framework_alpha_packaging_release_candidate_implementation_path_manifest.json`.

Any disagreement between this Markdown and those JSON files is an integrity
failure. The JSON files use strict duplicate-key rejection, no non-finite
numbers, UTF-8, LF endings, and one final LF.

## 2. Verified predecessor facts

The live private GitHub refs were freshly queried on 2026-08-26 UTC:

| Ref | Verified commit |
|---|---|
| `refs/heads/framework-v0.1` | `3c0b8939b9902e05584501e31d74e2bcb57c302a` |
| `refs/heads/main` | `e1c6000f7b050e56e6fd0aa4b23e56c5d9e641d0` |

The local branch named `framework-v0.1` is stale at
`4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e` and is not an admissible base.
Every unrelated, dirty, stale, historical, and prunable worktree remains out of
scope and must not be changed or pruned.

GitHub Actions run `33020110257` is a successful push run for exact head
`3c0b8939b9902e05584501e31d74e2bcb57c302a`. It proves:

- the conventional job completed successfully;
- the accepted T0 historical group completed 109 tests;
- the current I-9 reachability group completed 3 tests;
- the current CLCD diagnostic group completed 3 tests; and
- T1 completed 299 tests.

Its T2 job was skipped because the accepted workflow restricts T2 to
`workflow_dispatch`. The skipped job is not a T2 pass and cannot satisfy this
release-candidate gate.

The first immutable authority candidate, commit
`1267ed8d5b5c0cac567f4e14db31f2123905aaf6` and tree
`466e2813524abf1f50b77a65f314e593f8c702cf`, was independently rejected. Its
push CI run `33023757404` passed the conventional and T1 jobs but failed the
current I-9 reachability group because the five new authority paths were not
admitted by `_audit_current_head_scope`; T2 and CLCD did not complete. That
failure is evidence, not a pass.

The first corrected authority candidate, commit
`28d84c8373d9c0760fe330e448721a2ec0ba5561` and tree
`0c1266c672fbb078b2f8d4cec1273ff1b020e283`, was also independently rejected.
Its push CI run `33024871190` repeated the same authority-only reachability
failure while conventional and T1 passed, historical T0 completed 109 tests,
T2 was skipped, and CLCD did not complete. Independent inspection additionally
found that mandatory T2 file `tests/framework/test_bridge_exact_fixtures.py`
still binds whole-I8 failure and root-export inventories but was absent from
the closed modification set. This twice-corrected candidate adds only the exact
authority needed for that inventory reconciliation and the already diagnosed
current-scope repair during the later implementation.

The final Stage C authority candidate, commit
`97daec0c3982db546769a9d268332c9b7353daa8` and tree
`36422147de3efbad69bd21550b9c8f142a965481`, received an independent authority
`PASS`. It was normally integrated without history rewriting as commit
`f88496cfb2cce563db25a259e3ac9a6d1e22268f`, preserving the same tree, and was
the freshly verified live `refs/heads/framework-v0.1` coordinate when this
runtime correction was drafted.

Implementation then produced fail-closed runtime evidence that the accepted
source-ID rule was mechanically unsatisfiable for the exact pinned image. Push
run `33030540700` at implementation commit
`361e1541dcd383a6f13fbe0664597e0066c41c6d` / tree
`d7819c6ff06cda3db5cd749fe286c65618e1aa9f` and diagnostic run `33030733344`
at commit `1d4d2f8e53973c07fe7156d4ff3d710609648d76` / tree
`e270314bd23559ca9bc7989eb6ae7c6dd67ac38e` each passed all 92 static-authority
checks in all five required jobs, then refused before any build or test because
the pinned runtime returned SQLite source ID
`2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69aalt1`
from Debian package `libsqlite3-0:amd64=3.46.1-7+deb13u1`, rather than the
upstream release reference ending in `1e33`. Neither run is a validation pass.
The refusals establish only runtime-identity correction evidence; they do not
establish packaging, framework, scientific, release, result, or book evidence.
This descendant correction changes only this Markdown file,
`framework_alpha_packaging_release_candidate_contract.json`, and
`framework_alpha_packaging_release_candidate_validation_contract.json`.
`framework_alpha_packaging_release_candidate_implementation_path_manifest.json`
and `framework_alpha_packaging_release_candidate_predecessor_manifest.json`
remain byte-identical to the independently accepted authority.

## 3. Packaging diagnosis

The predecessor has exactly 48 regular files below `src/ebu_framework`, of
which 44 are Python module files. The backend's
`_PLANNED_PACKAGE_FILES` admits only 43 paths. These five accepted files are
present but omitted from that allowlist:

```text
src/ebu_framework/atomic.py
src/ebu_framework/conservation.py
src/ebu_framework/interaction.py
src/ebu_framework/correction_protocol.py
src/ebu_framework/correction_diagnostics.py
```

`_discover_package_files` encounters those files and refuses
`PACKAGE_FILE_SET_MISMATCH`, so no wheel or sdist can currently be built.

That first refusal masks two additional packaging inconsistencies:

1. the backend requires only the historical I-1 subset to be present, so a
   later admitted package file could be absent without a build refusal; and
2. accepted I-4 changed `pyproject.toml` to
   `dependencies = ["PyNaCl==1.6.2"]`, but the backend still validates an
   empty dependency list and still omits the corresponding `Requires-Dist`
   metadata field.

The accepted `pyproject.toml`, `requirements-framework.lock`, framework source,
exports, signatures, failure codes, and version are controlling. The backend
must be reconciled to them; none of those controlling inputs may be edited.

## 4. Narrow supersession and preserved authority

This amendment supersedes the accepted I-1 packaging authority only for:

- the completed-stage package inventory;
- the requirement that every admitted package file be present;
- reconciliation of backend validation and emitted core metadata to the
  accepted I-4 dependency declaration; and
- the Stage C release-candidate validation and stable runner decision.

Every other I-1 rule remains unchanged, including the in-tree stdlib-only
backend, empty build requirements, deterministic archive algorithms,
fail-closed path and source checks, artifact names, wheel tag, metadata order,
archive modes and timestamps, `RECORD`, evidence-only manifests, frontend role
separation, and P1-P12 acceptance intent.

Accepted I-1 through I-9, atomic-generator, interaction, topology/motif, CLCD,
conservation, durability, trace, recovery, publication-mechanism, and
dependency authorities remain authoritative. This amendment changes no
mathematical, scientific, institutional, or empirical claim and grants no new
registered study, full-horizon campaign, official result generation, or
scientific interpretation permission. Section 11 separately admits the exact
accepted bounded regression behavior already executed by the mandatory test
suites and classifies it only as static/synthetic implementation evidence.

## 5. Exact completed-stage package inventory

The closed package inventory is exactly the following 48 paths, ordered by
UTF-8 path bytes:

```text
src/ebu_framework/__init__.py
src/ebu_framework/actions.py
src/ebu_framework/artifacts.py
src/ebu_framework/atomic.py
src/ebu_framework/authorization.py
src/ebu_framework/authorization_use.py
src/ebu_framework/bridge.py
src/ebu_framework/canonical.py
src/ebu_framework/capabilities.py
src/ebu_framework/causal.py
src/ebu_framework/commitments.py
src/ebu_framework/conservation.py
src/ebu_framework/correction_diagnostics.py
src/ebu_framework/correction_protocol.py
src/ebu_framework/data/__init__.py
src/ebu_framework/data/core_registry_v1.json
src/ebu_framework/data/unicode/15.0.0/DerivedNormalizationProps.txt
src/ebu_framework/data/unicode/15.0.0/UnicodeData.txt
src/ebu_framework/distortion.py
src/ebu_framework/durability.py
src/ebu_framework/dynamic.py
src/ebu_framework/envelopes.py
src/ebu_framework/errors.py
src/ebu_framework/events.py
src/ebu_framework/execution.py
src/ebu_framework/experiment.py
src/ebu_framework/faults.py
src/ebu_framework/hashing.py
src/ebu_framework/identity.py
src/ebu_framework/interaction.py
src/ebu_framework/ledger.py
src/ebu_framework/network.py
src/ebu_framework/numeric.py
src/ebu_framework/observation.py
src/ebu_framework/ownership.py
src/ebu_framework/policy.py
src/ebu_framework/primitives.py
src/ebu_framework/provenance.py
src/ebu_framework/publication.py
src/ebu_framework/py.typed
src/ebu_framework/recovery.py
src/ebu_framework/registry.py
src/ebu_framework/scheduling.py
src/ebu_framework/settlement.py
src/ebu_framework/state.py
src/ebu_framework/traces.py
src/ebu_framework/trust.py
src/ebu_framework/validation.py
```

`_PLANNED_PACKAGE_FILES` must equal this set. Discovery must refuse if the
actual regular-file set differs in either direction. Missing files and unknown
files are both fatal; neither may be silently ignored. Existing path, symlink,
case-fold, normalization, regular-file, stable-read, and source-change checks
remain exact.

The accepted package-source tree object
`4de85ed2935d1c35bdcc0f1259f0acb2df569fdd` is immutable during Stage C
implementation. No file below `src/ebu_framework` may change.

## 6. Exact metadata reconciliation

`pyproject.toml` remains byte-identical with raw SHA-256
`98c7112d08a2d0b4251d2b79bcf583bef8ce4560be55dcdddec6b3a6fdffbb4b`.
`requirements-framework.lock` remains byte-identical with raw SHA-256
`8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a`.
The version remains exactly `0.1.0a1`.

The backend's exact expected project table changes only from the stale empty
dependency value to:

```python
"dependencies": ["PyNaCl==1.6.2"],
```

The emitted Core Metadata 2.5 gains exactly one field after `Import-Name`:

```text
Requires-Dist: PyNaCl==1.6.2
```

The terminal blank line remains. `PKG-INFO`, prepared metadata, direct-wheel
metadata, and sdist-derived-wheel metadata must use byte-identical core
metadata. No other header, order, spelling, dependency, extra, marker, version,
entry point, script, or dynamic field may change. `WHEEL` and the backend
identity remain `ebu-in-tree-pep517-backend/1`.

This is reconciliation to already accepted metadata, not authority to choose a
new dependency or version.

## 7. Frozen public and installed surface

The source and each clean installed artifact must expose exactly:

- 44 importable package modules derived bijectively from the 44 `.py` paths;
- 471 ordered, duplicate-free root exports;
- root-export LF projection SHA-256
  `804ff437fc0adfdb8980e976c099814c2ece2142d4e40ade3a577b3e14fc1bc9`;
- 294 ordered, duplicate-free `FailureCode` names;
- failure-code LF projection SHA-256
  `bde7371b5d4fd34a537e1d7137ca98c79b5e22d4b1e6678b295da6f321179a2c`;
- 162 exact accepted public function/signature rows; and
- `ebu_framework.__version__ == "0.1.0a1"`.

The installed-artifact probe must run from a new empty directory with isolated
Python, no `PYTHONPATH`, no editable installation, and no source or repository
path in `sys.path`. For every imported module, its resolved regular-file origin
must be below the tested environment's installed package directory and outside
the checkout, source snapshot, and sdist extraction tree. Namespace packages,
zip-path substitution, `.pth` injection, symlinks, and source fallback refuse.

The 162 signature rows are the exact accepted rows already reconstructed by
`tests/framework/test_validation_reachability.py`, including the accepted CLCD
suffix. Stage C may consume those authorities but may not rewrite them.

## 8. Stable SQLite and runner decision

`ubuntu-26.04` is rejected as the alpha reference runner. GitHub's official
runner-images records still classify it as public preview and warn that
software may be unstable and capacity may cause queuing. A successful
predecessor run on that image remains valid implementation evidence, but a
preview image is not the stable release gate.

The Stage C T1 and packaging reference environment is:

- GitHub host label: `ubuntu-24.04`;
- immutable runtime image:
  `docker.io/library/python@sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab`;
- OCI platform: `linux/amd64`;
- official-image provenance: Python `3.14.4-trixie`, docker-library/python
  revision `6cc07b27ad0df3769bbd1a2a1000a842634681d2`;
- required runtime: final CPython `3.14.4`; and
- required SQLite: exactly `3.46.1`, still satisfying
  `3.46.0 <= sqlite3.sqlite_version < 4.0.0`.

Two distinct SQLite source identities are frozen and must not be conflated:

- the upstream SQLite 3.46.1 release provenance reference is
  `2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69a1e33`;
  it must be recorded but must never be compared as the pinned runtime gate;
- the exact required `sqlite_source_id()` returned by the pinned Debian
  runtime is
  `2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69aalt1`.

The exact required Debian runtime package identity is
`libsqlite3-0:amd64=3.46.1-7+deb13u1`. The `alt1` runtime identity records the
distribution-modified SQLite source in that immutable image; it is not an
upstream release identity and may not be replaced by the upstream reference.

Before any T1 or packaging test, the job must record and verify the immutable
image digest, `/etc/os-release`, `sys.implementation`, `sys.version`,
`sys.version_info`, ABI/cache tag, executable hash when available,
`sqlite3.sqlite_version`, `sqlite3.sqlite_version_info`, `sqlite_source_id()`,
and the exact installed Debian `libsqlite3-0` identity. The removed
CPython 3.14 attributes `sqlite3.version` and `sqlite3.version_info` are not
required and must not be used as runtime gates. A missing required field,
unexpected platform, prerelease Python, different Python patch, or SQLite
outside the exact accepted version, pinned runtime source identity, or Debian
package identity refuses the lane.

The image must be pulled by digest while network is available. Packaging
frontend execution and clean installed-artifact probes must then run with
network disabled. The exact dependency lock and exact-hash wheelhouses remain
the only dependency inputs. A mutable image tag is evidence-only and may not be
used for execution.

If the immutable image fails the exact runtime checks, implementation must stop
for an authority correction; it may not fall back to `ubuntu-26.04`, a moving
container tag, an unpinned package repository, or a locally compiled SQLite.

External decision evidence, queried during drafting on 2026-08-26 UTC, is:

- GitHub runner-images available-image table:
  `https://github.com/actions/runner-images/blob/main/README.md`;
- GitHub's Ubuntu 26.04 public-preview announcement and warning:
  `https://github.com/actions/runner-images/issues/14226`;
- the official Python image source identified by the OCI manifest annotation:
  `https://github.com/docker-library/python/tree/6cc07b27ad0df3769bbd1a2a1000a842634681d2/3.14/trixie`;
- the official CPython 3.14 `sqlite3` reference, including removal of
  `version`/`version_info` and the retained runtime SQLite identities:
  `https://docs.python.org/3.14/library/sqlite3.html`;
- Debian stable Trixie `libsqlite3-0` package record:
  `https://packages.debian.org/trixie/libsqlite3-0`; and
- SQLite 3.46.1 release identity:
  `https://www.sqlite.org/releaselog/3_46_1.html`.

Those mutable pages are provenance evidence, not executable inputs. The OCI
platform manifest digest, exact runtime source ID, and exact Debian package are
the execution identity; the upstream SQLite source ID remains a separately
recorded provenance reference only.

## 9. Closed implementation path authority

After independent authority acceptance, Stage C implementation may modify only:

```text
.github/workflows/tests.yml
build_backend/ebu_build_backend.py
tests/framework/test_artifact_recovery_publication.py
tests/framework/test_atomic_declarations.py
tests/framework/test_bridge_exact_fixtures.py
tests/framework/test_capabilities.py
tests/framework/test_i3_integration.py
tests/framework/test_i3a_declarations.py
tests/framework/test_i3b_declarations.py
tests/framework/test_i3c_declarations.py
tests/framework/test_i3d_declarations.py
tests/framework/test_interaction_declarations.py
tests/framework/test_primitives_envelopes.py
tests/framework/test_validation_reachability.py
```

It may create only:

```text
scripts/validate_stage_c_release_candidate.py
tests/framework/installed_artifact_probe.py
tests/framework/test_packaging_release_candidate.py
```

No other tracked path may change. In particular, `pyproject.toml`,
`requirements-framework.lock`, every `src/ebu_framework` file, accepted tests,
fixtures, contracts, results, books, PDFs, and release notes remain
byte-identical except for the twelve test-only paths named above. The eleven
named historical inventory tests may change only stale whole-snapshot
assertions into exact accepted-prefix plus current CLCD-suffix assertions. They
must preserve all historical prefix bytes and order, all behavioral checks, all
fixtures, all call sites, all failure precedence, and every non-inventory
assertion. No test
may be deleted, skipped, filtered, weakened, or moved to a historical checkout
as a substitute for testing the current source and installed candidate.

`tests/framework/test_validation_reachability.py` may change only its
current-HEAD scope layer. Relative to its immutable I-9 implementation base, it
must continue to admit the two accepted post-I9 paths, require the five Stage C
authority files, and admit exactly the fourteen modified plus three new Stage C
implementation paths frozen here. After the two pre-existing post-I9 overlaps
are counted once, the completed delta from the immutable I-9 implementation
base has exactly 22 unique paths. The authority-only and completed-
implementation states must be represented as separate exact phases; neither
phase may admit an arbitrary, missing, renamed, deleted, symlinked,
mode-changed, source, result, book, or other unlisted path. Historical I-9 Git
object and archive reconstruction, identities, vectors, failure precedence,
and negative cases remain unchanged.

Within `tests/framework/test_bridge_exact_fixtures.py`, only
`test_failure_export_signature_and_import_surfaces` may reconcile its stale
whole-I8 failure and root-export assertions to the exact preserved I8 prefix,
exact accepted CLCD suffix, and whole-current uniqueness. Its test name and
count, 42-row T2 allowlist, fixtures, bridge/I6 assertions, signature and import-
graph assertions, failure precedence, and every non-inventory behavior remain
byte-for-byte or semantically unchanged as applicable.

Validation artifacts, wheelhouses, virtual environments,
source snapshots, extracted sdists, wheels, sdists, manifests, and logs must be
outside the repository.

## 10. Packaging and archive acceptance

All accepted I-1 P1-P12 relations remain mandatory and must each report a
positive completed-check count. Stage C additionally requires:

1. exact equality of actual package files and the 48-path inventory;
2. required-file refusal for removal of each admitted path;
3. unknown-file refusal for representative `.py`, data, bytecode, cache,
   dotfile, Unicode, case-collision, symlink, hardlink, FIFO, and socket inputs;
4. exact Core Metadata 2.5 and accepted `Requires-Dist` reconciliation;
5. wheel membership of exactly 48 package files plus the four required
   dist-info regular files;
6. sdist membership of the exact source snapshot, backend, metadata, license,
   package files, and generated `PKG-INFO`, with no tests or authority files;
7. complete `RECORD` validation for order, CSV, digest, size, and self-row;
8. independent ZIP/TAR/gzip safety, CRC, path, mode, owner, time, header,
   block, terminator, and trailing-payload validation;
9. at least three perturbed direct wheel and sdist builds with byte-identical
   results;
10. byte identity between the direct wheel and the sdist-derived wheel;
11. read-only source success and output-collision/source-mutation refusals;
12. clean installation of both the direct wheel and the separately produced
    sdist-derived wheel; and
13. exact filenames, byte lengths, SHA-256 hashes, build-input manifest,
    source identities, frontend identities, environments, commands, statuses,
    and logs in the evidence bundle.

Skipped, expected-failure, unexpected-success, terminated, incomplete, or
zero-check relations are not passes.

## 11. Source and installed validation lanes

The validation contract freezes the exact lane inventories. At minimum the
candidate must complete:

- all conventional suites applicable at current head;
- accepted historical pre-execution suites at their exact historical
  coordinates when current committed results intentionally make a current-head
  pre-execution assertion obsolete;
- source T0, I-9 reachability, and CLCD diagnostics;
- source T1 in the stable reference environment;
- source T2 with its exact accepted allowlist;
- direct-wheel installed T0, T1, T2, reachability, and CLCD;
- sdist-derived-wheel installed T0, T1, T2, reachability, and CLCD; and
- installed public surface, module origin, metadata, dependency, and version
  probes in two independent clean environments.

The Stage C CI workflow must run T2 on candidate and target pushes; a skipped
T2 job is a Stage C failure. Every unittest lane must verify a positive
discovered count, exact run count, zero failures/errors/skips/expected failures/
unexpected successes, and a successful process status.

The exact conventional and framework test files frozen by the validation
contract are authorized to execute their already accepted bounded synthetic,
pure-function, short-horizon, and preregistered-fixture in-memory deterministic
regression behavior,
including their existing `p1c_step`, `bounded_step`, bounded trajectory-loop,
and test-seam runner calls. Those calls may occur only through the frozen test
entry points, under the frozen inputs and assertions, with their existing test
counts, and without writing or replacing repository official result artifacts.
Ephemeral test fixtures may exist only outside the repository. The
evidence manifest must record the executed test files, counts, commands, and
this classification. The Stage C validator may orchestrate those exact tests
but may not directly call a model, step, trajectory, study runner, or Gate.

This narrow regression permission is static/synthetic implementation testing.
It is not a new numerical-verification claim, registered scientific simulation,
full-horizon campaign, official study execution, result generation, empirical
observation, outcome inspection, or scientific interpretation. All such work
remains separately gated.

Packaging and installed-artifact validation is implementation evidence only.
It does not prove mathematical theorems, scientific behavior, long-run
homeostasis, empirical applicability, or institutional outcomes.

## 12. Candidate evidence and independent audit

The implementation candidate must provide the independent auditor:

- exact base commit/tree, branch, candidate commit/tree, and complete diff;
- authority file identities and hashes;
- exact changed/new path list and scope result;
- package inventory before/after and every refusal result;
- source, direct-wheel, and sdist-derived module/export/failure/signature
  projections;
- wheel/sdist names, sizes, SHA-256 hashes, and equality result;
- complete archive/metadata/`RECORD` evidence;
- clean installation roots and module-origin evidence;
- exact commands and nonzero counts for P1-P12, Stage C additions,
  conventional, T0, T1, T2, reachability, and CLCD lanes;
- all skips, failures, retries, environment deviations, and unresolved risks;
- Python, SQLite, OS, runner, container, dependency, frontend, and lock
  identities;
- candidate-branch CI run URL and immutable run/job IDs; and
- an explicit statement that no registered/full-horizon scientific campaign,
  new official result generation, scientific interpretation, book generation,
  main merge, tag, upload, publication, or release occurred, together with an
  exact record of the bounded regression tests that did execute.

The independent auditor must inspect the complete candidate without repairing
it and issue `PASS` or `FAIL`. Integration into private `framework-v0.1` is
allowed only after `PASS`, exact live-target verification, and normal
non-force Git operations. Fresh target-branch CI must then complete every Stage
C lane, including T2 and packaging. No self-review counts as independent.

## 13. Prohibited actions and stop conditions

Stage C implementation and validation must not:

- edit framework/scientific source, accepted API declarations, metadata source,
  dependency lock, authority history, results, books, or PDFs;
- import checkout source during installed-artifact probes;
- directly invoke a model, step, simulation, trajectory, policy decision,
  framework runner, Gate, scientific callback, or scientific outcome outside
  the exact accepted test entry points and bounded regression behavior frozen
  in Section 11;
- hide, relabel, or weaken a failure, skip, zero-test lane, nondeterministic
  artifact, archive discrepancy, or source-isolation failure;
- use a preview runner, mutable runtime image, unpinned build frontend, editable
  install, source distribution for locked runtime dependencies, or network
  during offline packaging/probe execution;
- force-push, rewrite history, merge `main`, tag, upload to a package index,
  create a public release, publish books, or make an institutional claim.

Stop for an authority disagreement, wrong base/live identity, unauthorized
path, changed protected source, nondeterministic artifact, missing required
lane, unlisted scientific-execution edge, unresolved installed-origin leak, destructive
ambiguity, missing external permission, or explicit main/tag/release/publication
gate. Ordinary implementation, test, audit-helper, environment, or CI defects
must be diagnosed and corrected within the accepted scope.

## 14. Evidence classification and nonclaims

This authority and its static audit are institutional/normative evidence. The
future packaging tests, artifact probes, and exact bounded regression execution
allowed in Section 11 are static/synthetic implementation evidence. They are
not a new numerical-verification claim, registered scientific
simulation, empirical observation, or independently audited scientific
interpretation.

This authority does not claim that a corrected backend, passing artifact,
alpha release candidate, scientific protocol, simulation, result, figure,
book, tag, release, or publication exists. It does not claim long-run
homeostasis, invariance, stability, recovery, conservation beyond accepted
implementation checks, universal benefit, fairness, or empirical validity.

The authority candidate is ready for independent authority audit only when its
five-file diff passes strict JSON parsing, cross-document consistency,
UTF-8/LF/final-LF, trailing-whitespace, protected-predecessor, and exact Git
scope checks.

`FRAMEWORK_ALPHA_PACKAGING_RELEASE_CANDIDATE_AUTHORITY_READY_FOR_AUDIT`
