"""Offline complete Gate 1 record construction with local-only schema resolution."""
from __future__ import annotations
import base64,copy,hashlib,json,re,unicodedata
from pathlib import Path
import jsonschema
from referencing import Registry,Resource

ROOT=Path(__file__).resolve().parents[1]
CRT='aws_c0_cost_runtime_retrieval_closure_correction_evidence_schema.json'
REGISTRY='aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json'
LINEAGE='aws_c0_gate1_bootstrap_lineage_correction_contract.json'
SCHEMA_URI='https://ebu.invalid/local/preparation-packet-v4.json'

def canonical(value):
    def check(v):
        if isinstance(v,str):
            if unicodedata.normalize('NFC',v)!=v:raise ValueError('NFC strings required')
            return
        if v is None or isinstance(v,bool):return
        if isinstance(v,int) and not isinstance(v,bool):return
        if isinstance(v,list):
            for item in v:check(item)
            return
        if isinstance(v,dict) and all(isinstance(k,str) for k in v):
            for item in v.values():check(item)
            return
        raise ValueError('integer-only JSON control material required')
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def sha(raw):return hashlib.sha256(raw).hexdigest()
def identity(kind,value):
    digest=sha(canonical(value))
    return {'kind':kind,'value':digest,'sha256':digest}
def preimage(kind,value):
    return {'identity':identity(kind,value),'canonical_json_base64':base64.b64encode(canonical(value)).decode()}

def schema(root):
    parent=json.loads((root/REGISTRY).read_bytes())
    correction=json.loads((root/LINEAGE).read_bytes())
    result=copy.deepcopy(parent['$defs']['preparation_packet_v3'])
    result.update({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':SCHEMA_URI})
    props=result['allOf'][1]['properties']
    assert props['schema']['const']=='aws_c0_preparation_packet/v3'
    props['schema']['const']='aws_c0_preparation_packet/v4'
    assert props['bootstrap_control_candidates']['minItems']==props['bootstrap_control_candidates']['maxItems']==3
    props['bootstrap_control_candidates']['minItems']=props['bootstrap_control_candidates']['maxItems']=6
    assert props['planned_pre_live_object_count']['const']==21
    props['planned_pre_live_object_count']['const']=24
    props['planned_pre_live_record_kinds']['const']=correction['pre_live_record_kinds_in_order']
    def retrieve(uri):
        name=uri.rsplit('/',1)[-1]
        if name not in (CRT,REGISTRY):raise ValueError('unapproved external schema reference')
        return Resource.from_contents(json.loads((root/name).read_bytes()))
    return result,Registry(retrieve=retrieve)

def validate_packet(root,value):
    definition,registry=schema(root)
    jsonschema.Draft202012Validator(definition,registry=registry).validate(value)
    canonical(value)
    kinds=json.loads((root/'aws_c0_cost_runtime_retrieval_closure_correction_contract.json').read_bytes())['identity_kind_by_field']
    for field,wanted in kinds.items():
        if field in value and isinstance(wanted,str):
            got=value[field]
            if not isinstance(got,dict) or got.get('kind')!=wanted or got.get('value')!=got.get('sha256'):
                raise ValueError('packet identity kind/value mismatch: '+field)
    correction=json.loads((root/LINEAGE).read_bytes())
    for candidate,expected in zip(value['bootstrap_control_candidates'],correction['exact_lineage_candidates_in_order']):
        raw=base64.b64decode(candidate['canonical_json_base64'],validate=True)
        document=json.loads(raw)
        if canonical(document)!=raw or sha(raw)!=expected['sha256'] or document['schema']!=expected['kind']:
            raise ValueError('historical bootstrap/renewal bytes changed')
        if candidate['identity']!={'kind':expected['kind'],'value':expected['sha256'],'sha256':expected['sha256']}:
            raise ValueError('historical candidate identity changed')
        if candidate['target']['sha256']!=sha(raw):raise ValueError('candidate target differs from actual bytes')
    for field,bound in value['preapproval_identity_preimages'].items():
        raw=base64.b64decode(bound['canonical_json_base64'],validate=True)
        if canonical(json.loads(raw))!=raw or sha(raw)!=bound['identity']['sha256'] or bound['identity']['value']!=bound['identity']['sha256']:
            raise ValueError('preapproval contract identity mismatch: '+field)
        field_name=field+'_identity'
        if field_name in value and value[field_name]!=bound['identity']:
            raise ValueError('packet does not bind its exact preapproval contract: '+field)
    for row in value['initial_prestate_control_preimages']:
        raw=base64.b64decode(row['canonical_json_base64'],validate=True)
        if canonical(json.loads(raw))!=raw or sha(raw)!=row['identity']['sha256'] or row['identity']['value']!=row['identity']['sha256']:
            raise ValueError('initial prestate identity mismatch')
    if [v['control_kind'] for v in value['initial_prestate_control_preimages']]!=[
        'ACCOUNT_REGION','INSTANCE_PROFILE_SOLE_ROLE','IAM_POLICY_SET','BUCKET_CONTROLS_KMS','VPC_NETWORK_PATH','SERVICE_QUOTA']:
        raise ValueError('six ordered current preimages required')
    if [v['artifact_class'] for v in value['artifact_targets']]!=[
        'STATE_MACHINE_DEFINITION','SSM_DOCUMENT','CONTROLLER','SYSTEMD_UNIT','FINALIZER_ZIP',
        'SYNTHETIC_IMAGE_ARCHIVE','CONTAINER_RUNTIME_POLICY','CLOUDFORMATION_TEMPLATE']:
        raise ValueError('eight ordered artifact targets required')
    for target in [v['target'] for v in value['artifact_targets']]:
        if target['if_none_match']!='*' or 'version_id' in target:
            raise ValueError('preapproval artifact must be conditional and have no future version')
    return value

def build(root,fields):
    definition,_=schema(root)
    inherited=json.loads((root/CRT).read_bytes())['$defs']['common']['required']
    required=set(inherited)|set(definition['allOf'][1]['required'])
    if set(fields)!=required:
        raise ValueError('complete packet field set required; missing='+','.join(sorted(required-set(fields)))+
                         '; extra='+','.join(sorted(set(fields)-required)))
    return validate_packet(root,copy.deepcopy(fields))
