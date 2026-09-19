"""Artifact-only inspection and rendering. No EBU model modules are imported."""
from pathlib import Path
import hashlib
import json
import re
import os
import sys
import subprocess
from pypdf import PdfReader
import pdfplumber
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
PDF = REPO / 'output/pdf/EBP_Book_Part_I_Revised_Gaussian_Explanatory_Edition.pdf'
REVIEW = ROOT / 'review'
PAGES = REVIEW / 'pages'
REVIEW.mkdir(exist_ok=True)
PAGES.mkdir(exist_ok=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

reader = PdfReader(PDF)
assert len(reader.pages) >= 200, 'Latest author brief requires at least 200 substantive pages'
texts = [page.extract_text() or '' for page in reader.pages]
assert all(len(t.strip()) > 15 for t in texts), 'Blank or unextractable page'
assert all(abs(float(p.mediabox.width)-450)<.01 and abs(float(p.mediabox.height)-666)<.01 for p in reader.pages)

chapter_pages = []
for i,t in enumerate(texts,1):
    m=re.search(r'Chapter\s+(\d+)\s*\n',t)
    if m:
        chapter_pages.append({'chapter':int(m.group(1)),'pdf_page':i})
assert [r['chapter'] for r in chapter_pages] == list(range(1,33)), chapter_pages

texfiles=sorted(ROOT.glob('chapters/*.tex'))+[ROOT/'frontmatter.tex',ROOT/'glossary.tex',ROOT/'sources.tex',ROOT/'intro_sources.tex']
manuscript='\n'.join(p.read_text() for p in texfiles)
assert not re.search(r'TODO|FIXME|PLACEHOLDER',manuscript)
assert all(b'\r' not in p.read_bytes() for p in texfiles), 'Unexpected control character'
labels=re.findall(r'\\label\{([^}]+)\}',manuscript)
refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',manuscript)
assert len(labels)==len(set(labels))
assert not set(refs)-set(labels), set(refs)-set(labels)
citations={v for c in re.findall(r'\\cite\{([^}]+)\}',manuscript) for v in c.split(',')}
bibkeys=set(re.findall(r'\\bibitem\{([^}]+)\}',manuscript))
assert not citations-bibkeys
log=(ROOT/'build/build_console.log').read_text()
assert not re.search(r'Overfull|undefined|Missing character',log,re.I), 'Typesetting defect'

outside=[]
with pdfplumber.open(PDF) as doc:
    for n,p in enumerate(doc.pages,1):
        for c in p.chars:
            if c['x0'] < -0.5 or c['x1'] > p.width+.5 or c['top'] < -.5 or c['bottom'] > p.height+.5:
                outside.append([n,c['text'],c['x0'],c['top']])
assert not outside, outside[:20]

baselines={
 'I':'335ed5c6d3541d48a61438e213a8a1148eb196649da83392a4ba0741ce65a4ad',
 'II':'c36e3fad562455808775a3470b8c270faf089b2843dbe17b03635a31e1179095',
 'III':'0ab9b352c0464c8a15bd603845c8f8aa3d71b06d470e12ea1b5e393cef154019',
}
baseline_records=[]
for part,expected in baselines.items():
    p=Path(f'/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_{part}_Unified_Explanatory_Edition.pdf')
    actual=digest(p)
    assert actual==expected, (part,actual)
    baseline_records.append({'part':part,'path':str(p),'sha256':actual})

images=[PAGES/f'page-{n:03}.png' for n in range(1,len(reader.pages)+1)]
if '--reuse-existing-pages' in sys.argv:
    assert all(p.exists() and p.stat().st_mtime >= PDF.stat().st_mtime for p in images), 'Stale render'
else:
    (ROOT/'build/fontcache').mkdir(exist_ok=True)
    render=subprocess.run(['pdftoppm','-r','72','-png',str(PDF),str(PAGES/'page')],
        env=dict(os.environ,FONTCONFIG_FILE=str(ROOT/'fontconfig.xml')),
        text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (ROOT/'build/render_console.log').write_text(render.stdout)
    render.check_returncode()
assert all(p.exists() for p in images)
for start in range(0,len(images),8):
    sheet=Image.new('RGB',(1840,1400),'#d5dce0')
    draw=ImageDraw.Draw(sheet)
    for slot,p in enumerate(images[start:start+8]):
        x=10+(slot%4)*460;y=25+(slot//4)*690
        with Image.open(p) as im:
            sheet.paste(im.convert('RGB'),(x,y))
        draw.text((x,y-16),f'PDF page {start+slot+1}',fill='black')
    sheet.save(PAGES/f'sheet-{start//8+1:02}.jpg',quality=90)

report={
 'artifact':str(PDF.relative_to(REPO)),'sha256':digest(PDF),
 'pages':len(reader.pages),'trim_pdf_points':[450,666],
 'extracted_words':sum(len(t.split()) for t in texts),
 'chapters':chapter_pages,'illustrations':len(list((ROOT/'figures').glob('*.pdf'))),
 'baseline_pdfs_unchanged':baseline_records,
 'checks':['at least 200 pages under the current author brief','32 ordered chapters','nonempty extractable pages',
 '450x666 page size throughout','no missing labels or citations','no duplicate labels',
 'no source placeholders or carriage returns','no overfull or missing-character warnings',
 'no text characters outside media boxes','preserved original PDFs match hashes'],
 'rendered_pages':len(images),'overview_sheets':(len(images)+7)//8,
 'visual_review':'Rendering prepared; human/agent visual-review coverage is recorded separately.',
 'scope':'Artifact checks only; no model state advancement or scientific experiments.',
}
(REVIEW/'artifact_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['pages','extracted_words','sha256','overview_sheets']},indent=2))
