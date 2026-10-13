# ADR 0001 — Static bundled project families

Status: Accepted

AgentReady must generate both Python and CloudFormation repositories while preserving existing
Python invocations and detachable engineering tools. Python profiles describe application layout;
infrastructure repositories require a different verification and navigation contract.

Use an explicit `--family` selection with a static contract resolver. Python remains the default,
with minimal/application/service profiles. CloudFormation defaults to infrastructure; incompatible
pairs fail before writing. Copier renders only trusted bundled family content. Shared stdlib
capabilities and canonical governance scripts are exported through the existing source-rendering
seam. Family-specific resources, policies and validation remain separate template content.

Schema-1 manifests without family retain Python meaning. Existing work records without an evidence
marker remain readable; new configured work records opt into executed verification receipts.
Doctor resolves family contracts without executing project scripts. Detach retains its fixed
`.agentready/` removal boundary and preserves all ordinary files for both families.

This adds two explicit consumers, not a plugin framework, provider discovery or orchestration
runtime. File-level infrastructure maps avoid unreliable custom YAML parsing. cfn-lint and Guard
own CloudFormation-aware verification. Adding another family requires a concrete contract and
qualification; extension discovery is not implied by this decision.
