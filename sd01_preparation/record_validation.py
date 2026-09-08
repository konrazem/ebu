"""Frozen v2 record structural validation, never a production binding PASS.

Every input record is complete caller-supplied metadata. No missing control,
identity, field or scientific disposition is synthesized. Cross-record and
host evidence must still be resolved by a future independent binding verifier.
"""
from stage_e_harness.schema import Validator, AUTHORITY_METADATA_KEYS
from .build import source
from .mechanics import Refusal, canonical, strict_load

DEFINITIONS = ('campaign_execution_binding', 'process_allocation', 'attempt_binding',
               'run_resource_ledger', 'campaign_resource_ledger', 'continuation_checkpoint',
               'attempt_manifest', 'continuation_receipt', 'recovery_disposition',
               'infeasibility_finding', 'campaign_terminal_manifest')


def validate_record(definition, record):
    if definition not in DEFINITIONS: raise Refusal('unknown continuation record')
    schema = strict_load(source('stage_d_completion_oriented_continuation_evidence_schema.json'))
    validator = Validator(schema, allowed_metadata=AUTHORITY_METADATA_KEYS)
    validator.validate_definition(definition, record)
    return canonical(record)
