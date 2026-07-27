"""
V2.9 Gate 2.4B - serialization-repair audit tests (strict fail-closed JSON).

Validates serialization_v29.py and its integration into the D9/D10 result
write path, and validates the COMMITTED Attempt-2 artifacts against the strict
rules - WITHOUT running any trajectory: no physical step function is called,
no run is regenerated, and no committed result file is modified.

Covers (Gate 2.4B Sec 5):
  1/2  non-finite stability_tau / stability_amp normalize to null (+reason);
  3    finite diagnostics pass through unchanged;
  4-7  non-finite states / flows / service+unmet / ledger diagnostics FAIL
       (ledger residuals remain forbidden - they are not nullable);
  8    strict serialization never emits NaN/Infinity tokens;
  9    the committed 144-run summary passes strict validation as-is;
  10   normalization changes no classification, service, stock, crossing,
       or run ordering.

Plain stdlib, directly executable, import-safe:  python3 test_v29_serialization.py
"""
from __future__ import annotations
import copy
import gzip
import io
import json
import math
import os

import serialization_v29 as ser
import exp_v29_d9_d10 as X

PASS = 0
FAIL = 0
GROUPS: list[list] = []

SUMMARY_PATH = os.path.join("results", "v2.9", "d9_d10", "v29_d9_d10_summary.json")
TRACE_GZ_PATH = os.path.join("results", "v2.9", "d9_d10", "v29_d9_d10_trace.jsonl.gz")


def group(title: str) -> None:
    GROUPS.append([title, 0, 0])
    print(f"[{len(GROUPS)}] {title}")


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        GROUPS[-1][1] += 1
        print(f"  PASS  {name}" + (f"  ({detail})" if detail else ""))
    else:
        FAIL += 1
        GROUPS[-1][2] += 1
        print(f"  FAIL  {name}" + (f"  ({detail})" if detail else ""))


def raises_nonfinite(fn) -> bool:
    try:
        fn()
    except ser.NonFiniteFieldError:
        return True
    except Exception:
        return False
    return False


def synth_agg(**kw):
    """A synthetic COMPLETED aggregate record shaped like the harness output
    (every finiteness-relevant field class represented; values arbitrary but
    finite). Not a scientific result."""
    base = dict(
        run_id="SYNTH", experiment="D10", policy="P1", dt=0.05, ticks=400,
        burn_in=100, persistence_window=200, R_eff=11.0, A=5.0, demand=2.7,
        chi=0.0, group_chi=None, hard_cap=False, d_over_gmax=0.9, eta=0.7,
        theta=0.1, delta=1.0, rho=0.4, r_dt=None,
        terminal_status="completed", domain_exit_tick=None,
        domain_exit_cells=None, domain_exit_direction=None, valid_ticks=400,
        reserve_crossings=0, first_reserve_crossing_tick=None,
        allee_crossings=0, first_allee_crossing_tick=None,
        time_below_reserve=0, time_below_allee=0,
        lower_violation_ticks=0, upper_violation_ticks=0,
        locally_infeasible_ticks=0, p1c_binding_ticks=0,
        p1c_binding_fraction=0.0,
        cumulative_transport_loss=2.0, cumulative_requested_service=110.0,
        cumulative_delivered=100.0, cumulative_unmet_demand=8.0,
        O_physical=0.0, min_source_stock=11.0, final_source_stock=12.5,
        final_source_regen=1.0, dead_source_indicator=False,
        final_viability=1.0, postburn_mean_viability=1.0,
        final_delivered=2.7, postburn_mean_delivered=2.7,
        stability_class="converged", stability_tau=0.001, stability_amp=0.002,
        max_ledger_residual=1e-15, theorem_eligible_ticks=0,
        theorem_violation_count=0, primary_classification="safe_service",
    )
    base.update(kw)
    return base


def synth_trace_row():
    """A per-tick trace record row (states/flows/service/certificate data)."""
    return {"run_id": "SYNTH", "schema": X.TICK_FIELDS, "rows": [[
        1, [13.0, 2.0], [12.8, 1.96], [4.4, -5.0], 5.35, 14.4, 5.35, 4.8,
        0.107, 0.185, "P", False, False, False, False, 3.05e-16, None, None,
        False, False]]}


# ===========================================================================
# [1] nullable-diagnostic normalization (tests 1, 2, 3)
# ===========================================================================
def test_group1():
    group("nullable-diagnostic normalization (stability_tau/stability_amp only)")
    a = ser.normalize_aggregate_diagnostics(synth_agg(stability_tau=math.inf))
    check("(1) +Infinity stability_tau becomes null",
          a["stability_tau"] is None)
    check("(1) reason recorded: overflow_on_diverging_trajectory",
          a.get(ser.NORMALIZATION_KEY, {}).get("stability_tau")
          == ser.REASON_OVERFLOW)
    b = ser.normalize_aggregate_diagnostics(synth_agg(stability_amp=math.inf))
    check("(2) +Infinity stability_amp becomes null",
          b["stability_amp"] is None)
    check("(2) reason recorded: overflow_on_diverging_trajectory",
          b.get(ser.NORMALIZATION_KEY, {}).get("stability_amp")
          == ser.REASON_OVERFLOW)
    c = ser.normalize_aggregate_diagnostics(
        synth_agg(stability_tau=-math.inf, stability_amp=math.nan))
    check("-Infinity/NaN diagnostics also become null",
          c["stability_tau"] is None and c["stability_amp"] is None)
    # natively-None diagnostics (early domain exit -> empty post-burn window)
    d = ser.normalize_aggregate_diagnostics(
        synth_agg(stability_tau=None, stability_amp=None,
                  terminal_status="domain_exit", stability_class="unclassified"))
    check("natively-None diagnostics keep null and record undefined_after_domain_exit",
          d["stability_tau"] is None
          and d[ser.NORMALIZATION_KEY]["stability_tau"] == ser.REASON_UNDEFINED_EXIT
          and d[ser.NORMALIZATION_KEY]["stability_amp"] == ser.REASON_UNDEFINED_EXIT)
    e0 = synth_agg()
    e1 = ser.normalize_aggregate_diagnostics(copy.deepcopy(e0))
    check("(3) ordinary finite record passes through completely unchanged",
          e1 == e0)
    check("(3) finite diagnostics are not altered and get no reason entry",
          e1["stability_tau"] == e0["stability_tau"]
          and e1["stability_amp"] == e0["stability_amp"]
          and ser.NORMALIZATION_KEY not in e1)


# ===========================================================================
# [2] fail-closed on every non-nullable field (tests 4, 5, 6, 7)
# ===========================================================================
def test_group2():
    group("fail-closed: non-finite in any non-nullable field raises")
    cases = [
        ("(4) state: min_source_stock", dict(min_source_stock=-math.inf)),
        ("(4) state: final_source_stock", dict(final_source_stock=math.nan)),
        ("(5) flow: cumulative_transport_loss",
         dict(cumulative_transport_loss=math.inf)),
        ("(5) flow: cumulative_requested_service",
         dict(cumulative_requested_service=math.inf)),
        ("(6) service: cumulative_delivered", dict(cumulative_delivered=math.nan)),
        ("(6) service: postburn_mean_delivered",
         dict(postburn_mean_delivered=math.inf)),
        ("(6) unmet demand: cumulative_unmet_demand",
         dict(cumulative_unmet_demand=math.inf)),
        ("(7) ledger diagnostic: max_ledger_residual stays FORBIDDEN",
         dict(max_ledger_residual=math.inf)),
        ("physical over-use: O_physical", dict(O_physical=math.nan)),
        ("timestep: dt", dict(dt=math.inf)),
        ("regen: final_source_regen", dict(final_source_regen=math.nan)),
    ]
    for name, kw in cases:
        check(name + " -> NonFiniteFieldError",
              raises_nonfinite(
                  lambda kw=kw: ser.normalize_aggregate_diagnostics(synth_agg(**kw))))
    check("ledger residual is not in the nullable-diagnostic allowlist",
          "max_ledger_residual" not in ser.NULLABLE_DIAGNOSTICS
          and set(ser.NULLABLE_DIAGNOSTICS) == {"stability_tau", "stability_amp"})
    # trace rows: states/flows/service/certificate data are never nullable
    row = synth_trace_row()
    row["rows"][0][2][0] = math.inf          # x_after state cell
    check("(4) trace state (x_after) -> NonFiniteFieldError",
          raises_nonfinite(lambda: ser.assert_all_finite(row, "trace")))
    row2 = synth_trace_row()
    row2["rows"][0][7] = math.nan            # delivered_service
    check("(6) trace service (delivered_service) -> NonFiniteFieldError",
          raises_nonfinite(lambda: ser.assert_all_finite(row2, "trace")))
    row3 = synth_trace_row()
    row3["rows"][0][15] = math.inf           # ledger_residual
    check("(7) trace ledger_residual -> NonFiniteFieldError",
          raises_nonfinite(lambda: ser.assert_all_finite(row3, "trace")))
    check("missing diagnostic field is a hard error (schema fail-closed)",
          raises_nonfinite(lambda: ser.normalize_aggregate_diagnostics(
              {k: v for k, v in synth_agg().items() if k != "stability_tau"})))


# ===========================================================================
# [3] strict serializer (test 8)
# ===========================================================================
def test_group3():
    group("strict serialization emits no NaN/Infinity and fails closed")
    s = ser.strict_dumps(ser.normalize_aggregate_diagnostics(
        synth_agg(stability_tau=math.inf)))
    check("(8) normalized record serializes with no NaN/Infinity token",
          "NaN" not in s and "Infinity" not in s and '"stability_tau": null' in s)
    def _dump_inf():
        ser.strict_dumps({"x": math.inf})
    try:
        _dump_inf()
        raised = False
    except ValueError:
        raised = True
    check("(8) strict_dumps raises ValueError on a raw non-finite float", raised)
    fh = io.StringIO()
    try:
        ser.strict_dump({"x": math.nan}, fh)
        raised = False
    except ValueError:
        raised = True
    check("(8) strict_dump raises ValueError on NaN", raised)
    check("(8) allow_nan cannot be re-enabled through kwargs",
          (lambda: [t for t in [True] if not _try_allow_nan()])() == [True])
    check("stdlib default WOULD have emitted the bad token (negative control)",
          "Infinity" in json.dumps({"x": math.inf}))


def _try_allow_nan() -> bool:
    try:
        ser.strict_dumps({"x": math.inf}, allow_nan=True)
        return True
    except ValueError:
        return False


# ===========================================================================
# [4] committed Attempt-2 artifacts pass strict validation (test 9)
# ===========================================================================
def test_group4():
    group("committed 144-run summary + trace pass strict validation (no rerun)")
    raw = open(SUMMARY_PATH, encoding="utf-8").read()
    strict_fail = []
    summary = json.loads(raw, parse_constant=strict_fail.append)
    check("(9) committed summary parses with NO non-standard JSON constant",
          not strict_fail)
    runs = summary["runs"]
    check("(9) summary holds exactly 144 unique run records",
          len(runs) == 144 and len({r["run_id"] for r in runs}) == 144)
    ok = True
    for r in runs:
        rest = {k: v for k, v in r.items() if k not in ser.NULLABLE_DIAGNOSTICS}
        try:
            ser.assert_all_finite(rest, r["run_id"])
        except ser.NonFiniteFieldError:
            ok = False
    check("(9) every non-nullable committed field is finite", ok)
    nulls = [r for r in runs if r["stability_tau"] is None or r["stability_amp"] is None]
    check("(9) null diagnostics appear ONLY on the 18 domain-exit records",
          len(nulls) == 18
          and all(r["terminal_status"] == "domain_exit" for r in nulls)
          and all(r["stability_tau"] is None and r["stability_amp"] is None
                  for r in nulls))
    check("(9) committed summary re-serializes under allow_nan=False",
          isinstance(ser.strict_dumps(summary), str))
    n = 0
    ok = True
    with gzip.open(TRACE_GZ_PATH, "rt", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line, parse_constant=strict_fail.append)
            try:
                ser.assert_all_finite(rec, rec["run_id"])
            except ser.NonFiniteFieldError:
                ok = False
            n += 1
    check("(9) committed gzip trace: 144 rows, all strictly finite, no bad token",
          n == 144 and ok and not strict_fail)
    check("committed artifact bytes contain no unquoted non-finite token",
          isinstance(json.loads(
              raw, parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c))),
              dict))


# ===========================================================================
# [5] normalization preserves the science (test 10)
# ===========================================================================
def test_group5():
    group("normalization changes no classification/service/stock/crossing/order")
    protected = ("primary_classification", "stability_class", "terminal_status",
                 "cumulative_delivered", "cumulative_unmet_demand",
                 "postburn_mean_delivered", "final_delivered",
                 "min_source_stock", "final_source_stock", "O_physical",
                 "reserve_crossings", "allee_crossings",
                 "first_reserve_crossing_tick", "first_allee_crossing_tick",
                 "valid_ticks", "max_ledger_residual")
    src = synth_agg(stability_tau=math.inf, stability_amp=math.inf,
                    primary_classification="collapse",
                    stability_class="accumulation")
    before = copy.deepcopy(src)
    after = ser.normalize_aggregate_diagnostics(src)
    check("(10) every protected scientific field is bit-identical",
          all(after[k] == before[k] for k in protected))
    check("(10) only the two diagnostics and the reason record differ",
          {k for k in before if before[k] != after.get(k)}
          == {"stability_tau", "stability_amp"}
          and set(after) - set(before) == {ser.NORMALIZATION_KEY})
    # ordering: normalizing a run LIST record-by-record keeps order and ids
    batch = [synth_agg(run_id=f"R{i}",
                       stability_tau=(math.inf if i % 2 else 0.01))
             for i in range(6)]
    ids_before = [r["run_id"] for r in batch]
    normed = [ser.normalize_aggregate_diagnostics(r) for r in batch]
    check("(10) run ordering and identities are preserved",
          [r["run_id"] for r in normed] == ids_before)
    # committed data: fields OTHER than tau/amp/reasons would be untouched
    summary = json.load(open(SUMMARY_PATH, encoding="utf-8"))
    sample = [r for r in summary["runs"] if r["stability_tau"] is not None][:5]
    ok = True
    for r in sample:
        cp = copy.deepcopy(r)
        out = ser.normalize_aggregate_diagnostics(cp)
        if out != r:
            ok = False
    check("(10) finite committed records round-trip normalization unchanged", ok)


# ===========================================================================
# [6] write-path integration (source-level; no trajectory executed)
# ===========================================================================
def test_group6():
    group("harness write path uses the strict fail-closed serializer")
    src_text = open("exp_v29_d9_d10.py", encoding="utf-8").read()
    check("harness imports serialization_v29",
          "import serialization_v29 as ser" in src_text)
    check("summary is written via ser.strict_dump",
          "ser.strict_dump(summary, fh" in src_text)
    check("trace lines are written via ser.strict_dumps",
          "ser.strict_dumps(r, separators" in src_text)
    check("trace records are pre-validated with assert_all_finite",
          "ser.assert_all_finite(r, f\"trace[" in src_text)
    check("aggregates are normalized before serialization",
          "ser.normalize_aggregate_diagnostics(agg)" in src_text)
    check("no bare json.dump remains on the harness result-write path",
          "json.dump(summary" not in src_text
          and 'json.dumps(r, separators=(",", ":")) for r in all_rows'
          not in src_text)


# ===========================================================================
if __name__ == "__main__":
    import sys
    print("=" * 76)
    print("V2.9 Gate 2.4B - serialization repair audit (NO trajectory executed)")
    print("=" * 76)
    for fn in (test_group1, test_group2, test_group3, test_group4, test_group5,
               test_group6):
        fn()
    print("-" * 76)
    for k, (title, p, f) in enumerate(GROUPS, 1):
        print(f"group {k:>2}: {p:>3} passed, {f} failed - {title}")
    print(f"total checks: {PASS} passed, {FAIL} failed in {len(GROUPS)} groups")
    print("No trajectory was run; no committed artifact was modified.")
    if FAIL:
        print("SERIALIZATION AUDIT FAILED.")
        raise SystemExit(1)
    print("Serialization audit passed.")
