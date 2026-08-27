#!/usr/bin/env python3
"""Fail-closed Stage C packaging and software-validation orchestrator."""

from __future__ import annotations

import argparse
import ast
import base64
import binascii
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
import zlib


AUTHORITY_HASHES = {
    "FRAMEWORK_ALPHA_PACKAGING_RELEASE_CANDIDATE_AUTHORITY_AMENDMENT.md": "567fa4b8f75cd791856bbc9ce7dcad540d0aeb290e7e14311cfd25c08518e702",
    "framework_alpha_packaging_release_candidate_contract.json": "6ddd601013d86d7e14f77823c48c9c022becaef3c0f158cef05632f44a2a34c3",
    "framework_alpha_packaging_release_candidate_implementation_path_manifest.json": "f24c704f6ce72201b6b8d339183aa7511be540d0d1500f2a38878fd9c29983fe",
    "framework_alpha_packaging_release_candidate_predecessor_manifest.json": "a79c43b9a2f09744438320cdc8ef6a2b536b4ed065854b9ff675138f165c9918",
    "framework_alpha_packaging_release_candidate_validation_contract.json": "58bb97e83231d272a5d09fc92ecefa9d95ef3fa534b54d260964215f752729a0",
}
FRONTEND_WHEELS = {
    "build-1.5.0-py3-none-any.whl": (26018, "13f3eecb844759ab66efec90ca17639bbf14dc06cb2fdf37a9010322d9c50a6f"),
    "packaging-26.3-py3-none-any.whl": (129956, "d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c"),
    "pyproject_hooks-1.2.0-py3-none-any.whl": (10216, "9e5c6bfa8dcc30091c74b0cf803c81fdd29d94f01992a7707bc97babb1141913"),
    "pip-26.2.1-py3-none-any.whl": (1816632, "71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e"),
}
CONVENTIONAL_WHEELS = {
    "charset_normalizer-3.5.1-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl": (251240, "15f024313246a4ed976c60f440bb8d257815513a681d212ff74fd46f7d715a90"),
    "contourpy-1.3.3-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl": (363819, "f64836de09927cba6f79dcd00fdd7d5329f3fccc633468507079c829ca4db4e3"),
    "cycler-0.12.1-py3-none-any.whl": (8321, "85cef7cff222d8644161529808465972e51340599459b8ac3ccbac5a854e0d30"),
    "fonttools-4.63.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl": (4923946, "308f957cdeaf8abe4e5f2f124902ef405448af92c90f80e302a3b771c2e6116b"),
    "kiwisolver-1.5.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.whl": (1475913, "80aa065ffd378ff784822a6d7c3212f2d5f5e9c3589614b5c228b311fd3063ac"),
    "matplotlib-3.11.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl": (11131087, "5af0dcda57d471440a7b5b623e70e0a61003518443d9098f211a96ecfbbc25be"),
    "numpy-2.5.2-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl": (16713701, "318b9a4c845dbea06708a29c84ee429cc3065048db34cdb799047643492050ee"),
    "packaging-26.3-py3-none-any.whl": (129956, "d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c"),
    "pillow-12.3.0-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl": (6936962, "251bf95b67017e27b13d82f5b326234ca62d70f9cf4c2b9032de2358a3b12c7b"),
    "pyparsing-3.3.2-py3-none-any.whl": (122781, "850ba148bd908d7e2411587e247a1e4f0327839c40e2e5e6d05a007ecc69911d"),
    "python_dateutil-2.9.0.post0-py2.py3-none-any.whl": (229892, "a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427"),
    "reportlab-5.0.1-py3-none-any.whl": (1957258, "1c36e6bb0e71780c72331eba60da7f602e8d4389a8723825af71342e49d791e8"),
    "six-1.17.0-py2.py3-none-any.whl": (11050, "4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274"),
}
CONVENTIONAL_COUNTS = {
    "test_energy_balance.py": 8,
    "test_v22.py": 7,
    "test_v23.py": 4,
    "test_v24.py": 5,
    "test_v25.py": 9,
    "test_v26.py": 15,
    "test_math.py": 34,
    "test_v28.py": 132,
    "test_v29.py": 141,
    "test_v29_behavior.py": 108,
    "test_v29_p1c.py": 83,
    "test_v29_d9_d10.py": 114,
    "test_v29_serialization.py": 46,
    "test_v30_quote.py": 184,
    "test_v30_adversary.py": 150,
    "test_v30_service.py": 304,
    "test_v30_gate1dc.py": 456,
}
IMAGE_DIGEST = "sha256:a1f225293efe68c4cb9dddb084b04fa1a21a4d751ad130d0224902e00b1e55ab"
SQLITE_UPSTREAM_SOURCE_ID_REFERENCE = "2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69a1e33"
SQLITE_RUNTIME_SOURCE_ID_REQUIRED = "2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69aalt1"
DEBIAN_SQLITE_PACKAGE_REQUIRED = "libsqlite3-0:amd64=3.46.1-7+deb13u1"
WHEEL_NAME = "ebu_framework-0.1.0a1-cp314-none-any.whl"
SDIST_NAME = "ebu_framework-0.1.0a1.tar.gz"
SDIST_ROOT = "ebu_framework-0.1.0a1"
DIST_INFO = "ebu_framework-0.1.0a1.dist-info"
METADATA = (
    "Metadata-Version: 2.5\n"
    "Name: ebu-framework\n"
    "Version: 0.1.0a1\n"
    "Summary: Pre-alpha typed and reproducible research-framework infrastructure for EBU\n"
    "Requires-Python: >=3.14,<3.15\n"
    "License-Expression: MIT\n"
    "License-File: LICENSE\n"
    "Import-Name: ebu_framework\n"
    "Requires-Dist: PyNaCl==1.6.2\n"
    "\n"
).encode("utf-8")
WHEEL_METADATA = (
    "Wheel-Version: 1.0\n"
    "Generator: ebu-in-tree-pep517-backend/1\n"
    "Root-Is-Purelib: true\n"
    "Tag: cp314-none-any\n"
    "\n"
).encode("utf-8")
COORDINATE_ENV = {
    "EBU_I9_AUTHORITY_BASE": "4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e",
    "EBU_I9_AUTHORITY_CANDIDATE": "15c721cf745d79fabeda749badbac35a7fda9993",
    "EBU_I9_AUTHORITY_TARGET": "2e7848dc495c4b2d5fb2ea09d668f2b240d3ec02",
    "EBU_I9_IMPLEMENTATION_CANDIDATE": "f8623fe5f0d313e16558eb9a4c985940e6baf9dd",
    "EBU_I9_IMPLEMENTATION_TARGET": "ffc910329957f61deaa7e9fc09ba77a0e3f51381",
    "EBU_I9_LATER_DOCUMENTATION_FEATURE": "5674ea9c33b72b94669c86e7e4f1a35c0db5775a",
    "EBU_I9_REQUIRED_CURRENT_TARGET": "fc20d71e69cf226e6cecd9de7575f1d6249b193f",
}
EVIDENCE_CLASS = "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST"


class Refusal(RuntimeError):
    pass


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Refusal(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise Refusal(f"non-finite JSON value: {value}")


def _load_json(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise Refusal(f"JSON text integrity failure: {path}")
    value = json.loads(
        raw,
        object_pairs_hook=_strict_pairs,
        parse_constant=_reject_constant,
        parse_float=lambda value: (_ for _ in ()).throw(Refusal(value)),
    )
    if type(value) is not dict:
        raise Refusal(f"JSON root is not an object: {path}")
    return value


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def _directory(path: Path, *, empty: bool = False) -> Path:
    if not path.is_absolute():
        raise Refusal(f"path must be absolute: {path}")
    resolved = path.resolve(strict=True)
    if not resolved.is_dir() or resolved.is_symlink():
        raise Refusal(f"path must be a real directory: {path}")
    if empty and any(resolved.iterdir()):
        raise Refusal(f"directory must be empty: {path}")
    return resolved


def _new_directory(path: Path) -> Path:
    if not path.is_absolute():
        raise Refusal(f"path must be absolute: {path}")
    path.mkdir(mode=0o755, parents=True, exist_ok=False)
    return path.resolve(strict=True)


def _assert_read_only_source(source: Path) -> None:
    for path in (source, *source.rglob("*")):
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise Refusal(f"source snapshot symlink forbidden: {path}")
        if stat.S_IMODE(info.st_mode) & 0o222:
            raise Refusal(f"source snapshot is writable: {path}")


def _write_new(path: Path, value: object) -> None:
    raw = _canonical(value)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(descriptor, raw)
    finally:
        os.close(descriptor)


def _identity(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"path": str(path), "byte_count": len(raw), "sha256": _sha256(raw)}


def _base_environment(home: Path, python_bin: Path | None = None) -> dict[str, str]:
    executable_dir = str((python_bin or Path(sys.executable)).resolve().parent)
    home.mkdir(mode=0o700, parents=True, exist_ok=True)
    return {
        "HOME": str(home),
        "PATH": executable_dir + ":/usr/local/bin:/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "MPLCONFIGDIR": str(home / "matplotlib"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
        "SOURCE_DATE_EPOCH": "0",
        "TZ": "UTC",
        "XDG_CACHE_HOME": str(home / ".cache"),
    }


def _run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    records: list[dict[str, object]],
    label: str,
    umask: int | None = None,
) -> subprocess.CompletedProcess[str]:
    if not argv or not Path(argv[0]).is_absolute():
        raise Refusal(f"command executable must be absolute: {argv!r}")
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        preexec_fn=(None if umask is None else lambda: os.umask(umask)),
    )
    records.append(
        {
            "label": label,
            "argv": argv,
            "cwd": str(cwd),
            "environment": dict(sorted(env.items())),
            "exit_status": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    )
    if completed.returncode != 0:
        raise Refusal(f"command failed ({label}): {completed.stderr[-2000:]}")
    return completed


def _contracts(source: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    return (
        _load_json(source / "framework_alpha_packaging_release_candidate_contract.json"),
        _load_json(source / "framework_alpha_packaging_release_candidate_implementation_path_manifest.json"),
        _load_json(source / "framework_alpha_packaging_release_candidate_validation_contract.json"),
    )


def _package_paths(contract: dict[str, object]) -> tuple[str, ...]:
    return tuple(contract["package_inventory"]["paths"])  # type: ignore[index]


def _actual_package_paths(source: Path) -> tuple[str, ...]:
    root = source / "src/ebu_framework"
    values: list[str] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise Refusal(f"symlink in package source: {path}")
        if path.is_file():
            values.append(path.relative_to(source).as_posix())
        elif not path.is_dir():
            raise Refusal(f"nonregular package source: {path}")
    return tuple(sorted(values, key=lambda value: value.encode("utf-8")))


def _source_input_manifest(source: Path, package_paths: tuple[str, ...]) -> list[dict[str, object]]:
    paths = ("pyproject.toml", "build_backend/ebu_build_backend.py", "LICENSE", *package_paths)
    return [
        {
            "path": value,
            "byte_count": (source / value).stat().st_size,
            "sha256": _sha256((source / value).read_bytes()),
        }
        for value in paths
    ]


def _static_authority(args: argparse.Namespace) -> int:
    source = _directory(args.source)
    _assert_read_only_source(source)
    evidence = _directory(args.evidence, empty=True)
    contract, manifest, validation = _contracts(source)
    checks = 0
    authority = []
    for path, expected in AUTHORITY_HASHES.items():
        raw = (source / path).read_bytes()
        if _sha256(raw) != expected:
            raise Refusal(f"authority hash mismatch: {path}")
        if path.endswith(".json"):
            _load_json(source / path)
        authority.append({"path": path, "byte_count": len(raw), "sha256": expected})
        checks += 1
    package_paths = _package_paths(contract)
    if _actual_package_paths(source) != package_paths or len(package_paths) != 48:
        raise Refusal("source package inventory mismatch")
    checks += 49
    modified = tuple(row["path"] for row in manifest["modified_paths"])  # type: ignore[index]
    new = tuple(row["path"] for row in manifest["new_paths"])  # type: ignore[index]
    if modified != tuple(contract["implementation_scope"]["modified_paths"]):  # type: ignore[index]
        raise Refusal("modified-path authority mismatch")
    if new != tuple(contract["implementation_scope"]["new_paths"]):  # type: ignore[index]
        raise Refusal("new-path authority mismatch")
    if (len(modified), len(new), len(set(modified) | set(new))) != (14, 3, 17):
        raise Refusal("implementation path cardinality mismatch")
    if any(not (source / path).is_file() for path in (*modified, *new)):
        raise Refusal("authorized implementation path missing")
    checks += 20
    backend_tree = ast.parse((source / "build_backend/ebu_build_backend.py").read_text("utf-8"))
    forbidden_imports = {"subprocess", "socket", "urllib", "requests", "ebu_framework"}
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(backend_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".", 1)[0]
        for node in ast.walk(backend_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    if imports & forbidden_imports:
        raise Refusal(f"backend forbidden reachability: {sorted(imports & forbidden_imports)}")
    checks += len(imports)
    if validation["global_acceptance"]["registered_or_full_horizon_scientific_campaign_count"] != 0:  # type: ignore[index]
        raise Refusal("scientific boundary drift")
    checks += 1
    payload = {
        "command": "static-authority",
        "status": "PASS",
        "evidence_class": EVIDENCE_CLASS,
        "completed_checks": checks,
        "authority_files": authority,
        "package_file_count": len(package_paths),
        "modified_path_count": len(modified),
        "new_path_count": len(new),
        "relations": {"P1": 4, "P2": len(imports), "P12": 1, "SC1": 49, "SC4": 2, "SC15": 14, "SC16": 1},
        "scientific_counts": {
            "registered_or_full_horizon_campaign": 0,
            "new_official_result_artifact": 0,
            "scientific_outcome_interpretation": 0,
            "validator_direct_model_step_trajectory_runner_or_gate_call": 0,
        },
    }
    _write_new(evidence / "static-authority.json", payload)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def _verify_runtime() -> dict[str, object]:
    source_id = sqlite3.connect(":memory:").execute("SELECT sqlite_source_id()").fetchone()[0]
    dpkg_query = Path("/usr/bin/dpkg-query")
    if not dpkg_query.is_file():
        raise Refusal("Debian SQLite package query is unavailable")
    queried = subprocess.run(
        [str(dpkg_query), "-W", "-f=${binary:Package}=${Version}\\n", "libsqlite3-0"],
        check=False,
        capture_output=True,
        text=True,
        env={"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PATH": "/usr/bin:/bin"},
    )
    if queried.returncode != 0 or not queried.stdout.strip():
        raise Refusal(f"Debian SQLite package query failed: {queried.stderr.strip()}")
    debian_sqlite_package = queried.stdout.strip()
    observed = {
        "image_digest": os.environ.get("EBU_STAGE_C_IMAGE_DIGEST"),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "implementation": sys.implementation.name,
        "version": platform.python_version(),
        "version_info": tuple(sys.version_info),
        "cache_tag": sys.implementation.cache_tag,
        "executable": str(Path(sys.executable).resolve()),
        "executable_sha256": _sha256(Path(sys.executable).read_bytes()),
        "sqlite_version": sqlite3.sqlite_version,
        "sqlite_version_info": tuple(sqlite3.sqlite_version_info),
        "sqlite_source_id": source_id,
        "sqlite_upstream_source_id_reference": SQLITE_UPSTREAM_SOURCE_ID_REFERENCE,
        "sqlite_runtime_source_id_required": SQLITE_RUNTIME_SOURCE_ID_REQUIRED,
        "debian_libsqlite3_0": debian_sqlite_package,
        "debian_libsqlite3_0_required": DEBIAN_SQLITE_PACKAGE_REQUIRED,
        "os_release": Path("/etc/os-release").read_text("utf-8") if Path("/etc/os-release").is_file() else None,
    }
    if observed["image_digest"] != IMAGE_DIGEST:
        raise Refusal("immutable runtime image digest missing or different")
    if (observed["platform_system"], observed["platform_machine"]) not in {
        ("Linux", "x86_64"), ("Linux", "amd64")
    }:
        raise Refusal("runtime platform is not linux/amd64")
    if sys.implementation.name != "cpython" or sys.version_info[:5] != (3, 14, 4, "final", 0):
        raise Refusal("runtime is not final CPython 3.14.4")
    if sqlite3.sqlite_version != "3.46.1" or tuple(sqlite3.sqlite_version_info) != (3, 46, 1):
        raise Refusal(
            f"SQLite runtime is not exactly 3.46.1: "
            f"{sqlite3.sqlite_version!r} {tuple(sqlite3.sqlite_version_info)!r}"
        )
    if source_id != SQLITE_RUNTIME_SOURCE_ID_REQUIRED:
        raise Refusal(
            f"SQLite source identity mismatch: observed={source_id!r}; "
            f"required_runtime={SQLITE_RUNTIME_SOURCE_ID_REQUIRED!r}; "
            f"upstream_provenance={SQLITE_UPSTREAM_SOURCE_ID_REFERENCE!r}; "
            f"Debian={debian_sqlite_package!r}"
        )
    if debian_sqlite_package != DEBIAN_SQLITE_PACKAGE_REQUIRED:
        raise Refusal(
            f"Debian SQLite package mismatch: observed={debian_sqlite_package!r}; "
            f"required={DEBIAN_SQLITE_PACKAGE_REQUIRED!r}"
        )
    return observed


def _verify_frontend_wheelhouse(wheelhouse: Path) -> list[dict[str, object]]:
    members = tuple(wheelhouse.iterdir())
    if any(not path.is_file() or path.is_symlink() for path in members):
        raise Refusal("unsafe frontend wheelhouse member")
    actual = {path.name: path for path in members}
    if set(actual) != set(FRONTEND_WHEELS):
        raise Refusal("frontend wheelhouse member set mismatch")
    rows = []
    for name, (size, digest) in FRONTEND_WHEELS.items():
        row = _identity(actual[name])
        if (row["byte_count"], row["sha256"]) != (size, digest):
            raise Refusal(f"frontend wheel identity mismatch: {name}")
        rows.append(row)
    return rows


def _verify_conventional_wheelhouse(wheelhouse: Path) -> list[dict[str, object]]:
    members = tuple(wheelhouse.iterdir())
    if any(not path.is_file() or path.is_symlink() for path in members):
        raise Refusal("unsafe conventional wheelhouse member")
    actual = {path.name: path for path in members}
    if set(actual) != set(CONVENTIONAL_WHEELS):
        raise Refusal("conventional wheelhouse member set mismatch")
    rows = []
    for name, (size, digest) in CONVENTIONAL_WHEELS.items():
        row = _identity(actual[name])
        if (row["byte_count"], row["sha256"]) != (size, digest):
            raise Refusal(f"conventional wheel identity mismatch: {name}")
        rows.append(row)
    return rows


def _verify_dependency_wheelhouse(source: Path, wheelhouse: Path) -> list[dict[str, object]]:
    lock = (source / "requirements-framework.lock").read_text("utf-8")
    accepted_hashes = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", lock))
    expected_prefixes = ("cffi-2.1.1-", "pycparser-3.0-", "pynacl-1.6.2-")
    rows = []
    for path in wheelhouse.iterdir():
        if not path.is_file() or path.is_symlink() or path.suffix != ".whl":
            raise Refusal(f"unsafe dependency wheelhouse member: {path.name}")
        lowered = path.name.lower()
        if not any(lowered.startswith(prefix) for prefix in expected_prefixes):
            raise Refusal(f"unexpected dependency wheel: {path.name}")
        row = _identity(path)
        if row["sha256"] not in accepted_hashes:
            raise Refusal(f"dependency wheel hash is not locked: {path.name}")
        rows.append(row)
    if len(rows) != 3 or not all(any(Path(row["path"]).name.lower().startswith(prefix) for row in rows) for prefix in expected_prefixes):
        raise Refusal("dependency wheelhouse must contain exactly one wheel per locked project")
    return sorted(rows, key=lambda row: Path(row["path"]).name.lower())


def _copy_build_source(source: Path, destination: Path) -> Path:
    destination.mkdir(mode=0o755)
    for relative in ("pyproject.toml", "LICENSE"):
        shutil.copy2(source / relative, destination / relative)
    shutil.copytree(source / "build_backend", destination / "build_backend", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(source / "src", destination / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for path in sorted(destination.rglob("*"), reverse=True):
        path.chmod(0o555 if path.is_dir() else 0o444)
    destination.chmod(0o555)
    return destination


def _install_frontend(work: Path, wheelhouse: Path, records: list[dict[str, object]]) -> Path:
    environment = work / "frontend-env"
    base = _base_environment(work / "home-frontend")
    _run([sys.executable, "-m", "venv", str(environment)], cwd=work, env=base, records=records, label="create-frontend-env")
    python = environment / "bin/python"
    env = _base_environment(work / "home-frontend", python)
    wheels = [str(wheelhouse / name) for name in FRONTEND_WHEELS]
    _run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", *wheels], cwd=work, env=env, records=records, label="install-frontends")
    versions = _run([str(python), "-c", "import build,packaging,pip,pyproject_hooks;print(build.__version__,packaging.__version__,pip.__version__,pyproject_hooks.__version__)"], cwd=work, env=env, records=records, label="frontend-versions")
    if versions.stdout.strip() != "1.5.0 26.3 26.2.1 1.2.0":
        raise Refusal("frontend version mismatch")
    return python


def _build_pair(source: Path, output: Path, python: Path, env: dict[str, str], records: list[dict[str, object]], index: int) -> tuple[Path, Path]:
    output.mkdir(mode=0o755)
    _run([str(python), "-m", "build", "--no-isolation", "--wheel", "--sdist", "--outdir", str(output), str(source)], cwd=output.parent, env=env, records=records, label=f"build-pair-{index}", umask=(0o022 if index % 2 == 0 else 0o077))
    wheel = output / WHEEL_NAME
    sdist = output / SDIST_NAME
    if set(path.name for path in output.iterdir()) != {WHEEL_NAME, SDIST_NAME}:
        raise Refusal("build output member set mismatch")
    return wheel, sdist


def _safe_extract(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(mode=0o755)
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name.rstrip("/"))
            if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
                raise Refusal(f"unsafe archive path: {member.name}")
            if member.issym() or member.islnk():
                raise Refusal(f"archive link forbidden: {member.name}")
            target = destination.joinpath(*pure.parts)
            if member.isdir():
                target.mkdir(mode=0o755, parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise Refusal(f"archive nonregular member: {member.name}")
            target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            if stream is None:
                raise Refusal(f"archive member unreadable: {member.name}")
            descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            try:
                os.write(descriptor, stream.read())
            finally:
                os.close(descriptor)
    return destination / SDIST_ROOT


def _inspect_wheel(path: Path, package_paths: tuple[str, ...], source: Path) -> dict[str, object]:
    expected_package = tuple(sorted((PurePosixPath(value).relative_to("src").as_posix() for value in package_paths), key=lambda value: value.encode("utf-8")))
    expected = expected_package + (f"{DIST_INFO}/METADATA", f"{DIST_INFO}/WHEEL", f"{DIST_INFO}/licenses/LICENSE", f"{DIST_INFO}/RECORD")
    rows = []
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = tuple(info.filename for info in infos)
        if (names, len(names), len(set(names))) != (expected, 52, 52):
            raise Refusal("wheel member inventory mismatch")
        if archive.comment:
            raise Refusal("wheel archive comment forbidden")
        for info in infos:
            pure = PurePosixPath(info.filename)
            if pure.is_absolute() or ".." in pure.parts or info.is_dir():
                raise Refusal(f"unsafe wheel member: {info.filename}")
            raw = archive.read(info)
            if info.date_time != (1980, 1, 1, 0, 0, 0) or info.compress_type != zipfile.ZIP_STORED or info.extra or info.comment or info.flag_bits:
                raise Refusal(f"wheel archive property mismatch: {info.filename}")
            if (
                info.external_attr >> 16 != stat.S_IFREG | 0o644
                or info.CRC != binascii.crc32(raw)
                or info.file_size != len(raw)
                or info.compress_size != len(raw)
            ):
                raise Refusal(f"wheel member mode/CRC mismatch: {info.filename}")
            rows.append({"name": info.filename, "byte_count": len(raw), "sha256": _sha256(raw)})
        if archive.read(f"{DIST_INFO}/METADATA") != METADATA:
            raise Refusal("wheel METADATA mismatch")
        if archive.read(f"{DIST_INFO}/WHEEL") != WHEEL_METADATA:
            raise Refusal("wheel WHEEL metadata mismatch")
        if archive.read(f"{DIST_INFO}/licenses/LICENSE") != (source / "LICENSE").read_bytes():
            raise Refusal("wheel license mismatch")
        record = list(csv.reader(io.StringIO(archive.read(f"{DIST_INFO}/RECORD").decode("utf-8"))))
        if tuple(row[0] for row in record) != names or record[-1] != [f"{DIST_INFO}/RECORD", "", ""]:
            raise Refusal("wheel RECORD order/self-row mismatch")
        for record_row, member_row in zip(record[:-1], rows[:-1], strict=True):
            digest = base64.urlsafe_b64encode(bytes.fromhex(member_row["sha256"])).rstrip(b"=").decode("ascii")
            if record_row != [member_row["name"], f"sha256={digest}", str(member_row["byte_count"])]:
                raise Refusal(f"wheel RECORD identity mismatch: {member_row['name']}")
    return {**_identity(path), "member_count": len(rows), "members": rows}


def _inspect_sdist(path: Path, package_paths: tuple[str, ...], source: Path) -> dict[str, object]:
    raw = path.read_bytes()
    if raw[:10] != bytes.fromhex("1f8b08000000000000ff"):
        raise Refusal("sdist gzip header mismatch")
    decoder = zlib.decompressobj(wbits=-15)
    tar_bytes = decoder.decompress(raw[10:]) + decoder.flush()
    if (
        len(decoder.unused_data) != 8
        or int.from_bytes(decoder.unused_data[:4], "little") != binascii.crc32(tar_bytes)
        or int.from_bytes(decoder.unused_data[4:], "little") != len(tar_bytes) % (1 << 32)
        or len(tar_bytes) % 512
        or tar_bytes[-1024:] != b"\0" * 1024
    ):
        raise Refusal("sdist gzip trailer or tar terminator mismatch")
    expected_files = tuple(sorted((f"{SDIST_ROOT}/pyproject.toml", f"{SDIST_ROOT}/build_backend/ebu_build_backend.py", f"{SDIST_ROOT}/LICENSE", f"{SDIST_ROOT}/PKG-INFO", *(f"{SDIST_ROOT}/{value}" for value in package_paths)), key=lambda value: value.encode("utf-8")))
    expected_directories = tuple(
        sorted(
            {
                parent.as_posix()
                for name in expected_files
                for parent in PurePosixPath(name).parents
                if parent.as_posix() != "."
            },
            key=lambda value: value.encode("utf-8"),
        )
    )
    expected_members = tuple(
        sorted(
            (*expected_files, *expected_directories),
            key=lambda value: value.encode("utf-8"),
        )
    )
    rows = []
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:") as archive:
        members = archive.getmembers()
        files = tuple(member for member in members if member.isfile())
        if (
            tuple(member.name for member in members) != expected_members
            or tuple(member.name for member in files) != expected_files
            or len(files) != 52
        ):
            raise Refusal("sdist member inventory mismatch")
        if len({member.name for member in members}) != len(members):
            raise Refusal("duplicate sdist member")
        for member in members:
            pure = PurePosixPath(member.name.rstrip("/"))
            if pure.is_absolute() or ".." in pure.parts or member.issym() or member.islnk():
                raise Refusal(f"unsafe sdist member: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise Refusal(f"nonregular sdist member: {member.name}")
            if (member.uid, member.gid, member.uname, member.gname, member.mtime) != (0, 0, "", "", 0):
                raise Refusal(f"sdist ownership/time mismatch: {member.name}")
            if member.pax_headers != {"comment": "ebu-sdist-v1"}:
                raise Refusal(f"sdist PAX header mismatch: {member.name}")
            if member.mode != (0o755 if member.isdir() else 0o644):
                raise Refusal(f"sdist mode mismatch: {member.name}")
            if member.isfile():
                stream = archive.extractfile(member)
                if stream is None:
                    raise Refusal(f"unreadable sdist member: {member.name}")
                payload = stream.read()
                payloads[member.name] = payload
                rows.append({"name": member.name, "byte_count": len(payload), "sha256": _sha256(payload)})
    expected_payloads = {
        f"{SDIST_ROOT}/PKG-INFO": METADATA,
        f"{SDIST_ROOT}/LICENSE": (source / "LICENSE").read_bytes(),
        f"{SDIST_ROOT}/pyproject.toml": (source / "pyproject.toml").read_bytes(),
        f"{SDIST_ROOT}/build_backend/ebu_build_backend.py": (source / "build_backend/ebu_build_backend.py").read_bytes(),
        **{f"{SDIST_ROOT}/{value}": (source / value).read_bytes() for value in package_paths},
    }
    if payloads != expected_payloads:
        raise Refusal("sdist payload mismatch")
    return {**_identity(path), "regular_member_count": len(rows), "members": rows}


def _create_install_environment(work: Path, label: str, frontend_wheelhouse: Path, source: Path, dependency_wheelhouse: Path, wheel: Path, records: list[dict[str, object]]) -> Path:
    environment = work / f"{label}-env"
    env = _base_environment(work / f"home-{label}")
    _run([sys.executable, "-m", "venv", str(environment)], cwd=work, env=env, records=records, label=f"create-{label}-env")
    python = environment / "bin/python"
    run_env = _base_environment(work / f"home-{label}", python)
    _run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(frontend_wheelhouse / "pip-26.2.1-py3-none-any.whl")], cwd=work, env=run_env, records=records, label=f"install-{label}-pip")
    _run([str(python), "-m", "pip", "install", "--no-index", "--find-links", str(dependency_wheelhouse), "--require-hashes", "-r", str(source / "requirements-framework.lock")], cwd=work, env=run_env, records=records, label=f"install-{label}-dependencies")
    _run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", "--no-compile", str(wheel)], cwd=work, env=run_env, records=records, label=f"install-{label}-candidate")
    return python


def _packaging(args: argparse.Namespace) -> int:
    source = _directory(args.source)
    _assert_read_only_source(source)
    frontend = _directory(args.wheelhouse)
    work = _directory(args.work, empty=True)
    evidence = _directory(args.evidence)
    dependency = _directory(frontend.parent / "dependency-wheelhouse")
    contract, _, _ = _contracts(source)
    package_paths = _package_paths(contract)
    if _actual_package_paths(source) != package_paths:
        raise Refusal("source package inventory mismatch before build")
    runtime = _verify_runtime()
    frontend_rows = _verify_frontend_wheelhouse(frontend)
    dependency_rows = _verify_dependency_wheelhouse(source, dependency)
    records: list[dict[str, object]] = []
    frontend_python = _install_frontend(work, frontend, records)
    wheel_bytes = []
    sdist_bytes = []
    build_rows = []
    for index in range(3):
        build_source = _copy_build_source(source, work / f"source-{index}")
        manifest_before = _source_input_manifest(build_source, package_paths)
        build_env = _base_environment(work / f"home-build-{index}", frontend_python)
        build_env.update({"PYTHONHASHSEED": str(index + 1), "SOURCE_DATE_EPOCH": str(1_700_000_000 + index), "EBU_STAGE_C_PERTURBATION": str(index)})
        wheel, sdist = _build_pair(build_source, work / f"build-{index}", frontend_python, build_env, records, index)
        if _source_input_manifest(build_source, package_paths) != manifest_before:
            raise Refusal("source input changed during build")
        wheel_bytes.append(wheel.read_bytes())
        sdist_bytes.append(sdist.read_bytes())
        build_rows.append({"index": index, "wheel": _identity(wheel), "sdist": _identity(sdist), "source_manifest": manifest_before})
    if len(set(wheel_bytes)) != 1 or len(set(sdist_bytes)) != 1:
        raise Refusal("perturbed build reproducibility mismatch")
    artifacts = work / "artifacts"
    (artifacts / "direct").mkdir(parents=True)
    (artifacts / "sdist").mkdir()
    direct_wheel = artifacts / "direct" / WHEEL_NAME
    direct_sdist = artifacts / "sdist" / SDIST_NAME
    direct_wheel.write_bytes(wheel_bytes[0])
    direct_sdist.write_bytes(sdist_bytes[0])
    wheel_inspection = _inspect_wheel(direct_wheel, package_paths, source)
    sdist_inspection = _inspect_sdist(direct_sdist, package_paths, source)
    extracted = _safe_extract(direct_sdist, work / "sdist-extracted")
    derived_output = artifacts / "sdist-wheel"
    derived_output.mkdir()
    derived_env = _base_environment(work / "home-derived", frontend_python)
    derived = _build_pair(extracted, work / "derived-pair", frontend_python, derived_env, records, 4)[0]
    derived_target = derived_output / WHEEL_NAME
    derived_target.write_bytes(derived.read_bytes())
    if derived_target.read_bytes() != direct_wheel.read_bytes():
        raise Refusal("direct and sdist-derived wheels differ")
    derived_inspection = _inspect_wheel(derived_target, package_paths, source)
    direct_python = _create_install_environment(work, "direct", frontend, source, dependency, direct_wheel, records)
    sdist_python = _create_install_environment(work, "sdist", frontend, source, dependency, derived_target, records)
    packaging_runner = work / "runner-packaging.py"
    descriptor = os.open(packaging_runner, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(descriptor, RUNNER_SOURCE.encode("utf-8"))
    finally:
        os.close(descriptor)
    packaging_env = _base_environment(work / "home-packaging-tests", direct_python)
    packaging_test = _run(
        [
            str(direct_python),
            "-I",
            str(packaging_runner),
            str(source),
            "source",
            "test_packaging_release_candidate.py",
        ],
        cwd=source,
        env=packaging_env,
        records=records,
        label="packaging-conformance-tests",
    )
    packaging_marker = next(
        (
            line.removeprefix("STAGE_C_TEST_RESULT=")
            for line in packaging_test.stdout.splitlines()
            if line.startswith("STAGE_C_TEST_RESULT=")
        ),
        None,
    )
    if packaging_marker is None:
        raise Refusal("packaging conformance result marker missing")
    packaging_counts = json.loads(packaging_marker)
    if packaging_counts.get("discovered") != 8 or packaging_counts.get("tests_run") != 8 or not packaging_counts.get("success"):
        raise Refusal(f"packaging conformance count/outcome mismatch: {packaging_counts!r}")
    probe_rows = []
    for label, python in (("direct", direct_python), ("sdist", sdist_python)):
        empty_cwd = _new_directory(work / f"probe-cwd-{label}")
        probe_env = _base_environment(work / f"home-probe-{label}", python)
        artifact = direct_wheel if label == "direct" else derived_target
        result = _run(
            [
                str(python),
                "-I",
                str(source / "tests/framework/installed_artifact_probe.py"),
                "--checkout",
                str(source),
                "--forbid-root",
                str(extracted),
                "--artifact-name",
                artifact.name,
                "--artifact-sha256",
                _sha256(artifact.read_bytes()),
            ],
            cwd=empty_cwd,
            env=probe_env,
            records=records,
            label=f"installed-probe-{label}",
        )
        try:
            probe = json.loads(result.stdout.strip().splitlines()[-1])
        except Exception as exc:
            raise Refusal(f"installed probe output invalid: {label}: {exc}") from exc
        if probe.get("completed_checks", 0) <= 0:
            raise Refusal(f"installed probe zero checks: {label}")
        probe_rows.append(probe)
    relations = {f"P{index}": 1 for index in range(1, 13)} | {f"SC{index}": 1 for index in range(1, 15)} | {"SC16": 1}
    relations.update({"P5": 3, "P6": 3, "SC2": 48, "SC3": 11, "SC11": 162, "SC13": len(wheel_inspection["members"]) + len(sdist_inspection["members"])})
    payload = {
        "command": "packaging",
        "status": "PASS",
        "evidence_class": EVIDENCE_CLASS,
        "runtime": runtime,
        "frontend_wheelhouse": frontend_rows,
        "dependency_wheelhouse": dependency_rows,
        "builds": build_rows,
        "wheel": wheel_inspection,
        "sdist": sdist_inspection,
        "sdist_derived_wheel": derived_inspection,
        "direct_equals_sdist_derived": True,
        "installed_probes": probe_rows,
        "packaging_test_counts": packaging_counts,
        "commands": records,
        "relations": relations,
        "scientific_counts": {"registered_or_full_horizon_campaign": 0, "new_official_result_artifact": 0, "scientific_outcome_interpretation": 0, "validator_direct_model_step_trajectory_runner_or_gate_call": 0},
    }
    _write_new(evidence / "packaging.json", payload)
    print(json.dumps({"status": "PASS", "wheel_sha256": wheel_inspection["sha256"], "sdist_sha256": sdist_inspection["sha256"]}, sort_keys=True))
    return 0


RUNNER_SOURCE = r'''import json, pathlib, sys, unittest
source = pathlib.Path(sys.argv[1]).resolve()
artifact = sys.argv[2]
patterns = sys.argv[3:]
test_root = source / "tests/framework"
sys.path.insert(0, str(test_root))
if artifact == "source":
    sys.path.insert(0, str(source / "src"))
loader = unittest.TestLoader()
suite = unittest.TestSuite()
for pattern in patterns:
    suite.addTests(loader.discover(str(test_root), pattern))
import ebu_framework
origin = pathlib.Path(ebu_framework.__file__).resolve()
source_package = (source / "src/ebu_framework").resolve()
if artifact == "source" and not origin.is_relative_to(source_package):
    raise SystemExit("source lane imported a non-source package")
if artifact != "source" and origin.is_relative_to(source):
    raise SystemExit("installed lane imported the checkout package")
discovered = suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
payload = {"discovered": discovered, "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skips": len(result.skipped), "expected_failures": len(result.expectedFailures), "unexpected_successes": len(result.unexpectedSuccesses), "success": result.wasSuccessful()}
print("STAGE_C_TEST_RESULT=" + json.dumps(payload, sort_keys=True, separators=(",", ":")))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == discovered and discovered > 0 and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses else 1)
'''


def _framework(args: argparse.Namespace) -> int:
    source = _directory(args.source)
    _assert_read_only_source(source)
    work = _directory(args.work)
    evidence = _directory(args.evidence)
    _, _, validation = _contracts(source)
    artifact = args.artifact
    tier = args.tier
    if artifact not in {"source", "direct-wheel", "sdist-wheel"} or tier not in {"t0", "t1", "t2"}:
        raise Refusal("invalid framework artifact/tier")
    patterns = [Path(value).name for value in validation["framework_tiers"][tier]["test_files"]]  # type: ignore[index]
    expected = {"t0": 123, "t1": 299, "t2": 21}[tier]
    python = {
        "source": work / "direct-env/bin/python",
        "direct-wheel": work / "direct-env/bin/python",
        "sdist-wheel": work / "sdist-env/bin/python",
    }[artifact]
    if not python.is_file():
        raise Refusal("packaging environments are missing")
    runner = work / f"runner-{artifact}-{tier}.py"
    descriptor = os.open(runner, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(descriptor, RUNNER_SOURCE.encode("utf-8"))
    finally:
        os.close(descriptor)
    records: list[dict[str, object]] = []
    env = _base_environment(work / f"home-framework-{artifact}-{tier}", python)
    env.update(COORDINATE_ENV)
    head = subprocess.run(["/usr/bin/git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    env["EBU_POST_I9_CURRENT_HEAD"] = head
    result = _run([str(python), "-I", str(runner), str(source), artifact, *patterns], cwd=source, env=env, records=records, label=f"framework-{artifact}-{tier}")
    marker = next((line.removeprefix("STAGE_C_TEST_RESULT=") for line in result.stdout.splitlines() if line.startswith("STAGE_C_TEST_RESULT=")), None)
    if marker is None:
        raise Refusal("framework runner result marker missing")
    counts = json.loads(marker)
    if counts != {"discovered": expected, "tests_run": expected, "failures": 0, "errors": 0, "skips": 0, "expected_failures": 0, "unexpected_successes": 0, "success": True}:
        raise Refusal(f"framework count/outcome mismatch: {counts!r}")
    payload = {"command": "framework", "status": "PASS", "evidence_class": EVIDENCE_CLASS, "artifact": artifact, "tier": tier, "test_files": patterns, "counts": counts, "commands": records, "scientific_counts": {"registered_or_full_horizon_campaign": 0, "new_official_result_artifact": 0, "scientific_outcome_interpretation": 0, "validator_direct_model_step_trajectory_runner_or_gate_call": 0}}
    _write_new(evidence / f"framework-{artifact}-{tier}.json", payload)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def _tree_digest(root: Path, prefixes: tuple[str, ...]) -> str:
    rows = []
    for prefix in prefixes:
        base = root / prefix
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and not path.is_symlink():
                raw = path.read_bytes()
                rows.append((path.relative_to(root).as_posix(), len(raw), _sha256(raw)))
    return _sha256(_canonical(sorted(rows)))


def _conventional(args: argparse.Namespace) -> int:
    source = _directory(args.source)
    _assert_read_only_source(source)
    work = _directory(args.work)
    evidence = _directory(args.evidence)
    _, _, validation = _contracts(source)
    if args.historical_o14 != "4939e1f99935185952f3e1c82a6993a4388839f4":
        raise Refusal("historical O14 coordinate mismatch")
    frontend_wheelhouse = _directory(work.parent / "frontend-wheelhouse")
    conventional_wheelhouse = _directory(work.parent / "conventional-wheelhouse")
    frontend_rows = _verify_frontend_wheelhouse(frontend_wheelhouse)
    conventional_rows = _verify_conventional_wheelhouse(conventional_wheelhouse)
    before = _tree_digest(source, ("results", "figures", "books"))
    records: list[dict[str, object]] = []
    environment = work / "conventional-env"
    if environment.exists():
        raise Refusal("preexisting conventional environment is forbidden")
    base_env = _base_environment(work / "home-conventional")
    _run([sys.executable, "-m", "venv", str(environment)], cwd=work, env=base_env, records=records, label="create-conventional-env")
    python = environment / "bin/python"
    env = _base_environment(work / "home-conventional", python)
    _run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(frontend_wheelhouse / "pip-26.2.1-py3-none-any.whl")], cwd=work, env=env, records=records, label="install-conventional-pip")
    _run([str(python), "-m", "pip", "install", "--no-index", "--no-deps", "--no-compile", *(str(conventional_wheelhouse / name) for name in CONVENTIONAL_WHEELS)], cwd=work, env=env, records=records, label="install-conventional-dependencies")
    versions = _run(
        [
            str(python),
            "-c",
            "import importlib.metadata as m,json;print(json.dumps({n:m.version(n) for n in ('numpy','matplotlib','pillow','reportlab')},sort_keys=True,separators=(',',':')))",
        ],
        cwd=work,
        env=env,
        records=records,
        label="conventional-dependency-versions",
    )
    if json.loads(versions.stdout) != {
        "matplotlib": "3.11.1",
        "numpy": "2.5.2",
        "pillow": "12.3.0",
        "reportlab": "5.0.1",
    }:
        raise Refusal("conventional dependency version mismatch")
    current_rows = []
    filenames = tuple(validation["conventional_suites"]["current_head_files"])  # type: ignore[index]
    if filenames != tuple(CONVENTIONAL_COUNTS):
        raise Refusal("conventional file/count authority mismatch")
    for filename in filenames:
        result = _run([str(python), str(source / filename)], cwd=source, env=env, records=records, label=f"conventional-{filename}")
        totals = re.findall(
            r"(?:All|validation checks:|total checks:|Gate 1D-C pre-execution:)\s+(\d+)[^\n]*?\bpassed\b",
            result.stdout,
            flags=re.IGNORECASE,
        )
        if not totals or int(totals[-1]) != CONVENTIONAL_COUNTS.get(filename):
            raise Refusal(f"conventional check count mismatch: {filename}: {totals!r}")
        completed = int(totals[-1])
        current_rows.append({"file": filename, "completed_checks": completed})
    archive_path = work / "historical-o14.tar"
    _run(["/usr/bin/git", "-C", str(source), "archive", "--format=tar", f"--output={archive_path}", args.historical_o14], cwd=source, env=env, records=records, label="historical-o14-archive")
    historical_root = work / "historical-o14"
    historical_root.mkdir()
    with tarfile.open(archive_path, mode="r:") as archive:
        archive.extractall(historical_root, filter="data")
    historical = _run([str(python), str(historical_root / "test_v30_o14.py")], cwd=historical_root, env=env, records=records, label="historical-o14")
    match = re.search(r"total checks:\s*(\d+) passed,\s*(\d+) failed", historical.stdout)
    if match is None or (int(match.group(1)), int(match.group(2))) != (299, 0):
        raise Refusal("historical O14 check count mismatch")
    after = _tree_digest(source, ("results", "figures", "books"))
    if after != before:
        raise Refusal("conventional suite changed official outputs")
    payload = {"command": "conventional", "status": "PASS", "evidence_class": EVIDENCE_CLASS, "current": current_rows, "historical_o14": {"commit": args.historical_o14, "completed_checks": 299}, "frontend_wheelhouse": frontend_rows, "conventional_wheelhouse": conventional_rows, "commands": records, "official_output_digest_before": before, "official_output_digest_after": after, "scientific_counts": {"registered_or_full_horizon_campaign": 0, "new_official_result_artifact": 0, "scientific_outcome_interpretation": 0, "validator_direct_model_step_trajectory_runner_or_gate_call": 0}}
    _write_new(evidence / "conventional.json", payload)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


def _emit_manifest(args: argparse.Namespace) -> int:
    evidence = _directory(args.evidence)
    output = args.output
    if not output.is_absolute() or output.exists() or output.is_symlink():
        raise Refusal("manifest output must be an absolute new path")
    required = ["static-authority.json", "packaging.json", "conventional.json"] + [f"framework-{artifact}-{tier}.json" for artifact in ("source", "direct-wheel", "sdist-wheel") for tier in ("t0", "t1", "t2")]
    if set(path.name for path in evidence.iterdir() if path.is_file()) != set(required):
        raise Refusal("evidence directory is incomplete or contains extras")
    rows = []
    for name in required:
        value = _load_json(evidence / name)
        if value.get("status") != "PASS":
            raise Refusal(f"non-pass evidence: {name}")
        rows.append({"name": name, "identity": _identity(evidence / name), "evidence": value})
    manifest = {"schema_version": "1.0.0", "stage": "C", "status": "ALPHA_RELEASE_CANDIDATE_VALIDATION_PASS", "evidence_class": EVIDENCE_CLASS, "evidence": rows, "scientific_counts": {"registered_or_full_horizon_campaign": 0, "new_official_result_artifact": 0, "scientific_outcome_interpretation": 0, "validator_direct_model_step_trajectory_runner_or_gate_call": 0}, "release_actions": {"main_merge": 0, "tag": 0, "upload": 0, "publication": 0}}
    _write_new(output, manifest)
    print(json.dumps({"status": manifest["status"], "output": str(output), "sha256": _sha256(output.read_bytes())}, sort_keys=True))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    static = subparsers.add_parser("static-authority")
    static.add_argument("--source", type=Path, required=True)
    static.add_argument("--evidence", type=Path, required=True)
    packaging = subparsers.add_parser("packaging")
    packaging.add_argument("--source", type=Path, required=True)
    packaging.add_argument("--wheelhouse", type=Path, required=True)
    packaging.add_argument("--work", type=Path, required=True)
    packaging.add_argument("--evidence", type=Path, required=True)
    framework = subparsers.add_parser("framework")
    framework.add_argument("--source", type=Path, required=True)
    framework.add_argument("--artifact", required=True)
    framework.add_argument("--tier", required=True)
    framework.add_argument("--work", type=Path, required=True)
    framework.add_argument("--evidence", type=Path, required=True)
    conventional = subparsers.add_parser("conventional")
    conventional.add_argument("--source", type=Path, required=True)
    conventional.add_argument("--historical-o14", required=True)
    conventional.add_argument("--work", type=Path, required=True)
    conventional.add_argument("--evidence", type=Path, required=True)
    emit = subparsers.add_parser("emit-manifest")
    emit.add_argument("--evidence", type=Path, required=True)
    emit.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    return {"static-authority": _static_authority, "packaging": _packaging, "framework": _framework, "conventional": _conventional, "emit-manifest": _emit_manifest}[args.command](args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Refusal as exc:
        print(f"STAGE_C_REFUSAL: {exc}", file=sys.stderr)
        raise SystemExit(1)
