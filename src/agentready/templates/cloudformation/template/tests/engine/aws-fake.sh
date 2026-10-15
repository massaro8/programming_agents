#!/usr/bin/env bash
# AWS CLI simulator: no network, credentials or real AWS executable.
set -euo pipefail
printf '%s\n' "$*" >>"$MOCK_LOG"
[[ $1 != --cli-connect-timeout ]] || shift 4
service=$1 operation=$2
shift 2
query='' stack=''
while (($#)); do
  case $1 in --query) query=$2; shift 2 ;; --stack-name) stack=$2; shift 2 ;; *) shift ;; esac
done
case "$service/$operation" in
  sts/get-caller-identity) printf '%s\t%s\r\n' "${MOCK_ACCOUNT:-123456789012}" "${MOCK_IDENTITY:-arn:aws:sts::123456789012:assumed-role/deploy/session}" ;;
  cloudformation/validate-template) printf '%b\n' "${MOCK_PARAMETERS:-EnvironmentName\tNone\tFalse}" ;;
  cloudformation/describe-stacks)
    if [[ ${MOCK_DENIED:-0} == 1 ]]; then echo 'AccessDenied' >&2; exit 1; fi
    if [[ ${MOCK_MISSING:-0} == 1 ]]; then echo 'ValidationError: Stack does not exist' >&2; exit 1; fi
    if [[ $query == *RoleARN* ]]; then printf "%s\n" "${MOCK_EXECUTION_ROLE:-arn:aws:iam::123456789012:role/execute}"; exit 0; fi
    if [[ $query == *Outputs* ]]; then printf '%b\n' "${MOCK_OUTPUTS:-NetworkId\tvpc-example}"
    else printf '%s\r\n' "${MOCK_STATUS:-UPDATE_COMPLETE}"; fi ;;
  cloudformation/create-change-set) printf '%s\n' 'arn:aws:cloudformation:eu-west-1:123456789012:changeSet/review/unique' ;;
  cloudformation/describe-change-set)
    case $query in
      Status) printf '%s\n' "${MOCK_CHANGE_STATUS:-CREATE_COMPLETE}" ;;
      StackName) printf '%s\n' project-sandbox-artifact-storage ;;
      ExecutionStatus) echo EXECUTE_COMPLETE ;;
      '[Status,ExecutionStatus]') printf 'CREATE_COMPLETE\tAVAILABLE\n' ;;
      *StatusReason*) printf '%s\n' "${MOCK_EMPTY:-False}" ;;
      length*) printf '%s\n' "${MOCK_UNSUPPORTED:-0}" ;;
      *) printf '%b\n' "${MOCK_CHANGES:-Modify\tArtifacts\tAWS::S3::Bucket\tFalse}" ;;
    esac ;;
  cloudformation/execute-change-set) [[ ${MOCK_EXECUTION_FAILURE:-0} == 0 ]] ;;
  *) echo "Unexpected fake AWS operation: $service/$operation" >&2; exit 99 ;;
esac
