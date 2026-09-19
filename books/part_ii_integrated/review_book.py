"""Check and render the current integrated PDF; no scientific execution."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import pdfplumber
from pypdf import PdfReader
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
REVIEW=ROOT/'review'
pdf=REPO/'output/pdf/EBP_Book_Part_II_Integrated_Gaussian_Explanatory_Edition.pdf'
record=json.loads((REVIEW/'build_outputs.json').read_text())
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==record['sha256']
r=PdfReader(pdf);texts=[p.extract_text() or '' for p in r.pages]
assert len(r.pages)>=200
assert not [i+1 for i,t in enumerate(texts) if len(t.strip())<140], 'Blank/sparse page needs review'
assert all(abs(float(p.mediabox.width)-450)<.05 and abs(float(p.mediabox.height)-666)<.05 for p in r.pages)
chapters=[];historical=[]
for n,t in enumerate(texts,1):
 if 'HISTORICAL READING H' in t:
  m=re.search(r'HISTORICAL READING H(\d+)\s*\| Original (II|III), PDF (\d+)',t)
  assert m,(n,t[-200:])
  historical.append({'pdf_page':n,'chapter':int(m.group(1)),'original_part':m.group(2),'original_page':int(m.group(3))})
 else:
  m=re.match(r'\s*Chapter\s+(\d+)\s*\n',t)
  if m:chapters.append({'chapter':int(m.group(1)),'pdf_page':n})
assert [c['chapter'] for c in chapters]==list(range(33,63)),chapters
specs=json.loads((ROOT/'readings.json').read_text())
expected=[(s['chapter'],s['part'],n) for s in specs for n in range(s['first'],s['last']+1)]
assert [(h['chapter'],h['original_part'],h['original_page']) for h in historical]==expected
assert len(historical)==record['historical_source_pages']
texfiles=list((ROOT/'chapters').glob('*.tex'))+list((ROOT/'extensions').glob('*.tex'))+[ROOT/'frontmatter.tex',ROOT/'sources.tex',ROOT/'series.tex']
source='\n'.join(p.read_text() for p in texfiles)
labels=re.findall(r'\\label\{([^}]+)\}',source)
refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',source)
assert len(labels)==len(set(labels))
assert not set(refs)-set(labels),set(refs)-set(labels)
cites={v for c in re.findall(r'\\cite\{([^}]+)\}',source) for v in c.split(',')}
assert not cites-set(re.findall(r'\\bibitem\{([^}]+)\}',source))
assert not re.search(r'TODO|FIXME|PLACEHOLDER|Appendix H-|three books|revised Parts II and III',source)
log=(ROOT/'build/console.log').read_text()
assert not re.search(r'Overfull|undefined|Missing character',log,re.I),log
outside=[]
with pdfplumber.open(pdf) as d:
 for n,p in enumerate(d.pages,1):
  for c in p.chars:
   if c['x0']<-.5 or c['x1']>p.width+.5 or c['top']<-.5 or c['bottom']>p.height+.5:
    outside.append([n,c['text']])
assert not outside,outside[:12]
pages=REVIEW/'pages';sheets=REVIEW/'sheets'
pages.mkdir(exist_ok=True);sheets.mkdir(exist_ok=True)
render=subprocess.run(['/Users/konrad.grzyb/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm',
 '-r','65','-png',str(pdf),str(pages/'page')],
 env=dict(os.environ,FONTCONFIG_FILE=str(REPO/'books/part_i_revised/fontconfig.xml')),
 text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(ROOT/'build/render.log').write_text(render.stdout);render.check_returncode()
images=[pages/f'page-{n:03}.png' for n in range(1,len(r.pages)+1)]
assert all(p.exists() for p in images)
for start in range(0,len(images),8):
 sheet=Image.new('RGB',(1660,1260),'#d5dce0');draw=ImageDraw.Draw(sheet)
 for slot,p in enumerate(images[start:start+8]):
  x=8+(slot%4)*415;y=20+(slot//4)*620
  with Image.open(p) as im:sheet.paste(im.convert('RGB'),(x,y))
  draw.text((x,y-14),f'Part II PDF {start+slot+1}',fill='black')
 sheet.save(sheets/f'sheet-{start//8+1:02}.jpg',quality=88)
record.update(chapters=chapters,historical_pages=historical,rendered_pages=len(images),
 overview_sheets=(len(images)+7)//8,extracted_words=sum(len(t.split()) for t in texts),
 checks=['200-page minimum without blank insertions','continuous chapters 33–62',
  'all source readings at declared positions','no unresolved labels or citations','450x666 trim',
  'no overfull or missing-glyph warnings','no text outside page bounds','all pages rendered'],
 visual_review='Prepared; actual visual coverage recorded separately')
(REVIEW/'artifact_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['pages','new_typeset_pages','historical_source_pages','extracted_words','overview_sheets','sha256']},indent=2))
