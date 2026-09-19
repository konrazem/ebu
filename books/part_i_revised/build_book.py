"""Render the revised textbook only. Does not import or execute EBU models."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
build = ROOT / 'build'
build.mkdir(exist_ok=True)
env = dict(os.environ, SOURCE_DATE_EPOCH='1789776000')
cmd = ['/opt/homebrew/bin/tectonic', '--untrusted', '-Z', 'deterministic-mode',
       '--keep-logs', '--keep-intermediates', '--outdir', str(build), str(ROOT/'book.tex')]
if '--offline' in sys.argv:
    cmd.insert(1,'--only-cached')
result = subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(build/'build_console.log').write_text(result.stdout)
print(result.stdout)
result.check_returncode()
destination=REPO/'output/pdf/EBP_Book_Part_I_Revised_Gaussian_Explanatory_Edition.pdf'
destination.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(build/'book.pdf',destination)
print(destination)
