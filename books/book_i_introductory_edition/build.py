"""Rebuild this book only. Requires ReportLab and Tectonic; no model imports."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
build = ROOT / 'build'
build.mkdir(exist_ok=True)
subprocess.run([sys.executable, str(ROOT / 'figures.py')], check=True)
renderer = os.environ.get('BOOK_TECTONIC', 'tectonic')
env = dict(os.environ, SOURCE_DATE_EPOCH='1789776000')
args = [renderer, '--untrusted', '-Z', 'deterministic-mode', '--keep-logs',
        '--keep-intermediates', '--makefile-rules', str(build / 'dependencies.mk'),
        '--outdir', str(build), str(ROOT / 'book.tex')]
if '--only-cached' in sys.argv:
    args.insert(1, '--only-cached')
result = subprocess.run(args, cwd=ROOT, env=env, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(build / 'build_console.log').write_text(result.stdout)
print(result.stdout)
result.check_returncode()
staged = build / 'candidate-staged.pdf'
shutil.copyfile(build / 'book.pdf', staged)
os.replace(staged, ROOT / 'why_ebu_book_i_candidate.pdf')
print('Candidate PDF rebuilt successfully.')
