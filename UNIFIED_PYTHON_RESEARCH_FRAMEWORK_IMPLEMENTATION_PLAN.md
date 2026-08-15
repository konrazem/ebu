# Unified Python Research Framework Implementation Plan

**Plan version:** 0.2.9
**Stage:** Prospective complete I-3 mechanical authority only
**Status:** Accepted and implemented I-2 remains frozen and unchanged; I-3 is specification-ready and unimplemented; no framework implementation, scientific execution, Gate, publication, or release authority
**Date:** 2026-08-12
**Authority reconciliation date:** 2026-08-14
**Language:** English
**Original I-0 repository branch:** `v3.0-local-ebu-foundation`
**Original I-0 starting repository HEAD:** `4897dd69f60860e6c45c979ac37f87b9124e7a3e`
**Historical v0.2.2 authority-reconciliation base HEAD:** `c3965c87554911c526592ac9688d4c35f0c49516`
**I-2 authority-amendment branch:** `framework-v0.1`
**I-2 authority-amendment base HEAD:** `64e7d692dbae2c3beb6752d955c8f6193e481010`
**I-3 authority-amendment base HEAD:** `85cc43b4fafe298245ceb5baf48b1731de47df44`
**Framework specification version:** 0.1.9
**Framework specification SHA-256:**
`3eb023e4a729fe5205f4edf476d1347cc2584a99467648ce552c98954bd976e4`
**I-3 authority amendment SHA-256:**
`a392874c473219df9a24d044dee7444327f347924438cd8a86627f69f79d3be2`
**I-3 mechanical contract SHA-256:**
`505fcad67139bcf9c45d38a59c759f06d9e347e995d50c5ea8c3637ebe4cbcbb`
**I-3 validation contract SHA-256:**
`0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0`
**Future-books structure SHA-256:**
`0c8eeb402b201e81e20c0167f5b66d93ccb9d6d847d1c4c145891e145c9ec26f`
**Conservation and boundary-accounting foundation SHA-256:**
`b164b8079ebafbb86309f1c2a073c3467fc43356a719c95bd89227a1064e9d4a`

---

## 1. Decision and authority boundary

This revision preserves accepted and implemented I-2 exactly and adopts the
complete prospective I-3 Markdown, mechanical, and validation authority.
It creates no Python package, code, implementation schema,
fixture, test, dependency lock, accepted configuration, execution binding,
authorization credential, result, manifest, or publication record. It
authorizes no implementation and no scientific execution.

The current governing architectural and scientific authority is
`UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` v0.1.9 at the exact
whole-file hash above, reconciled with the current source locks in §1.3. This
plan makes I-3 mechanically specification-ready but does not begin I-3A, any
implementation, or I-5.
It does not change an imported definition, equation, state component, event
phase, hypothesis, parameter, comparison, metric, threshold, tolerance,
falsifier, causal rule, settlement rule, or interpretation rule.

### 1.1 Original I-0 read-only start verification — historical

The following checks completed before the original I-0 plan was created. The
table is preserved as historical evidence; it does not claim that the later
specification revisions or current books-structure bytes were verified during
the original I-0 task:

| Check | Required | Observed | Disposition |
|---|---|---|---|
| Repository root | `/Users/konrad.grzyb/code/ebu` | Exact match | Pass |
| Applicable guidance | Root `AGENTS.md` | Read completely; no nested `AGENTS.md` exists | Pass |
| Worktree | Clean | Clean | Pass |
| Branch | `v3.0-local-ebu-foundation` | Exact match | Pass |
| Local HEAD | `4897dd69f60860e6c45c979ac37f87b9124e7a3e` | Exact match | Pass |
| Tracked remote tip | Same expected SHA | `origin/v3.0-local-ebu-foundation` at exact SHA | Pass |
| Live remote branch tip | Same expected SHA | `refs/heads/v3.0-local-ebu-foundation` at exact SHA | Pass |
| Recent history | Consistent with framework-specification checkpoint | HEAD is `Add Unified Python Research Framework Specification v0.1` | Pass |
| Specification SHA-256 | `4c2b3bc...abead38` | Exact match | Pass |
| Unexplained artifacts | None | None | Pass |

No material mismatch was found during the original I-0 task. Its authority
gate therefore permitted that planning task to proceed. This historical
disposition does not authorize I-1 under the current locks.

### 1.2 Original I-0 source register — historical

| Source | Version or role | SHA-256 verified during original I-0 | Historical authority retained by the original record |
|---|---|---|---|
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` | v0.1 framework specification | `4c2b3bc65628d37fefb874ab577f8b9ce173554ae2399c788e2d7d301abead38` | Governing framework object, workflow, hashing, execution, provenance, and stage contracts |
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | Future-books architecture | `1e4df33b4898a8dd0314ce771f8c06a86eca97782a8d27ffdb9c7165e2663558` | Parts IV–IX order, object requirements, reproducibility, claim status, and stop conditions |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | v0.2 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | Part VI definitions, grouping, comparators, physical measurement, causal limits, receipt closure, and batching |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | v0.1 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | Dynamic state, seven-layer separation, exact ten-phase order, network evolution, uncertainty, objectives, and falsifiers |

All four files were read completely during original I-0, and their registered
hashes then agreed with the committed bytes. The specification's explanation
of the planning register's older bridge-v0.1 pointer is retained; the imported
bridge authority is v0.2. The old specification and books hashes in this
subsection are historical only and are not active implementation authority
for this or any later revision.

### 1.3 Current v0.2.9 mechanical authority locks and status

The current prospective authority set is:

| Source | Current version or role | Current required raw SHA-256 | Mechanical status |
|---|---|---|---|
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` | v0.1.9 framework specification | `3eb023e4a729fe5205f4edf476d1347cc2584a99467648ce552c98954bd976e4` | Current governing specification and complete prospective I-3 lock |
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | Current future-books architecture, including K1–K6, literature/originality, and conservation-accounting planning | `0c8eeb402b201e81e20c0167f5b66d93ccb9d6d847d1c4c145891e145c9ec26f` | Current planning-authority lock, within the scope boundaries below |
| `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` | v0.1 conceptual and algebraic planning foundation | `b164b8079ebafbb86309f1c2a073c3467fc43356a719c95bd89227a1064e9d4a` | Current conservation/boundary-accounting planning lock; no implementation authority |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | v0.2 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | Unchanged imported Part VI authority |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | v0.1 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | Unchanged imported dynamic-coordination authority |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I1_PACKAGING_AMENDMENT.md` | I-1 packaging amendment v1.1.1 | `a27aedf955c1e7bbf7039efc905951f516e070a2f36dc24b23c72d75f6a2f448` | Unchanged narrow packaging authority |
| `unified_python_research_framework_packaging_contract.json` | I-1 packaging contract v1.1.1 | `edf2bd33361e7b2b2e083a10535c87e1e1cbbd36d21c2a3f3004f12b1743c351` | Unchanged mechanical packaging authority |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md` | v1.0.0 normative human I-3 rendering | `a392874c473219df9a24d044dee7444327f347924438cd8a86627f69f79d3be2` | Current narrow prospective I-3 authority; no implementation permission |
| `unified_python_research_framework_i3_contract.json` | v1.0.0 mechanical I-3 authority | `505fcad67139bcf9c45d38a59c759f06d9e347e995d50c5ea8c3637ebe4cbcbb` | Exact I-3 types, fields, validators, failures, projections, exports, imports, paths, and stages |
| `unified_python_research_framework_i3_validation_contract.json` | v1.0.0 validation authority | `0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0` | Exact 544-vector fully materialized prospective validation corpus and collision rules |
| Accepted combined I-1 raw-hash/path/blob manifest | Accepted I-1 integration evidence | `f7b1b7abc9a71b090320b8dc468d57e3a7e39f4f2a045b7a5946a4174882fee8` | Immutable accepted I-1 evidence; not recomputed or redefined here |

The aggregate row is historical corroboration, not a semantic I-2 input.
Commit `ed75790b20c7d6b86cedc4d9dbeb269f32cca9ea` introduced exactly 22 I-1
implementation paths. The complete feature range from
`fae76042746e55b9fe5ec5c62de0f47fbc5ccb47` through `ed75790...` contains
those paths plus the two packaging-authority documents, for 24 paths total.
The original aggregate serialization recipe is not committed; the digest is
not independently reproducible and is preserved without recreation or
redefinition. Current integrity is verified from Git path/blob identities,
raw hashes, and byte sizes.

Only this table and the matching top-level fields are active mechanical
authority locks. The old hashes in §§1.1–1.2, §20, and the frozen §21 I-2
acceptance record are retained solely as historical evidence. The original plan's
whole-file SHA-256 is
`a1cebfa63528e49d9bada3c6564c7d40616369a45afd97640ff937ae07389674`;
that value is historical and is not the hash of a later revision.

Revision v0.2.1 is also immutable historical evidence. It used specification
v0.1.1 at raw SHA-256
`a52b0232595719afd554d842aefb16d6dba0e039ced75c4aed05b358964c6de1`,
the books-structure raw SHA-256
`4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c`,
and had plan whole-file SHA-256
`d89fe92ac6cafd8990588e72d294bcf547cbb478d4b43b638a380e38116ba42e`.
None of those three values is an active v0.2.9 authority lock.

Revision v0.2.2 is immutable historical evidence. It used specification
v0.1.2 at raw SHA-256
`32bc5b9d1983b3b46242d0ccc9323636847d1c8cfeea641f64796f0665916f69`
and had plan whole-file SHA-256
`3422a0887b82637ce323de7015869770ffa59408cb11907f7266ed0e95a22a9c`.
Neither value is an active v0.2.9 lock.

Revision v0.2.3 is immutable historical evidence. It used specification
v0.1.3 at raw SHA-256
`44ae0d5587b24bbca32acda822cddfdc7db76795f81337cd8fc7951bf2946193`
and had plan whole-file SHA-256
`bcc25725575dcd0905a17dc7712da9e534a92c3e6e5335e65248979ad1c22d46`.
Neither value is an active v0.2.9 lock.

Revision v0.2.4 is immutable historical evidence. It used specification
v0.1.4 at raw SHA-256
`25250235e5cb2b61ab0ec6c330245766084cf7b2528d323c70018a99dd1c8380`
and had plan whole-file SHA-256
`bd65010e6231f71d68d9e2165f723efab5175d2e8ea3c05d8624a060602ac6ff`.
Neither value is an active v0.2.9 lock.

Revision v0.2.5 is immutable historical evidence. It used specification
v0.1.5 at raw SHA-256
`9486619dd0e5632e0efadfe1353cbf71923b8ba789923cac790797259d756928`
and had plan whole-file SHA-256
`8db6a9bac25aaa7654d614497640e8429888416d01148e1b33fe2026ce4200c6`.
Neither value is an active v0.2.9 lock.

Revision v0.2.6 is immutable historical evidence. It used specification
v0.1.6 at raw SHA-256
`884767698f26ca75b59ab51d3d95a06e7f2996ae7071145b2f5564baed6787d2`
and had plan whole-file SHA-256
`34241b44b5d6b8bc5b5d6fea6e517afa47507b4cd905eea464347e9865eedc97`.
Neither value is an active v0.2.9 lock.

Revision v0.2.7 is immutable historical evidence. It used specification
v0.1.7 at raw SHA-256
`01f7392459af3eaccbd6966b1504fa1206997722677415d080b0b6883d8081ca`,
the books-structure raw SHA-256
`120496aa0d304561e16b3556bbbd5300c651a3082a297fd21f6bad6034746255`,
and had plan whole-file SHA-256
`f152d680028c4f35027371d036d7282fd1c5648274018237f98626afbacf170e`.
None of those three values is an active v0.2.9 lock.

The signed tag `foundation-v0.1.0` remains the unchanged tag object
`90646d3c7e1ff2201eab4739e894598b80782b79` at commit
`fa08920a56485962b368bfa032fa284f455413eb`. The original specification,
plan, and books bytes recorded by that milestone remain immutable evidence.
The signed tag `foundation-v0.1.1` likewise remains the unchanged tag object
`29060d72ce2fac10ab85e52330c1a375c1d5cb5b` at commit
`fae76042746e55b9fe5ec5c62de0f47fbc5ccb47`. The v0.1.2/v0.2.2
reconciliation was not present at or verified during either signed milestone
and does not move or reinterpret either tag.

The signed tag `foundation-v0.1.2` remains tag object
`63a3f71401e1cc91e85cdff89dbd4d8d38fcbd57`, peeled target
`38aae5e8c59d0bced598f2918f76dbee6df7481c`, signed by ED25519 key
fingerprint `SHA256:PmHC6U5rPJ+Jv7sCyjyF2UYLM6wgE8+iG5T6eGwHFCQ`. It is immutable
foundation evidence and is not moved or reinterpreted by I-2.

The plan uses the 0.2 revision line, rather than the specification's 0.1
revision line, because the pre-amendment
plan explicitly identifies itself as version 0.2. This patch increment
preserves its existing version lineage instead of downgrading it.

The K1–K6 circuit-network programme is future Part VI/Part VIII planning. It
does not change I-1 core semantics or the closed §9 file manifest. It requires
a separately authorized future framework/domain extension before any
implementation, adapter, domain model, or fixture is added. Kirchhoff's laws
do not derive or validate EBU; any later Kirchhoff-style comparison remains a
conditional analogy or domain model with prospectively frozen assumptions and
falsifiers.

Revision v0.2.1 recorded an unresolved packaging contradiction among the
explicit PEP 517 backend requirement, the initially stdlib-only framework
lock, and the absence of a standard-library PEP 517 backend. That statement
is retained as historical evidence. The existing packaging amendment and
matching contract prospectively resolved the contradiction under their
narrow precedence. Revision v0.2.9 does not edit, repeat, or redefine that
resolution, any packaging rule, the accepted I-2 design, or the implemented
§21.2 manifest. It grants only prospective I-3 design authority under §22 and
no framework implementation, I-5, framework-
alpha, scientific-execution, Gate, publication, or release authority.

### 1.4 Preserved Gate 1D-C incident

The incident is preserved exactly:

> One official runner invocation has occurred; no receipt was created; no
> model state advanced; the result directory remains absent; the scientific
> state is `UNSTARTED`.

I-0 did not investigate, correct, retry, invoke, finalize, reinterpret, or
otherwise interact with Gate 1D-C. Nothing in this plan authorizes a second
invocation or changes its invocation count, operational evidence, or
scientific state. All Gate 1D-C source, protocol, plan, contract, runner,
finalizer, test, and result paths are excluded from every implementation and
validation stage below.

### 1.5 Scope of the resolutions

| Question | I-0 disposition |
|---|---|
| UQ-02 | Resolved only for lossless core representations and the interface that a later domain-owned numerical policy must implement. No domain precision, rounding, tolerance, approximation, backend, or cross-platform guarantee is selected. |
| UQ-03 | Resolved by EBU Canonical JSON Version 1 (`ECJ-1`), defined exactly in §3. |
| UQ-04 | Resolved by namespace registration plus deterministic, content-neutral SHA-256 allocation claims, defined in §4. |
| UQ-31 | Narrowly resolved for the first implementation-validation inventory in §11. Scientific execution remains unreachable. |
| UQ-35 | Resolved at the mechanism and protocol level in §6. Deployment trust-anchor key material and authority assignments require a prospective governance bootstrap before protected operations can be activated. |
| UQ-36 | Resolved by the closed-world classification in §7. |
| UQ-38 | Not resolved. Only the base `FaultSchedule` boundary is frozen in §8; all fault kinds, effect schemas, delivery acknowledgements, and terminal rules remain future work. |

### 1.6 Prospective conservation and boundary-accounting boundary

The conservation foundation accepts three first-class account levels:
reduced represented-stock, open control-volume, and isolated boundary-
complete. Reduced and open accounts remain fully supported cases. Existing
D0, P1C, service, Gate 1D-C, and other historical models remain unchanged
reduced or open models under their existing boundaries and are not
retroactively classified as isolated or boundary-complete.

This reconciliation preserves every existing equation, algorithm, constant,
theorem, test, result, protocol, Gate rule, and interpretation boundary. It
also preserves accepted and implemented I-2 exactly as introduced at
`351417c39fa26b9045e7c162a9897a7c38e4e1d1` and integrated at
`ede89d8af6b89da491e03c352efcf1868a913f6f`: no I-2 inventory, failure code,
precedence rule, fixture, import edge, API surface, implementation path, byte,
or hash is changed or reinterpreted.

Section 22 and its three named authority files now define optional I-3
declarative boundary/conservation profiles exactly. Reduced/open profiles are
first-class; isolated profiles require explicit supplied declarations;
historical configurations require no profile or migration; and I-3 validates
only local declaration consistency. A later separately authorized I-5 may
calculate and compare residuals under the selected profile. Neither stage may
impose a universal zero-residual requirement or a hidden framework-wide
numerical tolerance.

Physical conservation, represented-stock closure, EBU accounting, causal
inference, policy, and institutional settlement remain distinct. Detailed
Bridge and Dynamic Coordination amendments remain separately authorized and
unstarted as behavior stages. This revision prospectively freezes the exact
I-3 path/type/callable/export/dependency/fixture authority in §22 but creates
none of those implementation files and grants no executable permission or
scientific, experimental, empirical, novelty, or result claim.

## 2. Non-scientific implementation principles

The future implementation SHALL apply the following rules before any
module-specific rule:

1. The package is a new `src/ebu_framework` package. It SHALL NOT retrofit,
   import, or call a historical experiment, runner, finalizer, or Gate 1D-C
   module.
2. Public values are immutable value objects. Accepted objects are never
   modified in place.
3. Public APIs return typed values or typed failure envelopes. An exception
   without a failure classification is not sufficient at a protected
   boundary.
4. A scientific reference is always the exact triple of ID, semantic version,
   and object-content hash.
5. Scientific and operational authority follows the dependency direction in
   the specification. A Python import cannot confer scientific authority.
6. Python `float` is forbidden in every canonical scientific preimage. A
   domain that elects binary floating arithmetic must use the explicit bit
   representation and a separately accepted numerical policy from §2.2.
7. No runtime default supplies a missing scientific value. Missing policy,
   fault, route, stochastic, tolerance, conversion, or terminal semantics
   fail with an explicit unresolved or unsupported status.
8. Every public interface has one intrinsic capability class in §10. Pure
   structure-only handling of already supplied immutable scientific data may
   be T0; the class is determined by reachable behavior, not merely by the
   data's scientific type or registration status. A lower-class helper called
   inside T2 or T3 work inherits the enclosing operation's authorization,
   classification, and provenance for that invocation.
9. Validation code is structurally unable to construct a scientific-execution
   lease or import the scientific runner entry point.
10. A file listed in §9 may be created or changed only in its owning stage,
    after separate authorization for that stage.

### 2.1 UQ-02: canonical core numeric substrate

The canonical core numeric union is `CoreNumberV1`. It contains exactly four
representations:

| Variant | Mathematical value | Canonical fields and normalization |
|---|---|---|
| `IntegerV1` | Arbitrary-precision signed integer | `value` is a Python arbitrary-precision integer in memory and an ECJ-1 integer token. Zero has no sign; leading zeroes are impossible. |
| `RationalV1` | Exact rational | `numerator: IntegerV1`, `denominator: IntegerV1`; denominator is strictly positive; `gcd(abs(numerator), denominator)=1`; zero is exactly `0/1`. |
| `DecimalV1` | Exact finite base-10 value | `coefficient: IntegerV1`, `exponent10: IntegerV1`, meaning `coefficient * 10**exponent10`; a nonzero coefficient has no trailing decimal zero; zero is exactly coefficient `0`, exponent `0`. |
| `Binary64BitsV1` | Exact stored IEEE-754 binary64 bit pattern, not a selected arithmetic policy | `bits` is exactly 16 lowercase hexadecimal digits in network bit order; exponent-all-ones encodings are rejected, so NaN and infinities are impossible; both signed-zero bit patterns are preserved and may be equated only by a domain policy. |

The variant tag is part of the canonical representation. Therefore integer
`1`, rational `1/1`, decimal `1*10^0`, and a binary64 encoding of one have
different serialized types even where a later numerical policy judges their
mathematical values equivalent. Conversion among variants is never implicit.

The core may implement lossless normalization, sign handling, integer
arithmetic, rational arithmetic, and exact conversion of a finite decimal to
a rational. It SHALL NOT silently choose:

- a decimal precision or context;
- a rounding mode;
- an absolute, relative, ULP, interval, or classification tolerance;
- an approximate comparison rule;
- a decimal rendering precision for binary values;
- overflow, underflow, subnormal, fused-operation, or signed-zero semantics;
- a numerical library or hardware backend; or
- a cross-platform equivalence promise.

### 2.2 Domain-owned `NumericalPolicyV1` interface

Every operation that is not provably lossless in the core substrate requires
an accepted, content-hashed `NumericalPolicyV1`. The interface is a typed
protocol with these mandatory declarations:

```text
NumericalPolicyV1 = {
    policy_ref,
    owning_domain_ref,
    supported_input_variants,
    supported_operations,
    result_variant_by_operation,
    precision_contract,
    rounding_contract,
    comparison_and_tolerance_contract,
    approximation_contract,
    error_bound_contract,
    overflow_underflow_nonfinite_contract,
    signed_zero_contract,
    backend_and_dependency_contract,
    cross_platform_contract,
    failure_contract,
    evidence_requirements
}
```

Its implementation protocol exposes exactly:

```text
validate_operands(operation, operands, quantity_context) -> ValidationRecord
evaluate(operation, operands, quantity_context) -> NumericalResult
compare(purpose, left, right, quantity_context) -> ComparisonResult
bound_error(operation, operands, result, quantity_context) -> ErrorBound
runtime_requirements() -> RuntimeConstraintSet
```

`NumericalResult` includes the exact returned `CoreNumberV1`, the policy
reference, operation identifier, rounding evidence, error bound or explicit
`NOT_APPLICABLE`, and a completeness state. No default implementation of this
protocol is scientifically usable. A domain must prospectively accept its
precision, tolerances, approximation method, and backend before a domain
distortion, transition, classifier, or settlement calculation can use it.
This is the deliberate UQ-02 boundary.

## 3. UQ-03: EBU Canonical JSON Version 1

The selected standard is **EBU Canonical JSON Version 1**, identifier
`ebu-canonical-json/1`, abbreviated `ECJ-1`. Its canonical media type is:

```text
application/json;profile="urn:ebu:canonical-json:1"
```

ECJ-1 is a closed profile of RFC 8259 JSON, UTF-8, Unicode 15.0.0 NFC, and the
rules below. The profile is defined here because RFC 8785 JSON Canonicalization
Scheme is not adopted: RFC 8785 sorts property names by UTF-16 code units,
whereas the governing specification requires a specified Unicode code-point
rule. Quietly using RFC 8785 would create divergent ordering for some
non-BMP/BMP key pairs. ECJ-1 retains the required Unicode-scalar ordering.

### 3.1 ECJ-1 data model and rejection rules

An ECJ-1 value is exactly one of object, array, string, arbitrary-precision
integer, `true`, `false`, or `null`. Raw JSON fraction or exponent number
tokens are forbidden. Rational, decimal, and permitted binary values use the
tagged `CoreNumberV1` objects from §2.1. Schema validation, not the serializer,
decides whether `null` is allowed; `null` can never substitute for a required
resolution state.

Before encoding, the serializer SHALL:

1. accept only Unicode scalar values assigned by Unicode 15.0.0;
2. reject isolated surrogates and unassigned code points;
3. normalize every string value and property name to NFC;
4. reject an object if two original names become equal after NFC;
5. reject duplicate object names at parse time;
6. reject every float, non-finite value, byte string, implicit date/time,
   tuple, set, mapping with a non-string key, or application object that was
   not first projected to the ECJ-1 data model; and
7. reject cyclic object graphs and every value outside its declared schema.

### 3.2 Version-pinned Unicode enforcement

ECJ-1 SHALL NOT use Python's host `unicodedata` database, ICU, the host locale,
or any runtime-downloaded Unicode data to decide assignment or normalization.
I-1 shall vendor these exact Unicode Character Database 15.0.0 source bytes:

| Runtime data asset | Unicode source | Required raw SHA-256 |
|---|---|---|
| `src/ebu_framework/data/unicode/15.0.0/UnicodeData.txt` | `https://www.unicode.org/Public/15.0.0/ucd/UnicodeData.txt` | `806e9aed65037197f1ec85e12be6e8cd870fc5608b4de0fffd990f689f376a73` |
| `src/ebu_framework/data/unicode/15.0.0/DerivedNormalizationProps.txt` | `https://www.unicode.org/Public/15.0.0/ucd/DerivedNormalizationProps.txt` | `d5687a48c95c7d6e1ec59cb29c0f2e8b052018eb069a4371b7368d0561e12a29` |

`canonical.py` contains those two expected digests as fixed implementation
constants and verifies the packaged raw bytes before parsing them. Missing,
extra, malformed, wrong-version, or wrong-digest data causes
`UNICODE_DATA_INTEGRITY_FAILURE` before any ECJ-1 parse, normalization,
serialization, or hash. Network fallback is forbidden.

The assignment set is exactly the scalar entries and expanded `First`/`Last`
ranges in the pinned `UnicodeData.txt`, excluding surrogate code points.
Consequently a code point absent from Unicode 15.0 is rejected even if the
running Python or operating system assigns it in a later Unicode version.
NFC is implemented from the pinned canonical decomposition mappings and
canonical combining classes, the Unicode 15.0 UAX #15 Hangul
decomposition/composition algorithm, and `Full_Composition_Exclusion` from
the pinned `DerivedNormalizationProps.txt`. Compatibility decompositions are
not used. The implementation compares its output against the complete pinned
Unicode 15.0 `NormalizationTest.txt` corpus described in §9.5.

Host `unicodedata.unidata_version` may be recorded as run metadata but cannot
affect an ECJ-1 result. Static reachability checks reject any import of
`unicodedata` or ICU from `canonical.py` and reject any code path that replaces
the pinned tables with host or downloaded data.

### 3.3 Exact byte encoding

- Output is UTF-8 without a BOM, leading/trailing whitespace, or terminal
  newline.
- Object names are sorted lexicographically by their sequences of Unicode
  scalar values after NFC. A shorter identical prefix sorts first.
- Arrays preserve declared order. A mathematical set must first be converted
  by its owning schema to an array sorted by a schema-declared total key; the
  generic serializer never guesses set order.
- Objects use `{`, `:`, `,`, and `}` with no whitespace. Arrays use `[`, `,`,
  and `]` with no whitespace.
- Strings use double quotes. Quotation mark and reverse solidus are escaped as
  `\"` and `\\`. U+0008, U+0009, U+000A, U+000C, and U+000D use `\b`, `\t`,
  `\n`, `\f`, and `\r`. Other U+0000–U+001F scalars use lowercase
  `\u00xx`. Solidus is not escaped. Every other scalar is emitted as its
  direct UTF-8 sequence; `\u` escapes for it are noncanonical.
- Integers use `0` or `-?[1-9][0-9]*`. A plus sign, negative zero, leading
  zero, fraction, or exponent is invalid.
- Literal tokens are exactly `true`, `false`, and `null`.
- Canonical operational UTC timestamps, where a schema calls for a timestamp,
  use exactly `YYYY-MM-DDTHH:MM:SS.ffffffZ` with six fractional digits, the
  proleptic Gregorian calendar, and no leap-second spelling. Scientific model
  time remains the separately typed clock/epoch representation.

An ECJ-1 parser SHALL parse strictly and re-emit the exact same bytes. A
noncanonical input may be parsed only by an explicitly named ingestion
adapter; it is never hashed or accepted until it has been converted to a
typed value and serialized by ECJ-1. ECJ-1 itself is versioned scientific
infrastructure. Any change to these bytes requires a new canonicalization
version and a prospective migration protocol under UQ-05.

## 4. UQ-04: deterministic `ScientificId` allocation

### 4.1 Namespace ownership

`ScientificId` retains the specification grammar:

```text
ebu:<kind>:<namespace>:<local-id>
```

The root namespace registry contains immutable namespace entries. Each entry
binds one lowercase ASCII namespace segment to an owning authority reference
and an allocation-policy version. The reserved namespaces are `core`,
`schema`, `authority`, and `validation`; no user or study may claim them.
Every other namespace must be registered before an ID is allocated. A
namespace name or owner change creates a new registry entry/version and never
reassigns existing IDs.

### 4.2 Allocation claim and algorithm

Every non-reserved ID is allocated from this exact content-neutral claim:

```text
ScientificIdAllocationPreimageV1 = {
    hash_domain: "ebu.scientific-id-allocation.v1",
    id_scheme: "sha256-fullhex-v1",
    kind: <validated lowercase ASCII kind segment>,
    namespace: <registered lowercase ASCII namespace segment>,
    namespace_registry_ref: <exact ObjectRef>,
    allocation_authority_ref: <exact ObjectRef>,
    stable_key: <NFC string satisfying the stable-key rules>
}

digest = SHA-256(ECJ1(ScientificIdAllocationPreimageV1))
local-id = "sha256-" || lowercase_hex(digest)
ScientificId = "ebu:" || kind || ":" || namespace || ":" || local-id
```

The full 256-bit digest is retained; it is never truncated. `stable_key` is a
prospective identity key controlled by the namespace owner. It must describe
the intended logical object lineage, be chosen before object-content or
outcome inspection, and remain unchanged across that object's semantic
versions. It must not contain a mutable path, display label, branch, commit,
database row, clock time, random value, result, object version, or object
content hash.

The allocation claim excludes object content, object version, and every
derived hash, so allocation is non-recursive and later versions retain one
logical ID. The namespace registry atomically records the claim and ID. The
same claim is idempotent and returns the same ID. Reuse of a `stable_key` with
different claim fields, collision with an existing different claim, an
unregistered namespace, or a concurrent conflicting allocation fails closed.
There is no auto-increment, “next available” number, random UUID, path-derived
ID, label-derived ID, or outcome-derived ID.

Reserved bootstrap IDs are literal entries committed in the core registry
fixture and reviewed as source. They do not use their own not-yet-existing
namespace registry reference. No other exception is permitted.

## 5. Exact hash domains and non-self-referential preimages

### 5.1 Common rules

Except for the binary artifact and conventional raw-file cases explicitly
defined below, every framework digest is:

```text
SHA-256(ECJ1(<exact named preimage>))
```

Stored digest text is exactly `sha256:` followed by 64 lowercase hexadecimal
digits. Domain strings are data inside each preimage, not informal labels.
No preimage contains its own derived digest field, an alias for it, an
embedded enclosing record, a signature over it, or a reference to an object
that recursively contains it. ECJ-1 version is pinned by the schema and is
not selected at call time.

### 5.2 Scientific-object and replay hashes

The following preimages are exact and retain the specification's field
meanings:

```text
ObjectContentPreimageV1 = {
    hash_domain: "ebu.object-content.v1",
    object_id,
    object_kind,
    schema_id,
    schema_version,
    object_version,
    authority_refs,
    supersedes_ref,
    object_content_payload
}
```

For `CommonObjectEnvelope`, the field stores exact `CanonicalBytes`, while
the term shown in this preimage is the logical ECJ-1 value produced by one
fresh `parse_ecj1` call. That logical value is passed to the unchanged I-1
`compute_object_content_hash`; the stored bytes are not projected as text,
hex, an integer array, or nested JSON and are not double-encoded. The logical
payload, stored canonical bytes, complete preimage, and resulting content
hash are distinct.

`ObjectContentHash` excludes its own field, lifecycle status, signatures,
authorization and validation evidence, record times, host/process/storage,
cache, publication, and presentation metadata. Configuration, binding,
authorization, ledger-entry, result, manifest, publication, correction,
trust-registry, and ordinary artifact-record hashes all use this projection.

```text
StatePayloadPreimageV1 = {
    hash_domain: "ebu.state-payload.v1",
    state_schema_ref,
    epoch,
    physical_state_x,
    topology_state_g,
    queue_and_transit_state_q,
    commitment_state_c,
    delayed_effect_state_ell,
    declared_external_inputs_applied
}
```

`StatePayloadHash` excludes object identity/version/content hash, its own
field, predecessor links, policy memory, ownership/commit/trace references,
durability, storage, and run provenance.

```text
PolicyMemoryPayloadPreimageV1 = {
    hash_domain: "ebu.policy-memory-payload.v1",
    policy_ref,
    memory_schema_ref,
    available_for_decision_epoch,
    resolution_state,
    memory_payload
}
```

`PolicyMemoryPayloadHash` excludes its own field, memory object
identity/version/content hash, predecessor and decision links, physical
state, trace/durability/storage, and run provenance.

```text
AugmentedClosedLoopReplayStatePreimageV1 = {
    hash_domain: "ebu.augmented-closed-loop-replay-state.v1",
    physical_state_payload_hash,
    policy_memory_payload_hash
}
```

`AugmentedClosedLoopReplayStateHash` exists only for one active stateful
policy under v0.1. `NOT_APPLICABLE` is a typed marker, never a dummy hash.
Multi-controller composition remains UQ-37.

```text
RepresentedStateProjectionPreimageV1 = {
    hash_domain: "ebu.represented-state-projection.v1",
    source_state_payload_hash,
    boundary_ref,
    projection_contract_ref,
    included_coordinate_ids,
    excluded_coordinate_ids_and_resolution_states,
    represented_state_payload
}
```

`RepresentedStateProjectionHash` is the specification's projection hash. It
excludes the `RepresentedState` object identity and every derived hash.

### 5.3 Decision, proposal, and execution-semantics hashes

```text
InformationViewPreimageV1 = {
    hash_domain: "ebu.information-view.v1",
    policy_ref,
    information_contract_ref,
    decision_epoch,
    current_policy_memory_payload_hash_or_not_applicable,
    ordered_visible_field_records,
    ordered_visible_object_refs
}
```

Each visible field record contains field ID, typed value or resolution state,
availability epoch, measurement/provenance reference, and access-capability
ID. `InformationViewHash` covers the complete supplied view. The actual read
set is separately recorded in the decision record and may not contain a field
absent from this preimage.

```text
ProposalSetPreimageV1 = {
    hash_domain: "ebu.proposal-set.v1",
    policy_ref_or_open_loop_schedule_ref,
    decision_coordinate,
    information_view_hash_or_not_applicable,
    before_policy_memory_payload_hash_or_not_applicable,
    after_policy_memory_payload_hash_or_not_applicable,
    ordered_proposal_payloads
}
```

`ProposalSetHash` is the specification's proposal hash. Proposal ordering is
the policy/schedule's frozen total order and cannot depend on a container or
outcome.

```text
ExecutionSemanticsPreimageV1 = {
    hash_domain: "ebu.execution-semantics.v1",
    accepted_configuration_ref,
    implementation_refs,
    source_refs,
    implementation_entrypoint_semantics,
    science_affecting_runtime_constraints,
    science_affecting_operational_exclusions,
    policy_memory_transition_contracts_or_not_applicable,
    fault_injection_delivery_contracts_or_not_applicable,
    event_order_contract,
    arithmetic_and_numerical_policy_contracts,
    information_capability_contract,
    canonical_scientific_trace_schema_ref,
    scientific_result_schema_ref,
    stochastic_generator_and_stream_contract_or_not_applicable
}
```

The exact contents of `science_affecting_runtime_constraints` are frozen in
§7. `ExecutionSemanticsHash` excludes its own field and every run-specific
property in §7.3.

### 5.4 Canonical trace row, prefix, and complete-payload hashes

Every scientific row first has this independent preimage:

```text
CanonicalTraceRowPreimageV1 = {
    hash_domain: "ebu.canonical-trace-row.v1",
    trace_schema_ref,
    row_index,
    epoch,
    event_key,
    phase_ordinal,
    scientific_object_refs,
    predecessor_state_payload_hash,
    successor_state_payload_hash,
    information_view_hash_or_not_applicable,
    before_policy_memory_payload_hash_or_not_applicable,
    after_policy_memory_payload_hash_or_not_applicable,
    augmented_replay_state_hash_or_not_applicable,
    proposal_set_hash_or_not_applicable,
    admission_group_and_ownership_facts,
    typed_quantities,
    uncertainty_values,
    lifecycle_transitions,
    declared_scientific_or_model_faults,
    scientifically_relevant_failures,
    resolution_state,
    predecessor_trace_row_hash_or_genesis
}
```

`CanonicalTraceRowHash` excludes its own sibling field. Row zero uses the
literal typed marker `GENESIS`. Canonical row-stream bytes are the ordered
concatenation of `UINT64_BE(length(ECJ1(row))) || ECJ1(row)` for each row,
where `row` contains the row preimage fields and its already computed sibling
row hash. A confirmed row stream is therefore a literal byte prefix of any
valid later completion.

```text
CanonicalTracePrefixPreimageV1 = {
    hash_domain: "ebu.canonical-trace-prefix.v1",
    trace_header,
    ordered_rows,
    confirmed_row_count,
    last_confirmed_state_payload_hash,
    last_confirmed_policy_memory_payload_hash_or_not_applicable,
    last_confirmed_augmented_replay_state_hash_or_not_applicable,
    completeness_state
}
```

`CanonicalTracePrefixHash` applies only to a finalized, hash-valid prefix and
never claims full completion. `ordered_rows` is exactly the confirmed row
sequence, including sibling row hashes.

```text
CanonicalScientificTracePayloadPreimageV1 = {
    hash_domain: "ebu.canonical-scientific-trace-payload.v1",
    trace_schema_ref,
    accepted_configuration_object_content_hash,
    execution_semantics_hash,
    initial_state_payload_hash,
    initial_policy_memory_payload_hash_or_not_applicable,
    initial_augmented_replay_state_hash_or_not_applicable,
    ordered_external_scientific_input_payload_hashes,
    fault_schedule_object_content_hash_or_not_applicable,
    stochastic_stream_identities_and_draw_coordinates_or_not_applicable,
    ordered_rows,
    terminal_or_last_confirmed_state_payload_hash,
    terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable,
    terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable,
    confirmed_row_count,
    trace_completeness_state
}
```

`CanonicalScientificTracePayloadHash` excludes its own field. The normal
determinism target is `ECJ1(CanonicalScientificTracePayloadPreimageV1)` only
under the completion qualifications in the specification. Run-envelope
bytes are never part of this target.

### 5.5 Artifact, source, proof, and allocation hashes

Artifact bytes use the specification's binary frame exactly:

```text
ArtifactBytePreimageV1 =
    UTF8("ebu.artifact-bytes.v1")
    || 0x00
    || UINT64_BE(length(exact_artifact_bytes))
    || exact_artifact_bytes

ArtifactByteHash = SHA-256(ArtifactBytePreimageV1)
```

The raw 64-byte Ed25519 signature in an authenticity envelope is an artifact
for this purpose; its `proof_byte_hash` is an `ArtifactByteHash`. An
implementation artifact, lock file, figure, trace stream, or other byte
artifact uses the same framed byte identity plus an object-content-hashed
artifact record.

External source files additionally record conventional
`SourceFileRawSha256 = SHA-256(exact_file_bytes)` with the explicit algorithm
label `sha256-raw`. This raw digest has no domain prefix and must never be
substituted for an `ArtifactByteHash` or `ObjectContentHash`.

`ScientificIdAllocationDigest` uses the exact preimage in §4.2. It is an ID
allocation primitive, not object-content identity.

The authorization single-use database key is:

```text
AuthorizationUseKeyPreimageV1 = {
    hash_domain: "ebu.authorization-use-key.v1",
    stage_authorization_ref,
    requested_operation,
    target_object_refs,
    accepted_configuration_ref_or_not_applicable,
    accepted_execution_binding_ref_or_not_applicable,
    execution_identity_or_not_applicable
}
```

`AuthorizationUseKey` is its SHA-256 digest. It excludes use time, process,
host, database row ID, result, and use status. Those facts belong to the
append-only use record. All other hashes required by the specification are
instances of one of the named projections above or ordinary
`ObjectContentHash`/`ArtifactByteHash`; no unnamed generic “hash object” API
is permitted.

## 6. UQ-35: non-recursive authorization model

### 6.1 Trust profile and algorithms

The v0.1 authenticity profile is `EBU-Authorization-Ed25519-V1`:

- signatures are PureEdDSA Ed25519 as defined by RFC 8032;
- public keys are exactly 32 bytes and signatures exactly 64 bytes;
- encoded keys/signatures use unpadded base64url;
- key IDs are `ed25519:` followed by the lowercase raw SHA-256 of the
  32 public-key bytes;
- the signed bytes are ECJ-1 bytes of the exact message being authenticated;
  no caller-selected prehash, algorithm negotiation, or fallback exists; and
- any unknown algorithm, malformed point/key/signature, noncanonical message,
  or verification error is invalid, never “unresolved permission.”

The bootstrap `TrustProfileV1` is installed and pinned out of band. It is the
only non-recursive trust root. It contains exactly three offline issuer-root
public keys with a two-of-three threshold, three revocation-root public keys
with a two-of-three threshold, and exactly three online time-attestation
public keys of which one valid signature is required. It also pins the issuer
and revocation service identities, ECJ-1 and signature profiles, maximum
delegation depth, freshness limits, and permitted stage/operation vocabulary.

The framework validates the installed trust profile against an operator-
configured exact `ObjectRef` and object-content hash. It does not attempt to
prove that pin by another framework authorization. Replacing the pin is an
external governance operation, not a self-authorized framework call.

Actual root public keys, service endpoints, issuer identities, and their
authority assignments do not exist in the governing sources. A prospective
governance bootstrap document must supply and approve them before I-4 can
activate any protected operation. I-4 may implement and T1-check the mechanism
with RFC 8032 and synthetic validation keys, but synthetic keys and the
reserved `validation` namespace are permanently rejected by production
trust profiles.

Root signatures over issuer registries, revocation snapshots, and delegation
credentials use this exact non-recursive message:

```text
TrustEvidenceSignatureMessageV1 = {
    hash_domain: "ebu.trust-evidence-signature-message.v1",
    signature_profile: "EBU-Authorization-Ed25519-V1",
    evidence_kind,
    evidence_ref,
    trust_profile_ref,
    signer_role,
    signer_key_id
}
```

`evidence_ref` contains the evidence object's already computed
`ObjectContentHash`; its signature and authenticity-envelope ref are absent
from that object preimage and signed message. Each root proof is a separate
immutable envelope created after the signed evidence hash.

### 6.2 Issuer registry

An `IssuerRegistrySnapshotV1` is an immutable object containing:

```text
registry_id, sequence, predecessor_snapshot_ref_or_genesis,
valid_from, next_update,
ordered_issuer_entries
```

Each issuer entry contains issuer `ScientificId`, legal/governance evidence
references, active Ed25519 keys with validity intervals, maximum stages,
maximum operations, allowed target namespaces/kinds, whether delegation is
allowed, and maximum delegated depth. The snapshot's object-content hash is
signed by at least two distinct issuer-root keys from the pinned trust
profile. A lower sequence than the last durably accepted sequence, two
different snapshots with the same sequence, a broken predecessor chain, an
expired snapshot, or an insufficient root threshold fails closed.

An issuer registry grants only a ceiling. A `StageAuthorization` remains
specific to exact target objects and cannot rely on a wildcard registry grant
as its operation permission.

### 6.3 Delegation

Delegation uses immutable `DelegationCredentialV1` objects plus separate
Ed25519 authenticity envelopes. A credential contains the delegator issuer
and key, delegate issuer and key, exact parent credential reference or direct
issuer-registry entry, permitted stages/operations/target namespaces and
kinds, `not_before`, `expires_at`, delegation permission, remaining maximum
depth, revocation-registry reference, and explicit exclusions.

The maximum chain depth is four credentials. Validation walks from the leaf
to one directly registered issuer and SHALL prove:

- every object-content hash and every signature;
- exact parent/child key and issuer continuity;
- no repeated credential, issuer/key pair, or cycle;
- temporal overlap across the whole chain;
- the same pinned trust profile and revocation authority throughout;
- strict attenuation: the child stage, operation, target, time, and
  delegation scopes are subsets of the parent's effective scope;
- decrement of remaining depth at every link; and
- current non-revocation of every issuer, key, and credential.

Scope union across different parents is forbidden. Threshold or joint
delegation is not supported in v0.1. A need for either requires a prospective
authorization-profile revision.

### 6.4 Exact operation and target scope

The v0.1 operation vocabulary is:

```text
ACCEPT_EXPERIMENT_CONFIGURATION
ACCEPT_EXECUTION_BINDING
EXECUTE_BOUND_RUN
FINALIZE_EXECUTION_RESULT_MANIFEST
RECOVER_EXECUTION_ARTIFACTS
CREATE_CORRECTION_RECORD
PUBLISH_ARTIFACTS
```

One `StageAuthorization` grants exactly one of these operations. Its target
list contains exact `ObjectRef` values, never path or label patterns.
Configuration acceptance targets the exact draft configuration content hash.
Binding acceptance targets both the accepted configuration and exact draft
binding content hash. `EXECUTE_BOUND_RUN` targets the exact accepted
configuration, accepted binding, execution identity, and runner entry
contract. Later run-artifact operations additionally target the exact
manifest or artifact refs they consume.

For execution, a single successful authorization consumption grants one
entry into the exact bound run. The resulting nonserializable
`ScientificExecutionLease` is bound to the authorization-use key, execution
identity, binding hash, process entry, and one active call stack. Internal
epoch advances require that lease but do not consume additional invocations.
The lease cannot be persisted, transferred, reconstructed after process loss,
or used with another binding. A crash after consumption does not restore the
authorization; recovery or another invocation requires its own authority.

### 6.5 Trusted time and freshness

Authorization time is UTC at microsecond precision with half-open validity
`[not_before, expires_at)`. It never uses scientific model time.

Every protected validation obtains a fresh `TrustedTimeAttestationV1` from an
online time service whose key is pinned by the trust profile. The validator
creates a 256-bit cryptographically random challenge with
`secrets.token_bytes(32)`, backed by the operating-system CSPRNG, and the
exact `AuthorizationUseKey` from §5.5. The service signs ECJ-1 bytes of:

```text
TrustedTimeAttestationMessageV1 = {
    hash_domain: "ebu.trusted-time-attestation-message.v1",
    signature_profile: "EBU-Authorization-Ed25519-V1",
    trust_profile_ref,
    time_service_id,
    signer_key_id,
    challenge_base64url,
    authorization_use_key,
    attested_utc,
    service_sequence,
    issued_at,
    expires_at
}
```

The signed response binds the request, the attested UTC time, a service
sequence, issue time, and expiry no more than 30 seconds after issue. The
response must arrive during that local request; supplied cached attestations
are rejected. Local monotonic time may enforce the 30-second processing
window but is not the authority for authorization validity.

If fresh time cannot be obtained or verified, the protected operation does
not start. Wall-clock rollback, time-zone configuration, or a caller-supplied
timestamp cannot extend authority.

### 6.6 Revocation

`RevocationSnapshotV1` is a complete, immutable, monotonically sequenced list
of revoked issuer IDs, key IDs, delegation refs, authorization refs, and
trust-profile successor notices, each with effective UTC time and reason.
Entries are ordered by `(entry_kind, revoked_ref, effective_utc, reason)` in
ECJ-1 string order, and duplicate `(entry_kind, revoked_ref)` entries are
invalid. The snapshot contains a predecessor snapshot reference, `as_of`, and
`next_update`; its lifetime may not exceed five minutes. Its object-content
hash requires two distinct valid revocation-root signatures.

The validator fetches the current snapshot during the protected request,
checks it against the fresh time attestation, verifies the threshold and
predecessor chain, and durably rejects sequence rollback or same-sequence
equivocation. Failure to fetch, an expired snapshot, an unknown gap, or any
revoked element fails closed. Revocation never mutates an authorization or
delegation object.

### 6.7 Single-use enforcement

Every v0.1 `StageAuthorization` has `maximum_invocations=1`. Before entering
the protected interface, the validator computes `AuthorizationUseKey` from
§5.5 and performs a linearizable compare-and-consume in a local SQLite use
store:

1. require a local regular filesystem explicitly approved for SQLite locking;
   network and distributed filesystems are unsupported;
2. open SQLite in rollback-journal mode with `journal_mode=DELETE`,
   `synchronous=FULL`, foreign keys enabled, and a declared SQLite library
   version captured in operational provenance;
3. execute `BEGIN IMMEDIATE`;
4. insert the use key into a table where it is the primary key, together with
   exact authorization/target refs and status `CONSUMED`;
5. append a predecessor-linked authorization-use ledger record in the same
   transaction;
6. commit durably before the protected interface is entered; and
7. never delete or reset a consumed key.

A uniqueness conflict means already used. An ambiguous commit, I/O error,
unsupported filesystem, lock failure, or durability uncertainty returns
`AUTHORIZATION_USE_UNRESOLVED` and does not enter the operation. It never
assumes the authorization remains unused. Distributed or multi-site use is
unsupported in v0.1 and requires a new authorization profile, not a weaker
local check.

This SQLite choice resolves the local single-use mechanism only. It does not
resolve UQ-26's broader atomic physical-state, policy-memory, trace, and phase
durability problem.

### 6.8 External authenticity envelope

The signer signs these exact ECJ-1 bytes:

```text
AuthorizationSignatureMessageV1 = {
    hash_domain: "ebu.authorization-signature-message.v1",
    signature_profile: "EBU-Authorization-Ed25519-V1",
    stage_authorization_ref,
    trust_profile_ref,
    signer_issuer_id,
    signer_key_id,
    ordered_delegation_credential_refs
}
```

`stage_authorization_ref` includes the already computed authorization object
content hash. The resulting `AuthorizationAuthenticityEnvelopeV1` contains
the complete message, unpadded-base64url signature, its `ArtifactByteHash` as
`proof_byte_hash`, signer credential evidence refs, and its own common object
envelope. The envelope's `ObjectContentHash` is computed after the signature;
neither that envelope hash nor the signature enters the authorization
preimage or the signed message. This is non-recursive.

The validation bundle is external and contains the authorization,
authenticity envelope, pinned trust-profile ref, issuer-registry snapshot and
root proofs, ordered delegation objects and proofs, fresh trusted-time
attestation, current revocation snapshot and proofs, exact predecessor-stage
evidence, and single-use-store identity. The accepted configuration and
binding contain none of this permission evidence.

### 6.9 Authorization validation order

Validation is fail-fast but records every check safely completed before the
failure:

1. strict ECJ-1 parse and all object-content hashes;
2. pinned trust profile and supported profiles;
3. issuer-registry threshold, sequence, time, and signer key;
4. authorization signature message and signature;
5. delegation chain and effective attenuated issuer ceiling;
6. fresh trusted time;
7. current revocation snapshot and non-revocation;
8. exact stage, operation, target, configuration, binding, execution identity,
   exclusions, and lifecycle states;
9. exact predecessor-evidence hashes and accepted statuses;
10. binding-to-configuration consistency; and
11. atomic single-use consumption.

No validation branch trusts file existence, Git authorship, username,
filesystem ownership, process identity, repository access, a self-asserted
issuer string, or later-stage artifacts as authorization.

## 7. UQ-36: `ExecutionSemanticsHash` classification

### 7.1 Closed-world rule

The execution process receives a normalized, allowlisted environment. Every
runtime property that code can read and that could select a value, branch,
order, arithmetic result, scientific failure, trace row, or terminal state
must be declared in `science_affecting_runtime_constraints` and therefore
enters `ExecutionSemanticsHash`. An undeclared runtime read, unpinned native
dependency, or dependence on a property classified as run metadata aborts
preflight before model-state advance.

The classification is based on semantic influence, not convenience. A
property is not demoted to run metadata merely because two observed runs
happened to agree.

### 7.2 Properties included in `ExecutionSemanticsHash`

The following fields are mandatory, using exact values or an explicit
`NOT_APPLICABLE` marker:

| Included class | Exact content |
|---|---|
| Scientific binding | Accepted configuration ref; initial physical and policy-memory contracts; event-order, fault-schedule applicability, stochastic applicability, and domain numerical-policy refs |
| Framework and domain implementation | Artifact refs and `ArtifactByteHash` values for every imported framework/domain module, generated table, compiled extension, executable resource, and result-producing script reachable by the entry point |
| Source | Repository identity, exact source commit, and ordered raw SHA-256/source artifact refs for every reachable result-producing source file; dirty source is forbidden rather than hashed as a new implicit implementation |
| Interpreter | Implementation name (`CPython` for v0.1), full major/minor/patch/release/build identity, executable artifact identity, compile flags, byte order, pointer width, and Python ABI tag |
| Dependency closure | Exact package version, distribution/wheel or source archive hash, build tag, native library/ABI identity, and transitive dependency closure for every reachable dependency |
| OS and architecture contract | OS family/release/build, kernel ABI relied upon, machine architecture, byte order, libc/runtime identity, and container/image digest or explicit `NOT_APPLICABLE` |
| Numerical hardware/backend | CPU instruction features actually enabled for numerical work; FPU rounding mode, denormal/subnormal handling, FMA policy; accelerator/GPU model, driver, runtime, deterministic-mode settings, or `NOT_APPLICABLE`; BLAS/LAPACK/libm/backend identities or `NOT_APPLICABLE` |
| Arithmetic | Every `NumericalPolicyV1`, precision, rounding, tolerance, approximation/error rule, overflow/underflow/signed-zero rule, unit/conversion policy, and backend configuration |
| Concurrency | Process/thread/worker count, start method, work partition, deterministic scheduler/reduction/tie-break rules, thread-pool and native-library thread limits; v0.1 rejects any scheduling-dependent scientific order |
| Environment allowlist | Exact values for `PYTHONHASHSEED`, locale categories, encoding settings, time zone, numerical-backend variables, thread-count variables, and every additional environment variable declared readable by result-producing code; secrets are forbidden as scientific inputs |
| Entry semantics | Importable entry point, normalized non-secret argument vector, working-data object refs rather than paths, mode, phase/event version, and explicit no-fallback behavior |
| Information and memory | Capability/view construction, availability/read-set enforcement, stateless/stateful mode, initial-memory validation, and atomic memory-transition contracts |
| Fault delivery | Base hook version and exact accepted study-specific delivery semantics, or `NOT_APPLICABLE`; the schedule itself remains a scientific configuration input |
| Trace/result | Canonicalization version, exact Unicode 15.0 runtime-asset hashes and pinned normalization algorithm, all named hash/preimage versions, trace schema, row ordering/framing, completeness rules, result schema, and deterministic equality contract |
| Operational exclusions that affect science | Exact prohibited fallbacks, modes, APIs, configuration namespaces, runtime substitutions, implicit retries, timeout-driven scientific decisions, and other exclusions whose absence could change scientific behavior |
| Stochastic contract | Generator, implementation, seed/stream derivation, owner, counter/draw consumption, and platform guarantee, or `NOT_APPLICABLE` until UQ-23/UQ-24 are resolved |

If a platform property cannot affect science because the implementation
provably normalizes or blocks access to it, the normalization/blocking
contract above is included instead of the observed property. For example,
wall time is not a scientific input: the included semantics state that model
decisions and terminal conditions cannot read it.

### 7.3 Run-specific metadata excluded from `ExecutionSemanticsHash`

The following remain in `RunTraceEnvelopeV1`, operational provenance, an
authorization validation record, or `ExecutionResultManifest` as applicable:

| Excluded run-specific class | Exact examples and qualification |
|---|---|
| Run identity | Execution identity, authorization-use key/record, invocation ledger position, retry/recovery case ID |
| Human/host identity | Host name, host instance ID, machine serial, cloud instance ID, user/account name, PID, parent PID, worker PIDs |
| Wall-clock observation | Actual start/end timestamps, durations, scheduling delays, log timestamps, trusted authorization-time nonce/response, clock source diagnostics |
| Location/storage | Current working directory, source checkout path, artifact/storage URI, mount/volume/inode/database row IDs, cache paths, temporary paths, publication destinations |
| Resource observations | Available memory/disk, transient CPU load, unrelated core count, process priority, thermal/power state, network latency; code may not branch scientifically on them, and an induced failure is run-specific |
| Contextual VCS | Branch name, remote URL, tag, pull-request number; exact source commit and source bytes remain included semantics |
| Non-read environment | Variables outside the normalized allowlist; the process blocks their access from result-producing code and records only names/presence when operationally useful |
| Blocked host text databases | Host `unicodedata.unidata_version`, ICU version, and locale normalization tables may be diagnostic metadata only because ECJ-1 statically blocks their use; the pinned Unicode 15.0 assets and algorithm remain included semantics |
| Logs and diagnostics | Stdout/stderr, stack traces, profiler/coverage data, runtime observations, undeclared interruption and durability evidence |
| Trust and permission evidence | Authenticity envelope, issuer/delegation chain, time/revocation evidence, signer, use-store location; these decide whether execution may start, not what the accepted science means |
| Publication | Publisher identity, target, publication time, receipt, write-once confirmation, mirror status |
| Undeclared operational failure | Host loss, signal, OOM, disk-full/torn-write/storage error, power loss, transport failure; these determine run completion/prefix classification and never become retrospective scientific inputs |

An actual CPU feature, dependency, environment value, filesystem ordering, or
resource limit moves from this table to §7.2 if any result-producing path can
read it or behave differently because of it. The binding then changes and so
does `ExecutionSemanticsHash`; the framework never makes that promotion after
candidate outcome inspection.

## 8. Base `FaultSchedule` boundary; UQ-38 remains open

The core freezes representation and guardrails, not a usable fault taxonomy.
`FaultScheduleV1` is an immutable common-envelope object whose content payload
is exactly:

```text
FaultSchedulePayloadV1 = {
    schedule_class,
    owning_study_or_validation_protocol_ref,
    fault_extension_registry_ref,
    ordered_fault_directives,
    ordering_contract_ref,
    delivery_contract_ref,
    expected_trace_completeness_rule_ref
}
```

`schedule_class` is exactly `SCIENTIFIC_STUDY` or
`INERT_VALIDATION`. The latter is not a scientific permission and is rejected
by scientific configurations. Absence of a schedule is the typed marker
`NOT_APPLICABLE`; an empty object or empty schedule is not an alias for it.

Each `FaultDirectiveV1` contains only the base fields:

```text
fault_id,
fault_kind_ref,
fault_class,
target_coordinate,
trigger_predicate_ref,
effect_payload_ref,
declared_priority,
local_sequence,
delivery_acknowledgement_rule_ref,
continuation_or_terminal_rule_ref
```

`fault_class` is either `SCIENTIFIC_MODEL_EVENT` or
`OPERATIONAL_DURABILITY_INJECTION`. A model target coordinate carries exact
epoch, phase ordinal, scope/group ID, event kind, primary object ID, and local
sequence. An operational target carries an exact registered durability-
boundary ref and occurrence ordinal; it has no epoch unless the future
extension independently binds one. Trigger predicates may read only frozen
replay inputs and named event/durability coordinates. They cannot read
candidate values, outcomes, wall time, host state, storage symptoms, or an
undeclared exception.

The core validator can prove identity/hash integrity, schedule class,
reference completeness, coordinate syntax, phase range, total ordering,
absence of duplicate coordinates, and the prohibition on forbidden trigger
inputs. It cannot interpret or deliver a directive without a separately
accepted extension registry.

UQ-38 must prospectively define, before any fault directive is instantiated or
delivered:

- every admissible scientific and inert fault kind;
- the target coordinate schema for that kind;
- effect payload and precondition semantics;
- delivery acknowledgement and exactly-once proof;
- continuation, recovery, and terminal rule;
- expected trace-completeness classification;
- interaction of coincident faults; and
- study-specific hypotheses, falsifiers, and nonclaims where scientific.

The base package SHALL contain no built-in “crash,” “drop write,” “fail edge,”
or generic arbitrary-callback kind and no default terminal rule. Until UQ-38
is resolved, `delivery_contract_ref` cannot resolve to an accepted production
implementation and any non-`NOT_APPLICABLE` schedule fails with
`FAULT_EXTENSION_UNAVAILABLE`. Abstract delivery hooks may be implemented in
I-5, but they may be checked only for rejection and non-reachability; no fault
delivery check may invent a sentinel kind. Undeclared operational failures
remain run-specific under the specification and are never converted to this
type.

## 9. Exact proposed implementation file manifest

### 9.1 Manifest rules

Paths are repository-relative. In this whole-program table, “New” and
“existing” remain historical classifications relative to original I-0
starting HEAD `4897dd69...`; §21.2 gives the exact current I-2 modified/new
states relative to the accepted I-1 base. Only the files below may be created
or modified by the planned I-1–I-9 implementation programme. Adding,
renaming, splitting, or
merging a file requires an implementation-plan revision before the affected
stage begins. Authority documents are read-only inputs and are listed
separately in §9.7.

Dependency abbreviations used below are exact package modules:

```text
err=errors, can=canonical, num=numeric, id=identity, hash=hashing,
env=envelopes, reg=registry, prim=primitives, auth=authorization,
trust=trust, cap=capabilities, exp=experiment, evt=events,
own=ownership, dur=durability, tr=traces, art=artifacts
```

No framework source module may import a top-level historical `exp_*`,
`gate*`, `finalize_*`, `test_*`, result directory, or Gate 1D-C path.

For I-3 only, the older rows and broad future catalogue in §§9.3–9.6 are
historical/provisional and are superseded by the exact 23-path manifest in
§22 and the I-3 mechanical contract. Later-stage rows remain future planning
but do not authorize those stages.

### 9.2 Packaging and cross-stage control files

| Path | Responsibility | Direct dependencies | Owner | State |
|---|---|---|---|---|
| `pyproject.toml` | Package metadata, `src` layout, Unicode package-data inclusion, supported CPython line, build backend, static tooling, and test groups; no scientific entry point. I-4 alone may add the exact audited Ed25519 provider metadata selected under UQ-25, in the same reviewed change set as the lock finalization. | I-1 build tooling; I-4 UQ-25 provider decision and `requirements-framework.lock` | I-1; exact crypto dependency metadata extension I-4 | New |
| `requirements-framework.lock` | Exact hashed framework dependency closure; initially stdlib-only and extended/finalized during I-4 with the audited Ed25519 provider selected under UQ-25 | `pyproject.toml`, UQ-25 audit | I-1; exact crypto dependency extension/finalization I-4 | New |
| `.github/workflows/tests.yml` | Add push/PR T0 and T1 jobs plus a separately gated `workflow_dispatch` T2 job that first validates exact T2 authority; never add a T3 framework job or Gate 1D-C invocation | Lock file and validation commands | I-9 | Existing, modify |

The cross-stage-control table above is unchanged. Revision v0.2.1
recorded the explicit-backend/stdlib-only contradiction as a current blocker;
that status is historical. The existing packaging amendment and matching
contract prospectively resolve only their stated packaging scope. Revision
v0.2.7 does not edit, repeat, or redefine that resolution, select a different
backend or dependency, or add any packaging/control manifest path. Its I-2
ownership amendments are exactly those in §21.2.

The existing `requirements.txt` remains the legacy figure/PDF dependency file
and is not changed or reused as the framework lock.

### 9.3 Core source files

| Path | Responsibility | Direct dependencies | Owner | State |
|---|---|---|---|---|
| `src/ebu_framework/__init__.py` | Version constant and reviewed re-exports of only the public interfaces in §10 | Stage-complete modules only | I-1, extended by owning stages | New |
| `src/ebu_framework/py.typed` | PEP 561 marker for the reviewed typed public surface | Package type annotations | I-1 | New |
| `src/ebu_framework/data/__init__.py` | Package-data boundary; exports no API and executes no code | None | I-1 | New |
| `src/ebu_framework/data/unicode/15.0.0/UnicodeData.txt` | Exact raw Unicode 15.0.0 assignment, canonical decomposition, and canonical-combining-class data with the §3.2 digest | Unicode Consortium UCD 15.0.0 source bytes | I-1 | New |
| `src/ebu_framework/data/unicode/15.0.0/DerivedNormalizationProps.txt` | Exact raw Unicode 15.0.0 `Full_Composition_Exclusion` and normalization-property data with the §3.2 digest | Unicode Consortium UCD 15.0.0 source bytes | I-1 | New |
| `src/ebu_framework/errors.py` | I-1 failures plus only the v0.1.7/v0.2.7 common fields, stable failure identity, closed I-1 compatibility map, and exact I-2 failure codes; no domain behavior | Stdlib only; must not import any package module | I-1; narrowly extended I-2 | New |
| `src/ebu_framework/canonical.py` | Strict ECJ-1 projection, parser, encoder, pinned-table NFC/assignment, code-point ordering, asset-digest verification, and host-Unicode rejection rules | `err`, the two pinned Unicode 15.0.0 runtime assets | I-1 | New |
| `src/ebu_framework/identity.py` | `ScientificId`, semantic versions, allocation claims, `ObjectRef`, typed digest wrappers | `can`, `err` | I-1 | New |
| `src/ebu_framework/hashing.py` | All exact §5 projections, SHA-256 domains, binary framing, and raw-source labeling | `can`, `id`, `err` | I-1; extended I-3/I-5 | New |
| `src/ebu_framework/envelopes.py` | Common immutable envelope storing exact `CanonicalBytes`, fresh `parse_ecj1` validation/hash decoding without a mutable cache, recursive direct stored-hash occurrence exclusion, metadata separation, and pure lifecycle/supersession validation; no alias/graph resolution or registry mutation | `can` only for `CanonicalBytes` and `parse_ecj1`; `id`, `hash`, `err` | I-2 | New |
| `src/ebu_framework/registry.py` | Immutable namespace/object registries, alias resolution, and collision checks; I-2 may only strengthen `RegistryRecord.lifecycle_status` to exact `LifecycleStatus` while preserving draft-only registration | `can`, `id`, `err`; I-2 adds `env` | I-1; narrowly type-strengthened I-2; acceptance mutation I-4 | New |
| `src/ebu_framework/data/core_registry_v1.json` | Reviewed literal bootstrap namespace/schema IDs and allocation-policy refs; no study or domain entries | ECJ-1, §4 bootstrap exception | I-1 | New |
| `src/ebu_framework/numeric.py` | Exact core-number records/projections/operation matrix, I-2-owned runtime constraints, and non-executing `NumericalPolicyV1` protocol/completeness validation | `can`, `id`, `err` | I-2 | New |
| `src/ebu_framework/primitives.py` | Exact dimensions, units/conversions, quantities, resources/services, regions/boundaries, clocks/horizons, resolution, uncertainty, and compatibility predicates | `num`, `id`, `env`, `err`; no registry lookup | I-2 | New |
| `src/ebu_framework/state.py` | Declarative `SystemState`/`RepresentedState`, state/projection preimages, static and protected projection contracts | `prim`, `id`, `env`, `hash`, `err` | I-3 | New |
| `src/ebu_framework/distortion.py` | Declarative distortion/evaluation contracts and numerical-policy binding; no domain model | `state`, `prim`, `num`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/actions.py` | Action definitions/instances, supports, intervals, lifecycle, and proposal records | `state`, `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/network.py` | Providers, topology, capacity loci, provisional routes, failures/status records | `state`, `prim`, `id`, `env`, `reg`, `err` | I-3 | New |
| `src/ebu_framework/commitments.py` | Commitments, reservations, capacity records, queues, admissions, shortfalls | `actions`, `network`, `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/observation.py` | Measurements, calibration, availability time, uncertainty, information-source records | `state`, `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/scheduling.py` | Open-loop schedules, comparator declarations, immutable event declarations | `actions`, `network`, `commitments`, `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/policy.py` | Policy/interface records, immutable memory, decision records, read sets, memory transitions | `observation`, `scheduling`, `prim`, `id`, `env`, `hash`, `err` | I-3 | New |
| `src/ebu_framework/causal.py` | Causal-model protocol, identification statuses, contribution/remainder records; no model implementation | `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/settlement.py` | Quote, receipt/group/child, allocation, share/residual, and closure records/checks; no institutional default | `prim`, `id`, `env`, `err` | I-3 | New |
| `src/ebu_framework/ledger.py` | Typed predecessor-linked append-only ledgers and evidence-ledger records | `prim`, `id`, `env`, `hash`, `err` | I-3 | New |
| `src/ebu_framework/faults.py` | Base §8 types and static rejection/extension boundary only | `prim`, `id`, `env`, `hash`, `err` | I-3; hooks I-5 | New |
| `src/ebu_framework/experiment.py` | Configuration/binding/stage records, acceptance projection, UQ-36 split | `prim`, `policy`, `faults`, `id`, `env`, `hash`, `err` | I-3 | New |
| `src/ebu_framework/artifacts.py` | Result/summary/figure/manifest/publication/correction record types and byte refs | `exp`, `ledger`, `prim`, `id`, `env`, `hash`, `err` | I-3; behavior I-8 | New |

### 9.4 Authorization, execution, and scientific adapters

| Path | Responsibility | Direct dependencies | Owner | State |
|---|---|---|---|---|
| `src/ebu_framework/trust.py` | Trust profile, issuer/delegation registries, signature envelopes, time/revocation evidence, Ed25519 provider boundary | `id`, `env`, `hash`, `can`, `err`; audited crypto provider | I-4 | New |
| `src/ebu_framework/authorization.py` | Stage authorization records, exact validation order, evidence bundles, validation records | `trust`, `exp`, `art`, `ledger`, `id`, `hash`, `err` | I-4 | New |
| `src/ebu_framework/authorization_use.py` | Exact local SQLite compare-and-consume and append-only use records | `auth`, `ledger`, `id`, `hash`, `err`, stdlib `sqlite3` | I-4 | New |
| `src/ebu_framework/capabilities.py` | Information-view capabilities, availability/read-set checks, T0–T3 capability tokens and escalation | `auth`, `policy`, `observation`, `exp`, `hash`, `err` | I-4 | New |
| `src/ebu_framework/events.py` | Ten phase ordinals, `EventKey`, deterministic ordering, immutable transition/commit record types | `actions`, `faults`, `prim`, `id`, `hash`, `err` | I-5 | New |
| `src/ebu_framework/ownership.py` | Epoch-wide physical update-ownership construction and conflict validation | `events`, `state`, `id`, `hash`, `err` | I-5 | New |
| `src/ebu_framework/durability.py` | Abstract atomic store contracts, typed commit outcomes, prefix preservation, policy-memory transaction boundary | `events`, `ownership`, `policy`, `ledger`, `hash`, `err` | I-5; backend decision deferred UQ-26 | New |
| `src/ebu_framework/traces.py` | Canonical row, framed stream, prefix, full trace, run-envelope construction and validation | `events`, `policy`, `state`, `exp`, `art`, `hash`, `can`, `err` | I-5; finalization I-8 | New |
| `src/ebu_framework/execution.py` | T3 entry/lease, exact ten-phase orchestration, proposal/screen/commit contracts, anti-disguise guards | `auth`, `cap`, `exp`, `events`, `own`, `dur`, `tr`, scientific adapter modules; never `validation` | I-5; extended I-6/I-7 | New |
| `src/ebu_framework/bridge.py` | Exact Bridge v0.2 grouping, comparators, group measurement, `N_G`, interaction, causal/settlement separation | `state`, `distortion`, `actions`, `settlement`, `prim`, `id`, `err` | I-6 | New |
| `src/ebu_framework/dynamic.py` | Dynamic-foundation capacity/queue/delay/topology/reroute/delayed-effect/natural-drive mechanics and route guard | `network`, `commitments`, `scheduling`, `policy`, `events`, `ownership`, `state`, `prim`, `err` | I-7 | New |
| `src/ebu_framework/provenance.py` | Source/runtime/environment inventory and §7 projection/run-metadata enforcement | `exp`, `art`, `tr`, `id`, `hash`, `err` | I-8 | New |
| `src/ebu_framework/recovery.py` | Evidence-classified recovery and immutable prefix/same-bytes rules; no runner entry | `art`, `tr`, `dur`, `auth`, `ledger`, `err` | I-8 | New |
| `src/ebu_framework/publication.py` | Manifest finalization, inert write-once store protocol, separate publication/correction records | `art`, `provenance`, `recovery`, `auth`, `ledger`, `hash`, `err` | I-8 | New |
| `src/ebu_framework/validation.py` | Safe T0/T1/T2 harness descriptors and forbidden-reachability checks; cannot import `execution` | `can`, `num`, `id`, `hash`, `prim`, record modules, `err` | I-9 | New |

### 9.5 Validation fixtures

These files contain only static data. No fixture is an accepted world,
configuration, policy, seed, trajectory, or result.

| Path | Responsibility | Direct dependencies | Owner | State |
|---|---|---|---|---|
| `tests/framework/fixtures/ecj1_vectors.json` | Valid/invalid Unicode, key-order, escaping, integer, and timestamp byte vectors, including assigned Unicode 15.0 boundaries and mandatory rejection of later-assigned U+2EBF0 | §3 and pinned Unicode 15.0.0 assets | I-1 | New |
| `tests/framework/fixtures/unicode/15.0.0/NormalizationTest.txt` | Exact complete Unicode 15.0.0 NFC conformance corpus; required raw SHA-256 `fb9ac8cc154a80cad6caac9897af55a4e75176af6f4e2bb6edc2bf8b1d57f326` | `https://www.unicode.org/Public/15.0.0/ucd/NormalizationTest.txt` | I-1 | New |
| `tests/framework/fixtures/hash_preimages_v1.json` | Exact §5 preimage/exclusion/domain vectors with synthetic values | ECJ-1 vectors | I-1 | New |
| `tests/framework/fixtures/scientific_id_vectors_v1.json` | Namespace/allocation/idempotency/collision vectors | §4 | I-1 | New |
| `tests/framework/fixtures/numeric_vectors_v1.json` | Exact 335-vector ordered §21 fixture with block counts `18,35,42,4,36,107,20,41,32`, authority hashes, derived projections/hex/failure IDs, and no domain policy or tolerance | Specification §21.8 and plan §21.5 | I-2 | New |
| `tests/framework/fixtures/authorization_vectors_v1.json` | RFC 8032 plus synthetic trust/delegation/revocation/time/single-use records | §6; synthetic keys only | I-4 | New |
| `tests/framework/fixtures/bridge_m1_m9_v1.json` | Frozen hand-derived Bridge v0.2 M1–M9 inputs/statuses/expected exact values | Bridge v0.2 §14 | I-6 | New |
| `tests/framework/fixtures/dynamic_static_v1.json` | Frozen independent-provider, queue, delay, route-failure, timing, and worsening arithmetic from the dynamic foundation | Dynamic foundation §9 | I-7 | New |

### 9.6 Validation code files

| Path | Responsibility | Direct dependencies | Owner | State |
|---|---|---|---|---|
| `tests/framework/safety.py` | Synthetic namespace/store factory and process-level forbidden import/call guard | No production T3 module | I-1; extended I-9 | New |
| `tests/framework/test_ecj1.py` | T0 exact canonical bytes/rejections, complete pinned NFC conformance, asset-integrity failure, later-Unicode rejection, and host-database independence | `canonical`, ECJ-1 vectors, pinned `NormalizationTest.txt` | I-1 | New |
| `tests/framework/test_hash_preimages.py` | T0 domains, exclusions, self-reference rejection, byte frames | `hashing`, hash vectors | I-1 | New |
| `tests/framework/test_identity_registry.py` | T0/T1 allocation, resolution, immutability, alias, collision checks | `identity`, `registry`, ID vectors | I-1 | New |
| `tests/framework/test_numeric.py` | T0 constructor/projection/normalization, complete exact-operation matrix, explicit conversion, policy completeness/refusal, deterministic failures, fixture-schema/hash checks | `numeric`, `errors`, numeric vectors | I-2 | New |
| `tests/framework/test_primitives_envelopes.py` | T0 primitive compatibility, resolution/uncertainty, nine exact canonical-byte envelope immutability/hash/cache checks, metadata/lifecycle exclusion, lifecycle/supersession, exact export/29-edge-DAG/forbidden-reachability AST audit | source text/AST plus `primitives`, `envelopes`, `registry`, numeric vectors; no production import during AST audit | I-2 | New |
| `tests/framework/test_declarative_records.py` | T0 representability, configuration/binding split, route/fault unresolved guards | I-3 record modules | I-3 | New |
| `tests/framework/test_policy_memory.py` | T0 hashes, lineage, epoch, and stateless/stateful applicability; no policy callback or durability claim | `policy`, `hashing` | I-3 | New |
| `tests/framework/test_authorization.py` | T1 synthetic signatures, thresholds, attenuation, freshness, revocation, exact scope | `trust`, `authorization`, auth vectors | I-4 | New |
| `tests/framework/test_authorization_use.py` | T1 local temp-SQLite consume, duplicate, ambiguous/failure classification | `authorization_use`, auth vectors | I-4 | New |
| `tests/framework/test_capabilities.py` | T1 fabricated view visibility/read-set denial; no scientific policy | `capabilities`, fabricated fields | I-4 | New |
| `tests/framework/test_event_ownership.py` | T0 order/key checks and T1 opaque-coordinate ownership conflicts; no transformation | `events`, `ownership` | I-5 | New |
| `tests/framework/test_inert_durability.py` | T1 dummy bytes/store atomicity classifications and undeclared-prefix preservation; no `FaultSchedule` delivery | `durability`, `traces`, inert store | I-5 | New |
| `tests/framework/test_bridge_exact_fixtures.py` | Separately authorized T2 isolated M1–M9 exact functions; no state chaining | `bridge`, Bridge fixtures, T2 capability | I-6 | New |
| `tests/framework/test_dynamic_static_identities.py` | Separately authorized T2 isolated capacity/queue/delay arithmetic; no epoch transition | `dynamic`, dynamic fixtures, T2 capability | I-7 | New |
| `tests/framework/test_route_guards.py` | T0 refusal of unfrozen Part VII semantics | `network`, `dynamic` | I-7 | New |
| `tests/framework/test_artifact_recovery_publication.py` | T1 dummy trace/artifact/manifest/prefix/same-bytes/write-once checks | `traces`, `artifacts`, `recovery`, `publication` | I-8 | New |
| `tests/framework/test_validation_reachability.py` | T0 AST/import/export scan proving validation cannot reach T3 or historical runners/finalizers | Repository source tree as text only | I-9 | New |

### 9.7 Existing read-only authority dependencies

These existing files are dependencies but are not implementation change
targets: `AGENTS.md`, `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md`,
this accepted plan once reviewed, `EBU_FUTURE_BOOKS_STRUCTURE.md`,
`SEQUENTIAL_PARALLEL_BRIDGE.md`, and
`DYNAMIC_COORDINATION_FOUNDATION.md`. Every implementation stage re-hashes
them. A mismatch stops the stage; it is not repaired inside implementation.

## 10. Public interface capability classification

### 10.1 Classification rule

Only the interfaces below may be re-exported from `ebu_framework`. A callable
not listed is private implementation detail. The class describes the highest
direct capability the public interface accepts:

- **T0**: parsing, projection construction without domain evaluation, typing,
  hashing, serialization, algebraic/structural validation, or read-only
  resolution. A T0 interface may accept an already supplied immutable
  registered or candidate scientific record as opaque typed data, but it
  cannot evaluate that record's scientific meaning, derive or inspect an
  outcome, invoke scientific behavior, mutate scientific or operational
  state, choose a result-sensitive value, or make an acceptance/publication
  decision.
- **T1**: synthetic/operational durability or workflow mutation on inert or
  declarative records; no scientific function, state, policy, outcome, or
  runner is accepted.
- **T2**: exactly one isolated pure scientific mapping on a frozen analytical
  fixture carrying a valid `T2FixtureCapability`; no successor can feed
  another call.
- **T3**: can evaluate a registered/candidate scientific object as science,
  derive or inspect a candidate outcome, call a scientific policy,
  transformation, or measurement, advance state, make a result-sensitive
  decision, or participate directly in a scientific run or protected
  post-execution scientific-artifact operation. It requires a live
  `ScientificExecutionLease` or the separately authorized post-execution
  stage evidence named by the interface. Mere structural receipt of an
  immutable scientific record does not by itself make a pure operation T3.

The table records each interface's intrinsic maximum reachable capability in
isolation. For an actual invocation, classification is the maximum of the
interface's intrinsic class and its enclosing work: a T0/T1 helper called
inside T2 or T3 work is covered by that enclosing T2/T3 authorization,
classification, evidence, and trace. This contextual escalation does not
permanently reclassify the helper, and no wrapper, callback, subclass,
reflection, or test-framework call may lower either class.

### 10.2 Public value and protocol types

For I-3, the historical all-stage catalogue below is superseded by §22: only
the exact 69 retained I-3 types are post-I-3 exports. Every type assigned to a
later stage is excluded even when the older table grouped its semantic shape
near I-3 records.

Every type constructor in this table is T0-capable: it creates or parses an
immutable draft/value/protocol declaration and cannot accept a callback,
access a registry implicitly, mutate a store, inspect an outcome, or advance
state. A constructed value acquires the class of the operation to which it is
later supplied. Enum member access is likewise T0. No unlisted type is
re-exported.

| Owner | Exact public types (all T0-capable constructors unless noted) |
|---|---|
| `errors` | `Applicability`, `CanonicalTraceState`, `DurabilityState`, `FailureCode`, `FailureEnvelope`, `FailureEventKey`, `FailureEvidenceRef`, `FailureId`, `FailureInterfaceRef`, `FailureObjectRef`, `FailureStage`, `PolicyMemoryAdvance`, `RetryClass`, `ScientificStatusEffect`, `StateAdvance` |
| `canonical` | `ECJ1Value`, `CanonicalBytes`, `CanonicalizationVersion` |
| `identity` | `ScientificId`, `ScientificIdAllocationClaimV1`, `SemanticVersion`, `ObjectRef`, `ObjectContentHash`, `StatePayloadHash`, `PolicyMemoryPayloadHash`, `AugmentedClosedLoopReplayStateHash`, `RepresentedStateProjectionHash`, `InformationViewHash`, `ProposalSetHash`, `ExecutionSemanticsHash`, `CanonicalTraceRowHash`, `CanonicalTracePrefixHash`, `CanonicalScientificTracePayloadHash`, `ArtifactByteHash`, `SourceFileRawSha256`, `AuthorizationUseKey` |
| `numeric` | `Binary64BitsV1`, `ComparisonResult`, `Completeness`, `CoreNumberV1`, `DecimalV1`, `ErrorBound`, `ExactConversion`, `IntegerV1`, `NumericalOperation`, `NumericalPolicyV1`, `NumericalResult`, `NumericalVariant`, `OperandValidationResult`, `QuantityContext`, `RationalV1`, `RuntimeConstraintSet` |
| `envelopes` | `CommonObjectEnvelope`, `LifecycleStatus`, `LifecycleTransition`, `LifecycleValidationResult`, `RecordMetadata`, `SupersessionRelation`, `SupersessionValidationResult` |
| `registry` | `NamespaceEntry`, `NamespaceRegistrySnapshot`, `RegistryRecord`, `AliasRecord`, `ResolutionRecord` |
| `primitives` | `AccountingBoundary`, `ClaimStatus`, `ClockSystem`, `CompatibilityResult`, `ConversionRule`, `Dimension`, `Duration`, `Epoch`, `Horizon`, `Instant`, `Quantity`, `Region`, `ResolutionDetail`, `ResolutionState`, `ResourceType`, `ServiceType`, `SignConvention`, `UncertaintyKind`, `UncertaintyRecord`, `Unit` |
| `state` | `SystemState`, `RepresentedState`, `ProjectionContract`, `StatePayloadPreimageV1`, `RepresentedStateProjectionPreimageV1` |
| `distortion` | `DistortionModel`, `DistortionEvaluation`, `DistortionDomainFailure` |
| `actions` | `ActionDefinition`, `ActionInstance`, `EffectiveInterval`, `WriteSupport`, `ConstraintSupport`, `TransitionProposal`, `ActionStatus` |
| `network` | `Provider`, `ProviderNetwork`, `TopologySnapshot`, `TopologyChangeEvent`, `CapacityLocus`, `RoutePlan`, `RouteRef`, `RouteSemanticsStatus`, `AvailabilityStatus` |
| `commitments` | `Commitment`, `Reservation`, `CapacityRecord`, `AdmissionDecision`, `QueueRecord`, `ReservationShortfall`, `CongestionRecord` |
| `observation` | `Measurement`, `MeasurementContract`, `CalibrationRecord`, `InformationSourceRecord` |
| `scheduling` | `Schedule`, `ComparatorSchedule`, `ComparatorKind`, `CoordinationEventDeclaration` |
| `policy` | `Policy`, `InformationContract`, `InformationView`, `InformationReadSet`, `PolicyMemoryState`, `PolicyDecisionRecord`, `MemoryMode` |
| `causal` | `CausalModel`, `CausalContributionRecord`, `CausalIdentificationStatus`, `CausalRemainder` |
| `settlement` | `Quote`, `Receipt`, `GroupReceipt`, `ChildActionRecord`, `SettlementRule`, `SettlementShare`, `GroupResidual`, `SettlementClosureRecord` |
| `ledger` | `Ledger`, `LedgerEntry`, `EvidenceLedgerEntry`, `LedgerKind` |
| `faults` | `FaultScheduleV1`, `FaultDirectiveV1`, `FaultClass`, `FaultTargetCoordinate`, `FaultScheduleClass` |
| `experiment` | `ExperimentConfiguration`, `ExecutionBinding`, `ExecutionMode`, `RuntimeMetadata`, `OperationalExclusion`, `ExecutionIdentity` |
| `trust` | `TrustProfileV1`, `IssuerRegistrySnapshotV1`, `IssuerEntry`, `DelegationCredentialV1`, `RevocationSnapshotV1`, `TrustedTimeAttestationV1`, `AuthorizationAuthenticityEnvelopeV1`, `TrustEvidenceEnvelopeV1` |
| `authorization` | `StageAuthorization`, `AuthorizedOperation`, `AuthorizationEvidenceBundle`, `AuthorizationValidationRecord` |
| `authorization_use` | `AuthorizationUseRecord`, `AuthorizationUseStatus` |
| `capabilities` | `T2FixtureCapability` (private constructor; T2 use only), `ScientificExecutionLease` (private constructor; T3 use only), `AccessCapability`, `CapabilityClass` |
| `events` | `EventKey`, `PhaseOrdinal`, `PhaseCommitRecord`, `TraceCompleteness`, `EventDeclaration` |
| `ownership` | `UpdateOwnershipClaim`, `EpochUpdateOwnership`, `OwnershipValidationRecord` |
| `durability` | `AtomicStore`, `PolicyDecisionStore`, `PhaseCommitStore`, `CommitOutcome`, `DurablePrefixEvidence` |
| `traces` | `CanonicalTraceRow`, `CanonicalTracePrefix`, `CanonicalScientificTracePayloadV1`, `RunTraceEnvelopeV1`, `TraceHeader`, `TraceFooter` |
| `artifacts` | `ResultArtifact`, `SummaryArtifact`, `FigureArtifact`, `ExecutionResultManifest`, `PublicationRecord`, `CorrectionRecord`, `ArtifactRecord` |
| `bridge` | `DependencyEdge`, `JointTransitionGroup`, `AdmissibleComparatorSet`, `GroupMeasurement`, `SameBaselineNonadditivity`, `ComparatorInteraction`, `NonserializableGroup` |
| `dynamic` | `DelayRecord`, `InTransitRecord`, `DelayedEffect`, `DynamicUpdateRecord`, `NaturalDriveContract` |
| `provenance` | `SourceProvenance`, `RuntimeProvenance`, `EnvironmentProvenance`, `ExecutionSemanticsProjection` |
| `recovery` | `RecoveryClassification`, `RecoveryRecord` |
| `publication` | `WriteOnceStore`, `PublicationReceipt` |

Abstract protocols (`NumericalPolicyV1`, `Policy`, `CausalModel`, atomic-store
protocols, and `WriteOnceStore`) declare methods but do not make their
implementations lower-capability. Invoking their scientific methods is
possible only through the classified callables below.

### 10.3 Exhaustive planned callable catalogue

For post-I-3 API purposes this all-stage planning catalogue is superseded by
§22. I-3 exports only its 23 `validate_*` callables. Builders, acceptance,
scientific evaluation, mutation, trace, dynamic, finalization, and publication
callables remain assigned to their exact later stages and are absent from the
post-I-3 root API.

| Public interface | Owner | Class | Capability boundary |
|---|---|---:|---|
| `parse_ecj1` | `canonical` | T0 | Strict parse only; noncanonical bytes rejected |
| `encode_ecj1` | `canonical` | T0 | Typed ECJ-1 value to exact bytes |
| `normalize_core_number` | `numeric` | T0 | Lossless §2 normalization only |
| `apply_exact_core_operation` | `numeric` | T0 | Integer/rational/finite-decimal operation only when result is exact and uniquely represented; otherwise `NUMERICAL_POLICY_REQUIRED` |
| `decimal_to_rational_exact` | `numeric` | T0 | Sole explicit cross-variant I-2 conversion; exact and total for `DecimalV1` |
| `validate_numerical_policy` | `numeric` | T0 | Contract completeness; no domain evaluation |
| `allocate_scientific_id` | `registry` | T1 | Atomically records a content-neutral allocation claim |
| `parse_scientific_id` | `identity` | T0 | Grammar validation only |
| `parse_semantic_version` | `identity` | T0 | Grammar validation only |
| `compute_object_content_hash` | `hashing` | T0 | Exact §5.2 projection |
| `compute_state_payload_hash` | `hashing` | T0 | Exact §5.2 projection; no state generation |
| `compute_policy_memory_payload_hash` | `hashing` | T0 | Exact §5.2 projection |
| `compute_augmented_replay_state_hash` | `hashing` | T0 | Component-hash pairing only |
| `compute_represented_state_projection_hash` | `hashing` | T0 | Exact projection hash only |
| `compute_information_view_hash` | `hashing` | T0 | Hashes a supplied view; does not build one |
| `compute_proposal_set_hash` | `hashing` | T0 | Hashes supplied ordered proposals |
| `compute_execution_semantics_hash` | `hashing` | T0 | Exact UQ-36 projection only |
| `compute_canonical_trace_row_hash` | `hashing` | T0 | Exact row preimage only |
| `compute_canonical_trace_prefix_hash` | `hashing` | T0 | Exact confirmed-prefix preimage only |
| `compute_canonical_trace_payload_hash` | `hashing` | T0 | Exact complete/fault-qualified payload preimage only |
| `compute_artifact_byte_hash` | `hashing` | T0 | Exact binary frame only |
| `compute_source_file_raw_sha256` | `hashing` | T0 | Conventional raw digest with distinct type |
| `validate_object_envelope` | `envelopes` | T0 | Envelope/preimage/lifecycle consistency and recursive direct stored-hash occurrence exclusion; no alias/graph resolution |
| `validate_lifecycle_transition` | `envelopes` | T0 | Pure closed-graph and typed-authorization-presence validation; no mutation |
| `validate_supersession_relation` | `envelopes` | T0 | Pure immutable identity/schema/version/ancestry validation; no mutation |
| `resolve_ref` | `registry` | T0 | Exact ID/version/hash resolution |
| `resolve_alias` | `registry` | T0 | Presentation alias to one exact ref; no accepted hash uses alias |
| `register_draft` | `registry` | T1 | Immutable draft insertion only |
| `accept_registry_object` | `registry`/`authorization` | T1 | I-4 only: authorization-gated lifecycle freeze; absent from the post-I-2 API |
| `supersede_registry_object` | `registry`/`authorization` | T1 | I-4 only: authorized new immutable status/relation records; absent from the post-I-2 API |
| `validate_dimension_compatibility` | `primitives` | T0 | Exact ref and complete basis-exponent equality |
| `validate_unit_compatibility` | `primitives` | T0 | Exact identity or supplied rule with observable endpoints, direction, three-way dimension, and declared horizon form only |
| `validate_conversion_rule` | `primitives` | T0 | Supplied rule plus source/target units: factor/offset, direction/endpoints, three-way dimension, and declared horizon form |
| `validate_quantity` | `primitives` | T0 | Dimensions, unit/type/region/time/boundary checks |
| `convert_quantity_exact` | `primitives` | T0 | Only a pinned exact conversion from explicit quantity/source/target/rule arguments; approximate conversion requires T3 domain policy |
| `validate_resource_service_compatibility` | `primitives` | T0 | Symmetric exact declared compatibility only |
| `validate_region_compatibility` | `primitives` | T0 | Exact identity or explicit declared common-parent links; no membership/disjointness resolution or aggregation |
| `validate_boundary_compatibility` | `primitives` | T0 | Exact identity or declared common-parent links plus supplied cross-effect treatment-key coverage; no aggregation/adequacy claim |
| `validate_sign_convention_compatibility` | `primitives` | T0 | Matching typed applicability and exact ref only |
| `validate_time_basis` | `primitives` | T0 | Rate applicability then exact time-basis ref equality |
| `validate_clock_compatibility` | `primitives` | T0 | Exact clock-ref equality |
| `validate_horizon` | `primitives` | T0 | Clock/endpoints and exact supplied pending-effect/due-ref pair declarations only |
| `validate_uncertainty_record` | `primitives` | T0 | Kind/unit/provenance and explicit violated-contract role checks; no contract resolution or inference |
| `validate_resolution_detail` | `primitives` | T0 | Closed present/pending/failed/partial/unresolved/out-of-boundary predicates |
| `validate_state_record` | `state` | T0 | Shape, refs, payload hash, physical/memory separation |
| `validate_projection_contract` | `state` | T0 | Static required/excluded coordinate contract |
| `project_static_fixture` | `state` | T2 | One allowlisted isolated synthetic state only |
| `project_state` | `state` | T3 | Registered/candidate state projection |
| `evaluate_distortion_fixture` | `distortion` | T2 | One allowlisted exact-lossless fixture contract; no domain approximation/tolerance |
| `evaluate_distortion` | `distortion` | T3 | Scientific distortion evaluation |
| `validate_action_definition` | `actions` | T0 | Declarative contract only |
| `build_schedule` | `scheduling` | T0 | Constructs/validates a declarative schedule; cannot evaluate it |
| `validate_policy_memory_state` | `policy` | T0 | Applicability, hash, schema, epoch, lineage |
| `policy_propose` | `policy` | T3 | Calls a scientific policy on a permitted live view |
| `commit_policy_decision` | `policy`/`durability` | T3 | Atomically commits live decision/next memory/trace row |
| `measure_state` | `observation` | T3 | Produces/inspects a scientific measurement |
| `append_operational_ledger_entry` | `ledger` | T1 | Authorization/use/publication/correction and inert validation ledgers only |
| `append_scientific_ledger_entry` | `ledger` | T3 | Physical/receipt/causal/settlement evidence in a scientific context |
| `validate_fault_schedule_boundary` | `faults` | T0 | Base structure and forbidden-input checks only |
| `deliver_declared_fault` | `faults`/`execution` | T3 | Unavailable until UQ-38 extension and T3 authority |
| `accept_experiment_configuration` | `experiment` | T1 | Exact external preregistration authority; freezes content; no execution |
| `accept_execution_binding` | `experiment` | T1 | Exact external pre-execution authority; freezes binding; no execution |
| `classify_execution_runtime_property` | `experiment`/`provenance` | T0 | Closed §7 enumeration; unknown class rejected |
| `validate_stage_authorization` | `authorization` | T1 | Full §6 validation without entering target operation |
| `consume_stage_authorization` | `authorization_use` | T1 | Durable one-use burn; returns target-specific entry evidence, never a scientific lease by itself |
| `build_synthetic_information_view` | `capabilities` | T1 | Fabricated fields only; rejects scientific refs |
| `build_information_view` | `capabilities` | T3 | Live permitted scientific view |
| `validate_information_read_set` | `capabilities` | T3 | Validates a live policy decision read set |
| `order_event_keys` | `events` | T0 | Total ordering/duplicate detection on declarations |
| `validate_update_ownership` | `ownership` | T0 | Static claim-disjointness check; no commit |
| `classify_inert_commit_failure` | `durability` | T1 | Dummy store/bytes only |
| `classify_undeclared_interruption` | `recovery` | T1 | Evidence classification; cannot resume or execute |
| `begin_bound_scientific_execution` | `execution` | T3 | Validates/consumes exact authority and creates one live lease; the invocation has begun even before a state step |
| `propose_phase_updates` | `execution` | T3 | Calls scientific transition proposal for phases 1/2/9/10 |
| `screen_and_admit` | `execution` | T3 | Applies scientific constraints/capacity/queue rules |
| `propose_joint_transition` | `execution` | T3 | Calls scientific joint transformation on common pre-state |
| `commit_phase_updates` | `execution` | T3 | Can advance physical state atomically |
| `advance_epoch` | `execution` | T3 | Exact ten-phase state advancement |
| `classify_joint_groups_fixture` | `bridge` | T2 | One frozen M1–M9 grouping fixture |
| `classify_joint_groups` | `bridge` | T3 | Registered/candidate actions and boundaries |
| `compute_group_measurement_fixture` | `bridge` | T2 | One frozen M1–M9 exact calculation |
| `compute_group_measurement` | `bridge` | T3 | Scientific endpoint/group calculation |
| `compute_same_baseline_nonadditivity_fixture` | `bridge` | T2 | One frozen M1–M9 exact calculation |
| `compute_same_baseline_nonadditivity` | `bridge` | T3 | Scientific diagnostic; never causal allocation |
| `compute_comparator_interaction_fixture` | `bridge` | T2 | One frozen named-comparator calculation |
| `compute_comparator_interaction` | `bridge` | T3 | Scientific comparator-relative calculation |
| `validate_settlement_closure` | `settlement` | T0 | Exact supplied share-plus-residual algebra only |
| `infer_causal_contributions` | `causal` | T3 | Separately authorized result interpretation; unsupported without identified model |
| `allocate_settlement` | `settlement` | T3 | Separately authorized institutional operation on immutable physical evidence |
| `validate_dynamic_static_identity` | `dynamic` | T2 | One frozen capacity/queue/delay identity; no successor chaining |
| `propose_reroute` | `dynamic` | T3 | Live unfinished-suffix scientific proposal; Part VII guard enforced |
| `finalize_inert_trace_payload` | `traces` | T1 | Dummy validation rows only; rejects scientific refs |
| `finalize_trace_payload` | `traces` | T3 | Finalizes already durable scientific rows under exact finalization authority; cannot create rows or advance state |
| `finalize_inert_manifest` | `publication` | T1 | Dummy artifact inventory only; rejects scientific refs |
| `finalize_execution_result_manifest` | `publication` | T3 | Pre-publication scientific inventory under exact authority; no runner |
| `recover_inert_artifacts` | `recovery` | T1 | Dummy same-bytes/prefix reconstruction only |
| `recover_artifacts` | `recovery` | T3 | Authorized recovery of scientific artifacts; no model call |
| `create_inert_correction_record` | `publication` | T1 | Dummy linked immutable record only |
| `create_correction_record` | `publication` | T3 | Authorized scientific-artifact correction relation; no recomputation or interpretation |
| `publish_inert_artifacts` | `publication` | T1 | Dummy write-once bytes and separate record |
| `publish_artifacts` | `publication` | T3 | Authorized real artifact publication; runner import forbidden |

`apply_numerical_policy` is intentionally not a public generic interface. A
domain operation invokes its exact accepted policy inside its own T2 fixture
wrapper or T3 scientific interface, preventing a validation caller from using
the numeric layer as an unclassified scientific evaluator.

## 11. Static and synthetic validation plan

### 11.1 Non-reachability architecture

The validation plan has four simultaneous controls:

1. `ebu_framework.validation` and all T0/T1/T2 tests are statically forbidden
   from importing `ebu_framework.execution`. Production modules are forbidden
   from importing `ebu_framework.validation`.
2. Every T3 interface requires a `ScientificExecutionLease` whose constructor
   is private to the successful `begin_bound_scientific_execution` path after
   external-authenticity validation and durable single-use consumption.
   Deserialization, copying, subclassing, and synthetic namespaces cannot
   create a valid lease.
3. T2 wrappers require an allowlisted fixture ID/hash and a
   `T2FixtureCapability` issued only by the validation harness after matching
   the frozen fixture inventory. They accept one input and do not return a
   `SystemState` or value accepted by another T2 wrapper.
4. A static AST/import/export scan fails if validation code references a T3
   interface, a historical runner/finalizer/experiment module, any Gate 1D-C
   path, any `results/` path, or a network/subprocess entry capable of starting
   science. CI contains no T3 framework job.

Validation stores use a temporary directory created for the job, the reserved
`validation` namespace, and records whose schema marks them
`SYNTHETIC_NONSCIENTIFIC`. Production registries reject that namespace. Test
names do not affect classification.

### 11.2 Frozen validation groups

| Group | Class | Exact permitted checks | Explicitly unreachable |
|---|---:|---|---|
| V0 canonical bytes | T0 | Verify both runtime Unicode assets' exact SHA-256 values; run the complete pinned Unicode 15.0 `NormalizationTest.txt`; check assigned-range expansion, assigned Unicode 15.0 boundaries, rejection of later-assigned U+2EBF0 even on a later host, rejection on missing/corrupt data, absence of host `unicodedata`/ICU/network reachability, code-point key order, escapes, integers, re-encoding, and duplicate/rejection vectors | Host Unicode normalization, object acceptance, policies, transitions |
| V1 hash and identity | T0/T1 | Every §5 domain/preimage/exclusion, metadata invariance, artifact frame, raw-source distinction, ID idempotency/collision in temp registry | Scientific registry/configuration |
| V2 core numbers/types | T0 | Strict §21.5 fixture schema/order/hash binding; exact 335-vector sequence; every integer/rational/decimal/binary-bit normal form and rejection; the exact 17-case `ErrorBound` basis; every exact operation cell and explicit conversion; policy shape/completeness and refusal without method call; explicit quantity/source/target/rule conversion context and opaque-renaming distinction, declared parent links, boundary treatment coverage, horizon due pairs, uncertainty contract roles, and every frozen I-2 compatibility/lifecycle/supersession predicate; 23 adjacent precedence pairs and nine named multiply-invalid cases | Domain precision/tolerance/rounding, policy callback, host-float arithmetic, unit lookup/inference, registry acceptance, membership/disjointness, global effect completeness, treatment adequacy, aggregation, scientific operation |
| V3 declarative records | T0 | During I-2 only: static construction/projection of `CommonObjectEnvelope` with exact stored `CanonicalBytes`, fresh decode and no decoded cache, `RecordMetadata`, `LifecycleTransition`, `SupersessionRelation`, and strengthened draft-only `RegistryRecord`; the exact four-case `FailureEventKey` lexical basis in specification §21.2.1; later stages add the remaining v0.1 records | Configuration, binding, state, action, policy memory, fault, result, authorization, artifact, scientific callbacks, lifecycle mutation |
| V4 synthetic authorization | T1 | RFC 8032 vectors; synthetic threshold, issuer scope, delegation attenuation/depth/cycle, fresh-time response parser, revocation rollback, exact targets, single-use SQLite conflict | Production keys, real stage authority, model entry |
| V5 capability leakage | T1 | Fabricated availability epochs, forbidden field traversal, read-set rejection, stateless/stateful applicability | Scientific policy code |
| V6 event/ownership | T0/T1 | Phase constants, `EventKey` total order, duplicate rejection, opaque synthetic ownership conflicts, phase-8/phase-9 duplicate identifiers | Transition proposal callback or state mutation |
| V7 inert durability | T1 | Dummy byte/record atomic outcomes, ambiguous commit classification, immutable prefix framing, no-durable-trace classification | FaultSchedule delivery, policy, state, runner |
| V8 Bridge exact fixtures | T2 | M1–M9 one-at-a-time grouping/status/arithmetic from Bridge v0.2, including undefined values and both M8 comparators | Trajectory, parameter search, causal inference, settlement choice |
| V9 dynamic exact fixtures | T2 | Six §9 static examples' unit/capacity/queue/delay arithmetic one at a time | `advance_epoch`, route science, schedule comparison |
| V10 artifact workflow | T1 | Dummy trace finalization, inert partial prefix, manifest completeness, byte-identical recovery, write-once refusal, separate publication record | Result generation, analysis, real publication |
| V11 reachability/audit | T0 | For I-2, source-text/AST-only proof of the exact 127-entry root export tuple, module subsets, 29-edge acyclic §21 DAG, exact `envelopes` canonical import subset, nine-path manifest, no decoded payload cache, no dynamic imports/local failure-code domains, and no scientific/runner/finalizer/result/Gate/package/network/subprocess/T1/T2/T3 reachability; later stages extend the audit prospectively | Production import during the AST audit, dynamic imports, execution, policy invocation, state mutation |

T2 groups V8 and V9 require separate static-fixture validation authority in
I-6/I-7 or I-9. Their presence in the plan does not authorize their execution.
No test advances `Z_k`, reuses a successor as a predecessor, calls a policy,
samples randomness, inspects candidate outcomes, invokes a runner/finalizer,
or opens a registered scientific configuration.

### 11.3 Acceptance evidence for every validation run

Every later validation report SHALL record repository/authority hashes,
changed source hashes, exact test file list, class of every called public
interface, fixture refs, command, exit status, completed check counts, and an
explicit statement of whether model state or scientific execution occurred.
A terminated, skipped, quarantined, or zero-check group is not a pass.

## 12. Implementation stages and dependency order

No stage below begins automatically. Each needs separate explicit authority,
a clean-tree/hash gate, and review of all predecessor evidence. The dependency
order is strict:

```text
I-0 plan
  -> I-1 canonicalization/identity/registry
  -> I-2 numbers/primitives/envelopes
  -> I-3 declarative records
  -> I-4 authorization/capabilities
  -> I-5 event/durability/trace kernel
  -> I-6 exact Bridge adapter
  -> I-7 dynamic mechanics
  -> I-8 provenance/recovery/publication
  -> I-9 implementation audit
```

### I-1 — Canonicalization, identity, hashing, and base registry

**Historical v0.2.1 status:** **BLOCKED** by the then-unresolved PEP
517/stdlib-only packaging contradiction recorded in §1.3.
**Current authority boundary:** the existing packaging amendment and matching
contract prospectively supersede that blocker within their narrow scope.
Revision v0.2.2 neither repeats that resolution nor determines current branch
implementation or integration status; those are established from Git and
retained stage evidence. It grants no authority to run this or a later stage.
**Historical planned inputs:** the accepted I-0 plan, the four authority
hashes then active, and the separately governed prospective packaging
authority without silently changing the closed manifest. Current accepted
I-1 evidence is recorded separately in §21.1.
**Work:** only I-1 files in §9; ECJ-1 and exact vendored Unicode 15.0.0 data,
all immediately constructible §5 hash projections, IDs, refs, semantic
versions, immutable registry base.
**Validation:** V0, V1, and import-safety portions of V11.
**Acceptance:** both Unicode runtime assets and the normalization fixture match
their §3.2/§9.5 raw SHA-256 values; the complete Unicode 15.0 normalization
corpus passes; U+2EBF0 is rejected independently of host Unicode support;
static reachability proves no host `unicodedata`, ICU, locale, or network
normalization path; exact bytes agree on every vector; all self-reference and
metadata-contamination cases fail; full-digest allocation is deterministic;
registry conflicts are atomic; source package imports no historical science.
**Fail closed:** missing/malformed/wrong-digest Unicode data, host-Unicode or
network fallback, canonical ambiguity, a Unicode-15.0-unassigned scalar, raw
float, unregistered namespace, digest/type mismatch, alias in accepted
content, or authority hash drift.
**Exclusions:** quantities, scientific records, authorization, event logic,
and every scientific function.

### I-2 — Numeric substrate, immutable envelope, and typed primitives

**Depends on:** accepted I-1.
**Current status:** accepted and implemented exactly at feature commit
`351417c39fa26b9045e7c162a9897a7c38e4e1d1`, then integrated without
amendment at merge commit `ede89d8af6b89da491e03c352efcf1868a913f6f`.
Revision v0.2.9 does not reopen I-2 or authorize any implementation change.
**Work:** exactly the nine-path §21.2 manifest: backward-compatible common
failure extension; exact core records/operations and non-executing policy
protocol; immutable envelopes; typed primitives and pure compatibility,
lifecycle, and supersession validation; draft registry type strengthening.
**Validation:** the strict ordered §21.5 fixture, V2, only the enumerated I-2
portion of V3, and the I-2 T0 AST/import/export audit. Existing
`tests/framework/safety.py` remains unchanged.
**Acceptance:** exact §21.3 post-I-2 root export tuple has 127 entries; all
normal forms and projections are unique; every operation-matrix cell and
multiply-invalid precedence vector agrees; policy-required operations refuse
without invoking a provider; quantity/source and rule/source conversion
failures are distinguished from explicit arguments under opaque-ref renaming;
incompatible aggregation and implicit absence fail; metadata cannot alter
scientific hashes; no I-1 observable failure semantics change.
**Fail closed:** authority/hash drift, any path beyond the nine-path manifest,
Python float at a canonical boundary, missing/incomplete policy field,
implicit conversion, untyped absence, incompatible coordinate, unexpected
import edge/export, registry acceptance mutation, or policy invocation.
**Exclusions:** no accepted policy, domain precision/tolerance/rounding,
distortion, action, state transition, acceptance/supersession mutation, T1,
T2, T3, scientific operation, or Gate operation.

### I-3 — Declarative scientific and operational records

**Depends on:** accepted I-2.
**Current status:** mechanically specification-ready under §22; unimplemented.
**Work:** only the exact 23-path manifest, 69 retained immutable types, 23
locally observable T0 validators, 35-code failure suffix, 92-name root suffix,
15-node/91-edge import graph, and 544-vector fully materialized prospective corpus in §22 and its
contracts.
**Validation:** type formation, exact projections/hashes, every validator
success and precedence pair, all-invalid cases, exports/imports, effective-
input collision freedom, and accepted I-1/I-2 byte preservation; no callback,
registry lookup, or referenced-content inspection.
**Acceptance:** all five I-3A–I-3E implementation substages complete under one
separate implementation authority; root exports total 219; every deferred
later-stage name remains unreachable; no accepted object or scientific use.
**Fail closed:** any authority/hash/path/name/field/projection/precedence/
fixture drift, untyped absence, hidden direct configuration field, physical/
memory/causal/settlement conflation, nonprovisional route claim, fault semantic
overclaim, or later-stage reachability.
**Exclusions:** no authorization or accepted-status transition, scientific
policy/distortion/measurement, state mutation, residual calculation, Bridge,
Dynamic behavior, trace/durability, finalization, publication, correction, or
acceptance of a real configuration/binding.

### I-4 — External authorization and information capabilities

**Depends on:** accepted I-3, prospective trust-bootstrap governance approval
for production activation, and audited exact crypto dependency under UQ-25.
**Work:** §6 trust/issuer/delegation/time/revocation/envelope/use mechanism,
real configuration/binding acceptance transitions,
stage guard, information capabilities, synthetic validation profile, and—only
after UQ-25 selects it—the exact Ed25519 provider metadata in `pyproject.toml`
and matching fully hashed finalization of `requirements-framework.lock` in
one reviewed change set. It also owns `accept_registry_object` and
`supersede_registry_object`; those mutations require the exact external
authorization validation and cannot be activated from I-2.
**Validation:** V4, V5, V11; synthetic keys/records only.
**Acceptance:** the provider/version/build and dependency closure selected by
UQ-25 agree exactly between `pyproject.toml`, the finalized lock, installed
distribution hashes, and provenance; every validation dimension is mandatory
and ordered; scope attenuates; current revocation and fresh time are required;
duplicate or ambiguous use cannot enter; future/forbidden field access fails
before a proposal; production rejects validation keys/namespaces.
**Fail closed:** absent UQ-25 provider decision, dependency metadata/lock/hash
drift, missing service, stale/gapped/equivocating evidence,
signature/key/profile mismatch, scope/time/target/predecessor mismatch,
unsupported filesystem, or use-store ambiguity.
**Exclusions:** no production credentials in fixtures; no scientific lease,
policy call, state advance, or distributed single use.

### I-5 — Deterministic event, ownership, durability, and trace kernel

**Depends on:** accepted I-4 and a prospective UQ-26 operational durability
contract before any real atomic backend is accepted.
**Work:** exact ten phase constants/order, event keys, proposals, epoch-wide
ownership, abstract atomic commits, policy decision/memory transaction,
canonical rows/prefixes, T3 lease/entry guard, base fault hooks that cannot
deliver a kind.
**Validation:** V6, V7, V11 only; opaque coordinates and dummy bytes.
**Acceptance:** order and ownership conflicts are deterministic; phase 9
cannot duplicate phase 8; informational memory ownership stays outside
physical ownership; known prefixes are immutable/literal; T3 entry cannot be
constructed by validation; non-`NOT_APPLICABLE` faults are rejected pending
UQ-38.
**Fail closed:** equal event key, predecessor mismatch, ownership conflict,
ambiguous durability, missing trace evidence, invalid lease, or any fault
delivery attempt.
**Exclusions:** no scientific transformation, policy, state, world, schedule,
fault directive, runner, or accepted atomic backend absent UQ-26.

### I-6 — Exact Sequential–Parallel Bridge v0.2 adapter

**Depends on:** accepted I-5.
**Work:** imported grouping graph/transitive closure, comparator records,
quantity-fixed/rule-replayed distinction, group measurement, `N_G`, named
interaction, undefined/nonserializable states, causal-status separation, and
settlement closure validation.
**Validation:** V8 only after separate T2 authority; static conformance review.
**Acceptance:** no local definition differs from Bridge v0.2; M1–M9 exact
values/statuses pass; M9 invents no comparator/causal value; no allocation is
called measurement.
**Fail closed:** incompatible boundary, unresolved coupling, missing
comparator kind, invalid same-baseline endpoint, or undefined value coerced to
zero.
**Exclusions:** no deterministic parallel-testing preregistration, trajectory,
parameter search, causal model, O3 settlement choice, or Gate 1D-C action.

### I-7 — Dynamic Coordination records and deterministic mechanics

**Depends on:** accepted I-6.
**Work:** exact `Z_k` component ownership; topology/capacity/admission/queue,
reservation/shortfall, congestion, delay/transit/effects, reroute suffix,
natural-drive proposal interfaces, policy-memory pairing, provisional Part
VII guards.
**Validation:** V9 and route guards after separate T2 authority; isolated
static arithmetic only.
**Acceptance:** imported ten-phase responsibilities and no-double-application
rules map exactly; physical state retains `x,g,q,c,ell`; queues partition
correctly; pending is nonzero/nonabsence; route-dependent claims fail
unresolved.
**Fail closed:** missing typed balance term, capacity excess, rejected-demand
queue mutation, completed-route rewrite, overlapping delay double count,
natural drive outside phase 10, or unaccepted domain numerical policy.
**Exclusions:** no Part VII law, domain natural-drive model, controller,
trajectory, schedule comparison, stochastic engine, or hypothesis test.

### I-8 — Provenance, artifacts, recovery, and publication

**Depends on:** accepted I-7, a UQ-27 publication protocol before a real store,
and UQ-26 for recovery against a real execution store.
**Work:** UQ-36 enforcement, immutable trace/run envelope/result/manifest,
same-bytes recovery, dummy content-addressed publication, separate
publication/correction records.
**Validation:** V10 and V11 on dummy bytes only.
**Acceptance:** full/prefix/run projections remain distinct; a partial
manifest cannot be complete; recovery never calls execution; different bytes
cannot overwrite; publication facts never mutate the manifest.
**Fail closed:** missing artifact, hash mismatch, ambiguous prefix, different
destination bytes, publication authorization mismatch, or source/runtime
property outside §7.
**Exclusions:** no real result, analysis, figure, publication destination,
correction decision, or scientific rerun.

### I-9 — Separately authorized implementation audit

**Depends on:** accepted I-8 and explicit validation authority naming the
exact T0/T1/T2 groups.
**Work:** complete diff/import/API/hash/authority/threat/invariant audit; add
only the CI changes in §9.2; produce a separate validation report if later
authorized.
**Validation:** V0–V11 as individually authorized; no T3.
**Acceptance:** every changed path is in §9 and each change was made only by a
listed owning stage; public exports equal §10 exactly; the `pyproject.toml`
crypto requirement and finalized lock are identical to the UQ-25 decision;
the Unicode assets and normalization fixture have the exact frozen hashes and
no host-Unicode fallback is reachable; every invariant/threat maps to code
and completed evidence or a named blocker; tests report nonzero completed
checks; authority/source hashes match; no registered world, policy, runner,
finalizer, model step, trajectory, Gate 1D-C path, or result path was
reachable.
**Fail closed:** skipped/terminated/zero-check group, unexplained path/import,
dependency/hash drift, T3 reachability, unresolved scientific conflict, or
evidence gap.
**Exclusions:** no preregistration, pre-execution binding for a study,
scientific execution, interpretation, publication, commit, or push unless
each is separately authorized outside this plan.

## 13. Cross-stage fail-closed rules

These rules apply even if a stage-specific acceptance criterion appears to
permit progress:

1. A mismatch among the specification, this plan, or any of the three
   authorities stops work. Implementation may not choose one selectively.
2. A dirty tree, wrong branch, local/remote SHA mismatch, unregistered path,
   unexpected artifact, or unexplained dependency change stops the stage.
3. A hash/preimage, ECJ-1, ID, schema, reference, lifecycle, or authority
   mismatch fails before the referenced object is used.
4. Unknown enums, runtime-property classes, operation scopes, numerical
   policies, fault extensions, route semantics, modes, or completeness states
   fail unsupported. They never select a default.
5. `PENDING`, `FAILED`, `PARTIAL`, `UNRESOLVED`, `OUT_OF_BOUNDARY`, and
   `NOT_APPLICABLE` remain typed and cannot become zero, empty, `null`, or
   omission.
6. Physical measurement, causal inference, policy choice, and institutional
   settlement cannot share a result field or overwrite one another.
7. Policy memory cannot enter physical `Z_k`, and physical ownership cannot
   own a memory transition.
8. A proposal failure advances nothing. A commit ambiguity preserves prior
   durable evidence and becomes partial/unresolved; it is never retried as a
   fresh uncounted invocation.
9. A validation capability token cannot be upgraded or confer T3 authority.
   Contextual classification may escalate a T0/T1 helper invocation inside
   already authorized T2/T3 work, but it creates no higher capability. T3
   still requires new external authority and a one-use execution entry.
10. Any result-sensitive selection of a parameter, precision, tolerance,
    comparator, world, schedule, fault, objective, or classification is
    forbidden unless a separate prospective scientific authority explicitly
    permits it.
11. No recovery, finalization, correction, publication, or test interface may
    import or call the runner.
12. Unsupported or absent durability guarantees stop acceptance; an
    in-memory success is not evidence of durable atomicity.

## 14. Explicit exclusions for the whole plan

This plan does not select or authorize:

- any domain state, distortion, action transformation, natural drive,
  controller, objective, uncertainty set, precision, rounding, tolerance,
  approximation, or cross-platform numerical guarantee;
- a Part VII route, distance, loss, propagation, actor, or closure law;
- a stochastic generator, seed derivation, stream ownership, or draw rule;
- a multi-controller memory composition;
- a fault kind, effect, delivery acknowledgement, continuation, recovery, or
  terminal rule;
- a causal-identification model or institutional settlement/allocation rule;
- a durable physical execution store, distributed authorization-use store, or
  real publication store beyond the stated interfaces;
- a real trust root, issuer, key, credential, time/revocation endpoint, or
  governance role assignment;
- a scientific configuration, preregistration, execution binding, run,
  interpretation, result, figure, publication, or correction;
- the deterministic parallel-testing programme;
- any Gate 1D-C investigation, remedy, retry, finalization, or invocation;
- alteration of a frozen source, protocol, plan, result, manifest, or incident
  record; or
- a commit, push, pull request, branch change, tag, release, package
  publication, or history rewrite.

## 15. Decision register

All `ACCEPTED_I0` decisions are implementation-plan decisions only. They do
not establish scientific facts or authorize their implementation.

| ID | Status | Decision | Consequence |
|---|---|---|---|
| I0-DR-001 | `ACCEPTED_I0` | Use new `src/ebu_framework` package boundaries and never retrofit historical experiment files | Preserves earlier evidence and blocks accidental Gate/runner coupling |
| I0-DR-002 | `ACCEPTED_I0` | `CoreNumberV1` is integer, reduced rational, normalized finite decimal, or finite binary64 bits | Lossless interchange is exact while arithmetic meaning remains domain-owned |
| I0-DR-003 | `ACCEPTED_I0` | Every non-lossless operation requires an accepted `NumericalPolicyV1` with no default implementation | UQ-02 is resolved only at the core/interface boundary |
| I0-DR-004 | `ACCEPTED_I0` | Adopt ECJ-1 rather than RFC 8785 and pin its assignment/NFC behavior to vendored Unicode 15.0.0 data | Satisfies UTF-8/NFC and Unicode-scalar key ordering without a hidden UTF-16 or host-Unicode-version conflict |
| I0-DR-005 | `ACCEPTED_I0` | Forbid raw JSON fraction/exponent tokens and all Python floats in canonical scientific preimages | Eliminates cross-runtime numeric spelling ambiguity |
| I0-DR-006 | `ACCEPTED_I0` | Allocate IDs from full SHA-256 of a namespace-owned, content-neutral stable allocation claim | Deterministic under concurrency, stable across versions, non-recursive, not outcome-derived |
| I0-DR-007 | `ACCEPTED_I0` | Use all named §5 SHA-256 projections and distinct digest types | Prevents cross-domain substitution and metadata/self-reference contamination |
| I0-DR-008 | `ACCEPTED_I0` | Canonical trace rows form a predecessor-hash chain and length-framed row stream | Makes the known durable row stream a literal prefix while retaining a distinct complete payload |
| I0-DR-009 | `ACCEPTED_I0` | Use out-of-band pinned 2-of-3 Ed25519 issuer roots, 2-of-3 revocation roots, and online pinned time attestation | Gives UQ-35 a non-recursive trust root and explicit freshness |
| I0-DR-010 | `ACCEPTED_I0` | Delegation is single-parent, attenuation-only, acyclic, and at most four credentials | Prevents scope union, escalation, and unbounded validation |
| I0-DR-011 | `ACCEPTED_I0` | Every authorization grants one operation and one invocation; execution consumes once at run entry and uses a nontransferable live lease internally | Prevents authorization replay without counting each epoch as a new invocation |
| I0-DR-012 | `ACCEPTED_I0` | Enforce local single use with exact SQLite compare-and-consume; distributed use unsupported | Concrete v0.1 enforcement without pretending UQ-26 is resolved |
| I0-DR-013 | `ACCEPTED_I0` | Use the closed-world UQ-36 classification and reject undeclared runtime reads | Replay semantics cannot be chosen retrospectively from observed agreement |
| I0-DR-014 | `ACCEPTED_I0` | Freeze only the base `FaultSchedule` type and make every nonempty schedule unavailable until UQ-38 | Avoids inventing study faults or terminal science in framework code |
| I0-DR-015 | `ACCEPTED_I0` | Public APIs are exhaustive and classified by reachable behavior: pure structural handling of supplied immutable science may be T0, while enclosing T2/T3 context escalates each invocation and no wrapper can lower it | Removes input-type overclassification without permitting helper/test naming to bypass stage controls |
| I0-DR-016 | `ACCEPTED_I0` | Validation is split into V0–V11 with structural T3 non-reachability | Static/synthetic checks cannot become a one-tick experiment |
| I0-DR-017 | `ACCEPTED_I0` | M1–M9 and the six dynamic hand examples are the only first T2 fixtures | Resolves UQ-31 narrowly without beginning a study or trajectory |
| I0-DR-018 | `ACCEPTED_I0` | The §9 file list is closed and each permitted initial or later modification has an explicit stage owner, including I-4 ownership of `pyproject.toml` crypto metadata | Implementation scope and cross-stage dependency changes are inspectable before code exists |
| I0-DR-019 | `ACCEPTED_I0` | Production authorization activation waits for an explicit trust-bootstrap governance record | Actual institutional authority is not invented in this technical plan |
| I0-DR-020 | `ACCEPTED_I0` | Preserve Gate 1D-C exactly and blacklist every related path from framework validation | I-0 cannot alter or consume that study's state |
| I0-DR-021 | `ACCEPTED_I0` | Vendor and raw-hash-check Unicode 15.0.0 `UnicodeData.txt` and `DerivedNormalizationProps.txt`, and test against the pinned complete normalization corpus | Later Python Unicode databases cannot silently change ECJ-1 assignment or NFC bytes |
| I0-DR-022 | `ACCEPTED_I0` | Freeze four separately named release milestones and disjoint tag namespaces in §18 | Documentation, alpha software, scientific v3.0, and complete books cannot be conflated |
| I0-DR-023 | `ACCEPTED_I0` | Implement every I-2 T0 predicate from exact declared argument values only; refs prove identity and trigger no lookup | Makes predicate outcomes reproducible and defers lifecycle/role/content/completeness/disjointness/adequacy/indirect-cycle claims to their owning later authority |
| I0-DR-024 | `ACCEPTED_I0` | Give `convert_quantity_exact` explicit quantity, source-unit, target-unit, and rule arguments without adding a callable | Separates quantity/source from rule/source authority and preserves exact local observability under opaque-ref renaming |

## 16. Threat register

This register supplements, and does not replace, the specification's TM-001
through TM-044.

| ID | Threat | Control frozen here | Residual or blocker |
|---|---|---|---|
| I0-TM-001 | Canonical bytes differ across languages for non-BMP keys | ECJ-1 Unicode-scalar sorting, raw-hash-pinned Unicode 15.0 assignment/NFC tables, complete normalization corpus, exact vectors | Other implementations require independent conformance evidence |
| I0-TM-002 | Unicode normalization merges two keys | Normalize then reject duplicate names | Human-confusable but unequal names remain a review concern |
| I0-TM-003 | JSON parser rounds large numbers or accepts NaN | Arbitrary-precision integer-only raw tokens; strict parser; tagged other numbers | Third-party ingestion adapters remain separately reviewable |
| I0-TM-004 | Core arithmetic silently becomes domain policy | Only provably lossless operations; mandatory accepted policy otherwise | Domain policy quality remains future science |
| I0-TM-005 | Content-derived ID changes across versions or becomes recursive | Content-neutral stable allocation claim excluding content/version/hash | Namespace owner may choose a poor stable key; registry review remains needed |
| I0-TM-006 | Digest from one domain is accepted in another | Distinct types, mandatory domain, no generic public hash API | Type erasure in external systems must fail at ingestion |
| I0-TM-007 | Trace prefix cannot extend byte-identically | Length-framed canonical row stream and row predecessor hashes | Atomic storage of rows/state/memory remains UQ-26 |
| I0-TM-008 | Authorization authenticates itself recursively | Out-of-band pin; signature over exact authorization ref; separate envelope hashed afterward | Bootstrap distribution and custody require governance control |
| I0-TM-009 | One compromised issuer grants broader authority | Root-signed issuer ceiling, attenuation-only delegation, exact authorization targets | Compromise within valid ceiling remains possible until revocation |
| I0-TM-010 | Stale revocation evidence is replayed | Online fresh time and current short-lived threshold-signed snapshot; rollback/equivocation ledger | Service outage stops protected work; availability is intentionally sacrificed |
| I0-TM-011 | One authorization is reused after crash or concurrency race | Durable unique use key consumed before entry; ambiguity burns permission | SQLite relies on approved local filesystem and hardware; distributed case unsupported |
| I0-TM-012 | Actual runtime influence is mislabeled metadata | Closed allowlist/environment; reachable dependency closure; undeclared-read failure | Proving absence of covert native/hardware influence remains implementation audit work |
| I0-TM-013 | Including every host fact makes replay identity meaningless | §7.3 excludes instance/time/storage facts and instead includes normalization rules | Conservative included OS/backend constraints may narrow equivalence intentionally |
| I0-TM-014 | Framework invents a generic fault that changes study meaning | No built-in fault kinds/effects/terminal rules; nonempty schedule rejected | UQ-38 amendment is mandatory before any delivery test |
| I0-TM-015 | T1 storage failure is disguised scientific fault injection | T1 uses dummy bytes/stores and never a `FaultSchedule` or scientific state | Review must distinguish inert failure doubles from accepted durability backend |
| I0-TM-016 | T2 fixture becomes a trajectory | One-call capability; no `SystemState` return accepted for another call; exact allowlist | Python cannot prevent malicious source edits; closed diff and audit are required |
| I0-TM-017 | A pure helper is overclassified from its input type, or a wrapper underclassifies reachable scientific behavior | Behavior-based intrinsic classification, contextual maximum/escalation, closed export catalogue, T3 lease parameter, AST reachability scan | Dynamic language reflection remains in reviewed threat model and is forbidden by policy |
| I0-TM-018 | Validation imports legacy experiment code indirectly | Explicit import/path blacklist and dependency DAG scan | Existing legacy tests remain outside this framework validation claim |
| I0-TM-019 | A file is added to hide behavior | Closed file manifest and staged filename audit | Legitimate split requires prospective plan revision |
| I0-TM-020 | Crypto library/version weakens selected profile or differs between package metadata and lock | I-4 owns one reviewed `pyproject.toml`/lock update after exact UQ-25 selection, plus installed-distribution hash audit | Provider vulnerabilities may require prospective security migration |
| I0-TM-021 | Publication or recovery silently invokes execution | Import-direction rule and T1 interface classification | External scripts outside the framework remain governance risk |
| I0-TM-022 | Gate 1D-C incident is accidentally consumed as framework fixture | All Gate paths blacklisted; only incident text is preserved in this plan | Manual commands outside authorized scope remain prohibited by repository guidance |
| I0-TM-023 | A later host runtime recognizes a code point absent from Unicode 15.0 and changes canonical bytes | Pinned runtime tables, mandatory U+2EBF0 rejection, host-library import ban, missing/corrupt-asset failure | A defect in the independent table parser remains possible until I-1 conformance review |
| I0-TM-024 | A foundation or alpha milestone is presented as scientific or complete-books release evidence | Disjoint prerequisites, acceptance evidence, tag namespaces, branch lanes, and nonclaim rules in §18 | External mirrors or prose can mislabel an artifact and require correction |
| I0-TM-025 | A T0 validator resolves an opaque ref or relies on fixture/patch/hidden state to make a semantic claim | Exact argument-only implementation rule, AST lookup/import exclusions, explicit pair/role fields, and corrected static vectors | I-4 and domain authorities must later validate the stronger referenced semantics |
| I0-TM-026 | Exact conversion assigns codes from fixture or patch provenance because no source unit is authoritative | Four explicit conversion arguments, exact role-position comparisons, unchanged rule predicates, and a bijective opaque-ref-renaming assertion | Ref contents and scientific adequacy remain deferred under unchanged UQ-40 authority |

## 17. Questions intentionally deferred beyond I-0

### 17.1 Specification questions not resolved here

| IDs | Deferred subject | Required future authority or amendment |
|---|---|---|
| UQ-01 | Minimal sufficient domain physical/closed-loop state | Part-specific analytical design |
| UQ-05 | Meaning-preserving schema migration proof | Separate migration protocol before first migration |
| UQ-06–UQ-07 | Continuous/hybrid time and physically unresolved simultaneity | New analytical foundation or Dynamic Coordination revision |
| UQ-08–UQ-11 | Uncertain coupling, separability evidence, comparator existence/coverage | Bridge revision and Part VI preregistration |
| UQ-12–UQ-13 | Causal identification and acceptable unidentified-contribution settlement | Causal protocol and Part IX institutional design |
| UQ-14–UQ-22 | Part VII routes; multi-resource conversion; queues; distributed reservations; horizons; delayed causality; natural drive; objectives; institutional values | Named Part/domain foundations and study designs |
| UQ-23–UQ-24 | PRNG/streams and shared exogenous histories | Stochastic specification and study preregistration |
| UQ-25 | Exact third-party implementations/dependency versions | Implementation dependency/security audit before each dependency is admitted |
| UQ-26 | Durable atomic physical phase, policy-memory/decision/trace, and recovery store | Prospective operational durability contract before I-5 backend acceptance |
| UQ-27–UQ-30 | Real publication store, correction authority, minimum trace/privacy, restricted provenance | Publication, governance, security, and study-specific protocols |
| UQ-32–UQ-34 | Machine proof tooling, plugin certification, major-version boundary | Separate formal verification/conformance/specification work |
| UQ-37 | Multi-controller canonical memory and ordering | Part-specific foundation/framework extension |
| UQ-38 | Fault kinds, targets, acknowledgements, continuation/terminal rules | Separate fault-injection specification and applicable preregistration |
| UQ-39 | Sensitive policy-memory encryption/access/retention/disclosure | Security/privacy/study-governance protocol |
| UQ-40 | Registry/domain proof of policy/contract roles and contents, region disjointness, global pending/effect completeness, treatment adequacy, true violation, and indirect alias/object-graph cycle freedom | I-4 registry design plus applicable domain analytical/governance authority |

UQ-02, UQ-03, UQ-04, UQ-31, UQ-35, and UQ-36 have the limited I-0
resolutions recorded in this plan. Their scientific application is not
thereby accepted.

Revision v0.2.9 does not resolve, narrow, or expand UQ-40. Comparing the
quantity's declared unit ref with an explicitly supplied source-unit ref is a
local I-2 identity predicate only; it establishes no referenced unit or rule
content, lifecycle, role, or scientific adequacy.

### 17.2 Mandatory amendments or decisions before affected implementation

The following are concrete blockers or retained prerequisite records, not
optional refinements:

1. **Historical v0.2.1 prerequisite before I-1:** revision v0.2.1 required a
   separately authorized prospective packaging amendment to resolve the
   explicit-backend/stdlib-only contradiction. The existing packaging
   amendment and matching contract prospectively supplied that narrow
   resolution. Revision v0.2.2 does not edit, repeat, or redefine it and does
   not itself authorize implementation or integration.
2. **Before I-4 production activation or registry acceptance/supersession:**
   a governance bootstrap must register real trust-profile key material, key
   custody/rotation, issuer roles and ceilings, time/revocation services,
   endpoints, and operator pin procedure. I-2 supplies validation only and
   cannot create an accepted object or numerical policy.
3. **Before the I-4 cryptographic provider is accepted:** UQ-25 review must
   select exact provider versions/builds/hashes, verify RFC 8032 behavior, and
   freeze identical direct-dependency metadata in `pyproject.toml` and the
   complete hashed closure in `requirements-framework.lock` during I-4.
4. **Before I-5 accepts a real durability backend:** a UQ-26 operational
   contract must select and prove the atomic physical phase and
   policy-decision/memory/trace mechanisms. The abstract interface may be
   implemented earlier; a real runner may not.
5. **Before any nonempty fault schedule, delivery implementation, or delivery
   test:** UQ-38 must be resolved prospectively. Base records and rejection
   hooks alone may proceed.
6. **Before any domain distortion/action/controller/natural-drive function:**
   that domain must accept its `NumericalPolicyV1`, state, boundary, and
   scientific contracts. The core supplies none.
7. **Before route-derived physical claims:** a Part VII foundation must replace
   the provisional route boundary.
8. **Before stochastic code:** UQ-23 and applicable UQ-24 must be resolved.
9. **Before a real publication backend or correction workflow:** UQ-27 and
   UQ-28 must be resolved.
10. **Before any claim stronger than I-2 declared identity/shape:** UQ-40 must
    be resolved by I-4 registry design and the applicable domain authority;
    no I-2 implementation may fill the gap through lookup or inference.

## 18. Release roadmap — planning only

This roadmap distinguishes four release milestones. It creates no branch,
tag, release, package, manuscript, manifest, or publication artifact. Each
milestone requires a new explicit authorization and a prospective release
checklist naming the exact commit, evidence paths, hashes, signer, tag command,
and destination before any release action. Reaching one milestone neither
authorizes the next nor cures a missing scientific stage.

All future tags named here are immutable annotated and cryptographically
signed Git tags. A tag is created only after its evidence is accepted at the
exact commit it names; it is never moved, deleted for reuse, or made to point
at a dirty/unreviewed tree. Historical `v2.x.y` tags are untouched. A rejected
candidate receives no tag. Milestone-specific tag namespaces below prevent a
documentation or software status from being presented as scientific evidence.

### 18.1 Documentation/foundation milestone

**Meaning:** the architecture and I-0 implementation contract are reviewable
foundations. This is documentation, not an implemented framework, validated
scientific result, complete book, or permission to execute.

**Prerequisites:**

1. the framework specification, its three authoritative sources, and the I-0
   plan are accepted with exact hashes and no unresolved integrity conflict;
2. the I-0 diff is documentation-only and its decision, threat, file,
   interface, validation, dependency, exclusion, and deferral registers are
   internally consistent;
3. every scientific unknown remains open or points to a prospective owner;
4. repository guidance, branch/HEAD provenance, and the exact Gate 1D-C
   incident statement remain preserved; and
5. no implementation, scientific execution, interpretation, or publication
   is claimed by the milestone.

**Acceptance evidence:** a reviewed authority-hash table; complete changed-file
and diff audit; static Markdown/reference/identifier checks with nonzero
counts; explicit no-execution/no-model-state declaration; repository and
remote-tip state; reviewer disposition; and a release checklist binding all
of those records to one commit. The plan alone is not that disposition.

**Version/tag policy:** the documentation milestone series is
`foundation-v0.1.0`; documentation-only corrections increment the patch
component (`foundation-v0.1.1`, and so on). A scientific, interface, or
architecture-breaking change requires a new prospective minor/major
foundation version. No foundation commit receives `v3.0.0`, `framework-*`, or
`books-*` merely because its documents are complete.

**Branch strategy:** the present foundation work remains on
`v3.0-local-ebu-foundation`. After a foundation milestone is accepted, later
corrections use separately authorized short-lived branches named
`docs/foundation-<issue>` from the exact tagged commit and return through
reviewed non-history-rewriting merges. The milestone tag points to the exact
accepted foundation commit on that lineage. Nothing here creates a branch or
merges it into `main` or `v3.0-ecological-accounting`.

### 18.2 Framework v0.1 alpha

**Meaning:** a pre-stable implementation of the unified framework suitable
for conformance evaluation. Alpha status explicitly does not assert
production authorization, a scientific finding, API stability, or book
completion.

**Prerequisites:**

1. accepted `foundation-v0.1.x` evidence and separately authorized completion
   and acceptance of I-1 through I-9 in dependency order;
2. exact UQ-25 Ed25519 provider selection, matching `pyproject.toml` and
   hashed lock metadata, pinned Unicode assets, complete public-interface and
   file inventories, and a clean dependency/security audit;
3. completed nonzero T0/T1 checks and only the separately authorized frozen T2
   groups, with structural proof that T3 and historical runners were
   unreachable;
4. an accepted implementation-validation report mapping every invariant and
   threat to evidence or an explicit non-release blocker; and
5. production trust activation, real execution backends, real worlds,
   scientific credentials, and results remain absent unless separately
   specified—and none is needed merely to label an alpha.

**Acceptance evidence:** exact source, Unicode-data, dependency, distribution,
and authority hashes; the I-9 report and completed-check counts; API/export and
file-manifest comparisons; an install/import conformance record for declared
platforms; software bill of materials and license/security review; and an
explicit statement that no T3 scientific execution occurred.

**Version/tag policy:** Python package version `0.1.0a1` corresponds exactly to
Git tag `framework-v0.1.0-alpha.1`. Later alpha candidates increment only the
final positive integer and package suffix (`a2` /
`framework-v0.1.0-alpha.2`). A stable `framework-v0.1.0` tag is outside this
roadmap and requires a prospective stability decision; it cannot be inferred
from an alpha passing its checks.

**Branch strategy:** after separate authorization, a future
`framework-v0.1` integration branch is forked from the exact accepted
foundation tag. Each I-1–I-9 stage uses a short-lived
`framework/i-<stage>-<issue>` branch from its accepted predecessor and returns
only through reviewed, non-history-rewriting merge commits. The alpha tag is
placed on the accepted I-9 integration commit. Framework commits are imported
into science only by exact reviewed commit/tag reference; no alpha merge
automatically enters a scientific branch.

### 18.3 Scientific v3.0 release

**Meaning:** the repository's v3.0 scientific claims and artifacts have passed
their separately authorized scientific lifecycle. Neither accepted foundation
documents nor a framework alpha is evidence that this milestone is complete.

**Prerequisites:**

1. every v3.0 hypothesis, world, arm, comparator, parameter, numerical policy,
   tolerance, metric, falsifier, interpretation rule, and nonclaim is frozen
   prospectively in its applicable accepted protocol;
2. every required analytical, implementation, validation, pre-execution,
   execution, finalization, interpretation, and release-audit stage is
   separately authorized and accepted in order;
3. every framework-backed study pins one accepted framework alpha or later
   framework version and its complete execution-semantics/dependency closure;
4. canonical traces or qualified durable prefixes, run envelopes, immutable
   results, manifests, provenance, and correction/publication state are
   complete for the release scope, with no missing required gate;
5. all released legacy and v3.0 regression/conformance evidence is accepted;
   and
6. the Gate 1D-C incident has a later authoritative disposition sufficient for
   the release scope. Its present `UNSTARTED` state cannot be treated as a pass,
   failure, result, or satisfied prerequisite.

**Acceptance evidence:** frozen protocol/configuration/binding hashes;
authorization and stage-ledger evidence; completed scientific trace/result
manifests and provenance; accepted interpretation and claim-status ledger;
reproduction and regression audit; complete changed-file and source/dependency
hash inventory; release notes; and independent release disposition. An alpha
validation report cannot substitute for any scientific item.

**Version/tag policy:** the scientific release version and immutable tag are
exactly `v3.0.0`, continuing the repository's `v<major>.<minor>.<patch>`
scientific namespace. Post-release corrections preserve the original tag and
evidence; an authorized scientific correction release increments the patch
(`v3.0.1`). Foundation, framework, or books tags never satisfy a `v3.0.0`
reference.

**Branch strategy:** scientific integration occurs on the existing
`v3.0-ecological-accounting` branch only after separate authorization. Each
gate or study uses its own prospectively named branch from the exact accepted
predecessor, with immutable evidence merged through review. Accepted
foundation/framework commits enter only by exact reviewed merge or pin. The
release is proposed by a reviewed integration-to-`main` merge, and `v3.0.0`
would tag that accepted merge commit. The present branches are not changed by
this plan, and no Gate 1D-C branch, command, or evidence is touched.

### 18.4 Complete-books release

**Meaning:** the complete Parts IV–IX book programme is rendered and released
with every claim bounded by accepted evidence. It is a publication milestone,
not a new scientific result and not synonymous with v3.0 alone.

**Prerequisites:**

1. the `v3.0.0` scientific release and every later scientific foundation,
   proof, study, protocol, result, interpretation, and correction required by
   Parts IV–IX are accepted and immutable;
2. all chapters, dependency maps, notation/definition registries, evidence and
   claim-status ledgers, figures, citations, limitations, nonclaims, and open
   questions required by `EBU_FUTURE_BOOKS_STRUCTURE.md` are complete;
3. cross-part dependencies and duplicated definitions are reconciled without
   changing scientific evidence in editorial review;
4. every generated figure/table binds to accepted source data and exact
   generation provenance, and rendering, accessibility, citation, rights,
   and archival checks pass; and
5. no unresolved scientific question is silently converted into exposition or
   a release claim.

**Acceptance evidence:** complete source and rendered-artifact hash inventory;
chapter-to-authority and claim-to-evidence matrices; figure/table provenance;
cross-reference, citation, link, accessibility, and visual-render reports;
open-question/nonclaim ledger; independent editorial/scientific review; and a
write-once publication/release manifest authorized in its own future stage.

**Version/tag policy:** the first complete-books edition uses edition version
`1.0.0` and immutable Git tag `books-v1.0.0`. Editorial corrections that do
not change scientific meaning increment the books patch component. A change to
a scientific claim first requires its own authorized scientific amendment or
release and then a new books minor/major version; a books tag never moves or
rewrites the scientific `v3.0.0` tag.

**Branch strategy:** only after separate authorization, a future
`books-complete` integration branch is created from a released `main` commit
that contains `v3.0.0` and every later accepted scientific dependency needed
by the books. Part-specific work uses reviewed `books/part-iv` through
`books/part-ix` branches from the recorded integration base. The complete
edition returns through a reviewed release merge to `main`, and the books tag
would name that accepted merge commit. Scientific source/result artifacts are
referenced, never edited on a books branch.

### 18.5 Ordering and present status

The release dependency order is foundation evidence → framework alpha →
scientific v3.0 → complete books, but documentation may be drafted ahead when
clearly marked provisional and no milestone may borrow acceptance from a later
one. Framework alpha is a required implementation baseline only for studies
that use it; all scientific prerequisites remain independently mandatory.

Historical original I-0 status: at that correction, none of the four
milestones was declared achieved. No branch, tag, package, release,
manuscript, manifest, or publication artifact had been created, and no
release authorization had been consumed.

Historical v0.2.1 status: the signed documentation tags
`foundation-v0.1.0` and `foundation-v0.1.1` are immutable evidence at the
objects and commits recorded in §1.3.

Historical v0.2.2 authority boundary: that reconciliation created no milestone,
branch, tag, package, release, manuscript, manifest, or publication artifact.
It did not grant framework integration, I-2, framework-alpha, scientific-
execution, Gate, publication, or release authority. Milestone and branch
status must be established independently from Git and their retained
acceptance evidence rather than inferred from this plan.

Historical v0.2.7 authority boundary: that correction created no milestone,
branch, tag, package, release, manuscript, manifest, or publication artifact.
It froze the prospective I-2 source-unit authority that was later implemented
and accepted without reinterpretation.

Current v0.2.9 authority boundary: this amendment creates no milestone,
branch, tag, package, release, manuscript, implementation manifest, validation
fixture, or publication artifact. It preserves accepted I-2 and closes only
prospective I-3 mechanical authority. It does not begin I-3A implementation or
authorize I-4 through I-8 behavior, framework-alpha, scientific execution, a
Gate operation, publication, or release.

## 19. Current prospective document acceptance checklist

Revision v0.2.9 is complete only if review confirms all of the following:

- the active authority locks are exactly those in §1.3, while the
  original I-0 verification and starting SHA in §§1.1–1.2 remain explicitly
  historical;
- exactly the specification, this plan, the I-3 authority amendment, and the
  two strict JSON I-3 contracts changed for this prospective authority closure;
- the only active books-structure and conservation-foundation hashes are the
  exact values in §1.3, while superseded values occur only in explicitly
  historical records or the frozen accepted-I-2 input record;
- the three account levels are reduced represented-stock, open control-volume,
  and isolated boundary-complete, with reduced/open models retained as first-
  class supported cases;
- existing D0, P1C, service, Gate 1D-C, and historical models remain unchanged
  reduced or open models, with no retroactive isolation claim;
- I-2 remains exactly the accepted nine-path implementation and retains all
  inventories, failure codes, precedence, fixtures, imports, exports, API
  counts, bytes, and hashes;
- optional declarative boundary/conservation profiles are frozen as I-3A
  authority, while residual calculation and comparison remain I-5 behavior;
- no universal zero-residual requirement, hidden global tolerance, dependency,
  implemented fixture, schema, workflow, or executable permission is
  introduced;
- physical conservation, represented-stock closure, EBU accounting, causal
  inference, policy, and institutional settlement remain distinct;
- the exact 69 I-3 types, 23 validators, 35 appended failures, 92-entry root
  suffix, 15-module/91-edge direct import graph, 23-path future manifest, and
  544-vector future fixture are frozen by §22 and its contracts, but remain
  unimplemented and require separate I-3A through I-3E implementation
  authorization;
- Bridge and Dynamic Coordination amendments remain separately authorized and
  unstarted, and no scientific or experimental claim is made;
- specification §21 and plan §21 agree on the complete common failure,
  numeric, numerical-policy, primitive, envelope, registry, API, fixture,
  dependency, capability, and exclusion contracts;
- every I-2 T0 predicate is computable from exact declared argument values;
  refs prove identity only, with no registry/envelope/alias lookup, hidden
  state, fixture knowledge, or patch/construction-history dependency;
- numerical-policy validation makes no lifecycle/placeholder claim, requires
  distinct declared policy/owner identities, and requires an exact tolerance
  ref whenever `COMPARE` is supported;
- standalone rule validation receives the rule and both units; exact quantity
  conversion receives quantity, explicit source unit, explicit target unit,
  and rule, checks intrinsic quantity state, quantity/source identity,
  quantity/source/target dimensions, and the unchanged ordered rule
  predicates without lookup or inferred reference contents;
- region parent validation checks only declared parent links, clocks,
  intervals, distinct IDs, and aggregation-ref presence; it makes no
  membership/disjointness claim;
- `AccountingBoundary` includes exact ordered unique effect/treatment pairs
  and child treatment keys exactly cover the union of the two declared
  cross-effect sets without claiming real-world completeness or adequacy;
- horizon validation consumes exact ordered unique effect/due-ref pairs and
  validates supplied declarations only; global completeness is deferred;
- `UncertaintyRecord` includes the explicit violated-contract coordinate,
  with exact OUT_OF_SET role/provenance identity and typed not-applicability
  for every other kind;
- envelope validation recursively excludes direct exact stored-hash string
  occurrences before final recomputation, while alias/graph cycles are
  expressly deferred;
- `SupersessionRelation` has exactly the eleven ordered predecessor/successor
  coordinates in §21.5, and kind/schema equality is directly observable
  without lookup or inference;
- every fixture/supplement record has one exact formation/semantic failure
  owner, all Block-5 through Block-8 candidates reach their declared public
  boundary, and no constructor pre-empts or relabels a validator predicate;
- the historical v0.1.6/v0.2.6 fixture identity is first reproduced exactly
  as 335 vectors and 809,689 bytes at raw SHA-256
  `92664cb12ace29dc05d3fd7bbd1b349c6edfd6bb0cc60708acdbff0678d4fcf9`,
  with no trailing LF; then two independent external standard-library
  reconstructions agree byte for byte on the prospective fixture, all 335
  IDs/names and 214 failure IDs, and report no incompatible effective-input
  collision;
- the only logical fixture delta is the inputs of `i2-0149` through
  `i2-0158`, with zero additions/removals and unchanged outcomes, codes,
  failure IDs, and projections; the two authority fields change mechanically;
- `i2-0154` proves quantity/source inequality and `i2-0156` proves
  quantity/source equality plus rule/source inequality, and the distinction
  survives every bijective renaming of opaque refs;
- all 29 I-1 failure codes and 95 existing `_fail` call semantics remain
  preserved while the exact 24 I-2 codes and deterministic typed envelope are
  frozen;
- the accepted I-2 manifest is exactly nine paths, existing
  `tests/framework/safety.py` remains unchanged, and packaging needs no
  amendment;
- the post-I-2 public inventory is exactly 84 types, 42 callables, and one
  version name in a sorted 127-entry root export tuple;
- UQ-02 is limited to the exact substrate/interface boundary and every
  policy-required I-2 operation refuses without invoking a provider;
- ECJ-1 is byte-exact and resolves the RFC 8785 ordering conflict explicitly;
- ECJ-1 assignment and NFC are bound to raw-hash-pinned Unicode 15.0.0 assets,
  reject later-assigned code points independently of the host, and have a
  complete pinned normalization corpus in the manifest;
- ID allocation is deterministic, stable, content-neutral, and
  non-self-referential;
- every specification-required hash maps to an exact named preimage or to the
  explicitly distinct artifact/raw-source rules;
- authorization covers authenticity, bootstrap trust, issuer scope,
  delegation, trusted time, revocation, exact operation/targets,
  predecessor evidence, single use, and an external non-recursive envelope;
- UQ-36 has a closed included/excluded classification;
- the fault base does not define UQ-38 science;
- every proposed file and public interface is enumerated;
- `pyproject.toml` explicitly grants I-4—and no intervening stage—ownership of
  the exact UQ-25 Ed25519 dependency-metadata update paired with lock
  finalization;
- revision v0.2.1's packaging-blocker statement is historical, the existing
  packaging amendment and contract retain their narrow prospective
  precedence, and this amendment neither edits nor repeats them;
- T0 structural operations may receive supplied immutable scientific records
  without evaluating science, while enclosing T2/T3 context escalates the
  invocation and cannot be lowered;
- validation cannot reach scientific execution;
- the four release milestones have distinct prerequisites, evidence, tag
  namespaces, branch strategies, and nonclaims;
- stages, dependencies, acceptance criteria, failures, exclusions, decisions,
  threats, and deferred questions are explicit;
- the complete document and diff pass static inspection and
  `git diff --check`; and
- no code, implementation fixture, test, package, repository directory,
  result, branch, tag, release, model state, or scientific execution was
  created or run; only these five unstaged documentation/mechanical-authority
  files exist after validation.

This revision establishes prospective I-3 documentation locks only. Neither
its existence nor its review reopens I-2, begins I-3A implementation, or
authorizes I-4 through I-8 behavior, a framework-alpha milestone, scientific
execution, Gate operation, publication, release, or other later stage.

## 20. Document revision history

### 20.1 Original plan v0.2 — historical

The original plan's whole-file SHA-256 is
`a1cebfa63528e49d9bada3c6564c7d40616369a45afd97640ff937ae07389674`.
Its starting repository SHA, original I-0 verification table, original
specification hash, and original books-structure hash remain historical
evidence. They do not claim that the v0.1.1 specification or later
books-structure bytes were verified during original I-0.

### 20.2 Revision v0.2.1 — historical prospective amendment

Revision v0.2.1 adopts specification v0.1.1 at raw SHA-256
`a52b0232595719afd554d842aefb16d6dba0e039ced75c4aed05b358964c6de1`
and the v0.2.1 books-structure raw SHA-256
`4dcccf8dfbcb12b8db983abd33892c9a98084c40a9e61790027324e5c9691b3c`
as its then-active mechanical authority locks. It adds no implementation file,
backend, dependency, fixture, test, or scientific permission. Its exact
historical whole-file SHA-256 is
`d89fe92ac6cafd8990588e72d294bcf547cbb478d4b43b638a380e38116ba42e`.

### 20.3 Revision v0.2.2 — historical prospective reconciliation

Revision v0.2.2 adopted specification v0.1.2 at historical raw SHA-256
`32bc5b9d1983b3b46242d0ccc9323636847d1c8cfeea641f64796f0665916f69`
and the literature-extended books structure at raw SHA-256
`120496aa0d304561e16b3556bbbd5300c651a3082a297fd21f6bad6034746255`.
This narrow reconciliation recorded the added bibliography and
citation policy, prior-art and nearest-antecedent mapping,
candidate-contribution boundaries, bibliography/endnote page reserves, and
literature checkpoints before manuscript generation.

It changed no implementation stage, closed manifest, API, invariant,
decision, threat, validation fixture, dependency selection, packaging rule,
scientific semantic, Gate rule, or execution permission. It preserved the
distinction among physical measurement, causal inference, policy, and
settlement. It neither edited nor repeated the existing packaging resolution
and granted no integration, I-2, framework-alpha, scientific-execution, Gate,
publication, or release authority. Its exact historical whole-file SHA-256
is `3422a0887b82637ce323de7015869770ffa59408cb11907f7266ed0e95a22a9c`.

### 20.4 Revision v0.2.3 — historical prospective I-2 authority amendment

Revision v0.2.3 adopts specification v0.1.3 at raw SHA-256
`44ae0d5587b24bbca32acda822cddfdc7db76795f81337cd8fc7951bf2946193`
and freezes the prospective I-2 mechanics in §21. The v0.2.2 whole-file
SHA-256
`3422a0887b82637ce323de7015869770ffa59408cb11907f7266ed0e95a22a9c`
is immutable historical evidence. Revision v0.2.3 has exact whole-file
SHA-256
`bcc25725575dcd0905a17dc7712da9e534a92c3e6e5335e65248979ad1c22d46`.

### 20.5 Revision v0.2.4 — historical prospective I-2 validation correction

Revision v0.2.4 adopted specification v0.1.4 at its then-active raw SHA-256
recorded in §1.3's historical revision register. It corrected only the
Block-5 collision between structurally absent case
16 and explicitly `NOT_APPLICABLE` case 34, while preserving their respective
`IMPLICIT_ABSENCE_FORBIDDEN` and `NUMERICAL_POLICY_INCOMPLETE` outcomes. It
changes no other case, count, interface, manifest, dependency, scientific
definition, Gate record, package, I-1 byte, or accepted milestone. Its raw
SHA-256 is
`bd65010e6231f71d68d9e2165f723efab5175d2e8ea3c05d8624a060602ac6ff`.

### 20.6 Revision v0.2.5 — historical prospective I-2 authority correction

Revision v0.2.5 adopted specification v0.1.5 at its then-active raw SHA-256
recorded in §1.3's historical revision register. It froze direct predecessor/successor supersession kind/schema
coordinates, explicit typed-not-applicable authorization refusal, and the
complete constructor-versus-validator responsibility and reachability
contract. It preserves all 335 IDs and names, block/outcome counts, expected
outcomes and codes, API/export/path/dependency counts, scientific definitions,
Gate record, package, I-1 bytes, and accepted milestones. Its raw SHA-256 is
`8db6a9bac25aaa7654d614497640e8429888416d01148e1b33fe2026ce4200c6`.

### 20.7 Revision v0.2.6 — historical prospective I-2 predicate-observability correction

Revision v0.2.6 adopted specification v0.1.6 at historical raw SHA-256
`884767698f26ca75b59ab51d3d95a06e7f2996ae7071145b2f5564baed6787d2`
and corrected all eight then-known I-2 predicate-observability defects under
the exact argument-only T0 rule. It updates only prospective authority,
mechanical signatures/fields, fixture derivation, static coverage, and
explicit later-stage nonclaims. It changes no scientific definition, Gate
record, implementation byte, package, accepted milestone, public type or
callable count, dependency edge, or future path count. Its exact whole-file
SHA-256 is
`34241b44b5d6b8bc5b5d6fea6e517afa47507b4cd905eea464347e9865eedc97`.

### 20.8 Revision v0.2.7 — historical prospective I-2 source-unit authority correction

Revision v0.2.7 adopted specification v0.1.7 at historical raw SHA-256
`01f7392459af3eaccbd6966b1504fa1206997722677415d080b0b6883d8081ca`
and added the explicit source-unit argument required to distinguish
quantity/source disagreement from rule/source disagreement locally. It
changes only prospective authority, the existing callable's argument
structure, the ten conversion-vector input recipes and adapter instructions,
and dependent static audit/acceptance text. It preserves every vector ID,
name, expected outcome/code, failure coordinate/ID, projection, block/outcome
count, public type/callable/export count, path, dependency, scientific
definition, UQ-40 deferral, Gate record, package, I-1 byte, and accepted
milestone. Its historical raw SHA-256 is
`f152d680028c4f35027371d036d7282fd1c5648274018237f98626afbacf170e`.

### 20.9 Revision v0.2.8 — historical prospective conservation-authority reconciliation

Revision v0.2.8 adopted specification v0.1.8 at historical raw SHA-256
`ff81bbe7bcf1e5a9ae7a7ecb9663a89aceb677f5d3642e4c9e225e56a36e16d3`,
the conservation-extended books structure, and the conservation and boundary-
accounting foundation. It records the three account levels, preserves reduced
and open accounts as first-class supported cases, and assigns only optional
future profile declaration to a separately authorized I-3 stage and profile-
specific residual validation to a later separately authorized I-5 stage.

It preserves all equations, algorithms, constants, theorems, tests, results,
protocols, Gate rules, interpretation boundaries, and the exact accepted I-2
implementation. It adds no universal zero-residual rule, hidden tolerance,
implementation path, public type, callable, export, dependency, fixture,
schema, workflow, executable permission, Bridge/Dynamic amendment, or
scientific claim. Its historical whole-file SHA-256 is
`91180a812a909c644692b11aadf659930567f0853d1e10a19e6f98b699e2a6ce`.

### 20.10 Revision v0.2.9 — current prospective I-3 authority closure

Revision v0.2.9 adopts specification v0.1.9 at raw SHA-256
`3eb023e4a729fe5205f4edf476d1347cc2584a99467648ce552c98954bd976e4`
and the complete prospective I-3 authority in §22. The normative human
amendment has raw SHA-256
`a392874c473219df9a24d044dee7444327f347924438cd8a86627f69f79d3be2`;
the mechanical contract has raw/canonical SHA-256
`505fcad67139bcf9c45d38a59c759f06d9e347e995d50c5ea8c3637ebe4cbcbb` /
`3a56b15447ccedd39eb473f8e7838fbba6cbbb0f4d85a60c9b68d26ca5aa8f22`;
and the validation contract has raw/canonical SHA-256
`0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0` /
`88283fe2efda6c769688985805d3654d6deb5016195ea119f337b2fd843dd8ec`.

It freezes declarative I-3 types, local T0 validators, projections, failures,
exports, imports, validation vectors, conservation profiles, stage ownership,
and review-size substages. It adds no implementation byte or fixture and
authorizes no implementation, registry acceptance, behavior, scientific use,
execution, Gate operation, finalization, or publication. This file does not
contain its own current whole-file hash; that value remains external.

## 21. Normative prospective Framework I-2 implementation authority

This section is retained as the complete mechanical authority implemented and
accepted at `351417c39fa26b9045e7c162a9897a7c38e4e1d1` and integrated at
`ede89d8af6b89da491e03c352efcf1868a913f6f`. Its v0.2.7 future-tense language
and authority locks are historical acceptance inputs. Revision v0.2.9 changes
none of its manifests, inventories, fixtures, hashes, paths, dependencies,
failure semantics, precedence, exports, API, capability, or exclusion rules.

This section supersedes only incomplete or provisional I-2 implementation
details elsewhere in its historical design record. Specification v0.1.7 §21
controls every I-2 semantic, field, projection, invariant, operation-matrix
cell, predicate,
failure meaning, precedence rule, fixture requirement, exclusion, and
nonclaim. This section is the mechanical path, export, ownership, dependency,
and validation source. Any mismatch fails closed; neither source may be
selected piecemeal.

At the v0.2.7 freeze this was authority for a future separately authorized
implementation task. The accepted feature and integration commits named above
subsequently satisfied that stage without changing the contract. This
v0.2.9 amendment supplies no permission to alter I-2. Its separate §22 closes
prospective I-3 authority but supplies no permission to implement I-3A or
begin I-4 through I-8 behavior.

### 21.1 Accepted predecessor and fixed failure audit

The starting repository evidence for this amendment is branch
`framework-v0.1` at
`64e7d692dbae2c3beb6752d955c8f6193e481010`, subject `Synchronize framework
authority with foundation v0.1.2`, with ordered parents
`f0f8ed8a7d19991f5084ac203cea0a243de8b46d` and
`38aae5e8c59d0bced598f2918f76dbee6df7481c`. Local, remote-tracking, and live
remote tips matched and the tree/index were clean before amendment.

The accepted I-1 source audit is exact: 95 `_fail` calls—23 in
`canonical.py`, 14 in `hashing.py`, 13 in `identity.py`, and 45 in
`registry.py`. Every call supplies exactly two positional arguments and no
keyword. The only direct `FrameworkError` construction is within `_fail` in
`errors.py`; no I-1 test directly constructs `FailureEnvelope` or
`FrameworkError` or relies on the former untyped defaults. Therefore the
backward-compatible specification outcome is mandatory and the manifest need
not add an I-1 caller or existing test.

The aggregate I-1 evidence has two non-conflicting path scopes. Commit
`ed75790b20c7d6b86cedc4d9dbeb269f32cca9ea` itself introduced 22
implementation paths. The closed feature range from
`fae76042746e55b9fe5ec5c62de0f47fbc5ccb47` through that commit contains the
same 22 plus the packaging Markdown and JSON authority, for 24 paths. The
historical aggregate digest
`f7b1b7abc9a71b090320b8dc468d57e3a7e39f4f2a045b7a5946a4174882fee8`
is corroboration only: its serialization recipe was not committed, it is not
independently reproducible, and it is not an I-2 semantic input. Git
path/blob identities, raw hashes, and byte sizes provide current integrity.

All 29 accepted I-1 failure codes retain their exact names and meanings:

```text
ALIAS_CONFLICT
ALIAS_INVALID
ALLOCATION_CLAIM_CONFLICT
ALLOCATION_COLLISION
ARTIFACT_TOO_LARGE
CANONICALIZATION_FAILURE
CYCLIC_OBJECT_GRAPH
DIGEST_INVALID
DIGEST_TYPE_MISMATCH
DUPLICATE_OBJECT_NAME
ECJ1_TYPE_UNSUPPORTED
FLOAT_FORBIDDEN
HASH_DOMAIN_MISMATCH
HASH_MISMATCH
INVALID_ECJ1
INVALID_UNICODE_SCALAR
NAMESPACE_UNREGISTERED
NONCANONICAL_ECJ1
REF_NOT_FOUND
REGISTRY_IMMUTABLE
REGISTRY_RECORD_CONFLICT
RESERVED_NAMESPACE
SCIENTIFIC_ID_INVALID
SEMANTIC_VERSION_INVALID
STABLE_KEY_INVALID
UNASSIGNED_UNICODE_SCALAR
UNICODE_DATA_INTEGRITY_FAILURE
UNICODE_DATA_MALFORMED
VERSION_MISMATCH
```

I-2 adds exactly the following 24 codes, with the meanings and precedence in
specification §21.2.4; no further code is authorized:

```text
BOUNDARY_MISMATCH
CLOCK_MISMATCH
CONVERSION_RULE_MISMATCH
CORE_NUMBER_INVALID
DIMENSION_MISMATCH
DIVISION_BY_ZERO
ERROR_BOUND_INVALID
HORIZON_INVALID
IMPLICIT_ABSENCE_FORBIDDEN
IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN
INVALID_AGGREGATION
LIFECYCLE_TRANSITION_INVALID
NONFINITE_NUMBER_FORBIDDEN
NUMERICAL_OPERATION_UNSUPPORTED
NUMERICAL_POLICY_INCOMPLETE
NUMERICAL_POLICY_REQUIRED
QUANTITY_TYPE_MISMATCH
REGION_MISMATCH
RESOLUTION_STATE_INVALID
SIGN_CONVENTION_MISMATCH
SUPERSESSION_INVALID
TIME_BASIS_MISMATCH
UNCERTAINTY_RECORD_INVALID
UNIT_MISMATCH
```

### 21.2 Exact nine-path I-2 implementation manifest

The future I-2 change set is exactly these paths and states:

| State | Path | Narrow I-2 ownership |
|---|---|---|
| Modified | `src/ebu_framework/__init__.py` | Set the exact §21.3 imports and 127-entry root `__all__`; leave `__version__ = "0.1.0a1"` unchanged |
| Modified | `src/ebu_framework/errors.py` | Add only the specification §21.2 typed common failure fields/types, stable ID allocation, closed four-module I-1 compatibility map, and exact 24 I-2 codes; preserve every I-1 code/string/call-site behavior |
| Modified | `src/ebu_framework/registry.py` | Strengthen only `RegistryRecord.lifecycle_status` to `LifecycleStatus`; `register_draft` still accepts only `DRAFT`; resolution and alias behavior unchanged; no acceptance/supersession mutation |
| New | `src/ebu_framework/envelopes.py` | Exact common envelope/metadata and pure lifecycle/supersession records and validators; stores only canonical `CanonicalBytes`, imports only `CanonicalBytes`/`parse_ecj1` from `canonical`, and retains no decoded tree |
| New | `src/ebu_framework/numeric.py` | Exact core numeric substrate, result/policy records, I-2-owned `RuntimeConstraintSet`, and structural policy validation without provider invocation |
| New | `src/ebu_framework/primitives.py` | Exact typed primitive records and pure compatibility/conversion validators |
| New | `tests/framework/fixtures/numeric_vectors_v1.json` | Exact deterministic 335-vector specification §21.8 / plan §21.5 fixture |
| New | `tests/framework/test_numeric.py` | T0 exact numeric/projection/failure/policy-refusal checks against the fixture |
| New | `tests/framework/test_primitives_envelopes.py` | T0 primitive/envelope/lifecycle checks, the exact specification §21.8.6 all-record static supplement, nine immutable-byte checks, plus source-text/AST import/export/29-edge reachability audit |

No tenth path is authorized. In particular,
`tests/framework/safety.py` remains unchanged because the new test can perform
the required AST/export audit directly and reuse existing guards without
altering them. The frozen backend's manifest-selection rule already permits
the three new `src/ebu_framework/*.py` paths once they are present in the
accepted stage manifest; the tests and fixture remain excluded from wheel and
sdist exactly as before. No packaging authority amendment is required.

The following remain byte-for-byte unchanged during I-2:

```text
build_backend/ebu_build_backend.py
pyproject.toml
requirements-framework.lock
src/ebu_framework/canonical.py
src/ebu_framework/hashing.py
src/ebu_framework/identity.py
src/ebu_framework/data/core_registry_v1.json
tests/framework/safety.py
UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I1_PACKAGING_AMENDMENT.md
unified_python_research_framework_packaging_contract.json
```

All scientific, Gate, result, historical runner/finalizer, and other
repository paths are also unchanged.

### 21.3 Exact post-I-2 public API

The exact post-I-2 public type inventory contains 84 names. Module ownership
is closed as follows:

| Owner | Exact public types |
|---|---|
| `errors` | `Applicability`, `CanonicalTraceState`, `DurabilityState`, `FailureCode`, `FailureEnvelope`, `FailureEventKey`, `FailureEvidenceRef`, `FailureId`, `FailureInterfaceRef`, `FailureObjectRef`, `FailureStage`, `PolicyMemoryAdvance`, `RetryClass`, `ScientificStatusEffect`, `StateAdvance` |
| `canonical` | `CanonicalBytes`, `CanonicalizationVersion`, `ECJ1Value` |
| `identity` | `ArtifactByteHash`, `AugmentedClosedLoopReplayStateHash`, `AuthorizationUseKey`, `CanonicalScientificTracePayloadHash`, `CanonicalTracePrefixHash`, `CanonicalTraceRowHash`, `ExecutionSemanticsHash`, `InformationViewHash`, `ObjectContentHash`, `ObjectRef`, `PolicyMemoryPayloadHash`, `ProposalSetHash`, `RepresentedStateProjectionHash`, `ScientificId`, `ScientificIdAllocationClaimV1`, `SemanticVersion`, `SourceFileRawSha256`, `StatePayloadHash` |
| `registry` | `AliasRecord`, `NamespaceEntry`, `NamespaceRegistrySnapshot`, `RegistryRecord`, `ResolutionRecord` |
| `numeric` | `Binary64BitsV1`, `ComparisonResult`, `Completeness`, `CoreNumberV1`, `DecimalV1`, `ErrorBound`, `ExactConversion`, `IntegerV1`, `NumericalOperation`, `NumericalPolicyV1`, `NumericalResult`, `NumericalVariant`, `OperandValidationResult`, `QuantityContext`, `RationalV1`, `RuntimeConstraintSet` |
| `envelopes` | `CommonObjectEnvelope`, `LifecycleStatus`, `LifecycleTransition`, `LifecycleValidationResult`, `RecordMetadata`, `SupersessionRelation`, `SupersessionValidationResult` |
| `primitives` | `AccountingBoundary`, `ClaimStatus`, `ClockSystem`, `CompatibilityResult`, `ConversionRule`, `Dimension`, `Duration`, `Epoch`, `Horizon`, `Instant`, `Quantity`, `Region`, `ResolutionDetail`, `ResolutionState`, `ResourceType`, `ServiceType`, `SignConvention`, `UncertaintyKind`, `UncertaintyRecord`, `Unit` |

The exact post-I-2 public callable inventory contains 42 names. The 21
accepted I-1 callables remain unchanged:

```text
allocate_scientific_id
compute_artifact_byte_hash
compute_augmented_replay_state_hash
compute_canonical_trace_payload_hash
compute_canonical_trace_prefix_hash
compute_canonical_trace_row_hash
compute_execution_semantics_hash
compute_information_view_hash
compute_object_content_hash
compute_policy_memory_payload_hash
compute_proposal_set_hash
compute_represented_state_projection_hash
compute_source_file_raw_sha256
compute_state_payload_hash
encode_ecj1
parse_ecj1
parse_scientific_id
parse_semantic_version
register_draft
resolve_alias
resolve_ref
```

I-2 adds exactly these 21 T0 callables with the signatures and behavior in
specification §§21.3–21.6:

```text
apply_exact_core_operation
convert_quantity_exact
decimal_to_rational_exact
normalize_core_number
validate_boundary_compatibility
validate_clock_compatibility
validate_conversion_rule
validate_dimension_compatibility
validate_horizon
validate_lifecycle_transition
validate_numerical_policy
validate_object_envelope
validate_quantity
validate_region_compatibility
validate_resolution_detail
validate_resource_service_compatibility
validate_sign_convention_compatibility
validate_supersession_relation
validate_time_basis
validate_uncertainty_record
validate_unit_compatibility
```

The existing callable count is unchanged. Its corrected conversion signature
is exactly:

```text
convert_quantity_exact(
    quantity: Quantity,
    source_unit: Unit,
    target_unit: Unit,
    rule: ConversionRule,
) -> Quantity
```

No overload, default, variadic adapter, resolver callback, or additional
public conversion callable is authorized.

With `__version__`, the exact root export count is therefore
`84 + 42 + 1 = 127`. `ebu_framework.__all__` is the following exact
lexicographically ordered tuple; no extra, missing, duplicate, or differently
ordered name conforms:

```text
AccountingBoundary
AliasRecord
Applicability
ArtifactByteHash
AugmentedClosedLoopReplayStateHash
AuthorizationUseKey
Binary64BitsV1
CanonicalBytes
CanonicalScientificTracePayloadHash
CanonicalTracePrefixHash
CanonicalTraceRowHash
CanonicalTraceState
CanonicalizationVersion
ClaimStatus
ClockSystem
CommonObjectEnvelope
ComparisonResult
CompatibilityResult
Completeness
ConversionRule
CoreNumberV1
DecimalV1
Dimension
DurabilityState
Duration
ECJ1Value
Epoch
ErrorBound
ExactConversion
ExecutionSemanticsHash
FailureCode
FailureEnvelope
FailureEventKey
FailureEvidenceRef
FailureId
FailureInterfaceRef
FailureObjectRef
FailureStage
Horizon
InformationViewHash
Instant
IntegerV1
LifecycleStatus
LifecycleTransition
LifecycleValidationResult
NamespaceEntry
NamespaceRegistrySnapshot
NumericalOperation
NumericalPolicyV1
NumericalResult
NumericalVariant
ObjectContentHash
ObjectRef
OperandValidationResult
PolicyMemoryAdvance
PolicyMemoryPayloadHash
ProposalSetHash
Quantity
QuantityContext
RationalV1
RecordMetadata
Region
RegistryRecord
RepresentedStateProjectionHash
ResolutionDetail
ResolutionRecord
ResolutionState
ResourceType
RetryClass
RuntimeConstraintSet
ScientificId
ScientificIdAllocationClaimV1
ScientificStatusEffect
SemanticVersion
ServiceType
SignConvention
SourceFileRawSha256
StateAdvance
StatePayloadHash
SupersessionRelation
SupersessionValidationResult
UncertaintyKind
UncertaintyRecord
Unit
__version__
allocate_scientific_id
apply_exact_core_operation
compute_artifact_byte_hash
compute_augmented_replay_state_hash
compute_canonical_trace_payload_hash
compute_canonical_trace_prefix_hash
compute_canonical_trace_row_hash
compute_execution_semantics_hash
compute_information_view_hash
compute_object_content_hash
compute_policy_memory_payload_hash
compute_proposal_set_hash
compute_represented_state_projection_hash
compute_source_file_raw_sha256
compute_state_payload_hash
convert_quantity_exact
decimal_to_rational_exact
encode_ecj1
normalize_core_number
parse_ecj1
parse_scientific_id
parse_semantic_version
register_draft
resolve_alias
resolve_ref
validate_boundary_compatibility
validate_clock_compatibility
validate_conversion_rule
validate_dimension_compatibility
validate_horizon
validate_lifecycle_transition
validate_numerical_policy
validate_object_envelope
validate_quantity
validate_region_compatibility
validate_resolution_detail
validate_resource_service_compatibility
validate_sign_convention_compatibility
validate_supersession_relation
validate_time_basis
validate_uncertainty_record
validate_unit_compatibility
```

The exact new/modified module `__all__` subsets are the names assigned to
each owner above plus its assigned callables: `errors` 15, `numeric` 20,
`envelopes` 10, and `primitives` 34. `FrameworkError`, `_fail`, helper
constructors, projection helpers, enum aliases, and imported names remain
private. `accept_registry_object` and `supersede_registry_object` are absent
from the post-I-2 API and assigned to I-4.

### 21.4 Capability, dependency, and cycle contract

Every new I-2 callable is T0. It may construct, normalize, project, compare
exact core numbers, perform an exact conversion from explicitly supplied
quantity/source-unit/target-unit/rule arguments, or
validate immutable structure. No I-2 callable accepts a capability token,
invokes a `NumericalPolicyV1` method, performs registry mutation, evaluates a
scientific mapping, inspects an outcome, advances state, or enters T1, T2, or
T3.

The exact relevant production import DAG after I-2 is:

```text
errors -> Python standard library only
canonical -> errors + pinned Unicode package data
identity -> canonical, errors
hashing -> canonical, identity, errors
envelopes -> canonical, hashing, identity, errors
registry -> canonical, identity, errors, envelopes
numeric -> canonical, identity, errors
primitives -> numeric, identity, envelopes, errors
__init__ -> canonical, errors, hashing, identity, registry, numeric,
            envelopes, primitives
```

Counting only directed package-module imports—not the canonical module's
resource read of pinned Unicode package data—this DAG has exactly 29 edges.
The prior inventory had 28; `envelopes -> canonical` is the sole added edge.
The displayed topological order
`errors, canonical, identity, hashing, envelopes, registry, numeric,
primitives, __init__` proves acyclicity because every edge points from a later
node to an earlier node. `numeric` and `registry` are incomparable siblings;
their displayed relative order is immaterial because neither imports the
other.

The new edge is narrow: `envelopes.py` may import exactly `CanonicalBytes` and
`parse_ecj1` from `canonical.py`, may call `parse_ecj1` only to validate or
freshly decode stored payload bytes, and must immediately discard the decoded
value after validation/hash construction. It may not import `encode_ecj1`,
normalization/Unicode internals, or `registry`; retain a decoded cache; or use
dynamic import. No reverse edge from canonical, hashing, or identity into
envelopes is permitted. No reverse edge into `errors` and no
`primitives -> registry` is permitted. Production and test/validation code
must not use dynamic import. No listed module may import or refer to a
scientific module, historical `exp_*`, runner, finalizer, result, Gate,
network, subprocess, packaging hook, or dependency-installation path.

The backward-compatible `_fail` mechanism may inspect only the immediate
caller module name against the closed four-entry map frozen by specification
§21.2.3. It cannot walk arbitrary frames, infer a later stage, or expose a
universal I-1 default. Every I-2 call supplies `FailureStage.I2` and an exact
`FailureInterfaceRef` explicitly.

### 21.5 Deterministic validation and readiness contract

`tests/framework/fixtures/numeric_vectors_v1.json` is the exact 335-vector
ECJ-1 sequence in specification §21.8: block counts
`18,35,42,4,36,107,20,41,32`, first ID `i2-0001`, terminal ID `i2-0335`.
Its schema/key order, literal catalog, nested-loop order, input patches,
projections, canonical hex, failure coordinates/IDs, and authority-field
placement are closed. It binds the accepted specification v0.1.7 raw hash
above and the future accepted plan v0.2.7 raw hash reported externally after
this document is complete. It is static validation data, not a policy, world,
configuration, trajectory, or result.

Before deriving prospective bytes, the external stdlib-only authority audit
must reproduce the exact historical v0.1.6/v0.2.6 fixture: 335 vectors,
809,689 bytes, raw SHA-256
`92664cb12ace29dc05d3fd7bbd1b349c6edfd6bb0cc60708acdbff0678d4fcf9`,
and no trailing LF. The prospective fixture is then independently built by
two stdlib-only routes. The routes must agree byte for byte and report the
total, nine block counts, outcome counts, bytes, SHA-256, LF status, every
changed/added/removed vector, all derived failure IDs and canonical
projections, effective-input collision audit, and public-boundary
reachability. Neither fixture nor generator is created in the repository by
this document-only task.

Every T0 validator implementation uses only the exact declared values of its
arguments. An `ObjectRef` proves identity only. Registry/envelope/alias
lookup, inferred lifecycle/kind/role/content, hidden mutable state,
fixture-specific knowledge, and construction/patch history are forbidden.
The exact corrected public signatures are:

```text
convert_quantity_exact(
    quantity: Quantity,
    source_unit: Unit,
    target_unit: Unit,
    rule: ConversionRule,
) -> Quantity

validate_conversion_rule(
    rule: ConversionRule,
    source_unit: Unit,
    target_unit: Unit,
) -> CompatibilityResult

validate_horizon(
    horizon: Horizon,
    pending_effect_due_pairs: tuple[tuple[ObjectRef, ObjectRef], ...],
) -> CompatibilityResult
```

The prospective implementation additionally freezes these mechanical
responsibilities:

- numerical policy refs are declared identities only; policy/owner identities
  differ, `COMPARE` always requires an exact tolerance ref, and lifecycle,
  placeholder, kind, role, and referenced contents are not resolved;
- conversion-rule validation receives both units and shares exact
  factor/offset, direction/orientation, endpoint, three-way dimension, and
  declared horizon rules with unit compatibility; exact quantity conversion
  receives the quantity plus explicit source and target units, requires exact
  quantity/source ref equality, compares quantity/source/target dimensions,
  and then calls or faithfully reuses those ordered rule predicates;
- region parent success checks only exact declared parent links, parent/child
  clocks and intervals, distinct IDs, and aggregation-ref presence;
  `membership_rule_ref` remains opaque and disjointness is deferred;
- `AccountingBoundary` has the exact final field
  `cross_boundary_effect_treatments`, whose exact `(effect_ref,treatment_ref)`
  pairs are ordered by unique effect key; each child's keys equal the union of
  its two declared cross-effect tuples, without a completeness/adequacy claim;
- horizon pair arguments have exact pair/member types, effect-ref order, and
  unique keys; `REQUIRE_NONE_PENDING` requires empty input and
  `ALLOW_EXPLICIT_PENDING` accepts supplied ordered pairs without claiming
  global completeness or resolving due conditions;
- `UncertaintyRecord` has the exact `violated_contract_ref` coordinate;
  OUT_OF_SET requires an exact ref, the same provenance ref, and a present
  supplied value, while all other kinds require typed `NOT_APPLICABLE`;
- envelope `direct_content_hash_exclusion` recursively rejects the exact
  stored hash string as an object name, object value, or array member before
  final recomputation; alias/ref/registry/object-graph cycles are deferred.

The exact conversion implementation order and locally observable evidence
are: `quantity_valid` from the supplied quantity's intrinsic required state;
`source_unit` from `quantity.unit_ref` and `source_unit.unit_ref` with
`UNIT_MISMATCH`; `target_unit` from the quantity/source/target dimensions
with `DIMENSION_MISMATCH`; `conversion_rule` by calling or faithfully reusing
`validate_conversion_rule(rule,source_unit,target_unit)` with
`CONVERSION_RULE_MISMATCH`; and `exact_arithmetic` from the supplied magnitude,
factor, and offset with unchanged exact-refusal semantics. The
`reverse_not_explicit` rejection supplies UNIT_B as source and UNIT_A as
target and is witnessed by the unchanged forward-only rule. Rule-declared
dimension disagreement is owned by the rule validator; no unit is resolved
or inferred.

Within Block 5, case 16 has exactly `remove /precision_contract_ref` and
expects `IMPLICIT_ABSENCE_FORBIDDEN`; case 34 has exactly
`replace /precision_contract_ref NA`, leaves baseline `/completeness` equal to
`COMPLETE`, and expects `NUMERICAL_POLICY_INCOMPLETE`. Validation uses only the
resulting declaration and never patch history.

V2 checks the closed finite basis: all four numeric forms; the 25 binary/four
unary cells; exact conversions and terminating/repeating division; the ten
finite and six nonfinite bit patterns; the exact 17-case `ErrorBound` basis;
policy completeness/refusal; the exact 107 compatibility vectors; all
resolution/uncertainty states and explicit violated-contract roles; declared
boundary-treatment coverage and horizon effect/due pairs; 20 envelope
vectors; 25 lifecycle cells, three
lifecycle evidence refusals, and 13 supersession vectors; 23 adjacent
precedence pairs and nine multiply-invalid cases. Infinite numeric/graph
domains remain constructor/algebra/predicate proof obligations; the fixture
detects implementation disagreement and is not exhaustive empirical proof.

The I-2 portion of V3 is exactly static construction and projection of
`CommonObjectEnvelope` with exact canonical bytes, `RecordMetadata`,
`LifecycleTransition`, `SupersessionRelation`, and the strengthened draft-only
`RegistryRecord`. `test_primitives_envelopes.py` performs eleven frozen
envelope/immutability checks: source encoded before construction; source mutation
invariance; independent parsed-tree mutation invariance; direct
dict/list/bytearray/memoryview rejection; noncanonical-byte rejection; exact
hash reproduction; metadata/lifecycle invariance; invalid-or-different-hash
byte mutation; absence of a decoded mutable cache; recursive direct stored-hash
occurrence refusal; and a static alias/graph-resolution nonclaim. Its static
supplement also covers boundary treatment-pair formation/coverage and horizon
effect/due-pair formation/duplicates. No production alias or graph lookup is
added. Every other V3 record is I-3 or later and unreachable.

The complete public-record closure audit is specification §21.8.6. It covers
every concrete I-2 error, numeric, primitive, envelope, and strengthened
registry record; all 16 relevant public enum domains; the exact
`CoreNumberV1` union; and the property/method surface and noninvocation of
`NumericalPolicyV1`. Its non-fixture supplement has exact names, inputs,
expected projections/codes, and one independently derived nonempty-coordinate
failure ID. Revision v0.2.7 adds the exact
`conversion-source-anchor-opaque-renaming` static assertion from specification
§21.8.6; it adds no fixture vector or public boundary. This adds no public
name, callable, dependency edge, or tenth
path. The closed totals are 84 types, 42 callables, `__version__`, 127 root
exports, 29 I-1 plus 24 I-2 failure codes, 24 I-2 precedence entries, 29 DAG
edges, and nine future paths.

Implementation must follow the responsibility table rather than infer
semantic acceptance from `dataclass` construction. Constructors establish
only the formation checks assigned there. Each public `validate_*` callable
owns every named predicate in its frozen order and receives all information
needed for it through exact arguments plus an immutable,
structurally well-formed candidate that may be semantically invalid. No
`__new__` bypass, mutation, unchecked/test mode, raw mapping contrary to a
signature, caught-and-relabelled constructor exception, patch-history check,
registry lookup, envelope/alias lookup, inferred ref contents, hidden state,
fixture-specific knowledge, or dynamic import is permitted. A candidate
is not valid, lifecycle-accepted, scientifically accepted, or registry-
accepted until the appropriate validator and later authorized boundary have
succeeded.

The complete predicate-observability audit was repeated across common failure
formation, all core-number/bound/result operations, numerical-policy
validation, every primitive compatibility validator, exact quantity
conversion, envelope validation, lifecycle validation, supersession
validation, all 24 I-2 precedence codes, and the retained I-1 failure
boundary. Each distinction is witnessed by exact constructor values or exact
declared public arguments. After the explicit source-unit correction, no
other failure-code distinction lacks an argument witness and no outcome
depends on a lookup, hidden state, fixture identity, patch history, inferred
ref contents, or a privileged literal ref.

The future `SupersessionRelation` implementation has exactly eleven fields in
this order:

```text
predecessor_ref
successor_ref
predecessor_object_kind_id
successor_object_kind_id
predecessor_schema_id
successor_schema_id
predecessor_status
successor_status
predecessor_supersedes_chain
relation_evidence_refs
authorization_ref
```

The last field is exactly `ObjectRef | Applicability`; it has no default.
Predicate `object_kind_id` directly compares the two kind fields and predicate
`schema_id` directly compares the two schema fields. No registry, envelope,
inferred metadata, patch history, or external state supplies a missing
coordinate. `SUPER0` uses equal `SID(4)` kind fields and equal `SID(5)` schema
fields. Its isolated kind/schema rejections replace only the corresponding
successor field with `SID(63)`. Its authorization rejection retains the field
and replaces its value with typed `NOT_APPLICABLE`, which is forbidden absence
at that unconditionally required validator coordinate and therefore retains
`IMPLICIT_ABSENCE_FORBIDDEN`.

The historical v0.1.6/v0.2.6 fixture already contains the earlier 42-vector
predicate-observability correction and is immutable baseline evidence. The
v0.1.7/v0.2.7 fixture retains all 335 vectors and every ID, name, expected
outcome/code, failure coordinate/ID, successful projection, category,
operation, and quantity-context coordinate. Its only logical changes are the
ten conversion `inputs` below; zero vectors are added or removed:

| Vector ID | Exact prospective input |
|---|---|
| `i2-0149` | `[QTY_R,UNIT_A,UNIT_B,RULE_AB]` |
| `i2-0150` | `[QTY_D,UNIT_A,UNIT_B,RULE_AFFINE]` |
| `i2-0151` | `[QTY_R,UNIT_A,UNIT_B,RULE_AB,UNIT_C,RULE_BC]` |
| `i2-0152` | `[QTY_D,UNIT_A,UNIT_B,RULE_AFFINE,UNIT_C,RULE_BC_DEC]` |
| `i2-0153` | `[PATCH(QTY_R,[["replace","/resolution",RES_PENDING]]),UNIT_A,UNIT_B,RULE_AB]` |
| `i2-0154` | `[PATCH(QTY_R,[["replace","/unit_ref",R(63)]]),UNIT_A,UNIT_B,RULE_AB]` |
| `i2-0155` | `[QTY_R,UNIT_A,PATCH(UNIT_B,[["replace","/dimension_ref",R(63)]]),RULE_AB]` |
| `i2-0156` | `[QTY_R,UNIT_A,UNIT_B,PATCH(RULE_AB,[["replace","/source_unit_ref",R(63)]])]` |
| `i2-0157` | `[QTY0,UNIT_A,UNIT_B,RULE_AB]` |
| `i2-0158` | `[PATCH(QTY_R,[["replace","/unit_ref",R(5)]]),UNIT_B,UNIT_A,RULE_AB]` |

The displayed patch arrays use the exact transport grammar from specification
§21.8. Direct inputs dispatch as one four-argument call.
Each six-item composition input dispatches as
`(quantity,UNIT_A,UNIT_B,first_rule)` followed by
`(returned_quantity,UNIT_B,UNIT_C,second_rule)`. The adapter must use this
explicit unit chain and must not invent, infer, or resolve a unit.

All vectors change mechanically only through the two top-level v0.1.7/v0.2.7
authority-hash fields. The fixture's 214 failure IDs and all canonical
projections are re-derived and remain byte-for-byte unchanged as values.
`i2-0154` has quantity/source inequality with source/rule-source equality;
`i2-0156` has quantity/source equality with source/rule-source inequality.
A bijective opaque-ref renaming preserves these different role-equality
graphs, so their respective `UNIT_MISMATCH` and
`CONVERSION_RULE_MISMATCH` outcomes require no lookup, literal-value
privilege, fixture ID, patch history, or inferred ref contents.

Every validator-bound Block-5 through Block-8 candidate has all required
fields and signature-correct runtime members; the deliberately malformed
Block-7 constructor inputs remain constructor-bound formation tests. Semantic
closed-domain, cross-field, evidence, resolution, uncertainty, graph,
ancestry, lifecycle, and authorization defects survive formation and fail
only at their named validator interface.

The dual envelope boundary is mechanical: Block-7 cases whose operation is
`CommonObjectEnvelope` retain constructor-owned exact-byte/type/canonical
formation and unchanged I-1 failures. Structurally formed cases 14–16 and
18–19 whose operation is `validate_object_envelope` first construct normally
and then fail, if at all, only at the assigned validator predicate. Case 17's
malformed bytes instead fail the constructor prerequisite with their unchanged
I-1 identity; they are not relabelled as a validator failure. Hash mismatch
remains the last I-2 validator failure after direct stored-hash exclusion;
metadata/lifecycle variation remains
hash-invariant; and source-tree, independently parsed-tree, valid-byte-change,
and no-decoded-cache assertions remain separate. The fixture adapter
constructs declared records and a read-only policy provider only; it never
supplies a raw mapping as a record candidate or relabels an earlier failure.

The I-2 V11 audit is T0 source-text/AST inspection. It verifies the exact
127-entry root tuple and module subsets; nine-path manifest; 29 direct module
edges and acyclicity; the exact `envelopes` import subset
`CanonicalBytes,parse_ecj1`; absence of `encode_ecj1`, canonical internals,
registry/alias/object-graph/dynamic lookup and decoded caches; exact
failure-code set; no local
failure enum/string code; and no scientific/runner/finalizer/result/Gate/
package/network/subprocess/T1/T2/T3 reachability. The AST audit imports no
production module. It must report nonzero completed checks; skipped,
terminated, or zero-check work is not a pass.

### 21.6 Registry dependency, exclusions, and Gate preservation

I-2 implements only pure lifecycle and supersession validation.
`accept_registry_object` and `supersede_registry_object` belong to I-4, after
the required external authorization records and validator exist. I-2 cannot
fabricate authority, create a synthetic production acceptance result, mutate
a production object to accepted/superseded, or accept a numerical policy.
Draft registration and exact ref/alias resolution retain their I-1 semantics.
Those registry callables are never invoked by an I-2 validator. Policy/owner
lifecycle/kind/role/content, tolerance or violated-contract contents, region
membership/disjointness, global pending/effect completeness, treatment
adequacy, true contract violation, and alias/object-graph cycle freedom remain
UQ-40 later-stage claims.

I-2 contains no domain numerical policy, EBU quote rule, distortion, action,
transition, trajectory, controller, topology, equilibrium/homeostasis rule,
routing/settlement rule, parameter search/optimization, stochastic semantic,
or wave, interference, spectral, Taylor, Fibonacci-like, recursive, fractal,
or self-similar model. It authorizes no framework execution, policy callback,
scientific test, package/build/install operation, result, publication,
commit, push, merge, branch, tag, release, or PR.

The one roadmap remains: Framework I-1 through I-9; Part IV local measurement
and outcome discrimination; Part V long-run viability and homeostasis; Part
VI sequential and parallel actions; Part VII routes and infrastructure; Part
VIII topology, timing, waves, spectra, interaction hierarchies, recurrence,
hierarchy, and fractal hypotheses; then Part IX institutional application and
settlement. Future candidates are derived where possible from declared
mathematics, compared with simpler baselines, and tested against a
homeostasis-preservation gate. This context grants no scientific work.

Gate 1D-C remains exactly: one cumulative official runner invocation; no
receipt; no result directory; no model-state advance; scientific state
`UNSTARTED`. I-2 does not inspect, investigate, correct, retry, invoke,
finalize, reinterpret, or otherwise interact with it and never records its
cumulative invocation count as zero.

## 22. Normative prospective Framework I-3 implementation authority

### 22.1 Exact locks, precedence, and authorization boundary

The complete corrected prospective I-3 authority is locked by:

1. specification v0.1.9 raw SHA-256 `3eb023e4a729fe5205f4edf476d1347cc2584a99467648ce552c98954bd976e4`;
2. amendment v1.0.0 raw SHA-256 `a392874c473219df9a24d044dee7444327f347924438cd8a86627f69f79d3be2`;
3. mechanical contract v1.0.0 raw/canonical SHA-256 `505fcad67139bcf9c45d38a59c759f06d9e347e995d50c5ea8c3637ebe4cbcbb` / `3a56b15447ccedd39eb473f8e7838fbba6cbbb0f4d85a60c9b68d26ca5aa8f22`; and
4. validation contract v1.0.0 raw/canonical SHA-256 `0b1d0a2a39e0286ecdf02045838887dd342cd8977062e0e55673ae9437da59b0` / `88283fe2efda6c769688985805d3654d6deb5016195ea119f337b2fd843dd8ec`.

The plan does not contain its own whole-file hash. The amendment is the normative human rendering, the mechanical JSON is the schema/ordering source, and the validation JSON is the fully materialized vector source. Any mismatch fails closed. These sources do not change accepted I-1/I-2 bytes or scientific authority.

This plan remains documentation authority only. No implementation file, fixture, test, package, registry state, scientific state, result, Gate state, commit, push, or publication is authorized. A fresh independent review is required before any I-3A authorization.

### 22.2 Closed inventory and exact future path manifest

| Inventory | Exact value |
|---|---:|
| Retained types (historical + conservation) | 69 (55 + 14) |
| Validators / appended failures | 23 / 35 |
| Root prefix / suffix / total | 127 / 92 / 219 |
| Modules / direct acyclic imports | 15 / 91 |
| Future paths | 23 |
| Historical / separate deferred types | 25 / 8 |
| Fully materialized vectors | 544 |

| State | Exact path | Narrow future purpose |
|---|---|---|
| `MODIFIED` | `src/ebu_framework/__init__.py` | append exact I-3 root suffix after frozen 127-entry prefix |
| `MODIFIED` | `src/ebu_framework/errors.py` | append exact 35-code I-3 failure suffix only |
| `NEW` | `src/ebu_framework/state.py` | I-3A declarations and validators |
| `NEW` | `src/ebu_framework/conservation.py` | I-3A optional conservation declarations and validators |
| `NEW` | `src/ebu_framework/distortion.py` | I-3A distortion declaration only |
| `NEW` | `src/ebu_framework/actions.py` | I-3B action declarations |
| `NEW` | `src/ebu_framework/network.py` | I-3B static network and provisional-route declarations |
| `NEW` | `src/ebu_framework/commitments.py` | I-3B commitment, reservation, and capacity declarations |
| `NEW` | `src/ebu_framework/observation.py` | I-3B measurement declarations |
| `NEW` | `src/ebu_framework/scheduling.py` | I-3B schedule declarations |
| `NEW` | `src/ebu_framework/policy.py` | I-3C information and policy-memory declarations |
| `NEW` | `src/ebu_framework/causal.py` | I-3C causal-status and remainder declarations |
| `NEW` | `src/ebu_framework/settlement.py` | I-3C quote, receipt, share, residual, and closure declarations |
| `NEW` | `src/ebu_framework/ledger.py` | I-3C ledger declarations; no append behavior |
| `NEW` | `src/ebu_framework/faults.py` | I-3D base fault declarations and local boundary validator |
| `NEW` | `src/ebu_framework/experiment.py` | I-3D configuration and binding declaration shapes |
| `NEW` | `src/ebu_framework/artifacts.py` | I-3D generic artifact and manifest declaration shapes |
| `NEW` | `tests/framework/fixtures/i3_validation_v1.json` | exact externally reconstructed validation corpus |
| `NEW` | `tests/framework/test_i3a_declarations.py` | I-3A T0 validation |
| `NEW` | `tests/framework/test_i3b_declarations.py` | I-3B T0 validation |
| `NEW` | `tests/framework/test_i3c_declarations.py` | I-3C T0 validation |
| `NEW` | `tests/framework/test_i3d_declarations.py` | I-3D T0 validation |
| `NEW` | `tests/framework/test_i3_integration.py` | I-3E exports, imports, projections, failure precedence, collision freedom, and frozen-I2 audit |

No path in this table is created or modified by v0.2.9. In particular, the future fixture remains absent. The accepted 127-entry prefix remains locked by LF-joined SHA-256 `f5f49518ad67b3cbb0f8fb16c974a61dc64b90038b8149013f4846947675d0a3`; the suffix is the exact 69-type sequence followed by the 23 validators.

### 22.3 Exact implementation interfaces and precedence

| Interface | Exact positional-only signature | Exact first-failure precedence |
|---|---|---|
| `validate_state_record` | `(record: SystemState, projection_contract: ProjectionContract, predecessor_epoch: Epoch\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `PHYSICAL_POLICY_MEMORY_CONFLATION` → `STATE_PROJECTION_FAILURE` → `MISSING_COORDINATE` → `EPOCH_MISMATCH` → `HASH_MISMATCH` |
| `validate_projection_contract` | `(represented: RepresentedState, contract: ProjectionContract, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `STATE_PROJECTION_FAILURE` → `MISSING_COORDINATE` → `HASH_MISMATCH` |
| `validate_conservation_profile_selection` | `(selection: ConservationProfileSelection, /) -> None` | `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` |
| `validate_conservation_profile` | `(profile: ConservationProfile, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONSERVATION_PROFILE_INVALID` → `CONSERVATION_QUANTITY_DUPLICATE` → `CONSERVATION_COORDINATE_DUPLICATE` → `CONSERVATION_FLOW_CHANNEL_DUPLICATE` → `CONSERVATION_UNIT_MISMATCH` → `CONSERVATION_LEVEL_REQUIREMENT_MISSING` → `CONSERVATION_EVIDENCE_INCOMPLETE` → `CONSERVATION_ISOLATION_INVALID` → `CONSERVATION_TOLERANCE_UNDECLARED` → `HASH_MISMATCH` |
| `validate_distortion_model` | `(model: DistortionModel, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `DISTORTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_action_definition` | `(definition: ActionDefinition, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_action_instance` | `(instance: ActionInstance, route: RoutePlan\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `PROVISIONAL_ROUTE_REQUIRED` → `HASH_MISMATCH` |
| `validate_provider_network` | `(provider: Provider, network: ProviderNetwork, topology: TopologySnapshot, locus: CapacityLocus, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `HASH_MISMATCH` |
| `validate_route_plan` | `(route: RoutePlan, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_DUPLICATE_MEMBER` → `PROVISIONAL_ROUTE_REQUIRED` → `HASH_MISMATCH` |
| `validate_commitment` | `(record: Commitment, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_reservation` | `(record: Reservation, capacity: CapacityRecord, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `ACTION_DECLARATION_INVALID` → `CONSERVATION_UNIT_MISMATCH` → `RESERVATION_CAPACITY_MISMATCH` → `HASH_MISMATCH` |
| `validate_capacity_record` | `(record: CapacityRecord, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `CONSERVATION_UNIT_MISMATCH` → `ACTION_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_measurement` | `(measurement: Measurement, contract: MeasurementContract, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `EPOCH_MISMATCH` → `CONSERVATION_UNIT_MISMATCH` → `MEASUREMENT_CONTRACT_MISMATCH` → `HASH_MISMATCH` |
| `validate_schedule` | `(record: Schedule\|ComparatorSchedule\|CoordinationEventDeclaration, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INADMISSIBLE_SCHEDULE` → `MISSING_COMPARATOR` → `HASH_MISMATCH` |
| `validate_information_view` | `(contract: InformationContract, view: InformationView, read_set: InformationReadSet\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INFORMATION_VIEW_DECLARATION_INVALID` → `HASH_MISMATCH` |
| `validate_policy_memory_state` | `(record: PolicyMemoryState, mode: MemoryMode, predecessor_epoch: Epoch\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `POLICY_MEMORY_NOT_APPLICABLE` → `EPOCH_MISMATCH` → `HASH_MISMATCH` |
| `validate_causal_remainder` | `(record: CausalRemainder, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONSERVATION_UNIT_MISMATCH` → `CAUSAL_ATTRIBUTION_UNRESOLVED` → `HASH_MISMATCH` |
| `validate_settlement_closure` | `(closure: SettlementClosureRecord, quote: Quote, receipt: Receipt, group_receipt: GroupReceipt, child_actions: tuple[ChildActionRecord,...], residual: GroupResidual, shares: tuple[SettlementShare,...], causal_status: CausalIdentificationStatus, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `SETTLEMENT_LINK_INVALID` → `CONSERVATION_UNIT_MISMATCH` → `SETTLEMENT_CLOSURE_FAILURE` → `CAUSAL_ATTRIBUTION_UNRESOLVED` → `HASH_MISMATCH` |
| `validate_ledger` | `(ledger: Ledger, entries: tuple[LedgerEntry,...], /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `LEDGER_LINK_INVALID` → `HASH_MISMATCH` |
| `validate_fault_schedule_boundary` | `(schedule: FaultScheduleV1, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `FAULT_SCHEDULE_INVALID` → `HASH_MISMATCH` |
| `validate_experiment_configuration` | `(configuration: ExperimentConfiguration, fault_schedule: FaultScheduleV1\|Applicability, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `CONFIGURATION_INCOMPLETE` → `POLICY_MEMORY_NOT_APPLICABLE` → `FAULT_EXTENSION_UNAVAILABLE` → `HASH_MISMATCH` |
| `validate_execution_binding` | `(binding: ExecutionBinding, /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `EXECUTION_SEMANTICS_PROJECTION_FAILURE` → `HASH_MISMATCH` |
| `validate_execution_result_manifest` | `(manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], /) -> None` | `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `ARTIFACT_COMPLETENESS_INVALID` → `HASH_MISMATCH` |

There are exactly 145 validator/failure sites. The exact appended failure sequence is: `I3_RECORD_FORMATION_INVALID`, `I3_OBJECT_CONTENT_MISMATCH`, `I3_COLLECTION_ORDER_INVALID`, `I3_DUPLICATE_MEMBER`, `STATE_PROJECTION_FAILURE`, `MISSING_COORDINATE`, `POLICY_MEMORY_NOT_APPLICABLE`, `EPOCH_MISMATCH`, `CONSERVATION_PROFILE_INVALID`, `CONSERVATION_LEVEL_REQUIREMENT_MISSING`, `CONSERVATION_QUANTITY_DUPLICATE`, `CONSERVATION_COORDINATE_DUPLICATE`, `CONSERVATION_FLOW_CHANNEL_DUPLICATE`, `CONSERVATION_UNIT_MISMATCH`, `CONSERVATION_EVIDENCE_INCOMPLETE`, `CONSERVATION_ISOLATION_INVALID`, `CONSERVATION_TOLERANCE_UNDECLARED`, `PHYSICAL_POLICY_MEMORY_CONFLATION`, `DISTORTION_DECLARATION_INVALID`, `ACTION_DECLARATION_INVALID`, `RESERVATION_CAPACITY_MISMATCH`, `MEASUREMENT_CONTRACT_MISMATCH`, `INADMISSIBLE_SCHEDULE`, `MISSING_COMPARATOR`, `PROVISIONAL_ROUTE_REQUIRED`, `INFORMATION_VIEW_DECLARATION_INVALID`, `CAUSAL_ATTRIBUTION_UNRESOLVED`, `SETTLEMENT_LINK_INVALID`, `SETTLEMENT_CLOSURE_FAILURE`, `LEDGER_LINK_INVALID`, `FAULT_SCHEDULE_INVALID`, `FAULT_EXTENSION_UNAVAILABLE`, `CONFIGURATION_INCOMPLETE`, `EXECUTION_SEMANTICS_PROJECTION_FAILURE`, `ARTIFACT_COMPLETENESS_INVALID`.

Constructor formation checks exact fields, runtime types, tuple containers/members, enum/Literal arms, and strict `CanonicalBytes`. Cross-field, order, duplicate, applicability, projection, link, and hash defects remain formable for the named validator. Every validator inspects only complete supplied arguments and fresh local payload parses; no reference resolution, registry lookup, fixture-ID branch, or execution is permitted.

For `I3_OBJECT_CONTENT_MISMATCH`, implementation must traverse exact positional-signature order. A direct enveloped I-3 record is inspected at its argument position; members of an explicitly frozen ordered tuple/list-like record collection are inspected in canonical tuple order before the next argument. Enums, scalar witnesses, `Applicability`, primitive records, and non-enveloped values are skipped. Each stored payload is freshly parsed and compared byte-logically with its exact canonical projection excluding `envelope` and `derived_exclusions`; the earliest mismatch emits the code and stops precedence. The failure envelope names the validator, carries exactly that record's stored object ID/version/content hash, names the argument/member position in its summary, and receives a newly derived failure ID. Stored-hash recomputation remains the later `HASH_MISMATCH` predicate. Registry lookup, opaque-reference resolution, inferred content, patch history, and fixture identity are forbidden.

The exact mechanical scan inventory covers all 23 validators, including settlement `child_actions` and `shares`, ledger `entries`, and manifest `artifacts` member-by-member in canonical tuple order. Provider-network order is provider, network, topology, locus; information-view order is contract, view, applicable read set. The primitive conservation-profile selection has no enveloped record to scan. Formation negatives remain distinct `I3_RECORD_FORMATION_INVALID` outcomes with empty object refs because they fail before a valid supplied enveloped-record identity exists.

The corrected paired signatures provide direct local witnesses for state coordinates, predecessor epochs, routes, reservation/capacity, measurement/contract, information contract/view/read set, settlement closure graph, ledger entries, configuration/fault schedule, and manifest/artifacts. `POLICY_MEMORY_PROJECTION_FAILURE` and `POLICY_MEMORY_MISMATCH` are deferred to I-4/I-5.

Uncertainty tolerance is `ObjectRef|Applicability`; `NOT_APPLICABLE` reaches `CONSERVATION_TOLERANCE_UNDECLARED` and malformed `APPLICABLE` reaches `IMPLICIT_ABSENCE_FORBIDDEN`. Direct physical-payload reserved keys alone can reach `PHYSICAL_POLICY_MEMORY_CONFLATION`; opaque referenced targets are explicit nonclaims. Every collection and applicability arm has the exact owner listed in the mechanical contract.

### 22.4 Materialized corpus and external reconstruction

| Coverage | Exact count |
|---|---:|
| Formation positive / boundary / negative | 69 / 69 / 69 |
| Validator positive / boundary | 23 / 23 |
| Isolated validator sites / all isolated sites | 145 / 214 |
| Adjacent pairs / multiply-invalid validators | 122 / 23 |
| Object-content scan-order cases | 1 |
| **Total** | **544** |

The normative materialized vector array is 24104258 canonical bytes, ends in exactly one LF, and has SHA-256 `fbdaffc00e88b9f20a14b443d7f18f854f625413e4b11475088102f60600c01b`. Two independently written standard-library-only reconstructions agreed byte-for-byte on count, IDs, names, effective inputs, outcomes, bytes, newline, digest, failure-ID derivations, successful projections, object-content scan order/evidence, and collision audit. They found 543 unique effective inputs, one benign same-outcome collision for the one-member enum positive/boundary formation, and zero conflicting outcomes.

Every vector includes complete ordered arguments, exact recursive runtime descriptors, every full record payload, exact successful projection or failure, first failure, interface evidence, stage, and precedence evidence. Baseline/patch notation is non-normative. All 67 validator-level object-content outcomes identify their earliest mismatching record and have rederived failure envelopes and IDs. The six provider-network/information-view vectors identify `CapacityLocus`/`InformationReadSet` after their earlier arguments match. New vector `i3v-08-o01` has matching provider, mismatching network, matching topology, and mismatching locus, and selects the network as earliest. `APPLICABLE` with empty conservation `profile_refs` yields `IMPLICIT_ABSENCE_FORBIDDEN`; the distinct self-parent condition yields `CONSERVATION_PROFILE_INVALID`.

### 22.5 Staged implementation boundary and nonclaims

I-3A is state, conservation, and distortion; I-3B actions, network, commitments, observation, and scheduling; I-3C policy, causal, settlement, and ledger; I-3D faults, experiment, and artifacts; I-3E exports, fixture, projections, imports, and full T0 integration. All corrected authority must be accepted before I-3A starts.

Reduced/open accounts remain first-class, isolated completeness remains only a local declaration claim, and historical models require no migration. There is no universal zero residual or hidden tolerance. Residual computation is I-5, Bridge is I-6, Dynamic Coordination is I-7, and finalization/publication is I-8. None has begun.
