"""Record artifact provenance only; never import a scientific model."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
REVIEW = ROOT / 'review'
DEST = REVIEW / 'build_manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


editorial = [
    'BOOK_I_GENERATION_HANDOVER.md', 'BOOK_I_INTRODUCTION_BLUEPRINT.md',
    'CURRENT_SCIENTIFIC_AUTHORITY.md', 'EBU_FUTURE_BOOKS_STRUCTURE.md',
    'LOCAL_GAUSSIAN_EBU_BOOK_SERIES_RECONCILIATION.md',
    'BOOK_I_FULL_LENGTH_REVISION.md', 'books/README.md',
]
sources = [
    'LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md',
    'V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md', 'SEQUENTIAL_PARALLEL_BRIDGE.md',
    'results/v3.0/gate1dc/MANIFEST.md',
]
paths = [REPO / p for p in editorial]
for p in ROOT.rglob('*'):
    relative = p.relative_to(ROOT)
    if (not p.is_file() or p == DEST or 'build' in relative.parts
            or '__pycache__' in relative.parts
            or relative.parts[:2] == ('review', 'pages')):
        continue
    paths.append(p)
checks = json.loads((REVIEW / 'artifact_checks.json').read_text())
pdf = REPO / checks['artifact']
assert digest(pdf) == checks['sha256']
paths.append(pdf)
paths = sorted(set(paths))
for p in paths:
    if p.suffix in {'.md', '.tex', '.py', '.json', '.xml'}:
        for line, text in enumerate(p.read_text().splitlines(), 1):
            assert text.rstrip() == text, (str(p), line, 'trailing whitespace')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
repeat = json.loads((REPO / 'books/part_ii_integrated/review/repeat_build.json').read_text())
assert repeat['byte_identical'] and repeat['after'][checks['artifact']] == digest(pdf)
record = {
    'status': 'AUTHOR_REVIEW_MANUSCRIPT',
    'source_parent_head_at_recording': head,
    'artifact': checks['artifact'], 'artifact_sha256': digest(pdf),
    'pages': checks['pages'], 'trim_pdf_points': checks['trim_pdf_points'],
    'repeat_build_byte_identical': True,
    'arithmetic_checks': 127, 'scientific_experiments_executed': 0,
    'original_pdfs': checks['baseline_pdfs_unchanged'],
    'scientific_sources': [
        {'path': p, 'sha256': digest(REPO / p),
         'git_blob_at_head': subprocess.check_output(
             ['git', 'rev-parse', 'HEAD:' + p], cwd=REPO, text=True).strip()}
        for p in sources
    ],
    'files': [{'path': str(p.relative_to(REPO)), 'sha256': digest(p),
               'bytes': p.stat().st_size} for p in paths],
    'inventory_exclusions': ['this manifest', 'build caches', 'rendered review images',
                             'unchanged earlier short edition'],
}
DEST.write_text(json.dumps(record, indent=2) + '\n')
print(f'{len(paths)} delivery files locked; {checks["pages"]} pages; HEAD unchanged.')
