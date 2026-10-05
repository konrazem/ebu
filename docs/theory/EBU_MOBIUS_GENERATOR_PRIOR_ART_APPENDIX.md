# EBU — Möbius–generator continuity prior-art appendix

Review date: 2026-10-05. Companion to the [S-MG theorem report](EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md).

```text
STATUS: NON-CONTROLLING THEORETICAL CANDIDATE
SCIENTIFIC AUTHORITY: UNCHANGED
IMPLEMENTATION / EXPERIMENTAL EXECUTION: NONE
NO NOVELTY CLAIM IS AUTHORISED BY THIS REPORT.
INDEPENDENT THEOREM AUDIT AND LITERATURE VERIFICATION: REQUIRED
```

## 1. Scope, method and source limitations

This review tested whether the proposed identities already occur in set-function theory,
cooperative games, pseudo-Boolean analysis, epistasis, functional ANOVA, log-linear models,
statistical mechanics, stochastic thermodynamics and nonlinear control. It used primary
papers, author manuscripts, publisher records and author textbooks. The mathematical
proofs in the companion report are independently written derivations; literature citations
establish antecedents and terminology, not a substitute for those proofs.

Search families included Möbius/set-function derivatives, Harsanyi dividends, multilinear
Boolean representations, discrete Taylor expansions, Shapley interactions, epistasis,
Sobol/ANOVA interactions, hierarchical log-linear models, Gibbs/energy decompositions,
cluster expansions, semigroups, detailed balance, local detailed balance, Faà di Bruno,
Volterra series, control-affine flows and Lie derivatives. Publication searches also covered
2025–2026 through the review date. Recent relevant results R22–R23 were verified at their
publisher pages. This is a targeted review, not an exhaustive bibliographic census.

**Access labels below matter.** “Selected full text” means the relevant definitions,
formulas or arguments were available and inspected, not that every page was read.
“Abstract/metadata” is not evidence of a complete original proof review. In particular,
the original Harsanyi chapters and the complete Darroch–Lauritzen–Speed paper were not
fully inspected. Their attribution is supported by primary bibliographic records; exact
set-function equivalences were checked directly against R3. The Jansma equation comparison
uses a precisely versioned author preprint because the publisher PDF was unavailable.

## 2. Jansma equation-level comparison

Jansma's 2025 paper is a direct antecedent for the energy/probability portion, alongside
older set-function and log-linear theory. Equation numbers here refer to
[arXiv:2404.14423v5](https://arxiv.org/pdf/2404.14423v5), posted 7 February 2025, with manuscript
front date 10 February 2025. Publication identity is independently verified as
[Physical Review Research **7**, 023016, 7 April 2025](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.7.023016).
Publisher pagination and equation numbering are not assumed identical.

Use the dictionary `𝓔(z)=G(z)=V(x_z)` for the paper's dimensionless energy and
`E_EBU(z)=G(0)−G(z)` for EBU. With `𝓔(z)=−Σ_T J_T z_T`, the nonempty coefficients obey
`m_EBU(T)=J_T`; with an energy expansion using a positive coefficient convention they
instead have the opposite sign. These statements follow by direct substitution. All sums
in this comparison use each unordered subset once. A sum over ordered pairs needs its
own factor convention.

| RESULT | JANSMA VERSION | EBU VERSION | MATHEMATICALLY SAME? | DIFFERENT ASSUMPTIONS? | EBU-SPECIFIC ADDITION? | NOVELTY STATUS |
|---|---|---|---|---|---|---|
| Inversion | Theorem 1, Eq. (9); Boolean signs Eq. (14) | Theorem A | Yes, on the Boolean lattice | Full admissible action cube is declared | Physical action/value meaning | Known |
| Recursive effects | Eqs. (18)–(20) | A1: contextual differences | Yes | Fixed action background | Registered context | Known |
| Energy coefficients | §III C.1, Eq. (41) | A2 and `m_E=−m_G` for nonempty sets | Yes after sign/basis translation | Energy coordinates versus action endpoints | Composite `V∘x` interpretation | Known/direct corollary |
| Canonical density | Eq. (42) | D: `p∝exp(−V)` | Yes | Independent physical scale and reference measure required here | E1a calibration discipline | Known physics |
| Log-probability inversion | Eqs. (44)–(45) | D1: `m_E=Δ_T log p(x_S)` | Yes algebraically | Endpoint densities need not be a binary joint law | Intervention semantics | Known/direct corollary |
| Pair product | Eq. (46) | `log(p_AB p_0/(p_A p_B))` | Yes | Other coordinates fixed at the declared reference | Action face specification | Known |
| Triple product | Eq. (47) | `log(p_ABC p_A p_B p_C/(p_AB p_AC p_BC p_0))` | Yes | Same density/measure on all eight endpoints | Action face specification | Known |
| Cooperative-game coefficients | §III E, Eqs. (64)–(65) | A2 Harsanyi dividends | Yes | Normalization and ledger interpretation are separate | No allocation supplied | Known |
| Moments/connected quantities | §III C.2, Eqs. (48)–(53) | Distinguished from D in §24.1 | Different object | Partition-of-moments construction versus pointwise log contrast | Prevents a false identification | Known distinction |

The table rules out claiming the energy inversion, Boltzmann conversion or pair/triple
products as EBU discoveries. It does not establish that EBU's entire physical and
institutional architecture appears in that paper, nor that absence from it proves novelty.
The sign convention here was checked directly from the energy and density definitions.

## 3. Set functions, cooperative games and pseudo-Boolean functions

The EBU table is exactly a pseudo-Boolean real function once its action protocol is fixed.
For `E(∅)=0`, its coefficients are exactly Harsanyi dividends. Rota supplies the incidence-
algebra framework; Harsanyi is the game-theoretic historical attribution. R3 directly
identifies the Möbius transform, dividends, multilinear coefficients and discrete derivatives:
Eqs. (1)–(2), (8)–(10), (19), (23). Owen's multilinear game extension and the classical
pseudo-Boolean literature are additional antecedents. [R1–R5, bibliography below.]

For clarity, the following comparison is derived from the definitions. If
`F(z)=Σ_R m(R)z_R`, then for disjoint `S,T`,

\[
\Delta_TF(S)=\sum_{R\subseteq S}m(T\cup R).
\]

Thus a context-dependent difference can contain larger anchored coefficients. A Shapley
interaction averages over contexts; it is generally not the one contrast at the empty
context. In the conventional Shapley interaction index and Banzhaf interaction index,
respectively,

\[
I_{Sh}(T)=\sum_{R\supseteq T}\frac{m(R)}{|R|-|T|+1},\qquad
I_B(T)=\sum_{R\supseteq T}2^{-|R\setminus T|}m(R).
\]

These identities are given in R3's representation tables. They can be verified by expanding
each monomial and integrating its derivative along the diagonal, or evaluating it at the
cube center. For the pure triple `F=z₁z₂z₃`, the anchored pair dividend is zero whereas
both displayed pair indices equal `1/2`. The order-two Shapley–Taylor allocation instead
assigns `1/3` to each pair for this unanimity function. That last value follows from the
order-two unanimity rule in R8; it redistributes a higher-order term into an order cap.
None of these numbers changes the underlying Möbius coefficient.

Accordingly, “discrete Taylor” in S-MG names the complete multilinear identity, with no
remainder. It does not rename Shapley–Taylor truncation or provide a payment allocation.
The degree ceiling and quadratic pair-only corollary follow immediately by affine
substitution and Boolean reduction of polynomial powers. Their EBU interpretation is useful,
but their proof mechanism is classical.

## 4. Epistasis, background choice and functional ANOVA

Reference-genotype epistasis applies successive mutation differences to a measured fitness
or phenotype landscape. The same subset-difference algebra applies to a registered-action
landscape. What changes scientifically is the intervention, response variable, background,
scale, admissibility and physical interpretation. A nonlinear transformation of the measured
phenotype generally changes the coefficients. Background-averaged epistasis/Walsh coordinates
are not automatically the reference-cell coefficients used here. Poelwijk, Krishna and
Ranganathan explicitly compare these formalisms. [R6.]

Functional ANOVA and Sobol decompositions additionally choose an input probability measure
and form centered, orthogonal components under independence. An anchored Boolean table
requires no such measure. To make the distinction concrete, let independent uniform
Bernoulli variables `Z₁,Z₂` and `F=Z₁Z₂`. Direct algebra gives

\[
F=\tfrac14+\tfrac12(Z_1-\tfrac12)+\tfrac12(Z_2-\tfrac12)
 +(Z_1-\tfrac12)(Z_2-\tfrac12).
\]

The anchored coefficient is `m_F({1,2})=1`. The ANOVA interaction is the centered random
function in the last term, whose variance is `1/16`; the total variance is `3/16`, so its
normalized Sobol interaction is `1/3`. Neither variance quantity equals the anchored
coefficient. This example is an elementary calculation here, not a quotation from Sobol.
Classical variance-based sensitivity is the relevant antecedent R7. Distributional choices
and the conditional/marginal feature-value construction also matter when comparing modern
additive explanations with Shapley values; see the primary result R21.

## 5. Log-linear, Gibbs, information and cluster comparisons

The probability formula in the report has two possible scientific readings. For a positive
binary joint law, it is a reference-cell log-linear interaction on a selected face. For
physical endpoint densities `p(x_S)`, it is a contrast of counterfactual/intervention states;
it supplies no joint law of actions without an additional construction. The former belongs
to classical contingency-table and hierarchical interaction theory (R9); the energy and
pointwise-log bridge is especially explicit in R10–R11.

The comparison must also specify the object being transformed:

| Construction | Input and operation | Relation to S-MG |
|---|---|---|
| Reference-cell log-linear parameter | Alternating pointwise log joint probabilities | Same algebra when the points really are cells of that law |
| EBU endpoint contrast | Alternating `log p(x_S)` | Main conditional density theorem; action law not assumed |
| Interaction information | Alternating marginal entropies | Different quantities and averaging |
| Multi-information | Sum of marginal entropies minus joint entropy | Nonnegative divergence, not an arbitrary signed endpoint contrast |
| Connected information | Successive maximum-entropy fits to marginal constraints | Different hierarchy; R12 |
| Cumulant / connected moment | Partition combinations of moments | Different poset and input; not obtained by relabeling the EBU contrast |
| Cluster/fragment energy increment | Inclusion-poset differences of specified cluster energies | Related Möbius architecture; physical subsystems and boundary definitions differ |

The selected literature does not support treating all uses of the word “interaction” as
one observable. Nor does a pairwise microscopic potential guarantee a pairwise potential
after eliminating hidden variables. The exact S-MG ceiling concerns its declared composite
and coordinates, not every coarse-graining of a physical model.

Lafuente–Cuesta (R20) uses Möbius functions for lattice cluster free-energy constructions.
Barker–Griebel–Hamaekers (R23), published in 2026, explicitly formulates energy fragmentation
through partially ordered sets and inclusion–exclusion. These provide further reasons not
to claim an energy-plus-Möbius connection as new. Neither citation establishes that fragment
energies are automatically EBU action values or that physical interaction determines actor
credit.

## 6. Generator and calculus antecedents

A declared controlled flow followed by a scalar observable is standard control theory.
Applying a finite Boolean contrast to that observable immediately yields the S-MG
Generator–Flow–Möbius theorem. Fliess's noncommutative causal functional expansions and
Sontag's Volterra/control treatment are direct background for the short-time Lie-word
calculation (R13–R14). The report uses finite-order differentiability and a proved remainder;
it does not infer convergence of a full Volterra, Lie or Baker–Campbell–Hausdorff series.

The higher chain rule is the classical set-partition formula (R15). Its groups of response
derivatives provide a useful coordinate-dependent explanation of physical interaction.
Repeated FTC, Taylor remainders and polynomial degree arguments are standard calculus;
R24 gives related divided-difference background, but univariate divided differences are
not identical to the multivariate Boolean contrasts proved here.

Likewise Markov semigroups and their observable generators are standard (R19). Stationarity,
reversibility and canonical density need separate hypotheses. The nonreversible Langevin
construction R18 directly preserves a target density while adding stationary current.
Local detailed balance and entropy flow require the physical reservoir and state model
(R16–R17). S-MG's entropy coefficient is then a linear transform of an already conditional
entrywise thermodynamic relation, not new entropy physics.

## 7. Recent coverage and novelty disposition

The 2026 Shapley-interaction paper R22 concerns approximation of context-averaged interaction
indices. It does not turn a capped or averaged index into the full anchored Möbius table.
The 2026 energy-fragmentation paper R23 supplies particularly relevant recent energy-poset
prior art. R10's 2025 publication is the closest single equation-level comparison for the
probability segment. R3 remains the strongest direct source for the finite set-function,
multilinear and derivative equivalences.

The report therefore classifies the core results as known standard results, known results
in different notation, direct corollaries, or known physics in EBU notation. A possible
**EBU synthesis** joins registered human-readable physical actions, joint valuation before
attribution, generator interfaces, independent thermodynamic `beta_bridge=1` testing,
cross-field denomination tests and historical accounts that are not repriced. The sources
inspected did not establish this full package as a single validated architecture. That is
a bounded observation about this review, not an originality claim or a finding of absence.
Cross-field stable denomination remains a separate scientific question.

Publication-level priority would require independent checking of the theorem package,
verification against the final publications, a broader dedicated search and external expert
review. No result here is labeled a newly discovered theorem on the strength of search
failure. The companion report's novelty matrix and unresolved-item register control the
scope of that statement.

## 8. Primary-source bibliography and access record

| ID | Primary source | Access and specific use |
|---|---|---|
| R1 | G.-C. Rota (1964), [On the Foundations of Combinatorial Theory. I. Theory of Möbius Functions](https://webhomes.maths.ed.ac.uk/~v1ranick/papers/rota1.pdf), *Z. Wahrscheinlichkeitstheorie* **2**, 340–368; DOI 10.1007/BF00531932 | Original scan, selected material; incidence-algebra antecedent |
| R2 | J. C. Harsanyi (1959), [A Bargaining Model for the Cooperative n-Person Game](https://www.degruyterbrill.com/document/doi/10.1515/9781400882168-019/html), *Contributions to the Theory of Games IV*; and (1963), [A Simplified Bargaining Model for the n-Person Cooperative Game](https://www.jstor.org/stable/2525487), *International Economic Review* **4**, 194–220 | Publisher/bibliographic records; complete original text not inspected. Attribution cross-checked through R3 and the author's [Nobel lecture bibliography](https://www.nobelprize.org/uploads/2018/06/harsanyi-lecture.pdf) |
| R3 | M. Grabisch, J.-L. Marichal and M. Roubens (2000), [Equivalent Representations of Set Functions](https://ikojadin.perso.univ-pau.fr/kappalab/pub/GraMarRouMOR2000.pdf), *Mathematics of Operations Research* **25**, 157–178; DOI 10.1287/moor.25.2.157.12225 | Selected full author manuscript, definitions, equations and representation tables |
| R4 | E. Boros and P. L. Hammer (2002), [Pseudo-Boolean Optimization](https://scholarship.libraries.rutgers.edu/esploro/outputs/conferenceProceeding/Pseudo-Boolean-optimization/991031665032004646), *Discrete Applied Mathematics* **123**, 155–225; DOI 10.1016/S0166-218X(01)00341-9. P. L. Hammer and S. Rudeanu (1968), [Boolean Methods in Operations Research and Related Areas](https://link.springer.com/book/10.1007/978-3-642-85823-9) | Institutional/publisher records and indexed preprint material; classical terminology/history, not a claim of complete book review |
| R5 | G. Owen (1972), [Multilinear Extensions of Games](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.18.5.64), *Management Science* **18**, 64–79 | Publisher abstract; multilinear game-extension antecedent |
| R6 | F. J. Poelwijk, V. Krishna and R. Ranganathan (2016), [The Context-Dependence of Mutations: A Linkage of Formalisms](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004771), *PLoS Computational Biology* **12**, e1004771 | Selected full text; reference and background-averaged epistasis |
| R7 | I. M. Sobol (1993), [Sensitivity Estimates for Nonlinear Mathematical Models](https://www.andreasaltelli.eu/file/repository/sobol1993.pdf), *Mathematical Modelling and Computational Experiments* **1**, 407–414; and (2001), [Global Sensitivity Indices for Nonlinear Mathematical Models and Their Monte Carlo Estimates](https://doi.org/10.1016/S0378-4754(00)00270-6), *Mathematics and Computers in Simulation* **55**, 271–280 | Scan/indexed primary text and abstract; access limited. No Monte Carlo procedure executed |
| R8 | M. Sundararajan, K. Dhamdhere and A. Agarwal (2020), [The Shapley Taylor Interaction Index](https://proceedings.mlr.press/v119/sundararajan20a.html), *PMLR* **119**, 9259–9268 | Selected full paper, §2 and proof appendix; index versus complete expansion |
| R9 | J. N. Darroch, S. L. Lauritzen and T. P. Speed (1980), [Markov Fields and Log-Linear Interaction Models for Contingency Tables](https://researchprofiles.ku.dk/da/publications/markov-fields-and-log-linear-interaction-models-for-contingency-t/), *Annals of Statistics* **8**, 522–539; DOI 10.1214/aos/1176345006 | Author-institution record/abstract; original complete text not inspected |
| R10 | A. Jansma (2025), [Mereological Approach to Higher-Order Structure in Complex Systems: From Macro to Micro with Möbius](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.7.023016), *Physical Review Research* **7**, 023016 | Publisher publication record and selected full [version 5 preprint](https://arxiv.org/pdf/2404.14423v5); equation-level comparison in §2 |
| R11 | A. Jansma (2023), [Higher-Order Interactions and Their Duals Reveal Synergy and Logical Dependence beyond Shannon-Information](https://arxiv.org/abs/2205.04440), *Entropy* **25**, 648; DOI 10.3390/e25040648 | Selected full author preprint; log-probability versus entropy constructions |
| R12 | E. Schneidman, S. Still, M. J. Berry II and W. Bialek (2003), [Network Information and Connected Correlations](https://arxiv.org/abs/physics/0307072), *Physical Review Letters* **91**, 238701; DOI 10.1103/PhysRevLett.91.238701 | Primary abstract/publication record; connected-information hierarchy |
| R13 | M. Fliess (1981), [Fonctionnelles causales non linéaires et indéterminées non commutatives](https://www.numdam.org/item/BSMF_1981__109__3_0/), *Bulletin de la Société Mathématique de France* **109**, 3–40 | Selected original text; noncommutative causal response series |
| R14 | E. D. Sontag (1998), [Mathematical Control Theory: Deterministic Finite Dimensional Systems](https://sontaglab.org/mct.html), 2nd ed., Springer | Selected author-hosted full book, §2.11 and Chapter 4; Volterra response and nonlinear control |
| R15 | M. Hardy (2006), [Combinatorics of Partial Derivatives](https://arxiv.org/pdf/math/0601149), *Electronic Journal of Combinatorics* **13**, R1; DOI 10.37236/1027 | Selected full text, Proposition 1, Example 1 and proof; set-partition chain rule |
| R16 | C. Maes (2021), [Local Detailed Balance](https://arxiv.org/pdf/2011.09200), *SciPost Physics Lecture Notes* **32** | Selected full author text; Eq. (10), reservoir/state-scope qualifications |
| R17 | U. Seifert (2012), [Stochastic Thermodynamics, Fluctuation Theorems and Molecular Machines](https://arxiv.org/abs/1205.4176), *Reports on Progress in Physics* **75**, 126001 | Selected full author review; heat and stochastic entropy conventions |
| R18 | A. B. Duncan, T. Lelièvre and G. A. Pavliotis (2016), [Variance Reduction Using Nonreversible Langevin Samplers](https://arxiv.org/html/1506.04934), *Journal of Statistical Physics* | Selected full author text, §1.3, Eqs. (6)–(8); invariant density with nonzero current |
| R19 | T. J. Sargent and J. Stachurski, [Continuous Time Markov Chains, Chapter 6: Semigroups and Generators](https://continuous-time-mcs.quantecon.org/generators.html) | Selected author online textbook, accessed 2026-10-05; finite matrix semigroups and generator scope |
| R20 | L. Lafuente and J. A. Cuesta (2005), [Cluster Density Functional Theory for Lattice Models Based on the Theory of Möbius Functions](https://salmorejo.uc3m.es/PDFs/JPA07461.pdf), *Journal of Physics A* **38**, 7461–7482 | Selected author-hosted paper and primary abstract; cluster/free-energy Möbius antecedent |
| R21 | S. Bordt and U. von Luxburg (2023), [From Shapley Values to Generalized Additive Models and back](https://proceedings.mlr.press/v206/bordt23a.html), *PMLR* **206**, 709–745 | Primary abstract; functional decomposition and explanation connection |
| R22 | P. Kolpaczki, F. Edelmann, M. Muschalik and E. Hüllermeier (2026), [Approximating Shapley Interactions with Marginal Contributions](https://link.springer.com/article/10.1007/s10994-026-07062-6), *Machine Learning* **115**, article 129, published 19 May 2026 | Selected publisher full text, abstract and Definitions 1–2; recent interaction-index work |
| R23 | J. Barker, M. Griebel and J. Hamaekers (2026), [On Multilevel Energy-Based Fragmentation Methods](https://onlinelibrary.wiley.com/doi/full/10.1002/qua.70128), *International Journal of Quantum Chemistry* **126**, e70128, published 29 January 2026 | Selected publisher full text, §2.3, Theorem 2.1 and Eqs. (12)–(13), (23); energy-poset antecedent |
| R24 | C. de Boor (2005), [Divided Differences](https://pages.cs.wisc.edu/~deboor/sat/papers/2/), *Surveys in Approximation Theory* **1**, 46–69 | Author journal page and selected preprint; classical finite-difference calculus context, not an identity of all difference conventions |

## 9. Checks still required before publication or Book 1 integration

The independent audit should check all signs, reference choices, physical scope and
remainder hypotheses in the main report, and verify this appendix against final publisher
versions where only author manuscripts or records were accessible. It should also verify
original historical attribution where this review used a later primary mathematical source.
No source-access limitation prevents the elementary proofs supplied here, but it does limit
what can responsibly be claimed about priority or complete literature coverage.

This appendix changes no authority, study target, execution gate or institutional allocation.
