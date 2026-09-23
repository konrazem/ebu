"""Closed-cycle no-issuance, and where aggregate capacity can legitimately come from.

Everything in this module follows from one exact identity. Write the epoch as
`x_t -> y_t -> x_{t+1}`, where nature acts first and the actor acts second:

    E_t          = V(y_t) - V(x_{t+1})        the actor's contribution
    dV_ext,t     = V(y_t) - V(x_t)            what nature injected

Summing over a window and telescoping,

    sum_t E_t = V(x_0) - V(x_T) + sum_t dV_ext,t

and since settlement is exact and the common-path receipts of the executed
group sum to its own EBU,

    delta B_total = V(x_0) - V(x_T) + sum_t dV_ext,t.          (*)

**Theorem (closed-cycle no issuance).** Assume no external physical injection
during the cycle, exact finite EBU, exact settlement, no process burden, and
that the complete represented potential state returns, `x_T = x_0`. Then both
right-hand terms of (*) vanish, so `sum_t E_t = 0` and `delta B_total = 0`.
Repeating `A -> B -> A -> B -> A` therefore cannot mint aggregate capacity.
Capacity may move between actors; the total cannot grow. The argument uses only
telescoping and receipt closure, so it is indifferent to how many actions ran
in each epoch, which is why it extends to simultaneous groups verbatim: the
executed object per epoch is one group, and `sum_a R_a = E_G` exactly.

**Corollary (loss forces the ledger, not the theorem).** Every action's
increment sums to zero over all coordinates, so with no external injection the
grand total of every resource is invariant. If the valued coordinates return to
`x_0`, the audit-only sinks must hold exactly what they held before: a closed
cycle in the represented state admits no net irreversible loss. A path with
genuine loss is therefore not a closed cycle and must not be called one.

**Process burden.** A declared nonnegative per-action burden `C_a >= 0` is
*not* part of the accepted mechanism. If one were adopted, settling `R_a - C_a`
would give `delta B_total = -sum C_a <= 0` under otherwise closed return, by
the same telescoping. That form is recorded here as a conditional derivation
with its hypothesis attached, and it is not implemented: no burden is charged
anywhere in this package, and `C_a = 0` throughout.

**Provenance, not potential.** Whether an interval is actor-only is decided
from recorded external-event identities, never from `sum dV_ext == 0`. Nature
can inject deviation and remove it again, or permute stock at constant `V`;
both leave the potential term zero while the interval plainly contained
external physical transitions. See `actor_only`.

**Capacity sources.** Reading (*) as a table, aggregate capacity can increase
in exactly two ways: nature injected deviation that actors were paid to remove,
or the window ended closer to the reference than it started. Nothing else can
do it. In particular the arrival of an economic demand cannot: an arrival
changes no stock, so it changes no `V`, so it contributes nothing to either
term. A demand is a reason to act, never a receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Vector

from .harness import EconomyRun, EpochRecord
from .world import ROLE_SINK, DemandWorld

SOURCE_EXTERNAL = "EXTERNAL_PHYSICAL_DEVIATION"
SOURCE_NET_APPROACH = "NET_APPROACH_TO_REFERENCE"
SOURCE_ECONOMIC_ARRIVAL = "ECONOMIC_DEMAND_ARRIVAL"
SOURCE_CLOSED_ACTOR_CYCLE = "CLOSED_ACTOR_ONLY_CYCLE"

CAPACITY_SOURCE_TABLE = (
    (SOURCE_EXTERNAL, "may increase aggregate capacity", "sum_t dV_ext,t > 0"),
    (SOURCE_NET_APPROACH, "may increase aggregate capacity", "V(x_0) - V(x_T) > 0"),
    (SOURCE_ECONOMIC_ARRIVAL, "cannot change aggregate capacity", "an arrival moves no stock"),
    (SOURCE_CLOSED_ACTOR_CYCLE, "cannot change aggregate capacity", "both terms vanish"),
)


@dataclass(frozen=True)
class WindowAccounting:
    epochs: int
    external_events: tuple[str, ...]
    potential_initial: Fraction
    potential_final: Fraction
    external_total: Fraction
    ebu_total: Fraction
    balance_total: Fraction
    identity_residual: Fraction
    telescoping_residual: Fraction


def window(records: tuple[EpochRecord, ...]) -> WindowAccounting:
    """Exact accounting over a contiguous window of epochs."""
    if not records:
        raise ValueError("an accounting window needs at least one epoch")
    initial = records[0].potential_before
    final = records[-1].potential_after
    external = Fraction(0)
    ebu = Fraction(0)
    for record in records:
        external += record.external_deviation
        ebu += record.epoch_ebu
    # The balance the window opened with: strip epoch 0's own settlement back
    # off the balance it closed with.
    opening = records[0].balance_total - records[0].epoch_ebu
    balance = records[-1].balance_total - opening
    return WindowAccounting(
        len(records),
        tuple(event for record in records for event in record.external_events),
        initial,
        final,
        external,
        ebu,
        balance,
        balance - (initial - final + external),
        ebu - (initial - final + external),
    )


def net_loss(world: DemandWorld, before: Vector, after: Vector) -> Fraction:
    """Total quantity that irreversibly entered sinks over the window."""
    total = Fraction(0)
    for index, coordinate in enumerate(world.coordinates):
        if coordinate.role == ROLE_SINK:
            total += after[index] - before[index]
    return total


@dataclass(frozen=True)
class CycleVerdict:
    is_closed_cycle: bool
    reason: str
    state_returned: bool
    external_injection: Fraction
    ebu_total: Fraction
    balance_change: Fraction
    net_loss: Fraction
    external_events: tuple[str, ...] = ()


def actor_only(records: tuple[EpochRecord, ...]) -> bool:
    """Whether literally no external physical state transition occurred.

    Decided from recorded event provenance, never from `sum dV_ext == 0`.
    Two external events can cancel in the potential, and an external
    permutation of stock between symmetric coordinates changes the state at
    constant `V`; an interval containing either is not actor-only, and a
    classifier reading only the potential would call both actor-only and
    certify a no-issuance result that the theorem does not cover.

    An economic arrival is not an external physical event. It moves no stock,
    so it cannot break actor-only status.
    """
    return not any(record.external_events for record in records)


def closed_cycle(run: EconomyRun) -> CycleVerdict:
    """Classify a completed run against the closed-cycle hypotheses."""
    records = tuple(run.records)
    if not records:
        return CycleVerdict(
            False, "NO_EPOCHS", False, Fraction(0), Fraction(0), Fraction(0), Fraction(0), ()
        )
    accounting = window(records)
    returned = records[-1].state_after == records[0].state_before
    loss = net_loss(run.world, records[0].state_before, records[-1].state_after)
    change = run.ledger.total

    if not returned:
        reason = "STATE_DID_NOT_RETURN"
    elif not actor_only(records):
        reason = "EXTERNAL_PHYSICAL_EVENT_PRESENT"
    elif loss != 0:
        reason = "IRREVERSIBLE_LOSS_PRESENT"
    else:
        reason = "CLOSED_ACTOR_ONLY_CYCLE"
    closed = reason == "CLOSED_ACTOR_ONLY_CYCLE"
    return CycleVerdict(
        closed,
        reason,
        returned,
        accounting.external_total,
        accounting.ebu_total,
        change,
        loss,
        accounting.external_events,
    )
