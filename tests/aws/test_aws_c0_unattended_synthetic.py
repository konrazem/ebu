"""Offline tests for the closure-closed AWS-C0 implementation."""
from __future__ import annotations

import ast
import base64
import copy
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec); sys.modules[name] = loaded; spec.loader.exec_module(loaded)
    return loaded


V = module("scripts/validate_aws_c0_static.py", "aws_c0_validator")
C = module("aws/c0/controller/ebu_c0_controller.py", "aws_c0_controller")
F = module("aws/c0/finalizer/finalizer.py", "aws_c0_finalizer")
W = module("aws/c0/container/synthetic_worker.py", "aws_c0_worker")
D = module("scripts/build_aws_c0_deployment_manifest.py", "aws_c0_deployment_manifest")
P = module("scripts/collect_aws_c0_pricing.py", "aws_c0_pricing")
B = module("aws/c0/bootstrap/bootstrap_transport.py", "aws_c0_bootstrap_transport")
S = module("aws/c0/bootstrap/staging_transport.py", "aws_c0_staging_transport")
G = module("scripts/build_aws_c0_preparation_records.py", "aws_c0_preparation_records")


class CompletePreparationBuilderTests(unittest.TestCase):
    def test_schema_upgrade_is_narrow_and_uses_exact_existing_lineage(self):
        schema, _ = G.schema(ROOT)
        p = schema['allOf'][1]['properties']
        self.assertEqual(p['schema']['const'], 'aws_c0_preparation_packet/v5')
        self.assertEqual(p['bootstrap_control_candidates']['minItems'], 6)
        self.assertEqual(p['bootstrap_control_candidates']['maxItems'], 6)
        self.assertEqual(p['planned_pre_live_object_count']['const'], 24)
        self.assertEqual(p['planned_pre_live_record_kinds']['const'], list(V.SEQUENCE_PRELIVE_RECORD_KINDS))
        original = json.loads((ROOT / G.REGISTRY).read_bytes())['$defs']['preparation_packet_v3']
        self.assertEqual(schema['allOf'][1]['required'], original['allOf'][1]['required']+['material_correction_authority_id'])

    def test_complete_builder_refuses_convenience_draft_or_missing_observations(self):
        for value in ({}, {'schema': 'aws_c0_gate1_preparation_packet_draft/v1'},
                      {'schema': 'aws_c0_preparation_packet/v5', 'instance_id': 'i-048bac00bdb540a4e'}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'complete packet field set'):
                G.build(ROOT, value)

    def test_control_material_rejects_floating_point_and_noncanonical_unicode(self):
        for value in ({'amount': 1.5}, {'amount': float('inf')}, {'text': 'e\u0301'}):
            with self.subTest(value=value), self.assertRaises(ValueError): G.canonical(value)
        self.assertEqual(G.canonical({'b': 2, 'a': 1}), b'{"a":1,"b":2}')

class PhaseObligationProducerTests(unittest.TestCase):
    """Explicit offline API-shaped fixtures; never actual AWS observations."""
    def material(self,phase='PREDEPLOYMENT'):
        plan=G.build_phase_obligation_plan(ROOT)
        caller=F.identity('aws_sts_role_session/v1','a'*64)
        source=F.identity('aws_authenticated_api_source/v1','b'*64)
        interval=dict(earliest='2026-09-06T18:00:00Z',latest='2026-09-06T18:01:00Z',
                      caller_identity=caller,authentication_source_identity=source)
        observations={};conditions={}
        for row in plan['rows']:
            row_id=row['id'];conditions[row_id]=row['call_requirement']=='ALWAYS'
            if G.PHASES.index(phase)<G.PHASES.index(G.obligation_phase(row_id)) or not conditions[row_id]:continue
            raw=F.canonical_bytes({'offline_fixture':True,'row_id':row_id})
            observations[row_id]={'row_id':row_id,'action':row['action'],'resource_selector':row['resource_selector'],
                'caller_identity':caller,'authentication_source_identity':source,
                'request_canonical_json_base64':base64.b64encode(raw).decode(),'request_sha256':F.digest(raw),
                'response_canonical_json_base64':base64.b64encode(raw).decode(),'response_sha256':F.digest(raw),
                'http_status':200,'request_id':'offline-'+row_id,'requested_utc':interval['earliest'],
                'completed_utc':interval['latest'],'pagination_page':1,'pagination_item_count':1,
                'authentication_disposition':'SIGNED_CALLER_AND_EXACT_REQUEST_RESPONSE_BYTES_PASS',
                'api_success_disposition':'AWS_API_CALL_SUCCESS'}
        return plan,phase,observations,conditions,interval

    def build(self,values):
        return G.build_phase_observation_set(ROOT,*values[:4],**values[4])

    def test_plan_preserves_all_63_actions_resources_conditions_and_order(self):
        source=json.loads((ROOT/'aws_c0_material_identity_runtime_validation_correction_contract.json').read_bytes())
        plan=G.build_phase_obligation_plan(ROOT)
        self.assertEqual(plan['rows'],source['sealed_read_plan']['rows'])
        self.assertFalse(plan['planned_inputs_are_observed_receipts'])
        self.assertEqual(len(plan['rows']),63)

    def test_partial_phase_is_never_a_complete_reconstruction(self):
        for phase in G.PHASES:
            result=self.build(self.material(phase))
            self.assertEqual(len(result['rows_in_order']),63)
            self.assertFalse(result['complete_reconstruction_claimed'])
            r37=result['rows_in_order'][36]
            expected='NOT_YET_PRODUCED' if G.PHASES.index(phase)<2 else 'CALLED'
            self.assertEqual(r37['state'],expected)
            if expected=='NOT_YET_PRODUCED':
                self.assertIsNone(r37['called_receipt']);self.assertIsNone(r37['condition_evaluated'])

    def test_future_receipt_and_disabled_always_obligation_refused(self):
        values=self.material();later=self.material('EXECUTION_PREFLIGHT')
        values[2]['R37']=later[2]['R37']
        with self.assertRaisesRegex(ValueError,'precedes required producer'):self.build(values)
        values=self.material();values[3]['R37']=False
        with self.assertRaisesRegex(ValueError,'ALWAYS obligation'):self.build(values)

    def test_every_ssm_document_object_read_requires_document_creation(self):
        values=self.material();result=self.build(values)
        document_rows=[r for r in values[0]['rows'] if r['resource_selector']=='SEALED_SSM_DOCUMENT_ARN']
        self.assertEqual([r['id'] for r in document_rows],['R39','R40','R41'])
        entries={r['row_id']:r for r in result['rows_in_order']}
        for row in document_rows:
            self.assertEqual(G.obligation_phase(row['id']),'POSTDEPLOYMENT')
            self.assertEqual(entries[row['id']]['state'],'NOT_YET_PRODUCED')

    def test_missing_due_receipt_and_wrong_row_or_tampered_bytes_refused(self):
        for change in (lambda v:v[2].pop('R01'),lambda v:v[2]['R01'].update(action='sts:AssumeRole'),
                       lambda v:v[2]['R01'].update(response_sha256='0'*64),
                       lambda v:v[2]['R01'].update(completed_utc='2026-09-06T18:02:00Z'),
                       lambda v:v[2]['R01'].update(pagination_page=2)):
            values=self.material();change(values)
            with self.assertRaises(ValueError):self.build(values)

    def test_unknown_rows_condition_false_receipt_and_plan_drift_refused(self):
        values=self.material();values[2]['R64']=values[2]['R01']
        with self.assertRaises(ValueError):self.build(values)
        values=self.material();values[0]['rows'][0]['resource_selector']='other'
        with self.assertRaises(ValueError):self.build(values)
        values=self.material();conditional=next(r['id'] for r in values[0]['rows']
            if r['call_requirement']!='ALWAYS' and G.obligation_phase(r['id'])=='PREDEPLOYMENT')
        values[2][conditional]=values[2]['R01']
        with self.assertRaisesRegex(ValueError,'condition-false'):self.build(values)

    def test_r51_absence_is_not_success_under_unchanged_accepted_contract(self):
        values=self.material('POSTDEPLOYMENT')
        row=values[0]['rows'][50]
        self.assertEqual((row['id'],row['action'],row['call_requirement']),('R51','lambda:GetPolicy','ALWAYS'))
        values[2]['R51']['http_status']=404
        with self.assertRaises(G.jsonschema.ValidationError):self.build(values)
        template=json.loads((ROOT/'aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml').read_bytes())
        self.assertEqual(template['Resources']['FinalizerFunction']['Type'],'AWS::Lambda::Function')
        self.assertNotIn('AWS::Lambda::Permission',[r['Type'] for r in template['Resources'].values()])


class R51ProspectiveAmendmentTests(unittest.TestCase):
    """The same pure validator used by the producer; all API bytes are offline."""
    @staticmethod
    def encode(receipt,stem,value):
        raw=F.canonical_bytes(value)
        receipt[stem+'_canonical_json_base64']=base64.b64encode(raw).decode()
        receipt[stem+'_sha256']=F.digest(raw)

    @staticmethod
    def decode(receipt,stem='response'):
        return F.strict_json(base64.b64decode(receipt[stem+'_canonical_json_base64']))

    def material(self,present=False):
        values=PhaseObligationProducerTests().material('POSTDEPLOYMENT')
        observations=values[2];interval=values[4]
        config={'FunctionArn':F.R51_TARGET,'FunctionName':F.R51_TARGET.rsplit(':',1)[-1],
                'Version':'$LATEST','RevisionId':'offline-function-revision',
                'CodeSha256':base64.b64encode(b'x'*32).decode(),'LastModified':'2026-09-06T17:00:00.000+0000'}
        policy={'Version':'2012-10-17','Statement':[{'Effect':'Allow','Action':'lambda:InvokeFunction',
            'Resource':F.R51_TARGET,'Principal':{'AWS':'arn:aws:iam::623609441658:role/EBU-C0-Corrected-StepFunctions-v1'}}]}
        for row,start,end in [('R49',1,2),('R51',3,4),('R50',5,6)]:
            receipt=observations[row]
            receipt.update(requested_utc='2026-09-06T18:00:%02dZ'%start,completed_utc='2026-09-06T18:00:%02dZ'%end)
            self.encode(receipt,'request',{'FunctionName':F.R51_TARGET})
            metadata={'HTTPStatusCode':200,'RequestId':receipt['request_id']}
            if row=='R49':response={'Configuration':copy.deepcopy(config),'ResponseMetadata':metadata}
            elif row=='R50':response={**copy.deepcopy(config),'ResponseMetadata':metadata}
            else:
                receipt['schema']=F.R51_RECEIPT_KIND
                if present:
                    response={'Policy':json.dumps(policy,indent=2),'RevisionId':'offline-policy-revision','ResponseMetadata':metadata}
                else:
                    receipt.update(http_status=404,api_success_disposition='AWS_API_RESOURCE_NOT_FOUND')
                    metadata.update(HTTPStatusCode=404,HTTPHeaders={'x-amzn-errortype':'ResourceNotFoundException',
                                                               'x-amzn-requestid':receipt['request_id']})
                    response={'Error':{'Code':'ResourceNotFoundException','Message':'Offline policy absent fixture'},'ResponseMetadata':metadata}
            self.encode(receipt,'response',response)
        context=dict(caller_identity=interval['caller_identity'],authentication_source_identity=interval['authentication_source_identity'],
                     expected_policy=policy if present else None,observed_utc=interval['latest'],freshness_max_seconds=60)
        result=G.build_r51_policy_observation(ROOT,observations['R51'],[observations['R49'],observations['R50']],**context)
        return result,context,values

    def test_absence_and_present_pass_shared_validator_and_new_schema(self):
        for present in (False,True):
            result,context,_=self.material(present)
            self.assertEqual(F.validate_r51_policy_observation(result,**context),result)
            self.assertEqual(G.validate_record(ROOT,'r51_result',result),result)
            self.assertEqual(result['outcome'],'POLICY_PRESENT' if present else 'POLICY_ABSENT')
            if not present:
                self.assertIsNone(result['policy'])
                self.assertNotEqual(result['policy_receipt']['api_success_disposition'],'AWS_API_CALL_SUCCESS')

    def test_new_phase_binds_exact_witnesses_and_distinct_absence_result(self):
        result,context,values=self.material()
        observations=copy.deepcopy(values[2]);observations['R51']=result
        plan=G.build_phase_obligation_plan_v2(ROOT)
        self.assertEqual(plan['rows'],G.build_phase_obligation_plan(ROOT)['rows'])
        self.assertEqual(plan['r51_existence_bookend_call_order'],['R49','R51','R50'])
        actual=G.build_phase_observation_set_v2(ROOT,plan,values[1],observations,values[3],
            expected_lambda_policy=None,freshness_max_seconds=60,**values[4])
        self.assertEqual(actual['schema'],'aws_c0_runtime_control_phase_observation_set/v2')
        self.assertEqual(actual['rows_in_order'][50]['state'],'CALLED_POLICY_ABSENT')
        self.assertFalse(actual['complete_reconstruction_claimed'])
        observations['R49']=copy.deepcopy(observations['R49']);observations['R49']['request_id']='different-offline-id'
        with self.assertRaisesRegex(ValueError,'differ from phase'):
            G.build_phase_observation_set_v2(ROOT,plan,values[1],observations,values[3],
                expected_lambda_policy=None,freshness_max_seconds=60,**values[4])

    def test_http_errors_float_bool_and_old_success_label_refused(self):
        for value in (403,429,500,0,404.0,True):
            record,context,_=self.material();record['policy_receipt']['http_status']=value
            with self.subTest(value=value),self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)
        for key,value in [('schema','aws_c0_api_request_response_receipt/v1'),('api_success_disposition','AWS_API_CALL_SUCCESS'),
                          ('request_id',''),('action','lambda:AddPermission'),('resource_selector','*')]:
            record,context,_=self.material();record['policy_receipt'][key]=value
            with self.subTest(key=key),self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)

    def test_generic_404_access_denied_code_and_missing_response_evidence_refused(self):
        for mutate in (lambda r:r['Error'].update(Code='AccessDeniedException'),lambda r:r['Error'].pop('Code'),
                       lambda r:r.pop('Error'),lambda r:r['ResponseMetadata'].pop('HTTPHeaders'),
                       lambda r:r['ResponseMetadata']['HTTPHeaders'].update({'x-amzn-errortype':'Unknown'}),
                       lambda r:r['ResponseMetadata'].update(RequestId='other-request'),
                       lambda r:r.update(Policy='{}')):
            record,context,_=self.material();receipt=record['policy_receipt'];response=self.decode(receipt);mutate(response)
            self.encode(receipt,'response',response)
            with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)
        record,context,_=self.material();record['policy_receipt']['response_sha256']='0'*64
        with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)

    def test_missing_stale_future_failed_and_non_bookend_witness_refused(self):
        for mutate in (lambda r:r['function_existence_receipts_in_order'].pop(),
                       lambda r:r['function_existence_receipts_in_order'].reverse(),
                       lambda r:r['function_existence_receipts_in_order'][0].update(requested_utc='2026-09-06T17:59:00Z'),
                       lambda r:r['function_existence_receipts_in_order'][1].update(completed_utc='2026-09-06T18:02:00Z'),
                       lambda r:r['function_existence_receipts_in_order'][0].update(http_status=404),
                       lambda r:r['function_existence_receipts_in_order'][1].update(requested_utc='2026-09-06T18:00:00Z')):
            record,context,_=self.material();mutate(record)
            with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)

    def test_exact_function_account_region_qualifier_and_revision_required(self):
        for target in (F.R51_TARGET+':alias',F.R51_TARGET.replace('us-east-1','us-west-2'),
                       F.R51_TARGET.replace('623609441658','111111111111'),F.R51_TARGET+'other'):
            record,context,_=self.material();self.encode(record['policy_receipt'],'request',{'FunctionName':target})
            with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)
        for field in ('FunctionArn','RevisionId','CodeSha256','LastModified'):
            record,context,_=self.material();receipt=record['function_existence_receipts_in_order'][1]
            response=self.decode(receipt);response[field]='changed';self.encode(receipt,'response',response)
            with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)

    def test_caller_channel_missing_policy_and_no_historical_retagging(self):
        for field in ('caller_identity','authentication_source_identity'):
            record,context,_=self.material();context[field]=F.identity(context[field]['kind'],'c'*64)
            with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)
        record,context,values=self.material(True);context['expected_policy']=None
        with self.assertRaises(F.Refusal):F.validate_r51_policy_observation(record,**context)
        original=copy.deepcopy(values[2]['R51']);del original['schema']
        with self.assertRaisesRegex(ValueError,'historical receipt unchanged'):
            G.build_r51_policy_observation(ROOT,original,[values[2]['R49'],values[2]['R50']],**context)
        self.assertNotIn('schema',original)


class RuntimeControlReadPlanTests(unittest.TestCase):
    def test_constructor_schema_and_runtime_bind_actual_complete_frozen_plan(self):
        result=G.build_runtime_control_read_plan_fields(ROOT)
        plan=result['runtime_control_read_plan'];plan_id=result['runtime_control_read_plan_identity']
        contract=load('aws_c0_material_identity_runtime_validation_correction_contract.json')['sealed_read_plan']
        self.assertEqual(plan['rows'],contract['rows'])
        self.assertEqual(plan['required_control_mapping'],contract['required_control_mapping'])
        self.assertEqual(plan['plan_contract_identity'],G.identity('aws_c0_runtime_control_read_plan_contract/v1',contract))
        self.assertEqual(F.validate_runtime_control_read_plan(plan,plan_id),plan)
        self.assertEqual(G.validate_named_definition(ROOT,'runtime_control_read_plan',plan),plan)
        self.assertEqual(plan['rows'][36]['call_requirement'],'ALWAYS')
        self.assertEqual(G.obligation_phase('R37'),'EXECUTION_PREFLIGHT')
        self.assertNotIn('called_receipts',plan)

    def test_changed_actions_resources_map_or_identity_fail_even_when_rehashed(self):
        for mutate in (lambda p:p['rows'][50].update(action='lambda:AddPermission'),
                       lambda p:p['rows'][50].update(resource_selector='*'),
                       lambda p:p['rows'][36].update(call_requirement='CONDITIONAL'),
                       lambda p:p['rows'].reverse(),lambda p:p['required_control_mapping'][0]['row_ids'].append('R02'),
                       lambda p:p.update(shared_row_ids=['R02']),lambda p:p.update(row_ids=['R01']),
                       lambda p:p.update(map_sha256='a'*64),lambda p:p['plan_contract_identity'].update(value='b'*64),
                       lambda p:p.update(extra=True)):
            plan=G.build_runtime_control_read_plan_fields(ROOT)['runtime_control_read_plan'];mutate(plan)
            with self.assertRaises(F.Refusal):F.validate_runtime_control_read_plan(plan,G.identity(plan['schema'],plan))
        result=G.build_runtime_control_read_plan_fields(ROOT)
        with self.assertRaises(F.Refusal):F.validate_runtime_control_read_plan(result['runtime_control_read_plan'],F.identity('aws_c0_runtime_control_read_plan/v1','c'*64))

    def test_freshness_is_exact_bounded_and_runtime_gate_attaches_before_controls(self):
        for bound in (True,0,301,1.0):
            with self.assertRaises((RuntimeError,ValueError,G.jsonschema.ValidationError)):
                G.build_runtime_control_read_plan_fields(ROOT,freshness_max_seconds=bound)
        source=(ROOT/'aws/c0/finalizer/finalizer.py').read_text()
        fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='_validate_live_packet_v6')
        body=ast.get_source_segment(source,fn)
        self.assertLess(body.index('validate_runtime_control_read_plan_v2('),body.index('_deployment_control_values('))


class R64IngressAmendmentTests(unittest.TestCase):
    """API-shaped offline evidence only; no transport, AWS, service or science."""
    def material(self):
        caller=F.identity('aws_sts_role_session/v1','a'*64)
        channel=F.identity('aws_authenticated_api_source/v1','b'*64)
        attempt=F.identity('aws_c0_attempt/v1','c'*64)
        context={'caller_identity':caller,'authentication_source_identity':channel,
                 'observed_utc':'2026-09-06T18:00:07Z','freshness_max_seconds':300}
        vpc='vpc-01234567';group_ids=['sg-01234567','sg-89abcdef']
        interfaces=[]
        for n,gid in enumerate(group_ids):
            interfaces.append({'NetworkInterfaceId':['eni-01234567','eni-89abcdef'][n],'VpcId':vpc,
                'Groups':[{'GroupId':gid,'GroupName':'offline-fixture'}],
                'Attachment':{'DeviceIndex':n,'Status':'attached'}})
        instance={'InstanceId':F.INSTANCE_ID,'InstanceType':'t3.small','State':{'Name':'stopped'},'VpcId':vpc,
            'NetworkInterfaces':copy.deepcopy(interfaces),'SecurityGroups':copy.deepcopy(interfaces[0]['Groups'])}
        described=copy.deepcopy(interfaces)
        for eni in described:eni.update(OwnerId='623609441658');eni['Attachment']['InstanceId']=F.INSTANCE_ID
        requests=[{'InstanceIds':[F.INSTANCE_ID]},
                  {'Filters':[{'Name':'attachment.instance-id','Values':[F.INSTANCE_ID]}]},
                  {'GroupIds':group_ids}]
        responses=[{'Reservations':[{'OwnerId':'623609441658','Instances':[instance]}]},
                   {'NetworkInterfaces':described},
                   {'SecurityGroups':[{'GroupId':gid,'OwnerId':'623609441658','VpcId':vpc,'IpPermissions':[]} for gid in group_ids]}]
        receipts=[]
        for index,(row,action,count) in enumerate([('R02','DescribeInstances',1),('R04','DescribeNetworkInterfaces',2),('R64','DescribeSecurityGroups',2)]):
            request_id='offline-request-'+row
            responses[index]['ResponseMetadata']={'RequestId':request_id,'HTTPStatusCode':200,'RetryAttempts':0,
                'HTTPHeaders':{'x-amzn-requestid':request_id}}
            receipt={'row_id':row,'action':'ec2:'+action,'resource_selector':'*','caller_identity':caller,
                'authentication_source_identity':channel,'http_status':200,'request_id':request_id,
                'requested_utc':'2026-09-06T18:00:%02dZ'%(index*2+1),
                'completed_utc':'2026-09-06T18:00:%02dZ'%(index*2+2),
                'pagination_page':1,'pagination_item_count':count,
                'authentication_disposition':'SIGNED_CALLER_AND_EXACT_REQUEST_RESPONSE_BYTES_PASS',
                'api_success_disposition':'AWS_API_CALL_SUCCESS'}
            for stem,value in [('request',requests[index]),('response',responses[index])]:
                R51ProspectiveAmendmentTests.encode(receipt,stem,value)
            if row=='R64':receipt['schema']='aws_c0_r64_api_request_response_receipt/v1'
            receipts.append(receipt)
        return receipts[:2],receipts[2],attempt,context

    def result(self):
        sources,receipt,attempt,context=self.material()
        result=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=attempt,**context)
        return result['network_ingress_observation'],attempt,context

    def mutate_api(self,receipt,stem,mutate):
        value=F.strict_json(base64.b64decode(receipt[stem+'_canonical_json_base64']))
        mutate(value);R51ProspectiveAmendmentTests.encode(receipt,stem,value)

    def test_distinct_64_plan_preserves_all_original_rows_and_history(self):
        original=G.build_runtime_control_read_plan_fields(ROOT)
        current=G.build_runtime_control_read_plan_fields_v2(ROOT)
        old=original['runtime_control_read_plan'];new=current['runtime_control_read_plan']
        self.assertEqual(new['rows'][:-1],old['rows'])
        self.assertEqual(new['rows'][-1],F.R64_ROW)
        self.assertEqual(new['original_read_plan_identity'],original['runtime_control_read_plan_identity'])
        self.assertEqual(F.validate_runtime_control_read_plan_v2(new,current['runtime_control_read_plan_identity']),new)
        self.assertEqual(F.validate_runtime_control_read_plan(old,original['runtime_control_read_plan_identity']),old)
        G.validate_record(ROOT,'runtime_read_plan_v2',new)
        for mutate in (lambda p:p['rows'][0].update(action='sts:AssumeRole'),
                       lambda p:p['rows'][-1].update(action='ec2:AuthorizeSecurityGroupIngress'),
                       lambda p:p['required_control_mapping'][4]['row_ids'].pop(),
                       lambda p:p.update(amendment_packet_identity=F.identity('aws_c0_network_ingress_source_authority_amendment_packet/v1','0'*64))):
            bad=copy.deepcopy(new);mutate(bad);bad['map_sha256']=G.sha(G.canonical(bad['required_control_mapping']))
            with self.assertRaises(F.Refusal):F.validate_runtime_control_read_plan_v2(bad,G.identity(bad['schema'],bad))

    def test_actual_complete_group_union_and_empty_rule_arrays_produce_zero(self):
        sources,receipt,attempt,context=self.material()
        self.assertEqual(G.build_r64_exact_request(ROOT,sources,**context),{'GroupIds':['sg-01234567','sg-89abcdef']})
        result=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=attempt,**context)
        value=result['network_ingress_observation']
        self.assertEqual(value['ingress_rule_count'],0)
        self.assertEqual(result['network_ingress_observation_identity'],G.identity(value['schema'],value))
        self.assertEqual(F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context),value)
        self.assertEqual(value['source_receipts_in_order'],sources)
        self.assertEqual(value['rule_receipt'],receipt)

    def test_rehashed_missing_extra_duplicate_wrong_owner_vpc_or_nonempty_rules_refuse(self):
        mutations=[lambda v:v['SecurityGroups'].pop(),
            lambda v:v['SecurityGroups'].append(copy.deepcopy(v['SecurityGroups'][0])),
            lambda v:v['SecurityGroups'][1].update(GroupId=v['SecurityGroups'][0]['GroupId']),
            lambda v:v['SecurityGroups'][0].update(OwnerId='111111111111'),
            lambda v:v['SecurityGroups'][0].update(VpcId='vpc-89abcdef'),
            lambda v:v['SecurityGroups'][0].pop('IpPermissions'),
            lambda v:v['SecurityGroups'][0].update(IpPermissions=None),
            lambda v:v['SecurityGroups'][0].update(IpPermissions=[{'IpProtocol':'-1'}]),
            lambda v:v.update(NextToken='another-page')]
        for mutate in mutations:
            value,attempt,context=self.result();self.mutate_api(value['rule_receipt'],'response',mutate)
            with self.subTest(mutate=mutate),self.assertRaises(F.Refusal):
                F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)

    def test_request_guard_rejects_incomplete_or_cross_instance_sources(self):
        mutations=[(0,'request',lambda v:v.update(InstanceIds=['i-other'])),
            (1,'request',lambda v:v.clear()),
            (1,'response',lambda v:v['NetworkInterfaces'].pop()),
            (1,'response',lambda v:v['NetworkInterfaces'][0]['Attachment'].update(InstanceId='i-other')),
            (1,'response',lambda v:v['NetworkInterfaces'][0]['Groups'][0].update(GroupId='sg-11111111')),
            (0,'response',lambda v:v['Reservations'][0]['Instances'][0].update(InstanceType='t3.large')),
            (0,'response',lambda v:v['Reservations'][0]['Instances'][0]['State'].update(Name='running')),
            (0,'response',lambda v:v['Reservations'][0]['Instances'][0].pop('NetworkInterfaces'))]
        for index,stem,mutate in mutations:
            sources,_,_,context=self.material();self.mutate_api(sources[index],stem,mutate)
            with self.assertRaises(F.Refusal):F.derive_r64_exact_request(sources,**context)
        value,attempt,context=self.result()
        self.mutate_api(value['rule_receipt'],'request',lambda v:v.update(GroupIds=['sg-11111111']))
        with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)

    def test_authentication_retry_freshness_and_response_bounds_are_mandatory(self):
        for mutate in (lambda v:v['ResponseMetadata'].update(HTTPStatusCode=403),
                       lambda v:v['ResponseMetadata'].update(RetryAttempts=1),
                       lambda v:v['ResponseMetadata'].pop('RetryAttempts'),
                       lambda v:v['ResponseMetadata']['HTTPHeaders'].update({'x-amzn-requestid':'other-id'}),
                       lambda v:v.update(Error={'Code':'AccessDenied'})):
            value,attempt,context=self.result();self.mutate_api(value['rule_receipt'],'response',mutate)
            with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)
        for mutate in (lambda r:r.update(requested_utc='2026-09-06T17:50:00Z'),
                       lambda r:r.update(completed_utc='2026-09-06T18:00:08Z'),
                       lambda r:r.update(caller_identity=F.identity('aws_sts_role_session/v1','d'*64)),
                       lambda r:r.update(response_canonical_json_base64='A'*87385),
                       lambda r:r.update(pagination_page=2),lambda r:r.update(pagination_item_count=True)):
            value,attempt,context=self.result();mutate(value['rule_receipt'])
            with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)

    def test_supplied_zero_or_schema_constant_cannot_replace_actual_source_arrays(self):
        value,attempt,context=self.result()
        for mutate in (lambda v:v.update(ingress_rule_count=True),lambda v:v.update(source_receipts_in_order=[]),
                       lambda v:v.update(security_group_ids=[]),lambda v:v.update(rule_receipt={}),
                       lambda v:v.update(zero_science_counters={**F.ZERO,'scientific_runs':1})):
            bad=copy.deepcopy(value);mutate(bad)
            with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(bad,attempt_identity=attempt,**context)

    def test_runtime_rejects_schema_invalid_iso_variants_without_loosening_history(self):
        variants=('2026-09-06 18:00:07Z','20260906T180007Z','2026-09-06T18:00:07.000Z')
        for when in variants:
            value,attempt,context=self.result();value['observed_utc']=context['observed_utc']=when
            with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)
        for index in range(3):
            for field in ('requested_utc','completed_utc'):
                for transform in (lambda s:s.replace('T',' '),lambda s:s.replace('-','').replace(':',''),lambda s:s.replace('Z','.000Z')):
                    value,attempt,context=self.result()
                    receipt=(value['source_receipts_in_order']+[value['rule_receipt']])[index]
                    receipt[field]=transform(receipt[field])
                    with self.assertRaises(F.Refusal):F.validate_r64_ingress_observation(value,attempt_identity=attempt,**context)


class R64CallBudgetTests(unittest.TestCase):
    """Offline ledger state transitions, not authenticated or durable storage."""
    def material(self,index=0):
        sources,receipt,attempt,context=R64IngressAmendmentTests().material()
        for number,r in enumerate(sources+[receipt]):
            for field in ('requested_utc','completed_utc'):
                r[field]=r[field].replace('18:00:','18:%02d:'%index)
            r['request_id']+='-phase-'+str(index)
            response=F.strict_json(base64.b64decode(r['response_canonical_json_base64']))
            response['ResponseMetadata']['RequestId']=r['request_id']
            response['ResponseMetadata']['HTTPHeaders']['x-amzn-requestid']=r['request_id']
            R51ProspectiveAmendmentTests.encode(r,'response',response)
        context['observed_utc']='2026-09-06T18:%02d:07Z'%index
        return sources,receipt,attempt,context

    def empty(self):
        _,_,attempt,_=self.material()
        return G.build_r64_initial_call_budget(ROOT,attempt)['network_ingress_call_budget']

    def reserve(self,budget,index=0):
        sources,_,attempt,context=self.material(index)
        context['observed_utc']='2026-09-06T18:%02d:04Z'%index
        return F.reserve_r64_call(budget,G.identity(F.R64_BUDGET_KIND,budget),sources,
            attempt_identity=attempt,phase=F.R64_READ_PHASES[index],**context)

    def complete(self,budget,index=0):
        sources,receipt,attempt,context=self.material(index)
        value=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=attempt,**context)['network_ingress_observation']
        return F.complete_r64_call(budget,G.identity(F.R64_BUDGET_KIND,budget),value,
            attempt_identity=attempt,phase=F.R64_READ_PHASES[index],**context)

    def test_three_phase_reservations_and_schema_round_trip(self):
        budget=self.empty();original=copy.deepcopy(budget)
        for index in range(3):
            prior=copy.deepcopy(budget);budget=self.reserve(budget,index)
            self.assertEqual(budget['reservations_in_order'][:-1],prior['reservations_in_order'])
            G.validate_record(ROOT,'network_ingress_call_budget',budget)
            budget=self.complete(budget,index)
            G.validate_record(ROOT,'network_ingress_call_budget',budget)
        self.assertEqual(original['reservations_in_order'],[])
        self.assertLess(len(G.canonical(budget)),8192)
        self.assertEqual([v['ordinal'] for v in budget['reservations_in_order']],[1,2,3])
        for phase in F.R64_READ_PHASES+('COMPLETION',):
            sources,_,attempt,context=self.material(3)
            with self.assertRaises(F.Refusal):F.reserve_r64_call(budget,G.identity(F.R64_BUDGET_KIND,budget),sources,
                attempt_identity=attempt,phase=phase,**context)

    def test_pending_failed_and_uncertain_calls_never_return_a_slot(self):
        pending=self.reserve(self.empty());_,_,attempt,context=self.material()
        for budget in [pending]+[F.fail_r64_call(pending,G.identity(F.R64_BUDGET_KIND,pending),
                attempt_identity=attempt,phase='PREDEPLOYMENT',observed_utc=context['observed_utc'],failure_class=c)
                for c in F.R64_FAILURE_CLASSES]:
            G.validate_record(ROOT,'network_ingress_call_budget',budget)
            self.assertEqual(len(budget['reservations_in_order']),1)
            for index in (0,1):
                with self.assertRaises(F.Refusal):self.reserve(budget,index)
            if budget is not pending:
                with self.assertRaises(F.Refusal):self.complete(budget)
                with self.assertRaises(F.Refusal):F.fail_r64_call(budget,G.identity(F.R64_BUDGET_KIND,budget),
                    attempt_identity=attempt,phase='PREDEPLOYMENT',observed_utc=context['observed_utc'],failure_class='TRANSPORT_FAILURE')

    def test_wrong_anchor_attempt_phase_and_replayed_completion_refuse(self):
        empty=self.empty();sources,_,attempt,context=self.material()
        for anchor,target,phase in [(G.identity(F.R64_BUDGET_KIND,{'different':True}),attempt,'PREDEPLOYMENT'),
            (G.identity(F.R64_BUDGET_KIND,empty),F.identity('aws_c0_attempt/v1','d'*64),'PREDEPLOYMENT'),
            (G.identity(F.R64_BUDGET_KIND,empty),attempt,'POSTDEPLOYMENT')]:
            with self.assertRaises(F.Refusal):F.reserve_r64_call(empty,anchor,sources,attempt_identity=target,phase=phase,**context)
        complete=self.complete(self.reserve(empty))
        with self.assertRaises(F.Refusal):self.complete(complete)
        with self.assertRaises(F.Refusal):self.reserve(complete,0)
        with self.assertRaises(F.Refusal):F.validate_r64_call_budget(empty,G.identity(F.R64_BUDGET_KIND,complete),attempt_identity=attempt)

    def test_rehashed_ledger_mutations_and_unclosed_fields_refuse(self):
        budget=self.complete(self.reserve(self.empty()));_,_,attempt,_=self.material()
        for mutate in (lambda b:b.update(extra=True),lambda b:b.update(attempt_identity={}),
            lambda b:b['reservations_in_order'][0].update(ordinal=True),
            lambda b:b['reservations_in_order'][0].update(phase='EXECUTION_PREFLIGHT'),
            lambda b:b['reservations_in_order'][0].update(request={}),
            lambda b:b['reservations_in_order'][0]['request'].update(GroupIds=['sg-01234567','sg-01234567']),
            lambda b:b['reservations_in_order'][0].update(finished_utc='2026-09-06T17:00:00Z'),
            lambda b:b['reservations_in_order'][0].update(failure_class='UNCERTAIN_DELIVERY'),
            lambda b:b['reservations_in_order'][0].update(source_receipt_identities_in_order=[]),
            lambda b:b['reservations_in_order'][0].update(request_id=''),
            lambda b:b['reservations_in_order'][0].update(reserved_utc='2026-09-06 18:00:04Z')):
            bad=copy.deepcopy(budget);mutate(bad)
            with self.assertRaises(F.Refusal):F.validate_r64_call_budget(bad,G.identity(F.R64_BUDGET_KIND,bad),attempt_identity=attempt)

    def test_completion_requires_exact_precall_sources_caller_and_time(self):
        budget=self.reserve(self.empty());sources,receipt,attempt,context=self.material()
        observation=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=attempt,**context)['network_ingress_observation']
        for mutate in (lambda b:b['reservations_in_order'][0].update(reserved_utc='2026-09-06T18:00:06Z'),
                       lambda b:b['reservations_in_order'][0].update(caller_identity=F.identity('aws_sts_role_session/v1','e'*64)),
                       lambda b:b['reservations_in_order'][0]['source_receipt_identities_in_order'].__setitem__(0,F.identity('aws_c0_api_request_response_receipt/v1','e'*64)),
                       lambda b:b['reservations_in_order'][0]['request'].update(GroupIds=['sg-01234567'])):
            bad=copy.deepcopy(budget);mutate(bad)
            with self.assertRaises(F.Refusal):F.complete_r64_call(bad,G.identity(F.R64_BUDGET_KIND,bad),observation,
                attempt_identity=attempt,phase='PREDEPLOYMENT',**context)
        complete=self.complete(budget)
        with self.assertRaises(F.Refusal):F.reserve_r64_call(complete,G.identity(F.R64_BUDGET_KIND,complete),sources,
            attempt_identity=attempt,phase='POSTDEPLOYMENT',**context)


class R64PhaseBindingTests(unittest.TestCase):
    def material(self,index=0):
        fixture=R64CallBudgetTests();budget=fixture.empty()
        for n in range(index):budget=fixture.complete(fixture.reserve(budget,n),n)
        previous=copy.deepcopy(budget);budget=fixture.complete(fixture.reserve(budget,index),index)
        sources,receipt,attempt,context=fixture.material(index)
        observation=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=attempt,**context)['network_ingress_observation']
        read=G.build_runtime_control_read_plan_fields_v2(ROOT)
        args={'phase':F.R64_READ_PHASES[index],'attempt_identity':attempt,
            'read_plan':read['runtime_control_read_plan'],'read_plan_identity':read['runtime_control_read_plan_identity'],
            'previous_budget':previous,'previous_budget_identity':G.identity(F.R64_BUDGET_KIND,previous),
            'caller_identity':context['caller_identity'],'authentication_source_identity':context['authentication_source_identity'],
            'phase_not_before_utc':'2026-09-06T18:%02d:00Z'%index,'validation_utc':context['observed_utc']}
        fields=G.build_r64_phase_binding(ROOT,observation,budget,**args)
        return fields['network_ingress_phase_binding'],args

    def test_three_distinct_phase_results_bind_history_and_actual_source(self):
        for index in range(3):
            record,args=self.material(index)
            self.assertEqual(F.validate_r64_phase_binding(record,**args),record)
            G.validate_record(ROOT,'network_ingress_phase_binding',record)
            self.assertEqual(len(record['call_budget']['reservations_in_order']),index+1)
            self.assertEqual(record['call_budget']['reservations_in_order'][:-1],args['previous_budget']['reservations_in_order'])

    def test_wrong_phase_previous_attempt_plan_collector_and_anchor_refuse(self):
        for field,value in [('phase','COMPLETION'),('phase','POSTDEPLOYMENT'),
            ('attempt_identity',F.identity('aws_c0_attempt/v1','0'*64)),
            ('previous_budget_identity',F.identity(F.R64_BUDGET_KIND,'0'*64)),
            ('caller_identity',F.identity('aws_sts_role_session/v1','0'*64)),
            ('authentication_source_identity',F.identity('aws_authenticated_api_source/v1','0'*64)),
            ('read_plan_identity',F.identity('aws_c0_runtime_control_read_plan/v2','0'*64))]:
            record,args=self.material();args[field]=value
            with self.assertRaises(F.Refusal):F.validate_r64_phase_binding(record,**args)

    def test_fresh_at_collection_is_not_fresh_at_late_consumption(self):
        record,args=self.material()
        for field,value in [('validation_utc','2026-09-06T18:05:02Z'),
            ('validation_utc','2026-09-06T18:00:06Z'),
            ('phase_not_before_utc','2026-09-06T18:00:02Z')]:
            bad=copy.deepcopy(args);bad[field]=value
            with self.assertRaises(F.Refusal):F.validate_r64_phase_binding(record,**bad)
        args['validation_utc']='2026-09-06T18:05:01Z'
        self.assertEqual(F.validate_r64_phase_binding(record,**args),record)

    def test_rehashed_budget_cannot_replace_current_or_prior_evidence(self):
        for mutate in (lambda b:b['reservations_in_order'][-1].update(request_id='offline-other-id'),
            lambda b:b['reservations_in_order'][-1].update(reserved_utc='2026-09-06T18:01:01Z'),
            lambda b:b['reservations_in_order'][-1].update(reserved_utc='2026-09-06T18:01:06Z'),
            lambda b:b['reservations_in_order'][-1].update(observation_identity=F.identity('aws_c0_network_ingress_observation/v1','d'*64)),
            lambda b:b['reservations_in_order'][0].update(request_id='offline-other-id'),
            lambda b:b['reservations_in_order'][-1]['request'].update(GroupIds=['sg-01234567'])):
            record,args=self.material(1);mutate(record['call_budget'])
            record['call_budget_identity']=G.identity(F.R64_BUDGET_KIND,record['call_budget'])
            with self.assertRaises(F.Refusal):F.validate_r64_phase_binding(record,**args)

    def test_reset_budget_and_pending_tail_cannot_replace_phase_success(self):
        record,args=self.material(1)
        reset=R64CallBudgetTests().empty()
        record['previous_call_budget_identity']=args['previous_budget_identity']=G.identity(F.R64_BUDGET_KIND,reset)
        args['previous_budget']=reset
        with self.assertRaises(F.Refusal):F.validate_r64_phase_binding(record,**args)
        record,args=self.material()
        record['call_budget']=R64CallBudgetTests().reserve(R64CallBudgetTests().empty())
        record['call_budget_identity']=G.identity(F.R64_BUDGET_KIND,record['call_budget'])
        with self.assertRaises(F.Refusal):F.validate_r64_phase_binding(record,**args)


class R64LocalBudgetStoreTests(unittest.TestCase):
    """Real private temporary files, offline synthetic observations, no AWS."""
    def setUp(self):
        self.attempt=F.identity('aws_c0_attempt/v1',hashlib.sha256(os.urandom(32)).hexdigest())
        self.store=G.R64LocalCallBudgetStore(ROOT,self.attempt)
        self.initial=self.store.initialize()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        # Only this test's newly created, non-recursive private ledger files.
        os.chmod(self.store.path,0o700)
        for child in self.store.path.iterdir():child.unlink()
        self.store.path.rmdir()

    def material(self,index=0):
        sources,receipt,_,context=R64CallBudgetTests().material(index)
        return sources,receipt,context

    def reserve(self,store=None,expected=None,index=0):
        sources,_,context=self.material(index)
        context['observed_utc']='2026-09-06T18:%02d:04Z'%index
        return (store or self.store).reserve(expected or self.initial['network_ingress_call_budget_identity'],
            sources,phase=F.R64_READ_PHASES[index],**context)

    def test_durable_reservation_reopens_without_reset_or_replay(self):
        reserved=self.reserve();reopened=G.R64LocalCallBudgetStore(ROOT,self.attempt)
        self.assertEqual(reopened.load(reserved['network_ingress_call_budget_identity']),reserved)
        with self.assertRaises(FileExistsError):reopened.initialize()
        with self.assertRaises(Exception):self.reserve(reopened)
        with self.assertRaises(Exception):self.reserve(reopened,reserved['network_ingress_call_budget_identity'])
        self.assertEqual(sorted(p.name for p in self.store.path.iterdir()),['00.json','01.json'])
        for p in self.store.path.iterdir():self.assertEqual(p.stat().st_mode&0o777,0o600)
        self.assertEqual(self.store.path.stat().st_mode&0o777,0o700)

    def test_complete_and_three_slots_preserve_all_seven_snapshots(self):
        current=self.initial
        for index in range(3):
            reserved=self.reserve(expected=current['network_ingress_call_budget_identity'],index=index)
            sources,receipt,context=self.material(index)
            observation=G.build_r64_ingress_observation(ROOT,sources,receipt,attempt_identity=self.attempt,**context)['network_ingress_observation']
            current=self.store.complete(reserved['network_ingress_call_budget_identity'],observation,phase=F.R64_READ_PHASES[index],**context)
        self.assertEqual(self.store.load(current['network_ingress_call_budget_identity']),current)
        self.assertEqual(sorted(p.name for p in self.store.path.iterdir()),['%02d.json'%i for i in range(7)])
        with self.assertRaises(Exception):self.reserve(expected=current['network_ingress_call_budget_identity'],index=2)

    def test_racing_process_equivalent_writers_have_only_one_winner(self):
        import concurrent.futures
        import threading
        barrier=threading.Barrier(2)
        def contender():
            local=G.R64LocalCallBudgetStore(ROOT,self.attempt)
            barrier.wait()
            try:return self.reserve(local)
            except Exception:return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            winners=list(pool.map(lambda _:contender(),range(2)))
        accepted=[r for r in winners if r is not None]
        self.assertEqual(len(accepted),1)
        self.assertEqual(self.store.load(accepted[0]['network_ingress_call_budget_identity']),accepted[0])

    def test_torn_write_is_preserved_and_blocks_next_call(self):
        real_write=os.write;calls=[]
        def interrupted(fd,raw):
            calls.append(True)
            if len(calls)==1:return real_write(fd,raw[:30])
            raise OSError('offline injected interruption')
        with mock.patch.object(G.os,'write',side_effect=interrupted):
            with self.assertRaises(OSError):self.reserve()
        self.assertEqual((self.store.path/'01.json').stat().st_size,30)
        with self.assertRaises(Exception):self.reserve()
        self.assertEqual(sorted(p.name for p in self.store.path.iterdir()),['00.json','01.json'])

    def test_failed_fsync_keeps_slot_reserved_and_cannot_be_reused(self):
        with mock.patch.object(G.os,'fsync',side_effect=OSError('offline injected sync failure')):
            with self.assertRaises(OSError):self.reserve()
        candidate=F.strict_json((self.store.path/'01.json').read_bytes())
        self.assertEqual(candidate['reservations_in_order'][-1]['state'],'RESERVED')
        with self.assertRaises(Exception):self.reserve(expected=G.identity(F.R64_BUDGET_KIND,candidate))
        with self.assertRaises(Exception):self.reserve()

    def test_unsafe_or_incomplete_local_history_refused(self):
        initial_path=self.store.path/'00.json';raw=initial_path.read_bytes()
        for mutate,restore in [
            (lambda:initial_path.chmod(0o644),lambda:initial_path.chmod(0o600)),
            (lambda:self.store.path.chmod(0o755),lambda:self.store.path.chmod(0o700)),
            (lambda:(self.store.path/'unexpected').write_bytes(b'x'),lambda:(self.store.path/'unexpected').unlink()),
            (lambda:(self.store.path/'02.json').write_bytes(raw),lambda:(self.store.path/'02.json').unlink()),
            (lambda:os.link(initial_path,self.store.path/'outside-link'),lambda:(self.store.path/'outside-link').unlink())]:
            mutate()
            try:
                with self.assertRaises(Exception):self.store.load(self.initial['network_ingress_call_budget_identity'])
            finally:restore()
        initial_path.unlink();initial_path.symlink_to('missing-target')
        with self.assertRaises(OSError):self.store.load(self.initial['network_ingress_call_budget_identity'])

    def test_failed_transport_state_is_durable_and_never_fabricates_success(self):
        reserved=self.reserve()
        failed=self.store.fail(reserved['network_ingress_call_budget_identity'],phase='PREDEPLOYMENT',
            observed_utc='2026-09-06T18:00:07Z',failure_class='UNCERTAIN_DELIVERY')
        self.assertEqual(self.store.load(failed['network_ingress_call_budget_identity']),failed)
        self.assertIsNone(failed['network_ingress_call_budget']['reservations_in_order'][-1]['observation_identity'])
        with self.assertRaises(Exception):self.reserve(expected=failed['network_ingress_call_budget_identity'],index=1)


class SealedRoleProducerTests(unittest.TestCase):
    def material(self):
        values=PhaseObligationProducerTests().material();receipts={k:values[2][k] for k in ('R02','R03','R13','R14')}
        name='EBU-Rehearsal-EC2-Role';role={'Arn':'arn:aws:iam::623609441658:role/'+name,'RoleName':name,'RoleId':'AROA'+'A'*16}
        profile={'Arn':'arn:aws:iam::623609441658:instance-profile/'+name,'InstanceProfileName':name,'Roles':[role]}
        requests={'R02':{'InstanceIds':[F.INSTANCE_ID]},'R03':{'Filters':[{'Name':'instance-id','Values':[F.INSTANCE_ID]}]},
                  'R13':{'InstanceProfileName':name},'R14':{'RoleName':name}}
        responses={'R02':{'Reservations':[{'Instances':[{'InstanceId':F.INSTANCE_ID,'State':{'Name':'stopped'},'IamInstanceProfile':{'Arn':profile['Arn']}}]}]},
            'R03':{'IamInstanceProfileAssociations':[{'InstanceId':F.INSTANCE_ID,'State':'associated','IamInstanceProfile':{'Arn':profile['Arn']}}]},
            'R13':{'InstanceProfile':profile},'R14':{'Role':role}}
        for row,receipt in receipts.items():
            responses[row]['ResponseMetadata']={'RequestId':receipt['request_id'],'HTTPStatusCode':200}
            R51ProspectiveAmendmentTests.encode(receipt,'request',requests[row])
            R51ProspectiveAmendmentTests.encode(receipt,'response',responses[row])
        # Complete schema-shaped offline snapshot, not actual AWS evidence.
        snapshot={'schema':'aws_c0_private_infrastructure_snapshot/v1','authority_id':F.AUTHORITY_ID,
            'record_class':'NON_SCIENTIFIC_AWS_C0_EVIDENCE','scientific_execution_authorized':False,
            'stage_f_readiness_claimed':False,'zero_science_counters':copy.deepcopy(F.ZERO),
            'observed_utc':values[4]['latest'],'account_identity':F.identity('aws_account_identity/v1','a'*64),
            'region':F.REGION,'instance_id':F.INSTANCE_ID,'instance_state':'stopped','workflow_type':'STANDARD',
            'workflow_identity':F.identity('aws_step_functions_standard_workflow/v1','b'*64),
            'iam_policy_set_identity':F.identity('aws_iam_policy_set/v1','c'*64),
            'ssm_document_sha256':'d'*64,'quota_observation_identity':F.identity('aws_service_quota_observation/v1','e'*64),
            'quota_fact_verified':True,'snapshot_sha256':'f'*64}
        snapshot['record_sha256']=F.digest(F.canonical_bytes(snapshot))
        return F.canonical_bytes(snapshot),receipts,values[4]

    def test_real_constructor_derives_role_id_and_accepted_closed_context(self):
        raw,receipts,context=self.material()
        result=G.build_sealed_role_launch_fields(ROOT,raw,receipts,**context)
        nested=result['sealed_ec2_role_context_preimage']
        self.assertEqual(nested['role_id'],'AROA'+'A'*16)
        self.assertEqual(nested['private_infrastructure_snapshot_sha256'],F._root_digest(F.strict_json(raw)))
        self.assertNotEqual(nested['private_infrastructure_snapshot_sha256'],F.digest(raw))
        self.assertEqual(nested['instance_profile_role_observation_preimage']['source_row_ids'],['R02','R03','R13','R14'])
        self.assertEqual(G.validate_named_definition(ROOT,'sealed_ec2_role_context_preimage',nested),nested)
        self.assertEqual(result['sealed_ec2_role_context_identity'],G.identity('aws_c0_sealed_ec2_role_context/v1',nested))

    def test_actual_response_drift_and_incomplete_role_inventory_refused(self):
        for row,mutate in [('R02',lambda d:d['Reservations'][0]['Instances'][0].update(InstanceId='i-other')),
                           ('R03',lambda d:d['IamInstanceProfileAssociations'][0].update(State='disassociating')),
                           ('R13',lambda d:d['InstanceProfile']['Roles'].append(copy.deepcopy(d['InstanceProfile']['Roles'][0]))),
                           ('R14',lambda d:d['Role'].update(RoleId='AROA'+'B'*16)),
                           ('R13',lambda d:d.update(NextToken='more'))]:
            raw,receipts,context=self.material();response=R51ProspectiveAmendmentTests.decode(receipts[row]);mutate(response)
            R51ProspectiveAmendmentTests.encode(receipts[row],'response',response)
            with self.assertRaises(ValueError):G.build_sealed_role_launch_fields(ROOT,raw,receipts,**context)

    def test_snapshot_digest_source_identity_and_missing_source_refused(self):
        raw,receipts,context=self.material();snapshot=F.strict_json(raw);snapshot['quota_fact_verified']=False
        with self.assertRaises(RuntimeError):G.build_sealed_role_launch_fields(ROOT,F.canonical_bytes(snapshot),receipts,**context)
        raw,receipts,context=self.material();receipts.pop('R13')
        with self.assertRaises(ValueError):G.build_sealed_role_launch_fields(ROOT,raw,receipts,**context)
        raw,receipts,context=self.material();receipts['R02']['caller_identity']=F.identity('aws_sts_role_session/v1','c'*64)
        with self.assertRaises(ValueError):G.build_sealed_role_launch_fields(ROOT,raw,receipts,**context)

    def test_complete_snapshot_shape_state_and_chronology_are_required(self):
        for mutate in (lambda d:d.pop('workflow_identity'),lambda d:d.update(instance_state='running'),
                       lambda d:d.update(quota_fact_verified=False),lambda d:d.update(observed_utc='2026-09-06T17:59:59Z'),
                       lambda d:d.update(observed_utc='2026-09-06T18:00:30Z'),lambda d:d.update(extra='not accepted')):
            raw,receipts,context=self.material();snapshot=F.strict_json(raw);mutate(snapshot)
            snapshot.pop('record_sha256');snapshot['record_sha256']=F.digest(F.canonical_bytes(snapshot))
            with self.assertRaises((ValueError,G.jsonschema.ValidationError)):
                G.build_sealed_role_launch_fields(ROOT,F.canonical_bytes(snapshot),receipts,**context)
        raw,receipts,context=self.material();response=R51ProspectiveAmendmentTests.decode(receipts['R02'])
        response['Reservations'][0]['Instances'][0]['State']['Name']='running'
        R51ProspectiveAmendmentTests.encode(receipts['R02'],'response',response)
        with self.assertRaisesRegex(ValueError,'instance state disagree'):
            G.build_sealed_role_launch_fields(ROOT,raw,receipts,**context)


class SsmDispatchInterfaceTests(unittest.TestCase):
    def material(self):
        launch=load('aws/c0/fixtures/launch-request.valid.json');prefix=launch['artifact_prefix']
        args=C.argparse.Namespace(bucket='valid-bucket',artifact_prefix=prefix,
            rehearsal_id=launch['rehearsal_id'],attempt_id=launch['attempt_id'],region='us-east-1',
            workflow_execution_arn='arn:aws:states:us-east-1:623609441658:execution:EBU-C0-492a4f1:'+launch['attempt_id'],
            ssm_client_request_token='OFFLINE_START_0001',ssm_expected_command_not_before_utc='2026-09-06T18:00:00Z',
            ssm_expected_command_not_after_utc='2026-09-06T18:01:00Z',output='/var/lib/ebu-c0/requests/'+launch['attempt_id']+'.json')
        for stem,suffix in (('launch','launch-request'),('live_packet','live-packet'),('live_authorization','live-authorization')):
            for key,value in {'key':prefix+suffix+'.json','version_id':'observed-offline-version','sha256':'a'*64,'bytes':1234}.items():
                setattr(args,stem+'_'+key,value)
        semantic=C.ssm_semantic_parameters_from_argv(args)
        result=G.build_ssm_dispatch_transport_v2(ROOT,semantic,launch['attempt_identity'],'1')
        args.ssm_dispatch_request_canonical_json_base64=result['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
        args.ssm_dispatch_request_sha256=result['transport_parameters']['SsmDispatchRequestSha256'][0]
        return args,result,launch

    def test_complete_accepted_start_envelope_and_exact_transport_arity(self):
        args,result,_=self.material()
        self.assertEqual(C.validate_ssm_dispatch_v2(args),result['dispatch_request_preimage'])
        self.assertEqual(len(result['semantic_parameters']),21)
        self.assertEqual(len(result['transport_parameters']),2)
        self.assertEqual(len(result['send_command_parameters']),23)
        self.assertEqual(result['dispatch_request_identity'],G.identity('aws_c0_ssm_dispatch_request/v2',result['dispatch_request_preimage']))
        document=load('aws/c0/ssm/EBU-C0-Start-v1.yaml')
        self.assertEqual(set(document['parameters']),set(result['send_command_parameters']))
        self.assertEqual(document,load('aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml')['Resources']['EBUC0StartDocument']['Properties']['Content'])
        self.assertNotIn('SsmDispatchRequestBase64',document['parameters'])
        token=args.ssm_client_request_token
        self.assertIsNotNone(C.re.fullmatch(document['parameters']['SsmClientRequestToken']['allowedPattern'],token))
        guards=[line for line in document['mainSteps'][0]['inputs']['runCommand']
                if 'SSM_SsmClientRequestToken-' in line and 'grep -Eq' in line]
        self.assertEqual(len(guards),1)
        # Execute only this fixed string-format/regex guard, never the document.
        for candidate,expected in ((token,0),('short',1),('A'*65,1),('bad token',1)):
            tested=C.subprocess.run(['/bin/sh','-c',guards[0]],env={'SSM_SsmClientRequestToken':candidate},
                                    stdout=C.subprocess.PIPE,stderr=C.subprocess.PIPE,timeout=5)
            self.assertEqual(tested.returncode,expected)

    def test_bare_map_unknown_kind_extra_field_and_split_transport_refused(self):
        for mutate in (lambda d:d['semantic_parameters'],lambda d:{**d,'schema':'aws_c0_controller_local_helper_request/v1'},
                       lambda d:{**d,'extra':True},lambda d:{**d,'target_instance_id':'i-other'},
                       lambda d:{**d,'document_version':'$LATEST'},lambda d:{**d,'document_name':'AWS-RunShellScript'}):
            args,result,_=self.material();raw=C.canonical_bytes(mutate(result['dispatch_request_preimage']))
            args.ssm_dispatch_request_canonical_json_base64=base64.b64encode(raw).decode();args.ssm_dispatch_request_sha256=C.digest(raw)
            with self.assertRaises(C.Refusal):C.validate_ssm_dispatch_v2(args)
        args,_,_=self.material();args.ssm_dispatch_request_sha256='0'*64
        with self.assertRaisesRegex(C.Refusal,'pair derivation'):C.validate_ssm_dispatch_v2(args)
        args,_,_=self.material();args.ssm_dispatch_request_canonical_json_base64+='!'
        with self.assertRaises(C.Refusal):C.validate_ssm_dispatch_v2(args)

    def test_semantics_are_explicit_argv_and_mismatch_refuses_before_credentials(self):
        for key,value in (('region','us-west-2'),('bucket','dot.bucket'),('launch_bytes',True),('launch_bytes',0),
                          ('launch_key','other-prefix/launch.json'),('launch_version_id',''),
                          ('workflow_execution_arn','arn:aws:states:us-east-1:111111111111:execution:W:ATTEMPT-CLOSURE-SUCCESS'),
                          ('ssm_expected_command_not_before_utc','2026-09-06T18:00:00.1Z'),
                          ('ssm_expected_command_not_before_utc','20260906T180000Z'),
                          ('ssm_expected_command_not_before_utc','2026-09-06 18:00:00Z'),
                          ('ssm_expected_command_not_after_utc','2026-09-06T17:00:00Z')):
            args,_,_=self.material();setattr(args,key,value)
            provider=mock.Mock(side_effect=AssertionError('credentials must not be requested'))
            with self.assertRaises(C.Refusal):C.prepare_request(args,credential_provider=provider)
            provider.assert_not_called()
        args,_,_=self.material();args.launch_bytes=1235
        with self.assertRaisesRegex(C.Refusal,'explicit argv'):C.validate_ssm_dispatch_v2(args)
        args,_,_=self.material();del args.region
        with self.assertRaisesRegex(C.Refusal,'21 explicit'):C.validate_ssm_dispatch_v2(args)

    def test_actual_document_and_attempt_must_match_authenticated_sources(self):
        _,result,launch=self.material();dispatch=result['dispatch_request_preimage']
        observed={'Name':'EBU-C0-Start-v1','DocumentVersion':'1','Status':'Active','DocumentType':'Command'}
        def auth(value):
            return {'deployment_completed_utc':'2026-09-06T17:58:00Z','observed_utc':'2026-09-06T18:00:00Z',
                'post_deployment_control_preimages':[DeploymentSequenceTests.control('SSM_DOCUMENT',value,'2026-09-06T17:59:00Z')]}
        C.bind_ssm_dispatch_to_authenticated_sources(dispatch,launch,auth(observed))
        for field,value in (('Name','other'),('DocumentVersion','2'),('Status','Creating'),('DocumentType','Automation')):
            with self.assertRaises(C.Refusal):C.bind_ssm_dispatch_to_authenticated_sources(dispatch,launch,auth({**observed,field:value}))
        with self.assertRaises(C.Refusal):
            C.bind_ssm_dispatch_to_authenticated_sources(dispatch,{**launch,'attempt_identity':C.identity('aws_c0_attempt/v1','b'*64)},auth(observed))
        a=auth(observed);a['post_deployment_control_preimages']*=2
        with self.assertRaises(C.Refusal):C.bind_ssm_dispatch_to_authenticated_sources(dispatch,launch,a)
        a=auth(observed);a['post_deployment_control_preimages'][0]['identity']['sha256']='0'*64
        with self.assertRaises(C.Refusal):C.bind_ssm_dispatch_to_authenticated_sources(dispatch,launch,a)

    def test_parser_supplies_region_and_all_semantics_from_flags(self):
        args,result,_=self.material();argv=['prepare-request-v4']
        for name in C.SEMANTIC21:
            flag='bucket' if name=='artifact_bucket' else name.replace('_','-')
            argv.append('--'+flag+'='+str(getattr(args,'bucket' if name=='artifact_bucket' else name)))
        for name in C.TRANSPORT2:argv.append('--'+name.replace('_','-')+'='+getattr(args,name))
        argv.append('--output='+args.output)
        parsed=C.parser().parse_args(argv)
        self.assertEqual(C.validate_ssm_dispatch_v2(parsed),result['dispatch_request_preimage'])


class LocalHelperTransportTests(unittest.TestCase):
    def material(self,operation='STATUS'):
        args,start,_=SsmDispatchInterfaceTests().material()
        deadline='2026-09-06T18:15:00Z'
        helper=G.build_local_helper_transport_v1(ROOT,start['dispatch_request_preimage'],operation,deadline)
        context={'semantic_parameters':start['semantic_parameters'],'expected_start_dispatch':start['dispatch_request_preimage'],
            'attempt_deadline_utc':deadline,'now':C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc)}
        return args,helper,context

    def test_helper_plan_is_distinct_closed_and_has_no_start_or_aws_effect(self):
        for operation in ('STATUS','SAFE_CLOSE'):
            args,helper,context=self.material(operation)
            with (mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials')),
                  mock.patch.object(C,'_download',side_effect=AssertionError('no network')),
                  mock.patch.object(C,'prepare_request',side_effect=AssertionError('no preparation')),
                  mock.patch.object(C,'_run',side_effect=AssertionError('no external command'))):
                self.assertEqual(C.validate_local_helper_request_v1(helper['helper_request'],**context),helper['helper_request'])
            self.assertEqual(len(helper['send_command_parameters']),23)
            self.assertEqual(helper['send_command_parameters'].keys(),{*context['semantic_parameters'],*helper['transport_parameters']})
            G.validate_record(ROOT,'ssm_local_helper_request',helper['helper_request'])
            args.ssm_dispatch_request_canonical_json_base64=helper['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
            args.ssm_dispatch_request_sha256=helper['transport_parameters']['SsmDispatchRequestSha256'][0]
            with self.assertRaisesRegex(C.Refusal,'full SSM dispatch'):C.validate_ssm_dispatch_v2(args)

    def test_unknown_start_extra_fields_and_cross_attempt_refused(self):
        for mutate in (lambda d:d.update(operation='START'),lambda d:d.update(operation='RUN_SCIENCE'),
                       lambda d:d.update(schema='aws_c0_ssm_dispatch_request/v2'),lambda d:d.update(extra=True),
                       lambda d:d['start_dispatch_request'].update(document_version='2'),
                       lambda d:d['start_dispatch_request'].update(attempt_identity=C.identity('aws_c0_attempt/v1','c'*64))):
            _,helper,context=self.material();record=helper['helper_request'];mutate(record)
            with self.assertRaises(C.Refusal):C.validate_local_helper_request_v1(record,**context)

    def test_expired_early_extended_and_noncanonical_deadlines_refused(self):
        _,helper,context=self.material()
        for now in (C.dt.datetime(2026,9,6,17,59,tzinfo=C.dt.timezone.utc),
                    C.dt.datetime(2026,9,6,18,15,tzinfo=C.dt.timezone.utc),
                    C.dt.datetime(2026,9,6,18,16,tzinfo=C.dt.timezone.utc),C.dt.datetime(2026,9,6,18,2)):
            with self.assertRaises(C.Refusal):C.validate_local_helper_request_v1(helper['helper_request'],**{**context,'now':now})
        for deadline in ('2026-09-06T18:16:00Z','2026-09-06T18:15:00.0Z'):
            record={**helper['helper_request'],'attempt_deadline_utc':deadline}
            with self.assertRaises(C.Refusal):C.validate_local_helper_request_v1(record,**context)
        for deadline in ('2026-09-07T18:15:00Z','2026-09-06T17:00:00Z'):
            with self.assertRaises(ValueError):
                G.build_local_helper_transport_v1(ROOT,context['expected_start_dispatch'],'STATUS',deadline)

    def test_invalid_expected_semantics_cannot_validate_themselves(self):
        for bad in ({}, {'ArtifactBucket':['valid-bucket']}):
            _,helper,context=self.material();record=helper['helper_request']
            record['start_dispatch_request']['semantic_parameters']=bad
            context['expected_start_dispatch']['semantic_parameters']=bad;context['semantic_parameters']=bad
            with self.assertRaises(C.Refusal):C.validate_local_helper_request_v1(record,**context)
        for value in ([1234],['01234'],['1','2'],[True]):
            _,helper,context=self.material();record=helper['helper_request']
            for params in (record['start_dispatch_request']['semantic_parameters'],context['expected_start_dispatch']['semantic_parameters'],context['semantic_parameters']):
                params['LaunchRequestBytes']=value
            with self.assertRaises(C.Refusal):C.validate_local_helper_request_v1(record,**context)


class LocalHelperDecodeTests(unittest.TestCase):
    def material(self,operation='STATUS'):
        args,helper,context=LocalHelperTransportTests().material(operation)
        args.ssm_dispatch_request_canonical_json_base64=helper['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
        args.ssm_dispatch_request_sha256=helper['transport_parameters']['SsmDispatchRequestSha256'][0]
        del context['semantic_parameters']
        return args,helper,context

    def test_helper_decode_requires_separate_expected_context_and_no_effects(self):
        for operation in ('STATUS','SAFE_CLOSE'):
            args,helper,context=self.material(operation)
            with (mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials')),
                  mock.patch.object(C,'_download',side_effect=AssertionError('no network')),
                  mock.patch.object(C,'prepare_request',side_effect=AssertionError('no preparation')),
                  mock.patch.object(C,'_run',side_effect=AssertionError('no command')),
                  mock.patch.object(C.os,'open',side_effect=AssertionError('no filesystem'))):
                self.assertEqual(C.validate_local_helper_transport_v1(args,**context),helper['helper_request'])
            context['expected_start_dispatch']=copy.deepcopy(context['expected_start_dispatch'])
            context['expected_start_dispatch']['document_version']='2'
            with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)
        args,_,context=self.material();args.launch_bytes+=1
        with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)

    def test_encoded_bound_split_hash_noncanonical_and_start_refusals(self):
        for encoded in ('A'*21849,None,123,'!notbase64!'):
            args,_,context=self.material();args.ssm_dispatch_request_canonical_json_base64=encoded
            with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)
        args,_,context=self.material();args.ssm_dispatch_request_sha256='0'*64
        with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)
        for raw in (b'{}\n',b'{"a":1,"a":1}',b'[]',b' '*16385):
            args,_,context=self.material();args.ssm_dispatch_request_canonical_json_base64=base64.b64encode(raw).decode()
            args.ssm_dispatch_request_sha256=C.digest(raw)
            with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)
        args,_,_=SsmDispatchInterfaceTests().material();_,_,context=self.material()
        with self.assertRaises(C.Refusal):C.validate_local_helper_transport_v1(args,**context)
        # Nonzero base64 pad bits decode identically, but are not canonical.
        args,_,_=self.material();args.ssm_dispatch_request_canonical_json_base64='e31='
        args.ssm_dispatch_request_sha256=C.digest(b'{}')
        with self.assertRaisesRegex(C.Refusal,'pair derivation'):C._decode_ssm_transport(args)


class LocalHelperSourceTests(unittest.TestCase):
    def material(self):
        args,_,_=SsmDispatchInterfaceTests().material()
        launch=current_launch(load('aws/c0/fixtures/launch-request.valid.json'))
        launch.update(observed_utc='2026-09-06T18:00:00Z',attempt_deadline_utc='2026-09-06T18:40:00Z',cleanup_deadline_utc='2026-09-06T18:50:00Z')
        launch['cost_envelope']['accounting_window'].update(start_inclusive_utc='2026-09-06T00:00:00Z',end_exclusive_utc='2026-09-07T00:00:00Z')
        launch=reroot(launch);raws={'launch':C.canonical_bytes(launch)}
        def receipt(stem):
            raw=raws[stem]
            return {'bucket_identity':launch['closure_seed_object']['bucket_identity'],'key':getattr(args,stem+'_key'),
                'version_id':getattr(args,stem+'_version_id'),'bytes':len(raw),'sha256':C.digest(raw),
                'checksum_sha256_base64':base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        packet={'schema':'aws_c0_live_packet/v6','launch_request_identity':C.identity('aws_c0_launch_request/v6',C.root_digest(launch)),
            'launch_request_object':receipt('launch'),'packet_disposition':'AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED'}
        raws['live_packet']=C.canonical_bytes(packet)
        observed={'Name':'EBU-C0-Start-v1','DocumentVersion':'1','Status':'Active','DocumentType':'Command'}
        auth={'schema':'aws_c0_live_authorization/v6','live_packet_identity':C.identity('aws_c0_live_packet/v6',C.digest(raws['live_packet'])),
            'live_packet_object':receipt('live_packet'),'attempt_identity':launch['attempt_identity'],
            'deployment_completed_utc':'2026-09-06T17:58:00Z','observed_utc':'2026-09-06T18:00:00Z',
            'post_deployment_control_preimages':[DeploymentSequenceTests.control('SSM_DOCUMENT',observed,'2026-09-06T17:59:00Z')]}
        raws['live_authorization']=C.canonical_bytes(auth)
        for stem,raw in raws.items():setattr(args,stem+'_sha256',C.digest(raw));setattr(args,stem+'_bytes',len(raw))
        start=G.build_ssm_dispatch_transport_v2(ROOT,C.ssm_semantic_parameters_from_argv(args),launch['attempt_identity'],'1')
        args.ssm_dispatch_request_canonical_json_base64=start['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
        args.ssm_dispatch_request_sha256=start['transport_parameters']['SsmDispatchRequestSha256'][0]
        bykey={getattr(args,stem+'_key'):raw for stem,raw in raws.items()};stored={}
        def transport(host,uri,query,headers):
            raw=bykey[C.urllib.parse.unquote(uri[1:])]
            return raw,{'version_id':'observed-offline-version','checksum_sha256':base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                'etag':'offline-etag','request_id':'offline-request-id','tls_certificate_sha256':'a'*64}
        with mock.patch.object(C,'_exclusive',side_effect=lambda path,raw:stored.update({path.name:raw})):
            C.prepare_request(args,credential_provider=lambda:{'access_key_id':'OFFLINE_KEY','secret_access_key':'OFFLINE_SECRET','session_token':'OFFLINE_TOKEN'},
                transport=transport,now=C.dt.datetime(2026,9,6,18,0,30,tzinfo=C.dt.timezone.utc))
        helper=G.build_local_helper_transport_v1(ROOT,start['dispatch_request_preimage'],'STATUS',launch['attempt_deadline_utc'])
        args.ssm_dispatch_request_canonical_json_base64=helper['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
        args.ssm_dispatch_request_sha256=helper['transport_parameters']['SsmDispatchRequestSha256'][0]
        return args,stored[args.attempt_id+'.json'],stored[args.attempt_id+'.source.json']

    def test_actual_prepare_producer_to_helper_binding_without_second_download(self):
        args,launch_raw,source_raw=self.material()
        with (mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials')),
              mock.patch.object(C,'_download',side_effect=AssertionError('no download')),
              mock.patch.object(C,'prepare_request',side_effect=AssertionError('no second prepare')),
              mock.patch.object(C,'_run',side_effect=AssertionError('no command'))):
            context=C.validate_helper_local_source_context(args,launch_raw,source_raw)
            helper=C.validate_local_helper_transport_v1(args,expected_start_dispatch=context['expected_start_dispatch'],
                attempt_deadline_utc=context['attempt_deadline_utc'],now=C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc))
            self.assertEqual(helper['operation'],'STATUS')
            self.assertEqual(context['launch'],C.strict_json(launch_raw))

    def test_source_scalar_dispatch_capture_and_science_drift_are_refused(self):
        for mutate in (lambda s:s.update(launch_sha256='a'*64),lambda s:s.update(attempt_id='OTHER'),
                       lambda s:s.update(workflow_execution_identity=C.identity('aws_step_functions_standard_execution/v1','a'*64)),
                       lambda s:s['ssm_dispatch_transport2'].update(ssm_dispatch_request_sha256='0'*64),
                       lambda s:s['declared_exact_version_source_get_captures_in_order'].reverse(),
                       lambda s:s['declared_exact_version_source_get_captures_in_order'][0]['operation_capture_preimage'].update(key='wrong'),
                       lambda s:s['zero_science_counters'].update(trajectory_count=False),lambda s:s.update(extra=True)):
            args,launch_raw,source_raw=self.material();source=C.strict_json(source_raw);mutate(source)
            with self.assertRaises(C.Refusal):C.validate_helper_local_source_context(args,launch_raw,C.canonical_bytes(source))
        args,launch_raw,source_raw=self.material();launch=C.strict_json(launch_raw);launch['attempt_deadline_utc']='2026-09-06T18:55:00Z'
        with self.assertRaises(C.Refusal):C.validate_helper_local_source_context(args,C.canonical_bytes(reroot(launch)),source_raw)

    def test_loader_derives_only_exact_paths_and_refuses_start_before_file_access(self):
        args,launch_raw,source_raw=self.material()
        with mock.patch.object(C,'_read_bound_request_file',side_effect=[launch_raw,source_raw]) as reading:
            C.load_local_helper_context(args)
            self.assertEqual(reading.call_args_list,[mock.call(C.REQUESTS/(args.attempt_id+'.json')),mock.call(C.REQUESTS/(args.attempt_id+'.source.json'))])
        args,_,_=SsmDispatchInterfaceTests().material()
        with mock.patch.object(C,'_read_bound_request_file') as reading:
            with self.assertRaises(C.Refusal):C.load_local_helper_context(args)
            reading.assert_not_called()

    def test_rehashed_rechained_capture_still_binds_actual_get_operation_and_source(self):
        for changes in ({'operation':'S3_PUT_OBJECT'}, {'source_object_identity':C.identity('aws_c0_s3_object/v1','c'*64)},
                        {'request_envelope_sha256':'d'*64}, {'key':'wrong-key'}, {'observed_bytes':True},
                        {'operation_completed_utc':'2026-09-06T18:00:50.000000Z'}):
            args,launch_raw,source_raw=self.material();source=C.strict_json(source_raw)
            captures=source['declared_exact_version_source_get_captures_in_order']
            captures[0]['operation_capture_preimage'].update(changes)
            previous=None
            for item in captures:
                item['body_sha256']=C.digest(C.canonical_bytes(item['operation_capture_preimage']))
                item['previous_envelope_sha256']=previous;previous=C.digest(C.canonical_bytes(item))
            C.CaptureJournal.restore('EC2_INSTANCE_PROFILE_CONTROLLER',captures)
            with self.assertRaisesRegex(C.Refusal,'capture differs|capture chronology'):
                C.validate_helper_local_source_context(args,launch_raw,C.canonical_bytes(source))

    def test_private_request_reader_refuses_path_symlink_and_insecure_file(self):
        actual_fstat=os.fstat
        def root_owned(fd):
            fields=list(actual_fstat(fd));fields[4]=0
            return os.stat_result(fields)
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/'state';state.mkdir(mode=0o700);requests=state/'requests';requests.mkdir(mode=0o700)
            name='ATTEMPT-OFFLINE-SUCCESS.json';path=requests/name;path.write_bytes(b'{}');path.chmod(0o600)
            with mock.patch.object(C,'REQUESTS',requests),mock.patch.object(C.os,'geteuid',return_value=0),mock.patch.object(C.os,'fstat',side_effect=root_owned):
                self.assertEqual(C._read_bound_request_file(path),b'{}')
                with self.assertRaises(C.Refusal):C._read_bound_request_file(state/name)
                path.chmod(0o644)
                with self.assertRaises(C.Refusal):C._read_bound_request_file(path)
                path.unlink();path.symlink_to(state/'missing')
                with self.assertRaises(OSError):C._read_bound_request_file(path)


class LocalStatusActionTests(unittest.TestCase):
    def material(self):
        args,launch_raw,source_raw=LocalHelperSourceTests().material()
        context=C.validate_helper_local_source_context(args,launch_raw,source_raw)
        return args,context,C._decode_ssm_transport(args),launch_raw,source_raw

    def test_status_progress_requires_terminal_then_actual_handoff_flag(self):
        _,context,request,_,_=self.material();now=C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc)
        projection={k:context[k] for k in ('launch','workflow_execution_arn')}
        def response(value):return C.build_local_status_response(request,value,context=context,now=now)
        self.assertEqual(response(None)['state'],'WAITING_FOR_START')
        status=C.new_local_operational_status(**projection)
        for kind,expected in (('start','WAITING_FOR_HEARTBEAT'),('heartbeat','RUNNING'),('terminal','TERMINAL_AWAITING_JOURNAL_HANDOFF')):
            status=LocalOperationalStatusTests().advance(status,projection,kind)
            result=response(status);self.assertEqual(result['state'],expected)
            self.assertFalse(result['synthetic_outcome_claimed'])
        status['controller_journal_handoff_complete']=True
        result=response(status);self.assertEqual(result['state'],'CONTROLLER_HANDOFF_COMPLETE')
        self.assertLessEqual(len(C.canonical_bytes(result)),20000)
        self.assertEqual(result['authentication_disposition'],'LOCAL_OPERATIONAL_ONLY_NOT_AUTHENTICATED_EVIDENCE')

    def test_freshness_boundary_future_status_and_expired_helper_refused(self):
        _,context,request,_,_=self.material()
        projection={k:context[k] for k in ('launch','workflow_execution_arn')};status=C.new_local_operational_status(**projection)
        for kind in ('start','heartbeat'):status=LocalOperationalStatusTests().advance(status,projection,kind)
        for second,expected in ((119,'RUNNING'),(120,'HEARTBEAT_STALE')):
            now=C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc)+C.dt.timedelta(seconds=second)
            result=C.build_local_status_response(request,status,context=context,now=now)
            self.assertEqual(result['state'],expected);self.assertEqual(result['heartbeat_age_seconds'],second)
        for now in (C.dt.datetime(2026,9,6,18,1,59,tzinfo=C.dt.timezone.utc),C.dt.datetime(2026,9,6,18,40,tzinfo=C.dt.timezone.utc)):
            with self.assertRaises(C.Refusal):C.build_local_status_response(request,status,context=context,now=now)

    def test_actual_status_action_missing_cache_is_waiting_but_missing_source_or_unsafe_cache_refused(self):
        args,_,_,launch_raw,source_raw=self.material();now=C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc)
        with (mock.patch.object(C,'_read_bound_request_file',side_effect=[launch_raw,source_raw]),
              mock.patch.object(C,'read_local_operational_status',side_effect=FileNotFoundError),
              mock.patch.object(C,'_download',side_effect=AssertionError('no network')),
              mock.patch.object(C,'_run',side_effect=AssertionError('no command')),
              mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials'))):
            self.assertEqual(C.execute_local_status_helper(args,now=now)['state'],'WAITING_FOR_START')
        with mock.patch.object(C,'_read_bound_request_file',side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):C.execute_local_status_helper(args,now=now)
        with mock.patch.object(C,'_read_bound_request_file',side_effect=[launch_raw,source_raw]),mock.patch.object(C,'read_local_operational_status',side_effect=C.Refusal('unsafe')):
            with self.assertRaises(C.Refusal):C.execute_local_status_helper(args,now=now)

    def test_public_status_cli_dispatch_does_not_prepare_or_run_controller(self):
        args,_,_,launch_raw,source_raw=self.material();argv=['local-status-v1']
        for name in (*C.SEMANTIC21,*C.TRANSPORT2):
            attr='bucket' if name=='artifact_bucket' else name
            argv+=['--'+attr.replace('_','-'),str(getattr(args,attr))]
        parsed=C.parser().parse_args(argv);self.assertEqual(parsed.command,'local-status-v1')
        self.assertFalse(hasattr(parsed,'output'))
        original=C.execute_local_status_helper;output=io.BytesIO()
        with (mock.patch.object(C,'_read_bound_request_file',side_effect=[launch_raw,source_raw]),
              mock.patch.object(C,'read_local_operational_status',side_effect=FileNotFoundError),
              mock.patch.object(C,'execute_local_status_helper',side_effect=lambda a:original(a,now=C.dt.datetime(2026,9,6,18,2,tzinfo=C.dt.timezone.utc))),
              mock.patch.object(C.sys,'stdout',mock.Mock(buffer=output)),
              mock.patch.object(C,'prepare_request',side_effect=AssertionError('no preparation')),
              mock.patch.object(C,'run_attempt',side_effect=AssertionError('no worker'))):
            self.assertEqual(C.main(argv),0)
        raw=output.getvalue();self.assertTrue(raw.endswith(b'\n'))
        self.assertEqual(C.strict_json(raw[:-1])['state'],'WAITING_FOR_START')


class LocalSafeCloseActionTests(unittest.TestCase):
    def material(self):
        args,context,_,launch_raw,source_raw=LocalStatusActionTests().material()
        request=G.build_local_helper_transport_v1(ROOT,context['expected_start_dispatch'],'SAFE_CLOSE',context['attempt_deadline_utc'])
        args.ssm_dispatch_request_canonical_json_base64=request['transport_parameters']['SsmDispatchRequestCanonicalJsonBase64'][0]
        args.ssm_dispatch_request_sha256=request['transport_parameters']['SsmDispatchRequestSha256'][0]
        projection={k:context[k] for k in ('launch','workflow_execution_arn')}
        status=C.new_local_operational_status(**projection)
        for kind in ('start','heartbeat'):status=LocalOperationalStatusTests().advance(status,projection,kind)
        return args,context,request['helper_request'],status,launch_raw,source_raw

    def test_marker_requires_start_heartbeat_zero_and_never_claims_completed_close(self):
        _,context,request,status,_,_=self.material();now=C.dt.datetime(2026,9,6,18,3,tzinfo=C.dt.timezone.utc)
        marker=C.build_local_safe_close_marker(request,status,context=context,now=now)
        self.assertFalse(marker['safe_close_completed']);self.assertFalse(marker['synthetic_outcome_claimed'])
        self.assertEqual(marker['status_sha256'],C.digest(C.canonical_bytes(status)))
        for changes in ({'start':None},{'heartbeat_zero':None}):
            with self.assertRaises(C.Refusal):C.build_local_safe_close_marker(request,{**status,**changes},context=context,now=now)
        projection={k:context[k] for k in ('launch','workflow_execution_arn')}
        terminal=LocalOperationalStatusTests().advance(status,projection,'terminal')
        with self.assertRaises(C.Refusal):C.build_local_safe_close_marker(request,terminal,context=context,now=now)
        for now in (C.dt.datetime(2026,9,6,18,1,tzinfo=C.dt.timezone.utc),C.dt.datetime(2026,9,6,18,4,tzinfo=C.dt.timezone.utc),
                    C.dt.datetime(2026,9,6,18,40,tzinfo=C.dt.timezone.utc)):
            with self.assertRaises(C.Refusal):C.build_local_safe_close_marker(request,status,context=context,now=now)

    def test_exact_exclusive_private_marker_refuses_replay_and_symlink(self):
        args,context,request,status,_,_=self.material()
        marker=C.build_local_safe_close_marker(request,status,context=context,now=C.dt.datetime(2026,9,6,18,3,tzinfo=C.dt.timezone.utc))
        actual_fstat=os.fstat
        def root_owned(fd):
            fields=list(actual_fstat(fd));fields[4]=0
            return os.stat_result(fields)
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/'state';state.mkdir(mode=0o700);directory=state/'status';directory.mkdir(mode=0o700)
            with mock.patch.object(C,'STATUS',directory),mock.patch.object(C.os,'geteuid',return_value=0),mock.patch.object(C.os,'fstat',side_effect=root_owned):
                C._write_local_safe_close_marker(args.attempt_id,marker)
                path=directory/(args.attempt_id+'.safe-close.json');raw=path.read_bytes()
                self.assertEqual(raw,C.canonical_bytes(marker));self.assertEqual(path.stat().st_mode & 0o777,0o600)
                with self.assertRaises(FileExistsError):C._write_local_safe_close_marker(args.attempt_id,marker)
                self.assertEqual(path.read_bytes(),raw)
                path.unlink();target=state/'untouched';target.write_bytes(b'unchanged');path.symlink_to(target)
                with self.assertRaises(FileExistsError):C._write_local_safe_close_marker(args.attempt_id,marker)
                self.assertEqual(target.read_bytes(),b'unchanged')
                with self.assertRaises(C.Refusal):C._write_local_safe_close_marker('../escape',marker)

    def test_actual_safe_close_cli_only_writes_local_intent(self):
        args,_,_,status,launch_raw,source_raw=self.material();argv=['local-safe-close-v1']
        for name in (*C.SEMANTIC21,*C.TRANSPORT2):
            attr='bucket' if name=='artifact_bucket' else name
            argv+=['--'+attr.replace('_','-'),str(getattr(args,attr))]
        original=C.execute_local_safe_close_helper;output=io.BytesIO()
        with (mock.patch.object(C,'_read_bound_request_file',side_effect=[launch_raw,source_raw]),
              mock.patch.object(C,'read_local_operational_status',return_value=status),
              mock.patch.object(C,'execute_local_safe_close_helper',side_effect=lambda a:original(a,now=C.dt.datetime(2026,9,6,18,3,tzinfo=C.dt.timezone.utc))),
              mock.patch.object(C,'_write_local_safe_close_marker') as writing,
              mock.patch.object(C.sys,'stdout',mock.Mock(buffer=output)),
              mock.patch.object(C,'_run',side_effect=AssertionError('no command')),
              mock.patch.object(C,'_s3_put',side_effect=AssertionError('no S3')),
              mock.patch.object(C,'prepare_request',side_effect=AssertionError('no preparation')),
              mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials')),
              mock.patch.object(C,'run_attempt',side_effect=AssertionError('no worker'))):
            self.assertEqual(C.main(argv),0);self.assertEqual(writing.call_count,1)
        response=C.strict_json(output.getvalue()[:-1]);self.assertTrue(response['marker_written'])
        self.assertFalse(response['safe_close_completed']);self.assertLess(len(output.getvalue()),20000)


class LocalSsmRoutingTests(unittest.TestCase):
    def test_classifier_is_typed_and_has_no_filesystem_credential_or_command_effect(self):
        material=[('START',SsmDispatchInterfaceTests().material()[0]),
                  ('STATUS',LocalHelperSourceTests().material()[0]),('SAFE_CLOSE',LocalSafeCloseActionTests().material()[0])]
        with (mock.patch.object(C.os,'open',side_effect=AssertionError('no file')),
              mock.patch.object(C,'_run',side_effect=AssertionError('no command')),
              mock.patch.object(C,'bootstrap_imdsv2_credentials',side_effect=AssertionError('no credentials')),
              mock.patch.object(C,'prepare_request',side_effect=AssertionError('no prepare'))):
            for expected,args in material:self.assertEqual(C.classify_local_dispatch(args),expected)
            args=copy.deepcopy(material[1][1]);record=C._decode_ssm_transport(args);record['operation']='SCIENCE'
            raw=C.canonical_bytes(record);args.ssm_dispatch_request_canonical_json_base64=base64.b64encode(raw).decode();args.ssm_dispatch_request_sha256=C.digest(raw)
            with self.assertRaises(C.Refusal):C.classify_local_dispatch(args)
            args=copy.deepcopy(material[1][1]);args.launch_bytes+=1
            with self.assertRaises(C.Refusal):C.classify_local_dispatch(args)

    def test_document_helpers_exit_before_any_preparation_or_service_start(self):
        document=load('aws/c0/ssm/EBU-C0-Start-v1.yaml')
        self.assertEqual(document,load('aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml')['Resources']['EBUC0StartDocument']['Properties']['Content'])
        self.assertEqual(len(document['parameters']),23)
        lines=document['mainSteps'][0]['inputs']['runCommand']
        begin=lines.index('case "$dispatch_operation" in');end=lines.index('esac',begin)
        self.assertLess(end,next(i for i,line in enumerate(lines) if '/usr/bin/install -d' in line))
        self.assertLess(end,next(i for i,line in enumerate(lines) if ' prepare-request-v4 ' in line))
        self.assertEqual(sum('/usr/bin/systemctl start --no-block' in line for line in lines),1)
        self.assertTrue(lines[begin-1].startswith('dispatch_operation="$(/usr/bin/python3 '))
        self.assertIn(' classify-dispatch-v1 ',lines[begin-1])
        routed=lines[begin:end+1]
        # Exercise only the literal case/exit structure with side-effect-free
        # printf stand-ins, never the SSM document or controller runtime.
        modeled=[]
        for line in routed:
            if line.startswith(('STATUS) ','SAFE_CLOSE) ')):
                start=line.index('/usr/bin/python3 ');stop=line.index('; exit 0 ;;',start)
                operation=line.split(')',1)[0]
                line=line[:start]+"printf '%s\\n' "+operation+line[stop:]
            modeled.append(line)
        script='\n'.join(['set -eu','dispatch_operation="$OFFLINE_OPERATION"',*modeled,"printf '%s\\n' START_PATH"])
        for operation,code,wanted in (('STATUS',0,b'STATUS\n'),('SAFE_CLOSE',0,b'SAFE_CLOSE\n'),('START',0,b'START_PATH\n'),('UNKNOWN',64,b'')):
            result=C.subprocess.run(['/bin/sh','-c',script],env={'OFFLINE_OPERATION':operation},capture_output=True,timeout=5)
            self.assertEqual((result.returncode,result.stdout),(code,wanted))
        for operation in ('STATUS','SAFE_CLOSE'):
            failed=script.replace("printf '%s\\n' "+operation+';','false;')
            result=C.subprocess.run(['/bin/sh','-c',failed],env={'OFFLINE_OPERATION':operation},capture_output=True,timeout=5)
            self.assertEqual((result.returncode,result.stdout),(1,b''))
        failed=script.replace('dispatch_operation="$OFFLINE_OPERATION"','dispatch_operation="$(exit 23)"')
        result=C.subprocess.run(['/bin/sh','-c',failed],capture_output=True,timeout=5)
        self.assertEqual((result.returncode,result.stdout),(23,b''))

    def test_classifier_cli_reuses_all_explicit_semantics_and_transport(self):
        args=LocalHelperSourceTests().material()[0];argv=['classify-dispatch-v1']
        for name in (*C.SEMANTIC21,*C.TRANSPORT2):
            attr='bucket' if name=='artifact_bucket' else name
            argv+=['--'+attr.replace('_','-'),str(getattr(args,attr))]
        output=io.StringIO()
        with mock.patch.object(C.sys,'stdout',output):self.assertEqual(C.main(argv),0)
        self.assertEqual(output.getvalue(),'STATUS\n')


class LocalOperationalStatusTests(unittest.TestCase):
    def material(self):
        launch=current_launch(load('aws/c0/fixtures/launch-request.valid.json'))
        workflow='arn:aws:states:us-east-1:623609441658:execution:EBU-C0-492a4f1:'+launch['attempt_id']
        context={'launch':launch,'workflow_execution_arn':workflow}
        return C.new_local_operational_status(**context),context

    def publication(self,status,context,kind,**changes):
        common={'attempt_identity':status['attempt_identity'],'observed_utc':'2026-09-06T18:02:00Z'}
        if kind=='start':
            schema='aws_c0_start_receipt/v7'
            common.update(start_disposition='AWS_C0_START_ACCEPTED',failure_phase=None,failure_code=None,
                workflow_execution_identity=status['workflow_execution_identity'],workflow_execution_arn=context['workflow_execution_arn'],
                launch_request_identity=status['launch_request_identity'])
        elif kind=='heartbeat':
            schema='aws_c0_heartbeat/v1';last=status['latest_heartbeat']
            common.update(sequence=0 if last is None else last['sequence']+1,
                          previous_heartbeat_identity=None if last is None else last['identity'])
        else:
            schema='aws_c0_terminal_receipt/v1'
            common.update(last_heartbeat_sequence=status['latest_heartbeat']['sequence'],disposition='AWS_C0_SYNTHETIC_PASS')
        common.update(changes)
        record,raw,rid=C._root_record(schema,common)
        receipt={'key':status['artifact_prefix']+'evidence/'+kind+'-'+rid+'.json','version_id':'offline-exact-version',
                 'bytes':len(raw),'sha256':C.digest(raw),'checksum_sha256_base64':base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        return raw,receipt

    def advance(self,status,context,kind,**changes):
        return C.advance_local_operational_status(status,*self.publication(status,context,kind,**changes),**context)

    def test_published_start_heartbeat_zero_chain_and_terminal_bindings(self):
        status,context=self.material()
        status=self.advance(status,context,'start')
        status=self.advance(status,context,'heartbeat');zero=copy.deepcopy(status['heartbeat_zero'])
        status=self.advance(status,context,'heartbeat',observed_utc='2026-09-06T18:02:30Z')
        self.assertEqual(status['heartbeat_zero'],zero)
        self.assertEqual(status['latest_heartbeat']['sequence'],1)
        self.assertNotEqual(status['start']['identity']['sha256'],status['start']['object']['sha256'])
        status=self.advance(status,context,'terminal',observed_utc='2026-09-06T18:03:00Z')
        self.assertFalse(status['controller_journal_handoff_complete'])
        status['controller_journal_handoff_complete']=True
        self.assertEqual(C.validate_local_operational_status(status,**context),status)
        self.assertLess(len(C.canonical_bytes(status)),16384)

    def test_missing_replayed_or_out_of_order_roots_are_refused(self):
        status,context=self.material()
        with self.assertRaises(C.Refusal):self.advance(status,context,'heartbeat')
        status=self.advance(status,context,'start')
        with self.assertRaises(C.Refusal):self.advance(status,context,'start')
        with self.assertRaises(C.Refusal):self.advance(status,context,'heartbeat',sequence=1)
        status=self.advance(status,context,'heartbeat')
        for changes in ({'sequence':0},{'sequence':2},{'sequence':True},{'previous_heartbeat_identity':None},
                        {'observed_utc':'2026-09-06T18:01:00Z'}):
            with self.assertRaises(C.Refusal):self.advance(status,context,'heartbeat',**changes)
        with self.assertRaises(C.Refusal):self.advance(status,context,'terminal',last_heartbeat_sequence=2)
        status=self.advance(status,context,'heartbeat',observed_utc='2026-09-06T18:04:00Z')
        with self.assertRaises(C.Refusal):self.advance(status,context,'heartbeat',observed_utc='2026-09-06T18:03:00Z')
        spliced=copy.deepcopy(status)
        spliced['latest_heartbeat']=copy.deepcopy(spliced['heartbeat_zero'])
        spliced['latest_heartbeat']['sequence']=1
        with self.assertRaises(C.Refusal):C.validate_local_operational_status(spliced,**context)

    def test_wrong_publication_bytes_version_and_attempt_are_refused(self):
        status,context=self.material();raw,receipt=self.publication(status,context,'start')
        with self.assertRaises(C.Refusal):C.advance_local_operational_status(status,raw,None,**context)
        with self.assertRaises(C.Refusal):C.advance_local_operational_status(status,b'[]',receipt,**context)
        for field,value in (('key','different'),('sha256','b'*64),('bytes',1),('version_id',''),('checksum_sha256_base64','bad')):
            with self.assertRaises(C.Refusal):C.advance_local_operational_status(status,raw,{**receipt,field:value},**context)
        for changes in ({'attempt_identity':C.identity('aws_c0_attempt/v1','b'*64)},
                        {'scientific_execution_authorized':True},{'zero_science_counters':{**C.ZERO,'trajectory_count':False}}):
            with self.assertRaises(C.Refusal):self.advance(status,context,'start',**changes)

    def test_local_cache_cannot_change_workflow_or_claim_early_handoff(self):
        status,context=self.material()
        for changes in ({'workflow_execution_arn':'other'},{'attempt_id':'OTHER'},
                        {'controller_journal_handoff_complete':True},{'extra':True},
                        {'zero_science_counters':{**C.ZERO,'trajectory_count':False}}):
            with self.assertRaises(C.Refusal):C.validate_local_operational_status({**status,**changes},**context)

    def test_producer_is_wired_after_successful_put_and_after_journal_handoff(self):
        source=(ROOT/'aws/c0/controller/ebu_c0_controller.py').read_text()
        run=ast.get_source_segment(source,next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='run_attempt'))
        self.assertLess(run.index('start_publication = put('),run.index('operational_status = advance_local_operational_status('))
        self.assertLess(run.index('root_publication = put('),run.index('advance_local_operational_status(operational_status,raw,root_publication'))
        self.assertLess(run.index('publish_controller_journal_handoff('),run.index("operational_status['controller_journal_handoff_complete'] = True"))
        self.assertNotIn('aws_c0_controller_status/v1',run)

    def test_status_storage_survives_runtime_directory_removal(self):
        service=(ROOT/'aws/c0/controller/ebu-c0@.service').read_text()
        self.assertIn('StateDirectory=ebu-c0\n',service)
        self.assertIn('StateDirectoryMode=0700\n',service)
        self.assertEqual(C.STATUS,Path('/var/lib/ebu-c0/status'))
        actual_fstat=os.fstat
        def root_owned(fd):
            # Offline filesystem model only; never run the service or use root.
            fields=list(actual_fstat(fd));fields[4]=0
            return os.stat_result(fields)
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);state=base/'state';state.mkdir(mode=0o700)
            runtime=base/'run';runtime.mkdir(mode=0o700)
            with mock.patch.object(C,'STATUS',state/'status'),mock.patch.object(C.os,'geteuid',return_value=0),mock.patch.object(C.os,'fstat',side_effect=root_owned):
                status,context=self.material()
                for kind in ('start','heartbeat','terminal'):status=self.advance(status,context,kind)
                status['controller_journal_handoff_complete']=True
                destination=C.STATUS/(status['attempt_id']+'.json')
                C._publish_status(destination,status)
                runtime.rmdir()  # Model systemd's RuntimeDirectory cleanup.
                self.assertEqual(C.strict_json(destination.read_bytes()),status)
                self.assertEqual(C.read_local_operational_status(**context),status)
                self.assertEqual(destination.stat().st_mode & 0o777,0o600)
                self.assertEqual(list(C.STATUS.iterdir()),[destination])
                with self.assertRaises(C.Refusal):C._publish_status(state/'wrong.json',status)
                C.STATUS.chmod(0o777)
                with self.assertRaises(C.Refusal):C._publish_status(destination,status)
                C.STATUS.chmod(0o700)

    def test_status_directory_refuses_nonroot_owner_mode_and_symlink(self):
        actual_fstat=os.fstat
        def fake_owner(fd,uid=0):
            fields=list(actual_fstat(fd));fields[4]=uid
            return os.stat_result(fields)
        with mock.patch.object(C.os,'geteuid',return_value=501),mock.patch.object(C.os,'open') as opening:
            with self.assertRaises(C.Refusal):C._status_directory_fd(create=True)
            opening.assert_not_called()
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);state=base/'state';state.mkdir(mode=0o700)
            target=base/'target';target.mkdir(mode=0o700)
            with mock.patch.object(C,'STATUS',state/'status'),mock.patch.object(C.os,'geteuid',return_value=0):
                with mock.patch.object(C.os,'fstat',side_effect=lambda fd:fake_owner(fd,501)):
                    with self.assertRaises(C.Refusal):C._status_directory_fd(create=True)
                with mock.patch.object(C.os,'fstat',side_effect=fake_owner):
                    state.chmod(0o755)
                    with self.assertRaises(C.Refusal):C._status_directory_fd(create=True)
                    state.chmod(0o700);C.STATUS.symlink_to(target,target_is_directory=True)
                    with self.assertRaises(OSError):C._status_directory_fd(create=True)
                    self.assertEqual(list(target.iterdir()),[])


class LocalOperationalReadTests(unittest.TestCase):
    def test_reader_refuses_missing_unsafe_and_nonregular_status(self):
        actual_fstat=os.fstat
        def root_owned(fd):
            fields=list(actual_fstat(fd));fields[4]=0
            return os.stat_result(fields)
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/'state';state.mkdir(mode=0o700)
            with mock.patch.object(C,'STATUS',state/'status'),mock.patch.object(C.os,'geteuid',return_value=0),mock.patch.object(C.os,'fstat',side_effect=root_owned):
                fixture=LocalOperationalStatusTests();status,context=fixture.material()
                with self.assertRaises(FileNotFoundError):C.read_local_operational_status(**context)
                self.assertFalse(C.STATUS.exists())  # The reader cannot create status.
                destination=C.STATUS/(status['attempt_id']+'.json')
                C._publish_status(destination,status)
                self.assertFalse(C.read_local_operational_status(**context)['controller_journal_handoff_complete'])
                destination.chmod(0o644)
                with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)
                destination.chmod(0o600);linked=C.STATUS/'second-link';os.link(destination,linked)
                with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)
                linked.unlink();destination.unlink()
                destination.symlink_to(state/'nonexistent')
                with self.assertRaises(OSError):C.read_local_operational_status(**context)
                destination.unlink();os.mkfifo(destination,0o600)
                with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)
                destination.unlink();destination.mkdir(mode=0o700)
                with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)

    def test_reader_checks_complete_bytes_bindings_and_concurrent_changes(self):
        actual_fstat=os.fstat
        reads=0;change=False;wrong_owner=False
        def observed(fd):
            nonlocal reads
            actual=actual_fstat(fd);fields=list(actual);fields[4]=0
            if C.stat.S_ISREG(actual.st_mode):
                reads+=1
                if wrong_owner:fields[4]=501
                if change and reads%2==0:fields[6]+=1
            return os.stat_result(fields)
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/'state';state.mkdir(mode=0o700)
            with mock.patch.object(C,'STATUS',state/'status'),mock.patch.object(C.os,'geteuid',return_value=0),mock.patch.object(C.os,'fstat',side_effect=observed):
                fixture=LocalOperationalStatusTests();status,context=fixture.material()
                destination=C.STATUS/(status['attempt_id']+'.json')
                C._publish_status(destination,status)
                change=True
                with self.assertRaisesRegex(C.Refusal,'changed during'):C.read_local_operational_status(**context)
                change=False;wrong_owner=True
                with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)
                wrong_owner=False
                for raw in (b'',b' '*16385,b'{}\n',C.canonical_bytes({**status,'attempt_id':'OTHER'})):
                    destination.write_bytes(raw)
                    with self.assertRaises(C.Refusal):C.read_local_operational_status(**context)


class JournalSourceContractDiagnosticTests(unittest.TestCase):
    def material(self):
        schema=load('aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json')
        return ((ROOT/'aws/c0/finalizer/finalizer.py').read_bytes(),
                (ROOT/'aws/c0/state-machine/aws-c0.asl.json').read_bytes(),
                schema['$defs']['journal_capture_source_structure_proof_preimage'])

    def test_exact_current_source_refutes_frozen_zero_s3_obligations(self):
        source,asl,schema=self.material()
        result=V.inspect_journal_zero_s3_obligations(source,asl,schema)
        self.assertEqual(result['disposition'],'REFUSE_CONCRETE_COUNTEREXAMPLE')
        self.assertEqual(result['source_raw_sha256'],hashlib.sha256(source).hexdigest())
        self.assertEqual(result['asl_raw_sha256'],hashlib.sha256(asl).hexdigest())
        self.assertEqual(result['parser_version'],'.'.join(map(str,sys.version_info[:3])))
        self.assertFalse(result['complete_callgraph_claimed']);self.assertFalse(result['readiness_claimed'])
        rows={r['helper_branch_id']:r for r in result['findings']}
        self.assertEqual([r['required_pointer_exists'] for r in rows.values()],[False]*4)
        for branch in ('PREFLIGHT_FAILURE','POLL','SAFE_CLOSE'):
            self.assertTrue(rows[branch]['literal_s3_call_path_counterexamples'])
        self.assertIsNone(rows['SSM_COMPLETION']['resolved_literal_handler'])

    def test_state_aliases_do_not_fix_s3_calls(self):
        source,asl,schema=self.material();workflow=json.loads(asl)
        for row in V.inspect_journal_zero_s3_obligations(source,asl,schema)['findings']:
            workflow['States'][row['required_source_pointer'].split('/')[-1]]={'Type':'Pass','End':True}
        result=V.inspect_journal_zero_s3_obligations(source,F.canonical_bytes(workflow),schema)
        self.assertTrue(all(r['required_pointer_exists'] for r in result['findings']))
        self.assertEqual(result['disposition'],'REFUSE_CONCRETE_COUNTEREXAMPLE')

    def test_no_counterexample_never_becomes_a_complete_proof(self):
        _,_,schema=self.material()
        workflow={'States':{row['properties']['source_json_pointer']['const'].split('/')[-1]:{'Type':'Pass','End':True}
            for row in schema['allOf'][1]['then']['properties']['zero_s3_helpers_in_order']['prefixItems']}}
        result=V.inspect_journal_zero_s3_obligations(b'def unused():\n    return None\n',F.canonical_bytes(workflow),schema)
        self.assertEqual(result['disposition'],'INCOMPLETE_NOT_A_PROOF')

    def test_unused_nested_call_is_not_an_executed_edge(self):
        _,_,schema=self.material()
        source=b'''def preflight_failure(event):
    def unused():
        return _aws_request('s3', 'GET')
    return None
def lambda_handler(event, context):
    action=event['action']
    if action == 'preflight_failure': return preflight_failure(event)
'''
        result=V.inspect_journal_zero_s3_obligations(source,b'{"States":{}}',schema)
        self.assertFalse(result['findings'][0]['literal_s3_call_path_counterexamples'])


class ByteBoundStagingTests(unittest.TestCase):
    def material(self):
        plan = S.plan('a' * 40, b'controller\n', b'unit\n')
        receipts = [{k: obj[k] for k in ['role', 'key', 'sha256', 'bytes', 'checksum_sha256_base64']}
                    for obj in plan['objects']]
        for i, receipt in enumerate(receipts):
            receipt.update(bucket=S.BUCKET, version_id='observed-version-' + str(i), etag='"etag"', request_id='request-id')
        return plan, receipts

    def test_plan_has_no_guessed_aws_version_and_preserves_verified_archive(self):
        p, _ = self.material()
        self.assertEqual(S.validate_plan(p, b'controller\n', b'unit\n'), p)
        self.assertEqual(p['objects'][2]['sha256'], S.ARCHIVE_SHA)
        self.assertEqual(p['objects'][2]['bytes'], 414462464)
        self.assertNotIn('version_id', S.canonical(p).decode())
        for bad in (b'controller\r\n', b'', 'not bytes'):
            with self.assertRaises(ValueError): S.plan('a' * 40, bad, b'unit\n')

    def test_document_is_closed_fixed_and_cannot_execute_a_container_or_service(self):
        p, receipts = self.material()
        d = S.document(p, receipts, b'controller\n', b'unit\n')
        self.assertEqual(d['parameters'], {})
        self.assertEqual(len(d['mainSteps']), 1)
        self.assertEqual(d['mainSteps'][0]['inputs']['timeoutSeconds'], '360')
        body = d['mainSteps'][0]['inputs']['runCommand'][0]
        self.assertNotIn('{{', body)
        for forbidden in ('shell=True', "'docker','run'", "'systemctl','start'", "'systemctl','enable'", 'pip install', 'apt-get', "'pull'"):
            self.assertNotIn(forbidden, body)
        self.assertIn("'--version-id'", body)
        self.assertIn('os.O_EXCL|os.O_NOFOLLOW', body)
        self.assertIn("'image','load'", body)
        compile(S.HOST_BODY, '<nonexecuted-staging-body>', 'exec')

    def test_each_staging_receipt_is_exact_and_closed(self):
        p, original = self.material()
        for field, bad in [('version_id', 'null'), ('bucket', 'other-bucket'), ('key', 'other-key'),
                           ('sha256', '0' * 64), ('bytes', 0), ('request_id', ''), ('extra', True)]:
            receipts = copy.deepcopy(original); receipts[0][field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError): S.validate_receipts(p, receipts)
        with self.assertRaises(ValueError): S.validate_receipts(p, original[::-1])

    def test_material_or_destination_changes_refuse(self):
        p, receipts = self.material()
        for field, bad in [('instance_id', 'i-other'), ('maximum_staging_commands', 2), ('container_execution', True)]:
            changed = copy.deepcopy(p); changed[field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError): S.document(changed, receipts, b'controller\n', b'unit\n')
        p['objects'][0]['destination'] = '/etc/passwd'
        with self.assertRaises(ValueError): S.document(p, receipts, b'controller\n', b'unit\n')

    def test_staging_permission_is_expiring_and_has_only_exact_targets(self):
        p = S.temporary_policy('AROAAAAAAAAAAAAAAAAAA', '2026-09-06T15:00:00Z', '2026-09-06T16:00:00Z')
        self.assertNotIn('*', S.canonical(p).decode())
        for s in p['Statement']:
            self.assertEqual(s['Condition']['StringEquals']['aws:SourceIdentity'], 'konrad')
            self.assertTrue(s['Condition']['StringEquals']['aws:userid'].endswith(':' + S.SESSION))
        with self.assertRaises(ValueError): S.temporary_policy('AROAAAAAAAAAAAAAAAAAA', '2026-09-06T15:00:00Z', '2026-09-06T17:00:01Z')

    def test_instance_read_policy_binds_each_exact_object_to_its_own_version(self):
        p, receipts = self.material()
        policy = S.instance_read_policy(p, receipts, b'controller\n', b'unit\n',
                                       '2026-09-06T15:00:00Z', '2026-09-06T16:00:00Z')
        self.assertEqual(len(policy['Statement']), 3)
        self.assertNotIn('*', json.dumps(policy))
        for statement, receipt in zip(policy['Statement'], receipts):
            self.assertEqual(set(statement), {'Sid', 'Effect', 'Action', 'Resource', 'Condition'})
            self.assertEqual(statement['Effect'], 'Allow')
            self.assertEqual(statement['Action'], 's3:GetObjectVersion')
            self.assertEqual(statement['Resource'], 'arn:aws:s3:::' + S.BUCKET + '/' + receipt['key'])
            self.assertEqual(statement['Condition'], {
                'StringEquals': {'s3:VersionId': receipt['version_id'], 's3:ResourceAccount': S.ACCOUNT},
                'Bool': {'aws:SecureTransport': 'true'},
                'DateLessThan': {'aws:CurrentTime': '2026-09-06T16:00:00Z'}})
        # No statement admits another object's version: avoid a cross-product grant.
        for i, receipt in enumerate(receipts):
            for j, other in enumerate(receipts):
                matching = [s for s in policy['Statement']
                            if s['Resource'].endswith('/' + receipt['key'])
                            and s['Condition']['StringEquals']['s3:VersionId'] == other['version_id']]
                self.assertEqual(len(matching), int(i == j))

    def test_instance_read_policy_refuses_unbound_material_or_unobserved_versions(self):
        p, receipts = self.material()
        for field, bad in [('version_id', 'null'), ('version_id', '*'), ('key', 'other/key'),
                           ('bucket', 'other-bucket'), ('sha256', '0' * 64), ('request_id', '')]:
            changed = copy.deepcopy(receipts); changed[0][field] = bad
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                S.instance_read_policy(p, changed, b'controller\n', b'unit\n',
                                       '2026-09-06T15:00:00Z', '2026-09-06T16:00:00Z')
        with self.assertRaises(ValueError):
            S.instance_read_policy(p, receipts, b'other\n', b'unit\n',
                                   '2026-09-06T15:00:00Z', '2026-09-06T16:00:00Z')

    def test_instance_read_policy_refuses_unbounded_or_noncanonical_expiry(self):
        p, receipts = self.material()
        for expiry in ['2026-09-06T16:00:01Z', '2026-09-06T15:00:00Z', '2026-09-06T14:59:59Z',
                       '2026-9-6T16:00:00Z', '2026-09-06T16:00:00+00:00', None]:
            with self.subTest(expiry=expiry), self.assertRaises(ValueError):
                S.instance_read_policy(p, receipts, b'controller\n', b'unit\n',
                                       '2026-09-06T15:00:00Z', expiry)


class ImageManifestBindingTests(unittest.TestCase):
    def verify(self, inspection):
        reference = 'ebu-aws-c0@sha256:' + '1' * 64
        contract = {
            'controller_identity': C.identity('aws_c0_controller_software/v1', C.digest(b'controller')),
            'service_identity': C.identity('aws_c0_service_unit/v1', C.digest(b'service')),
            'container_runtime_policy_identity': C.identity('aws_c0_container_runtime_policy/v1', C.digest(C.canonical_bytes(C.RUNTIME_POLICY))),
            'image_reference': reference, 'image_identity': C.identity('oci_image_digest/v1', '1' * 64),
        }
        with mock.patch.object(C, '_software_contract', return_value=contract), \
             mock.patch.object(C, '_file_secure', side_effect=[b'controller', b'service']), \
             mock.patch.object(C, '_run', return_value=mock.Mock(stdout=json.dumps(inspection).encode())) as command:
            result = C._verify_software({})
            command.assert_called_once_with([C.DOCKER, 'image', 'inspect', reference], 30)
            return result

    def inspection(self):
        return [{'Id': 'sha256:' + '2' * 64, 'RepoDigests': ['ebu-aws-c0@sha256:' + '1' * 64],
                 'Os': 'linux', 'Architecture': 'amd64'}]

    def test_manifest_and_configuration_digests_must_be_distinguished(self):
        self.assertEqual(self.verify(self.inspection())['image_identity']['sha256'], '1' * 64)

    def test_matching_configuration_id_cannot_replace_repository_digest(self):
        value = self.inspection(); value[0]['Id'] = 'sha256:' + '1' * 64
        for references in ([], None, ['other@sha256:' + '1' * 64], ['ebu-aws-c0@sha256:' + '3' * 64]):
            value[0]['RepoDigests'] = references
            with self.subTest(references=references), self.assertRaises(C.Refusal): self.verify(value)

    def test_local_image_configuration_and_platform_are_closed(self):
        for field, bad in [('Id', 'mutable-tag'), ('Os', 'windows'), ('Architecture', 'arm64')]:
            value = self.inspection(); value[0][field] = bad
            with self.subTest(field=field), self.assertRaises(C.Refusal): self.verify(value)

    def test_image_inspection_must_be_singular(self):
        for value in ([], self.inspection() * 2, {}, [None]):
            with self.subTest(value=value), self.assertRaises(C.Refusal): self.verify(value)


class BootstrapTransportTests(unittest.TestCase):
    def plan(self):
        return B.plan('AROAAAAAAAAAAAAAAAAAA', '2026-09-06T16:00:00Z', '2026-09-06T15:00:00Z')

    def test_exact_material_and_no_user_command_parameters(self):
        p = self.plan()
        self.assertEqual(B.validate_plan(p), p)
        self.assertEqual(p['document']['parameters'], {})
        self.assertEqual(p['document']['mainSteps'][0]['inputs']['timeoutSeconds'], '60')
        compile(B.PROBE, '<nonexecuted-bootstrap-probe>', 'exec')
        self.assertNotIn('shell=True', B.PROBE)
        self.assertNotIn('{{', B.PROBE)
        for forbidden in ('docker load', 'docker run', 'systemctl start', 'aws s3', 'pip install'):
            self.assertNotIn(forbidden, B.PROBE)

    def test_policy_has_only_exact_document_instance_and_preparation_context(self):
        statements = self.plan()['temporary_policy']['Statement']
        self.assertEqual(statements[0]['Resource'], B.DOCUMENT_ARN)
        self.assertEqual(statements[1]['Resource'], [B.DOCUMENT_ARN, B.INSTANCE_ARN])
        for row in statements:
            self.assertEqual(row['Condition']['StringEquals']['aws:SourceIdentity'], 'konrad')
            self.assertTrue(row['Condition']['StringEquals']['aws:userid'].endswith(':'+B.SESSION))
            self.assertNotIn('*', B.canonical(row).decode())

    def test_expired_or_overlong_policy_refused(self):
        for expiry in ('2026-09-06T15:00:00Z', '2026-09-06T17:00:01Z'):
            with self.assertRaises(ValueError):
                B.policy('AROAAAAAAAAAAAAAAAAAA', expiry, '2026-09-06T15:00:00Z')

    def test_modified_document_policy_target_or_bounds_refused(self):
        for key, value in [('instance_id','i-other'), ('maximum_send_commands',2),
                           ('aggregate_cost_ceiling_minor_units',5001), ('scientific_execution',True)]:
            p=self.plan(); p[key]=value
            with self.assertRaises(ValueError):
                B.validate_plan(p)
        p=self.plan(); p['document']['parameters']['Commands']={}
        with self.assertRaises(ValueError):
            B.validate_plan(p)
        p=self.plan(); p['temporary_policy']['Statement'][1]['Resource']=['*']
        with self.assertRaises(ValueError):
            B.validate_plan(p)

    def test_dispatch_exact_version_hash_single_instance(self):
        p=self.plan(); request=B.dispatch_request(p)
        self.assertEqual(request['DocumentName'], B.DOCUMENT)
        self.assertNotEqual(request['DocumentName'], 'EBU-C0-Start-v1')
        self.assertEqual(request['DocumentVersion'], '1')
        self.assertEqual(request['DocumentHash'], B.digest(p['document']))
        self.assertEqual(request['InstanceIds'], [B.INSTANCE])
        self.assertEqual(request['Parameters'], {})
        self.assertTrue(p['instance_start_requires_separate_fresh_bound'])


class PricingCollectorTests(unittest.TestCase):
    """Synthetic API responses exercise transport-independent proof replay."""
    def pages(self, source_unit="Hrs", prices=("0.0208000000",), tokens=None):
        request = P.request_for("AmazonEC2", {"regionCode": "us-east-1"})
        responses = []
        for index, price in enumerate(prices):
            sku = f"SYNTHETIC-SKU-{index}"
            rate_code = sku + ".TERM.RATE"
            product = {"product": {"sku": sku, "attributes": {"regionCode": "us-east-1"}},
                       "serviceCode": "AmazonEC2", "version": "SYNTHETIC-TEST",
                       "publicationDate": "2026-09-01T00:00:00Z", "terms": {"OnDemand": {
                           sku + ".TERM": {"sku": sku, "effectiveDate": "2026-09-01T00:00:00Z",
                           "priceDimensions": {rate_code: {"rateCode": rate_code, "unit": source_unit,
                             "beginRange": "0", "endRange": "Inf", "appliesTo": [],
                             "pricePerUnit": {"USD": price}}}}}}}
            body = {"FormatVersion": "aws_v1", "PriceList": [P.canonical(product).decode()]}
            if tokens is not None and tokens[index] is not None:
                body["NextToken"] = tokens[index]
            responses.append(body)
        iterator = iter(responses)
        def fetch(request):
            body = next(iterator)
            return body, P.canonical(body), "synthetic-request-id"
        self.saved = []
        with mock.patch.object(P, 'now', return_value="2026-09-04T22:00:00Z"):
            return P.collect_pages(fetch, request, P.identity("aws_c0_constrained_operator_session/v1", {}), self.saved.append)

    def row(self, dimension="instance_running_seconds", unit="SECOND", source_unit="Hrs"):
        fraction = P.CONVERSIONS[unit][source_unit]
        return P.rate_row(dimension, unit, self.pages(source_unit),
                          {source_unit: [fraction.numerator, fraction.denominator]},
                          "2026-09-04T22:00:00Z", "2026-09-04T23:00:00Z")

    def test_receipts_paginate_and_replay_every_page(self):
        pages = self.pages(prices=("0.0208", "0.04"), tokens=("next", None))
        self.assertEqual(pages[1]['request']['NextToken'], 'next')
        self.assertEqual(len(P.validate_pages(pages)), 2)
        row = P.rate_row('instance_running_seconds', 'SECOND', pages, {'Hrs': [1, 36]},
                         '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z')
        self.assertEqual((row['numerator_minor_units'], row['denominator_units']), (1, 900))
        self.assertEqual(len(row['pricing_observations']), 2)

    def test_truncated_repeated_and_altered_pages_refused(self):
        pages = self.pages(prices=("0.02", "0.03"), tokens=("next", None))
        with self.assertRaisesRegex(P.Refusal, 'terminal'):
            P.validate_pages(pages[:1])
        pages[0]['response']['PriceList'] = []
        with self.assertRaisesRegex(P.Refusal, 'receipt mismatch'):
            P.validate_pages(pages)
        with self.assertRaisesRegex(P.Refusal, 'repeated'):
            self.pages(prices=("0.02", "0.03"), tokens=("next", "next"))
        self.assertEqual(len(self.saved), 2)

    def test_empty_page_missing_request_id_and_wrong_filters_refused(self):
        with self.assertRaisesRegex(P.Refusal, 'request id'):
            P.collect_pages(lambda r: ({}, b'{}', ''), {}, P.identity('test/v1', {}), lambda p: None)
        pages = self.pages()
        pages[0]['request']['Filters'][0]['Value'] = 'eu-west-1'
        pages[0]['receipt']['request_sha256'] = P.digest(P.canonical(pages[0]['request']))
        with self.assertRaisesRegex(P.Refusal, 'violates filter'):
            P.validate_pages(pages)

    def test_units_decimal_and_tier_coverage_refused(self):
        pages = self.pages()
        with self.assertRaisesRegex(P.Refusal, 'unit conversion'):
            P.rate_row('instance_running_seconds', 'SECOND', pages, {'Hrs': [1, 360000]},
                       '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z')
        for price in ('NaN', '-1', '1e-6'):
            with self.assertRaises(P.Refusal):
                P.decimal_parts(price)
        body = pages[0]['response']
        product = P.strict(body['PriceList'][0])
        next(iter(next(iter(product['terms']['OnDemand'].values()))['priceDimensions'].values()))['beginRange'] = '1'
        body['PriceList'] = [P.canonical(product).decode()]
        raw = P.canonical(body)
        pages[0]['wire_response_base64'] = base64.b64encode(raw).decode()
        pages[0]['wire_response_sha256'] = P.digest(raw)
        pages[0]['receipt']['response_sha256'] = P.digest(raw)
        with self.assertRaisesRegex(P.Refusal, 'tier gap'):
            P.rate_row('instance_running_seconds', 'SECOND', pages, {'Hrs': [1, 36]},
                       '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z')

    def test_schema_valid_22_row_model_and_runtime_validator(self):
        contract = load('aws_c0_cost_runtime_retrieval_closure_correction_contract.json')
        rows, evidence = [], {}
        for dimension in contract['resource_dimensions_in_order']:
            unit = contract['resource_dimension_units'][dimension]
            source_unit = next(iter(P.CONVERSIONS[unit]))
            ratio = P.CONVERSIONS[unit][source_unit]
            pages = self.pages(source_unit)
            conversion = {source_unit: [ratio.numerator, ratio.denominator]}
            rows.append(P.rate_row(dimension, unit, pages, conversion, '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z'))
            evidence[dimension] = {'pages': pages, 'conversion': conversion}
        model = P.cost_model(rows, '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z', '2026-09-04T22:00:00Z')
        self.assertEqual(P.validate_model(model, evidence), model)
        model_id = P.digest(P.canonical(model))
        launch = {'cost_model_identity': F.identity('aws_c0_cost_model/v2', model_id),
                  'cost_envelope': {'accounting_window': {'start_inclusive_utc': model['valid_from_utc'],
                                                         'end_exclusive_utc': model['valid_until_utc']}}}
        self.assertEqual(F._validate_cost_model(model, model_id, launch), model)
        limits = {d: 0 for d in evidence}
        self.assertEqual(P.maximum_cost(model, limits), 0)
        limits['instance_running_seconds'] = 10000000
        with self.assertRaisesRegex(P.Refusal, 'USD 50'):
            P.maximum_cost(model, limits)
        changed = copy.deepcopy(model)
        changed['rates'][0]['numerator_minor_units'] = 0
        with self.assertRaisesRegex(P.Refusal, 'replayed'):
            P.validate_model(changed, evidence)
        with self.assertRaisesRegex(P.Refusal, '22 dimensions'):
            P.cost_model(rows[:-1], model['valid_from_utc'], model['valid_until_utc'], model['observed_utc'])

    def test_duplicate_json_and_float_refused(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":1.1}', b'{"x":NaN}'):
            with self.assertRaises(P.Refusal):
                P.strict(raw)

    def test_sealed_product_selection_keeps_exclusion_proof(self):
        pages = self.pages(prices=('0.02', '0.04'), tokens=('next', None))
        row = P.rate_row('instance_running_seconds', 'SECOND', pages, {'Hrs': [1, 36]},
                         '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z',
                         {'sku': 'SYNTHETIC-SKU-0'})
        proof = P.strict(base64.b64decode(row['selected_rate_upper_bound_proof_canonical_json_base64']))
        self.assertEqual(proof['excluded_skus'], ['SYNTHETIC-SKU-1'])
        self.assertEqual(proof['product_filter'], {'sku': 'SYNTHETIC-SKU-0'})
        self.assertEqual(len(proof['pages']), 2)
        self.assertEqual((row['numerator_minor_units'], row['denominator_units']), (1, 1800))
        with self.assertRaisesRegex(P.Refusal, 'rate observation bound'):
            P.rate_row('instance_running_seconds', 'SECOND', pages, {'Hrs': [1, 36]},
                       '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z', {'sku': 'ABSENT'})

    def test_gibps_month_converts_to_mibps_seconds(self):
        ratio = P.CONVERSIONS['MIBPS_SECOND']['GiBps-mo']
        row = P.rate_row('ebs_provisioned_throughput_mibps_seconds', 'MIBPS_SECOND',
                         self.pages('GiBps-mo', ('40.96',)),
                         {'GiBps-mo': [ratio.numerator, ratio.denominator]},
                         '2026-09-04T22:00:00Z', '2026-09-04T23:00:00Z')
        self.assertEqual((row['numerator_minor_units'], row['denominator_units']), (1, 604800))

    def test_page_and_item_bounds_and_empty_result(self):
        body = {'FormatVersion': 'aws_v1', 'PriceList': [], 'NextToken': 'more'}
        with self.assertRaisesRegex(P.Refusal, 'page bound'):
            P.collect_pages(lambda r: (body, P.canonical(body), 'request-id'), {},
                            P.identity('test/v1', {}), lambda p: None, max_pages=1)
        body = {'FormatVersion': 'aws_v1', 'PriceList': ['{}', '{}']}
        with self.assertRaisesRegex(P.Refusal, 'item bound'):
            P.collect_pages(lambda r: (body, P.canonical(body), 'request-id'), {},
                            P.identity('test/v1', {}), lambda p: None, max_items=1)
        pages = self.pages()
        body = {'FormatVersion': 'aws_v1', 'PriceList': []}
        pages = P.collect_pages(lambda r: (body, P.canonical(body), 'request-id'), pages[0]['request'],
                                pages[0]['receipt']['caller_identity'], lambda p: None)
        with self.assertRaisesRegex(P.Refusal, 'empty pricing'):
            P.validate_pages(pages)

    def test_offline_collection_build_and_exclusive_files(self):
        contract = load('aws_c0_cost_runtime_retrieval_closure_correction_contract.json')
        spec = {'rows': [], 'valid_from_utc': '2026-09-04T22:00:00Z', 'valid_until_utc': '2026-09-04T23:00:00Z',
                'observed_utc': '2026-09-04T22:00:00Z', 'fixed_minor_units': 0,
                'resource_limits': {d: 0 for d in contract['resource_dimensions_in_order']}}
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for dimension in contract['resource_dimensions_in_order']:
                unit = contract['resource_dimension_units'][dimension]
                source_unit = next(iter(P.CONVERSIONS[unit]))
                ratio = P.CONVERSIONS[unit][source_unit]
                pages = self.pages(source_unit)
                collection = directory / dimension
                collection.mkdir()
                for page in pages:
                    P.save(collection, f'page-{page["page_index"]:04d}.json', page)
                P.save(collection, 'completion.json', {'terminal': True, 'page_count': len(pages),
                    'page_sha256': [P.digest(P.canonical(p)) for p in pages]})
                spec['rows'].append({'dimension': dimension, 'collection': dimension,
                                    'conversion': {source_unit: [ratio.numerator, ratio.denominator]}})
            model, evidence, bound = P.build_from_collections(spec, directory)
            self.assertEqual(bound, 0)
            self.assertEqual(len(model['rates']), 22)
            with self.assertRaises(FileExistsError):
                P.save(collection, 'completion.json', {})
            (collection / 'page-0000.json').unlink()
            with self.assertRaisesRegex(P.Refusal, 'completion mismatch'):
                P.build_from_collections(spec, directory)

    def test_old_digest_only_packet_model_is_refused(self):
        builder = module('scripts/build_aws_c0_gate1_packet.py', 'aws_c0_gate1_builder')
        observations = {k: {'synthetic': True} for k in builder.REQUIRED}
        observations.update(instance_preimage={'state': 'stopped'}, cost_ceiling_minor_units=5000,
                            pricing_evidence={d: {} for d in builder.COST_DIMENSIONS})
        with self.assertRaisesRegex(ValueError, 'cost_model'):
            builder.build({'repository_commit': 'test', 'repository_tree': 'test'}, observations)


def load(path: str):
    return json.loads((ROOT / path).read_text())


def reroot(record):
    result = copy.deepcopy(record); result.pop("record_sha256", None)
    result["record_sha256"] = hashlib.sha256(V.canonical_bytes(result)).hexdigest(); return result


def current_launch(record):
    result = copy.deepcopy(record)
    result["schema"] = "aws_c0_launch_request/v6"
    result["preparation_packet_identity"]["kind"] = "aws_c0_preparation_packet/v5"
    result["preparation_authorization_identity"]["kind"] = "aws_c0_preparation_authorization/v4"
    result["authority_audit_identity"]["kind"] = "aws_c0_audit_static_handoff_authority_audit/v4"
    result["static_validation_identity"]["kind"] = "aws_c0_material_runtime_static_validation/v4"
    result["closure_seed_identity"]["kind"] = "aws_c0_closure_seed/v2"
    result['material_correction_authority_id']=F.MATERIAL_AUTHORITY_ID
    return reroot(result)


class DeploymentSequenceTests(unittest.TestCase):
    """Simulated observations only: these fixtures are never AWS evidence."""
    @staticmethod
    def control(kind, value, when):
        raw=F.canonical_bytes(value)
        return {'control_kind':kind,'identity':F.identity(F.CONTROL_IDENTITY_KINDS[kind],F.digest(raw)),
                'canonical_json_base64':base64.b64encode(raw).decode(),'observed_utc':when,
                'authenticated_source_identity':F.identity(F.CONTROL_SOURCE_KINDS[kind],'a'*64)}

    @staticmethod
    def receipt(value, name):
        raw=F.canonical_bytes(value)
        return {'bucket_identity':F.identity('aws_s3_bucket/v1','b'*64),
                'key':'rehearsal/aws-c0/preparation/AWS-C0-PREP-492A4F1/'+name+'.json',
                'version_id':'offline-fixture-version-'+name,'bytes':len(raw),'sha256':F.digest(raw),
                'checksum_sha256_base64':base64.b64encode(hashlib.sha256(raw).digest()).decode()}

    @staticmethod
    def iam(after):
        names=['EBU-C0-Operator-492a4f1','EBU-Rehearsal-EC2-Role']
        if after:names+=['EBU-C0-Corrected-StepFunctions-v1','EBU-C0-Corrected-Finalizer-v1']
        return {'schema':'aws_c0_iam_policy_configuration/v1','roles':[
            {'role_arn':'arn:aws:iam::623609441658:role/'+name,'trust_policy':{'Version':'2012-10-17','Statement':[]},
             'inline_policies':{},'attached_managed_policies':[],'permissions_boundary':None,'tags':{},'max_session_duration':3600}
            for name in sorted(names)]}

    @staticmethod
    def rebind(packet,auth,seed,launch):
        launch['closure_seed_identity']=F.identity('aws_c0_closure_seed/v2',F.digest(F.canonical_bytes(seed)))
        launch['closure_seed_object']=DeploymentSequenceTests.receipt(seed,'seed')
        rooted=reroot(launch);launch.clear();launch.update(rooted)
        packet['launch_request_identity']=F.identity('aws_c0_launch_request/v6',launch['record_sha256'])
        packet['launch_request_object']=DeploymentSequenceTests.receipt(launch,'launch')
        auth['live_packet_identity']=F.identity('aws_c0_live_packet/v6',F.digest(F.canonical_bytes(packet)))
        auth['live_packet_object']=DeploymentSequenceTests.receipt(packet,'packet')
        auth['statement_sha256']=F.digest(F._live_statement(auth).encode())

    def material(self):
        inputs=G.build_deployment_inputs(ROOT,(ROOT/'aws/c0/state-machine/aws-c0.asl.json').read_bytes(),
            (ROOT/'aws/c0/ssm/EBU-C0-Start-v1.yaml').read_bytes(),
            (ROOT/'aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml').read_bytes())
        input_raw=F.canonical_bytes(inputs);input_id=F.identity('aws_c0_deployment_inputs/v1',F.digest(input_raw))
        launch=current_launch(load('aws/c0/fixtures/launch-request.valid.json'))
        seed={'schema':'aws_c0_closure_seed/v2','deployment_inputs_identity':input_id,
              'material_correction_authority_id':F.MATERIAL_AUTHORITY_ID,
              'deployment_inputs_canonical_json_base64':base64.b64encode(input_raw).decode(),
              'state_machine_arn':inputs['state_machine_arn'],'attempt_identity':launch['attempt_identity']}
        for index,sha in ((0,inputs['definition_source']['sha256']),(1,inputs['document_source']['sha256']),(7,inputs['template_sha256'])):
            launch['artifact_version_receipts'][index]['sha256']=sha
            launch['artifact_version_receipts'][index]['checksum_sha256_base64']=base64.b64encode(bytes.fromhex(sha)).decode()
        pre={'change_set_arn':'arn:aws:cloudformation:us-east-1:623609441658:changeSet/EBU-C0-492a4f1/offline-fixture',
             'stack_name':'EBU-C0-492a4f1','status':'CREATE_COMPLETE','execution_status':'AVAILABLE',
             'template_sha256':inputs['template_sha256'],'parameters_identity':F.identity('aws_c0_parameters/v1','c'*64),
             'effect_api_set_identity':F.identity('aws_c0_change_set_effect_api_set/v1','d'*64),
             'effect_resource_set_identity':F.identity('aws_c0_change_set_effect_resource_set/v1','e'*64),
             'expected_iam_after_identity':F.identity('aws_c0_planned_iam_policy_set/v1',F.digest(F.canonical_bytes(self.iam(True)))),
             'observed_utc':'2026-09-06T18:00:00Z','request_id':'offline-pre-request'}
        stable=['change_set_arn','stack_name','template_sha256','parameters_identity','effect_api_set_identity','effect_resource_set_identity']
        post={k:pre[k] for k in stable}
        post.update(execution_status='EXECUTE_COMPLETE',stack_status='CREATE_COMPLETE',execution_count=1,
                    execute_request_id='offline-execute-request',stack_observation_request_id='offline-stack-request',
                    execute_started_utc='2026-09-06T18:02:00Z',execute_completed_utc='2026-09-06T18:03:00Z',
                    observed_utc='2026-09-06T18:04:00Z')
        observed_workflow,observed_document=F._expected_deployed_controls(inputs,'1')
        before={k:{'offline_fixture':k} for k in F.PREDEPLOYMENT_CONTROLS}
        before.update(IAM_POLICY_SET=self.iam(False),CHANGE_SET_AND_EFFECTS=pre)
        after=copy.deepcopy(before);after.update(IAM_POLICY_SET=self.iam(True),CHANGE_SET_AND_EFFECTS=post,
            STANDARD_WORKFLOW=observed_workflow,SSM_DOCUMENT=observed_document)
        packet={'schema':'aws_c0_live_packet/v6','observed_utc':'2026-09-06T18:00:00Z',
                'deployment_inputs_identity':input_id,
                'runtime_control_preimages':[self.control(k,before[k],'2026-09-06T18:00:00Z') for k in F.PREDEPLOYMENT_CONTROLS],
                'change_set_identity':F.identity('aws_cloudformation_change_set/v1',F.digest(F.canonical_bytes(pre))),
                'live_session_assumer_expires_utc':'2026-09-06T19:00:00Z',
                'effect_api_set_identity':pre['effect_api_set_identity'],'effect_resource_set_identity':pre['effect_resource_set_identity']}
        auth={'schema':'aws_c0_live_authorization/v6','observed_utc':'2026-09-06T18:05:00Z',
              'deployment_inputs_identity':input_id,'deployment_authorized_utc':'2026-09-06T18:01:00Z',
              'deployment_started_utc':'2026-09-06T18:02:00Z','deployment_completed_utc':'2026-09-06T18:03:00Z',
              'execution_session_expires_utc':'2026-09-06T18:59:00Z',
              'post_deployment_control_preimages':[self.control(k,after[k],'2026-09-06T18:04:00Z') for k in F.POST_DEPLOYMENT_CONTROLS],
              'change_set_identity':packet['change_set_identity'],'account_identity':F.identity('aws_account/v1','1'*64),
              'attempt_identity':launch['attempt_identity'],
              'authenticated_source_identity':F.identity('aws_c0_operator_live_authorization_source/v1','2'*64)}
        for field in ('live_session_assumer_identity','execution_operator_role_identity','execution_session_policy_identity',
                      'execution_session_policy_ceiling_identity','execution_session_policy_subset_proof_identity','pass_role_scope_proof_identity'):
            packet[field]=auth[field]=F.identity('offline_test_identity/v1','3'*64)
        packet['execution_session_max_duration_seconds']=auth['execution_session_max_duration_seconds']=3600
        self.rebind(packet,auth,seed,launch)
        return packet,auth,seed,launch

    def change_control(self,packet,auth,seed,launch,kind,mutate,post=True):
        rows=auth['post_deployment_control_preimages'] if post else packet['runtime_control_preimages']
        for i,row in enumerate(rows):
            if row['control_kind']==kind:
                value=F.strict_json(base64.b64decode(row['canonical_json_base64']))
                mutate(value);rows[i]=self.control(kind,value,row['observed_utc'])
                break
        self.rebind(packet,auth,seed,launch)

    def test_truthful_local_three_phase_positive_flow(self):
        values=self.material()
        result=F.validate_deployment_sequence(*values)
        self.assertFalse(result['observed_deployed_resources'])
        self.assertNotIn('state_machine_identity',values[2])
        self.assertEqual(len(values[0]['runtime_control_preimages']),9)
        self.assertEqual(len(values[1]['post_deployment_control_preimages']),11)
        self.assertNotIn('ASSUME_EXACT_LIVE_SESSION',F._live_statement(values[1]))

    def complete_material(self):
        """Candidate OFFLINE chain; the public gate exposes missing bindings.

        This is not authenticated evidence or a claimed schema-valid fixture.
        Keep its positive-path regression red until the accepted inherited
        producer/runtime attachments are implemented; do not weaken the schema.
        """
        packet,auth,seed,launch=self.material()
        for record in (packet,auth,seed):
            for key,value in F._control_record(record['schema'],{}).items():record.setdefault(key,value)
        seed['observed_utc']='2026-09-06T17:58:00Z'
        launch.update(observed_utc='2026-09-06T17:59:00Z',attempt_deadline_utc='2026-09-06T18:20:00Z',cleanup_deadline_utc='2026-09-06T18:30:00Z')
        seed.update({key:copy.deepcopy(launch[key]) for key in ('region','instance_id','artifact_prefix','attempt_identity',
                     'iam_pagination_bounds','attempt_deadline_utc','cleanup_deadline_utc')})
        seed.update(account_identity=F.identity('aws_account/v1','1'*64),artifact_bucket_identity=self.receipt({},'x')['bucket_identity'],
            execution_name_prefix='AWS-C0-PLATFORM-SMOKE-492A4F1',closure_state_name='EmitSupervisorClosure',
            finalizer_software_identity=F.identity('aws_c0_finalizer_software/v1','2'*64),
            s3_version_max_pages=10,s3_version_max_items=200,history_max_pages=10,history_max_events=1000,
            malformed_input_disposition='AWS_C0_FINAL_INCONCLUSIVE')
        proof_raw=F.canonical_bytes({'offline_fixture':'not-authenticated-AWS-evidence'})
        encoded=base64.b64encode(proof_raw).decode()
        for stem,kind in [('execution_name_derivation','aws_c0_execution_name_derivation/v1'),('history_retrieval_contract','aws_c0_history_retrieval_contract/v1')]:
            seed[stem+'_identity']=F.identity(kind,F.digest(proof_raw));seed[stem+'_canonical_json_base64']=encoded
        seed['cost_envelope']={k:copy.deepcopy(launch['cost_envelope'][k]) for k in
            ('currency','ceiling_minor_units','cost_model_identity','accounting_window','resource_limits','iam_pagination_bounds')}
        seed['cost_envelope'].update(cost_model_key=launch['cost_model_object']['key'],cost_model_sha256=launch['cost_model_object']['sha256'])
        packet.update(packet_disposition='AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED',
            preparation_closure_identity=F.identity('aws_c0_preparation_closure/v5','4'*64),
            preparation_closure_object=self.receipt({},'preparation-closure'),
            pre_live_predecessor_object_receipts=[self.receipt({'offline_index':i},'predecessor-'+str(i)) for i in range(23)],
            live_authorization_key_target={'bucket_identity':self.receipt({},'x')['bucket_identity'],
                'key':launch['artifact_prefix']+'live-authorization.json','if_none_match':'*'},
            change_set_observation_identity=F.identity('aws_c0_change_set_observation/v1',packet['change_set_identity']['sha256']),
            iam_pagination_bounds=launch['iam_pagination_bounds'],final_preflight_observed_utc=packet['observed_utc'],
            final_instance_state='stopped',pre_live_object_count=24)
        packet.update(G.build_runtime_control_read_plan_fields_v2(ROOT))
        for record in (packet,auth):
            record['live_session_assumer_identity']=F.identity('aws_iam_principal/v1','5'*64)
            record['execution_operator_role_identity']=F.identity('aws_iam_role/v1','6'*64)
            for stem,kind in [('execution_session_policy','aws_iam_session_policy/v1'),
                              ('execution_session_policy_ceiling','aws_iam_policy_ceiling/v1'),
                              ('execution_session_policy_subset_proof','aws_iam_policy_subset_proof/v1'),
                              ('pass_role_scope_proof','aws_iam_passrole_scope_proof/v1')]:
                record[stem+'_identity']=F.identity(kind,F.digest(proof_raw));record[stem+'_canonical_json_base64']=encoded
        auth.update(live_authorization_key=launch['artifact_prefix']+'live-authorization.json',
            execution_session_identity=F.identity('aws_sts_role_session/v1','7'*64),
            execution_session_derivation_proof_identity=F.identity('aws_sts_session_derivation_proof/v1',F.digest(proof_raw)),
            execution_session_derivation_proof_canonical_json_base64=encoded,
            authorized_actions=['EXECUTE_EXACT_CHANGE_SET','PUBLISH_EXACT_LIVE_AUTHORIZATION','START_ONE_EXACT_EXECUTION'],
            denied_actions=['REPLAY','OTHER_CHANGE_SET','OTHER_ATTEMPT','SCIENTIFIC_EXECUTION'])
        self.rebind(packet,auth,seed,launch)
        return packet,auth,seed,launch

    def test_complete_schema_valid_chain_through_public_prepublication_gate(self):
        values=self.complete_material()
        self.assertEqual(G.validate_postdeployment_authorization(ROOT,*values),values[1])
        values[0]['final_preflight_observed_utc']='2026-09-06T17:59:59Z'
        with self.assertRaisesRegex(RuntimeError,'deployment phase record identity mismatch'):
            G.validate_postdeployment_authorization(ROOT,*values)

    def test_deployed_definition_role_logging_and_document_drift_refused(self):
        mutations=[('STANDARD_WORKFLOW',lambda v:v.update(type='EXPRESS')),
                   ('STANDARD_WORKFLOW',lambda v:v.update(roleArn='arn:aws:iam::623609441658:role/other')),
                   ('STANDARD_WORKFLOW',lambda v:v['definition'].update(StartAt='other')),
                   ('STANDARD_WORKFLOW',lambda v:v['loggingConfiguration'].update(level='OFF')),
                   ('SSM_DOCUMENT',lambda v:v.update(DocumentVersion='planned-version')),
                   ('SSM_DOCUMENT',lambda v:v['Content'].update(description='changed'))]
        for kind,mutation in mutations:
            values=self.material();self.change_control(*values,kind,mutation)
            with self.subTest(kind=kind),self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_observations_must_follow_successful_exact_deployment(self):
        for field,bad in [('change_set_arn','arn:aws:cloudformation:us-east-1:623609441658:changeSet/other/id'),
                          ('execution_status','AVAILABLE'),('stack_status','ROLLBACK_COMPLETE'),('execution_count',2),
                          ('execute_request_id',''),('template_sha256','0'*64),('execute_started_utc','2026-09-06T18:00:00Z')]:
            values=self.material();self.change_control(*values,'CHANGE_SET_AND_EFFECTS',lambda v:v.update({field:bad}))
            with self.subTest(field=field),self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)
        for when in ('2026-09-06T18:02:00Z','2026-09-06T18:06:00Z'):
            values=self.material();values[1]['post_deployment_control_preimages'][6]['observed_utc']=when
            with self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_no_future_resource_receipt_or_retroactive_authority(self):
        for mutation in (lambda p,a,s,l:s.update(state_machine_identity=F.identity('aws_step_functions_standard_state_machine/v1','4'*64)),
                         lambda p,a,s,l:a.update(deployment_authorized_utc='2026-09-06T18:04:00Z'),
                         lambda p,a,s,l:a['post_deployment_control_preimages'].pop(),
                         lambda p,a,s,l:p['runtime_control_preimages'].append(a['post_deployment_control_preimages'][6])):
            values=self.material();mutation(*values);self.rebind(*values)
            with self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_wrong_source_kind_or_fabricated_digest_refused(self):
        for field,bad in [('authenticated_source_identity',F.identity('made_up_observation_source/v1','a'*64)),
                          ('identity',F.identity('aws_iam_policy_set/v1','a'*64)),
                          ('identity',F.identity('', 'a'*64))]:
            values=self.material();values[1]['post_deployment_control_preimages'][6][field]=bad
            with self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_iam_plan_cannot_contain_future_role_id_or_change_existing_role(self):
        for mutation in (lambda v:v['roles'][0].update(RoleId='not-yet-created'),
                         lambda v:v['roles'][-1].update(tags={'changed':'yes'})):
            values=self.material();self.change_control(*values,'IAM_POLICY_SET',mutation)
            with self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_cross_record_and_exact_receipt_mismatch_refused_before_start(self):
        for mutate in (lambda p,a,s,l:p.update(observed_utc='2026-09-06T18:00:01Z'),
                       lambda p,a,s,l:a['live_packet_object'].update(version_id=''),
                       lambda p,a,s,l:s.update(state_machine_arn='other'),
                       lambda p,a,s,l:a.update(deployment_inputs_identity=F.identity('aws_c0_deployment_inputs/v1','f'*64))):
            values=self.material();mutate(*values)
            with self.assertRaises(F.Refusal):F.validate_deployment_sequence(*values)

    def test_new_schema_derivation_is_offline_deterministic_and_keeps_history(self):
        generator=module('scripts/build_aws_c0_sequence_schema.py','aws_c0_sequence_schema_builder')
        self.assertEqual(generator.build(ROOT),load(generator.OUTPUT))
        self.assertEqual(F.FROZEN_PRELIVE_OBJECT_COUNT,24);self.assertEqual(F.FROZEN_PRELIVE_PREDECESSOR_COUNT,23)
        self.assertEqual(tuple(F.FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256),tuple(v for _,v in V.GATE1_LINEAGE_IN_ORDER))
        self.assertEqual(F.FROZEN_PRELIVE_RECORD_KINDS[:6],tuple(k for k,_ in V.GATE1_LINEAGE_IN_ORDER))
        seed_schema=G.record_schema(ROOT,'closure_seed')['allOf'][1]
        self.assertNotIn('state_machine_identity',seed_schema['required'])
        self.assertIn('deployment_inputs_identity',seed_schema['required'])
        closure=G.record_schema(ROOT,'preparation_closure')['allOf'][1]
        self.assertEqual(closure['properties']['final_runtime_control_preimages']['maxItems'],9)
        self.assertEqual(G.record_schema(ROOT,'live_authorization')['allOf'][1]['properties']['post_deployment_control_preimages']['minItems'],11)

    def test_runtime_rechecks_real_definition_and_document_before_instance_start(self):
        packet,auth,seed,launch=self.material()
        packet['iam_pagination_bounds']=launch['iam_pagination_bounds'];self.rebind(packet,auth,seed,launch)
        inputs=F._seed_deployment_inputs(seed)
        workflow,document=F._expected_deployed_controls(inputs,'1')
        workflow['definition']=json.dumps(workflow['definition'],indent=2)+'\n'
        document['Content']=json.dumps(document['Content'],indent=2)+'\n'
        environment={'AWS_C0_EXPECTED_ACCOUNT_ID':'623609441658','AWS_C0_STATE_MACHINE_ARN':inputs['state_machine_arn'],
            'AWS_C0_SSM_DOCUMENT_NAME':inputs['ssm_document_name'],'AWS_C0_SSM_DOCUMENT_VERSION':'1',
            'AWS_C0_STATE_MACHINE_DEFINITION_SHA256':inputs['definition_source']['sha256'],
            'AWS_C0_SSM_DOCUMENT_SHA256':inputs['document_source']['sha256']}
        execution='arn:aws:states:us-east-1:623609441658:execution:ebu-c0-closure-synthetic-v1:'+launch['attempt_id']
        for changed in (False,True):
            current=copy.deepcopy(workflow)
            if changed:current['roleArn']='arn:aws:iam::623609441658:role/unapproved'
            with (mock.patch.object(F,'_env',side_effect=lambda name,*args:environment[name]),
                  mock.patch.object(F,'_query',return_value=F.ET.fromstring('<Response><Account>623609441658</Account></Response>')),
                  mock.patch.object(F,'_instance_state',return_value='stopped') as stopped,
                  mock.patch.object(F,'_json_api',side_effect=[current,document]) as reads,
                  mock.patch.object(F,'_aws_request',side_effect=AssertionError('no AWS allowed in local test'))):
                if changed:
                    with self.assertRaises(F.Refusal):F._runtime_preflight(packet,launch,execution,auth,seed)
                else:F._runtime_preflight(packet,launch,execution,auth,seed)
                stopped.assert_called_once();self.assertEqual(reads.call_count,2)

    def test_active_template_and_record_producers_form_acyclic_sequence(self):
        from graphlib import TopologicalSorter
        template=load('aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml')
        env=template['Resources']['FinalizerFunction']['Properties']['Environment']['Variables']
        self.assertEqual(env['AWS_C0_CLOSURE_SEED_VERSION_ID'],{'Ref':'ClosureSeedVersionId'})
        self.assertEqual(env['AWS_C0_LAUNCH_VERSION_ID'],{'Ref':'LaunchRequestVersionId'})
        self.assertNotIn('StateMachineSha256',template['Parameters'])
        self.assertEqual(env['AWS_C0_STATE_MACHINE_DEFINITION_SHA256'],{'Ref':'StateMachineDefinitionSha256'})
        self.assertEqual(template['Resources']['StateMachine']['Properties']['DefinitionSubstitutions']['FinalizerFunctionArn'],
                         {'Fn::GetAtt':['FinalizerFunction','Arn']})
        inputs=G.build_deployment_inputs(ROOT,(ROOT/'aws/c0/state-machine/aws-c0.asl.json').read_bytes(),
            (ROOT/'aws/c0/ssm/EBU-C0-Start-v1.yaml').read_bytes(),
            (ROOT/'aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml').read_bytes())
        self.assertFalse(inputs['observed_deployed_resources'])
        graph={'input_artifacts':set(),'seed':{'input_artifacts'},'launch':{'seed','input_artifacts'},
               'change_set':{'launch','seed'},'live_packet':{'change_set','launch'},'prior_authority':{'live_packet'},
               'finalizer':{'prior_authority','launch','seed'},'workflow':{'finalizer'},
               'observations':{'workflow'},'post_authorization':{'observations','live_packet','prior_authority'},
               'start':{'post_authorization'}}
        ordered=list(TopologicalSorter(graph).static_order())
        self.assertLess(ordered.index('seed'),ordered.index('workflow'))
        self.assertLess(ordered.index('observations'),ordered.index('post_authorization'))
        G.jsonschema.Draft202012Validator.check_schema(load('aws_c0_deployment_sequence_evidence_schema.json'))


class CanonicalTests(unittest.TestCase):
    def test_duplicate_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{"x":1,"x":2}')

    def test_float_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{"x":1.0}')

    def test_final_lf_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{}\n', canonical=True)

    def test_root_preimage_and_object_digest_differ(self):
        launch = load("aws/c0/fixtures/launch-request.valid.json")
        root_id = V.validate_root(launch, "aws_c0_launch_request/v3")
        self.assertNotEqual(root_id, V.digest(V.canonical_bytes(launch)))

    def test_nonroot_self_digest_refused(self):
        record = {"schema": "aws_c0_closure_seed/v2", "record_sha256": "0" * 64}
        with self.assertRaises(V.ValidationError): V.validate_nonroot(record, V.canonical_bytes(record), record["schema"])

    def test_identity_is_closed(self):
        with self.assertRaises(V.ValidationError): V.validate_identity({"kind": "x", "sha256": "0" * 64, "value": "1" * 64})


class AuthorityTests(unittest.TestCase):
    def test_frozen_arithmetic(self): V.validate_authorities()
    def test_exact_paths_and_modes(self): V.validate_paths()

    def test_overnight_scope_addition_remains_exact_and_refuses_unrelated_paths(self):
        self.assertIn('aws/c0/ssm/EBU-C0-Start-v1.yaml',V.LOCAL_DEPLOYMENT_READINESS_PATHS)
        self.assertIn('aws/c0/ssm/EBU-C0-Start-v1.yaml',V.GATE1_BOOTSTRAP_LINEAGE_EXCLUDED_PATHS)
        original=V._git
        def injected(*args,**kwargs):
            value=original(*args,**kwargs)
            if args[:2]==('diff','--name-only'):return value+'\nunauthorized-local-path.py'
            return value
        with mock.patch.object(V,'_git',side_effect=injected):
            with self.assertRaisesRegex(V.ValidationError,'path gate differs'):V.validate_paths()

    def test_66_84_108(self):
        counts = []
        for path in V.VALIDATION_PATHS:
            suite = load(path); counts.append(len(suite["positive_cases"]) + len(suite["negative_cases"]))
        self.assertEqual(counts, [66, 84, 108])

    def test_eighteen_schema_union(self):
        schema = load(V.EVIDENCE_SCHEMA_PATH)
        self.assertEqual(len(schema["oneOf"]), len(V.NEW_SCHEMAS), 18)

    def test_21_12_22_63(self):
        contract = load(V.CONTRACT_PATH)
        self.assertEqual(contract["pre_live_publication"]["minimum_object_count"], 21)
        self.assertEqual(len(contract["evidence_root_categories_semantic_order"]), 12)
        self.assertEqual(len(contract["resource_dimensions_in_order"]), 22)
        self.assertEqual(len(contract["read_only_preflight_api_resource_allowlist"]), 63)

    def test_stage_boundaries(self):
        contract = load(V.CONTRACT_PATH)
        self.assertEqual(contract["stage_boundary"]["stage_e_status"], "ACCEPTED_FINISHED_UNCHANGED")
        self.assertEqual(contract["stage_boundary"]["stage_f"], "FROZEN_SEPARATE_AWS_LINUX_BINDING_SCIENTIFIC_PACKET_AND_AUTHORIZATION_REQUIRED")

    def test_gate1_lineage_lane_is_additive_to_historical_registry(self):
        fixture = load("aws/c0/fixtures/negative-cases.json")
        self.assertEqual(fixture["schema"], "aws_c0_static_negative_case_execution/v5")
        self.assertEqual(fixture["executed_case_count"], 358)
        self.assertEqual(fixture["case_ids"][-6:], [
            "C0-G1-LINEAGE-N01", "C0-G1-LINEAGE-N02", "C0-G1-LINEAGE-N03",
            "C0-G1-LINEAGE-N04", "C0-G1-LINEAGE-N05", "C0-G1-LINEAGE-N06",
        ])

    def test_gate1_preparation_authorization_v3_statement_is_exact(self):
        contract = load("aws_c0_gate1_bootstrap_lineage_correction_contract.json")
        statement = contract["preparation_authorization_statement"]
        self.assertEqual(statement["statement_version"], "AUTHORIZE_AWS_C0_PREPARATION_V3")
        self.assertEqual(statement["statement_template"], V.GATE1_PREPARATION_STATEMENT_TEMPLATE)
        self.assertIn("pre_live_object_count=24", statement["statement_template"])
        self.assertNotIn("pre_live_object_count=21", statement["statement_template"])
        self.assertIn("deny=LIVE_EXECUTION,REPLAY,DELETE,TERMINATE,SCIENTIFIC_EXECUTION",
                      statement["statement_template"])

    def test_audit_and_static_v4_modes_are_distinct_and_offline(self):
        self.assertEqual(V.main(["--mode", "audit-v4"]), 0)
        self.assertEqual(V.main(["--mode", "static-v4"]), 0)
        with self.assertRaises(SystemExit):
            V.main(["--mode", "static-v3"])

    def test_local_deployment_manifest_refuses_checkout_byte_conversion(self):
        original_read = Path.read_bytes
        targets = [path for _, path in D.ARTIFACTS] + [D.FINALIZER_SOURCE]
        for target in targets:
            with self.subTest(target=target):
                def converted(path):
                    data = original_read(path)
                    return data.replace(b'\n', b'\r\n') if path == ROOT / target else data
                with mock.patch.object(Path, 'read_bytes', autospec=True, side_effect=converted):
                    with self.assertRaisesRegex(ValueError, 'exact committed bytes'):
                        D.build(ROOT)

    def test_local_deployment_manifest_is_deterministic_and_leaves_aws_values_unresolved(self):
        first = D.build(ROOT)
        second = D.build(ROOT)
        self.assertEqual(first, second)
        self.assertTrue(first["offline_only"])
        self.assertEqual(first["schema"], "aws_c0_local_deployment_material_manifest/v1")
        artifacts = {artifact["kind"]: artifact for artifact in first["artifacts"]}
        finalizer = artifacts["finalizer_zip"]
        self.assertEqual(finalizer["handler"], "finalizer.lambda_handler")
        self.assertEqual(finalizer["zip_member_order"], ["finalizer.py"])
        self.assertEqual(finalizer["zip_compression"], "stored")
        self.assertEqual(len(finalizer["sha256"]), 64)
        self.assertEqual(first["unresolved_external_inputs"], list(D.UNRESOLVED_EXTERNAL_INPUTS))

    def test_public_cli_writes_only_an_exclusive_canonical_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); inputs = []
            for name in ("audit.json", "static.json", "provisional.json"):
                path = root / name; path.write_bytes(b"{}") ; inputs.append(path)
            output = root / "audit-v4.json"
            args = ["--mode", "audit-v4", "--source", str(ROOT), "--output", str(output),
                    "--authority-audit-receipt", str(inputs[0]), "--static-validation-receipt", str(inputs[1]),
                    "--provisional-put-observation", str(inputs[2])]
            self.assertEqual(V.main(args), 0)
            record = V.strict_json_bytes(output.read_bytes(), canonical=True)
            self.assertEqual((len(record["parent_receipts"]), len(record["axis_receipts"]),
                              len(record["member_execution_receipts"])), (352, 878, 1108))
            self.assertEqual(V.main(args), 1)


class LaunchTests(unittest.TestCase):
    def setUp(self): self.launch = load("aws/c0/fixtures/launch-request.valid.json")
    def test_valid_in_static_and_controller(self):
        V.validate_launch_v3(self.launch)
        current = current_launch(self.launch)
        C.validate_launch(current, current["rehearsal_id"], current["attempt_id"])

    def test_extra_field_refused(self):
        changed = reroot({**self.launch, "unexpected_scientific_switch": False})
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_future_identity_refused_by_closure(self):
        changed = reroot({**self.launch, "live_authorization_identity": {"kind": "aws_c0_live_authorization/v2", "sha256": "0"*64, "value": "0"*64}})
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_wrong_attempt_suffix_refused(self):
        changed = copy.deepcopy(self.launch); changed["attempt_id"] = "ATTEMPT-CLOSURE-EVIL"; changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_timeout_cross_layer_refused(self):
        changed = copy.deepcopy(self.launch); changed["phase_timeouts_seconds"]["finalizer"] = 301; changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_cost_dimension_missing_refused(self):
        changed = copy.deepcopy(self.launch); changed["cost_envelope"]["resource_limits"].pop("kms_requests"); changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_three_modes_only(self):
        self.assertEqual(set(C.MODE_BY_SUFFIX.values()), {"SUCCESS", "FAIL_AFTER_CHECKPOINT", "TIMEOUT"})
        with self.assertRaises(C.Refusal): C._mode("ATTEMPT-X-OTHER")

    def test_platform_smoke_first_capsule_binds_existing_success_launch_only(self):
        current = current_launch(self.launch)
        binding = C.build_platform_smoke_known_case_local_binding(current)
        self.assertEqual(binding["schema"], "aws_c0_platform_smoke_known_case_local_binding/v3")
        self.assertEqual(binding["capsule_id"], "platform-smoke-known-case-v1")
        self.assertEqual(binding["test_case"], "SUCCESS_KNOWN_CASE")
        self.assertEqual(binding["budget_binding"]["ceiling_minor_units"], 5000)
        self.assertEqual(binding["budget_binding"]["currency"], "USD")
        self.assertEqual(binding["common_receipt_fields_in_order"],
                         list(C.PLATFORM_SMOKE_COMMON_RECEIPT_FIELDS))
        self.assertEqual(binding["reused_foundation_capabilities_in_order"],
                         list(C.PLATFORM_SMOKE_FOUNDATION_CAPABILITIES))
        self.assertEqual(binding["expected_artifact_classes_in_order"], [
            "ATTEMPT_CLAIM", "START_RECEIPT", "HEARTBEAT", "SAFE_CLOSE_RECEIPT",
            "CHECKPOINT", "SYNTHETIC_MANIFEST", "TERMINAL_RECEIPT",
            "CONTROLLER_CAPTURE_JOURNAL", "CONTROLLER_JOURNAL_HANDOFF",
            "STOPPED_OBSERVATION", "RESOURCE_USE_CLOSURE", "FINALIZER_RECEIPT",
            "FINALIZER_CAPTURE_JOURNAL", "COST_CLOSURE",
            "RETRIEVAL_VERIFICATION", "FINAL_MANIFEST",
        ])
        self.assertFalse(binding["scientific_conclusion_authorized"])
        self.assertFalse(binding["live_aws_execution_authorized"])
        self.assertTrue(binding["separate_capsule_authority_required"])
        self.assertFalse(binding["global_aggregate_payload_embedded"])
        self.assertNotIn("final_s3_capture_aggregate", json.dumps(binding, sort_keys=True))

    def test_platform_smoke_first_capsule_refuses_non_success_known_case(self):
        changed = copy.deepcopy(self.launch)
        changed = current_launch(changed)
        changed["attempt_id"] = "ATTEMPT-CLOSURE-FAIL-AFTER-CHECKPOINT"
        changed["artifact_prefix"] = (
            "rehearsal/aws-c0/AWS-C0-CLOSURE/"
            "ATTEMPT-CLOSURE-FAIL-AFTER-CHECKPOINT/"
        )
        changed = reroot(changed)
        with self.assertRaises(C.Refusal):
            C.build_platform_smoke_known_case_local_binding(changed)


class Gate1LineageCorrectionTests(unittest.TestCase):
    @staticmethod
    def packet(*, schema="aws_c0_live_packet/v6", count=24, predecessors=23):
        packet = {field: None for field in F.LIVE_PACKET_V6_FIELDS}
        packet.update({
            "schema": schema,
            "packet_disposition": "AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED",
            "final_instance_state": "stopped",
            "pre_live_object_count": count,
            "pre_live_predecessor_object_receipts": [object() for _ in range(predecessors)],
            "preparation_closure_identity": C.identity("aws_c0_preparation_closure/v5", "a" * 64),
            "launch_request_identity": C.identity("aws_c0_launch_request/v6", "b" * 64),
            "observed_utc": "2026-09-04T00:00:00Z",
            "live_session_assumer_expires_utc": "2026-09-04T01:00:00Z",
        })
        return packet

    @staticmethod
    def validate_packet(packet):
        with (mock.patch.object(F, "_common"), mock.patch.object(F, "_identity"),
              mock.patch.object(F, "_bound_base64")):
            F._validate_live_packet_v6(packet)

    def test_c0_g1_lineage_n01_stale_launch_version_refused(self):
        launch = current_launch(load("aws/c0/fixtures/launch-request.valid.json"))
        launch["schema"] = "aws_c0_launch_request/v4"
        launch = reroot(launch)
        with self.assertRaises(C.Refusal):
            C.validate_launch(launch, launch["rehearsal_id"], launch["attempt_id"])

    def test_c0_g1_lineage_n02_stale_live_packet_version_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(schema="aws_c0_live_packet/v4"))

    def test_c0_g1_lineage_n03_stale_live_authorization_version_refused(self):
        auth = {field: None for field in F.LIVE_AUTH_V6_FIELDS}
        auth["schema"] = "aws_c0_live_authorization/v4"
        with self.assertRaises(F.Refusal):
            F._validate_live_authorization_v6(auth)

    def test_c0_g1_lineage_n04_stale_21_object_count_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(count=21))

    def test_c0_g1_lineage_n05_stale_20_predecessor_count_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(predecessors=20))

    def test_c0_g1_lineage_n06_same_kind_wrong_hash_refused(self):
        self.assertEqual(F.FROZEN_PRELIVE_OBJECT_COUNT, 24)
        self.assertEqual(F.FROZEN_PRELIVE_PREDECESSOR_COUNT, 23)
        self.assertEqual(len(F.FROZEN_PRELIVE_RECORD_KINDS), 15)
        self.assertEqual(F.FROZEN_PRELIVE_RECORD_KINDS[:6], (
            "aws_c0_operator_bootstrap_packet/v4",
            "aws_c0_operator_bootstrap_authorization/v5",
            "aws_c0_operator_bootstrap_closure/v5",
            "aws_c0_operator_session_renewal_packet/v1",
            "aws_c0_operator_session_renewal_authorization/v1",
            "aws_c0_operator_session_renewal_closure/v1",
        ))
        coordinates = [{"key": f"object-{index}", "version_id": f"v-{index}",
                        "sha256": f"{index:064x}", "bytes": 1}
                       for index in range(23)]
        artifacts = coordinates[:8]
        records = coordinates[8:]
        packet = self.packet()
        packet["pre_live_predecessor_object_receipts"] = artifacts + records
        auth = {"live_packet_identity": C.identity("aws_c0_live_packet/v6", "c" * 64)}
        stale = V.canonical_bytes({"schema": "aws_c0_operator_bootstrap_packet/v4"})
        with (mock.patch.object(F, "_fetch_receipt", side_effect=[
                  (packet, b"", "c" * 64), (auth, b"", "d" * 64)]),
              mock.patch.object(F, "_validate_live_packet_v6"),
              mock.patch.object(F, "_validate_live_authorization_v6"),
              mock.patch.object(F, "_receipt", side_effect=lambda value: value),
              mock.patch.object(F, "_bucket_from_receipt", return_value="bucket"),
              mock.patch.object(F, "_s3_get", return_value=stale)):
            with self.assertRaisesRegex(F.Refusal, "complete-byte SHA-256 mismatch"):
                F._verify_prelive_objects({}, {}, {"artifact_version_receipts": artifacts})

    def test_sealed_gate0_lineage_semantics_are_explicitly_enforced(self):
        bootstrap = {
            "schema": "aws_c0_operator_bootstrap_closure/v5",
            "operator_bootstrap_disposition": "AWS_C0_OPERATOR_BOOTSTRAP_FAIL",
        }
        bootstrap_raw = V.canonical_bytes(bootstrap)
        bootstrap_hashes = list(F.FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256)
        bootstrap_hashes[2] = F.digest(bootstrap_raw)
        with mock.patch.object(F, "FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256", tuple(bootstrap_hashes)):
            with self.assertRaisesRegex(F.Refusal, "V5 bootstrap closure is not PASS"):
                F._validate_sealed_gate0_lineage_record(
                    2, "aws_c0_operator_bootstrap_closure/v5", bootstrap_raw, bootstrap)

        predecessor = {
            "kind": "aws_c0_operator_session_renewal_closure/v1",
            "sha256": F.FROZEN_GATE0_RENEWAL_PREDECESSOR_SHA256,
            "value": F.FROZEN_GATE0_RENEWAL_PREDECESSOR_SHA256,
        }
        base_renewal = {
            "schema": "aws_c0_operator_session_renewal_closure/v1",
            "operator_session_renewal_disposition": "AWS_C0_OPERATOR_SESSION_RENEWAL_PASS",
            "credentials_issued": True,
            "predecessor_closure_identity": predecessor,
        }
        mutations = (
            {**base_renewal, "credentials_issued": False},
            {**base_renewal, "predecessor_closure_identity": C.identity(
                "aws_c0_operator_session_renewal_closure/v1", "0" * 64)},
        )
        for renewal in mutations:
            with self.subTest(renewal=renewal):
                renewal_raw = V.canonical_bytes(renewal)
                renewal_hashes = list(F.FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256)
                renewal_hashes[5] = F.digest(renewal_raw)
                with mock.patch.object(F, "FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256", tuple(renewal_hashes)):
                    with self.assertRaisesRegex(F.Refusal, "V6 renewal closure semantics mismatch"):
                        F._validate_sealed_gate0_lineage_record(
                            5, "aws_c0_operator_session_renewal_closure/v1", renewal_raw, renewal)


class PaginationTests(unittest.TestCase):
    def test_all_pages_and_token_transcript(self):
        items, pages = V.paginate([{"Values":[1],"NextToken":"n"},{"Values":[2]}], max_pages=2, max_items=2, item_fields=("Values",))
        self.assertEqual(items, [1,2]); self.assertEqual(len(pages), 2)

    def test_truncation_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[1],"NextToken":"n"}], max_pages=1, max_items=2, item_fields=("Values",))

    def test_item_overflow_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[1,2]}], max_pages=1, max_items=1, item_fields=("Values",))

    def test_repeated_token_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[],"NextToken":"n"},{"Values":[],"NextToken":"n"}], max_pages=2, max_items=1, item_fields=("Values",))

    def test_no_latest_listing_api(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("ListObjectVersions", source); self.assertNotIn("ListObjectsV2", source)


class CostTests(unittest.TestCase):
    def setUp(self):
        dims = load(V.CONTRACT_PATH)["resource_dimensions_in_order"]; units = load(V.CONTRACT_PATH)["resource_dimension_units"]
        self.model = {"integer_maximum":9007199254740991,"product_maximum":100000,"total_maximum":100000,"fixed_minor_units":3,
                      "rates":[{"dimension":d,"unit":units[d],"numerator_minor_units":2,"denominator_units":3} for d in dims]}
        self.use = {"dimensions":[{"dimension":d,"unit":units[d],"charged_units":4,"limit_units":4} for d in dims]}

    def test_ceil_each_dimension_then_sum(self):
        charges,total=V.compute_cost(self.model,self.use); self.assertEqual(charges,[3]*22); self.assertEqual(total,69)

    def test_dimension_order_refused(self):
        self.use["dimensions"].reverse()
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_limit_refused(self):
        self.use["dimensions"][0]["charged_units"]=5
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_product_overflow_refused(self):
        self.model["product_maximum"]=1
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_finalizer_uses_same_integer_rule(self):
        charges,total=F.compute_cost(self.model,self.use); self.assertEqual((charges,total),([3]*22,69))


class RuntimeContractTests(unittest.TestCase):
    def test_local_sigv4_exact_version_get_is_transport_injected_and_offline(self):
        raw = b'{"schema":"test"}'
        expected = hashlib.sha256(raw).hexdigest()
        calls = []

        def credentials():
            return {"access_key_id": "AKIDEXAMPLE", "secret_access_key": "secret",
                    "session_token": "token"}

        def transport(host, uri, query, headers):
            calls.append((host, uri, query, headers))
            return raw, {"version_id": "v1", "checksum_sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "etag": '"source-etag"', "request_id": "request-1",
                         "tls_certificate_sha256": "a" * 64}

        received, receipt = C._download("valid-bucket", "frozen/key.json", "v1", expected,
                                        credential_provider=credentials, transport=transport,
                                        now=C.dt.datetime(2026, 9, 3, tzinfo=C.dt.timezone.utc))
        self.assertEqual(received, raw)
        self.assertEqual(receipt["version_id"], "v1")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], "versionId=v1")
        self.assertEqual(calls[0][3]["x-amz-checksum-mode"], "ENABLED")
        self.assertIn("AWS4-HMAC-SHA256", calls[0][3]["authorization"])

    def test_controller_preparation_get_callgraph_has_no_aws_cli_s3_get(self):
        source = (ROOT / "aws/c0/controller/ebu_c0_controller.py").read_text()
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        download = ast.get_source_segment(source, functions["_download"])
        prepare = ast.get_source_segment(source, functions["prepare_request"])
        self.assertIn("sigv4_exact_version_get", download)
        self.assertNotIn('"s3api", "get-object"', source)
        self.assertEqual(prepare.count("source_role=\""), 3)
        for role in ("LAUNCH_REQUEST_V5", "LIVE_PACKET_V5", "LIVE_AUTHORIZATION_V5"):
            self.assertIn(role, prepare)

    def test_ssm_completion_v2_is_closed_and_refuses_non_success(self):
        identity = {"kind": "aws_c0_attempt/v1", "sha256": "a" * 64, "value": "a" * 64}
        dispatch = {"kind": "aws_c0_ssm_dispatch_request/v2", "sha256": "b" * 64, "value": "b" * 64}
        record = C.build_ssm_completion_v2(attempt_identity=identity, dispatch_identity=dispatch,
                                           command_id="cmd-1", invocation_status="Success",
                                           observed_utc="2026-09-01T00:00:00Z")
        self.assertEqual(C.validate_ssm_completion_v2(record)["schema"], "aws_c0_ssm_completion_observation/v2")
        record["invocation_status"] = "Failed"
        with self.assertRaises(C.Refusal): C.validate_ssm_completion_v2(record)

    def test_bucket_names_are_dot_free_across_ssm_cfn_controller_and_finalizer(self):
        with self.assertRaises(C.Refusal):
            C._download("dot.bucket", "key", "version", "a" * 64)
        with mock.patch.dict(os.environ, {"AWS_C0_ARTIFACT_BUCKET": "dot.bucket",
                                          "AWS_C0_BUCKET_IDENTITY_SHA256": "a" * 64}, clear=False):
            with self.assertRaises(F.Refusal):
                F._bucket_from_receipt({"bucket_identity": {"kind": "aws_s3_bucket/v1", "sha256": "a" * 64,
                                                              "value": "a" * 64}})
        self.assertEqual(load("aws/c0/ssm/EBU-C0-Start-v1.yaml")["parameters"]["ArtifactBucket"]["allowedPattern"],
                         "^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")
        self.assertEqual(load("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")["Parameters"]["ArtifactBucketName"]["AllowedPattern"],
                         "^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")

    def test_retrieval_expected_count_is_frozen_not_observed(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("FROZEN_PRELIVE_OBJECT_COUNT = 24", source)
        self.assertIn("FROZEN_PRELIVE_PREDECESSOR_COUNT = 23", source)
        self.assertIn('"expected_object_count": FROZEN_PRELIVE_OBJECT_COUNT', source)
        self.assertNotIn('"expected_object_count": len(verified)', source)

    def test_finalizer_authenticated_requests_reserve_and_record_sanitized_journal_rows(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("journal.reserve(capture)", source)
        self.assertIn("observed_checksum_sha256", source)
        self.assertIn("finalizer_journal_aggregate", source)
        self.assertNotIn('"authorization": request_headers["authorization"]', source)

    def test_capture_journals_are_reserved_acyclic_and_observed_only(self):
        journal=C.CaptureJournal("controller")
        journal.reserve_for_operation({"operation":"S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                         {"observed_sha256":"a" * 64})
        journal.failed("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                       {"failure_class":"Refusal"})
        self.assertEqual([row["disposition"] for row in journal.envelopes],
                         ["OBSERVED_COMPLETE", "OBSERVED_FAILURE"])
        self.assertIsNone(journal.envelopes[0]["previous_envelope_sha256"])
        self.assertEqual(F.CaptureJournal().aggregate()["envelope_count"], 0)

    def test_controller_journal_seals_publishes_and_exact_version_readbacks_offline(self):
        attempt = C.identity("aws_c0_attempt/v1", "b" * 64)
        journal_key = "rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json"
        journal = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        journal.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                         {"observed_sha256": "a" * 64})
        published = []
        def publisher(bucket, key, raw):
            published.append((bucket, key, raw))
            return {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            self.assertEqual((bucket, key, version), ("valid-bucket", journal_key, "v1"))
            raw = published[0][2]
            return raw, {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "request-1"}
        journal_identity, receipt = C.publish_and_readback_controller_journal(
            journal=journal, bucket="valid-bucket", key=journal_key,
            attempt_identity=attempt, publisher=publisher, readback=readback)
        self.assertEqual(len(published), 1)
        self.assertEqual(journal_identity["kind"], "aws_c0_controller_capture_journal/v1")
        self.assertEqual(receipt["readback_receipt"]["version_id"], "v1")
        with self.assertRaises(C.Refusal): journal.seal()

    def test_controller_journal_refuses_bad_exact_version_readback(self):
        attempt = C.identity("aws_c0_attempt/v1", "b" * 64)
        journal = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        journal.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {})
        def publisher(bucket, key, raw):
            return {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        with self.assertRaises(C.Refusal):
            C.publish_and_readback_controller_journal(
                journal=journal, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json",
                attempt_identity=attempt, publisher=publisher,
                readback=lambda bucket, key, version: (b"wrong", {
                    "key": key, "version_id": version, "etag": '"journal-etag"',
                    "bytes": 5, "sha256": "0" * 64,
                    "checksum_sha256_base64": base64.b64encode(b"0" * 32).decode(),
                    "request_id": "request-1"}))

    def test_controller_journal_seals_only_after_terminal_attempt_completion(self):
        source = (ROOT / "aws/c0/controller/ebu_c0_controller.py").read_text()
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        prepare = ast.get_source_segment(source, functions["prepare_request"])
        run = ast.get_source_segment(source, functions["run_attempt"])
        self.assertIn("CaptureJournal", prepare)
        self.assertNotIn("publish_and_readback_controller_journal", prepare)
        self.assertNotIn("build_controller_journal_handoff_v1", prepare)
        self.assertNotIn("publish_controller_journal_handoff", prepare)
        self.assertIn("CaptureJournal.restore", run)
        terminal = run.index('if code != expected_exit or not terminal_seen')
        journal_put = run.index("publish_and_readback_controller_journal")
        carrier_build = run.index("build_controller_journal_handoff_v1")
        carrier_put = run.index("publish_controller_journal_handoff")
        self.assertLess(terminal, journal_put)
        self.assertLess(journal_put, carrier_build)
        self.assertLess(carrier_build, carrier_put)
        self.assertEqual(prepare.count("source_role=\""), 3)

    def test_fixed_carrier_passes_controller_version_and_publication_receipt_reference(self):
        controller = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        controller.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        controller.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {"observed_sha256": "a" * 64})
        stored = {}
        def publisher(bucket, key, raw):
            stored["raw"] = raw
            return {"key": key, "version_id": "controller-version-1", "etag": '"controller-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["raw"]
            return raw, {"key": key, "version_id": version, "etag": '"controller-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "controller-request-1"}
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "b" * 64, "value": "b" * 64}
        controller_identity, authenticated = C.publish_and_readback_controller_journal(
            journal=controller, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json",
            attempt_identity=attempt, publisher=publisher, readback=readback)
        handoff = C.build_controller_journal_handoff_v1(
            attempt_identity=attempt, bucket="valid-bucket",
            journal_identity=controller_identity, authenticated_readback=authenticated)
        self.assertEqual(handoff["controller_journal_object"]["version_id"], "controller-version-1")
        self.assertEqual(handoff["controller_publication_receipt_identity"], authenticated["publication_receipt_identity"])
        self.assertEqual(len(handoff["controller_receipt_coordinate_execution_receipts_in_order"]), 22)
        accepted = load("aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json")["$defs"]
        self.assertEqual(set(handoff["controller_publication_receipt"]),
                         set(accepted["capture_journal_publication_receipt"]["required"]))
        self.assertEqual(set(handoff["controller_readback_receipt"]),
                         set(accepted["capture_journal_readback_receipt"]["required"]))
        receipt_fields = set(accepted["closed_pointer_comparison_execution_receipt"]["required"])
        self.assertTrue(all(set(row) == receipt_fields for row in
                            handoff["controller_receipt_coordinate_execution_receipts_in_order"]))
        validated = F.validate_controller_journal_handoff_v1(
            handoff, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
            attempt_identity=attempt)
        self.assertEqual(validated, handoff)
        self.assertEqual(C.CONTROLLER_HANDOFF_COORDINATE_ROWS,
                         F.CONTROLLER_HANDOFF_COORDINATE_ROWS)
        tautology = copy.deepcopy(handoff)
        tautology["controller_receipt_coordinate_execution_receipts_in_order"][0] = F._execution_receipt(
            1, "ARBITRARY_TAUTOLOGY_001", "/attempt_identity/value",
            "/attempt_identity/value", "STRING_EQUAL", attempt["value"], attempt["value"])
        comparison_root = {
            "attempt_identity": attempt,
            "controller_journal_object": tautology["controller_journal_object"],
            "controller_publication_receipt": tautology["controller_publication_receipt"],
            "controller_readback_receipt": tautology["controller_readback_receipt"],
            "controller_publication_receipt_identity": tautology["controller_publication_receipt_identity"],
            "controller_readback_receipt_identity": tautology["controller_readback_receipt_identity"],
        }
        local_preimage = {
            **comparison_root,
            "coordinate_receipt_sha256s": [
                row["receipt_sha256"] for row in
                tautology["controller_receipt_coordinate_execution_receipts_in_order"]
            ],
        }
        local_sha = F.digest(F.canonical_bytes(local_preimage))
        tautology["controller_local_validation_receipt_sha256"] = local_sha
        tautology["controller_local_validation_receipt_identity"] = F.identity(
            "aws_c0_controller_journal_local_validation_receipt/v1", local_sha)
        core = {name: item for name, item in tautology.items()
                if name not in F.HANDOFF_EXCLUDED_FIELDS}
        core_raw = F.canonical_bytes(core)
        handoff_sha = F.digest(F.HANDOFF_HASH_DOMAIN.encode() + b"\0" + core_raw)
        tautology["handoff_canonical_body_byte_count"] = len(core_raw)
        tautology["handoff_canonical_sha256"] = handoff_sha
        tautology["handoff_identity"] = F.identity(
            "aws_c0_controller_journal_handoff/v1", handoff_sha)
        with self.assertRaises(F.Refusal):
            F.validate_controller_journal_handoff_v1(
                tautology, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
                attempt_identity=attempt)
        changed = copy.deepcopy(handoff)
        changed["controller_journal_object"]["version_id"] = "wrong-version"
        with self.assertRaises(F.Refusal):
            F.validate_controller_journal_handoff_v1(
                changed, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
                attempt_identity=attempt)

    def test_finalizer_discovers_carrier_then_gets_carrier_and_controller_exact_versions(self):
        prefix = "rehearsal/aws-c0/R/A/"
        journal_key = prefix + "evidence/controller-capture-journal.json"
        carrier_key = prefix + "evidence/controller-capture-journal-handoff.json"
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "8" * 64, "value": "8" * 64}
        controller = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        controller.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        controller.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {"observed_sha256": "9" * 64})
        stored = {}
        def publisher(bucket, key, raw):
            stored["journal"] = raw
            return {"key": key, "version_id": "controller-v1", "etag": '"controller-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["journal"]
            return raw, {"key": key, "version_id": version, "etag": '"controller-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "controller-request-2"}
        journal_identity, authenticated = C.publish_and_readback_controller_journal(
            journal=controller, bucket="valid-bucket", key=journal_key,
            attempt_identity=attempt, publisher=publisher, readback=readback)
        handoff = C.build_controller_journal_handoff_v1(
            attempt_identity=attempt, bucket="valid-bucket",
            journal_identity=journal_identity, authenticated_readback=authenticated)
        carrier_raw = C.canonical_bytes(handoff)
        listing_raw = (
            "<ListVersionsResult><IsTruncated>false</IsTruncated><Version>"
            f"<Key>{carrier_key}</Key><VersionId>carrier-v1</VersionId>"
            "</Version></ListVersionsResult>"
        ).encode()
        calls = []
        def request(service, method, host, path, query, body, headers=None):
            calls.append((service, method, path, tuple(query)))
            if path == "/":
                raw, observed, operation = listing_raw, {}, "LIST_OBJECT_VERSIONS"
            elif path == "/" + carrier_key:
                raw, observed, operation = carrier_raw, {
                    "x-amz-version-id": "carrier-v1", "etag": '"carrier-etag"',
                    "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(carrier_raw).digest()).decode(),
                }, "GET_OBJECT_EXACT_VERSION"
            elif path == "/" + journal_key:
                raw = stored["journal"]
                observed, operation = {
                    "x-amz-version-id": "controller-v1", "etag": '"controller-etag"',
                    "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                }, "GET_OBJECT_EXACT_VERSION"
            else:
                raise AssertionError(path)
            capture = {
                "path": path, "operation": operation,
                "operation_requested_utc": "2026-09-03T00:00:00.000000Z",
                "operation_completed_utc": "2026-09-03T00:00:00.000001Z",
                "request_envelope_sha256": hashlib.sha256(repr((path, query)).encode()).hexdigest(),
                "observed_request_id": "request-1",
            }
            if operation == "LIST_OBJECT_VERSIONS":
                capture["response_body_base64"] = base64.b64encode(raw).decode()
            assert F._ACTIVE_JOURNAL is not None
            F._ACTIVE_JOURNAL.reserve(capture)
            F._ACTIVE_JOURNAL.append(operation, capture, "OBSERVED_COMPLETE")
            return raw, observed
        original = F._aws_request
        original_journal = F._ACTIVE_JOURNAL
        F._aws_request = request
        F._ACTIVE_JOURNAL = F.CaptureJournal()
        try:
            with mock.patch.dict(os.environ, {"AWS_C0_BUCKET_IDENTITY_SHA256": "a" * 64}):
                decoded, observation = F._discover_controller_journal_handoff(
                    "valid-bucket", prefix, attempt)
        finally:
            F._aws_request = original
            F._ACTIVE_JOURNAL = original_journal
        self.assertEqual([row[2] for row in calls], ["/", "/" + carrier_key, "/" + journal_key])
        self.assertEqual(decoded["controller_journal_object"]["version_id"], "controller-v1")
        self.assertEqual(observation["controller_publication_receipt_identity"],
                         authenticated["publication_receipt_identity"])

    def test_final_aggregate_exactly_matches_accepted_one_hundred_field_interface(self):
        schema = load("aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json")
        required = set(schema["$defs"]["final_s3_capture_aggregate"]["required"])
        self.assertEqual(len(required), 100)
        self.assertEqual(F.FINAL_CAPTURE_AGGREGATE_FIELDS, required)
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        tree = ast.parse(source)
        function = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}[
            "_build_accepted_capture_aggregate"
        ]
        aggregate_assignment = next(
            node for node in ast.walk(function)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "aggregate" for target in node.targets)
            and isinstance(node.value, ast.Dict)
        )
        literal_fields = {
            key.value for key in aggregate_assignment.value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        post_assignment_fields = {
            node.slice.value for node in ast.walk(function)
            if isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name) and node.value.id == "aggregate"
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)
        }
        self.assertEqual(literal_fields | post_assignment_fields, required)

    def test_final_manifest_put_is_the_last_substantive_finalizer_put(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        functions = {node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}
        closure = ast.get_source_segment(source, functions["closure"])
        terminal_put = closure.index('"evidence/final-manifest"')
        self.assertEqual(closure.count('"evidence/final-manifest"'), 1)
        self.assertNotIn("_put_record(", closure[terminal_put + 1:])
        self.assertIn('"aws_c0_final_manifest_publication_observation/v4"', closure[terminal_put:])
        self.assertIn('"final_manifest_publication_observation_object": None', closure[terminal_put:])

    def test_finalizer_journal_conditional_publish_and_exact_readback_are_injected(self):
        journal = F.CaptureJournal()
        journal.reserve({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.append("S3_GET_OBJECT_EXACT_VERSION", {"response_sha256": "a" * 64}, "OBSERVED_COMPLETE")
        stored = {}
        def publisher(bucket, key, raw):
            stored["raw"] = raw
            return {"key": key, "version_id": "v1", "etag": '"finalizer-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["raw"]
            return raw, {"key": key, "version_id": version, "etag": '"finalizer-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "finalizer-request-1"}
        identity, receipt = F.publish_and_readback_finalizer_journal(
            journal=journal, bucket="valid-bucket", key="journal", publisher=publisher, readback=readback)
        self.assertEqual(identity["kind"], "aws_c0_finalizer_capture_journal/v1")
        self.assertEqual(receipt["readback_receipt"]["version_id"], "v1")

    def test_finalizer_journal_readback_failure_refuses_and_aws_request_is_journaled(self):
        journal = F.CaptureJournal(); journal.reserve({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.append("S3_GET_OBJECT_EXACT_VERSION", {}, "OBSERVED_COMPLETE")
        publisher = lambda bucket, key, raw: {"key": key, "version_id": "v1", "etag": '"finalizer-etag"',
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        with self.assertRaises(F.Refusal):
            F.publish_and_readback_finalizer_journal(journal=journal, bucket="valid-bucket", key="journal",
                publisher=publisher, readback=lambda bucket, key, version: (b"bad", {
                    "key": key, "version_id": version, "etag": '"finalizer-etag"',
                    "bytes": 3, "sha256": "0" * 64,
                    "checksum_sha256_base64": base64.b64encode(b"0" * 32).decode(),
                    "request_id": "finalizer-request-1"}))
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        request = ast.get_source_segment(source, {node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}["_aws_request"])
        self.assertIn("journal.reserve(capture)", request)
        self.assertIn("OBSERVED_COMPLETE", request)
        self.assertIn("OBSERVED_FAILURE", request)

    def test_runtime_bundle_binds_sealed_controller_journal_and_readback(self):
        sidecar = {"kind": "aws_c0_source_sidecar/v5", "sha256": "a" * 64, "value": "a" * 64}
        dispatch = {"kind": "aws_c0_ssm_dispatch_request/v2", "sha256": "b" * 64, "value": "b" * 64}
        journal = {"kind": "aws_c0_controller_capture_journal/v1", "sha256": "c" * 64, "value": "c" * 64}
        readback = {"schema": "aws_c0_controller_journal_authenticated_readback/v1",
                    "content_chain_sha256": "d" * 64,
                    "publication_receipt": {},
                    "publication_receipt_identity": {"kind": "aws_c0_capture_journal_publication_receipt/v1", "sha256": "e" * 64, "value": "e" * 64},
                    "readback_receipt": {},
                    "readback_receipt_identity": {"kind": "aws_c0_capture_journal_readback_receipt/v1", "sha256": "f" * 64, "value": "f" * 64}}
        bundle = C.build_runtime_start_attestation_bundle_v3(
            source_sidecar_identity=sidecar, source_sidecar_bytes=b"sidecar", dispatch_identity=dispatch,
            controller_capture_journal_identity=journal,
            controller_capture_journal_authenticated_readback=readback)
        self.assertEqual(bundle["schema"], "aws_c0_runtime_start_attestation_bundle/v4")
        self.assertEqual(bundle["controller_capture_journal_identity"], journal)

    def test_ssm_embedded_is_structurally_identical(self):
        template=load("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        self.assertEqual(template["Resources"]["EBUC0StartDocument"]["Properties"]["Content"], load("aws/c0/ssm/EBU-C0-Start-v1.yaml"))

    def test_ssm_exact_three_version_handoff(self):
        doc=load("aws/c0/ssm/EBU-C0-Start-v1.yaml"); command="\n".join(doc["mainSteps"][0]["inputs"]["runCommand"])
        for token in ("prepare-request-v4","LaunchRequestVersionId","LivePacketVersionId","LiveAuthorizationVersionId","systemctl start --no-block"):
            self.assertIn(token, command)

    def test_asl_no_retry_and_single_stop(self):
        states=load("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertFalse(any("Retry" in state for state in states.values()))
        self.assertEqual(sum(state.get("Resource")=="arn:aws:states:::aws-sdk:ec2:stopInstances" for state in states.values()),1)

    def test_asl_first_heartbeat_remainder_and_safe_close(self):
        states=load("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertIn("WaitFirstHeartbeatRemainder",states); self.assertIn("EmitSafeClose",states)

    def test_asl_is_strict_json_and_compacts_api_evidence(self):
        states=V.load_json("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertEqual(states["CompactPreflight"]["ResultPath"],"$")
        self.assertNotIn("launch.$",states["CompactPreflight"]["Parameters"]["context"])
        self.assertEqual(set(states["Preflight"]["ResultSelector"]["value"]),set(states["CompactPreflight"]["Parameters"]["context"]))
        self.assertEqual(states["DescribeBootState"]["ResultSelector"], {"state.$":"$.Reservations[0].Instances[0].State.Name"})
        self.assertEqual(states["GetSsmDelivery"]["ResultSelector"], {"status.$":"$.Status"})

    def test_execution_history_iam_uses_only_sealed_execution_arns(self):
        template=V.load_json("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        statements=template["Resources"]["FinalizerRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        entries={entry.get("Sid"):entry for entry in statements if isinstance(entry,dict)}
        execution=entries["ClosureReadSealedExecutionOnly"]
        self.assertEqual(execution["Action"],["states:DescribeExecution","states:GetExecutionHistory"])
        self.assertEqual(execution["Resource"]["Fn::Sub"],"arn:aws:states:us-east-1:${AWS::AccountId}:execution:ebu-c0-closure-synthetic-v1:*")
        self.assertEqual(entries["ClosureReadExactStateMachine"]["Action"],"states:DescribeStateMachine")

    def test_cloudformation_creation_time_arns_use_only_known_names(self):
        template = V.load_json("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        parameters = template["Parameters"]
        self.assertNotIn("ChangeSetArn", parameters)
        self.assertNotIn("StackArn", parameters)
        self.assertEqual(parameters["ExpectedChangeSetName"], {
            "Type": "String", "AllowedPattern": "^[A-Za-z][-A-Za-z0-9]{0,127}$",
        })
        statements = template["Resources"]["FinalizerRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        entries = {entry.get("Sid"): entry for entry in statements if isinstance(entry, dict)}
        self.assertEqual(
            entries["ClosureReadChangeSet"]["Resource"]["Fn::Sub"],
            "arn:${AWS::Partition}:cloudformation:${AWS::Region}:${AWS::AccountId}:changeSet/${ExpectedChangeSetName}/*",
        )
        self.assertEqual(
            entries["ClosureReadStack"]["Resource"]["Fn::Sub"],
            "arn:${AWS::Partition}:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/${AWS::StackName}/*",
        )
        expected_actions = {
            "ClosureReadChangeSet": {"cloudformation:DescribeChangeSet"},
            "ClosureReadStack": {
                "cloudformation:GetTemplate", "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
            },
        }
        observed = {}
        for statement in statements:
            actions = statement.get("Action", [])
            actions = [actions] if isinstance(actions, str) else actions
            selected = {action for action in actions if action.startswith("cloudformation:")}
            if selected:
                self.assertNotEqual(statement.get("Resource"), "*")
                observed[statement["Sid"]] = selected
        self.assertEqual(observed, expected_actions)

    def test_controller_claim_precedes_start(self):
        source=(ROOT/"aws/c0/controller/ebu_c0_controller.py").read_text()
        claim=source.index("attempt-claim-")
        self.assertLess(claim,source.index('aws_c0_start_receipt/v7',claim))

    def test_service_has_only_needed_dac_capability(self):
        unit=(ROOT/"aws/c0/controller/ebu-c0@.service").read_text()
        self.assertIn("CapabilityBoundingSet=CAP_DAC_OVERRIDE",unit); self.assertNotIn("CAP_CHOWN",unit)

    def test_worker_environment_and_mode_are_closed(self):
        with mock.patch.dict(os.environ,{"AWS_C0_ATTEMPT_ID":"ATTEMPT-X-SUCCESS","AWS_C0_MODE":"SUCCESS","AWS_C0_HEARTBEAT_SECONDS":"1","AWS_C0_CHECKPOINT_SECONDS":"1"},clear=True):
            self.assertEqual(W._mode_from_attempt(os.environ["AWS_C0_ATTEMPT_ID"]),"SUCCESS")
        with self.assertRaises(W.WorkerRefusal): W._mode_from_attempt("ATTEMPT-X-EVIL")

    def test_closure_response_forbids_future_history_transcript(self):
        schema=load(V.EVIDENCE_SCHEMA_PATH); closure=schema["$defs"]["closure_response"]
        serialized=json.dumps(closure,sort_keys=True)
        self.assertGreaterEqual(serialized.count('"history_pagination_transcript": {"type": "null"}'),2)

    def test_history_normalizer_is_bounded_and_unique(self):
        payload={"action":"closure","response_variant":"FULL"}
        pages=[{"events":[{"type":"TaskSucceeded","taskSucceededEventDetails":{"output":json.dumps({"Payload":payload})}}]}]
        with mock.patch.object(F,"_json_api",side_effect=pages), mock.patch.dict(os.environ,{"AWS_C0_HISTORY_MAX_PAGES":"2","AWS_C0_HISTORY_MAX_EVENTS":"10"},clear=False):
            found,transcript=F.normalize_execution_history("arn:aws:states:us-east-1:123456789012:execution:x:y")
        self.assertEqual(found,payload); self.assertEqual(transcript["event_count"],1)


class AuthorityCaseExecutionTests(unittest.TestCase):
    """Execute every coordinate through a thematic positive or falsifier lane."""
    def test_all_258_coordinates_execute(self):
        launch=load("aws/c0/fixtures/launch-request.valid.json"); executed=[]
        for path in V.VALIDATION_PATHS:
            suite=load(path)
            for case in suite["positive_cases"]:
                V.validate_authorities(); executed.append(case.get("id",case.get("case_id")))
            for case in suite["negative_cases"]:
                theme=" ".join(str(case.get(key,"")) for key in ("theme","mutation","falsifier")).lower()
                if any(word in theme for word in ("cost","dimension","rate","ceiling","integer","round")):
                    bad={"integer_maximum":1,"product_maximum":0,"total_maximum":0,"fixed_minor_units":0,"rates":[]}
                    with self.assertRaises(V.ValidationError): V.compute_cost(bad,{"dimensions":[]})
                elif any(word in theme for word in ("page","pagination","latest","listobject","history","token")):
                    with self.assertRaises(V.ValidationError): V.paginate([{"Values":[],"NextToken":"x"}],max_pages=1,max_items=1,item_fields=("Values",))
                elif any(word in theme for word in ("json","digest","identity","canonical","record","schema","launch","packet","seed","start","safe-close","manifest","closure","receipt","timeout","attempt","runtime")):
                    bad=reroot({**launch,"unexpected":False})
                    with self.assertRaises(V.ValidationError): V.validate_launch_v3(bad)
                else:
                    V.validate_sources()
                executed.append(case.get("id",case.get("case_id")))
        self.assertEqual(len(executed),258); self.assertEqual(len(set(executed)),258)
        self.assertEqual(executed, load("aws/c0/fixtures/negative-cases.json")["case_ids"][:258])

    def test_all_878_literal_axes_execute_offline(self):
        # The real-execution registry is the accepted literal axis catalogue;
        # this invokes its non-scientific predicates exactly once each.
        V.validate_real_execution_registry()

    def test_registry_validator_does_not_use_polarity_as_an_outcome(self):
        row = load(V.REGISTRY_PATH)["ordered_registry_rows"][0]
        fixture = getattr(V, row[9])()
        self.assertEqual(getattr(V, row[10])(fixture)[0], "PASS")
        registry=load(V.REGISTRY_PATH)["ordered_registry_rows"]
        self.assertEqual(len(registry),878)
        self.assertEqual(sum(len(row[7]) for row in registry),1108)
        self.assertEqual(len({row[1] for row in registry}),878)

    def test_every_frozen_symbol_resolves_to_a_distinct_callable_and_every_member_is_observed(self):
        rows = load(V.REGISTRY_PATH)["ordered_registry_rows"]
        bound = V._literal_registry_callables(rows)
        symbols = [name for row in rows for name in row[9:12]]
        self.assertTrue(all(callable(bound[name]) and bound[name].__name__ == name for name in set(symbols)))
        self.assertEqual(len({row[9] for row in rows}), 878)
        self.assertEqual(len({row[11] for row in rows}), 878)
        parents, axes, members = V.execute_real_execution_registry()
        self.assertEqual((len(parents), len(axes), len(members)), (352, 878, 1108))
        self.assertEqual(sum(receipt["actual_disposition"] == "REFUSE" for receipt in axes), 711)
        self.assertTrue(all((r["actual_disposition"], r["actual_code"], r["actual_refusal"]) ==
                            (r["expected_disposition"], r["expected_code"], r["expected_refusal"])
                            for r in axes))

    def test_g06_literal_source_and_direct_callgraph_refuse_dynamic_funnels(self):
        rows = load(V.REGISTRY_PATH)["ordered_registry_rows"]
        tree = ast.parse((ROOT / "scripts/validate_aws_c0_static.py").read_text())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        frozen = {name for row in rows for name in row[9:12]}
        operators = {f"operate_axis_{i:04d}" for i in range(1, 879)}
        members = {f"member_axis_{i:04d}_{j}" for i, row in enumerate(rows, 1)
                   for j in range(1, len(row[7]) + 1)}
        self.assertTrue(frozen | operators | members <= set(functions))
        executor = functions["execute_real_execution_registry"]
        calls = {node.func.id for node in ast.walk(executor)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertTrue(frozen | members <= calls)
        self.assertFalse(any(isinstance(node, ast.Lambda) for node in ast.walk(executor)))
        self.assertNotIn("_fixture_from_coordinate", ast.unparse(executor))
        self.assertNotIn("_observe_fixture", ast.unparse(executor))
        for name in frozen:
            self.assertNotIn("row", {node.id for node in ast.walk(functions[name]) if isinstance(node, ast.Name)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
