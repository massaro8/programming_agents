#!/usr/bin/env bash
# Exercise a disposable copy only. AWS is always replaced by the bundled simulator.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
[[ ! -d "$repo/infrastructure" ]] || repo="$repo/infrastructure"
# Hybrid puts tests under infrastructure but scripts remain at repository root.
scripts="$repo/scripts"
[[ -d $scripts ]] || scripts="$repo/../scripts"
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
mkdir -p "$work/project/scripts" "$work/project/stacks/storage" "$work/project/deployment" "$work/bin"
cp "$scripts/cfn_lib.sh" "$scripts/deploy.sh" "$work/project/scripts/"
cp "$repo/tests/engine/aws-fake.sh" "$work/bin/aws"
chmod +x "$work/bin/aws"
export PATH="$work/bin:$PATH" MOCK_LOG="$work/aws.log"
export BITBUCKET_BRANCH=sandbox BITBUCKET_DEPLOYMENT_ENVIRONMENT=sandbox AWS_REGION=eu-west-1
export BITBUCKET_STEP_OIDC_TOKEN=synthetic-offline-token
export SANDBOX_ACCOUNT=123456789012 SANDBOX_DEPLOYMENT_ROLE=arn:aws:iam::123456789012:role/deploy SANDBOX_EXECUTION_ROLE=arn:aws:iam::123456789012:role/execute
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE AWS_DEFAULT_PROFILE AWS_SECURITY_TOKEN AWS_WEB_IDENTITY_TOKEN_FILE AWS_DEFAULT_REGION
cd "$work/project"
printf '%s\n' 'sandbox sandbox SANDBOX_ACCOUNT eu-west-1 SANDBOX_DEPLOYMENT_ROLE SANDBOX_EXECUTION_ROLE project' >deployment/environments.conf
printf '%s\n' 'Resources: {}' >stacks/storage/example.yaml
catalog() { printf '%s\n' '03-storage artifact-storage stacks/storage/example.yaml sandbox' >stacks/catalog.conf; }
pass() { bash scripts/deploy.sh "$@" >"$work/result" 2>&1 || { cat "$work/result"; exit 1; }; }
fail() { if bash scripts/deploy.sh "$@" >"$work/result" 2>&1; then echo "Unexpected success: $*"; exit 1; fi; }
expect() { grep -q "$1" "$work/result" || { cat "$work/result"; exit 1; }; }
arn=arn:aws:cloudformation:eu-west-1:123456789012:changeSet/review/unique
catalog
pass catalog
fail
expect 'disabled by default'
cp deployment/environments.conf "$work/config"
printf '# unconfigured\n' >deployment/environments.conf
fail inspect sandbox
expect unconfigured
cp "$work/config" deployment/environments.conf
pass inspect sandbox
BITBUCKET_BRANCH=unknown fail inspect sandbox
expect mismatch
AWS_REGION=us-east-1 fail inspect sandbox
expect mismatch
MOCK_ACCOUNT=999999999999 fail inspect sandbox
expect identity
MOCK_IDENTITY=arn:aws:sts::123456789012:assumed-role/wrong/session fail inspect sandbox
expect identity
AWS_ACCESS_KEY_ID=static fail inspect sandbox
expect forbidden
fail plan sandbox artifact-storage
expect authorize-plan
pass plan sandbox artifact-storage --authorize-plan
expect 'Plan only'
! grep -q execute-change-set "$MOCK_LOG"
MOCK_PARAMETERS=$'Required\tNone\tFalse' fail plan sandbox artifact-storage --authorize-plan
expect 'Missing required input'
MOCK_PARAMETERS=$'SsmKey\t/path/to/parameter\tFalse' pass plan sandbox artifact-storage --authorize-plan
MOCK_CHANGES=$'Remove\tBucket\tAWS::S3::Bucket\tNone' fail plan sandbox artifact-storage --authorize-plan
expect 'Deletion/import'
MOCK_CHANGES=$'Modify\tBucket\tAWS::S3::Bucket\tConditional' fail plan sandbox artifact-storage --authorize-plan
expect 'Replacement risk'
MOCK_UNSUPPORTED=1 fail plan sandbox artifact-storage --authorize-plan
expect Nested
MOCK_CHANGE_STATUS=FAILED MOCK_EMPTY=True pass plan sandbox artifact-storage --authorize-plan
expect 'Empty change set'
MOCK_CHANGE_STATUS=FAILED fail plan sandbox artifact-storage --authorize-plan
expect failed
fail execute sandbox "$arn" --authorize-execution different
MOCK_EXECUTION_ROLE=arn:aws:iam::123456789012:role/wrong fail execute sandbox "$arn" --authorize-execution "$arn"
expect ExecutionRole
pass execute sandbox "$arn" --authorize-execution "$arn"
MOCK_EXECUTION_FAILURE=1 fail execute sandbox "$arn" --authorize-execution "$arn"
expect 'execution failed'
MOCK_STATUS=UPDATE_ROLLBACK_COMPLETE fail execute sandbox "$arn" --authorize-execution "$arn"
expect 'failed or rolled back'
printf '%s\n' '03-storage artifact-storage stacks/storage/example.yaml -' >stacks/catalog.conf
fail plan sandbox artifact-storage --authorize-plan
expect disabled
# Two earlier disabled stacks may supply outputs, but ambiguous names must fail.
printf '%s\n' 'Resources: {}' >stacks/storage/upstream.yml
printf '%s\n' 'Resources: {}' >stacks/storage/another.yml
printf '%s\n' '01-network network stacks/storage/upstream.yml -' '03-storage artifact-storage stacks/storage/example.yaml sandbox' >stacks/catalog.conf
MOCK_PARAMETERS=$'NetworkId\tNone\tFalse' pass plan sandbox artifact-storage --authorize-plan
MOCK_PARAMETERS=$'NetworkId\tNone\tTrue' fail plan sandbox artifact-storage --authorize-plan
expect Secret
MOCK_MISSING=1 MOCK_PARAMETERS=$'NetworkId\tNone\tFalse' fail plan sandbox artifact-storage --authorize-plan
expect 'Missing required input'
MOCK_STATUS=UPDATE_FAILED fail plan sandbox artifact-storage --authorize-plan
expect unhealthy
MOCK_DENIED=1 fail plan sandbox artifact-storage --authorize-plan
expect 'not treated as absence'
printf '%s\n' '02-network other stacks/storage/another.yml -' >>stacks/catalog.conf
fail catalog
expect order
printf '%s\n' '01-network network stacks/storage/upstream.yml -' '02-network other stacks/storage/another.yml -' '03-storage artifact-storage stacks/storage/example.yaml sandbox' >stacks/catalog.conf
fail plan sandbox artifact-storage --authorize-plan
expect Ambiguous
# Catalog diagnostics, same-stage ordering, and malformed paths.
catalog
printf '%s\n' '03-storage other stacks/storage/another.yml sandbox' >>stacks/catalog.conf
pass catalog
printf '%s\n' '03-storage other stacks/storage/upstream.yml sandbox' >>stacks/catalog.conf
fail catalog
expect Duplicate
printf '%s\n' '03-storage sample stacks/../outside.yaml sandbox' >stacks/catalog.conf
fail catalog
expect Unsafe
printf '%s\n' '03-storage sample stacks/storage/missing.yml sandbox' >stacks/catalog.conf
fail catalog
expect Missing
printf '%s\n' '03-storage sample stacks/storage/example.yaml sandbox extra' >stacks/catalog.conf
fail catalog
expect 'four fields'
catalog
printf '%s\n' 'Engine offline regression tests passed'
