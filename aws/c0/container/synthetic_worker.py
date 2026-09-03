#!/usr/local/bin/python3
"""Inert AWS-C0 event worker with three and only three modes.

The worker accepts no command-line arguments and has no AWS, Docker, project,
harness, third-party, filesystem-output, or network dependency. Its complete
input is the closed AWS_C0_* environment interface. It emits one compact,
key-sorted UTF-8 JSON event per stdout line; the root controller owns durable
payload objects and evidence records.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import unicodedata


MODES = ("SUCCESS", "FAIL_AFTER_CHECKPOINT", "TIMEOUT")
MODE_BY_ATTEMPT_SUFFIX = {
    "-SUCCESS": "SUCCESS",
    "-FAIL-AFTER-CHECKPOINT": "FAIL_AFTER_CHECKPOINT",
    "-TIMEOUT": "TIMEOUT",
}
ATTEMPT_PATTERN = re.compile(
    r"^ATTEMPT-[A-Z0-9-]{1,64}-(SUCCESS|FAIL-AFTER-CHECKPOINT|TIMEOUT)$"
)
POSITIVE_INTEGER_PATTERN = re.compile(r"^[1-9][0-9]*$")
MAX_INTERVAL_SECONDS = 432000
SUCCESS_CHECKPOINT_COUNT = 2


class WorkerRefusal(RuntimeError):
    """Raised when the closed worker input or event contract is invalid."""


def _validate_tree(value: object) -> None:
    if value is None or type(value) in (bool, int):
        return
    if type(value) is str:
        if value != unicodedata.normalize("NFC", value):
            raise WorkerRefusal("non-NFC string")
        return
    if type(value) is list:
        for item in value:
            _validate_tree(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or key != unicodedata.normalize("NFC", key):
                raise WorkerRefusal("non-NFC object key")
            _validate_tree(item)
        return
    raise WorkerRefusal(f"unsupported JSON value: {type(value).__name__}")


def canonical_json_bytes(value: object) -> bytes:
    _validate_tree(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _required_environment(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise WorkerRefusal(f"missing environment input: {name}")
    if value != unicodedata.normalize("NFC", value):
        raise WorkerRefusal(f"non-NFC environment input: {name}")
    return value


def _bounded_positive_environment(name: str) -> int:
    value = _required_environment(name)
    if POSITIVE_INTEGER_PATTERN.fullmatch(value) is None:
        raise WorkerRefusal(f"{name} must be a canonical positive integer")
    parsed = int(value, 10)
    if parsed > MAX_INTERVAL_SECONDS:
        raise WorkerRefusal(f"{name} exceeds the worker interval bound")
    return parsed


def _mode_from_attempt(attempt_id: str) -> str:
    if ATTEMPT_PATTERN.fullmatch(attempt_id) is None:
        raise WorkerRefusal("attempt identity has no exact terminal mode suffix")
    matches = [
        mode
        for suffix, mode in MODE_BY_ATTEMPT_SUFFIX.items()
        if attempt_id.endswith(suffix)
    ]
    if len(matches) != 1:
        raise WorkerRefusal("attempt identity mode suffix is ambiguous")
    return matches[0]


def _emit(event: dict[str, object], expected_fields: set[str]) -> None:
    if set(event) != expected_fields:
        raise WorkerRefusal("worker event field set is not closed")
    raw = canonical_json_bytes(event) + b"\n"
    written = sys.stdout.buffer.write(raw)
    if written != len(raw):
        raise WorkerRefusal("short stdout write")
    sys.stdout.buffer.flush()


def _heartbeat_payload_sha256(
    attempt_id: str, mode: str, sequence: int
) -> str:
    return _sha256(
        {
            "attempt_id": attempt_id,
            "event": "heartbeat",
            "mode": mode,
            "sequence": sequence,
        }
    )


def _checkpoint_payload_sha256(
    attempt_id: str, mode: str, sequence: int, progress_units: int
) -> str:
    return _sha256(
        {
            "attempt_id": attempt_id,
            "event": "checkpoint",
            "mode": mode,
            "sequence": sequence,
            "synthetic_progress_units": progress_units,
        }
    )


def _manifest_sha256(
    attempt_id: str,
    heartbeat_count: int,
    checkpoint_count: int,
) -> str:
    return _sha256(
        {
            "attempt_id": attempt_id,
            "checkpoint_count": checkpoint_count,
            "heartbeat_count": heartbeat_count,
            "mode": "SUCCESS",
            "schema": "aws_c0_synthetic_manifest_payload/v1",
            "synthetic_progress_units": checkpoint_count,
        }
    )


def _burn_unit(previous: bytes, unit: int) -> bytes:
    block = previous + unit.to_bytes(8, "big") + b"AWS-C0-INERT-CHECKSUM-LOAD"
    digest = hashlib.sha256(block).digest()
    for inner in range(128):
        digest = hashlib.sha256(digest + inner.to_bytes(4, "big")).digest()
    return digest


def _emit_terminal(
    *,
    disposition: str,
    failure_phase: str,
    failure_code: str | None,
    last_heartbeat_sequence: int,
    last_checkpoint_sequence: int,
    synthetic_manifest_sha256: str | None,
) -> None:
    _emit(
        {
            "event": "terminal",
            "disposition": disposition,
            "failure_phase": failure_phase,
            "failure_code": failure_code,
            "last_heartbeat_sequence": last_heartbeat_sequence,
            "last_checkpoint_sequence": last_checkpoint_sequence,
            "synthetic_manifest_sha256": synthetic_manifest_sha256,
        },
        {
            "event",
            "disposition",
            "failure_phase",
            "failure_code",
            "last_heartbeat_sequence",
            "last_checkpoint_sequence",
            "synthetic_manifest_sha256",
        },
    )


def run() -> int:
    attempt_id = _required_environment("AWS_C0_ATTEMPT_ID")
    mode = _required_environment("AWS_C0_MODE")
    heartbeat_seconds = _bounded_positive_environment(
        "AWS_C0_HEARTBEAT_SECONDS"
    )
    checkpoint_seconds = _bounded_positive_environment(
        "AWS_C0_CHECKPOINT_SECONDS"
    )
    if mode not in MODES or mode != _mode_from_attempt(attempt_id):
        raise WorkerRefusal("mode differs from the exact attempt suffix")

    start = time.monotonic()
    next_heartbeat = start
    next_checkpoint = start
    heartbeat_sequence = 0
    checkpoint_sequence = 0
    load_unit = 0
    load_chain = hashlib.sha256(attempt_id.encode("ascii")).digest()

    while True:
        load_chain = _burn_unit(load_chain, load_unit)
        load_unit += 1
        now = time.monotonic()

        while now >= next_heartbeat:
            _emit(
                {
                    "event": "heartbeat",
                    "sequence": heartbeat_sequence,
                    "monotonic_nanoseconds": time.monotonic_ns(),
                    "payload_sha256": _heartbeat_payload_sha256(
                        attempt_id, mode, heartbeat_sequence
                    ),
                },
                {
                    "event",
                    "sequence",
                    "monotonic_nanoseconds",
                    "payload_sha256",
                },
            )
            heartbeat_sequence += 1
            next_heartbeat += heartbeat_seconds

        while now >= next_checkpoint:
            progress_units = checkpoint_sequence + 1
            _emit(
                {
                    "event": "checkpoint",
                    "sequence": checkpoint_sequence,
                    "synthetic_progress_units": progress_units,
                    "payload_sha256": _checkpoint_payload_sha256(
                        attempt_id, mode, checkpoint_sequence, progress_units
                    ),
                },
                {
                    "event",
                    "sequence",
                    "synthetic_progress_units",
                    "payload_sha256",
                },
            )
            checkpoint_sequence += 1
            next_checkpoint += checkpoint_seconds

            if mode == "FAIL_AFTER_CHECKPOINT":
                _emit_terminal(
                    disposition="AWS_C0_SYNTHETIC_FAIL",
                    failure_phase="WORKER",
                    failure_code="DECLARED_FAIL_AFTER_CHECKPOINT",
                    last_heartbeat_sequence=heartbeat_sequence - 1,
                    last_checkpoint_sequence=checkpoint_sequence - 1,
                    synthetic_manifest_sha256=None,
                )
                return 23

            if mode == "SUCCESS" and checkpoint_sequence == SUCCESS_CHECKPOINT_COUNT:
                _emit_terminal(
                    disposition="AWS_C0_SYNTHETIC_PASS",
                    failure_phase="NONE",
                    failure_code=None,
                    last_heartbeat_sequence=heartbeat_sequence - 1,
                    last_checkpoint_sequence=checkpoint_sequence - 1,
                    synthetic_manifest_sha256=_manifest_sha256(
                        attempt_id, heartbeat_sequence, checkpoint_sequence
                    ),
                )
                return 0

        time.sleep(0.05)


def main() -> int:
    if len(sys.argv) != 1:
        print("AWS_C0_WORKER_REFUSED: command-line arguments are forbidden", file=sys.stderr)
        return 64
    try:
        return run()
    except (BrokenPipeError, OSError, WorkerRefusal, ValueError) as exc:
        print(f"AWS_C0_WORKER_REFUSED: {exc}", file=sys.stderr)
        return 64


if __name__ == "__main__":
    raise SystemExit(main())
