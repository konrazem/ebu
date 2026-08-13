"""The sole EBU I-1 in-tree PEP 517 backend.

Contract identity: ebu-in-tree-pep517-backend/1.
This module is intentionally project-specific and standard-library-only.
"""

from __future__ import annotations

import base64
import binascii
from collections.abc import Mapping
import csv
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import struct
import sys
import tarfile
import tomllib
import zipfile


_BACKEND_IDENTITY = "ebu-in-tree-pep517-backend/1"
_DIST_INFO = "ebu_framework-0.1.0a1.dist-info"
_WHEEL_FILENAME = "ebu_framework-0.1.0a1-cp314-none-any.whl"
_SDIST_FILENAME = "ebu_framework-0.1.0a1.tar.gz"
_SDIST_ROOT = "ebu_framework-0.1.0a1"

_METADATA = (
    "Metadata-Version: 2.5\n"
    "Name: ebu-framework\n"
    "Version: 0.1.0a1\n"
    "Summary: Pre-alpha typed and reproducible research-framework infrastructure for EBU\n"
    "Requires-Python: >=3.14,<3.15\n"
    "License-Expression: MIT\n"
    "License-File: LICENSE\n"
    "Import-Name: ebu_framework\n"
    "\n"
).encode("utf-8")

_WHEEL = (
    "Wheel-Version: 1.0\n"
    "Generator: ebu-in-tree-pep517-backend/1\n"
    "Root-Is-Purelib: true\n"
    "Tag: cp314-none-any\n"
    "\n"
).encode("utf-8")

_I1_REQUIRED_PACKAGE_FILES = frozenset(
    {
        "src/ebu_framework/__init__.py",
        "src/ebu_framework/py.typed",
        "src/ebu_framework/data/__init__.py",
        "src/ebu_framework/data/core_registry_v1.json",
        "src/ebu_framework/data/unicode/15.0.0/UnicodeData.txt",
        "src/ebu_framework/data/unicode/15.0.0/DerivedNormalizationProps.txt",
        "src/ebu_framework/errors.py",
        "src/ebu_framework/canonical.py",
        "src/ebu_framework/identity.py",
        "src/ebu_framework/hashing.py",
        "src/ebu_framework/registry.py",
    }
)

_PLANNED_PACKAGE_FILES = frozenset(
    _I1_REQUIRED_PACKAGE_FILES
    | {
        "src/ebu_framework/actions.py",
        "src/ebu_framework/artifacts.py",
        "src/ebu_framework/authorization.py",
        "src/ebu_framework/authorization_use.py",
        "src/ebu_framework/bridge.py",
        "src/ebu_framework/capabilities.py",
        "src/ebu_framework/causal.py",
        "src/ebu_framework/commitments.py",
        "src/ebu_framework/distortion.py",
        "src/ebu_framework/durability.py",
        "src/ebu_framework/dynamic.py",
        "src/ebu_framework/envelopes.py",
        "src/ebu_framework/events.py",
        "src/ebu_framework/execution.py",
        "src/ebu_framework/experiment.py",
        "src/ebu_framework/faults.py",
        "src/ebu_framework/ledger.py",
        "src/ebu_framework/network.py",
        "src/ebu_framework/numeric.py",
        "src/ebu_framework/observation.py",
        "src/ebu_framework/ownership.py",
        "src/ebu_framework/policy.py",
        "src/ebu_framework/primitives.py",
        "src/ebu_framework/provenance.py",
        "src/ebu_framework/publication.py",
        "src/ebu_framework/recovery.py",
        "src/ebu_framework/scheduling.py",
        "src/ebu_framework/settlement.py",
        "src/ebu_framework/state.py",
        "src/ebu_framework/traces.py",
        "src/ebu_framework/trust.py",
        "src/ebu_framework/validation.py",
    }
)


class BackendRefusal(RuntimeError):
    """A fail-closed packaging-contract refusal."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        super().__init__(f"{code}: {detail}")


def _refuse(code: str, detail: str) -> "NoReturn":
    raise BackendRefusal(code, detail)


def _validate_interpreter() -> None:
    version = sys.version_info
    if (
        sys.implementation.name != "cpython"
        or version.major != 3
        or version.minor != 14
        or version.releaselevel != "final"
    ):
        _refuse(
            "UNSUPPORTED_BUILD_INTERPRETER",
            "final CPython >=3.14.0,<3.15.0 is required",
        )


def _validate_config_settings(config_settings: object) -> None:
    if config_settings is None:
        return
    if type(config_settings) is dict and not config_settings:
        return
    _refuse(
        "UNSUPPORTED_CONFIG_SETTINGS",
        "only None or an empty exact mapping is supported",
    )


def _backend_and_source_root() -> tuple[Path, Path]:
    backend_lexical = Path(__file__).absolute()
    build_backend_lexical = backend_lexical.parent
    source_root_lexical = build_backend_lexical.parent
    if (
        build_backend_lexical.name != "build_backend"
        or backend_lexical.name != "ebu_build_backend.py"
    ):
        _refuse("BACKEND_PATH_ESCAPE", "unexpected lexical backend path")
    try:
        build_backend_lstat = build_backend_lexical.lstat()
        backend_lstat = backend_lexical.lstat()
    except OSError as exc:
        _refuse("BACKEND_PATH_ESCAPE", f"backend path cannot be inspected: {exc}")
    if not stat.S_ISDIR(build_backend_lstat.st_mode) or stat.S_ISLNK(
        build_backend_lstat.st_mode
    ):
        _refuse("BACKEND_PATH_ESCAPE", "build_backend must be a real directory")
    if not stat.S_ISREG(backend_lstat.st_mode) or stat.S_ISLNK(
        backend_lstat.st_mode
    ):
        _refuse("BACKEND_PATH_ESCAPE", "backend source must be a real regular file")
    try:
        source_root_real = source_root_lexical.resolve(strict=True)
        build_backend_real = build_backend_lexical.resolve(strict=True)
        backend_real = backend_lexical.resolve(strict=True)
    except OSError as exc:
        _refuse("BACKEND_PATH_ESCAPE", f"backend path cannot be resolved: {exc}")
    if (
        build_backend_real.parent != source_root_real
        or backend_real.parent != build_backend_real
    ):
        _refuse("BACKEND_PATH_ESCAPE", "backend escapes the lexical source root")
    spec = globals().get("__spec__")
    origin = getattr(spec, "origin", None)
    try:
        origin_real = None if origin is None else Path(origin).resolve(strict=True)
    except OSError as exc:
        _refuse("BACKEND_ORIGIN_MISMATCH", f"module origin cannot be resolved: {exc}")
    if origin_real != backend_real:
        _refuse("BACKEND_ORIGIN_MISMATCH", "module origin is not backend source")
    return backend_real, source_root_real


def _safe_relative_path(path: str) -> None:
    try:
        path.encode("ascii", "strict")
    except UnicodeEncodeError:
        _refuse("UNSAFE_SOURCE_PATH", f"non-ASCII path: {path!r}")
    if "\\" in path or any(ord(character) < 0x20 for character in path):
        _refuse("UNSAFE_SOURCE_PATH", f"unsafe path characters: {path!r}")
    pure = PurePosixPath(path)
    if pure.is_absolute() or not pure.parts or any(
        part in ("", ".", "..") for part in pure.parts
    ):
        _refuse("UNSAFE_SOURCE_PATH", f"unsafe relative path: {path!r}")


def _discover_package_files(source_root: Path) -> tuple[str, ...]:
    package_root = source_root / "src" / "ebu_framework"
    try:
        package_lstat = package_root.lstat()
    except OSError as exc:
        _refuse("PACKAGE_DATA_MISSING", f"package root is missing: {exc}")
    if not stat.S_ISDIR(package_lstat.st_mode) or package_root.is_symlink():
        _refuse("UNSAFE_SOURCE_PATH", "package root must be a regular directory")

    discovered: list[str] = []
    seen_casefold: dict[str, str] = {}
    for current_text, directory_names, file_names in os.walk(
        package_root, topdown=True, followlinks=False
    ):
        current = Path(current_text)
        directory_names.sort(key=lambda item: item.encode("utf-8"))
        file_names.sort(key=lambda item: item.encode("utf-8"))
        for directory_name in directory_names:
            directory_path = current / directory_name
            directory_stat = directory_path.lstat()
            if not stat.S_ISDIR(directory_stat.st_mode) or directory_path.is_symlink():
                _refuse("UNSAFE_SOURCE_PATH", f"unsafe directory: {directory_path}")
        for file_name in file_names:
            file_path = current / file_name
            relative = file_path.relative_to(source_root).as_posix()
            _safe_relative_path(relative)
            file_stat = file_path.lstat()
            if not stat.S_ISREG(file_stat.st_mode) or file_path.is_symlink():
                _refuse("UNSAFE_SOURCE_PATH", f"nonregular source: {relative}")
            if relative not in _PLANNED_PACKAGE_FILES:
                _refuse("PACKAGE_FILE_SET_MISMATCH", f"unknown package file: {relative}")
            folded = relative.casefold()
            prior = seen_casefold.get(folded)
            if prior is not None and prior != relative:
                _refuse(
                    "UNSAFE_SOURCE_PATH",
                    f"case-fold-colliding paths: {prior!r}, {relative!r}",
                )
            seen_casefold[folded] = relative
            discovered.append(relative)
    result = tuple(sorted(discovered, key=lambda item: item.encode("utf-8")))
    missing = _I1_REQUIRED_PACKAGE_FILES.difference(result)
    if missing:
        _refuse(
            "PACKAGE_DATA_MISSING",
            "missing I-1 package files: " + ", ".join(sorted(missing)),
        )
    return result


def _stat_identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
    )


def _read_stable_regular(source_root: Path, relative: str) -> bytes:
    _safe_relative_path(relative)
    path = source_root.joinpath(*PurePosixPath(relative).parts)
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or path.is_symlink():
            _refuse("UNSAFE_SOURCE_PATH", f"selected input is not regular: {relative}")
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            after_open = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        first_bytes = b"".join(chunks)
        after = path.lstat()
        if not (
            _stat_identity(before)
            == _stat_identity(opened)
            == _stat_identity(after_open)
            == _stat_identity(after)
        ) or len(first_bytes) != before.st_size:
            _refuse("SOURCE_CHANGED_DURING_BUILD", f"identity changed: {relative}")
        second_bytes = path.read_bytes()
        final = path.lstat()
        if _stat_identity(after) != _stat_identity(final) or second_bytes != first_bytes:
            _refuse("SOURCE_CHANGED_DURING_BUILD", f"content changed: {relative}")
        return first_bytes
    except BackendRefusal:
        raise
    except OSError as exc:
        _refuse("UNSAFE_SOURCE_PATH", f"cannot snapshot {relative}: {exc}")


def _validate_pyproject(data: bytes) -> None:
    try:
        parsed = tomllib.loads(data.decode("utf-8", "strict"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        _refuse("DYNAMIC_METADATA_FORBIDDEN", f"invalid pyproject.toml: {exc}")
    if set(parsed) != {"build-system", "project"}:
        _refuse("DYNAMIC_METADATA_FORBIDDEN", "unexpected pyproject table")
    build_system = parsed["build-system"]
    expected_build_system = {
        "requires": [],
        "build-backend": "ebu_build_backend",
        "backend-path": ["build_backend"],
    }
    if build_system != expected_build_system:
        _refuse("UNDECLARED_BUILD_DEPENDENCY", "build-system contract mismatch")
    project = parsed["project"]
    expected_project = {
        "name": "ebu-framework",
        "version": "0.1.0a1",
        "description": "Pre-alpha typed and reproducible research-framework infrastructure for EBU",
        "requires-python": ">=3.14,<3.15",
        "dependencies": [],
        "dynamic": [],
        "license": "MIT",
        "license-files": ["LICENSE"],
        "import-names": ["ebu_framework"],
    }
    if project != expected_project:
        _refuse("DYNAMIC_METADATA_FORBIDDEN", "project metadata contract mismatch")


def _source_snapshot() -> tuple[Path, dict[str, bytes], tuple[str, ...]]:
    backend, source_root = _backend_and_source_root()
    package_files_before = _discover_package_files(source_root)
    selected = (
        "pyproject.toml",
        "build_backend/ebu_build_backend.py",
        "LICENSE",
        *package_files_before,
    )
    if backend != (source_root / "build_backend" / "ebu_build_backend.py").resolve(
        strict=True
    ):
        _refuse("BACKEND_ORIGIN_MISMATCH", "backend is not source-root member")
    snapshot = {relative: _read_stable_regular(source_root, relative) for relative in selected}
    package_files_after = _discover_package_files(source_root)
    if package_files_after != package_files_before:
        _refuse("SOURCE_CHANGED_DURING_BUILD", "selected package file set changed")
    _validate_pyproject(snapshot["pyproject.toml"])
    return source_root, snapshot, package_files_before


def _validate_common(config_settings: object) -> None:
    _validate_interpreter()
    _validate_config_settings(config_settings)
    _, snapshot, _ = _source_snapshot()
    _validate_pyproject(snapshot["pyproject.toml"])


def _metadata_payloads(snapshot: Mapping[str, bytes]) -> dict[str, bytes]:
    return {
        "METADATA": _METADATA,
        "WHEEL": _WHEEL,
        "licenses/LICENSE": snapshot["LICENSE"],
    }


def _output_directory(value: str, label: str) -> Path:
    path = Path(value).absolute()
    try:
        info = path.lstat()
    except OSError as exc:
        _refuse("UNSAFE_SOURCE_PATH", f"{label} is unavailable: {exc}")
    if not stat.S_ISDIR(info.st_mode) or path.is_symlink():
        _refuse("UNSAFE_SOURCE_PATH", f"{label} must be a regular directory")
    return path


def _write_new_file(path: Path, data: bytes, mode: int = 0o644) -> None:
    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fchmod(descriptor, mode)
    except FileExistsError:
        _refuse("OUTPUT_ALREADY_EXISTS", f"output already exists: {path.name}")
    except BackendRefusal:
        raise
    except OSError as exc:
        if descriptor is not None:
            os.close(descriptor)
            descriptor = None
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        _refuse("WHEEL_CONTRACT_MISMATCH", f"cannot create output: {exc}")
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _zip_info(name: str) -> zipfile.ZipInfo:
    _safe_relative_path(name)
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    info.internal_attr = 0
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.flag_bits = 0
    info.extra = b""
    info.comment = b""
    return info


def _record_bytes(members: list[tuple[str, bytes]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(
        stream,
        delimiter=",",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    for name, payload in members:
        digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=")
        writer.writerow((name, "sha256=" + digest.decode("ascii"), str(len(payload))))
    writer.writerow((f"{_DIST_INFO}/RECORD", "", ""))
    return stream.getvalue().encode("utf-8")


def _wheel_bytes(
    snapshot: Mapping[str, bytes],
    package_files: tuple[str, ...],
    metadata: Mapping[str, bytes],
) -> bytes:
    installed_members = [
        (relative.removeprefix("src/"), snapshot[relative])
        for relative in package_files
    ]
    installed_members.sort(key=lambda item: item[0].encode("utf-8"))
    members = installed_members + [
        (f"{_DIST_INFO}/METADATA", metadata["METADATA"]),
        (f"{_DIST_INFO}/WHEEL", metadata["WHEEL"]),
        (f"{_DIST_INFO}/licenses/LICENSE", metadata["licenses/LICENSE"]),
    ]
    record = _record_bytes(members)
    complete_members = members + [(f"{_DIST_INFO}/RECORD", record)]
    output = io.BytesIO()
    with zipfile.ZipFile(
        output, mode="w", compression=zipfile.ZIP_STORED, strict_timestamps=True
    ) as archive:
        archive.comment = b""
        for name, payload in complete_members:
            archive.writestr(_zip_info(name), payload)
    return output.getvalue()


def _validate_prepared_metadata(path_text: str, expected: Mapping[str, bytes]) -> dict[str, bytes]:
    path = Path(path_text).absolute()
    if path.name != _DIST_INFO:
        _refuse("METADATA_DIRECTORY_MISMATCH", "metadata basename mismatch")
    try:
        root_stat = path.lstat()
    except OSError as exc:
        _refuse("METADATA_DIRECTORY_MISMATCH", f"metadata missing: {exc}")
    if (
        not stat.S_ISDIR(root_stat.st_mode)
        or path.is_symlink()
        or stat.S_IMODE(root_stat.st_mode) != 0o755
    ):
        _refuse("METADATA_DIRECTORY_MISMATCH", "metadata root mode/type mismatch")
    observed: dict[str, bytes] = {}
    expected_directories = {"licenses"}
    for current_text, directories, files in os.walk(path, topdown=True, followlinks=False):
        current = Path(current_text)
        relative_dir = current.relative_to(path).as_posix()
        if relative_dir == ".":
            relative_dir = ""
        for directory in directories:
            directory_path = current / directory
            relative = (PurePosixPath(relative_dir) / directory).as_posix()
            info = directory_path.lstat()
            if (
                relative not in expected_directories
                or not stat.S_ISDIR(info.st_mode)
                or directory_path.is_symlink()
                or stat.S_IMODE(info.st_mode) != 0o755
            ):
                _refuse("METADATA_DIRECTORY_MISMATCH", f"unexpected directory: {relative}")
        for filename in files:
            file_path = current / filename
            relative = (PurePosixPath(relative_dir) / filename).as_posix()
            info = file_path.lstat()
            if (
                relative not in expected
                or not stat.S_ISREG(info.st_mode)
                or file_path.is_symlink()
                or stat.S_IMODE(info.st_mode) != 0o644
            ):
                _refuse("METADATA_DIRECTORY_MISMATCH", f"unexpected metadata: {relative}")
            observed[relative] = file_path.read_bytes()
    if observed != dict(expected):
        _refuse("METADATA_DIRECTORY_MISMATCH", "metadata bytes/member set mismatch")
    return observed


def _tar_info(name: str, *, directory: bool, size: int = 0) -> tarfile.TarInfo:
    _safe_relative_path(name.rstrip("/"))
    info = tarfile.TarInfo(name)
    info.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
    info.mode = 0o755 if directory else 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    info.linkname = ""
    info.size = 0 if directory else size
    info.pax_headers = {}
    return info


def _tar_bytes(snapshot: Mapping[str, bytes], package_files: tuple[str, ...]) -> bytes:
    files: dict[str, bytes] = {
        f"{_SDIST_ROOT}/pyproject.toml": snapshot["pyproject.toml"],
        f"{_SDIST_ROOT}/build_backend/ebu_build_backend.py": snapshot[
            "build_backend/ebu_build_backend.py"
        ],
        f"{_SDIST_ROOT}/LICENSE": snapshot["LICENSE"],
        f"{_SDIST_ROOT}/PKG-INFO": _METADATA,
    }
    for relative in package_files:
        files[f"{_SDIST_ROOT}/{relative}"] = snapshot[relative]
    directories: set[str] = {_SDIST_ROOT + "/"}
    for file_name in files:
        parent = PurePosixPath(file_name).parent
        while str(parent) not in (".", ""):
            directories.add(parent.as_posix() + "/")
            parent = parent.parent
    member_names = sorted(
        (*directories, *files), key=lambda item: item.encode("utf-8")
    )
    output = io.BytesIO()
    archive = tarfile.open(
        fileobj=output,
        mode="w",
        format=tarfile.PAX_FORMAT,
        pax_headers={"comment": "ebu-sdist-v1"},
    )
    try:
        for name in member_names:
            if name.endswith("/"):
                archive.addfile(_tar_info(name, directory=True))
            else:
                payload = files[name]
                archive.addfile(
                    _tar_info(name, directory=False, size=len(payload)),
                    io.BytesIO(payload),
                )
        effective_end = archive.offset
    finally:
        archive.close()
    return output.getvalue()[:effective_end] + b"\x00" * 1024


def _stored_gzip(data: bytes) -> bytes:
    output = bytearray.fromhex("1f8b08000000000000ff")
    if data:
        offset = 0
        while offset < len(data):
            end = min(offset + 65535, len(data))
            chunk = data[offset:end]
            final = end == len(data)
            output.append(1 if final else 0)
            length = len(chunk)
            output.extend(struct.pack("<H", length))
            output.extend(struct.pack("<H", 0xFFFF ^ length))
            output.extend(chunk)
            offset = end
    else:
        output.extend(b"\x01\x00\x00\xff\xff")
    output.extend(struct.pack("<I", binascii.crc32(data) & 0xFFFFFFFF))
    output.extend(struct.pack("<I", len(data) & 0xFFFFFFFF))
    return bytes(output)


def _build_input_manifest(snapshot: Mapping[str, bytes]) -> bytes:
    lines = ["ebu-build-input-manifest-v1"]
    for path in sorted(snapshot, key=lambda item: item.encode("utf-8")):
        payload = snapshot[path]
        lines.append(
            f"sha256={hashlib.sha256(payload).hexdigest()} size={len(payload)} path={path}"
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def get_requires_for_build_wheel(config_settings=None):
    _validate_common(config_settings)
    return []


def get_requires_for_build_sdist(config_settings=None):
    _validate_common(config_settings)
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    _validate_interpreter()
    _validate_config_settings(config_settings)
    _, snapshot, _ = _source_snapshot()
    parent = _output_directory(metadata_directory, "metadata_directory")
    target = parent / _DIST_INFO
    if target.exists() or target.is_symlink():
        _refuse("OUTPUT_ALREADY_EXISTS", "prepared metadata already exists")
    expected = _metadata_payloads(snapshot)
    created = False
    try:
        os.mkdir(target, 0o755)
        created = True
        os.chmod(target, 0o755)
        licenses = target / "licenses"
        os.mkdir(licenses, 0o755)
        os.chmod(licenses, 0o755)
        _write_new_file(target / "METADATA", expected["METADATA"])
        _write_new_file(target / "WHEEL", expected["WHEEL"])
        _write_new_file(licenses / "LICENSE", expected["licenses/LICENSE"])
    except BaseException:
        if created:
            shutil.rmtree(target, ignore_errors=True)
        raise
    return _DIST_INFO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    _validate_interpreter()
    _validate_config_settings(config_settings)
    _, snapshot, package_files = _source_snapshot()
    output_directory = _output_directory(wheel_directory, "wheel_directory")
    target = output_directory / _WHEEL_FILENAME
    if target.exists() or target.is_symlink():
        _refuse("OUTPUT_ALREADY_EXISTS", "wheel already exists")
    expected_metadata = _metadata_payloads(snapshot)
    if metadata_directory is None:
        metadata = expected_metadata
    else:
        metadata = _validate_prepared_metadata(metadata_directory, expected_metadata)
    payload = _wheel_bytes(snapshot, package_files, metadata)
    _write_new_file(target, payload)
    return _WHEEL_FILENAME


def build_sdist(sdist_directory, config_settings=None):
    _validate_interpreter()
    _validate_config_settings(config_settings)
    _, snapshot, package_files = _source_snapshot()
    output_directory = _output_directory(sdist_directory, "sdist_directory")
    target = output_directory / _SDIST_FILENAME
    if target.exists() or target.is_symlink():
        _refuse("OUTPUT_ALREADY_EXISTS", "sdist already exists")
    payload = _stored_gzip(_tar_bytes(snapshot, package_files))
    _write_new_file(target, payload)
    return _SDIST_FILENAME


from typing import NoReturn  # noqa: E402


__all__ = (
    "build_sdist",
    "build_wheel",
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_wheel",
)
