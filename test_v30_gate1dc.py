"""Gate 1D-C pre-execution validation; static and pure-function only.

This suite MUST NOT call a model step, ``gate1dc_tick``, ``run_arm``, a
runner, a simulation, or any trajectory helper.  It validates the locked
plan, algebraic certificates, pure menu/selector/quote functions, information
guards, frozen predicates, schemas, filenames, and fail-closed behavior.
Temporary altered plan copies are used only to prove hash refusal.
"""
from __future__ import annotations

import ast
import copy
import errno
import gzip
import hashlib
import inspect
import json
import math
import os
import signal
import stat
import subprocess
import sys
import tempfile

import d0_v29 as d0
import exp_v30_gate1dc as runner
import finalize_v30_gate1dc as finalizer
import gate1dc_v30 as dc
import service_v30 as sv


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
    except (AssertionError, KeyError, OSError, RuntimeError, TypeError,
            ValueError, SystemExit) as error:
        check(not contains or contains in str(error), label)
    else:
        check(False, label)


def close(actual, expected, tolerance=1e-14) -> bool:
    return abs(actual - expected) <= tolerance * max(1.0, abs(expected))


def menu_at_initial(world_name: str, dt_label: str):
    world, state, configs, _demand, _meta = dc.build_world(world_name)
    drive = sv.drive_no_demand(world, state)
    state_class, budget, candidates = dc.candidate_menu(
        world, state, drive, 0, configs[0], dc.world_dts(world_name)[dt_label])
    return world, state, configs, drive, state_class, budget, candidates


def test_plan_lock_and_schema() -> None:
    group("locked hashes, strict JSON, and fail-closed schema")
    raw = open(dc.PLAN_PATH, "rb").read()
    check(hashlib.sha256(raw).hexdigest() == dc.PLAN_RAW,
          "raw SHA-256 equals the registered lock")
    check(dc.plan_canonical_hash(dc.PLAN) == dc.PLAN_CANONICAL,
          "canonical SHA-256 equals the registered lock")
    check(json.loads(raw, parse_constant=dc._reject_nonfinite) == dc.PLAN,
          "authoritative plan parses as strict JSON")
    check(dc.PLAN["equation_version_expected"] == "v3.0-gate0.1",
          "equation-version expectation is frozen")
    dc.validate_plan(dc.PLAN)
    check(True, "complete execution-relevant schema validates")

    mutations = []
    for path, replacement in (
        (("experiment_size", "total_runs"), 31),
        (("quantity_menu", "fractions"), [0.5, 1.0]),
        (("worlds", "DC1_flux_lock", "x0"), [12.0, 0.0, 3.6]),
        (("worlds", "DC3_demand_pulse", "demand_schedule", "pulse_ticks"),
         [10, 35]),
        (("timestep", "per_world", "DC2_capacity_split",
          "registered_conservative_dt"), 0.2),
        (("arms", "primary_comparison"), "D versus A"),
        (("positive_control", "PC1_DC1_S_starves_dst2",
          "certified_lower_bound"), {"conservative": 0.0,
                                     "near_certificate": 0.0}),
        (("discriminator_v2", "tolerance"), "1e-6"),
        (("planned_future_files_not_created",), []),
    ):
        altered = copy.deepcopy(dc.PLAN)
        target = altered
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = replacement
        mutations.append((".".join(path), altered))
    for label, altered in mutations:
        rejects(lambda plan=altered: dc.validate_plan(plan),
                f"in-memory mutation rejected: {label}")
        check(dc.plan_canonical_hash(altered) != dc.PLAN_CANONICAL,
              f"in-memory mutation changes canonical hash: {label}")

    with tempfile.TemporaryDirectory() as directory:
        changed = copy.deepcopy(dc.PLAN)
        changed["experiment_size"]["run_length_ticks"] = 201
        path = os.path.join(directory, "altered-plan.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(changed, handle, indent=2, allow_nan=False)
        rejects(lambda: dc.load_plan(path),
                "altered temporary copy is rejected by raw hash", "raw")
        altered_raw = open(path, "rb").read()
        altered_raw_hash = hashlib.sha256(altered_raw).hexdigest()
        rejects(lambda: dc.load_plan(path, expected_raw=altered_raw_hash),
                "altered temporary copy is rejected by canonical hash",
                "canonical")
        nonfinite_path = os.path.join(directory, "nonfinite-plan.json")
        with open(nonfinite_path, "w", encoding="utf-8") as handle:
            handle.write('{"value": NaN}')
        rejects(lambda: dc.load_plan(nonfinite_path, expected_canonical="0" * 64,
                                     expected_raw=None),
                "non-finite temporary JSON is rejected", "non-finite")


def test_worlds_and_demand() -> None:
    group("exact worlds and current-tick demand schedule")
    check(dc.WORLD_NAMES == tuple(sorted(dc.PLAN["worlds"])),
          "world names use the frozen sorted order")
    for name in dc.WORLD_NAMES:
        world, state, configs, demand, meta = dc.build_world(name)
        spec = dc.PLAN["worlds"][name]
        check(len(world.cells) == len(spec["cells"]) == len(state) == len(demand),
              f"{name}: cell/state/demand dimensions agree")
        check(len(world.edges) == len(spec["edges"]),
              f"{name}: exact edge count")
        check(tuple(configs) == (0,) and all(edge.i == 0 for edge in world.edges),
              f"{name}: exactly one configured source and static fan-out")
        check(meta["feasible"] is spec["feasible"],
              f"{name}: feasibility flag is exact")
        check(all(edge.i != edge.j for edge in world.edges)
              and len({edge.j for edge in world.edges}) == len(world.edges),
              f"{name}: distinct destinations, no shared destination endpoint")
    dc1, *_ = dc.build_world("DC1_flux_lock")
    dc3, *_ = dc.build_world("DC3_demand_pulse")
    check(dc1.cells == dc3.cells and dc1.edges == dc3.edges,
          "DC1 and DC3 have identical topology and cell parameters")

    pulses = {10, 35, 60, 85, 110, 135, 160, 185}
    for label in dc.DT_LABELS:
        dt = dc.world_dts("DC3_demand_pulse")[label]
        for tick in (1, 10, 34, 35, 50, 185, 200):
            demand = dc.demand_rate_for_tick("DC3_demand_pulse", label, tick)
            expected = 1.0 / dt if tick in pulses else 0.0
            check(demand[0] == 0.0 and demand[1] == 3.0
                  and demand[2] == expected,
                  f"DC3/{label}/tick-{tick}: only current pulse demand exposed")
        window_pulses = [tick for tick in pulses if tick > dc.BURN_IN_TICKS]
        check(len(window_pulses) == 6,
              f"DC3/{label}: exactly six pulses in measurement window")
        check(close(dt * dc.demand_rate_for_tick(
            "DC3_demand_pulse", label, 10)[2], 1.0),
              f"DC3/{label}: pulse demanded amount is exactly 1.0")
    for name in ("DC1_flux_lock", "DC2_capacity_split"):
        for label in dc.DT_LABELS:
            check(dc.demand_rate_for_tick(name, label, 1)
                  == dc.demand_rate_for_tick(name, label, 200),
                  f"{name}/{label}: constant demand is tick-invariant")
    rejects(lambda: dc.demand_rate_for_tick("DC1_flux_lock", "conservative", 0),
            "tick zero is rejected")


def test_certificates_and_inventory() -> None:
    group("binding certificates and exact 30-run inventory")
    for name in dc.WORLD_NAMES:
        certificate = dc.world_certificates(name)
        locked = dc.PLAN["timestep"]["per_world"][name]
        check(certificate == {key: locked[key] for key in certificate},
              f"{name}: all certificate fields recompute exactly")
        check(certificate["binding_kind"] == "gershgorin",
              f"{name}: registered binding kind")
        dts = dc.world_dts(name)
        check(dts["conservative"] / certificate["binding_certificate"] == 0.5,
              f"{name}: conservative r_dt exactly 0.5")
        check(close(dts["near_certificate"] /
                    certificate["binding_certificate"], 0.9),
              f"{name}: near-certificate r_dt exactly 0.9")
        check(all(value <= certificate["binding_certificate"]
                  for value in dts.values()),
              f"{name}: neither registered timestep exceeds certificate")

    specs = dc.build_run_specs()
    expected = [
        f"{world}|{arm}|{label}"
        for world in dc.WORLD_NAMES for label in dc.DT_LABELS
        for arm in dc.EXEC_ARMS
    ]
    check(len(specs) == 30 and len({spec["run_id"] for spec in specs}) == 30,
          "exactly 30 unique runs")
    check([spec["run_id"] for spec in specs] == expected,
          "frozen world x timestep x arm ordering is exact")
    check(dc.RUN_TICKS == 200 and dc.BURN_IN_TICKS == 50
          and dc.MEASUREMENT_TICKS == 150 and dc.PERSISTENCE_WINDOW == 20,
          "200/50/150/20 horizon and windows are exact")
    check(dc.PLAN["experiment_size"]["stochastic_study"] is False
          and "seed" not in dc.PLAN["experiment_size"],
          "study is deterministic and has no seed")


def test_menu_filtering_and_identity() -> None:
    group("common feasible menu and filter-before-ranking discipline")
    for name in dc.WORLD_NAMES:
        for label in dc.DT_LABELS:
            world, state, configs, drive, state_class, budget, candidates = \
                menu_at_initial(name, label)
            check(state_class == "P" and budget > 0.0,
                  f"{name}/{label}: initial source is State P with budget")
            check(len(candidates) == len(world.edges) * len(dc.FRACTIONS),
                  f"{name}/{label}: every edge has four ordered candidates")
            check([candidate["frac"] for candidate in candidates]
                  == list(dc.FRACTIONS) * len(world.edges),
                  f"{name}/{label}: fractions use frozen per-edge order")
            check(all(0.0 < candidate["q_acc"] <= candidate["q_e_max"]
                      <= candidate["J"] for candidate in candidates),
                  f"{name}/{label}: every candidate is prefiltered and capped")
            check(all(candidate["q_acc"] == min(candidate["q_req"], budget)
                      for candidate in candidates),
                  f"{name}/{label}: authoritative budget arithmetic is exact")
            check(all(candidate["quant_index"] in range(4)
                      and candidate["edge"] in range(len(world.edges))
                      for candidate in candidates),
                  f"{name}/{label}: deterministic candidate identifiers")
            selected = dc.select_arm_B(candidates)
            shaped = dc.shaped_active_world(world, selected)
            shaped_force, shaped_request = d0.edge_flux(
                d0.local_view(world.cells[0], state[0]),
                d0.local_view(world.cells[shaped.edges[0].j],
                              state[shaped.edges[0].j]), shaped.edges[0])
            check(shaped_force == selected["f"]
                  and shaped_request == selected["q_req"]
                  and min(shaped_request, budget) == selected["q_acc"],
                  f"{name}/{label}: pure request shaping reproduces selected quantity")
            snapshots = [copy.deepcopy(candidates) for _arm in dc.EXEC_ARMS[1:]]
            check(all(snapshot == snapshots[0] for snapshot in snapshots),
                  f"{name}/{label}: B/C/D/S consume one identical menu object value")

            unsafe_state = list(state)
            unsafe_state[0] = configs[0].R_eff - 0.01
            unsafe_drive = sv.drive_no_demand(world, unsafe_state)
            unsafe_class, unsafe_budget, unsafe_menu = dc.candidate_menu(
                world, unsafe_state, unsafe_drive, 0, configs[0],
                dc.world_dts(name)[label])
            check(unsafe_class == "R" and unsafe_budget == 0.0
                  and unsafe_menu == [],
                  f"{name}/{label}: unsafe state is removed before ranking")
            check(dc.select_arm_B(unsafe_menu) is None
                  and dc.select_arm_D(unsafe_menu, []) is None
                  and dc.select_arm_S(unsafe_menu, (), world) is None,
                  f"{name}/{label}: every selector rests on filtered empty menu")

    check(dc.MENU_CONTRACT_HASH == hashlib.sha256(json.dumps(
        {"fractions": dc.FRACTIONS, "arms": dc.EXEC_ARMS[1:],
         "cap": "authoritative-p1c-before-ranking", "unsafe": "removed"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
          "per-tick capability contract hash is deterministic")


def test_selectors_and_quotes() -> None:
    group("arm identity, ranking, deterministic ties, and exact quotes")
    tied = [
        {"f": 2.0, "q_acc": 1.0, "edge": 1, "quant_index": 0},
        {"f": 2.0, "q_acc": 1.0, "edge": 0, "quant_index": 1},
        {"f": 2.0, "q_acc": 1.0, "edge": 0, "quant_index": 0},
    ]
    check(dc.select_arm_B(tied) is tied[2],
          "B ties by lower edge then lower quantity index")
    check(dc.select_arm_D(tied, [3.0, 3.0, 3.0]) == 2,
          "D ties by lower edge then lower quantity index")
    check(dc.select_arm_D(tied, [0.0, -1.0, 0.0]) is None,
          "D rests unless the best exact total quote is strictly positive")
    total_vs_unit = [
        {"f": 1.0, "q_acc": 100.0, "edge": 0, "quant_index": 0},
        {"f": 1.0, "q_acc": 1.0, "edge": 1, "quant_index": 0},
    ]
    check(dc.select_arm_D(total_vs_unit, [2.0, 1.5]) == 0,
          "D chooses larger exact total even when its per-unit value is smaller")
    source_d = inspect.getsource(dc.select_arm_D)
    check("q_acc" not in source_d and "per_unit" not in source_d,
          "D selector has no quantity normalization or per-unit input")

    for label in dc.DT_LABELS:
        world, state, _configs, drive, _class, _budget, candidates = \
            menu_at_initial("DC2_capacity_split", label)
        exact = [dc.quote_schedule_for(world, state, drive,
                                       dc.world_dts("DC2_capacity_split")[label],
                                       candidate, 1).exact(candidate["q_acc"])
                 for candidate in candidates]
        pick_b = dc.select_arm_B(candidates)
        pick_d = candidates[dc.select_arm_D(candidates, exact)]
        check(pick_b["edge"] == 0 and pick_b["frac"] == 1.0,
              f"DC2/{label}: B provably chooses edge a at t0")
        check(pick_d["edge"] == 2 and pick_d["frac"] == 1.0,
              f"DC2/{label}: D provably chooses edge c at t0")
        expected_quotes = dc.PLAN["instrument_sensitivity_certificate"] \
            ["DC2_capacity_split"]["registered_t0_divergence"] \
            ["quotes_conservative" if label == "conservative"
             else "quotes_near_certificate"]
        full = {"a": exact[3], "b": exact[7], "c": exact[11]}
        check(all(close(full[key], expected_quotes[key])
                  for key in ("a", "b", "c")),
              f"DC2/{label}: exact full-quantity quotes match registration")
        invalid = dict(candidates[0])
        invalid["q_acc"] = invalid["q_e_max"] + 1.0
        rejects(lambda candidate=invalid: dc.quote_schedule_for(
            world, state, drive, dc.world_dts("DC2_capacity_split")[label],
            candidate, 1),
                f"DC2/{label}: quote outside [0, q_e_max] is rejected")

    source_tick = inspect.getsource(dc.gate1dc_tick)
    b_select = source_tick.index("pick = select_arm_B(candidates)")
    quote_after = source_tick.index("exact = [quote_schedule_for", b_select)
    check(b_select < quote_after,
          "B/C physical selection is fixed before observational quote creation")
    check("if arm in (EXEC_ARMS[2], EXEC_ARMS[3])" in source_tick,
          "settlement is gated to C and D only")
    check("if arm == EXEC_ARMS[0]" in source_tick
          and "group_quote_diagnostic" in source_tick,
          "A carries only the settlement-free group diagnostic")


class CurrentDemandPoison:
    """Allows indexed current demand only; iteration/lookahead explodes."""
    def __init__(self, values):
        self.values = tuple(values)
        self.reads = []

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise AssertionError("non-local demand access")
        self.reads.append(index)
        return self.values[index]

    def __iter__(self):
        raise AssertionError("decision attempted demand-vector traversal")

    def __len__(self):
        raise AssertionError("decision attempted schedule-like inspection")


def test_information_boundary() -> None:
    group("AST and runtime enforcement of the information boundary")
    forbidden = {
        "V_total", "service", "unmet", "demand_schedule", "pulse_ticks",
        "future", "rollout", "classification", "result", "wallet",
        "health", "price", "market", "gate1dc_tick", "run_arm",
        "bounded_step", "p1c_step",
    }
    for function in dc.DECISION_PATH_FUNCS:
        tree = ast.parse(inspect.getsource(function))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        names |= {node.attr for node in ast.walk(tree)
                  if isinstance(node, ast.Attribute)}
        hits = sorted(names & forbidden)
        check(not hits, f"{function.__name__}: no forbidden identifier {hits}")
        check("V_total" not in inspect.getsource(function),
              f"{function.__name__}: global V never enters decision path")

    world, state, _configs, _drive, _class, _budget, candidates = \
        menu_at_initial("DC3_demand_pulse", "conservative")
    off_pulse = CurrentDemandPoison((0.0, 3.0, 0.0))
    pick = dc.select_arm_S(candidates, off_pulse, world)
    check(pick["edge"] == 0 and set(off_pulse.reads) <= {1, 2},
          "S reads only adjacent current-tick demand and selects edge 0 off-pulse")
    pulse = CurrentDemandPoison((0.0, 3.0, 1.0 / dc.world_dts(
        "DC3_demand_pulse")["conservative"]))
    pick = dc.select_arm_S(candidates, pulse, world)
    check(pick["edge"] == 0 and set(pulse.reads) <= {1, 2},
          "S-lock selects edge 0 at a pulse without schedule access")
    source_s = inspect.getsource(dc.select_arm_S)
    tree_s = ast.parse(source_s)
    argument_names = {argument.arg for node in ast.walk(tree_s)
                      if isinstance(node, (ast.FunctionDef, ast.Lambda))
                      for argument in node.args.args}
    identifier_names = {node.id for node in ast.walk(tree_s)
                        if isinstance(node, ast.Name)}
    check("tick" not in argument_names and "schedule" not in identifier_names
          and "current_demand_rate" in argument_names,
          "S selector accepts current demand only, with no tick/schedule handle")

    source = open(__file__, "r", encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden_calls = {"gate1dc_tick", "run_arm", "bounded_step", "p1c_step",
                       "d0_step"}
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    check(not (calls & forbidden_calls),
          "the pre-execution suite contains no step, run, runner, or trajectory call")
    runner_imports = [node for node in ast.walk(tree)
                      if isinstance(node, (ast.Import, ast.ImportFrom))
                      and any(alias.name.startswith("exp_v30_gate1dc")
                              for alias in node.names)]
    check(len(runner_imports) == 1,
          "the official runner is imported once for zero-side-effect validation")


def test_analytic_certificates() -> None:
    group("static instrument-sensitivity and binding analytical checks")
    world, state, configs, drive, _class, budget, candidates = \
        menu_at_initial("DC1_flux_lock", "conservative")
    source = world.cells[0]
    check(all(d0.marginal(source.alpha, source.beta, source.chi, source.L,
                          source.U, source.R, value) == 0.0
              for value in (8.0, 12.0, 20.0)),
          "source marginal is exactly flat over the protected reachable band")
    check(sv.drive_no_demand(world, (8.0, 0.0, 3.5))[0] == 2.88,
          "source budget floor g(8) is exactly 2.88")
    thresholds = dc.PLAN["instrument_sensitivity_certificate"] \
        ["DC1_flux_lock"]["registered_thresholds"]
    full = [candidate for candidate in candidates if candidate["frac"] == 1.0]
    check(full[0]["f"] == thresholds["F1MAX"]
          and full[0]["J"] == thresholds["J1"]
          and world.edges[0].eta * full[0]["J"] == thresholds["eta1J1"],
          "DC1 frozen F1/J1/delivered-rate constants recompute exactly")
    zero_state = list(state)
    zero_state[2] = 0.0
    zero_drive = sv.drive_no_demand(world, zero_state)
    _s, _b, zero_menu = dc.candidate_menu(
        world, zero_state, zero_drive, 0, configs[0],
        dc.world_dts("DC1_flux_lock")["conservative"])
    zero_full = [candidate for candidate in zero_menu
                 if candidate["edge"] == 1 and candidate["frac"] == 1.0][0]
    check(zero_full["J"] == thresholds["J2_at_zero_stock"]
          and world.edges[1].eta * zero_full["J"] == thresholds["eta2J2max"],
          "DC1 dst2 zero-stock maximum recomputes exactly")
    check(close(thresholds["eta1J1"] / thresholds["eta2J2max"],
                thresholds["S_lock_ratio"]),
          "DC1 S-lock ratio recomputes")
    check(thresholds["eta1J1"] < 3.0
          and thresholds["eta1J1"] > thresholds["eta2J2max"],
          "flow-revealing pinning and S-lock inequalities are strict")
    check(budget > thresholds["J1"],
          "restricted DC1 requests are initially below the P1C budget")

    for label, expected_root in (
        ("conservative", thresholds["xbar_D_conservative"]),
        ("near_certificate", thresholds["xbar_D_near_certificate"]),
    ):
        dt = dc.world_dts("DC1_flux_lock")[label]

        def quote_difference(stock):
            candidate_state = (12.0, 0.0, stock)
            candidate_drive = sv.drive_no_demand(world, candidate_state)
            _state, _budget, menu = dc.candidate_menu(
                world, candidate_state, candidate_drive, 0, configs[0], dt)
            max_candidates = {candidate["edge"]: candidate for candidate in menu
                              if candidate["frac"] == 1.0}
            values = {edge: dc.quote_schedule_for(
                world, candidate_state, candidate_drive, dt, candidate, 1
            ).exact(candidate["q_acc"])
                      for edge, candidate in max_candidates.items()}
            return values[1] - values[0]

        lower, upper = 0.0, 3.0
        for _ in range(80):
            midpoint = (lower + upper) / 2.0
            if quote_difference(midpoint) > 0.0:
                lower = midpoint
            else:
                upper = midpoint
        root = (lower + upper) / 2.0
        check(close(root, expected_root, 3e-14),
              f"DC1/{label}: registered D threshold root recomputes")

    dc2, *_ = dc.build_world("DC2_capacity_split")
    caps = dc.PLAN["instrument_sensitivity_certificate"] \
        ["DC2_capacity_split"]["caps"]
    computed_caps = {}
    for key, edge, destination in zip(("a", "b", "c"), dc2.edges,
                                      dc2.cells[1:]):
        force_max = 2.0 * edge.eta * destination.alpha * destination.L
        computed_caps[key] = edge.eta * edge.M * (force_max - edge.theta)
    check(computed_caps == caps,
          "DC2 all three maximum service-rate caps recompute exactly")
    check(max(caps.values()) < 1.9,
          "DC2 every one-edge cap is strictly below total demand 1.9")

    for label in dc.DT_LABELS:
        dt = dc.world_dts("DC1_flux_lock")[label]
        pc1 = dc.MEASUREMENT_TICKS * dt * 0.5 - 3.5
        check(close(pc1, dc._PC_BOUNDS["PC1_DC1_S_starves_dst2"][label]),
              f"PC1/{label}: certified starvation bound recomputes")
        check(6.0 - 0.5 == dc._PC_BOUNDS[
            "PC2_DC3_S_misses_pulses"][label],
              f"PC2/{label}: six pulses minus initial buffer equals 5.5")
        floor_stock = 3.0 - dt * 0.5
        force_2 = 4.5 * (5.0 - floor_stock)
        r2_max = 0.9 * 0.08 * (force_2 - 0.05)
        n_b = (dc.MEASUREMENT_TICKS - 1) * 0.5 / r2_max - 1.0
        pc3 = ((n_b - dc.MEASUREMENT_TICKS / 2.0) * dt
               * thresholds["eta1J1"] - dt * (r2_max + 0.5))
        check(close(pc3, dc._PC_BOUNDS[
            "PC3_DC1_A_vs_B_capability_cost"][label]),
              f"PC3/{label}: exact frozen lower-bound formula recomputes")
        dt_dc2 = dc.world_dts("DC2_capacity_split")[label]
        dc2_spec = dc.PLAN["worlds"]["DC2_capacity_split"]
        bank_upper = []
        for edge, destination, initial, cap in zip(
                dc2.edges, dc2.cells[1:], dc2_spec["x0"][1:],
                computed_caps.values()):
            dead_stock = destination.L - edge.theta / (
                2.0 * edge.eta * destination.alpha)
            bank_upper.append(max(initial, dead_stock) + dt_dc2 * cap)
        pc4 = (dc.MEASUREMENT_TICKS * dt_dc2 * 1.9
               - (dc.MEASUREMENT_TICKS * dt_dc2 * max(computed_caps.values())
                  + math.fsum(bank_upper)))
        check(close(pc4, dc._PC_BOUNDS[
            "PC4_DC2_A_vs_B_capacity_gap"][label]),
              f"PC4/{label}: capacity-cap and bank bound recomputes")


def test_controls_hypotheses_and_falsifiers() -> None:
    group("PC1-PC4, F1-F16, H1-H10, and exact F4 threshold")
    check(list(dc.PLAN["hypotheses"]) == [f"H{i}" for i in range(1, 11)],
          "H1-H10 are complete and ordered")
    check(list(dc.PLAN["falsifiers"]) == [f"F{i}" for i in range(1, 17)],
          "F1-F16 are complete and ordered")
    check(list(dc.PLAN["positive_control"]) == list(dc._PC_BOUNDS) + ["rule"],
          "PC1-PC4 are complete and ordered")
    thresholds = dc.positive_control_thresholds()
    for control, bounds in dc._PC_BOUNDS.items():
        for label, bound in bounds.items():
            expected = bound - 1e-9 * (1 + abs(bound))
            check(thresholds[control][label] == expected,
                  f"{control}/{label}: F4 is bound minus exact sole tolerance")
            at_bound = dc.positive_control_result(control, label, bound)
            below = dc.positive_control_result(
                control, label, expected - math.ulp(expected))
            check(not at_bound["f4_fired"] and below["f4_fired"],
                  f"{control}/{label}: one-sided F4 firing rule is executable")
            check(bound > 1e6 * 1e-9 * (1 + abs(bound))
                  and bound >= 5.0,
                  f"{control}/{label}: declared safety-margin rule holds")
    source = inspect.getsource(dc.f4_threshold)
    check("1e-9 * (1 + abs(certified_lower_bound))" in source,
          "F4 source contains the exact registered expression")
    check("max(" not in source and "floor" not in source.split('"""')[-1],
          "F4 implementation has no second slack floor or silent interval")
    check("reported, never tuned away" in dc.PLAN["falsifier_policy"],
          "falsifier policy forbids tuning")
    check("OPEN OUTCOME" in dc.PLAN["hypotheses"]["H5"],
          "D-versus-B remains scientifically open")
    check("EBU per unit" in dc.PLAN["falsifiers"]["F9"],
          "per-unit production ranking remains falsifier F9")
    check("tick other than the current one" in dc.PLAN["falsifiers"]["F10"],
          "future-demand access remains falsifier F10")


def synthetic_run(arm: str, service_value: float, unmet_value: float,
                  ebu: float, feasible: bool = True) -> sv.RunResult:
    service = [service_value] * dc.RUN_TICKS
    unmet = [unmet_value] * dc.RUN_TICKS
    unmet_by_dest = [[0.0, unmet_value] for _ in range(dc.RUN_TICKS)]
    service_by_dest = [[0.0, service_value] for _ in range(dc.RUN_TICKS)]
    return sv.RunResult(
        run_id=f"synthetic|{arm}", world="synthetic", arm=arm,
        dt_label="conservative", dt=0.1, dt_certificate=0.2,
        certificate_kind="gershgorin", r_dt=0.5,
        series={"service": service, "unmet": unmet,
                "unmet_by_dest": unmet_by_dest,
                "service_by_dest": service_by_dest,
                "min_source": [8.0] * dc.RUN_TICKS},
        totals={"ebu": ebu, "reserve_crossings": 0, "allee_crossings": 0,
                "overuse": 0.0, "p1c_rejected": 0,
                "max_ledger_residual": 0.0},
        final={"x": [8.0, 0.0], "burden": 0.0, "dead_sources": 0,
               "negative_state": False, "domain_failure_tick": None,
               "feasible_world": feasible}, x_trajectory_tail=(8.0, 0.0))


def test_predicates_and_precedence() -> None:
    group("frozen Gate 1D predicates, destination channel, and precedence")
    baseline = synthetic_run(dc.EXEC_ARMS[1], 2.0, 0.0, 0.0)
    actor = synthetic_run(dc.EXEC_ARMS[3], 1.0, 2.0, 2.0)
    predicate = sv.service_alignment_predicate(actor, baseline)
    check(predicate["ebu_threshold_met"]
          and predicate["service_condition"]
          and predicate["unmet_condition"]
          and predicate["is_service_alignment_failure"],
          "verbatim total predicate fires on a frozen synthetic positive case")
    destination = dc.per_destination_alignment_predicate(actor, baseline)
    check(destination["any_destination_failure"]
          and destination["destinations"][1]["is_service_alignment_failure"],
          "registered per-destination channel fires with 5%/1.0/20 structure")
    check(not destination["destinations"][0]["is_service_alignment_failure"],
          "per-destination channel does not invent a deficit")
    capability = synthetic_run(dc.EXEC_ARMS[0], 3.0, 0.0, 0.0)
    channels = dc.discriminator_v2_channels(capability, baseline, actor)
    check(channels["i_capability_cost_absolute"] > 0.0
          and channels["ii_service_ratio_delta"] > 0.0
          and channels["iii_max_destination_unmet_delta"] > 0.0
          and channels["world_discriminating"],
          "discriminator_v2 implements all three registered channels")
    flat = dc.discriminator_v2_channels(baseline, baseline, baseline)
    check(not flat["world_discriminating"],
          "F3 antecedent is detectable when every channel is flat")
    no_ebu = synthetic_run(dc.EXEC_ARMS[3], 1.0, 2.0, 1.0)
    check(not sv.service_alignment_predicate(no_ebu, baseline)
          ["is_service_alignment_failure"],
          "EBU threshold is strict: EBU == 1.0 does not fire")
    infeasible = synthetic_run(dc.EXEC_ARMS[3], 1.0, 2.0, 2.0,
                               feasible=False)
    align = sv.service_alignment_predicate(infeasible, baseline)
    check(sv.classify_outcome(infeasible, baseline, align)
          == "physical_impossibility",
          "physical_impossibility precedes distributive under-service")
    check(sv.PERSISTENCE_WINDOW == dc.PERSISTENCE_WINDOW
          and sv.SERVICE_REL == dc.SERVICE_REL
          and sv.SERVICE_ABS == dc.SERVICE_ABS
          and sv.UNMET_REL == dc.UNMET_REL and sv.UNMET_ABS == dc.UNMET_ABS
          and sv.EBU_THRESHOLD == dc.EBU_THRESHOLD and sv.DELTA_R == dc.DELTA_R,
          "all inherited predicate constants are byte-for-byte numeric matches")
    check(sv.PRECEDENCE == (
        "numerical_or_domain_failure", "systemic_collapse",
        "destructive_service", "physical_impossibility",
        "distributive_or_policy_under_service",
        "safe_rationing_physical_scarcity", "preserve_but_under_serve",
        "preserve_and_serve", "unclassified"),
          "outcome-class precedence is unchanged")


def test_output_contract() -> None:
    group("frozen metrics, schemas, filenames, and manifest expectations")
    dc.validate_output_contract()
    check(list(dc.METRIC_FIELDS) == dc.PLAN["metrics_per_run"]
          and len(dc.METRIC_FIELDS) == 24,
          "every registered metric maps once in frozen order")
    required_tick = {field for fields in dc.METRIC_FIELDS.values()
                     for field in fields}
    check(required_tick <= set(dc.TICK_RECORD_FIELDS),
          "tick schema contains every metric realization field")
    check(len(dc.TRACE_PROVENANCE_FIELDS) == len(set(dc.TRACE_PROVENANCE_FIELDS))
          and {"plan_canonical_hash", "plan_raw_sha256", "run_id", "tick",
               "record"} <= set(dc.TRACE_PROVENANCE_FIELDS),
          "trace schema carries unique complete provenance fields")
    check({"runs", "comparisons", "discriminator_v2", "positive_controls",
           "hypotheses", "falsifiers", "outcome_class_counts"}
          <= set(dc.SUMMARY_REQUIRED_BLOCKS),
          "summary schema covers all registered analyses")
    check(dc.FUTURE_ARTIFACTS == (
        "exp_v30_gate1dc.py",
        "results/v3.0/gate1dc/MANIFEST.md",
        "results/v3.0/gate1dc/v30_gate1dc_summary.json",
        "results/v3.0/gate1dc/v30_gate1dc_trace.jsonl.gz",
        "results/v3.0/gate1dc/v30_gate1dc_stdout.txt"),
          "future runner and four artifact filenames are exact")
    check(len(dc.MANIFEST_REQUIRED_SECTIONS) == 10,
          "future manifest contract covers provenance, integrity, science, and limits")
    check(30 * dc.RUN_TICKS == 6000,
          "future trace schema requires exactly 6000 ordered tick rows")
    check(os.path.isfile(dc.FUTURE_ARTIFACTS[0]),
          "the authorized official runner now exists")
    check(not any(os.path.exists(path) for path in dc.FUTURE_ARTIFACTS[1:]),
          "no result directory artifact, stdout, trace, summary, or manifest exists")
    check(json.loads(dc.strict_json_dumps({"x": 1.0})) == {"x": 1.0},
          "strict finite JSON serialization succeeds")
    rejects(lambda: dc.strict_json_dumps({"x": float("nan")}),
            "strict JSON rejects NaN", "Out of range")
    rejects(lambda: dc.strict_json_dumps({"x": float("inf")}),
            "strict JSON rejects Infinity", "Out of range")


def test_static_execution_guards() -> None:
    group("implementation-stage execution and scope guards")
    module_source = open("gate1dc_v30.py", "r", encoding="utf-8").read()
    module_tree = ast.parse(module_source)
    top_level_calls = []
    for node in module_tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            top_level_calls.append(node.value)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            top_level_calls.append(node.value)
    called_names = set()
    for call in top_level_calls:
        if isinstance(call.func, ast.Name):
            called_names.add(call.func.id)
        elif isinstance(call.func, ast.Attribute):
            called_names.add(call.func.attr)
    check(not ({"gate1dc_tick", "run_arm", "bounded_step", "p1c_step",
                "d0_step"} & called_names),
          "module import has no model-step or run call")
    check("import exp_v30_gate1dc" not in module_source,
          "implementation library does not import a runner")
    check("random" not in {alias.name for node in ast.walk(module_tree)
                           if isinstance(node, (ast.Import, ast.ImportFrom))
                           for alias in node.names},
          "implementation imports no randomness module")
    check(set(dc.EXEC_ARMS) == {
        "A_full_multi_edge_p1c", "B_restricted_matched_non_ebu",
        "C_restricted_observational_quote",
        "D_restricted_exact_total_quote_greedy",
        "S_restricted_local_service_priority"},
          "only registered arms A/B/C/D/S are executable")
    check("E_aggregate_source_group_quote" not in dc.EXEC_ARMS,
          "arm E remains non-executable and O3 remains open")
    check("migration" not in {node.id for node in ast.walk(module_tree)
                              if isinstance(node, ast.Name)},
          "no migration or dynamic-topology implementation exists")
    check(os.path.basename(__file__) == "test_v30_gate1dc.py",
          "pre-execution harness filename is exact")


def test_official_runner_static_guards() -> None:
    group("official runner durable ordering and no scientific pre-receipt import")
    source = open("exp_v30_gate1dc.py", "r", encoding="utf-8").read()
    tree = ast.parse(source)
    project_modules = {"d0_v29", "p1c_v29", "ebu_quote_v30",
                       "service_v30", "gate1dc_v30"}
    top_imports = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_imports.add(node.module)
    check(not (top_imports & project_modules),
          "runner imports no project/scientific module before receipt")
    check("if __name__ == \"__main__\":" in source,
          "direct execution is protected by an explicit entry point")
    main_source = inspect.getsource(runner.main)
    ordered_tokens = (
        "preflight()", "_create_result_directory()",
        "_publish_new(RECEIPT", "_verify_published(RECEIPT",
        "_publish_new(EXECUTION_STARTED", "_verify_published(EXECUTION_STARTED",
        "_lock_execution_start()", "_load_scientific_modules(plan)",
        "execute_registered_study(specs)", "write_outputs(",
    )
    positions = [main_source.index(token) for token in ordered_tokens]
    check(positions == sorted(positions),
          "preflight, receipt, start lock, scientific reachability, and outputs are ordered")
    execute_source = inspect.getsource(runner.execute_registered_study)
    check("called.add(run_identifier)" in execute_source
          and execute_source.index("called.add(run_identifier)")
          < execute_source.index("run = dc.run_arm"),
          "run IDs are consumed before invocation so failures cannot retry")
    check("run_fn" not in execute_source and "run_fn" not in main_source,
          "production execution exposes no substitution seam")
    check("for index, spec in enumerate(specs)" in execute_source
          and "sorted(" not in execute_source,
          "execution consumes the provided frozen list without reordering")
    publish_source = inspect.getsource(runner._publish_new)
    check("os.link(temporary, path" in publish_source
          and "os.O_EXCL" in publish_source and "os.fsync" in publish_source,
          "publication is exclusive, hard-linked, and fsynced")
    write_source = inspect.getsource(runner.write_outputs)
    check(write_source.index("_publish_new(TRACE")
          < write_source.index("_publish_new(STDOUT")
          < write_source.index("_publish_new(SUMMARY"),
          "trace, closed stdout, and summary publish in exact order")
    check("_publish_new(MANIFEST" not in source
          and runner.MANIFEST == dc.MANIFEST_PATH,
          "runner never writes the separately finalized manifest")
    check(runner.SUMMARY == dc.SUMMARY_PATH
          and runner.TRACE == dc.TRACE_PATH
          and runner.STDOUT == dc.STDOUT_PATH,
          "runner output filenames exactly match the frozen contract")
    check(tuple(runner.SOURCE_HASH_ORDER) == dc.SOURCE_HASH_ORDER,
          "runner locks all 13 sources in receipt order")
    check(runner.PLAN_RAW == dc.PLAN_RAW and runner.PLAN_CANONICAL == dc.PLAN_CANONICAL
          and runner.CONTRACT_RAW == dc.CONTRACT_RAW
          and runner.CONTRACT_CANONICAL == dc.CONTRACT_CANONICAL,
          "runner and library share raw/canonical plan and contract locks")
    check(runner.strict_dumps({"finite": 1.0}) == '{"finite": 1.0}',
          "runner strict JSON serializes finite synthetic data")
    rejects(lambda: runner.strict_dumps({"bad": float("nan")}),
            "runner strict JSON rejects non-finite synthetic data",
            "Out of range")


def _load_operational_sources():
    contract_raw = open(finalizer.CONTRACT_PATH, "rb").read()
    plan_raw = open(finalizer.PLAN_PATH, "rb").read()
    return (finalizer.strict_json_loads(contract_raw),
            finalizer.strict_json_loads(plan_raw), contract_raw, plan_raw)


def test_operational_hashes_strict_json_and_schemas() -> None:
    group("operational raw/canonical hashes, strict JSON, and exact schemas")
    contract, plan, contract_raw, plan_raw = _load_operational_sources()
    check(hashlib.sha256(contract_raw).hexdigest() == runner.CONTRACT_RAW,
          "contract raw SHA-256 is frozen")
    check(hashlib.sha256(finalizer.canonical_json_bytes(contract)).hexdigest()
          == runner.CONTRACT_CANONICAL,
          "contract canonical SHA-256 is frozen")
    check(hashlib.sha256(plan_raw).hexdigest() == runner.PLAN_RAW
          and hashlib.sha256(finalizer.canonical_json_bytes(plan)).hexdigest()
          == runner.PLAN_CANONICAL,
          "plan raw and canonical SHA-256 values are frozen")
    rejects(lambda: finalizer.strict_json_loads(b'{"x":1,"x":2}'),
            "duplicate object key is rejected", "duplicate")
    rejects(lambda: finalizer.strict_json_loads(b'{"x":NaN}'),
            "non-finite number is rejected", "non-finite")
    rejects(lambda: finalizer.strict_json_loads(b'\xef\xbb\xbf{}'),
            "UTF-8 BOM is rejected", "BOM")
    rejects(lambda: finalizer.strict_json_loads(b'{} trailing'),
            "trailing JSON data is rejected")
    check(tuple(contract["execution_receipt"]["source_hash_order"])
          == runner.SOURCE_HASH_ORDER,
          "receipt source schema has exact 13-path order")
    check(contract["runner_summary_completion_contract"]
          ["required_top_level_fields"] == list(dc.SUMMARY_REQUIRED_BLOCKS),
          "summary top-level schema is exact")
    check(len(contract["failure_retry_matrix"]) == 17,
          "failure/retry matrix has exactly 17 cases")


def test_state_machine_and_all_failure_rows() -> None:
    group("all seven states and all 17 frozen failure/recovery cases")
    snapshots = {
        "FINALIZED": {"recoverable_runner_complete": True,
                      "manifest_valid": True, "manifest_exists": True,
                      "no_unexpected_entries": True, "lock_held": False},
        "RUNNER_COMPLETE": {"recoverable_runner_complete": True,
                            "manifest_exists": False},
        "EXECUTING": {"receipt_valid": True, "start_valid": True,
                      "lock_held": True, "prefix_valid": True,
                      "no_unexpected_entries": True, "manifest_exists": False},
        "ATTEMPT_COMMITTED": {"receipt_valid": True, "start_exists": False,
                              "runner_outputs_exist": False,
                              "manifest_exists": False, "lock_held": False,
                              "no_unexpected_entries": True},
        "PREFLIGHT": {"result_directory_exists": True,
                      "preflight_entries_valid": True, "any_final_exists": False},
        "UNSTARTED": {"result_directory_exists": False},
        "FAILED_OR_INTERRUPTED": {"result_directory_exists": True,
                                  "receipt_valid": False,
                                  "preflight_entries_valid": False},
    }
    for expected, snapshot in snapshots.items():
        check(finalizer.classify_state(snapshot) == expected,
              f"state classifier returns {expected}")
    contract, _plan, _raw, _plan_raw = _load_operational_sources()
    rows = contract["failure_retry_matrix"]
    points = [row["failure_point"] for row in rows]
    check(len(points) == len(set(points)) == 17,
          "all 17 failure points are unique")
    for row in rows:
        check(finalizer.failure_disposition(contract, row["failure_point"]) == row,
              f"failure disposition is exact: {row['failure_point']}")
    check(all(row["scientific_retry"] is False or "Forbidden" in str(
        row["scientific_retry"]) or "Allowed only" in str(row["scientific_retry"])
              for row in rows),
          "every failure row carries an explicit retry disposition")


def _temporary_runner_paths(directory: str):
    outdir = os.path.join(directory, "gate1dc")
    receipt = os.path.join(outdir, "v30_gate1dc_execution_receipt.json")
    start = os.path.join(outdir, "v30_gate1dc_execution_started.json")
    trace = os.path.join(outdir, "v30_gate1dc_trace.jsonl.gz")
    stdout = os.path.join(outdir, "v30_gate1dc_stdout.txt")
    summary = os.path.join(outdir, "v30_gate1dc_summary.json")
    manifest = os.path.join(outdir, "MANIFEST.md")
    finals = (receipt, start, trace, stdout, summary, manifest)
    temporaries = {
        receipt: os.path.join(outdir, ".v30_gate1dc_execution_receipt.json.tmp"),
        start: os.path.join(outdir, ".v30_gate1dc_execution_started.json.tmp"),
        trace: os.path.join(outdir, ".v30_gate1dc_trace.jsonl.gz.tmp"),
        stdout: os.path.join(outdir, ".v30_gate1dc_stdout.txt.tmp"),
        summary: os.path.join(outdir, ".v30_gate1dc_summary.json.tmp"),
        manifest: os.path.join(outdir, ".MANIFEST.md.tmp"),
    }
    return outdir, finals, temporaries


def test_exclusive_publication_fsync_and_same_filesystem() -> None:
    group("fixed-name exclusive hard-link publication and durability")
    original = (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
                runner.TRACE, runner.STDOUT, runner.SUMMARY, runner.MANIFEST,
                runner.TEMPORARY_PATHS, runner.REGISTERED_ARTIFACTS)
    try:
        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            os.mkdir(outdir, 0o700)
            (runner.RECEIPT, runner.EXECUTION_STARTED, runner.TRACE,
             runner.STDOUT, runner.SUMMARY, runner.MANIFEST) = finals
            runner.OUTDIR = outdir
            runner.TEMPORARY_PATHS = temporaries
            runner.REGISTERED_ARTIFACTS = finals
            events = []
            real_fsync = runner.os.fsync

            def fsync_spy(descriptor):
                events.append(stat.S_ISDIR(os.fstat(descriptor).st_mode))
                return real_fsync(descriptor)

            runner.os.fsync = fsync_spy
            try:
                payload = b'{"synthetic":true}\n'
                runner._publish_new(finals[0], payload)
            finally:
                runner.os.fsync = real_fsync
            info = os.lstat(finals[0])
            check(open(finals[0], "rb").read() == payload
                  and stat.S_IMODE(info.st_mode) == 0o444 and info.st_nlink == 1,
                  "published bytes are immutable mode-0444 with one link")
            check(not os.path.lexists(temporaries[finals[0]])
                  and events.count(False) >= 2 and events.count(True) >= 2,
                  "file and directory fsync occur before and after publication")
            check(info.st_dev == os.lstat(outdir).st_dev,
                  "published artifact is on the destination filesystem")
            rejects(lambda: runner._publish_new(finals[0], b"replacement\n"),
                    "publication refuses overwrite")
            check(open(finals[0], "rb").read() == payload,
                  "overwrite refusal preserves original bytes")
    finally:
        (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
         runner.TRACE, runner.STDOUT, runner.SUMMARY, runner.MANIFEST,
         runner.TEMPORARY_PATHS, runner.REGISTERED_ARTIFACTS) = original


def test_runner_publication_cut_points_signals_and_sigkill_stub() -> None:
    group("runner publication power-loss cut points and signal preservation")
    original_paths = (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
                      runner.TRACE, runner.STDOUT, runner.SUMMARY,
                      runner.MANIFEST, runner.TEMPORARY_PATHS,
                      runner.REGISTERED_ARTIFACTS)
    real_fsync, real_link, real_stat = os.fsync, os.link, os.stat
    payload = b'{"synthetic-cut-point":true}\n'
    try:
        for cut in range(1, 5):
            with tempfile.TemporaryDirectory() as directory:
                outdir, finals, temporaries = _temporary_runner_paths(directory)
                os.mkdir(outdir, 0o700)
                (runner.RECEIPT, runner.EXECUTION_STARTED, runner.TRACE,
                 runner.STDOUT, runner.SUMMARY, runner.MANIFEST) = finals
                runner.OUTDIR = outdir
                runner.TEMPORARY_PATHS = temporaries
                runner.REGISTERED_ARTIFACTS = finals
                counter = {"fsync": 0}

                def failing_fsync(descriptor):
                    counter["fsync"] += 1
                    if counter["fsync"] == cut:
                        raise OSError(errno.EIO, "synthetic power-loss cut")
                    return real_fsync(descriptor)

                os.fsync = failing_fsync
                try:
                    rejects(lambda: runner._publish_new(finals[0], payload),
                            f"publication propagates synthetic fsync cut {cut}",
                            "synthetic power-loss cut")
                finally:
                    os.fsync = real_fsync
                temporary_exists = os.path.lexists(temporaries[finals[0]])
                final_exists = os.path.lexists(finals[0])
                expected = {
                    1: (True, False, 0o600, 1),
                    2: (True, False, 0o444, 1),
                    3: (True, True, 0o444, 2),
                    4: (False, True, 0o444, 1),
                }[cut]
                inspected = (temporaries[finals[0]] if temporary_exists
                             else finals[0])
                info = os.lstat(inspected)
                check((temporary_exists, final_exists,
                       stat.S_IMODE(info.st_mode), info.st_nlink) == expected,
                      f"fsync cut {cut} preserves the exact publication residue")

        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            os.mkdir(outdir, 0o700)
            (runner.RECEIPT, runner.EXECUTION_STARTED, runner.TRACE,
             runner.STDOUT, runner.SUMMARY, runner.MANIFEST) = finals
            runner.OUTDIR = outdir
            runner.TEMPORARY_PATHS = temporaries
            runner.REGISTERED_ARTIFACTS = finals

            def failing_link(*_args, **_kwargs):
                raise OSError(errno.EIO, "synthetic link cut")

            os.link = failing_link
            try:
                rejects(lambda: runner._publish_new(finals[0], payload),
                        "publication propagates the synthetic link cut",
                        "synthetic link cut")
            finally:
                os.link = real_link
            info = os.lstat(temporaries[finals[0]])
            check(not os.path.lexists(finals[0])
                  and stat.S_IMODE(info.st_mode) == 0o444
                  and open(temporaries[finals[0]], "rb").read() == payload,
                  "link failure preserves complete immutable temporary bytes")

        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            os.mkdir(outdir, 0o700)
            (runner.RECEIPT, runner.EXECUTION_STARTED, runner.TRACE,
             runner.STDOUT, runner.SUMMARY, runner.MANIFEST) = finals
            runner.OUTDIR = outdir
            runner.TEMPORARY_PATHS = temporaries
            runner.REGISTERED_ARTIFACTS = finals

            def foreign_directory_stat(path, *args, **kwargs):
                info = real_stat(path, *args, **kwargs)
                if path == outdir:
                    fields = list(info)
                    fields[2] += 1
                    return os.stat_result(fields)
                return info

            os.stat = foreign_directory_stat
            try:
                rejects(lambda: runner._publish_new(finals[0], payload),
                        "publication rejects a synthetic cross-filesystem temp",
                        "another filesystem")
            finally:
                os.stat = real_stat
            check(not os.path.lexists(finals[0]),
                  "same-filesystem refusal cannot create a final path")

        for signum in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            rejects(lambda signum=signum: runner._signal_abort(signum, None),
                    f"signal {signum} handler aborts without cleanup",
                    "residues preserved")

        with tempfile.TemporaryDirectory() as directory:
            child = (
                "import os,signal,sys\n"
                "d=sys.argv[1]; t=os.path.join(d,'.artifact.tmp'); "
                "f=os.path.join(d,'artifact')\n"
                "fd=os.open(t,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)\n"
                "os.write(fd,b'synthetic\\n'); os.fsync(fd); "
                "os.fchmod(fd,0o444); os.fsync(fd); os.close(fd)\n"
                "os.link(t,f); dd=os.open(d,os.O_RDONLY); os.fsync(dd); "
                "os.close(dd)\n"
                "os.kill(os.getpid(),signal.SIGKILL)\n"
            )
            completed = subprocess.run(
                (sys.executable, "-B", "-c", child, directory), check=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            temporary = os.path.join(directory, ".artifact.tmp")
            final = os.path.join(directory, "artifact")
            temp_info, final_info = os.lstat(temporary), os.lstat(final)
            check(completed.returncode == -signal.SIGKILL
                  and (temp_info.st_dev, temp_info.st_ino)
                  == (final_info.st_dev, final_info.st_ino)
                  and final_info.st_nlink == 2,
                  "SIGKILL-equivalent child death preserves the durable alias pair")
    finally:
        os.fsync, os.link, os.stat = real_fsync, real_link, real_stat
        (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
         runner.TRACE, runner.STDOUT, runner.SUMMARY, runner.MANIFEST,
         runner.TEMPORARY_PATHS, runner.REGISTERED_ARTIFACTS) = original_paths


def test_pre_receipt_cleanup_and_post_receipt_preservation() -> None:
    group("pre-receipt-only cleanup and post-receipt preservation")
    original = (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
                runner.TRACE, runner.STDOUT, runner.SUMMARY, runner.MANIFEST,
                runner.TEMPORARY_PATHS)
    try:
        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            (runner.RECEIPT, runner.EXECUTION_STARTED, runner.TRACE,
             runner.STDOUT, runner.SUMMARY, runner.MANIFEST) = finals
            runner.OUTDIR = outdir
            runner.TEMPORARY_PATHS = temporaries
            os.mkdir(outdir, 0o700)
            with open(temporaries[finals[0]], "wb") as handle:
                handle.write(b"partial")
            runner._pre_receipt_cleanup()
            check(not os.path.lexists(outdir),
                  "receipt-temporary-only preflight residue is removed")
            os.mkdir(outdir, 0o700)
            with open(finals[0], "wb") as handle:
                handle.write(b"malformed receipt must persist")
            rejects(runner._pre_receipt_cleanup,
                    "malformed/partial final receipt blocks cleanup and retry",
                    "forbidden")
            check(open(finals[0], "rb").read() == b"malformed receipt must persist",
                  "post-receipt residue is preserved byte-for-byte")
    finally:
        (runner.OUTDIR, runner.RECEIPT, runner.EXECUTION_STARTED,
         runner.TRACE, runner.STDOUT, runner.SUMMARY, runner.MANIFEST,
         runner.TEMPORARY_PATHS) = original


def test_manifest_publication_cut_points_and_resume() -> None:
    group("manifest publication cut points and exact deterministic resume")
    original_paths = (finalizer.RESULT_DIRECTORY, finalizer.RECEIPT_PATH,
                      finalizer.START_PATH, finalizer.TRACE_PATH,
                      finalizer.STDOUT_PATH, finalizer.SUMMARY_PATH,
                      finalizer.MANIFEST_PATH, finalizer.FINAL_PATHS,
                      finalizer.TEMPORARY_PATHS)
    real_fsync, real_link = os.fsync, os.link
    payload = b"# Synthetic deterministic manifest\n"
    try:
        for cut in range(1, 5):
            with tempfile.TemporaryDirectory() as directory:
                outdir, finals, temporaries = _temporary_runner_paths(directory)
                os.mkdir(outdir, 0o700)
                (finalizer.RECEIPT_PATH, finalizer.START_PATH,
                 finalizer.TRACE_PATH, finalizer.STDOUT_PATH,
                 finalizer.SUMMARY_PATH, finalizer.MANIFEST_PATH) = finals
                finalizer.RESULT_DIRECTORY = outdir
                finalizer.FINAL_PATHS = finals
                finalizer.TEMPORARY_PATHS = temporaries
                counter = {"fsync": 0}

                def failing_fsync(descriptor):
                    counter["fsync"] += 1
                    if counter["fsync"] == cut:
                        raise OSError(errno.EIO, "synthetic manifest fsync cut")
                    return real_fsync(descriptor)

                os.fsync = failing_fsync
                try:
                    rejects(lambda: finalizer._publish_manifest(payload),
                            f"manifest propagates synthetic fsync cut {cut}",
                            "synthetic manifest fsync cut")
                finally:
                    os.fsync = real_fsync
                temporary_exists = os.path.lexists(temporaries[finals[5]])
                final_exists = os.path.lexists(finals[5])
                expected = {
                    1: (True, False, 0o600, 1),
                    2: (True, False, 0o444, 1),
                    3: (True, True, 0o444, 2),
                    4: (False, True, 0o444, 1),
                }[cut]
                inspected = temporaries[finals[5]] if temporary_exists else finals[5]
                info = os.lstat(inspected)
                check((temporary_exists, final_exists,
                       stat.S_IMODE(info.st_mode), info.st_nlink) == expected,
                      f"manifest fsync cut {cut} preserves exact residue")
                if cut == 1:
                    rejects(lambda: finalizer._publish_manifest(payload),
                            "mode-0600 incomplete manifest temporary is not resumable",
                            "cannot be resumed")
                    check(os.path.lexists(temporaries[finals[5]])
                          and not os.path.lexists(finals[5]),
                          "invalid manifest temporary remains untouched")
                else:
                    finalizer._publish_manifest(payload)
                    final_info = os.lstat(finals[5])
                    check(open(finals[5], "rb").read() == payload
                          and stat.S_IMODE(final_info.st_mode) == 0o444
                          and final_info.st_nlink == 1
                          and not os.path.lexists(temporaries[finals[5]]),
                          f"manifest fsync cut {cut} resumes without overwrite")

        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            os.mkdir(outdir, 0o700)
            (finalizer.RECEIPT_PATH, finalizer.START_PATH,
             finalizer.TRACE_PATH, finalizer.STDOUT_PATH,
             finalizer.SUMMARY_PATH, finalizer.MANIFEST_PATH) = finals
            finalizer.RESULT_DIRECTORY = outdir
            finalizer.FINAL_PATHS = finals
            finalizer.TEMPORARY_PATHS = temporaries

            def failing_link(*_args, **_kwargs):
                raise OSError(errno.EIO, "synthetic manifest link cut")

            os.link = failing_link
            try:
                rejects(lambda: finalizer._publish_manifest(payload),
                        "manifest propagates the synthetic link cut",
                        "synthetic manifest link cut")
            finally:
                os.link = real_link
            finalizer._publish_manifest(payload)
            check(open(finals[5], "rb").read() == payload
                  and not os.path.lexists(temporaries[finals[5]]),
                  "link-cut manifest resumes from exact immutable temporary")
    finally:
        os.fsync, os.link = real_fsync, real_link
        (finalizer.RESULT_DIRECTORY, finalizer.RECEIPT_PATH,
         finalizer.START_PATH, finalizer.TRACE_PATH, finalizer.STDOUT_PATH,
         finalizer.SUMMARY_PATH, finalizer.MANIFEST_PATH,
         finalizer.FINAL_PATHS, finalizer.TEMPORARY_PATHS) = original_paths


def test_deterministic_gzip_and_control_field_order() -> None:
    group("deterministic gzip and exact receipt/start field order")
    rows = [{"index": index, "finite": float(index)} for index in range(6000)]
    first = finalizer.deterministic_gzip(rows)
    second = finalizer.deterministic_gzip(copy.deepcopy(rows))
    lines = gzip.decompress(first).splitlines(keepends=True)
    check(first == second and len(lines) == 6000,
          "6000-row gzip is byte-deterministic")
    check(all(finalizer.canonical_json_bytes(row) + b"\n" == line
              for row, line in zip(rows, lines)),
          "every trace line is canonical strict JSON plus one LF")
    check(first[:10] == b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff",
          "gzip header has empty filename, mtime=0, level-9 flags, no extras")
    contract, _plan, _raw, _plan_raw = _load_operational_sources()
    repository = {
        "execution_sha": "a" * 40,
        "source_sha256": {path: "b" * 64 for path in runner.SOURCE_HASH_ORDER},
        "python": {"invoked_as": runner.PYTHON_INVOKED_AS,
                   "executable_realpath": runner.PYTHON_REALPATH,
                   "version": runner.PYTHON_VERSION,
                   "zlib_version": runner.ZLIB_VERSION,
                   "zlib_runtime_version": runner.ZLIB_VERSION,
                   "flags": ["-B", "-s", "-X", "utf8"]},
    }
    receipt = runner._build_receipt(repository)
    receipt_bytes = runner.ordered_bytes(receipt)
    runner._validate_receipt_bytes(receipt, receipt_bytes, contract)
    started = runner._build_execution_start(receipt, receipt_bytes)
    check(list(receipt) == contract["execution_receipt"]["field_order"],
          "receipt fields use exact registered insertion order")
    check(list(started) == contract["execution_started_control"]["field_order"],
          "execution-start fields use exact registered insertion order")


def _synthetic_manifest_inputs():
    contract, plan, _contract_raw, _plan_raw = _load_operational_sources()
    run_ids = contract["registered_execution_inventory"]["run_ids"]
    source_hashes = {path: hashlib.sha256(path.encode()).hexdigest()
                     for path in finalizer.SOURCE_HASH_ORDER}
    receipt = {
        "attempt_id": finalizer.ATTEMPT_ID,
        "authorized_execution_sha": "a" * 40,
        "source_sha256": source_hashes,
    }
    start = {"phase": "scientific_execution_reachable"}
    summary = {
        "execution_sha": "a" * 40, "n_runs": 30,
        "registered": {"frozen_order": list(run_ids)},
        "runs": {run_id: {"run_id": run_id, "total_service": 0.0,
                           "total_unmet": 0.0, "ebu_total": 0.0, "r_dt": 0.5}
                 for run_id in run_ids},
        "positive_controls": {}, "hypotheses": {}, "falsifiers": {},
        "discriminator_v2": {},
        "o3_aggregate_diagnostic": {
            "arm_A_ticks": 1200, "multi_action_ticks": 0,
            "total_group_quote": 0.0, "total_naive_independent_sum": 0.0,
            "total_double_count": 0.0, "nothing_settled_or_allocated": True,
            "note": "settlement-free diagnostic only; O3 remains open"},
        "outcome_class_counts": {"unclassified": 30},
        "non_claims": list(plan["non_claims"]),
    }
    for control in finalizer.CONTROL_ORDER:
        summary["positive_controls"][control] = {}
        for label in finalizer.DT_ORDER:
            bound = plan["positive_control"][control]["certified_lower_bound"][label]
            threshold = bound - 1e-9 * (1 + abs(bound))
            summary["positive_controls"][control][label] = {
                "measured_as": plan["positive_control"][control]["measured_as"],
                "certified_lower_bound": bound, "f4_threshold": threshold,
                "executed_value": bound, "f4_fired": False,
            }
    for index in range(1, 11):
        summary["hypotheses"][f"H{index}"] = {
            "status": "synthetic", "evidence": {"fixture": True}}
    for index in range(1, 17):
        summary["falsifiers"][f"F{index}"] = {
            "fired": False, "evidence": {"fixture": True}}
    for world in finalizer.WORLD_ORDER:
        for label in finalizer.DT_ORDER:
            summary["discriminator_v2"][f"{world}|{label}"] = {
                "i_capability_cost_absolute": 0.0,
                "ii_service_ratio_delta": 0.0,
                "iii_max_destination_unmet_delta": 0.0,
                "world_discriminating": False,
            }
    artifacts = {path: {"bytes": index, "sha256": f"{index:064x}"}
                 for index, path in enumerate(finalizer.FINAL_PATHS[:5], 1)}
    return receipt, start, summary, plan, contract, artifacts


def test_manifest_exact_rendering_and_sentinels() -> None:
    group("pure exact 12-section manifest rendering and sentinel separation")
    receipt, start, summary, plan, contract, artifacts = \
        _synthetic_manifest_inputs()
    first = finalizer.render_manifest(receipt, start, summary, plan, contract,
                                      artifacts)
    second = finalizer.render_manifest(copy.deepcopy(receipt),
                                       copy.deepcopy(start),
                                       copy.deepcopy(summary), plan, contract,
                                       copy.deepcopy(artifacts))
    text = first.decode("utf-8")
    check(first == second, "independent manifest rerender is byte-identical")
    check(text.startswith(contract["manifest_rendering"]["title"] + "\n\n")
          and first.endswith(b"\n") and not first.endswith(b"\n\n"),
          "title and exact final-LF grammar are fixed")
    positions = [text.index(heading) for heading in
                 contract["manifest_rendering"]["section_order"]]
    check(positions == sorted(positions) and len(positions) == 12
          and all(text.count(heading) == 1 for heading in
                  contract["manifest_rendering"]["section_order"]),
          "all 12 headings occur in exact order")
    fixed_text = [paragraph
                  for section in contract["manifest_rendering"]["sections"]
                  for key in ("fixed_paragraphs", "fixed_limitations")
                  for paragraph in section.get(key, [])]
    check(all(paragraph in text for paragraph in fixed_text),
          "every fixed paragraph and limitation is rendered verbatim")
    check(text.count("| present | 200 | 1–200 |") == 30
          and all(text.index(control) < text.index(finalizer.CONTROL_ORDER[-1])
                  for control in finalizer.CONTROL_ORDER[:-1])
          and all(f"| {index} | {outcome} |" in text
                  for index, outcome in enumerate(finalizer.OUTCOME_ORDER, 1)),
          "inventory, PC1-PC4, and all nine outcome rows are complete and ordered")
    check(all(statement in text for statement in plan["non_claims"])
          and all(f"| H{index} |" in text for index in range(1, 11))
          and all(f"| F{index} |" in text for index in range(1, 17)),
          "all frozen nonclaims, H1-H10, and F1-F16 rows are present")
    check("summary plus trace never constitutes a finalized study" in text
          and "MANIFEST.md establishes finalization" in text,
          "runner completion and full-study finalization are distinct")
    check("Next possible stage: separately authorized scientific interpretation"
          in text and "It has not begun" in text,
          "exact next-stage-not-begun sentence is rendered")
    check("MANIFEST.md does not contain its own hash" in text
          and "not self-hashed" in text,
          "recursive manifest hashing is refused by the schema")
    missing = copy.deepcopy(summary)
    del missing["hypotheses"]["H10"]
    rejects(lambda: finalizer.render_manifest(
        receipt, start, missing, plan, contract, artifacts),
        "missing manifest pointer fails closed")
    nonfinite = copy.deepcopy(summary)
    nonfinite["discriminator_v2"][
        "DC1_flux_lock|conservative"]["i_capability_cost_absolute"] = float("nan")
    rejects(lambda: finalizer.render_manifest(
        receipt, start, nonfinite, plan, contract, artifacts),
        "non-finite manifest pointer fails closed", "non-finite")
    check(finalizer.render_cell("a\\b|c\r\nd") == "a\\\\b\\|c<br>d",
          "manifest cell escaping is exact")


def test_finalizer_import_and_scientific_prohibitions() -> None:
    group("finalizer zero-side-effect import shape and scientific prohibition")
    source = open("finalize_v30_gate1dc.py", "r", encoding="utf-8").read()
    tree = ast.parse(source)
    project = {"gate1dc_v30", "exp_v30_gate1dc", "service_v30", "d0_v29",
               "p1c_v29", "ebu_quote_v30"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    check(not (imports & project), "finalizer contains no scientific/project import")
    forbidden_calls = {"run_arm", "gate1dc_tick", "bounded_step", "p1c_step",
                       "classify_outcome", "service_alignment_predicate",
                       "build_quote", "world_certificates"}
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    check(not (calls & forbidden_calls),
          "finalizer contains no scientific function call")
    allowed_top = (ast.Expr, ast.Import, ast.ImportFrom, ast.Assign,
                   ast.AnnAssign, ast.ClassDef, ast.FunctionDef, ast.If)
    check(all(isinstance(node, allowed_top) for node in tree.body),
          "finalizer import body contains only declarations and guarded entry point")
    entry = tree.body[-1]
    check(isinstance(entry, ast.If)
          and isinstance(entry.test, ast.Compare),
          "all finalization work is behind the explicit __main__ guard")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        (sys.executable, "-B", "-c", "import finalize_v30_gate1dc"),
        cwd=os.getcwd(), env=environment, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    check(completed.returncode == 0 and completed.stdout == b""
          and completed.stderr == b"",
          "isolated finalizer import exits silently without executing finalization")


def test_refusal_guards_and_no_stdout_after_summary() -> None:
    group("refusal guards, exact paths, and no post-summary stdout")
    runner_source = open("exp_v30_gate1dc.py", "r", encoding="utf-8").read()
    finalizer_source = open("finalize_v30_gate1dc.py", "r", encoding="utf-8").read()
    preflight_source = inspect.getsource(runner.preflight)
    repository_source = inspect.getsource(runner._validate_repository)
    check(preflight_source.index("_validate_runtime()")
          < preflight_source.index("_validate_contract_and_plan()")
          < preflight_source.index("_validate_repository"),
          "environment/schema/Git checks are complete pre-receipt")
    check("ls-remote" in repository_source and "porcelain=v2" in repository_source
          and "worktree/Git blob byte mismatch" in repository_source,
          "live ref, dirty tree, and source blob mismatches fail closed")
    check("unregistered publication path" in runner_source
          and "FileExistsError" in runner_source
          and "another filesystem" in runner_source,
          "alternate paths, overwrite, and filesystem substitutions are refused")
    write_source = inspect.getsource(runner.write_outputs)
    main_source = inspect.getsource(runner.main)
    after_summary = write_source[write_source.index("_publish_new(SUMMARY"):]
    check("_publish_new(STDOUT" not in after_summary
          and "_verify_published(STDOUT" not in after_summary,
          "stdout has no reachable write after summary publication")
    check(main_source.index("_publish_new(RECEIPT")
          < main_source.index("_load_scientific_modules"),
          "receipt durability precedes scientific import reachability")
    finalize_source = inspect.getsource(finalizer.finalize)
    numbered = [finalize_source.index(f"# {index}.") for index in range(1, 16)]
    check(numbered == sorted(numbered),
          "finalizer implements the exact numbered 1-through-15 sequence")
    check("Accept no manual parameter" in open(
        finalizer.CONTRACT_PATH, "r", encoding="utf-8").read()
          or "Accept no manual parameter" in finalizer_source,
          "manual finalization inputs are prohibited")


def test_operational_refusal_stubs_and_sentinel_states() -> None:
    group("runtime, Git, path, artifact, and sentinel refusal stubs")
    original_argv = runner.sys.argv
    runner.sys.argv = ["exp_v30_gate1dc.py", "--forbidden"]
    try:
        rejects(runner._validate_runtime,
                "runner rejects every command-line substitution", "no arguments")
    finally:
        runner.sys.argv = original_argv

    original_git, original_git_bytes = finalizer._git, finalizer._git_bytes
    authorized_sha = "a" * 40

    def valid_git(*arguments):
        command = tuple(arguments)
        if command == ("rev-parse", "--show-toplevel"):
            return finalizer.REPOSITORY_ROOT
        if command == ("symbolic-ref", "--quiet", "--short", "HEAD"):
            return finalizer.BRANCH
        if command in (("rev-parse", "HEAD"),
                       ("rev-parse", f"refs/remotes/origin/{finalizer.BRANCH}")):
            return authorized_sha
        if command == ("status", "--porcelain=v2", "--untracked-files=all"):
            return "1 .M N... 100644 100644 100644 deadbeef deadbeef gate1dc_v30.py"
        raise AssertionError(command)

    def valid_live(*_arguments, **_kwargs):
        return f"{authorized_sha}\t{finalizer.REMOTE_REF}\n".encode()

    finalizer._git, finalizer._git_bytes = valid_git, valid_live
    try:
        rejects(lambda: finalizer._validate_git_state(authorized_sha),
                "dirty tracked worktree is refused", "unexpected worktree")

        def wrong_ref_git(*arguments):
            if tuple(arguments) == ("rev-parse", "HEAD"):
                return "b" * 40
            return valid_git(*arguments)

        finalizer._git = wrong_ref_git
        rejects(lambda: finalizer._validate_git_state(authorized_sha),
                "local/ref mismatch is refused", "identity mismatch")

        def clean_git(*arguments):
            if tuple(arguments) == (
                    "status", "--porcelain=v2", "--untracked-files=all"):
                return "\n".join(f"? {path}" for path in finalizer.FINAL_PATHS[:5])
            return valid_git(*arguments)

        finalizer._git = clean_git
        finalizer._git_bytes = lambda *_args, **_kwargs: (
            f"{'b' * 40}\t{finalizer.REMOTE_REF}\n".encode())
        rejects(lambda: finalizer._validate_git_state(authorized_sha),
                "live remote mismatch is refused", "live remote ref differs")
    finally:
        finalizer._git, finalizer._git_bytes = original_git, original_git_bytes

    rejects(lambda: runner._publish_new("/tmp/unregistered-gate1dc-path",
                                        b"forbidden\n"),
            "alternate publication path is refused", "unregistered")

    original_paths = (finalizer.RESULT_DIRECTORY, finalizer.RECEIPT_PATH,
                      finalizer.START_PATH, finalizer.TRACE_PATH,
                      finalizer.STDOUT_PATH, finalizer.SUMMARY_PATH,
                      finalizer.MANIFEST_PATH, finalizer.FINAL_PATHS,
                      finalizer.TEMPORARY_PATHS)
    try:
        with tempfile.TemporaryDirectory() as directory:
            outdir, finals, temporaries = _temporary_runner_paths(directory)
            os.mkdir(outdir, 0o700)
            with open(os.path.join(outdir, "unexpected-artifact"), "wb") as handle:
                handle.write(b"synthetic")
            (finalizer.RECEIPT_PATH, finalizer.START_PATH,
             finalizer.TRACE_PATH, finalizer.STDOUT_PATH,
             finalizer.SUMMARY_PATH, finalizer.MANIFEST_PATH) = finals
            finalizer.RESULT_DIRECTORY = outdir
            finalizer.FINAL_PATHS = finals
            finalizer.TEMPORARY_PATHS = temporaries
            rejects(finalizer._validate_entries_and_inputs,
                    "unexpected result-directory artifact is refused",
                    "unexpected result-directory")
    finally:
        (finalizer.RESULT_DIRECTORY, finalizer.RECEIPT_PATH,
         finalizer.START_PATH, finalizer.TRACE_PATH, finalizer.STDOUT_PATH,
         finalizer.SUMMARY_PATH, finalizer.MANIFEST_PATH,
         finalizer.FINAL_PATHS, finalizer.TEMPORARY_PATHS) = original_paths

    incomplete = {
        "result_directory_exists": True, "receipt_valid": True,
        "start_valid": True, "start_exists": True, "lock_held": False,
        "prefix_valid": True, "no_unexpected_entries": True,
        "manifest_exists": False, "recoverable_runner_complete": False,
    }
    check(finalizer.classify_state(incomplete) == "FAILED_OR_INTERRUPTED",
          "summary-plus-trace or released incomplete prefix is never FINALIZED")


def main() -> int:
    test_plan_lock_and_schema()
    test_worlds_and_demand()
    test_certificates_and_inventory()
    test_menu_filtering_and_identity()
    test_selectors_and_quotes()
    test_information_boundary()
    test_analytic_certificates()
    test_controls_hypotheses_and_falsifiers()
    test_predicates_and_precedence()
    test_output_contract()
    test_static_execution_guards()
    test_official_runner_static_guards()
    test_operational_hashes_strict_json_and_schemas()
    test_state_machine_and_all_failure_rows()
    test_exclusive_publication_fsync_and_same_filesystem()
    test_runner_publication_cut_points_signals_and_sigkill_stub()
    test_pre_receipt_cleanup_and_post_receipt_preservation()
    test_manifest_publication_cut_points_and_resume()
    test_deterministic_gzip_and_control_field_order()
    test_manifest_exact_rendering_and_sentinels()
    test_finalizer_import_and_scientific_prohibitions()
    test_refusal_guards_and_no_stdout_after_summary()
    test_operational_refusal_stubs_and_sentinel_states()
    print(f"\nGate 1D-C pre-execution: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
