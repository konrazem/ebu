"""
V3.0 Gate 1C official runner for the preregistered Q22 adversarial replay.

Executes the registered study EXACTLY ONCE: 12 released V2.6 layouts (seeds
0..11, including the known seed-0 standing falsifier) x 3 arms
  A - P1C physical baseline (no EBU-guided selection),
  B - P1C + observational exact quote (physically identical to A),
  C - production-local exact-quote-maximizing adversary,
plus the separately labelled red-team oracle and the historical V2.6 positive
controls.

DISCIPLINE
  * recomputes and enforces the canonical plan hash; refuses to run on mismatch;
  * takes NO command-line option;
  * REFUSES to overwrite a completed study (fail closed, V2.9 convention);
  * records every run exactly once; drops nothing; records domain exits and
    terminal status as first-class outputs;
  * strict JSON (allow_nan=False) for every emitted record.

"No exploit found" means only: no exploit was found within the declared
fixtures, seeds, action menu, search depth, width, and predicate. It is NEVER
a security proof.

Run with the project venv (the released exp_v26 layout generator imports
matplotlib):  venv/bin/python exp_v30_adversary.py
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
import adversary_v30 as adv

PLAN_PATH = "v30_quote_validation_plan.json"
PLAN_CANONICAL = "a1916e8ecf366cee93a5284a0d8fcb68a3e1a429f49ce62b9f5914df87f94061"
PLAN_RAW = "5f01a1fd554bfb2f5e684dc318a805f2887d51274e456c98d1a1d5788d1a6f4f"
OUTDIR = "results/v3.0/gate1c"
SUMMARY = os.path.join(OUTDIR, "v30_adversarial_summary.json")
TRACE = os.path.join(OUTDIR, "v30_adversarial_trace.jsonl.gz")


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


def _run_record(arm, seed, world, is_src, st, base_burden, base_tail,
                attack_tail, dt_cert):
    """Full per-run record: EBU and physical state side by side."""
    m = adv.physical_metrics(world, st.x, is_src)
    verdict = adv.classify_profitable_harm(st.ebu_total, attack_tail, base_tail)
    coalition_ebu = math.fsum(st.ebu_by_actor[i] for i in adv.COALITION
                              if i < len(st.ebu_by_actor)) \
        if st.ebu_by_actor else 0.0
    verdict_coal = adv.classify_profitable_harm(coalition_ebu, attack_tail,
                                                base_tail)
    rec = dict(
        run_id=f"{arm}-seed{seed}", arm=arm, seed=seed,
        # --- EBU (evaluation variables; NOT a wallet) ---
        ebu_total=st.ebu_total, ebu_positive=st.ebu_positive,
        ebu_negative=st.ebu_negative, ebu_coalition=coalition_ebu,
        # --- actions ---
        actions=st.actions, q_req_total=st.q_req_total,
        q_acc_total=st.q_acc_total, q_settled_total=st.q_settled_total,
        unquotable_multi_edge=st.unquotable_multi_edge,
        violations=st.violations, duplicate_attempts=st.duplicate_attempts,
        # --- physical state ---
        physical_loss=st.loss_total, physical_overuse=st.overuse,
        served=st.served, unmet=st.unmet,
        reserve_crossings=st.reserve_crossings,
        allee_crossings=st.allee_crossings,
        dead_sources=m["dead"], below_R=m["below_R"], below_A=m["below_A"],
        final_burden=m["burden"], final_viability=m["viable"],
        source_stock=m["source_stock"], total_stock=m["total_stock"],
        tail_burden_mean=(math.fsum(attack_tail) / len(attack_tail)
                          if attack_tail else None),
        tail_viability=m["viable"],
        baseline_final_burden=base_burden[-1] if base_burden else None,
        baseline_tail_burden_mean=(math.fsum(base_tail) / len(base_tail)
                                   if base_tail else None),
        # --- terminal status ---
        domain_exit_tick=st.domain_exit_tick,
        terminal_status=("domain_exit" if st.domain_exit_tick is not None
                         else "completed"),
        dt=adv.DT, dt_certified=dt_cert, r_dt=adv.DT / dt_cert,
        # --- predicate components, all physical ---
        predicate=dict(all_actors=verdict, coalition=verdict_coal),
        profitable_harm_exploit=bool(verdict["is_exploit"]
                                     or verdict_coal["is_exploit"]),
    )
    return rec


def _arm_run(arm, seed, world, x0, cfg, is_src, dt_cert):
    """One (arm, layout) run: attack horizon H_RUN, then a TAIL persistence
    window with every actor resting, against the PAIRED no-action baseline."""
    base_full, _bx, _bex = adv.no_action_baseline(world, x0, cfg, is_src,
                                                 adv.H_RUN + adv.TAIL)
    fn = {"A_p1c_baseline": adv.arm_a_p1c,
          "B_p1c_plus_observational_quote": adv.arm_b_observational,
          "C_quote_maximizing_adversary": adv.arm_c_quote_greedy}[arm]
    st = fn(world, x0, cfg, is_src, adv.H_RUN)
    # persistence tail: actors rest (no transport), physical dynamics only
    tail_burden = []
    st_tail = st
    empty = d0.World(cells=world.cells, edges=())
    x = st.x
    import p1c_v29 as p1c
    for t in range(1, adv.TAIL + 1):
        x = p1c.p1c_step(empty, x, adv.DT, {}).x_after
        tail_burden.append(d0.V_total(world, x))
    st_end = st.with_field(x)
    if st_end.domain_exit_tick is None and any(
            x[i] < -adv.DOMAIN_TOL or x[i] > world.cells[i].K + adv.DOMAIN_TOL
            for i in range(world.n)):
        st_end = st_end.__class__(**{**st_end.__dict__,
                                     "domain_exit_tick": adv.H_RUN + adv.TAIL})
    return _run_record(arm, seed, world, is_src, st_end, base_full,
                       base_full[adv.H_RUN:adv.H_RUN + adv.TAIL], tail_burden,
                       dt_cert), st


def main() -> int:
    if len(sys.argv) > 1:
        raise SystemExit("FATAL: this harness takes no command-line option")
    plan = _plan()
    if os.path.exists(SUMMARY):
        raise SystemExit(f"FATAL: {SUMMARY} exists; the registered study runs "
                         "exactly once and refuses to overwrite results")
    os.makedirs(OUTDIR, exist_ok=True)

    print("EBP V3.0 Gate 1C - preregistered Q22 adversarial replay")
    print(f"  plan canonical hash: {PLAN_CANONICAL}")
    print(f"  python: {platform.python_version()}")
    print(f"  frozen: DEPTH={adv.DEPTH} WIDTH={adv.WIDTH} TAIL={adv.TAIL} "
          f"QUANTS={adv.QUANTS} COALITION={list(adv.COALITION)} "
          f"H_RUN={adv.H_RUN} MARGIN={adv.MARGIN} dt={adv.DT}")
    print(f"  layouts: seeds {list(adv.LAYOUT_SEEDS)} (seed 0 = standing "
          "falsifier)\n")
    print("  A falsification search, never a proof of security.\n")

    arms = ("A_p1c_baseline", "B_p1c_plus_observational_quote",
            "C_quote_maximizing_adversary")
    records, trace = [], []

    print("=== (1) Registered arms: 12 layouts x 3 arms ===")
    hdr = (f"  {'run':34s} {'EBU':>10s} {'pos':>8s} {'neg':>8s} {'acts':>5s} "
           f"{'burden':>9s} {'viab%':>6s} {'dead':>4s} {'Rx':>3s} {'Ax':>3s} "
           f"{'served':>8s} {'exploit':>7s}")
    print(hdr)
    arm_states = {}
    for seed in adv.LAYOUT_SEEDS:
        world, x0, cfg, is_src = adv.translate_layout(seed)
        dt_cert = adv.certified_dt(world)
        for arm in arms:
            rec, st = _arm_run(arm, seed, world, x0, cfg, is_src, dt_cert)
            records.append(rec)
            arm_states[(arm, seed)] = st
            trace.append(dict(run_id=rec["run_id"], kind="arm_history",
                              history=[list(h) for h in st.history[:400]],
                              history_truncated=len(st.history) > 400,
                              history_len=len(st.history)))
            print(f"  {rec['run_id']:34s} {rec['ebu_total']:+10.3f} "
                  f"{rec['ebu_positive']:8.3f} {rec['ebu_negative']:8.3f} "
                  f"{rec['actions']:5d} {rec['final_burden']:9.2f} "
                  f"{rec['final_viability']:6.1f} {rec['dead_sources']:4d} "
                  f"{rec['reserve_crossings']:3d} {rec['allee_crossings']:3d} "
                  f"{rec['served']:8.2f} "
                  f"{str(rec['profitable_harm_exploit']):>7s}")

    print("\n=== (2) Observational identity: arm B vs arm A (paired) ===")
    ident = []
    for seed in adv.LAYOUT_SEEDS:
        a = arm_states[("A_p1c_baseline", seed)]
        b = arm_states[("B_p1c_plus_observational_quote", seed)]
        same = (a.x == b.x)
        ident.append(same)
        print(f"  seed {seed:2d}: trajectories byte-identical: {same}  "
              f"(max |diff| = "
              f"{max(abs(p - q) for p, q in zip(a.x, b.x)):.3e})")
    print(f"  all identical: {all(ident)}")

    print("\n=== (3) Red-team ORACLE (separately labelled; uses global harm "
          "as an EXTERNAL objective - never production-actor information) ===")
    oracle_recs = []
    for seed in adv.LAYOUT_SEEDS:
        world, x0, cfg, is_src = adv.translate_layout(seed)
        dt_cert = adv.certified_dt(world)
        base_full, _bx, _bex = adv.no_action_baseline(
            world, x0, cfg, is_src, adv.DEPTH + adv.TAIL)
        beams, explored = adv.redteam_oracle(world, x0, cfg, is_src,
                                             adv.DEPTH, adv.WIDTH, base_full)
        best = None
        import p1c_v29 as p1c
        for (st, score, harm) in beams:
            tail = []
            x = st.x
            empty = d0.World(cells=world.cells, edges=())
            for t in range(adv.TAIL):
                x = p1c.p1c_step(empty, x, adv.DT, {}).x_after
                tail.append(d0.V_total(world, x))
            v = adv.classify_profitable_harm(st.ebu_total, tail,
                                             base_full[adv.DEPTH:adv.DEPTH + adv.TAIL])
            cand = dict(seed=seed, run_id=f"ORACLE-seed{seed}",
                        arm="ORACLE_redteam", ebu_total=st.ebu_total,
                        ebu_positive=st.ebu_positive,
                        ebu_negative=st.ebu_negative,
                        actions=st.actions, cum_harm=harm,
                        reserve_crossings=st.reserve_crossings,
                        allee_crossings=st.allee_crossings,
                        final_burden=d0.V_total(world, st.x),
                        physical_overuse=st.overuse,
                        domain_exit_tick=st.domain_exit_tick,
                        terminal_status=("domain_exit"
                                         if st.domain_exit_tick is not None
                                         else "completed"),
                        explored=explored, predicate=v,
                        profitable_harm_exploit=bool(v["is_exploit"]),
                        history=[list(h) for h in st.history])
            if best is None or (cand["profitable_harm_exploit"],
                                cand["cum_harm"]) > (best["profitable_harm_exploit"],
                                                     best["cum_harm"]):
                best = cand
        oracle_recs.append(best)
        print(f"  seed {seed:2d}: best oracle beam  EBU={best['ebu_total']:+9.3f}  "
              f"cum_harm={best['cum_harm']:+9.2f}  "
              f"persistent={best['predicate']['harm_persistent']}  "
              f"exploit={best['profitable_harm_exploit']}  "
              f"explored={explored}")

    print("\n=== (4) Historical V2.6 positive controls (released code) ===")
    import exp_v26
    from ebu_v26 import (State, baseline_BR_schedule, redteam_search,
                         find_exploit)
    g, actors, _src = exp_v26.redteam_world()
    init = State(list(g.x), [0.0] * len(actors))
    controls = {}
    for mode in ("naive", "guarded"):
        base, _ = baseline_BR_schedule(g, actors, init, adv.DEPTH + adv.TAIL,
                                       mode)
        beams, expl = redteam_search(g, actors, list(adv.COALITION), init, mode,
                                     adv.DEPTH, adv.WIDTH, adv.QUANTS,
                                     base[:adv.DEPTH], min_net=0.5)
        v = find_exploit(g, actors, list(adv.COALITION), beams, mode,
                         base[adv.DEPTH:adv.DEPTH + adv.TAIL], adv.TAIL)
        controls[f"v26_{mode}_redteam"] = dict(
            is_exploit=bool(v.is_exploit), net_ebu=v.net_ebu,
            harm_persistent=bool(v.harm_persistent),
            mean_tail_harm=v.harm_margin, explored=expl)
        print(f"  V2.6 {mode:8s} red-team: exploit={v.is_exploit}  "
              f"net EBU={v.net_ebu:+.2f}  persistent={v.harm_persistent}  "
              f"mean tail harm={v.harm_margin:+.2f}")
    r0 = exp_v26.studyC_layout(0)
    controls["v26_seed0_guarded"] = dict(
        net=r0["net"], harmful=bool(r0["harmful"]), exploit=bool(r0["exploit"]),
        dead_end=r0.get("dead_end"), n_src=r0["n_src"],
        viable_end=r0.get("viable_end"), tail_margin=r0.get("tail_margin"))
    print(f"  V2.6 seed-0 guarded (standing falsifier): net=+{r0['net']:.2f}  "
          f"exploit={r0['exploit']}  dead={r0.get('dead_end')}/{r0['n_src']}  "
          f"viability@end={r0.get('viable_end'):.0f}%")

    # ---------------- verdict ----------------
    print("\n=== (5) Gate-1C verdict ===")
    prod_exploits = [r for r in records if r["profitable_harm_exploit"]]
    oracle_exploits = [r for r in oracle_recs if r["profitable_harm_exploit"]]
    print(f"  production-local arms: {len(prod_exploits)} profitable "
          f"persistent-harm exploit(s) in {len(records)} runs")
    print(f"  red-team ORACLE:       {len(oracle_exploits)} profitable "
          f"persistent-harm exploit(s) in {len(oracle_recs)} searches")
    for r in prod_exploits + oracle_exploits:
        print(f"    EXPLOIT: {r['run_id']}  EBU={r['ebu_total']:+.3f}  "
              f"persistent={r['predicate'].get('harm_persistent', r['predicate'])}")
    if not prod_exploits and not oracle_exploits:
        print("  => NO EXPLOIT FOUND within the declared fixtures, seeds, "
              "action menu, search depth, width, and predicate.")
        print("     This is NOT a proof of security, not 'exploit-free', and "
              "not a guarantee.")
    exits = [r["run_id"] for r in records if r["domain_exit_tick"] is not None]
    print(f"  domain exits (recorded, none dropped): {len(exits)} "
          f"{exits if exits else ''}")

    summary = dict(
        plan_id=plan["plan_id"], plan_canonical_hash=PLAN_CANONICAL,
        plan_raw_sha256=PLAN_RAW, equation_version=eq.EQUATION_VERSION,
        python=platform.python_version(),
        gate="V3.0 Gate 1C (Q22 adversarial replay)",
        semantics=adv.GATE1C_SEMANTICS,
        layout_signatures={str(s): adv.layout_signature(
            adv.translate_layout(s)[3]) for s in adv.LAYOUT_SEEDS},
        arms=list(arms), runs=records, oracle=oracle_recs,
        historical_controls=controls,
        observational_identity_all=bool(all(ident)),
        n_runs=len(records),
        n_production_exploits=len(prod_exploits),
        n_oracle_exploits=len(oracle_exploits),
        domain_exits=exits,
        non_claims=[
            "no exploit found means only: none within the declared fixtures, "
            "seeds, action menu, search depth, width, and predicate",
            "this is not a security proof, not exploit-freedom, not a guarantee",
            "cumulative EBU is an evaluation variable, not a wallet",
            "no actor economy, wallet, health, need, price, or transfer exists",
            "O8 (overexecution settlement) and O1-O9 remain open",
        ])
    blob = json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False)
    with open(SUMMARY, "w") as f:
        f.write(blob + "\n")
    with gzip.open(TRACE, "wt", encoding="utf-8") as f:
        for t in trace:
            f.write(json.dumps(t, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False) + "\n")
        for o in oracle_recs:
            f.write(json.dumps(dict(kind="oracle_beam", **o), sort_keys=True,
                               separators=(",", ":"), ensure_ascii=True,
                               allow_nan=False) + "\n")
    print(f"\nwrote {SUMMARY} ({len(blob)} bytes) and {TRACE}")
    print("Every registered run appears exactly once; no run was dropped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
