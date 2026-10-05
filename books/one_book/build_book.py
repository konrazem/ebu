"""Build only the one-volume manuscript; no EBU model is imported or run."""

from pathlib import Path
import os
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)

tectonic = shutil.which("tectonic") or "/opt/homebrew/bin/tectonic"
command = [
    tectonic,
    "--only-cached",
    "--untrusted",
    "-Z",
    "deterministic-mode",
    "--keep-logs",
    "--keep-intermediates",
    "--outdir",
    str(BUILD),
    str(ROOT / "book.tex"),
]
env = dict(os.environ, SOURCE_DATE_EPOCH="1789776000")
completed = subprocess.run(
    command,
    cwd=ROOT,
    env=env,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    check=False,
)
print(completed.stdout)
completed.check_returncode()

destination = REPO / "output/pdf/EBU_What_an_Economy_Must_Keep_Alive.pdf"
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(BUILD / "book.pdf", destination)
print(destination)
