# SD-01 prospective control-binding authority draft

Status: **STATIC_DERIVATION_ONLY — BINDING_NOT_DERIVABLE**.
Draft ID: `SD01-CONTROL-DERIVATION-v1`.
Starting commit: `db448403da2c7c16ae62479e88bb748e377820e1`.

The attached [derivation](SD01_CONTROL_DERIVATION.md) proposes:

- Four already-registered controls: logistic rho=3/10 and 3/5 at x0=15,
  and Allee rho=3/10 and 3/5 at x0=4; each with d=0, H1 and no shocks.
- One existing positive-control cell: logistic rho=3/10, demand ratio1/4,
  d=9/32, H1, no shocks, x0=15, assessed using the frozen predicates.
- One existing high-demand candidate: Allee rho=3/10, demand ratio5/4,
  d=45/16, H1, no shocks, x0=15. Its existing ledgers distinguish stock-set
  viability from inability to serve full demand.

These exact candidate mappings have mathematical justifications but are not
uniquely selected by the frozen sources. H1/H2_eta=1 equivalence, control shock
and Allee-demand alternatives, a second safe logistic cell, and the undefined
composition of demand feasibility with the overall viability label prove the
missing semantic bindings. The derivation states each missing rule precisely.
No alternative is selected by preference.

Approval accepts the exact arithmetic, candidate derivations and non-uniqueness
findings in the attached report and checks. It does **not** adopt an unstated
selector, substitute service shortfall for a stock predicate, alter the
negative-control wording, bind the candidate tuples for execution, or close
`STAGE_F_SD01_ADAPTER_AND_RUN_ID_CLOSURE`.

All frozen hypotheses, 192 scientific cells, four additional controls, demand
ratios, seeds, policies, thresholds, horizons, checkpoint rules, expected
counts, output requirements, numerical policy and interpretation rules remain
unchanged. The exact-real proofs are not binary64 conformance or observed
scientific outcomes. No scientific workload or AWS-C0 work occurred.

The independent review is retained in `SD01_CONTROL_BINDING_REVIEW.md`.
Complete scientific control binding remains non-derivable under the instruction
to add no semantic rule or interpretation. Scientific execution still requires
a later complete sealed packet and its separate exact user authorization.
