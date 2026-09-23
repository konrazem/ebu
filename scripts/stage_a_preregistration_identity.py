"""Cryptographic identity of the frozen Stage-A preregistration.

Reads the document, removes the identity line so the digest is stable under
its own recording, and prints the SHA-256 of what remains. Executes no model
code, advances no state and generates no evidence.

Run: python3 scripts/stage_a_preregistration_identity.py
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys

DOCUMENT = "DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md"
MARKER = re.compile(r"^PREREGISTRATION_SHA256 = .*$", re.MULTILINE)


def digest(text: str) -> str:
    stripped = MARKER.sub("PREREGISTRATION_SHA256 = <recorded below>", text)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()


def main() -> int:
    path = pathlib.Path(__file__).resolve().parent.parent / DOCUMENT
    text = path.read_text(encoding="utf-8")
    current = digest(text)
    recorded = MARKER.search(text)
    print(f"{DOCUMENT}")
    print(f"  computed  {current}")
    if recorded and "<recorded below>" not in recorded.group(0):
        stated = recorded.group(0).split("=", 1)[1].strip()
        print(f"  recorded  {stated}")
        if stated != current:
            print("  MISMATCH: the document changed after it was frozen")
            return 1
        print("  MATCH")
    else:
        print("  recorded  (none yet)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
