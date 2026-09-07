"""Offline-only byte-bound staging material. Importing never contacts AWS."""
import base64
import hashlib
import json
import re
from datetime import datetime

ACCOUNT = '623609441658'
REGION = 'us-east-1'
INSTANCE = 'i-048bac00bdb540a4e'
BUCKET = 'ebu-stage-f-results-k7m4p2'
PREFIX = 'rehearsal/aws-c0/preparation/AWS-C0-PREP-492A4F1/'
RECOVERY_PREFIX = re.compile(
    r'^rehearsal/aws-c0/preparation/AWS-C0-PREP-492A4F1/recovery/[0-9a-f]{64}/$')
DOCUMENT = 'EBU-C0-Stage-492a4f1-v1'
ROLE = 'EBU-C0-Operator-492a4f1'
SESSION = 'AWS-C0-PREP-492a4f1'
POLICY = 'EBU-C0-Staging-Transport-v1'
INSTANCE_READ_POLICY = 'EBU-C0-Staging-Exact-Version-Read-v1'
INSTANCE_ROLE = 'EBU-Rehearsal-EC2-Role'
ARCHIVE_SHA = '4be82fa06928644167c3a2d65c1da1064b910872a841d44b0d3ab4a5bf8357ef'
ARCHIVE_BYTES = 414462464
MANIFEST_SHA = '130f80c15eb32be6d22e47e0b149b81ffa0ff04a6f69eb92bb35a8e683fe3641'
CONFIG_SHA = 'b7e5f119fa4f06ee013580de495bd391fb348d45316a11b836a98629620f2e9f'
SHA = re.compile(r'[0-9a-f]{64}')
VERSION = re.compile(r'[A-Za-z0-9._+~=/:-]{1,1024}')
ARTIFACTS = (
    ('CONTROLLER', 'ebu_c0_controller.py', '/usr/local/libexec/ebu-c0/ebu_c0_controller.py'),
    ('SYSTEMD_UNIT', 'ebu-c0@.service', '/etc/systemd/system/ebu-c0@.service'),
    ('SYNTHETIC_IMAGE_ARCHIVE', 'synthetic-image.tar', None),
)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def plan(commit,controller_bytes,unit_bytes):
    if not isinstance(commit,str) or not re.fullmatch(r'[0-9a-f]{40}',commit):
        raise ValueError('exact committed implementation required')
    for raw in (controller_bytes,unit_bytes):
        if not isinstance(raw,bytes) or not 0<len(raw)<=4194304 or b'\r' in raw:
            raise ValueError('bounded raw LF source bytes required')
    values=[(hashlib.sha256(controller_bytes).hexdigest(),len(controller_bytes)),
            (hashlib.sha256(unit_bytes).hexdigest(),len(unit_bytes)),(ARCHIVE_SHA,ARCHIVE_BYTES)]
    objects=[]
    for (role,name,destination),(sha,size) in zip(ARTIFACTS,values):
        objects.append({'role':role,'name':name,'key':PREFIX+'artifacts/'+sha+'/'+name,
                        'sha256':sha,'bytes':size,'destination':destination,
                        'checksum_sha256_base64':base64.b64encode(bytes.fromhex(sha)).decode()})
    return {'schema':'aws_c0_byte_bound_host_staging_plan/v1','implementation_commit':commit,
            'account':ACCOUNT,'region':REGION,'instance_id':INSTANCE,'bucket':BUCKET,'objects':objects,
            'image_manifest_sha256':MANIFEST_SHA,'image_config_sha256':CONFIG_SHA,
            'allowed_image_references':[repo+'@sha256:'+MANIFEST_SHA for repo in
                ['ebu/aws-c0-platform-smoke','docker.io/ebu/aws-c0-platform-smoke']],
            'maximum_puts':3,'maximum_instance_starts':1,'maximum_staging_commands':1,
            'maximum_running_seconds':900,'command_timeout_seconds':360,
            'aggregate_cost_ceiling_minor_units':5000,'conditional_create_only':True,
            'stop_required':True,'package_installation':False,'container_execution':False,
            'systemd_start_or_enable':False,'scientific_execution':False}

def recovery_plan(commit,controller_bytes,unit_bytes,attempt_identity_sha256):
    """Derive a fresh, collision-free namespace below the permitted prefix."""
    if not isinstance(attempt_identity_sha256,str) or not SHA.fullmatch(attempt_identity_sha256):
        raise ValueError('fresh attempt identity SHA-256 required')
    value=plan(commit,controller_bytes,unit_bytes)
    prefix=PREFIX+'recovery/'+attempt_identity_sha256+'/'
    if not RECOVERY_PREFIX.fullmatch(prefix):raise ValueError('bounded recovery prefix required')
    value['schema']='aws_c0_byte_bound_host_staging_plan/v2'
    value['recovery_attempt_identity_sha256']=attempt_identity_sha256
    for obj in value['objects']:
        obj['key']=prefix+'artifacts/'+obj['sha256']+'/'+obj['name']
    return value

def validate_plan(value,controller_bytes,unit_bytes):
    expected=plan(value['implementation_commit'],controller_bytes,unit_bytes)
    if value!=expected:raise ValueError('staging plan differs from exact material')
    return expected

def validate_recovery_plan(value,controller_bytes,unit_bytes):
    if not isinstance(value,dict):raise ValueError('recovery plan object required')
    expected=recovery_plan(value['implementation_commit'],controller_bytes,unit_bytes,
                           value.get('recovery_attempt_identity_sha256'))
    if value!=expected:raise ValueError('recovery plan differs from exact material')
    return expected

def validate_any_plan(value,controller_bytes,unit_bytes):
    if isinstance(value,dict) and value.get('schema')=='aws_c0_byte_bound_host_staging_plan/v2':
        return validate_recovery_plan(value,controller_bytes,unit_bytes)
    return validate_plan(value,controller_bytes,unit_bytes)

def validate_receipts(value,receipts):
    if not isinstance(receipts,list) or len(receipts)!=3:raise ValueError('three exact-version receipts required')
    for obj,receipt in zip(value['objects'],receipts):
        expected={'role','bucket','key','version_id','sha256','bytes','checksum_sha256_base64','etag','request_id'}
        if not isinstance(receipt,dict) or set(receipt)!=expected:raise ValueError('receipt fields not closed')
        for field in ('role','key','sha256','bytes','checksum_sha256_base64'):
            if receipt[field]!=obj[field]:raise ValueError('receipt does not bind intended artifact')
        if receipt['bucket']!=BUCKET or not isinstance(receipt['version_id'],str) or not VERSION.fullmatch(receipt['version_id']) or receipt['version_id']=='null':
            raise ValueError('exact versioned bucket receipt required')
        if not all(isinstance(receipt[k],str) and receipt[k] for k in ('etag','request_id')):
            raise ValueError('authenticated write receipt metadata required')
    return receipts

def instance_read_policy(value,receipts,controller_bytes,unit_bytes,observed_utc,expires_utc):
    """Additional temporary grant only; never replace an existing role policy.

    Each statement binds one key to its own VersionId, not a Cartesian product.
    Authenticated receipts and before/after role snapshots remain executor gates.
    """
    validate_any_plan(value,controller_bytes,unit_bytes)
    validate_receipts(value,receipts)
    if not all(isinstance(v,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',v)
               for v in (observed_utc,expires_utc)):
        raise ValueError('exact UTC observation and expiry required')
    try:
        timestamps=[datetime.strptime(v,'%Y-%m-%dT%H:%M:%SZ') for v in (observed_utc,expires_utc)]
    except (TypeError,ValueError) as exc:
        raise ValueError('exact UTC observation and expiry required') from exc
    if not 0<(timestamps[1]-timestamps[0]).total_seconds()<=3600:
        raise ValueError('temporary read grant must expire within one hour')
    return {'Version':'2012-10-17','Statement':[
        {'Sid':'ReadExactStagingVersion'+str(i+1),'Effect':'Allow','Action':'s3:GetObjectVersion',
         'Resource':'arn:aws:s3:::'+BUCKET+'/'+receipt['key'],
         'Condition':{'StringEquals':{'s3:VersionId':receipt['version_id'],'s3:ResourceAccount':ACCOUNT},
                      'Bool':{'aws:SecureTransport':'true'},'DateLessThan':{'aws:CurrentTime':expires_utc}}}
        for i,receipt in enumerate(receipts)]}

# Fixed command body, instantiated only with closed, exact-version receipts.
# It stages bytes and loads an image; it NEVER runs the image or starts a unit.
HOST_BODY = r'''
import base64,hashlib,json,os,shutil,stat,subprocess
from pathlib import Path
assert os.geteuid()==0
ENV={'PATH':'/usr/local/bin:/usr/bin:/bin','LC_ALL':'C','AWS_DEFAULT_REGION':'us-east-1',
     'AWS_CONFIG_FILE':'/dev/null','AWS_SHARED_CREDENTIALS_FILE':'/dev/null','AWS_EC2_METADATA_DISABLED':'false'}
def run(argv,timeout=30):
    p=subprocess.run(argv,cwd='/',env=ENV,stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout,check=False)
    if p.returncode:raise RuntimeError('bounded command failed: '+Path(argv[0]).name+':'+str(p.returncode))
    return p.stdout
def safe_dir(path,mode):
    p=Path(path)
    if not p.exists():p.mkdir(mode=mode)
    s=p.lstat()
    assert stat.S_ISDIR(s.st_mode) and not p.is_symlink() and s.st_uid==0 and s.st_gid==0
    assert stat.S_IMODE(s.st_mode)==mode
    return p
def file_hash(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1048576):h.update(chunk)
    return h.hexdigest()
for obj in PLAN['objects']:
    if obj['destination']:assert not os.path.lexists(obj['destination'])
assert shutil.disk_usage('/var/lib').free>=4294967296
run(['/usr/bin/docker','info','--format',chr(123)*2+'.ServerVersion'+chr(125)*2])
safe_dir('/var/lib/ebu-c0',0o700)
safe_dir('/var/lib/ebu-c0/requests',0o700)
safe_dir('/usr/local/libexec',0o755)
safe_dir('/usr/local/libexec/ebu-c0',0o755)
work=Path('/var/lib/ebu-c0/staging-'+PLAN_ID[:24]);work.mkdir(mode=0o700)
receipt_results=[]
for obj,receipt in zip(PLAN['objects'],RECEIPTS):
    destination=work/obj['name']
    output=run(['/usr/local/bin/aws','s3api','get-object','--region','us-east-1',
        '--bucket',PLAN['bucket'],'--key',receipt['key'],'--version-id',receipt['version_id'],
        '--checksum-mode','ENABLED','--expected-bucket-owner',PLAN['account'],str(destination)],120)
    metadata=json.loads(output)
    assert metadata['VersionId']==receipt['version_id']
    assert metadata['ContentLength']==receipt['bytes']
    assert metadata['ChecksumSHA256']==receipt['checksum_sha256_base64']
    assert destination.stat().st_size==obj['bytes'] and file_hash(destination)==obj['sha256']
    os.chmod(destination,0o600)
    receipt_results.append({'role':obj['role'],'version_id':metadata['VersionId'],
        'bytes':destination.stat().st_size,'sha256':obj['sha256']})
run(['/usr/bin/docker','image','load','--input',str(work/'synthetic-image.tar')],180)
metadata=json.loads(run(['/usr/bin/docker','image','inspect','sha256:'+PLAN['image_config_sha256']]))
assert len(metadata)==1
image=metadata[0]
assert image['Id']=='sha256:'+PLAN['image_config_sha256'] and image['Os']=='linux' and image['Architecture']=='amd64'
assert image['Config']['User']=='65534:65534' and image['Config']['WorkingDir']=='/work'
references=[r for r in image.get('RepoDigests',[]) if r in PLAN['allowed_image_references']]
assert references,'loaded archive does not preserve exact immutable repository manifest reference'
installed=[]
for obj in PLAN['objects']:
    if not obj['destination']:continue
    destination=Path(obj['destination'])
    raw=(work/obj['name']).read_bytes()
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.chmod(destination,0o644)
    s=destination.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o644
    assert s.st_size==obj['bytes'] and file_hash(destination)==obj['sha256']
    installed.append({'path':str(destination),'sha256':obj['sha256'],'bytes':s.st_size,'uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode)})
run(['/usr/bin/systemctl','daemon-reload'])
for obj in PLAN['objects']:
    p=work/obj['name']
    assert file_hash(p)==obj['sha256'];p.unlink()
work.rmdir()
print(json.dumps({'schema':'aws_c0_byte_bound_host_staging_result/v1','plan_sha256':PLAN_ID,
    'receipt_readbacks':receipt_results,'installed_files':installed,'image_config_sha256':PLAN['image_config_sha256'],
    'image_manifest_sha256':PLAN['image_manifest_sha256'],'verified_image_references':references,
    'image_loaded':True,'container_executed':False,'service_started_or_enabled':False,
    'package_installed':False,'scientific_execution':False},sort_keys=True,separators=(',',':')))
'''

def document(value,receipts,controller_bytes,unit_bytes):
    validate_any_plan(value,controller_bytes,unit_bytes);validate_receipts(value,receipts)
    variables={'PLAN':value,'RECEIPTS':receipts,'PLAN_ID':digest(value)}
    encoded=base64.b64encode(canonical(variables)).decode()
    script="import base64,json\nglobals().update(json.loads(base64.b64decode('"+encoded+"')))\n"+HOST_BODY
    compile(script,'<nonexecuted-byte-bound-staging>','exec')
    if '{{' in script:raise ValueError('SSM parser parameter marker refused')
    return {'schemaVersion':'2.2','description':'Exact-version verified AWS-C0 staging only; no container or service execution.',
            'parameters':{},'mainSteps':[{'action':'aws:runShellScript','name':'stageExactC0Bytes',
            'precondition':{'StringEquals':['platformType','Linux']},
            'inputs':{'timeoutSeconds':'360','runCommand':["set -eu\n/usr/bin/python3 - <<'C0_FIXED_STAGE'\n"+script+"\nC0_FIXED_STAGE\n"]}}]}

def temporary_policy(role_id,observed_utc,expires_utc):
    if not isinstance(role_id,str) or not re.fullmatch(r'AROA[A-Z0-9]{12,32}',role_id):raise ValueError('exact role ID required')
    times=[]
    for value in (observed_utc,expires_utc):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',value):raise ValueError('exact UTC required')
        times.append(datetime.fromisoformat(value.replace('Z','+00:00')))
    if not 0<(times[1]-times[0]).total_seconds()<=7200:raise ValueError('bounded policy lifetime required')
    condition={'DateLessThan':{'aws:CurrentTime':expires_utc},'StringEquals':{
        'aws:SourceIdentity':'konrad','aws:userid':role_id+':'+SESSION,'aws:PrincipalArn':f'arn:aws:iam::{ACCOUNT}:role/{ROLE}'}}
    doc=f'arn:aws:ssm:{REGION}:{ACCOUNT}:document/{DOCUMENT}'
    return {'Version':'2012-10-17','Statement':[
        {'Effect':'Allow','Action':['ssm:GetDocument','ssm:DescribeDocument'],'Resource':doc,'Condition':condition},
        {'Effect':'Allow','Action':'ssm:SendCommand','Resource':[doc,f'arn:aws:ec2:{REGION}:{ACCOUNT}:instance/{INSTANCE}'],'Condition':condition}]}
