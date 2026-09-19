# Part I full-length revision contract

The author's latest request supersedes the compressed 18-chapter edition:
revise the original 296-page Part I, retain its explanatory depth and style,
update the introduction and Gaussian potential, remove obsolete Allee/band/
numerical-error-controller exposition from this edition. The author's later
clarification removed the 300-page minimum; the latest combined-volume brief
now sets a 200-page minimum for each current volume. Part I continues into
combined Part II; the forward series has eight parts, not nine. Clear,
descriptive explanation remains the standard; no page inflation or filler.

Original baseline: `/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_I_Unified_Explanatory_Edition.pdf`.
Starting HEAD: `05f3cb02d0c48e60de98342edfac9c36f2cecc6f`.
Original chapter text is extracted into `build/original_01.txt` through
`build/original_26.txt`. Original manuscript source was not recovered; this
revision reconstructs editable source with an explicit section disposition.
The original artifact and the 69-page candidate remain recoverable unchanged.

## Writing standard

Write complete patient textbook prose. Preserve the original named Ridge,
Vale and clinic teaching world, careful symbol introductions, step-by-step
calculations, common misconceptions, guided problems and practice answers.
Give each chapter the space its subject needs. There is no chapter word quota,
whole-manuscript word target or minimum page count. Retain the original
450x666 pt trim and approximately 11pt body for stylistic continuity, not to
manufacture length. Expand explanations where needed and cut needless repetition.

Use LaTeX. Chapter files start with `\chapter{Title}\label{ch:unique}`.
Use numbered `\section`, `\subsection` sparingly, `equation`, `align`,
`booktabs` tabular with wrapped p columns. No manual page breaks to hit quota.
Available environments: `intuitionbox` (one title argument), `lawbox` (one
title argument), `cautionbox` (one title argument), `workedbox` (one title
argument). Keep boxes short, ordinarily under 180 words. Long solutions use
normal text. `\X` gives the physical stock unit, `\E` gives EBU.
Cross-reference with `\ref{ch:...}`, never guessed chapter/page numbers.
References use `\cite{key}` and are shared at the end.

## Content and math

Fixed homogeneous lossless scalar; nonnegative stocks; fixed mass M;
compatible nonnegative x_i^*; fixed positive sigma_i; V_i=1/2((x_i-x_i^*)/
sigma_i)^2. Sigma is a declared physical scale, not automatically uncertainty.
mu_i=(x_i-x_i^*)/sigma_i^2. H=diag(1/sigma_i^2).
Finite source-side quantity q; delta=S q; rate j has q=dt j.
E=V(z)-V(z+delta)-C. Ideal lossless worked model C=0.
Exact quadratic: E=-mu(z)^T delta-1/2 delta^T H delta-C.
Transfer i->j: E=q(mu_i-mu_j)-q^2/2(1/sigma_i^2+1/sigma_j^2).
No implied optimizing selector or restoring dynamics.
Straight-path R_a=-mu(z)^T delta_a-1/2 delta_a^T H delta_G;
sum R=group field reduction. Declared attribution, no entitlement/fairness.
The main repeated fixture: z=(18,2), x*=(10,10), sigma=(2,2),
V=16; q=4 gives (14,6), V=4, E=12; q=8 gives (10,10), E=16;
q=16 gives (2,18), E=0. q=17 feasible if sufficient stock but E=-4.25.
An asymmetric reference, different scale, alternative graph, process cost,
two simultaneous actions or route must explicitly declare changed data.
Keep physics, value, permission, receipt attribution and institutions distinct.
Do not treat a Gaussian reference as observed distribution or equilibrium.
No Allee law, L/U/R hinge penalty, P1C controller or timestep-error certificate
in the new instructional core. They remain valid scoped historical subjects
in preserved Parts II/III. Measurement uncertainty as a real limitation may
still be discussed; 'remove errors' does not license claiming perfect data.
External forcing is before shared z; update physical and audit records, not
actor credit. Conditional telescoping is not a recovery theorem.

## Planned chapter sequence and labels

01 Why the physical question matters (motivation)
02 What money records and what it leaves open (money)
03 Scarcity, access and unequal exposure (scarcity)
04 Planetary pressures and conditional futures (planet)
05 From economic feedback to a research question (research)
06 Homeostasis and functional balance (homeostasis)
07 Equilibrium, reference and continuing life (equilibrium)
08 The physical question beneath an economic action (action)
09 Cells, nodes and edges (graph)
10 Quantities, boundaries and one physical change (conservation)
11 Declaring a reference and a scale (reference)
12 Homeostasis as a Gaussian landscape (potential)
13 From a marginal to an edge field (field)
14 Finite changes and curvature (finite)
15 Permission before value (permission)
16 The exact local signed EBU quote (quote)
17 From pre-action schedule to measured record (lifecycle)
18 Positive, zero and negative EBU in real needs (signs)
19 Local actions and exact global identities (locality)
20 Action receipts and closure (receipts)
21 Closed cycles, splitting and external change (cycles)
22 Several actors on one nonlinear field (groups)
23 Routes, resource accounts and learning (routes)
24 Studio: reading the Ridge-Vale state (studio-state)
25 Studio: draw the action before calculating it (studio-action)
26 Studio: build the Gaussian landscape (studio-potential)
27 Studio: from slope to finite field effect (studio-field)
28 Studio: compare actions without hiding a policy (studio-choice)
29 Studio: a medicine route in local epochs (studio-route)
30 Studio: several actors at one source (studio-group)
31 Studio: run the complete physical account (studio-account)
32 What is established and what comes next (claims)

Pure illustrative arithmetic only. No model imports, trajectories, scientific
tests, runtime changes, commits or pushes in this authoring work.
