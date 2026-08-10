# EBU Future Books Structure and Revision Register

Status: Living planning document  
Created: 2026-08-10  
Purpose: Preserve new EBU concepts and place them in the future book structure before they are lost or diluted across conversations.

## 1. How to use this file

This file is a structural and conceptual register, not a finished manuscript and not a replacement for the existing EBU books.

It should be updated whenever a new principle, equation, distinction, example, chapter, or unresolved question is developed. Each item should be marked as one of the following:

- **Established** — already defined in the books or project.
- **Confirmed addition** — accepted for a future revision but not yet integrated into the manuscript.
- **Open question** — important, but not yet settled.
- **Editorial task** — requires reconciliation with existing chapters, terminology, equations, or proofs.

The complete current tables of contents must eventually be copied here from the authoritative Part I–III manuscripts. Until that reconciliation is performed, this file deliberately avoids inventing titles for missing or unseen material.

## 2. Current high-level book map

### Existing manuscripts

- **Part I** — Existing manuscript. Exact chapter structure to be imported from the authoritative source.
- **Part II** — Existing manuscript. Exact chapter structure to be imported from the authoritative source.
- **Part III** — Existing manuscript. Exact chapter structure to be imported from the authoritative source.

Known existing reference:

- Chapter 1.6, **The Map of Laws We Will Build**, introduces ten laws. Its definitions and numbering must be preserved when the master structure is reconciled.

### Future or not-yet-reconciled manuscripts

- **Parts IV–VI** — Structure not available in the present working context. Do not invent or renumber them here.
- **Part VII** — Confirmed major addition concerning pre-action EBU valuation, binding quotes, failed actions, institutional responsibility, measurement residuals, reserves, the system-as-organism analogy, initiative, enterprise, and the possibility that motivations and preferences change under a different institutional system.

## 3. Confirmed conceptual distinctions to preserve across all books

### 3.1 Ledger

The ledger is the persistent memory of state transitions, obligations, transfers, errors, and settlements. It is not merely a list of payments. It allows the system to remember what was predicted, what was authorized, what occurred, what remained unresolved, and who ultimately bears each balance.

### 3.2 Pre-action EBU quote

Before an action, the system observes the current local state and derives an EBU value for the specified action:

\[
Q_t = F(S_t,a_t)
\]

where:

- \(S_t\) is the observable local system state;
- \(a_t\) is the precisely specified proposed action;
- \(Q_t\) is the quoted EBU consequence offered to the actor.

The quote is calculated before the action. It is the system's actionable statement about the transition it expects and is prepared to guarantee under stated conditions.

### 3.3 EBU record, receipt, and settlement

The theoretical EBU receipt should not be confused with a technical execution marker used by an experiment runner.

The preferred theoretical model is one evolving EBU record:

1. **QUOTED** — created before the action from the current local state.
2. **ACCEPTED** — accepted by the actor under explicit conditions.
3. **IN_PROGRESS** — the specified action has begun.
4. **SETTLED** — the action and its observed consequences have been evaluated.
5. **FAILED** — the specified action did not complete.
6. **PARTIAL** — only part of the specified transition occurred.
7. **UNRESOLVED** — the system cannot yet determine the actual outcome safely.

The pre-action record contains the quoted value. The post-action receipt settles the same record using the newly observed state. The quote is not erased or silently rewritten after the outcome is known.

### 3.4 Physical accounting versus responsibility

Two questions must always remain separate:

1. What physically happened in the system?
2. Which actor or institution is responsible for the resulting balance?

A refund or guaranteed payment changes who bears the cost. It does not erase energy, material, time, information, infrastructure use, or dissipation that physically occurred.

### 3.5 Binding quote principle

Once an actor truthfully accepts a valid quote and performs the specified action within its declared conditions, the quoted EBU settlement is binding for that actor.

The actor must not face an unlimited retroactive charge merely because the institution misunderstood its own system. Without this rule, participation becomes a gamble: the actor cannot know the consequence of acting until after the action is irreversible.

### 3.6 Measurement residual

After the action, the system measures the actual local transition:

\[
A_t = G(S_t,a_t,S_{t+1})
\]

The measurement or model residual is:

\[
\varepsilon_t = A_t-Q_t
\]

The residual is not hidden and does not retroactively replace the accepted actor quote. It is entered visibly in the ledger and assigned according to the responsibility rules defined in Part VII.

### 3.7 Earning EBU, initiative, and ownership

EBU must not be described as a system in which a person cannot earn EBU by creating something useful. If an actor creates and operates a restaurant that contributes positively to the local system, the relevant work may generate EBU.

The unresolved question is not whether initiative may be rewarded. It is how to distinguish and value several different contributions that are combined in today's concept of profit:

- discovering an unmet local need;
- designing and establishing the restaurant;
- supplying capital, tools, or a location;
- accepting a declared and bounded project risk;
- coordinating people and resources;
- cooking, serving, cleaning, maintaining, and administering;
- creating nourishment, pleasure, hospitality, safety, culture, and community;
- learning and improving the service over time;
- consuming energy, materials, land, labor capacity, and ecological capacity;
- receiving an ownership return after active contribution has ended.

EBU may reward verified contribution, initiative, innovation, responsibility, and continuing service without assuming that ownership alone creates an unlimited permanent claim on future value. The correct duration, scale, and distribution of founder rewards remain open theoretical questions.

The restaurant's system contribution is not identical to its revenue or customer demand. A preliminary decomposition is:

\[
V_{\mathrm{restaurant}}
=
B_{\mathrm{nutrition}}
+B_{\mathrm{hospitality}}
+B_{\mathrm{community}}
+B_{\mathrm{learning}}
-C_{\mathrm{resources}}
-C_{\mathrm{labor\ burden}}
-C_{\mathrm{ecology}}
-C_{\mathrm{externalities}}
\]

This is a conceptual decomposition, not yet an authoritative EBU equation. It must be reconciled with the established formalism before publication.

The total system contribution must also be kept separate from the settlement of each participant. Founder, workers, suppliers, customers, the issuing institution, and the ecological reserve may each have distinct quotes, receipts, and balances.

### 3.8 Preferences are partly produced by the system

The books must not assume that preferences observed under today's monetary, employment, ownership, advertising, scarcity, and status systems will remain fixed under EBU.

People adapt to the incentives, risks, recognition systems, and opportunities around them. If ecological restoration, care, prevention, maintenance, knowledge creation, or community work becomes visible and reliably rewarded, people may learn to value and pursue those activities differently. Work for the planet may become a source of EBU, competence, identity, status, and genuine satisfaction rather than an underfunded sacrifice.

This does not justify assuming that everyone will become altruistic. EBU must remain workable for people with mixed motives, including care, curiosity, autonomy, security, recognition, enjoyment, ambition, and personal benefit. The theory should treat motivation as adaptive and plural rather than reducing it either to profit maximization or to perfect altruism.

## 4. Part VII — The Binding EBU Quote and Institutional Self-Knowledge

Status: **Confirmed addition**

Working title alternatives:

- **The Binding EBU Quote: Risk, Failure, and Institutional Responsibility**
- **The System Must Know Its Own Body**
- **From Quote to Settlement: How EBU Handles Error**

Recommended main title:

> **The Binding EBU Quote: Institutional Responsibility and the Knowledge of the System**

### 4.1 Central thesis

EBU should calculate a usable value before an actor commits to an action. If an accepted quote can be replaced afterward by an arbitrarily worse settlement, EBU does not provide coordination; it exposes the actor to institutional uncertainty.

Therefore, when the actor supplied truthful information and performed the specified action under the quoted conditions, the institution that produced the quote must honor it. The institution—not the compliant actor—bears the residual caused by incomplete measurement, model error, environmental uncertainty, or inadequate knowledge of the governed system.

The actual physical outcome must still be measured and recorded. The guarantee governs allocation of the resulting balance, not denial of physical reality.

### 4.2 Opening problem: coordination or gambling?

Begin the chapter with the actor's dilemma.

The system offers:

\[
Q_t=+100\ \mathrm{EBU}
\]

The actor accepts and performs the action. Afterward, the system discovers:

\[
A_t=-256\ \mathrm{EBU}
\]

If the actor can now be charged \(-256\) EBU, the original quote had no dependable meaning. The actor accepted an unknown distribution of outcomes rather than a known coordination signal.

The correct settlement is:

\[
\varepsilon_t=A_t-Q_t=-256-100=-356\ \mathrm{EBU}
\]

and the ledger allocation is:

\[
\underbrace{+100}_{\text{binding actor settlement}}
+
\underbrace{(-356)}_{\text{institutional residual}}
=
\underbrace{-256}_{\text{actual system effect}}
\]

This example should appear near the beginning and be revisited throughout the chapter.

### 4.3 Why the pre-action quote matters

Explain that a quote is not only a prediction. It is a coordination interface between the local system and the actor.

The actor needs the quote to decide:

- whether to act;
- whether the action is compatible with personal and local homeostasis;
- whether alternative actions are preferable;
- whether the expected benefit justifies time, effort, risk, and opportunity cost;
- whether the institution's requested behavior can be trusted.

A quote that can change without a declared bound after the action fails these functions.

### 4.4 Ideal system and real system

In an ideal closed, deterministic, and completely observed system:

\[
S_{t+1}=T(S_t,a_t)
\]

and:

\[
Q_t=A_t
\]

In a real system:

\[
S_{t+1}=T(S_t,a_t,E_t)+\eta_t
\]

where \(E_t\) represents environmental interaction and \(\eta_t\) represents unobserved effects, uncertainty, model error, or measurement error.

The chapter must emphasize that the residual is not mystical disappearance. It indicates an incomplete accounting boundary, transport cost, dissipation, external transfer, unobserved state, or incorrect causal model.

### 4.5 Energy is not erased when a promise is honored

The institution honoring the actor's quote does not change the physical past. A failed action may still consume:

- energy;
- time;
- material;
- attention;
- information-processing capacity;
- infrastructure lifetime;
- ecological capacity;
- opportunity;
- recovery capacity.

The physical balance may be expressed as:

\[
C_{\mathrm{actual}}
=
C_{\mathrm{actor}}
+C_{\mathrm{system}}
+C_{\mathrm{external}}
+C_{\mathrm{unresolved}}
\]

Part VII must explain that physical accounting determines what was consumed, while the guarantee and responsibility rules determine which account bears that consumption.

### 4.6 Failure and immediate recalculation

After every attempted action, including failure, the system must observe the new local state and settle the existing EBU record.

Required cases:

- **No action occurred and no resource was consumed** — settle the actor exactly under the quote; release unused reservations; record any administrative cost in the appropriate system account.
- **Partial action** — measure the actual partial transition, honor the actor-facing quoted rule applicable to the accepted action, and assign the residual.
- **System-caused failure** — restore or pay the compliant actor according to the quote; charge the residual to the responsible institution or reserve.
- **Actor deviation** — if the actor materially departed from the quoted action or conditions, the quote is no longer automatically binding for the unquoted behavior.
- **Fraud or sensor manipulation** — suspend ordinary settlement and apply a separately defined verification procedure; do not classify manipulated input as institutional model error.
- **Uncertain result** — mark the record `UNRESOLVED`; do not pretend success, failure, or safe repeatability.

### 4.7 Institutional responsibility rule

Recommended rule for the manuscript:

> An accepted EBU quote is binding for an actor who truthfully disclosed the relevant state and performed the specified action within the quoted conditions. The system must recalculate the actual local transition after execution, but any difference caused by the institution's measurement, model, boundary, or governance error is assigned to the institution or its declared reserve. The residual remains visible and must be used to improve future measurement.

The institution is responsible because it:

- selected the measurement boundary;
- selected and maintained the sensors;
- defined the state representation;
- selected the model;
- issued the quote;
- authorized or requested the action;
- possessed greater capacity to pool uncertainty;
- controls the feedback process needed to improve future estimates.

### 4.8 The organism and its body

This analogy should be developed as a major explanatory section, not a short metaphor.

A country, company, city, hospital, or platform can be understood as a regulatory organism. Its land, infrastructure, resources, members, and institutions form its body. Sensors, statistics, audits, and local reports form its sensory system. Its models and policies form its nervous and regulatory systems.

If an organism cannot sense its own condition, it cannot regulate itself well. It may send an inappropriate signal to a cell, receive the cell's compliant response, and then discover that the action harmed the whole body. The organism cannot honestly claim that its sensory and regulatory error belongs entirely to the cell that followed the signal.

Likewise, an institution that issues a wrong EBU quote reveals that it did not know some relevant part of its own body:

- the state of its land;
- the condition of infrastructure;
- the availability of resources;
- the needs and constraints of people;
- transport and dissipation losses;
- externalities crossing its chosen boundary;
- delayed effects;
- interactions between local subsystems.

The residual is therefore a physiological symptom of institutional ignorance.

### 4.9 Quote error as a measure of governance quality

Part VII should propose that persistent quote error is a measurable indicator of institutional self-knowledge.

Useful measures to develop:

\[
\mathrm{MAE}_Q=\frac{1}{N}\sum_{t=1}^{N}|A_t-Q_t|
\]

\[
\mathrm{Bias}_Q=\frac{1}{N}\sum_{t=1}^{N}(A_t-Q_t)
\]

\[
\mathrm{TailRisk}_Q=P(|A_t-Q_t|>\tau)
\]

Possible interpretation:

- low average error suggests good local measurement and modeling;
- persistent signed bias suggests structural misvaluation rather than random noise;
- large tail risk suggests that the institution hides rare but severe uncertainty behind apparently precise quotes;
- error concentrated in particular regions or groups suggests unequal sensing or unequal institutional knowledge;
- slow correction suggests weak institutional learning.

These measures must not become simplistic league tables without normalization for task difficulty, environmental volatility, data availability, and boundary scale. The book should present them as diagnostic signals, not complete measures of moral worth.

### 4.10 Why institutional liability creates an improvement incentive

If every quote error is passed retroactively to the actor, the institution has weak incentives to improve. The actor becomes the absorber of measurement failure.

If the institution bears its own residual, repeated errors create visible pressure to improve:

- sensing;
- local measurement;
- causal models;
- maintenance;
- infrastructure maps;
- uncertainty bounds;
- data quality;
- feedback speed;
- institutional memory;
- cross-boundary accounting.

The reserve is therefore not merely insurance. It is a feedback organ. Its gains and losses reveal where the system lacks knowledge.

### 4.11 The EBU measurement reserve

Create a visible reserve account:

\[
R_{t+1}=R_t+\varepsilon_t+F_t-P_t
\]

where:

- \(R_t\) is the reserve balance;
- \(\varepsilon_t\) is the signed measurement residual assigned to the institution;
- \(F_t\) is prospective reserve funding;
- \(P_t\) is any separately defined payout or correction flow not already represented by \(\varepsilon_t\).

Editorial note: the signs and accounting convention must be reconciled with the authoritative EBU equations before publication.

Possible prospective funding mechanisms:

- general taxation;
- a small transparent measurement-risk contribution;
- company or institutional capital reserves;
- insurance or reinsurance between institutions;
- public budgets for collectively beneficial actions;
- sector-specific reserve pools;
- retained surpluses from conservatively accurate quotes.

The funding rule must be declared before outcomes. It need not distribute cost equally. It should distribute risk transparently, predictably, and according to a defensible institutional rule.

### 4.12 Why collective risk pooling can be appropriate

An institution can often absorb prediction error better than a single actor because it can pool many actions across time, geography, and categories. A rare large error can ruin one person while remaining manageable for a broad reserve.

Risk pooling is justified when:

- the system requested or authorized the action;
- the institution controlled the quote model;
- the actor complied with the quoted conditions;
- measurement error is systemic or collectively generated;
- spreading the risk improves participation and coordination;
- the reserve remains transparent and cannot silently socialize avoidable private manipulation.

This section should distinguish legitimate collective insurance from hiding institutional incompetence. Repeated residuals must trigger learning, review, and model correction.

### 4.13 Safeguards against exploitation

A binding quote cannot be unconditional. The chapter must specify that it remains binding only when:

1. the actor provided truthful relevant information;
2. the quoted action was identified precisely enough to verify;
3. the actor performed that action within the stated conditions and validity period;
4. the actor did not manipulate sensors, state reports, or settlement evidence;
5. the institution actually authorized the quote;
6. the quote was not visibly corrupted or outside a mechanically enforced validity range.

Safeguards should protect the institution without transferring ordinary measurement uncertainty back to the actor.

### 4.14 Actions the system does not understand

When uncertainty is too large, the system should not issue a falsely precise guaranteed quote. It should choose explicitly among:

- decline to quote;
- delay authorization until adequate measurement is available;
- issue a guaranteed bounded quote with a declared interval;
- cap the scale of the authorized action;
- divide the action into measurable stages;
- classify it as experimental and obtain separate informed consent;
- require additional reserve coverage before authorization.

The system must communicate uncertainty before the action, not reveal unlimited uncertainty afterward.

### 4.15 Bounded quotes

Open design question: whether some EBU actions should use a guaranteed point quote or a guaranteed interval.

A bounded quote could take the form:

\[
Q_t\in[L_t,U_t]
\]

The actor would know the maximum possible adverse settlement before acting. The final actor settlement could vary within the accepted interval, while any residual outside the interval would remain institutional.

This may preserve coordination when exact point valuation is impossible. However, intervals must not be made so wide that they recreate gambling under another name.

### 4.16 Nested institutional responsibility

A local institution may issue the quote while relying on regional, national, corporate, or international data and infrastructure. Part VII should explain how residuals move through nested responsibility layers.

Possible hierarchy:

1. actor-facing quote remains binding;
2. local issuer settles with the actor;
3. local issuer attributes upstream components using frozen rules;
4. reserve or insurance layers redistribute the institutional residual;
5. the complete chain remains visible in the ledger;
6. no upstream dispute delays the compliant actor's settlement.

### 4.17 Positive and negative residuals

The book must address both directions.

- If the actual effect is worse than quoted, the institution bears the negative residual.
- If the actual effect is better than quoted, the positive residual must follow a declared rule rather than being opportunistically appropriated after observation.

Open question: positive residuals may replenish the reserve, be shared with the actor, or be divided according to a prospective formula. The rule must be symmetrical enough to avoid institutions systematically underquoting benefits while socializing only losses.

### 4.18 Learning loop

Every settled record should feed a controlled learning process:

\[
(S_t,a_t,Q_t,S_{t+1},A_t,\varepsilon_t)
\longrightarrow
\text{model review and future calibration}
\]

The system should ask:

- Which state variable was missing?
- Which boundary was incomplete?
- Was a transport or dissipation path ignored?
- Was the causal model wrong?
- Was uncertainty understated?
- Was the failure local or systemic?
- Does the same bias affect particular communities or locations?
- Which sensor, process, or institution must improve?

Model improvement may change future quotes, but it must never rewrite historical quotes or receipts.

### 4.19 Ledger requirements for Part VII

Each EBU action record should preserve at least:

- record identifier;
- quote issuer;
- actor or protected participant identity according to the privacy model;
- timestamp or causal sequence;
- observable pre-action state reference;
- exact action specification;
- quote value or bounded quote;
- assumptions and validity conditions;
- acceptance evidence;
- action status;
- observable post-action state reference;
- actual EBU evaluation;
- residual;
- residual classification;
- actor settlement;
- institutional settlement;
- reserve account movement;
- unresolved balance, if any;
- model version;
- measurement provenance;
- audit and appeal status;
- immutable links between quote and settlement.

### 4.20 Appeals and corrections

The actor should be able to challenge whether:

- the correct quote was applied;
- the performed action matched the specification;
- a deviation was attributed correctly;
- a failure was wrongly classified as actor-caused;
- the institution altered conditions after acceptance;
- the settlement record matches the observed evidence.

An appeal may correct measurement or responsibility. It must not erase the original record. Corrections should be appended and linked so institutional learning remains possible.

### 4.21 Why create a restaurant? Initiative, enterprise, and motivation

This should be a substantial chapter section, not a footnote. It begins with a direct question:

> Why would an actor create a restaurant, workshop, laboratory, farm, school, or other enterprise if the actor cannot earn EBU from creating it?

The present working answer is that the premise is probably wrong. A useful enterprise can generate EBU, and its initiator can earn EBU for identifiable contribution. EBU should not eliminate initiative. It should make the basis of its reward clearer.

#### 4.21.1 The restaurant as a bundle of contributions

Creating a restaurant can involve several actions with distinct EBU effects:

- recognizing that a community lacks a useful service;
- imagining and designing a new response;
- organizing a location, equipment, supplies, knowledge, and people;
- accepting responsibility for a difficult coordination process;
- producing nourishment and safe food;
- producing hospitality, pleasure, culture, meeting space, and belonging;
- creating learning, apprenticeships, and local capability;
- reducing or increasing ecological and health burdens;
- maintaining the service when novelty has passed;
- improving the restaurant in response to receipts and local feedback.

The actor may receive EBU for these contributions. Workers and other contributors must also receive their own settlements. The fact that an initiator had the original idea does not make everyone else's contribution disappear, but neither should the existence of collective contribution erase the value of initiative.

#### 4.21.2 Reward without copying today's profit formula

Today's profit combines many different things: payment for work, return for risk, control of scarce assets, bargaining power, temporary innovation reward, inherited ownership, externalized costs, and sometimes monopoly rent. EBU should not treat this bundle as one indivisible natural law.

A future EBU design may separate:

- **creation reward** for discovering and developing a valuable possibility;
- **coordination reward** for organizing a functioning system;
- **labor settlement** for continuing work;
- **stewardship reward** for maintaining assets and capabilities responsibly;
- **declared risk coverage** for a bounded risk accepted before action;
- **learning reward** for verified improvements that help the wider system;
- **ownership or access rights**, whose duration and EBU consequence require separate justification;
- **external costs**, which must not be hidden by a positive customer-facing balance.

Possible mechanisms include a guaranteed project quote, milestone quotes and receipts, a time-bounded founder reward, continuing EBU tied to continuing contribution, or a prospectively declared share of verified system benefit. These are design candidates, not settled laws.

The key distinction to investigate is:

> Reward for creating and sustaining value is not necessarily the same as an unlimited claim produced by ownership alone.

#### 4.21.3 Motivation is plural

People do not create restaurants only for money. Possible motives include:

- material security and spendable EBU;
- autonomy;
- enjoyment of food and hospitality;
- mastery and creativity;
- recognition and reputation;
- social connection;
- care for a place or community;
- curiosity and experimentation;
- ambition and the wish to build something excellent;
- ecological or public purpose.

EBU should not require altruism, but it also should not assume that profit is the only stable human motive. A robust design should allow personal benefit and system benefit to align while protecting people from coercion and deprivation.

#### 4.21.4 Preferences may change under EBU

Statements such as “people will not do this unless it is profitable in today's sense” extrapolate from preferences formed inside today's institutions. That evidence remains relevant, but it is not automatically valid under a substantially different system.

Preferences are influenced by:

- what work is visible and recognized;
- which activities provide security;
- which actions receive status and social meaning;
- how much time and capacity people have after basic needs are met;
- what institutions teach people to count as success;
- which harms are hidden and which contributions are measured;
- whether cooperation is rewarded or exploited;
- whether experimentation can occur without catastrophic personal loss.

If EBU makes ecological regeneration, prevention, care, maintenance, and knowledge creation measurable and dependable, people may increasingly want to generate EBU through work for the planet. The system may change not only the chosen action but also the culture in which desires develop.

This possibility must be stated carefully. The manuscript must not claim that EBU will automatically create altruistic people, eliminate status competition, or make all socially valuable work enjoyable. It should claim only that preferences are not external constants and that institutional feedback can cultivate some motives while suppressing others.

#### 4.21.4a Evidence anchor: economic organization and learned social behavior

Use one principal anthropology/cross-cultural study here rather than a broad literature review:

> Henrich, Joseph, et al. (2005). “Economic Man” in Cross-Cultural Perspective: Behavioral Experiments in 15 Small-Scale Societies. *Behavioral and Brain Sciences*, 28(6), 795–855. https://doi.org/10.1017/S0140525X05000142

The researchers used ultimatum, public-goods, and dictator games across 15 small-scale societies with different economic and cultural conditions. The simple self-interested actor model failed in every society studied, while behavior varied substantially between societies. At group level, economic organization and patterns of everyday social interaction explained a substantial portion of that variation. In particular, higher payoffs to cooperation and greater aggregate market integration were associated with more prosocial experimental behavior.

For Part VII, the important lesson is not that markets necessarily create altruism, nor that EBU will produce one predictable personality. It is narrower:

> Human economic behavior is not adequately described as a fixed preference independent of culture and institutions. The forms of cooperation practiced and rewarded in everyday life can be reflected in later choices.

This supports treating the restaurant founder's motives, ecological-work preferences, cooperation, and ideas of success as partly adaptive rather than timeless constants. If EBU changes which contributions are secure, visible, respected, and rewarded, motivation may change over time. That remains a hypothesis to test, not an outcome to assume.

The manuscript must state the study's limitation. It compared societies at one period and found associations; the authors explicitly said their historical data could not establish the direction of causality. It therefore cannot prove that introducing EBU would cause a particular cultural change. It justifies rejecting the opposite unsupported assumption that today's observed preferences must remain unchanged under every institutional arrangement.

This study appears in publicly searchable material attributed to Peter Joseph's *The New Human Rights Movement* and closely matches the theme of the linked 2017 lecture. Before final publication, verify its exact page or endnote against an authoritative copy of the book; cite the original paper as the scientific source rather than citing the lecture as evidence.

#### 4.21.5 Ecological work as productive work

If the planet, ecosystem, or ecological subsystem is inside the relevant EBU boundary, work that improves its homeostasis is productive even when it produces no conventional sale.

Examples may include:

- restoring soil, wetlands, forests, rivers, or biodiversity;
- reducing pollution and material waste;
- maintaining long-lived infrastructure;
- preventing future damage;
- increasing resilience and recovery capacity;
- producing shared ecological knowledge;
- caring for common resources that no single customer owns.

EBU could make such contributions legible and rewardable. This reverses a common present distortion in which extraction produces private revenue while restoration appears merely as a cost.

However, ecological value must not be reduced to whichever variables are easiest to count. Delayed effects, uncertainty, local knowledge, irreversible loss, and cross-boundary consequences require explicit treatment.

#### 4.21.6 The counterfactual problem

The theory needs a method for asking what would happen without the enterprise. A busy restaurant is not automatically a positive contribution if it merely displaces an equally good service, depends on exploited labor, worsens local health, or creates greater ecological loss elsewhere.

Possible questions include:

- Did the enterprise satisfy an unmet need or only capture existing activity?
- Did it create new local capability?
- Did it improve or degrade homeostasis across the relevant time horizon?
- Were costs shifted to workers, distant communities, future actors, or ecosystems?
- Would another allocation of the same resources have produced greater benefit?
- How much of the result came from the founder, workers, inherited infrastructure, public knowledge, location, or institutional support?

This makes EBU evaluation harder than counting sales, but it also reveals what sales alone leave invisible.

#### 4.21.7 Avoiding two symmetrical mistakes

Part VII must reject both of these unsupported assumptions:

1. **Present-system determinism** — people will always behave exactly as they do under today's monetary and ownership incentives.
2. **Altruistic utopianism** — changing the accounting system will automatically remove self-interest, conflict, scarcity, gaming, and status competition.

EBU needs a transition theory and empirical tests. It should observe how motivations change, preserve freedom to initiate projects, reward verified contribution, expose externalities, and revise future quotes without dictating a single approved way of life.

#### 4.21.8 Placement question

This theme may be too large for one section inside the binding-quote chapter. During manuscript integration, decide whether it becomes:

- a major chapter within Part VII;
- a second division of Part VII;
- or a separate future part on enterprise, motivation, ownership, and preference formation.

Do not settle that editorial placement until the authoritative Parts I–III and any planned Parts IV–VI are available.

### 4.22 Moral and political consequences

This design changes the relationship between actors and institutions.

The institution can no longer demand precise obedience while externalizing the cost of its own ignorance. Authority to issue actionable valuations is paired with responsibility for valuation error.

Potential consequences to explore:

- greater trust in public and corporate coordination;
- stronger pressure for transparent measurement;
- explicit budgeting for uncertainty;
- reduced fear of catastrophic retroactive charges;
- institutional reluctance to authorize poorly understood actions;
- possible overconservatism if reserves are weak;
- political conflict over who funds residuals;
- pressure to conceal or reclassify errors;
- unequal measurement quality across populations;
- the need for independent audit of quote models and reserves.

### 4.23 Limits and nonclaims

Part VII must not claim that:

- every physical effect can already be measured exactly;
- every residual can immediately be assigned to one cause;
- institutional payment makes physical damage disappear;
- all institutional error should be funded equally by every actor;
- all risky or experimental actions deserve a guaranteed point quote;
- a binding quote protects fraud, manipulation, or material deviation;
- low quote error alone proves good governance;
- EBU eliminates uncertainty.
- people will cease to value personal reward;
- every useful enterprise should receive unlimited EBU;
- observed demand is identical to total system benefit;
- preferences formed under the present system are timeless human constants;
- EBU will automatically make people altruistic or ecologically responsible.

The claim is narrower: EBU should make uncertainty, responsibility, and settlement explicit, and should place ordinary model error on the institution that issued and guaranteed the actionable quote.

### 4.24 Proposed laws or propositions to formalize

These are working propositions and require reconciliation with the existing ten laws and formal EBU notation.

1. **Pre-action valuation principle** — an actionable EBU quote is derived from the observable local state before commitment.
2. **Quote immutability principle** — an accepted quote cannot be rewritten after observing the outcome.
3. **Compliant-actor guarantee** — a truthful actor performing the specified action receives the accepted settlement.
4. **Residual visibility principle** — the difference between quote and observation remains visible in the ledger.
5. **Issuer responsibility principle** — ordinary measurement and model residual belongs to the guaranteeing institution.
6. **Physical conservation principle** — settlement allocation cannot erase real physical consumption or transfer.
7. **Unresolved-state principle** — uncertainty must be recorded explicitly and must not authorize unsafe repetition.
8. **Prospective-risk principle** — uncertainty limits and funding rules must be declared before the action.
9. **Institutional-learning principle** — residuals must feed measurement and model improvement.
10. **Historical-integrity principle** — learning may change future quotes but cannot rewrite historical records.
11. **Contribution-reward principle** — initiative and verified contribution may earn EBU without making ownership alone an unlimited permanent source of EBU.
12. **Adaptive-preference principle** — the system must not treat preferences formed under one incentive environment as immutable when evaluating a different institutional environment.

### 4.25 Suggested figures and tables

1. **Quote-to-settlement timeline** — observe state, calculate quote, accept, act, observe, settle, allocate residual, learn.
2. **The +100 / -256 example** — actor settlement, institutional residual, and actual system balance.
3. **Organism analogy** — sensors, regulatory model, signal to cell, action, body response, corrective feedback.
4. **Physical effect versus responsibility table** — what happened compared with who bears it.
5. **Failure decision table** — no action, partial action, system failure, actor deviation, fraud, unresolved result.
6. **Nested reserve diagram** — local issuer, sector reserve, national reserve, insurance layer.
7. **Governance diagnostic dashboard** — mean error, bias, tail error, group disparity, and learning speed.
8. **Restaurant contribution map** — founder initiative, worker contributions, customer benefit, institutional support, resource costs, and ecological effects.
9. **Motivation under different systems** — security, EBU reward, autonomy, recognition, purpose, and ecological contribution without claiming a single deterministic response.

### 4.26 Suggested chapter sequence

1. The actor's problem: a quote that can become a gamble.
2. The EBU quote derived from the current local state.
3. The ideal transition and the real transition.
4. From quote to receipt and settlement.
5. The +100 EBU / -256 EBU example.
6. Physical loss versus accounting responsibility.
7. Why the compliant actor receives the quoted settlement.
8. Failed, partial, manipulated, and unresolved actions.
9. Why create a restaurant? Initiative and the right to earn EBU.
10. Contribution, coordination, labor, risk, and ownership.
11. Why motivations and preferences may change under EBU.
12. Ecological restoration as productive work.
13. The institution as an organism that must know its body.
14. Measurement residual as a governance signal.
15. Institutional reserves and collective risk pooling.
16. Safeguards against manipulation and moral hazard.
17. Bounded quotes and experimental actions.
18. Nested institutions and upstream responsibility.
19. Learning from residuals without rewriting history.
20. Political consequences, limitations, and open questions.
21. Formal propositions and connection to the existing EBU laws.

## 5. Exact wording to preserve for the future manuscript

The following formulations capture the present conceptual decision and should survive editorial revision unless the theory itself changes:

> The actor bears the quoted consequence. The institution that produced and guaranteed the quote bears its measurement error.

> A refund or guaranteed settlement changes who bears the cost; it does not erase a physical cost that has already occurred.

> The quote predicts and guarantees the actor-facing settlement. The receipt records what physically occurred. The residual connects the two without rewriting either.

> An institution's persistent EBU residual measures, in part, how well it knows the body it governs.

> The system must communicate uncertainty before the action, not impose unlimited uncertainty after the action.

> EBU should reward initiative and verified contribution without assuming that ownership alone creates an unlimited permanent claim on future value.

> We cannot infer motivation under EBU solely from preferences produced by today's institutions.

> A system does not merely respond to preferences; through security, recognition, measurement, and reward, it also helps to form them.

## 6. Open questions for later theoretical work

Status: **Open questions**

1. Is EBU strictly a unit of measurement, a spendable balance, or both in different layers?
2. Should the default guarantee be a point quote, a bounded interval, or depend on action class?
3. How are positive residuals divided between the actor, issuer, reserve, and wider system?
4. What exact conditions count as material actor deviation?
5. How is causal responsibility assigned when actor error and system error interact?
6. How long may a record remain `UNRESOLVED`?
7. Who funds the reserve at municipal, national, company, and international levels?
8. Which reserve contributions are fair: equal, progressive, sector-weighted, risk-weighted, or benefit-weighted?
9. What prevents an institution from intentionally issuing conservative quotes to protect its reserve?
10. What prevents an institution from classifying its own error as actor misconduct?
11. Which independent body audits measurement quality and reserve solvency?
12. How should rare catastrophic residuals be handled?
13. How are ecological effects with long delays settled?
14. How are privacy and local-state observability balanced?
15. How do the Part VII propositions map onto the existing ten EBU laws without duplication or contradiction?
16. By which mechanism does a founder earn EBU for creating a useful enterprise?
17. Which founder rewards should be one-time, time-bounded, milestone-based, or tied to continuing contribution?
18. How are EBU settlements divided among initiators, workers, suppliers, customers, public infrastructure, knowledge commons, and ecological accounts?
19. Does supplying capital create an EBU contribution, a repayment claim, a stewardship duty, or some combination?
20. Can ownership alone continue producing EBU after active contribution ends, and if so, for how long and why?
21. How should EBU value novelty, coordination, risk, maintenance, and counterfactual benefit?
22. How can the system distinguish a genuinely unmet need from displacement, captured demand, or preference manipulation?
23. Which basic security conditions are required before observed choices can be interpreted as relatively free preferences?
24. How should preference change be studied without allowing the institution to manipulate citizens toward centrally approved desires?
25. How should ecological work be quoted when its benefits are delayed, distributed, uncertain, or partly irreversible?
26. What transition rules allow enterprise and experimentation while moving from current money, ownership, and employment structures toward EBU?

## 7. Editorial integration tasks

Status: **Editorial tasks**

1. Import the exact authoritative tables of contents for Parts I–III.
2. Locate the intended place and existing meaning of “Part 7” in the manuscripts.
3. Determine whether this material is one large chapter, several chapters within Part VII, or a complete standalone Part VII volume.
4. Reconcile `quote`, `receipt`, `ledger`, `settlement`, `reserve`, `residual`, and `EBU balance` with the book's established glossary.
5. Verify every equation against the authoritative EBU formalism.
6. Preserve the existing ten-law numbering and avoid introducing duplicate laws.
7. Connect the institutional organism analogy to the book's homeostasis framework.
8. Connect transport and dissipation residuals to the physics chapters.
9. Add worked examples at individual, company, city, national, and ecological scales.
10. Add failure examples where the actor deviates, the institution errs, both contribute, or the outcome remains unknown.
11. Define reserve solvency, governance audits, and appeals without prematurely claiming a complete legal system.
12. Separate theoretical EBU receipts from technical execution markers used in scientific experiments.
13. Decide whether the +100 / -256 / -356 example remains the canonical introductory example.
14. After integration, run a duplication review across all books.
15. Develop the restaurant as a complete worked case from project proposal through quotes, opening, operation, failures, receipts, participant settlements, ecological effects, and institutional learning.
16. Separate founder initiative, labor, coordination, capital, ownership, stewardship, public infrastructure, inherited knowledge, and externalities in that case.
17. Add contrasting examples: a community restaurant, a founder-led commercial restaurant, an ecological restoration cooperative, and a project that attracts demand while harming system homeostasis.
18. Add a motivation chapter that distinguishes material reward, security, autonomy, mastery, recognition, belonging, purpose, and altruism.
19. Review evidence on endogenous preferences, crowding out of intrinsic motivation, cooperative behavior, entrepreneurship, and institutional transition before making empirical claims.
20. Decide whether enterprise and adaptive preferences belong inside Part VII or require a separate future part.
21. Verify the exact Peter Joseph book page or endnote for Henrich et al. (2005), then retain the primary paper—not the lecture—as the scientific citation.

## 8. Future revision log

### 2026-08-10 — Binding quote and institutional residual

Confirmed direction:

- EBU derives a pre-action quote from the current local system state.
- A compliant actor should be able to rely on the accepted quote.
- Post-action observation does not retroactively rewrite the actor's quote.
- The difference between quoted and actual system effect is recorded as a residual.
- Ordinary model and measurement error is borne by the issuing institution or its prospectively funded reserve.
- Physical costs remain recorded even when the actor is refunded or paid.
- The residual is a measure of institutional self-knowledge and an incentive to improve sensing, modeling, maintenance, and governance.
- A country or company that repeatedly misquotes actions demonstrates that it does not adequately know the state of the body it governs.
- Safeguards are required for fraud, manipulation, material deviation, experimental actions, bounded uncertainty, and unresolved outcomes.

No final decision yet:

- exact reserve funding formula;
- treatment of positive residuals;
- default use of point versus interval quotes;
- formal mapping to the existing ten EBU laws;
- exact placement and numbering inside the authoritative manuscripts.

### 2026-08-10 — Enterprise, motivation, and adaptive preferences

Confirmed direction:

- EBU must not be presented as forbidding a person from earning EBU by creating a useful restaurant or other enterprise.
- Initiative, innovation, coordination, labor, stewardship, and continuing service may all be real contributions that deserve EBU settlement.
- These contributions must be distinguished from an assumed unlimited reward for ownership alone.
- A restaurant's sales or popularity are not identical to its complete EBU contribution; nourishment, hospitality, community, labor burden, resource use, ecology, and externalities must also be considered.
- Founder, workers, suppliers, customers, institutions, and ecological accounts may require separate quotes and settlements.
- Human motivation is plural and includes personal benefit, security, autonomy, mastery, recognition, belonging, curiosity, care, ambition, and purpose.
- Preferences observed under today's system cannot be assumed to remain unchanged under EBU.
- If ecological and collective work becomes visible, secure, respected, and rewardable, people may increasingly choose to generate EBU through work for the planet.
- This is a testable possibility, not a claim that EBU automatically makes everyone altruistic.
- EBU must avoid both present-system determinism and altruistic utopianism.

No final decision yet:

- the exact founder-reward mechanism;
- the duration and basis of any ownership-linked return;
- the allocation between founder, workers, capital, public infrastructure, knowledge commons, and ecological accounts;
- the valuation of novelty, coordination, risk, counterfactual benefit, and displaced alternatives;
- the institutional design for measuring preference change without manipulating preferences;
- whether this material belongs within Part VII or a separate future part.

Evidence anchor selected:

- Henrich et al. (2005), a cross-cultural experimental study of 15 small-scale societies, will support only the restrained proposition that economic organization and everyday patterns of cooperation are associated with differences in social behavior.
- It must not be presented as causal proof that EBU will create altruism or any predetermined culture.
- The citation's exact location in Peter Joseph's book must be verified against an authoritative copy before publication.
