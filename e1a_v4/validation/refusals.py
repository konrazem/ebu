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
