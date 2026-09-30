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
from fractions import Fraction
import os
import re
import struct
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from ..branch_a import BranchAField, stiffness_matrix
from ..contract import sha256_file
from ..calibration import (
    BLOCK1_GATES, CalibrationArtifact, CalibrationCondition, canonical_float,
)
from ..effective_size import sigma_stat
from ..endpoints import (
    UncertaintyModel, p1_geometry, p2_cross_field, p3_absolute, p4_consistency,
)
from ..geometry import analyse_field
from ..numerics import Refusal
from .calibrate import CalibrationRequest, generate_block1_artifact
from .classification import CampaignCounts, classify_campaign
from .coherence import derived_n_samples
from .dispositions import cp_upper
from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_identity_component,
    require_canonical_driver,
)
from .generate import (
    BranchAErrorModel, Generator, ou_observations, truth_from_field,
)
from . import PLAN_MARKDOWN
from .plan import ExecutionBinding, VALIDATION_MODULES, bind_execution
from .publication import (
    COMMIT_SCHEMA, PublicationReceipt, canonical_digest, canonical_json,
    publish_transaction, read_committed, require_clean_inventory, sealed_digest,
)
from .refusals import (
    BranchAEvidenceAltered, BranchAMeasurementInvalid, CodedRefusal, BranchANotPublished, BranchAProvenanceMismatch,
    BranchAPublicationImmutable, BranchBPremature,
    CalibrationArtifactBindingInvalid, CalibrationLockFieldMismatch,
    CalibrationLockJobMismatch, CalibrationLockMissing,
    CalibrationLockProvenanceMismatch, CalibrationLockUnplanned,
    CalibrationLockWithoutPublication, CampaignIncomplete,
    CampaignManifestInvalid, CampaignPlanMismatch,
    ContractMandatoryDiagnosticMissing, EndpointEventMissing,
    EndpointEventReductionUndeclared, ExecutionAuthorisationMissing,
    JobStateInvalid, PublicationDigestMismatch, PublicationIncomplete,
    RestartInventoryMismatch, ResultCaseMismatch, ResultFieldSetMismatch,
    ResultSchemaInvalid, ScaleControlInvalid, StochasticProviderRefused,
    TerminalProvenanceMismatch,
)
from .release_authority import (
    mandatory_diagnostics_for, require_mandatory_diagnostics,
)
from .results import (
    CAMPAIGN_RESULT_SCHEMA, JOB_RECORD_SCHEMA, MANIFEST_SCHEMA, RESULT_SCHEMA,
    aggregate_skeleton,
)
from .scope import (
    CampaignCalibrationLedger, CaseCalibrationScope, ReplicateCalibration,
)
from .seal import require_execution_gate
from .seeds import EXPERIMENT_SCOPE, ValidationSeedFamily

#: Schema of the immutable Branch-A publication record. Version 2 adds the
#: `publication_digest` that authenticates the COMPLETE provenance envelope. An
#: independent audit demonstrated that version 1, authenticated by the Branch-A
#: evidence hash alone, accepted a record whose execution identity,
#: calibration-condition hash or publication state had been edited. No official
#: publication exists, so the break is free to make explicit now.
BRANCH_A_PUBLICATION_SCHEMA = "e1a_v4_branch_a_publication/2"

#: The Branch-A measurement generator, named by the frozen plan itself
#: (`generating_model.branch_a`, "generate.BranchAErrorModel.measure"). Recorded
#: as provenance on every realisation; it is a pointer to the frozen
#: implementation, never a scientific constant restated here.
BRANCH_A_GENERATOR_IDENTITY = "e1a_v4.validation.generate.BranchAErrorModel.measure"
#: Schema of the deterministic pre-execution campaign manifest.
CAMPAIGN_MANIFEST_SCHEMA = "e1a_v4_campaign_manifest/1"

#: Where Branch-A publications live, relative to the campaign output directory.
BRANCH_A_PUBLICATION_DIR = "branch_a"
#: Where terminal job records live. A completed job is one whose TERMINAL RECORD
#: is durably committed, not one whose Branch-A evidence happens to exist: an
#: independent audit found restart trusting a caller's list for exactly this
#: question, and the answer has to come from persisted storage.
JOB_RECORD_DIR = "job_records"
#: Where the COMMITTED calibration-lock records live. One per calibrating job.
#:
#: THE DEFECT THIS DIRECTORY CLOSES
#:     A terminal record carries `calibration_artifact_sha256`, and until this
#:     store existed that value had no external referent anywhere: the adopted
#:     STREAMING_PER_REPLICATE implementation finalises, locks and SPENDS each
#:     artifact, so the only persisted evidence was the terminal record's own
#:     claim about itself. An audit set the field to null and to a fabricated
#:     digest, re-digested the record, and validation accepted both -- necessarily
#:     so, because there was nothing to check the claim against.
#:
#:     The lock is now durably committed at the moment it happens, BEFORE Branch B
#:     is unblinded, through the same publish-then-commit transaction Branch-A
#:     evidence uses. The terminal record is checked against it.
CALIBRATION_LOCK_DIR = "calibration_locks"
CAMPAIGN_MANIFEST_BASENAME = "campaign_manifest.json"

#: Schema of the immutable calibration-lock record.
CALIBRATION_LOCK_SCHEMA = "e1a_v4_calibration_lock/1"
#: Every key a calibration-lock record must carry. Checked before belief.
CALIBRATION_LOCK_KEYS = (
    "job_id", "coordinates", "branch_a_evidence_sha256",
    "publication_basename", "publication_digest",
    "calibration_condition_sha256", "calibration_artifact_sha256",
    "artifact_field_id", "analysis_procedure_identity",
    "package_identities", "lock_digest",
)

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
#: Every key a published Branch-A record carries. EXACT: a missing key and an
#: unknown key are both refusals, so a record cannot gain an unauthenticated
#: field or lose an authenticated one and still parse.
PUBLICATION_FIELDS = (
    "schema", "state", "coordinates", "branch_a_evidence",
    "branch_a_evidence_sha256", "calibration_condition_sha256",
    "package_identities", "not_execution_authorisation", "publication_digest",
)
#: The package identities a publication binds. Recomputed on every read.
PUBLICATION_IDENTITIES = (
    "contract_sha256", "plan_sha256", "seed_map_sha256",
    "analysis_procedure_identity", "execution_identity",
)


def publication_basename(coordinates: JobCoordinates) -> str:
    """One immutable record per scientific coordinate. Deterministic, no clock."""
    return f"branch_a_{canonical_digest(coordinates.as_dict())}.json"


def publication_path(output_dir: str, coordinates: JobCoordinates) -> str:
    return os.path.join(publication_directory(output_dir),
                        publication_basename(coordinates))


def publication_directory(output_dir: str) -> str:
    return os.path.join(output_dir, BRANCH_A_PUBLICATION_DIR)


def publication_envelope(realisation: "BranchARealisation",
                         condition: CalibrationCondition | None,
                         binding: ExecutionBinding) -> dict[str, Any]:
    """The COMPLETE provenance envelope, authenticated as ONE object.

    THE DEFECT THIS CLOSES
        The first revision authenticated the record by the Branch-A evidence hash
        alone. An independent audit demonstrated the consequence: the published
        execution identity, the calibration-condition hash and the publication
        state could each be edited while verification still accepted the record.
        Reproduced against the previous HEAD; all three escaped.

        A provenance field that nothing hashes is not provenance. Every field
        below is inside `publication_digest`, so editing ANY of them -- schema,
        state, coordinates, evidence, evidence digest, condition hash, or any
        package identity -- invalidates the publication.

    The digest deliberately excludes itself, so verification is a recomputation
    rather than a comparison of a field with itself.
    """
    envelope: dict[str, Any] = {
        "schema": BRANCH_A_PUBLICATION_SCHEMA,
        "state": BRANCH_A_PUBLISHED,
        "coordinates": realisation.coordinates.as_dict(),
        # The evidence already binds the Branch-A and common-mode seed
        # identities, the analysis identity and the generator identity; it is
        # carried whole rather than restated field by field.
        "branch_a_evidence": realisation.canonical(),
        "branch_a_evidence_sha256": realisation.evidence_sha256,
        "calibration_condition_sha256": condition.sha256 if condition else None,
        "package_identities": {
            "contract_sha256": binding.binding.sha256,
            "plan_sha256": binding.plan_sha256,
            "seed_map_sha256": binding.seed_map_sha256,
            "analysis_procedure_identity": binding.analysis_identity,
            # The execution identity already contains the canonical driver's own
            # file hash and every validation module, so binding it binds the
            # software that produced the evidence.
            "execution_identity": binding.execution_identity,
        },
        "not_execution_authorisation": True,
    }
    envelope["publication_digest"] = sealed_digest(envelope, "publication_digest")
    return envelope


def require_publication_schema(record: Mapping[str, Any], where: str) -> None:
    """Fail closed on a missing field, an unknown field, or a wrong type.

    Duplicate keys are already refused one layer down, by `strict_loads`: the
    parser never silently keeps the last of two values a human would read as the
    first.
    """
    keys = set(record)
    missing = sorted(set(PUBLICATION_FIELDS) - keys)
    unknown = sorted(keys - set(PUBLICATION_FIELDS))
    if missing or unknown:
        raise PublicationIncomplete(
            f"{where}: the published record is not the frozen publication schema "
            f"(missing {missing}, unknown {unknown}). An authoritative record "
            "carries exactly the declared fields: an unknown field is an "
            "unauthenticated channel and a missing one is a dropped guarantee.")
    if record["schema"] != BRANCH_A_PUBLICATION_SCHEMA:
        raise PublicationIncomplete(
            f"{where}: schema {record['schema']!r} is not "
            f"{BRANCH_A_PUBLICATION_SCHEMA!r}")
    if record["state"] != BRANCH_A_PUBLISHED:
        raise PublicationIncomplete(
            f"{where}: publication state {record['state']!r} is not "
            f"{BRANCH_A_PUBLISHED!r}")
    if record["not_execution_authorisation"] is not True:
        raise PublicationIncomplete(
            f"{where}: a publication record always states that it is not an "
            "execution authorisation")
    for key, kind in (("coordinates", dict), ("branch_a_evidence", dict),
                      ("package_identities", dict),
                      ("branch_a_evidence_sha256", str),
                      ("publication_digest", str)):
        if not isinstance(record[key], kind):
            raise PublicationIncomplete(
                f"{where}: {key!r} must be {kind.__name__}, found "
                f"{type(record[key]).__name__}")
    for key in ("branch_a_evidence_sha256", "publication_digest"):
        if not re.fullmatch(r"[0-9a-f]{64}", record[key]):
            raise PublicationIncomplete(
                f"{where}: {key} {record[key]!r} is not a sha256 digest")
    condition = record["calibration_condition_sha256"]
    if condition is not None and not (isinstance(condition, str)
                                      and re.fullmatch(r"[0-9a-f]{64}", condition)):
        raise PublicationIncomplete(
            f"{where}: calibration_condition_sha256 must be null or a sha256 "
            f"digest, found {condition!r}")
    identities = record["package_identities"]
    missing = sorted(set(PUBLICATION_IDENTITIES) - set(identities))
    unknown = sorted(set(identities) - set(PUBLICATION_IDENTITIES))
    if missing or unknown:
        raise PublicationIncomplete(
            f"{where}: package identities are not the declared set "
            f"(missing {missing}, unknown {unknown})")
    coordinates = record["coordinates"]
    if sorted(coordinates) != ["case_id", "replicate_id", "scope", "subcondition_id"]:
        raise PublicationIncomplete(
            f"{where}: coordinates {sorted(coordinates)} are not the complete "
            "scientific address")


def publish_branch_a(output_dir: str, realisation: "BranchARealisation",
                     condition: CalibrationCondition | None,
                     binding: ExecutionBinding) -> PublicationReceipt:
    """HASH, PUBLISH and COMMIT Branch-A evidence. Durable, immutable, closed.

    Returns only when a reader may treat the evidence as published: the artifact
    is durable AND its commit marker is durable. If it raises, no reader will,
    whatever residue remains on disk -- which is the invariant the audit found
    missing.
    """
    envelope = publication_envelope(realisation, condition, binding)
    return publish_transaction(
        publication_directory(output_dir),
        publication_basename(realisation.coordinates),
        envelope,
        publication_digest=envelope["publication_digest"],
        provenance={
            "coordinates": realisation.coordinates.as_dict(),
            "branch_a_evidence_sha256": realisation.evidence_sha256,
            "execution_identity": binding.execution_identity,
        },
    )


#: Sentinel for "the caller did not state an expected calibration condition",
#: which is different from "the caller states there must be none".
_UNSTATED = object()


def verify_publication(output_dir: str, realisation: "BranchARealisation",
                       binding: ExecutionBinding,
                       expected_condition_sha256: Any = _UNSTATED) -> dict[str, Any]:
    """Re-read committed Branch-A evidence and prove it is the same evidence.

    Used on the unblind path and on restart. EVERY check is a recomputation, not
    a trusted field: the commit marker is verified against the bytes on disk, the
    publication digest is recomputed over the whole envelope, the evidence digest
    is recomputed from the published evidence, and the published evidence is
    compared with the realisation in hand.
    """
    directory = publication_directory(output_dir)
    basename = publication_basename(realisation.coordinates)
    path = os.path.join(directory, basename)
    record, marker = read_committed(directory, basename,
                                    "the Branch-A publication record")
    require_publication_schema(record, path)
    recomputed = sealed_digest(record, "publication_digest")
    if recomputed != record["publication_digest"]:
        raise PublicationDigestMismatch(
            f"{path}: the published envelope hashes to {recomputed}, but the record "
            f"declares {record['publication_digest']}. Some bound provenance field "
            "was edited after publication. The evidence hash alone is not the "
            "authentication; the envelope is.")
    if marker.get("publication_digest") != record["publication_digest"]:
        raise PublicationDigestMismatch(
            f"{path}: the commit marker committed publication digest "
            f"{marker.get('publication_digest')!r}, the record carries "
            f"{record['publication_digest']!r}. A marker commits one exact envelope.")
    if record["coordinates"] != realisation.coordinates.as_dict():
        raise BranchAProvenanceMismatch(
            f"{path}: published coordinates {record['coordinates']!r} are not "
            f"{realisation.coordinates.as_dict()!r}")
    expected_basename = publication_basename(
        JobCoordinates(**record["coordinates"]))
    if expected_basename != basename:
        raise BranchAProvenanceMismatch(
            f"{path}: a record whose coordinates address {expected_basename!r} is "
            f"filed at {basename!r}; the path is a pure function of the coordinates "
            "and a misfiled record is not this replicate's publication")
    evidence = record["branch_a_evidence"]
    recomputed = canonical_digest(evidence)
    if recomputed != record["branch_a_evidence_sha256"]:
        raise BranchAEvidenceAltered(
            f"{path}: the published evidence hashes to {recomputed}, but the record "
            f"declares {record['branch_a_evidence_sha256']}. Published evidence "
            "and its digest must agree or neither is evidence.")
    if evidence != realisation.canonical():
        raise BranchAEvidenceAltered(
            f"{path}: the published Branch-A evidence is not the evidence held for "
            "these coordinates. Branch B may not be unblinded against substituted "
            "Branch-A evidence.")
    identities = record["package_identities"]
    for key, actual in (("contract_sha256", binding.binding.sha256),
                        ("plan_sha256", binding.plan_sha256),
                        ("seed_map_sha256", binding.seed_map_sha256),
                        ("analysis_procedure_identity", binding.analysis_identity),
                        ("execution_identity", binding.execution_identity)):
        if identities.get(key) != actual:
            raise BranchAProvenanceMismatch(
                f"{path}: published {key} {identities.get(key)!r} != current "
                f"{actual!r}; the package changed since publication")
    if expected_condition_sha256 is not _UNSTATED:
        if record["calibration_condition_sha256"] != expected_condition_sha256:
            raise BranchAProvenanceMismatch(
                f"{path}: the publication carries calibration condition "
                f"{record['calibration_condition_sha256']!r}, this job derived "
                f"{expected_condition_sha256!r} from its own Branch-A evidence")
    return record


# ----------------------------------------------- the LOCKED calibration artifact
def calibration_lock_directory(output_dir: str) -> str:
    return os.path.join(output_dir, CALIBRATION_LOCK_DIR)


def calibration_lock_basename(coordinates: JobCoordinates) -> str:
    """One immutable lock record per scientific coordinate. Deterministic."""
    return f"calibration_lock_{canonical_digest(coordinates.as_dict())}.json"


def is_sha256(value: Any) -> bool:
    """A syntactically well-formed SHA-256 identity: 64 lowercase hex digits."""
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def calibration_lock_envelope(coordinates: JobCoordinates,
                              artifact: CalibrationArtifact,
                              condition: CalibrationCondition,
                              artifact_sha256: str,
                              publication: Mapping[str, Any],
                              binding: ExecutionBinding) -> dict[str, Any]:
    """The COMPLETE calibration link, authenticated as ONE object.

    Every hop of the chain frozen authority requires is written down together, so
    a later reader checks the whole thing rather than four unrelated fields:

        committed Branch-A publication
              -> the CalibrationCondition derived from that published evidence
              -> the artifact calibrated at that condition, and LOCKED
              -> the terminal record that names it

    The Branch-A evidence hash and the publication digest are copied FROM the
    committed publication rather than from the caller, so a lock record cannot
    cite evidence that was never published.
    """
    record: dict[str, Any] = {
        "schema": CALIBRATION_LOCK_SCHEMA,
        "job_id": coordinates.job_id,
        "coordinates": coordinates.as_dict(),
        "branch_a_evidence_sha256": publication["branch_a_evidence_sha256"],
        "publication_basename": publication_basename(coordinates),
        "publication_digest": publication["publication_digest"],
        "calibration_condition_sha256": condition.sha256,
        "calibration_artifact_sha256": artifact_sha256,
        "artifact_field_id": artifact.field_id,
        "artifact_schema": artifact.schema,
        "artifact_replicates": artifact.replicates,
        "artifact_alpha_1": artifact.alpha_1,
        "analysis_procedure_identity": artifact.procedure_identity,
        "package_identities": {
            "contract_sha256": binding.binding.sha256,
            "plan_sha256": binding.plan_sha256,
            "seed_map_sha256": binding.seed_map_sha256,
            "analysis_procedure_identity": binding.analysis_identity,
            "execution_identity": binding.execution_identity,
        },
        "not_execution_authorisation": True,
    }
    record["lock_digest"] = sealed_digest(record, "lock_digest")
    return record


def require_calibration_lock_schema(record: Mapping[str, Any], where: str) -> None:
    """Strict shape and self-authentication, before any field is believed."""
    if record.get("schema") != CALIBRATION_LOCK_SCHEMA:
        raise CalibrationLockProvenanceMismatch(
            f"{where}: schema {record.get('schema')!r} is not "
            f"{CALIBRATION_LOCK_SCHEMA!r}")
    missing = [k for k in CALIBRATION_LOCK_KEYS if k not in record]
    if missing:
        raise CalibrationLockProvenanceMismatch(
            f"{where}: the calibration-lock record omits {missing}")
    if sealed_digest(dict(record), "lock_digest") != record["lock_digest"]:
        raise CalibrationLockProvenanceMismatch(
            f"{where}: the calibration-lock record's own digest does not "
            "authenticate its bytes")
    if not is_sha256(record["calibration_artifact_sha256"]):
        raise CalibrationLockProvenanceMismatch(
            f"{where}: the locked artifact identity "
            f"{record['calibration_artifact_sha256']!r} is not a SHA-256 identity")


def publish_calibration_lock(output_dir: str, job: CampaignJob,
                             artifact: CalibrationArtifact,
                             condition: CalibrationCondition,
                             artifact_sha256: str,
                             binding: ExecutionBinding) -> PublicationReceipt:
    """Durably COMMIT the fact that this exact artifact was locked for this job.

    Written at the moment of the lock and BEFORE Branch B is unblinded, so the
    external record of the threshold exists before anything that could depend on
    the threshold's value does. It goes through the same two-step transaction as
    Branch-A evidence: a record with no commit marker is an orphan, and is
    refused rather than promoted.
    """
    coordinates = job.coordinates
    # VERIFIED, not merely committed: a lock is a statement about the evidence it
    # is conditional on, so that evidence is proven valid before the lock cites it.
    publication = verified_publication(output_dir, job, binding)
    if publication is None:
        raise CalibrationLockWithoutPublication(
            f"{coordinates.job_id}: no committed Branch-A publication exists, so "
            "there is nothing for a calibration lock to be conditional on")
    record = calibration_lock_envelope(coordinates, artifact, condition,
                                       artifact_sha256, publication, binding)
    return publish_transaction(
        calibration_lock_directory(output_dir),
        calibration_lock_basename(coordinates), record,
        publication_digest=record["lock_digest"],
        provenance={"coordinates": coordinates.as_dict(),
                    "job_id": coordinates.job_id,
                    "execution_identity": binding.execution_identity})


def committed_calibration_lock(output_dir: str, coordinates: JobCoordinates
                               ) -> dict[str, Any] | None:
    """STRUCTURALLY load the committed lock at these coordinates' slot, or None.

    Resolves the canonical path from the coordinates, refuses anything present
    but not committed, checks the record's own digest and schema, and checks that
    the record's coordinates are the ones it was read for. It does NOT decide
    whether the lock is SEMANTICALLY this job's -- that is
    `verified_calibration_lock`, and this function is not a substitute for it.

    An audit found the difference mattered: a canonically committed lock whose
    own `job_id` or `artifact_field_id` named another job passed every structural
    check here, and the semantic checks lived downstream in terminal validation,
    so a lock with no terminal record yet was never semantically checked at all.
    """
    directory = calibration_lock_directory(output_dir)
    basename = calibration_lock_basename(coordinates)
    path = os.path.join(directory, basename)
    if not os.path.lexists(path):
        return None
    record, marker = read_committed(directory, basename,
                                    "the calibration-lock record")
    require_calibration_lock_schema(record, path)
    if marker["publication_digest"] != record["lock_digest"]:
        raise CalibrationLockProvenanceMismatch(
            f"{path}: the commit marker committed a different lock digest")
    if record.get("coordinates") != coordinates.as_dict():
        raise CalibrationLockJobMismatch(
            f"{path}: the lock record addresses {record.get('coordinates')!r} and "
            f"was read for {coordinates.as_dict()!r}; a misfiled lock is not this "
            "job's calibration")
    return record


def inventory_calibration_locks(output_dir: str) -> dict[str, dict[str, Any]]:
    """INDEPENDENTLY discover every committed calibration lock on disk.

    Nothing here consults an argument about what should exist, for the same
    reason `inventory_publications` does not: a store that is asked what the
    caller already believes cannot contradict the caller.
    """
    directory = calibration_lock_directory(output_dir)
    inventory = require_clean_inventory(directory, "the calibration-lock store")
    found: dict[str, dict[str, Any]] = {}
    for basename in inventory.committed:
        record, marker = read_committed(directory, basename,
                                        "a calibration-lock record")
        path = os.path.join(directory, basename)
        require_calibration_lock_schema(record, path)
        if marker["publication_digest"] != record["lock_digest"]:
            raise CalibrationLockProvenanceMismatch(
                f"{path}: the commit marker committed a different lock digest")
        coordinates = JobCoordinates(**record["coordinates"])
        # STORE LOCATION IDENTITY == LOCK RECORD IDENTITY. The basename is a pure
        # function of the coordinates, so this is what makes an alias impossible:
        # a second file holding the same coordinates cannot also be that
        # coordinate's canonical name, and is refused rather than shadowing it.
        if calibration_lock_basename(coordinates) != basename:
            raise CalibrationLockJobMismatch(
                f"{basename!r} holds the lock of {coordinates.job_id!r}, which "
                f"belongs at {calibration_lock_basename(coordinates)!r}")
        if coordinates.job_id in found:
            raise CalibrationLockJobMismatch(
                f"two committed locks claim {coordinates.job_id}; a job locks "
                "exactly one calibration artifact")
        found[coordinates.job_id] = record
    return found


# ---- EMBEDDED Branch-A FIELD AUTHORITY, DECLARED FIELD BY FIELD -------------
#: A DIGEST AUTHENTICATES BYTES. IT DOES NOT ESTABLISH AGREEMENT WITH AUTHORITY.
#:
#: THE DEFECT THIS TABLE CLOSES
#:     The previous repair bound the embedded PACKAGE identities to the current
#:     binding and classified everything else as "scientific value". That
#:     catch-all was wrong: several of those values are fixed externally, by the
#:     frozen job, the seed map, the validation plan or the design contract. An
#:     audit forged correctly committed, fully re-digested publications carrying
#:     another planned job's Branch-A seed, another subcondition's common-mode
#:     stream, n_samples 2,000,001 instead of 2,000,000, a doubled dt, and the
#:     calibration route the contract explicitly FORBIDS -- and the shared read
#:     verifier accepted every one of them.
#:
#:     Seed correctness was checked when evidence was CREATED and not when it was
#:     RECOVERED. That asymmetry is the defect: a read path that trusts what a
#:     write path proved is not a verifier.
#:
#: WHY A TABLE AND NOT A SEQUENCE OF SPECIAL CASES
#:     A chain of `if field == "dt"` checks cannot be audited for completeness and
#:     silently omits the next field someone adds. Every embedded field is
#:     declared here with its meaning, its authority class, where that authority
#:     comes from and which rule verifies it. The verifier DISPATCHES on the
#:     table, and a permanent test requires the table to cover exactly the keys
#:     `BranchARealisation.canonical()` emits -- no unclassified key, no stale row.
#: The closed set of Branch-A field statuses `BranchAField` can carry.
#: A realised field that fails its own validity check is BRANCH_A_INVALID,
#: and publishing one is legitimate -- the analysis then fails closed and
#: that refusal is a scientific RESULT. So the rule is closed-world
#: membership, not "must be VALID".
BRANCH_A_FIELD_STATUSES = ("VALID", "BRANCH_A_INVALID")

AUTHORITY_PACKAGE_BOUND = "PACKAGE_BOUND"
AUTHORITY_JOB_BOUND = "JOB_BOUND"
AUTHORITY_SEED_BOUND = "SEED_BOUND"
AUTHORITY_PLAN_BOUND = "PLAN_BOUND"
AUTHORITY_CONTRACT_BOUND = "CONTRACT_BOUND"
AUTHORITY_DERIVED = "DERIVED"
AUTHORITY_MEASURED = "MEASURED"
AUTHORITY_OPEN_UNRESOLVED = "OPEN_UNRESOLVED"

AUTHORITY_CLASSES = (
    AUTHORITY_PACKAGE_BOUND, AUTHORITY_JOB_BOUND, AUTHORITY_SEED_BOUND,
    AUTHORITY_PLAN_BOUND, AUTHORITY_CONTRACT_BOUND, AUTHORITY_DERIVED,
    AUTHORITY_MEASURED, AUTHORITY_OPEN_UNRESOLVED,
)

#: The classes whose authority fixes an EXACT value, which
#: `embedded_authority_expectations` must therefore supply.
AUTHORITY_CLASSES_WITH_EXPECTED_VALUE = (
    AUTHORITY_PACKAGE_BOUND, AUTHORITY_JOB_BOUND, AUTHORITY_SEED_BOUND,
    AUTHORITY_PLAN_BOUND,
)


@dataclass(frozen=True)
class EmbeddedFieldAuthority:
    """One embedded Branch-A evidence field and where its authority comes from."""

    field: str
    meaning: str
    authority_class: str
    authority_source: str
    rule: str


BRANCH_A_FIELD_AUTHORITY = (
    # ---- PACKAGE_BOUND: the package this evidence claims to come from --------
    EmbeddedFieldAuthority(
        "schema", "the frozen Branch-A publication schema",
        AUTHORITY_PACKAGE_BOUND, "BRANCH_A_PUBLICATION_SCHEMA", "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "contract_sha256", "the design contract this evidence was produced under",
        AUTHORITY_PACKAGE_BOUND, "binding.binding.sha256", "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "plan_sha256", "the validation plan this evidence was produced under",
        AUTHORITY_PACKAGE_BOUND, "binding.plan_sha256", "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "analysis_identity", "the analysis procedure identity",
        AUTHORITY_PACKAGE_BOUND, "binding.analysis_identity", "EQUALS_EXPECTED"),
    # ---- JOB_BOUND: the exact planned scientific job ------------------------
    EmbeddedFieldAuthority(
        "coordinates", "the complete scientific address of this job",
        AUTHORITY_JOB_BOUND, "the frozen planner (plan_campaign)",
        "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "field_id", "the field/scope this evidence measures",
        AUTHORITY_JOB_BOUND, "job.coordinates.scope", "EQUALS_EXPECTED"),
    # ---- SEED_BOUND: streams authorised for THESE coordinates ---------------
    EmbeddedFieldAuthority(
        "branch_a_seed", "the per-field Branch-A measurement stream identity",
        AUTHORITY_SEED_BOUND,
        "CaseSeedAccess.stream(branch_a_measurement, sub, replicate, scope)",
        "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "common_mode_seed",
        "the Branch-A COMMON-MODE stream: ONE per experiment, SHARED across the "
        "fields of a replicate, which is why it cancels in P2 and not in P3",
        AUTHORITY_SEED_BOUND,
        "CaseSeedAccess.stream(branch_a_measurement, sub, replicate, "
        "EXPERIMENT_SCOPE)", "EQUALS_EXPECTED"),
    # ---- PLAN_BOUND: frozen generating-model primitives ---------------------
    EmbeddedFieldAuthority(
        "dt", "the Branch-B sampling interval, seconds -- a plan PRIMITIVE",
        AUTHORITY_PLAN_BOUND, "plan.generating_model.branch_b.dt_s",
        "EQUALS_EXPECTED"),
    # ---- CONTRACT_BOUND: the anti-circularity route rule -------------------
    EmbeddedFieldAuthority(
        "calibration_route", "how the Branch-A stiffness was calibrated",
        AUTHORITY_CONTRACT_BOUND,
        "contract.information_separation.authorised_branch_A_routes and "
        "forbidden_branch_A_routes", "CONTRACT_ROUTE"),
    # ---- DERIVED: mechanically determined by authoritative primitives -------
    EmbeddedFieldAuthority(
        "n_samples", "the Branch-B record length in samples",
        AUTHORITY_DERIVED,
        "int(round(T_total_s / dt_s)), exactly as e1a_v4.world.World derives it "
        "and as the plan's own surface map declares it DERIVED",
        "EQUALS_EXPECTED"),
    EmbeddedFieldAuthority(
        "branch_a_status", "whether the realised field is usable",
        AUTHORITY_DERIVED, "BranchAField.status, a closed set of two values",
        "STATUS_ENUM"),
    EmbeddedFieldAuthority(
        "tau_modes",
        "per-mode relaxation times tau_r = gamma / k_r, carried with ASCENDING "
        "k so the pairing survives -- deliberately not sorted(tau)",
        AUTHORITY_DERIVED,
        "the frozen pairing rule. The absolute values depend on gamma = 6 pi eta "
        "a, whose inputs are the ACKNOWLEDGED OPEN field-construction gap, so "
        "only the pairing and arity are verifiable here",
        "TAU_PAIRING"),
    # ---- MEASURED: realised Branch-A observations ---------------------------
    # These vary by design. Comparing them with a predetermined number would
    # validate a procedure nobody proposes to run.
    EmbeddedFieldAuthority(
        "H_A", "the realised Branch-A stiffness matrix the analysis receives",
        AUTHORITY_MEASURED, "realised measurement", "FLOAT_MATRIX"),
    EmbeddedFieldAuthority(
        "T_measured", "the measured temperature, carrying thermometry error",
        AUTHORITY_MEASURED, "realised measurement", "FLOAT"),
    EmbeddedFieldAuthority(
        "k_modes_measured", "the measured per-mode stiffnesses",
        AUTHORITY_MEASURED, "realised measurement", "FLOAT_LIST"),
    EmbeddedFieldAuthority(
        "rot_deg_measured", "the measured trap-axis orientation",
        AUTHORITY_MEASURED, "realised measurement", "FLOAT"),
    EmbeddedFieldAuthority(
        "scale_factor",
        "the declared scale factor AFTER the common-mode perturbation "
        "scale_factor * (1 + sigma_cm * common_mode); it is realised, not fixed",
        AUTHORITY_MEASURED,
        "realised measurement; BranchAField.__post_init__ requires it > 0",
        "POSITIVE_FLOAT"),
    # ---- OPEN_UNRESOLVED: authority genuinely not frozen yet ----------------
    EmbeddedFieldAuthority(
        "generator_identity",
        "which code produced the Branch-A measurement",
        AUTHORITY_OPEN_UNRESOLVED,
        "NOT DECLARED by frozen authority. generating_model.branch_a describes "
        "the MODEL in prose; the only generator_identity the plan declares "
        "anywhere belongs to CALIBRATION. Choosing an authoritative value is a "
        "pre-seal decision and is NOT made here.",
        "NON_EMPTY_STRING"),
)

#: field -> its authority row. Built once; the table is the single source.
BRANCH_A_FIELD_AUTHORITY_BY_FIELD = {row.field: row
                                     for row in BRANCH_A_FIELD_AUTHORITY}

#: field -> authority class. Kept as the coarse view earlier code and reports use.
EMBEDDED_EVIDENCE_CLASSIFICATION = {row.field: row.authority_class
                                    for row in BRANCH_A_FIELD_AUTHORITY}

#: The embedded keys carrying CURRENT-PACKAGE authority, derived from the table.
EMBEDDED_PACKAGE_IDENTITY_FIELDS = tuple(sorted(
    row.field for row in BRANCH_A_FIELD_AUTHORITY
    if row.authority_class == AUTHORITY_PACKAGE_BOUND))

#: Every embedded field whose value is fixed OUTSIDE the record, derived from the
#: table. These are the ones a forger must not be able to choose.
EXTERNALLY_BOUND_EMBEDDED_FIELDS = tuple(sorted(
    row.field for row in BRANCH_A_FIELD_AUTHORITY
    if row.authority_class in (AUTHORITY_PACKAGE_BOUND, AUTHORITY_JOB_BOUND,
                               AUTHORITY_SEED_BOUND, AUTHORITY_PLAN_BOUND,
                               AUTHORITY_CONTRACT_BOUND, AUTHORITY_DERIVED)))


def authority_class_counts() -> dict[str, int]:
    """MACHINE-DERIVED totals. Never hard-coded in a report."""
    counts = {name: 0 for name in AUTHORITY_CLASSES}
    for row in BRANCH_A_FIELD_AUTHORITY:
        counts[row.authority_class] += 1
    counts["total"] = len(BRANCH_A_FIELD_AUTHORITY)
    return counts


#: Embedded key -> the OUTER envelope key restating the SAME identity. The two
#: spellings differ for the analysis identity, which is exactly why they were
#: never noticed to be two independently editable sources of one truth.
EMBEDDED_TO_OUTER_IDENTITY = (
    ("contract_sha256", "contract_sha256"),
    ("plan_sha256", "plan_sha256"),
    ("analysis_identity", "analysis_procedure_identity"),
)


def embedded_authority_expectations(job: CampaignJob,
                                    binding: ExecutionBinding) -> dict[str, Any]:
    """The value frozen authority REQUIRES for every field that fixes one.

    Every expectation is obtained INDEPENDENTLY of the record being checked --
    from the current binding, the frozen planned job, the seed map through its
    own scoped interface, and the validated plan. Nothing is read from the
    publication, the evidence, a downstream lock or a terminal record.

    No seed arithmetic happens here. `CaseSeedAccess.stream` is the frozen
    authorisation boundary and is the only route to a stream identity; deriving
    one constructs no generator and draws no number.
    """
    branch_b = binding.plan["generating_model"]["branch_b"]
    access = binding.case_access(job.coordinates.case_id)
    subcondition = job.coordinates.subcondition_id
    replicate = job.coordinates.replicate_id
    return {
        # PACKAGE_BOUND
        "schema": BRANCH_A_PUBLICATION_SCHEMA,
        "contract_sha256": binding.binding.sha256,
        "plan_sha256": binding.plan_sha256,
        "analysis_identity": binding.analysis_identity,
        # JOB_BOUND
        "coordinates": job.coordinates.as_dict(),
        "field_id": job.coordinates.scope,
        # SEED_BOUND -- through the frozen scoped seed interface
        "branch_a_seed": access.stream(
            ValidationSeedFamily.BRANCH_A_MEASUREMENT, subcondition, replicate,
            job.coordinates.scope),
        "common_mode_seed": access.stream(
            ValidationSeedFamily.BRANCH_A_MEASUREMENT, subcondition, replicate,
            EXPERIMENT_SCOPE),
        # PLAN_BOUND -- the plan's own primitive, never a literal in driver code
        "dt": canonical_float(float(branch_b["dt_s"])),
        # DERIVED -- recomputed from the plan's primitives by the plan layer's
        # own function, so the driver does not define the derivation
        "n_samples": derived_n_samples(branch_b),
    }


def _is_canonical_float(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        float.fromhex(value)
    except (TypeError, ValueError):
        return False
    return True


def _rule_equals_expected(evidence, row, expectations, binding, where) -> None:
    if row.field not in expectations:
        raise BranchAProvenanceMismatch(
            f"{where}: {row.field!r} is classified {row.authority_class} but no "
            "expectation was derived for it; a bound field with no expectation is "
            "an unverified field")
    expected = expectations[row.field]
    value = evidence.get(row.field)
    # SHAPE BEFORE VALUE, so "this is not even a string" stays distinguishable
    # from "this is the wrong string". Both refuse; they refuse differently.
    if isinstance(expected, str) and (not isinstance(value, str) or not value):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is {value!r}; the frozen evidence "
            "schema carries it as a non-empty string")
    if isinstance(expected, bool) or not isinstance(expected, (str, dict)):
        if isinstance(value, bool) or not isinstance(value, type(expected)):
            raise PublicationIncomplete(
                f"{where}: embedded {row.field} is {value!r}; the frozen evidence "
                f"schema carries it as {type(expected).__name__}")
    if isinstance(expected, dict) and not isinstance(value, dict):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is {value!r}; the frozen evidence "
            "schema carries it as an object")
    if value != expected:
        raise BranchAProvenanceMismatch(
            f"{where}: the Branch-A evidence embeds {row.field} "
            f"{value!r}; {row.authority_class} authority "
            f"({row.authority_source}) requires {expected!r}. Recomputing the "
            "evidence and envelope digests makes the record self-consistent; it "
            "does not make it conform to authority.")


def _rule_contract_route(evidence, row, expectations, binding, where) -> None:
    route = evidence.get(row.field)
    if not isinstance(route, str) or not route:
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is {route!r}; the schema carries it "
            "as a non-empty string")
    if route in binding.binding.forbidden_branch_a_routes:
        raise BranchAProvenanceMismatch(
            f"{where}: ANTI-CIRCULARITY. The published Branch-A evidence declares "
            f"calibration route {route!r}, which the adopted contract FORBIDS. "
            f"Authorised: {list(binding.binding.authorised_branch_a_routes)}")
    if route not in binding.binding.authorised_branch_a_routes:
        raise BranchAProvenanceMismatch(
            f"{where}: calibration route {route!r} is not on the contract's "
            f"authorised list {list(binding.binding.authorised_branch_a_routes)}; "
            "refusing rather than assuming")


def _rule_status_enum(evidence, row, expectations, binding, where) -> None:
    status = evidence.get(row.field)
    if status not in BRANCH_A_FIELD_STATUSES:
        raise BranchAProvenanceMismatch(
            f"{where}: embedded {row.field} {status!r} is not one of the declared "
            f"Branch-A field statuses {list(BRANCH_A_FIELD_STATUSES)}. A status "
            "outside the closed set cannot be branched on.")


def _rule_tau_pairing(evidence, row, expectations, binding, where) -> None:
    """SHAPE and the pairing ORDER only.

    The substantive relation -- that one shared drag coefficient produces every
    recorded tau -- is a JOINT constraint and lives in
    `require_branch_a_measurement_invariants`, because it needs the recorded
    stiffnesses too. An audit showed why the order check alone is not enough: a
    tau rescaled so the sequence stays non-increasing preserved the order and
    still broke the relation.
    """
    taus = evidence.get(row.field)
    modes = evidence.get("H_A")
    if not isinstance(taus, list) or not all(_is_canonical_float(t) for t in taus):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is not a list of canonical floats")
    if not isinstance(modes, list) or len(taus) != len(modes):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} carries {len(taus)} relaxation "
            "time(s); the frozen rule is one per mode")
    values = [float.fromhex(t) for t in taus]
    # tau_r = gamma / k_r with ONE gamma, carried with ASCENDING k, so the stored
    # order is non-increasing. A shuffled list is a broken pairing.
    if any(b > a for a, b in zip(values, values[1:])):
        raise BranchAMeasurementInvalid(
            f"{where}: embedded {row.field} is not carried with ascending "
            "stiffness. tau_r = gamma / k_r, so the frozen pairing gives a "
            "non-increasing sequence; this one is not, and a mispaired tau "
            "changes every phi and the whole Block-1 null law.")


def _rule_float(evidence, row, expectations, binding, where) -> None:
    """A finite canonically encoded float. Domain, not value: a measurement is
    free to be any value production would accept."""
    if not _is_canonical_float(evidence.get(row.field)):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} {evidence.get(row.field)!r} is not a "
            "canonically encoded float")
    _persisted_float(evidence, row.field, where)


def _rule_positive_float(evidence, row, expectations, binding, where) -> None:
    """Finite AND strictly positive, because that is exactly what
    `BranchAField.__post_init__` requires of this field."""
    _rule_float(evidence, row, expectations, binding, where)
    if _persisted_float(evidence, row.field, where) <= 0.0:
        raise BranchAMeasurementInvalid(
            f"{where}: embedded {row.field} is not positive; the production "
            "constructor refuses to build a Branch-A measurement with it")


def _rule_float_list(evidence, row, expectations, binding, where) -> None:
    value = evidence.get(row.field)
    if not isinstance(value, list) or not value or not all(
            _is_canonical_float(v) for v in value):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is not a non-empty list of "
            "canonically encoded floats")


def _rule_float_matrix(evidence, row, expectations, binding, where) -> None:
    value = evidence.get(row.field)
    if (not isinstance(value, list) or not value
            or not all(isinstance(r, list) and r
                       and all(_is_canonical_float(v) for v in r) for r in value)
            or len({len(r) for r in value}) != 1):
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is not a rectangular matrix of "
            "canonically encoded floats")


def _rule_non_empty_string(evidence, row, expectations, binding, where) -> None:
    value = evidence.get(row.field)
    if not isinstance(value, str) or not value:
        raise PublicationIncomplete(
            f"{where}: embedded {row.field} is {value!r}; the schema carries it "
            "as a non-empty string")


#: rule name -> implementation. The verifier dispatches; it does not branch on
#: field names.
_AUTHORITY_RULES = {
    "EQUALS_EXPECTED": _rule_equals_expected,
    "CONTRACT_ROUTE": _rule_contract_route,
    "STATUS_ENUM": _rule_status_enum,
    "TAU_PAIRING": _rule_tau_pairing,
    "FLOAT": _rule_float,
    "POSITIVE_FLOAT": _rule_positive_float,
    "FLOAT_LIST": _rule_float_list,
    "FLOAT_MATRIX": _rule_float_matrix,
    "NON_EMPTY_STRING": _rule_non_empty_string,
}


def require_embedded_field_authority(record: Mapping[str, Any], job: CampaignJob,
                                     binding: ExecutionBinding,
                                     where: str) -> None:
    """Verify EVERY embedded Branch-A field against its declared authority.

    Table-driven: one row per embedded field, one rule per row, dispatched. The
    expectations are derived independently of the record, so a forger who edits
    an embedded value and recomputes every digest down through the lock and the
    terminal record still disagrees with the only thing that can tell -- frozen
    authority.
    """
    evidence = record.get("branch_a_evidence")
    if not isinstance(evidence, dict):
        raise PublicationIncomplete(
            f"{where}: the published Branch-A evidence is not an object")
    unknown = sorted(set(evidence) - set(BRANCH_A_FIELD_AUTHORITY_BY_FIELD))
    if unknown:
        raise PublicationIncomplete(
            f"{where}: the published Branch-A evidence carries undeclared "
            f"field(s) {unknown}; an unknown field is an unauthenticated channel")
    expectations = embedded_authority_expectations(job, binding)
    for row in BRANCH_A_FIELD_AUTHORITY:
        if row.field not in evidence:
            raise PublicationIncomplete(
                f"{where}: the published Branch-A evidence omits {row.field!r}, "
                f"which the frozen evidence schema requires "
                f"({row.authority_class})")
        _AUTHORITY_RULES[row.rule](evidence, row, expectations, binding, where)
    # ONE package identity per publication, not two editable copies of it.
    identities = record.get("package_identities") or {}
    for embedded_key, outer_key in EMBEDDED_TO_OUTER_IDENTITY:
        if evidence.get(embedded_key) != identities.get(outer_key):
            raise BranchAProvenanceMismatch(
                f"{where}: embedded {embedded_key} {evidence.get(embedded_key)!r} "
                f"disagrees with the envelope's {outer_key} "
                f"{identities.get(outer_key)!r}. One publication carries one "
                "package identity, not two editable copies of it.")
    if evidence.get("schema") != record.get("schema"):
        raise BranchAProvenanceMismatch(
            f"{where}: the embedded evidence schema {evidence.get('schema')!r} is "
            f"not the envelope's {record.get('schema')!r}")
    # THE RECORD AS A WHOLE. Per-field authority is necessary and not sufficient:
    # every field can be individually valid while the combination is one the
    # production constructor could never have produced.
    require_branch_a_measurement_invariants(evidence, where)



# ---- Branch-A MEASUREMENT INVARIANTS: the record as a WHOLE ----------------
#: INDIVIDUALLY VALID FIELDS ARE NOT A VALID MEASUREMENT.
#:
#: THE DEFECT THIS SECTION CLOSES
#:     The field-authority repair verified each embedded field against its own
#:     authority. An audit then forged records in which every field was
#:     individually well-formed and externally authorised, the record was
#:     correctly re-digested and durably committed, and the COMBINATION could
#:     never have come out of the production constructor:
#:
#:         H_A altered while the recorded stiffnesses, orientation, temperature
#:           and scale stayed exactly as published
#:         relaxation times no single drag coefficient could produce
#:         T_measured = -1
#:         scale_factor = -1
#:
#:     A committed digest authenticates the record's bytes. It says nothing about
#:     whether those bytes form a physically and algorithmically possible
#:     Branch-A measurement.
#:
#: HOW THE EXPECTATIONS ARE OBTAINED
#:     By REUSING the production constructor. `reconstructed_branch_a_field`
#:     rebuilds a real `BranchAField` from the persisted primitives, so every
#:     creation-time domain rule `BranchAField.__post_init__` enforces is enforced
#:     again on read, and the derived values are taken from its own properties --
#:     `.H` and `.status`. No production formula is restated here, and
#:     `e1a_v4/branch_a.py` is NOT modified: it is one of the SCIENTIFIC_MODULES
#:     and the analysis identity must not move for a provenance repair.
#:
#: WHAT IS NOT DONE
#:     Measured values are NOT pinned to nominal plan values. A measurement is
#:     free to be any value inside the production constructor's declared domain.
#:     The absolute drag coefficient gamma is NOT chosen, estimated or frozen: it
#:     is not persisted, it is the acknowledged-open field-construction input, and
#:     the relaxation check below is deliberately scale-free in gamma.
@dataclass(frozen=True)
class BranchAInvariant:
    """One joint constraint on a persisted Branch-A record."""

    invariant_id: str
    dependent_fields: tuple[str, ...]
    primitive_sources: tuple[str, ...]
    production_rule: str
    verification: str


BRANCH_A_MEASUREMENT_INVARIANTS = (
    BranchAInvariant(
        "H_A_FROM_PRIMITIVES", ("H_A",),
        ("k_modes_measured", "rot_deg_measured", "T_measured", "scale_factor"),
        "BranchAField.H = stiffness_matrix(k_modes, rot_deg) * scale_factor "
        "/ (K_B * T)",
        "recomputed by reconstructing the production BranchAField from the "
        "persisted primitives and reading its own .H property; compared exactly, "
        "because every persisted float is an exact float.hex() and the operation "
        "order is the production one"),
    BranchAInvariant(
        "STATUS_FROM_H_U", ("branch_a_status",),
        ("k_modes_measured", "rot_deg_measured"),
        "BranchAField.__post_init__ sets BRANCH_A_INVALID when min eig(H_U) <= 0",
        "recomputed from the same reconstruction and compared exactly"),
    BranchAInvariant(
        "TAU_SINGLE_GAMMA", ("tau_modes",), ("k_modes_measured",),
        "tau_r = fl(gamma / k_r) for ONE shared BINARY64 gamma, itself the "
        "rounded product 6 pi eta a, carried with ASCENDING k",
        "exact rational feasibility that some gamma yields every recorded tau, "
        "with each rounding cell owning its endpoints by the IEEE ties-to-even "
        "rule, AND that the intersection of those exact regions contains a finite "
        "binary64 -- production divides by a representable value, not by a real "
        "number -- confirmed by replaying that witness through the real division; "
        "plus the exact consequence that equal stiffnesses give equal relaxation "
        "times. No gamma value is chosen and no tolerance is introduced"),
    BranchAInvariant(
        "RELAXATION_DOMAIN", ("tau_modes", "H_A"),
        ("k_modes_measured", "T_measured", "scale_factor"),
        "production evaluates tau_r = gamma / k_r and H = H_U * scale / (K_B * T) "
        "in binary64 and then SERIALIZES the result: a zero stiffness makes the "
        "division undefined, a temperature whose K_B * T underflows to zero makes "
        "it raise, and a product that overflows to infinity is refused by "
        "canonical_float -- each of them before any record exists",
        "the persisted record must lie in the IMAGE of the production constructor "
        "AND serializer, so every one of those conditions becomes a coded "
        "BRANCH_A_MEASUREMENT_INVALID on read and never a raw ZeroDivisionError, "
        "OverflowError or uncoded Refusal"),
    BranchAInvariant(
        "PRODUCTION_DOMAIN",
        ("T_measured", "scale_factor", "H_A"),
        ("T_measured", "scale_factor", "k_modes_measured", "rot_deg_measured"),
        "BranchAField.__post_init__ refuses a non-symmetric H_U, a temperature "
        "that is not positive, an x_star dimension mismatch, and a scale factor "
        "that is not positive",
        "the production constructor is CALLED on the persisted primitives; its "
        "own refusals become coded provenance refusals"),
)


def _finite(value: float) -> bool:
    return isinstance(value, float) and math.isfinite(value)


def _persisted_float(evidence: Mapping[str, Any], key: str, where: str) -> float:
    value = evidence.get(key)
    try:
        number = float.fromhex(value)
    except (AttributeError, TypeError, ValueError):
        raise BranchAMeasurementInvalid(
            f"{where}: embedded {key} {value!r} is not a canonically encoded "
            "float") from None
    if not _finite(number):
        # The production rule for temperature is "must be positive" and for the
        # scale factor "must be positive". NaN and the infinities are not
        # positive real measurements: `NaN <= 0.0` is False, so a NaN would slip
        # through the production comparison itself. Requiring a finite value is
        # the faithful reading of that rule, not an additional one.
        raise BranchAMeasurementInvalid(
            f"{where}: embedded {key} is {number!r}, which is not a finite "
            "measured value")
    return number


def _persisted_float_list(evidence: Mapping[str, Any], key: str,
                          where: str) -> tuple[float, ...]:
    values = evidence.get(key)
    if not isinstance(values, list) or not values:
        raise BranchAMeasurementInvalid(
            f"{where}: embedded {key} is not a non-empty list")
    out = []
    for index, raw in enumerate(values):
        try:
            number = float.fromhex(raw)
        except (AttributeError, TypeError, ValueError):
            raise BranchAMeasurementInvalid(
                f"{where}: embedded {key}[{index}] {raw!r} is not a canonically "
                "encoded float") from None
        if not _finite(number):
            raise BranchAMeasurementInvalid(
                f"{where}: embedded {key}[{index}] is {number!r}, which is not a "
                "finite measured value")
        out.append(number)
    return tuple(out)


def reconstructed_branch_a_field(evidence: Mapping[str, Any],
                                 where: str) -> BranchAField:
    """Rebuild the PRODUCTION `BranchAField` from the persisted primitives.

    This is reuse, not reimplementation: constructing the real object re-applies
    every domain rule `BranchAField.__post_init__` enforces, and its `.H` and
    `.status` properties ARE the expected derived values.

    `viscosity` and `bead_radius` are not persisted -- they are the acknowledged
    OPEN field-construction inputs -- and they enter only `gamma`, which is never
    recomputed here. Neutral positive placeholders keep the constructor's own
    checks meaningful without inventing a drag coefficient; nothing derived from
    them is compared against anything.
    """
    k_modes = _persisted_float_list(evidence, "k_modes_measured", where)
    rot_deg = _persisted_float(evidence, "rot_deg_measured", where)
    temperature = _persisted_float(evidence, "T_measured", where)
    scale_factor = _persisted_float(evidence, "scale_factor", where)
    try:
        return BranchAField(
            field_id=str(evidence.get("field_id")),
            H_U=stiffness_matrix(k_modes, rot_deg),
            T=temperature,
            x_star=[0.0] * len(k_modes),
            k_modes=k_modes,
            rot_deg=rot_deg,
            viscosity=1.0,
            bead_radius=1.0,
            calibration_route=str(evidence.get("calibration_route")),
            scale_factor=scale_factor,
        )
    except (Refusal, ZeroDivisionError, OverflowError) as exc:
        raise BranchAMeasurementInvalid(
            f"{where}: the persisted primitives do not form a Branch-A "
            f"measurement the production constructor would create ({exc})"
        ) from exc


#: One step above the largest finite binary64 value, in EXACT arithmetic. The
#: format holds MAX = 2**1024 - 2**971 and the ulp of that binade is 2**971, so
#: the value the format would hold next, were its exponent range unbounded, is
#: exactly 2**1024. `math.nextafter` cannot return it -- it saturates to infinity,
#: and `Fraction(infinity)` raises OverflowError -- yet the rounding cell of MAX
#: is still an ordinary FINITE rational interval, and 2**1024 is its outer
#: endpoint. This is not a large-finite sentinel standing in for infinity: it is
#: the exact mathematical successor, so the interval stays exact and no tolerance
#: is introduced anywhere.
_VIRTUAL_BINADE = Fraction(2) ** 1024


def _neighbour(value: float, direction: float) -> Fraction:
    """The adjacent representable value, exactly, saturating to the virtual binade.

    Total over every finite `value`, which is what makes `_rounding_interval`
    total: only at +/- MAX is the outward neighbour unrepresentable, and there its
    exact value is +/- 2**1024.
    """
    step = math.nextafter(value, direction)
    if math.isinf(step):
        return _VIRTUAL_BINADE if step > 0.0 else -_VIRTUAL_BINADE
    return Fraction(step)


def _rounding_interval(value: float) -> tuple[Fraction, Fraction]:
    """The exact LOCATIONS of this float's two rounding-cell endpoints.

    Round-to-nearest maps the reals between the midpoints to `value`, so the
    endpoints sit at (prev+value)/2 and (value+next)/2. Computed in `Fraction`,
    so they are exact: no epsilon is chosen and no floating comparison is
    involved.

    LOCATIONS ONLY. Whether each endpoint BELONGS to this float's cell is decided
    by the ties-to-even rule and is returned by `_rounding_cell`. Treating both as
    included is wrong at an exact midpoint, which is where a tie is resolved
    against one of the two neighbours.

    TOTAL over every finite float, the largest and the most negative included.
    The zero and subnormal neighbourhoods need no special case: `nextafter` is
    exact there, and only the two outermost finite values reach the virtual
    binade at all.
    """
    exact = Fraction(value)
    return ((_neighbour(value, -math.inf) + exact) / 2,
            (exact + _neighbour(value, math.inf)) / 2)


def _significand_is_even(value: float) -> bool:
    """Is this float's significand even -- the tie-break winner at a midpoint?

    Read from the binary64 bit pattern, so it is exact by construction and needs
    no arithmetic at all.
    """
    return struct.unpack("<Q", struct.pack("<d", value))[0] & 1 == 0


def _rounding_cell(value: float) -> tuple[Fraction, Fraction, bool]:
    """This float's EXACT rounding cell: endpoint locations AND ownership.

    IEEE-754 binary64 division rounds to nearest with TIES TO EVEN, so a real
    landing exactly on a midpoint does not belong to both neighbours -- it belongs
    to whichever has the even significand. Adjacent floats always differ in that
    last bit (within a binade the significand increments by one; at a binade edge,
    at the subnormal/normal edge and at zero, the lower neighbour's significand is
    all ones and the upper one's is zero), so the tie is always resolved against
    exactly one of them and BOTH of this value's endpoints are owned together:

        significand even  ->  both midpoints round back here, cell CLOSED
        significand odd   ->  both go to the neighbours, cell OPEN

    Returned as one flag because both endpoints always share it. The distinction
    is not cosmetic: the smallest positive subnormal has an odd significand, so
    its cell is open at both ends, and treating it as closed admits drag values
    whose actual division lands on a neighbour instead.
    """
    lower, upper = _rounding_interval(value)
    return lower, upper, _significand_is_even(value)


#: The largest finite binary64, exactly. Written as a hex literal so the constant
#: is the bit pattern itself rather than a decimal that has to be re-rounded.
_MAX_FINITE = float.fromhex("0x1.fffffffffffffp+1023")
_MAX_FINITE_EXACT = Fraction(_MAX_FINITE)


def _smallest_binary64_at_least(bound: Fraction, *, strict: bool) -> float | None:
    """The smallest finite binary64 `x` with `x > bound`, or `x >= bound`.

    `None` when no finite binary64 satisfies the bound at all.

    `float(Fraction)` rounds to NEAREST-EVEN, so it does not by itself answer
    "the smallest float at or above this rational" -- it can land either side of
    the bound. The result is therefore corrected exactly: step outward until the
    bound is satisfied, then step back in while it still is. Each phase moves at
    most a couple of ulps, because the nearest-even result is already within one
    ulp of the bound, and every comparison is made in `Fraction`, never in
    floating point. No float space is enumerated and no tolerance is involved.
    """
    if bound > _MAX_FINITE_EXACT:
        return None                     # above every finite binary64
    if bound < -_MAX_FINITE_EXACT:
        return -_MAX_FINITE             # below every finite binary64
    candidate = float(bound)            # finite: |bound| <= MAX by the guards above

    def satisfies(value: float) -> bool:
        exact = Fraction(value)
        return exact > bound if strict else exact >= bound

    while not satisfies(candidate):
        step = math.nextafter(candidate, math.inf)
        if math.isinf(step):
            return None
        candidate = step
    while True:
        step = math.nextafter(candidate, -math.inf)
        if math.isinf(step) or not satisfies(step):
            return candidate
        candidate = step


def interval_contains_binary64(lower: Fraction, upper: Fraction, *,
                               lower_closed: bool = True,
                               upper_closed: bool = True) -> bool:
    """Does this exact rational interval contain a finite binary64 value?

    THE DISTINCTION THIS DRAWS
        A non-empty interval of REALS need not contain a representable one. Below
        the smallest positive subnormal there are infinitely many positive reals
        and no positive binary64 at all, so "some gamma exists" and "some gamma
        production could hold exists" are different statements. That gap is
        exactly what let a record through whose relaxation times no representable
        drag coefficient can produce.

    Decided in closed form: take the smallest binary64 satisfying the lower
    bound, then test it against the upper bound. If that one fails, no larger
    one can pass either. Endpoint strictness is carried through both bounds, so a
    float sitting exactly on an EXCLUDED endpoint is not counted as a witness.
    """
    return binary64_in_interval(lower, upper, lower_closed=lower_closed,
                                upper_closed=upper_closed) is not None


def binary64_in_interval(lower: Fraction, upper: Fraction, *,
                         lower_closed: bool = True,
                         upper_closed: bool = True) -> float | None:
    """One finite binary64 inside this exact rational interval, or `None`.

    Same decision as `interval_contains_binary64`, returning the value so the
    caller can REPLAY it through the real operation. The witness is
    verifier-local: it is never persisted, never compared against authority and
    never treated as a measurement.
    """
    witness = _smallest_binary64_at_least(lower, strict=not lower_closed)
    if witness is None:
        return None
    exact = Fraction(witness)
    if exact < upper or (upper_closed and exact == upper):
        return witness
    return None


def single_gamma_feasible(k_ascending: Sequence[float],
                          taus: Sequence[float]) -> bool:
    """Is there ONE REPRESENTABLE gamma with tau_r == fl(gamma / k_r) for every
    mode, where every mode's division is itself DEFINED in production?

    REPRESENTABLE is the operative word. Production does not divide by a real
    number: `BranchAField.gamma` is a rounded binary64 product chain, and the
    value that reaches the division is that single float. So the question is not
    "does some real gamma satisfy the rounding constraints" but "does some
    binary64 gamma". Those differ near the representational boundaries, and the
    difference is not academic: a record recording tau = 2**-1074 against
    k = 1e-4 has a non-empty real solution region lying entirely BELOW the
    smallest positive subnormal, so a real witness exists and no production value
    does.

    The domain clause is not decoration. Asking only "do the tau intervals
    intersect" admits k_r = 0, because the interval scaled by zero collapses to
    the single point 0 and gamma = 0 then looks like a witness -- while production
    cannot perform that division at all. A witness gamma is only a witness if
    production could have executed every division that produced the record.

    EXACT, and deliberately free of any tolerance. The production relation is one
    division per mode from ONE shared drag coefficient, so each recorded tau
    constrains gamma to an interval; the intersection of those intervals is the
    exact real solution region, and the record is realizable only if that region
    contains a finite binary64. IEEE division is correctly rounded, so
    `fl(g / k_r) == tau_r` exactly when the real quotient `g / k_r` lies in the
    rounding cell of `tau_r` -- which is what makes the interval intersection the
    faithful statement of the production map rather than an approximation of it.

    The intersection is taken FIRST and the witness sought once, in it. Asking
    each mode separately whether some representable gamma works would be a
    different and much weaker question: the modes share one drag coefficient.

    The absolute gamma is never chosen -- only its existence is tested, which is
    why the acknowledged-open drag coefficient stays open. The witness is a pure
    internal decision value; it is not persisted, compared against authority, or
    treated as a measurement.

    Comparing the products tau_r * k_r for exact equality would be WRONG: for
    unequal stiffnesses (theta2_ellipse) genuine production values differ in the
    last bits, and such a check rejects real measurements.
    """
    low = high = None
    low_closed = high_closed = True
    for stiffness, tau in zip(k_ascending, taus):
        if stiffness == 0.0:
            # PRODUCTION DOMAIN, not a numeric edge case. Production evaluates
            # `gamma / k_r`, and that raises ZeroDivisionError for EVERY gamma
            # when k_r is zero, so no witness exists and the pair is outside the
            # image of the constructor. Multiplying the tau interval by zero would
            # instead collapse it to the single point 0 and make gamma = 0 look
            # like a witness, which is exactly how an impossible record passed.
            # `== 0.0` is true for -0.0 as well: -0.0 divides just as badly.
            return False
        lo, hi, closed = _rounding_cell(tau)
        lower, upper = lo * Fraction(stiffness), hi * Fraction(stiffness)
        if lower > upper:                       # negative stiffness flips the order
            lower, upper = upper, lower
        # Scaling by an exact nonzero rational maps endpoints to endpoints and
        # cannot change whether one is included, so both carry this cell's own
        # ownership -- including through the reversal above, where the two swap
        # places but share the same flag.
        if low is None or lower > low:
            low, low_closed = lower, closed
        elif lower == low:
            low_closed = low_closed and closed
        if high is None or upper < high:
            high, high_closed = upper, closed
        elif upper == high:
            high_closed = high_closed and closed
    if low is None:
        return False
    # The real solution region is necessary but NOT sufficient. Production holds
    # gamma as a binary64, so the region has to contain one. A singleton
    # intersection survives only if EVERY contributing endpoint includes it --
    # which is exactly the auditor's case, where one mode excludes the point.
    witness = binary64_in_interval(low, high, lower_closed=low_closed,
                                   upper_closed=high_closed)
    if witness is None:
        return False
    # FINAL REPLAY. The interval arithmetic above is exact, so this should always
    # agree; it is kept as an independent confirmation through the real operation
    # rather than through a model of it. Deliberately NOT a search: if the witness
    # the exact machinery produced does not reproduce the record, that is a defect
    # in this verifier, and it fails closed rather than trying its neighbours.
    return all(witness / stiffness == tau
               for stiffness, tau in zip(k_ascending, taus))


def require_branch_a_measurement_invariants(evidence: Mapping[str, Any],
                                            where: str) -> None:
    """The JOINT constraints: derived fields and intra-record relations.

    Every check here is either a recomputation through production code or an
    exact consequence of the production relation. Nothing is compared against a
    nominal plan value, so the measurement stays free to vary.
    """
    field = reconstructed_branch_a_field(evidence, where)
    # --- H_A_FROM_PRIMITIVES: recomputed by production, compared exactly ------
    # Production evaluates H = H_U * scale / (K_B * T) and then serializes it, and
    # BOTH steps can fail on primitives that are individually finite and well
    # formed: K_B * T underflows to zero for a subnormal temperature, which makes
    # the division raise, and the product overflows to infinity for a large enough
    # stiffness or scale, which `canonical_float` refuses. In production either
    # failure happens BEFORE a record exists, so on read they are impossible-record
    # conditions and must carry the measurement code rather than escaping the read
    # verifier as a raw numeric exception.
    try:
        expected_h = [[canonical_float(v) for v in row] for row in field.H]
    except CodedRefusal:
        raise
    except (Refusal, ZeroDivisionError, OverflowError) as exc:
        raise BranchAMeasurementInvalid(
            f"{where}: the recorded stiffnesses, orientation, temperature and "
            f"scale do not yield a representable H_A ({exc}). Production computes "
            "H_U * scale / (K_B * T) and serializes it, so it could never have "
            "written this record.") from exc
    if evidence.get("H_A") != expected_h:
        raise BranchAMeasurementInvalid(
            f"{where}: the published H_A is not the matrix the recorded "
            "stiffnesses, orientation, temperature and scale produce. H_A is "
            "DERIVED -- H_U(k, psi) * scale / (k_B T) -- so it is not "
            "independently choosable, however consistently the digests are "
            "recomputed.")
    # --- STATUS_FROM_H_U ------------------------------------------------------
    if evidence.get("branch_a_status") != field.status:
        raise BranchAMeasurementInvalid(
            f"{where}: the published Branch-A status "
            f"{evidence.get('branch_a_status')!r} is not the status these "
            f"primitives yield ({field.status!r}); the status is derived from the "
            "eigenvalues of H_U, not declared")
    # --- TAU_SINGLE_GAMMA ----------------------------------------------------
    taus = _persisted_float_list(evidence, "tau_modes", where)
    k_modes = _persisted_float_list(evidence, "k_modes_measured", where)
    if len(taus) != len(k_modes):
        raise BranchAMeasurementInvalid(
            f"{where}: {len(taus)} relaxation time(s) for {len(k_modes)} "
            "stiffness(es); the frozen rule is one per mode")
    # RELAXATION_DOMAIN: the production division must be DEFINED for every mode.
    # A zero stiffness is not a badly measured stiffness. Production evaluates
    # tau_r = gamma / k_r, which raises ZeroDivisionError under EVERY drag
    # coefficient when k_r is zero, so no such record can ever be serialized. This
    # is precisely the line between "a measurement production CAN publish" and "a
    # record production CANNOT construct": a NEGATIVE stiffness stays publishable
    # -- it drives min eig(H_U) <= 0 and therefore status BRANCH_A_INVALID, a
    # legitimate recorded outcome -- while a zero stiffness has no publishable form
    # at all. Checked before the feasibility test because zero is a domain fact
    # about the operation, not a statement about which gamma might exist.
    for index, stiffness in enumerate(k_modes):
        if stiffness == 0.0:
            raise BranchAMeasurementInvalid(
                f"{where}: mode {index} records a measured stiffness of "
                f"{stiffness!r}. The frozen relaxation rule is tau_r = gamma / k_r "
                "and that division is undefined for a zero stiffness under every "
                "drag coefficient, so production raises before any such record "
                "exists. A negative stiffness is a different matter and remains "
                "publishable as BRANCH_A_INVALID.")
    if any(tau <= 0.0 for tau in taus):
        raise BranchAMeasurementInvalid(
            f"{where}: a recorded relaxation time is not positive")
    # The stored order is tau carried with ASCENDING stiffness, exactly as
    # `from_branch_a_field` pairs them. Sorting k the same way is what makes the
    # pairing check meaningful -- mode ordering has been a defect source before.
    ascending = sorted(k_modes)
    for index in range(1, len(ascending)):
        if ascending[index] == ascending[index - 1] and taus[index] != taus[index - 1]:
            raise BranchAMeasurementInvalid(
                f"{where}: modes {index - 1} and {index} record the SAME measured "
                f"stiffness and DIFFERENT relaxation times ({taus[index - 1]!r} "
                f"and {taus[index]!r}). One shared drag coefficient gives one "
                "relaxation time for one stiffness, exactly.")
    if not single_gamma_feasible(ascending, taus):
        raise BranchAMeasurementInvalid(
            f"{where}: no single drag coefficient yields the recorded relaxation "
            f"times for the recorded stiffnesses. tau_r = gamma / k_r with ONE "
            "gamma per measurement, so the recorded pairs are not a measurement; "
            "a mispaired or rescaled tau changes every phi and the whole Block-1 "
            "null law.")


# ---- THE ONE CANONICAL VERIFIED-PUBLICATION LOADER --------------------------
def verified_publication(output_dir: str, job: CampaignJob,
                         binding: ExecutionBinding) -> dict[str, Any] | None:
    """Resolve, load and COMPLETELY verify this job's Branch-A publication.

    COMMIT VERIFICATION IS NOT PUBLICATION VALIDATION. They answer different
    questions, and the official path needs both:

        commit verification        "were these exact bytes durably committed?"
        publication verification   "is this committed record a VALID Branch-A
                                    publication, for this exact planned job, under
                                    the current execution package?"

    THE DEFECT THIS CLOSES
        Terminal validation resolved the publication from the store -- which
        closed the caller-trust hole -- and then trusted it on the strength of its
        commit transaction alone. An audit committed publications carrying an
        invalid schema, a state other than BRANCH_A_PUBLISHED, an extra
        unauthenticated field, a false execution identity and a false analysis
        procedure identity, re-digested the lock and the terminal record so the
        whole downstream chain agreed with the forgery, and terminal validation
        accepted every one of them. Atomic commitment makes bytes durable; it
        says nothing about whether those bytes are a valid publication.

        Internal consistency downstream cannot legalise invalid upstream
        provenance. The hierarchy is frozen planned job and current package, then
        the verified publication, then the verified lock, then the terminal
        record -- each one authoritative over the next, never the reverse.

    The heavy lifting is delegated to the EXISTING `verify_publication`, which is
    the same routine the unblind path and restart already use. Nothing about
    publication validity is reimplemented here.
    """
    directory = publication_directory(output_dir)
    basename = publication_basename(job.coordinates)
    path = os.path.join(directory, basename)
    if not os.path.lexists(path):
        return None
    record, _marker = read_committed(directory, basename,
                                     "the Branch-A publication record")
    # STRICT PARSE FIRST. Every check below reads fields of this record, so its
    # shape is established before any of them believes one.
    require_publication_schema(record, path)
    # THE PLANNED JOB'S coordinates, checked against the record independently.
    # This cannot be delegated: the realisation rebuilt below comes FROM the
    # record, so `verify_publication`'s own coordinate check would compare the
    # record with itself. The frozen planner is the authority here, not the file.
    if record["coordinates"] != job.coordinates.as_dict():
        raise BranchAProvenanceMismatch(
            f"{path}: the committed publication addresses "
            f"{record['coordinates']!r}, but this is the canonical location of "
            f"{job.coordinates.as_dict()!r}. A publication filed under another "
            "job's coordinates is not this job's evidence.")
    # EVERY EMBEDDED FIELD AGAINST ITS DECLARED AUTHORITY, before the evidence
    # is rebuilt from it: a missing, malformed or unauthorised embedded value must
    # refuse with a coded provenance failure rather than crash inside the
    # reconstruction, and the seed, plan, contract and derived rules must hold on
    # the READ path exactly as they did when the evidence was created.
    require_embedded_field_authority(record, job, binding, path)
    # THE COMPLETE EXISTING VERIFIER: envelope digest recomputed, marker digest
    # compared, basename re-derived, evidence digest recomputed, outer package and
    # execution identities compared with the current binding.
    verified = verify_publication(output_dir, realisation_from_record(record),
                                  binding)
    return verified


# ---- THE CANONICAL PLAN IS THE AUTHORITY, NOT THE CALLER'S LIST -------------
_CANONICAL_PLAN_CACHE: dict[str, tuple[CampaignJob, ...]] = {}


def canonical_plan(binding: ExecutionBinding) -> tuple[CampaignJob, ...]:
    """The frozen deterministic job plan, memoised on the plan's own identity.

    `plan_campaign` remains the ONE planner; this only avoids re-enumerating
    53,200 descriptors on every reconciliation. The cache key is the plan digest,
    so a different plan can never return another plan's jobs.
    """
    cached = _CANONICAL_PLAN_CACHE.get(binding.plan_sha256)
    if cached is None:
        cached = plan_campaign(binding.plan)
        _CANONICAL_PLAN_CACHE[binding.plan_sha256] = cached
    return cached


def require_authentic_plan(binding: ExecutionBinding,
                           planned: Sequence[CampaignJob] | None,
                           what: str) -> tuple[CampaignJob, ...]:
    """The planned jobs a reconciliation runs against must BE the frozen plan's.

    THE DEFECT THIS CLOSES
        `planned` was optional, and omitting it silently downgraded restart from
        semantic reconciliation to a structural inventory. An audit placed a
        canonically committed lock naming job B in job A's slot and showed that
        `verify_restart(planned=None)` accepted it while
        `verify_restart(planned=<plan>)` refused. A provenance API must not offer
        a mode that stops checking identity.

    A SUBSET IS STILL ALLOWED, deliberately: the campaign supports running part
    of the plan, and omitting a job makes reconciliation STRICTER rather than
    weaker -- a persisted object whose job is not listed refuses as unplanned, so
    nothing can be hidden by leaving it out. What is refused is a job descriptor
    that is not the frozen planner's: an unknown identity, or a known identity
    whose coordinates, role, calibration requirement, seed families or result kind
    have been edited. Those could legalise a bad object, so they fail closed.
    """
    if planned is None:
        raise CampaignPlanMismatch(
            f"{what} requires the canonical planned jobs. Passing none used to "
            "mean 'skip semantic reconciliation', which is not a mode a "
            "provenance verifier may offer: persisted evidence is checked "
            "against the frozen plan or it is not checked.")
    supplied = tuple(planned)
    authentic = {job.job_id: job for job in canonical_plan(binding)}
    seen: set[str] = set()
    for job in supplied:
        expected = authentic.get(job.job_id)
        if expected is None:
            raise CampaignPlanMismatch(
                f"{what}: {job.job_id!r} is not a job the frozen plan declares; a "
                "caller may not introduce jobs the deterministic planner never "
                "produced")
        if job.as_dict() != expected.as_dict():
            raise CampaignPlanMismatch(
                f"{what}: the supplied descriptor for {job.job_id!r} is not the "
                "frozen planner's. Restart truth is defined by frozen authority, "
                "not by the descriptor a caller hands in.")
        if job.job_id in seen:
            raise CampaignPlanMismatch(
                f"{what}: {job.job_id!r} is listed twice")
        seen.add(job.job_id)
    return supplied


# ---- THE ONE CANONICAL DURABLE-LOCK VERIFIER -------------------------------
def verified_calibration_lock(output_dir: str, job: CampaignJob,
                              binding: ExecutionBinding) -> dict[str, Any] | None:
    """Resolve, load and COMPLETELY verify this job's durable calibration lock.

    THE ONE ROUTINE. Terminal validation and restart reconciliation both call it,
    so there is no `terminal_lock_verifier` and no separate `restart_lock_
    verifier` that could drift apart. Everything it needs it derives:

        planned job coordinates
              -> the canonical lock path in the campaign's own store
              -> the committed lock record
              -> the committed Branch-A publication for the SAME coordinates
              -> every cross-check, then the verified record

    THE DEFECTS THIS CLOSES
        An audit found two, and both were trust-boundary defects rather than
        comparison defects.

        FINDING A. The official terminal validator accepted the calibration lock
        as an ARGUMENT. A caller could therefore hand it a fabricated lock mapping
        that had never been persisted, matching a fabricated artifact digest in
        the terminal record, and validation accepted the pair -- while the same
        terminal record checked against the actual committed lock refused. The
        object that is supposed to PROVE a record's provenance may not be supplied
        by whoever wants the record believed.

        FINDING B. The semantic checks -- does this lock name THIS job, and THIS
        job's field -- lived only in terminal validation. A canonically committed
        lock that named another planned job, or another field, was therefore
        accepted by restart reconciliation whenever no terminal record existed
        yet. Whether an intermediate provenance object is valid cannot depend on
        whether a downstream record happens to have been written.

    Returns the verified record, or None for a job the frozen plan gives no
    calibration -- for which the presence of a lock is itself a refusal.
    """
    lock = committed_calibration_lock(output_dir, job.coordinates)
    if not job.requires_calibration:
        # No calibration requirement is invented for a case that evaluates no
        # P1 / Block-1 quantity -- and none is smuggled in by a stray lock.
        if lock is not None:
            raise CalibrationLockUnplanned(
                f"{job.job_id}: {job.coordinates.case_id} evaluates no P1 / "
                "Block-1 quantity, yet a committed calibration lock exists for "
                "these coordinates")
        return None
    if lock is None:
        raise CalibrationLockMissing(
            f"{job.job_id}: no committed calibration lock exists at "
            f"{calibration_lock_basename(job.coordinates)!r} in the campaign's "
            "calibration-lock store, so no artifact was ever locked for this job")
    where = os.path.join(calibration_lock_directory(output_dir),
                         calibration_lock_basename(job.coordinates))
    # --- identity: the slot, the record and the planned job must all agree ---
    if lock.get("job_id") != job.job_id:
        raise CalibrationLockJobMismatch(
            f"{job.job_id}: the lock in this job's canonical slot names "
            f"{lock.get('job_id')!r}. A lock is not valid because it names SOME "
            "valid planned job; the store location, the record's own identity and "
            "the planned job are one identity or the provenance is wrong.")
    if lock.get("artifact_field_id") != job.coordinates.scope:
        raise CalibrationLockFieldMismatch(
            f"{job.job_id}: the locked artifact is calibrated for field "
            f"{lock.get('artifact_field_id')!r}; this job is "
            f"{job.coordinates.scope!r}. Under REPLICATE_CONDITIONAL calibration "
            "the null law moves with H_A, so another field's artifact is another "
            "field's threshold.")
    if lock.get("publication_basename") != publication_basename(job.coordinates):
        raise CalibrationLockProvenanceMismatch(
            f"{job.job_id}: the lock cites publication "
            f"{lock.get('publication_basename')!r}, not this job's "
            f"{publication_basename(job.coordinates)!r}")
    # --- the upstream Branch-A publication, resolved AND VERIFIED HERE -------
    # Not `committed_publication`: a durable commit proves the bytes, not that
    # they are a valid publication for this job under the current package.
    publication = verified_publication(output_dir, job, binding)
    if publication is None:
        raise CalibrationLockWithoutPublication(
            f"{job.job_id}: a committed calibration lock exists with no committed "
            "Branch-A publication. A threshold conditional on evidence that is "
            "not there is not a conditional threshold.")
    for key, category in (("branch_a_evidence_sha256",
                           "Branch-A evidence hash"),
                          ("publication_digest", "publication digest"),
                          ("calibration_condition_sha256",
                           "calibration-condition identity")):
        if lock.get(key) != publication.get(key):
            raise CalibrationLockProvenanceMismatch(
                f"{job.job_id}: the lock's {category} {lock.get(key)!r} is not the "
                f"committed Branch-A publication's {publication.get(key)!r}")
    # --- the package the threshold was locked under -------------------------
    identities = lock.get("package_identities") or {}
    for key, current in (("contract_sha256", binding.binding.sha256),
                         ("plan_sha256", binding.plan_sha256),
                         ("seed_map_sha256", binding.seed_map_sha256),
                         ("analysis_procedure_identity", binding.analysis_identity),
                         ("execution_identity", binding.execution_identity)):
        if identities.get(key) != current:
            raise CalibrationLockProvenanceMismatch(
                f"{where}: the lock's {key} {identities.get(key)!r} is not the "
                f"current {current!r}; the threshold was locked under a different "
                "package")
    if lock.get("analysis_procedure_identity") != binding.analysis_identity:
        raise CalibrationLockProvenanceMismatch(
            f"{where}: the locked artifact declares analysis procedure "
            f"{lock.get('analysis_procedure_identity')!r}, not the current "
            f"{binding.analysis_identity!r}")
    return lock


def reconcile_calibration_locks(output_dir: str, binding: ExecutionBinding,
                                planned: Sequence[CampaignJob]
                                ) -> dict[str, dict[str, Any]]:
    """Validate EVERY persisted calibration lock as a complete provenance object.

    The authoritative universe is the campaign's own store, never a mapping a
    caller passes in: `inventory_calibration_locks` enumerates it, and every
    entry it finds must then survive the one canonical verifier above.

    THE DEFECT THIS CLOSES
        Restart reconciliation used to check a lock's planned membership, its
        calibration requirement and the existence of its publication, and left
        the lock's own semantic identity -- which job, which field -- to terminal
        validation. An audit demonstrated the consequence: with no terminal record
        written yet, a canonically committed lock naming another planned job, or
        another field, was accepted. A legitimate resumable state is exactly the
        state in which a terminal record does NOT exist yet, so that was the case
        that mattered most.
    """
    declared = {job.job_id: job for job in planned}
    verified: dict[str, dict[str, Any]] = {}
    for job_id in sorted(inventory_calibration_locks(output_dir)):
        job = declared.get(job_id)
        if job is None:
            raise CalibrationLockUnplanned(
                f"the calibration lock for {job_id!r} belongs to no planned job; "
                "the store holds a threshold this campaign never declared")
        if not job.requires_calibration:
            raise CalibrationLockUnplanned(
                f"{job_id}: a calibration lock exists for a case that evaluates "
                "no P1 / Block-1 quantity")
        # THE SAME ROUTINE TERMINAL VALIDATION USES, and it runs here whether or
        # not a terminal record for this job exists.
        verified[job_id] = verified_calibration_lock(output_dir, job, binding)
    return verified


def _compare_terminal_to_verified_lock(record: Mapping[str, Any],
                                       job: CampaignJob,
                                       lock: Mapping[str, Any] | None,
                                       publication: Mapping[str, Any],
                                       binding: ExecutionBinding) -> None:
    """Compare a terminal record against an ALREADY-VERIFIED calibration lock.

    PRIVATE, AND DELIBERATELY SO. `lock` here means a record that has already
    passed `verified_calibration_lock` -- the canonical durable-store verifier --
    and nothing else. This helper is pure, which makes it convenient to unit
    test, and that convenience is exactly why it must not be the production
    trust boundary: an audit showed that when the official validator accepted the
    lock as an argument, a caller could fabricate one that was never persisted
    and have a forged terminal record believed. The official entry point is
    `validate_job_record`, which resolves the lock itself.

    Bind a terminal record to the ACTUAL locked calibration artifact.

    THE DEFECT THIS CLOSES
        A terminal record for a calibration-requiring job could carry
        `calibration_artifact_sha256 = null`, or a fabricated valid-looking
        digest, or another job's digest, then recompute its own terminal digest --
        and validation accepted it, on the write path and on restart alike.
        Necessarily so: the adopted STREAMING_PER_REPLICATE implementation
        finalises, locks and SPENDS each artifact, so nothing on disk recorded the
        lock and the record was the only witness to its own calibration.

        Self-consistency proves that a record's bytes were not edited after it was
        written. It says nothing about which threshold the job's P1 decision was
        actually taken against -- and for a Block-1 case, the calibration artifact
        IS that threshold.

    WHAT IS AUTHORITATIVE HERE
        Not the terminal record, which is the object under test, and not a
        caller-supplied expected digest, which would only move the question one
        step. The authority is the COMMITTED calibration-lock record published for
        these exact coordinates at the moment of the lock, before Branch B was
        unblinded. Its basename is a pure function of the coordinates, so a lock
        belonging to another case, subcondition, replicate or field cannot be read
        in this one's place; and its contents are cross-checked against the
        committed Branch-A publication, so the complete chain

            publication -> condition -> locked artifact -> terminal record

        is verified together rather than as four unrelated fields.
    """
    stored = record.get("calibration_artifact_sha256")
    if not job.requires_calibration:
        # UNCHANGED FROZEN SEMANTICS. A case that evaluates no P1 / Block-1
        # quantity has no calibration, and a calibration requirement may not be
        # invented for it in EITHER direction: not by a digest in the record --
        # which `validate_job_record` already refuses -- and not by a lock record
        # on disk, which would be an artifact this case never needed.
        if lock is not None:
            raise CalibrationLockUnplanned(
                f"{job.job_id}: {job.coordinates.case_id} evaluates no P1 / "
                "Block-1 quantity, yet a committed calibration lock exists for "
                "these coordinates")
        return
    if lock is None:
        raise CalibrationLockMissing(
            f"{job.job_id}: no committed calibration lock exists for these "
            "coordinates, so no artifact was ever locked for this job. A record "
            f"naming {stored!r} cites a lock that left no evidence, and "
            "re-digesting the record does not lock an artifact.")
    if "calibration_artifact_sha256" not in record or stored is None:
        raise CalibrationArtifactBindingInvalid(
            f"{job.job_id}: the terminal record carries no locked calibration "
            "artifact identity, but this job's Block-1 threshold came from one. A "
            "missing link is not a passed check.")
    if not is_sha256(stored):
        raise CalibrationArtifactBindingInvalid(
            f"{job.job_id}: the stored calibration artifact identity {stored!r} "
            "is not a SHA-256 identity")
    if stored != lock["calibration_artifact_sha256"]:
        raise CalibrationArtifactBindingInvalid(
            f"{job.job_id}: the terminal record names calibration artifact "
            f"{stored!r}; the artifact actually locked for these coordinates is "
            f"{lock['calibration_artifact_sha256']!r}. The threshold a result was "
            "judged against is not a property the result may declare about "
            "itself.")
    # --- the complete chain, verified together, never as isolated fields -----
    if record.get("calibration_condition_sha256") != lock[
            "calibration_condition_sha256"]:
        raise CalibrationArtifactBindingInvalid(
            f"{job.job_id}: the record's calibration condition is not the one the "
            "locked artifact was calibrated at")
    if lock["calibration_condition_sha256"] != publication.get(
            "calibration_condition_sha256"):
        raise CalibrationLockProvenanceMismatch(
            f"{job.job_id}: the locked artifact's condition is not the one the "
            "committed Branch-A publication was bound to. An artifact calibrated "
            "at another realised Branch-A condition is not this replicate's: "
            "under REPLICATE_CONDITIONAL calibration the null law moves with H_A.")
    if lock["branch_a_evidence_sha256"] != publication.get(
            "branch_a_evidence_sha256"):
        raise CalibrationLockProvenanceMismatch(
            f"{job.job_id}: the calibration lock cites Branch-A evidence that is "
            "not the committed publication's")
    if lock["publication_digest"] != publication.get("publication_digest"):
        raise CalibrationLockProvenanceMismatch(
            f"{job.job_id}: the calibration lock cites a publication digest that "
            "is not the committed publication's own")
    # The lock's OWN identity, field and package are `verified_calibration_lock`'s
    # responsibility and are re-asserted here only as a cheap contract check, so
    # a future caller that reaches this helper with an unverified mapping fails
    # loudly instead of silently comparing against it.
    if lock.get("job_id") != job.job_id:
        raise CalibrationLockJobMismatch(
            f"{job.job_id}: the calibration lock belongs to {lock.get('job_id')!r}")
    if lock.get("artifact_field_id") != job.coordinates.scope:
        raise CalibrationLockFieldMismatch(
            f"{job.job_id}: the locked artifact is calibrated for field "
            f"{lock.get('artifact_field_id')!r}; this job is "
            f"{job.coordinates.scope!r}")


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
    publication_digest: str
    calibration_condition_sha256: str | None
    calibration_artifact_sha256: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            **self.coordinates.as_dict(),
            "branch_a_evidence_sha256": self.branch_a_evidence_sha256,
            "publication_path": os.path.basename(self.publication_path),
            "publication_digest": self.publication_digest,
            "calibration_condition_sha256": self.calibration_condition_sha256,
            "calibration_artifact_sha256": self.calibration_artifact_sha256,
        }


class JobExecution:
    """The state machine for ONE scientific job. The only route to Branch B.

    Ordering is enforced by state, not by call convention: every method that
    advances the chain checks the frozen transition table first, performs the
    work, verifies the work, and only then enters the new state. A step that
    fails anywhere leaves the job exactly where it was.
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
        self._publication: PublicationReceipt | None = None
        self._condition: CalibrationCondition | None = None
        self._artifact_digest: str | None = None
        self._token: BranchBUnblindToken | None = None
        self._outcome: dict[str, Any] | None = None
        self._record: dict[str, Any] | None = None

    # ----------------------------------------------------------------- state
    @property
    def state(self) -> str:
        return self._state

    @property
    def coordinates(self) -> JobCoordinates:
        return self.job.coordinates

    @property
    def publication_path(self) -> str | None:
        return self._publication.path if self._publication else None

    @property
    def terminal_record(self) -> dict[str, Any] | None:
        return dict(self._record) if self._record is not None else None

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
        """Enter the state only AFTER the work succeeded AND was verified.

        Checking and entering are separate on purpose, and entering is always the
        LAST statement of a step: an audit found that `analyse` advanced before
        copying its outcome, so a failing analysis left a job reporting ANALYSED.
        VALIDATE, PERFORM, VERIFY, THEN COMMIT THE TRANSITION -- never the reverse.
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
        boundary = self._require_calibration_boundary()
        expected_seed = boundary.branch_a_seed(self.coordinates.scope)
        if branch_a_seed != expected_seed:
            raise BranchAProvenanceMismatch(
                f"{self.job.job_id}: Branch-A evidence carries seed identity "
                f"{branch_a_seed}, but this job's declared Branch-A stream is "
                f"{expected_seed}. Evidence from another stream is not this "
                "replicate's Branch-A measurement.")
        if common_mode_seed != boundary.common_mode_seed():
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
        """Hash, publish, COMMIT and re-verify. Branch B stays unreachable until
        every one of those succeeds."""
        if self._realisation is None:
            raise BranchANotPublished(
                f"{self.job.job_id}: no Branch-A evidence has been realised")
        self._require_transition(BRANCH_A_PUBLISHED)
        condition = (self._realisation.calibration_condition(self.binding)
                     if self.job.requires_calibration else None)
        receipt = publish_branch_a(self.output_dir, self._realisation, condition,
                                   self.binding)
        # VERIFY THE OUTPUT BEFORE COMMITTING THE TRANSITION. Re-reading from disk
        # is what distinguishes "the write returned" from "a reader can now obtain
        # exactly this evidence", and only the second is publication.
        verify_publication(self.output_dir, self._realisation, self.binding,
                           condition.sha256 if condition else None)
        self._enter(BRANCH_A_PUBLISHED)
        self._publication = receipt
        return receipt.path

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
        condition = self._realisation.calibration_condition(self.binding)
        verify_publication(self.output_dir, self._realisation, self.binding,
                           condition.sha256)
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
        return self._require_calibration_boundary().calibration_seed(
            self.coordinates.scope)

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
        digest = self._require_calibration_boundary().lock(
            self.coordinates.scope, artifact, self._condition)
        # DURABLY COMMIT THE LOCK, then re-read it, BEFORE entering the state and
        # therefore before Branch B can be unblinded. The artifact itself is
        # spent under STREAMING_PER_REPLICATE, so this record is the only
        # external evidence of which threshold this job's P1 decision was taken
        # against; without it the terminal record is its own sole witness, which
        # an audit showed is no witness at all.
        publish_calibration_lock(self.output_dir, self.job, artifact,
                                 self._condition, digest, self.binding)
        # RE-READ THROUGH THE CANONICAL VERIFIER, not the raw loader: what must
        # hold is that the lock this job will later be judged against verifies
        # completely NOW, while the failure is still recoverable by refusing.
        written = verified_calibration_lock(self.output_dir, self.job, self.binding)
        if written is None or written["calibration_artifact_sha256"] != digest:
            raise CalibrationLockProvenanceMismatch(
                f"{self.job.job_id}: the calibration lock was written but does "
                "not verify as this job's own lock")
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
        if self._publication is None:
            raise BranchANotPublished(
                f"{self.job.job_id}: Branch-A evidence has not been published. The "
                "frozen rule is that Branch-A output is hashed and PUBLISHED before "
                "Branch B is unblinded.")
        self._require_transition(BRANCH_B_UNBLINDED)
        record = verify_publication(
            self.output_dir, self._realisation, self.binding,
            self._condition.sha256 if self._condition else None)
        if self.job.requires_calibration:
            if self._condition is None or self._artifact_digest is None:
                raise BranchBPremature(
                    f"{self.job.job_id}: the calibration artifact is not locked")
            locked = self._require_calibration_boundary().artifact(
                self.coordinates.scope)
            if locked.condition.sha256 != self._condition.sha256:
                raise BranchBPremature(
                    f"{self.job.job_id}: the locked artifact's condition is not the "
                    "one derived from this job's published Branch-A evidence")
            # The EXTERNAL record of the lock, re-read from disk through the ONE
            # canonical verifier. Branch B stays blind until the threshold it will
            # be judged against is not merely held in memory but durably committed,
            # completely verified, and still saying what it said.
            lock = verified_calibration_lock(self.output_dir, self.job,
                                             self.binding)
            if lock is None:
                raise BranchBPremature(
                    f"{self.job.job_id}: no committed calibration lock exists for "
                    "these coordinates")
            if lock["calibration_artifact_sha256"] != self._artifact_digest:
                raise BranchBPremature(
                    f"{self.job.job_id}: the committed calibration lock names a "
                    "different artifact than the one locked here")
        token = BranchBUnblindToken(
            coordinates=self.coordinates,
            branch_a_evidence_sha256=self._realisation.evidence_sha256,
            publication_path=self._publication.path,
            publication_digest=record["publication_digest"],
            calibration_condition_sha256=(self._condition.sha256
                                          if self._condition else None),
            calibration_artifact_sha256=self._artifact_digest,
        )
        self._enter(BRANCH_B_UNBLINDED)
        self._token = token
        return token

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
        return self._require_calibration_boundary().validation_seed(
            self.coordinates.scope, requested)

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

    def _require_calibration_boundary(self) -> ReplicateCalibration:
        if self.calibration is None:
            raise JobStateInvalid(
                f"{self.job.job_id}: this job's calibration boundary has been "
                "released. Seeds, calibration and Branch-B access are reachable only "
                "while the boundary that orders them is held; they are never "
                "re-derived afterwards.")
        return self.calibration

    def release_calibration(self) -> None:
        """Drop this job's reference to its replicate calibration boundary.

        The adopted campaign-level implementation is STREAMING_PER_REPLICATE, for
        a stated reason: one artifact carries four gates x R_cal null draws, and
        materialising a whole case's artifacts at once would be tens of gigabytes.
        Permitted only once the job is ANALYSED -- by then every ordering
        guarantee the boundary exists to enforce has already been enforced -- and
        any later seed or calibration request refuses rather than silently
        re-deriving one.
        """
        if self._state not in (ANALYSED, RECORDED):
            raise JobStateInvalid(
                f"{self.job.job_id}: the calibration boundary may not be released in "
                f"state {self._state}; it orders Branch A, the lock and Branch B, and "
                "releasing it earlier would remove the ordering it exists to enforce.")
        self.calibration = None

    # ---------------------------------------------------------------- step 8-9
    def analyse(self, outcome: Mapping[str, Any]) -> dict[str, Any]:
        """Record the analysis outcome. Refusals stay refusals.

        THE DEFECT THIS CLOSES
            The previous implementation entered ANALYSED and only then copied the
            outcome. An audit demonstrated that a failing copy therefore left the
            job reporting ANALYSED with no analysis, and the next step's
            precondition was satisfied by a step that had failed. The outcome is
            now copied, canonicalised and validated FIRST.
        """
        if self._token is None:
            raise BranchBPremature(
                f"{self.job.job_id}: nothing may be analysed before Branch B is "
                "unblinded")
        self._require_transition(ANALYSED)
        canonical = self._canonical_outcome(outcome)
        self._enter(ANALYSED)
        self._outcome = canonical
        return dict(canonical)

    def _canonical_outcome(self, outcome: Mapping[str, Any]) -> dict[str, Any]:
        """Copy, canonicalise and validate an analysis outcome. May fail; must.

        A structured scientific refusal is a RESULT and is accepted here. What is
        refused is an outcome that cannot be written down: a non-mapping, an empty
        one, non-string keys, or a value canonical JSON cannot represent -- NaN
        and infinity included, because `allow_nan=False` would otherwise fail at
        write time, long after the job had been marked analysed.
        """
        try:
            copied = dict(outcome)
        except Exception as exc:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: the analysis outcome could not be copied "
                f"({type(exc).__name__}: {exc}); nothing has been analysed"
            ) from exc
        if not copied:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: an empty analysis outcome is not a result. A "
                "structured scientific refusal is a result and must say so; silence "
                "is not.")
        bad = sorted(k for k in copied if not isinstance(k, str))
        if bad:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: analysis outcome keys must be strings, found "
                f"{bad}")
        try:
            canonical_json(copied)
        except (TypeError, ValueError) as exc:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: the analysis outcome is not canonically "
                f"serialisable ({exc}). A result that cannot be written down "
                "cannot be evidence."
            ) from exc
        return copied

    def record(self, aggregate: Mapping[str, Any],
               fields: Sequence[str] | None = None) -> dict[str, Any]:
        """Finalise this job, deriving its structure from the FROZEN job.

        THE DEFECTS THIS CLOSES
            An audit demonstrated three. The recorder accepted a C7 aggregate for
            a C2 job; it accepted an EMPTY field list, so C2's mandatory per-field
            diagnostic was satisfied by having no rows to check; and having
            checked the mandatory diagnostic it then discarded it, so the stored
            record could not demonstrate the requirement it had passed.

            Case identity, the expected field set and the mandatory diagnostic set
            are now all DERIVED from the immutable planned job and the frozen
            plan. The caller may restate them and is refused if it restates them
            wrongly; it cannot supply them.
        """
        if self._outcome is None:
            raise JobStateInvalid(f"{self.job.job_id}: nothing has been analysed")
        self._require_transition(RECORDED)
        record = self._terminal_record(aggregate, fields)
        self._enter(RECORDED)
        self._record = record
        return dict(record)

    def _terminal_record(self, aggregate: Mapping[str, Any],
                         fields: Sequence[str] | None) -> dict[str, Any]:
        plan = self.binding.plan
        case_id = self.coordinates.case_id               # FROZEN, not supplied
        try:
            supplied = dict(aggregate)
        except Exception as exc:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: the aggregate could not be read ({exc})") from exc
        if supplied.get("schema") != MANIFEST_SCHEMA:
            raise ResultSchemaInvalid(
                f"{self.job.job_id}: aggregate schema {supplied.get('schema')!r} is "
                f"not {MANIFEST_SCHEMA!r}")
        if supplied.get("case_id") != case_id:
            raise ResultCaseMismatch(
                f"{self.job.job_id}: this job belongs to case {case_id!r}; the "
                f"aggregate presented declares {supplied.get('case_id')!r}. A result "
                "is authorised for the case its frozen job identity names, and for "
                "no other -- a Python shape that happens to be accepted is not "
                "case compatibility.")
        declared_sub = supplied.get("subcondition_id")
        if declared_sub is not None and declared_sub != self.coordinates.subcondition_id:
            raise ResultCaseMismatch(
                f"{self.job.job_id}: the aggregate is for subcondition "
                f"{declared_sub!r}, this job is {self.coordinates.subcondition_id!r}")
        required = required_result_fields(plan, case_id)
        resolved = canonical_result_fields(self.job.job_id, required, fields)
        require_mandatory_diagnostics(supplied, plan, resolved)
        stored = stored_mandatory_diagnostics(plan, case_id, supplied)
        record: dict[str, Any] = {
            "schema": JOB_RECORD_SCHEMA,
            "job_id": self.job.job_id,
            "coordinates": self.coordinates.as_dict(),
            # DERIVED from the frozen job. The caller never supplies these.
            "result_kind": self.job.result_kind,
            "role": self.job.role,
            "requires_calibration": self.job.requires_calibration,
            "fields": list(resolved),
            "branch_a_evidence_sha256": self._realisation.evidence_sha256,
            "publication_basename": os.path.basename(self._publication.path),
            "publication_digest": self._publication.commit_record["publication_digest"],
            "calibration_condition_sha256": (self._condition.sha256
                                             if self._condition else None),
            "calibration_artifact_sha256": self._artifact_digest,
            "package_identities": {
                "contract_sha256": self.binding.binding.sha256,
                "plan_sha256": self.binding.plan_sha256,
                "seed_map_sha256": self.binding.seed_map_sha256,
                "analysis_procedure_identity": self.binding.analysis_identity,
                "execution_identity": self.binding.execution_identity,
            },
            "result": dict(self._outcome),
            # The EVIDENCE for every mandatory diagnostic that was checked, kept
            # so the stored record can demonstrate the requirement it passed.
            "mandatory_diagnostics": stored,
            "terminal_state": RECORDED,
        }
        record["result_digest"] = sealed_digest(record, "result_digest")
        return record

    # ------------------------------------------------------------- immutability
    def republish_branch_a(self, realisation: BranchARealisation) -> str:
        """Always refuses. Published Branch-A evidence is immutable."""
        raise BranchAPublicationImmutable(
            f"{self.job.job_id}: Branch-A evidence for these coordinates is already "
            "published. It may not be replaced, edited, republished with a different "
            "hash, or rebound to other coordinates -- least of all once Branch B has "
            "been unblinded against it.")


# --------------------------------------------------- result structure, derived
def case_entry(plan: Mapping[str, Any], case_id: str) -> Mapping[str, Any]:
    for case in plan["cases"]:
        if case["case_id"] == case_id:
            return case
    raise ResultCaseMismatch(
        f"the frozen plan declares no case {case_id!r}; it declares "
        f"{[c['case_id'] for c in plan['cases']]}")


def required_result_fields(plan: Mapping[str, Any], case_id: str) -> tuple[str, ...]:
    """The exact per-field rows a case's result must carry, in FROZEN plan order."""
    return tuple(case_entry(plan, case_id)["fields_affected"])


def canonical_result_fields(job_id: str, required: tuple[str, ...],
                            supplied: Sequence[str] | None) -> tuple[str, ...]:
    """Validate a caller's field list against the frozen one, and canonicalise it.

    Ordering carries no meaning here -- the plan's order is the canonical one, so
    a correct set in another order is accepted and re-ordered rather than refused
    for a difference that is not scientific. Everything else refuses: an empty
    list, a missing field, an extra field, a duplicate, a wrong name.
    """
    if supplied is None:
        return required
    listed = list(supplied)
    duplicates = sorted({f for f in listed if listed.count(f) > 1})
    if duplicates:
        raise ResultFieldSetMismatch(
            f"{job_id}: duplicated per-field rows {duplicates}; one row per declared "
            "field, and a repeated row is an ambiguous denominator")
    if set(listed) != set(required):
        missing = sorted(set(required) - set(listed))
        extra = sorted(set(listed) - set(required))
        raise ResultFieldSetMismatch(
            f"{job_id}: per-field rows are not the frozen field set (missing "
            f"{missing}, unexpected {extra}). A missing row is not a successful "
            "zero-rejection row, and the recorder derives the required set from "
            "the frozen plan rather than accepting the caller's list.")
    return required


def stored_mandatory_diagnostics(plan: Mapping[str, Any], case_id: str,
                                 aggregate: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Capture the EVIDENCE for every mandatory diagnostic that was validated.

    Frozen authority requires these to be REPORTED. A result that passes
    validation and then discards what it was validated against cannot demonstrate
    the requirement, so the raw counts, the computed bound, the confidence rule,
    the threshold and the classification are carried into the record itself.
    """
    stored: list[dict[str, Any]] = []
    for diagnostic in mandatory_diagnostics_for(plan, case_id):
        stored.append({
            "diagnostic_id": diagnostic.diagnostic_id,
            "authority_source": diagnostic.authority_source,
            "authority_path": diagnostic.authority_path,
            "requirement": diagnostic.requirement,
            "aggregate_key": diagnostic.aggregate_key,
            "required_keys": list(diagnostic.required_keys),
            "value": aggregate[diagnostic.aggregate_key],
        })
    return stored


def validate_job_record(record: Mapping[str, Any], plan: Mapping[str, Any],
                        binding: ExecutionBinding, job: CampaignJob | None,
                        output_dir: str) -> None:
    """THE OFFICIAL terminal-record validator. It obtains its own provenance.

    A caller identifies the campaign output root, the planned job and the record
    to check. It supplies NO provenance object: not the Branch-A publication, not
    the calibration lock, not an expected artifact digest, not an expected lock
    digest. Those are resolved here, from the frozen job coordinates and the
    campaign's own durable stores.

    THE DEFECT THIS CLOSES
        This function used to accept `publication` and `lock` as arguments. An
        audit fabricated a calibration lock that had never been persisted --
        matching a fabricated artifact digest in a re-digested terminal record --
        passed the pair in, and validation ACCEPTED it, while the same terminal
        record checked against the actual committed lock refused. The comparison
        logic was right; the trust boundary was not. An object that exists to
        PROVE a record's provenance may not be provided by whoever wants the
        record believed.

    Three independent layers, and all three are required:

        INTERNAL   the record's own digest, its frozen field set, its mandatory
                   diagnostics revalidated from the stored evidence alone
        EXTERNAL   `_require_terminal_links`: package identities, planner
                   coordinates and the committed Branch-A publication
        THRESHOLD  `verified_calibration_lock` then
                   `_compare_terminal_to_verified_lock`: the committed
                   calibration lock, for every job whose frozen plan requires one

    The internal layer is the round trip the first audit found missing. The
    external layer is what the second audit found missing: without it a caller
    could edit any provenance link, recompute the record's digest, and be
    believed. The threshold layer is the third audit's finding, and it is
    separate because the first two do not imply it: a record can name the right
    campaign, the right coordinates and the right published evidence while naming
    a calibration artifact that was never locked, or none at all.
    """
    if record.get("schema") != JOB_RECORD_SCHEMA:
        raise ResultSchemaInvalid(
            f"job record schema {record.get('schema')!r} is not {JOB_RECORD_SCHEMA!r}")
    if "result_digest" not in record:
        raise ResultSchemaInvalid("a job record carries its own digest")
    recomputed = sealed_digest(dict(record), "result_digest")
    if recomputed != record["result_digest"]:
        raise ResultSchemaInvalid(
            f"the job record hashes to {recomputed} but declares "
            f"{record['result_digest']}; it was edited after it was recorded")
    coordinates = record.get("coordinates") or {}
    case_id = coordinates.get("case_id")
    required = required_result_fields(plan, case_id)
    if tuple(record.get("fields") or ()) != required:
        raise ResultFieldSetMismatch(
            f"{record.get('job_id')}: stored fields {record.get('fields')} are not "
            f"the frozen field set {list(required)}")
    declared = mandatory_diagnostics_for(plan, case_id)
    stored = {row["diagnostic_id"]: row for row in record.get("mandatory_diagnostics", [])}
    missing = [d.diagnostic_id for d in declared if d.diagnostic_id not in stored]
    if missing:
        raise ContractMandatoryDiagnosticMissing(
            f"{record.get('job_id')}: the stored result omits mandatory "
            f"diagnostic(s) {missing}, which frozen authority requires to be "
            "reported. A result may not pass validation and then discard the "
            "evidence proving it.")
    # Rebuild the minimum aggregate the diagnostics describe and re-run the SAME
    # validator, so the stored evidence is checked rather than merely present.
    rebuilt = {"case_id": case_id, "schema": MANIFEST_SCHEMA}
    for row in stored.values():
        rebuilt[row["aggregate_key"]] = row["value"]
    require_mandatory_diagnostics(rebuilt, plan, required)
    require_endpoint_events(plan, case_id, record.get("result") or {},
                            record.get("job_id") or "<unnamed job>")
    # THE DURABLE PROVENANCE, RESOLVED HERE, from the frozen job and the store.
    if job is None:
        raise TerminalProvenanceMismatch(
            f"{record.get('job_id')}: no planned job was supplied to validate this "
            "record against. A terminal record cannot vouch for its own "
            "coordinates.")
    publication = verified_publication(output_dir, job, binding)
    lock = verified_calibration_lock(output_dir, job, binding)
    _require_terminal_links(record, binding, job=job, publication=publication)
    # `_require_terminal_links` has established that `publication` is present and
    # is this record's own, so the threshold comparison can rely on it without
    # restating its absence.
    _compare_terminal_to_verified_lock(record, job, lock, publication, binding)


def _require_terminal_links(record: Mapping[str, Any], binding: ExecutionBinding,
                            job: CampaignJob | None = None,
                            publication: Mapping[str, Any] | None = None) -> None:
    """Bind a terminal record to the CURRENT authority, not only to itself.

    PRIVATE. `publication` must already be the committed record resolved from the
    campaign's own store; the official entry point `validate_job_record` resolves
    it, and a caller may not supply one.

    THE DEFECT THIS CLOSES
        `validate_job_record` recomputed the record's own digest and nothing
        else. An independent audit changed the execution identity, the Branch-A
        evidence hash, the publication digest and even the job coordinates,
        re-digested the record, and validation accepted all four. A self-
        consistent digest proves only that the bytes were not edited after they
        were written; it cannot prove the bytes describe THIS campaign.

    The internal digest is KEPT -- it protects the bytes -- and these external
    links are added on top:

        package identities   == the current ExecutionBinding
        coordinates, job id,
        result kind, role,
        calibration requirement
                             == the frozen deterministic planner
        Branch-A evidence hash,
        publication digest,
        calibration condition
                             == the COMMITTED Branch-A publication for this job

    A record cannot define its own scientific coordinates, and it cannot vouch
    for upstream evidence by quoting a hash it also supplies.
    """
    job_id = record.get("job_id") or "<unnamed job>"
    # BOTH external anchors are REQUIRED. An optional cross-check is a weaker
    # validation path, and a weaker path is the defect: a terminal record with no
    # planned job or no committed publication is not evidence of anything.
    if job is None:
        raise TerminalProvenanceMismatch(
            f"{job_id}: no planned job was supplied to validate this record "
            "against. A terminal record cannot vouch for its own coordinates.")
    if publication is None:
        raise TerminalProvenanceMismatch(
            f"{job_id}: no committed Branch-A publication exists for these "
            "coordinates. A result whose upstream evidence is absent is not a "
            "completed job, whatever its own digest says.")
    identities = record.get("package_identities") or {}
    for key, current in (("contract_sha256", binding.binding.sha256),
                         ("plan_sha256", binding.plan_sha256),
                         ("seed_map_sha256", binding.seed_map_sha256),
                         ("analysis_procedure_identity", binding.analysis_identity),
                         ("execution_identity", binding.execution_identity)):
        if identities.get(key) != current:
            raise TerminalProvenanceMismatch(
                f"{job_id}: stored {key} {identities.get(key)!r} is not the current "
                f"{current!r}. The record describes a different package than the one "
                "validating it; re-digesting the record does not make it current.")
    # --- the frozen deterministic planner ------------------------------------
    if record.get("coordinates") != job.coordinates.as_dict():
        raise TerminalProvenanceMismatch(
            f"{job_id}: stored coordinates {record.get('coordinates')!r} are not "
            f"the planner's {job.coordinates.as_dict()!r}. A terminal record does "
            "not define its own scientific coordinates.")
    for key, expected in (("job_id", job.job_id),
                          ("result_kind", job.result_kind),
                          ("role", job.role),
                          ("requires_calibration", job.requires_calibration)):
        if record.get(key) != expected:
            raise TerminalProvenanceMismatch(
                f"{job_id}: stored {key} {record.get(key)!r} is not the frozen "
                f"planner's {expected!r}")
    # --- the COMMITTED Branch-A publication for these exact coordinates ------
    if record.get("branch_a_evidence_sha256") != publication.get(
            "branch_a_evidence_sha256"):
        raise TerminalProvenanceMismatch(
            f"{job_id}: the stored Branch-A evidence hash is not the one in the "
            "committed publication for these coordinates")
    if record.get("publication_digest") != publication.get("publication_digest"):
        raise TerminalProvenanceMismatch(
            f"{job_id}: the stored publication digest is not the committed "
            "publication's own digest")
    if record.get("calibration_condition_sha256") != publication.get(
            "calibration_condition_sha256"):
        raise TerminalProvenanceMismatch(
            f"{job_id}: the stored calibration-condition identity is not the one "
            "the committed Branch-A publication was bound to")
    if not job.requires_calibration:
        for key in ("calibration_condition_sha256", "calibration_artifact_sha256"):
            if record.get(key) is not None:
                raise TerminalProvenanceMismatch(
                    f"{job_id}: {job.coordinates.case_id} evaluates no P1 / Block-1 "
                    f"quantity, so {key} must be null; a calibration requirement may "
                    "not be invented for it")


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


# ------------------------------------------------------- restart reconciliation
def published_coordinates(record: Mapping[str, Any]) -> JobCoordinates:
    """The coordinates a published record declares, as a typed address."""
    return JobCoordinates(**record["coordinates"])


def inventory_publications(output_dir: str) -> dict[str, dict[str, Any]]:
    """INDEPENDENTLY discover every committed Branch-A publication on disk.

    THE DEFECT THIS CLOSES
        Restart verification used to iterate over the records its CALLER supplied
        and report success when that list was empty -- including when a published
        artifact existed on disk. An audit demonstrated exactly that: an empty
        supplied list returned `{"verified_publications": 0}` beside a real
        publication. A caller could therefore hide an artifact by not mentioning
        it, which is the one thing a reconciliation must make impossible.

        Nothing here consults an argument about what should exist. The directory
        is scanned, every entry is classified, and orphans, dangling markers and
        unexplained entries refuse rather than being skipped.
    """
    directory = publication_directory(output_dir)
    inventory = require_clean_inventory(directory, "the Branch-A publication store")
    found: dict[str, dict[str, Any]] = {}
    for basename in inventory.committed:
        record, _ = read_committed(directory, basename, "a Branch-A publication")
        require_publication_schema(record, os.path.join(directory, basename))
        coordinates = published_coordinates(record)
        if publication_basename(coordinates) != basename:
            raise RestartInventoryMismatch(
                f"{basename!r} contains a record addressing "
                f"{publication_basename(coordinates)!r}; a misfiled publication is "
                "not this replicate's evidence")
        if coordinates.job_id in found:
            raise RestartInventoryMismatch(
                f"two committed publications claim {coordinates.job_id}; a job has "
                "exactly one Branch-A publication")
        found[coordinates.job_id] = record
    return found


def realisation_from_record(record: Mapping[str, Any]) -> BranchARealisation:
    """Rebuild the Branch-A evidence object from its own published record.

    The canonical form is exact -- every float is `float.hex()` -- so this is a
    lossless inverse, not a reconstruction. It is what makes a resume possible
    after the process that published the evidence is gone: the campaign recovers
    what it published from the publication itself, never from memory and never by
    regenerating it under a fresh seed.
    """
    evidence = record["branch_a_evidence"]

    def number(value: str) -> float:
        return float.fromhex(value)

    return BranchARealisation(
        coordinates=JobCoordinates(**record["coordinates"]),
        field_id=evidence["field_id"],
        branch_a_seed=evidence["branch_a_seed"],
        common_mode_seed=evidence["common_mode_seed"],
        H_A=tuple(tuple(number(v) for v in row) for row in evidence["H_A"]),
        T_measured=number(evidence["T_measured"]),
        k_modes_measured=tuple(number(k) for k in evidence["k_modes_measured"]),
        rot_deg_measured=number(evidence["rot_deg_measured"]),
        tau_modes=tuple(number(t) for t in evidence["tau_modes"]),
        scale_factor=number(evidence["scale_factor"]),
        n_samples=evidence["n_samples"],
        dt=number(evidence["dt"]),
        calibration_route=evidence["calibration_route"],
        branch_a_status=evidence["branch_a_status"],
        contract_sha256=evidence["contract_sha256"],
        plan_sha256=evidence["plan_sha256"],
        analysis_identity=evidence["analysis_identity"],
        generator_identity=evidence["generator_identity"],
    )


def recover_realisations(output_dir: str,
                         binding: ExecutionBinding) -> dict[str, BranchARealisation]:
    """The AUTHORISED deterministic recovery: rebuild the checkpoint from disk.

    This is the only permitted way to answer "what did the previous run publish?"
    after that run is gone. It reads; it never writes, never deletes and never
    regenerates. An orphaned or tampered store refuses here rather than being
    quietly repaired, because an interrupted publication is a thing to inspect.

    The recovered records are then put through the SAME strict reconciliation as
    a caller-supplied checkpoint: recovery is not a way around set equality, it
    is a way to obtain the set honestly.
    """
    recovered: dict[str, BranchARealisation] = {}
    for job_id, record in inventory_publications(output_dir).items():
        # A persisted non-finite measurement refuses in the SCIENTIFIC canonical
        # encoder, which is right but uncoded. Recovery gives it the same coded
        # provenance category the shared verifier uses, so restart reports the
        # same diagnosis rather than an anonymous refusal.
        try:
            realisation = realisation_from_record(record)
            recomputed = realisation.evidence_sha256
        except Refusal as exc:
            if isinstance(exc, CodedRefusal):
                raise
            raise BranchAMeasurementInvalid(
                f"{job_id}: the published Branch-A evidence cannot be recovered "
                f"as a measurement ({exc})") from exc
        if recomputed != record["branch_a_evidence_sha256"]:
            raise RestartInventoryMismatch(
                f"{job_id}: the evidence recovered from its publication does not "
                "reproduce the published digest; the canonical form is exact, so a "
                "mismatch means the record is not what it claims to be")
        recovered[job_id] = realisation
    return recovered


# ------------------------------------------------------ terminal job records
def job_record_directory(output_dir: str) -> str:
    return os.path.join(output_dir, JOB_RECORD_DIR)


def job_record_basename(coordinates: JobCoordinates) -> str:
    """One immutable record per job. A pure function of the coordinates."""
    return f"job_{canonical_digest(coordinates.as_dict())}.json"


def committed_publication(output_dir: str,
                          coordinates: JobCoordinates) -> dict[str, Any] | None:
    """The COMMITTED Branch-A publication for these coordinates, or None.

    None only when no publication exists at all; anything present but not
    committed refuses inside `read_committed` rather than being skipped.
    """
    directory = publication_directory(output_dir)
    basename = publication_basename(coordinates)
    if not os.path.lexists(os.path.join(directory, basename)):
        return None
    record, _marker = read_committed(directory, basename,
                                     "the Branch-A publication record")
    return record


def publish_job_record(output_dir: str, record: Mapping[str, Any],
                       binding: ExecutionBinding) -> PublicationReceipt:
    """Durably COMMIT one job's terminal record, through the same transaction.

    A scientific result that exists only in a process's memory is not evidence,
    and a result file that appears at a path is not a completed job. Both
    questions get the same answer as Branch-A publication does: an artifact plus
    a commit marker that binds its exact bytes.
    """
    coordinates = JobCoordinates(**record["coordinates"])
    return publish_transaction(
        job_record_directory(output_dir), job_record_basename(coordinates),
        dict(record), publication_digest=record["result_digest"],
        provenance={"coordinates": coordinates.as_dict(),
                    "job_id": record["job_id"],
                    "execution_identity": binding.execution_identity})


def inventory_job_records(output_dir: str, binding: ExecutionBinding,
                          planned: Sequence[CampaignJob]
                          ) -> dict[str, dict[str, Any]]:
    """INDEPENDENTLY discover every committed terminal record. Reads only.

    Orphans, dangling markers and unexplained entries refuse here exactly as they
    do for Branch-A publications: a partial result must never count as completed
    scientific evidence.

    `planned` is REQUIRED and is checked against the frozen planner. It used to
    default to None, which silently turned off every semantic check below.
    """
    planned = require_authentic_plan(binding, planned,
                                     "terminal-record reconciliation")
    directory = job_record_directory(output_dir)
    inventory = require_clean_inventory(directory, "the terminal job-record store")
    by_job_id = {job.job_id: job for job in planned}
    # EVERY PERSISTED LOCK IS VALIDATED FIRST, as a complete intermediate
    # provenance object in its own right. Whether a lock is valid may not depend
    # on whether a downstream terminal record happens to exist, so this does not
    # wait for the loop below to reach one.
    reconcile_calibration_locks(output_dir, binding, planned)
    found: dict[str, dict[str, Any]] = {}
    for basename in inventory.committed:
        record, marker = read_committed(directory, basename, "a terminal job record")
        coordinates = JobCoordinates(**record["coordinates"])
        if job_record_basename(coordinates) != basename:
            raise RestartInventoryMismatch(
                f"{basename!r} holds the record of {coordinates.job_id!r}, which "
                f"belongs at {job_record_basename(coordinates)!r}")
        if marker["publication_digest"] != record.get("result_digest"):
            raise RestartInventoryMismatch(
                f"{basename!r}: the commit marker committed a different result digest")
        # An undeclared job is named as such BEFORE the provenance verifier runs,
        # so the refusal says "this record belongs to no planned job" rather than
        # the vaguer "no planned job was supplied to validate it against".
        if coordinates.job_id not in by_job_id:
            raise RestartInventoryMismatch(
                f"the terminal record {basename!r} belongs to {coordinates.job_id!r}, "
                "which this campaign never declared")
        # THE SAME VERIFIER THE WRITE PATH USES, with the same external links --
        # the committed publication AND the committed calibration lock. A record
        # accepted when written and refused on restart, or the reverse, is a
        # design error; there is one terminal-provenance rule and one threshold
        # rule, and restart is never the weaker path.
        validate_job_record(record, binding.plan, binding,
                            job=by_job_id.get(coordinates.job_id),
                            output_dir=output_dir)
        if coordinates.job_id in found:
            raise RestartInventoryMismatch(
                f"two committed records claim {coordinates.job_id}")
        found[coordinates.job_id] = record
    undeclared = sorted(set(found) - {job.job_id for job in planned})
    if undeclared:
        raise RestartInventoryMismatch(
            f"{len(undeclared)} terminal record(s) belong to no planned job "
            f"(e.g. {undeclared[:3]})")
    return found


def verify_restart(output_dir: str, realisations: Mapping[str, BranchARealisation],
                   binding: ExecutionBinding,
                   planned: Sequence[CampaignJob]) -> dict[str, Any]:
    """Reconcile what the campaign CLAIMS exists against what ACTUALLY exists.

    Set equality in BOTH directions:

        claimed but absent on disk    -> refuse  (the checkpoint is wrong)
        present on disk but unclaimed -> refuse  (the caller omitted an artifact)

    An empty result is valid only when the persisted inventory is also empty.
    Published evidence is never regenerated, replaced or dropped here: a completed
    replicate is not re-run because its outcome was undesirable, and this only
    proves that what was published is still exactly what was published.
    """
    planned = require_authentic_plan(binding, planned, "restart reconciliation")
    on_disk = inventory_publications(output_dir)
    claimed = dict(realisations)
    for job_id, realisation in claimed.items():
        if realisation.coordinates.job_id != job_id:
            raise RestartInventoryMismatch(
                f"the restart record keyed {job_id!r} holds evidence for "
                f"{realisation.coordinates.job_id!r}")
    missing = sorted(set(claimed) - set(on_disk))
    if missing:
        raise RestartInventoryMismatch(
            f"the campaign claims {len(missing)} publication(s) that do not exist on "
            f"disk (e.g. {missing[:3]}). A checkpoint that names evidence the store "
            "does not hold is not a resumable state.")
    unclaimed = sorted(set(on_disk) - set(claimed))
    if unclaimed:
        raise RestartInventoryMismatch(
            f"{len(unclaimed)} committed publication(s) exist on disk that the "
            f"campaign does not claim (e.g. {unclaimed[:3]}). Persisted scientific "
            "evidence is append-only: it may not be ignored, replaced, regenerated "
            "under another seed, or dropped because it is inconvenient.")
    declared = {job.job_id: job for job in planned}
    undeclared = sorted(set(on_disk) - set(declared))
    if undeclared:
        raise RestartInventoryMismatch(
            f"{len(undeclared)} publication(s) belong to no planned job (e.g. "
            f"{undeclared[:3]}); the store holds evidence this campaign never "
            "declared")
    # EVERY PERSISTED PUBLICATION, through the SAME verifier terminal validation
    # uses -- not only the ones a caller claims. A publication that was durably
    # committed but is not a valid publication for its planned job under the
    # current package must not enter reconciled state.
    for job_id in sorted(on_disk):
        verified_publication(output_dir, declared[job_id], binding)
    verified = 0
    for job_id, realisation in sorted(claimed.items()):
        # The claimed ones additionally prove that the evidence IN HAND is the
        # evidence that was published, which the store alone cannot show.
        verify_publication(output_dir, realisation, binding)
        verified += 1
    # THE CALIBRATION-LOCK STORE, reconciled through the ONE canonical verifier.
    # Every committed lock is a claim that a Block-1 threshold was fixed for a
    # specific job, so an unexplained one is exactly as serious as an unexplained
    # publication -- and it is checked COMPLETELY here, not partially, because a
    # legitimate resumable state is precisely one where no terminal record exists
    # yet and there is nothing downstream left to catch it.
    locks = reconcile_calibration_locks(output_dir, binding, planned)
    return {"verified_publications": verified,
            "publications_on_disk": len(on_disk),
            "claimed_publications": len(claimed),
            "calibration_locks_on_disk": len(locks),
            "missing_on_disk": 0, "unclaimed_on_disk": 0}


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
        "job_record_schema": JOB_RECORD_SCHEMA,
        "campaign_result_schema": CAMPAIGN_RESULT_SCHEMA,
        "publication_schema": BRANCH_A_PUBLICATION_SCHEMA,
        "publication_commit_schema": COMMIT_SCHEMA,
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


# ------------------------------------------- completeness and case aggregation
def require_campaign_completeness(jobs: Sequence[CampaignJob],
                                  records: Mapping[str, Mapping[str, Any]]
                                  ) -> dict[str, int]:
    """Every frozen job has EXACTLY ONE authorised terminal record. Derived.

    The expected total is never written down here: it is the length of the job
    plan the FROZEN plan produces, so a plan declaring different replicate counts
    changes this number mechanically and a hard-coded one could not.
    """
    declared = [job.job_id for job in jobs]
    if len(set(declared)) != len(declared):
        raise CampaignPlanMismatch("the job plan contains duplicate job identities")
    expected, present = set(declared), set(records)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing or extra:
        raise CampaignIncomplete(
            f"campaign aggregation refused: {len(missing)} frozen job(s) have no "
            f"terminal record (e.g. {missing[:3]}) and {len(extra)} record(s) belong "
            f"to no frozen job (e.g. {extra[:3]}). A case rate whose denominator is "
            "'the jobs that happened to finish' is not the declared denominator.")
    for job_id, record in records.items():
        if record.get("terminal_state") != RECORDED:
            raise CampaignIncomplete(
                f"{job_id}: terminal state {record.get('terminal_state')!r} is not "
                f"{RECORDED!r}")
    return {"declared_jobs": len(expected), "terminal_records": len(present),
            "missing_terminal_jobs": 0, "extra_terminal_jobs": 0,
            "duplicate_terminal_jobs": 0}


def release_subconditions(plan: Mapping[str, Any], case_id: str) -> tuple[str, ...]:
    """The subconditions a case's RELEASE criterion is evaluated over.

    Where the frozen plan marks one subcondition `feeds_primary_claim`, that one
    alone carries the release claim and the others are reported and never pooled
    into it -- disposition G3, closed prospectively. Where none is marked, every
    declared subcondition is a release unit in its own right (per cell, per rho,
    per alternative), which is what the assurance row's `unit` says.
    """
    subs = case_entry(plan, case_id)["subconditions"]
    primary = tuple(s["subcondition_id"] for s in subs if s.get("feeds_primary_claim"))
    return primary or tuple(s["subcondition_id"] for s in subs)


def assemble_case_aggregates(jobs: Sequence[CampaignJob],
                             records: Mapping[str, Mapping[str, Any]]
                             ) -> dict[str, dict[str, Any]]:
    """Group terminal records by case using the IMMUTABLE planned job identity.

    Case membership is a property of the frozen plan, never of an argument. A
    caller cannot present a C7 record inside C1's denominator, because the
    grouping reads `job.coordinates.case_id` from the planned job and refuses if
    the record disagrees with the job it is filed under.
    """
    membership: dict[str, list[str]] = {}
    for job in jobs:
        membership.setdefault(job.coordinates.case_id, []).append(job.job_id)
    aggregates: dict[str, dict[str, Any]] = {}
    for case_id, job_ids in sorted(membership.items()):
        by_subcondition: dict[str, list[str]] = {}
        for job_id in sorted(job_ids):
            record = records[job_id]
            coordinates = record.get("coordinates") or {}
            if coordinates.get("case_id") != case_id:
                raise ResultCaseMismatch(
                    f"{job_id} is planned in case {case_id!r} but its terminal record "
                    f"declares {coordinates.get('case_id')!r}; cross-case "
                    "substitution refused")
            by_subcondition.setdefault(coordinates.get("subcondition_id"),
                                       []).append(job_id)
        aggregates[case_id] = {
            "case_id": case_id,
            "planned_jobs": len(job_ids),
            "terminal_records": len(job_ids),
            "by_subcondition": {k: sorted(v) for k, v in sorted(by_subcondition.items())},
        }
    return aggregates


#: Endpoint events that belong to ONE FIELD. Each field record carries its own.
FIELD_LEVEL_EVENTS = ("analysis_status", "P1", "p1_rejected", "block1_rejected",
                      "g5_rejected", "beta_hat")
#: Endpoint events that belong to the REPLICATE as a whole. Every field record of
#: a replicate carries the same value, and disagreement is a defect.
REPLICATE_LEVEL_EVENTS = ("P2", "P3", "P4", "complete_pass", "false_acceptance",
                          "scale_recovered")


def required_endpoint_events(plan: Mapping[str, Any], case_id: str) -> tuple[str, ...]:
    """The endpoint decisions a case's record MUST carry, derived from the plan.

    Case-aware by construction, as the audit requires: a case that evaluates a
    P1 / Block-1 quantity owes the per-field P1 decision and both block decisions;
    a case whose release endpoint is the complete pipeline owes `complete_pass`;
    the false-bridge control owes its acceptance event; the blinded scale control
    owes its recovery event. Nothing is nullable-by-default and then interpreted
    opportunistically.
    """
    case = case_entry(plan, case_id)
    required = ["analysis_status"]
    if case.get("uses_p1_block1"):
        required += ["P1", "p1_rejected", "block1_rejected", "g5_rejected"]
    endpoint = case["primary_release_endpoint"]
    if endpoint == "COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4":
        required.append("complete_pass")
    if endpoint == "P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE":
        required.append("false_acceptance")
    if endpoint == "P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY":
        required.append("scale_recovered")
    return tuple(required)


def require_endpoint_events(plan: Mapping[str, Any], case_id: str,
                            outcome: Mapping[str, Any], job_id: str) -> None:
    """Fail closed on an absent endpoint decision. MISSING IS NOT PASS.

    The one legitimate absence is a STRUCTURED SCIENTIFIC REFUSAL: when the
    analysis did not reach ESTIMATED, the two block decisions do not exist
    because the frozen gate produced no p-values, and P1 has already failed
    closed. That exemption is explicit, is justified by the record's own
    `analysis_status`, and is the only one.
    """
    estimated = outcome.get("analysis_status") == "ESTIMATED"
    for event in required_endpoint_events(plan, case_id):
        if event not in outcome:
            raise EndpointEventMissing(
                f"{job_id}: the record carries no {event!r}, which {case_id} "
                "requires. A missing decision is not a pass and not a "
                "zero-rejection.")
        if outcome[event] is None:
            if event in ("block1_rejected", "g5_rejected") and not estimated:
                continue          # structured refusal: the gate produced no rows
            raise EndpointEventMissing(
                f"{job_id}: {event!r} is null while analysis_status is "
                f"{outcome.get('analysis_status')!r}. A null decision may not be "
                "counted as zero rejections.")


def field_event_count(records: Mapping[str, Mapping[str, Any]], case_id: str,
                      subcondition_id: str, field_id: str, event: str,
                      declared_replicates: int) -> int:
    """Count the replicates in which THIS FIELD's own event occurred.

    THE DEFECT THIS CLOSES
        C2's frozen rule is PER FIELD, never pooled. The previous counter
        filtered records by field but read a replicate-wide value, so one field
        rejecting made all four fields count a rejection. This reads the field's
        own decision, and refuses if it is absent rather than scoring it zero.
    """
    if event not in FIELD_LEVEL_EVENTS:
        raise ResultSchemaInvalid(
            f"{event!r} is not a per-field endpoint event; per-field counting of a "
            "replicate-level value is exactly the defect this function exists to "
            "prevent")
    seen: dict[int, bool] = {}
    for record in records.values():
        coordinates = record.get("coordinates") or {}
        if (coordinates.get("case_id") != case_id
                or coordinates.get("subcondition_id") != subcondition_id
                or coordinates.get("scope") != field_id):
            continue
        result = record.get("result") or {}
        if event not in result or result[event] is None:
            raise EndpointEventMissing(
                f"{case_id}/{subcondition_id}/{field_id} replicate "
                f"{coordinates.get('replicate_id')}: {event!r} is absent or null; "
                "it may not be counted as a non-event")
        seen[coordinates.get("replicate_id")] = bool(result[event])
    if len(seen) != declared_replicates:
        raise CampaignIncomplete(
            f"{case_id}/{subcondition_id}/{field_id}: {len(seen)} replicate records "
            f"for a declared {declared_replicates}. Structured refusals COUNT in "
            "the denominator; a missing replicate does not.")
    return sum(1 for value in seen.values() if value)


def replicate_outcomes(records: Mapping[str, Mapping[str, Any]], case_id: str,
                       subcondition_id: str) -> dict[int, Mapping[str, Any]]:
    """One outcome per REPLICATE of one subcondition, from the per-field records.

    Only genuinely REPLICATE-LEVEL events are read. Per-field events -- the
    analysis status, P1, and the two block decisions -- legitimately differ
    between the fields of one replicate and are counted by
    `field_event_count` instead; requiring them to agree here was part of the
    same conflation the audit found.
    """
    out: dict[int, Mapping[str, Any]] = {}
    for record in records.values():
        coordinates = record.get("coordinates") or {}
        if (coordinates.get("case_id") != case_id
                or coordinates.get("subcondition_id") != subcondition_id):
            continue
        replicate = coordinates.get("replicate_id")
        result = record.get("result") or {}
        verdict = {k: result.get(k) for k in REPLICATE_LEVEL_EVENTS}
        previous = out.get(replicate)
        if previous is not None and previous != verdict:
            raise ResultSchemaInvalid(
                f"{case_id}/{subcondition_id} replicate {replicate}: two field "
                "records disagree about a REPLICATE-LEVEL endpoint; the fields of "
                "one replicate are one experiment and have one such outcome")
        out[replicate] = verdict
    return out


#: C3 and C4 are scored over REPLICATES -- `unit: campaign`, R = 400 and R = 2000 --
#: while the events they score, the Block-2 (G5) and Block-1 decisions, are
#: produced PER FIELD by the two-block gate. Both cases declare four fields, so a
#: rule is needed to turn four per-field decisions into the one replicate-level
#: event their denominators count. Frozen authority does not state one:
#: `size_validation_semantics.derived_boundaries` marks C2 `per_field: true` and
#: says nothing of the kind for C3 or C4, and neither case's criterion, endpoint
#: nor assurance row defines the reduction. Disjunction ("any field rejects") is
#: the obvious guess and it is still a guess: it changes the measured size, so it
#: is a scientific decision, not an implementation detail.
UNDECLARED_EVENT_REDUCTION = (
    "frozen authority does not declare how the four PER-FIELD decisions of a "
    "replicate combine into the ONE replicate-level event this case's denominator "
    "counts. The case is scored over replicates (assurance unit 'campaign') while "
    "the two-block gate decides per field, and no frozen document states the "
    "reduction. The driver refuses rather than choosing between 'any field "
    "rejects', 'the reference field rejects' and 'every field rejects', which are "
    "different measured sizes. This must be declared in frozen authority BEFORE "
    "the seal is frozen."
)


def replicate_level_rejections(plan: Mapping[str, Any],
                               records: Mapping[str, Mapping[str, Any]],
                               case_id: str, event: str) -> int:
    """The replicate-level rejection count for a case scored over replicates.

    Implemented where the reduction is unambiguous (a single declared field) and
    REFUSED, by name, where frozen authority leaves it open. The per-field
    decisions themselves are recorded faithfully either way, so the eventual
    authorised reduction has genuine events to consume.
    """
    fields = required_result_fields(plan, case_id)
    subcondition = release_subconditions(plan, case_id)[0]
    declared = case_entry(plan, case_id)["replicate_count"]
    if len(fields) == 1:
        return field_event_count(records, case_id, subcondition, fields[0], event,
                                 declared)
    raise EndpointEventReductionUndeclared(
        f"{case_id}: {UNDECLARED_EVENT_REDUCTION} It declares {len(fields)} fields "
        f"and scores {event!r} over {declared} replicates.")


def campaign_counts_from_records(plan: Mapping[str, Any],
                                 records: Mapping[str, Mapping[str, Any]]
                                 ) -> CampaignCounts:
    """Build the frozen classifier's counts from the immutable terminal records.

    Every denominator is the case's DECLARED replicate count, and every count is
    taken over the subconditions the frozen plan makes release units. Nothing here
    is a threshold: the thresholds live in `classify_campaign`, which this feeds.
    """
    def replicates(case_id: str) -> int:
        return case_entry(plan, case_id)["replicate_count"]

    def verdicts(case_id: str, subcondition_id: str) -> dict[int, Mapping[str, Any]]:
        found = replicate_outcomes(records, case_id, subcondition_id)
        if len(found) != replicates(case_id):
            raise CampaignIncomplete(
                f"{case_id}/{subcondition_id}: {len(found)} replicate outcomes for a "
                f"declared {replicates(case_id)}. Structured refusals COUNT in the "
                "denominator; a missing replicate does not.")
        return found

    c1_sub = release_subconditions(plan, "C1_true_bridge_complete")[0]
    c1 = sum(1 for v in verdicts("C1_true_bridge_complete", c1_sub).values()
             if v["complete_pass"] is True)
    # C2: PER FIELD, never pooled. Each field's own P1 decision, counted over its
    # own R replicates -- `size_validation_semantics.derived_boundaries.C2`
    # carries `per_field: true` and `pooling: FORBIDDEN`.
    c2_case = "C2_geometry_false_rejection"
    c2_sub = release_subconditions(plan, c2_case)[0]
    c2 = {field_id: field_event_count(records, c2_case, c2_sub, field_id,
                                      "p1_rejected", replicates(c2_case))
          for field_id in required_result_fields(plan, c2_case)}
    c3 = replicate_level_rejections(plan, records, "C3_g5_block", "g5_rejected")
    c4 = replicate_level_rejections(plan, records, "C4_surrogate_validity",
                                    "block1_rejected")
    # C5 is REPORT ONLY in frozen authority: the criterion is that every declared
    # cell is reported, not that any cell clears a threshold. Completeness IS the
    # criterion, and dropping a cell after inspection is the failure it guards.
    c5_cells = release_subconditions(plan, "C5_plug_in_branch_a")
    c5_pass = all(len(replicate_outcomes(records, "C5_plug_in_branch_a", cell))
                  == replicates("C5_plug_in_branch_a") for cell in c5_cells)
    # C6 has a frozen upper-bound criterion at EACH declared rho.
    # C6 declares exactly ONE field, so its per-field and per-replicate counts
    # coincide and no reduction rule is needed.
    c6_case = "C6_mode_resolution_boundary"
    c6_row = next(r for r in plan["assurance"] if r["case_id"] == c6_case)
    c6_field = required_result_fields(plan, c6_case)
    if len(c6_field) != 1:
        raise EndpointEventReductionUndeclared(
            f"{c6_case} now declares {len(c6_field)} fields; its per-rho count "
            "assumed exactly one and frozen authority declares no reduction rule "
            "for more")
    c6_pass = True
    for rho in release_subconditions(plan, c6_case):
        rejections = field_event_count(records, c6_case, rho, c6_field[0],
                                       "p1_rejected", replicates(c6_case))
        if cp_upper(rejections, c6_row["replicates"]) > c6_row["target_value"]:
            c6_pass = False
    c7 = {alt: sum(1 for v in verdicts("C7_false_bridge", alt).values()
                   if v["false_acceptance"] is True)
          for alt in release_subconditions(plan, "C7_false_bridge")}
    c8_sub = release_subconditions(plan, "C8_blinded_scale_control")[0]
    c8 = sum(1 for v in verdicts("C8_blinded_scale_control", c8_sub).values()
             if v["scale_recovered"] is True)
    return CampaignCounts(
        c1_successes=c1, c2_rejections_by_field=c2, c3_rejections=c3,
        c4_rejections=c4, c5_pass=bool(c5_pass), c6_pass=bool(c6_pass),
        c7_false_acceptances_by_alternative=c7, c8_successes=c8)


# ---------------------------------------------------- the stochastic boundary
class StochasticProvider(Protocol):
    """The ONLY way the orchestration can obtain a source of random numbers.

    Production and tests differ ONLY in which object implements this. There is no
    `force`, `skip_gate`, `ignore_seal`, `test_mode` or `rng_factory` parameter
    anywhere on the production entry point, and `run_campaign` constructs its own
    provider AFTER the gate rather than accepting one, so no argument can carry a
    generator past a refused gate.
    """

    def generator(self, seed: int, purpose: str) -> Generator: ...


#: Why the production provider cannot yet build a generator. This is an AUTHORITY
#: gap, not a missing implementation: frozen authority declares seed INTEGERS
#: (docs/e1a/e1a_v4_seed_map.json) and nowhere declares the pseudo-random
#: algorithm or the transform from uniform to standard normal. Two algorithms
#: seeded identically produce different trajectories, so the choice determines
#: every number the campaign draws. Making it here would be choosing a scientific
#: parameter no frozen document has chosen.
UNDECLARED_GENERATOR = (
    "the pseudo-random generator is NOT DECLARED in frozen authority. The seed map "
    "declares the master seed, the family seeds and the derivation of stream "
    "identities; no frozen document declares the PRNG algorithm or the transform "
    "from uniform to standard normal. Those determine every number drawn, so the "
    "driver refuses rather than choosing them. They must be declared in frozen "
    "authority, and thereby enter the execution identity, BEFORE the seal is frozen."
)


class AuthorisedStochasticProvider:
    """THE production provider. Constructed only past the complete lifecycle gate.

    It is a real object on the real path and it refuses for a real reason: the
    generator it would construct is not declared. The refusal is deliberately
    reachable only after the gate, so a reviewer who ever sees it knows the gate
    passed and the remaining gap is an authority gap, not a software one.
    """

    def __init__(self, binding: ExecutionBinding) -> None:
        self.binding = binding
        self.requests = 0

    def generator(self, seed: int, purpose: str) -> Generator:
        self.requests += 1
        raise StochasticProviderRefused(
            f"STOCHASTIC PROVIDER REFUSED for {purpose!r}: {UNDECLARED_GENERATOR}")


# ------------------------------------------------- the per-job specification
@dataclass(frozen=True)
class JobSpecification:
    """Everything the stochastic path needs for ONE job, resolved from authority.

    Resolution is a separate, auditable step from execution, so "where did this
    number come from?" has one answer per job and the orchestration below cannot
    quietly default anything.
    """

    coordinates: JobCoordinates
    #: The NOISELESS Branch-A field. Branch-A measurement error is applied to it.
    field: BranchAField
    error_model: BranchAErrorModel
    beta_true: float
    dt: float
    n_samples: int
    rank_tol: float
    theta_cap_deg: float
    #: C8 only: the declared deterministic Branch-A scale factors, applied to ONE
    #: underlying replicate. Empty for every other case.
    scale_factors: tuple[float, ...] = ()


def subcondition_entry(plan: Mapping[str, Any], case_id: str,
                       subcondition_id: str) -> Mapping[str, Any]:
    for sub in case_entry(plan, case_id)["subconditions"]:
        if sub["subcondition_id"] == subcondition_id:
            return sub
    raise CampaignPlanMismatch(
        f"case {case_id!r} declares no subcondition {subcondition_id!r}")


def branch_a_error_model(binding: ExecutionBinding, case_id: str,
                         subcondition_id: str) -> BranchAErrorModel:
    """The declared Branch-A measurement-error model for one (case, subcondition).

    Every value is READ: the frozen contract's hypothetical uncertainty scenario
    supplies the declared values, and a subcondition overrides only the parameters
    it explicitly declares. Nothing is defaulted in code, so a scenario key that
    disappeared from the contract would refuse rather than silently become zero.
    """
    scenario = binding.binding.data["hypothetical_uncertainty_scenario"]
    for key in ("sigma_cm", "sigma_k", "sigma_T_K", "sigma_psi_deg"):
        if key not in scenario:
            raise CampaignPlanMismatch(
                f"the frozen contract's uncertainty scenario declares no {key!r}; "
                "the driver refuses to assume a measurement-error parameter")
    sub = subcondition_entry(binding.plan, case_id, subcondition_id)
    return BranchAErrorModel(
        sigma_cm=float(scenario["sigma_cm"]),
        sigma_k=float(sub.get("sigma_k", scenario["sigma_k"])),
        sigma_psi_deg=float(sub.get("sigma_psi_deg", scenario["sigma_psi_deg"])),
        sigma_T=float(scenario["sigma_T_K"]),
    )


def declared_beta_true(plan: Mapping[str, Any], case_id: str, subcondition_id: str,
                       field_id: str) -> float:
    """The truth beta for one field of one subcondition, READ from the plan.

    A false-bridge alternative declares a per-field beta vector aligned with the
    case's `fields_affected`; every other case declares a scalar `beta_truth`.
    Anything else refuses: guessing which field an unaligned vector refers to is
    exactly how a negative control stops being a control.
    """
    case = case_entry(plan, case_id)
    sub = subcondition_entry(plan, case_id, subcondition_id)
    if "beta_true" in sub:
        declared = sub["beta_true"]
        fields = list(case["fields_affected"])
        if not isinstance(declared, list) or len(declared) != len(fields):
            raise CampaignPlanMismatch(
                f"{case_id}/{subcondition_id}: beta_true must declare one value per "
                f"declared field ({len(fields)}), found {declared!r}")
        return float(declared[fields.index(field_id)])
    truth = case.get("beta_truth")
    if isinstance(truth, (int, float)) and not isinstance(truth, bool):
        return float(truth)
    raise CampaignPlanMismatch(
        f"{case_id}/{subcondition_id}: the beta truth for {field_id!r} is declared as "
        f"{truth!r}, which is not a machine-readable value. The driver refuses to "
        "interpret prose as a generating parameter.")


#: Branch-A field construction needs three inputs frozen authority does not
#: declare: the calibration route, the medium viscosity eta and the bead radius a.
#: They are not cosmetic. The frozen relaxation rule is tau_r = gamma(T)/k_r with
#: gamma = 6 pi eta(T) a, so they set every relaxation time, every phi, every
#: effective size N_ab and therefore the entire Block-1 null law. Test fixtures
#: pass literals for them; an official campaign may not.
UNDECLARED_FIELD_INPUTS = (
    "the Branch-A field construction inputs are NOT DECLARED in frozen authority: "
    "calibration_route, viscosity (eta) and bead_radius (a). The frozen relaxation "
    "rule tau_r = gamma(T)/k_r with gamma = 6 pi eta(T) a makes them determine "
    "every phi, every effective size and the entire Block-1 null law. They must be "
    "declared in the frozen contract or plan, and thereby enter the execution "
    "identity, BEFORE the seal is frozen."
)

#: C6 analyses a 'synthetic two-mode field at the declared rho'. The plan declares
#: the three rho values and N_12 and gives no machine-readable construction for
#: the field that realises them; the four contract fields are not it.
UNDECLARED_C6_FIELD = (
    "case C6_mode_resolution_boundary declares its field as prose -- 'synthetic "
    "two-mode field at the declared rho' -- and frozen authority gives no "
    "machine-readable construction for it. The contract declares four fields and "
    "none is at a declared rho. The construction must be declared in frozen "
    "authority BEFORE the seal is frozen: the driver refuses to invent a geometry "
    "whose eigenvalue ratio IS the quantity under test."
)


def resolve_job_specification(binding: ExecutionBinding,
                              job: CampaignJob) -> JobSpecification:
    """Resolve one job's generating inputs FROM FROZEN AUTHORITY, or refuse.

    This is the AUTHORITY BOUNDARY of the execution path. Below it the
    orchestration is mechanical; above it every value must have been declared by a
    frozen document. Where authority is silent the resolver refuses and names the
    exact missing declaration, because a driver that supplies a plausible default
    for an undeclared generating parameter has quietly become the author of the
    experiment.

    Both refusals below are AUTHORITY GAPS found by writing this path before the
    seal was frozen, which is what writing it before the seal is for.
    """
    case_id = job.coordinates.case_id
    field_id = job.coordinates.scope
    declared_fields = {f["id"] for f in binding.binding.fields}
    if field_id not in declared_fields:
        if case_id == "C6_mode_resolution_boundary":
            raise CampaignPlanMismatch(f"{job.job_id}: {UNDECLARED_C6_FIELD}")
        raise CampaignPlanMismatch(
            f"{job.job_id}: the frozen contract declares no field {field_id!r}")
    raise CampaignPlanMismatch(f"{job.job_id}: {UNDECLARED_FIELD_INPUTS}")


# --------------------------------------------------- endpoint assembly, frozen
def uncertainty_model(binding: ExecutionBinding,
                      specifications: Mapping[str, JobSpecification],
                      analyses: Mapping[str, Any]) -> UncertaintyModel:
    """The declared uncertainty model, with sigma_stat DERIVED per field.

    sigma_cm and sigma_fs come from the frozen contract scenario;
    `e1a_v4.effective_size.sigma_stat` supplies the statistical term from the
    field's own phi modes and record length. No term is restated here.
    """
    per_field: dict[str, float] = {}
    for field_id, specification in specifications.items():
        phis = [math.exp(-specification.dt / tau)
                for tau in specification.field.tau_modes]
        per_field[field_id] = sigma_stat(list(phis), specification.n_samples)
    return UncertaintyModel.from_contract(binding.binding, per_field)


#: The two-block P1 gate's own gate names, from the frozen calibration layer.
#: Used only to READ the p-values `p1_geometry` already computed.
_BLOCK1_GATES = BLOCK1_GATES


def p1_block_decisions(result: Any, artifact: CalibrationArtifact | None,
                       binding: ExecutionBinding) -> tuple[bool | None, bool | None]:
    """Split the FROZEN P1 result into its two block decisions. READS; recomputes nothing.

    THE DEFECT THIS CLOSES
        Endpoint assembly wrote `block1_rejected = None` and `g5_rejected = None`
        unconditionally, so C4's and C3's rejection counters read zero whatever
        was observed. An independent audit demonstrated it; this recovers the two
        decisions the frozen gate already made.

    `e1a_v4.endpoints.p1_geometry` returns the per-gate p-values it computed and
    the artifact carries the critical p_min it finalised at calibration time.
    Both are read here; no statistic, threshold or p-value is recalculated, and
    no new test is introduced. `p1_geometry` itself is an analysis-bound
    SCIENTIFIC MODULE and is deliberately not modified to expose them, because
    that would move the frozen analysis procedure identity.

    Returns `(None, None)` only when the gate produced no rows at all, which
    happens exactly when the analysis was not ESTIMATED and P1 failed closed.
    That case is a STRUCTURED SCIENTIFIC REFUSAL, and the record must say so.
    """
    rows = {gate: p_value for gate, _observed, p_value in getattr(result, "rows", ())}
    if not rows or artifact is None:
        return None, None
    missing = [g for g in _BLOCK1_GATES if g not in rows] + (
        [] if "G5" in rows else ["G5"])
    if missing:
        raise EndpointEventMissing(
            f"the frozen P1 result carries no p-value for {missing}; the two-block "
            "decision cannot be read from it")
    p_min = min(rows[gate] for gate in _BLOCK1_GATES)
    block1_rejected = bool(p_min < artifact.critical_p_min())
    g5_rejected = bool(rows["G5"] < binding.binding.alpha_2)
    return block1_rejected, g5_rejected


def evaluate_replicate(binding: ExecutionBinding, case_id: str, subcondition_id: str,
                       specifications: Mapping[str, JobSpecification],
                       analyses: Mapping[str, Any],
                       conditions: Mapping[str, CalibrationCondition],
                       artifacts: Mapping[str, CalibrationArtifact],
                       blinded: Mapping[float, Mapping[str, Any]] | None = None,
                       ) -> dict[str, Any]:
    """The frozen endpoints for ONE replicate. Calls; never reimplements.

        P1  e1a_v4.endpoints.p1_geometry     per field, against its locked artifact
        P2  e1a_v4.endpoints.p2_cross_field  intersection-union across fields
        P3  e1a_v4.endpoints.p3_absolute     conjunctive over every tested field
        P4  e1a_v4.endpoints.p4_consistency  deterministic, consumes no Branch-B data

    THE DEFECT THIS CLOSES
        The previous revision returned ONE replicate-wide `p1_rejected`, which
        `execute_replicate` then stamped onto all four field records. An
        independent audit showed the consequence: a replicate in which exactly
        one field rejected was counted by C2 as FOUR field rejections, because
        C2's frozen rule is PER FIELD and the value it read was the replicate's
        disjunction. Per-field outcomes now live in `per_field`, one entry per
        field, and the replicate-level endpoints keep their own names.

    The composition is the plan's own declared endpoint, not a convention: a case
    whose `primary_release_endpoint` is COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4
    passes only if every one of them passes.
    """
    contract = binding.binding
    unc = uncertainty_model(binding, specifications, analyses)
    per_field: dict[str, dict[str, Any]] = {}
    for field_id, analysis in sorted(analyses.items()):
        status = getattr(analysis.status, "value", str(analysis.status))
        row: dict[str, Any] = {"analysis_status": status,
                               "beta_hat": analysis.beta_hat}
        condition = conditions.get(field_id)
        if condition is not None:
            result = p1_geometry(analysis, contract,
                                 procedure_identity=binding.analysis_identity,
                                 condition=condition, artifact=artifacts.get(field_id))
            # THE FROZEN FAIL-CLOSED SEMANTIC: a non-ESTIMATED analysis does not
            # pass P1, so `not passed` is well defined for every field.
            block1, g5 = p1_block_decisions(result, artifacts.get(field_id), binding)
            row.update({"P1": bool(result.passed),
                        "p1_rejected": bool(not result.passed),
                        "block1_rejected": block1, "g5_rejected": g5})
        per_field[field_id] = row
    p1_values = [row["P1"] for row in per_field.values() if "P1" in row]
    p1_all = all(p1_values) if p1_values else None
    p2 = p2_cross_field(analyses, contract, unc)
    p3 = p3_absolute(analyses, contract, unc)
    p4 = p4_consistency(contract)
    outcome: dict[str, Any] = {
        "per_field": per_field,
        "P2": bool(p2.passed), "P3": bool(p3.passed), "P4": bool(p4.passed),
        "false_acceptance": bool(p2.passed and p3.passed),
        "complete_pass": (bool(p1_all and p2.passed and p3.passed and p4.passed)
                          if p1_all is not None else None),
        "scale_recovered": None,
    }
    scale_factors = next((s.scale_factors for s in specifications.values()
                          if s.scale_factors), ())
    if scale_factors:
        outcome.update(evaluate_scale_control(binding, case_id, contract, unc,
                                              analyses, blinded or {}, scale_factors))
    return outcome


#: Only this case may request the blinded Branch-A scale transform. Read from the
#: frozen plan: it is the sole case declaring `scale_factors` on a subcondition.
SCALE_CONTROL_CASE = "C8_blinded_scale_control"


def blinded_branch_a(field: BranchAField, factor: float) -> BranchAField:
    """THE frozen Branch-A scale transform. `e1a_v4.branch_a.BranchAField.blinded`.

    Not reimplemented here: the transform lives in the analysis-bound scientific
    layer, which states its own consequence --

        "Under the ideal null the analysis must then recover beta_hat = 1/c,
         because beta_hat = m / tr(H_A S) and H_A -> c H_A."

    -- and returns a NEW field, leaving the primary one unmutated. H is
    H_U * scale_factor / (k_B T), so multiplying the declared scale multiplies H,
    which is exactly the "duplicate Branch-A declaration" the frozen C8 design
    calls for.
    """
    return field.blinded(float(factor))


def evaluate_scale_control(binding: ExecutionBinding, case_id: str, contract,
                           unc: UncertaintyModel, analyses: Mapping[str, Any],
                           blinded: Mapping[float, Mapping[str, Any]],
                           scale_factors: Sequence[float]) -> dict[str, Any]:
    """C8: the BLINDED BRANCH-A CONTROL, then the frozen recovery rule.

    THE DEFECT THIS CLOSES
        The previous revision never built the blinded branch at all. It took the
        ordinary UNBLINDED estimate and multiplied it by c:

            beta_tilde = c * beta_hat_unblinded        # WRONG

        Under the true null beta_hat_unblinded ~ 1, so that evaluates to ~c --
        1.07 and 0.90 -- which lies outside delta_abs = 0.05 of 1 and can never
        pass P3. It reproduced neither the declared control nor its arithmetic.

        The frozen design duplicates the Branch-A DECLARATION and scales it:

            H_control = c * H        (same Branch-B observations, byte-identical)
            beta_hat_blind = m / tr(c H S) = beta_hat / c   ~ 1/c
            beta_tilde     = c * beta_hat_blind             ~ 1

        `blinded` carries the analyses of those scaled duplicates, produced by
        the frozen `analyse_field` against the SAME Branch-B record. The frozen
        `p3_absolute` then decides, at every tested field, for BOTH factors; a
        replicate succeeds only if both branches pass.
    """
    import dataclasses
    if case_id != SCALE_CONTROL_CASE:
        raise ScaleControlInvalid(
            f"{case_id} declared scale factors {list(scale_factors)}, but the "
            f"blinded Branch-A control is frozen to {SCALE_CONTROL_CASE!r} alone. "
            "A free scaling parameter on every Branch-A job is not a control.")
    missing = [factor for factor in scale_factors if factor not in blinded]
    if missing:
        raise ScaleControlInvalid(
            f"{case_id}: no blinded Branch-A analysis was supplied for c={missing}. "
            "The control is the scaled duplicate re-analysed against the same "
            "Branch-B observations; multiplying the unblinded estimate is not it.")
    branches: dict[str, Any] = {}
    recovered = True
    for factor in scale_factors:
        analyses_blind = blinded[factor]
        absent = sorted(set(analyses) - set(analyses_blind))
        if absent:
            raise ScaleControlInvalid(
                f"{case_id}: the c={factor} control is missing fields {absent}")
        # THE FROZEN RECOVERY RULE, verbatim from the case criterion:
        #     beta_tilde_theta = c * beta_hat_theta
        # applied to the BLINDED estimate, then judged by the frozen P3 rule.
        transformed = {
            field_id: (dataclasses.replace(a, beta_hat=float(factor) * a.beta_hat)
                       if a.beta_hat is not None else a)
            for field_id, a in analyses_blind.items()
        }
        result = p3_absolute(transformed, contract, unc)
        recovered = recovered and bool(result.passed)
        branches[repr(float(factor))] = {
            "c": float(factor),
            "beta_hat_blind": {f: a.beta_hat for f, a in sorted(analyses_blind.items())},
            "beta_tilde_recovered": {f: (None if a.beta_hat is None
                                         else float(factor) * a.beta_hat)
                                     for f, a in sorted(analyses_blind.items())},
            "blinded_field_ids": {f: a.field_id for f, a in sorted(analyses_blind.items())},
            "p3_passed": bool(result.passed),
        }
    return {
        "scale_recovered": bool(recovered),
        "scale_factors": [float(f) for f in scale_factors],
        "scale_control": {
            "transform": "e1a_v4.branch_a.BranchAField.blinded",
            "recovery_rule": "beta_tilde_theta = c * beta_hat_blind_theta",
            "branch_b_shared": True,
            "beta_hat_unblinded": {f: a.beta_hat for f, a in sorted(analyses.items())},
            "branches": branches,
        },
    }


# ------------------------------------------------- the execution orchestration
def replicate_groups(jobs: Sequence[CampaignJob]
                     ) -> list[tuple[tuple[str, str, int], tuple[CampaignJob, ...]]]:
    """Group planned jobs into replicates, preserving the frozen plan's order.

    A replicate is one synthetic EXPERIMENT: its fields share the Branch-A
    common mode and are evaluated by the cross-field endpoints together. Grouping
    is a pure function of the coordinates, so a permuted schedule yields the same
    groups with the same members.
    """
    groups: dict[tuple[str, str, int], list[CampaignJob]] = {}
    order: list[tuple[str, str, int]] = []
    for job in jobs:
        key = (job.coordinates.case_id, job.coordinates.subcondition_id,
               job.coordinates.replicate_id)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(job)
    return [(key, tuple(groups[key])) for key in order]


def execute_replicate(binding: ExecutionBinding, group: Sequence[CampaignJob],
                      provider: StochasticProvider, ledger: CampaignCalibrationLedger,
                      output_dir: str, *, resolver) -> dict[str, dict[str, Any]]:
    """Execute ONE replicate's frozen dependency graph. Calls, never reimplements.

        Branch-A measurement  e1a_v4.validation.generate.BranchAErrorModel.measure
        calibration artifact  e1a_v4.validation.calibrate.generate_block1_artifact
        Branch-B trajectory   e1a_v4.validation.generate.ou_observations
        Branch-B analysis     e1a_v4.geometry.analyse_field
        endpoints             e1a_v4.endpoints.p1..p4

    The driver supplies the ORDER, the provenance and the seeds, and no formula.
    Every seed comes from the replicate's own `ReplicateCalibration`, so Branch B
    is unreachable until Branch-A evidence is published and, where the case
    requires one, its calibration artifact is locked.
    """
    first = group[0]
    calibration = replicate_calibration_for(binding, first, ledger)
    # ONE common-mode draw per experiment, SHARED across the fields. Redrawing it
    # per field would destroy the cancellation P2 depends on.
    common_mode_seed = calibration.common_mode_seed()
    common_mode = provider.generator(common_mode_seed,
                                     "branch_a_common_mode").normal(1)[0]
    executions: dict[str, JobExecution] = {}
    specifications: dict[str, JobSpecification] = {}
    analyses: dict[str, Any] = {}
    conditions: dict[str, CalibrationCondition] = {}
    artifacts: dict[str, CalibrationArtifact] = {}
    measured_fields: dict[str, BranchAField] = {}
    blinded_analyses: dict[float, dict[str, Any]] = {}
    for job in group:
        field_id = job.coordinates.scope
        execution = job_execution(binding, job, ledger, output_dir, calibration)
        specification = resolver(binding, job)
        specifications[field_id] = specification
        branch_a_seed = calibration.branch_a_seed(field_id)
        branch_a_rng = provider.generator(branch_a_seed, "branch_a_measurement")
        measured = specification.error_model.measure(specification.field,
                                                     branch_a_rng, common_mode)
        execution.realise_branch_a(measured, branch_a_seed=branch_a_seed,
                                   common_mode_seed=common_mode_seed,
                                   generator_identity=BRANCH_A_GENERATOR_IDENTITY)
        # HASH, PUBLISH, COMMIT. Branch B is unreachable until this returns.
        execution.publish_branch_a()
        if job.requires_calibration:
            condition = execution.calibration_condition()
            conditions[field_id] = condition
            calibration_rng = provider.generator(execution.calibration_seed(),
                                                 "calibration")
            artifact = generate_block1_artifact(
                CalibrationRequest(
                    field_id=condition.field_id,
                    H_A=[list(row) for row in measured.H],
                    n=condition.n, phis=condition.phi_modes,
                    replicates=condition.replicates, alpha_1=condition.alpha_1,
                    theta_cap_deg=condition.theta_cap_deg,
                    procedure_identity=condition.procedure_identity,
                    contract_sha256=condition.contract_sha256,
                    plan_sha256=condition.plan_sha256,
                    dt=condition.dt, tau_modes=condition.tau_modes),
                calibration_rng)
            execution.lock_calibration(artifact)
            artifacts[field_id] = artifact
        # ---- ONLY NOW may Branch B be unblinded ------------------------------
        execution.unblind()
        branch_b_rng = provider.generator(execution.branch_b_seed(), "branch_b")
        truth = truth_from_field(specification.field, specification.dt,
                                 specification.n_samples, specification.beta_true)
        observations = ou_observations(truth, branch_b_rng)
        phi_modes = [math.exp(-specification.dt / tau) for tau in truth.tau_true]
        analyses[field_id] = analyse_field(
            measured, observations, rank_tol=specification.rank_tol,
            theta_cap_deg=specification.theta_cap_deg, phi_modes=phi_modes)
        # --- C8 ONLY: the blinded Branch-A control ---------------------------
        # A DUPLICATE Branch-A declaration scaled by c, re-analysed against the
        # SAME Branch-B observations object. Branch B is not regenerated, not
        # reseeded and not touched; only the Branch-A declaration differs. The
        # duplicates are built here, while the observations are live, so the
        # trajectory is never retained beyond its own replicate.
        for factor in specification.scale_factors:
            blinded_analyses.setdefault(float(factor), {})[field_id] = analyse_field(
                blinded_branch_a(measured, factor), observations,
                rank_tol=specification.rank_tol,
                theta_cap_deg=specification.theta_cap_deg, phi_modes=phi_modes)
        measured_fields[field_id] = measured
        executions[field_id] = execution
    replicate = evaluate_replicate(binding, first.coordinates.case_id,
                                   first.coordinates.subcondition_id,
                                   specifications, analyses, conditions, artifacts,
                                   blinded_analyses)
    outcomes: dict[str, dict[str, Any]] = {}
    for field_id, execution in executions.items():
        analysis = analyses[field_id]
        # The replicate-level endpoints, then THIS FIELD's own events. The
        # per-field block is merged last and deliberately: an audit found the
        # replicate-wide P1 disjunction being stamped on every field record and
        # then counted by C2, whose frozen rule is PER FIELD.
        outcome = {k: v for k, v in replicate.items() if k != "per_field"}
        outcome.update({
            "field_id": field_id,
            "G1": analysis.g1, "G2": analysis.g2_spread,
            "G3": list(analysis.g3) if analysis.g3 else None,
            "G4": analysis.g4, "G5": analysis.g5,
        })
        outcome.update(replicate["per_field"][field_id])
        require_endpoint_events(binding.plan, first.coordinates.case_id, outcome,
                                execution.job.job_id)
        execution.analyse(outcome)
        # STREAMING_PER_REPLICATE: the artifacts are finalised, locked and spent.
        execution.release_calibration()
        outcomes[execution.job.job_id] = {"execution": execution, "outcome": outcome}
    return outcomes


#: The per-case DIAGNOSTIC AGGREGATOR is the reporting layer's contribution, and
#: it is not part of the driver. Frozen authority states each mandatory
#: diagnostic's requirement in prose (`release_authority.mandatory_diagnostics`)
#: and states no machine-readable recipe for computing several of them -- C4's
#: operating-quantile discrepancy and C3's delta-method error among them. The
#: driver REQUIRES them, which is its job; computing them is not.
UNDECLARED_DIAGNOSTIC_AGGREGATOR = (
    "the per-case MANDATORY DIAGNOSTIC AGGREGATOR is not supplied. Frozen "
    "authority requires these diagnostics to be reported and states several of "
    "them only in prose, so the driver refuses rather than reporting an empty "
    "one. The aggregator is supplied by the authorised execution stage, and the "
    "diagnostics it must compute are declared in "
    "release_authority.mandatory_diagnostics."
)


def default_case_aggregate(binding: ExecutionBinding, case_id: str,
                           rows: Sequence[tuple["JobExecution", Mapping[str, Any]]]
                           ) -> dict[str, Any]:
    """The frozen aggregate SHAPE for a case, and a refusal where content is owed.

    A case that frozen authority requires no diagnostic for aggregates to the
    declared skeleton. A case that DOES owe one refuses here, by name, rather
    than further downstream with a shape error: an empty mandatory diagnostic is
    exactly the outcome the release-authority layer exists to prevent.
    """
    declared = mandatory_diagnostics_for(binding.plan, case_id)
    owed = [d for d in declared if d.required_keys]
    if owed:
        raise ContractMandatoryDiagnosticMissing(
            f"{case_id}: {UNDECLARED_DIAGNOSTIC_AGGREGATOR} Owed here: "
            f"{[d.diagnostic_id for d in owed]}.")
    return aggregate_skeleton(case_id)


def execute_campaign(binding: ExecutionBinding, jobs: Sequence[CampaignJob],
                     provider: StochasticProvider, output_dir: str, *,
                     resolver=resolve_job_specification,
                     aggregator=None,
                     ledger: CampaignCalibrationLedger | None = None,
                     realisations: Mapping[str, BranchARealisation] | None = None,
                     ) -> dict[str, Any]:
    """The campaign loop, BELOW the gate. Not an entry point and not authorised.

        reconcile restart state against the persisted inventory
              -> for each planned replicate: the frozen dependency graph
              -> per-case aggregate, built from that case's own records
              -> immutable terminal record per job, with its mandatory diagnostics
              -> campaign completeness: every frozen job, exactly once
              -> case aggregates from the IMMUTABLE planned job identities
              -> the frozen release classifier
              -> the final campaign result

    `run_campaign` is the only production caller and passes neither `resolver` nor
    `aggregator`: both exist so a deterministic fixture can exercise this control
    flow without a real generator. Neither can reach a real provider past a
    refused gate, because the gate runs ABOVE this function and this function is
    never reached when it refuses.
    """
    ledger = ledger if ledger is not None else CampaignCalibrationLedger()
    known = dict(realisations or {})
    # RECONCILE BOTH PERSISTED STORES BEFORE RESUMING. A restart never begins by
    # writing, and it never asks the caller what exists.
    restart = verify_restart(output_dir, known, binding, jobs)
    completed = inventory_job_records(output_dir, binding, jobs)
    orphan_results = sorted(set(completed) - set(known))
    if orphan_results:
        raise RestartInventoryMismatch(
            f"{len(orphan_results)} terminal record(s) exist for jobs with no "
            f"committed Branch-A publication (e.g. {orphan_results[:3]}); a result "
            "whose evidence is missing is not a completed job.")
    interrupted = sorted(set(known) - set(completed))
    if interrupted:
        raise RestartInventoryMismatch(
            f"{len(interrupted)} job(s) published Branch-A evidence and committed no "
            f"terminal record (e.g. {interrupted[:3]}). The run was interrupted "
            "between publication and recording. That Branch-A evidence is immutable "
            "and may not be republished, so the job can be neither re-run nor "
            "completed automatically: recovery is an authorised decision, not "
            "something a resume may take on its own.")
    by_case: dict[str, list[tuple[JobExecution, dict[str, Any]]]] = {}
    executed: list[str] = []
    for _key, group in replicate_groups(jobs):
        pending = [job for job in group if job.job_id not in completed]
        if not pending:
            continue                        # already published; never re-run
        if len(pending) != len(group):
            raise RestartInventoryMismatch(
                f"replicate {_key} is partially complete: {len(pending)} of "
                f"{len(group)} field jobs are outstanding. A replicate is one "
                "experiment and is resumed whole or not at all.")
        produced = execute_replicate(binding, group, provider, ledger, output_dir,
                                     resolver=resolver)
        for job_id, row in produced.items():
            by_case.setdefault(row["execution"].coordinates.case_id, []).append(
                (row["execution"], row["outcome"]))
            executed.append(job_id)
    records: dict[str, dict[str, Any]] = dict(completed)      # recovered from disk
    for case_id, rows in sorted(by_case.items()):
        aggregate = ((aggregator or default_case_aggregate)(binding, case_id, rows))
        for execution, _outcome in rows:
            record = execution.record(aggregate)
            # COMMIT THE RESULT DURABLY before it counts as a completed job.
            publish_job_record(output_dir, record, binding)
            records[execution.job.job_id] = record
    completeness = require_campaign_completeness(jobs, records)
    by_job_id = {job.job_id: job for job in jobs}
    for job_id, record in records.items():
        validate_job_record(record, binding.plan, binding,
                            job=by_job_id.get(job_id), output_dir=output_dir)
    aggregates = assemble_case_aggregates(jobs, records)
    # THE FROZEN RELEASE CLASSIFIER RUNS OVER THE COMPLETE CAMPAIGN OR NOT AT ALL.
    # Whether it runs is decided mechanically, by comparing the supplied job set
    # with the complete frozen plan -- not by a parameter a caller could set. A
    # subset run is self-evidently not a release decision, and classifying one
    # would produce a verdict whose denominators are "the jobs that were asked for".
    complete = {job.job_id for job in jobs} == {
        job.job_id for job in plan_campaign(binding.plan)}
    classification = None
    if complete:
        classification = classify_campaign(
            campaign_counts_from_records(binding.plan, records))
    return {
        "schema": CAMPAIGN_RESULT_SCHEMA,
        "restart": restart,
        "completeness": completeness,
        "case_aggregates": aggregates,
        "executed_jobs": executed,
        "complete_campaign": complete,
        "classification": classification,
        "records": records,
    }


# ----------------------------------------------------------- the execution gate
def require_execution_lifecycle(root: str, binding: ExecutionBinding,
                                output_dir: str) -> dict[str, Any]:
    """THE COMPLETE GATE. It runs BEFORE any stochastic provider object exists.

        1. the canonical campaign driver is present and declares its entry point
        2. the external execution seal is FROZEN
        3. the recomputed execution identity equals the independently sealed one
        4. execution_authorised is true in the frozen plan
        5. the campaign manifest is valid
        6. the output / restart state is valid

    The order is the plan's declared `execution_gate_order`: the most fundamental
    missing precondition first, so a refusal never reads as "just flip the
    authorisation flag".
    """
    require_canonical_driver(root)
    require_execution_gate(root, binding.plan, binding.execution_identity)
    manifest = campaign_manifest(binding, root)
    if manifest["execution_authorised"] is not True:
        raise ExecutionAuthorisationMissing(
            "the campaign manifest does not carry execution authorisation")
    inventory = require_clean_inventory(publication_directory(output_dir),
                                        "the Branch-A publication store")
    results = require_clean_inventory(job_record_directory(output_dir),
                                      "the terminal job-record store")
    locks = require_clean_inventory(calibration_lock_directory(output_dir),
                                    "the calibration-lock store")
    return {"manifest": manifest, "manifest_sha256": manifest_digest(manifest),
            "inventory": inventory.as_dict(), "job_records": results.as_dict(),
            "calibration_locks": locks.as_dict()}


# ------------------------------------------------------------- the entry point
def run_campaign(root: str = ".", *, output_dir: str | None = None,
                 plan_only: bool = False) -> dict[str, Any]:
    """THE official campaign entry point, declared in e1a_v4/validation/driver.py.

    `plan_only` performs the complete RNG-free planning phase and returns the
    manifest. The stochastic path passes the COMPLETE lifecycle gate first and
    constructs its provider only afterwards, so the first real generator cannot be
    requested before the gate has passed.

    There is deliberately no `force`, `skip_gate`, `ignore_seal`, `test_mode`,
    `rng_factory` or `provider` parameter. An earlier revision accepted an
    `rng_factory`: that was an injection point on the production entry point and
    it is removed. An escape hatch is exactly the thing this package exists not to
    have.
    """
    binding = bind_execution(root=root, output_dir=output_dir)
    jobs = plan_campaign(binding.plan)
    agreement = require_plan_driver_agreement(binding.plan, jobs)
    manifest = campaign_manifest(binding, root)
    if plan_only:
        return {"manifest": manifest, "manifest_sha256": manifest_digest(manifest),
                "agreement": agreement, "jobs": len(jobs),
                "rng_objects": 0, "random_draws": 0, "trajectories": 0}
    out = os.path.join(root, binding.output_dir)
    # --- THE GATE. Nothing stochastic exists yet, and nothing will if it refuses.
    lifecycle = require_execution_lifecycle(root, binding, out)
    # --- the AUTHORISED deterministic recovery: the campaign asks the disk what
    # it published, never its own memory and never the caller. The recovered set
    # then goes through the same strict reconciliation as any other checkpoint.
    recovered = recover_realisations(out, binding)
    # --- only past the gate does a provider get constructed --------------------
    provider = AuthorisedStochasticProvider(binding)
    result = execute_campaign(binding, jobs, provider, out, realisations=recovered)
    result["lifecycle"] = lifecycle
    result["recovered_publications"] = len(recovered)
    return result


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
    if not args.plan_only:
        print("EXECUTION NOT ATTEMPTED: pass --plan-only explicitly; the stochastic "
              "path refuses while the seal is unfrozen and execution is unauthorised")
    print("  RNG OBJECTS: 0   RANDOM DRAWS: 0   TRAJECTORIES: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
