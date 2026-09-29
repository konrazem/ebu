"""Validation-plan loading, execution binding and the execution identity.

FROZEN EXECUTION vs GENERAL IMPLEMENTATION — the distinction this module exists for:

    GENERAL IMPLEMENTATION        `e1a_v4.contract.load_contract` reads whatever
                                  valid contract it is given. That is correct
                                  architecture: no magic numbers in code.

    FROZEN VALIDATION EXECUTION   an OFFICIAL run must refuse to execute a
                                  contract other than the exact adopted one.
                                  `bind_execution` enforces that, and it refuses
                                  BEFORE any RNG can be created.

CLASSIFICATION
    plan / seed-map / execution identity ... EXACT (deterministic hashes)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any

from .. import DESIGN_CONTRACT
from ..contract import ContractBinding, load_contract, sha256_file
from ..identity import SCIENTIFIC_MODULES, procedure_identity
from ..numerics import Refusal
from . import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON, VALIDATION_IDENTITY
from .coherence import require_plan_authority_coherence
from .contract_plan import require_contract_plan_conformance
from .driver import driver_identity_component
from .refusals import (
    ContractIdentityMismatch, ExecutionIdentityMismatch, FrozenSourceMismatch,
    ImplementationHashMismatch, OutputCollision, PlanAnalysisIdentityMismatch,
    PlanStructureInvalid, SeedMapNotReproducible, UnexpectedExecutionStage,
)
from .seal import load_seal, require_seal_plan_agreement
from .strict_json import strict_load_file
from .scope import (
    BRANCH_A_STATUS_KEY, CALIBRATION_SCOPE_KEY, CAMPAIGN_CALIBRATION_SCOPE,
    REQUIRES_CALIBRATION_KEY, SUBCONDITION_ID_KEY, SUBCONDITIONS_KEY,
    CampaignCalibrationLedger, CaseCalibrationScope, ReplicateCalibration,
)
from .seeds import (
    ALLOWED_FAMILIES_KEY, CaseSeedAccess, FrozenSeedMap, ValidationSeedFamily,
)
from .classification import REQUIRED_C2_FIELDS, REQUIRED_C7_ALTERNATIVES

#: Validation modules whose content can change an execution. Sorted on use.
VALIDATION_MODULES = (
    "e1a_v4/validation/__init__.py",
    "e1a_v4/validation/calibrate.py",
    "e1a_v4/validation/classification.py",
    "e1a_v4/validation/coherence.py",
    "e1a_v4/validation/contract_plan.py",
    "e1a_v4/validation/dispositions.py",
    "e1a_v4/validation/driver.py",
    "e1a_v4/validation/generate.py",
    "e1a_v4/validation/plan.py",
    "e1a_v4/validation/refusals.py",
    "e1a_v4/validation/results.py",
    "e1a_v4/validation/runner.py",
    "e1a_v4/validation/scope.py",
    "e1a_v4/validation/seal.py",
    "e1a_v4/validation/seeds.py",
    "e1a_v4/validation/strict_json.py",
)

REQUIRED_PLAN_KEYS = (
    "plan_id", "plan_version", "frozen_identities", "cases", "generating_model",
    "calibration", "assurance", "failure_classifications", "output_schema",
    "controls", "no_post_outcome_tuning", "authority_gaps", "execution_command",
)


def require_output_schema_agreement(root: str, plan: dict[str, Any]) -> None:
    """Refuse a human/mechanical output-schema mismatch before any RNG exists."""
    path = os.path.join(root, PLAN_MARKDOWN)
    if not os.path.exists(path):
        raise Refusal("normative Markdown validation plan is absent")
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    section = text.split("## 9. Output schema", 1)
    if len(section) != 2:
        raise Refusal("normative Markdown output schema section is absent")
    body = section[1].split("\n## 10.", 1)[0]
    schema = plan["output_schema"]
    if (f"`{schema['record_schema']}`" not in body or
            f"`{schema['manifest_schema']}`" not in body):
        raise Refusal("Markdown/JSON output schema versions disagree")
    for label, key in (("Per record:", "per_record_fields"),
                       ("Aggregate:", "aggregate_fields")):
        line = next((line for line in body.splitlines() if line.startswith(label)), None)
        if line is None or re.findall(r"`([^`]+)`", line) != schema[key]:
            raise Refusal(f"Markdown/JSON output schema fields disagree at {label}")
    if "subcondition id + replicate index" not in body or "declared scope" not in body:
        raise Refusal("Markdown reproduction recipe omits subcondition or scope")


def load_plan(root: str = ".") -> dict[str, Any]:
    # STRICT: duplicate object keys at any depth refuse. `json.load` keeps the LAST
    # duplicate while a human reads the FIRST, so an ambiguous authority document
    # would parse cleanly and mislead every reader.
    plan = strict_load_file(os.path.join(root, PLAN_JSON), "the validation plan")
    for key in REQUIRED_PLAN_KEYS:
        if key not in plan:
            raise PlanStructureInvalid(
                f"validation plan missing required section {key!r}")
    if plan["plan_id"] != "e1a_v4_synthetic_validation":
        raise PlanStructureInvalid(f"unexpected plan_id {plan['plan_id']!r}")
    known = {f.value for f in ValidationSeedFamily}
    for case in plan["cases"]:
        cid = case.get("case_id", "<unnamed>")
        if ALLOWED_FAMILIES_KEY not in case:
            raise Refusal(
                f"case {cid!r} does not declare {ALLOWED_FAMILIES_KEY!r}. Seed "
                "permissions must be machine-readable, not prose."
            )
        declared = case[ALLOWED_FAMILIES_KEY]
        if not isinstance(declared, list) or not declared:
            raise Refusal(f"case {cid!r}: {ALLOWED_FAMILIES_KEY!r} must be a non-empty list")
        bad = [f for f in declared if f not in known]
        if bad:
            raise Refusal(f"case {cid!r} declares undeclared seed families {bad}")
        subs = case.get(SUBCONDITIONS_KEY)
        if not isinstance(subs, list) or not subs:
            raise Refusal(
                f"case {cid!r} declares no {SUBCONDITIONS_KEY!r}; every stochastic case must "
                "carry an explicit machine-readable subcondition list"
            )
        ids = [x.get(SUBCONDITION_ID_KEY) for x in subs]
        if any(not i for i in ids) or len(set(ids)) != len(ids):
            raise Refusal(f"case {cid!r} has missing or duplicated subcondition ids")
        if REQUIRES_CALIBRATION_KEY not in case:
            raise Refusal(f"case {cid!r} does not declare {REQUIRES_CALIBRATION_KEY!r}")
        if not case[REQUIRES_CALIBRATION_KEY] and "calibration" in declared:
            raise Refusal(
                f"case {cid!r} evaluates no P1 / Block-1 quantity but is granted the "
                "calibration seed family; unused families are not granted"
            )
        CaseCalibrationScope.from_plan(cid, plan)          # validates the pairing
    if plan.get("calibration", {}).get("calibration_scope") != CAMPAIGN_CALIBRATION_SCOPE:
        raise Refusal(
            "validation plan must declare calibration.calibration_scope = "
            f"{CAMPAIGN_CALIBRATION_SCOPE!r}; the adopted architecture is not implicit"
        )
    return plan


def load_seed_map(root: str = ".") -> dict[str, Any]:
    return strict_load_file(os.path.join(root, SEED_MAP_JSON), "the seed map")


def execution_identity(
    binding: ContractBinding,
    plan_sha256: str,
    seed_map_sha256: str,
    root: str = ".",
) -> str:
    """Binds the ANALYSIS identity plus the validation layer. Separate by design.

    The normative Markdown plan is part of the preimage. It is NORMATIVE authority,
    not commentary, so a stale Markdown must move the identity rather than sit
    outside the seal. The external execution seal is deliberately EXCLUDED: it
    asserts the expected value of this hash and so can never be one of its inputs.
    """
    code = {p: sha256_file(os.path.join(root, p)) for p in sorted(VALIDATION_MODULES)}
    payload = {
        "validation_identity": VALIDATION_IDENTITY,
        "analysis_procedure_identity": procedure_identity(binding, {}, root),
        "validation_code": code,
        "plan_sha256": plan_sha256,
        "plan_markdown_sha256": sha256_file(os.path.join(root, PLAN_MARKDOWN)),
        "seed_map_sha256": seed_map_sha256,
        # The CANONICAL campaign driver's own file hash, or the sentinel "ABSENT".
        # Always in the preimage, so the identity is defined at every lifecycle
        # stage AND moves the moment a real driver appears. That is precisely why
        # today's value is a PRE-DRIVER diagnostic and not a seal.
        "official_campaign_driver_sha256": driver_identity_component(root),
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ExecutionBinding:
    """Everything an official run must match. Built only by `bind_execution`."""

    binding: ContractBinding
    plan: dict[str, Any]
    seed_map: FrozenSeedMap
    plan_sha256: str
    seed_map_sha256: str
    analysis_identity: str
    execution_identity: str
    output_dir: str

    def calibration_scope(self, case_id: str) -> CaseCalibrationScope:
        """The case's declared Branch-A status and calibration scope."""
        return CaseCalibrationScope.from_plan(case_id, self.plan)

    def replicate_calibration(self, case_id: str, subcondition_id: str, replicate: int,
                              ledger: CampaignCalibrationLedger) -> ReplicateCalibration:
        """The per-replicate ordering boundary: Branch A, then LOCK, then Branch B.

        This is the ONLY route an official run may use to reach a validation
        stream, because it refuses one until that field's calibration is locked.
        """
        return ReplicateCalibration(self.calibration_scope(case_id),
                                    self.case_access(case_id), subcondition_id,
                                    replicate, ledger)

    def case_access(self, case_id: str) -> CaseSeedAccess:
        """The ONLY seed route an official run may use. Authorised by the plan.

        Deriving a seed is not a draw: this returns integers and constructs no
        generator. RNG construction remains a separate, separately reported step.
        """
        return CaseSeedAccess.from_plan(case_id, self.plan, self.seed_map)


def bind_execution(root: str = ".", output_dir: str | None = None) -> ExecutionBinding:
    """Full fail-closed preflight. Contains NO RNG and creates none.

    Every check below runs before the caller is permitted to obtain a generator.
    """
    binding = load_contract(root)
    plan = load_plan(root)
    # AUTHORITY COHERENCE FIRST. Neither representation may be trusted until the
    # two agree: a stale identity in either one misidentifies the whole package.
    require_output_schema_agreement(root, plan)
    require_plan_authority_coherence(root, plan)
    require_contract_plan_conformance(binding.data, plan)
    require_seal_plan_agreement(plan, load_seal(root))
    cases = {case["case_id"]: case for case in plan["cases"]}
    if (set(cases["C2_geometry_false_rejection"]["fields_affected"]) != REQUIRED_C2_FIELDS
            or {s["subcondition_id"] for s in cases["C7_false_bridge"]["subconditions"]}
            != REQUIRED_C7_ALTERNATIVES):
        raise Refusal("campaign classifier rows disagree with contract/plan declarations")
    if {f["id"] for f in binding.fields} != REQUIRED_C2_FIELDS:
        raise Refusal("campaign classifier fields disagree with the adopted contract")
    frozen = plan["frozen_identities"]

    # --- the frozen-execution rule: the EXACT adopted contract, nothing else ----
    actual_contract = sha256_file(os.path.join(root, DESIGN_CONTRACT))
    if actual_contract != frozen["contract_sha256"]:
        raise ContractIdentityMismatch(
            "FROZEN EXECUTION REFUSED: contract identity is "
            f"{actual_contract} but the validation plan is frozen against "
            f"{frozen['contract_sha256']}. A general analysis may read a modified "
            "contract; an OFFICIAL validation run may not."
        )
    for key, path in (("design_sha256", "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"),
                      ("foundation_sha256", "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md"),
                      ("baseline_sha256", "docs/theory/EBU_THEORY_BASELINE.md")):
        actual = sha256_file(os.path.join(root, path))
        if actual != frozen[key]:
            raise FrozenSourceMismatch(
                f"FROZEN EXECUTION REFUSED: {path} is {actual}, frozen {frozen[key]}")

    analysis = procedure_identity(binding, {}, root)
    if analysis != frozen["analysis_procedure_identity"]:
        raise PlanAnalysisIdentityMismatch(
            f"FROZEN EXECUTION REFUSED: analysis procedure identity is {analysis}, "
            f"frozen {frozen['analysis_procedure_identity']}"
        )
    for path in SCIENTIFIC_MODULES:
        actual = sha256_file(os.path.join(root, path))
        if actual != frozen["implementation_file_hashes"][path]:
            raise ImplementationHashMismatch(
                f"FROZEN EXECUTION REFUSED: {path} changed since the freeze")
    if frozen["implementation_work_commit"] != plan["frozen_identities"]["implementation_work_commit"]:
        raise PlanStructureInvalid(
            "plan is internally inconsistent about the implementation commit")

    plan_sha = sha256_file(os.path.join(root, PLAN_JSON))
    seed_sha = sha256_file(os.path.join(root, SEED_MAP_JSON))
    raw_map = load_seed_map(root)
    derived = FrozenSeedMap.derive(actual_contract, raw_map["campaign"])
    if derived.as_json()["families"] != raw_map["families"] or derived.master != raw_map["master_seed"]:
        raise SeedMapNotReproducible(
            "FROZEN EXECUTION REFUSED: the committed seed map does not reproduce from its "
            "own declared derivation. Seeds must be mechanical, never hand-edited."
        )
    exec_id = execution_identity(binding, plan_sha, seed_sha, root)

    # --- the final expected execution identity: NOT-YET-FROZEN vs FORGOTTEN -----
    # The slot must exist. An ABSENT key is forgotten and refuses; only an explicit
    # null means "deliberately not yet frozen", which is correct while the official
    # campaign driver does not exist. The authoritative expectation, once frozen,
    # lives in the EXTERNAL seal, because the plan itself is inside the preimage.
    if "final_expected_execution_identity" not in frozen:
        raise PlanStructureInvalid(
            "FROZEN EXECUTION REFUSED: the plan omits the "
            "final_expected_execution_identity slot. An absent slot is "
            "indistinguishable from a forgotten freeze; declare it explicitly as "
            "null while the official campaign driver is absent."
        )
    expected = frozen["final_expected_execution_identity"]
    if expected is not None:
        if not (isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected)):
            raise PlanStructureInvalid(
                "FROZEN EXECUTION REFUSED: final_expected_execution_identity must be "
                f"null or a 64-character lowercase hex digest; found {expected!r}"
            )
        if exec_id != expected:
            raise ExecutionIdentityMismatch(
                f"FROZEN EXECUTION REFUSED: execution identity is {exec_id}, "
                f"frozen {expected}"
            )

    out = output_dir or plan["output_schema"]["directory"]
    out_abs = os.path.join(root, out)
    if os.path.exists(out_abs) and os.listdir(out_abs):
        raise OutputCollision(
            f"FROZEN EXECUTION REFUSED: output collision, {out} already contains results. "
            "A failed or superseded campaign is preserved, never overwritten."
        )
    if plan["execution_stage"] != "synthetic_validation":
        raise UnexpectedExecutionStage(
            f"unexpected execution stage {plan['execution_stage']!r}")

    return ExecutionBinding(binding, plan, derived, plan_sha, seed_sha, analysis, exec_id, out)
