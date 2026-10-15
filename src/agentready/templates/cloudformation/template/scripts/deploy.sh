#!/usr/bin/env bash
# Optional CI workflow; never called by init/bootstrap/check/verify/default CI.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd -- "$repo"
source scripts/cfn_lib.sh
[[ ! -d infrastructure ]] || cd infrastructure
load_catalog
mode=${1:-} environment=${2:-}
if [[ $mode == catalog && $# == 1 ]]; then log 'Catalog valid'; exit 0; fi
case $mode in
  inspect) (($# == 2)) || die 'Usage: deploy.sh inspect <environment>' ;;
  plan) (($# == 4)) && [[ $4 == --authorize-plan ]] || die 'Usage: deploy.sh plan <environment> <stack-id> --authorize-plan (AWS write)' ;;
  execute) (($# == 5)) && [[ $4 == --authorize-execution && $5 == "$3" ]] || die 'Usage: deploy.sh execute <environment> <change-set-arn> --authorize-execution <same-arn>' ;;
  *) die 'Deployment disabled by default. Commands: catalog, inspect, plan, execute; see ENGINEERING.md' ;;
esac
[[ $environment =~ ^[a-z][a-z0-9-]*$ ]] || die 'Explicit environment required'
safe_file deployment/environments.conf
# branch environment account-variable region role-variable execution-role-variable namespace
found=0
line_no=0
declare -A branches=() env_names=()
while IFS= read -r line || [[ -n $line ]]; do
  line=${line%$'\r'}
  [[ $line =~ ^[[:space:]]*(#|$) ]] && continue
  read -r branch env account_ref region role_ref execution_ref prefix extra <<<"$line"
  [[ -n $prefix && -z $extra ]] || die 'Deployment configuration requires seven columns'
  [[ $branch =~ ^[A-Za-z0-9][A-Za-z0-9/_.-]*$ && $env =~ ^[a-z][a-z0-9-]*$ && $prefix =~ ^[a-z][a-z0-9-]*$ && ${#prefix} -le 24 ]] || die 'Invalid branch/environment/namespace'
  [[ -z ${branches[$branch]+x} && -z ${env_names[$env]+x} ]] || die 'Duplicate branch/environment configuration'
  branches[$branch]=1 env_names[$env]=1
  for ref in "$account_ref" "$role_ref" "$execution_ref"; do
    [[ $ref =~ ^[A-Z][A-Z0-9_]*$ ]] || die 'Invalid deployment variable reference'
  done
  [[ $region =~ ^[a-z]{2}(-[a-z]+)+-[0-9]+$ ]] || die 'Invalid configured region'
  if [[ $env == "$environment" ]]; then
    expected_branch=$branch expected_region=$region namespace=$prefix
    account=${!account_ref:-} role=${!role_ref:-} execution_role=${!execution_ref:-}
    found=1
  fi
done <deployment/environments.conf
((found)) || die 'Deployment workflow is unconfigured for this environment'
for envs in "${cat_envs[@]}"; do
  [[ $envs != - ]] || continue
  IFS=, read -r -a names <<<"$envs"
  for e in "${names[@]}"; do [[ -n ${env_names[$e]+x} ]] || die "Unknown catalog environment: $e"; done
done
[[ ${BITBUCKET_BRANCH:-} == "$expected_branch" && ${BITBUCKET_DEPLOYMENT_ENVIRONMENT:-} == "$environment" ]] || die 'Branch/deployment environment mismatch'
[[ ${AWS_REGION:-} == "$expected_region" && ${AWS_DEFAULT_REGION:-$expected_region} == "$expected_region" ]] || die 'Region mismatch or missing AWS_REGION'
[[ $account =~ ^[0-9]{12}$ ]] || die 'Missing expected account reference'
[[ $role =~ ^arn:(aws|aws-us-gov|aws-cn):iam::$account:role/[A-Za-z0-9/+=,.@_-]+$ ]] || die 'Missing/invalid DeploymentRole ARN'
partition=${BASH_REMATCH[1]}
[[ $execution_role =~ ^arn:$partition:iam::$account:role/[A-Za-z0-9/+=,.@_-]+$ && $execution_role != "$role" ]] || die 'Separate same-account ExecutionRole required'
for key in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_DEFAULT_PROFILE AWS_SECURITY_TOKEN AWS_WEB_IDENTITY_TOKEN_FILE; do
  [[ -z ${!key:-} ]] || die "Inherited credential source forbidden: $key"
done
[[ -n ${BITBUCKET_STEP_OIDC_TOKEN:-} ]] || die 'Missing Bitbucket OIDC token; configure oidc: true and deployment'
command -v aws >/dev/null || die 'Missing AWS CLI v2'
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
umask 077
printf '%s' "$BITBUCKET_STEP_OIDC_TOKEN" >"$work/token"
# Isolate shared credentials/config and alternate endpoint settings.
export AWS_CONFIG_FILE="$(native_path "$work/config")" AWS_SHARED_CREDENTIALS_FILE="$(native_path "$work/credentials")"
export AWS_ROLE_ARN="$role" AWS_WEB_IDENTITY_TOKEN_FILE="$(native_path "$work/token")" AWS_ROLE_SESSION_NAME=repository-reviewed
export AWS_EC2_METADATA_DISABLED=true AWS_PAGER='' AWS_DEFAULT_REGION="$expected_region" AWS_IGNORE_CONFIGURED_ENDPOINT_URLS=true
unset AWS_ENDPOINT_URL AWS_ENDPOINT_URL_STS AWS_ENDPOINT_URL_CLOUDFORMATION
identity=$(aws sts get-caller-identity --query '[Account,Arn]' --output text) || die 'OIDC authentication failed'
read -r actual_account actual_arn <<<"$identity"
role_name=${role##*/}
[[ $actual_account == "$account" && $actual_arn == "arn:$partition:sts::$account:assumed-role/$role_name/"* ]] || die 'Unexpected assumed account/role identity'
if [[ $mode == inspect ]]; then
  for sid in "${cat_id[@]}"; do
    status=$(stack_status "$namespace-$environment-$sid") || exit 1
    log "$sid: $status"
  done
  exit 0
fi
if [[ $mode == plan ]]; then
  idx=-1
  for i in "${!cat_id[@]}"; do [[ ${cat_id[i]} != "$3" ]] || idx=$i; done
  ((idx >= 0)) || die 'Stack not in catalog'
  [[ ,${cat_envs[idx]}, == *",$environment,"* ]] || die 'Stack disabled for environment'
  stack="$namespace-$environment-${cat_id[idx]}"
  build_parameters "$idx"
  status=$(stack_status "$stack") || exit 1
  if [[ $status == NONE ]]; then change_type=CREATE
  elif healthy "$status"; then change_type=UPDATE
  else die "Target stack unhealthy: $status"; fi
  # IAM capabilities require an explicit variable set only after policy review.
  caps=()
  if [[ ${CFN_REVIEWED_IAM:-} == yes ]]; then caps=(--capabilities CAPABILITY_NAMED_IAM); fi
  arn=$(aws cloudformation create-change-set --stack-name "$stack" --change-set-name "review-$(date -u +%Y%m%d%H%M%S)-$RANDOM" --change-set-type "$change_type" --template-body "file://${cat_template[idx]}" --parameters "file://$(native_path "$work/parameters.json")" --role-arn "$execution_role" "${caps[@]}" --query Id --output text) || die 'Change-set creation failed'
  deadline=$((SECONDS+600))
  while :; do
    state=$(aws cloudformation describe-change-set --change-set-name "$arn" --query Status --output text) || die 'Cannot inspect change-set status'
    case $state in
      CREATE_COMPLETE) break ;;
      FAILED)
        # Classify empty change sets without printing service messages containing values.
        empty=$(aws cloudformation describe-change-set --change-set-name "$arn" --query "contains(StatusReason, \`\"didn't contain changes\"\`) || contains(StatusReason, \`\"No updates are to be performed\"\`)" --output text) || die 'Cannot inspect failure'
        [[ $empty == True || $empty == true ]] && { log 'Empty change set: no changes; nothing executed'; exit 0; }
        die 'Change-set creation failed; inspect in the AWS console' ;;
      CREATE_PENDING|CREATE_IN_PROGRESS) ;;
      *) die "Unexpected change-set status: $state" ;;
    esac
    ((SECONDS < deadline)) || die 'Change-set creation timeout'
    sleep 5
  done
  log "Review change set: $arn"
  inspect_change_set "$arn"
  log 'Plan only. Review every Modify and security effect, then separately authorize this exact ARN.'
  exit 0
fi
arn=$3
[[ $arn == "arn:$partition:cloudformation:$expected_region:$account:changeSet/"* ]] || die 'Change-set ARN account/region mismatch'
stack=$(aws cloudformation describe-change-set --change-set-name "$arn" --query StackName --output text) || die 'Cannot identify change-set stack'
selected=0
for i in "${!cat_id[@]}"; do
  if [[ $stack == "$namespace-$environment-${cat_id[i]}" && ,${cat_envs[i]}, == *",$environment,"* ]]; then selected=1; fi
done
((selected)) || die 'Change-set stack is not enabled in catalog'
state=$(aws cloudformation describe-change-set --change-set-name "$arn" --query '[Status,ExecutionStatus]' --output text) || die 'Cannot inspect change-set execution contract'
[[ $state == $'CREATE_COMPLETE\tAVAILABLE' ]] || die 'Change set unavailable'
actual_execution_role=$(aws cloudformation describe-stacks --stack-name "$stack" --query 'Stacks[0].RoleARN' --output text) || die 'Cannot inspect stack ExecutionRole'
[[ $actual_execution_role == "$execution_role" ]] || die 'Unexpected stack ExecutionRole; use the separately authorized role migration procedure'
inspect_change_set "$arn"
aws cloudformation execute-change-set --change-set-name "$arn" --no-disable-rollback >/dev/null || die 'Change-set execution failed'
deadline=$((SECONDS+3600))
while :; do
  status=$(stack_status "$stack") || exit 1
  case $status in
    CREATE_COMPLETE|UPDATE_COMPLETE|IMPORT_COMPLETE)
      execution=$(aws cloudformation describe-change-set --change-set-name "$arn" --query ExecutionStatus --output text) || die "Cannot inspect execution result"
      if [[ $execution == EXECUTE_COMPLETE ]]; then log "$stack: $status"; exit 0; fi ;;
    *_IN_PROGRESS) ;;
    *) die "Stack failed or rolled back: $status; later stacks must not run" ;;
  esac
  ((SECONDS < deadline)) || die 'Stack completion timeout; inspect AWS before any retry'
  sleep 10
done
