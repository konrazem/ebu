"""E1a v4 TERMINAL RECORDS BOUND TO THE ACTUAL LOCKED CALIBRATION ARTIFACT.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Deterministic matrices,
arithmetic calibration fixtures and filesystem publication only.

    REAL RNG OBJECTS ................ 0
    REAL STOCHASTIC RANDOM DRAWS .... 0
    OFFICIAL CAMPAIGN TRAJECTORIES .. 0
    DETERMINISTIC TEST TRAJECTORIES . 0   this suite generates none. No
                                          observation array is produced at all;
                                          `ou_observations` is never called and
                                          no world state advances.
    OFFICIAL CAMPAIGN JOBS .......... 0
    REAL CALIBRATION EXECUTIONS ..... 0   every null draw below is written out by
                                          hand, so no calibration is executed.

WHAT THIS SUITE PROVES

    An independent audit cleared the driver's endpoint mapping, its C8 control and
    its Branch-A publication linkage, and left one blocker standing:

        a terminal record for a calibration-requiring job could carry
        `calibration_artifact_sha256 = null`, or a fabricated valid-looking
        digest, recompute its own terminal digest, and still validate.

    The root cause was not a missing comparison. It was a missing referent. The
    adopted STREAMING_PER_REPLICATE implementation finalises, locks and SPENDS
    each calibration artifact, so nothing on disk recorded the lock: the terminal
    record was the only witness to its own calibration, and a record cannot
    corroborate itself. The lock is now durably COMMITTED when it happens --
    before Branch B is unblinded -- and the terminal record is checked against it
    on the write path and on restart alike.

    For a Block-1 case the calibration artifact IS the threshold its P1 decision
    was taken against, so an unverifiable artifact identity is an unverifiable
    scientific result, not a bookkeeping defect.
"""

from __future__ import annotations

import inspect
import json
import math
import os
import shutil
import tempfile
from fractions import Fraction

from e1a_v4.branch_a import BranchAField, build_field, stiffness_matrix
from e1a_v4.calibration import CalibrationArtifact, canonical_float
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.campaign_driver import (
    CALIBRATION_LOCK_KEYS, CALIBRATION_LOCK_SCHEMA, JobCoordinates,
    calibration_lock_basename, calibration_lock_directory,
    _compare_terminal_to_verified_lock, calibration_lock_basename,
    calibration_lock_directory, calibration_lock_envelope,
    AUTHORITY_CLASSES, AUTHORITY_CLASSES_WITH_EXPECTED_VALUE,
    AUTHORITY_DERIVED, AUTHORITY_MEASURED, AUTHORITY_OPEN_UNRESOLVED,
    BRANCH_A_FIELD_AUTHORITY, BRANCH_A_MEASUREMENT_INVARIANTS,
    single_gamma_feasible, _rounding_interval, _VIRTUAL_BINADE,
    require_branch_a_measurement_invariants, interval_contains_binary64,
    _smallest_binary64_at_least, _MAX_FINITE, _rounding_cell,
    _significand_is_even, binary64_in_interval, _VIRTUAL_BINADE as VIRTUAL,
    BRANCH_A_FIELD_AUTHORITY_BY_FIELD, EMBEDDED_EVIDENCE_CLASSIFICATION,
    EMBEDDED_PACKAGE_IDENTITY_FIELDS, EMBEDDED_TO_OUTER_IDENTITY,
    EXTERNALLY_BOUND_EMBEDDED_FIELDS, authority_class_counts, CampaignJob,
    canonical_plan,
    committed_calibration_lock, committed_publication,
    embedded_authority_expectations, inventory_calibration_locks,
    inventory_job_records, is_sha256, job_execution, plan_campaign,
    publication_basename, publication_directory,
    publish_calibration_lock, publish_job_record, reconcile_calibration_locks,
    realisation_from_record, recover_realisations, validate_job_record,
    verified_calibration_lock, verified_publication,
    verify_restart,
)
from e1a_v4.validation.classification import GROSS_INFLATION_TOLERANCE
from e1a_v4.validation.dispositions import cp_upper
from e1a_v4.validation.plan import bind_execution
from e1a_v4.validation.publication import (
    canonical_digest, commit_name, publish_transaction, read_published,
    sealed_digest,
)
from e1a_v4.validation.results import aggregate_skeleton
from e1a_v4.validation.scope import CampaignCalibrationLedger
from e1a_v4.validation.seeds import EXPERIMENT_SCOPE, ValidationSeedFamily
from e1a_v4.validation.seal import SEAL_JSON

ROOT = os.path.dirname(os.path.abspath(__file__))
PASSED = 0
FAILED = 0

BINDING = bind_execution(ROOT)
CONTRACT = BINDING.binding
PLAN = BINDING.plan
RULES = PLAN["adopted_rules_unchanged"]
FIELDS = tuple(f["id"] for f in CONTRACT.fields)

C2 = "C2_geometry_false_rejection"
C7 = "C7_false_bridge"
C8 = "C8_blinded_scale_control"


def check(label: str, ok: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def refusal_code(fn, *args, **kwargs) -> str | None:
    try:
        fn(*args, **kwargs)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return None


def refuses_with_code(label: str, expected: str, fn, *args, **kwargs) -> None:
    got = refusal_code(fn, *args, **kwargs)
    check(f"{label} -> {expected}", got == expected, f"got {got!r}")


# ------------------------------------------------------------------ fixtures
COPIED = ("docs/e1a/e1a_v4_design_contract.json",
          "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
          "docs/theory/EBU_THEORY_BASELINE.md",
          "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
          PLAN_JSON, SEED_MAP_JSON, PLAN_MARKDOWN, SEAL_JSON)


def sandbox() -> str:
    tmp = tempfile.mkdtemp()
    for rel in COPIED:
        destination = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), destination)
    shutil.copytree(os.path.join(ROOT, "e1a_v4"), os.path.join(tmp, "e1a_v4"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


def fixture_artifact(condition, value: float = 0.0):
    """Null draws all equal to `value`. Deterministic; every column is arithmetic.

    This is a FIXTURE, not a calibration execution: nothing is drawn, and the
    artifact says so through `is_fixture`.
    """
    draws = {gate: tuple(float(value) for _ in range(condition.replicates))
             for gate in condition.gates}
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=condition.procedure_identity,
        field_id=condition.field_id, n=condition.n, m=condition.m,
        alpha_1=condition.alpha_1, null_draws=draws, condition=condition,
        schema=condition.canonical()["schema"], provenance="pure fixture",
        is_fixture=True)


def c2_aggregate(subcondition_id: str) -> dict:
    """A complete, arithmetically consistent C2 aggregate. Deterministic."""
    aggregate = aggregate_skeleton(C2, subcondition_id)
    aggregate["contract_diagnostics"] = {"per_field": {
        f: {"rejections": 2, "replicates": 400, "cp_upper": cp_upper(2, 400),
            "threshold": GROSS_INFLATION_TOLERANCE, "direction": "UPPER",
            "confidence_level": 0.95,
            "pass": cp_upper(2, 400) <= GROSS_INFLATION_TOLERANCE}
        for f in FIELDS}}
    return aggregate


C2_OUTCOME = {"analysis_status": "ESTIMATED", "beta_hat": 1.0, "P1": False,
              "p1_rejected": False, "block1_rejected": False, "g5_rejected": False}


class Campaign:
    """One sandboxed campaign output directory. Pure; nothing here draws."""

    def __init__(self) -> None:
        self.root = sandbox()
        self.binding = bind_execution(self.root)
        self.jobs = plan_campaign(self.binding.plan)
        self.out = os.path.join(self.root, "results", "e1a_v4_validation")
        self.ledger = CampaignCalibrationLedger()
        # A distinct null-draw column per locked artifact, so each fixture is a
        # DIFFERENT artifact. Identical fixtures would hash identically and the
        # ledger would refuse the second as CALIBRATION_REUSE_REFUSED -- correctly,
        # since under REPLICATE_CONDITIONAL calibration an identical digest is not
        # permission to share an artifact.
        self._fixtures = 0

    def job(self, case_id: str, *, replicate: int = 0, field_id: str | None = None,
            subcondition_id: str | None = None):
        for job in self.jobs:
            c = job.coordinates
            if (c.case_id == case_id and c.replicate_id == replicate
                    and (field_id is None or c.scope == field_id)
                    and (subcondition_id is None or c.subcondition_id == subcondition_id)):
                return job
        raise AssertionError(f"no planned job for {case_id} r{replicate} {field_id}")

    def run(self, job, *, aggregate=None, outcome=None, terminal=True):
        """Drive ONE job through the frozen dependency graph. No RNG, no draws.

        `terminal=False` stops after the calibration lock, which is the ordinary
        partially completed state a restart must reconcile.
        """
        execution = job_execution(self.binding, job, self.ledger, self.out)
        calibration = execution.calibration
        spec = next(f for f in self.binding.binding.fields
                    if f["id"] == job.coordinates.scope)
        field = build_field(self.binding.binding, spec,
                            calibration_route="force_displacement_with_stokes_drag",
                            viscosity=0.00089, bead_radius=1e-6)
        execution.realise_branch_a(
            field, branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
            common_mode_seed=calibration.common_mode_seed(),
            generator_identity="PURE-FIXTURE-NO-DRAW")
        execution.publish_branch_a()
        digest = None
        if job.requires_calibration:
            condition = execution.calibration_condition()
            self._fixtures += 1
            digest = execution.lock_calibration(
                fixture_artifact(condition, self._fixtures * 1e-9))
        if not terminal:
            return execution, None, digest
        execution.unblind()
        execution.analyse(dict(outcome if outcome is not None else C2_OUTCOME))
        record = execution.record(
            aggregate if aggregate is not None
            else c2_aggregate(job.coordinates.subcondition_id))
        return execution, record, digest

    def links(self, coordinates: JobCoordinates):
        return (committed_publication(self.out, coordinates),
                committed_calibration_lock(self.out, coordinates))

    def validate(self, job, record):
        """Through the OFFICIAL entry point, which resolves its own provenance."""
        return refusal_code(validate_job_record, record, self.binding.plan,
                            self.binding, job, self.out)

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


def replace_lock(campaign, job, mutate) -> dict:
    """Rewrite the COMMITTED lock at this job's canonical slot, re-digested and
    re-committed so every structural check of the transaction layer is satisfied.

    This is what makes the counterexamples below real: the tampered lock is not
    a mapping handed to a function, it is a canonically formed committed record
    sitting in the campaign's own store.
    """
    directory = calibration_lock_directory(campaign.out)
    basename = calibration_lock_basename(job.coordinates)
    record = json.loads(json.dumps(
        committed_calibration_lock(campaign.out, job.coordinates)))
    mutate(record)
    record["lock_digest"] = sealed_digest(record, "lock_digest")
    for name in (basename, commit_name(basename)):
        path = os.path.join(directory, name)
        os.chmod(path, 0o600)
        os.remove(path)
    publish_transaction(directory, basename, record,
                        publication_digest=record["lock_digest"],
                        provenance={"coordinates": job.coordinates.as_dict(),
                                    "job_id": record["job_id"],
                                    "execution_identity": "restated"})
    return record


def plant_lock(campaign, job, borrow_from) -> dict:
    """COMMIT a canonically formed lock at `job`'s slot, built from another job's.

    Used to place a lock where the frozen plan says none belongs.
    """
    source = json.loads(json.dumps(
        committed_calibration_lock(campaign.out, borrow_from.coordinates)))
    source["coordinates"] = job.coordinates.as_dict()
    source["job_id"] = job.job_id
    source["lock_digest"] = sealed_digest(source, "lock_digest")
    publish_transaction(calibration_lock_directory(campaign.out),
                        calibration_lock_basename(job.coordinates), source,
                        publication_digest=source["lock_digest"],
                        provenance={"coordinates": job.coordinates.as_dict(),
                                    "job_id": job.job_id,
                                    "execution_identity": "restated"})
    return source


def mutated(record: dict, key: str, value) -> dict:
    """Change one field and RE-DIGEST, exactly as the auditor did. The record is
    internally self-consistent again and must still be refused."""
    candidate = json.loads(json.dumps(record))
    if value is _ABSENT:
        candidate.pop(key, None)
    else:
        candidate[key] = value
    candidate["result_digest"] = sealed_digest(candidate, "result_digest")
    return candidate


class _Absent:
    def __repr__(self) -> str:
        return "<absent>"


_ABSENT = _Absent()


# ================================ A1. the auditor's two counterexamples
def test_auditor_counterexamples() -> None:
    """THE BLOCKER. Null and fabricated artifact identities, re-digested."""
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)

    check("the terminal record names the artifact that was actually locked",
          record["calibration_artifact_sha256"] == digest, str(digest)[:16] + "...")
    check("A valid calibrating terminal record validates",
          campaign.validate(job, record) is None,
          str(campaign.validate(job, record)))

    refuses_with_code(
        "A. calibration_artifact_sha256 = null, RE-DIGESTED",
        "CALIBRATION_ARTIFACT_BINDING_INVALID", validate_job_record,
        mutated(record, "calibration_artifact_sha256", None), campaign.binding.plan,
        campaign.binding, job, campaign.out)
    refuses_with_code(
        "B. calibration_artifact_sha256 = fabricated valid-looking SHA-256, "
        "RE-DIGESTED",
        "CALIBRATION_ARTIFACT_BINDING_INVALID", validate_job_record,
        mutated(record, "calibration_artifact_sha256", "f" * 64),
        campaign.binding.plan, campaign.binding, job, campaign.out)
    campaign.close()


# ================================ A2. every required case of the invariant
def test_every_required_case() -> None:
    """The complete refusal table, plus the one ACCEPT it is measured against."""
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    publication, lock = campaign.links(job.coordinates)

    # A SECOND calibrating job, so "another job's artifact" is a real digest that
    # was genuinely locked -- not an invented string that any check would catch.
    other_field = campaign.job(C2, field_id=FIELDS[1])
    _e2, _r2, other_field_digest = campaign.run(other_field)
    other_replicate = campaign.job(C2, replicate=1)
    _e3, _r3, other_replicate_digest = campaign.run(other_replicate)
    subconditions = [s["subcondition_id"]
                     for s in next(c for c in PLAN["cases"] if c["case_id"] == C2)
                     ["subconditions"]]
    other_sub = campaign.job(C2, subcondition_id=subconditions[1])
    _e4, _r4, other_sub_digest = campaign.run(other_sub)
    other_case = campaign.job("C1_true_bridge_complete")
    _e5, _r5, other_case_digest = campaign.run(
        other_case, aggregate=aggregate_skeleton(
            "C1_true_bridge_complete", other_case.coordinates.subcondition_id),
        outcome={"analysis_status": "ESTIMATED", "beta_hat": 1.0, "P1": False,
                 "P2": True, "P3": True, "P4": True, "complete_pass": True,
                 "p1_rejected": False, "block1_rejected": False,
                 "g5_rejected": False})

    check("the four foreign artifacts are genuinely distinct locked digests",
          len({digest, other_field_digest, other_replicate_digest,
               other_sub_digest, other_case_digest}) == 5)

    table = (
        ("terminal artifact SHA absent", _ABSENT),
        ("terminal artifact SHA null", None),
        ("terminal artifact SHA malformed", "not-a-sha256"),
        ("terminal artifact SHA malformed (uppercase hex)", "F" * 64),
        ("terminal artifact SHA malformed (63 hex digits)", "a" * 63),
        ("terminal artifact SHA fabricated", "f" * 64),
        ("terminal artifact SHA for another field", other_field_digest),
        ("terminal artifact SHA for another replicate", other_replicate_digest),
        ("terminal artifact SHA for another subcondition", other_sub_digest),
        ("terminal artifact SHA for another case", other_case_digest),
    )
    for label, value in table:
        refuses_with_code(label, "CALIBRATION_ARTIFACT_BINDING_INVALID",
                          validate_job_record,
                          mutated(record, "calibration_artifact_sha256", value),
                          campaign.binding.plan, campaign.binding, job,
                          campaign.out)

    # Correct artifact SHA, but the artifact was never locked. A caller can no
    # longer express this by passing lock=None; it is expressed the only way it
    # can actually occur, by the canonical store not holding the lock.
    directory = calibration_lock_directory(campaign.out)
    basename = calibration_lock_basename(job.coordinates)
    for name in (basename, commit_name(basename)):
        os.chmod(os.path.join(directory, name), 0o600)
        os.remove(os.path.join(directory, name))
    refuses_with_code("correct artifact SHA but artifact NOT locked",
                      "CALIBRATION_LOCK_MISSING", validate_job_record,
                      json.loads(json.dumps(record)), campaign.binding.plan,
                      campaign.binding, job, campaign.out)
    campaign.close()
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    check("correct locked artifact SHA for the exact job -> ACCEPT",
          campaign.validate(job, record) is None,
          str(campaign.validate(job, record)))
    campaign.close()


# ================================ A3. the lock is EXTERNAL, not caller-supplied
def test_binding_is_external() -> None:
    """The authority is the committed lock on disk, never an argument."""
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    directory = calibration_lock_directory(campaign.out)
    basename = calibration_lock_basename(job.coordinates)

    check("the lock is persisted as a COMMITTED transaction, not held in memory",
          os.path.isfile(os.path.join(directory, basename))
          and os.path.isfile(os.path.join(directory, commit_name(basename))))
    stored = read_published(os.path.join(directory, basename), "the lock")
    check("the lock record carries every key the strict schema requires",
          all(k in stored for k in CALIBRATION_LOCK_KEYS))
    check("the lock record declares its own schema",
          stored["schema"] == CALIBRATION_LOCK_SCHEMA, str(stored["schema"]))
    check("the lock names the artifact the ledger actually registered",
          stored["calibration_artifact_sha256"] == digest)
    check("the lock is bound to the COMMITTED Branch-A publication, so the "
          "complete chain is one object",
          stored["branch_a_evidence_sha256"]
          == committed_publication(campaign.out, job.coordinates)[
              "branch_a_evidence_sha256"]
          and stored["publication_digest"] == committed_publication(
              campaign.out, job.coordinates)["publication_digest"]
          and stored["calibration_condition_sha256"] == committed_publication(
              campaign.out, job.coordinates)["calibration_condition_sha256"])
    check("the lock's basename is a pure function of the coordinates, so a lock "
          "for another job cannot be read in this one's place",
          basename == calibration_lock_basename(job.coordinates)
          and basename != calibration_lock_basename(
              campaign.job(C2, replicate=1).coordinates))

    # A lock edited in place, without its marker, refuses on the bytes.
    forged = dict(stored, calibration_artifact_sha256="e" * 64)
    forged["lock_digest"] = sealed_digest(forged, "lock_digest")
    path = os.path.join(directory, basename)
    os.chmod(path, 0o600)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(forged, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(path, 0o444)
    # The lock's own `lock_digest` is self-consistent again, so only the commit
    # marker's byte hash can tell. It does.
    refuses_with_code(
        "a lock record rewritten and RE-DIGESTED in place, under its unchanged "
        "commit marker",
        "PUBLICATION_INCOMPLETE", committed_calibration_lock, campaign.out,
        job.coordinates)
    campaign.close()


# ================================ A4. C7 and C8 remain no-calibration paths
def test_non_calibrating_cases_unchanged() -> None:
    """FROZEN SEMANTICS PRESERVED. No calibration requirement is invented."""
    campaign = Campaign()
    # One real calibrating job first, purely so a genuine committed lock exists
    # to build the planted counterexamples from. Its own validity is A1's job.
    donor = campaign.job(C2)
    campaign.run(donor)
    for case_id in (C7, C8):
        job = campaign.job(case_id)
        check(f"{case_id}: the frozen plan requires no calibration",
              job.requires_calibration is False)
        outcome = {"analysis_status": "ESTIMATED", "beta_hat": 1.0,
                   "false_acceptance": False} if case_id == C7 else {
            "analysis_status": "ESTIMATED", "beta_hat": 1.0,
            "scale_recovered": True}
        _execution, record, digest = campaign.run(
            job, aggregate=aggregate_skeleton(case_id,
                                              job.coordinates.subcondition_id),
            outcome=outcome)
        check(f"{case_id}: no artifact is locked", digest is None)
        publication, lock = campaign.links(job.coordinates)
        check(f"{case_id}: no calibration lock is written", lock is None)
        check(f"{case_id}: calibration_artifact_sha256 is null, as frozen "
              "authority requires",
              record["calibration_artifact_sha256"] is None)
        check(f"{case_id}: the record validates", campaign.validate(job, record)
              is None, str(campaign.validate(job, record)))
        # the EXISTING rule, unchanged: a calibration link may not be invented
        refuses_with_code(
            f"{case_id}: a fabricated artifact SHA, RE-DIGESTED",
            "TERMINAL_PROVENANCE_MISMATCH", validate_job_record,
            mutated(record, "calibration_artifact_sha256", "f" * 64),
            campaign.binding.plan, campaign.binding, job, campaign.out)
        # and the new rule in the other direction: no lock may exist for it.
        # Checked through the CANONICAL verifier by planting a real committed
        # lock at this non-calibrating job's canonical slot.
        plant_lock(campaign, job, borrow_from=donor)
        refuses_with_code(
            f"{case_id}: a committed calibration lock present for a "
            "no-calibration case",
            "CALIBRATION_LOCK_UNPLANNED", verified_calibration_lock,
            campaign.out, job, campaign.binding)
        refuses_with_code(
            f"{case_id}: and restart reconciliation refuses it too",
            "CALIBRATION_LOCK_UNPLANNED", reconcile_calibration_locks,
            campaign.out, campaign.binding, [job])
    campaign.close()


# ================================ A5. restart is never the weaker path
def test_restart_uses_the_same_validator() -> None:
    """§8. The same external artifact binding, on the reconciliation path."""
    for label, key, value in (
            ("null artifact SHA", "calibration_artifact_sha256", None),
            ("fabricated artifact SHA", "calibration_artifact_sha256", "f" * 64),
            ("absent artifact SHA", "calibration_artifact_sha256", _ABSENT)):
        campaign = Campaign()
        job = campaign.job(C2)
        _execution, record, _digest = campaign.run(job)
        publish_job_record(campaign.out, mutated(record, key, value),
                           campaign.binding)
        refuses_with_code(
            f"RESTART inventory of a record with a {label}",
            "CALIBRATION_ARTIFACT_BINDING_INVALID", inventory_job_records,
            campaign.out, campaign.binding, [job])
        campaign.close()

    # a WRONG-JOB artifact SHA, on the restart path
    campaign = Campaign()
    job = campaign.job(C2)
    other = campaign.job(C2, replicate=1)
    _e1, record, _d1 = campaign.run(job)
    _e2, _r2, other_digest = campaign.run(other)
    publish_job_record(campaign.out,
                       mutated(record, "calibration_artifact_sha256", other_digest),
                       campaign.binding)
    refuses_with_code(
        "RESTART inventory of a record naming ANOTHER job's locked artifact",
        "CALIBRATION_ARTIFACT_BINDING_INVALID", inventory_job_records,
        campaign.out, campaign.binding, [job, other])
    campaign.close()

    # A threshold conditional on evidence that is not there is not a conditional
    # threshold. The lock store is reconciled against the publication store, so a
    # lock whose Branch-A publication is gone refuses instead of being skipped.
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job)
    directory = publication_directory(campaign.out)
    basename = publication_basename(job.coordinates)
    for name in (basename, commit_name(basename)):
        os.chmod(os.path.join(directory, name), 0o600)
        os.remove(os.path.join(directory, name))
    refuses_with_code(
        "RESTART reconciliation of a calibration lock whose Branch-A publication "
        "is absent",
        "CALIBRATION_LOCK_WITHOUT_PUBLICATION", verify_restart, campaign.out, {},
        campaign.binding, [job])
    campaign.close()


def recovered(campaign):
    return recover_realisations(campaign.out, campaign.binding)


# ================================ A6. the valid round trip survives
def test_valid_round_trip() -> None:
    """§9. write -> read -> verify -> restart verify preserves the identity."""
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    publish_job_record(campaign.out, record, campaign.binding)

    found = inventory_job_records(campaign.out, campaign.binding, [job])
    check("the committed record is recovered from disk", job.job_id in found)
    check("the artifact identity survives the round trip EXACTLY",
          found[job.job_id]["calibration_artifact_sha256"] == digest, digest[:16])
    restart = verify_restart(campaign.out, recovered(campaign), campaign.binding,
                             [job])
    check("restart reconciles the calibration-lock store",
          restart["calibration_locks_on_disk"] == 1,
          str(restart.get("calibration_locks_on_disk")))
    locks = inventory_calibration_locks(campaign.out)
    check("the lock store is independently discoverable", list(locks) == [job.job_id])
    check("and it names the same artifact",
          locks[job.job_id]["calibration_artifact_sha256"] == digest)
    check("is_sha256 accepts the locked identity and rejects near-misses",
          is_sha256(digest) and not is_sha256(digest.upper())
          and not is_sha256(digest[:-1]) and not is_sha256(None))
    campaign.close()


# ================ B1. FINDING A -- the caller cannot supply the lock
def test_caller_cannot_supply_the_lock() -> None:
    """AUDIT FINDING A. The trust boundary, not the comparison, was the defect.

    The auditor's counterexample: a fabricated lock mapping that was never
    persisted, matching a fabricated artifact digest in a re-digested terminal
    record, handed straight to the official validator -- which accepted the pair,
    while the same terminal record checked against the actual committed lock
    refused. The comparison was already right. What was wrong is that the object
    which exists to PROVE a record's provenance could be supplied by whoever
    wanted the record believed.
    """
    signature = inspect.signature(validate_job_record)
    for forbidden in ("lock", "publication", "expected_artifact_sha256",
                      "expected_lock_digest"):
        check(f"the official validator declares no {forbidden!r} parameter",
              forbidden not in signature.parameters,
              str(list(signature.parameters)))
    check("it takes the campaign output ROOT instead",
          "output_dir" in signature.parameters, str(list(signature.parameters)))

    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    forged = "a1b2c3d4" * 8
    tampered = mutated(record, "calibration_artifact_sha256", forged)

    # The auditor's fabricated lock: canonically shaped, self-consistent, and
    # never written to the store.
    fake_lock = json.loads(json.dumps(
        committed_calibration_lock(campaign.out, job.coordinates)))
    fake_lock["calibration_artifact_sha256"] = forged
    fake_lock["lock_digest"] = sealed_digest(fake_lock, "lock_digest")
    check("the fabricated lock IS internally self-consistent, so nothing about "
          "its own bytes would have caught it",
          sealed_digest(dict(fake_lock), "lock_digest") == fake_lock["lock_digest"])
    check("and it was never persisted",
          committed_calibration_lock(campaign.out, job.coordinates)
          ["calibration_artifact_sha256"] != forged)

    try:
        validate_job_record(tampered, campaign.binding.plan, campaign.binding,
                            job, committed_publication(campaign.out,
                                                       job.coordinates), fake_lock)
        supplied = "ACCEPTED"
    except TypeError:
        supplied = "TypeError"
    except Refusal:
        supplied = "Refusal"
    check("the fabricated lock cannot even be PASSED to the official validator",
          supplied == "TypeError", supplied)
    refuses_with_code(
        "and the same tampered terminal record, through the official path",
        "CALIBRATION_ARTIFACT_BINDING_INVALID", validate_job_record, tampered,
        campaign.binding.plan, campaign.binding, job, campaign.out)

    # THE POSITIVE CONTROL. Mandatory: a repair that refuses everything is not a
    # repair.
    check("the untampered record still validates through the official path",
          campaign.validate(job, record) is None,
          str(campaign.validate(job, record)))

    # The private pure helper still exists for unit testing, and still means
    # "compare against an ALREADY-VERIFIED lock".
    verified = verified_calibration_lock(campaign.out, job, campaign.binding)
    check("the canonical verifier returns this job's own verified lock",
          verified["job_id"] == job.job_id
          and verified["calibration_artifact_sha256"] == digest)
    check("the private helper is private: it is not the production entry point",
          _compare_terminal_to_verified_lock.__name__.startswith("_"))
    check("and it accepts the verified lock for the valid record",
          refusal_code(_compare_terminal_to_verified_lock, record, job, verified,
                       committed_publication(campaign.out, job.coordinates),
                       campaign.binding) is None)
    campaign.close()


# ================ B2. FINDING B -- every lock is valid before any terminal
def test_locks_validate_before_any_terminal_exists() -> None:
    """AUDIT FINDING B. Semantic lock validation used to happen too late.

    A canonically committed lock that named another planned job, or another
    field, was accepted by restart reconciliation whenever no terminal record had
    been written yet -- because those two checks lived only in terminal
    validation. Whether an intermediate provenance object is valid may not depend
    on whether a downstream record happens to exist, and the state in which no
    terminal record exists is the ordinary resumable state.
    """
    # --- Case 1: job A's canonical slot, holding a lock that names job B -----
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    b = campaign.job(C2, field_id=FIELDS[0])
    campaign.run(a)
    campaign.run(b)
    replace_lock(campaign, a, lambda r: r.__setitem__("job_id", b.job_id))
    check("both A and B are legitimate planned calibrating jobs -- the wrong "
          "identity is a VALID identity elsewhere",
          a.requires_calibration and b.requires_calibration and a.job_id != b.job_id)
    check("no terminal record exists for either", not os.path.isdir(
        os.path.join(campaign.out, "job_records")) or not os.listdir(
        os.path.join(campaign.out, "job_records")))
    for name, fn, args in (
            ("verify_restart", verify_restart,
             (campaign.out, recovered(campaign), campaign.binding, [a, b])),
            ("inventory_job_records", inventory_job_records,
             (campaign.out, campaign.binding, [a, b])),
            ("reconcile_calibration_locks", reconcile_calibration_locks,
             (campaign.out, campaign.binding, [a, b])),
            ("verified_calibration_lock", verified_calibration_lock,
             (campaign.out, a, campaign.binding))):
        refuses_with_code(f"job A's slot holding job B's lock, via {name}",
                          "CALIBRATION_LOCK_JOB_MISMATCH", fn, *args)
    campaign.close()

    # --- Case 2: job A's canonical slot, holding another field's artifact ----
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    campaign.run(a)
    replace_lock(campaign, a,
                 lambda r: r.__setitem__("artifact_field_id", FIELDS[0]))
    for name, fn, args in (
            ("verify_restart", verify_restart,
             (campaign.out, recovered(campaign), campaign.binding, [a])),
            ("inventory_job_records", inventory_job_records,
             (campaign.out, campaign.binding, [a])),
            ("reconcile_calibration_locks", reconcile_calibration_locks,
             (campaign.out, campaign.binding, [a])),
            ("verified_calibration_lock", verified_calibration_lock,
             (campaign.out, a, campaign.binding))):
        refuses_with_code(
            f"job A's lock carrying field {FIELDS[0]!r} instead of "
            f"{FIELDS[1]!r}, via {name}",
            "CALIBRATION_LOCK_FIELD_MISMATCH", fn, *args)
    campaign.close()

    # --- an UNPLANNED lock ---------------------------------------------------
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    other = campaign.job(C2, replicate=1)
    campaign.run(a)
    campaign.run(other)
    refuses_with_code(
        "a committed lock whose coordinates match no job this campaign planned",
        "CALIBRATION_LOCK_UNPLANNED", reconcile_calibration_locks, campaign.out,
        campaign.binding, [a])
    campaign.close()

    # --- the lock's upstream links, checked with no terminal record ----------
    for label, mutate, expected in (
            ("Branch-A evidence hash",
             lambda r: r.__setitem__("branch_a_evidence_sha256", "0" * 64),
             "CALIBRATION_LOCK_PROVENANCE_MISMATCH"),
            ("publication digest",
             lambda r: r.__setitem__("publication_digest", "0" * 64),
             "CALIBRATION_LOCK_PROVENANCE_MISMATCH"),
            ("calibration-condition identity",
             lambda r: r.__setitem__("calibration_condition_sha256", "0" * 64),
             "CALIBRATION_LOCK_PROVENANCE_MISMATCH"),
            ("execution identity",
             lambda r: r["package_identities"].__setitem__(
                 "execution_identity", "0" * 64),
             "CALIBRATION_LOCK_PROVENANCE_MISMATCH"),
            ("cited publication basename",
             lambda r: r.__setitem__("publication_basename", "branch_a_0.json"),
             "CALIBRATION_LOCK_PROVENANCE_MISMATCH")):
        campaign = Campaign()
        a = campaign.job(C2, field_id=FIELDS[1])
        campaign.run(a)
        replace_lock(campaign, a, mutate)
        refuses_with_code(
            f"a committed lock whose {label} is wrong, with no terminal record",
            expected, verify_restart, campaign.out, recovered(campaign),
            campaign.binding, [a])
        campaign.close()

    # --- THE POSITIVE CONTROL. Guards against over-repair. -------------------
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    campaign.run(a)
    restart = verify_restart(campaign.out, recovered(campaign), campaign.binding,
                             [a])
    check("valid publication + exact durable lock + NO terminal record -> "
          "restart reconciliation ACCEPTS",
          restart["calibration_locks_on_disk"] == 1,
          str(restart.get("calibration_locks_on_disk")))
    check("and the terminal-record inventory accepts that state too",
          refusal_code(inventory_job_records, campaign.out, campaign.binding,
                       [a]) is None)
    check("Branch-A published, calibration locked, terminal not yet written is a "
          "NORMAL resumable state",
          reconcile_calibration_locks(campaign.out, campaign.binding, [a])
          [a.job_id]["job_id"] == a.job_id)
    campaign.close()


# ================ B3. one verifier, no aliases, ordering preserved
def test_one_verifier_and_no_aliases() -> None:
    """§20 / §22 / §34. Structural properties the repair must not have lost."""
    jobs = plan_campaign(PLAN)
    calibrating = [j for j in jobs if j.requires_calibration]
    basenames = {calibration_lock_basename(j.coordinates) for j in calibrating}
    check("every calibrating job has a DISTINCT canonical lock filename",
          len(basenames) == len(calibrating) == 46000,
          f"{len(basenames)} names for {len(calibrating)} jobs")
    check("a lock filename is a pure function of the coordinates, so no two "
          "coordinates alias one slot",
          len({calibration_lock_basename(j.coordinates) for j in jobs})
          == len(jobs) == 53200)

    # ONE verifier: terminal validation and restart both route through it.
    source = inspect.getsource(validate_job_record)
    check("the official terminal validator calls the canonical lock verifier",
          "verified_calibration_lock(" in source)
    check("and resolves a VERIFIED publication itself, not a merely committed one",
          "verified_publication(" in source
          and "committed_publication(" not in source)
    restart_source = inspect.getsource(reconcile_calibration_locks)
    check("restart reconciliation calls the SAME canonical lock verifier",
          "verified_calibration_lock(" in restart_source)
    check("and enumerates the store itself rather than trusting an argument",
          "inventory_calibration_locks(" in restart_source)

    # A second file cannot shadow a job's canonical slot.
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    campaign.run(a)
    lock = committed_calibration_lock(campaign.out, a.coordinates)
    alias = "calibration_lock_" + "0" * 64 + ".json"
    publish_transaction(calibration_lock_directory(campaign.out), alias,
                        dict(lock), publication_digest=lock["lock_digest"],
                        provenance={"coordinates": a.coordinates.as_dict(),
                                    "job_id": a.job_id,
                                    "execution_identity": "restated"})
    refuses_with_code(
        "a SECOND committed file holding the same job's lock record",
        "CALIBRATION_LOCK_JOB_MISMATCH", inventory_calibration_locks, campaign.out)
    campaign.close()

    # ORDERING: a lock that cannot be persisted leaves the job before
    # CALIBRATION_LOCKED, and Branch B stays unreachable.
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    execution = job_execution(campaign.binding, a, campaign.ledger, campaign.out)
    calibration = execution.calibration
    spec = next(f for f in campaign.binding.binding.fields
                if f["id"] == a.coordinates.scope)
    field = build_field(campaign.binding.binding, spec,
                        calibration_route="force_displacement_with_stokes_drag",
                        viscosity=0.00089, bead_radius=1e-6)
    execution.realise_branch_a(
        field, branch_a_seed=calibration.branch_a_seed(a.coordinates.scope),
        common_mode_seed=calibration.common_mode_seed(),
        generator_identity="PURE-FIXTURE-NO-DRAW")
    execution.publish_branch_a()
    condition = execution.calibration_condition()
    # Obstruct the lock's canonical path with a DIRECTORY, so persistence fails
    # for a filesystem reason rather than a patched function.
    os.makedirs(os.path.join(calibration_lock_directory(campaign.out),
                             calibration_lock_basename(a.coordinates)),
                exist_ok=True)
    before = execution.state
    failed = False
    try:
        execution.lock_calibration(fixture_artifact(condition, 7e-9))
    except (Refusal, OSError):
        failed = True
    check("a lock that cannot be persisted FAILS", failed)
    check("and leaves the job in its pre-lock state, not CALIBRATION_LOCKED",
          execution.state == before == "CALIBRATION_CONDITION_BOUND",
          f"{before} -> {execution.state}")
    refuses_with_code("so Branch B cannot be unblinded", "JOB_STATE_INVALID",
                      execution.unblind)
    refuses_with_code("and no Branch-B seed is reachable", "BRANCH_B_PREMATURE",
                      execution.branch_b_seed)
    campaign.close()


# ================ C1. FINDING A -- a committed publication is not a valid one
def republish(directory, basename, record, digest_key, job_id, coordinates):
    """Re-COMMIT a record at its canonical slot through the real transaction."""
    for name in (basename, commit_name(basename)):
        path = os.path.join(directory, name)
        if os.path.lexists(path):
            os.chmod(path, 0o600)
            os.remove(path)
    publish_transaction(directory, basename, record,
                        publication_digest=record[digest_key],
                        provenance={"coordinates": coordinates.as_dict(),
                                    "job_id": job_id,
                                    "execution_identity": "restated"})


def restart_refusal(campaign, planned):
    """The first coded refusal anywhere on the restart path, or None."""
    try:
        known = recover_realisations(campaign.out, campaign.binding)
    except Refusal as exc:
        return getattr(type(exc), "code", "UNCODED")
    return refusal_code(verify_restart, campaign.out, known, campaign.binding,
                        planned)


def forge_chain(campaign, job, mutate_publication):
    """Tamper the COMMITTED publication, then re-digest the lock and the terminal
    record so the entire downstream chain agrees with the forgery.

    This is the shape that matters: every object is internally self-consistent and
    durably committed, and they all agree with each other. What they disagree with
    is frozen authority, which is the only thing that can tell.
    """
    coordinates = job.coordinates
    publication = json.loads(json.dumps(
        committed_publication(campaign.out, coordinates)))
    mutate_publication(publication)
    publication["publication_digest"] = sealed_digest(publication,
                                                      "publication_digest")
    republish(publication_directory(campaign.out),
              publication_basename(coordinates), publication,
              "publication_digest", job.job_id, coordinates)
    lock = json.loads(json.dumps(
        committed_calibration_lock(campaign.out, coordinates)))
    for key in ("publication_digest", "branch_a_evidence_sha256",
                "calibration_condition_sha256"):
        lock[key] = publication[key]
    lock["lock_digest"] = sealed_digest(lock, "lock_digest")
    republish(calibration_lock_directory(campaign.out),
              calibration_lock_basename(coordinates), lock, "lock_digest",
              job.job_id, coordinates)
    return publication, lock


def retied(record, publication, lock):
    """The terminal record, re-digested to agree with the forged chain."""
    out = json.loads(json.dumps(record))
    for key in ("publication_digest", "branch_a_evidence_sha256",
                "calibration_condition_sha256"):
        out[key] = publication[key]
    out["calibration_artifact_sha256"] = lock["calibration_artifact_sha256"]
    out["result_digest"] = sealed_digest(out, "result_digest")
    return out


PUBLICATION_MUTATIONS = (
    ("invalid publication schema", "PUBLICATION_INCOMPLETE",
     lambda p: p.__setitem__("schema", "e1a_v4_branch_a_publication/999")),
    ("state is not BRANCH_A_PUBLISHED", "PUBLICATION_INCOMPLETE",
     lambda p: p.__setitem__("state", "PLANNED")),
    ("an unknown extra field in the envelope", "PUBLICATION_INCOMPLETE",
     lambda p: p.__setitem__("smuggled", "an unauthenticated channel")),
    ("a declared field removed", "PUBLICATION_INCOMPLETE",
     lambda p: p.pop("not_execution_authorisation")),
    ("not_execution_authorisation is false", "PUBLICATION_INCOMPLETE",
     lambda p: p.__setitem__("not_execution_authorisation", False)),
    ("false execution identity", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["package_identities"].__setitem__("execution_identity", "0" * 64)),
    ("false analysis procedure identity", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["package_identities"].__setitem__(
         "analysis_procedure_identity", "0" * 64)),
    ("false contract identity", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["package_identities"].__setitem__("contract_sha256", "0" * 64)),
    ("false plan identity", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["package_identities"].__setitem__("plan_sha256", "0" * 64)),
    ("false seed-map identity", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["package_identities"].__setitem__("seed_map_sha256", "0" * 64)),
    ("wrong case", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["coordinates"].__setitem__("case_id", "C1_true_bridge_complete")),
    ("wrong subcondition", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["coordinates"].__setitem__("subcondition_id", "sigma_psi_0p5")),
    ("wrong replicate", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["coordinates"].__setitem__("replicate_id", 999999)),
    ("wrong field/scope", "BRANCH_A_PROVENANCE_MISMATCH",
     lambda p: p["coordinates"].__setitem__("scope", "theta3_temperature")),
    ("wrong evidence digest", "BRANCH_A_EVIDENCE_ALTERED",
     lambda p: p.__setitem__("branch_a_evidence_sha256", "0" * 64)),
)


def test_committed_publication_is_not_a_valid_one() -> None:
    """AUDIT FINDING A. Commit verification is not publication validation.

        commit verification       "were these exact bytes durably committed?"
        publication verification  "is this committed record a VALID Branch-A
                                   publication, for this exact planned job, under
                                   the current execution package?"

    Terminal validation resolved the publication from the store -- which closed
    the caller-trust hole -- and then trusted it on its commit transaction alone.
    Every mutation below is durably committed and every downstream object is
    re-digested to agree with it, so nothing local can tell. Only frozen authority
    can, and now it does.
    """
    for label, expected, mutate in PUBLICATION_MUTATIONS:
        campaign = Campaign()
        job = campaign.job(C2)
        _execution, record, _digest = campaign.run(job)
        publication, lock = forge_chain(campaign, job, mutate)
        forged = retied(record, publication, lock)
        refuses_with_code(
            f"committed publication with {label}, whole chain re-digested",
            expected, validate_job_record, forged, campaign.binding.plan,
            campaign.binding, job, campaign.out)
        # §9: RESTART must not be the weaker path for the same forgery. The
        # refusal may come from either half of the restart path -- recovering the
        # claimed evidence, or reconciling the store -- so both are taken.
        got = restart_refusal(campaign, [job])
        check(f"    and the restart path refuses it too", got is not None,
              f"got {got!r}")
        campaign.close()

    # PINNED: the package-identity forgeries pass every STRUCTURAL check, so they
    # are exactly the class that used to be invisible. They must be refused by the
    # publication verifier itself, inside verify_restart, not by an earlier layer.
    for label, mutate in (
            ("execution identity",
             lambda p: p["package_identities"].__setitem__(
                 "execution_identity", "0" * 64)),
            ("analysis procedure identity",
             lambda p: p["package_identities"].__setitem__(
                 "analysis_procedure_identity", "0" * 64))):
        campaign = Campaign()
        job = campaign.job(C2)
        campaign.run(job)
        forge_chain(campaign, job, mutate)
        known = recover_realisations(campaign.out, campaign.binding)
        check(f"the store still RECOVERS a publication with a false {label} -- "
              "nothing structural can tell", len(known) == 1)
        refuses_with_code(
            f"    and verify_restart's publication verifier refuses it",
            "BRANCH_A_PROVENANCE_MISMATCH", verify_restart, campaign.out, known,
            campaign.binding, [job])
        campaign.close()

    # THE POSITIVE CONTROL. A valid publication still verifies, end to end.
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, digest = campaign.run(job)
    check("a valid committed publication verifies",
          verified_publication(campaign.out, job, campaign.binding)
          ["branch_a_evidence_sha256"] == record["branch_a_evidence_sha256"])
    check("and the valid terminal chain still validates",
          campaign.validate(job, record) is None,
          str(campaign.validate(job, record)))
    check("a job with no publication at all resolves to None, not a refusal",
          verified_publication(campaign.out, campaign.job(C2, replicate=3),
                               campaign.binding) is None)
    campaign.close()


# ================ C2. FINDING B -- semantic reconciliation cannot be disabled
def test_restart_requires_the_canonical_plan() -> None:
    """AUDIT FINDING B. `planned=None` used to mean "stop checking identity".

    A provenance verifier may not offer a mode that silently downgrades itself to
    a structural inventory. The auditor placed a canonically committed lock naming
    job B in job A's slot, with no terminal record, and showed that
    `verify_restart(planned=None)` accepted what `verify_restart(planned=<plan>)`
    refused.
    """
    for label, mutate, with_plan in (
            ("a lock naming another planned job",
             lambda r, a, b: r.__setitem__("job_id", b.job_id),
             "CALIBRATION_LOCK_JOB_MISMATCH"),
            ("a lock carrying the wrong field",
             lambda r, a, b: r.__setitem__("artifact_field_id",
                                           b.coordinates.scope),
             "CALIBRATION_LOCK_FIELD_MISMATCH")):
        campaign = Campaign()
        a = campaign.job(C2, field_id=FIELDS[1])
        b = campaign.job(C2, field_id=FIELDS[0])
        campaign.run(a, terminal=False)
        campaign.run(b, terminal=False)
        replace_lock(campaign, a, lambda r: mutate(r, a, b))
        known = recover_realisations(campaign.out, campaign.binding)
        check(f"no terminal record exists for {label}",
              not os.path.isdir(os.path.join(campaign.out, "job_records")))
        refuses_with_code(f"{label}, with the canonical plan", with_plan,
                          verify_restart, campaign.out, known, campaign.binding,
                          [a, b])
        refuses_with_code(f"{label}, with planned=None",
                          "CAMPAIGN_PLAN_MISMATCH", verify_restart, campaign.out,
                          known, campaign.binding, None)
        omitted = False
        try:
            verify_restart(campaign.out, known, campaign.binding)
        except TypeError:
            omitted = True
        except Refusal:
            omitted = False
        check(f"{label}, with planned omitted entirely -> TypeError", omitted)
        campaign.close()

    # The same rule on the terminal-record inventory.
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job)
    refuses_with_code("the terminal-record inventory also requires the plan",
                      "CAMPAIGN_PLAN_MISMATCH", inventory_job_records,
                      campaign.out, campaign.binding, None)

    # §14: a caller may not REDEFINE restart truth by editing a descriptor.
    forged_job = CampaignJob(
        coordinates=job.coordinates, role=job.role, requires_calibration=False,
        seed_families=job.seed_families, branch_a_scopes=job.branch_a_scopes,
        result_kind=job.result_kind, depends_on=job.depends_on)
    refuses_with_code(
        "a supplied job descriptor whose calibration requirement was edited",
        "CAMPAIGN_PLAN_MISMATCH", verify_restart, campaign.out,
        recover_realisations(campaign.out, campaign.binding), campaign.binding,
        [forged_job])
    alien = CampaignJob(
        coordinates=JobCoordinates(C2, "sigma_psi_0p0", 999999, FIELDS[0]),
        role=job.role, requires_calibration=True,
        seed_families=job.seed_families, branch_a_scopes=job.branch_a_scopes,
        result_kind=job.result_kind, depends_on=())
    refuses_with_code("a supplied job the frozen planner never produced",
                      "CAMPAIGN_PLAN_MISMATCH", verify_restart, campaign.out,
                      recover_realisations(campaign.out, campaign.binding),
                      campaign.binding, [alien])
    check("a SUBSET of the canonical plan is still accepted, because omitting a "
          "job makes reconciliation stricter, not weaker",
          refusal_code(verify_restart, campaign.out,
                       recover_realisations(campaign.out, campaign.binding),
                       campaign.binding, [job]) is None)
    check("and the canonical plan is the frozen planner's, memoised by plan digest",
          len(canonical_plan(campaign.binding)) == 53200
          and canonical_plan(campaign.binding)
          is canonical_plan(campaign.binding))
    campaign.close()

    # THE POSITIVE CONTROLS. Valid partial progress, and the valid full chain.
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    campaign.run(a, terminal=False)
    restart = verify_restart(campaign.out,
                             recover_realisations(campaign.out, campaign.binding),
                             campaign.binding, [a])
    check("valid publication + valid lock + NO terminal -> restart ACCEPTS",
          restart["calibration_locks_on_disk"] == 1
          and restart["publications_on_disk"] == 1,
          str(restart))
    campaign.close()

    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[1])
    _execution, record, _digest = campaign.run(a)
    publish_job_record(campaign.out, record, campaign.binding)
    check("valid publication + valid lock + valid terminal -> terminal ACCEPTS",
          campaign.validate(a, record) is None, str(campaign.validate(a, record)))
    check("   and restart ACCEPTS",
          refusal_code(verify_restart, campaign.out,
                       recover_realisations(campaign.out, campaign.binding),
                       campaign.binding, [a]) is None)
    check("   and the terminal-record inventory ACCEPTS",
          refusal_code(inventory_job_records, campaign.out, campaign.binding,
                       [a]) is None)
    campaign.close()


# ================ D1. embedded Branch-A identities bound to the package
def forge_embedded(campaign, job, key, value):
    """Change ONE identity INSIDE the Branch-A evidence, then consistently
    recompute the evidence digest, the envelope digest and the commit marker.

    The result is a durably committed, internally self-consistent publication.
    Nothing local can tell it is wrong -- which is the whole point.
    """
    coordinates = job.coordinates
    publication = json.loads(json.dumps(
        committed_publication(campaign.out, coordinates)))
    if value is _ABSENT:
        publication["branch_a_evidence"].pop(key, None)
    else:
        publication["branch_a_evidence"][key] = value
    publication["branch_a_evidence_sha256"] = canonical_digest(
        publication["branch_a_evidence"])
    publication["publication_digest"] = sealed_digest(publication,
                                                      "publication_digest")
    republish(publication_directory(campaign.out),
              publication_basename(coordinates), publication,
              "publication_digest", job.job_id, coordinates)
    return publication


#: A different valid-looking value for each package-bound embedded identity.
FOREIGN_IDENTITY = {
    "schema": "e1a_v4_branch_a_publication/999",
    "contract_sha256": "b" * 64,
    "plan_sha256": "c" * 64,
    "analysis_identity": "a" * 64,
}


def test_embedded_identities_bound_to_package() -> None:
    """AUDIT BLOCKER. The evidence carried its own copies of the package
    identities and nobody compared them.

    The constructor stamped `contract_sha256`, `plan_sha256` and
    `analysis_identity` into the Branch-A evidence from the binding, and the
    verifier only ever compared the envelope's OUTER `package_identities`. An
    audit changed the embedded analysis identity and the embedded contract
    identity, recomputed the evidence digest, the envelope digest and the commit
    marker, and the shared publication verifier accepted the record -- on the
    terminal path and on restart alike.

    A field written from authority and never read back against it is the shape of
    defect that keeps recurring here.
    """
    # --- §4 / §10: the machine-defined set, and a guard against it going stale
    campaign = Campaign()
    job = campaign.job(C2)
    execution, record, digest = campaign.run(job)
    emitted = set(execution._realisation.canonical())
    check("every key the evidence emits is CLASSIFIED -- a new field cannot ship "
          "unclassified",
          sorted(emitted - set(EMBEDDED_EVIDENCE_CLASSIFICATION)) == [],
          str(sorted(emitted - set(EMBEDDED_EVIDENCE_CLASSIFICATION))))
    check("and the classification carries no stale key",
          sorted(set(EMBEDDED_EVIDENCE_CLASSIFICATION) - emitted) == [],
          str(sorted(set(EMBEDDED_EVIDENCE_CLASSIFICATION) - emitted)))
    check("the package-bound subset is exactly the four authority identities",
          EMBEDDED_PACKAGE_IDENTITY_FIELDS
          == ("analysis_identity", "contract_sha256", "plan_sha256", "schema"),
          str(EMBEDDED_PACKAGE_IDENTITY_FIELDS))

    # --- §18: the CONSTRUCTOR's source and the VERIFIER's expectation agree ---
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    for key, expected in sorted(
            embedded_authority_expectations(job, campaign.binding).items()):
        check(f"constructor stamps embedded {key} from the binding, and the "
              f"verifier expects that same value", evidence[key] == expected,
              f"{evidence[key]!r} vs {expected!r}")
    campaign.close()

    # --- §10 / §13 / §14 / §15: the programmatic mutation audit --------------
    tested = refused = unexpected = 0
    for key in EMBEDDED_PACKAGE_IDENTITY_FIELDS:
        campaign = Campaign()
        job = campaign.job(C2)
        _execution, record, _digest = campaign.run(job)
        publication = forge_embedded(campaign, job, key, FOREIGN_IDENTITY[key])
        # §9 / §21: the whole chain re-digested to agree with the forgery.
        lock = json.loads(json.dumps(
            committed_calibration_lock(campaign.out, job.coordinates)))
        for linked in ("publication_digest", "branch_a_evidence_sha256",
                       "calibration_condition_sha256"):
            lock[linked] = publication[linked]
        lock["lock_digest"] = sealed_digest(lock, "lock_digest")
        republish(calibration_lock_directory(campaign.out),
                  calibration_lock_basename(job.coordinates), lock, "lock_digest",
                  job.job_id, job.coordinates)
        forged = retied(record, publication, lock)
        tested += 1
        outcomes = {
            "shared verifier": refusal_code(verified_publication, campaign.out,
                                            job, campaign.binding),
            "terminal validation": refusal_code(
                validate_job_record, forged, campaign.binding.plan,
                campaign.binding, job, campaign.out),
            "restart": restart_refusal(campaign, [job]),
        }
        if all(v is not None for v in outcomes.values()):
            refused += 1
        else:
            unexpected += 1
        for path, got in outcomes.items():
            check(f"embedded {key} mismatched, whole chain re-digested -> "
                  f"{path} refuses", got is not None, f"got {got!r}")
        campaign.close()
    check(f"mutation audit: {tested} package-bound embedded identity field(s) "
          f"tested, {refused} refused on every path, {unexpected} unexpected "
          f"pass(es)", unexpected == 0 and tested == 4, f"{tested}/{refused}/{unexpected}")

    # --- §13 / §14: the two the auditor named, pinned to a stable category ---
    for label, key in (("analysis identity", "analysis_identity"),
                       ("contract identity", "contract_sha256"),
                       ("plan identity", "plan_sha256")):
        campaign = Campaign()
        job = campaign.job(C2)
        campaign.run(job, terminal=False)
        forge_embedded(campaign, job, key, FOREIGN_IDENTITY[key])
        refuses_with_code(
            f"embedded {label} != current, all digests recomputed, correctly "
            "committed", "BRANCH_A_PROVENANCE_MISMATCH", verified_publication,
            campaign.out, job, campaign.binding)
        # The claimed set must be the recovered one, or an earlier
        # unclaimed-publication check fires before the publication verifier.
        refuses_with_code(f"    and restart refuses it",
                          "BRANCH_A_PROVENANCE_MISMATCH", verify_restart,
                          campaign.out, recovered(campaign), campaign.binding,
                          [job])
        campaign.close()

    # --- §5: embedded and OUTER must not be two editable copies of one truth --
    for embedded_key, outer_key in EMBEDDED_TO_OUTER_IDENTITY:
        campaign = Campaign()
        job = campaign.job(C2)
        campaign.run(job, terminal=False)
        coordinates = job.coordinates
        publication = json.loads(json.dumps(
            committed_publication(campaign.out, coordinates)))
        # BOTH copies moved to the same foreign value: the record is now fully
        # self-consistent AND disagrees with the binding.
        foreign = "d" * 64
        publication["branch_a_evidence"][embedded_key] = foreign
        publication["package_identities"][outer_key] = foreign
        publication["branch_a_evidence_sha256"] = canonical_digest(
            publication["branch_a_evidence"])
        publication["publication_digest"] = sealed_digest(publication,
                                                          "publication_digest")
        republish(publication_directory(campaign.out),
                  publication_basename(coordinates), publication,
                  "publication_digest", job.job_id, coordinates)
        refuses_with_code(
            f"embedded AND outer {embedded_key} both moved to one foreign value",
            "BRANCH_A_PROVENANCE_MISMATCH", verified_publication, campaign.out,
            job, campaign.binding)
        campaign.close()

    # --- §17: required embedded identities may not be absent or malformed -----
    for key in EMBEDDED_PACKAGE_IDENTITY_FIELDS + ("generator_identity",):
        for label, value in (("absent", _ABSENT), ("null", None),
                             ("an empty string", ""), ("a non-string", 12345)):
            campaign = Campaign()
            job = campaign.job(C2)
            campaign.run(job, terminal=False)
            forge_embedded(campaign, job, key, value)
            refuses_with_code(f"embedded {key} is {label}",
                              "PUBLICATION_INCOMPLETE", verified_publication,
                              campaign.out, job, campaign.binding)
            campaign.close()

    # --- §11: a RECORDED PROVENANCE field, classified and NOT pinned ----------
    # `generator_identity` names the code that produced the measurement. Frozen
    # authority declares no expected value for it: the plan's
    # `generating_model.branch_a` describes the MODEL in prose, and the only
    # `generator_identity` the plan declares anywhere belongs to CALIBRATION
    # ("EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1"), not to Branch-A evidence.
    # Pinning it would invent a requirement and would forbid these very fixtures,
    # which legitimately record that the official generator did NOT run.
    plan_declared = json.loads(json.dumps(PLAN.get("calibration", {}))).get(
        "generator_identity")
    check("the plan declares a generator identity for CALIBRATION only",
          plan_declared == "EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1",
          str(plan_declared))
    check("Branch-A evidence has no plan-declared generator identity to pin to",
          "generator_identity" not in PLAN["generating_model"]["branch_a"])
    check("so it is classified OPEN_UNRESOLVED, not PACKAGE_BOUND",
          EMBEDDED_EVIDENCE_CLASSIFICATION["generator_identity"]
          == "OPEN_UNRESOLVED")
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    forge_embedded(campaign, job, "generator_identity", "ANOTHER-GENERATOR")
    check("a DIFFERENT non-empty generator identity is therefore accepted, by "
          "classification rather than by omission",
          refusal_code(verified_publication, campaign.out, job,
                       campaign.binding) is None)
    campaign.close()

    # --- §12 / §19: the positive control and the round trip -------------------
    campaign = Campaign()
    job = campaign.job(C2)
    execution, record, digest = campaign.run(job)
    publish_job_record(campaign.out, record, campaign.binding)
    check("a publication built by the production constructor VERIFIES",
          refusal_code(verified_publication, campaign.out, job,
                       campaign.binding) is None)
    check("   terminal validation ACCEPTS it", campaign.validate(job, record)
          is None, str(campaign.validate(job, record)))
    check("   restart ACCEPTS it",
          refusal_code(verify_restart, campaign.out, recovered(campaign),
                       campaign.binding, [job]) is None)
    reread = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    original = execution._realisation.canonical()
    check("construct -> serialise -> commit -> read preserves every package "
          "identity exactly",
          all(reread[k] == original[k]
              for k in EMBEDDED_PACKAGE_IDENTITY_FIELDS + ("generator_identity",)))
    check("and the rebuilt realisation round-trips to the same evidence digest",
          realisation_from_record(
              committed_publication(campaign.out, job.coordinates)
          ).evidence_sha256 == record["branch_a_evidence_sha256"])
    campaign.close()

    # --- §22: the CLEARED restart-plan finding is preserved, not reopened -----
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    known = recover_realisations(campaign.out, campaign.binding)
    refuses_with_code("planned=None still refuses (previously cleared)",
                      "CAMPAIGN_PLAN_MISMATCH", verify_restart, campaign.out,
                      known, campaign.binding, None)
    omitted = False
    try:
        verify_restart(campaign.out, known, campaign.binding)
    except TypeError:
        omitted = True
    except Refusal:
        omitted = False
    check("planned omitted still raises TypeError (previously cleared)", omitted)
    check("a valid partial restart still ACCEPTS (previously cleared)",
          refusal_code(verify_restart, campaign.out, known, campaign.binding,
                       [job]) is None)
    campaign.close()


# ================ E1. every embedded field verified against its authority
def foreign_job_seed(campaign, case_id, subcondition_id, replicate, scope):
    """A GENUINE authorised stream identity belonging to another planned job.

    Adversarially stronger than random garbage: the substituted value is a real
    seed the seed map authorises somewhere, so only a coordinate-specific check
    can tell it is not this job's.
    """
    return campaign.binding.case_access(case_id).stream(
        ValidationSeedFamily.BRANCH_A_MEASUREMENT, subcondition_id, replicate,
        scope)


def authority_mutations(campaign, job):
    """(label, embedded field, forged value) for EVERY externally bound field.

    Derived from the authority table, so a newly bound field that nobody writes a
    mutation for is caught by the coverage assertion below rather than skipped.
    """
    coordinates = job.coordinates
    sub = coordinates.subcondition_id
    other_sub = next(s["subcondition_id"] for c in PLAN["cases"]
                     if c["case_id"] == C2 for s in c["subconditions"]
                     if s["subcondition_id"] != sub)
    other_field = next(f for f in FIELDS if f != coordinates.scope)
    branch_b = campaign.binding.plan["generating_model"]["branch_b"]
    return (
        # PACKAGE_BOUND
        ("schema", "schema", "e1a_v4_branch_a_publication/999"),
        ("contract_sha256", "contract_sha256", "b" * 64),
        ("plan_sha256", "plan_sha256", "c" * 64),
        ("analysis_identity", "analysis_identity", "a" * 64),
        # JOB_BOUND
        ("coordinates", "coordinates",
         dict(coordinates.as_dict(), replicate_id=999999)),
        ("field_id", "field_id", other_field),
        # SEED_BOUND -- a GENUINE seed from another planned job
        ("branch_a_seed", "branch_a_seed",
         foreign_job_seed(campaign, C2, sub, coordinates.replicate_id,
                          other_field)),
        ("common_mode_seed", "common_mode_seed",
         foreign_job_seed(campaign, C2, other_sub, coordinates.replicate_id,
                          EXPERIMENT_SCOPE)),
        # PLAN_BOUND
        ("dt", "dt", canonical_float(float(branch_b["dt_s"]) * 2.0)),
        # CONTRACT_BOUND
        ("calibration_route", "calibration_route",
         "equipartition_k_equals_kBT_over_sigma_squared"),
        # DERIVED
        ("n_samples", "n_samples", int(branch_b["n_samples"]) + 1),
        ("branch_a_status", "branch_a_status", "TOTALLY_FINE"),
        ("tau_modes", "tau_modes", None),        # filled in below: re-sorted
    )


def test_embedded_field_authority() -> None:
    """AUDIT BLOCKER. A digest authenticates bytes; it does not establish
    agreement with the frozen job, the seed map, the plan or the contract.

    The previous repair bound the embedded PACKAGE identities and classified
    everything else as "scientific value". That catch-all was wrong: an audit
    forged correctly committed, fully re-digested publications carrying another
    planned job's Branch-A seed, another subcondition's common-mode stream,
    n_samples 2,000,001, a doubled dt, and the calibration route the contract
    explicitly FORBIDS -- and the shared read verifier accepted all of them.

    Seed correctness was checked when evidence was CREATED and not when it was
    RECOVERED. A read path that trusts what a write path proved is not a
    verifier.
    """
    # --- §6: totality, from machine-derived counts ---------------------------
    campaign = Campaign()
    job = campaign.job(C2)
    execution, record, digest = campaign.run(job)
    emitted = set(execution._realisation.canonical())
    declared = {row.field for row in BRANCH_A_FIELD_AUTHORITY}
    counts = authority_class_counts()
    check("the authority table classifies EXACTLY the keys the evidence emits",
          emitted == declared,
          f"unclassified {sorted(emitted - declared)}, stale {sorted(declared - emitted)}")
    check(f"unclassified = 0 (total {counts['total']})",
          len(emitted - declared) == 0, str(sorted(emitted - declared)))
    check("every class count is machine-derived and sums to the total",
          sum(counts[name] for name in AUTHORITY_CLASSES) == counts["total"]
          == len(emitted), str(counts))
    check("every declared class is one of the eight authority classes",
          all(row.authority_class in AUTHORITY_CLASSES
              for row in BRANCH_A_FIELD_AUTHORITY))
    check("there is no ambiguous catch-all: nothing is classified MEASURED that "
          "the plan, contract, seed map or planner fixes",
          set(EXTERNALLY_BOUND_EMBEDDED_FIELDS).isdisjoint(
              {row.field for row in BRANCH_A_FIELD_AUTHORITY
               if row.authority_class == AUTHORITY_MEASURED}))

    # --- §24: constructor source and verifier expectation agree --------------
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    expectations = embedded_authority_expectations(job, campaign.binding)
    for field, expected in sorted(expectations.items()):
        check(f"constructor stamps {field} and the verifier expects that same "
              f"value", evidence[field] == expected,
              f"{evidence[field]!r} vs {expected!r}")
    check("every class that fixes an exact value has an expectation derived",
          all(row.field in expectations for row in BRANCH_A_FIELD_AUTHORITY
              if row.authority_class in AUTHORITY_CLASSES_WITH_EXPECTED_VALUE),
          str(sorted(expectations)))
    campaign.close()

    # --- §10 / §14 / §17 / §18 / §19 / §26 / §27 / §28: the mutation audit ---
    campaign = Campaign()
    probe = campaign.job(C2)
    campaign.run(probe, terminal=False)
    mutations = list(authority_mutations(campaign, probe))
    campaign.close()
    covered = {field for _label, field, _value in mutations}
    check("the mutation audit covers EVERY externally bound field",
          covered == set(EXTERNALLY_BOUND_EMBEDDED_FIELDS),
          f"missing {sorted(set(EXTERNALLY_BOUND_EMBEDDED_FIELDS) - covered)}")

    tested = unexpected = 0
    by_class = {}
    for label, field, value in mutations:
        campaign = Campaign()
        job = campaign.job(C2)
        _execution, record, _digest = campaign.run(job)
        if field == "tau_modes":
            # Break the FROZEN PAIRING while keeping the same multiset: the taus
            # are carried with ascending stiffness, so reversing them to
            # non-decreasing order is a mispairing, not a different measurement.
            current = committed_publication(campaign.out, job.coordinates)[
                "branch_a_evidence"]["tau_modes"]
            value = sorted(current, key=lambda h: float.fromhex(h))
            if len(set(value)) == 1:
                # degenerate field: make it strictly increasing instead
                value = [current[0],
                         canonical_float(float.fromhex(current[0]) * 2.0)]
        publication = forge_embedded(campaign, job, field, value)
        lock = json.loads(json.dumps(
            committed_calibration_lock(campaign.out, job.coordinates)))
        for linked in ("publication_digest", "branch_a_evidence_sha256",
                       "calibration_condition_sha256"):
            lock[linked] = publication[linked]
        lock["lock_digest"] = sealed_digest(lock, "lock_digest")
        republish(calibration_lock_directory(campaign.out),
                  calibration_lock_basename(job.coordinates), lock, "lock_digest",
                  job.job_id, job.coordinates)
        forged = retied(record, publication, lock)
        tested += 1
        paths = {
            "shared verifier": refusal_code(verified_publication, campaign.out,
                                            job, campaign.binding),
            "terminal": refusal_code(validate_job_record, forged,
                                     campaign.binding.plan, campaign.binding,
                                     job, campaign.out),
            "restart": restart_refusal(campaign, [job]),
        }
        if any(v is None for v in paths.values()):
            unexpected += 1
        row = BRANCH_A_FIELD_AUTHORITY_BY_FIELD[field]
        by_class.setdefault(row.authority_class, 0)
        by_class[row.authority_class] += 1
        for path, got in paths.items():
            check(f"{row.authority_class} {label} forged, whole chain "
                  f"re-digested -> {path} refuses", got is not None,
                  f"got {got!r}")
        campaign.close()
    check(f"mutation audit: {tested} externally bound field(s) tested across "
          f"{len(by_class)} authority class(es), {unexpected} unexpected pass(es)",
          unexpected == 0 and tested == len(EXTERNALLY_BOUND_EMBEDDED_FIELDS),
          f"{tested} tested, {unexpected} unexpected, by class {by_class}")

    # --- §8 / §9 / §10: seeds, pinned, with the frozen shared-scope intact ---
    campaign = Campaign()
    a = campaign.job(C2, field_id=FIELDS[0])
    b = campaign.job(C2, field_id=FIELDS[1])
    campaign.run(a, terminal=False)
    campaign.run(b, terminal=False)
    ev_a = committed_publication(campaign.out, a.coordinates)["branch_a_evidence"]
    ev_b = committed_publication(campaign.out, b.coordinates)["branch_a_evidence"]
    check("the per-field Branch-A streams DIFFER between fields of one replicate",
          ev_a["branch_a_seed"] != ev_b["branch_a_seed"])
    check("but the COMMON-MODE stream is SHARED, exactly as the frozen model "
          "intends -- it cancels in P2 and not in P3",
          ev_a["common_mode_seed"] == ev_b["common_mode_seed"])
    check("and the verifier accepts that sharing rather than demanding a "
          "per-field common mode",
          refusal_code(verified_publication, campaign.out, a, campaign.binding)
          is None
          and refusal_code(verified_publication, campaign.out, b,
                           campaign.binding) is None)
    # the cross-job substitution: b's REAL seed placed in a's publication
    forge_embedded(campaign, a, "branch_a_seed", ev_b["branch_a_seed"])
    refuses_with_code(
        "another field's GENUINE authorised Branch-A seed, substituted",
        "BRANCH_A_PROVENANCE_MISMATCH", verified_publication, campaign.out, a,
        campaign.binding)
    campaign.close()

    # --- §15 / §16: the contract's route rule, both directions ---------------
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    contract = campaign.binding.binding
    check("the contract declares a closed authorised route set",
          len(contract.authorised_branch_a_routes) >= 1
          and len(contract.forbidden_branch_a_routes) >= 1,
          f"{list(contract.authorised_branch_a_routes)} / "
          f"{list(contract.forbidden_branch_a_routes)}")
    for route in contract.forbidden_branch_a_routes:
        campaign2 = Campaign()
        j = campaign2.job(C2)
        campaign2.run(j, terminal=False)
        forge_embedded(campaign2, j, "calibration_route", route)
        refuses_with_code(f"contract-FORBIDDEN route {route!r}",
                          "BRANCH_A_PROVENANCE_MISMATCH", verified_publication,
                          campaign2.out, j, campaign2.binding)
        campaign2.close()
    forge_embedded(campaign, job, "calibration_route", "a_route_nobody_declared")
    refuses_with_code("a route on neither contract list (closed world)",
                      "BRANCH_A_PROVENANCE_MISMATCH", verified_publication,
                      campaign.out, job, campaign.binding)
    campaign.close()
    for route in contract.authorised_branch_a_routes:
        campaign2 = Campaign()
        j = campaign2.job(C2)
        campaign2.run(j, terminal=False)
        forge_embedded(campaign2, j, "calibration_route", route)
        check(f"contract-AUTHORISED route {route!r} is accepted",
              refusal_code(verified_publication, campaign2.out, j,
                           campaign2.binding) is None)
        campaign2.close()

    # --- §20 / §38: MEASURED values stay observations, not constants ----------
    campaign = Campaign()
    measured = tuple(row.field for row in BRANCH_A_FIELD_AUTHORITY
                     if row.authority_class == AUTHORITY_MEASURED)
    check("the MEASURED set is exactly the realised Branch-A observations",
          measured == ("H_A", "T_measured", "k_modes_measured",
                       "rot_deg_measured", "scale_factor"), str(measured))
    check("no MEASURED field has an expectation derived for it -- none is "
          "compared with a predetermined number",
          all(f not in embedded_authority_expectations(
              campaign.job(C2), campaign.binding) for f in measured))
    temperatures = set()
    for field_id in FIELDS:
        j = campaign.job(C2, field_id=field_id)
        campaign.run(j, terminal=False)
        ev = committed_publication(campaign.out, j.coordinates)[
            "branch_a_evidence"]
        temperatures.add(ev["T_measured"])
        check(f"{field_id}: its realised measurement verifies",
              refusal_code(verified_publication, campaign.out, j,
                           campaign.binding) is None)
    check("measured temperatures genuinely differ across the contract fields, "
          "and all verify", len(temperatures) > 1, str(len(temperatures)))
    # A measured value changed ON ITS OWN is now an INCONSISTENT record, because
    # H_A is derived from the temperature. That is the joint-invariant repair
    # working; the "observations may vary" control needs a COMPLETE consistent
    # measurement and lives in group F1.
    j = campaign.job(C2, field_id=FIELDS[0])
    forge_embedded(campaign, j, "T_measured", canonical_float(297.5))
    refuses_with_code("a measured temperature changed ALONE leaves H_A "
                      "inconsistent with it", "BRANCH_A_MEASUREMENT_INVALID",
                      verified_publication, campaign.out, j, campaign.binding)
    # but its ENCODING is still enforced
    forge_embedded(campaign, j, "T_measured", "not-a-float")
    refuses_with_code("a malformed measured temperature", "PUBLICATION_INCOMPLETE",
                      verified_publication, campaign.out, j, campaign.binding)
    campaign.close()

    # --- §21 / §22: the OPEN field, classified and left open -----------------
    open_fields = tuple(row.field for row in BRANCH_A_FIELD_AUTHORITY
                        if row.authority_class == AUTHORITY_OPEN_UNRESOLVED)
    check("exactly one embedded field is OPEN_UNRESOLVED, and it is the "
          "generator identity", open_fields == ("generator_identity",),
          str(open_fields))
    check("no expectation is invented for it",
          "generator_identity" not in embedded_authority_expectations(
              Campaign().job(C2), BINDING) if True else False)
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    forge_embedded(campaign, job, "generator_identity", "ANOTHER-GENERATOR")
    check("a different non-empty generator identity is accepted, because its "
          "authority is genuinely unresolved",
          refusal_code(verified_publication, campaign.out, job, campaign.binding)
          is None)
    forge_embedded(campaign, job, "generator_identity", "")
    refuses_with_code("but an empty generator identity still refuses",
                      "PUBLICATION_INCOMPLETE", verified_publication,
                      campaign.out, job, campaign.binding)
    campaign.close()

    # --- §5: an UNDECLARED embedded field is an unauthenticated channel ------
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    coordinates = job.coordinates
    publication = json.loads(json.dumps(
        committed_publication(campaign.out, coordinates)))
    publication["branch_a_evidence"]["smuggled"] = "extra"
    publication["branch_a_evidence_sha256"] = canonical_digest(
        publication["branch_a_evidence"])
    publication["publication_digest"] = sealed_digest(publication,
                                                      "publication_digest")
    republish(publication_directory(campaign.out),
              publication_basename(coordinates), publication,
              "publication_digest", job.job_id, coordinates)
    refuses_with_code("an undeclared extra field inside the evidence",
                      "PUBLICATION_INCOMPLETE", verified_publication,
                      campaign.out, job, campaign.binding)
    campaign.close()

    # --- §38: the positive control, every contract field, every path ---------
    for field_id in FIELDS:
        campaign = Campaign()
        job = campaign.job(C2, field_id=field_id)
        _execution, record, _digest = campaign.run(job)
        publish_job_record(campaign.out, record, campaign.binding)
        check(f"{field_id}: constructor-produced publication -> verifier ACCEPTS",
              refusal_code(verified_publication, campaign.out, job,
                           campaign.binding) is None)
        check(f"{field_id}: -> terminal validation ACCEPTS",
              campaign.validate(job, record) is None,
              str(campaign.validate(job, record)))
        check(f"{field_id}: -> restart ACCEPTS",
              refusal_code(verify_restart, campaign.out, recovered(campaign),
                           campaign.binding, [job]) is None)
        campaign.close()


# ================ F1. the record as a WHOLE: domain and joint invariants
def forge_evidence(campaign, job, mutate):
    """Mutate the embedded evidence, then consistently recompute the evidence
    digest, the envelope digest and the commit marker."""
    coordinates = job.coordinates
    publication = json.loads(json.dumps(
        committed_publication(campaign.out, coordinates)))
    mutate(publication["branch_a_evidence"])
    publication["branch_a_evidence_sha256"] = canonical_digest(
        publication["branch_a_evidence"])
    publication["publication_digest"] = sealed_digest(publication,
                                                      "publication_digest")
    republish(publication_directory(campaign.out),
              publication_basename(coordinates), publication,
              "publication_digest", job.job_id, coordinates)
    return publication


def valid_measurement(job, k_modes, rot_deg, temperature, scale, gamma):
    """A COMPLETE, internally consistent, NON-NOMINAL Branch-A measurement.

    Built the way production builds one: H_A and the status come from a real
    `BranchAField`, and the relaxation times come from one shared gamma carried
    with ascending stiffness. `gamma` here is an arbitrary positive fixture
    value, never frozen authority -- the verifier only asks that ONE exists.
    """
    field = BranchAField(
        field_id=job.coordinates.scope, H_U=stiffness_matrix(k_modes, rot_deg),
        T=temperature, x_star=[0.0] * len(k_modes), k_modes=k_modes,
        rot_deg=rot_deg, viscosity=1.0, bead_radius=1.0,
        calibration_route="force_displacement_with_stokes_drag",
        scale_factor=scale)
    taus = tuple(gamma / k for k in k_modes)
    paired = tuple(t for _, t in sorted(zip(k_modes, taus)))

    def mutate(evidence):
        evidence["k_modes_measured"] = [canonical_float(v) for v in k_modes]
        evidence["rot_deg_measured"] = canonical_float(rot_deg)
        evidence["T_measured"] = canonical_float(temperature)
        evidence["scale_factor"] = canonical_float(scale)
        evidence["H_A"] = [[canonical_float(v) for v in row] for row in field.H]
        evidence["branch_a_status"] = field.status
        evidence["tau_modes"] = [canonical_float(t) for t in paired]

    return mutate


#: Valid measurements well away from the nominal contract values. If any of these
#: were rejected, the repair would have pinned observations to expectations.
NON_NOMINAL_MEASUREMENTS = (
    ("warmer, softer, rotated, scaled", (8.7e-5, 1.93e-4), 17.5, 301.44, 1.0037,
     1.6776e-8),
    ("cooler, stiffer, unrotated", (2.4e-4, 2.4e-4), 0.0, 288.13, 0.9912, 2.5e-8),
    ("strongly elliptic, large rotation", (5.1e-5, 3.3e-4), 42.7, 318.66, 1.05,
     9.1e-9),
    ("very small drag, unequal stiffness", (1.1e-4, 7.9e-5), 5.0, 297.0, 1.0,
     3.3e-12),
)


def test_branch_a_measurement_invariants() -> None:
    """AUDIT BLOCKER. Individually valid fields are not a valid measurement.

    Every field can pass its own authority check, the record can be correctly
    re-digested and durably committed, and the COMBINATION can still be one the
    production constructor could never have produced. A digest authenticates
    bytes; it does not prove they form a measurement.
    """
    # --- §26: the invariant inventory, and what each one covers --------------
    check("the invariant inventory declares every joint constraint",
          len(BRANCH_A_MEASUREMENT_INVARIANTS) == 5,
          str([i.invariant_id for i in BRANCH_A_MEASUREMENT_INVARIANTS]))
    dependents = {f for i in BRANCH_A_MEASUREMENT_INVARIANTS
                  for f in i.dependent_fields}
    derived = {row.field for row in BRANCH_A_FIELD_AUTHORITY
               if row.authority_class == AUTHORITY_DERIVED}
    # A DERIVED field is verified either by a joint measurement invariant or by a
    # recomputed expectation in the field-authority layer. `n_samples` takes the
    # second route: it is recomputed from the plan's own primitives.
    campaign0 = Campaign()
    recomputed = set(embedded_authority_expectations(campaign0.job(C2),
                                                     campaign0.binding))
    campaign0.close()
    uncovered = sorted(derived - dependents - recomputed)
    check("every DERIVED persisted field is covered, by an invariant or by a "
          "recomputed expectation", uncovered == [], f"uncovered {uncovered}")

    # --- §2 A / §14: H_A is derived, not independently choosable -------------
    campaign = Campaign()
    job = campaign.job(C2)
    _execution, record, _digest = campaign.run(job)
    forge_evidence(campaign, job, lambda e: e.__setitem__(
        "H_A", [[canonical_float(float.fromhex(v) * 1.5) for v in row]
                for row in e["H_A"]]))
    refuses_with_code(
        "H_A changed while the recorded stiffnesses, orientation, temperature "
        "and scale stayed exactly as published",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    check("   and restart refuses it",
          restart_refusal(campaign, [job]) == "BRANCH_A_MEASUREMENT_INVALID",
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # --- §2 B / §21 / §22: the relaxation relation ---------------------------
    # equal stiffness, unequal relaxation times
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta0_circular")   # k_1 == k_2
    campaign.run(job, terminal=False)
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    ks = [float.fromhex(v) for v in evidence["k_modes_measured"]]
    check("theta0_circular records EQUAL measured stiffnesses", ks[0] == ks[1],
          str(ks))
    forge_evidence(campaign, job, lambda e: e.__setitem__(
        "tau_modes", [e["tau_modes"][0],
                      canonical_float(float.fromhex(e["tau_modes"][0]) * 0.5)]))
    refuses_with_code(
        "equal stiffnesses, UNEQUAL relaxation times -- one gamma cannot do that",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    campaign.close()

    # unequal stiffness, order preserved, products broken. This is the case a
    # pairing-order check alone misses, which is why it is tested separately.
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")    # k_1 != k_2
    campaign.run(job, terminal=False)
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    ks = [float.fromhex(v) for v in evidence["k_modes_measured"]]
    taus = [float.fromhex(v) for v in evidence["tau_modes"]]
    check("theta2_ellipse records UNEQUAL measured stiffnesses", ks[0] != ks[1],
          str(ks))
    shrunk = [canonical_float(taus[0] * 0.8), evidence["tau_modes"][1]]
    check("the forged sequence is still NON-INCREASING, so the ordering rule "
          "alone would accept it",
          float.fromhex(shrunk[0]) >= float.fromhex(shrunk[1]))
    forge_evidence(campaign, job, lambda e: e.__setitem__("tau_modes", shrunk))
    refuses_with_code(
        "unequal stiffnesses, tau*k products broken while the order is preserved",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    check("   and restart refuses it",
          restart_refusal(campaign, [job]) == "BRANCH_A_MEASUREMENT_INVALID",
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # a SHUFFLED pairing, same multiset
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, lambda e: e.__setitem__(
        "tau_modes", list(reversed(e["tau_modes"]))))
    refuses_with_code("the relaxation times re-paired with the wrong stiffnesses",
                      "BRANCH_A_MEASUREMENT_INVALID", verified_publication,
                      campaign.out, job, campaign.binding)
    campaign.close()

    # --- §23: the POSITIVE relaxation control, at an arbitrary fixture gamma --
    check("one shared gamma over UNEQUAL stiffnesses is feasible",
          single_gamma_feasible((6.0e-5, 1.5e-4),
                                (1.6776104770169493e-08 / 6.0e-5,
                                 1.6776104770169493e-08 / 1.5e-4)))
    # Exact PRODUCT equality would have been the wrong test. Measured over real
    # production fixtures rather than asserted: for unequal stiffnesses the
    # products tau_r * k_r are not bit-identical, so a product-equality check
    # rejects genuine measurements while the interval test accepts them.
    product_mismatches = 0
    for _label, k_modes, rot_deg, temperature, scale, gamma in NON_NOMINAL_MEASUREMENTS:
        taus = tuple(gamma / k for k in k_modes)
        paired = tuple(t for _, t in sorted(zip(k_modes, taus)))
        ascending = sorted(k_modes)
        products = {t * k for t, k in zip(paired, ascending)}
        if len(products) > 1:
            product_mismatches += 1
        check(f"one shared gamma is feasible for {_label}",
              single_gamma_feasible(ascending, paired))
    check("and at least one genuine fixture has products that are NOT "
          "bit-identical, which is why exact product equality is the wrong test",
          product_mismatches >= 1, f"{product_mismatches} of "
          f"{len(NON_NOMINAL_MEASUREMENTS)}")

    # --- §2 C / §2 D / §8 / §9: measured-value domains ----------------------
    for field, label, value, expected in (
            ("T_measured", "= -1", canonical_float(-1.0),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("T_measured", "= 0", canonical_float(0.0),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("T_measured", "= NaN", float("nan").hex(),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("T_measured", "= +inf", float("inf").hex(),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("T_measured", "= -inf", float("-inf").hex(),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("scale_factor", "= -1", canonical_float(-1.0),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("scale_factor", "= 0", canonical_float(0.0),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("scale_factor", "= NaN", float("nan").hex(),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("scale_factor", "= +inf", float("inf").hex(),
             "BRANCH_A_MEASUREMENT_INVALID"),
            ("rot_deg_measured", "= NaN", float("nan").hex(),
             "BRANCH_A_MEASUREMENT_INVALID")):
        campaign = Campaign()
        job = campaign.job(C2)
        campaign.run(job, terminal=False)
        forge_evidence(campaign, job, lambda e, f=field, v=value: e.__setitem__(f, v))
        refuses_with_code(f"{field} {label}", expected, verified_publication,
                          campaign.out, job, campaign.binding)
        check(f"   and restart refuses {field} {label}",
              restart_refusal(campaign, [job]) is not None,
              str(restart_refusal(campaign, [job])))
        campaign.close()

    # --- §4 / §5: the production constructor's own domain rules, on read ------
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, lambda e: e.__setitem__(
        "H_A", [[e["H_A"][0][0], canonical_float(7.0)],
                [e["H_A"][1][0], e["H_A"][1][1]]]))
    refuses_with_code("an asymmetric published H_A", "BRANCH_A_MEASUREMENT_INVALID",
                      verified_publication, campaign.out, job, campaign.binding)
    campaign.close()

    # the status is DERIVED from the eigenvalues, not declared
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job,
                   lambda e: e.__setitem__("branch_a_status", "BRANCH_A_INVALID"))
    refuses_with_code("a declared status the primitives do not yield",
                      "BRANCH_A_MEASUREMENT_INVALID", verified_publication,
                      campaign.out, job, campaign.binding)
    campaign.close()

    # --- §39: every DERIVED field, changed alone with primitives fixed -------
    tested = unexpected = 0
    for row in BRANCH_A_FIELD_AUTHORITY:
        if row.authority_class != AUTHORITY_DERIVED:
            continue
        campaign = Campaign()
        job = campaign.job(C2, field_id="theta2_ellipse")
        campaign.run(job, terminal=False)
        evidence = committed_publication(campaign.out, job.coordinates)[
            "branch_a_evidence"]
        if row.field == "H_A":
            forged = [[canonical_float(float.fromhex(v) * 1.5) for v in r]
                      for r in evidence["H_A"]]
        elif row.field == "tau_modes":
            forged = [canonical_float(float.fromhex(evidence["tau_modes"][0]) * 0.8),
                      evidence["tau_modes"][1]]
        elif row.field == "branch_a_status":
            forged = "BRANCH_A_INVALID"
        elif row.field == "n_samples":
            forged = int(evidence["n_samples"]) + 1
        else:                                     # a newly DERIVED field
            forged = None
        tested += 1
        forge_evidence(campaign, job,
                       lambda e, f=row.field, v=forged: e.__setitem__(f, v))
        got = refusal_code(verified_publication, campaign.out, job,
                           campaign.binding)
        if got is None:
            unexpected += 1
        check(f"DERIVED {row.field} changed alone, primitives fixed -> refuses",
              got is not None, f"got {got!r}")
        campaign.close()
    check(f"derived-field audit: {tested} field(s) tested, {unexpected} "
          f"unexpected pass(es)", unexpected == 0 and tested == len(derived),
          f"{tested}/{unexpected}")

    # --- §12 / §15 / §38: POSITIVE controls, several valid realisations -------
    for label, k_modes, rot_deg, temperature, scale, gamma in NON_NOMINAL_MEASUREMENTS:
        campaign = Campaign()
        job = campaign.job(C2, field_id="theta2_ellipse")
        campaign.run(job, terminal=False)
        forge_evidence(campaign, job, valid_measurement(
            job, k_modes, rot_deg, temperature, scale, gamma))
        check(f"NON-NOMINAL valid measurement accepted: {label}",
              refusal_code(verified_publication, campaign.out, job,
                           campaign.binding) is None,
              str(refusal_code(verified_publication, campaign.out, job,
                               campaign.binding)))
        campaign.close()
    check("none of those measurements is the nominal contract state",
          all(temperature != 298.0 or scale != 1.0
              for _l, _k, _r, temperature, scale, _g in NON_NOMINAL_MEASUREMENTS))

    # every contract field's real production publication still verifies
    campaign = Campaign()
    for field_id in FIELDS:
        job = campaign.job(C2, field_id=field_id)
        _execution, record, _digest = campaign.run(job)
        check(f"{field_id}: the production publication verifies",
              refusal_code(verified_publication, campaign.out, job,
                           campaign.binding) is None)
        check(f"{field_id}: terminal validation ACCEPTS",
              campaign.validate(job, record) is None,
              str(campaign.validate(job, record)))
    campaign.close()

    # --- §31: previously cleared external-authority checks still refuse ------
    campaign = Campaign()
    job = campaign.job(C2)
    campaign.run(job, terminal=False)
    for label, field, value, expected in (
            ("embedded analysis identity", "analysis_identity", "a" * 64,
             "BRANCH_A_PROVENANCE_MISMATCH"),
            ("the Branch-A seed", "branch_a_seed", 1234567890123456789,
             "BRANCH_A_PROVENANCE_MISMATCH"),
            ("dt", "dt", canonical_float(0.00024),
             "BRANCH_A_PROVENANCE_MISMATCH"),
            ("the calibration route", "calibration_route",
             "equipartition_k_equals_kBT_over_sigma_squared",
             "BRANCH_A_PROVENANCE_MISMATCH")):
        campaign2 = Campaign()
        j = campaign2.job(C2)
        campaign2.run(j, terminal=False)
        forge_evidence(campaign2, j, lambda e, f=field, v=value: e.__setitem__(f, v))
        refuses_with_code(f"{label} still refuses (previously cleared)", expected,
                          verified_publication, campaign2.out, j, campaign2.binding)
        campaign2.close()
    campaign.close()


# ================================ A7. no science moved
def test_science_unchanged() -> None:
    """A provenance repair changes no scientific quantity."""
    jobs = plan_campaign(PLAN)
    check("the campaign is still 53,200 jobs", len(jobs) == 53200, str(len(jobs)))
    calibrating = sum(1 for j in jobs if j.requires_calibration)
    declared = sum(c["calibration_artifact_count"] for c in PLAN["cases"])
    check("the calibration artifact count is unchanged and matches the plan",
          calibrating == declared == 46000, f"{calibrating} vs {declared}")
    check("C7 and C8 still require no calibration",
          not any(j.requires_calibration for j in jobs
                  if j.coordinates.case_id in (C7, C8)))
    with open(os.path.join(ROOT, SEAL_JSON), encoding="utf-8") as handle:
        seal = json.load(handle)
    check("the execution seal is still PRE_DRIVER",
          seal["state"] == "PRE_DRIVER", str(seal["state"]))
    check("the final execution identity is still DELIBERATELY NOT FROZEN",
          seal["expected_execution_identity"] is None)
    check("execution is still not authorised",
          seal["execution_authorised"] is False)
    check("the seal still records zero draws and zero trajectories",
          seal["random_draws"] == 0 and seal["trajectories"] == 0,
          f"{seal['random_draws']} draws, {seal['trajectories']} trajectories")



# ---------------------------------------------------------------------------
# G1  THE RELAXATION DOMAIN: RECORDS PRODUCTION COULD NEVER HAVE WRITTEN
# ---------------------------------------------------------------------------
#: The three binary64 boundaries the interval arithmetic has to survive.
MAX_FINITE = 1.7976931348623157e308
MIN_SUBNORMAL = 5e-324
MIN_NORMAL = 2.2250738585072014e-308

#: An arbitrary POSITIVE fixture drag coefficient. Never frozen authority: the
#: verifier only ever asks whether SOME gamma exists, and this file must not
#: become the place an absolute gamma is chosen.
FIXTURE_GAMMA = 1.6776104770169493e-08


def production_record(k_modes, *, gamma=FIXTURE_GAMMA, temperature=300.0,
                      scale=1.0, rot_deg=0.0):
    """Run the REAL production path and report what it could actually write.

    Returns `(evidence, status, failure)`. `failure` is non-None exactly when
    production raises before a record exists -- which is the whole question the
    read verifier has to mirror. Nothing is asserted from intuition here: the
    constructor, the derived properties and the serializer are all executed.
    """
    try:
        field = BranchAField(
            field_id="parity", H_U=stiffness_matrix(k_modes, rot_deg),
            T=temperature, x_star=[0.0] * len(k_modes), k_modes=tuple(k_modes),
            rot_deg=rot_deg, viscosity=gamma / (6.0 * math.pi), bead_radius=1.0,
            calibration_route="force_displacement_with_stokes_drag",
            scale_factor=scale)
        paired = tuple(t for _, t in sorted(zip(k_modes, field.tau_modes)))
        evidence = {
            "field_id": "parity",
            "calibration_route": "force_displacement_with_stokes_drag",
            "k_modes_measured": [canonical_float(v) for v in k_modes],
            "rot_deg_measured": canonical_float(rot_deg),
            "T_measured": canonical_float(temperature),
            "scale_factor": canonical_float(scale),
            "H_A": [[canonical_float(v) for v in row] for row in field.H],
            "branch_a_status": field.status,
            "tau_modes": [canonical_float(t) for t in paired],
        }
        return evidence, field.status, None
    except Exception as exc:                      # noqa: BLE001 - classified below
        return None, None, f"{type(exc).__name__}: {exc}"


def forced_measurement(k_modes, taus, *, temperature=300.0, scale=1.0, rot_deg=0.0):
    """Set the primitives AND everything derived from them, leaving the
    relaxation tuple free.

    `valid_measurement` cannot express these cases: it computes tau from a shared
    gamma, so by construction it can only ever build a POSSIBLE record. An
    impossible one has to be stated directly.
    """
    field = BranchAField(
        field_id="forced", H_U=stiffness_matrix(k_modes, rot_deg), T=temperature,
        x_star=[0.0] * len(k_modes), k_modes=tuple(k_modes), rot_deg=rot_deg,
        viscosity=1.0, bead_radius=1.0,
        calibration_route="force_displacement_with_stokes_drag",
        scale_factor=scale)

    def mutate(evidence):
        evidence["k_modes_measured"] = [canonical_float(v) for v in k_modes]
        evidence["rot_deg_measured"] = canonical_float(rot_deg)
        evidence["T_measured"] = canonical_float(temperature)
        evidence["scale_factor"] = canonical_float(scale)
        evidence["H_A"] = [[canonical_float(v) for v in row] for row in field.H]
        evidence["branch_a_status"] = field.status
        evidence["tau_modes"] = [canonical_float(t) for t in taus]

    return mutate


def read_outcome(evidence):
    """ACCEPT, REFUSE[code], or UNCODED-<type>. Never raises."""
    try:
        require_branch_a_measurement_invariants(evidence, "g1")
        return "ACCEPT"
    except Refusal as exc:
        code = getattr(type(exc), "code", None)
        return f"REFUSE[{code}]" if code else f"UNCODED-Refusal"
    except Exception as exc:                      # noqa: BLE001 - that IS the defect
        return f"UNCODED-{type(exc).__name__}"


#: Representative constructor inputs spanning the stiffness domain. Whether each
#: is serializable is MEASURED by `production_record`, never declared here.
RELAXATION_DOMAIN_CASES = (
    ("ordinary positive, equal stiffnesses", (1.0e-4, 1.0e-4)),
    ("ordinary positive, unequal stiffnesses", (1.5e-4, 6.0e-5)),
    ("one negative stiffness", (-1.0e-4, 6.0e-5)),
    ("both stiffnesses negative", (-1.0e-4, -6.0e-5)),
    ("zero stiffness mixed with a real one", (0.0, 6.0e-5)),
    ("both stiffnesses zero", (0.0, 0.0)),
    ("negative zero stiffness", (-0.0, 6.0e-5)),
    ("very small nonzero stiffness", (1.0e-300, 6.0e-5)),
    ("large magnitude stiffness", (1.0e10, 6.0e-5)),
)


def test_branch_a_relaxation_domain() -> None:
    """AUDIT BLOCKER. A shared gamma must exist AND every division must be real.

    The previous repair asked whether some drag coefficient could produce the
    recorded relaxation times. That question is necessary but not sufficient: it
    is answerable for stiffness tuples the production constructor cannot divide
    by at all, and it was asked with interval arithmetic that was not total over
    the floats it accepted.
    """
    # --- §28: the invariant inventory records the realizability constraint ----
    ids = [i.invariant_id for i in BRANCH_A_MEASUREMENT_INVARIANTS]
    check("the invariant inventory declares the relaxation domain", len(ids) == 5,
          str(ids))
    check("RELAXATION_DOMAIN is one of them", "RELAXATION_DOMAIN" in ids, str(ids))

    # --- §4 / §5: what production ACTUALLY does at each stiffness -------------
    # Established by running the constructor, not by reading the formula.
    serializable = {}
    for label, k_modes in RELAXATION_DOMAIN_CASES:
        evidence, status, failure = production_record(k_modes)
        serializable[label] = evidence is not None
        if label == "both stiffnesses zero":
            check("PRODUCTION cannot serialize a zero stiffness at all",
                  evidence is None and "ZeroDivisionError" in failure, str(failure))
        if label == "one negative stiffness":
            check("PRODUCTION CAN serialize a negative stiffness, as "
                  "BRANCH_A_INVALID", evidence is not None
                  and status == "BRANCH_A_INVALID", str(status or failure))

    # The distinction the repair turns on, stated as an assertion rather than as
    # prose: negative is publishable, zero is not. Solving k == 0 by requiring a
    # positive stiffness would have erased a legitimate outcome.
    check("negative stiffness and zero stiffness are DIFFERENT production cases",
          serializable["one negative stiffness"]
          and not serializable["both stiffnesses zero"])

    # --- §17: the auditor's zero-stiffness counterexample --------------------
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, forced_measurement((0.0, 0.0), (1.0, 1.0)))
    refuses_with_code(
        "k = (0, 0) with tau = (1, 1) -- gamma = 0 is not a witness, because "
        "production cannot divide by zero under ANY gamma",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    check("   and restart refuses it with the measurement code",
          restart_refusal(campaign, [job]) == "BRANCH_A_MEASUREMENT_INVALID",
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # --- §18: a verifier that only special-cased (0, 0) would still be wrong --
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, forced_measurement((0.0, 6.0e-5), (1.0, 0.5)))
    refuses_with_code(
        "a zero stiffness MIXED with a real one still refuses",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    campaign.close()

    # --- §19: IEEE signed zero divides exactly as badly ----------------------
    check("-0.0 and 0.0 are the same divisor problem", -0.0 == 0.0)
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, forced_measurement((-0.0, 6.0e-5), (1.0, 0.5)))
    refuses_with_code(
        "a NEGATIVE zero stiffness refuses too",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    campaign.close()
    check("the feasibility predicate itself rejects a zero stiffness",
          not single_gamma_feasible((0.0, 0.0), (1.0, 1.0)))
    check("   and rejects a negative zero",
          not single_gamma_feasible((-0.0, 6.0e-5), (1.0, 0.5)))

    # --- §13 / §14 / §22: the interval routine is TOTAL and EXACT ------------
    # nextafter saturates to infinity at the outermost finite floats, and
    # Fraction(infinity) raises. The cell of MAX is still a finite rational
    # interval; 2**1024 is its exact outer endpoint, not a stand-in for infinity.
    lo, hi = _rounding_interval(MAX_FINITE)
    check("the rounding cell of the largest finite float is exact and finite",
          lo == Fraction(MAX_FINITE) - Fraction(2) ** 970
          and hi == _VIRTUAL_BINADE - Fraction(2) ** 970, f"{lo} {hi}")
    check("   and its upper endpoint IS the IEEE overflow threshold",
          hi == Fraction(2) ** 1024 - Fraction(2) ** 970)
    lo, hi = _rounding_interval(-MAX_FINITE)
    check("the cell of the most negative finite float is exact and finite",
          lo == -(_VIRTUAL_BINADE - Fraction(2) ** 970)
          and hi == Fraction(-MAX_FINITE) + Fraction(2) ** 970, f"{lo} {hi}")
    for label, value in (("zero", 0.0), ("smallest subnormal", MIN_SUBNORMAL),
                         ("smallest normal", MIN_NORMAL),
                         ("just below the smallest normal",
                          math.nextafter(MIN_NORMAL, 0.0))):
        lo, hi = _rounding_interval(value)
        check(f"the cell around the {label} is a proper exact interval",
              lo < Fraction(value) < hi or (value == 0.0 and lo < 0 < hi),
              f"{lo} {hi}")
    check("the cell of zero is symmetric across the subnormal boundary",
          _rounding_interval(0.0)[0] == -_rounding_interval(0.0)[1])
    check("no endpoint anywhere is an approximation: every one is a Fraction",
          all(isinstance(e, Fraction)
              for v in (MAX_FINITE, -MAX_FINITE, 0.0, MIN_SUBNORMAL, MIN_NORMAL)
              for e in _rounding_interval(v)))

    # --- §15 / §20: the largest finite relaxation time -----------------------
    # It is NOT rejected for being large. gamma = 6 pi eta a reaches MAX for
    # finite eta and a, so tau = MAX is production-realizable and must be read
    # back. The requirement was no UNCODED exception, not a rejection.
    reachable, _status, failure = production_record(
        (1.0, 2.0), gamma=MAX_FINITE, temperature=300.0)
    check("gamma = MAX is reachable from FINITE eta and a, so tau = MAX is "
          "production-realizable", reachable is not None, str(failure))
    check("   and its recorded relaxation times really are the largest finite "
          "float", reachable is not None
          and float.fromhex(reachable["tau_modes"][0]) == MAX_FINITE)
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job,
                   forced_measurement((1.0, 2.0), (MAX_FINITE, MAX_FINITE / 2.0)))
    outcome = read_outcome(committed_publication(
        campaign.out, job.coordinates)["branch_a_evidence"])
    check("tau = MAX raises NO uncoded exception (it used to be OverflowError)",
          not outcome.startswith("UNCODED"), outcome)
    check("   and it is ACCEPTED, because production can produce it",
          outcome == "ACCEPT", outcome)
    campaign.close()

    # --- §16: no raw numeric exception escapes the read verifier -------------
    # Each of these persists FINITE, individually well-formed primitives and
    # still names a record production could not have written.
    escapes = (
        ("H_U * scale / (K_B T) overflows to infinity",
         (1.0e300, 2.0e300), (1.0, 0.5), 1.0e-300, 1.0),
        ("K_B * T underflows to zero, so production's own division raises",
         (6.0e-5, 1.5e-4), (1.0, 0.5), MIN_SUBNORMAL, 1.0),
        ("a subnormal temperature above the smallest one, same failure",
         (6.0e-5, 1.5e-4), (1.0, 0.5), 1.0e-310, 1.0),
        ("the scale factor drives H_A out of range",
         (6.0e-5, 1.5e-4), (1.0, 0.5), 300.0, MAX_FINITE),
    )
    for label, k_modes, taus, temperature, scale in escapes:
        evidence = {
            "field_id": "escape",
            "calibration_route": "force_displacement_with_stokes_drag",
            "k_modes_measured": [canonical_float(v) for v in k_modes],
            "rot_deg_measured": canonical_float(0.0),
            "T_measured": canonical_float(temperature),
            "scale_factor": canonical_float(scale),
            "H_A": [[canonical_float(0.0)] * len(k_modes)] * len(k_modes),
            "branch_a_status": "VALID",
            "tau_modes": [canonical_float(t) for t in taus],
        }
        check(f"{label} -> coded refusal, not a raw exception",
              read_outcome(evidence) == "REFUSE[BRANCH_A_MEASUREMENT_INVALID]",
              read_outcome(evidence))

    # --- §23: constructor / read-verifier parity -----------------------------
    # For every representative input: if production can write the record, the
    # verifier must accept the UNTOUCHED produced record; if it cannot, the
    # equivalent forged record must refuse. One divergence is known, named and
    # deliberately left open -- see the gamma-sign item below.
    divergences = []
    for label, k_modes in RELAXATION_DOMAIN_CASES:
        evidence, _status, _failure = production_record(k_modes)
        if evidence is None:
            forged = dict(
                field_id="parity",
                calibration_route="force_displacement_with_stokes_drag",
                k_modes_measured=[canonical_float(v) for v in k_modes],
                rot_deg_measured=canonical_float(0.0),
                T_measured=canonical_float(300.0),
                scale_factor=canonical_float(1.0),
                H_A=[[canonical_float(0.0)] * len(k_modes)] * len(k_modes),
                branch_a_status="BRANCH_A_INVALID",
                tau_modes=[canonical_float(1.0) for _ in k_modes])
            check(f"production CANNOT write {label!r}; the forgery refuses",
                  read_outcome(forged) == "REFUSE[BRANCH_A_MEASUREMENT_INVALID]",
                  read_outcome(forged))
            continue
        outcome = read_outcome(evidence)
        check(f"no uncoded exception reading a produced record: {label}",
              not outcome.startswith("UNCODED"), outcome)
        if outcome != "ACCEPT":
            divergences.append((label, outcome))
    # The ONLY tolerated divergence is the negative-stiffness class, which the
    # verifier refuses because it requires a positive relaxation time -- i.e.
    # because it assumes gamma > 0. That assumption is NOT resolved here: eta and
    # a are undeclared in frozen authority, so the sign of gamma is an open
    # field-construction question and this check is left exactly as it was.
    check("the only production/read divergence is the negative-stiffness class",
          {label for label, _ in divergences}
          == {"one negative stiffness", "both stiffnesses negative"},
          str(divergences))

    # --- §24: positive controls; the exact method must not become strict -----
    for label, k_modes in (("unequal", (6.0e-5, 1.5e-4)),
                           ("equal", (1.0e-4, 1.0e-4)),
                           ("very small", (1.0e-300, 6.0e-5)),
                           ("large", (1.0e10, 6.0e-5))):
        for gamma in (FIXTURE_GAMMA, 1.0, 3.3e-12):
            ascending = sorted(k_modes)
            taus = tuple(gamma / k for k in ascending)
            check(f"a genuine shared gamma over {label} stiffnesses is feasible "
                  f"(gamma={gamma!r})", single_gamma_feasible(ascending, taus))

    # --- §25: the order-preserving forgery must STILL refuse -----------------
    # The case a pairing-order rule alone misses. Re-asserted here because the
    # domain clause added above must not have made the predicate coarser.
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    taus = [float.fromhex(v) for v in evidence["tau_modes"]]
    shrunk = [canonical_float(taus[0] * 0.8), evidence["tau_modes"][1]]
    check("the forged relaxation sequence is still correctly ORDERED",
          float.fromhex(shrunk[0]) >= float.fromhex(shrunk[1]))
    forge_evidence(campaign, job, lambda e: e.__setitem__("tau_modes", shrunk))
    refuses_with_code(
        "unequal stiffnesses, order preserved, common gamma broken -- still "
        "refused", "BRANCH_A_MEASUREMENT_INVALID", verified_publication,
        campaign.out, job, campaign.binding)
    campaign.close()

    # --- §8 / §30: no absolute gamma was chosen ------------------------------
    source = inspect.getsource(single_gamma_feasible)
    check("the feasibility predicate names no drag coefficient of its own",
          "6.0 * math.pi" not in source and "viscosity" not in source
          and "bead_radius" not in source)
    check("it decides EXISTENCE: the same stiffnesses are feasible at wildly "
          "different gammas",
          all(single_gamma_feasible((6.0e-5, 1.5e-4),
                                    (g / 6.0e-5, g / 1.5e-4))
              for g in (1e-12, 1e-8, 1.0, 1e8)))

    # --- §12: still no tolerance anywhere on this path -----------------------
    for fn in (single_gamma_feasible, _rounding_interval,
               require_branch_a_measurement_invariants):
        text = inspect.getsource(fn)
        check(f"{fn.__name__} introduces no epsilon or isclose",
              "isclose" not in text and "1e-6" not in text and "1e-9" not in text
              and "rtol" not in text and "atol" not in text)



# ---------------------------------------------------------------------------
# H1  THE SHARED DRAG VALUE MUST BE REPRESENTABLE, NOT MERELY REAL
# ---------------------------------------------------------------------------
#: The smallest positive binary64. Below it there are infinitely many positive
#: REALS and no positive float at all -- the whole of this group's subject.
SMALLEST_SUBNORMAL = 2.0 ** -1074
SMALLEST_NORMAL = 2.0 ** -1022


def gamma_region(stiffness, tau):
    """The exact real gamma interval one mode admits, as the verifier forms it."""
    lo, hi = _rounding_interval(tau)
    low, high = lo * Fraction(stiffness), hi * Fraction(stiffness)
    return (low, high) if low <= high else (high, low)


def scan_contains_binary64(lower, upper, lower_closed, upper_closed, anchor,
                           span=6):
    """An EXPLICIT walk over the floats around `anchor`, for cross-checking only.

    The verifier must never enumerate the float space; a test may, over a bounded
    neighbourhood, to confirm the closed-form helper agrees with the ground truth.
    """
    value = anchor
    for _ in range(span):
        value = math.nextafter(value, -math.inf)
    for _ in range(2 * span):
        if math.isinf(value):
            break
        exact = Fraction(value)
        if ((exact > lower or (lower_closed and exact == lower))
                and (exact < upper or (upper_closed and exact == upper))):
            return True
        value = math.nextafter(value, math.inf)
    return False


#: Representative finite drag values that production could actually hold, and
#: stiffness pairs spanning the checkable domain. Test data only: choosing one of
#: these as THE drag coefficient is exactly what this verifier must not do.
FIXTURE_GAMMAS = (SMALLEST_SUBNORMAL, SMALLEST_SUBNORMAL * 7, SMALLEST_NORMAL,
                  math.nextafter(SMALLEST_NORMAL, 0.0), 1e-300,
                  1.6776104770169493e-08, 3.3e-12, 1.0, 1e10, 1e300, _MAX_FINITE)
FIXTURE_STIFFNESSES = ((6.0e-5, 1.5e-4), (1.0e-4, 1.0e-4), (1.0e-300, 6.0e-5),
                       (1e10, 1.0), (2.0, 3.0), (1.0e-4, 9.7e-5))


def test_shared_drag_representability() -> None:
    """AUDIT BLOCKER. A real witness is not a production witness.

    The previous repair asked whether SOME real gamma satisfies every mode's
    rounding constraint. Production does not divide by a real number: the value
    reaching the division is a binary64, so a record whose solution region holds
    no representable value cannot have been produced, however non-empty that
    region is over the reals.
    """
    # --- §3: what actually enters the division -------------------------------
    # gamma is a rounded product chain, and the result is ONE float. Established
    # by executing it, not by reading the expression.
    field = BranchAField(
        field_id="drag", H_U=stiffness_matrix((6.0e-5, 1.5e-4), 0.0), T=300.0,
        x_star=[0.0, 0.0], k_modes=(6.0e-5, 1.5e-4), rot_deg=0.0,
        viscosity=0.00089, bead_radius=1e-6,
        calibration_route="force_displacement_with_stokes_drag")
    check("the production drag coefficient is a single binary64 value",
          isinstance(field.gamma, float) and math.isfinite(field.gamma))
    check("   and it is NOT the exact real 6*pi*eta*a: the product chain rounds",
          Fraction(field.gamma) != Fraction(6) * Fraction(math.pi)
          * Fraction(0.00089) * Fraction(1e-6))
    check("   so each recorded tau is fl(gamma_fp / k_fp)",
          field.tau_modes[0] == field.gamma / 6.0e-5)

    # --- §2 / §19: the auditor's counterexample ------------------------------
    low, high = gamma_region(1.0e-4, SMALLEST_SUBNORMAL)
    check("the 2**-1074 fixture DOES admit a real gamma", low <= high)
    check("   but its whole region lies below the smallest positive binary64",
          high < Fraction(SMALLEST_SUBNORMAL) and low > 0)
    check("   so a representable gamma does not exist",
          not interval_contains_binary64(low, high))
    check("   and the smallest representable gamma overshoots by far",
          SMALLEST_SUBNORMAL / 1.0e-4 > SMALLEST_SUBNORMAL)
    check("the feasibility predicate now refuses it",
          not single_gamma_feasible((1.0e-4, 1.0e-4),
                                    (SMALLEST_SUBNORMAL, SMALLEST_SUBNORMAL)))

    campaign = Campaign()
    job = campaign.job(C2, field_id="theta0_circular")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, forced_measurement(
        (1.0e-4, 1.0e-4), (SMALLEST_SUBNORMAL, SMALLEST_SUBNORMAL)))
    refuses_with_code(
        "k = (1e-4, 1e-4) with tau = (2**-1074, 2**-1074) -- no representable "
        "drag value produces it", "BRANCH_A_MEASUREMENT_INVALID",
        verified_publication, campaign.out, job, campaign.binding)
    check("   and restart refuses it with the measurement code",
          restart_refusal(campaign, [job]) == "BRANCH_A_MEASUREMENT_INVALID",
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # --- §10 / §11: the helper, cross-checked against an explicit scan -------
    # float(Fraction) rounds to NEAREST-EVEN, so it does not by itself give "the
    # smallest float at or above this rational". The correction is verified here
    # rather than assumed.
    for value in (1.0, 3.7e-5, SMALLEST_SUBNORMAL, SMALLEST_NORMAL, 1e300):
        exact = Fraction(value)
        check(f"smallest binary64 >= exact {value!r} is itself",
              _smallest_binary64_at_least(exact, strict=False) == value)
        check(f"smallest binary64 > exact {value!r} is its successor",
              _smallest_binary64_at_least(exact, strict=True)
              == math.nextafter(value, math.inf))
    combinations = 0
    disagreements = 0
    for anchor in (1.0, 0.5, 3.7e-5, SMALLEST_SUBNORMAL, SMALLEST_NORMAL,
                   math.nextafter(SMALLEST_NORMAL, 0.0), 1e300, _MAX_FINITE, 0.0,
                   1.6776104770169493e-08):
        successor = math.nextafter(anchor, math.inf)
        if math.isinf(successor):
            successor = anchor
        a, b = Fraction(anchor), Fraction(successor)
        endpoints = (a, b, (a * 2 + b) / 3, (a + b * 2) / 3, (a + b) / 2)
        for lower in endpoints:
            for upper in endpoints:
                if lower > upper:
                    continue
                for lower_closed in (True, False):
                    for upper_closed in (True, False):
                        combinations += 1
                        if (interval_contains_binary64(
                                lower, upper, lower_closed=lower_closed,
                                upper_closed=upper_closed)
                                != scan_contains_binary64(
                                    lower, upper, lower_closed, upper_closed,
                                    anchor)):
                            disagreements += 1
    check(f"the closed-form helper agrees with an explicit float walk on all "
          f"{combinations} interval/endpoint combinations", disagreements == 0,
          f"{disagreements} disagreements")

    # --- §21: real-nonempty, binary64-empty ---------------------------------
    one, successor = 1.0, math.nextafter(1.0, math.inf)
    inner_low = (Fraction(one) * 2 + Fraction(successor)) / 3
    inner_high = (Fraction(one) + Fraction(successor) * 2) / 3
    check("an interval strictly between two adjacent floats is non-empty over R",
          inner_low < inner_high)
    check("   and contains NO representable value",
          not interval_contains_binary64(inner_low, inner_high))

    # --- §20: the witness just above a fractional lower bound ---------------
    check("a lower bound between floats still finds the next representable one",
          interval_contains_binary64(inner_low, Fraction(successor)))
    check("   unless that endpoint is excluded",
          not interval_contains_binary64(inner_low, Fraction(successor),
                                         upper_closed=False))

    # --- §22: singleton intervals and endpoint semantics --------------------
    check("a closed singleton at a representable value is a witness",
          interval_contains_binary64(Fraction(one), Fraction(one)))
    check("   not with the lower endpoint open",
          not interval_contains_binary64(Fraction(one), Fraction(one),
                                         lower_closed=False))
    check("   not with the upper endpoint open",
          not interval_contains_binary64(Fraction(one), Fraction(one),
                                         upper_closed=False))
    check("an empty interval has no witness",
          not interval_contains_binary64(Fraction(3), Fraction(2)))

    # --- §13: the zero / subnormal boundary, which IS the audit finding -----
    check("an interval inside (0, 2**-1074) holds positive reals",
          Fraction(SMALLEST_SUBNORMAL) / 8 < Fraction(SMALLEST_SUBNORMAL) / 2)
    check("   and no positive representable value",
          not interval_contains_binary64(Fraction(SMALLEST_SUBNORMAL) / 8,
                                         Fraction(SMALLEST_SUBNORMAL) / 2))
    check("   while one reaching 2**-1074 does",
          interval_contains_binary64(Fraction(SMALLEST_SUBNORMAL) / 8,
                                     Fraction(SMALLEST_SUBNORMAL)))
    check("zero itself is representable",
          interval_contains_binary64(Fraction(0), Fraction(SMALLEST_SUBNORMAL) / 2))

    # --- §14: the subnormal/normal transition, where spacing changes --------
    check("the helper does not assume constant spacing across 2**-1022",
          interval_contains_binary64(
              Fraction(math.nextafter(SMALLEST_NORMAL, 0.0)),
              Fraction(SMALLEST_NORMAL)))
    check("   and finds nothing strictly inside that last subnormal gap",
          not interval_contains_binary64(
              (Fraction(math.nextafter(SMALLEST_NORMAL, 0.0)) * 2
               + Fraction(SMALLEST_NORMAL)) / 3,
              (Fraction(math.nextafter(SMALLEST_NORMAL, 0.0))
               + Fraction(SMALLEST_NORMAL) * 2) / 3))

    # --- §15: the large finite boundary is still handled --------------------
    check("no finite binary64 lies above the max-finite value",
          not interval_contains_binary64(Fraction(_MAX_FINITE) * 2,
                                         Fraction(_MAX_FINITE) * 4))
    check("   but an interval reaching max finite has it as a witness",
          interval_contains_binary64(Fraction(_MAX_FINITE),
                                     Fraction(_MAX_FINITE) * 2))

    # --- §23: ONE gamma must serve EVERY mode -------------------------------
    # Each mode alone admits a representable gamma. Their intersection is the
    # single point 1 + 2**-53, which is exactly a midpoint between adjacent
    # floats and therefore not representable. A verifier that asked each mode
    # separately would accept this.
    region_a = gamma_region(1.0, 1.0)
    region_b = gamma_region(2.0, math.nextafter(0.5, math.inf))
    check("mode A alone admits a representable gamma",
          interval_contains_binary64(*region_a))
    check("mode B alone admits a representable gamma",
          interval_contains_binary64(*region_b))
    joint_low, joint_high = max(region_a[0], region_b[0]), min(region_a[1],
                                                              region_b[1])
    check("their intersection is non-empty over the reals",
          joint_low <= joint_high)
    check("   and is exactly the non-representable midpoint 1 + 2**-53",
          joint_low == joint_high == Fraction(1) + Fraction(2) ** -53)
    check("so the SHARED requirement refuses the pair",
          not single_gamma_feasible((1.0, 2.0),
                                    (1.0, math.nextafter(0.5, math.inf))))

    # --- §18 / §33: ACTUAL production outputs must be accepted --------------
    accepted = tested = 0
    for gamma in FIXTURE_GAMMAS:
        for k_modes in FIXTURE_STIFFNESSES:
            ascending = sorted(k_modes)
            taus = tuple(gamma / stiffness for stiffness in ascending)
            if any(t == 0.0 or not math.isfinite(t) for t in taus):
                continue        # canonical_float refuses these; not serializable
            tested += 1
            if single_gamma_feasible(ascending, taus):
                accepted += 1
    check(f"every genuine production (gamma, k) tuple is accepted "
          f"({tested} tuples, subnormal through max-finite gamma)",
          tested == accepted and tested >= 40, f"{accepted}/{tested}")

    # --- §18: and end to end, through the shared read path ------------------
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    verified_publication(campaign.out, job, campaign.binding)
    check("an UNFORGED production publication is accepted by the shared verifier",
          True)
    check("   and restart accepts it",
          restart_refusal(campaign, [job]) is None,
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # --- §41 / §27 / §28: the four cleared repairs stay cleared -------------
    check("zero stiffness is still refused by the predicate",
          not single_gamma_feasible((0.0, 0.0), (1.0, 1.0)))
    check("   including negative zero",
          not single_gamma_feasible((-0.0, 6.0e-5), (1.0, 0.5)))
    check("max-finite tau is still handled without an uncoded exception, and "
          "still accepted", single_gamma_feasible((1.0, 2.0),
                                                  (_MAX_FINITE, _MAX_FINITE / 2)))
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    evidence = committed_publication(campaign.out, job.coordinates)[
        "branch_a_evidence"]
    taus = [float.fromhex(v) for v in evidence["tau_modes"]]
    shrunk = [canonical_float(taus[0] * 0.8), evidence["tau_modes"][1]]
    forge_evidence(campaign, job, lambda e: e.__setitem__("tau_modes", shrunk))
    refuses_with_code(
        "the order-preserving inconsistent tau tuple is still refused",
        "BRANCH_A_MEASUREMENT_INVALID", verified_publication, campaign.out, job,
        campaign.binding)
    campaign.close()

    # --- §29: the parity divergence count must NOT have moved ---------------
    divergences = []
    for label, k_modes in RELAXATION_DOMAIN_CASES:
        evidence, _status, _failure = production_record(k_modes)
        if evidence is None:
            continue
        if read_outcome(evidence) != "ACCEPT":
            divergences.append(label)
    check("the constructor/verifier parity divergence set is UNCHANGED: still "
          "exactly the negative-stiffness class",
          set(divergences) == {"one negative stiffness",
                               "both stiffnesses negative"}, str(divergences))

    # --- §5 / §25: no gamma was chosen, and none is persisted ---------------
    source = inspect.getsource(single_gamma_feasible)
    check("the predicate still names no drag coefficient of its own",
          "6.0 * math.pi" not in source and "viscosity" not in source
          and "bead_radius" not in source)
    check("the representability helper names none either",
          all(token not in inspect.getsource(interval_contains_binary64)
              for token in ("viscosity", "bead_radius", "6.0 * math.pi")))
    check("gamma is still absent from the published evidence schema",
          "gamma" not in BRANCH_A_FIELD_AUTHORITY_BY_FIELD)

    # --- §7: still no tolerance anywhere on the path ------------------------
    for fn in (single_gamma_feasible, interval_contains_binary64,
               _smallest_binary64_at_least, _rounding_interval):
        text = inspect.getsource(fn)
        check(f"{fn.__name__} introduces no epsilon or isclose",
              "isclose" not in text and "rtol" not in text and "atol" not in text
              and "1e-6" not in text and "1e-9" not in text)



# ---------------------------------------------------------------------------
# I1  IEEE-754 TIES TO EVEN: WHO OWNS AN EXACT MIDPOINT
# ---------------------------------------------------------------------------
M_SUB = 2.0 ** -1074            # smallest positive binary64; ODD significand


def rounds_to(exact, target):
    """Independent oracle: does this exact rational round to `target`?

    `float(Fraction)` performs a correctly-rounded, ties-to-even conversion, so
    this asks the question through a DIFFERENT mechanism than the bit-level
    parity rule under test.
    """
    try:
        return float(exact) == target
    except OverflowError:
        return False


def oracle_cell_closed(value):
    """Do BOTH exact midpoints round back to `value`? Ground truth for ownership."""
    lower, upper = _rounding_interval(value)
    return rounds_to(lower, value), rounds_to(upper, value)


def test_ties_to_even_midpoints() -> None:
    """AUDIT BLOCKER. A midpoint belongs to ONE neighbour, not to both.

    The rounding-cell endpoint LOCATIONS were right. Their OWNERSHIP was not:
    both were treated as included, so a drag value sitting exactly on a midpoint
    counted as a witness for a relaxation time that production's own division
    would never have produced from it.
    """
    # --- §2 / §33: the auditor's arithmetic, replayed ------------------------
    gamma = 3 * M_SUB
    check("3 * 2**-1074 is representable", Fraction(gamma) == 3 * Fraction(M_SUB))
    check("fl(3m / 2) is 2m, NOT m -- the tie at 1.5m goes to the even neighbour",
          gamma / 2.0 == 2 * M_SUB and gamma / 2.0 != M_SUB)
    check("fl(3m / 6) is 0, NOT m -- the tie at 0.5m goes to zero",
          gamma / 6.0 == 0.0 and gamma / 6.0 != M_SUB)
    check("so gamma = 3m produces NEITHER stored value",
          gamma / 2.0 != M_SUB and gamma / 6.0 != M_SUB)

    # --- §5: the ownership rule, and why one flag covers both endpoints -----
    check("the smallest positive subnormal has an ODD significand",
          not _significand_is_even(M_SUB))
    lower, upper, closed = _rounding_cell(M_SUB)
    check("   so its cell is OPEN at both ends", not closed)
    check("   its endpoints are still at m/2 and 3m/2",
          lower == Fraction(M_SUB) / 2 and upper == Fraction(M_SUB) * 3 / 2)
    check("adjacent floats always differ in significand parity, so a tie always "
          "resolves to exactly one of them",
          all(_significand_is_even(v) != _significand_is_even(
              math.nextafter(v, math.inf))
              for v in (0.0, M_SUB, 2 * M_SUB, 1.0, 0.5, 2.0, 1e300,
                        math.nextafter(2.0 ** -1022, 0.0), 2.0 ** -1022)))

    # --- §13: the midpoint goes to the ties-to-even winner, both directions --
    lower_wins = 1.0                      # even significand
    check("a midpoint whose LOWER neighbour is even rounds down",
          _significand_is_even(lower_wins)
          and rounds_to((Fraction(lower_wins)
                         + Fraction(math.nextafter(lower_wins, math.inf))) / 2,
                        lower_wins))
    upper_wins = math.nextafter(1.0, math.inf)          # odd
    beyond = math.nextafter(upper_wins, math.inf)       # even
    check("a midpoint whose UPPER neighbour is even rounds up",
          not _significand_is_even(upper_wins) and _significand_is_even(beyond)
          and rounds_to((Fraction(upper_wins) + Fraction(beyond)) / 2, beyond))

    # --- §19: bounded oracle cross-check of ownership ------------------------
    # The verifier stays non-enumerative; the TEST may walk a finite set and
    # compare the bit-level rule against correctly-rounded conversion.
    regions = {
        "zero / subnormal": [0.0, M_SUB, 2 * M_SUB, 3 * M_SUB, 4 * M_SUB,
                             5 * M_SUB, 17 * M_SUB],
        "subnormal / normal transition": [
            math.nextafter(2.0 ** -1022, 0.0), 2.0 ** -1022,
            math.nextafter(2.0 ** -1022, math.inf)],
        "ordinary normal": [1.0, math.nextafter(1.0, math.inf), 0.1, 0.2, 3.7e-5,
                            1.6776104770169493e-08, 123.456, 2.0, 3.0, 7.0],
        "power of two / binade edge": [
            0.5, math.nextafter(0.5, 0.0), 1.0, math.nextafter(1.0, 0.0), 2.0,
            math.nextafter(2.0, 0.0), 4.0, 2.0 ** 60,
            math.nextafter(2.0 ** 60, 0.0)],
        "large finite and max finite": [1e300, _MAX_FINITE,
                                        math.nextafter(_MAX_FINITE, 0.0)],
        "negative": [-1.0, -M_SUB, -2 * M_SUB, -_MAX_FINITE, -0.0],
    }
    for name, values in regions.items():
        disagreements = 0
        for value in values:
            low_closed, high_closed = oracle_cell_closed(value)
            _lo, _hi, rule = _rounding_cell(value)
            if not (low_closed == high_closed == rule):
                disagreements += 1
        check(f"ownership matches correctly-rounded conversion across {name} "
              f"({len(values)} values)", disagreements == 0,
              f"{disagreements} disagreements")
    walked = mismatched = 0
    for start, count in ((0.0, 400), (1.0, 400), (math.nextafter(2.0, 0.0), 60),
                         (math.nextafter(2.0 ** -1022, 0.0), 60)):
        value = start
        for _ in range(count):
            walked += 1
            low_closed, high_closed = oracle_cell_closed(value)
            _lo, _hi, rule = _rounding_cell(value)
            if not (low_closed == high_closed == rule):
                mismatched += 1
            value = math.nextafter(value, math.inf)
    check(f"and across {walked} CONSECUTIVE floats spanning the subnormals, the "
          f"binade edge and the normal/subnormal transition", mismatched == 0,
          f"{mismatched} mismatches")

    # --- §18: max finite still has no inf -> Fraction failure ---------------
    lo, hi, closed = _rounding_cell(_MAX_FINITE)
    check("the max-finite cell is still exact and finite",
          hi == VIRTUAL - Fraction(2) ** 970 and isinstance(lo, Fraction))
    check("   and max finite has an odd significand, so it is open",
          not closed and not _significand_is_even(_MAX_FINITE))

    # --- §9: a singleton intersection excluded by ONE contributor is empty ---
    cell_lo, cell_hi, _c = _rounding_cell(M_SUB)
    region_a = (cell_lo * Fraction(2.0), cell_hi * Fraction(2.0))
    region_b = (cell_lo * Fraction(6.0), cell_hi * Fraction(6.0))
    check("the two mode regions meet at exactly one point, 3m",
          region_a[1] == region_b[0] == 3 * Fraction(M_SUB))
    check("that point is representable, so CLOSED endpoints admit it",
          interval_contains_binary64(region_a[1], region_b[0]))
    check("but both contributors EXCLUDE it, so the intersection is empty",
          not interval_contains_binary64(region_a[1], region_b[0],
                                         lower_closed=False, upper_closed=False))
    check("   and one contributor excluding it is already enough",
          not interval_contains_binary64(region_a[1], region_b[0],
                                         lower_closed=False))
    check("the predicate refuses k = (2, 6) with tau = (m, m)",
          not single_gamma_feasible((2.0, 6.0), (M_SUB, M_SUB)))

    # --- §33: the permanent publication regression --------------------------
    campaign = Campaign()
    job = campaign.job(C2, field_id="theta2_ellipse")
    campaign.run(job, terminal=False)
    forge_evidence(campaign, job, forced_measurement((2.0, 6.0),
                                                     (M_SUB, M_SUB)))
    refuses_with_code(
        "k = (2, 6) with tau = (2**-1074, 2**-1074) -- gamma = 3m sits on a "
        "midpoint each mode rounds AWAY from", "BRANCH_A_MEASUREMENT_INVALID",
        verified_publication, campaign.out, job, campaign.binding)
    check("   and restart refuses it with the measurement code",
          restart_refusal(campaign, [job]) == "BRANCH_A_MEASUREMENT_INVALID",
          str(restart_refusal(campaign, [job])))
    campaign.close()

    # --- §11 / §12: the replay guard ----------------------------------------
    source = inspect.getsource(single_gamma_feasible)
    check("the predicate replays the witness through the REAL division",
          "witness / stiffness == tau" in source)
    check("   and does not search neighbouring floats on failure",
          "nextafter" not in source)
    witness = binary64_in_interval(*_rounding_cell(1.0)[:2])
    check("the witness helper returns an actual float, not just a verdict",
          isinstance(witness, float))
    check("   and that witness really does reproduce the stored value",
          witness / 1.0 == 1.0)

    # --- §22: genuine production tuples, including subnormal gamma ----------
    accepted = tested = 0
    for gamma in (M_SUB, 2 * M_SUB, 3 * M_SUB, 7 * M_SUB, 17 * M_SUB,
                  2.0 ** -1022, math.nextafter(2.0 ** -1022, 0.0), 1e-300,
                  1.6776104770169493e-08, 3.3e-12, 0.1, 1.0, 2.0, 1e10, 1e300,
                  _MAX_FINITE, math.nextafter(1.0, math.inf)):
        for k_modes in ((6.0e-5, 1.5e-4), (1.0e-4, 1.0e-4), (1.0e-300, 6.0e-5),
                        (1e10, 1.0), (2.0, 3.0), (1.0e-4, 9.7e-5), (2.0, 6.0),
                        (1.0, 1.0), (3.0, 7.0), (0.5, 0.25), (2.0 ** 60, 1.0)):
            ascending = sorted(k_modes)
            relaxations = tuple(gamma / k for k in ascending)
            if any(t == 0.0 or not math.isfinite(t) for t in relaxations):
                continue
            tested += 1
            if single_gamma_feasible(ascending, relaxations):
                accepted += 1
    check(f"every genuine production tuple is STILL accepted after tightening "
          f"({tested} tuples)", tested == accepted and tested >= 150,
          f"{accepted}/{tested}")
    # exhaustive over a contiguous run of subnormal drag values: the region the
    # tightening actually changed
    swept = lost = 0
    for multiple in range(1, 301):
        gamma = multiple * M_SUB
        for k_modes in ((2.0, 6.0), (1.0, 2.0), (3.0, 5.0), (0.5, 4.0)):
            ascending = sorted(k_modes)
            relaxations = tuple(gamma / k for k in ascending)
            if any(t == 0.0 for t in relaxations):
                continue
            swept += 1
            if not single_gamma_feasible(ascending, relaxations):
                lost += 1
    check(f"and every subnormal drag value from 1m to 300m still round-trips "
          f"({swept} tuples)", lost == 0, f"{lost} rejected")
    check("the neighbouring GENUINE records at k = (2, 6) are accepted",
          all(single_gamma_feasible((2.0, 6.0),
                                    ((n * M_SUB) / 2.0, (n * M_SUB) / 6.0))
              for n in (4, 6, 12)))

    # --- §20 / §21: the two previous drag fixes are not regressed -----------
    one, successor = 1.0, math.nextafter(1.0, math.inf)
    inner_low = (Fraction(one) * 2 + Fraction(successor)) / 3
    inner_high = (Fraction(one) + Fraction(successor) * 2) / 3
    check("real-nonempty but binary64-empty still has no witness",
          inner_low < inner_high
          and not interval_contains_binary64(inner_low, inner_high))
    check("the 2**-1074 representability case is still refused",
          not single_gamma_feasible((1.0e-4, 1.0e-4), (M_SUB, M_SUB)))
    check("the common-witness case is still refused",
          not single_gamma_feasible((1.0, 2.0),
                                    (1.0, math.nextafter(0.5, math.inf))))

    # --- §25: the domain repairs are regression-only ------------------------
    check("zero stiffness still refused", not single_gamma_feasible((0.0, 0.0),
                                                                    (1.0, 1.0)))
    check("mixed zero/nonzero still refused",
          not single_gamma_feasible((0.0, 6.0e-5), (1.0, 0.5)))
    check("max-finite tau still total and accepted",
          single_gamma_feasible((1.0, 2.0), (_MAX_FINITE, _MAX_FINITE / 2)))

    # --- §26: the open authority question is untouched ----------------------
    divergences = []
    for label, k_modes in RELAXATION_DOMAIN_CASES:
        evidence, _status, _failure = production_record(k_modes)
        if evidence is None:
            continue
        if read_outcome(evidence) != "ACCEPT":
            divergences.append(label)
    check("the parity divergence set is UNCHANGED: still exactly the "
          "negative-stiffness class",
          set(divergences) == {"one negative stiffness",
                               "both stiffnesses negative"}, str(divergences))

    # --- §23 / §24: no shortcut, no tolerance -------------------------------
    # Structural, not a word search: the docstring legitimately discusses why
    # product equality is the wrong test, so assert the interval path is intact.
    check("no product-equality shortcut replaced the interval logic",
          "_rounding_cell(" in source and "binary64_in_interval(" in source
          and "Fraction(stiffness)" in source)
    for fn in (single_gamma_feasible, _rounding_cell, _significand_is_even,
               binary64_in_interval, interval_contains_binary64,
               _smallest_binary64_at_least):
        text = inspect.getsource(fn)
        check(f"{fn.__name__} introduces no epsilon or isclose",
              "isclose" not in text and "rtol" not in text and "atol" not in text
              and "1e-6" not in text and "1e-9" not in text)


GROUPS = (
    ("A1  the auditor's two counterexamples", test_auditor_counterexamples),
    ("A2  every required case of the invariant", test_every_required_case),
    ("A3  the binding is EXTERNAL", test_binding_is_external),
    ("A4  C7 / C8 remain no-calibration paths", test_non_calibrating_cases_unchanged),
    ("A5  restart is never the weaker path", test_restart_uses_the_same_validator),
    ("A6  the valid round trip survives", test_valid_round_trip),
    ("B1  FINDING A: the caller cannot supply the lock",
     test_caller_cannot_supply_the_lock),
    ("B2  FINDING B: locks validate before any terminal exists",
     test_locks_validate_before_any_terminal_exists),
    ("B3  one verifier, no aliases, ordering preserved",
     test_one_verifier_and_no_aliases),
    ("C1  FINDING A: a committed publication is not a valid one",
     test_committed_publication_is_not_a_valid_one),
    ("C2  FINDING B: restart requires the canonical plan",
     test_restart_requires_the_canonical_plan),
    ("D1  embedded Branch-A identities bound to the package",
     test_embedded_identities_bound_to_package),
    ("E1  every embedded field verified against its authority",
     test_embedded_field_authority),
    ("F1  the record as a whole: domain and joint invariants",
     test_branch_a_measurement_invariants),
    ("G1  the relaxation domain: production realizability",
     test_branch_a_relaxation_domain),
    ("H1  the shared drag value must be representable",
     test_shared_drag_representability),
    ("I1  ties to even: who owns an exact midpoint",
     test_ties_to_even_midpoints),
    ("A7  no science moved", test_science_unchanged),
)

if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 terminal calibration provenance gate: {PASSED} passed, "
          f"{FAILED} failed, {len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    for line, value in (("REAL RNG OBJECTS", 0), ("REAL STOCHASTIC RANDOM DRAWS", 0),
                        ("OFFICIAL CAMPAIGN TRAJECTORIES", 0),
                        ("DETERMINISTIC TEST TRAJECTORIES", 0),
                        ("OFFICIAL CAMPAIGN JOBS", 0),
                        ("REAL CALIBRATION EXECUTIONS", 0)):
        print(f"  {line} {'.' * (32 - len(line))} {value}")
    raise SystemExit(1 if FAILED else 0)
