#!/usr/bin/env python3
"""Report repository changes that fall outside an authorized path set."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath


def run_git(repo: Path, *args: str) -> bytes:
    command = ["git", "-C", str(repo), *args]
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise RuntimeError(f"cannot run Git: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Git command failed ({' '.join(args)}): {detail}")
    return completed.stdout


def nul_paths(data: bytes) -> list[str]:
    return sorted(
        path.decode("utf-8", errors="surrogateescape")
        for path in data.split(b"\0")
        if path
    )


def normalize_authorized_path(repo: Path, value: str) -> str:
    candidate = Path(value)
    resolved = (
        candidate.resolve(strict=False)
        if candidate.is_absolute()
        else (repo / candidate).resolve(strict=False)
    )
    try:
        relative = resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"authorized path is outside the repository: {value}") from exc
    normalized = PurePosixPath(relative.as_posix()).as_posix()
    return "." if normalized == "." else normalized.rstrip("/")


def is_authorized(path: str, allowed: list[str]) -> bool:
    normalized = PurePosixPath(path).as_posix()
    return any(
        prefix == "." or normalized == prefix or normalized.startswith(prefix + "/")
        for prefix in allowed
    )


def print_group(label: str, paths: list[str]) -> None:
    print(f"{label}:")
    if not paths:
        print("  (none)")
        return
    for path in paths:
        print(f"  {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report staged, unstaged, untracked, and out-of-scope paths without modifying the repository."
    )
    parser.add_argument("repository", help="path to the Git worktree")
    parser.add_argument("base_revision", help="commit used as the authorized comparison base")
    parser.add_argument(
        "authorized_paths",
        nargs="+",
        metavar="AUTHORIZED_PATH",
        help="repository-relative file or directory permitted to change",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested_repo = Path(args.repository).resolve()

    try:
        root_text = run_git(requested_repo, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        repo = Path(root_text).resolve()
        base_commit = run_git(
            repo,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{args.base_revision}^{{commit}}",
        ).decode("ascii").strip()
        allowed = sorted(
            {normalize_authorized_path(repo, value) for value in args.authorized_paths}
        )
        staged = nul_paths(
            run_git(
                repo,
                "diff",
                "--cached",
                "--no-ext-diff",
                "--no-renames",
                "--name-only",
                "-z",
                "--",
            )
        )
        unstaged = nul_paths(
            run_git(
                repo,
                "diff",
                "--no-ext-diff",
                "--no-renames",
                "--name-only",
                "-z",
                "--",
            )
        )
        untracked = nul_paths(
            run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
        )
        since_base = nul_paths(
            run_git(
                repo,
                "diff",
                "--no-ext-diff",
                "--no-renames",
                "--name-only",
                "-z",
                base_commit,
                "--",
            )
        )
    except (RuntimeError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    changed = sorted(set(since_base) | set(untracked))
    outside = [path for path in changed if not is_authorized(path, allowed)]

    print(f"repository: {repo}")
    print(f"base revision: {args.base_revision} ({base_commit})")
    print_group("authorized paths", allowed)
    print_group("staged paths", staged)
    print_group("unstaged paths", unstaged)
    print_group("untracked paths", untracked)
    print_group("changed paths outside authorized scope", outside)

    if outside:
        print("result: FAIL (out-of-scope changes found)")
        return 1
    print("result: PASS (all changed paths are authorized)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
