"""Prepare book-only layout and original-PDF provenance; no model imports."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
BUILD = ROOT / 'build'
BUILD.mkdir(exist_ok=True)
(ROOT / 'review').mkdir(exist_ok=True)
base = (REPO / 'books/part_i_revised/book.tex').read_text().split('\\begin{document}')[0]
base = '\n'.join(base.splitlines()[1:])
base = base.replace('Part I -- Physical Intuition and the EBU Idea', '\\VolumeFooter')
start = base.index('\\hypersetup{')
end = base.index('\n', start)
base = base[:start] + '\\hypersetup{colorlinks=true,linkcolor=navy,citecolor=navy,urlcolor=navy,pdfauthor={Konrad Grzyb},pdfsubject={Revised Gaussian explanatory edition; author-review manuscript}}' + base[end:]
(BUILD / 'style.tex').write_text(base)
specs = {
 'II': ('Mathematical Structure and Proof', 33, 46,
        'c36e3fad562455808775a3470b8c270faf089b2843dbe17b03635a31e1179095'),
 'III': ('Implementation, Preservation and Evidence', 47, 60,
         '0ab9b352c0464c8a15bd603845c8f8aa3d71b06d470e12ea1b5e393cef154019'),
}
records = []
for part, (title, first, last, expected) in specs.items():
 p = Path(f'/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_{part}_Unified_Explanatory_Edition.pdf')
 actual = hashlib.sha256(p.read_bytes()).hexdigest()
 assert actual == expected
 r = PdfReader(p)
 rows = []
 def walk(items, depth=0):
  for item in items:
   if isinstance(item, list):
    walk(item, depth+1)
   else:
    rows.append({'title': item.title, 'depth': depth,
                 'original_pdf_page': r.get_destination_page_number(item)+1})
 walk(r.outline)
 (BUILD / f'original_{part}.txt').write_text('\n'.join(
     f'\n[PDF PAGE {i}]\n{p.extract_text()}' for i,p in enumerate(r.pages,1)))
 records.append({'part': part, 'path': str(p), 'sha256': actual,
                 'pages': len(r.pages), 'outline': rows})
 inputs = '\n'.join(f'\\input{{{part}/{n}.tex}}' for n in range(first,last+1))
 book = (f'\\documentclass[11pt,twoside,openany]{{book}}\n'
         f'\\newcommand{{\\VolumeFooter}}{{Part {part} -- {title}}}\n'
         '\\input{build/style.tex}\n'
         f'\\hypersetup{{pdftitle={{The Energy Balance Project, Part {part}: {title} -- Revised Gaussian Edition}}}}\n'
         '\\begin{document}\n\\frontmatter\n'
         f'\\input{{{part}/frontmatter.tex}}\n\\tableofcontents\n'
         f'\\mainmatter\n\\setcounter{{chapter}}{{{first-1}}}\n{inputs}\n'
         '\\backmatter\n\\input{sources.tex}\n'
         f'\\input{{{part}/historical_intro.tex}}\n\\end{{document}}\n')
 (ROOT / f'part_{part}.tex').write_text(book)
(ROOT / 'review/original_inventory.json').write_text(json.dumps(records,indent=2)+'\n')
print('Two original PDFs verified; editable layout prepared from the Book I style.')
