"""Offline exact bootstrap transport material; no AWS/host commands run here."""
import hashlib
import json
import re
from datetime import datetime

ACCOUNT = '623609441658'
REGION = 'us-east-1'
INSTANCE = 'i-048bac00bdb540a4e'
ROLE = 'EBU-C0-Operator-492a4f1'
ROLE_ARN = f'arn:aws:iam::{ACCOUNT}:role/{ROLE}'
DOCUMENT = 'EBU-C0-Bootstrap-492a4f1-v1'
DOCUMENT_ARN = f'arn:aws:ssm:{REGION}:{ACCOUNT}:document/{DOCUMENT}'
INSTANCE_ARN = f'arn:aws:ec2:{REGION}:{ACCOUNT}:instance/{INSTANCE}'
POLICY = 'EBU-C0-Bootstrap-Transport-v1'
SESSION = 'AWS-C0-PREP-492a4f1'

# Data only: tests inspect and compile this string, never execute it.
PROBE = r'''import hashlib, json, os, platform, stat, subprocess
from pathlib import Path
def command(argv):
    try:
        result=subprocess.run(argv,cwd='/',env={'PATH':'/usr/local/bin:/usr/bin:/bin','LC_ALL':'C'},
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10,check=False)
        return {'argv':argv,'exit_code':result.returncode,
            'stdout':result.stdout[:2048].decode('utf-8','replace'),
            'stderr':result.stderr[:1024].decode('utf-8','replace')}
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {'argv':argv,'error':type(exc).__name__}
def file_fact(name):
    p=Path(name)
    try:
        s=p.lstat()
    except FileNotFoundError:
        return {'path':name,'exists':False}
    result={'path':name,'exists':True,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),
        'symlink':stat.S_ISLNK(s.st_mode),'regular':stat.S_ISREG(s.st_mode),'bytes':s.st_size}
    if stat.S_ISREG(s.st_mode) and s.st_size<=4194304:
        result['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    return result
assert os.geteuid()==0
def go(field):
    return chr(123)*2+field+chr(125)*2
facts={'schema':'aws_c0_bootstrap_host_preimage/v1','disposition':'INVENTORY_ONLY_NOT_BOOTSTRAP_OR_SMOKE_PASS',
    'machine':platform.machine(),'system':platform.system(),'uid':os.geteuid(),
    'docker_version':command(['/usr/bin/docker','--version']),
    'aws_version':command(['/usr/local/bin/aws','--version']),
    'docker_daemon':command(['/usr/bin/docker','info','--format',' '.join(map(go,['.ServerVersion','.Architecture','.OSType']))]),
    'image':command(['/usr/bin/docker','image','inspect','--format',' '.join(map(go,['.Id','.Os','.Architecture'])),
        'sha256:b7e5f119fa4f06ee013580de495bd391fb348d45316a11b836a98629620f2e9f']),
    'files':[file_fact('/usr/local/libexec/ebu-c0/ebu_c0_controller.py'),file_fact('/etc/systemd/system/ebu-c0@.service')],
    'software_installed':False,'image_loaded':False,'container_executed':False,'scientific_execution':False}
print(json.dumps(facts,sort_keys=True,separators=(',',':')))
'''

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def document():
    return {'schemaVersion':'2.2','description':'Fixed AWS-C0 bootstrap host inventory only; no user command parameters.',
        'parameters':{},'mainSteps':[{'action':'aws:runShellScript','name':'inspectC0Host',
        'precondition':{'StringEquals':['platformType','Linux']},
        'inputs':{'timeoutSeconds':'60','runCommand':["set -eu\n/usr/bin/python3 - <<'C0_FIXED_PY'\n"+PROBE+'C0_FIXED_PY\n']}}]}

def policy(role_id,expires_utc,observed_utc):
    if not re.fullmatch(r'AROA[A-Z0-9]{12,32}',role_id):
        raise ValueError('exact AWS role ID required')
    for value in (expires_utc,observed_utc):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value):
            raise ValueError('exact UTC timestamp required')
    expiry=datetime.fromisoformat(expires_utc.replace('Z','+00:00'))
    observed=datetime.fromisoformat(observed_utc.replace('Z','+00:00'))
    if not 0<(expiry-observed).total_seconds()<=7200:
        raise ValueError('policy lifetime exceeds two hours or expired')
    condition={'DateLessThan':{'aws:CurrentTime':expires_utc},'StringEquals':{
        'aws:SourceIdentity':'konrad','aws:userid':role_id+':'+SESSION,'aws:PrincipalArn':ROLE_ARN}}
    return {'Version':'2012-10-17','Statement':[
        {'Sid':'ReadOnlyExactBootstrapDocument','Effect':'Allow',
         'Action':['ssm:GetDocument','ssm:DescribeDocument'],'Resource':DOCUMENT_ARN,'Condition':condition},
        {'Sid':'SendOnlyExactBootstrapToRetainedInstance','Effect':'Allow','Action':'ssm:SendCommand',
         'Resource':[DOCUMENT_ARN,INSTANCE_ARN],'Condition':condition}]}

def plan(role_id,expires_utc,observed_utc):
    doc=document(); permission=policy(role_id,expires_utc,observed_utc)
    return {'schema':'aws_c0_bootstrap_transport_plan/v1','account':ACCOUNT,'region':REGION,'instance_id':INSTANCE,
        'role_name':ROLE,'role_id':role_id,'policy_name':POLICY,'temporary_policy':permission,
        'temporary_policy_sha256':digest(permission),'document_name':DOCUMENT,'document':doc,
        'document_sha256':digest(doc),'document_version':'1','observed_utc':observed_utc,'expires_utc':expires_utc,
        'maximum_document_creates':1,'maximum_policy_puts':1,'maximum_send_commands':1,
        'maximum_instance_running_seconds':900,'aggregate_cost_ceiling_minor_units':5000,
        'parameterized_shell':False,'scientific_execution':False,'inspection_only':True,
        'instance_start_requires_separate_fresh_bound':True,'cleanup_required':True}

def validate_plan(value):
    expected=plan(value['role_id'],value['expires_utc'],value['observed_utc'])
    if value!=expected:
        raise ValueError('bootstrap transport plan differs from exact generated material')
    return expected

def dispatch_request(value):
    validate_plan(value)
    return {'DocumentName':DOCUMENT,'DocumentVersion':'1','DocumentHash':value['document_sha256'],
        'DocumentHashType':'Sha256','InstanceIds':[INSTANCE],'TimeoutSeconds':60,
        'MaxConcurrency':'1','MaxErrors':'0','Parameters':{}}
