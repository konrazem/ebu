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
    original_ref='#/$defs/'+next(k for k in definitions if k.endswith('_api_request_response_receipt'))
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
    read_v3=copy.deepcopy(read_v2);mapping_v3=copy.deepcopy(mapping)
    iam_owner=next(v for v in mapping_v3 if v['control']=='IAM_POLICY_SET')
    iam_owner['output_schema']=iam_owner['output_kind']='aws_c0_iam_policy_set_observation/v2'
    read_v3['required']+=['previous_read_plan_identity','iam_source_mapping_authority_id']
    read_v3['properties'].update(schema={'const':'aws_c0_runtime_control_read_plan/v3'},
        required_control_mapping={'const':mapping_v3},
        previous_read_plan_identity=typed_identity('aws_c0_runtime_control_read_plan/v2'),
        iam_source_mapping_authority_id={'const':'EBU-AWS-C0-IAM-RECONSTRUCTION-SOURCE-MAPPING-AMENDMENT-v1'})
    read_v4=copy.deepcopy(read_v3);mapping_v4=copy.deepcopy(mapping_v3)
    change_owner=next(v for v in mapping_v4 if v['control']=='CHANGE_SET_AND_EFFECTS')
    change_owner['conditional_use']='R47_R48_ONLY_WHEN_STACK_EXISTS_IN_CURRENT_PHASE'
    rows_v4=copy.deepcopy(read_contract['rows'])+[r64]
    for row in rows_v4:
        if row['id'] in ('R47','R48'):
            row.update(use='CONDITIONAL',condition='WHEN_STACK_EXISTS_IN_CURRENT_PHASE',call_requirement='CONDITIONAL')
    read_v4['required']+=['chronology_predecessor_identity','change_set_phase_chronology_authority_id']
    read_v4['properties'].update(schema={'const':'aws_c0_runtime_control_read_plan/v4'},rows={'const':rows_v4},
        required_control_mapping={'const':mapping_v4},
        chronology_predecessor_identity=typed_identity('aws_c0_runtime_control_read_plan/v3'),
        change_set_phase_chronology_authority_id={'const':'EBU-AWS-C0-CHANGE-SET-PHASE-CHRONOLOGY-AUTHORITY-v1'})
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
    binding_fields={'schema':{'const':'aws_c0_network_ingress_phase_binding/v1'},
        'phase':{'enum':['PREDEPLOYMENT','POSTDEPLOYMENT','EXECUTION_PREFLIGHT']},
        'attempt_identity':typed_identity('aws_c0_attempt/v1'),'read_plan_identity':typed_identity('aws_c0_runtime_control_read_plan/v2'),
        'previous_call_budget_identity':typed_identity('aws_c0_network_ingress_call_budget/v1'),
        'call_budget':{'$ref':'#/$defs/network_ingress_call_budget_v1'},
        'call_budget_identity':typed_identity('aws_c0_network_ingress_call_budget/v1'),
        'ingress_observation':{'$ref':'#/$defs/network_ingress_observation_v1'},
        'ingress_observation_identity':typed_identity('aws_c0_network_ingress_observation/v1')}
    definitions['network_ingress_phase_binding_v1']={'type':'object','required':list(binding_fields),
        'properties':binding_fields,'additionalProperties':False}
    definitions['network_ingress_phase_binding']={'$ref':'#/$defs/network_ingress_phase_binding_v1'}
    decoded_vpc=copy.deepcopy(next(v for k,v in definitions.items() if k.endswith('_decoded_vpc_network_observation')))
    decoded_vpc['required']+=['attached_subnet_ids','instance_source_receipt_identity','ingress_phase_binding_identity','ec2_pagination_bounds']
    decoded_vpc['properties'].update(schema={'const':'aws_c0_vpc_network_observation_preimage/v2'},
        source_row_ids={'const':['R%02d'%i for i in range(4,13)]+['R64']},
        attached_subnet_ids={'type':'array','minItems':1,'maxItems':16,'uniqueItems':True,
            'items':copy.deepcopy(decoded_vpc['properties']['subnet_id'])},
        instance_source_receipt_identity=typed_identity('aws_c0_api_request_response_receipt/v1'),
        ec2_pagination_bounds={'type':'object','required':['max_pages','max_items'],'additionalProperties':False,
            'properties':{k:{'type':'integer','minimum':1} for k in ('max_pages','max_items')}},
        ingress_phase_binding_identity=typed_identity('aws_c0_network_ingress_phase_binding/v1'))
    decoded_vpc['properties']['ingress_rule_count']={'type':'integer','const':0}
    definitions['vpc_network_decoded_v2']=decoded_vpc
    output_union=next(v for k,v in definitions.items() if k.endswith('_reconstruction_output_tagged_union'))
    definitions['account_region_reconstruction_output']=copy.deepcopy(next(v for v in output_union['oneOf']
        if v['properties']['control']['const']=='ACCOUNT_REGION'))
    definitions['account_region_output']={'$ref':'#/$defs/account_region_reconstruction_output'}
    definitions['instance_profile_reconstruction_output']=copy.deepcopy(next(v for v in output_union['oneOf']
        if v['properties']['control']['const']=='INSTANCE_PROFILE_SOLE_ROLE'))
    definitions['instance_profile_output']={'$ref':'#/$defs/instance_profile_reconstruction_output'}
    definitions['service_quota_reconstruction_output']=copy.deepcopy(next(v for v in output_union['oneOf']
        if v['properties']['control']['const']=='SERVICE_QUOTA'))
    definitions['service_quota_output']={'$ref':'#/$defs/service_quota_reconstruction_output'}
    definitions['bucket_controls_kms_reconstruction_output']=copy.deepcopy(next(v for v in output_union['oneOf']
        if v['properties']['control']['const']=='BUCKET_CONTROLS_KMS'))
    definitions['bucket_controls_kms_output']={'$ref':'#/$defs/bucket_controls_kms_reconstruction_output'}
    output_artifact=copy.deepcopy(next(v for v in output_union['oneOf']
        if v['properties']['control']['const']=='ARTIFACT_VERSION_SET'))
    decoded_iam=copy.deepcopy(next(v for k,v in definitions.items() if k.endswith('_decoded_iam_policy_set_observation')))
    decoded_iam['properties'].update(schema={'const':'aws_c0_iam_policy_set_observation_preimage/v2'},
        source_row_ids={'const':['R15','R16','R17','R18','R19']})
    output_iam=copy.deepcopy(next(v for v in output_union['oneOf'] if v['properties']['control']['const']=='IAM_POLICY_SET'))
    output_iam['properties'].update(schema={'const':'aws_c0_iam_policy_set_observation/v2'},
        kind={'const':'aws_c0_iam_policy_set_observation/v2'},
        identity=typed_identity('aws_c0_iam_policy_set_observation/v2'),
        decoded_json={'$ref':'#/$defs/iam_policy_set_decoded_v2'})
    iam_binding_fields={'schema':{'const':'aws_c0_iam_role_context_binding/v1'},
        'authority_id':{'const':'EBU-AWS-C0-IAM-CROSS-CONTROL-SOURCE-BINDING-AUTHORITY-v1'},
        'read_plan_identity':typed_identity('aws_c0_runtime_control_read_plan/v3'),
        'source_control':{'const':'INSTANCE_PROFILE_SOLE_ROLE'},'source_row_id':{'const':'R14'},
        'target_control':{'const':'IAM_POLICY_SET'},
        'instance_profile_output_identity':typed_identity('aws_c0_instance_profile_role_observation/v1'),
        'r14_receipt_identity':typed_identity('aws_c0_api_request_response_receipt/v1'),
        'role_arn':{'type':'string','pattern':'^arn:aws:'},
        'instance_profile_arn':{'type':'string','pattern':'^arn:aws:'},
        'assume_role_policy_sha256':copy.deepcopy(decoded_iam['properties']['assume_role_policy_sha256']),
        'disposition':{'const':'AUTHENTICATED_EXISTING_R14_CROSS_CONTROL_BINDING_PASS'}}
    output_vpc=copy.deepcopy(next(v for v in output_union['oneOf'] if v['properties']['control']['const']=='VPC_NETWORK_PATH'))
    output_vpc['properties'].update(schema={'const':'aws_c0_vpc_network_observation/v2'},kind={'const':'aws_c0_vpc_network_observation/v2'},
        identity=typed_identity('aws_c0_vpc_network_observation/v2'),decoded_json={'$ref':'#/$defs/vpc_network_decoded_v2'})
    definitions['vpc_network_reconstruction_output_v2']=output_vpc
    definitions['vpc_network_output_v2']={'$ref':'#/$defs/vpc_network_reconstruction_output_v2'}
    progress_slot={'type':'object','required':['control','mapped_row_ids','state','output','output_identity'],
        'properties':{'control':{'type':'string'},'mapped_row_ids':{'type':'array','minItems':1,'maxItems':16,
            'items':{'type':'string','pattern':'^R[0-9]{2}$'}},
            'state':{'enum':['CANONICAL_OUTPUT_CANDIDATE','UNRESOLVED']},
            'output':{'type':['object','null']},'output_identity':{'type':['object','null']}},'additionalProperties':False}
    progress_fields={'schema':{'const':'aws_c0_runtime_control_reconstruction_progress/v2'},
        'read_plan_identity':typed_identity('aws_c0_runtime_control_read_plan/v2'),
        'phase':{'enum':['PREDEPLOYMENT','POSTDEPLOYMENT','EXECUTION_PREFLIGHT','COMPLETION']},
        'observed_utc':{'$ref':time_ref},'controls_in_order':{'type':'array','minItems':11,'maxItems':11,
            'prefixItems':[copy.deepcopy(progress_slot) for _ in range(11)],'items':False},
        'candidate_control_ids_in_order':{'type':'array','maxItems':4,'uniqueItems':True,'items':{'type':'string'}},
        'unresolved_control_ids_in_order':{'type':'array','minItems':1,'maxItems':11,'uniqueItems':True,'items':{'type':'string'}},
        'source_revalidation_performed':{'const':False},'complete_reconstruction_claimed':{'const':False},'disposition':{'const':'PARTIAL_NOT_READY'}}
    definitions['runtime_reconstruction_progress_v2_definition']={'type':'object','required':list(progress_fields),
        'properties':progress_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_progress_v2']={'$ref':'#/$defs/runtime_reconstruction_progress_v2_definition'}
    attachment_fields={'schema':{'const':'aws_c0_runtime_control_reconstruction_source_attachment/v1'},
        'read_plan_identity':typed_identity('aws_c0_runtime_control_read_plan/v2'),
        'phase':{'const':'PREDEPLOYMENT'},'validation_utc':{'$ref':time_ref},
        'sealed_context':{'type':'object'},'sealed_context_identity':typed_identity('aws_c0_predeployment_reconstruction_context/v1'),
        'source_bundles_in_order':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'object'}},
        'outputs_in_order':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'object'}},
        'source_revalidation_performed':{'const':True},'complete_reconstruction_claimed':{'const':False},
        'disposition':{'const':'PARTIAL_SOURCE_BOUND_NOT_READY'}}
    definitions['runtime_reconstruction_source_attachment_v1_definition']={'type':'object',
        'required':list(attachment_fields),'properties':attachment_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_source_attachment_v1']={'$ref':'#/$defs/runtime_reconstruction_source_attachment_v1_definition'}
    progress_v3_fields=copy.deepcopy(progress_fields)
    progress_v3_fields.update(schema={'const':'aws_c0_runtime_control_reconstruction_progress/v3'},
        read_plan_identity=typed_identity('aws_c0_runtime_control_read_plan/v3'))
    progress_v3_fields['candidate_control_ids_in_order']['maxItems']=5
    attachment_v2_fields=copy.deepcopy(attachment_fields)
    attachment_v2_fields.update(schema={'const':'aws_c0_runtime_control_reconstruction_source_attachment/v2'},
        read_plan_identity=typed_identity('aws_c0_runtime_control_read_plan/v3'),
        previous_source_attachment_identity=typed_identity('aws_c0_runtime_control_reconstruction_source_attachment/v1'),
        sealed_context_identity=typed_identity('aws_c0_predeployment_reconstruction_context/v2'))
    for field in ('source_bundles_in_order','outputs_in_order'):
        attachment_v2_fields[field]['minItems']=attachment_v2_fields[field]['maxItems']=5
    progress_v4_fields=copy.deepcopy(progress_v3_fields)
    progress_v4_fields['schema']={'const':'aws_c0_runtime_control_reconstruction_progress/v4'}
    progress_v4_fields['candidate_control_ids_in_order']['maxItems']=6
    attachment_v3_fields=copy.deepcopy(attachment_v2_fields)
    attachment_v3_fields.update(schema={'const':'aws_c0_runtime_control_reconstruction_source_attachment/v3'},
        previous_source_attachment_identity=typed_identity('aws_c0_runtime_control_reconstruction_source_attachment/v2'),
        sealed_context_identity=typed_identity('aws_c0_predeployment_reconstruction_context/v3'))
    for field in ('source_bundles_in_order','outputs_in_order'):
        attachment_v3_fields[field]['minItems']=attachment_v3_fields[field]['maxItems']=6
    progress_v5_fields=copy.deepcopy(progress_v4_fields)
    progress_v5_fields['schema']={'const':'aws_c0_runtime_control_reconstruction_progress/v5'}
    progress_v5_fields['candidate_control_ids_in_order']['maxItems']=7
    attachment_v4_fields=copy.deepcopy(attachment_v3_fields)
    attachment_v4_fields.update(schema={'const':'aws_c0_runtime_control_reconstruction_source_attachment/v4'},
        previous_source_attachment_identity=typed_identity('aws_c0_runtime_control_reconstruction_source_attachment/v3'),
        sealed_context_identity=typed_identity('aws_c0_predeployment_reconstruction_context/v4'))
    for field in ('source_bundles_in_order','outputs_in_order'):
        attachment_v4_fields[field]['minItems']=attachment_v4_fields[field]['maxItems']=7
    include(CRT,'pagination_transcript')
    # Append prospective definitions so regenerating the ordered registry does
    # not reorder any historical definition.
    definitions['read_plan_iam_v3']=read_v3
    definitions['runtime_read_plan_v3']={'$ref':'#/$defs/read_plan_iam_v3'}
    definitions['iam_policy_set_decoded_v2']=decoded_iam
    definitions['iam_policy_set_reconstruction_output_v2']=output_iam
    definitions['iam_policy_set_output_v2']={'$ref':'#/$defs/iam_policy_set_reconstruction_output_v2'}
    definitions['iam_role_context_binding_v1_definition']={'type':'object',
        'required':list(iam_binding_fields),'properties':iam_binding_fields,'additionalProperties':False}
    definitions['iam_role_context_binding']={'$ref':'#/$defs/iam_role_context_binding_v1_definition'}
    definitions['runtime_reconstruction_progress_v3_definition']={'type':'object',
        'required':list(progress_v3_fields),'properties':progress_v3_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_progress_v3']={'$ref':'#/$defs/runtime_reconstruction_progress_v3_definition'}
    definitions['runtime_reconstruction_source_attachment_v2_definition']={'type':'object',
        'required':list(attachment_v2_fields),'properties':attachment_v2_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_source_attachment_v2']={'$ref':'#/$defs/runtime_reconstruction_source_attachment_v2_definition'}
    definitions['runtime_reconstruction_progress_v4_definition']={'type':'object',
        'required':list(progress_v4_fields),'properties':progress_v4_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_progress_v4']={'$ref':'#/$defs/runtime_reconstruction_progress_v4_definition'}
    definitions['runtime_reconstruction_source_attachment_v3_definition']={'type':'object',
        'required':list(attachment_v3_fields),'properties':attachment_v3_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_source_attachment_v3']={'$ref':'#/$defs/runtime_reconstruction_source_attachment_v3_definition'}
    definitions['artifact_version_set_reconstruction_output']=output_artifact
    definitions['artifact_version_set_output']={'$ref':'#/$defs/artifact_version_set_reconstruction_output'}
    content_binding_fields={'schema':{'const':'aws_c0_s3_exact_version_content_binding/v1'},
        'api_receipt':{'$ref':original_ref},
        'api_receipt_identity':typed_identity('aws_c0_api_request_response_receipt/v1'),
        'body_byte_count':{'type':'integer','minimum':1},
        'body_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
        'body_checksum_sha256_base64':{'type':'string','pattern':'^[A-Za-z0-9+/]{43}=$'},
        'body_fully_consumed':{'const':True},
        'disposition':{'const':'EXACT_VERSION_BODY_FULLY_CONSUMED_SHA256_AND_SERVER_CHECKSUM_BOUND'}}
    definitions['s3_exact_version_content_binding_v1_definition']={'type':'object',
        'required':list(content_binding_fields),'properties':content_binding_fields,'additionalProperties':False}
    definitions['s3_exact_version_content_binding']={'$ref':'#/$defs/s3_exact_version_content_binding_v1_definition'}
    definitions['runtime_reconstruction_progress_v5_definition']={'type':'object',
        'required':list(progress_v5_fields),'properties':progress_v5_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_progress_v5']={'$ref':'#/$defs/runtime_reconstruction_progress_v5_definition'}
    definitions['runtime_reconstruction_source_attachment_v4_definition']={'type':'object',
        'required':list(attachment_v4_fields),'properties':attachment_v4_fields,'additionalProperties':False}
    definitions['runtime_reconstruction_source_attachment_v4']={'$ref':'#/$defs/runtime_reconstruction_source_attachment_v4_definition'}
    definitions['read_plan_change_set_chronology_v4']=read_v4
    definitions['runtime_read_plan_v4']={'$ref':'#/$defs/read_plan_change_set_chronology_v4'}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
            '$id':'https://ebu.invalid/schema/aws-c0-deployment-sequence-v1.json',
            'description':'New versioned sequencing schemas; historical source schemas remain unchanged.',
            'oneOf':[{'$ref':'#/$defs/'+name} for name in list(records)+['r51_result','ssm_local_helper_request','runtime_read_plan_v2','runtime_read_plan_v3','r64_receipt','network_ingress_observation','network_ingress_call_budget','network_ingress_phase_binding','vpc_network_output_v2','account_region_output','instance_profile_output','service_quota_output','iam_policy_set_output_v2','iam_role_context_binding','runtime_reconstruction_progress_v2','runtime_reconstruction_source_attachment_v1','runtime_reconstruction_progress_v3','runtime_reconstruction_source_attachment_v2','bucket_controls_kms_output','runtime_reconstruction_progress_v4','runtime_reconstruction_source_attachment_v3','artifact_version_set_output','s3_exact_version_content_binding','runtime_reconstruction_progress_v5','runtime_reconstruction_source_attachment_v4','runtime_read_plan_v4']], '$defs':definitions}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    raw=(json.dumps(build(),indent=2,ensure_ascii=False)+'\n').encode();path=ROOT/OUTPUT
    if args.check:
        if path.read_bytes()!=raw:raise SystemExit('derived sequence schema differs')
    else:path.write_bytes(raw)
    print('sequence schema deterministic check PASS' if args.check else 'sequence schema generated locally')

if __name__=='__main__':main()
