"""Actor policies: how to satisfy an obligation that already exists.

A policy never decides *whether* to act, *which* demand to serve, or *in what
order*. Those are settled before it is called: the demand set is given, the
components are given, and every plan in the menu already serves its whole
component completely. All a policy does is choose among equally complete
answers to the same obligation.

    ALIGNED   argmax_G E_G
    RANDOM    uniform over the affordable complete plans
    HOSTILE   argmin_G E_G
    CONTROL   uniform over the complete plans, with no affordability filter

The hostile actor is the corrected hostile test. It may choose a physically
damaging way of meeting the obligation -- including one that overshoots and
makes the deviation worse -- but it cannot ignore the demand and it cannot
perform an unrelated destructive action, because no such plan is in any menu.
That is a much sharper test than the old environment could pose, where a
hostile actor was free to do arbitrary damage that nobody had asked for.

There is no voluntary no-action. When a component has at least one complete,
executable, affordable plan, one of them executes. Legitimate inaction exists
only in three physically distinct situations, which are logged separately and
never collapsed into one another: no active demand, no complete physical
solution, and no affordable solution.

The random and control policies reach their choice through a function whose
entire input is a count of candidates. It is not merely convention that they
cannot see an EBU value, a sign, a potential, a deviation or a balance -- the
value is not passed, so there is nothing to ignore.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from gaussian_harness.numerics import Refusal

from .rng import Counter, uniform_index

POLICY_ALIGNED = "ebu_aligned"
POLICY_RANDOM = "ebu_random"
POLICY_HOSTILE = "ebu_hostile"
POLICY_CONTROL = "control_random_no_ebu"
DECLARED_POLICIES = (POLICY_ALIGNED, POLICY_RANDOM, POLICY_HOSTILE, POLICY_CONTROL)


@dataclass(frozen=True)
class PolicySpecification:
    policy_id: str
    description: str
    reads_ebu_to_choose: bool
    applies_affordability: bool


POLICY_TABLE = (
    PolicySpecification(
        POLICY_ALIGNED,
        "argmax E_G over affordable complete service plans",
        True,
        True,
    ),
    PolicySpecification(
        POLICY_RANDOM,
        "uniform over affordable complete service plans",
        False,
        True,
    ),
    PolicySpecification(
        POLICY_HOSTILE,
        "argmin E_G over affordable complete service plans",
        True,
        True,
    ),
    PolicySpecification(
        POLICY_CONTROL,
        "uniform over complete service plans, no affordability filter, EBU never read",
        False,
        False,
    ),
)


def specification(policy_id: str) -> PolicySpecification:
    for entry in POLICY_TABLE:
        if entry.policy_id == policy_id:
            return entry
    raise Refusal(f"undeclared actor policy {policy_id!r}")


def _uniform_over_count(count: int, counter: Counter) -> int:
    """Choose one of `count` candidates. Structurally blind to what they are."""
    index, _ = uniform_index(counter, count)
    return index


def _extremum_positions(values: Sequence[Fraction], largest: bool) -> tuple[int, ...]:
    if not values:
        raise Refusal("an extremum needs a nonempty candidate list")
    best = max(values) if largest else min(values)
    return tuple(index for index, value in enumerate(values) if value == best)


def choose(
    policy_id: str,
    plan_count: int,
    ebu_values: Sequence[Fraction] | None,
    counter: Counter,
) -> int:
    """Return the chosen plan's index in the canonically ordered menu.

    `ebu_values` is passed only for the two policies that are declared to read
    it. For `RANDOM` and `CONTROL` the caller passes `None`, so no value can
    reach the decision even by accident.
    """
    entry = specification(policy_id)
    if plan_count <= 0:
        raise Refusal("a policy is never called on an empty menu")
    if entry.reads_ebu_to_choose:
        if ebu_values is None or len(ebu_values) != plan_count:
            raise Refusal(f"{policy_id} requires one EBU value per candidate plan")
        tied = _extremum_positions(ebu_values, largest=(policy_id == POLICY_ALIGNED))
        if len(tied) == 1:
            return tied[0]
        return tied[_uniform_over_count(len(tied), counter)]
    if ebu_values is not None:
        raise Refusal(f"{policy_id} must not be given EBU values")
    return _uniform_over_count(plan_count, counter)
