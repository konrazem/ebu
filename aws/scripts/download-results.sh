#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_ACCOUNT_ID="623609441658"
EXPECTED_BUCKET="ebu-stage-f-results-k7m4p2"
DEFAULT_REGION="us-east-1"

usage() {
  cat <<'USAGE'
Usage:
  download-results.sh S3_PREFIX DESTINATION [REGION]

Example:
  download-results.sh \
    s3://ebu-stage-f-results-k7m4p2/rehearsal/i-048bac00bdb540a4e/20260901T110354Z/ \
    "$HOME/Downloads/ebu-rehearsal-20260901"

The S3 prefix must be below rehearsal/ or campaigns/. The destination must be
absent or empty. The script downloads without deleting remote or local files
and requires at least one valid .sha256 checksum file.
USAGE
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  usage >&2
  exit 2
fi

S3_PREFIX="$1"
DESTINATION="$2"
REGION="${3:-${DEFAULT_REGION}}"

command -v aws >/dev/null 2>&1 || fail 'AWS CLI is not installed.'

case "${S3_PREFIX}" in
  "s3://${EXPECTED_BUCKET}/rehearsal/"*|"s3://${EXPECTED_BUCKET}/campaigns/"*)
    ;;
  *)
    fail "S3 prefix must be inside s3://${EXPECTED_BUCKET}/rehearsal/ or campaigns/."
    ;;
esac

[[ "${S3_PREFIX}" == */ ]] \
  || fail 'S3_PREFIX must end with / so a complete result prefix is retrieved.'

if [[ -e "${DESTINATION}" ]]; then
  [[ -d "${DESTINATION}" ]] || fail 'Destination exists and is not a directory.'
  if find "${DESTINATION}" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    fail 'Destination exists and is not empty; refusing to overwrite files.'
  fi
else
  mkdir -p "${DESTINATION}"
fi

CALLER_ACCOUNT="$(aws sts get-caller-identity \
  --region "${REGION}" \
  --query Account \
  --output text)"
[[ "${CALLER_ACCOUNT}" == "${EXPECTED_ACCOUNT_ID}" ]] \
  || fail "Expected AWS account ${EXPECTED_ACCOUNT_ID}, got ${CALLER_ACCOUNT}."

CALLER_ARN="$(aws sts get-caller-identity \
  --region "${REGION}" \
  --query Arn \
  --output text)"
if [[ "${CALLER_ARN}" == "arn:aws:iam::${EXPECTED_ACCOUNT_ID}:root" ]]; then
  printf '%s\n' \
    'WARNING: using the temporary AWS root browser session for read-only retrieval.' \
    'Create a named identity with MFA before routine campaign administration.' >&2
fi

printf 'Downloading %s\n' "${S3_PREFIX}"
aws s3 cp "${S3_PREFIX}" "${DESTINATION}/" \
  --recursive \
  --region "${REGION}" \
  --only-show-errors

if command -v sha256sum >/dev/null 2>&1; then
  HASH_COMMAND=(sha256sum --check)
elif command -v shasum >/dev/null 2>&1; then
  HASH_COMMAND=(shasum -a 256 --check)
else
  fail 'Neither sha256sum nor shasum is available.'
fi

CHECKSUM_COUNT=0
while IFS= read -r -d '' CHECKSUM_FILE; do
  CHECKSUM_COUNT="$((CHECKSUM_COUNT + 1))"
  CHECKSUM_DIRECTORY="$(dirname "${CHECKSUM_FILE}")"
  CHECKSUM_BASENAME="$(basename "${CHECKSUM_FILE}")"
  (
    cd "${CHECKSUM_DIRECTORY}"
    "${HASH_COMMAND[@]}" "${CHECKSUM_BASENAME}"
  )
done < <(find "${DESTINATION}" -type f -name '*.sha256' -print0)

[[ "${CHECKSUM_COUNT}" -gt 0 ]] \
  || fail 'No .sha256 checksum file was downloaded; refusing to report success.'

printf 'DOWNLOAD_STATUS=SUCCESS\n'
printf 'SOURCE=%s\n' "${S3_PREFIX}"
printf 'DESTINATION=%s\n' "${DESTINATION}"
printf 'VERIFIED_CHECKSUM_FILES=%s\n' "${CHECKSUM_COUNT}"
