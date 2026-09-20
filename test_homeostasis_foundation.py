"""Homeostasis foundation conformance gate.

Covers mission sections 18.1 (policy conformance), 18.2 (capacity
independence) and 18.3 (homeostasis region), plus the structural guards that
keep the registered Stage-A/Stage-B evidence replayable.

**Execution class: NON-MODEL-ADVANCING STATIC/PURE.** Every check is a pure
function evaluation on a synthetic or frozen individual state, an exact
rational identity, an enumeration of a finite fixed lattice, or an AST/source
inspection. This suite constructs no run, advances no tick and generates no
trajectory; `test_no_transition_is_called` asserts that by AST over this file.

All region and occupancy arithmetic is exact rational with tolerance zero. The
only floats appearing anywhere are in checks that a certified rational bracket
*contains* a reference decimal, where the float is the thing under test.

**No science is adopted here.** No world, horizon, seed, load, occupancy
threshold or success criterion is registered by this file, and no check asserts
that any policy keeps the system anywhere.
"""

from __future__ import annotations

import ast
import inspect
import math
from fractions import Fraction

from gaussian_harness.actions import ActionGroup, AtomicAction
from gaussian_harness.capacity import CapacityLedger, SignedShadowLedger
from gaussian_harness.harness import code_identity as gaussian_code_identity
from gaussian_harness.numerics import Refusal
from gaussian_harness.potential import LocalGaussianPotential
from gaussian_harness.rng import STREAM_ACTOR, Counter
from gaussian_harness.valuation import value_group

from homeostasis import jobs, metrics, policies, region
from homeostasis.jobs import ExecutionEnvelope, JobIdentity, JobResult, manifest
from homeostasis.metrics import (
    exact_median,
    excursions,
    exit_count,
    occupancy,
    summarize,
)
from homeostasis.policies import (
    CORE_POLICIES,
    POLICIES,
    POLICY_CONTROL_RANDOM,
    POLICY_EBU_ALIGNED,
    POLICY_EBU_HOSTILE,
    POLICY_EBU_RANDOM,
    SELECTION_ARGMAX,
    SELECTION_ARGMIN,
    SELECTION_UNIFORM,
    choose,
)
from homeostasis.region import (
    ConservationLaw,
    ReferenceRegion,
    effective_dimension,
    radial_square,
    threshold_enclosure,
)

# The identity the registered Stage-A and Stage-B artifacts were produced under.
# It is frozen in `stage_b_registry.REGISTERED_CODE_IDENTITY` and reproduced
# here so this suite fails the moment the pinned package is edited.
REGISTERED_GAUSSIAN_CODE_IDENTITY = (
    "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55"
)

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS  {label}")
    else:
        FAILED += 1
        print(f"  FAIL  {label}{(' -- ' + detail) if detail else ''}")


def _potential() -> LocalGaussianPotential:
    return LocalGaussianPotential.declare([10, 10, 10], [1, 1, 1])


def _region() -> ReferenceRegion:
    potential = _potential()
    return ReferenceRegion.derive(potential, [ConservationLaw.total_mass(3, 30)])


def _state(*values) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def _counter(seed: int = 4242, tick: int = 0) -> Counter:
    return Counter("static", "cfg", seed, STREAM_ACTOR, tick, 1, 0)


# --------------------------------------------------------------------------
# Section 18.3 -- the homeostatic region
# --------------------------------------------------------------------------


def test_effective_dimension_is_derived() -> None:
    potential = _potential()
    law = ConservationLaw.total_mass(3, 30)
    check("d = 2 is derived from the manifold", effective_dimension(potential, [law]) == 2)
    check(
        "an unconstrained world keeps its full dimension",
        effective_dimension(potential, []) == 3,
    )
    wide = LocalGaussianPotential.declare([5, 5, 5, 5], [1, 1, 1, 1])
    check(
        "a four-cell world with one law has d = 3",
        effective_dimension(wide, [ConservationLaw.total_mass(4, 20)]) == 3,
    )
    check(
        "unequal scales do not change d",
        effective_dimension(
            LocalGaussianPotential.declare([10, 10, 10], [1, 2, 3]),
            [ConservationLaw.total_mass(3, 30)],
        )
        == 2,
    )
    try:
        effective_dimension(potential, [ConservationLaw.total_mass(3, 31)])
        check("an off-constraint reference is refused", False, "no refusal raised")
    except Refusal as error:
        check(
            "an off-constraint reference is refused",
            "REFERENCE_OFF_CONSTRAINT" in str(error),
            str(error),
        )
    try:
        ReferenceRegion.derive(wide, [ConservationLaw.total_mass(4, 20)])
        check("a derived dimension other than two is refused", False, "no refusal")
    except Refusal as error:
        check(
            "a derived dimension other than two is refused",
            "UNSUPPORTED_EFFECTIVE_DIMENSION" in str(error),
            str(error),
        )


def test_quantile_enclosures_are_certified() -> None:
    low95, high95 = threshold_enclosure("H95")
    low99, high99 = threshold_enclosure("H99")
    check("H95 bracket is ordered", low95 < high95)
    check("H99 bracket is ordered", low99 < high99)
    check("H95 lies strictly inside H99", high95 < low99)
    # The bracket must contain the value the closed form gives. -2 ln(1-p) is
    # computed here in floating point precisely because the float is the thing
    # being tested against the certified rational bracket.
    for level, bounds in (("H95", (low95, high95)), ("H99", (low99, high99))):
        target = -2.0 * math.log(1.0 - (0.95 if level == "H95" else 0.99))
        check(
            f"{level} bracket contains -2 ln(1-p) = {target:.9f}",
            float(bounds[0]) - 1e-9 <= target <= float(bounds[1]) + 1e-9,
        )
    check("H95 bracket is narrower than 1e-40", high95 - low95 < Fraction(1, 10**40))
    check("H99 bracket is narrower than 1e-40", high99 - low99 < Fraction(1, 10**40))
    try:
        region.chi2_two_quantile_enclosure(90, 100)
        check("an underived level is refused", False, "no refusal raised")
    except Refusal as error:
        check("an underived level is refused", "QUANTILE_NOT_DERIVED" in str(error))


def test_radial_statistic_and_membership() -> None:
    reference_region = _region()
    potential = _potential()
    for state in (_state(10, 10, 10), _state(11, 9, 10), _state(12, 9, 9), _state(30, 0, 0)):
        check(
            f"R^2 = 2V at {tuple(int(v) for v in state)}",
            reference_region.radial_square(state) == 2 * potential.value_total(state),
        )
    check("the reference is in H95", reference_region.contains(_state(10, 10, 10), "H95"))
    check("one unit transfer stays in H95", reference_region.contains(_state(11, 9, 10), "H95"))
    check(
        "two units out of one cell leaves H95",
        not reference_region.contains(_state(12, 9, 9), "H95"),
    )
    check("that state is still in H99", reference_region.contains(_state(12, 9, 9), "H99"))
    check(
        "a simplex vertex is outside H99",
        not reference_region.contains(_state(30, 0, 0), "H99"),
    )
    try:
        reference_region.contains_radial_square(threshold_enclosure("H95")[0], "H95")
        check("an undecidable comparison refuses", False, "no refusal raised")
    except Refusal as error:
        check(
            "an undecidable comparison refuses",
            "THRESHOLD_ENCLOSURE_TOO_COARSE" in str(error),
        )


def test_lattice_collapse_and_coverage() -> None:
    reference_region = _region()
    values: set[int] = set()
    in95 = in99 = totalpoints = 0
    for first in range(0, 31):
        for second in range(0, 31 - first):
            state = _state(first, second, 30 - first - second)
            squared = reference_region.radial_square(state)
            values.add(int(squared))
            totalpoints += 1
            if reference_region.contains_radial_square(squared, "H95"):
                in95 += 1
            if reference_region.contains_radial_square(squared, "H99"):
                in99 += 1
    check("every lattice R^2 is an even integer", all(value % 2 == 0 for value in values))
    check("R^2 = 4 is unattainable", 4 not in values)
    check("max R^2 is 600, so V_max is 300", max(values) == 600)
    check("H95 attainable shells are {0, 2}", sorted(v for v in values if v <= 5) == [0, 2])
    check(
        "H99 attainable shells are {0, 2, 6, 8}",
        sorted(v for v in values if v <= 9) == [0, 2, 6, 8],
    )
    check("H95 holds 7 of 496 lattice states", (in95, totalpoints) == (7, 496), f"{in95}/{totalpoints}")
    check("H99 holds 19 of 496 lattice states", in99 == 19, str(in99))


def test_boundary_truncation_is_immaterial() -> None:
    reference_region = _region()
    boundary = reference_region.boundary_radial_square()
    check("the inscribed boundary is at R^2 = 150", boundary == 150)
    check(
        "the boundary is far outside H99",
        boundary > 16 * threshold_enclosure("H99")[1],
    )
    excluded = 3 * math.exp(-float(boundary) / 2) / (2 * math.sqrt(float(boundary)))
    check(f"excluded reference mass < 1e-33 ({excluded:.2e})", excluded < 1e-33)
    skewed = LocalGaussianPotential.declare([10, 10, 10], [1, 1, 2])
    skewed_region = ReferenceRegion.derive(skewed, [ConservationLaw.total_mass(3, 30)])
    check(
        "an anisotropic world recomputes its own boundary",
        skewed_region.boundary_radial_square() != boundary,
    )


# --------------------------------------------------------------------------
# Section 18.1 -- policy conformance on hand-checkable menus
# --------------------------------------------------------------------------


def test_hostile_and_aligned_pick_exact_extrema() -> None:
    menu = (Fraction(-7), Fraction(-2), Fraction(3), Fraction(-4))
    hostile = choose(POLICY_EBU_HOSTILE, menu, _counter())
    aligned = choose(POLICY_EBU_ALIGNED, menu, _counter())
    check("hostile takes the exact minimum -7", menu[hostile.index] == Fraction(-7))
    check("aligned takes the exact maximum 3", menu[aligned.index] == Fraction(3))
    check("hostile records its rule", hostile.rule == SELECTION_ARGMIN)
    check("aligned records its rule", aligned.rule == SELECTION_ARGMAX)
    # The mission's worked example: every candidate negative, the actor still acts.
    negative = (Fraction(-2), Fraction(-4), Fraction(-7))
    forced = choose(POLICY_EBU_ALIGNED, negative, _counter())
    check(
        "aligned still acts when every candidate is negative, taking -2",
        negative[forced.index] == Fraction(-2),
    )
    check("no zero-valued no-op was introduced", Fraction(0) not in negative)
    exact_ties = (Fraction(5), Fraction(5), Fraction(1))
    tied = choose(POLICY_EBU_ALIGNED, exact_ties, _counter())
    check("aligned reports the exact tie size", tied.tie_size == 2)
    check("aligned resolves the tie inside the tied set", tied.index in (0, 1))
    check(
        "tie-breaking is deterministic under the same counter",
        choose(POLICY_EBU_ALIGNED, exact_ties, _counter()).index == tied.index,
    )
    varied = {
        choose(POLICY_EBU_ALIGNED, exact_ties, _counter(seed=seed)).index
        for seed in range(1, 60)
    }
    check("tie-breaking uses the actor RNG, not a fixed position", varied == {0, 1}, str(varied))


def test_random_policies_only_choose_admissible() -> None:
    menu = tuple(Fraction(value) for value in (-9, 4, 0, 7, -1))
    for policy in (POLICY_EBU_RANDOM, POLICY_CONTROL_RANDOM):
        seen = set()
        for seed in range(1, 200):
            decision = choose(policy, menu, _counter(seed=seed))
            seen.add(decision.index)
            if not 0 <= decision.index < len(menu):
                break
        check(f"{policy} stays inside the admissible set", seen <= set(range(len(menu))))
        check(f"{policy} can reach every admissible index", seen == set(range(len(menu))), str(sorted(seen)))
        check(f"{policy} records the uniform rule", decision.rule == SELECTION_UNIFORM)
    # The two uniform policies differ only by the affordability filter upstream:
    # given the same admissible count and counter they select identically.
    same = all(
        choose(POLICY_EBU_RANDOM, menu, _counter(seed=seed)).index
        == choose(POLICY_CONTROL_RANDOM, menu, _counter(seed=seed)).index
        for seed in range(1, 50)
    )
    check("both uniform policies share one selection rule", same)


def test_uniform_selection_is_structurally_ebu_blind() -> None:
    source = inspect.getsource(policies._uniform_over_count)
    tree = ast.parse(source).body[0]
    names = tuple(argument.arg for argument in tree.args.args)
    check("the uniform selector takes only (count, counter)", names == ("count", "counter"), str(names))
    check(
        "its count parameter is annotated as an integer",
        ast.unparse(tree.args.args[0].annotation) == "int",
    )
    forbidden = {"group_ebu", "receipts", "balances", "owner_deltas", "value_group",
                 "potential", "marginal", "radial_square", "ledger"}
    used = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    used |= {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    leaked = used & forbidden
    check("no value, potential or balance is in its scope", not leaked, str(leaked))


def test_no_policy_may_decline_to_act() -> None:
    check("exactly four core policies are declared", len(CORE_POLICIES) == 4)
    table = {row["policy_id"]: row for row in policies.policy_table()}
    check(
        "no policy may decline to act",
        all(row["may_decline_to_act"] is False for row in table.values()),
    )
    check(
        "three policies apply affordability and one does not",
        sum(1 for row in table.values() if row["applies_affordability"]) == 3,
    )
    check(
        "exactly two policies read EBU to choose",
        sum(1 for row in table.values() if row["reads_ebu_to_choose"]) == 2,
    )
    banned = {"abstain", "no_op", "noop", "wait", "do_nothing", "rest", "skip_action",
              "voluntary", "decline"}
    tree = ast.parse(inspect.getsource(policies))
    identifiers = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    identifiers |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    identifiers |= {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    check("no abstention identifier exists in the policy module", not (identifiers & banned),
          str(identifiers & banned))
    for policy in CORE_POLICIES:
        try:
            choose(policy, (), _counter())
            check(f"{policy} refuses an empty admissible set", False, "no refusal raised")
        except Refusal:
            check(f"{policy} refuses an empty admissible set", True)


# --------------------------------------------------------------------------
# Section 18.2 / 9 -- capacity must not change EBU measurement
# --------------------------------------------------------------------------


def test_capacity_does_not_change_valuation() -> None:
    potential = _potential()
    state = _state(12, 9, 9)
    group = ActionGroup.of(
        AtomicAction.declare(0, 1, 1), AtomicAction.declare(0, 2, 1)
    )
    signature = inspect.signature(value_group)
    check(
        "value_group has no ledger, balance or capacity parameter",
        not ({"ledger", "balance", "balances", "capacity"} & set(signature.parameters)),
        str(tuple(signature.parameters)),
    )
    baseline = value_group(potential, state, group)
    ledgers = (
        CapacityLedger.zero(3),
        CapacityLedger((Fraction(0), Fraction(5), Fraction(1, 2))),
        CapacityLedger((Fraction(1000), Fraction(1000), Fraction(1000))),
        SignedShadowLedger((Fraction(-40), Fraction(3), Fraction(0))),
    )
    values = set()
    receipt_sets = set()
    affordabilities = set()
    projections = set()
    for ledger in ledgers:
        valuation = value_group(potential, state, group)
        values.add(valuation.group_ebu)
        receipt_sets.add(tuple((a.action_id, r) for a, r in valuation.receipts))
        decision = ledger.project(valuation.owner_deltas)
        affordabilities.add(decision.affordable)
        projections.add(decision.projected)
    check("E_G is identical under every capacity vector", len(values) == 1, str(values))
    check("per-action receipts are identical too", len(receipt_sets) == 1)
    check(
        "V_pre and V_post do not depend on capacity",
        len({potential.value_total(state) for _ in ledgers}) == 1,
    )
    check("affordability status does differ across capacities", len(affordabilities) > 1)
    check("projected balances do differ across capacities", len(projections) > 1)


# --------------------------------------------------------------------------
# Section 5 -- the metric battery on hand-checkable sequences
# --------------------------------------------------------------------------


def test_metrics_on_hand_checkable_sequences() -> None:
    #            t: 0   1   2   3   4   5   6   7
    inside = [True, True, False, False, True, False, True, True]
    radii = [Fraction(v) for v in (0, 2, 6, 14, 2, 8, 0, 2)]
    check("occupancy is exact", occupancy(inside) == Fraction(5, 8))
    check("exits are inside-to-outside transitions", exit_count(inside) == 2)
    runs = excursions(inside, radii)
    check("two excursions are found", len(runs) == 2)
    check("the first runs t=2..3 with peak 14", (runs[0].start, runs[0].length, runs[0].peak_radial_square) == (2, 2, Fraction(14)))
    check("the second runs t=5 with peak 8", (runs[1].start, runs[1].length, runs[1].peak_radial_square) == (5, 1, Fraction(8)))
    check("both excursions returned", all(run.returned for run in runs))
    tail_inside = [True, False, False]
    tail = excursions(tail_inside, [Fraction(0), Fraction(2), Fraction(6)])
    check("an unfinished excursion is flagged censored", tail[0].returned is False)
    check("a leading excursion is not counted as an exit", exit_count([False, False, True]) == 0)
    check("exact median of an even sample", exact_median([Fraction(1), Fraction(4)]) == Fraction(5, 2))
    summary = summarize(radii, inside, [True] * 8, block=4, blocks=2)
    check("summary occupancy matches", summary.occupancy_95 == Fraction(5, 8))
    check("summary counts time outside", summary.time_outside_95 == 3)
    check("peak severity is the largest excursion peak", summary.excursion_severity_max == Fraction(14))
    check("return-time median excludes censored runs", summary.return_time_median == Fraction(3, 2))
    check("max R is sqrt of max R^2", abs(summary.radius_max - math.sqrt(14)) < 1e-12)
    check("median R is sqrt of the exact median R^2", summary.max_radial_square_exact == Fraction(14))
    check("blocks are summarized", len(summary.blocks) == 2)
    check(
        "drift compares last block with first",
        summary.drift.occupancy_change == summary.blocks[-1].occupancy_95 - summary.blocks[0].occupancy_95,
    )


def test_metrics_read_no_account_quantity() -> None:
    """Homeostasis is a physical-state property (mission section 4)."""
    banned = {"balance", "balances", "ledger", "capacity", "audit", "audit_ledger",
              "receipt", "receipts", "settle", "owner_deltas", "affordable", "sumB"}
    for module in (metrics, region):
        tree = ast.parse(inspect.getsource(module))
        identifiers = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        identifiers |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        identifiers |= {
            argument.arg
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            for argument in node.args.args
        }
        leaked = identifiers & banned
        check(f"{module.__name__} reads no account quantity", not leaked, str(leaked))


# --------------------------------------------------------------------------
# Sections 21 and 22 -- deterministic job identity (pure parts)
# --------------------------------------------------------------------------


def _identity(**overrides) -> JobIdentity:
    fields = dict(
        preregistration_id="prereg-static",
        configuration_identity="cfgid-static",
        code_identity="codeid-static",
        load_id="p_force_1_2",
        policy_id=POLICY_EBU_RANDOM,
        menu_rule="with_net_zero_groups",
        replicate=3,
        horizon=64,
        forcing_seed=11,
        actor_seed=22,
    )
    fields.update(overrides)
    return JobIdentity(**fields)


def test_job_identity_covers_every_scientific_input() -> None:
    base = _identity()
    check("job_id is a sha256 hex digest", len(base.job_id) == 64)
    check("job_id is stable across constructions", base.job_id == _identity().job_id)
    varied = {
        "preregistration_id": "other", "configuration_identity": "other",
        "code_identity": "other", "load_id": "p_force_1_4",
        "policy_id": POLICY_EBU_ALIGNED, "menu_rule": "strict_physical_change",
        "replicate": 4, "horizon": 65, "forcing_seed": 12, "actor_seed": 23,
    }
    for field, value in varied.items():
        check(f"changing {field} changes the job id",
              _identity(**{field: value}).job_id != base.job_id)
    for bad, label in (
        ({"preregistration_id": "  "}, "an empty preregistration id"),
        ({"policy_id": "gradient_follower"}, "an undeclared policy"),
        ({"menu_rule": "whatever"}, "an undeclared menu rule"),
        ({"load_id": "p_force_2"}, "an undeclared load"),
        ({"replicate": -1}, "a negative replicate"),
        ({"horizon": 0}, "a zero horizon"),
        ({"preregistration_id": "a|b"}, "a separator injected into a field"),
    ):
        try:
            _identity(**bad)
            check(f"{label} is refused", False, "no refusal raised")
        except Refusal:
            check(f"{label} is refused", True)


def test_payload_hash_excludes_the_execution_envelope() -> None:
    payload = {"columns": {"V": ["0/1", "2/1"]}, "job_id": _identity().job_id}
    plain = JobResult(_identity(), payload)
    cloudy = JobResult(_identity(), dict(payload),
                       ExecutionEnvelope("aws-batch", 4, "2026-01-01T00:00:00Z", "ip-10-0-0-7"))
    check("a different executor does not change the payload hash",
          plain.payload_hash == cloudy.payload_hash)
    document = cloudy.envelope_document()
    check("the envelope is recorded beside the payload",
          document["execution_envelope"]["executor"] == "aws-batch")
    check("the envelope is not inside the payload",
          "execution_envelope" not in document["payload"])
    check("the recorded hash is the payload hash",
          document["payload_sha256"] == cloudy.payload_hash)
    check("the canonical payload is sorted and separator-free",
          plain.canonical_payload == plain.canonical_payload.replace(", ", ","))


def test_manifest_reports_conflicts_rather_than_merging() -> None:
    identity = _identity()
    good = JobResult(identity, {"columns": {"V": ["0/1"]}})
    retry = JobResult(identity, {"columns": {"V": ["0/1"]}},
                      ExecutionEnvelope("retry", 1))
    clean = manifest([good, retry])
    check("an idempotent retry is not a conflict", clean["integrity_passed"])
    check("but the duplicate is counted", clean["duplicate_identities"] == 1)
    check("and the expected job count stays one", clean["jobs_expected"] == 1)
    divergent = JobResult(identity, {"columns": {"V": ["2/1"]}})
    broken = manifest([good, divergent])
    check("a divergent payload for one identity fails integrity",
          not broken["integrity_passed"])
    check("and the conflicting job is named",
          broken["conflicting_payloads"] == [identity.job_id])


def test_jobs_cannot_reach_a_clock_or_a_host() -> None:
    """No worker may derive a scientific choice from time or placement."""
    tree = ast.parse(inspect.getsource(jobs))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    banned = {"time", "datetime", "os", "socket", "random", "uuid", "platform",
              "getpass", "secrets", "subprocess"}
    leaked = imported & banned
    check("the job module imports no clock, host or entropy source", not leaked, str(leaked))
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    names |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    forbidden = {"monotonic", "perf_counter", "getpid", "gethostname", "now", "utcnow"}
    check("and calls no clock or host primitive", not (names & forbidden),
          str(names & forbidden))


# --------------------------------------------------------------------------
# Section 25 -- the frozen analysis plan
# --------------------------------------------------------------------------


def test_analysis_reproduces_the_frozen_stage_b_definitions() -> None:
    """The new module must not quietly redefine the registered statistics."""
    import random
    import homeostasis_analysis as new
    import stage_b_analysis as frozen
    check("alpha is unchanged from Stage B", new.ALPHA == frozen.ALPHA)
    random.seed(20260920)
    agree_p = agree_ci = True
    for _ in range(300):
        count = random.randint(1, 40)
        sample = [
            Fraction(random.randint(-5, 5), random.randint(1, 4)) for _ in range(count)
        ]
        if new.exact_sign_test(sample)["p_value"] != frozen.exact_sign_test(sample)["p_value"]:
            agree_p = False
        left = new.sign_confidence_interval(sample)
        right = frozen.sign_confidence_interval(sample)
        if (left["lower"], left["upper"]) != (right["lower"], right["upper"]):
            agree_ci = False
    check("the sign test agrees on 300 random samples", agree_p)
    check("the median interval agrees on 300 random samples", agree_ci)


def test_analysis_plan_is_compact_and_exact() -> None:
    import homeostasis_analysis as analysis
    check("exactly three contrasts are registered", len(analysis.CONTRASTS) == 3)
    check("nine tests in total across three loads", 3 * len(analysis.CONTRASTS) == 9)
    check("delta_meaningful is registered", analysis.DELTA_MEANINGFUL == Fraction(5, 100))
    # An all-positive paired difference on 8 replicates is the exact extreme.
    positive = [Fraction(1, 10)] * 8
    result = analysis.exact_sign_test(positive)
    check("the exact two-sided p-value for 8/8 is 2/256",
          result["p_value"] == Fraction(2, 256), str(result["p_value"]))
    check("ties are excluded from the trial count",
          analysis.exact_sign_test([Fraction(0)] * 4 + positive)["trials"] == 8)
    check("an all-tied sample returns p = 1",
          analysis.exact_sign_test([Fraction(0)] * 6)["p_value"] == Fraction(1))
    decisions = analysis.holm({
        "a": Fraction(1, 1000), "b": Fraction(3, 100), "c": Fraction(4, 10)})
    check("Holm rejects only below alpha/(m-i)", decisions == {"a": True, "b": False, "c": False},
          str(decisions))
    check("Holm is step-down: a later failure stops the chain",
          analysis.holm({"a": Fraction(4, 10), "b": Fraction(1, 1000)})["b"] is True)
    interval = analysis.sign_confidence_interval([Fraction(n) for n in range(1, 21)])
    check("the median interval is a pair of order statistics",
          interval["lower"] in [Fraction(n) for n in range(1, 21)]
          and interval["upper"] in [Fraction(n) for n in range(1, 21)])
    check("and it is ordered", interval["lower"] <= interval["upper"])


def test_result_categories_are_registered_not_pass_fail() -> None:
    import homeostasis_analysis as analysis
    check("occupancy 0.6 is localized", analysis.band(Fraction(6, 10)) == "localized")
    check("occupancy 0.3 is partially localized",
          analysis.band(Fraction(3, 10)) == "partially_localized")
    check("occupancy 0.03 is not localized", analysis.band(Fraction(3, 100)) == "not_localized")
    check("occupancy 0.10 is neither extreme", analysis.band(Fraction(1, 10)) == "weakly_localized")
    check("no pass threshold at 0.95 exists",
          not hasattr(analysis, "PASS_THRESHOLD") and analysis.BAND_LOCALIZED != Fraction(95, 100))
    falling = [Fraction(5, 10), Fraction(4, 10), Fraction(3, 10)]
    rising = [Fraction(10), Fraction(20), Fraction(30)]
    check("falling occupancy with rising radius is divergence",
          analysis.divergence_flag(falling, rising))
    check("falling occupancy alone is not divergence",
          not analysis.divergence_flag(falling, [Fraction(30), Fraction(20), Fraction(10)]))
    check("rising radius alone is not divergence",
          not analysis.divergence_flag([Fraction(1, 10)] * 3, rising))


# --------------------------------------------------------------------------
# Structural guards
# --------------------------------------------------------------------------


def test_registered_package_is_untouched() -> None:
    actual = gaussian_code_identity()
    check(
        "gaussian_harness still has its registered code identity",
        actual == REGISTERED_GAUSSIAN_CODE_IDENTITY,
        f"found {actual}",
    )


def test_no_transition_is_called() -> None:
    """This file must not advance model state, and says so by inspection."""
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
            called.add(name)
    banned = {"run_tick", "run_trajectory", "recovery_trial", "run_stage_a", "advance",
              "PolicyRun", "Run"}
    leaked = called & banned
    check("no transition entry point is called in this suite", not leaked, str(leaked))


def test_no_science_is_adopted_here() -> None:
    check("no occupancy pass threshold is defined here", not hasattr(metrics, "PASS_THRESHOLD"))
    check("no hypothesis is registered here", not hasattr(metrics, "HYPOTHESES"))
    check("no world, horizon or seed is frozen here", not hasattr(region, "REGISTERED_SEEDS"))


def main() -> int:
    groups = (
        ("effective dimension is derived", test_effective_dimension_is_derived),
        ("quantile enclosures are certified", test_quantile_enclosures_are_certified),
        ("radial statistic and membership", test_radial_statistic_and_membership),
        ("lattice collapse and coverage", test_lattice_collapse_and_coverage),
        ("boundary truncation is immaterial", test_boundary_truncation_is_immaterial),
        ("hostile and aligned pick exact extrema", test_hostile_and_aligned_pick_exact_extrema),
        ("random policies only choose admissible", test_random_policies_only_choose_admissible),
        ("uniform selection is structurally EBU-blind", test_uniform_selection_is_structurally_ebu_blind),
        ("no policy may decline to act", test_no_policy_may_decline_to_act),
        ("capacity does not change valuation", test_capacity_does_not_change_valuation),
        ("metrics on hand-checkable sequences", test_metrics_on_hand_checkable_sequences),
        ("metrics read no account quantity", test_metrics_read_no_account_quantity),
        ("job identity covers every scientific input",
         test_job_identity_covers_every_scientific_input),
        ("payload hash excludes the execution envelope",
         test_payload_hash_excludes_the_execution_envelope),
        ("manifest reports conflicts rather than merging",
         test_manifest_reports_conflicts_rather_than_merging),
        ("jobs cannot reach a clock or a host", test_jobs_cannot_reach_a_clock_or_a_host),
        ("analysis reproduces the frozen Stage-B definitions",
         test_analysis_reproduces_the_frozen_stage_b_definitions),
        ("analysis plan is compact and exact", test_analysis_plan_is_compact_and_exact),
        ("result categories are registered, not pass/fail",
         test_result_categories_are_registered_not_pass_fail),
        ("registered package is untouched", test_registered_package_is_untouched),
        ("no transition is called", test_no_transition_is_called),
        ("no science adopted here", test_no_science_is_adopted_here),
    )
    for label, test in groups:
        print(f"\n{label}")
        test()
    print(f"\nHomeostasis foundation gate: {PASSED} passed, {FAILED} failed, {len(groups)} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  numeric policy: exact rational, tolerance 0")
    print("  scientific trajectories generated: 0")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
