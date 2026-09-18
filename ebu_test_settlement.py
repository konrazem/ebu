"""EBU field evaluation, exact path settlement, and Mobius interaction audit.

Implements the HOMEOSTATIC FIELD, RECEIPT and INTERACTION-ANALYSIS layers of
the EBU Scientific Test Design (sections 6, 12-17, 20, 42).

**The field never acts** (Principle A).  Every function here evaluates a
transformation that the physical layer (`ebu_test_world`) performed or would
perform.  Nothing in this module moves resource.

**Committed authority reused, not re-derived.**  The potential is
`V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md` Definition 6.1,
`v_i(x) = alpha[L-x]_+^2 + beta[x-U]_+^2 + chi[R-x]_+^2`, implemented as
`d0_v29.penalty` with marginal `d0_v29.marginal`.  This module calls those
committed functions; it does not fork them, and it invents no weight or band
(design section 6).

**Exactness (section 42).**  Along a straight path the marginal of a piecewise
quadratic is piecewise LINEAR in the path parameter, with breakpoints where a
coordinate crosses its own `L`, `U` or `R`.  Splitting at those breakpoints and
integrating each linear piece is therefore EXACT - no quadrature, no tolerance
beyond floating point.  Endpoint difference remains an independent closure
check, exactly as section 42 requires.

**Status separation, maintained everywhere below.**
  * THEOREM: the group closure identity `sum_a R_a^V = V(z) - V(z + dx_G)`.
    It follows from linearity of the integral plus the fundamental theorem of
    calculus and holds for any `C^1` V and any straight common path.
  * IMPLEMENTATION: the exact breakpoint integrator here.
  * CANDIDATE: reading `R_a^V` as *the* registered per-action entitlement at
    group size >= 2.  Committed authority records this as scheme 4,
    "registered refinement, **not required**", with scheme 5 (one action per
    source per micro-step) "adopted for the first formal model", and
    escalation E2 / open problem O3 / 16.O3 unresolved.  The attribution record
    therefore carries an explicit diagnostic role and refuses settlement,
    wallet, causal-entitlement, Shapley and Mobius-allocation readings.
  * EVIDENCE: none. Nothing here is a scientific result.

**Execution safety.**  No world, tick, trajectory, simulation, parameter
search, subprocess or network call; no file is opened.  Every function is pure
over frozen or synthetic individual states.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Mapping, Sequence

import d0_v29 as d0
import ebu_test_world as world

__all__ = [
    "SettlementError", "ClosureViolation", "UnlicensedReading",
    "PosetRefusal",
    "potential", "marginal_at", "path_breakpoints", "path_integral",
    "endpoint_difference",
    "SimultaneousPathFieldAttribution", "PATH_SEMANTICS",
    "LICENSED_READINGS", "UNLICENSED_READINGS", "PATH_CLAIM_READINGS",
    "GroupSettlement", "settle_group",
    "telescope_path", "SegmentReceipt", "settle_segments",
    "subset_field_value", "boolean_mobius", "poset_mobius",
    "MobiusAudit", "audit_group", "require_no_double_issuance",
]


class SettlementError(Exception):
    """Base: the settlement or audit layer refused."""


class ClosureViolation(SettlementError):
    """A closure identity failed beyond the declared tolerance. INVALID."""


class UnlicensedReading(SettlementError):
    """A per-action number was read as something no authority licenses."""


class PosetRefusal(SettlementError):
    """A configuration family is not a valid poset for Mobius inversion."""


# ---------------------------------------------------------------------------
# section 6 - the committed potential and its marginal
# ---------------------------------------------------------------------------
def potential(spec: world.WorldSpec, values: Mapping) -> float:
    """V(x) = sum_i v_i(x_i), via the committed `d0_v29.penalty`.

    Separable by Definition 6.1, which is what makes locality exact rather than
    approximate (Lemma 6.6).  This is the represented homeostatic burden, NOT
    total physical energy (design section 6).
    """
    total = 0.0
    for node, spec_i in spec.node_specs.items():
        total += d0.penalty(spec_i.alpha, spec_i.beta, spec_i.chi,
                            spec_i.lower, spec_i.upper, spec_i.reserve,
                            values[node])
    return total


def marginal_at(spec: world.WorldSpec, node: str, x: float) -> float:
    """mu_i(x) = v_i'(x), via the committed `d0_v29.marginal`."""
    s = spec.node_specs[node]
    return d0.marginal(s.alpha, s.beta, s.chi, s.lower, s.upper, s.reserve, x)


# ---------------------------------------------------------------------------
# sections 12, 13, 42 - EXACT piecewise-analytic path integration
# ---------------------------------------------------------------------------
def path_breakpoints(spec: world.WorldSpec, z: Mapping,
                     delta: Mapping) -> tuple:
    """Every lambda in (0,1) where some coordinate crosses L, U or R.

    These are exactly the points where the piecewise-quadratic marginal changes
    branch.  Between consecutive breakpoints the integrand is linear in lambda,
    so integrating piecewise is exact.  Missing a breakpoint is the classic way
    an "analytic" integrator silently becomes an approximation, so all three
    bands are collected for every coordinate that moves.
    """
    cuts = {0.0, 1.0}
    for node, d in delta.items():
        if d == 0.0:
            continue
        s = spec.node_specs[node]
        start = z[node]
        for band in (s.lower, s.upper, s.reserve):
            lam = (band - start) / d
            if 0.0 < lam < 1.0:
                cuts.add(lam)
    return tuple(sorted(cuts))


def _integrand(spec: world.WorldSpec, z: Mapping, delta_group: Mapping,
               delta_action: Mapping, lam: float) -> float:
    """sum_i mu_i(z_i + lam*dG_i) * dA_i  -- the integrand of R_a^V."""
    total = 0.0
    for node, da in delta_action.items():
        if da == 0.0:
            continue
        x = z[node] + lam * delta_group.get(node, 0.0)
        total += marginal_at(spec, node, x) * da
    return total


def path_integral(spec: world.WorldSpec, z: Mapping, delta_group: Mapping,
                  delta_action: Mapping) -> float:
    """R_a^V = -int_0^1 grad V(z + lam*dx_G)^T dx_a dlambda, computed EXACTLY.

    The common path `x(lambda) = z + lambda * dx_G` is the one every
    simultaneous action actually travels together (design section 13,
    Principle D).  Each action's receipt is the accumulated local marginal
    along ITS OWN direction while all actions move together.

    Exact because the integrand is piecewise linear in lambda between the
    breakpoints returned by `path_breakpoints`; the trapezoid rule is exact on
    a linear function, so each piece is integrated without error.
    """
    cuts = path_breakpoints(spec, z, delta_group)
    total = 0.0
    for left, right in zip(cuts, cuts[1:]):
        width = right - left
        if width <= 0.0:
            continue
        f_left = _integrand(spec, z, delta_group, delta_action, left)
        f_right = _integrand(spec, z, delta_group, delta_action, right)
        total += 0.5 * (f_left + f_right) * width
    return -total


def endpoint_difference(spec: world.WorldSpec, z: Mapping,
                        delta_group: Mapping) -> float:
    """F(G) = V(z) - V(z + dx_G). The INDEPENDENT closure check (section 42)."""
    after = {node: z[node] + delta_group.get(node, 0.0) for node in z}
    return potential(spec, z) - potential(spec, after)


# ---------------------------------------------------------------------------
# section 13 - group settlement, with the per-action reading kept diagnostic
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# SIMULTANEOUS-PATH FIELD ATTRIBUTION (the m >= 2 record)
# ---------------------------------------------------------------------------
# Declared path semantics. Which one holds is a property of the SYNCHRONOUS
# MODEL, not of this code, so it is a required declaration rather than an
# inference.
#
#   model_realised_constant_rate
#       The declared synchronous model specifies that accepted actions act
#       SIMULTANEOUSLY at CONSTANT RATES over the tick. Then
#           x(lambda) = z + lambda * sum_a dx_a
#       IS the model-realised physical path, and the per-action integrals are
#       its EXACT MATHEMATICAL DECOMPOSITION. This is a statement about the
#       declared model's own path, and it is not generalised beyond it.
#
#   endpoint_interpolation
#       Only the pre- and post-state endpoints are known. The SAME straight
#       interpolation is then a DECLARED ACCOUNTING CONVENTION - a choice of
#       how to interpolate, not an observed physical path.
#
# In BOTH cases attribution alone creates no wallet credit, no ownership, no
# fairness claim, no causal entitlement, no Shapley meaning and no extra
# interaction issuance.
PATH_SEMANTICS = ("model_realised_constant_rate", "endpoint_interpolation")

#: Readings licensed under each declared path semantics.
LICENSED_READINGS = {
    "model_realised_constant_rate": (
        "model_realised_path_decomposition",   # exact decomposition of THE path
        "diagnostic", "reconstruction_check", "audit_record",
    ),
    "endpoint_interpolation": (
        "declared_accounting_convention",      # an interpolation, not a path
        "diagnostic", "reconstruction_check", "audit_record",
    ),
}

#: Refused under EVERY path semantics. Attribution alone establishes none of
#: these, and the list is explicit so a reading cannot arrive by convention.
UNLICENSED_READINGS = (
    "wallet_credit", "wallet", "ownership", "fairness_claim",
    "causal_entitlement", "shapley_meaning", "shapley_allocation",
    "aumann_shapley_allocation", "mobius_allocation",
    "extra_interaction_issuance", "settlement", "responsibility_share",
)

#: Refused specifically under `endpoint_interpolation`: claiming an observed or
#: physical path when only endpoints are known generalises the interpretation
#: beyond the declared path semantics.
PATH_CLAIM_READINGS = (
    "model_realised_path_decomposition", "physical_path_claim",
    "observed_physical_path", "common_physical_path_claim",
)


@dataclass(frozen=True)
class SimultaneousPathFieldAttribution:
    """The m >= 2 record: one action's share of a simultaneous group's value.

    Named `simultaneous-path field attribution` deliberately.  It is an
    ATTRIBUTION of field-value change along a declared path - not a settlement,
    not a credit, and not an entitlement.

    The number is exact.  What it MEANS depends on the declared
    `path_semantics`, which is why that is a required field rather than an
    assumption:

    * under `model_realised_constant_rate` the declared synchronous model says
      the actions genuinely act together at constant rates, so the straight
      path IS the model-realised physical path and these integrals are its
      exact mathematical decomposition;
    * under `endpoint_interpolation` only endpoints are known, so the identical
      arithmetic is a declared accounting convention.

    Under BOTH, `require_reading` refuses wallet credit, ownership, fairness,
    causal entitlement, Shapley meaning and extra interaction issuance.  Under
    `endpoint_interpolation` it additionally refuses any physical-path claim,
    because that would generalise the interpretation past the declared
    semantics.

    The GROUP TOTAL is a separate matter and is a theorem under either
    semantics (linearity of the integral plus the fundamental theorem of
    calculus); nothing here weakens it.
    """
    action_id: str
    value: float
    group_size: int
    path_semantics: str
    reading: str = "diagnostic"

    def __post_init__(self):
        if self.group_size < 1:
            raise SettlementError("group_size must be at least 1")
        if self.path_semantics not in PATH_SEMANTICS:
            raise SettlementError(
                f"path_semantics must be one of {PATH_SEMANTICS}; it is a "
                f"property of the declared synchronous model and is never "
                f"inferred from the arithmetic")
        self.require_reading(self.reading)

    def require_reading(self, reading: str) -> str:
        """Refuse a reading the declared path semantics does not license.

        At `group_size == 1` no attribution occurs - the record IS the whole
        group value and Theorem 8.2 applies under (T3) - so any reading is
        vacuously licensed. The question begins at two.
        """
        normalized = str(reading).strip().lower()
        if self.group_size <= 1:
            return normalized
        if normalized in UNLICENSED_READINGS:
            raise UnlicensedReading(
                f"reading action {self.action_id!r}'s simultaneous-path field "
                f"attribution over {self.group_size} actions as {normalized!r} "
                f"is refused under every path semantics. Attribution alone "
                f"creates no wallet credit, ownership, fairness claim, causal "
                f"entitlement, Shapley meaning or extra interaction issuance. "
                f"Licensed here: {LICENSED_READINGS[self.path_semantics]}.")
        if self.path_semantics == "endpoint_interpolation" \
                and normalized in PATH_CLAIM_READINGS:
            raise UnlicensedReading(
                f"{normalized!r} claims a realised physical path, but the "
                f"declared semantics is 'endpoint_interpolation': only the "
                f"pre- and post-state endpoints are known, so the straight "
                f"interpolation is a DECLARED ACCOUNTING CONVENTION. The "
                f"physical-path interpretation is not generalised beyond the "
                f"explicitly declared path semantics.")
        if normalized not in LICENSED_READINGS[self.path_semantics]:
            raise UnlicensedReading(
                f"unrecognized reading {normalized!r}; under "
                f"{self.path_semantics!r} the licensed readings are "
                f"{LICENSED_READINGS[self.path_semantics]}")
        return normalized

    @property
    def is_exact_decomposition_of_realised_path(self) -> bool:
        """True only under declared constant-rate simultaneous semantics."""
        return self.path_semantics == "model_realised_constant_rate"


@dataclass(frozen=True)
class GroupSettlement:
    """The settled simultaneous group: total, attributions, residual.

    `path_semantics` travels with the result so that a downstream reader cannot
    recover the numbers without also recovering the interpretation they are
    licensed under.
    """
    group_total: float
    endpoint_value: float
    receipts: tuple
    residual: float
    group_size: int
    path_semantics: str = "endpoint_interpolation"

    @property
    def shares_sum(self) -> float:
        return sum(r.value for r in self.receipts)


def settle_group(spec: world.WorldSpec, z: Mapping,
                 increments: Mapping, *, tolerance: float,
                 path_semantics: str,
                 reading: str = "diagnostic") -> GroupSettlement:
    """Settle one accepted simultaneous group along the common path.

    Verifies the section 13 closure identity

        sum_a R_a^V  ==  V(z) - V(z + dx_G)                        [THEOREM]

    and refuses beyond `tolerance` - which makes the affected run INVALID under
    section 34, never EBU-FAIL.

    `increments` maps `action_id -> {node: delta}` and must already hold
    ACCEPTED quantities (section 8): settling a request the resolver reduced is
    one of the deliberate errors section 19 requires the harness to catch.

    `path_semantics` is REQUIRED and has no default.  Whether the straight
    common path is the model-realised physical path or a declared endpoint
    interpolation is a property of the declared synchronous model, and letting
    it default would silently pick an interpretation.
    """
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) \
            or tolerance < 0.0:
        raise SettlementError("an explicit non-negative tolerance is required")
    if not increments:
        raise SettlementError("a group needs at least one action")
    group = dict.fromkeys(z, 0.0)
    for per_action in increments.values():
        for node, delta in per_action.items():
            if node not in group:
                raise SettlementError(f"increment names unknown node {node!r}")
            group[node] += delta
    size = len(increments)
    receipts = tuple(
        SimultaneousPathFieldAttribution(
            action_id=action_id,
            value=path_integral(spec, z, group, per_action),
            group_size=size, path_semantics=path_semantics, reading=reading)
        for action_id, per_action in sorted(increments.items()))
    group_total = path_integral(spec, z, group, group)
    endpoint = endpoint_difference(spec, z, group)
    residual = abs(endpoint - sum(r.value for r in receipts))
    if residual > tolerance:
        raise ClosureViolation(
            f"settlement closure residual {residual!r} exceeds tolerance "
            f"{tolerance!r}: sum of per-action path receipts "
            f"{sum(r.value for r in receipts)!r} != endpoint difference "
            f"{endpoint!r}. Section 34: the run is INVALID, not EBU-FAIL.")
    return GroupSettlement(group_total=group_total, endpoint_value=endpoint,
                           receipts=receipts, residual=residual,
                           group_size=size, path_semantics=path_semantics)


# ---------------------------------------------------------------------------
# section 20 - long-duration actions, live epochs and receipt telescoping
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SegmentReceipt:
    """One live epoch of a longer action."""
    segment_index: int
    start: Mapping
    increment: Mapping
    value: float


def telescope_path(spec: world.WorldSpec, z: Mapping,
                   segments: Sequence) -> tuple:
    """Walk a sequence of increments through LIVE state, one segment at a time.

    Section 20: a long action must read the field as it actually progresses, and
    an action starting later begins from the live state at its start, not from
    a frozen original field.  Each segment is therefore evaluated from the state
    the previous segments produced.

    Returns `(segment_receipts, final_state)`.  Nothing is iterated in time
    here beyond the segments the caller supplies; this is path decomposition,
    not a simulation.
    """
    current = dict(z)
    out = []
    for index, increment in enumerate(segments):
        value = path_integral(spec, current, increment, increment)
        out.append(SegmentReceipt(index, dict(current), dict(increment), value))
        current = {node: current[node] + increment.get(node, 0.0)
                   for node in current}
    return tuple(out), current


def settle_segments(spec: world.WorldSpec, z: Mapping, segments: Sequence,
                    *, tolerance: float) -> float:
    """Verify that segment receipts telescope to the whole-path value.

        sum_k R_k  ==  V(z) - V(x_final)                            [THEOREM]

    Exact for any segmentation because the path integral is additive over
    consecutive sub-paths.  This is what makes a long action's receipt
    independent of how finely it is segmented - and a failure here means the
    implementation, not the mathematics, is wrong.
    """
    receipts, final = telescope_path(spec, z, segments)
    total = sum(r.value for r in receipts)
    endpoint = potential(spec, z) - potential(spec, final)
    residual = abs(endpoint - total)
    if residual > tolerance:
        raise ClosureViolation(
            f"telescoping residual {residual!r} exceeds tolerance "
            f"{tolerance!r}: segment receipts {total!r} != endpoint "
            f"{endpoint!r}. A long action's receipt must not depend on how it "
            f"was segmented.")
    return residual


# ---------------------------------------------------------------------------
# sections 14-17 - Mobius interaction AUDIT (not the runtime settlement engine)
# ---------------------------------------------------------------------------
def subset_field_value(spec: world.WorldSpec, z: Mapping, resolve) -> "callable":
    """Build `F(S) = V(z) - V(x_S)` for subsets of a simultaneous group.

    `resolve(subset) -> {node: delta}` is the SAME physical resolver the full
    group used.  Section 15 is explicit that a subset may legitimately resolve
    to different accepted quantities than it holds in the full group - with one
    source shared, `rho(A) = 5` while `rho(AB) = (3, 3)` is valid - so this
    function never reuses the full group's quantities for a subset.  Fixture F7
    checks exactly that.

    Every subset starts from the SAME frozen baseline `z`.  Changing the
    baseline between counterfactuals is one of section 19's deliberate errors.
    """
    baseline = potential(spec, z)

    def F(subset) -> float:
        increments = resolve(tuple(sorted(subset)))
        after = {node: z[node] + increments.get(node, 0.0) for node in z}
        return baseline - potential(spec, after)

    return F


def boolean_mobius(members: Sequence, F) -> Mapping:
    """Boolean-lattice Mobius coefficients: I(S) = sum_{T<=S} (-1)^{|S-T|} F(T).

    Valid only when every subset is a physically meaningful configuration.
    When it is not, use `poset_mobius` - section 17 forbids inventing an
    impossible configuration and assigning it zero merely to complete a cube.
    """
    members = tuple(members)
    if len(set(members)) != len(members):
        raise PosetRefusal("duplicate member in the interaction family")
    out = {}
    for size in range(len(members) + 1):
        for subset in itertools.combinations(members, size):
            total = 0.0
            for inner_size in range(len(subset) + 1):
                for inner in itertools.combinations(subset, inner_size):
                    sign = -1.0 if (len(subset) - len(inner)) % 2 else 1.0
                    total += sign * F(inner)
            out[subset] = total
    return out


def poset_mobius(feasible: Sequence, F) -> Mapping:
    """Mobius coefficients over an ARBITRARY finite family of feasible subsets.

    Defined recursively over the induced subset order:

        I(S) = F(S) - sum_{T < S, T in the family} I(T)

    so reconstruction `sum_{T <= S, T in family} I(T) = F(S)` holds by
    construction over exactly the configurations that physically exist.

    **The family is deliberately NOT required to be downward closed.**  Section
    17 is explicit that a structurally impossible configuration must not be
    invented and assigned zero merely to complete a Boolean cube - so if `(b,)`
    cannot physically occur, the family `{(), (a,), (a,b)}` is legitimate and is
    handled here as the chain it is.  Requiring downward closure would force
    exactly the fabrication section 17 forbids.

    The empty configuration IS required: a zero-execution configuration is
    physically valid and is the base of the recursion.  Refusing a family
    without it is not the same as refusing a non-closed one.
    """
    family = tuple(sorted({tuple(sorted(s)) for s in feasible},
                          key=lambda s: (len(s), s)))
    if () not in set(family):
        raise PosetRefusal(
            "the feasible family must contain the empty configuration; a "
            "zero-execution configuration is physically valid and is the base "
            "of the Mobius recursion")
    coefficients = {}
    for subset in family:                       # linear extension: size then key
        total = F(subset)
        below = set(subset)
        for other in family:
            if other != subset and set(other) < below:
                total -= coefficients[other]
        coefficients[subset] = total
    return coefficients


@dataclass(frozen=True)
class MobiusAudit:
    """One selected-event interaction audit (section 33's audited-event record)."""
    members: tuple
    coefficients: Mapping
    group_value: float
    reconstruction: float
    residual: float
    lattice: str

    def interaction_of(self, subset) -> float:
        return self.coefficients[tuple(sorted(subset))]


def audit_group(members: Sequence, F, *, tolerance: float,
                feasible: Sequence = None) -> MobiusAudit:
    """Decompose a group's field value into irreducible interaction structure.

    Roles, per section 15: interaction detection, topology discovery, motif
    analysis, recursive-topology validation, independent reconstruction of the
    exact group value, and selected-event audit.  Mobius is NOT the runtime
    settlement engine (Principle F) and this function is never on a decision
    path.

    Verifies section 16's reconstruction leg,
    `F(G) == sum_{S <= G} I_F(S)`, to the declared tolerance.
    """
    members = tuple(members)
    if feasible is None:
        coefficients = boolean_mobius(members, F)
        lattice = "boolean"
        top = tuple(sorted(members))
        below = [s for s in coefficients if set(s) <= set(top)]
    else:
        coefficients = poset_mobius(feasible, F)
        lattice = "feasible_poset"
        top = tuple(sorted(members))
        if top not in coefficients:
            raise PosetRefusal(
                f"the full group {top} is not in the feasible family")
        below = [s for s in coefficients if set(s) <= set(top)]
    reconstruction = sum(coefficients[s] for s in below)
    group_value = F(top)
    residual = abs(group_value - reconstruction)
    if residual > tolerance:
        raise ClosureViolation(
            f"Mobius reconstruction residual {residual!r} exceeds tolerance "
            f"{tolerance!r}: reconstruction {reconstruction!r} != group value "
            f"{group_value!r}")
    return MobiusAudit(members=top, coefficients=coefficients,
                       group_value=group_value, reconstruction=reconstruction,
                       residual=residual, lattice=lattice)


def require_no_double_issuance(group_total: float, audit: MobiusAudit, *,
                               tolerance: float) -> float:
    """Section 14: interaction is ALREADY in the realised joint field change.

    If `F(A) = 8`, `F(B) = 7` and `F(AB) = 20`, then `I(AB) = 5` explains the
    20 - it does not entitle anyone to a further 5 afterwards.  This function
    exists so the rule is checkable: it confirms the Mobius reconstruction
    equals the settled group total and returns that total UNCHANGED, and there
    is deliberately no function anywhere in this module that adds interaction
    coefficients on top of a settled group value.

    A persistent pair or triple balance would require an actual persistent
    state coordinate in `ebu_test_world`, which the interaction coefficients
    are not.
    """
    residual = abs(group_total - audit.reconstruction)
    if residual > tolerance:
        raise ClosureViolation(
            f"Mobius reconstruction {audit.reconstruction!r} disagrees with the "
            f"settled group total {group_total!r} by {residual!r}")
    return group_total
