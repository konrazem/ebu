"""Immutable reference-environment and installed-origin checks."""

from __future__ import annotations

import os
import platform
import sqlite3
import sys
from pathlib import Path
from typing import Any

from .canonical import Refusal, sha256_bytes


EXPECTED_ENVIRONMENT = {
    "oci_manifest_digest": "sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab",
    "architecture": "linux/amd64",
    "python_version": "3.14.4-final",
    "python_executable_sha256": "353d0275b5ca0447ebfc6ecae7d80a7a7e7a627d4669fdcc3f836f0b8d804c79",
    "sqlite_version": "3.46.1",
    "sqlite_version_info": [3, 46, 1],
    "sqlite_source_id": "2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69aalt1",
    "debian_sqlite_package": "libsqlite3-0:amd64=3.46.1-7+deb13u1",
    "network": "OFFLINE",
}


def observed_environment(*, debian_identity: str, image_digest: str | None = None) -> dict[str, Any]:
    with sqlite3.connect(":memory:") as db:
        source_id = db.execute("SELECT sqlite_source_id()").fetchone()[0]
    executable = Path(sys.executable).read_bytes()
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}-{'final' if sys.version_info.releaselevel == 'final' else sys.version_info.releaselevel}"
    architecture = "linux/amd64" if sys.platform.startswith("linux") and platform.machine() in {"x86_64", "amd64"} else f"{sys.platform}/{platform.machine()}"
    return {
        "oci_manifest_digest": image_digest or os.environ.get("EBU_STAGE_C_IMAGE_DIGEST", ""),
        "architecture": architecture,
        "python_version": version,
        "python_executable_sha256": sha256_bytes(executable),
        "sqlite_version": sqlite3.sqlite_version,
        "sqlite_version_info": list(sqlite3.sqlite_version_info),
        "sqlite_source_id": source_id,
        "debian_sqlite_package": debian_identity,
        "network": "OFFLINE",
    }


def validate_environment(observed: dict[str, Any]) -> None:
    if observed != EXPECTED_ENVIRONMENT:
        differing = sorted(key for key in EXPECTED_ENVIRONMENT if observed.get(key) != EXPECTED_ENVIRONMENT[key])
        raise Refusal(f"immutable environment mismatch: {differing}")
    if "PYTHONPATH" in os.environ:
        raise Refusal("PYTHONPATH forbidden in isolated harness")


def validate_framework_origin(origin: str, site_packages: str, source_root: str) -> None:
    resolved = Path(origin).resolve()
    site = Path(site_packages).resolve()
    source = Path(source_root).resolve()
    if not resolved.is_relative_to(site):
        raise Refusal("framework import is not under isolated site-packages")
    if resolved.is_relative_to(source):
        raise Refusal("framework imported from source checkout")
