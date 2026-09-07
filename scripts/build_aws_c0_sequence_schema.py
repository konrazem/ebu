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
    helper_fields={'schema':{'const':'aws_c0_controller_local_helper_request/v1'},
        'operation':{'enum':['STATUS','SAFE_CLOSE']},
        'start_dispatch_request':{'$ref':include('aws_c0_audit_static_publication_handoff_correction_evidence_schema.json','ssm_dispatch_request_v2')},
        'attempt_deadline_utc':{'$ref':time_ref}}
    definitions['local_helper_request_v1']={'type':'object','required':list(helper_fields),
        'properties':helper_fields,'additionalProperties':False}
    definitions['ssm_local_helper_request']={'$ref':'#/$defs/local_helper_request_v1'}
    # A new read-plan kind, never a global upgrade of the historical v1 plan.
    read_contract=json.loads((root/'aws_c0_material_identity_runtime_validation_correction_contract.json').read_bytes())['sealed_read_plan']
    r64={'id':'R64','action':'ec2:DescribeSecurityGroups','resource_selector':'*',
        'use':'ALWAYS','control':'VPC_NETWORK_PATH','condition':'ALWAYS','call_requirement':'ALWAYS',
        'pagination_bounds':{'max_pages':1,'max_items':16},
        'reconstruction_output_kind':'aws_c0_vpc_network_observation/v2'}
    read_v2=copy.deepcopy(next(v for k,v in definitions.items() if k.endswith('_runtime_control_read_plan')))
    mapping=copy.deepcopy(read_contract['required_control_mapping'])
    owner=next(v for v in mapping if v['control']=='VPC_NETWORK_PATH')
    owner['row_ids'].append('R64');owner['output_schema']=owner['output_kind']='aws_c0_vpc_network_observation/v2'
    read_v2['required']+=['original_read_plan_identity','amendment_packet_identity']
    def typed_identity(kind):return {'allOf':[{'$ref':identity_ref},{'properties':{'kind':{'const':kind}}}]}
    read_v2['properties'].update(schema={'const':'aws_c0_runtime_control_read_plan/v2'},
        rows={'const':copy.deepcopy(read_contract['rows'])+[r64]},
        row_ids={'const':['R%02d'%i for i in range(1,65)]},required_control_mapping={'const':mapping},
        original_read_plan_identity=typed_identity('aws_c0_runtime_control_read_plan/v1'),
        amendment_packet_identity=typed_identity('aws_c0_network_ingress_source_authority_amendment_packet/v1'))
    definitions['read_plan_r64_v2']=read_v2
    definitions['runtime_read_plan_v2']={'$ref':'#/$defs/read_plan_r64_v2'}
    current_packet=definitions[definitions['live_packet']['$ref'].rsplit('/',1)[-1]]['allOf'][1]['properties']
    current_packet['runtime_control_read_plan']={'$ref':'#/$defs/read_plan_r64_v2'}
    current_packet['runtime_control_read_plan_identity']=typed_identity('aws_c0_runtime_control_read_plan/v2')
    r64_receipt=copy.deepcopy(original)
    r64_receipt['required'].append('schema')
    r64_receipt['properties'].update(schema={'const':'aws_c0_r64_api_request_response_receipt/v1'},
        row_id={'const':'R64'},action={'const':'ec2:DescribeSecurityGroups'},resource_selector={'const':'*'},
        pagination_page={'const':1},pagination_item_count={'type':'integer','minimum':1,'maximum':16})
    definitions['r64_receipt_v1']=r64_receipt
    definitions['r64_receipt']={'$ref':'#/$defs/r64_receipt_v1'}
    source_receipts=[]
    for row,action in [('R02','DescribeInstances'),('R04','DescribeNetworkInterfaces')]:
        source=copy.deepcopy(original)
        source['properties'].update(row_id={'const':row},action={'const':'ec2:'+action},resource_selector={'const':'*'},
            pagination_page={'const':1},pagination_item_count={'type':'integer','minimum':1,'maximum':16})
        source_receipts.append(source)
    zero_science=copy.deepcopy(definitions[definitions['live_packet']['$ref'].rsplit('/',1)[-1]])
    # Resolve common only to copy the fixed science-counter contract.
    common=definitions[zero_science['allOf'][0]['$ref'].rsplit('/',1)[-1]]
    ingress_fields={'schema':{'const':'aws_c0_network_ingress_observation/v1'},
        'amendment_packet_identity':typed_identity('aws_c0_network_ingress_source_authority_amendment_packet/v1'),
        'attempt_identity':typed_identity('aws_c0_attempt/v1'),'observed_utc':{'$ref':time_ref},
        'freshness_max_seconds':{'type':'integer','minimum':1,'maximum':300},
        'instance_id':{'const':'i-048bac00bdb540a4e'},'vpc_id':{'type':'string','pattern':'^vpc-[0-9a-f]{8,17}$'},
        'security_group_ids':{'type':'array','minItems':1,'maxItems':16,'uniqueItems':True,
                              'items':{'type':'string','pattern':'^sg-[0-9a-f]{8,17}$'}},
        'ingress_rule_count':{'type':'integer','const':0},
        'source_receipts_in_order':{'type':'array','minItems':2,'maxItems':2,'prefixItems':source_receipts,'items':False},
        'rule_receipt':{'$ref':'#/$defs/r64_receipt_v1'},'zero_science_counters':copy.deepcopy(common['properties']['zero_science_counters'])}
    definitions['network_ingress_observation_v1']={'type':'object','required':list(ingress_fields),
        'properties':ingress_fields,'additionalProperties':False}
    definitions['network_ingress_observation']={'$ref':'#/$defs/network_ingress_observation_v1'}
    nullable_time={'anyOf':[{'$ref':time_ref},{'type':'null'}]}
    nullable_observation={'anyOf':[typed_identity('aws_c0_network_ingress_observation/v1'),{'type':'null'}]}
    reservation_fields={'ordinal':{'type':'integer','minimum':1,'maximum':3},
        'phase':{'enum':['PREDEPLOYMENT','POSTDEPLOYMENT','EXECUTION_PREFLIGHT']},
        'reserved_utc':{'$ref':time_ref},'caller_identity':{'$ref':identity_ref},
        'authentication_source_identity':{'$ref':identity_ref},
        'request':{'type':'object','required':['GroupIds'],'additionalProperties':False,
            'properties':{'GroupIds':copy.deepcopy(ingress_fields['security_group_ids'])}},
        'source_receipt_identities_in_order':{'type':'array','minItems':2,'maxItems':2,'uniqueItems':True,
            'items':typed_identity('aws_c0_api_request_response_receipt/v1')},
        'state':{'enum':['RESERVED','OBSERVED_SUCCESS','OBSERVED_FAILURE']},
        'finished_utc':nullable_time,'observation_identity':nullable_observation,
        'request_id':{'anyOf':[{'type':'string','pattern':'^[A-Za-z0-9-]{8,128}$'},{'type':'null'}]},
        'failure_class':{'enum':[None,'TRANSPORT_FAILURE','UNCERTAIN_DELIVERY','INVALID_RESPONSE']}}
    reservation={'type':'object','required':list(reservation_fields),'properties':reservation_fields,'additionalProperties':False,
        'allOf':[{'if':{'properties':{'state':{'const':'RESERVED'}}},
            'then':{'properties':{k:{'type':'null'} for k in ('finished_utc','observation_identity','request_id','failure_class')}},
            'else':{'properties':{'finished_utc':{'$ref':time_ref}}}},
            {'if':{'properties':{'state':{'const':'OBSERVED_SUCCESS'}}},
            'then':{'properties':{'observation_identity':typed_identity('aws_c0_network_ingress_observation/v1'),
                'request_id':{'type':'string','pattern':'^[A-Za-z0-9-]{8,128}$'},'failure_class':{'type':'null'}}}},
            {'if':{'properties':{'state':{'const':'OBSERVED_FAILURE'}}},
            'then':{'properties':{'observation_identity':{'type':'null'},'request_id':{'type':'null'},
                'failure_class':{'enum':['TRANSPORT_FAILURE','UNCERTAIN_DELIVERY','INVALID_RESPONSE']}}}}]}
    budget_fields={'schema':{'const':'aws_c0_network_ingress_call_budget/v1'},
        'amendment_packet_identity':typed_identity('aws_c0_network_ingress_source_authority_amendment_packet/v1'),
        'attempt_identity':typed_identity('aws_c0_attempt/v1'),
        'reservations_in_order':{'type':'array','minItems':0,'maxItems':3,'items':reservation}}
    definitions['network_ingress_call_budget_v1']={'type':'object','required':list(budget_fields),
        'properties':budget_fields,'additionalProperties':False}
    definitions['network_ingress_call_budget']={'$ref':'#/$defs/network_ingress_call_budget_v1'}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
            '$id':'https://ebu.invalid/schema/aws-c0-deployment-sequence-v1.json',
            'description':'New versioned sequencing schemas; historical source schemas remain unchanged.',
            'oneOf':[{'$ref':'#/$defs/'+name} for name in list(records)+['r51_result','ssm_local_helper_request','runtime_read_plan_v2','r64_receipt','network_ingress_observation','network_ingress_call_budget']], '$defs':definitions}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    raw=(json.dumps(build(),indent=2,ensure_ascii=False)+'\n').encode();path=ROOT/OUTPUT
    if args.check:
        if path.read_bytes()!=raw:raise SystemExit('derived sequence schema differs')
    else:path.write_bytes(raw)
    print('sequence schema deterministic check PASS' if args.check else 'sequence schema generated locally')

if __name__=='__main__':main()
