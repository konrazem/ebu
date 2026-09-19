"""Offline typesetting and labelled historical-page assembly, never model execution."""
from pathlib import Path
import hashlib
import io
import json
import os
import subprocess
import sys
from pypdf import PdfReader, PdfWriter
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
BUILD = ROOT / 'build'
subprocess.run([sys.executable, str(ROOT/'setup_books.py')], check=True)
inventory = json.loads((ROOT/'review/original_inventory.json').read_text())
specs = {'II': (65,94), 'III': (66,110)}
report = []
for part, (first,last) in specs.items():
 out = BUILD / part
 out.mkdir(exist_ok=True)
 cmd = ['/opt/homebrew/bin/tectonic', '--only-cached', '--untrusted', '-Z',
        'deterministic-mode', '--keep-logs', '--keep-intermediates',
        '--outdir', str(out), str(ROOT/f'part_{part}.tex')]
 result = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ,SOURCE_DATE_EPOCH='1789776000'),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
 (out/'console.log').write_text(result.stdout)
 print(result.stdout)
 result.check_returncode()
 core = PdfReader(out/f'part_{part}.pdf')
 writer = PdfWriter(clone_from=core)
 baseline = next(row for row in inventory if row['part']==part)
 original = PdfReader(baseline['path'])
 original_geometry = pdfplumber.open(baseline['path'])
 headings = {r['original_pdf_page']:r['title'] for r in baseline['outline'] if r['depth']==0}
 archive_root = writer.add_outline_item(f'Historical Appendix H-{part}: original source pages',len(writer.pages))
 for n in range(first,last+1):
  page = original.pages[n-1]
  b = io.BytesIO()
  c = canvas.Canvas(b,pagesize=(450,666),invariant=1)
  if n in headings:
   chars=[ch for ch in original_geometry.pages[n-1].chars if ch['size']>20 and ch['top']<300]
   if chars:
    left=min(ch['x0'] for ch in chars);right=max(ch['x1'] for ch in chars)
    top=min(ch['top'] for ch in chars);bottom=max(ch['bottom'] for ch in chars)
    c.setFillColorRGB(1,1,1)
    c.rect(left-2,666-bottom-2,right-left+4,bottom-top+4,fill=1,stroke=0)
    c.setFont('Helvetica-Bold',18);c.setFillColor(HexColor('#123F56'))
    words=headings[n].replace('``','"').replace("''",'"').split()
    lines=[];line=''
    for word in words:
     candidate=(line+' '+word).strip()
     if c.stringWidth(candidate,'Helvetica-Bold',18)>366 and line:
      lines.append(line);line=word
     else:line=candidate
    lines.append(line)
    assert len(lines)*22 <= bottom-top+25,headings[n]
    for k,line in enumerate(lines):c.drawString(left,666-top-18-k*22,line)
  c.setFont('Helvetica',6.5)
  c.setFillColor(HexColor('#627786'))
  c.drawString(39,656,f'HISTORICAL MODEL - original Part {part}, PDF {n} - not Gaussian evidence')
  c.save()
  page.merge_page(PdfReader(b).pages[0])
  # Old excerpt links can target pages outside the reproduced original range.
  # Preserve their printed references, not misleading copied click targets.
  page.pop('/Annots',None)
  writer.add_page(page)
 original_geometry.close()
 for row in baseline['outline']:
  if row['depth']==0 and first<=row['original_pdf_page']<=last:
   writer.add_outline_item('Original: '+row['title'],len(core.pages)+row['original_pdf_page']-first,parent=archive_root)
 writer.add_metadata({'/Title':f'The Energy Balance Project, Part {part} - Revised Gaussian Explanatory Edition',
                      '/Author':'Konrad Grzyb','/Subject':'Author-review manuscript; conditional mathematics and explicitly historical evidence'})
 destination = REPO/f'output/pdf/EBP_Book_Part_{part}_Revised_Gaussian_Explanatory_Edition.pdf'
 with destination.open('wb') as f:
  writer.write(f)
 report.append({'part':part,'path':str(destination.relative_to(REPO)),
                'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
                'new_edition_pages':len(core.pages),'historical_pages':last-first+1,
                'total_pages':len(writer.pages),'historical_original_pdf_range':[first,last]})
(ROOT/'review/build_outputs.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
