"""Post-execution verification of the produced artifacts.

Reads artifacts and re-checks them. Executes no model code and advances no
state: every check is arithmetic, comparison or hashing over recorded values.

Run: python3 -m demand_driven_stage_a.verify
"""

from __future__ import annotations

import gzip
import json
import pathlib
from fractions import Fraction

from . import registry, sources

OUT = sources.ROOT / "results" / "demand_driven_stage_a"
PRIOR = sources.ROOT / "results" / "demand_driven_stage_a_SUPERSEDED_ATTEMPT_3"

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))


def load(directory: pathlib.Path, episode: str):
    path = directory / f"EPISODES_{episode}.json.gz"
    return json.loads(gzip.decompress(path.read_bytes()))


def main() -> int:
    inventory = json.loads((OUT / "EXECUTION_INVENTORY.json").read_text())
    manifest = json.loads((OUT / "SOURCE_MANIFEST.json").read_text())
    jobs = json.loads((OUT / "JOB_MANIFEST.json").read_text())

    print("\ninventory and manifest")
    check("768 declared, 768 completed, 0 failed, 0 unstarted",
          (inventory["total_declared"], inventory["completed"],
           inventory["failed"], inventory["unstarted"]) == (768, 768, 0, 0),
          str(inventory))
    check("execution did not halt on an integrity failure",
          inventory["halted_on_integrity_failure"] is False)
    check("the protected packages were unchanged after execution",
          inventory["protected_packages_unchanged_after"])
    check("and they are still unchanged now",
          all(r["unchanged"] for r in sources.protected_identities().values()))
    check("768 distinct run identities in the manifest",
          jobs["total"] == 768 and jobs["distinct_run_ids"] == 768)

    declared = {j.job_key: registry.build_run(j).run_id for j in registry.jobs()}
    recorded = {j["job_key"]: j["run_id"] for j in jobs["jobs"]}
    check("every recorded identity equals the one the registry builds today",
          declared == recorded)

    snapshot = OUT / "source_snapshot"
    mismatched = [
        e["path"] for e in manifest["files"]
        if not (snapshot / e["path"]).exists()
        or sources.file_digest(snapshot / e["path"]) != e["sha256"]
    ]
    check(f"the source snapshot reproduces all {manifest['file_count']} "
          "manifested files byte for byte", not mismatched, str(mismatched[:3]))

    episodes = {e: load(OUT, e) for e in ("A1", "A2", "A3")}

    print("\nper-episode records")
    for name, rows in episodes.items():
        check(f"{name}: 256 episodes, all COMPLETED",
              len(rows) == 256 and all(r["status"] == "COMPLETED" for r in rows))
        check(f"{name}: every epoch's four residuals are exactly zero",
              all(e[k] == "0/1" for r in rows for e in r["epochs"] for k in
                  ("accounting_residual", "conservation_residual",
                   "nonnegativity_residual", "separability_residual")))
        check(f"{name}: the joint gate is closed at every epoch",
              all(e["joint_gate"] == "JOINT_CLOSURE_VERIFIED"
                  for r in rows for e in r["epochs"]))
        check(f"{name}: the decomposition gate is VERIFIED at every epoch that "
              "carried active demand",
              all(e["decomposition_gate"] == "POLICY_EXECUTION_EQUALS_GLOBAL_REFERENCE"
                  for r in rows for e in r["epochs"]
                  if e["active_physical"] or e["active_economic"]))
        check(f"{name}: mass is exactly 12 at every recorded state",
              all(sum(Fraction(v) for v in e["state_after"]) == 12
                  and all(Fraction(v) >= 0 for v in e["state_after"])
                  for r in rows for e in r["epochs"]))
        check(f"{name}: transitions recorded never exceed the declared horizon",
              all(r["transitions_recorded"] <= r["horizon"] for r in rows))

    print("\nstopping rules, as recorded")
    a1 = episodes["A1"]
    check("A1: every stopping reason is one of the three declared",
          {r["report"]["stopping_reason"] for r in a1}
          <= {"RETURNED_TO_REFERENCE", "NO_AFFORDABLE_SOLUTION", "HORIZON_REACHED"})
    check("A1: a RETURNED episode's terminal state is exactly x*",
          all(r["report"]["terminal_state"] == ["4/1", "4/1", "4/1"]
              for r in a1 if r["report"]["stopping_reason"] == "RETURNED_TO_REFERENCE"))
    check("A1: return_time equals transitions_recorded on every return",
          all(r["report"]["return_time"] == r["report"]["transitions_recorded"]
              for r in a1 if r["report"]["stopping_reason"] == "RETURNED_TO_REFERENCE"))
    check("A1: terminal_no_active_demand is true exactly on a return, and was "
          "derived rather than executed",
          all((r["report"]["terminal_no_active_demand"])
              == (r["report"]["stopping_reason"] == "RETURNED_TO_REFERENCE")
              for r in a1))
    check("A1: a HORIZON_REACHED episode recorded exactly T transitions",
          all(r["report"]["transitions_recorded"] == r["report"]["horizon"]
              for r in a1 if r["report"]["stopping_reason"] == "HORIZON_REACHED"))
    check("A3: every episode ran the full declared horizon -- A3 does not "
          "inherit A1's return stop",
          all(r["transitions_recorded"] == 32 for r in episodes["A3"]))

    print("\nreport / mechanism cross-checks")
    a3 = episodes["A3"]
    bad_afford = []
    for r in a3:
        report = r["report"]
        chosen = {e["executed_group_id"] for e in r["epochs"] if e["epoch"] == 3}
        for row in report["candidate_table"]:
            if row["plan_id"] in chosen and not row["affordable"]:
                bad_afford.append((r["job_key"], row["plan_id"]))
    check("no A3 report marks the plan the mechanism actually executed as "
          "unaffordable -- the defect that superseded attempt 3",
          not bad_afford, str(bad_afford[:3]))

    label_bad = []
    for r in a3:
        report = r["report"]
        facts = report["restoration_facts"]
        outcome = report["order_outcome"]
        if outcome == "RESTORATION_COMPLETED":
            if facts["tracked_count"] == 0 or facts["first_simultaneous_closure"] is None:
                label_bad.append(r["job_key"])
        if outcome == "SERVED_WITHOUT_RESTORATION":
            if report["served_without_restoration_reason"] is None:
                label_bad.append(r["job_key"])
    check("RESTORATION_COMPLETED is never recorded on an empty tracked set, "
          "and SERVED_WITHOUT_RESTORATION always carries its reason",
          not label_bad, str(label_bad[:3]))

    check("every A3 outcome is one of the five declared labels",
          {r["report"]["order_outcome"] for r in a3}
          <= {"ORDER_REJECTED", "ORDER_PENDING_UNAFFORDABLE",
              "ORDER_PENDING_NO_COMPLETE_PLAN", "RESTORATION_COMPLETED",
              "SERVED_WITHOUT_RESTORATION"})

    burden_bad = []
    for name, rows in episodes.items():
        for r in rows:
            for e in r["epochs"]:
                ebu = Fraction(e["epoch_ebu"])
                delta = Fraction(e["potential_before"]) - Fraction(e["potential_after"])
                if ebu != delta:
                    burden_bad.append((r["job_key"], e["epoch"]))
    check("epoch EBU equals V(pre) - V(post) exactly, at every epoch of all 768",
          not burden_bad, str(burden_bad[:3]))

    print("\ntrajectory identity against the superseded attempt")
    if PRIOR.exists():
        differing = []
        for name in ("A1", "A2", "A3"):
            prior = {r["job_key"]: r for r in load(PRIOR, name)}
            for r in episodes[name]:
                before = prior.get(r["job_key"])
                if before is None or before.get("status") != "COMPLETED":
                    continue
                if before["epochs"] != r["epochs"]:
                    differing.append(r["job_key"])
        check("every epoch record is IDENTICAL to the superseded attempt: the "
              "correction touched a derived column, not a trajectory",
              not differing, str(differing[:3]))
    else:
        check("the superseded attempt is available for comparison", False)

    print(f"\n{PASSED} passed, {FAILED} failed")
    print("Execution class: READ-ONLY VERIFICATION. No model code ran.")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
