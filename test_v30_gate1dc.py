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
import hashlib
import inspect
import json
import math
import os
import tempfile

import d0_v29 as d0
import exp_v30_gate1dc as runner
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
    except (AssertionError, KeyError, TypeError, ValueError, SystemExit) as error:
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
    group("official runner preflight, single-execution, and finalization guards")
    source = open("exp_v30_gate1dc.py", "r", encoding="utf-8").read()
    tree = ast.parse(source)
    top_level_calls = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            top_level_calls.append(node.value)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            top_level_calls.append(node.value)
    names = set()
    for call in top_level_calls:
        if isinstance(call.func, ast.Name):
            names.add(call.func.id)
        elif isinstance(call.func, ast.Attribute):
            names.add(call.func.attr)
    check(not ({"main", "preflight", "execute_registered_study", "run_arm",
                "gate1dc_tick", "bounded_step", "p1c_step"} & names),
          "runner import has no execution, preflight, step, print, or write call")
    check("if __name__ == \"__main__\":" in source,
          "direct execution is protected by an explicit entry point")
    main_source = inspect.getsource(runner.main)
    check(main_source.index("preflight()")
          < main_source.index("execute_registered_study"),
          "complete preflight precedes the only study-execution call")
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
    check("os.link(temporary, path)" in inspect.getsource(runner._publish_new),
          "artifact publication is atomic and cannot overwrite an existing path")
    write_source = inspect.getsource(runner.write_outputs)
    check(write_source.index("_publish_new(TRACE")
          < write_source.index("_publish_new(SUMMARY"),
          "trace publishes before the summary completion sentinel")
    check("_publish_new(MANIFEST" not in source
          and runner.MANIFEST == dc.MANIFEST_PATH,
          "runner never writes the separately finalized manifest")
    check(runner.SUMMARY == dc.SUMMARY_PATH
          and runner.TRACE == dc.TRACE_PATH
          and runner.STDOUT == dc.STDOUT_PATH,
          "runner output filenames exactly match the frozen contract")
    check(tuple(runner.REQUIRED_SOURCE_HASHES) == (
        "AGENTS.md", "V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md",
        "v30_gate1dc_outcome_discrimination_plan.json", "gate1dc_v30.py",
        "test_v30_gate1dc.py", "d0_v29.py", "p1c_v29.py",
        "ebu_quote_v30.py", "service_v30.py"),
          "preflight locks every authoritative and scientific source")
    check("TO_BE_LOCKED" not in runner.REQUIRED_SOURCE_HASHES[
        "test_v30_gate1dc.py"],
          "runner-validation source hash is finalized, not a placeholder")
    check(runner.PLAN_RAW == dc.PLAN_RAW
          and runner.PLAN_CANONICAL == dc.PLAN_CANONICAL,
          "runner and implementation share both plan hash locks")
    check(set(dc.TICK_RECORD_FIELDS) <= set(runner.REQUIRED_TICK_FIELDS),
          "runner tick schema contains every frozen metric field")

    original = (runner.OUTDIR, runner.STDOUT, runner.SUMMARY,
                runner.TRACE, runner.MANIFEST)
    try:
        with tempfile.TemporaryDirectory() as directory:
            runner.OUTDIR = directory
            runner.STDOUT = os.path.join(directory, "stdout.txt")
            runner.SUMMARY = os.path.join(directory, "summary.json")
            runner.TRACE = os.path.join(directory, "trace.jsonl.gz")
            runner.MANIFEST = os.path.join(directory, "MANIFEST.md")
            with open(runner.STDOUT, "wb") as handle:
                runner._validate_output_start(stdout_fd=handle.fileno())
                check(True,
                      "fresh empty stdout attached to the supplied fd passes")
            with open(runner.TRACE, "wb") as handle:
                handle.write(b"orphan")
            with open(runner.STDOUT, "rb") as handle:
                rejects(lambda: runner._validate_output_start(
                    stdout_fd=handle.fileno()),
                        "an orphan registered artifact causes refusal",
                        "fresh stdout capture")
            os.unlink(runner.TRACE)
            with open(runner.STDOUT, "wb") as handle:
                handle.write(b"prior output")
            with open(runner.STDOUT, "rb") as handle:
                rejects(lambda: runner._validate_output_start(
                    stdout_fd=handle.fileno()),
                        "a nonempty stdout artifact causes refusal",
                        "already contains data")
    finally:
        (runner.OUTDIR, runner.STDOUT, runner.SUMMARY,
         runner.TRACE, runner.MANIFEST) = original

    production_calls = []
    original_run_arm = runner.dc.run_arm
    try:
        runner.dc.run_arm = lambda *args, **kwargs: production_calls.append(
            (args, kwargs))
        rejects(runner.preflight,
                "committed preflight refuses before execution without the "
                "fresh exclusive stdout capture", "does not exist")
        check(production_calls == [],
              "failed preflight cannot reach the production execution function")
    finally:
        runner.dc.run_arm = original_run_arm

    specs = dc.build_run_specs()
    check([spec["run_id"] for spec in specs] == [
        dc.run_id(world, arm, label)
        for world in dc.WORLD_NAMES for label in dc.DT_LABELS
        for arm in dc.EXEC_ARMS],
          "runner receives all 30 run IDs in exact world/dt/arm order")
    check(len(specs) * dc.RUN_TICKS == 6000,
          "runner row contract is 30 x 200 = 6000 without generating rows")
    check(runner.strict_dumps({"finite": 1.0}) == '{"finite": 1.0}',
          "runner strict JSON serializes finite synthetic data")
    rejects(lambda: runner.strict_dumps({"bad": float("nan")}),
            "runner strict JSON rejects non-finite synthetic data",
            "Out of range")


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
    print(f"\nGate 1D-C pre-execution: {PASSED} passed, {FAILED} failed, "
          f"{GROUPS} groups")
    print("Model-state advancement: NONE; registered runs generated: 0")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
