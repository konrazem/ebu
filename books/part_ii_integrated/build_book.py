"""Offline manuscript rendering, preserving explicitly labelled source readings.

No scientific implementation is imported or executed. Original source PDFs are
read-only. Generated style, reading PDFs and TeX include list are build artifacts.
"""
from pathlib import Path
import hashlib
import io
import json
import os
import shutil
import subprocess
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
BUILD=ROOT/'build'
HASHES={
 'II':'c36e3fad562455808775a3470b8c270faf089b2843dbe17b03635a31e1179095',
 'III':'0ab9b352c0464c8a15bd603845c8f8aa3d71b06d470e12ea1b5e393cef154019'}

def escape(s):
 return s.replace('&',r'\&').replace('_',r'\_').replace('%',r'\%')

def main():
 BUILD.mkdir(exist_ok=True)
 (ROOT/'review').mkdir(exist_ok=True)
 specs=json.loads((ROOT/'readings.json').read_text())
 readers={}; geometries={}; heads={}
 for part,expected in HASHES.items():
  path=Path(f'/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_{part}_Unified_Explanatory_Edition.pdf')
  assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
  readers[part]=PdfReader(path); geometries[part]=pdfplumber.open(path)
  heads[part]={}
  for item in readers[part].outline:
   if not isinstance(item,list):
    heads[part][readers[part].get_destination_page_number(item)+1]=item.title
 for spec in specs:
  part=spec['part']; writer=PdfWriter()
  for n in range(spec['first'],spec['last']+1):
   page=readers[part].pages[n-1]
   geometry=geometries[part].pages[n-1]
   b=io.BytesIO(); c=canvas.Canvas(b,pagesize=(450,666),invariant=1)
   # Margin furniture only: retain all original body content and equation labels.
   c.setFillColorRGB(1,1,1);c.rect(0,630,450,36,fill=1,stroke=0)
   c.rect(0,0,450,33,fill=1,stroke=0)
   c.setFont('Helvetica',6.8);c.setFillColor(HexColor('#627786'))
   c.drawString(39,646,f'HISTORICAL READING H{spec["chapter"]} | Original {part}, PDF {n} | Original numbering')
   c.setStrokeColor(HexColor('#627786'));c.setLineWidth(.3);c.line(39,635,411,635)
   if n in heads[part]:
    for label in geometry.search(r'Chapter\s+\d+'):
     c.setFillColorRGB(1,1,1)
     c.rect(label['x0']-50,666-label['bottom']-2,label['x1']-label['x0']+52,label['bottom']-label['top']+4,fill=1,stroke=0)
     c.setFillColor(HexColor('#123F56'));c.setFont('Helvetica-Bold',10)
     c.drawRightString(label['x1'],666-label['bottom']+2,'Source chapter '+label['text'].split()[-1])
    chars=[ch for ch in geometry.chars if ch['size']>20 and ch['top']<300]
    if chars:
     left=min(ch['x0'] for ch in chars);right=max(ch['x1'] for ch in chars)
     top=min(ch['top'] for ch in chars);bottom=max(ch['bottom'] for ch in chars)
     c.setFillColorRGB(1,1,1);c.rect(left-2,666-bottom-2,right-left+4,bottom-top+4,fill=1,stroke=0)
     c.setFont('Helvetica-Bold',18);c.setFillColor(HexColor('#123F56'))
     words=heads[part][n].replace('``','"').replace("''",'"').split()
     lines=[];line=''
     for word in words:
      candidate=(line+' '+word).strip()
      if c.stringWidth(candidate,'Helvetica-Bold',18)>366 and line:
       lines.append(line);line=word
      else:line=candidate
     lines.append(line)
     assert len(lines)*22<=bottom-top+25,(part,n)
     for k,line in enumerate(lines):c.drawString(left,666-top-18-k*22,line)
   c.save();page.merge_page(PdfReader(b).pages[0]);page.pop('/Annots',None)
   writer.add_page(page)
  with (BUILD/f'H{spec["chapter"]}.pdf').open('wb') as f:writer.write(f)
 for g in geometries.values():g.close()
 base=(REPO/'books/part_i_revised/book.tex').read_text().split(r'\begin{document}')[0]
 base='\n'.join(base.splitlines()[1:])
 base=base.replace('Part I -- Physical Intuition and the EBU Idea','Part II -- Mathematics, Implementation and Evidence')
 a=base.index(r'\hypersetup{');b=base.index('\n',a)
 base=base[:a]+r'\hypersetup{colorlinks=true,linkcolor=navy,citecolor=navy,urlcolor=navy,pdfauthor={Konrad Grzyb},pdftitle={The Energy Balance Project, Part II: Mathematics, Implementation and Evidence},pdfsubject={Integrated revised explanatory edition; conditional mathematics and scoped historical evidence}}'+base[b:]
 # Use already-cached graphicx/geometry rather than downloading pdfpages.
 base+='\n'+r'''\newcommand{\historicalpage}[2]{%
 \thispagestyle{sourcepage}%
 \noindent\makebox[\linewidth][c]{\includegraphics[page=#2,height=638bp]{#1}}\par\newpage}
 '''+'\n'
 base+=r'\fancypagestyle{sourcepage}{\fancyhf{}\fancyfoot[C]{\color{slate}\sffamily\fontsize{8}{10}\selectfont\thepage\quad\textbullet\quad Part II -- Historical source reading}\renewcommand{\headrulewidth}{0pt}}'+'\n'
 (BUILD/'style.tex').write_text(base)
 bodies=[]
 for n in range(33,63):
  supplement=ROOT/f'extensions/{n}.tex'
  if supplement.exists():
   manuscript=(ROOT/f'chapters/{n}.tex').read_text()
   markers=[manuscript.rfind(r'\section*{Chapter recap}'),manuscript.rfind(r'\section*{Final synthesis}')]
   pos=max(markers)
   assert pos>=0,f'Missing closing synthesis in {n}'
   (BUILD/f'chapter-{n}.tex').write_text(manuscript[:pos]+supplement.read_text()+'\n'+manuscript[pos:])
   bodies.append(f'\\input{{build/chapter-{n}.tex}}')
  else:bodies.append(f'\\input{{chapters/{n}.tex}}')
  spec=next((s for s in specs if s['chapter']==n),None)
  if spec:
   bodies.extend([
    f'\\section*{{Historical reading H{n}: {escape(spec["title"])}}}',
    f'\\addcontentsline{{toc}}{{section}}{{H{n}: {escape(spec["title"])}}}',
    '\\begin{cautionbox}{Historical model; not Gaussian evidence}',escape(spec['before']),
    f' Original Part {spec["part"]}, PDF pages {spec["first"]}--{spec["last"]}. Internal chapter, section, equation and page references retain their original meaning. The new running folio belongs to this integrated volume.',
    '\\end{cautionbox}',
    '\\paragraph{What to carry forward.}',escape(spec['after']),
    '\\clearpage\\newgeometry{left=0pt,right=0pt,top=0pt,bottom=20bp,nohead,footskip=5bp}',
    '\\begingroup\\setlength{\\headwidth}{\\textwidth}\\setlength{\\topskip}{0pt}\\setlength{\\parskip}{0pt}',
    '\n'.join(f'\\historicalpage{{build/H{n}.pdf}}{{{p}}}' for p in range(1,spec['last']-spec['first']+2)),
    '\\endgroup\\restoregeometry'])
  bridge=ROOT/f'transitions/{n}.tex'
  if bridge.exists():bodies.append(f'\\input{{transitions/{n}.tex}}')
 (BUILD/'chapters.tex').write_text('\n'.join(bodies)+'\n')
 result=subprocess.run(['/opt/homebrew/bin/tectonic','--only-cached','--untrusted','-Z','deterministic-mode',
  '--keep-logs','--keep-intermediates','--outdir',str(BUILD),str(ROOT/'book.tex')],cwd=ROOT,
  env=dict(os.environ,SOURCE_DATE_EPOCH='1789776000'),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (BUILD/'console.log').write_text(result.stdout);print(result.stdout);result.check_returncode()
 out=REPO/'output/pdf/EBP_Book_Part_II_Integrated_Gaussian_Explanatory_Edition.pdf'
 shutil.copyfile(BUILD/'book.pdf',out)
 pages=len(PdfReader(out).pages);historical=sum(s['last']-s['first']+1 for s in specs)
 record={'path':str(out.relative_to(REPO)),'pages':pages,'new_typeset_pages':pages-historical,
  'historical_source_pages':historical,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
  'original_sha256':HASHES,'model_execution':False,'scientific_evidence_created':False}
 (ROOT/'review/build_outputs.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2))

if __name__=='__main__':main()
