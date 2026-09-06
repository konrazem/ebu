"""Deterministic offline derivation of NEW schemas; never edits historical ones."""
import argparse
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT='aws_c0_deployment_sequence_evidence_schema.json'
CRT='aws_c0_cost_runtime_retrieval_closure_correction_evidence_schema.json'
REG='aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json'

def build(root=ROOT):
    lineage=json.loads((root/'aws_c0_gate1_bootstrap_lineage_correction_contract.json').read_bytes())
    sequence=json.loads((root/'aws_c0_deployment_sequence_correction_contract.json').read_bytes())
    prior={r['from']:r['to'] for r in lineage['required_version_upgrades']+lineage['required_transitive_version_upgrades']}
    current=sequence['version_upgrades']
    documents={};definitions={};names={}
    def upgrade(value):return current.get(prior.get(value,value),prior.get(value,value))
    def document(name):
        if name not in documents:
            if '/' in name or not name.startswith('aws_c0_') or not name.endswith('_evidence_schema.json'):
                raise ValueError('non-local schema dependency refused')
            documents[name]=json.loads((root/name).read_bytes())
        return documents[name]
    def include(filename,key):
        key=key if key.startswith('/') else '/$defs/'+key
        pair=(filename,key)
        if pair in names:return '#/$defs/'+names[pair]
        name='d'+str(len(names))+'_'+key.rsplit('/',1)[-1];names[pair]=name;definitions[name]={}
        def walk(v):
            if isinstance(v,list):return [walk(x) for x in v]
            if isinstance(v,str):return upgrade(v)
            if not isinstance(v,dict):return v
            result={k:walk(x) for k,x in v.items()}
            if '$ref' in v:
                target,fragment=v['$ref'].split('#',1)
                if not fragment.startswith('/'):
                    raise ValueError('unsupported reference projection: '+v['$ref'])
                result['$ref']=include(target or filename,fragment)
            for field,prop in result.get('properties',{}).items():
                if field in ('bootstrap_control_candidates','bootstrap_control_objects') and prop.get('minItems')==3:
                    prop['minItems']=prop['maxItems']=6
                if field in ('runtime_control_preimages','final_runtime_control_preimages') and prop.get('maxItems')==11:
                    prop['maxItems']=9
                    if prop.get('minItems')==11:prop['minItems']=9
                if field=='pre_live_predecessor_object_receipts' and prop.get('minItems')==20:
                    prop['minItems']=prop['maxItems']=23
                if field=='published_object_receipts' and prop.get('minItems')==19:
                    prop['minItems']=prop['maxItems']=22
                if field in ('planned_pre_live_object_count','pre_live_object_count','pre_live_object_count_after_live_packet') and prop.get('const')==21:
                    prop['const']=24
                if field=='objects_published_before_closure' and prop.get('const')==19:prop['const']=22
                if field=='planned_pre_live_record_kinds':prop['const']=[current.get(k,k) for k in lineage['pre_live_record_kinds_in_order']]
            return result
        source=document(filename)
        pointer=key if key.startswith('/') else '/$defs/'+key
        for part in pointer[1:].split('/'):
            decoded=part.replace('~1','/').replace('~0','~')
            source=source[int(decoded)] if isinstance(source,list) else source[decoded]
        definitions[name]=walk(copy.deepcopy(source))
        return '#/$defs/'+name
    records={
        'closure_seed':(CRT,'closure_seed','aws_c0_closure_seed/v2'),
        'preparation_packet':(REG,'preparation_packet_v3','aws_c0_preparation_packet/v5'),
        'preparation_authorization':(REG,'preparation_authorization_v2','aws_c0_preparation_authorization/v4'),
        'launch':(REG,'launch_v4','aws_c0_launch_request/v6'),
        'preparation_closure':(REG,'preparation_closure_v3','aws_c0_preparation_closure/v5'),
        'live_packet':(REG,'live_packet_v4','aws_c0_live_packet/v6'),
        'live_authorization':(REG,'live_authorization_v4','aws_c0_live_authorization/v6')}
    identity_ref=include(CRT,'identity');base64_ref=include(CRT,'canonical_json_base64')
    control_ref=include(CRT,'control_preimage');time_ref=include(CRT,'timestamp')
    for alias,(filename,key,kind) in records.items():
        target=include(filename,key);definition=definitions[target.rsplit('/',1)[-1]]
        body=definition['allOf'][1];props=body['properties'];props['schema']={'const':kind}
        def add(field,value):
            if field not in body['required']:body['required'].append(field)
            props[field]=value
        add('material_correction_authority_id',{'const':'EBU-AWS-C0-MATERIAL-IDENTITY-RUNTIME-VALIDATION-CORRECTION-AUTHORITY-v1'})
        if alias=='closure_seed':
            body['required'].remove('state_machine_identity');del props['state_machine_identity']
            add('deployment_inputs_identity',{'$ref':identity_ref})
            add('deployment_inputs_canonical_json_base64',{'$ref':base64_ref})
        if alias in ('preparation_closure','live_packet','live_authorization'):
            add('deployment_inputs_identity',{'$ref':identity_ref})
        if alias=='live_authorization':
            for field in ('deployment_authorized_utc','deployment_started_utc','deployment_completed_utc'):add(field,{'$ref':time_ref})
            add('post_deployment_control_preimages',{'type':'array','minItems':11,'maxItems':11,'items':{'$ref':control_ref}})
            props['authorized_actions']['const']=['EXECUTE_EXACT_CHANGE_SET','PUBLISH_EXACT_LIVE_AUTHORIZATION','START_ONE_EXACT_EXECUTION']
        definitions[alias]={'$ref':target}
    # Prospective R51 result: clone, never relax the accepted HTTP200 receipt.
    original=next(v for k,v in definitions.items() if k.endswith('_api_request_response_receipt'))
    receipt=copy.deepcopy(original)
    receipt['required'].append('schema')
    receipt['properties'].update(schema={'const':'aws_c0_r51_api_request_response_receipt/v2'},
        row_id={'const':'R51'},action={'const':'lambda:GetPolicy'},resource_selector={'const':'SEALED_FINALIZER_FUNCTION_ARN'},
        http_status={'enum':[200,404]},api_success_disposition={'enum':['AWS_API_CALL_SUCCESS','AWS_API_RESOURCE_NOT_FOUND']})
    receipt['allOf']=[{'if':{'properties':{'http_status':{'const':200}}},
        'then':{'properties':{'api_success_disposition':{'const':'AWS_API_CALL_SUCCESS'}}},
        'else':{'properties':{'api_success_disposition':{'const':'AWS_API_RESOURCE_NOT_FOUND'}}}}]
    definitions['r51_receipt_v2']=receipt
    existence=[]
    for row,action in [('R49','GetFunction'),('R50','GetFunctionConfiguration')]:
        item=copy.deepcopy(original)
        item['properties'].update(row_id={'const':row},action={'const':'lambda:'+action},
                                  resource_selector={'const':'SEALED_FINALIZER_FUNCTION_ARN'})
        existence.append(item)
    fields={'schema':{'const':'aws_c0_lambda_resource_policy_observation/v2'},
        'target_function_arn':{'const':'arn:aws:lambda:us-east-1:623609441658:function:ebu-c0-corrected-finalizer-v1'},
        'observed_utc':{'$ref':time_ref},'freshness_max_seconds':{'type':'integer','minimum':1,'maximum':300},
        'outcome':{'enum':['POLICY_PRESENT','POLICY_ABSENT']},'policy':{'type':['object','null']},
        'policy_receipt':{'$ref':'#/$defs/r51_receipt_v2'},
        'function_existence_receipts_in_order':{'type':'array','minItems':2,'maxItems':2,'prefixItems':existence,'items':False}}
    definitions['r51_policy_result_v2']={'type':'object','required':list(fields),'properties':fields,'additionalProperties':False,
        'allOf':[{'if':{'properties':{'outcome':{'const':'POLICY_ABSENT'}}},
                  'then':{'properties':{'policy':{'type':'null'},'policy_receipt':{'properties':{'http_status':{'const':404}}}}},
                  'else':{'properties':{'policy':{'type':'object'},'policy_receipt':{'properties':{'http_status':{'const':200}}}}}}]}
    definitions['r51_result']={'$ref':'#/$defs/r51_policy_result_v2'}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
            '$id':'https://ebu.invalid/schema/aws-c0-deployment-sequence-v1.json',
            'description':'New versioned sequencing schemas; historical source schemas remain unchanged.',
            'oneOf':[{'$ref':'#/$defs/'+name} for name in list(records)+['r51_result']], '$defs':definitions}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    raw=(json.dumps(build(),indent=2,ensure_ascii=False)+'\n').encode();path=ROOT/OUTPUT
    if args.check:
        if path.read_bytes()!=raw:raise SystemExit('derived sequence schema differs')
    else:path.write_bytes(raw)
    print('sequence schema deterministic check PASS' if args.check else 'sequence schema generated locally')

if __name__=='__main__':main()
