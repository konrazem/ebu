# Local Gaussian EBU — programme reconciliation

Status: **current prospective programme and editorial reconciliation**.
Date: 18 September 2026. This document records the author's new direction,
source-inspected compatibility findings, and conditional mathematical checks.
It does not register parameters, implement a model, authorize execution, or
report new scientific evidence. See [the authority index](CURRENT_SCIENTIFIC_AUTHORITY.md).

## 1. Outcome and scope

Keep the existing EBU research history. Make the new active question explicit:

> Given a declared physical world and deviation potential, what happens when
> actors choose randomly among physically feasible actions/groups they can
> afford under a separately declared signed capacity-accounting rule?

EBU supplies the value calculation. It does not secretly choose the action
that maximizes value, minimizes deviation, meets service first, or restores
the reference. Recovery, cycling, refusal and poor performance remain open.

The immediate deliverable is a clean, source-locked documentation state and a
new book architecture. The next author-facing stage is Book I preparation/
generation, under a separate instruction. Experimental implementation with
Claude follows later. The handover's instruction to proceed automatically
into implementation is explicitly out of scope for this stage.

## 2. Preservation baseline

Starting commit: `36373aa44c2fe065ed54c186c8037e541805f87f` on
`v3.0-local-ebu-foundation`, 18 commits ahead of the cached origin reference.
The author authorized local checkpoint and reconciliation commits only.

The 22-path pre-existing Claude snapshot was preserved, without content
changes, at `924a4d9a801b96f265aa3f0adc40e2c09063e469`. It contains 20 new
files and two modified files. This is a **preservation checkpoint**, not a
validation or scientific acceptance commit. Its 216 tracked files are all
listed with SHA-256 hashes and dispositions in the migration inventory.

Reconciliation uses `codex/local-gaussian-reconciliation`. No other branch is
rewritten; no source lineage is merged; no remote is updated. Framework code
is inspected at exact other-lineage sources, not presumed present because
ignored bytecode directories happen to exist on disk.

## 3. Scientific objects and their meanings

| Object | Declared meaning | Not the same as |
|---|---|---|
| Physical stock `x_i` | Quantity of the one represented homogeneous resource | Money, EBU balance, marginal burden |
| Reference `x_i*` | Declared functional reference for the model | Automatically an empirical mean, ethical optimum, or dynamic equilibrium |
| Scale `sigma_i > 0` | Declared reference width in stock units | Automatically measurement error or fitted standard deviation |
| Potential `V` | Dimensionless standardized squared deviation in this model | Conserved mass, thermodynamic free energy, total social welfare |
| Marginal `mu_i` | Derivative of the declared potential | An instruction that forces an actor to act |
| Finite value `E_G` | Before/after potential difference minus separately declared process burden | Price, a physical conserved token, causal entitlement |
| Path attribution `R_a` | Exact decomposition under a declared common path | Unique measured contribution, fairness or ownership |
| Balance `B_i >= 0` | Proposed persistent experimental action capacity | Physical installed capacity, stock reserve, real-world entitlement |
| External audit `J` | Signed cumulative deviation change due to forcing | Spendable balance or an actor reward |

Use distinct names for old C3 export budget and new capacity balance; the old
symbol `B` cannot transfer meaning by spelling alone. `R_eff` remains a stock
quantity in its historical P1C source; it is neither Gaussian scale nor the
homeostatic reserve `R` nor the new path attribution `R_a`.

## 4. Potential family and first prospective physical domain

The historical hinge family remains valid within its original definitions:

\[
v_i(x_i)=\alpha_i[L_i-x_i]_+^2+\beta_i[x_i-U_i]_+^2
          +\chi_i[R_i-x_i]_+^2.
\]

It is not globally replaced by a theorem saying nature is Gaussian. The new
candidate family is

\[
V_i(x_i)=\tfrac12((x_i-x_i^*)/\sigma_i)^2,\quad
V(x)=\sum_i V_i(x_i),\quad
\mu_i=(x_i-x_i^*)/\sigma_i^2.
\]

The first programme assumes a finite number of cells, nonnegative stock,
fixed positive scales, fixed nonnegative references, one homogeneous
conserved scalar, lossless internal transfer, and compatible mass
`sum(x_i*) = M = sum(x_i)`. This makes the reference physically compatible;
it does not establish its reachability through the action menu or dynamics.
No Allee term, lower/upper homeostatic bands, regeneration, autonomous
restoring flow, service optimizer, or Ornstein–Uhlenbeck mean reversion is
silently included. No parameter values are chosen here.

`Gaussian` describes reference geometry. The quadratic is the relative
negative log of an unnormalized Gaussian shape with its minimum removed.
On the nonnegative fixed-mass domain this is not automatically a product
probability law for actual states. Conservation couples coordinates even
when the declared Hessian is diagonal. Do not replace `V` with `1-exp(-V)`:
that changes both the field and finite values.

## 5. Finite actions and local evaluation

For finite source-side **quantity** `q_a`, write `delta_a = S_a q_a`. If an
older source uses a rate, write `delta_a = Delta t S_a rate_a` and convert
explicitly. Do not add a timestep twice or omit it because a fixture used 1.
The group increment is `delta_G = sum_a delta_a`, evaluated from one frozen
pre-action baseline `z` after that epoch's forcing.

General finite accounting:

\[
E_G=V_{\rm loc}(z)-V_{\rm loc}(z+\delta_G)-C_G.
\]

Here `V_loc` includes every affected factor; unchanged factors cancel. The
ideal first model declares `C_G=0`. A later nonzero process burden must
identify physical action burden not already represented through the state
and evaluated potential. Loss cannot disappear merely because it is absent
from `V`. Loss-aware worlds still need explicit carriers/sinks/boundaries.
The existing loss-aware runtime gap is not solved by this lossless plan.

A physical transformation chain remains a linked chain of atomic actions,
not a mega-action concealing fuel, electricity, delivery and water movement.
No extra burden is invented solely because upstream/downstream actions exist.

## 6. Conditional algebra checked for exposition, not a recovery theorem

Let `H=diag(1/sigma_i^2)` with fixed references/scales and additive increments.
Expansion of the quadratic gives

\[
V(z+\delta)=V(z)+\mu(z)^T\delta+\tfrac12\delta^TH\delta,
\qquad E_G=-\mu(z)^T\delta_G-\tfrac12\delta_G^TH\delta_G.
\]

This is exact algebra, not a first-order approximation. At `z=x*`, nonzero
**net** `delta_G` has negative value. A nonempty group whose increments
cancel has `delta_G=0`; do not confuse group membership with net change.
In the ideal cost-free model such cancellation can have zero value; this is
not a claim that real movements are free.

For the declared straight path `z+s delta_G`, `0<=s<=1`, define

\[
R_a=-\int_0^1\nabla V(z+s\delta_G)^T\delta_a\,ds
   =-\mu(z)^T\delta_a-\tfrac12\delta_a^TH\delta_G.
\]

Linearity and the fundamental theorem of calculus give

\[
\sum_aR_a=E_G\quad(C_G=0).
\]

The sign convention is explicit: this is the **negative** derivative
integral, because positive EBU means lower potential. If the physical model
realizes that constant-rate path, it is a decomposition of that model path.
If only endpoints are specified, it is a declared interpolation convention.
The two interpretations share arithmetic, not authority. Neither establishes
ownership, fairness, causal contribution or spending permission.

Sequential endpoint differences telescope under one fixed potential and
consistent complete states; external changes and process burdens must be
accounted separately. Historical V3 no-overissue theorems retain their own
one-action and other assumptions. The new group identity does not silently
rewrite those theorem statements.

### Interaction diagnostic boundary

For `F(A)=V(z)-V(z+sum_{a in A}delta_a)` with the same fixed increments,
baseline and potential, the pair Möbius term is

\[
m_{ab}=-\delta_a^TH\delta_b.
\]

Terms of order three and above vanish for this quadratic **set function**.
This is not a universal claim about physical groups. If each subset reruns
a resolver and obtains different increments, that degree argument no longer
applies. Boolean-lattice diagnostics require every relevant subset to be
admissible; otherwise use an explicitly justified alternative or refuse.
Möbius is optional research analysis, not runtime settlement or extra issuance.

Physical-edge topology, potential-factor topology and action-interaction
topology are separate. Shared coordinates can create interaction even for a
diagonal potential; a dense multivariate Gaussian is not required.

## 7. Capacity proposal and external accounting

The handover proposes persistent per-owner nonnegative balances with zero
genesis. For a declared ownership map, sum the signed child attributions
owned by `i` into `Delta B_i`. A group is affordable only if every affected
owner satisfies `B_i + Delta B_i >= 0` under the registered numerical rule.
Same-event netting is part of the proposed policy; it is not derived from
the group closure theorem. No borrowing, refill, direct balance transfer,
global pool, free initial spending, or positive-only issuance is introduced.

Forcing changes `x_t` to `z_t` conservatively before the action epoch. Define

\[
D_{{\rm ext},t}=V(z_t)-V(x_t),\quad
J_{t+1}=J_t+D_{{\rm ext},t},\quad
\sum_i\Delta B_{i,t}=V(z_t)-V(x_{t+1}).
\]

Adding the two differences gives the conditional accounting invariant

\[
V(x_{t+1})+\sum_iB_{i,t+1}-J_{t+1}
=V(x_t)+\sum_iB_{i,t}-J_t=K.
\]

With `x_0=x*`, zero balances and zero audit, `K=0`. `D_ext` and `J` are
signed; a disturbance that lowers deviation is not an accounting error.
Forcing earns no actor balance. Exact cancellation establishes this invariant
under the declared update rules, not the legitimacy or efficacy of the rules.

After a single shock and no more forcing, `J` is fixed and balances can
exchange with deviation subject to nonnegativity. The identity permits
cycles, trapping or refusal; it does not force recovery. With continuing
forcing, the physical state may have a stationary distribution while
`B`/`J` drift. Any claim about a stationary **augmented** process must address
those accounts separately.

## 8. Actor and comparator separation

Intended later ordering:

`external forcing -> frozen state -> EBU-blind candidates/groups -> joint
physical feasibility -> exact value/attribution -> owner affordability ->
unweighted random choice -> exact selected execution -> settlement/audit`.

Nature and actor choices use independently addressed random streams. A
proposal stream, if needed, is separately declared. No random seed, horizon,
distribution parameter or outcome threshold is frozen here.

The physical-random control uses the same declared physical rules and menu
construction but no capacity affordability restriction. Neither arm ranks by
EBU, global `V`, target proximity or service. A future protocol must state
precisely how empty menus, no-action choices, group multiplicity, duplicate
groups, retries and actor/group sampling units are handled.

Paired raw forcing draws do not necessarily produce equal applied forcing
after states diverge: state-dependent feasibility rejection can change the
realized disturbance. The later protocol must distinguish common raw draws
from common physical inputs and report any exposure difference. Do not
silently promise both by saying “same seed.”

Finite candidate menus are experimental menu restrictions, not proof that
all physically divisible quantities have been enumerated. Local valuation
does not prove a global group-choice mechanism is decentralized. Group
assembly, selector information and per-owner authorization need their own
explicit locality statements.

## 9. What changes, what survives

| Material | Disposition for new work |
|---|---|
| Historical D0/P1C, finite quote, result artifacts | Preserve unchanged; original assumptions/results remain scoped |
| Generic framework identities, provenance, typed state/actions, ledgers | Reuse candidates under F2; not copied or executed this stage |
| Old threshold-coupled study world and C0–C4 code | Preserve as superseded prospective implementation; do not relabel Gaussian |
| C5/Direction C service-face proposals | Superseded prospective design, not the new actor policy |
| N/H/X and old long-horizon cost/launch documents | Not active; no delete needed to remove their authority |
| Stage D/E/F SD programme | Source-locked separate programme, not automatic Gaussian execution permission |
| Books I–III PDFs | Preserve; major new I architecture, targeted future II/III compatibility notes only |
| Old electrical/wave/superposition book gates | Do not revive; retain the newer canonical topology/motif replacement |
| Later feedback, mass bridge, identification and oscillator proposals | Preserve as domain/actor research candidates; no hidden restoring plant |

## 10. Exact remaining decisions and stop gates

| ID | Proposition or contract requiring a later explicit decision | Why not guessed now |
|---|---|---|
| G1 | Recognized Gaussian forcing-first event profile versus framework ten-phase order | Existing specification fixes a different chronology |
| G2 | `owner(a)` and receipt-to-capacity mapping, signed group netting, path semantics | Closure does not define legal/model ownership or spendability |
| G3 | Actor/group assembly and selection locality, duplicate/menu/no-action semantics | These choices change the stochastic process |
| G4 | Forcing distribution, feasibility handling and paired-control coupling | Same raw draws need not yield same applied drive |
| G5 | Metrics, falsifiers, numerical representation and preregistered comparison | Boundedness alone is structurally guaranteed on a fixed simplex |
| G6 | Stage A acceptance criteria and separate authority to begin Stage B | One impulse study does not authorize ongoing stochastic execution |
| B1 | Locate original Book I sources, or authorize a new source edition | PDF identity does not imply reproducible manuscript provenance |

These are specific later-stage gates, not a demand for the author to choose
every implementation detail now. Routine documentation reconciliation and
conditional derivation can proceed. Stop only the stage that needs the
missing decision; do not invent it or bury it in code.

### Boundedness is not the scientific question

For finite `n`, `0<=x_i<=M`, fixed finite references and `sigma_i>0`,

\[
V(x)\le\tfrac12\sum_i
\frac{\max\{(x_i^*)^2,(M-x_i^*)^2\}}{\sigma_i^2}<\infty.
\]

Thus both arms are bounded before any EBU benefit is established. Useful
future comparisons concern recovery, occupation away from the reference,
cycling, refusal, distribution and exposure—not unbounded divergence in
this closed fixed-mass model. This is a model-domain correction, not a
parameter change or an outcome-based adjustment.

## 11. Completion meaning

Reconciliation can establish a coherent documented direction and preserve
history. It cannot supply unexecuted results. Book I can explain definitions,
motivation and conditional identities now, without claiming the proposed
random-affordable economy maintains life or has passed scientific tests.
The detailed next-stage gates are in the
[implementation roadmap](LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md).
