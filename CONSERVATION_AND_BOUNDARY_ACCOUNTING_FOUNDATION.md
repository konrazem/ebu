# Conservation and Boundary Accounting Foundation

**Version:** 0.1
**Status:** Conceptual and algebraic foundation; no experimental result
**Scope:** Historical D0, P1C, service, Gate 1D-C, and future Parts IV-IX
**Language:** English
**Purpose:** Separate reduced stock ledgers, open control-volume balances, and isolated physical conservation without changing any accepted EBU equation or result

---

## 1. Executive decision

The historical D0, P1C, service, Gate 1D-C, and related models are reduced or
open descriptions. They are not retroactively reclassified as isolated,
boundary-complete physical systems. Their explicit drive, transport, service,
correction, source, sink, and boundary terms are legitimate parts of a reduced
account when the represented stock and omitted surroundings are stated.

This decision is terminological and interpretive. It changes no historical
equation, parameter, execution, result, or evidence status. In particular:

1. the D0 and P1C represented-stock ledger remains valid;
2. D0 potential descent is not a theorem of physical energy conservation;
3. P1C reserve preservation is not a theorem of total energy conservation;
4. no completed or planned Gate is thereby shown to be isolated or physically
   complete; and
5. conservation of physical quantities is established science, not an EBU
   discovery or an empirical consequence of EBU accounting.

The governing distinction is:

> A balance can be exact inside a declared representation without that
> representation containing every physical carrier or every boundary flow.

Conversely, a physically complete isolated-system claim requires an explicit
boundary, compatible units, all relevant carriers, all conversions, and a
demonstration that no exchange crosses that boundary.

---

## 2. Authority and compatibility

This foundation is prospective documentation. It interprets, but does not
amend, the following established project layers:

- Part I's discrete local model and its explicit stock-loss ledger;
- `SEQUENTIAL_PARALLEL_BRIDGE.md` v0.2;
- `DYNAMIC_COORDINATION_FOUNDATION.md` v0.1;
- `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` v0.1;
- `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` v0.1; and
- the frozen scientific content and evidence status of Gate 1D-C.

Where a historical model names a transport loss, drive, regeneration, service,
or correction without representing its complete physical destination or
source, the model is read at Level 1 or Level 2 below. Nothing in this document
licenses a post-result parameter change, a reinterpretation of a registered
outcome, or a new execution.

The accepted framework I-2 core types remain accepted unchanged at
`351417c39fa26b9045e7c162a9897a7c38e4e1d1`, as integrated on
`framework-v0.1` at `ede89d8af6b89da491e03c352efcf1868a913f6f`.
This foundation creates only later planning responsibilities for I-3 and I-5.

---

## 3. Three accepted levels of account

| Level | Name | What must be represented | Permitted claim | Claim that is not permitted |
|---|---|---|---|---|
| 1 | Reduced represented-stock account | The selected stock coordinates and every term that changes those coordinates | The declared stock ledger closes, or its residual has a stated value | Total physical energy, mass, matter, charge, or another carrier is conserved by the represented model |
| 2 | Open control-volume balance | The selected coordinates, a declared system boundary, internal transformations, and all modeled exchange across that boundary | The typed open-system balance closes for the declared quantity and boundary | The control volume is isolated, or the inventory is physically complete, unless separately demonstrated |
| 3 | Isolated boundary-complete physical conservation | All relevant carrier coordinates and transformations inside a physically complete boundary, with zero external exchange | The declared physical quantity is conserved in the isolated model under the stated assumptions | Equilibrium, homeostasis, stability, efficiency, causality, or good settlement follows merely from conservation |

All three levels are first-class scientific descriptions. Level 1 is not a
defective Level 3 when it is used for a clearly scoped question. Level 2 is
often the correct description of an operating biological, ecological,
industrial, or service system. Level 3 is a stronger special case, not the
default interpretation.

### 3.1 Level 1: reduced represented-stock account

A Level 1 account asks whether the coordinates actually present in the model
change according to their declared update. A term called `transport_loss` can
be an accounted outflow from represented usable stock even when the downstream
heat, waste, dispersion, degradation, or surrounding reservoir is omitted.

The scientific requirements are:

- name the represented stock and its units;
- name every modeled source and outflow;
- state which destinations, reservoirs, and conversions are outside scope;
- do not call the account isolated or physically complete; and
- distinguish exact algebra from physical interpretation.

### 3.2 Level 2: open control-volume balance

A Level 2 account declares a boundary and separates internal transformation
from boundary exchange. Supply, export, service draw, environmental exchange,
and correction can be legitimate boundary terms. Closure means that the
declared inventory and declared exchanges agree. It does not mean that nothing
crossed the boundary.

### 3.3 Level 3: isolated boundary-complete physical conservation

A Level 3 claim is admissible only if the modeled system is isolated with
respect to the conserved quantity and the state includes all relevant physical
forms. A coordinate described only as useful stock, reserve, service capacity,
burden, or EBU is not automatically a complete physical carrier coordinate.

---

## 4. Typed balance law

Let

- \(y[k] \in \mathcal{Y}\) be the typed state at discrete time \(k\);
- \(J[k] \in \mathcal{J}\) be the vector of internal transformation or transfer
  amounts during the transition;
- \(\widetilde{S}\) be the typed internal incidence or stoichiometric map;
- \(\phi[k] \in \Phi\) be the vector of exchanges across the declared system
  boundary; and
- \(B\) be the typed boundary-incidence map.

The general one-transition account is

\[
y[k+1]-y[k]=\widetilde{S}J[k]+B\phi[k].
\]

The equation is meaningful only when each addition is type- and
unit-compatible. It does not authorize summing kilograms, joules, hours,
service events, and EBU into one scalar.

For a candidate conserved physical quantity \(q\), let \(c_q\) map the typed
state into units of \(q\). Internal transformations conserve \(q\) when

\[
c_q^{\mathsf T}\widetilde{S}=0.
\]

This is a left-nullspace condition on the declared internal transformation
map. It is not a statement that every state coordinate is conserved.

### 4.1 Balance residual with boundary exchange

Define the typed residual

\[
r_q[k]
=c_q^{\mathsf T}
\left(
y[k+1]-y[k]-\widetilde{S}J[k]-B\phi[k]
\right).
\]

When \(c_q^{\mathsf T}\widetilde{S}=0\), this reduces to

\[
r_q[k]
=c_q^{\mathsf T}\left(y[k+1]-y[k]\right)
-c_q^{\mathsf T}B\phi[k].
\]

Thus a zero residual means that the observed inventory change agrees with the
declared boundary exchange for the selected quantity, boundary, resolution,
and transition. It does not prove that every exchange was observed or that the
chosen state is physically complete.

### 4.2 Isolated special case

If the boundary is physically closed to quantity \(q\), then

\[
B\phi[k]=0,
\]

and a boundary-complete model satisfying the internal conservation condition
has

\[
c_q^{\mathsf T}\left(y[k+1]-y[k]\right)=0.
\]

The isolated equation is a special case of the open balance. It must not be
silently imposed on D0, P1C, service, Gate 1D-C, or future operating systems.

### 4.3 Residual tolerance

An exact symbolic account uses exact equality. A measured or floating-point
account may use a tolerance only when a named profile declares:

- the conserved quantity and units;
- the boundary and included coordinates;
- the measurement resolution and uncertainty model;
- the numerical representation;
- the absolute and, if needed, relative tolerance; and
- the failure action.

There is no universal zero-residual rule and no hidden global tolerance.

---

## 5. Historical D0 and P1C ledger

Let \(x_i\) be the represented stock at node \(i\), \(u_i\) the declared drive
rate, \(\Delta t\) the transition duration, and `transport_loss` the total
represented stock removed by inefficient transfer during that transition.
The accepted ledger is

\[
\Delta\sum_i x_i
=\Delta t\sum_i u_i-\mathrm{transport\_loss},
\]

where \(\Delta\sum_i x_i=\sum_i x_i[k+1]-\sum_i x_i[k]\).

This is an exact Level 1 account when its terms are computed from the accepted
update. It states that internal lossless transfers cancel in the node sum,
drive changes the represented stock, and transfer inefficiency removes stock
from the represented coordinates.

It does not state that physical energy has been destroyed. It also does not
state where the removed carrier goes unless the model includes the relevant
destination coordinate and conversion law.

### 5.1 Optional augmented loss coordinate

Let \(w\) be a typed lower-grade, waste, heat, dispersed-material, or other
destination coordinate compatible with the transported carrier, and let
\(L=\mathrm{transport\_loss}\). Under the explicit assumption that all of the
represented loss enters \(w\), an augmented account can use

\[
\Delta\sum_i x_i=\Delta t\sum_i u_i-L,
\qquad
\Delta w=L.
\]

Then

\[
\Delta\left(\sum_i x_i+w\right)=\Delta t\sum_i u_i.
\]

This augmentation is optional and domain-specific. A generic resource-stock
loss must not automatically be relabelled heat. Conversion factors,
coproducts, mass-energy distinctions, and units must be supplied by the domain.

### 5.2 Optional isolated regeneration extension

The historical drive term may represent regeneration entering the reduced
account. A future isolated extension may instead include an internal reservoir
\(z\). In the simplest same-carrier case,

\[
\Delta\sum_i x_i=G-L,
\qquad
\Delta z=-G,
\qquad
\Delta w=L,
\]

so that

\[
\Delta\left(\sum_i x_i+z+w\right)=0.
\]

This is a new optional model, not a reinterpretation of historical D0 or P1C.
If regeneration converts sunlight, chemical fuel, food, money, labour, or
another typed input, the state and conversion map must represent the actual
carriers rather than force them into the same scalar.

---

## 6. Service is not physical destruction

Service can consume or remove a modeled usable-stock coordinate without
destroying physical energy. For example, a battery may lose 1 kWh of stored
electrochemical availability while delivering a service and dispersing energy
as motion, sound, resistive heat, and environmental heat. A Level 1 service
model may record only the 1 kWh decrease and the delivered service event. A
Level 2 account adds the imported or exported boundary flows. A Level 3 energy
account would include every relevant energy form inside an isolated boundary.

The following are therefore distinct:

- useful-stock depletion;
- physical energy conversion and dispersion;
- service delivery;
- exergy destruction;
- EBU accounting; and
- institutional payment or settlement.

The number of service events is not generally a conserved physical quantity.
Exergy, unlike energy, can be destroyed by irreversible processes relative to
a declared environment. A useful-stock ledger can decrease even when total
energy in a larger isolated system is conserved.

---

## 7. Atomic joint transitions and parallel groups

For a parallel or overlapping group \(G\), conservation and boundary closure
must be evaluated on the complete atomic joint transition

\[
\Delta y_G=T_G(y_{\mathrm{before}})-y_{\mathrm{before}}.
\]

The group balance is

\[
\Delta y_G=\widetilde{S}_GJ_G+B_G\phi_G.
\]

The physical transition is counted once. Child effects evaluated from a shared
baseline must not be independently added to the state unless the accepted
joint transition defines that composition. A named sequential execution is a
comparator, not an alternative bookkeeping path that may be mixed into the
joint result.

A group receipt may contain child observations and actor lines, but its
physical residual belongs to the atomic before/after group transition.
Allocation among children is a separate causal or institutional question.

---

## 8. Hierarchical roll-up and internal cancellation

Suppose child regions \(A\) and \(B\) share an internal transfer \(F\), positive
from \(A\) to \(B\). Their open accounts contain

\[
\Delta y_A=I_A-F+E_A,
\qquad
\Delta y_B=I_B+F+E_B,
\]

where \(I_A,I_B\) are internal transformations and \(E_A,E_B\) are exchanges
with the parent boundary's exterior. At parent level,

\[
\Delta(y_A+y_B)=I_A+I_B+E_A+E_B.
\]

The child-to-child transfer cancels exactly once. It is visible in each child
account but is not an external input to the parent. A valid roll-up therefore
requires stable boundary identifiers, typed transfer identifiers, direction,
units, timestamps, and a rule preventing double counting.

This cancellation rule applies to spatial regions, organizations, supply-chain
tiers, product components, lifecycle stages, and temporal aggregations. It does
not imply that loss, conversion, delay, or storage between levels disappears.

---

## 9. Five ledgers that must remain separate

| Ledger | Question | Closure object | What closure does not establish |
|---|---|---|---|
| Physical conservation | Did a physical carrier balance across a declared boundary? | Typed state and boundary-flow residual | Homeostasis, efficiency, welfare, or causality |
| Represented-stock ledger | Did the selected model coordinates change according to their update? | Stock, drive, loss, service, and correction terms | Physical completeness or isolation |
| EBU accounting | Did the declared burden or potential account close under its definitions? | EBU quote, observed burden, potential difference, and stated residual | Conservation of mass or energy |
| Causal attribution | Which action caused which part of a joint observed change? | Identified contrasts under explicit causal assumptions | Physical conservation or a fair allocation |
| Institutional settlement | Who is charged, credited, compensated, guaranteed, or held responsible? | Contractual actor lines and settlement rules | A law of physics or uniquely correct causal shares |

One record may link all five ledgers, but no scalar should silently serve all
five roles. In particular, EBU, potential, useful stock, service, exergy, and
settlement value are not automatically conserved quantities.

---

## 10. Worked hand examples

These examples are algebraic checks, not simulations or empirical evidence.

### 10.1 Reduced two-node stock ledger

Two nodes begin with a total represented stock of 20 units. Drive adds 3 units
during the transition. A transfer moves 5 units from node 1, delivers 4, and
records 1 unit of transport loss. Then

\[
\Delta\sum_i x_i=3-1=2,
\]

so the final represented total is 22. The ledger closes. Without another
coordinate, the example says only that 1 unit left represented usable stock.

### 10.2 Augmented destination coordinate

Add a compatible waste coordinate \(w\) and assign the 1 lost unit to it. The
usable stock rises by 2 and \(w\) rises by 1, so the augmented inventory rises
by 3, equal to the external drive. The account is Level 2 unless the source of
the drive is also included internally.

### 10.3 Isolated reservoir extension

Add an internal source reservoir \(z\) that falls by 3 units during the same
transition. The usable stock rises by 2, waste rises by 1, and the reservoir
falls by 3. The augmented total changes by zero. This Level 3 conclusion holds
only under the same-carrier, complete-boundary assumptions.

### 10.4 Open service control volume

A service site begins with 8 stock units, receives 4 units across its boundary,
and uses 5 units to provide service. Its represented stock ends at 7:

\[
7-8=4-5=-1.
\]

The open balance closes. Neither the service count nor the one-unit inventory
decrease is a claim that physical energy vanished.

### 10.5 Parent roll-up

Region \(A\) exports 6 units to region \(B\); transmission records 1 unit in a
typed loss coordinate. At child level the transfer is a boundary crossing. At
the parent level the 5 units delivered to \(B\) and the matching outflow from
\(A\) are internal, while the loss remains as its represented destination or
declared outflow. Counting the import again at parent level would create a
hidden input.

---

## 11. Counterexamples to invalid inference

1. **Closed stock ledger, incomplete physics.** A fuel tank account can exactly
   record fuel use while omitting exhaust, heat, oxygen, and products. Exact
   ledger closure does not make it a complete mass or energy model.
2. **Conserved quantity, unstable dynamics.** A lossless two-state system can
   conserve a sum while deviations grow in opposite directions. Conservation
   alone does not prove Lyapunov stability.
3. **Stationary inventory, nonzero throughput.** Equal inflow and outflow can
   hold a stock constant in an open system. Zero state change does not prove
   isolation or equilibrium.
4. **Homeostasis with exchange.** A living system can regulate a state by
   continuously importing resources and exporting heat and waste. Homeostasis
   does not require isolation.
5. **Efficient service, nonzero exergy destruction.** Useful service can be
   delivered while energy is conserved and exergy is destroyed. Conservation
   does not establish efficiency.
6. **Perfect physical balance, unidentified cause.** A group transition can
   have zero physical residual while child contributions remain causally
   unidentified.
7. **Perfect physical balance, contested settlement.** A physical receipt can
   close while several incompatible payment or responsibility rules remain.
8. **Apparent topology improvement from a hidden budget.** A hub can outperform
   a line only because its source capacity, boundary, or omitted loss differs.
   That is not evidence for topology itself.

---

## 12. Part I terminology inventory

### 12.1 Source and method

The current Part I source reviewed for this inventory was
`EBP_Book_Part_I_Unified_Explanatory_Edition.pdf`, 296 PDF pages, raw SHA-256
`335ed5c6d3541d48a61438e213a8a1148eb196649da83392a4ba0741ce65a4ad`.
All pages yielded extractable text. Exact case-insensitive terms were counted
with alphabetic token boundaries, with whitespace normalized inside the
two-word term `transport loss`; page numbers below are one-based PDF pages and
therefore include front matter. Every occurrence was inspected in context.

### 12.2 Interpretive inventory

| Term | Exact occurrences | Existing Part I usage | Required v0.1 clarification |
|---|---:|---|---|
| conservation | 9 | Mostly explicit denials that receipt, potential, allocation, or EBU closure is stock, material, or energy conservation; also reference/TOC uses | Preserve. Add the three-level boundary account; do not soften the denials. |
| loss | 125 | Transport inefficiency, represented stock loss, service and reserve loss, information loss, numerical/optimization loss, and ordinary-language loss | Qualify physical carrier, represented coordinate, or informational/objective meaning. Never infer destruction from the bare word. |
| transport loss | 12 | The explicit D0/P1C outflow from represented stock | Preserve the equation. State its Level 1 meaning and make augmented waste/heat destinations optional. |
| dissipation | 38 | Primarily potential descent, gradient-flow interpretation, and comparison with physical dissipation | Preserve the mathematics. Keep the distinction between an engineering potential and total physical energy. |
| energy | 41 | Book title and domain examples, explicit warnings that \(V\) or EBU is not automatically physical energy, and bibliography entries | Preserve the warnings. Use `physical energy` only for a typed energy account with a boundary. |
| isolated | 3 | An isolated equilibrium, an isolated edge, and the ordinary verb `isolated`; no classification of D0/P1C as an isolated thermodynamic system | Add an explicit nonclaim rather than rewriting these occurrences. |
| closed | 31 | Closed cycles, closed-form expressions, fail-closed behavior, route closure, and a charge analogy; not a general physical-system classification | Reserve `closed system` or `isolated` for a declared boundary; keep algebraic and operational uses. |
| open | 29 | Open questions, problems, frontiers, epochs, intervals, and chains; not a general physical-system classification | Add `open control volume` as a new defined term without retroactively changing ordinary uses. |
| boundary | 84 | Accounting, model, information, viability, reserve, claim, loss, and scope boundaries | Preserve and type the boundary. A claim boundary is not a physical control surface. |
| drive | 161 | The declared natural or external state-change term in the discrete and continuous models | Treat as internal only when its reservoir and conversion are explicitly represented; otherwise it is a Level 1 term or Level 2 exchange. |
| regeneration | 43 | A stock-restoring process or future dynamical assumption | Do not treat it as creation ex nihilo. A Level 3 extension must debit an internal reservoir. |
| service | 97 | Delivered outcome, bounded demand channel, and model state/update term | Service may remove usable stock; it is not automatically a physical carrier or conserved quantity. |
| consumption | 1 | A single ordinary-language use in the drive discussion | Define future uses by the consumed coordinate and destination rather than implying physical annihilation. |
| sink | 0 | The exact term is absent | Introduce only as a typed boundary or destination role; never as an unexplained disappearance. |
| source | 308 | Physical sources, provider/source nodes, source budgets, source code, documentary sources, and references | Disambiguate physical source, graph source node, code source, and bibliographic source. A physical source is internal or external only relative to a boundary. |

The decisive existing passages are compatible with this foundation:

- PDF page 43 says to name every boundary crossing;
- PDF page 44 discusses processes and cells that need several coordinates;
- PDF page 54 gives the D0 stock-loss ledger;
- PDF page 64 says the engineering potential is not total energy, stock,
  welfare, price, or moral worth;
- PDF page 67 rejects the misconception that \(V\) is automatically energy;
- PDF page 174 (printed page 149) says receipt or potential closure resembles
  conservation without being stock, material, or energy conservation;
- PDF page 190 (printed page 165) says ownership does not create conservation;
- PDF page 246 says telescoping needs no conservation law; and
- PDF page 278 (printed page 253) says EBU is not automatically energy.

### 12.3 Complete occurrence-page index

Repeated occurrences on one page are shown in parentheses.

- **conservation:** 17, 18, 174(3), 190(3), 246
- **loss:** 3, 7(2), 9, 10(2), 15, 20, 27, 28, 29(4), 33, 35, 39, 42(2), 43(2), 45, 48, 49, 50, 51, 53(2), 54(4), 55, 57(2), 59(3), 60, 61(2), 67, 86, 87(2), 88, 89(5), 90, 91(2), 92, 93, 94, 95(2), 96(3), 98, 101, 105, 107, 122(2), 124, 132, 134, 153, 155, 156, 174, 176, 177, 185, 195, 196, 200, 201, 204, 205, 209, 211(3), 213, 214(4), 215(2), 216, 218(3), 224, 231(2), 247, 249, 258, 259, 260(2), 261(2), 262, 265, 267, 268(2), 270, 273(3), 275, 278, 281, 285, 287, 289
- **transport loss:** 29, 54(2), 59, 61, 90, 209, 211, 214, 218(2), 260
- **dissipation:** 10(2), 11, 29, 91, 95, 97(2), 98, 99(3), 100(2), 101(3), 102, 103(3), 104(3), 105(3), 107, 108, 110, 113(2), 114(2), 131, 273, 275, 293
- **energy:** 1(4), 2, 3(3), 26, 28, 32, 64, 67, 86, 91, 95, 98, 157, 174, 194, 195, 218, 224, 248, 278(3), 291, 293(9), 294, 295(3)
- **isolated:** 79, 112, 262
- **closed:** 11, 17(2), 30, 49, 59, 106, 139, 140, 145, 147(2), 150, 155, 175, 180, 181(4), 183(2), 184, 185(3), 186, 196, 275, 281, 291
- **open:** 4, 18, 24, 30, 81, 82, 110, 145, 147, 148, 155, 173, 183(2), 189, 191, 192, 199, 205, 251, 262, 269, 270, 272, 273, 275, 291(3)
- **boundary:** 2, 4, 6, 7, 9, 10, 12, 16, 30, 35, 39, 42, 43, 55(2), 64, 65(2), 70(3), 71(2), 75, 78, 79, 80, 81, 83(3), 84, 93(2), 94(2), 113, 120, 122(2), 123, 124, 126, 128, 135, 137, 142, 158, 163, 164, 165(4), 166, 171, 175, 185, 188, 191, 203, 219(3), 221(2), 223, 224(2), 226(3), 227, 237(2), 247, 259, 260, 262, 270, 280, 285, 286, 292
- **drive:** 7, 10, 12, 14, 16(2), 20, 30, 32, 34, 35, 43, 45, 51(4), 53(3), 54(2), 55(2), 56, 57(2), 58, 59, 60, 61(2), 78, 82(2), 85(2), 97(4), 98(2), 99(4), 101, 102(2), 103(3), 104(3), 105(2), 107(2), 108(2), 113, 114(2), 115, 117(2), 118(3), 119, 123(2), 125, 126(2), 127, 129(3), 132, 135, 140, 143, 146(6), 147, 149, 150, 151(2), 168, 169(2), 170(2), 172(2), 173(5), 174, 178, 179(2), 180, 182, 183(3), 184, 185(2), 215, 216, 217, 218, 221, 222, 224(2), 225, 233, 234, 239, 242(2), 245, 246(2), 249(2), 260, 264(3), 266, 269, 270, 272, 273, 274, 275(3), 281(2), 282, 283, 286(2), 289, 290, 291
- **regeneration:** 9(4), 14, 29, 43, 51(2), 60, 74, 76, 77(4), 78, 79(4), 81(2), 82(4), 83, 84, 85, 103, 124, 130, 135, 146(2), 147, 173, 183, 215, 217, 273, 286
- **service:** 7, 9, 10, 12, 16, 18, 24, 27, 34, 35, 44, 55(2), 60, 61(3), 67(2), 73(5), 74, 75, 79, 80, 85, 90, 96, 99, 110(2), 115, 119, 122(5), 124(5), 125(4), 127, 136(2), 140, 152, 156, 158(3), 171, 173, 175, 176, 182(2), 183(2), 184, 198, 200, 201, 204(2), 223, 259, 261, 272(2), 273, 274(4), 278, 281(2), 282, 284(3), 285, 287, 288, 290, 291, 293(2)
- **consumption:** 51
- **sink:** no exact occurrence
- **source:** 6(2), 9(2), 11, 12(3), 13, 22(2), 24, 27, 29(3), 32, 33, 35(3), 37(3), 39(2), 40, 41(4), 42, 44(3), 45(2), 47(2), 48(4), 54, 55(2), 58, 59, 60, 61, 73, 74, 76(2), 77(2), 78(3), 79, 80, 82(3), 83, 84, 85(2), 86, 87(2), 88, 89(3), 90(3), 92(4), 93(2), 94, 95, 102(2), 109, 111(3), 112, 113, 115, 116, 117(4), 118(5), 119(3), 120(5), 121(4), 122(4), 123(3), 124(2), 125(3), 126(6), 127, 128, 130, 132(2), 133(2), 135(3), 136, 137(2), 138(3), 139(2), 140(2), 143, 144, 145, 146(2), 147(3), 149, 152, 153(4), 155, 156, 157(3), 158, 159(2), 160(2), 168, 173, 176(2), 180, 182, 185, 187(4), 188(5), 189(2), 190, 191(5), 192, 196, 198, 202, 203(2), 204, 206, 207, 211(2), 213(3), 214, 215, 217(2), 218(2), 220(2), 223, 226, 228, 229, 230(2), 231, 232, 239, 244, 247, 249(2), 251(6), 252(6), 253(4), 254(4), 255(4), 256(4), 257(10), 258, 259(4), 260(3), 261, 262(5), 264(2), 274, 278(2), 283, 284, 286(2), 287(2), 289(2), 291, 293(4)

### 12.4 Part I correction plan

Part I needs a 16-24 page addendum or integrated revision. It should:

1. insert the three account levels and typed boundary notation;
2. retain the D0/P1C stock ledger verbatim in substance;
3. add the optional augmented loss and reservoir examples;
4. cross-reference the existing warnings that \(V\) and EBU are not physical
   energy;
5. distinguish service consumption from physical destruction;
6. add one roll-up example and one incomplete-boundary counterexample; and
7. state explicitly that no historical Gate is thereby recast as isolated or
   physically complete.

No Part I result figure or equation needs to be regenerated merely because of
this terminology correction.

---

## 13. Requirements for future comparative studies

Any topology, wave, hierarchy, fractal, Fibonacci, structural, routing,
coordination, product, lifecycle, or supply-network comparison must use:

1. a common declared outer boundary;
2. equal external input and service-demand budgets, or an explicit normalized
   comparison when exact equality is impossible;
3. the same initial stored resources and terminal accounting horizon;
4. all material boundary inflows and outflows;
5. all energy, useful-stock, waste, heat, delay, maintenance, and correction
   flows relevant to the stated claim;
6. explicit treatment of internal transfers so they cancel at roll-up;
7. a declared residual profile and observability limit; and
8. a falsifier for any apparent improvement caused by hidden input, omitted
   loss, different boundary placement, or incomplete terminal inventory.

No structure may be credited with an improvement that disappears when the
external budgets, omitted flows, or final stored inventories are equalized.
This discipline applies equally to an EBU-favoured structure and to every
comparator.

---

## 14. Framework planning implications

This section is planning only. It does not modify framework code or authorize a
new implementation stage.

### 14.1 I-2 remains unchanged

I-2 is accepted unchanged; its core types need no retroactive edit. Reduced
and open accounts can be expressed later through declared domain/profile
objects rather than by changing the type foundation.

### 14.2 Later I-3 profile

If separately authorized, I-3 may add an optional declared
boundary/conservation profile containing at least:

- profile identifier and version;
- account level;
- boundary identifier and hierarchy;
- quantity identifier and units;
- state coordinates included in \(c_q\);
- internal transformation map or declared invariant;
- boundary-flow channels and sign convention;
- observability status;
- exact or uncertainty-aware residual policy; and
- explicit nonclaims about isolation and completeness.

The profile must allow Level 1 and Level 2 accounts. It must not require every
domain to pretend to be Level 3.

### 14.3 Later I-5 validation

If separately authorized, I-5 may check residuals against each declared
profile. Validation must fail closed on missing units, unknown channels,
duplicate roll-up transfers, profile mismatch, or an undeclared tolerance. It
must not impose a universal zero residual, infer isolation from a small
residual, or use a hidden framework-wide tolerance.

### 14.4 Deferred documents

Any detailed changes to `SEQUENTIAL_PARALLEL_BRIDGE.md` or
`DYNAMIC_COORDINATION_FOUNDATION.md` belong to separate future documentation
stages. Their present equations remain valid. Future revisions should import
the atomic group balance and hierarchical cancellation rules without
reclassifying their models as isolated.

---

## 15. Assumptions and interpretation rules

1. Every balance has a declared spatial, organizational, temporal, and model
   boundary.
2. Every coordinate and flow has a type and unit.
3. Sign conventions are fixed before computing a residual.
4. Internal and external roles are relative to the chosen boundary.
5. A source at child level may be an internal transfer at parent level.
6. A sink is a modeled destination or boundary outflow, never a synonym for
   physical annihilation.
7. Loss means loss from a named coordinate or quality class unless a complete
   physical transformation is represented.
8. Boundary completeness is a claim requiring evidence, not a default.
9. Measurement closure is limited by observability and uncertainty.
10. Conservation does not identify causal responsibility or prescribe
    settlement.
11. Potential descent, reserve invariance, homeostasis, stability, attraction,
    and efficiency each require their own assumptions and proof or evidence.
12. Algebraic closure remains true only for the exact definitions and update
    order from which it was derived.

---

## 16. Falsifiers and fail-closed conditions

| Proposed claim | Falsifier or stop condition |
|---|---|
| A represented-stock ledger closes | Recomputed endpoint change differs from the declared drive, service, loss, and correction terms under exact arithmetic or the declared numerical profile |
| An open control-volume account is complete enough for its claim | A material boundary channel, stored carrier, conversion product, or terminal inventory relevant to the claim is omitted |
| Internal transformations conserve \(q\) | \(c_q^{\mathsf T}\widetilde{S}\neq0\) with compatible units |
| A model is isolated for \(q\) | Any nonzero or unobserved exchange of \(q\) crosses the declared boundary |
| A hierarchical roll-up closes | A child transfer lacks a matching counter-entry, is counted twice, or changes units without a conversion record |
| A parallel group closes | The group residual is constructed by double-applying child effects or by mixing the joint transition with a sequential comparator |
| A topology improves performance | The improvement disappears under a common boundary, equal external budgets, equal initial/terminal inventory accounting, and included losses |
| A conserved quantity establishes homeostasis or stability | A counterexample satisfies conservation while leaving the viable set or amplifying deviations |
| A physical receipt establishes causal shares | Multiple child allocations remain compatible with the same joint observation |
| A physical receipt determines settlement | Two admissible institutional rules produce different actor lines from the same physical history |

On any failed type, unit, boundary, provenance, or residual-profile check, the
stronger conservation claim must be refused. The model may still retain a
narrower Level 1 claim if that claim is independently valid and clearly stated.

---

## 17. Initial literature and antecedent map

This map positions the foundation; it is not a systematic review and supports
no novelty or priority claim.

| Topic | Established antecedent family | Use here | Limitation still requiring review |
|---|---|---|---|
| Physical conservation | Classical mechanics and thermodynamics; Noether's relation between symmetries and conservation laws | Treat conservation as established science and distinguish it from EBU | Domain-specific physical carriers and boundary completeness must still be justified |
| Control-volume balances | Reynolds transport theorem and continuum balance laws | Separate inventory change, internal transformation, and boundary exchange | The correct control surface and measurement model are domain-specific |
| Reaction and transformation invariants | Stoichiometric matrices and left-nullspace conservation relations | Motivate \(c_q^{\mathsf T}\widetilde{S}=0\) | Generic stock models need not possess a physical stoichiometry |
| Network cancellation | Kirchhoff node laws, Tellegen's theorem, network thermodynamics, and bond graphs | Explain internal-transfer cancellation and typed ports | Electrical analogies do not supply EBU constitutive laws |
| Dissipativity and storage | Willems dissipativity theory and port-Hamiltonian systems | Separate storage functions, supply rates, and interconnection | An EBU potential is not automatically physical stored energy |
| Energy quality | Non-equilibrium thermodynamics and exergy analysis | Separate energy conservation from useful-work potential and irreversibility | Exergy requires a declared reference environment |
| Material and lifecycle accounting | Material-flow analysis, life-cycle inventory, input-output accounting, and supply-network provenance | Motivate complete boundary inventories and multi-scale roll-up | Allocation, truncation, substitution, and data-quality conventions differ by method |
| Causal and institutional allocation | Causal inference, cooperative allocation, accounting, and settlement systems | Keep physical closure, causal attribution, and settlement distinct | No unique allocation follows from conservation alone |

The future literature checkpoint should verify primary editions, exact
definitions, and nearest antecedents for every manuscript claim. It should
include negative searches and failed correspondences, not only supportive
citations. Existing project limitations on originality remain unchanged.

---

## 18. Open problems

1. Which physical carriers, if any, should be represented in each EBU domain
   adapter rather than left as reduced stock?
2. How should partially observed boundary exchange produce an interval or
   probabilistic residual without hiding model error inside uncertainty?
3. Which conversion maps are sufficiently identified to augment transport loss
   with heat, waste, or lower-grade stock coordinates?
4. How should service stocks, service flows, useful work, and exergy be linked
   without conflating them?
5. How should nested boundaries and asynchronous child transitions be rolled up
   without duplicate or missing transfers?
6. What atomicity contract is required for overlapping groups with delayed
   measurements and provisional settlement?
7. Which conservation manifolds are invariant under the future Part V
   controller, and which homeostatic claims require additional regeneration,
   viability, and stability assumptions?
8. How can boundary completeness be falsified when some environmental channels
   are unmeasured?
9. What benchmark prevents topology, wave, hierarchy, fractal, or Fibonacci
   comparisons from benefiting through hidden input or missing loss?
10. Which parts of product and supply-network histories are physical balances,
    which are causal accounts, and which are institutional allocations?
11. What minimum receipt data permit a physical residual to be recomputed
    independently without exposing protected actor data?
12. When should a reduced account be preferred because a purported complete
    account would add unsupported assumptions rather than information?

---

## 19. Explicit nonclaims

This foundation does not claim that:

- D0, P1C, service, Gate 1D-C, or any other historical Gate is isolated or
  physically boundary-complete;
- the D0 potential is physical energy;
- P1C reserve preservation is total energy conservation;
- EBU, potential, useful stock, service, exergy, payment, or settlement value is
  automatically conserved;
- a zero represented-stock residual proves that all physical flows were
  observed;
- conservation proves equilibrium, homeostasis, viability, Lyapunov stability,
  attraction, efficiency, causal attribution, moral value, or good settlement;
- topology, waves, hierarchy, fractals, Fibonacci structure, or any named
  pattern improves outcomes;
- the typed balance notation is novel; or
- this document authorizes framework I-3, I-5, a Gate operation, a model run, or
  any scientific execution.

---

## 20. Acceptance checklist

The foundation is internally acceptable only if all of the following remain
true:

- [ ] the three account levels are stated without ranking reduced/open accounts
  as scientific failures;
- [ ] the typed balance includes internal transformations and boundary exchange;
- [ ] the conserved condition and residual use compatible units;
- [ ] the isolated case is explicitly special;
- [ ] the D0/P1C ledger and all historical results are unchanged;
- [ ] optional augmentations are labelled new domain models;
- [ ] service depletion is not described as physical energy destruction;
- [ ] joint transitions and roll-up cancellation are defined;
- [ ] physical, stock, EBU, causal, and settlement ledgers remain distinct;
- [ ] future structural comparisons share boundaries and external budgets;
- [ ] I-2 remains unchanged and I-3/I-5 remain separately authorized future
  work;
- [ ] no universal residual tolerance is introduced; and
- [ ] originality and literature limitations remain explicit.

---

## 21. Version history

### v0.1

- freezes the reduced/open interpretation of historical models;
- defines the three account levels and typed balance law;
- preserves the D0/P1C ledger while adding optional augmented accounts;
- distinguishes service, exergy, physical conservation, EBU, causality, and
  settlement;
- records atomic group and hierarchical roll-up rules;
- completes the Part I terminology inventory;
- establishes fair-boundary requirements for future structural studies; and
- records planning-only I-3 and I-5 responsibilities while accepting I-2
  unchanged.
