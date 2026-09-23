# Demand-driven Stage A — publication note

This branch publishes the complete, audited record of the demand-driven Stage-A
study `EBU-DEMAND-DRIVEN-STAGE-A-v1`, and nothing else.

It is built on the published mainline `origin/main` and adds only the transitive
closure required to reproduce Stage A. It deliberately does **not** carry the
book series, Stage B, the homeostasis or SD study programmes, or the Dynamic EBU
theory workstream, all of which remain unpublished on their own branches.

## What is here, and why each part is required

| path | why it is required |
|---|---|
| `demand_driven_ebu/` | the mechanism under study; identity `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48` |
| `gaussian_harness/` | direct dependency — `demand_driven_ebu` imports `gaussian_harness.numerics` and `.potential`. It imports no other first-party package |
| `capacity_v2/`, `homeostasis/` | **identity pins only.** `demand_driven_stage_a/sources.py` and `test_demand_driven_ebu.py::test_pinned_packages_are_untouched` verify their code identities to prove Stage A did not perturb neighbouring models. The packages are needed for that check to run; **none of the homeostasis or capacity study work, results or documents is published here** |
| `demand_driven_stage_a/` | the runner, registry, stopping rules, reporting, source manifest and the read-only verifier |
| `test_demand_driven_ebu.py`, `test_demand_driven_stage_a.py` | the permanent regressions and the execution-free preflight |
| `scripts/stage_a_preregistration_identity.py` | recomputes the frozen preregistration digest; executes no model code |
| `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` + corrections 1 and 2 | the frozen protocol and its two pre-execution correction records |
| `DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md`, `..._STUDY_ONE_DOMAIN.md`, `..._MODEL_FINDINGS.md`, `..._STUDY_ONE_READINESS.md` | contract, domain, findings and readiness records |
| `DEMAND_DRIVEN_STAGE_A_EXECUTION_REPORT.md` | outcomes, the observation/guarantee boundary, the accepted deviation and the attempt history |
| two `..._AUDIT_HANDOFF.md` | the audit records needed to reconstruct the implemented Stage-A decisions |
| `results/demand_driven_stage_a*/` | all four attempt directories, preserved exactly |

## Provenance references to unpublished analysis

Two documents previously cited the Dynamic EBU workstream as the home of the
finding F-7 accessibility evidence. **Those citations have been redirected to
the self-contained regressions published here**, which are the authoritative
evidence and are reproducible from this branch alone:

- `DEMAND_DRIVEN_MODEL_FINDINGS.md` — now cites the named regressions in
  `test_demand_driven_ebu.py`, including the 91-state accessibility oracle;
- `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` — now cites
  `test_study_one_is_wholly_accessible_under_atomic_p_service` and finding F-7.

`EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md` and `dynamic_ebu_theory_checks.py` are
**not published here**, and neither was added merely to satisfy a citation.

Three references to them survive, in documents that were deliberately **not**
edited:

| document | why it was not edited |
|---|---|
| `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` §0 | **frozen.** Its identity `a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17` is the seal under which 768 episodes executed. Editing it would break that seal and falsify the record |
| `DEMAND_DRIVEN_ATOMIC_P_DEMAND_AUDIT_HANDOFF.md` | a **historical** audit record of what was validated in that pass. Rewriting it would misreport what was actually run |
| `DEMAND_DRIVEN_STAGE_A_FOUNDATION_AUDIT_HANDOFF.md` | same |

**These are historical provenance, not Stage-A authority.** Nothing in Stage A's
execution, results or verification consults them: the runner, the mechanism, the
frozen protocol, the verifier and the artifacts are self-contained on this
branch. In the preregistration's own three-way split, the surviving citation
supports **L** ("where aggregate reserve is maximal") and part of **R** ("whether
the allowed actions provide a path"); **R is independently settled here by
finding F-7**, and **P** — whether actor policies take such paths — is the open
question Stage A was built to observe and makes no use of the cited material.

A reader who wants that background must obtain it from the Dynamic EBU
workstream separately. Its absence does not impair reproduction of Stage A.

## Reproducing the verification

All read-only; none of it advances model state or runs an episode:

```
python3 scripts/stage_a_preregistration_identity.py     # frozen digest -> MATCH
python3 -m demand_driven_stage_a.verify                 # 36 checks over the artifacts
python3 test_demand_driven_stage_a.py                   # execution-free preflight
```

`test_demand_driven_ebu.py` is the mechanism conformance suite and **does**
advance model state; it is a conformance instrument, not a Stage-A episode, and
it generates no scientific evidence.

## Status

Stage A is closed: execution and numerical audit complete, accepted with one
documented operational deviation, recorded in the execution report §5. Stage B
is unauthorized and unfrozen.
