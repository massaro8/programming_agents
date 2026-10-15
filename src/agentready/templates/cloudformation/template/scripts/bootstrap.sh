#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'AWS bootstrap is operator owned. Configure account OIDC provider, scoped DeploymentRole,' 'separate ExecutionRole, constrained iam:PassRole and workload boundaries.' 'See docs/infrastructure/ENGINEERING.md. This script never creates IAM resources.' >&2
exit 1
