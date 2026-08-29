#!/usr/bin/env python3
"""Build the deterministic, standard-library-only Stage E harness zipapp."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath


AUTHORITY_INPUTS = (
    "STAGE_D_SCIENTIFIC_VALIDATION_AUTHORITY.md",
    "stage_d_scientific_validation_contract.json",
    "stage_d_scientific_validation_evidence_schema.json",
    "stage_d_scientific_validation_master_matrix.json",
    "stage_d_scientific_validation_predecessor_manifest.json",
    "stage_d_scientific_validation_validation_contract.json",
    "STAGE_D_COMPLETION_ORIENTED_CONTINUATION_AUTHORITY_AMENDMENT.md",
    "stage_d_completion_oriented_continuation_contract.json",
    "stage_d_completion_oriented_continuation_evidence_schema.json",
    "stage_d_completion_oriented_continuation_predecessor_manifest.json",
    "stage_d_completion_oriented_continuation_validation_contract.json",
    "STAGE_E_SCIENTIFIC_HARNESS_AUTHORITY.md",
    "stage_e_scientific_harness_contract.json",
    "stage_e_scientific_harness_evidence_schema.json",
    "stage_e_scientific_harness_implementation_path_manifest.json",
    "stage_e_scientific_harness_predecessor_manifest.json",
    "stage_e_scientific_harness_validation_contract.json",
    "STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_AMENDMENT.md",
    "stage_d_dynamic_growth_campaign_contract.json",
    "stage_d_dynamic_growth_campaign_evidence_schema.json",
    "stage_d_dynamic_growth_campaign_predecessor_manifest.json",
    "stage_d_dynamic_growth_campaign_validation_contract.json",
    "STAGE_E_DYNAMIC_GROWTH_HARNESS_RECONCILIATION_AUTHORITY_AMENDMENT.md",
    "stage_e_dynamic_growth_harness_reconciliation_contract.json",
    "stage_e_dynamic_growth_harness_reconciliation_evidence_schema.json",
    "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json",
    "stage_e_dynamic_growth_harness_reconciliation_predecessor_manifest.json",
    "stage_e_dynamic_growth_harness_reconciliation_validation_contract.json",
)

ROOT_MAIN = b"from stage_e_harness.__main__ import main\nraise SystemExit(main())\n"


class BuildRefusal(RuntimeError):
    pass


def _strict_manifest(path: Path) -> dict:
    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BuildRefusal(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise BuildRefusal(f"floating JSON number forbidden: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate, parse_float=reject_float, parse_constant=reject_float)


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _safe_member(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not name or "\\" in name or "\x00" in name:
        raise BuildRefusal(f"unsafe zip member: {name}")


def _zip_info(name: str) -> zipfile.ZipInfo:
    _safe_member(name)
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.flag_bits = 0x800
    return info


def source_members(source: Path) -> list[str]:
    manifest = _strict_manifest(source / "stage_e_dynamic_growth_harness_reconciliation_implementation_path_manifest.json")
    paths = manifest["prospective_harness_implementation"]["new_paths"]
    members = [path for path in paths if path.startswith("stage_e_harness/") and path.endswith(".py")]
    if len(members) != 34 or len(set(members)) != 34:
        raise BuildRefusal("harness source-member closure mismatch")
    return members


def build(source: Path, output: Path, *, perturbation: str) -> dict[str, object]:
    members: dict[str, bytes] = {"__main__.py": ROOT_MAIN}
    for path in source_members(source):
        members[path] = (source / path).read_bytes()
    identities = []
    for path in AUTHORITY_INPUTS:
        data = (source / path).read_bytes()
        member = f"stage_e_harness/authority/{path}"
        members[member] = data
        identities.append({"path": path, "byte_count": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    index = {"schema": "stage_e_embedded_authority_index/v1", "authority_files": identities}
    members["stage_e_harness/authority/index.json"] = _canonical(index)
    ordered_names = sorted(members, key=lambda value: value.encode("utf-8"))
    # Exercise perturbed source discovery without changing the mandated archive order.
    discovered = list(reversed(ordered_names)) if perturbation == "reverse" else list(ordered_names)
    if perturbation == "evens-odds":
        discovered = ordered_names[::2] + ordered_names[1::2]
    if set(discovered) != set(ordered_names):
        raise BuildRefusal("perturbed discovery changed member set")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for name in ordered_names:
            archive.writestr(_zip_info(name), members[name])
    data = output.read_bytes()
    return {
        "path": output.name,
        "byte_count": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "member_count": len(ordered_names),
        "source_member_count": len(source_members(source)),
        "authority_member_count": len(AUTHORITY_INPUTS),
        "perturbation": perturbation,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--perturbation", choices=("canonical", "reverse", "evens-odds"), default="canonical")
    args = parser.parse_args()
    result = build(args.source.resolve(), args.output.resolve(), perturbation=args.perturbation)
    print(_canonical(result).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
