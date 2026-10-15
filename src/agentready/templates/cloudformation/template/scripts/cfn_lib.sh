#!/usr/bin/env bash
# Standalone offline catalog and AWS helpers. Requires Bash 4+ and coreutils.
set -euo pipefail
export LC_ALL=C
# Prevent Git Bash argument rewriting of IAM paths and file:// URIs.
export MSYS_NO_PATHCONV=1
native_path() { if command -v cygpath >/dev/null; then cygpath -m "$1"; else printf "%s" "$1"; fi; }
log() { printf '%s\n' "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }
[[ ${BASH_VERSINFO[0]} -ge 4 ]] || die 'Bash 4+ required (Git Bash on Windows).'

# Paths are relative to the infrastructure root. Never follow symlinks.
safe_file() {
  local p=$1 part current=.
  [[ $p != /* && $p != *..* && $p != *//* && $p != *\\* ]] || die "Unsafe path: $p"
  IFS=/ read -r -a parts <<<"$p"
  for part in "${parts[@]}"; do
    [[ -n $part && $part != . ]] || die "Unsafe path component: $p"
    current+="/$part"
    [[ ! -L $current ]] || die "Symlink forbidden: $p"
  done
  [[ -f $p ]] || die "Missing file: $p"
}

load_catalog() {
  safe_file stacks/catalog.conf
  cat_stage=() cat_id=() cat_template=() cat_envs=()
  local line stage sid template envs extra last='' e seen_env
  declare -A seen=() paths=()
  while IFS= read -r line || [[ -n $line ]]; do
    line=${line%$'\r'}
    [[ $line =~ ^[[:space:]]*(#|$) ]] && continue
    read -r stage sid template envs extra <<<"$line"
    [[ -n $envs && -z $extra ]] || die 'Catalog requires four fields: stage stack-id template environments'
    [[ $stage =~ ^[0-9]{2}-[a-z][a-z0-9-]*$ ]] || die "Invalid stage: $stage"
    [[ -z $last || $stage == "$last" || $stage > $last ]] || die "Catalog stage order: $stage after $last"
    [[ $sid =~ ^[a-z][a-z0-9-]*$ && ${#sid} -le 64 ]] || die "Invalid stack identifier: $sid"
    [[ -z ${seen[$sid]+x} ]] || die "Duplicate stack: $sid"
    [[ $template =~ ^stacks/[A-Za-z0-9_./-]+\.(yaml|yml)$ ]] || die "Invalid template path: $template"
    safe_file "$template"
    [[ -z ${paths[$template]+x} ]] || die "Duplicate template: $template"
    [[ $(wc -c <"$template") -le 51200 ]] || die "Template exceeds inline 51200-byte limit: $template"
    if [[ $envs != - ]]; then
      [[ $envs =~ ^[a-z][a-z0-9-]*(,[a-z][a-z0-9-]*)*$ ]] || die "Invalid environments: $envs"
      seen_env=,
      IFS=, read -r -a environments <<<"$envs"
      for e in "${environments[@]}"; do
        [[ $seen_env != *",$e,"* ]] || die "Duplicate environment: $e"
        seen_env+="$e,"
      done
    fi
    seen[$sid]=1 paths[$template]=1
    cat_stage+=("$stage") cat_id+=("$sid") cat_template+=("$template") cat_envs+=("$envs")
    last=$stage
  done <stacks/catalog.conf
  ((${#cat_id[@]})) || die 'Catalog is empty'
}

aws() { command aws --cli-connect-timeout 10 --cli-read-timeout 60 "$@" | tr -d '\r'; }
healthy() { [[ $1 =~ ^((CREATE|UPDATE|IMPORT)_COMPLETE|UPDATE_ROLLBACK_COMPLETE)$ ]]; }
stack_status() {
  local result
  if result=$(aws cloudformation describe-stacks --stack-name "$1" --query 'Stacks[0].StackStatus' --output text 2>"$work/error"); then
    printf '%s' "$result"
  elif [[ $(cat "$work/error") == *'ValidationError'* && $(cat "$work/error") == *'does not exist'* ]]; then
    printf NONE
  else
    die "Cannot inspect stack $1 (access/network error; not treated as absence)"
  fi
}

# Never print output values or resolved parameter values. No remote secret retrieval.
build_parameters() {
  local idx=$1 key default noecho j status rows value source
  declare -A owners=() values=()
  for ((j=0; j<idx; j++)); do
    source="$namespace-$environment-${cat_id[j]}"
    status=$(stack_status "$source") || return 1
    if [[ $status == NONE ]]; then log "Upstream $source: missing"; continue; fi
    healthy "$status" || die "Upstream $source: unhealthy ($status)"
    rows=$(aws cloudformation describe-stacks --stack-name "$source" --query 'Stacks[0].Outputs[].[OutputKey,OutputValue]' --output text) || die "Upstream $source: outputs unavailable"
    while IFS=$'\t' read -r key value; do
      [[ -n $key && $key != None ]] || continue
      [[ $key =~ ^[A-Za-z][A-Za-z0-9]*$ && -n $value && $value != None ]] || die "Invalid output contract on $source"
      [[ -z ${owners[$key]+x} ]] || die "Ambiguous output contract: $key"
      owners[$key]=$source values[$key]=$value
    done <<<"$rows"
  done
  rows=$(aws cloudformation validate-template --template-body "file://${cat_template[idx]}" --query 'Parameters[].[ParameterKey,DefaultValue,NoEcho]' --output text) || die 'Template validation failed'
  printf '[' >"$work/parameters.json"
  local sep='' resolved
  while IFS=$'\t' read -r key default noecho; do
    [[ -n $key && $key != None ]] || continue
    [[ $key =~ ^[A-Za-z][A-Za-z0-9]*$ ]] || die 'Invalid parameter key'
    resolved=''
    if [[ $key == EnvironmentName ]]; then resolved=$environment
    elif [[ -n ${owners[$key]+x} ]]; then
      [[ $noecho != True && $noecho != true ]] || die "Secret parameter $key must not use Outputs"
      resolved=${values[$key]}
    elif [[ $default != None ]]; then continue
    else die "Missing required input $key (no upstream output or default)"; fi
    # JSON string encoding without external parser: reject controls, escape quotes/backslashes.
    [[ $resolved != *[$'\001'-$'\037']* ]] || die "Unsupported control character in input $key"
    resolved=${resolved//\\/\\\\}; resolved=${resolved//\"/\\\"}
    printf '%s{"ParameterKey":"%s","ParameterValue":"%s"}' "$sep" "$key" "$resolved" >>"$work/parameters.json"
    sep=,
  done <<<"$rows"
  printf ']\n' >>"$work/parameters.json"
}

inspect_change_set() {
  local arn=$1 rows action logical type replacement count=0
  rows=$(aws cloudformation describe-change-set --change-set-name "$arn" --query 'Changes[].ResourceChange.[Action,LogicalResourceId,ResourceType,Replacement]' --output text) || die 'Cannot inspect change set'
  [[ -n $rows && $rows != None ]] || die 'Empty change set; nothing executable'
  while IFS=$'\t' read -r action logical type replacement; do
    [[ -n $action ]] || continue
    count=$((count+1))
    log "$action $logical $type replacement=$replacement"
    [[ $type != AWS::IAM::* && $type != AWS::EC2::* && $type != AWS::S3::* && $type != AWS::KMS::* ]] || log 'SECURITY REVIEW REQUIRED: permissions, networking, storage or key changes'
    case $action in
      Add) [[ $replacement == None || $replacement == False ]] || die 'Unexpected Add replacement metadata' ;;
      Modify) [[ $replacement == False ]] || die 'Replacement risk requires separate procedure' ;;
      *) die 'Deletion/import/unknown action requires separate procedure' ;;
    esac
  done <<<"$rows"
  ((count)) || die 'No resource changes'
  # Nested changes and non-resource changes are outside this deliberately small runner.
  local unsupported
  unsupported=$(aws cloudformation describe-change-set --change-set-name "$arn" --query "length(Changes[?Type!='Resource' || ResourceChange.ResourceType=='AWS::CloudFormation::Stack'])" --output text) || die 'Cannot check change types'
  [[ $unsupported == 0 ]] || die 'Nested/non-resource changes require separate procedure'
}
