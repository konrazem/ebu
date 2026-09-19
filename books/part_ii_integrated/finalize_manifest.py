"""Lock the editorial delivery; hash sources without importing scientific code."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
REVIEW = ROOT / 'review'
DEST = REVIEW / 'build_manifest.json'
EDITORIAL = [
    'BOOK_I_GENERATION_HANDOVER.md', 'BOOK_I_INTRODUCTION_BLUEPRINT.md',
    'BOOK_I_FULL_LENGTH_REVISION.md', 'CURRENT_SCIENTIFIC_AUTHORITY.md',
    'EBU_FUTURE_BOOKS_STRUCTURE.md',
    'LOCAL_GAUSSIAN_EBU_BOOK_SERIES_RECONCILIATION.md', 'books/README.md',
    'books/.gitattributes',
]
AUTHORITIES = [
    'LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md',
    'LOCAL_GAUSSIAN_EBU_FRAMEWORK_DECISION.md',
    'LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md',
    'V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md', 'SEQUENTIAL_PARALLEL_BRIDGE.md',
    'results/v3.0/gate1dc/MANIFEST.md',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()


part_i = json.loads((REPO / 'books/part_i_revised/review/artifact_checks.json').read_text())
part_ii = json.loads((REVIEW / 'artifact_checks.json').read_text())
repeat = json.loads((REVIEW / 'repeat_build.json').read_text())
assert repeat['byte_identical']
artifacts = []
for path, checks in [(part_i['artifact'], part_i), (part_ii['path'], part_ii)]:
    assert digest(REPO / path) == checks['sha256'] == repeat['after'][path]
    artifacts.append({'path': path, 'sha256': checks['sha256'], 'pages': checks['pages']})

files = [REPO / p for p in EDITORIAL]
for p in ROOT.rglob('*'):
    rel = p.relative_to(ROOT)
    if (not p.is_file() or p == DEST or 'build' in rel.parts
            or '__pycache__' in rel.parts
            or rel.parts[:2] in [('review', 'pages'), ('review', 'sheets')]):
        continue
    files.append(p)
files += [REPO / a['path'] for a in artifacts]
# Part I has its own complete source manifest; include that lock here.
files.append(REPO / 'books/part_i_revised/review/build_manifest.json')
files = sorted(set(files))
for p in files:
    if p.suffix in {'.md', '.tex', '.py', '.json'}:
        assert all(s.rstrip() == s for s in p.read_text().splitlines()), p
authority_records = []
for name in AUTHORITIES:
    committed = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=REPO)
    assert committed == (REPO / name).read_bytes(), name
    authority_records.append({'path': name, 'sha256': digest(REPO / name),
                              'git_blob_at_head': git('rev-parse', 'HEAD:' + name)})
record = {
    'status': 'AUTHOR_REVIEW_MANUSCRIPTS',
    'branch_at_recording': git('branch', '--show-current'),
    'source_parent_head_at_recording': git('rev-parse', 'HEAD'),
    'current_series_parts': 8,
    'artifacts': artifacts,
    'integrated_main_chapters': [33, 62],
    'new_typeset_pages': part_ii['new_typeset_pages'],
    'historical_source_pages': part_ii['historical_source_pages'],
    'repeat_build_byte_identical': True,
    'fixed_arithmetic_checks': {'part_i': 127, 'earlier_ii_iii': 69, 'new_extensions': 36},
    'model_transitions': 0, 'scientific_experiments': 0,
    'scientific_sources_unchanged': authority_records,
    'original_pdfs': part_i['baseline_pdfs_unchanged'],
    'files': [{'path': str(p.relative_to(REPO)), 'sha256': digest(p),
               'bytes': p.stat().st_size} for p in files],
    'exclusions': ['this manifest', 'build caches', 'rendered page images',
                   'preserved intermediate editions, which retain their own records'],
}
DEST.write_text(json.dumps(record, indent=2) + '\n')
print(f'{len(files)} integrated delivery files locked; eight-part series; no model execution.')
