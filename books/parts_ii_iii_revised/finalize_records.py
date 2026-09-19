"""Book provenance and editorial subject map; no scientific model imports."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
REVIEW = ROOT / 'review'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# One subject-level disposition for each original chapter and its descendants.
# Rewriting a subject does not claim verbatim coverage of every old subsection.
targets = {
    'II': ['II33', 'II34', 'II34', 'II35', 'II36', 'II37,44', 'II38',
           'II39', 'II40,42,43', 'II40', 'II41,42', 'II44 + H-II',
           'II44 + H-II', 'II44 + H-II', 'II45 + H-II', 'II45', 'II45', 'II46'],
    'III': ['III47', 'III48', 'III49–55', 'III56', 'III56 + II45',
            'III51', 'III52', 'III54', 'III57 + H-III', 'III57 + H-III',
            'III57 + H-III', 'III57 + H-III', 'III57 + H-III',
            'III57 + H-III', 'III57 + H-III', 'III58', 'III55', 'III59,60'],
}
inventory = json.loads((REVIEW / 'original_inventory.json').read_text())
dispositions = []
for volume in inventory:
    assert digest(Path(volume['path'])) == volume['sha256']
    part = volume['part']
    chapter = -1
    destination = 'Revised front matter; original wording retained in source PDF'
    for item in volume['outline']:
        if item['depth'] == 0:
            if item['title'] == 'References and source map':
                destination = 'Revised source map; complete old references remain in original PDF'
            elif item['original_pdf_page'] >= (12 if part == 'II' else 14):
                chapter += 1
                destination = targets[part][chapter]
        archived = ((65 <= item['original_pdf_page'] <= 94) if part == 'II'
                    else (66 <= item['original_pdf_page'] <= 110))
        dispositions.append(dict(part=part, **item, revised_subject_home=destination,
            disposition=('Original page retained in historical appendix, with visual title/banner changes'
                         if archived else 'Subject rewritten selectively; full original treatment remains in source PDF')))
    assert chapter + 1 == len(targets[part])
(REVIEW / 'original_outline_disposition.json').write_text(json.dumps({
    'scope': 'Chapter-level subject routing inherited by subsection entries; not a word-level completeness claim',
    'entries': dispositions}, indent=2) + '\n')

sources = [
    'LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md',
    'LOCAL_GAUSSIAN_EBU_FRAMEWORK_DECISION.md',
    'LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md',
    'V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md', 'SEQUENTIAL_PARALLEL_BRIDGE.md',
    'results/v3.0/gate1dc/MANIFEST.md',
]
checks = json.loads((REVIEW / 'artifact_checks.json').read_text())
for row in checks:
    assert digest(REPO / row['path']) == row['sha256']
head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=REPO, text=True).strip()
assert head == '05f3cb02d0c48e60de98342edfac9c36f2cecc6f'
files = [p for p in ROOT.rglob('*') if p.is_file()
         and not {'build', '__pycache__', 'pages'}.intersection(p.relative_to(ROOT).parts)
         and p.name != 'build_manifest.json']
files += [REPO / 'books/part_i_revised/book.tex']
files += [REPO / row['path'] for row in checks]
manifest = {
    'status': 'AUTHOR_REVIEW_UNCOMMITTED', 'starting_head': head, 'final_head': head,
    'artifacts': checks, 'arithmetic_checks': 69,
    'model_transitions': 0, 'scientific_experiments': 0,
    'originals': [{k:v for k,v in p.items() if k != 'outline'} for p in inventory],
    'original_outline_entries_mapped': len(dispositions),
    'source_locks': [{'path':p, 'sha256':digest(REPO / p),
                     'git_blob_at_head':subprocess.check_output(
                         ['git','rev-parse','HEAD:'+p],cwd=REPO,text=True).strip()}
                    for p in sources],
    'files': [{'path':str(p.relative_to(REPO)), 'sha256':digest(p)} for p in sorted(set(files))],
}
(REVIEW / 'build_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(f'{len(dispositions)} original outline entries routed; {len(files)} delivery paths hashed.')
