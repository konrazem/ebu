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

The attempt timestamp is part of the attempt ID, plan, host binding, AWS command
chronology, and seal-time freshness check. Cleanup is armed before StartInstances.
One absolute 900-second post-start deadline governs every running-host wait and
cleanup, with 300 seconds reserved for stop/readback and bounded AWS CLI calls.
Unknown or out-of-order worker rows refuse PASS.

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
RUN_DEADLINE_EPOCH=0

aws_c0() {
  aws --profile "$PROFILE" --region "$REGION" \
    --cli-connect-timeout 5 --cli-read-timeout 20 "$@"
}

stop_and_record() {
  if [ "$STARTED" -eq 1 ] && [ "$STOPPED" -eq 0 ]; then
    set +e
    aws_c0 ec2 stop-instances \
      --instance-ids "$INSTANCE" --output json > "$RUN_DIR/stop-request.json"
    while [ "$(date -u +%s)" -le "$RUN_DEADLINE_EPOCH" ]; do
      if aws_c0 ec2 describe-instances --instance-ids "$INSTANCE" \
        --output json > "$RUN_DIR/stopped-instance.json" && \
        python3 - "$RUN_DIR/stopped-instance.json" "$ACCOUNT" "$INSTANCE" <<'PY'
import json,sys
rows=json.load(open(sys.argv[1],encoding='utf-8'))['Reservations']
instances=rows[0]['Instances'] if len(rows)==1 and rows[0]['OwnerId']==sys.argv[2] else []
raise SystemExit(0 if len(instances)==1 and instances[0]['InstanceId']==sys.argv[3] and instances[0]['State']=={'Code':80,'Name':'stopped'} else 1)
PY
      then
        if [ "$(date -u +%s)" -le "$RUN_DEADLINE_EPOCH" ]; then STOPPED=1; fi
        break
      fi
      sleep 5
    done
    set -e
  fi
}
trap stop_and_record EXIT
trap 'exit 130' HUP INT TERM

python3 "$TOOL" prepare --attempt-id "$ATTEMPT" --output-dir "$RUN_DIR"
PREPARED_EPOCH="$(python3 -c 'import datetime,json,sys;v=json.load(open(sys.argv[1]))["prepared_utc"];print(int(datetime.datetime.fromisoformat(v.replace("Z","+00:00")).timestamp()))' "$RUN_DIR/plan.json")"
SEND_DEADLINE_EPOCH=$((PREPARED_EPOCH + 300))
aws_c0 sts get-caller-identity \
  --output json > "$RUN_DIR/caller-identity.json"
aws_c0 ec2 describe-instances \
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

RUN_DEADLINE_EPOCH=$(( $(date -u +%s) + 900 ))
STARTED=1
aws_c0 ec2 start-instances \
  --instance-ids "$INSTANCE" --output json > "$RUN_DIR/start-request.json"

RUNNING=0
while [ "$(date -u +%s)" -lt "$SEND_DEADLINE_EPOCH" ]; do
  if aws_c0 ec2 describe-instances --instance-ids "$INSTANCE" \
    --output json > "$RUN_DIR/running-instance.json" && \
    python3 - "$RUN_DIR/running-instance.json" "$INSTANCE" <<'PY'
import json,sys
rows=json.load(open(sys.argv[1],encoding='utf-8'))['Reservations']
instances=rows[0]['Instances'] if len(rows)==1 else []
raise SystemExit(0 if len(instances)==1 and instances[0]['InstanceId']==sys.argv[2] and instances[0]['State']=={'Code':16,'Name':'running'} else 1)
PY
  then
    RUNNING=1
    break
  fi
  sleep 5
done
test "$RUNNING" -eq 1

ONLINE=0
while [ "$(date -u +%s)" -lt "$SEND_DEADLINE_EPOCH" ]; do
  aws_c0 ssm describe-instance-information \
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
  sleep 5
done
test "$ONLINE" -eq 1
test "$(date -u +%s)" -lt "$SEND_DEADLINE_EPOCH"

SCRIPT_SHA="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["command_script_sha256"])' "$RUN_DIR/plan.json")"
aws_c0 ssm send-command \
  --document-name 'AWS-RunShellScript' --instance-ids "$INSTANCE" \
  --parameters "file://$RUN_DIR/parameters.json" --timeout-seconds 120 \
  --max-concurrency 1 --max-errors 0 --comment "AWS-C0 formal smoke $SCRIPT_SHA" \
  --output json > "$RUN_DIR/send-command.json"
COMMAND_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["Command"]["CommandId"])' "$RUN_DIR/send-command.json")"

COMMAND_DEADLINE_EPOCH=$(( $(date -u +%s) + 180 ))
STOP_RESERVE_EPOCH=$((RUN_DEADLINE_EPOCH - 300))
if [ "$COMMAND_DEADLINE_EPOCH" -gt "$STOP_RESERVE_EPOCH" ]; then COMMAND_DEADLINE_EPOCH="$STOP_RESERVE_EPOCH"; fi
TERMINAL=0
while [ "$(date -u +%s)" -lt "$COMMAND_DEADLINE_EPOCH" ]; do
  if aws_c0 ssm get-command-invocation \
    --command-id "$COMMAND_ID" --instance-id "$INSTANCE" \
    --output json > "$RUN_DIR/invocation.json" 2> "$RUN_DIR/invocation-poll.stderr"; then
    STATUS="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["Status"])' "$RUN_DIR/invocation.json")"
    case "$STATUS" in
      Success|Cancelled|TimedOut|Failed) TERMINAL=1; break ;;
    esac
  fi
  sleep 2
done
test "$TERMINAL" -eq 1

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
aws_c0 s3api put-object \
  --bucket "$BUCKET" --key "$RESULT_KEY" \
  --body "$RUN_DIR/invocation-stdout.jsonl" \
  --content-type 'application/x-ndjson' --metadata "sha256=$STDOUT_SHA" \
  --checksum-algorithm SHA256 --checksum-sha256 "$STDOUT_CHECKSUM" \
  --if-none-match '*' --expected-bucket-owner "$ACCOUNT" \
  --output json > "$RUN_DIR/upload-receipt.json"
VERSION_ID="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["VersionId"])' "$RUN_DIR/upload-receipt.json")"
test -n "$VERSION_ID"
test "$VERSION_ID" != 'null'
aws_c0 s3api get-object \
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
