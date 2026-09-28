"""The single official validation entry point. FAIL-CLOSED BEFORE THE FIRST DRAW.

    python3 -m e1a_v4.validation.runner --preflight-only
    python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation

The ordering this module exists to guarantee:

    1. bind_execution(...)   complete preflight, no RNG in scope
    2. only then             rng_factory(seed) is called for the first time

`--execute` additionally passes THE EXECUTION GATE, in this order:

    1. the official campaign driver exists on disk
    2. the external execution seal is FROZEN
    3. the recomputed execution identity equals the independently frozen seal
    4. the plan's `execution_authorised` flag is true

In the current package the driver is ABSENT and the seal is PRE_DRIVER, so the
official command runs the preflight and stops at step 1. Ordering matters: a
refusal must never read as "just flip the authorisation flag" when the driver
that would do the work does not exist.

The preflight never constructs a generator. `run` takes an `rng_factory` so a
sentinel provider can prove, in a deterministic test, that a failed preflight
leaves RNG_CALL_COUNT at exactly 0.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Callable

from ..numerics import Refusal
from .plan import ExecutionBinding, bind_execution
from .scope import CampaignCalibrationLedger, ReplicateCalibration
from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_exists, driver_state,
)
from .refusals import (
    CampaignDriverAbsent, DriverAbsent, ExecutionAuthorisationMissing,
    ExecutionIdentityUnsealed, ExecutionNotAuthorised, ExecutionSealNotFrozen,
)
from .seal import load_seal, require_execution_gate
from .seeds import CaseSeedAccess, ValidationSeedFamily

RNGFactory = Callable[[int], object]

#: Re-exported so `from e1a_v4.validation.runner import ExecutionNotAuthorised`
#: keeps working. The class now lives with the seal lifecycle it belongs to, and
#: its subclasses name WHICH precondition is missing.
__all__ = [
    "ExecutionNotAuthorised", "CampaignDriverAbsent", "DriverAbsent",
    "ExecutionSealNotFrozen", "ExecutionIdentityUnsealed",
    "ExecutionAuthorisationMissing",
    "preflight", "run", "main", "case_seed_access", "replicate_calibration",
]


def preflight(root: str = ".", output_dir: str | None = None) -> ExecutionBinding:
    """Every fail-closed check, in order, with no RNG anywhere in scope."""
    return bind_execution(root=root, output_dir=output_dir)


def case_seed_access(binding: ExecutionBinding, case_id: str) -> CaseSeedAccess:
    """The official seed route. A case may reach ONLY the families it declares.

    The low-level derivation functions remain importable and remain correct
    mathematics. They are not an authorisation: an official run reaches a family
    through this boundary, which reads the frozen case plan rather than trusting
    the caller to pass matching family arguments.
    """
    return binding.case_access(case_id)


def replicate_calibration(binding: ExecutionBinding, case_id: str, subcondition_id: str,
                          replicate: int,
                          ledger: CampaignCalibrationLedger) -> ReplicateCalibration:
    """The official per-replicate calibration boundary.

    REPLICATE-CONDITIONAL CALIBRATION is the adopted architecture: each replicate
    of each declared SUBCONDITION is calibrated at its own realised Branch-A
    condition, and its Branch-B stream is not released until that artifact is
    locked. An official run reaches a validation stream only through here.

    A case that evaluates no P1 / Block-1 quantity has no calibration step and is
    not gated on one: gating it would let a calibration refusal change an outcome
    it has no scientific bearing on.
    """
    return binding.replicate_calibration(case_id, subcondition_id, replicate, ledger)


def run(root: str = ".", *, rng_factory: RNGFactory | None = None,
        output_dir: str | None = None, execute: bool = False) -> ExecutionBinding:
    """Preflight, then refuse to execute unless separately authorised.

    `rng_factory` is NOT called during preflight. It is not called at all while
    `execution_authorised` is false in the frozen plan.
    """
    binding = preflight(root=root, output_dir=output_dir)
    if not execute:
        return binding
    # THE EXECUTION GATE. Driver, then seal, then identity, then authorisation --
    # most fundamental missing precondition first, so a refusal is never mistaken
    # for "just flip the flag". Every branch refuses before `rng_factory` is touched.
    require_execution_gate(root, binding.plan, binding.execution_identity)
    if rng_factory is None:
        raise Refusal("an authorised execution must supply an RNG factory")
    # --- the authorised stage continues from here; nothing below runs today ----
    raise Refusal(
        "EXECUTION PATH NOT IMPLEMENTED IN THE PRE-EXECUTION STAGE: the campaign "
        "driver is added by the authorised execution task, after this package is "
        "reviewed. Preflight, plan, seeds, generators and schema are frozen."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="e1a_v4.validation.runner",
                                     description="E1a v4 synthetic validation")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--i-have-execution-authorisation", action="store_true")
    args = parser.parse_args(argv)
    try:
        binding = preflight(root=args.root, output_dir=args.output_dir)
    except Refusal as exc:
        print(f"PREFLIGHT REFUSED: {exc}")
        return 2
    print("PREFLIGHT PASSED")
    print(f"  contract sha256            : {binding.binding.sha256}")
    print(f"  plan sha256                : {binding.plan_sha256}")
    print(f"  seed map sha256            : {binding.seed_map_sha256}")
    print(f"  analysis procedure identity: {binding.analysis_identity}")
    print(f"  output directory           : {binding.output_dir}")
    print(f"  declared cases             : {len(binding.plan['cases'])}")
    seal = load_seal(args.root)
    label = ("PRE-DRIVER PACKAGE EXECUTION IDENTITY (NOT the final seal)"
             if not seal.is_frozen else "execution identity")
    print(f"  {label}:")
    print(f"      {binding.execution_identity}")
    print(f"  execution seal state       : {seal.state}")
    print(f"  expected execution identity: {seal.expected_execution_identity}")
    print(f"  official campaign driver   : {OFFICIAL_CAMPAIGN_DRIVER_PATH} "
          f"({driver_state(args.root)})   [canonical, identity-bound]")
    print(f"  execution_authorised       : {binding.plan.get('execution_authorised', False)}")
    if args.preflight_only or not args.execute:
        print("  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)")
        return 0
    if not args.i_have_execution_authorisation:
        print("EXECUTION REFUSED: --execute requires --i-have-execution-authorisation")
        return 2
    try:
        run(root=args.root, output_dir=args.output_dir, execute=True)
    except Refusal as exc:
        text = str(exc)
        print(text if text.startswith("EXECUTION REFUSED") else f"EXECUTION REFUSED: {text}")
        print("  RANDOM DRAWS: 0   TRAJECTORIES: 0")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
