# SD-01: two required scientific control bindings

SD-01 is **not sealable**. This record requests no new runs or thresholds and
selects no defaults. It resolves only the analysis of
`STAGE_F_SD01_ADAPTER_AND_RUN_ID_CLOSURE`, from base
`6078febefb8f082a76a0b9fc6c61331b14743aca`.

1. **SD01-CONTROL-TUPLES:** Supply the exact demand, shock schedule and H-policy
   (including eta if H2) for each of the four already registered control
   trajectories. The matrix fixes logistic x0=15, d=0 and both rho values;
   the paired Allee controls fix x0=4 and no external inflow, but their demand,
   policy and shock binding is not explicit. Policy labels affect viability
   predicates and H3 can have no action; equal zero-demand stock paths would
   not justify choosing their policy labels silently. An H3 assignment also
   needs reconciliation with the frozen 39,120,000 evaluations, whose arithmetic
   counts 32 H3 scientific cells and no control H3 checks. Preserve four controls.
2. **SD01-CONTROL-ASSERTION-MAPPING:** Name the exact existing cells and frozen
   predicates implementing “accepted safe policy” in the low-demand positive
   control and “demand above feasible regeneration must not be reported viable”
   in the negative control. The latter must be reconciled with stock-set
   viability, which does not itself require fully served demand. Choosing a
   demand-feasibility definition or a new service threshold changes the
   scientific interpretation and is not an adapter repair.

Sources: `stage_d_scientific_validation_master_matrix.json`, SD-01
`configuration.parameters`, `positive_controls`, `negative_controls`, `seeds`,
and `computational_feasibility.exact_problem_size`;
`STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md` §4.1; Stage E §5 prohibits
filling missing authority by default. Matrix ancestor revisions `db5440a`,
`96c9391`, `1a63d08`, and `8936bb4` do not supply these bindings.
The dossier retains exact source identities/hashes and the frozen scientific
row and operational projections; full source bytes remain at the pinned Git commit.

H3 empty-set behavior needs no new decision: retain recursive-feasibility
failure and stop where no selected action exists; do not invent zero service.
The invariance wording is read as x_t and x_(t+1), not the intermediate
regenerated x_pre. No new scientific predicate has been adopted.

A prospective control-binding amendment and independent review are required
before the adapter, complete v2 records, cloud binding, and authorization can
be sealed. No scientific workload, AWS-C0 work, result or interpretation was
executed in this preparation.
