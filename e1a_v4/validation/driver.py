"""The CANONICAL official campaign-driver declaration. Identity-bound.

THE DEFECT THIS CLOSES
    The driver path used to live in the execution SEAL, and the presence check was
    `os.path.exists(seal.driver_module)`. A seal could therefore nominate any
    existing file as "the driver". Reproduced against this package at the previous
    HEAD: with a correctly FROZEN seal naming `e1a_v4/validation/plan.py`, the
    complete execution gate PASSED while no campaign driver existed anywhere.

    The seal asserts the expected execution identity. It must not also get to
    define WHICH FILE the package is about to execute -- that is the one thing it
    could use to make a nonexistent driver look present.

WHERE THE DECLARATION LIVES, AND WHY HERE
    In this module, which is one of the VALIDATION_MODULES hashed into the
    execution identity. So changing the declared module or path changes the
    pre-driver execution identity, and no seal can override it: a seal that
    disagrees is refused, and a seal written against a different declaration no
    longer matches the identity it asserts.

WHAT IS DECLARED, PROSPECTIVELY
    The path is chosen now and frozen; the file does NOT exist and is NOT created
    here. Declaring a name is not implementing a driver, and it is not an
    execution authorisation.

THE DRIVER'S FILE HASH IS PART OF THE EXECUTION IDENTITY
    `driver_identity_component` returns the sentinel "ABSENT" while the file does
    not exist, and the file's sha256 once it does. It is included in the
    execution-identity preimage either way, so the identity moves the moment a
    real driver appears -- which is exactly why today's identity is a PRE-DRIVER
    diagnostic and not a seal.

THE INTERFACE CHECK DOES NOT IMPORT THE DRIVER
    Importing would execute driver code, which this stage forbids. The entry point
    is checked by parsing the module's AST, which executes nothing.

CLASSIFICATION
    declaration, presence and interface checks ... EXACT (deterministic)

NO RNG. Nothing in this module draws or advances any model state.
"""

from __future__ import annotations

import ast
import os

from ..contract import sha256_file
from .refusals import DriverAbsent, DriverIdentityMismatch

#: THE canonical declaration. Frozen prospectively; the file does not exist yet.
OFFICIAL_CAMPAIGN_DRIVER_MODULE = "e1a_v4.validation.campaign_driver"
OFFICIAL_CAMPAIGN_DRIVER_PATH = "e1a_v4/validation/campaign_driver.py"

#: The minimal machine-checkable interface the future driver must expose.
OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT = "run_campaign"

#: Sentinel recorded in the execution-identity preimage while the driver is absent.
DRIVER_ABSENT_SENTINEL = "ABSENT"

#: Lifecycle states of the driver itself, independent of the seal.
DRIVER_ABSENT_STATE = "ABSENT"
DRIVER_PRESENT_STATE = "PRESENT"


def driver_path(root: str = ".") -> str:
    return os.path.join(root, OFFICIAL_CAMPAIGN_DRIVER_PATH)


def driver_exists(root: str = ".") -> bool:
    """Presence of THE canonical driver. Never 'whatever path the seal names'."""
    return os.path.isfile(driver_path(root))


def driver_state(root: str = ".") -> str:
    return DRIVER_PRESENT_STATE if driver_exists(root) else DRIVER_ABSENT_STATE


def driver_identity_component(root: str = ".") -> str:
    """The driver's contribution to the execution-identity preimage.

    `DRIVER_ABSENT_SENTINEL` while absent, the file's sha256 once present. Always
    present in the preimage, so the identity is defined at every lifecycle stage
    and moves the moment a real driver appears.
    """
    if not driver_exists(root):
        return DRIVER_ABSENT_SENTINEL
    return sha256_file(driver_path(root))


def declared_entry_points(root: str = ".") -> tuple[str, ...]:
    """Top-level function and class names defined by the driver module.

    Parsed from the AST. NOTHING IS IMPORTED and nothing is executed.
    """
    if not driver_exists(root):
        return ()
    with open(driver_path(root), encoding="utf-8") as handle:
        source = handle.read()
    try:
        tree = ast.parse(source, filename=OFFICIAL_CAMPAIGN_DRIVER_PATH)
    except SyntaxError as exc:
        raise DriverIdentityMismatch(
            f"the official campaign driver {OFFICIAL_CAMPAIGN_DRIVER_PATH} does not "
            f"parse: {exc}"
        ) from exc
    return tuple(node.name for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))


def require_canonical_driver(root: str = ".") -> None:
    """The driver precondition of the execution gate. Refuses BEFORE any RNG.

    Binds to the CANONICAL declaration, never to a seal-supplied path.
    """
    if not driver_exists(root):
        raise DriverAbsent(
            f"the official campaign driver {OFFICIAL_CAMPAIGN_DRIVER_PATH} is ABSENT. "
            "The path is the canonical identity-bound declaration in "
            "e1a_v4/validation/driver.py; no execution seal may nominate another "
            "file in its place. A passing static preflight is not an execution "
            "clearance."
        )
    entries = declared_entry_points(root)
    if OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT not in entries:
        raise DriverIdentityMismatch(
            f"the official campaign driver exists but declares no "
            f"{OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT!r} entry point; found {entries}"
        )


def require_seal_driver_metadata(declared: object) -> None:
    """A seal MAY report driver metadata, but it is never authoritative.

    Any value that disagrees with the canonical declaration is refused, so seal
    metadata can only ever restate the declaration -- never redefine it.
    """
    if declared is None:
        return
    if declared not in (OFFICIAL_CAMPAIGN_DRIVER_PATH, OFFICIAL_CAMPAIGN_DRIVER_MODULE):
        raise DriverIdentityMismatch(
            f"the execution seal names {declared!r} as the official campaign driver, "
            f"but the canonical identity-bound declaration is "
            f"{OFFICIAL_CAMPAIGN_DRIVER_PATH!r}. The seal may restate the "
            "declaration; it may not redefine which file counts as the driver."
        )
