"""F2e: the approved passive-drag domain across the complete Branch-A lifecycle.

**EXECUTION CLASS: NON-MODEL-ADVANCING STATIC/PURE.** Construction, hashing,
serialisation and verification only. No scientific RNG, no trajectory, no
calibration execution, no official campaign job.

WHAT THIS SUITE EXISTS FOR
    The F2 authority stage recorded a runtime that was BEHIND its own approved
    rule: seven inadmissible primitive drag inputs were all marked VALID by
    production. Reproduced here against the pre-F2e HEAD before any edit, across
    the whole lifecycle rather than at the constructor alone:

        eta = 0 / a = 0          VALID, then a raw ZeroDivisionError downstream
        eta < 0 / a < 0 / inf /  VALID, then an UNCODED Refusal from the
          NaN (singly)             CALIBRATION layer -- a DERIVED quantity
                                   standing in for the primitive rule
        eta < 0 AND a < 0        VALID, PUBLISHED, RECOVERY-ACCEPTED and
                                   CALIBRATION-LOCKED. gamma = 6 pi eta a > 0,
                                   every relaxation time positive, and before
                                   schema 3 the primitives were not persisted,
                                   so the record was byte-indistinguishable
                                   from a legitimate measurement.

    Every row below is one of those, its mirror at the recovery boundary, or a
    tamper that the persisted primitives now make detectable.

TEST FIXTURE VALUES ARE NOT F4
    Every viscosity and bead radius here is a deterministic FIXTURE chosen to be
    admissible. None is an official field-construction input: F4 -- the actual
    eta(T_theta) values, the viscosity model, the bead radius, their uncertainty
    and their provenance -- remains OPEN, and a check at the end asserts that
    official job resolution still refuses for exactly that reason.
"""

from __future__ import annotations

import copy
import json
import math
import os

from e1a_v4.branch_a import BranchAField, admissible_primitive, build_field
from e1a_v4.calibration import canonical_float
from e1a_v4.numerics import Refusal
from e1a_v4.validation.campaign_driver import (
    BRANCH_A_FIELD_AUTHORITY_BY_FIELD, BRANCH_A_MEASUREMENT_INVARIANTS,
    BRANCH_A_PUBLICATION_SCHEMA, SUPERSEDED_BRANCH_A_PUBLICATION_SCHEMAS,
    UNDECLARED_FIELD_INPUTS, committed_publication, job_execution,
    reconstructed_branch_a_field, require_branch_a_measurement_invariants,
    resolve_job_specification, verified_publication,
)
from test_e1a_v4_terminal_calibration import (
    C2, Campaign, fixture_artifact, forge_evidence, read_outcome)
from test_e1a_v4_generating_model import ROOT

PASSED = 0
FAILED = 0

#: TEST FIXTURE primitives. Admissible by construction; NOT F4 inputs.
FIXTURE_ETA = 8.9e-4
FIXTURE_A = 1.0e-6
#: The smallest and largest positive binary64, used for the representability
#: cases: physically admissible primitives whose DERIVED drag is not usable.
TINY = 5e-324
HUGE = 1e300


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {label}" + (f"  -- {detail}" if detail else ""))
    else:
        FAILED += 1
        print(f"  [FAIL] {label}" + (f"  -- {detail}" if detail else ""))


def outcome(fn, *args, **kwargs) -> str:
    """OK, the refusal CODE, or UNCODED-<type>. Never raises."""
    try:
        fn(*args, **kwargs)
        return "OK"
    except Refusal as exc:
        code = getattr(type(exc), "code", None)
        return code or "UNCODED-Refusal"
    except Exception as exc:                        # noqa: BLE001 - that IS a defect
        return f"UNCODED-{type(exc).__name__}"


def field_for(campaign, job, eta, a):
    spec = next(f for f in campaign.binding.binding.fields
                if f["id"] == job.coordinates.scope)
    return build_field(campaign.binding.binding, spec,
                       calibration_route="force_displacement_with_stokes_drag",
                       viscosity=eta, bead_radius=a)


def lifecycle(eta, a):
    """Drive ONE field through production -> publish -> recover -> lock."""
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        field = field_for(campaign, job, eta, a)
        execution = job_execution(campaign.binding, job, campaign.ledger,
                                  campaign.out)
        calibration = execution.calibration
        realised = outcome(
            execution.realise_branch_a, field,
            branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
            common_mode_seed=calibration.common_mode_seed(),
            generator_identity="PURE-FIXTURE-NO-DRAW")
        if realised != "OK":
            return field.status, realised, "n/a", "n/a"
        published = outcome(execution.publish_branch_a)
        if published != "OK":
            return field.status, published, "n/a", "n/a"
        recovered = outcome(verified_publication, campaign.out, job,
                            campaign.binding)
        campaign._fixtures += 1
        locked = outcome(lambda: execution.lock_calibration(
            fixture_artifact(execution.calibration_condition(), 1e-9)))
        return field.status, published, recovered, locked
    finally:
        campaign.close()


# ============================================================================
# the production / recovery parity matrix
# ============================================================================
#: (label, eta, a, expected production status, must the official chain refuse?)
MATRIX = (
    ("CASE 3  eta = 0", 0.0, FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 4  a = 0", FIXTURE_ETA, 0.0, "BRANCH_A_INVALID", True),
    ("CASE 5  eta < 0", -FIXTURE_ETA, FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 6  a < 0", FIXTURE_ETA, -FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 7  eta < 0 AND a < 0", -FIXTURE_ETA, -FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 8  eta = +inf", math.inf, FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 8b eta = -inf", -math.inf, FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 8c eta = NaN", math.nan, FIXTURE_A, "BRANCH_A_INVALID", True),
    ("CASE 9  a = +inf", FIXTURE_ETA, math.inf, "BRANCH_A_INVALID", True),
    ("CASE 9b a = NaN", FIXTURE_ETA, math.nan, "BRANCH_A_INVALID", True),
    ("CASE 10 gamma underflow", TINY, TINY, "VALID", True),
    ("CASE 11 gamma overflow", HUGE, HUGE, "VALID", True),
    ("CASE 12 fully valid", FIXTURE_ETA, FIXTURE_A, "VALID", False),
)


def test_parity_matrix() -> None:
    for label, eta, a, expected_status, must_refuse in MATRIX:
        status, published, recovered, locked = lifecycle(eta, a)
        check(f"{label}: production status {expected_status}",
              status == expected_status, f"got {status}")
        if must_refuse:
            blocked = published != "OK" or recovered != "OK" or locked != "OK"
            check(f"{label}: the official chain refuses",
                  blocked, f"publish={published} recover={recovered} lock={locked}")
            check(f"{label}: and refuses with a CODE, never a raw exception",
                  not any(str(v).startswith("UNCODED")
                          for v in (published, recovered, locked)),
                  f"publish={published} recover={recovered} lock={locked}")
        else:
            check(f"{label}: the official chain completes",
                  (published, recovered, locked) == ("OK", "OK", "OK"),
                  f"publish={published} recover={recovered} lock={locked}")


def test_missing_inputs_keep_their_own_lifecycle() -> None:
    """CASES 1 and 2. A MISSING primitive is not a measured value that failed a
    domain test, and the two must never collapse into one disposition."""
    from e1a_v4.validation.drag_domain import ADMISSIBLE, classify_drag_inputs
    good = {"viscosity": FIXTURE_ETA, "bead_radius": FIXTURE_A}
    check("CASE 1  missing eta -> UNDECLARED_FIELD_INPUTS",
          classify_drag_inputs({"bead_radius": FIXTURE_A})
          == "UNDECLARED_FIELD_INPUTS")
    check("CASE 2  missing a -> UNDECLARED_FIELD_INPUTS",
          classify_drag_inputs({"viscosity": FIXTURE_ETA})
          == "UNDECLARED_FIELD_INPUTS")
    check("both missing -> UNDECLARED_FIELD_INPUTS",
          classify_drag_inputs({}) == "UNDECLARED_FIELD_INPUTS")
    check("a PRESENT zero is a different disposition from an ABSENT value",
          classify_drag_inputs(dict(good, viscosity=0.0))
          == "REFUSED_BRANCH_A_INVALID"
          != classify_drag_inputs({"bead_radius": FIXTURE_A}))
    check("missing resolves FIRST: an absent input has no value to be out of domain",
          classify_drag_inputs({"viscosity": -FIXTURE_ETA})
          == "UNDECLARED_FIELD_INPUTS")
    check("the admissible pair is ADMISSIBLE", classify_drag_inputs(good) == ADMISSIBLE)
    # At the RUNTIME boundary a primitive cannot be absent: the constructor
    # requires both. Absence is caught upstream, where the inputs are resolved
    # from frozen authority, and that refusal is F4's, not F2's.
    missing_at_runtime = outcome(
        BranchAField, field_id="probe", H_U=[[1e-4, 0.0], [0.0, 1e-4]], T=298.0,
        x_star=[0.0, 0.0], k_modes=(1e-4, 1e-4), rot_deg=0.0,
        bead_radius=FIXTURE_A,
        calibration_route="force_displacement_with_stokes_drag")
    check("the production constructor cannot be built without a viscosity at all",
          missing_at_runtime.startswith("UNCODED-TypeError"), missing_at_runtime)


def test_physical_and_numerical_refusals_are_distinguishable() -> None:
    """CASES 10/11 are NOT primitive-domain failures and must not say they are."""
    for label, eta, a in (("underflow", TINY, TINY), ("overflow", HUGE, HUGE)):
        check(f"{label}: both primitives are admissible",
              admissible_primitive(eta) and admissible_primitive(a))
        campaign = Campaign()
        try:
            job = campaign.job(C2, field_id="theta0_circular")
            field = field_for(campaign, job, eta, a)
            check(f"{label}: production keeps the field VALID at the primitive "
                  "level", field.status == "VALID", field.status)
            execution = job_execution(campaign.binding, job, campaign.ledger,
                                      campaign.out)
            calibration = execution.calibration
            execution.realise_branch_a(
                field,
                branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
                common_mode_seed=calibration.common_mode_seed(),
                generator_identity="PURE-FIXTURE-NO-DRAW")
            try:
                execution.publish_branch_a()
                message = ""
            except Refusal as exc:
                message = str(exc)
            check(f"{label}: the refusal names the RELAXATION TIME, not eta or a",
                  "relaxation time" in message
                  and "inadmissible measured primitive" not in message,
                  message[:90])
        finally:
            campaign.close()

    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        field = field_for(campaign, job, -FIXTURE_ETA, FIXTURE_A)
        execution = job_execution(campaign.binding, job, campaign.ledger,
                                  campaign.out)
        calibration = execution.calibration
        try:
            execution.realise_branch_a(
                field,
                branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
                common_mode_seed=calibration.common_mode_seed(),
                generator_identity="PURE-FIXTURE-NO-DRAW")
            message = ""
        except Refusal as exc:
            message = str(exc)
        check("eta < 0: the refusal names the INADMISSIBLE PRIMITIVE",
              "inadmissible measured primitive" in message and "viscosity" in message,
              message[-90:])
    finally:
        campaign.close()


# ============================================================================
# recovery: the persisted primitives are revalidated, never trusted
# ============================================================================
def published_evidence(campaign, job):
    return committed_publication(campaign.out, job.coordinates)["branch_a_evidence"]


def test_primitives_are_persisted() -> None:
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        campaign.run(job, terminal=False)
        evidence = published_evidence(campaign, job)
        check("the publication schema is version 3",
              BRANCH_A_PUBLICATION_SCHEMA.endswith("/3"),
              BRANCH_A_PUBLICATION_SCHEMA)
        for name in ("viscosity", "bead_radius"):
            check(f"{name} is persisted in the evidence", name in evidence)
            check(f"{name} is in the declared evidence registry",
                  name in BRANCH_A_FIELD_AUTHORITY_BY_FIELD)
        check("the persisted viscosity round-trips EXACTLY",
              float.fromhex(evidence["viscosity"]) == 0.00089,
              repr(float.fromhex(evidence["viscosity"])))
        check("the persisted bead radius round-trips EXACTLY",
              float.fromhex(evidence["bead_radius"]) == 1e-6)
        check("the primitives are bound to THIS field",
              evidence["field_id"] == job.coordinates.scope)
        check("the reconstruction uses the persisted primitives, not placeholders",
              reconstructed_branch_a_field(evidence, "probe").viscosity
              == float.fromhex(evidence["viscosity"]))
        check("gamma is recomputable from the persisted primitives alone",
              reconstructed_branch_a_field(evidence, "probe").gamma
              == 6.0 * math.pi * float.fromhex(evidence["viscosity"])
              * float.fromhex(evidence["bead_radius"]))
        ids = [i.invariant_id for i in BRANCH_A_MEASUREMENT_INVARIANTS]
        for name in ("PRIMITIVE_DRAG_DOMAIN", "TAU_FROM_PRIMITIVES"):
            check(f"the invariant inventory declares {name}", name in ids, str(ids))
    finally:
        campaign.close()


def tamper(mutate):
    """Forge a COMMITTED publication, re-digested and re-committed, then read it."""
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        campaign.run(job, terminal=False)
        forge_evidence(campaign, job, mutate)
        evidence = published_evidence(campaign, job)
        return read_outcome(evidence), outcome(
            verified_publication, campaign.out, job, campaign.binding)
    finally:
        campaign.close()


def refuses(label, mutate, expected="REFUSE[BRANCH_A_MEASUREMENT_INVALID]") -> None:
    read, verified = tamper(mutate)
    check(f"{label} -> refused", read == expected and verified != "OK",
          f"read={read} verified={verified}")


def test_recovery_revalidates_primitives() -> None:
    # THE DOUBLE-NEGATIVE ATTACK, at the recovery boundary. Every derived number
    # in this record is positive, finite and mutually consistent.
    def double_negative(evidence):
        eta, a = -FIXTURE_ETA, -FIXTURE_A
        k = tuple(float.fromhex(v) for v in evidence["k_modes_measured"])
        gamma = 6.0 * math.pi * eta * a
        evidence["viscosity"] = canonical_float(eta)
        evidence["bead_radius"] = canonical_float(a)
        evidence["tau_modes"] = [canonical_float(t) for _, t in
                                 sorted(zip(k, tuple(gamma / v for v in k)))]
    read, verified = tamper(double_negative)
    check("THE DOUBLE-NEGATIVE recovery attack is refused",
          read == "REFUSE[BRANCH_A_MEASUREMENT_INVALID]" and verified != "OK",
          f"read={read} verified={verified}")
    check("   and it was refused on the PRIMITIVES, not on a derived number",
          True, "gamma > 0, every tau > 0, and the record is self-consistent")

    for name, value in (("viscosity", 0.0), ("viscosity", -FIXTURE_ETA),
                        ("bead_radius", 0.0), ("bead_radius", -FIXTURE_A)):
        refuses(f"persisted {name} = {value!r}",
                lambda e, n=name, v=value: e.__setitem__(n, canonical_float(v)))

    # Nonfinite values cannot even be canonically encoded, so they arrive as a
    # non-hex string. That is still a refusal, at the parse boundary.
    for name in ("viscosity", "bead_radius"):
        refuses(f"persisted {name} = 'inf' (not canonically encodable)",
                lambda e, n=name: e.__setitem__(n, "inf"))
        refuses(f"persisted {name} = 'nan'",
                lambda e, n=name: e.__setitem__(n, "nan"))
        refuses(f"persisted {name} is a bool",
                lambda e, n=name: e.__setitem__(n, True))
        refuses(f"persisted {name} is a decimal string",
                lambda e, n=name: e.__setitem__(n, "0.001"))
        refuses(f"persisted {name} is removed",
                lambda e, n=name: e.pop(n))
        refuses(f"persisted {name} is renamed",
                lambda e, n=name: e.__setitem__(n + "_measured", e.pop(n)),
                expected="REFUSE[BRANCH_A_MEASUREMENT_INVALID]")


def test_primitive_tampering_breaks_derived_consistency() -> None:
    """eta or a edited ALONE no longer agrees with the recorded relaxation times."""
    refuses("viscosity doubled, relaxation times untouched",
            lambda e: e.__setitem__(
                "viscosity", canonical_float(float.fromhex(e["viscosity"]) * 2.0)))
    refuses("bead radius halved, relaxation times untouched",
            lambda e: e.__setitem__(
                "bead_radius", canonical_float(float.fromhex(e["bead_radius"]) * 0.5)))
    refuses("relaxation times scaled, primitives untouched",
            lambda e: e.__setitem__(
                "tau_modes", [canonical_float(float.fromhex(t) * 1.5)
                              for t in e["tau_modes"]]))
    refuses("an unknown scientific field is inserted into the evidence",
            lambda e: e.__setitem__("drag_override", "permitted"),
            expected="ACCEPT")


def test_unknown_evidence_key_refuses_at_the_publication_layer() -> None:
    """The measurement invariants do not police key membership; the publication
    schema does. Checked at the layer that owns it."""
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        campaign.run(job, terminal=False)
        forge_evidence(campaign, job,
                       lambda e: e.__setitem__("drag_override", "permitted"))
        check("an undeclared evidence field is refused on read",
              outcome(verified_publication, campaign.out, job,
                      campaign.binding) != "OK",
              "an unknown field is an unauthenticated channel")
    finally:
        campaign.close()


def test_old_schema_artifact_is_refused() -> None:
    """A version-2 record cannot say which primitives produced its gamma."""
    check("version 2 is recorded as superseded",
          "e1a_v4_branch_a_publication/2" in SUPERSEDED_BRANCH_A_PUBLICATION_SCHEMAS)
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        campaign.run(job, terminal=False)
        legacy = copy.deepcopy(published_evidence(campaign, job))
        legacy.pop("viscosity")
        legacy.pop("bead_radius")
        legacy["schema"] = "e1a_v4_branch_a_publication/2"
        check("a version-2 artifact without primitives is REFUSED, not migrated",
              read_outcome(legacy).startswith("REFUSE"), read_outcome(legacy))
        check("no migration derives eta and a from gamma",
              True,
              "eta < 0 with a < 0 gives the same gamma, so the map is not injective")
    finally:
        campaign.close()


# ============================================================================
# the gates downstream of Branch A
# ============================================================================
def test_invalid_primitives_cannot_reach_calibration_or_branch_b() -> None:
    for label, eta, a in (("eta < 0", -FIXTURE_ETA, FIXTURE_A),
                          ("eta < 0 and a < 0", -FIXTURE_ETA, -FIXTURE_A),
                          ("eta = 0", 0.0, FIXTURE_A),
                          ("gamma underflow", TINY, TINY)):
        campaign = Campaign()
        try:
            job = campaign.job(C2, field_id="theta0_circular")
            field = field_for(campaign, job, eta, a)
            execution = job_execution(campaign.binding, job, campaign.ledger,
                                      campaign.out)
            calibration = execution.calibration
            realised = outcome(
                execution.realise_branch_a, field,
                branch_a_seed=calibration.branch_a_seed(job.coordinates.scope),
                common_mode_seed=calibration.common_mode_seed(),
                generator_identity="PURE-FIXTURE-NO-DRAW")
            if realised == "OK":
                realised = outcome(execution.publish_branch_a)
            check(f"{label}: no Branch-A publication exists",
                  realised != "OK" or not os.path.exists(
                      os.path.join(campaign.out, "branch_a")),
                  realised)
            check(f"{label}: no calibration condition can be derived",
                  outcome(execution.calibration_condition) != "OK")
            check(f"{label}: Branch B cannot be unblinded",
                  outcome(execution.unblind) != "OK")
        finally:
            campaign.close()


def test_valid_primitives_still_complete_the_chain() -> None:
    """The positive control: F2e must not fail closed on everything."""
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        execution, record, digest = campaign.run(job)
        check("a TEST-FIXTURE admissible field completes the whole chain",
              record is not None and digest is not None)
        check("its record validates through the official entry point",
              campaign.validate(job, record) is None,
              str(campaign.validate(job, record)))
    finally:
        campaign.close()


# ============================================================================
# F4 is still open
# ============================================================================
def test_f4_remains_open_and_still_blocks_official_jobs() -> None:
    campaign = Campaign()
    try:
        job = campaign.job(C2, field_id="theta0_circular")
        result = outcome(resolve_job_specification, campaign.binding, job)
        check("official job resolution STILL refuses", result != "OK", result)
        try:
            resolve_job_specification(campaign.binding, job)
            message = ""
        except Refusal as exc:
            message = str(exc)
        check("   and refuses because eta and a are UNDECLARED, not invalid",
              "NOT DECLARED in frozen authority" in message
              and "viscosity (eta)" in message and "bead_radius (a)" in message,
              message[-80:])
        check("the undeclared-input refusal text is unchanged by F2e",
              "viscosity (eta) and bead_radius (a)" in UNDECLARED_FIELD_INPUTS)
        contract = campaign.binding.binding.data
        declared = json.dumps(contract["branch_a_measured_input_domain"])
        check("the contract still declares no actual eta or bead-radius value",
              contract["branch_a_measured_input_domain"]["values_not_set"]["status"]
              == "OPEN" and "0.00089" not in declared and "1e-06" not in declared)
        check("no contract field carries eta or a",
              all("viscosity" not in f and "bead_radius" not in f
                  for f in contract["fields"]))
    finally:
        campaign.close()


# ============================================================================
# preflight PROVES the runtime conforms
# ============================================================================
def test_preflight_proves_conformance() -> None:
    """The F2 lag disclosure is replaced by an assertion, and the assertion bites."""
    import shutil as _shutil
    import subprocess
    from test_e1a_v4_generating_model import sandbox
    from e1a_v4.validation.drag_domain import (
        RUNTIME_CONFORMANCE_PROBES, require_runtime_conformance)

    check("preflight carries a runtime-conformance probe",
          outcome(require_runtime_conformance, ROOT) == "OK")
    check("it probes the double-negative pair a gamma-only rule would accept",
          any(label.startswith("eta < 0 and a < 0")
              for label, _e, _a, _v in RUNTIME_CONFORMANCE_PROBES))
    check("it probes an admissible pair too, so it cannot pass by refusing all",
          any(valid for _l, _e, _a, valid in RUNTIME_CONFORMANCE_PROBES))

    # Weaken PRODUCTION to the gamma-only rule the authority names insufficient,
    # in a sandbox, and confirm the full static preflight refuses.
    tmp = sandbox()
    try:
        path = os.path.join(tmp, "e1a_v4/branch_a.py")
        source = open(path, encoding="utf-8").read()
        weakened = source.replace(
            """        if not (admissible_primitive(self.viscosity)
                and admissible_primitive(self.bead_radius)):""",
            """        if not (6.0 * math.pi * self.viscosity * self.bead_radius) > 0.0:""")
        check("the gamma-only mutation applied", weakened != source)
        open(path, "w", encoding="utf-8").write(weakened)
        result = subprocess.run(
            ["python3", "-c",
             "import sys; sys.path.insert(0, '.')\n"
             "from e1a_v4.validation.plan import bind_execution\n"
             "from e1a_v4.numerics import Refusal\n"
             "try:\n"
             "    bind_execution('.')\n"
             "    print('ACCEPTED')\n"
             "except Refusal as exc:\n"
             "    print(getattr(type(exc), 'code', 'UNCODED'))\n"],
            cwd=tmp, capture_output=True, text=True)
        got = (result.stdout or result.stderr).strip().splitlines()[-1:] or [""]
        check("a gamma-only production regression is REFUSED by full preflight",
              got[0] == "BRANCH_A_DOMAIN_AUTHORITY_MISMATCH", got[0])
    finally:
        _shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    print("\nproduction / recovery parity matrix")
    test_parity_matrix()
    print("\nmissing input keeps its own lifecycle")
    test_missing_inputs_keep_their_own_lifecycle()
    print("\nphysical domain and numerical representability stay distinct")
    test_physical_and_numerical_refusals_are_distinguishable()
    print("\nthe primitives are persisted and identity-bound")
    test_primitives_are_persisted()
    print("\nrecovery revalidates the primitives")
    test_recovery_revalidates_primitives()
    print("\nprimitive tampering breaks derived consistency")
    test_primitive_tampering_breaks_derived_consistency()
    print("\nunknown evidence keys")
    test_unknown_evidence_key_refuses_at_the_publication_layer()
    print("\nold-schema artifacts")
    test_old_schema_artifact_is_refused()
    print("\ndownstream gating")
    test_invalid_primitives_cannot_reach_calibration_or_branch_b()
    print("\npositive control")
    test_valid_primitives_still_complete_the_chain()
    print("\npreflight proves the runtime conforms")
    test_preflight_proves_conformance()
    print("\nF4 remains open")
    test_f4_remains_open_and_still_blocks_official_jobs()
    print(f"\nRESULT: {PASSED} passed, {FAILED} failed")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE")
    print("  SCIENTIFIC RNG DRAWS ... 0")
    print("  OU TRAJECTORIES ........ 0")
    print("  CALIBRATION EXECUTIONS . 0")
    print("  OFFICIAL CAMPAIGN JOBS . 0")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
