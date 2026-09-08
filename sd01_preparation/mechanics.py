"""Static identity, synthetic durability, retrieval and budget primitives.

No scientific adapter imports, execution entry point, AWS client or sealer.
The POSIX store is a tested local primitive, not the inherited Windows host
attestation or proof of S3 durability. Production binding remains blocked.
"""
from __future__ import annotations
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import unicodedata

class Refusal(ValueError):
    pass


def canonical(value):
    def check(v):
        if isinstance(v, str):
            if unicodedata.normalize('NFC', v) != v:
                raise Refusal('non-NFC string')
        elif v is None or type(v) in (int, bool):
            pass
        elif isinstance(v, list):
            for item in v: check(item)
        elif isinstance(v, dict):
            for k, item in v.items():
                if not isinstance(k, str): raise Refusal('non-string key')
                check(k); check(item)
        else:
            raise Refusal('noncanonical type; binary64 must use exact bit strings')
    check(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_load(data):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d: raise Refusal('duplicate JSON key')
            d[k] = v
        return d
    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=pairs)
        canonical(value)
        return value
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal('invalid UTF-8 JSON') from exc


def identity(kind, preimage):
    h = digest(canonical(preimage))
    return {'kind': kind, 'value': h, 'sha256': h}


def bound_identity(kind, preimage, frozen_fields):
    if set(preimage) != set(frozen_fields) or any(preimage[k] is None for k in frozen_fields if k != 'incoming_checkpoint_identity'):
        raise Refusal('incomplete or extra identity preimage')
    return identity(kind, preimage)


def require_digest(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise Refusal('invalid SHA-256')
    return value


def result_key(campaign_digest, run_digest, role, ordinal, content_digest):
    for value in (campaign_digest, run_digest, content_digest): require_digest(value)
    if role not in ('attempts', 'checkpoints', 'traces', 'receipts', 'ledgers', 'manifests') or type(ordinal) is not int or ordinal < 0:
        raise Refusal('invalid result coordinate')
    return f'SD-01/{campaign_digest}/runs/{run_digest}/{role}/{ordinal:08d}-{content_digest}.json'


class ObjectStore:
    """Write-once content-addressed files in a private, already-created root.

    Parent ownership and filesystem durability must be independently attested
    before production use. A commit marker is published only after its objects.
    """
    def __init__(self, root):
        self.root = Path(root)
        if self.root.is_symlink() or not self.root.is_dir(): raise Refusal('unsafe store root')

    def put(self, data):
        h = digest(data)
        fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=self.root)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data); stream.flush(); os.fsync(stream.fileno())
            try:
                os.link(temporary, self.root / h, follow_symlinks=False)
            except FileExistsError:
                if self.get(h) != data: raise Refusal('immutable object collision')
            directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
            try: os.fsync(directory)
            finally: os.close(directory)
        finally:
            os.unlink(temporary)
        return h

    def get(self, h):
        require_digest(h)
        fd = os.open(self.root / h, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode): raise Refusal('not a regular object')
            data = stream.read()
        if digest(data) != h: raise Refusal('object hash mismatch')
        return data

    def checkpoint(self, *, binding_digest, predecessor, next_sequence, object_digests):
        require_digest(binding_digest)
        if not isinstance(object_digests, list): raise Refusal('checkpoint objects must be an array')
        if type(next_sequence) is not int or next_sequence < 0: raise Refusal('invalid sequence')
        if predecessor is not None:
            previous = self.recover(predecessor, binding_digest)
            if next_sequence <= previous['next_sequence']: raise Refusal('nonmonotone checkpoint')
        for h in object_digests: self.get(h)
        if len(set(object_digests)) != len(object_digests): raise Refusal('duplicate checkpoint object')
        marker = {'schema': 'sd01_preparation_checkpoint_bundle/v1', 'binding_digest': binding_digest,
                  'predecessor': predecessor, 'next_sequence': next_sequence, 'objects': object_digests}
        return self.put(canonical(marker))

    def recover(self, marker_digest, binding_digest):
        require_digest(binding_digest)
        marker = strict_load(self.get(marker_digest))
        if set(marker) != {'schema', 'binding_digest', 'predecessor', 'next_sequence', 'objects'} or marker['schema'] != 'sd01_preparation_checkpoint_bundle/v1' or marker['binding_digest'] != binding_digest:
            raise Refusal('checkpoint binding mismatch')
        if type(marker['next_sequence']) is not int or marker['next_sequence'] < 0 or not isinstance(marker['objects'], list): raise Refusal('checkpoint shape')
        for h in marker['objects']: self.get(h)
        if len(set(marker['objects'])) != len(marker['objects']): raise Refusal('duplicate object')
        if marker['predecessor'] is not None:
            previous = self.recover(marker['predecessor'], binding_digest)
            if marker['next_sequence'] <= previous['next_sequence']: raise Refusal('checkpoint sequence reversal')
        return marker


def retrieve_exact(entries, read_object, store):
    """Verify pinned keys/versions and every byte before retaining a manifest.

    The caller's source reader must use an exact version, never list/latest.
    No fetched object is deserialized or executed as code.
    """
    if not isinstance(entries, list): raise Refusal('retrieval entries must be an array')
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'key', 'version_id', 'sha256', 'byte_count'}:
            raise Refusal('malformed evidence entry')
        if any(not isinstance(entry[k], str) or not entry[k] for k in ('key', 'version_id')):
            raise Refusal('exact nonempty key and version strings required')
    keys = [entry['key'] for entry in entries]
    if keys != sorted(set(keys)): raise Refusal('retrieval keys must be unique and sorted')
    for entry in entries:
        if set(entry) != {'key', 'version_id', 'sha256', 'byte_count'} or not entry['version_id']:
            raise Refusal('unversioned or malformed evidence')
        if type(entry['byte_count']) is not int or entry['byte_count'] < 0: raise Refusal('invalid byte count')
        require_digest(entry['sha256'])
        data = read_object(entry['key'], entry['version_id'])
        if len(data) != entry['byte_count'] or digest(data) != entry['sha256']: raise Refusal('retrieval integrity failure')
        store.put(data)
    return store.put(canonical({'schema': 'sd01_preparation_retrieval/v1', 'objects': entries}))


def reserve_cost(cap_microusd, committed_microusd, reservations, request_id, units, price_numerator, price_denominator):
    """Pure worst-case admission arithmetic; reservations never refunded here.

    Production requires a serialized durable journal, verified price coverage,
    resource watchdog and independent cloud finalizer before use.
    """
    values = [cap_microusd, committed_microusd, units, price_numerator, price_denominator]
    if any(type(v) is not int or v < 0 for v in values) or price_denominator == 0 or not isinstance(request_id, str) or not request_id:
        raise Refusal('invalid budget input')
    if request_id in reservations or any(type(v) is not int or v < 0 for v in reservations.values()): raise Refusal('invalid/replayed reservation')
    rational = Fraction(units * price_numerator, price_denominator)
    charge = -(-rational.numerator // rational.denominator)
    if committed_microusd + sum(reservations.values()) + charge > cap_microusd: raise Refusal('hard cost admission cap')
    return {**reservations, request_id: charge}


def execution_authorization(*_args, **_kwargs):
    # This preparation package cannot seal, self-authorize or dispatch a runner.
    raise Refusal('SD-01 control decisions unresolved; no sealed execution packet')


ADDITIVE_COUNTERS = ('active_wall_time_nanoseconds', 'primary_evaluations',
                     'physical_trace_bytes_written', 'physical_output_bytes_written')
HIGH_WATER_COUNTERS = ('durable_logical_trace_bytes', 'durable_logical_output_bytes',
                       'process_tree_peak_resident_memory_bytes', 'campaign_calendar_elapsed_seconds')


def fold_attempts(ordered_runs, attempts):
    """Pure cumulative accounting of supplied metadata; no execution.

    All failed work remains charged. A per-run logical high water is summed
    once at the campaign barrier; physical duplicate bytes are never refunded.
    Calendar observations are elapsed from one frozen campaign start, never
    per-run durations. Input ordering is irrelevant; the declared run ordering and ordinal decide.
    """
    if not ordered_runs or len(set(ordered_runs)) != len(ordered_runs): raise Refusal('invalid run order')
    fields = {'run_id', 'attempt_ordinal', *ADDITIVE_COUNTERS, *HIGH_WATER_COUNTERS}
    groups = {run: [] for run in ordered_runs}
    for row in attempts:
        if set(row) != fields or row['run_id'] not in groups: raise Refusal('attempt membership or shape')
        if any(type(row[k]) is not int or row[k] < 0 for k in fields - {'run_id'}): raise Refusal('invalid attempt counter')
        groups[row['run_id']].append(row)
    totals = {key: 0 for key in (*ADDITIVE_COUNTERS, *HIGH_WATER_COUNTERS)}
    per_run = []
    for run in ordered_runs:
        rows = sorted(groups[run], key=lambda row: row['attempt_ordinal'])
        if [r['attempt_ordinal'] for r in rows] != list(range(len(rows))): raise Refusal('missing or duplicate attempt')
        sums = {key: sum(row[key] for row in rows) for key in ADDITIVE_COUNTERS}
        for key in HIGH_WATER_COUNTERS:
            vals = [row[key] for row in rows]
            # Memory is an attempt peak; logical bytes and elapsed time cannot reset.
            if key != 'process_tree_peak_resident_memory_bytes' and vals != sorted(vals): raise Refusal('cumulative high-water reset')
            sums[key] = max(vals, default=0)
        per_run.append({'run_id': run, 'attempt_count': len(rows), **sums})
        for key in ADDITIVE_COUNTERS: totals[key] += sums[key]
        for key in ('durable_logical_trace_bytes', 'durable_logical_output_bytes'): totals[key] += sums[key]
        for key in ('process_tree_peak_resident_memory_bytes', 'campaign_calendar_elapsed_seconds'): totals[key] = max(totals[key], sums[key])
    return {'attempt_count': len(attempts), 'runs': per_run, 'totals': totals}


def verify_recovery_metadata(facts):
    """Require every frozen recovery fact; identity resolution is a later gate."""
    required = ('transient_failure', 'no_post_checkpoint_state_accepted', 'code_identity_unchanged',
                'environment_identity_unchanged', 'failed_costs_retained')
    if set(facts) != {*required, 'independent_audit_identity', 'applicable_recovery_rule_identity'} or any(facts[k] is not True for k in required):
        raise Refusal('recovery conditions incomplete')
    for name in ('independent_audit_identity', 'applicable_recovery_rule_identity'):
        audit = facts[name]
        if not isinstance(audit, dict) or set(audit) != {'kind', 'value', 'sha256'} or not audit['kind']:
            raise Refusal('recovery authority identity missing')
        require_digest(audit['sha256'])
        if audit['value'] != audit['sha256']: raise Refusal('recovery authority identity mismatch')
    return True
