"""Stable, machine-checkable refusal codes for the validation layer.

WHY CODES
    A regression test that asserts only "a Refusal was raised" cannot tell a
    refusal for the RIGHT reason from a refusal for an incidental one. That is not
    hypothetical here: when the coherence and seal checks were added earlier in
    `bind_execution`, eight existing preflight fixtures began refusing before they
    reached the path each was written to exercise, and every one of them still
    reported PASS. Codes make the intended reason assertable.

WHY NOT IN `e1a_v4.numerics`
    `Refusal` lives in `e1a_v4/numerics.py`, which is one of the twelve SCIENTIFIC
    MODULES bound by the analysis procedure identity. Adding codes there would move
    that identity for a purely operational reason. This module sits in the
    VALIDATION layer instead, so the analysis identity is untouched.

WHAT A CODE IS AND IS NOT
    A code is a stable testing and auditing handle, not user-interface wording.
    Messages stay free to improve; codes do not change without a recorded reason.

CLASSIFICATION
    every refusal here ... EXACT (deterministic classification of a failed check)

NO RNG. Nothing in this module draws or advances any model state.
"""

from __future__ import annotations

from ..numerics import Refusal


class CodedRefusal(Refusal):
    """A refusal carrying a stable machine-checkable code."""

    code = "UNCLASSIFIED_REFUSAL"

    def __init__(self, message: str) -> None:
        super().__init__(f"[{type(self).code}] {message}")
        self.message = message


# ---------------------------------------------------------- authority coherence
class PlanVersionMismatch(CodedRefusal):
    code = "PLAN_VERSION_MISMATCH"


class PlanAnalysisIdentityMismatch(CodedRefusal):
    code = "PLAN_ANALYSIS_IDENTITY_MISMATCH"


class PlanIdentityMismatch(CodedRefusal):
    """A frozen identity other than the analysis identity disagrees."""

    code = "PLAN_IDENTITY_MISMATCH"


class PlanCaseMismatch(CodedRefusal):
    code = "PLAN_CASE_MISMATCH"


class PlanSubconditionMismatch(CodedRefusal):
    code = "PLAN_SUBCONDITION_MISMATCH"


class PlanReleaseRuleMismatch(CodedRefusal):
    code = "PLAN_RELEASE_RULE_MISMATCH"


class PlanAdoptedRuleMismatch(CodedRefusal):
    """A frozen scientific decision rule is rendered differently in the Markdown."""

    code = "PLAN_ADOPTED_RULE_MISMATCH"


class PlanSurfaceMismatch(CodedRefusal):
    """A declared normative field disagrees and has no more specific code."""

    code = "PLAN_SURFACE_MISMATCH"


class PlanGeneratingModelMismatch(CodedRefusal):
    """Markdown section 4 and the JSON generating model disagree, or the plan's
    restatement contradicts the frozen design contract."""

    code = "PLAN_GENERATING_MODEL_MISMATCH"


class ContractFieldSetMismatch(CodedRefusal):
    code = "CONTRACT_FIELD_SET_MISMATCH"


class ContractFieldDuplicate(CodedRefusal):
    code = "CONTRACT_FIELD_DUPLICATE"


class ContractReferenceFieldMismatch(CodedRefusal):
    code = "CONTRACT_REFERENCE_FIELD_MISMATCH"


class ContractGeneratingParameterMismatch(CodedRefusal):
    code = "CONTRACT_GENERATING_PARAMETER_MISMATCH"


class ContractRelaxationRuleMismatch(CodedRefusal):
    code = "CONTRACT_RELAXATION_RULE_MISMATCH"


class ContractTrueBridgeBetaMismatch(CodedRefusal):
    code = "CONTRACT_TRUE_BRIDGE_BETA_MISMATCH"


class ContractBindingUnclassified(CodedRefusal):
    code = "CONTRACT_BINDING_UNCLASSIFIED"


# ------------------------------------- Branch-A provenance and publication
class BranchAProvenanceMismatch(CodedRefusal):
    """Branch-A evidence does not belong to the coordinates it is presented for."""

    code = "BRANCH_A_PROVENANCE_MISMATCH"


class BranchAEvidenceAltered(CodedRefusal):
    """Published Branch-A evidence does not reproduce its own recorded digest."""

    code = "BRANCH_A_EVIDENCE_ALTERED"


class BranchANotPublished(CodedRefusal):
    """Branch-A evidence has not been hashed and published yet."""

    code = "BRANCH_A_NOT_PUBLISHED"


class BranchAPublicationImmutable(CodedRefusal):
    """Published Branch-A evidence may not be replaced, edited or rebound."""

    code = "BRANCH_A_PUBLICATION_IMMUTABLE"


class PublicationCollision(CodedRefusal):
    """A final published path already exists; publication never overwrites."""

    code = "PUBLICATION_COLLISION"


class PublicationIncomplete(CodedRefusal):
    """A published record is truncated, appended to, or otherwise not whole."""

    code = "PUBLICATION_INCOMPLETE"


class PublicationNotDurable(CodedRefusal):
    """The publication primitive could not guarantee atomic durable creation."""

    code = "PUBLICATION_NOT_DURABLE"


class PublicationOrphaned(CodedRefusal):
    """Evidence was PREPARED at its final path but never COMMITTED.

    The artifact bytes exist and its commit marker does not. That is the exact
    state an interrupted publication leaves behind, and it is the one state a
    reader must never round up to PUBLISHED. It is preserved, not deleted: the
    orphan is the only surviving record of what was attempted.
    """

    code = "PUBLICATION_ORPHANED"


class PublicationUnexpectedEntry(CodedRefusal):
    """A publication directory contains something the protocol did not put there."""

    code = "PUBLICATION_UNEXPECTED_ENTRY"


class PublicationDigestMismatch(CodedRefusal):
    """A published record does not reproduce its own publication digest.

    Distinct from BRANCH_A_EVIDENCE_ALTERED: that one means the scientific
    evidence moved, this one means any bound provenance field did -- execution
    identity, calibration-condition hash, coordinates, seed identity, state or
    schema. The envelope is authenticated as a whole, not evidence-first.
    """

    code = "PUBLICATION_DIGEST_MISMATCH"


class RestartInventoryMismatch(CodedRefusal):
    """What the campaign claims exists and what actually exists disagree.

    Raised in BOTH directions. A caller cannot hide an artifact by omitting it
    from an argument, and cannot conjure one by naming it.
    """

    code = "RESTART_INVENTORY_MISMATCH"


class ResultCaseMismatch(CodedRefusal):
    """A result was presented for a job whose frozen case it does not belong to."""

    code = "RESULT_CASE_MISMATCH"


class ResultFieldSetMismatch(CodedRefusal):
    """The per-field rows are not exactly the frozen job's declared field set."""

    code = "RESULT_FIELD_SET_MISMATCH"


class CampaignIncomplete(CodedRefusal):
    """Aggregation was attempted before every frozen job had one terminal record."""

    code = "CAMPAIGN_INCOMPLETE"


class StochasticProviderRefused(CodedRefusal):
    """A real stochastic provider was requested outside an authorised execution."""

    code = "STOCHASTIC_PROVIDER_REFUSED"


class EndpointEventMissing(CodedRefusal):
    """A frozen endpoint decision the case requires is absent from a record.

    A missing decision is NOT a pass and NOT a zero-rejection. An independent
    audit found `g5_rejected` and `block1_rejected` written as null and then
    counted as zero, so every observation of those endpoints was discarded while
    the campaign reported a clean size. Absence now refuses.
    """

    code = "ENDPOINT_EVENT_MISSING"


class EndpointEventReductionUndeclared(CodedRefusal):
    """Frozen authority does not declare how per-field events become one
    replicate-level event for this case, so the driver refuses to choose."""

    code = "ENDPOINT_EVENT_REDUCTION_UNDECLARED"


class ScaleControlInvalid(CodedRefusal):
    """The blinded Branch-A scale control was requested or built incorrectly."""

    code = "SCALE_CONTROL_INVALID"


class TerminalProvenanceMismatch(CodedRefusal):
    """A terminal record's provenance links disagree with the CURRENT authority.

    An internally self-consistent digest proves only that the record's bytes were
    not edited after it was written. It cannot prove the bytes describe this
    campaign: an audit re-digested a record after changing its execution
    identity, its Branch-A evidence hash and its publication digest, and
    validation still accepted it. The links are now cross-checked against the
    execution binding, the frozen planner and the committed publication.
    """

    code = "TERMINAL_PROVENANCE_MISMATCH"


class CalibrationArtifactBindingInvalid(CodedRefusal):
    """A terminal record's calibration artifact identity is not the LOCKED one.

    `calibration_artifact_sha256` is the only link between a completed job and
    the artifact that actually set its Block-1 threshold, and until this check
    existed the field had no external referent at all: nothing on disk recorded
    the lock, so the record was the sole witness to its own calibration. An audit
    set the field to null and to a fabricated digest, re-digested the record, and
    both were accepted -- on the write path and on restart alike.

    The identity is now cross-checked against the COMMITTED calibration-lock
    record published for these exact coordinates at lock time. A digest the
    record supplies about itself is not evidence; the locked artifact is.
    """

    code = "CALIBRATION_ARTIFACT_BINDING_INVALID"


class BranchAMeasurementInvalid(BranchAProvenanceMismatch):
    """A persisted Branch-A record the production constructor could never produce.

    Every field can be individually well-formed and externally authorised, the
    record can be correctly re-digested and durably committed, and the
    COMBINATION can still be impossible: an H_A that does not follow from the
    recorded stiffnesses, orientation, temperature and scale; relaxation times no
    single drag coefficient could yield; a negative temperature; a negative scale
    factor.

    A digest authenticates the bytes. It does not prove the bytes form a valid
    measurement. Deliberately a subclass of `BranchAProvenanceMismatch`, so every
    existing handler still catches it while the diagnosis stays distinguishable:
    "wrong authority value" and "impossible measurement" are different faults.
    """

    code = "BRANCH_A_MEASUREMENT_INVALID"


class CalibrationLockMissing(CalibrationArtifactBindingInvalid):
    """A calibration-requiring job has no committed lock in the canonical store."""

    code = "CALIBRATION_LOCK_MISSING"


class CalibrationLockJobMismatch(CalibrationArtifactBindingInvalid):
    """The store slot, the lock record's own identity and the planned job disagree.

    A lock is not valid because it names SOME valid planned job. If it occupies
    the canonical slot for job A and internally names job B, the two identities
    that must agree do not, and one of them is wrong.
    """

    code = "CALIBRATION_LOCK_JOB_MISMATCH"


class CalibrationLockFieldMismatch(CalibrationArtifactBindingInvalid):
    """The locked artifact's field is not the job's field/scope."""

    code = "CALIBRATION_LOCK_FIELD_MISMATCH"


class CalibrationLockUnplanned(CalibrationArtifactBindingInvalid):
    """A committed lock exists for coordinates the frozen plan never declared, or
    for a case that evaluates no P1 / Block-1 quantity."""

    code = "CALIBRATION_LOCK_UNPLANNED"


class CalibrationLockWithoutPublication(CalibrationArtifactBindingInvalid):
    """A committed lock exists with no committed Branch-A publication upstream.

    A threshold conditional on evidence that is not there is not a conditional
    threshold.
    """

    code = "CALIBRATION_LOCK_WITHOUT_PUBLICATION"


class CalibrationLockProvenanceMismatch(CalibrationArtifactBindingInvalid):
    """A committed lock's schema, digest, condition, evidence links or package
    identities disagree with the authority that must corroborate them."""

    code = "CALIBRATION_LOCK_PROVENANCE_MISMATCH"


class BranchBPremature(CodedRefusal):
    """Branch-B access was requested before its frozen prerequisites held."""

    code = "BRANCH_B_PREMATURE"


class JobStateInvalid(CodedRefusal):
    """An execution-state transition the frozen dependency graph does not allow."""

    code = "JOB_STATE_INVALID"


class CampaignPlanMismatch(CodedRefusal):
    """The driver-generated job plan disagrees with the frozen machine plan."""

    code = "CAMPAIGN_PLAN_MISMATCH"


class CampaignManifestInvalid(CodedRefusal):
    """The pre-execution campaign manifest is incomplete or inconsistent."""

    code = "CAMPAIGN_MANIFEST_INVALID"


# ------------------------------------------------- frozen RELEASE authority
class ContractReleaseReplicateCountMismatch(CodedRefusal):
    """The plan declares a replicate count the frozen authority does not."""

    code = "CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH"


class ContractReleaseTargetMismatch(CodedRefusal):
    """A target probability/rate disagrees with frozen release authority."""

    code = "CONTRACT_RELEASE_TARGET_MISMATCH"


class ContractReleaseConfidenceRuleMismatch(CodedRefusal):
    """Confidence level, sidedness or interval method disagrees."""

    code = "CONTRACT_RELEASE_CONFIDENCE_RULE_MISMATCH"


class ContractReleaseBoundDirectionMismatch(CodedRefusal):
    """A lower/upper bound direction disagrees with frozen authority."""

    code = "CONTRACT_RELEASE_BOUND_DIRECTION_MISMATCH"


class ContractReleaseDerivedThresholdMismatch(CodedRefusal):
    """A stored integer threshold is not the one its frozen inputs derive."""

    code = "CONTRACT_RELEASE_DERIVED_THRESHOLD_MISMATCH"


class ContractReleaseEndpointMismatch(CodedRefusal):
    """The declared release endpoint or its semantics disagree."""

    code = "CONTRACT_RELEASE_ENDPOINT_MISMATCH"


class ContractReleaseBindingUnclassified(CodedRefusal):
    """A release-relevant frozen authority leaf carries no classification."""

    code = "CONTRACT_RELEASE_BINDING_UNCLASSIFIED"


class ContractReleaseImplicationBroken(CodedRefusal):
    """An IMPLIED_STRONGER relationship no longer holds over its frozen range."""

    code = "CONTRACT_RELEASE_IMPLICATION_BROKEN"


class ContractMandatoryDiagnosticMissing(CodedRefusal):
    """Frozen authority requires a diagnostic the result does not carry."""

    code = "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING"


class ContractMandatoryDiagnosticMismatch(CodedRefusal):
    """A mandatory diagnostic is present but inconsistent with its raw counts."""

    code = "CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH"


class ResultSchemaInvalid(CodedRefusal):
    """A completed campaign result is not structurally valid."""

    code = "RESULT_SCHEMA_INVALID"


class PlanDerivedValueMismatch(CodedRefusal):
    """A value the Markdown displays as derived does not equal its recomputation
    from the JSON primitives it is derived from."""

    code = "PLAN_DERIVED_VALUE_MISMATCH"


class PlanSectionUnregistered(CodedRefusal):
    """The Markdown carries a section the normative-section registry does not
    classify, so its normative status was never decided."""

    code = "PLAN_SECTION_UNREGISTERED"


class PlanSurfaceUndeclared(CodedRefusal):
    """The plan carries authority the coherence specification does not classify."""

    code = "PLAN_SURFACE_UNDECLARED"


class PlanDuplicateKey(CodedRefusal):
    code = "PLAN_DUPLICATE_KEY"


class PlanAmbiguousBlock(CodedRefusal):
    """A generated authority region is absent, duplicated or malformed."""

    code = "PLAN_AMBIGUOUS_BLOCK"


class PlanStructureInvalid(CodedRefusal):
    """The plan is structurally unusable: missing sections, bad types, bad ids."""

    code = "PLAN_STRUCTURE_INVALID"


# ------------------------------------------------------------ frozen identities
class ContractIdentityMismatch(CodedRefusal):
    code = "CONTRACT_IDENTITY_MISMATCH"


class FrozenSourceMismatch(CodedRefusal):
    """Prospective design, frozen foundation or working baseline moved."""

    code = "FROZEN_SOURCE_MISMATCH"


class ImplementationHashMismatch(CodedRefusal):
    code = "IMPLEMENTATION_HASH_MISMATCH"


class SeedMapNotReproducible(CodedRefusal):
    """The committed seed map does not rederive from its declared algorithm.

    Covers BOTH an edited seed family and an edited master seed: the derivation is
    a single mechanical function of the contract identity, so either edit fails the
    same reproduction check. The fixtures for both assert this code.
    """

    code = "SEED_MAP_NOT_REPRODUCIBLE"


class UnexpectedExecutionStage(CodedRefusal):
    code = "UNEXPECTED_EXECUTION_STAGE"


class OutputCollision(CodedRefusal):
    code = "OUTPUT_COLLISION"


class ExecutionIdentityMismatch(CodedRefusal):
    """The recomputed execution identity differs from a frozen expectation.

    Raised for BOTH the plan's `final_expected_execution_identity` slot and the
    external seal: they are the same question asked of two authorities.
    """

    code = "EXECUTION_IDENTITY_MISMATCH"


# ------------------------------------------------------------ the execution gate
class ExecutionNotAuthorised(CodedRefusal):
    """UMBRELLA: this run is NOT cleared to execute.

    The subclasses name WHICH precondition is missing, so a refusal can never be
    read as "just flip the authorisation flag". Every one of them is raised before
    any RNG object can exist. `except ExecutionNotAuthorised` catches them all.
    """

    code = "EXECUTION_GATE_REFUSED"


class DriverAbsent(ExecutionNotAuthorised):
    """The CANONICAL official campaign driver does not exist."""

    code = "DRIVER_ABSENT"


#: Historical name for the same condition, kept so existing callers still work.
CampaignDriverAbsent = DriverAbsent


class DriverIdentityMismatch(ExecutionNotAuthorised):
    """A seal contradicts the canonical driver declaration, or the driver on disk
    does not satisfy the declared interface."""

    code = "DRIVER_IDENTITY_MISMATCH"


class ExecutionSealMalformed(ExecutionNotAuthorised):
    code = "EXECUTION_SEAL_MALFORMED"


class ExecutionSealStateDisagreement(ExecutionNotAuthorised):
    code = "EXECUTION_SEAL_STATE_DISAGREEMENT"


class ExecutionSealNotFrozen(ExecutionNotAuthorised):
    code = "EXECUTION_SEAL_NOT_FROZEN"


class ExecutionIdentityUnsealed(ExecutionIdentityMismatch, ExecutionNotAuthorised):
    """The seal's expected identity does not match the recomputation.

    Deliberately both: it IS an execution-identity mismatch, and it IS a reason the
    run is not cleared to execute, so either `except` clause catches it.
    """

    code = "EXECUTION_IDENTITY_MISMATCH"


class ExecutionAuthorisationMissing(ExecutionNotAuthorised):
    """Driver, seal and identity are in order, but authorisation was not granted."""

    code = "EXECUTION_NOT_AUTHORISED"


#: Every refusal class this layer can emit. A test asserts the mapping is complete.
ALL_REFUSAL_CLASSES = (
    BranchAProvenanceMismatch, BranchAEvidenceAltered, BranchANotPublished,
    BranchAPublicationImmutable, BranchBPremature, JobStateInvalid,
    PublicationCollision, PublicationIncomplete, PublicationNotDurable,
    PublicationOrphaned, PublicationUnexpectedEntry, PublicationDigestMismatch,
    RestartInventoryMismatch, ResultCaseMismatch, ResultFieldSetMismatch,
    ResultSchemaInvalid, CampaignIncomplete, CampaignPlanMismatch,
    CampaignManifestInvalid, StochasticProviderRefused,
    EndpointEventMissing, EndpointEventReductionUndeclared,
    ScaleControlInvalid, TerminalProvenanceMismatch,
    BranchAMeasurementInvalid,
    CalibrationArtifactBindingInvalid, CalibrationLockMissing,
    CalibrationLockJobMismatch, CalibrationLockFieldMismatch,
    CalibrationLockUnplanned, CalibrationLockWithoutPublication,
    CalibrationLockProvenanceMismatch,
    ContractMandatoryDiagnosticMissing, ContractMandatoryDiagnosticMismatch,
    PlanVersionMismatch, PlanAnalysisIdentityMismatch, PlanIdentityMismatch,
    PlanCaseMismatch, PlanSubconditionMismatch, PlanReleaseRuleMismatch,
    PlanAdoptedRuleMismatch, PlanSurfaceMismatch, PlanSurfaceUndeclared,
    PlanDuplicateKey, PlanAmbiguousBlock, PlanStructureInvalid,
    PlanGeneratingModelMismatch, PlanDerivedValueMismatch, PlanSectionUnregistered,
    ContractIdentityMismatch, FrozenSourceMismatch, ImplementationHashMismatch,
    SeedMapNotReproducible, UnexpectedExecutionStage, OutputCollision,
    ExecutionIdentityMismatch, ExecutionNotAuthorised, DriverAbsent,
    DriverIdentityMismatch, ExecutionSealMalformed, ExecutionSealStateDisagreement,
    ExecutionSealNotFrozen, ExecutionIdentityUnsealed, ExecutionAuthorisationMissing,
)

#: `ExecutionIdentityUnsealed` deliberately shares EXECUTION_IDENTITY_MISMATCH with
#: `ExecutionIdentityMismatch`: one condition, two raise sites, one stable code.
REFUSAL_CODES = tuple(sorted({c.code for c in ALL_REFUSAL_CLASSES}))
