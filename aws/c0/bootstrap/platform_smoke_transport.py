#!/usr/bin/env python3
"""Offline preparation and sealing for the user-operated AWS-C0 platform smoke.

This module never imports an AWS SDK and never contacts AWS.  ``prepare`` writes
the exact bytes sent through the public ``AWS-RunShellScript`` document.
``seal`` validates AWS CLI JSON captured by the user after the command and stop.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ACCOUNT = "623609441658"
REGION = "us-east-1"
INSTANCE = "i-048bac00bdb540a4e"
DOCUMENT = "AWS-RunShellScript"
BUCKET = "ebu-stage-f-results-k7m4p2"
IMAGE_MANIFEST_SHA256 = "130f80c15eb32be6d22e47e0b149b81ffa0ff04a6f69eb92bb35a8e683fe3641"
IMAGE_REFERENCE = "ebu/aws-c0-platform-smoke@sha256:" + IMAGE_MANIFEST_SHA256
ATTEMPT = re.compile(r"ATTEMPT-USER-([0-9]{8}T[0-9]{6}Z)-SUCCESS")
COMMAND_ID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
VERSION_ID = re.compile(r"[A-Za-z0-9._+~=/:-]{1,1024}")
TERMINAL_STATUSES = {"Success", "Cancelled", "TimedOut", "Failed"}


class Refusal(ValueError):
    """The proposed or observed smoke material is not the sealed procedure."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json(path: Path) -> Any:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise Refusal(f"JSON object required: {path}")
    return value


def _attempt(value: str) -> str:
    if not isinstance(value, str) or ATTEMPT.fullmatch(value) is None:
        raise Refusal("fresh SUCCESS attempt ID required")
    return value


def _utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise Refusal(f"{label} UTC timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Refusal(f"{label} UTC timestamp required") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise Refusal(f"{label} UTC timestamp required")
    return parsed


def _attempt_utc(attempt_id: str) -> str:
    match = ATTEMPT.fullmatch(_attempt(attempt_id))
    assert match is not None
    parsed = datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return parsed.isoformat(timespec="seconds").replace("+00:00", "Z")


def render_command_script(attempt_id: str) -> bytes:
    attempt_id = _attempt(attempt_id)
    container_name = "ebu-c0-" + attempt_id.lower()
    binding = canonical({
        "account": ACCOUNT,
        "attempt_id": attempt_id,
        "prepared_utc": _attempt_utc(attempt_id),
        "container_execution": True,
        "image_manifest_sha256": IMAGE_MANIFEST_SHA256,
        "image_reference": IMAGE_REFERENCE,
        "instance_id": INSTANCE,
        "region": REGION,
        "schema": "aws_c0_user_operated_platform_smoke_host_binding/v1",
        "scientific_execution": False,
    }).decode("ascii")
    script = f"""#!/bin/sh
set -eu
umask 077
/usr/bin/test \"$(/usr/bin/id -u)\" -eq 0
IMAGE='{IMAGE_REFERENCE}'
ACTUAL=\"$(/usr/bin/docker image inspect --format '{{{{.Id}}}}|{{{{.Os}}}}|{{{{.Architecture}}}}|{{{{.Config.User}}}}|{{{{.Config.WorkingDir}}}}' \"$IMAGE\")\"
/usr/bin/test \"$ACTUAL\" = 'sha256:{IMAGE_MANIFEST_SHA256}|linux|amd64|65534:65534|/work'
/usr/bin/printf '%s\\n' '{binding}'
exec /usr/bin/docker run --rm --pull never --name '{container_name}' --network none --read-only --security-opt no-new-privileges --cap-drop ALL --user 65534:65534 --pids-limit 64 --memory 268435456 --cpus 1 --tmpfs /tmp:rw,noexec,nosuid,size=16777216 --env AWS_C0_ATTEMPT_ID='{attempt_id}' --env AWS_C0_MODE=SUCCESS --env AWS_C0_HEARTBEAT_SECONDS=1 --env AWS_C0_CHECKPOINT_SECONDS=1 \"$IMAGE\"
"""
    raw = script.encode("utf-8")
    if b"\r" in raw or b"AWS-RunShellScript" in raw:
        raise AssertionError("command script construction invariant failed")
    return raw


def build_plan(attempt_id: str) -> dict[str, Any]:
    script = render_command_script(attempt_id)
    result_key = f"rehearsal/aws-c0/user-operated-platform-smoke/{attempt_id}/stdout.jsonl"
    parameters = {"commands": [script.decode("utf-8")], "executionTimeout": ["120"]}
    request = {
        "DocumentName": DOCUMENT,
        "InstanceIds": [INSTANCE],
        "MaxConcurrency": "1",
        "MaxErrors": "0",
        "Parameters": parameters,
        "TimeoutSeconds": 120,
    }
    return {
        "schema": "aws_c0_user_operated_platform_smoke_plan/v1",
        "account": ACCOUNT,
        "region": REGION,
        "instance_id": INSTANCE,
        "attempt_id": attempt_id,
        "prepared_utc": _attempt_utc(attempt_id),
        "document_name": DOCUMENT,
        "result_bucket": BUCKET,
        "result_key": result_key,
        "image_reference": IMAGE_REFERENCE,
        "image_manifest_sha256": IMAGE_MANIFEST_SHA256,
        "command_script_base64": base64.b64encode(script).decode("ascii"),
        "command_script_bytes": len(script),
        "command_script_sha256": digest(script),
        "send_command_request": request,
        "send_command_request_sha256": digest(canonical(request)),
        "maximum_instance_starts": 1,
        "maximum_send_commands": 1,
        "maximum_s3_puts": 1,
        "maximum_s3_exact_version_gets": 1,
        "maximum_running_seconds": 900,
        "maximum_prepare_to_send_seconds": 300,
        "maximum_prepare_to_seal_seconds": 1200,
        "conditional_s3_create_only": True,
        "temporary_private_document_operations": 0,
        "iam_mutations": 0,
        "container_execution": True,
        "scientific_execution": False,
        "final_stopped_receipt_required": True,
    }


def validate_plan(plan: Any, script: bytes) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise Refusal("plan object required")
    expected = build_plan(plan.get("attempt_id"))
    if plan != expected or script != base64.b64decode(expected["command_script_base64"], validate=True):
        raise Refusal("plan or command-script bytes differ from sealed material")
    return expected


def _worker_payload(attempt_id: str, event: str, sequence: int, progress: int | None = None) -> str:
    value: dict[str, Any] = {"attempt_id": attempt_id, "event": event, "mode": "SUCCESS", "sequence": sequence}
    if progress is not None:
        value["synthetic_progress_units"] = progress
    return digest(canonical(value))


def validate_stdout(stdout: str, plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(stdout, str) or not stdout.endswith("\n") or "\r" in stdout:
        raise Refusal("complete LF-framed invocation stdout required")
    try:
        rows = [json.loads(line) for line in stdout.splitlines()]
    except json.JSONDecodeError as exc:
        raise Refusal("invocation stdout contains non-JSON data") from exc
    if len(rows) < 5 or not all(isinstance(row, dict) for row in rows):
        raise Refusal("complete host binding and worker event stream required")
    expected_binding = {
        "schema": "aws_c0_user_operated_platform_smoke_host_binding/v1",
        "account": ACCOUNT,
        "region": REGION,
        "instance_id": INSTANCE,
        "attempt_id": plan["attempt_id"],
        "prepared_utc": plan["prepared_utc"],
        "image_reference": IMAGE_REFERENCE,
        "image_manifest_sha256": IMAGE_MANIFEST_SHA256,
        "container_execution": True,
        "scientific_execution": False,
    }
    if rows[0] != expected_binding:
        raise Refusal("host binding differs from sealed account, Region, instance, attempt, or image")
    events = rows[1:]
    if any(row.get("event") not in {"heartbeat", "checkpoint", "terminal"} for row in events):
        raise Refusal("unknown worker stdout row refused")
    heartbeats = [row for row in events if row.get("event") == "heartbeat"]
    checkpoints = [row for row in events if row.get("event") == "checkpoint"]
    terminals = [row for row in events if row.get("event") == "terminal"]
    if len(terminals) != 1 or events[-1] != terminals[0] or len(checkpoints) != 2 or not heartbeats:
        raise Refusal("SUCCESS known-case event shape is incomplete")
    if events != [heartbeats[0], checkpoints[0], *heartbeats[1:], checkpoints[1], terminals[0]]:
        raise Refusal("SUCCESS known-case event order differs from sealed worker order")
    prior_monotonic = 0
    for sequence, row in enumerate(heartbeats):
        if set(row) != {"event", "sequence", "monotonic_nanoseconds", "payload_sha256"}:
            raise Refusal("heartbeat fields not closed")
        if (row["sequence"] != sequence or type(row["monotonic_nanoseconds"]) is not int
                or row["monotonic_nanoseconds"] <= prior_monotonic):
            raise Refusal("heartbeat sequence or clock invalid")
        prior_monotonic = row["monotonic_nanoseconds"]
        if row["payload_sha256"] != _worker_payload(plan["attempt_id"], "heartbeat", sequence):
            raise Refusal("heartbeat payload identity mismatch")
    for sequence, row in enumerate(checkpoints):
        if set(row) != {"event", "sequence", "synthetic_progress_units", "payload_sha256"}:
            raise Refusal("checkpoint fields not closed")
        if row["sequence"] != sequence or row["synthetic_progress_units"] != sequence + 1:
            raise Refusal("checkpoint sequence invalid")
        if row["payload_sha256"] != _worker_payload(plan["attempt_id"], "checkpoint", sequence, sequence + 1):
            raise Refusal("checkpoint payload identity mismatch")
    manifest = digest(canonical({
        "attempt_id": plan["attempt_id"],
        "checkpoint_count": 2,
        "heartbeat_count": len(heartbeats),
        "mode": "SUCCESS",
        "schema": "aws_c0_synthetic_manifest_payload/v1",
        "synthetic_progress_units": 2,
    }))
    terminal = terminals[0]
    if terminal != {
        "event": "terminal",
        "disposition": "AWS_C0_SYNTHETIC_PASS",
        "failure_phase": "NONE",
        "failure_code": None,
        "last_heartbeat_sequence": len(heartbeats) - 1,
        "last_checkpoint_sequence": 1,
        "synthetic_manifest_sha256": manifest,
    }:
        raise Refusal("terminal SUCCESS evidence mismatch")
    return {"event_count": len(events), "heartbeat_count": len(heartbeats),
            "checkpoint_count": 2, "synthetic_manifest_sha256": manifest,
            "stdout_sha256": digest(stdout.encode("utf-8"))}


def _command_from_send(value: dict[str, Any]) -> dict[str, Any]:
    command = value.get("Command")
    if not isinstance(command, dict):
        raise Refusal("SendCommand response Command object required")
    return command


def _stopped_instance(value: dict[str, Any]) -> dict[str, Any]:
    reservations = value.get("Reservations")
    if not isinstance(reservations, list) or len(reservations) != 1:
        raise Refusal("one stopped-instance reservation required")
    reservation = reservations[0]
    if not isinstance(reservation, dict) or reservation.get("OwnerId") != ACCOUNT:
        raise Refusal("stopped-instance account mismatch")
    instances = reservation.get("Instances")
    if not isinstance(instances, list) or len(instances) != 1:
        raise Refusal("one stopped instance required")
    instance = instances[0]
    if not isinstance(instance, dict) or instance.get("InstanceId") != INSTANCE:
        raise Refusal("stopped-instance identity mismatch")
    if instance.get("InstanceType") != "t3.small" or instance.get("State") != {"Code": 80, "Name": "stopped"}:
        raise Refusal("final retained t3.small is not stopped")
    return {"instance_id": INSTANCE, "instance_type": "t3.small", "state": "stopped", "state_code": 80}


def _s3_receipts(*, plan: dict[str, Any], uploaded: bytes, upload: dict[str, Any],
                 retrieved: bytes, retrieval: dict[str, Any], invocation_stdout: str) -> dict[str, Any]:
    expected = invocation_stdout.encode("utf-8")
    if uploaded != expected:
        raise Refusal("uploaded object bytes differ from invocation stdout")
    if retrieved != uploaded:
        raise Refusal("exact-version retrieval bytes differ from uploaded object")
    object_sha256 = digest(uploaded)
    checksum = base64.b64encode(bytes.fromhex(object_sha256)).decode("ascii")
    version_id = upload.get("VersionId")
    if (not isinstance(version_id, str) or VERSION_ID.fullmatch(version_id) is None
            or version_id == "null"):
        raise Refusal("returned non-null S3 VersionId required")
    if upload.get("ChecksumSHA256") != checksum or not isinstance(upload.get("ETag"), str) or not upload["ETag"]:
        raise Refusal("upload receipt checksum or ETag mismatch")
    if retrieval.get("VersionId") != version_id:
        raise Refusal("retrieval receipt does not bind returned VersionId")
    if retrieval.get("ContentLength") != len(uploaded) or retrieval.get("ChecksumSHA256") != checksum:
        raise Refusal("retrieval receipt length or checksum mismatch")
    if retrieval.get("Metadata") != {"sha256": object_sha256}:
        raise Refusal("retrieval receipt SHA-256 metadata mismatch")
    if not isinstance(retrieval.get("ETag"), str) or not retrieval["ETag"]:
        raise Refusal("retrieval receipt ETag required")
    return {
        "bucket": plan["result_bucket"],
        "key": plan["result_key"],
        "version_id": version_id,
        "bytes": len(uploaded),
        "sha256": object_sha256,
        "checksum_sha256_base64": checksum,
        "upload_request": {
            "Bucket": plan["result_bucket"], "Key": plan["result_key"],
            "BodyBytes": len(uploaded), "BodySha256": object_sha256,
            "ChecksumAlgorithm": "SHA256", "ChecksumSHA256": checksum,
            "ContentType": "application/x-ndjson", "IfNoneMatch": "*",
            "Metadata": {"sha256": object_sha256}, "ExpectedBucketOwner": ACCOUNT,
        },
        "retrieval_request": {
            "Bucket": plan["result_bucket"], "Key": plan["result_key"],
            "VersionId": version_id, "ChecksumMode": "ENABLED",
            "ExpectedBucketOwner": ACCOUNT,
        },
        "exact_version_retrieval_verified": True,
    }


def seal_evidence(*, plan: dict[str, Any], script: bytes, caller: dict[str, Any],
                  send: dict[str, Any], invocation: dict[str, Any], stopped: dict[str, Any],
                  uploaded: bytes, upload: dict[str, Any], retrieved: bytes,
                  retrieval: dict[str, Any], observed_utc: str) -> dict[str, Any]:
    validate_plan(plan, script)
    if caller.get("Account") != ACCOUNT or not all(isinstance(caller.get(k), str) and caller[k] for k in ("Arn", "UserId")):
        raise Refusal("authenticated caller does not bind the fixed AWS account")
    command = _command_from_send(send)
    command_id = command.get("CommandId")
    if not isinstance(command_id, str) or COMMAND_ID.fullmatch(command_id) is None:
        raise Refusal("returned SSM command ID required")
    request = plan["send_command_request"]
    for field in ("DocumentName", "InstanceIds", "Parameters", "TimeoutSeconds", "MaxConcurrency", "MaxErrors"):
        if command.get(field) != request[field]:
            raise Refusal(f"SendCommand response does not bind {field}")
    prepared = _utc(plan["prepared_utc"], "prepared")
    requested = _utc(command.get("RequestedDateTime"), "SendCommand requested")
    observed = _utc(observed_utc, "seal observation")
    if not prepared - timedelta(seconds=5) <= requested <= prepared + timedelta(
            seconds=plan["maximum_prepare_to_send_seconds"]):
        raise Refusal("SendCommand is outside the fresh prepared window")
    if invocation.get("CommandId") != command_id or invocation.get("InstanceId") != INSTANCE:
        raise Refusal("invocation does not bind returned command and retained instance")
    if invocation.get("DocumentName") != DOCUMENT or invocation.get("Status") not in TERMINAL_STATUSES:
        raise Refusal("terminal AWS-RunShellScript invocation required")
    execution_start = _utc(invocation.get("ExecutionStartDateTime"), "invocation start")
    execution_end = _utc(invocation.get("ExecutionEndDateTime"), "invocation end")
    if not requested - timedelta(seconds=5) <= execution_start <= execution_end:
        raise Refusal("invocation chronology differs from returned SendCommand")
    if (execution_end - execution_start).total_seconds() > request["TimeoutSeconds"]:
        raise Refusal("invocation exceeds sealed command timeout")
    if not execution_end <= observed <= prepared + timedelta(seconds=plan["maximum_prepare_to_seal_seconds"]):
        raise Refusal("evidence sealing is outside the fresh attempt window")
    stdout = invocation.get("StandardOutputContent")
    stderr = invocation.get("StandardErrorContent")
    response_code = invocation.get("ResponseCode")
    if not isinstance(stdout, str) or not isinstance(stderr, str) or type(response_code) is not int:
        raise Refusal("complete invocation stdout, stderr, and response code required")
    stopped_summary = _stopped_instance(stopped)
    s3_summary = _s3_receipts(plan=plan, uploaded=uploaded, upload=upload,
                              retrieved=retrieved, retrieval=retrieval,
                              invocation_stdout=stdout)
    passed = invocation["Status"] == "Success" and response_code == 0 and stderr == ""
    validation: dict[str, Any] | None = None
    validation_error: str | None = None
    if passed:
        try:
            validation = validate_stdout(stdout, plan)
        except Refusal as exc:
            passed = False
            validation_error = str(exc)
    return {
        "schema": "aws_c0_user_operated_platform_smoke_evidence/v1",
        "disposition": "FORMAL_PLATFORM_SMOKE_PASS" if passed else "FORMAL_PLATFORM_SMOKE_FAIL",
        "account": ACCOUNT,
        "region": REGION,
        "instance_id": INSTANCE,
        "attempt_id": plan["attempt_id"],
        "prepared_utc": plan["prepared_utc"],
        "sealed_utc": observed_utc,
        "fresh_attempt_window_verified": True,
        "image_reference": IMAGE_REFERENCE,
        "image_manifest_sha256": IMAGE_MANIFEST_SHA256,
        "command_script_base64": plan["command_script_base64"],
        "command_script_bytes": plan["command_script_bytes"],
        "command_script_sha256": plan["command_script_sha256"],
        "send_command_request_sha256": plan["send_command_request_sha256"],
        "ssm_command_id": command_id,
        "invocation_status": invocation["Status"],
        "invocation_response_code": response_code,
        "invocation_stdout": stdout,
        "invocation_stdout_sha256": digest(stdout.encode("utf-8")),
        "invocation_stderr": stderr,
        "invocation_stderr_sha256": digest(stderr.encode("utf-8")),
        "worker_validation": validation,
        "worker_validation_error": validation_error,
        "caller_identity": caller,
        "caller_identity_sha256": digest(canonical(caller)),
        "send_command_response": send,
        "send_command_response_sha256": digest(canonical(send)),
        "command_invocation": invocation,
        "command_invocation_sha256": digest(canonical(invocation)),
        "s3_result_object": s3_summary,
        "s3_upload_receipt": upload,
        "s3_upload_receipt_sha256": digest(canonical(upload)),
        "s3_retrieval_receipt": retrieval,
        "s3_retrieval_receipt_sha256": digest(canonical(retrieval)),
        "retrieved_object_sha256": digest(retrieved),
        "final_stopped_instance": stopped_summary,
        "final_stopped_instance_receipt": stopped,
        "final_stopped_instance_receipt_sha256": digest(canonical(stopped)),
        "temporary_private_document_operations": 0,
        "iam_mutations": 0,
        "scientific_execution": False,
        "prior_manual_run_used_as_formal_evidence": False,
    }


def _write_exclusive(path: Path, raw: bytes, mode: int = 0o600) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def prepare(args: argparse.Namespace) -> int:
    target = Path(args.output_dir)
    target.mkdir(mode=0o700, parents=False, exist_ok=False)
    plan = build_plan(args.attempt_id)
    script = base64.b64decode(plan["command_script_base64"], validate=True)
    _write_exclusive(target / "command-script.sh", script, 0o600)
    _write_exclusive(target / "parameters.json", canonical(plan["send_command_request"]["Parameters"]) + b"\n")
    _write_exclusive(target / "plan.json", canonical(plan) + b"\n")
    print(json.dumps({"plan": str(target / "plan.json"), "command_script_sha256": plan["command_script_sha256"]}, sort_keys=True))
    return 0


def seal(args: argparse.Namespace) -> int:
    evidence = seal_evidence(
        plan=_json(Path(args.plan)), script=Path(args.command_script).read_bytes(),
        caller=_json(Path(args.caller_identity)), send=_json(Path(args.send_command)),
        invocation=_json(Path(args.invocation)), stopped=_json(Path(args.stopped_instance)),
        uploaded=Path(args.uploaded_object).read_bytes(), upload=_json(Path(args.upload_receipt)),
        retrieved=Path(args.retrieved_object).read_bytes(), retrieval=_json(Path(args.retrieval_receipt)),
        observed_utc=datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
    )
    output = Path(args.output)
    _write_exclusive(output, canonical(evidence) + b"\n")
    print(json.dumps({"disposition": evidence["disposition"], "evidence": str(output),
                      "evidence_sha256": digest(canonical(evidence))}, sort_keys=True))
    return 0 if evidence["disposition"] == "FORMAL_PLATFORM_SMOKE_PASS" else 2


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    make = sub.add_parser("prepare")
    make.add_argument("--attempt-id", required=True)
    make.add_argument("--output-dir", required=True)
    make.set_defaults(func=prepare)
    close = sub.add_parser("seal")
    close.add_argument("--plan", required=True)
    close.add_argument("--command-script", required=True)
    close.add_argument("--caller-identity", required=True)
    close.add_argument("--send-command", required=True)
    close.add_argument("--invocation", required=True)
    close.add_argument("--stopped-instance", required=True)
    close.add_argument("--uploaded-object", required=True)
    close.add_argument("--upload-receipt", required=True)
    close.add_argument("--retrieved-object", required=True)
    close.add_argument("--retrieval-receipt", required=True)
    close.add_argument("--output", required=True)
    close.set_defaults(func=seal)
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, json.JSONDecodeError, Refusal, ValueError) as exc:
        print(f"REFUSE: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
