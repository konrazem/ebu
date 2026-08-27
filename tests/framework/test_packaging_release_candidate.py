"""Stage C packaging and alpha-release-candidate conformance tests."""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = json.loads(
    (ROOT / "framework_alpha_packaging_release_candidate_contract.json").read_bytes()
)
PACKAGE_PATHS = tuple(CONTRACT["package_inventory"]["paths"])
INSTALLED_PATHS = tuple(
    sorted(
        (PurePosixPath(path).relative_to("src").as_posix() for path in PACKAGE_PATHS),
        key=lambda value: value.encode("utf-8"),
    )
)
DIST_INFO = "ebu_framework-0.1.0a1.dist-info"
WHEEL_NAME = "ebu_framework-0.1.0a1-cp314-none-any.whl"
SDIST_NAME = "ebu_framework-0.1.0a1.tar.gz"
SDIST_ROOT = "ebu_framework-0.1.0a1"
METADATA = (
    "Metadata-Version: 2.5\n"
    "Name: ebu-framework\n"
    "Version: 0.1.0a1\n"
    "Summary: Pre-alpha typed and reproducible research-framework infrastructure for EBU\n"
    "Requires-Python: >=3.14,<3.15\n"
    "License-Expression: MIT AND Unicode-3.0\n"
    "License-File: LICENSE\n"
    "License-File: LICENSE-UNICODE\n"
    "Import-Name: ebu_framework\n"
    "Requires-Dist: PyNaCl==1.6.2\n"
    "\n"
).encode("utf-8")


def _copy_source(destination: Path) -> Path:
    destination.mkdir()
    shutil.copy2(ROOT / "pyproject.toml", destination / "pyproject.toml")
    shutil.copy2(ROOT / "LICENSE", destination / "LICENSE")
    shutil.copy2(ROOT / "LICENSE-UNICODE", destination / "LICENSE-UNICODE")
    shutil.copytree(ROOT / "build_backend", destination / "build_backend")
    shutil.copytree(ROOT / "src", destination / "src")
    for path in destination.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)
        elif path.is_file():
            path.chmod(0o644)
    return destination


def _load_backend(source: Path, discriminator: str):
    path = source / "build_backend/ebu_build_backend.py"
    spec = importlib.util.spec_from_file_location(
        f"_ebu_stage_c_backend_{discriminator}", path
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot create backend import specification")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build(source: Path, output: Path, discriminator: str) -> tuple[Path, Path]:
    backend = _load_backend(source, discriminator)
    wheel_dir = output / "wheel"
    sdist_dir = output / "sdist"
    wheel_dir.mkdir(parents=True)
    sdist_dir.mkdir(parents=True)
    wheel = wheel_dir / backend.build_wheel(str(wheel_dir))
    sdist = sdist_dir / backend.build_sdist(str(sdist_dir))
    return wheel, sdist


def _safe_extract_sdist(archive_path: Path, destination: Path) -> Path:
    destination.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name.rstrip("/"))
            if (
                pure.is_absolute()
                or not pure.parts
                or any(part in ("", ".", "..") for part in pure.parts)
                or member.issym()
                or member.islnk()
            ):
                raise AssertionError(f"unsafe sdist member: {member.name}")
            target = destination.joinpath(*pure.parts)
            if member.isdir():
                target.mkdir(mode=0o755, parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise AssertionError(f"nonregular sdist member: {member.name}")
            target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            extracted = archive.extractfile(member)
            if extracted is None:
                raise AssertionError(f"unreadable sdist member: {member.name}")
            target.write_bytes(extracted.read())
            target.chmod(0o644)
    return destination / SDIST_ROOT


def _record_rows(raw: bytes) -> list[tuple[str, str, str]]:
    return [tuple(row) for row in csv.reader(io.StringIO(raw.decode("utf-8")))]


class StageCPackagingTests(unittest.TestCase):
    def test_exact_source_and_backend_inventory(self) -> None:
        actual = tuple(
            sorted(
                (
                    path.relative_to(ROOT).as_posix()
                    for path in (ROOT / "src/ebu_framework").rglob("*")
                    if path.is_file() and not path.is_symlink()
                ),
                key=lambda value: value.encode("utf-8"),
            )
        )
        self.assertEqual((actual, len(actual)), (PACKAGE_PATHS, 48))
        backend = _load_backend(ROOT, "inventory")
        self.assertEqual(backend._PLANNED_PACKAGE_FILES, frozenset(PACKAGE_PATHS))
        self.assertEqual(backend._discover_package_files(ROOT), PACKAGE_PATHS)
        self.assertEqual(
            hashlib.sha256((ROOT / "pyproject.toml").read_bytes()).hexdigest(),
            "25f7a0cacdfa54c23f0fb7122d14f28d9e3e44d76105f8805f636e895e325b47",
        )
        self.assertEqual(
            hashlib.sha256((ROOT / "requirements-framework.lock").read_bytes()).hexdigest(),
            "8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a",
        )
        license_identities = {
            "LICENSE": (
                1069,
                "2cdab1dd4903f2652a8c52be11911573d8bacf0b9c7d7cf2c1e81af118b2b907",
            ),
            "LICENSE-UNICODE": (
                1995,
                "e7a93b009565cfce55919a381437ac4db883e9da2126fa28b91d12732bc53d96",
            ),
        }
        self.assertEqual(backend._LICENSE_INPUT_IDENTITIES, license_identities)
        for relative, expected in license_identities.items():
            payload = (ROOT / relative).read_bytes()
            self.assertEqual((len(payload), hashlib.sha256(payload).hexdigest()), expected)

    def test_each_missing_package_file_refuses(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-stage-c-missing-") as temporary:
            source = _copy_source(Path(temporary) / "source")
            backend = _load_backend(source, "missing")
            for index, relative in enumerate(PACKAGE_PATHS):
                with self.subTest(path=relative):
                    path = source / relative
                    saved = path.read_bytes()
                    path.unlink()
                    with self.assertRaises(backend.BackendRefusal) as caught:
                        backend._discover_package_files(source)
                    self.assertEqual(caught.exception.code, "PACKAGE_DATA_MISSING")
                    path.write_bytes(saved)
                    path.chmod(0o644)
            for relative in ("LICENSE", "LICENSE-UNICODE"):
                with self.subTest(missing_license=relative):
                    path = source / relative
                    saved = path.read_bytes()
                    path.unlink()
                    with self.assertRaises(backend.BackendRefusal) as caught:
                        backend._source_snapshot()
                    self.assertEqual(caught.exception.code, "UNSAFE_SOURCE_PATH")
                    path.write_bytes(saved)
                    path.chmod(0o644)
                with self.subTest(changed_license=relative):
                    saved = path.read_bytes()
                    path.write_bytes(saved + b"changed\n")
                    with self.assertRaises(backend.BackendRefusal) as caught:
                        backend._source_snapshot()
                    self.assertEqual(caught.exception.code, "LICENSE_FILE_MISMATCH")
                    path.write_bytes(saved)
                    path.chmod(0o644)

    def test_unknown_and_unsafe_inputs_refuse_fail_closed(self) -> None:
        cases = (
            ("unknown.py", "PACKAGE_FILE_SET_MISMATCH", "file"),
            ("unknown.data", "PACKAGE_FILE_SET_MISMATCH", "file"),
            ("unknown.pyc", "PACKAGE_FILE_SET_MISMATCH", "file"),
            ("__pycache__/unknown.pyc", "PACKAGE_FILE_SET_MISMATCH", "file"),
            (".hidden", "PACKAGE_FILE_SET_MISMATCH", "file"),
            ("Actions.py", "UNSAFE_SOURCE_PATH", "case_collision"),
            ("é.py", "UNSAFE_SOURCE_PATH", "file"),
            ("unsafe-link", "UNSAFE_SOURCE_PATH", "symlink"),
            ("unsafe-hardlink", "UNSAFE_SOURCE_PATH", "hardlink"),
            ("unsafe-fifo", "UNSAFE_SOURCE_PATH", "fifo"),
            ("unsafe-socket", "UNSAFE_SOURCE_PATH", "socket"),
        )
        short_temp_root = "/private/tmp" if Path("/private/tmp").is_dir() else None
        with tempfile.TemporaryDirectory(prefix="e-c-", dir=short_temp_root) as temporary:
            base = Path(temporary)
            for index, (relative, expected, kind) in enumerate(cases):
                with self.subTest(relative=relative, kind=kind):
                    source = _copy_source(base / f"source-{index}")
                    target = source / "src/ebu_framework" / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if kind in {"file", "case_collision", "socket"}:
                        target.write_bytes(b"unknown\n")
                    elif kind == "symlink":
                        target.symlink_to(source / "src/ebu_framework/errors.py")
                    elif kind == "hardlink":
                        os.link(source / "src/ebu_framework/errors.py", target)
                    elif kind == "fifo":
                        os.mkfifo(target)
                    backend = _load_backend(source, f"unknown_{index}")
                    if kind == "case_collision":
                        backend._PLANNED_PACKAGE_FILES = frozenset(
                            (*backend._PLANNED_PACKAGE_FILES, "src/ebu_framework/Actions.py")
                        )
                    original_lstat = Path.lstat

                    def synthetic_lstat(path: Path):
                        result = original_lstat(path)
                        if kind == "socket" and path == target:
                            values = list(result)
                            values[0] = stat.S_IFSOCK | 0o644
                            return os.stat_result(values)
                        return result

                    original_walk = os.walk

                    def synthetic_walk(top, *args, **kwargs):
                        for current, directories, files in original_walk(top, *args, **kwargs):
                            if kind == "case_collision" and Path(current) == source / "src/ebu_framework":
                                files.append("Actions.py")
                            yield current, directories, files

                    with (
                        mock.patch.object(Path, "lstat", synthetic_lstat),
                        mock.patch.object(backend.os, "walk", synthetic_walk),
                    ):
                        with self.assertRaises(backend.BackendRefusal) as caught:
                            backend._discover_package_files(source)
                        self.assertEqual(caught.exception.code, expected)
            for index, license_files in enumerate(
                (
                    '["LICENSE-UNICODE", "LICENSE"]',
                    '["LICENSE", "LICENSE-UNICODE", "LICENSE-UNKNOWN"]',
                )
            ):
                with self.subTest(license_files=license_files):
                    source = _copy_source(base / f"license-metadata-{index}")
                    pyproject = source / "pyproject.toml"
                    pyproject.write_text(
                        pyproject.read_text("utf-8").replace(
                            '["LICENSE", "LICENSE-UNICODE"]', license_files
                        ),
                        encoding="utf-8",
                    )
                    backend = _load_backend(source, f"license_metadata_{index}")
                    with self.assertRaises(backend.BackendRefusal) as caught:
                        backend._source_snapshot()
                    self.assertEqual(caught.exception.code, "DYNAMIC_METADATA_FORBIDDEN")

    def test_wheel_metadata_record_and_archive_are_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-stage-c-wheel-") as temporary:
            base = Path(temporary)
            source = _copy_source(base / "source")
            backend = _load_backend(source, "wheel")
            metadata_parent = base / "prepared"
            metadata_parent.mkdir()
            prepared = metadata_parent / backend.prepare_metadata_for_build_wheel(
                str(metadata_parent)
            )
            prepared_files = {
                path.relative_to(prepared).as_posix(): path.read_bytes()
                for path in prepared.rglob("*")
                if path.is_file()
            }
            self.assertEqual(
                prepared_files,
                {
                    "METADATA": METADATA,
                    "WHEEL": backend._WHEEL,
                    "licenses/LICENSE": (ROOT / "LICENSE").read_bytes(),
                    "licenses/LICENSE-UNICODE": (ROOT / "LICENSE-UNICODE").read_bytes(),
                },
            )
            wheel_dir = base / "output"
            wheel_dir.mkdir()
            wheel = wheel_dir / backend.build_wheel(
                str(wheel_dir), metadata_directory=str(prepared)
            )
            self.assertEqual(wheel.name, WHEEL_NAME)
            with zipfile.ZipFile(wheel) as archive:
                self.assertEqual(archive.comment, b"")
                infos = archive.infolist()
                names = tuple(info.filename for info in infos)
                expected = INSTALLED_PATHS + (
                    f"{DIST_INFO}/METADATA",
                    f"{DIST_INFO}/WHEEL",
                    f"{DIST_INFO}/licenses/LICENSE",
                    f"{DIST_INFO}/licenses/LICENSE-UNICODE",
                    f"{DIST_INFO}/RECORD",
                )
                self.assertEqual((names, len(names), len(set(names))), (expected, 53, 53))
                for info in infos:
                    pure = PurePosixPath(info.filename)
                    self.assertFalse(pure.is_absolute())
                    self.assertNotIn("..", pure.parts)
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(info.extra, b"")
                    self.assertEqual(info.comment, b"")
                    self.assertEqual(info.flag_bits, 0)
                    self.assertEqual(info.external_attr >> 16, stat.S_IFREG | 0o644)
                    payload = archive.read(info)
                    self.assertEqual(info.CRC, binascii.crc32(payload))
                    self.assertEqual(info.file_size, len(payload))
                self.assertEqual(archive.read(f"{DIST_INFO}/METADATA"), METADATA)
                self.assertEqual(archive.read(f"{DIST_INFO}/licenses/LICENSE"), (ROOT / "LICENSE").read_bytes())
                self.assertEqual(
                    archive.read(f"{DIST_INFO}/licenses/LICENSE-UNICODE"),
                    (ROOT / "LICENSE-UNICODE").read_bytes(),
                )
                rows = _record_rows(archive.read(f"{DIST_INFO}/RECORD"))
                self.assertEqual(tuple(row[0] for row in rows), names)
                for row, name in zip(rows[:-1], names[:-1], strict=True):
                    payload = archive.read(name)
                    digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
                    self.assertEqual(row, (name, f"sha256={digest}", str(len(payload))))
                self.assertEqual(rows[-1], (f"{DIST_INFO}/RECORD", "", ""))

    def test_sdist_contents_safety_and_metadata_are_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-stage-c-sdist-") as temporary:
            base = Path(temporary)
            source = _copy_source(base / "source")
            _, sdist = _build(source, base / "output", "sdist")
            self.assertEqual(sdist.name, SDIST_NAME)
            raw = sdist.read_bytes()
            self.assertEqual(raw[:10], bytes.fromhex("1f8b08000000000000ff"))
            with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
                members = archive.getmembers()
                files = tuple(member for member in members if member.isfile())
                directories = tuple(member for member in members if member.isdir())
                expected_files = tuple(
                    sorted(
                        (
                            f"{SDIST_ROOT}/pyproject.toml",
                            f"{SDIST_ROOT}/build_backend/ebu_build_backend.py",
                            f"{SDIST_ROOT}/LICENSE",
                            f"{SDIST_ROOT}/LICENSE-UNICODE",
                            f"{SDIST_ROOT}/PKG-INFO",
                            *(f"{SDIST_ROOT}/{path}" for path in PACKAGE_PATHS),
                        ),
                        key=lambda value: value.encode("utf-8"),
                    )
                )
                self.assertEqual((tuple(member.name for member in files), len(files)), (expected_files, 53))
                self.assertGreater(len(directories), 0)
                self.assertEqual(len({member.name for member in members}), len(members))
                for member in members:
                    pure = PurePosixPath(member.name.rstrip("/"))
                    self.assertFalse(pure.is_absolute())
                    self.assertNotIn("..", pure.parts)
                    self.assertFalse(member.issym() or member.islnk())
                    self.assertEqual((member.uid, member.gid, member.uname, member.gname, member.mtime), (0, 0, "", "", 0))
                    self.assertEqual(member.mode, 0o755 if member.isdir() else 0o644)
                pkg_info = archive.extractfile(f"{SDIST_ROOT}/PKG-INFO")
                self.assertIsNotNone(pkg_info)
                self.assertEqual(pkg_info.read(), METADATA)
                for relative in ("LICENSE", "LICENSE-UNICODE"):
                    license_file = archive.extractfile(f"{SDIST_ROOT}/{relative}")
                    self.assertIsNotNone(license_file)
                    self.assertEqual(license_file.read(), (ROOT / relative).read_bytes())

    def test_direct_and_sdist_derived_wheels_are_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-stage-c-repro-") as temporary:
            base = Path(temporary)
            wheel_bytes: list[bytes] = []
            sdist_bytes: list[bytes] = []
            prior_epoch = os.environ.get("SOURCE_DATE_EPOCH")
            try:
                for index in range(3):
                    source = _copy_source(base / f"source-{index}")
                    os.utime(source / "pyproject.toml", (1_000_000 + index, 1_000_000 + index))
                    os.environ["SOURCE_DATE_EPOCH"] = str(1_700_000_000 + index)
                    wheel, sdist = _build(source, base / f"output-{index}", f"repro_{index}")
                    wheel_bytes.append(wheel.read_bytes())
                    sdist_bytes.append(sdist.read_bytes())
            finally:
                if prior_epoch is None:
                    os.environ.pop("SOURCE_DATE_EPOCH", None)
                else:
                    os.environ["SOURCE_DATE_EPOCH"] = prior_epoch
            self.assertEqual(len(set(wheel_bytes)), 1)
            self.assertEqual(len(set(sdist_bytes)), 1)
            extracted = _safe_extract_sdist(base / "output-0/sdist" / SDIST_NAME, base / "extracted")
            derived_output = base / "derived"
            derived_output.mkdir()
            backend = _load_backend(extracted, "derived")
            derived = derived_output / backend.build_wheel(str(derived_output))
            self.assertEqual(derived.read_bytes(), wheel_bytes[0])

    def test_preexisting_output_refuses_without_partial_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ebu-stage-c-existing-") as temporary:
            base = Path(temporary)
            source = _copy_source(base / "source")
            output = base / "output"
            output.mkdir()
            target = output / WHEEL_NAME
            sentinel = b"do-not-replace\n"
            target.write_bytes(sentinel)
            backend = _load_backend(source, "existing")
            with self.assertRaises(backend.BackendRefusal) as caught:
                backend.build_wheel(str(output))
            self.assertEqual(caught.exception.code, "OUTPUT_ALREADY_EXISTS")
            self.assertEqual(target.read_bytes(), sentinel)
            self.assertEqual(tuple(output.iterdir()), (target,))

    def test_backend_static_reachability_is_packaging_only(self) -> None:
        source = (ROOT / "build_backend/ebu_build_backend.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        called_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_names.add(node.func.attr)
        self.assertTrue(imported_roots <= {
            "__future__", "base64", "binascii", "collections", "csv", "hashlib",
            "io", "os", "pathlib", "shutil", "stat", "struct", "sys", "tarfile",
            "tomllib", "typing", "zipfile",
        })
        self.assertTrue(called_names.isdisjoint({
            "system", "popen", "run", "Popen", "urlopen", "create_connection",
            "advance_epoch", "bounded_step", "p1c_step", "runner", "finalize_run",
        }))
        lowered = source.lower()
        for term in ("results/", "books/", "trajectory", "model_step", "gate1"):
            self.assertNotIn(term, lowered)
        validator_tree = ast.parse(
            (ROOT / "scripts/validate_stage_c_release_candidate.py").read_text(
                encoding="utf-8"
            )
        )
        runner_source = next(
            ast.literal_eval(node.value)
            for node in validator_tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "RUNNER_SOURCE"
        )
        runner_tree = ast.parse(runner_source)
        path_insertions = tuple(
            ast.unparse(node)
            for node in ast.walk(runner_tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "sys"
            and node.func.value.attr == "path"
            and node.func.attr == "insert"
        )
        self.assertEqual(
            path_insertions,
            (
                "sys.path.insert(0, str(source))",
                "sys.path.insert(0, str(test_root))",
                "sys.path.insert(0, str(source / 'src'))",
            ),
        )
        self.assertIn(
            "if artifact != \"source\" and origin.is_relative_to(source):",
            runner_source,
        )
        assignments = {
            node.targets[0].id: ast.literal_eval(node.value)
            for node in validator_tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in {
                "AUTHORITY_HASHES",
                "SEMANTIC_SCOPE_AST_IDENTITIES",
                "CONVENTIONAL_WHEELS",
                "CONVENTIONAL_COUNTS",
                "SQLITE_UPSTREAM_SOURCE_ID_REFERENCE",
                "SQLITE_RUNTIME_SOURCE_ID_REQUIRED",
                "DEBIAN_SQLITE_PACKAGE_REQUIRED",
            }
        }
        self.assertEqual(
            assignments,
            {
                "AUTHORITY_HASHES": {
                    "FRAMEWORK_ALPHA_PACKAGING_RELEASE_CANDIDATE_AUTHORITY_AMENDMENT.md": "c2868aded1c7135b36933915de8abe363bc7a4ffaa3bced186dacb880e321765",
                    "framework_alpha_packaging_release_candidate_contract.json": "835b01ee5f979454f0b57bd8d374f5294a9907e01508413b90c84c888b87b67d",
                    "framework_alpha_packaging_release_candidate_implementation_path_manifest.json": "d1fb69aa62ae666312e82e406b44906e63b24eaf7e8a32c398c19b2e845058b3",
                    "framework_alpha_packaging_release_candidate_predecessor_manifest.json": "a79c43b9a2f09744438320cdc8ef6a2b536b4ed065854b9ff675138f165c9918",
                    "framework_alpha_packaging_release_candidate_validation_contract.json": "85a7c556cb11ce276129eb04e4a43276f561d9f8e2ca09a24ce872791617af0f",
                },
                "SEMANTIC_SCOPE_AST_IDENTITIES": {
                    "artifact_predecessor_function": (40643, "56f0fcdb275b3d402b2ce65b05f4df285e2c0b83ef5e1020bb89e8f69fb4e7db"),
                    "atomic_predecessor_method": (32971, "289db10d3223b4d547e5aaa5e788efe67b24abafd59c59b334b3f1ba5fd539e7"),
                    "capabilities_reachability_method": (55295, "ff226be2349bc580482d28ad29a2c181a0eb27d725d11f509872b996283cc4b7"),
                    "interaction_graph_method": (43399, "c27b4a36b3feaa46cc6e3e9a2d5587fc8f8c5231f683fd066351c71ccdeab8b4"),
                    "interaction_predecessor_method": (53348, "9ccef25ed0cdd8f9048f08b44b1c1b6c2d64f044f289c742b245da6a54664cd7"),
                },
                "CONVENTIONAL_WHEELS": {
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
                },
                "CONVENTIONAL_COUNTS": {
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
                },
                "SQLITE_UPSTREAM_SOURCE_ID_REFERENCE": "2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69a1e33",
                "SQLITE_RUNTIME_SOURCE_ID_REQUIRED": "2024-08-13 09:16:08 c9c2ab54ba1f5f46360f1b4f35d849cd3f080e6fc2b6c60e91b16c63f69aalt1",
                "DEBIAN_SQLITE_PACKAGE_REQUIRED": "libsqlite3-0:amd64=3.46.1-7+deb13u1",
            },
        )
        verify_runtime = next(
            node
            for node in validator_tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_verify_runtime"
        )
        runtime_comparisons = {
            ast.unparse(node)
            for node in ast.walk(verify_runtime)
            if isinstance(node, ast.Compare)
        }
        self.assertIn(
            "source_id != SQLITE_RUNTIME_SOURCE_ID_REQUIRED", runtime_comparisons
        )
        self.assertIn(
            "debian_sqlite_package != DEBIAN_SQLITE_PACKAGE_REQUIRED",
            runtime_comparisons,
        )
        self.assertFalse(
            any(
                "SQLITE_UPSTREAM_SOURCE_ID_REFERENCE" in comparison
                for comparison in runtime_comparisons
            )
        )
        observed_assignment = next(
            node
            for node in verify_runtime.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "observed"
                for target in node.targets
            )
        )
        self.assertIsInstance(observed_assignment.value, ast.Dict)
        observed_entries = {
            ast.literal_eval(key): ast.unparse(value)
            for key, value in zip(
                observed_assignment.value.keys, observed_assignment.value.values
            )
            if key is not None
        }
        self.assertEqual(
            {
                key: observed_entries[key]
                for key in (
                    "sqlite_upstream_source_id_reference",
                    "sqlite_runtime_source_id_required",
                    "debian_libsqlite3_0_required",
                )
            },
            {
                "sqlite_upstream_source_id_reference": "SQLITE_UPSTREAM_SOURCE_ID_REFERENCE",
                "sqlite_runtime_source_id_required": "SQLITE_RUNTIME_SOURCE_ID_REQUIRED",
                "debian_libsqlite3_0_required": "DEBIAN_SQLITE_PACKAGE_REQUIRED",
            },
        )


if __name__ == "__main__":
    unittest.main()
