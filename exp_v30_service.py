"""
V3.0 Gate 1D official runner for the locked bounded capability-matched
service-alignment study.

Executes the registered study EXACTLY ONCE: 7 worlds x 4 arms x 2 certified
timesteps = 56 deterministic runs, 200 ticks each, 50-tick burn-in, no random
seed.

DISCIPLINE
  * recomputes and enforces the canonical plan hash; refuses to run on mismatch;
  * takes NO command-line option and no scientific parameter override;
  * REFUSES to overwrite a completed study (fail closed);
  * writes every registered run exactly once; drops nothing;
  * records domain failures and terminal status as first-class outputs;
  * strict JSON (allow_nan=False) for every emitted record;
  * fails before execution if any paired run would exceed its certificate.

Reported comparisons: A vs B (action-capacity cost), B vs C (observational
identity), B vs D (service alignment - the PRIMARY comparison).

No outcome authorizes automatic progression to the actor economy.

Run: python3 exp_v30_service.py
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import os
import platform
import sys

import d0_v29 as d0
import ebu_quote_v30 as eq
import service_v30 as sv

PLAN_PATH = "v30_service_alignment_plan.json"
PLAN_CANONICAL = "71c706021d738330d5382fec5056ea5228abac61aba0738b00a9a8e75edc1020"
PLAN_RAW = "7a5676e2013d3baa4f18d48443fe448f1d6d0973be79b5c1ca8634a95bfa4f7c"
OUTDIR = "results/v3.0/gate1d"
SUMMARY = os.path.join(OUTDIR, "v30_service_alignment_summary.json")
TRACE = os.path.join(OUTDIR, "v30_service_alignment_trace.jsonl.gz")

DTS = (("conservative", sv.DT_CONSERVATIVE), ("near_certificate", sv.DT_NEAR))


def _plan():
    raw = open(PLAN_PATH, "rb").read()
    if hashlib.sha256(raw).hexdigest() != PLAN_RAW:
        raise SystemExit("FATAL: raw plan SHA-256 mismatch")
    plan = json.loads(raw)
    canon = hashlib.sha256(json.dumps(plan, sort_keys=True,
                                      separators=(",", ":"),
                                      ensure_ascii=True).encode()).hexdigest()
    if canon != PLAN_CANONICAL:
        raise SystemExit(f"FATAL: canonical plan hash mismatch: {canon}")
    return plan


def _record(run: sv.RunResult, baseline, align, reserve) -> dict:
    t, f, s = run.totals, run.final, run.series
    pbi = sv.post_burn_in
    return dict(
        run_id=run.run_id, world=run.world, arm=run.arm,
        dt_label=run.dt_label, dt=run.dt, dt_certificate=run.dt_certificate,
        certificate_kind=run.certificate_kind, r_dt=run.r_dt,
        # EBU (evaluation variables, not a wallet)
        ebu_total=t["ebu"], ebu_positive=t["ebu_pos"], ebu_negative=t["ebu_neg"],
        # action accounting
        action_opportunities=t["opportunities"], proposed_actions=t["proposed"],
        accepted_actions=t["accepted"], quoted_actions=t["quoted"],
        quote_coverage=(t["quoted"] / t["accepted"] if t["accepted"] else 0.0),
        voluntary_rests=t["rests"], p1c_rejections=t["p1c_rejected"],
        # physical service
        delivered_service=t["service"], unmet_demand=t["unmet"],
        total_demand=t["demand"],
        service_ratio=(t["service"] / t["demand"] if t["demand"] > 0 else 0.0),
        pbi_delivered_service=sv.pbi_sum(s["service"]),
        pbi_unmet_demand=sv.pbi_sum(s["unmet"]),
        pbi_service_mean=sv.pbi_mean(s["service"]),
        pbi_unmet_mean=sv.pbi_mean(s["unmet"]),
        # physical state
        source_stock=f["source_stock"], destination_stock=f["destination_stock"],
        transport_loss=t["loss"], physical_overuse=t["overuse"],
        reserve_crossings=t["reserve_crossings"],
        allee_crossings=t["allee_crossings"], dead_sources=f["dead_sources"],
        final_burden=f["burden"], final_viability=f["viability"],
        pbi_burden_mean=sv.pbi_mean(s["burden"]),
        pbi_viability_mean=sv.pbi_mean(s["viability"]),
        min_source_stock=min((v for v in s["min_source"]
                              if not math.isnan(v)), default=None),
        final_state=[float(v) for v in f["x"]],
        # integrity / terminal status
        negative_state=bool(f["negative_state"]),
        domain_failure_tick=f["domain_failure_tick"],
        negative_corrections_total=t["corrections"],
        max_ledger_residual=t["max_ledger_residual"],
        terminal_status=("domain_failure"
                        if f["domain_failure_tick"] is not None else "completed"),
        feasible_world=bool(f["feasible_world"]), world_note=f["note"],
        # predicates and classification
        reserve_harm_predicate=reserve,
        service_alignment_predicate=align,
        outcome_class=sv.classify_outcome(run, baseline, align),
    )


def main() -> int:
    if len(sys.argv) > 1:
        raise SystemExit("FATAL: this harness takes no command-line option and "
                         "no scientific parameter override")
    plan = _plan()
    if os.path.exists(SUMMARY):
        raise SystemExit(f"FATAL: {SUMMARY} exists; the registered study runs "
                         "exactly once and refuses to overwrite results")
    os.makedirs(OUTDIR, exist_ok=True)

    print("EBP V3.0 Gate 1D - bounded capability-matched service-alignment study")
    print(f"  plan canonical hash: {PLAN_CANONICAL}")
    print(f"  python: {platform.python_version()}")
    print(f"  registered: 7 worlds x 4 arms x 2 timesteps = "
          f"{plan['experiment_size']['total_runs']} runs, "
          f"{sv.RUN_TICKS} ticks, burn-in {sv.BURN_IN_TICKS}, no seed")
    print(f"  dt conservative = {sv.DT_CONSERVATIVE!r}, "
          f"near-certificate = {sv.DT_NEAR!r}")
    print("  tau = 0, eps_x = eps_u = 0; NO real-world latency or robustness "
          "claim.\n")

    # pre-execution certificate gate for every paired run
    for wname in sv.WORLDS:
        w, *_ = sv.build_world(wname)
        cert, kind = sv.world_certificate(w)
        for label, dt in DTS:
            r = dt / cert
            if r > 1.0:
                raise SystemExit(f"FATAL: {wname}/{label} r_dt = {r} > 1")
    print("  certificate gate: every paired run has r_dt <= 1  [ok]\n")

    runs, records, trace = {}, [], []
    print("=== (1) 56 registered runs ===")
    hdr = (f"  {'run':52s} {'EBU':>9s} {'svc':>8s} {'unmet':>8s} {'burden':>8s} "
           f"{'viab%':>6s} {'acts':>5s} {'rest':>5s} {'Rx':>3s} {'dead':>4s} "
           f"{'r_dt':>5s} {'class':>34s}")
    print(hdr)
    for wname in sv.WORLDS:
        for label, dt in DTS:
            for arm in sv.ARMS:
                runs[(wname, arm, label)] = sv.run_arm(wname, arm, dt, label)
            base = runs[(wname, "B_restricted_p1c", label)]
            for arm in sv.ARMS:
                run = runs[(wname, arm, label)]
                align = (sv.service_alignment_predicate(run, base)
                         if arm == "D_restricted_quote_greedy" else None)
                reserve = sv.reserve_harm_predicate(run)
                rec = _record(run, base, align, reserve)
                records.append(rec)
                trace.append(dict(run_id=run.run_id, kind="series",
                                  service=run.series["service"],
                                  unmet=run.series["unmet"],
                                  burden=run.series["burden"],
                                  viability=run.series["viability"],
                                  ebu=run.series["ebu"],
                                  actions=run.series["actions"],
                                  rests=run.series["rests"],
                                  min_source=[None if math.isnan(v) else v
                                              for v in run.series["min_source"]]))
                print(f"  {rec['run_id']:52s} {rec['ebu_total']:+9.3f} "
                      f"{rec['delivered_service']:8.2f} "
                      f"{rec['unmet_demand']:8.2f} {rec['final_burden']:8.2f} "
                      f"{rec['final_viability']:6.1f} "
                      f"{rec['accepted_actions']:5d} "
                      f"{rec['voluntary_rests']:5d} "
                      f"{rec['reserve_crossings']:3d} {rec['dead_sources']:4d} "
                      f"{rec['r_dt']:5.3f} {rec['outcome_class']:>34s}")

    def get(w, a, l):
        return next(r for r in records if r["world"] == w and r["arm"] == a
                    and r["dt_label"] == l)

    print("\n=== (2) A vs B - how much service loss came from restricting "
          "action capacity? ===")
    cap = []
    for wname in sv.WORLDS:
        for label, _dt in DTS:
            A, B = get(wname, "A_full_p1c", label), get(wname, "B_restricted_p1c", label)
            d = A["pbi_delivered_service"] - B["pbi_delivered_service"]
            rel = (d / A["pbi_delivered_service"]
                   if A["pbi_delivered_service"] > 0 else 0.0)
            cap.append(rel)
            print(f"  {wname:26s} {label:16s} A {A['pbi_delivered_service']:8.3f} "
                  f"B {B['pbi_delivered_service']:8.3f}  capacity cost "
                  f"{d:+8.3f} ({100*rel:+6.2f}%)  acts A {A['accepted_actions']:4d} "
                  f"B {B['accepted_actions']:4d}")

    print("\n=== (3) B vs C - did observational quoting stay physically "
          "identical? ===")
    ident = []
    for wname in sv.WORLDS:
        for label, _dt in DTS:
            B, C = get(wname, "B_restricted_p1c", label), \
                get(wname, "C_restricted_p1c_quote", label)
            same = (B["final_state"] == C["final_state"]
                    and B["delivered_service"] == C["delivered_service"]
                    and B["unmet_demand"] == C["unmet_demand"]
                    and B["final_burden"] == C["final_burden"])
            ident.append(same)
            md = max(abs(p - q) for p, q in zip(B["final_state"],
                                                C["final_state"]))
            print(f"  {wname:26s} {label:16s} identical={same}  "
                  f"max|dx|={md:.3e}  C EBU {C['ebu_total']:+9.3f}")
    print(f"  all identical: {all(ident)}")

    print("\n=== (4) B vs D - PRIMARY: after equalizing capability, does "
          "exact-quote maximization still reduce service? ===")
    prim = []
    for wname in sv.WORLDS:
        for label, _dt in DTS:
            B, D = get(wname, "B_restricted_p1c", label), \
                get(wname, "D_restricted_quote_greedy", label)
            a = D["service_alignment_predicate"]
            prim.append((wname, label, a))
            print(f"  {wname:26s} {label:16s} "
                  f"svc B {B['pbi_delivered_service']:8.3f} "
                  f"D {D['pbi_delivered_service']:8.3f} "
                  f"deficit {a['service_deficit_absolute']:+8.3f} "
                  f"({100*a['service_deficit_relative']:+6.2f}%) "
                  f"persist={str(a['service_persistent']):5s} "
                  f"EBU {D['ebu_total']:+9.3f} rests {D['voluntary_rests']:4d} "
                  f"FAILURE={a['is_service_alignment_failure']}")

    print("\n=== (5) outcome classes and integrity ===")
    from collections import Counter
    cls = Counter(r["outcome_class"] for r in records)
    for k in sv.PRECEDENCE:
        if cls.get(k):
            print(f"  {k:38s} {cls[k]:3d}")
    dom = [r["run_id"] for r in records if r["domain_failure_tick"] is not None]
    neg = [r["run_id"] for r in records if r["negative_state"]]
    print(f"  domain failures: {len(dom)} {dom if dom else ''}")
    print(f"  negative states: {len(neg)} {neg if neg else ''}")
    print(f"  max |ledger residual|: "
          f"{max(r['max_ledger_residual'] for r in records):.3e}")
    print(f"  reserve crossings total: "
          f"{sum(r['reserve_crossings'] for r in records)}; Allee "
          f"{sum(r['allee_crossings'] for r in records)}; dead sources "
          f"{sum(r['dead_sources'] for r in records)}; max overuse "
          f"{max(r['physical_overuse'] for r in records):.3e}")
    align_fail = [r["run_id"] for r in records
                  if r["service_alignment_predicate"]
                  and r["service_alignment_predicate"]["is_service_alignment_failure"]]
    print(f"  service-alignment failures: {len(align_fail)} "
          f"{align_fail if align_fail else ''}")

    print("\n=== (6) timestep sensitivity ===")
    for wname in sv.WORLDS:
        Dc = get(wname, "D_restricted_quote_greedy", "conservative")
        Dn = get(wname, "D_restricted_quote_greedy", "near_certificate")
        Bc = get(wname, "B_restricted_p1c", "conservative")
        Bn = get(wname, "B_restricted_p1c", "near_certificate")
        fc = Dc["service_alignment_predicate"]["is_service_alignment_failure"]
        fn = Dn["service_alignment_predicate"]["is_service_alignment_failure"]
        print(f"  {wname:26s} failure cons={fc} near={fn}  "
              f"D/B svc ratio cons "
              f"{(Dc['pbi_delivered_service']/Bc['pbi_delivered_service'] if Bc['pbi_delivered_service'] else float('nan')):.4f}"
              f"  near "
              f"{(Dn['pbi_delivered_service']/Bn['pbi_delivered_service'] if Bn['pbi_delivered_service'] else float('nan')):.4f}"
              f"  {'CONSISTENT' if fc == fn else 'TIMESTEP-SENSITIVE'}")

    summary = dict(
        plan_id=plan["plan_id"], plan_canonical_hash=PLAN_CANONICAL,
        plan_raw_sha256=PLAN_RAW, equation_version=eq.EQUATION_VERSION,
        python=platform.python_version(),
        gate="V3.0 Gate 1D (bounded capability-matched service-alignment study)",
        derived_semantics=sv.DERIVED_SEMANTICS,
        registered_dts={k: v for k, v in DTS},
        n_runs=len(records), runs=records,
        observational_identity_all=bool(all(ident)),
        n_service_alignment_failures=len(align_fail),
        service_alignment_failures=align_fail,
        domain_failures=dom, negative_states=neg,
        outcome_class_counts=dict(cls),
        capacity_cost_relative_mean=(math.fsum(cap) / len(cap) if cap else 0.0),
        non_claims=[
            "the bounded service wrapper is OUTSIDE the V2.8 D0 theorem "
            "(open problem O13); passing checks are numerical validation, "
            "never proof",
            "tau = 0 and eps_x = eps_u = 0: NO real-world latency or "
            "robustness claim",
            "cumulative signed EBU is an evaluation variable, not a wallet",
            "no needs, health, death, wallets, prices, transfers, personal "
            "debt, markets or learning exist",
            "no outcome authorizes automatic progression to the actor economy",
        ])
    blob = json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False)
    with open(SUMMARY, "w") as f:
        f.write(blob + "\n")
    with gzip.open(TRACE, "wt", encoding="utf-8") as f:
        for t in trace:
            f.write(json.dumps(t, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False) + "\n")
    print(f"\nwrote {SUMMARY} ({len(blob)} bytes) and {TRACE}")
    print(f"Every registered run appears exactly once ({len(records)} of "
          f"{plan['experiment_size']['total_runs']}); no run was dropped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
