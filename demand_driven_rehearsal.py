"""Small local rehearsal of the demand-driven economy. NON-CONFIRMATORY.

Contract section 42. The purpose is to exercise the machinery end to end --
arrival, admission, E/P coexistence, plan enumeration, all four actor
policies, capacity circulation, physical evolution, and artifact/replay
behaviour -- and to confirm that the exact residuals stay at zero once the
pieces run together rather than one fixture at a time.

**This is not evidence.** No hypothesis is registered, no comparison is
preregistered, no seed is selected, and nothing below may be read as a finding
about whether the demand-driven economy restores, is safe under a hostile
actor, or behaves better than its comparator. The model is not tuned to
anything seen here, and the run is deliberately short.

Every number printed is either an infrastructure observation (did it run, did
it replay, did the residuals close) or a descriptive count with no inferential
claim attached.
"""

from __future__ import annotations

import gzip
import json
import time
from fractions import Fraction
from pathlib import Path

from demand_driven_ebu.arrivals import ArrivalProcess
from demand_driven_ebu.disturbance import DisturbanceProcess
from demand_driven_ebu.fixtures import sandwater_world, study_one_state, study_one_world
from demand_driven_ebu.harness import (
    DECOMPOSITION_NOT_CHECKED,
    DECOMPOSITION_VERIFIED,
    DECLARED_STATUSES,
    STATUS_ALL_UNAFFORDABLE,
    STATUS_EXECUTED,
    STATUS_NO_ACTIVE_DEMAND,
    STATUS_NO_COMPLETE_PLAN,
    STATUS_SEARCH_INCOMPLETE,
    STATUS_SEARCH_UNRESOLVED,
    EconomyRun,
    code_identity,
    read_code_identity,
)
from demand_driven_ebu.policies import (
    POLICY_ALIGNED,
    POLICY_CONTROL,
    POLICY_HOSTILE,
    POLICY_RANDOM,
)
from demand_driven_ebu.demand import DECLARED_LIFECYCLE, LIFECYCLE_SERVED
from demand_driven_ebu.service import pool
from demand_driven_ebu.study_one import completeness_bound, in_domain

EPOCHS = 200
STUDY_ONE_EPOCHS = 200
REPLICATES = 4
POLICIES = (POLICY_CONTROL, POLICY_HOSTILE, POLICY_RANDOM, POLICY_ALIGNED)
ARTIFACT = Path("results/rehearsal_demand_driven/DEMAND_DRIVEN_REHEARSAL.json.gz")


def build():
    world = sandwater_world()
    disturbance = DisturbanceProcess.declare(
        world, ((0, 1), (1, 2), (2, 0), (3, 4), (4, 3)), 2, 1, 2
    )
    arrivals = ArrivalProcess.declare(
        (("sand", "A", 1), ("sand", "C", 2), ("water", "E", 1)), 1, 4, 2
    )
    return world, disturbance, arrivals


def exact_median(values: list[Fraction]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        return Fraction(0)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def summarize(records) -> dict:
    statuses = {
        key: sum(1 for r in records if r.epoch_status == key)
        for key in DECLARED_STATUSES
    }
    rejected: dict[str, int] = {}
    for record in records:
        for _, reason in record.rejected_now:
            rejected[reason] = rejected.get(reason, 0) + 1
    plan_counts = [o.plan_count for r in records for o in r.outcomes]
    return {
        "statuses": statuses,
        "arrivals": sum(len(r.arrivals) for r in records),
        "admitted": sum(len(r.admitted_now) for r in records),
        "served": sum(len(r.served_economic) for r in records),
        "rejected": rejected,
        "unaffordable_epochs": sum(1 for r in records if r.unaffordable_economic),
        "components_seen": sum(len(r.outcomes) for r in records),
        "median_menu_size": exact_median([Fraction(c) for c in plan_counts]),
        "max_menu_size": max(plan_counts) if plan_counts else 0,
        "median_V": exact_median([r.potential_after for r in records]),
        "final_V": records[-1].potential_after,
        "final_B_total": records[-1].balance_total,
        "worst_accounting": max(abs(r.accounting_residual) for r in records),
        "worst_conservation": max(abs(r.conservation_residual) for r in records),
        "worst_nonnegativity": max(abs(r.nonnegativity_residual) for r in records),
        "worst_separability": max(abs(r.separability_residual) for r in records),
    }


def columns(records) -> list[list[str]]:
    """The scientific columns a replay must reproduce byte for byte."""
    return [
        [
            str(r.epoch),
            r.epoch_status,
            r.executed_group_id,
            str(r.epoch_ebu),
            str(r.balance_total),
            str(r.potential_after),
            ",".join(r.arrivals),
            ",".join(r.admitted_now),
            ",".join(r.served_economic),
            ",".join(r.external_events),
            ";".join(f"{a}:{'|'.join(d)}" for a, d in r.executed_provenance),
            ";".join(str(v) for v in r.state_after),
        ]
        for r in records
    ]


def audit(world, run, records) -> dict:
    """The seven checks the audit correction pass asks the rehearsal to make.

    Every one of these is an infrastructure or semantics check. None of them
    is a behavioural observation and none may be read as one.
    """
    quantities = {row.demand_id: row.quantity for row in run.arrival_ledger.values()}

    double_service = []
    unprovenanced = []
    for record in records:
        increment = tuple(
            after - forced
            for after, forced in zip(record.state_after, record.state_forced)
        )
        claimed: dict[int, Fraction] = {}
        for demand_id in record.served_economic:
            coordinate = run.arrival_ledger[demand_id].destination
            claimed[coordinate] = claimed.get(coordinate, Fraction(0)) + quantities[demand_id]
        for coordinate, total in claimed.items():
            if total > pool(increment, coordinate):
                double_service.append(
                    f"t={record.epoch} c={coordinate} claimed={total} "
                    f"pool={pool(increment, coordinate)}"
                )
        executed = {action_id for action_id, _ in record.executed_provenance}
        for action_id, demand_ids in record.executed_provenance:
            if not demand_ids:
                unprovenanced.append(f"t={record.epoch} {action_id}")
        if record.executed_group_id != "g:[]":
            members = record.executed_group_id[3:-1].split(",")
            if set(members) != executed:
                unprovenanced.append(f"t={record.epoch} group/provenance mismatch")

    served_twice = []
    seen: dict[str, int] = {}
    for record in records:
        for demand_id in record.served_economic:
            seen[demand_id] = seen.get(demand_id, 0) + 1
    served_twice = sorted(k for k, v in seen.items() if v > 1)

    frozen_but_others_ran = sum(
        1
        for record in records
        if any(o.status == STATUS_NO_COMPLETE_PLAN for o in record.outcomes)
        and any(o.status == STATUS_EXECUTED for o in record.outcomes)
    )

    lifecycle: dict[str, int] = {state: 0 for state in DECLARED_LIFECYCLE}
    for row in run.arrival_ledger.values():
        lifecycle[row.state] = lifecycle.get(row.state, 0) + 1

    return {
        "double_service": double_service,
        "served_twice": served_twice,
        "unprovenanced": unprovenanced,
        "independent_progress_epochs": frozen_but_others_ran,
        "lifecycle": lifecycle,
        "arrivals_total": len(run.arrival_ledger),
        "served_total": sum(
            1 for row in run.arrival_ledger.values() if row.state == LIFECYCLE_SERVED
        ),
    }


def execute():
    world, disturbance, arrivals = build()
    table = {}
    payload = {}
    for policy in POLICIES:
        for replicate in range(REPLICATES):
            run = EconomyRun(
                world,
                disturbance,
                arrivals,
                policy,
                natural_seed=1000 + replicate,
                arrival_seed=2000 + replicate,
                admission_seed=3000 + replicate,
                actor_seed=4000 + replicate,
            )
            records = run.run(EPOCHS)
            key = f"{policy}#{replicate}"
            summary = summarize(records)
            summary["audit"] = audit(world, run, records)
            summary["raw_arrivals"] = tuple(
                demand for record in records for demand in record.arrivals
            )
            table[key] = (summary, run)
            payload[key] = columns(records)
    return world, table, payload


def study_one_build():
    """The frozen-domain rehearsal world, run under registered semantics."""
    world = study_one_world()
    disturbance = DisturbanceProcess.declare(
        world, ((0, 1), (1, 2), (2, 1), (1, 0)), 2, 1, 2
    )
    arrivals = ArrivalProcess.declare((("r", "A", 1), ("r", "C", 2)), 1, 3, 2)
    return world, disturbance, arrivals


def study_one_execute():
    """Every arm of the Study-1 rehearsal, registered and decomposition-gated.

    `registered=True` means an undecided search would raise `JobInvalid` and
    stop the job rather than being recorded. `decomposition_gate=True` means
    every epoch independently verifies the component path against the
    decomposition-free **policy-conditioned** reference at four levels --
    physical eligibility, the affordable set under this arm's balances, the
    selection law this policy induces over canonical plan identities, and the
    modeled-outcome law it pushes forward.
    """
    world, disturbance, arrivals = study_one_build()
    table = {}
    payload = {}
    for policy in POLICIES:
        for replicate in range(REPLICATES):
            run = EconomyRun(
                world,
                disturbance,
                arrivals,
                policy,
                natural_seed=1000 + replicate,
                arrival_seed=2000 + replicate,
                admission_seed=3000 + replicate,
                actor_seed=4000 + replicate,
                initial_state=study_one_state(),
                registered=True,
                decomposition_gate=True,
            )
            records = run.run(STUDY_ONE_EPOCHS)
            key = f"{policy}#{replicate}"
            summary = summarize(records)
            summary["gate"] = {
                verdict: sum(1 for r in records if r.decomposition_gate == verdict)
                for verdict in (DECOMPOSITION_VERIFIED, DECOMPOSITION_NOT_CHECKED)
            }
            summary["capacity_source"] = abs(run.capacity_source_residual)
            table[key] = summary
            payload[key] = columns(records)
    return world, table, payload


def report_study_one() -> tuple[bool, dict]:
    world, _, _ = study_one_build()
    bound = completeness_bound(world)
    print("\n" + "=" * 78)
    print("STUDY-1 FROZEN-DOMAIN REHEARSAL -- NON-CONFIRMATORY, NOT EVIDENCE")
    print("=" * 78)
    print(f"world: {world.world_id}   inside the frozen domain: {in_domain(world)}")
    print(f"registered failure semantics: ON   decomposition gate: ON")
    print(f"completeness: {bound.usable_routes} usable routes, "
          f"{bound.atomic_actions} atomic actions, complete plan space "
          f"{bound.plan_space} against a budget of {bound.exhaustive_budget}")
    print(f"SEARCH_UNRESOLVED impossible by construction: "
          f"{bound.unresolved_impossible}    plan cap binds: {bound.cap_binds}")

    started = time.time()
    _, table, payload = study_one_execute()
    elapsed = time.time() - started
    _, _, replay = study_one_execute()
    deterministic = payload == replay
    print(f"wall: {elapsed:.1f}s per pass of "
          f"{len(POLICIES) * REPLICATES * STUDY_ONE_EPOCHS} epochs "
          f"(decomposition gate on), run twice for replay")
    print(f"replay deterministic: {deterministic}")

    worst = Fraction(0)
    for summary in table.values():
        for key in ("worst_accounting", "worst_conservation", "worst_nonnegativity",
                    "worst_separability"):
            worst = max(worst, summary[key])
        worst = max(worst, summary["capacity_source"])
    unresolved = sum(
        summary["statuses"][STATUS_SEARCH_UNRESOLVED] for summary in table.values()
    )
    incomplete = sum(
        summary["statuses"][STATUS_SEARCH_INCOMPLETE] for summary in table.values()
    )
    verified = sum(summary["gate"][DECOMPOSITION_VERIFIED] for summary in table.values())
    unchecked = sum(
        summary["gate"][DECOMPOSITION_NOT_CHECKED] for summary in table.values()
    )

    header = (
        f"{'policy':24s}{'exec':>6s}{'idle':>6s}{'noplan':>8s}{'srchInc':>9s}"
        f"{'srchUnr':>9s}{'unaff':>7s}{'arriv':>7s}{'admit':>7s}{'serve':>7s}"
        f"{'gateOK':>8s}"
    )
    print("\n" + header)
    for policy in POLICIES:
        rows = [s for key, s in table.items() if key.startswith(policy + "#")]
        print(
            f"{policy:24s}"
            f"{sum(r['statuses'][STATUS_EXECUTED] for r in rows):>6d}"
            f"{sum(r['statuses'][STATUS_NO_ACTIVE_DEMAND] for r in rows):>6d}"
            f"{sum(r['statuses'][STATUS_NO_COMPLETE_PLAN] for r in rows):>8d}"
            f"{sum(r['statuses'][STATUS_SEARCH_INCOMPLETE] for r in rows):>9d}"
            f"{sum(r['statuses'][STATUS_SEARCH_UNRESOLVED] for r in rows):>9d}"
            f"{sum(r['statuses'][STATUS_ALL_UNAFFORDABLE] for r in rows):>7d}"
            f"{sum(r['arrivals'] for r in rows):>7d}"
            f"{sum(r['admitted'] for r in rows):>7d}"
            f"{sum(r['served'] for r in rows):>7d}"
            f"{sum(r['gate'][DECOMPOSITION_VERIFIED] for r in rows):>8d}"
        )
    print(f"\n    worst residual anywhere                    {worst}")
    print(f"    Study-1 SEARCH_UNRESOLVED epochs           {unresolved}")
    print(f"    Study-1 SEARCH_INCOMPLETE_AT_PLAN_CAP      {incomplete}")
    print(f"    epochs where decomposition == global       {verified}")
    print(f"    epochs with nothing to decompose           {unchecked}")

    healthy = (
        deterministic
        and worst == 0
        and unresolved == 0
        and incomplete == 0
        and bound.unresolved_impossible
        and not bound.cap_binds
    )
    return healthy, {
        "world_id": world.world_id,
        "epochs": STUDY_ONE_EPOCHS,
        "registered": True,
        "decomposition_gate": True,
        "replay_deterministic": deterministic,
        "worst_residual": str(worst),
        "search_unresolved_epochs": unresolved,
        "search_incomplete_epochs": incomplete,
        "decomposition_verified_epochs": verified,
        "decomposition_unchecked_epochs": unchecked,
        "completeness_bound": {
            "usable_routes": bound.usable_routes,
            "atomic_actions": bound.atomic_actions,
            "plan_space": bound.plan_space,
            "exhaustive_budget": bound.exhaustive_budget,
            "plan_cap": bound.plan_cap,
            "cap_binds": bound.cap_binds,
            "unresolved_impossible": bound.unresolved_impossible,
        },
        "healthy": healthy,
    }


def main() -> int:
    opening_identity = read_code_identity()
    started = time.time()
    world, table, payload = execute()
    elapsed = time.time() - started

    replay_started = time.time()
    _, _, replay_payload = execute()
    replay_elapsed = time.time() - replay_started
    deterministic = payload == replay_payload

    closing_identity = read_code_identity()

    print("DEMAND-DRIVEN REHEARSAL -- NON-CONFIRMATORY, NOT EVIDENCE")
    print(f"world: {world.world_id}  epochs: {EPOCHS}  replicates: {REPLICATES}  "
          f"policies: {len(POLICIES)}")
    print(f"code identity at start: {opening_identity}")
    print(f"code identity at end:   {closing_identity}")
    print(f"identity stable: {opening_identity == closing_identity}")
    print(f"wall: {elapsed:.1f}s run, {replay_elapsed:.1f}s replay "
          f"({len(POLICIES) * REPLICATES * EPOCHS} epochs each)")
    print(f"replay deterministic: {deterministic}")

    worst = {
        "accounting": Fraction(0),
        "conservation": Fraction(0),
        "nonnegativity": Fraction(0),
        "separability": Fraction(0),
        "capacity_source": Fraction(0),
    }
    for _, (summary, run) in table.items():
        worst["accounting"] = max(worst["accounting"], summary["worst_accounting"])
        worst["conservation"] = max(worst["conservation"], summary["worst_conservation"])
        worst["nonnegativity"] = max(worst["nonnegativity"], summary["worst_nonnegativity"])
        worst["separability"] = max(worst["separability"], summary["worst_separability"])
        worst["capacity_source"] = max(
            worst["capacity_source"], abs(run.capacity_source_residual)
        )
    print("worst residual across every run:")
    for name, value in worst.items():
        print(f"    {name:16s} {value}")

    header = (
        f"{'policy':24s}{'exec':>6s}{'idle':>6s}{'noplan':>8s}{'srchInc':>9s}"
        f"{'srchUnr':>9s}{'unaff':>7s}{'arriv':>7s}{'admit':>7s}{'serve':>7s}"
        f"{'rejS':>6s}{'rejI':>6s}{'medMenu':>9s}{'medV':>8s}{'endB':>10s}"
    )
    print("\n" + header)
    for policy in POLICIES:
        rows = [summary for key, (summary, _) in table.items() if key.startswith(policy + "#")]
        totals = {
            "exec": sum(r["statuses"][STATUS_EXECUTED] for r in rows),
            "idle": sum(r["statuses"][STATUS_NO_ACTIVE_DEMAND] for r in rows),
            "noplan": sum(r["statuses"][STATUS_NO_COMPLETE_PLAN] for r in rows),
            "srchInc": sum(r["statuses"][STATUS_SEARCH_INCOMPLETE] for r in rows),
            "srchUnr": sum(r["statuses"][STATUS_SEARCH_UNRESOLVED] for r in rows),
            "unaff": sum(r["statuses"][STATUS_ALL_UNAFFORDABLE] for r in rows),
            "arriv": sum(r["arrivals"] for r in rows),
            "admit": sum(r["admitted"] for r in rows),
            "serve": sum(r["served"] for r in rows),
            "rejS": sum(r["rejected"].get("E_REJECTED_PHYSICAL_SCARCITY", 0) for r in rows),
            "rejI": sum(r["rejected"].get("E_REJECTED_INCOMPATIBLE", 0) for r in rows),
        }
        med_menu = exact_median([r["median_menu_size"] for r in rows])
        med_v = exact_median([r["median_V"] for r in rows])
        end_b = sum((r["final_B_total"] for r in rows), Fraction(0)) / len(rows)
        print(
            f"{policy:24s}{totals['exec']:>6d}{totals['idle']:>6d}{totals['noplan']:>8d}"
            f"{totals['srchInc']:>9d}{totals['srchUnr']:>9d}{totals['unaff']:>7d}"
            f"{totals['arriv']:>7d}{totals['admit']:>7d}"
            f"{totals['serve']:>7d}{totals['rejS']:>6d}{totals['rejI']:>6d}"
            f"{str(med_menu):>9s}{str(med_v):>8s}{str(end_b):>10s}"
        )
        covered = sum(
            totals[k] for k in ("exec", "idle", "noplan", "srchInc", "srchUnr", "unaff")
        )
        if covered != EPOCHS * REPLICATES:
            print(f"    WARNING: {policy} statuses cover {covered} of "
                  f"{EPOCHS * REPLICATES} epochs")

    # ---- audit correction pass checks (infrastructure, not behaviour) ----
    raw_by_policy = {}
    for policy in POLICIES:
        for replicate in range(REPLICATES):
            summary, _ = table[f"{policy}#{replicate}"]
            raw_by_policy.setdefault(replicate, {})[policy] = summary["raw_arrivals"]
    arrivals_identical = all(
        len({tuple(v) for v in per_replicate.values()}) == 1
        for per_replicate in raw_by_policy.values()
    )
    admitted_by_policy = {
        policy: sum(
            table[f"{policy}#{r}"][0]["audit"]["lifecycle"].get("ARRIVED", 0)
            for r in range(REPLICATES)
        )
        for policy in POLICIES
    }
    never_admitted = {
        policy: sum(
            table[f"{policy}#{r}"][0]["admitted"] for r in range(REPLICATES)
        )
        for policy in POLICIES
    }
    double = [
        entry
        for key, (summary, _) in table.items()
        for entry in summary["audit"]["double_service"]
    ]
    twice = [
        f"{key}:{entry}"
        for key, (summary, _) in table.items()
        for entry in summary["audit"]["served_twice"]
    ]
    unprov = [
        f"{key}:{entry}"
        for key, (summary, _) in table.items()
        for entry in summary["audit"]["unprovenanced"]
    ]
    independent_progress = sum(
        summary["audit"]["independent_progress_epochs"] for summary, _ in table.values()
    )

    print("\naudit correction pass checks")
    print(f"    E/E double service events                  {len(double)}")
    print(f"    economic demands served more than once     {len(twice)}")
    print(f"    executed actions without demand provenance {len(unprov)}")
    print(f"    raw arrival sequences identical across arms {arrivals_identical}")
    print(f"    admitted counts by arm                     "
          f"{ {p: never_admitted[p] for p in POLICIES} }")
    print(f"    epochs where an unserviceable component sat beside an executing one "
          f"{independent_progress}")

    lifecycle_total: dict[str, int] = {}
    for summary, _ in table.values():
        for state, count in summary["audit"]["lifecycle"].items():
            lifecycle_total[state] = lifecycle_total.get(state, 0) + count
    print("    arrival lifecycle over the common raw set:")
    for state in DECLARED_LIFECYCLE:
        print(f"        {state:38s} {lifecycle_total.get(state, 0)}")

    study_one_healthy, study_one_summary = report_study_one()

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "class": "REHEARSAL / NON-CONFIRMATORY",
        "model_id": "EBU-DEMAND-DRIVEN-ECONOMY-v1",
        "code_identity": code_identity(),
        "world_id": world.world_id,
        "epochs": EPOCHS,
        "replicates": REPLICATES,
        "policies": list(POLICIES),
        "replay_deterministic": deterministic,
        "worst_residuals": {k: str(v) for k, v in worst.items()},
        "audit": {
            "double_service_events": len(double),
            "served_more_than_once": len(twice),
            "actions_without_provenance": len(unprov),
            "raw_arrivals_identical_across_arms": arrivals_identical,
            "admitted_by_arm": {p: never_admitted[p] for p in POLICIES},
            "independent_progress_epochs": independent_progress,
            "arrival_lifecycle": lifecycle_total,
        },
        "arrival_ledger": {
            key: sorted(
                (row.demand_id, str(row.quantity), row.state, row.arrival_epoch)
                for row in run.arrival_ledger.values()
            )
            for key, (_, run) in table.items()
        },
        "study_one": study_one_summary,
        "columns": payload,
    }
    with gzip.open(ARTIFACT, "wt", encoding="utf-8") as handle:
        json.dump(document, handle, sort_keys=True)
    print(f"\nwritten: {ARTIFACT}")
    print("CLASS: REHEARSAL / NON-CONFIRMATORY -- no scientific claim is made here")

    healthy = (
        deterministic
        and opening_identity == closing_identity
        and all(value == 0 for value in worst.values())
        and not double
        and not twice
        and not unprov
        and arrivals_identical
        and study_one_healthy
    )
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
