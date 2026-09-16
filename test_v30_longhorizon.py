"""Long-horizon mechanism validation; static and pure-function only.

This suite MUST NOT call a model step, a runner, a simulation, a trajectory,
a multi-tick loop, ``p1c_v29.p1c_step``, ``service_v30.bounded_step``, or any
tick function.  Every check below is an isolated pure-function evaluation on a
frozen synthetic state, or a static source/AST inspection.

It validates the prospective mechanisms, their fail-closed behaviour, their
agreement with the published P1C rule and with the frozen single-action
selectors, and the module's execution-safety guarantees.
"""
from __future__ import annotations

import ast
import inspect
import json
import math
import os
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


def synthetic_world_three_edges():
    """The same source with THREE out-edges, for set-scoring probes only.

    With only two out-edges every permitted pair carries the same force
    multiset, so descending-lexicographic, sum, maximum and average rank the
    pairs identically and no probe could tell them apart. A third edge is the
    smallest topology in which the declared rule is falsifiable. It is a
    mechanism fixture, not a study configuration: the proposed families
    declare one source with two out-edges.
    """
    base = synthetic_world()
    third = d0.Cell(alpha=0.6, beta=1.0, chi=0.0, L=1.0, U=4.0, R=0.0,
                    K=6.0, s=0.0, d=0.25, lam=0.0, kappa=0.0,
                    source="none", rho=0.0, A=0.0)
    return d0.World(cells=base.cells + (third,),
                    edges=base.edges + (d0.Edge(i=0, j=3, M=10.0, theta=0.1,
                                                eta=0.9),))


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
    check(imported == {"__future__", "itertools", "json", "math", "os",
                       "dataclasses", "typing", "d0_v29", "p1c_v29",
                       "ebu_quote_v30"},
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
            "rejects m above the prospective bound", "bound")
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


def test_mechanism_2_set_enumeration_and_joint_ebu():
    group("mechanism 2: action-set enumeration")
    world = synthetic_world()
    cfg = synthetic_config()
    dt = 0.02
    x = (1.15, 0.2, 0.3)
    u = (0.98, -0.25, -0.25)
    _state, budget = lh.source_budget_rate(cfg, x[0], u[0], dt)
    # Sized against the budget so singletons fit but pairs must be scaled:
    # that is the regime the joint cap exists for.
    menu = [candidate(0, 0, 0.5, 0.60, 0.30 * budget, 0.30 * budget),
            candidate(0, 1, 1.0, 0.60, 0.70 * budget, 0.70 * budget),
            candidate(1, 0, 0.5, 0.55, 0.35 * budget, 0.35 * budget),
            candidate(1, 1, 1.0, 0.55, 0.80 * budget, 0.80 * budget)]

    sets = lh.enumerate_action_sets(menu, m=2)
    check(len(sets) == 4 + 4, "2 edges x 2 rungs gives 4 singletons + 4 pairs")
    check(all(len(g) <= 2 for g in sets), "no set exceeds the bound m = 2")
    check(all(len({int(c["edge"]) for c in g}) == len(g) for g in sets),
          "every set obeys the distinct-edge rule")
    check(all(tuple(int(c["edge"]) for c in g)
              == tuple(sorted(int(c["edge"]) for c in g)) for g in sets),
          "each set is ordered by ascending edge index")
    sizes = [len(g) for g in sets]
    check(sizes == sorted(sizes), "sets are ordered by size, then identifiers")
    again = lh.enumerate_action_sets(list(reversed(menu)), m=2)
    check([[(int(c["edge"]), int(c["quant_index"])) for c in g] for g in sets]
          == [[(int(c["edge"]), int(c["quant_index"])) for c in g]
              for g in again],
          "enumeration is independent of menu order")
    check(len(lh.enumerate_action_sets(menu, m=1)) == 4,
          "m = 1 enumerates singletons only")
    check(() not in sets, "rest is not enumerated; it is the act-condition "
                          "fallback")

    group("mechanism 2: exact joint EBU equals the frozen quote path")
    # Single action: the joint form must agree with ebu_quote_v30's exact
    # finite endpoint difference, which is the governing authority.
    lam_l = 0.5
    for edge_index in (0, 1):
        for quantity in (0.05, 0.2, 0.4):
            joint = lh.joint_exact_ebu(world, x, u, dt, (edge_index,),
                                       (quantity,), lam_l)
            spec = world.edges[edge_index]
            cost = eq.ProcessCost(category=eq.ALLOWED_COST_CATEGORY, c0=0.0,
                                  c1=lam_l * dt * (1.0 - spec.eta))
            inp = eq.LocalQuoteInput(
                src=d0.local_view(world.cells[spec.i], x[spec.i]),
                dst=d0.local_view(world.cells[spec.j], x[spec.j]),
                u_src=u[spec.i], u_dst=u[spec.j], dt=dt, eta=spec.eta,
                q_req=quantity, q_acc=quantity, source_id=spec.i,
                dest_id=spec.j, config_id="probe")
            schedule = eq.build_quote(inp, cost, "probe-pass", 0, 0)
            check(close(joint.group_quote, schedule.exact(quantity), 1e-12),
                  f"edge {edge_index} q={quantity}: joint form equals "
                  f"QuoteSchedule.exact")
            check(close(joint.naive_sum, joint.group_quote, 1e-12)
                  and close(joint.double_count, 0.0, 1e-12),
                  f"edge {edge_index} q={quantity}: one action has zero "
                  f"double_count by construction")

    group("mechanism 2: the joint transition is counted once")
    pair = lh.joint_exact_ebu(world, x, u, dt, (0, 1), (0.2, 0.15), lam_l)
    single_a = lh.joint_exact_ebu(world, x, u, dt, (0,), (0.2,), lam_l)
    single_b = lh.joint_exact_ebu(world, x, u, dt, (1,), (0.15,), lam_l)
    check(close(pair.naive_sum, single_a.group_quote + single_b.group_quote,
                1e-12),
          "naive_sum is exactly the sum of independently frozen per-edge "
          "quotes")
    check(close(pair.double_count, pair.naive_sum - pair.group_quote, 1e-15),
          "double_count = naive_sum - group_quote, as registered")
    check(pair.n_actions == 2, "the action count is recorded")
    check(abs(pair.double_count) > 0.0,
          "a shared source makes the interaction term non-zero here")
    check(pair.naive_sum >= pair.group_quote - 1e-12,
          "naive_sum >= group_quote on this state (registered expected sign)")
    empty = lh.joint_exact_ebu(world, x, u, dt, (), (), lam_l)
    check(empty.group_quote == 0.0 and empty.naive_sum == 0.0
          and empty.double_count == 0.0 and empty.n_actions == 0,
          "rest quotes exactly zero on every field")

    group("mechanism 2: ranked value IS the executed value")
    evaluations = lh.evaluate_action_sets(world, cfg, x, u, dt, menu, lam_l,
                                          m=2)
    check(len(evaluations) == len(sets),
          "every enumerated set is capped and quoted")
    # Falsifiable: for every BOUND set the recorded quote must equal the
    # capped-vector quote and must DIFFER from the requested-vector quote.
    # A regression that quoted the request would fail the second clause.
    bound_checked = 0
    mismatch = 0
    for evaluation in evaluations:
        requested = tuple(float(c["q_req"]) for c in evaluation.actions)
        capped = lh.joint_exact_ebu(world, x, u, dt, evaluation.edges,
                                    evaluation.allocation.q_acc, lam_l)
        asked = lh.joint_exact_ebu(world, x, u, dt, evaluation.edges,
                                   requested, lam_l)
        if evaluation.quote.group_quote != capped.group_quote:
            mismatch += 1
        if evaluation.allocation.binding:
            bound_checked += 1
            if evaluation.quote.group_quote == asked.group_quote:
                mismatch += 1
            if evaluation.allocation.q_acc == requested:
                mismatch += 1
    check(mismatch == 0 and bound_checked > 0,
          f"every set is quoted on its capped vector, and on all "
          f"{bound_checked} bound sets that differs from the requested "
          f"vector's quote")
    binding = [e for e in evaluations if e.allocation.binding]
    check(binding, "at least one enumerated set is budget-bound on this state")
    for evaluation in binding:
        requested = math.fsum(float(c["q_req"]) for c in evaluation.actions)
        check(evaluation.allocation.accepted_total < requested,
              "a bound set executes strictly less than it requested")
        break

    group("mechanism 2: the exact-EBU arm selects on the joint value")
    chosen = lh.select_exact_ebu_joint(evaluations)
    check(chosen is not None, "a strictly positive joint quote is acted on")
    best = max(e.quote.group_quote for e in evaluations)
    check(chosen.quote.group_quote == best,
          "the selected set maximises the exact joint EBU of what executes")
    check(all(not isinstance(n, ast.Div) for n in ast.walk(
              ast.parse(textwrap.dedent(
                  inspect.getsource(lh.select_exact_ebu_joint))))),
          "the exact-EBU arm performs no division: per-unit ranking (F8) "
          "cannot occur")

    # Act condition: rest unless strictly positive.
    negative = tuple(
        lh.SetEvaluation(actions=e.actions, allocation=e.allocation,
                         quote=lh.JointQuote(-1.0, -1.0, 0.0,
                                             e.quote.n_actions))
        for e in evaluations)
    check(lh.select_exact_ebu_joint(negative) is None,
          "rests when no set has a strictly positive joint quote")
    zeroed = tuple(
        lh.SetEvaluation(actions=e.actions, allocation=e.allocation,
                         quote=lh.JointQuote(0.0, 0.0, 0.0,
                                             e.quote.n_actions))
        for e in evaluations)
    check(lh.select_exact_ebu_joint(zeroed) is None,
          "a zero joint quote is not strictly positive, so it rests")
    check(lh.select_exact_ebu_joint(()) is None,
          "an empty enumeration rests")

    group("mechanism 2: deterministic identifier tie-breaking")
    tied = tuple(
        lh.SetEvaluation(actions=e.actions, allocation=e.allocation,
                         quote=lh.JointQuote(1.0, 1.0, 0.0,
                                             e.quote.n_actions))
        for e in evaluations)
    winner = lh.select_exact_ebu_joint(tied)
    check(len(winner.actions) == 1,
          "on an exact tie the singleton wins because its edge tuple is a "
          "prefix, not because any cardinality preference is imposed")
    check(winner.edges == (0,) and winner.quant_indices == (0,),
          "then the lowest edge index, then the lowest quantity-menu index")
    shuffled = lh.select_exact_ebu_joint(tuple(reversed(tied)))
    check(shuffled.edges == winner.edges
          and shuffled.quant_indices == winner.quant_indices,
          "tie-breaking is independent of evaluation order")

    group("mechanism 2: arms are matched, and unregistered scores fail closed")
    shared = inspect.getsource(lh.select_set_by_declared_score)
    check("select_set_by_declared_score(" in inspect.getsource(
              lh.select_exact_ebu_joint),
          "the exact-EBU arm routes through the shared set selector")
    for name, function in (("matched non-EBU", lh.select_matched_non_ebu_joint),
                           ("stock-blind", lh.select_stock_blind_joint)):
        body = inspect.getsource(function)
        calls = {n.func.id for n in ast.walk(ast.parse(textwrap.dedent(body)))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        check(calls & {"select_set_by_declared_score"}
              and not (calls & {"_select_by_tuple_score"}),
              f"the {name} arm calls ONLY the shared set selector")
    check(not hasattr(lh, "_select_by_tuple_score"),
          "there is exactly one selector, so no arm can acquire a different "
          "tie discipline")
    check("edges" in shared and "quant_indices" in shared,
          "tie-breaking uses identifiers only, in the shared path")

    # The divergence a second selector would have caused: an f-tie must be
    # broken by the larger accepted quantity, as the frozen key requires.
    tie_world = synthetic_world()
    tie_cfg = synthetic_config()
    _st, tie_budget = lh.source_budget_rate(tie_cfg, x[0], u[0], dt)
    tie_menu = [candidate(0, 0, 1.0, 0.5, 0.02 * tie_budget, 0.0),
                candidate(1, 0, 1.0, 0.5, 0.09 * tie_budget, 0.0)]
    tie_evals = lh.evaluate_action_sets(tie_world, tie_cfg, x, u, dt,
                                        tie_menu, lam_l, m=1)
    tie_pick = lh.select_matched_non_ebu_joint(tie_evals)
    check(tie_pick.edges == (1,),
          "on an f-tie the larger accepted quantity wins, as select_arm_B "
          "requires")

    check(issubclass(lh.UnregisteredScoringRule, lh.MechanismError),
          "an out-of-invariant scoring case is a fail-closed MechanismError")
    # An explicitly registered override still routes through one selector.
    supplied = lh.select_matched_non_ebu_joint(
        evaluations, set_score=lambda e: math.fsum(
            float(c["f"]) for c in e.actions))
    check(supplied is not None,
          "a caller-registered set score is accepted through the shared path")

    group("mechanism 2: the DECLARED set-level score for arm B")
    check(lh.DECLARED_SET_SCORES["B_restricted_matched_non_ebu"].startswith(
              "DECLARED."),
          "arm B's set score is recorded as declared, never as derived")
    check(lh.DECLARED_SET_SCORES[
              "D_restricted_exact_total_quote_greedy"].startswith("DERIVED."),
          "the exact-EBU arm's set score is recorded as derived")
    # Descending lexicographic over member forces: (0.9, 0.1) beats (0.8, 0.8)
    # even though the second set has the larger total force.
    # One force per EDGE, as the frozen menu builds it. Three out-edges is the
    # smallest topology where pairs differ in their force multiset at all.
    lex_world = synthetic_world_three_edges()
    lex_x, lex_u = x + (0.3,), u + (-0.25,)
    lex = [candidate(0, 0, 1.0, 0.9, 0.02 * budget, 0.02 * budget),
           candidate(1, 0, 1.0, 0.1, 0.02 * budget, 0.02 * budget),
           candidate(2, 0, 1.0, 0.8, 0.02 * budget, 0.02 * budget)]
    lex_evals = lh.evaluate_action_sets(lex_world, cfg, lex_x, lex_u, dt, lex,
                                        lam_l, m=2)
    lex_pick = lh.select_matched_non_ebu_joint(lex_evals, m=2)
    check(lex_pick.edges == (0, 2),
          "descending lexicographic picks (0.9, 0.8) over (0.9, 0.1) and "
          "(0.8, 0.1)")

    # How far the declared rule actually is from the three aggregations the
    # candidate document names as the alternatives. At m = 2, with one force
    # per edge and every force strictly positive, the lexicographic argmax is
    # the pair of the two largest forces - and so is the largest-total argmax,
    # because adding a positive force always raises a sum. They therefore
    # SELECT identically; only their induced rankings differ, and a ranking is
    # never used. Against maximum-of-set and average-of-set they diverge.
    # This narrows the registration gap rather than closing it.
    import itertools as _it
    same_as_sum = diff_from_max = diff_from_avg = 0
    grids = 0
    forces_grid = (0.2, 0.45, 0.5, 0.9, 1.3)
    for triple in _it.product(forces_grid, repeat=3):
        probe = [candidate(e, 0, 1.0, triple[e], 0.02 * budget,
                           0.02 * budget) for e in range(3)]
        probe_evals = lh.evaluate_action_sets(lex_world, cfg, lex_x, lex_u,
                                              dt, probe, lam_l, m=2)
        grids += 1
        declared = lh.select_matched_non_ebu_joint(probe_evals, m=2).edges
        by_sum = lh.select_matched_non_ebu_joint(
            probe_evals, set_score=lambda e: math.fsum(
                float(c["f"]) for c in e.actions)).edges
        by_max = lh.select_matched_non_ebu_joint(
            probe_evals, set_score=lambda e: max(
                float(c["f"]) for c in e.actions)).edges
        by_avg = lh.select_matched_non_ebu_joint(
            probe_evals, set_score=lambda e: math.fsum(
                float(c["f"]) for c in e.actions) / len(e.actions)).edges
        same_as_sum += declared == by_sum
        diff_from_max += declared != by_max
        diff_from_avg += declared != by_avg
    check(same_as_sum == grids,
          f"over {grids} force grids the declared rule selects EXACTLY what "
          f"largest-total selects ({same_as_sum}/{grids})")
    check(diff_from_max > 0 and diff_from_avg > 0,
          f"but differs from maximum-of-set ({diff_from_max} grids) and from "
          f"average-of-set ({diff_from_avg} grids)")

    # The lexicographic prefix rule: a pair extending a singleton's leading
    # force outranks it. Safe because every member force is strictly positive.
    check(all(float(a["f"]) > 0.0 for e in lex_evals for a in e.actions),
          "every member force in the probe is strictly positive")
    prefix_probe = tuple(e for e in lex_evals
                         if e.edges in ((0,), (0, 2)))
    check(len(prefix_probe) == 2
          and lh.select_matched_non_ebu_joint(prefix_probe, m=2).edges
          == (0, 2),
          "a pair extending a singleton's leading force outranks it (the "
          "lexicographic prefix rule)")
    check(lh.LEX_PAD == -math.inf,
          "the declared pad IS the prefix rule, so padding invents no order")

    # Accepted quantities are the NEXT tie level only, never the first.
    tie_forces = [candidate(0, 0, 1.0, 0.5, 0.02 * budget, 0.02 * budget),
                  candidate(1, 0, 1.0, 0.5, 0.09 * budget, 0.09 * budget)]
    tie_evals2 = lh.evaluate_action_sets(world, cfg, x, u, dt, tie_forces,
                                         lam_l, m=1)
    check(lh.select_matched_non_ebu_joint(tie_evals2, m=1).edges == (1,),
          "on an equal force the larger ACCEPTED quantity wins, as the "
          "declared next tie level")
    rejects(lambda: lh.select_matched_non_ebu_joint(
                lh.evaluate_action_sets(
                    world, cfg, x, u, dt,
                    [candidate(0, 0, 1.0, 0.0, 0.02 * budget,
                               0.02 * budget)], lam_l, m=1), m=1),
            "refuses a non-positive member force (outside the registered "
            "menu invariant)", "not strictly positive")
    rejects(lambda: lh.select_matched_non_ebu_joint(
                lh.evaluate_action_sets(
                    world, cfg, x, u, dt,
                    [{"edge": 0, "quant_index": 0, "frac": 1.0,
                      "q_req": 0.02 * budget}], lam_l, m=1), m=1),
            "refuses a menu with no force at all", "requires candidate key")

    group("mechanism 2: the DECLARED set-level score for arm S")
    check(lh.DECLARED_SET_SCORES[
              "S_restricted_local_service_priority"].startswith("DECLARED."),
          "arm S's set score is recorded as declared, never as derived")
    demand_all = (0.0, 1.0, 1.0, 1.0)
    demand_one = (0.0, 1.0, 0.0, 0.0)
    both = lh.select_stock_blind_joint(lex_evals, lex_world, demand_all)
    check(len(both.actions) == 2,
          "with every destination demanding, total delivered service prefers "
          "a two-action set")
    expected = math.fsum(lex_world.edges[e].eta * q for e, q
                         in zip(both.allocation.edges, both.allocation.q_acc))
    alternatives = []
    for evaluation in lex_evals:
        alternatives.append(math.fsum(
            lex_world.edges[e].eta * q for e, q
            in zip(evaluation.allocation.edges, evaluation.allocation.q_acc)))
    check(close(expected, max(alternatives)),
          "the winning set maximises sum(eta_e * q_acc_e) exactly")
    one = lh.select_stock_blind_joint(lex_evals, lex_world, demand_one)
    check(all(lex_world.edges[e].j == 1 for e in one.allocation.edges),
          "an edge to a zero-demand destination contributes nothing, so only "
          "the demanding destination's edge is chosen")
    check(lh.select_stock_blind_joint(lex_evals, lex_world,
                                      (0.0, 0.0, 0.0, 0.0)) is None,
          "with no demand anywhere the total is zero, so arm S rests")
    blind_tree = ast.parse(textwrap.dedent(
        inspect.getsource(lh.select_stock_blind_joint)))
    blind_names = {n.id for n in ast.walk(blind_tree)
                   if isinstance(n, ast.Name)}
    blind_attrs = {n.attr for n in ast.walk(blind_tree)
                   if isinstance(n, ast.Attribute)}
    for forbidden in ("quote", "group_quote", "penalty", "naive_sum",
                      "double_count"):
        check(forbidden not in blind_names and forbidden not in blind_attrs,
              f"the stock-blind control never reads {forbidden!r}")
    check("x" not in blind_names,
          "the stock-blind control never reads the state vector")
    rejects(lambda: lh.select_stock_blind_joint(lex_evals, lex_world,
                                                (0.0, 1.0)),
            "refuses a demand vector of the wrong length", "cell count")
    rejects(lambda: lh.select_stock_blind_joint(lex_evals, None, demand_all),
            "refuses to score without the world", "needs the world")
    rejects(lambda: lh.select_stock_blind_joint(lex_evals, lex_world, None),
            "refuses to score without declared demand rates", "demand rates")

    group("mechanism 2: fail-closed")
    rejects(lambda: lh.enumerate_action_sets(menu, m=3),
            "rejects m above the prospective bound", "bound")
    rejects(lambda: lh.enumerate_action_sets([{"edge": 0}]),
            "rejects a malformed candidate", "missing required key")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, dt, (0, 0), (0.1, 0.1),
                                       lam_l),
            "rejects repeated edges in one action vector", "distinct")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, dt, (0,), (0.1, 0.2),
                                       lam_l),
            "rejects an edges/accepted length mismatch", "mismatch")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, dt, (9,), (0.1,), lam_l),
            "rejects an out-of-range edge", "out of range")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, 0.0, (0,), (0.1,), lam_l),
            "rejects dt = 0", "dt must be > 0")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, dt, (0,), (-0.1,), lam_l),
            "rejects a negative accepted quantity", ">= 0")
    rejects(lambda: lh.joint_exact_ebu(world, x, u, dt, (0,), (0.1,), -1.0),
            "rejects a negative cost coefficient", ">= 0")
    rejects(lambda: lh.joint_exact_ebu(world, (1.0,), u, dt, (0,), (0.1,),
                                       lam_l),
            "rejects a state of the wrong length", "one entry per cell")
    rejects(lambda: lh.select_set_by_declared_score(["not an evaluation"],
                                                    lambda e: 1.0),
            "rejects a non-SetEvaluation", "SetEvaluation")


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
    rejects(lambda: lh.shaped_active_world(
        world, [candidate(0, 0, 1.0 + 2 ** -52, 0.6, 1.0, 1.0)]),
        "rejects a fraction one ulp above 1", "(0, 1]")

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
    """At m=1 with an unbinding budget, set selection IS the frozen selection.

    ``gate1dc_v30`` is imported here, inside the test, rather than by
    ``longhorizon_v30``: it builds and validates its locked plan at module
    scope, so it is not import-pure. Importing it performs read-only plan
    validation and calls no step, tick, runner or trajectory function -
    ``test_v30_gate1dc.py`` imports it the same way.
    """
    import itertools
    import gate1dc_v30 as dc

    world = synthetic_world()
    cfg = synthetic_config()
    dt = 0.02
    x = (1.15, 0.2, 0.3)
    u = (0.98, -0.25, -0.25)
    lam_l = 0.5
    _state, budget = lh.source_budget_rate(cfg, x[0], u[0], dt)

    group("fidelity: m=1 unbound reproduces select_arm_B over tie-saturated "
          "menus")
    # Strictly positive forces: the registered menu admits a candidate only
    # when J_e = M_e*[f_e - theta_e]_+ > 0 with theta_e >= 0, so f_e > 0 holds
    # for every real menu candidate, and the declared set rule is defined only
    # there. Three distinct values over four slots still saturates ties.
    grid = (0.25, 0.5, 0.75)
    # q_acc must be the accepted quantity, so it follows q_req. Every
    # singleton is unbound here, where menu q_acc and the joint-capped
    # allocation agree exactly (sigma == 1.0), which is what makes the frozen
    # comparison meaningful at all.
    quantities = tuple(0.01 * budget * (k + 1) for k in range(4))
    divergences = 0
    menus = 0
    for values in itertools.product(grid, repeat=4):
        menu = [candidate(0, 0, 1.0, values[0], quantities[0], quantities[0]),
                candidate(0, 1, 1.0, values[1], quantities[1], quantities[1]),
                candidate(1, 0, 1.0, values[2], quantities[2], quantities[2]),
                candidate(1, 1, 1.0, values[3], quantities[3], quantities[3])]
        menus += 1
        evaluations = lh.evaluate_action_sets(world, cfg, x, u, dt, menu,
                                              lam_l, m=1)
        mine = lh.select_matched_non_ebu_joint(evaluations)
        frozen = dc.select_arm_B(menu)
        picked = mine.actions[0] if mine else None
        if picked is not frozen:
            divergences += 1
    check(divergences == 0,
          f"arm B: {menus} tie-saturated menus with consistent quantities, "
          f"{divergences} divergences")
    check(all(not e.allocation.binding for e in lh.evaluate_action_sets(
              world, cfg, x, u, dt,
              [candidate(0, 0, 1.0, 0.5, quantities[0], quantities[0])],
              lam_l, m=1)),
          "the sweep runs in the unbound regime where menu and allocation "
          "agree exactly")

    group("fidelity: m=1 unbound reproduces select_arm_S")
    divergences = 0
    cases = 0
    for demand in itertools.product((0.0, 1.0), repeat=2):
        rates = (0.0,) + demand
        for values in itertools.product((0.005, 0.01, 0.02), repeat=2):
            a0, a1 = values[0] * budget, values[1] * budget
            probe = [candidate(0, 0, 1.0, 0.6, a0, a0),
                     candidate(0, 1, 1.0, 0.6, a1, a1),
                     candidate(1, 0, 1.0, 0.5, a1 * 1.5, a1 * 1.5),
                     candidate(1, 1, 1.0, 0.5, a0 * 1.5, a0 * 1.5)]
            cases += 1
            evaluations = lh.evaluate_action_sets(world, cfg, x, u, dt, probe,
                                                  lam_l, m=1)
            mine = lh.select_stock_blind_joint(evaluations, world, rates)
            frozen = dc.select_arm_S(probe, rates, world)
            picked = mine.actions[0] if mine else None
            if picked is not frozen:
                divergences += 1
    check(divergences == 0,
          f"arm S: {cases} demand/menu cases, {divergences} divergences")

    group("fidelity: m=1 unbound reproduces select_arm_D on the same quotes")
    menu = [candidate(0, 0, 0.25, 0.60, 0.05 * budget, 0.05 * budget),
            candidate(0, 1, 1.00, 0.60, 0.20 * budget, 0.20 * budget),
            candidate(1, 0, 0.25, 0.55, 0.06 * budget, 0.06 * budget),
            candidate(1, 1, 1.00, 0.55, 0.22 * budget, 0.22 * budget)]
    evaluations = lh.evaluate_action_sets(world, cfg, x, u, dt, menu, lam_l,
                                          m=1)
    check(all(not e.allocation.binding for e in evaluations),
          "every singleton is unbound at these quantities")
    quotes = [lh.joint_exact_ebu(world, x, u, dt, (int(c["edge"]),),
                                 (float(c["q_req"]),), lam_l).group_quote
              for c in menu]
    index = dc.select_arm_D(menu, quotes)
    frozen = menu[index] if index is not None else None
    mine = lh.select_exact_ebu_joint(evaluations)
    picked = mine.actions[0] if mine else None
    check(picked is frozen,
          "unbound m=1 exact-EBU selection equals select_arm_D on the same "
          "exact quotes")

    group("fidelity: the correction is visible exactly where it should be")
    # With a BINDING pair the ranked value and the executed value would have
    # differed under the superseded rule. Here they cannot.
    wide = [candidate(0, 1, 1.0, 0.60, 0.70 * budget, 0.70 * budget),
            candidate(1, 1, 1.0, 0.55, 0.80 * budget, 0.80 * budget)]
    pairs = lh.evaluate_action_sets(world, cfg, x, u, dt, wide, lam_l, m=2)
    bound = [e for e in pairs if e.allocation.binding]
    check(bound, "the two-action set is budget-bound at these quantities")
    for evaluation in bound:
        requested = tuple(float(c["q_req"]) for c in evaluation.actions)
        uncapped = lh.joint_exact_ebu(world, x, u, dt, evaluation.edges,
                                      requested, lam_l)
        check(uncapped.group_quote != evaluation.quote.group_quote,
              "the uncapped quote differs from the executed quote, so ranking "
              "on the uncapped one would have been the defect")
        check(evaluation.quote.group_quote == lh.joint_exact_ebu(
                  world, x, u, dt, evaluation.edges,
                  evaluation.allocation.q_acc, lam_l).group_quote,
              "the recorded quote is the one for the vector that executes")

    group("fidelity: the joint quote equals the frozen group diagnostic")
    probe_world = synthetic_world()
    divergences = 0
    cases = 0
    for quantities in ((0.2, 0.15), (0.5, 0.5), (1.0, 0.0001), (0.3, 0.0),
                       (0.0, 0.0), (0.0, 0.4)):
        cases += 1
        mine = lh.joint_exact_ebu(probe_world, x, u, dt, (0, 1), quantities,
                                  dc.LAM_L)
        frozen_quote = dc.group_quote_diagnostic(probe_world, x, u, dt,
                                                 list(quantities), 0)
        if (mine.group_quote != frozen_quote["group_quote"]
                or mine.naive_sum != frozen_quote["naive_independent_sum"]
                or mine.double_count != frozen_quote["double_count"]
                or mine.n_actions != frozen_quote["n_actions"]):
            divergences += 1
    check(divergences == 0,
          f"joint quote bitwise equals gate1dc_v30.group_quote_diagnostic on "
          f"{cases} vectors, including zero-quantity members")
    # The zero-quantity case is the one that used to diverge in sign.
    zero_member = lh.joint_exact_ebu(probe_world, x, u, dt, (0, 1),
                                     (0.3, 0.0), dc.LAM_L)
    check(zero_member.n_actions == 1,
          "a zero-quantity member is not counted as an active action")
    check(zero_member.double_count == 0.0,
          "one active action leaves double_count exactly zero")

    group("fidelity: shaping reproduces the frozen single-action shaping")
    divergences = 0
    for edge_index in (0, 1):
        for fraction in dc.FRACTIONS:
            one = candidate(edge_index, 0, fraction, 0.6, 1.0, 1.0)
            mine = lh.shaped_active_world(world, [one])
            frozen_world = dc.shaped_active_world(world, one)
            if mine.edges != frozen_world.edges \
                    or mine.cells is not frozen_world.cells:
                divergences += 1
    check(divergences == 0,
          "shaped edges identical to gate1dc_v30.shaped_active_world for "
          "every registered fraction on every edge")
    rest_mine = lh.shaped_active_world(world, [])
    rest_frozen = dc.shaped_active_world(world, None)
    check(rest_mine.edges == rest_frozen.edges == (),
          "the empty selection matches the frozen rest tick")

    group("fidelity: the frozen single-action assertion is subsumed")
    one = candidate(0, 0, 1.0, 0.6, 0.1 * budget, 0.1 * budget)
    allocation = lh.joint_budget_cap(world, cfg, x[0], u[0], dt, [one])
    lh.check_request_shaping_identity([one], allocation, allocation.q_acc)
    check(len(allocation.q_acc) == 1,
          "m=1 yields exactly one accepted quantity, as gate1dc asserts")
    rejects(lambda: lh.check_request_shaping_identity(
        [one], allocation, (allocation.q_acc[0], 0.0)),
        "two executed quantities for one selected action are refused",
        "identity violated")


def test_prospective_constants_and_arm_roles():
    group("prospective constants, arm roles, and truthful status")
    check(lh.M_BOUND == 2, "simultaneous-action bound is the proposed m = 2")
    check(len(lh.PROSPECTIVE_ARMS) == 4
          and len(set(lh.PROSPECTIVE_ARMS)) == 4,
          "exactly four distinct prospective arms")
    check(lh.PROSPECTIVE_ARMS[0] == "A_full_multi_edge_p1c",
          "first arm is the full-capability reference")
    check(set(lh.RESTRICTED_ARMS) == set(lh.PROSPECTIVE_ARMS[1:]),
          "the other three are restricted policies sharing one menu")
    check(set(lh.ARM_ROLES) == set(lh.PROSPECTIVE_ARMS),
          "every prospective arm has a declared role")
    check(lh.ARM_ROLES["S_restricted_local_service_priority"]
          == "stock-blind control",
          "arm S is the registered stock-blind control")
    check(len(lh.DECISION_RULE) == 6,
          "the prospective decision rule is recorded as six ordered steps")
    rule = " ".join(lh.DECISION_RULE).lower()
    check("admissibility" in rule and rule.index("admissibility")
          < rule.index("joint ebu"),
          "admissibility precedes the joint EBU step in the recorded order")
    check("accepted action vector" in rule,
          "the rule quotes the accepted vector, not the request")

    # Documentation truthfulness: the code must not claim adoption while the
    # candidate authority says "PROPOSED, NOT ADOPTED".
    module_text = inspect.getsource(lh)
    names = [n for n in dir(lh) if not n.startswith("_")]
    check(not any("ADOPTED" in n for n in names),
          "no public symbol is named ADOPTED while the authority says "
          "proposed")
    with open("V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md",
              encoding="utf-8") as handle:
        candidate_doc = handle.read()
    check("PROPOSED, NOT ADOPTED" in candidate_doc,
          "the candidate authority still records PROPOSED, NOT ADOPTED")
    check("PROSPECTIVE, NOT ADOPTED" in module_text,
          "the module records the same status as its authority")

    # This file's own prose must not claim adoption either.
    with open(__file__, encoding="utf-8") as handle:
        own_text = handle.read()
    for text, label in ((module_text, "longhorizon_v30.py"),
                        (own_text, "this test file")):
        marker = "adopt" + "ed"
        negations = ("not", "no ", "nothing", "never", "nor ")
        offenders = [line.strip() for line in text.splitlines()
                     if marker in line.lower()
                     and not any(n in line.lower() for n in negations)]
        check(not offenders,
              f"{label} claims adoption on no line "
              f"({len(offenders)} affirmative: {offenders[:2]})")

    # The module hardcodes arm identifiers because importing gate1dc_v30 is
    # not import-pure. Verify them against the locked plan by static read.
    with open("v30_gate1dc_outcome_discrimination_plan.json",
              encoding="utf-8") as handle:
        plan = json.load(handle)
    registered = set(plan["arms"])
    check(set(lh.PROSPECTIVE_ARMS) <= registered,
          "every arm identifier appears verbatim in the locked plan")
    blind = plan["arms"]["S_restricted_local_service_priority"]
    check("stock-blind" in blind and "positive-control" in blind,
          "the locked plan confirms arm S is the stock-blind positive control")
    check("C_restricted_observational_quote" not in lh.PROSPECTIVE_ARMS
          and "E_aggregate_source_group_quote" not in lh.PROSPECTIVE_ARMS,
          "no unselected registered arm is smuggled in")
    check("NOT REGISTERED FOR EXECUTION" in plan["arms"][
              "E_aggregate_source_group_quote"],
          "the locked plan still defers a settling aggregate arm (O3 open)")
    check(any("no aggregate-quote settlement" in p
              for p in json.load(open("v30_o14_multi_edge_plan.json",
                                      encoding="utf-8"))["prohibitions"]),
          "aggregate-quote settlement remains prohibited while O3 is open")

    # Behavioural, not prose: the module must not reach for any EBU
    # construction the governing mathematics forbids.
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



def test_full_fidelity_interaction_record():
    group("the full-fidelity interaction record")
    world = synthetic_world()
    cfg = synthetic_config()
    dt = 0.02
    x = (1.15, 0.2, 0.3)
    u = (0.98, -0.25, -0.25)
    lam_l = 0.5
    _state, budget = lh.source_budget_rate(cfg, x[0], u[0], dt)
    # Sized so that every pair is budget-bound: that is where the requested
    # and accepted vectors actually differ.
    menu = [candidate(0, 0, 1.0, 0.60, 0.70 * budget, 0.70 * budget),
            candidate(1, 0, 1.0, 0.55, 0.80 * budget, 0.80 * budget)]
    evaluations = lh.evaluate_action_sets(world, cfg, x, u, dt, menu, lam_l,
                                          m=2)
    pair = [e for e in evaluations if len(e.actions) == 2][0]
    check(pair.allocation.binding,
          "the probe pair is budget-bound, so request and acceptance differ")

    record = lh.interaction_record("D_restricted_exact_total_quote_greedy", 7,
                                   pair)
    check(record.n_actions == 2 and record.edges == (0, 1),
          "the record names both actions and their edges")
    check(record.group_quote is not None and record.naive_sum is not None
          and record.double_count is not None,
          "group_quote, naive_sum and double_count are all recorded for a "
          "two-action decision")
    check(close(record.double_count, record.naive_sum - record.group_quote),
          "double_count is exactly naive_sum - group_quote")
    check(len(record.independent) == 2
          and close(math.fsum(record.independent), record.naive_sum),
          "the per-edge quotes behind naive_sum are kept, so the interaction "
          "term is reproducible from the record")
    check(record.settled_ebu is None
          and record.allocation_between_actions is None
          and record.o3_open is True,
          "the record settles nothing, allocates nothing, and says O3 is open")
    dumped = json.loads(eq.canonical_json(record.as_record()))
    check(dumped["settled_ebu"] is None and dumped["o3_open"] is True,
          "the serialised record carries the same non-claims")
    check(dumped["q_req"] != dumped["q_acc"],
          "the record keeps BOTH the request and the acceptance, and they "
          "differ here")

    rest = lh.rest_record("B_restricted_matched_non_ebu", 7, "P", budget)
    check(rest.rest and rest.n_actions == 0 and rest.edges == (),
          "a rest is recorded explicitly, as the registered act condition")
    rejects(lambda: lh.interaction_record("not_an_arm", 7, pair),
            "rejects an unknown arm", "unknown arm")
    rejects(lambda: lh.interaction_record(
                "D_restricted_exact_total_quote_greedy", -1, pair),
            "rejects a negative tick", "non-negative")
    rejects(lambda: lh.rest_record("B_restricted_matched_non_ebu", 7, "Z",
                                   budget),
            "rejects an unknown P1C state", "unknown P1C state")
    rejects(lambda: lh.interaction_record(
                "D_restricted_exact_total_quote_greedy", 7,
                lh.SetEvaluation(actions=pair.actions,
                                 allocation=pair.allocation,
                                 quote=lh.JointQuote(1.0, 1.0, 0.0, 2, ()))),
            "refuses a two-action record whose interaction term is not "
            "reproducible", "reproducible")

    group("NEGATIVE: an uncapped request can never be quoted as executed")
    requested = tuple(float(action["q_req"]) for action in pair.actions)
    accepted = tuple(pair.allocation.q_acc)
    check(requested != accepted,
          f"request {requested} differs from acceptance {accepted}")
    request_quote = lh.joint_exact_ebu(world, x, u, dt, pair.allocation.edges,
                                       requested, lam_l)
    check(request_quote.group_quote != pair.quote.group_quote,
          "quoting the request gives a DIFFERENT value from quoting the "
          "acceptance, so the distinction is not cosmetic")
    check(close(pair.quote.group_quote,
                lh.joint_exact_ebu(world, x, u, dt, pair.allocation.edges,
                                   accepted, lam_l).group_quote, 0.0),
          "the recorded quote is bitwise the quote of the ACCEPTED vector")
    quotes = {e.quote.group_quote for e in evaluations}
    check(request_quote.group_quote not in quotes,
          "no enumerated set anywhere carries the request's quote")
    for evaluation in evaluations:
        requested_here = tuple(float(a["q_req"]) for a in evaluation.actions)
        if requested_here == tuple(evaluation.allocation.q_acc):
            continue
        check(evaluation.quote.group_quote != lh.joint_exact_ebu(
                  world, x, u, dt, evaluation.allocation.edges,
                  requested_here, lam_l).group_quote,
              f"set {evaluation.edges} is bound, and its quote is the "
              "accepted one")
    rejects(lambda: lh.check_request_shaping_identity(
                pair.actions, pair.allocation, requested),
            "the shaping identity REFUSES an executed vector equal to the "
            "request", "request-shaping identity violated")
    lh.check_request_shaping_identity(pair.actions, pair.allocation, accepted)
    check(True, "and accepts the joint-capped vector, exactly")
    # Structural: evaluate_action_sets passes the ALLOCATION to the quote.
    evaluate_tree = ast.parse(textwrap.dedent(
        inspect.getsource(lh.evaluate_action_sets)))
    quote_calls = [n for n in ast.walk(evaluate_tree)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id == "joint_exact_ebu"]
    check(len(quote_calls) == 1,
          "there is exactly one place a set is quoted")
    sources = {ast.unparse(argument) for argument in quote_calls[0].args}
    check("allocation.q_acc" in sources and not any(
              "q_req" in text for text in sources),
          "and it is handed allocation.q_acc, never a requested quantity")


def test_persistent_checkpoint_file():
    import tempfile

    group("persistence: closed versioned format and atomic writes")
    digest = lh.config_digest({"study": "synthetic-persistence-probe"})
    study = "synthetic-probe"
    chain = []
    previous = None
    for index, tick in enumerate((0, 5, 11)):
        previous = lh.make_checkpoint(study, digest, tick,
                                      (1.0 + index, 2.0, 3.0), prior=previous)
        chain.append(previous)
    chain = tuple(chain)

    with tempfile.TemporaryDirectory() as workspace:
        path = os.path.join(workspace, "chain.jsonl")
        final = lh.write_chain(path, chain)
        check(final == chain[-1].digest,
              "write_chain returns the final digest")
        restored = lh.read_chain(path)
        check(len(restored) == 3 and restored == chain,
              "a written chain reads back exactly equal")
        check(lh.resume_from_file(path, study, digest)[0] == 12,
              "resume_from_file returns the next tick after the last record")
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        check(len(lines) == 4, "three records plus one footer")
        footer = json.loads(lines[-1])
        check(footer["schema"] == lh.CHECKPOINT_LOG_SCHEMA
              and footer["record_count"] == 3,
              "the footer is versioned and commits to the record count")
        check(all(json.loads(line)["schema"] == lh.CHECKPOINT_SCHEMA
                  for line in lines[:-1]),
              "every record carries the versioned record schema")
        check(lines == sorted(lines, key=lambda line: 0) and all(
                  line == eq.canonical_json(json.loads(line))
                  for line in lines),
              "every line is strict canonical JSON")

        def corrupt(name, mutate):
            target = os.path.join(workspace, name)
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(mutate(list(lines)))
            return target

        group("persistence: refusal on every declared defect")
        rejects(lambda: lh.read_chain(corrupt(
                    "no_footer.jsonl",
                    lambda rows: "\n".join(rows[:-1]) + "\n")),
                "refuses a file with no footer (truncation)", "truncated")
        rejects(lambda: lh.read_chain(corrupt(
                    "short.jsonl",
                    lambda rows: "\n".join(rows[:-2] + rows[-1:]) + "\n")),
                "refuses a file whose record count disagrees with the footer",
                "truncated or edited")
        rejects(lambda: lh.read_chain(corrupt(
                    "torn.jsonl",
                    lambda rows: "\n".join(rows[:-1]
                                           + [rows[-1][:len(rows[-1]) // 2]])
                    + "\n")),
                "refuses a torn final line", "not strict JSON")

        def tampered(rows):
            record = json.loads(rows[1])
            record["state"] = [99.0, 2.0, 3.0]
            rows[1] = eq.canonical_json(record)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("tampered.jsonl", tampered)),
                "refuses an altered record (digest mismatch)",
                "altered after it was written")

        def forked(rows):
            record = json.loads(rows[2])
            record["prior_digest"] = "0" * 64
            record["digest"] = lh._checkpoint_digest(
                record["schema"], record["study_id"], record["config_digest"],
                record["sequence"], record["tick"], record["state"],
                record["prior_digest"])
            rows[2] = eq.canonical_json(record)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("forked.jsonl", forked)),
                "refuses a fork: a link pointing at a different predecessor",
                "chain broken")

        def unknown_key(rows):
            record = json.loads(rows[0])
            record["extra"] = 1
            rows[0] = eq.canonical_json(record)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("unknown.jsonl", unknown_key)),
                "refuses an unknown field (the format is closed)",
                "format is closed")

        def missing_key(rows):
            record = json.loads(rows[0])
            del record["tick"]
            rows[0] = eq.canonical_json(record)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("missing.jsonl", missing_key)),
                "refuses a missing field", "wrong key set")

        def wrong_schema(rows):
            record = json.loads(rows[0])
            record["schema"] = "v99.unknown"
            rows[0] = eq.canonical_json(record)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("schema.jsonl", wrong_schema)),
                "refuses an unknown record schema", "unknown schema")

        def footer_digest(rows):
            foot = json.loads(rows[-1])
            foot["final_digest"] = "1" * 64
            rows[-1] = eq.canonical_json(foot)
            return "\n".join(rows) + "\n"
        rejects(lambda: lh.read_chain(corrupt("footdig.jsonl", footer_digest)),
                "refuses a footer digest that disagrees with the last record",
                "does not match the last record")

        rejects(lambda: lh.read_chain(os.path.join(workspace, "absent.jsonl")),
                "refuses a missing file", "cannot read")
        rejects(lambda: lh.read_chain(corrupt("empty.jsonl", lambda r: "\n")),
                "refuses an empty file", "empty")

        group("persistence: rewind, fork and identity refusals at the API")
        rejects(lambda: lh.write_chain(
                    os.path.join(workspace, "never.jsonl"), chain[1:]),
                "refuses to persist a chain that does not start at sequence 0",
                "verified from its root")
        check(not os.path.exists(os.path.join(workspace, "never.jsonl")),
              "and nothing was written, so a bad chain never reaches disk")
        rejects(lambda: lh.resume_from_file(path, "another-study", digest),
                "refuses to resume another study's chain", "cannot resume")
        rejects(lambda: lh.resume_from_file(path, study, "f" * 64),
                "refuses to resume under an altered configuration",
                "configuration digest differs")
        rejects(lambda: lh.append_checkpoint(path, "another-study", digest,
                                             20, (1.0, 2.0, 3.0)),
                "refuses to extend a chain recorded for another study",
                "recorded for")
        rejects(lambda: lh.append_checkpoint(path, study, "f" * 64, 20,
                                             (1.0, 2.0, 3.0)),
                "refuses to extend under an altered configuration",
                "configuration digest differs")
        rejects(lambda: lh.append_checkpoint(path, study, digest, 11,
                                             (1.0, 2.0, 3.0)),
                "refuses a rewind: the tick must advance", "does not advance")
        rejects(lambda: lh.append_checkpoint(path, study, digest, 20,
                                             (1.0, 2.0)),
                "refuses a changed state dimension", "state dimension changed")
        before = open(path, encoding="utf-8").read()
        extended = lh.append_checkpoint(path, study, digest, 20,
                                        (4.0, 2.0, 3.0))
        check(extended.sequence == 3 and extended.tick == 20,
              "a valid extension advances the sequence and the tick")
        check(len(lh.read_chain(path)) == 4,
              "and the persisted chain still verifies from its root")
        check(before != open(path, encoding="utf-8").read(),
              "the file was rewritten in full, not appended to")
        fresh = os.path.join(workspace, "fresh.jsonl")
        started = lh.append_checkpoint(fresh, study, digest, 0, (1.0, 2.0))
        check(started.sequence == 0 and started.prior_digest is None,
              "a fresh attempt starts a new chain at sequence 0")

        group("persistence: atomic write discipline")
        rejects(lambda: lh._atomic_write_text(
                    os.path.join(workspace, "absent_dir", "f.jsonl"), "x"),
                "refuses to write into a directory that does not exist",
                "output directory does not exist")
        leftovers = [name for name in os.listdir(workspace)
                     if name.endswith(".partial")]
        check(not leftovers,
              f"no partial file is left behind ({leftovers})")
        write_tree = ast.parse(textwrap.dedent(
            inspect.getsource(lh._atomic_write_text)))
        attributes = {n.attr for n in ast.walk(write_tree)
                      if isinstance(n, ast.Attribute)}
        check({"fsync", "replace", "O_EXCL"} <= attributes,
              "the writer fsyncs, renames atomically, and uses O_EXCL on its "
              "temporary")
        check("O_APPEND" not in attributes and "O_TRUNC" not in attributes,
              "it never appends to or truncates the live file")


def test_l0_smoke_path_fails_closed():
    import tempfile

    group("L0 smoke path: implemented, never invoked, fails closed")
    check(lh.L0_SCOPE == "L0_smoke_one_decision_cycle",
          "the L0 authorization scope is explicit and narrow")
    tree = ast.parse(textwrap.dedent(inspect.getsource(lh.run_l0_smoke)))
    body = [n for n in tree.body[0].body
            if not isinstance(n, ast.Expr)]
    first = body[0]
    check(isinstance(first, ast.Assign)
          and isinstance(first.value, ast.Call)
          and getattr(first.value.func, "id", "") == "verify_l0_preconditions",
          "verification is the FIRST statement, so no decision work is "
          "reachable without it")
    called = {n.func.attr for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    for forbidden in ("p1c_step", "bounded_step", "step", "run", "simulate"):
        check(forbidden not in called,
              f"the L0 path never calls {forbidden!r}")

    good = lh.L0Authorization(scope=lh.L0_SCOPE,
                              author_statement="synthetic probe only",
                              permits_decision_cycle=True)
    with tempfile.TemporaryDirectory() as workspace:
        missing_plan = os.path.join(workspace, "no_such_plan.json")
        output = os.path.join(workspace, "out.json")

        def request(**overrides):
            fields = {"plan_path": missing_plan,
                      "expected_plan_hash": "a" * 64,
                      "study_id": "synthetic-probe",
                      "config_digest": "b" * 64,
                      "output_path": output, "authorization": good}
            fields.update(overrides)
            return lh.L0Request(**fields)

        rejects(lambda: lh.verify_l0_preconditions("not a request"),
                "refuses a non-L0Request", "must be an L0Request")
        rejects(lambda: lh.verify_l0_preconditions(
                    request(authorization=None)),
                "refuses a missing authorization object",
                "L0Authorization object is required")
        rejects(lambda: lh.verify_l0_preconditions(request(
                    authorization=lh.L0Authorization(
                        scope="something_else", author_statement="x",
                        permits_decision_cycle=True))),
                "refuses an authorization for a different scope",
                "never carries to another")
        rejects(lambda: lh.verify_l0_preconditions(request(
                    authorization=lh.L0Authorization(
                        scope=lh.L0_SCOPE, author_statement="   ",
                        permits_decision_cycle=True))),
                "refuses an empty author statement", "author statement")
        rejects(lambda: lh.verify_l0_preconditions(request(
                    authorization=lh.L0Authorization(
                        scope=lh.L0_SCOPE, author_statement="x"))),
                "refuses an authorization that does not permit a cycle",
                "does not permit a decision cycle")
        check(lh.L0Authorization(scope=lh.L0_SCOPE, author_statement="x"
                                 ).permits_decision_cycle is False,
              "permission defaults to False, so an incomplete object refuses")
        rejects(lambda: lh.verify_l0_preconditions(request(study_id="")),
                "refuses an empty study identity", "non-empty string")
        rejects(lambda: lh.verify_l0_preconditions(
                    request(expected_plan_hash="abc")),
                "refuses a malformed plan hash", "64-character")
        rejects(lambda: lh.verify_l0_preconditions(
                    request(config_digest="abc")),
                "refuses a malformed configuration digest", "64-character")
        rejects(lambda: lh.verify_l0_preconditions(request()),
                "refuses when no frozen plan exists at the declared path",
                "never generates a plan")

        # Deliberately invalid fixtures: each must be refused. None of them
        # can pass, so the decision code below verification is unreachable.
        broken = os.path.join(workspace, "not_a_plan.json")
        with open(broken, "w", encoding="utf-8") as handle:
            handle.write("{not json")
        rejects(lambda: lh.verify_l0_preconditions(
                    request(plan_path=broken)),
                "refuses a plan that is not strict JSON", "not strict JSON")

        wrong_keys = os.path.join(workspace, "wrong_keys.json")
        payload = {"schema": lh.L0_PLAN_SCHEMA, "study_id": "synthetic-probe"}
        with open(wrong_keys, "w", encoding="utf-8") as handle:
            handle.write(eq.canonical_json(payload))
        rejects(lambda: lh.verify_l0_preconditions(request(
                    plan_path=wrong_keys, expected_plan_hash="c" * 64)),
                "refuses a plan whose hash is not the declared one",
                "plan hash mismatch")
        rejects(lambda: lh.verify_l0_preconditions(request(
                    plan_path=wrong_keys,
                    expected_plan_hash=eq.commitment_hash(payload))),
                "refuses a plan with the wrong key set (the schema is closed)",
                "plan schema is closed")

        occupied = os.path.join(workspace, "taken.json")
        with open(occupied, "w", encoding="utf-8") as handle:
            handle.write("{}")
        rejects(lambda: lh.verify_l0_preconditions(
                    request(output_path=occupied)),
                "refuses to overwrite an existing output", "already exists")
        rejects(lambda: lh.verify_l0_preconditions(request(
                    output_path=os.path.join(workspace, "absent", "o.json"))),
                "refuses an output directory that does not exist",
                "output directory does not exist")

        # run_l0_smoke itself refuses, proving the guard is not bypassable.
        rejects(lambda: lh.run_l0_smoke(request()),
                "run_l0_smoke refuses an under-specified request without "
                "reaching any decision code", "never generates a plan")
        check(not os.path.exists(output),
              "and wrote no output at all")

    group("L0 smoke path: the open launch gate is recorded in code")
    check(len(lh.OPEN_LAUNCH_GATES) >= 1,
          "at least one launch gate is still open")
    gates = " ".join(lh.OPEN_LAUNCH_GATES).lower()
    check("settlement" in gates and "o3" in gates,
          "the open gate is the multi-action settlement form while O3 is open")
    source = inspect.getsource(lh)
    check("settled_ebu: None" in source,
          "the record type cannot carry a settled value at all")


def test_documentation_status_agrees_with_code():
    group("status language: code and its authorities say the same thing")
    docs = {}
    for name in ("V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md",
                 "V3.0_LONG_HORIZON_STUDY_DECISION_PACKET.md",
                 "V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md"):
        with open(name, encoding="utf-8") as handle:
            docs[name] = handle.read()

    candidate_doc = docs["V3.0_LONG_HORIZON_NORMALIZED_MECHANISM_CANDIDATE.md"]
    check("PROPOSED, NOT ADOPTED" in candidate_doc,
          "the candidate authority still records PROPOSED, NOT ADOPTED")
    check("PROSPECTIVE, NOT ADOPTED" in inspect.getsource(lh),
          "the module records the same status as its authority")
    # Sentence-level, because these documents wrap prose: a line scan splits
    # "proposed, not adopted" across two lines and reports the second half as
    # an affirmative claim. Every sentence using the marker must either negate
    # it, or be one of the recorded non-study uses below. A NEW affirmative
    # sentence fails this check and needs a human to look at it.
    import re as _re
    marker = "adopt"
    negations = ("not adopt", "no adopt", "never adopt", "nothing",
                 "does not", "do **not**", "proposed, not", "not adopted",
                 "remain open", "still asks", "still reads")
    # Recorded non-study uses. None of these is a claim that this study, its
    # families, or its arms have been taken up; each line says which it is.
    allowed_non_study = (
        "units adopted here",                  # not a claim: normalization
        "exact-model conformance convention",  # not a claim: SourceConfig
        "adopting a decision in this packet does not authorize",  # a negation
        "adopting anything in this file does not authorize",      # a negation
        "i adopt family ______",               # not a claim: unfilled blank
        "this adopts a design and",            # not a claim: same blank
        "author adoption of the n/h/x",        # not a claim: a launch gate
        "list of launch gates",                # not a claim: a launch gate
        "not an adoption",                     # a negation
        "the adoption itself",                 # not a claim: what is missing
        "author-adoption statement",           # not a claim: what is missing
        "which family or families to adopt",   # not a claim: an open question
        "are selected",                        # not a claim: packet-level
    )
    for name, text in docs.items():
        flat = " ".join(text.split())
        offenders = []
        for sentence in _re.split(r"(?<=[.;:])\s+", flat):
            low = sentence.lower()
            if marker not in low:
                continue
            if any(n in low for n in negations):
                continue
            if any(a in low for a in allowed_non_study):
                continue
            offenders.append(sentence[:120])
        check(not offenders,
              f"{name} makes no affirmative adoption claim "
              f"({len(offenders)}: {offenders[:1]})")

    # Declared-vs-derived must read identically in the code and the authority.
    check("### The three declared set-level rules" in candidate_doc,
          "the candidate records the three declared set-level rules")
    check("declarations, not derivations" in candidate_doc,
          "and says in terms that they are declarations, not derivations")
    for arm in ("B_restricted_matched_non_ebu",
                "S_restricted_local_service_priority"):
        check(lh.DECLARED_SET_SCORES[arm].startswith("DECLARED."),
              f"{arm} is marked DECLARED in code")
    check(lh.DECLARED_SET_SCORES["D_restricted_exact_total_quote_greedy"]
          .startswith("DERIVED."),
          "the exact-EBU arm is marked DERIVED in code")
    check(set(lh.DECLARED_SET_SCORES) - {"_final_ties"}
          == set(lh.RESTRICTED_ARMS),
          "every restricted arm has a recorded set-level score status")

    # The one gate that is still open must read as open everywhere.
    check("UNRESOLVED" in candidate_doc and "settled and recorded EBU is"
          in candidate_doc,
          "the candidate still records the settlement form as unresolved")
    gates = " ".join(lh.OPEN_LAUNCH_GATES).lower()
    check("settlement" in gates and "o3" in gates,
          "the code records the same open gate")
    plan_doc = docs["V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md"]
    check("OPEN — blocks execution" in plan_doc
          or "OPEN - blocks execution" in plan_doc,
          "the cost plan records it as blocking execution")
    for phrase in ("No AWS call", "No scientific execution occurred",
                   "no dollar ceiling", "not chosen horizons"):
        check(phrase.lower() in plan_doc.lower(),
              f"the cost plan states its non-claim: {phrase!r}")
    check("NON-FROZEN MARKET INFORMATION" in plan_doc,
          "the price snapshot is labelled non-frozen market information")
    check("2026-09-12" in plan_doc,
          "and carries the date it was retrieved")

    # The forward-work selections are recorded prospectively in both places.
    check("Selections declared in the forward-work package" in candidate_doc,
          "the candidate records the declared selections prospectively")
    packet = docs["V3.0_LONG_HORIZON_STUDY_DECISION_PACKET.md"]
    check("0c. Further selections declared in the forward-work package"
          in packet,
          "the decision packet records them too")
    for text, name in ((candidate_doc, "candidate"), (packet, "packet")):
        check("`F = 5`" in text, f"the {name} records the declared F = 5")


def main() -> int:
    test_execution_safety_and_import_purity()
    test_mechanism_1_joint_budget_cap()
    test_mechanism_2_set_enumeration_and_joint_ebu()
    test_mechanism_3_shaping_identity()
    test_mechanism_4_checkpoint_restart()
    test_full_fidelity_interaction_record()
    test_persistent_checkpoint_file()
    test_l0_smoke_path_fails_closed()
    test_fidelity_to_the_frozen_selectors()
    test_prospective_constants_and_arm_roles()
    test_documentation_status_agrees_with_code()
    print(f"\nLong-horizon mechanisms: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
