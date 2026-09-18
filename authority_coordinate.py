"""Fail-closed authority coordinate for the V3.0 programme.

This module is INFRASTRUCTURE.  It proves nothing, adopts nothing, registers
nothing and executes nothing.  It encodes, as data, the source-lineage and
status map reconciled in ``V3.0_PROGRAMME_AUTHORITY_COORDINATE.md`` and then
REFUSES, rather than defaults, when work asks for an authority that the active
branch does not carry.

Execution safety.  Importing this module must not call a model step, a runner,
a simulation, a trajectory, a tick function, a subprocess, or the network, and
must not open any file for writing.  It reads nothing at import time.  Every
public function is a pure function of its arguments plus, in two clearly named
cases, read-only filesystem probing of the working directory.

Why it exists.  Three gaps motivate it, all recorded in the coordinate document:

1. The Stage D master matrix, the Stage D and Stage E authorities, the Stage E
   harness code, the Stage F implementation and the atomic-action package are
   NOT on the active branch.  Work that silently proceeds as if they were is the
   failure this module is built to prevent.
2. ``src/``, ``stage_e_harness/``, ``sd01_stage_f_binding/``, ``tests/``,
   ``sd01_preparation/`` and ``scripts/`` exist on disk holding only stale
   ``.pyc`` bytecode from other lineages.  Python's implicit namespace-package
   rule therefore makes ``import stage_e_harness`` SUCCEED with an empty
   package.  A presence check by import alone would be wrong.
3. Per-action allocation of a simultaneous group's value is an open candidate
   question (O3 / 16.O3).  Diagnostics are permitted; settlement, causal
   entitlement and allocation are not.  The distinction is enforced here rather
   than left to convention.

Status vocabulary is load-bearing and is never collapsed.  A single object may
carry several statuses; ``ebu_quote_v30``'s law is CANDIDATE and IMPLEMENTATION
at once, and is not EVIDENCE at all.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass, field
from typing import Mapping, Sequence

__all__ = [
    "AuthorityError", "AuthorityUnavailable", "ExcludedMaterial",
    "UnlicensedAllocation", "NamespacePackageTrap",
    "THEOREM", "IMPLEMENTATION", "CANDIDATE", "EVIDENCE", "INFRASTRUCTURE",
    "MISSING", "RULEBOOK", "STATUS_VOCABULARY",
    "ACTIVE_BRANCH", "COORDINATE_ID", "SUPERSEDED_COORDINATE_ID",
    "COORDINATE_DOCUMENT",
    "AUTHOR_DECISION_DATE", "PROGRAMME_COORDINATE", "DECISION_NON_CLAIMS",
    "Rulebook", "RULEBOOKS", "rulebook", "require_rulebook",
    "rulebook_is_evidence", "require_execution_permission",
    "NOT_VALUE_ALLOCATION",
    "Authority", "AUTHORITIES", "EXCLUDED",
    "OPEN_ESCALATIONS", "RESOLVED_ESCALATIONS",
    "STALE_BYTECODE_DIRECTORIES",
    "authority", "require_authority", "require_status", "is_on_active_branch",
    "require_not_excluded", "allocation_role", "require_diagnostic_only",
    "namespace_package_traps", "require_no_namespace_trap",
    "missing_authorities", "escalations_blocking",
]


# ---------------------------------------------------------------------------
# refusals - every one of these is a fail-closed path, never a warning
# ---------------------------------------------------------------------------
class AuthorityError(Exception):
    """Base: the authority coordinate refused an operation."""


class AuthorityUnavailable(AuthorityError):
    """A required authority is not carried by the active branch."""


class ExcludedMaterial(AuthorityError):
    """Material the author has excluded from the active programme."""


class UnlicensedAllocation(AuthorityError):
    """A per-action allocation was requested that no authority licenses."""


class NamespacePackageTrap(AuthorityError):
    """A directory resolves as an empty namespace package (stale lineage)."""


# ---------------------------------------------------------------------------
# status vocabulary - six categories, never collapsed into one label
# ---------------------------------------------------------------------------
THEOREM = "THEOREM"                  # proved, under stated assumptions
IMPLEMENTATION = "IMPLEMENTATION"    # committed code
CANDIDATE = "CANDIDATE"              # prospective / proposed / not adopted
EVIDENCE = "EVIDENCE"                # an executed, recorded scientific result
INFRASTRUCTURE = "INFRASTRUCTURE"    # preparation; not a scientific result
MISSING = "MISSING"                  # authority required and absent
RULEBOOK = "RULEBOOK"                # author-adopted PROSPECTIVE rules

STATUS_VOCABULARY = (
    THEOREM, IMPLEMENTATION, CANDIDATE, EVIDENCE, INFRASTRUCTURE, MISSING,
    RULEBOOK,
)

# RULEBOOK is the narrowest status in the vocabulary and the easiest to
# over-read, so its meaning is fixed here.  It means: the author has adopted
# this source, AT A PINNED COMMIT, as the rules that PROSPECTIVE work must be
# designed against.  It does NOT mean the source was merged, that its content
# is evidence, or that anything may execute.  RULEBOOK and EVIDENCE are
# mutually exclusive by construction (enforced in ``Authority.__post_init__``).

ACTIVE_BRANCH = "v3.0-local-ebu-foundation"
COORDINATE_ID = "W-2"
SUPERSEDED_COORDINATE_ID = "W-1"   # retained: W-2 extends it, nothing is voided
COORDINATE_DOCUMENT = "V3.0_PROGRAMME_AUTHORITY_COORDINATE.md"


@dataclass(frozen=True)
class Authority:
    """One governing source, with its location and its separated statuses.

    ``on_active_branch`` is the load-bearing field.  An authority that exists
    somewhere in the object database but not on the active branch cannot govern
    work here, and ``require_authority`` refuses it.
    """
    name: str
    path: str
    home_branch: str
    commit: str
    on_active_branch: bool
    statuses: tuple
    note: str = ""

    def __post_init__(self):
        if not self.statuses:
            raise ValueError(f"{self.name}: at least one status is required")
        for s in self.statuses:
            if s not in STATUS_VOCABULARY:
                raise ValueError(
                    f"{self.name}: unknown status {s!r}; the vocabulary is "
                    f"{STATUS_VOCABULARY}")
        if self.on_active_branch and MISSING in self.statuses:
            raise ValueError(
                f"{self.name}: cannot be MISSING and on the active branch")
        if RULEBOOK in self.statuses and EVIDENCE in self.statuses:
            raise ValueError(
                f"{self.name}: RULEBOOK and EVIDENCE are mutually exclusive. "
                f"Adopting a source as prospective rules does not make its "
                f"content a scientific result.")


def _a(*args, **kw) -> Authority:
    return Authority(*args, **kw)


# ---------------------------------------------------------------------------
# the author's programme decision (2026-09-16) - resolves E1
# ---------------------------------------------------------------------------
# Recorded verbatim in intent, as DATA.  This decision settles which lineage
# supplies the governing Stage D/E/F coordinate; it settles nothing else.
AUTHOR_DECISION_DATE = "2026-09-16"

PROGRAMME_COORDINATE = (
    "current V3 / Gate 1D-C remains the historical local foundation and "
    "evidence record",
    "Stage D defines the prospective SD study programme",
    "Stage E defines prospective harness requirements",
    "Stage F defines prospective route-preparation requirements",
    "no prospective material is scientific evidence or permission to execute",
    "every scientific world, parameter, controller definition, metric, "
    "threshold, preregistration, AWS request, and execution packet remains "
    "separately authorized",
)

# The three things this decision explicitly does NOT say.  Kept as data so a
# caller can quote them rather than reconstruct them.
DECISION_NON_CLAIMS = (
    "the rulebook branches were NOT merged into the active branch",
    "the rulebooks' prospective material is NOT scientific evidence",
    "this decision does NOT authorize execution",
)


@dataclass(frozen=True)
class Rulebook:
    """One source-locked prospective rulebook, pinned to an exact commit.

    ``commit`` is load-bearing: the author locked these sources at a specific
    revision, so the rulebook is read AT THAT COMMIT and nowhere else.  The
    branch tip may move; the rulebook does not.
    """
    name: str
    scope: str
    branch: str
    commit: str
    status_quote: str

    def __post_init__(self):
        if len(self.commit) < 7:
            raise ValueError(f"{self.name}: an exact commit is required")


RULEBOOKS: Mapping[str, Rulebook] = {r.name: r for r in (
    Rulebook(
        "stage_d", "prospective SD study programme",
        "research/stage-d-scientific-validation-authority", "8936bb4",
        "prospective scientific-validation authority candidate; documentation "
        "and strict-JSON records only; no harness implementation, model "
        "execution, outcome inspection, result, figure, book, or publication"),
    Rulebook(
        "stage_e", "prospective harness requirements",
        "research/stage-e-scientific-harness-authority", "0b1d58a",
        "prospective authority candidate only"),
    Rulebook(
        "stage_f", "prospective route-preparation requirements",
        "codex/sd01-stage-f-implementation", "cc5581c",
        "USER_OPERATED_FORMAL_SMOKE_READY_NOT_RUN; SD-01/ empty; no "
        "trajectory ran"),
)}


# ---------------------------------------------------------------------------
# the registry - mirrors V3.0_PROGRAMME_AUTHORITY_COORDINATE.md sections 2 & 3
# ---------------------------------------------------------------------------
AUTHORITIES: Mapping[str, Authority] = {a.name: a for a in (
    # --- present on the active branch ---
    _a("agents", "AGENTS.md", ACTIVE_BRANCH, "", True,
       (INFRASTRUCTURE,), "process authority; not scientific content"),
    _a("local_ebu_foundation", "V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md",
       ACTIVE_BRANCH, "", True, (THEOREM, CANDIDATE),
       "Obs 6.12 / Thm 8.2 / Prop 10.2 proved; design 6.5 is CANDIDATE"),
    _a("conservation", "CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md",
       ACTIVE_BRANCH, "a89945a", True, (CANDIDATE,),
       "prospective documentation; explicitly no experimental result"),
    _a("sequential_parallel_bridge", "SEQUENTIAL_PARALLEL_BRIDGE.md",
       ACTIVE_BRANCH, "", True, (CANDIDATE,),
       "grouping rule is 'deliberately conservative and provisional'"),
    _a("quote_law", "ebu_quote_v30.py", ACTIVE_BRANCH, "", True,
       (IMPLEMENTATION, CANDIDATE),
       "implemented and bound to v30_quote_validation_plan.json; the law "
       "itself is candidate design 6.5, NOT accepted"),
    _a("o14_multi_edge_plan", "v30_o14_multi_edge_plan.json", ACTIVE_BRANCH,
       "", True, (CANDIDATE,), "O3 remains open; no settling aggregate arm"),
    _a("gate1dc", "results/v3.0/gate1dc/", ACTIVE_BRANCH, "f2c60e1", True,
       (EVIDENCE,),
       "executed 2026-09-12: 30 runs, 200 ticks; outcomes 20/8/2; no "
       "falsifier fired. Narrow historical scope; not a general result"),
    _a("d5_benchmark", "results/benchmarks/d5/", ACTIVE_BRANCH, "e21db1d",
       True, (INFRASTRUCTURE,),
       "NON-SCIENTIFIC SOFTWARE MEASUREMENT; timing only, never physics"),
    _a("sd03_readiness", "SD_03_PRE_EXECUTION_READINESS.md", ACTIVE_BRANCH,
       "45a6622", True, (CANDIDATE,), "SD-03 blocked on P1-P7"),
    _a("sd_register", "SD_01_TO_14_MASTER_TEST_REGISTER.md", ACTIVE_BRANCH,
       "d0d572e", True, (CANDIDATE,),
       "self-declared PROSPECTIVE, DERIVED, SUBORDINATE, Not an authority; "
       "its superseded 'only stage' sentence is corrected in place, with the "
       "false claim retained verbatim in a correction note (sd03_readiness "
       "section 8 governs the point)"),

    # --- NOT on the active branch: every one of these refuses ---
    _a("stage_d_matrix", "stage_d_scientific_validation_master_matrix.json",
       "codex/sd01-stage-f-implementation", "8856d23", False,
       (CANDIDATE, MISSING, RULEBOOK),
       "blob e6cd44f8b9; status 1.0.0-candidate / "
       "PROSPECTIVE_NO_EXECUTION_NO_OUTCOMES. Identical blob at the locked "
       "Stage F commit cc5581c, of which 8856d23 is an ancestor"),
    _a("stage_d_authority", "STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md",
       "research/stage-d-scientific-validation-authority", "8936bb4", False,
       (MISSING, RULEBOOK),
       "the normative human authority for Stage D; adopted as the prospective "
       "SD study rulebook at this exact commit"),
    _a("stage_e_authority", "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md",
       "research/stage-e-scientific-harness-authority", "0b1d58a", False,
       (CANDIDATE, MISSING, RULEBOOK),
       "'prospective authority candidate only'; no accepted harness PASS. "
       "Adopted as the prospective harness rulebook; adoption of RULES is not "
       "a Stage E PASS"),
    _a("stage_e_harness", "stage_e_harness/", "codex/sd01-stage-f-implementation",
       "cc5581c", False, (IMPLEMENTATION, MISSING, RULEBOOK),
       "mobius.py, dag.py, cache.py, oracles.py, registry.py, checkpoint.py; "
       "zero tracked files at HEAD. mobius.py is Boolean Mobius CONFORMANCE, "
       "not a value-allocation rule - see NOT_VALUE_ALLOCATION"),
    _a("stage_f_binding", "sd01_stage_f_binding/",
       "codex/sd01-stage-f-implementation", "cc5581c", False,
       (IMPLEMENTATION, MISSING, RULEBOOK),
       "ladder.py and tests/sd01_stage_f/; allocation.py allocates WORKERS "
       "and budget, not per-action value - see NOT_VALUE_ALLOCATION"),
    _a("atomic_generator", "ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md",
       "framework/atomic-generator-foundation-authority", "d0d1edd", False,
       (CANDIDATE, MISSING),
       "F1-F16 remain candidate decisions; does not self-close Gate A"),
    _a("atomic_interaction",
       "ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md",
       "framework/atomic-interaction-declaration-authority", "0094087", False,
       (CANDIDATE, MISSING), "unaccepted candidate"),
    _a("post_atomic_open_problems", "POST_ATOMIC_OPEN_PROBLEM_REGISTER.md",
       "framework/canonical-topology-motif-programme-authority", "4e1f5ba",
       False, (CANDIDATE, MISSING), ""),
    _a("aws_c0", "aws/c0/", "aws/campaign-orchestration", "df7e844", False,
       (INFRASTRUCTURE, MISSING),
       "formal user-operated smoke is READY but has NOT run; no authorization"),
    _a("sd01_aws_preparation", "SD01_AWS_ENVIRONMENT_PREPARATION.md",
       "codex/sd01-stage-f-implementation", "cc5581c", False,
       (INFRASTRUCTURE, MISSING),
       "environment measured, role/profile created, 11 artifacts staged, one "
       "VersionId durability probe passed; SD-01/ is empty; no trajectory ran"),
)}


# ---------------------------------------------------------------------------
# material excluded by the author - kept visible, never deleted
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Exclusion:
    name: str
    reason: str
    preserved_at: tuple
    reopen_requires: str


EXCLUDED: Mapping[str, Exclusion] = {e.name: e for e in (
    Exclusion(
        "nhx_long_horizon",
        "N/H/X is excluded from the active programme. The SD register records "
        "it as an unregistered alternative parameterization of SD-01 that "
        "would substitute for SD-01 rather than contribute to it.",
        ("f3eed78", "f6a4ee9", "36373aa"),
        "explicit author reopening; history is NOT rewritten and no committed "
        "material is deleted",
    ),
)}


# ---------------------------------------------------------------------------
# open escalations - author decisions, mirrored from the coordinate section 6
# ---------------------------------------------------------------------------
# E1 is RESOLVED by the author's 2026-09-16 decision and is recorded here, not
# deleted: the resolution is part of the trace.  Every other escalation stands.
RESOLVED_ESCALATIONS: Mapping[str, str] = {
    "E1": "Which lineage supplies the governing Stage D/E/F coordinate. "
          "RESOLVED 2026-09-16 by author decision: current V3 remains the "
          "project's home and the historical evidence record; the exact Stage "
          "D (8936bb4), Stage E (0b1d58a) and Stage F (cc5581c) documents on "
          "their existing branches are the PROSPECTIVE future-programme "
          "rulebook. The branches were NOT merged, their material is NOT "
          "evidence, and the decision does NOT authorize execution.",
}

OPEN_ESCALATIONS: Mapping[str, str] = {
    "E2": "Whether a per-action field decomposition is registered at m >= 2. "
          "Theorem at m = 1 only (Thm 8.2 under T3). Blocks: any scientific "
          "claim requiring a specific simultaneous-action allocation rule. "
          "Does NOT block diagnostic-only group evaluation.",
    "E3": "SD-03 prerequisite P1: f_e, Psi_e and J_e are unregistered for the "
          "declared domain. Blocks: SD-03 execution.",
    "E4": "Acceptance of the atomic-action authority package (F1-F16). "
          "Blocks: any atomic-ontology claim used as authority.",
    "E5": "Any SD-01 successor campaign and any AWS execution or spend. "
          "Blocks: all cloud work.",
}


# directories that exist on disk carrying only stale bytecode from other
# lineages.  Not deleted - see the coordinate document section 2.2.
STALE_BYTECODE_DIRECTORIES = (
    "src", "tests", "stage_e_harness", "sd01_preparation",
    "sd01_stage_f_binding", "scripts",
)


# ---------------------------------------------------------------------------
# lookups and guards
# ---------------------------------------------------------------------------
def authority(name: str) -> Authority:
    """Return one registered authority, or refuse."""
    try:
        return AUTHORITIES[name]
    except KeyError:
        raise AuthorityUnavailable(
            f"{name!r} is not a registered authority. Known: "
            f"{sorted(AUTHORITIES)}") from None


def is_on_active_branch(name: str) -> bool:
    return authority(name).on_active_branch


def require_authority(name: str) -> Authority:
    """Return the authority, or REFUSE if the active branch does not carry it.

    This is the central guard.  It exists because an authority present
    elsewhere in the object database cannot govern work here, and because
    silently proceeding as if it could is the specific failure the programme
    ordering exists to prevent.
    """
    found = authority(name)
    if not found.on_active_branch:
        raise AuthorityUnavailable(
            f"{name!r} is NOT carried by the active branch {ACTIVE_BRANCH!r}. "
            f"It lives at {found.path!r} on {found.home_branch!r} "
            f"(commit {found.commit or 'unrecorded'}). "
            f"Coordinate {COORDINATE_ID} does not authorize work that depends "
            f"on it; see {COORDINATE_DOCUMENT} section 6. "
            f"Note: {found.note or 'none'}")
    return found


def require_status(name: str, *required: str) -> Authority:
    """Require an authority AND that it carries every named status.

    Refuses a status outside the vocabulary rather than silently missing it,
    so a typo can never weaken a guard.
    """
    found = require_authority(name)
    for status in required:
        if status not in STATUS_VOCABULARY:
            raise ValueError(
                f"unknown status {status!r}; the vocabulary is "
                f"{STATUS_VOCABULARY}")
        if status not in found.statuses:
            raise AuthorityUnavailable(
                f"{name!r} does not carry status {status}; it carries "
                f"{found.statuses}. Statuses are never collapsed: an "
                f"implementation is not a theorem and a benchmark is not "
                f"scientific evidence.")
    return found


def require_not_excluded(name: str) -> None:
    """Refuse material the author has excluded from the active programme."""
    if name in EXCLUDED:
        e = EXCLUDED[name]
        raise ExcludedMaterial(
            f"{name!r} is excluded from the active programme. {e.reason} "
            f"It is preserved, not deleted, at {', '.join(e.preserved_at)}. "
            f"Reopening requires: {e.reopen_requires}")


def missing_authorities() -> tuple:
    """Every registered authority the active branch does not carry."""
    return tuple(sorted(n for n, a in AUTHORITIES.items()
                        if not a.on_active_branch))


def escalations_blocking(*codes: str) -> tuple:
    """Return the escalation text for the named codes, refusing unknown ones."""
    out = []
    for c in codes:
        if c not in OPEN_ESCALATIONS:
            raise AuthorityError(
                f"unknown escalation {c!r}; known: {sorted(OPEN_ESCALATIONS)}")
        out.append((c, OPEN_ESCALATIONS[c]))
    return tuple(out)


# ---------------------------------------------------------------------------
# rulebook access - prospective rules, read at a pinned commit
# ---------------------------------------------------------------------------
def rulebook(name: str) -> Rulebook:
    """Return one source-locked rulebook, or refuse."""
    try:
        return RULEBOOKS[name]
    except KeyError:
        raise AuthorityUnavailable(
            f"{name!r} is not an adopted rulebook. Adopted: "
            f"{sorted(RULEBOOKS)}") from None


def require_rulebook(name: str) -> Rulebook:
    """Return a rulebook for PROSPECTIVE design work only.

    Deliberately separate from ``require_authority``.  ``require_authority``
    answers "may this govern work on the active branch?" and still refuses all
    three rulebooks, because they are still not carried here.  This function
    answers the different question the author's decision settled: "which rules
    must prospective work be designed against?"

    Collapsing the two would be the exact error the decision warns about -
    treating an adopted prospective rulebook as if it had been merged.
    """
    return rulebook(name)


def rulebook_is_evidence(name: str) -> bool:
    """Always False. Present so the question has one answer, not a convention."""
    rulebook(name)
    return False


def require_execution_permission(name: str) -> None:
    """Always refuses. Adopting rules is not permission to run them."""
    book = rulebook(name)
    raise AuthorityUnavailable(
        f"the {book.name!r} rulebook grants NO execution permission. The "
        f"author's {AUTHOR_DECISION_DATE} decision adopts it as prospective "
        f"rules only, at {book.branch}@{book.commit}, and records: "
        f"{DECISION_NON_CLAIMS[2]}. Its own status reads: "
        f"{book.status_quote!r}. Every scientific world, parameter, "
        f"controller definition, metric, threshold, preregistration, AWS "
        f"request and execution packet remains separately authorized.")


# ---------------------------------------------------------------------------
# simultaneous-group allocation guard (escalation E2)
# ---------------------------------------------------------------------------
# Name collisions that must never be mistaken for an adopted per-action value
# allocation.  Each was checked against the locked rulebook source; each is
# something else entirely.  E2 stays open in spite of these names.
NOT_VALUE_ALLOCATION: Mapping[str, str] = {
    "stage_e_harness/mobius.py":
        "exact Boolean Mobius CONFORMANCE algorithms over subset tables "
        "(harness correctness and complexity), not a Mobius allocation of a "
        "simultaneous group's value among its actions",
    "sd01_stage_f_binding/allocation.py":
        "allocation of WORKERS to an instance and of campaign BUDGET "
        "dimensions; its own text records that budget exhaustion 'is not a "
        "scientific outcome'. Not per-action value allocation",
    "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3C_SETTLEMENT_CAUSALITY_REPAIR"
    "_AUTHORITY_AMENDMENT.md":
        "'prospective documentation-only authority candidate; unimplemented; "
        "current fail-closed runtime remains controlling', and it is "
        "downstream of the atomic package that escalation E4 records as "
        "unaccepted. Adopts nothing",
}
# Roles a per-action number may legitimately play while E2 is open.  Anything
# outside DIAGNOSTIC_ROLES asserts a licence that no committed authority grants.
DIAGNOSTIC_ROLES = ("diagnostic", "reconstruction_check", "audit_record")
UNLICENSED_ROLES = (
    "settlement", "wallet", "causal_entitlement", "shapley_allocation",
    "mobius_allocation", "physical_path_claim", "responsibility_share",
)


def allocation_role(role: str) -> str:
    """Normalize and validate a role label for a per-action group quantity."""
    if not isinstance(role, str) or not role.strip():
        raise UnlicensedAllocation("a per-action role label is required")
    return role.strip().lower()


def require_diagnostic_only(role: str, *, group_size: int) -> str:
    """Permit a per-action group quantity ONLY in a diagnostic role.

    The group VALUE is well defined: the registered aggregate form evaluates
    the accepted vector once.  Splitting that value among the actions is what
    no committed authority licenses while O3 / 16.O3 are open, so this guard
    keys on the role, never on the arithmetic.

    ``group_size <= 1`` needs no split, so any role is vacuously diagnostic:
    the registered per-candidate rules apply directly.  The ambiguity begins
    at two, which is exactly where a simultaneous group puts it.
    """
    if not isinstance(group_size, int) or isinstance(group_size, bool) \
            or group_size < 0:
        raise UnlicensedAllocation("group_size must be a non-negative int")
    normalized = allocation_role(role)
    if group_size <= 1:
        return normalized
    if normalized in UNLICENSED_ROLES:
        raise UnlicensedAllocation(
            f"role {normalized!r} on a group of {group_size} actions asserts a "
            f"licence no committed authority grants. Per-action allocation of "
            f"a joint value is open (O3, 16.O3); the telescoping identity is a "
            f"theorem at m = 1 only (Thm 8.2 under T3). Permitted roles: "
            f"{DIAGNOSTIC_ROLES}. See {COORDINATE_DOCUMENT} section 6, E2.")
    if normalized not in DIAGNOSTIC_ROLES:
        raise UnlicensedAllocation(
            f"unrecognized role {normalized!r}; while E2 is open a per-action "
            f"group quantity must declare one of {DIAGNOSTIC_ROLES}")
    return normalized


# ---------------------------------------------------------------------------
# namespace-package trap (coordinate section 2.2)
# ---------------------------------------------------------------------------
def _is_namespace_trap(module_name: str, root: str) -> bool:
    """True when ``module_name`` is a STALE-LINEAGE empty namespace package.

    Four conditions must all hold, and the last two are what make this a trap
    rather than an ordinary directory:

    1. the directory exists and has no ``__init__.py``;
    2. it resolves through the import system with ``loader is None``, which is
       exactly the implicit-namespace-package case, so ``import`` succeeds;
    3. it contains no ``.py`` source anywhere - so the import yields nothing;
    4. it contains at least one ``.pyc``, which is the positive evidence that
       it WAS a real package on another lineage.

    Condition 4 is why an ordinary tracked data directory such as ``results/``
    is not reported: it also imports as a namespace package, but it was never
    a Python package and importing it misleads nobody.

    Read-only: probes the import system and walks the directory, opens nothing.
    """
    directory = os.path.join(root, module_name)
    if not os.path.isdir(directory):
        return False
    if os.path.isfile(os.path.join(directory, "__init__.py")):
        return False
    try:
        spec = importlib.util.find_spec(module_name)
    except (ImportError, ValueError):
        return False
    if spec is None or spec.loader is not None:
        return False
    has_source = False
    has_bytecode = False
    for _, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                has_source = True
            elif filename.endswith(".pyc"):
                has_bytecode = True
        if has_source:
            break
    return has_bytecode and not has_source


def namespace_package_traps(root: str = ".") -> tuple:
    """Directories that would import as empty namespace packages.

    ``import stage_e_harness`` succeeding does NOT mean the Stage E harness is
    present; the directory holds only stale ``.pyc`` files from another
    lineage.  Callers must treat a non-empty result as a refusal condition.
    """
    return tuple(sorted(
        name for name in STALE_BYTECODE_DIRECTORIES
        if _is_namespace_trap(name, root)))


def require_no_namespace_trap(module_name: str, root: str = ".") -> None:
    """Refuse when a module would import as an empty namespace package."""
    if _is_namespace_trap(module_name, root):
        found = AUTHORITIES.get(module_name)
        where = (f" Its source lives on {found.home_branch!r} "
                 f"(commit {found.commit})." if found else "")
        raise NamespacePackageTrap(
            f"{module_name!r} resolves as an EMPTY namespace package: the "
            f"directory exists but carries no source on the active branch "
            f"(stale bytecode only). Importing it would silently succeed and "
            f"yield nothing.{where} "
            f"See {COORDINATE_DOCUMENT} section 2.2.")
