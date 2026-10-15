# 0003 — Catalog-driven CloudFormation and an optional AWS CLI workflow

Status: Accepted
Date: 2026-10-15

## Context
Real repository use showed that domain ownership, explicit stage order and native
CloudFormation contracts are reusable. Deployment authorization and account IAM remain
project responsibilities. The historical ASIA report predates its five-column manual
selection change, so its deploy-on-push behavior is not an appropriate generated default.

## Decision
Generate domain stacks, a strict four-column catalog and a disabled storage example.
Validate every template offline. Bundle a Bash/coreutils/AWS CLI workflow, with explicit
configuration and distinct inspect, plan and exact-ARN execute operations. Resolve only
same-account upstream outputs or native defaults; never retrieve secrets. Keep account
OIDC/bootstrap outside the normal catalog. Preserve the single Python governance system
in CloudFormation and Hybrid; generated repositories remain independent and detachable.

## Consequences
No Python deployment packages or graph engine. Every stack is planned/reviewed/executed
separately in catalog order; sequences are not transactional. Automatic branch deployment,
project IAM policies, nested changes, replacements/deletions, role migrations and oversized
inline templates require a separately designed and authorized procedure. Default CI remains
validation only, and local hooks are optional. See the generated engineering contract.
