"""Read-only documentation/provenance checks. Never imports EBU model code.

This validates preservation and links, not scientific correctness or runtime
readiness. It launches only read-only Git object queries; no hooks or runners.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def read_json(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=reject_constant)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-external-books", action="store_true",
                        help="also require the three source PDFs at their locked local paths")
    args = parser.parse_args()
    inventory = read_json("local_gaussian_ebu_migration_inventory.json")
    contract = read_json("reconciliation_preservation_contract.json")
    checkpoint = contract["checkpoint"]
    require(checkpoint == inventory["checkpoint"], "Checkpoint disagreement")
    rows = inventory["entries"]
    paths = [row["path"] for row in rows]
    require(len(paths) == len(set(paths)) == 216, "Inventory count/duplicates")
    expected = git("ls-tree", "-r", "--name-only", checkpoint).decode().splitlines()
    require(set(paths) == set(expected), "Inventory does not cover exact checkpoint tree")
    replacements = {row["path"]: row["archive"] for row in contract["replacements"]}
    banners = {row["path"]: row["prefix"].encode() for row in contract["navigation_banners"]}
    newline_only = {row["path"] for row in contract.get("body_normalizations", [])
                    if row["change"] == "one final newline added"}
    require(not set(replacements).intersection(banners), "Overlapping preservation rules")
    for row in rows:
        path = row["path"]
        require(row["category"] in inventory["categories"], f"Unknown category: {path}")
        source = git("show", f"{checkpoint}:{path}")
        require(digest(source) == row["sha256"], f"Wrong checkpoint hash: {path}")
        if path in replacements:
            current = (ROOT / replacements[path]).read_bytes()
        else:
            current = (ROOT / path).read_bytes()
            if path in banners:
                require(current.startswith(banners[path]), f"Changed notice: {path}")
                current = current[len(banners[path]):]
        if path in newline_only:
            require(not source.endswith(b"\n") and current.endswith(b"\n"),
                    f"Undeclared newline state: {path}")
            current = current[:-1]
        require(current == source, f"Unapproved change to checkpoint body: {path}")
    for row in contract["historical_snapshots"]:
        data = (ROOT / row["path"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == row["git_blob"], f"Historical snapshot mismatch: {row['path']}")
    for row in contract["supplied_inputs"]:
        data = (ROOT / row["path"]).read_bytes()
        require(data.endswith(b"\n"), f"Missing declared final newline: {row['path']}")
        require(digest(data[:-1]) == row["original_sha256"],
                f"Supplied input changed beyond final newline: {row['path']}")

    documents = [ROOT / p for p in [
        "README.md", "CURRENT_SCIENTIFIC_AUTHORITY.md", "EBU_FUTURE_BOOKS_STRUCTURE.md",
        "GAUSSIAN_EBU_BASELINE_DECISION.md", "LOCAL_GAUSSIAN_EBU_FRAMEWORK_DECISION.md",
        "LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md",
        "LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md",
        "LOCAL_GAUSSIAN_EBU_MIGRATION_MATRIX.md",
        "LOCAL_GAUSSIAN_EBU_BOOK_SERIES_RECONCILIATION.md",
        "BOOK_I_INTRODUCTION_BLUEPRINT.md", "BOOK_I_GENERATION_HANDOVER.md",
        "BOOK_I_MOTIVATION_SOURCE_REGISTER.md", "docs/history/README.md",
        "docs/programme/sources/README.md",
    ]]
    links = 0
    for document in documents:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            target = target.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            local = document.parent / unquote(parsed.path)
            require(local.exists(), f"Missing local link from {document.name}: {target}")
            links += 1
    if args.check_external_books:
        for row in contract["book_pdfs"]:
            require(digest(Path(row["path"]).read_bytes()) == row["sha256"],
                    f"Book baseline changed: {row['path']}")
    print(f"PASS: {len(rows)} checkpoint paths; {len(banners)} body-preserving notices; "
          f"{len(replacements)} archived replacements; 4 historical snapshots; "
          f"2 supplied inputs; {links} local links across {len(documents)} documents.")
    print("External PDF checks: " + ("3 passed" if args.check_external_books else "not requested"))
    print("Validation class: document parsing, hashing and read-only Git queries only.")
    print("EBU imports: NONE. Model transitions: NONE. Scientific execution: NONE.")


if __name__ == "__main__":
    main()
