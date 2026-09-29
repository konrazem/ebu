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
    committed_calibration_lock, committed_publication, inventory_calibration_locks,
    inventory_job_records, is_sha256, job_execution, plan_campaign,
    publication_basename, publication_directory,
    publish_job_record, recover_realisations,
    require_calibration_artifact_binding, validate_job_record,
    verify_restart,
)
from e1a_v4.validation.classification import GROSS_INFLATION_TOLERANCE
from e1a_v4.validation.dispositions import cp_upper
from e1a_v4.validation.plan import bind_execution
from e1a_v4.validation.publication import (
    commit_name, read_published, sealed_digest,
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
        publication, lock = self.links(job.coordinates)
        return refusal_code(validate_job_record, record, self.binding.plan,
                            self.binding, job, publication, lock)

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


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
        campaign.binding, job, *campaign.links(job.coordinates))
    refuses_with_code(
        "B. calibration_artifact_sha256 = fabricated valid-looking SHA-256, "
        "RE-DIGESTED",
        "CALIBRATION_ARTIFACT_BINDING_INVALID", validate_job_record,
        mutated(record, "calibration_artifact_sha256", "f" * 64),
        campaign.binding.plan, campaign.binding, job,
        *campaign.links(job.coordinates))
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
                          publication, lock)

    # correct artifact SHA, but the artifact was never locked: no committed lock
    refuses_with_code("correct artifact SHA but artifact NOT locked",
                      "CALIBRATION_ARTIFACT_BINDING_INVALID", validate_job_record,
                      json.loads(json.dumps(record)), campaign.binding.plan,
                      campaign.binding, job, publication, None)
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
            campaign.binding.plan, campaign.binding, job, publication, lock)
        # and the new rule in the other direction: no lock may exist for it
        refuses_with_code(
            f"{case_id}: a calibration lock present for a no-calibration case",
            "CALIBRATION_ARTIFACT_BINDING_INVALID",
            require_calibration_artifact_binding, record, job,
            {"calibration_artifact_sha256": "a" * 64}, publication,
            campaign.binding)
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
        "CALIBRATION_ARTIFACT_BINDING_INVALID", verify_restart, campaign.out, {},
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
