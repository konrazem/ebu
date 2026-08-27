"""Isolated installed-artifact probe for the Stage C alpha candidate."""

from __future__ import annotations

import argparse
import ast
import hashlib
from importlib import import_module, metadata
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_CONTRACT = ROOT / "framework_alpha_packaging_release_candidate_contract.json"
I9_CONTRACT = ROOT / "unified_python_research_framework_i9_contract.json"
CLCD_CONTRACT = ROOT / "closed_loop_correction_diagnostics_contract.json"


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _regular_real_file(path: Path) -> None:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise AssertionError(f"installed origin is not a regular nonsymlink file: {path}")
    for parent in path.parents:
        if parent == parent.parent:
            break
        if parent.is_symlink():
            raise AssertionError(f"installed origin has a symlinked parent: {path}")


def _module_names(package_paths: tuple[str, ...]) -> tuple[str, ...]:
    names: list[str] = []
    for value in package_paths:
        relative = PurePosixPath(value).relative_to("src")
        if relative.suffix != ".py":
            continue
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        names.append(".".join(parts))
    return tuple(names)


def _digest(values: tuple[str, ...]) -> tuple[int, str]:
    payload = ("\n".join(values) + "\n").encode("utf-8")
    return len(payload), hashlib.sha256(payload).hexdigest()


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--forbid-root", type=Path, action="append", default=[])
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--artifact-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = _arguments()
    checks = 0
    checkout = args.checkout.resolve(strict=True)
    forbidden = (checkout, *(path.resolve(strict=True) for path in args.forbid_root))
    if not sys.flags.isolated or os.environ.get("PYTHONPATH"):
        raise AssertionError("probe requires -I and no PYTHONPATH")
    if any(Path.cwd().iterdir()):
        raise AssertionError("probe working directory must be empty")
    checks += 2

    resolved_sys_path = tuple(
        Path(value).resolve(strict=False) for value in sys.path if value
    )
    if any(_within(path, root) for path in resolved_sys_path for root in forbidden):
        raise AssertionError("forbidden source or extraction root is on sys.path")
    if Path(sys.prefix).resolve() == Path(sys.base_prefix).resolve():
        raise AssertionError("probe interpreter is not an isolated environment")
    environment = Path(sys.prefix).resolve(strict=True)
    checks += 2

    contract = json.loads(PACKAGE_CONTRACT.read_bytes())
    i9 = json.loads(I9_CONTRACT.read_bytes())
    clcd = json.loads(CLCD_CONTRACT.read_bytes())
    package_paths = tuple(contract["package_inventory"]["paths"])
    module_names = _module_names(package_paths)
    if len(module_names) != 44 or len(set(module_names)) != 44:
        raise AssertionError("accepted module inventory is not exactly 44 unique names")
    checks += 1

    distribution = metadata.distribution("ebu-framework")
    if distribution.metadata["Name"] != "ebu-framework":
        raise AssertionError("distribution name mismatch")
    if distribution.version != "0.1.0a1":
        raise AssertionError("distribution version mismatch")
    if distribution.metadata["Requires-Python"] != ">=3.14,<3.15":
        raise AssertionError("Requires-Python mismatch")
    if distribution.metadata.get_all("Requires-Dist") != ["PyNaCl==1.6.2"]:
        raise AssertionError("Requires-Dist mismatch")
    direct_url_text = distribution.read_text("direct_url.json")
    if direct_url_text is None:
        raise AssertionError("installed wheel provenance metadata is missing")
    direct_url = json.loads(direct_url_text)
    expected_archive_info = {
        "hash": f"sha256={args.artifact_sha256}",
        "hashes": {"sha256": args.artifact_sha256},
    }
    if (
        set(direct_url) != {"archive_info", "url"}
        or direct_url.get("archive_info") != expected_archive_info
        or not str(direct_url.get("url", "")).endswith(f"/{args.artifact_name}")
        or "dir_info" in direct_url
        or "vcs_info" in direct_url
    ):
        raise AssertionError("installed provenance is not the exact non-editable wheel")
    checks += 5

    installed_package_files = tuple(
        sorted(
            (
                PurePosixPath(str(item)).as_posix()
                for item in distribution.files or ()
                if PurePosixPath(str(item)).parts[:1] == ("ebu_framework",)
            ),
            key=lambda value: value.encode("utf-8"),
        )
    )
    expected_installed_files = tuple(
        sorted(
            (PurePosixPath(value).relative_to("src").as_posix() for value in package_paths),
            key=lambda value: value.encode("utf-8"),
        )
    )
    if installed_package_files != expected_installed_files:
        raise AssertionError("installed package file inventory mismatch")
    checks += 1

    imported = {name: import_module(name) for name in module_names}
    package_root = Path(imported["ebu_framework"].__file__).resolve(strict=True).parent
    if not _within(package_root, environment):
        raise AssertionError("installed package is outside the environment")
    for name, module in imported.items():
        origin_text = getattr(module, "__file__", None)
        if type(origin_text) is not str:
            raise AssertionError(f"module lacks a regular origin: {name}")
        origin = Path(origin_text).resolve(strict=True)
        _regular_real_file(origin)
        if not _within(origin, package_root):
            raise AssertionError(f"module origin escapes installed package: {name}")
        if any(_within(origin, root) for root in forbidden):
            raise AssertionError(f"module origin reaches forbidden source: {name}")
    checks += len(imported) + 1

    root_exports = tuple(imported["ebu_framework"].__all__)
    expected_i9_exports = tuple(i9["accepted_surface"]["root_exports"]["values"])
    if root_exports[:444] != expected_i9_exports:
        raise AssertionError("I-9 root-export prefix mismatch")
    if root_exports[444:] != tuple(clcd["root_export_suffix"]):
        raise AssertionError("CLCD root-export suffix mismatch")
    if (len(root_exports), len(set(root_exports)), *_digest(root_exports)) != (
        471,
        471,
        10526,
        "804ff437fc0adfdb8980e976c099814c2ece2142d4e40ade3a577b3e14fc1bc9",
    ):
        raise AssertionError("whole installed root-export projection mismatch")
    checks += 3

    failure_type = imported["ebu_framework.errors"].FailureCode
    failures = tuple(item.value for item in failure_type)
    expected_i9_failures = tuple(i9["accepted_surface"]["failure_codes"]["values"])
    if failures[:280] != expected_i9_failures:
        raise AssertionError("I-9 FailureCode prefix mismatch")
    if failures[280:] != tuple(clcd["failure_suffix"]):
        raise AssertionError("CLCD FailureCode suffix mismatch")
    if (len(failures), len(set(failures)), *_digest(failures)) != (
        294,
        294,
        7945,
        "bde7371b5d4fd34a537e1d7137ca98c79b5e22d4b1e6678b295da6f321179a2c",
    ):
        raise AssertionError("whole installed FailureCode projection mismatch")
    checks += 3

    signature_rows = [tuple(row) for row in i9["accepted_surface"]["public_signature_rows"]["rows"]]
    signature_rows.append(
        (
            "correction_protocol",
            clcd["public_callables"][0][0],
            clcd["public_callables"][0][1],
        )
    )
    signature_rows.extend(
        ("correction_diagnostics", row[0], row[1])
        for row in clcd["public_callables"][1:]
    )
    if len(signature_rows) != 162 or len(set(signature_rows)) != 162:
        raise AssertionError("accepted signature row inventory mismatch")
    installed_functions: dict[tuple[str, str], ast.FunctionDef] = {}
    for owner in {row[0] for row in signature_rows}:
        module_path = Path(imported[f"ebu_framework.{owner}"].__file__).resolve(strict=True)
        tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
        installed_functions.update(
            ((owner, node.name), node)
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        )
    if set(installed_functions) != {(row[0], row[1]) for row in signature_rows}:
        raise AssertionError("installed public-function inventory mismatch")
    for owner, name, expected in signature_rows:
        value = getattr(imported[f"ebu_framework.{owner}"], name)
        if not callable(value):
            raise AssertionError(f"accepted callable is not callable: {owner}.{name}")
        actual_node = installed_functions[(owner, name)]
        expected_node = ast.parse(f"def _expected{expected}:\n    pass\n").body[0]
        if not isinstance(expected_node, ast.FunctionDef) or (
            ast.dump(actual_node.args, include_attributes=False)
            != ast.dump(expected_node.args, include_attributes=False)
            or ast.dump(actual_node.returns, include_attributes=False)
            != ast.dump(expected_node.returns, include_attributes=False)
        ):
            raise AssertionError(f"signature mismatch: {owner}.{name}")
    checks += len(signature_rows) + 1

    for site in resolved_sys_path:
        if not site.is_dir() or not _within(site, environment):
            continue
        for pth in site.glob("*.pth"):
            content = pth.read_text(encoding="utf-8", errors="strict")
            if "ebu_framework" in content or any(str(root) in content for root in forbidden):
                raise AssertionError(f"source-path injection detected: {pth}")
    checks += 1

    print(
        json.dumps(
            {
                "evidence_class": "STATIC_OR_SYNTHETIC_IMPLEMENTATION_TEST",
                "completed_checks": checks,
                "distribution": "ebu-framework",
                "version": distribution.version,
                "module_count": len(module_names),
                "root_export_count": len(root_exports),
                "failure_code_count": len(failures),
                "public_signature_count": len(signature_rows),
                "package_root": str(package_root),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
