"""Prospective size-validation semantics and the final campaign classification.

WHY THE INHERITED 3% RULE WAS INSUFFICIENT
------------------------------------------
The earlier frozen plan validated the geometry gates with "one-sided 95% CP UPPER
bound <= 0.03". That is a COARSE GROSS-INFLATION TOLERANCE inherited from development
analysis, not validation of the nominal alpha allocations. At the declared nominal
levels it would have tolerated

    C2  up to  6/400  = 0.0150    ->   3x the nominal alpha_geom = 0.005
    C3  up to  6/400  = 0.0150    ->  15x the nominal alpha_2    = 0.001
    C4  up to 47/2000 = 0.0235    ->   6x the nominal alpha_1    = 0.004

A rule that passes fifteen times the nominal rate cannot be described as validating it.

WHAT REPLACES IT
----------------
Two DIFFERENT questions, never merged:

    QUESTION A  complete practical performance.  C1, unchanged: one-sided 95% CP LOWER
                bound on complete-pipeline success >= 0.90, R = 300, i.e. >= 279/300.

    QUESTION B  component size inflation.  C2, C3, C4 test prospectively

                    H0: p <= nominal alpha        H1: p > nominal alpha

                at one-sided 5%. Inflation is DETECTED iff the one-sided 95% CP LOWER
                bound on the rejection probability EXCEEDS the nominal alpha.

At the feasible replicate counts these are NOT positive proofs that the achieved rate
sits at or below a tiny nominal alpha. Passing means exactly:

    NO_SIGNIFICANT_SIZE_INFLATION_DETECTED

and never "nominal size proved". That distinction is asserted by a test.

CLASSIFICATION
    cp_lower / cp_upper, the derived boundaries ... EXACT (exact binomial, bisected)
    the campaign rule ............................. EXACT (the frozen conjunction)

NO RNG. Nothing here draws.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..numerics import Refusal
from ..status import NON_ESTIMATED, AnalysisStatus
from .dispositions import cp_lower, cp_upper

#: The two STATISTICAL verdicts a size diagnostic may produce.
SIZE_FAILURE = "STATISTICAL_SIZE_FAILURE"
SIZE_NO_INFLATION = "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED"
#: The THIRD primary state, from the G5 structured-refusal amendment. It is NOT a
#: statistical verdict: it says the preregistered evidence was not fully observed
#: because a valid structured refusal left a required primary endpoint undefined.
#: Only C3 and C4 can reach it -- C2's composite P1 endpoint fails closed, so its
#: elementary event is defined for every replicate.
SIZE_NOT_EVALUABLE = "NOT_EVALUABLE"
#: The campaign-level classification a NOT_EVALUABLE field contributes. Distinct
#: from SIZE_FAILURE on purpose: "the size test could not be validly evaluated as
#: preregistered" is not "the size test rejected".
INCOMPLETE_EVIDENCE_CLASSIFICATION = "VALIDATION_INCONCLUSIVE"


# ---------------------------------------- structured-refusal AUTHORISATION ---
# F1f-g. An independent runtime audit showed that "the primary endpoint is
# undefined" was being granted on evidence that did not establish it. The rule
# below is THE single source of truth for whether a terminal record may leave a
# C3/C4 block decision undefined. `campaign_driver.is_structured_refusal` -- which
# both the endpoint VALIDATOR and the per-field AGGREGATOR call -- delegates here,
# and preflight probes this function directly, so no layer carries its own copy.

#: Every analysis status the repository DECLARES, read from the canonical roster
#: in `e1a_v4.status` rather than retyped here. A record carrying a value outside
#: this set is MALFORMED, not refused-for-cause: the status is the thing that
#: authorises an undefined endpoint, so an unrecognised one authorises nothing.
DECLARED_ANALYSIS_STATUSES = frozenset(status.value for status in AnalysisStatus)
#: The status that means the frozen gate actually produced its rows.
ESTIMATED_STATUS = AnalysisStatus.ESTIMATED.value
#: The one DECLARED non-ESTIMATED status that `e1a_v4.endpoints.p1_geometry` does
#: NOT fail closed on. Its guard reads
#:     if not analysis.is_estimated and analysis.status not in (GEOMETRY_FAIL,)
#: so a GEOMETRY_FAIL analysis is carried PAST the fail-closed return and scored
#: against real gate statistics: it either yields DEFINED block decisions or
#: refuses outright, and `p1_block_decisions` documents that `(None, None)` arises
#: "exactly when the analysis was not ESTIMATED and P1 failed closed". It
#: therefore never authorises an undefined block decision. Treating every
#: non-ESTIMATED status alike would have let it.
NON_FAIL_CLOSED_STATUSES = frozenset({AnalysisStatus.GEOMETRY_FAIL.value})
#: The statuses that AUTHORISE an undefined per-field block decision: DERIVED from
#: the canonical `NON_ESTIMATED` frozenset, never enumerated by hand, less the
#: statuses the frozen gate does not fail closed on.
REFUSAL_AUTHORISING_STATUSES = frozenset(
    status.value for status in NON_ESTIMATED) - NON_FAIL_CLOSED_STATUSES
#: The composite P1 state such a record MUST express, read off the frozen record
#: assembly in `campaign_driver.evaluate_replicate`:
#:     P1          = bool(result.passed)
#:     p1_rejected = bool(not result.passed)
#: and `p1_geometry` returns `passed = False` for exactly the statuses above. A
#: record claiming an authorised refusal while reporting a PASSED composite P1 is
#: internally inconsistent, and no part of the frozen pipeline can produce it.
#: This is NOT a new P1 semantic; it is the existing one, now checked.
FAIL_CLOSED_P1_STATE = (("P1", False), ("p1_rejected", True))


def authorises_undefined_block_decision(outcome: Mapping[str, Any]) -> bool:
    """May THIS record leave a C3/C4 primary block decision undefined?

    Validity is never inferred from the ABSENCE of data. Two affirmative things
    must both be present and agree, and either one missing refuses:

        STATUS    `analysis_status` is present, is a string, and is one of the
                  DECLARED statuses that authorise an undefined block decision.
                  An unknown value -- a typo, a renamed status, a status from
                  another pipeline -- is malformed, not authorised.
        P1        the record's own composite P1 fields express the frozen
                  FAIL-CLOSED state. The statuses above are precisely the ones
                  `p1_geometry` fails closed on, so a record that claims one of
                  them while reporting a PASSED P1 contradicts itself, and the
                  contradiction must refuse rather than be resolved in favour of
                  the convenient half.

    THE DEFECTS THIS CLOSES (independent runtime audit, F1f-g)
        `analysis_status != "ESTIMATED"` accepted ANY string that was not that one
        literal, so `"NOT_A_REAL_STATUS"` authorised a refusal. And nothing looked
        at P1 at all, so `RANK_GUARD_FAIL` with `P1=True, p1_rejected=False` --
        a record asserting both that the analysis never ran and that the gate
        passed -- was accepted as valid refusal evidence.

    `is` comparison, not `==`: a `1` or a `0` arriving from a loosely typed
    producer is not the frozen boolean state, and `1 == True` would have hidden
    that.
    """
    status = outcome.get("analysis_status")
    if not isinstance(status, str) or status not in REFUSAL_AUTHORISING_STATUSES:
        return False
    return all(outcome.get(name) is expected for name, expected in FAIL_CLOSED_P1_STATE)


#: Machine-readable statement of what a pass does and does not mean.
SIZE_INTERPRETATION = {
    "verdict_on_pass": SIZE_NO_INFLATION,
    "means": "this experiment did not establish excess size at the chosen confidence level",
    "does_not_mean": "that the achieved rate is mathematically proved to be at or below the nominal alpha",
    "forbidden_wording": ["NOMINAL SIZE PROVED", "nominal size proved", "size proved",
                          "exact size established"],
    "test": "H0: p <= nominal alpha  vs  H1: p > nominal alpha, one-sided 5%",
    "detector": "inflation detected iff CP_lower(rejections, R) > nominal alpha",
}

#: The contract's coarse rule. It is SUPERSEDED as the release classifier by the
#: stricter nominal-inflation test, which implies it over the whole accepting
#: range -- but `synthetic_validation_requirements[2]` still REQUIRES it, so it is
#: mandatory to report. "may be reported" was the wrong word and is now corrected.
GROSS_INFLATION_TOLERANCE = 0.03
GROSS_INFLATION_LABEL = ("MANDATORY CONTRACT DIAGNOSTIC [synthetic_validation_"
                         "requirements[2]], inherited from development analysis; NOT "
                         "validation of the nominal alpha and NOT the release gate")


#: MEMOISED, not changed. `size_boundary` is a pure function of (n, nominal) and
#: `classify_size` calls it on every per-field assessment, so scoring three cases
#: PER FIELD evaluates the same three boundaries twelve times per classification
#: and many times again inside preflight. The cache returns the identical derived
#: integer; it exists so that counting four fields instead of one does not make
#: the frozen boundary derivation quadratically expensive. Three entries is the
#: whole working set.
@functools.lru_cache(maxsize=None)
def size_boundary(n: int, nominal: float) -> int:
    """Largest rejection count whose one-sided 95% CP LOWER bound stays <= nominal.

    DERIVED, never copied. The frozen plan records 5 (C2), 2 (C3) and 13 (C4); the
    test suite recomputes each of them here.
    """
    if n < 1 or not 0.0 < nominal < 1.0:
        raise Refusal("size_boundary needs n >= 1 and 0 < nominal < 1")
    k = 0
    while k <= n and cp_lower(k, n) <= nominal:
        k += 1
    return k - 1


def size_inflation_detected(rejections: int, n: int, nominal: float) -> bool:
    """True iff the one-sided 95% CP LOWER bound EXCEEDS the nominal alpha."""
    if not 0 <= rejections <= n:
        raise Refusal(f"rejections must lie in [0, {n}]")
    return cp_lower(rejections, n) > nominal


def classify_size(rejections: int, n: int, nominal: float) -> dict:
    """One size diagnostic. Returns the verdict plus both bounds, primary and secondary."""
    detected = size_inflation_detected(rejections, n, nominal)
    lower = cp_lower(rejections, n)
    upper = cp_upper(rejections, n)
    return {
        "rejections": rejections, "replicates": n, "nominal_alpha": nominal,
        "observed_rate": rejections / n,
        "cp_lower": lower, "cp_upper": upper,
        "boundary": size_boundary(n, nominal),
        "verdict": SIZE_FAILURE if detected else SIZE_NO_INFLATION,
        "primary_rule": "inflation detected iff CP_lower > nominal alpha",
        "secondary_gross_diagnostic": {
            "label": GROSS_INFLATION_LABEL,
            "tolerance": GROSS_INFLATION_TOLERANCE,
            "within_tolerance": upper <= GROSS_INFLATION_TOLERANCE,
        },
        "interpretation": SIZE_INTERPRETATION["means"] if not detected else
                          "excess size established at the chosen confidence level",
    }


def _strict_count(field_id: str, what: str, value: Any) -> int:
    """A count of replicates is a NON-NEGATIVE int. Nothing else is accepted.

    `bool` is excluded explicitly. Python makes `True` an `int` worth 1, so an
    unguarded `isinstance(value, int)` would accept `{reason: True}` as "one
    refusal" and `{reason: False}` as "zero", which is an accident of the type
    system rather than a recorded count. A float is refused for the same reason a
    fractional replicate is meaningless, not because it cannot be summed.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise Refusal(
            f"{field_id}: {what} = {value!r} is a {type(value).__name__}, not an "
            "integer count of replicates")
    if value < 0:
        raise Refusal(
            f"{field_id}: {what} = {value} is negative; a count of replicates "
            "cannot be less than zero")
    return value


@dataclass(frozen=True)
class FieldSizeOutcome:
    """One field's PRIMARY size evidence, in THREE states rather than two.

    WHY THIS IS NOT A COUNT
        A per-field rejection count cannot express the amendment. `rejections = 2`
        over a planned 400 is a different scientific object depending on whether
        the other 398 endpoint decisions exist. The three counts are therefore
        carried together and never collapsed:

            evaluable       replicates whose required primary endpoint EXISTS
            structured_refusals  replicates whose primary endpoint is UNDEFINED
                            because of a valid structured refusal
            rejections      TRUE decisions AMONG THE EVALUABLE ones only

        `planned_replicates` is the frozen prospective R and remains the primary
        denominator whatever the other two are: an undefined endpoint never
        shrinks the declared experiment to its survivors.
    """

    field_id: str
    planned_replicates: int
    evaluable: int
    structured_refusals: int
    rejections: int
    #: Structured-refusal reason -> how many replicates carried it. Kept so a
    #: reader can tell WHY a field was not evaluable, which frozen authority
    #: requires (`required_terminal_counts` names `refusal_reasons`).
    refusal_reasons: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _strict_count(self.field_id, "planned_replicates", self.planned_replicates)
        if self.planned_replicates < 1:
            raise Refusal(f"{self.field_id}: planned replicates must be >= 1")
        for name, value in (("evaluable", self.evaluable),
                            ("structured_refusals", self.structured_refusals),
                            ("rejections", self.rejections)):
            _strict_count(self.field_id, name, value)
            if not 0 <= value <= self.planned_replicates:
                raise Refusal(
                    f"{self.field_id}: {name} = {value} lies outside "
                    f"[0, {self.planned_replicates}]")
        if self.rejections > self.evaluable:
            raise Refusal(
                f"{self.field_id}: {self.rejections} rejections among "
                f"{self.evaluable} evaluable endpoints; a rejection is a DEFINED "
                "decision and cannot exceed the decisions that exist")
        if self.evaluable + self.structured_refusals != self.planned_replicates:
            raise Refusal(
                f"{self.field_id}: {self.evaluable} evaluable + "
                f"{self.structured_refusals} structured refusals != the planned "
                f"{self.planned_replicates}. Every planned replicate is accounted "
                "for exactly once; a silently discarded record is the defect this "
                "refuses.")
        # --- REFUSAL-REASON ACCOUNTING (F1f-g) ------------------------------
        # The previous guard was `if total and total != refusals`, which skipped
        # itself whenever the reasons summed to ZERO -- so one refusal with NO
        # reason attribution at all was accepted, and the terminal report frozen
        # authority requires could name a field NOT_EVALUABLE without saying why.
        # The arithmetic is now unconditional, and the counts are type-checked
        # before they are summed, because `{A: 2, B: -1}` also sums to one.
        if not isinstance(self.refusal_reasons, Mapping):
            raise Refusal(
                f"{self.field_id}: refusal reasons must be a mapping of reason -> "
                f"count, not {type(self.refusal_reasons).__name__}")
        for reason, count in self.refusal_reasons.items():
            if not isinstance(reason, str) or not reason:
                raise Refusal(
                    f"{self.field_id}: refusal reason key {reason!r} is not a "
                    "non-empty string; a reason has to be nameable to be reported")
            _strict_count(self.field_id, f"refusal reason {reason!r}", count)
        total = sum(self.refusal_reasons.values())
        if total != self.structured_refusals:
            raise Refusal(
                f"{self.field_id}: refusal reasons account for {total} replicates "
                f"but {self.structured_refusals} refused. Every structured refusal "
                "carries a recorded reason and no reason counts a replicate that "
                "did not refuse.")
        # The canonical zero form is the EMPTY mapping, which is what both
        # producers emit -- `field_primary_outcome` builds the map from the
        # refusals it actually saw, and `classify_field_size` writes `{}` on the
        # fully evaluable branch. A key counting its reason zero times passes the
        # arithmetic above while naming a reason that never occurred, so it is not
        # an alternative spelling of "nothing refused".
        if not self.structured_refusals and self.refusal_reasons:
            raise Refusal(
                f"{self.field_id}: no replicate refused, so the reason accounting "
                f"is the empty mapping, not {dict(self.refusal_reasons)!r}")

    @property
    def fully_evaluable(self) -> bool:
        """True iff every planned primary endpoint decision exists."""
        return self.structured_refusals == 0


def classify_field_size(outcome: FieldSizeOutcome, nominal: float) -> dict:
    """One field's PRIMARY size assessment. THE PRECEDENCE IS NORMATIVE.

    `size_validation_semantics.verdicts.evaluation_order` states it: a structured
    refusal is resolved FIRST, and the detector is NOT run on an incomplete
    primary sequence. The order is not a convenience. The two statistical verdicts
    partition every (rejections, R) pair between them -- `otherwise` catches
    everything that is not a detection -- so computing the detector first and then
    overriding it would already have claimed a clean field, and an all-refused
    field would report NO_SIGNIFICANT_SIZE_INFLATION_DETECTED on zero observations.
    """
    if not outcome.fully_evaluable:
        return {
            "field_id": outcome.field_id,
            "verdict": SIZE_NOT_EVALUABLE,
            "planned_replicates": outcome.planned_replicates,
            "evaluable": outcome.evaluable,
            "structured_refusals": outcome.structured_refusals,
            "rejections": outcome.rejections,
            "refusal_reasons": dict(outcome.refusal_reasons),
            "nominal_alpha": nominal,
            "boundary": size_boundary(outcome.planned_replicates, nominal),
            "primary_rule": ("a structured refusal is resolved FIRST: the "
                             "preregistered detector is NOT run on an incomplete "
                             "primary endpoint sequence"),
            "means": ("required primary evidence was not fully observed because "
                      "one or more valid structured refusals left the primary "
                      "endpoint undefined"),
            "does_not_mean": ("neither that excess size was established nor that "
                              "nominal size behaviour was established"),
            "campaign_classification": INCOMPLETE_EVIDENCE_CLASSIFICATION,
        }
    # Fully evaluable: the frozen rules are untouched, scored against the PLANNED
    # denominator, which equals `evaluable` precisely because nothing refused.
    result = dict(classify_size(outcome.rejections, outcome.planned_replicates,
                                nominal))
    result.update({
        "field_id": outcome.field_id,
        "planned_replicates": outcome.planned_replicates,
        "evaluable": outcome.evaluable,
        "structured_refusals": 0,
        "refusal_reasons": {},
    })
    return result


# ------------------------------------------------------------------ campaign
RELEASE_FAILING_CLASSIFICATIONS = (
    "SOFTWARE_OR_INVARIANT_FAILURE",
    "CALIBRATION_FAILURE",
    "NUMERICAL_OR_PRECISION_FAILURE",
)

# A missing row is not a successful zero-rejection row.
#: THE canonical four-field roster, typed ONCE. C2, C3 and C4 are all scored PER
#: FIELD over exactly these fields. `plan.bind_execution` refuses unless every one
#: of those cases declares this set in `fields_affected` and the adopted contract
#: carries it too, so a missing, duplicated, extra, unknown or reference-field-only
#: set cannot reach the classifier.
REQUIRED_SIZE_FIELDS = frozenset((
    "theta0_circular", "theta1_power", "theta2_ellipse", "theta3_temperature",
))
REQUIRED_C7_ALTERNATIVES = frozenset((
    "alt_1_06", "alt_0_93_1_05", "alt_1_10", "hard_1_025",
))

#: The three PER-FIELD size cases: (replicates PER FIELD, nominal alpha). Each
#: declared field keeps its OWN R-replicate sequence of decisions, so there is no
#: within-replicate cross-field reduction and no pooling of counts. The integer
#: boundary is deliberately NOT written here: `classify_size` derives it with
#: `size_boundary(R, alpha)`, which is the one canonical computation.
PER_FIELD_SIZE_CASES = {
    "C2": (400, 0.005),       # P1 rejection per field,          alpha_geom
    "C3": (400, 0.001),       # G5 / Block-2 rejection per field, alpha_2
    "C4": (2000, 0.004),      # Block-1 rejection per field,      alpha_1
}

#: What each per-field size case RELEASES on, and -- for C3 -- what it explicitly
#: does not. Reported beside the counts so no reader of a result has to infer
#: which endpoint carried the release decision.
PER_FIELD_ENDPOINTS = {
    "C2": {
        "primary_endpoint": "P1_FALSE_REJECTION_RATE_PER_FIELD",
        "elementary_event": "P1 rejection for ONE declared field",
    },
    "C3": {
        "primary_endpoint": "G5_BLOCK_SIZE",
        "elementary_event": "actual G5 / Block-2 rejection for ONE declared field",
        "secondary_diagnostic": {
            "label": "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC",
            "quantity": "the full two-block P1 result, recorded per field",
            "release_bearing": False,
            "note": ("reported because the frozen scientific purpose requires the "
                     "two-mode max statistic's INTERACTION WITH THE TWO-BLOCK GATE; "
                     "it never enters the C3 primary rejection count and cannot "
                     "fail the C3 release on its own"),
        },
    },
    "C4": {
        "primary_endpoint": "BLOCK1_ACHIEVED_SIZE",
        "elementary_event": "actual Block-1 rejection for ONE declared field",
    },
}


@dataclass(frozen=True)
class CampaignCounts:
    """Frozen shape of the counts the campaign will produce. No values are supplied here.

    C3 AND C4 CARRY FOUR FIELD COUNTS, NOT A SCALAR
        They used to carry `c3_rejections: int` and `c4_rejections: int`, which was
        the implementation of a replicate-level event the frozen authority never
        declared. The authority now declares both cases PER FIELD with no
        within-replicate reduction and no pooling, so a single scalar can no longer
        express the scientific result: it cannot say WHICH field inflated, and the
        count it would hold -- replicates in which ANY field rejected -- is a
        different statistical object with a different null rate. No ambiguous
        scalar is retained, because no official result data exists to be
        reinterpreted and an unused convenience field would be the exact ambiguity
        the amendment removed.
    """

    c1_successes: int                              # of 300
    c2_rejections_by_field: Mapping[str, int]      # of 400 each
    #: C3 and C4 carry a FieldSizeOutcome per field, not a count. Their primary
    #: endpoint is ONE BLOCK of the two-block gate and a valid structured refusal
    #: can leave it undefined, so the evaluable count, the refusal count and the
    #: rejection count must travel together. C2 keeps plain counts BY DESIGN: its
    #: composite P1 endpoint fails closed, its elementary event is defined for
    #: every replicate, and giving it the richer type would create a
    #: NOT_EVALUABLE path that frozen authority marks NOT_APPLICABLE for it.
    c3_rejections_by_field: Mapping[str, "FieldSizeOutcome"]   # planned 400 each
    c4_rejections_by_field: Mapping[str, "FieldSizeOutcome"]   # planned 2000 each
    c5_pass: bool
    c6_pass: bool
    c7_false_acceptances_by_alternative: Mapping[str, int]   # of 400 each
    c8_successes: int                              # of 200
    hard_failures: Sequence[str] = ()
    refusal_accounting_ok: bool = True


def _refusal_semantics(case: str) -> dict:
    """What a valid structured refusal means for this case. From the G5 amendment.

    C2 is scoped OUT explicitly rather than by silence: its composite P1 endpoint
    fails closed, so its primary decision is defined for every replicate and it has
    no NOT_EVALUABLE path at all.
    """
    if case == "C2":
        return {
            "undefined_primary_endpoint_possible": False,
            "verdict_on_structured_refusal": "NOT_APPLICABLE",
            "structured_refusal_note": (
                "the composite P1 decision FAILS CLOSED, so this case's elementary "
                "event is defined for every replicate including a structured "
                "refusal"),
        }
    return {
        "undefined_primary_endpoint_possible": True,
        "verdict_on_structured_refusal": SIZE_NOT_EVALUABLE,
        "refusal_is_statistical_rejection": False,
        "refusal_is_statistical_non_rejection": False,
        "primary_denominator": "PLANNED_R_PRESERVED",
        "release_requires": "EVALUABLE_AND_CLEAN",
        "campaign_failure_classification": INCOMPLETE_EVIDENCE_CLASSIFICATION,
        "tolerated_structured_refusal_fraction": "NONE",
    }


def classify_campaign(counts: CampaignCounts) -> dict:
    """The frozen conjunctive release rule.

    Every required case must pass on its own terms. There is NO weighted score and NO
    compensation: one case cannot make up for another's failure.
    """
    per_field = {"C2": counts.c2_rejections_by_field,
                 "C3": counts.c3_rejections_by_field,
                 "C4": counts.c4_rejections_by_field}
    for case, supplied in per_field.items():
        replicates, _nominal = PER_FIELD_SIZE_CASES[case]
        if set(supplied) != REQUIRED_SIZE_FIELDS:
            raise Refusal(
                f"{case} requires exactly the four declared field counts. A missing "
                "field, an extra field, a reference-field-only set and a single "
                "pooled scalar are each a DIFFERENT statistical object from the "
                "declared per-field rule, not a convenience")
        if case == "C2":
            if any(not isinstance(k, int) or isinstance(k, bool)
                   or not 0 <= k <= replicates for k in supplied.values()):
                raise Refusal(
                    f"{case} field rejection count exceeds its declared "
                    f"{replicates} per-field replicates")
            continue
        # C3 and C4 must arrive as THREE-STATE evidence. A bare count here would
        # be the pre-amendment shape, in which an undefined endpoint has already
        # been silently resolved into a rejection or a non-rejection.
        for fid, outcome in supplied.items():
            if not isinstance(outcome, FieldSizeOutcome):
                raise Refusal(
                    f"{case} field {fid} supplied {type(outcome).__name__}, not a "
                    "FieldSizeOutcome. A bare count cannot distinguish a defined "
                    "non-rejection from an undefined primary endpoint, and that "
                    "distinction is the release rule")
            if outcome.field_id != fid:
                raise Refusal(
                    f"{case} field {fid} carries evidence labelled "
                    f"{outcome.field_id!r}; field identity may not drift")
            if outcome.planned_replicates != replicates:
                raise Refusal(
                    f"{case} field {fid} declares a planned denominator of "
                    f"{outcome.planned_replicates}, but the frozen plan declares "
                    f"{replicates}. The planned R is the primary denominator and "
                    "never shrinks to the surviving replicates")
    if set(counts.c7_false_acceptances_by_alternative) != REQUIRED_C7_ALTERNATIVES:
        raise Refusal("C7 requires exactly the four declared alternative counts")
    if not 0 <= counts.c1_successes <= 300 or not 0 <= counts.c8_successes <= 200:
        raise Refusal("C1/C8 success counts exceed their declared replicate ranges")
    if any(not 0 <= k <= 400 for k in counts.c7_false_acceptances_by_alternative.values()):
        raise Refusal("C7 false-acceptance count exceeds 400 replicates")
    if type(counts.c5_pass) is not bool or type(counts.c6_pass) is not bool:
        raise Refusal("C5/C6 require explicit Boolean outcomes")
    failures: list[str] = []
    detail: dict[str, object] = {}

    # 1. C1 complete-pipeline success, unchanged
    c1_bound = cp_lower(counts.c1_successes, 300)
    c1_ok = c1_bound >= 0.90
    detail["C1"] = {"successes": counts.c1_successes, "replicates": 300,
                    "cp_lower": c1_bound, "target": 0.90, "passed": c1_ok,
                    "threshold": 279}
    if not c1_ok:
        failures.append("TRUE_BRIDGE_POWER_FAILURE (C1 complete-pipeline success)")

    # 2, 3, 4. C2, C3 and C4 PER FIELD, never pooled. Each declared field is its
    # own R-replicate size assessment against its own boundary and contributes its
    # own release condition, so a failing field stays identifiable in `failures`.
    # There is NO within-replicate any-field event, NO every-field event, NO
    # reference-field-only event and NO pooled count: each of those is a different
    # statistical object with a different null rate. Four field conditions entering
    # the conjunction below is an intersection-union test, not a reduction of the
    # replicate-level event -- the same shape C7 already uses per alternative.
    for case, endpoint in (("C2", "P1 geometry"), ("C3", "G5 block"),
                           ("C4", "Block-1 surrogate")):
        replicates, nominal = PER_FIELD_SIZE_CASES[case]
        detail[case] = {}
        for fid in sorted(per_field[case]):
            supplied = per_field[case][fid]
            res = (classify_size(supplied, replicates, nominal) if case == "C2"
                   else classify_field_size(supplied, nominal))
            detail[case][fid] = res
            # The two non-clean states are DIFFERENT scientific reasons and are
            # never collapsed: one says the size test rejected, the other says it
            # could not be validly evaluated as preregistered. Both block release.
            if res["verdict"] == SIZE_FAILURE:
                failures.append(
                    f"{SIZE_FAILURE} ({case} {endpoint}, field {fid})")
            elif res["verdict"] == SIZE_NOT_EVALUABLE:
                failures.append(
                    f"{INCOMPLETE_EVIDENCE_CLASSIFICATION} ({case} {endpoint}, "
                    f"field {fid}: required validation evidence incomplete, "
                    f"{res['structured_refusals']} structured refusal(s) of a "
                    f"planned {res['planned_replicates']})")

    # 5, 6. already-frozen criteria
    detail["C5"] = {"passed": counts.c5_pass}
    if not counts.c5_pass:
        failures.append("STATISTICAL_SIZE_FAILURE (C5 plug-in Branch-A)")
    detail["C6"] = {"passed": counts.c6_pass}
    if not counts.c6_pass:
        failures.append("MODE_RESOLUTION_FAILURE (C6 theta_cap boundary)")

    # 7. C7 per alternative, never pooled, G2 disposition
    detail["C7"] = {}
    for alt, k in counts.c7_false_acceptances_by_alternative.items():
        bound = cp_upper(k, 400)
        ok = bound <= 0.025
        detail["C7"][alt] = {"false_acceptances": k, "cp_upper": bound,
                             "target": 0.025, "passed": ok, "threshold": 4}
        if not ok:
            failures.append(f"FALSE_BRIDGE_DISCRIMINATION_FAILURE (C7 {alt})")

    # 8. C8 blinded scale control, G1 disposition
    c8_bound = cp_lower(counts.c8_successes, 200)
    c8_ok = c8_bound >= 0.90
    detail["C8"] = {"successes": counts.c8_successes, "replicates": 200,
                    "cp_lower": c8_bound, "target": 0.90, "passed": c8_ok,
                    "threshold": 188}
    if not c8_ok:
        failures.append("BLINDED_SCALE_CONTROL_FAILURE (C8)")

    # 9, 10. hard failures and refusal accounting
    for name in counts.hard_failures:
        if name in RELEASE_FAILING_CLASSIFICATIONS:
            failures.append(name)
    if not counts.refusal_accounting_ok:
        failures.append("STRUCTURED_REFUSAL_EXCESS (denominator accounting)")

    verdict = "VALIDATION_PASS" if not failures else "VALIDATION_FAILURE"
    return {
        "verdict": verdict,
        "failures": failures,
        "detail": detail,
        "rule": ("conjunctive: every required case must pass on its own terms; no weighted "
                 "score, no compensation between cases"),
        # C2, C3 and C4 each contribute FOUR field conditions. Stated explicitly so
        # a reader never has to infer which endpoint carried the release decision,
        # and so C3's full-P1 diagnostic is visibly NOT one of them.
        "endpoint_semantics": {
            case: dict(PER_FIELD_ENDPOINTS[case],
                       field_scope="PER_FIELD",
                       replicates_per_field=PER_FIELD_SIZE_CASES[case][0],
                       nominal_alpha=PER_FIELD_SIZE_CASES[case][1],
                       within_replicate_field_reduction="NONE",
                       pooling="FORBIDDEN",
                       required_field_conditions=sorted(REQUIRED_SIZE_FIELDS),
                       **_refusal_semantics(case))
            for case in PER_FIELD_SIZE_CASES
        },
        "independent_facts": {
            "complete_pipeline_met": c1_ok,
            "component_size_clean": not any(f.startswith(SIZE_FAILURE) for f in failures),
            # Separate from `component_size_clean` DELIBERATELY. A campaign with a
            # NOT_EVALUABLE field has no size-inflation finding, so the clean flag
            # above is True; reporting only that would read as "the components
            # behaved" when a required assessment was never made.
            "component_size_evaluable": not any(
                f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION) for f in failures),
            "incomplete_evidence_fields": [
                f for f in failures
                if f.startswith(INCOMPLETE_EVIDENCE_CLASSIFICATION)],
            "note": ("these are reported separately and never collapsed. C1 may meet >= 0.90 while a "
                     "component case detects significant size inflation; that is still a validation "
                     "failure, because the implemented calibration is not behaving according to its "
                     "declared nominal structure. The converse is also a valid scientific failure."),
        },
    }
