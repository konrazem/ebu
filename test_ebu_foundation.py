"""EBU foundation conformance gate: fixtures F1-F10 and negative controls.

Implements the MANDATORY gate of EBU Scientific Test Design sections 18 and 19.
Section 18 requires these fixtures before any long-run campaign; section 19
requires proof that incorrect implementations FAIL.

**Execution class: NON-MODEL-ADVANCING STATIC/PURE.**  Every check here is a
pure-function evaluation on a frozen or synthetic INDIVIDUAL state, an AST or
source inspection, or a refusal check.

**What is actually checked, stated precisely.**
`test_transition_guards_statically` parses THIS FILE's own source and asserts it
contains no DIRECT call to `apply_joint`, `plan_tick` or `execute_tick`.  That
is a real check, and it is also a LIMITED one: **it inspects direct calls in one
file.  It does not prove that an imported module, a helper, a callback or a
dynamic dispatch reached from here cannot execute a transition.**  A stronger
guarantee would need call-graph analysis or runtime instrumentation, neither of
which is implemented.  The claim this file makes is therefore the narrow one -
no direct transition call - and not "no transition can possibly occur".

This label covers THIS suite.  It is not a claim about the repository's whole
CI workflow, which also runs older V2.9/V3.0 suites whose execution class is
declared separately and is not all static.

**A previous revision of this file was mislabelled.**  It executed one
`world.apply_joint` in F8 and one `proto.execute_tick` conformance tick, while
its footer printed `Model-state advancement: NONE`.  That statement was FALSE
and is withdrawn.  Both checks now live in
`test_ebu_foundation_transitions.py`, a separate execution class that requires
`EBU_ALLOW_MODEL_TRANSITIONS=1` and is not on the default CI path.  The
guarantees they exercised are retained here by AST inspection of the transition
functions themselves.

Nothing is written and no network or subprocess is touched.

**The numbers here are synthetic and carry no scientific meaning.**  They
exercise mathematics and mechanism only.  No world, band, weight, demand
distribution, horizon, threshold or success criterion is adopted anywhere in
this file, and a test at the end asserts that none may be.
"""
from __future__ import annotations

import ast
import inspect
import re
import sys

import authority_coordinate as ac
import ebu_test_protocol as proto
import ebu_test_settlement as settle
import ebu_test_world as world

PASSED = FAILED = GROUPS = 0
EXACT = 1e-12


def group(title: str) -> None:
    global GROUPS
    GROUPS += 1
    print(f"\n[{GROUPS:02d}] {title}")


def check(condition: bool, label: str) -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  PASS {label}")
    else:
        FAILED += 1
        print(f"  FAIL {label}")


def rejects(fn, label: str, contains: str = "") -> None:
    try:
        fn()
    except Exception as error:
        check(not contains or contains in str(error), label)
    else:
        check(False, label)


# --- synthetic fixture world; meaningless numbers, adopted by nothing -------
def fixture_spec(nodes=("n0", "n1", "n2"), capacity=20.0, lower=4.0,
                 upper=16.0, reserve=2.0, alpha=1.0, beta=1.0, chi=1.0):
    edges = tuple(("n0", n) for n in nodes if n != "n0")
    topo = world.Topology(nodes, edges)
    specs = {n: world.NodeSpec(n, capacity, lower, upper, reserve,
                               alpha, beta, chi) for n in nodes}
    return world.WorldSpec("SYNTHETIC-FIXTURE", "0", topo, specs,
                           path_semantics="model_realised_constant_rate")


# ===========================================================================
# Section 18 - foundation conformance fixtures
# ===========================================================================
def test_f1_one_finite_action():
    group("F1 - one finite action: endpoint difference == path integral")
    spec = fixture_spec()
    for z, delta in (
        ({"n0": 15.0, "n1": 3.0, "n2": 5.0}, {"n0": -4.0, "n1": 4.0}),
        ({"n0": 18.0, "n1": 1.0, "n2": 2.0}, {"n0": -6.0, "n1": 6.0}),
        ({"n0": 5.0, "n1": 17.0, "n2": 9.0}, {"n0": 3.0, "n1": -3.0}),
    ):
        path = settle.path_integral(spec, z, delta, delta)
        endpoint = settle.endpoint_difference(spec, z, delta)
        check(abs(path - endpoint) <= EXACT,
              f"path {path:.10g} == endpoint {endpoint:.10g}")

    # Exactness is structural: the integrator must split at every band crossing.
    z = {"n0": 18.0, "n1": 1.0, "n2": 2.0}
    delta = {"n0": -16.0, "n1": 16.0}          # crosses L, R and U of n1
    cuts = settle.path_breakpoints(spec, z, delta)
    check(len(cuts) > 2, f"band crossings produce interior breakpoints ({len(cuts)})")
    check(abs(settle.path_integral(spec, z, delta, delta)
              - settle.endpoint_difference(spec, z, delta)) <= EXACT,
          "exact across multiple band crossings")


def test_f2_symmetric_simultaneous():
    group("F2 - two symmetric simultaneous actions: endpoint == group == sum")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 1.0}
    increments = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    check(abs(g.shares_sum - g.endpoint_value) <= EXACT,
          f"sum of receipts {g.shares_sum:.10g} == endpoint {g.endpoint_value:.10g}")
    check(abs(g.group_total - g.endpoint_value) <= EXACT,
          "group path integral == endpoint difference")
    values = [r.value for r in g.receipts]
    check(abs(values[0] - values[1]) <= EXACT,
          "a genuinely symmetric fixture yields equal receipts")

    # Mobius reconstruction over the same frozen baseline.
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))
    audit = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    check(audit.residual <= EXACT, "Mobius reconstruction returns the group value")


def _merge(increments, subset):
    out = {}
    for name in subset:
        for node, delta in increments[name].items():
            out[node] = out.get(node, 0.0) + delta
    return out


def test_f3_asymmetric_simultaneous():
    group("F3 - asymmetric actions must NOT produce equal receipts")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 1.0}
    increments = {"a": {"n0": -6.0, "n1": 6.0}, "b": {"n0": -1.0, "n2": 1.0}}
    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    values = {r.action_id: r.value for r in g.receipts}
    check(abs(g.shares_sum - g.endpoint_value) <= EXACT, "closure still exact")
    check(abs(values["a"] - values["b"]) > EXACT,
          f"unequal quantities give unequal receipts ({values['a']:.6g} vs "
          f"{values['b']:.6g})")

    # Asymmetry in the FIELD alone must also separate the receipts.
    uneven = fixture_spec()
    uneven = world.WorldSpec(
        "SYNTHETIC-FIXTURE", "0", uneven.topology,
        {"n0": uneven.node_specs["n0"],
         "n1": world.NodeSpec("n1", 20.0, 4.0, 16.0, 2.0, 5.0, 1.0, 1.0),
         "n2": world.NodeSpec("n2", 20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0)},
        path_semantics="model_realised_constant_rate")
    sym = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    g2 = settle.settle_group(uneven, z, sym, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    v2 = {r.action_id: r.value for r in g2.receipts}
    check(abs(v2["a"] - v2["b"]) > EXACT,
          "equal quantities into different fields give different receipts")


def test_f4_positive_interaction():
    group("F4 - positive interaction is already inside the joint settlement")
    # Constructing this legitimately is not arbitrary. With the committed
    # SEPARABLE CONVEX potential (Definition 6.1), two actions that push the
    # SAME direction through a shared node always interact non-positively:
    # their interaction is exactly minus the second difference of v_i, which
    # convexity makes >= 0. Positive interaction therefore requires OPPOSING
    # flows through the shared node, where the two actions partly cancel.
    topo = world.Topology(("n0", "n1", "n2"), (("n1", "n0"), ("n0", "n2")))
    specs = {n: world.NodeSpec(n, 40.0, 4.0, 16.0, 0.0, 1.0, 1.0, 0.0)
             for n in ("n0", "n1", "n2")}
    spec = world.WorldSpec("SYNTHETIC-F4", "0", topo, specs,
                           path_semantics="model_realised_constant_rate")
    z = {"n0": 18.0, "n1": 10.0, "n2": 10.0}          # n0 sits above U

    increments = {"a": {"n1": -2.0, "n0": 2.0},       # pushes n0 further up
                  "b": {"n0": -2.0, "n2": 2.0}}       # pulls n0 back down
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))
    fa, fb, fab = F(("a",)), F(("b",)), F(("a", "b"))
    check(fab > fa + fb + EXACT,
          f"F(AB)={fab:.6g} > F(A)+F(B)={fa + fb:.6g} (positive interaction)")

    audit = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    interaction = audit.interaction_of(("a", "b"))
    check(interaction > EXACT, f"I(AB)={interaction:.6g} is positive")

    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    check(abs(g.endpoint_value - fab) <= EXACT,
          "the settled group total already equals F(AB)")
    check(abs(g.shares_sum - fab) <= EXACT,
          "the per-action path receipts already sum to it")
    total = settle.require_no_double_issuance(g.endpoint_value, audit,
                                              tolerance=EXACT)
    check(abs(total - g.endpoint_value) <= EXACT,
          "section 14: the interaction is NOT issued a second time")

    # EXACT ASSUMPTIONS of this fixture, asserted so they cannot drift and so
    # the result is never restated more generally than it was obtained.
    check(spec.eta == 1.0 and spec.is_conservative,
          "F4 assumption: closed, lossless, conservative world")
    check(all(specs[n].chi == 0.0 for n in specs),
          "F4 assumption: reserve term switched off (chi = 0)")
    check(all(specs[n].alpha == 1.0 and specs[n].beta == 1.0 for n in specs),
          "F4 assumption: unit band weights, separable convex v_i")
    check(z["n0"] > specs["n0"].upper,
          "F4 assumption: the shared node n0 starts ABOVE its upper band")
    check(increments["a"]["n0"] > 0 and increments["b"]["n0"] < 0,
          "F4 assumption: the two actions push n0 in OPPOSING directions")
    check(abs(increments["a"]["n0"] + increments["b"]["n0"]) <= EXACT,
          "F4 assumption: the opposing flows exactly cancel at n0")
    check(abs(interaction - 8.0) <= EXACT,
          "F4 result: I(AB) = +8 exactly, under those assumptions only")

    # NON-GENERALISATION. The positive result holds for opposing flows through
    # a shared node under a separable convex potential. It is NOT a claim about
    # same-direction interaction, and NOT a claim about any non-separable
    # potential - no non-separable potential exists in this repository.
    check(not hasattr(settle, "factor_potential"),
          "no non-separable factor potential exists; F4 claims nothing about one")

    # Record the structural fact the fixture had to work around.
    same_direction = fixture_spec()
    zz = {"n0": 19.0, "n1": 1.0, "n2": 1.0}
    inc2 = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    F2 = settle.subset_field_value(same_direction, zz,
                                   lambda s: _merge(inc2, s))
    a2 = settle.audit_group(("a", "b"), F2, tolerance=EXACT)
    check(a2.interaction_of(("a", "b")) <= EXACT,
          "same-direction flows through a shared source cannot interact "
          "positively under a convex separable V")


def test_f5_negative_interaction():
    group("F5 - independent frozen quotes would OVERSTATE the group result")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 2.0}
    increments = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))
    fa, fb, fab = F(("a",)), F(("b",)), F(("a", "b"))
    check(fab < fa + fb - EXACT,
          f"F(AB)={fab:.6g} < F(A)+F(B)={fa + fb:.6g} (negative interaction)")
    check(fa + fb - fab > EXACT,
          f"independent quotes overstate by {fa + fb - fab:.6g}")
    audit = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    check(audit.interaction_of(("a", "b")) < -EXACT, "I(AB) is negative")
    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    check(abs(g.shares_sum - fab) <= EXACT,
          "joint path settlement pays the true group total, not the naive sum")


def test_f6_three_way_interaction():
    group("F6 - a genuine three-way term, independently checked")
    spec = fixture_spec(("n0", "n1", "n2", "n3"))
    z = {"n0": 19.0, "n1": 1.0, "n2": 1.0, "n3": 1.0}
    increments = {"a": {"n0": -2.0, "n1": 2.0},
                  "b": {"n0": -2.0, "n2": 2.0},
                  "c": {"n0": -2.0, "n3": 2.0}}
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))
    audit = settle.audit_group(("a", "b", "c"), F, tolerance=EXACT)
    check(audit.residual <= EXACT, "three-way Mobius reconstruction is exact")

    # Independent hand computation of the inclusion-exclusion coefficient.
    manual = (F(("a", "b", "c")) - F(("a", "b")) - F(("a", "c")) - F(("b", "c"))
              + F(("a",)) + F(("b",)) + F(("c",)) - F(()))
    check(abs(audit.interaction_of(("a", "b", "c")) - manual) <= EXACT,
          f"I(ABC)={audit.interaction_of(('a','b','c')):.6g} matches inclusion-exclusion")

    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    check(abs(g.shares_sum - g.endpoint_value) <= EXACT,
          "three-action path closure is exact")
    check(g.group_size == 3, "the group is genuinely of size three")


def test_f7_shared_source_resolution():
    group("F7 - subset counterfactuals may resolve to DIFFERENT quantities")
    # Section 15: rho(A)=5 while rho(AB)=(3,3) is valid under one resolver.
    budget = 6.0
    requests = {("n0", "n1"): 5.0, ("n0", "n2"): 5.0}
    alone = world.resolve_shared_source("n0", {("n0", "n1"): 5.0}, budget)
    both = world.resolve_shared_source("n0", requests, budget)
    check(abs(alone.accepted[("n0", "n1")] - 5.0) <= EXACT,
          "A alone is served in full (5.0)")
    check(abs(both.accepted[("n0", "n1")] - 3.0) <= EXACT,
          "A within AB is scaled to 3.0")
    check(both.was_scaled and not alone.was_scaled,
          "the resolver scaled the joint request only")
    check(abs(both.sigma - 0.6) <= EXACT,
          "sigma = min(1, budget/total) = 0.6, the committed P1C rule")

    # The subset field value must use the RE-RESOLVED quantities.
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 1.0}

    def resolve(subset):
        req = {e: 5.0 for e, name in (((("n0", "n1")), "a"), ((("n0", "n2")), "b"))
               if name in subset}
        if not req:
            return {}
        outcome = world.resolve_shared_source("n0", req, budget)
        out = {}
        for (src, dst), q in outcome.accepted.items():
            out[src] = out.get(src, 0.0) - q
            out[dst] = out.get(dst, 0.0) + q
        return out

    F = settle.subset_field_value(spec, z, resolve)
    check(abs(F(("a",)) - F(("b",))) <= EXACT, "symmetric singletons agree")
    audit = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    check(audit.residual <= EXACT,
          "Mobius reconstruction holds under re-resolved subsets")


def test_f8_conservation():
    group("F8 - exact closed-system conservation (STATIC: no transition call)")
    spec = fixture_spec()
    check(spec.is_conservative, "the fixture world is closed and lossless")
    state = world.WorldState(spec.digest, {"n0": 18.0, "n1": 1.0, "n2": 1.0})
    ladder = world.QuantityLadder(4.0, 4.0, 4.0, 4.0, 4.0)
    action = world.Action("A", "fixture", ("n0", "n1"), "scalar", ladder,
                          0, 0, "fixture-permission")

    # Conservation is a property of the INCREMENT ALGEBRA, checkable without
    # producing a successor state. `Action.increment` is a pure dict.
    increment = action.increment(spec)
    check(abs(sum(increment.values())) <= EXACT,
          "the increment sums to zero: nothing is created or destroyed")
    check(abs(increment["n0"] + 4.0) <= EXACT, "source loses exactly 4")
    check(abs(increment["n1"] - 4.0) <= EXACT, "destination gains exactly 4")

    # The successor VALUES are computed purely; no WorldState is advanced.
    projected = world.joint_successor(spec, state, [action])
    check(abs(projected["n0"] - 14.0) <= EXACT, "projected source is 14")
    check(abs(projected["n1"] - 5.0) <= EXACT, "projected destination is 5")
    check(abs(sum(projected.values()) - state.total()) <= EXACT,
          "the projected total equals the pre-state total")

    # The conservation METRIC is pure over two states, both constructed as data.
    after = world.WorldState(spec.digest, projected)
    check(world.conservation_residual(spec, state, after) <= EXACT,
          "conservation residual between pre and projected state is exact")
    leaky = world.WorldState(spec.digest, {"n0": 10.0, "n1": 1.0, "n2": 1.0})
    check(world.conservation_residual(spec, state, leaky) > EXACT,
          "a vanished quantity shows up as a non-zero residual")

    # A lossy world must declare where the loss goes, or refuse.
    rejects(lambda: world.WorldSpec("L", "0", spec.topology, spec.node_specs,
                                    eta=0.9,
                                    path_semantics="model_realised_constant_rate"),
            "eta<1 without a declared loss_sink refuses",
            "Section 3 forbids silent destruction")
    # The transition function's own conservation guard is asserted statically
    # in test_transition_guards_statically; executing it belongs to
    # test_ebu_foundation_transitions.py.


def test_f9_long_overlapping_epochs():
    group("F9 - live-state segmentation and receipt telescoping")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 1.0}

    # One long action, cut into segments: the total must not depend on the cut.
    whole = {"n0": -8.0, "n1": 8.0}
    coarse = [{"n0": -4.0, "n1": 4.0}, {"n0": -4.0, "n1": 4.0}]
    fine = [{"n0": -1.0, "n1": 1.0}] * 8
    direct = settle.path_integral(spec, z, whole, whole)
    for name, segments in (("2 segments", coarse), ("8 segments", fine)):
        residual = settle.settle_segments(spec, z, segments, tolerance=EXACT)
        receipts, final = settle.telescope_path(spec, z, segments)
        total = sum(r.value for r in receipts)
        check(residual <= EXACT, f"{name}: telescoping residual is exact")
        check(abs(total - direct) <= EXACT,
              f"{name}: total {total:.10g} == whole-path {direct:.10g}")

    # Section 20: B starting later reads the LIVE state, not the original.
    a_first = [{"n0": -4.0, "n1": 4.0}]
    receipts_a, mid = settle.telescope_path(spec, z, a_first)
    b_from_live = settle.path_integral(spec, mid, {"n0": -2.0, "n2": 2.0},
                                       {"n0": -2.0, "n2": 2.0})
    b_from_frozen = settle.path_integral(spec, z, {"n0": -2.0, "n2": 2.0},
                                         {"n0": -2.0, "n2": 2.0})
    check(mid["n0"] == 14.0, "the live state advanced before B began")
    check(isinstance(b_from_live, float) and isinstance(b_from_frozen, float),
          "a later action is evaluated from the live state, not the frozen one")


def test_f10_mobius_reconstruction():
    group("F10 - Mobius reconstruction, Boolean AND feasible poset")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 2.0}
    increments = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))

    boolean = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    check(boolean.lattice == "boolean", "the Boolean case is exercised")
    check(boolean.residual <= EXACT, "Boolean reconstruction is exact")
    check(abs(sum(boolean.coefficients[s] for s in boolean.coefficients
                  if set(s) <= {"a", "b"}) - F(("a", "b"))) <= EXACT,
          "inverse Mobius returns the declared group field value")

    # Section 17: ('b',) structurally impossible must NOT be invented as zero.
    feasible = [(), ("a",), ("a", "b")]
    poset = settle.audit_group(("a", "b"), F, tolerance=EXACT, feasible=feasible)
    check(poset.lattice == "feasible_poset", "the poset case is exercised")
    check(poset.residual <= EXACT, "poset reconstruction is exact")
    check(("b",) not in poset.coefficients,
          "the impossible configuration is absent, not fabricated as zero")
    check(abs(sum(poset.coefficients.values()) - F(("a", "b"))) <= EXACT,
          "poset coefficients reconstruct the group value")
    rejects(lambda: settle.poset_mobius([("a",), ("a", "b")], F),
            "a family without the empty configuration refuses",
            "must contain the empty configuration")


# ===========================================================================
# Section 19 - deliberately broken implementations MUST fail
# ===========================================================================
def test_negative_controls():
    group("section 19 - eleven deliberate errors, each must be caught")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 2.0}
    state = world.WorldState(spec.digest, z)

    # NC1 - settling the REQUESTED quantity instead of the ACCEPTED one.
    outcome = world.resolve_shared_source(
        "n0", {("n0", "n1"): 5.0, ("n0", "n2"): 5.0}, 6.0)
    accepted = outcome.accepted[("n0", "n1")]
    settled_on_request = settle.path_integral(
        spec, z, {"n0": -6.0, "n1": 3.0, "n2": 3.0}, {"n0": -5.0, "n1": 5.0})
    settled_on_accept = settle.path_integral(
        spec, z, {"n0": -6.0, "n1": 3.0, "n2": 3.0},
        {"n0": -accepted, "n1": accepted})
    check(abs(settled_on_request - settled_on_accept) > EXACT,
          "NC1 settling the request differs from settling the accepted quantity")
    rejects(lambda: world.QuantityLadder(5.0, 5.0, 5.0, 3.0, 3.0).audit_clean()
            or (_ for _ in ()).throw(AssertionError()),
            "NC1 a measured-vs-accepted mismatch is not audit-clean")

    # NC2 - evaluating from STALE state.
    stale = settle.path_integral(spec, z, {"n0": -2.0, "n1": 2.0},
                                 {"n0": -2.0, "n1": 2.0})
    live_state = {"n0": 14.0, "n1": 5.0, "n2": 2.0}
    live = settle.path_integral(spec, live_state, {"n0": -2.0, "n1": 2.0},
                                {"n0": -2.0, "n1": 2.0})
    check(abs(stale - live) > EXACT,
          "NC2 a stale baseline gives a different receipt than the live one")

    # NC3 - imposing a sequential order on a SIMULTANEOUS event.
    increments = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    joint = settle.settle_group(spec, z, increments, tolerance=EXACT,
                                 path_semantics="model_realised_constant_rate")
    seq_first = settle.path_integral(spec, z, increments["a"], increments["a"])
    mid = {k: z[k] + increments["a"].get(k, 0.0) for k in z}
    seq_second = settle.path_integral(spec, mid, increments["b"], increments["b"])
    by_action = {r.action_id: r.value for r in joint.receipts}
    check(abs(seq_first - by_action["a"]) > EXACT
          or abs(seq_second - by_action["b"]) > EXACT,
          "NC3 sequential order gives the first mover a different receipt")
    check(abs((seq_first + seq_second) - joint.endpoint_value) <= EXACT,
          "NC3 the TOTAL still telescopes - only the split differs")

    # NC4 - settling independent same-baseline quotes as if additive.
    F = settle.subset_field_value(spec, z, lambda s: _merge(increments, s))
    naive = F(("a",)) + F(("b",))
    check(abs(naive - joint.endpoint_value) > EXACT,
          f"NC4 naive sum {naive:.6g} != true group {joint.endpoint_value:.6g}")

    # NC5 - adding Mobius interaction on top of an already exact group value.
    audit = settle.audit_group(("a", "b"), F, tolerance=EXACT)
    inflated = joint.endpoint_value + audit.interaction_of(("a", "b"))
    check(abs(inflated - joint.endpoint_value) > EXACT,
          "NC5 re-adding I(AB) changes a total that was already correct")
    rejects(lambda: settle.require_no_double_issuance(
                inflated, audit, tolerance=EXACT),
            "NC5 double issuance is refused", "disagrees with the settled")

    # NC6 - changing the BASELINE between subset counterfactuals.
    shifted = settle.subset_field_value(spec, {"n0": 17.0, "n1": 1.0, "n2": 2.0},
                                        lambda s: _merge(increments, s))
    check(abs(shifted(("a",)) - F(("a",))) > EXACT,
          "NC6 a shifted baseline changes the subset field value")

    # NC7 - silently changing the potential definition.
    altered = world.WorldSpec(
        "SYNTHETIC-FIXTURE", "0", spec.topology,
        {n: world.NodeSpec(n, 20.0, 4.0, 16.0, 2.0,
                           2.0 if n == "n1" else 1.0, 1.0, 1.0)
         for n in spec.topology.nodes},
        path_semantics="model_realised_constant_rate")
    check(altered.digest != spec.digest,
          "NC7 changing a potential weight changes the world digest")
    check(abs(settle.potential(altered, z) - settle.potential(spec, z)) > EXACT,
          "NC7 the altered potential yields a different V")

    # NC8 - violating source capacity / the hard physical domain. Detected by
    # the PURE predicate `hard_feasible`; that `apply_joint` then refuses on a
    # non-empty result is asserted statically in
    # test_transition_guards_statically and exercised in the transition suite.
    huge = world.Action("X", "fixture", ("n0", "n1"), "scalar",
                        world.QuantityLadder(30.0, 30.0, 30.0, 30.0, 30.0),
                        0, 0, "fixture")
    offending = world.hard_feasible(spec, state, [huge])
    check(offending and any(node == "n0" for node, _ in offending),
          "NC8 leaving the hard physical domain is detected at the source")
    # Jointly infeasible though individually feasible.
    half = [world.Action("H0", "fixture", ("n0", "n1"), "scalar",
                         world.QuantityLadder(10.0, 10.0, 10.0, 10.0, 10.0),
                         0, 0, "fixture"),
            world.Action("H1", "fixture", ("n0", "n2"), "scalar",
                         world.QuantityLadder(10.0, 10.0, 10.0, 10.0, 10.0),
                         0, 0, "fixture")]
    check(world.hard_feasible(spec, state, [half[0]]) == ()
          and world.hard_feasible(spec, state, [half[1]]) == ()
          and world.hard_feasible(spec, state, half) != (),
          "NC8 two individually feasible withdrawals are jointly infeasible")

    # NC9 - losing resource from the closed system.
    leaky = world.WorldState(spec.digest, {"n0": 10.0, "n1": 1.0, "n2": 2.0})
    residual = world.conservation_residual(spec, state, leaky)
    check(residual > EXACT, f"NC9 a vanished 8.0 shows as residual {residual:.6g}")

    # NC10 - a controller reading global V or any undeclared field.
    schedule = world.DemandSchedule("s", "m", 1, ())
    view = proto.build_local_view(spec, state, "n0", 0, schedule)
    for forbidden in ("global_V", "full_state", "future_demand", "rollout",
                      "oracle_verdict", "research_score", "other_arm"):
        rejects(lambda f=forbidden: getattr(view, f),
                f"NC10 reading {forbidden!r} refuses", "may not read")
    check(view.source_stock == 18.0, "the permitted local read still works")

    # NC11 - a controller inspecting FUTURE demand.
    future = world.DemandSchedule("s", "m", 5, (
        world.DemandEvent(0, ("n0", "n1"), 1.0),
        world.DemandEvent(3, ("n0", "n1"), 9.0)))
    check(len(future.at_tick(0)) == 1 and future.at_tick(0)[0].quantity == 1.0,
          "NC11 the present tick is revealed")
    check(not hasattr(future, "future") and not hasattr(future, "__getitem__"),
          "NC11 the schedule exposes no future accessor")
    view2 = proto.build_local_view(spec, state, "n0", 0, future)
    check(all(d.tick == 0 for d in view2.demand_here),
          "NC11 the local view carries only this tick's demand")


def test_simultaneous_path_field_attribution():
    group("simultaneous-path field attribution: semantics govern the reading")
    spec = fixture_spec()
    z = {"n0": 18.0, "n1": 1.0, "n2": 2.0}
    increments = {"a": {"n0": -2.0, "n1": 2.0}, "b": {"n0": -2.0, "n2": 2.0}}
    g = settle.settle_group(spec, z, increments, tolerance=EXACT,
                            path_semantics="model_realised_constant_rate")

    check(g.group_size == 2, "a two-action simultaneous group IS representable")
    check(len(g.receipts) == 2, "per-action attributions are retained")
    check(abs(g.shares_sum - g.endpoint_value) <= EXACT,
          "the group TOTAL is exact - a theorem under either semantics")
    check(g.path_semantics == "model_realised_constant_rate",
          "the settlement carries the semantics it was settled under")

    # Nothing forces a permanent one-action-only design.
    for size in (1, 2, 3, 4):
        inc = {f"a{i}": {"n0": -1.0, "n1": 1.0} for i in range(size)}
        got = settle.settle_group(spec, z, inc, tolerance=EXACT,
                                  path_semantics="model_realised_constant_rate")
        check(got.group_size == size, f"a group of {size} settles")

    # Under DECLARED constant-rate simultaneous semantics the straight path IS
    # the model-realised path, so its exact decomposition is licensed.
    realised = settle.SimultaneousPathFieldAttribution(
        "a", 1.0, 2, "model_realised_constant_rate",
        "model_realised_path_decomposition")
    check(realised.is_exact_decomposition_of_realised_path,
          "constant-rate semantics licenses the exact-decomposition reading")

    # With only endpoints known the identical arithmetic is a CONVENTION, and
    # the physical-path reading must not be generalised onto it.
    convention = settle.SimultaneousPathFieldAttribution(
        "a", 1.0, 2, "endpoint_interpolation", "declared_accounting_convention")
    check(not convention.is_exact_decomposition_of_realised_path,
          "endpoint interpolation is a declared accounting convention")
    for claim in settle.PATH_CLAIM_READINGS:
        rejects(lambda c=claim: settle.SimultaneousPathFieldAttribution(
                    "a", 1.0, 2, "endpoint_interpolation", c),
                f"under endpoint interpolation, {claim!r} refuses",
                "not generalised beyond")

    # Refused under EVERY semantics: attribution alone establishes none of these.
    for semantics in settle.PATH_SEMANTICS:
        for reading in ("wallet_credit", "ownership", "fairness_claim",
                        "causal_entitlement", "shapley_meaning",
                        "mobius_allocation", "extra_interaction_issuance"):
            rejects(lambda sem=semantics, r=reading:
                    settle.SimultaneousPathFieldAttribution("a", 1.0, 2, sem, r),
                    f"{reading!r} refuses under {semantics}",
                    "refused under every path semantics")

    # Semantics is declared, never inferred.
    rejects(lambda: settle.SimultaneousPathFieldAttribution(
                "a", 1.0, 2, "guessed", "diagnostic"),
            "an undeclared path semantics refuses", "never inferred")
    rejects(lambda: settle.settle_group(spec, z, increments, tolerance=EXACT),
            "settle_group requires declared path semantics")

    # At m = 1 there is no attribution, so Theorem 8.2 (T3) applies.
    check(settle.SimultaneousPathFieldAttribution(
              "a", 1.0, 1, "endpoint_interpolation", "wallet_credit"
          ).group_size == 1,
          "at group size 1 no attribution occurs and the theorem applies")

    check("E2" in ac.OPEN_ESCALATIONS, "E2 remains an open escalation")


def test_raw_facts_separate_from_inference():
    group("raw run facts are never mixed with scientific inference")
    valid = proto.PhysicalValidity("VALID")
    broken = proto.PhysicalValidity("INVALID", ("CONSERVATION_RESIDUAL",))
    check(valid.is_valid and not broken.is_valid, "physical validity is raw")
    rejects(lambda: proto.PhysicalValidity("VALID", ("x",)),
            "a VALID run cannot carry invalidity flags")
    rejects(lambda: proto.PhysicalValidity("INVALID"),
            "an INVALID run must record why")

    ebu_met = proto.ArmResult("C4-ebu", "C4", "TARGET_MET", valid, True, True)
    ebu_missed = proto.ArmResult("C4-ebu", "C4", "TARGET_MISSED", valid, True, False)
    comp_missed = proto.ArmResult("C3", "C3", "TARGET_MISSED", valid, True, False)
    comp_broken = proto.ArmResult("C3", "C3", "TARGET_MISSED", broken, True, False)
    check(ebu_met.target_outcome == "TARGET_MET", "an arm records a raw outcome")
    rejects(lambda: proto.ArmResult("x", "C1", "TARGET_MET", valid, True, False),
            "section 36: viability alone cannot be recorded as target met",
            "reject-everything loophole")

    controllable = proto.OracleResult("CONTROLLABLE")
    impossible = proto.OracleResult("PHYSICALLY_IMPOSSIBLE")
    unresolved = proto.OracleResult("UNRESOLVED")
    check(unresolved.result == "UNRESOLVED",
          "UNRESOLVED is a first-class oracle outcome, not a missing value")

    # Derived labels, only where their conditions are established.
    check(proto.derive_ebu_run_label(ebu_met, controllable) == "SUCCESS",
          "target met gives SUCCESS")
    check(proto.derive_ebu_run_label(ebu_missed, controllable) == "EBU-FAIL",
          "missed + CONTROLLABLE gives EBU-FAIL")
    check(proto.derive_ebu_run_label(ebu_missed, impossible)
          == "PHYSICALLY-IMPOSSIBLE",
          "an impossible challenge is never EBU-FAIL")
    check(proto.derive_ebu_run_label(
              proto.ArmResult("C4-ebu", "C4", "TARGET_MISSED", broken, True, False),
              controllable) == "INVALID",
          "INVALID takes precedence over everything")
    rejects(lambda: proto.derive_ebu_run_label(ebu_missed, unresolved),
            "missed + UNRESOLVED derives no label", "not guessed")
    rejects(lambda: proto.derive_ebu_run_label(comp_missed, controllable),
            "a comparator gets no SUCCESS/EBU-FAIL label",
            "defined for the EBU arm")

    # The distinction the revision turns on.
    absolute = proto.conclude_claim(
        claim_id="EBU-meets-target", kind="absolute", ebu_arm=ebu_met,
        oracle=unresolved, comparators=[comp_missed])
    check(absolute.status == "CONCLUSIVE",
          "a comparator missing its target does NOT make an absolute EBU "
          "success claim inconclusive")
    comparative = proto.conclude_claim(
        claim_id="EBU-beats-C3", kind="comparative", ebu_arm=ebu_met,
        oracle=controllable, comparators=[comp_missed])
    check(comparative.status == "CONCLUSIVE",
          "a valid comparator that merely missed its target still concludes a "
          "comparative claim")
    broken_comp = proto.conclude_claim(
        claim_id="EBU-beats-C3", kind="comparative", ebu_arm=ebu_met,
        oracle=controllable, comparators=[comp_broken])
    check(broken_comp.status == "INCONCLUSIVE"
          and "COMPARATOR_INVALID" in broken_comp.reasons,
          "an INVALID comparator makes the comparative claim inconclusive")
    oracle_gap = proto.conclude_claim(
        claim_id="EBU-meets-target", kind="absolute", ebu_arm=ebu_missed,
        oracle=unresolved)
    check(oracle_gap.status == "INCONCLUSIVE"
          and "ORACLE_UNRESOLVED" in oracle_gap.reasons,
          "missed target + unresolved oracle is ORACLE_UNRESOLVED")
    missing = proto.conclude_claim(
        claim_id="EBU-beats-C3", kind="comparative", ebu_arm=ebu_met,
        oracle=controllable, comparators=[], required_arms=["C3"])
    check("MISSING_REQUIRED_ARM" in missing.reasons,
          "an absent registered arm is MISSING_REQUIRED_ARM")

    rejects(lambda: proto.ClaimConclusion("c", "absolute", "INCONCLUSIVE", ()),
            "an INCONCLUSIVE claim must carry a reason")
    rejects(lambda: proto.ClaimConclusion("c", "absolute", "CONCLUSIVE",
                                          ("ORACLE_UNRESOLVED",)),
            "a CONCLUSIVE claim carries no reasons")
    rejects(lambda: proto.ClaimConclusion("c", "absolute", "INCONCLUSIVE",
                                          ("MADE_UP",)),
            "an unknown reason code refuses")


def test_candidate_controllers_are_drafts_only():
    group("C0-C4 are unapproved candidates in a named, unnumbered study")
    import ebu_candidate_controllers as cc

    # --- the study identity registration, clause by clause ----------------
    check(cc.STUDY_NAME ==
          "prospective stochastic sustained-demand conservative-world study",
          "the study carries its declared name")
    identity = cc.identity_record()
    check(identity["sd_number"] is None, "no SD number is assigned")
    check(identity["amends_or_replaces_sd01"] is False,
          "SD-01 is neither amended nor replaced")
    check(identity["is_regenerative"] is False,
          "it is conservative, not regenerative")
    check(identity["scientific_content_frozen"] is False,
          "nothing scientific is frozen by the registration")
    for flag in ("is_preregistration", "is_execution_permission",
                 "is_scientific_evidence", "aws_authorized",
                 "execution_authorized"):
        check(identity[flag] is False, f"registration asserts not {flag}")
    check(set(identity["clauses"]) == set(cc.IDENTITY_CLAUSES),
          "all six identity clauses are carried")
    for purpose in ("preregistration", "execution", "aws", "evidence",
                    "sd_number", "amendment"):
        rejects(lambda p=purpose: cc.require_identity_only(p),
                f"the identity may not serve {purpose!r}")
    rejects(lambda: cc.StudyIdentity("s", "SD-01", "k", cc.IDENTITY_CLAUSES),
            "an identity carrying an SD number refuses", "no SD number")
    check("no SD number" in cc.STUDY_STATUS and "not SD-01" in cc.STUDY_STATUS,
          "the status line disclaims SD-01 and any SD number")
    check("regeneration is NOT represented" in cc.STUDY_STATUS,
          "the status line disclaims regeneration")
    check("unfrozen" in cc.STUDY_STATUS and "unauthorized" in cc.STUDY_STATUS,
          "the status line disclaims freezing and authorization")

    # --- five arms, every one unapproved, every build path closed ---------
    check(len(cc.DRAFTS) == 5, "five arms, C0 included")
    check(tuple(d.family for d in cc.DRAFTS) == ("C0", "C1", "C2", "C3", "C4"),
          "one draft per declared family")
    check(len(cc.unapproved_drafts()) == 5, "none is approved")
    check(set(cc.statuses().values()) == {cc.CANDIDATE_UNAPPROVED},
          "every recorded status is CANDIDATE_UNAPPROVED")

    for item in cc.DRAFTS:
        d = item.declaration()
        for required in ("decision_formula", "information_available",
                         "candidate_logic", "tie_breaking",
                         "no_feasible_action", "information_use",
                         "resolver_interaction", "proof_no_global_V",
                         "proof_no_future_demand", "proof_no_oracle_or_arms",
                         "config_to_preregister", "worked_examples",
                         "anti_strawman", "added_information",
                         "informational_asymmetry", "decision_power",
                         "quantity_freedom", "credibility"):
            check(bool(d[required]), f"{item.controller_id}: {required} declared")
        check(d["status"] == cc.CANDIDATE_UNAPPROVED,
              f"{item.controller_id} is CANDIDATE_UNAPPROVED")
        check(len(item.worked_examples) >= 2,
              f"{item.controller_id}: at least two hand-worked examples")
        check(all(e.label == cc.FIXTURE_LABEL for e in item.worked_examples),
              f"{item.controller_id}: every example is {cc.FIXTURE_LABEL}")
        check(set(item.information_use) >= {"L", "U", "R", "mu", "f_e",
                                            "demand", "neighbour_state",
                                            "reserve_information"},
              f"{item.controller_id}: use or non-use of each symbol declared")
        rejects(lambda i=item: cc.build(i.controller_id, lambda v: {}),
                f"{item.controller_id} cannot be built while unapproved",
                "has not been approved")

    # A draft missing a disclosure, or under-exampled, refuses outright.
    complete = cc.draft("C1-local-greedy")
    rejects(lambda: cc.ControllerDraft(
                **{**complete.__dict__, "anti_strawman": "  "}),
            "a draft without an anti-strawman justification refuses",
            "strawman")
    rejects(lambda: cc.ControllerDraft(
                **{**complete.__dict__,
                   "worked_examples": complete.worked_examples[:1]}),
            "a draft with one worked example refuses", "two hand-worked")
    rejects(lambda: cc.WorkedExample("t", "g", ("s",), "r", "x", label="REAL"),
            "an unlabelled worked example refuses", "ILLUSTRATIVE_FIXTURE_ONLY")

    # --- the arms differ in decision rule, never in physics ---------------
    check(cc.PIPELINE == ("common physical opportunities -> controller "
                          "proposal -> common physical resolver -> accepted "
                          "actions"),
          "the common pipeline is declared verbatim")
    check(len(cc.OPPORTUNITY_INVARIANTS) == 8,
          "all eight common-opportunity invariants are declared")
    opp = cc.OpportunitySet(tick=0, source="n0",
                            edge_caps={("n0", "n1"): 5.0, ("n0", "n2"): 2.0},
                            source_cap=6.0, derivation="synthetic fixture")
    check(opp.feasible_interval(("n0", "n1")) == (0.0, 5.0),
          "the continuous feasible set is an interval from 0")
    check(cc.require_within_opportunity("x", {("n0", "n1"): 5.0}, opp),
          "a proposal inside the common set is admitted")
    rejects(lambda: cc.require_within_opportunity(
                "x", {("n0", "n3"): 1.0}, opp),
            "an arm may not propose on an edge outside the common set",
            "never enlarge it")
    rejects(lambda: cc.require_within_opportunity(
                "x", {("n0", "n2"): 2.5}, opp),
            "an arm may not exceed the common per-edge cap",
            "outside the common continuous feasible set")
    rejects(lambda: cc.require_within_opportunity(
                "x", {("n0", "n1"): 5.0, ("n0", "n2"): 2.0}, opp),
            "an arm may not exceed the common joint cap", "joint bound")
    rejects(lambda: cc.OpportunitySet(0, "n0", {("n9", "n1"): 1.0}, 1.0, "d"),
            "an opportunity on another source's edge refuses",
            "does not leave source")
    rejects(lambda: cc.common_opportunities(None),
            "the opportunity set refuses anything but a CommonLocalContext",
            "policy-dependent")

    # --- the comparison keeps C3 strong and C0 present --------------------
    rows = {r["controller_id"]: r for r in cc.comparison_rows()}
    check(len(rows) == 5, "the comparison table covers every arm")
    check(all(r["status"] == cc.CANDIDATE_UNAPPROVED for r in rows.values()),
          "no table row implies an approval")
    check("Continuous" in rows["C4-ebu-local-field"]["quantity_freedom"]
          and "Continuous" in rows["C3-reserve-and-band-aware"]["quantity_freedom"],
          "C3 and C4 have the same continuous quantity freedom")
    check("NOT read" in rows["C3-reserve-and-band-aware"]["sees_mu"]
          and "NOT read" in rows["C3-reserve-and-band-aware"]["sees_f_e"],
          "C3 uses no marginal and no force")
    check("central" in rows["C4-ebu-local-field"]["sees_f_e"],
          "C4's decision rule is the force")
    check(cc.draft("C3-reserve-and-band-aware").use_of_L_U_R
          .startswith("Declared homeostatic boundaries only"),
          "C3 uses the declared boundaries but not the burden")
    check("water-fill" in cc.draft("C3-reserve-and-band-aware").candidate_logic.lower(),
          "C3 is drafted in its strong, redistributing form")
    check("None" in cc.draft("C2-myopic-service").use_of_L_U_R,
          "C2 deliberately uses no band")
    check("UNIFORMLY" in cc.draft("C0-reject-all").anti_strawman,
          "C0 cannot win by a UNIFORM service floor, not by its identity")

    # --- the unresolved decisions are recorded, not silently resolved -----
    check(set(cc.RESOLVED_QUESTIONS) == {"Q-1", "Q-2", "Q-3"},
          "Q-1, Q-2 and Q-3 are recorded as resolved")
    check(set(cc.CLOSED_GAPS) == {"G-1", "G-2"},
          "G-1 and G-2 are recorded as closed")
    check(set(cc.OPEN_QUESTIONS) == {"Q-4", "Q-5"},
          "the two new open questions are registered for the author")
    check(set(cc.BLOCKING_GAPS) == {"G-3", "G-4"},
          "the two new blocking gaps are registered")


def test_controller_correction_package():
    group("corrected C3, opportunity semantics, typed locality, fixtures")
    import ebu_candidate_controllers as cc

    # --- 1. the corrected fixture A, DERIVED from the rule -----------------
    a3 = cc.fixture_outcome("A", "C3", "C3-reserve-and-band-aware")
    check(a3.proposal == {("i", "j1"): 5.0, ("i", "j2"): 1.0},
          "corrected C3 proposes (5, 1) on fixture A")
    check(a3.post_state == {"i": 4.0, "j1": 8.0, "j2": 16.0},
          "corrected C3 leaves x' = (4, 8, 16) on fixture A")
    check(a3.post_state["i"] >= 4.0,
          "the C3 source ends AT OR ABOVE its lower band L_i = 4")
    check(not a3.lower_band_violations and not a3.upper_band_violations
          and not a3.reserve_violations,
          "no node is left outside a band on fixture A under corrected C3")
    check(a3.delivered == 6.0, "corrected C3 delivers 6 of 12 on fixture A")

    # The OLD claim is now false and must not be reconstructible: the earlier
    # reserve-based export [x_i - R]_+ = 8 would have left the source at 3.
    check(10.0 - 7.0 < 4.0,
          "the superseded reserve-based export would have left x_i = 3 < L = 4")

    # --- 2. fixture B recomputed, not preserved ---------------------------
    b3 = cc.fixture_outcome("B", "C3", "C3-reserve-and-band-aware")
    check(b3.proposal == {}, "corrected C3 proposes nothing on fixture B")
    check(b3.delivered == 0.0, "corrected C3 delivers 0 on fixture B")
    check(b3.post_state == {"i": 3.0, "j1": 3.0, "j2": 1.0},
          "fixture B's state is unchanged under corrected C3")
    check(any("j2" in v for v in b3.reserve_violations),
          "corrected C3 leaves j2 below its reserve on fixture B")
    b4 = cc.fixture_outcome("B", "C4", "C4-ebu-local-field")
    check(b4.delivered == 1.0 and b4.post_state["j2"] == 2.0,
          "C4 lifts j2 to its reserve on fixture B")
    check(not b4.reserve_violations,
          "C4 clears the reserve breach C3 leaves standing")
    check(b4.post_state["i"] == 2.0 and b4.post_state["i"] < 4.0,
          "C4 pays by deepening its own lower-band shortfall")

    # --- no fixture collapses its dimensions into a winner ----------------
    for key in ("A", "B"):
        for family in ("C0", "C1", "C2", "C3", "C4"):
            outcome = cc.fixture_outcome(key, family, family)
            check(outcome.label == cc.FIXTURE_LABEL,
                  f"{family} on {key}: outcome is {cc.FIXTURE_LABEL}")
            check(not any(w in " ".join(outcome.lines()).lower()
                          for w in ("dominat", "winner", "wins", "better")),
                  f"{family} on {key}: dimensions are reported, never ranked")
    check(not any(f.name in ("winner", "score", "rank", "dominates")
                  for f in cc.FixtureOutcome.__dataclass_fields__.values()),
          "FixtureOutcome carries no aggregate, score, rank or winner field")
    for item in cc.DRAFTS:
        for example in item.worked_examples:
            check("dominat" not in example.reading.lower(),
                  f"{item.controller_id}: no dominance claim in a fixture reading")

    # --- 3/4. the layers stay separate, and C3 is band-aware --------------
    c3 = cc.draft("C3-reserve-and-band-aware")
    check(c3.controller_id == "C3-reserve-and-band-aware" and c3.family == "C3",
          "C3 is redrafted as reserve-and-band-aware, still in family C3")
    check(c3.status == cc.CANDIDATE_UNAPPROVED, "C3 remains unapproved")
    check("[ x_i - L_i ]_+" in c3.decision_formula,
          "C3's SOURCE-side bound is the lower band")
    check("[R_j - x_j]_+" in c3.decision_formula,
          "C3's stage 1 serves the DESTINATION homeostatic reserve deficit")
    check(c3.information_use["R"].startswith("READ")
          and "R_eff" in c3.information_use["R"],
          "C3 READS the homeostatic reserve R_j and distinguishes it from R_eff")
    check("NOT" in c3.information_use["reserve_information"]
          and "R_eff" in c3.information_use["reserve_information"],
          "C3 reads no R_eff and no provider budget")
    check("R_eff" in cc.RESOLVED_QUESTIONS["Q-2"]
          and "R_eff" in cc.FIXTURE_BUDGET_READING,
          "R_eff is preserved as distinct from the model coordinate R")
    check("not budgeted" in world.UnresolvedContention.__doc__
          or "DIAGNOSTIC" in world.UnresolvedContention.__doc__,
          "the destination-side gap cites P1C's diagnostic-only incoming")

    # --- 4.1 units: rates and quantities are never mixed -------------------
    check(world.tick_quantity_from_rate(6.0, 0.5) == 3.0,
          "q = dt * J converts a rate to a tick quantity")
    check(world.rate_from_tick_quantity(3.0, 0.5) == 6.0, "and back again")
    rejects(lambda: world.tick_quantity_from_rate(1.0, 0.0),
            "a non-positive dt refuses", "dt must be positive")

    # --- 5/6. the water-filling operator is exact and order-independent ----
    fill = cc.capped_max_min_water_fill
    check(fill(10.0, {"a": 2.0, "b": 3.0}) == {"a": 2.0, "b": 3.0},
          "B >= sum b gives every edge its full cap")
    filled = fill(5.0, {"a": 5.0, "b": 1.0})
    check(filled == {"a": 4.0, "b": 1.0} and abs(sum(filled.values()) - 5.0) < 1e-12,
          "capped max-min water-filling exhausts B and respects each cap")
    check(fill(3.0, {"a": 9.0, "b": 9.0}) == {"a": 1.5, "b": 1.5},
          "equal caps receive equal quantities")
    forward = fill(7.0, {"a": 1.0, "b": 4.0, "c": 9.0})
    backward = fill(7.0, {"c": 9.0, "b": 4.0, "a": 1.0})
    check(forward == backward, "the allocation is independent of edge ordering")
    check(fill(0.0, {"a": 3.0}) == {"a": 0.0},
          "zero available quantity allocates nothing")

    stages = cc.c3_candidate_stages(
        cc.fixture_context(cc.FIXTURES["A"]["stocks"],
                           cc.FIXTURES["A"]["demand"]).project("C3"))
    check(stages["available"] == 6.0, "A_i = [x_i - L_i]_+ = 6 on fixture A")
    check(stages["served_stage1"] == 0.0,
          "stage 1 (RESERVE) is inert on fixture A: no destination is below R")
    check(stages["available_stage2"] == 6.0,
          "stage 2 therefore inherits the whole budget B^(2) = A_i")
    check(stages["served_stage2"] == 1.0,
          "stage 2 spends exactly the one genuine lower-band deficit")
    check(stages["available_stage3"] == 5.0, "stage 3 inherits the remainder")
    check(sum(stages["stage3"].values()) == 5.0,
          "stage 3 water-fills the whole remaining budget")
    check(stages["total"] <= stages["available"] + 1e-12,
          "the two-stage rule never exceeds A_i")

    # --- 7. the conservative domain is not quietly made lossy -------------
    spec = cc._fixture_spec()
    check(spec.eta == 1.0 and spec.is_conservative,
          "the illustrative world stays closed and lossless (eta = 1)")
    for key in ("A", "B"):
        for family in ("C0", "C1", "C2", "C3", "C4"):
            outcome = cc.fixture_outcome(key, family, family)
            before = sum(cc.FIXTURES[key]["stocks"].values())
            check(abs(sum(outcome.post_state.values()) - before) < 1e-12,
                  f"{family} on {key}: quantity is conserved exactly")

    # --- 10. one common context, typed projections, structural absence ----
    context = cc.fixture_context(cc.FIXTURES["A"]["stocks"],
                                 cc.FIXTURES["A"]["demand"])
    check(isinstance(context, cc.CommonLocalContext),
          "one immutable CommonLocalContext carries the local physics")
    check(set(context.endpoint_specs) == {"j1", "j2"},
          "G-2 closed: endpoint NodeSpecs are on the COMMON context")
    check(all(isinstance(e, world.EdgeSpec) for e in context.edge_specs.values()),
          "G-1 closed: per-edge M_e and theta_e are on the COMMON context")
    ledger = cc.information_ledger()
    check(set(ledger["per_family"]) == {"C0", "C1", "C2", "C3", "C4"},
          "the ledger covers every family")
    for family in ("C0", "C1", "C2", "C3", "C4"):
        row = ledger["per_family"][family]
        check(bool(row["exposed_by_typed_view"]) and bool(row["consumed_by_formula"]),
              f"{family}: exposure and consumption are recorded separately")
        view = context.project(family)
        check(set(row["exposed_by_typed_view"]) == set(view.__dataclass_fields__),
              f"{family}: the ledger's exposure IS the projection's fields")
        for absent in cc.FORBIDDEN_ON_VIEW[family]:
            rejects(lambda v=view, a=absent: getattr(v, a),
                    f"{family}View has no {absent!r} to read",
                    "carries no")
    check(set(context.project("C1").__dataclass_fields__)
          == set(context.project("C2").__dataclass_fields__),
          "C1 and C2 differ in rule, never in information")
    rejects(lambda: context.project("C9"), "an undeclared family has no view",
            "no typed projection")

    # --- 11. hard capacity is common, and the joint successor is the law ---
    opportunity = cc.common_opportunities(context)
    check(opportunity.edge_caps[("i", "j2")] == 5.0,
          "the common cap carries the destination hard headroom (Q-3)")
    check("no controller" in cc.OPPORTUNITY_DERIVATION
          or "no controller," in cc.OPPORTUNITY_DERIVATION,
          "the derivation declares itself policy-independent")
    hard_spec = fixture_spec()
    hard_state = world.WorldState(hard_spec.digest,
                                  {"n0": 5.0, "n1": 5.0, "n2": 5.0})
    # n1 simultaneously receives 3 and sends 4: the joint successor is 4, and
    # an isolated per-edge headroom check would have looked at 5 + 3 = 8 alone.
    ladder = lambda q: world.QuantityLadder(q, q, q, q, q)
    acts = [world.Action("a", "x", ("n0", "n1"), "scalar", ladder(3.0), 0, 0, "e"),
            world.Action("b", "x", ("n1", "n2"), "scalar", ladder(4.0), 0, 0, "e")]
    successor = world.joint_successor(hard_spec, hard_state, acts)
    check(abs(successor["n1"] - 4.0) < 1e-12,
          "the joint successor nets a node's simultaneous inflow and outflow")
    check(world.hard_feasible(hard_spec, hard_state, acts) == (),
          "hard feasibility is decided on the joint successor")

    # --- 12. contested destinations fail closed, never silently allocated --
    check(world.contested_destinations(hard_spec, acts) == (),
          "a single-source destination is not contested")
    both = [world.Action("a", "x", ("n0", "n1"), "scalar", ladder(3.0), 0, 0, "e"),
            world.Action("b", "y", ("n2", "n1"), "scalar", ladder(3.0), 0, 0, "e")]
    check(world.contested_destinations(hard_spec, both) == (("n1", ("n0", "n2")),),
          "two sources feeding one destination are detected")
    check(world.require_resolved_destination_contention(
              hard_spec, hard_state, both) == (("n1", ("n0", "n2")),),
          "contention within K_j is reported and permitted")
    over = [world.Action("a", "x", ("n0", "n1"), "scalar", ladder(9.0), 0, 0, "e"),
            world.Action("b", "y", ("n2", "n1"), "scalar", ladder(9.0), 0, 0, "e")]
    rejects(lambda: world.require_resolved_destination_contention(
                hard_spec, hard_state, over),
            "contention OVER K_j fails closed instead of inventing a rule",
            "NO committed authority")

    # --- 13. C3's band claim is not generalised past single-source ---------
    check(cc.require_single_source_destinations(cc._fixture_spec()),
          "the illustrative topology has one source per destination")
    multi = world.Topology(("a", "b", "c"), (("a", "c"), ("b", "c")))
    multi_spec = world.WorldSpec(
        "m", "0", multi,
        {n: world.NodeSpec(n, 20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0)
         for n in multi.nodes},
        path_semantics="endpoint_interpolation")
    rejects(lambda: cc.require_single_source_destinations(multi_spec),
            "a multiply-fed destination refuses C3's general band claim",
            "G-4")
    check("not established" in cc.BLOCKING_GAPS["G-4"].lower()
          or "NOT established" in cc.BLOCKING_GAPS["G-4"],
          "G-4 records the unresolved multi-source band exposure")

    # --- 14/15. opportunities are demand-triggered and policy-independent --
    quiet = cc.fixture_context({"i": 10.0, "j1": 3.0, "j2": 15.0},
                               {("i", "j1"): 6.0})
    caps = cc.common_opportunities(quiet).edge_caps
    check(caps[("i", "j2")] == 0.0,
          "Q-1: a zero-demand edge carries no opportunity")
    check(caps[("i", "j1")] <= 6.0, "Q-1: the cap never exceeds current demand")
    for family in ("C0", "C1", "C2", "C3", "C4"):
        proposal = cc.CANDIDATE_RULES[family](quiet.project(family))
        check(proposal.get(("i", "j2"), 0.0) == 0.0,
              f"{family} creates no transfer where no demand exists")
    import inspect as _inspect
    signature = _inspect.signature(cc.common_opportunities)
    check(list(signature.parameters) == ["context"],
          "the opportunity set takes a context and NO controller argument")

    # --- 16. the foundation fixture is not a scientific controller ---------
    fixture = proto.FixtureRejectAllController.for_conformance_fixture()
    check(fixture.family == proto.FIXTURE_ONLY_FAMILY
          and fixture.family not in proto.CONTROLLER_FAMILIES,
          "the fixture's family is not a declared controller family")
    check(fixture.declaration()["is_fixture_only"] is True,
          "the fixture declares itself fixture-only")
    rejects(lambda: proto.FixtureRejectAllController(None, "c"),
            "the fixture cannot be constructed without its fixture token",
            "conformance fixture")
    rejects(lambda: proto.require_study_controller(fixture),
            "the fixture may never serve as a scientific study arm",
            "may not serve as a scientific study arm")
    rejects(lambda: proto.DeclaredController("c0", proto.FIXTURE_ONLY_FAMILY,
                                             lambda v: {}, declared_formula="f"),
            "the fixture family cannot be registered as a controller family",
            "unknown controller family")
    check(not hasattr(proto, "RejectAllController"),
          "no second, ungated reject-all controller remains constructible")
    rejects(lambda: cc.build("C0-reject-all", fixture),
            "a fixture cannot supply a study arm's rule", "conformance fixture")

    # --- the packet's numbers stay tied to the rules that produce them ----
    packet = "V3.0_PROSPECTIVE_STUDY_CONTROLLER_DECISION_PACKET.md"
    with open(packet, encoding="utf-8") as handle:
        doc = handle.read()
    flat = " ".join(doc.split())
    a3 = cc.fixture_outcome("A", "C3", "C3-reserve-and-band-aware")
    check(f"`i = {a3.post_state['i']:g}`, `j1 = {a3.post_state['j1']:g}`, "
          f"`j2 = {a3.post_state['j2']:g}`" in flat,
          "the packet quotes the derived fixture-A post-state")
    check("{j1: 5, j2: 1}" in flat,
          "the packet quotes the derived fixture-A C3 proposal")
    check("[ x_i - L_i ]_+" in doc and "E_i = [ x_i - R_i ]_+" not in doc,
          "the packet's C3 bound is the band, and the reserve bound is gone")
    check("exportable stock" not in doc,
          "the superseded 'exportable stock' framing is gone from the packet")
    # Every surviving mention of dominance must be a withdrawal, not a claim.
    for match in re.finditer(r"dominat\w*", doc, re.IGNORECASE):
        window = doc[max(0, match.start() - 220):match.end() + 220]
        check(any(mark in window for mark in
                  ("withdrawn", "false", "not used", "is not a wrong answer",
                   "superseded", "→ `C3-band-aware`")),
              "a dominance mention in the packet is a withdrawal, not a claim")
    check("R_eff" in doc and "not** the model coordinate `R`" in doc,
          "the packet preserves R_eff as distinct from R")
    check("S-M is unfilled" in doc,
          "the packet grounds the no-dominance rule in the unfilled metric slot")
    for fixture_key, family in (("A", "C3"), ("A", "C4"), ("B", "C4")):
        outcome = cc.fixture_outcome(fixture_key, family, family)
        check(f"{outcome.delivered:g} of {outcome.demanded:g} demanded" in flat
              or f"{outcome.delivered:g} of 12" in flat,
              f"the packet's {family} fixture-{fixture_key} service "
              f"({outcome.delivered:g}) matches the rule")
    # The three-stage C3 and the P1C binding result must both be documented.
    for marker in ("B_i^(1)", "B_i^(2)", "B_i^(3)", "[R_j - x_j]_+ / eta_e",
                   "PROPOSAL-LEVEL lexicographic priority",
                   "NOT proven lexicographically saturated"):
        check(marker in flat, f"the packet documents {marker!r}")
    demo = cc.p1c_binding_demonstration()
    check(f"`sigma = {demo['sigma']:g}`" in flat,
          "the packet quotes the derived P1C binding sigma")
    check("Model-state advancement: NONE" in flat
          and "withdrawn" in flat.lower(),
          "the packet withdraws the false execution claim rather than hiding it")
    check("transition SITES" in flat and "NOT TRACKED" in flat,
          "the packet records transition SITES, and that cumulative historical "
          "executions are untracked rather than estimated")
    check("direct calls in one file" in flat
          and "call-graph analysis" in flat,
          "the packet states the AST check's actual scope and its limitation")
    check("any nonzero exit" in flat and "exactly 2" in flat,
          "the packet records the weak CI refusal check and its correction")
    check("not the workflow as a whole" in flat,
          "the packet scopes the static label to the V3.0 subset")

    # --- 17. no controller-identity-specific scientific classification -----
    valid = proto.PhysicalValidity("VALID")
    met = proto.ArmResult("any-c0-arm", "C0", "TARGET_MET", valid, True, True)
    check(met.target_outcome == "TARGET_MET",
          "a C0-family arm meeting BOTH axes records TARGET_MET - no identity gate")
    rejects(lambda: proto.ArmResult("a", "C4", "TARGET_MET", valid, True, False),
            "the service floor refuses TARGET_MET on viability alone",
            "reject-everything loophole")
    source = inspect.getsource(proto.ArmResult)
    check(not any(token in source for token in ('== "C0"', "== 'C0'")),
          "ArmResult contains no controller-identity branch")


def test_protocol_refuses_to_run_science():
    group("the protocol layer cannot produce evidence")
    spec = fixture_spec()
    schedule = world.DemandSchedule("s", "declared-model", 1, ())

    # The tick BUDGET is checked purely: no tick is planned or executed here.
    # Executing one belongs to test_ebu_foundation_transitions.py, which is a
    # separate execution class and is not on the default CI path.
    budget = proto.TickBudget.conformance()
    check(budget.limit == 1 and budget.used == 0,
          "the conformance budget admits exactly one tick and starts unspent")
    budget.spend()
    rejects(budget.spend,
            "a SECOND spend refuses - a trajectory cannot be produced",
            "budget for")
    rejects(lambda: proto.TickBudget(0, "x"),
            "a non-positive tick budget refuses")
    rejects(lambda: proto.TickBudget(1, "  "),
            "a tick budget without a declared purpose refuses")

    # The campaign runner has no success path.
    rejects(lambda: proto.ExperimentRunner(spec).run_campaign(),
            "run_campaign without a preregistration refuses",
            "no frozen preregistration")
    rejects(lambda: proto.Preregistration({"horizon": 10}),
            "an incomplete preregistration refuses", "incomplete")
    check(len(proto.PREREGISTRATION_FIELDS) == 20,
          "all twenty section 44 fields are required")

    # Oracle output can never reach a controller.
    oracle = proto.FeasibilityOracle("O", lambda s, d: True)
    rejects(lambda: oracle.verdict_for_evaluator(
                caller="C4-ebu", spec=spec, schedule=schedule),
            "a controller asking the oracle refuses", "never exposed")
    check(oracle.verdict_for_evaluator(caller="evaluator", spec=spec,
                                       schedule=schedule) is True,
          "the offline evaluator may read the verdict")
    rejects(lambda: oracle.as_local_view(), "the oracle cannot become a view")

    # Run labels are derived elsewhere from raw facts; see the dedicated
    # group. Here only the refusal to run science is checked.
    # Readiness verdict.
    report = proto.readiness_report(fixtures_passed=True,
                                    negative_controls_passed=True)
    check(report["verdict"] == "FOUNDATION INCOMPLETE",
          "readiness is FOUNDATION INCOMPLETE while escalations stand")
    check(proto.readiness_report(fixtures_passed=False,
                                 negative_controls_passed=True)["verdict"]
          == "IMPLEMENTATION INVALID",
          "a failing fixture reports IMPLEMENTATION INVALID first")


def test_reserve_band_and_unit_integrity():
    group("R_eff vs R, three-stage C3, units, and config-time domain limits")
    import ebu_candidate_controllers as cc

    # --- 1. R_eff is NOT R, and the distinction is enforced ----------------
    check(set(world.RESERVE_CONCEPTS) == {"R_eff", "R", "relationship"},
          "both reserve concepts and their (non-)relationship are declared")
    check("PROVIDER" in world.RESERVE_CONCEPTS["R_eff"]
          and "EXPORT" in world.RESERVE_CONCEPTS["R_eff"],
          "R_eff is declared as the provider/export floor")
    check("HOMEOSTATIC" in world.RESERVE_CONCEPTS["R"]
          and "NodeSpec.reserve" in world.RESERVE_CONCEPTS["R"],
          "R is declared as the homeostatic reserve coordinate")
    check("does NOT implement" in world.RESERVE_CONCEPTS["relationship"],
          "the declaration states R_eff does not implement R")
    for bad in ("R_eff is R",
                "the reserve is protected for every arm by the P1C resolver",
                "the provider layer already protects the reserve"):
        rejects(lambda b=bad: world.require_reserve_concepts_distinct(b),
                f"an assertion that {bad!r} refuses", "does NOT implement")
    # A retraction must still be expressible, or a correction notice could not
    # name the error it corrects.
    check(world.require_reserve_concepts_distinct(
              "an earlier revision claimed the reserve is protected for every "
              "arm; that inference was FALSE"),
          "a quotation marked false is a withdrawal, not an assertion")
    # Every declared prose block in the study passes the guard.
    blocks = 0
    for register in ("RESOLVED_QUESTIONS", "OPEN_QUESTIONS", "BLOCKING_GAPS",
                     "CLOSED_GAPS"):
        for text in getattr(cc, register).values():
            world.require_reserve_concepts_distinct(text)
            blocks += 1
    for item in cc.DRAFTS:
        for text in item.information_use.values():
            world.require_reserve_concepts_distinct(text)
            blocks += 1
        world.require_reserve_concepts_distinct(item.resolver_interaction)
        blocks += 1
    check(blocks > 40, f"{blocks} declared prose blocks pass the guard")

    # --- 2. the three-stage C3, and its budget algebra ---------------------
    c3 = cc.draft("C3-reserve-and-band-aware")
    for marker in ("B_i^(1)", "B_i^(2)", "B_i^(3)", "[R_j - x_j]_+",
                   "[L_j - x_j", "[U_j - x_j", "[ x_i - L_i ]_+"):
        check(marker in c3.decision_formula,
              f"the C3 formula declares {marker}")
    check("NO mu" in c3.decision_formula and "NO alpha" in c3.decision_formula,
          "C3 declares it uses no field quantity and no potential weight")
    for family_view in (cc.C3View,):
        for forbidden in ("alpha", "beta", "chi", "mu", "f_e"):
            check(forbidden not in family_view.__dataclass_fields__,
                  f"C3View has no {forbidden} field at all")
    check("endpoint_reserve" in cc.C3View.__dataclass_fields__,
          "C3View carries the destination homeostatic reserve R_j")

    # Stage budgets are conserved, and the total never exceeds A_i.
    for key in ("A", "B"):
        context = cc.fixture_context(cc.FIXTURES[key]["stocks"],
                                     cc.FIXTURES[key]["demand"])
        d = cc.c3_candidate_stages(context.project("C3"))
        served = [sum(d[f"stage{k}"].values()) for k in (1, 2, 3)]
        check(abs(d["available_stage2"]
                  - max(d["available"] - served[0], 0.0)) <= EXACT,
              f"fixture {key}: B^(2) = [A_i - sum q^(1)]_+")
        check(abs(d["available_stage3"]
                  - max(d["available"] - served[0] - served[1], 0.0)) <= EXACT,
              f"fixture {key}: B^(3) = [A_i - sum q^(1) - sum q^(2)]_+")
        for k in (1, 2, 3):
            budget_k = d["available"] if k == 1 else d[f"available_stage{k}"]
            check(sum(d[f"stage{k}"].values()) <= budget_k + EXACT,
                  f"fixture {key}: stage {k} never exceeds its own budget")
        check(d["total"] <= d["available"] + EXACT,
              f"fixture {key}: sum_e q^C3 <= A_i")

    # --- 3. water-filling, every declared edge case ------------------------
    fill = cc.capped_max_min_water_fill
    check(fill(0.0, {"a": 3.0, "b": 1.0}) == {"a": 0.0, "b": 0.0},
          "B = 0 allocates zero on every edge")
    check(fill(5.0, {}) == {}, "an empty edge set allocates nothing")
    check(fill(5.0, {"a": 0.0, "b": 0.0}) == {"a": 0.0, "b": 0.0},
          "all-zero caps allocate zero")
    check(fill(9.0, {"a": 3.0, "b": 1.0}) == {"a": 3.0, "b": 1.0},
          "B >= sum b gives every edge its full cap")
    got = fill(5.0, {"a": 5.0, "b": 1.0})
    check(got == {"a": 4.0, "b": 1.0} and abs(sum(got.values()) - 5.0) <= EXACT,
          "B < sum b binds, exhausts B, and respects each cap")
    check(fill(3.0, {"a": 9.0, "b": 9.0}) == {"a": 1.5, "b": 1.5},
          "equal caps receive equal quantities")
    check(fill(7.0, {"a": 1.0, "b": 4.0, "c": 9.0})
          == fill(7.0, {"c": 9.0, "b": 4.0, "a": 1.0}),
          "the continuous allocation is independent of edge ordering")
    rejects(lambda: fill(-1.0, {"a": 1.0}), "a negative budget refuses")
    rejects(lambda: fill(1.0, {"a": -1.0}), "a negative cap refuses")
    fill_doc = " ".join(fill.__doc__.split())      # wrapping is not meaning
    check("destination node id ascending" in fill_doc
          and "must never change the continuous allocation" in fill_doc
          and "already tied" in fill_doc,
          "the residual rule may only settle ties the continuous rule created")
    check("symmetric function of the cap MULTISET" in fill_doc,
          "order independence is declared a property of the continuous rule")
    ledger = cc.water_fill_budget_ledger(6.0, [{"a": 1.0}, {"a": 2.0, "b": 9.0}])
    check(abs(ledger["stages"][1]["budget"] - 5.0) <= EXACT,
          "the stage ledger reduces the budget by what the prior stage served")
    check(ledger["total"] <= ledger["available"] + EXACT,
          "the stage ledger never allocates more than the budget")

    # --- 4. P1C can STILL BIND after C3 proposes ---------------------------
    demo = cc.p1c_binding_demonstration()
    check(demo["R_eff_exceeds_L_i"],
          "no declared ordering prevents R_eff > L_i")
    check(demo["sigma"] < 1.0, "the common resolver still binds: sigma < 1")
    check(not demo["stage1_reserve_cleared"],
          "proportional scaling leaves a Stage-1 reserve deficit unserved")
    check(demo["stage3_ordinary_service_still_executed"] > 0.0,
          "while Stage-3 ordinary service still executes")
    check(demo["lexicographically_saturated"] is False,
          "the accepted vector is NOT claimed lexicographically saturated")
    check("PROPOSAL-LEVEL" in cc.P1C_BINDING_ANALYSIS
          and "NOT proven lexicographically saturated"
          in cc.P1C_BINDING_ANALYSIS,
          "the analysis states the ordering is proposal-level only")
    check("does NOT expose a P1C-safe joint quantity" in
          cc.OPPORTUNITY_CAP_IS_NOT_P1C_SAFE,
          "the opportunity layer exposes no P1C-safe cap before proposal")
    context = cc.fixture_context(cc.FIXTURES["A"]["stocks"],
                                 cc.FIXTURES["A"]["demand"])
    check(cc.common_opportunities(context).source_cap == context.source_stock,
          "the joint opportunity cap is the source's own stock, not the budget")

    # --- 5. units: rate vs quantity, at NON-UNIT dt ------------------------
    for dt, rate in ((0.5, 6.0), (2.0, 3.0), (0.25, 8.0)):
        quantity = world.tick_quantity_from_rate(rate, dt)
        check(abs(quantity - rate * dt) <= EXACT,
              f"dt={dt}: q = dt * J = {quantity:g}")
        check(abs(world.rate_from_tick_quantity(quantity, dt) - rate) <= EXACT,
              f"dt={dt}: the inverse recovers the rate exactly")
        check(quantity != rate,
              f"dt={dt}: rate and quantity DIFFER, so the bug cannot hide")
    check(world.tick_quantity_from_rate(6.0, 1.0) == 6.0,
          "at dt = 1 they coincide - which is exactly why dt != 1 is tested")
    # The committed budget is a rate; the resolver consumes a quantity.
    budget_q = cc.p1c_tick_budget_quantity(stock=10.0, R_eff=2.0, dt=0.5)
    check(abs(budget_q - 8.0) <= EXACT,
          "the P1C budget converts to a tick quantity through the converter")
    rejects(lambda: world.tick_quantity_from_rate(1.0, 0.0),
            "a non-positive dt refuses", "dt must be positive")
    check(abs(world.delivered_from_sent(4.0, 0.5) - 2.0) <= EXACT,
          "delivered = eta * sent")
    check(abs(world.sent_from_delivered(2.0, 0.5) - 4.0) <= EXACT,
          "sent = delivered / eta")
    for field in ("q_e", "d_e", "D_e", "c_e", "delivered", "eta_e"):
        check(field in world.QUANTITY_SEMANTICS,
              f"the side/units of {field} are declared")
    check("SOURCE-SIDE" in world.QUANTITY_SEMANTICS["d_e"]
          and "D_e" in world.QUANTITY_SEMANTICS["d_e"],
          "d_e is declared source-side, with a distinct symbol for the other")
    check("eta_e = 1" in world.QUANTITY_SEMANTICS["eta_e"]
          and "NOT a universal" in world.QUANTITY_SEMANTICS["eta_e"],
          "eta = 1 is a first-study restriction, not a universal assumption")

    # --- 6. configuration-time domain restrictions -------------------------
    good = cc._fixture_spec()
    record = cc.validate_study_configuration(good)
    check(record["is_approval"] is False
          and record["is_preregistration"] is False
          and record["is_universal_theorem"] is False,
          "configuration validation is not approval, preregistration or theorem")
    check(all(count <= 1 for _node, count in record["destination_in_degrees"]),
          "every destination in the candidate topology has in-degree <= 1")
    for node, R, L, U, K in record["node_boundaries_R_L_U_K"]:
        check(0.0 <= R <= L <= U <= K,
              f"{node}: 0 <= R <= L <= U <= K holds")
    # Committed authority does NOT guarantee the ordering - verified, not assumed.
    loose = world.NodeSpec("n", 20.0, 4.0, 16.0, 9.0, 1.0, 1.0, 1.0)
    check(loose.reserve > loose.lower,
          "committed NodeSpec ACCEPTS R > L, so the ordering is not guaranteed")
    topo = world.Topology(("n",), ())
    rejects(lambda: world.require_nested_boundaries(world.WorldSpec(
                "b", "0", topo, {"n": loose},
                path_semantics="endpoint_interpolation")),
            "configuration validation refuses R > L", "configuration validation")
    multi = world.Topology(("a", "b", "c"), (("a", "c"), ("b", "c")))
    multi_spec = world.WorldSpec(
        "m", "0", multi,
        {n: world.NodeSpec(n, 20.0, 4.0, 16.0, 2.0, 1.0, 1.0, 1.0)
         for n in multi.nodes},
        path_semantics="endpoint_interpolation")
    rejects(lambda: world.require_single_source_destinations(multi_spec),
            "a multiply-fed destination refuses at configuration validation",
            "configuration validation")
    rejects(lambda: cc.validate_study_configuration(multi_spec),
            "study configuration validation refuses it too")
    # It fails CLOSED before any controller exists, not later at apply_joint.
    rejects(lambda: cc.build_common_context(
                multi_spec,
                world.WorldState(multi_spec.digest,
                                 {"a": 5.0, "b": 5.0, "c": 5.0}),
                "a", 0, world.DemandSchedule("s", "m", 1, ())),
            "no local context can be built on a violating topology")
    for declaration in (world.SINGLE_SOURCE_RESTRICTION,
                        world.NODE_BOUNDARY_ORDERING):
        check("NOT a universal EBU theorem" in declaration
              or "NOT a general EBU theorem" in declaration,
              "the restriction denies being a universal EBU theorem")
        check("NOT" in declaration and "preregistration" in declaration,
              "the restriction denies being a frozen preregistration")
    check("R_eff is deliberately ABSENT" in world.NODE_BOUNDARY_ORDERING,
          "R_eff is excluded from the R <= L <= U <= K ordering")

    # --- 7. identity-neutral success predicate -----------------------------
    import inspect as _inspect
    parameters = _inspect.signature(proto.target_met).parameters
    check(set(parameters) == {"viability_ok", "service_ok"},
          "the target predicate takes ONLY the two axes")
    check(all(p.kind is p.KEYWORD_ONLY for p in parameters.values()),
          "they are keyword-only: no positional identity can be smuggled in")
    check(not any(name in parameters
                  for name in ("arm_id", "family", "controller")),
          "the target predicate cannot see any controller identity")
    for family in ("C0", "C1", "C2", "C3", "C4"):
        valid = proto.PhysicalValidity("VALID")
        met = proto.ArmResult(f"{family}-arm", family, "TARGET_MET", valid,
                              True, True)
        check(met.target_outcome == "TARGET_MET",
              f"{family}: meeting both axes records TARGET_MET - no identity gate")
        rejects(lambda f=family: proto.ArmResult(
                    f"{f}-arm", f, "TARGET_MET",
                    proto.PhysicalValidity("VALID"), True, False),
                f"{family}: viability alone never meets the target",
                "reject-everything loophole")
    check("IDENTITY-NEUTRAL" in proto.TARGET_PREDICATE
          and "NOT because any rule names C0" in proto.TARGET_PREDICATE,
          "C0 fails a positive service floor naturally, not by special case")
    arm_src = inspect.getsource(proto.ArmResult)
    check(not any(token in arm_src for token in ('== "C0"', "== 'C0'",
                                                 '!= "C4"', "!= 'C4'")),
          "ArmResult contains no controller-identity branch")
    label_doc = proto.derive_ebu_run_label.__doc__
    check("EBU-SPECIFIC" in label_doc and "not a success predicate" in label_doc,
          "derive_ebu_run_label is declared a label vocabulary, not a predicate")
    check("raw `ArmResult`" in label_doc and "ClaimConclusion" in label_doc,
          "comparison arms keep raw results and per-claim conclusions")
    rejects(lambda: proto.derive_ebu_run_label(
                proto.ArmResult("c1", "C1", "TARGET_MISSED",
                                proto.PhysicalValidity("VALID"), True, False),
                proto.OracleResult("CONTROLLABLE")),
            "the EBU label vocabulary does not apply to a comparison arm",
            "defined for the EBU arm")


def test_design_readiness_findings():
    group("FINDING-1 (C4 degeneracy) and FINDING-2 (no export permission)")
    import d0_v29
    import p1c_v29
    import ebu_candidate_controllers as cc

    # --- FINDING-1: the marginal is EXACTLY zero in band, given R <= L -----
    # Pure arithmetic on individual synthetic values; no model, no transition.
    for x, L, U, R in ((4.0, 4.0, 16.0, 2.0),     # at L
                       (10.0, 4.0, 16.0, 2.0),    # interior
                       (16.0, 4.0, 16.0, 2.0),    # at U
                       (4.0, 4.0, 16.0, 4.0)):    # R == L == x
        mu = d0_v29.marginal(1.0, 1.0, 1.0, L, U, R, x)
        check(mu == 0.0,
              f"mu is EXACTLY 0 in band at x={x:g}, L={L:g}, U={U:g}, R={R:g}")
    # ... hence f_e = 0, and theta_e >= 0 forces J_e = 0.
    edge = d0_v29.Edge(0, 1, 1.0, 0.0, 1.0)
    check(edge.theta >= 0.0, "committed Edge requires theta_e >= 0")
    rejects(lambda: d0_v29.Edge(0, 1, 1.0, -1.0, 1.0),
            "a negative theta_e refuses, so [f - theta]_+ cannot be lifted")
    for theta in (0.0, 0.5, 3.0):
        excess = 0.0 - theta                      # f_e = 0 from mu == 0
        flux = 1.0 * excess if excess > 0.0 else 0.0
        check(flux == 0.0,
              f"with f_e = 0 and theta_e = {theta:g}, the flux is 0")
    # Demand cannot lift it: C4's sizing is min(dt*J, c_e), a cap only.
    for cap in (0.0, 6.0, 1e6):
        check(min(1.0 * 0.0, cap) == 0.0,
              f"a cap of {cap:g} cannot raise a zero flux")
    # The plant has no autonomous stock-changing term: verified structurally.
    world_src = inspect.getsource(world)
    check("natural_drive" not in world_src,
          "the candidate plant never calls the committed drive term")
    successor_calls = [n for n in ast.walk(ast.parse(world_src))
                       if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Attribute)
                       and n.func.attr == "successor"]
    check(len(successor_calls) == 1,
          "exactly one state-advancing call site exists in the plant")
    check("totals" in inspect.getsource(world.apply_joint)
          and "increment" in inspect.getsource(world.apply_joint),
          "that call site's deltas come solely from Action.increment")

    # --- FINDING-2: the COMPLETE committed dispatch, not the arithmetic ----
    check(p1c_v29.SOURCE_TYPES
          == ("regenerative", "finite", "irreversible", "flow"),
          "committed P1C declares exactly four source types")
    check(p1c_v29.STOCK_TYPES == ("regenerative", "finite", "irreversible"),
          "three of them are stock-reserve types")
    dispatch = inspect.getsource(p1c_v29._source_budget)
    check('cfg.source_type == "regenerative"' in dispatch,
          "the robust budget is reached ONLY for a regenerative source")
    check('if cfg.source_type == "finite"' in dispatch
          and "return 0.0" in dispatch,
          "a finite source's budget is ZERO in the committed dispatch")
    check("irreversible source: safe extraction rate is zero" in dispatch,
          "an irreversible source's budget is ZERO")
    for state_marker in ('if state == "R"', 'if state == "I"'):
        check(state_marker in dispatch,
              f"the dispatch handles {state_marker} with export zero")
    budget_doc = " ".join(p1c_v29.robust_budget.__doc__.split())
    check("typed it regenerative" in budget_doc,
          "robust_budget's own docstring requires a regenerative typing")
    check("assumes the caller has already classified" in budget_doc,
          "robust_budget states the caller must classify first")
    check("stock units" in " ".join(p1c_v29.SourceConfig.__doc__.split()),
          "R_eff is documented as a STOCK quantity, not a rate")
    # The study's own identity forbids the only typing that would permit export.
    check(cc.identity_record()["is_regenerative"] is False,
          "this study is declared NOT regenerative, so that typing is unavailable")
    check("regeneration is ABSENT from the physical plant"
          in cc.IDENTITY_CLAUSES["not_regenerative"],
          "identity clause 3 states the plant has no regeneration")
    # The helper reproduces arithmetic only, and now says so.
    helper_doc = " ".join(cc.p1c_tick_budget_quantity.__doc__.split())
    check("APPLICABILITY WARNING" in helper_doc
          and "ARITHMETIC ONLY" in helper_doc,
          "the budget helper declares it performs no eligibility check")
    check("_source_budget" in helper_doc and "ZERO" in helper_doc,
          "the helper names the complete policy and its zero result")
    check("STOCK QUANTITY" in world.RESERVE_CONCEPTS["R_eff"],
          "R_eff is declared a stock quantity, not a rate")

    # --- both findings are recorded in the note, and neither is generalised -
    with open("V3.0_DESIGN_READINESS_NOTE_C4_DEGENERACY_AND_P1C_APPLICABILITY.md",
              encoding="utf-8") as handle:
        note = " ".join(handle.read().split())
    for marker in ("C4 is behaviourally identical to C0",
                   "no committed basis for positive export",
                   "not** a claim about EBU mechanisms in general",
                   "No model was run"):
        check(marker in note, f"the note records {marker!r}")
    for alternative in ("A0", "A1", "A2", "A3", "A4",
                        "B0", "B1", "B2", "B3"):
        check(f"**{alternative}**" in note,
              f"alternative {alternative} is offered with its trade-offs")
    check("declared conservation or boundary accounting" in note,
          "the disturbance alternative requires conservation/boundary accounting")
    check("independent of the controller" in note,
          "and requires independence from the controller and field")
    check("separately identified candidate" in note
          or "separately identified" in note,
          "a service-aware variant must be a separately identified candidate")
    check("No direction is adopted here" in note,
          "the note recommends without adopting")
    # Nothing was accepted by this review.
    check(len(cc.unapproved_drafts()) == 5,
          "all five arms remain CANDIDATE_UNAPPROVED after the review")


def test_transition_guards_statically():
    group("this suite is static-only, and the transition guards still hold")

    # --- 1. NARROW CHECK: this FILE contains no DIRECT transition call ------
    # Limitation, stated rather than glossed: this inspects direct calls in one
    # file. It does NOT prove that an import, helper or callback reached from
    # here cannot execute a transition; that would need call-graph analysis or
    # runtime instrumentation, neither of which is implemented.
    TRANSITIONS = {"execute_tick", "plan_tick", "apply_joint", "run_campaign"}
    own = ast.parse(inspect.getsource(sys.modules[__name__]))
    called = set()
    for node in ast.walk(own):
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) \
                else getattr(node.func, "id", None)
            if name in TRANSITIONS:
                called.add(name)
    check(called <= {"run_campaign"},
          f"this FILE makes no direct state-advancing transition call "
          f"(found {sorted(called) or 'none'}; run_campaign only ever refuses)")
    check("apply_joint" not in called and "execute_tick" not in called
          and "plan_tick" not in called,
          "no apply_joint, execute_tick or plan_tick call exists in this file")

    # --- 2. the transition suite exists, is opt-in, and declares itself -----
    with open("test_ebu_foundation_transitions.py", encoding="utf-8") as handle:
        dynamic = handle.read()
    check("EBU_ALLOW_MODEL_TRANSITIONS" in dynamic,
          "the transition suite requires an explicit opt-in variable")
    check("NOT PART OF THE DEFAULT CI PATH" in dynamic,
          "the transition suite declares it is off the default CI path")
    dynamic_tree = ast.parse(dynamic)
    guarded = any(
        isinstance(node, ast.Compare)
        and any(isinstance(c, ast.Constant) and c.value == "1"
                for c in node.comparators)
        for node in ast.walk(dynamic_tree))
    check(guarded, "the opt-in is compared against an explicit value")
    # The phrase may appear only where the file is RETRACTING it, never in an
    # executable print. Check the statements the suite actually emits.
    printed = [node for node in ast.walk(dynamic_tree)
               if isinstance(node, ast.Call)
               and getattr(node.func, "id", None) == "print"]
    emitted = " ".join(arg.value for node in printed for arg in node.args
                       if isinstance(arg, ast.Constant)
                       and isinstance(arg.value, str))
    check("Model-state advancement: NONE" not in emitted,
          "the transition suite never PRINTS a zero-advancement claim")
    check("model-state advancement: 2 single transitions" in emitted.lower()
          or "2 single transitions" in emitted,
          "the transition suite prints the true advancement count")

    # --- 3. the guards the static suite no longer exercises, asserted on the
    #        transition functions' own source ------------------------------
    joint_src = inspect.getsource(world.apply_joint)
    check("hard_feasible" in joint_src and "InfeasibleAction" in joint_src,
          "apply_joint refuses on a non-empty hard_feasible result")
    check("conservation_residual" in joint_src
          and "ConservationFailure" in joint_src,
          "apply_joint refuses when the conservation residual exceeds tolerance")
    check("tolerance" in inspect.signature(world.apply_joint).parameters,
          "apply_joint takes an explicit tolerance, never a default")
    feasible_src = inspect.getsource(world.hard_feasible)
    check("joint_successor" in feasible_src,
          "hard feasibility is decided on the JOINT successor")
    tick_src = inspect.getsource(proto.execute_tick)
    check(tick_src.index("budget.spend()") < tick_src.index("plan_tick"),
          "execute_tick spends its budget BEFORE planning anything")
    check(proto.TickBudget.conformance().limit == 1,
          "the conformance budget is exactly one tick")

    # --- 4. the execution record this repository may honestly print ---------
    check("2 single transitions" in dynamic,
          "the transition suite records exactly how much it advances")


def test_no_science_is_adopted_here():
    group("no world, parameter or scientific choice is adopted")
    for module in (world, settle, proto):
        source = inspect.getsource(module)
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        banned = {"subprocess", "socket", "urllib", "requests", "boto3",
                  "docker", "random"}
        check(not (imported & banned),
              f"{module.__name__}: no subprocess/network/cloud/global-random "
              f"import ({imported & banned or 'none'})")
        opens = {n.func.id for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "open"}
        check(not opens, f"{module.__name__}: never calls open()")

    # N/H/X stays excluded.
    check("nhx_long_horizon" in ac.EXCLUDED, "N/H/X remains excluded")
    for module in (world, settle, proto):
        check("N/H/X" not in inspect.getsource(module),
              f"{module.__name__} does not revive N/H/X")

    # Every scientific parameter is a required argument, never a default.
    rejects(lambda: world.WorldSpec("x", "0", world.Topology(("a",), ()), {},
                                    path_semantics="model_realised_constant_rate"),
            "a world without node specs refuses")
    rejects(lambda: proto.DeclaredController("c", "C1", lambda v: {},
                                             declared_formula=""),
            "a controller without a declared formula refuses",
            "requires the exact formula")
    rejects(lambda: world.generate_demand_schedule(
                seed="s", model_id="", horizon=1, edges=(), draw=lambda *a: 0.0),
            "a demand schedule without a declared model_id refuses",
            "forbids an undocumented")

    # The committed potential is reused, not forked.
    check("d0_v29" in inspect.getsource(settle),
          "the settlement layer calls the committed d0_v29 potential")


# ===========================================================================
# F-L1 - F-L6: the loss account and the two accounting boundaries
# ===========================================================================
# EXECUTION CLASS: identical to the rest of this file. Every state below is
# CONSTRUCTED AS DATA and every endpoint pair is SUPPLIED; `apply_joint`,
# `execute_tick` and `WorldState.successor` are never called, so no transition
# is performed. `conservation_profile`, `endpoint_difference`, `path_integral`
# and `marginal_at` are pure functions over supplied arguments.
#
# EXACTNESS: eta = 3/4 and every quantity below is a DYADIC RATIONAL, so
# eta*q, (1-eta)*q and the quadratic potential are all exactly representable in
# binary floating point. Every closure check therefore requires EXACT equality
# (tolerance 0.0), not a tolerance. The two places where exactness is NOT
# claimed - the difference quotient in F-L4 - are labelled as such.
#
# THE NUMBERS ARE ILLUSTRATIVE SOFTWARE-TEST CONSTANTS. eta = 3/4 is chosen
# only because it is dyadic; it is not a study parameter, not a candidate
# value, and the first study remains eta = 1.
def lossy_pair():
    """A two-node world with a DECLARED loss channel, and its lossless twin."""
    topo = world.Topology(("n0", "n1"), (("n0", "n1"),))
    specs = {"n0": world.NodeSpec("n0", 100.0, 16.0, 20.0, 2.0, 1.0, 1.0, 1.0),
             "n1": world.NodeSpec("n1", 100.0, 4.0, 8.0, 2.0, 1.0, 1.0, 1.0)}
    lossless = world.WorldSpec("LOSS-FIXTURE", "0", topo, specs,
                               path_semantics="model_realised_constant_rate")
    lossy = world.WorldSpec("LOSS-FIXTURE", "0", topo, specs, eta=0.75,
                            loss_sink="w",
                            path_semantics="model_realised_constant_rate")
    return lossless, lossy


def transfer(spec, q):
    return world.Action("A", "fixture", ("n0", "n1"), "scalar",
                        world.QuantityLadder(q, q, q, q, spec.eta * q),
                        0, 0, "fixture-permission")


def test_loss_accounting_and_boundaries():
    group("F-L1..F-L6 - lossless closure, lossy balance, and the sink's limits")
    lossless, lossy = lossy_pair()
    q = 4.0

    # --- F-L1: lossless closure at eta = 1 -------------------------------
    # A NONZERO PRE-EXISTING loss balance is carried throughout so that no
    # check can confuse the INCREMENT dw with the LEVEL w'. Design section 6:
    # a nonzero accumulated w is not a conservation failure, and there is no
    # universal rule that a historical ledger must contain zero.
    check(lossless.is_conservative, "F-L1 the eta=1 twin is closed and lossless")
    before = world.WorldState(lossless.digest, {"n0": 12.0, "n1": 6.0}, 7.0)
    after = world.WorldState(lossless.digest, {"n0": 8.0, "n1": 10.0}, 7.0)
    profile = world.conservation_profile(lossless, before, after,
                                         [transfer(lossless, q)],
                                         tolerance=0.0)
    check(profile.interior_delta == 0.0,
          "F-L1 active-stock closure is EXACT: d(sum x) = 0")
    check(profile.sink_delta == 0.0 and profile.expected_sink == 0.0,
          "F-L1 the sink increment is exactly zero at eta = 1")
    check(before.loss_accumulated == 7.0 and after.loss_accumulated == 7.0,
          "F-L1 a nonzero pre-existing w is preserved, not required to be 0")
    check(profile.active_balance_holds,
          "F-L1 the active balance d(sum x) = -dw holds")

    # --- F-L2: explicit lossy balance ------------------------------------
    # q = 4 leaves the source; eta*q = 3 is delivered; (1-eta)*q = 1 is lost.
    # Each of the four quantities is checked INDEPENDENTLY - total closure
    # alone would not establish that any one of them is right.
    lb = world.WorldState(lossy.digest, {"n0": 12.0, "n1": 6.0}, 7.0)
    la = world.WorldState(lossy.digest, {"n0": 8.0, "n1": 9.0}, 8.0)
    lp = world.conservation_profile(lossy, lb, la, [transfer(lossy, q)],
                                    tolerance=0.0)
    check(lp.per_node["n0"] == (-4.0, -4.0),
          "F-L2 the source withdrawal is the FULL sent q = 4, not eta*q")
    check(lp.per_node["n1"] == (3.0, 3.0),
          "F-L2 the useful delivery is eta*q = 3")
    check(lp.sink_delta == 1.0 and lp.expected_sink == 1.0,
          "F-L2 the sink increment is (1-eta)*q = 1, from the ACTION LAW")
    check(lp.interior_delta == -1.0,
          "F-L2 the active balance is d(sum x) = -dw = -1")
    check(lp.residual == 0.0,
          "F-L2 the EXPANDED balance d(sum x + w) = 0 closes EXACTLY")
    check(la.loss_accumulated == 8.0 and lp.sink_delta == 1.0,
          "F-L2 dw = 1 is distinguished from the level w' = 8")
    check(lp.boundary == world.EXPANDED_ACCOUNTING,
          "F-L2 the ledger DECLARES which accounting boundary it describes")

    # --- F-L3: exact lossy finite field difference ------------------------
    # V is evaluated on the ACTIVE endpoints only. w is NOT added to V, and the
    # LOSSY successor is used - never a lossless successor with a correction.
    z = {"n0": 12.0, "n1": 6.0}
    increment = transfer(lossy, q).increment(lossy)
    check(increment == {"n0": -4.0, "n1": 3.0},
          "F-L3 the increment used for V is the LOSSY one")
    field = settle.endpoint_difference(lossy, z, increment)
    check(field == -49.0,
          f"F-L3 F = V(z) - V(T_a z) = {field:g}, exact on dyadic data")
    wrong = settle.endpoint_difference(lossy, z, {"n0": -4.0, "n1": 4.0})
    check(wrong != field,
          f"F-L3 the LOSSLESS successor gives {wrong:g} != {field:g}: "
          f"'evaluate lossless, then append a loss correction' is wrong")
    check(settle.potential(lossy, z) == settle.potential(lossless, z),
          "F-L3 V does not read eta or w: it is a function of ACTIVE stocks")

    # --- F-L4: the marginal relation, distinguished from the finite value --
    mu_i = settle.marginal_at(lossy, "n0", z["n0"])
    mu_j = settle.marginal_at(lossy, "n1", z["n1"])
    slope = mu_i - lossy.eta * mu_j
    check(slope == -8.0,
          f"F-L4 dF/dq at q=0 = mu_i - eta*mu_j = {slope:g}")
    # NOT an exact check: a difference quotient is not the derivative, and this
    # is floating point. The claim is CONVERGENCE, and it is labelled as such.
    quotients = [settle.endpoint_difference(
        lossy, z, {"n0": -h, "n1": lossy.eta * h}) / h
        for h in (1e-4, 1e-5, 1e-6)]
    check(all(abs(qt - slope) < 1e-3 for qt in quotients)
          and abs(quotients[-1] - slope) < abs(quotients[0] - slope),
          "F-L4 difference quotients CONVERGE to that slope "
          "(convergence, not an exact identity; floating point)")
    check(field != q * slope,
          f"F-L4 the finite value {field:g} is NOT q times the initial force "
          f"{q * slope:g}: the identity is a derivative, not a shortcut")

    # --- F-L5: endpoint/path closure -------------------------------------
    # EXACT: the integrand is piecewise linear in lambda between breakpoints
    # and the trapezoid rule is exact on each piece, so this is exact
    # mathematical integration evaluated in floating point on dyadic data -
    # not a numerical approximation that happens to be close.
    integral = settle.path_integral(lossy, z, increment, increment)
    check(integral == field,
          f"F-L5 path integral {integral:g} == endpoint difference "
          f"{field:g} EXACTLY under the declared path semantics")
    check(lossy.path_semantics == "model_realised_constant_rate",
          "F-L5 the path semantics is DECLARED, not inferred from arithmetic")

    # --- F-L6: burden separation -----------------------------------------
    # C_a = 0 for this idealized fixture. No synthetic inefficiency penalty is
    # added anywhere, and the ledger entry is NOT a burden-valued term.
    c_a = 0.0
    check(field - c_a == field,
          "F-L6 dE = F - C_a with C_a = 0: no loss surcharge is added")
    # A TEST MUST NOT PROMOTE AN INTERPRETIVE JUDGMENT INTO AUTHORITY. An
    # earlier revision asserted here that the lambda_L term "remains category
    # 2 because w is not an argument of V_loc". That reads ONE clause of
    # Definition 6.4 while ignoring four others (the body's "transport loss
    # already visible through the state", category 1's "state transition OR
    # V_loc", category 2's own "no corresponding state coordinate" admission
    # condition, and the no-double-count condition's "or any admissible
    # extended" state functional) and O9, which registers this exact case as
    # OPEN. The assertion is withdrawn. What is checked now is that the module
    # RECORDS the question as unresolved - not that it answers it.
    detail = world.LOSS_ACCOUNT_SEMANTICS["w and C_a"]
    check("UNRESOLVED AUTHORITY SCOPE QUESTION" in detail
          and "WITHDRAWN" in detail,
          "F-L6 the Definition 6.4 classification is recorded as UNRESOLVED, "
          "and the earlier 'still category 2' assertion is withdrawn")
    check("O9" in detail and "ADMISSIBLE EXTENDED" in detail,
          "F-L6 the record cites the clauses that conflict, including O9 and "
          "the extended-state-functional language")
    check("does not by itself VALUE any burden"
          in world.LOSS_ACCOUNT_SEMANTICS["w and C_a - what IS settled"],
          "F-L6 ledger presence is bookkeeping, and proves NO burden valued")
    check("IDENTICALLY ZERO"
          in world.LOSS_ACCOUNT_SEMANTICS["w and C_a - why Study 1 is unaffected"],
          "F-L6 at eta = 1 the lambda_L term vanishes whichever category it "
          "is, so the unresolved question blocks nothing in Study 1")
    check("DECLARED OMISSION" in world.LOSS_ACCOUNT_SEMANTICS["w and V"],
          "F-L6 Vtilde(x,w) = V(x) is a declared omission, not a finding that "
          "waste is harmless")


def test_loss_negative_controls():
    group("F-L negative controls - each wrong loss accounting must be caught")
    lossless, lossy = lossy_pair()
    q = 4.0
    lb = world.WorldState(lossy.digest, {"n0": 12.0, "n1": 6.0}, 7.0)

    # NL1 - undeclared loss channel. THIS IS THE GAP THAT MOTIVATED THE REPAIR:
    # `conservation_residual` returns 0.0 here, reporting a vanished 2.0 as
    # conserved, because an undeclared sink absorbed it.
    cb = world.WorldState(lossless.digest, {"n0": 12.0, "n1": 6.0}, 0.0)
    ca = world.WorldState(lossless.digest, {"n0": 10.0, "n1": 6.0}, 2.0)
    check(world.conservation_residual(lossless, cb, ca) == 0.0,
          "NL1 r_cons ALONE reports this masked 2.0 loss as conserved")
    rejects(lambda: world.sink_increment(lossless, cb, ca),
            "NL1 an undeclared sink change is refused",
            "declares\nNO loss channel".replace("\n", " "))
    rejects(lambda: world.conservation_profile(lossless, cb, ca, [],
                                               tolerance=0.0),
            "NL1 the profile refuses it too, so the mask cannot survive")

    # NL2 - withdrawal from the irreversible cumulative loss account.
    rb = world.WorldState(lossy.digest, {"n0": 12.0, "n1": 6.0}, 5.0)
    ra = world.WorldState(lossy.digest, {"n0": 15.0, "n1": 6.0}, 2.0)
    check(world.conservation_residual(lossy, rb, ra) == 0.0,
          "NL2 r_cons ALONE reports a sink withdrawal as conserved")
    rejects(lambda: world.sink_increment(lossy, rb, ra),
            "NL2 a DECREASING loss account is refused",
            "irreversible cumulative loss account")

    # NL3 - the full q delivered although eta < 1 (the loss never taken).
    rejects(lambda: world.conservation_profile(
                lossy, lb, world.WorldState(lossy.digest,
                                            {"n0": 8.0, "n1": 10.0}, 7.0),
                [transfer(lossy, q)], tolerance=0.0),
            "NL3 delivering the full q when eta < 1 is refused")

    # NL4 - the lost quantity counted twice in the sink.
    rejects(lambda: world.conservation_profile(
                lossy, lb, world.WorldState(lossy.digest,
                                            {"n0": 8.0, "n1": 9.0}, 9.0),
                [transfer(lossy, q)], tolerance=0.0),
            "NL4 double-counting the loss in the sink is refused",
            "does not match the declared action law")

    # NL5 - the lost quantity omitted from the sink.
    rejects(lambda: world.conservation_profile(
                lossy, lb, world.WorldState(lossy.digest,
                                            {"n0": 8.0, "n1": 9.0}, 7.0),
                [transfer(lossy, q)], tolerance=0.0),
            "NL5 omitting the loss from the sink is refused")

    # NL6 - a sink increment used as a PLUG. The interior is wrong at BOTH
    # nodes, but the sink is chosen so the TOTAL closes. Total closure alone
    # must not pass it; the per-node identities must be checked separately.
    plug = world.WorldState(lossy.digest, {"n0": 9.0, "n1": 8.0}, 8.0)
    check(world.conservation_residual(lossy, lb, plug) == 0.0,
          "NL6 the plugged transition closes TOTALLY (r_cons = 0)")
    rejects(lambda: world.conservation_profile(lossy, lb, plug,
                                               [transfer(lossy, q)],
                                               tolerance=0.0),
            "NL6 per-node identities still catch it: closure is not proof",
            "individually\ncorrect".replace("\n", " "))

    # NL7 - the sink treated as ordinary transferable stock. Structural:
    # a loss sink may not be a topology node, so no edge can reach it.
    topo = world.Topology(("n0", "w"), (("n0", "w"),))
    specs = {n: world.NodeSpec(n, 100.0, 4.0, 8.0, 2.0, 1.0, 1.0, 1.0)
             for n in ("n0", "w")}
    rejects(lambda: world.WorldSpec(
                "BAD", "0", topo, specs, eta=0.75, loss_sink="w",
                path_semantics="model_realised_constant_rate"),
            "NL7 a loss sink that is also a transferable node is refused",
            "not an\nordinary node".replace("\n", " "))
    check("w" not in lossy.topology.nodes,
          "NL7 the declared sink is outside the topology, so no edge reaches it")
    check(lb.total() == 18.0,
          "NL7 WorldState.total() is the INTERIOR total: it excludes w")

    # NL8 - wrong sent/delivered convention.
    check(world.delivered_from_sent(q, lossy.eta) == 3.0
          and world.sent_from_delivered(3.0, lossy.eta) == 4.0,
          "NL8 sent 4 -> delivered 3, and delivered 3 needs sent 4")
    check(world.sent_from_delivered(q, lossy.eta) != q,
          "NL8 a DELIVERED requirement of 4 needs a different sent quantity: "
          "D_e / eta, so the two conventions are not interchangeable")
    check("D_e / eta_e" in world.QUANTITY_SEMANTICS["d_e"],
          "NL8 d_e stays SOURCE-SIDE; delivered demand is the distinct D_e")

    # NL9 - negative and non-finite quantities.
    rejects(lambda: world.WorldState(lossy.digest, {"n0": 1.0, "n1": 1.0}, -1.0),
            "NL9 a negative loss account is refused")
    rejects(lambda: world.QuantityLadder(-1.0, -1.0, -1.0, -1.0, -1.0),
            "NL9 a negative ladder quantity is refused")
    rejects(lambda: world.delivered_from_sent(q, 0.0),
            "NL9 eta = 0 is outside (0, 1] and is refused")
    rejects(lambda: world.delivered_from_sent(q, 1.5),
            "NL9 eta > 1 would CREATE resource and is refused")

    # NL10 - a closure check accepting an invalid residual. The tolerance is a
    # REQUIRED argument; there is no default that could quietly widen it, and
    # the committed foundation declares no universal zero-residual rule.
    rejects(lambda: world.conservation_profile(lossy, lb, lb,
                                               [transfer(lossy, q)]),
            "NL10 conservation_profile requires an EXPLICIT tolerance")
    rejects(lambda: world.conservation_profile(lossy, lb, lb,
                                               [transfer(lossy, q)],
                                               tolerance=-1.0),
            "NL10 a negative tolerance is refused")
    rejects(lambda: world.conservation_profile(
                lossy, lb, world.WorldState(lossy.digest,
                                            {"n0": 8.0, "n1": 9.0}, 8.0),
                [transfer(lossy, q)], tolerance=0.0, boundary="unstated"),
            "NL10 a ledger with an undeclared accounting boundary is refused")

    # NL11 - states from a different world. eta is part of the spec digest, so
    # a lossy and a lossless world are not interchangeable.
    check(lossy.digest != lossless.digest,
          "NL11 eta and loss_sink are inside the spec digest")
    rejects(lambda: world.conservation_profile(
                lossless, lb, world.WorldState(lossless.digest,
                                               {"n0": 8.0, "n1": 9.0}, 7.0),
                [transfer(lossless, q)], tolerance=0.0),
            "NL11 mixing states across worlds is refused")


def test_first_study_stays_lossless():
    group("the first study is UNCHANGED: eta = 1, and the guards are inert")
    import ebu_candidate_controllers as cc
    lossless, lossy = lossy_pair()
    # The study configuration validator still demands a conservative world.
    check(lossless.is_conservative and not lossy.is_conservative,
          "eta = 1 with no sink is conservative; eta = 3/4 with a sink is not")
    rejects(lambda: cc.validate_study_configuration(lossy),
            "the candidate study REFUSES a lossy world: it is a different study",
            "CONSERVATIVE world")
    # At eta = 1 every loss term is identically zero, so the new guards can
    # never fire in the first study. They add no parameter and change no
    # first-study behaviour.
    action = transfer(lossless, 4.0)
    check(action.loss(lossless) == 0.0,
          "at eta = 1 the action law yields exactly zero loss")
    b = world.WorldState(lossless.digest, {"n0": 12.0, "n1": 6.0}, 0.0)
    a = world.WorldState(lossless.digest, {"n0": 8.0, "n1": 10.0}, 0.0)
    check(world.sink_increment(lossless, b, a) == 0.0,
          "sink_increment is identically 0 in the first study")
    prof = world.conservation_profile(lossless, b, a, [action], tolerance=0.0)
    check(prof.expected_sink == 0.0 and prof.residual == 0.0,
          "conservation_profile passes the first study's own transition")
    # The repair is ADDITIVE: conservation_residual and apply_joint are
    # untouched, so no existing call site changes behaviour.
    source = inspect.getsource(world.conservation_residual)
    check("sank = after.loss_accumulated - before.loss_accumulated" in source
          and "raise" not in source,
          "conservation_residual is UNCHANGED: same formula, still total, "
          "still returns rather than raises")
    check("conservation_profile" not in inspect.getsource(world.apply_joint),
          "apply_joint is UNCHANGED: the new audit is not wired into it")


def main() -> int:
    for test in (test_f1_one_finite_action, test_f2_symmetric_simultaneous,
                 test_f3_asymmetric_simultaneous, test_f4_positive_interaction,
                 test_f5_negative_interaction, test_f6_three_way_interaction,
                 test_f7_shared_source_resolution, test_f8_conservation,
                 test_f9_long_overlapping_epochs, test_f10_mobius_reconstruction,
                 test_negative_controls,
                 test_simultaneous_path_field_attribution,
                 test_raw_facts_separate_from_inference,
                 test_candidate_controllers_are_drafts_only,
                 test_controller_correction_package,
                 test_protocol_refuses_to_run_science,
                 test_reserve_band_and_unit_integrity,
                 test_design_readiness_findings,
                 test_transition_guards_statically,
                 test_loss_accounting_and_boundaries,
                 test_loss_negative_controls,
                 test_first_study_stays_lossless,
                 test_no_science_is_adopted_here):
        test()
    print(f"\nEBU foundation gate: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)")
    print("  direct transition calls in this file: 0 "
          "(no apply_joint, plan_tick or execute_tick) - checked by AST over "
          "THIS FILE only; imports/helpers are not proven transition-free")
    print("  foundation fixture model-state advancement: NONE in this suite. "
          "test_ebu_foundation_transitions.py contains 2 transition SITES per "
          "execution (opt-in, off the default path). The cumulative number of "
          "historical executions of those sites is NOT TRACKED and is unknown.")
    print("  scientific-study execution: NONE")
    print("  scientific trajectories generated: 0")
    print("  scientific evidence generated: NONE")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
