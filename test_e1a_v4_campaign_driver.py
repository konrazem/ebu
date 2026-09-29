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
    recover_realisations, realisation_from_record,
    ANALYSED, BRANCH_A_GENERATOR_IDENTITY, BRANCH_A_PUBLICATION_DIR,
    BRANCH_A_PUBLICATION_SCHEMA, BRANCH_A_PUBLISHED, BRANCH_A_REALIZED,
    BRANCH_B_UNBLINDED, CALIBRATION_CONDITION_BOUND, CALIBRATION_LOCKED,
    CAMPAIGN_MANIFEST_SCHEMA, PLANNED, PUBLICATION_FIELDS, RECORDED,
    UNDECLARED_C6_FIELD, UNDECLARED_FIELD_INPUTS, UNDECLARED_GENERATOR,
    AuthorisedStochasticProvider, BranchARealisation, BranchBUnblindToken,
    CampaignJob, JobCoordinates, JobExecution, JobSpecification,
    assemble_case_aggregates, branch_a_error_model, campaign_manifest,
    campaign_shape, canonical_result_fields, declared_beta_true,
    execute_campaign, inventory_publications, job_execution,
    main as driver_main, manifest_digest, plan_campaign, publication_basename,
    publication_directory, publication_envelope, publication_path,
    committed_publication, field_event_count,
    replicate_calibration_for, replicate_groups,
    require_campaign_completeness,
    require_execution_lifecycle, require_plan_driver_agreement,
    required_endpoint_events, required_result_fields,
    resolve_job_specification, run_campaign,
    validate_job_record, verify_publication, verify_restart,
)
from e1a_v4.validation.driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, declared_entry_points, driver_exists,
    driver_identity_component, require_canonical_driver,
)
from e1a_v4.validation.plan import bind_execution, execution_identity, load_plan
from e1a_v4.validation.publication import (
    PUBLICATION_STAGES, canonical_bytes, canonical_digest, canonical_json,
    commit_name, inventory_directory, is_commit_name,
    is_committed, publish_atomic,
    read_committed, read_published, require_clean_inventory, sealed_digest,
)
import e1a_v4.validation.publication as publication_module
from e1a_v4.validation.results import aggregate_skeleton
from e1a_v4.validation.dispositions import cp_upper
from e1a_v4.validation.scope import CampaignCalibrationLedger
from e1a_v4.validation.seeds import EXPERIMENT_SCOPE, ValidationSeedFamily
from e1a_v4.validation.seal import SEAL_JSON
from e1a_v4.validation.strict_json import strict_load_file

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTRACT_JSON = "docs/e1a/e1a_v4_design_contract.json"
#: Pinned so the repair cannot move the authority it is forbidden to move.
PLAN_JSON_SHA256 = "dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a"
PLAN_MARKDOWN_SHA256 = "3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940"
FAKE_SUPPLIERS_BEFORE_GATE = [0]
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


def endpoint_outcome(case_id: str, **overrides) -> dict:
    """A COMPLETE, case-appropriate set of endpoint decisions. Deterministic.

    Derived from `required_endpoint_events`, so a case that owes the per-field P1
    decision and both block decisions gets all three. A test may not hand the
    recorder a partial outcome, because production may not either.
    """
    outcome = {"analysis_status": "ESTIMATED", "beta_hat": 1.0}
    for event in required_endpoint_events(PLAN, case_id):
        if event == "analysis_status":
            continue
        outcome.setdefault(event, True if event == "P1" else False)
    outcome.update(overrides)
    return outcome


def revalidate(harness, execution, record):
    """Validate a terminal record through the SAME strict verifier production uses.

    Internal digest AND external provenance links AND the committed calibration
    lock. There is deliberately no weaker call and no way to hand it provenance:
    `validate_job_record` takes the campaign output ROOT and resolves the
    committed publication and the committed lock itself, so a test cannot
    exercise a path production does not have, and cannot supply the very object
    that is supposed to prove the record.
    """
    return refusal_code(validate_job_record, record, harness.binding.plan,
                        harness.binding, execution.job, harness.out)


def write_record(path: str, record) -> None:
    """Overwrite a published artifact in place. A read-only file is not immutable
    storage; it is a convention, and the point of the commit marker is that
    defeating the convention still does not produce accepted evidence."""
    os.chmod(path, 0o600)
    with open(path, "wb") as handle:
        handle.write(canonical_bytes(record))
    os.chmod(path, 0o444)


def recommit(directory: str, basename: str, mutate, *,
             fix_publication_digest: bool = False) -> None:
    """Tamper with an artifact AND rebuild a fully self-consistent commit marker.

    This is the capable adversary: byte digests, the marker's own digest and the
    commit linkage are all repaired. Only the publication digest over the whole
    provenance envelope can still catch it, which is exactly what the audit found
    missing when the evidence hash alone was the authentication.
    """
    import hashlib
    artifact = os.path.join(directory, basename)
    record = read_published(artifact, "record")
    mutate(record)
    if fix_publication_digest:
        record["publication_digest"] = sealed_digest(record, "publication_digest")
    write_record(artifact, record)
    marker_path = os.path.join(directory, commit_name(basename))
    marker = read_published(marker_path, "marker")
    marker["artifact_bytes_sha256"] = hashlib.sha256(
        open(artifact, "rb").read()).hexdigest()
    if fix_publication_digest:
        marker["publication_digest"] = record["publication_digest"]
    marker["commit_digest"] = sealed_digest(marker, "commit_digest")
    write_record(marker_path, marker)


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
    receipt = publish_atomic(directory, "probe.json", {"b": 2, "a": 1})
    path = receipt.path
    check("publication creates the final path", os.path.isfile(path))
    check("the receipt carries the exact byte digest",
          receipt.byte_sha256
          == __import__("hashlib").sha256(open(path, "rb").read()).hexdigest())
    check("a clean publication leaves no residual alias",
          receipt.residual_alias is None)
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
    directory = publication_directory(harness.out)
    basename = os.path.basename(path)
    check("publication is COMMITTED, not merely written",
          is_committed(directory, basename))
    check("the commit marker exists beside the artifact",
          os.path.isfile(os.path.join(directory, commit_name(basename))))
    record, marker = read_committed(directory, basename, "branch A")
    check("the marker commits this artifact's exact bytes",
          marker["artifact_bytes_sha256"]
          == __import__("hashlib").sha256(open(path, "rb").read()).hexdigest())
    check("the marker commits the same publication digest",
          marker["publication_digest"] == record["publication_digest"])
    check("the record carries exactly the declared publication fields",
          set(record) == set(PUBLICATION_FIELDS), str(sorted(record)))
    check("the publication digest is a recomputation over everything else",
          record["publication_digest"] == sealed_digest(record, "publication_digest"))
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

    # LAYER 1: editing the artifact alone breaks the committed byte digest.
    for label, mutate in (
            ("edited published EVIDENCE",
             lambda r: r["branch_a_evidence"].__setitem__("T_measured", "0x1.0p+8")),
            ("edited published HASH",
             lambda r: r.__setitem__("branch_a_evidence_sha256", "0" * 64)),
            ("rebound coordinates",
             lambda r: r["coordinates"].__setitem__("replicate_id", 7)),
            ("a package identity changed after publication",
             lambda r: r["package_identities"].__setitem__("plan_sha256", "0" * 64))):
        tampered = copy.deepcopy(record)
        mutate(tampered)
        write_record(path, tampered)
        refuses_with_code(label, "PUBLICATION_INCOMPLETE", verify_publication,
                          harness.out, realisation, harness.binding)
    write_record(path, record)
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
    execution.analyse(endpoint_outcome(execution.coordinates.case_id,
                                      complete_pass=True))
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
    refuses_with_code("a tampered record on resume", "PUBLICATION_INCOMPLETE",
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
    execution.analyse(endpoint_outcome(execution.coordinates.case_id))

    subcondition = job.coordinates.subcondition_id
    bare = aggregate_skeleton("C2_geometry_false_rejection", subcondition)
    refuses_with_code("recording a C2 result with NO contract diagnostic",
                      "RESULT_SCHEMA_INVALID", execution.record, bare, FIELDS)

    complete = aggregate_skeleton("C2_geometry_false_rejection", subcondition)
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
    stored = {d["diagnostic_id"]: d for d in recorded["mandatory_diagnostics"]}
    check("the checked diagnostic SURVIVES into the stored result",
          "C2_CONTRACT_COARSE_UPPER_BOUND" in stored, str(sorted(stored)))
    evidence = stored["C2_CONTRACT_COARSE_UPPER_BOUND"]["value"]["per_field"]
    check("the stored evidence carries one row per declared field",
          set(evidence) == set(FIELDS))
    row = evidence[sorted(evidence)[0]]
    for key in ("rejections", "replicates", "cp_upper", "threshold", "direction",
                "confidence_level", "pass"):
        check(f"the stored diagnostic retains {key!r}", key in row)
    check("the stored record re-validates from ITSELF after a JSON round trip",
          revalidate(harness, execution, json.loads(json.dumps(recorded))) is None)
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
    code = refusal_code(run_campaign, harness.root)
    check("the stochastic path REFUSES at the lifecycle gate",
          code == "EXECUTION_SEAL_NOT_FROZEN", str(code))
    message = ""
    try:
        run_campaign(harness.root)
    except Refusal as exc:
        message = str(exc)
    check("the refusal names the seal state, not a missing file",
          "PRE_DRIVER" in message and "ABSENT" not in message, message[:110])

    import inspect
    signature = inspect.signature(run_campaign)
    for forbidden in ("force", "skip_seal", "skip_gate", "ignore_authorisation",
                      "ignore_seal", "test_mode", "yes", "no_check", "provider",
                      "rng_factory"):
        check(f"run_campaign has no {forbidden!r} escape parameter",
              forbidden not in signature.parameters)
    source = open(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH),
                  encoding="utf-8").read()
    for flag in ("--force", "--skip-seal", "--skip-gate", "--ignore-authorisation",
                 "--test-mode"):
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



# =============================================================================
# REGRESSION SUITE FOR THE INDEPENDENT AUDIT'S FIVE BLOCKING FINDINGS
#
# Every check below was demonstrated to ESCAPE at commit 29ffe625. Each one is
# reproduced here as a permanent regression, so the repair cannot be undone
# silently. Nothing in this section draws a random number: the stochastic
# providers are deterministic van der Corput suppliers, counted separately and
# never described as scientific execution.
# =============================================================================
class FakeSupplier:
    """A DETERMINISTIC van der Corput supplier. NOT a random number generator.

    It has no entropy source, no seed state beyond an index, and returns the
    same values every time. It exists to exercise the orchestration's CONTROL
    FLOW. Nothing it produces is a scientific result, and the numbers below are
    not samples from any distribution.
    """

    CONSTRUCTED = 0
    VALUES = 0

    def __init__(self, seed: int) -> None:
        self.i = seed % 977
        type(self).CONSTRUCTED += 1

    def normal(self, count: int) -> list[float]:
        out = []
        for _ in range(count):
            self.i += 1
            n, base, frac = self.i, 0.0, 0.5
            while n:
                frac /= 2
                base += frac * (n & 1)
                n >>= 1
            out.append((base - 0.5) * 2.0)
        type(self).VALUES += count
        return out


class FakeProvider:
    """A deterministic StochasticProvider for control-flow tests only."""

    def __init__(self) -> None:
        self.requests: list[tuple[int, str]] = []

    def generator(self, seed: int, purpose: str):
        self.requests.append((seed, purpose))
        return FakeSupplier(seed)


def fixture_resolver(binding, job) -> JobSpecification:
    """Supply the inputs frozen authority does not yet declare. TEST ONLY.

    `resolve_job_specification` refuses for every job today, naming three
    authority gaps. A test fixture may state what a frozen document must later
    state; production may not, which is why the production resolver refuses
    instead of defaulting. The trajectory length here is deliberately tiny: this
    exercises ordering and provenance, not statistics.
    """
    spec = next(f for f in binding.binding.fields if f["id"] == job.coordinates.scope)
    field = build_field(binding.binding, spec,
                        calibration_route="force_displacement_with_stokes_drag",
                        viscosity=0.00089, bead_radius=1e-6)
    rules = binding.plan["adopted_rules_unchanged"]
    case_id, sub = job.coordinates.case_id, job.coordinates.subcondition_id
    scale: tuple[float, ...] = ()
    for entry in next(c for c in binding.plan["cases"]
                      if c["case_id"] == case_id)["subconditions"]:
        if entry["subcondition_id"] == sub and "scale_factors" in entry:
            scale = tuple(float(x) for x in entry["scale_factors"])
    beta = (1.0 if case_id == "C8_blinded_scale_control"
            else declared_beta_true(binding.plan, case_id, sub, job.coordinates.scope))
    return JobSpecification(
        coordinates=job.coordinates, field=field,
        error_model=branch_a_error_model(binding, case_id, sub),
        beta_true=beta, dt=1e-5, n_samples=400, rank_tol=rules["rank_tol"],
        theta_cap_deg=rules["theta_cap_deg"], scale_factors=scale)


class inject:
    """Fail EXACTLY ONE filesystem stage, on exactly one call. Deterministic.

    No system state is corrupted: the stage function is restored on exit and the
    injected error is an ordinary OSError, which is what a full disk or a failing
    device actually raises.
    """

    def __init__(self, stage: str, on_call: int = 1) -> None:
        self.stage, self.on_call, self.calls = stage, on_call, 0

    def __enter__(self):
        self.attr = f"_stage_{self.stage}"
        self.original = getattr(publication_module, self.attr)
        original = self.original

        def failing(*args, **kwargs):
            self.calls += 1
            if self.calls == self.on_call:
                raise OSError(f"INJECTED FAILURE at stage {self.stage!r}")
            return original(*args, **kwargs)

        setattr(publication_module, self.attr, failing)
        return self

    def __exit__(self, *exc):
        setattr(publication_module, self.attr, self.original)
        return False


def published(harness, case_id="C2_geometry_false_rejection", scope=None):
    """One execution carried to BRANCH_A_PUBLISHED. No draws."""
    job = first_job(harness.jobs, case_id, scope=scope)
    execution = harness.execution(job)
    realisation = harness.realise(execution)
    path = execution.publish_branch_a()
    return execution, realisation, path


def unblinded(harness, case_id="C2_geometry_false_rejection", scope=None):
    """One execution carried to BRANCH_B_UNBLINDED using fixture artifacts."""
    execution, realisation, path = published(harness, case_id, scope)
    if execution.job.requires_calibration:
        condition = execution.calibration_condition()
        execution.lock_calibration(fixture_artifact(condition))
    execution.unblind()
    return execution, realisation, path


# ----------------------------------- A. the complete provenance envelope binds
def test_publication_envelope_binds_every_field() -> None:
    """AUDIT FINDING A. Editing ANY bound provenance field must invalidate."""
    harness = Harness()
    execution, realisation, path = published(harness)
    directory, basename = publication_directory(harness.out), os.path.basename(path)
    envelope = publication_envelope(
        realisation, realisation.calibration_condition(harness.binding),
        harness.binding)
    check("the envelope binds the schema, state, coordinates, evidence, evidence "
          "digest, condition hash and every package identity",
          set(envelope) == set(PUBLICATION_FIELDS), str(sorted(envelope)))
    check("the publication schema is version 2: version 1 authenticated by the "
          "evidence hash alone and is refused, not reinterpreted",
          envelope["schema"] == BRANCH_A_PUBLICATION_SCHEMA
          and BRANCH_A_PUBLICATION_SCHEMA.endswith("/2"))
    check("the record is filed at a path that is a pure function of its coordinates",
          basename == publication_basename(realisation.coordinates))
    check("the evidence names the frozen Branch-A generator as its provenance",
          BRANCH_A_GENERATOR_IDENTITY
          == "e1a_v4.validation.generate.BranchAErrorModel.measure")
    check("a freshly published store is CLEAN by independent inspection",
          require_clean_inventory(directory, "probe").committed == (basename,))
    recovered = realisation_from_record(read_published(path, "record"))
    check("the evidence recovers losslessly from its own publication",
          recovered.evidence_sha256 == realisation.evidence_sha256
          and recovered.canonical() == realisation.canonical())
    check("the digest excludes itself, so verification is a recomputation",
          envelope["publication_digest"]
          == sealed_digest(envelope, "publication_digest"))
    harness.close()

    # Each field individually, against a tamperer who ALSO re-commits the marker
    # consistently -- so only the envelope digest can catch the edit.
    edits = (
        ("execution identity",
         lambda r: r["package_identities"].__setitem__("execution_identity", "0" * 64)),
        ("analysis identity",
         lambda r: r["package_identities"].__setitem__(
             "analysis_procedure_identity", "0" * 64)),
        ("calibration-condition hash",
         lambda r: r.__setitem__("calibration_condition_sha256", "f" * 64)),
        ("Branch-A evidence hash",
         lambda r: r.__setitem__("branch_a_evidence_sha256", "a" * 64)),
        ("coordinates",
         lambda r: r["coordinates"].__setitem__("replicate_id", 4242)),
        ("Branch-A seed identity",
         lambda r: r["branch_a_evidence"].__setitem__("branch_a_seed", 1)),
        ("common-mode seed identity",
         lambda r: r["branch_a_evidence"].__setitem__("common_mode_seed", 2)),
        ("contract identity",
         lambda r: r["package_identities"].__setitem__("contract_sha256", "0" * 64)),
        ("plan identity",
         lambda r: r["package_identities"].__setitem__("plan_sha256", "0" * 64)),
        ("seed-map identity",
         lambda r: r["package_identities"].__setitem__("seed_map_sha256", "0" * 64)),
    )
    for label, mutate in edits:
        harness = Harness()
        execution, realisation, path = published(harness)
        directory, basename = publication_directory(harness.out), os.path.basename(path)
        recommit(directory, basename, mutate)
        refuses_with_code(f"{label} edited, marker re-committed",
                          "PUBLICATION_DIGEST_MISMATCH", verify_publication,
                          harness.out, realisation, harness.binding)
        harness.close()

    # publication STATE and SCHEMA are refused by the strict schema, before the
    # digest is even reached: an invalid state is not a record to authenticate.
    for label, mutate, expected in (
            ("publication state",
             lambda r: r.__setitem__("state", "PUBLISHED_HONESTLY"),
             "PUBLICATION_INCOMPLETE"),
            ("publication schema",
             lambda r: r.__setitem__("schema", "e1a_v4_branch_a_publication/1"),
             "PUBLICATION_INCOMPLETE")):
        harness = Harness()
        execution, realisation, path = published(harness)
        recommit(publication_directory(harness.out), os.path.basename(path), mutate)
        refuses_with_code(f"{label} edited, marker re-committed", expected,
                          verify_publication, harness.out, realisation, harness.binding)
        harness.close()

    # and a tamperer who repairs the envelope digest TOO still cannot substitute
    # evidence or identities, because the realisation in hand is compared.
    for label, mutate, expected in (
            ("execution identity, envelope digest also recomputed",
             lambda r: r["package_identities"].__setitem__(
                 "execution_identity", "0" * 64),
             "BRANCH_A_PROVENANCE_MISMATCH"),
            ("evidence body, envelope digest also recomputed",
             lambda r: r["branch_a_evidence"].__setitem__("T_measured", "0x1.0p+0"),
             "BRANCH_A_EVIDENCE_ALTERED")):
        harness = Harness()
        execution, realisation, path = published(harness)
        recommit(publication_directory(harness.out), os.path.basename(path), mutate,
                 fix_publication_digest=True)
        refuses_with_code(label, expected, verify_publication, harness.out,
                          realisation, harness.binding)
        harness.close()


def test_publication_strict_schema() -> None:
    """A published record fails closed on shape, not just on content."""
    harness = Harness()
    execution, realisation, path = published(harness)
    directory, basename = publication_directory(harness.out), os.path.basename(path)
    pristine = read_published(path, "record")
    for label, mutate, expected in (
            ("a MISSING required field",
             lambda r: r.pop("calibration_condition_sha256"), "PUBLICATION_INCOMPLETE"),
            ("an UNKNOWN authoritative field",
             lambda r: r.__setitem__("side_channel", 1), "PUBLICATION_INCOMPLETE"),
            ("a WRONG type",
             lambda r: r.__setitem__("coordinates", "C2"), "PUBLICATION_INCOMPLETE"),
            ("an INVALID publication state",
             lambda r: r.__setitem__("state", "MAYBE"), "PUBLICATION_INCOMPLETE"),
            ("a MALFORMED digest",
             lambda r: r.__setitem__("publication_digest", "not-a-digest"),
             "PUBLICATION_INCOMPLETE"),
            ("a missing package identity",
             lambda r: r["package_identities"].pop("execution_identity"),
             "PUBLICATION_INCOMPLETE"),
            ("an unknown package identity",
             lambda r: r["package_identities"].__setitem__("extra", "x"),
             "PUBLICATION_INCOMPLETE"),
            ("incomplete coordinates",
             lambda r: r["coordinates"].pop("scope"), "PUBLICATION_INCOMPLETE")):
        record = copy.deepcopy(pristine)          # each probe starts from clean
        mutate(record)
        write_record(path, record)
        import hashlib
        marker_path = os.path.join(directory, commit_name(basename))
        marker = read_published(marker_path, "marker")
        marker["artifact_bytes_sha256"] = hashlib.sha256(
            open(path, "rb").read()).hexdigest()
        marker["commit_digest"] = sealed_digest(marker, "commit_digest")
        write_record(marker_path, marker)
        refuses_with_code(label, expected, verify_publication, harness.out,
                          realisation, harness.binding)
    # DUPLICATE KEYS are refused one layer down, by the strict parser, so an
    # ambiguous record never reaches the schema at all.
    duplicated = os.path.join(directory, "duplicated.json")
    with open(duplicated, "wb") as handle:
        handle.write(b'{"a":1,"a":2}\n')
    refuses_with_code("a record with a DUPLICATE key", "PLAN_DUPLICATE_KEY",
                      read_published, duplicated, "duplicated")
    harness.close()


# ---------------------------------------- B. publication transaction semantics
def test_publication_fault_injection() -> None:
    """AUDIT FINDING D. A failed publication is never accepted as published.

    For every injectable stage: the operation reports failure, the job does not
    advance, the verifier does not accept, and restart does not infer completion.
    """
    # `publish_branch_a` is ONE transaction publishing TWO artifacts: the
    # evidence, then its commit marker. Each has its own durability point (the
    # directory fsync right after its link) and its own alias unlink afterwards.
    # A failure at or before a durability point must fail the transaction; a
    # failure after one leaves recoverable residue and must NOT fail it.
    stages = (
        ("lstat", 1, False),          # absence probe for the evidence
        ("open_temp", 1, False),      # evidence temporary
        ("write", 1, False),          # evidence bytes
        ("fsync_file", 1, False),     # evidence durability
        ("fchmod", 1, False),         # evidence read-only
        ("link", 1, False),           # evidence finalisation
        ("fsync_dir", 1, False),      # EVIDENCE DURABILITY POINT
        ("fsync_dir", 2, True),       # evidence alias unlink: residue, not failure
        ("unlink", 1, True),          # evidence alias unlink: residue, not failure
        ("open_temp", 2, False),      # commit-marker temporary
        ("link", 2, False),           # commit-marker finalisation
        ("fsync_dir", 3, False),      # COMMIT-MARKER DURABILITY POINT
        ("fsync_dir", 4, True),       # marker alias unlink: residue, not failure
        ("unlink", 2, True),          # marker alias unlink: residue, not failure
    )
    check("every injectable stage is a declared publication stage",
          {stage for stage, _, _ in stages} <= set(PUBLICATION_STAGES)
          | {"fsync_dir", "unlink"},
          str(sorted({stage for stage, _, _ in stages})))
    for stage, on_call, durable in stages:
        harness = Harness()
        job = first_job(harness.jobs, "C2_geometry_false_rejection")
        execution = harness.execution(job)
        realisation = harness.realise(execution)
        raised = None
        with inject(stage, on_call):
            try:
                execution.publish_branch_a()
            except BaseException as exc:      # noqa: BLE001 - the point of the probe
                raised = exc
        label = f"{stage} (call {on_call})"
        if durable:
            # PAST the durability point: the artifact IS published and a leftover
            # alias is recoverable residue, exactly as the addendum specifies.
            check(f"{label}: publication SUCCEEDS past the durability point",
                  raised is None and execution.state == BRANCH_A_PUBLISHED,
                  f"raised={type(raised).__name__ if raised else None}, "
                  f"state={execution.state}")
            check(f"{label}: the verifier accepts the durable artifact",
                  refusal_code(verify_publication, harness.out, realisation,
                               harness.binding) is None)
        else:
            check(f"{label}: the operation REPORTS FAILURE", raised is not None,
                  type(raised).__name__ if raised else "no exception")
            check(f"{label}: the job does NOT advance",
                  execution.state == BRANCH_A_REALIZED, execution.state)
            check(f"{label}: the verifier does NOT accept a publication",
                  refusal_code(verify_publication, harness.out, realisation,
                               harness.binding) is not None)
            inventory = inventory_directory(publication_directory(harness.out))
            check(f"{label}: restart does NOT infer a completed publication",
                  inventory.committed == (), str(inventory.as_dict()))
            check(f"{label}: any residue is reported, never promoted",
                  refusal_code(verify_restart, harness.out, {}, harness.binding)
                  is None or not inventory.is_clean, str(inventory.as_dict()))
        harness.close()


def test_publication_orphan_detection() -> None:
    """An artifact without its commit marker is ORPHANED, never PUBLISHED."""
    harness = Harness()
    execution, realisation, path = published(harness)
    directory, basename = publication_directory(harness.out), os.path.basename(path)
    marker = os.path.join(directory, commit_name(basename))
    os.remove(marker)
    inventory = inventory_directory(directory)
    check("the inventory reports the artifact as ORPHANED",
          inventory.orphaned == (basename,) and inventory.committed == (),
          str(inventory.as_dict()))
    refuses_with_code("verifying an orphan", "PUBLICATION_ORPHANED",
                      verify_publication, harness.out, realisation, harness.binding)
    refuses_with_code("restarting over an orphan", "PUBLICATION_ORPHANED",
                      verify_restart, harness.out, {}, harness.binding)
    check("the orphan is PRESERVED, not deleted: it is the only record of the "
          "attempt", os.path.isfile(path))
    harness.close()

    # the mirror image: a commit marker whose artifact is gone
    harness = Harness()
    execution, realisation, path = published(harness)
    directory = publication_directory(harness.out)
    os.remove(path)
    inventory = inventory_directory(directory)
    check("the inventory reports a DANGLING commit marker",
          len(inventory.dangling) == 1 and inventory.committed == (),
          str(inventory.as_dict()))
    refuses_with_code("a marker whose artifact is missing", "PUBLICATION_INCOMPLETE",
                      verify_restart, harness.out, {}, harness.binding)
    harness.close()

    # an unexplained entry in a scientific result directory
    harness = Harness()
    execution, realisation, path = published(harness)
    directory = publication_directory(harness.out)
    with open(os.path.join(directory, "notes.txt"), "w", encoding="utf-8") as handle:
        handle.write("scratch\n")
    refuses_with_code("an unexplained entry in the publication store",
                      "PUBLICATION_UNEXPECTED_ENTRY", verify_restart, harness.out,
                      {execution.coordinates.job_id: realisation}, harness.binding)
    harness.close()


# ------------------------------------------ C. result recording, case-derived
def test_case_result_type_compatibility() -> None:
    """AUDIT FINDING B. A C2 job must not accept a C7 aggregate. Nor any other."""
    cases = [c["case_id"] for c in PLAN["cases"]]
    # C6 declares its field as prose and cannot be realised from the contract's
    # four declared fields; that gap is asserted separately, by name.
    drivable = [c for c in cases if c != "C6_mode_resolution_boundary"]
    for case_id in drivable:
        harness = Harness()
        execution, realisation, path = unblinded(harness, case_id)
        execution.analyse(endpoint_outcome(execution.coordinates.case_id))
        job = execution.job
        own = aggregate_skeleton(case_id, job.coordinates.subcondition_id)
        wrong = [other for other in cases if other != case_id]
        refused = 0
        for other in wrong:
            foreign = aggregate_skeleton(other, job.coordinates.subcondition_id)
            if refusal_code(execution.record, foreign,
                            required_result_fields(PLAN, case_id)) == "RESULT_CASE_MISMATCH":
                refused += 1
        check(f"{case_id}: all {len(wrong)} foreign aggregates refused",
              refused == len(wrong), f"{refused}/{len(wrong)}")
        check(f"{case_id}: the job is still ANALYSED after every refusal",
              execution.state == ANALYSED, execution.state)
        # a foreign SUBCONDITION of the right case is refused too
        others = [s["subcondition_id"] for s in
                  next(c for c in PLAN["cases"] if c["case_id"] == case_id)["subconditions"]
                  if s["subcondition_id"] != job.coordinates.subcondition_id]
        if others:
            refuses_with_code(f"{case_id}: a foreign subcondition aggregate",
                              "RESULT_CASE_MISMATCH", execution.record,
                              aggregate_skeleton(case_id, others[0]),
                              required_result_fields(PLAN, case_id))
        # the aggregate SCHEMA is checked too
        bad_schema = aggregate_skeleton(case_id, job.coordinates.subcondition_id)
        bad_schema["schema"] = "e1a_v4_validation_manifest/2"
        refuses_with_code(f"{case_id}: an aggregate with a superseded schema",
                          "RESULT_SCHEMA_INVALID", execution.record, bad_schema,
                          required_result_fields(PLAN, case_id))
        harness.close()


def test_field_set_derived_from_the_job() -> None:
    """AUDIT FINDING B. The field set comes from the frozen plan, not the caller."""
    required = required_result_fields(PLAN, "C2_geometry_false_rejection")
    check("the required set is the plan's declared fields_affected, in plan order",
          list(required) == next(c for c in PLAN["cases"]
                                 if c["case_id"] == "C2_geometry_false_rejection"
                                 )["fields_affected"])
    probes = (
        ("an EMPTY field list", ()),
        ("a MISSING field", required[:-1]),
        ("an EXTRA field", required + ("theta9_invented",)),
        ("a DUPLICATE field", required + (required[0],)),
        ("a WRONG field name", required[:-1] + ("theta3_temperatures",)),
    )
    for label, supplied in probes:
        expected = ("RESULT_FIELD_SET_MISMATCH")
        got = refusal_code(canonical_result_fields, "probe", required, supplied)
        check(f"{label} -> {expected}", got == expected, f"got {got!r}")
    reordered = tuple(reversed(required))
    check("a CORRECT set in another order is canonicalised, not refused: ordering "
          "is not semantic here and the plan's order is the canonical one",
          canonical_result_fields("probe", required, reordered) == required)
    check("None means 'derive it', which is the recorder's default",
          canonical_result_fields("probe", required, None) == required)

    # and the same rules through the recorder itself
    harness = Harness()
    execution, realisation, path = unblinded(harness, "C2_geometry_false_rejection")
    execution.analyse(endpoint_outcome(execution.coordinates.case_id))
    aggregate = c2_aggregate(execution.job.coordinates.subcondition_id)
    for label, supplied in probes:
        refuses_with_code(f"the recorder rejects {label}", "RESULT_FIELD_SET_MISMATCH",
                          execution.record, aggregate, supplied)
    check("the job is still ANALYSED after every refused field set",
          execution.state == ANALYSED, execution.state)
    recorded = execution.record(aggregate, reordered)
    check("a reordered but correct set records, canonicalised",
          recorded["fields"] == list(required), str(recorded["fields"]))
    harness.close()


def c2_aggregate(subcondition_id: str, rejections: int = 2) -> dict:
    """A complete, arithmetically consistent C2 aggregate. Deterministic."""
    from e1a_v4.validation.classification import GROSS_INFLATION_TOLERANCE
    aggregate = aggregate_skeleton("C2_geometry_false_rejection", subcondition_id)
    aggregate["contract_diagnostics"] = {"per_field": {
        f: {"rejections": rejections, "replicates": 400,
            "cp_upper": cp_upper(rejections, 400),
            "threshold": GROSS_INFLATION_TOLERANCE, "direction": "UPPER",
            "confidence_level": 0.95,
            "pass": cp_upper(rejections, 400) <= GROSS_INFLATION_TOLERANCE}
        for f in FIELDS}}
    return aggregate


def test_mandatory_diagnostic_persistence_and_round_trip() -> None:
    """AUDIT FINDING B. A checked diagnostic must survive into the record."""
    harness = Harness()
    execution, realisation, path = unblinded(harness, "C2_geometry_false_rejection")
    execution.analyse(endpoint_outcome(execution.coordinates.case_id))
    subcondition = execution.job.coordinates.subcondition_id
    recorded = execution.record(c2_aggregate(subcondition))
    stored = {d["diagnostic_id"]: d for d in recorded["mandatory_diagnostics"]}
    check("C2's frozen mandatory contract diagnostic is stored",
          "C2_CONTRACT_COARSE_UPPER_BOUND" in stored, str(sorted(stored)))
    row = stored["C2_CONTRACT_COARSE_UPPER_BOUND"]
    check("the stored diagnostic names its frozen authority path",
          row["authority_path"] == "synthetic_validation_requirements[2]")
    per_field = row["value"]["per_field"]
    check("every declared field has a row", set(per_field) == set(FIELDS))
    sample = per_field[sorted(per_field)[0]]
    check("the RAW COUNTS survive", {"rejections", "replicates"} <= set(sample))
    check("the COMPUTED one-sided 95% upper bound survives",
          abs(sample["cp_upper"] - cp_upper(sample["rejections"],
                                            sample["replicates"])) < 1e-15)
    check("the CONFIDENCE RULE survives",
          sample["confidence_level"] == 0.95 and sample["direction"] == "UPPER")
    check("the THRESHOLD survives", sample["threshold"] == 0.03)
    check("the CLASSIFICATION survives", isinstance(sample["pass"], bool))

    # ROUND TRIP: serialise, read back, revalidate from the record ALONE
    round_trip = json.loads(json.dumps(recorded))
    check("the record survives a canonical JSON round trip byte for byte",
          canonical_json(round_trip) == canonical_json(recorded))
    check("the round-tripped record re-validates WITHOUT its original aggregate",
          revalidate(harness, execution, round_trip) is None)
    check("the record's own digest is a recomputation over everything else",
          recorded["result_digest"] == sealed_digest(dict(recorded), "result_digest"))
    tampered = json.loads(json.dumps(recorded))
    tampered["result"]["p1_rejected"] = True
    check("an edited stored result -> RESULT_SCHEMA_INVALID",
          revalidate(harness, execution, tampered) == "RESULT_SCHEMA_INVALID",
          str(revalidate(harness, execution, tampered)))
    stripped = json.loads(json.dumps(recorded))
    stripped["mandatory_diagnostics"] = []
    stripped["result_digest"] = sealed_digest(stripped, "result_digest")
    check("a stored result with its diagnostics removed -> "
          "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING",
          revalidate(harness, execution, stripped)
          == "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING",
          str(revalidate(harness, execution, stripped)))
    inconsistent = json.loads(json.dumps(recorded))
    diagnostics = inconsistent["mandatory_diagnostics"][0]["value"]["per_field"]
    diagnostics[sorted(diagnostics)[0]]["cp_upper"] = 0.5
    inconsistent["result_digest"] = sealed_digest(inconsistent, "result_digest")
    check("a stored diagnostic inconsistent with its own counts -> "
          "CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH",
          revalidate(harness, execution, inconsistent)
          == "CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH",
          str(revalidate(harness, execution, inconsistent)))
    harness.close()

    # a C7 result cannot satisfy C2's requirement: it is not a C2 result at all
    harness = Harness()
    execution, realisation, path = unblinded(harness, "C7_false_bridge")
    execution.analyse(endpoint_outcome(execution.coordinates.case_id))
    refuses_with_code("a C7 job presented with C2's mandatory diagnostic",
                      "RESULT_CASE_MISMATCH", execution.record,
                      c2_aggregate(execution.job.coordinates.subcondition_id))
    recorded = execution.record(
        aggregate_skeleton("C7_false_bridge", execution.job.coordinates.subcondition_id))
    check("a C7 result carries no C2 diagnostic and is still valid on its own terms",
          recorded["mandatory_diagnostics"] == []
          and revalidate(harness, execution, recorded) is None)
    harness.close()


def test_result_round_trip_every_case() -> None:
    """Every drivable case: construct, serialise, read back, revalidate."""
    for case in PLAN["cases"]:
        case_id = case["case_id"]
        if case_id == "C6_mode_resolution_boundary":
            continue
        harness = Harness()
        execution, realisation, path = unblinded(harness, case_id)
        execution.analyse(endpoint_outcome(execution.coordinates.case_id))
        subcondition = execution.job.coordinates.subcondition_id
        aggregate = (c2_aggregate(subcondition)
                     if case_id == "C2_geometry_false_rejection"
                     else case_aggregate(case_id, subcondition))
        recorded = execution.record(aggregate)
        round_trip = json.loads(json.dumps(recorded))
        ok = revalidate(harness, execution, round_trip)
        check(f"{case_id}: a valid result round-trips and revalidates", ok is None,
              str(ok))
        check(f"{case_id}: provenance identities survive",
              round_trip["package_identities"]["execution_identity"]
              == harness.binding.execution_identity
              and round_trip["publication_digest"]
              and round_trip["branch_a_evidence_sha256"]
              == realisation.evidence_sha256)
        check(f"{case_id}: the result kind is DERIVED from the frozen job",
              round_trip["result_kind"] == execution.job.result_kind)
        harness.close()


def case_aggregate(case_id: str, subcondition_id: str) -> dict:
    """A minimal aggregate carrying whatever that case's frozen authority demands."""
    from e1a_v4.validation.release_authority import mandatory_diagnostics_for
    aggregate = aggregate_skeleton(case_id, subcondition_id)
    for diagnostic in mandatory_diagnostics_for(PLAN, case_id):
        if diagnostic.required_keys:
            aggregate[diagnostic.aggregate_key] = {k: {} for k in diagnostic.required_keys}
            for key in diagnostic.required_keys:
                aggregate[diagnostic.aggregate_key][key] = {"declared": True}
    return aggregate


# ---------------------------------------------- D. restart reconciliation
def test_restart_reconciles_with_the_persisted_inventory() -> None:
    """AUDIT FINDING C. The caller's list is never the universe of evidence."""
    harness = Harness()
    check("an EMPTY restart over an EMPTY store is valid, and only then",
          refusal_code(verify_restart, harness.out, {}, harness.binding) is None)
    check("the empty store really is empty",
          inventory_directory(publication_directory(harness.out)).is_empty)
    realisations = {}
    for scope in FIELDS:
        execution, realisation, path = published(harness, "C1_true_bridge_complete",
                                                 scope)
        realisations[execution.coordinates.job_id] = realisation
    report = verify_restart(harness.out, realisations, harness.binding)
    check("a complete claim reconciles", report["verified_publications"] == 4
          and report["publications_on_disk"] == 4, str(report))

    refuses_with_code("a publication exists and the caller supplies []",
                      "RESTART_INVENTORY_MISMATCH", verify_restart, harness.out, {},
                      harness.binding)
    partial = dict(list(realisations.items())[:2])
    refuses_with_code("the caller omits half the store",
                      "RESTART_INVENTORY_MISMATCH", verify_restart, harness.out,
                      partial, harness.binding)
    invented = dict(realisations)
    ghost_job = first_job(harness.jobs, "C1_true_bridge_complete", scope="theta0_circular")
    ghost_exec = harness.execution(
        CampaignJob(JobCoordinates("C1_true_bridge_complete", "sigma_psi_0p2", 5,
                                   "theta0_circular"),
                    ghost_job.role, ghost_job.requires_calibration,
                    ghost_job.seed_families, ghost_job.branch_a_scopes,
                    ghost_job.result_kind, ()))
    ghost = harness.realise(ghost_exec)
    invented[ghost_exec.coordinates.job_id] = ghost
    refuses_with_code("the caller claims a publication whose bytes are missing",
                      "RESTART_INVENTORY_MISMATCH", verify_restart, harness.out,
                      invented, harness.binding)
    mislabelled = dict(list(realisations.items())[:3])
    mislabelled["C1_true_bridge_complete|sigma_psi_0p0|000000|wrong"] = \
        realisations[sorted(realisations)[0]]
    refuses_with_code("a restart record filed under the wrong key",
                      "RESTART_INVENTORY_MISMATCH", verify_restart, harness.out,
                      mislabelled, harness.binding)
    harness.close()

    # a publication belonging to no planned job
    harness = Harness()
    execution, realisation, path = published(harness, "C1_true_bridge_complete")
    undeclared = [j for j in harness.jobs
                  if j.coordinates.case_id != "C1_true_bridge_complete"]
    refuses_with_code("a publication for a job this campaign never declared",
                      "RESTART_INVENTORY_MISMATCH", verify_restart, harness.out,
                      {execution.coordinates.job_id: realisation}, harness.binding,
                      undeclared)
    harness.close()

    # a DUPLICATE publication: two committed records claiming the same coordinates
    harness = Harness()
    execution, realisation, path = published(harness, "C1_true_bridge_complete")
    directory, basename = publication_directory(harness.out), os.path.basename(path)
    import shutil as _shutil
    copy_base = "branch_a_" + "0" * 64 + ".json"
    _shutil.copy(os.path.join(directory, basename), os.path.join(directory, copy_base))
    _shutil.copy(os.path.join(directory, commit_name(basename)),
                 os.path.join(directory, commit_name(copy_base)))
    code = refusal_code(verify_restart, harness.out,
                        {execution.coordinates.job_id: realisation}, harness.binding)
    check("a duplicated publication refuses",
          code in ("RESTART_INVENTORY_MISMATCH", "PUBLICATION_INCOMPLETE"), str(code))
    harness.close()


def test_restart_cannot_delete_history() -> None:
    """Persisted scientific evidence is append-only, on every path."""
    harness = Harness()
    realisations = {}
    for scope in FIELDS[:2]:
        execution, realisation, path = published(harness, "C1_true_bridge_complete",
                                                 scope)
        realisations[execution.coordinates.job_id] = realisation
    directory = publication_directory(harness.out)
    before = sorted(os.listdir(directory))
    verify_restart(harness.out, realisations, harness.binding)
    check("a successful reconciliation writes nothing and deletes nothing",
          sorted(os.listdir(directory)) == before)
    refusal_code(verify_restart, harness.out, {}, harness.binding)
    check("a REFUSED reconciliation also writes nothing and deletes nothing",
          sorted(os.listdir(directory)) == before, str(sorted(os.listdir(directory))))
    check("inventory_publications is a pure read",
          set(inventory_publications(harness.out)) == set(realisations)
          and sorted(os.listdir(directory)) == before)
    harness.close()


# ------------------------------------------- E. transactional state transitions
def test_every_transition_is_atomic() -> None:
    """AUDIT FINDING D. A deterministic injected failure never advances a job.

    VALIDATE, PERFORM, VERIFY, THEN COMMIT THE TRANSITION. The audit found
    `analyse` doing the reverse; this walks every transition of the frozen
    dependency graph and proves the rule holds at each one.
    """
    # 1. Branch-A realisation: evidence from another stream
    harness = Harness()
    job = first_job(harness.jobs, "C2_geometry_false_rejection")
    execution = harness.execution(job)
    before = execution.state
    refuses_with_code("realisation with a foreign Branch-A seed",
                      "BRANCH_A_PROVENANCE_MISMATCH", execution.realise_branch_a,
                      noiseless_field(job.coordinates.scope), branch_a_seed=1,
                      common_mode_seed=execution.calibration.common_mode_seed(),
                      generator_identity="STATIC-FIXTURE-NO-DRAW")
    check("a refused realisation leaves the job PLANNED",
          execution.state == before == PLANNED, execution.state)
    harness.close()

    # 2. publication: injected failure at the durability point
    harness = Harness()
    job = first_job(harness.jobs, "C2_geometry_false_rejection")
    execution = harness.execution(job)
    harness.realise(execution)
    with inject("fsync_dir", 1):
        try:
            execution.publish_branch_a()
        except BaseException:                     # noqa: BLE001
            pass
    check("a refused publication leaves the job BRANCH_A_REALIZED",
          execution.state == BRANCH_A_REALIZED, execution.state)
    harness.close()

    # 3. condition binding: the publication no longer verifies
    harness = Harness()
    execution, realisation, path = published(harness)
    os.remove(os.path.join(publication_directory(harness.out),
                           commit_name(os.path.basename(path))))
    refuses_with_code("binding a condition against an uncommitted publication",
                      "PUBLICATION_ORPHANED", execution.calibration_condition)
    check("a refused condition binding leaves the job BRANCH_A_PUBLISHED",
          execution.state == BRANCH_A_PUBLISHED, execution.state)
    harness.close()

    # 4. calibration lock: an artifact from another condition
    harness = Harness()
    execution, realisation, path = published(harness)
    condition = execution.calibration_condition()
    other = first_job(harness.jobs, "C2_geometry_false_rejection", scope="theta1_power")
    other_exec = harness.execution(other)
    other_real = harness.realise(other_exec)
    refuses_with_code("locking an artifact calibrated elsewhere",
                      "BRANCH_A_PROVENANCE_MISMATCH", execution.lock_calibration,
                      fixture_artifact(other_real.calibration_condition(harness.binding)))
    check("a refused lock leaves the job CALIBRATION_CONDITION_BOUND",
          execution.state == CALIBRATION_CONDITION_BOUND, execution.state)

    # 5. unblind: the publication is tampered with after the lock
    execution.lock_calibration(fixture_artifact(condition))
    check("locking advanced to CALIBRATION_LOCKED",
          execution.state == CALIBRATION_LOCKED, execution.state)
    recommit(publication_directory(harness.out), os.path.basename(path),
             lambda r: r["package_identities"].__setitem__("plan_sha256", "0" * 64))
    refuses_with_code("unblinding against an altered publication",
                      "PUBLICATION_DIGEST_MISMATCH", execution.unblind)
    check("a refused unblind leaves the job CALIBRATION_LOCKED",
          execution.state == CALIBRATION_LOCKED, execution.state)
    check("Branch B is STILL unreachable after the refused unblind",
          refusal_code(execution.branch_b_seed) == "BRANCH_B_PREMATURE")
    harness.close()

    # 6. analysis: the outcome cannot be copied (THE AUDIT'S EXACT SCENARIO)
    harness = Harness()
    execution, realisation, path = unblinded(harness)
    from collections.abc import Mapping as _Mapping

    class HostileOutcome(_Mapping):
        """A real Mapping whose iteration fails, so dict(x) genuinely raises."""

        def __getitem__(self, key):
            raise KeyError(key)

        def __iter__(self):
            raise RuntimeError("INJECTED: the analysis outcome could not be copied")

        def __len__(self):
            return 1

    refuses_with_code("an analysis outcome that cannot be copied",
                      "RESULT_SCHEMA_INVALID", execution.analyse, HostileOutcome())
    check("a FAILED analysis leaves the job BRANCH_B_UNBLINDED, not ANALYSED",
          execution.state == BRANCH_B_UNBLINDED, execution.state)
    refuses_with_code("an EMPTY analysis outcome", "RESULT_SCHEMA_INVALID",
                      execution.analyse, {})
    refuses_with_code("an outcome that is not canonically serialisable",
                      "RESULT_SCHEMA_INVALID", execution.analyse,
                      {"beta_hat": float("nan")})
    refuses_with_code("an outcome with non-string keys", "RESULT_SCHEMA_INVALID",
                      execution.analyse, {1: "x"})
    check("after four refused analyses the job is STILL not ANALYSED",
          execution.state == BRANCH_B_UNBLINDED, execution.state)
    check("and recording is therefore still impossible",
          refusal_code(execution.record,
                       c2_aggregate(execution.job.coordinates.subcondition_id))
          == "JOB_STATE_INVALID")
    execution.analyse(endpoint_outcome(execution.coordinates.case_id))
    check("a VALID outcome does advance to ANALYSED", execution.state == ANALYSED)

    # 7. record: a refused record leaves the job ANALYSED
    refuses_with_code("recording with a foreign aggregate", "RESULT_CASE_MISMATCH",
                      execution.record, aggregate_skeleton("C7_false_bridge"))
    check("a refused record leaves the job ANALYSED, not RECORDED",
          execution.state == ANALYSED, execution.state)
    execution.record(c2_aggregate(execution.job.coordinates.subcondition_id))
    check("a valid record advances to RECORDED", execution.state == RECORDED)
    check("RECORDED is terminal: nothing follows it",
          refusal_code(execution.analyse, {"a": 1}) == "JOB_STATE_INVALID")
    harness.close()


def test_structured_refusal_is_a_result() -> None:
    """A scientific refusal is RECORDED, never retried, dropped or reclassified."""
    harness = Harness()
    execution, realisation, path = unblinded(harness)
    # A STRUCTURED SCIENTIFIC REFUSAL. P1 fails closed, so `p1_rejected` is True
    # and well defined; the two block decisions genuinely do not exist because the
    # frozen gate produced no p-values, and the record says why.
    refusal_outcome = endpoint_outcome(
        execution.coordinates.case_id, analysis_status="RANK_GUARD_FAIL",
        refusal_reason="rank guard", beta_hat=None, P1=False, p1_rejected=True,
        block1_rejected=None, g5_rejected=None)
    execution.analyse(refusal_outcome)
    recorded = execution.record(c2_aggregate(execution.job.coordinates.subcondition_id))
    check("a structured scientific refusal reaches a TERMINAL record",
          recorded["terminal_state"] == RECORDED)
    check("the refusal survives verbatim in the record",
          recorded["result"]["analysis_status"] == "RANK_GUARD_FAIL"
          and recorded["result"]["refusal_reason"] == "rank guard")
    check("it was not converted into a software error and not dropped",
          revalidate(harness, execution, recorded) is None)
    check("no second seed can be drawn to replace it: the Branch-B stream is a "
          "pure function of the frozen coordinates, so 'retry under another seed' "
          "is not an operation this interface has",
          execution.branch_b_seed() == execution.branch_b_seed())
    check("and the refusal was not converted into a software error: it is stored "
          "as the job's scientific result",
          recorded["result"]["analysis_status"] == "RANK_GUARD_FAIL")
    harness.close()


# ------------------------------- F. completeness, aggregation, classification
def test_campaign_completeness_and_aggregation() -> None:
    """AUDIT-ADJACENT. A case rate's denominator is the DECLARED job set."""
    jobs = plan_campaign(PLAN)
    total = len(jobs)
    check("the planned total is DERIVED from the frozen plan, never written down",
          total == sum(len(c["subconditions"]) * c["replicate_count"]
                       * len(c["fields_affected"]) for c in PLAN["cases"]), str(total))
    sample = tuple(jobs[:8])

    def terminal(job, state=RECORDED):
        return {"schema": "e1a_v4_validation_job_record/1", "job_id": job.job_id,
                "coordinates": job.coordinates.as_dict(), "terminal_state": state}

    complete = {job.job_id: terminal(job) for job in sample}
    report = require_campaign_completeness(sample, complete)
    check("a complete job set reports zero missing, extra and duplicate",
          report["missing_terminal_jobs"] == 0 and report["extra_terminal_jobs"] == 0
          and report["duplicate_terminal_jobs"] == 0 and report["declared_jobs"] == 8)
    missing = {k: v for k, v in list(complete.items())[:-1]}
    refuses_with_code("a MISSING terminal record", "CAMPAIGN_INCOMPLETE",
                      require_campaign_completeness, sample, missing)
    extra = dict(complete)
    extra["C1_true_bridge_complete|sigma_psi_0p0|999999|theta0_circular"] = {
        "terminal_state": RECORDED, "coordinates": {}}
    refuses_with_code("an EXTRA terminal record belonging to no planned job",
                      "CAMPAIGN_INCOMPLETE", require_campaign_completeness, sample, extra)
    unfinished = dict(complete)
    key = sorted(unfinished)[0]
    unfinished[key] = terminal(sample[0], state=ANALYSED)
    refuses_with_code("a record that never reached its terminal state",
                      "CAMPAIGN_INCOMPLETE", require_campaign_completeness, sample,
                      unfinished)
    duplicated = sample + (sample[0],)
    refuses_with_code("a duplicated planned job", "CAMPAIGN_PLAN_MISMATCH",
                      require_campaign_completeness, duplicated, complete)

    # aggregation derives case membership from the PLANNED job, not the record
    aggregates = assemble_case_aggregates(sample, complete)
    check("aggregation groups by the immutable planned case identity",
          set(aggregates) == {"C1_true_bridge_complete"}, str(sorted(aggregates)))
    substituted = dict(complete)
    victim = sorted(substituted)[0]
    substituted[victim] = dict(substituted[victim])
    substituted[victim]["coordinates"] = dict(substituted[victim]["coordinates"])
    substituted[victim]["coordinates"]["case_id"] = "C7_false_bridge"
    refuses_with_code("a record claiming a different case than its planned job",
                      "RESULT_CASE_MISMATCH", assemble_case_aggregates, sample,
                      substituted)


def test_release_subconditions_follow_frozen_authority() -> None:
    """The release unit is the plan's, not the driver's."""
    from e1a_v4.validation.campaign_driver import release_subconditions
    for case_id, expected in (
            ("C1_true_bridge_complete", ("sigma_psi_0p5",)),
            ("C2_geometry_false_rejection", ("sigma_psi_0p5",)),
            ("C3_g5_block", ("sigma_psi_0p5",))):
        check(f"{case_id}: the PRIMARY subcondition alone carries the release claim",
              release_subconditions(PLAN, case_id) == expected,
              str(release_subconditions(PLAN, case_id)))
    check("C5: every one of the twelve declared cells is a release unit",
          len(release_subconditions(PLAN, "C5_plug_in_branch_a")) == 12)
    check("C6: each of the three declared rho is a release unit",
          len(release_subconditions(PLAN, "C6_mode_resolution_boundary")) == 3)
    check("C7: each of the four alternatives is a release unit, never pooled",
          len(release_subconditions(PLAN, "C7_false_bridge")) == 4)
    check("the secondary and stress sigma_psi scenarios are NOT pooled into the "
          "primary claim",
          "sigma_psi_1p0" not in release_subconditions(PLAN, "C1_true_bridge_complete"))


# ------------------------------- G. the stochastic execution path, without RNG
def test_execution_gate_refuses_before_any_rng() -> None:
    """The gate is complete, ordered, and passed BEFORE a provider exists."""
    harness = Harness()
    out = os.path.join(harness.root, harness.binding.output_dir)
    FAKE_SUPPLIERS_BEFORE_GATE[0] = FakeSupplier.CONSTRUCTED
    code = refusal_code(require_execution_lifecycle, harness.root, harness.binding, out)
    check("the complete lifecycle gate REFUSES on this package",
          code == "EXECUTION_SEAL_NOT_FROZEN", str(code))
    check("no RNG object was constructed by the gate",
          SentinelRNG.CONSTRUCTED == 0 and SentinelRNG.DRAWS == 0)
    check("no deterministic supplier was constructed either",
          FakeSupplier.CONSTRUCTED == FAKE_SUPPLIERS_BEFORE_GATE[0],
          f"{FakeSupplier.CONSTRUCTED} vs {FAKE_SUPPLIERS_BEFORE_GATE[0]}")

    # the driver's own entry point refuses at the same place
    check("run_campaign refuses at the gate",
          refusal_code(run_campaign, harness.root) == "EXECUTION_SEAL_NOT_FROZEN")

    # and the production provider, if it were ever reached, refuses too
    provider = AuthorisedStochasticProvider(harness.binding)
    refuses_with_code("the production provider asked for a generator",
                      "STOCHASTIC_PROVIDER_REFUSED", provider.generator, 1, "branch_b")
    check("its refusal names the UNDECLARED generator as an authority gap",
          "NOT DECLARED in frozen authority" in UNDECLARED_GENERATOR
          and "PRNG algorithm" in UNDECLARED_GENERATOR)
    check("the provider counted the request rather than silently returning None",
          provider.requests == 1)
    harness.close()


def test_production_resolver_names_its_authority_gaps() -> None:
    """The resolver refuses rather than defaulting an undeclared input."""
    harness = Harness()
    job = first_job(harness.jobs, "C1_true_bridge_complete")
    code = refusal_code(resolve_job_specification, harness.binding, job)
    check("resolving a declared field's job still refuses",
          code == "CAMPAIGN_PLAN_MISMATCH", str(code))
    message = ""
    try:
        resolve_job_specification(harness.binding, job)
    except Refusal as exc:
        message = str(exc)
    check("it names the undeclared field-construction inputs exactly",
          UNDECLARED_FIELD_INPUTS in message, message[-90:])
    check("and it names each of the three by name",
          all(token in UNDECLARED_FIELD_INPUTS
              for token in ("calibration_route", "viscosity", "bead_radius")))
    c6 = first_job(harness.jobs, "C6_mode_resolution_boundary")
    try:
        resolve_job_specification(harness.binding, c6)
    except Refusal as exc:
        message = str(exc)
    check("C6's undeclared field construction is named separately",
          UNDECLARED_C6_FIELD in message)
    check("and it says why the driver must not supply one: the eigenvalue ratio "
          "IS the quantity under test",
          "refuses to invent a geometry" in UNDECLARED_C6_FIELD)
    check("C8's beta truth is prose, so the driver refuses to read it as a "
          "generating parameter",
          refusal_code(declared_beta_true, PLAN, "C8_blinded_scale_control",
                       "paired_scale_control", "theta0_circular")
          == "CAMPAIGN_PLAN_MISMATCH")
    check("C7's per-alternative beta vector IS machine-readable and is read",
          declared_beta_true(PLAN, "C7_false_bridge", "alt_1_06", "theta1_power")
          == 1.06)
    check("a scalar beta truth is read as declared",
          declared_beta_true(PLAN, "C1_true_bridge_complete", "sigma_psi_0p5",
                             "theta0_circular") == 1.0)
    harness.close()


def test_fake_orchestration_end_to_end() -> None:
    """The FULL control flow, with a deterministic supplier. NOT a scientific run.

    Nothing below is a measurement. The supplier is a van der Corput sequence, so
    the endpoint verdicts are arbitrary and are never read as results; what is
    being proved is that the frozen dependency graph is walked in the frozen
    order, that publication precedes unblinding, and that every job reaches
    exactly one terminal record.
    """
    for case_id, label, calibrating in (
            ("C7_false_bridge", "a NO-CALIBRATION case", False),
            ("C8_blinded_scale_control", "the C8 PAIRED case", False),
            ("C1_true_bridge_complete", "a CALIBRATION-REQUIRING case", True)):
        harness = Harness()
        key, group = next((k, g) for k, g in replicate_groups(harness.jobs)
                          if k[0] == case_id)
        provider = FakeProvider()
        result = execute_campaign(harness.binding, group, provider, harness.out,
                                  resolver=fixture_resolver, ledger=harness.ledger)
        check(f"{label}: every job of the replicate reached a terminal record",
              len(result["executed_jobs"]) == len(group)
              and result["completeness"]["missing_terminal_jobs"] == 0)
        check(f"{label}: a partial job set is NOT classified",
              result["complete_campaign"] is False and result["classification"] is None)
        purposes = [p for _, p in provider.requests]
        check(f"{label}: the common mode was drawn ONCE for the experiment",
              purposes.count("branch_a_common_mode") == 1, str(purposes.count(
                  "branch_a_common_mode")))
        check(f"{label}: one Branch-A stream per field",
              purposes.count("branch_a_measurement") == len(group))
        check(f"{label}: one Branch-B stream per field",
              purposes.count("branch_b") == len(group))
        check(f"{label}: calibration streams match the case's declared requirement",
              purposes.count("calibration") == (len(group) if calibrating else 0),
              f"{purposes.count('calibration')} for requires_calibration={calibrating}")
        check(f"{label}: every Branch-A publication is COMMITTED on disk",
              len(inventory_publications(harness.out)) == len(group))
        for record in result["records"].values():
            check(f"{label}: {record['job_id']} stores its publication digest and "
                  "re-validates",
                  bool(record["publication_digest"])
                  and refusal_code(
                      validate_job_record, record, harness.binding.plan,
                      harness.binding,
                      next(j for j in group if j.job_id == record["job_id"]),
                      harness.out) is None)
            break
        if case_id == "C8_blinded_scale_control":
            sample = result["records"][sorted(result["records"])[0]]["result"]
            check("C8: BOTH declared scale factors were evaluated on ONE replicate",
                  sample.get("scale_factors") == [1.07, 0.9]
                  and isinstance(sample.get("scale_recovered"), bool),
                  str(sample.get("scale_factors")))
            check("C8: no calibration artifact was locked for it",
                  harness.ledger.artifact_count == 0)
        if case_id == "C7_false_bridge":
            check("C7: no calibration artifact was locked for it",
                  harness.ledger.artifact_count == 0)
        if calibrating:
            check("a calibrating case locked exactly one artifact per field",
                  harness.ledger.artifact_count == len(group),
                  str(harness.ledger.artifact_count))
        harness.close()


def test_fake_orchestration_refusal_and_restart() -> None:
    """A structured refusal is a result; a resumed campaign never re-runs a job."""
    harness = Harness()
    key, group = next((k, g) for k, g in replicate_groups(harness.jobs)
                      if k[0] == "C7_false_bridge")
    provider = FakeProvider()
    first = execute_campaign(harness.binding, group, provider, harness.out,
                             resolver=fixture_resolver)
    published_now = inventory_publications(harness.out)
    check("the first pass published every job of the replicate",
          len(published_now) == len(group))

    # RESUME after the publishing process is gone: the checkpoint is RECOVERED
    # from the publications themselves, never carried in memory and never
    # regenerated under a fresh seed.
    realisations = recover_realisations(harness.out, harness.binding)
    check("recovery rebuilds exactly the published evidence, losslessly",
          set(realisations) == set(published_now)
          and all(realisations[j].evidence_sha256
                  == published_now[j]["branch_a_evidence_sha256"]
                  for j in realisations))
    resumed = execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                               resolver=fixture_resolver, realisations=realisations)
    check("a resumed campaign re-runs NOTHING that is already published",
          resumed["executed_jobs"] == [], str(resumed["executed_jobs"]))
    check("and the published evidence is untouched",
          len(inventory_publications(harness.out)) == len(group))

    # a caller that 'forgets' an artifact cannot resume past it
    partial = dict(list(realisations.items())[:2])
    refuses_with_code("resuming while omitting half the published evidence",
                      "RESTART_INVENTORY_MISMATCH", execute_campaign,
                      harness.binding, group, FakeProvider(), harness.out,
                      resolver=fixture_resolver, realisations=partial)
    harness.close()


def test_no_production_bypass_reaches_a_provider() -> None:
    """There is no argument, flag or path that carries a generator past the gate."""
    import inspect
    signature = inspect.signature(run_campaign)
    check("run_campaign takes only root, output_dir and plan_only",
          set(signature.parameters) == {"root", "output_dir", "plan_only"},
          str(sorted(signature.parameters)))
    source = open(os.path.join(ROOT, OFFICIAL_CAMPAIGN_DRIVER_PATH),
                  encoding="utf-8").read()
    for token in ("force=True", "skip_gate", "ignore_seal", "test_mode",
                  "rng_factory"):
        check(f"the driver source declares no {token!r} bypass",
              f"{token}=" not in source.replace(f"`{token}`", "")
              or token in ("rng_factory",) and "rng_factory=" not in source,
              token)
    tree = __import__("ast").parse(source)
    entry = next(n for n in tree.body
                 if isinstance(n, __import__("ast").FunctionDef)
                 and n.name == "run_campaign")
    names = [a.arg for a in entry.args.args + entry.args.kwonlyargs]
    check("the AST confirms run_campaign's parameter list",
          names == ["root", "output_dir", "plan_only"], str(names))
    # the gate is lexically BEFORE the provider construction in run_campaign
    body = source.split("def run_campaign(", 1)[1].split("\ndef ", 1)[0]
    check("the lifecycle gate appears before the provider is constructed",
          body.index("require_execution_lifecycle")
          < body.index("AuthorisedStochasticProvider"))
    check("execute_campaign is never called before the gate in run_campaign",
          body.index("require_execution_lifecycle") < body.index("execute_campaign("))
    check("the CLI exposes no provider, resolver or aggregator argument",
          "--provider" not in source and "--resolver" not in source
          and "--aggregator" not in source)


def test_authority_still_unchanged_by_this_repair() -> None:
    """NO E1a SCIENTIFIC DECISION RULE CHANGED. Byte-level, on every source."""
    for label, path, digest in (
            ("physical foundation",
             "docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md",
             "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507"),
            ("theory baseline", "docs/theory/EBU_THEORY_BASELINE.md",
             "0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa"),
            ("design contract", CONTRACT_JSON,
             "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b"),
            ("prospective design", "docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md",
             "e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495"),
            ("seed map", SEED_MAP_JSON,
             "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce")):
        check(f"the {label} is BYTE-unchanged by this repair",
              sha256_file(os.path.join(ROOT, path)) == digest)
    check("the JSON plan is byte-unchanged", sha256_file(os.path.join(ROOT, PLAN_JSON))
          == PLAN_JSON_SHA256)
    check("the Markdown plan is byte-unchanged",
          sha256_file(os.path.join(ROOT, PLAN_MARKDOWN)) == PLAN_MARKDOWN_SHA256)
    check("the execution seal is still PRE_DRIVER",
          strict_load_file(os.path.join(ROOT, SEAL_JSON), "seal")["state"] == "PRE_DRIVER")
    check("the final expected execution identity is still null",
          PLAN["frozen_identities"]["final_expected_execution_identity"] is None)
    check("execution_authorised is still false", PLAN["execution_authorised"] is False)
    check("the campaign has produced no results directory",
          not os.path.exists(os.path.join(ROOT, "results/e1a_v4_validation")))


def test_deterministic_supplier_is_not_an_rng() -> None:
    """The fake suppliers are reported separately and are never called scientific."""
    check("NO REAL RNG OBJECT WAS CONSTRUCTED ANYWHERE IN THIS SUITE",
          SentinelRNG.CONSTRUCTED == 0, str(SentinelRNG.CONSTRUCTED))
    check("NO REAL RANDOM NUMBER WAS DRAWN", SentinelRNG.DRAWS == 0,
          str(SentinelRNG.DRAWS))
    a, b = FakeSupplier(7), FakeSupplier(7)
    check("the deterministic supplier is reproducible: same seed, same values",
          a.normal(8) == b.normal(8))
    check("it has no entropy source and no hidden state",
          set(vars(FakeSupplier(1))) == {"i"})
    check("its values are counted and reported SEPARATELY from scientific draws",
          FakeSupplier.VALUES > 0 and SentinelRNG.DRAWS == 0,
          f"deterministic values={FakeSupplier.VALUES}, random draws={SentinelRNG.DRAWS}")



def test_publication_and_result_restart_interactions() -> None:
    """Crash-shaped states, and what a resume is allowed to conclude from each.

        publication prepared but not committed   -> INCOMPLETE, refuse
        publication committed                    -> verify and resume
        publication bytes exist, commit absent   -> ORPHAN, refuse
        inventory says committed, bytes missing  -> refuse
        analysis done, result not committed      -> refuse (authorised recovery)
        result committed, publication missing    -> refuse
    """
    from e1a_v4.validation.campaign_driver import (
        inventory_job_records, job_record_basename, job_record_directory,
    )

    def one_replicate(harness):
        return next((k, g) for k, g in replicate_groups(harness.jobs)
                    if k[0] == "C7_false_bridge")

    # 1. a completed pass, then a clean resume that re-runs nothing
    harness = Harness()
    key, group = one_replicate(harness)
    execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                     resolver=fixture_resolver)
    records_dir = job_record_directory(harness.out)
    check("every terminal record is durably COMMITTED, not merely written",
          len(inventory_job_records(harness.out, harness.binding, group)) == len(group))
    check("each terminal record is filed at a path derived from its coordinates",
          all(os.path.isfile(os.path.join(records_dir,
                                          job_record_basename(job.coordinates)))
              for job in group))
    resumed = execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                               resolver=fixture_resolver,
                               realisations=recover_realisations(harness.out,
                                                                 harness.binding))
    check("a committed campaign resumes, verifies and re-runs nothing",
          resumed["executed_jobs"] == [] and
          resumed["completeness"]["missing_terminal_jobs"] == 0)

    # 2. ANALYSIS COMPLETED, RESULT NOT COMMITTED: remove one terminal record
    victim = sorted(os.listdir(records_dir))[0]
    if is_commit_name(victim):
        victim = sorted(n for n in os.listdir(records_dir)
                        if not is_commit_name(n) and n.endswith(".json"))[0]
    os.remove(os.path.join(records_dir, victim))
    os.remove(os.path.join(records_dir, commit_name(victim)))
    refuses_with_code("a job that published evidence and committed no result",
                      "RESTART_INVENTORY_MISMATCH", execute_campaign,
                      harness.binding, group, FakeProvider(), harness.out,
                      resolver=fixture_resolver,
                      realisations=recover_realisations(harness.out, harness.binding))
    check("the refusal preserves every surviving record and publication",
          len(inventory_publications(harness.out)) == len(group))
    harness.close()

    # 3. RESULT COMMITTED, PUBLICATION MISSING
    harness = Harness()
    key, group = one_replicate(harness)
    execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                     resolver=fixture_resolver)
    store = publication_directory(harness.out)
    gone = sorted(n for n in os.listdir(store)
                  if not is_commit_name(n) and n.endswith(".json"))[0]
    os.remove(os.path.join(store, gone))
    os.remove(os.path.join(store, commit_name(gone)))
    # The provenance verifier now names this precisely: the record's upstream
    # evidence is gone, so the record is not evidence of a completed job.
    refuses_with_code("a terminal record whose Branch-A evidence is gone",
                      "TERMINAL_PROVENANCE_MISMATCH", execute_campaign,
                      harness.binding, group, FakeProvider(), harness.out,
                      resolver=fixture_resolver,
                      realisations=recover_realisations(harness.out, harness.binding))
    harness.close()

    # 4. A TERMINAL RECORD EDITED AFTER COMMIT
    harness = Harness()
    key, group = one_replicate(harness)
    execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                     resolver=fixture_resolver)
    records_dir = job_record_directory(harness.out)
    target = sorted(n for n in os.listdir(records_dir)
                    if not is_commit_name(n) and n.endswith(".json"))[0]
    record = read_published(os.path.join(records_dir, target), "record")
    record["result"]["complete_pass"] = True
    write_record(os.path.join(records_dir, target), record)
    refuses_with_code("an edited terminal record on resume", "PUBLICATION_INCOMPLETE",
                      inventory_job_records, harness.out, harness.binding, group)
    harness.close()

    # 5. A TERMINAL RECORD FOR A JOB THIS CAMPAIGN NEVER DECLARED
    harness = Harness()
    key, group = one_replicate(harness)
    execute_campaign(harness.binding, group, FakeProvider(), harness.out,
                     resolver=fixture_resolver)
    other = [j for j in harness.jobs if j.coordinates.case_id != "C7_false_bridge"]
    refuses_with_code("a terminal record belonging to no planned job",
                      "RESTART_INVENTORY_MISMATCH", inventory_job_records,
                      harness.out, harness.binding, other)
    harness.close()


def test_diagnostic_aggregator_refuses_rather_than_reporting_nothing() -> None:
    """A case that owes a mandatory diagnostic refuses; it never reports an empty one."""
    from e1a_v4.validation.campaign_driver import (
        UNDECLARED_DIAGNOSTIC_AGGREGATOR, default_case_aggregate,
    )
    harness = Harness()
    for case_id, owes in (("C2_geometry_false_rejection", True),
                          ("C4_surrogate_validity", True),
                          ("C5_plug_in_branch_a", True),
                          ("C6_mode_resolution_boundary", True),
                          ("C7_false_bridge", False),
                          ("C8_blinded_scale_control", False),
                          ("C1_true_bridge_complete", False)):
        code = refusal_code(default_case_aggregate, harness.binding, case_id, ())
        if owes:
            check(f"{case_id}: refuses rather than reporting an empty diagnostic",
                  code == "CONTRACT_MANDATORY_DIAGNOSTIC_MISSING", str(code))
        else:
            check(f"{case_id}: owes no keyed diagnostic and aggregates cleanly",
                  code is None, str(code))
    check("the refusal names where the requirement is declared",
          "release_authority.mandatory_diagnostics" in UNDECLARED_DIAGNOSTIC_AGGREGATOR)
    harness.close()


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
    # --- the independent audit's five blocking findings, as regressions -------
    ("AUDIT A: the publication envelope binds every field",
     test_publication_envelope_binds_every_field),
    ("AUDIT A: the strict publication schema", test_publication_strict_schema),
    ("AUDIT D: publication fault injection", test_publication_fault_injection),
    ("AUDIT D: orphan and dangling detection", test_publication_orphan_detection),
    ("AUDIT B: case / result-type compatibility", test_case_result_type_compatibility),
    ("AUDIT B: the field set is derived from the job",
     test_field_set_derived_from_the_job),
    ("AUDIT B: mandatory diagnostics persist and round-trip",
     test_mandatory_diagnostic_persistence_and_round_trip),
    ("AUDIT B: result round trip, every case", test_result_round_trip_every_case),
    ("AUDIT C: restart reconciles with the persisted inventory",
     test_restart_reconciles_with_the_persisted_inventory),
    ("AUDIT C: restart cannot delete history", test_restart_cannot_delete_history),
    ("AUDIT D: every transition is atomic", test_every_transition_is_atomic),
    ("structured refusals stay results", test_structured_refusal_is_a_result),
    ("campaign completeness and case aggregation",
     test_campaign_completeness_and_aggregation),
    ("release units follow frozen authority",
     test_release_subconditions_follow_frozen_authority),
    ("AUDIT E: the execution gate refuses before any RNG",
     test_execution_gate_refuses_before_any_rng),
    ("AUDIT E: the resolver names its authority gaps",
     test_production_resolver_names_its_authority_gaps),
    ("AUDIT E: fake full-orchestration control flow",
     test_fake_orchestration_end_to_end),
    ("AUDIT E: fake refusal and restart paths",
     test_fake_orchestration_refusal_and_restart),
    ("publication and result restart interactions",
     test_publication_and_result_restart_interactions),
    ("the diagnostic aggregator refuses rather than reporting nothing",
     test_diagnostic_aggregator_refuses_rather_than_reporting_nothing),
    ("no production bypass reaches a provider",
     test_no_production_bypass_reaches_a_provider),
    ("frozen authority unchanged by this repair",
     test_authority_still_unchanged_by_this_repair),
    ("the deterministic supplier is not an RNG",
     test_deterministic_supplier_is_not_an_rng),
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
    print("  REAL CALIBRATION EXECUTIONS: 0")
    print("  REAL CAMPAIGN JOBS    : 0")
    print("Deterministic fixtures, reported separately and NEVER scientific execution:")
    print(f"  van der Corput suppliers constructed: {FakeSupplier.CONSTRUCTED}")
    print(f"  deterministic values supplied       : {FakeSupplier.VALUES}")
    raise SystemExit(1 if FAILED else 0)
