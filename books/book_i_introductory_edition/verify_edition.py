"""Read-only provenance, manuscript, PDF-structure and scope checks for the book."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from collections import Counter
from pypdf import PdfReader
import pdfplumber

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
checks=[]
def check(name, condition, detail=None):
    checks.append({'check':name,'passed':bool(condition),'detail':detail})
    if not condition: raise AssertionError(name+': '+str(detail))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,text=True).strip()
locks=json.loads((ROOT/'source_locks.json').read_text())
check('HEAD unchanged',git('rev-parse','HEAD')==locks['starting_head'],git('rev-parse','HEAD'))
check('branch unchanged',git('branch','--show-current')==locks['branch'],git('branch','--show-current'))
check('tracked files unchanged',git('diff','HEAD','--name-only')=='')
check('index unchanged',git('diff','--cached','--name-only')=='')
untracked=git('ls-files','--others','--exclude-standard').splitlines()
check('all new nonignored paths within authorized edition',all(p.startswith('books/book_i_introductory_edition/') for p in untracked),len(untracked))
for src in locks['documents']:
    check('locked source: '+src['path'],digest(REPO/src['path'])==src['sha256'],src['sha256'])
for src in locks['preserved_pdfs']:
    p=Path(src['path']);check('preserved PDF: '+p.name,digest(p)==src['sha256'],src['sha256'])
    check('preserved page count: '+p.name,len(PdfReader(p).pages)==src['pages'],src['pages'])
base=next(Path(v['path']) for v in locks['preserved_pdfs'] if 'Part_I_' in v['path'])
r=PdfReader(base);outline=[]
def walk(items,level=0):
    for item in items:
        if isinstance(item,list):walk(item,level+1)
        else:outline.append((level,item.title,r.get_destination_page_number(item)+1))
walk(r.outline)
inv=json.loads((ROOT/'baseline_section_inventory.json').read_text())
check('complete ordered baseline section inventory',outline==[(v['level'],v['title'],v['pdf_page_start']) for v in inv],len(outline))
check('every inventory disposition is declared',all(v['disposition'] in {'retained and rewritten','rewritten','condensed','relocated','omitted from new spine'} and v['new_home'] and v['reason'] for v in inv))
rows=[x for x in (ROOT/'content_disposition.md').read_text().splitlines() if x.startswith('| ')][1:]
check('markdown disposition has one row per section',len(rows)==len(inv),len(rows))
chapters=sorted((ROOT/'manuscript').glob('[0-9][0-9].tex'))
check('18 complete numbered chapters',len(chapters)==18 and all(len(p.read_text())>2000 for p in chapters))
sources=[ROOT/'book.tex',*sorted((ROOT/'manuscript').glob('*.tex'))]
tex='\n'.join(p.read_text() for p in sources)
labels=re.findall(r'\\label\{([^}]+)\}',tex)
refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',tex)
check('labels unique',len(labels)==len(set(labels)),len(labels))
check('all cross-references resolve in sources',set(refs)<=set(labels),sorted(set(refs)-set(labels)))
bib=set(re.findall(r'\\bibitem\[[^]]+\]\{([^}]+)\}',tex))
cites={k for group in re.findall(r'\\cite\{([^}]+)\}',tex) for k in group.split(',')}
check('all citations have bibliography entries',cites<=bib,{'citations':len(cites),'entries':len(bib)})
figs=re.findall(r'\\illustration\{([^}]+)\}',tex)
check('six complete figure references',len(figs)==6 and all((ROOT/'figures'/(f+'.pdf')).exists() for f in figs),figs)
log=(ROOT/'build/book.log').read_text()
problems=re.findall(r'(?im)^.*(?:overfull|underfull|undefined references|missing character|LaTeX Warning|Package \S+ Warning|^!|Error:).*$' ,log)
check('final TeX log has no warnings/errors',not problems,problems)
for p in ROOT.rglob('*'):
    if not p.is_file() or 'build' in p.relative_to(ROOT).parts or 'pages' in p.relative_to(ROOT).parts or p.suffix not in {'.tex','.md','.py','.json'}:continue
    s=p.read_text()
    check('no trailing whitespace: '+str(p.relative_to(ROOT)),not any(line.rstrip()!=line for line in s.splitlines()))
pdf=ROOT/'why_ebu_book_i_candidate.pdf';reader=PdfReader(pdf)
texts=[p.extract_text() for p in reader.pages]
check('no blank PDF pages',all(len(t.strip())>100 for t in texts))
check('no unresolved PDF reference or replacement glyph',all('??' not in t and '\ufffd' not in t for t in texts))
page_records=[]
with pdfplumber.open(pdf) as parsed:
    for i,p in enumerate(parsed.pages):
        bad=[c['text'] for c in p.chars if c['x0'] < -0.5 or c['x1']>p.width+.5 or c['top']<-.5 or c['bottom']>p.height+.5]
        check('PDF page content within media box: '+str(i+1),not bad,bad)
        page_records.append({'pdf_page':i+1,'printed_label':reader.page_labels[i], 'opening':texts[i][:100].replace('\n',' / '),'characters':len(texts[i])})
check('expected page labels',reader.page_labels[:4]==['i','ii','iii','iv'] and reader.page_labels[4:]==[str(i) for i in range(1,len(reader.pages)-3)])
report={'scope':'Editorial/static inspection only; visual review is separate.', 'passed':True,'checks':checks,'pdf_sha256':digest(pdf),'pdf_pages':len(reader.pages),'page_records':page_records,'disposition_counts':dict(Counter(v['disposition'] for v in inv)),'rendered_word_count_approximate':sum(len(t.split()) for t in texts)}
(ROOT/'review/edition_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'checks','page_records'}}))
print(str(len(checks))+' editorial/provenance checks passed.')
