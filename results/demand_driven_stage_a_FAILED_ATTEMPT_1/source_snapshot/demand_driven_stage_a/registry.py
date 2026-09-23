"""The frozen registered configuration. Constructs jobs; runs nothing.

Every number here is transcribed from `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md`
and nothing in it is derived from an observed outcome. Building an `EconomyRun`
does not advance it: `EconomyRun.__post_init__` sets the opening state and a
zero ledger and stops. Only `run_epoch` is a model transition, and this module
never calls it.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from demand_driven_ebu.arrivals import ArrivalProcess
from demand_driven_ebu.fixtures import (
    ScriptedArrivals,
    no_arrivals,
    quiet_disturbance,
    study_one_state,
    study_one_world,
)
from demand_driven_ebu.harness import EconomyRun
from demand_driven_ebu.policies import (
    POLICY_ALIGNED,
    POLICY_CONTROL,
    POLICY_HOSTILE,
    POLICY_RANDOM,
)

from . import REGISTRATION_ID

# Section 5. Exactly four arms, in the frozen order.
ARMS = (POLICY_CONTROL, POLICY_RANDOM, POLICY_ALIGNED, POLICY_HOSTILE)

# Section 6. 64 replicates per arm per episode class.
REPLICATES = 64

EPISODES = ("A1", "A2", "A3")

# Section 6, seed table. `k` is the replicate index.
NATURAL_SEED = 1
ARRIVAL_SEED = 2


def admission_seed(replicate: int) -> int:
    return 3 + replicate


def actor_seed(replicate: int) -> int:
    return 1000 + replicate


@dataclass(frozen=True)
class EpisodeSpec:
    """One declared episode class, independent of policy and replicate."""

    episode: str
    opening: tuple[int, ...]
    horizon: int
    arrivals_kind: str

    def arrivals(self):
        if self.arrivals_kind == "none":
            # A1: no economic demand at any epoch.
            return no_arrivals()
        if self.arrivals_kind == "stochastic_one_slot":
            # A2: one slot, probability 1, alphabet of one kind.
            return ArrivalProcess.declare((("r", "C", 1),), 1, 1, 1)
        if self.arrivals_kind == "scripted_epoch_three":
            # A3: exactly one order, one unit at C, at epoch 3, and none else.
            return ScriptedArrivals({3: (("r", "C", 1),)})
        raise ValueError(f"undeclared arrival kind {self.arrivals_kind!r}")


# Sections 2, 3 and 4. The declared fixtures.
SPECS = {
    "A1": EpisodeSpec("A1", (1, 7, 4), 32, "none"),
    "A2": EpisodeSpec("A2", (4, 4, 4), 1, "stochastic_one_slot"),
    "A3": EpisodeSpec("A3", (1, 7, 4), 32, "scripted_epoch_three"),
}


@dataclass(frozen=True)
class Job:
    """One registered episode, fully identified before it is run."""

    episode: str
    policy: str
    replicate: int
    horizon: int

    @property
    def job_key(self) -> str:
        return f"{self.episode}|{self.policy}|k={self.replicate}"


def jobs() -> tuple[Job, ...]:
    """The complete declared set, in frozen order: 3 x 4 x 64 = 768."""
    built = []
    for episode in EPISODES:
        spec = SPECS[episode]
        for policy in ARMS:
            for replicate in range(REPLICATES):
                built.append(Job(episode, policy, replicate, spec.horizon))
    return tuple(built)


def build_run(job: Job) -> EconomyRun:
    """Construct the job's run object. Advances nothing."""
    spec = SPECS[job.episode]
    world = study_one_world()
    return EconomyRun(
        world=world,
        disturbance=quiet_disturbance(world),
        arrivals=spec.arrivals(),
        policy=job.policy,
        natural_seed=NATURAL_SEED,
        arrival_seed=ARRIVAL_SEED,
        admission_seed=admission_seed(job.replicate),
        actor_seed=actor_seed(job.replicate),
        initial_state=study_one_state(*spec.opening),
        registered=True,
        decomposition_gate=True,
        registration=REGISTRATION_ID,
        episode=job.episode,
        replicate=job.replicate,
    )


def opening_balances_are_zero(run: EconomyRun) -> bool:
    """Section 2/3/4: `B_i(0) = 0` for every owner."""
    return all(balance == Fraction(0) for _, balance in run.ledger.balances)
