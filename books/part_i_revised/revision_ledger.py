"""Map every original PDF outline entry to the full-length revision disposition."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
OUT=ROOT/'review'
OUT.mkdir(exist_ok=True)
BASE=Path('/Users/konrad.grzyb/Documents/EBU/v4/EBP_Book_Part_I_Unified_Explanatory_Edition.pdf')
r=PdfReader(BASE)
outline=[]
def walk(items,level=0):
    for item in items:
        if isinstance(item,list):
            walk(item,level+1)
        else:
            outline.append({'level':level,'title':item.title,'pdf_page_start':r.get_destination_page_number(item)+1})
walk(r.outline)
prior=json.loads((ROOT.parent/'book_i_introductory_edition/baseline_section_inventory.json').read_text())
assert len(outline)==len(prior)
for fresh,old in zip(outline,prior):
    assert (fresh['title'],fresh['pdf_page_start'])==(old['title'],old['pdf_page_start'])
    fresh['id']=old['id'];fresh['original_chapter']=old['chapter']

mapping={
1:('8; expanded motivation 1–7','Physical action, need, accounts and measurement retained; examples rewritten.'),
2:('9','Cells, vectors, graph, incidence, paths and cuts retained with patient notation teaching.'),
3:('10','Units, physical balance, declared carriers and boundaries retained; main examples now lossless.'),
4:('11–12','Potential and calculus teaching retained; threshold penalty replaced by reference/scale Gaussian geometry.'),
5:('6–7, 11–12; original PDF and historical Parts II/III','Allee/logistic/reserve derivations removed from this instructional core; homeostasis and reference distinguished. Historical mathematics not invalidated.'),
6:('13','Chain-rule field and signs retained; field does not silently choose a flow.'),
7:('13–14; original PDF and historical Part II','Autonomous force–flux/dissipation law not adopted; slope versus finite action and choice are taught separately.'),
8:('14; original PDF and historical Parts II/III','Timestep/error certificates removed from core; finite overshoot taught by exact quadratic curvature.'),
9:('15; original PDF and historical Parts II/III','P1C extraction permission not imported; generic physical and joint admissibility taught explicitly.'),
10:('16','Finite quote, zero branch, committed schedule, local inputs and cost-category discipline retained.'),
11:('17','Exact finite EBU, path integral and tangent comparison retained with Gaussian derivations.'),
12:('18','Need, signed value, repair and service/valuation distinctions retained.'),
13:('19','Local/global cancellation retained, including factor dependencies and complete information support.'),
14:('20','Sequential records, signed closure, external changes and account separation retained.'),
15:('21','Subdivision, granularity and closed cycles retained; path and burden assumptions explicit.'),
16:('22','Group versus singleton value, interactions and declared path attribution retained; no unlicensed entitlement.'),
17:('23','Atomic routes, distance, causal chains and multiple carrier accounts retained.'),
18:('24','State-reading studio retained and expanded; Gaussian quantities and worked answers.'),
19:('25','Physical drawing/action studio retained; explicit joint route cap and boundary variants.'),
20:('26','Landscape studio retained; old thresholds replaced by Gaussian references/scales.'),
21:('27','Slope studio retained; compulsory flux replaced by exact finite/integral and short-execution exercises.'),
22:('28','Finite-menu studio retained; ranking separated from actor policy, no hidden maximizer.'),
23:('29','Medicine-route studio retained; negative-first route, external event and multi-carrier chain.'),
24:('30','Shared-source/group studio retained; both feasible serial orders and qualified path accounting.'),
25:('31','Complete-account studio retained; detailed reconstruction, short execution and answer key.'),
26:('32; glossary and sources','Synthesis and claim audit retained. Historical O14/F13 outcome-example belongs to preserved Part III, not new Gaussian evidence.'),
}
rows=[]
for item in outline:
    ch=item['original_chapter']
    dest,reason=mapping.get(ch,('Front matter; glossary and sources','Rights, provenance, reader guidance and source map rewritten for this revision.'))
    status='REWRITTEN_SUBJECT'
    if ch in {5,7,8,9}:
        status='MODEL_SPECIFIC_CORE_REPLACED'
    if re.search(r'Allee|logistic|P1C|D[0-9]|F13|O14|timestep|error certificate|\breserve\b',item['title'],re.I):
        status='HISTORICAL_FORMULATION_NOT_CARRIED_FORWARD'
        reason+=' Original named formulation remains in the preserved sources; the new chapter is a conceptual destination, not a claim of verbatim retention.'
    item.update(disposition=status,new_home=dest,reason=reason)
    rows.append(item)
(OUT/'original_outline_disposition.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
lines=['# Full-length revision: original-outline disposition','',
 'All 533 original PDF outline entries are indexed below. Their titles and page',
 'starts were checked directly against the preserved PDF bookmarks. The previous',
 'short draft supplied only chapter/section identifiers, not the new dispositions.',
 '',
 'This is a subject-level editorial map, not a claim that every old sentence or',
 'formula is preserved. Replacement of a model-specific chapter is explicit.',
 'The original PDF remains unchanged and recoverable in full.',
 '', '| Original ID / PDF page | Original subject | New home | Disposition |',
 '|---|---|---|---|']
for row in rows:
    title=row['title'].replace('|','/')
    lines.append(f"| {row['id']} / {row['pdf_page_start']} | {title} | {row['new_home']} | {row['disposition']} |")
lines+=['','## Chapter-level reasons','']
for ch,(dest,reason) in mapping.items():
    lines.append(f'- Original {ch} → {dest}: {reason}')
(OUT/'revision_ledger.md').write_text('\n'.join(lines)+'\n')

short=ROOT.parent/'book_i_introductory_edition'
manifest=json.loads((short/'build_manifest.json').read_text())
for record in manifest['files']:
    p=short/record['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],str(p)
print(f'{len(rows)} original outline entries mapped; {len(manifest["files"])} preserved short-edition manifest entries unchanged.')
