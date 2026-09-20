"""Deterministic job identity and canonical scientific payloads.

Mission sections 21 and 22. Each replicate/policy/load combination is an
independent deterministic job whose scientific output is a pure function of its
declared identity.

The separation this module exists to enforce
--------------------------------------------

    JobIdentity          what the job is -- every input that can change science
    canonical payload    what the job produced -- scientific content only
    ExecutionEnvelope    where and when it ran -- host, wall clock, attempt

The payload hash covers the first two and **never** the third. Mission section
21 prefers a byte-identical scientific artifact and allows environment metadata
to differ; keeping the envelope structurally outside the payload is what makes
that preference achievable rather than aspirational.

Consequences that the conformance suite asserts rather than assumes:

  * no worker may derive a scientific choice from wall-clock time, process
    order, scheduling order or attempt number -- none of those is reachable
    from a job's inputs;
  * retries are idempotent, because a retry re-runs the same identity and the
    payload is a function of it;
  * two successful executions of one identity must have identical payload
    hashes, and a difference is a reproducibility failure rather than noise.

Nothing in this module contacts a cloud provider, and nothing in it is
specific to one. It is the local half of the equivalence gate, and it is the
half that carries the science.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Mapping, Sequence

from gaussian_harness.numerics import Refusal

from .harness import (
    DECLARED_LOADS,
    DECLARED_MENU_RULES,
    ForcingLoad,
    PolicyRun,
    PolicyWorld,
    code_identity,
    rehearsal_budget,
)
from .policies import CORE_POLICIES
from .region import ReferenceRegion

JOB_RULE_ID = "EBU-HOMEOSTASIS-JOB-v1"
SEPARATOR = "|"


def _rational(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class JobIdentity:
    """Everything that can change the science, and nothing that cannot."""

    preregistration_id: str
    configuration_identity: str
    code_identity: str
    load_id: str
    policy_id: str
    menu_rule: str
    replicate: int
    horizon: int
    forcing_seed: int
    actor_seed: int

    def __post_init__(self) -> None:
        if not self.preregistration_id.strip():
            raise Refusal("JOB_REFUSED: a job needs a preregistration identifier")
        if self.policy_id not in CORE_POLICIES:
            raise Refusal(f"undeclared policy {self.policy_id!r}")
        if self.menu_rule not in DECLARED_MENU_RULES:
            raise Refusal(f"undeclared menu rule {self.menu_rule!r}")
        if self.load_id not in {load.load_id for load in DECLARED_LOADS}:
            raise Refusal(f"undeclared load {self.load_id!r}")
        if self.replicate < 0 or self.horizon < 1:
            raise Refusal("replicate must be nonnegative and horizon positive")
        for field_name in ("preregistration_id", "configuration_identity",
                           "code_identity", "load_id", "policy_id", "menu_rule"):
            if SEPARATOR in getattr(self, field_name):
                raise Refusal(f"{field_name} must not contain the field separator")

    @property
    def preimage(self) -> str:
        return SEPARATOR.join((
            JOB_RULE_ID,
            self.preregistration_id,
            self.configuration_identity,
            self.code_identity,
            self.load_id,
            self.policy_id,
            self.menu_rule,
            f"{self.replicate:04d}",
            str(self.horizon),
            str(self.forcing_seed),
            str(self.actor_seed),
        ))

    @property
    def job_id(self) -> str:
        return hashlib.sha256(self.preimage.encode("ascii")).hexdigest()

    def as_dict(self) -> dict:
        return {
            "job_rule": JOB_RULE_ID,
            "job_id": self.job_id,
            "preregistration_id": self.preregistration_id,
            "configuration_identity": self.configuration_identity,
            "code_identity": self.code_identity,
            "load_id": self.load_id,
            "policy_id": self.policy_id,
            "menu_rule": self.menu_rule,
            "replicate": self.replicate,
            "horizon": self.horizon,
            "forcing_seed": self.forcing_seed,
            "actor_seed": self.actor_seed,
        }


@dataclass(frozen=True)
class ExecutionEnvelope:
    """Where and when a job ran. Deliberately outside the payload hash.

    A cloud worker legitimately differs from a laptop here -- hostname, start
    time, attempt number, queue. None of it may reach the scientific payload,
    so an AWS artifact and a local artifact of the same identity can be
    compared byte for byte on the part that matters.
    """

    executor: str
    attempt: int
    started_at: str | None = None
    host: str | None = None

    def as_dict(self) -> dict:
        return {
            "executor": self.executor,
            "attempt": self.attempt,
            "started_at": self.started_at,
            "host": self.host,
        }


@dataclass(frozen=True)
class JobResult:
    """A completed job: identity, canonical payload, and a separate envelope."""

    identity: JobIdentity
    payload: dict
    envelope: ExecutionEnvelope = field(
        default_factory=lambda: ExecutionEnvelope("unspecified", 0)
    )

    @property
    def canonical_payload(self) -> str:
        """Deterministic serialization of the scientific content only."""
        return json.dumps(self.payload, sort_keys=True, separators=(",", ":"))

    @property
    def payload_hash(self) -> str:
        return hashlib.sha256(self.canonical_payload.encode("utf-8")).hexdigest()

    def envelope_document(self) -> dict:
        """The full artifact: payload, its hash, and the envelope beside it."""
        return {
            "identity": self.identity.as_dict(),
            "payload_sha256": self.payload_hash,
            "payload": self.payload,
            "execution_envelope": self.envelope.as_dict(),
        }


def _load_for(load_id: str) -> ForcingLoad:
    for load in DECLARED_LOADS:
        if load.load_id == load_id:
            return load
    raise Refusal(f"undeclared load {load_id!r}")


def run_job(
    identity: JobIdentity,
    reference: Sequence,
    scale: Sequence,
    quanta: Sequence,
    study_id: str,
    configuration_id: str,
    envelope: ExecutionEnvelope | None = None,
    budget=None,
) -> JobResult:
    """Execute one job deterministically.

    Reads only the identity and the declared world. No wall clock, environment
    variable, process identifier, host name or scheduling position is consulted
    anywhere in this function or anything it calls.
    """
    if identity.code_identity != code_identity():
        raise Refusal(
            f"CODE_IDENTITY_MISMATCH: job declares {identity.code_identity}, "
            f"found {code_identity()}"
        )
    world = PolicyWorld.declare(
        study_id, configuration_id, list(reference), list(scale), list(quanta),
        identity.policy_id, menu_rule=identity.menu_rule,
    )
    load = _load_for(identity.load_id)
    run = PolicyRun(
        world, identity.forcing_seed, identity.actor_seed,
        budget or rehearsal_budget(identity.horizon),
    )

    columns: dict[str, list] = {key: [] for key in (
        "R2", "in95", "in99", "V", "sumB", "minB", "J", "status",
        "raw_forcing", "forcing_status", "null_action", "n_feasible",
        "n_affordable", "chosen", "tie_size",
    )}
    worst = {"accounting": Fraction(0), "conservation": Fraction(0), "nonnegativity": Fraction(0)}

    for _ in range(identity.horizon):
        record = run.run_tick(load)
        columns["R2"].append(_rational(record.radial_square))
        columns["in95"].append(record.in_h95)
        columns["in99"].append(record.in_h99)
        columns["V"].append(_rational(record.potential_total))
        columns["sumB"].append(_rational(record.balance_total))
        columns["minB"].append(_rational(min(record.balances)))
        columns["J"].append(_rational(record.audit_ledger))
        columns["status"].append(record.status)
        columns["raw_forcing"].append(record.raw_forcing)
        columns["forcing_status"].append(record.forcing_status)
        columns["null_action"].append(record.null_action)
        columns["n_feasible"].append(record.n_feasible)
        columns["n_affordable"].append(record.n_affordable)
        columns["chosen"].append(record.chosen_id)
        columns["tie_size"].append(record.tie_size)
        worst["accounting"] = max(worst["accounting"], abs(record.accounting_residual))
        worst["conservation"] = max(worst["conservation"], abs(record.conservation_residual))
        worst["nonnegativity"] = max(worst["nonnegativity"], abs(record.nonnegativity_residual))
        run.records.clear()

    payload = {
        "job_id": identity.job_id,
        "run_id": run.run_id,
        "protocol": JOB_RULE_ID,
        "columns": columns,
        "max_accounting_residual": _rational(worst["accounting"]),
        "max_conservation_residual": _rational(worst["conservation"]),
        "max_nonnegativity_residual": _rational(worst["nonnegativity"]),
    }
    return JobResult(identity, payload, envelope or ExecutionEnvelope("local", 0))


def manifest(results: Sequence[JobResult]) -> dict:
    """Integrity manifest over a set of jobs (mission section 28).

    Duplicate identities are permitted -- a retry produces one -- but they must
    carry identical payload hashes. A conflict is reported, never merged away.
    """
    by_id: dict[str, set[str]] = {}
    for result in results:
        by_id.setdefault(result.identity.job_id, set()).add(result.payload_hash)
    conflicts = sorted(job for job, hashes in by_id.items() if len(hashes) > 1)
    return {
        "jobs_expected": len(by_id),
        "jobs_observed": len(results),
        "duplicate_identities": len(results) - len(by_id),
        "conflicting_payloads": conflicts,
        "integrity_passed": not conflicts,
    }
