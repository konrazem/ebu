"""No science: byte payloads, static AST, rational parameter projection only."""
import ast
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sd01_preparation import mechanics as m
from sd01_preparation.build import BASE, ROOT, projections, source


class StaticPreparation(unittest.TestCase):
    def test_adapter_is_not_imported(self):
        self.assertNotIn('sd01_preparation.adapter', sys.modules)
        tree = ast.parse((ROOT / 'sd01_preparation/adapter.py').read_bytes())
        for node in tree.body:
            self.assertIsInstance(node, (ast.Expr, ast.Import, ast.ImportFrom, ast.FunctionDef))
        self.assertEqual([n.name for n in tree.body if isinstance(n, ast.FunctionDef)],
                         ['parameter', 'regeneration', 'shock', 'action_menu', 'h1_branch', 'select_action', 'transition'])

    def test_source_is_exact_base(self):
        raw = source('stage_d_scientific_validation_master_matrix.json')
        self.assertEqual(raw, subprocess.check_output(['git', 'show', BASE + ':stage_d_scientific_validation_master_matrix.json'], cwd=ROOT))

    def test_complete_parameter_projection(self):
        cells = projections()
        self.assertEqual(len(cells), 192)
        self.assertEqual(len({m.canonical(c) for c in cells}), 192)
        self.assertEqual(sum(c['policy'] == 'H3' for c in cells), 32)
        self.assertEqual({tuple(c['demand_exact']) for c in cells if c['source'] == 'logistic' and c['rho'] == [3, 10]},
                         {(9, 32), (27, 32), (9, 8), (45, 32)})
        self.assertEqual(196 * 20000 + 32 * 20000 * 55, 39120000)
        self.assertLessEqual(20000 * 56, 1200000)

    def test_authorization_always_refuses(self):
        for argument in (None, {}, {'approved': True}, {'status': 'SEALED', 'execution_permitted': True}):
            with self.subTest(argument=argument), self.assertRaises(m.Refusal): m.execution_authorization(argument)
        self.assertNotIn('sd01_preparation.adapter', sys.modules)

    def test_canonical_rejects_ambiguous_inputs(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":1.0}', b'{"x":NaN}', b'{}{}', b'"\xff"', '"e\u0301"'.encode()):
            with self.subTest(raw=raw), self.assertRaises(m.Refusal): m.strict_load(raw)
        self.assertEqual(m.canonical({'z': [], 'a': 2}), b'{"a":2,"z":[]}')

    def test_identity_requires_complete_preimage(self):
        fields = ['a', 'b']
        for obj in ({'a': 1}, {'a': 1, 'b': None}, {'a': 1, 'b': 2, 'c': 3}):
            with self.assertRaises(m.Refusal): m.bound_identity('synthetic', obj, fields)
        a = m.bound_identity('synthetic', {'a': 1, 'b': 2}, fields)
        b = m.bound_identity('synthetic', {'a': 1, 'b': 3}, fields)
        self.assertNotEqual(a, b)

    def test_result_layout_refuses_traversal(self):
        h = '1' * 64
        for role in ('../traces', 'latest', '/tmp', ''):
            with self.assertRaises(m.Refusal): m.result_key(h, h, role, 0, h)
        with self.assertRaises(m.Refusal): m.result_key(h, h, 'traces', True, h)
        self.assertTrue(m.result_key(h, h, 'traces', 0, h).startswith('SD-01/'))


class SyntheticDurability(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='sd01-synthetic-')
        self.root = Path(self.tmp.name)
        self.store = m.ObjectStore(self.root)
        self.binding = m.digest(b'SYNTHETIC ONLY')

    def tearDown(self): self.tmp.cleanup()

    def checkpoint(self, sequence=1, predecessor=None):
        obj = self.store.put(b'arbitrary bytes, not a model state')
        return self.store.checkpoint(binding_digest=self.binding, predecessor=predecessor,
                                     next_sequence=sequence, object_digests=[obj])

    def test_immutable_and_idempotent(self):
        h = self.store.put(b'fixture')
        self.assertEqual(h, self.store.put(b'fixture'))
        self.assertEqual(self.store.get(h), b'fixture')
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_corrupt_object_refuses(self):
        h = self.store.put(b'fixture')
        (self.root / h).write_bytes(b'corruption injected in synthetic test')
        with self.assertRaises(m.Refusal): self.store.get(h)
        with self.assertRaises(m.Refusal): self.store.put(b'fixture')

    def test_symlink_refuses(self):
        h = 'a' * 64
        (self.root / h).symlink_to('/dev/null')
        with self.assertRaises(OSError): self.store.get(h)

    def test_checkpoint_reload_fresh_process(self):
        marker = self.checkpoint()
        code = 'from sd01_preparation.mechanics import ObjectStore; import sys; print(ObjectStore(sys.argv[1]).recover(sys.argv[2],sys.argv[3])["next_sequence"])'
        p = subprocess.run([sys.executable, '-B', '-c', code, str(self.root), marker, self.binding], cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(p.stdout.strip(), '1')

    def test_checkpoint_chain_monotonic_and_bound(self):
        a = self.checkpoint(); b = self.checkpoint(2, a)
        self.assertEqual(self.store.recover(b, self.binding)['predecessor'], a)
        with self.assertRaises(m.Refusal): self.checkpoint(1, a)
        with self.assertRaises(m.Refusal): self.store.recover(b, 'f' * 64)

    def test_missing_object_prevents_marker(self):
        with self.assertRaises(FileNotFoundError):
            self.store.checkpoint(binding_digest=self.binding, predecessor=None, next_sequence=1, object_digests=['f' * 64])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_orphan_is_not_checkpoint(self):
        self.store.put(b'orphan fixture')
        with self.assertRaises(FileNotFoundError): self.store.recover('e' * 64, self.binding)

    def test_retrieval_exact_version_and_hash(self):
        raw = b'evidence bytes, not scientific data'
        entries = [{'key': 'fixture/object', 'version_id': 'v1', 'sha256': m.digest(raw), 'byte_count': len(raw)}]
        calls = []
        def read(key, version): calls.append((key, version)); return raw
        h = m.retrieve_exact(entries, read, self.store)
        self.assertEqual(calls, [('fixture/object', 'v1')])
        self.assertEqual(m.strict_load(self.store.get(h))['objects'], entries)
        with self.assertRaises(m.Refusal): m.retrieve_exact(entries, lambda *_: raw + b'x', self.store)
        wrong = deepcopy(entries); wrong[0]['version_id'] = ''
        with self.assertRaises(m.Refusal): m.retrieve_exact(wrong, read, self.store)
        with self.assertRaises(m.Refusal): m.retrieve_exact(entries * 2, read, self.store)


class SyntheticBudget(unittest.TestCase):
    def test_round_up_and_boundary(self):
        r = m.reserve_cost(2, 0, {}, 'first', 1, 1, 3)
        self.assertEqual(r, {'first': 1})
        r = m.reserve_cost(2, 0, r, 'second', 1, 1, 3)
        self.assertEqual(sum(r.values()), 2)
        with self.assertRaises(m.Refusal): m.reserve_cost(2, 0, r, 'third', 1, 1, 3)

    def test_replay_negative_boolean_zero_denominator(self):
        for args in [(10, 0, {'x': 1}, 'x', 1, 1, 1), (10, 0, {}, 'x', -1, 1, 1),
                     (10, 0, {}, 'x', True, 1, 1), (10, 0, {}, 'x', 1, 1, 0)]:
            with self.assertRaises(m.Refusal): m.reserve_cost(*args)

    def test_zero_live_budget(self):
        with self.assertRaises(m.Refusal): m.reserve_cost(0, 0, {}, 'cloud', 1, 1, 1)


class SyntheticRecords(unittest.TestCase):
    def test_frozen_checkpoint_schema_and_mutations(self):
        from sd01_preparation.record_validation import validate_record
        from stage_e_harness.canonical import Refusal as SchemaRefusal
        schema = m.strict_load(source('stage_d_completion_oriented_continuation_evidence_schema.json'))
        fixture = schema['prospective_non_evidence_schema_fixtures']['valid_sd01_deterministic_empty_checkpoint']
        validate_record('continuation_checkpoint', fixture)
        for mutate in ('seed', 'extra', 'missing', 'dummy_stream'):
            value = deepcopy(fixture)
            if mutate == 'seed': value['seed'] = 1
            elif mutate == 'extra': value['invented'] = True
            elif mutate == 'missing': del value['state_identity']
            else: value['ordered_permitted_stream_ids'] = ['dummy']
            with self.subTest(mutate=mutate), self.assertRaises(SchemaRefusal): validate_record('continuation_checkpoint', value)
        self.assertNotIn('sd01_preparation.adapter', sys.modules)

    def test_cumulative_failed_writes_and_order(self):
        def row(run, ordinal, logical, physical):
            return {'run_id': run, 'attempt_ordinal': ordinal, 'active_wall_time_nanoseconds': 10,
                    'primary_evaluations': 3, 'physical_trace_bytes_written': physical,
                    'physical_output_bytes_written': 1, 'durable_logical_trace_bytes': logical,
                    'durable_logical_output_bytes': 1, 'process_tree_peak_resident_memory_bytes': 100,
                    'campaign_calendar_elapsed_seconds': ordinal + 1}
        rows = [row('a', 0, 5, 7), row('a', 1, 5, 9), row('b', 0, 4, 4)]
        result = m.fold_attempts(['a', 'b'], rows)
        self.assertEqual(result, m.fold_attempts(['a', 'b'], list(reversed(rows))))
        self.assertEqual(result['totals']['physical_trace_bytes_written'], 20)
        self.assertEqual(result['totals']['durable_logical_trace_bytes'], 9)
        self.assertEqual(result['totals']['primary_evaluations'], 9)
        with self.assertRaises(m.Refusal): m.fold_attempts(['a', 'b'], rows + [rows[0]])
        with self.assertRaises(m.Refusal): m.fold_attempts(['a', 'b'], rows[1:])
        reset = deepcopy(rows); reset[1]['durable_logical_trace_bytes'] = 3
        with self.assertRaises(m.Refusal): m.fold_attempts(['a', 'b'], reset)

    def test_recovery_requires_all_conditions(self):
        facts = {k: True for k in ('transient_failure', 'no_post_checkpoint_state_accepted',
                 'code_identity_unchanged', 'environment_identity_unchanged', 'failed_costs_retained')}
        facts['independent_audit_identity'] = m.identity('synthetic-audit', {'fixture': 1})
        facts['applicable_recovery_rule_identity'] = m.identity('synthetic-rule', {'fixture': 2})
        self.assertTrue(m.verify_recovery_metadata(facts))
        for key in list(facts):
            bad = deepcopy(facts); del bad[key]
            with self.assertRaises(m.Refusal): m.verify_recovery_metadata(bad)
        bad = deepcopy(facts); bad['transient_failure'] = False
        with self.assertRaises(m.Refusal): m.verify_recovery_metadata(bad)


class ReviewRegressions(unittest.TestCase):
    def test_checkpoint_rejects_nonarray_before_publication(self):
        with tempfile.TemporaryDirectory(prefix='sd01-review-') as directory:
            store = m.ObjectStore(directory)
            for value in ({}, (), ''):
                with self.assertRaises(m.Refusal):
                    store.checkpoint(binding_digest='a' * 64, predecessor=None, next_sequence=1, object_digests=value)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_retrieval_refuses_malformed_coordinates_before_reader(self):
        with tempfile.TemporaryDirectory(prefix='sd01-review-') as directory:
            store = m.ObjectStore(directory)
            def forbidden(*_): self.fail('reader called with invalid coordinates')
            for key, version in [('', 'v'), (True, 'v'), ('key', True), ('key', 1), ('key', '')]:
                with self.assertRaises(m.Refusal):
                    m.retrieve_exact([{'key': key, 'version_id': version, 'sha256': 'a' * 64, 'byte_count': 0}], forbidden, store)

    def test_stage_e_archive_is_parsed_from_verified_bytes(self):
        tree = ast.parse((ROOT / 'sd01_preparation/build.py').read_bytes())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'stage_e')
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'ZipFile']
        self.assertEqual(len(calls), 1)
        self.assertEqual(ast.unparse(calls[0].args[0]), 'BytesIO(data)')

if __name__ == '__main__': unittest.main()
