# `EBU-DEMAND-DRIVEN-STAGE-A-v1` — registered results

Produced by `python3 -m demand_driven_stage_a.execute --execute`.
Verified by `python3 -m demand_driven_stage_a.verify` (read-only, 36 checks).

| file | contents |
|---|---|
| `EXECUTION_INVENTORY.json` | completed / failed / unstarted counts, identities, post-execution source check |
| `JOB_MANIFEST.json` | all 768 declared jobs with their run identities and full configuration strings |
| `SOURCE_MANIFEST.json` | per-file SHA-256 of every source the run read, plus the four protected package identities |
| `source_snapshot/` | byte-identical copies of those 46 files — reproduction needs no commit |
| `PREFLIGHT.json` | the gate result recorded before the first epoch |
| `EPISODES_A1.json.gz` | 256 episodes: full epoch records and the A1 report |
| `EPISODES_A2.json.gz` | 256 episodes: full epoch records and the A2 report |
| `EPISODES_A3.json.gz` | 256 episodes: full epoch records and the A3 report |

Preregistration identity (freeze 3):
`a74d83802c900cc79ee308b876e409e1f94cf11d8fe3fe1bda5fdb764654bd17`.
Mechanism identity: `demand_driven_ebu` =
`f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48`.

**Every scientific quantity is stored exactly, as `numerator/denominator`, and
passed through no float.** One exclusion, recorded rather than glossed:
`EXECUTION_INVENTORY.json` carries `elapsed_seconds` as a float (wall-clock
runtime metadata, `58.844`). A scan of the full artifact set finds it is the
only float anywhere; nothing scientific is derived from it.

These files are **attempt 4**, the reported set: 768 jobs, 11,066 saved epochs.
Its epoch sequences are identical to attempt 3 record for record.

Two things the artifacts do **not** say, and which the execution report sets out
in full:

- `RESTORATION_COMPLETED` means simultaneous closure of the deficits tracked
  immediately after economic service. It does **not** mean equilibrium return.
  `ebu_hostile` is 64/64 on the first and 0/64 on the second;
- one integrity-predicate discrepancy between preregistration §7 and §8 is
  **closed by author acceptance** of a narrowly scoped operational deviation,
  covering only epochs with `DECOMPOSITION_NOT_CHECKED` + `NO_ACTIVE_DEMAND` +
  both active demand sets empty — **192 A3 episodes, 4,737 epochs**. It waives
  no active-demand check and no gate refusal, and does not affect the verified
  numerical integrity of these records.

Read `../../DEMAND_DRIVEN_STAGE_A_EXECUTION_REPORT.md` for the outcomes, the
observation/guarantee boundary, and the preserved attempt history. Superseded
attempts are in the sibling `..._FAILED_ATTEMPT_1`, `..._FAILED_ATTEMPT_2` and
`..._SUPERSEDED_ATTEMPT_3` directories and are retained deliberately.

These results are **not** `results/stage_a/`, which belongs to the unrelated
`EBU-STAGE-A-V1` study over `gaussian_harness`.
