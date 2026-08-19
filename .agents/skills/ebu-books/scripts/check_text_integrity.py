#!/usr/bin/env python3
"""Check UTF-8 text and basic Markdown structure without modifying files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
BACKTICK_RE = re.compile(r"`+")


def escaped(text: str, index: int) -> bool:
    slashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        slashes += 1
        index -= 1
    return slashes % 2 == 1


def markdown_issues(text: str) -> list[str]:
    issues: list[str] = []
    fence: tuple[str, int, int] | None = None
    inline: tuple[int, int] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if (
            match
            and fence is None
            and match.group(2).startswith("`")
            and "`" in match.group(3)
        ):
            # A same-line backtick span is inline code, not a valid fence opener.
            match = None
        if match:
            marker = match.group(2)
            marker_char = marker[0]
            marker_length = len(marker)
            remainder = match.group(3)
            if fence is None:
                fence = (marker_char, marker_length, line_number)
                continue
            if (
                marker_char == fence[0]
                and marker_length >= fence[1]
                and not remainder.strip()
            ):
                fence = None
            continue

        if fence is not None:
            continue

        for tick_match in BACKTICK_RE.finditer(line):
            length = len(tick_match.group(0))
            if inline is None:
                if escaped(line, tick_match.start()):
                    continue
                inline = (length, line_number)
            elif length == inline[0]:
                inline = None

    if fence is not None:
        issues.append(f"line {fence[2]}: unclosed {fence[0] * fence[1]} fence")
    if inline is not None:
        issues.append(
            f"line {inline[1]}: unclosed inline-code span with {inline[0]} backtick(s)"
        )
    return issues


def check_file(path: Path, allow_tabs: bool) -> list[str]:
    issues: list[str] = []
    try:
        data = path.read_bytes()
    except OSError as exc:
        return [f"cannot read file: {exc}"]

    if data.startswith(b"\xef\xbb\xbf"):
        issues.append("UTF-8 BOM present")
    if b"\x00" in data:
        issues.append("NUL byte present")
    if b"\r" in data:
        issues.append("CR byte present")

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        issues.append(f"invalid UTF-8 at byte {exc.start}")
        return issues

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            issues.append(f"line {line_number}: trailing space or tab")
        if not allow_tabs and "\t" in line:
            issues.append(f"line {line_number}: tab prohibited")

    if not data.endswith(b"\n"):
        issues.append("missing final newline")
    elif data.endswith(b"\n\n"):
        issues.append("multiple final newlines")

    issues.extend(markdown_issues(text))
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check text files for encoding, whitespace, newline, and basic Markdown defects."
    )
    parser.add_argument(
        "--allow-tabs",
        action="store_true",
        help="allow tab characters while retaining all other checks",
    )
    parser.add_argument("files", nargs="+", metavar="FILE")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failed = False
    for value in args.files:
        path = Path(value)
        issues = check_file(path, allow_tabs=args.allow_tabs)
        if issues:
            failed = True
            print(f"{path}: FAIL")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"{path}: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
