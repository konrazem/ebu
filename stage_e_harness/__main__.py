"""Outcome-blind command surface for the deterministic Stage E zipapp."""

from __future__ import annotations

import argparse
import json
import sys

from .canonical import Refusal, canonical_bytes
from .cache import exercise_controls_detail
from .dag import agreement_suite as dag_agreement_suite
from .dag import complexity_cell as dag_complexity_cell
from .execution import StageEExecutionRefusal, guard_registered_configuration
from .growth import growth_conformance
from .mobius import agreement_suite as mobius_agreement_suite
from .mobius import complexity_cell as mobius_complexity_cell
from .recursive import recursive_conformance
from .registry import load_bindings, validate_partition


def _emit(value: object) -> None:
    sys.stdout.buffer.write(canonical_bytes(value) + b"\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="stage-e-harness")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("registry")
    guard = sub.add_parser("guard")
    guard.add_argument("configuration_id")
    sub.add_parser("mobius-agreement")
    mobius_cell = sub.add_parser("mobius-cell")
    mobius_cell.add_argument("n", type=int)
    mobius_cell.add_argument("repetition", type=int)
    sub.add_parser("dag-agreement")
    dag_cell = sub.add_parser("dag-cell")
    dag_cell.add_argument("vertices", type=int)
    dag_cell.add_argument("edges", type=int)
    dag_cell.add_argument("cell_class")
    sub.add_parser("cache-conformance")
    sub.add_parser("recursive-conformance")
    sub.add_parser("growth-conformance")
    args = parser.parse_args(argv)
    try:
        if args.command == "registry":
            validate_partition()
            _emit({"status": "PASS", "studies": [binding.study_id for binding in load_bindings()], "scientific_execution_count": 0})
        elif args.command == "guard":
            guard_registered_configuration(args.configuration_id)
            _emit({"status": "SYNTHETIC_NONREGISTERED", "scientific_execution_count": 0})
        elif args.command == "mobius-agreement":
            _emit({"status": "PASS", **mobius_agreement_suite(), "scientific_execution_count": 0})
        elif args.command == "mobius-cell":
            _emit({"status": "PASS", **mobius_complexity_cell(args.n, args.repetition), "scientific_execution_count": 0})
        elif args.command == "dag-agreement":
            _emit({"status": "PASS", **dag_agreement_suite(), "scientific_execution_count": 0})
        elif args.command == "dag-cell":
            _emit({"status": "PASS", **dag_complexity_cell(args.vertices, args.edges, args.cell_class), "scientific_execution_count": 0})
        elif args.command == "cache-conformance":
            _emit({"status": "PASS", **exercise_controls_detail(), "scientific_execution_count": 0})
        elif args.command == "recursive-conformance":
            _emit({"status": "PASS", **recursive_conformance(), "scientific_execution_count": 0})
        elif args.command == "growth-conformance":
            _emit({"status": "PASS", **growth_conformance(), "scientific_execution_count": 0})
        else:
            raise AssertionError
    except StageEExecutionRefusal as exc:
        _emit({"status": "REFUSED", "receipt": exc.receipt, "scientific_execution_count": 0})
        return 3
    except Refusal as exc:
        _emit({"status": "REFUSED", "reason": str(exc), "scientific_execution_count": 0})
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
