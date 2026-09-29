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
import os
import shutil
import tempfile

from e1a_v4.branch_a import build_field
from e1a_v4.calibration import CalibrationArtifact
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.campaign_driver import (
    CALIBRATION_LOCK_KEYS, CALIBRATION_LOCK_SCHEMA, JobCoordinates,
    calibration_lock_basename, calibration_lock_directory,
    _compare_terminal_to_verified_lock, calibration_lock_basename,
    calibration_lock_directory, calibration_lock_envelope,
    committed_calibration_lock, committed_publication, inventory_calibration_locks,
    inventory_job_records, is_sha256, job_execution, plan_campaign,
    publication_basename, publication_directory,
    publish_calibration_lock, publish_job_record, reconcile_calibration_locks,
    recover_realisations, validate_job_record, verified_calibration_lock,
    verify_restart,
)
from e1a_v4.validation.classification import GROSS_INFLATION_TOLERANCE
from e1a_v4.validation.dispositions import cp_upper
from e1a_v4.validation.plan import bind_execution
from e1a_v4.validation.publication import (
    commit_name, publish_transaction, read_published, sealed_digest,
)
from e1a_v4.validation.results import aggregate_skeleton
from e1a_v4.validation.scope import CampaignCalibrationLedger
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

    def run(self, job, *, aggregate=None, outcome=None):
        """Drive ONE job through the frozen dependency graph. No RNG, no draws."""
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
    check("and resolves the publication itself",
          "committed_publication(" in source)
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
