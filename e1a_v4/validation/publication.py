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

THE DEFECT THIS MODULE'S SECOND REVISION CLOSES
    An independent audit demonstrated that the first revision satisfied the bytes
    of the primitive and not its guarantee. Reproduced against the previous HEAD:

        publish the artifact
          -> INJECT a failure in the directory fsync that makes the final path
             durable
          -> publish_atomic raises, the job does NOT advance
          -> the final file nevertheless exists, complete and well-formed
          -> the reader accepts it as published

    So `publish() raised FAILURE` and `the reader treats it as PUBLISHED` were
    simultaneously true. A data file merely appearing at the final pathname was
    being taken as proof of a committed publication.

    The repository's own answer is in the same addendum, section 5: a Gate 1D-C
    result directory is not `FINALIZED` because its scientific artifacts exist. It
    is finalized because a SEPARATE registered artifact -- the manifest -- exists
    and validates against them. Everything else is `RUNNER_COMPLETE`, which is
    explicitly a recoverable, not-finished state, and state is classified by
    inventorying the directory rather than by asking the writer what it did.

    That is the mechanism adopted here, one level down:

        PREPARED EVIDENCE      <dir>/<name>.json          the artifact bytes
        COMMITTED PUBLICATION  <dir>/<name>.commit.json   the commit marker

    The marker carries the artifact's exact byte digest and the publication
    digest, and is itself self-validating. A reader treats an artifact as
    published if and only if its marker exists, validates, and matches the bytes
    actually on disk. An artifact without its marker is ORPHANED -- never
    published, never silently promoted, never silently deleted.

    The invariant is therefore mechanical:

        publish_transaction() returns          iff  a reader may treat the
                                                    artifact as PUBLISHED
        publish_transaction() raises           ==>  no reader will, whatever
                                                    filesystem residue remains

THE DURABILITY POINT
    Inside one artifact's publication there is exactly one instant at which the
    final path becomes durable: the directory fsync immediately after
    `link(temp, final)`. Before it, a failure must leave nothing a reader can
    accept, so the final link is removed. After it, the artifact IS durable and
    only the temporary alias is outstanding; the addendum calls that residue
    recoverable, not failed, so publication succeeds and reports the residue.

SCOPE, STATED HONESTLY
    `AGENTS.md` makes that addendum's PRECEDENCE deliberately narrow: it governs
    Gate 1D-C execution mechanics and nothing else. It is therefore NOT E1a
    scientific authority, and this module does not claim it is. What is borrowed
    is the repository's established operational MEANING of publication, its
    commit/inventory model and its canonical serialisation, so that E1a
    implements the repository's intent rather than inventing a weaker one. The
    Gate 1D-C artifact NAMES and paths are not borrowed; E1a supplies its own.

NO RNG. Serialisation, hashing and filesystem calls only. No model state moves.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from typing import Any

from .refusals import (
    PublicationCollision, PublicationIncomplete, PublicationNotDurable,
    PublicationOrphaned, PublicationUnexpectedEntry,
)
from .strict_json import strict_loads

#: The frozen temporary-name convention: a dot-prefixed sibling of the final
#: name, inside the same directory. Random or alternate names are forbidden.
TEMPORARY_PREFIX = "."
TEMPORARY_SUFFIX = ".tmp"

#: The commit marker's suffix. `x.json` commits as `x.commit.json`.
COMMIT_INFIX = ".commit"
COMMIT_SCHEMA = "e1a_v4_publication_commit/1"
COMMITTED = "COMMITTED"

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


def sealed_digest(record: dict[str, Any], digest_key: str) -> str:
    """The digest a self-validating record carries over everything BUT itself.

    A record that contained its own digest could not be verified by
    recomputation, so the field is removed from the preimage. Every other field
    is inside it, which is what makes a single edited field detectable.
    """
    preimage = {k: v for k, v in record.items() if k != digest_key}
    return canonical_digest(preimage)


# ---------------------------------------------------------- filesystem stages
# Named stages, so a DETERMINISTIC test fixture can fail exactly one of them and
# prove the failure is handled (section 11 of the repair task). They are module
# level functions, never parameters: production code has no argument, flag or
# environment variable that selects a different implementation, so this is an
# audit seam and NOT a bypass.
PUBLICATION_STAGES = (
    "lstat", "open_temp", "write", "fsync_file", "fchmod", "link",
    "fsync_dir_commit", "unlink_alias", "fsync_dir_final",
)


def _stage_lstat(path: str):
    return os.lstat(path)


def _stage_open_temp(path: str, flags: int, mode: int) -> int:
    return os.open(path, flags, mode)


def _stage_write(fd: int, data: bytes) -> int:
    return os.write(fd, data)


def _stage_fsync_file(fd: int) -> None:
    os.fsync(fd)


def _stage_fchmod(fd: int, mode: int) -> None:
    os.fchmod(fd, mode)


def _stage_link(temp: str, final: str) -> None:
    os.link(temp, final)


def _stage_fsync_dir(directory: str) -> None:
    """A final path is not durable until its directory has been fsynced."""
    fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _stage_unlink(path: str) -> None:
    os.unlink(path)


def _remove_or_incident(path: str, why: str) -> None:
    """Remove a path that must not survive, or refuse loudly if it cannot be.

    A non-durable final path is worse than no path at all: it is exactly the
    artifact a later reader would mistake for published evidence. If it cannot be
    removed, that is an INCIDENT requiring recovery, not something to continue
    past.
    """
    try:
        os.unlink(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise PublicationNotDurable(
            f"INCIDENT: {why}, and the residue {path!r} could not be removed "
            f"({exc}). It must not be read as published evidence. Recovery is "
            "manual: this publication is INCOMPLETE and the campaign is blocked "
            "until the residue is inspected and removed."
        ) from exc


def temporary_name(final_basename: str) -> str:
    return f"{TEMPORARY_PREFIX}{final_basename}{TEMPORARY_SUFFIX}"


def commit_name(final_basename: str) -> str:
    """`branch_a_x.json` -> `branch_a_x.commit.json`. Deterministic, no clock."""
    if final_basename.endswith(".json"):
        return f"{final_basename[:-len('.json')]}{COMMIT_INFIX}.json"
    return f"{final_basename}{COMMIT_INFIX}.json"


def is_commit_name(basename: str) -> bool:
    return basename.endswith(f"{COMMIT_INFIX}.json")


def artifact_name_of_commit(commit_basename: str) -> str:
    return f"{commit_basename[:-len(COMMIT_INFIX + '.json')]}.json"


@dataclass(frozen=True)
class PublishedFile:
    """The receipt of ONE durable artifact. Returned only after durability."""

    path: str
    byte_sha256: str
    #: The temporary alias, when the artifact became durable but its alias could
    #: not be unlinked. Recoverable residue, per the addendum; never a failure.
    residual_alias: str | None = None


@dataclass(frozen=True)
class PublicationReceipt:
    """The receipt of one COMMITTED publication: artifact plus its marker."""

    artifact: PublishedFile
    commit: PublishedFile
    commit_record: dict[str, Any]

    @property
    def path(self) -> str:
        return self.artifact.path


def publish_atomic(directory: str, final_basename: str, payload: Any) -> PublishedFile:
    """Durably publish one artifact at `directory/final_basename`. Fails closed.

    On return the file exists, is mode 0444, contains every byte of the canonical
    serialisation, and its directory entry has been fsynced. If it raises, no
    final path this call created survives.

    This publishes ONE FILE. It does not by itself make that file a committed
    publication -- `publish_transaction` does. Callers that need the
    publish/reader invariant must use the transaction.
    """
    os.makedirs(directory, exist_ok=True)
    final = os.path.join(directory, final_basename)
    temp = os.path.join(directory, temporary_name(final_basename))
    for path in (final, temp):
        try:
            _stage_lstat(path)
        except FileNotFoundError:
            continue
        raise PublicationCollision(
            f"refusing to publish {final_basename!r}: {path!r} already exists. "
            "Publication creates an ABSENT final path; it never overwrites, and a "
            "leftover temporary is evidence of an interrupted publication that "
            "must be inspected rather than clobbered."
        )
    data = canonical_bytes(payload)
    byte_digest = hashlib.sha256(data).hexdigest()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = _stage_open_temp(temp, flags, TEMPORARY_MODE)
    try:
        if os.fstat(fd).st_dev != os.stat(directory).st_dev:
            raise PublicationNotDurable(
                f"temporary {temp!r} is not on the same device as its destination "
                "directory; link() could not then be atomic")
        written = 0
        while written < len(data):
            written += _stage_write(fd, data[written:])
        _stage_fsync_file(fd)
        _stage_fchmod(fd, FINAL_MODE)
        _stage_fsync_file(fd)
    except BaseException:
        os.close(fd)
        _remove_or_incident(temp, f"{final_basename!r} could not be written")
        raise
    os.close(fd)
    # Atomically create the ABSENT final path. A collision here fails closed.
    try:
        _stage_link(temp, final)
    except FileExistsError as exc:
        _remove_or_incident(temp, f"{final_basename!r} appeared while publishing")
        raise PublicationCollision(
            f"{final!r} appeared while publishing; refusing to replace published "
            "evidence") from exc
    except BaseException:
        _remove_or_incident(temp, f"{final_basename!r} could not be linked")
        raise
    # ------------------------------- THE DURABILITY POINT -------------------
    # Before this fsync returns, `final` exists but may not survive a crash, so a
    # reader must never see it. Remove it, then the alias, then re-raise.
    try:
        _stage_fsync_dir(directory)
    except BaseException as exc:
        _remove_or_incident(final, f"{final_basename!r} never became durable")
        _remove_or_incident(temp, f"{final_basename!r} never became durable")
        raise PublicationNotDurable(
            f"{final!r} was linked but its directory entry could not be made "
            f"durable ({exc}); the final path has been removed. A file that "
            "exists is not a publication: only a durable one is."
        ) from exc
    # Past the durability point the artifact IS published. The addendum treats a
    # leftover alias as recoverable residue, so a failure here is reported, not
    # raised: raising would claim a publication failed that in fact succeeded.
    residual: str | None = None
    try:
        _stage_unlink(temp)
        _stage_fsync_dir(directory)
    except OSError:
        residual = temporary_name(final_basename)
    return PublishedFile(final, byte_digest, residual)


def publish_transaction(directory: str, final_basename: str, payload: Any, *,
                        publication_digest: str,
                        provenance: dict[str, Any]) -> PublicationReceipt:
    """Publish an artifact AND commit it. The only route to a published record.

    Two durable artifacts, in this order:

        1. the evidence itself                 PREPARED
        2. its commit marker, binding the      COMMITTED
           evidence's exact bytes and digest

    If (2) never happens the evidence is an ORPHAN: `read_transaction` refuses it
    and `inventory_directory` reports it as ORPHANED. It is never promoted and
    never deleted -- deleting it would destroy the only record of what happened.
    """
    artifact = publish_atomic(directory, final_basename, payload)
    record: dict[str, Any] = {
        "schema": COMMIT_SCHEMA,
        "state": COMMITTED,
        "artifact_basename": final_basename,
        "artifact_bytes_sha256": artifact.byte_sha256,
        "publication_digest": publication_digest,
        "provenance": provenance,
        "residual_alias": artifact.residual_alias,
        "not_execution_authorisation": True,
    }
    record["commit_digest"] = sealed_digest(record, "commit_digest")
    commit = publish_atomic(directory, commit_name(final_basename), record)
    return PublicationReceipt(artifact, commit, record)


def read_published(path: str, what: str) -> dict[str, Any]:
    """Strictly parse a published record. Duplicate keys refuse, as everywhere."""
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        raise PublicationIncomplete(f"{what}: no published record at {path!r}") from None
    if not stat.S_ISREG(info.st_mode):
        raise PublicationUnexpectedEntry(
            f"{what}: {path!r} is not a regular file; a symlink, directory or "
            "device is never published evidence")
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


def read_committed(directory: str, final_basename: str,
                   what: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read an artifact ONLY IF its publication was committed. Else refuse.

    Every field of the marker is recomputed rather than trusted: its own digest,
    the artifact's exact bytes, and the basename it claims to commit.
    """
    artifact_path = os.path.join(directory, final_basename)
    commit_path = os.path.join(directory, commit_name(final_basename))
    artifact_exists = os.path.lexists(artifact_path)
    commit_exists = os.path.lexists(commit_path)
    if not artifact_exists and not commit_exists:
        raise PublicationIncomplete(f"{what}: no published record at {artifact_path!r}")
    if artifact_exists and not commit_exists:
        raise PublicationOrphaned(
            f"{what}: {artifact_path!r} exists but its commit marker "
            f"{commit_name(final_basename)!r} does not. The artifact was PREPARED "
            "and never COMMITTED, so it is not published evidence. It is preserved "
            "for inspection, not promoted and not deleted.")
    if commit_exists and not artifact_exists:
        raise PublicationIncomplete(
            f"{what}: the commit marker {commit_path!r} exists but the artifact it "
            f"commits, {final_basename!r}, does not. Inventory claims a publication "
            "whose bytes are missing.")
    marker = read_published(commit_path, f"{what} commit marker")
    if marker.get("schema") != COMMIT_SCHEMA:
        raise PublicationIncomplete(
            f"{what}: commit schema {marker.get('schema')!r} is not {COMMIT_SCHEMA!r}")
    if marker.get("state") != COMMITTED:
        raise PublicationIncomplete(
            f"{what}: commit marker state {marker.get('state')!r} is not "
            f"{COMMITTED!r}")
    if "commit_digest" not in marker:
        raise PublicationIncomplete(f"{what}: the commit marker carries no digest")
    recomputed = sealed_digest(marker, "commit_digest")
    if recomputed != marker["commit_digest"]:
        raise PublicationIncomplete(
            f"{what}: the commit marker hashes to {recomputed}, but declares "
            f"{marker['commit_digest']}. An edited marker is not a commit.")
    if marker.get("artifact_basename") != final_basename:
        raise PublicationIncomplete(
            f"{what}: the commit marker commits {marker.get('artifact_basename')!r}, "
            f"not {final_basename!r}")
    with open(artifact_path, "rb") as handle:
        actual = hashlib.sha256(handle.read()).hexdigest()
    if actual != marker.get("artifact_bytes_sha256"):
        raise PublicationIncomplete(
            f"{what}: {artifact_path!r} hashes to {actual}, but its commit marker "
            f"committed {marker.get('artifact_bytes_sha256')}. The bytes changed "
            "after the publication was committed.")
    return read_published(artifact_path, what), marker


def is_committed(directory: str, final_basename: str) -> bool:
    """True only for a complete, self-consistent committed publication."""
    try:
        read_committed(directory, final_basename, "a publication")
    except (PublicationIncomplete, PublicationOrphaned, PublicationUnexpectedEntry):
        return False
    return True


def is_published(path: str) -> bool:
    """Presence of an artifact FILE. NOT proof of a committed publication.

    Retained because presence and commitment are different questions and the
    difference is the whole point of this module; callers deciding whether a
    reader may treat evidence as published must use `is_committed`.
    """
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except OSError:
        return False


# ------------------------------------------------------------------ inventory
@dataclass(frozen=True)
class DirectoryInventory:
    """What ACTUALLY exists in a publication directory, by independent scan.

    This is the answer to "what has been published?" -- never a caller's list.
    A caller cannot hide an artifact by omitting it from an argument, because no
    argument is consulted.
    """

    directory: str
    committed: tuple[str, ...] = ()
    orphaned: tuple[str, ...] = ()
    dangling: tuple[str, ...] = ()
    #: An artifact whose commit marker exists but no longer matches it: the bytes
    #: changed after the publication was committed, or the marker was edited.
    tampered: tuple[str, ...] = ()
    residues: tuple[str, ...] = ()
    unexpected: tuple[str, ...] = ()

    @property
    def is_empty(self) -> bool:
        return not (self.committed or self.orphaned or self.dangling
                    or self.tampered or self.residues or self.unexpected)

    @property
    def is_clean(self) -> bool:
        """Every entry is a committed publication, or a recoverable alias."""
        return not (self.orphaned or self.dangling or self.tampered
                    or self.unexpected)

    def as_dict(self) -> dict[str, Any]:
        return {"directory": self.directory, "committed": list(self.committed),
                "orphaned": list(self.orphaned), "dangling": list(self.dangling),
                "tampered": list(self.tampered), "residues": list(self.residues),
                "unexpected": list(self.unexpected)}


def inventory_directory(directory: str) -> DirectoryInventory:
    """Classify every entry of a publication directory. Reads only; deletes never.

    Modelled on the addendum's `no_unexpected_entries` and its state machine: an
    entry is a registered artifact, a registered commit marker, an exact
    temporary alias of one of those, or it is UNEXPECTED. Unexpected entries are
    reported rather than ignored, because an unexplained file in a scientific
    result directory is evidence of something that was not supposed to happen.
    """
    if not os.path.isdir(directory):
        return DirectoryInventory(directory)
    artifacts: set[str] = set()
    commits: set[str] = set()
    residues: list[str] = []
    unexpected: list[str] = []
    entries = sorted(os.listdir(directory))
    for name in entries:
        info = os.lstat(os.path.join(directory, name))
        if not stat.S_ISREG(info.st_mode):
            unexpected.append(name)
            continue
        if name.startswith(TEMPORARY_PREFIX) and name.endswith(TEMPORARY_SUFFIX):
            residues.append(name)
            continue
        if not name.endswith(".json"):
            unexpected.append(name)
            continue
        (commits if is_commit_name(name) else artifacts).add(name)
    committed: list[str] = []
    orphaned: list[str] = []
    tampered: list[str] = []
    for name in sorted(artifacts):
        marker = commit_name(name)
        if marker not in commits:
            orphaned.append(name)
        elif is_committed(directory, name):
            committed.append(name)
        else:
            # The marker exists but does not validate against the bytes on disk.
            tampered.append(name)
    dangling = sorted(m for m in commits
                      if artifact_name_of_commit(m) not in artifacts)
    # A temporary alias is recoverable only while the final path it aliases
    # exists; otherwise it is an interrupted write nobody has accounted for.
    accounted, stray = [], []
    for name in residues:
        final = name[len(TEMPORARY_PREFIX):-len(TEMPORARY_SUFFIX)]
        (accounted if final in artifacts or final in commits else stray).append(name)
    return DirectoryInventory(
        directory, tuple(committed), tuple(orphaned), tuple(dangling),
        tuple(tampered), tuple(sorted(accounted)), tuple(sorted(unexpected + stray)))


def require_clean_inventory(directory: str, what: str) -> DirectoryInventory:
    """Refuse a directory carrying orphans, dangling markers or strangers."""
    inventory = inventory_directory(directory)
    if inventory.tampered:
        # Re-read the first one so the refusal states exactly WHAT disagrees,
        # rather than reporting a generic "something is wrong here".
        read_committed(directory, inventory.tampered[0], what)
    if inventory.orphaned:
        raise PublicationOrphaned(
            f"{what}: {len(inventory.orphaned)} artifact(s) were PREPARED and never "
            f"COMMITTED (e.g. {list(inventory.orphaned)[:3]}). An interrupted "
            "publication must be inspected and recovered deliberately; it is never "
            "promoted to PUBLISHED and never silently discarded.")
    if inventory.dangling:
        raise PublicationIncomplete(
            f"{what}: {len(inventory.dangling)} commit marker(s) name artifacts that "
            f"do not exist (e.g. {list(inventory.dangling)[:3]}); the inventory "
            "claims publications whose bytes are missing.")
    if inventory.unexpected:
        raise PublicationUnexpectedEntry(
            f"{what}: {len(inventory.unexpected)} unexplained entr(y/ies) in "
            f"{directory!r} (e.g. {list(inventory.unexpected)[:3]}). A scientific "
            "result directory contains what the protocol put there, or the run is "
            "not reproducible.")
    return inventory
