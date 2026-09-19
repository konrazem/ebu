"""Extract the author's Part I for editorial comparison; no research imports."""
from pathlib import Path
import hashlib
import json
import subprocess
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
BASE = Path('/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_I_Unified_Explanatory_Edition.pdf')
reader = PdfReader(BASE)
scratch = ROOT / 'build'
scratch.mkdir(exist_ok=True)
pages = [p.extract_text() for p in reader.pages]
(scratch / 'original_full.txt').write_text('\n\n'.join(f'PDF PAGE {i+1}\n{t}' for i,t in enumerate(pages)))
starts = [26,36,51,62,76,86,97,106,117,129,143,152,160,168,180,187,195,206,213,219,226,233,241,251,263,272,293]
for i,(a,b) in enumerate(zip(starts,starts[1:]),1):
    (scratch / f'original_{i:02}.txt').write_text('\n\n'.join(pages[a-1:b-1]))
(scratch/'baseline_identity.json').write_text(json.dumps({'path':str(BASE),'sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'pages':len(pages),'words':sum(len(t.split()) for t in pages),'chapter_starts':starts},indent=2)+'\n')
for n in [1,26,38,63,132,169,206,252]:
    subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-scale-to','1100','-png',str(BASE),str(scratch/f'original_page_{n}')],check=True)
print('Extracted 26 original chapters and rendered eight style controls.')
