#!/usr/bin/env python3
"""Produce the local, deterministic material portion of an AWS-C0 deployment packet.

This tool is deliberately offline.  It does not invoke AWS, Docker, or a
scientific workload.  AWS-derived values (the image digest on the retained
host, S3 VersionIds, current cost observations, and the eventual change-set
identity) are reported as unresolved rather than guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import zipfile
from pathlib import Path


ARTIFACTS = (
    ("cloudformation_template", "aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml"),
    ("state_machine_definition", "aws/c0/state-machine/aws-c0.asl.json"),
    ("ssm_document", "aws/c0/ssm/EBU-C0-Start-v1.yaml"),
    ("controller", "aws/c0/controller/ebu_c0_controller.py"),
    ("service_unit", "aws/c0/controller/ebu-c0@.service"),
    ("container_dockerfile", "aws/c0/container/Dockerfile"),
    ("synthetic_worker", "aws/c0/container/synthetic_worker.py"),
)
FINALIZER_SOURCE = "aws/c0/finalizer/finalizer.py"
UNRESOLVED_EXTERNAL_INPUTS = (
    "artifact_bucket_identity",
    "artifact_version_receipts",
    "current_cost_model_observations",
    "expected_change_set_name",
    "retained_host_preloaded_synthetic_image_digest",
)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.flag_bits = 0x800
    return info


def finalizer_zip_bytes(source: bytes) -> bytes:
    """Return the Lambda archive with finalizer.py at the archive root."""
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        archive.writestr(zip_info("finalizer.py"), source)
    return buffer.getvalue()


def build(root: Path) -> dict[str, object]:
    records = []
    for kind, relative_path in ARTIFACTS:
        data = (root / relative_path).read_bytes()
        records.append({"kind": kind, "path": relative_path, "byte_count": len(data), "sha256": sha256(data)})
    source = (root / FINALIZER_SOURCE).read_bytes()
    archive = finalizer_zip_bytes(source)
    records.append({
        "kind": "finalizer_zip", "path": "finalizer.zip", "source_path": FINALIZER_SOURCE,
        "handler": "finalizer.lambda_handler", "byte_count": len(archive), "sha256": sha256(archive),
        "zip_member_order": ["finalizer.py"], "zip_compression": "stored", "zip_timestamp_utc": "1980-01-01T00:00:00Z",
    })
    return {
        "schema": "aws_c0_local_deployment_material_manifest/v1",
        "repository_commit": git(root, "rev-parse", "HEAD"),
        "repository_tree": git(root, "rev-parse", "HEAD^{tree}"),
        "offline_only": True,
        "artifacts": records,
        "unresolved_external_inputs": list(UNRESOLVED_EXTERNAL_INPUTS),
        "refusal": "No AWS-derived identity, receipt, cost observation, image digest, or change-set identity is inferred locally.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = canonical(build(args.root.resolve()))
    if args.output:
        args.output.write_bytes(result + b"\n")
    else:
        print(result.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
