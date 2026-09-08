# User-operated AWS-C0 platform smoke

This is the only current formal platform-smoke procedure. It supersedes the
temporary private SSM document lifecycle for the smoke itself. It uses the AWS
managed `AWS-RunShellScript` document, performs no document creation/deletion
and performs no IAM mutation.

The local preparer seals one exact LF command script and its SHA-256, the fixed
account, Region, retained instance, and immutable platform-smoke image manifest
digest. The local sealer requires the returned SendCommand ID, complete terminal
invocation stdout/stderr/status, authenticated caller identity, and the final
stopped `t3.small` receipt. The exact invocation stdout bytes are conditionally
uploaded beneath `rehearsal/aws-c0/user-operated-platform-smoke/`, retrieved by
the returned non-null VersionId, and compared byte-for-byte and by SHA-256.
Upload and retrieval receipts are part of the sealed evidence. Any missing or
mismatched member refuses formal PASS.

The command runs only the inert `SUCCESS` synthetic worker in a networkless,
read-only, non-root, capability-free, resource-bounded container. It is a
non-scientific platform smoke. Earlier manual execution is diagnostic only and
must never be supplied, renamed, or cited as evidence for this fresh procedure.

From the repository root, copy and paste this complete block. It starts the one
fixed retained instance once, sends one command, captures a terminal invocation,
stops the instance even on interruption or failure, and then seals the receipts.
It expects an authenticated `ebu-admin` profile unless `AWS_PROFILE` is already
set. Do not substitute receipts from any prior attempt.

```sh
set -eu
PROFILE="${AWS_PROFILE:-ebu-admin}"
REGION='us-east-1'
INSTANCE='i-048bac00bdb540a4e'
ACCOUNT='623609441658'
BUCKET='ebu-stage-f-results-k7m4p2'
ATTEMPT="ATTEMPT-USER-$(date -u +%Y%m%dT%H%M%SZ)-SUCCESS"
RUN_DIR="$(pwd)/aws-c0-platform-smoke-${ATTEMPT}"
TOOL='aws/c0/bootstrap/platform_smoke_transport.py'
STARTED=0
STOPPED=0

stop_and_record() {
  if [ "$STARTED" -eq 1 ] && [ "$STOPPED" -eq 0 ]; then
    set +e
    aws --profile "$PROFILE" --region "$REGION" ec2 stop-instances \
      --instance-ids "$INSTANCE" --output json > "$RUN_DIR/stop-request.json"
    aws --profile "$PROFILE" --region "$REGION" ec2 wait instance-stopped \
      --instance-ids "$INSTANCE"
    if aws --profile "$PROFILE" --region "$REGION" ec2 describe-instances \
      --instance-ids "$INSTANCE" --output json > "$RUN_DIR/stopped-instance.json"; then
      STOPPED=1
    fi
    set -e
  fi
}
trap stop_and_record EXIT
trap 'exit 130' HUP INT TERM

python3 "$TOOL" prepare --attempt-id "$ATTEMPT" --output-dir "$RUN_DIR"
aws --profile "$PROFILE" --region "$REGION" sts get-caller-identity \
  --output json > "$RUN_DIR/caller-identity.json"
aws --profile "$PROFILE" --region "$REGION" ec2 describe-instances \
  --instance-ids "$INSTANCE" --output json > "$RUN_DIR/pre-start-instance.json"
python3 - "$RUN_DIR/caller-identity.json" "$RUN_DIR/pre-start-instance.json" "$ACCOUNT" "$INSTANCE" <<'PY'
import json,sys
caller=json.load(open(sys.argv[1],encoding='utf-8'))
state=json.load(open(sys.argv[2],encoding='utf-8'))
assert caller['Account']==sys.argv[3]
reservations=state['Reservations']
assert len(reservations)==1 and reservations[0]['OwnerId']==sys.argv[3]
instances=reservations[0]['Instances']
assert len(instances)==1 and instances[0]['InstanceId']==sys.argv[4]
assert instances[0]['InstanceType']=='t3.small'
assert instances[0]['State']=={'Code':80,'Name':'stopped'}
PY

aws --profile "$PROFILE" --region "$REGION" ec2 start-instances \
  --instance-ids "$INSTANCE" --output json > "$RUN_DIR/start-request.json"
STARTED=1
aws --profile "$PROFILE" --region "$REGION" ec2 wait instance-running \
  --instance-ids "$INSTANCE"

ONLINE=0
COUNT=0
while [ "$COUNT" -lt 60 ]; do
  aws --profile "$PROFILE" --region "$REGION" ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=$INSTANCE" --output json > "$RUN_DIR/ssm-online.json"
  if python3 - "$RUN_DIR/ssm-online.json" "$INSTANCE" <<'PY'
import json,sys
rows=json.load(open(sys.argv[1],encoding='utf-8'))['InstanceInformationList']
raise SystemExit(0 if len(rows)==1 and rows[0]['InstanceId']==sys.argv[2] and rows[0]['PingStatus']=='Online' else 1)
PY
  then
    ONLINE=1
    break
  fi
  COUNT=$((COUNT + 1))
  sleep 5
done
test "$ONLINE" -eq 1

SCRIPT_SHA="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["command_script_sha256"])' "$RUN_DIR/plan.json")"
aws --profile "$PROFILE" --region "$REGION" ssm send-command \
  --document-name 'AWS-RunShellScript' --instance-ids "$INSTANCE" \
  --parameters "file://$RUN_DIR/parameters.json" --timeout-seconds 120 \
  --max-concurrency 1 --max-errors 0 --comment "AWS-C0 formal smoke $SCRIPT_SHA" \
  --output json > "$RUN_DIR/send-command.json"
COMMAND_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["Command"]["CommandId"])' "$RUN_DIR/send-command.json")"

COUNT=0
while [ "$COUNT" -lt 90 ]; do
  if aws --profile "$PROFILE" --region "$REGION" ssm get-command-invocation \
    --command-id "$COMMAND_ID" --instance-id "$INSTANCE" \
    --output json > "$RUN_DIR/invocation.json" 2> "$RUN_DIR/invocation-poll.stderr"; then
    STATUS="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["Status"])' "$RUN_DIR/invocation.json")"
    case "$STATUS" in
      Success|Cancelled|TimedOut|Failed) break ;;
    esac
  fi
  COUNT=$((COUNT + 1))
  sleep 2
done
test "$COUNT" -lt 90

stop_and_record
test "$STOPPED" -eq 1
RESULT_KEY="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result_key"])' "$RUN_DIR/plan.json")"
python3 - "$RUN_DIR/invocation.json" "$RUN_DIR/invocation-stdout.jsonl" <<'PY'
import json,sys
value=json.load(open(sys.argv[1],encoding='utf-8'))['StandardOutputContent'].encode('utf-8')
with open(sys.argv[2],'xb') as stream:
    stream.write(value)
PY
set -- $(python3 - "$RUN_DIR/invocation-stdout.jsonl" <<'PY'
import base64,hashlib,sys
raw=open(sys.argv[1],'rb').read()
sha=hashlib.sha256(raw).digest()
print(sha.hex(),base64.b64encode(sha).decode('ascii'),len(raw))
PY
)
STDOUT_SHA="$1"
STDOUT_CHECKSUM="$2"
STDOUT_BYTES="$3"
aws --profile "$PROFILE" --region "$REGION" s3api put-object \
  --bucket "$BUCKET" --key "$RESULT_KEY" \
  --body "$RUN_DIR/invocation-stdout.jsonl" \
  --content-type 'application/x-ndjson' --metadata "sha256=$STDOUT_SHA" \
  --checksum-algorithm SHA256 --checksum-sha256 "$STDOUT_CHECKSUM" \
  --if-none-match '*' --expected-bucket-owner "$ACCOUNT" \
  --output json > "$RUN_DIR/upload-receipt.json"
VERSION_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["VersionId"])' "$RUN_DIR/upload-receipt.json")"
test -n "$VERSION_ID"
test "$VERSION_ID" != 'null'
aws --profile "$PROFILE" --region "$REGION" s3api get-object \
  --bucket "$BUCKET" --key "$RESULT_KEY" --version-id "$VERSION_ID" \
  --checksum-mode ENABLED --expected-bucket-owner "$ACCOUNT" \
  "$RUN_DIR/retrieved-stdout.jsonl" \
  --output json > "$RUN_DIR/retrieval-receipt.json"
python3 "$TOOL" seal \
  --plan "$RUN_DIR/plan.json" \
  --command-script "$RUN_DIR/command-script.sh" \
  --caller-identity "$RUN_DIR/caller-identity.json" \
  --send-command "$RUN_DIR/send-command.json" \
  --invocation "$RUN_DIR/invocation.json" \
  --stopped-instance "$RUN_DIR/stopped-instance.json" \
  --uploaded-object "$RUN_DIR/invocation-stdout.jsonl" \
  --upload-receipt "$RUN_DIR/upload-receipt.json" \
  --retrieved-object "$RUN_DIR/retrieved-stdout.jsonl" \
  --retrieval-receipt "$RUN_DIR/retrieval-receipt.json" \
  --output "$RUN_DIR/formal-platform-smoke-evidence.json"
trap - EXIT HUP INT TERM
printf 'Formal evidence: %s\n' "$RUN_DIR/formal-platform-smoke-evidence.json"
```
