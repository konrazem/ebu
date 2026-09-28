"""The single official validation entry point. FAIL-CLOSED BEFORE THE FIRST DRAW.

    python3 -m e1a_v4.validation.runner --preflight-only
    python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation

The ordering this module exists to guarantee:

    1. bind_execution(...)   complete preflight, no RNG in scope
    2. only then             rng_factory(seed) is called for the first time

`--execute` additionally refuses unless the plan's `execution_authorised` flag is
true. In the frozen package that flag is FALSE, so the official command runs the
preflight and stops. The authorised execution stage flips it in a separate,
reviewed commit.

The preflight never constructs a generator. `run` takes an `rng_factory` so a
sentinel provider can prove, in a deterministic test, that a failed preflight
leaves RNG_CALL_COUNT at exactly 0.
"""

from __future__ import annotations

import argparse
import sys
from typing import Callable

from ..numerics import Refusal
from .plan import ExecutionBinding, bind_execution
from .seeds import ValidationSeedFamily

RNGFactory = Callable[[int], object]


class ExecutionNotAuthorised(Refusal):
    """Raised when the frozen plan has not been given execution authorisation."""


def preflight(root: str = ".", output_dir: str | None = None) -> ExecutionBinding:
    """Every fail-closed check, in order, with no RNG anywhere in scope."""
    return bind_execution(root=root, output_dir=output_dir)


def run(root: str = ".", *, rng_factory: RNGFactory | None = None,
        output_dir: str | None = None, execute: bool = False) -> ExecutionBinding:
    """Preflight, then refuse to execute unless separately authorised.

    `rng_factory` is NOT called during preflight. It is not called at all while
    `execution_authorised` is false in the frozen plan.
    """
    binding = preflight(root=root, output_dir=output_dir)
    if not execute:
        return binding
    if not binding.plan.get("execution_authorised", False):
        raise ExecutionNotAuthorised(
            "EXECUTION REFUSED: the frozen validation plan has "
            "execution_authorised = false. The synthetic-validation campaign is a "
            "separate authorised stage. No random number has been drawn."
        )
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
    print(f"  execution identity         : {binding.execution_identity}")
    print(f"  output directory           : {binding.output_dir}")
    print(f"  declared cases             : {len(binding.plan['cases'])}")
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
        print(f"EXECUTION REFUSED: {exc}")
        print("  RANDOM DRAWS: 0   TRAJECTORIES: 0")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
