# EBU Stage F route-level binding authority correction

Status: **PROSPECTIVE, ADDITIVE, OUTCOME-BLIND AUTHORITY CANDIDATE ONLY**

Authority ID: `EBU-STAGE-F-ROUTE-LEVEL-BINDING-CORRECTION-v1`

Required target: commit `9f7d217d04a201e98611580a1a0d0be88f188143`, tree
`1136341a84fa30de269bf2bc0486f70e19d5dc05`.

`STAGE_F_ROUTE_LEVEL_BINDING_CORRECTION_CANDIDATE_COMPLETE`

## Narrow correction

The campaign order remains `SD-01`, nested `SD-01-GROWTH-v1`, then `SD-02`
through `SD-14`.  The order is an ordered queue, not a requirement that every
route be simultaneously sealable before the first route packet may be
considered.  A **sealed route packet**, rather than the complete campaign
packet, is the smallest execution-binding unit.

This correction supersedes only the complete-campaign prerequisite in the
Stage F packet gate.  It does not modify any study, hypothesis, model, input,
parameter, seed, stream, control, threshold, outcome rule, hard cap,
continuation rule, scientific authority, institutional authority, or existing
unresolved-authority gap.  It does not turn a named future authority into an
identity.

## Per-route gate

A route can be `SEALED` only when its exact inherited authority projection has
zero gaps, its own frozen packet passes deterministic validation, a separate
independent binding audit records `INDEPENDENT_BINDING_PASS`, its packet names
a hard route-level cost cap and result-S3 layout, and the exact protocol
permits execution.  Otherwise it is `BLOCKED_AUTHORITY_GAP` and has no
execution identity.  A route-level PASS is not a campaign PASS.

Execution is still separately prohibited until all those route-local facts
exist.  This authority does not authorize runner import, model advance,
trajectory, stochastic draw, outcome inspection, result production, release,
or publication.

## Dependencies

`SD-01-GROWTH-v1` is a nested subcampaign of `SD-01`, not an independent
fifteenth study, and cannot start before the fixed SD-01 route has an accepted
disposition. `SD-14` remains last and requires accepted dispositions for
SD-01 through SD-13. Other routes retain their inherited dependencies. A
blocked route does not allow a dependent route to proceed.

## Scope and evidence

This candidate adds exactly the six files named in
`stage_f_route_level_binding_correction_contract.json`; no existing path is
modified. The subsequent, separately reviewed implementation may add only the
paths declared in its implementation manifest. It must build deterministic
route packets and a programme ledger from committed authority bytes, preserve
all recorded gaps exactly, and refuse a packet that claims execution without
the route-local conditions above.

The correction is effective only after independent audit, normal local
integration, and a committed validation PASS.
