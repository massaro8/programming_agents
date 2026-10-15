# Architecture

CloudFormation stacks under `stacks/<domain>/` own resources and stable parameter/output
contracts. The four-column catalog owns order and environment enablement; directories own
responsibility. Guard owns static policy checks. Standalone Python owns local governance.
Bash/AWS CLI owns an optional, separately configured and authorized change-set workflow.

Default CI validates offline. Bootstrap IAM is operator controlled and outside the catalog.
No generated application imports AgentReady. See [engineering](infrastructure/ENGINEERING.md)
for catalog, OIDC, configuration, review, failure and rollback contracts.
