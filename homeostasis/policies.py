"""The four core actor policies, and the information each is allowed to read.

Mission section 7. All four share one physical world, topology, forcing,
candidate generation, physical feasibility and mandatory-action rule. They
differ only in (a) whether EBU affordability filters the menu and (b) how one
group is chosen from what remains.

    C  control_random   no affordability filter; uniform over feasible groups
    H  ebu_hostile      affordability; argmin E_G  -- the red-team arm
    R  ebu_random       affordability; uniform     -- the "stupid-proof" arm
    A  ebu_aligned      affordability; argmax E_G  -- the incentive arm

Information boundary
--------------------

The EBU-blind policies do not merely *decline* to read EBU values: the function
that implements them takes an integer count and has no candidate list, no
value, no sign, no potential and no balance in scope at all. That is a
structural guarantee an AST check can verify, not a convention.

The ranking policies read exactly one thing beyond the count: the exact group
EBU of each admissible candidate. They never read balances, the global
potential, the deviation ledger or the homeostatic region. `arg max E_G` is
*not* "minimum V globally": it is the largest exact finite EBU among the
candidates the actor may actually take, which on a common frozen pre-state
coincides with the smallest post-event `V` **restricted to that menu**.

Mandatory action
----------------

No policy may return "no action". There is no abstain, wait or no-op branch
anywhere in this module, and the empty group is absent from the menu upstream.
A policy is only ever asked to choose from a nonempty admissible set.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from gaussian_harness.numerics import Refusal
from gaussian_harness.rng import Counter, uniform_index

POLICY_RULE_ID = "EBU-GAUSSIAN-ACTOR-POLICY-v1"

POLICY_CONTROL_RANDOM = "control_random"
POLICY_EBU_HOSTILE = "ebu_hostile"
POLICY_EBU_RANDOM = "ebu_random"
POLICY_EBU_ALIGNED = "ebu_aligned"

CORE_POLICIES = (
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
    POLICY_EBU_ALIGNED,
)

SELECTION_UNIFORM = "uniform_over_admissible"
SELECTION_ARGMIN = "argmin_group_ebu"
SELECTION_ARGMAX = "argmax_group_ebu"


@dataclass(frozen=True)
class PolicySpecification:
    """Declared, frozen description of one arm."""

    policy_id: str
    label: str
    applies_affordability: bool
    selection: str
    purpose: str

    @property
    def reads_ebu_to_choose(self) -> bool:
        return self.selection in (SELECTION_ARGMIN, SELECTION_ARGMAX)


POLICIES: dict[str, PolicySpecification] = {
    POLICY_CONTROL_RANDOM: PolicySpecification(
        POLICY_CONTROL_RANDOM,
        "C -- control-random",
        applies_affordability=False,
        selection=SELECTION_UNIFORM,
        purpose="baseline random physical behaviour without EBU protection",
    ),
    POLICY_EBU_HOSTILE: PolicySpecification(
        POLICY_EBU_HOSTILE,
        "H -- EBU-hostile",
        applies_affordability=True,
        selection=SELECTION_ARGMIN,
        purpose="worst physically destructive choice still obeying affordability",
    ),
    POLICY_EBU_RANDOM: PolicySpecification(
        POLICY_EBU_RANDOM,
        "R -- EBU-random",
        applies_affordability=True,
        selection=SELECTION_UNIFORM,
        purpose="robustness to actors with no homeostatic intelligence",
    ),
    POLICY_EBU_ALIGNED: PolicySpecification(
        POLICY_EBU_ALIGNED,
        "A -- EBU-aligned",
        applies_affordability=True,
        selection=SELECTION_ARGMAX,
        purpose="does following the EBU incentive produce the strongest regulation",
    ),
}


@dataclass(frozen=True)
class PolicyDecision:
    """Which admissible candidate was chosen, and by exactly which rule."""

    index: int
    rule: str
    tie_size: int
    provenance: str


def _uniform_over_count(count: int, counter: Counter) -> tuple[int, str]:
    """Choose one of `count` canonically ordered candidates.

    Deliberately takes an integer. No candidate, value, sign, potential or
    balance is in scope here, so an EBU-blind policy cannot encode a
    preference even accidentally.
    """
    if count <= 0:
        raise Refusal("uniform selection needs a nonempty admissible set")
    index, _ = uniform_index(counter, count)
    return index, counter.provenance


def _extremum_positions(values: Sequence[Fraction], largest: bool) -> tuple[int, ...]:
    """Positions attaining the exact extremum.

    Values are exact rationals, so ties are exact equalities rather than
    near-equalities under a tolerance -- and in a small symmetric world they
    are common, which is why tie-breaking is a registered rule and not an
    afterthought.
    """
    if not values:
        raise Refusal("extremum selection needs a nonempty admissible set")
    best = max(values) if largest else min(values)
    return tuple(index for index, value in enumerate(values) if value == best)


def choose(
    policy_id: str, admissible_ebu: Sequence[Fraction], counter: Counter
) -> PolicyDecision:
    """Select one admissible candidate under the declared policy.

    `admissible_ebu` is indexed by the canonical order of the admissible set;
    the caller guarantees that order. Ranking arms resolve exact ties with the
    registered actor RNG over the canonically ordered tied positions, which is
    frozen and EBU-neutral *within* a tied value.
    """
    specification = POLICIES.get(policy_id)
    if specification is None:
        raise Refusal(f"undeclared actor policy {policy_id!r}")

    if specification.selection == SELECTION_UNIFORM:
        index, provenance = _uniform_over_count(len(admissible_ebu), counter)
        return PolicyDecision(index, SELECTION_UNIFORM, len(admissible_ebu), provenance)

    largest = specification.selection == SELECTION_ARGMAX
    tied = _extremum_positions(admissible_ebu, largest)
    if len(tied) == 1:
        # Still record the counter that *would* have been used, so the actor
        # stream stays addressable at the same coordinates in every arm.
        return PolicyDecision(tied[0], specification.selection, 1, counter.provenance)
    position, provenance = _uniform_over_count(len(tied), counter)
    return PolicyDecision(tied[position], specification.selection, len(tied), provenance)


def policy_table() -> tuple[dict[str, object], ...]:
    """Machine-readable declaration of the four arms, for the frozen record."""
    return tuple(
        {
            "policy_id": specification.policy_id,
            "label": specification.label,
            "applies_affordability": specification.applies_affordability,
            "selection": specification.selection,
            "reads_ebu_to_choose": specification.reads_ebu_to_choose,
            "purpose": specification.purpose,
            "may_decline_to_act": False,
        }
        for specification in (POLICIES[name] for name in CORE_POLICIES)
    )
