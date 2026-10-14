# Local tools

Repository scripts use Python standard library. cfn-lint and cfn-guard are required for infrastructure verification. Explicit bootstrap prepares missing tools locally in .tools using pinned versions; initial installation requires network access. Checks remain offline and fail if tools are missing. CI pins tool versions. Do not add application runtime dependencies on AgentReady or silently install global tools.
