"""Calibration SCOPE: which realised experiment a calibration artifact belongs to.

*** NOTHING HERE DRAWS A RANDOM NUMBER OR CONSTRUCTS A GENERATOR. ***

THE ADOPTED ARCHITECTURE IS REPLICATE-CONDITIONAL CALIBRATION.

    Every synthetic validation replicate that includes stochastic Branch-A
    measurement uncertainty is analysed using calibration artifacts generated for
    that replicate's OWN realised Branch-A calibration condition.

        H_true,theta  ->  H_A,theta,r  ->  C_theta,r  ->  Branch-B analysis

WHY, and it is not a performance argument. A synthetic replicate stands for one
repeated COMPLETE experiment, and Branch-A measurement is part of that experiment.
When Branch-A varies across replicates, H_A,r1 != H_A,r2 in general, and the P1
null depends on the realised Branch-A condition. Analysing both against one
nominal artifact because the field LABEL matches would validate a procedure nobody
proposes to run. The campaign validates Branch-A measurement, conditional
calibration, Branch-B measurement and endpoint analysis as ONE repeated pipeline.

    A matching field name is insufficient.
    A nominal H is insufficient.
    An eigenvalue ratio is insufficient.
    The complete repaired CalibrationCondition must match.

THE ORDERING THIS MODULE EXISTS TO ENFORCE. Conditional calibration must not become
outcome adaptation, so per replicate and field:

    1. derive the frozen seed identities          (no draw)
    2. generate the Branch-A measurement          branch_a_measurement family
    3. construct the complete CalibrationCondition
    4. generate and finalise the calibration artifact   calibration family
    5. LOCK it                                    immutable from here
    6. ONLY THEN release the Branch-B stream      validation family

`ReplicateCalibration.validation_seed` refuses before step 5, so the threshold is
conditional on Branch A and BLIND to Branch B. It cannot inspect Branch-B
observations, G1-G5 from validation data, beta_hat, P1/P2/P3 or the complete-pass
result, because none of them exists when it is built.

CLASSIFICATION
    scope resolution, ordering, reuse refusal ... EXACT (deterministic rules)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..calibration import CalibrationArtifact, CalibrationCondition
from ..numerics import Refusal
from .seeds import CaseSeedAccess, ValidationSeedFamily

#: Machine-readable plan keys. Never inferred from prose.
CALIBRATION_SCOPE_KEY = "calibration_scope"
BRANCH_A_STATUS_KEY = "branch_a_uncertainty_status"
SHARED_RATIONALE_KEY = "shared_calibration_rationale"

#: Branch-A status of a case.
BRANCH_A_STOCHASTIC = "STOCHASTIC_PER_REPLICATE"
BRANCH_A_FIXED = "FIXED"
BRANCH_A_STATUSES = (BRANCH_A_STOCHASTIC, BRANCH_A_FIXED)

#: Calibration scope of a case.
REPLICATE_CONDITIONAL = "REPLICATE_CONDITIONAL"
CASE_FIXED = "CASE_FIXED"
CALIBRATION_SCOPES = (REPLICATE_CONDITIONAL, CASE_FIXED)

#: The campaign-level value recorded in the frozen plan.
CAMPAIGN_CALIBRATION_SCOPE = REPLICATE_CONDITIONAL


@dataclass(frozen=True)
class CaseCalibrationScope:
    """One case's declared Branch-A status and calibration scope."""

    case_id: str
    branch_a_status: str
    scope: str
    shared_calibration_rationale: str = ""

    def __post_init__(self) -> None:
        if self.branch_a_status not in BRANCH_A_STATUSES:
            raise Refusal(
                f"case {self.case_id!r}: {BRANCH_A_STATUS_KEY} must be one of "
                f"{BRANCH_A_STATUSES}, got {self.branch_a_status!r}"
            )
        if self.scope not in CALIBRATION_SCOPES:
            raise Refusal(
                f"case {self.case_id!r}: {CALIBRATION_SCOPE_KEY} must be one of "
                f"{CALIBRATION_SCOPES}, got {self.scope!r}"
            )
        if self.branch_a_status == BRANCH_A_STOCHASTIC and self.scope != REPLICATE_CONDITIONAL:
            raise Refusal(
                f"case {self.case_id!r} realises Branch-A measurement per replicate, so its "
                f"calibration scope must be {REPLICATE_CONDITIONAL!r}, not {self.scope!r}. "
                "Reusing one nominal artifact across independently realised Branch-A "
                "conditions is prohibited: the null law moves with H_A."
            )
        if self.scope == CASE_FIXED and not self.shared_calibration_rationale:
            raise Refusal(
                f"case {self.case_id!r} declares {CASE_FIXED!r} but gives no "
                f"{SHARED_RATIONALE_KEY!r}. Shared calibration is part of a case DESIGN or it "
                "is not permitted; it is never an implicit cache."
            )

    @property
    def is_replicate_conditional(self) -> bool:
        return self.scope == REPLICATE_CONDITIONAL

    @classmethod
    def from_plan(cls, case_id: str, plan: Mapping[str, Any]) -> "CaseCalibrationScope":
        cases = {c["case_id"]: c for c in plan.get("cases", [])}
        if case_id not in cases:
            raise Refusal(f"unknown case {case_id!r}: the frozen plan declares {sorted(cases)}")
        case = cases[case_id]
        for key in (BRANCH_A_STATUS_KEY, CALIBRATION_SCOPE_KEY):
            if key not in case:
                raise Refusal(
                    f"case {case_id!r} does not declare {key!r}; calibration scope must be "
                    "machine-readable and explicit, never implicit"
                )
        return cls(case_id, case[BRANCH_A_STATUS_KEY], case[CALIBRATION_SCOPE_KEY],
                   case.get(SHARED_RATIONALE_KEY, ""))


@dataclass
class CampaignCalibrationLedger:
    """Campaign-wide registry of locked artifacts. Prevents SILENT reuse.

    A digest match is not permission. Under REPLICATE_CONDITIONAL an artifact
    belongs to exactly one (case, replicate, field); presenting it for another is
    refused even when the condition digest is byte-identical, because the reuse
    would have to be part of the case DESIGN to be legitimate.
    """

    owners: dict[str, tuple[str, int, str]] = field(default_factory=dict)
    digests: dict[tuple[str, int, str], str] = field(default_factory=dict)

    def register(self, scope: CaseCalibrationScope, replicate: int, field_id: str,
                 artifact: CalibrationArtifact) -> str:
        key = (scope.case_id, replicate, field_id)
        if key in self.digests:
            raise Refusal(
                f"calibration artifact for {key} is already locked and is immutable; "
                "a replicate may not be recalibrated"
            )
        digest = artifact.artifact_sha256
        owner = self.owners.get(digest)
        if owner is not None and owner != key and scope.is_replicate_conditional:
            raise Refusal(
                f"CALIBRATION_REUSE_REFUSED: artifact {digest[:16]}... is already locked to "
                f"{owner} and {scope.case_id!r} is {REPLICATE_CONDITIONAL}. An identical digest "
                "is not permission to share an artifact; shared calibration must be declared in "
                "the case design."
            )
        self.owners.setdefault(digest, key)
        self.digests[key] = digest
        return digest

    def digest_for(self, case_id: str, replicate: int, field_id: str) -> str | None:
        return self.digests.get((case_id, replicate, field_id))

    @property
    def artifact_count(self) -> int:
        return len(self.digests)


class ReplicateCalibration:
    """The per-replicate ordering boundary. Branch A, then LOCK, then Branch B.

    Seeds are DERIVED here, which constructs no generator and draws no number.
    """

    def __init__(self, scope: CaseCalibrationScope, access: CaseSeedAccess,
                 replicate: int, ledger: CampaignCalibrationLedger) -> None:
        if access.case_id != scope.case_id:
            raise Refusal(
                f"seed access is scoped to {access.case_id!r} but the calibration scope is "
                f"{scope.case_id!r}"
            )
        if replicate < 0:
            raise Refusal("replicate index must be nonnegative")
        self.scope = scope
        self.access = access
        self.replicate = replicate
        self.ledger = ledger
        self._locked: dict[str, CalibrationArtifact] = {}
        self._released: set[str] = set()

    # ---------------------------------------------------------------- step 1-2
    def branch_a_seed(self, field_id: str) -> int:
        """Branch-A measurement stream for this replicate and field."""
        return self.access.job(ValidationSeedFamily.BRANCH_A_MEASUREMENT,
                               self.replicate, field_id)

    # ------------------------------------------------------------------ step 4
    def calibration_seed(self, field_id: str) -> int:
        """Calibration stream for this replicate and field. Distinct from both
        the Branch-A and the Branch-B streams by domain separation."""
        if field_id in self._released:
            raise Refusal(
                f"ORDERING VIOLATION: Branch-B data for {field_id!r} has already been "
                "released; its calibration may not be regenerated"
            )
        return self.access.job(ValidationSeedFamily.CALIBRATION, self.replicate, field_id)

    # ------------------------------------------------------------------ step 5
    def lock(self, field_id: str, artifact: CalibrationArtifact,
             condition: CalibrationCondition | None = None) -> str:
        """Finalise and LOCK. Immutable afterwards; Branch B opens only after this."""
        if field_id in self._locked:
            raise Refusal(
                f"calibration for {field_id!r} replicate {self.replicate} is already locked; "
                "a locked artifact is immutable"
            )
        if field_id in self._released:
            raise Refusal(
                f"ORDERING VIOLATION: Branch-B data for {field_id!r} has already been "
                "released; no calibration may be locked afterwards"
            )
        if artifact.field_id != field_id:
            raise Refusal(
                f"artifact is for {artifact.field_id!r}, presented for {field_id!r}")
        if condition is not None and artifact.condition.sha256 != condition.sha256:
            raise Refusal(
                "artifact condition does not match the realised calibration condition")
        digest = self.ledger.register(self.scope, self.replicate, field_id, artifact)
        self._locked[field_id] = artifact
        return digest

    # ------------------------------------------------------------------ step 6
    def validation_seed(self, field_id: str) -> int:
        """Branch-B stream. REFUSES until the calibration for this field is locked."""
        if field_id not in self._locked:
            raise Refusal(
                f"ORDERING VIOLATION: Branch-B validation data for {field_id!r} replicate "
                f"{self.replicate} of {self.scope.case_id!r} was requested before its "
                "calibration artifact was locked. Conditional calibration must be blind to "
                "Branch B; the threshold is fixed first or it is not a threshold."
            )
        self._released.add(field_id)
        return self.access.job(ValidationSeedFamily.VALIDATION, self.replicate, field_id)

    def artifact(self, field_id: str) -> CalibrationArtifact:
        if field_id not in self._locked:
            raise Refusal(f"no locked calibration artifact for {field_id!r}")
        return self._locked[field_id]

    @property
    def locked_fields(self) -> tuple[str, ...]:
        return tuple(sorted(self._locked))

    @property
    def released_fields(self) -> tuple[str, ...]:
        return tuple(sorted(self._released))


def artifact_manifest_row(case_id: str, replicate: int, field_id: str,
                          artifact: CalibrationArtifact, calibration_seed: int) -> dict:
    """The frozen manifest row for one locked artifact. Recorded, never recomputed."""
    return {
        "case_id": case_id,
        "replicate_id": replicate,
        "field_id": field_id,
        "calibration_condition_sha256": artifact.condition.sha256,
        "artifact_sha256": artifact.artifact_sha256,
        "analysis_procedure_identity": artifact.procedure_identity,
        "contract_sha256": artifact.condition.contract_sha256,
        "calibrator_identity": artifact.condition.calibrator_identity,
        "R_cal": artifact.replicates,
        "alpha_1": artifact.alpha_1,
        "calibration_seed_identity": calibration_seed,
        "artifact_schema": artifact.schema,
    }
