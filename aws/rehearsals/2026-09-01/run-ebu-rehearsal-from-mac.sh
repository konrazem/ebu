#!/usr/bin/env bash
set -Eeuo pipefail

# Runs the infrastructure-only rehearsal from the Mac. It verifies the target,
# adds least-privilege rehearsal permissions, dispatches the VM script through
# SSM Run Command, and independently verifies the S3 result on the Mac.

EXPECTED_ACCOUNT_ID="623609441658"
INSTANCE_ID="i-048bac00bdb540a4e"
INSTANCE_NAME="EBU-rehearsal-01"
INSTANCE_PROFILE_NAME="EBU-Rehearsal-EC2-Role"
REGION="us-east-1"
S3_BUCKET="ebu-stage-f-results-k7m4p2"
ECR_REPOSITORY="ebu/ebu-stage-f"
INLINE_POLICY_NAME="EBU-Rehearsal-S3-ECR"

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_SCRIPT="${SCRIPT_DIRECTORY}/ebu-rehearsal-vm.sh"

say() {
  printf '\n==> %s\n' "$*"
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

command -v aws >/dev/null 2>&1 || die 'AWS CLI is not installed on the Mac.'
command -v python3 >/dev/null 2>&1 || die 'python3 is required to encode the SSM command.'
command -v shasum >/dev/null 2>&1 || die 'shasum is required for Mac-side SHA-256 verification.'
[[ -f "${VM_SCRIPT}" ]] || die "Missing VM script: ${VM_SCRIPT}"

say "Checking the Mac AWS login"
CALLER_ACCOUNT="$(aws sts get-caller-identity \
  --region "${REGION}" \
  --query Account \
  --output text)"
CALLER_ARN="$(aws sts get-caller-identity \
  --region "${REGION}" \
  --query Arn \
  --output text)"
[[ "${CALLER_ACCOUNT}" == "${EXPECTED_ACCOUNT_ID}" ]] \
  || die "Expected AWS account ${EXPECTED_ACCOUNT_ID}, got ${CALLER_ACCOUNT}."
printf 'AWS account: %s\nCaller: %s\n' "${CALLER_ACCOUNT}" "${CALLER_ARN}"

say "Verifying the exact EC2 instance before making changes"
STATE="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text)"
NAME="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].Tags[?Key==`Name`].Value | [0]' \
  --output text)"
INSTANCE_TYPE="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].InstanceType' \
  --output text)"
ARCHITECTURE="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].Architecture' \
  --output text)"
PROFILE_ARN="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' \
  --output text)"
IMDS_TOKENS="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].MetadataOptions.HttpTokens' \
  --output text)"
SECURITY_GROUP_ID="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text)"
INBOUND_RULE_COUNT="$(aws ec2 describe-security-groups \
  --group-ids "${SECURITY_GROUP_ID}" \
  --region "${REGION}" \
  --query 'length(SecurityGroups[0].IpPermissions)' \
  --output text)"
ROOT_VOLUME_ID="$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query 'Reservations[0].Instances[0].BlockDeviceMappings[0].Ebs.VolumeId' \
  --output text)"
VOLUME_ENCRYPTED="$(aws ec2 describe-volumes \
  --volume-ids "${ROOT_VOLUME_ID}" \
  --region "${REGION}" \
  --query 'Volumes[0].Encrypted' \
  --output text)"

[[ "${STATE}" == "running" ]] || die "Instance state is ${STATE}; expected running."
[[ "${NAME}" == "${INSTANCE_NAME}" ]] || die "Instance Name is ${NAME}; expected ${INSTANCE_NAME}."
[[ "${ARCHITECTURE}" == "x86_64" ]] || die "Architecture is ${ARCHITECTURE}; expected x86_64."
[[ "${PROFILE_ARN}" == */"${INSTANCE_PROFILE_NAME}" ]] \
  || die "Unexpected instance profile: ${PROFILE_ARN}."
[[ "${IMDS_TOKENS}" == "required" ]] || die "IMDSv2 tokens are not required."
[[ "${INBOUND_RULE_COUNT}" == "0" ]] || die "Security group ${SECURITY_GROUP_ID} has inbound rules."
[[ "${VOLUME_ENCRYPTED}" == "True" || "${VOLUME_ENCRYPTED}" == "true" ]] \
  || die "Root volume ${ROOT_VOLUME_ID} is not encrypted."

printf 'Name: %s\nState: %s\nType: %s\nArchitecture: %s\n' \
  "${NAME}" "${STATE}" "${INSTANCE_TYPE}" "${ARCHITECTURE}"
printf 'Role profile: %s\nIMDSv2 required: %s\nInbound rules: %s\nEncrypted root volume: %s\n' \
  "${PROFILE_ARN}" "${IMDS_TOKENS}" "${INBOUND_RULE_COUNT}" "${ROOT_VOLUME_ID}"

say "Applying the least-privilege rehearsal policy to the EC2 role"
POLICY_FILE="$(mktemp /tmp/ebu-rehearsal-policy.XXXXXX)"
PARAMETERS_FILE="$(mktemp /tmp/ebu-rehearsal-parameters.XXXXXX)"

cleanup_control_files() {
  rm -f "${POLICY_FILE}" "${PARAMETERS_FILE}"
}
trap cleanup_control_files EXIT

cat >"${POLICY_FILE}" <<'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadBucketLocation",
      "Effect": "Allow",
      "Action": "s3:GetBucketLocation",
      "Resource": "arn:aws:s3:::ebu-stage-f-results-k7m4p2"
    },
    {
      "Sid": "ListOnlyTheRehearsalPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::ebu-stage-f-results-k7m4p2",
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "rehearsal",
            "rehearsal/*"
          ]
        }
      }
    },
    {
      "Sid": "ReadAndWriteOnlyRehearsalObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::ebu-stage-f-results-k7m4p2/rehearsal/*"
    },
    {
      "Sid": "AuthenticateToECR",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "ReadOnlyAccessToTheSpecificECRRepository",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ecr:DescribeRepositories",
        "ecr:GetDownloadUrlForLayer",
        "ecr:ListImages"
      ],
      "Resource": "arn:aws:ecr:us-east-1:623609441658:repository/ebu/ebu-stage-f"
    }
  ]
}
POLICY

aws iam put-role-policy \
  --role-name "${INSTANCE_PROFILE_NAME}" \
  --policy-name "${INLINE_POLICY_NAME}" \
  --policy-document "file://${POLICY_FILE}"

aws iam get-role-policy \
  --role-name "${INSTANCE_PROFILE_NAME}" \
  --policy-name "${INLINE_POLICY_NAME}" \
  --query '{Role:RoleName,Policy:PolicyName}' \
  --output table

say "Encoding and dispatching the VM automation through SSM Run Command"
python3 - "${VM_SCRIPT}" "${PARAMETERS_FILE}" <<'PYTHON'
import base64
import json
import pathlib
import sys

script_path = pathlib.Path(sys.argv[1])
parameters_path = pathlib.Path(sys.argv[2])
encoded = base64.b64encode(script_path.read_bytes()).decode("ascii")
command = "printf '%s' '{}' | base64 -d | bash".format(encoded)
parameters_path.write_text(json.dumps({"commands": [command]}), encoding="utf-8")
PYTHON

COMMAND_ID="$(aws ssm send-command \
  --instance-ids "${INSTANCE_ID}" \
  --document-name AWS-RunShellScript \
  --comment 'EBU infrastructure-only rehearsal; no scientific configuration' \
  --parameters "file://${PARAMETERS_FILE}" \
  --timeout-seconds 1800 \
  --region "${REGION}" \
  --query 'Command.CommandId' \
  --output text)"
printf 'SSM command ID: %s\n' "${COMMAND_ID}"

say "Waiting for the VM automation to finish"
DEADLINE="$(( $(date +%s) + 1800 ))"
STATUS="Pending"
while [[ "$(date +%s)" -lt "${DEADLINE}" ]]; do
  STATUS="$(aws ssm get-command-invocation \
    --command-id "${COMMAND_ID}" \
    --instance-id "${INSTANCE_ID}" \
    --region "${REGION}" \
    --query Status \
    --output text 2>/dev/null || printf 'Pending')"
  printf 'SSM status: %s\n' "${STATUS}"
  case "${STATUS}" in
    Success|Cancelled|TimedOut|Failed|Cancelling)
      break
      ;;
  esac
  sleep 5
done

STANDARD_OUTPUT="$(aws ssm get-command-invocation \
  --command-id "${COMMAND_ID}" \
  --instance-id "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query StandardOutputContent \
  --output text 2>/dev/null || true)"
STANDARD_ERROR="$(aws ssm get-command-invocation \
  --command-id "${COMMAND_ID}" \
  --instance-id "${INSTANCE_ID}" \
  --region "${REGION}" \
  --query StandardErrorContent \
  --output text 2>/dev/null || true)"

printf '\n----- VM standard output -----\n%s\n' "${STANDARD_OUTPUT}"
if [[ -n "${STANDARD_ERROR}" && "${STANDARD_ERROR}" != "None" ]]; then
  printf '\n----- VM standard error -----\n%s\n' "${STANDARD_ERROR}" >&2
fi

[[ "${STATUS}" == "Success" ]] || die "SSM command ended with status ${STATUS}."

S3_URI="$(printf '%s\n' "${STANDARD_OUTPUT}" \
  | awk -F= '/^REHEARSAL_S3_URI=/{print substr($0, index($0, "=") + 1)}' \
  | tail -n 1)"
EXPECTED_SHA256="$(printf '%s\n' "${STANDARD_OUTPUT}" \
  | awk -F= '/^REHEARSAL_SHA256=/{print substr($0, index($0, "=") + 1)}' \
  | tail -n 1)"

[[ "${S3_URI}" == s3://"${S3_BUCKET}"/rehearsal/* ]] \
  || die "Unexpected or missing S3 result URI: ${S3_URI}"
[[ "${EXPECTED_SHA256}" =~ ^[0-9a-f]{64}$ ]] \
  || die 'The VM did not return a valid SHA-256 hash.'

say "Independently downloading and hashing the result on the Mac"
MAC_VERIFY_DIRECTORY="$(mktemp -d /tmp/ebu-rehearsal-mac-verify.XXXXXX)"
MAC_RESULT_FILE="${MAC_VERIFY_DIRECTORY}/synthetic-result.txt"
aws s3 cp "${S3_URI}" "${MAC_RESULT_FILE}" \
  --region "${REGION}" \
  --only-show-errors
MAC_SHA256="$(shasum -a 256 "${MAC_RESULT_FILE}" | awk '{print $1}')"

[[ "${MAC_SHA256}" == "${EXPECTED_SHA256}" ]] \
  || die "Hash mismatch: VM ${EXPECTED_SHA256}; Mac ${MAC_SHA256}."

S3_KEY="${S3_URI#s3://${S3_BUCKET}/}"
aws s3api head-object \
  --bucket "${S3_BUCKET}" \
  --key "${S3_KEY}" \
  --region "${REGION}" \
  --query '{Bytes:ContentLength,ETag:ETag,VersionId:VersionId,Encryption:ServerSideEncryption,LastModified:LastModified}' \
  --output json

printf '\nREHEARSAL COMPLETE\n'
printf 'S3 result: %s\n' "${S3_URI}"
printf 'SHA-256:  %s\n' "${EXPECTED_SHA256}"
printf 'Mac copy: %s\n' "${MAC_RESULT_FILE}"
printf 'The VM and Mac hashes match. No EBU scientific configuration was run.\n'
printf '\nThe instance is still running. To stop compute billing, run:\n'
printf 'aws ec2 stop-instances --instance-ids %s --region %s\n' \
  "${INSTANCE_ID}" "${REGION}"

