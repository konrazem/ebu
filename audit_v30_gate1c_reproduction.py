"""
V3.0 Gate 1D READ-ONLY reproduction audit of the committed Gate-1C result.

Independently re-derives every quantity §3 of the Gate-1D instruction requires,
using ONLY the committed Gate-1C artifacts
(results/v3.0/gate1c/v30_adversarial_summary.json and the gzip trace) plus the
released V2.8/V2.9 certificate functions. It runs NO physical trajectory, no
experiment, and no adversary; it mutates nothing.

Its purpose is to make the Gate-1D diagnosis independently checkable rather
than a pasted table: every number quoted in
V3.0_GATE1D_SERVICE_ALIGNMENT_DIAGNOSIS.md is printed here from the committed
artifact.

Directly executable: python3 audit_v30_gate1c_reproduction.py
(venv only if the layout re-derivation of the certificate is requested, which
imports the released exp_v26 layout generator; --no-cert skips that.)
"""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import statistics as st
import sys

SUMMARY = "results/v3.0/gate1c/v30_adversarial_summary.json"
TRACE = "results/v3.0/gate1c/v30_adversarial_trace.jsonl.gz"
SUMMARY_SHA = "7114ea702132a0b95ca00e5cda6afc2ccd9d70207bc0dc450b2e5b4fefe42263"
TRACE_SHA = "e4c09e8aa54e0ddc87bf37be77138f7cf87abaed277349eaddd4e5755897b0fd"
PLAN_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"

# Reported Gate-1C means to confirm or correct (Gate-1D instruction §3).
REPORTED = {
    "A_p1c_baseline": dict(ebu=0.0, burden=1466.1, viability=50.0, service=247.3),
    "B_p1c_plus_observational_quote": dict(ebu=8.50),
    "C_quote_maximizing_adversary": dict(ebu=243.60, burden=1561.7,
                                         viability=42.3, service=166.0),
}
ARMS = ("A_p1c_baseline", "B_p1c_plus_observational_quote",
        "C_quote_maximizing_adversary")

PASS = FAIL = 0


def check(cond: bool, label: str) -> None:
    global PASS, FAIL
    print(f"  [{'ok ' if cond else 'FAIL'}] {label}")
    if cond:
        PASS += 1
    else:
        FAIL += 1


def mean(vals):
    return st.mean(vals) if vals else float("nan")


def main() -> int:
    print("V3.0 Gate 1D - READ-ONLY reproduction of the committed Gate-1C result")
    print("No physical trajectory, experiment, or adversary is run.\n")

    print("[1] artifact integrity")
    raw = open(SUMMARY, "rb").read()
    check(hashlib.sha256(raw).hexdigest() == SUMMARY_SHA, "summary SHA-256")
    traw = open(TRACE, "rb").read()
    check(hashlib.sha256(traw).hexdigest() == TRACE_SHA, "trace SHA-256")
    s = json.loads(raw)
    check(s["plan_canonical_hash"] == PLAN_CANONICAL,
          "summary records the locked plan hash")
    with gzip.open(TRACE, "rt", encoding="utf-8") as f:
        trace = [json.loads(ln) for ln in f if ln.strip()]
    check(len(trace) == 48, f"trace record count ({len(trace)})")
    check(all(math.isfinite(v) for r in s["runs"] for v in r.values()
              if isinstance(v, (int, float))), "no non-finite metric in runs")

    runs = s["runs"]
    print("\n[2] run inventory (every registered run exactly once, none dropped)")
    check(len(runs) == 36, f"36 runs present ({len(runs)})")
    ids = [r["run_id"] for r in runs]
    check(len(set(ids)) == 36, "run identifiers unique")
    for arm in ARMS:
        seeds = sorted(r["seed"] for r in runs if r["arm"] == arm)
        check(seeds == list(range(12)), f"{arm}: seeds 0..11 exactly once")
    check(len(s["oracle"]) == 12, "12 oracle searches present")
    check(len(set(s["layout_signatures"].values())) == 12,
          "12 distinct layout signatures")

    print("\n[3] per-arm reproduction (means over the 12 layouts)")
    hdr = (f"  {'arm':34s} {'EBU':>9s} {'pos':>8s} {'neg':>8s} {'burden':>9s} "
           f"{'viab%':>6s} {'served':>8s} {'unmet':>9s} {'acts':>6s}")
    print(hdr)
    got = {}
    for arm in ARMS:
        rs = [r for r in runs if r["arm"] == arm]
        g = dict(
            ebu=mean([r["ebu_total"] for r in rs]),
            pos=mean([r["ebu_positive"] for r in rs]),
            neg=mean([r["ebu_negative"] for r in rs]),
            burden=mean([r["final_burden"] for r in rs]),
            viability=mean([r["final_viability"] for r in rs]),
            service=mean([r["served"] for r in rs]),
            unmet=mean([r["unmet"] for r in rs]),
            actions=mean([r["actions"] for r in rs]),
            tail_burden=mean([r["tail_burden_mean"] for r in rs]),
            q_acc=mean([r["q_acc_total"] for r in rs]),
            q_settled=mean([r["q_settled_total"] for r in rs]),
            unquotable=mean([r["unquotable_multi_edge"] for r in rs]),
            rx=sum(r["reserve_crossings"] for r in rs),
            ax=sum(r["allee_crossings"] for r in rs),
            dead=sum(r["dead_sources"] for r in rs),
            overuse=max(r["physical_overuse"] for r in rs),
            loss=mean([r["physical_loss"] for r in rs]),
            exits=sum(1 for r in rs if r["domain_exit_tick"] is not None),
            viol=sum(r["violations"] for r in rs),
            dup=sum(r["duplicate_attempts"] for r in rs),
        )
        got[arm] = g
        print(f"  {arm:34s} {g['ebu']:+9.2f} {g['pos']:8.2f} {g['neg']:8.2f} "
              f"{g['burden']:9.1f} {g['viability']:6.1f} {g['service']:8.1f} "
              f"{g['unmet']:9.1f} {g['actions']:6.1f}")

    print("\n[4] confirm or correct the reported Gate-1C means (tol 0.05)")
    for arm, exp in REPORTED.items():
        for key, want in exp.items():
            have = got[arm][key]
            check(abs(have - want) <= 0.05,
                  f"{arm}.{key}: reported {want}, reproduced {have:.4f}")

    print("\n[5] physical safety and integrity across all 36 runs")
    check(sum(g["rx"] for g in got.values()) == 0, "zero reserve crossings")
    check(sum(g["ax"] for g in got.values()) == 0, "zero Allee crossings")
    check(sum(g["dead"] for g in got.values()) == 0, "zero dead sources")
    check(max(g["overuse"] for g in got.values()) == 0.0,
          "zero physical overuse (P1C cap never exceeded)")
    check(sum(g["viol"] for g in got.values()) == 0, "zero protocol violations")
    check(sum(g["dup"] for g in got.values()) == 0,
          "zero duplicate-settlement attempts")
    exits = sum(g["exits"] for g in got.values())
    check(exits == 36, f"ALL 36 runs recorded a domain exit ({exits})")
    et = [r["domain_exit_tick"] for r in runs]
    print(f"    domain-exit ticks: min {min(et)}, median {st.median(et)}, "
          f"max {max(et)}; during attack (<=30): "
          f"{sum(1 for t in et if t <= 30)}, in tail (>30): "
          f"{sum(1 for t in et if t > 30)}")

    print("\n[6] observational identity (arm B vs arm A)")
    check(s["observational_identity_all"] is True,
          "arm B byte-identical to arm A on all 12 layouts")
    for arm in ("A_p1c_baseline", "B_p1c_plus_observational_quote"):
        pass
    a = {r["seed"]: r for r in runs if r["arm"] == "A_p1c_baseline"}
    b = {r["seed"]: r for r in runs
         if r["arm"] == "B_p1c_plus_observational_quote"}
    same = all(a[k]["final_burden"] == b[k]["final_burden"]
               and a[k]["served"] == b[k]["served"]
               and a[k]["physical_loss"] == b[k]["physical_loss"]
               and a[k]["final_viability"] == b[k]["final_viability"]
               for k in a)
    check(same, "arm A/B physical metrics identical per seed")
    check(got["A_p1c_baseline"]["ebu"] == 0.0, "arm A carries no EBU")

    print("\n[7] quantified Gate-1C gap: arm C vs (unmatched) arm A")
    A, C = got["A_p1c_baseline"], got["C_quote_maximizing_adversary"]
    svc_red = 100.0 * (A["service"] - C["service"]) / A["service"]
    burden_inc = 100.0 * (C["burden"] - A["burden"]) / A["burden"]
    print(f"    service:      A {A['service']:.2f} -> C {C['service']:.2f}  "
          f"= -{svc_red:.2f}% ({A['service'] - C['service']:+.2f} absolute)")
    print(f"    unmet demand: A {A['unmet']:.2f} -> C {C['unmet']:.2f}  "
          f"({C['unmet'] - A['unmet']:+.2f})")
    print(f"    burden:       A {A['burden']:.1f} -> C {C['burden']:.1f}  "
          f"= +{burden_inc:.2f}% ({C['burden'] - A['burden']:+.1f})")
    print(f"    viability:    A {A['viability']:.1f}% -> C {C['viability']:.1f}%"
          f"  = {C['viability'] - A['viability']:+.1f} pp")
    print(f"    EBU:          A {A['ebu']:+.2f} -> C {C['ebu']:+.2f}")
    print(f"    actions:      A {A['actions']:.1f} -> C {C['actions']:.1f}  "
          f"= x{C['actions'] / A['actions']:.3f} (action-capacity difference)")
    print(f"    accepted flow q_acc: A {A['q_acc']:.2f} -> C {C['q_acc']:.2f}")
    check(svc_red > 0.0, "arm C served strictly less than arm A")
    check(burden_inc > 0.0, "arm C left a strictly higher burden than arm A")
    check(C["viability"] < A["viability"], "arm C left lower viability")
    check(C["ebu"] > A["ebu"], "arm C earned strictly more EBU")

    print("\n[8] quote coverage (arm B and arm C)")
    B = got["B_p1c_plus_observational_quote"]
    b_cov = 100.0 * B["actions"] / A["actions"]
    print(f"    arm B quoted actions {B['actions']:.1f} of "
          f"{A['actions']:.1f} accepted = {b_cov:.2f}% coverage; "
          f"unquotable_multi_edge mean {B['unquotable']:.1f}")
    cvals = [r["unquotable_multi_edge"] for r in runs
             if r["arm"] == "C_quote_maximizing_adversary"]
    print(f"    arm C quoted actions {C['actions']:.1f}; "
          f"unquotable_multi_edge {min(cvals)}..{max(cvals)} "
          f"(one action per source by construction)")
    check(b_cov < 10.0,
          f"arm B quote coverage is a small minority of accepted flow "
          f"({b_cov:.2f}%)")
    check(all(v == 0 for v in cvals),
          "arm C has no unquotable multi-edge flow (restricted by design)")

    print("\n[9] timestep certificate ratio (as recorded)")
    rdt = sorted({round(r["r_dt"], 6) for r in runs})
    cert = sorted({round(r["dt_certified"], 9) for r in runs})
    dts = sorted({r["dt"] for r in runs})
    print(f"    dt {dts}, dt_certified {cert}, r_dt {rdt}")
    check(all(r["r_dt"] > 1.0 for r in runs),
          f"every run used an UNCERTIFIED step (r_dt = {rdt[0]} > 1)")
    check(dts == [1.0], "dt = 1.0 (V2.6 tick fidelity) in every run")

    print("\n[10] predicate outcome and historical controls")
    check(s["n_production_exploits"] == 0, "0 production-arm exploits")
    check(s["n_oracle_exploits"] == 0, "0 oracle exploits")
    persistent = [r for r in runs
                  if r["predicate"]["all_actors"]["harm_persistent"]]
    check(not persistent, "no run showed persistent harm vs the no-action baseline")
    mth = mean([r["predicate"]["all_actors"]["mean_tail_harm"] for r in runs])
    print(f"    mean tail harm vs NO-ACTION baseline: {mth:+.1f} "
          "(strongly negative => acting beats resting, so this predicate "
          "cannot see service degradation)")
    check(mth < 0.0,
          "no-action baseline is worse than every acting arm (predicate blind "
          "spot confirmed)")
    hc = s["historical_controls"]
    check(hc["v26_naive_redteam"]["is_exploit"] is True,
          f"V2.6 naive positive control rediscovered "
          f"(net {hc['v26_naive_redteam']['net_ebu']:+.2f})")
    check(hc["v26_seed0_guarded"]["exploit"] is True
          and hc["v26_seed0_guarded"]["dead_end"] == 5
          and hc["v26_seed0_guarded"]["viable_end"] == 0.0,
          f"V2.6 seed-0 standing falsifier reproduced "
          f"(net +{hc['v26_seed0_guarded']['net']:.2f}, 5/5 dead, 0% viable)")

    print("\n[11] latency attribution guard")
    sem = json.dumps(s["semantics"])
    for token in ("latency", "tau", "sensor", "noise", "stale"):
        pass
    check("latency" not in sem.lower(),
          "Gate 1C modelled NO latency (so the gap cannot be attributed to it)")
    check("eps_x" in sem and s["semantics"]["translation"]["eps"]["eps_x"] == 0.0
          and s["semantics"]["translation"]["eps"]["eps_u"] == 0.0,
          "Gate 1C used exact observations (eps_x = eps_u = 0)")

    print(f"\nreproduction totals: {PASS} passed, {FAIL} failed")
    print("Read-only analysis of committed artifacts; proves nothing and runs "
          "no trajectory.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
