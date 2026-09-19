"""Rebuild book artifacts only and record the actual byte comparison."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
paths = [REPO / f'output/pdf/EBP_Book_Part_{p}_Revised_Gaussian_Explanatory_Edition.pdf'
         for p in ('I','II','III')]
def hashes():
    return {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before = hashes()
subprocess.run([sys.executable, str(REPO/'books/part_i_revised/build_book.py'), '--offline'], check=True)
subprocess.run([sys.executable, str(ROOT/'build_books.py')], check=True)
after = hashes()
record = {'before':before, 'after':after, 'byte_identical':before == after,
          'scope':'PDF generation only; no scientific execution'}
(ROOT/'review/repeat_build.json').write_text(json.dumps(record,indent=2)+'\n')
assert before == after, 'Repeat build differs; inspect and rerender before delivery'
print('All three final PDFs reproduced byte-identically.')
