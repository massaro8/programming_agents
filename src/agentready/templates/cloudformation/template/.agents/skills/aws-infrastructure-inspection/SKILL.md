---
name: aws-infrastructure-inspection
description: Inspect a named existing AWS CloudFormation stack using explicit authorization and a configured read-only role; fall back to local infrastructure evidence when tools or credentials are unavailable.
---

# AWS infrastructure inspection

## Purpose
Gather bounded existing-stack metadata without changing AWS or retrieving secrets.

## Positive triggers
Inspect an existing named stack, verify its status, or compare local infrastructure against authorized AWS metadata.

## Exclusions
Offline validation alone, deployment, profile configuration, secret retrieval and account-wide discovery.

## Scope
Discover local AWS CLI with --version and --help; discover agent-toolkit with --help and run list-installed-skills only if help confirms support. Never install, configure or change global tools. Optional AWS MCP is usable only when already available with explicitly suitable read-only capabilities; do not auto-configure it.

## Procedure
1. Read docs/infrastructure contracts and name environment, profile, region, stack, expected account and read-only role. Resolve branch/account/region with scripts/environment_contracts.py; no production fallback.
2. Require explicit inspection authorization before credentials or AWS requests. Existing local configuration must provide a read-only IAM role; identity does not prove permissions.
3. Use scripts/aws_inspection.py discover and inspect_stack with structured argv. STS get-caller-identity must match expected account and role before CloudFormation describe-stacks for the named target. The configured region must match the environment contract.
4. Return stack status and explicitly allowlisted nonsensitive outputs only. No get-template, parameter/secret retrieval, role assumption or write operations. Bound responses and report failures using local fallback.
5. AWS CLI operations are statically allowlisted; IAM restrictions remain the security boundary. Never claim shell denylisting proves safety.

## Verification
Use injectable mocked runners to verify identity mismatch, authorization refusal, missing tools/credentials, denied calls, absent/existing stacks and output redaction; do not query an actual account during local tests.

## Failure / escalation
If context, authorization, configured role, CLI or credentials are unavailable, return offline local-template and contract evidence. Do not bootstrap credentials. Request missing user context only for required account access.

## Output contract
Return named target, safe metadata, checks performed and uncertainty. Never emit raw responses, credentials, parameter values or secrets.
