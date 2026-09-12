"""Long-horizon mechanism validation; static and pure-function only.

This suite MUST NOT call a model step, a runner, a simulation, a trajectory,
a multi-tick loop, ``p1c_v29.p1c_step``, ``service_v30.bounded_step``, or any
tick function.  Every check below is an isolated pure-function evaluation on a
frozen synthetic state, or a static source/AST inspection.

It validates the four adopted mechanisms, their fail-closed behaviour, their
agreement with the published P1C rule and with the frozen single-action
selectors, and the module's execution-safety guarantees.
"""
from __future__ import annotations

import ast
import inspect
import json
import math
import textwrap

import d0_v29 as d0
import ebu_quote_v30 as eq
import longhorizon_v30 as lh
import p1c_v29 as p1c

PASSED = 0
FAILED = 0
GROUPS = 0


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


def rejects(function, label: str, contains: str = "") -> None:
    try:
        function()
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        check(not contains or contains in str(error), label)
    else:
        check(False, label)


def close(actual, expected, tolerance=1e-14) -> bool:
    return abs(actual - expected) <= tolerance * max(1.0, abs(expected))


# --------------------------------------------------------------------------
# synthetic fixtures - declared states only, never a trajectory
# --------------------------------------------------------------------------
def synthetic_world():
    """One regenerative source, two out-edges, two distinct destinations.

    Values are chosen to exercise the arithmetic and are NOT the adopted N/H/X
    tuples; this suite tests mechanisms, not a study configuration.
    """
    source = d0.Cell(alpha=0.5, beta=1.0, chi=0.5, L=2.0, U=6.0, R=1.0,
                     K=8.0, s=0.0, d=0.0, lam=0.0, kappa=0.0,
                     source="logistic", rho=1.0, A=0.0)
    dest1 = d0.Cell(alpha=1.0, beta=1.0, chi=0.0, L=1.0, U=4.0, R=0.0,
                    K=6.0, s=0.0, d=0.25, lam=0.0, kappa=0.0,
                    source="none", rho=0.0, A=0.0)
    dest2 = d0.Cell(alpha=0.8, beta=1.0, chi=0.0, L=1.0, U=4.0, R=0.0,
                    K=6.0, s=0.0, d=0.25, lam=0.0, kappa=0.0,
                    source="none", rho=0.0, A=0.0)
    edges = (d0.Edge(i=0, j=1, M=10.0, theta=0.1, eta=0.9),
             d0.Edge(i=0, j=2, M=10.0, theta=0.1, eta=0.9))
    return d0.World(cells=(source, dest1, dest2), edges=edges)


def synthetic_config(reserve=1.0):
    return p1c.SourceConfig(source_id=0, source_type="regenerative",
                            R_eff=reserve, eps_x=0.0, eps_u=0.0)


def candidate(edge, quant_index, frac, f, q_req, q_acc):
    return {"edge": edge, "quant_index": quant_index, "frac": frac, "f": f,
            "J": q_req / frac if frac else 0.0, "q_req": q_req,
            "q_e_max": q_acc, "q_acc": q_acc}


# --------------------------------------------------------------------------
def test_execution_safety_and_import_purity():
    group("execution safety: no step, runner, or trajectory anywhere")
    source = inspect.getsource(lh)
    tree = ast.parse(source)
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Attribute):
                called.add(target.attr)
            elif isinstance(target, ast.Name):
                called.add(target.id)
    forbidden = {"p1c_step", "bounded_step", "run_arm", "gate1dc_tick",
                 "step", "simulate", "rollout", "trajectory"}
    check(not (called & forbidden),
          f"no forbidden step call (found {sorted(called & forbidden)})")

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    check("gate1dc_v30" not in imported,
          "does not import gate1dc_v30 (not import-pure at module scope)")
    check("service_v30" not in imported, "does not import service_v30")
    check(imported == {"__future__", "math", "dataclasses", "typing",
                       "d0_v29", "p1c_v29", "ebu_quote_v30"},
          f"imports EXACTLY the stdlib and frozen law modules it needs "
          f"(found {sorted(imported)})")

    module_calls = [n for n in tree.body
                    if isinstance(n, (ast.Expr, ast.Assign, ast.AnnAssign))
                    and any(isinstance(sub, ast.Call) for sub in ast.walk(n))]
    check(not module_calls,
          "no module-scope call in any Expr/Assign/AnnAssign: import is pure")
    check("random" not in imported and "secrets" not in imported,
          "no stochastic source imported")


def test_mechanism_1_joint_budget_cap():
    group("mechanism 1: joint two-action budget cap")
    world = synthetic_world()
    cfg = synthetic_config()
    dt = 0.02
    # State P with headroom: x above reserve, positive drive.
    x, u = 1.15, 0.98
    state, budget = lh.source_budget_rate(cfg, x, u, dt)
    expected = ((x - 0.0) + dt * (u - 0.0) - 1.0) / dt
    check(state == "P", "state P at declared headroom")
    check(close(budget, expected), "budget reproduces robust_budget A4.5")
    check(close(budget, p1c.robust_budget(cfg, x, u, dt)),
          "budget equals the published robust_budget entry point")

    # Exhaustive branch table against the frozen rule, all source types and
    # all reachable states. p1c._source_budget is the authority; comparison is
    # bitwise, not by tolerance.
    mismatches = []
    covered = set()
    for source_type in ("regenerative", "finite", "irreversible", "flow"):
        if source_type == "flow":
            probe = p1c.SourceConfig(source_id=0, source_type="flow",
                                     flow_cap=2.5)
        else:
            probe = p1c.SourceConfig(source_id=0, source_type=source_type,
                                     R_eff=1.0, eps_x=0.05, eps_u=0.05)
        for xv in (0.0, 0.5, 0.9, 1.0, 1.5, 3.0):
            for uv in (-5.0, -0.5, 0.0, 0.5, 5.0):
                for step in (0.01, 0.25, 1.0):
                    frozen_state = p1c.classify_state(probe, xv, uv, step)
                    frozen = p1c._source_budget(probe, frozen_state, xv, uv,
                                                step)[0]
                    mine_state, mine = lh.source_budget_rate(probe, xv, uv,
                                                             step)
                    covered.add((source_type, frozen_state))
                    if mine_state != frozen_state or mine != frozen:
                        mismatches.append((source_type, frozen_state, xv, uv,
                                           step, frozen, mine))
    check(not mismatches,
          f"budget table matches p1c._source_budget bitwise on "
          f"{len(covered)} (type, state) branches; {len(mismatches)} mismatch")
    check(len(covered) >= 10,
          f"branch coverage reaches every reachable pair (covered {len(covered)})")
    check({"flow", "regenerative", "finite", "irreversible"}
          == {t for t, _ in covered}, "all four source types exercised")
    check({"P", "R", "I", "F"} <= {st for _, st in covered},
          "all four action-time states exercised")

    # Single action reduces exactly to the frozen min(q_req, Q_max) clamp.
    for q_req in (0.5 * budget, budget, 2.0 * budget):
        one = lh.joint_budget_cap(world, cfg, x, u, dt,
                                  [candidate(0, 0, 1.0, 0.6, q_req, 0.0)])
        scale = min(1.0, budget / q_req) if q_req > 0.0 else 0.0
        check(one.q_acc[0] == scale * q_req,
              f"m=1 equals p1c_step's sigma*q_req EXACTLY at "
              f"q_req={q_req:.4f}")
        check(close(one.q_acc[0], min(q_req, budget)),
              f"m=1 agrees with min(q_req, Q_max) to rounding at "
              f"q_req={q_req:.4f}")
    # The documented ulp caveat is real, not hypothetical.
    tight = p1c.SourceConfig(source_id=0, source_type="regenerative",
                             R_eff=0.0)
    ulp = lh.joint_budget_cap(world, tight, 7.0, 0.0, 1.0,
                              [candidate(0, 0, 1.0, 0.6, 25.0, 0.0)])
    check(ulp.q_acc[0] == 7.000000000000001 and min(25.0, 7.0) == 7.0,
          "the documented one-ulp divergence from min(q_req, Q_max) is real")

    # Two actions: proportional scaling, never an independent clamp.
    a = candidate(0, 4, 1.0, 0.60, 0.7 * budget, 0.7 * budget)
    b = candidate(1, 4, 1.0, 0.55, 0.7 * budget, 0.7 * budget)
    pair = lh.joint_budget_cap(world, cfg, x, u, dt, [a, b])
    check(close(pair.requested_total, 1.4 * budget), "aggregate request summed")
    check(close(pair.scale, 1.0 / 1.4), "sigma = min(1, Q_max/Q_req)")
    check(close(pair.accepted_total, budget), "pair total capped at Q_max")
    check(pair.binding, "binding flag set when the cap bites")
    independent = min(0.7 * budget, budget) * 2
    check(independent > pair.accepted_total + 1e-12,
          "independent per-candidate clamp over-states the pair (the gap)")
    check(close(pair.q_acc[0], pair.q_acc[1]),
          "equal requests receive equal shares")

    # Unbinding pair passes through untouched.
    small_a = candidate(0, 0, 0.2, 0.60, 0.2 * budget, 0.2 * budget)
    small_b = candidate(1, 0, 0.2, 0.55, 0.3 * budget, 0.3 * budget)
    loose = lh.joint_budget_cap(world, cfg, x, u, dt, [small_a, small_b])
    check(close(loose.scale, 1.0), "sigma = 1 when the budget does not bind")
    check(not loose.binding, "binding flag clear when the cap does not bite")
    check(close(loose.q_acc[0], 0.2 * budget)
          and close(loose.q_acc[1], 0.3 * budget),
          "unbound requests are granted in full")

    # Zero budget in state R: admissibility precedes EBU, menu is empty.
    state_r, budget_r = lh.source_budget_rate(cfg, 0.9, 0.5, dt)
    check(state_r == "R" and budget_r == 0.0, "state R yields a zero budget")
    starved = lh.joint_budget_cap(world, cfg, 0.9, 0.5, dt, [a, b])
    check(starved.scale == 0.0 and starved.accepted_total == 0.0,
          "zero budget grants nothing to any action")

    group("mechanism 1: fail-closed")
    rejects(lambda: lh.joint_budget_cap(world, cfg, x, u, 0.0, [a]),
            "rejects dt = 0", "dt must be > 0")
    rejects(lambda: lh.joint_budget_cap(world, cfg, x, u, dt, [a, b, a]),
            "rejects more actions than m", "exceed")
    rejects(lambda: lh.joint_budget_cap(
        world, cfg, x, u, dt, [a, candidate(0, 3, 0.8, 0.6, 0.1, 0.1)]),
        "rejects two actions on one edge", "distinct")
    rejects(lambda: lh.joint_budget_cap(world, cfg, x, u, dt, [a], m=3),
            "rejects m above the adopted bound", "bound")
    rejects(lambda: lh.joint_budget_cap(world, cfg, x, u, dt, [{"edge": 0}]),
            "rejects a malformed candidate", "missing required key")
    rejects(lambda: lh.joint_budget_cap(
        world, cfg, x, u, dt, [candidate(0, 0, 1.0, 0.6, -1.0, 0.0)]),
        "rejects a negative request", ">= 0")
    rejects(lambda: lh.source_budget_rate("not a config", x, u, dt),
            "rejects a non-SourceConfig", "SourceConfig")
    rejects(lambda: lh.joint_budget_cap("not a world", cfg, x, u, dt, [a]),
            "rejects a non-World", "World")
    rejects(lambda: lh.joint_budget_cap(
        world, cfg, x, u, dt, [candidate(9, 0, 1.0, 0.6, 0.1, 0.1)]),
        "rejects an out-of-range edge", "out of range")

    # One source's budget must never be applied to another source's edges:
    # p1c_step groups by source and caps each group separately.
    foreign = d0.World(cells=world.cells,
                       edges=(world.edges[0],
                              d0.Edge(i=2, j=1, M=10.0, theta=0.1, eta=0.9)))
    rejects(lambda: lh.joint_budget_cap(foreign, cfg, x, u, dt, [a, b]),
            "rejects an edge that does not leave this source",
            "not source 0")

    # Type laxity: the frozen law rejects strings and bools; so must this.
    rejects(lambda: lh.source_budget_rate(cfg, "1.15", u, dt),
            "rejects a string stock", "finite real number")
    rejects(lambda: lh.source_budget_rate(cfg, True, u, dt),
            "rejects a bool stock", "finite real number")
    # Built inline: the candidate() helper would divide by frac first.
    rejects(lambda: lh.joint_budget_cap(
        world, cfg, x, u, dt,
        [{"edge": 0, "quant_index": 0, "frac": 1.0, "q_req": "3.0"}]),
        "rejects a string request", "finite real number")
    rejects(lambda: lh.joint_budget_cap(
        world, cfg, x, u, dt,
        [{"edge": 0, "quant_index": 0, "frac": 1.0, "q_req": True}]),
        "rejects a bool request", "finite real number")
    for bad in ("1.0", True):
        rejects(lambda bad=bad: p1c._req_finite("probe", bad),
                f"the frozen law also rejects {bad!r} (parity confirmed)",
                "finite real number")


def test_mechanism_2_matched_selection():
    group("mechanism 2: matched two-action selection")
    world = synthetic_world()
    menu = [candidate(0, 0, 0.2, 0.60, 0.20, 0.20),
            candidate(0, 4, 1.0, 0.60, 1.00, 1.00),
            candidate(1, 0, 0.2, 0.55, 0.18, 0.18),
            candidate(1, 4, 1.0, 0.55, 0.90, 0.90)]

    picked = lh.select_matched_non_ebu(menu, m=2)
    check(len(picked) == 2, "non-EBU comparator selects two actions")
    check({c["edge"] for c in picked} == {0, 1}, "one action per distinct edge")
    check(all(c["quant_index"] == 4 for c in picked),
          "ties on f broken by larger q_acc, as the frozen key does")
    check([c["edge"] for c in picked] == [0, 1],
          "returned in ascending edge order for shaping")

    single = lh.select_matched_non_ebu(menu, m=1)
    check(len(single) == 1 and single[0]["edge"] == 0 and
          single[0]["quant_index"] == 4,
          "m=1 reproduces the frozen select_arm_B choice (highest f, then q_acc)")

    quotes = [0.10, 0.40, 0.05, 0.90]
    ebu = lh.select_exact_ebu(menu, quotes, m=2)
    check([c["edge"] for c in ebu] == [0, 1], "exact-EBU arm picks both edges")
    check([c["quant_index"] for c in ebu] == [4, 4],
          "exact-EBU arm picks the highest exact quote per edge")
    negative = lh.select_exact_ebu(menu, [-1.0, -2.0, -3.0, -4.0], m=2)
    check(negative == (), "non-positive exact quotes are declined, as arm D does")
    mixed = lh.select_exact_ebu(menu, [0.0, 0.0, 0.0, 0.7], m=2)
    check(len(mixed) == 1 and mixed[0]["edge"] == 1,
          "only strictly positive exact quotes are acted on")

    demand = (0.0, 1.0, 0.0)
    blind = lh.select_stock_blind(menu, world, demand, m=2)
    check(len(blind) == 1 and blind[0]["edge"] == 0,
          "stock-blind control acts only toward a currently demanding "
          "destination")
    both = lh.select_stock_blind(menu, world, (0.0, 1.0, 1.0), m=2)
    check([c["edge"] for c in both] == [0, 1],
          "stock-blind control takes both edges when both destinations demand")
    none = lh.select_stock_blind(menu, world, (0.0, 0.0, 0.0), m=2)
    check(none == (), "stock-blind control rests when nothing demands")

    group("mechanism 2: the arms are matched by construction")
    shared = inspect.getsource(lh.select_actions)
    for name, function in (("non-EBU", lh.select_matched_non_ebu),
                           ("exact-EBU", lh.select_exact_ebu),
                           ("stock-blind", lh.select_stock_blind)):
        body = inspect.getsource(function)
        check("select_actions(" in body,
              f"{name} arm delegates to the shared selector")
    check("sorted(" in shared, "one shared ranking path for every arm")

    def code_of(function):
        """The function's AST with its docstring removed (code, not prose)."""
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        body = tree.body[0].body
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            body = body[1:]
        return ast.Module(body=body, type_ignores=[])

    def keys_read(function):
        return {n.slice.value for n in ast.walk(code_of(function))
                if isinstance(n, ast.Subscript)
                and isinstance(n.slice, ast.Constant)
                and isinstance(n.slice.value, str)}

    non_ebu_keys = keys_read(lh.select_matched_non_ebu)
    check(non_ebu_keys <= {"f", "q_acc"},
          f"matched comparator reads only the physical menu keys {sorted(non_ebu_keys)}")
    check(not any(term in key for key in non_ebu_keys
                  for term in ("quote", "exact", "ebu", "delta")),
          "matched comparator never reads an EBU-valued field")
    check(any(isinstance(n, ast.Div)
              for n in ast.walk(code_of(lh.select_exact_ebu))) is False,
          "exact-EBU arm performs no division: no per-unit value is formed")
    check("q_req" not in keys_read(lh.select_exact_ebu),
          "exact-EBU arm never reads a quantity to normalise a quote by")

    group("mechanism 2: determinism and fail-closed")
    first = lh.select_matched_non_ebu(menu, m=2)
    second = lh.select_matched_non_ebu(list(reversed(menu)), m=2)
    check([c["edge"] for c in first] == [c["edge"] for c in second] and
          [c["quant_index"] for c in first] == [c["quant_index"] for c in second],
          "selection is independent of menu order")
    rejects(lambda: lh.select_actions(menu, lambda c: 1.0, m=3),
            "rejects m above the adopted bound", "bound")
    rejects(lambda: lh.select_actions(menu, lambda c: 1.0,
                                      ranking_basis="joint_objective"),
            "rejects an unimplemented ranking basis", "not provided")
    rejects(lambda: lh.select_actions(
        menu, lambda c: (1.0,) if c["edge"] == 0 else (1.0, 2.0)),
        "rejects score keys of non-uniform arity", "uniform arity")

    # A score callable is evaluated exactly once per candidate, so it cannot
    # change the answer between ranking and the positivity filter.
    calls = []

    def counting(c):
        calls.append(c["edge"])
        return float(c["f"])

    lh.select_actions(menu, counting, m=2)
    check(len(calls) == len(menu),
          f"each candidate's score is evaluated exactly once "
          f"({len(calls)} calls for {len(menu)} candidates)")
    rejects(lambda: lh.select_exact_ebu(menu, quotes[:2]),
            "rejects a quote/candidate length mismatch", "mismatch")
    rejects(lambda: lh.select_exact_ebu(menu, [1.0, 2.0, 3.0, float("nan")]),
            "rejects a non-finite quote", "finite")
    rejects(lambda: lh.select_stock_blind(menu, world, (0.0, 1.0)),
            "rejects a demand vector of the wrong length", "length")
    check(lh.select_actions([], lambda c: 1.0) == (),
          "an empty menu selects nothing (explicit rest)")


def test_mechanism_3_shaping_identity():
    group("mechanism 3: generalized request-shaping identity")
    world = synthetic_world()
    cfg = synthetic_config()
    dt = 0.02
    x, u = 1.15, 0.98
    _state, budget = lh.source_budget_rate(cfg, x, u, dt)

    a = candidate(0, 4, 1.0, 0.60, 0.7 * budget, 0.7 * budget)
    b = candidate(1, 2, 0.6, 0.55, 0.5 * budget, 0.5 * budget)
    shaped = lh.shaped_active_world(world, [a, b])
    check(shaped.cells is world.cells,
          "shaped world passes cells through by identity (step contract)")
    check(len(shaped.edges) == 2, "one shaped edge per selected action")
    check(close(shaped.edges[0].M, 1.0 * world.edges[0].M) and
          close(shaped.edges[1].M, 0.6 * world.edges[1].M),
          "mobility scaled by each action's declared fraction")
    check([e.j for e in shaped.edges] == [1, 2], "edges in ascending index order")
    check(all(shaped.edges[k].theta == world.edges[k].theta and
              shaped.edges[k].eta == world.edges[k].eta for k in (0, 1)),
          "theta and eta are untouched by shaping")

    rest = lh.shaped_active_world(world, [])
    check(rest.edges == () and rest.cells is world.cells,
          "an empty selection shapes an explicit rest tick")
    check(all(0.0 < c["frac"] <= 1.0 for c in (a, b)),
          "shaping fractions stay within the physical edge")

    # Shaping preserves the force and scales the request, as the frozen
    # single-action shaping asserts.
    views = tuple(d0.local_view(c, v)
                  for c, v in zip(world.cells, (x, 0.2, 0.3)))
    f_full, j_full = d0.edge_flux(views[0], views[1], world.edges[0])
    f_shaped, j_shaped = d0.edge_flux(views[0], views[1],
                                      d0.Edge(i=0, j=1, M=0.6 * 10.0,
                                              theta=0.1, eta=0.9))
    check(f_shaped == f_full, "mobility scaling does not change the force")
    check(close(j_shaped, 0.6 * j_full), "mobility scaling scales the request")

    allocation = lh.joint_budget_cap(world, cfg, x, u, dt, [a, b])
    lh.check_request_shaping_identity([a, b], allocation, allocation.q_acc)
    default = inspect.signature(
        lh.check_request_shaping_identity).parameters["tolerance"].default
    check(default == 0.0,
          "the identity defaults to exact equality, never a silent tolerance")
    nudged = (allocation.q_acc[0] * (1 + 2 ** -52) + 5e-324,
              allocation.q_acc[1])
    rejects(lambda: lh.check_request_shaping_identity([a, b], allocation,
                                                      nudged),
            "the default tolerance rejects even a one-ulp divergence",
            "identity violated")

    group("mechanism 3: fail-closed")
    rejects(lambda: lh.check_request_shaping_identity(
        [a, b], allocation, allocation.q_acc[:1]),
        "rejects a wrong executed cardinality", "executed 1 actions")
    perturbed = (allocation.q_acc[0] + 1e-9, allocation.q_acc[1])
    rejects(lambda: lh.check_request_shaping_identity([a, b], allocation,
                                                      perturbed),
            "rejects a perturbed executed quantity", "identity violated")
    swapped = (allocation.q_acc[1], allocation.q_acc[0])
    rejects(lambda: lh.check_request_shaping_identity([a, b], allocation,
                                                      swapped),
            "rejects swapped quantities between edges", "identity violated")
    rejects(lambda: lh.shaped_active_world(
        world, [a, candidate(0, 1, 0.4, 0.6, 0.1, 0.1)]),
        "rejects shaping two actions onto one edge", "distinct")
    rejects(lambda: lh.shaped_active_world(
        world, [candidate(7, 0, 1.0, 0.6, 0.1, 0.1)]),
        "rejects an out-of-range edge index", "out of range")
    rejects(lambda: lh.check_request_shaping_identity([a, b], "nope",
                                                      allocation.q_acc),
            "rejects a non-JointAllocation", "JointAllocation")
    single = lh.joint_budget_cap(world, cfg, x, u, dt, [a])
    lh.check_request_shaping_identity([a], single, single.q_acc)
    check(len(single.q_acc) == 1,
          "m=1 identity still holds, matching the frozen assertion")
    rejects(lambda: lh.shaped_active_world(
        world, [candidate(0, 0, 5.0, 0.6, 1.0, 1.0)]),
        "rejects frac > 1: a restricted arm cannot out-mobilise the edge",
        "(0, 1]")
    rejects(lambda: lh.shaped_active_world(
        world, [candidate(0, 0, 0.0, 0.6, 1.0, 1.0)]),
        "rejects frac = 0 as a MechanismError, not a downstream error",
        "(0, 1]")


def test_mechanism_4_checkpoint_restart():
    group("mechanism 4: checkpoint and restart")
    digest = lh.config_digest({"study": "mechanism-ladder", "m": 2, "F": 5})
    check(len(digest) == 64, "config digest is a SHA-256 hex string")
    check(digest == eq.commitment_hash({"F": 5, "m": 2,
                                        "study": "mechanism-ladder"}),
          "digest uses the committed canonical hashing path, key-order stable")

    first = lh.make_checkpoint("LH-N", digest, 240, (1.15, 0.2, 0.3))
    second = lh.make_checkpoint("LH-N", digest, 580, (1.06, 0.3, 0.4),
                                prior=first)
    third = lh.make_checkpoint("LH-N", digest, 920, (1.05, 0.35, 0.45),
                               prior=second)
    check(first.sequence == 0 and first.prior_digest is None,
          "a fresh attempt starts at sequence 0 with no predecessor")
    check(second.prior_digest == first.digest and second.sequence == 1,
          "each link commits to its predecessor's digest")
    lh.verify_chain([first, second, third])
    check(True, "an intact chain verifies")

    next_tick, state, last = lh.resume_from([first, second, third], "LH-N",
                                            digest)
    check(next_tick == 921 and state == (1.05, 0.35, 0.45)
          and last is third,
          "resume continues at the tick after the last checkpoint")

    group("mechanism 4: a restart must not become a rerun")
    rejects(lambda: lh.make_checkpoint("LH-N", digest, 580, (1.0,),
                                       prior=second),
            "rejects a checkpoint that does not advance the tick",
            "does not advance")
    rejects(lambda: lh.make_checkpoint("LH-N", digest, 100, (1.0,),
                                       prior=second),
            "rejects a rewound tick", "does not advance")
    rejects(lambda: lh.make_checkpoint("LH-X", digest, 900, (1.0,),
                                       prior=second),
            "rejects a changed study_id", "same attempt")
    other = lh.config_digest({"study": "mechanism-ladder", "m": 2, "F": 4})
    rejects(lambda: lh.make_checkpoint("LH-N", other, 900, (1.0,),
                                       prior=second),
            "rejects a changed configuration digest", "different study")

    tampered = lh.Checkpoint(
        schema=second.schema, study_id=second.study_id,
        config_digest=second.config_digest, sequence=second.sequence,
        tick=second.tick, state=(9.9, 9.9, 9.9),
        prior_digest=second.prior_digest, digest=second.digest)
    rejects(lambda: lh.verify_chain([first, tampered, third]),
            "detects a record altered after it was written", "digest mismatch")
    forked = lh.make_checkpoint("LH-N", digest, 580, (2.0, 0.1, 0.1),
                                prior=first)
    rejects(lambda: lh.verify_chain([first, second, forked]),
            "detects a forked chain", "sequence")
    rejects(lambda: lh.verify_chain([first, third]),
            "detects a missing link", "sequence")
    rejects(lambda: lh.verify_chain([]), "rejects an empty chain", "empty")
    rejects(lambda: lh.resume_from([first, second], "LH-H", digest),
            "refuses to resume another study's chain", "cannot resume")
    rejects(lambda: lh.resume_from([first, second], "LH-N", other),
            "refuses to resume under an altered configuration",
            "different study")
    rejects(lambda: lh.make_checkpoint("LH-N", "short", 1, (1.0,)),
            "rejects a malformed config digest", "64-character")
    rejects(lambda: lh.make_checkpoint("", digest, 1, (1.0,)),
            "rejects an empty study_id", "non-empty")
    rejects(lambda: lh.make_checkpoint("LH-N", digest, 1, ()),
            "rejects an empty state", "non-empty")
    rejects(lambda: lh.make_checkpoint("LH-N", digest, 1,
                                       (float("inf"),)),
            "rejects a non-finite state value", "finite")
    check(lh.make_checkpoint("LH-N", digest, 240, (1.15, 0.2, 0.3)).digest
          == first.digest,
          "checkpoint digests are deterministic")


def test_fidelity_to_the_frozen_selectors():
    """At m=1 the generalized selectors must BE the frozen ones.

    ``gate1dc_v30`` is imported here, inside the test, rather than by
    ``longhorizon_v30``: it builds and validates its locked plan at module
    scope, so it is not import-pure. Importing it performs read-only plan
    validation and calls no step, tick, runner or trajectory function -
    ``test_v30_gate1dc.py`` imports it the same way.
    """
    import itertools
    import gate1dc_v30 as dc

    group("fidelity: m=1 reproduces select_arm_B over a tie-saturated sweep")
    grid = (0.0, 0.25, 0.5)
    divergences = 0
    menus = 0
    for values in itertools.product(grid, repeat=4):
        menu = [candidate(0, 0, 1.0, values[0], 1.0, values[1]),
                candidate(0, 1, 1.0, values[1], 1.0, values[0]),
                candidate(1, 0, 1.0, values[2], 1.0, values[3]),
                candidate(1, 1, 1.0, values[3], 1.0, values[2])]
        menus += 1
        mine = lh.select_matched_non_ebu(menu, m=1)
        frozen = dc.select_arm_B(menu)
        if (mine[0] if mine else None) is not frozen:
            divergences += 1
    check(divergences == 0,
          f"arm B: {menus} tie-saturated menus, {divergences} divergences")

    group("fidelity: m=1 reproduces select_arm_D and select_arm_S")
    menu = [candidate(0, 0, 0.5, 0.60, 0.5, 0.5),
            candidate(0, 1, 1.0, 0.60, 1.0, 1.0),
            candidate(1, 0, 0.5, 0.55, 0.5, 0.5),
            candidate(1, 1, 1.0, 0.55, 1.0, 1.0)]
    quote_values = (-1.0, -0.0, 0.0, 0.5, 1.0)
    divergences = 0
    combos = 0
    for quotes in itertools.product(quote_values, repeat=4):
        combos += 1
        mine = lh.select_exact_ebu(menu, list(quotes), m=1)
        index = dc.select_arm_D(menu, list(quotes))
        frozen = menu[index] if index is not None else None
        if (mine[0] if mine else None) is not frozen:
            divergences += 1
    check(divergences == 0,
          f"arm D: {combos} quote vectors incl. -0.0 and ties, "
          f"{divergences} divergences")

    world = synthetic_world()
    divergences = 0
    cases = 0
    for demand in itertools.product((0.0, 1.0), repeat=2):
        rates = (0.0,) + demand
        for values in itertools.product((0.0, 0.5, 1.0), repeat=2):
            probe = [candidate(0, 0, 1.0, 0.6, 1.0, values[0]),
                     candidate(0, 1, 1.0, 0.6, 1.0, values[1]),
                     candidate(1, 0, 1.0, 0.5, 1.0, values[1]),
                     candidate(1, 1, 1.0, 0.5, 1.0, values[0])]
            cases += 1
            mine = lh.select_stock_blind(probe, world, rates, m=1)
            frozen = dc.select_arm_S(probe, rates, world)
            if (mine[0] if mine else None) is not frozen:
                divergences += 1
    check(divergences == 0,
          f"arm S: {cases} demand/menu cases, {divergences} divergences")

    group("fidelity: shaping reproduces the frozen single-action shaping")
    divergences = 0
    for edge_index in (0, 1):
        for fraction in dc.FRACTIONS:
            one = candidate(edge_index, 0, fraction, 0.6, 1.0, 1.0)
            mine = lh.shaped_active_world(world, [one])
            frozen = dc.shaped_active_world(world, one)
            if mine.edges != frozen.edges or mine.cells is not frozen.cells:
                divergences += 1
    check(divergences == 0,
          "shaped edges identical to gate1dc_v30.shaped_active_world for "
          "every registered fraction on every edge")
    rest_mine = lh.shaped_active_world(world, [])
    rest_frozen = dc.shaped_active_world(world, None)
    check(rest_mine.edges == rest_frozen.edges == (),
          "the empty selection matches the frozen rest tick")

    group("fidelity: the frozen single-action assertion is subsumed")
    cfg = synthetic_config()
    one = candidate(0, 0, 1.0, 0.6, 1.0, 1.0)
    allocation = lh.joint_budget_cap(world, cfg, 1.15, 0.98, 0.02, [one])
    lh.check_request_shaping_identity([one], allocation, allocation.q_acc)
    check(len(allocation.q_acc) == 1,
          "m=1 yields exactly one accepted quantity, as gate1dc asserts")
    rejects(lambda: lh.check_request_shaping_identity(
        [one], allocation, (allocation.q_acc[0], 0.0)),
        "two executed quantities for one selected action are refused",
        "identity violated")


def test_adopted_constants_and_arm_roles():
    group("adopted constants and arm roles")
    check(lh.M_MAX == 2, "simultaneous-action bound is the adopted m = 2")
    check(len(lh.ADOPTED_ARMS) == 4 and len(set(lh.ADOPTED_ARMS)) == 4,
          "exactly four distinct adopted arms")
    check(lh.ADOPTED_ARMS[0] == "A_full_multi_edge_p1c",
          "first arm is the full-capability reference")
    check(set(lh.RESTRICTED_ARMS) == set(lh.ADOPTED_ARMS[1:]),
          "the other three are restricted policies sharing one menu")
    check(set(lh.ARM_ROLES) == set(lh.ADOPTED_ARMS),
          "every adopted arm has a declared role")
    check(lh.ARM_ROLES["S_restricted_local_service_priority"]
          == "stock-blind control",
          "arm S is the registered stock-blind control")
    check(lh.RANKING_BASIS == "menu_rank_then_joint_cap",
          "the selection semantics is named and single-valued")

    # The module hardcodes arm identifiers because importing gate1dc_v30 is
    # not import-pure. Verify them against the locked plan by static read.
    with open("v30_gate1dc_outcome_discrimination_plan.json",
              encoding="utf-8") as handle:
        plan = json.load(handle)
    registered = set(plan["arms"])
    check(set(lh.ADOPTED_ARMS) <= registered,
          "every adopted arm identifier appears verbatim in the locked plan")
    blind = plan["arms"]["S_restricted_local_service_priority"]
    check("stock-blind" in blind and "positive-control" in blind,
          "the locked plan confirms arm S is the stock-blind positive control")
    check("C_restricted_observational_quote" not in lh.ADOPTED_ARMS
          and "E_aggregate_source_group_quote" not in lh.ADOPTED_ARMS,
          "no unadopted registered arm is smuggled in")

    # Behavioural, not prose: the module must not reach for any EBU
    # construction the adopted mathematics forbids.
    source_tree = ast.parse(inspect.getsource(lh))
    attributes = {n.attr for n in ast.walk(source_tree)
                  if isinstance(n, ast.Attribute)}
    for forbidden in ("build_quote", "QuoteSchedule", "EpochRegistry",
                      "settle", "register", "exact", "linear_diagnostic"):
        check(forbidden not in attributes,
              f"module never reaches for {forbidden} (EBU is caller-supplied)")
    divisions = [n for n in ast.walk(source_tree) if isinstance(n, ast.Div)]
    check(len(divisions) == 2,
          f"exactly two divisions exist, both frozen-rule rates "
          f"(found {len(divisions)})")
    check(lh.joint_budget_cap.__doc__ and "PROPORTIONAL"
          in lh.joint_budget_cap.__doc__,
          "the joint cap documents that it scales, never clamps independently")


def main() -> int:
    test_execution_safety_and_import_purity()
    test_mechanism_1_joint_budget_cap()
    test_mechanism_2_matched_selection()
    test_mechanism_3_shaping_identity()
    test_mechanism_4_checkpoint_restart()
    test_fidelity_to_the_frozen_selectors()
    test_adopted_constants_and_arm_roles()
    print(f"\nLong-horizon mechanisms: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
