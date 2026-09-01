#!/usr/bin/env bash
set -Eeuo pipefail

# Infrastructure-only AWS rehearsal. This script deliberately performs no EBU
# scientific configuration and runs no scientific workload.

EXPECTED_INSTANCE_ID="i-048bac00bdb540a4e"
EXPECTED_ROLE_NAME="EBU-Rehearsal-EC2-Role"
EXPECTED_REGION="us-east-1"
S3_BUCKET="ebu-stage-f-results-k7m4p2"
ECR_REPOSITORY="ebu/ebu-stage-f"
AWS_ACCOUNT_ID="623609441658"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${EXPECTED_REGION}.amazonaws.com"

if [[ "${EUID}" -eq 0 ]]; then
  ROOT=()
else
  ROOT=(sudo)
fi

say() {
  printf '\n==> %s\n' "$*"
}

say "Installing base packages"
"${ROOT[@]}" env DEBIAN_FRONTEND=noninteractive apt-get update -qq
"${ROOT[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  ca-certificates curl unzip

say "Verifying the VM from IMDSv2"
IMDS_TOKEN="$(curl -fsS -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600' \
  http://169.254.169.254/latest/api/token)"

INSTANCE_ID="$(curl -fsS \
  -H "X-aws-ec2-metadata-token: ${IMDS_TOKEN}" \
  http://169.254.169.254/latest/meta-data/instance-id)"

INSTANCE_REGION="$(curl -fsS \
  -H "X-aws-ec2-metadata-token: ${IMDS_TOKEN}" \
  http://169.254.169.254/latest/meta-data/placement/region)"

INSTANCE_TYPE="$(curl -fsS \
  -H "X-aws-ec2-metadata-token: ${IMDS_TOKEN}" \
  http://169.254.169.254/latest/meta-data/instance-type)"

if [[ "${INSTANCE_ID}" != "${EXPECTED_INSTANCE_ID}" ]]; then
  printf 'ERROR: expected instance %s, got %s\n' \
    "${EXPECTED_INSTANCE_ID}" "${INSTANCE_ID}" >&2
  exit 1
fi

if [[ "${INSTANCE_REGION}" != "${EXPECTED_REGION}" ]]; then
  printf 'ERROR: expected region %s, got %s\n' \
    "${EXPECTED_REGION}" "${INSTANCE_REGION}" >&2
  exit 1
fi

if [[ "$(uname -m)" != "x86_64" ]]; then
  printf 'ERROR: expected x86_64, got %s\n' "$(uname -m)" >&2
  exit 1
fi

. /etc/os-release
if [[ "${ID}" != "ubuntu" || "${VERSION_ID}" != "24.04" ]]; then
  printf 'ERROR: expected Ubuntu 24.04, got %s %s\n' \
    "${ID}" "${VERSION_ID}" >&2
  exit 1
fi

printf 'Instance: %s\nRegion: %s\nType: %s\nOS: %s\nArchitecture: %s\n' \
  "${INSTANCE_ID}" "${INSTANCE_REGION}" "${INSTANCE_TYPE}" \
  "${PRETTY_NAME}" "$(uname -m)"

say "Installing Docker Engine from Docker's official Ubuntu repository"
"${ROOT[@]}" install -m 0755 -d /etc/apt/keyrings
"${ROOT[@]}" curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
"${ROOT[@]}" chmod a+r /etc/apt/keyrings/docker.asc

{
  printf '%s\n' \
    'Types: deb' \
    'URIs: https://download.docker.com/linux/ubuntu' \
    "Suites: ${UBUNTU_CODENAME:-${VERSION_CODENAME}}" \
    'Components: stable' \
    "Architectures: $(dpkg --print-architecture)" \
    'Signed-By: /etc/apt/keyrings/docker.asc'
} | "${ROOT[@]}" tee /etc/apt/sources.list.d/docker.sources >/dev/null

"${ROOT[@]}" env DEBIAN_FRONTEND=noninteractive apt-get update -qq
"${ROOT[@]}" env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
"${ROOT[@]}" systemctl enable --now docker

say "Testing Docker"
"${ROOT[@]}" docker --version
"${ROOT[@]}" docker info --format 'Docker server {{.ServerVersion}}'
"${ROOT[@]}" docker run --rm hello-world

say "Installing AWS CLI v2"
if ! command -v aws >/dev/null 2>&1; then
  AWS_INSTALL_DIR="$(mktemp -d /tmp/ebu-awscli-install.XXXXXX)"
  curl -fsSL \
    https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip \
    -o "${AWS_INSTALL_DIR}/awscliv2.zip"
  unzip -q "${AWS_INSTALL_DIR}/awscliv2.zip" -d "${AWS_INSTALL_DIR}"
  "${ROOT[@]}" "${AWS_INSTALL_DIR}/aws/install"
fi
aws --version

say "Verifying the EC2 role"
CALLER_ARN="$(aws sts get-caller-identity \
  --region "${EXPECTED_REGION}" \
  --query Arn \
  --output text)"

if [[ "${CALLER_ARN}" != *"assumed-role/${EXPECTED_ROLE_NAME}/"* ]]; then
  printf 'ERROR: expected assumed role %s, got %s\n' \
    "${EXPECTED_ROLE_NAME}" "${CALLER_ARN}" >&2
  exit 1
fi
printf 'Caller ARN: %s\n' "${CALLER_ARN}"

say "Waiting for the narrowly scoped S3 and ECR permissions"
PERMISSIONS_READY=0
for ATTEMPT in {1..24}; do
  if aws s3api get-bucket-location \
      --bucket "${S3_BUCKET}" \
      --region "${EXPECTED_REGION}" >/dev/null 2>&1 \
    && aws ecr describe-repositories \
      --repository-names "${ECR_REPOSITORY}" \
      --region "${EXPECTED_REGION}" >/dev/null 2>&1; then
    PERMISSIONS_READY=1
    break
  fi
  printf 'Permissions not visible yet (attempt %s/24); retrying...\n' \
    "${ATTEMPT}"
  sleep 5
done

if [[ "${PERMISSIONS_READY}" -ne 1 ]]; then
  printf 'ERROR: rehearsal S3/ECR permissions did not become available.\n' >&2
  exit 1
fi

say "Testing read-only ECR repository access and Docker registry authentication"
aws ecr describe-repositories \
  --repository-names "${ECR_REPOSITORY}" \
  --region "${EXPECTED_REGION}" \
  --query 'repositories[0].{URI:repositoryUri,TagMutability:imageTagMutability,Encryption:encryptionConfiguration.encryptionType}' \
  --output table

ECR_IMAGE_COUNT="$(aws ecr list-images \
  --repository-name "${ECR_REPOSITORY}" \
  --region "${EXPECTED_REGION}" \
  --query 'length(imageIds)' \
  --output text)"
printf 'ECR currently contains %s image reference(s).\n' "${ECR_IMAGE_COUNT}"

ECR_DOCKER_CONFIG="/tmp/ebu-rehearsal-ecr-docker-config"
"${ROOT[@]}" install -d -m 0700 "${ECR_DOCKER_CONFIG}"
aws ecr get-login-password --region "${EXPECTED_REGION}" \
  | "${ROOT[@]}" docker --config "${ECR_DOCKER_CONFIG}" login \
      --username AWS \
      --password-stdin "${ECR_REGISTRY}"
"${ROOT[@]}" docker --config "${ECR_DOCKER_CONFIG}" logout \
  "${ECR_REGISTRY}" >/dev/null
printf 'ECR authentication succeeded; the temporary Docker login was removed.\n'

say "Creating a synthetic, non-scientific result"
RUN_TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_PREFIX="rehearsal/${INSTANCE_ID}/${RUN_TIMESTAMP}"
RUN_DIR="$(mktemp -d /tmp/ebu-synthetic-result.XXXXXX)"
RESULT_FILE="${RUN_DIR}/synthetic-result.txt"
CHECKSUM_FILE="${RUN_DIR}/synthetic-result.txt.sha256"

{
  printf 'artifact_type=EBU infrastructure rehearsal synthetic result\n'
  printf 'scientific_configuration=NOT_RUN\n'
  printf 'scientific_workload=NOT_RUN\n'
  printf 'created_at_utc=%s\n' "${RUN_TIMESTAMP}"
  printf 'aws_account_id=%s\n' "${AWS_ACCOUNT_ID}"
  printf 'region=%s\n' "${INSTANCE_REGION}"
  printf 'instance_id=%s\n' "${INSTANCE_ID}"
  printf 'instance_type=%s\n' "${INSTANCE_TYPE}"
  printf 'operating_system=%s\n' "${PRETTY_NAME}"
  printf 'architecture=%s\n' "$(uname -m)"
  printf 'docker_version=%s\n' "$("${ROOT[@]}" docker version --format '{{.Server.Version}}')"
  printf 'aws_cli_version=%s\n' "$(aws --version 2>&1)"
  printf 'ecr_repository=%s\n' "${ECR_REPOSITORY}"
} >"${RESULT_FILE}"

(
  cd "${RUN_DIR}"
  sha256sum synthetic-result.txt >synthetic-result.txt.sha256
)
RESULT_SHA256="$(awk '{print $1}' "${CHECKSUM_FILE}")"
printf 'Synthetic result SHA-256: %s\n' "${RESULT_SHA256}"

S3_URI="s3://${S3_BUCKET}/${RUN_PREFIX}/synthetic-result.txt"
CHECKSUM_S3_URI="${S3_URI}.sha256"

say "Uploading the result and checksum to S3"
aws s3 cp "${RESULT_FILE}" "${S3_URI}" \
  --region "${EXPECTED_REGION}" \
  --sse AES256 \
  --only-show-errors
aws s3 cp "${CHECKSUM_FILE}" "${CHECKSUM_S3_URI}" \
  --region "${EXPECTED_REGION}" \
  --sse AES256 \
  --only-show-errors

say "Checking the stored S3 object"
aws s3api head-object \
  --bucket "${S3_BUCKET}" \
  --key "${RUN_PREFIX}/synthetic-result.txt" \
  --region "${EXPECTED_REGION}" \
  --query '{Bytes:ContentLength,ETag:ETag,VersionId:VersionId,Encryption:ServerSideEncryption,LastModified:LastModified}' \
  --output json

aws s3api list-objects-v2 \
  --bucket "${S3_BUCKET}" \
  --prefix "${RUN_PREFIX}/" \
  --region "${EXPECTED_REGION}" \
  --query 'Contents[].{Key:Key,Bytes:Size,LastModified:LastModified}' \
  --output table

say "Downloading a fresh S3 copy and verifying SHA-256 on the VM"
VERIFY_DIR="$(mktemp -d /tmp/ebu-s3-verify.XXXXXX)"
aws s3 cp "${S3_URI}" "${VERIFY_DIR}/synthetic-result.txt" \
  --region "${EXPECTED_REGION}" \
  --only-show-errors
aws s3 cp "${CHECKSUM_S3_URI}" "${VERIFY_DIR}/synthetic-result.txt.sha256" \
  --region "${EXPECTED_REGION}" \
  --only-show-errors
(
  cd "${VERIFY_DIR}"
  sha256sum --check synthetic-result.txt.sha256
)

printf '\nREHEARSAL_STATUS=SUCCESS\n'
printf 'REHEARSAL_S3_URI=%s\n' "${S3_URI}"
printf 'REHEARSAL_CHECKSUM_S3_URI=%s\n' "${CHECKSUM_S3_URI}"
printf 'REHEARSAL_SHA256=%s\n' "${RESULT_SHA256}"
printf 'REHEARSAL_S3_PREFIX=s3://%s/%s/\n' "${S3_BUCKET}" "${RUN_PREFIX}"
