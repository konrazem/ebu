"""Record original-outline coverage honestly; no scientific model execution."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
old=json.loads((ROOT.parent/'parts_ii_iii_revised/review/original_inventory.json').read_text())
readings=json.loads((ROOT/'readings.json').read_text())
routes={
 'II':{12:[33],16:[34],21:[34],25:[36],29:[35],34:[38],38:[37],42:[39],
       47:[39,41,53],54:[42],60:[40],65:[44],72:[44],79:[44],85:[45],95:[45],104:[45],114:[46]},
 'III':{14:[47],19:[57],26:[57],31:[50],37:[49],45:[52],53:[53],60:[55],
        66:[58],71:[58],75:[58],80:[58],86:[58],93:[58],101:[59],111:[60],119:[56],133:[61,62]},
}
rows=[]
for volume in old:
 part=volume['part']; current=[]; parent=''
 for row in volume['outline']:
  if row['depth']==0:
   current=routes[part].get(row['original_pdf_page'],[]);parent=row['title']
  retained=next((s for s in readings if s['part']==part and s['first']<=row['original_pdf_page']<=s['last']),None)
  if retained:
   disposition='Original source page retained in full in a labelled, chapter-integrated historical reading; original scientific meaning retained.'
  elif current:
   disposition='Subject-level revised exposition or explicit domain limitation; not a claim of sentence-by-sentence retention.'
  else:
   disposition='Edition furniture/references replaced in the current edition; original remains preserved.'
  rows.append(dict(row,original_part=part,original_parent=parent,current_chapters=current,
                   reading=('H'+str(retained['chapter'])) if retained else None,disposition=disposition))
(ROOT/'review/source_coverage.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# Original-to-integrated coverage ledger','',
 'Every original outline entry is retained in `source_coverage.json`. The map',
 'provides destinations and preservation status; it does not claim that every',
 'original sentence or numerical example was rewritten. Original PDFs remain intact.','',
 '| Original part / chapter | Original PDF start | Current chapter(s) | Disposition |',
 '|---|---:|---|---|']
for row in rows:
 if row['depth']==0:
  label=row['original_part']+' / '+row['title'].replace('|','/')
  dest=', '.join(map(str,row['current_chapters'])) or 'Front matter / sources'
  status=('Full historical reading '+row['reading']) if row['reading'] else 'Reconstructed / scoped replacement'
  lines.append(f'| {label} | {row["original_pdf_page"]} | {dest} | {status} |')
lines+=['','## Specific preservation and replacement decisions','',
 '- The original threshold potential is explained as a historical family, not retained as the active Gaussian definition.',
 '- Original II PDF 65–113 survives in full: conditional dissipation, finite-step and network certificates, preservation, routes and long-run distinctions.',
 '- Original III PDF 19–132 survives in full, reordered by dependency rather than old part boundaries. The original core implementation, tests, D-series, Gate 1B, service/O14 record, observation and reproduction discussion remain inspectable.',
 '- Original II PDF 114–156 is not reproduced as an active threshold laboratory. Current Chapter 46 reconstructs Gaussian calculations, group/subset cases, routes, finite accounting, a scoped pump-seal repair discussion, eight proof exercises and ten failure diagnostics. Numerical old-potential tables remain in the original rather than being relabelled.',
 '- Original III PDF 133–149 is replaced by Chapters 61–62 and the eight-part roadmap. Institutional, adaptive-infrastructure and cross-domain research remains prospective, with its teaching home in later parts; those proposals are not transformed into completed studies.',
 '- Earlier separate 83/88-page drafts are preserved unchanged. Their old reports describe those artifacts, not this integrated edition.',
 '- Historical internal references point to their original source numbering; the source banner supplies original part/PDF page. Main chapters 33–62 and new folios are continuous.',
 '',f'Inventory: {len(rows)} original outline entries; {sum(s["last"]-s["first"]+1 for s in readings)} original source pages retained in the new volume.','']
(ROOT/'review/SOURCE_COVERAGE.md').write_text('\n'.join(lines))
print(f'{len(rows)} original outline entries mapped; no verbatim-completeness claim.')
