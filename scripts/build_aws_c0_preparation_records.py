"""Offline complete Gate 1 record construction with local-only schema resolution."""
from __future__ import annotations
import base64,copy,hashlib,importlib.util,json,os,re,stat,types,unicodedata
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

def build_phase_obligation_plan_v2(root):
    plan=build_phase_obligation_plan(root)
    plan.update(schema='aws_c0_runtime_control_phase_obligation_plan/v2',
                r51_result_kind='aws_c0_lambda_resource_policy_observation/v2',
                r51_existence_bookend_call_order=['R49','R51','R50'])
    return plan

def build_runtime_control_read_plan_fields(root,*,freshness_max_seconds=300):
    """Construct the accepted complete plan; no called/readback claims."""
    f=finalizer(root)
    contract=json.loads((root/'aws_c0_material_identity_runtime_validation_correction_contract.json').read_bytes())['sealed_read_plan']
    if sha(canonical(contract))!=f.READ_PLAN_CONTRACT_SHA256:
        raise ValueError('runtime read plan contract drift refused')
    plan={'schema':'aws_c0_runtime_control_read_plan/v1','rows':copy.deepcopy(contract['rows']),
        'row_ids':[r['id'] for r in contract['rows']],
        'required_control_mapping':copy.deepcopy(contract['required_control_mapping']),'shared_row_ids':[],
        'map_sha256':sha(canonical(contract['required_control_mapping'])),
        'plan_contract_identity':identity('aws_c0_runtime_control_read_plan_contract/v1',contract),
        'freshness_max_seconds':freshness_max_seconds}
    plan_id=identity(plan['schema'],plan)
    validate_named_definition(root,'runtime_control_read_plan',plan)
    f.validate_runtime_control_read_plan(plan,plan_id)
    return {'runtime_control_read_plan':plan,'runtime_control_read_plan_identity':plan_id}

def build_runtime_control_read_plan_fields_v2(root,*,freshness_max_seconds=300):
    f=finalizer(root);authority=sequence(root)
    packet=authority['pending_network_ingress_amendment_packet']
    if (sha(canonical(packet))!=f.INGRESS_AMENDMENT_SHA256 or
            authority.get('network_ingress_amendment_authorization',{}).get('packet_sha256')!=f.INGRESS_AMENDMENT_SHA256):
        raise ValueError('exact authorized R64 amendment required')
    old=build_runtime_control_read_plan_fields(root,freshness_max_seconds=freshness_max_seconds)
    plan=copy.deepcopy(old['runtime_control_read_plan']);plan['schema']='aws_c0_runtime_control_read_plan/v2'
    plan['original_read_plan_identity']=old['runtime_control_read_plan_identity']
    plan['amendment_packet_identity']=identity(packet['schema'],packet)
    plan['rows'].append(copy.deepcopy(f.R64_ROW));plan['row_ids'].append('R64')
    target=next(x for x in plan['required_control_mapping'] if x['control']=='VPC_NETWORK_PATH')
    target['row_ids'].append('R64')
    target['output_kind']=target['output_schema']='aws_c0_vpc_network_observation/v2'
    plan['map_sha256']=sha(canonical(plan['required_control_mapping']))
    plan_id=identity(plan['schema'],plan)
    f.validate_runtime_control_read_plan_v2(plan,plan_id)
    validate_record(root,'runtime_read_plan_v2',plan)
    return {'runtime_control_read_plan':plan,'runtime_control_read_plan_identity':plan_id}

def build_runtime_control_read_plan_fields_v3(root,*,freshness_max_seconds=300):
    """Bind the authorized IAM output/v2 correction without changing any read."""
    f=finalizer(root);authority=sequence(root)
    amendment=authority.get('iam_source_mapping_amendment_authorization')
    expected={'authority_id':f.IAM_SOURCE_MAPPING_AUTHORITY_ID,
        'source':'EXPLICIT_USER_AUTHORIZATION_2026_09_07',
        'historical_output_preserved':'aws_c0_iam_policy_set_observation/v1',
        'prospective_output':'aws_c0_iam_policy_set_observation/v2',
        'corrected_source_row_ids':['R15','R16','R17','R18','R19'],
        'read_plan_predecessor':'aws_c0_runtime_control_read_plan/v2',
        'prospective_read_plan':'aws_c0_runtime_control_read_plan/v3',
        'rows_actions_resources_conditions_changed':False,
        'other_control_mappings_changed':False,
        'aws_authority_permissions_science_cost_or_publication_changed':False}
    if amendment!=expected:
        raise ValueError('exact authorized IAM source-mapping amendment required')
    old=build_runtime_control_read_plan_fields_v2(root,freshness_max_seconds=freshness_max_seconds)
    plan=copy.deepcopy(old['runtime_control_read_plan']);plan['schema']='aws_c0_runtime_control_read_plan/v3'
    plan['previous_read_plan_identity']=old['runtime_control_read_plan_identity']
    plan['iam_source_mapping_authority_id']=f.IAM_SOURCE_MAPPING_AUTHORITY_ID
    target=next(x for x in plan['required_control_mapping'] if x['control']=='IAM_POLICY_SET')
    target['output_kind']=target['output_schema']='aws_c0_iam_policy_set_observation/v2'
    plan['map_sha256']=sha(canonical(plan['required_control_mapping']))
    plan_id=identity(plan['schema'],plan)
    f.validate_runtime_control_read_plan_v3(plan,plan_id)
    validate_record(root,'runtime_read_plan_v3',plan)
    return {'runtime_control_read_plan':plan,'runtime_control_read_plan_identity':plan_id}

def build_r64_exact_request(root,source_receipts,**context):
    # Gate the new action by the exact authorized packet before deriving IDs.
    build_runtime_control_read_plan_fields_v2(root,freshness_max_seconds=context['freshness_max_seconds'])
    return finalizer(root).derive_r64_exact_request(source_receipts,**context)['request']

def build_r64_ingress_observation(root,source_receipts,rule_receipt,*,attempt_identity,**context):
    f=finalizer(root)
    build_r64_exact_request(root,source_receipts,**context)
    targets=f.derive_r64_exact_request(source_receipts,**context)
    validate_record(root,'r64_receipt',rule_receipt)
    response=f.strict_json(base64.b64decode(rule_receipt['response_canonical_json_base64'],validate=True))
    groups=response.get('SecurityGroups')
    if not isinstance(groups,list) or any(not isinstance(g,dict) or not isinstance(g.get('IpPermissions'),list) for g in groups):
        raise ValueError('R64 actual explicit ingress arrays required before deriving count')
    observed_count=sum(len(g['IpPermissions']) for g in groups)
    record={'schema':'aws_c0_network_ingress_observation/v1',
        'amendment_packet_identity':f.identity('aws_c0_network_ingress_source_authority_amendment_packet/v1',f.INGRESS_AMENDMENT_SHA256),
        'attempt_identity':copy.deepcopy(attempt_identity),'instance_id':f.INSTANCE_ID,
        'observed_utc':context['observed_utc'],'freshness_max_seconds':context['freshness_max_seconds'],
        'vpc_id':targets['vpc_id'],'security_group_ids':targets['security_group_ids'],
        'ingress_rule_count':observed_count,'source_receipts_in_order':copy.deepcopy(source_receipts),
        'rule_receipt':copy.deepcopy(rule_receipt),'zero_science_counters':dict(f.ZERO)}
    f.validate_r64_ingress_observation(record,attempt_identity=attempt_identity,**context)
    validate_record(root,'network_ingress_observation',record)
    return {'network_ingress_observation':record,'network_ingress_observation_identity':identity(record['schema'],record)}

def build_r64_initial_call_budget(root,attempt_identity):
    """Offline empty budget; creation is not authority to reset a live attempt."""
    build_runtime_control_read_plan_fields_v2(root)
    f=finalizer(root)
    budget={'schema':f.R64_BUDGET_KIND,'attempt_identity':copy.deepcopy(attempt_identity),
        'amendment_packet_identity':f.identity('aws_c0_network_ingress_source_authority_amendment_packet/v1',f.INGRESS_AMENDMENT_SHA256),
        'reservations_in_order':[]}
    return r64_call_budget_fields(root,budget,attempt_identity)

def r64_call_budget_fields(root,budget,attempt_identity):
    f=finalizer(root);budget_id=identity(f.R64_BUDGET_KIND,budget)
    f.validate_r64_call_budget(budget,budget_id,attempt_identity=attempt_identity)
    validate_record(root,'network_ingress_call_budget',budget)
    return {'network_ingress_call_budget':copy.deepcopy(budget),'network_ingress_call_budget_identity':budget_id}

def build_r64_phase_binding(root,observation,call_budget,*,phase,attempt_identity,read_plan,
        read_plan_identity,previous_budget,previous_budget_identity,**context):
    f=finalizer(root)
    record={'schema':'aws_c0_network_ingress_phase_binding/v1','phase':phase,
        'attempt_identity':copy.deepcopy(attempt_identity),'read_plan_identity':copy.deepcopy(read_plan_identity),
        'previous_call_budget_identity':copy.deepcopy(previous_budget_identity),
        'call_budget':copy.deepcopy(call_budget),'call_budget_identity':identity(f.R64_BUDGET_KIND,call_budget),
        'ingress_observation':copy.deepcopy(observation),
        'ingress_observation_identity':identity('aws_c0_network_ingress_observation/v1',observation)}
    f.validate_r64_phase_binding(record,phase=phase,attempt_identity=attempt_identity,read_plan=read_plan,
        read_plan_identity=read_plan_identity,previous_budget=previous_budget,previous_budget_identity=previous_budget_identity,**context)
    validate_record(root,'network_ingress_phase_binding',record)
    return {'network_ingress_phase_binding':record,'network_ingress_phase_binding_identity':identity(record['schema'],record)}

def build_vpc_network_output_v2(root,receipts,ingress_binding,**phase_context):
    output=finalizer(root).build_vpc_network_reconstruction_output_v2(receipts,ingress_binding,**phase_context)
    validate_record(root,'vpc_network_output_v2',output)
    return output

def build_account_region_output(root,receipt,**context):
    output=finalizer(root).build_account_region_reconstruction_output(receipt,**context)
    validate_record(root,'account_region_output',output)
    return output

def build_instance_profile_output(root,receipts,**context):
    output=finalizer(root).build_instance_profile_reconstruction_output(receipts,**context)
    validate_record(root,'instance_profile_output',output)
    return output

def build_iam_role_context_binding(root,read_plan,read_plan_identity,instance_profile_bundle):
    authority=sequence(root).get('iam_cross_control_binding_authorization')
    expected={'authority_id':finalizer(root).IAM_CROSS_CONTROL_BINDING_AUTHORITY_ID,
        'source':'EXPLICIT_USER_AUTHORIZATION_2026_09_07_ALL_NECESSARY_REPAIRS',
        'source_control':'INSTANCE_PROFILE_SOLE_ROLE','source_row_id':'R14','target_control':'IAM_POLICY_SET',
        'allowed_fields':['role_arn','instance_profile_arn','assume_role_policy_sha256'],
        'iam_direct_source_row_ids_unchanged':['R15','R16','R17','R18','R19'],
        'prospective_progress':'aws_c0_runtime_control_reconstruction_progress/v3',
        'prospective_source_attachment':'aws_c0_runtime_control_reconstruction_source_attachment/v2',
        'source_attachment_predecessor':'aws_c0_runtime_control_reconstruction_source_attachment/v1',
        'prospective_sealed_context':'aws_c0_predeployment_reconstruction_context/v2',
        'new_aws_actions_or_calls_authorized':False,
        'permissions_science_cost_or_publication_changed':False,'historical_schemas_changed':False}
    if authority!=expected:raise ValueError('exact authorized IAM cross-control binding required')
    binding=finalizer(root).build_iam_role_context_binding(read_plan=read_plan,
        read_plan_identity=read_plan_identity,instance_profile_bundle=instance_profile_bundle)
    validate_record(root,'iam_role_context_binding',binding)
    return binding

def build_iam_policy_set_output_v2(root,receipts,role_context_binding,instance_profile_bundle,**context):
    output=finalizer(root).build_iam_policy_set_reconstruction_output_v2(receipts,
        role_context_binding,instance_profile_bundle,**context)
    validate_record(root,'iam_policy_set_output_v2',output)
    return output

def build_service_quota_output(root,receipts,**context):
    output=finalizer(root).build_service_quota_reconstruction_output(receipts,**context)
    validate_record(root,'service_quota_output',output)
    return output

def build_runtime_control_reconstruction_progress_v2(root,outputs,*,phase,validation_utc,
        freshness_max_seconds=300):
    """Bind only reconstructed controls; this cannot claim the v1 PASS gate."""
    if not isinstance(outputs,dict) or set(outputs)-set(finalizer(root).RECONSTRUCTION_PROGRESS_OUTPUT_KINDS):
        raise ValueError('only implemented reconstruction outputs may be supplied')
    plan_fields=build_runtime_control_read_plan_fields_v2(root,freshness_max_seconds=freshness_max_seconds)
    plan=plan_fields['runtime_control_read_plan'];f=finalizer(root);entries=[]
    for mapping in plan['required_control_mapping']:
        control=mapping['control'];output=outputs.get(control)
        if output is not None:
            state='CANONICAL_OUTPUT_CANDIDATE';output_id=copy.deepcopy(output['identity'])
        else:
            state='UNRESOLVED'
            output_id=None
        entries.append({'control':control,'mapped_row_ids':copy.deepcopy(mapping['row_ids']),
            'state':state,'output':copy.deepcopy(output),'output_identity':output_id})
    record={'schema':'aws_c0_runtime_control_reconstruction_progress/v2',
        'read_plan_identity':copy.deepcopy(plan_fields['runtime_control_read_plan_identity']),
        'phase':phase,'observed_utc':validation_utc,'controls_in_order':entries,
        'candidate_control_ids_in_order':[x['control'] for x in entries if x['state']=='CANONICAL_OUTPUT_CANDIDATE'],
        'unresolved_control_ids_in_order':[x['control'] for x in entries if x['state']!='CANONICAL_OUTPUT_CANDIDATE'],
        'source_revalidation_performed':False,'complete_reconstruction_claimed':False,'disposition':'PARTIAL_NOT_READY'}
    f.validate_runtime_control_reconstruction_progress_v2(record,read_plan=plan,
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase=phase,validation_utc=validation_utc)
    validate_record(root,'runtime_reconstruction_progress_v2',record)
    return record

def build_runtime_control_reconstruction_progress_v3(root,outputs,*,phase,validation_utc,
        freshness_max_seconds=300):
    """Bind the five implemented candidates to the corrected read-plan/v3."""
    f=finalizer(root)
    if not isinstance(outputs,dict) or set(outputs)-set(f.RECONSTRUCTION_PROGRESS_OUTPUT_KINDS_V3):
        raise ValueError('only implemented v3 reconstruction outputs may be supplied')
    plan_fields=build_runtime_control_read_plan_fields_v3(root,freshness_max_seconds=freshness_max_seconds)
    plan=plan_fields['runtime_control_read_plan'];entries=[]
    for mapping in plan['required_control_mapping']:
        control=mapping['control'];output=outputs.get(control)
        state='CANONICAL_OUTPUT_CANDIDATE' if output is not None else 'UNRESOLVED'
        entries.append({'control':control,'mapped_row_ids':copy.deepcopy(mapping['row_ids']),
            'state':state,'output':copy.deepcopy(output),
            'output_identity':None if output is None else copy.deepcopy(output['identity'])})
    record={'schema':'aws_c0_runtime_control_reconstruction_progress/v3',
        'read_plan_identity':copy.deepcopy(plan_fields['runtime_control_read_plan_identity']),
        'phase':phase,'observed_utc':validation_utc,'controls_in_order':entries,
        'candidate_control_ids_in_order':[item['control'] for item in entries if item['state']=='CANONICAL_OUTPUT_CANDIDATE'],
        'unresolved_control_ids_in_order':[item['control'] for item in entries if item['state']=='UNRESOLVED'],
        'source_revalidation_performed':False,'complete_reconstruction_claimed':False,'disposition':'PARTIAL_NOT_READY'}
    f.validate_runtime_control_reconstruction_progress_v3(record,read_plan=plan,
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase=phase,validation_utc=validation_utc)
    validate_record(root,'runtime_reconstruction_progress_v3',record)
    return record

def build_runtime_control_reconstruction_source_attachment_v1(root,*,account_bundle,
        instance_profile_bundle,vpc_bundle,service_quota_bundle,sealed_context,sealed_context_identity,
        validation_utc,freshness_max_seconds=300):
    """Construct the partial attachment only by rerunning its source validators."""
    plan_fields=build_runtime_control_read_plan_fields_v2(root,freshness_max_seconds=freshness_max_seconds)
    f=finalizer(root)
    record=f.build_runtime_control_reconstruction_source_attachment_v1(
        read_plan=plan_fields['runtime_control_read_plan'],
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase='PREDEPLOYMENT',
        validation_utc=validation_utc,sealed_context=sealed_context,sealed_context_identity=sealed_context_identity,account_bundle=account_bundle,
        instance_profile_bundle=instance_profile_bundle,vpc_bundle=vpc_bundle,service_quota_bundle=service_quota_bundle)
    f.validate_runtime_control_reconstruction_source_attachment_v1(record,
        read_plan=plan_fields['runtime_control_read_plan'],
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase='PREDEPLOYMENT',
        validation_utc=validation_utc,expected_sealed_context_identity=sealed_context_identity)
    validate_record(root,'runtime_reconstruction_source_attachment_v1',record)
    return record

def build_runtime_control_reconstruction_source_attachment_v2(root,*,account_bundle,
        instance_profile_bundle,iam_bundle,vpc_bundle,service_quota_bundle,sealed_context,
        sealed_context_identity,validation_utc,freshness_max_seconds=300):
    """Construct the five-control attachment by rerunning every source validator."""
    plan_fields=build_runtime_control_read_plan_fields_v3(root,freshness_max_seconds=freshness_max_seconds)
    f=finalizer(root)
    record=f.build_runtime_control_reconstruction_source_attachment_v2(
        read_plan=plan_fields['runtime_control_read_plan'],
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase='PREDEPLOYMENT',
        validation_utc=validation_utc,sealed_context=sealed_context,sealed_context_identity=sealed_context_identity,
        account_bundle=account_bundle,instance_profile_bundle=instance_profile_bundle,iam_bundle=iam_bundle,
        vpc_bundle=vpc_bundle,service_quota_bundle=service_quota_bundle)
    f.validate_runtime_control_reconstruction_source_attachment_v2(record,
        read_plan=plan_fields['runtime_control_read_plan'],
        read_plan_identity=plan_fields['runtime_control_read_plan_identity'],phase='PREDEPLOYMENT',
        validation_utc=validation_utc,expected_sealed_context_identity=sealed_context_identity)
    validate_record(root,'runtime_reconstruction_source_attachment_v2',record)
    return record

class R64LocalCallBudgetStore:
    """Append-only local reservation snapshots for one exact attempt.

    A deterministic /private/tmp path prevents a fresh process from choosing a
    new random ledger. Each state transition exclusively creates the next
    numbered file; racing writers cannot both reserve the same slot. An
    interrupted or malformed write is retained and blocks continuation. This
    is local crash/race protection, not protection against the user deleting
    files, a replacement host, or an unbound/untrusted attempt identity.

    No credentials, AWS client, transport or live-authority bypass exists here.
    The controller must supply the externally anchored attempt/previous budget
    and invoke transport only after reserve() returns the durable reservation.
    """
    def __init__(self,root,attempt_identity):
        self.root=root;self.f=finalizer(root)
        self.f._identity({'attempt':attempt_identity},'attempt','aws_c0_attempt/v1')
        self.attempt=copy.deepcopy(attempt_identity)
        self.name='ebu-c0-r64-budget-'+attempt_identity['sha256']
        self.path=Path('/private/tmp')/self.name

    @staticmethod
    def _private_stat(value,directory=False):
        kind=stat.S_ISDIR if directory else stat.S_ISREG
        if (not kind(value.st_mode) or value.st_uid!=os.geteuid()
                or stat.S_IMODE(value.st_mode)!=(0o700 if directory else 0o600)
                or (not directory and (value.st_nlink!=1 or not 0<value.st_size<=8192))):
            raise ValueError('R64 budget private owner/mode/type/link/size required')

    def _directory(self,create=False):
        parent=os.open('/private/tmp',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            if create:os.mkdir(self.name,0o700,dir_fd=parent)
            fd=os.open(self.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            try:
                self._private_stat(os.fstat(fd),directory=True)
                if create:os.fsync(parent)
                return fd
            except BaseException:
                os.close(fd);raise
        finally:os.close(parent)

    def _write(self,fd,index,budget):
        raw=canonical(budget)
        if len(raw)>8192:raise ValueError('R64 budget byte limit exceeded')
        name='%02d.json'%index
        target=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:
            # No truncation, replacement or deletion, including on failure.
            view=memoryview(raw)
            while view:
                count=os.write(target,view)
                if count<=0:raise OSError('R64 budget short write')
                view=view[count:]
            os.fsync(target)
            self._private_stat(os.fstat(target))
        finally:os.close(target)
        os.fsync(fd)

    def initialize(self):
        initial=build_r64_initial_call_budget(self.root,self.attempt)['network_ingress_call_budget']
        fd=self._directory(create=True)
        try:self._write(fd,0,initial)
        finally:os.close(fd)
        return r64_call_budget_fields(self.root,initial,self.attempt)

    def _read(self,fd):
        names=sorted(os.listdir(fd))
        if not names or len(names)>7 or names!=['%02d.json'%i for i in range(len(names))]:
            raise ValueError('R64 budget complete contiguous snapshot history required')
        previous=None
        for index,name in enumerate(names):
            source=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            try:
                before=os.fstat(source);self._private_stat(before)
                raw=b''
                while len(raw)<=8192:
                    part=os.read(source,8193-len(raw))
                    if not part:break
                    raw+=part
                after=os.fstat(source)
                if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(
                        after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                    raise ValueError('R64 budget file changed during read')
            finally:os.close(source)
            budget=self.f.strict_json(raw)
            self.f.validate_r64_call_budget(budget,identity(self.f.R64_BUDGET_KIND,budget),attempt_identity=self.attempt)
            if index==0:
                if budget['reservations_in_order']:
                    raise ValueError('R64 budget history must begin with the empty snapshot')
            else:self._transition(previous,budget)
            previous=budget
        return previous,len(names)

    def _transition(self,previous,candidate):
        old=previous['reservations_in_order'];new=candidate['reservations_in_order']
        self.f.validate_r64_call_budget(candidate,identity(self.f.R64_BUDGET_KIND,candidate),attempt_identity=self.attempt)
        if len(new)==len(old)+1:
            if (new[:-1]!=old or new[-1]['state']!='RESERVED'
                    or (old and old[-1]['state']!='OBSERVED_SUCCESS')):
                raise ValueError('R64 budget append must exclusively reserve the next slot')
        elif old and len(new)==len(old):
            outcome_fields={'state','finished_utc','observation_identity','request_id','failure_class'}
            if (new[:-1]!=old[:-1] or old[-1]['state']!='RESERVED'
                    or new[-1]['state'] not in ('OBSERVED_SUCCESS','OBSERVED_FAILURE')
                    or {k:v for k,v in old[-1].items() if k not in outcome_fields}!=
                       {k:v for k,v in new[-1].items() if k not in outcome_fields}):
                raise ValueError('R64 budget completion must preserve the outstanding reservation')
        else:raise ValueError('R64 budget history cannot shrink, skip or reset')

    def load(self,expected_identity):
        fd=self._directory()
        try:budget,_=self._read(fd)
        finally:os.close(fd)
        self.f.validate_r64_call_budget(budget,expected_identity,attempt_identity=self.attempt)
        return r64_call_budget_fields(self.root,budget,self.attempt)

    def _commit(self,expected_identity,candidate):
        fd=self._directory()
        try:
            budget,index=self._read(fd)
            self.f.validate_r64_call_budget(budget,expected_identity,attempt_identity=self.attempt)
            self._transition(budget,candidate)
            # The deterministic O_EXCL filename is the compare-and-set. A
            # concurrent winner or a torn write consumes it and causes refusal.
            self._write(fd,index,candidate)
        finally:os.close(fd)
        return r64_call_budget_fields(self.root,candidate,self.attempt)

    def reserve(self,expected_identity,source_receipts,**context):
        budget=self.load(expected_identity)['network_ingress_call_budget']
        candidate=self.f.reserve_r64_call(budget,expected_identity,source_receipts,attempt_identity=self.attempt,**context)
        return self._commit(expected_identity,candidate)

    def complete(self,expected_identity,observation,**context):
        budget=self.load(expected_identity)['network_ingress_call_budget']
        candidate=self.f.complete_r64_call(budget,expected_identity,observation,attempt_identity=self.attempt,**context)
        return self._commit(expected_identity,candidate)

    def fail(self,expected_identity,**context):
        budget=self.load(expected_identity)['network_ingress_call_budget']
        candidate=self.f.fail_r64_call(budget,expected_identity,attempt_identity=self.attempt,**context)
        return self._commit(expected_identity,candidate)

def build_r51_policy_observation(root,policy_receipt,function_receipts,*,expected_policy,
                                 caller_identity,authentication_source_identity,observed_utc,freshness_max_seconds):
    f=finalizer(root)
    # The new receipt kind must come from the prospective collector. Historical
    # receipts are not retagged, modified or promoted to a new result.
    if policy_receipt.get('schema')!=f.R51_RECEIPT_KIND:
        raise ValueError('new R51 receipt kind required; historical receipt unchanged')
    result={'schema':f.R51_RESULT_KIND,'target_function_arn':f.R51_TARGET,'observed_utc':observed_utc,
        'freshness_max_seconds':freshness_max_seconds,
        'outcome':'POLICY_PRESENT' if policy_receipt.get('http_status')==200 else 'POLICY_ABSENT',
        'policy':copy.deepcopy(expected_policy),'policy_receipt':copy.deepcopy(policy_receipt),
        'function_existence_receipts_in_order':copy.deepcopy(function_receipts)}
    validate_record(root,'r51_result',result)
    f.validate_r51_policy_observation(result,caller_identity=caller_identity,
        authentication_source_identity=authentication_source_identity,expected_policy=expected_policy,
        observed_utc=observed_utc,freshness_max_seconds=freshness_max_seconds)
    return result

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
                                caller_identity,authentication_source_identity,_r51_context=None):
    """Account for all obligations without mislabelling future rows as PASS.

    This low-level producer deliberately does NOT certify reconstruction,
    resource resolution, pagination closure, or launch readiness. Those require
    the complete phase attachment verifier. It retains all supplied receipts.
    """
    expected_plan=build_phase_obligation_plan(root) if _r51_context is None else build_phase_obligation_plan_v2(root)
    if plan!=expected_plan or phase not in PHASES:
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
            if row_id=='R51' and _r51_context is not None:
                validate_record(root,'r51_result',receipt)
                f=finalizer(root)
                f.validate_r51_policy_observation(receipt,caller_identity=caller_identity,
                    authentication_source_identity=authentication_source_identity,observed_utc=latest,**_r51_context)
                if receipt['function_existence_receipts_in_order']!=[observations.get('R49'),observations.get('R50')]:
                    raise ValueError('R51 existence witnesses differ from phase R49/R50 observations')
                if f._utc(receipt['policy_receipt']['requested_utc'])<f._utc(earliest):
                    raise ValueError('R51 receipt precedes phase interval')
                state='CALLED_POLICY_ABSENT' if receipt['outcome']=='POLICY_ABSENT' else 'CALLED_POLICY_PRESENT'
            else:
                receipt=validate_phase_api_receipt(root,receipt,row,earliest=earliest,latest=latest,
                    caller_identity=caller_identity,authentication_source_identity=authentication_source_identity)
                state='CALLED'
        entries.append({'row_id':row_id,'earliest_producer_phase':producer,'state':state,
                        'condition_evaluated':None if state=='NOT_YET_PRODUCED' else condition,'called_receipt':receipt})
    return {'schema':'aws_c0_runtime_control_phase_observation_set/v1' if _r51_context is None else 'aws_c0_runtime_control_phase_observation_set/v2',
            'obligation_plan_identity':identity(plan['schema'],plan),'phase':phase,'observed_utc':latest,
            'rows_in_order':entries,'complete_reconstruction_claimed':False}

def build_phase_observation_set_v2(root,plan,phase,observations,conditions,*,expected_lambda_policy,
                                   freshness_max_seconds,**context):
    return build_phase_observation_set(root,plan,phase,observations,conditions,
        _r51_context={'expected_policy':expected_lambda_policy,'freshness_max_seconds':freshness_max_seconds},**context)

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

def named_definition(root,suffix):
    bundle=json.loads((root/'aws_c0_deployment_sequence_evidence_schema.json').read_bytes())
    names=[k for k in bundle['$defs'] if k.endswith('_'+suffix)]
    if len(names)!=1:raise ValueError('unique accepted evidence definition required: '+suffix)
    return copy.deepcopy(bundle['$defs'][names[0]]),bundle['$defs']

def validate_named_definition(root,suffix,value):
    definition,definitions=named_definition(root,suffix)
    definition['$defs']=definitions
    jsonschema.Draft202012Validator(definition,registry=Registry()).validate(value)
    canonical(value)
    return value

def build_ssm_dispatch_transport_v2(root,semantic_parameters,attempt_identity,document_version):
    """Construct the unchanged accepted full START envelope and transport pair.

    Pure local data construction; it sends no command and observes no delivery.
    The semantic21 is an explicit input, not derived from downloaded objects.
    """
    record={'schema':'aws_c0_ssm_dispatch_request/v2','document_name':'EBU-C0-Start-v1',
        'document_version':document_version,'target_instance_id':'i-048bac00bdb540a4e',
        'attempt_identity':copy.deepcopy(attempt_identity),'semantic_parameters':copy.deepcopy(semantic_parameters)}
    definitions=json.loads((root/'aws_c0_audit_static_publication_handoff_correction_evidence_schema.json').read_bytes())['$defs']
    jsonschema.Draft202012Validator({'$ref':'#/$defs/ssm_dispatch_request_v2','$defs':definitions},registry=Registry()).validate(record)
    spec=importlib.util.spec_from_file_location('aws_c0_dispatch_verifier',root/'aws/c0/controller/ebu_c0_controller.py')
    controller=importlib.util.module_from_spec(spec);spec.loader.exec_module(controller)
    arguments={}
    for name,aws_name in zip(controller.SEMANTIC21,controller.SSM_SEMANTIC_NAMES):
        value=semantic_parameters[aws_name][0]
        arguments['bucket' if name=='artifact_bucket' else name]=int(value) if name.endswith('_bytes') else value
    raw=canonical(record)
    arguments.update(ssm_dispatch_request_canonical_json_base64=base64.b64encode(raw).decode(),ssm_dispatch_request_sha256=sha(raw))
    controller.validate_ssm_dispatch_v2(types.SimpleNamespace(**arguments))
    transport={'SsmDispatchRequestCanonicalJsonBase64':[arguments['ssm_dispatch_request_canonical_json_base64']],
               'SsmDispatchRequestSha256':[arguments['ssm_dispatch_request_sha256']]}
    parameters={**copy.deepcopy(semantic_parameters),**transport}
    jsonschema.Draft202012Validator({'$ref':'#/$defs/send_command_parameter_envelope','$defs':definitions},registry=Registry()).validate(parameters)
    return {'dispatch_request_preimage':record,'dispatch_request_identity':identity(record['schema'],record),
            'semantic_parameters':copy.deepcopy(semantic_parameters),'transport_parameters':transport,
            'send_command_parameters':parameters}

def build_local_helper_transport_v1(root,start_dispatch_request,operation,attempt_deadline_utc):
    """Plan helper-only transport within the original 21+2 parameter slots.

    No SSM delivery, local status or safe-close success is asserted by a plan.
    The runtime must independently compare the embedded START with its bound
    local source and check the actual clock/deadline before using this request.
    """
    validate_start=build_ssm_dispatch_transport_v2(root,start_dispatch_request['semantic_parameters'],
        start_dispatch_request['attempt_identity'],start_dispatch_request['document_version'])
    if validate_start['dispatch_request_preimage']!=start_dispatch_request:
        raise ValueError('exact accepted START request required for helper plan')
    record={'schema':'aws_c0_controller_local_helper_request/v1','operation':operation,
        'start_dispatch_request':copy.deepcopy(start_dispatch_request),'attempt_deadline_utc':attempt_deadline_utc}
    validate_record(root,'ssm_local_helper_request',record)
    f=finalizer(root);earliest=f._utc(start_dispatch_request['semantic_parameters']['SsmExpectedCommandNotBeforeUtc'][0])
    if not 0<(f._utc(attempt_deadline_utc)-earliest).total_seconds()<=43200:
        raise ValueError('helper plan must remain inside bounded attempt interval')
    raw=canonical(record)
    if len(raw)>16384:raise ValueError('helper plan exceeds transport bound')
    transport={'SsmDispatchRequestCanonicalJsonBase64':[base64.b64encode(raw).decode()],
               'SsmDispatchRequestSha256':[sha(raw)]}
    return {'helper_request':record,'helper_request_identity':identity(record['schema'],record),
            'transport_parameters':transport,'send_command_parameters':{**copy.deepcopy(start_dispatch_request['semantic_parameters']),**transport}}

def build_sealed_role_launch_fields(root,snapshot_bytes,receipts,*,earliest,latest,
                                   caller_identity,authentication_source_identity):
    """Construct the accepted role context from real, existing-resource reads.

    No caller-supplied role/profile/RoleId scalar can replace an API observation.
    All four source receipts must also be carried by the phase reconstruction;
    the accepted nested context itself carries the exact R14 read observation.
    """
    f=finalizer(root);snapshot=f.strict_json(snapshot_bytes)
    if not isinstance(snapshot,dict) or snapshot.get('schema')!='aws_c0_private_infrastructure_snapshot/v1':
        raise ValueError('exact existing private snapshot root required')
    snapshot_id={'kind':snapshot['schema'],'value':f._root_digest(snapshot),'sha256':f._root_digest(snapshot)}
    snapshot_schema=json.loads((root/'aws_c0_unattended_synthetic_rehearsal_evidence_schema.json').read_bytes())
    jsonschema.Draft202012Validator({'$ref':'#/$defs/aws_c0_private_infrastructure_snapshot',
        '$defs':snapshot_schema['$defs']},registry=Registry()).validate(snapshot)
    if snapshot['instance_state']!='stopped' or not snapshot['quota_fact_verified']:
        raise ValueError('stopped instance and verified quota snapshot required')
    if not f._utc(earliest)<=f._utc(snapshot['observed_utc'])<=f._utc(latest):
        raise ValueError('snapshot outside the sealed producer interval')
    row_ids=('R02','R03','R13','R14')
    if set(receipts)!=set(row_ids):raise ValueError('exact four role/profile source receipts required')
    plan=build_phase_obligation_plan(root);rows={r['id']:r for r in plan['rows']}
    data={};requests={}
    for row_id in row_ids:
        receipt=validate_phase_api_receipt(root,receipts[row_id],rows[row_id],earliest=earliest,latest=latest,
            caller_identity=caller_identity,authentication_source_identity=authentication_source_identity)
        requests[row_id]=f.strict_json(base64.b64decode(receipt['request_canonical_json_base64'],validate=True))
        data[row_id]=f.strict_json(base64.b64decode(receipt['response_canonical_json_base64'],validate=True))
        response=data[row_id];metadata=response.get('ResponseMetadata')
        if not isinstance(metadata,dict) or metadata.get('RequestId')!=receipt['request_id'] or metadata.get('HTTPStatusCode')!=200 or \
                'Error' in response or any(response.get(k) for k in ('NextToken','Marker','IsTruncated')):
            raise ValueError('complete authenticated role/profile response required')
        if receipt['pagination_page']!=1:raise ValueError('unaccounted earlier role/profile page')
    role_name='EBU-Rehearsal-EC2-Role';role_arn='arn:aws:iam::623609441658:role/'+role_name
    profile_arn='arn:aws:iam::623609441658:instance-profile/'+role_name
    expected_requests={'R02':{'InstanceIds':[f.INSTANCE_ID]},
        'R03':{'Filters':[{'Name':'instance-id','Values':[f.INSTANCE_ID]}]},
        'R13':{'InstanceProfileName':role_name},'R14':{'RoleName':role_name}}
    if requests!=expected_requests:raise ValueError('role/profile request coordinate mismatch')
    reservations=data['R02'].get('Reservations')
    if not isinstance(reservations,list) or len(reservations)!=1 or len(reservations[0].get('Instances',[]))!=1:
        raise ValueError('exactly one observed instance required')
    instance=reservations[0]['Instances'][0]
    if instance.get('InstanceId')!=f.INSTANCE_ID or instance.get('IamInstanceProfile',{}).get('Arn')!=profile_arn:
        raise ValueError('observed instance/profile mismatch')
    if instance.get('State',{}).get('Name')!=snapshot['instance_state']:
        raise ValueError('snapshot and authenticated instance state disagree')
    if any(f._utc(r['completed_utc'])>f._utc(snapshot['observed_utc']) for r in receipts.values()):
        raise ValueError('snapshot predates its role/profile source observations')
    associations=data['R03'].get('IamInstanceProfileAssociations')
    if not isinstance(associations,list) or len(associations)!=1 or associations[0].get('InstanceId')!=f.INSTANCE_ID or \
            associations[0].get('State')!='associated' or associations[0].get('IamInstanceProfile',{}).get('Arn')!=profile_arn:
        raise ValueError('exact associated instance profile required')
    profile=data['R13'].get('InstanceProfile');role=data['R14'].get('Role')
    if not isinstance(profile,dict) or profile.get('Arn')!=profile_arn or profile.get('InstanceProfileName')!=role_name or \
            not isinstance(role,dict) or role.get('Arn')!=role_arn or role.get('RoleName')!=role_name or \
            not isinstance(profile.get('Roles'),list) or len(profile['Roles'])!=1:
        raise ValueError('exact sole observed role/profile required')
    if any(profile['Roles'][0].get(key)!=role.get(key) for key in ('RoleId','Arn','RoleName')):
        raise ValueError('profile role and GetRole disagree')
    observed={'schema':'aws_c0_instance_profile_role_observation_preimage/v1','instance_id':f.INSTANCE_ID,
        'instance_profile_arn':profile_arn,'instance_profile_name':role_name,'role_arn':role_arn,
        'attached_role_count':1,'source_row_ids':list(row_ids)}
    definition,_=named_definition(root,'sealed_ec2_role_context_preimage')
    context={k:copy.deepcopy(v['const']) for k,v in definition['properties'].items() if 'const' in v}
    context.update(account_id='623609441658',role_id=role['RoleId'],role_name_utf8=role_name,
        role_arn_utf8=role_arn,instance_profile_arn_utf8=profile_arn,
        private_infrastructure_snapshot_identity=snapshot_id,private_infrastructure_snapshot_sha256=snapshot_id['sha256'],
        instance_profile_role_observation_identity=identity('aws_c0_instance_profile_role_observation/v1',observed),
        instance_profile_role_observation_preimage=observed,
        instance_profile_role_observation_canonical_json_base64=base64.b64encode(canonical(observed)).decode(),
        instance_profile_role_observation_byte_count=len(canonical(observed)),instance_profile_role_observation_sha256=sha(canonical(observed)),
        r14_get_role_observation={'row':rows['R14'],'call_disposition':'CALLED','condition_evaluated':True,
                                 'called_receipt':copy.deepcopy(receipts['R14']),'not_called_reason':None})
    validate_named_definition(root,'sealed_ec2_role_context_preimage',context)
    launch_schema=record_schema(root,'launch')['allOf'][1]['properties']
    return {'sealed_ec2_role_context_identity':identity('aws_c0_sealed_ec2_role_context/v1',context),
        'sealed_ec2_role_context_preimage':context,
        'sealed_ec2_role_context_preimage_canonical_json_base64':base64.b64encode(canonical(context)).decode(),
        'sealed_ec2_role_context_preimage_byte_count':len(canonical(context)),
        'sealed_ec2_role_context_preimage_sha256':sha(canonical(context)),
        'sealed_ec2_role_context_cross_binding_disposition':launch_schema['sealed_ec2_role_context_cross_binding_disposition']['const']}

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
