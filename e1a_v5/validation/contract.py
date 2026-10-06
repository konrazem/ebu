"""Plan-to-code correspondence, checked against the MACHINE PLAN.

The V4 meta-test compared the case registry to the dispatcher -- both of them
code -- and so could not detect the two controls being weakened away from the
frozen plan.  ``CTL-ETA-T-COV`` and ``CTL-AXIAL-MEMORY`` were reduced from 200
stochastic replicates to one deterministic check each while
``docs/e1a/e1a_v5_validation_plan.json`` continued to require 200, and the
test passed.

Here the plan JSON is parsed and compared field by field against the
implementation.  The plan is the source of truth: any difference is a
failure, there is no warning-only mode, and there is no fallback that treats
the registry as authoritative.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

#: Repository-relative path of the machine-readable validation plan.
PLAN_PATH = os.path.join("docs", "e1a", "e1a_v5_validation_plan.json")

#: Fields compared for every case.
COMPARED_FIELDS = (
    "case_id",
    "purpose",
    "replicates",
    "seed_namespace",
    "expected_event",
    "family",
    "detail",
)


class PlanContractViolation(Exception):
    """The implementation does not match the frozen machine plan."""


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, os.pardir, os.pardir))


def load_plan(path: str | None = None) -> dict:
    full = path or os.path.join(_repo_root(), PLAN_PATH)
    with open(full, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _normalise(value: Any) -> Any:
    """JSON round-trips tuples to lists; compare on the JSON shape."""
    if isinstance(value, tuple):
        return [_normalise(v) for v in value]
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in sorted(value.items())}
    return value


def case_as_plan_entry(case) -> dict:
    """The implementation's view of one case, in the plan's own shape."""
    return {
        "case_id": case.case_id,
        "purpose": case.purpose,
        "replicates": case.replicates,
        "seed_namespace": case.seed_namespace,
        "expected_event": case.expected_event.value,
        "family": case.family,
        "detail": _normalise(case.config.as_dict()),
    }


@dataclass(frozen=True)
class CorrespondenceReport:
    missing_from_code: tuple[str, ...] = ()
    missing_from_plan: tuple[str, ...] = ()
    field_mismatches: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not (
            self.missing_from_code or self.missing_from_plan
            or self.field_mismatches
        )

    def as_list(self) -> list[str]:
        out = [f"case {c} is in the plan but not in the code"
               for c in self.missing_from_code]
        out += [f"case {c} is in the code but not in the plan"
                for c in self.missing_from_plan]
        out += list(self.field_mismatches)
        return out


def check_correspondence(cases: Sequence, plan: Mapping | None = None
                         ) -> CorrespondenceReport:
    """Compare every registered case against the machine plan, field by field."""
    doc = plan if plan is not None else load_plan()
    raw_plan = doc.get("cases", [])
    plan_cases = {c["case_id"]: c for c in raw_plan}
    code_cases = {c.case_id: case_as_plan_entry(c) for c in cases}

    missing_code = tuple(sorted(set(plan_cases) - set(code_cases)))
    missing_plan = tuple(sorted(set(code_cases) - set(plan_cases)))
    mismatches: list[str] = []
    # A duplicate on either side would vanish into its map and take its
    # mismatch with it, so duplicates are detected before the maps are used.
    for label, ids in (("plan", [c.get("case_id") for c in raw_plan]),
                       ("code", [c.case_id for c in cases])):
        seen: set[str] = set()
        for cid in ids:
            if cid in seen:
                mismatches.append(f"{cid}: duplicated in the {label}")
            seen.add(cid)
    for cid in sorted(set(plan_cases) & set(code_cases)):
        p, c = plan_cases[cid], code_cases[cid]
        for field in COMPARED_FIELDS:
            if field not in p:
                mismatches.append(f"{cid}: plan has no {field!r} field")
                continue
            pv, cv = _normalise(p[field]), c[field]
            if pv != cv:
                mismatches.append(
                    f"{cid}: {field} differs -- plan {pv!r}, code {cv!r}"
                )
    return CorrespondenceReport(missing_code, missing_plan, tuple(mismatches))


def require_correspondence(cases: Sequence, plan: Mapping | None = None) -> None:
    report = check_correspondence(cases, plan)
    if not report.ok:
        raise PlanContractViolation(
            "implementation does not match the frozen machine plan:\n  "
            + "\n  ".join(report.as_list())
        )
