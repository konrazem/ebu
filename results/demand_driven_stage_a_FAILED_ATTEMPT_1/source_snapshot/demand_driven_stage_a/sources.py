"""Source identity, the execution manifest, and the immutable snapshot.

HEAD alone does not identify this working state: every file this study depends
on is currently UNCOMMITTED or UNTRACKED. The manifest therefore hashes actual
bytes on disk, and the snapshot copies those exact bytes, so the run is
reproducible without a commit -- and no commit is created to fake provenance.
"""

from __future__ import annotations

import hashlib
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Package identity: sorted *.py, each contributing its path relative to the
# package root followed by its bytes. This is the recipe under which the three
# protected identities were recorded, and it is pinned here so the check is
# reproducible rather than remembered.
PROTECTED = {
    "demand_driven_ebu": "f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48",
    "gaussian_harness": "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55",
    "capacity_v2": "8976da3c44a121d1b9c058795a9ee38b05999e2cf674e70134d18222e70221c2",
    "homeostasis": "8b462401a00ed8624fbd649e460b9e44e6adf8ba749ca1fa3872e9a6ddd4c3c6",
}

# Everything the registered run reads or executes.
MANIFEST_PACKAGES = ("demand_driven_ebu", "gaussian_harness", "demand_driven_stage_a")
MANIFEST_DOCUMENTS = (
    "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md",
    "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION_CORRECTION_1.md",
    "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION_CORRECTION_2.md",
    "DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md",
    "DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md",
    "AGENTS.md",
)


def package_files(package: str) -> list[pathlib.Path]:
    base = ROOT / package
    return sorted(
        (p for p in base.rglob("*.py") if "__pycache__" not in str(p)),
        key=lambda p: str(p),
    )


def package_identity(package: str) -> str:
    base = ROOT / package
    h = hashlib.sha256()
    for path in package_files(package):
        h.update(str(path.relative_to(base)).encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def protected_identities() -> dict[str, dict]:
    report = {}
    for package, expected in PROTECTED.items():
        actual = package_identity(package)
        report[package] = {
            "expected": expected,
            "actual": actual,
            "unchanged": actual == expected,
        }
    return report


def file_digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_coordinate() -> dict:
    def run(*args):
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip()

    return {
        "branch": run("git", "branch", "--show-current"),
        "head": run("git", "rev-parse", "HEAD"),
        "tree_is_clean": run("git", "status", "--porcelain") == "",
        "note": (
            "HEAD does NOT identify this working state: every source below is "
            "uncommitted or untracked. The per-file digests are authoritative."
        ),
    }


def source_manifest() -> dict:
    entries = []
    for package in MANIFEST_PACKAGES:
        for path in package_files(package):
            rel = path.relative_to(ROOT)
            entries.append(
                {
                    "path": str(rel),
                    "sha256": file_digest(path),
                    "bytes": path.stat().st_size,
                    "tracked_state": "uncommitted-or-untracked",
                }
            )
    for name in MANIFEST_DOCUMENTS:
        path = ROOT / name
        if path.exists():
            entries.append(
                {
                    "path": name,
                    "sha256": file_digest(path),
                    "bytes": path.stat().st_size,
                    "tracked_state": "uncommitted-or-untracked",
                }
            )
    body = "\n".join(f"{e['sha256']}  {e['path']}" for e in entries)
    return {
        "git": git_coordinate(),
        "protected_packages": protected_identities(),
        "files": entries,
        "file_count": len(entries),
        "manifest_digest": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def write_snapshot(manifest: dict, destination: pathlib.Path) -> int:
    """Copy the exact manifested bytes. Reproduction needs no commit."""
    written = 0
    for entry in manifest["files"]:
        source = ROOT / entry["path"]
        target = destination / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if file_digest(target) != entry["sha256"]:
            raise AssertionError(f"snapshot digest mismatch for {entry['path']}")
        written += 1
    return written
