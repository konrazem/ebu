"""
V3.0 Gate 1D-A Attempt-2 runner: OUTPUT ROUTING ONLY.

Executes the identical frozen Gate 1D study (exp_v30_service.main, imported
unmodified) exactly once, directing its three output artifacts to the isolated
directory results/v3.0/gate1d/attempt2/ so that the committed Attempt-1
artifacts remain byte-identical at their original paths.

Nothing scientific is touched: worlds, arms, policies, action menus,
quantities, timesteps, certificates, thresholds, tolerances (beyond the
already-committed registered reserve diagnostic tolerance in service_v30),
equations, simulation ordering, tick count, plan hashes, and classification
precedence are all those of the frozen runner. The plan-hash gate, the
no-command-line-option rule, the certificate gate, and the fail-closed
refusal to overwrite a completed study all apply unchanged - the overwrite
guard now protects the attempt2/ summary.

Run: python3 exp_v30_service_attempt2.py
"""
import os

import exp_v30_service as exp

exp.OUTDIR = "results/v3.0/gate1d/attempt2"
exp.SUMMARY = os.path.join(exp.OUTDIR, "v30_service_alignment_summary.json")
exp.TRACE = os.path.join(exp.OUTDIR, "v30_service_alignment_trace.jsonl.gz")

if __name__ == "__main__":
    raise SystemExit(exp.main())
