"""The frozen per-episode reports, as pure functions of recorded epochs.

Everything here reads records. Nothing advances a state. Where a quantity is
re-derived rather than persisted -- the A3 candidate table -- it is derived by
exact enumeration from the RECORDED pre-action state, and the reconstruction is
checked against the recorded demand ids before it is used.

Exact rational values are carried as strings in `numerator/denominator` form.
No quantity in any artifact passes through a float.

Sections 2, 4 and 7 of the preregistration.
"""

from __future__ import annotations

from fractions import Fraction

from demand_driven_ebu.capacity import CapacityLedger
from demand_driven_ebu.coupling import components
from demand_driven_ebu.demand import (
    ActiveDemandSet,
    EconomicDemand,
    derive_physical_demands,
)
from demand_driven_ebu.harness import (
    STATUS_ALL_UNAFFORDABLE,
    STATUS_NO_COMPLETE_PLAN,
)
from demand_driven_ebu.plans import enumerate_service_plans
from demand_driven_ebu.policies import POLICY_CONTROL
from demand_driven_ebu.valuation import value_group

ORDER_REJECTED = "ORDER_REJECTED"
ORDER_PENDING_UNAFFORDABLE = "ORDER_PENDING_UNAFFORDABLE"
ORDER_PENDING_NO_COMPLETE_PLAN = "ORDER_PENDING_NO_COMPLETE_PLAN"
RESTORATION_COMPLETED = "RESTORATION_COMPLETED"
SERVED_WITHOUT_RESTORATION = "SERVED_WITHOUT_RESTORATION"

NO_INDUCED_DEFICIT = "NO_INDUCED_DEFICIT"
INDUCED_DEFICIT_UNCLOSED = "INDUCED_DEFICIT_UNCLOSED"

ORDER_OUTCOMES = (
    ORDER_REJECTED,
    ORDER_PENDING_UNAFFORDABLE,
    ORDER_PENDING_NO_COMPLETE_PLAN,
    RESTORATION_COMPLETED,
    SERVED_WITHOUT_RESTORATION,
)


def q(value) -> str:
    """Exact rational, as a string. Never a float."""
    f = Fraction(value)
    return f"{f.numerator}/{f.denominator}"


def qv(vector) -> list[str]:
    return [q(v) for v in vector]


def deficits(world, state) -> dict[int, Fraction]:
    """The P-demand read off a state, as {coordinate: shortfall}."""
    return {d.coordinate: d.required for d in derive_physical_demands(world, state)}


# ---------------------------------------------------------------------------
# A1
# ---------------------------------------------------------------------------


def a1_report(world, records, *, horizon: int, stopping_reason: str) -> dict:
    reference = world.reference_state()
    states = [records[0].state_before] + [r.state_after for r in records]
    burden = [world.potential.value_total(s) for s in states]
    n = len(records)

    return_time = None
    for index, record in enumerate(records):
        if tuple(record.state_after) == tuple(reference):
            return_time = index + 1
            break

    terminal = states[-1]
    return {
        "stopping_reason": stopping_reason,
        "return_time": return_time,
        "transitions_recorded": n,
        "horizon": horizon,
        "burden_path": [q(v) for v in burden],
        "restoring_drift": [q(burden[i] - burden[i + 1]) for i in range(n)],
        "plateau_crossings": [
            index
            for index, record in enumerate(records)
            if burden[index + 1] == burden[index] and record.executed_group_id
        ],
        "terminal_state": qv(terminal),
        "terminal_no_active_demand": tuple(terminal) == tuple(reference),
        "reserve_path": [
            {"total": q(r.balance_total), "owners": {o: q(b) for o, b in r.balances}}
            for r in records
        ],
        "restoration_ledger": [
            {
                "epoch": r.epoch,
                "entries": [
                    {
                        "coordinate": s.coordinate,
                        "demand_id": s.demand_id,
                        "deficit_before": q(s.deficit_before),
                        "delivered": q(s.delivered),
                        "progress": q(s.progress),
                        "remainder": q(s.remainder),
                        "overshoot": q(s.overshoot),
                    }
                    for s in r.restoration
                ],
            }
            for r in records
            if r.restoration
        ],
    }


# ---------------------------------------------------------------------------
# A2
# ---------------------------------------------------------------------------


def a2_report(world, records) -> dict:
    record = records[0]
    before, after = record.state_before, record.state_after
    outcome = record.outcomes[0] if record.outcomes else None
    return {
        "arrival_state": [list(pair) for pair in record.arrival_states],
        "epoch_status": record.epoch_status,
        "menu_size": outcome.plan_count if outcome else 0,
        "affordable_count": outcome.affordable_count if outcome else 0,
        "physical_consequence": {
            "increment": [q(after[i] - before[i]) for i in range(world.dimension)],
            "potential_change": q(
                world.potential.value_total(after) - world.potential.value_total(before)
            ),
        },
        "induced_p_demand": {
            str(c): q(v) for c, v in sorted(deficits(world, after).items())
        },
        "receipts": {owner: q(amount) for owner, amount in record.receipts},
        "balances": {owner: q(amount) for owner, amount in record.balances},
        "executed_group_id": record.executed_group_id,
    }


# ---------------------------------------------------------------------------
# A3
# ---------------------------------------------------------------------------

ARRIVAL_EPOCH = 3
# (resource, quantity, node) -- the argument order of `EconomicDemand.declare`.
ORDER_KIND = ("r", 1, "C")


def expected_order_id(world) -> str:
    return EconomicDemand.declare(world, *ORDER_KIND, ARRIVAL_EPOCH, 0).demand_id


def candidate_table(world, record, *, baseline_balances, policy: str) -> list[dict]:
    """Every plan in the order's component at the recorded arrival baseline.

    Re-derived by exact enumeration from `record.state_forced`, the recorded
    pre-action state of that epoch. The economic demand is reconstructed from
    the declared schedule and its id is checked against the recorded active set
    before anything is enumerated, so a reconstruction that does not match the
    run is refused rather than reported.

    Affordability is decided against `baseline_balances` -- the owner vector as
    it stood WHEN THE ORDER ARRIVED, which section 4 declares as the recorded
    quantity -- and through the mechanism's own `CapacityLedger.is_affordable`,
    not a re-implementation of it. Deciding it against the epoch's CLOSING
    balances instead would subtract the chosen plan's own cost before asking
    whether that plan was affordable, and could report the executed plan as
    unaffordable inside the same record that executes it.
    """
    order = EconomicDemand.declare(world, *ORDER_KIND, ARRIVAL_EPOCH, 0)
    if order.demand_id not in record.active_economic:
        raise AssertionError(
            f"reconstructed order {order.demand_id!r} is not in the recorded "
            f"active set {record.active_economic!r}"
        )
    baseline = record.state_forced
    physical = derive_physical_demands(world, baseline)
    active = ActiveDemandSet.of(physical, (order,))
    found = components(world, baseline, active)
    target = [c for c in found if order.demand_id in c.demand_ids]
    if len(target) != 1:
        raise AssertionError("the order must lie in exactly one component")
    ledger = CapacityLedger(
        tuple(sorted((o, Fraction(b)) for o, b in baseline_balances)),
        constrained=policy != POLICY_CONTROL,
    )
    rows = []
    for plan in enumerate_service_plans(world, baseline, target[0]):
        valuation = value_group(world, baseline, plan.group)
        owners = valuation.owner_map
        increment = plan.group.increment(world.dimension)
        post = tuple(baseline[i] + increment[i] for i in range(world.dimension))
        rows.append(
            {
                "plan_id": plan.group.group_id,
                "post_state": qv(post),
                "aggregate_ebu": q(valuation.group_ebu),
                "owner_receipts": {o: q(v) for o, v in sorted(owners.items())},
                "serves": list(plan.served),
                "affordable": ledger.is_affordable(valuation).affordable,
                "deficient_owners": list(
                    ledger.is_affordable(valuation).deficient_owners
                ),
            }
        )
    return sorted(rows, key=lambda r: r["plan_id"])


def a3_report(world, records, *, horizon: int, stopping_reason: str, policy: str) -> dict:
    order_id = expected_order_id(world)
    states = [records[0].state_before] + [r.state_after for r in records]

    by_epoch = {r.epoch: r for r in records}
    arrival_record = by_epoch.get(ARRIVAL_EPOCH)

    # --- the four chain facts, recorded separately -------------------------
    admission_status, admission_epoch = "NEVER_ARRIVED", None
    for record in records:
        for demand_id, status in record.arrival_states:
            if demand_id == order_id and admission_epoch is None:
                admission_status, admission_epoch = status, record.epoch
    rejected = False
    for record in records:
        for demand_id, reason in record.rejected_now:
            if demand_id == order_id:
                admission_status, admission_epoch, rejected = (
                    reason,
                    record.epoch,
                    True,
                )

    service_epoch = None
    for record in records:
        if order_id in record.served_economic:
            service_epoch = record.epoch
            break

    pending = []
    for record in records:
        if service_epoch is not None and record.epoch > service_epoch:
            break
        if order_id in record.active_economic and order_id not in record.served_economic:
            pending.append({"epoch": record.epoch, "reason": record.epoch_status})

    # --- restoration facts --------------------------------------------------
    tracked, first_closure, first_simultaneous = {}, {}, None
    if service_epoch is not None:
        post_service = states[service_epoch + 1]
        tracked = deficits(world, post_service)
        for coordinate in tracked:
            for index in range(service_epoch + 1, len(states)):
                if deficits(world, states[index]).get(coordinate, Fraction(0)) == 0:
                    first_closure[coordinate] = index
                    break
        if tracked:
            # Evaluated over the WHOLE tracked set at each index in turn. It is
            # NOT max(first_closure): a coordinate may close and reopen.
            for index in range(service_epoch + 1, len(states)):
                here = deficits(world, states[index])
                if all(here.get(c, Fraction(0)) == 0 for c in tracked):
                    first_simultaneous = index
                    break

    # --- the ordered, exhaustive label decision -----------------------------
    reason = None
    if rejected:
        outcome = ORDER_REJECTED                                          # L1
    elif service_epoch is None:
        if any(p["reason"] == STATUS_NO_COMPLETE_PLAN for p in pending):
            outcome = ORDER_PENDING_NO_COMPLETE_PLAN                      # L3
        else:
            outcome = ORDER_PENDING_UNAFFORDABLE                          # L2
    elif tracked and first_simultaneous is not None:
        outcome = RESTORATION_COMPLETED                                   # L4
    else:
        outcome = SERVED_WITHOUT_RESTORATION                              # L5
        reason = NO_INDUCED_DEFICIT if not tracked else INDUCED_DEFICIT_UNCLOSED

    prelude = by_epoch.get(ARRIVAL_EPOCH)
    return {
        "stopping_reason": stopping_reason,
        "transitions_recorded": len(records),
        "horizon": horizon,
        "arrival_baseline": qv(prelude.state_forced) if prelude else None,
        "prelude_reserve": (
            {
                "total": q(by_epoch[ARRIVAL_EPOCH - 1].balance_total),
                "owners": {o: q(b) for o, b in by_epoch[ARRIVAL_EPOCH - 1].balances},
            }
            if (ARRIVAL_EPOCH - 1) in by_epoch
            else None
        ),
        "order_admission_status": admission_status,
        "order_admission_epoch": admission_epoch,
        "order_service_epoch": service_epoch,
        "order_pending_epochs": pending,
        # A rejected order joins no component, so it has no menu. The table is
        # empty in that case by construction, not by omission.
        "candidate_table": (
            candidate_table(
                world,
                arrival_record,
                baseline_balances=(
                    by_epoch[ARRIVAL_EPOCH - 1].balances
                    if (ARRIVAL_EPOCH - 1) in by_epoch
                    else ()
                ),
                policy=policy,
            )
            if arrival_record is not None and order_id in arrival_record.active_economic
            else []
        ),
        "restoration_facts": {
            "tracked_deficits": {str(c): q(v) for c, v in sorted(tracked.items())},
            "first_closure": {str(c): v for c, v in sorted(first_closure.items())},
            "first_simultaneous_closure": first_simultaneous,
            "closure_count": len(first_closure),
            "tracked_count": len(tracked),
        },
        "order_outcome": outcome,
        "served_without_restoration_reason": reason,
        "deficit_provenance": [
            {
                "epoch": r.epoch,
                "pre": {str(c): q(v) for c, v in sorted(deficits(world, r.state_forced).items())},
                "post": {str(c): q(v) for c, v in sorted(deficits(world, r.state_after).items())},
            }
            for r in records
            if r.executed_group_id
        ],
        "burden_path": [q(world.potential.value_total(s)) for s in states],
        "reserve_path": [
            {"total": q(r.balance_total), "owners": {o: q(b) for o, b in r.balances}}
            for r in records
        ],
        "restoration_ledger": [
            {
                "epoch": r.epoch,
                "entries": [
                    {
                        "coordinate": s.coordinate,
                        "demand_id": s.demand_id,
                        "deficit_before": q(s.deficit_before),
                        "delivered": q(s.delivered),
                        "progress": q(s.progress),
                        "remainder": q(s.remainder),
                        "overshoot": q(s.overshoot),
                    }
                    for s in r.restoration
                ],
            }
            for r in records
            if r.restoration
        ],
    }
