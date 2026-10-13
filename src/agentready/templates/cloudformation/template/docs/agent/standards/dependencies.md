# Local tools

Repository scripts use Python standard library. cfn-lint and cfn-guard are required for infrastructure verification; install into a project or user-selected local environment following README.md. Missing tools fail checks. CI pins tool versions. Do not add application runtime dependencies on AgentReady or silently install global tools.
