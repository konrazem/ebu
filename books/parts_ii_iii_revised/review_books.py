"""Read/render the delivered PDFs and write book-only verification records."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
from pypdf import PdfReader
import pdfplumber
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
POPPER='/Users/konrad.grzyb/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm'
FONTCONFIG=REPO/'books/part_i_revised/fontconfig.xml'
rows=json.loads((ROOT/'review/build_outputs.json').read_text())
for row in rows:
 part=row['part'];pdf=REPO/row['path'];r=PdfReader(pdf)
 assert hashlib.sha256(pdf.read_bytes()).hexdigest()==row['sha256']
 texts=[p.extract_text() or '' for p in r.pages]
 assert all(len(t.strip())>10 for t in texts)
 assert all(abs(float(p.mediabox.width)-450)<.05 and abs(float(p.mediabox.height)-666)<.05 for p in r.pages)
 first,last=(33,46) if part=='II' else (47,60)
 chapters=[]
 for n,t in enumerate(texts[:row['new_edition_pages']],1):
  m=re.match(r'\s*Chapter\s+(\d+)\s*\n',t)
  if m:chapters.append({'chapter':int(m.group(1)),'pdf_page':n})
 assert [p['chapter'] for p in chapters]==list(range(first,last+1)),chapters
 source='\n'.join(p.read_text() for p in sorted((ROOT/part).glob('*.tex')))+(ROOT/'sources.tex').read_text()
 labels=re.findall(r'\\label\{([^}]+)\}',source)
 refs=re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',source)
 assert len(labels)==len(set(labels))
 assert not set(refs)-set(labels)
 citations={k for s in re.findall(r'\\cite\{([^}]+)\}',source) for k in s.split(',')}
 bib=set(re.findall(r'\\bibitem\{([^}]+)\}',source))
 assert not citations-bib
 assert not re.search('TODO|FIXME|PLACEHOLDER',source)
 log=(ROOT/f'build/{part}/console.log').read_text()
 assert not re.search(r'Overfull|Missing character|undefined',log,re.I), 'Typesetting defect: '+part
 outside=[]
 with pdfplumber.open(pdf) as doc:
  for n,p in enumerate(doc.pages,1):
   for ch in p.chars:
    if ch['x0']<-.5 or ch['x1']>p.width+.5 or ch['top']<-.5 or ch['bottom']>p.height+.5:
     outside.append([n,ch['text']])
 assert not outside,outside[:15]
 images=ROOT/f'review/pages/{part}'
 images.mkdir(parents=True,exist_ok=True)
 result=subprocess.run([POPPER,'-r','65','-png',str(pdf),str(images/'page')],
    env=dict(os.environ,FONTCONFIG_FILE=str(FONTCONFIG)),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (ROOT/f'build/{part}/render.log').write_text(result.stdout)
 result.check_returncode()
 pages=sorted(images.glob('page-*.png'))
 assert len(pages)==len(r.pages),(len(pages),len(r.pages))
 for start in range(0,len(pages),8):
  sheet=Image.new('RGB',(1660,1260),'#d5dce0');draw=ImageDraw.Draw(sheet)
  for slot,p in enumerate(pages[start:start+8]):
   x=8+(slot%4)*415;y=20+(slot//4)*620
   with Image.open(p) as im:sheet.paste(im.convert('RGB'),(x,y))
   draw.text((x,y-14),f'Part {part} PDF {start+slot+1}',fill='black')
  sheet.save(images/f'sheet-{start//8+1:02}.jpg',quality=90)
 row['chapters']=chapters
 row['checks']=['nonempty pages','original trim','chapter order','references and citations',
                'no overfull/missing glyph warnings','no text outside media boxes','all pages rendered']
(ROOT/'review/artifact_checks.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['part','total_pages','new_edition_pages','historical_pages','sha256']} for r in rows],indent=2))
