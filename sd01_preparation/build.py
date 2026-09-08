"""Build an explicitly UNSEALED dossier from pinned committed authority.

Usage: python3 -B -m sd01_preparation.build --stage-e-archive PATH --output PATH
The output is preparation metadata, never a configuration/run/result manifest.
"""
from __future__ import annotations
import argparse
import ast
from io import BytesIO
from fractions import Fraction
from pathlib import Path
import subprocess
import zipfile
from .mechanics import Refusal, canonical, digest, strict_load

BASE = '6078febefb8f082a76a0b9fc6c61331b14743aca'
E_SHA = '2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345'
ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def source(name):
    data = git('show', f'{BASE}:{name}')
    if (ROOT / name).read_bytes() != data: raise Refusal(f'frozen source modified: {name}')
    return data


def locked_sources():
    paths = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
    selected = [p for p in paths if p.startswith(('STAGE_D_', 'STAGE_E_', 'STAGE_F_', 'stage_d_', 'stage_e_', 'stage_f_'))
                and p.endswith(('.md', '.json', '.py'))]
    selected += ['AGENTS.md', 'UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md',
                 'UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md', 'CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md']
    rows = []
    for path in sorted(set(selected)):
        data = source(path)
        if path.endswith('.json'): strict_load(data)
        if path.endswith('.py'): ast.parse(data, filename=path)
        rows.append({'path': path, 'revision': BASE, 'git_object': git('rev-parse', f'{BASE}:{path}').decode().strip(),
                     'byte_count': len(data), 'sha256': digest(data)})
    return rows


def stage_e(archive):
    data = Path(archive).read_bytes()
    if digest(data) != E_SHA: raise Refusal('Stage E artifact differs from frozen raw archive hash')
    with zipfile.ZipFile(BytesIO(data)) as z:
        names = z.namelist()
        if len(names) != len(set(names)): raise Refusal('duplicate archive member')
        manifest = strict_load(z.read('stage-e-evidence/final-manifest.json'))
        if manifest['head_commit'] != 'c43ead831c3e4021405985134ed564b761bb1aed' or manifest['status'] != 'STAGE_E_SCIENTIFIC_HARNESS_VALIDATION_PASS' or manifest['record_count'] != 9 or len(manifest['records']) != 9:
            raise Refusal('Stage E manifest coordinate or closure')
        identities = []
        for row in manifest['records']:
            name = row['identity']['path']; raw = z.read('stage-e-evidence/' + name)
            record = strict_load(raw)
            if len(raw) != row['identity']['byte_count'] or digest(raw) != row['identity']['sha256']: raise Refusal('Stage E record hash')
            if record['head_commit'] != manifest['head_commit'] or record['head_tree'] != manifest['head_tree'] or record['environment'] != manifest['environment'] or record['status'] != row['status'] or record['evidence_class'] != row['evidence_class']: raise Refusal('Stage E record linkage')
            if any(record['scientific_counters'].values()) or any(record['release_counters'].values()): raise Refusal('nonzero Stage E boundary')
            identities.append(row['identity'])
        complexity = strict_load(z.read('stage-e-evidence/complexity.json'))
        projections = [p for p in complexity['projections'] if p['study_id'] == 'SD-01']
        if len(projections) != 1: raise Refusal('Stage E SD-01 projection closure')
        return {'artifact_id': 9708926559, 'raw_archive_sha256': E_SHA, 'raw_archive_bytes': len(data),
                'archive_endpoint': 'https://api.github.com/repos/konrazem/ebu/actions/artifacts/9708926559/zip',
                'verified_base_record_identities': identities, 'environment': manifest['environment'],
                'frozen_sd01_projection': projections[0],
                'limitation': 'Accepted harness complexity estimate, not measured SD-01 throughput. Its 33 projected slices are not a feasible run allocation: at least 196 run attempts are required. Do not substitute the scalar for a sealed campaign envelope.'}


def projections():
    # Metadata only: no runner import, initial-state construction or transitions.
    cells = []
    for family in ('logistic', 'allee'):
        for rho in (Fraction(3, 10), Fraction(3, 5)):
            g15 = rho * 15 * (1 - Fraction(15, 20))
            if family == 'allee': g15 *= Fraction(15, 5) - 1
            for ratio in (Fraction(1, 4), Fraction(3, 4), Fraction(1), Fraction(5, 4)):
                demand = ratio * g15
                for schedule in ('none', 'adversarial'):
                    for policy, eta in [('H0', None), ('H1', None), ('H3', None), ('H2', Fraction(1, 2)), ('H2', Fraction(9, 10)), ('H2', Fraction(1))]:
                        rat = lambda x: None if x is None else [x.numerator, x.denominator]
                        cells.append({'source': family, 'rho': rat(rho), 'demand_ratio': rat(ratio), 'demand_exact': rat(demand),
                                      'schedule': schedule, 'policy': policy, 'eta': rat(eta),
                                      'initial_stock': 15, 'horizon_ticks': 20000})
    # Ordering is a proposed mechanical serialization, not a new scientific choice.
    return sorted(cells, key=canonical)


def build(archive):
    sources = locked_sources()
    implementation_commit = git('rev-parse', 'HEAD').decode().strip()
    git('merge-base', '--is-ancestor', BASE, implementation_commit)
    implementation_paths = sorted([str(p.relative_to(ROOT)) for p in (ROOT / 'sd01_preparation').glob('*.py')]
                                  + ['sd01_preparation/README.md', 'SD01_CONTROL_DECISIONS.md', 'tests/sd01_preparation/test_preparation.py'])
    implementation_rows = []
    for path in implementation_paths:
        raw = git('show', f'{implementation_commit}:{path}')
        if raw != (ROOT / path).read_bytes(): raise Refusal('uncommitted implementation source')
        implementation_rows.append({'path': path, 'byte_count': len(raw), 'sha256': digest(raw)})
    matrix = strict_load(source('stage_d_scientific_validation_master_matrix.json'))
    row = matrix['studies'][0]
    if row['study_id'] != 'SD-01': raise Refusal('route order drift')
    continuation = strict_load(source('stage_d_completion_oriented_continuation_contract.json'))
    contract = strict_load(source('stage_d_scientific_validation_contract.json'))
    evidence = stage_e(archive)
    cells = projections()
    if len(cells) != 192 or len({canonical(c) for c in cells}) != 192: raise Refusal('cell closure')
    packet = {
        'schema': 'sd01_preparation_dossier/v1', 'status': 'UNSEALED_SCIENTIFIC_CONTROL_DECISIONS_REQUIRED',
        'base_commit': BASE, 'implementation_commit': implementation_commit, 'implementation_sources': implementation_rows, 'route_id': 'SD-01', 'gap_id': 'STAGE_F_SD01_ADAPTER_AND_RUN_ID_CLOSURE',
        'execution_permitted': False, 'authorization_line': None, 'campaign_id': None, 'scientific_run_ids': [],
        'source_inventory': sources, 'frozen_scientific_row': row,
        'frozen_numerical_policy': contract['prospective_numerical_policy'],
        'cell_metadata_projections': cells, 'projection_is_execution_configuration': False,
        'control_slots': [
            {'family': f, 'rho': r, 'initial_stock': 15 if f == 'logistic' else 4,
             'demand': [0, 1] if f == 'logistic' else None, 'policy': None, 'shock_schedule': None,
             'status': 'REQUIRES_EXACT_CONTROL_BINDING'}
            for f in ('logistic', 'allee') for r in ([3, 10], [3, 5])],
        'scientific_decisions': ['SD01-CONTROL-TUPLES', 'SD01-CONTROL-ASSERTION-MAPPING'],
        'decision_record': 'SD01_CONTROL_DECISIONS.md',
        'frozen_identity_hierarchy': continuation['identity_hierarchy'],
        'frozen_execution_binding_policy': continuation['execution_binding_policy'],
        'frozen_checkpoint_binding': continuation['checkpoint_binding'],
        'frozen_attempt_protocol': continuation['attempt_protocol'],
        'frozen_cumulative_accounting': continuation['cumulative_accounting'],
        'frozen_terminal_states': continuation['terminal_states'],
        'frozen_campaign_budget_policy': continuation['campaign_budget_policy'],
        'frozen_attempt_watchdog_policy': continuation['attempt_watchdog_policy'],
        'record_schema_sources': [
            {'path': 'stage_d_scientific_validation_evidence_schema.json', 'role': 'configuration/trace/receipt/computation/limit/output'},
            {'path': 'stage_d_completion_oriented_continuation_evidence_schema.json', 'role': 'campaign/attempt/checkpoint/recovery/terminal and cumulative ledgers'}],
        'stage_e_evidence': evidence,
        'compute_derivation': {'scientific_cells': 192, 'control_trajectories': 4, 'total_trajectories': 196,
            'ticks_per_trajectory': 20000, 'maximum_transitions': 3920000,
            'h3_scientific_cells': 32, 'additional_h3_checks_per_tick_upper_bound': 55,
            'frozen_primary_evaluations': 39120000,
            'evaluation_count_condition': '39120000 is the frozen count and assumes controls add no H3 branch checks. An H3 control assignment must reconcile this count prospectively; this is not a sealed total-work upper bound.', 'h3_primary_evaluations_per_run_upper_bound': 1120000,
            'checkpoint_interval_ticks': 1000, 'checkpoint_boundaries_per_complete_run': 20,
            'all_run_checkpoint_boundaries': 3920, 'minimum_attempt_count_all_runs': 196,
            'suggested_worker_count': 1, 'suggested_host_memory_bytes': 8589934592,
            'process_memory_cap_bytes': 4294967296, 'logical_study_output_cap_bytes': 21474836480,
            'host_memory_is_operational_proposal': True, 'cloud_instance_identity': None},
        'result_layout': {'status': 'PROPOSED_NOT_ALLOCATED', 'bucket': None,
            'key_template': 'SD-01/{campaign_sha256}/runs/{run_sha256}/{role}/{ordinal:08d}-{content_sha256}.json',
            'roles': ['attempts', 'checkpoints', 'traces', 'receipts', 'ledgers', 'manifests'],
            'requirements': ['write-once objects', 'exact S3 VersionId plus byte count and SHA-256',
                             'manifest after verified data durability', 'independent audit copy outside Git',
                             'retain all failed attempts and partial traces', 'no mutable latest pointer as recovery authority']},
        'cost_cap': {'status': 'NOT_SEALED', 'currency': 'USD', 'live_authorized_spend_microusd': 0,
            'arithmetic_implementation': 'reserve_cost: exact rational price, upward-rounded micro-USD, no replay/refund',
            'required_before_seal': ['bounded price schedule for every AWS service and retention/retrieval horizon',
                'exact resource identities and quantities', 'durable serialized reservations before side effects',
                'host watchdog and independent finalizer with reserved shutdown/retrieval allowance',
                'verified IAM and storage policies', 'explicit post-packet user authorization'],
            'aws_c0_resources_reused': False},
        'remaining_implementation_gates': ['complete scientific control binding', 'numerical conformance without registered execution',
            'complete schema-valid v2 run/attempt/checkpoint composition', 'independent production durability and retrieval validation',
            'AWS host-specific operational binding preserving frozen scientific runtime', 'complete cost enclosure and watchdog validation',
            'full independent binding audit and seal'],
        'scientific_execution_count': 0,
    }
    packet['dossier_sha256'] = digest(canonical(packet))
    return packet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage-e-archive', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    packet = build(args.stage_e_archive)
    with args.output.open('xb') as stream: stream.write(canonical(packet))
    print(packet['status'], packet['dossier_sha256'])

if __name__ == '__main__': main()
