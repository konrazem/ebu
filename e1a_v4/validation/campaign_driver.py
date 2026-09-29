"""THE official E1a v4 campaign driver. Declared canonically; implemented here.

    e1a_v4/validation/driver.py  ->  OFFICIAL_CAMPAIGN_DRIVER_PATH
                                     OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT

WHAT THIS MODULE IS
    An EXECUTOR. It orchestrates the frozen protocol; it does not define it.
    Every replicate count, threshold, alpha, margin, field parameter, case
    definition, subcondition, C7 alternative, C8 scale factor and mandatory
    diagnostic is READ from the validated authority loaders. None is restated
    here. `grep` this file for a number and you will find array indices and
    schema versions, not science.

THE INVARIANT THIS MODULE EXISTS TO ENFORCE
    The frozen authority states, identically, in the working baseline, the
    prospective design and the design contract:

        "Branch-A output is hashed and published BEFORE Branch B is unblinded."

    The existing `ReplicateCalibration` enforced part of the chain -- an artifact
    is checked against a supplied condition, and the Branch-B seed is refused
    before the artifact is locked. Two gaps remained:

      1. nothing HASHED or PUBLISHED Branch-A evidence at all; and
      2. `lock()` accepted an externally prepared `CalibrationCondition` as proof
         of Branch-A provenance, so a caller could present a condition that never
         came from the Branch-A measurement of that replicate.

    The complete chain is now mechanical:

        Branch-A measurement
              -> immutable BranchARealisation bound to its coordinates
              -> deterministic canonical evidence hash
              -> DURABLE PUBLICATION (e1a_v4.validation.publication)
              -> CalibrationCondition derived FROM THAT EXACT REALISATION
              -> calibration artifact generated for the same coordinates
              -> artifact locked
              -> Branch-B unblind token issued only if every predicate holds
              -> Branch-B stochastic access
              -> analysis
              -> case result, with its mandatory contract diagnostics

    `JobExecution.branch_b_seed` is the ONLY route to a Branch-B stream, and it
    refuses unless the token exists. Premature access is a refusal, not a
    convention.

WHAT IS NOT HERE, DELIBERATELY
    No RNG is constructed. No random number is drawn. No trajectory is generated.
    `run_campaign` refuses: the execution seal is not frozen and execution is not
    authorised. The stochastic providers are INJECTED, so a static test can prove
    with a sentinel that the real provider was never requested.

CLASSIFICATION
    planning, coordinates, hashing, state transitions ... EXACT (deterministic)
"""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..branch_a import BranchAField
from ..contract import sha256_file
from ..calibration import CalibrationArtifact, CalibrationCondition, canonical_float
from ..numerics import Refusal
from .calibrate import CalibrationRequest
from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_identity_component,
)
from . import PLAN_MARKDOWN
from .plan import ExecutionBinding, VALIDATION_MODULES, bind_execution
from .publication import canonical_digest, publish_atomic, read_published
from .refusals import (
    BranchAEvidenceAltered, BranchANotPublished, BranchAProvenanceMismatch,
    BranchAPublicationImmutable, BranchBPremature, CampaignManifestInvalid,
    CampaignPlanMismatch, JobStateInvalid,
)
from .release_authority import require_mandatory_diagnostics
from .results import MANIFEST_SCHEMA, RESULT_SCHEMA
from .scope import (
    CampaignCalibrationLedger, CaseCalibrationScope, ReplicateCalibration,
)
from .seeds import EXPERIMENT_SCOPE, ValidationSeedFamily

#: Schema of the immutable Branch-A publication record.
BRANCH_A_PUBLICATION_SCHEMA = "e1a_v4_branch_a_publication/1"
#: Schema of the deterministic pre-execution campaign manifest.
CAMPAIGN_MANIFEST_SCHEMA = "e1a_v4_campaign_manifest/1"

#: Where Branch-A publications live, relative to the campaign output directory.
BRANCH_A_PUBLICATION_DIR = "branch_a"
CAMPAIGN_MANIFEST_BASENAME = "campaign_manifest.json"

# --------------------------------------------------------------- job lifecycle
PLANNED = "PLANNED"
BRANCH_A_REALIZED = "BRANCH_A_REALIZED"
BRANCH_A_PUBLISHED = "BRANCH_A_PUBLISHED"
CALIBRATION_CONDITION_BOUND = "CALIBRATION_CONDITION_BOUND"
CALIBRATION_LOCKED = "CALIBRATION_LOCKED"
BRANCH_B_UNBLINDED = "BRANCH_B_UNBLINDED"
ANALYSED = "ANALYSED"
RECORDED = "RECORDED"

#: The frozen dependency graph, as explicit transitions rather than call order.
#: A case that evaluates no P1 / Block-1 quantity has no calibration states, so
#: its Branch-B prerequisite is publication ALONE -- which is the frozen rule,
#: and is not weakened by the absence of a calibration step.
CALIBRATING_TRANSITIONS = {
    PLANNED: (BRANCH_A_REALIZED,),
    BRANCH_A_REALIZED: (BRANCH_A_PUBLISHED,),
    BRANCH_A_PUBLISHED: (CALIBRATION_CONDITION_BOUND,),
    CALIBRATION_CONDITION_BOUND: (CALIBRATION_LOCKED,),
    CALIBRATION_LOCKED: (BRANCH_B_UNBLINDED,),
    BRANCH_B_UNBLINDED: (ANALYSED,),
    ANALYSED: (RECORDED,),
    RECORDED: (),
}
NON_CALIBRATING_TRANSITIONS = {
    PLANNED: (BRANCH_A_REALIZED,),
    BRANCH_A_REALIZED: (BRANCH_A_PUBLISHED,),
    BRANCH_A_PUBLISHED: (BRANCH_B_UNBLINDED,),
    BRANCH_B_UNBLINDED: (ANALYSED,),
    ANALYSED: (RECORDED,),
    RECORDED: (),
}


# ------------------------------------------------------------- job descriptors
@dataclass(frozen=True, order=True)
class JobCoordinates:
    """The complete scientific address of one job. Never partial."""

    case_id: str
    subcondition_id: str
    replicate_id: int
    scope: str

    def as_dict(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "subcondition_id": self.subcondition_id,
                "replicate_id": self.replicate_id, "scope": self.scope}

    @property
    def job_id(self) -> str:
        return (f"{self.case_id}|{self.subcondition_id}|{self.replicate_id:06d}|"
                f"{self.scope}")


@dataclass(frozen=True)
class CampaignJob:
    """One planned scientific job. Produced with NO RNG in scope."""

    coordinates: JobCoordinates
    role: str
    requires_calibration: bool
    seed_families: tuple[str, ...]
    branch_a_scopes: tuple[str, ...]
    result_kind: str
    depends_on: tuple[str, ...]

    @property
    def job_id(self) -> str:
        return self.coordinates.job_id

    @property
    def transitions(self) -> Mapping[str, tuple[str, ...]]:
        return (CALIBRATING_TRANSITIONS if self.requires_calibration
                else NON_CALIBRATING_TRANSITIONS)

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.coordinates.as_dict(),
            "role": self.role,
            "requires_calibration": self.requires_calibration,
            "seed_families": list(self.seed_families),
            "branch_a_scopes": list(self.branch_a_scopes),
            "result_kind": self.result_kind,
            "depends_on": list(self.depends_on),
        }


#: What each case's job produces. Read as a label, not as a threshold.
RESULT_KIND_BY_ENDPOINT = {
    "COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4": "complete_pass",
    "P1_FALSE_REJECTION_RATE_PER_FIELD": "p1_rejection",
    "G5_BLOCK_SIZE": "g5_block_rejection",
    "BLOCK1_ACHIEVED_SIZE": "block1_rejection",
    "P1_REJECTION_RATE_PER_CELL": "p1_rejection",
    "P1_REJECTION_RATE_PER_RHO": "p1_rejection",
    "P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE": "false_bridge_acceptance",
    "P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY": "paired_scale_recovery",
}


def plan_campaign(plan: Mapping[str, Any]) -> tuple[CampaignJob, ...]:
    """Enumerate the COMPLETE campaign from the frozen plan. RNG-FREE.

    Deterministic by construction: the frozen case order, then the frozen
    subcondition order, then the replicate index, then the case's declared field
    scopes. Planning twice yields identical descriptors, and no filesystem,
    clock, environment variable or hash-ordering input is read.
    """
    jobs: list[CampaignJob] = []
    for case in plan["cases"]:
        scope = CaseCalibrationScope.from_plan(case["case_id"], plan)
        endpoint = case["primary_release_endpoint"]
        if endpoint not in RESULT_KIND_BY_ENDPOINT:
            raise CampaignPlanMismatch(
                f"case {case['case_id']!r} declares release endpoint {endpoint!r}, "
                "for which the driver has no result kind. The driver must not guess "
                "what a case produces.")
        families = tuple(case["allowed_seed_families"])
        branch_a = ((EXPERIMENT_SCOPE,) if ValidationSeedFamily.BRANCH_A_MEASUREMENT.value
                    in families else ())
        for sub in case["subconditions"]:
            for replicate in range(case["replicate_count"]):
                previous = ""
                for field_scope in case["fields_affected"]:
                    coordinates = JobCoordinates(case["case_id"], sub["subcondition_id"],
                                                 replicate, field_scope)
                    jobs.append(CampaignJob(
                        coordinates=coordinates,
                        role=case["role"],
                        requires_calibration=scope.requires_calibration,
                        seed_families=families,
                        branch_a_scopes=branch_a + (field_scope,),
                        result_kind=RESULT_KIND_BY_ENDPOINT[endpoint],
                        # Fields of one replicate share the experiment-scope
                        # common mode, so they are ordered but not independent.
                        depends_on=(previous,) if previous else (),
                    ))
                    previous = coordinates.job_id
    return tuple(jobs)


def campaign_shape(plan: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    """Per-case job counts, derived from the plan without materialising jobs."""
    shape: dict[str, dict[str, int]] = {}
    for case in plan["cases"]:
        scope = CaseCalibrationScope.from_plan(case["case_id"], plan)
        subs = len(case["subconditions"])
        fields = len(case["fields_affected"])
        replicates = case["replicate_count"]
        shape[case["case_id"]] = {
            "subconditions": subs,
            "replicates": replicates,
            "field_scopes": fields,
            "jobs": subs * replicates * fields,
            "calibration_jobs": subs * replicates * fields if scope.requires_calibration else 0,
        }
    return shape


def require_plan_driver_agreement(plan: Mapping[str, Any],
                                  jobs: Sequence[CampaignJob]) -> dict[str, int]:
    """The driver's job plan must equal the frozen plan. Both directions."""
    expected: set[str] = set()
    expected_meta: dict[str, tuple[bool, tuple[str, ...]]] = {}
    for case in plan["cases"]:
        scope = CaseCalibrationScope.from_plan(case["case_id"], plan)
        families = tuple(case["allowed_seed_families"])
        for sub in case["subconditions"]:
            for replicate in range(case["replicate_count"]):
                for field_scope in case["fields_affected"]:
                    jid = JobCoordinates(case["case_id"], sub["subcondition_id"],
                                         replicate, field_scope).job_id
                    expected.add(jid)
                    expected_meta[jid] = (scope.requires_calibration, families)
    produced = {job.job_id for job in jobs}
    if len(produced) != len(jobs):
        raise CampaignPlanMismatch("the driver produced duplicate job identities")
    missing = sorted(expected - produced)
    extra = sorted(produced - expected)
    if missing or extra:
        raise CampaignPlanMismatch(
            f"driver/plan disagreement: {len(missing)} missing planned jobs "
            f"(e.g. {missing[:3]}), {len(extra)} extra driver jobs "
            f"(e.g. {extra[:3]})")
    for job in jobs:
        needs, families = expected_meta[job.job_id]
        if job.requires_calibration != needs:
            raise CampaignPlanMismatch(
                f"{job.job_id}: driver says requires_calibration="
                f"{job.requires_calibration}, the plan says {needs}")
        if job.seed_families != families:
            raise CampaignPlanMismatch(
                f"{job.job_id}: driver families {job.seed_families} != plan {families}")
    return {"planned_jobs": len(expected), "driver_jobs": len(produced),
            "missing_planned_jobs": 0, "extra_driver_jobs": 0}


# ------------------------------------------------------ Branch-A realisation
@dataclass(frozen=True)
class BranchARealisation:
    """IMMUTABLE Branch-A evidence, bound to its complete scientific coordinates.

    This is the object the frozen rule is about. It carries the realised
    Branch-A measurement -- the H_A the analysis will actually receive, the
    measured temperature, stiffnesses and orientation, the relaxation times and
    the declared scale factor -- together with every coordinate and identity that
    says WHICH experiment it belongs to.

    Floats are canonicalised through `float.hex()` (`e1a_v4.calibration.
    canonical_float`), the convention already used by `CalibrationCondition`, so
    the digest is exact rather than rounded text.
    """

    coordinates: JobCoordinates
    field_id: str
    branch_a_seed: int
    common_mode_seed: int
    H_A: tuple[tuple[float, ...], ...]
    T_measured: float
    k_modes_measured: tuple[float, ...]
    rot_deg_measured: float
    tau_modes: tuple[float, ...]
    scale_factor: float
    n_samples: int
    dt: float
    calibration_route: str
    branch_a_status: str
    contract_sha256: str
    plan_sha256: str
    analysis_identity: str
    generator_identity: str

    def __post_init__(self) -> None:
        if self.field_id != self.coordinates.scope:
            raise BranchAProvenanceMismatch(
                f"Branch-A evidence is for field {self.field_id!r} but its "
                f"coordinates declare scope {self.coordinates.scope!r}")
        if self.n_samples < 2 or self.dt <= 0.0:
            raise BranchAProvenanceMismatch(
                "Branch-A evidence needs the declared observation length and dt")
        if len(self.tau_modes) != len(self.H_A):
            raise BranchAProvenanceMismatch(
                "Branch-A evidence needs one relaxation time per mode")

    @classmethod
    def from_branch_a_field(cls, coordinates: JobCoordinates, field: BranchAField,
                            *, branch_a_seed: int, common_mode_seed: int,
                            n_samples: int, dt: float, binding: ExecutionBinding,
                            generator_identity: str) -> "BranchARealisation":
        """Build the evidence record from the realised Branch-A measurement.

        `field` is the MEASURED field the analysis will receive, not the noiseless
        truth. Nothing about Branch B is read, and nothing is drawn here.
        """
        # jacobi orders eigenmodes ascending; carry each tau with its stiffness,
        # exactly as `truth_from_field` does, so the pairing invariant survives.
        paired = tuple(t for _, t in sorted(zip(field.k_modes, field.tau_modes)))
        return cls(
            coordinates=coordinates,
            field_id=field.field_id,
            branch_a_seed=branch_a_seed,
            common_mode_seed=common_mode_seed,
            H_A=tuple(tuple(float(v) for v in row) for row in field.H),
            T_measured=float(field.T),
            k_modes_measured=tuple(float(k) for k in field.k_modes),
            rot_deg_measured=float(field.rot_deg),
            tau_modes=paired,
            scale_factor=float(field.scale_factor),
            n_samples=int(n_samples),
            dt=float(dt),
            calibration_route=field.calibration_route,
            branch_a_status=field.status,
            contract_sha256=binding.binding.sha256,
            plan_sha256=binding.plan_sha256,
            analysis_identity=binding.analysis_identity,
            generator_identity=generator_identity,
        )

    def canonical(self) -> dict[str, Any]:
        """The exact hashing preimage. Order-independent by construction."""
        return {
            "schema": BRANCH_A_PUBLICATION_SCHEMA,
            "coordinates": self.coordinates.as_dict(),
            "field_id": self.field_id,
            "branch_a_seed": self.branch_a_seed,
            "common_mode_seed": self.common_mode_seed,
            "H_A": [[canonical_float(v) for v in row] for row in self.H_A],
            "T_measured": canonical_float(self.T_measured),
            "k_modes_measured": [canonical_float(k) for k in self.k_modes_measured],
            "rot_deg_measured": canonical_float(self.rot_deg_measured),
            "tau_modes": [canonical_float(t) for t in self.tau_modes],
            "scale_factor": canonical_float(self.scale_factor),
            "n_samples": self.n_samples,
            "dt": canonical_float(self.dt),
            "calibration_route": self.calibration_route,
            "branch_a_status": self.branch_a_status,
            "contract_sha256": self.contract_sha256,
            "plan_sha256": self.plan_sha256,
            "analysis_identity": self.analysis_identity,
            "generator_identity": self.generator_identity,
        }

    @property
    def evidence_sha256(self) -> str:
        return canonical_digest(self.canonical())

    def calibration_condition(self, binding: ExecutionBinding) -> CalibrationCondition:
        """The condition derived FROM THIS EXACT Branch-A evidence.

        This is the repository equivalent of
        `CalibrationCondition.from_branch_a_realisation(...)`. It is a function of
        the realisation and the frozen plan alone; the caller supplies no H, no n,
        no temporal law and no identity, so a condition cannot be prepared
        elsewhere and presented as Branch-A provenance.

        (It is NOT added as a classmethod on `CalibrationCondition` itself:
        `e1a_v4/calibration.py` is one of the SCIENTIFIC_MODULES bound by the
        analysis procedure identity, and this task must not move that identity.)
        """
        plan = binding.plan
        calibration = plan["calibration"]
        rules = plan["adopted_rules_unchanged"]
        request = CalibrationRequest(
            field_id=self.field_id,
            H_A=[list(row) for row in self.H_A],
            n=self.n_samples,
            phis=tuple(math.exp(-self.dt / t) for t in self.tau_modes),
            replicates=calibration["replicates"],
            alpha_1=rules["alpha_1"],
            theta_cap_deg=rules["theta_cap_deg"],
            procedure_identity=self.analysis_identity,
            contract_sha256=self.contract_sha256,
            plan_sha256=self.plan_sha256,
            dt=self.dt,
            tau_modes=self.tau_modes,
        )
        return request.condition()


# ------------------------------------------------------ Branch-A publication
def publication_basename(coordinates: JobCoordinates) -> str:
    """One immutable record per scientific coordinate. Deterministic, no clock."""
    return f"branch_a_{canonical_digest(coordinates.as_dict())}.json"


def publication_path(output_dir: str, coordinates: JobCoordinates) -> str:
    return os.path.join(output_dir, BRANCH_A_PUBLICATION_DIR,
                        publication_basename(coordinates))


def publish_branch_a(output_dir: str, realisation: BranchARealisation,
                     condition: CalibrationCondition | None,
                     binding: ExecutionBinding) -> str:
    """HASH AND PUBLISH Branch-A evidence. Durable, immutable, fail-closed.

    Returns the final published path. After this returns, the record exists at a
    read-only final path; a partial write never occupies it, and a second
    publication for the same coordinates refuses.
    """
    record = {
        "schema": BRANCH_A_PUBLICATION_SCHEMA,
        "state": BRANCH_A_PUBLISHED,
        "coordinates": realisation.coordinates.as_dict(),
        "branch_a_evidence": realisation.canonical(),
        "branch_a_evidence_sha256": realisation.evidence_sha256,
        "calibration_condition_sha256": condition.sha256 if condition else None,
        "package_identities": {
            "contract_sha256": binding.binding.sha256,
            "plan_sha256": binding.plan_sha256,
            "seed_map_sha256": binding.seed_map_sha256,
            "analysis_procedure_identity": binding.analysis_identity,
            "execution_identity": binding.execution_identity,
        },
        "not_execution_authorisation": True,
    }
    directory = os.path.join(output_dir, BRANCH_A_PUBLICATION_DIR)
    return publish_atomic(directory, publication_basename(realisation.coordinates),
                          record)


def verify_publication(output_dir: str, realisation: BranchARealisation,
                       binding: ExecutionBinding) -> dict[str, Any]:
    """Re-read published Branch-A evidence and prove it is the same evidence.

    Used on the unblind path and on restart. Every check is a recomputation, not
    a trusted field: the digest is recomputed from the published evidence, and
    the published evidence is compared with the realisation in hand.
    """
    path = publication_path(output_dir, realisation.coordinates)
    record = read_published(path, "the Branch-A publication record")
    if record.get("schema") != BRANCH_A_PUBLICATION_SCHEMA:
        raise BranchAEvidenceAltered(
            f"{path}: schema {record.get('schema')!r} is not "
            f"{BRANCH_A_PUBLICATION_SCHEMA!r}")
    if record.get("coordinates") != realisation.coordinates.as_dict():
        raise BranchAProvenanceMismatch(
            f"{path}: published coordinates {record.get('coordinates')!r} are not "
            f"{realisation.coordinates.as_dict()!r}")
    evidence = record.get("branch_a_evidence")
    recomputed = canonical_digest(evidence)
    if recomputed != record.get("branch_a_evidence_sha256"):
        raise BranchAEvidenceAltered(
            f"{path}: the published evidence hashes to {recomputed}, but the record "
            f"declares {record.get('branch_a_evidence_sha256')}. Published evidence "
            "and its digest must agree or neither is evidence.")
    if evidence != realisation.canonical():
        raise BranchAEvidenceAltered(
            f"{path}: the published Branch-A evidence is not the evidence held for "
            "these coordinates. Branch B may not be unblinded against substituted "
            "Branch-A evidence.")
    identities = record.get("package_identities") or {}
    for key, actual in (("contract_sha256", binding.binding.sha256),
                        ("plan_sha256", binding.plan_sha256),
                        ("seed_map_sha256", binding.seed_map_sha256),
                        ("analysis_procedure_identity", binding.analysis_identity)):
        if identities.get(key) != actual:
            raise BranchAProvenanceMismatch(
                f"{path}: published {key} {identities.get(key)!r} != current "
                f"{actual!r}; the package changed since publication")
    return record


# --------------------------------------------------------- Branch-B unblinding
@dataclass(frozen=True)
class BranchBUnblindToken:
    """Proof that every frozen prerequisite for Branch-B access holds.

    It is issued by `JobExecution.unblind`, never constructed by a caller who
    wants a Branch-B stream, and it names exactly what it was issued against.
    """

    coordinates: JobCoordinates
    branch_a_evidence_sha256: str
    publication_path: str
    calibration_condition_sha256: str | None
    calibration_artifact_sha256: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.coordinates.as_dict(),
            "branch_a_evidence_sha256": self.branch_a_evidence_sha256,
            "publication_path": os.path.basename(self.publication_path),
            "calibration_condition_sha256": self.calibration_condition_sha256,
            "calibration_artifact_sha256": self.calibration_artifact_sha256,
        }


class JobExecution:
    """The state machine for ONE scientific job. The only route to Branch B.

    Ordering is enforced by state, not by call convention: every method that
    advances the chain checks the frozen transition table first, and
    `branch_b_seed` refuses unless the unblind token exists.
    """

    def __init__(self, job: CampaignJob, binding: ExecutionBinding,
                 calibration: ReplicateCalibration, output_dir: str) -> None:
        if calibration.scope.case_id != job.coordinates.case_id:
            raise BranchAProvenanceMismatch(
                f"calibration scope is {calibration.scope.case_id!r}, job is "
                f"{job.coordinates.case_id!r}")
        if calibration.subcondition_id != job.coordinates.subcondition_id:
            raise BranchAProvenanceMismatch(
                f"calibration is for subcondition {calibration.subcondition_id!r}, "
                f"job is {job.coordinates.subcondition_id!r}")
        if calibration.replicate != job.coordinates.replicate_id:
            raise BranchAProvenanceMismatch(
                f"calibration is for replicate {calibration.replicate}, job is "
                f"{job.coordinates.replicate_id}")
        if calibration.scope.requires_calibration != job.requires_calibration:
            raise BranchAProvenanceMismatch(
                "calibration scope disagrees with the job's calibration requirement")
        self.job = job
        self.binding = binding
        self.calibration = calibration
        self.output_dir = output_dir
        self._state = PLANNED
        self._realisation: BranchARealisation | None = None
        self._publication_path: str | None = None
        self._condition: CalibrationCondition | None = None
        self._artifact_digest: str | None = None
        self._token: BranchBUnblindToken | None = None
        self._result: dict[str, Any] | None = None

    # ----------------------------------------------------------------- state
    @property
    def state(self) -> str:
        return self._state

    @property
    def coordinates(self) -> JobCoordinates:
        return self.job.coordinates

    def _require_transition(self, target: str) -> None:
        """Check the transition BEFORE doing the work."""
        allowed = self.job.transitions.get(self._state, ())
        if target not in allowed:
            raise JobStateInvalid(
                f"{self.job.job_id}: {self._state} -> {target} is not a permitted "
                f"transition; from {self._state} this job may only go to "
                f"{list(allowed)}. The dependency graph is the authority, not the "
                "order in which methods happen to be called.")

    def _enter(self, target: str) -> None:
        """Enter the state only AFTER the work succeeded.

        Checking and entering are separate on purpose: a step that refuses must
        leave the job exactly where it was. Advancing first would let a refused
        publication or a refused lock satisfy the precondition of the next step.
        """
        self._require_transition(target)
        self._state = target

    # ------------------------------------------------------------ step 1 & 2
    def realise_branch_a(self, field: BranchAField, *, branch_a_seed: int,
                         common_mode_seed: int,
                         generator_identity: str) -> BranchARealisation:
        """Bind the realised Branch-A measurement to these exact coordinates."""
        self._require_transition(BRANCH_A_REALIZED)
        plan_branch_b = self.binding.plan["generating_model"]["branch_b"]
        realisation = BranchARealisation.from_branch_a_field(
            self.coordinates, field, branch_a_seed=branch_a_seed,
            common_mode_seed=common_mode_seed,
            n_samples=plan_branch_b["n_samples"], dt=plan_branch_b["dt_s"],
            binding=self.binding, generator_identity=generator_identity)
        expected_seed = self.calibration.branch_a_seed(self.coordinates.scope)
        if branch_a_seed != expected_seed:
            raise BranchAProvenanceMismatch(
                f"{self.job.job_id}: Branch-A evidence carries seed identity "
                f"{branch_a_seed}, but this job's declared Branch-A stream is "
                f"{expected_seed}. Evidence from another stream is not this "
                "replicate's Branch-A measurement.")
        if common_mode_seed != self.calibration.common_mode_seed():
            raise BranchAProvenanceMismatch(
                f"{self.job.job_id}: the common-mode stream identity is not this "
                "experiment's. The Branch-A common mode is drawn ONCE per "
                "experiment and shared across its fields; a per-field redraw would "
                "destroy the cancellation P2 depends on.")
        self._enter(BRANCH_A_REALIZED)
        self._realisation = realisation
        return realisation

    # ------------------------------------------------------------ step 3 & 4
    def publish_branch_a(self) -> str:
        """Hash and publish. Branch B stays unreachable until this succeeds."""
        if self._realisation is None:
            raise BranchANotPublished(
                f"{self.job.job_id}: no Branch-A evidence has been realised")
        self._require_transition(BRANCH_A_PUBLISHED)
        condition = (self._realisation.calibration_condition(self.binding)
                     if self.job.requires_calibration else None)
        path = publish_branch_a(self.output_dir, self._realisation, condition,
                                self.binding)
        self._enter(BRANCH_A_PUBLISHED)
        self._publication_path = path
        return path

    # ---------------------------------------------------------------- step 5
    def calibration_condition(self) -> CalibrationCondition:
        """Derive the condition from the PUBLISHED Branch-A object, not an argument."""
        if not self.job.requires_calibration:
            raise JobStateInvalid(
                f"{self.job.job_id}: case {self.coordinates.case_id!r} evaluates no "
                "P1 / Block-1 quantity and has no calibration condition. Giving it "
                "one would create a refusal path that cannot affect the science but "
                "CAN affect the outcome.")
        if self._realisation is None:
            raise BranchANotPublished(f"{self.job.job_id}: Branch A is not realised")
        self._require_transition(CALIBRATION_CONDITION_BOUND)
        verify_publication(self.output_dir, self._realisation, self.binding)
        condition = self._realisation.calibration_condition(self.binding)
        self._enter(CALIBRATION_CONDITION_BOUND)
        self._condition = condition
        return condition

    def calibration_seed(self) -> int:
        """The calibration stream, available only once the condition is bound."""
        if self._state != CALIBRATION_CONDITION_BOUND:
            raise JobStateInvalid(
                f"{self.job.job_id}: the calibration stream is available only after "
                f"the condition is derived from published Branch-A evidence; state "
                f"is {self._state}")
        return self.calibration.calibration_seed(self.coordinates.scope)

    # ---------------------------------------------------------------- step 6
    def lock_calibration(self, artifact: CalibrationArtifact) -> str:
        """Lock the artifact against the condition DERIVED here, never a supplied one."""
        if self._condition is None:
            raise JobStateInvalid(
                f"{self.job.job_id}: no calibration condition has been derived from "
                "published Branch-A evidence")
        self._require_transition(CALIBRATION_LOCKED)
        # Coded provenance checks BEFORE delegating, so a substituted artifact
        # names the reason rather than surfacing as an uncoded ordering refusal.
        if artifact.field_id != self.coordinates.scope:
            raise BranchAProvenanceMismatch(
                f"{self.job.job_id}: the artifact is calibrated for field "
                f"{artifact.field_id!r}, presented for {self.coordinates.scope!r}")
        if artifact.condition.sha256 != self._condition.sha256:
            difference = self._condition.first_difference(artifact.condition)
            raise BranchAProvenanceMismatch(
                f"{self.job.job_id}: the artifact was calibrated at a different "
                f"condition (first difference: {difference}). A condition that merely "
                "looks numerically similar is not this job's published Branch-A "
                "evidence.")
        digest = self.calibration.lock(self.coordinates.scope, artifact, self._condition)
        self._enter(CALIBRATION_LOCKED)
        self._artifact_digest = digest
        return digest

    # ---------------------------------------------------------------- step 7
    def unblind(self) -> BranchBUnblindToken:
        """Issue the Branch-B token, only if every frozen predicate holds."""
        if self._realisation is None:
            raise BranchANotPublished(
                f"{self.job.job_id}: Branch B may not be unblinded before Branch-A "
                "evidence exists")
        if self._publication_path is None:
            raise BranchANotPublished(
                f"{self.job.job_id}: Branch-A evidence has not been published. The "
                "frozen rule is that Branch-A output is hashed and PUBLISHED before "
                "Branch B is unblinded.")
        self._require_transition(BRANCH_B_UNBLINDED)
        verify_publication(self.output_dir, self._realisation, self.binding)
        if self.job.requires_calibration:
            if self._condition is None or self._artifact_digest is None:
                raise BranchBPremature(
                    f"{self.job.job_id}: the calibration artifact is not locked")
            locked = self.calibration.artifact(self.coordinates.scope)
            if locked.condition.sha256 != self._condition.sha256:
                raise BranchBPremature(
                    f"{self.job.job_id}: the locked artifact's condition is not the "
                    "one derived from this job's published Branch-A evidence")
        self._enter(BRANCH_B_UNBLINDED)
        self._token = BranchBUnblindToken(
            coordinates=self.coordinates,
            branch_a_evidence_sha256=self._realisation.evidence_sha256,
            publication_path=self._publication_path,
            calibration_condition_sha256=(self._condition.sha256
                                          if self._condition else None),
            calibration_artifact_sha256=self._artifact_digest,
        )
        return self._token

    def branch_b_seed(self, family: ValidationSeedFamily | None = None) -> int:
        """THE ONLY route to a Branch-B stream. Refuses without the token.

        Deriving a seed constructs no generator and draws no number; the four
        stages -- derivation, construction, draw, trajectory -- stay separate.
        """
        if self._token is None:
            raise BranchBPremature(
                f"{self.job.job_id}: Branch-B access was requested in state "
                f"{self._state}. Branch B becomes reachable only after Branch-A "
                "evidence is published"
                + (" and its calibration artifact is locked."
                   if self.job.requires_calibration else "."))
        requested = family or self._default_branch_b_family()
        return self.calibration.validation_seed(self.coordinates.scope, requested)

    def _default_branch_b_family(self) -> ValidationSeedFamily:
        """The case's declared Branch-B family, read from the plan, never guessed."""
        declared = self.job.seed_families
        for candidate in (ValidationSeedFamily.BLINDED_SCALE_CONTROL,
                          ValidationSeedFamily.VALIDATION):
            if candidate.value in declared:
                return candidate
        raise BranchBPremature(
            f"{self.job.job_id}: the frozen plan grants this case no Branch-B "
            f"family; it declares {list(declared)}")

    @property
    def token(self) -> BranchBUnblindToken | None:
        return self._token

    # ---------------------------------------------------------------- step 8-9
    def analyse(self, outcome: Mapping[str, Any]) -> None:
        """Record the analysis outcome. Refusals stay refusals."""
        if self._token is None:
            raise BranchBPremature(
                f"{self.job.job_id}: nothing may be analysed before Branch B is "
                "unblinded")
        self._require_transition(ANALYSED)
        self._enter(ANALYSED)
        self._result = dict(outcome)

    def record(self, aggregate: Mapping[str, Any], fields: Sequence[str]) -> dict[str, Any]:
        """Finalise, requiring every MANDATORY CONTRACT DIAGNOSTIC to be present."""
        if self._result is None:
            raise JobStateInvalid(f"{self.job.job_id}: nothing has been analysed")
        self._require_transition(RECORDED)
        require_mandatory_diagnostics(dict(aggregate), self.binding.plan, tuple(fields))
        self._enter(RECORDED)
        return {"schema": RESULT_SCHEMA, **self.coordinates.as_dict(),
                "branch_a_evidence_sha256": self._realisation.evidence_sha256,
                "result": self._result}

    # ------------------------------------------------------------- immutability
    def republish_branch_a(self, realisation: BranchARealisation) -> str:
        """Always refuses. Published Branch-A evidence is immutable."""
        raise BranchAPublicationImmutable(
            f"{self.job.job_id}: Branch-A evidence for these coordinates is already "
            "published. It may not be replaced, edited, republished with a different "
            "hash, or rebound to other coordinates -- least of all once Branch B has "
            "been unblinded against it.")


def replicate_calibration_for(binding: ExecutionBinding, job: CampaignJob,
                              ledger: CampaignCalibrationLedger) -> ReplicateCalibration:
    """The per-replicate calibration boundary for one job's coordinates.

    Built from the FROZEN plan through the validated loaders: the case's declared
    calibration scope and its case-scoped seed authorisation. The driver never
    derives a seed itself and never constructs a generator.
    """
    scope = CaseCalibrationScope.from_plan(job.coordinates.case_id, binding.plan)
    access = binding.case_access(job.coordinates.case_id)
    return ReplicateCalibration(scope, access, job.coordinates.subcondition_id,
                                job.coordinates.replicate_id, ledger)


def job_execution(binding: ExecutionBinding, job: CampaignJob,
                  ledger: CampaignCalibrationLedger, output_dir: str,
                  calibration: ReplicateCalibration | None = None) -> "JobExecution":
    """The official route to a JobExecution. Shares one ReplicateCalibration
    across the fields of a replicate, because they share its common mode."""
    return JobExecution(job, binding,
                        calibration or replicate_calibration_for(binding, job, ledger),
                        output_dir)


# ---------------------------------------------------------------- restart
def verify_restart(output_dir: str, realisations: Mapping[str, BranchARealisation],
                   binding: ExecutionBinding) -> dict[str, int]:
    """Re-verify every published record on resume. Never regenerate, never replace.

    A completed replicate is never re-run because its outcome was undesirable;
    this only proves that what was published is still exactly what was published.
    """
    verified = 0
    for realisation in realisations.values():
        verify_publication(output_dir, realisation, binding)
        verified += 1
    return {"verified_publications": verified}


# ---------------------------------------------------------------- manifest
def campaign_manifest(binding: ExecutionBinding, root: str = ".") -> dict[str, Any]:
    """The deterministic PRE-EXECUTION manifest. Contains no seal and no outcome."""
    plan = binding.plan
    frozen = plan["frozen_identities"]
    shape = campaign_shape(plan)
    diagnostics = [
        {"diagnostic_id": row["diagnostic_id"], "case_id": row["case_id"],
         "authority_path": row["authority_path"], "aggregate_key": row["aggregate_key"]}
        for row in plan["release_authority"]["mandatory_diagnostics"]
    ]
    manifest = {
        "schema": CAMPAIGN_MANIFEST_SCHEMA,
        "state": "DRIVER_PRESENT_UNSEALED",
        "not_execution_authorisation": True,
        "identities": {
            "foundation_sha256": frozen["foundation_sha256"],
            "baseline_sha256": frozen["baseline_sha256"],
            "contract_sha256": binding.binding.sha256,
            "design_sha256": frozen["design_sha256"],
            "analysis_procedure_identity": binding.analysis_identity,
            "plan_json_sha256": binding.plan_sha256,
            "plan_markdown_sha256": sha256_file(os.path.join(root, PLAN_MARKDOWN)),
            "seed_map_sha256": binding.seed_map_sha256,
            "execution_identity": binding.execution_identity,
            "official_campaign_driver_path": OFFICIAL_CAMPAIGN_DRIVER_PATH,
            "official_campaign_driver_sha256": driver_identity_component(root),
            "validation_modules": list(VALIDATION_MODULES),
        },
        "final_expected_execution_identity": frozen["final_expected_execution_identity"],
        "execution_authorised": plan["execution_authorised"],
        "campaign": {
            "cases": shape,
            "total_jobs": sum(c["jobs"] for c in shape.values()),
            "total_calibration_jobs": sum(c["calibration_jobs"] for c in shape.values()),
        },
        "result_schema": RESULT_SCHEMA,
        "manifest_schema": MANIFEST_SCHEMA,
        "mandatory_diagnostics": diagnostics,
        "output_directory": binding.output_dir,
    }
    for key in ("foundation_sha256", "baseline_sha256", "contract_sha256",
                "design_sha256", "analysis_procedure_identity", "plan_json_sha256",
                "plan_markdown_sha256", "seed_map_sha256", "execution_identity",
                "official_campaign_driver_sha256"):
        if not manifest["identities"].get(key):
            raise CampaignManifestInvalid(f"the campaign manifest omits {key!r}")
    return manifest


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    return canonical_digest(manifest)


# ------------------------------------------------------------- the entry point
def run_campaign(root: str = ".", *, output_dir: str | None = None,
                 plan_only: bool = False,
                 rng_factory: Any = None) -> dict[str, Any]:
    """THE official campaign entry point, declared in e1a_v4/validation/driver.py.

    `plan_only` performs the complete RNG-free planning phase and returns the
    manifest. The stochastic path refuses: the execution seal is not frozen and
    `execution_authorised` is false. There is deliberately no force, skip-seal or
    ignore-authorisation parameter -- an escape hatch is exactly the thing this
    package exists to not have.
    """
    binding = bind_execution(root=root, output_dir=output_dir)
    jobs = plan_campaign(binding.plan)
    agreement = require_plan_driver_agreement(binding.plan, jobs)
    manifest = campaign_manifest(binding, root)
    if plan_only:
        return {"manifest": manifest, "manifest_sha256": manifest_digest(manifest),
                "agreement": agreement, "jobs": len(jobs),
                "rng_objects": 0, "random_draws": 0, "trajectories": 0}
    # --- the stochastic path -------------------------------------------------
    # The execution gate lives in the runner and is not duplicated here. The
    # driver refuses on its own account as well, so importing and calling it
    # directly cannot become a way around the gate.
    from .seal import load_seal
    seal = load_seal(root)
    if not seal.is_frozen or not binding.plan.get("execution_authorised", False):
        raise Refusal(
            "EXECUTION REFUSED: the official campaign driver is PRESENT but the "
            f"execution seal is {seal.state} and execution_authorised is "
            f"{binding.plan.get('execution_authorised', False)}. A driver that "
            "exists is not a driver that may run: the seal is frozen by a reviewer "
            "after the driver is independently audited, and authorisation is a "
            "separate task again. No RNG was constructed."
        )
    raise Refusal(
        "EXECUTION REFUSED: the stochastic execution stage is not implemented in "
        "this task. The driver's planning, provenance, publication and unblind "
        "machinery are complete and statically tested; drawing the first random "
        "number is a separately authorised stage."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=OFFICIAL_CAMPAIGN_DRIVER_MODULE,
        description="E1a v4 official campaign driver (planning and provenance)")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--plan-only", action="store_true",
                        help="RNG-free planning and manifest generation")
    parser.add_argument("--preflight-only", action="store_true",
                        help="fail-closed preflight only; plans nothing")
    args = parser.parse_args(argv)
    try:
        if args.preflight_only:
            binding = bind_execution(root=args.root, output_dir=args.output_dir)
            print("PREFLIGHT PASSED")
            print(f"  execution identity  : {binding.execution_identity}")
            print(f"  official driver     : {OFFICIAL_CAMPAIGN_DRIVER_PATH} "
                  f"({driver_identity_component(args.root)[:16]}...)")
            print(f"  entry point         : {OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT}")
            print("  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)")
            return 0
        result = run_campaign(root=args.root, output_dir=args.output_dir,
                              plan_only=True)
    except Refusal as exc:
        text = str(exc)
        print(text if text.startswith("EXECUTION REFUSED") else f"REFUSED: {text}")
        print("  RANDOM DRAWS: 0   TRAJECTORIES: 0")
        return 2
    manifest = result["manifest"]
    print("CAMPAIGN PLAN COMPLETE (RNG-FREE)")
    print(f"  planned jobs        : {result['jobs']}")
    print(f"  calibration jobs    : {manifest['campaign']['total_calibration_jobs']}")
    print(f"  manifest sha256     : {result['manifest_sha256']}")
    print(f"  execution identity  : {manifest['identities']['execution_identity']}")
    print(f"  lifecycle state     : {manifest['state']}")
    print(f"  execution_authorised: {manifest['execution_authorised']}")
    print(f"  final expected id   : {manifest['final_expected_execution_identity']}")
    if not args.plan_only:
        print("EXECUTION NOT ATTEMPTED: pass --plan-only explicitly; the stochastic "
              "path refuses while the seal is unfrozen and execution is unauthorised")
    print("  RNG OBJECTS: 0   RANDOM DRAWS: 0   TRAJECTORIES: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
