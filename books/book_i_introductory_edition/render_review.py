"""Render an immutable snapshot for visual inspection; never inspect model state."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
pdf = ROOT / 'why_ebu_book_i_candidate.pdf'
digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
work = ROOT/'build'
work.mkdir(exist_ok=True)
snapshot = work / f'visual-input-{digest[:12]}.pdf'
shutil.copyfile(pdf, snapshot)
out = ROOT/'review'/'pages'/digest[:12]
out.mkdir(parents=True,exist_ok=True)
config = work/'fonts.conf'
config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">'
                  '<fontconfig><dir>/System/Library/Fonts</dir><cachedir>'
                  +str(work/'fontcache')+'</cachedir></fontconfig>')
env=dict(os.environ, FONTCONFIG_FILE=str(config))
result=subprocess.run(['pdftoppm','-r','100','-png',str(snapshot),str(out/'page')],
                      env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(work/'render_console.log').write_text(result.stdout)
result.check_returncode()
if result.stdout.strip():
    print(result.stdout[:3000])
if hashlib.sha256(pdf.read_bytes()).hexdigest()!=digest:
    raise RuntimeError('Candidate changed during review rendering; discard this review.')
print(json.dumps({'pdf_sha256':digest,'directory':str(out),'images':len(list(out.glob('page-*.png')))}))
