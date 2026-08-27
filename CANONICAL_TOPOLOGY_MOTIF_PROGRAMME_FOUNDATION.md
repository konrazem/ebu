# Canonical Topology / Motif Programme Foundation

**Status:** Prospective documentation authority; unimplemented; unexecuted; unaudited
**Version:** 1.0.0
**Accepted predecessor branch:** framework-v0.1
**Accepted predecessor commit:** 72183037b00930a766f0f0f613d8689bdfd82e8e
**Accepted predecessor tree:** 74ca6cc46b77bc1c13a3b1d2e736e0a56f246188
**Scope:** Canonical layered topology identity, recursive-motif theorem authority, future Stage A declaration design, future Stage B research boundary, future Stage C refusal, and book replacement instructions

This package is prospective authority only. It does not implement framework
behavior, materialize a fixture, infer a topology, execute a transition,
calculate scientific EBU, run a benchmark, create an atlas, populate a cache,
edit a manuscript or PDF, or publish a result. The companion JSON contracts
are the mechanical source for schemas, ordering, vectors, paths, and stage
boundaries. A disagreement between this document and either JSON contract is
an integrity failure requiring refusal.

## 1. Decision and programme headline

The programme adopts one limited and positive result:

> A theorem-backed example showing how structured recursive systems can avoid
> exhaustive primitive-subset recomputation.

The result is conditional. It does not say that arbitrary action families have
polynomial interaction tables, that Fibonacci structure is universal, that a
visually repeated shape is scientifically equivalent, or that a structural
identity predicts EBU performance. The compression mechanism is the declared
and proved combination of topology, equivalence, factorization, sufficient
boundary summaries, and complete correction/invalidation rules.

The programme also adopts a positive impossibility result for arbitrary
black-box subset values. That result explains why the declared structure is
necessary rather than decorative.

## 2. Claim classes and precedence

Every programme claim has one of these classes:

| Code | Meaning |
|---|---|
| AM | Accepted mathematics: proved here or imported with its assumptions |
| EA | Accepted architecture: repository responsibility or preservation rule |
| EI | Accepted implementation fact at the predecessor coordinate |
| CT | Conditional theorem: exact conclusion only under named assumptions |
| FO | Finite observation: exact enumeration or fixture fact, not a universal law |
| IC | Institutional choice: frozen programme or implementation boundary |
| PA | Prospective architecture: authorized design, not implementation |
| EH | Empirical hypothesis: requires a future preregistered execution |
| FT | Future theorem or evidence obligation |

Accepted Atomic Generator and Atomic Interaction authority retains precedence
over the meaning of generators, histories, subsets, interactions, factors,
causality, settlement, and physical topology. The accepted Framework I-4 and
I-5 packages retain precedence over authorization, capabilities, records,
events, trace, durability, and provenance. Sequential–Parallel Bridge v0.2
retains precedence over I-6. This package adds canonical structural identity
and recursive-motif authority; it changes none of those meanings.

The excluded electrical-voltage, physical-wave, phase-interference, and
superposition concepts remain excluded. No formula, chapter, validation
vector, prospective path, or later-stage reservation in this package restores
them.

## 3. Canonical layered topology

### 3.1 Object and layer responsibilities

**[PA]** A finite declared topology is

\[
\Theta=(P,\mathcal C,\mathcal O,\mathcal H,\mathcal B).
\]

The layers have distinct meanings:

- \(P\) records prerequisites and admissible configurations;
- \(\mathcal C\) records shared-factor incidence;
- \(\mathcal O\) records precedence, concurrency, and accepted commutation
  evidence;
- \(\mathcal H\) records structural pair and higher-order support and typed
  references to frozen interaction declarations; and
- \(\mathcal B\) records parent, port, boundary, and dependency structure.

These layers must not be collapsed into one untyped graph. A relation moved
between layers changes the structural object even if its endpoints look the
same. Structural interaction support is not a measured coefficient, physical
transport edge, causal allocation, settlement relation, or institutional
authority.

Local vertex names are the only values eligible for permutation. Semantic
types, roles, units, schema versions, referenced object versions, factor
kinds, ordered child roles, boundary-port meanings, and protocol digests are
colors and remain fixed.

### 3.2 Versioned serialization

**[IC]** Canonical topology schema version 1 is named
CANONICAL_TOPOLOGY_SCHEMA_V1. Its serializer is
CANONICAL_TOPOLOGY_SERIALIZE_V1. Serialization is a prefix-free, injective
encoding of the normalized layered declaration over ECJ-1-compatible values.

The mechanical contract freezes every field as ordered or unordered:

- unordered semantic sets are duplicate-free and sorted by their canonical
  bytes;
- mappings use recursive Unicode code-point key order;
- histories, precedence paths, ordered composition children, and ordered
  child roles retain declared order;
- text is NFC UTF-8;
- numbers are integers only;
- booleans and null remain distinct from integers and text;
- non-finite and floating-point values are forbidden; and
- a schema or identity domain/version is part of the preimage and cannot be
  inferred from payload shape.

Unknown fields, dangling vertex references, duplicate vertices or relations,
illegal self-relations, cycles in a declared strict-order relation,
layer/type mismatches, malformed versions, duplicate members of unordered
sets, and noncanonical stored bytes are rejected. A validator does not repair,
guess, coerce, or infer intent.

### 3.3 Canonical minimum and supported bound

For \(n\) permutable vertices and permutation group \(S_n\), define

\[
\boxed{\operatorname{Can}_v(\Theta)
=\min_{\pi\in S_n}\operatorname{Serialize}_v(\pi\Theta)}
\]

using lexicographic byte order.

**[IC]** Version 1 supports exhaustive canonicalization for exactly
\(0\le n\le8\). The algorithm enumerates all \(n!\) permutations in
lexicographic permutation order, serializes each color- and layer-preserving
relabeling, and selects the lexicographically least byte string. It may
deduplicate equal candidate bytes but may not stop early on a heuristic.
For \(n>8\), it must return the typed failure
CANONICAL_TOPOLOGY_SIZE_UNSUPPORTED. It must not emit a heuristic identity.
The value 8 is a frozen implementation safety bound, not a mathematical
scalability claim.

The topology identity preimage is

\[
\text{domain}\parallel\text{version}\parallel
\text{byte-length}\parallel\operatorname{Can}_v(\Theta),
\]

with exact domains and length encoding frozen mechanically. Its digest assumes
only collision resistance. A dedicated CanonicalTopologyId is required;
generic object-content hashing alone does not prove relabel invariance.

### 3.4 Invariance and characterization

**[AM] Relabeling invariance.** For every \(\sigma\in S_n\),

\[
\operatorname{Can}_v(\sigma\Theta)
=\operatorname{Can}_v(\Theta).
\]

Proof: the candidate set for \(\sigma\Theta\) is
\(\{\operatorname{Serialize}_v(\pi\sigma\Theta):\pi\in S_n\}\), which is the
same set as for \(\Theta\) because right multiplication by \(\sigma\) is a
bijection of \(S_n\). Equal finite candidate sets have the same minimum.

**[CT] Isomorphism characterization.** If Serialize_v is faithful over the
normalized colored layered schema, then

\[
\operatorname{Can}_v(\Theta)=\operatorname{Can}_v(\Theta')
\quad\Longleftrightarrow\quad
\Theta\cong_v\Theta'
\]

for color- and layer-preserving isomorphism. The forward implication composes
the inverse of one minimizing permutation with the other; the reverse
implication is relabeling invariance. Faithful encoding is an explicit
precondition, not an assumption supplied by a digest.

**[EA] Identity/performance separation.** Canonical equivalence states that
two declarations are the same structural object under allowed relabeling.
It says nothing about measured EBU, feasibility, service, robustness,
interaction sign, causality, fairness, or social value. Performance belongs
only to a separately frozen benchmark protocol and result.

### 3.5 Finite catalogue observations

**[FO]** Read-only standard-library enumeration at the controlling review
coordinate generated every strict labeled relation, filtered irreflexive and
transitive relations, and quotiented under every vertex permutation. It found:

| Vertex count | Labeled posets | Unlabeled posets |
|---:|---:|---:|
| 2 | 3 | 2 |
| 3 | 19 | 5 |
| 4 | 219 | 16 |

The two-action representatives are the antichain and one chain. The five
three-action representatives are the antichain, one comparable pair plus an
isolated action, the three-chain, a one-minimum/two-maxima fork, and its order
dual.

**[FO]** Quotienting the three possible pair-support edges under \(S_3\) gives
four unweighted pair-support classes. Crossing these with absence or presence
of the one triple hyperedge gives exactly \(4\times2=8\) unweighted
three-action interaction-support topologies.

These are finite observations for the stated schemas. They are not measured
domain topologies, canonical motif catalogue authority, or performance
results. Independent block, sequential chain, prerequisite fork, reconvergent
fork, order-sensitive fork, shared-constraint fork, join, pure higher-order
hyperedge, recursively encapsulated parent, active topology switch, and
Fibonacci recursive composite remain proposed research labels until their
exact typed definitions receive separate authority.

## 4. Recursive motifs and exact counting

### 4.1 Definition and occurrence count

Let \(M_0\) and \(M_1\) be immutable, version-addressed base motif
definitions. Let \(C\) be an immutable ordered composition rule whose first
and second child roles remain distinct. Define

\[
\boxed{M_{n+1}=C(M_n,M_{n-1})}\qquad(n\ge1).
\]

An occurrence is a leaf occurrence in the expanded composition tree; repeated
definitions retain distinct occurrence identities. With
\(N(M_0)=N(M_1)=1\),

\[
N(M_{n+1})=N(M_n)+N(M_{n-1}).
\]

Using \(F_1=F_2=1\), induction gives

\[
\boxed{N(M_n)=F_{n+1}}.
\]

**[AM]** This is an exact count for this declared ordered substitution family.
It is not a universal law of networks, EBU, cooperation, biology, geometry,
or growth. Visual resemblance is not evidence of the recurrence.

### 4.2 Conditional boundary compression

For each motif \(M_n\), let \(B_n=B(M_n)\) be a certified boundary summary.
Under A1–A8 below, the summary recurrence is

\[
\boxed{B_{n+1}=\Phi(B_n,B_{n-1})}.
\]

After the two bases, computing all summaries through level \(n\) requires
exactly \(n-1\) new applications of \(\Phi\). If each summary has uniformly
bounded size and each composition has uniformly bounded cost, the work is
\(O(n)\), while the expanded occurrence count is \(F_{n+1}\).

More generally, if summary size \(s_k=O(k^d)\) and
\(\Phi\) costs \(O((s_k+s_{k-1})^p)\), then

\[
\boxed{T(n)=O(n^{dp+1})},
\]

subject to the output-size lower bound and all A1–A8 obligations. If a summary
or composition cost grows polynomially in \(F_{n+1}\), no exponential-in-level
compression follows.

### 4.3 A1–A8 certificate

All eight conditions are jointly required:

| ID | Required declaration and proof |
|---|---|
| A1 identity | Every motif definition, instance, ordered child role, topology schema, boundary protocol, and composition rule is immutable and version-addressed. |
| A2 sufficiency | \(B_n\) answers every declared external query over the frozen initial augmented state, boundary, horizon, and admissible external history. |
| A3 complete composition | \(\Phi\) preserves carrier and unit declarations, conversion and loss, reserves, commitments, queues, delays, memory, modes, burden and process accounts, receipts, residuals, and settlement-visible content required by the query domain. |
| A4 closure | No undeclared cross-boundary factor, constraint, hyperedge, observation, or dependency reaches hidden internals; every crossing relation is exposed in the signature. |
| A5 interaction preservation | Reused interaction evidence includes the complete exposed subset protocol, removal semantics, outcomes, and the Atomic F16 all-subset equality obligation. |
| A6 cache-key completeness | Any future key separates topology, motif and occurrence, boundary and state versions, initial/history digest, horizon, numerical policy, composition version, evidence, and provenance. Performance is never identity. |
| A7 dependency completeness | The dependency DAG includes aliases, occurrences, parents, evidence, corrections, and invalidation edges. |
| A8 history-wide equivalence | Reuse is justified by complete history-wide boundary equivalence, never a snapshot, endpoint, local commutator, or visual resemblance. |

Missing any one condition invalidates the compression certificate and requires
expanded evaluation or fail-closed refusal under a separately authorized
protocol. The theorem is conditional; the presence checklist is structurally
testable, while scientific sufficiency for a real query family is not inferred
by Stage A.

## 5. Interaction corrections and locality

For a finite Boolean subset domain over action set \(A\), with explicit
empty-baseline value \(E(\varnothing)\), the F13-authoritative raw Boolean
Möbius coefficient is, for every \(S\subseteq A\), including the empty set,

\[
\boxed{I_{\mathrm{raw}}(S)=
\sum_{T\subseteq S}(-1)^{|S|-|T|}E(T)},
\qquad
I_{\mathrm{raw}}(\varnothing)=E(\varnothing).
\]

No argument in this authority assumes \(E(\varnothing)=0\). If one raw subset
value at any \(Q\subseteq A\), including \(Q=\varnothing\), is corrected by
\(\delta\) while every other raw entry is held fixed, then for every
\(S\subseteq A\), including \(S=\varnothing\),

\[
\boxed{\Delta I_{\mathrm{raw}}(S)=
\begin{cases}
(-1)^{|S|-|Q|}\delta,&Q\subseteq S,\\
0,&Q\nsubseteq S.
\end{cases}}
\]

**[AM]** This is algebraic correction locality on the Boolean lattice:
raw coefficient changes occupy the upward cone of \(Q\). In the exceptional
empty-to-empty case the exponent is zero, so changing only
\(E(\varnothing)\) by \(\delta\) changes
\(I_{\mathrm{raw}}(\varnothing)\) by \(\delta\).

Normalization remains available without replacing the raw F13 coefficient.
Define

\[
\widetilde E(S)=E(S)-E(\varnothing),
\qquad I_{\mathrm{norm}}(\varnothing):=0,
\]

and, only for nonempty \(S\),

\[
I_{\mathrm{norm}}(S)=
\sum_{T\subseteq S}(-1)^{|S|-|T|}\widetilde E(T).
\]

For every nonempty \(S\), the alternating subset sum is zero, and therefore

\[
\begin{aligned}
I_{\mathrm{norm}}(S)
&=I_{\mathrm{raw}}(S)
-E(\varnothing)\sum_{T\subseteq S}(-1)^{|S|-|T|}\\
&=I_{\mathrm{raw}}(S)-E(\varnothing)(1-1)^{|S|}\\
&=I_{\mathrm{raw}}(S).
\end{aligned}
\]

Consequently, changing any raw \(E(Q)\) by \(\delta\) gives the same
upward-cone delta for \(I_{\mathrm{norm}}(S)\) at every nonempty \(S\), even
when \(Q=\varnothing\). In that baseline-correction case both nonempty
transforms change by \((-1)^{|S|}\delta\), while the explicit convention
\(I_{\mathrm{norm}}(\varnothing)=0\) remains unchanged. This normalized
empty-set convention is distinct from the raw F13 identity
\(I_{\mathrm{raw}}(\varnothing)=E(\varnothing)\).

Two exact nonzero-baseline examples make the distinction visible. For
\(A=\{a,b\}\), let

\[
E(\varnothing)=5,\quad E(a)=8,\quad E(b)=9,\quad E(ab)=15.
\]

Then the raw coefficients are \((5,3,4,3)\) in the order
\((\varnothing,a,b,ab)\), whereas the normalized coefficients are
\((0,3,4,3)\). For \(A=\{a,b,c\}\), let every proper-subset value equal
\(5\) and let \(E(abc)=11\). Then
\(I_{\mathrm{raw}}(\varnothing)=5\), every nonempty coefficient below order
three is zero, and
\(I_{\mathrm{raw}}(abc)=I_{\mathrm{norm}}(abc)=6\): a pure three-way term
with a visible nonzero baseline.

These identities do not by themselves authorize cache reuse. Changed boundary
evidence, aliases, feasibility, removal semantics, history, horizon, or
scientific meaning may require wider revalidation even where the algebraic
coefficient delta is zero.

For infeasible subset families, no Boolean value may be silently invented.
A future feasible-poset calculus must declare its domain and incidence algebra
before using a poset Möbius transform.

## 6. Recursive surplus

For a separately frozen common protocol, define

\[
R_n=E(M_n)-E(\varnothing)
\]

and

\[
\boxed{J_n=R_{n+1}-R_n-R_{n-1}}.
\]

Under common boundary, units, initial augmented state, history, removal,
feasibility, preservation, resolver, loss, process-account, commitment, and
settlement semantics, \(J_n>0\) is a positive same-protocol recursive surplus,
\(J_n<0\) is a negative same-protocol recursive surplus, and \(J_n=0\) is
same-protocol structural additivity for that comparison. None of these signs
is preregistered or observed here. \(J_n\) is an empirical quantity, not part
of canonical identity and not implied by the Fibonacci occurrence count.

## 7. Six distinct compression concepts

The following concepts must never be conflated:

| Concept | Exact role | What it does not establish |
|---|---|---|
| Canonical equivalence | Quotients declared colored layered structures by allowed relabeling | Equal scientific performance or boundary equivalence |
| Feasible-poset restriction | Removes undefined subsets under an explicitly declared feasible incidence domain | Values for missing subsets or Boolean reconstruction |
| Proven sparse hypergraph support | Restricts possible structural interaction support under a proof/evidence rule | Coefficient sign, value, causality, or physical propagation |
| Structural additivity | Factorizes independent blocks when every independence, history, boundary, constraint, and account condition is proved | Recursive boundary sufficiency |
| Recursive boundary compression | Reuses sufficient summaries through \(\Phi\) under A1–A8 | Answers to undeclared cross-boundary queries |
| Correction locality | Identifies the algebraic upward cone affected by a subset correction | Operational cache validity outside complete dependency and alias authority |

## 8. Arbitrary black-box lower bound

**[AM] Query lower bound.** Let \(E:2^A\to\mathbb R\) be an otherwise
arbitrary black-box table on \(N=|A|\) actions, and write its raw Boolean
Möbius transform as

\[
I_{\mathrm{raw}}(S)=
\sum_{T\subseteq S}(-1)^{|S|-|T|}E(T).
\]

Any deterministic exact procedure that makes fewer than \(2^N\) subset
queries leaves some \(Q\subseteq A\) unqueried. Construct \(E'\) to equal
\(E\) on every queried subset and to set \(E'(Q)=E(Q)+\delta\) for nonzero
\(\delta\). The complete observed transcript is identical, but for every
\(S\supseteq Q\),

\[
I'_{\mathrm{raw}}(S)-I_{\mathrm{raw}}(S)
=(-1)^{|S|-|Q|}\delta.
\]

Thus at least one—and in fact every—Möbius coefficient in the upward cone of
\(Q\) differs. No exact reconstruction of the full arbitrary table or all its
Möbius coefficients is possible with fewer than \(2^N\) subset queries.
Randomization cannot give an exact worst-case guarantee without querying the
hidden entry.

This lower bound is positive programme guidance: any legitimate compression
must declare the non-black-box assumptions that supply information—topology,
equivalence, feasibility, factorization, sufficient boundaries, or another
proved restriction. An attractive motif picture is not such information.

## 9. Domain responsibility and positive cycle

Providers, institutions, and scientific domain authorities declare and
measure meaningful prerequisite, factor, order, interaction, boundary,
physical, causal, and institutional relations. EBU does not discover their
meaning from generic data. EBU’s responsibility is limited to typed
declarations, completeness claims, versions, provenance, consistency, frozen
protocol use, and fail-closed validation.

Consequently, topology identification is not a universal EBU open problem.
Each real domain owns the evidence that its topology represents the intended
system.

A permitted positive research cycle is:

\[
\boxed{\text{declare}\to\text{measure EBU}\to\text{refine}\to
\text{measure again}\to\text{certified recursive structure}}.
\]

The cycle can make cooperation, shared-factor use, synergy, redundancy, and
recursive reuse testable and auditable. It does not prove causality, fairness,
universal benefit, social sufficiency, entitlement, or a governance rule.

## 10. Prospective framework declarations

The mechanical contract freezes these inert shapes:

- LayeredTopologyDeclaration;
- CanonicalTopologyWitness;
- RecursiveMotifDeclaration;
- CertifiedBoundarySummaryDeclaration;
- TopologyBenchmarkDeclaration; and
- TopologyBenchmarkResult.

The last two are declaration/result envelope shapes only; Stage A may validate
their static field and reference form but may not create a scientific result
or compute one. Every declaration refers to accepted objects rather than
copying or reinterpreting mutable scientific payloads.

### 10.1 Stage A — declarations and canonical identity only

A later, separately authorized Stage A implementation may:

- create inert declaration types and pure validators;
- implement version 1 exhaustive canonicalization for \(0\le n\le8\);
- implement the topology-specific deterministic identity;
- materialize static conformance fixtures; and
- test relabeling invariance, unordered-input invariance, ordered-child
  sensitivity, layer separation, version separation, malformed input refusal,
  and identity/performance separation.

It may not infer topology, call a transition or model step, calculate EBU,
optimize, benchmark, cache scientific results, materialize a result, create a
research atlas, import a framework runner, or perform a scientific execution.

The exact prospective Stage A production and test paths are:

- new src/ebu_framework/topology.py;
- new tests/framework/fixtures/canonical_topology_v1.json;
- new tests/framework/test_canonical_topology.py;
- tightly scoped future edits to src/ebu_framework/identity.py,
  src/ebu_framework/hashing.py, src/ebu_framework/errors.py, and
  src/ebu_framework/__init__.py.

Compatibility validation must explicitly include:

- tests/framework/test_primitives_envelopes.py;
- tests/framework/test_i3_integration.py;
- tests/framework/test_i3a_declarations.py;
- tests/framework/test_i3b_declarations.py;
- tests/framework/test_i3c_declarations.py;
- tests/framework/test_i3d_declarations.py;
- tests/framework/test_atomic_declarations.py; and
- tests/framework/test_interaction_declarations.py.

These paths are prospective only. This package creates or changes none of
them.

### 10.2 Stage B — production-independent research

A separate Stage B authority may create a production-independent
research/topology/ area. Its allowed future scope is:

- full and compressed finite computations;
- strict enumeration;
- Fibonacci, Lucas, chain, tree, balanced, random-recursive, and
  perturbed-substitution controls;
- boundary-sufficiency negative controls;
- correction and invalidation experiments; and
- a versioned, nonnormative research atlas.

Stage B requires a separate frozen benchmark protocol, JSON plan, execution
authority, result authority, and publication authority. This package creates
no protocol, result, figure, dataset, benchmark output, or atlas.

### 10.3 Stage C — runtime reuse refused

No committed runtime-cache path is named or reserved. Stage C remains
unavailable until theorem authority fixes:

- sufficient summaries for concrete query families;
- exact query domains;
- dependency and alias closure;
- correction and invalidation semantics;
- history-wide boundary equivalence;
- interaction preservation;
- performance and output-size obligations;
- audit evidence; and
- durability, recovery, correction, and publication mechanics.

No later implementation may infer a Stage C path from this foundation.

## 11. I-6 noninterference

Sequential–Parallel Bridge v0.2 and the accepted I-6 adapter remain exact and
unchanged. Canonical topology is neither a prerequisite nor a blocker for I-6.
This package adds no I-6 type, validator, failure code, path, fixture, test,
benchmark, Fibonacci primitive, topology inference, cache behavior, or
scientific requirement.

A later Stage B protocol may use separately authorized I-6 evidence as an
input reference. It may not reinterpret or expand I-6, and the existence of
I-6 evidence does not authorize a topology benchmark.

## 12. Book replacement authority

This is a replacement and consolidation plan, not additive manuscript scope.
It creates no manuscript or PDF and does not change verified historical
results. The preserved explanatory spine is

\[
V\to\mu=\nabla V\to f_e\to\Psi_e\to J_e\to G_T\to
\text{finite EBU}.
\]

### 12.1 Parts I–III

No standalone topology chapter is added to current Parts I–III.

- Part I Chapter 16 is replaced/consolidated as the shared-source and parallel
  action explanation. Overlapping Chapter 24 practice is merged into it.
- Part I Chapter 17 retains route and Bellman reasoning, removes Fermat and
  wave material, and substitutes dependency-DAG and recursive-reuse intuition.
- Part I Chapter 26 is synchronized with these replacements.
- Part II Chapter 37 is replaced by atomic and parallel interaction calculus:
  nonzero empty baseline, Boolean Möbius coefficients, hyperedges, shared
  factors, commutators, structural versus active topology, and recursive
  boundary equivalence.
- Part II Chapter 42 retains route and dynamic-programming treatment and
  removes wave material.
- Part II Chapter 43 uses history-wide equivalence, not snapshot or endpoint
  equivalence.
- Part III preserves the D0–O14 historical record. Chapter 47 is regenerated
  against accepted D1, D2, I-3C, I-4, and I-5. Chapter 51 is updated for
  lifecycle, institutional share, causality, residual, and settlement
  separation. Chapter 62 replaces the obsolete O3/O5/framework roadmap.

### 12.2 Future books and appendix

The smallest complete main teaching unit is **Canonical Motifs, Topology
Benchmarks, and Recursive Reuse**, placed principally in future Part VI after
the sequential–parallel and higher-order foundations. It teaches canonical
equivalence, the five layers, identity/performance separation, recursive
encapsulation, exact Fibonacci counting, A1–A8 compression, recursive surplus,
correction locality, the black-box lower bound, and negative controls.

The mathematical proofs appendix contains:

- canonical/isomorphism proofs;
- finite poset enumeration;
- Boolean and prospective feasible-poset Möbius proofs;
- recursive compression and explicit size/cost bounds;
- dependency invalidation and upward-cone proofs;
- the arbitrary-table lower bound; and
- negative controls.

Future Part VIII receives only a short cross-reference for active topology and
geometry. It does not own a competing topology programme. The atlas is a
separate versioned nonnormative research companion, not a normative chapter or
source.

Fibonacci is the first exact recursive worked family. It is never called
universal and is never inferred from visual similarity. Voltage, wave, phase,
superposition, and physical-wave language remain excluded.

### 12.3 Feature-teaching record

Every major feature must teach, in accessible language:

1. the practical problem;
2. the capability the feature adds;
3. one life-facing example;
4. the defining equation or proof;
5. its connection to the preserved explanatory spine;
6. its declaration and evidence requirements; and
7. an adjacent limit or falsifier.

Capabilities remain prominent; limits are adjacent rather than deferred.

## 13. Open questions after this authority

Only these topology/motif programme questions remain open:

1. scalable canonical labeling beyond the frozen exhaustive \(n\le8\) bound;
2. feasible-poset calculus for declared domains;
3. boundary-summary sufficiency for concrete query families;
4. correction, alias, and cache-invalidation authority;
5. empirical recursive surplus \(J_n\); and
6. controlled Fibonacci, substitution, and geometric comparisons.

The canonical proof, Fibonacci occurrence-count induction, raw Boolean Möbius
locality including the empty-set case, conditional A1–A8 theorem, arbitrary
black-box lower bound, and provider/domain responsibility are not open
questions. Their assumptions and
future empirical applications remain visible without reopening the results.

## 14. Nonclaims and stop conditions

This package makes no claim that:

- canonical structure measures EBU performance;
- structural support is active, causal, physical, or institutional topology;
- Fibonacci recurrence is universal;
- A1–A8 holds for any real domain;
- arbitrary subset evaluation is compressed;
- an unqueried subset may be imputed;
- a boundary summary is sufficient merely because it has the right shape;
- cooperation is always beneficial, fair, causal, or socially sufficient;
- any runtime cache is safe or authorized;
- a large-\(n\) heuristic identity is acceptable;
- a Stage B protocol or execution exists;
- I-6 is changed or blocked;
- a book or atlas has been generated; or
- any model state or scientific experiment has executed.

Any failure of source identity, schema agreement, strict JSON parsing,
projection reconstruction, UTF-8/LF rules, path scope, predecessor
reconstruction, or Stage A–C separation requires fail-closed refusal.

## 15. Completion

The next possible stage is independent audit of exactly this ten-path
authority package. It is not begun by this package. Implementation, benchmark
design, execution, result interpretation, book generation, atlas generation,
and publication remain separate authorization boundaries.

CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION_COMPLETE
