"""
V3.0 Gate 1D-B / O14 OFFICIAL RUNNER for the locked multi-out-edge
capability study (plan v30_o14_multi_edge_plan.json).

EXECUTES THE REGISTERED STUDY EXACTLY ONCE when - and only when - the
separately authorized execution gate invokes:

    mkdir -p results/v3.0/gate1db     # non-scientific filesystem preparation
    python3 exp_v30_o14.py > results/v3.0/gate1db/v30_o14_stdout.txt

IMPORTING THIS MODULE IS SIDE-EFFECT FREE: no trajectory, no directory, no
file, no print. All work happens inside main(), which the runner-preparation
gate never calls.

DISCIPLINE
  * fail-closed preflight (plan hashes, schema, certificates, run inventory,
    output sentinels) completes BEFORE the first trajectory;
  * takes NO command-line option and no scientific override of any kind;
  * REFUSES to overwrite a completed study (the summary is the completion
    sentinel) and REFUSES to run over an orphan trace/manifest (a partial or
    ambiguous prior attempt requires separate human authorization);
  * executes exactly o14.build_run_specs() in its frozen order: 60 runs x
    200 ticks, no seed, no retry, no filtering, no subset, no rerun;
  * a domain failure or a fired scientific falsifier is a REPORTED OUTCOME,
    never an excuse to drop, rerun or tune a registered run; only integrity
    failures stop execution;
  * strict JSON everywhere (allow_nan=False); deterministic gzip (mtime=0);
    the trace is written first, the summary LAST (completion sentinel);
    MANIFEST.md is NOT written here (post-execution validation stage);
  * arm A settles nothing: its EBU must be exactly zero (O3 stays open).

The `run_fn` parameter of execute_registered_study/main is a TEST SEAM for
the pre-execution suite's mocks only; it defaults to the production
o14.run_arm and offers no scientific choice.

Numerical results will not prove alignment or safety; O3, O12 and O13 stay
open; Gate 1E and Gate 2 remain paused. Standard library only; never
imports a test module.
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import os
import platform
import sys
import tempfile

import ebu_quote_v30 as eq
import service_v30 as sv
import o14_v30 as o14

PLAN_CANONICAL = ("2524ba268db004969e04f9c8636cc240b643f0f7"
                  "685507edf65350ea98a37745")
PLAN_RAW = ("00c4dd472eb332e57865f845e41265032fa69ef3"
            "535bb170a8ade013f783d22a")

OUTDIR = "results/v3.0/gate1db"
SUMMARY = "results/v3.0/gate1db/v30_o14_summary.json"
TRACE = "results/v3.0/gate1db/v30_o14_trace.jsonl.gz"
MANIFEST = "results/v3.0/gate1db/MANIFEST.md"   # NEVER written by the runner
STDOUT_NAME = "v30_o14_stdout.txt"              # created by shell redirection

PRIMARY_BASELINE_ARM = "B_restricted_matched_non_ebu"
ARM_A = "A_full_multi_edge_p1c"
ARM_B = "B_restricted_matched_non_ebu"
ARM_C = "C_restricted_observational_quote"
ARM_D = "D_restricted_exact_total_quote_greedy"
ARM_S = "S_restricted_local_service_priority"

# every field o14_tick emits; all are required in every retained record
REQUIRED_TICK_FIELDS = (
    "tick", "arm", "dt", "x_before", "x_after", "u", "active_out_edges",
    "menus", "candidate_exact_quotes", "candidate_per_unit_quotes",
    "candidate_continuous_vertices", "selected", "rested", "executed_q_acc",
    "q_req", "delivered", "sigma", "budget_utilization", "service", "unmet",
    "demand_amount", "transport_loss", "negative_corrections",
    "ledger_residual", "domain_failure", "reserve_crossings",
    "allee_crossings", "physical_overuse", "min_source", "burden",
    "viability", "ebu", "ebu_pos", "ebu_neg", "quoted", "group_diagnostic")

# physical per-tick fields for the B-vs-C identity (EBU/quote fields and the
# arm label are excluded: B carries no EBU, C records observational EBU)
PHYS_TICK_FIELDS = (
    "x_before", "x_after", "u", "active_out_edges", "menus", "selected",
    "rested", "executed_q_acc", "q_req", "delivered", "sigma",
    "budget_utilization", "service", "unmet", "demand_amount",
    "transport_loss", "negative_corrections", "ledger_residual",
    "domain_failure", "reserve_crossings", "allee_crossings",
    "physical_overuse", "min_source", "burden", "viability",
    "candidate_continuous_vertices")

_NUM_TOL = 1e-9      # registered 1e-9-scale reporting tolerance (sv.tol)


def _fatal(msg: str):
    raise SystemExit(f"FATAL: {msg}")


def _assert_finite(obj, path: str) -> None:
    """Fail closed on any NaN/Infinity anywhere in a record. None is the
    only permitted representation of an undefined optional diagnostic."""
    if isinstance(obj, float):
        if not math.isfinite(obj):
            _fatal(f"non-finite value at {path}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _assert_finite(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _assert_finite(v, f"{path}[{i}]")


def strict_dumps(obj, **kw) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, **kw)


# ---------------------------------------------------------------------------
# preflight - must complete before the first trajectory
# ---------------------------------------------------------------------------
def preflight() -> list:
    """Fail-closed integrity preflight. Returns the frozen run specs.
    Scientific falsifiers are NOT preflight failures - they are reported
    outcomes of the study; only integrity failures stop execution."""
    if len(sys.argv) > 1:
        _fatal("this harness takes no command-line option and no "
               "scientific parameter override")
    raw = open(o14.PLAN_PATH, "rb").read()
    if hashlib.sha256(raw).hexdigest() != PLAN_RAW:
        _fatal("raw O14 plan SHA-256 mismatch")
    plan = json.loads(raw, parse_constant=o14._reject_nonfinite)
    if o14.plan_canonical_hash(plan) != PLAN_CANONICAL:
        _fatal("canonical O14 plan hash mismatch")
    if o14.PLAN_CANONICAL != PLAN_CANONICAL or o14.PLAN_RAW != PLAN_RAW:
        _fatal("o14_v30 locked hash constants disagree with the runner")
    o14.validate_plan(plan)
    specs = o14.build_run_specs()
    if len(specs) != 60 or len({s["run_id"] for s in specs}) != 60:
        _fatal("run inventory is not exactly 60 unique specifications")
    expected = {f"{w}|{a}|{l}" for w in o14.WORLD_NAMES
                for a in o14.EXEC_ARMS for l in o14.DT_LABELS}
    if {s["run_id"] for s in specs} != expected:
        _fatal("run inventory differs from the registered Cartesian product")
    if any("E_aggregate" in s["arm"] for s in specs):
        _fatal("an arm-E specification exists (E is not executable)")
    for fname in ("o14_v30.py", "exp_v30_o14.py"):
        src = open(fname).read()
        if "import random" in src or "import secrets" in src:
            _fatal(f"{fname} imports a randomness module")
    for name in o14.WORLD_NAMES:
        o14.world_certificates(name)          # fail-closed vs locked plan
        dts = o14.world_dts(name)
        cert = o14.world_certificates(name)["binding_certificate"]
        for label, r_exp in (("conservative", 0.5),
                             ("near_certificate", 0.9)):
            r = dts[label] / cert
            if abs(r - r_exp) > 1e-12 or r > 1.0:
                _fatal(f"{name}/{label}: r_dt {r!r} != registered {r_exp}")
    if os.path.exists(SUMMARY):
        _fatal(f"{SUMMARY} exists; the registered study runs exactly once "
               "and refuses to overwrite results")
    for orphan in (TRACE, MANIFEST):
        if os.path.exists(orphan):
            _fatal(f"{orphan} exists without a summary: a partial or "
                   "ambiguous prior attempt requires separate human "
                   "authorization; nothing is deleted or overwritten")
    if os.path.isdir(OUTDIR):
        extra = [f for f in os.listdir(OUTDIR) if f != STDOUT_NAME]
        if extra:
            _fatal(f"unexpected prior artifact(s) in {OUTDIR}: {extra}")
    return specs


# ---------------------------------------------------------------------------
# execution loop (implemented here; NOT run in the preparation gate)
# ---------------------------------------------------------------------------
def _validate_tick_record(rec: dict, run_id: str, t: int) -> None:
    missing = [f for f in REQUIRED_TICK_FIELDS if f not in rec]
    if missing:
        _fatal(f"{run_id} tick {t}: missing tick fields {missing}")
    if rec["tick"] != t:
        _fatal(f"{run_id}: tick sequence broken at {t} (got {rec['tick']})")
    _assert_finite({k: v for k, v in rec.items()}, f"{run_id}[{t}]")


def validate_run(run, spec, ticks: int) -> None:
    """Immediate fail-closed validation of one returned run."""
    locked = o14.PLAN["timestep"]["per_world"][spec["world"]]
    if run.run_id != spec["run_id"]:
        _fatal(f"run_id {run.run_id!r} != spec {spec['run_id']!r}")
    if (run.world, run.arm, run.dt_label) != (spec["world"], spec["arm"],
                                              spec["dt_label"]):
        _fatal(f"{spec['run_id']}: identity fields differ from the spec")
    if run.arm not in o14.EXEC_ARMS or run.world not in o14.WORLD_NAMES:
        _fatal(f"{spec['run_id']}: unregistered arm or world")
    dt_field = ("registered_conservative_dt"
                if spec["dt_label"] == "conservative"
                else "registered_near_certificate_dt")
    if run.dt != locked[dt_field]:
        _fatal(f"{spec['run_id']}: dt {run.dt!r} != locked")
    if run.dt_certificate != locked["binding_certificate"] \
            or run.certificate_kind != locked["binding_kind"]:
        _fatal(f"{spec['run_id']}: certificate differs from locked values")
    if run.r_dt > 1.0:
        _fatal(f"{spec['run_id']}: r_dt > 1")
    recs = run.series.get("tick_records", [])
    if len(recs) != ticks:
        _fatal(f"{spec['run_id']}: {len(recs)} tick records != {ticks}")
    for t, rec in enumerate(recs, 1):
        _validate_tick_record(rec, spec["run_id"], t)
    if run.arm == ARM_A and run.totals["ebu"] != 0.0:
        _fatal(f"{spec['run_id']}: arm A settled EBU (must be exactly 0)")
    _assert_finite(run.totals, f"{spec['run_id']}.totals")


def execute_registered_study(specs, run_fn=None) -> list:
    """Execute EXACTLY the frozen specification list, once each, at the
    registered horizon. No shuffling, filtering, retrying or subsetting; a
    domain failure stays in the results as a first-class outcome."""
    if run_fn is None:
        run_fn = o14.run_arm                      # production path
    runs = []
    for spec in specs:
        run = run_fn(spec["world"], spec["arm"], spec["dt_label"],
                     ticks=o14.RUN_TICKS)
        validate_run(run, spec, o14.RUN_TICKS)
        runs.append(run)
        print(f"  {run.run_id:70s} class-pending  "
              f"svc {run.totals['service']:9.3f}  "
              f"unmet {run.totals['unmet']:9.3f}  "
              f"EBU {run.totals['ebu']:+10.3f}  Rx "
              f"{run.totals['reserve_crossings']:2d}  "
              f"r_dt {run.r_dt:4.2f}")
    if len(runs) != len(specs):
        _fatal("a registered run was dropped")
    return runs


# ---------------------------------------------------------------------------
# analysis / summary (evaluation layer; Gate 1D predicates verbatim)
# ---------------------------------------------------------------------------
def _by_id(runs):
    d = {r.run_id: r for r in runs}
    if len(d) != len(runs):
        _fatal("duplicate run identifiers in results")
    return d


def _get(runs_by_id, world, arm, label):
    return runs_by_id[f"{world}|{arm}|{label}"]


def _edge_switches(run) -> int:
    seq = [e for e in run.series["selected_edge"] if e is not None]
    return sum(1 for a, b in zip(seq, seq[1:]) if a != b)


def _min_sigma(run):
    vals = [s for rec in run.series["tick_records"]
            for s in rec["sigma"].values()]
    return min(vals) if vals else None


def _dest_totals(run, key):
    n = len(run.final["x"])
    return [math.fsum(v[i] for v in run.series[f"{key}_by_dest"])
            for i in range(n)]


def run_record(run, baseline, align) -> dict:
    t, f, s = run.totals, run.final, run.series
    reserve = sv.reserve_harm_predicate(run)
    per_unit_vs_total_divergences = 0
    for rec in s["tick_records"]:
        for sid, exact in rec["candidate_exact_quotes"].items():
            cands = rec["menus"][sid]["candidates"]
            if len(cands) >= 2:
                tot_i = max(range(len(cands)),
                            key=lambda i: (exact[i], -cands[i]["edge"],
                                           -cands[i]["quant_index"]))
                pu = [q / c["q_acc"] for q, c in zip(exact, cands)]
                pu_i = max(range(len(cands)),
                           key=lambda i: (pu[i], -cands[i]["edge"],
                                          -cands[i]["quant_index"]))
                per_unit_vs_total_divergences += (tot_i != pu_i)
    return dict(
        run_id=run.run_id, world=run.world, arm=run.arm,
        dt_label=run.dt_label, dt=run.dt, dt_certificate=run.dt_certificate,
        certificate_kind=run.certificate_kind, r_dt=run.r_dt,
        ebu_total=t["ebu"], ebu_positive=t["ebu_pos"],
        ebu_negative=t["ebu_neg"],
        delivered_service=t["service"], unmet_demand=t["unmet"],
        total_demand=t["demand"],
        service_ratio=(t["service"] / t["demand"] if t["demand"] > 0
                       else 0.0),
        pbi_delivered_service=sv.pbi_sum(s["service"]),
        pbi_unmet_demand=sv.pbi_sum(s["unmet"]),
        pbi_service_mean=sv.pbi_mean(s["service"]),
        pbi_unmet_mean=sv.pbi_mean(s["unmet"]),
        service_by_destination=_dest_totals(run, "service"),
        unmet_by_destination=_dest_totals(run, "unmet"),
        final_burden=f["burden"], final_viability=f["viability"],
        pbi_burden_mean=sv.pbi_mean(s["burden"]),
        pbi_viability_mean=sv.pbi_mean(s["viability"]),
        reserve_crossings=t["reserve_crossings"],
        allee_crossings=t["allee_crossings"],
        dead_sources=f["dead_sources"], physical_overuse=t["overuse"],
        transport_loss=t["loss"],
        action_opportunities=t["opportunities"],
        proposed_actions=t["proposed"], accepted_actions=t["accepted"],
        voluntary_rests=t["rests"], p1c_rejections=t["p1c_rejected"],
        quoted_actions=t["quoted"],
        quote_coverage=(t["quoted"] / t["accepted"] if t["accepted"]
                        else 0.0),
        quote_candidates_positive=t["quote_pos"],
        quote_candidates_zero=t["quote_zero"],
        quote_candidates_negative=t["quote_neg"],
        per_unit_vs_total_rank_divergences=per_unit_vs_total_divergences,
        selected_edge_switches=_edge_switches(run),
        min_sigma=_min_sigma(run),
        min_source_stock=min((v for v in s["min_source"]
                              if not math.isnan(v)), default=None),
        final_state=[float(v) for v in f["x"]],
        source_stock=f["source_stock"],
        destination_stock=f["destination_stock"],
        negative_state=bool(f["negative_state"]),
        domain_failure_tick=f["domain_failure_tick"],
        terminal_status=("domain_failure"
                         if f["domain_failure_tick"] is not None
                         else "completed"),
        negative_corrections_total=t["corrections"],
        max_ledger_residual=t["max_ledger_residual"],
        feasible_world=bool(f["feasible_world"]), world_note=f["note"],
        reserve_harm_predicate=reserve,
        service_alignment_predicate=align,
        outcome_class=sv.classify_outcome(run, baseline, align),
    )


def compare_bc(run_b, run_c) -> dict:
    """Complete-trajectory physical identity (EBU fields excluded)."""
    rb, rc = run_b.series["tick_records"], run_c.series["tick_records"]
    if len(rb) != len(rc):
        return dict(identical=False, first_difference="tick_count",
                    max_state_diff=None)
    first = None
    for t, (a, b) in enumerate(zip(rb, rc), 1):
        for k in PHYS_TICK_FIELDS:
            if a[k] != b[k] and not (isinstance(a[k], float)
                                     and isinstance(b[k], float)
                                     and math.isnan(a[k])
                                     and math.isnan(b[k])):
                first = f"tick {t} field {k}"
                break
        if first:
            break
    md = max((max(abs(p - q) for p, q in zip(a["x_after"], b["x_after"]))
              for a, b in zip(rb, rc)), default=0.0)
    return dict(identical=first is None, first_difference=first,
                max_state_diff=md)


def build_summary(runs, plan) -> dict:
    by_id = _by_id(runs)
    records, comparisons = {}, {}
    # per-run records (baseline = matched arm B of the same world/dt)
    for run in runs:
        base = (_get(by_id, run.world, ARM_B, run.dt_label)
                if run.arm != ARM_B else None)
        align = (sv.service_alignment_predicate(
                     run, _get(by_id, run.world, ARM_B, run.dt_label))
                 if run.arm == ARM_D else None)
        records[run.run_id] = run_record(run, base, align)
    # comparisons
    a_vs_b, b_vs_c, b_vs_d, s_vs, tsens = {}, {}, {}, {}, {}
    for w in o14.WORLD_NAMES:
        for label in o14.DT_LABELS:
            A = records[f"{w}|{ARM_A}|{label}"]
            B = records[f"{w}|{ARM_B}|{label}"]
            D = records[f"{w}|{ARM_D}|{label}"]
            S = records[f"{w}|{ARM_S}|{label}"]
            cap = A["pbi_delivered_service"] - B["pbi_delivered_service"]
            a_vs_b[f"{w}|{label}"] = dict(
                pbi_service_A=A["pbi_delivered_service"],
                pbi_service_B=B["pbi_delivered_service"],
                capability_cost_absolute=cap,
                capability_cost_relative=(
                    cap / A["pbi_delivered_service"]
                    if A["pbi_delivered_service"] > 0 else 0.0),
                actions_A=A["accepted_actions"],
                actions_B=B["accepted_actions"],
                min_sigma_A=A["min_sigma"],
                restriction_binding=bool(
                    (A["min_sigma"] is not None and A["min_sigma"] < 1.0)
                    or cap > _NUM_TOL))
            b_vs_c[f"{w}|{label}"] = compare_bc(
                _get(by_id, w, ARM_B, label), _get(by_id, w, ARM_C, label))
            al = D["service_alignment_predicate"]
            b_vs_d[f"{w}|{label}"] = dict(
                pbi_service_B=B["pbi_delivered_service"],
                pbi_service_D=D["pbi_delivered_service"],
                service_ratio_D_over_B=(
                    D["pbi_delivered_service"] / B["pbi_delivered_service"]
                    if B["pbi_delivered_service"] > 0 else None),
                predicate=al,
                is_service_alignment_failure=al[
                    "is_service_alignment_failure"])
            s_vs[f"{w}|{label}"] = dict(
                pbi_service_S=S["pbi_delivered_service"],
                pbi_service_B=B["pbi_delivered_service"],
                pbi_service_D=D["pbi_delivered_service"],
                pbi_unmet_S=S["pbi_unmet_demand"],
                pbi_unmet_B=B["pbi_unmet_demand"],
                pbi_unmet_D=D["pbi_unmet_demand"],
                note="registered secondary attribution; informational only")
    for w in o14.WORLD_NAMES:
        fc = b_vs_d[f"{w}|conservative"]["is_service_alignment_failure"]
        fn = b_vs_d[f"{w}|near_certificate"]["is_service_alignment_failure"]
        tsens[w] = dict(failure_conservative=fc, failure_near=fn,
                        consistent=bool(fc == fn))
    comparisons = dict(A_vs_B_capability_cost=a_vs_b,
                       B_vs_C_observational_identity=b_vs_c,
                       B_vs_D_primary_alignment=b_vs_d,
                       S_vs_B_and_D_secondary=s_vs,
                       timestep_sensitivity=tsens,
                       primary_baseline_arm=PRIMARY_BASELINE_ARM,
                       forbidden_baseline_arm=ARM_A)
    # O3 settlement-free diagnostic (arm-A ticks)
    g_all = [rec["group_diagnostic"]
             for r in runs if r.arm == ARM_A
             for rec in r.series["tick_records"]
             if rec["group_diagnostic"] and
             rec["group_diagnostic"]["n_actions"] > 0]
    multi = [g for g in g_all if g["n_actions"] >= 2]
    o3 = dict(
        arm_A_ticks_with_actions=len(g_all),
        arm_A_ticks_with_multi_actions=len(multi),
        total_group_quote=math.fsum(g["group_quote"] for g in g_all),
        total_naive_independent_sum=math.fsum(
            g["naive_independent_sum"] for g in g_all),
        total_double_count=math.fsum(g["double_count"] for g in g_all),
        min_double_count=(min(g["double_count"] for g in g_all)
                          if g_all else None),
        sign_check_naive_ge_group=bool(
            all(g["double_count"] >= -_NUM_TOL for g in g_all)),
        nothing_settled_or_allocated=bool(
            all(r.totals["ebu"] == 0.0 for r in runs if r.arm == ARM_A)),
        note="recorded functionals of frozen tick data; O3 remains open")
    # hypotheses H1-H10 (evaluation rules frozen before execution)
    ident_all = all(v["identical"] for v in b_vs_c.values())
    binding = [k for k, v in a_vs_b.items() if v["restriction_binding"]]
    cap_nonzero = [k for k, v in a_vs_b.items()
                   if v["capability_cost_absolute"] > _NUM_TOL]
    d_runs = [records[r.run_id] for r in runs if r.arm == ARM_D]
    h4_ok = all(r["reserve_crossings"] == 0
                and r["physical_overuse"] <= sv.tol(0.0)
                for r in d_runs)
    w5_switches = {r["run_id"]: r["selected_edge_switches"]
                   for r in d_runs if r["world"] == "O14_W5_reversal"}
    h6_count = sum(r["per_unit_vs_total_rank_divergences"]
                   for rid, r in records.items())
    feas_fail = [r["run_id"] for r in d_runs
                 if r["feasible_world"] and r["service_alignment_predicate"]
                 ["is_service_alignment_failure"]]
    w6_unmet = {rid: r["pbi_unmet_demand"] for rid, r in records.items()
                if r["world"] == "O14_W6_infeasible"}
    rests_recorded = all("voluntary_rests" in r for r in records.values())
    h10_pos = [g["double_count"] for g in multi
               if g["double_count"] > _NUM_TOL]

    def _status(ok, testable=True):
        if not testable:
            return "not_testable"
        return "supported" if ok else "not_supported"

    hypotheses = dict(
        H1=dict(status=_status(ident_all),
                evidence=dict(identical_pairs=sum(
                    v["identical"] for v in b_vs_c.values()), of=12)),
        H2=dict(status=_status(bool(binding)),
                evidence=dict(binding_world_dts=binding)),
        H3=dict(status=_status(bool(cap_nonzero)),
                evidence=dict(nonzero_capability_cost=cap_nonzero)),
        H4=dict(status=_status(h4_ok),
                evidence=dict(d_reserve_crossings=sum(
                    r["reserve_crossings"] for r in d_runs),
                    d_overuse=math.fsum(r["physical_overuse"]
                                        for r in d_runs))),
        H5=dict(status=_status(all(v >= 1 for v in w5_switches.values())),
                evidence=dict(w5_selected_edge_switches=w5_switches)),
        H6=dict(status=_status(h6_count > 0),
                evidence=dict(per_unit_vs_total_divergent_ticks=h6_count)),
        H7=dict(status=_status(not feas_fail),
                evidence=dict(feasible_world_alignment_failures=feas_fail)),
        H8=dict(status=_status(all(v > _NUM_TOL for v in w6_unmet.values())),
                evidence=dict(w6_pbi_unmet=w6_unmet)),
        H9=dict(status=_status(rests_recorded),
                evidence=dict(total_voluntary_rests=sum(
                    r["voluntary_rests"] for r in records.values()),
                    quote_sign_counts_recorded=True)),
        H10=dict(status=_status(bool(h10_pos),
                                testable=bool(multi)),
                 evidence=dict(multi_action_ticks=len(multi),
                               strictly_positive_double_counts=len(h10_pos))),
    )
    # falsifiers F1-F15 (fired/evidence; reported, never suppressed)
    f1_bad = [k for k, v in b_vs_c.items() if not v["identical"]]
    f3_multi = {w: max((len(set(c["edge"]
                                for m in rec["menus"].values()
                                for c in m["candidates"]))
                        for r in runs if r.world == w and r.arm == ARM_B
                        for rec in r.series["tick_records"]), default=0)
                for w in o14.WORLD_NAMES}
    f5_fired = [k for k, v in b_vs_d.items()
                if v["is_service_alignment_failure"]]
    f6_bad = [r["run_id"] for r in d_runs
              if r["reserve_crossings"] > 0
              or r["physical_overuse"] > sv.tol(0.0)]
    f8_bad, f10_bad = [], []
    for r in runs:
        for rec in r.series["tick_records"]:
            for sid, exact in rec["candidate_exact_quotes"].items():
                cands = rec["menus"][sid]["candidates"]
                if r.arm == ARM_D and rec["selected"] is not None and exact:
                    best = max(range(len(cands)),
                               key=lambda i: (exact[i], -cands[i]["edge"],
                                              -cands[i]["quant_index"]))
                    if exact[best] > 0.0 and rec["selected"] != cands[best]:
                        f8_bad.append((r.run_id, rec["tick"]))
            for m in rec["menus"].values():
                for c in m["candidates"]:
                    if c["q_acc"] > c["q_e_max"] * (1 + 1e-12):
                        f10_bad.append((r.run_id, rec["tick"]))
    f9_bad = [g for g in g_all if g["double_count"] < -_NUM_TOL]
    f11_bad = [r.run_id for r in runs if r.r_dt > 1.0]
    disc = [w for w in o14.WORLD_NAMES
            if any(a_vs_b[f"{w}|{l}"]["capability_cost_absolute"] > _NUM_TOL
                   or (b_vs_d[f"{w}|{l}"]["service_ratio_D_over_B"]
                       is not None
                       and abs(b_vs_d[f"{w}|{l}"]["service_ratio_D_over_B"]
                               - 1.0) > _NUM_TOL)
                   for l in o14.DT_LABELS)]
    falsifiers = dict(
        F1=dict(fired=bool(f1_bad), evidence=dict(non_identical=f1_bad)),
        F2=dict(fired=False, evidence=dict(
            note="menus/budgets/timesteps identity is asserted per tick "
                 "inside o14_tick (request-shaping assertion) and by the "
                 "shared constructor; any violation raises an integrity "
                 "failure before this summary exists")),
        F3=dict(fired=not any(v >= 2 for v in f3_multi.values()),
                evidence=dict(max_simultaneous_active_edges=f3_multi)),
        F4=dict(fired=not binding,
                evidence=dict(binding_world_dts=binding)),
        F5=dict(fired=bool(f5_fired), evidence=dict(failures=f5_fired)),
        F6=dict(fired=bool(f6_bad), evidence=dict(runs=f6_bad)),
        F7=dict(fired=False, evidence=dict(
            note="information boundary enforced by AST + runtime poison in "
                 "test_v30_o14.py before execution")),
        F8=dict(fired=bool(f8_bad), evidence=dict(divergences=f8_bad[:50])),
        F9=dict(fired=bool(f9_bad),
                evidence=dict(negative_double_counts=len(f9_bad))),
        F10=dict(fired=bool(f10_bad), evidence=dict(hits=f10_bad[:50])),
        F11=dict(fired=bool(f11_bad), evidence=dict(runs=f11_bad)),
        F12=dict(fired=False, evidence=dict(
            note="capability identity is structural (shared menu "
                 "constructor); see F2")),
        F13=dict(fired=not disc,
                 evidence=dict(discriminating_worlds=disc)),
        F14=dict(fired=False, evidence=dict(
            note="plan hash locked and recomputed at start; predicates and "
                 "thresholds are service_v30 verbatim")),
        F15=dict(fired=False, evidence=dict(
            note="static graphs reconstructed from the locked plan; no "
                 "migration or topology change exists")),
    )
    own_hashes = {f: hashlib.sha256(open(f, "rb").read()).hexdigest()
                  for f in ("o14_v30.py", "exp_v30_o14.py")}
    summary = dict(
        gate=("V3.0 Gate 1D-B / O14 - multi-out-edge capability study "
              "(single authorized execution)"),
        plan_id=plan["plan_id"], plan_version=plan["plan_version"],
        plan_canonical_hash=PLAN_CANONICAL, plan_raw_sha256=PLAN_RAW,
        equation_version=eq.EQUATION_VERSION,
        python=platform.python_version(),
        implementation_sha256=own_hashes,
        registered=dict(total_runs=60, run_length_ticks=o14.RUN_TICKS,
                        burn_in_ticks=o14.BURN_IN_TICKS,
                        persistence_window_ticks=sv.PERSISTENCE_WINDOW,
                        deterministic=True, seed=None,
                        worlds=list(o14.WORLD_NAMES),
                        arms=list(o14.EXEC_ARMS),
                        dt_labels=list(o14.DT_LABELS)),
        n_runs=len(runs), runs=records,
        comparisons=comparisons,
        hypotheses=hypotheses, falsifiers=falsifiers,
        o3_aggregate_diagnostic=o3,
        outcome_class_counts={},
        non_claims=[
            "numerical results do not prove alignment, safety, security or "
            "any theorem",
            "O3 (aggregate multi-edge settlement) remains open",
            "O12/O13 remain theorem-less (bounded wrapper outside the V2.8 "
            "theorem)",
            "Gate 1E (latency/uncertainty) remains untouched",
            "Gate 2 (actor economy) remains paused",
            "migration/diffusion/convection remain future research only",
            "cumulative signed EBU is an evaluation variable, not a wallet",
        ])
    counts = {}
    for rec in records.values():
        counts[rec["outcome_class"]] = counts.get(rec["outcome_class"],
                                                  0) + 1
    summary["outcome_class_counts"] = counts
    return summary


# ---------------------------------------------------------------------------
# trace + output writing (trace first; summary LAST = completion sentinel)
# ---------------------------------------------------------------------------
def trace_rows(runs):
    """One deterministic JSONL row per retained tick (60 x 200 = 12000)."""
    for run in runs:
        for rec in run.series["tick_records"]:
            yield dict(plan_canonical_hash=PLAN_CANONICAL,
                       run_id=run.run_id, world=run.world, arm=run.arm,
                       dt_label=run.dt_label, dt=run.dt,
                       dt_certificate=run.dt_certificate,
                       certificate_kind=run.certificate_kind,
                       r_dt=run.r_dt, tick=rec["tick"], record=rec)


def validate_complete_outputs_in_memory(runs, summary, rows,
                                        expected_runs: int = 60,
                                        expected_ticks: int = None) -> None:
    """Everything is validated BEFORE anything is written."""
    if expected_ticks is None:
        expected_ticks = o14.RUN_TICKS
    ids = [r.run_id for r in runs]
    if len(ids) != expected_runs or len(set(ids)) != expected_runs:
        _fatal(f"expected {expected_runs} unique runs, got {len(set(ids))}")
    expected_ids = {f"{w}|{a}|{l}" for w in o14.WORLD_NAMES
                    for a in o14.EXEC_ARMS for l in o14.DT_LABELS}
    if expected_runs == 60 and set(ids) != expected_ids:
        _fatal("run-identifier set differs from the registered inventory")
    if len(rows) != expected_runs * expected_ticks:
        _fatal(f"trace has {len(rows)} rows, expected "
               f"{expected_runs * expected_ticks}")
    if set(summary["runs"]) != set(ids):
        _fatal("summary run set differs from executed runs")
    for h in (f"H{i}" for i in range(1, 11)):
        if h not in summary["hypotheses"]:
            _fatal(f"summary missing hypothesis {h}")
    for fk in (f"F{i}" for i in range(1, 16)):
        if fk not in summary["falsifiers"]:
            _fatal(f"summary missing falsifier {fk}")
    for blk in ("A_vs_B_capability_cost", "B_vs_C_observational_identity",
                "B_vs_D_primary_alignment", "S_vs_B_and_D_secondary",
                "timestep_sensitivity"):
        if blk not in summary["comparisons"]:
            _fatal(f"summary missing comparison block {blk}")
    # aggregate recomputation from the trace rows (spot identities)
    per_run = {}
    for row in rows:
        d = per_run.setdefault(row["run_id"],
                               dict(service=0.0, ebu=0.0, ticks=0))
        d["service"] += math.fsum(row["record"]["service"])
        d["ebu"] += row["record"]["ebu"]
        d["ticks"] += 1
    for r in runs:
        d = per_run[r.run_id]
        if d["ticks"] != expected_ticks:
            _fatal(f"{r.run_id}: trace tick count {d['ticks']}")
        if abs(d["service"] - r.totals["service"]) > 1e-9 \
                or abs(d["ebu"] - r.totals["ebu"]) > 1e-9:
            _fatal(f"{r.run_id}: aggregates not reconstructible from trace")
    strict_dumps(summary)                        # must serialize strictly
    for row in rows:
        strict_dumps(row)


def _atomic_write(path: str, write_fn) -> None:
    """Temporary file inside the output directory + atomic replace."""
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_",
                               suffix=os.path.basename(path))
    try:
        with os.fdopen(fd, "wb") as f:
            write_fn(f)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def write_trace(rows, path) -> None:
    def _w(f):
        gz = gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0)
        for row in rows:
            gz.write((json.dumps(row, sort_keys=True,
                                 separators=(",", ":"), ensure_ascii=True,
                                 allow_nan=False) + "\n").encode())
        gz.close()
    _atomic_write(path, _w)


def write_summary(summary, path) -> None:
    def _w(f):
        f.write((strict_dumps(summary, indent=2) + "\n").encode())
    _atomic_write(path, _w)


def write_outputs(runs, summary, rows, expected_runs: int = 60,
                  expected_ticks: int = None) -> None:
    """Validates EVERYTHING in memory first, then writes the trace, then
    the summary LAST (the summary is the completion sentinel). If anything
    fails, no completed summary is fabricated."""
    validate_complete_outputs_in_memory(runs, summary, rows,
                                        expected_runs=expected_runs,
                                        expected_ticks=expected_ticks)
    os.makedirs(OUTDIR, exist_ok=True)
    write_trace(rows, TRACE)
    write_summary(summary, SUMMARY)


def main(run_fn=None) -> int:
    specs = preflight()
    print("EBP V3.0 Gate 1D-B / O14 - multi-out-edge capability study")
    print(f"  plan canonical hash: {PLAN_CANONICAL}")
    print(f"  python: {platform.python_version()}")
    print(f"  registered: 6 worlds x 5 arms x 2 timesteps = 60 runs, "
          f"{o14.RUN_TICKS} ticks, burn-in {o14.BURN_IN_TICKS}, no seed\n")
    print("=== (1) the 60 registered runs ===")
    runs = execute_registered_study(specs, run_fn=run_fn)
    plan = o14.load_plan()
    summary = build_summary(runs, plan)
    rows = list(trace_rows(runs))
    write_outputs(runs, summary, rows)      # validates everything first
    print("\n=== (2) outcome classes ===")
    for k, v in sorted(summary["outcome_class_counts"].items()):
        print(f"  {k:40s} {v:3d}")
    print("\n=== (3) falsifiers fired ===")
    for k in (f"F{i}" for i in range(1, 16)):
        if summary["falsifiers"][k]["fired"]:
            print(f"  {k}: FIRED {summary['falsifiers'][k]['evidence']}")
    print(f"\nwrote {TRACE} and {SUMMARY}")
    print(f"Every registered run appears exactly once ({len(runs)} of 60); "
          "no run was dropped; nothing was settled for arm A (O3 open).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
