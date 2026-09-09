# SD-01 static control derivations and proposed mappings

Status: **STATIC_DERIVATION_ONLY — BINDING_NOT_DERIVABLE**.
Draft ID: `SD01-CONTROL-DERIVATION-v1`.
Base: `db448403da2c7c16ae62479e88bb748e377820e1`.

This draft preserves every frozen equation, predicate, threshold, configuration
count, numerical policy and interpretation rule. It supplies exact candidate
mappings and identifies where the sources cannot select or complete them.
Approval accepts this static analysis only; it does not choose an unresolved
semantic rule, close the Stage F gap, modify implementation, or authorize science.

The source chain is the SD-01 row `/studies/0` of
`stage_d_scientific_validation_master_matrix.json` (configuration parameters,
controls, accounts, acceptance and stopping rules),
`STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md` §4.1,
`stage_d_scientific_validation_contract.json` `/prospective_numerical_policy`,
Stage E authority §5, and the Stage F route-level seal requirements. Existing
files and the prior unsealed dossier remain unchanged. Exact source identities
and arithmetic checks accompany this draft in `sd01_control_derivation_checks.json`.

## 1. Exact source and demand table

At x=15, `x(1-x/20)=15/4` and `x/5-1=2`. Thus logistic
`g(15)=15*rho/4`, Allee `g(15)=15*rho/2`, and each registered demand
is exactly its column ratio times g(15). The g(15) and demand entries below
are stock-unit/tick; demand ratios are dimensionless. No additional unit
convention for rho is adopted here.

| Source | rho | g(15) | ratio 1/4 | ratio 3/4 | ratio 1 | ratio 5/4 |
|---|---:|---:|---:|---:|---:|---:|
| Logistic | 3/10 | 9/8 | 9/32 | 27/32 | 9/8 | 45/32 |
| Logistic | 3/5 | 9/4 | 9/16 | 27/16 | 9/4 | 45/16 |
| Allee | 3/10 | 9/4 | 9/16 | 27/16 | 9/4 | 45/16 |
| Allee | 3/5 | 9/2 | 9/8 | 27/8 | 9/2 | 45/8 |

These are exact rational parameter derivations, not binary64 trajectories.
The frozen one-time conversion and written operation order still apply later.

## 2. Four complete candidate control mappings and derivation chains

The following is one complete, mathematically consistent candidate. The labels
C1–C4 are document row labels, not scientific run identities. All cumulative
accounts start at zero; horizon 20,000 and checkpoint cadence 1,000 remain
unchanged; no stochastic draws or external inflow occur. The policy and shock
assignments below are **proposals, not uniquely implied bindings**.

| Row | Source | rho | x0 | Demand | Policy | Shock schedule | Frozen target predicate |
|---|---|---:|---:|---:|---|---|---|
| C1 | Logistic | 3/10 | 15 | 0 | H1 | none | Reach abs(x-20)<=1e-6 by tick 1,000; persist 100 ticks |
| C2 | Logistic | 3/5 | 15 | 0 | H1 | none | Same predicate for the other frozen rho |
| C3 | Allee | 3/10 | 4 | 0 | H1 | none | Never label the x0=4 trajectory regenerative without inflow |
| C4 | Allee | 3/5 | 4 | 0 | H1 | none | Same predicate for the other frozen rho |

**C1:** Two zero-demand logistic controls and the two rho values are frozen.
With d=0, H1 gives u=0. Put e=20-x. The written equations imply
`e_next=e*(1-rho*x/20)`. For x in [15,20], x remains in that interval and
`0<=e_next<=31e/40`. Therefore `e_t<=5*(31/40)^t`; exact integer arithmetic
shows `5*(31/40)^100<1e-6`. The bound persists thereafter. This supplies a
mathematical witness for the already-frozen entry/persistence predicate.

**C2:** The same frozen control definition uses rho=3/5. Its deficit bound is
`e_next<=11e/20<=31e/40`, so the same proof supplies the existing target.
H1 assigns service without introducing reserve stock or hidden replenishment.

**C3:** The source, rho pairing, initial stock below A=5 and prohibition on a
regenerative label without inflow are frozen. For x in (0,4],
`x+g(x)=x*[1-rho*(1-x/20)*(1-x/5)]`. The multiplier lies in [1-rho,1), so
stock stays positive and decreases in exact real arithmetic. Consequently
x_pre<5 and H1 selects u=0. Also g(x)<0 throughout this interval. Zero demand
and no shocks isolate the source-sign control, but the frozen assertion does
not uniquely mandate those assignments. The deliberately sub-reserve initial
state must not be called H1-stock-viable or silently clamped to 5.

**C4:** Substitute rho=3/5 into the same factorization; its multiplier is at
least 2/5 and below 1. The same non-regeneration argument holds. Neither C3 nor
C4 is required to pass a reserve-viability predicate that its initial state
already violates. Their target is the frozen negative regeneration assertion.

All four use no H3 branch checks and preserve the frozen count arithmetic:
`196*20000 + 32*20000*55 = 39,120,000` registered expected evaluations.
This is an accounting derivation, not observed work or a reason to tune controls.

## 3. Exact registered safe-policy candidate

Candidate P: **logistic, rho=3/10, demand ratio=1/4, d=9/32,
H1, no shocks, x0=15**. It is an existing member of the 192-cell product,
not an additional trajectory.

Derivation chain: the table fixes d; H1 supplies the reserve constraint.
On `I=[15,x*]`, where `x*=10+5*sqrt(13)/2<20`, one has
`g(x*)=9/32`, `x+g(x)-5>d`, and hence u=d. The map is
`F(x)=x+(3/10)*x*(1-x/20)-9/32`, with
`0<F'(x)=13/10-3x/100<=17/20` on I. Thus F maps I into itself,
stock increases toward x*, and service is constant. The first increment is
27/32 and subsequent increments obey
`0<=x_(t+1)-x_t<=(27/32)*(17/20)^t`.
Exact arithmetic makes this bound less than 1e-8 at t=120 and thereafter.

Already-frozen checks remain separate: all post-transition states in [5,20];
pre/post reserve states at least 5; logistic g nonnegative on [0,20]; exact
owning accounts and the frozen scaled 1e-12 conservation-residual rule; and
1,000 consecutive post-transition ticks after the final shock with both stock
and service increments at most 1e-8, ending by tick 20,000. The interval
`t=120..1119` is an analytic witness for the existing homeostasis window,
not a new deadline. Shock recovery and H3 branch predicates do not apply to P.
All original falsifiers, numerical checks and acceptance rules remain controlling.

This proves suitability in exact real arithmetic, not observed binary64 PASS,
and does not uniquely identify what the source means by “accepted safe policy.”

## 4. Exact registered high-demand candidate and the unresolved assertion

Candidate N: **Allee, rho=3/10, demand ratio=5/4, d=45/16,
H1, no shocks, x0=15**. It too is an existing scientific cell.

Derivation chain: `g(x)=(-3x^3+75x^2-300x)/1000`.
On the H1 stock set [5,20], its maximum occurs at
`x_m=(25+5*sqrt(13))/3`, and
`g(x_m)=(35+13*sqrt(13))/36 < 29/12 < 45/16=d`.
The upper bound follows from sqrt(13)<4. Thus every full-demand transition
would consume more than `d-29/12=19/48` of stock. Twenty-six such transitions
would imply `x_26<15-26*(19/48)=113/24<5`. Full demand cannot be served on
every tick while remaining reserve-viable. This finite algebraic contradiction
uses no trajectory; 26 is a derived witness, not a new stopping rule or threshold.

Nevertheless, for x in [5,20], g(x)>=0 and
`20-(x+g(x))=(20-x)*[1-(3/10)*x*(x-5)/100]>=0`, because the bracket is
at least 1/10. H1 therefore maps [5,20] into itself by restricting served
u to `min(d,max(0,x_pre-5))`. Stock can remain viable while service is rationed.
The existing unmet-demand ledger `d-u` distinguishes these facts exactly.
Positive unmet demand is an account value, **not a newly adopted acceptance
threshold or permission to relabel stock viability**.

N is a justified candidate for demonstrating inability to serve all requested
demand. It cannot be certified as the uniquely intended mapping of “demand
above feasible regeneration must not be reported viable” without specifying
what “feasible regeneration” tests and how this control composes with the
stock-set and overall acceptance predicates. Overall “viable” requires all
acceptance predicates, so this is an unresolved semantic binding, not proof
that the frozen documents are logically contradictory. No wording is replaced.

A high ratio alone is insufficient: logistic rho=3/10 at ratio5/4 has
`d=45/32>g(15)=9/8` but `d<max_[0,20] g=3/2`. Initial regeneration,
maximum regeneration, stock feasibility and full-demand feasibility are
mathematically different quantities.

## 5. Proven ambiguity and precise missing semantic rules

These are witnesses of non-uniqueness, not preferences or adopted alternatives.

| Missing rule | Two mathematically consistent assignments / distinction | Why frozen predicates cannot select |
|---|---|---|
| Policy selector for the four controls | H1 versus H2_eta=1 | Same u for every state and demand, same [5,20] stock set, same four control targets and no extra H3 checks; distinct registered policy labels |
| Control shock selector | none versus registered adversarial outflow | First shock is tick2,500, after logistic entry-by1,000/persist100; “no external inflow” does not forbid Allee outflow, which cannot make the sub-threshold stock regenerative |
| Allee-control demand selector | zero versus its registered ratio1/4 demand (9/16 or 9/8 by rho) under H1 | Below 5, H1 serves zero for either; the regeneration assertion is identical while unmet-demand accounts differ |
| Which low-demand cell implements the positive assertion | P versus logistic rho=3/5, ratio1/4, d=9/16, H1, none | Same invariant interval and fixed point; the second map has derivative at most 7/10 and satisfies the same exact-real frozen predicates |
| Definition and composition of demand-feasibility negative assertion | Existence of admissible u<=d preserving the stock set versus existence with u=d every tick | N admits the former and rules out the latter; the source does not define this quantifier or its relation to the aggregate “viable” label |

The demand table, four candidate tuples, P and N are decision-ready mathematical
proposals with explicit derivation chains. A complete authoritative selection
cannot follow from the frozen material alone. Under the instruction to add no
rule or interpretation, this draft records those missing selectors instead of
supplying them. The original gap remains open and execution remains blocked.
