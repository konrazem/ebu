"""Rebuild both delivered books and compare bytes; never execute EBU models."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
paths=[REPO/'output/pdf/EBP_Book_Part_I_Revised_Gaussian_Explanatory_Edition.pdf',
       REPO/'output/pdf/EBP_Book_Part_II_Integrated_Gaussian_Explanatory_Edition.pdf']
def hashes():return {str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes()
for script,args in [(REPO/'books/part_i_revised/build_book.py',['--offline']),(ROOT/'build_book.py',[])]:
 result=subprocess.run([sys.executable,str(script),*args],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 result.check_returncode()
after=hashes()
record={'byte_identical':before==after,'before':before,'after':after,'model_execution':False}
(ROOT/'review/repeat_build.json').write_text(json.dumps(record,indent=2)+'\n')
assert before==after,record
print('Both current book PDFs rebuilt byte-identically; no scientific model executed.')
