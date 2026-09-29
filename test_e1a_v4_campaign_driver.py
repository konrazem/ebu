"""E1a v4 OFFICIAL CAMPAIGN DRIVER: planning, provenance and the unblind gate.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Planning, canonical
serialisation, hashing, filesystem publication and state transitions only.

THE STOCHASTIC SENTINEL
    `SentinelRNG` counts every construction and raises on every draw. Branch-A
    fields are built from the frozen contract WITHOUT measurement noise, and
    calibration artifacts are deterministic FIXTURES. The suite asserts at the end
    that no RNG object was constructed, no number drawn and no trajectory made.

WHAT THIS SUITE PROVES
    The frozen rule, stated identically in the working baseline, the prospective
    design and the design contract, is

        "Branch-A output is hashed and published BEFORE Branch B is unblinded."

    Every substitution the chain must refuse is exercised: wrong case, wrong
    subcondition, wrong replicate, wrong field, wrong seed identity, edited
    evidence, edited published hash, unpublished evidence, and a condition built
    from different Branch-A evidence. A numerically identical-looking condition is
    not enough where the frozen design requires provenance identity.
"""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import tempfile

from e1a_v4.branch_a import build_field
from e1a_v4.calibration import CalibrationArtifact, CalibrationCondition
from e1a_v4.contract import load_contract, sha256_file
from e1a_v4.numerics import Refusal
from e1a_v4.validation import PLAN_JSON, PLAN_MARKDOWN, SEED_MAP_JSON
from e1a_v4.validation.campaign_driver import (
    ANALYSED, BRANCH_A_PUBLICATION_DIR, BRANCH_A_PUBLISHED, BRANCH_A_REALIZED,
    BRANCH_B_UNBLINDED, CALIBRATION_CONDITION_BOUND, CALIBRATION_LOCKED,
    CAMPAIGN_MANIFEST_SCHEMA, PLANNED, RECORDED, BranchARealisation,
    BranchBUnblindToken, CampaignJob, JobCoordinates, JobExecution,
    campaign_manifest, campaign_shape, job_execution, main as driver_main,
    manifest_digest, plan_campaign, publication_path,
    replicate_calibration_for, require_plan_driver_agreement, run_campaign,
    verify_publication, verify_restart,
)
from e1a_v4.validation.driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, declared_entry_points, driver_exists,
    driver_identity_component, require_canonical_driver,
)
from e1a_v4.validation.plan import bind_execution, execution_identity, load_plan
from e1a_v4.validation.publication import (
    canonical_bytes, canonical_digest, canonical_json, publish_atomic,
    read_published,
)
from e1a_v4.validation.scope import CampaignCalibrationLedger
from e1a_v4.validation.seeds import EXPERIMENT_SCOPE, ValidationSeedFamily
from e1a_v4.validation.seal import SEAL_JSON
from e1a_v4.validation.strict_json import strict_load_file

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT_JSON = "docs/e1a/e1a_v4_design_contract.json"
PASSED = 0
FAILED = 0


class SentinelRNG:
    """Fails loudly if any real stochastic provider is requested or used."""

    CONSTRUCTED = 0
    DRAWS = 0

    def __init__(self) -> None:
        type(self).CONSTRUCTED += 1

    def normal(self, count: int) -> list[float]:
        type(self).DRAWS += 1
        raise AssertionError("SENTINEL: a random draw was attempted")


def real_rng_factory(seed: int) -> SentinelRNG:
    SentinelRNG.CONSTRUCTED += 1
    raise AssertionError("SENTINEL: a real RNG object was requested")


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
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
    before = (SentinelRNG.CONSTRUCTED, SentinelRNG.DRAWS)
    got = refusal_code(fn, *args, **kwargs)
    check(f"{label} -> {expected}",
          got == expected and (SentinelRNG.CONSTRUCTED, SentinelRNG.DRAWS) == before,
          f"got {got!r}")


COPIED = (CONTRACT_JSON, "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
          "docs/theory/EBU_THEORY_BASELINE.md",
          "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
          PLAN_JSON, SEED_MAP_JSON, PLAN_MARKDOWN, SEAL_JSON)


def sandbox() -> str:
    tmp = tempfile.mkdtemp()
    for rel in COPIED:
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), dst)
    shutil.copytree(os.path.join(ROOT, "e1a_v4"), os.path.join(tmp, "e1a_v4"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    return tmp


BINDING = bind_execution(ROOT)
PLAN = BINDING.plan
CONTRACT = load_contract(ROOT)
FIELDS = tuple(f["id"] for f in CONTRACT.fields)


# ------------------------------------------------------------------ fixtures
def noiseless_field(field_id: str):
    """A Branch-A field built from the CONTRACT with no measurement noise.

    The measurement-error model is deliberately not applied: applying it needs a
    generator, and this suite constructs none.
    """
    spec = next(f for f in CONTRACT.fields if f["id"] == field_id)
    return build_field(CONTRACT, spec,
                       calibration_route="force_displacement_with_stokes_drag",
                       viscosity=0.00089, bead_radius=1e-6)


def fixture_artifact(condition: CalibrationCondition) -> CalibrationArtifact:
    """A deterministic calibration artifact. No draws: the columns are arithmetic."""
    replicates = condition.replicates
    draws = {g: tuple(float(i + 1) / replicates for i in range(replicates))
             for g in condition.gates}
    return CalibrationArtifact(
        kind="block1_min_p", procedure_identity=condition.procedure_identity,
        field_id=condition.field_id, n=condition.n, m=condition.m,
        alpha_1=condition.alpha_1, null_draws=draws, condition=condition,
        schema=condition.canonical()["schema"], provenance="deterministic fixture",
        is_fixture=True)


def first_job(jobs, case_id: str, *, scope: str | None = None) -> CampaignJob:
    for job in jobs:
        if job.coordinates.case_id == case_id and (
                scope is None or job.coordinates.scope == scope):
            return job
    raise AssertionError(f"no planned job for {case_id}")


class Harness:
    """One sandboxed campaign root with a shared ledger and output directory."""

    def __init__(self) -> None:
        self.root = sandbox()
        self.binding = bind_execution(self.root)
        self.jobs = plan_campaign(self.binding.plan)
        self.ledger = CampaignCalibrationLedger()
        self.out = os.path.join(self.root, "results", "e1a_v4_validation")

    def execution(self, job: CampaignJob, calibration=None) -> JobExecution:
        return job_execution(self.binding, job, self.ledger, self.out, calibration)

    def realise(self, execution: JobExecution, field=None) -> BranchARealisation:
        coords = execution.coordinates
        cal = execution.calibration
        return execution.realise_branch_a(
            field or noiseless_field(coords.scope),
            branch_a_seed=cal.branch_a_seed(coords.scope),
            common_mode_seed=cal.common_mode_seed(),
            generator_identity="STATIC-FIXTURE-NO-DRAW")

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


# ----------------------------------------------- 1. the canonical declaration
def test_canonical_driver_present() -> None:
    check("the driver exists at the canonical declared path", driver_exists(ROOT),
          OFFICIAL_CAMPAIGN_DRIVER_PATH)
    check("the declared path is unchanged by this task",
          OFFICIAL_CAMPAIGN_DRIVER_PATH == "e1a_v4/validation/campaign_driver.py")
    check("the declared module is unchanged",
          OFFICIAL_CAMPAIGN_DRIVER_MODULE == "e1a_v4.validation.campaign_driver")
    entries = declared_entry_points(ROOT)
    check("the declared entry point is defined",
          OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT in entries,
          OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT)
    check("the entry point is found by AST parsing, with NOTHING imported",
          "run_campaign" in entries and "JobExecution" in entries)
    check("the canonical driver check now passes",
          refusal_code(require_canonical_driver, ROOT) is None)
    check("there is exactly one driver module",
          not os.path.exists(os.path.join(ROOT, "e1a_v4/validation/campaign_driver2.py")))
    component = driver_identity_component(ROOT)
    check("the driver contributes its file sha256, not the ABSENT sentinel",
          component != "ABSENT" and len(component) == 64, component[:16] + "...")
    check("it is the actual file hash",
          component == sha256_file(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH)))


def test_driver_identity_binding() -> None:
    """Changing the driver source must change the execution identity."""
    tmp = sandbox()
    plan_sha = sha256_file(os.path.join(tmp, PLAN_JSON))
    seed_sha = sha256_file(os.path.join(tmp, SEED_MAP_JSON))
    binding = load_contract(tmp)
    before = execution_identity(binding, plan_sha, seed_sha, tmp)
    path = os.path.join(tmp, OFFICIAL_CAMPAIGN_DRIVER_PATH)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n# provenance probe\n")
    after = execution_identity(binding, plan_sha, seed_sha, tmp)
    check("changing the driver source CHANGES the execution identity", before != after,
          f"{before[:12]}... -> {after[:12]}...")
    os.remove(path)
    absent = execution_identity(binding, plan_sha, seed_sha, tmp)
    check("removing the driver changes it again", absent not in (before, after))
    shutil.rmtree(tmp)
    check("the final expected execution identity is still NOT frozen",
          PLAN["frozen_identities"]["final_expected_execution_identity"] is None)


# ---------------------------------------------------- 2. deterministic planning
def test_campaign_planning() -> None:
    jobs = plan_campaign(PLAN)
    again = plan_campaign(PLAN)
    check("planning is RNG-free and deterministic",
          [j.as_dict() for j in jobs] == [j.as_dict() for j in again],
          f"{len(jobs)} jobs")
    check("every job identity is unique",
          len({j.job_id for j in jobs}) == len(jobs))
    shape = campaign_shape(PLAN)
    check("the shape is derived from the plan, case by case",
          sum(c["jobs"] for c in shape.values()) == len(jobs), str(len(jobs)))
    for case in PLAN["cases"]:
        cid = case["case_id"]
        expected = (len(case["subconditions"]) * case["replicate_count"]
                    * len(case["fields_affected"]))
        actual = sum(1 for j in jobs if j.coordinates.case_id == cid)
        check(f"{cid}: {expected} jobs planned", actual == expected, str(actual))
        # An independent cross-check the plan already carries.
        if case["requires_block1_calibration"]:
            check(f"{cid}: planned calibration jobs equal the plan's declared "
                  "calibration_artifact_count",
                  shape[cid]["calibration_jobs"] == case["calibration_artifact_count"],
                  f"{shape[cid]['calibration_jobs']} vs "
                  f"{case['calibration_artifact_count']}")
        else:
            check(f"{cid}: declares no calibration artifacts",
                  shape[cid]["calibration_jobs"] == 0 == case["calibration_artifact_count"])
    check("every job carries complete coordinates",
          all(j.coordinates.case_id and j.coordinates.subcondition_id
              and j.coordinates.replicate_id >= 0 and j.coordinates.scope
              for j in jobs))
    check("every job declares its seed families, calibration need and result kind",
          all(j.seed_families and j.result_kind and isinstance(j.requires_calibration, bool)
              for j in jobs))


def test_plan_driver_agreement() -> None:
    jobs = plan_campaign(PLAN)
    report = require_plan_driver_agreement(PLAN, jobs)
    check("missing planned jobs = 0", report["missing_planned_jobs"] == 0)
    check("extra driver jobs = 0", report["extra_driver_jobs"] == 0)
    check("planned and driver job counts agree",
          report["planned_jobs"] == report["driver_jobs"] == len(jobs),
          str(len(jobs)))
    # both directions genuinely discriminate
    refuses_with_code("a job dropped from the driver plan", "CAMPAIGN_PLAN_MISMATCH",
                      require_plan_driver_agreement, PLAN, jobs[:-1])
    extra = jobs + (CampaignJob(JobCoordinates("C1_true_bridge_complete", "sigma_psi_0p5",
                                               999999, "theta0_circular"),
                                "primary", True, ("validation",), ("theta0_circular",),
                                "complete_pass", ()),)
    refuses_with_code("an extra driver job", "CAMPAIGN_PLAN_MISMATCH",
                      require_plan_driver_agreement, PLAN, extra)
    shrunk = copy.deepcopy(PLAN)
    shrunk["cases"][0]["replicate_count"] -= 1
    refuses_with_code("the plan declaring fewer replicates than the driver planned",
                      "CAMPAIGN_PLAN_MISMATCH", require_plan_driver_agreement,
                      shrunk, jobs)


def test_parallel_order_invariance() -> None:
    """Scheduling order must not touch scientific identity."""
    jobs = plan_campaign(PLAN)
    forward = [j.job_id for j in jobs]
    reverse = [j.job_id for j in reversed(jobs)]
    permuted = [j.job_id for j in sorted(jobs, key=lambda j: j.coordinates.scope)]
    check("forward and reverse schedules carry the same job identities",
          sorted(forward) == sorted(reverse) == sorted(permuted), str(len(forward)))

    # seed identities are a pure function of coordinates, not of schedule order
    harness = Harness()
    sample = [first_job(jobs, c["case_id"]) for c in PLAN["cases"]]
    sample += [j for j in jobs if j.coordinates.case_id == "C8_blinded_scale_control"][:8]
    identities: dict[str, tuple] = {}
    for order in (sample, list(reversed(sample)),
                  sorted(sample, key=lambda j: j.coordinates.scope)):
        seen: dict[str, tuple] = {}
        for job in order:
            cal = replicate_calibration_for(harness.binding, job, CampaignCalibrationLedger())
            seen[job.job_id] = (cal.branch_a_seed(job.coordinates.scope),
                                cal.common_mode_seed())
        if not identities:
            identities = seen
        else:
            check("a permuted schedule derives identical seed identities",
                  seen == identities, f"{len(seen)} jobs")
    check("the first schedule produced seed identities at all", bool(identities))

    # result destinations are order-independent too
    paths = {j.job_id: publication_path(harness.out, j.coordinates) for j in sample}
    reversed_paths = {j.job_id: publication_path(harness.out, j.coordinates)
                      for j in reversed(sample)}
    check("publication destinations are a pure function of coordinates",
          paths == reversed_paths)
    harness.close()


# -------------------------------------------- 3. Branch-A evidence and its hash
def test_branch_a_realisation_and_hash() -> None:
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    execution = harness.execution(job)
    check("a fresh job starts PLANNED", execution.state == PLANNED)
    realisation = harness.realise(execution)
    check("realising Branch A advances the state",
          execution.state == BRANCH_A_REALIZED, execution.state)
    check("the evidence is bound to its complete coordinates",
          realisation.coordinates == job.coordinates)
    check("the evidence carries the realised Branch-A measurement",
          len(realisation.H_A) == 2 and realisation.T_measured > 0
          and len(realisation.tau_modes) == 2)
    check("it carries the package identities",
          realisation.contract_sha256 == harness.binding.binding.sha256
          and realisation.plan_sha256 == harness.binding.plan_sha256
          and realisation.analysis_identity == harness.binding.analysis_identity)
    check("it carries both Branch-A seed identities",
          isinstance(realisation.branch_a_seed, int)
          and isinstance(realisation.common_mode_seed, int))

    digest = realisation.evidence_sha256
    check("the evidence hash is deterministic",
          digest == realisation.evidence_sha256 == canonical_digest(realisation.canonical()),
          digest[:16] + "...")
    check("the hash is 64 hex characters", len(digest) == 64)

    # canonicalisation must not depend on accidents
    shuffled = dict(reversed(list(realisation.canonical().items())))
    check("the hash does not depend on dictionary iteration order",
          canonical_digest(shuffled) == digest)
    check("canonical JSON is sorted-key compact, ASCII, no NaN",
          canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}')
    check("a published file is canonical JSON plus exactly one LF",
          canonical_bytes({"a": 1}) == b'{"a":1}\n')

    # every scientific coordinate and every piece of evidence moves the hash
    for label, mutate in (
            ("case_id", lambda d: d["coordinates"].__setitem__("case_id", "C2_geometry_false_rejection")),
            ("subcondition_id", lambda d: d["coordinates"].__setitem__("subcondition_id", "sigma_psi_0p5")),
            ("replicate_id", lambda d: d["coordinates"].__setitem__("replicate_id", 1)),
            ("scope", lambda d: d["coordinates"].__setitem__("scope", "theta1_power")),
            ("H_A", lambda d: d["H_A"][0].__setitem__(0, "0x1.0p+0")),
            ("T_measured", lambda d: d.__setitem__("T_measured", "0x1.0p+8")),
            ("tau_modes", lambda d: d["tau_modes"].__setitem__(0, "0x1.0p+0")),
            ("branch_a_seed", lambda d: d.__setitem__("branch_a_seed", 1)),
            ("common_mode_seed", lambda d: d.__setitem__("common_mode_seed", 1)),
            ("scale_factor", lambda d: d.__setitem__("scale_factor", "0x1.0p+1")),
            ("plan_sha256", lambda d: d.__setitem__("plan_sha256", "0" * 64)),
            ("analysis_identity", lambda d: d.__setitem__("analysis_identity", "0" * 64))):
        canonical = copy.deepcopy(realisation.canonical())
        mutate(canonical)
        check(f"changing {label} changes the evidence hash",
              canonical_digest(canonical) != digest)

    refuses_with_code("evidence whose field disagrees with its scope",
                      "BRANCH_A_PROVENANCE_MISMATCH",
                      BranchARealisation, job.coordinates, "theta1_power",
                      *(getattr(realisation, f) for f in
                        ("branch_a_seed", "common_mode_seed", "H_A", "T_measured",
                         "k_modes_measured", "rot_deg_measured", "tau_modes",
                         "scale_factor", "n_samples", "dt", "calibration_route",
                         "branch_a_status", "contract_sha256", "plan_sha256",
                         "analysis_identity", "generator_identity")))
    harness.close()


def test_branch_a_seed_substitution_refuses() -> None:
    """Evidence from another stream is not this replicate's Branch-A measurement."""
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    cal = replicate_calibration_for(harness.binding, job, harness.ledger)
    other = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta1_power")
    wrong_seed = cal.branch_a_seed(other.coordinates.scope)

    execution = harness.execution(job, cal)
    refuses_with_code("a Branch-A seed identity from another field",
                      "BRANCH_A_PROVENANCE_MISMATCH",
                      execution.realise_branch_a,
                      noiseless_field("theta0_circular"),
                      branch_a_seed=wrong_seed,
                      common_mode_seed=cal.common_mode_seed(),
                      generator_identity="STATIC-FIXTURE-NO-DRAW")

    execution2 = harness.execution(job, cal)
    refuses_with_code("a common-mode identity that is not this experiment's",
                      "BRANCH_A_PROVENANCE_MISMATCH",
                      execution2.realise_branch_a,
                      noiseless_field("theta0_circular"),
                      branch_a_seed=cal.branch_a_seed("theta0_circular"),
                      common_mode_seed=cal.common_mode_seed() + 1,
                      generator_identity="STATIC-FIXTURE-NO-DRAW")
    harness.close()


# ------------------------------------------------------ 4. durable publication
def test_publication_primitive() -> None:
    directory = tempfile.mkdtemp()
    path = publish_atomic(directory, "probe.json", {"b": 2, "a": 1})
    check("publication creates the final path", os.path.isfile(path))
    check("the published file is read-only (0444)",
          (os.stat(path).st_mode & 0o777) == 0o444, oct(os.stat(path).st_mode & 0o777))
    check("no temporary alias survives publication",
          os.listdir(directory) == ["probe.json"], str(os.listdir(directory)))
    check("the bytes are canonical JSON plus one LF",
          open(path, "rb").read() == b'{"a":1,"b":2}\n')
    check("a published record reads back", read_published(path, "probe") == {"a": 1, "b": 2})
    refuses_with_code("publishing twice at the same final path", "PUBLICATION_COLLISION",
                      publish_atomic, directory, "probe.json", {"a": 1})

    # a truncated or appended record is not a record
    torn = os.path.join(directory, "torn.json")
    with open(torn, "wb") as handle:
        handle.write(b'{"a":1}')
    refuses_with_code("a record with no terminating LF", "PUBLICATION_INCOMPLETE",
                      read_published, torn, "torn")
    appended = os.path.join(directory, "appended.json")
    with open(appended, "wb") as handle:
        handle.write(b'{"a":1}\n{"a":2}\n')
    refuses_with_code("a record with appended bytes", "PUBLICATION_INCOMPLETE",
                      read_published, appended, "appended")
    refuses_with_code("a missing record", "PUBLICATION_INCOMPLETE",
                      read_published, os.path.join(directory, "absent.json"), "absent")

    # a leftover temporary is evidence of an interrupted publication
    leftover = os.path.join(directory, ".fresh.json.tmp")
    with open(leftover, "wb") as handle:
        handle.write(b"partial")
    refuses_with_code("publishing over a leftover temporary", "PUBLICATION_COLLISION",
                      publish_atomic, directory, "fresh.json", {"a": 1})
    shutil.rmtree(directory)


def test_branch_a_publication_and_immutability() -> None:
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    execution = harness.execution(job)
    realisation = harness.realise(execution)
    path = execution.publish_branch_a()
    check("publishing advances the state", execution.state == BRANCH_A_PUBLISHED)
    check("the publication lives under the campaign output directory",
          BRANCH_A_PUBLICATION_DIR in path and os.path.isfile(path))
    record = read_published(path, "branch A")
    check("the record binds the coordinates",
          record["coordinates"] == job.coordinates.as_dict())
    check("the record carries the evidence and its hash",
          record["branch_a_evidence_sha256"] == realisation.evidence_sha256
          == canonical_digest(record["branch_a_evidence"]))
    check("the record carries the calibration-condition identity",
          record["calibration_condition_sha256"]
          == realisation.calibration_condition(harness.binding).sha256)
    check("the record carries the package identities",
          record["package_identities"]["plan_sha256"] == harness.binding.plan_sha256)
    check("the record says it is not an execution authorisation",
          record["not_execution_authorisation"] is True)
    check("verification of the freshly published record passes",
          refusal_code(verify_publication, harness.out, realisation,
                       harness.binding) is None)

    # immutability
    refuses_with_code("republishing from the same execution", "JOB_STATE_INVALID",
                      execution.publish_branch_a)
    twin = harness.execution(job)
    harness.realise(twin)
    refuses_with_code("a second execution publishing the same coordinates",
                      "PUBLICATION_COLLISION", twin.publish_branch_a)
    check("the refused republication left the twin in BRANCH_A_REALIZED, not published",
          twin.state == BRANCH_A_REALIZED, twin.state)
    refuses_with_code("an explicit republish attempt", "BRANCH_A_PUBLICATION_IMMUTABLE",
                      execution.republish_branch_a, realisation)

    # edited evidence on disk is detected by recomputation
    for label, mutate, expected in (
            ("edited published EVIDENCE",
             lambda r: r["branch_a_evidence"].__setitem__("T_measured", "0x1.0p+8"),
             "BRANCH_A_EVIDENCE_ALTERED"),
            ("edited published HASH",
             lambda r: r.__setitem__("branch_a_evidence_sha256", "0" * 64),
             "BRANCH_A_EVIDENCE_ALTERED"),
            ("rebound coordinates",
             lambda r: r["coordinates"].__setitem__("replicate_id", 7),
             "BRANCH_A_PROVENANCE_MISMATCH"),
            ("a package identity changed after publication",
             lambda r: r["package_identities"].__setitem__("plan_sha256", "0" * 64),
             "BRANCH_A_PROVENANCE_MISMATCH")):
        tampered = copy.deepcopy(record)
        mutate(tampered)
        os.chmod(path, 0o600)
        with open(path, "wb") as handle:
            handle.write(canonical_bytes(tampered))
        os.chmod(path, 0o444)
        refuses_with_code(label, expected, verify_publication, harness.out,
                          realisation, harness.binding)
    os.chmod(path, 0o600)
    with open(path, "wb") as handle:
        handle.write(canonical_bytes(record))
    os.chmod(path, 0o444)
    check("restoring the record restores verification",
          refusal_code(verify_publication, harness.out, realisation,
                       harness.binding) is None)
    harness.close()


# ------------------------------------ 5. the condition comes from the evidence
def test_calibration_condition_derivation() -> None:
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    execution = harness.execution(job)
    realisation = harness.realise(execution)
    execution.publish_branch_a()
    condition = execution.calibration_condition()
    check("deriving the condition advances the state",
          execution.state == CALIBRATION_CONDITION_BOUND)
    check("the condition is derived from THIS realisation",
          condition.sha256 == realisation.calibration_condition(harness.binding).sha256)
    check("the condition names the same field", condition.field_id == job.coordinates.scope)
    check("the condition takes n and dt from the frozen generating model",
          condition.n == PLAN["generating_model"]["branch_b"]["n_samples"]
          and condition.dt == PLAN["generating_model"]["branch_b"]["dt_s"])
    check("the condition takes alpha_1 and theta_cap from the frozen rules",
          condition.alpha_1 == PLAN["adopted_rules_unchanged"]["alpha_1"]
          and condition.theta_cap_deg == PLAN["adopted_rules_unchanged"]["theta_cap_deg"])
    check("the condition takes R_cal from the frozen calibration block",
          condition.replicates == PLAN["calibration"]["replicates"])
    check("phi agrees with exp(-dt/tau) for every mode",
          all(math.isclose(p, math.exp(-condition.dt / t), rel_tol=1e-12)
              for p, t in zip(condition.phi_modes, condition.tau_modes)))

    # a condition built from DIFFERENT Branch-A evidence has a different identity
    other_job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta1_power")
    other_exec = harness.execution(other_job)
    other = harness.realise(other_exec)
    check("a condition from another field's evidence differs",
          other.calibration_condition(harness.binding).sha256 != condition.sha256)
    check("the difference is diagnosable",
          condition.first_difference(other.calibration_condition(harness.binding))
          is not None)

    # the public interface does not accept an externally prepared condition
    check("JobExecution exposes no way to supply a CalibrationCondition",
          "condition" not in JobExecution.lock_calibration.__code__.co_varnames[:2],
          str(JobExecution.lock_calibration.__code__.co_varnames[:3]))
    check("the calibration stream is unreachable before the condition is bound",
          refusal_code(harness.execution(other_job).calibration_seed) == "JOB_STATE_INVALID")
    harness.close()


def test_cross_coordinate_substitution_refuses() -> None:
    """A condition or artifact from other coordinates must never be accepted."""
    harness = Harness()
    base = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    cal = replicate_calibration_for(harness.binding, base, harness.ledger)
    execution = harness.execution(base, cal)
    harness.realise(execution)
    execution.publish_branch_a()
    condition = execution.calibration_condition()

    substitutes = {
        "wrong case": JobCoordinates("C2_geometry_false_rejection",
                                     base.coordinates.subcondition_id, 0, "theta0_circular"),
        "wrong subcondition": JobCoordinates(base.coordinates.case_id, "sigma_psi_0p5",
                                             0, "theta0_circular"),
        "wrong replicate": JobCoordinates(base.coordinates.case_id,
                                          base.coordinates.subcondition_id, 1,
                                          "theta0_circular"),
        "wrong field": JobCoordinates(base.coordinates.case_id,
                                      base.coordinates.subcondition_id, 0, "theta1_power"),
    }
    base_path = publication_path(harness.out, base.coordinates)
    for label, coordinates in substitutes.items():
        assert coordinates != base.coordinates, (
            f"{label!r} substitute equals the base coordinates; the probe would "
            "pass vacuously")
        job = next(j for j in harness.jobs if j.coordinates == coordinates)
        other_cal = replicate_calibration_for(harness.binding, job,
                                              CampaignCalibrationLedger())
        other = harness.execution(job, other_cal)
        foreign = harness.realise(other)
        check(f"{label}: its Branch-A evidence hash differs",
              foreign.evidence_sha256 != execution._realisation.evidence_sha256)
        check(f"{label}: its publication path differs from the base path",
              publication_path(harness.out, coordinates) != base_path)
        # The path is a pure function of the coordinates, so foreign evidence can
        # never be read as if it belonged to these coordinates: there is simply no
        # record there. That is a stronger protection than a comparison.
        refuses_with_code(f"{label}: no published record exists for it",
                          "PUBLICATION_INCOMPLETE", verify_publication,
                          harness.out, foreign, harness.binding)

    # SAME coordinates, DIFFERENT evidence: the substitution that a shared path
    # would otherwise permit. `theta1_power` differs from `theta0_circular` only in
    # stiffness, so the two conditions look alike without being the same evidence.
    class _Swapped(BranchARealisation):
        pass
    swapped_source = noiseless_field("theta1_power")
    swapped = BranchARealisation.from_branch_a_field(
        base.coordinates,
        type(swapped_source)(**{**swapped_source.__dict__,
                                "field_id": base.coordinates.scope}),
        branch_a_seed=cal.branch_a_seed(base.coordinates.scope),
        common_mode_seed=cal.common_mode_seed(),
        n_samples=harness.binding.plan["generating_model"]["branch_b"]["n_samples"],
        dt=harness.binding.plan["generating_model"]["branch_b"]["dt_s"],
        binding=harness.binding, generator_identity="STATIC-FIXTURE-NO-DRAW")
    check("substituted evidence at the SAME coordinates has a different hash",
          swapped.evidence_sha256 != execution._realisation.evidence_sha256)
    refuses_with_code("substituted Branch-A evidence at the same coordinates",
                      "BRANCH_A_EVIDENCE_ALTERED", verify_publication,
                      harness.out, swapped, harness.binding)
    refuses_with_code("an artifact from that substituted evidence, locked here",
                      "BRANCH_A_PROVENANCE_MISMATCH", execution.lock_calibration,
                      fixture_artifact(swapped.calibration_condition(harness.binding)))

    # an artifact calibrated for another field is refused at lock time
    other_job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta1_power")
    other = harness.execution(other_job, cal)
    harness.realise(other)
    other.publish_branch_a()
    other_condition = other.calibration_condition()
    refuses_with_code("an artifact built for another field, locked here",
                      "BRANCH_A_PROVENANCE_MISMATCH", execution.lock_calibration,
                      fixture_artifact(other_condition))
    check("the refused lock left the job in CALIBRATION_CONDITION_BOUND",
          execution.state == CALIBRATION_CONDITION_BOUND, execution.state)

    # edited evidence: the condition no longer matches the artifact
    edited = fixture_artifact(condition)
    check("the matching artifact locks cleanly",
          refusal_code(execution.lock_calibration, edited) is None
          and execution.state == CALIBRATION_LOCKED)
    harness.close()


# --------------------------------------------- 6. the Branch-B unblind boundary
def test_branch_b_requires_publication_and_lock() -> None:
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")

    # (a) before anything
    execution = harness.execution(job)
    refuses_with_code("Branch-B seed in state PLANNED", "BRANCH_B_PREMATURE",
                      execution.branch_b_seed)
    refuses_with_code("unblinding before Branch A is realised", "BRANCH_A_NOT_PUBLISHED",
                      execution.unblind)

    # (b) realised but NOT published
    harness.realise(execution)
    refuses_with_code("Branch-B seed after realisation, before publication",
                      "BRANCH_B_PREMATURE", execution.branch_b_seed)
    refuses_with_code("unblinding before publication", "BRANCH_A_NOT_PUBLISHED",
                      execution.unblind)

    # (c) published but calibration NOT locked
    execution.publish_branch_a()
    refuses_with_code("Branch-B seed after publication, before the calibration lock",
                      "BRANCH_B_PREMATURE", execution.branch_b_seed)
    refuses_with_code("unblinding before the calibration lock", "JOB_STATE_INVALID",
                      execution.unblind)

    # (d) condition bound and artifact locked -> eligible
    condition = execution.calibration_condition()
    execution.lock_calibration(fixture_artifact(condition))
    token = execution.unblind()
    check("unblinding yields a token", isinstance(token, BranchBUnblindToken))
    check("the state is BRANCH_B_UNBLINDED", execution.state == BRANCH_B_UNBLINDED)
    check("the token names the exact evidence it was issued against",
          token.branch_a_evidence_sha256 == execution._realisation.evidence_sha256)
    check("the token names the calibration condition and artifact",
          token.calibration_condition_sha256 == condition.sha256
          and token.calibration_artifact_sha256 is not None)
    seed = execution.branch_b_seed()
    check("only now is a Branch-B stream identity obtainable", isinstance(seed, int))
    check("deriving it constructed NO generator and drew NO number",
          SentinelRNG.CONSTRUCTED == 0 and SentinelRNG.DRAWS == 0)

    # ordering is structural: the underlying boundary agrees
    check("the same seed comes from the frozen scope machinery",
          seed == execution.calibration.validation_seed("theta0_circular",
                                                        ValidationSeedFamily.VALIDATION))
    harness.close()


def test_state_machine_transitions() -> None:
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    execution = harness.execution(job)
    refuses_with_code("publishing before realising", "BRANCH_A_NOT_PUBLISHED",
                      execution.publish_branch_a)
    harness.realise(execution)
    refuses_with_code("realising twice", "JOB_STATE_INVALID",
                      harness.realise, execution)
    refuses_with_code("binding the condition before publication", "JOB_STATE_INVALID",
                      execution.calibration_condition)
    execution.publish_branch_a()
    refuses_with_code("locking before the condition is derived", "JOB_STATE_INVALID",
                      execution.lock_calibration,
                      fixture_artifact(
                          execution._realisation.calibration_condition(harness.binding)))
    condition = execution.calibration_condition()
    refuses_with_code("analysing before unblinding", "BRANCH_B_PREMATURE",
                      execution.analyse, {"complete_pass": True})
    execution.lock_calibration(fixture_artifact(condition))
    execution.unblind()
    execution.branch_b_seed()
    execution.analyse({"complete_pass": True})
    check("analysis advances to ANALYSED", execution.state == ANALYSED)
    refuses_with_code("unblinding again after analysis", "JOB_STATE_INVALID",
                      execution.unblind)
    harness.close()


# ------------------------------------------ 7. case semantics the plan fixes
def test_c7_and_c8_have_no_calibration_dependency() -> None:
    harness = Harness()
    for case_id in ("C7_false_bridge", "C8_blinded_scale_control"):
        job = first_job(harness.jobs, case_id)
        check(f"{case_id}: the driver asks the plan and gets requires_calibration=False",
              job.requires_calibration is False)
        execution = harness.execution(job)
        harness.realise(execution)
        execution.publish_branch_a()
        refuses_with_code(f"{case_id}: asking for a calibration condition",
                          "JOB_STATE_INVALID", execution.calibration_condition)
        refuses_with_code(f"{case_id}: asking for a calibration stream",
                          "JOB_STATE_INVALID", execution.calibration_seed)
        token = execution.unblind()
        check(f"{case_id}: publication ALONE is the frozen prerequisite",
              token.calibration_condition_sha256 is None
              and token.calibration_artifact_sha256 is None)
        seed = execution.branch_b_seed()
        check(f"{case_id}: the Branch-B stream is obtainable after publication",
              isinstance(seed, int))
    harness.close()


def test_c7_alternatives_scheduled_exactly() -> None:
    jobs = plan_campaign(PLAN)
    c7 = [j for j in jobs if j.coordinates.case_id == "C7_false_bridge"]
    declared = [s["subcondition_id"] for s in
                next(c for c in PLAN["cases"] if c["case_id"] == "C7_false_bridge")
                ["subconditions"]]
    scheduled = sorted({j.coordinates.subcondition_id for j in c7})
    check("the driver schedules exactly the frozen alternatives",
          scheduled == sorted(declared), str(scheduled))
    check("there are exactly four", len(declared) == 4)
    for alternative in declared:
        count = sum(1 for j in c7 if j.coordinates.subcondition_id == alternative)
        check(f"C7 {alternative}: R x fields jobs, never pooled", count == 400 * 4,
              str(count))
    check("C7's result kind is false-bridge acceptance",
          {j.result_kind for j in c7} == {"false_bridge_acceptance"})
    check("C7 is a negative control", {j.role for j in c7} == {"negative_control"})


def test_c8_pairing_shares_one_underlying_replicate() -> None:
    harness = Harness()
    c8 = [j for j in harness.jobs if j.coordinates.case_id == "C8_blinded_scale_control"]
    check("C8 declares exactly one subcondition",
          len({j.coordinates.subcondition_id for j in c8}) == 1)
    replicates = {j.coordinates.replicate_id for j in c8}
    check("C8 schedules R replicates, not R per scale factor",
          len(replicates) == 200, str(len(replicates)))
    check("C8 jobs are R x fields, with NO job per scale factor",
          len(c8) == 200 * 4, str(len(c8)))
    factors = next(c for c in PLAN["cases"]
                   if c["case_id"] == "C8_blinded_scale_control")["subconditions"][0][
                       "scale_factors"]
    check("the two frozen factors are read from the plan", factors == [1.07, 0.9])

    # one underlying Branch-A realisation; the two branches are a deterministic
    # transform of it, not independent experiments
    job = first_job(harness.jobs, "C8_blinded_scale_control")
    execution = harness.execution(job)
    realisation = harness.realise(execution)
    base = noiseless_field(job.coordinates.scope)
    branches = {c: base.blinded(c) for c in factors}
    check("both blinded branches derive from the SAME underlying field",
          all(b.H_U == base.H_U and b.T == base.T for b in branches.values()))
    check("they differ only by the frozen scale factor",
          {round(b.scale_factor / base.scale_factor, 12) for b in branches.values()}
          == {round(c, 12) for c in factors})
    check("the underlying true bridge is unchanged by blinding",
          all(b.k_modes == base.k_modes and b.rot_deg == base.rot_deg
              for b in branches.values()))
    check("one published Branch-A evidence record serves the paired control",
          realisation.coordinates == job.coordinates)
    check("C8 uses its own blinded_scale_control Branch-B family",
          "blinded_scale_control" in job.seed_families)
    harness.close()


def test_c3_secondary_diagnostic_isolated() -> None:
    case = next(c for c in PLAN["cases"] if c["case_id"] == "C3_g5_block")
    jobs = [j for j in plan_campaign(PLAN) if j.coordinates.case_id == "C3_g5_block"]
    check("C3's primary release endpoint is the G5 / Block-2 size",
          case["primary_release_endpoint"] == "G5_BLOCK_SIZE")
    check("the driver's result kind is the G5 block rejection, not the joint P1",
          {j.result_kind for j in jobs} == {"g5_block_rejection"}, str(jobs[0].result_kind))
    check("the full two-block P1 result stays a SECONDARY predeclared diagnostic",
          case["block1_role"] == "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC")
    check("the joint P1 result does not change the C3 release verdict",
          case["c3_semantics"]["joint_p1_result_changes_C3_release_verdict"] is False)
    check("C3 still requires Block-1 calibration, as a diagnostic input",
          case["requires_block1_calibration"] is True
          and all(j.requires_calibration for j in jobs))
    check("adding a C3 release threshold on Block 1 remains forbidden",
          case["c3_semantics"]["what_is_forbidden"].startswith(
              "adding any new C3 release threshold"),
          case["c3_semantics"]["what_is_forbidden"][:60])


def test_seed_scopes_sharing_and_independence() -> None:
    harness = Harness()
    job0 = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    cal = replicate_calibration_for(harness.binding, job0, harness.ledger)
    common = cal.common_mode_seed()
    check("the common mode is ONE experiment-scope stream", isinstance(common, int))
    per_field = {f: cal.branch_a_seed(f) for f in FIELDS}
    check("the four fields share that one common mode",
          all(cal.common_mode_seed() == common for _ in FIELDS))
    check("their per-field Branch-A streams are independent",
          len(set(per_field.values())) == 4)
    check("no per-field stream equals the shared common mode",
          common not in set(per_field.values()))

    other_replicate = replicate_calibration_for(
        harness.binding,
        next(j for j in harness.jobs
             if j.coordinates.case_id == "C1_true_bridge_complete"
             and j.coordinates.replicate_id == 1
             and j.coordinates.scope == "theta0_circular"),
        CampaignCalibrationLedger())
    check("a different replicate has a different common mode",
          other_replicate.common_mode_seed() != common)
    other_sub = replicate_calibration_for(
        harness.binding,
        next(j for j in harness.jobs
             if j.coordinates.case_id == "C1_true_bridge_complete"
             and j.coordinates.subcondition_id == "sigma_psi_0p5"
             and j.coordinates.replicate_id == 0
             and j.coordinates.scope == "theta0_circular"),
        CampaignCalibrationLedger())
    check("a different subcondition has a different common mode",
          other_sub.common_mode_seed() != common)
    check("the driver derives no seed itself: every identity came from CaseSeedAccess",
          EXPERIMENT_SCOPE == "experiment")
    harness.close()


# ------------------------------------------------- 8. manifest, restart, results
def test_campaign_manifest() -> None:
    harness = Harness()
    manifest = campaign_manifest(harness.binding, harness.root)
    check("the manifest schema is declared",
          manifest["schema"] == CAMPAIGN_MANIFEST_SCHEMA)
    check("the lifecycle state is DRIVER_PRESENT_UNSEALED",
          manifest["state"] == "DRIVER_PRESENT_UNSEALED")
    identities = manifest["identities"]
    for key in ("foundation_sha256", "baseline_sha256", "contract_sha256",
                "design_sha256", "analysis_procedure_identity", "plan_json_sha256",
                "plan_markdown_sha256", "seed_map_sha256", "execution_identity",
                "official_campaign_driver_sha256"):
        check(f"the manifest binds {key}", bool(identities.get(key)))
    check("it binds the driver path and the validation modules",
          identities["official_campaign_driver_path"] == OFFICIAL_CAMPAIGN_DRIVER_PATH
          and "e1a_v4/validation/campaign_driver.py"
          not in identities["validation_modules"])
    check("it binds the case structure, subconditions and replicate counts",
          set(manifest["campaign"]["cases"]) == {c["case_id"] for c in PLAN["cases"]}
          and manifest["campaign"]["total_jobs"] == 53200)
    check("it binds the result and manifest schemas",
          manifest["result_schema"] == "e1a_v4_validation_result/2"
          and manifest["manifest_schema"] == "e1a_v4_validation_manifest/3")
    check("it binds every mandatory diagnostic",
          len(manifest["mandatory_diagnostics"])
          == len(PLAN["release_authority"]["mandatory_diagnostics"]) == 7)
    check("it binds the output location", manifest["output_directory"])
    check("the final expected execution identity is NULL, not frozen",
          manifest["final_expected_execution_identity"] is None)
    check("execution_authorised is false", manifest["execution_authorised"] is False)
    check("the manifest digest is deterministic",
          manifest_digest(manifest) == manifest_digest(campaign_manifest(
              harness.binding, harness.root)))
    check("the manifest says it is not an authorisation",
          manifest["not_execution_authorisation"] is True)
    stripped = bind_execution(harness.root)
    object.__setattr__(stripped, "analysis_identity", "")
    refuses_with_code("a manifest missing a required identity",
                      "CAMPAIGN_MANIFEST_INVALID", campaign_manifest, stripped,
                      harness.root)
    harness.close()


def test_restart_verification() -> None:
    harness = Harness()
    realisations = {}
    for scope in FIELDS:
        job = first_job(harness.jobs, "C1_true_bridge_complete", scope=scope)
        execution = harness.execution(job)
        realisations[job.job_id] = harness.realise(execution)
        execution.publish_branch_a()
    report = verify_restart(harness.out, realisations, harness.binding)
    check("every published record re-verifies on resume",
          report["verified_publications"] == 4, str(report))

    # a tampered record is caught on resume, not silently replaced
    job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    path = publication_path(harness.out, job.coordinates)
    record = read_published(path, "branch A")
    record["branch_a_evidence"]["rot_deg_measured"] = "0x1.0p+3"
    os.chmod(path, 0o600)
    with open(path, "wb") as handle:
        handle.write(canonical_bytes(record))
    os.chmod(path, 0o444)
    refuses_with_code("a tampered record on resume", "BRANCH_A_EVIDENCE_ALTERED",
                      verify_restart, harness.out, realisations, harness.binding)
    check("resume never regenerates a completed replicate: it refuses instead",
          os.path.isfile(path))
    harness.close()


def test_mandatory_diagnostics_required_at_record_time() -> None:
    from e1a_v4.validation.classification import GROSS_INFLATION_TOLERANCE
    from e1a_v4.validation.dispositions import cp_upper
    from e1a_v4.validation.results import aggregate_skeleton

    harness = Harness()
    job = first_job(harness.jobs, "C2_geometry_false_rejection", scope="theta0_circular")
    execution = harness.execution(job)
    harness.realise(execution)
    execution.publish_branch_a()
    condition = execution.calibration_condition()
    execution.lock_calibration(fixture_artifact(condition))
    execution.unblind()
    execution.branch_b_seed()
    execution.analyse({"p1_rejected": False})

    bare = aggregate_skeleton("C2_geometry_false_rejection", "sigma_psi_0p5")
    refuses_with_code("recording a C2 result with NO contract diagnostic",
                      "RESULT_SCHEMA_INVALID", execution.record, bare, FIELDS)

    complete = aggregate_skeleton("C2_geometry_false_rejection", "sigma_psi_0p5")
    complete["contract_diagnostics"] = {"per_field": {
        f: {"rejections": 2, "replicates": 400, "cp_upper": cp_upper(2, 400),
            "threshold": GROSS_INFLATION_TOLERANCE, "direction": "UPPER",
            "confidence_level": 0.95,
            "pass": cp_upper(2, 400) <= GROSS_INFLATION_TOLERANCE} for f in FIELDS}}
    recorded = execution.record(complete, FIELDS)
    check("a complete C2 result records", execution.state == RECORDED)
    check("the record carries the Branch-A evidence hash",
          recorded["branch_a_evidence_sha256"]
          == execution._realisation.evidence_sha256)
    check("the C2 contract diagnostic is structurally required, not optional logging",
          "contract_diagnostics" in complete)
    harness.close()


# ------------------------------------------------ 9. the execution path is shut
def test_execute_path_remains_blocked() -> None:
    harness = Harness()
    result = run_campaign(harness.root, plan_only=True)
    check("plan-only completes with no RNG",
          result["rng_objects"] == 0 and result["random_draws"] == 0
          and result["trajectories"] == 0)
    check("plan-only plans the whole campaign", result["jobs"] == 53200)
    check("plan-only reports plan/driver agreement",
          result["agreement"]["missing_planned_jobs"] == 0
          and result["agreement"]["extra_driver_jobs"] == 0)
    message = ""
    try:
        run_campaign(harness.root)
    except Refusal as exc:
        message = str(exc)
    check("the stochastic path REFUSES while the seal is unfrozen", bool(message))
    check("the refusal names the seal state and the authorisation flag, not a "
          "missing file",
          "PRE_DRIVER" in message and "execution_authorised" in message
          and "ABSENT" not in message, message[:110])
    check("it says explicitly that no RNG was constructed", "No RNG" in message)

    import inspect
    signature = inspect.signature(run_campaign)
    for forbidden in ("force", "skip_seal", "ignore_authorisation", "yes", "no_check"):
        check(f"run_campaign has no {forbidden!r} escape parameter",
              forbidden not in signature.parameters)
    source = open(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH),
                  encoding="utf-8").read()
    for flag in ("--force", "--skip-seal", "--ignore-authorisation"):
        check(f"the CLI declares no {flag} escape", f'"{flag}"' not in source)
    check("the CLI declares --plan-only and --preflight-only",
          '"--plan-only"' in source and '"--preflight-only"' in source)
    check("the runner's official execute path still refuses",
          refusal_code(__import__("e1a_v4.validation.runner", fromlist=["run"]).run,
                       harness.root, execute=True) is not None)
    harness.close()


def test_frozen_authority_unchanged() -> None:
    contract = strict_load_file(os.path.join(ROOT, CONTRACT_JSON), "the contract")
    check("the frozen foundation is unchanged",
          sha256_file(os.path.join(ROOT, "docs/physical_foundation/"
                                   "EBU_PHYSICAL_FOUNDATION_CANONICAL.md"))
          == "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507")
    check("the working baseline is unchanged",
          sha256_file(os.path.join(ROOT, "docs/theory/EBU_THEORY_BASELINE.md"))
          == "0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa")
    check("the design contract is unchanged",
          sha256_file(os.path.join(ROOT, CONTRACT_JSON))
          == "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b")
    check("the prospective design is unchanged",
          sha256_file(os.path.join(ROOT, "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md"))
          == "e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495")
    check("the seed map is unchanged",
          sha256_file(os.path.join(ROOT, SEED_MAP_JSON))
          == "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")
    rules = PLAN["adopted_rules_unchanged"]
    for key, expected in (("delta_cross", 0.02), ("delta_abs", 0.05),
                          ("z_cross", 1.959963985), ("z_abs", 1.959963985),
                          ("alpha_geom", 0.005), ("alpha_1", 0.004),
                          ("alpha_2", 0.001), ("theta_cap_deg", 5.0),
                          ("rank_tol", 1e-12), ("pipeline_target", 0.9)):
        check(f"{key} unchanged at {expected}", rules[key] == expected, repr(rules[key]))
    check("the eight cases and their replicate counts are unchanged",
          [(c["case_id"], c["replicate_count"]) for c in PLAN["cases"]]
          == [("C1_true_bridge_complete", 300), ("C2_geometry_false_rejection", 400),
              ("C3_g5_block", 400), ("C4_surrogate_validity", 2000),
              ("C5_plug_in_branch_a", 400), ("C6_mode_resolution_boundary", 400),
              ("C7_false_bridge", 400), ("C8_blinded_scale_control", 200)])
    gm = PLAN["generating_model"]["branch_b"]
    check("the corrected OU generator is unchanged",
          gm["dt_s"] == 0.00012 and gm["T_total_s"] == 240.0
          and gm["n_samples"] == 2000000)
    check("the release rules are unchanged",
          [r["integer_boundary"] for r in PLAN["assurance"]]
          == [279, 5, 2, 13, None, 6, 4, 188])
    check("the driver restates no scientific constant",
          all(token not in open(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH),
                                encoding="utf-8").read()
              for token in ("0.005", "1.959963985", "0.00012", "2000000", "279/300")))


def test_stochastic_boundary() -> None:
    check("NO REAL RNG OBJECT WAS CONSTRUCTED", SentinelRNG.CONSTRUCTED == 0,
          str(SentinelRNG.CONSTRUCTED))
    check("NO RANDOM NUMBER WAS DRAWN", SentinelRNG.DRAWS == 0, str(SentinelRNG.DRAWS))
    check("no results directory was created in the repository",
          not os.path.exists(os.path.join(ROOT, "results/e1a_v4_validation")))
    check("the execution seal is still PRE_DRIVER",
          strict_load_file(os.path.join(ROOT, SEAL_JSON), "seal")["state"] == "PRE_DRIVER")
    check("execution_authorised is still false", PLAN["execution_authorised"] is False)


GROUPS = (
    ("the canonical driver declaration", test_canonical_driver_present),
    ("driver identity binding", test_driver_identity_binding),
    ("deterministic campaign planning", test_campaign_planning),
    ("plan / driver exact agreement", test_plan_driver_agreement),
    ("parallel-order invariance", test_parallel_order_invariance),
    ("Branch-A realisation and its hash", test_branch_a_realisation_and_hash),
    ("Branch-A seed substitution", test_branch_a_seed_substitution_refuses),
    ("the durable publication primitive", test_publication_primitive),
    ("Branch-A publication and immutability", test_branch_a_publication_and_immutability),
    ("CalibrationCondition derived from the evidence", test_calibration_condition_derivation),
    ("cross-coordinate substitution", test_cross_coordinate_substitution_refuses),
    ("Branch-B requires publication and lock", test_branch_b_requires_publication_and_lock),
    ("the job state machine", test_state_machine_transitions),
    ("C7 and C8 no-calibration paths", test_c7_and_c8_have_no_calibration_dependency),
    ("C7 frozen alternatives", test_c7_alternatives_scheduled_exactly),
    ("C8 pairing", test_c8_pairing_shares_one_underlying_replicate),
    ("C3 secondary-diagnostic isolation", test_c3_secondary_diagnostic_isolated),
    ("seed scopes: sharing and independence", test_seed_scopes_sharing_and_independence),
    ("the campaign manifest", test_campaign_manifest),
    ("restart verification", test_restart_verification),
    ("mandatory diagnostics at record time", test_mandatory_diagnostics_required_at_record_time),
    ("the execute path remains blocked", test_execute_path_remains_blocked),
    ("frozen authority unchanged", test_frozen_authority_unchanged),
    ("the stochastic boundary", test_stochastic_boundary),
)


if __name__ == "__main__":
    for title, fn in GROUPS:
        print(f"\n{title}")
        fn()
    print(f"\nE1a v4 campaign-driver gate: {PASSED} passed, {FAILED} failed, "
          f"{len(GROUPS)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print(f"  REAL RNG OBJECTS      : {SentinelRNG.CONSTRUCTED}")
    print(f"  REAL RANDOM DRAWS     : {SentinelRNG.DRAWS}")
    print("  REAL TRAJECTORIES     : 0")
    raise SystemExit(1 if FAILED else 0)
