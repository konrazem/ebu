# EBP V3.0 Gate 1D-C — Finalized Execution Manifest

## 1. Completion status

This manifest is the sole full-study completion sentinel. The summary is only the runner-output completion sentinel; summary plus trace never constitutes a finalized study.

The durable execution receipt proves that the sole authorized scientific attempt was committed before scientific execution became reachable.

| Field | Value | Source |
| --- | --- | --- |
| Study state | FINALIZED | contract state machine |
| Attempt ID | gate1dc-single-authorized-attempt | execution receipt |
| Execution SHA | 8793bda07ff7470c6362d2ef3b21c41825ae98ed | execution receipt; must equal summary:/execution_sha |
| Runner completion sentinel | results/v3.0/gate1dc/v30_gate1dc_summary.json | contract artifact inventory |
| Full-study completion sentinel | results/v3.0/gate1dc/MANIFEST.md | contract artifact inventory |
| Registered runs | 30 | summary:/n_runs; exact 30 |
| Trace rows | 6000 | validated trace count |
| Single scientific attempt | true | receipt exists; no retry path |

## 2. Provenance and source locks

The original protocol and plan retain precedence over all scientific content. The execution/finalization addendum governs only the prospective operational mechanics explicitly identified there.

Any scientific conflict would have caused fail-closed refusal.

| Order | Source | SHA-256 |
| --- | --- | --- |
| 1 | AGENTS.md | 2538964de3ff0b328ce5b10efa4396a0f870f6f10b6d31b86d174cc607d8820e |
| 2 | V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md | 3122aa673f47290bbee866feb56d16afc4540f552ed7c7b458f097ef4e44d04f |
| 3 | v30_gate1dc_outcome_discrimination_plan.json | 91a2c42558c09051988bfebe6f0d11c0fab440340d161171afc4442c86fa30fe |
| 4 | V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md | 28d47aa314e74206b4cc3da9ceccfbf0a08bd2196930490636c1d3c991039fa1 |
| 5 | v30_gate1dc_execution_finalization_contract.json | 81d96d3f377a2d1d2471b38328af8968b9c728db590023d0d921e4312cd23155 |
| 6 | V3.0_GATE1D_C_MACOS_ENVIRONMENT_COMPATIBILITY_ADDENDUM.md | 2e439afad6ba7532aae83631ef4fb7ea6648980be035674f8e2d13faeecd9b51 |
| 7 | v30_gate1dc_macos_environment_compatibility_contract.json | 628ee126011b3bdb6587af53c64f69db2fbd86d92deaef27ff60366b4d80ef8b |
| 8 | V3.0_GATE1D_C_MACOS_PYTHON_LAUNCHER_COMPATIBILITY_ADDENDUM.md | d81afc5d77e1d2c7ccd9ceaae44d96ce33ddbb85ddc35fe0a0a0e1141394e8c3 |
| 9 | v30_gate1dc_macos_python_launcher_compatibility_contract.json | b937e0ed047799fbcce9d6390ca2836b0db6ca18c0a2b8ab854f89395bd79c82 |
| 10 | gate1dc_v30.py | 33ebb3c83d5a4cb6653012e71fe1f5bd3929eb7efe7488f1ce1851134707cf80 |
| 11 | test_v30_gate1dc.py | 1f143f1d3d73cea2f8ec192b257d77a9e0c12635c36c66dd82d9422f188ff9e4 |
| 12 | exp_v30_gate1dc.py | 89b8016c2017839faaee38b172f6041ca2d987669db448ffa260399cb872deb2 |
| 13 | finalize_v30_gate1dc.py | f4c7af1415d38e753aacf1be644047d6744cefaa36da9bc87042cc1946db2e85 |
| 14 | d0_v29.py | f7fdce8d946b44b4e0bfab9338fcd5c378796f9d14cd80323c53732e08a3bfe9 |
| 15 | p1c_v29.py | a30c869000080b4b0235a9ba1daa517a5b0fe734ba55ac423ae3042da5940729 |
| 16 | ebu_quote_v30.py | 44a2ea282837f7613198a06a7037fb89f2f9fd99f05cedde65e0b1ba726e1b79 |
| 17 | service_v30.py | a83bcd5e449b8804f44607e56326ec392324cdfed71260e28fdc4c48899d44e0 |

## 3. Artifact integrity

MANIFEST.md does not contain its own hash. The finalizer verifies it by rendering the expected bytes twice, atomically publishing them, and reopening for byte identity. The result commit records the manifest as a Git blob; post-commit verification uses the commit tree and git hash-object without recursive self-hashing.

| Order | Role | Path | Bytes | SHA-256 |
| --- | --- | --- | --- | --- |
| 1 | control | results/v3.0/gate1dc/v30_gate1dc_execution_receipt.json | 3202 | f76d25c66bc251e5becfe18cfb883548bd3a8de297eafdf6e6e9fbd056b44a4e |
| 2 | control | results/v3.0/gate1dc/v30_gate1dc_execution_started.json | 349 | 82b134e6d80c6ecd09ed607f2baf256c848bae58f8171ddfca0054a3ef26cfff |
| 3 | runner-output | results/v3.0/gate1dc/v30_gate1dc_trace.jsonl.gz | 1534620 | 9463e2d18adffd5374f005c2123e23849ae810e3251eccb4f3f5aa61b73a5783 |
| 4 | runner-output | results/v3.0/gate1dc/v30_gate1dc_stdout.txt | 5299 | 7aa3bc09a4948ea32200c49dc18810a808bc9d0917851e75f9dc5a9b1bc4bf85 |
| 5 | runner-output completion sentinel | results/v3.0/gate1dc/v30_gate1dc_summary.json | 117304 | e1e1cc6b6ed3f9ae84cf43197e66cc2c36716e51279d3a0192272a6ceff6f375 |
| 6 | full-study completion sentinel | results/v3.0/gate1dc/MANIFEST.md | verified by deterministic render and Git blob | not self-hashed |

## 4. Frozen execution inventory

Inventory verification: exactly 30 unique runs in frozen world × timestep × arm order, exactly 200 trace rows per run, ticks 1 through 200, and exactly 6,000 rows overall.

| # | Run ID | Summary record | Trace rows | Tick range |
| --- | --- | --- | --- | --- |
| 1 | DC1_flux_lock\|A_full_multi_edge_p1c\|conservative | present | 200 | 1–200 |
| 2 | DC1_flux_lock\|B_restricted_matched_non_ebu\|conservative | present | 200 | 1–200 |
| 3 | DC1_flux_lock\|C_restricted_observational_quote\|conservative | present | 200 | 1–200 |
| 4 | DC1_flux_lock\|D_restricted_exact_total_quote_greedy\|conservative | present | 200 | 1–200 |
| 5 | DC1_flux_lock\|S_restricted_local_service_priority\|conservative | present | 200 | 1–200 |
| 6 | DC1_flux_lock\|A_full_multi_edge_p1c\|near_certificate | present | 200 | 1–200 |
| 7 | DC1_flux_lock\|B_restricted_matched_non_ebu\|near_certificate | present | 200 | 1–200 |
| 8 | DC1_flux_lock\|C_restricted_observational_quote\|near_certificate | present | 200 | 1–200 |
| 9 | DC1_flux_lock\|D_restricted_exact_total_quote_greedy\|near_certificate | present | 200 | 1–200 |
| 10 | DC1_flux_lock\|S_restricted_local_service_priority\|near_certificate | present | 200 | 1–200 |
| 11 | DC2_capacity_split\|A_full_multi_edge_p1c\|conservative | present | 200 | 1–200 |
| 12 | DC2_capacity_split\|B_restricted_matched_non_ebu\|conservative | present | 200 | 1–200 |
| 13 | DC2_capacity_split\|C_restricted_observational_quote\|conservative | present | 200 | 1–200 |
| 14 | DC2_capacity_split\|D_restricted_exact_total_quote_greedy\|conservative | present | 200 | 1–200 |
| 15 | DC2_capacity_split\|S_restricted_local_service_priority\|conservative | present | 200 | 1–200 |
| 16 | DC2_capacity_split\|A_full_multi_edge_p1c\|near_certificate | present | 200 | 1–200 |
| 17 | DC2_capacity_split\|B_restricted_matched_non_ebu\|near_certificate | present | 200 | 1–200 |
| 18 | DC2_capacity_split\|C_restricted_observational_quote\|near_certificate | present | 200 | 1–200 |
| 19 | DC2_capacity_split\|D_restricted_exact_total_quote_greedy\|near_certificate | present | 200 | 1–200 |
| 20 | DC2_capacity_split\|S_restricted_local_service_priority\|near_certificate | present | 200 | 1–200 |
| 21 | DC3_demand_pulse\|A_full_multi_edge_p1c\|conservative | present | 200 | 1–200 |
| 22 | DC3_demand_pulse\|B_restricted_matched_non_ebu\|conservative | present | 200 | 1–200 |
| 23 | DC3_demand_pulse\|C_restricted_observational_quote\|conservative | present | 200 | 1–200 |
| 24 | DC3_demand_pulse\|D_restricted_exact_total_quote_greedy\|conservative | present | 200 | 1–200 |
| 25 | DC3_demand_pulse\|S_restricted_local_service_priority\|conservative | present | 200 | 1–200 |
| 26 | DC3_demand_pulse\|A_full_multi_edge_p1c\|near_certificate | present | 200 | 1–200 |
| 27 | DC3_demand_pulse\|B_restricted_matched_non_ebu\|near_certificate | present | 200 | 1–200 |
| 28 | DC3_demand_pulse\|C_restricted_observational_quote\|near_certificate | present | 200 | 1–200 |
| 29 | DC3_demand_pulse\|D_restricted_exact_total_quote_greedy\|near_certificate | present | 200 | 1–200 |
| 30 | DC3_demand_pulse\|S_restricted_local_service_priority\|near_certificate | present | 200 | 1–200 |

## 5. Positive controls PC1–PC4

F4 remains exactly: certified_lower_bound - 1e-9 * (1 + abs(certified_lower_bound)). There is no second slack floor, tuning interval, or rerun permission.

| Control | Timestep | Measured as | Certified lower bound | F4 threshold | Executed value | F4 fired |
| --- | --- | --- | --- | --- | --- | --- |
| PC1_DC1_S_starves_dst2 | conservative | post-burn-in cumulative dst2 unmet of S minus post-burn-in cumulative dst2 unmet of B | 15.564565327910522 | 15.564565311345957 | 19.064565327910522 | false |
| PC1_DC1_S_starves_dst2 | near_certificate | post-burn-in cumulative dst2 unmet of S minus post-burn-in cumulative dst2 unmet of B | 30.816217590238942 | 30.816217558422725 | 34.31621759023894 | false |
| PC2_DC3_S_misses_pulses | conservative | window pulse-tick cumulative dst2 unmet of S minus window pulse-tick cumulative dst2 unmet of B | 5.5 | 5.4999999935 | 6.0 | false |
| PC2_DC3_S_misses_pulses | near_certificate | window pulse-tick cumulative dst2 unmet of S minus window pulse-tick cumulative dst2 unmet of B | 5.5 | 5.4999999935 | 6.0 | false |
| PC3_DC1_A_vs_B_capability_cost | conservative | post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B | 18.427051868293074 | 18.42705184886602 | 63.86407266407291 | false |
| PC3_DC1_A_vs_B_capability_cost | near_certificate | post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B | 28.012116339140597 | 28.01211631012848 | 108.30487466130812 | false |
| PC4_DC2_A_vs_B_capacity_gap | conservative | post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B | 7.476597260519597 | 7.476597252043 | 32.42852345773769 | false |
| PC4_DC2_A_vs_B_capacity_gap | near_certificate | post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B | 25.384451045418373 | 25.38445101903392 | 57.802096325434135 | false |

## 6. Hypotheses H1–H10

| Hypothesis | Frozen preregistered statement | Status | Evidence |
| --- | --- | --- | --- |
| H1 | B and C are physically byte-identical at every tick of every paired run | supported | {"non_identical_pairs":[]} |
| H2 | instrument sensitivity: discriminator_v2's primary channels are certified in DC1/DC2 at both timesteps by PC3/PC4; DC3 sensitivity is independently certified by the secondary per-destination PC2 channel. PC2 is not silently relabelled as a primary D-vs-B discriminator channel | supported | {"PC2":{"conservative":{"certified_lower_bound":5.5,"control":"PC2_DC3_S_misses_pulses","dt_label":"conservative","executed_value":6.0,"f4_fired":false,"f4_threshold":5.4999999935,"measured_as":"window pulse-tick cumulative dst2 unmet of S minus window pulse-tick cumulative dst2 unmet of B"},"near_certificate":{"certified_lower_bound":5.5,"control":"PC2_DC3_S_misses_pulses","dt_label":"near_certificate","executed_value":6.0,"f4_fired":false,"f4_threshold":5.4999999935,"measured_as":"window pulse-tick cumulative dst2 unmet of S minus window pulse-tick cumulative dst2 unmet of B"}},"discriminating_world_timestep_pairs":["DC1_flux_lock\|conservative","DC1_flux_lock\|near_certificate","DC2_capacity_split\|conservative","DC2_capacity_split\|near_certificate","DC3_demand_pulse\|conservative","DC3_demand_pulse\|near_certificate"]} |
| H3 | every positive control (PC1-PC4) meets or exceeds its certified lower bound (the F4 threshold) | supported | {"failed_positive_controls":[]} |
| H4 | the one-action restriction binds where intended: arm A executes >= 2 simultaneous positive deliveries in every world, and the certified A-vs-B costs appear in DC1 and DC2 | supported | {"PC3":{"conservative":{"certified_lower_bound":18.427051868293074,"control":"PC3_DC1_A_vs_B_capability_cost","dt_label":"conservative","executed_value":63.86407266407291,"f4_fired":false,"f4_threshold":18.42705184886602,"measured_as":"post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B"},"near_certificate":{"certified_lower_bound":28.012116339140597,"control":"PC3_DC1_A_vs_B_capability_cost","dt_label":"near_certificate","executed_value":108.30487466130812,"f4_fired":false,"f4_threshold":28.01211631012848,"measured_as":"post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B"}},"PC4":{"conservative":{"certified_lower_bound":7.476597260519597,"control":"PC4_DC2_A_vs_B_capacity_gap","dt_label":"conservative","executed_value":32.42852345773769,"f4_fired":false,"f4_threshold":7.476597252043,"measured_as":"post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B"},"near_certificate":{"certified_lower_bound":25.384451045418373,"control":"PC4_DC2_A_vs_B_capacity_gap","dt_label":"near_certificate","executed_value":57.802096325434135,"f4_fired":false,"f4_threshold":25.38445101903392,"measured_as":"post-burn-in cumulative total service of A minus post-burn-in cumulative total service of B"}},"max_simultaneous_actions_A":{"DC1_flux_lock":2,"DC2_capacity_split":3,"DC3_demand_pulse":2}} |
| H5 | OPEN OUTCOME (never analytically forced): whether D's post-burn-in service equals, exceeds or falls below B's - on totals and per destination - in each world; the registered threshold analysis predicts directions in DC1/DC3 but those predictions are themselves falsifiable in-run and their failure is a reportable finding, not a defect | open_outcome | {"DC1_flux_lock\|conservative":{"service_D_minus_B":29.81209964412811,"unmet_D_minus_B_by_destination":[0.0,-29.81209964412811,0.0]},"DC1_flux_lock\|near_certificate":{"service_D_minus_B":51.59786476868328,"unmet_D_minus_B_by_destination":[0.0,-51.597864768683266,0.0]},"DC2_capacity_split\|conservative":{"service_D_minus_B":6.304295295011407,"unmet_D_minus_B_by_destination":[0.0,0.0,0.0,-6.304295295011406]},"DC2_capacity_split\|near_certificate":{"service_D_minus_B":10.21058593642853,"unmet_D_minus_B_by_destination":[0.0,0.0,0.0,-10.21058593642853]},"DC3_demand_pulse\|conservative":{"service_D_minus_B":6.879715302491093,"unmet_D_minus_B_by_destination":[0.0,-6.8797153024911,0.0]},"DC3_demand_pulse\|near_certificate":{"service_D_minus_B":7.22370106761565,"unmet_D_minus_B_by_destination":[0.0,-7.22370106761565,0.0]}} |
| H6 | D preserves P1C reserves with zero material crossings and zero physical overuse | supported | {"D_harm_runs":[]} |
| H7 | every verdict is consistent across the conservative and near-certificate timesteps | supported | {"DC1_flux_lock":{"consistent":true,"total_alignment_failure_conservative":false,"total_alignment_failure_near_certificate":false},"DC2_capacity_split":{"consistent":true,"total_alignment_failure_conservative":false,"total_alignment_failure_near_certificate":false},"DC3_demand_pulse":{"consistent":true,"total_alignment_failure_conservative":false,"total_alignment_failure_near_certificate":false}} |
| H8 | B and D select different candidates somewhere: at t0 in DC2 (registered provable divergence) and in the threshold region x2 in (xbar_D, xbar_B) of DC1/DC3 | supported | {"DC2_t0_divergence":{"conservative":true,"near_certificate":true},"pair_divergence":{"DC1_flux_lock\|conservative":true,"DC1_flux_lock\|near_certificate":true,"DC2_capacity_split\|conservative":true,"DC2_capacity_split\|near_certificate":true,"DC3_demand_pulse\|conservative":true,"DC3_demand_pulse\|near_certificate":true}} |
| H9 | all unmet demand is exposed explicitly (DC1/DC3 dst1 structural unmet; DC2 restricted-capacity shortfall); no phantom service, no hidden deficit | supported | {"negative_corrections":0.0,"total_unmet":2294.8856986119704} |
| H10 | the flow-revealing pinning invariant holds: x_dst1(t) = 0 at every tick of every DC1/DC3 run (registered analytic invariant, falsifiable in-run) | supported | {"pinning_violations":[]} |

## 7. Falsifiers F1–F16

| Falsifier | Frozen preregistered statement | Fired | Evidence |
| --- | --- | --- | --- |
| F1 | arm C changes any physical value versus arm B at any tick | false | [] |
| F2 | B/C/D/S menus, candidate quantities, budgets or timesteps differ at any tick (per-tick capability-identity assertion) | false | [] |
| F3 | F13-SYMMETRIC: all primary worlds are non-discriminating - no world-timestep pair exceeds tolerance on any discriminator_v2 channel | false | {"discriminating_world_timestep_pairs":["DC1_flux_lock\|conservative","DC1_flux_lock\|near_certificate","DC2_capacity_split\|conservative","DC2_capacity_split\|near_certificate","DC3_demand_pulse\|conservative","DC3_demand_pulse\|near_certificate"]} |
| F4 | INSTRUMENT FAILURE: any positive-control executed value falls below its certified lower bound minus the frozen numerical tolerance (the static sensitivity analysis was wrong) | false | [] |
| F5 | PLATEAU: every destination is demand-saturated (service = demand) for every executed arm at every measurement-window tick of an anti-plateau world (DC1/DC3) | false | [] |
| F6 | CAPABILITY: arm A never executes >= 2 simultaneous positive deliveries in any primary world (the intended restriction never binds) | false | {"DC1_flux_lock":2,"DC2_capacity_split":3,"DC3_demand_pulse":2} |
| F7 | CHOICE: the selected-candidate series of B and D are identical at every tick of every run (intended divergence never occurs) | false | {"DC1_flux_lock\|conservative":true,"DC1_flux_lock\|near_certificate":true,"DC2_capacity_split\|conservative":true,"DC2_capacity_split\|near_certificate":true,"DC3_demand_pulse\|conservative":true,"DC3_demand_pulse\|near_certificate":true} |
| F8 | a protected reserve is materially crossed (corrected Gate 1D-A tolerance) or physical overuse occurs while the theorem assumptions are reported satisfied, or any Allee crossing occurs | false | [] |
| F9 | any production arm ranks candidates by EBU per unit | false | {} |
| F10 | the decision path reads forbidden information, including ANY demand-schedule value for a tick other than the current one | false | {"note":"decision-path AST and current-demand poison probes are mandatory pre-execution validation; locked test/source hashes were enforced before execution"} |
| F11 | any run uses r_dt > 1 (uncertified timestep) | false | [] |
| F12 | any parameter, threshold or predicate changes after outcome inspection (post-result adjustment) | false | {"note":"frozen plan/protocol/implementation/test hashes enforced before execution; no runtime scientific options exist"} |
| F13 | any trajectory, step-function call, runner invocation or outcome-inspecting parameter search is found to have produced this preregistration (audit falsifier over the repository history and the registered derivations) | false | {"note":"preregistration provenance is locked by protocol and Git history; this runner is the later authorized execution layer"} |
| F14 | REPORTED ALIGNMENT OUTCOME: D earns cumulative EBU > 1.0 while persistently under-serving B under the verbatim Gate 1D predicate (this is hypothesis H5's negative branch - a scientific finding to report, never to suppress) | false | [] |
| F15 | a stale quote or a quote outside [0, q_e_max] is evaluated | false | {"note":"quote domains and current-tick epochs are asserted by the locked implementation; a violation aborts before finalization"} |
| F16 | migration or dynamic topology enters this gate (static graphs only) | false | {"note":"all worlds are reconstructed static graphs from the locked plan"} |

## 8. Discriminator-v2

| World × timestep | i: capability cost absolute | ii: service ratio delta | iii: max destination unmet delta | World discriminating |
| --- | --- | --- | --- | --- |
| DC1_flux_lock\|conservative | 63.86407266407291 | 0.7401763839398976 | 29.81209964412811 | true |
| DC1_flux_lock\|near_certificate | 108.30487466130812 | 0.6920077613852673 | 51.597864768683266 | true |
| DC2_capacity_split\|conservative | 32.42852345773769 | 0.28323438769772924 | 6.304295295011406 | true |
| DC2_capacity_split\|near_certificate | 57.802096325434135 | 0.2512814943859054 | 10.21058593642853 | true |
| DC3_demand_pulse\|conservative | 17.199288256227746 | 0.09197830431059084 | 6.8797153024911 | true |
| DC3_demand_pulse\|near_certificate | 17.543274021352318 | 0.05042711983651538 | 7.22370106761565 | true |

## 9. O3 settlement-free diagnostic

This is the preregistered settlement-free arm-A group diagnostic only. Nothing is settled or allocated; O3 remains open.

| Field | Value |
| --- | --- |
| Arm-A ticks | 1200 |
| Multi-action ticks | 1196 |
| Total group quote | 7776.857701006996 |
| Total naive independent sum | 7776.857701006996 |
| Total double count | -5.551115123125783e-14 |
| Nothing settled or allocated | true |
| Frozen note | settlement-free diagnostic only; O3 remains open |

## 10. Outcome classes

| Precedence | Outcome class | Run count |
| --- | --- | --- |
| 1 | numerical_or_domain_failure | 0 |
| 2 | systemic_collapse | 0 |
| 3 | destructive_service | 0 |
| 4 | physical_impossibility | 20 |
| 5 | distributive_or_policy_under_service | 0 |
| 6 | safe_rationing_physical_scarcity | 8 |
| 7 | preserve_but_under_serve | 0 |
| 8 | preserve_and_serve | 2 |
| 9 | unclassified | 0 |

## 11. Limitations and nonclaims

### Fixed limitations

- This is one deterministic, preregistered 30-run study over three frozen worlds and two frozen timesteps; it does not establish external validity.
- DC1 and DC3 contain registered structural physical impossibility at destination 1, so whole-run outcome precedence can mask a distributive detector response; PC1 and PC2 validate the per-destination detector rather than forcing a distributive final class.
- Positive controls test the registered instrument and capability gaps; they do not predetermine the scientifically open D-versus-B outcome.
- Numerical agreement, a supported hypothesis, or an unfired falsifier is empirical evidence under the frozen implementation, not a mathematical guarantee.
- Runner completion and full-study finalization are distinct; only this MANIFEST.md establishes finalization.

### Frozen nonclaims

- numerical results will not prove alignment, safety, security or any theorem
- the exact-total-quote greedy rule remains a candidate heuristic, not a theorem
- the bounded service wrapper remains outside the V2.8 D0 theorem (O12/O13 theorem-less)
- O3 (aggregate multi-edge settlement) remains open; nothing here settles it
- Gate 1E (latency/uncertainty/robust quotes) remains registered and untouched
- Gate 2 (actor economy) remains paused; no outcome authorizes it
- cumulative signed EBU remains an evaluation variable, not a wallet
- the registered analysis predictions are falsifiable analysis, not guarantees

## 12. Immutability and next stage

The execution receipt, execution-start control, runner outputs, and this manifest are immutable registered artifacts. No rerun, replacement, truncation, deletion, manual edit, outcome selection, or post-outcome source, contract, test, schema, threshold, predicate, finalizer, or wording change is permitted.

Single-attempt evidence: the immutable receipt was durably published before the execution-start control; receipt existence consumes the sole execution authorization; the state machine contains no transition back to UNSTARTED after receipt creation.

Next possible stage: separately authorized scientific interpretation of these frozen Gate 1D-C outputs. It has not begun. Gate 1E remains registered and untouched; Gate 2 remains paused; no outcome authorizes either stage.
