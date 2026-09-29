"""Durable publication: what "published" MEANS in this repository.

WHY THIS MODULE EXISTS
    The frozen authority states the rule three times, identically:

        docs/theory/EBU_THEORY_BASELINE.md line 459
        docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md line 60
        docs/e1a/e1a_v4_design_contract.json  information_separation.unblinding

            "Branch-A output is hashed and published BEFORE Branch B is
             unblinded."

    None of the three defines "published" operationally. That would be an
    ambiguity worth stopping over if the repository had no answer -- but it does.
    `V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md` section 2, "Strict
    serialization and publication primitives", specifies the repository's
    publication primitive exactly:

        "Each temporary is opened at that exact name with O_WRONLY|O_CREAT|O_EXCL
         and O_NOFOLLOW where available, mode 0600, only after lstat proves
         absence. Random or alternate names are forbidden. Its st_dev must equal
         the result directory's st_dev.

         Publication writes every byte, flushes, fsyncs the file, changes the mode
         to 0444, fsyncs again, closes, and atomically creates the absent final
         path by link(temp, final). Collision fails closed. The destination
         directory is fsynced before the final path counts as durable. The
         temporary alias is then unlinked and the directory is fsynced again. No
         alternate publication primitive is permitted."

    and the canonical serialisation:

        "Canonical hashing and nested canonical evidence use sorted-key compact
         JSON, ensure_ascii=True, allow_nan=False, UTF-8, and no final newline."
        "Every text artifact is UTF-8 without BOM, contains LF rather than CR or
         CRLF, contains no NUL, and ends in exactly one LF."

SCOPE, STATED HONESTLY
    `AGENTS.md` makes that addendum's PRECEDENCE deliberately narrow: it governs
    Gate 1D-C execution mechanics and nothing else. It is therefore NOT E1a
    scientific authority, and this module does not claim it is. What is borrowed
    is the repository's established operational MEANING of publication and its
    canonical serialisation, so that E1a implements the repository's intent rather
    than inventing a weaker one. The Gate 1D-C artifact NAMES and paths are not
    borrowed; E1a supplies its own.

    Concretely, "published" here means: an immutable, world-readable file at a
    final path, created atomically from a fully-written and fsynced temporary, in
    a directory that has itself been fsynced. A partial write can never occupy the
    final path, and a second publication at the same path fails closed.

NO RNG. Serialisation, hashing and filesystem calls only. No model state moves.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from .refusals import (
    PublicationCollision, PublicationIncomplete, PublicationNotDurable,
)
from .strict_json import strict_loads

#: The frozen temporary-name convention: a dot-prefixed sibling of the final
#: name, inside the same directory. Random or alternate names are forbidden.
TEMPORARY_PREFIX = "."
TEMPORARY_SUFFIX = ".tmp"

FINAL_MODE = 0o444
TEMPORARY_MODE = 0o600


def canonical_json(value: Any) -> str:
    """Sorted-key compact JSON, ensure_ascii, no NaN, no final newline.

    This is the repository's canonical-hashing form and is what every evidence
    digest in this package is taken over. `sort_keys` is what makes the digest
    independent of dictionary insertion order, so a hash cannot depend on which
    branch of the code happened to populate a mapping first.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def canonical_digest(value: Any) -> str:
    """sha256 over the canonical form. Deterministic across processes and hosts."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    """The published file's exact bytes: canonical JSON plus exactly one LF."""
    return canonical_json(value).encode("utf-8") + b"\n"


def _fsync_directory(directory: str) -> None:
    """A final path is not durable until its directory has been fsynced."""
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def temporary_name(final_basename: str) -> str:
    return f"{TEMPORARY_PREFIX}{final_basename}{TEMPORARY_SUFFIX}"


def publish_atomic(directory: str, final_basename: str, payload: Any) -> str:
    """Durably publish `payload` at `directory/final_basename`. Fails closed.

    Returns the final path. After it returns, the file exists, is mode 0444, and
    contains every byte of the canonical serialisation. If it raises, no final
    path was created by this call.
    """
    os.makedirs(directory, exist_ok=True)
    final = os.path.join(directory, final_basename)
    temp = os.path.join(directory, temporary_name(final_basename))
    for path in (final, temp):
        try:
            os.lstat(path)
        except FileNotFoundError:
            continue
        raise PublicationCollision(
            f"refusing to publish {final_basename!r}: {path!r} already exists. "
            "Publication creates an ABSENT final path; it never overwrites, and a "
            "leftover temporary is evidence of an interrupted publication that "
            "must be inspected rather than clobbered."
        )
    data = canonical_bytes(payload)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(temp, flags, TEMPORARY_MODE)
    try:
        if os.fstat(fd).st_dev != os.stat(directory).st_dev:
            raise PublicationNotDurable(
                f"temporary {temp!r} is not on the same device as its destination "
                "directory; link() could not then be atomic")
        written = 0
        while written < len(data):
            written += os.write(fd, data[written:])
        os.fsync(fd)
        os.fchmod(fd, FINAL_MODE)
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        os.unlink(temp)
        raise
    os.close(fd)
    # Atomically create the ABSENT final path. A collision here fails closed.
    try:
        os.link(temp, final)
    except FileExistsError as exc:
        os.unlink(temp)
        raise PublicationCollision(
            f"{final!r} appeared while publishing; refusing to replace published "
            "evidence") from exc
    _fsync_directory(directory)
    # Only now, with the final link durable, may the temporary alias go.
    os.unlink(temp)
    _fsync_directory(directory)
    return final


def read_published(path: str, what: str) -> dict[str, Any]:
    """Strictly parse a published record. Duplicate keys refuse, as everywhere."""
    if not os.path.isfile(path):
        raise PublicationIncomplete(f"{what}: no published record at {path!r}")
    with open(path, "rb") as handle:
        raw = handle.read()
    if not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        raise PublicationIncomplete(
            f"{what}: {path!r} is not a complete published record; a published "
            "artifact is canonical JSON followed by exactly one LF, so a truncated "
            "or appended file is refused rather than parsed")
    if b"\x00" in raw:
        raise PublicationIncomplete(f"{what}: {path!r} contains a NUL byte")
    record = strict_loads(raw.decode("utf-8"), what)
    if not isinstance(record, dict):
        raise PublicationIncomplete(f"{what}: {path!r} is not a JSON object")
    return record


def is_published(path: str) -> bool:
    return os.path.isfile(path)
