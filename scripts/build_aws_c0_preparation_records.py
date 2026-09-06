"""Offline complete Gate 1 record construction with local-only schema resolution."""
from __future__ import annotations
import base64,copy,hashlib,importlib.util,json,re,unicodedata
from pathlib import Path
import jsonschema
from referencing import Registry

ROOT=Path(__file__).resolve().parents[1]
CRT='aws_c0_cost_runtime_retrieval_closure_correction_evidence_schema.json'
REGISTRY='aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json'
LINEAGE='aws_c0_gate1_bootstrap_lineage_correction_contract.json'
SCHEMA_URI='https://ebu.invalid/local/preparation-packet-v5.json'
SEQUENCE='aws_c0_deployment_sequence_correction_contract.json'
PHASES=('PREDEPLOYMENT','POSTDEPLOYMENT','EXECUTION_PREFLIGHT','COMPLETION')
# These are producer boundaries, not exemptions from the frozen 63 obligations.
# In particular DescribeExecution is ALWAYS, but its producer is StartExecution.
POSTDEPLOYMENT_ROWS=frozenset(('R36','R39','R40','R41','R46','R47','R48','R49','R50','R51','R52','R53'))
EXECUTION_ROWS=frozenset(('R37',))
COMPLETION_ROWS=frozenset(('R38','R44','R54','R55','R56','R57','R58'))

def sequence(root):return json.loads((root/SEQUENCE).read_bytes())

def currentize(root,value):
    mapping=sequence(root)['version_upgrades']
    def visit(v):
        if isinstance(v,str):return mapping.get(v,v)
        if isinstance(v,list):return [visit(x) for x in v]
        if isinstance(v,dict):return {k:visit(x) for k,x in v.items()}
        return v
    return visit(copy.deepcopy(value))

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

def obligation_phase(row_id):
    if row_id in COMPLETION_ROWS:return 'COMPLETION'
    if row_id in EXECUTION_ROWS:return 'EXECUTION_PREFLIGHT'
    if row_id in POSTDEPLOYMENT_ROWS:return 'POSTDEPLOYMENT'
    return 'PREDEPLOYMENT'

def build_phase_obligation_plan(root):
    """Preserve every accepted action/resource/condition; add producer order.

    This is only an input plan, never an authenticated read observation. No
    version, request ID, caller identity or future receipt is invented here.
    """
    source=(root/'aws_c0_material_identity_runtime_validation_correction_contract.json').read_bytes()
    contract=json.loads(source)
    rows=copy.deepcopy(contract['sealed_read_plan']['rows'])
    if [r['id'] for r in rows]!=['R%02d'%i for i in range(1,64)]:
        raise ValueError('exact accepted 63-row obligation order required')
    return {'schema':'aws_c0_runtime_control_phase_obligation_plan/v1',
            'source_contract_sha256':sha(source),'accepted_obligations_sha256':sha(canonical(rows)),
            'rows':rows,'phases_in_order':list(PHASES),
            'earliest_producer_phase_in_order':[obligation_phase(r['id']) for r in rows],
            'planned_inputs_are_observed_receipts':False}

def validate_phase_api_receipt(root,receipt,row,*,earliest,latest,caller_identity,authentication_source_identity):
    """Validate accepted API evidence bytes, not just its PASS labels.

    The collector supplies authenticated observations. This pure function never
    performs a request or upgrades unsigned/planned values to authenticated ones.
    """
    bundle=json.loads((root/'aws_c0_deployment_sequence_evidence_schema.json').read_bytes())
    aliases=[k for k in bundle['$defs'] if k.endswith('_api_request_response_receipt')]
    if not aliases:raise ValueError('accepted receipt schema absent')
    definition={'$ref':'#/$defs/'+aliases[0],'$defs':bundle['$defs']}
    jsonschema.Draft202012Validator(definition,registry=Registry()).validate(receipt)
    for key,wanted in [('row_id',row['id']),('action',row['action']),('resource_selector',row['resource_selector']),
                       ('caller_identity',caller_identity),('authentication_source_identity',authentication_source_identity)]:
        if receipt[key]!=wanted:raise ValueError('API observation binding mismatch: '+key)
    f=finalizer(root)
    if not f._utc(earliest)<=f._utc(receipt['requested_utc'])<=f._utc(receipt['completed_utc'])<=f._utc(latest):
        raise ValueError('API observation outside producer interval')
    for name,field in [('max_pages','pagination_page'),('max_items','pagination_item_count')]:
        bound=row['pagination_bounds'][name]
        if type(bound) is int and receipt[field]>bound:
            raise ValueError('API observation exceeds fixed pagination bound')
    for stem in ('request','response'):
        raw=base64.b64decode(receipt[stem+'_canonical_json_base64'],validate=True)
        value=f.strict_json(raw)
        if not isinstance(value,dict) or sha(raw)!=receipt[stem+'_sha256']:
            raise ValueError('API '+stem+' bytes/hash mismatch')
    return copy.deepcopy(receipt)

def build_phase_observation_set(root,plan,phase,observations,conditions,*,earliest,latest,
                                caller_identity,authentication_source_identity):
    """Account for all obligations without mislabelling future rows as PASS.

    This low-level producer deliberately does NOT certify reconstruction,
    resource resolution, pagination closure, or launch readiness. Those require
    the complete phase attachment verifier. It retains all supplied receipts.
    """
    if plan!=build_phase_obligation_plan(root) or phase not in PHASES:
        raise ValueError('exact phased obligation plan required')
    ids={r['id'] for r in plan['rows']}
    if set(conditions)!=ids or set(observations)-ids or any(type(v) is not bool for v in conditions.values()):
        raise ValueError('closed boolean condition inventory required')
    rank=PHASES.index(phase);entries=[]
    for row,producer in zip(plan['rows'],plan['earliest_producer_phase_in_order']):
        row_id=row['id'];condition=conditions[row_id];receipt=observations.get(row_id)
        if row['call_requirement']=='ALWAYS' and not condition:
            raise ValueError('ALWAYS obligation cannot be disabled: '+row_id)
        if rank<PHASES.index(producer):
            if receipt is not None:raise ValueError('receipt precedes required producer: '+row_id)
            state='NOT_YET_PRODUCED'
        elif not condition:
            if receipt is not None:raise ValueError('condition-false row has fabricated receipt: '+row_id)
            state='NOT_CALLED'
        else:
            if receipt is None:raise ValueError('due required observation missing: '+row_id)
            receipt=validate_phase_api_receipt(root,receipt,row,earliest=earliest,latest=latest,
                caller_identity=caller_identity,authentication_source_identity=authentication_source_identity)
            state='CALLED'
        entries.append({'row_id':row_id,'earliest_producer_phase':producer,'state':state,
                        'condition_evaluated':None if state=='NOT_YET_PRODUCED' else condition,'called_receipt':receipt})
    return {'schema':'aws_c0_runtime_control_phase_observation_set/v1',
            'obligation_plan_identity':identity(plan['schema'],plan),'phase':phase,'observed_utc':latest,
            'rows_in_order':entries,'complete_reconstruction_claimed':False}

def record_schema(root,name):
    bundle=json.loads((root/'aws_c0_deployment_sequence_evidence_schema.json').read_bytes())
    target=bundle['$defs'][name]['$ref'].rsplit('/',1)[-1]
    result=copy.deepcopy(bundle['$defs'][target])
    result.update({'$schema':bundle['$schema'],'$id':SCHEMA_URI+'/'+name,'$defs':bundle['$defs']})
    return result

def schema(root):return record_schema(root,'preparation_packet'),Registry()

def validate_record(root,name,value):
    jsonschema.Draft202012Validator(record_schema(root,name),registry=Registry()).validate(value)
    canonical(value)
    return value

def validate_packet(root,value):
    definition,registry=schema(root)
    jsonschema.Draft202012Validator(definition,registry=registry).validate(value)
    canonical(value)
    kinds=currentize(root,json.loads((root/'aws_c0_cost_runtime_retrieval_closure_correction_contract.json').read_bytes())['identity_kind_by_field'])
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

def finalizer(root):
    spec=importlib.util.spec_from_file_location('aws_c0_sequence_verifier',root/'aws/c0/finalizer/finalizer.py')
    loaded=importlib.util.module_from_spec(spec);spec.loader.exec_module(loaded)
    return loaded

def build_deployment_inputs(root,definition_bytes,document_bytes,template_bytes):
    """Pure source-byte plan. It has no AWS receipts, versions or observed claims."""
    f=finalizer(root)
    definition=f._source_json(definition_bytes);document=f._source_json(document_bytes)
    template=f._source_json(template_bytes);resources=template['Resources']
    if resources['EBUC0StartDocument']['Properties']['Content']!=document:
        raise ValueError('template SSM content differs from source artifact')
    if resources['StateMachine']['Properties']['StateMachineName']!='ebu-c0-closure-synthetic-v1':
        raise ValueError('unexpected workflow name')
    arn='arn:aws:'
    value={'schema':'aws_c0_deployment_inputs/v1','account_id':'623609441658','region':'us-east-1',
        'instance_id':'i-048bac00bdb540a4e','stack_name':'EBU-C0-492a4f1','change_set_name':'EBU-C0-492a4f1',
        'artifact_bucket_name':'ebu-stage-f-results-k7m4p2','observed_deployed_resources':False,
        'state_machine_arn':arn+'states:us-east-1:623609441658:stateMachine:'+resources['StateMachine']['Properties']['StateMachineName'],
        'workflow_role_arn':arn+'iam::623609441658:role/'+resources['StepFunctionsRole']['Properties']['RoleName'],
        'finalizer_function_arn':arn+'lambda:us-east-1:623609441658:function:'+resources['FinalizerFunction']['Properties']['FunctionName'],
        'ssm_document_name':template['Parameters']['SsmDocumentName']['Default'],
        'logging_configuration':{'level':resources['StateMachine']['Properties']['LoggingConfiguration']['Level'],
            'includeExecutionData':resources['StateMachine']['Properties']['LoggingConfiguration']['IncludeExecutionData'],'destinations':[
            {'cloudWatchLogsLogGroup':{'logGroupArn':arn+'logs:us-east-1:623609441658:log-group:'+resources['WorkflowLogGroup']['Properties']['LogGroupName']+':*'}}]},
        'tracing_configuration':resources['StateMachine']['Properties']['TracingConfiguration'],
        'definition_source':{'sha256':sha(definition_bytes),'bytes_base64':base64.b64encode(definition_bytes).decode()},
        'document_source':{'sha256':sha(document_bytes),'bytes_base64':base64.b64encode(document_bytes).decode()},
        'template_sha256':sha(template_bytes)}
    value['tracing_configuration']={'enabled':value['tracing_configuration']['Enabled']}
    return f._deployment_inputs(value)

def validate_predeployment_closure(root,closure):
    """The closure proves preparation, not objects which execution will create."""
    f=finalizer(root)
    validate_record(root,'preparation_closure',closure)
    if closure.get('schema')!='aws_c0_preparation_closure/v5':raise ValueError('current preparation closure required')
    f._deployment_control_values(closure['final_runtime_control_preimages'],f.PREDEPLOYMENT_CONTROLS,
                                '1970-01-01T00:00:00Z',closure['observed_utc'])
    return closure

def validate_postdeployment_authorization(root,packet,authorization,seed,launch):
    """Mandatory offline validation before the later auth publication and start."""
    f=finalizer(root)
    for name,value in [('live_packet',packet),('live_authorization',authorization),('closure_seed',seed),('launch',launch)]:
        validate_record(root,name,value)
    f._validate_live_packet_v6(packet);f._validate_live_authorization_v6(authorization)
    f._validate_launch_v6(launch)
    f.validate_deployment_sequence(packet,authorization,seed,launch)
    return copy.deepcopy(authorization)
